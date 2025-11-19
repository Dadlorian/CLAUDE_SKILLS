# Apache Flink Architecture & Concepts

## Overview

Apache Flink is a distributed stream processing framework designed for high-throughput, low-latency, and fault-tolerant data processing at scale.

## Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│         Client (Job Submission)          │
└──────────────────┬──────────────────────┘
                   │
           ┌───────▼────────┐
           │  JobManager    │
           │  (Master)      │
           │  - Scheduling  │
           │  - Checkpoints │
           │  - Recovery    │
           └────────┬───────┘
                    │
        ┌───────────┴───────────┐
        │                       │
   ┌────▼─────┐           ┌────▼─────┐
   │TaskManager│          │TaskManager│
   │(Worker 1) │          │(Worker 2) │
   │ - Slots   │          │ - Slots   │
   │ - Tasks   │          │ - Tasks   │
   │ - State   │          │ - State   │
   └───────────┘          └───────────┘
```

### JobManager
- **Resource Management**: Allocates resources to jobs
- **Scheduling**: Assigns tasks to TaskManagers
- **Checkpointing**: Coordinates distributed snapshots
- **Recovery**: Restores jobs from failures
- **High Availability**: Leader election via ZooKeeper/Kubernetes

### TaskManager
- **Task Execution**: Runs actual data processing
- **Task Slots**: Isolated execution environments
- **Network Buffers**: Inter-task communication
- **State Backend**: Manages operator state
- **Metrics**: Collects and reports performance data

### Deployment Modes

#### Standalone
```bash
# Start cluster
./bin/start-cluster.sh

# Submit job
./bin/flink run -c com.example.Job app.jar
```

#### YARN
```bash
# Session mode
./bin/yarn-session.sh -n 4 -tm 4096 -s 2

# Per-job mode
./bin/flink run -m yarn-cluster -yn 4 -ytm 4096 app.jar
```

#### Kubernetes
```yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: flink-analytics
spec:
  flinkVersion: v1_17
  jobManager:
    replicas: 1
    resource:
      memory: 2048m
      cpu: 1
  taskManager:
    replicas: 3
    resource:
      memory: 4096m
      cpu: 2
```

## Programming Model

### DataStream API

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// Source
DataStream<Event> events = env
    .addSource(new FlinkKafkaConsumer<>(
        "events",
        new EventDeserializationSchema(),
        kafkaProps
    ));

// Transform
DataStream<Tuple2<String, Long>> counts = events
    .filter(event -> event.isValid())
    .map(event -> Tuple2.of(event.getType(), 1L))
    .keyBy(tuple -> tuple.f0)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .sum(1);

// Sink
counts.addSink(new FlinkKafkaProducer<>(
    "results",
    new ResultSerializationSchema(),
    kafkaProps
));

env.execute("Event Counter");
```

### Table API & SQL

```java
StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

// Register Kafka table
tableEnv.executeSql(
    "CREATE TABLE events (" +
    "  event_time TIMESTAMP(3)," +
    "  user_id STRING," +
    "  event_type STRING," +
    "  revenue DECIMAL(10, 2)," +
    "  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND" +
    ") WITH (" +
    "  'connector' = 'kafka'," +
    "  'topic' = 'events'," +
    "  'properties.bootstrap.servers' = 'localhost:9092'," +
    "  'format' = 'json'" +
    ")"
);

// SQL query
Table result = tableEnv.sqlQuery(
    "SELECT " +
    "  TUMBLE_START(event_time, INTERVAL '1' HOUR) as window_start," +
    "  event_type," +
    "  COUNT(*) as event_count," +
    "  SUM(revenue) as total_revenue " +
    "FROM events " +
    "GROUP BY TUMBLE(event_time, INTERVAL '1' HOUR), event_type"
);

// Write to sink
tableEnv.executeSql(
    "INSERT INTO event_stats SELECT * FROM " + result
);
```

## Time & Watermarks

### Time Semantics

#### Event Time
```java
// Time when event actually occurred
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

DataStream<Event> events = source
    .assignTimestampsAndWatermarks(
        WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
            .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
    );
```

#### Processing Time
```java
// Time when event is processed by operator
env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

// Simpler, no watermarks needed, but non-deterministic
```

#### Ingestion Time
```java
// Time when event enters Flink
env.setStreamTimeCharacteristic(TimeCharacteristic.IngestionTime);

// Compromise between event time and processing time
```

### Watermarks

**Concept**: Mechanism to handle out-of-order events

```java
// Watermark strategies
WatermarkStrategy<Event> strategy = WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
    .withIdleness(Duration.ofMinutes(1))
    .withTimestampAssigner((event, timestamp) -> event.getTimestamp());

// Custom watermark generator
public class CustomWatermarkGenerator implements WatermarkGenerator<Event> {
    private long maxTimestamp = Long.MIN_VALUE;
    private long outOfOrdernessMillis = 5000;

    @Override
    public void onEvent(Event event, long eventTimestamp, WatermarkOutput output) {
        maxTimestamp = Math.max(maxTimestamp, eventTimestamp);
    }

    @Override
    public void onPeriodicEmit(WatermarkOutput output) {
        output.emitWatermark(new Watermark(maxTimestamp - outOfOrdernessMillis));
    }
}
```

## Windows

### Window Types

#### Tumbling Windows
```java
// Non-overlapping, fixed-size
events
    .keyBy(Event::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .reduce((e1, e2) -> e1.merge(e2));

// [00:00-00:05), [00:05-00:10), [00:10-00:15)
```

#### Sliding Windows
```java
// Overlapping windows
events
    .keyBy(Event::getUserId)
    .window(SlidingEventTimeWindows.of(
        Time.minutes(10),  // Window size
        Time.minutes(5)    // Slide interval
    ))
    .reduce((e1, e2) -> e1.merge(e2));

// [00:00-00:10), [00:05-00:15), [00:10-00:20)
```

#### Session Windows
```java
// Dynamic windows based on inactivity gap
events
    .keyBy(Event::getUserId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .reduce((e1, e2) -> e1.merge(e2));

// Window closes after 30 minutes of inactivity
```

#### Global Windows
```java
// Manual trigger control
events
    .keyBy(Event::getUserId)
    .window(GlobalWindows.create())
    .trigger(CountTrigger.of(1000))  // Trigger every 1000 events
    .reduce((e1, e2) -> e1.merge(e2));
```

### Window Functions

#### Reduce
```java
windowedStream.reduce((e1, e2) -> {
    e1.setCount(e1.getCount() + e2.getCount());
    e1.setRevenue(e1.getRevenue() + e2.getRevenue());
    return e1;
});
```

#### Aggregate
```java
windowedStream.aggregate(new AggregateFunction<Event, Accumulator, Result>() {
    @Override
    public Accumulator createAccumulator() {
        return new Accumulator();
    }

    @Override
    public Accumulator add(Event event, Accumulator acc) {
        acc.count++;
        acc.sum += event.getValue();
        return acc;
    }

    @Override
    public Result getResult(Accumulator acc) {
        return new Result(acc.count, acc.sum / acc.count);
    }

    @Override
    public Accumulator merge(Accumulator a, Accumulator b) {
        a.count += b.count;
        a.sum += b.sum;
        return a;
    }
});
```

#### Process
```java
windowedStream.process(new ProcessWindowFunction<Event, Result, String, TimeWindow>() {
    @Override
    public void process(
        String key,
        Context context,
        Iterable<Event> elements,
        Collector<Result> out
    ) {
        long count = 0;
        double sum = 0;

        for (Event event : elements) {
            count++;
            sum += event.getValue();
        }

        out.collect(new Result(
            key,
            context.window().getStart(),
            count,
            sum / count
        ));
    }
});
```

## State Management

### Keyed State

#### ValueState
```java
public class StatefulMapper extends RichMapFunction<Event, Result> {
    private transient ValueState<Long> countState;

    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor =
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public Result map(Event event) throws Exception {
        Long count = countState.value();
        count++;
        countState.update(count);
        return new Result(event.getUserId(), count);
    }
}
```

#### ListState
```java
private transient ListState<Event> recentEvents;

@Override
public void open(Configuration config) {
    ListStateDescriptor<Event> descriptor =
        new ListStateDescriptor<>("recent", Event.class);
    recentEvents = getRuntimeContext().getListState(descriptor);
}

@Override
public Result map(Event event) throws Exception {
    recentEvents.add(event);

    List<Event> events = new ArrayList<>();
    for (Event e : recentEvents.get()) {
        events.add(e);
    }

    // Keep only last 100 events
    if (events.size() > 100) {
        recentEvents.clear();
        recentEvents.addAll(events.subList(events.size() - 100, events.size()));
    }

    return process(events);
}
```

#### MapState
```java
private transient MapState<String, Long> productCounts;

@Override
public void open(Configuration config) {
    MapStateDescriptor<String, Long> descriptor =
        new MapStateDescriptor<>("products", String.class, Long.class);
    productCounts = getRuntimeContext().getMapState(descriptor);
}

@Override
public Result map(Event event) throws Exception {
    String product = event.getProductId();
    Long count = productCounts.get(product);
    if (count == null) {
        count = 0L;
    }
    productCounts.put(product, count + 1);

    return new Result(product, count + 1);
}
```

### State Backends

#### HashMapStateBackend
```java
// In-memory, heap-based (fast for small state)
env.setStateBackend(new HashMapStateBackend());
env.getCheckpointConfig().setCheckpointStorage("file:///checkpoint-dir");
```

#### EmbeddedRocksDBStateBackend
```java
// RocksDB, disk-based (scalable for large state)
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig().setCheckpointStorage("s3://checkpoint-bucket/");
```

### State TTL

```java
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.days(7))
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .cleanupFullSnapshot()
    .build();

ValueStateDescriptor<Long> descriptor =
    new ValueStateDescriptor<>("count", Long.class);
descriptor.enableTimeToLive(ttlConfig);
```

## Fault Tolerance

### Checkpointing

```java
// Enable checkpointing
env.enableCheckpointing(60000);  // Every 60 seconds

// Configure checkpoint behavior
CheckpointConfig config = env.getCheckpointConfig();
config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(600000);
config.setMaxConcurrentCheckpoints(1);
config.enableExternalizedCheckpoints(
    CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);

// Checkpoint storage
config.setCheckpointStorage("s3://my-bucket/checkpoints");
```

### Savepoints

```bash
# Trigger savepoint
flink savepoint <jobId> [targetDirectory]

# Cancel with savepoint
flink cancel -s [targetDirectory] <jobId>

# Restore from savepoint
flink run -s <savepointPath> app.jar
```

### Recovery

```
Job Failure:
1. Detect failure (heartbeat timeout)
2. Cancel all tasks
3. Restore from latest checkpoint
4. Resume from checkpoint state
5. Replay events from checkpoint offset
```

## Performance Optimization

### Parallelism

```java
// Set default parallelism
env.setParallelism(4);

// Set operator parallelism
stream
    .map(new MyMapper()).setParallelism(8)
    .keyBy(...)
    .window(...)
    .reduce(...).setParallelism(4);
```

### Operator Chaining

```java
// Enable chaining (default)
env.disableOperatorChaining();  // Disable globally

// Control chaining per operator
stream
    .map(new MyMapper()).startNewChain()  // Start new chain
    .filter(...).disableChaining();        // Disable for this operator
```

### Buffer Tuning

```java
// Network buffer configuration
taskmanager.network.memory.fraction: 0.1
taskmanager.network.memory.min: 64mb
taskmanager.network.memory.max: 1gb

// Latency vs throughput
env.setBufferTimeout(100);  // Flush buffers every 100ms
// Lower = lower latency, higher overhead
// Higher = higher throughput, higher latency
```

## Connectors

### Kafka

```java
// Source
FlinkKafkaConsumer<Event> kafkaSource = new FlinkKafkaConsumer<>(
    "events-topic",
    new EventDeserializationSchema(),
    kafkaProps
);
kafkaSource.setStartFromEarliest();
kafkaSource.setCommitOffsetsOnCheckpoints(true);

// Sink
FlinkKafkaProducer<Result> kafkaSink = new FlinkKafkaProducer<>(
    "results-topic",
    new ResultSerializationSchema(),
    kafkaProps,
    FlinkKafkaProducer.Semantic.EXACTLY_ONCE
);
```

### JDBC

```java
// Sink
JdbcSink.sink(
    "INSERT INTO events (id, type, timestamp) VALUES (?, ?, ?)",
    (statement, event) -> {
        statement.setLong(1, event.getId());
        statement.setString(2, event.getType());
        statement.setTimestamp(3, event.getTimestamp());
    },
    JdbcExecutionOptions.builder()
        .withBatchSize(1000)
        .withBatchIntervalMs(200)
        .withMaxRetries(3)
        .build(),
    new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        .withUrl("jdbc:postgresql://localhost:5432/db")
        .withDriverName("org.postgresql.Driver")
        .build()
);
```

### Elasticsearch

```java
// Sink
ElasticsearchSink<Event> esSink = new ElasticsearchSink.Builder<>(
    httpHosts,
    new ElasticsearchSinkFunction<Event>() {
        @Override
        public void process(Event event, RuntimeContext ctx, RequestIndexer indexer) {
            indexer.add(createIndexRequest(event));
        }
    }
).setBulkFlushMaxActions(1000)
 .setBulkFlushInterval(5000)
 .build();
```

## Best Practices

1. **Use Event Time**: For deterministic results
2. **Set Parallelism Appropriately**: Match data volume
3. **Enable Checkpointing**: For fault tolerance
4. **Use RocksDB for Large State**: Scalable state backend
5. **Configure Watermarks**: Handle out-of-order events
6. **Monitor Backpressure**: Indicates bottlenecks
7. **Use Operator Chaining**: Reduce network overhead
8. **State TTL**: Prevent unbounded state growth
9. **Tune Buffer Timeout**: Balance latency and throughput
10. **Test at Scale**: Validate performance under load

## Resources

- Official Docs: https://flink.apache.org/
- Flink Forward conferences
- "Stream Processing with Apache Flink" (O'Reilly)
- Ververica blog
