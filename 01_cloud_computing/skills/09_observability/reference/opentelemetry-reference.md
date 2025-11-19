# OpenTelemetry Reference

## Overview

OpenTelemetry (OTEL) is an open-source observability framework providing vendor-neutral APIs, SDKs, and tools to instrument, generate, collect, and export telemetry data (metrics, logs, and traces).

## Architecture

### Components

```
Application Code
      ↓
OpenTelemetry API (instrument code)
      ↓
OpenTelemetry SDK (collect telemetry)
      ↓
OTEL Collector (optional pipeline)
      ↓
Backend (Jaeger, Prometheus, etc.)
```

### Core Components

#### API
- **Purpose**: Instrument application code
- **Language**: Per-language implementation
- **Stability**: Stable, backward compatible
- **Usage**: Import and use in code

#### SDK
- **Purpose**: Implement API, manage telemetry
- **Configuration**: Sampling, export, resources
- **Providers**: Tracer, Meter, Logger providers
- **Usage**: Configure at application startup

#### Collector
- **Purpose**: Receive, process, export telemetry
- **Deployment**: Agent or gateway mode
- **Features**: Batching, retry, filtering
- **Usage**: Optional but recommended

## Installation

### Python
```bash
# Core packages
pip install opentelemetry-api
pip install opentelemetry-sdk

# Auto-instrumentation
pip install opentelemetry-instrumentation

# Exporters
pip install opentelemetry-exporter-otlp
pip install opentelemetry-exporter-prometheus
pip install opentelemetry-exporter-jaeger

# Specific instrumentations
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-sqlalchemy
```

### Node.js
```bash
# Core packages
npm install @opentelemetry/api
npm install @opentelemetry/sdk-node

# Auto-instrumentation
npm install @opentelemetry/auto-instrumentations-node

# Exporters
npm install @opentelemetry/exporter-trace-otlp-grpc
npm install @opentelemetry/exporter-metrics-otlp-grpc
npm install @opentelemetry/exporter-prometheus

# Specific instrumentations
npm install @opentelemetry/instrumentation-http
npm install @opentelemetry/instrumentation-express
npm install @opentelemetry/instrumentation-mongodb
```

### Go
```bash
# Core packages
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/sdk

# Exporters
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc
go get go.opentelemetry.io/otel/exporters/prometheus

# Instrumentation libraries
go get go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp
go get go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc
```

### Java
```xml
<!-- Maven dependencies -->
<dependencies>
  <!-- Core -->
  <dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-api</artifactId>
    <version>1.32.0</version>
  </dependency>
  <dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-sdk</artifactId>
    <version>1.32.0</version>
  </dependency>

  <!-- Auto-instrumentation agent -->
  <dependency>
    <groupId>io.opentelemetry.javaagent</groupId>
    <artifactId>opentelemetry-javaagent</artifactId>
    <version>1.32.0</version>
  </dependency>

  <!-- Exporters -->
  <dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
    <version>1.32.0</version>
  </dependency>
</dependencies>
```

## Instrumentation

### Auto-Instrumentation

#### Python
```python
# Run with auto-instrumentation
# opentelemetry-instrument --traces_exporter otlp python app.py

# Or programmatic auto-instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

#### Node.js
```javascript
// Auto-instrumentation (before other imports)
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter(),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

#### Java (Agent)
```bash
# Download agent
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# Run with agent
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=payment-api \
     -Dotel.traces.exporter=otlp \
     -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
     -jar app.jar
```

### Manual Instrumentation

#### Python
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Get tracer
tracer = trace.get_tracer(__name__)

# Create spans
@app.route('/users/<user_id>')
def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("http.method", "GET")

        user = fetch_user(user_id)

        span.add_event("user_fetched", {
            "user.email": user.email
        })

        return jsonify(user)

def fetch_user(user_id):
    with tracer.start_as_current_span("db.query") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.statement", "SELECT * FROM users WHERE id = $1")

        result = db.query(user_id)
        return result
```

#### Go
```go
import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/trace"
)

func getUser(ctx context.Context, userID string) (*User, error) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "getUser")
    defer span.End()

    span.SetAttributes(
        attribute.String("user.id", userID),
        attribute.String("http.method", "GET"),
    )

    user, err := fetchUser(ctx, userID)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return nil, err
    }

    span.AddEvent("user_fetched", trace.WithAttributes(
        attribute.String("user.email", user.Email),
    ))

    return user, nil
}

func fetchUser(ctx context.Context, userID string) (*User, error) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "db.query")
    defer span.End()

    span.SetAttributes(
        attribute.String("db.system", "postgresql"),
        attribute.String("db.statement", "SELECT * FROM users WHERE id = $1"),
    )

    // Query database
    user, err := db.QueryUser(ctx, userID)
    return user, err
}
```

## Semantic Conventions

### HTTP Attributes
```python
span.set_attribute("http.method", "POST")
span.set_attribute("http.url", "https://api.example.com/users")
span.set_attribute("http.target", "/users")
span.set_attribute("http.status_code", 200)
span.set_attribute("http.request_content_length", 1234)
span.set_attribute("http.response_content_length", 5678)
span.set_attribute("http.route", "/users/:id")
span.set_attribute("http.scheme", "https")
span.set_attribute("http.flavor", "1.1")
```

### Database Attributes
```python
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.connection_string", "postgresql://localhost:5432")
span.set_attribute("db.user", "app_user")
span.set_attribute("db.name", "users_db")
span.set_attribute("db.statement", "SELECT * FROM users WHERE id = $1")
span.set_attribute("db.operation", "SELECT")
span.set_attribute("db.sql.table", "users")
```

### RPC Attributes
```python
span.set_attribute("rpc.system", "grpc")
span.set_attribute("rpc.service", "UserService")
span.set_attribute("rpc.method", "GetUser")
span.set_attribute("rpc.grpc.status_code", 0)
```

### Messaging Attributes
```python
span.set_attribute("messaging.system", "kafka")
span.set_attribute("messaging.destination", "orders")
span.set_attribute("messaging.destination_kind", "topic")
span.set_attribute("messaging.operation", "publish")
span.set_attribute("messaging.message_id", "msg_12345")
span.set_attribute("messaging.kafka.partition", 3)
```

## OpenTelemetry Collector

### Deployment Modes

#### Agent Mode
```yaml
# Runs on each host, collects local telemetry
Deployment: DaemonSet in Kubernetes, systemd on VMs
Purpose: Local collection and forwarding
Configuration: Simple, forward to gateway
```

#### Gateway Mode
```yaml
# Centralized collector cluster
Deployment: Deployment/Service in Kubernetes
Purpose: Processing, batching, routing
Configuration: Complex, multiple exporters
```

### Collector Configuration

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          scrape_interval: 10s
          static_configs:
            - targets: ['localhost:8888']

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

  memory_limiter:
    check_interval: 1s
    limit_mib: 512

  resourcedetection:
    detectors: [env, system, docker]

  attributes:
    actions:
      - key: environment
        value: production
        action: insert

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

  prometheus:
    endpoint: "0.0.0.0:8889"

  logging:
    loglevel: debug

  otlp/honeycomb:
    endpoint: api.honeycomb.io:443
    headers:
      x-honeycomb-team: YOUR_API_KEY

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resourcedetection]
      exporters: [otlp/jaeger, logging]

    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus, logging]

  extensions: [health_check, pprof]
```

### Running Collector

```bash
# Docker
docker run -p 4317:4317 -p 4318:4318 \
  -v $(pwd)/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
  otel/opentelemetry-collector:latest \
  --config=/etc/otel-collector-config.yaml

# Kubernetes
kubectl apply -f https://github.com/open-telemetry/opentelemetry-collector/releases/latest/download/otel-collector.yaml
```

## Context Propagation

### W3C Trace Context
```python
# Extract context from incoming request
from opentelemetry import trace
from opentelemetry.propagate import extract

context = extract(request.headers)

with tracer.start_as_current_span("process_request", context=context):
    # Process request
    pass

# Inject context into outgoing request
from opentelemetry.propagate import inject

headers = {}
inject(headers)

requests.post(url, headers=headers)
# Headers now include: traceparent, tracestate
```

### Baggage
```python
from opentelemetry import baggage

# Set baggage (propagated to all child spans)
ctx = baggage.set_baggage("user.id", "12345")
ctx = baggage.set_baggage("tenant.id", "acme", ctx)

# Get baggage (available in all downstream services)
user_id = baggage.get_baggage("user.id")
tenant_id = baggage.get_baggage("tenant.id")
```

## Sampling

### Configuration
```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
    ALWAYS_OFF
)

# Always sample (100%)
provider = TracerProvider(sampler=ALWAYS_ON)

# Never sample (0%)
provider = TracerProvider(sampler=ALWAYS_OFF)

# Probability sampling (10%)
provider = TracerProvider(sampler=TraceIdRatioBased(0.1))

# Parent-based sampling (follow parent's decision)
provider = TracerProvider(
    sampler=ParentBased(
        root=TraceIdRatioBased(0.1),
        remote_parent_sampled=ALWAYS_ON,
        remote_parent_not_sampled=ALWAYS_OFF
    )
)
```

### Custom Sampler
```python
from opentelemetry.sdk.trace.sampling import Sampler, Decision

class CustomSampler(Sampler):
    def should_sample(self, context, trace_id, name, attributes=None, links=None):
        # Always sample errors
        if attributes and attributes.get("http.status_code", 0) >= 500:
            return Decision.RECORD_AND_SAMPLE

        # Always sample slow requests
        if attributes and attributes.get("duration", 0) > 1000:
            return Decision.RECORD_AND_SAMPLE

        # Sample 1% of normal requests
        if trace_id % 100 == 0:
            return Decision.RECORD_AND_SAMPLE

        return Decision.DROP

provider = TracerProvider(sampler=CustomSampler())
```

## Metrics with OpenTelemetry

### Counter
```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# Counter
requests_counter = meter.create_counter(
    "http.requests",
    description="Total HTTP requests",
    unit="1"
)

requests_counter.add(1, {"method": "GET", "endpoint": "/users"})
```

### Histogram
```python
# Histogram (for latency, size, etc.)
request_duration = meter.create_histogram(
    "http.request.duration",
    description="HTTP request duration",
    unit="ms"
)

request_duration.record(245, {"method": "POST", "endpoint": "/orders"})
```

### UpDownCounter
```python
# UpDownCounter (can go up or down)
active_connections = meter.create_up_down_counter(
    "http.active_connections",
    description="Active HTTP connections",
    unit="1"
)

active_connections.add(1)  # Connection opened
active_connections.add(-1)  # Connection closed
```

### Observable Gauge
```python
# Asynchronous gauge
def get_memory_usage():
    import psutil
    return psutil.virtual_memory().percent

memory_usage = meter.create_observable_gauge(
    "system.memory.usage",
    [get_memory_usage],
    description="System memory usage",
    unit="%"
)
```

## Resource Detection

### Automatic Resource Detection
```python
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

# Automatic resource detection
resource = Resource.create({
    "service.name": "payment-api",
    "service.version": "1.2.3",
    "deployment.environment": "production"
})

provider = TracerProvider(resource=resource)
```

### Available Resource Detectors
```python
from opentelemetry.sdk.resources import (
    ProcessResourceDetector,
    OTELResourceDetector,
    Resource
)

# Detect from environment and process
resource = Resource.create().merge(
    ProcessResourceDetector().detect()
).merge(
    OTELResourceDetector().detect()
)

# Environment variables:
# OTEL_RESOURCE_ATTRIBUTES="service.name=api,service.version=1.0"
# OTEL_SERVICE_NAME="payment-api"
```

## Best Practices

### Do's
1. **Use semantic conventions**
2. **Enable auto-instrumentation first**
3. **Add manual spans for critical paths**
4. **Include meaningful attributes**
5. **Use appropriate sampling**
6. **Propagate context correctly**
7. **Set resource attributes**
8. **Use OTLP when possible**

### Don'ts
1. **Don't create too many spans**
2. **Don't add high-cardinality attributes**
3. **Don't sample too aggressively**
4. **Don't forget to end spans**
5. **Don't log sensitive data**
6. **Don't ignore errors**
7. **Don't mix instrumentation approaches**

## Migration from Vendor SDKs

### From Datadog
```python
# Before (Datadog)
from ddtrace import tracer

@tracer.wrap('process_payment')
def process_payment():
    pass

# After (OpenTelemetry)
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span('process_payment')
def process_payment():
    pass
```

### From Jaeger
```python
# Before (Jaeger)
from jaeger_client import Config

config = Config(config={}, service_name='api')
tracer = config.initialize_tracer()

# After (OpenTelemetry with Jaeger exporter)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger import JaegerExporter

provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)
```

## OpenTelemetry Operator (Kubernetes)

### Installation
```bash
# Install cert-manager (prerequisite)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Install OpenTelemetry Operator
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

### Auto-Instrumentation
```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: my-instrumentation
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
  sampler:
    type: parentbased_traceidratio
    argument: "0.1"

  python:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:latest

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        instrumentation.opentelemetry.io/inject-python: "true"
    spec:
      containers:
      - name: app
        image: my-python-app:latest
```

## Troubleshooting

### Common Issues
```yaml
Issue: No traces appearing

Checks:
  1. Is instrumentation enabled?
  2. Is exporter configured correctly?
  3. Is sampling preventing traces?
  4. Is collector reachable?
  5. Check logs for errors

Solution:
  - Enable debug logging
  - Use ALWAYS_ON sampler for testing
  - Test exporter connection
  - Check collector logs
```

## Resources

- Official Docs: https://opentelemetry.io
- Specification: https://github.com/open-telemetry/opentelemetry-specification
- Registry: https://opentelemetry.io/registry/
- Collector: https://github.com/open-telemetry/opentelemetry-collector
