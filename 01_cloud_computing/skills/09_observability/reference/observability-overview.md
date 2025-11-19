# Observability Overview

## Introduction

Observability is the ability to understand the internal state of a system by examining its external outputs. It enables teams to ask arbitrary questions about system behavior without needing to predict those questions in advance.

## Three Pillars of Observability

### 1. Metrics
- **Definition**: Numeric measurements aggregated over time
- **Characteristics**:
  - Time-series data (timestamp + value)
  - Cheap to collect and store
  - Excellent for trends and alerts
  - Limited cardinality
- **Examples**: Request rate, error rate, latency, CPU usage
- **Use Cases**: Dashboards, alerting, capacity planning

### 2. Logs
- **Definition**: Discrete events with timestamp and context
- **Characteristics**:
  - High volume, detailed information
  - Expensive to store at scale
  - Rich context per event
  - Great for debugging
- **Examples**: Application logs, access logs, error messages
- **Use Cases**: Debugging, audit trails, security analysis

### 3. Traces
- **Definition**: Journey of a request through distributed systems
- **Characteristics**:
  - Shows causality and relationships
  - Sampling usually required
  - Moderate storage cost
  - Critical for microservices
- **Examples**: Distributed traces, transaction flows, service dependencies
- **Use Cases**: Performance analysis, bottleneck identification, dependency mapping

## Monitoring vs Observability

### Traditional Monitoring
- Predefined dashboards and alerts
- Known-unknowns (anticipated failure modes)
- Static thresholds
- System-centric view
- "Is the system up?"

### Modern Observability
- Exploratory analysis
- Unknown-unknowns (unexpected issues)
- Dynamic baselines and anomaly detection
- User-centric view
- "Why is the system behaving this way?"

## Key Concepts

### Cardinality
- Number of unique combinations of label/tag values
- High cardinality = more storage/query cost
- Example: userID (millions) vs region (tens)
- Balance granularity with cost

### Context Propagation
- Passing trace context across service boundaries
- W3C Trace Context standard (traceparent, tracestate)
- Enables correlation across pillars
- Critical for distributed systems

### Sampling
- Recording subset of telemetry data
- Head-based: Decision at trace start
- Tail-based: Decision after trace completes
- Trade-offs: cost vs completeness

### Aggregation
- Combining data points over time/dimensions
- Metrics: Sum, average, percentiles, histograms
- Logs: Counting patterns, grouping errors
- Traces: Service-level statistics

## Observability Methods

### RED Method (Services)
- **Rate**: Requests per second
- **Errors**: Number of failed requests
- **Duration**: Time to process requests
- Best for request-driven services

### USE Method (Resources)
- **Utilization**: Percentage of resource used
- **Saturation**: Queue depth, wait time
- **Errors**: Error count
- Best for infrastructure resources

### Four Golden Signals (Google SRE)
- **Latency**: Response time
- **Traffic**: Request volume
- **Errors**: Error rate
- **Saturation**: Resource fullness
- Comprehensive service health view

## Observability Maturity Levels

### Level 1: Basic Monitoring
- Infrastructure metrics (CPU, memory, disk)
- Simple uptime checks
- Basic alerting
- Manual log searching

### Level 2: Application Monitoring
- Application-level metrics
- Structured logging
- APM tools deployed
- Service dashboards

### Level 3: Full Observability
- Distributed tracing implemented
- Metrics, logs, traces correlated
- SLIs/SLOs defined
- Comprehensive dashboards
- Advanced alerting

### Level 4: Observability-Driven Development
- Instrumentation in code reviews
- Observability testing in CI/CD
- Chaos engineering integrated
- Automatic anomaly detection
- AI-assisted incident response

## Benefits of Observability

### For Developers
- Faster debugging and root cause analysis
- Understanding of system behavior in production
- Performance optimization insights
- Confidence in deployments

### For Operations
- Proactive issue detection
- Reduced MTTR (Mean Time To Resolution)
- Capacity planning data
- Clear service health picture

### For Business
- Customer experience insights
- SLA compliance tracking
- Cost optimization opportunities
- Data-driven decision making

## Challenges

### Technical Challenges
- **Scale**: High-cardinality data at massive volume
- **Cost**: Storage and processing expenses
- **Complexity**: Multiple tools and platforms
- **Integration**: Correlating data across pillars
- **Performance**: Instrumentation overhead

### Organizational Challenges
- **Culture**: Shifting from reactive to proactive
- **Skills**: Learning new tools and practices
- **Standardization**: Consistent instrumentation
- **Tool Sprawl**: Too many observability tools
- **Alert Fatigue**: Too many noisy alerts

## Best Practices

### Instrumentation
1. Instrument at development time, not after production issues
2. Use semantic conventions for consistency
3. Include context (trace IDs, user IDs, request IDs)
4. Balance detail with performance impact
5. Make instrumentation code maintainable

### Data Management
1. Define retention policies based on value
2. Use appropriate sampling for high-volume data
3. Archive historical data for compliance
4. Monitor observability system costs
5. Implement data lifecycle policies

### Analysis
1. Build dashboards for specific audiences
2. Create runbooks for common alerts
3. Use traces to understand request flow
4. Correlate metrics, logs, and traces
5. Document investigation procedures

### Culture
1. Make observability data accessible to all teams
2. Include observability in definition of done
3. Review observability during retrospectives
4. Share insights across teams
5. Invest in observability training

## Observability Stack Patterns

### Open Source Stack
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK/EFK Stack
- **Traces**: Jaeger or Zipkin
- **Collection**: OpenTelemetry
- **Pros**: No vendor lock-in, customizable
- **Cons**: More operational overhead

### Commercial SaaS Stack
- **All-in-one**: Datadog, New Relic, Dynatrace
- **Pros**: Easy setup, managed service, AI features
- **Cons**: Cost, vendor lock-in, data egress

### Hybrid Stack
- **Metrics**: Prometheus + Grafana Cloud
- **Logs**: Cloud-native logging (CloudWatch, Stackdriver)
- **Traces**: Managed Jaeger or APM SaaS
- **Collection**: OpenTelemetry
- **Pros**: Balance of control and convenience
- **Cons**: Integration complexity

### Cloud-Native Stack
- **AWS**: CloudWatch, X-Ray, Container Insights
- **Azure**: Azure Monitor, Application Insights
- **GCP**: Cloud Monitoring, Cloud Logging, Cloud Trace
- **Pros**: Deep cloud integration, simple setup
- **Cons**: Cloud vendor lock-in, limited customization

## Observability for Different Architectures

### Monoliths
- Application-level metrics and logging
- APM for transaction tracing
- Database query monitoring
- Infrastructure monitoring
- Simpler correlation (single process)

### Microservices
- Distributed tracing essential
- Service mesh observability
- Cross-service correlation
- Service dependency mapping
- Higher instrumentation complexity

### Serverless
- Cold start monitoring
- Function-level metrics
- Log aggregation across invocations
- Distributed tracing for workflows
- Limited direct host access

### Container Orchestration (Kubernetes)
- Container metrics (cAdvisor)
- Cluster state metrics (kube-state-metrics)
- Pod and node monitoring
- Service discovery integration
- Multiple layers of abstraction

## The Future of Observability

### Emerging Trends
- **Unified Telemetry**: Single pipeline for all data types
- **AI/ML Integration**: Automatic anomaly detection, root cause analysis
- **Continuous Profiling**: Always-on performance profiling
- **Observability as Code**: Version-controlled instrumentation
- **Privacy-Preserving**: Observability without PII exposure
- **Edge Observability**: Monitoring at edge locations
- **eBPF-based**: Kernel-level observability without code changes

### OpenTelemetry Impact
- Vendor-neutral instrumentation standard
- Unified SDKs across languages
- Flexible backend selection
- Community-driven innovation
- Reducing instrumentation fragmentation

## Key Metrics

### Observability System Health
- **Data Ingestion Rate**: Events/sec processed
- **Storage Growth**: GB/day added
- **Query Performance**: p95/p99 query latency
- **System Availability**: Uptime of observability platform
- **Cost per GB**: Efficiency metric
- **Alert Accuracy**: True positive rate

## Resources

### Standards
- OpenTelemetry (OTEL)
- W3C Trace Context
- Prometheus exposition format
- Common Log Format (CLF)

### Books
- "Observability Engineering" by Charity Majors, Liz Fong-Jones, George Miranda
- "Distributed Systems Observability" by Cindy Sridharan
- "Site Reliability Engineering" by Google
- "The Art of Monitoring" by James Turnbull

### Communities
- CNCF Observability TAG
- OpenTelemetry community
- Prometheus community
- SRE community

## Practical Implementation Examples

### Example 1: OpenTelemetry Instrumentation (Python Flask)

```python
from flask import Flask, request
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import logging
import time

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://collector:4317"),
    export_interval_millis=30000
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Create custom metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="s"
)

active_connections = meter.create_up_down_counter(
    name="active_connections",
    description="Number of active connections",
    unit="1"
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - trace_id=%(otelTraceID)s span_id=%(otelSpanID)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Auto-instrument Flask and requests library
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.before_request
def before_request():
    """Track request start and active connections"""
    request.start_time = time.time()
    active_connections.add(1, {"method": request.method, "endpoint": request.endpoint})

@app.after_request
def after_request(response):
    """Record metrics and log after each request"""
    # Calculate duration
    duration = time.time() - request.start_time

    # Get trace context for correlation
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

    # Record metrics
    labels = {
        "method": request.method,
        "endpoint": request.endpoint or "unknown",
        "status": str(response.status_code)
    }

    request_counter.add(1, labels)
    request_duration.record(duration, labels)
    active_connections.add(-1, {"method": request.method, "endpoint": request.endpoint})

    # Structured logging with trace context
    logger.info(
        f"Request completed",
        extra={
            "otelTraceID": trace_id,
            "otelSpanID": span_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": duration,
            "user_agent": request.user_agent.string
        }
    )

    return response

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """Example endpoint with custom span attributes"""
    # Add custom attributes to current span
    span = trace.get_current_span()
    span.set_attribute("user.id", user_id)
    span.set_attribute("user.tier", "premium")

    # Create child span for database operation
    with tracer.start_as_current_span("database.query") as db_span:
        db_span.set_attribute("db.system", "postgresql")
        db_span.set_attribute("db.statement", f"SELECT * FROM users WHERE id = {user_id}")
        db_span.set_attribute("db.name", "production")

        # Simulate database query
        time.sleep(0.05)

        logger.info(f"Fetched user {user_id} from database")

    # Create child span for cache operation
    with tracer.start_as_current_span("cache.get") as cache_span:
        cache_span.set_attribute("cache.system", "redis")
        cache_span.set_attribute("cache.key", f"user:{user_id}")

        # Simulate cache lookup
        time.sleep(0.01)

    return {"user_id": user_id, "name": "John Doe", "tier": "premium"}

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Example with error tracking"""
    span = trace.get_current_span()

    try:
        order_data = request.get_json()
        span.set_attribute("order.items", len(order_data.get('items', [])))
        span.set_attribute("order.total", order_data.get('total', 0))

        # Simulate order processing
        if order_data.get('total', 0) > 10000:
            raise ValueError("Order total exceeds limit")

        logger.info("Order created successfully", extra={"order_id": "12345"})
        return {"order_id": "12345", "status": "created"}

    except ValueError as e:
        # Record exception in span
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

        logger.error(f"Order creation failed: {str(e)}")
        return {"error": str(e)}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Example 2: Prometheus Metrics and Queries

```python
# Python application with Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, start_http_server
import time
import random

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['service']
)

cache_hit_rate = Summary(
    'cache_hit_rate',
    'Cache hit rate percentage',
    ['cache_type']
)

app_info = Info(
    'app_info',
    'Application information'
)

# Set application info
app_info.info({
    'version': '1.2.3',
    'environment': 'production',
    'region': 'us-east-1'
})

def process_request(method, endpoint):
    """Simulate request processing with metrics"""
    # Track active connections
    active_connections.labels(service='api').inc()

    # Start timing
    start_time = time.time()

    try:
        # Simulate processing
        time.sleep(random.uniform(0.01, 0.5))
        status = random.choice([200, 200, 200, 200, 404, 500])  # Mostly 200s

        # Record metrics
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

    finally:
        # Record duration
        duration = time.time() - start_time
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        # Decrease active connections
        active_connections.labels(service='api').dec()

    # Simulate cache operations
    cache_hit = random.choice([True, True, True, False])  # 75% hit rate
    cache_hit_rate.labels(cache_type='redis').observe(75 if cache_hit else 0)

# Start Prometheus metrics server
start_http_server(8000)

# Simulate traffic
while True:
    process_request('GET', '/api/users')
    process_request('POST', '/api/orders')
    time.sleep(0.1)
```

**Prometheus Query Examples:**

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate percentage
(rate(http_requests_total{status=~"5.."}[5m]) /
 rate(http_requests_total[5m])) * 100

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 99th percentile latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Average request duration by endpoint
avg(rate(http_request_duration_seconds_sum[5m]) /
    rate(http_request_duration_seconds_count[5m]))
by (endpoint)

# Requests per minute by status code
sum(rate(http_requests_total[1m])) by (status) * 60

# Active connections gauge
active_connections{service="api"}

# Cache hit rate
avg(cache_hit_rate) by (cache_type)

# Top 5 slowest endpoints
topk(5, avg(rate(http_request_duration_seconds_sum[5m]) /
             rate(http_request_duration_seconds_count[5m]))
         by (endpoint))

# Alert: High error rate
(rate(http_requests_total{status=~"5.."}[5m]) /
 rate(http_requests_total[5m])) > 0.05

# Alert: High latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
```

### Example 3: Structured Logging with ELK Stack

```python
import logging
import json
from datetime import datetime
import traceback
import sys

class JSONFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add trace context if available
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'span_id'):
            log_data['span_id'] = record.span_id

        # Add custom fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())

logger = logging.getLogger('my_app')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage examples
def process_order(order_id, user_id):
    """Example function with structured logging"""

    logger.info(
        "Processing order",
        extra={
            'user_id': user_id,
            'request_id': 'req-12345',
            'extra_fields': {
                'order_id': order_id,
                'action': 'process',
                'environment': 'production'
            }
        }
    )

    try:
        # Simulate order processing
        if order_id < 0:
            raise ValueError("Invalid order ID")

        logger.info(
            "Order processed successfully",
            extra={
                'user_id': user_id,
                'duration': 150,  # ms
                'extra_fields': {
                    'order_id': order_id,
                    'status': 'completed'
                }
            }
        )

    except Exception as e:
        logger.error(
            "Order processing failed",
            extra={
                'user_id': user_id,
                'extra_fields': {
                    'order_id': order_id,
                    'error_type': type(e).__name__
                }
            },
            exc_info=True
        )
        raise

# Elasticsearch query examples (Kibana Query Language - KQL)
```

**Elasticsearch/Kibana Queries:**

```
# Find all errors in last hour
level: ERROR AND timestamp >= now-1h

# Find slow requests (> 1 second)
duration_ms > 1000 AND timestamp >= now-15m

# Find requests for specific user
user_id: "user123" AND level: INFO

# Find exceptions by type
exception.type: "ValueError"

# Aggregation: Top 10 error messages
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "top_errors": {
      "terms": {
        "field": "message.keyword",
        "size": 10
      }
    }
  }
}

# Aggregation: Request rate by endpoint over time
{
  "query": {
    "range": {"timestamp": {"gte": "now-1h"}}
  },
  "aggs": {
    "requests_over_time": {
      "date_histogram": {
        "field": "timestamp",
        "fixed_interval": "1m"
      },
      "aggs": {
        "by_endpoint": {
          "terms": {
            "field": "extra_fields.endpoint.keyword"
          }
        }
      }
    }
  }
}
```

### Example 4: Distributed Tracing with Jaeger

```python
from jaeger_client import Config
from opentracing.ext import tags
from opentracing.propagation import Format
import time
import requests

def init_tracer(service_name='my-service'):
    """Initialize Jaeger tracer"""
    config = Config(
        config={
            'sampler': {
                'type': 'probabilistic',
                'param': 1.0,  # Sample 100% for demo, use 0.01-0.1 in production
            },
            'logging': True,
            'reporter_batch_size': 1,
            'local_agent': {
                'reporting_host': 'jaeger-agent',
                'reporting_port': 6831,
            }
        },
        service_name=service_name,
        validate=True,
    )
    return config.initialize_tracer()

tracer = init_tracer('order-service')

def create_order(order_data):
    """Create order with distributed tracing"""

    with tracer.start_active_span('create_order') as scope:
        span = scope.span

        # Add tags
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)
        span.set_tag('order.total', order_data.get('total', 0))
        span.set_tag('order.items', len(order_data.get('items', [])))
        span.set_tag('customer.id', order_data.get('customer_id'))

        # Log event
        span.log_kv({
            'event': 'order_validation',
            'message': 'Validating order data'
        })

        # Validate inventory (child span)
        inventory_available = check_inventory(order_data['items'])

        if not inventory_available:
            span.set_tag('error', True)
            span.log_kv({
                'event': 'error',
                'error.kind': 'inventory_error',
                'message': 'Insufficient inventory'
            })
            raise ValueError("Insufficient inventory")

        # Process payment (child span)
        payment_result = process_payment(order_data['total'], order_data['customer_id'])

        # Save to database (child span)
        order_id = save_order(order_data)

        span.log_kv({
            'event': 'order_created',
            'order.id': order_id
        })

        return order_id

def check_inventory(items):
    """Check inventory availability"""

    with tracer.start_active_span('check_inventory') as scope:
        span = scope.span
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
        span.set_tag('items.count', len(items))

        # Simulate API call to inventory service
        headers = {}
        tracer.inject(span.context, Format.HTTP_HEADERS, headers)

        time.sleep(0.05)  # Simulate network latency

        span.log_kv({'event': 'inventory_checked'})
        return True

def process_payment(amount, customer_id):
    """Process payment through payment gateway"""

    with tracer.start_active_span('process_payment') as scope:
        span = scope.span
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
        span.set_tag('payment.amount', amount)
        span.set_tag('payment.gateway', 'stripe')

        try:
            # Simulate payment processing
            time.sleep(0.1)

            span.log_kv({
                'event': 'payment_processed',
                'transaction.id': 'txn-12345'
            })

            return {'success': True, 'transaction_id': 'txn-12345'}

        except Exception as e:
            span.set_tag('error', True)
            span.log_kv({
                'event': 'error',
                'error.object': str(e),
                'error.kind': type(e).__name__
            })
            raise

def save_order(order_data):
    """Save order to database"""

    with tracer.start_active_span('database.save_order') as scope:
        span = scope.span
        span.set_tag(tags.DATABASE_TYPE, 'postgresql')
        span.set_tag(tags.DATABASE_INSTANCE, 'orders-db')
        span.set_tag(tags.DATABASE_STATEMENT, 'INSERT INTO orders ...')

        # Simulate database operation
        time.sleep(0.02)

        order_id = 'order-67890'
        span.log_kv({'order.id': order_id})

        return order_id
```

### Example 5: Grafana Dashboard Configuration (JSON)

```json
{
  "dashboard": {
    "title": "Service Health Dashboard",
    "tags": ["production", "api"],
    "timezone": "utc",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ],
        "yaxes": [
          {
            "label": "requests/sec",
            "format": "reqps"
          }
        ]
      },
      {
        "id": 2,
        "title": "Error Rate %",
        "type": "graph",
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
            "legendFormat": "Error Rate"
          }
        ],
        "alert": {
          "name": "High Error Rate",
          "conditions": [
            {
              "evaluator": {
                "type": "gt",
                "params": [5]
              },
              "query": {
                "params": ["A", "5m", "now"]
              }
            }
          ]
        }
      },
      {
        "id": 3,
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "active_connections"
          }
        ]
      }
    ],
    "templating": {
      "list": [
        {
          "name": "service",
          "type": "query",
          "query": "label_values(http_requests_total, service)"
        },
        {
          "name": "environment",
          "type": "query",
          "query": "label_values(http_requests_total, environment)"
        }
      ]
    }
  }
}
```

### Example 6: Alert Rules Configuration

```yaml
# Prometheus Alert Rules
groups:
  - name: service_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) /
           sum(rate(http_requests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1.0
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High request latency detected"
          description: "p95 latency is {{ $value }}s (threshold: 1s)"

      # Service down
      - alert: ServiceDown
        expr: up{job="api-service"} == 0
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "Service has been down for more than 1 minute"

      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
          node_memory_MemTotal_bytes > 0.90
        for: 5m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          db_connection_pool_active / db_connection_pool_max > 0.90
        for: 2m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of connections in use"

# AlertManager Configuration
route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-pager'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
        description: '{{ .GroupLabels.alertname }}'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### Example 7: SLI/SLO Implementation

```python
# SLI/SLO tracking and reporting
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import prometheus_client

@dataclass
class SLI:
    """Service Level Indicator"""
    name: str
    good_events: int
    total_events: int

    @property
    def ratio(self) -> float:
        """Calculate SLI ratio"""
        if self.total_events == 0:
            return 1.0
        return self.good_events / self.total_events

@dataclass
class SLO:
    """Service Level Objective"""
    name: str
    target: float  # e.g., 0.999 for 99.9%
    window_days: int  # e.g., 30 for 30-day window

    def error_budget_remaining(self, sli: SLI) -> float:
        """Calculate remaining error budget"""
        allowed_failures = (1 - self.target) * sli.total_events
        actual_failures = sli.total_events - sli.good_events
        remaining = allowed_failures - actual_failures
        return remaining / allowed_failures if allowed_failures > 0 else 0

class SLOTracker:
    """Track and report on SLOs"""

    def __init__(self):
        # Define SLOs
        self.slos = {
            'availability': SLO('Service Availability', 0.999, 30),
            'latency': SLO('Request Latency', 0.99, 30),
            'error_rate': SLO('Error Rate', 0.99, 30)
        }

        # Prometheus metrics for SLI/SLO
        self.sli_gauge = prometheus_client.Gauge(
            'sli_ratio',
            'Current SLI ratio',
            ['slo_name']
        )

        self.error_budget_gauge = prometheus_client.Gauge(
            'error_budget_remaining',
            'Remaining error budget (0-1)',
            ['slo_name']
        )

    def calculate_availability_sli(self, window_hours: int = 24) -> SLI:
        """Calculate availability SLI from Prometheus"""
        # Query successful requests
        good_query = f'sum(rate(http_requests_total{{status!~"5.."}}[{window_hours}h]))'
        # Query all requests
        total_query = f'sum(rate(http_requests_total[{window_hours}h]))'

        # In practice, query Prometheus here
        good_events = 9950  # Example: 99.5% availability
        total_events = 10000

        return SLI('availability', good_events, total_events)

    def calculate_latency_sli(self, window_hours: int = 24) -> SLI:
        """Calculate latency SLI (requests under threshold)"""
        # Count requests under latency threshold (e.g., 500ms)
        good_query = f'''
            sum(rate(http_request_duration_seconds_bucket{{le="0.5"}}[{window_hours}h]))
        '''
        total_query = f'sum(rate(http_request_duration_seconds_count[{window_hours}h]))'

        # In practice, query Prometheus here
        good_events = 9900  # 99% under 500ms
        total_events = 10000

        return SLI('latency', good_events, total_events)

    def generate_report(self) -> dict:
        """Generate SLO compliance report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'slos': []
        }

        # Calculate each SLI
        availability_sli = self.calculate_availability_sli()
        latency_sli = self.calculate_latency_sli()

        for slo_name, slo in self.slos.items():
            if slo_name == 'availability':
                sli = availability_sli
            elif slo_name == 'latency':
                sli = latency_sli
            else:
                continue

            error_budget = slo.error_budget_remaining(sli)
            is_compliant = sli.ratio >= slo.target

            # Update Prometheus metrics
            self.sli_gauge.labels(slo_name=slo_name).set(sli.ratio)
            self.error_budget_gauge.labels(slo_name=slo_name).set(error_budget)

            report['slos'].append({
                'name': slo.name,
                'target': slo.target,
                'actual': sli.ratio,
                'compliant': is_compliant,
                'error_budget_remaining': error_budget,
                'window_days': slo.window_days
            })

        return report

# Usage
tracker = SLOTracker()
report = tracker.generate_report()

print(f"SLO Report - {report['timestamp']}")
for slo in report['slos']:
    status = "✓" if slo['compliant'] else "✗"
    print(f"{status} {slo['name']}: {slo['actual']:.4f} (target: {slo['target']:.4f})")
    print(f"  Error budget: {slo['error_budget_remaining']:.2%}")
```

## Glossary

- **Telemetry**: Data emitted by systems (metrics, logs, traces)
- **Instrumentation**: Code that generates telemetry
- **Exporter**: Component that sends telemetry to backend
- **Backend**: Storage and analysis system for telemetry
- **Cardinality**: Number of unique label combinations
- **Golden Signals**: Key metrics (latency, traffic, errors, saturation)
- **SRE**: Site Reliability Engineering
- **MTTD**: Mean Time To Detect
- **MTTR**: Mean Time To Resolve
- **SLI**: Service Level Indicator
- **SLO**: Service Level Objective
- **SLA**: Service Level Agreement
