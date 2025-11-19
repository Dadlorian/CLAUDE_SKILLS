# Prometheus Reference

## Overview

Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It features a multi-dimensional data model, powerful query language (PromQL), and efficient time-series database.

## Architecture

```
[Targets] → [Prometheus Server] → [Storage]
              ↓            ↑
         [PromQL]    [Service Discovery]
              ↓
         [Alertmanager] → [Notifications]
              ↓
         [Grafana/UI]
```

### Components

#### Prometheus Server
- Scrapes and stores metrics
- Evaluates recording and alerting rules
- Serves PromQL queries
- Built-in web UI

#### Pushgateway
- Accepts metrics pushed from batch jobs
- Exposes metrics for Prometheus to scrape
- Use sparingly (mainly for batch jobs)

#### Alertmanager
- Receives alerts from Prometheus
- Deduplicates, groups, routes alerts
- Sends notifications (email, Slack, PagerDuty)

#### Exporters
- Expose metrics from third-party systems
- Node Exporter (system metrics)
- Blackbox Exporter (probing)
- Custom exporters

## Installation

### Binary
```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz

# Extract
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Run
./prometheus --config.file=prometheus.yml
```

### Docker
```bash
docker run -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Kubernetes (Helm)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

## Configuration

### prometheus.yml
```yaml
# Global configuration
global:
  scrape_interval: 15s      # How often to scrape targets
  evaluation_interval: 15s  # How often to evaluate rules
  external_labels:
    cluster: 'prod-us-east-1'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Rule files
rule_files:
  - 'alerts/*.yml'
  - 'rules/*.yml'

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node1:9100'
          - 'node2:9100'
        labels:
          environment: 'production'

  # Application metrics
  - job_name: 'api'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'api1:8080'
          - 'api2:8080'

  # Kubernetes service discovery
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

## Metric Types

### Counter
```python
from prometheus_client import Counter

# Define
requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Use
requests_total.labels(method='GET', endpoint='/api/users', status='200').inc()
requests_total.labels(method='POST', endpoint='/api/orders', status='201').inc(5)
```

### Gauge
```python
from prometheus_client import Gauge

# Define
temperature = Gauge(
    'room_temperature_celsius',
    'Room temperature in Celsius',
    ['room']
)

# Use
temperature.labels(room='server-room').set(22.5)
temperature.labels(room='office').inc()     # +1
temperature.labels(room='storage').dec(2)   # -2
```

### Histogram
```python
from prometheus_client import Histogram

# Define
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Use
with request_duration.labels(method='GET', endpoint='/api/users').time():
    process_request()

# Or manually
request_duration.labels(method='POST', endpoint='/api/orders').observe(0.245)
```

### Summary
```python
from prometheus_client import Summary

# Define
request_latency = Summary(
    'http_request_latency_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Use
with request_latency.labels(method='GET', endpoint='/api/users').time():
    process_request()
```

## PromQL

### Basic Queries

#### Instant Vector Selectors
```promql
# Exact match
http_requests_total{method="GET"}

# Regex match
http_requests_total{status=~"2.."}

# Negative match
http_requests_total{status!="200"}

# Negative regex
http_requests_total{status!~"5.."}

# Multiple labels
http_requests_total{method="GET", status="200"}
```

#### Range Vector Selectors
```promql
# Last 5 minutes
http_requests_total[5m]

# Last 1 hour
http_requests_total[1h]

# Last 1 day
http_requests_total[1d]
```

### Rate and Increase

```promql
# Rate per second over 5 minutes
rate(http_requests_total[5m])

# Instant rate (last two points)
irate(http_requests_total[5m])

# Total increase over 5 minutes
increase(http_requests_total[5m])

# Delta for gauge
delta(cpu_temp_celsius[5m])
```

### Aggregation

```promql
# Sum across all dimensions
sum(http_requests_total)

# Sum by label
sum(http_requests_total) by (method)

# Sum without label (keep all except status)
sum(http_requests_total) without (status)

# Average
avg(http_request_duration_seconds)

# Min/Max
max(http_request_duration_seconds) by (endpoint)
min(http_request_duration_seconds) by (endpoint)

# Count
count(http_requests_total)

# Count values
count_values("status", http_requests_total)

# Standard deviation
stddev(http_request_duration_seconds)

# Quantile
quantile(0.95, http_request_duration_seconds)
```

### Math Operations

```promql
# Addition
node_memory_total_bytes + 1000000

# Subtraction
node_memory_total_bytes - node_memory_available_bytes

# Multiplication
rate(requests_total[5m]) * 60

# Division
sum(rate(http_requests_total{status="500"}[5m])) /
sum(rate(http_requests_total[5m]))

# Modulo
node_filesystem_size_bytes % 1000000

# Power
node_cpu_usage ^ 2
```

### Comparison Operators

```promql
# Greater than
cpu_usage_percent > 80

# Less than
disk_free_bytes < 1000000000

# Equal
up == 1

# Not equal
up != 0

# Greater or equal
memory_usage_percent >= 90

# Less or equal
network_errors <= 10
```

### Logical Operators

```promql
# AND
(cpu_usage > 80) and (memory_usage > 80)

# OR
(cpu_usage > 90) or (memory_usage > 90)

# UNLESS (exclude)
up unless on (instance) down
```

### Functions

#### Rate/Increase
```promql
rate(metric[5m])        # Per-second average rate
irate(metric[5m])       # Instant rate
increase(metric[5m])    # Total increase
delta(metric[5m])       # Difference (for gauges)
idelta(metric[5m])      # Instant delta
```

#### Aggregation Over Time
```promql
avg_over_time(metric[5m])
min_over_time(metric[5m])
max_over_time(metric[5m])
sum_over_time(metric[5m])
count_over_time(metric[5m])
stddev_over_time(metric[5m])
quantile_over_time(0.95, metric[5m])
```

#### Prediction
```promql
# Predict value in 4 hours
predict_linear(disk_used_bytes[1h], 4*3600)

# Derivative
deriv(metric[5m])
```

#### Sorting
```promql
# Top 5 by value
topk(5, http_requests_total)

# Bottom 3
bottomk(3, http_requests_total)

# Sort ascending
sort(http_requests_total)

# Sort descending
sort_desc(http_requests_total)
```

#### Time Functions
```promql
time()                  # Current timestamp
hour()                  # Hour of day (0-23)
day_of_week()          # Day of week (0-6)
day_of_month()         # Day of month (1-31)
month()                # Month (1-12)
year()                 # Year
```

#### Math Functions
```promql
abs(metric)            # Absolute value
ceil(metric)           # Round up
floor(metric)          # Round down
round(metric)          # Round to nearest
exp(metric)            # Exponential
ln(metric)             # Natural log
log2(metric)           # Log base 2
log10(metric)          # Log base 10
sqrt(metric)           # Square root
```

#### Label Functions
```promql
# Replace label
label_replace(metric, "new_label", "$1", "old_label", "(.*)")

# Join labels
label_join(metric, "new_label", ",", "label1", "label2")
```

### Histogram Quantiles

```promql
# 95th percentile from histogram
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# Per endpoint
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# Multiple percentiles
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))  # p50
histogram_quantile(0.90, rate(http_request_duration_seconds_bucket[5m]))  # p90
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # p99
```

### Subqueries

```promql
# Max rate over last hour (sampled every 5m)
max_over_time(
  rate(requests_total[5m])[1h:5m]
)

# Moving average
avg_over_time(
  rate(requests_total[5m])[10m:1m]
)
```

## Recording Rules

### Purpose
- Pre-calculate expensive queries
- Improve dashboard performance
- Reduce query complexity

### Configuration
```yaml
# rules/recording_rules.yml
groups:
  - name: http_metrics
    interval: 30s
    rules:
      # Request rate per job
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)

      # Error ratio per job
      - record: job:http_errors:ratio
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)

      # 95th percentile latency per job
      - record: job:http_request_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le)
          )

  - name: node_metrics
    interval: 30s
    rules:
      # CPU usage per instance
      - record: instance:node_cpu:ratio
        expr: |
          1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)

      # Memory usage per instance
      - record: instance:node_memory:ratio
        expr: |
          (
            node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
          ) / node_memory_MemTotal_bytes

      # Disk usage per instance and device
      - record: instance:node_disk:ratio
        expr: |
          (
            node_filesystem_size_bytes - node_filesystem_avail_bytes
          ) / node_filesystem_size_bytes
```

## Alerting Rules

```yaml
# alerts/alert_rules.yml
groups:
  - name: instance_alerts
    interval: 30s
    rules:
      # Instance down
      - alert: InstanceDown
        expr: up == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
          description: "{{ $labels.instance }} has been down for more than 5 minutes."

      # High CPU
      - alert: HighCPU
        expr: instance:node_cpu:ratio > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanizePercentage }}."

      # High Memory
      - alert: HighMemory
        expr: instance:node_memory:ratio > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }}."

      # Disk space low
      - alert: DiskSpaceLow
        expr: instance:node_disk:ratio > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk {{ $labels.device }} is {{ $value | humanizePercentage }} full."

  - name: application_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: job:http_errors:ratio > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}."

      # High latency
      - alert: HighLatency
        expr: job:http_request_duration:p95 > 1.0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.job }}"
          description: "p95 latency is {{ $value }}s."
```

## Service Discovery

### Static Configuration
```yaml
scrape_configs:
  - job_name: 'static'
    static_configs:
      - targets:
          - 'server1:9090'
          - 'server2:9090'
        labels:
          environment: 'production'
```

### File-Based Discovery
```yaml
scrape_configs:
  - job_name: 'file'
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/*.json'
          - '/etc/prometheus/targets/*.yml'
        refresh_interval: 5m
```

```json
# targets.json
[
  {
    "targets": ["server1:9090", "server2:9090"],
    "labels": {
      "job": "api",
      "environment": "production"
    }
  }
]
```

### Kubernetes Discovery
```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
```

### EC2 Discovery
```yaml
scrape_configs:
  - job_name: 'ec2'
    ec2_sd_configs:
      - region: us-east-1
        port: 9100
    relabel_configs:
      - source_labels: [__meta_ec2_tag_Name]
        target_label: instance
```

### Consul Discovery
```yaml
scrape_configs:
  - job_name: 'consul'
    consul_sd_configs:
      - server: 'consul.example.com:8500'
        services: ['api', 'web']
```

## Relabeling

### Use Cases
- Modify labels before scraping
- Filter targets
- Add/remove labels
- Modify metric names

### Actions
```yaml
relabel_configs:
  # Keep targets matching regex
  - source_labels: [__meta_kubernetes_pod_label_app]
    action: keep
    regex: 'my-app'

  # Drop targets matching regex
  - source_labels: [__meta_kubernetes_pod_label_app]
    action: drop
    regex: 'test-.*'

  # Replace label value
  - source_labels: [__meta_ec2_tag_Name]
    target_label: instance
    action: replace

  # Hash source labels
  - source_labels: [__address__]
    target_label: __tmp_hash
    action: hashmod
    modulus: 4

  # Label map (copy all matching labels)
  - action: labelmap
    regex: __meta_kubernetes_pod_label_(.+)

  # Drop labels
  - action: labeldrop
    regex: __meta_kubernetes_pod_label_.*
```

## Storage and Retention

### Configuration
```yaml
# Command line flags
--storage.tsdb.path=/prometheus/data
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=50GB
```

### Remote Write (Long-term Storage)
```yaml
remote_write:
  - url: "https://prometheus-remote-storage.example.com/api/v1/write"
    basic_auth:
      username: user
      password: pass
    queue_config:
      capacity: 10000
      max_shards: 50
      min_shards: 1
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'expensive_metric'
        action: drop
```

### Remote Read
```yaml
remote_read:
  - url: "https://prometheus-remote-storage.example.com/api/v1/read"
    read_recent: true
```

## High Availability

### Prometheus Federation
```yaml
# Central Prometheus scrapes from local Prometheus instances
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="prometheus"}'
        - '{__name__=~"job:.*"}'
    static_configs:
      - targets:
          - 'prometheus-1:9090'
          - 'prometheus-2:9090'
```

### Thanos
- Long-term storage for Prometheus
- Global query view across clusters
- Downsampling and compaction
- Object storage backend (S3, GCS)

### Cortex
- Multi-tenant Prometheus
- Horizontal scalability
- Long-term storage
- High availability

## Best Practices

### Naming
```
# Pattern: <namespace>_<name>_<unit>_<suffix>
http_requests_total
http_request_duration_seconds
node_memory_usage_bytes
process_cpu_seconds_total
```

### Labels
```yaml
Good (low cardinality):
  - method: GET, POST, PUT, DELETE (~10 values)
  - status: 200, 404, 500 (~20 values)
  - region: us-east-1, eu-west-1 (~10 values)

Bad (high cardinality):
  - user_id (millions of users)
  - request_id (unique per request)
  - timestamp (infinite values)
```

### Cardinality
```promql
# Check cardinality
count({__name__=~".+"}) by (__name__)

# Check series count
prometheus_tsdb_symbol_table_size_bytes
```

## Troubleshooting

### Check Target Health
```
http://localhost:9090/targets
```

### Check Configuration
```bash
promtool check config prometheus.yml
promtool check rules alerts/*.yml
```

### Query Performance
```promql
# Slow queries
topk(10, prometheus_engine_query_duration_seconds)

# Most queried metrics
topk(10, prometheus_http_requests_total{handler="/api/v1/query"})
```

## Tools

- **Prometheus**: Core server
- **Alertmanager**: Alert routing
- **Pushgateway**: Metrics from batch jobs
- **Node Exporter**: System metrics
- **Blackbox Exporter**: Probing endpoints
- **Grafana**: Visualization
- **Thanos**: Long-term storage and HA
- **Cortex**: Multi-tenant Prometheus
