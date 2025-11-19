# Implementing Distributed Tracing Guide

This guide walks you through implementing distributed tracing in a microservices architecture using OpenTelemetry, with Jaeger as the backend.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Setting Up the Tracing Backend](#setting-up-the-tracing-backend)
4. [Deploying OpenTelemetry Collector](#deploying-opentelemetry-collector)
5. [Instrumenting a Python Application](#instrumenting-a-python-application)
6. [Instrumenting a Go Application](#instrumenting-a-go-application)
7. [Instrumenting a Node.js Application](#instrumenting-a-nodejs-application)
8. [Context Propagation](#context-propagation)
9. [Sampling Strategies](#sampling-strategies)
10. [Integrating with Logs and Metrics](#integrating-with-logs-and-metrics)
11. [Production Best Practices](#production-best-practices)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   Microservices                          │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Frontend  │  │  API       │  │  User      │        │
│  │  (Node.js) │→ │  Gateway   │→ │  Service   │        │
│  │            │  │  (Go)      │  │  (Python)  │        │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘        │
│        │               │               │                │
│        │ OTLP/gRPC     │ OTLP/gRPC     │ OTLP/gRPC     │
│        │               │               │                │
└────────┼───────────────┼───────────────┼────────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  OpenTelemetry Collector       │
         │                                │
         │  - Receive traces (OTLP)      │
         │  - Process (sampling, etc.)   │
         │  - Export to backends         │
         └────────┬──────────────────────┘
                  │
                  ├──────────────┬─────────────┐
                  ▼              ▼             ▼
         ┌───────────┐  ┌───────────┐  ┌──────────┐
         │  Jaeger   │  │  Tempo    │  │  Zipkin  │
         │           │  │           │  │          │
         └───────────┘  └───────────┘  └──────────┘
```

---

## Prerequisites

- Docker and Docker Compose
- Multiple microservices (or sample apps)
- Basic understanding of your programming languages
- Network connectivity between services

---

## Setting Up the Tracing Backend

### Option 1: Jaeger All-in-One (Development)

```yaml
# docker-compose.yml
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "5775:5775/udp"   # Zipkin thrift
      - "6831:6831/udp"   # Jaeger thrift compact
      - "6832:6832/udp"   # Jaeger thrift binary
      - "5778:5778"       # Serve configs
      - "16686:16686"     # UI
      - "14250:14250"     # gRPC
      - "14268:14268"     # HTTP
      - "14269:14269"     # Admin
      - "9411:9411"       # Zipkin
      - "4317:4317"       # OTLP gRPC
      - "4318:4318"       # OTLP HTTP
```

Start Jaeger:

```bash
docker-compose up -d jaeger

# Access UI
open http://localhost:16686
```

### Option 2: Jaeger with Elasticsearch (Production)

```yaml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms2g -Xmx2g
    ports:
      - "9200:9200"
    volumes:
      - esdata:/usr/share/elasticsearch/data

  jaeger-collector:
    image: jaegertracing/jaeger-collector:latest
    container_name: jaeger-collector
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - ES_NUM_SHARDS=1
      - ES_NUM_REPLICAS=0
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "14269:14269"  # Admin
      - "14268:14268"  # HTTP
      - "14250:14250"  # gRPC
      - "9411:9411"    # Zipkin
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    depends_on:
      - elasticsearch

  jaeger-query:
    image: jaegertracing/jaeger-query:latest
    container_name: jaeger-query
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - QUERY_BASE_PATH=/jaeger
    ports:
      - "16686:16686"  # UI
      - "16687:16687"  # Admin
    depends_on:
      - elasticsearch

volumes:
  esdata:
```

---

## Deploying OpenTelemetry Collector

### Collector Configuration

Create `otel-collector-config.yaml`:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Prometheus receiver for scraping metrics
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          scrape_interval: 10s
          static_configs:
            - targets: ['localhost:8888']

processors:
  # Batch processor for better performance
  batch:
    timeout: 10s
    send_batch_size: 1024
    send_batch_max_size: 2048

  # Memory limiter to prevent OOM
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128

  # Resource processor to add/modify resource attributes
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert
      - key: cluster
        value: k8s-prod-01
        action: upsert

  # Attributes processor to modify span attributes
  attributes:
    actions:
      # Remove sensitive data
      - key: http.request.header.authorization
        action: delete
      - key: http.request.header.cookie
        action: delete
      # Add custom attributes
      - key: custom.region
        value: us-east-1
        action: insert

  # Tail sampling processor (decision after trace completion)
  tail_sampling:
    decision_wait: 10s
    num_traces: 100
    expected_new_traces_per_sec: 10
    policies:
      # Always sample errors
      - name: errors-policy
        type: status_code
        status_code:
          status_codes: [ERROR]

      # Always sample slow requests
      - name: slow-traces-policy
        type: latency
        latency:
          threshold_ms: 1000

      # Sample 10% of normal traces
      - name: probabilistic-policy
        type: probabilistic
        probabilistic:
          sampling_percentage: 10

exporters:
  # Jaeger exporter
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true

  # Zipkin exporter
  zipkin:
    endpoint: http://zipkin:9411/api/v2/spans
    format: proto

  # OTLP exporter (for Grafana Tempo, etc.)
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Prometheus exporter for metrics
  prometheus:
    endpoint: 0.0.0.0:8889

  # Logging exporter (for debugging)
  logging:
    loglevel: debug
    sampling_initial: 5
    sampling_thereafter: 200

extensions:
  health_check:
    endpoint: 0.0.0.0:13133

  pprof:
    endpoint: 0.0.0.0:1777

  zpages:
    endpoint: 0.0.0.0:55679

service:
  extensions: [health_check, pprof, zpages]

  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, attributes, tail_sampling, batch]
      exporters: [jaeger, logging]

    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus, logging]

  telemetry:
    logs:
      level: info
    metrics:
      address: 0.0.0.0:8888
```

### Deploy Collector

Add to `docker-compose.yml`:

```yaml
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: otel-collector
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8888:8888"   # Metrics
      - "8889:8889"   # Prometheus exporter
      - "13133:13133" # Health check
      - "55679:55679" # zPages
    depends_on:
      - jaeger-collector
```

Start the collector:

```bash
docker-compose up -d otel-collector

# Verify health
curl http://localhost:13133/
```

---

## Instrumenting a Python Application

### Installation

```bash
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-instrumentation-flask \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-sqlalchemy \
            opentelemetry-exporter-otlp-proto-grpc
```

### Manual Instrumentation

```python
# app.py
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests

# Configure resource
resource = Resource.create({
    "service.name": "user-service",
    "service.version": "1.0.0",
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

# Create Flask app
app = Flask(__name__)

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)

# Auto-instrument requests library
RequestsInstrumentor().instrument()

# Get tracer
tracer = trace.get_tracer(__name__)

@app.route('/users/<user_id>')
def get_user(user_id):
    # Current span is automatically created by Flask instrumentation
    current_span = trace.get_current_span()

    # Add custom attributes
    current_span.set_attribute("user.id", user_id)
    current_span.set_attribute("http.route", "/users/:id")

    # Create a custom span
    with tracer.start_as_current_span("fetch_user_from_db") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", "SELECT")

        # Add event
        span.add_event("Querying database", {
            "query": f"SELECT * FROM users WHERE id = {user_id}"
        })

        try:
            # Simulate database query
            user = {"id": user_id, "name": "John Doe"}

            span.set_status(trace.Status(trace.StatusCode.OK))
            return user

        except Exception as e:
            # Record exception
            span.record_exception(e)
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, str(e))
            )
            raise

@app.route('/users/<user_id>/profile')
def get_user_profile(user_id):
    with tracer.start_as_current_span("get_user_profile") as span:
        span.set_attribute("user.id", user_id)

        # Call another service (auto-instrumented)
        response = requests.get(f"http://auth-service/verify/{user_id}")

        if response.status_code == 200:
            # Call internal function with custom span
            profile = fetch_profile_data(user_id)
            return profile
        else:
            span.set_status(
                trace.Status(trace.StatusCode.ERROR, "Auth failed")
            )
            return {"error": "Unauthorized"}, 401

def fetch_profile_data(user_id):
    with tracer.start_as_current_span("fetch_profile_data") as span:
        span.set_attribute("user.id", user_id)

        # Simulate database query
        return {
            "user_id": user_id,
            "bio": "Software Engineer",
            "location": "San Francisco"
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Auto-Instrumentation (Easier Approach)

```bash
# Install auto-instrumentation
pip install opentelemetry-distro \
            opentelemetry-instrumentation

# Bootstrap (installs all available instrumentations)
opentelemetry-bootstrap -a install
```

Run with auto-instrumentation:

```bash
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
export OTEL_SERVICE_NAME=user-service
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp

opentelemetry-instrument python app.py
```

---

## Instrumenting a Go Application

### Installation

```bash
go get go.opentelemetry.io/otel \
       go.opentelemetry.io/otel/sdk \
       go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc \
       go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp
```

### Implementation

```go
// main.go
package main

import (
    "context"
    "fmt"
    "log"
    "net/http"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
    "go.opentelemetry.io/otel/trace"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
)

var tracer trace.Tracer

func initTracer() (*sdktrace.TracerProvider, error) {
    ctx := context.Background()

    // Create OTLP exporter
    conn, err := grpc.DialContext(
        ctx,
        "otel-collector:4317",
        grpc.WithTransportCredentials(insecure.NewCredentials()),
        grpc.WithBlock(),
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create gRPC connection: %w", err)
    }

    exporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
    if err != nil {
        return nil, fmt.Errorf("failed to create OTLP exporter: %w", err)
    }

    // Create resource
    res, err := resource.New(
        ctx,
        resource.WithAttributes(
            semconv.ServiceName("api-gateway"),
            semconv.ServiceVersion("1.0.0"),
            semconv.DeploymentEnvironment("production"),
        ),
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create resource: %w", err)
    }

    // Create tracer provider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )

    // Set global tracer provider
    otel.SetTracerProvider(tp)

    // Set global propagator for context propagation
    otel.SetTextMapPropagator(
        propagation.NewCompositeTextMapPropagator(
            propagation.TraceContext{},
            propagation.Baggage{},
        ),
    )

    return tp, nil
}

func main() {
    // Initialize tracer
    tp, err := initTracer()
    if err != nil {
        log.Fatal(err)
    }
    defer func() {
        if err := tp.Shutdown(context.Background()); err != nil {
            log.Printf("Error shutting down tracer provider: %v", err)
        }
    }()

    // Get tracer
    tracer = otel.Tracer("api-gateway")

    // Create HTTP handlers with instrumentation
    http.Handle("/api/users", otelhttp.NewHandler(
        http.HandlerFunc(handleUsers),
        "GET /api/users",
    ))

    http.Handle("/api/users/", otelhttp.NewHandler(
        http.HandlerFunc(handleUserByID),
        "GET /api/users/:id",
    ))

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleUsers(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Create custom span
    ctx, span := tracer.Start(ctx, "handle_users")
    defer span.End()

    // Add attributes
    span.SetAttributes(
        attribute.String("http.method", r.Method),
        attribute.String("http.route", "/api/users"),
    )

    // Call backend service
    users, err := fetchUsers(ctx)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    span.SetStatus(codes.Ok, "Success")
    fmt.Fprintf(w, "Users: %v\n", users)
}

func handleUserByID(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    ctx, span := tracer.Start(ctx, "handle_user_by_id")
    defer span.End()

    // Extract user ID from path
    userID := r.URL.Path[len("/api/users/"):]
    span.SetAttributes(attribute.String("user.id", userID))

    // Make HTTP call to downstream service
    user, err := callUserService(ctx, userID)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    span.SetStatus(codes.Ok, "Success")
    fmt.Fprintf(w, "User: %v\n", user)
}

func fetchUsers(ctx context.Context) ([]string, error) {
    ctx, span := tracer.Start(ctx, "fetch_users_from_cache")
    defer span.End()

    // Add event
    span.AddEvent("Checking cache", trace.WithAttributes(
        attribute.String("cache.key", "all_users"),
    ))

    // Simulate cache operation
    time.Sleep(10 * time.Millisecond)

    users := []string{"Alice", "Bob", "Charlie"}
    span.SetAttributes(attribute.Int("users.count", len(users)))

    return users, nil
}

func callUserService(ctx context.Context, userID string) (string, error) {
    ctx, span := tracer.Start(ctx, "call_user_service")
    defer span.End()

    span.SetAttributes(
        attribute.String("peer.service", "user-service"),
        attribute.String("user.id", userID),
    )

    // Create HTTP client with instrumentation
    client := http.Client{
        Transport: otelhttp.NewTransport(http.DefaultTransport),
    }

    // Create request
    req, err := http.NewRequestWithContext(
        ctx,
        "GET",
        fmt.Sprintf("http://user-service:5000/users/%s", userID),
        nil,
    )
    if err != nil {
        return "", err
    }

    // Make request (context is automatically propagated)
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        err := fmt.Errorf("user service returned %d", resp.StatusCode)
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return "", err
    }

    span.SetStatus(codes.Ok, "Success")
    return fmt.Sprintf("User %s data", userID), nil
}
```

---

## Instrumenting a Node.js Application

### Installation

```bash
npm install @opentelemetry/api \
            @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-trace-otlp-grpc
```

### Implementation

```javascript
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'frontend-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'production',
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel-collector:4317',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;
```

```javascript
// app.js
require('./tracing'); // Must be first!

const express = require('express');
const axios = require('axios');
const { trace, context } = require('@opentelemetry/api');

const app = express();
const PORT = 3000;

// Get tracer
const tracer = trace.getTracer('frontend-service');

app.get('/', (req, res) => {
  // Current span is automatically created
  const currentSpan = trace.getSpan(context.active());

  if (currentSpan) {
    currentSpan.setAttribute('custom.attribute', 'value');
    currentSpan.addEvent('Homepage accessed');
  }

  res.send('Hello from Frontend!');
});

app.get('/user/:id', async (req, res) => {
  const userId = req.params.id;

  // Create custom span
  const span = tracer.startSpan('get_user_profile');
  span.setAttribute('user.id', userId);

  try {
    // Call API gateway (auto-instrumented by axios instrumentation)
    const response = await axios.get(
      `http://api-gateway:8080/api/users/${userId}`
    );

    span.setStatus({ code: 0 }); // OK
    span.end();

    res.json(response.data);
  } catch (error) {
    span.recordException(error);
    span.setStatus({
      code: 2, // ERROR
      message: error.message,
    });
    span.end();

    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Frontend service listening on port ${PORT}`);
});
```

Run the application:

```bash
node app.js
```

---

## Context Propagation

Context propagation ensures trace context flows across service boundaries.

### HTTP Headers

OpenTelemetry uses W3C Trace Context by default:

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor1=value1,vendor2=value2
```

### Manual Context Injection (if needed)

```python
# Python
from opentelemetry import trace
from opentelemetry.propagate import inject

headers = {}
inject(headers)  # Injects trace context into headers

response = requests.get('http://service/endpoint', headers=headers)
```

```go
// Go
import "go.opentelemetry.io/otel"

headers := http.Header{}
otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(headers))

req.Header = headers
```

```javascript
// Node.js
const { propagation, context } = require('@opentelemetry/api');

const headers = {};
propagation.inject(context.active(), headers);

axios.get('http://service/endpoint', { headers });
```

---

## Sampling Strategies

### Head-based Sampling

Decision made when trace starts.

```yaml
# OpenTelemetry Collector
processors:
  probabilistic_sampler:
    sampling_percentage: 10  # Sample 10% of traces
```

### Tail-based Sampling

Decision made after trace completes (see collector config above).

### Application-level Sampling

```python
# Python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

sampler = TraceIdRatioBased(0.1)  # 10% sampling
tracer_provider = TracerProvider(sampler=sampler)
```

```go
// Go
tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)), // 10%
)
```

---

## Integrating with Logs and Metrics

### Add Trace ID to Logs

```python
# Python with structlog
import structlog
from opentelemetry import trace

logger = structlog.get_logger()

def log_with_trace():
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')

    logger.info("Processing request", trace_id=trace_id)
```

### Link Traces to Metrics (Exemplars)

```python
# Python
from prometheus_client import Counter
from opentelemetry import trace

request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests'
)

# Increment with exemplar
span = trace.get_current_span()
trace_id = format(span.get_span_context().trace_id, '032x')

request_counter.inc(exemplar={'trace_id': trace_id})
```

---

## Production Best Practices

### 1. Use Batch Exporters

Reduces overhead by batching spans.

### 2. Implement Sampling

Don't trace 100% in production - use intelligent sampling.

### 3. Set Resource Attributes

Always include service name, version, environment.

### 4. Handle Errors Gracefully

```python
try:
    # Operation
    pass
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR))
    raise
```

### 5. Monitor Collector Performance

- Set memory limits
- Monitor queue sizes
- Set up health checks

### 6. Use Proper Span Names

```
# Good
GET /api/users/:id

# Bad
/api/users/123 (too specific)
HTTP request (too generic)
```

### 7. Limit Span Attributes

Don't add unbounded attributes (user IDs, request IDs in high volume).

### 8. Set Retention Policies

Configure appropriate retention in your tracing backend.

---

## Verification

### Generate Test Traffic

```bash
# Frontend
curl http://localhost:3000/user/123

# API Gateway
curl http://localhost:8080/api/users/123

# User Service
curl http://localhost:5000/users/123
```

### View in Jaeger

1. Open http://localhost:16686
2. Select service (e.g., "frontend-service")
3. Click "Find Traces"
4. Click on a trace to view details
5. Verify span hierarchy and context propagation

### Check Collector Metrics

```bash
curl http://localhost:8888/metrics
```

## Conclusion

You now have distributed tracing implemented across your microservices with:
- OpenTelemetry instrumentation
- OpenTelemetry Collector for processing
- Jaeger for visualization
- Context propagation across services
- Intelligent sampling strategies

Next steps:
- Implement SLO monitoring using trace data
- Set up alerts for trace anomalies
- Integrate with logging (trace ID correlation)
- Implement custom instrumentations
- Set up long-term storage and analysis
