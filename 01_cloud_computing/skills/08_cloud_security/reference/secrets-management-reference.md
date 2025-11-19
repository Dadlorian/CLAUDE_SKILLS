# Secrets Management Reference

## Introduction

Secrets management is the practice of securely storing, accessing, and managing sensitive credentials, API keys, certificates, and other confidential data. This reference covers secrets management strategies, tools, and best practices for cloud environments.

## What Are Secrets?

### Types of Secrets

**Authentication Credentials**:
- Passwords and passphrases
- API keys and tokens
- OAuth client secrets
- Database credentials
- Service account keys

**Cryptographic Material**:
- Private keys (RSA, EC)
- TLS/SSL certificates and private keys
- SSH keys
- Encryption keys
- Signing keys

**Infrastructure Secrets**:
- Cloud provider access keys (AWS access keys, Azure service principal secrets)
- Database connection strings
- Message queue credentials
- Cache credentials (Redis, Memcached)

**Application Secrets**:
- Third-party API keys (Stripe, Twilio, SendGrid)
- Webhook secrets
- Feature flag tokens
- License keys

**Sensitive Configuration**:
- Environment-specific settings
- Connection strings
- Internal service URLs
- Security tokens

## Secrets Management Principles

### Core Principles

**1. Never Hardcode Secrets**:
- No secrets in source code
- No secrets in configuration files committed to version control
- No secrets in container images
- No secrets in environment variables (with exceptions)

**2. Principle of Least Privilege**:
- Grant minimal necessary access to secrets
- Time-bound access when possible
- Role-based access control
- Separate secrets per environment and application

**3. Defense in Depth**:
- Encryption at rest and in transit
- Access control policies
- Audit logging
- Network isolation
- Runtime protection

**4. Rotation and Lifecycle**:
- Regular secret rotation (automated when possible)
- Versioning for rollback capability
- Deprecation and revocation processes
- Expiration policies

**5. Auditability**:
- Log all secret access
- Track secret creation, rotation, and deletion
- Monitor for unusual access patterns
- Compliance reporting

## Cloud-Native Secrets Management

### AWS Secrets Manager

**Features**:
- Automatic secret rotation for AWS services (RDS, Redshift, DocumentDB)
- Versioning and staging labels
- Fine-grained IAM access control
- Encryption at rest with KMS
- Cross-region replication
- Integration with Lambda for custom rotation

**Secret Types**:
- Database credentials (auto-rotation supported)
- API keys
- OAuth tokens
- Custom key-value pairs
- Binary secrets

**Best Practices**:
```python
import boto3
import json

# Retrieve secret
def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Enable automatic rotation
client.rotate_secret(
    SecretId='prod/db/credentials',
    RotationLambdaARN='arn:aws:lambda:...',
    RotationRules={'AutomaticallyAfterDays': 30}
)
```

**Pricing**: Pay per secret per month + API calls

**When to Use**:
- Database credentials with auto-rotation
- Application secrets needing versioning
- Cross-region secret replication needed
- Integration with AWS services

### AWS Systems Manager Parameter Store

**Features**:
- Standard and advanced tiers
- String, StringList, SecureString (encrypted with KMS)
- Hierarchical organization (/app/env/param)
- No automatic rotation (use Lambda)
- Free tier available (10,000 standard parameters)
- Parameter policies (expiration, notifications)

**Best Practices**:
```python
import boto3

ssm = boto3.client('ssm')

# Store secret
ssm.put_parameter(
    Name='/prod/app/db-password',
    Value='secret-value',
    Type='SecureString',
    KeyId='alias/aws/ssm',  # KMS key
    Tier='Standard',
    Tags=[
        {'Key': 'Environment', 'Value': 'prod'},
        {'Key': 'Application', 'Value': 'myapp'}
    ]
)

# Retrieve secret
response = ssm.get_parameter(Name='/prod/app/db-password', WithDecryption=True)
secret = response['Parameter']['Value']
```

**When to Use**:
- Simple configuration and secrets
- Cost-sensitive deployments (free tier)
- Hierarchical organization needed
- Non-sensitive parameters alongside secrets

### Azure Key Vault

**Features**:
- Keys, secrets, and certificates in one service
- Managed HSM option (FIPS 140-2 Level 3)
- Soft-delete and purge protection
- Azure AD RBAC or vault access policies
- Private endpoint support
- Logging to Azure Monitor

**Tiers**:
- **Standard**: Software-protected keys
- **Premium**: HSM-protected keys

**Secret Types**:
- Secrets (text, passwords, connection strings)
- Keys (RSA, EC for encryption/signing)
- Certificates (PFX/PEM with auto-renewal)

**Best Practices**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)

# Store secret
client.set_secret("db-password", "secret-value")

# Retrieve secret
secret = client.get_secret("db-password")
print(secret.value)

# Enable soft-delete and purge protection at vault level
# Set access policies or use Azure RBAC
```

**When to Use**:
- Azure-native applications
- Certificate management needed
- HSM-backed keys required
- Integration with Azure services

### GCP Secret Manager

**Features**:
- Secret versioning with automatic version management
- IAM-based access control
- Encryption with Cloud KMS (customer-managed keys supported)
- Regional and multi-regional secrets
- Audit logging with Cloud Audit Logs
- Rotation notifications (manual rotation)

**Best Practices**:
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
project_id = "my-project"

# Create secret
parent = f"projects/{project_id}"
secret = client.create_secret(
    request={
        "parent": parent,
        "secret_id": "db-password",
        "secret": {"replication": {"automatic": {}}},
    }
)

# Add secret version
client.add_secret_version(
    request={
        "parent": secret.name,
        "payload": {"data": b"secret-value"},
    }
)

# Access secret
name = f"projects/{project_id}/secrets/db-password/versions/latest"
response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode('UTF-8')
```

**When to Use**:
- GCP-native applications
- Multi-regional secrets needed
- Integration with GCP services (Cloud Run, GKE, Cloud Functions)
- Fine-grained IAM control

## Third-Party Secrets Management

### HashiCorp Vault

**Features**:
- Multi-cloud secrets management
- Dynamic secrets (temporary credentials)
- Encryption as a service
- PKI and certificate management
- Secret engines for various backends (AWS, Azure, GCP, databases, SSH)
- Comprehensive audit logging
- High availability and replication

**Deployment Options**:
- Self-hosted (open source or enterprise)
- HashiCorp Cloud Platform (HCP) Vault

**Secret Engines**:
- **KV (Key-Value)**: Static secrets (v1: no versioning, v2: versioning)
- **Dynamic Secrets**: AWS IAM, database credentials, SSH, PKI
- **Transit**: Encryption as a service
- **Cloud**: AWS, Azure, GCP credentials
- **Database**: MySQL, PostgreSQL, MongoDB, etc.

**Best Practices**:
```python
import hvac

# Initialize Vault client
client = hvac.Client(url='https://vault.example.com:8200')
client.token = 'your-vault-token'

# Write secret (KV v2)
client.secrets.kv.v2.create_or_update_secret(
    path='myapp/db',
    secret={'username': 'dbuser', 'password': 'secret'},
)

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='myapp/db')
db_password = secret['data']['data']['password']

# Dynamic database credentials
db_creds = client.secrets.database.generate_credentials(name='my-role')
temp_username = db_creds['data']['username']
temp_password = db_creds['data']['password']
lease_duration = db_creds['lease_duration']  # Auto-expires
```

**Authentication Methods**:
- Token, AppRole, AWS, Azure, GCP, Kubernetes
- LDAP, Okta, GitHub, OIDC
- TLS certificates, Username/Password

**When to Use**:
- Multi-cloud environments
- Dynamic secrets needed (temporary credentials)
- Centralized secrets management across platforms
- Advanced features (encryption as a service, PKI)

### CyberArk Conjur

**Features**:
- Open source secrets management
- Kubernetes-native
- Role-based access control
- Secrets rotation
- Audit logging
- Secrets injection for containers

**When to Use**:
- Kubernetes-centric deployments
- Open source preferred
- CyberArk integration

### Doppler

**Features**:
- Centralized secrets management
- Multi-environment support (dev, staging, prod)
- Secrets syncing to cloud providers
- GitOps workflow
- Team collaboration features
- Audit logs and versioning

**When to Use**:
- Developer-friendly secrets management
- Multi-environment configuration
- Team collaboration on secrets

## Kubernetes Secrets Management

### Native Kubernetes Secrets

**Features**:
- Base64 encoded (not encrypted by default)
- Stored in etcd
- Mounted as volumes or environment variables
- RBAC for access control

**Limitations**:
- Not encrypted at rest by default (need etcd encryption)
- Base64 encoding is not encryption
- No built-in rotation
- No audit logging by default

**Encryption at Rest**:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

### External Secrets Operator

**Features**:
- Sync secrets from external secrets managers to Kubernetes
- Supports AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, Vault, and more
- Automatic secret rotation
- Multiple secret stores per cluster

**Example**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets
    kind: SecretStore
  target:
    name: db-secret
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/password
```

### Sealed Secrets

**Features**:
- Encrypt secrets for safe storage in Git
- Controller decrypts and creates Kubernetes Secrets
- GitOps-friendly (can commit encrypted secrets)
- Public key encryption (only cluster can decrypt)

**Workflow**:
```bash
# Create sealed secret
echo -n 'my-secret' | kubectl create secret generic mysecret \
  --dry-run=client --from-file=password=/dev/stdin -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git
# Apply to cluster (controller decrypts)
kubectl apply -f sealed-secret.yaml
```

### SOPS (Secrets OPerationS)

**Features**:
- Encrypt YAML/JSON files with KMS, PGP, age
- Partial encryption (encrypt values, leave keys plaintext)
- Version control friendly
- Multiple key management backends

**Example**:
```bash
# Encrypt file with AWS KMS
sops --encrypt --kms 'arn:aws:kms:us-east-1:...' secret.yaml > secret.enc.yaml

# Decrypt file
sops --decrypt secret.enc.yaml

# Edit encrypted file in place
sops secret.enc.yaml
```

## Secrets Injection Patterns

### Environment Variables

**Pros**:
- Simple, widely supported
- Native OS support

**Cons**:
- Visible in process listings (`ps`, `/proc`)
- Leaked in error messages and logs
- Inherited by child processes
- No rotation without restart

**Best Practices**:
- Use for non-highly-sensitive secrets
- Combine with secret management tools
- Avoid logging environment variables
- Clear sensitive env vars after use

### Volume Mounts (Kubernetes)

**Pros**:
- File-based secrets
- Updated automatically (with some delay)
- Not in environment

**Cons**:
- Requires file I/O
- Application needs to reload on change

**Example**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-credentials
```

### Init Containers

**Pattern**: Fetch secrets in init container, pass to main container

**Example**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
  - name: secret-fetcher
    image: vault:latest
    command: ['sh', '-c', 'vault kv get -field=password secret/db > /secrets/db-pass']
    volumeMounts:
    - name: secrets
      mountPath: /secrets
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
  volumes:
  - name: secrets
    emptyDir: {}
```

### Sidecar Containers

**Pattern**: Sidecar fetches and rotates secrets, main container reads from shared volume

**Use Cases**:
- Automatic secret rotation
- Dynamic secrets with lease renewal
- Secret caching and refresh

**Example** (Vault Agent Sidecar):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: secrets
      mountPath: /vault/secrets
  - name: vault-agent
    image: vault:latest
    args:
      - agent
      - -config=/vault/config/agent.hcl
    volumeMounts:
    - name: secrets
      mountPath: /vault/secrets
    - name: config
      mountPath: /vault/config
  volumes:
  - name: secrets
    emptyDir: {}
  - name: config
    configMap:
      name: vault-agent-config
```

### SDK/Client Libraries

**Pattern**: Application fetches secrets directly from secrets manager

**Pros**:
- Direct access to secrets manager
- Can implement caching and refresh logic
- No infrastructure changes needed

**Cons**:
- Application must handle errors and retries
- Requires SDK dependencies
- Potential cold start latency

**Example**:
```python
import boto3
import json
from functools import lru_cache

@lru_cache(maxsize=128)
def get_secret(secret_name, ttl_hash=None):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Refresh every 5 minutes
import time
ttl = lambda: int(time.time() / 300)

# Usage
secret = get_secret('prod/db/creds', ttl_hash=ttl())
```

## Secret Rotation

### Rotation Strategies

**Automatic Rotation**:
- AWS Secrets Manager: Lambda-based rotation
- Vault: Dynamic secrets with TTL
- GCP Secret Manager: Manual trigger with Cloud Functions

**Manual Rotation**:
1. Create new secret version
2. Update applications to use new version
3. Verify new version works
4. Deprecate old version
5. Delete old version after grace period

**Zero-Downtime Rotation**:
- Blue-green: Two valid secrets simultaneously
- Version staging: Transition period with both versions valid
- Connection draining: Allow existing connections to complete

### Rotation Frequency

**High Security** (30-90 days):
- Production database credentials
- Administrative access keys
- Payment processing credentials

**Standard** (90-180 days):
- API keys
- Service account credentials
- Non-critical databases

**Low Priority** (180-365 days):
- Development/test credentials
- Internal service credentials

**On-Demand**:
- After security incident
- Employee departure
- Suspected compromise
- Regulatory requirement

### Rotation Best Practices

**Pre-Rotation**:
- Test rotation procedure in non-production
- Document rollback procedure
- Ensure monitoring and alerting in place
- Communicate to stakeholders

**During Rotation**:
- Use gradual rollout (canary, blue-green)
- Monitor error rates and logs
- Have rollback ready
- Verify new credentials work before deprecating old

**Post-Rotation**:
- Verify old credentials are disabled
- Update documentation
- Review logs for failed authentication attempts
- Document lessons learned

## Secrets Scanning and Detection

### Pre-Commit Hooks

**Tools**:
- **git-secrets**: Prevent committing secrets (AWS, custom patterns)
- **detect-secrets**: Yelp's secret scanning tool
- **gitleaks**: Comprehensive secret scanner
- **talisman**: Pre-commit hook for secrets

**Setup Example** (pre-commit framework):
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### CI/CD Pipeline Scanning

**Tools**:
- **GitGuardian**: SaaS secret scanning
- **TruffleHog**: Git history secret scanner
- **Gitleaks**: CI/CD integration
- **GitHub Secret Scanning**: Built-in GitHub feature
- **GitLab Secret Detection**: Built-in GitLab feature

**Example** (GitHub Actions):
```yaml
name: Secret Scanning
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Repository Scanning

**Full History Scan**:
```bash
# Scan entire git history
gitleaks detect --source . --verbose

# TruffleHog
trufflehog git file://. --only-verified
```

**Remediation**:
1. Revoke/rotate compromised secret immediately
2. Remove from git history (git filter-branch, BFG Repo-Cleaner)
3. Force push (coordinate with team)
4. Audit usage of compromised secret
5. Post-mortem and prevention measures

## Compliance and Secrets Management

### PCI DSS Requirements
- Requirement 8: Identify and authenticate access
- Strong password policies
- MFA for privileged access
- Regular password/key rotation

### HIPAA Requirements
- 164.308(a)(5): Automatic logoff
- 164.312(a)(2): Emergency access procedure
- 164.312(d): Encryption and decryption

### SOC 2 Controls
- CC6.1: Logical access controls
- CC6.2: Prior to issuing system credentials
- CC6.7: Access removed when no longer needed

## Best Practices Summary

### DO
- ✅ Use cloud-native secrets managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- ✅ Encrypt secrets at rest and in transit
- ✅ Implement least privilege access
- ✅ Rotate secrets regularly (30-90 days for high-value secrets)
- ✅ Use temporary credentials when possible (dynamic secrets)
- ✅ Audit all secret access
- ✅ Scan repositories for secrets (pre-commit hooks, CI/CD)
- ✅ Use different secrets per environment (dev, staging, prod)
- ✅ Implement secret versioning
- ✅ Document secret rotation procedures

### DON'T
- ❌ Hardcode secrets in source code
- ❌ Commit secrets to version control
- ❌ Store secrets in container images
- ❌ Share secrets between applications
- ❌ Use same secrets across environments
- ❌ Store secrets in plaintext
- ❌ Log secret values
- ❌ Email or Slack secrets
- ❌ Use default/example secrets in production
- ❌ Ignore secret expiration warnings

## Tools Reference

### Cloud-Native
- AWS Secrets Manager
- AWS Systems Manager Parameter Store
- Azure Key Vault
- GCP Secret Manager

### Third-Party
- HashiCorp Vault
- CyberArk Conjur
- Doppler
- 1Password Secrets Automation
- Infisical

### Kubernetes
- External Secrets Operator
- Sealed Secrets
- Vault Agent Injector
- SOPS

### Scanning
- git-secrets
- gitleaks
- TruffleHog
- detect-secrets
- GitGuardian
- GitHub/GitLab native scanning

## Resources

### Documentation
- AWS Secrets Manager: https://docs.aws.amazon.com/secretsmanager/
- Azure Key Vault: https://docs.microsoft.com/azure/key-vault/
- GCP Secret Manager: https://cloud.google.com/secret-manager/docs
- HashiCorp Vault: https://www.vaultproject.io/docs

### Learning
- OWASP Secrets Management Cheat Sheet
- HashiCorp Vault Tutorials
- AWS Secrets Manager Best Practices
- Kubernetes Secrets Management Guide
