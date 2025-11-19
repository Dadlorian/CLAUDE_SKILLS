# Configuration Management - Elite Professional Practices

**Automated, consistent system and application configuration at scale**

---

## Overview

Configuration Management ensures systems and applications are configured consistently, securely, and repeatably across all environments. It separates code (immutable) from configuration (environment-specific), enabling the same application to run in development, staging, and production with appropriate settings for each environment.

You are an expert in designing configuration management strategies that enable organizations to manage application and infrastructure configuration safely, efficiently, and auditably across thousands of systems.

## Core Principles

### 1. Externalize Configuration

Configuration should be external to application code and environment-specific.

```java
// BAD: Hardcoded configuration
public class DatabaseConfig {
  public static final String DB_URL = "jdbc:mysql://prod.db.company.com:3306/app";
  public static final String DB_USER = "dbuser";
  public static final String DB_PASSWORD = "hardcoded_password"; // SECURITY RISK!
}

// GOOD: Configuration from environment
public class DatabaseConfig {
  public DatabaseConfig() {
    this.dbUrl = System.getenv("DATABASE_URL");
    this.dbUser = System.getenv("DATABASE_USER");
    this.dbPassword = System.getenv("DATABASE_PASSWORD"); // From vault
  }
}
```

**Benefits**:
- Same binary/container runs in all environments
- Secrets not in source code
- Configuration changes don't require rebuilds
- Easy to rotate secrets and update settings

### 2. 12-Factor App Configuration

```yaml
# Twelve-Factor Application Configuration Pattern

# 1. Codebase: One codebase, multiple deployments
#    └─ Git repository shared across all environments

# 2. Dependencies: Explicitly declared and isolated
#    └─ requirements.txt, package.json, Gemfile in version control

# 3. Config: Store configuration in environment variables
DATABASE_URL: "postgresql://user:pass@localhost/dbname"
REDIS_URL: "redis://localhost:6379"
API_KEY: "secret_key_from_vault"
ENVIRONMENT: "production"

# 4. Backing Services: Treat as attached resources
#    └─ Database, cache, message queue are external services

# 5. Build/Run Separation
#    Build stage: Dependencies, compilation, artifact creation
#    Run stage: Start application with environment configuration

# 6. Stateless Processes
#    └─ Application stores no local state; persistent data in backing services

# 7. Port Binding
#    └─ Service is self-contained and exports HTTP via port binding
#    PORT: "8080"

# 8. Concurrency: Scale by deploying multiple instances
#    WORKER_PROCESSES: "4"

# 9. Disposability: Fast startup, graceful shutdown
#    └─ Handle SIGTERM for clean shutdown

# 10. Dev/Prod Parity: Environments as similar as possible
#     └─ Same versions of services, same configuration patterns

# 11. Logs: Write to stdout, managed by execution environment
#     └─ Application logs to console; infrastructure captures and aggregates

# 12. Admin Tasks: Run as one-off processes
#     └─ Database migrations, cache warming run separately
```

### 3. Configuration Hierarchy

```
Global/Default
    ↓
Environment-specific (dev, staging, production)
    ↓
Application-specific (microservice, worker, api)
    ↓
Runtime overrides (environment variables, command-line flags)
```

**Example**:

```yaml
# config/defaults.yaml (committed to Git)
database:
  pool_size: 10
  timeout: 30
redis:
  ttl: 3600

---

# config/production.yaml (committed to Git)
database:
  pool_size: 50  # Override: larger pool in production
  timeout: 60    # Override: longer timeout
redis:
  ttl: 86400     # Override: longer TTL in production

---

# Environment variables (from vault/secrets manager)
DATABASE_PASSWORD: "secret_from_vault"
API_KEY: "api_key_from_vault"
ENCRYPTION_KEY: "encryption_key_from_vault"

---

# Runtime overrides (when running application)
DATABASE_POOL_SIZE=100  # Override again if needed
```

## Core Competencies

### 1. Secrets Management

Secrets (passwords, API keys, encryption keys) require special handling.

**Anti-patterns**:
```bash
# WRONG: Hardcoded in code
API_KEY="sk-1234567890abcdef"

# WRONG: Committed to Git
echo "DATABASE_PASSWORD=mysecret" > .env
git add .env && git commit

# WRONG: Logged in plain text
logger.info("Connecting to database with password: " + password)
```

**Best Practices**:

```bash
# Store secrets in dedicated vault
vault write secret/myapp/prod \
  database_password="secure_password" \
  api_key="secure_key"

# Retrieve at runtime
DATABASE_PASSWORD=$(vault kv get -field=database_password secret/myapp/prod)

# Or use HashiCorp Vault dynamic secrets
vault read database/static-creds/myapp-user  # Generates temporary credentials
```

**Hashicorp Vault**:

```bash
# Start Vault
vault server -dev

# Store secrets
vault kv put secret/myapp/prod \
  db_password="mypassword" \
  api_key="myapikey" \
  jwt_secret="jwtsecret"

# Retrieve secrets
vault kv get secret/myapp/prod
vault kv get -field=db_password secret/myapp/prod

# Dynamic secrets (auto-rotate)
vault read database/static-creds/myapp-user
```

### 2. Feature Flags

Decouple deployment from feature release.

```python
# Using LaunchDarkly or similar
from ldclient import Context
import ldclient

ldclient.set_config("sdk_key")

# Check feature flag at runtime
context = Context.builder("user@example.com").build()

# Simple flag
if client.variation("new-checkout-flow", context, False):
    # New checkout logic
    return new_checkout_handler()
else:
    # Existing checkout logic
    return legacy_checkout_handler()

# Percentage rollout
if client.variation("new-search-algorithm", context, False):
    return new_search(query)  # 10% of users
else:
    return legacy_search(query)  # 90% of users

# User-based targeting
if client.variation("premium-features", context, False):
    if user.is_premium:
        return enable_premium_features()
```

**Benefits**:
- Deploy code before enabling feature
- Quick kill switch for problems
- A/B testing and gradual rollout
- No need to rebuild/redeploy to disable feature

### 3. Configuration Drift Detection

**Problem**: Actual system configuration differs from declared configuration

```yaml
# Configuration Management Tool (Ansible)

# Desired state
- name: Ensure NTP is installed and running
  hosts: servers
  tasks:
    - name: Install NTP
      package:
        name: ntp
        state: present

    - name: Configure NTP
      copy:
        content: |
          server 0.pool.ntp.org
          server 1.pool.ntp.org
        dest: /etc/ntp.conf

    - name: Start NTP service
      service:
        name: ntp
        state: started
        enabled: yes

# Running playbook shows drift if:
# - NTP not installed
# - NTP configuration differs
# - NTP service not running

# Tool automatically fixes drift (idempotent)
```

### 4. Configuration Validation

```python
# Pydantic for Python configuration validation
from pydantic import BaseSettings, validator, conint

class Settings(BaseSettings):
    # Required fields
    database_url: str
    api_key: str

    # Optional with defaults
    debug: bool = False
    workers: conint(ge=1, le=256) = 4
    request_timeout: conint(ge=1) = 30

    # Validation
    @validator('database_url')
    def validate_db_url(cls, v):
        if not v.startswith(('postgresql://', 'mysql://')):
            raise ValueError('Database URL must be valid')
        return v

    @validator('api_key')
    def validate_api_key(cls, v):
        if len(v) < 32:
            raise ValueError('API key must be at least 32 characters')
        return v

    class Config:
        env_file = '.env'

# Load and validate configuration
settings = Settings()
# Raises ValidationError if invalid
```

## Technology Stack

### Ansible (Agentless Configuration)

```yaml
# Ansible playbook for application deployment
---
- name: Deploy application
  hosts: web_servers
  become: yes  # Run with sudo

  vars:
    app_version: "1.2.3"
    app_user: "appuser"
    app_home: "/opt/myapp"

  tasks:
    - name: Create application user
      user:
        name: "{{ app_user }}"
        home: "{{ app_home }}"
        shell: /bin/false
        createhome: yes

    - name: Download application artifact
      get_url:
        url: "https://artifactory.company.com/releases/myapp-{{ app_version }}.jar"
        dest: "{{ app_home }}/app.jar"
        owner: "{{ app_user }}"

    - name: Create application configuration
      template:
        src: application.properties.j2
        dest: "{{ app_home }}/application.properties"
        owner: "{{ app_user }}"
      notify: restart application

    - name: Create systemd service
      template:
        src: myapp.service.j2
        dest: /etc/systemd/system/myapp.service
      notify: restart application

    - name: Ensure application is running
      systemd:
        name: myapp
        state: started
        enabled: yes

  handlers:
    - name: restart application
      systemd:
        name: myapp
        state: restarted
```

**Advantages**:
- Agentless (no software to install on targets)
- YAML playbooks (readable)
- Excellent for configuration management
- Large module ecosystem
- Great documentation

### Chef (Server-Based Configuration)

```ruby
# Chef recipe
describe "Apache Configuration" do
  # Install Apache
  package 'apache2' do
    action :install
  end

  # Configure Apache
  template '/etc/apache2/apache2.conf' do
    source 'apache2.conf.erb'
    variables lazy {
      {
        max_clients: node['apache']['max_clients'],
        document_root: node['apache']['document_root']
      }
    }
    notifies :restart, 'service[apache2]'
  end

  # Ensure service is running
  service 'apache2' do
    action [:enable, :start]
  end
end
```

**Advantages**:
- Ruby DSL (powerful)
- Test Kitchen for testing recipes
- Server-based configuration tracking
- Good for complex orchestration

### Puppet (Enterprise Configuration)

```puppet
# Puppet manifest
class apache {
  package { 'apache2':
    ensure => installed,
  }

  file { '/etc/apache2/apache2.conf':
    ensure  => present,
    source  => 'puppet:///modules/apache/apache2.conf',
    require => Package['apache2'],
    notify  => Service['apache2'],
  }

  service { 'apache2':
    ensure    => running,
    enable    => true,
    subscribe => File['/etc/apache2/apache2.conf'],
  }
}

node 'webserver1.example.com' {
  include apache
}
```

**Advantages**:
- Declarative language
- Server-based state tracking
- Enterprise-grade tooling
- Strong compliance/audit features

### Vault (Secrets Management)

```hcl
# Vault configuration
vault {
  address = "https://vault.company.com:8200"
  retry {
    num_retries = 3
  }
}

# Template for retrieving secrets
template {
  source      = "/etc/vault/application.properties.tpl"
  destination = "/opt/myapp/application.properties"
  command     = "/opt/myapp/restart.sh"
}

# Template file
# application.properties.tpl
database.password={{ with secret "secret/myapp/prod" }}{{ .Data.data.password }}{{ end }}
api.key={{ with secret "secret/myapp/prod" }}{{ .Data.data.api_key }}{{ end }}
```

### LaunchDarkly (Feature Flags)

```javascript
// Feature flag client initialization
import * as ld from '@launchdarkly/js-client-sdk';

const client = ld.initialize('sdk_key', {
  key: 'user@example.com'
});

// Check feature flag
client.variation('new-dashboard', false, (value) => {
  if (value) {
    renderNewDashboard();
  } else {
    renderLegacyDashboard();
  }
});

// Track custom events
client.track('checkout-completed', { revenue: 99.99 });

// Context updates
client.identify({
  key: 'user@example.com',
  isPremium: true,
  accountValue: 5000
});
```

## Implementation Patterns

### Environment-Specific Configuration

```
config/
├── defaults.yaml          # All environments
├── development.yaml       # Dev-only overrides
├── staging.yaml          # Staging-only overrides
└── production.yaml       # Production-only overrides
```

### Secrets Rotation

```bash
#!/bin/bash
# Rotate database password every 90 days

ROTATION_INTERVAL=7776000  # 90 days in seconds

# Check if rotation needed
current_secret=$(aws secretsmanager get-secret-value \
  --secret-id "prod/database/password" \
  --query SecretString --output text)

rotation_date=$(aws secretsmanager describe-secret \
  --secret-id "prod/database/password" \
  --query 'RotationRules.LastRotationDate')

if [[ $(date +%s) - $(date -d "$rotation_date" +%s) -gt $ROTATION_INTERVAL ]]; then
  # Generate new password
  new_password=$(openssl rand -base64 32)

  # Update in Vault
  vault kv put secret/prod/database password="$new_password"

  # Update in application secret store
  aws secretsmanager update-secret \
    --secret-id "prod/database/password" \
    --secret-string "$new_password"

  # Update in database
  # (application handles credential refresh)
fi
```

## Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.local
*.key
*.pem
secrets.yaml
credentials.json
```

### 2. Use Configuration Management Tools

```bash
# Centralize configuration in configuration management system
ansible-playbook site.yml  # Applies configuration consistently

# Or use Kubernetes ConfigMaps/Secrets
kubectl create configmap app-config \
  --from-file=config/

kubectl create secret generic app-secrets \
  --from-literal=database_password=secret
```

### 3. Implement Configuration Validation

```python
# Before deploying, validate configuration
def validate_configuration():
    required_vars = ['DATABASE_URL', 'API_KEY', 'ENCRYPTION_KEY']

    for var in required_vars:
        if var not in os.environ:
            raise ConfigurationError(f"Missing required variable: {var}")

    # Validate format
    if not is_valid_postgres_url(os.environ['DATABASE_URL']):
        raise ConfigurationError("Invalid DATABASE_URL format")

    if len(os.environ['API_KEY']) < 32:
        raise ConfigurationError("API_KEY too short")

if __name__ == '__main__':
    validate_configuration()
    # Run application
```

### 4. Test Configuration Changes

```bash
# Test on staging before production
ansible-playbook -i inventory/staging playbooks/deploy.yml --check
# --check shows what would change without applying

# Apply to staging first
ansible-playbook -i inventory/staging playbooks/deploy.yml

# Verify in staging
curl https://staging.example.com/health

# Then apply to production
ansible-playbook -i inventory/production playbooks/deploy.yml
```

### 5. Audit Configuration Changes

```yaml
# Enable audit logging in Vault
audit {
  file {
    path = "/vault/logs/audit.log"
  }
}

# Monitor configuration changes
- name: Monitor Vault audit logs
  hosts: localhost
  tasks:
    - name: Parse audit logs
      shell: |
        tail -f /vault/logs/audit.log | \
        jq 'select(.type=="request") | {timestamp, path, auth}'
      register: audit_logs
```

## Tools and Integration

**Configuration Validation**: Ansible lint, Puppet Lint, Rubocop
**Secret Management**: Vault, AWS Secrets Manager, Azure Key Vault
**Feature Flags**: LaunchDarkly, Unleash, Split.io
**Configuration Sync**: Consul, etcd, Kubernetes ConfigMaps

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Ansible, Chef, Puppet, HashiCorp, Spotify practices
