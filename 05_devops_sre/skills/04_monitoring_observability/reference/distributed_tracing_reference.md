# Distributed Tracing Reference Guide

## Table of Contents
1. [Distributed Tracing Fundamentals](#distributed-tracing-fundamentals)
2. [OpenTelemetry](#opentelemetry)
3. [Jaeger](#jaeger)
4. [Zipkin](#zipkin)
5. [Trace Analysis](#trace-analysis)
6. [Best Practices](#best-practices)

---

## Distributed Tracing Fundamentals

### Core Concepts

#### Trace
A trace represents the complete journey of a request through a distributed system. It consists of one or more spans.

```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
Duration: 234ms

┌─ Frontend (45ms) ─────────────────────────────────┐
  └─ API Gateway (12ms) ───────────────────────┐
      ├─ Auth Service (23ms) ─────────┐
      └─ User Service (156ms) ────────────────┐
          └─ Database Query (143ms) ──────┐
```

#### Span
A span represents a single operation within a trace. It has:
- **Span ID**: Unique identifier
- **Parent Span ID**: Links to parent span
- **Operation name**: Description of the operation
- **Start time** and **duration**
- **Tags**: Key-value metadata
- **Logs**: Timestamped events
- **Baggage**: Cross-process context

```json
{
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "parentSpanId": "00f067aa0ba90100",
  "operationName": "database.query",
  "startTime": 1609459200000000,
  "duration": 143000,
  "tags": {
    "db.type": "postgresql",
    "db.statement": "SELECT * FROM users WHERE id = $1",
    "db.instance": "users-db",
    "span.kind": "client"
  },
  "logs": [
    {
      "timestamp": 1609459200050000,
      "fields": {
        "event": "connection_acquired",
        "pool_size": 10
      }
    }
  ]
}
```

#### Context Propagation
Passing trace context across service boundaries.

**W3C Trace Context Format (Standard)**
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: vendor1=value1,vendor2=value2
```

**B3 Format (Zipkin)**
```
X-B3-TraceId: 4bf92f3577b34da6a3ce929d0e0e4736
X-B3-SpanId: 00f067aa0ba902b7
X-B3-ParentSpanId: 00f067aa0ba90100
X-B3-Sampled: 1
```

### Sampling Strategies

#### Head-based Sampling
Decision made at trace initiation.

**Probabilistic Sampling**
```yaml
sampling:
  type: probabilistic
  param: 0.1  # Sample 10% of traces
```

**Rate Limiting Sampling**
```yaml
sampling:
  type: rate-limiting
  param: 100  # Maximum 100 traces per second
```

#### Tail-based Sampling
Decision made after trace completion.

```yaml
sampling:
  type: tail-based
  policies:
    - name: errors
      type: status_code
      status_code:
        status_codes: [ERROR]
    - name: slow_requests
      type: latency
      latency:
        threshold_ms: 1000
    - name: probabilistic
      type: probabilistic
      probabilistic:
        sampling_percentage: 5
```

---

## OpenTelemetry

OpenTelemetry (OTel) is the industry-standard observability framework for cloud-native software.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Application                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         OpenTelemetry SDK                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │  Tracer  │  │  Meter   │  │  Logger  │        │ │
│  │  └──────────┘  └──────────┘  └──────────┘        │ │
│  │                                                    │ │
│  │  ┌────────────────────────────────────────────┐  │ │
│  │  │        Exporters (OTLP, Jaeger, etc.)     │  │ │
│  │  └────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────┘
                           │ OTLP/gRPC or HTTP
                           ▼
┌─────────────────────────────────────────────────────────┐
│              OpenTelemetry Collector                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ Receivers  │→ │ Processors │→ │ Exporters  │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
         ┌────────┐              ┌─────────┐
         │ Jaeger │              │ Zipkin  │
         └────────┘              └─────────┘
```

### Semantic Conventions

Standard attributes for common operations.

#### HTTP Spans
```python
span.set_attribute("http.method", "GET")
span.set_attribute("http.url", "https://api.example.com/users/123")
span.set_attribute("http.status_code", 200)
span.set_attribute("http.user_agent", "Mozilla/5.0...")
span.set_attribute("http.request_content_length", 1234)
span.set_attribute("http.response_content_length", 5678)
```

#### Database Spans
```python
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.connection_string", "postgresql://db.example.com:5432")
span.set_attribute("db.user", "app_user")
span.set_attribute("db.name", "production")
span.set_attribute("db.statement", "SELECT * FROM users WHERE id = $1")
span.set_attribute("db.operation", "SELECT")
```

#### RPC/gRPC Spans
```python
span.set_attribute("rpc.system", "grpc")
span.set_attribute("rpc.service", "UserService")
span.set_attribute("rpc.method", "GetUser")
span.set_attribute("rpc.grpc.status_code", 0)
```

#### Messaging Spans
```python
span.set_attribute("messaging.system", "kafka")
span.set_attribute("messaging.destination", "user-events")
span.set_attribute("messaging.destination_kind", "topic")
span.set_attribute("messaging.operation", "publish")
span.set_attribute("messaging.message_id", "abc123")
```

### OpenTelemetry Collector Configuration

#### Basic Configuration
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024
    send_batch_max_size: 2048

  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128

  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

  attributes:
    actions:
      - key: sensitive_data
        action: delete

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  zipkin:
    endpoint: http://zipkin:9411/api/v2/spans

  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889

  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resource, attributes]
      exporters: [jaeger, zipkin, otlp/tempo]

    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]

  telemetry:
    logs:
      level: info
    metrics:
      address: 0.0.0.0:8888
```

#### Advanced Processors

**Span Processor**
```yaml
processors:
  span:
    name:
      # Extract service name from attributes
      from_attributes: ["http.method", "http.route"]
      separator: " "
    status:
      # Override span status based on attributes
      code: Error
      description: "Request failed"
```

**Tail Sampling Processor**
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100
    expected_new_traces_per_sec: 10
    policies:
      - name: errors-policy
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: slow-traces-policy
        type: latency
        latency:
          threshold_ms: 1000
      - name: sample-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 10
```

**Resource Detection Processor**
```yaml
processors:
  resourcedetection:
    detectors: [env, system, docker, kubernetes]
    timeout: 5s
    override: false
```

### SDK Configuration Examples

#### Python (Auto-instrumentation)
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Configure resource
resource = Resource.create({
    "service.name": "user-service",
    "service.version": "1.2.3",
    "deployment.environment": "production"
})

# Set up tracer provider
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True
)

# Add batch span processor
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Auto-instrument libraries
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)
```

#### Go
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
)

func initTracer() (*sdktrace.TracerProvider, error) {
    // Create OTLP exporter
    exporter, err := otlptracegrpc.New(
        context.Background(),
        otlptracegrpc.WithEndpoint("otel-collector:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    // Create resource
    res, err := resource.New(
        context.Background(),
        resource.WithAttributes(
            semconv.ServiceName("user-service"),
            semconv.ServiceVersion("1.2.3"),
            semconv.DeploymentEnvironment("production"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // Create tracer provider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )

    otel.SetTracerProvider(tp)
    return tp, nil
}
```

#### Node.js
```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'user-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.2.3',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'production',
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel-collector:4317',
  }),
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});

sdk.start();
```

---

## Jaeger

Jaeger is an open-source, distributed tracing platform.

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Application │────▶│Jaeger Agent  │────▶│  Collector   │
│              │     │   (Client)   │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Storage    │
                                          │ (Cassandra/  │
                                          │ Elasticsearch)│
                                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  Query UI    │
                                          │              │
                                          └──────────────┘
```

### Deployment Configuration

#### All-in-One (Development)
```bash
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14250:14250 \
  -p 14268:14268 \
  -p 14269:14269 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

#### Production with Elasticsearch
```yaml
# docker-compose.yml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - "9200:9200"
    volumes:
      - esdata:/usr/share/elasticsearch/data

  jaeger-collector:
    image: jaegertracing/jaeger-collector:latest
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "14269:14269"  # Admin port
      - "14268:14268"  # HTTP
      - "14250:14250"  # gRPC
      - "9411:9411"    # Zipkin compatible
    depends_on:
      - elasticsearch

  jaeger-query:
    image: jaegertracing/jaeger-query:latest
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    ports:
      - "16686:16686"  # UI
      - "16687:16687"  # Admin
    depends_on:
      - elasticsearch

  jaeger-agent:
    image: jaegertracing/jaeger-agent:latest
    command:
      - "--reporter.grpc.host-port=jaeger-collector:14250"
    ports:
      - "5775:5775/udp"  # Zipkin thrift
      - "6831:6831/udp"  # Jaeger thrift compact
      - "6832:6832/udp"  # Jaeger thrift binary
      - "5778:5778"      # Serve configs
    depends_on:
      - jaeger-collector

volumes:
  esdata:
```

### Query API

#### Find Traces
```bash
# Search by service and operation
curl -G "http://jaeger:16686/api/traces" \
  --data-urlencode "service=user-service" \
  --data-urlencode "operation=GET /users/:id" \
  --data-urlencode "start=1609459200000000" \
  --data-urlencode "end=1609545600000000" \
  --data-urlencode "limit=20"

# Search by tags
curl -G "http://jaeger:16686/api/traces" \
  --data-urlencode "service=user-service" \
  --data-urlencode "tags={\"http.status_code\":\"500\"}" \
  --data-urlencode "limit=20"

# Search by minimum duration
curl -G "http://jaeger:16686/api/traces" \
  --data-urlencode "service=user-service" \
  --data-urlencode "minDuration=1s" \
  --data-urlencode "limit=20"
```

#### Get Trace by ID
```bash
curl "http://jaeger:16686/api/traces/4bf92f3577b34da6a3ce929d0e0e4736"
```

### Sampling Strategies

#### Remote Sampling Configuration
```json
{
  "service_strategies": [
    {
      "service": "user-service",
      "type": "probabilistic",
      "param": 0.5
    },
    {
      "service": "auth-service",
      "type": "rate_limiting",
      "param": 100
    }
  ],
  "default_strategy": {
    "type": "probabilistic",
    "param": 0.1
  }
}
```

---

## Zipkin

Zipkin is a distributed tracing system that helps gather timing data for troubleshooting latency problems.

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Application │────▶│   Reporter   │────▶│  Collector   │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │   Storage    │
                                          │  (MySQL/     │
                                          │ Cassandra/   │
                                          │ Elasticsearch)│
                                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  Query UI    │
                                          │              │
                                          └──────────────┘
```

### Deployment

#### Docker Compose
```yaml
version: '3'
services:
  zipkin:
    image: openzipkin/zipkin:latest
    ports:
      - "9411:9411"
    environment:
      - STORAGE_TYPE=elasticsearch
      - ES_HOSTS=elasticsearch:9200
    depends_on:
      - elasticsearch

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    volumes:
      - esdata:/usr/share/elasticsearch/data

volumes:
  esdata:
```

### API

#### Send Spans (JSON v2)
```bash
curl -X POST http://zipkin:9411/api/v2/spans \
  -H 'Content-Type: application/json' \
  -d '[{
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "id": "00f067aa0ba902b7",
    "name": "get-user",
    "timestamp": 1609459200000000,
    "duration": 234000,
    "kind": "SERVER",
    "localEndpoint": {
      "serviceName": "user-service",
      "ipv4": "192.168.1.10",
      "port": 8080
    },
    "tags": {
      "http.method": "GET",
      "http.path": "/users/123",
      "http.status_code": "200"
    }
  }]'
```

#### Query Traces
```bash
# By service name
curl "http://zipkin:9411/api/v2/traces?serviceName=user-service&limit=10"

# By span name
curl "http://zipkin:9411/api/v2/traces?serviceName=user-service&spanName=get-user"

# By tag
curl "http://zipkin:9411/api/v2/traces?annotationQuery=http.status_code=500"

# By duration
curl "http://zipkin:9411/api/v2/traces?serviceName=user-service&minDuration=1000000"
```

---

## Trace Analysis

### Key Metrics from Traces

#### Latency Analysis
```
P50: 45ms
P90: 123ms
P95: 234ms
P99: 567ms
Max: 1234ms

Critical path: Frontend → API Gateway → Database
Bottleneck: Database query (avg 143ms, 61% of total time)
```

#### Error Analysis
```
Total traces: 10,000
Error traces: 250 (2.5%)
Error types:
  - 500 Internal Server Error: 150 (60%)
  - 503 Service Unavailable: 75 (30%)
  - 504 Gateway Timeout: 25 (10%)

Most common error span: database.query
Error pattern: Connection pool exhaustion during peak hours
```

#### Dependency Analysis
```
Service dependency graph:
frontend → api-gateway → auth-service
                      → user-service → database
                      → cache-service

Critical dependencies (>100ms avg latency):
  - user-service → database (143ms)
  - api-gateway → user-service (156ms)

Redundant calls:
  - Multiple cache lookups in single request (optimize)
  - Duplicate auth checks (cache auth tokens)
```

### TraceQL (Grafana Tempo)

Query language for traces.

```traceql
# Find slow traces
{ duration > 1s }

# Find error traces
{ status = error }

# Find traces for specific service
{ resource.service.name = "user-service" }

# Find traces with specific HTTP status
{ span.http.status_code = 500 }

# Complex query
{
  resource.service.name = "user-service" &&
  span.http.method = "POST" &&
  duration > 500ms
}

# Aggregate by service
{} | by(resource.service.name)

# Count spans
{} | count() > 10
```

---

## Best Practices

### Instrumentation Best Practices

1. **Instrument at service boundaries**
   - HTTP requests/responses
   - RPC calls
   - Database queries
   - Message queue operations

2. **Use semantic conventions**
   - Follow OpenTelemetry semantic conventions
   - Consistent attribute naming
   - Standard span kinds (CLIENT, SERVER, PRODUCER, CONSUMER)

3. **Add meaningful attributes**
   ```python
   # Good
   span.set_attribute("user.id", user_id)
   span.set_attribute("cart.item_count", len(cart_items))
   span.set_attribute("payment.method", "credit_card")

   # Avoid high-cardinality attributes
   # Bad: span.set_attribute("request.uuid", generate_uuid())
   ```

4. **Log important events**
   ```python
   span.add_event(
       "cache_miss",
       attributes={
           "cache.key": key,
           "cache.ttl": ttl
       }
   )
   ```

5. **Record errors properly**
   ```python
   try:
       result = process_request()
   except Exception as e:
       span.record_exception(e)
       span.set_status(Status(StatusCode.ERROR, str(e)))
       raise
   ```

### Sampling Best Practices

1. **Use head-based sampling for high-volume services**
   - Probabilistic sampling (e.g., 1-10%)
   - Rate limiting (e.g., 1000 traces/sec)

2. **Use tail-based sampling for critical services**
   - Always sample errors
   - Always sample slow requests (>1s)
   - Probabilistic sample normal requests

3. **Per-service sampling rates**
   ```yaml
   high_volume_service: 0.01  # 1%
   medium_volume_service: 0.1  # 10%
   low_volume_service: 1.0     # 100%
   ```

### Performance Optimization

1. **Use batch exporters**
   - Reduce network overhead
   - Typical batch size: 512-2048 spans

2. **Configure memory limits**
   - Prevent memory exhaustion
   - Set appropriate queue sizes

3. **Use asynchronous exporters**
   - Don't block application threads
   - Handle export failures gracefully

4. **Implement circuit breakers**
   - Stop sending spans if backend is down
   - Prevent cascading failures

### Storage Best Practices

1. **Set appropriate retention periods**
   - Hot storage: 1-7 days (fast queries)
   - Cold storage: 30-90 days (archival)

2. **Index strategically**
   - Index on service name, operation name
   - Index on common query patterns
   - Avoid over-indexing (impacts write performance)

3. **Use tiered storage**
   - Recent traces: SSD storage
   - Older traces: Object storage (S3, GCS)

### Security Best Practices

1. **Sanitize sensitive data**
   ```python
   # Remove sensitive headers
   if "authorization" in headers:
       headers["authorization"] = "[REDACTED]"

   # Mask sensitive attributes
   span.set_attribute("credit_card", mask_credit_card(card_number))
   ```

2. **Implement access controls**
   - RBAC for trace data
   - Service-level isolation
   - PII redaction

3. **Use secure transport**
   - TLS for trace transmission
   - Mutual TLS for sensitive environments

### Debugging with Traces

1. **Identify slow spans**
   - Look for spans >100ms
   - Check critical path
   - Analyze parallel vs sequential operations

2. **Find error patterns**
   - Group errors by type
   - Identify common failure points
   - Correlate with deployment events

3. **Analyze dependencies**
   - Map service call graph
   - Identify unnecessary calls
   - Detect circular dependencies

4. **Correlate with metrics and logs**
   - Link trace IDs in logs
   - Compare trace latency with metrics
   - Use exemplars in Prometheus
