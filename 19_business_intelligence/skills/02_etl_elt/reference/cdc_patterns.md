# Change Data Capture (CDC) Patterns Reference

## Overview
Change Data Capture (CDC) tracks changes in source databases by reading transaction logs, providing near-real-time data replication with minimal performance impact.

## CDC Methods

### 1. Log-Based CDC (Recommended)
Reads database transaction logs (WAL, binlog, redo logs).

**Advantages**:
- Minimal source database impact
- Captures all changes (INSERT, UPDATE, DELETE)
- Near real-time latency
- Doesn't require schema modifications

**Disadvantages**:
- Requires log access permissions
- Database-specific implementation
- Complex setup

### 2. Trigger-Based CDC
Uses database triggers to capture changes.

**Advantages**:
- Works on any database
- Simple to implement
- Guaranteed capture

**Disadvantages**:
- Performance overhead on source
- Requires schema modifications
- Can be complex to maintain

### 3. Timestamp-Based
Queries using timestamp columns (created_at, updated_at).

**Advantages**:
- Simple to implement
- No special permissions needed
- Works everywhere

**Disadvantages**:
- Cannot detect deletes
- Requires timestamp columns
- Can miss rapid updates
- Not truly real-time

### 4. Diff-Based (Snapshot Comparison)
Compares current snapshot with previous.

**Advantages**:
- No source changes needed
- Can work without timestamps
- Simple concept

**Disadvantages**:
- Very high overhead
- Scales poorly
- Cannot detect deletes reliably
- Not real-time

## PostgreSQL CDC

### Using Debezium with PostgreSQL
```yaml
# PostgreSQL configuration (postgresql.conf)
wal_level = logical
max_wal_senders = 10
max_replication_slots = 10

# Create publication
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;

# Or specific tables
CREATE PUBLICATION airbyte_publication FOR TABLE orders, customers;

# Create replication slot
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

# Check replication lag
SELECT
    slot_name,
    confirmed_flush_lsn,
    pg_current_wal_lsn(),
    (pg_current_wal_lsn() - confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots
WHERE slot_name = 'airbyte_slot';
```

### Debezium Connector Configuration
```json
{
  "name": "postgres-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres.example.com",
    "database.port": "5432",
    "database.user": "debezium_user",
    "database.password": "${POSTGRES_PASSWORD}",
    "database.dbname": "production",
    "database.server.name": "prod_db",
    "plugin.name": "pgoutput",
    "publication.name": "airbyte_publication",
    "slot.name": "debezium_slot",
    "table.include.list": "public.orders,public.customers",
    "snapshot.mode": "initial",
    "time.precision.mode": "adaptive_time_microseconds",
    "tombstones.on.delete": true,
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": false,
    "transforms.unwrap.delete.handling.mode": "rewrite"
  }
}
```

### CDC Data Structure
```json
{
  "before": {
    "id": 123,
    "status": "pending",
    "amount": 100.00,
    "updated_at": "2024-01-15T10:00:00Z"
  },
  "after": {
    "id": 123,
    "status": "completed",
    "amount": 100.00,
    "updated_at": "2024-01-15T11:30:00Z"
  },
  "source": {
    "version": "1.9.0",
    "connector": "postgresql",
    "name": "prod_db",
    "ts_ms": 1705318200000,
    "snapshot": "false",
    "db": "production",
    "schema": "public",
    "table": "orders",
    "txId": 567890,
    "lsn": 123456789,
    "xmin": null
  },
  "op": "u",  // c=create, u=update, d=delete, r=read(snapshot)
  "ts_ms": 1705318200123
}
```

## MySQL CDC

### MySQL Configuration
```ini
# my.cnf
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW
binlog_row_image = FULL
expire_logs_days = 7
```

### Create CDC User
```sql
-- Create user with replication permissions
CREATE USER 'debezium'@'%' IDENTIFIED BY 'password';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT
  ON *.* TO 'debezium'@'%';
FLUSH PRIVILEGES;

-- Verify binlog is enabled
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';

-- Check binlog position
SHOW MASTER STATUS;
```

### Debezium MySQL Connector
```json
{
  "name": "mysql-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql.example.com",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "${MYSQL_PASSWORD}",
    "database.server.id": "184054",
    "database.server.name": "prod_mysql",
    "table.include.list": "ecommerce.orders,ecommerce.customers",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.ecommerce",
    "snapshot.mode": "initial",
    "snapshot.locking.mode": "minimal",
    "include.schema.changes": true
  }
}
```

## SQL Server CDC

### Enable CDC on SQL Server
```sql
-- Enable CDC on database
USE production;
EXEC sys.sp_cdc_enable_db;

-- Verify CDC is enabled
SELECT name, is_cdc_enabled
FROM sys.databases
WHERE name = 'production';

-- Enable CDC on specific table
EXEC sys.sp_cdc_enable_table
  @source_schema = 'dbo',
  @source_name = 'orders',
  @role_name = NULL,
  @supports_net_changes = 1;

-- Verify CDC on table
EXEC sys.sp_cdc_help_change_data_capture;

-- Query CDC changes
SELECT *
FROM cdc.dbo_orders_CT
WHERE __$operation IN (1, 2, 4)  -- 1=delete, 2=insert, 4=update
  AND __$start_lsn > sys.fn_cdc_get_min_lsn('dbo_orders');
```

### Debezium SQL Server Connector
```json
{
  "name": "sqlserver-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector",
    "database.hostname": "sqlserver.example.com",
    "database.port": "1433",
    "database.user": "debezium",
    "database.password": "${SQLSERVER_PASSWORD}",
    "database.dbname": "production",
    "database.server.name": "prod_sqlserver",
    "table.include.list": "dbo.orders,dbo.customers",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.production",
    "snapshot.mode": "initial"
  }
}
```

## MongoDB CDC

### MongoDB Change Streams
```javascript
// MongoDB configuration - replica set required
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "localhost:27017" }]
});

// Watch collection changes
const changeStream = db.orders.watch();
changeStream.on("change", (change) => {
  console.log(change);
});

// Watch with filter
const pipeline = [
  { $match: { operationType: { $in: ["insert", "update", "delete"] } } }
];
const filteredStream = db.orders.watch(pipeline);
```

### Debezium MongoDB Connector
```json
{
  "name": "mongodb-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
    "mongodb.hosts": "rs0/mongo1:27017,mongo2:27017,mongo3:27017",
    "mongodb.name": "prod_mongo",
    "mongodb.user": "debezium",
    "mongodb.password": "${MONGO_PASSWORD}",
    "collection.include.list": "ecommerce.orders,ecommerce.customers",
    "snapshot.mode": "initial"
  }
}
```

## DynamoDB Streams CDC

### Enable DynamoDB Streams
```python
import boto3

dynamodb = boto3.client('dynamodb')

# Enable stream on table
response = dynamodb.update_table(
    TableName='Orders',
    StreamSpecification={
        'StreamEnabled': True,
        'StreamViewType': 'NEW_AND_OLD_IMAGES'  # or NEW_IMAGE, OLD_IMAGE, KEYS_ONLY
    }
)

# Process stream records
from boto3.dynamodb.types import TypeDeserializer

def process_stream_record(record):
    deserializer = TypeDeserializer()

    if record['eventName'] == 'INSERT':
        new_image = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['NewImage'].items()}
        print(f"New item: {new_image}")

    elif record['eventName'] == 'MODIFY':
        old_image = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['OldImage'].items()}
        new_image = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['NewImage'].items()}
        print(f"Updated: {old_image} -> {new_image}")

    elif record['eventName'] == 'REMOVE':
        old_image = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['OldImage'].items()}
        print(f"Deleted: {old_image}")
```

## AWS DMS (Database Migration Service)

### DMS Replication Instance
```python
import boto3

dms = boto3.client('dms')

# Create replication instance
response = dms.create_replication_instance(
    ReplicationInstanceIdentifier='prod-cdc-instance',
    ReplicationInstanceClass='dms.c5.large',
    AllocatedStorage=100,
    VpcSecurityGroupIds=['sg-xxxxx'],
    ReplicationSubnetGroupIdentifier='dms-subnet-group',
    MultiAZ=True,
    EngineVersion='3.4.6',
    Tags=[
        {'Key': 'Environment', 'Value': 'Production'},
        {'Key': 'Purpose', 'Value': 'CDC'}
    ]
)
```

### DMS Task Configuration
```json
{
  "rules": [
    {
      "rule-type": "selection",
      "rule-id": "1",
      "rule-name": "include-orders-table",
      "object-locator": {
        "schema-name": "public",
        "table-name": "orders"
      },
      "rule-action": "include"
    },
    {
      "rule-type": "transformation",
      "rule-id": "2",
      "rule-name": "add-cdc-metadata",
      "rule-target": "column",
      "object-locator": {
        "schema-name": "public",
        "table-name": "orders"
      },
      "rule-action": "add-column",
      "value": "cdc_timestamp",
      "expression": "$AR_H_CHANGE_SEQ",
      "data-type": {
        "type": "datetime"
      }
    }
  ]
}
```

## CDC Processing Patterns

### Pattern 1: Upsert (Merge) Pattern
```sql
-- Process CDC events into target table
MERGE INTO target_table AS target
USING (
    SELECT
        id,
        customer_id,
        status,
        amount,
        updated_at,
        _ab_cdc_deleted_at
    FROM cdc_staging
    WHERE batch_id = :current_batch
) AS source
ON target.id = source.id
WHEN MATCHED AND source._ab_cdc_deleted_at IS NOT NULL THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET
        customer_id = source.customer_id,
        status = source.status,
        amount = source.amount,
        updated_at = source.updated_at,
        _synced_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (id, customer_id, status, amount, updated_at, _synced_at)
    VALUES (source.id, source.customer_id, source.status, source.amount,
            source.updated_at, CURRENT_TIMESTAMP);
```

### Pattern 2: Append-Only with Latest View
```sql
-- Raw CDC events table (append-only)
CREATE TABLE orders_cdc (
    id BIGINT,
    customer_id BIGINT,
    status VARCHAR(50),
    amount DECIMAL(10,2),
    _cdc_operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
    _cdc_timestamp TIMESTAMP,
    _cdc_lsn BIGINT,
    updated_at TIMESTAMP
);

-- Latest state view
CREATE VIEW orders_current AS
WITH ranked_changes AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _cdc_timestamp DESC) as rn
    FROM orders_cdc
)
SELECT
    id,
    customer_id,
    status,
    amount,
    updated_at
FROM ranked_changes
WHERE rn = 1
  AND _cdc_operation != 'DELETE';
```

### Pattern 3: Type 2 SCD from CDC
```sql
-- Slowly Changing Dimension Type 2
INSERT INTO dim_customers (
    customer_id,
    email,
    name,
    valid_from,
    valid_to,
    is_current
)
SELECT
    c.customer_id,
    c.email,
    c.name,
    c._cdc_timestamp as valid_from,
    NULL as valid_to,
    TRUE as is_current
FROM customers_cdc c
WHERE c._cdc_operation IN ('INSERT', 'UPDATE')
  AND c._cdc_timestamp >= :last_processed_timestamp;

-- Close out previous records
UPDATE dim_customers
SET valid_to = cdc.valid_from,
    is_current = FALSE
FROM (
    SELECT customer_id, _cdc_timestamp as valid_from
    FROM customers_cdc
    WHERE _cdc_operation = 'UPDATE'
) cdc
WHERE dim_customers.customer_id = cdc.customer_id
  AND dim_customers.is_current = TRUE
  AND dim_customers.valid_from < cdc.valid_from;
```

### Pattern 4: Event Sourcing
```sql
-- Store all events
CREATE TABLE order_events (
    event_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- created, updated, cancelled, etc.
    event_data JSONB NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    _cdc_lsn BIGINT,
    INDEX idx_order_events_order_id (order_id),
    INDEX idx_order_events_timestamp (event_timestamp)
);

-- Rebuild current state from events
CREATE VIEW order_current_state AS
WITH latest_events AS (
    SELECT
        order_id,
        event_type,
        event_data,
        event_timestamp,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY event_timestamp DESC) as rn
    FROM order_events
)
SELECT
    order_id,
    event_data->>'status' as status,
    (event_data->>'amount')::DECIMAL as amount,
    event_timestamp as last_updated
FROM latest_events
WHERE rn = 1
  AND event_type != 'deleted';
```

## Monitoring CDC

### Replication Lag
```sql
-- PostgreSQL replication lag
SELECT
    slot_name,
    confirmed_flush_lsn,
    pg_current_wal_lsn(),
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    ROUND(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) / 1024 / 1024, 2) AS lag_mb
FROM pg_replication_slots
WHERE active = true;

-- MySQL binlog lag
SHOW SLAVE STATUS\G
-- Check Seconds_Behind_Master
```

### CDC Health Checks
```python
# Monitor CDC connector health
def check_cdc_health():
    checks = {
        'replication_lag': check_replication_lag(),
        'connector_status': check_connector_status(),
        'slot_active': check_replication_slot(),
        'disk_space': check_disk_space(),
        'event_throughput': check_event_rate()
    }

    if not all(checks.values()):
        alert_team(checks)

    return checks

def check_replication_lag():
    """Alert if lag > 5 minutes"""
    lag = get_current_lag_seconds()
    return lag < 300

def check_connector_status():
    """Ensure connector is running"""
    status = get_debezium_connector_status()
    return status == 'RUNNING'

def check_replication_slot():
    """Ensure slot is active and not too far behind"""
    slot_info = get_replication_slot_info()
    return slot_info['active'] and slot_info['lag_bytes'] < 1_000_000_000
```

## Best Practices

### 1. Initial Snapshot Strategy
```yaml
# Consistent snapshot without locking
snapshot.mode: initial
snapshot.locking.mode: minimal  # or none, depending on database

# Skip snapshot if already loaded
snapshot.mode: schema_only

# Custom snapshot query
snapshot.select.statement.overrides: |
  SELECT * FROM orders WHERE created_at >= '2024-01-01'
```

### 2. Handle Schema Changes
```sql
-- Add column to source
ALTER TABLE orders ADD COLUMN notes TEXT;

-- CDC will capture schema change
-- Configure connector to handle gracefully:
# schema.evolution.mode: additive  # Allow new columns
# or
# schema.evolution.mode: strict    # Fail on schema change
```

### 3. Manage Deletes
```sql
-- Soft deletes preferred
ALTER TABLE orders ADD COLUMN deleted_at TIMESTAMP;

UPDATE orders SET deleted_at = CURRENT_TIMESTAMP WHERE id = 123;

-- If hard deletes required, capture in CDC
-- Store deleted records in separate table
CREATE TABLE orders_deleted AS
SELECT *, CURRENT_TIMESTAMP as deleted_at
FROM orders
WHERE id IN (SELECT id FROM cdc_deletes);
```

### 4. Backfill Historical Data
```python
def backfill_with_cdc_running():
    """
    Backfill historical data while CDC is active
    1. Note current CDC position
    2. Load historical data (WHERE created_at < cutoff)
    3. Resume CDC from noted position
    4. CDC will overlay updates on historical data
    """
    cdc_position = get_current_cdc_position()

    # Load historical in batches
    load_historical_data(end_date=CDC_START_DATE)

    # Resume CDC (will handle overlaps via upsert)
    resume_cdc_from_position(cdc_position)
```

## Troubleshooting

### Issue: Replication Slot Lag
```sql
-- Check WAL disk usage
SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn))
FROM pg_replication_slots;

-- Increase wal_keep_size if needed
ALTER SYSTEM SET wal_keep_size = '10GB';
SELECT pg_reload_conf();

-- Drop and recreate slot if too far behind
SELECT pg_drop_replication_slot('airbyte_slot');
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

### Issue: Missing CDC Events
```sql
-- Verify publication includes table
SELECT * FROM pg_publication_tables WHERE pubname = 'airbyte_publication';

-- Add missing table
ALTER PUBLICATION airbyte_publication ADD TABLE missing_table;
```

### Issue: High Source Database Load
```
Solutions:
1. Use log-based CDC (lowest impact)
2. Increase batch size to reduce queries
3. Add indexes on timestamp columns
4. Schedule initial snapshots during off-peak
5. Use read replicas for CDC
```

## Resources

- **Debezium**: https://debezium.io/documentation/
- **AWS DMS**: https://docs.aws.amazon.com/dms/
- **PostgreSQL Logical Replication**: https://www.postgresql.org/docs/current/logical-replication.html
- **MySQL Binlog**: https://dev.mysql.com/doc/refman/8.0/en/binary-log.html
