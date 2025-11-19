# Apache Pinot Features & Capabilities

## Introduction

Apache Pinot is a real-time distributed OLAP datastore designed to deliver ultra-low latency analytics even at extremely high throughput. Originally developed at LinkedIn, Pinot powers many of the world's largest user-facing analytics applications.

## Core Architecture

### Components

```
┌──────────────────────────────────────┐
│        External Storage              │
│   (HDFS, S3, Azure Blob)            │
└───────────────┬──────────────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
┌───▼────────┐      ┌───────▼────────┐
│  Offline   │      │   Real-time    │
│  Segments  │      │   Segments     │
└───┬────────┘      └────────┬───────┘
    │                        │
    └────────┬───────────────┘
             │
      ┌──────▼──────┐
      │   Servers   │
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │   Brokers   │
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │  Controller │
      └─────────────┘
```

### Process Types

#### Controller
- Cluster management and coordination
- Segment assignment to servers
- Schema and table management
- Health monitoring
- Rebalancing coordination

#### Broker
- Query routing and orchestration
- Result merging and aggregation
- Query optimization
- Connection pooling
- Request scatter-gather

#### Server
- **Realtime Server**: Consumes from streams, builds segments
- **Offline Server**: Serves pre-built segments from storage
- Query execution
- In-memory indexes
- Smart caching

#### Minion (Optional)
- Background task execution
- Segment merge and rollup
- Data purging and retention
- RealtimeToOffline segment conversion

## Key Features

### 1. Hybrid Table Architecture

#### Offline Table
```json
{
  "tableName": "events_OFFLINE",
  "tableType": "OFFLINE",
  "segmentsConfig": {
    "timeColumnName": "timestamp",
    "timeType": "MILLISECONDS",
    "segmentPushType": "APPEND",
    "segmentAssignmentStrategy": "BalanceNumSegmentAssignmentStrategy",
    "replication": "3"
  },
  "tableIndexConfig": {
    "loadMode": "MMAP",
    "invertedIndexColumns": ["user_id", "event_type"]
  }
}
```

**Characteristics:**
- Pre-built segments from batch processing
- Higher throughput ingestion
- Immutable, highly compressed
- Optimized for historical queries

#### Realtime Table
```json
{
  "tableName": "events_REALTIME",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "timeColumnName": "timestamp",
    "timeType": "MILLISECONDS",
    "replicasPerPartition": "2"
  },
  "tableIndexConfig": {
    "streamConfigs": {
      "streamType": "kafka",
      "stream.kafka.topic.name": "events-topic",
      "stream.kafka.broker.list": "localhost:9092",
      "stream.kafka.consumer.type": "lowlevel",
      "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
      "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder"
    }
  }
}
```

**Characteristics:**
- Consumes from streaming sources
- In-memory buffer, then persisted
- Low-latency data availability
- Automatic segment completion

#### Hybrid Table (Unified View)
```sql
-- Query seamlessly merges offline and realtime data
SELECT event_type, COUNT(*) AS count
FROM events  -- Automatically queries both OFFLINE and REALTIME
WHERE timestamp >= 1609459200000  -- 2021-01-01
GROUP BY event_type
ORDER BY count DESC
```

### 2. Advanced Indexing

#### Inverted Index
```json
{
  "tableIndexConfig": {
    "invertedIndexColumns": [
      "user_id",
      "country",
      "event_type"
    ]
  }
}
```

**Use Case:** Fast filtering on high-cardinality dimensions

#### Sorted Index
```json
{
  "tableIndexConfig": {
    "sortedColumn": ["timestamp"]
  }
}
```

**Use Case:** Range queries on sorted columns

#### Range Index
```json
{
  "tableIndexConfig": {
    "rangeIndexColumns": ["price", "age"]
  }
}
```

**Use Case:** Efficient range queries without inverted index overhead

#### Bloom Filter
```json
{
  "tableIndexConfig": {
    "bloomFilterColumns": ["transaction_id"]
  }
}
```

**Use Case:** Point lookups and deduplication

#### Star-Tree Index
```json
{
  "tableIndexConfig": {
    "starTreeIndexConfigs": [
      {
        "dimensionsSplitOrder": ["country", "device_type", "browser"],
        "functionColumnPairs": [
          "SUM__revenue",
          "COUNT__*",
          "MAX__session_duration"
        ],
        "maxLeafRecords": 10000
      }
    ]
  }
}
```

**Use Case:** Pre-aggregated multi-dimensional OLAP cubes

#### Text Index
```json
{
  "tableIndexConfig": {
    "textIndexColumns": ["description", "user_comment"]
  }
}
```

**Use Case:** Full-text search capabilities

#### JSON Index
```json
{
  "tableIndexConfig": {
    "jsonIndexColumns": ["metadata", "properties"]
  }
}
```

**Use Case:** Query nested JSON fields efficiently

### 3. Smart Query Routing

#### Segment Pruning
- Time-based pruning using segment time boundaries
- Partition pruning using partition metadata
- Bloom filter pruning for point lookups

#### Replica Selection
```json
{
  "routing": {
    "instanceSelectorType": "replicaGroup"
  }
}
```

**Strategies:**
- Balanced: Round-robin across replicas
- MinAvgLoadStrategy: Route to least loaded replica
- ReplicaGroup: Consistent routing for cache efficiency

### 4. Upserts (Experimental)

```json
{
  "tableName": "user_profiles",
  "tableType": "REALTIME",
  "segmentsConfig": {
    "timeColumnName": "last_modified",
    "replicasPerPartition": "2"
  },
  "upsertConfig": {
    "mode": "FULL",
    "partialUpsertStrategies": {
      "email": "OVERWRITE",
      "login_count": "INCREMENT"
    },
    "comparisonColumn": "last_modified",
    "hashFunction": "MURMUR3"
  }
}
```

**Capabilities:**
- Full upserts: Replace entire row
- Partial upserts: Update specific columns
- Deduplication based on primary key
- Merge strategies: OVERWRITE, INCREMENT, MAX, MIN

### 5. Multi-Stage Query Engine (v2)

```sql
-- Complex query with joins and subqueries
SELECT
  u.country,
  COUNT(DISTINCT e.user_id) AS active_users,
  SUM(e.revenue) AS total_revenue,
  AVG(e.session_duration) AS avg_duration
FROM events e
JOIN user_profiles u ON e.user_id = u.user_id
WHERE e.timestamp >= NOW() - INTERVAL '7' DAY
  AND u.subscription_tier = 'premium'
GROUP BY u.country
HAVING total_revenue > 10000
ORDER BY total_revenue DESC
LIMIT 20
```

**Features:**
- Distributed joins (broadcast and shuffle)
- Complex subqueries
- Window functions
- Set operations (UNION, INTERSECT, EXCEPT)
- CTEs (Common Table Expressions)

### 6. Streaming Integrations

#### Kafka
```json
{
  "streamConfigs": {
    "streamType": "kafka",
    "stream.kafka.topic.name": "events",
    "stream.kafka.broker.list": "kafka1:9092,kafka2:9092",
    "stream.kafka.consumer.type": "lowlevel",
    "stream.kafka.consumer.prop.auto.offset.reset": "smallest",
    "realtime.segment.flush.threshold.rows": "1000000",
    "realtime.segment.flush.threshold.time": "6h"
  }
}
```

#### Kinesis
```json
{
  "streamConfigs": {
    "streamType": "kinesis",
    "stream.kinesis.topic.name": "events-stream",
    "stream.kinesis.consumer.type": "lowlevel",
    "stream.kinesis.endpoint": "https://kinesis.us-east-1.amazonaws.com",
    "stream.kinesis.region": "us-east-1"
  }
}
```

#### Pulsar
```json
{
  "streamConfigs": {
    "streamType": "pulsar",
    "stream.pulsar.topic.name": "persistent://public/default/events",
    "stream.pulsar.bootstrap.servers": "pulsar://localhost:6650"
  }
}
```

### 7. Deduplication

```json
{
  "dedupConfig": {
    "dedupEnabled": true,
    "hashFunction": "MD5"
  }
}
```

**Approaches:**
- Dedup at ingestion time
- Dedup during segment merge
- Upsert-based deduplication

### 8. Tiering & Data Management

```json
{
  "tierConfigs": [
    {
      "name": "hotTier",
      "segmentSelectorType": "time",
      "segmentAge": "3d",
      "storageType": "PINOT_SERVER"
    },
    {
      "name": "coldTier",
      "segmentSelectorType": "time",
      "segmentAge": "30d",
      "storageType": "S3"
    }
  ]
}
```

**Benefits:**
- Cost optimization
- Performance tuning
- Automatic data lifecycle management

## Query Capabilities

### SQL Support

#### Standard SQL
```sql
SELECT
  country,
  device_type,
  COUNT(*) AS events,
  SUM(revenue) AS total_revenue,
  AVG(session_duration) AS avg_duration,
  PERCENTILE_EST(load_time, 95) AS p95_load_time
FROM events
WHERE timestamp BETWEEN 1609459200000 AND 1612137599999
  AND event_type IN ('page_view', 'purchase')
GROUP BY country, device_type
HAVING events > 1000
ORDER BY total_revenue DESC
LIMIT 100
```

#### Aggregation Functions
- COUNT, SUM, AVG, MIN, MAX
- DISTINCTCOUNT, DISTINCTCOUNTHLL (HyperLogLog)
- PERCENTILE, PERCENTILEEST, PERCENTILETDIGEST
- STDDEV, VARIANCE
- COVAR_POP, COVAR_SAMP
- HISTOGRAM, FREQUENT_ITEMS

#### Advanced Functions

**Array Functions:**
```sql
SELECT
  ARRAY_LENGTH(tags) AS tag_count,
  ARRAY_CONTAINS(tags, 'premium') AS is_premium
FROM events
WHERE ARRAY_CONCAT(tags, labels) IS NOT NULL
```

**JSON Functions:**
```sql
SELECT
  JSON_EXTRACT_SCALAR(metadata, '$.device.os', 'STRING') AS os,
  JSON_EXTRACT_SCALAR(metadata, '$.geo.lat', 'DOUBLE') AS latitude
FROM events
WHERE JSON_MATCH(metadata, '"$.plan"=''premium''')
```

**DateTime Functions:**
```sql
SELECT
  DATETIMECONVERT(timestamp, '1:MILLISECONDS:EPOCH', '1:DAYS:SIMPLE_DATE_FORMAT:yyyy-MM-dd', '1:DAYS') AS date,
  TOEPOCHDAYS(timestamp) AS epoch_days,
  FROMEPOCHDAYS(18628) AS date_from_epoch
FROM events
```

**Geospatial Functions:**
```sql
SELECT
  ST_DISTANCE(ST_POINT(lon1, lat1), ST_POINT(lon2, lat2)) AS distance_km,
  ST_WITHIN(ST_POINT(longitude, latitude), ST_POLYGON('POLYGON((...))')
FROM locations
```

### Query Optimization

#### Limit Optimization
```sql
-- Automatically optimized with selection limit
SELECT * FROM events
WHERE user_id = '12345'
ORDER BY timestamp DESC
LIMIT 100
```

#### Filter Optimization
```sql
-- Pushed down to segment level
SELECT country, COUNT(*)
FROM events
WHERE timestamp >= 1609459200000
  AND event_type = 'purchase'
  AND country IN ('US', 'UK', 'DE')
GROUP BY country
```

## Performance Features

### 1. Smart Segment Assignment

#### Replica Groups
```json
{
  "routing": {
    "segmentPrunerTypes": ["time", "partition"],
    "instanceSelectorType": "replicaGroup"
  }
}
```

**Benefits:**
- Consistent cache hit rates
- Reduced network overhead
- Better query locality

### 2. Query Result Caching

```properties
# Enable result cache
pinot.broker.enable.query.limit.override=true
pinot.broker.query.response.limit=2147483647
```

### 3. Column Encoding

- **Dictionary Encoding**: String compression
- **Run-Length Encoding**: Repeated values
- **Bit Packing**: Small value ranges
- **Fixed-Width**: Numeric types
- **Variable-Width**: Variable-length strings

### 4. Smart Data Placement

```json
{
  "segmentsConfig": {
    "segmentAssignmentStrategy": "BalanceNumSegmentAssignmentStrategy",
    "replication": "3"
  }
}
```

**Strategies:**
- BalanceNumSegmentAssignment
- ReplicaGroupSegmentAssignment
- BestEffortReplicaGroupSegmentAssignment

## Monitoring & Observability

### Metrics

#### Query Metrics
```
pinot.broker.queries - Total queries
pinot.broker.queryExecutionTime - Execution time
pinot.broker.scatterGatherStats - Distribution stats
pinot.server.queries - Server-side queries
```

#### Ingestion Metrics
```
pinot.server.realtimeRowsConsumed - Rows consumed
pinot.server.realtimeRowsDropped - Dropped rows
pinot.server.realtimeOffsetCommits - Offset commits
pinot.server.realtimeConsumptionExceptions - Errors
```

#### System Metrics
```
pinot.server.segmentCount - Segments per server
pinot.controller.tableCount - Total tables
pinot.controller.offlineTableCount - Offline tables
pinot.controller.realtimeTableCount - Realtime tables
```

### Query Console

```sql
-- View table configuration
SHOW CONFIG FROM events;

-- View segments
SELECT * FROM segments_metadata WHERE table = 'events';

-- Query stats
SELECT * FROM query_metadata WHERE query_id = 'query_123';
```

## Best Practices

### Schema Design
1. **Choose appropriate data types**: Use INT instead of LONG when possible
2. **Minimize dimensions**: More dimensions = larger segments
3. **Use appropriate granularity**: Rollup at query granularity
4. **Index selectively**: Don't index everything
5. **Leverage star-tree for OLAP**: Pre-aggregate common queries

### Table Configuration
1. **Set appropriate replication**: Balance availability and storage
2. **Configure segment size**: 100k-5M rows per segment
3. **Use sorting**: Sort on most filtered column
4. **Enable bloom filters**: For high-cardinality lookups
5. **Configure retention**: Auto-delete old segments

### Query Optimization
1. **Filter on indexed columns**: Use inverted indexes
2. **Prune segments**: Filter on time column
3. **Limit result sets**: Use LIMIT appropriately
4. **Avoid SELECT ***: Query only needed columns
5. **Use approximation**: DISTINCTCOUNTHLL for uniques

### Ingestion
1. **Batch real-time writes**: Higher throughput
2. **Monitor consumer lag**: Keep lag minimal
3. **Optimize segment flush**: Balance latency and efficiency
4. **Use appropriate partitioning**: Match Kafka partitions
5. **Handle late data**: Configure allowed lateness

## Use Cases

### User-Facing Analytics
- LinkedIn's "Who Viewed Your Profile"
- Uber's driver earnings dashboard
- Slice (restaurant analytics)

### Internal Analytics
- Application monitoring
- Business metrics
- A/B test analysis

### Anomaly Detection
- Real-time fraud detection
- Network security monitoring
- System health monitoring

## Resources

- Documentation: https://docs.pinot.apache.org/
- GitHub: https://github.com/apache/pinot
- Slack: https://apache-pinot.slack.com/
- Mailing List: dev@pinot.apache.org
