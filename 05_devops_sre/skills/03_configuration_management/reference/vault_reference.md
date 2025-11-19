# HashiCorp Vault Reference

## Overview
Comprehensive reference for HashiCorp Vault secrets management, covering setup, authentication, secrets engines, policies, and enterprise patterns.

## Table of Contents
- [Core Concepts](#core-concepts)
- [Installation and Setup](#installation-and-setup)
- [Authentication Methods](#authentication-methods)
- [Secrets Engines](#secrets-engines)
- [Policies](#policies)
- [Encryption as a Service](#encryption-as-a-service)
- [High Availability](#high-availability)
- [Best Practices](#best-practices)
- [Advanced Patterns](#advanced-patterns)

---

## Core Concepts

### Architecture
```
┌─────────────────────────────────────────┐
│         Vault Client (API/CLI)          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│            Vault Server                 │
│  ┌──────────────────────────────────┐  │
│  │      Authentication Methods       │  │
│  │  - Token  - LDAP  - Kubernetes   │  │
│  │  - AWS    - Azure - AppRole      │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │       Secrets Engines            │  │
│  │  - KV      - Database  - PKI     │  │
│  │  - AWS     - Azure     - SSH     │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │       Policy Engine              │  │
│  │  - ACL Policies                  │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │       Audit Devices              │  │
│  └──────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Storage Backend    │
         │  - Consul  - Raft    │
         │  - Etcd    - S3      │
         └─────────────────────┘
```

### Key Terms
- **Seal/Unseal**: Security mechanism to protect Vault data
- **Secrets Engine**: Component that stores, generates, or encrypts data
- **Authentication Method**: Way to verify identity and assign policies
- **Policy**: Set of rules defining what secrets can be accessed
- **Token**: Authentication credential used to access Vault
- **Lease**: Time-to-live for dynamically generated secrets
- **Path**: Hierarchical location where secrets are stored

---

## Installation and Setup

### Dev Server (Testing Only)
```bash
# Start dev server (in-memory, auto-unsealed)
vault server -dev -dev-root-token-id="root"

# Set environment variables
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Verify
vault status
```

### Production Server Configuration
```hcl
# vault.hcl
ui = true

storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-node-1"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"
}

api_addr = "https://vault.example.com:8200"
cluster_addr = "https://10.0.1.10:8201"

telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

# Seal configuration
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "12345678-1234-1234-1234-123456789012"
}
```

### Initialization
```bash
# Initialize Vault (first time only)
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init.json

# Extract unseal keys and root token
UNSEAL_KEY_1=$(jq -r '.unseal_keys_b64[0]' vault-init.json)
UNSEAL_KEY_2=$(jq -r '.unseal_keys_b64[1]' vault-init.json)
UNSEAL_KEY_3=$(jq -r '.unseal_keys_b64[2]' vault-init.json)
ROOT_TOKEN=$(jq -r '.root_token' vault-init.json)

# Unseal Vault (requires 3 of 5 keys)
vault operator unseal $UNSEAL_KEY_1
vault operator unseal $UNSEAL_KEY_2
vault operator unseal $UNSEAL_KEY_3

# Login with root token
vault login $ROOT_TOKEN
```

### Systemd Service
```ini
# /etc/systemd/system/vault.service
[Unit]
Description=HashiCorp Vault
Documentation=https://www.vaultproject.io/docs/
Requires=network-online.target
After=network-online.target
ConditionFileNotEmpty=/etc/vault.d/vault.hcl

[Service]
User=vault
Group=vault
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
SecureBits=keep-caps
AmbientCapabilities=CAP_IPC_LOCK
Capabilities=CAP_IPC_LOCK+ep
CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
NoNewPrivileges=yes
ExecStart=/usr/local/bin/vault server -config=/etc/vault.d/vault.hcl
ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGINT
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StartLimitInterval=60
StartLimitBurst=3
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```

---

## Authentication Methods

### 1. Token Auth (Built-in)
```bash
# Create a token
vault token create \
  -policy=app-policy \
  -ttl=1h \
  -renewable \
  -display-name="app-server-token"

# Create periodic token (can renew indefinitely)
vault token create \
  -policy=backup-policy \
  -period=24h

# Lookup token info
vault token lookup

# Renew token
vault token renew

# Revoke token
vault token revoke <token>
```

### 2. AppRole Auth
```bash
# Enable AppRole
vault auth enable approle

# Create role
vault write auth/approle/role/my-app \
  token_policies="app-policy" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=10m

# Get role ID
vault read auth/approle/role/my-app/role-id
# role_id: db02de05-fa39-4855-059b-67221c5c2f63

# Generate secret ID
vault write -f auth/approle/role/my-app/secret-id
# secret_id: 6a174c20-f6de-a53c-74d2-6018fcceff64

# Login with AppRole
vault write auth/approle/login \
  role_id="db02de05-fa39-4855-059b-67221c5c2f63" \
  secret_id="6a174c20-f6de-a53c-74d2-6018fcceff64"
```

### 3. AWS Auth
```bash
# Enable AWS auth
vault auth enable aws

# Configure AWS credentials
vault write auth/aws/config/client \
  access_key=AKIAIOSFODNN7EXAMPLE \
  secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Create role for EC2 instances
vault write auth/aws/role/my-app-role \
  auth_type=iam \
  bound_iam_principal_arn=arn:aws:iam::123456789012:role/MyAppRole \
  policies=app-policy \
  ttl=1h

# Login from EC2 instance
vault login -method=aws \
  role=my-app-role
```

### 4. Kubernetes Auth
```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure Kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc:443" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

# Create role
vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp \
  bound_service_account_namespaces=production \
  policies=app-policy \
  ttl=1h

# Login from pod
vault write auth/kubernetes/login \
  role=myapp \
  jwt=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
```

### 5. LDAP Auth
```bash
# Enable LDAP
vault auth enable ldap

# Configure LDAP
vault write auth/ldap/config \
  url="ldaps://ldap.example.com" \
  userdn="ou=Users,dc=example,dc=com" \
  groupdn="ou=Groups,dc=example,dc=com" \
  binddn="cn=vault,ou=ServiceAccounts,dc=example,dc=com" \
  bindpass="SecretPassword" \
  userattr="uid" \
  groupattr="cn"

# Map LDAP group to policy
vault write auth/ldap/groups/developers \
  policies=dev-policy

# Login
vault login -method=ldap username=john.doe
```

### 6. GitHub Auth
```bash
# Enable GitHub auth
vault auth enable github

# Configure
vault write auth/github/config \
  organization=mycompany

# Map team to policies
vault write auth/github/map/teams/engineering \
  value=dev-policy,common-policy

# Login
vault login -method=github token=<github-token>
```

---

## Secrets Engines

### 1. KV Secrets Engine (v2)
```bash
# Enable KV v2
vault secrets enable -path=secret kv-v2

# Write secret
vault kv put secret/myapp/config \
  db_password="SuperSecret123" \
  api_key="abc-123-def-456"

# Read secret
vault kv get secret/myapp/config
vault kv get -field=db_password secret/myapp/config

# List secrets
vault kv list secret/myapp/

# Get specific version
vault kv get -version=2 secret/myapp/config

# Delete latest version (soft delete)
vault kv delete secret/myapp/config

# Undelete
vault kv undelete -versions=1 secret/myapp/config

# Destroy permanently
vault kv destroy -versions=1,2 secret/myapp/config

# Set metadata
vault kv metadata put \
  -max-versions=5 \
  -delete-version-after=30d \
  secret/myapp/config
```

### 2. Database Secrets Engine
```bash
# Enable database engine
vault secrets enable database

# Configure PostgreSQL
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mydb?sslmode=disable" \
  username="vault" \
  password="vaultpass"

# Create role for readonly access
vault write database/roles/readonly \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Create role for read/write access
vault write database/roles/readwrite \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="4h"

# Generate dynamic credentials
vault read database/creds/readonly
# Key                Value
# ---                -----
# lease_id           database/creds/readonly/abc123
# lease_duration     1h
# username           v-token-readonly-xyz
# password           A1b2C3d4E5f6

# Rotate root credentials
vault write -f database/rotate-root/postgres
```

### 3. AWS Secrets Engine
```bash
# Enable AWS engine
vault secrets enable aws

# Configure root credentials
vault write aws/config/root \
  access_key=AKIAIOSFODNN7EXAMPLE \
  secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  region=us-east-1

# Create role
vault write aws/roles/s3-readonly \
  credential_type=iam_user \
  policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
EOF

# Generate credentials
vault read aws/creds/s3-readonly
```

### 4. PKI Secrets Engine
```bash
# Enable PKI
vault secrets enable pki

# Configure TTL
vault secrets tune -max-lease-ttl=87600h pki

# Generate root CA
vault write -field=certificate pki/root/generate/internal \
  common_name="example.com" \
  ttl=87600h > CA_cert.crt

# Configure CA and CRL URLs
vault write pki/config/urls \
  issuing_certificates="http://vault.example.com:8200/v1/pki/ca" \
  crl_distribution_points="http://vault.example.com:8200/v1/pki/crl"

# Create role
vault write pki/roles/example-dot-com \
  allowed_domains="example.com" \
  allow_subdomains=true \
  max_ttl="720h"

# Issue certificate
vault write pki/issue/example-dot-com \
  common_name="app.example.com" \
  ttl="24h"
```

### 5. Transit Secrets Engine (Encryption as a Service)
```bash
# Enable transit
vault secrets enable transit

# Create encryption key
vault write -f transit/keys/my-app-key

# Encrypt data
vault write transit/encrypt/my-app-key \
  plaintext=$(echo "Secret data" | base64)
# ciphertext: vault:v1:abc123def456...

# Decrypt data
vault write transit/decrypt/my-app-key \
  ciphertext="vault:v1:abc123def456..."
# plaintext: U2VjcmV0IGRhdGE=

# Rotate key
vault write -f transit/keys/my-app-key/rotate

# Rewrap with new key
vault write transit/rewrap/my-app-key \
  ciphertext="vault:v1:abc123def456..."
```

### 6. SSH Secrets Engine
```bash
# Enable SSH
vault secrets enable ssh

# Create CA
vault write ssh/config/ca \
  generate_signing_key=true

# Create role
vault write ssh/roles/otp \
  key_type=otp \
  default_user=ubuntu \
  cidr_list=10.0.0.0/8

# Get OTP
vault write ssh/creds/otp \
  ip=10.0.1.5 \
  username=ubuntu
```

---

## Policies

### Policy Syntax
```hcl
# policies/app-policy.hcl

# Allow reading application secrets
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

# Allow creating/updating specific paths
path "secret/data/myapp/config" {
  capabilities = ["create", "update", "read"]
}

# Deny delete operations
path "secret/data/myapp/production/*" {
  capabilities = ["deny"]
}

# Allow using transit encryption
path "transit/encrypt/my-app-key" {
  capabilities = ["update"]
}

path "transit/decrypt/my-app-key" {
  capabilities = ["update"]
}

# Database credentials
path "database/creds/readonly" {
  capabilities = ["read"]
}

# Templated policies with identity
path "secret/data/users/{{identity.entity.name}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Parameter constraints
path "secret/data/myapp/*" {
  capabilities = ["create", "update"]

  # Require specific fields
  required_parameters = ["ttl"]

  # Allowed values
  allowed_parameters = {
    "ttl" = ["1h", "2h", "3h"]
  }

  # Denied parameters
  denied_parameters = {
    "dangerous_setting" = []
  }
}

# Min/max values
path "aws/creds/s3-readonly" {
  capabilities = ["read"]
  min_wrapping_ttl = "100s"
  max_wrapping_ttl = "300s"
}
```

### Policy Management
```bash
# Write policy
vault policy write app-policy policies/app-policy.hcl

# Read policy
vault policy read app-policy

# List policies
vault policy list

# Delete policy
vault policy delete app-policy

# Test policy
vault token create -policy=app-policy
```

### Advanced Policy Examples
```hcl
# Admin policy
path "sys/policies/acl/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/auth/*" {
  capabilities = ["create", "read", "update", "delete", "sudo"]
}

path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Wildcard paths
path "secret/data/team/*/config" {
  capabilities = ["read"]
}

# Glob paths
path "secret/data/+/api-keys" {
  capabilities = ["read"]
}
```

---

## Encryption as a Service

### Transit Engine Patterns
```python
# Python example using hvac
import hvac
import base64

client = hvac.Client(url='http://localhost:8200', token='root')

# Encrypt
plaintext = "Sensitive data"
encoded = base64.b64encode(plaintext.encode()).decode()
result = client.secrets.transit.encrypt_data(
    name='my-app-key',
    plaintext=encoded
)
ciphertext = result['data']['ciphertext']

# Decrypt
result = client.secrets.transit.decrypt_data(
    name='my-app-key',
    ciphertext=ciphertext
)
decoded = base64.b64decode(result['data']['plaintext']).decode()

# Batch encryption
plaintexts = ['data1', 'data2', 'data3']
batch_input = [
    {'plaintext': base64.b64encode(p.encode()).decode()}
    for p in plaintexts
]
result = client.secrets.transit.encrypt_data(
    name='my-app-key',
    batch_input=batch_input
)

# Sign data
data_to_sign = "Important message"
encoded = base64.b64encode(data_to_sign.encode()).decode()
result = client.secrets.transit.sign_data(
    name='my-app-key',
    hash_input=encoded
)
signature = result['data']['signature']

# Verify signature
result = client.secrets.transit.verify_signed_data(
    name='my-app-key',
    hash_input=encoded,
    signature=signature
)
valid = result['data']['valid']  # True/False
```

---

## High Availability

### Raft Storage Configuration
```hcl
# vault-node-1.hcl
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"

  retry_join {
    leader_api_addr = "https://vault-1.example.com:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-2.example.com:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-3.example.com:8200"
  }
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"
}

api_addr = "https://vault-1.example.com:8200"
cluster_addr = "https://10.0.1.10:8201"
```

### Raft Operations
```bash
# List peers
vault operator raft list-peers

# Join cluster (from new node)
vault operator raft join https://vault-1.example.com:8200

# Remove peer
vault operator raft remove-peer vault-3

# Take snapshot
vault operator raft snapshot save backup.snap

# Restore snapshot
vault operator raft snapshot restore backup.snap

# Check autopilot status
vault operator raft autopilot state
```

### Auto-Unseal with AWS KMS
```hcl
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "12345678-1234-1234-1234-123456789012"
  endpoint   = "https://kms.us-east-1.amazonaws.com"
}
```

---

## Best Practices

### 1. Secret Lifecycle
```bash
# Use lease management
vault write database/config/postgres \
  max_ttl=24h \
  default_ttl=1h

# Monitor lease count
vault read sys/internal/counters/leases

# Revoke leases
vault lease revoke database/creds/readonly/abc123
vault lease revoke -prefix database/creds/readonly/
```

### 2. Audit Logging
```bash
# Enable file audit
vault audit enable file \
  file_path=/var/log/vault/audit.log

# Enable syslog audit
vault audit enable syslog

# Enable socket audit
vault audit enable socket \
  address="audit-server:9090" \
  socket_type="tcp"

# List audit devices
vault audit list

# Disable audit
vault audit disable file/
```

### 3. Namespaces (Enterprise)
```bash
# Create namespace
vault namespace create engineering

# List namespaces
vault namespace list

# Work in namespace
export VAULT_NAMESPACE=engineering
vault secrets enable -path=secrets kv-v2
```

### 4. Replication (Enterprise)
```bash
# Enable DR replication (primary)
vault write -f sys/replication/dr/primary/enable

# Generate secondary token
vault write sys/replication/dr/primary/secondary-token \
  id=dr-secondary-1

# Enable on secondary
vault write sys/replication/dr/secondary/enable \
  token=<token-from-primary>

# Check status
vault read sys/replication/status
```

### 5. Monitoring
```bash
# Health check
curl https://vault.example.com:8200/v1/sys/health

# Metrics (Prometheus)
curl https://vault.example.com:8200/v1/sys/metrics?format=prometheus

# Telemetry configuration
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true

  dogstatsd_addr = "localhost:8125"
  dogstatsd_tags = ["vault_cluster:prod"]
}
```

---

## Advanced Patterns

### 1. Response Wrapping
```bash
# Create wrapped token
vault kv get -wrap-ttl=5m secret/myapp/config

# Unwrap
vault unwrap <wrapping-token>

# In code
response = client.secrets.kv.v2.read_secret_version(
    path='myapp/config',
    wrap_ttl='5m'
)
wrapping_token = response['wrap_info']['token']

# Later...
unwrapped = client.sys.unwrap(wrapping_token)
```

### 2. Cubbyhole Secrets
```bash
# Each token has its own cubbyhole
vault write cubbyhole/my-secret value="secret-data"

# Only accessible with same token
vault read cubbyhole/my-secret

# New token cannot access
vault login <different-token>
vault read cubbyhole/my-secret  # Error: permission denied
```

### 3. Control Groups
```bash
# Require approval for sensitive operations
vault write sys/policies/egp/require-approval \
  policy=@require-approval.sentinel \
  enforcement_level="hard-mandatory" \
  paths="secret/data/production/*"
```

### 4. Vault Agent
```hcl
# vault-agent.hcl
pid_file = "/tmp/vault-agent.pid"

vault {
  address = "https://vault.example.com:8200"
}

auto_auth {
  method {
    type = "aws"
    config = {
      role = "my-app-role"
    }
  }

  sink {
    type = "file"
    config = {
      path = "/tmp/vault-token"
    }
  }
}

template {
  source      = "/etc/myapp/config.tmpl"
  destination = "/etc/myapp/config.yml"
  command     = "systemctl reload myapp"
}

cache {
  use_auto_auth_token = true
}
```

```bash
# Run agent
vault agent -config=vault-agent.hcl
```

### 5. Sentinel Policies (Enterprise)
```python
# require-mfa.sentinel
import "time"
import "strings"

# Require MFA for production secrets
main = rule {
  strings.has_prefix(request.path, "secret/data/production/") implies
    request.mfa_credentials is not empty
}

# Require business hours
is_business_hours = rule {
  time.hour >= 9 and time.hour < 17
}

# Combine rules
main = rule {
  is_business_hours and
  (not strings.has_prefix(request.path, "secret/data/production/") or
   request.mfa_credentials is not empty)
}
```

---

## Integration Examples

### Docker
```dockerfile
FROM alpine:latest

RUN apk add --no-cache curl jq

ENV VAULT_ADDR=https://vault.example.com:8200

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# entrypoint.sh

# Authenticate to Vault
VAULT_TOKEN=$(curl -s \
  --request POST \
  --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
  $VAULT_ADDR/v1/auth/approle/login | jq -r '.auth.client_token')

# Get database credentials
DB_CREDS=$(curl -s \
  --header "X-Vault-Token: $VAULT_TOKEN" \
  $VAULT_ADDR/v1/database/creds/myapp-readonly)

export DB_USERNAME=$(echo $DB_CREDS | jq -r '.data.username')
export DB_PASSWORD=$(echo $DB_CREDS | jq -r '.data.password')

# Start application
exec /app/myapp
```

### Kubernetes Sidecar
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  serviceAccountName: myapp

  initContainers:
  - name: vault-agent
    image: vault:latest
    args:
      - agent
      - -config=/vault/config/agent.hcl
    volumeMounts:
    - name: vault-config
      mountPath: /vault/config
    - name: shared-data
      mountPath: /vault/secrets

  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: shared-data
      mountPath: /vault/secrets

  volumes:
  - name: vault-config
    configMap:
      name: vault-agent-config
  - name: shared-data
    emptyDir:
      medium: Memory
```

---

## Troubleshooting

### Common Issues
```bash
# Sealed vault
vault operator unseal

# Permission denied
vault token lookup  # Check token capabilities
vault token capabilities <path>

# Connection issues
vault status -tls-skip-verify

# Debug mode
VAULT_LOG_LEVEL=debug vault server -config=vault.hcl

# Audit log analysis
jq 'select(.request.path | contains("secret"))' /var/log/vault/audit.log
```

### Backup and Recovery
```bash
# Raft snapshot
vault operator raft snapshot save backup-$(date +%Y%m%d).snap

# Automated backup
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
vault operator raft snapshot save /backup/vault-$DATE.snap
aws s3 cp /backup/vault-$DATE.snap s3://vault-backups/

# Restore
vault operator raft snapshot restore backup.snap
```

---

## Performance Tuning

### Connection Pooling
```hcl
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"

  # Increase connection pool
  max_parallel = 128
}
```

### Rate Limiting
```hcl
# Configure rate limits
vault write sys/quotas/rate-limit/global \
  rate=10000 \
  interval=1s

# Per-path limits
vault write sys/quotas/rate-limit/database \
  path="database/" \
  rate=100 \
  interval=1s
```

---

## Security Checklist

- [ ] Use TLS for all communications
- [ ] Enable audit logging
- [ ] Implement least privilege policies
- [ ] Use short-lived tokens/leases
- [ ] Enable auto-seal (KMS)
- [ ] Regular snapshots/backups
- [ ] Monitor for anomalies
- [ ] Rotate root credentials
- [ ] Use namespaces for isolation
- [ ] Implement MFA for sensitive paths
- [ ] Regular security audits
- [ ] Keep Vault updated
