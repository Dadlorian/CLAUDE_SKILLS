# Performance Tuning for Real-Time Analytics

## Overview

This guide covers performance optimization techniques across the real-time analytics stack: ingestion, processing, storage, and querying.

## Kafka Performance Tuning

### Producer Optimization

#### Batching
```properties
# Increase batch size for higher throughput
batch.size=32768  # 32KB (default: 16384)
linger.ms=10      # Wait up to 10ms to fill batch

# Trade-off: Higher throughput vs higher latency
```

**Impact:**
- batch.size=16KB, linger.ms=0: 50k msg/sec, 20ms latency
- batch.size=32KB, linger.ms=10: 200k msg/sec, 30ms latency
- batch.size=128KB, linger.ms=50: 500k msg/sec, 70ms latency

#### Compression
```properties
# Enable compression
compression.type=lz4  # Options: none, gzip, snappy, lz4, zstd

# Benchmark (1KB messages):
# none:   100 MB/s, 0ms CPU
# lz4:    500 MB/s, 2ms CPU, 3x compression
# snappy: 400 MB/s, 3ms CPU, 2.5x compression
# gzip:   800 MB/s, 15ms CPU, 5x compression
# zstd:   900 MB/s, 10ms CPU, 6x compression
```

#### Buffer Memory
```properties
# Increase buffer for high-throughput scenarios
buffer.memory=67108864  # 64MB (default: 33554432)

# Avoid blocking on buffer full
max.block.ms=1000  # Fail fast if buffer full
```

#### Parallelism
```java
// Use async sends with callbacks
Future<RecordMetadata> future = producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        log.error("Send failed", exception);
        metrics.incrementCounter("send_failures");
    } else {
        metrics.recordLatency(System.currentTimeMillis() - record.timestamp());
    }
});

// Don't use synchronous sends (blocks!)
// RecordMetadata metadata = future.get();  // BAD
```

### Consumer Optimization

#### Fetch Size
```properties
# Increase fetch size for throughput
fetch.min.bytes=1048576    # 1MB (default: 1)
fetch.max.wait.ms=500      # Wait up to 500ms

# Larger batches
max.poll.records=1000      # (default: 500)
max.partition.fetch.bytes=10485760  # 10MB
```

#### Parallelism
```properties
# Match partition count for parallelism
# If topic has 12 partitions, use 12 consumers max

# Consumer group size
num.consumers=12

# Thread pool for processing
processing.threads=4  # Per consumer
```

#### Offset Management
```properties
# Auto-commit for simplicity (at-least-once)
enable.auto.commit=true
auto.commit.interval.ms=5000

# Manual commit for control (exactly-once)
enable.auto.commit=false

# Commit after processing batch
for (ConsumerRecord record : records) {
    process(record);
}
consumer.commitSync();  # Or commitAsync for performance
```

### Broker Optimization

#### Replication
```properties
# Balance durability vs performance
default.replication.factor=3  # More replicas = more overhead
min.insync.replicas=2         # Require 2 acks for durability
```

#### Log Segments
```properties
# Segment rolling
log.segment.bytes=1073741824  # 1GB
log.roll.hours=168            # 7 days

# Retention
log.retention.hours=168       # 7 days
log.retention.bytes=1099511627776  # 1TB per partition
```

#### Network Threads
```properties
# Scale network and IO threads
num.network.threads=8   # Handle requests
num.io.threads=16       # Handle disk I/O

# Replica fetcher threads
num.replica.fetchers=4
```

## Stream Processing Optimization

### Flink Tuning

#### Parallelism
```java
// Set appropriate parallelism
env.setParallelism(16);  // Match CPU cores

// Per-operator parallelism
stream
    .map(new Parser()).setParallelism(32)  // CPU-intensive
    .keyBy(...)
    .reduce(...).setParallelism(8);         // Less parallelism needed
```

#### Network Buffers
```yaml
# flink-conf.yaml
taskmanager.network.memory.fraction: 0.1
taskmanager.network.memory.min: 64mb
taskmanager.network.memory.max: 1gb

# Buffer timeout (latency vs throughput)
env.setBufferTimeout(100)  # 100ms
# Lower = lower latency, higher overhead
# Higher = higher throughput, higher latency
```

#### Checkpointing
```java
// Enable checkpointing
env.enableCheckpointing(60000);  // Every 60 seconds

// Optimize checkpoint configuration
CheckpointConfig config = env.getCheckpointConfig();
config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
config.setMinPauseBetweenCheckpoints(30000);  // Don't checkpoint too often
config.setCheckpointTimeout(600000);          // 10 minute timeout
config.setMaxConcurrentCheckpoints(1);        // One at a time

// Use incremental checkpoints (RocksDB only)
env.setStateBackend(new EmbeddedRocksDBStateBackend(true));
```

#### Operator Chaining
```java
// Enable chaining to reduce serialization
// Enabled by default

// Disable if memory is limited
env.disableOperatorChaining();

// Control per-operator
stream
    .map(...).startNewChain()     // Start new chain here
    .filter(...).disableChaining();  // Never chain
```

#### State Backend
```java
// For small state (< 1GB)
env.setStateBackend(new HashMapStateBackend());

// For large state (> 1GB)
EmbeddedRocksDBStateBackend rocksDB = new EmbeddedRocksDBStateBackend(true);
rocksDB.setDbStoragePath("/mnt/ssd/rocksdb");  // Use SSD
env.setStateBackend(rocksDB);

// RocksDB tuning
rocksDB.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED);
// or PredefinedOptions.SSD_OPTIMIZED
```

### Spark Streaming Tuning

#### Micro-Batch Size
```scala
// Trigger configuration
val query = df.writeStream
  .trigger(Trigger.ProcessingTime("5 seconds"))  // Larger batches
  // vs
  .trigger(Trigger.ProcessingTime("1 second"))   // Smaller batches

// Trade-off: Throughput vs Latency
// 5 seconds: Higher throughput, 5s latency
// 1 second: Lower latency, lower throughput
```

#### Shuffle Partitions
```scala
// Reduce shuffle partitions for streaming
spark.conf.set("spark.sql.shuffle.partitions", "100")
// Default: 200 (too high for streaming)

// Rule of thumb: 2-4x number of cores
// 100-200 MB per partition after shuffle
```

#### State Store
```scala
// Configure state store
spark.conf.set("spark.sql.streaming.stateStore.providerClass",
  "org.apache.spark.sql.execution.streaming.state.HDFSBackedStateStoreProvider")

// State cleanup interval
spark.conf.set("spark.sql.streaming.stateStore.maintenanceInterval", "60s")

// Number of versions to retain
spark.conf.set("spark.sql.streaming.minBatchesToRetain", "100")
```

#### Memory Management
```scala
// Executor memory allocation
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.memoryOverhead", "2g")

// Storage vs execution memory
spark.conf.set("spark.memory.fraction", "0.6")
spark.conf.set("spark.memory.storageFraction", "0.5")
```

## Database Performance

### ClickHouse Optimization

#### Table Design
```sql
-- Use appropriate ORDER BY
CREATE TABLE events (
    timestamp DateTime,
    user_id UInt64,
    event_type String,
    country String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, user_id)  -- Most filtered columns first
SETTINGS index_granularity = 8192;
```

#### Query Optimization
```sql
-- Use PREWHERE for filtering
SELECT user_id, event_type, revenue
FROM events
PREWHERE timestamp >= '2025-01-01'  -- Filter early
WHERE revenue > 100;

-- Use materialized views for aggregations
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
ORDER BY (hour, country)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    country,
    count() AS events,
    sum(revenue) AS total_revenue
FROM events
GROUP BY hour, country;
```

#### Server Configuration
```xml
<!-- config.xml -->
<max_threads>16</max_threads>
<max_memory_usage>20000000000</max_memory_usage>
<max_bytes_before_external_group_by>30000000000</max_bytes_before_external_group_by>

<!-- Merge configuration -->
<background_pool_size>32</background_pool_size>
<background_merge_pool_size>32</background_merge_pool_size>
```

### Druid Optimization

#### Segment Size
```json
{
  "tuningConfig": {
    "maxRowsPerSegment": 5000000,
    "maxRowsInMemory": 1000000,
    "maxTotalRows": 20000000
  }
}
```

**Guidelines:**
- 5-10 million rows per segment
- 300-700 MB compressed size
- Balance parallelism vs overhead

#### Rollup
```json
{
  "granularitySpec": {
    "rollup": true,
    "queryGranularity": "minute"
  }
}
```

**Impact:**
- Without rollup: 1B rows, 500GB
- With minute rollup: 100M rows, 50GB
- 10x reduction in storage and query time

#### Query Optimization
```json
{
  "queryType": "groupBy",
  "dataSource": "events",
  "filter": {
    "type": "and",
    "fields": [
      {"type": "selector", "dimension": "country", "value": "US"},
      {"type": "bound", "dimension": "revenue", "lower": "100"}
    ]
  },
  "aggregations": [
    {"type": "count", "name": "count"},
    {"type": "thetaSketch", "name": "unique_users", "fieldName": "user_id"}
  ],
  "context": {
    "useApproximateCountDistinct": true,
    "groupByIsSingleThreaded": false
  }
}
```

### Pinot Optimization

#### Indexing
```json
{
  "tableIndexConfig": {
    "invertedIndexColumns": ["user_id", "country"],
    "rangeIndexColumns": ["revenue", "timestamp"],
    "bloomFilterColumns": ["transaction_id"],
    "starTreeIndexConfigs": [{
      "dimensionsSplitOrder": ["country", "device_type"],
      "functionColumnPairs": ["SUM__revenue", "COUNT__*"],
      "maxLeafRecords": 10000
    }]
  }
}
```

#### Routing
```json
{
  "routing": {
    "instanceSelectorType": "replicaGroup"
  }
}
```

**Benefits:**
- Consistent routing improves cache hit rate
- Reduces network overhead
- Better query performance

## Query Optimization

### Partition Pruning
```sql
-- ClickHouse: Partition by date
WHERE timestamp >= '2025-01-15'
  AND timestamp < '2025-01-16'
-- Only scans relevant partitions

-- Druid: Time-based filtering
WHERE __time BETWEEN '2025-01-15' AND '2025-01-16'
```

### Predicate Pushdown
```scala
// Spark: Filter before join
val filtered = events.filter($"revenue" > 100)
val result = filtered.join(users, "user_id")

// vs inefficient
val result = events.join(users, "user_id").filter($"revenue" > 100)
```

### Column Pruning
```sql
-- Select only needed columns
SELECT user_id, revenue
FROM events
WHERE timestamp >= '2025-01-01';

-- Not SELECT *
```

### Approximate Algorithms
```sql
-- Druid: Use theta sketch for uniques
SELECT
    country,
    APPROX_COUNT_DISTINCT_DS_THETA(user_id) AS unique_users
FROM events
GROUP BY country;

-- 1000x faster than exact COUNT(DISTINCT)
-- ~2% error rate
```

## Network Optimization

### Data Locality
```
Colocate processing with data:
- Flink task managers near Kafka
- Query servers near storage
- Use local SSDs for state
```

### Compression
```properties
# Enable compression everywhere
kafka.compression.type=lz4
clickhouse.compression=lz4
network.compression=true
```

### Batching
```java
// Batch API calls
List<Event> batch = new ArrayList<>();
for (Event event : events) {
    batch.add(event);
    if (batch.size() >= 1000) {
        writeBatch(batch);
        batch.clear();
    }
}
```

## Resource Allocation

### CPU
```yaml
# Kubernetes resource requests/limits
resources:
  requests:
    cpu: "4"
    memory: "8Gi"
  limits:
    cpu: "8"
    memory: "16Gi"

# Rule of thumb:
# - CPU intensive (parsing): High CPU
# - Stateful processing: Balanced CPU/Memory
# - Large state: High memory
```

### Memory
```
JVM heap sizing:
- Heap: 70-80% of container memory
- Off-heap: 20-30% (network buffers, RocksDB)

Example for 16GB container:
- Xmx12g (heap)
- 4GB overhead (off-heap, OS)
```

### Disk I/O
```
Use SSDs for:
- RocksDB state backend
- ClickHouse data storage
- Checkpoint storage (if local)

Use HDDs for:
- Long-term checkpoint storage
- Cold data storage
```

## Monitoring & Profiling

### JVM Profiling
```bash
# Enable JMX
-Dcom.sun.management.jmxremote
-Dcom.sun.management.jmxremote.port=9010
-Dcom.sun.management.jmxremote.authenticate=false

# GC logging
-Xlog:gc*:file=gc.log:time,uptime:filecount=10,filesize=10M

# Flight Recorder
-XX:StartFlightRecording=duration=60s,filename=recording.jfr
```

### Flame Graphs
```bash
# Using async-profiler
./profiler.sh -d 60 -f /tmp/flamegraph.svg <pid>

# Analyze:
# - CPU hotspots
# - Serialization overhead
# - GC pressure
```

## Best Practices Checklist

- [ ] Right-size partitions (Kafka, processing)
- [ ] Enable compression (network, storage)
- [ ] Tune batch sizes (throughput vs latency)
- [ ] Configure checkpointing appropriately
- [ ] Use appropriate state backend
- [ ] Optimize data layout (partitioning, ordering)
- [ ] Add indexes selectively
- [ ] Use approximate algorithms where acceptable
- [ ] Monitor and alert on key metrics
- [ ] Profile regularly
- [ ] Test at production scale
- [ ] Document configuration decisions

## Resources

- Kafka Performance Tuning Guide
- Flink Performance Tuning
- ClickHouse Optimization Tips
- Druid Best Practices
