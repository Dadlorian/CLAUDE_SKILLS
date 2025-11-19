# Metrics Reference

## Overview

Metrics are numerical measurements collected over time that represent the state and behavior of systems. They are the foundation of monitoring and alerting.

## Metric Types

### Counter
- **Definition**: Monotonically increasing value
- **Resets**: Only on restart
- **Examples**: Total requests, error count, bytes sent
- **Query Pattern**: Rate of change (rate, irate)
- **Prometheus Type**: counter

```promql
# Request rate over 5 minutes
rate(http_requests_total[5m])
```

### Gauge
- **Definition**: Point-in-time value that can go up or down
- **Examples**: CPU usage, memory usage, queue depth, temperature
- **Query Pattern**: Current value, average, min, max
- **Prometheus Type**: gauge

```promql
# Current CPU usage
node_cpu_usage_percent

# Average over time
avg_over_time(node_cpu_usage_percent[5m])
```

### Histogram
- **Definition**: Observations bucketed into configurable ranges
- **Includes**: Count, sum, buckets
- **Examples**: Request latency, response size
- **Calculations**: Percentiles, averages
- **Prometheus Type**: histogram

```promql
# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average latency
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

### Summary
- **Definition**: Pre-calculated quantiles on client side
- **Includes**: Count, sum, quantiles (φ-quantiles)
- **Examples**: Request latency percentiles
- **Limitation**: Cannot aggregate across instances
- **Prometheus Type**: summary

```promql
# Pre-calculated 95th percentile
http_request_duration_seconds{quantile="0.95"}
```

### Timer (StatsD)
- **Definition**: Measures duration of events
- **Auto-calculates**: Mean, percentiles, rate, count
- **Examples**: Function execution time, query duration
- **StatsD Type**: timer/timing

### Set (StatsD)
- **Definition**: Count of unique values
- **Examples**: Unique users, unique IP addresses
- **StatsD Type**: set

## Metric Naming Conventions

### Prometheus Naming
```
# Pattern: <namespace>_<name>_<unit>_<suffix>
http_requests_total
http_request_duration_seconds
node_memory_usage_bytes

# Labels for dimensions
http_requests_total{method="GET", status="200", path="/api/users"}
```

### Best Practices
1. Use base units (seconds not milliseconds, bytes not megabytes)
2. Suffix with unit name (_seconds, _bytes, _ratio)
3. Add _total suffix for counters
4. Use snake_case
5. Namespace metrics (app_, node_, http_)
6. Be consistent across codebase

## Labels and Cardinality

### Good Labels
```promql
# Low to medium cardinality
http_requests_total{
  method="GET",           # ~10 values
  status="200",           # ~10 values
  path="/api/users",      # ~100 endpoints
  region="us-east-1",     # ~20 regions
  service="api"           # ~50 services
}
# Total cardinality: 10 × 10 × 100 × 20 × 50 = 1,000,000
```

### Bad Labels (High Cardinality)
```promql
# Avoid!
http_requests_total{
  user_id="12345",        # Millions of users
  trace_id="abc...",      # Unique per request
  timestamp="...",        # Infinite values
  email="user@example"    # Millions of emails
}
```

### Label Best Practices
1. Keep cardinality under 10,000 per metric
2. Use labels for dimensions you'll query
3. Avoid unique identifiers as labels
4. Pre-aggregate high-cardinality data
5. Use recording rules for common aggregations

## Common Metric Patterns

### RED Method (for Services)
```promql
# Rate - Requests per second
sum(rate(http_requests_total[5m])) by (service)

# Errors - Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) /
sum(rate(http_requests_total[5m])) by (service)

# Duration - Latency percentiles
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)
```

### USE Method (for Resources)
```promql
# Utilization - Percentage used
avg(node_cpu_usage_percent) by (instance)

# Saturation - Queue depth
avg(node_disk_queue_depth) by (instance)

# Errors - Error count
rate(node_disk_errors_total[5m])
```

### Four Golden Signals
```promql
# 1. Latency
histogram_quantile(0.95, rate(http_duration_bucket[5m]))

# 2. Traffic
sum(rate(http_requests_total[5m]))

# 3. Errors
sum(rate(http_requests_total{status=~"5.."}[5m]))

# 4. Saturation
avg(node_cpu_usage_percent)
```

## Aggregation Operations

### Sum
```promql
# Total requests across all instances
sum(rate(http_requests_total[5m]))

# Total per service
sum(rate(http_requests_total[5m])) by (service)
```

### Average
```promql
# Average CPU across instances
avg(node_cpu_usage_percent)

# Average per region
avg(node_cpu_usage_percent) by (region)
```

### Min/Max
```promql
# Highest CPU usage
max(node_cpu_usage_percent)

# Lowest available memory
min(node_memory_available_bytes)
```

### Count
```promql
# Number of instances
count(up{job="api"})

# Number of services with errors
count(rate(errors_total[5m]) > 0)
```

### Quantile
```promql
# 95th percentile across all instances
quantile(0.95, http_request_duration_seconds)
```

### Standard Deviation
```promql
# Variability in latency
stddev(http_request_duration_seconds)
```

## Time Windows

### Range Vectors
```promql
# Last 5 minutes of data
http_requests_total[5m]

# Last 1 hour
http_requests_total[1h]

# Common windows: [30s], [1m], [5m], [15m], [1h], [1d]
```

### Rate Calculations
```promql
# rate() - Average rate over window
rate(http_requests_total[5m])

# irate() - Instant rate (last 2 points)
irate(http_requests_total[5m])

# increase() - Total increase over window
increase(http_requests_total[5m])
```

### Window Best Practices
1. Use at least 4x scrape interval for rate()
2. Larger windows = smoother graphs, less detail
3. Smaller windows = more detail, more noise
4. Align window with alert duration
5. irate() for volatile metrics, rate() for stable

## Percentiles and Histograms

### Calculating Percentiles
```promql
# 50th percentile (median)
histogram_quantile(0.50, rate(http_duration_bucket[5m]))

# 95th percentile
histogram_quantile(0.95, rate(http_duration_bucket[5m]))

# 99th percentile
histogram_quantile(0.99, rate(http_duration_bucket[5m]))

# 99.9th percentile
histogram_quantile(0.999, rate(http_duration_bucket[5m]))
```

### Histogram Buckets
```python
# Python Prometheus client
from prometheus_client import Histogram

# Latency histogram with custom buckets
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)
```

### Bucket Best Practices
1. Cover expected range of values
2. More buckets in areas of interest
3. Include outlier buckets (very low, very high)
4. Exponential distribution often works well
5. Default buckets: [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf]

## Metric Collection Methods

### Push-Based
- Client pushes metrics to collector
- Examples: StatsD, Carbon (Graphite), CloudWatch
- Pros: Simple, works behind firewalls
- Cons: No service discovery, can lose data

### Pull-Based
- Server scrapes metrics from clients
- Examples: Prometheus, VictoriaMetrics
- Pros: Service discovery, health checking
- Cons: Requires network access to clients

### Agent-Based
- Agent on each host collects and forwards
- Examples: Telegraf, Datadog Agent, Node Exporter
- Pros: Local aggregation, buffering
- Cons: Additional resource overhead

## Instrumentation Libraries

### Prometheus Client Libraries
```python
# Python
from prometheus_client import Counter, Histogram, Gauge

requests_total = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'Request latency')
active_connections = Gauge('active_connections', 'Active connections')

# Usage
requests_total.labels(method='GET', endpoint='/api/users').inc()
with request_duration.time():
    process_request()
active_connections.set(42)
```

```go
// Go
import "github.com/prometheus/client_golang/prometheus"

var (
    requestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "endpoint"},
    )
)

// Usage
requestsTotal.WithLabelValues("GET", "/api/users").Inc()
```

```javascript
// Node.js
const client = require('prom-client');

const requestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'endpoint']
});

// Usage
requestsTotal.labels('GET', '/api/users').inc();
```

### StatsD Client
```python
# Python
from statsd import StatsClient

statsd = StatsClient('localhost', 8125)

# Counter
statsd.incr('page.views')

# Timer
with statsd.timer('api.request'):
    process_request()

# Gauge
statsd.gauge('active.sessions', 1234)
```

## Metric Exporters

### Node Exporter (Infrastructure)
- CPU, memory, disk, network metrics
- File system metrics
- Hardware sensors
- Runs on each host

### Blackbox Exporter (Synthetic)
- HTTP, TCP, ICMP probes
- DNS lookups
- SSL certificate expiry
- External endpoint monitoring

### Custom Exporters
- Application-specific metrics
- Database metrics
- Third-party service metrics
- Business metrics

## Recording Rules

### Purpose
- Pre-calculate expensive queries
- Aggregate high-cardinality metrics
- Create derived metrics
- Speed up dashboard queries

### Example
```yaml
# prometheus_rules.yml
groups:
  - name: api_metrics
    interval: 30s
    rules:
      # Request rate per service
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)

      # Error ratio
      - record: job:http_errors:ratio
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)

      # 95th percentile latency
      - record: job:http_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le)
          )
```

## Best Practices

### Metric Design
1. Start with high-level metrics (RED method)
2. Add detail as needed (avoid premature optimization)
3. Use consistent naming across services
4. Include units in metric names
5. Document metrics in code comments

### Cardinality Management
1. Monitor cardinality per metric
2. Drop high-cardinality labels
3. Use recording rules for aggregations
4. Sample or aggregate before storage
5. Set retention based on cardinality

### Performance
1. Minimize metric collection overhead (<1% CPU)
2. Batch metric updates when possible
3. Use efficient data structures
4. Avoid blocking on metric updates
5. Consider async metric collection

### Accuracy
1. Use appropriate metric types
2. Initialize metrics at startup (avoid missing series)
3. Handle counter resets properly
4. Use consistent timestamp precision
5. Test metric instrumentation

## Common Metrics

### HTTP/API Metrics
```
http_requests_total{method, path, status}
http_request_duration_seconds{method, path}
http_request_size_bytes{method, path}
http_response_size_bytes{method, path}
```

### Database Metrics
```
db_queries_total{query_type}
db_query_duration_seconds{query_type}
db_connections_active
db_connections_idle
db_errors_total{error_type}
```

### Queue Metrics
```
queue_messages_published_total{queue}
queue_messages_consumed_total{queue}
queue_depth{queue}
queue_message_age_seconds{queue}
```

### Cache Metrics
```
cache_hits_total{cache}
cache_misses_total{cache}
cache_size_bytes{cache}
cache_evictions_total{cache}
```

### Infrastructure Metrics
```
node_cpu_usage_percent{cpu, mode}
node_memory_usage_bytes
node_disk_io_bytes{device, direction}
node_network_bytes{device, direction}
```

## Anti-Patterns

### What to Avoid
1. **Too many labels**: Cardinality explosion
2. **Unique labels**: User IDs, trace IDs as labels
3. **Missing units**: Is it seconds or milliseconds?
4. **Inconsistent naming**: Some metrics use camelCase, others snake_case
5. **Metric sprawl**: Too many similar metrics
6. **No aggregation**: Raw metrics without summary views
7. **Wrong metric type**: Using gauge for counter data
8. **Stale metrics**: Not updating regularly
9. **No documentation**: Unclear metric meaning
10. **Ignoring performance**: Heavy instrumentation overhead

## Tools and Platforms

### Open Source
- Prometheus
- VictoriaMetrics
- Thanos
- Cortex
- Graphite
- InfluxDB

### Commercial
- Datadog
- New Relic
- Dynatrace
- SignalFx
- Honeycomb

### Cloud Native
- AWS CloudWatch
- Azure Monitor
- Google Cloud Monitoring
