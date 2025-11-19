# Fivetran Connectors Guide

## Overview
Fivetran is a fully managed ELT platform with 300+ connectors, automatic schema migrations, and enterprise-grade reliability.

## Key Features
- **Zero-Maintenance**: Automatic updates and schema changes
- **High Reliability**: 99.9% uptime SLA
- **Smart Sync**: Incremental updates, CDC where available
- **Column Hashing**: Automatic PII detection and hashing
- **Schema Drift**: Automatic column addition
- **Monitoring**: Built-in alerting and logs

## Popular Connectors

### Databases
```yaml
# PostgreSQL Connector
connector: postgres
schema: my_schema
host: database.example.com
port: 5432
database: production
user: fivetran_user
password: ${POSTGRES_PASSWORD}

# Advanced settings
update_method: XMIN  # or WAL (CDC)
sync_mode: SOFT_DELETE  # or HISTORY
```

### SaaS Applications
```yaml
# Salesforce
connector: salesforce
domain: login.salesforce.com  # or test.salesforce.com
security_token: ${SF_TOKEN}
username: integration@company.com
password: ${SF_PASSWORD}

# Sync settings
sync_frequency: 60  # minutes
historical_sync: true
custom_objects: true
```

### Cloud Storage
```yaml
# S3 Connector
connector: s3
bucket: my-data-bucket
role_arn: arn:aws:iam::123456789:role/FivetranRole
prefix: data/exports/

# File format
file_type: CSV
delimiter: ","
escape_char: "\\"
compression: GZIP
archive_pattern: "*.csv.gz"
```

## Setup Patterns

### PostgreSQL CDC Setup
```sql
-- Create Fivetran user
CREATE USER fivetran WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT CONNECT ON DATABASE production TO fivetran;
GRANT USAGE ON SCHEMA public TO fivetran;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fivetran;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO fivetran;

-- For CDC (WAL)
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- Create publication
CREATE PUBLICATION fivetran_publication FOR ALL TABLES;

-- Grant replication
ALTER USER fivetran WITH REPLICATION;
```

### MySQL CDC Setup
```sql
-- Create Fivetran user
CREATE USER 'fivetran'@'%' IDENTIFIED BY 'secure_password';

-- Grant permissions
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT
ON *.* TO 'fivetran'@'%';

-- Verify binlog enabled
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';  -- Must be ROW

-- Set retention
SET GLOBAL binlog_expire_logs_seconds = 604800;  -- 7 days
```

### Salesforce Configuration
```yaml
# Connect to Salesforce
1. Create Connected App in Salesforce
2. Generate OAuth tokens
3. Configure in Fivetran

# Optimize sync
sync_frequency: 60  # Hourly for most objects
exclude_objects:
  - ActivityHistory
  - EmailMessage  # If not needed
  - FeedComment

# Include custom objects
custom_objects: true
custom_object_prefix: MyApp__
```

## Schema Management

### Auto-Schema Detection
Fivetran automatically:
- Detects new columns
- Adds columns to destination
- Handles type changes
- Preserves historical data

```sql
-- Fivetran creates tables like:
-- <connector>_<schema>.<table>

-- Example: Salesforce Account table
SELECT * FROM salesforce.account;

-- Columns added automatically:
_fivetran_deleted BOOLEAN  -- Soft delete flag
_fivetran_synced TIMESTAMP  -- Last sync time
_fivetran_id VARCHAR  -- Unique row ID
```

### Column Blocking
```yaml
# Block sensitive columns
blocked_columns:
  - table: users
    columns:
      - ssn
      - credit_card
      - password_hash
```

### Column Hashing (PII Protection)
```yaml
# Auto-hash PII columns
hashed_columns:
  - table: customers
    columns:
      - email
      - phone
      - address

# Result in warehouse:
# email_hash: MD5 hash of email
# Original email not synced
```

## Sync Modes

### Full Table Sync
- Reloads entire table each sync
- Use for small, frequently changing tables
- No history tracking

```yaml
sync_mode: FULL_TABLE
```

### Incremental Sync
- Syncs only new/changed rows
- Uses modification timestamp
- Most efficient

```yaml
sync_mode: INCREMENTAL
update_method: MODIFIED_TIMESTAMP
primary_key: id
modification_timestamp: updated_at
```

### Soft Delete
- Marks deleted rows with `_fivetran_deleted`
- Preserves deleted records
- Recommended for most use cases

```yaml
sync_mode: SOFT_DELETE
update_method: XMIN  # PostgreSQL
```

### History Mode (CDC)
- Captures all changes over time
- Creates history table with change log
- Use for audit trails

```yaml
sync_mode: HISTORY
update_method: WAL  # PostgreSQL
```

## Destination Configuration

### Snowflake
```yaml
destination: snowflake
account: xy12345.us-east-1
warehouse: FIVETRAN_WH
database: RAW_DATA
schema_prefix: ""  # or "fivetran_"
user: FIVETRAN_USER
password: ${SNOWFLAKE_PASSWORD}
role: FIVETRAN_ROLE

# Performance tuning
warehouse_size: LARGE
auto_suspend_minutes: 5
```

### BigQuery
```yaml
destination: bigquery
project_id: my-project
dataset_location: US
credentials: ${GCP_SERVICE_ACCOUNT_JSON}

# Schema options
dataset_id: fivetran_data
time_partitioning: true  # Partition by _fivetran_synced
```

### Redshift
```yaml
destination: redshift
host: cluster.region.redshift.amazonaws.com
port: 5439
database: analytics
schema: fivetran
user: fivetran_user
password: ${REDSHIFT_PASSWORD}

# Performance
compression: ZSTD
distribution_key: id  # for dimension tables
sort_key: created_at  # for fact tables
```

## Monitoring & Alerting

### Webhook Notifications
```yaml
# Configure webhook for sync events
webhook_url: https://your-app.com/fivetran/webhooks
events:
  - sync_end
  - sync_failed
  - schema_changed
  - rows_synced_threshold

# Payload example:
{
  "connector_id": "abc123",
  "connector_name": "postgres_production",
  "event": "sync_end",
  "status": "success",
  "schema": "public",
  "table": "orders",
  "rows_synced": 15000,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Email Alerts
```yaml
alerts:
  - email: data-team@company.com
    events:
      - sync_failed
      - schema_changed
      - sync_delayed

  - email: oncall@company.com
    events:
      - sync_failed
    connectors:
      - postgres_production
      - salesforce_prod
```

### Sync Monitoring
```sql
-- Query Fivetran metadata tables
-- Available in destination warehouse

-- Check sync status
SELECT
    connector_name,
    table_name,
    sync_start,
    sync_end,
    rows_updated,
    rows_inserted
FROM fivetran_metadata.sync_log
WHERE sync_end >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY sync_end DESC;

-- Check schema changes
SELECT
    connector_name,
    table_name,
    column_name,
    change_type,  -- added, removed, type_changed
    changed_at
FROM fivetran_metadata.schema_changes
WHERE changed_at >= CURRENT_TIMESTAMP - INTERVAL '7 days';
```

## Cost Optimization

### Monthly Active Rows (MAR)
Fivetran charges based on MAR (unique rows synced per month).

```yaml
# Optimize MAR usage:

1. Use incremental sync instead of full table
2. Exclude unnecessary tables/columns
3. Set appropriate sync frequencies
4. Filter rows at source when possible
5. Archive historical data
```

### Sync Frequency Tuning
```yaml
# Adjust frequency per connector
critical_data:
  connector: postgres_orders
  sync_frequency: 15  # minutes

regular_data:
  connector: crm_data
  sync_frequency: 360  # 6 hours

historical_data:
  connector: archived_logs
  sync_frequency: 1440  # daily
```

### Selective Syncing
```yaml
# Exclude tables
excluded_tables:
  - staging.*
  - temp_*
  - logs_*

# Include only specific tables
included_tables:
  - orders
  - customers
  - products
  - invoices
```

## API Usage

### Fivetran REST API
```python
import requests

# Authentication
headers = {
    'Authorization': f'Bearer {FIVETRAN_API_KEY}',
    'Content-Type': 'application/json'
}

# List connectors
response = requests.get(
    'https://api.fivetran.com/v1/connectors',
    headers=headers
)

# Get connector details
connector_id = 'abc123'
response = requests.get(
    f'https://api.fivetran.com/v1/connectors/{connector_id}',
    headers=headers
)

# Trigger sync
requests.post(
    f'https://api.fivetran.com/v1/connectors/{connector_id}/force',
    headers=headers
)

# Modify connector config
requests.patch(
    f'https://api.fivetran.com/v1/connectors/{connector_id}',
    headers=headers,
    json={
        'sync_frequency': 60,
        'paused': False
    }
)
```

### Terraform Integration
```hcl
# Manage Fivetran with Terraform
provider "fivetran" {
  api_key    = var.fivetran_api_key
  api_secret = var.fivetran_api_secret
}

resource "fivetran_connector" "postgres_prod" {
  group_id = var.fivetran_group_id
  service  = "postgres"

  destination_schema {
    name = "postgres_production"
  }

  config {
    host     = "database.example.com"
    port     = 5432
    database = "production"
    user     = "fivetran"
    password = var.postgres_password

    update_method = "WAL"
  }

  sync_frequency = 15
  paused         = false
}

resource "fivetran_connector_schedule" "postgres_schedule" {
  connector_id  = fivetran_connector.postgres_prod.id
  sync_frequency = 60  # minutes
  paused        = false
  pause_after_trial = false
}
```

## Transformation (dbt Integration)

### Fivetran Transformations
```yaml
# Fivetran includes managed dbt
# transformations/models/staging/stg_orders.sql

with source as (
    select * from {{ source('fivetran', 'salesforce_opportunity') }}
),

renamed as (
    select
        id as opportunity_id,
        account_id,
        name as opportunity_name,
        amount,
        stage_name,
        close_date,
        _fivetran_synced as last_synced_at
    from source
)

select * from renamed
```

## Best Practices

### Connection Security
```yaml
# Use SSH tunnels for databases
ssh_host: bastion.example.com
ssh_port: 22
ssh_user: fivetran
ssh_private_key: ${SSH_PRIVATE_KEY}

# Use IAM roles for AWS
role_arn: arn:aws:iam::123456789:role/FivetranS3Access

# Use service accounts for GCP
credentials: ${GCP_SERVICE_ACCOUNT_JSON}
```

### Schema Organization
```sql
-- Organize by source system
CREATE SCHEMA fivetran_postgres;
CREATE SCHEMA fivetran_salesforce;
CREATE SCHEMA fivetran_shopify;

-- Or by data domain
CREATE SCHEMA raw_sales;
CREATE SCHEMA raw_marketing;
CREATE SCHEMA raw_finance;
```

### Testing & Validation
```sql
-- Validate sync completeness
WITH source_count AS (
    SELECT COUNT(*) as cnt
    FROM source_system.orders
    WHERE updated_at >= CURRENT_DATE - 1
),
fivetran_count AS (
    SELECT COUNT(*) as cnt
    FROM fivetran.orders
    WHERE _fivetran_synced >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
)
SELECT
    s.cnt as source_count,
    f.cnt as fivetran_count,
    s.cnt - f.cnt as difference
FROM source_count s
CROSS JOIN fivetran_count f;
```

## Troubleshooting

### Common Issues

```yaml
# Sync failures
Issue: "Permission denied"
Solution: Verify user permissions, check firewall rules

Issue: "Schema change detected"
Solution: Review schema changes, approve in Fivetran UI

Issue: "High MAR usage"
Solution: Audit connectors, exclude unnecessary tables

Issue: "Sync lag"
Solution: Increase sync frequency, check source database load
```

### Debug Logs
```python
# View connector logs via API
response = requests.get(
    f'https://api.fivetran.com/v1/connectors/{connector_id}/logs',
    headers=headers,
    params={'limit': 100}
)

for log in response.json()['data']:
    print(f"{log['timestamp']}: {log['message']}")
```

## Comparison: Fivetran vs Airbyte

| Feature | Fivetran | Airbyte |
|---------|----------|---------|
| **Deployment** | Managed SaaS | Self-hosted or Cloud |
| **Pricing** | Usage-based (MAR) | Free (self-hosted) or usage |
| **Connectors** | 300+ certified | 300+ community |
| **Maintenance** | Zero (managed) | Manual updates |
| **Custom Connectors** | Via API | Python CDK |
| **Schema Changes** | Automatic | Manual/config |
| **CDC Support** | Extensive | Growing |
| **Best For** | Enterprises, low-maintenance | Startups, customization |

## Resources

- **Fivetran Docs**: https://fivetran.com/docs
- **Connector Hub**: https://fivetran.com/connectors
- **API Docs**: https://fivetran.com/docs/rest-api
- **Status Page**: https://status.fivetran.com
- **Support**: support@fivetran.com
