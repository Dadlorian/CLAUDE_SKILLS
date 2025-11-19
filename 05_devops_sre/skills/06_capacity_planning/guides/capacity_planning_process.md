# Capacity Planning Process Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Capacity Planning Framework](#capacity-planning-framework)
3. [Data Collection and Analysis](#data-collection-and-analysis)
4. [Forecasting Methods](#forecasting-methods)
5. [Load Testing and Validation](#load-testing-and-validation)
6. [Cost Optimization](#cost-optimization)
7. [Netflix Practices](#netflix-practices)
8. [Amazon Practices](#amazon-practices)
9. [Capacity Planning Workflow](#capacity-planning-workflow)
10. [Tools and Automation](#tools-and-automation)

---

## Introduction

Capacity planning ensures your infrastructure can handle current and future demand while optimizing costs and maintaining performance SLAs.

### Key Objectives

1. **Availability**: Ensure resources are available when needed
2. **Performance**: Maintain response times within SLOs
3. **Cost Efficiency**: Optimize resource utilization
4. **Scalability**: Plan for growth
5. **Risk Mitigation**: Prepare for peak events

### Capacity Planning Cycle

```
┌─────────────────────────────────────────────┐
│  1. Data Collection                         │
│     - Current usage metrics                 │
│     - Historical trends                     │
│     - Business forecasts                    │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  2. Analysis                                │
│     - Identify patterns                     │
│     - Resource utilization                  │
│     - Bottlenecks                           │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  3. Forecasting                             │
│     - Growth projections                    │
│     - Capacity requirements                 │
│     - Peak planning                         │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  4. Testing                                 │
│     - Load testing                          │
│     - Validation                            │
│     - Stress testing                        │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  5. Implementation                          │
│     - Resource provisioning                 │
│     - Autoscaling configuration             │
│     - Deployment                            │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  6. Monitoring & Review                     │
│     - Performance tracking                  │
│     - Cost analysis                         │
│     - Continuous improvement                │
└──────────────────┬──────────────────────────┘
                   ↓
                (Repeat)
```

---

## Capacity Planning Framework

### 1. Define Service Level Objectives (SLOs)

```yaml
Example SLOs:
  Availability:
    Production: 99.99% uptime
    Staging: 99.5% uptime

  Performance:
    API Response Time:
      p50: < 100ms
      p95: < 300ms
      p99: < 500ms

    Page Load Time:
      p50: < 1s
      p95: < 2s
      p99: < 3s

  Throughput:
    Minimum: 10,000 RPS
    Peak: 50,000 RPS
    Burst: 100,000 RPS (30 seconds)

  Error Rate:
    Maximum: < 0.1% (99.9% success)
```

### 2. Identify Capacity Dimensions

```yaml
Compute:
  - CPU cores
  - Memory (GB)
  - GPU units (if applicable)

Storage:
  - Disk space (TB)
  - IOPS
  - Throughput (MB/s)

Network:
  - Bandwidth (Gbps)
  - Packets per second
  - Connections

Application:
  - Concurrent users
  - Requests per second
  - Transactions per minute
  - Active sessions

Database:
  - Queries per second
  - Connection pool size
  - Replication lag

Cache:
  - Hit rate
  - Memory usage
  - Eviction rate
```

### 3. Set Safety Margins

```yaml
Netflix Approach:
  Safety Factor: 3x
  Reasoning: Handle regional failover + traffic spike

  Example:
    Expected Peak: 50,000 RPS
    Capacity: 150,000 RPS (3x)

Amazon Approach:
  Safety Factor: 2x
  Reasoning: Peak event preparation

  Example:
    Expected Peak: 100,000 RPS
    Capacity: 200,000 RPS (2x)

Standard Approach:
  Safety Factor: 1.5x
  Reasoning: Cost-performance balance

  Example:
    Expected Peak: 20,000 RPS
    Capacity: 30,000 RPS (1.5x)
```

---

## Data Collection and Analysis

### Metrics to Collect

#### 1. Resource Utilization

```promql
# CPU utilization (average over time)
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) by (instance) * 100

# Memory utilization
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Network bandwidth
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

#### 2. Application Metrics

```promql
# Request rate
rate(http_requests_total[5m])

# Response time percentiles
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Active connections
sum(nginx_connections_active)
```

#### 3. Business Metrics

```yaml
User Activity:
  - Daily Active Users (DAU)
  - Monthly Active Users (MAU)
  - Peak concurrent users
  - Session duration

Transactions:
  - Orders per minute
  - Checkout completions
  - Payment processing
  - Content consumption

Growth Metrics:
  - User growth rate
  - Traffic growth rate
  - Data growth rate
  - Feature adoption
```

### Historical Analysis

#### Trend Analysis
```python
# Example: Analyze traffic growth
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load historical data
df = pd.read_csv('traffic_data.csv', parse_dates=['date'])
df['days_since_start'] = (df['date'] - df['date'].min()).dt.days

# Linear regression
model = LinearRegression()
X = df[['days_since_start']]
y = df['requests_per_second']
model.fit(X, y)

# Forecast 90 days ahead
future_days = np.array([[df['days_since_start'].max() + i] for i in range(1, 91)])
forecast = model.predict(future_days)

print(f"Current RPS: {y.iloc[-1]:.0f}")
print(f"Projected RPS (90 days): {forecast[-1]:.0f}")
print(f"Growth rate: {((forecast[-1] / y.iloc[-1]) - 1) * 100:.1f}%")
```

#### Seasonality Analysis
```python
# Identify weekly patterns
df['hour_of_week'] = df['date'].dt.dayofweek * 24 + df['date'].dt.hour
hourly_avg = df.groupby('hour_of_week')['requests_per_second'].mean()

# Peak hours
peak_hour = hourly_avg.idxmax()
peak_value = hourly_avg.max()
avg_value = hourly_avg.mean()

print(f"Peak hour: {peak_hour} (Day {peak_hour//24}, Hour {peak_hour%24})")
print(f"Peak RPS: {peak_value:.0f}")
print(f"Average RPS: {avg_value:.0f}")
print(f"Peak/Average ratio: {peak_value/avg_value:.2f}x")
```

#### Event-Driven Spikes
```yaml
Historical Events:
  Black Friday 2023:
    Peak: 250,000 RPS (5x normal)
    Duration: 8 hours
    Preparation: 6x normal capacity

  Product Launch:
    Peak: 180,000 RPS (3.6x normal)
    Duration: 2 hours
    Preparation: 4x normal capacity

  Marketing Campaign:
    Peak: 120,000 RPS (2.4x normal)
    Duration: 4 hours
    Preparation: 3x normal capacity
```

---

## Forecasting Methods

### 1. Linear Forecasting

**Use Case**: Steady, predictable growth

```python
# Simple linear projection
current_rps = 50000
monthly_growth_rate = 0.05  # 5% monthly growth
months_ahead = 12

projected_rps = current_rps * ((1 + monthly_growth_rate) ** months_ahead)
print(f"Projected RPS in {months_ahead} months: {projected_rps:.0f}")

# Required capacity (with 2x safety factor)
required_capacity = projected_rps * 2
print(f"Required capacity: {required_capacity:.0f}")
```

### 2. Time Series Forecasting

**Use Case**: Complex patterns with seasonality

```python
from prophet import Prophet
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'ds': dates,  # Date column
    'y': rps_values  # Metric column
})

# Create and fit model
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
model.fit(df)

# Make forecast
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

# Extract predictions
predicted_rps = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

### 3. Machine Learning Forecasting

**Use Case**: Complex, multi-variable predictions

```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

# Features: day of week, hour, month, marketing spend, etc.
X = df[['day_of_week', 'hour', 'month', 'marketing_spend', 'user_count']]
y = df['requests_per_second']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict future capacity needs
future_X = pd.DataFrame({
    'day_of_week': [5],  # Saturday
    'hour': [20],  # 8 PM
    'month': [12],  # December
    'marketing_spend': [100000],
    'user_count': [1000000]
})

predicted_rps = model.predict(future_X)
```

### 4. Percentile-Based Planning

**Use Case**: Conservative planning for unknown patterns

```python
# Use historical p95 or p99 as baseline
historical_data = [...]  # List of daily peak RPS values

p95_value = np.percentile(historical_data, 95)
p99_value = np.percentile(historical_data, 99)

# Plan for p95 + growth
growth_factor = 1.3  # 30% growth
capacity_needed = p95_value * growth_factor * 2  # 2x safety factor

print(f"P95 historical: {p95_value:.0f} RPS")
print(f"Required capacity: {capacity_needed:.0f} RPS")
```

---

## Load Testing and Validation

### Capacity Test Plan

#### 1. Baseline Test
```yaml
Objective: Establish current capacity

Configuration:
  Load Pattern: Gradual ramp to average load
  Duration: 30 minutes
  VUs: Start 0, ramp to average, sustain

Metrics:
  - Response time at average load
  - Error rate
  - Resource utilization
  - Throughput
```

#### 2. Peak Load Test
```yaml
Objective: Validate capacity for peak traffic

Configuration:
  Load Pattern: Ramp to historical peak
  Duration: 15 minutes at peak
  VUs: Match peak concurrent users

Success Criteria:
  - p95 response time < 500ms
  - Error rate < 0.1%
  - CPU < 80%
  - Memory < 85%
```

#### 3. Stress Test
```yaml
Objective: Find breaking point

Configuration:
  Load Pattern: Ramp beyond capacity
  Duration: Until degradation
  VUs: Exceed expected maximum by 50%

Observe:
  - At what load does performance degrade?
  - What fails first (CPU, memory, network)?
  - Is degradation graceful?
  - Recovery time after load removal
```

#### 4. Soak Test
```yaml
Objective: Verify stability over time

Configuration:
  Load Pattern: Sustained average load
  Duration: 24 hours
  VUs: Average concurrent users

Monitor:
  - Memory leaks (growing memory usage)
  - Resource degradation over time
  - Database connection pool exhaustion
  - Cache effectiveness
```

### Example k6 Capacity Test

```javascript
// capacity-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
let errorRate = new Rate('errors');
let responseTime = new Trend('response_time');

export let options = {
  stages: [
    // Baseline
    { duration: '5m', target: 100 },   // Average load
    { duration: '10m', target: 100 },

    // Peak
    { duration: '5m', target: 500 },   // Historical peak
    { duration: '15m', target: 500 },

    // Stress
    { duration: '5m', target: 1000 },  // 2x peak
    { duration: '10m', target: 1000 },

    // Beyond capacity
    { duration: '5m', target: 1500 },  // 3x peak
    { duration: '5m', target: 1500 },

    // Recovery
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // Warning if exceeded
    'errors': ['rate<0.01'],
  },
};

export default function() {
  let res = http.get('https://api.example.com/users');

  let success = check(res, {
    'status 200': (r) => r.status === 200,
  });

  errorRate.add(!success);
  responseTime.add(res.timings.duration);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'capacity-test-results.json': JSON.stringify(data),
  };
}
```

---

## Cost Optimization

### Cost Analysis Framework

#### 1. Current Cost Breakdown
```yaml
Monthly Infrastructure Cost: $50,000

Compute (60%): $30,000
  - EC2 instances: $20,000
  - EKS control plane: $2,000
  - Lambda: $3,000
  - Other: $5,000

Storage (20%): $10,000
  - EBS volumes: $4,000
  - S3: $5,000
  - Snapshots: $1,000

Network (15%): $7,500
  - Data transfer: $5,000
  - Load balancers: $2,500

Database (5%): $2,500
  - RDS: $2,000
  - ElastiCache: $500
```

#### 2. Cost Optimization Strategies

**Compute Optimization**
```yaml
1. Right-Sizing:
   Current: m5.2xlarge (8 vCPU, 32GB)
   Actual Usage: 40% CPU, 50% memory
   Recommended: m5.xlarge (4 vCPU, 16GB)
   Savings: 50% ($10,000/month)

2. Spot Instances:
   Current: 100% On-Demand
   Target: 70% Spot, 30% On-Demand
   Savings: 45% ($9,000/month)

3. Reserved Instances:
   Commitment: 1-year for baseline capacity
   Coverage: 40% of compute
   Savings: 30% ($3,600/month)

4. Autoscaling Optimization:
   Current: Fixed 50 instances
   Target: 20-80 instances (autoscaling)
   Average: 35 instances
   Savings: 30% ($6,000/month)
```

**Storage Optimization**
```yaml
1. Lifecycle Policies:
   S3 Standard → Infrequent Access (30 days)
   Savings: 40% on storage ($2,000/month)

2. EBS Volume Optimization:
   Remove unused volumes: $500/month
   Right-size volumes: $1,000/month
   gp2 → gp3 migration: $400/month

3. Snapshot Management:
   Delete old snapshots (>30 days)
   Savings: $500/month
```

**Network Optimization**
```yaml
1. Data Transfer:
   Use CloudFront for static content
   Reduce cross-region transfer
   Savings: $2,000/month

2. Load Balancer:
   Consolidate ALBs
   Use NLB where appropriate
   Savings: $500/month
```

**Total Potential Savings: $35,500/month (71%)**

### Cost Per Request Optimization

```python
# Calculate current cost per request
monthly_requests = 100_000_000_000  # 100B requests
monthly_cost = 50_000  # $50,000

cost_per_request = monthly_cost / monthly_requests
print(f"Current cost per request: ${cost_per_request:.10f}")

# After optimization
optimized_cost = 14_500  # $14,500
optimized_cost_per_request = optimized_cost / monthly_requests
print(f"Optimized cost per request: ${optimized_cost_per_request:.10f}")

# Improvement
improvement = (1 - (optimized_cost / monthly_cost)) * 100
print(f"Cost improvement: {improvement:.1f}%")
```

---

## Netflix Practices

### 1. Regional Failover Planning

```yaml
Strategy:
  - Each region must handle 100% traffic
  - Global capacity = 3x normal (3 regions × 100%)
  - Any 1 region can fail without impact

Example:
  Normal Global Traffic: 1M RPS
  Per Region Capacity: 1M RPS
  Total Global Capacity: 3M RPS

Implementation:
  - Active-active architecture
  - Continuous cross-region testing
  - Automated failover mechanisms
  - Regional isolation
```

### 2. Chaos Engineering Integration

```yaml
Capacity Validation:
  1. Simulate region failure during load test
  2. Inject latency and measure impact
  3. Test autoscaling under failure conditions
  4. Validate backup capacity

Example Test:
  - Start: Normal load (500K RPS across 3 regions)
  - Action: Fail entire region (US-East)
  - Expected: Traffic shifts to US-West and EU (each handles 250K RPS more)
  - Validate: No degradation, autoscaling responds
```

### 3. Continuous Load Testing

```yaml
Production Load Testing:
  - Run low-level tests in production
  - Gradually increase to validate autoscaling
  - Monitor real user impact
  - Automated rollback on issues

Tools:
  - Custom load generators
  - Synthetic traffic mixed with real traffic
  - Real-time monitoring and alerting
```

### 4. Capacity Modeling

```python
# Netflix-style capacity model
class CapacityModel:
    def __init__(self):
        self.regions = ['us-east', 'us-west', 'eu-west']
        self.safety_factor = 3.0

    def calculate_capacity(self, expected_peak_rps):
        # Each region should handle full load
        per_region_capacity = expected_peak_rps * self.safety_factor
        total_capacity = per_region_capacity * len(self.regions)

        return {
            'expected_peak': expected_peak_rps,
            'per_region': per_region_capacity,
            'total': total_capacity,
            'regions': len(self.regions)
        }

    def simulate_failover(self, total_capacity, failed_regions=1):
        active_regions = len(self.regions) - failed_regions
        per_region_load = total_capacity / active_regions
        return per_region_load

# Example
model = CapacityModel()
capacity = model.calculate_capacity(500000)  # 500K RPS expected peak
print(f"Per region capacity: {capacity['per_region']:.0f} RPS")
print(f"Total capacity: {capacity['total']:.0f} RPS")

# Simulate one region failure
failover_load = model.simulate_failover(capacity['expected_peak'], 1)
print(f"Load per region after failover: {failover_load:.0f} RPS")
```

---

## Amazon Practices

### 1. GameDays

```yaml
GameDay Structure:
  Preparation (2 weeks):
    - Define scenarios
    - Set up monitoring
    - Brief teams
    - Prepare runbooks

  Execution (4 hours):
    - Baseline load test
    - Introduce planned events (sales, launches)
    - Inject failures
    - Test autoscaling
    - Validate alerts

  Review (1 week):
    - Analyze results
    - Document issues
    - Update capacity plans
    - Improve automation

Scenarios:
  1. Black Friday simulation
  2. Regional failure
  3. Database failover
  4. DDoS attack
  5. Code deployment under load
```

### 2. Incremental Load Testing

```yaml
Amazon Approach:
  Week 1: Test at 50% of expected peak
  Week 2: Test at 75% of expected peak
  Week 3: Test at 100% of expected peak
  Week 4: Test at 150% of expected peak (stress)

Benefits:
  - Identify issues early
  - Gradual confidence building
  - Time to fix problems
  - Reduced risk

Example Schedule:
  June 1: 50K RPS test
  June 8: 75K RPS test
  June 15: 100K RPS test
  June 22: 150K RPS test
  June 30: Prime Day event (100K RPS expected)
```

### 3. Cell-Based Architecture

```yaml
Concept:
  - Partition users into isolated "cells"
  - Each cell has complete stack
  - Blast radius limited to one cell

Capacity Planning:
  - Plan per-cell capacity
  - Number of cells based on user count
  - Add cells for growth

Example:
  Users per Cell: 100,000
  Total Users: 10,000,000
  Number of Cells: 100

  Peak RPS per User: 0.5
  Peak RPS per Cell: 50,000
  Cell Capacity: 100,000 RPS (2x safety)
```

### 4. Predictive Scaling

```yaml
Strategy:
  - Analyze historical patterns
  - Pre-scale before known events
  - Use ML for predictions
  - Automated scheduling

Implementation:
  Known Events:
    - Prime Day: Pre-scale to 5x capacity
    - Lightning Deals: Pre-scale 30 min before
    - Marketing Emails: Pre-scale at send time

  Pattern-Based:
    - Monday 9 AM: Scale up 30 min early
    - Friday 5 PM: Scale up 1 hour early
    - Holiday Season: Sustained higher capacity
```

---

## Capacity Planning Workflow

### Monthly Capacity Review

```yaml
Week 1: Data Collection
  - Gather last 30 days metrics
  - Analyze peak loads
  - Identify anomalies
  - Review costs

Week 2: Forecasting
  - Project growth (next 90 days)
  - Identify upcoming events
  - Calculate capacity needs
  - Estimate costs

Week 3: Testing
  - Execute load tests
  - Validate autoscaling
  - Test failure scenarios
  - Document results

Week 4: Implementation
  - Adjust capacity
  - Update autoscaling policies
  - Optimize costs
  - Document changes
```

### Quarterly Capacity Planning

```yaml
Quarter Review:
  1. Business Alignment
     - Product roadmap
     - User growth targets
     - New features
     - Marketing campaigns

  2. Technical Assessment
     - Infrastructure review
     - Performance analysis
     - Cost optimization
     - Technology updates

  3. Capacity Projection
     - 12-month forecast
     - Major event planning
     - Budget allocation
     - Risk assessment

  4. Strategic Initiatives
     - Architecture improvements
     - Scaling enhancements
     - Cost reduction projects
     - Automation opportunities
```

### Event-Driven Planning

```yaml
Major Event Checklist (T-minus timeline):

T-8 weeks:
  - Define expected load (peak RPS, duration)
  - Review historical data from similar events
  - Calculate required capacity
  - Get budget approval

T-6 weeks:
  - Provision additional capacity
  - Configure autoscaling
  - Set up enhanced monitoring
  - Create runbooks

T-4 weeks:
  - Execute load tests
  - Test autoscaling
  - Validate monitoring
  - Train on-call team

T-2 weeks:
  - Run full-scale test
  - Verify all systems
  - Final capacity check
  - Communication plan

T-1 week:
  - Freeze changes
  - Pre-scale infrastructure
  - War room setup
  - Final review

T-0 (Event Day):
  - Monitor real-time
  - War room active
  - Rapid response ready
  - Communicate status

T+1 week:
  - Post-mortem
  - Document lessons learned
  - Update capacity model
  - Celebrate success
```

---

## Tools and Automation

### Capacity Planning Dashboard

```python
# Example: Grafana dashboard JSON
{
  "dashboard": {
    "title": "Capacity Planning Dashboard",
    "panels": [
      {
        "title": "Current vs Capacity",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m]))",
          "legendFormat": "Current RPS"
        }, {
          "expr": "vector(100000)",
          "legendFormat": "Capacity"
        }]
      },
      {
        "title": "Growth Trend (30 days)",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m]))",
          "legendFormat": "RPS"
        }]
      },
      {
        "title": "Resource Utilization",
        "targets": [{
          "expr": "avg(rate(node_cpu_seconds_total{mode!='idle'}[5m])) * 100",
          "legendFormat": "CPU %"
        }, {
          "expr": "(1 - avg(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
          "legendFormat": "Memory %"
        }]
      },
      {
        "title": "Cost Trend",
        "targets": [{
          "expr": "sum(aws_cost_explorer_cost)",
          "legendFormat": "Daily Cost"
        }]
      }
    ]
  }
}
```

### Automated Capacity Reports

```python
# capacity_report.py
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class CapacityReport:
    def __init__(self, prometheus_url):
        self.prometheus_url = prometheus_url

    def get_metrics(self, query, days=30):
        # Query Prometheus for metrics
        # Implementation depends on your setup
        pass

    def generate_report(self):
        # Collect data
        rps_data = self.get_metrics('rate(http_requests_total[5m])')
        cpu_data = self.get_metrics('avg(rate(node_cpu_seconds_total[5m]))')

        # Calculate statistics
        current_rps = rps_data[-1]
        avg_rps = rps_data.mean()
        p95_rps = rps_data.quantile(0.95)

        # Forecast (simple linear)
        growth_rate = (rps_data[-1] - rps_data[0]) / rps_data[0]
        projected_30d = current_rps * (1 + growth_rate)
        projected_90d = current_rps * ((1 + growth_rate) ** 3)

        # Capacity recommendation
        required_capacity = projected_90d * 2  # 2x safety factor

        # Generate report
        report = f"""
        Capacity Planning Report - {datetime.now().strftime('%Y-%m-%d')}

        Current Metrics:
        - Current RPS: {current_rps:.0f}
        - Average RPS (30d): {avg_rps:.0f}
        - P95 RPS: {p95_rps:.0f}

        Projections:
        - 30-day forecast: {projected_30d:.0f} RPS
        - 90-day forecast: {projected_90d:.0f} RPS
        - Growth rate: {growth_rate*100:.1f}%

        Recommendations:
        - Required capacity: {required_capacity:.0f} RPS
        - Current headroom: {((required_capacity - current_rps) / current_rps * 100):.1f}%

        Action Items:
        - Review autoscaling policies
        - Conduct load test at {projected_90d:.0f} RPS
        - Plan for {required_capacity:.0f} RPS capacity
        """

        return report

# Usage
reporter = CapacityReport('http://prometheus:9090')
print(reporter.generate_report())
```

### Automated Load Testing

```bash
#!/bin/bash
# scheduled-load-test.sh

# Configuration
TEST_SCRIPT="capacity-test.js"
RESULTS_DIR="./load-test-results"
DATE=$(date +%Y-%m-%d)

# Create results directory
mkdir -p $RESULTS_DIR

# Run k6 test
k6 run \
  --out json=$RESULTS_DIR/results-$DATE.json \
  --out influxdb=http://influxdb:8086/k6 \
  $TEST_SCRIPT

# Analyze results
python3 analyze_results.py $RESULTS_DIR/results-$DATE.json

# Send notification
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -d "channel=#capacity-planning" \
  -d "text=Load test completed. Results: $RESULTS_DIR/results-$DATE.json"
```

**Cron schedule** (weekly on Sundays at 2 AM):
```cron
0 2 * * 0 /path/to/scheduled-load-test.sh
```

---

## References

- [Google SRE Book - Capacity Planning](https://sre.google/sre-book/handling-overload/)
- [Netflix Tech Blog - Capacity Planning](https://netflixtechblog.com/preparing-the-netflix-api-for-deployment-786d8f58090d)
- [Amazon Builders' Library - Load Testing](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Capacity Planning Spreadsheet Template](https://docs.google.com/spreadsheets/d/...)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/load-testing-best-practices/)
