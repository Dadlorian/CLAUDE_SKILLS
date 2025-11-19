# Monitoring and Alerting Setup Guide

## Prometheus Metrics
```java
Counter eventsProcessed = Counter.build()
    .name("events_processed_total")
    .labelNames("source", "type")
    .register();

Histogram latency = Histogram.build()
    .name("processing_latency_seconds")
    .buckets(0.01, 0.05, 0.1, 0.5, 1, 5)
    .register();

Timer.Sample sample = Timer.start();
processEvent(event);
sample.stop(latency);
eventsProcessed.labels("kafka", event.getType()).inc();
```

## Grafana Dashboard JSON
```json
{
  "panels": [{
    "title": "Event Throughput",
    "targets": [{
      "expr": "rate(events_processed_total[5m])"
    }]
  }]
}
```

## AlertManager Rules
```yaml
groups:
  - name: streaming
    rules:
      - alert: HighLag
        expr: kafka_consumergroup_lag > 10000
        for: 5m
        annotations:
          summary: "Consumer lag too high"
```

## Best Practices
- Monitor end-to-end latency
- Track consumer lag
- Alert on error rates
- Set up SLO dashboards
