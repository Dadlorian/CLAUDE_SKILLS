# ClickHouse Real-Time Setup Guide

## Overview
Complete guide for setting up ClickHouse for real-time analytics with Kafka integration.

## Installation

### Docker Setup
```yaml
version: '3'
services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - ./data:/var/lib/clickhouse
      - ./config:/etc/clickhouse-server/config.d
    environment:
      CLICKHOUSE_DB: analytics
      CLICKHOUSE_USER: default
      CLICKHOUSE_PASSWORD: password
```

### Configuration
```xml
<!-- /etc/clickhouse-server/config.d/custom.xml -->
<clickhouse>
    <max_threads>16</max_threads>
    <max_memory_usage>20000000000</max_memory_usage>
    <kafka>
        <kafka_broker_list>kafka:9092</kafka_broker_list>
    </kafka>
</clickhouse>
```

## Table Setup

### Create Database
```sql
CREATE DATABASE IF NOT EXISTS analytics;
```

### Kafka Engine Table
```sql
CREATE TABLE analytics.events_queue (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    properties String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_events',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 4;
```

### Storage Table
```sql
CREATE TABLE analytics.events (
    event_time DateTime,
    user_id UInt64,
    event_type LowCardinality(String),
    country LowCardinality(String),
    device_type LowCardinality(String),
    revenue Nullable(Float64),
    properties String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 8192;
```

### Materialized View
```sql
CREATE MATERIALIZED VIEW analytics.events_mv TO analytics.events AS
SELECT
    toDateTime(JSONExtractString(properties, 'timestamp')) AS event_time,
    user_id,
    event_type,
    JSONExtractString(properties, 'country') AS country,
    JSONExtractString(properties, 'device') AS device_type,
    JSONExtractFloat(properties, 'revenue') AS revenue,
    properties
FROM analytics.events_queue;
```

## Pre-Aggregated Views

```sql
CREATE MATERIALIZED VIEW analytics.hourly_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type, country)
AS SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    country,
    count() AS event_count,
    sum(revenue) AS total_revenue,
    uniq(user_id) AS unique_users
FROM analytics.events
GROUP BY hour, event_type, country;
```

## Best Practices

1. Use LowCardinality for enums
2. Partition by time for easy management
3. Use materialized views for real-time aggregation
4. Monitor merge activity
5. Set appropriate TTL for old data

## Monitoring

```sql
SELECT
    table,
    sum(rows) as rows,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts
WHERE database = 'analytics' AND active
GROUP BY table;
```
