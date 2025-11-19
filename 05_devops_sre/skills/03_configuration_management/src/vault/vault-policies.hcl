# Vault Policy Examples
# Policies define what secrets a user/application can access

# Admin Policy - Full access to Vault
path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "sys/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# -----------------------------------------------------------

# Application Policy - Read-only access to app secrets
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}

# Allow application to renew its own token
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# -----------------------------------------------------------

# Database Dynamic Credentials Policy
path "database/creds/myapp-role" {
  capabilities = ["read"]
}

path "database/static-creds/myapp-user" {
  capabilities = ["read"]
}

# -----------------------------------------------------------

# DevOps Team Policy - Manage infrastructure secrets
path "secret/data/infrastructure/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/infrastructure/*" {
  capabilities = ["list", "read"]
}

# Read AWS credentials
path "aws/creds/deploy-role" {
  capabilities = ["read"]
}

# Manage PKI certificates
path "pki/issue/web-server" {
  capabilities = ["create", "update"]
}

# -----------------------------------------------------------

# Developer Policy - Read development secrets
path "secret/data/dev/*" {
  capabilities = ["read", "list"]
}

path "secret/data/staging/*" {
  capabilities = ["read", "list"]
}

# No access to production secrets
path "secret/data/prod/*" {
  capabilities = ["deny"]
}

# -----------------------------------------------------------

# CI/CD Pipeline Policy
path "secret/data/cicd/*" {
  capabilities = ["read"]
}

# Read deployment credentials
path "aws/sts/deployment-role" {
  capabilities = ["read"]
}

# Read Kubernetes credentials
path "kubernetes/creds/deploy" {
  capabilities = ["read"]
}

# -----------------------------------------------------------

# Database Team Policy
path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Manage database connections
path "sys/mounts/database" {
  capabilities = ["create", "read", "update", "delete"]
}

# -----------------------------------------------------------

# Security Team Policy - Audit and compliance
path "sys/audit" {
  capabilities = ["read", "list", "sudo"]
}

path "sys/audit-hash" {
  capabilities = ["create", "update"]
}

path "sys/capabilities" {
  capabilities = ["create", "update"]
}

path "sys/policies/acl/*" {
  capabilities = ["read", "list"]
}

# -----------------------------------------------------------

# Secrets Rotation Policy (for automated rotation)
path "secret/data/rotation/*" {
  capabilities = ["read", "update"]
}

path "database/rotate-root/*" {
  capabilities = ["update"]
}

# -----------------------------------------------------------

# Monitoring Policy (for Prometheus exporters)
path "sys/metrics" {
  capabilities = ["read"]
}

path "sys/health" {
  capabilities = ["read", "list"]
}
