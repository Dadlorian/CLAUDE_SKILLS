# CDC Implementation Guide

## What is CDC?

Change Data Capture tracks all changes (inserts, updates, deletes) in source databases by reading transaction logs, providing near-real-time data replication.

## PostgreSQL CDC with Debezium

### 1. Configure PostgreSQL
```sql
-- postgresql.conf
wal_level = logical
max_wal_senders = 10
max_replication_slots = 10

-- Restart PostgreSQL
sudo systemctl restart postgresql

-- Create publication
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;

-- Create replication slot
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

### 2. Configure Debezium/Airbyte
```yaml
connector:
  type: postgres
  replication_method: CDC
  publication: airbyte_publication
  replication_slot: airbyte_slot
  plugin: pgoutput
```

### 3. Process CDC Events in dbt
```sql
-- models/staging/stg_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

WITH cdc_data AS (
    SELECT
        id as order_id,
        customer_id,
        status,
        amount,
        _airbyte_emitted_at,
        _airbyte_cdc_deleted_at
    FROM {{ source('airbyte_raw', 'orders') }}

    {% if is_incremental() %}
    WHERE _airbyte_emitted_at > (SELECT MAX(_airbyte_emitted_at) FROM {{ this }})
    {% endif %}
)

SELECT *
FROM cdc_data
WHERE _airbyte_cdc_deleted_at IS NULL  -- Exclude soft deletes
```

## MySQL CDC

### 1. Enable Binary Logging
```ini
# my.cnf
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW
binlog_row_image = FULL
```

### 2. Create Replication User
```sql
CREATE USER 'debezium'@'%' IDENTIFIED BY 'password';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT
ON *.* TO 'debezium'@'%';
```

## Handling Deletes

### Soft Delete Pattern
```sql
-- Maintain deleted records with timestamp
SELECT
    *,
    CASE
        WHEN _airbyte_cdc_deleted_at IS NOT NULL THEN TRUE
        ELSE FALSE
    END as is_deleted
FROM {{ source('cdc', 'orders') }}
```

### Hard Delete Pattern
```sql
-- Remove deleted records
DELETE FROM {{ this }}
WHERE order_id IN (
    SELECT id
    FROM {{ source('cdc', 'orders_changes') }}
    WHERE operation = 'DELETE'
);
```

## Monitoring CDC

```sql
-- Check replication lag (PostgreSQL)
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots;

-- Alert if lag > 1GB
SELECT CASE
    WHEN lag_bytes > 1073741824 THEN 'ALERT: High replication lag'
    ELSE 'OK'
END as status;
```

## Best Practices

1. **Monitor Replication Lag**: Alert on high lag
2. **Test Failover**: Practice recovery procedures
3. **Handle Schema Changes**: Plan for DDL changes
4. **Manage Storage**: Monitor WAL disk usage
5. **Document Dependencies**: Track downstream impacts

