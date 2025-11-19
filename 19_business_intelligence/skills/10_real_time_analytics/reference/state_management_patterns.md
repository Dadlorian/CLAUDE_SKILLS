# State Management Patterns in Stream Processing

## Overview

State management is crucial for stateful stream processing operations like aggregations, joins, and sessionization. This document covers patterns, backends, and best practices.

## State Types

### Keyed State
State partitioned by key, accessible only within KeyedStream

```java
// Flink Keyed State
DataStream<Event> events = ...;

events
    .keyBy(Event::getUserId)
    .map(new StatefulMapper());  // Can access keyed state
```

### Operator State
State partitioned by parallel operator instance

```java
// Flink Operator State
public class StatefulSource implements SourceFunction<Event>,
                                       CheckpointedFunction {
    private transient ListState<Long> offsetState;

    @Override
    public void initializeState(FunctionInitializationContext context) {
        offsetState = context.getOperatorStateStore()
            .getListState(new ListStateDescriptor<>("offset", Long.class));
    }
}
```

### Broadcast State
State broadcasted to all parallel instances

```java
// Flink Broadcast State
MapStateDescriptor<String, Rule> ruleDescriptor =
    new MapStateDescriptor<>("rules", String.class, Rule.class);

BroadcastStream<Rule> ruleBroadcast = ruleStream
    .broadcast(ruleDescriptor);

DataStream<Alert> alerts = events
    .keyBy(Event::getUserId)
    .connect(ruleBroadcast)
    .process(new RuleEvaluator());
```

## State Backends

### In-Memory (HashMap)

**Flink**
```java
env.setStateBackend(new HashMapStateBackend());
env.getCheckpointConfig().setCheckpointStorage("file:///checkpoints");
```

**Characteristics:**
- Fastest access
- Limited by heap size
- Synchronous checkpoints
- Best for small state (< 1GB)

**Use When:**
- State size fits in memory
- Low latency critical
- Checkpoint time acceptable

### RocksDB (Disk-Based)

**Flink**
```java
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig().setCheckpointStorage("s3://bucket/checkpoints");
```

**Characteristics:**
- Unbounded state size
- Disk-based storage
- Asynchronous checkpoints
- Slower than memory
- Incremental checkpoints

**Use When:**
- Large state (> 1GB)
- Memory limited
- State > available heap

**Tuning:**
```java
RocksDBStateBackend backend = new EmbeddedRocksDBStateBackend(true);

// Block cache for read performance
backend.setDbStoragePath("/mnt/ssd/rocksdb");
backend.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED);

// Memory budget
backend.setWriteBufferManagerCapacity(512 * 1024 * 1024);  // 512 MB
```

### Spark State Store

**Spark Structured Streaming**
```scala
spark.conf.set("spark.sql.streaming.stateStore.providerClass",
  "org.apache.spark.sql.execution.streaming.state.HDFSBackedStateStoreProvider")

spark.conf.set("spark.sql.streaming.stateStore.maintenanceInterval", "60s")
```

**Characteristics:**
- HDFS-backed by default
- Versioned state
- Supports time travel
- Checkpoint integrated

## State Operations

### ValueState

**Single value per key**

```java
// Flink
public class CountMapper extends RichMapFunction<Event, Tuple2<String, Long>> {
    private transient ValueState<Long> countState;

    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor =
            new ValueStateDescriptor<>("count", Long.class, 0L);
        countState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public Tuple2<String, Long> map(Event event) throws Exception {
        Long count = countState.value();
        count++;
        countState.update(count);
        return new Tuple2<>(event.getUserId(), count);
    }
}
```

**Spark**
```scala
def updateState(
    key: String,
    newValues: Iterator[Event],
    state: GroupState[Long]
): Iterator[(String, Long)] = {

    val count = state.getOption.getOrElse(0L) + newValues.size
    state.update(count)
    Iterator((key, count))
}

events
    .groupByKey(_.userId)
    .mapGroupsWithState(GroupStateTimeout.NoTimeout)(updateState)
```

### ListState

**List of values per key**

```java
// Flink
public class EventCollector extends RichFlatMapFunction<Event, List<Event>> {
    private transient ListState<Event> eventListState;

    @Override
    public void open(Configuration config) {
        ListStateDescriptor<Event> descriptor =
            new ListStateDescriptor<>("events", Event.class);
        eventListState = getRuntimeContext().getListState(descriptor);
    }

    @Override
    public void flatMap(Event event, Collector<List<Event>> out) throws Exception {
        eventListState.add(event);

        List<Event> events = new ArrayList<>();
        for (Event e : eventListState.get()) {
            events.add(e);
        }

        // Emit if we have 100 events
        if (events.size() >= 100) {
            out.collect(events);
            eventListState.clear();
        }
    }
}
```

### MapState

**Key-value map per key**

```java
// Flink
public class ProductCounter extends RichMapFunction<Event, Map<String, Long>> {
    private transient MapState<String, Long> productCounts;

    @Override
    public void open(Configuration config) {
        MapStateDescriptor<String, Long> descriptor =
            new MapStateDescriptor<>("products", String.class, Long.class);
        productCounts = getRuntimeContext().getMapState(descriptor);
    }

    @Override
    public Map<String, Long> map(Event event) throws Exception {
        String product = event.getProductId();
        Long count = productCounts.get(product);
        if (count == null) {
            count = 0L;
        }
        productCounts.put(product, count + 1);

        // Return current state
        Map<String, Long> result = new HashMap<>();
        for (Map.Entry<String, Long> entry : productCounts.entries()) {
            result.put(entry.getKey(), entry.getValue());
        }
        return result;
    }
}
```

### AggregatingState

**Aggregate values efficiently**

```java
// Flink
public class AverageAggregator extends RichMapFunction<Event, Double> {
    private transient AggregatingState<Double, Double> avgState;

    @Override
    public void open(Configuration config) {
        AggregatingStateDescriptor<Double, Tuple2<Double, Long>, Double> descriptor =
            new AggregatingStateDescriptor<>(
                "average",
                new AverageAggregateFunction(),
                TypeInformation.of(new TypeHint<Tuple2<Double, Long>>() {})
            );
        avgState = getRuntimeContext().getAggregatingState(descriptor);
    }

    @Override
    public Double map(Event event) throws Exception {
        avgState.add(event.getValue());
        return avgState.get();
    }

    private static class AverageAggregateFunction
            implements AggregateFunction<Double, Tuple2<Double, Long>, Double> {

        @Override
        public Tuple2<Double, Long> createAccumulator() {
            return new Tuple2<>(0.0, 0L);
        }

        @Override
        public Tuple2<Double, Long> add(Double value, Tuple2<Double, Long> acc) {
            return new Tuple2<>(acc.f0 + value, acc.f1 + 1);
        }

        @Override
        public Double getResult(Tuple2<Double, Long> acc) {
            return acc.f1 == 0 ? 0.0 : acc.f0 / acc.f1;
        }

        @Override
        public Tuple2<Double, Long> merge(Tuple2<Double, Long> a, Tuple2<Double, Long> b) {
            return new Tuple2<>(a.f0 + b.f0, a.f1 + b.f1);
        }
    }
}
```

## State TTL (Time-To-Live)

### Configuration

**Flink**
```java
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.hours(24))
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .cleanupIncrementally(10, true)
    .cleanupInRocksdbCompactFilter(1000)
    .build();

ValueStateDescriptor<Long> descriptor =
    new ValueStateDescriptor<>("count", Long.class);
descriptor.enableTimeToLive(ttlConfig);
```

**Update Types:**
- `OnCreateAndWrite`: Reset TTL on create and write
- `OnReadAndWrite`: Reset TTL on any access
- `Disabled`: No automatic TTL update

**Visibility:**
- `ReturnExpiredIfNotCleanedUp`: Return expired values if not deleted yet
- `NeverReturnExpired`: Never return expired values

**Cleanup Strategies:**
- Incremental: Clean during state access
- RocksDB Compaction: Clean during compaction
- Full Snapshot: Clean during checkpoint

### Spark State Timeout

```scala
def updateWithTimeout(
    key: String,
    newValues: Iterator[Event],
    state: GroupState[UserSession]
): Iterator[SessionResult] = {

    // Set timeout
    state.setTimeoutDuration("1 hour")

    if (state.hasTimedOut) {
        // State timed out, emit final result
        val session = state.get
        state.remove()
        Iterator(SessionResult(key, session))
    } else {
        // Update state
        val session = state.getOption.getOrElse(UserSession.empty)
        newValues.foreach(event => session.addEvent(event))
        state.update(session)
        Iterator.empty
    }
}

events
    .groupByKey(_.userId)
    .flatMapGroupsWithState(
        OutputMode.Append,
        GroupStateTimeout.ProcessingTimeTimeout
    )(updateWithTimeout)
```

## State Patterns

### Window State

```java
// Flink: Collect events in window, emit aggregate
public class WindowAggregator
        extends ProcessWindowFunction<Event, Result, String, TimeWindow> {

    @Override
    public void process(
            String key,
            Context context,
            Iterable<Event> events,
            Collector<Result> out) {

        long count = 0;
        double sum = 0;

        for (Event event : events) {
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
}
```

### Session State

```scala
// Spark: Track user session
case class Session(
    startTime: Long,
    endTime: Long,
    events: List[Event]
)

def sessionize(
    userId: String,
    newEvents: Iterator[Event],
    state: GroupState[Session]
): Iterator[Session] = {

    val session = state.getOption.getOrElse(
        Session(Long.MaxValue, 0, List.empty)
    )

    val events = newEvents.toList
    if (events.isEmpty) {
        Iterator.empty
    } else {
        val newSession = Session(
            math.min(session.startTime, events.map(_.timestamp).min),
            math.max(session.endTime, events.map(_.timestamp).max),
            session.events ++ events
        )

        // Session ends after 30 min inactivity
        val now = System.currentTimeMillis()
        if (now - newSession.endTime > 30 * 60 * 1000) {
            state.remove()
            Iterator(newSession)
        } else {
            state.update(newSession)
            state.setTimeoutDuration("30 minutes")
            Iterator.empty
        }
    }
}
```

### Deduplication State

```java
// Flink: Dedup using state
public class Deduplicator extends KeyedProcessFunction<String, Event, Event> {
    private transient ValueState<Boolean> seenState;

    @Override
    public void open(Configuration parameters) {
        StateTtlConfig ttlConfig = StateTtlConfig
            .newBuilder(Time.hours(24))
            .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
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
        }
    }
}
```

### Join State

```java
// Flink: Stream-stream join with state
public class StreamJoiner
        extends KeyedCoProcessFunction<String, EventA, EventB, JoinedEvent> {

    private transient ValueState<EventA> eventAState;
    private transient ValueState<EventB> eventBState;

    @Override
    public void processElement1(EventA eventA, Context ctx, Collector<JoinedEvent> out)
            throws Exception {
        EventB eventB = eventBState.value();

        if (eventB != null) {
            // Both sides available, join and emit
            out.collect(new JoinedEvent(eventA, eventB));
            eventAState.clear();
            eventBState.clear();
        } else {
            // Store and wait for other side
            eventAState.update(eventA);
            // Set timer to cleanup if no match
            ctx.timerService().registerEventTimeTimer(
                eventA.getTimestamp() + 3600000  // 1 hour
            );
        }
    }

    @Override
    public void processElement2(EventB eventB, Context ctx, Collector<JoinedEvent> out)
            throws Exception {
        EventA eventA = eventAState.value();

        if (eventA != null) {
            out.collect(new JoinedEvent(eventA, eventB));
            eventAState.clear();
            eventBState.clear();
        } else {
            eventBState.update(eventB);
            ctx.timerService().registerEventTimeTimer(
                eventB.getTimestamp() + 3600000
            );
        }
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<JoinedEvent> out)
            throws Exception {
        // Cleanup unpaired events
        eventAState.clear();
        eventBState.clear();
    }
}
```

## State Monitoring

### Metrics

```java
// Flink state metrics
public class StateMonitor extends RichMapFunction<Event, Event> {
    private transient ValueState<Long> state;
    private transient Counter stateAccessCounter;
    private transient Histogram stateSizeHistogram;

    @Override
    public void open(Configuration config) {
        // Initialize state
        state = getRuntimeContext().getState(...);

        // Initialize metrics
        stateAccessCounter = getRuntimeContext()
            .getMetricGroup()
            .counter("state_accesses");

        stateSizeHistogram = getRuntimeContext()
            .getMetricGroup()
            .histogram("state_size",
                new DescriptiveStatisticsHistogram(1000));
    }

    @Override
    public Event map(Event event) throws Exception {
        stateAccessCounter.inc();

        Long value = state.value();
        state.update(value + 1);

        // Track state size
        stateSizeHistogram.update(estimateSize(value));

        return event;
    }
}
```

## Best Practices

### 1. Choose Appropriate State Backend
```
Small state (< 1GB): HashMapStateBackend
Large state (> 1GB): RocksDBStateBackend
Very large state: RocksDB with incremental checkpoints
```

### 2. Use State TTL
```java
// Prevent unbounded state growth
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.days(7))
    .cleanupIncrementally(10, true)
    .build();
```

### 3. Monitor State Size
```
Track metrics:
- State size per key
- Total state size
- Checkpoint duration
- Checkpoint size
```

### 4. Optimize Serialization
```java
// Use Kryo for better performance
env.getConfig().enableForceKryo();
env.getConfig().registerTypeWithKryoSerializer(
    MyClass.class,
    MyClassSerializer.class
);
```

### 5. Tune Checkpointing
```java
// Balance fault tolerance and performance
env.enableCheckpointing(60000);  // 1 minute
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(600000);
```

### 6. State Partitioning
```
Ensure good key distribution:
- Avoid hot keys
- Use composite keys if needed
- Monitor partition skew
```

## Troubleshooting

### OutOfMemoryError
```
Solutions:
1. Switch to RocksDB backend
2. Enable state TTL
3. Increase heap size
4. Reduce state retention
```

### Slow Checkpoints
```
Solutions:
1. Use incremental checkpoints (RocksDB)
2. Reduce checkpoint frequency
3. Increase checkpoint timeout
4. Use faster storage for checkpoints
```

### State Growth
```
Solutions:
1. Enable TTL
2. Implement custom cleanup logic
3. Use windowing to limit state
4. Monitor and alert on state size
```

## Resources

- Flink State Documentation
- Spark Structured Streaming State Management
- "Streaming Systems" by Tyler Akidau
- RocksDB Tuning Guide
