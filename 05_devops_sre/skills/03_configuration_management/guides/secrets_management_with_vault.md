# Secrets Management with HashiCorp Vault - Complete Guide

## Overview

HashiCorp Vault is a tool for securely storing and accessing secrets, including passwords, API keys, certificates, and encryption keys. This guide covers production-ready Vault deployment and usage patterns.

## Table of Contents

1. [Why Vault?](#why-vault)
2. [Installation and Setup](#installation-and-setup)
3. [Core Concepts](#core-concepts)
4. [Secrets Engines](#secrets-engines)
5. [Authentication Methods](#authentication-methods)
6. [Policies and Access Control](#policies-and-access-control)
7. [Dynamic Secrets](#dynamic-secrets)
8. [High Availability Setup](#high-availability-setup)
9. [Application Integration](#application-integration)
10. [Best Practices](#best-practices)

## Why Vault?

### Problems Vault Solves

1. **Hardcoded Secrets**: No more secrets in code or configuration files
2. **Static Credentials**: Dynamic secrets with automatic rotation
3. **Access Control**: Fine-grained policies for who can access what
4. **Audit Trail**: Complete audit log of all secret access
5. **Encryption**: Centralized encryption as a service
6. **Multi-Cloud**: Unified secrets management across environments

### Vault vs Alternatives

| Feature | Vault | AWS Secrets Manager | Azure Key Vault | Kubernetes Secrets |
|---------|-------|---------------------|-----------------|-------------------|
| Dynamic Secrets | ✅ | ❌ | ❌ | ❌ |
| Multi-Cloud | ✅ | ❌ | ❌ | ❌ |
| Encryption Service | ✅ | ❌ | ✅ | ❌ |
| PKI/Certificates | ✅ | ✅ | ✅ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ✅ |

## Installation and Setup

### Installing Vault

```bash
# Using package manager (Ubuntu/Debian)
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install vault

# Using binary
wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
unzip vault_1.15.0_linux_amd64.zip
sudo mv vault /usr/local/bin/

# Verify installation
vault version
```

### Development Server

Quick start for testing:

```bash
# Start dev server (NOT for production)
vault server -dev

# In another terminal, set environment
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Test connection
vault status
```

### Production Server Setup

Create configuration file `/etc/vault.d/vault.hcl`:

```hcl
# Storage backend - Using Raft (integrated storage)
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-1"
}

# Listener
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"
}

# API and cluster addresses
api_addr     = "https://vault-1.example.com:8200"
cluster_addr = "https://vault-1.example.com:8201"

# Enable UI
ui = true

# Auto-unseal using AWS KMS
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "your-kms-key-id"
}
```

Create systemd service `/etc/systemd/system/vault.service`:

```ini
[Unit]
Description=HashiCorp Vault
Documentation=https://www.vaultproject.io/docs/
Requires=network-online.target
After=network-online.target

[Service]
Type=notify
User=vault
Group=vault
ExecStart=/usr/local/bin/vault server -config=/etc/vault.d/vault.hcl
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

Start Vault:

```bash
# Create vault user
sudo useradd --system --home /opt/vault --shell /bin/false vault

# Set permissions
sudo chown -R vault:vault /opt/vault /etc/vault.d

# Start service
sudo systemctl enable vault
sudo systemctl start vault
```

### Initialize Vault

```bash
# Initialize (first time only)
vault operator init

# This outputs unseal keys and root token
# SAVE THESE SECURELY!

# Example output:
# Unseal Key 1: abc123...
# Unseal Key 2: def456...
# Unseal Key 3: ghi789...
# Unseal Key 4: jkl012...
# Unseal Key 5: mno345...
# Initial Root Token: s.xyz789...

# Unseal Vault (requires 3 of 5 keys by default)
vault operator unseal # Enter key 1
vault operator unseal # Enter key 2
vault operator unseal # Enter key 3

# Login with root token
vault login s.xyz789...
```

## Core Concepts

### Paths

Everything in Vault is path-based:

```bash
# Secret paths
secret/data/myapp/prod/database
secret/data/myapp/prod/api-keys

# System paths
sys/policies/acl/
sys/auth/
sys/mounts/

# Authentication paths
auth/approle/
auth/kubernetes/
```

### Secrets Engines

Secrets engines store, generate, or encrypt data:

```bash
# Enable KV v2 secrets engine
vault secrets enable -version=2 -path=secret kv

# List secrets engines
vault secrets list

# Disable secrets engine
vault secrets disable secret/
```

### Policies

Policies define access control:

```hcl
# Read-only access to app secrets
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

# Full access to dev environment
path "secret/data/dev/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Deny access to production
path "secret/data/prod/*" {
  capabilities = ["deny"]
}
```

## Secrets Engines

### Key-Value (KV) Secrets

Static key-value pairs with versioning:

```bash
# Enable KV v2
vault secrets enable -version=2 -path=secret kv

# Store secrets
vault kv put secret/myapp/prod \
  database_url="postgresql://..." \
  api_key="sk-1234567890" \
  jwt_secret="super-secret"

# Read secrets
vault kv get secret/myapp/prod

# Get specific field
vault kv get -field=api_key secret/myapp/prod

# Get as JSON
vault kv get -format=json secret/myapp/prod

# List secrets
vault kv list secret/myapp/

# Delete secret (soft delete - can be recovered)
vault kv delete secret/myapp/prod

# Permanently delete all versions
vault kv metadata delete secret/myapp/prod

# Get secret version history
vault kv metadata get secret/myapp/prod

# Get specific version
vault kv get -version=2 secret/myapp/prod

# Rollback to previous version
vault kv rollback -version=1 secret/myapp/prod
```

### Database Secrets

Dynamic database credentials:

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="myapp-role" \
  connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb?sslmode=require" \
  username="vault_admin" \
  password="admin_password"

# Create role for application
vault write database/roles/myapp-role \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Generate credentials
vault read database/creds/myapp-role

# Output:
# Key                Value
# lease_id           database/creds/myapp-role/abc123
# lease_duration     1h
# username           v-myapp-role-xyz789
# password           A1B2C3D4E5F6

# Rotate root credentials
vault write -f database/rotate-root/postgresql
```

### AWS Secrets

Dynamic AWS credentials:

```bash
# Enable AWS secrets engine
vault secrets enable aws

# Configure AWS credentials
vault write aws/config/root \
  access_key=AKIAIOSFODNN7EXAMPLE \
  secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  region=us-east-1

# Create role
vault write aws/roles/deploy-role \
  credential_type=iam_user \
  policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*"
    }
  ]
}
EOF

# Generate credentials
vault read aws/creds/deploy-role
```

### PKI/Certificates

Certificate authority and certificate generation:

```bash
# Enable PKI secrets engine
vault secrets enable pki

# Tune max lease TTL
vault secrets tune -max-lease-ttl=87600h pki

# Generate root CA
vault write -field=certificate pki/root/generate/internal \
  common_name="example.com" \
  ttl=87600h > CA_cert.crt

# Configure CA and CRL URLs
vault write pki/config/urls \
  issuing_certificates="http://vault.example.com:8200/v1/pki/ca" \
  crl_distribution_points="http://vault.example.com:8200/v1/pki/crl"

# Create role for issuing certificates
vault write pki/roles/example-dot-com \
  allowed_domains="example.com" \
  allow_subdomains=true \
  max_ttl="720h"

# Issue certificate
vault write pki/issue/example-dot-com \
  common_name="web.example.com" \
  ttl="24h"
```

## Authentication Methods

### AppRole (for applications)

```bash
# Enable AppRole
vault auth enable approle

# Create policy
vault policy write myapp-policy - <<EOF
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
path "database/creds/myapp-role" {
  capabilities = ["read"]
}
EOF

# Create AppRole
vault write auth/approle/role/myapp \
  token_policies="myapp-policy" \
  token_ttl=1h \
  token_max_ttl=4h

# Get Role ID (permanent)
vault read auth/approle/role/myapp/role-id

# Get Secret ID (one-time or limited use)
vault write -f auth/approle/role/myapp/secret-id

# Login with AppRole
vault write auth/approle/login \
  role_id="abc-123" \
  secret_id="def-456"
```

### Kubernetes Authentication

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure Kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc:443" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

# Create role for Kubernetes service account
vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp \
  bound_service_account_namespaces=default \
  policies=myapp-policy \
  ttl=1h

# In pod, login using service account token
vault write auth/kubernetes/login \
  role=myapp \
  jwt=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
```

### LDAP Authentication

```bash
# Enable LDAP auth
vault auth enable ldap

# Configure LDAP
vault write auth/ldap/config \
  url="ldaps://ldap.example.com" \
  userdn="ou=users,dc=example,dc=com" \
  groupdn="ou=groups,dc=example,dc=com" \
  binddn="cn=vault,ou=users,dc=example,dc=com" \
  bindpass="password"

# Map LDAP groups to policies
vault write auth/ldap/groups/engineers policies=dev-policy
vault write auth/ldap/groups/operations policies=ops-policy

# Login with LDAP
vault login -method=ldap username=john.doe
```

## Policies and Access Control

### Writing Policies

```hcl
# Application read-only policy
path "secret/data/myapp/prod/*" {
  capabilities = ["read", "list"]
}

# Allow token renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# DevOps full access to infrastructure secrets
path "secret/data/infrastructure/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Read AWS dynamic credentials
path "aws/creds/deploy-role" {
  capabilities = ["read"]
}

# Pattern matching with + (single segment) and * (glob)
path "secret/data/team-+/prod/*" {
  capabilities = ["read"]
}

# Deny overrides all other permissions
path "secret/data/super-secret/*" {
  capabilities = ["deny"]
}
```

### Apply Policies

```bash
# Create policy from file
vault policy write myapp-policy policy.hcl

# Create policy from stdin
vault policy write dev-policy - <<EOF
path "secret/data/dev/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF

# List policies
vault policy list

# Read policy
vault policy read myapp-policy

# Delete policy
vault policy delete myapp-policy
```

## Dynamic Secrets

### PostgreSQL Example

Complete workflow:

```bash
# 1. Enable database engine
vault secrets enable database

# 2. Configure database connection
vault write database/config/mypostgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="*" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.example.com:5432/mydb?sslmode=require" \
  username="vault_admin" \
  password="admin_password" \
  password_authentication="scram-sha-256"

# 3. Create role with SQL statements
vault write database/roles/myapp \
  db_name=mypostgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE myapp_role; \
    GRANT CONNECT ON DATABASE mydb TO \"{{name}}\";" \
  revocation_statements="REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM \"{{name}}\"; \
    REVOKE USAGE ON SCHEMA public FROM \"{{name}}\"; \
    DROP ROLE IF EXISTS \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# 4. Request credentials
vault read database/creds/myapp

# 5. Renew lease
vault lease renew database/creds/myapp/abc123

# 6. Revoke lease
vault lease revoke database/creds/myapp/abc123
```

## High Availability Setup

### Raft Storage (Recommended)

```hcl
# Node 1 configuration
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
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"
}

api_addr     = "https://vault-1.example.com:8200"
cluster_addr = "https://vault-1.example.com:8201"
```

Initialize cluster:

```bash
# On node 1
vault operator init

# Unseal all nodes
vault operator unseal # Repeat 3 times on each node

# Join additional nodes
vault operator raft join https://vault-1.example.com:8200

# Check cluster status
vault operator raft list-peers
```

## Application Integration

### Python Example

```python
import hvac
import os

# Initialize client
client = hvac.Client(
    url=os.getenv('VAULT_ADDR'),
    token=os.getenv('VAULT_TOKEN')
)

# Or use AppRole
client = hvac.Client(url=os.getenv('VAULT_ADDR'))
client.auth.approle.login(
    role_id=os.getenv('ROLE_ID'),
    secret_id=os.getenv('SECRET_ID')
)

# Read KV secret
secret = client.secrets.kv.v2.read_secret_version(
    path='myapp/prod',
    mount_point='secret'
)
db_password = secret['data']['data']['database_password']

# Read dynamic database credentials
db_creds = client.read('database/creds/myapp-role')
db_user = db_creds['data']['username']
db_pass = db_creds['data']['password']

# Use credentials
connection = psycopg2.connect(
    host="db.example.com",
    database="mydb",
    user=db_user,
    password=db_pass
)
```

### Node.js Example

```javascript
const vault = require('node-vault')({
  apiVersion: 'v1',
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN
});

// Read secret
async function getSecrets() {
  const result = await vault.read('secret/data/myapp/prod');
  const secrets = result.data.data;

  return {
    databaseUrl: secrets.database_url,
    apiKey: secrets.api_key
  };
}

// Get dynamic credentials
async function getDatabaseCreds() {
  const result = await vault.read('database/creds/myapp-role');
  return {
    username: result.data.username,
    password: result.data.password,
    leaseId: result.lease_id,
    leaseDuration: result.lease_duration
  };
}
```

## Best Practices

### 1. Never Use Root Token in Production

```bash
# Create admin policy
vault policy write admin - <<EOF
path "*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
EOF

# Create admin token with TTL
vault token create -policy=admin -ttl=1h

# Revoke root token
vault token revoke <root-token>
```

### 2. Enable Audit Logging

```bash
# Enable file audit
vault audit enable file file_path=/var/log/vault_audit.log

# Enable syslog audit
vault audit enable syslog

# View audit logs
tail -f /var/log/vault_audit.log | jq
```

### 3. Use Namespaces (Enterprise)

```bash
# Create namespace
vault namespace create team-a

# Use namespace
export VAULT_NAMESPACE=team-a
vault kv put secret/app database_url=...
```

### 4. Rotate Secrets Regularly

```bash
# Rotate database root credentials
vault write -f database/rotate-root/postgresql

# Set up automatic rotation
vault write database/config/postgresql \
  ...
  rotation_period="24h"
```

### 5. Use Least Privilege

```bash
# Create minimal policy
vault policy write app-minimal - <<EOF
# Only read application secrets
path "secret/data/myapp/prod" {
  capabilities = ["read"]
}

# Only create database credentials
path "database/creds/myapp-role" {
  capabilities = ["read"]
}
EOF
```

## Troubleshooting

### Check Vault Status

```bash
vault status
vault operator members
vault operator raft list-peers
```

### Debug Authentication

```bash
# Check token capabilities
vault token capabilities secret/data/myapp/prod

# Lookup token info
vault token lookup

# Test policy
vault policy read myapp-policy
```

### Seal/Unseal Issues

```bash
# Check seal status
vault status

# Unseal manually
vault operator unseal

# Auto-unseal with cloud KMS (recommended)
# AWS: Use "awskms" seal
# Azure: Use "azurekeyvault" seal
# GCP: Use "gcpckms" seal
```

## Next Steps

1. **Set up High Availability**: Deploy 3+ node cluster
2. **Enable Auto-Unseal**: Use cloud KMS for automatic unsealing
3. **Implement Dynamic Secrets**: Convert static secrets to dynamic
4. **Set up Monitoring**: Integrate with Prometheus/Grafana
5. **Enable Replication** (Enterprise): DR and Performance replication

## Resources

- [Official Documentation](https://www.vaultproject.io/docs)
- [Learn Vault](https://learn.hashicorp.com/vault)
- [API Documentation](https://www.vaultproject.io/api-docs)
- [Best Practices](https://learn.hashicorp.com/tutorials/vault/pattern-approle)

---

**Last Updated**: 2025-11-19
**Version**: 1.0
