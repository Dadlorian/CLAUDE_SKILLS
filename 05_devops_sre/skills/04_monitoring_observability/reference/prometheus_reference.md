# Prometheus Reference Guide

## Table of Contents
1. [PromQL Fundamentals](#promql-fundamentals)
2. [Recording Rules](#recording-rules)
3. [Alerting Rules](#alerting-rules)
4. [Best Practices](#best-practices)

---

## PromQL Fundamentals

### Data Types

#### Instant Vector
Single sample per time series at a given timestamp.
```promql
http_requests_total
http_requests_total{job="api-server", handler="/api/comments"}
```

#### Range Vector
Set of time series containing data points over a time range.
```promql
http_requests_total[5m]
http_requests_total{job="api-server"}[1h]
```

#### Scalar
Simple numeric floating point value.
```promql
42
3.14159
```

#### String
Simple string value (rarely used).
```promql
"hello world"
```

### Selectors and Matchers

#### Label Matching
```promql
# Exact match
http_requests_total{method="GET"}

# Negative match
http_requests_total{method!="GET"}

# Regex match
http_requests_total{handler=~"/api/.*"}

# Negative regex match
http_requests_total{handler!~"/admin/.*"}

# Multiple labels
http_requests_total{job="api-server", method="GET", status=~"2.."}
```

#### Time Range Selectors
```promql
# Last 5 minutes
http_requests_total[5m]

# Last 1 hour
http_requests_total[1h]

# Last 1 day
http_requests_total[1d]

# Last 1 week
http_requests_total[1w]
```

### Operators

#### Arithmetic Operators
```promql
# Addition
node_memory_MemTotal_bytes - node_memory_MemFree_bytes

# Percentage
(node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / node_memory_MemTotal_bytes * 100

# Division
rate(http_requests_total[5m]) / rate(http_requests_total[5m] offset 1h)
```

#### Comparison Operators
```promql
# Greater than
http_requests_total > 1000

# Less than
node_memory_MemAvailable_bytes < 1e9

# Equal to
http_response_status_code == 500

# Not equal to
http_response_status_code != 200

# Greater than or equal
cpu_usage_percent >= 80

# Less than or equal
disk_usage_percent <= 90
```

#### Logical Operators
```promql
# AND
(rate(http_requests_total[5m]) > 10) and (http_request_duration_seconds > 1)

# OR
(up{job="api-server"} == 0) or (up{job="web-server"} == 0)

# UNLESS (AND NOT)
rate(http_requests_total[5m]) unless http_requests_total{status=~"5.."}
```

### Aggregation Operators

#### sum
```promql
# Sum across all dimensions
sum(rate(http_requests_total[5m]))

# Sum by specific labels
sum by (job, handler) (rate(http_requests_total[5m]))

# Sum without specific labels (keep all others)
sum without (instance) (rate(http_requests_total[5m]))
```

#### avg
```promql
# Average response time across all instances
avg(http_request_duration_seconds)

# Average by job
avg by (job) (http_request_duration_seconds)
```

#### min and max
```promql
# Minimum memory available across cluster
min(node_memory_MemAvailable_bytes)

# Maximum CPU usage per job
max by (job) (rate(process_cpu_seconds_total[5m]))
```

#### count
```promql
# Count number of instances
count(up{job="api-server"})

# Count errors per endpoint
count by (handler) (http_requests_total{status=~"5.."})
```

#### stddev and stdvar
```promql
# Standard deviation of response times
stddev(http_request_duration_seconds)

# Standard variance of CPU usage
stdvar by (job) (rate(process_cpu_seconds_total[5m]))
```

#### topk and bottomk
```promql
# Top 5 endpoints by request rate
topk(5, sum by (handler) (rate(http_requests_total[5m])))

# Bottom 3 instances by memory
bottomk(3, node_memory_MemAvailable_bytes)
```

#### quantile
```promql
# 95th percentile response time
quantile(0.95, http_request_duration_seconds)

# 99th percentile by job
quantile by (job) (0.99, http_request_duration_seconds)
```

#### count_values
```promql
# Count how many time series have each distinct value
count_values("version", prometheus_build_info)
```

### Functions

#### rate and irate
```promql
# Average per-second rate over 5 minutes (for counters)
rate(http_requests_total[5m])

# Instantaneous per-second rate (more sensitive to spikes)
irate(http_requests_total[5m])
```

#### increase
```promql
# Total increase over 1 hour
increase(http_requests_total[1h])

# Extrapolated to full hour even if range is partial
increase(http_requests_total[1h])
```

#### delta and idelta
```promql
# Delta for gauges (difference between first and last value)
delta(node_memory_MemAvailable_bytes[5m])

# Instantaneous delta (last two samples)
idelta(node_memory_MemAvailable_bytes[5m])
```

#### deriv and predict_linear
```promql
# Per-second derivative
deriv(node_memory_MemAvailable_bytes[1h])

# Predict value in 4 hours based on 1 hour trend
predict_linear(node_filesystem_free_bytes[1h], 4*3600)
```

#### histogram_quantile
```promql
# 95th percentile from histogram
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 99th percentile by job and handler
histogram_quantile(0.99,
  sum by (job, handler, le) (rate(http_request_duration_seconds_bucket[5m]))
)
```

#### changes and resets
```promql
# Number of times value changed in range
changes(process_start_time_seconds[1h])

# Number of counter resets
resets(http_requests_total[1d])
```

#### Time Functions
```promql
# Current time
time()

# Day of month (1-31)
day_of_month()

# Day of week (0-6, Sunday=0)
day_of_week()

# Hour of day (0-23)
hour()

# Days in month
days_in_month()
```

#### Label Manipulation
```promql
# Add/replace label
label_replace(
  up{job="api-server"},
  "env",
  "production",
  "instance",
  ".*"
)

# Join multiple label values
label_join(up{job="api-server"}, "full_name", "-", "job", "instance")
```

#### Mathematical Functions
```promql
# Absolute value
abs(delta(node_memory_MemAvailable_bytes[5m]))

# Ceiling
ceil(rate(http_requests_total[5m]))

# Floor
floor(rate(http_requests_total[5m]))

# Round
round(rate(http_requests_total[5m]), 0.1)

# Square root
sqrt(rate(http_requests_total[5m]))

# Exponential and logarithm
exp(rate(http_requests_total[5m]))
ln(rate(http_requests_total[5m]))
log2(rate(http_requests_total[5m]))
log10(rate(http_requests_total[5m]))
```

#### Sorting Functions
```promql
# Sort ascending
sort(rate(http_requests_total[5m]))

# Sort descending
sort_desc(rate(http_requests_total[5m]))
```

#### Aggregation Over Time
```promql
# Average over time
avg_over_time(http_request_duration_seconds[5m])

# Min/Max over time
min_over_time(http_request_duration_seconds[5m])
max_over_time(http_request_duration_seconds[5m])

# Sum over time
sum_over_time(http_requests_total[5m])

# Count over time
count_over_time(http_requests_total[5m])

# Quantile over time
quantile_over_time(0.95, http_request_duration_seconds[5m])

# Standard deviation over time
stddev_over_time(http_request_duration_seconds[5m])
stdvar_over_time(http_request_duration_seconds[5m])
```

#### Missing Data Handling
```promql
# Clamp minimum value
clamp_min(node_memory_MemAvailable_bytes, 1e9)

# Clamp maximum value
clamp_max(cpu_usage_percent, 100)

# Return 0 for absent metrics
absent(up{job="api-server"})

# Return 1 if metric doesn't exist, 0 if it does
absent_over_time(up{job="api-server"}[5m])
```

### Vector Matching

#### One-to-One Matching
```promql
# Method 1: Matching with 'on'
method_code:http_errors:rate5m{code="500"} / ignoring(code) method:http_requests:rate5m

# Method 2: Matching with 'ignoring'
method_code:http_errors:rate5m / ignoring(code) method:http_requests:rate5m
```

#### Many-to-One / One-to-Many Matching
```promql
# Group left (left side has more labels)
method_code:http_errors:rate5m / on(method) group_left method:http_requests:rate5m

# Group right (right side has more labels)
method:http_requests:rate5m / on(method) group_right method_code:http_errors:rate5m
```

---

## Recording Rules

Recording rules allow you to precompute frequently needed or computationally expensive expressions and save their result as a new set of time series.

### Basic Syntax
```yaml
groups:
  - name: example_recording_rules
    interval: 30s  # Optional: Override global evaluation interval
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
        labels:
          team: backend
```

### Naming Convention
Use the format: `level:metric:operations`

- **level**: Aggregation level (e.g., `job`, `instance`, `cluster`)
- **metric**: Base metric name
- **operations**: Operations applied (e.g., `rate5m`, `sum`, `avg`)

### Production Examples

#### HTTP Metrics
```yaml
groups:
  - name: http_recording_rules
    interval: 15s
    rules:
      # Request rate by job and handler
      - record: job_handler:http_requests:rate5m
        expr: sum by (job, handler) (rate(http_requests_total[5m]))

      # Request rate by job only
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))

      # Total cluster-wide request rate
      - record: cluster:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m]))

      # Error rate by job and handler
      - record: job_handler:http_errors:rate5m
        expr: |
          sum by (job, handler) (
            rate(http_requests_total{status=~"5.."}[5m])
          )

      # Error ratio (errors / total requests)
      - record: job_handler:http_error_ratio:rate5m
        expr: |
          job_handler:http_errors:rate5m
          /
          job_handler:http_requests:rate5m

      # P95 latency by job and handler
      - record: job_handler:http_request_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum by (job, handler, le) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )

      # P99 latency by job and handler
      - record: job_handler:http_request_duration:p99
        expr: |
          histogram_quantile(0.99,
            sum by (job, handler, le) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )
```

#### Resource Utilization
```yaml
groups:
  - name: resource_recording_rules
    interval: 30s
    rules:
      # CPU utilization by instance
      - record: instance:cpu_utilization:ratio
        expr: |
          1 - avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          )

      # CPU utilization by job
      - record: job:cpu_utilization:ratio
        expr: |
          avg by (job) (instance:cpu_utilization:ratio)

      # Memory utilization by instance
      - record: instance:memory_utilization:ratio
        expr: |
          1 - (
            node_memory_MemAvailable_bytes
            /
            node_memory_MemTotal_bytes
          )

      # Disk utilization by instance and device
      - record: instance_device:disk_utilization:ratio
        expr: |
          1 - (
            node_filesystem_avail_bytes
            /
            node_filesystem_size_bytes
          )

      # Network receive rate by instance
      - record: instance:network_receive_bytes:rate5m
        expr: |
          sum by (instance) (
            rate(node_network_receive_bytes_total[5m])
          )

      # Network transmit rate by instance
      - record: instance:network_transmit_bytes:rate5m
        expr: |
          sum by (instance) (
            rate(node_network_transmit_bytes_total[5m])
          )
```

#### Application Performance
```yaml
groups:
  - name: application_performance_rules
    interval: 30s
    rules:
      # Database query rate
      - record: job:db_queries:rate5m
        expr: sum by (job) (rate(db_queries_total[5m]))

      # Database query duration P50, P95, P99
      - record: job:db_query_duration:p50
        expr: |
          histogram_quantile(0.50,
            sum by (job, le) (rate(db_query_duration_seconds_bucket[5m]))
          )

      - record: job:db_query_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum by (job, le) (rate(db_query_duration_seconds_bucket[5m]))
          )

      - record: job:db_query_duration:p99
        expr: |
          histogram_quantile(0.99,
            sum by (job, le) (rate(db_query_duration_seconds_bucket[5m]))
          )

      # Cache hit rate
      - record: job:cache_hit_ratio:rate5m
        expr: |
          sum by (job) (rate(cache_hits_total[5m]))
          /
          sum by (job) (rate(cache_requests_total[5m]))

      # Goroutines by job (for Go applications)
      - record: job:goroutines:avg
        expr: avg by (job) (go_goroutines)
```

#### SLI Recording Rules
```yaml
groups:
  - name: sli_recording_rules
    interval: 30s
    rules:
      # Availability SLI (success rate)
      - record: service:availability:ratio_rate5m
        expr: |
          sum by (service) (rate(http_requests_total{status=~"2..|3.."}[5m]))
          /
          sum by (service) (rate(http_requests_total[5m]))

      # Latency SLI (percentage below threshold)
      - record: service:latency_le_100ms:ratio_rate5m
        expr: |
          sum by (service) (rate(http_request_duration_seconds_bucket{le="0.1"}[5m]))
          /
          sum by (service) (rate(http_request_duration_seconds_count[5m]))

      # Error budget consumption rate (1h)
      - record: service:error_budget_consumption:rate1h
        expr: |
          (1 - service:availability:ratio_rate5m) / (1 - 0.999)
```

---

## Alerting Rules

Alerting rules define conditions that should trigger alerts when met.

### Basic Syntax
```yaml
groups:
  - name: example_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: job:http_errors:rate5m > 0.05
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} for {{ $labels.job }}"
```

### Alert States
1. **Inactive**: Condition is false
2. **Pending**: Condition is true but not yet for the `for` duration
3. **Firing**: Condition has been true for longer than the `for` duration

### Production Alert Examples

#### Availability Alerts
```yaml
groups:
  - name: availability_alerts
    rules:
      # Service is down
      - alert: ServiceDown
        expr: up{job="api-server"} == 0
        for: 1m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"
          runbook_url: "https://runbooks.example.com/service-down"

      # High error rate
      - alert: HighErrorRate
        expr: |
          (
            sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum by (job) (rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High HTTP 5xx error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} on {{ $labels.job }}"
          dashboard_url: "https://grafana.example.com/d/http-overview"

      # Critical error rate
      - alert: CriticalErrorRate
        expr: |
          (
            sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum by (job) (rate(http_requests_total[5m]))
          ) > 0.10
        for: 2m
        labels:
          severity: critical
          team: backend
          page: "true"
        annotations:
          summary: "CRITICAL: Very high HTTP 5xx error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} on {{ $labels.job }}"
```

#### Latency Alerts
```yaml
groups:
  - name: latency_alerts
    rules:
      # High P95 latency
      - alert: HighP95Latency
        expr: |
          histogram_quantile(0.95,
            sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 1.0
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High P95 latency on {{ $labels.job }}"
          description: "P95 latency is {{ $value }}s on {{ $labels.job }}"

      # Critical P99 latency
      - alert: CriticalP99Latency
        expr: |
          histogram_quantile(0.99,
            sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 5.0
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "CRITICAL: Very high P99 latency on {{ $labels.job }}"
          description: "P99 latency is {{ $value }}s on {{ $labels.job }}"
```

#### Resource Alerts
```yaml
groups:
  - name: resource_alerts
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: instance:cpu_utilization:ratio > 0.80
        for: 15m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      # Critical CPU usage
      - alert: CriticalCPUUsage
        expr: instance:cpu_utilization:ratio > 0.95
        for: 5m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "CRITICAL: Very high CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      # High memory usage
      - alert: HighMemoryUsage
        expr: instance:memory_utilization:ratio > 0.85
        for: 15m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      # Critical memory usage
      - alert: CriticalMemoryUsage
        expr: instance:memory_utilization:ratio > 0.95
        for: 5m
        labels:
          severity: critical
          team: sre
          page: "true"
        annotations:
          summary: "CRITICAL: Very high memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      # Disk space warning
      - alert: DiskSpaceWarning
        expr: instance_device:disk_utilization:ratio > 0.80
        for: 30m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Disk space running low on {{ $labels.instance }}"
          description: "Disk {{ $labels.device }} is {{ $value | humanizePercentage }} full on {{ $labels.instance }}"

      # Disk space critical
      - alert: DiskSpaceCritical
        expr: instance_device:disk_utilization:ratio > 0.90
        for: 10m
        labels:
          severity: critical
          team: sre
        annotations:
          summary: "CRITICAL: Disk space very low on {{ $labels.instance }}"
          description: "Disk {{ $labels.device }} is {{ $value | humanizePercentage }} full on {{ $labels.instance }}"

      # Disk will fill in 4 hours
      - alert: DiskWillFillSoon
        expr: |
          predict_linear(node_filesystem_avail_bytes[1h], 4*3600) < 0
        for: 30m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Disk will fill in 4 hours on {{ $labels.instance }}"
          description: "Disk {{ $labels.device }} is predicted to fill in 4 hours on {{ $labels.instance }}"
```

#### Application-Specific Alerts
```yaml
groups:
  - name: application_alerts
    rules:
      # Database connection pool exhaustion
      - alert: DatabaseConnectionPoolExhaustion
        expr: |
          (
            db_connections_in_use
            /
            db_connections_max
          ) > 0.90
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "Database connection pool near exhaustion"
          description: "Connection pool usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

      # High goroutine count
      - alert: HighGoroutineCount
        expr: go_goroutines > 10000
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High goroutine count on {{ $labels.job }}"
          description: "Goroutine count is {{ $value }} on {{ $labels.instance }}"

      # Cache hit rate low
      - alert: LowCacheHitRate
        expr: job:cache_hit_ratio:rate5m < 0.80
        for: 30m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "Low cache hit rate on {{ $labels.job }}"
          description: "Cache hit rate is {{ $value | humanizePercentage }} on {{ $labels.job }}"

      # Queue depth high
      - alert: HighQueueDepth
        expr: queue_depth > 1000
        for: 15m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High queue depth on {{ $labels.job }}"
          description: "Queue depth is {{ $value }} on {{ $labels.queue }}"
```

#### SLO-Based Alerts
```yaml
groups:
  - name: slo_alerts
    rules:
      # Fast burn: 2% error budget consumed in 1 hour (30x burn rate)
      - alert: SLOFastBurn
        expr: |
          (
            1 - service:availability:ratio_rate5m
          ) / (1 - 0.999) > 30
        for: 5m
        labels:
          severity: critical
          team: sre
          page: "true"
        annotations:
          summary: "CRITICAL: Fast SLO error budget burn for {{ $labels.service }}"
          description: "Error budget burning at {{ $value }}x rate for {{ $labels.service }}"

      # Slow burn: 10% error budget consumed in 24 hours (2.5x burn rate)
      - alert: SLOSlowBurn
        expr: |
          (
            1 - service:availability:ratio_rate5m
          ) / (1 - 0.999) > 2.5
        for: 1h
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Slow SLO error budget burn for {{ $labels.service }}"
          description: "Error budget burning at {{ $value }}x rate for {{ $labels.service }}"
```

#### Prometheus Self-Monitoring
```yaml
groups:
  - name: prometheus_alerts
    rules:
      # Prometheus scrape failures
      - alert: PrometheusScrapeFailing
        expr: up == 0
        for: 5m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Prometheus cannot scrape {{ $labels.job }}"
          description: "{{ $labels.instance }} has been down for more than 5 minutes"

      # Prometheus target disappeared
      - alert: PrometheusTargetDisappeared
        expr: |
          sum by (job) (up) <
          count by (job) (up offset 1h) * 0.8
        for: 10m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Prometheus targets have disappeared for {{ $labels.job }}"
          description: "20% or more targets have disappeared for {{ $labels.job }}"

      # Prometheus config reload failed
      - alert: PrometheusConfigReloadFailed
        expr: prometheus_config_last_reload_successful == 0
        for: 5m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Prometheus config reload failed"
          description: "Prometheus {{ $labels.instance }} config reload failed"

      # Prometheus TSDB compaction failed
      - alert: PrometheusTSDBCompactionFailed
        expr: rate(prometheus_tsdb_compactions_failed_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Prometheus TSDB compaction failed"
          description: "Prometheus {{ $labels.instance }} TSDB compaction failed"

      # Prometheus too many restarts
      - alert: PrometheusTooManyRestarts
        expr: changes(process_start_time_seconds[15m]) > 2
        for: 0m
        labels:
          severity: warning
          team: sre
        annotations:
          summary: "Prometheus has restarted multiple times"
          description: "Prometheus {{ $labels.instance }} has restarted {{ $value }} times in 15 minutes"
```

---

## Best Practices

### PromQL Best Practices

1. **Use rate() for counters, not increase()**
   ```promql
   # Good
   rate(http_requests_total[5m])

   # Avoid for alerting
   increase(http_requests_total[5m])
   ```

2. **Choose appropriate time ranges**
   - For rate calculations: At least 4x scrape interval (5m is common)
   - For alerting: Consider your target response time

3. **Use recording rules for complex queries**
   - Precompute expensive queries
   - Improve dashboard performance
   - Simplify alerting rules

4. **Avoid high cardinality labels**
   - Don't use user IDs, email addresses, or request IDs as labels
   - Limit label values to a reasonable set

5. **Use histogram_quantile correctly**
   ```promql
   # Good: Aggregate before quantile calculation
   histogram_quantile(0.95,
     sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
   )

   # Bad: Quantile of aggregation
   quantile(0.95, rate(http_request_duration_seconds[5m]))
   ```

### Recording Rules Best Practices

1. **Follow naming conventions**
   - Format: `level:metric:operations`
   - Be consistent across your organization

2. **Create hierarchical rules**
   - Start with high-cardinality, specific rules
   - Aggregate to lower-cardinality rules

3. **Set appropriate evaluation intervals**
   - Balance between freshness and resource usage
   - Default: 30s to 1m for most rules

4. **Document your rules**
   - Add comments explaining purpose
   - Link to related documentation

### Alerting Best Practices

1. **Use the `for` clause**
   - Avoid alerting on transient issues
   - Balance between false positives and response time

2. **Implement alert severity levels**
   - **Critical**: Page someone immediately
   - **Warning**: Create a ticket, notify during business hours
   - **Info**: Log for visibility

3. **Provide actionable annotations**
   ```yaml
   annotations:
     summary: "Clear, concise summary"
     description: "Detailed description with context"
     runbook_url: "Link to troubleshooting steps"
     dashboard_url: "Link to relevant dashboard"
   ```

4. **Use multi-window multi-burn-rate for SLOs**
   - Detect both fast and slow error budget burns
   - Reduce alert fatigue

5. **Avoid alert fatigue**
   - Don't alert on every possible issue
   - Alert on symptoms, not causes
   - Group related alerts

6. **Test your alerts**
   - Use Prometheus recording rules to simulate conditions
   - Verify alerts fire as expected
   - Test notification routing

### Label Best Practices

1. **Keep label cardinality low**
   - Each unique label combination creates a new time series
   - High cardinality increases memory usage

2. **Use consistent label names**
   - `job`: Type of service
   - `instance`: Individual instance (host:port)
   - `environment`: prod, staging, dev
   - `service`: Service name
   - `region`: Geographic region

3. **Avoid changing labels**
   - Label changes create new time series
   - Use label_replace() in queries if needed

### Performance Optimization

1. **Use recording rules for dashboard queries**
   - Precompute expensive aggregations
   - Reduce query latency

2. **Limit query time ranges**
   - Shorter ranges = faster queries
   - Use recording rules for long-term trends

3. **Optimize regex matching**
   - Be as specific as possible
   - Avoid `.*` when unnecessary

4. **Use federation for large deployments**
   - Hierarchical Prometheus setup
   - Aggregate data at different levels
