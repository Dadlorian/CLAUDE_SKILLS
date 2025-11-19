# Kappa Architecture Implementation Guide

## Overview

Kappa Architecture simplifies Lambda by using only a streaming layer with replayable event logs, eliminating the separate batch layer complexity.

## Architecture

```
Data Sources → Kafka (Replayable Log) → Stream Processing → Serving Layer
                  ↓
            Historical Reprocessing
```

## Key Components

1. **Event Log**: Kafka with long retention
2. **Stream Processor**: Flink/Kafka Streams
3. **Serving Layer**: ClickHouse/Druid
4. **Replay Mechanism**: Reprocess from beginning

## Implementation Steps

### Step 1: Kafka Setup

```bash
# Create topic with long retention
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic events \
  --partitions 24 \
  --replication-factor 3 \
  --config retention.ms=-1 \  # Infinite retention
  --config segment.ms=86400000 \  # 1 day segments
  --config compression.type=lz4

# Enable log compaction for changelog topics
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic user-state \
  --partitions 24 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config min.compaction.lag.ms=3600000
```

### Step 2: Flink Streaming Job

```java
public class KappaProcessor {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Configure for production
        env.enableCheckpointing(60000);
        env.setStateBackend(new EmbeddedRocksDBStateBackend());
        env.getCheckpointConfig().setCheckpointStorage("s3://checkpoints/");
        
        // Kafka source with earliest offset for reprocessing
        KafkaSource<Event> source = KafkaSource.<Event>builder()
            .setBootstrapServers("kafka:9092")
            .setTopics("events")
            .setStartingOffsets(OffsetsInitializer.earliest())
            .setValueOnlyDeserializer(new EventDeserializationSchema())
            .build();
            
        DataStream<Event> events = env.fromSource(source, 
            WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofMinutes(5)));
            
        // Process stream
        DataStream<Metrics> metrics = events
            .keyBy(Event::getUserId)
            .process(new MetricsProcessor());
            
        // Write to serving layer
        metrics.addSink(new ClickHouseSink<>());
        
        env.execute("Kappa Architecture Processor");
    }
}
```

### Step 3: Reprocessing Strategy

```bash
# Stop current job
flink cancel <job-id> -s s3://savepoints/manual-1

# Deploy new version reading from beginning
flink run -s s3://savepoints/manual-1 \
  -p 48 \
  new-processor.jar \
  --fromEarliest true \
  --outputTable metrics_v2
```

## Advantages

- Single code base
- Simpler operations
- Easier to reason about
- No batch/stream synchronization

## Disadvantages

- Requires sufficient Kafka retention
- Reprocessing takes longer
- Higher resource requirements

## Best Practices

1. Use log compaction for state topics
2. Implement versioning for reprocessing
3. Monitor Kafka disk usage
4. Test reprocessing regularly
5. Use consistent hashing for keys

## Resources

- Questioning the Lambda Architecture - Jay Kreps
- Kafka documentation on log retention
- Flink checkpointing and savepoints
