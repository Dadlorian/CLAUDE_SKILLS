# Streaming Data Ingestion Pipeline Guide

## Overview
Build end-to-end streaming ingestion from sources to analytics databases.

## Pipeline Architecture
```
Sources → Kafka → Schema Validation → Enrichment → Sink
```

## Kafka Producer
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    compression_type='lz4',
    batch_size=32768,
    linger_ms=10
)

def send_event(event):
    producer.send('events', key=event['user_id'].encode(), value=event)
```

## Flink Ingestion Job
```java
DataStream<Event> events = env
    .addSource(new FlinkKafkaConsumer<>("events", schema, props))
    .filter(new EventValidator())
    .map(new EventEnricher())
    .addSink(new ClickHouseSink());
```

## Best Practices
- Use schema registry
- Implement validation early
- Monitor lag continuously
- Handle backpressure
- Enable exactly-once semantics
