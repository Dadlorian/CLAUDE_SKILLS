# Flink Stateful Stream Processing Guide

## State Types

### ValueState
```java
private transient ValueState<Long> countState;

@Override
public void open(Configuration config) {
    ValueStateDescriptor<Long> descriptor = 
        new ValueStateDescriptor<>("count", Long.class);
    countState = getRuntimeContext().getState(descriptor);
}
```

### ListState
```java
private transient ListState<Event> eventList;

eventList.add(event);
for (Event e : eventList.get()) {
    process(e);
}
```

### MapState
```java
private transient MapState<String, Long> productCounts;

Long count = productCounts.get(productId);
productCounts.put(productId, count + 1);
```

## State Backend Configuration
```java
// RocksDB for large state
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig().setCheckpointStorage("s3://checkpoints/");
```

## State TTL
```java
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.hours(24))
    .setUpdateType(UpdateType.OnCreateAndWrite)
    .cleanupIncrementally(10, true)
    .build();

descriptor.enableTimeToLive(ttlConfig);
```
