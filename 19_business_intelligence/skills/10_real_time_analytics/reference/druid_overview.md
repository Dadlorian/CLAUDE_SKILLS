# Apache Druid Overview

## Introduction

Apache Druid is a real-time analytical database designed for sub-second queries on event-driven data with high concurrency. It combines the best features of data warehouses, time-series databases, and search systems.

## Architecture

### Core Components

```
┌─────────────────────────────────────┐
│         Deep Storage                 │
│    (S3, HDFS, Azure Blob)           │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────┐      ┌──────▼─────┐
│Historical│      │  Real-time  │
│  Nodes   │      │   Nodes     │
└───┬──────┘      └──────┬─────┘
    │                    │
    └──────────┬─────────┘
               │
         ┌─────▼─────┐
         │  Broker   │
         │  Nodes    │
         └───────────┘
               │
         ┌─────▼─────┐
         │  Clients  │
         └───────────┘
```

### Process Types

#### Master Services

**Coordinator**
- Manages segment availability on Historical nodes
- Handles segment load/drop rules
- Rebalances segments across cluster
- Enforces retention policies

**Overlord**
- Manages ingestion tasks
- Distributes work to MiddleManagers
- Monitors task completion
- Handles task failures

#### Data Services

**Historical Nodes**
- Serve immutable segments from deep storage
- Cache segments locally for fast queries
- Handle bulk of query processing
- Scale horizontally

**MiddleManager**
- Execute ingestion tasks (Peons)
- Handle real-time data ingestion
- Create and publish segments
- Isolated task execution

**Indexer (Alternative to MiddleManager)**
- Unified process for batch and streaming
- Better resource utilization
- Simpler deployment model

#### Query Services

**Broker**
- Route queries to appropriate nodes
- Merge results from multiple nodes
- Cache query results
- Handle query prioritization

**Router (Optional)**
- API gateway for Druid cluster
- Query routing and load balancing
- Multi-tenancy support
- Authentication/authorization

## Data Model

### Datasource Structure

A Druid datasource consists of:

#### Timestamp Column
```json
{
  "type": "long",
  "column": "__time",
  "format": "millis"
}
```
**Required**: Every event must have a timestamp

#### Dimensions
```json
{
  "dimensions": [
    "country",
    "city",
    "device_type",
    {
      "name": "user_id",
      "type": "long"
    }
  ]
}
```
**Purpose**: Attributes for filtering and grouping

#### Metrics
```json
{
  "metricsSpec": [
    {
      "type": "count",
      "name": "count"
    },
    {
      "type": "longSum",
      "name": "total_amount",
      "fieldName": "amount"
    },
    {
      "type": "hyperUnique",
      "name": "unique_users",
      "fieldName": "user_id"
    }
  ]
}
```
**Purpose**: Pre-aggregated values for fast queries

### Segment Structure

```
Segment (immutable, time-partitioned):
├── version.bin
├── meta.smoosh
└── data columns:
    ├── __time (timestamp column)
    ├── dimension_1 (dictionary encoded)
    ├── dimension_2 (dictionary encoded)
    ├── metric_1 (numeric column)
    └── metric_2 (numeric column)
```

#### Segment Characteristics
- **Immutable**: Once created, never modified
- **Time-Partitioned**: Typically by hour or day
- **Columnar**: Each column stored separately
- **Compressed**: Dictionary encoding, bitmap indexes
- **Versioned**: For handling reingestion

## Ingestion

### Streaming Ingestion

#### Kafka Ingestion
```json
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "events",
      "timestampSpec": {
        "column": "timestamp",
        "format": "iso"
      },
      "dimensionsSpec": {
        "dimensions": [
          "user_id",
          "event_type",
          "country"
        ]
      },
      "metricsSpec": [
        {
          "type": "count",
          "name": "count"
        },
        {
          "type": "longSum",
          "name": "revenue",
          "fieldName": "amount"
        }
      ],
      "granularitySpec": {
        "type": "uniform",
        "segmentGranularity": "HOUR",
        "queryGranularity": "MINUTE",
        "rollup": true
      }
    },
    "ioConfig": {
      "topic": "events-topic",
      "consumerProperties": {
        "bootstrap.servers": "localhost:9092"
      },
      "taskCount": 1,
      "replicas": 2,
      "taskDuration": "PT1H"
    },
    "tuningConfig": {
      "type": "kafka",
      "maxRowsPerSegment": 5000000,
      "maxRowsInMemory": 1000000,
      "intermediatePersistPeriod": "PT10M"
    }
  }
}
```

#### Kinesis Ingestion
```json
{
  "type": "kinesis",
  "spec": {
    "ioConfig": {
      "stream": "events-stream",
      "endpoint": "kinesis.us-east-1.amazonaws.com",
      "taskCount": 2,
      "replicas": 1,
      "taskDuration": "PT1H"
    }
  }
}
```

### Batch Ingestion

#### Native Batch
```json
{
  "type": "index_parallel",
  "spec": {
    "dataSchema": {
      "dataSource": "historical_events",
      "timestampSpec": {
        "column": "timestamp",
        "format": "auto"
      },
      "dimensionsSpec": {
        "dimensions": ["user_id", "event_type"]
      },
      "metricsSpec": [
        {"type": "count", "name": "count"}
      ],
      "granularitySpec": {
        "type": "uniform",
        "segmentGranularity": "DAY",
        "queryGranularity": "HOUR",
        "rollup": true
      }
    },
    "ioConfig": {
      "type": "index_parallel",
      "inputSource": {
        "type": "s3",
        "uris": ["s3://bucket/path/to/data/*.json"]
      },
      "inputFormat": {
        "type": "json"
      }
    }
  }
}
```

## Query API

### Native Query

#### TimeSeries Query
```json
{
  "queryType": "timeseries",
  "dataSource": "events",
  "intervals": ["2025-01-01/2025-01-31"],
  "granularity": "day",
  "aggregations": [
    {
      "type": "count",
      "name": "total_events"
    },
    {
      "type": "longSum",
      "name": "total_revenue",
      "fieldName": "revenue"
    }
  ],
  "filter": {
    "type": "selector",
    "dimension": "country",
    "value": "US"
  }
}
```

#### TopN Query
```json
{
  "queryType": "topN",
  "dataSource": "events",
  "intervals": ["2025-01-01/2025-01-31"],
  "granularity": "all",
  "dimension": "event_type",
  "metric": "count",
  "threshold": 10,
  "aggregations": [
    {
      "type": "count",
      "name": "count"
    }
  ]
}
```

#### GroupBy Query
```json
{
  "queryType": "groupBy",
  "dataSource": "events",
  "intervals": ["2025-01-01/2025-01-31"],
  "granularity": "day",
  "dimensions": ["country", "device_type"],
  "aggregations": [
    {
      "type": "count",
      "name": "count"
    },
    {
      "type": "thetaSketch",
      "name": "unique_users",
      "fieldName": "user_id_sketch"
    }
  ],
  "filter": {
    "type": "and",
    "fields": [
      {
        "type": "selector",
        "dimension": "event_type",
        "value": "purchase"
      },
      {
        "type": "bound",
        "dimension": "amount",
        "lower": "100"
      }
    ]
  }
}
```

### SQL Query

```sql
SELECT
  TIME_FLOOR(__time, 'PT1H') AS hour,
  country,
  COUNT(*) AS event_count,
  SUM(revenue) AS total_revenue,
  APPROX_COUNT_DISTINCT_DS_THETA(user_id_sketch) AS unique_users
FROM events
WHERE __time BETWEEN '2025-01-01' AND '2025-01-31'
  AND event_type = 'purchase'
GROUP BY 1, 2
ORDER BY total_revenue DESC
LIMIT 100
```

## Advanced Features

### Rollup

**Automatic Pre-Aggregation**
```json
{
  "granularitySpec": {
    "rollup": true,
    "queryGranularity": "MINUTE"
  }
}
```

**Effect:**
- Reduces storage by combining rows
- Faster queries on aggregated data
- Loss of event-level detail

### Approximate Algorithms

#### HyperLogLog (Unique Counts)
```json
{
  "type": "hyperUnique",
  "name": "unique_users",
  "fieldName": "user_id"
}
```

#### Theta Sketches
```json
{
  "type": "thetaSketch",
  "name": "user_sketch",
  "fieldName": "user_id",
  "size": 16384
}
```

#### DataSketches (Quantiles)
```json
{
  "type": "quantilesDoublesSketch",
  "name": "latency_quantiles",
  "fieldName": "latency",
  "k": 128
}
```

### Lookups (Dimension Enrichment)

```json
{
  "type": "map",
  "map": {
    "US": "United States",
    "UK": "United Kingdom",
    "DE": "Germany"
  }
}
```

**Query with Lookup:**
```sql
SELECT
  LOOKUP(country_code, 'country_names') AS country_name,
  COUNT(*) AS events
FROM events
GROUP BY 1
```

### Multi-Value Dimensions

```json
{
  "dimensions": [
    {
      "name": "tags",
      "type": "string",
      "multiValueHandling": "SORTED_ARRAY"
    }
  ]
}
```

**Query:**
```sql
SELECT
  tags,
  COUNT(*) AS count
FROM events
WHERE ARRAY_CONTAINS(tags, 'promotion')
GROUP BY tags
```

## Performance Optimization

### Indexing Strategies

#### Segment Size
```json
{
  "tuningConfig": {
    "maxRowsPerSegment": 5000000,
    "maxRowsInMemory": 1000000
  }
}
```

**Guidelines:**
- 5-10 million rows per segment
- 300-700 MB compressed size
- Balance between parallelism and overhead

#### Partitioning

**Hash Partitioning:**
```json
{
  "partitionsSpec": {
    "type": "hashed",
    "numShards": 4,
    "partitionDimensions": ["user_id"]
  }
}
```

**Range Partitioning:**
```json
{
  "partitionsSpec": {
    "type": "single_dim",
    "partitionDimension": "country",
    "targetRowsPerSegment": 5000000
  }
}
```

### Query Optimization

#### Filter Early
```sql
-- Good: Filter before aggregation
SELECT country, COUNT(*)
FROM events
WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '1' DAY
  AND event_type = 'purchase'
GROUP BY country

-- Bad: Filter after aggregation
SELECT country, event_count
FROM (
  SELECT country, event_type, COUNT(*) AS event_count
  FROM events
  WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '1' DAY
  GROUP BY country, event_type
)
WHERE event_type = 'purchase'
```

#### Use Appropriate Granularity
```sql
-- For hourly trends, use hour granularity
SELECT TIME_FLOOR(__time, 'PT1H') AS hour, COUNT(*)
FROM events
GROUP BY 1

-- Not: GROUP BY __time (minute granularity)
```

#### Leverage Rollup
```sql
-- Efficient with rollup=true
SELECT DATE_TRUNC('day', __time) AS day,
       SUM(count) AS total
FROM events
GROUP BY 1

-- Inefficient without rollup
SELECT DATE_TRUNC('day', __time) AS day,
       COUNT(*) AS total
FROM events
GROUP BY 1
```

### Caching

#### Broker Cache
```properties
druid.broker.cache.useCache=true
druid.broker.cache.populateCache=true
druid.cache.type=caffeine
druid.cache.sizeInBytes=1000000000
```

#### Historical Cache
```properties
druid.historical.cache.useCache=true
druid.historical.cache.populateCache=true
```

## Monitoring

### Metrics

#### Ingestion Metrics
- `ingest/events/processed`: Events ingested per second
- `ingest/rows/output`: Rows persisted after rollup
- `ingest/persists/count`: Number of persist operations
- `ingest/kafka/lag`: Consumer lag

#### Query Metrics
- `query/time`: Query execution time
- `query/bytes`: Bytes scanned
- `query/cpu/time`: CPU time consumed
- `query/count`: Number of queries

#### Segment Metrics
- `segment/count`: Number of segments
- `segment/size`: Total segment size
- `segment/unavailable/count`: Unavailable segments
- `segment/loadQueue/count`: Segments waiting to load

### System Tables

```sql
-- List all datasources
SELECT * FROM INFORMATION_SCHEMA.SCHEMATA;

-- Table structure
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'events';

-- Segment information
SELECT * FROM sys.segments
WHERE datasource = 'events'
ORDER BY start DESC
LIMIT 10;
```

## High Availability

### Replication

```properties
# Coordinator configuration
druid.coordinator.startDelay=PT30S
druid.coordinator.period=PT30S

# Replication rules
[
  {
    "type": "loadForever",
    "tieredReplicants": {
      "hot": 2,
      "_default_tier": 1
    }
  }
]
```

### Load Balancing

```properties
# Broker configuration
druid.broker.balancer.type=cachingCost
druid.broker.select.tier=highPriority
druid.broker.select.tier.highPriority.minSegmentCount=10
```

### Disaster Recovery

1. **Deep Storage**: All segments backed up in S3/HDFS
2. **Metadata**: Replicated MySQL/PostgreSQL database
3. **ZooKeeper**: Multi-node quorum
4. **Process Redundancy**: Multiple instances of each service

## Use Cases

### Real-Time Analytics
- User behavior analysis
- Application performance monitoring
- Clickstream analytics
- IoT sensor data analysis

### Business Intelligence
- Interactive dashboards
- Ad-hoc exploration
- Multi-dimensional OLAP
- Time-series analysis

### Operational Intelligence
- Log analytics
- Network traffic analysis
- Security event monitoring
- System metrics aggregation

## Best Practices

1. **Design for Query Patterns**: Choose dimensions and metrics based on queries
2. **Use Rollup**: Enable rollup for dashboard queries
3. **Partition Appropriately**: Use hash partitioning for high-cardinality dimensions
4. **Monitor Segment Count**: Too many small segments hurt performance
5. **Configure Retention**: Auto-delete old data with load rules
6. **Use Sketches**: Approximate algorithms for large cardinality
7. **Pre-Aggregate**: Use rollup and materialized views
8. **Tune Segment Size**: Balance between parallelism and overhead
9. **Cache Wisely**: Enable caching for repeated queries
10. **Monitor Ingestion Lag**: Keep real-time ingestion current

## Comparison with Other Systems

| Feature | Druid | ClickHouse | Pinot |
|---------|-------|-----------|-------|
| **Query Latency** | Very Low | Very Low | Very Low |
| **Ingestion** | Real-time | Batch-oriented | Real-time |
| **SQL Support** | Good | Excellent | Good |
| **Approximate** | Yes | Limited | Yes |
| **Rollup** | Yes | Manual | Yes |
| **Updates** | No | Difficult | No |
| **Architecture** | Complex | Simple | Complex |

## Resources

- Official Docs: https://druid.apache.org/docs/latest/
- GitHub: https://github.com/apache/druid
- Community: https://druid.apache.org/community/
- Imply (Commercial): https://imply.io/
