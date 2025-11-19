# Capacity Planning - Elite Professional Practices

**Resource forecasting, optimization, and performance engineering at scale**

---

## Overview

Capacity Planning ensures systems have adequate resources to handle current and future demand while minimizing costs. It's the discipline of understanding system limits, predicting growth, and provisioning resources proactively to avoid outages while maximizing resource utilization.

You are an expert in capacity planning methodologies that enable organizations to serve billions of users reliably while maintaining cost efficiency and performance SLOs.

## Core Principles

### 1. Demand Forecasting

Understanding usage patterns and projecting future demand.

```
# Time series forecasting example
Historical data points:
Jan: 1M users    Apr: 1.5M   Jul: 2M    Oct: 2.5M
Feb: 1.1M users  May: 1.6M   Aug: 2.1M  Nov: 2.7M
Mar: 1.2M users  Jun: 1.8M   Sep: 2.2M  Dec: 3M (holiday spike)

Trend: Growing ~5% per month baseline
Seasonality: 20% increase in Dec, 10% increase in summer
Growth: New market entry planned Q3 - expect 3x traffic

Forecast for next quarter:
Q1 Year2: 3.2M-3.5M users with 30% spike for holidays
```

**Forecasting Methods**:
- Time series analysis (historical trends)
- Growth-driven forecasting (business metrics)
- Product launch impact modeling
- Seasonal adjustment

### 2. Resource Modeling

Understanding resource consumption per unit of work.

```
# Example: API request resource consumption
Single request (worst case):
- CPU: 10 milliseconds of compute
- Memory: 5 MB (request context)
- Database: 2 queries, average 50ms each
- Cache: 1 lookup + 1 write

Per 1,000 requests per second:
- CPU: 10 cores (assuming 1000ms per core available)
- Memory: 5 GB dedicated
- Database: 2,000 queries/sec
- Bandwidth: ~500 Mbps

Add headroom:
- CPU: 15 cores (50% headroom for peaks)
- Memory: 7.5 GB
- Database: 4,000 queries/sec capacity (2x actual)
- Bandwidth: 1 Gbps links (2x actual)
```

### 3. Headroom and Buffer Sizing

```
# Conservative headroom strategy
Measured peak: 5,000 requests/sec
Headroom: 50%
Provisioned capacity: 7,500 requests/sec

# Headroom levels by confidence
80th percentile load: +20% headroom
95th percentile load: +30% headroom
Peak load + growth: +50% headroom

Example:
Expected: 1,000 rps
95th percentile spike: 1,300 rps
6-month growth projection: 1,500 rps
Provisioned: 1,800 rps (headroom to 2,000)
```

## Core Competencies

### 1. Load Testing and Validation

```bash
# k6 load testing example
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  let response = http.get('https://api.example.com/products');

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}

# Run load test
k6 run load_test.js
# Results show p95 latency, error rates, throughput
```

**Load Testing Stages**:
1. **Baseline Testing**: Measure current performance
2. **Soak Testing**: Run at expected load for hours (memory leaks)
3. **Stress Testing**: Push past expected limits (find breaking point)
4. **Spike Testing**: Sudden traffic increase (how system recovers)
5. **Breakpoint Testing**: Incremental increase until failure

### 2. Autoscaling Configuration

```yaml
# Kubernetes Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale up when 70% utilized
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Scale up when 80% utilized
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50                        # Max 50% decrease per scaling
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30    # Scale up quickly (30 sec)
      policies:
      - type: Percent
        value: 100                       # Can double per scaling
        periodSeconds: 30
```

**Autoscaling Metrics**:
- CPU utilization (% of requested CPU)
- Memory utilization (% of requested memory)
- Custom metrics (requests/sec, queue depth, etc.)
- External metrics (Prometheus queries)

### 3. Database Scaling Strategies

```
# Vertical Scaling (bigger machine)
Pro: Simple, no application changes
Con: Eventually hit limit, brief downtime

# Horizontal Scaling
Pro: Unlimited scaling, no single point of failure
Con: Complex (sharding, replication)

# Read Replicas
- Master receives writes
- Replicas handle reads
- Eventual consistency acceptable
- Adds read capacity without sharding

# Sharding
- Partition data by customer ID, region, etc.
- Each shard on separate database
- Application routes queries to correct shard
- Most complex, highest scaling potential

# Caching Layer
- Add Redis/Memcached in front of database
- Reduces database load
- Trades consistency for performance
- Cache invalidation critical
```

### 4. Cost Optimization

```python
# Cost analysis for cloud resources
def analyze_costs():
    # Monthly costs
    compute = {
        'prod': 8000,     # 50 instances x $160/month
        'staging': 1200,  # 7 instances
        'dev': 400,       # 2 instances
    }

    database = {
        'prod': 3000,     # Multi-AZ RDS
        'staging': 500,   # Single node
        'dev': 100,       # Smallest instance
    }

    storage = {
        'prod': 2000,     # High IOPS
        'staging': 300,
        'dev': 50,
    }

    # Optimization opportunities
    opportunities = [
        ('Reserved instances', compute['prod'], 30),  # 30% savings
        ('Spot instances for workers', 500, 70),     # 70% savings
        ('Auto-scaling in staging', 600, 40),        # 40% savings
        ('Database optimization', database['prod'], 20),  # 20% savings
    ]

    total_monthly = sum(compute.values()) + sum(database.values()) + sum(storage.values())
    # Total: ~$15,550/month

    potential_savings = sum([opp[1] * (opp[2]/100) for opp in opportunities])
    # Potential: ~$3,000/month savings (19%)
```

## Technology Stack

### k6 (Load Testing)

**Modern, scriptable load testing tool**

```javascript
// Complex load test with custom logic
import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'https://api.example.com';

export let options = {
  vus: 50,           // 50 virtual users
  duration: '10m',   // 10 minute test
};

export default function () {
  // Create product
  let productRes = http.post(BASE_URL + '/products', {
    name: `Product ${Math.random()}`,
    price: 99.99,
  });

  check(productRes, {
    'product created': (r) => r.status === 201,
  });

  // Get product
  let getRes = http.get(BASE_URL + `/products/${productRes.body.id}`);
  check(getRes, {
    'product retrieved': (r) => r.status === 200,
  });

  // Delete product
  let deleteRes = http.delete(BASE_URL + `/products/${productRes.body.id}`);
  check(deleteRes, {
    'product deleted': (r) => r.status === 204,
  });
}
```

### JMeter (Legacy Load Testing)

**Apache project for load and performance testing**

```
Features:
- GUI and command-line modes
- Protocol support: HTTP, FTP, JDBC, SOAP, etc.
- Distributed testing (multiple machines)
- Detailed reporting and graphs
- Good for traditional applications
```

### Kubernetes HPA

**Automatic pod scaling based on metrics**

### AWS Auto Scaling

**Cloud-native auto-scaling for EC2, RDS, Lambda**

### Prometheus + Grafana

**Metrics collection and visualization for capacity planning**

## Implementation Patterns

### Traffic Forecast and Capacity Model

```
# Baseline capacity
Current: 10,000 rps peak
Growth: 20% per quarter
Seasonal: 2x spike during holidays

Quarter Forecast:
Q1: 12,000 rps peak (20% growth)
Q2: 14,400 rps peak
Q3: 17,280 rps peak
Q4: 34,560 rps peak (2x for holidays)

Required provisioning:
Q1: 18,000 rps capacity (50% headroom)
Q2: 21,600 rps capacity
Q3: 25,920 rps capacity
Q4: 51,840 rps capacity (during holidays)

Cost impact:
Phase 1 (Q1-Q2): +$50K/month
Phase 2 (Q3): +$100K/month
Phase 3 (Q4): +$200K/month (temporary)
```

### On-Demand Scaling for Events

```bash
# Example: Sales event planning
Normal peak: 5,000 rps
Expected spike: 50,000 rps
Desired headroom: 30%
Provisioned: 65,000 rps capacity

Scaling timeline:
T-1 hour: Warm up caches, run smoke tests
T-0 min: Scale to 2x normal (10,000 rps)
T+5 min: Monitor metrics
T+30 min: Scale to full capacity if needed (65,000 rps)
T+1 hour post-event: Scale back gradually
```

## Best Practices

### 1. Measure Baseline Performance

```bash
# Establish performance baseline
# Before scaling anything, measure current system
- Peak throughput (rps)
- Latency distribution (p50, p95, p99)
- Resource utilization (CPU, memory, disk, network)
- Error rates
- Database query performance

# Tools
ApacheBench: ab -c 100 -n 10000 https://example.com
wrk: wrk -c 100 -d 10s https://example.com
```

### 2. Plan for Peak, Not Average

```
# Wrong (causes outages during peaks)
Provisioned for: Average load (1,000 rps)

# Right (ensures reliability during peaks)
Peak load from historical data: 5,000 rps
Growth projection: +30%: 6,500 rps
Headroom (50%): 9,750 rps
Provisioned capacity: 10,000 rps
```

### 3. Regular Load Testing

```
# Schedule load tests
- After every major deployment
- Before high-traffic events
- Quarterly regression tests
- After infrastructure changes
- After code optimizations (validate improvement)
```

### 4. Monitor Resource Utilization

```
# Key metrics to track
- CPU utilization (target: 60-70% peak)
- Memory utilization (target: 70-80% peak)
- Disk utilization (target: 70-80%)
- Network bandwidth (target: 60-70%)
- Database connections (target: 70-80%)

# Alert on trending
If utilization growing 5% per week:
- At current growth, capacity exhausted in ~3 weeks
- Plan scaling immediately
```

### 5. Cost vs Performance Trade-offs

```
# Evaluate options
Option 1: Over-provisioned (safe but expensive)
- Cost: $100K/month
- Risk: Low outage risk
- Utilization: 30-40% average

Option 2: Right-sized (balanced)
- Cost: $60K/month
- Risk: Medium outage risk (during unexpected spikes)
- Utilization: 60-70% average

Option 3: Under-provisioned (cheap but risky)
- Cost: $40K/month
- Risk: High outage risk
- Utilization: 80-90% average

Recommendation: Option 2 + Auto-scaling for unexpected spikes
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Netflix, Amazon, Google capacity planning practices
