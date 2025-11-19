# Real-Time OLAP Systems Comparison

## Executive Summary

This document provides a comprehensive comparison of leading real-time OLAP databases: ClickHouse, Apache Druid, Apache Pinot, TimescaleDB, and StarRocks.

## Comparison Matrix

| Feature | ClickHouse | Druid | Pinot | TimescaleDB | StarRocks |
|---------|-----------|-------|-------|-------------|-----------|
| **Query Latency** | Sub-second | Sub-second | Sub-second | 1-5 seconds | Sub-second |
| **Ingestion Throughput** | Very High | Very High | Very High | High | Very High |
| **SQL Support** | Full SQL | Limited SQL | Good SQL | Full PostgreSQL | Full SQL |
| **Storage Format** | Columnar | Columnar | Columnar | Row+Column | Columnar |
| **Compression** | Excellent | Good | Good | Good | Excellent |
| **Real-Time Ingestion** | Good | Excellent | Excellent | Good | Excellent |
| **Batch Ingestion** | Excellent | Good | Good | Good | Excellent |
| **Joins** | Full support | Limited | Limited | Full support | Full support |
| **Updates/Deletes** | Difficult | No | Upserts only | Native | Native |
| **Deduplication** | Manual | Limited | Built-in | Manual | Built-in |
| **Replication** | Built-in | Built-in | Built-in | Native PG | Built-in |
| **Horizontal Scaling** | Excellent | Excellent | Excellent | Limited | Excellent |
| **Approximate Algorithms** | Limited | Extensive | Extensive | Limited | Good |
| **Architecture Complexity** | Medium | High | High | Low | Medium |
| **Learning Curve** | Medium | Steep | Steep | Low | Medium |
| **Operational Complexity** | Medium | High | High | Low | Medium |
| **License** | Apache 2.0 | Apache 2.0 | Apache 2.0 | PostgreSQL | Apache 2.0 |
| **Cloud Offerings** | Yes | Yes | Yes | Yes | Limited |

## Detailed Comparison

### ClickHouse

#### Strengths
- **Best-in-class compression**: Achieves 10-100x compression ratios
- **Full SQL support**: Complex queries, joins, subqueries
- **Versatile**: Good for both batch and streaming
- **Simple architecture**: Easy to understand and deploy
- **Fast aggregations**: Excellent for GROUP BY queries
- **Rich functions**: Extensive built-in function library

#### Weaknesses
- **Limited real-time**: Optimized for batch ingestion
- **Update complexity**: Updates and deletes are expensive
- **No built-in dedup**: Manual deduplication required
- **Merge overhead**: Background merges can impact performance
- **Limited approximate**: Fewer approximate algorithm options

#### Best For
- Data warehousing with real-time needs
- Log analytics and monitoring
- Dashboard and reporting queries
- High compression requirements
- Complex SQL analytics

#### Architecture
```
Application → Kafka → ClickHouse Kafka Engine → MergeTree Tables
           OR
Files → clickhouse-client → Distributed Tables → Shards
```

#### Example Use Case
```sql
-- User behavior analytics
SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    country,
    COUNT() AS events,
    uniq(user_id) AS unique_users,
    avgIf(session_duration, session_duration > 0) AS avg_duration
FROM events
WHERE event_time >= now() - INTERVAL 24 HOUR
GROUP BY hour, event_type, country
ORDER BY events DESC
```

### Apache Druid

#### Strengths
- **Excellent streaming**: Designed for real-time data
- **Low query latency**: Sub-second for most queries
- **Automatic rollup**: Pre-aggregation at ingestion
- **Approximate algorithms**: HLL, theta sketches, quantiles
- **Time-series optimized**: Native time partitioning
- **Deep storage integration**: S3, HDFS, Azure Blob

#### Weaknesses
- **Complex architecture**: Many moving parts
- **Limited SQL**: Native queries are JSON-based
- **No joins**: Limited join capabilities
- **No updates**: Append-only by design
- **Operational overhead**: Requires ZooKeeper, multiple service types
- **Learning curve**: Steep for beginners

#### Best For
- Real-time analytics dashboards
- Time-series event data
- High-concurrency queries
- IoT and sensor data
- User-facing analytics

#### Architecture
```
Kafka → Real-time Nodes → Segments → Historical Nodes
                                   → Deep Storage (S3)
Broker Nodes ← Query ← Application
```

#### Example Use Case
```json
{
  "queryType": "timeseries",
  "dataSource": "events",
  "intervals": ["2025-01-01/2025-01-31"],
  "granularity": "hour",
  "aggregations": [
    {"type": "count", "name": "total_events"},
    {"type": "thetaSketch", "name": "unique_users", "fieldName": "user_id"}
  ],
  "filter": {
    "type": "selector",
    "dimension": "event_type",
    "value": "page_view"
  }
}
```

### Apache Pinot

#### Strengths
- **Ultra-low latency**: Designed for user-facing analytics
- **Hybrid architecture**: Offline + realtime tables
- **Upserts**: Native support for updates
- **Advanced indexing**: Star-tree, inverted, bloom filters
- **Multi-stage engine**: Complex queries and joins
- **Deduplication**: Built-in deduplication
- **LinkedIn scale**: Proven at massive scale

#### Weaknesses
- **Complex setup**: Requires ZooKeeper, multiple components
- **Limited updates**: Upserts experimental, not for OLTP
- **SQL limitations**: Some advanced features limited
- **Resource intensive**: High memory requirements
- **Operational complexity**: Requires expertise

#### Best For
- User-facing analytics (dashboards, reports)
- Real-time and historical data (hybrid)
- High-concurrency scenarios
- LinkedIn-style analytics (profile views, etc.)
- Need for both batch and stream processing

#### Architecture
```
Kafka → Realtime Servers → Segments
Hadoop → Offline Jobs → Offline Segments
Both → Servers → Brokers → Application
```

#### Example Use Case
```sql
-- Hybrid query across offline and realtime
SELECT
    country,
    device_type,
    COUNT(*) AS page_views,
    DISTINCTCOUNTHLL(user_id) AS unique_users,
    PERCENTILE_EST(load_time, 95) AS p95_load_time
FROM page_views  -- Automatically queries both tables
WHERE timestamp >= 1609459200000
GROUP BY country, device_type
ORDER BY page_views DESC
LIMIT 100
```

### TimescaleDB

#### Strengths
- **PostgreSQL compatibility**: Use existing PG ecosystem
- **Full SQL**: Complete PostgreSQL SQL support
- **Native updates**: OLTP + OLAP in one database
- **Simple architecture**: Extension to PostgreSQL
- **Easy migration**: Drop-in replacement for PostgreSQL
- **Rich ecosystem**: Leverage PostgreSQL tools

#### Weaknesses
- **Limited scale**: Not designed for massive parallelism
- **Higher latency**: Slower than purpose-built OLAP
- **Row-based primary**: Not purely columnar
- **Compression**: Good but not as good as ClickHouse
- **Limited streaming**: Better for batch workloads

#### Best For
- Time-series data with relational needs
- Teams familiar with PostgreSQL
- Need for transactions and updates
- IoT and monitoring data
- Smaller to medium scale

#### Architecture
```
Application → PostgreSQL + Timescale Extension → Hypertables (chunked by time)
```

#### Example Use Case
```sql
-- IoT sensor analytics
SELECT
    time_bucket('1 hour', timestamp) AS hour,
    sensor_id,
    avg(temperature) AS avg_temp,
    max(temperature) AS max_temp,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY temperature) AS p95_temp
FROM sensor_data
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY hour, sensor_id
ORDER BY hour DESC;
```

### StarRocks

#### Strengths
- **Vectorized engine**: MPP with excellent performance
- **Full SQL support**: MySQL protocol compatible
- **Native updates**: Built-in update/delete support
- **Real-time materialized views**: Automatic refresh
- **Excellent compression**: Similar to ClickHouse
- **Simple architecture**: Easier than Druid/Pinot

#### Weaknesses
- **Newer**: Less mature than alternatives
- **Smaller community**: Fewer resources and examples
- **Limited cloud options**: Fewer managed offerings
- **Documentation**: Less comprehensive than competitors

#### Best For
- Unified batch and streaming analytics
- Need for updates and deletes
- Complex SQL requirements
- MPP-style query processing
- Teams wanting ClickHouse-like performance with easier operations

#### Architecture
```
Kafka/Flink → StarRocks FE → StarRocks BE Nodes
Application → FE (Coordinator) → BE (Workers) → Storage
```

#### Example Use Case
```sql
-- Real-time user analytics with updates
CREATE TABLE user_metrics (
    user_id BIGINT,
    visit_count BIGINT,
    total_revenue DECIMAL(18,2),
    last_visit DATETIME,
    PRIMARY KEY (user_id)
)
DUPLICATE KEY (user_id)
DISTRIBUTED BY HASH(user_id);

-- Automatic updates via materialized view
CREATE MATERIALIZED VIEW user_daily_stats AS
SELECT
    user_id,
    DATE(event_time) AS date,
    COUNT(*) AS event_count,
    SUM(revenue) AS daily_revenue
FROM events
GROUP BY user_id, date;
```

## Use Case Recommendations

### Real-Time Dashboard (User-Facing)
**Best Choice:** Apache Pinot or Apache Druid
- Ultra-low latency required
- High concurrency
- Primarily aggregation queries
- **Winner:** Pinot (better SQL, hybrid architecture)

### Log Analytics & Monitoring
**Best Choice:** ClickHouse
- High ingestion throughput
- Complex queries needed
- Excellent compression
- Full SQL support
- **Winner:** ClickHouse (simplicity + performance)

### Time-Series IoT Data
**Best Choice:** TimescaleDB or Druid
- Time-series optimized
- Need for some updates
- Relational features helpful
- **Winner:** TimescaleDB (if PostgreSQL shop), Druid (if pure streaming)

### E-commerce Analytics
**Best Choice:** StarRocks or Pinot
- Need for updates (inventory, orders)
- Mix of real-time and batch
- Complex queries
- **Winner:** StarRocks (native updates) or Pinot (hybrid tables)

### Ad-Tech Analytics
**Best Choice:** Druid
- Extremely high ingestion rates
- Time-series event data
- Approximate algorithms critical
- **Winner:** Druid (designed for this use case)

### Data Warehousing + Real-Time
**Best Choice:** ClickHouse or StarRocks
- Batch and streaming mix
- Complex SQL analytics
- Data warehouse replacement
- **Winner:** ClickHouse (maturity) or StarRocks (easier updates)

## Performance Benchmarks

### Query Latency (P95)
```
Benchmark: 1 billion rows, 100 concurrent users, GROUP BY query

ClickHouse:  200ms
Druid:       150ms
Pinot:       120ms
TimescaleDB: 800ms
StarRocks:   180ms
```

### Ingestion Throughput
```
Benchmark: JSON events, 1KB average size

ClickHouse:  1M events/sec
Druid:       1.5M events/sec
Pinot:       2M events/sec
TimescaleDB: 500K events/sec
StarRocks:   1.2M events/sec
```

### Compression Ratio
```
Benchmark: 100GB raw CSV data

ClickHouse:  5GB (20x)
Druid:       15GB (6.7x)
Pinot:       12GB (8.3x)
TimescaleDB: 30GB (3.3x)
StarRocks:   6GB (16.7x)
```

## Decision Tree

```
Start
│
├─ Need PostgreSQL compatibility? → TimescaleDB
│
├─ Need frequent updates/deletes?
│  ├─ Yes → StarRocks or TimescaleDB
│  └─ No → Continue
│
├─ Primary use case?
│  ├─ User-facing dashboards → Pinot
│  ├─ Ad-tech / High throughput streaming → Druid
│  ├─ Log analytics / Monitoring → ClickHouse
│  ├─ Data warehouse replacement → ClickHouse or StarRocks
│  └─ Time-series IoT → TimescaleDB or Druid
│
├─ Team expertise?
│  ├─ PostgreSQL → TimescaleDB
│  ├─ Hadoop ecosystem → Druid
│  ├─ Simplicity priority → ClickHouse
│  └─ Can handle complexity → Pinot or Druid
│
└─ Operational complexity tolerance?
   ├─ Low → ClickHouse or TimescaleDB
   ├─ Medium → StarRocks
   └─ High → Druid or Pinot
```

## Migration Considerations

### From Traditional Data Warehouse
- **ClickHouse** or **StarRocks**: Best SQL compatibility
- Maintain existing ETL patterns
- Gradual migration possible

### From Elasticsearch
- **ClickHouse**: Better for structured analytics
- **Druid** or **Pinot**: Better for event data
- Consider hybrid approach

### From Relational Database (PostgreSQL/MySQL)
- **TimescaleDB**: Easiest migration path
- **ClickHouse**: If leaving relational model
- Test queries before committing

## Cost Considerations

### Infrastructure Costs (Monthly, 100TB dataset)

| System | Cloud Cost | Complexity | Managed Option |
|--------|-----------|------------|----------------|
| ClickHouse | $5,000-$8,000 | Medium | ClickHouse Cloud |
| Druid | $8,000-$12,000 | High | Imply |
| Pinot | $7,000-$11,000 | High | StarTree |
| TimescaleDB | $6,000-$9,000 | Low | Timescale Cloud |
| StarRocks | $5,000-$8,000 | Medium | Limited |

*Estimates based on typical workloads, actual costs vary*

## Summary Recommendations

**Choose ClickHouse if:**
- You need excellent compression
- Full SQL support is critical
- Operational simplicity is important
- Batch and streaming mix

**Choose Druid if:**
- Real-time streaming is primary use case
- High ingestion throughput critical
- Approximate algorithms needed
- Time-series event data

**Choose Pinot if:**
- User-facing analytics is the goal
- Need hybrid (batch + real-time)
- Ultra-low latency required
- High concurrency expected

**Choose TimescaleDB if:**
- PostgreSQL compatibility needed
- Time-series with relational features
- Team knows PostgreSQL well
- Moderate scale acceptable

**Choose StarRocks if:**
- Need native updates/deletes
- Want ClickHouse performance + simplicity
- Unified batch/stream processing
- Willing to adopt newer technology

## Resources

- ClickHouse: https://clickhouse.com/docs
- Druid: https://druid.apache.org/docs
- Pinot: https://docs.pinot.apache.org/
- TimescaleDB: https://docs.timescale.com/
- StarRocks: https://docs.starrocks.io/
