# Real-Time Stream Joins Guide

## Stream-Stream Join (Flink)
```java
DataStream<Event> events = ...;
DataStream<Purchase> purchases = ...;

events
    .join(purchases)
    .where(Event::getUserId)
    .equalTo(Purchase::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .apply((event, purchase) -> new EnrichedPurchase(event, purchase));
```

## Stream-Table Join (Spark)
```scala
val events = spark.readStream...
val users = spark.read.parquet("users/")

val enriched = events.join(users, "user_id")
```

## Interval Join
```java
events
    .keyBy(Event::getId)
    .intervalJoin(purchases.keyBy(Purchase::getEventId))
    .between(Time.seconds(-30), Time.seconds(30))
    .process(new IntervalJoinFunction());
```

## Best Practices
- Use watermarks for event-time joins
- Set appropriate join windows
- Handle late data
- Monitor join state size
