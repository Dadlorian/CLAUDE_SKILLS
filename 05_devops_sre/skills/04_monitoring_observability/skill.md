# Monitoring & Observability - Elite Professional Practices

**Comprehensive system visibility through metrics, logs, and traces**

---

## Overview

You are an expert in monitoring and observability, skilled in designing comprehensive observability systems that provide deep insights into distributed systems. Your expertise is based on practices from Google SRE, Netflix, Uber, DataDog, and other tier-1 organizations.

## Three Pillars of Observability

### 1. Metrics (Aggregated Time-Series Data)

**Definition**: Numerical measurements aggregated over time windows

**Types of Metrics**:

**System Metrics**:
- CPU utilization, load average
- Memory usage (used, available, cached)
- Disk I/O (throughput, IOPS, latency)
- Network (bandwidth, packet loss, errors)

**Application Metrics** (RED Method):
- **Rate**: Requests per second
- **Errors**: Error rate (percentage of failed requests)
- **Duration**: Request latency (p50, p95, p99, p999)

**Business Metrics**:
- Sign-ups, conversions, transactions
- Revenue, cart value
- Active users, engagement

**Implementation with Prometheus**:
```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# Counter: Monotonically increasing value
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Histogram: Latency distribution with buckets
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Gauge: Value that can go up or down
active_connections = Gauge(
    'active_connections',
    'Number of active database connections'
)

# Usage in application code
@app.route('/api/users/<user_id>')
def get_user(user_id):
    start_time = time.time()

    try:
        user = db.get_user(user_id)
        status = 200
        return jsonify(user), status
    except UserNotFound:
        status = 404
        return jsonify({"error": "Not found"}), status
    except Exception:
        status = 500
        return jsonify({"error": "Internal error"}), status
    finally:
        # Record metrics
        http_requests_total.labels(
            method='GET',
            endpoint='/api/users',
            status_code=status
        ).inc()

        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method='GET',
            endpoint='/api/users'
        ).observe(duration)
```

**PromQL Queries** (Prometheus Query Language):
```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (percentage)
sum(rate(http_requests_total{status_code=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Top 5 endpoints by request count
topk(5, sum by (endpoint) (rate(http_requests_total[5m])))
```

### 2. Logs (Discrete Events with Context)

**Definition**: Time-stamped records of events that occurred

**Structured Logging** (JSON format):
```python
import json
import logging
from datetime import datetime

def log_event(level, message, **context):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "message": message,
        "service": "api-service",
        "environment": "production",
        **context
    }
    print(json.dumps(log_entry))

# Usage
log_event(
    "INFO",
    "User authenticated successfully",
    user_id=12345,
    ip_address="203.0.113.42",
    method="OAuth2",
    duration_ms=234,
    trace_id="abc123xyz789"
)

# Output:
{
  "timestamp": "2025-11-19T14:32:45.123Z",
  "level": "INFO",
  "message": "User authenticated successfully",
  "service": "api-service",
  "environment": "production",
  "user_id": 12345,
  "ip_address": "203.0.113.42",
  "method": "OAuth2",
  "duration_ms": 234,
  "trace_id": "abc123xyz789"
}
```

**Log Levels**:
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARN**: Something unexpected, but the system can continue
- **ERROR**: Serious problem, functionality failed
- **FATAL**: Critical error, system may crash

**Centralized Log Aggregation** (ELK Stack):

**Filebeat configuration**:
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/app/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "app-logs-%{+yyyy.MM.dd}"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
```

**Elasticsearch Queries**:
```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ],
      "filter": [
        { "term": { "service": "api-service" } }
      ]
    }
  },
  "aggs": {
    "errors_by_endpoint": {
      "terms": { "field": "endpoint.keyword" }
    }
  }
}
```

### 3. Traces (Request Flow Across Services)

**Definition**: End-to-end view of requests through distributed systems

**OpenTelemetry Implementation**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure exporter (to Jaeger, Zipkin, or any OTLP endpoint)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument your code
@app.route('/api/checkout')
def checkout():
    with tracer.start_as_current_span("checkout_process") as span:
        # Add attributes to span
        span.set_attribute("user.id", user_id)
        span.set_attribute("cart.total", cart_total)
        span.set_attribute("cart.items_count", len(items))

        # Step 1: Validate inventory
        with tracer.start_as_current_span("validate_inventory") as inv_span:
            inv_span.set_attribute("inventory.service", "inventory-api")
            available = inventory_service.check_availability(items)
            inv_span.set_attribute("inventory.available", available)

        # Step 2: Process payment
        with tracer.start_as_current_span("process_payment") as pay_span:
            pay_span.set_attribute("payment.amount", cart_total)
            pay_span.set_attribute("payment.method", "credit_card")
            try:
                payment_result = payment_service.charge(user_id, cart_total)
                pay_span.set_attribute("payment.transaction_id", payment_result.id)
            except PaymentException as e:
                pay_span.record_exception(e)
                pay_span.set_status(Status(StatusCode.ERROR, "Payment failed"))
                raise

        # Step 3: Create shipment
        with tracer.start_as_current_span("create_shipment"):
            shipment = shipping_service.create(user_id, items, address)

        return {"order_id": order_id, "status": "success"}
```

**What Traces Reveal**:
- End-to-end latency breakdown
- Service dependencies and call graph
- Slowest operations (critical path)
- Error propagation across services
- Resource consumption per span

## Observability Patterns

### RED Method (Request-Oriented Services)

For every service, monitor:
- **R**ate: Requests per second
- **E**rrors: Number of failed requests
- **D**uration: Latency distribution (p50, p95, p99)

**Implementation**:
```promql
# Request Rate
sum(rate(http_requests_total[5m])) by (service)

# Error Rate
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) /
sum(rate(http_requests_total[5m])) by (service)

# Duration (p99)
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (service, le)
)
```

### USE Method (Resource-Oriented Infrastructure)

For every resource, monitor:
- **U**tilization: % of time the resource is busy
- **S**aturation: Amount of work queued that cannot be serviced
- **E**rrors: Count of error events

**Implementation**:
```promql
# CPU Utilization
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Utilization
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
node_memory_MemTotal_bytes * 100

# Disk Saturation
rate(node_disk_io_time_weighted_seconds_total[5m])

# Network Errors
rate(node_network_receive_errs_total[5m])
```

### Four Golden Signals (Google SRE)

For every service:
1. **Latency**: Time to service requests
2. **Traffic**: Demand on the system
3. **Errors**: Rate of failed requests
4. **Saturation**: How "full" the service is

## Service Level Objectives (SLOs)

### Defining SLOs

**SLI** (Service Level Indicator): Quantitative measure of service level
- Availability: % of successful requests
- Latency: % of requests faster than threshold
- Throughput: Requests per second

**SLO** (Service Level Objective): Target value for an SLI
- "99.9% of requests succeed"
- "95% of requests complete in < 500ms"

**SLA** (Service Level Agreement): Contract with consequences
- Typically more lenient than internal SLOs
- Includes penalties for violations

**Example SLOs**:
```yaml
# API Service SLOs
availability:
  target: 99.9%  # "three nines"
  window: 30 days
  measurement: success_rate = successful_requests / total_requests

latency:
  target: 95%  # 95% of requests
  threshold: 500ms
  window: 30 days

error_budget:
  # 0.1% failure allowed over 30 days
  # = 43 minutes of downtime per month
  calculation: (1 - availability_target) * window
```

### Error Budgets

**Concept**: Quantify acceptable unreliability

**Calculation**:
```
Error Budget = (1 - SLO) × Time Period

Example:
SLO: 99.9% availability over 30 days
Error Budget: (1 - 0.999) × 30 days
           = 0.001 × 43,200 minutes
           = 43.2 minutes of downtime allowed per month
```

**Error Budget Policy**:
- If error budget remaining: focus on velocity (ship features)
- If error budget exhausted: focus on reliability (freeze features, fix bugs)

**Monitoring Error Budget Burn**:
```promql
# Availability SLI
availability_sli = sum(rate(http_requests_total{status!~"5.."}[30d])) /
                   sum(rate(http_requests_total[30d]))

# Error budget remaining (%)
error_budget_remaining = (availability_sli - 0.999) / (1 - 0.999) * 100

# Alert if burning error budget too fast
alert: ErrorBudgetBurnRateCritical
expr: |
  (1 - availability_sli) > (1 - 0.999) * 14.4  # Consuming 30-day budget in 2 days
for: 15m
```

## Alerting Best Practices

### Alert Design Principles

**1. Alert on Symptoms, Not Causes**
- ❌ Bad: "CPU is at 90%"
- ✅ Good: "p99 latency is 2x normal" (symptom that affects users)

**2. Actionable Alerts Only**
- Every alert should require human action
- If it's informational, use a dashboard instead

**3. Clear Severity Levels**
- **Critical (P1)**: User-facing impact, immediate response needed
- **Warning (P2)**: Potential issue, investigate within hours
- **Info**: For awareness, no immediate action

**4. Include Context in Alerts**
- Runbook link for resolution steps
- Dashboard link for investigation
- Query link to explore data

### Alert Examples

**SLO-Based Alerting**:
```yaml
groups:
- name: slo_alerts
  interval: 30s
  rules:
    # Fast burn: 2% budget consumed in 1 hour (would exhaust in 2 days)
    - alert: ErrorBudgetFastBurn
      expr: |
        (
          1 - (sum(rate(http_requests_total{status!~"5.."}[1h])) /
               sum(rate(http_requests_total[1h])))
        ) > 0.02
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Fast error budget burn detected"
        description: "Consuming 2% error budget per hour (30-day budget exhausted in 2 days)"
        runbook: "https://runbooks.example.com/fast-error-budget-burn"
        dashboard: "https://grafana.example.com/d/slo-dashboard"

    # Slow burn: 10% budget consumed in 6 hours (would exhaust in 12 days)
    - alert: ErrorBudgetSlowBurn
      expr: |
        (
          1 - (sum(rate(http_requests_total{status!~"5.."}[6h])) /
               sum(rate(http_requests_total[6h])))
        ) > 0.10
      for: 30m
      labels:
        severity: warning
      annotations:
        summary: "Slow error budget burn detected"
        runbook: "https://runbooks.example.com/error-budget-management"
```

**Latency Alerting**:
```yaml
- alert: HighLatency
  expr: |
    histogram_quantile(0.99,
      sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
    ) > 1.0
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High request latency (p99 > 1s)"
    description: "p99 latency is {{ $value }}s, exceeding 1s threshold"
    runbook: "https://runbooks.example.com/high-latency"
```

## Technology Stack

### Metrics Platforms

**Prometheus** (Open Source)
- Pull-based metric collection
- Powerful query language (PromQL)
- Service discovery (Kubernetes, Consul, EC2)
- Alertmanager for alert routing
- Grafana for visualization

**Datadog** (Commercial SaaS)
- Unified metrics, logs, traces
- 600+ integrations
- AI-powered anomaly detection
- Real-time dashboards

**New Relic** (Commercial SaaS)
- Application performance monitoring (APM)
- Infrastructure monitoring
- Distributed tracing
- Log management

### Logging Platforms

**ELK Stack** (Elasticsearch, Logstash, Kibana)
- Elasticsearch: Search and analytics
- Logstash: Log collection and processing
- Kibana: Visualization and dashboards

**Loki** (Grafana Labs)
- Like Prometheus, but for logs
- Indexes metadata, not content (cost-efficient)
- Integrates with Grafana

**Splunk** (Commercial)
- Enterprise log management
- Machine learning for anomaly detection
- Security and compliance features

### Tracing Platforms

**Jaeger** (CNCF, Open Source)
- Distributed tracing for microservices
- Root cause analysis
- Performance optimization
- Service dependency analysis

**Zipkin** (Open Source)
- Distributed tracing system
- Twitter origin
- Simpler than Jaeger

**Honeycomb** (Commercial)
- Observability platform
- High-cardinality data support
- Real-time querying

### Unified Platforms

**Datadog**: Metrics + Logs + Traces + RUM + Security
**New Relic**: APM + Infrastructure + Logs + Traces
**Dynatrace**: Full-stack monitoring with AI
**Grafana Cloud**: Prometheus + Loki + Tempo (traces)

## Best Practices

### 1. Instrumentation

**Start with Standards**:
- RED metrics for every service
- USE metrics for every resource
- Structured logging everywhere
- Distributed tracing for distributed systems

**Naming Conventions**:
```
# Metric naming (Prometheus)
<namespace>_<name>_<unit>

Examples:
http_requests_total
http_request_duration_seconds
database_connections_active
queue_messages_pending
```

**Cardinality Management**:
- Avoid high-cardinality labels (user IDs, trace IDs)
- Keep label cardinality < 1000 per metric
- Use exemplars for trace IDs instead of labels

### 2. Dashboards

**Dashboard Hierarchy**:
1. **Executive Dashboard**: High-level KPIs, SLOs, business metrics
2. **Service Dashboards**: Per-service RED metrics, dependencies
3. **Infrastructure Dashboards**: Resource utilization (USE method)
4. **Incident Dashboards**: Real-time situation awareness

**Dashboard Best Practices**:
- Start with SLIs and SLOs (what matters to users)
- Group related metrics
- Use consistent color schemes (red = bad, green = good)
- Include time range selector
- Link to runbooks and related dashboards

### 3. On-Call and Incident Response

**On-Call Rotation**:
- Primary and secondary on-call
- Clearly defined escalation paths
- Manageable alert volume (< 5 pages per shift)
- Post-incident reviews and runbook updates

**Runbooks Linked from Alerts**:
- What is this alert?
- What does it mean for users?
- How to investigate (queries, dashboards)
- How to mitigate
- How to resolve
- When to escalate

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Practices from Google SRE, Netflix, Uber, DataDog, Honeycomb
