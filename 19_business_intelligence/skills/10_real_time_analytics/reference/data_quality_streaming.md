# Data Quality in Real-Time Streaming Systems

## Overview

Maintaining data quality in real-time streaming systems presents unique challenges compared to batch processing. This document covers validation, monitoring, and correction strategies.

## Data Quality Dimensions

### Completeness
- All required fields present
- No missing critical data
- Records arrive within expected timeframe

### Accuracy
- Data matches expected format
- Values within valid ranges
- Correct data types

### Consistency
- Data consistent across systems
- No conflicting values
- Referential integrity maintained

### Timeliness
- Data arrives within SLA
- No excessive lag
- Fresh enough for use case

### Uniqueness
- No duplicate events
- Proper deduplication
- Idempotent processing

### Validity
- Conforms to schema
- Passes business rules
- Meets constraints

## Validation Strategies

### Schema Validation

```python
from pyspark.sql.types import *

# Define strict schema
schema = StructType([
    StructField("event_id", StringType(), nullable=False),
    StructField("timestamp", TimestampType(), nullable=False),
    StructField("user_id", LongType(), nullable=False),
    StructField("event_type", StringType(), nullable=False),
    StructField("revenue", DoubleType(), nullable=True),
    StructField("metadata", MapType(StringType(), StringType()), nullable=True)
])

# Validate on read
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "events") \
    .load() \
    .select(from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*")

# Invalid records become null, filter them out
valid_events = df.filter(col("event_id").isNotNull())
invalid_events = df.filter(col("event_id").isNull())
```

### Business Rule Validation

```java
// Flink validation
public class EventValidator extends FilterFunction<Event> {
    @Override
    public boolean filter(Event event) {
        // Timestamp validation
        long now = System.currentTimeMillis();
        long eventTime = event.getTimestamp();
        if (eventTime > now || eventTime < now - 86400000) {
            logInvalid("Invalid timestamp", event);
            return false;
        }

        // Revenue validation
        if (event.getRevenue() != null && event.getRevenue() < 0) {
            logInvalid("Negative revenue", event);
            return false;
        }

        // Event type validation
        if (!VALID_EVENT_TYPES.contains(event.getEventType())) {
            logInvalid("Unknown event type", event);
            return false;
        }

        // User ID validation
        if (event.getUserId() == null || event.getUserId() <= 0) {
            logInvalid("Invalid user ID", event);
            return false;
        }

        return true;
    }

    private void logInvalid(String reason, Event event) {
        // Send to dead letter queue
        dlqProducer.send("invalid_events", new InvalidEvent(reason, event));
        metrics.incrementCounter("invalid_events", reason);
    }
}

DataStream<Event> validEvents = events.filter(new EventValidator());
```

### Range Validation

```scala
// Spark validation with constraints
val validated = events
  .withColumn("is_valid",
    $"timestamp".between(
      current_timestamp() - expr("INTERVAL 1 DAY"),
      current_timestamp()
    ) &&
    $"revenue".between(0, 100000) &&
    length($"event_id") === 36 &&  // UUID length
    $"user_id" > 0
  )

val valid = validated.filter($"is_valid" === true)
val invalid = validated.filter($"is_valid" === false)

// Write invalid to DLQ
invalid
  .withColumn("validation_error", lit("constraint_violation"))
  .withColumn("validation_timestamp", current_timestamp())
  .writeStream
  .format("kafka")
  .option("topic", "invalid_events")
  .start()
```

## Deduplication

### Event ID Based

```java
// Flink deduplication with state
public class DeduplicateFunction extends KeyedProcessFunction<String, Event, Event> {
    private transient ValueState<Boolean> seenState;

    @Override
    public void open(Configuration parameters) {
        StateTtlConfig ttlConfig = StateTtlConfig
            .newBuilder(Time.hours(24))
            .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
            .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
            .build();

        ValueStateDescriptor<Boolean> descriptor =
            new ValueStateDescriptor<>("seen", Boolean.class);
        descriptor.enableTimeToLive(ttlConfig);

        seenState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public void processElement(Event event, Context ctx, Collector<Event> out)
            throws Exception {
        Boolean seen = seenState.value();

        if (seen == null || !seen) {
            seenState.update(true);
            out.collect(event);
        } else {
            // Duplicate detected
            metrics.incrementCounter("duplicates");
        }
    }
}

DataStream<Event> deduplicated = events
    .keyBy(Event::getEventId)
    .process(new DeduplicateFunction());
```

### Window-Based Deduplication

```python
# Spark deduplication within time window
deduplicated = events \
    .withWatermark("timestamp", "1 hour") \
    .dropDuplicates(["event_id", "timestamp"])

# Or manual with groupBy
deduplicated = events \
    .groupBy("event_id", window("timestamp", "1 hour")) \
    .agg(first("*").alias("event")) \
    .select("event.*")
```

### Bloom Filter Deduplication

```java
// Approximate deduplication for high throughput
public class BloomFilterDeduplication extends RichMapFunction<Event, Event> {
    private transient BloomFilter<String> bloomFilter;

    @Override
    public void open(Configuration parameters) {
        bloomFilter = BloomFilter.create(
            Funnels.stringFunnel(Charset.defaultCharset()),
            10_000_000,  // Expected insertions
            0.01         // False positive rate
        );
    }

    @Override
    public Event map(Event event) {
        String eventId = event.getEventId();

        if (bloomFilter.mightContain(eventId)) {
            // Possible duplicate, check precisely
            if (checkInStateStore(eventId)) {
                return null;  // Confirmed duplicate
            }
        }

        bloomFilter.put(eventId);
        return event;
    }
}
```

## Data Completeness

### Missing Field Handling

```scala
// Fill missing values
val completed = events
  .na.fill(Map(
    "country" -> "UNKNOWN",
    "device_type" -> "UNKNOWN",
    "revenue" -> 0.0
  ))

// Or drop incomplete records
val complete = events
  .na.drop("any", Seq("user_id", "timestamp", "event_type"))
```

### Late Data Handling

```java
// Flink late data sideoutput
OutputTag<Event> lateDataTag = new OutputTag<Event>("late-data"){};

SingleOutputStreamOperator<Result> results = events
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofMinutes(5))
            .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
    )
    .keyBy(Event::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .sideOutputLateData(lateDataTag)
    .reduce((e1, e2) -> e1.merge(e2));

// Process late data separately
DataStream<Event> lateData = results.getSideOutput(lateDataTag);
lateData.addSink(new LateDataSink());
```

## Data Accuracy

### Type Coercion

```python
from pyspark.sql.functions import col, when

# Safe type conversion with defaults
cleaned = events \
    .withColumn("revenue",
        when(col("revenue").cast("double").isNotNull(),
             col("revenue").cast("double"))
        .otherwise(0.0)
    ) \
    .withColumn("quantity",
        when(col("quantity").cast("int").isNotNull(),
             col("quantity").cast("int"))
        .otherwise(1)
    )
```

### Outlier Detection

```scala
// Statistical outlier detection
val stats = events
  .agg(
    avg("revenue").as("mean"),
    stddev("revenue").as("stddev")
  )
  .collect()(0)

val mean = stats.getAs[Double]("mean")
val stddev = stats.getAs[Double]("stddev")
val threshold = 3.0  // 3 standard deviations

val filtered = events
  .filter(abs($"revenue" - mean) <= threshold * stddev)

val outliers = events
  .filter(abs($"revenue" - mean) > threshold * stddev)
  .withColumn("outlier_type", lit("statistical"))
```

### Reference Data Validation

```java
// Validate against reference data
public class ReferenceDataValidator extends RichMapFunction<Event, Event> {
    private transient MapState<String, Country> countryMap;

    @Override
    public void open(Configuration parameters) throws Exception {
        // Load reference data
        MapStateDescriptor<String, Country> descriptor =
            new MapStateDescriptor<>("countries", String.class, Country.class);
        countryMap = getRuntimeContext().getMapState(descriptor);

        // Initialize with reference data
        loadCountries().forEach((code, country) -> {
            try {
                countryMap.put(code, country);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Override
    public Event map(Event event) throws Exception {
        String countryCode = event.getCountryCode();

        if (!countryMap.contains(countryCode)) {
            event.setCountryCode("UNKNOWN");
            event.setValidationWarning("Invalid country code");
        }

        return event;
    }
}
```

## Data Consistency

### Cross-Stream Consistency

```scala
// Ensure consistency across multiple streams
val userEvents = spark.readStream...
val userProfiles = spark.readStream...

// Join to check consistency
val inconsistent = userEvents
  .join(userProfiles, "user_id")
  .filter($"events.country" =!= $"profiles.country")

inconsistent
  .writeStream
  .foreachBatch { (batch, batchId) =>
    // Log inconsistencies
    batch.foreach { row =>
      logger.warn(s"Inconsistent country for user ${row.getAs[String]("user_id")}")
    }

    // Optionally trigger reconciliation
    reconciliationService.reconcile(batch)
  }
  .start()
```

### Referential Integrity

```java
// Ensure foreign key exists
public class ForeignKeyValidator extends KeyedCoProcessFunction<String, Event, User, Event> {
    private transient ValueState<User> userState;

    @Override
    public void processElement1(Event event, Context ctx, Collector<Event> out) {
        User user = userState.value();

        if (user == null) {
            // User not found, wait for user data or reject
            ctx.timerService().registerEventTimeTimer(
                event.getTimestamp() + 60000  // Wait 1 minute
            );
        } else {
            out.collect(event);
        }
    }

    @Override
    public void processElement2(User user, Context ctx, Collector<Event> out) {
        userState.update(user);
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Event> out) {
        if (userState.value() == null) {
            // User still not found after timeout
            metrics.incrementCounter("missing_user_reference");
        }
    }
}
```

## Monitoring & Alerting

### Quality Metrics

```python
# Calculate quality metrics
from pyspark.sql.functions import *

quality_metrics = events \
    .withColumn("has_required_fields",
        when(
            col("user_id").isNotNull() &
            col("timestamp").isNotNull() &
            col("event_type").isNotNull(),
            1
        ).otherwise(0)
    ) \
    .withColumn("is_timely",
        when(
            col("timestamp") >= current_timestamp() - expr("INTERVAL 5 MINUTES"),
            1
        ).otherwise(0)
    ) \
    .withColumn("is_valid_type",
        when(col("event_type").isin(valid_types), 1).otherwise(0)
    ) \
    .groupBy(window("timestamp", "1 minute")) \
    .agg(
        count("*").alias("total_events"),
        sum("has_required_fields").alias("complete_events"),
        sum("is_timely").alias("timely_events"),
        sum("is_valid_type").alias("valid_type_events"),
        (sum("has_required_fields") / count("*") * 100).alias("completeness_pct"),
        (sum("is_timely") / count("*") * 100).alias("timeliness_pct"),
        (sum("is_valid_type") / count("*") * 100).alias("validity_pct")
    )

# Alert on quality degradation
def alert_on_quality(batch_df, batch_id):
    metrics = batch_df.collect()
    for metric in metrics:
        if metric.completeness_pct < 95:
            send_alert(f"Low completeness: {metric.completeness_pct}%")
        if metric.timeliness_pct < 90:
            send_alert(f"Low timeliness: {metric.timeliness_pct}%")

quality_metrics \
    .writeStream \
    .foreachBatch(alert_on_quality) \
    .start()
```

### Data Profiling

```java
// Real-time data profiling
public class DataProfiler extends ProcessWindowFunction<Event, Profile, String, TimeWindow> {
    @Override
    public void process(
        String key,
        Context context,
        Iterable<Event> events,
        Collector<Profile> out
    ) {
        Profile profile = new Profile();

        for (Event event : events) {
            profile.incrementCount();
            profile.updateMin(event.getRevenue());
            profile.updateMax(event.getRevenue());
            profile.addToSum(event.getRevenue());
            profile.trackCardinality(event.getUserId());
            profile.trackNulls(event);
        }

        profile.calculateStats();
        out.collect(profile);

        // Alert on anomalies
        if (profile.getNullPercentage() > 10) {
            alerting.send("High null percentage: " + profile.getNullPercentage());
        }
        if (profile.getCardinality() < 100) {
            alerting.send("Low cardinality: " + profile.getCardinality());
        }
    }
}
```

## Correction Strategies

### Automated Correction

```scala
// Auto-correct common issues
val corrected = events
  .withColumn("country",
    when(length($"country") =!= 2, "US")  // Default to US
    .otherwise(upper($"country"))
  )
  .withColumn("email",
    lower(trim($"email"))
  )
  .withColumn("revenue",
    when($"revenue" < 0, 0)
    .when($"revenue" > 1000000, 1000000)  // Cap at 1M
    .otherwise($"revenue")
  )
  .withColumn("timestamp",
    when($"timestamp" > current_timestamp(), current_timestamp())
    .otherwise($"timestamp")
  )
```

### Manual Review Queue

```java
// Send suspicious events for manual review
public class ReviewQueueRouter extends ProcessFunction<Event, Event> {
    private final OutputTag<Event> reviewQueueTag = new OutputTag<Event>("review"){};

    @Override
    public void processElement(Event event, Context ctx, Collector<Event> out) {
        double suspicionScore = calculateSuspicionScore(event);

        if (suspicionScore > 0.8) {
            // High suspicion, route to review queue
            ctx.output(reviewQueueTag, event);
        } else if (suspicionScore > 0.5) {
            // Medium suspicion, flag but process
            event.setNeedsReview(true);
            out.collect(event);
        } else {
            // Low suspicion, process normally
            out.collect(event);
        }
    }

    private double calculateSuspicionScore(Event event) {
        double score = 0.0;

        // Check multiple factors
        if (event.getRevenue() > 10000) score += 0.3;
        if (event.getCountry() == null) score += 0.2;
        if (isWeekend(event.getTimestamp())) score += 0.1;
        if (event.getSessionDuration() < 10) score += 0.2;

        return Math.min(score, 1.0);
    }
}
```

## Dead Letter Queue

### DLQ Implementation

```python
# Comprehensive DLQ handling
valid_events = events.filter(
    col("user_id").isNotNull() &
    col("timestamp").isNotNull() &
    col("event_type").isin(valid_types)
)

invalid_events = events.filter(
    col("user_id").isNull() |
    col("timestamp").isNull() |
    ~col("event_type").isin(valid_types)
).withColumn("error_reason",
    when(col("user_id").isNull(), "missing_user_id")
    .when(col("timestamp").isNull(), "missing_timestamp")
    .when(~col("event_type").isin(valid_types), "invalid_event_type")
    .otherwise("unknown")
).withColumn("dlq_timestamp", current_timestamp())

# Write to DLQ
invalid_events \
    .writeStream \
    .format("kafka") \
    .option("topic", "dead_letter_queue") \
    .option("checkpointLocation", "/checkpoint/dlq") \
    .start()

# DLQ monitoring and reprocessing
dlq_events = spark \
    .readStream \
    .format("kafka") \
    .option("subscribe", "dead_letter_queue") \
    .load()

# Periodic DLQ analysis
dlq_stats = dlq_events \
    .groupBy("error_reason") \
    .count() \
    .writeStream \
    .format("console") \
    .outputMode("complete") \
    .start()
```

## Best Practices

1. **Fail Fast**: Validate early in the pipeline
2. **Monitor Continuously**: Track quality metrics in real-time
3. **DLQ Everything**: Never drop data silently
4. **Schema Evolution**: Plan for schema changes
5. **Idempotent Operations**: Handle reprocessing
6. **Comprehensive Logging**: Track all quality issues
7. **Alert Proactively**: Don't wait for catastrophic failure
8. **Test with Bad Data**: Validate error handling
9. **Document Assumptions**: Make expectations explicit
10. **Regular Audits**: Periodic quality reviews

## Tools & Frameworks

- **Great Expectations**: Data validation framework
- **Deequ**: AWS data quality library for Spark
- **Apache Griffin**: Data quality solution
- **Soda**: Data quality monitoring
- **Monte Carlo**: Data observability platform

## Resources

- "Data Quality: The Accuracy Dimension" - Loshin
- AWS Deequ GitHub
- Great Expectations documentation
- Data Quality patterns (Martin Fowler)
