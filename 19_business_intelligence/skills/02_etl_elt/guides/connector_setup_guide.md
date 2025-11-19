# Connector Setup Guide

## Airbyte Connector Setup

### PostgreSQL Source
```yaml
# 1. Prepare source database
CREATE USER airbyte WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE production TO airbyte;
GRANT USAGE ON SCHEMA public TO airbyte;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO airbyte;

# For CDC
ALTER SYSTEM SET wal_level = logical;
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;

# 2. Configure in Airbyte UI or via API
connector:
  type: postgres
  host: database.example.com
  port: 5432
  database: production
  username: airbyte
  password: ${POSTGRES_PASSWORD}
  replication_method: CDC
  ssl: true
```

### Shopify API Source
```yaml
connector:
  type: shopify
  shop_name: yourstore
  api_key: ${SHOPIFY_API_KEY}
  api_password: ${SHOPIFY_API_PASSWORD}
  start_date: '2024-01-01T00:00:00Z'
```

### S3 Source
```yaml
connector:
  type: s3
  bucket: data-bucket
  aws_access_key_id: ${AWS_ACCESS_KEY}
  aws_secret_access_key: ${AWS_SECRET_KEY}
  path_pattern: data/*.csv
  format:
    filetype: csv
    delimiter: ','
```

## Fivetran Connector Setup

### PostgreSQL
```yaml
# 1. Create Fivetran user
CREATE USER fivetran WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fivetran;

# For CDC
ALTER USER fivetran WITH REPLICATION;

# 2. Configure in Fivetran
connector: postgres
host: database.example.com
port: 5432
database: production
user: fivetran
password: ${POSTGRES_PASSWORD}
sync_method: WAL
sync_frequency: 60
```

### Salesforce
```yaml
# 1. Create Connected App in Salesforce
# 2. Generate OAuth tokens
# 3. Configure in Fivetran
connector: salesforce
domain: login.salesforce.com
username: integration@company.com
security_token: ${SF_TOKEN}
password: ${SF_PASSWORD}
```

## Best Practices

1. **Security**:
   - Use read-only users
   - Rotate credentials regularly
   - Enable SSL/TLS
   - Use secrets management

2. **Performance**:
   - Use incremental sync
   - Schedule during off-peak hours
   - Monitor source database load

3. **Reliability**:
   - Set up alerts on sync failures
   - Test failover scenarios
   - Document recovery procedures

4. **Cost**:
   - Exclude unnecessary tables/columns
   - Adjust sync frequency appropriately
   - Monitor usage metrics

## Troubleshooting

### Connection Timeout
- Check firewall rules
- Verify network connectivity
- Increase timeout settings

### Permission Errors
- Verify user permissions
- Check SSL certificate validity
- Review database logs

### Schema Changes
- Enable auto-schema detection
- Review schema change alerts
- Update dependent models

