# Real-Time Analytics Latency Requirements

## Overview

Understanding and meeting latency requirements is critical for real-time analytics systems. This document covers latency definitions, measurement, optimization, and SLA design.

## Latency Definitions

### End-to-End Latency
**Definition:** Time from event occurrence to query result availability

```
Event → Ingestion → Processing → Storage → Query → Result
│←──────────── End-to-End Latency ──────────────→│
```

**Components:**
1. **Event Generation Latency**: Application to message queue (1-10ms)
2. **Network Latency**: Queue to processor (5-50ms)
3. **Processing Latency**: Transform and aggregate (10-1000ms)
4. **Storage Latency**: Write to database (10-500ms)
5. **Query Latency**: Read and compute (10-5000ms)

### Common Latency Tiers

| Tier | Latency | Use Cases | Technologies |
|------|---------|-----------|--------------|
| **Ultra-Low** | < 100ms | Fraud detection, Trading | Redis, Druid, Pinot |
| **Low** | 100ms - 1s | Dashboards, Monitoring | ClickHouse, Druid, Pinot |
| **Medium** | 1s - 10s | Analytics, BI | ClickHouse, StarRocks |
| **High** | 10s - 60s | Reporting, Batch | Spark, traditional DWH |
| **Batch** | > 1 minute | Historical analysis | Hadoop, Data Warehouse |

## Measuring Latency

### Event Time vs Processing Time

```
Event Time: When event actually occurred
Processing Time: When system processes the event

Example:
Event occurred:  2025-01-15 10:00:00.000
Received:        2025-01-15 10:00:00.100  (100ms network delay)
Processed:       2025-01-15 10:00:00.250  (150ms processing)
Available:       2025-01-15 10:00:00.350  (100ms storage)
Queryable:       2025-01-15 10:00:00.400  (50ms indexing)

Total Latency: 400ms
```

### Latency Metrics

#### P50 (Median)
- 50% of requests complete faster
- Typical user experience
- Can hide problems

#### P95 (95th Percentile)
- 95% of requests complete faster
- Better indicator of user experience
- Industry standard SLA metric

#### P99 (99th Percentile)
- 99% of requests complete faster
- Shows tail latency issues
- Critical for user-facing systems

#### P99.9 (99.9th Percentile)
- Extreme tail latency
- Important for high-scale systems
- Often reveals infrastructure issues

### Measurement Implementation

```python
import time
from collections import defaultdict
import numpy as np

class LatencyTracker:
    def __init__(self):
        self.latencies = defaultdict(list)

    def record(self, stage, latency_ms):
        """Record latency for a specific stage"""
        self.latencies[stage].append(latency_ms)

    def get_percentiles(self, stage):
        """Calculate percentiles for a stage"""
        values = self.latencies[stage]
        if not values:
            return {}

        return {
            'p50': np.percentile(values, 50),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99),
            'p99.9': np.percentile(values, 99.9),
            'max': max(values),
            'avg': np.mean(values)
        }

# Usage
tracker = LatencyTracker()

# Track end-to-end
start = time.time()
event_id = produce_event(event)
tracker.record('ingestion', (time.time() - start) * 1000)

start = time.time()
process_event(event_id)
tracker.record('processing', (time.time() - start) * 1000)

start = time.time()
result = query_event(event_id)
tracker.record('query', (time.time() - start) * 1000)

# Get stats
print(tracker.get_percentiles('ingestion'))
print(tracker.get_percentiles('processing'))
print(tracker.get_percentiles('query'))
```

### Kafka Lag Monitoring

```java
public class KafkaLagMonitor {
    private final KafkaConsumer<String, String> consumer;

    public Map<TopicPartition, LagMetrics> measureLag() {
        Map<TopicPartition, LagMetrics> lagMap = new HashMap<>();

        for (TopicPartition partition : consumer.assignment()) {
            long currentOffset = consumer.position(partition);
            long endOffset = consumer.endOffsets(
                Collections.singleton(partition)
            ).get(partition);

            long lag = endOffset - currentOffset;

            // Estimate time lag based on production rate
            long estimatedTimeMs = estimateTimeLag(partition, lag);

            lagMap.put(partition, new LagMetrics(lag, estimatedTimeMs));
        }

        return lagMap;
    }

    private long estimateTimeLag(TopicPartition partition, long lag) {
        // Calculate based on recent ingestion rate
        long messagesPerSecond = getRecentIngestionRate(partition);
        return messagesPerSecond > 0 ? (lag * 1000) / messagesPerSecond : 0;
    }
}
```

## Latency Requirements by Use Case

### Fraud Detection
**Target:** < 100ms end-to-end
**Reasoning:** Prevent fraudulent transaction before completion
**Challenges:**
- Complex ML model inference
- Multi-source data enrichment
- High accuracy requirements

**Architecture:**
```
Event → Kafka → Flink (streaming inference) → Redis (hot storage)
                    ↓
              ML Model Serving (< 10ms)
```

**Optimization:**
- Pre-compute features
- Cache user profiles
- Use simple models or approximate
- Fallback to rule-based if timeout

### Real-Time Dashboard
**Target:** 500ms - 2s query latency
**Reasoning:** Users expect interactive experience
**Challenges:**
- High concurrency
- Complex aggregations
- Fresh data requirements

**Architecture:**
```
Events → Kafka → Flink → ClickHouse/Druid → Dashboard API → Browser
                           ↓
                    Pre-aggregated views (materialized)
```

**Optimization:**
- Pre-aggregate common queries
- Use rollups and materialized views
- Cache frequent queries
- Limit time ranges

### Monitoring & Alerting
**Target:** 1-5 seconds
**Reasoning:** Detect issues before significant impact
**Challenges:**
- High data volume
- Complex detection logic
- False positive prevention

**Architecture:**
```
Metrics → Kafka → Flink (windowing + rules) → Alert Queue → Notification
                      ↓
                Time-series DB (Prometheus/InfluxDB)
```

**Optimization:**
- Stream processing for alerting
- Batch write to storage
- Sampling for high-cardinality metrics
- Intelligent alert throttling

### User Analytics
**Target:** 2-10 seconds
**Reasoning:** Analytics queries can tolerate some delay
**Challenges:**
- Complex queries
- Large datasets
- Historical + real-time data

**Architecture:**
```
Events → Kafka → Batch (Spark) → Data Warehouse (offline)
              → Stream (Flink) → OLAP (Pinot/Druid) (realtime)
                              → Unified query layer
```

**Optimization:**
- Hybrid architecture (Lambda/Kappa)
- Partition pruning
- Approximate algorithms for uniques
- Query result caching

### Operational Intelligence
**Target:** 5-30 seconds
**Reasoning:** Operations teams need near real-time visibility
**Challenges:**
- Multiple data sources
- Complex joins
- Variable query patterns

**Architecture:**
```
Logs → Kafka → Logstash/Fluentd → Elasticsearch
Metrics → Kafka → Telegraf → InfluxDB
Events → Kafka → Flink → ClickHouse
                      ↓
              Unified dashboard (Grafana)
```

**Optimization:**
- Separate pipelines by data type
- Index optimization
- Retention policies
- Query time-range limitations

## Latency Optimization Strategies

### 1. Data Ingestion

**Batching**
```java
// Batch configuration for Kafka producer
Properties props = new Properties();
props.put("batch.size", 32768);        // 32 KB batches
props.put("linger.ms", 10);            // Wait up to 10ms
props.put("compression.type", "lz4");  // Fast compression

// Trade-off: +10ms latency, 5x throughput improvement
```

**Partitioning**
```java
// Optimal partition count
int optimalPartitions = Math.max(
    targetThroughputMBps / partitionThroughputMBps,
    consumerParallelism
);

// Too few: Bottleneck
// Too many: Coordination overhead
```

### 2. Stream Processing

**Operator Chaining**
```java
// Flink operator chaining reduces network overhead
DataStream<Event> events = env.addSource(kafkaSource)
    .filter(e -> e.isValid())      // Chained
    .map(e -> e.transform())        // Chained
    .keyBy(e -> e.getUserId())
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .reduce((e1, e2) -> e1.merge(e2));

// Operators in same task = no serialization/network
```

**State Backend Optimization**
```java
// RocksDB for large state, faster than heap for > 1GB
env.setStateBackend(new EmbeddedRocksDBStateBackend());

// Heap state backend for small state, faster access
env.setStateBackend(new HashMapStateBackend());
```

**Checkpoint Configuration**
```java
// Checkpoints add latency but ensure fault tolerance
env.enableCheckpointing(60000);  // Every 60 seconds

// Reduce checkpoint overhead
CheckpointConfig config = env.getCheckpointConfig();
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(10000);
config.setMaxConcurrentCheckpoints(1);
```

### 3. Storage Layer

**Write Buffering**
```python
# ClickHouse async inserts
clickhouse_client.execute(
    "INSERT INTO events FORMAT JSONEachRow",
    data,
    settings={'async_insert': 1, 'wait_for_async_insert': 0}
)
# Trade-off: Lower latency, eventual consistency
```

**Partitioning Strategy**
```sql
-- Time-based partitioning for pruning
CREATE TABLE events (
    timestamp DateTime,
    user_id UInt64,
    event_type String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)  -- Daily partitions
ORDER BY (timestamp, user_id)
SETTINGS index_granularity = 8192;

-- Query only touches relevant partitions
SELECT * FROM events
WHERE timestamp >= '2025-01-15'
  AND timestamp < '2025-01-16';
```

**Indexing**
```sql
-- Druid inverted index for fast filtering
{
  "tableIndexConfig": {
    "invertedIndexColumns": ["user_id", "country", "device_type"]
  }
}

-- Trade-off: Faster queries, slower ingestion, more storage
```

### 4. Query Layer

**Pre-Aggregation**
```sql
-- Materialized view for common query
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, country, event_type)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    country,
    event_type,
    count() AS event_count,
    sum(revenue) AS total_revenue
FROM events
GROUP BY hour, country, event_type;

-- Query materialized view instead of raw events
SELECT * FROM hourly_stats
WHERE hour >= '2025-01-15 00:00:00';
```

**Result Caching**
```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def get_dashboard_data(time_bucket):
    """Cache dashboard queries for 1 minute"""
    return execute_query(time_bucket)

def cached_query(query_hash):
    time_bucket = int(time.time() / 60)  # 1-minute buckets
    return get_dashboard_data(time_bucket)
```

**Approximate Algorithms**
```sql
-- Druid HyperLogLog for unique counts
SELECT
    TIME_FLOOR(__time, 'PT1H') AS hour,
    APPROX_COUNT_DISTINCT_DS_HLL(user_id) AS unique_users
FROM events
GROUP BY 1;

-- Trade-off: ~2% error, 100x faster than exact count
```

### 5. Network Optimization

**Compression**
```java
// Kafka producer compression
props.put("compression.type", "lz4");  // Fast, good ratio

// Benchmark:
// None:     100 MB/s, 0ms latency
// LZ4:      500 MB/s, 2ms latency
// Snappy:   400 MB/s, 3ms latency
// GZIP:     800 MB/s, 15ms latency
```

**Batching**
```java
// Batch API calls
List<Future<Result>> futures = new ArrayList<>();
for (Query query : queries) {
    futures.add(executor.submit(() -> execute(query)));
}

// Collect results
List<Result> results = futures.stream()
    .map(f -> f.get())
    .collect(Collectors.toList());
```

## SLA Design

### Defining SLAs

**SLI (Service Level Indicator)**
```
Example: P95 query latency for dashboard API

Measurement:
- Record all query durations
- Calculate P95 over 5-minute windows
- Alert if P95 > threshold
```

**SLO (Service Level Objective)**
```
Target: P95 query latency < 1 second

Success Criteria:
- 99.9% of 5-minute windows meet target
- Allows for brief degradation
```

**SLA (Service Level Agreement)**
```
Commitment: 99.9% availability, P95 < 1s

Penalties:
- < 99.5%: 10% credit
- < 99.0%: 25% credit
- < 95.0%: 50% credit
```

### Latency Budgets

```
End-to-End Budget: 1000ms

Breakdown:
- Event generation:     50ms (5%)
- Network (producer):   20ms (2%)
- Kafka write:          30ms (3%)
- Stream processing:   200ms (20%)
- Network (consumer):   20ms (2%)
- Storage write:       180ms (18%)
- Query execution:     400ms (40%)
- Network (response):   50ms (5%)
- Client rendering:     50ms (5%)

Total: 1000ms
```

### Monitoring Implementation

```python
from prometheus_client import Histogram

# Define metrics
query_latency = Histogram(
    'query_duration_seconds',
    'Query latency',
    ['query_type'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

# Record latency
with query_latency.labels(query_type='dashboard').time():
    result = execute_query(query)

# Alert in Prometheus
# ALERT HighQueryLatency
#   IF histogram_quantile(0.95, query_duration_seconds) > 1
#   FOR 5m
#   LABELS {severity="warning"}
#   ANNOTATIONS {summary="High query latency detected"}
```

## Troubleshooting High Latency

### Diagnostic Checklist

**1. Identify the Stage**
```
Measure each component:
- Event generation
- Network
- Ingestion
- Processing
- Storage
- Query
```

**2. Check Resource Utilization**
```
Monitor:
- CPU usage
- Memory pressure
- Disk I/O
- Network bandwidth
- Queue depths
```

**3. Analyze Bottlenecks**
```
Look for:
- Consumer lag
- Long GC pauses
- Slow queries
- Lock contention
- Network saturation
```

### Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Consumer Lag** | Growing offset lag | Add consumers, optimize processing |
| **Hot Partition** | Uneven load | Improve partitioning key |
| **Slow Queries** | High query latency | Add indexes, optimize queries |
| **GC Pauses** | Periodic spikes | Tune JVM, reduce heap |
| **Network Saturation** | High bandwidth usage | Compression, batching |
| **Small Batches** | Low throughput | Increase batch size/linger |
| **Too Many Partitions** | High overhead | Consolidate partitions |

## Best Practices

1. **Measure Everything**: Instrument all stages
2. **Set Realistic SLOs**: Based on business requirements
3. **Budget Latency**: Allocate time to each component
4. **Optimize Sequentially**: Focus on biggest bottleneck
5. **Test at Scale**: Latency changes with volume
6. **Monitor Percentiles**: P95/P99 more important than average
7. **Trade-offs**: Understand latency vs throughput vs cost
8. **Graceful Degradation**: Fallback for high latency
9. **Alert on Trends**: Catch degradation early
10. **Regular Review**: SLOs should evolve with product

## References

- "Tail at Scale" - Jeff Dean (Google)
- "Designing Data-Intensive Applications" - Martin Kleppmann
- Site Reliability Engineering (Google)
- High Performance Browser Networking - Ilya Grigorik
