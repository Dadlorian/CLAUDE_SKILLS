# Performance Metrics Reference

## Overview

Comprehensive guide to key performance indicators (KPIs) for capacity planning and performance monitoring.

## Metric Categories

### 1. Application Performance Metrics
### 2. Infrastructure Metrics
### 3. Business Metrics
### 4. User Experience Metrics
### 5. Cost Metrics

---

## Application Performance Metrics

### Response Time / Latency

#### Definition
Time taken to complete a request from start to finish.

#### Key Percentiles
```
p50 (median)  : 50% of requests complete within this time
p95           : 95% of requests complete within this time
p99           : 99% of requests complete within this time
p99.9         : 99.9% of requests complete within this time
```

#### SLA Targets (Industry Standards)
```yaml
Web Applications:
  p50: < 100ms
  p95: < 300ms
  p99: < 1000ms

APIs:
  p50: < 50ms
  p95: < 200ms
  p99: < 500ms

Database Queries:
  p50: < 10ms
  p95: < 50ms
  p99: < 100ms

Microservices (internal):
  p50: < 20ms
  p95: < 100ms
  p99: < 200ms
```

#### Measurement
```javascript
// k6 example
import { Trend } from 'k6/metrics';

let responseTrend = new Trend('response_time');

export default function() {
  let start = Date.now();
  let response = http.get('https://api.example.com/users');
  let duration = Date.now() - start;

  responseTrend.add(duration);
}
```

#### Prometheus Query
```promql
# 95th percentile response time
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# Average response time
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

### Throughput (Requests Per Second)

#### Definition
Number of requests processed per unit of time.

#### Targets
```yaml
Small Application:  100-1,000 RPS
Medium Application: 1,000-10,000 RPS
Large Application:  10,000-100,000 RPS
Massive Scale:      100,000+ RPS (Netflix, Amazon scale)
```

#### Measurement
```promql
# Current RPS
rate(http_requests_total[1m])

# Peak RPS (last 24 hours)
max_over_time(rate(http_requests_total[1m])[24h:1m])

# RPS by endpoint
sum by (endpoint) (rate(http_requests_total[5m]))
```

#### Capacity Planning Formula
```
Required Capacity = Peak RPS × Safety Factor
Safety Factor = 1.5 to 3.0 (Netflix uses 3x)

Example:
Peak RPS: 50,000
Safety Factor: 2.0
Required Capacity: 100,000 RPS
```

### Error Rate

#### Definition
Percentage of failed requests out of total requests.

#### Targets
```yaml
Critical Services: < 0.01% (99.99% success)
Production Services: < 0.1% (99.9% success)
Non-Critical: < 1% (99% success)
```

#### Error Classifications
```yaml
4xx Errors:
  - Client errors
  - Don't usually count against SLA
  - Track for debugging

5xx Errors:
  - Server errors
  - Count against SLA
  - Immediate alerting

Timeouts:
  - Service unavailable
  - Count against SLA
  - May indicate capacity issues
```

#### Measurement
```promql
# Overall error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Error rate by service
sum by (service) (rate(http_requests_total{status=~"5.."}[5m])) /
sum by (service) (rate(http_requests_total[5m])) * 100
```

### Apdex Score (Application Performance Index)

#### Definition
User satisfaction metric based on response time.

#### Calculation
```
Apdex = (Satisfied + (Tolerating / 2)) / Total Samples

Satisfied: Response time <= T
Tolerating: T < Response time <= 4T
Frustrated: Response time > 4T

Where T = Target response time (e.g., 500ms)
```

#### Interpretation
```yaml
1.00 - 0.94: Excellent
0.93 - 0.85: Good
0.84 - 0.70: Fair
0.69 - 0.50: Poor
< 0.50:      Unacceptable
```

#### Example
```javascript
// k6 custom metric
import { Rate } from 'k6/metrics';

const apdexSatisfied = new Rate('apdex_satisfied');
const apdexTolerating = new Rate('apdex_tolerating');

const T = 500; // 500ms target

export default function() {
  let response = http.get('https://api.example.com/users');
  let duration = response.timings.duration;

  if (duration <= T) {
    apdexSatisfied.add(1);
  } else if (duration <= 4 * T) {
    apdexTolerating.add(1);
  }
}
```

---

## Infrastructure Metrics

### CPU Utilization

#### Targets
```yaml
Production Nodes:
  Average: 50-70%
  Peak: < 80%
  Alert: > 85%

Database Servers:
  Average: 40-60%
  Peak: < 75%
  Alert: > 80%

Batch/Worker Nodes:
  Average: 70-85%
  Peak: < 95%
  Alert: > 90%
```

#### Monitoring
```promql
# Average CPU across cluster
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100

# Per-node CPU
100 - (avg by (instance) (
  rate(node_cpu_seconds_total{mode="idle"}[5m])
) * 100)

# Container CPU usage
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod_name) * 100
```

#### Capacity Thresholds
```yaml
Scale Up Triggers:
  - Average > 70% for 5 minutes
  - Any node > 85% for 2 minutes

Scale Down Triggers:
  - Average < 30% for 15 minutes
  - All nodes < 50% for 10 minutes
```

### Memory Utilization

#### Targets
```yaml
Application Pods:
  Usage: 60-80% of request
  Alert: > 90% of request

Database Pods:
  Usage: 70-85% of request
  Alert: > 95% of request

Cache (Redis/Memcached):
  Usage: 75-90% of capacity
  Alert: > 95% of capacity
```

#### Monitoring
```promql
# Node memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Container memory usage
container_memory_usage_bytes / container_spec_memory_limit_bytes * 100

# Memory working set (more accurate)
container_memory_working_set_bytes / container_spec_memory_limit_bytes * 100
```

#### Memory Leak Detection
```promql
# Memory growth rate
deriv(container_memory_usage_bytes[1h])

# Alert if growing > 10MB per minute
deriv(container_memory_usage_bytes[5m]) > 10485760
```

### Network I/O

#### Metrics to Track
```yaml
Bandwidth:
  - Bytes sent/received per second
  - Network utilization %
  - Saturation points

Connections:
  - Active connections
  - Connection rate
  - Connection errors

Latency:
  - RTT (Round Trip Time)
  - Packet loss
  - Jitter
```

#### Monitoring
```promql
# Network bandwidth (receive)
rate(node_network_receive_bytes_total[5m])

# Network bandwidth (transmit)
rate(node_network_transmit_bytes_total[5m])

# Connection count
node_netstat_Tcp_CurrEstab

# Packet drops
rate(node_network_receive_drop_total[5m])
```

#### Targets
```yaml
Bandwidth Utilization:
  Normal: < 50%
  Peak: < 70%
  Alert: > 80%

Connection Limits:
  Per Node: 10,000-50,000
  Per Pod: 100-1,000
  Alert: > 80% of limit

Latency:
  Same AZ: < 1ms
  Cross AZ: < 5ms
  Cross Region: < 50ms
```

### Disk I/O

#### Metrics
```yaml
IOPS:
  - Read operations per second
  - Write operations per second
  - Total IOPS

Throughput:
  - MB/s read
  - MB/s write

Latency:
  - Average read latency
  - Average write latency
  - p99 latency

Utilization:
  - % time disk is busy
```

#### Monitoring
```promql
# Disk IOPS
rate(node_disk_reads_completed_total[5m]) +
rate(node_disk_writes_completed_total[5m])

# Disk throughput (MB/s)
(rate(node_disk_read_bytes_total[5m]) +
 rate(node_disk_written_bytes_total[5m])) / 1024 / 1024

# Disk utilization %
rate(node_disk_io_time_seconds_total[5m]) * 100
```

#### Targets
```yaml
SSD/NVMe:
  IOPS: < 80% of provisioned
  Throughput: < 70% of max
  Latency: < 10ms (p99)

HDD:
  IOPS: < 100 per disk
  Throughput: < 100 MB/s
  Latency: < 50ms (p99)

EBS (AWS):
  gp3: 16,000 IOPS, 1000 MB/s
  io2: Up to 64,000 IOPS, 1000 MB/s
```

---

## Business Metrics

### Conversion Rate

#### Definition
Percentage of users who complete a desired action.

#### Examples
```yaml
E-commerce:
  - Add to cart rate
  - Checkout completion rate
  - Purchase completion rate

SaaS:
  - Trial to paid conversion
  - Feature adoption rate
  - Upgrade rate

Content:
  - Video watch completion rate
  - Article read completion rate
  - Click-through rate
```

#### Impact of Performance
```yaml
Performance Impact Study (Amazon):
  100ms latency increase → 1% revenue decrease

Google Study:
  500ms delay → 20% traffic drop

Netflix Finding:
  Each second of startup delay → 6% viewer drop
```

### Revenue Per Request

#### Calculation
```
RPR = Total Revenue / Total Requests

Example:
Daily Revenue: $1,000,000
Daily Requests: 100,000,000
RPR: $0.01 per request
```

#### Capacity Planning
```yaml
Cost-Benefit Analysis:
  Infrastructure Cost: $10,000/month
  Requests Served: 1,000,000,000
  Revenue Generated: $10,000,000
  ROI: 100x

Acceptable Cost per Request: < RPR / 10
```

### Service Level Objectives (SLOs)

#### Netflix SLO Example
```yaml
Video Playback Service:
  SLO: 99.9% availability
  Error Budget: 0.1% (43 minutes/month)

  Metrics:
    - Successful stream starts: > 99.9%
    - Video quality: HD or better for > 95%
    - Rebuffer rate: < 0.5%
    - Startup time: < 1 second for 90%
```

#### Amazon SLO Example
```yaml
Amazon.com Homepage:
  SLO: 99.99% availability
  Error Budget: 0.01% (4 minutes/month)

  Metrics:
    - Page load time: < 1 second for 99%
    - Search availability: > 99.99%
    - Add to cart success: > 99.95%
    - Checkout completion: > 99.9%
```

---

## User Experience Metrics

### Core Web Vitals (Google)

#### Largest Contentful Paint (LCP)
```yaml
Definition: Time to render largest content element
Targets:
  Good: < 2.5 seconds
  Needs Improvement: 2.5 - 4.0 seconds
  Poor: > 4.0 seconds
```

#### First Input Delay (FID)
```yaml
Definition: Time from user interaction to browser response
Targets:
  Good: < 100ms
  Needs Improvement: 100 - 300ms
  Poor: > 300ms
```

#### Cumulative Layout Shift (CLS)
```yaml
Definition: Visual stability during page load
Targets:
  Good: < 0.1
  Needs Improvement: 0.1 - 0.25
  Poor: > 0.25
```

### Video Streaming Metrics (Netflix Focus)

#### Video Start Time
```yaml
Definition: Time from play button to video playback

Netflix Targets:
  Excellent: < 1 second
  Good: 1-2 seconds
  Acceptable: 2-3 seconds
  Poor: > 3 seconds

Factors:
  - CDN response time
  - Manifest parsing
  - DRM negotiation
  - Initial chunk download
  - Buffer initialization
```

#### Rebuffer Rate
```yaml
Definition: Frequency of playback interruptions

Netflix Targets:
  Excellent: < 0.1%
  Good: 0.1 - 0.5%
  Acceptable: 0.5 - 1.0%
  Poor: > 1.0%

Causes:
  - Insufficient bandwidth
  - Network congestion
  - CDN overload
  - Client-side issues
```

#### Stream Quality
```yaml
Video Quality Distribution:
  4K: 30% (target market dependent)
  HD (1080p): 50%
  SD (720p): 15%
  Low: 5%

Quality Metrics:
  - Initial quality selection accuracy
  - Quality switching frequency
  - Time to optimal quality
  - Quality degradation events
```

---

## Cost Metrics

### Cost Per Request

#### Calculation
```
CPR = Infrastructure Cost / Total Requests

Example:
Monthly Infrastructure: $50,000
Monthly Requests: 5,000,000,000
CPR: $0.00001 per request
```

#### Industry Benchmarks
```yaml
Web Applications:
  High Scale: $0.000001 - $0.00001 per request
  Medium Scale: $0.0001 - $0.001 per request
  Small Scale: $0.001 - $0.01 per request

API Services:
  High Efficiency: < $0.000001 per request
  Standard: $0.00001 - $0.0001 per request

Video Streaming (Netflix):
  Streaming: $0.0001 - $0.001 per hour
  Encoding: $0.01 - $0.10 per hour
```

### Resource Efficiency

#### Compute Efficiency
```yaml
Requests per vCPU:
  Excellent: > 10,000 RPS
  Good: 1,000 - 10,000 RPS
  Average: 100 - 1,000 RPS
  Poor: < 100 RPS

Cost per vCPU-hour:
  On-Demand: $0.05 - $0.20
  Reserved: $0.03 - $0.12
  Spot: $0.01 - $0.06
```

#### Storage Efficiency
```yaml
Data Transfer:
  Same AZ: Free
  Cross AZ: $0.01 per GB
  Internet Egress: $0.09 per GB

Storage Costs:
  S3 Standard: $0.023 per GB/month
  S3 Intelligent: $0.0125 per GB/month
  EBS gp3: $0.08 per GB/month
  EBS io2: $0.125 per GB/month + IOPS cost
```

### Cost Optimization Metrics

#### Spot Instance Usage
```yaml
Target Spot Percentage:
  Stateless Services: 70-90%
  Batch Jobs: 90-100%
  Databases: 0-10%

Spot Savings:
  Average: 60-70% vs On-Demand
  m5.large: $0.096/hr → $0.029/hr (70% savings)
```

#### Reserved Instance Utilization
```yaml
Target Utilization:
  Reserved Instances: > 95%
  Savings Plans: > 90%

Commitment Period:
  1 Year: 30-40% savings
  3 Year: 50-60% savings
```

---

## Capacity Planning Formulas

### Peak Capacity Calculation
```
Required Capacity = (Peak Load × Growth Factor × Safety Factor) / Efficiency

Where:
- Peak Load: Historical maximum (e.g., 50,000 RPS)
- Growth Factor: Expected growth (e.g., 1.5 for 50% growth)
- Safety Factor: Buffer for spikes (e.g., 2.0)
- Efficiency: Resource utilization target (e.g., 0.7 for 70%)

Example:
Required = (50,000 × 1.5 × 2.0) / 0.7
Required = 214,286 RPS capacity
```

### Server Count Calculation
```
Required Servers = Required Capacity / (Server Capacity × Availability)

Where:
- Required Capacity: From above (214,286 RPS)
- Server Capacity: Per-server capability (e.g., 5,000 RPS)
- Availability: Uptime factor (e.g., 0.99 for 99%)

Example:
Required = 214,286 / (5,000 × 0.99)
Required = 44 servers
```

### Cost Projection
```
Monthly Cost = (Server Count × Server Cost × Hours) + (Storage + Network + Other)

Example:
Servers: 44 × $0.096/hr × 730 hrs = $3,086
Storage: 1TB × $0.08 = $80
Network: 10TB × $0.09 = $900
Total: $4,066/month
```

---

## Netflix-Specific Metrics

### Regional Capacity
```yaml
Capacity Distribution:
  US-East: 35%
  US-West: 20%
  Europe: 25%
  Asia: 15%
  Other: 5%

Regional Metrics:
  - Concurrent streams per region
  - CDN cache hit rate per region
  - Origin request rate per region
  - Cross-region failover capacity
```

### Content Delivery
```yaml
CDN Performance:
  Cache Hit Rate: > 95%
  Origin Offload: > 90%
  Edge Response Time: < 50ms

Encoding Pipeline:
  Throughput: 1000s of titles/day
  Quality Profiles: 4K, HD, SD, Mobile
  Codec: AV1, H.265, H.264, VP9

Storage:
  Original Content: Petabytes
  Encoded Versions: 10x original
  Total Storage: Exabytes
```

---

## Amazon-Specific Metrics

### Retail Metrics
```yaml
Peak Traffic Events:
  Prime Day: 5-10x normal traffic
  Black Friday: 3-5x normal traffic
  Holiday Season: 2-3x sustained

Critical Paths:
  Homepage: 99.99% availability
  Product Search: 99.99% availability
  Add to Cart: 99.95% availability
  Checkout: 99.9% availability

Performance Targets:
  Time to First Byte: < 100ms
  Page Load Time: < 1 second
  API Response: < 200ms
  Search Results: < 500ms
```

### AWS Service Metrics
```yaml
EC2:
  Availability: 99.99% SLA
  Launch Time: < 2 minutes
  Spot Interruption: 2-hour notice

S3:
  Durability: 99.999999999%
  Availability: 99.9-99.99%
  Request Rate: 5,500 GET/s, 3,500 PUT/s per prefix

Lambda:
  Cold Start: 100-1000ms
  Warm Invocation: 1-10ms overhead
  Concurrent Executions: 1,000 default, 10,000s possible
```

---

## Monitoring Dashboard Structure

### Executive Dashboard
```yaml
Panels:
  1. Overall Health (Green/Yellow/Red)
  2. Current RPS vs Capacity
  3. Error Rate (Last 24h)
  4. Active Users
  5. Revenue vs Target
  6. Cost vs Budget
  7. SLO Compliance
```

### Operations Dashboard
```yaml
Panels:
  1. Response Time (p50, p95, p99)
  2. Throughput by Service
  3. Error Rate by Endpoint
  4. CPU/Memory Utilization
  5. Autoscaler Status
  6. Node Count
  7. Database Performance
  8. Cache Hit Rate
```

### Capacity Dashboard
```yaml
Panels:
  1. Current vs Peak Capacity
  2. Growth Trend (30 days)
  3. Resource Utilization
  4. Scaling Events
  5. Cost Trend
  6. Efficiency Metrics
  7. Forecast (next 30 days)
```

---

## Alerting Thresholds

### Critical Alerts (Page On-Call)
```yaml
- Error rate > 1% for 5 minutes
- p99 latency > 2x baseline for 5 minutes
- Service availability < 99.9%
- CPU > 90% for 5 minutes
- Memory > 95% for 2 minutes
- Disk > 90% full
- PagerDuty integration required
```

### Warning Alerts (Slack Notification)
```yaml
- Error rate > 0.5% for 10 minutes
- p99 latency > 1.5x baseline for 10 minutes
- CPU > 80% for 10 minutes
- Memory > 85% for 10 minutes
- Disk > 80% full
- Autoscaler scaling frequently
```

### Info Alerts (Dashboard Only)
```yaml
- Traffic 2x normal
- Autoscaler triggered
- New deployment in progress
- Capacity at 70%
- Cost increase > 10%
```

---

## Performance Testing Benchmarks

### Load Test Targets
```yaml
Normal Load Test:
  RPS: Average daily peak
  Duration: 15-30 minutes
  Success Criteria: < 0.1% errors, p95 < SLO

Stress Test:
  RPS: 150% of capacity
  Duration: Until failure
  Success Criteria: Graceful degradation

Soak Test:
  RPS: Average load
  Duration: 24 hours
  Success Criteria: No memory leaks, stable performance

Spike Test:
  RPS: 0 → 10x → 0 in seconds
  Duration: Multiple spikes
  Success Criteria: Quick recovery, no crashes
```

---

## References

- [Netflix Tech Blog - Performance](https://netflixtechblog.com/tagged/performance)
- [Amazon Builders' Library](https://aws.amazon.com/builders-library/)
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Core Web Vitals](https://web.dev/vitals/)
- [DORA Metrics](https://www.devops-research.com/research.html)
