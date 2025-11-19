#!/bin/bash
# Vault Operations Script - Production-ready secrets management operations
# This script demonstrates common Vault operations for configuration management

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-https://vault.example.com:8200}"
export VAULT_ADDR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Vault is initialized
check_vault_status() {
    log_info "Checking Vault status..."
    if vault status &> /dev/null; then
        log_info "Vault is accessible and initialized"
        return 0
    else
        log_error "Vault is not accessible or not initialized"
        return 1
    fi
}

# Initialize Vault (first-time setup)
initialize_vault() {
    log_info "Initializing Vault..."

    vault operator init \
        -key-shares=5 \
        -key-threshold=3 \
        -format=json > vault-init-keys.json

    log_info "Vault initialized. Keys saved to vault-init-keys.json"
    log_warn "IMPORTANT: Store these keys securely and delete this file!"
}

# Unseal Vault
unseal_vault() {
    log_info "Unsealing Vault..."

    # Read unseal keys from file or prompt
    for i in {1..3}; do
        echo "Enter unseal key $i:"
        read -s UNSEAL_KEY
        vault operator unseal "$UNSEAL_KEY"
    done

    log_info "Vault unsealed successfully"
}

# Enable secrets engines
setup_secrets_engines() {
    log_info "Setting up secrets engines..."

    # Enable KV v2 secrets engine
    vault secrets enable -version=2 -path=secret kv || log_warn "KV secrets engine already enabled"

    # Enable database secrets engine
    vault secrets enable database || log_warn "Database secrets engine already enabled"

    # Enable AWS secrets engine
    vault secrets enable -path=aws aws || log_warn "AWS secrets engine already enabled"

    # Enable PKI secrets engine
    vault secrets enable pki || log_warn "PKI secrets engine already enabled"
    vault secrets tune -max-lease-ttl=87600h pki

    log_info "Secrets engines configured"
}

# Configure database dynamic secrets
setup_database_secrets() {
    local DB_HOST="$1"
    local DB_NAME="$2"
    local DB_ADMIN_USER="$3"
    local DB_ADMIN_PASSWORD="$4"

    log_info "Configuring PostgreSQL dynamic secrets..."

    # Configure database connection
    vault write database/config/postgresql \
        plugin_name=postgresql-database-plugin \
        allowed_roles="myapp-role" \
        connection_url="postgresql://{{username}}:{{password}}@${DB_HOST}:5432/${DB_NAME}?sslmode=require" \
        username="${DB_ADMIN_USER}" \
        password="${DB_ADMIN_PASSWORD}"

    # Create role for application
    vault write database/roles/myapp-role \
        db_name=postgresql \
        creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
        default_ttl="1h" \
        max_ttl="24h"

    log_info "Database secrets configured"
}

# Store application secrets
store_app_secrets() {
    local ENV="$1"
    local APP_NAME="$2"

    log_info "Storing secrets for ${APP_NAME} in ${ENV}..."

    # Store database credentials
    vault kv put "secret/${ENV}/${APP_NAME}/database" \
        host="db.${ENV}.example.com" \
        port="5432" \
        username="${APP_NAME}_user" \
        password="$(openssl rand -base64 32)" \
        database="${APP_NAME}_${ENV}"

    # Store API keys
    vault kv put "secret/${ENV}/${APP_NAME}/api" \
        stripe_key="sk_test_$(openssl rand -hex 16)" \
        sendgrid_key="SG.$(openssl rand -base64 22)" \
        google_api_key="AIza$(openssl rand -base64 30)"

    # Store encryption keys
    vault kv put "secret/${ENV}/${APP_NAME}/encryption" \
        jwt_secret="$(openssl rand -base64 64)" \
        aes_key="$(openssl rand -hex 32)" \
        hmac_secret="$(openssl rand -base64 32)"

    log_info "Secrets stored successfully"
}

# Retrieve secrets
get_secrets() {
    local SECRET_PATH="$1"

    log_info "Retrieving secrets from ${SECRET_PATH}..."
    vault kv get -format=json "$SECRET_PATH" | jq -r '.data.data'
}

# Rotate database credentials
rotate_database_creds() {
    local DB_CONNECTION="$1"

    log_info "Rotating database root credentials..."
    vault write -f "database/rotate-root/${DB_CONNECTION}"
    log_info "Root credentials rotated"
}

# Setup policies
setup_policies() {
    log_info "Creating Vault policies..."

    # Application policy
    vault policy write myapp-policy - <<EOF
path "secret/data/prod/myapp/*" {
  capabilities = ["read"]
}

path "database/creds/myapp-role" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}
EOF

    # DevOps policy
    vault policy write devops-policy - <<EOF
path "secret/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "aws/creds/*" {
  capabilities = ["read"]
}
EOF

    log_info "Policies created"
}

# Enable authentication methods
setup_auth_methods() {
    log_info "Setting up authentication methods..."

    # Enable AppRole authentication
    vault auth enable approle || log_warn "AppRole already enabled"

    # Enable Kubernetes authentication
    vault auth enable kubernetes || log_warn "Kubernetes auth already enabled"

    # Configure Kubernetes auth
    vault write auth/kubernetes/config \
        kubernetes_host="https://kubernetes.default.svc:443" \
        kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

    log_info "Authentication methods configured"
}

# Create AppRole for application
create_approle() {
    local ROLE_NAME="$1"
    local POLICIES="$2"

    log_info "Creating AppRole: ${ROLE_NAME}..."

    vault write "auth/approle/role/${ROLE_NAME}" \
        token_policies="${POLICIES}" \
        token_ttl=1h \
        token_max_ttl=4h \
        secret_id_ttl=0

    # Get role ID and secret ID
    ROLE_ID=$(vault read -field=role_id "auth/approle/role/${ROLE_NAME}/role-id")
    SECRET_ID=$(vault write -field=secret_id -f "auth/approle/role/${ROLE_NAME}/secret-id")

    log_info "AppRole created:"
    echo "Role ID: ${ROLE_ID}"
    echo "Secret ID: ${SECRET_ID}"
}

# Backup Vault data
backup_vault() {
    local BACKUP_DIR="${1:-/var/backups/vault}"
    local TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    log_info "Creating Vault backup..."

    mkdir -p "$BACKUP_DIR"

    # Snapshot Vault data
    vault operator raft snapshot save "${BACKUP_DIR}/vault-snapshot-${TIMESTAMP}.snap"

    # Export secrets (for disaster recovery)
    vault kv list -format=json secret/ | jq -r '.[]' | while read -r path; do
        vault kv get -format=json "secret/${path}" > "${BACKUP_DIR}/secret-${path//\//-}-${TIMESTAMP}.json"
    done

    log_info "Backup completed: ${BACKUP_DIR}/vault-snapshot-${TIMESTAMP}.snap"
}

# Health check
health_check() {
    log_info "Performing health check..."

    # Check Vault status
    if ! vault status &> /dev/null; then
        log_error "Vault is not accessible"
        return 1
    fi

    # Check seal status
    if vault status -format=json | jq -r '.sealed' | grep -q "true"; then
        log_warn "Vault is sealed"
        return 1
    fi

    # Check leadership
    if vault status -format=json | jq -r '.is_self' | grep -q "true"; then
        log_info "This node is the leader"
    else
        log_info "This node is a follower"
    fi

    log_info "Health check passed"
    return 0
}

# Main menu
main() {
    case "${1:-}" in
        init)
            initialize_vault
            ;;
        unseal)
            unseal_vault
            ;;
        setup)
            check_vault_status
            setup_secrets_engines
            setup_policies
            setup_auth_methods
            ;;
        store-secrets)
            store_app_secrets "${2}" "${3}"
            ;;
        get-secrets)
            get_secrets "${2}"
            ;;
        setup-db)
            setup_database_secrets "${2}" "${3}" "${4}" "${5}"
            ;;
        create-approle)
            create_approle "${2}" "${3}"
            ;;
        rotate-db)
            rotate_database_creds "${2}"
            ;;
        backup)
            backup_vault "${2:-}"
            ;;
        health)
            health_check
            ;;
        *)
            echo "Usage: $0 {init|unseal|setup|store-secrets|get-secrets|setup-db|create-approle|rotate-db|backup|health}"
            echo ""
            echo "Commands:"
            echo "  init                                  - Initialize Vault"
            echo "  unseal                                - Unseal Vault"
            echo "  setup                                 - Setup secrets engines and auth"
            echo "  store-secrets <env> <app>            - Store application secrets"
            echo "  get-secrets <path>                   - Retrieve secrets"
            echo "  setup-db <host> <db> <user> <pass>  - Configure database secrets"
            echo "  create-approle <name> <policies>     - Create AppRole"
            echo "  rotate-db <connection>               - Rotate database credentials"
            echo "  backup [dir]                         - Backup Vault data"
            echo "  health                               - Health check"
            exit 1
            ;;
    esac
}

main "$@"
