# Monitoring & Observability for Real-Time Analytics

## Overview

Comprehensive monitoring and observability are essential for operating real-time analytics systems at scale. This document covers metrics, logging, tracing, and alerting strategies.

## Key Metrics

### System Health Metrics

#### Throughput
```
Events/second ingested
Events/second processed
Events/second output
Bytes/second throughput
```

**Implementation (Prometheus)**
```java
Counter eventsProcessed = Counter.build()
    .name("events_processed_total")
    .help("Total events processed")
    .labelNames("source", "event_type")
    .register();

eventsProcessed.labels("kafka", "purchase").inc();
```

#### Latency
```
End-to-end latency (P50, P95, P99)
Processing latency
Query latency
Network latency
```

**Implementation**
```java
Summary latency = Summary.build()
    .name("processing_latency_seconds")
    .help("Processing latency")
    .quantile(0.5, 0.05)
    .quantile(0.95, 0.01)
    .quantile(0.99, 0.001)
    .register();

Timer.Sample sample = Timer.start();
processEvent(event);
sample.stop(latency);
```

#### Error Rate
```
Failed events
Invalid records
Deserialization errors
Processing exceptions
```

**Implementation**
```java
Counter errors = Counter.build()
    .name("processing_errors_total")
    .help("Total processing errors")
    .labelNames("error_type", "severity")
    .register();

try {
    process(event);
} catch (ValidationException e) {
    errors.labels("validation", "warning").inc();
} catch (ProcessingException e) {
    errors.labels("processing", "error").inc();
}
```

### Kafka Metrics

#### Consumer Lag
```bash
# Monitor consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group analytics-group --describe

# Key metrics:
# - LAG: Number of messages behind
# - CONSUMER-ID: Which consumer
# - CURRENT-OFFSET: Current position
# - LOG-END-OFFSET: Latest offset
```

**Prometheus Exporter**
```yaml
# Using kafka-lag-exporter
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-lag-exporter
data:
  application.conf: |
    poll-interval = 30 seconds
    lookup-table-size = 120
    clusters = [
      {
        name = "production"
        bootstrap-brokers = "kafka:9092"
        group-whitelist = ["analytics-.*"]
      }
    ]
```

#### Broker Metrics
```
MessagesInPerSec
BytesInPerSec
BytesOutPerSec
RequestsPerSec
PartitionCount
UnderReplicatedPartitions
OfflinePartitionsCount
```

**JMX Export**
```yaml
# Prometheus JMX exporter config
lowercaseOutputName: true
rules:
  - pattern: kafka.server<type=(.+), name=(.+)><>Value
    name: kafka_server_$1_$2
```

### Stream Processing Metrics

#### Flink Metrics
```java
public class MetricMapper extends RichMapFunction<Event, Event> {
    private transient Counter recordsProcessed;
    private transient Meter recordsPerSecond;
    private transient Histogram processingTime;

    @Override
    public void open(Configuration parameters) {
        MetricGroup metricGroup = getRuntimeContext().getMetricGroup();

        recordsProcessed = metricGroup.counter("records_processed");
        recordsPerSecond = metricGroup.meter("records_per_second",
            new MeterView(60));
        processingTime = metricGroup.histogram("processing_time",
            new DescriptiveStatisticsHistogram(1000));
    }

    @Override
    public Event map(Event event) {
        long start = System.currentTimeMillis();

        Event result = process(event);

        recordsProcessed.inc();
        recordsPerSecond.markEvent();
        processingTime.update(System.currentTimeMillis() - start);

        return result;
    }
}
```

**Key Flink Metrics**
```
numRecordsIn
numRecordsOut
numBytesIn
numBytesOut
currentInputWatermark
checkpointDuration
checkpointSize
lastCheckpointDuration
numberOfFailedCheckpoints
backPressuredTimeMsPerSecond
idleTimeMsPerSecond
busyTimeMsPerSecond
```

#### Spark Streaming Metrics
```scala
val query = streamingQuery.writeStream
  .foreachBatch { (batchDF: DataFrame, batchId: Long) =>
    // Track metrics
    val count = batchDF.count()
    val processingTime = batchDF.sparkSession.streams
      .get(query.id.toString)
      .lastProgress
      .durationMs("triggerExecution")

    metrics.gauge("batch_size", count)
    metrics.gauge("processing_time_ms", processingTime)
  }
  .start()

// StreamingQuery metrics
val progress = query.lastProgress
println(s"Input rows: ${progress.numInputRows}")
println(s"Processing rate: ${progress.processedRowsPerSecond}")
println(s"Input rate: ${progress.inputRowsPerSecond}")
```

### Database Metrics

#### ClickHouse
```sql
-- Query performance
SELECT
    query_id,
    user,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage,
    query
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date >= today()
ORDER BY query_duration_ms DESC
LIMIT 10;

-- Slow queries
SELECT
    normalized_query_hash,
    count() AS query_count,
    avg(query_duration_ms) AS avg_duration,
    max(query_duration_ms) AS max_duration
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date >= today()
GROUP BY normalized_query_hash
HAVING avg_duration > 1000
ORDER BY query_count DESC;

-- Parts and merges
SELECT
    database,
    table,
    count() AS parts,
    sum(rows) AS total_rows,
    formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active
GROUP BY database, table;
```

#### Druid
```bash
# Query metrics via HTTP
curl http://localhost:8082/druid/v2/datasources/events/candidates

# Segment information
curl http://localhost:8082/druid/v2/datasources/events/segments

# Historical node metrics
curl http://localhost:8083/druid/historical/v1/loadstatus
```

**Prometheus Metrics**
```
druid_query_time_total
druid_query_count_total
druid_segment_scan_pending
druid_segment_count
druid_segment_size_bytes
druid_jvm_mem_used
```

## Logging

### Structured Logging

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import net.logstash.logback.argument.StructuredArguments;

public class EventProcessor {
    private static final Logger log = LoggerFactory.getLogger(EventProcessor.class);

    public void process(Event event) {
        log.info("Processing event",
            StructuredArguments.keyValue("event_id", event.getId()),
            StructuredArguments.keyValue("event_type", event.getType()),
            StructuredArguments.keyValue("user_id", event.getUserId()),
            StructuredArguments.keyValue("timestamp", event.getTimestamp())
        );

        try {
            doProcess(event);
            log.info("Event processed successfully",
                StructuredArguments.keyValue("event_id", event.getId())
            );
        } catch (Exception e) {
            log.error("Failed to process event",
                StructuredArguments.keyValue("event_id", event.getId()),
                StructuredArguments.keyValue("error", e.getMessage()),
                e
            );
        }
    }
}
```

### Log Aggregation

**ELK Stack Configuration**
```yaml
# Filebeat configuration
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/flink/*.log
    fields:
      service: flink-analytics
      environment: production
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "flink-logs-%{+yyyy.MM.dd}"

# Logstash pipeline
input {
  kafka {
    bootstrap_servers => "localhost:9092"
    topics => ["application-logs"]
    codec => "json"
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

### Log Levels

```properties
# Log4j2 configuration
rootLogger.level = INFO

# Debug for specific packages
logger.flink.name = org.apache.flink
logger.flink.level = DEBUG

logger.kafka.name = org.apache.kafka
logger.kafka.level = WARN

# Custom appenders
appender.console.type = Console
appender.console.layout.type = JsonLayout

appender.file.type = RollingFile
appender.file.fileName = logs/app.log
appender.file.filePattern = logs/app-%d{yyyy-MM-dd}-%i.log.gz
appender.file.layout.type = JsonLayout
```

## Distributed Tracing

### OpenTelemetry Integration

```java
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

public class TracedEventProcessor {
    private final Tracer tracer;

    public void process(Event event) {
        Span span = tracer.spanBuilder("process_event")
            .setAttribute("event.id", event.getId())
            .setAttribute("event.type", event.getType())
            .setAttribute("user.id", event.getUserId())
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Kafka consumption span
            Span kafkaSpan = tracer.spanBuilder("kafka.consume")
                .setAttribute("kafka.topic", "events")
                .setAttribute("kafka.partition", event.getPartition())
                .setAttribute("kafka.offset", event.getOffset())
                .startSpan();
            kafkaSpan.end();

            // Processing span
            Span processSpan = tracer.spanBuilder("transform")
                .startSpan();
            try (Scope s = processSpan.makeCurrent()) {
                transform(event);
            } finally {
                processSpan.end();
            }

            // Database write span
            Span dbSpan = tracer.spanBuilder("database.write")
                .setAttribute("db.system", "clickhouse")
                .setAttribute("db.name", "analytics")
                .startSpan();
            try (Scope s = dbSpan.makeCurrent()) {
                writeToDatabase(event);
            } finally {
                dbSpan.end();
            }

        } finally {
            span.end();
        }
    }
}
```

### Jaeger Configuration

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-analytics
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
        index-prefix: jaeger
  collector:
    maxReplicas: 5
    resources:
      limits:
        cpu: 1
        memory: 2Gi
```

## Alerting

### Alert Rules

**Prometheus AlertManager**
```yaml
groups:
  - name: streaming_alerts
    interval: 30s
    rules:
      # High consumer lag
      - alert: HighConsumerLag
        expr: kafka_consumergroup_lag > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High consumer lag detected"
          description: "Consumer group {{ $labels.group }} has lag of {{ $value }}"

      # Processing errors
      - alert: HighErrorRate
        expr: rate(processing_errors_total[5m]) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate in stream processing"
          description: "Error rate is {{ $value }} per second"

      # Low throughput
      - alert: LowThroughput
        expr: rate(events_processed_total[5m]) < 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low processing throughput"
          description: "Processing only {{ $value }} events per second"

      # Query latency
      - alert: HighQueryLatency
        expr: histogram_quantile(0.95, query_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High query latency detected"
          description: "P95 query latency is {{ $value }} seconds"

      # Data freshness
      - alert: StaleData
        expr: time() - max(last_event_timestamp) > 300
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No recent data ingested"
          description: "Last event was {{ $value }} seconds ago"
```

### Notification Channels

```yaml
# AlertManager configuration
route:
  receiver: default
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    - match:
        severity: critical
      receiver: pagerduty
      continue: true

    - match:
        severity: warning
      receiver: slack

receivers:
  - name: default
    email_configs:
      - to: 'team@example.com'

  - name: pagerduty
    pagerduty_configs:
      - service_key: '<pagerduty-key>'

  - name: slack
    slack_configs:
      - api_url: '<slack-webhook-url>'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Dashboards

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Real-Time Analytics Pipeline",
    "panels": [
      {
        "title": "Event Throughput",
        "targets": [
          {
            "expr": "rate(events_processed_total[5m])",
            "legendFormat": "{{ source }}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Processing Latency (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, processing_latency_seconds)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Consumer Lag",
        "targets": [
          {
            "expr": "kafka_consumergroup_lag",
            "legendFormat": "{{ group }} - {{ topic }}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(processing_errors_total[5m])",
            "legendFormat": "{{ error_type }}"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

## Health Checks

### Application Health

```java
@RestController
@RequestMapping("/health")
public class HealthCheckController {

    @Autowired
    private KafkaConsumer consumer;

    @Autowired
    private DatabaseConnection database;

    @GetMapping
    public ResponseEntity<Health> health() {
        Health.Builder builder = new Health.Builder();

        // Check Kafka connectivity
        try {
            consumer.listTopics(Duration.ofSeconds(5));
            builder.up("kafka", "Connected");
        } catch (Exception e) {
            builder.down("kafka", e.getMessage());
        }

        // Check database connectivity
        try {
            database.ping();
            builder.up("database", "Connected");
        } catch (Exception e) {
            builder.down("database", e.getMessage());
        }

        // Check consumer lag
        long lag = getConsumerLag();
        if (lag > 10000) {
            builder.degraded("consumer_lag", lag);
        } else {
            builder.up("consumer_lag", lag);
        }

        Health health = builder.build();
        HttpStatus status = health.isHealthy() ?
            HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;

        return ResponseEntity.status(status).body(health);
    }

    @GetMapping("/ready")
    public ResponseEntity<Void> ready() {
        // Check if application is ready to receive traffic
        if (isReady()) {
            return ResponseEntity.ok().build();
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).build();
        }
    }

    @GetMapping("/live")
    public ResponseEntity<Void> live() {
        // Check if application is alive
        return ResponseEntity.ok().build();
    }
}
```

## Best Practices

1. **Multi-Layer Monitoring**: System, application, and business metrics
2. **SLI/SLO/SLA**: Define and track service levels
3. **Alert Fatigue**: Only alert on actionable issues
4. **Runbooks**: Document response procedures
5. **Correlation**: Link metrics, logs, and traces
6. **Retention**: Balance detail with storage costs
7. **Sampling**: Use for high-volume traces
8. **Dashboards**: Create role-specific views
9. **Synthetic Monitoring**: Proactive testing
10. **Cost Monitoring**: Track infrastructure costs

## Resources

- Prometheus documentation
- Grafana tutorials
- OpenTelemetry guides
- ELK Stack documentation
- Site Reliability Engineering (Google)
