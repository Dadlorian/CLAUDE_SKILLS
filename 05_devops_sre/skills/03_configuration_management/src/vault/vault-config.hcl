# HashiCorp Vault Production Configuration
# This configuration demonstrates enterprise-grade secrets management

# Storage Backend - Using integrated storage (Raft)
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault-node-1"

  # Retry configuration for raft storage
  retry_join {
    leader_api_addr = "https://vault-node-1.example.com:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-node-2.example.com:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-node-3.example.com:8200"
  }
}

# Alternative: Using Consul as storage backend (for existing Consul clusters)
# storage "consul" {
#   address = "127.0.0.1:8500"
#   path    = "vault/"
#   token   = "your-consul-token"
# }

# Listener configuration
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file  = "/opt/vault/tls/vault.key"

  # Enable CORS for web UI
  cors_enabled = true
  cors_allowed_origins = ["https://vault.example.com"]

  # Telemetry headers
  telemetry {
    unauthenticated_metrics_access = false
  }
}

# High Availability Configuration
api_addr     = "https://vault-node-1.example.com:8200"
cluster_addr = "https://vault-node-1.example.com:8201"

# UI Configuration
ui = true

# Seal configuration - Auto-unseal using AWS KMS
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  endpoint   = "https://kms.us-east-1.amazonaws.com"
}

# Alternative: Azure Key Vault seal
# seal "azurekeyvault" {
#   tenant_id     = "your-tenant-id"
#   vault_name    = "your-keyvault-name"
#   key_name      = "vault-seal-key"
# }

# Telemetry - Send metrics to Prometheus
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname          = false

  # StatsD configuration
  statsd_address = "localhost:8125"
}

# Logging
log_level = "info"
log_format = "json"

# Performance tuning
disable_mlock = false
max_lease_ttl = "8760h"  # 1 year
default_lease_ttl = "168h"  # 1 week

# Entropy Augmentation (for additional randomness)
entropy "seal" {
  mode = "augmentation"
}

# Plugin directory
plugin_directory = "/opt/vault/plugins"
