# Windowing and Aggregations Guide

## Tumbling Windows
```java
// Non-overlapping 5-minute windows
events
    .windowAll(TumblingEventTimeWindows.of(Time.minutes(5)))
    .reduce((e1, e2) -> e1.merge(e2));
```

## Sliding Windows
```java
// 10-minute windows sliding every 5 minutes
events
    .windowAll(SlidingEventTimeWindows.of(
        Time.minutes(10),
        Time.minutes(5)
    ))
    .aggregate(new AverageAggregator());
```

## Session Windows
```java
// Dynamic windows with 30-minute gap
events
    .keyBy(Event::getUserId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .reduce((e1, e2) -> e1.merge(e2));
```

## Custom Aggregations
```java
public class CustomAggregator 
        implements AggregateFunction<Event, Accumulator, Result> {
    
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
}
```
