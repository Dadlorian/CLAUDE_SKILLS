# ClickHouse Comprehensive Guide

## Introduction

ClickHouse is an open-source column-oriented database management system designed for online analytical processing (OLAP) with exceptional query performance for real-time analytics.

## Architecture

### Column-Oriented Storage
```
Traditional Row-Oriented:
| ID | Name  | Age | City      |
|----|-------|-----|-----------|
| 1  | Alice | 25  | NYC       |
| 2  | Bob   | 30  | LA        |

ClickHouse Column-Oriented:
ID:   [1, 2]
Name: [Alice, Bob]
Age:  [25, 30]
City: [NYC, LA]
```

### Benefits
- **Better Compression**: Similar data types compress better
- **Faster Scans**: Read only needed columns
- **Cache Efficiency**: Columns fit better in CPU cache
- **Vectorization**: SIMD operations on column data

### Core Components
- **Distributed Tables**: Shard data across nodes
- **ReplicatedMergeTree**: Replication for fault tolerance
- **Materialized Views**: Pre-aggregated query results
- **Dictionaries**: Fast lookup tables in memory

## Table Engines

### MergeTree Family

#### MergeTree
```sql
CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    properties String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 8192;
```

**Characteristics:**
- Base engine for most use cases
- Supports primary key for sorting
- Partitioning for data management
- Background merge operations

#### ReplicatedMergeTree
```sql
CREATE TABLE events_replicated (
    event_time DateTime,
    user_id UInt64,
    event_type String
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);
```

**Features:**
- Multi-master replication
- Uses ZooKeeper for coordination
- Automatic deduplication
- Fault tolerance

#### Distributed
```sql
CREATE TABLE events_distributed AS events_local
ENGINE = Distributed(cluster_name, database_name, events_local, rand());
```

**Purpose:**
- Query entry point for sharded data
- Distributes writes to shards
- Aggregates query results
- Transparent to applications

### Specialized Engines

#### SummingMergeTree
```sql
CREATE TABLE metrics_sum (
    date Date,
    metric_name String,
    value Float64
)
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, metric_name);
```

**Use Case:** Pre-aggregating sums during merges

#### AggregatingMergeTree
```sql
CREATE TABLE metrics_agg (
    date Date,
    metric_name String,
    value_state AggregateFunction(avg, Float64)
)
ENGINE = AggregatingMergeTree()
ORDER BY (date, metric_name);
```

**Use Case:** Store intermediate aggregation states

#### CollapsingMergeTree
```sql
CREATE TABLE updates (
    id UInt64,
    name String,
    sign Int8
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY id;
```

**Use Case:** Handle updates by canceling out rows

## Data Types

### Numeric Types
- **UInt8, UInt16, UInt32, UInt64**: Unsigned integers
- **Int8, Int16, Int32, Int64**: Signed integers
- **Float32, Float64**: Floating point
- **Decimal(P, S)**: Fixed-point decimal

### String Types
- **String**: Variable-length byte arrays
- **FixedString(N)**: Fixed-length strings
- **UUID**: Universally unique identifiers

### Date/Time Types
- **Date**: Date without time (2 bytes)
- **DateTime**: Unix timestamp (4 bytes)
- **DateTime64**: Microsecond precision (8 bytes)

### Array Types
```sql
Array(T) -- Dynamic array of type T
SELECT [1, 2, 3] AS arr;
SELECT arrayFilter(x -> x > 1, [1, 2, 3]);
```

### Nested Types
```sql
CREATE TABLE nested_example (
    id UInt64,
    items Nested(
        name String,
        price Float64,
        quantity UInt32
    )
);
```

### Special Types
- **Nullable(T)**: Allow NULL values
- **LowCardinality(T)**: Dictionary encoding
- **Tuple(T1, T2, ...)**: Fixed-length tuples
- **Map(K, V)**: Key-value maps

## Indexing

### Primary Key Index
```sql
-- Sparse index on (date, user_id)
ORDER BY (date, user_id)
SETTINGS index_granularity = 8192;
```

**How It Works:**
- Stores one index entry per 8192 rows (granule)
- Binary search on index, then scan granule
- Not unique, multiple rows can have same key
- Very memory efficient

### Secondary Indexes (Skip Indexes)

#### MinMax Index
```sql
ALTER TABLE events
ADD INDEX idx_event_type (event_type) TYPE minmax GRANULARITY 4;
```

**Use Case:** Skip blocks where column value is outside range

#### Set Index
```sql
ALTER TABLE events
ADD INDEX idx_user_set (user_id) TYPE set(1000) GRANULARITY 4;
```

**Use Case:** Skip blocks where value is not in set

#### Bloom Filter Index
```sql
ALTER TABLE events
ADD INDEX idx_user_bloom (user_id) TYPE bloom_filter GRANULARITY 1;
```

**Use Case:** Fast membership testing for high-cardinality columns

#### Token Bloom Filter
```sql
ALTER TABLE logs
ADD INDEX idx_message_token message TYPE tokenbf_v1(32768, 3, 0) GRANULARITY 1;
```

**Use Case:** Full-text search on string columns

## Query Optimization

### Best Practices

#### 1. Use Primary Key in WHERE
```sql
-- Good: Uses primary key
SELECT * FROM events
WHERE event_time >= '2025-01-01' AND user_id = 12345;

-- Bad: Doesn't use primary key
SELECT * FROM events
WHERE event_type = 'click';
```

#### 2. Partition Pruning
```sql
-- Good: Filters on partition key
SELECT count() FROM events
WHERE toYYYYMM(event_time) = 202501;

-- Better: Uses partition pruning
SELECT count() FROM events
WHERE event_time BETWEEN '2025-01-01' AND '2025-01-31';
```

#### 3. Use PREWHERE
```sql
-- Filters data before reading all columns
SELECT user_id, properties
FROM events
PREWHERE event_type = 'purchase'
WHERE user_id > 1000;
```

#### 4. LowCardinality for Enums
```sql
-- Saves memory and improves performance
CREATE TABLE events (
    event_type LowCardinality(String),
    country LowCardinality(String)
);
```

### Query Performance Analysis

#### EXPLAIN
```sql
EXPLAIN SELECT count()
FROM events
WHERE event_time >= '2025-01-01';
```

#### Query Log
```sql
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY query_duration_ms DESC
LIMIT 10;
```

## Materialized Views

### Simple Aggregation
```sql
-- Source table
CREATE TABLE page_views (
    timestamp DateTime,
    page_id UInt64,
    user_id UInt64
);

-- Materialized view
CREATE MATERIALIZED VIEW page_views_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, page_id)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    page_id,
    count() AS views
FROM page_views
GROUP BY hour, page_id;
```

### Real-Time Aggregation
```sql
CREATE MATERIALIZED VIEW user_daily_stats
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id)
AS SELECT
    toDate(event_time) AS date,
    user_id,
    countState() AS event_count,
    uniqState(session_id) AS session_count,
    avgState(session_duration) AS avg_duration_state
FROM events
GROUP BY date, user_id;

-- Query the materialized view
SELECT
    date,
    user_id,
    countMerge(event_count) AS total_events,
    uniqMerge(session_count) AS total_sessions,
    avgMerge(avg_duration_state) AS avg_duration
FROM user_daily_stats
WHERE date >= '2025-01-01'
GROUP BY date, user_id;
```

## Data Ingestion

### INSERT FROM SELECT
```sql
INSERT INTO events
SELECT * FROM remote('source_host', database, table);
```

### Kafka Integration
```sql
CREATE TABLE kafka_queue (
    event_time DateTime,
    user_id UInt64,
    event_data String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'localhost:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow';

-- Materialized view to persist data
CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT * FROM kafka_queue;
```

### HTTP Interface
```bash
curl -X POST 'http://localhost:8123/' \
  --data-binary @data.csv \
  -H "query: INSERT INTO events FORMAT CSV"
```

### JDBC/ODBC
```sql
CREATE TABLE mysql_source
ENGINE = MySQL('localhost:3306', 'database', 'table', 'user', 'password');

INSERT INTO events SELECT * FROM mysql_source;
```

## Performance Tuning

### Server Configuration

#### Memory
```xml
<max_memory_usage>10000000000</max_memory_usage>
<max_bytes_before_external_group_by>20000000000</max_bytes_before_external_group_by>
```

#### Threads
```xml
<max_threads>8</max_threads>
<max_insert_threads>4</max_insert_threads>
```

#### Merges
```xml
<background_pool_size>16</background_pool_size>
<background_merge_pool_size>16</background_merge_pool_size>
```

### Table Settings
```sql
-- Optimize merge frequency
ALTER TABLE events MODIFY SETTING
    merge_with_ttl_timeout = 3600;

-- Control part size
ALTER TABLE events MODIFY SETTING
    min_bytes_for_wide_part = 10485760;
```

### Query Settings
```sql
SET max_threads = 4;
SET max_memory_usage = 10000000000;
SET max_execution_time = 60;
```

## Monitoring

### System Tables

#### query_log
```sql
SELECT
    type,
    query_start_time,
    query_duration_ms,
    query,
    read_rows,
    read_bytes,
    memory_usage
FROM system.query_log
WHERE event_date >= today()
ORDER BY query_duration_ms DESC
LIMIT 10;
```

#### parts
```sql
SELECT
    database,
    table,
    count() AS part_count,
    sum(rows) AS total_rows,
    sum(bytes_on_disk) AS total_bytes
FROM system.parts
WHERE active
GROUP BY database, table;
```

#### mutations
```sql
SELECT
    database,
    table,
    command,
    create_time,
    is_done,
    latest_failed_part
FROM system.mutations
WHERE NOT is_done;
```

## High Availability

### Replication Setup
```sql
-- On each replica
CREATE TABLE events_local ON CLUSTER my_cluster (
    event_time DateTime,
    user_id UInt64,
    event_type String
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

-- Distributed table
CREATE TABLE events ON CLUSTER my_cluster AS events_local
ENGINE = Distributed(my_cluster, default, events_local, rand());
```

### Cluster Configuration
```xml
<clickhouse>
  <remote_servers>
    <my_cluster>
      <shard>
        <replica>
          <host>node1</host>
          <port>9000</port>
        </replica>
        <replica>
          <host>node2</host>
          <port>9000</port>
        </replica>
      </shard>
      <shard>
        <replica>
          <host>node3</host>
          <port>9000</port>
        </replica>
        <replica>
          <host>node4</host>
          <port>9000</port>
        </replica>
      </shard>
    </my_cluster>
  </remote_servers>
</clickhouse>
```

## Use Cases

### Real-Time Analytics Dashboard
- Sub-second query response times
- Billions of rows scanned per query
- Concurrent user queries

### Log Analytics
- High ingestion rates (millions/sec)
- Full-text search capabilities
- Time-series analysis

### User Behavior Analysis
- Event tracking and funnel analysis
- Session aggregation
- Cohort analysis

### Monitoring & Observability
- Metrics storage and querying
- Distributed tracing backend
- Application performance monitoring

## Best Practices

1. **Choose appropriate ORDER BY**: Put most filtered columns first
2. **Use partitioning wisely**: Partition by time for easy data management
3. **Leverage materialized views**: Pre-aggregate heavy queries
4. **Monitor merge activity**: Too many parts slow down queries
5. **Use LowCardinality**: For columns with < 10,000 unique values
6. **Avoid SELECT ***: Query only needed columns
7. **Use PREWHERE**: For filtering before reading all columns
8. **Batch inserts**: Insert in batches of 10,000+ rows
9. **Set TTL**: Automatically delete old data
10. **Monitor resource usage**: Watch memory and disk I/O

## Comparison with Other Databases

| Feature | ClickHouse | Druid | Pinot |
|---------|-----------|-------|-------|
| Query Latency | Sub-second | Sub-second | Sub-second |
| Ingestion | High | Very High | Very High |
| SQL Support | Full | Limited | Good |
| Compression | Excellent | Good | Good |
| Joins | Yes | Limited | Limited |
| Updates | Difficult | No | No |
| Deduplication | Manual | Limited | Yes |

## Resources

- Official documentation: https://clickhouse.com/docs
- GitHub: https://github.com/ClickHouse/ClickHouse
- Community Slack and Telegram
- ClickHouse meetups and conferences
