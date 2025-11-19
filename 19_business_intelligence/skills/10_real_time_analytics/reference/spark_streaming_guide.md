# Spark Structured Streaming Guide

## Overview

Spark Structured Streaming is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine, providing unified batch and streaming analytics with high-level DataFrame/Dataset APIs.

## Core Concepts

### Micro-Batch Processing

```
Continuous Stream → Micro-batches → Processing → Output

Stream: [e1, e2, e3, e4, e5, e6, e7, e8, e9, ...]
         └─batch1─┘  └─batch2─┘  └─batch3─┘

Each micro-batch processed as a static DataFrame
```

### Continuous Processing (Experimental)

```
Stream → Continuous Processing → Output

Low latency (~1ms) vs micro-batch (100ms+)
Limited feature support
```

## Programming Model

### Basic Structure

```scala
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

val spark = SparkSession.builder()
  .appName("StructuredStreaming")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

// Read from Kafka
val df = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("subscribe", "events")
  .load()

// Parse JSON
val events = df
  .selectExpr("CAST(value AS STRING)")
  .select(from_json($"value", schema).as("data"))
  .select("data.*")

// Transform
val results = events
  .filter($"event_type" === "purchase")
  .groupBy(window($"timestamp", "5 minutes"), $"country")
  .agg(
    count("*").as("event_count"),
    sum("revenue").as("total_revenue"),
    approx_count_distinct("user_id").as("unique_users")
  )

// Write to sink
val query = results
  .writeStream
  .outputMode("update")
  .format("console")
  .start()

query.awaitTermination()
```

### Python API

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("StructuredStreaming") \
    .getOrCreate()

# Define schema
schema = StructType([
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("revenue", DoubleType())
])

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "events") \
    .load()

# Parse and transform
events = df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Aggregation
results = events \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window("timestamp", "5 minutes"),
        "event_type"
    ) \
    .agg(
        count("*").alias("count"),
        sum("revenue").alias("total_revenue")
    )

# Write to sink
query = results \
    .writeStream \
    .outputMode("update") \
    .format("console") \
    .start()

query.awaitTermination()
```

## Sources

### Kafka Source

```scala
val kafkaDF = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
  .option("subscribe", "topic1,topic2,topic3")  // Multiple topics
  .option("startingOffsets", "earliest")        // or "latest"
  .option("maxOffsetsPerTrigger", 10000)        // Rate limiting
  .option("failOnDataLoss", "false")            // Handle topic deletion
  .load()

// Kafka message schema
// key: binary
// value: binary
// topic: string
// partition: int
// offset: long
// timestamp: timestamp
// timestampType: int
```

### File Source

```scala
// JSON files
val jsonDF = spark
  .readStream
  .schema(schema)
  .json("path/to/json/files")

// CSV files
val csvDF = spark
  .readStream
  .schema(schema)
  .option("header", "true")
  .csv("path/to/csv/files")

// Parquet files
val parquetDF = spark
  .readStream
  .schema(schema)
  .parquet("path/to/parquet/files")
```

### Socket Source (Testing Only)

```scala
val socketDF = spark
  .readStream
  .format("socket")
  .option("host", "localhost")
  .option("port", 9999)
  .load()
```

### Rate Source (Testing Only)

```scala
val rateDF = spark
  .readStream
  .format("rate")
  .option("rowsPerSecond", 100)
  .option("numPartitions", 10)
  .load()
```

## Transformations

### Stateless Operations

```scala
// Select, filter, map
val filtered = events
  .select("user_id", "event_type", "revenue")
  .filter($"revenue" > 100)
  .withColumn("revenue_usd", $"revenue" * 1.2)

// Joins with static data
val userProfiles = spark.read.parquet("users")
val enriched = events.join(userProfiles, "user_id")

// UDFs
val categorize = udf((revenue: Double) => {
  if (revenue > 1000) "high"
  else if (revenue > 100) "medium"
  else "low"
})

val categorized = events.withColumn("category", categorize($"revenue"))
```

### Aggregations

```scala
// Simple aggregation
val counts = events
  .groupBy("event_type")
  .count()

// Multiple aggregations
val stats = events
  .groupBy("country", "device_type")
  .agg(
    count("*").as("event_count"),
    sum("revenue").as("total_revenue"),
    avg("session_duration").as("avg_duration"),
    min("timestamp").as("first_seen"),
    max("timestamp").as("last_seen"),
    approx_count_distinct("user_id").as("unique_users")
  )

// Custom aggregations
import org.apache.spark.sql.expressions.Aggregator

case class EventStats(count: Long, sum: Double, max: Double)

val customAgg = new Aggregator[Event, EventStats, EventStats] {
  def zero: EventStats = EventStats(0, 0.0, 0.0)

  def reduce(buffer: EventStats, event: Event): EventStats = {
    EventStats(
      buffer.count + 1,
      buffer.sum + event.revenue,
      Math.max(buffer.max, event.revenue)
    )
  }

  def merge(b1: EventStats, b2: EventStats): EventStats = {
    EventStats(
      b1.count + b2.count,
      b1.sum + b2.sum,
      Math.max(b1.max, b2.max)
    )
  }

  def finish(buffer: EventStats): EventStats = buffer

  def bufferEncoder: Encoder[EventStats] = Encoders.product
  def outputEncoder: Encoder[EventStats] = Encoders.product
}

val results = events.groupBy("country").agg(customAgg.toColumn)
```

## Windowing

### Tumbling Windows

```scala
// 5-minute non-overlapping windows
val windowed = events
  .groupBy(window($"timestamp", "5 minutes"))
  .agg(count("*").as("event_count"))

// Output includes window start/end
// window: {start: timestamp, end: timestamp}
// event_count: long
```

### Sliding Windows

```scala
// 10-minute windows, sliding every 5 minutes
val sliding = events
  .groupBy(window($"timestamp", "10 minutes", "5 minutes"))
  .agg(count("*").as("event_count"))

// Windows: [00:00-00:10), [00:05-00:15), [00:10-00:20), ...
```

### Session Windows

```scala
// Session windows using session_window (Spark 3.2+)
val sessions = events
  .groupBy(
    $"user_id",
    session_window($"timestamp", "30 minutes")
  )
  .agg(
    count("*").as("event_count"),
    collect_list("event_type").as("events")
  )
```

## Watermarks & Late Data

### Watermarking

```scala
val withWatermark = events
  .withWatermark("timestamp", "10 minutes")
  .groupBy(
    window($"timestamp", "5 minutes"),
    $"event_type"
  )
  .count()

// Watermark = max_event_time - 10 minutes
// Events older than watermark are dropped
// State cleaned up after watermark passes window end
```

### Late Data Handling

```python
# Allow 10 minutes of late data
events_with_watermark = events \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(window("timestamp", "5 minutes")) \
    .count()

# Late data behavior:
# - Events within watermark: Included in window
# - Events beyond watermark: Dropped
# - Windows closed after watermark passes end time
```

## Joins

### Stream-Stream Joins

```scala
// Inner join with time constraints
val impressions = spark.readStream...
val clicks = spark.readStream...

val joined = impressions
  .withWatermark("impression_time", "10 minutes")
  .join(
    clicks.withWatermark("click_time", "10 minutes"),
    expr("""
      impression_id = click_id AND
      click_time >= impression_time AND
      click_time <= impression_time + interval 1 hour
    """)
  )
```

### Stream-Static Joins

```scala
// Join stream with static reference data
val events = spark.readStream...
val users = spark.read.parquet("users")

val enriched = events.join(users, "user_id")

// Static data can be broadcast for efficiency
val enriched = events.join(broadcast(users), "user_id")
```

### Multiple Stream Joins

```scala
val pageViews = spark.readStream...
val clicks = spark.readStream...
val purchases = spark.readStream...

val funnel = pageViews
  .withWatermark("view_time", "1 hour")
  .join(
    clicks.withWatermark("click_time", "1 hour"),
    expr("view_id = click_view_id AND click_time >= view_time")
  )
  .join(
    purchases.withWatermark("purchase_time", "1 hour"),
    expr("click_id = purchase_click_id AND purchase_time >= click_time")
  )
```

## Output Modes

### Append Mode

```scala
// Only new rows since last trigger
// Requires watermark for aggregations
val query = results
  .writeStream
  .outputMode("append")
  .format("parquet")
  .option("path", "output")
  .start()

// Use case: Immutable event log, file output
```

### Update Mode

```scala
// Updated rows since last trigger
// Not supported for sorting
val query = results
  .writeStream
  .outputMode("update")
  .format("kafka")
  .start()

// Use case: Updating dashboard, Kafka output
```

### Complete Mode

```scala
// Entire result table every trigger
// Requires aggregation
val query = results
  .writeStream
  .outputMode("complete")
  .format("console")
  .start()

// Use case: Small result sets, in-memory tables
```

## Sinks

### Kafka Sink

```scala
val query = results
  .selectExpr("CAST(key AS STRING)", "to_json(struct(*)) AS value")
  .writeStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("topic", "results")
  .option("checkpointLocation", "/tmp/checkpoint")
  .start()
```

### File Sink

```scala
// Parquet
val query = results
  .writeStream
  .format("parquet")
  .option("path", "output/parquet")
  .option("checkpointLocation", "/tmp/checkpoint")
  .partitionBy("country", "date")
  .start()

// JSON
val query = results
  .writeStream
  .format("json")
  .option("path", "output/json")
  .option("checkpointLocation", "/tmp/checkpoint")
  .start()
```

### Console Sink (Debugging)

```scala
val query = results
  .writeStream
  .outputMode("update")
  .format("console")
  .option("numRows", 100)
  .option("truncate", false)
  .start()
```

### Foreach Sink (Custom)

```scala
import org.apache.spark.sql.ForeachWriter

val writer = new ForeachWriter[Row] {
  def open(partitionId: Long, version: Long): Boolean = {
    // Initialize connection
    true
  }

  def process(row: Row): Unit = {
    // Process each row
    println(s"Processing: ${row}")
  }

  def close(errorOrNull: Throwable): Unit = {
    // Close connection
  }
}

val query = results
  .writeStream
  .foreach(writer)
  .start()
```

### ForeachBatch Sink

```scala
val query = results
  .writeStream
  .foreachBatch { (batchDF: DataFrame, batchId: Long) =>
    // Custom batch processing
    batchDF.write
      .mode("append")
      .jdbc(jdbcUrl, "table", jdbcProps)

    // Can write to multiple sinks
    batchDF.write.parquet(s"backup/$batchId")
  }
  .start()
```

## Checkpointing & Fault Tolerance

### Checkpoint Configuration

```scala
val query = results
  .writeStream
  .format("parquet")
  .option("path", "output")
  .option("checkpointLocation", "checkpoint")
  .start()

// Checkpoint stores:
// - Offset ranges processed
// - State store data
// - Configuration metadata
```

### Exactly-Once Semantics

```
Source → Processing → Sink

Kafka → Structured Streaming → Kafka/Files
  ↓           ↓                    ↓
Offsets   Stateful Ops         Idempotent writes

Requirements:
1. Replayable source (Kafka)
2. Checkpoint enabled
3. Idempotent sink
```

## Performance Optimization

### Trigger Configuration

```scala
import org.apache.spark.sql.streaming.Trigger

// Process every second
.trigger(Trigger.ProcessingTime("1 second"))

// Process once (batch mode)
.trigger(Trigger.Once())

// Process immediately (continuous)
.trigger(Trigger.Continuous("1 second"))

// Process when data available (default)
.trigger(Trigger.AvailableNow())
```

### Partition Tuning

```scala
// Repartition for better parallelism
val repartitioned = events
  .repartition(100, $"user_id")
  .groupBy("user_id")
  .count()

// Coalesce to reduce partitions
val coalesced = results.coalesce(10)
```

### Caching

```scala
// Cache for multiple aggregations
val cached = events.cache()

val counts = cached.groupBy("country").count()
val revenue = cached.groupBy("country").sum("revenue")
```

### State Store Tuning

```scala
// Configure state store
spark.conf.set("spark.sql.streaming.stateStore.providerClass",
  "org.apache.spark.sql.execution.streaming.state.HDFSBackedStateStoreProvider")

// State cleanup
spark.conf.set("spark.sql.streaming.stateStore.maintenanceInterval", "60s")
```

## Monitoring

### Query Progress

```scala
val query = results.writeStream...start()

// Get latest progress
val progress = query.lastProgress
println(s"Input rows: ${progress.numInputRows}")
println(s"Batch ID: ${progress.batchId}")
println(s"Duration: ${progress.durationMs}")

// Listen to progress
query.addStreamingQueryListener(new StreamingQueryListener {
  override def onQueryStarted(event: QueryStartedEvent): Unit = {
    println(s"Query started: ${event.id}")
  }

  override def onQueryProgress(event: QueryProgressEvent): Unit = {
    println(s"Progress: ${event.progress}")
  }

  override def onQueryTerminated(event: QueryTerminatedEvent): Unit = {
    println(s"Query terminated: ${event.id}")
  }
})
```

### Metrics

```scala
val metrics = query.recentProgress.map { p =>
  Map(
    "batchId" -> p.batchId,
    "inputRowsPerSecond" -> p.inputRowsPerSecond,
    "processedRowsPerSecond" -> p.processedRowsPerSecond,
    "durationMs" -> p.durationMs.get("triggerExecution"),
    "stateMemoryUsed" -> p.stateOperators.map(_.memoryUsedBytes).sum
  )
}
```

## Best Practices

1. **Always Set Checkpoint**: Required for fault tolerance
2. **Use Watermarks**: For aggregations and joins
3. **Choose Appropriate Output Mode**: Based on use case
4. **Monitor State Size**: Prevent unbounded growth
5. **Tune Trigger Interval**: Balance latency and throughput
6. **Partition Appropriately**: Match parallelism to data
7. **Use Broadcast Joins**: For small static data
8. **Test at Scale**: Validate performance with production data
9. **Handle Late Data**: Configure watermark appropriately
10. **Version Checkpoints**: Checkpoint format changes between versions

## Common Patterns

### Deduplication

```scala
val deduplicated = events
  .withWatermark("timestamp", "1 hour")
  .dropDuplicates("event_id", "timestamp")
```

### Sessionization

```scala
val sessions = events
  .withWatermark("timestamp", "30 minutes")
  .groupBy($"user_id", session_window($"timestamp", "30 minutes"))
  .agg(
    collect_list("page").as("pages_visited"),
    sum("revenue").as("session_revenue")
  )
```

### Change Data Capture

```scala
val changes = events
  .groupBy($"user_id")
  .agg(
    last("profile").as("current_profile"),
    collect_list(struct("timestamp", "profile")).as("history")
  )
```

## Resources

- Official Docs: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- "Spark: The Definitive Guide" (O'Reilly)
- Databricks blog
- Spark Summit videos
