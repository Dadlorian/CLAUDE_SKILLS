# Distributed Tracing Reference

## Overview

Distributed tracing tracks requests as they flow through multiple services in a distributed system, providing visibility into latency, dependencies, and performance bottlenecks.

## Core Concepts

### Trace
- **Definition**: Complete journey of a request through system
- **Composition**: Collection of spans forming a tree structure
- **Identifier**: Unique trace ID
- **Duration**: Start of first span to end of last span
- **Purpose**: End-to-end request visibility

### Span
- **Definition**: Single operation within a trace
- **Components**:
  - Span ID (unique identifier)
  - Trace ID (parent trace)
  - Parent Span ID (optional)
  - Operation name
  - Start timestamp
  - Duration
  - Tags/Attributes
  - Events
  - Status
- **Purpose**: Represents a unit of work

### Context Propagation
- **Definition**: Passing trace context across service boundaries
- **Methods**: HTTP headers, message metadata, RPC context
- **Standard**: W3C Trace Context
- **Headers**:
  - `traceparent`: Version, trace-id, parent-id, flags
  - `tracestate`: Vendor-specific data
- **Purpose**: Maintain trace continuity

## Trace Structure

### Example Trace Tree

```
Trace: e4a8c8e4-7b2d-4c3f-9e1a-2d5f6c8e9a1b
├─ Span: API Gateway (200ms)
   ├─ Span: Auth Service (50ms)
   │  └─ Span: Database Query (30ms)
   ├─ Span: User Service (80ms)
   │  ├─ Span: Database Query (40ms)
   │  └─ Span: Cache Lookup (10ms)
   └─ Span: Order Service (100ms)
      ├─ Span: Database Query (60ms)
      └─ Span: Payment Service (70ms)
         └─ Span: External API Call (50ms)
```

### Critical Path
- Longest path from root to leaf
- Determines total request latency
- Focus optimization efforts here

## Span Attributes

### Standard Attributes (OpenTelemetry Semantic Conventions)

#### HTTP
```json
{
  "http.method": "GET",
  "http.url": "https://api.example.com/users/123",
  "http.status_code": 200,
  "http.request_content_length": 0,
  "http.response_content_length": 1234,
  "http.user_agent": "Mozilla/5.0...",
  "http.route": "/users/:id"
}
```

#### Database
```json
{
  "db.system": "postgresql",
  "db.name": "users_db",
  "db.statement": "SELECT * FROM users WHERE id = $1",
  "db.operation": "SELECT",
  "db.connection_string": "postgresql://localhost:5432"
}
```

#### RPC
```json
{
  "rpc.system": "grpc",
  "rpc.service": "UserService",
  "rpc.method": "GetUser",
  "rpc.grpc.status_code": 0
}
```

#### Messaging
```json
{
  "messaging.system": "kafka",
  "messaging.destination": "orders",
  "messaging.operation": "publish",
  "messaging.message_id": "msg_123"
}
```

### Custom Attributes
```json
{
  "user.id": "user_12345",
  "tenant.id": "tenant_67890",
  "feature.flag": "new_checkout",
  "cache.hit": true,
  "retry.count": 2
}
```

## Span Events

### Purpose
- Mark significant moments within a span
- Add contextual information at specific timestamps
- Track retries, errors, cache hits, etc.

### Example
```python
span.add_event(
    "cache_miss",
    attributes={
        "cache.key": "user:12345",
        "cache.ttl": 3600
    }
)

span.add_event(
    "retry_attempt",
    attributes={
        "retry.count": 2,
        "retry.reason": "connection_timeout"
    }
)

span.add_event(
    "exception",
    attributes={
        "exception.type": "ValueError",
        "exception.message": "Invalid user ID"
    }
)
```

## Sampling Strategies

### Head-Based Sampling
- **Decision**: Made at trace start
- **Methods**:
  - Always sample (100%)
  - Never sample (0%)
  - Probability (e.g., 10%)
  - Rate limiting (N traces/second)
- **Pros**: Low overhead, simple
- **Cons**: May miss important traces

### Tail-Based Sampling
- **Decision**: Made after trace completes
- **Criteria**:
  - Trace duration > threshold
  - Contains errors
  - Specific attributes present
  - Random percentage
- **Pros**: Intelligent sampling, keeps important traces
- **Cons**: Higher overhead, requires buffering

### Sampling Algorithms

#### Probability Sampling
```python
import random

def should_sample(probability=0.1):
    return random.random() < probability

# Sample 10% of traces
if should_sample(0.1):
    start_trace()
```

#### Rate-Limited Sampling
```python
from collections import deque
import time

class RateLimitSampler:
    def __init__(self, max_per_second):
        self.max_per_second = max_per_second
        self.recent_samples = deque()

    def should_sample(self):
        now = time.time()

        # Remove old samples
        while self.recent_samples and now - self.recent_samples[0] > 1.0:
            self.recent_samples.popleft()

        # Check rate limit
        if len(self.recent_samples) < self.max_per_second:
            self.recent_samples.append(now)
            return True
        return False
```

#### Priority Sampling
```python
def should_sample(span):
    # Always sample errors
    if span.status == "error":
        return True

    # Always sample slow requests
    if span.duration > 1000:  # > 1 second
        return True

    # Sample 1% of normal requests
    return random.random() < 0.01
```

## W3C Trace Context

### Traceparent Header

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

Format: {version}-{trace-id}-{parent-id}-{trace-flags}
  version:     00
  trace-id:    4bf92f3577b34da6a3ce929d0e0e4736 (16 bytes, 32 hex chars)
  parent-id:   00f067aa0ba902b7 (8 bytes, 16 hex chars)
  trace-flags: 01 (sampled)
```

### Tracestate Header

```
tracestate: vendorA=value1,vendorB=value2

Purpose: Vendor-specific trace data
Example: congo=t61rcWkgMzE,rojo=00f067aa0ba902b7
```

### Implementation
```python
# Extract trace context from incoming request
def extract_trace_context(headers):
    traceparent = headers.get('traceparent')
    if not traceparent:
        return None

    parts = traceparent.split('-')
    return {
        'version': parts[0],
        'trace_id': parts[1],
        'parent_id': parts[2],
        'flags': parts[3]
    }

# Inject trace context into outgoing request
def inject_trace_context(headers, context):
    headers['traceparent'] = f"00-{context['trace_id']}-{context['span_id']}-{context['flags']}"
    if context.get('tracestate'):
        headers['tracestate'] = context['tracestate']
```

## Instrumentation Examples

### Python (OpenTelemetry)

```python
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Auto-instrumentation
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Manual instrumentation
tracer = trace.get_tracer(__name__)

@app.route('/users/<user_id>')
def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)

        # Database query span
        with tracer.start_as_current_span("db.query") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.statement", "SELECT * FROM users WHERE id = $1")
            user = db.query(user_id)

        # External API call span
        with tracer.start_as_current_span("external.api") as api_span:
            api_span.set_attribute("http.url", "https://api.example.com/profile")
            profile = requests.get(f"https://api.example.com/profile/{user_id}")

        return jsonify(user)
```

### Go (OpenTelemetry)

```go
import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

func getUser(ctx context.Context, userID string) (*User, error) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "getUser")
    defer span.End()

    span.SetAttributes(attribute.String("user.id", userID))

    // Database query
    ctx, dbSpan := tracer.Start(ctx, "db.query")
    dbSpan.SetAttributes(
        attribute.String("db.system", "postgresql"),
        attribute.String("db.statement", "SELECT * FROM users WHERE id = $1"),
    )
    user, err := db.QueryUser(ctx, userID)
    dbSpan.End()

    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "database query failed")
        return nil, err
    }

    return user, nil
}
```

### Node.js (OpenTelemetry)

```javascript
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('user-service');

async function getUser(userId) {
  return tracer.startActiveSpan('getUser', async (span) => {
    span.setAttribute('user.id', userId);

    try {
      // Database query
      const user = await tracer.startActiveSpan('db.query', async (dbSpan) => {
        dbSpan.setAttribute('db.system', 'postgresql');
        dbSpan.setAttribute('db.statement', 'SELECT * FROM users WHERE id = $1');
        const result = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
        dbSpan.end();
        return result.rows[0];
      });

      span.setStatus({ code: SpanStatusCode.OK });
      return user;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### Java (OpenTelemetry)

```java
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

public class UserService {
    private final Tracer tracer;

    public User getUser(String userId) {
        Span span = tracer.spanBuilder("getUser").startSpan();
        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("user.id", userId);

            // Database query
            Span dbSpan = tracer.spanBuilder("db.query")
                .setAttribute("db.system", "postgresql")
                .setAttribute("db.statement", "SELECT * FROM users WHERE id = ?")
                .startSpan();

            try (Scope dbScope = dbSpan.makeCurrent()) {
                User user = db.queryUser(userId);
                return user;
            } finally {
                dbSpan.end();
            }
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, "Failed to get user");
            throw e;
        } finally {
            span.end();
        }
    }
}
```

## Common Patterns

### Database Tracing
```python
def trace_database_query(query, params):
    with tracer.start_as_current_span("db.query") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.statement", query)
        span.set_attribute("db.operation", query.split()[0])  # SELECT, INSERT, etc.

        start_time = time.time()
        result = db.execute(query, params)
        duration = (time.time() - start_time) * 1000

        span.set_attribute("db.rows_affected", len(result))
        span.add_event("query_completed", {"duration_ms": duration})

        return result
```

### HTTP Client Tracing
```python
def trace_http_request(method, url, **kwargs):
    with tracer.start_as_current_span("http.request") as span:
        span.set_attribute("http.method", method)
        span.set_attribute("http.url", url)

        # Inject trace context
        headers = kwargs.get('headers', {})
        inject_trace_context(headers, get_current_context())
        kwargs['headers'] = headers

        response = requests.request(method, url, **kwargs)

        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.response_content_length", len(response.content))

        if response.status_code >= 400:
            span.set_status(Status(StatusCode.ERROR))

        return response
```

### Async Operations
```python
async def trace_async_operation():
    with tracer.start_as_current_span("async.operation") as span:
        # Start parallel operations
        span.add_event("parallel_operations_started")

        results = await asyncio.gather(
            fetch_user_data(user_id),
            fetch_order_data(user_id),
            fetch_payment_data(user_id)
        )

        span.add_event("parallel_operations_completed")
        return results
```

### Message Queue Tracing
```python
# Producer
def send_message(queue, message):
    with tracer.start_as_current_span("message.send") as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.destination", queue)

        # Inject trace context into message
        message['trace_context'] = get_current_context()

        producer.send(queue, message)

# Consumer
def process_message(message):
    # Extract trace context from message
    context = message.get('trace_context')
    with tracer.start_as_current_span("message.process", context=context) as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.operation", "process")

        handle_message(message)
```

## Performance Analysis

### Identifying Bottlenecks
```
1. Find slow traces (p95, p99 latency)
2. Examine critical path
3. Identify longest span
4. Check for:
   - Slow database queries
   - N+1 query problems
   - Slow external APIs
   - Sequential operations that could be parallel
```

### Service Dependencies
```
1. Visualize service dependency graph
2. Identify:
   - Critical dependencies (single points of failure)
   - Chatty services (too many calls)
   - Deep call chains
   - Circular dependencies
```

### Error Analysis
```
1. Filter traces with errors
2. Group by error type
3. Analyze error patterns:
   - Which service fails most?
   - Cascading failures?
   - Timeout patterns?
```

## Best Practices

### Do's
1. **Include meaningful operation names**
   ```python
   # Good
   span_name = "GET /users/:id"
   span_name = "db.query.users.select"

   # Bad
   span_name = "request"
   span_name = "operation"
   ```

2. **Add relevant attributes**
   ```python
   span.set_attribute("user.id", user_id)
   span.set_attribute("http.status_code", 200)
   span.set_attribute("cache.hit", True)
   ```

3. **Record exceptions**
   ```python
   try:
       process_request()
   except Exception as e:
       span.record_exception(e)
       span.set_status(Status(StatusCode.ERROR))
       raise
   ```

4. **Use appropriate sampling**
   ```python
   # Always trace errors and slow requests
   if is_error or duration > threshold:
       force_sampling = True
   ```

### Don'ts
1. **Don't create too many spans** (overhead)
2. **Don't include PII in attributes**
3. **Don't sample too aggressively** (miss important data)
4. **Don't forget to end spans**
5. **Don't ignore context propagation**

## Tools and Platforms

### Open Source
- **Jaeger**: Uber's distributed tracing
- **Zipkin**: Twitter's distributed tracing
- **OpenTelemetry**: Vendor-neutral standard
- **SkyWalking**: APM and observability

### Commercial
- **Datadog APM**: Full-stack APM
- **New Relic**: Application monitoring
- **Dynatrace**: AI-powered APM
- **Honeycomb**: Observability platform

### Cloud Native
- **AWS X-Ray**: AWS distributed tracing
- **Google Cloud Trace**: GCP tracing
- **Azure Application Insights**: Azure APM

## Advanced Topics

### Baggage
- Cross-cutting concerns propagated with trace
- Examples: user ID, tenant ID, feature flags
- Accessible to all spans in trace

```python
from opentelemetry import baggage

# Set baggage
baggage.set_baggage("user.id", "12345")
baggage.set_baggage("tenant.id", "acme-corp")

# Get baggage (available in all downstream spans)
user_id = baggage.get_baggage("user.id")
```

### Exemplars
- Link metrics to traces
- Example: "This high latency metric came from trace X"
- Enables drill-down from metrics to traces

### Trace-Based Testing
- Capture traces in test environments
- Assert on trace structure
- Verify expected spans present
- Check latency SLOs

## Metrics from Traces

### RED Metrics
```
# Rate (requests per second)
rate(span_count[5m]) by (service)

# Errors (error percentage)
rate(span_errors[5m]) / rate(span_count[5m])

# Duration (latency percentiles)
histogram_quantile(0.95, span_duration_bucket)
```

### Service-Level Metrics
- Request rate per endpoint
- Error rate per endpoint
- Latency distribution per endpoint
- Dependency call counts

## Cost Optimization

### Reduce Data Volume
1. **Sampling**: Sample 1-10% of successful requests
2. **Tail-based sampling**: Keep all errors, slow requests
3. **TTL**: Shorter retention for normal traces
4. **Attribute filtering**: Remove high-cardinality attributes

### Optimize Storage
1. **Compression**: Enable trace compression
2. **Archival**: Move old traces to cold storage
3. **Downsampling**: Reduce resolution for old traces
4. **Deletion**: Auto-delete after retention period
