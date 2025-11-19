# Stream to Data Warehouse Sync Guide

## CDC with Debezium
```json
{
  "name": "mysql-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.name": "production",
    "table.include.list": "ecommerce.*"
  }
}
```

## Flink CDC to Warehouse
```java
DataStream<ChangeEvent> changes = env
    .addSource(new DebeziumSourceFunction<>());

changes
    .keyBy(ChangeEvent::getTableName)
    .process(new WarehouseSyncFunction())
    .addSink(new ClickHouseSink());
```

## Upsert Logic
```sql
-- ClickHouse ReplacingMergeTree
CREATE TABLE users (
    user_id UInt64,
    name String,
    email String,
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;
```

## Best Practices
- Handle schema evolution
- Implement idempotent writes
- Monitor lag
- Use transactions where possible
