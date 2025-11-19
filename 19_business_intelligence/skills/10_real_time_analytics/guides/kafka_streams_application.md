# Kafka Streams Application Guide

## Basic Topology
```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, Event> events = builder.stream("events");

KTable<String, Long> counts = events
    .groupBy((key, event) -> event.getEventType())
    .count();

counts.toStream().to("event-counts");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

## Stateful Processing
```java
events
    .groupByKey()
    .aggregate(
        () -> new UserMetrics(),
        (key, event, metrics) -> metrics.add(event),
        Materialized.as("user-metrics-store")
    );
```

## Windowing
```java
events
    .groupByKey()
    .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
    .count()
    .toStream()
    .to("windowed-counts");
```

## Interactive Queries
```java
ReadOnlyKeyValueStore<String, Long> store = streams.store(
    StoreQueryParameters.fromNameAndType("user-metrics-store", 
        QueryableStoreTypes.keyValueStore())
);

Long count = store.get(userId);
```
