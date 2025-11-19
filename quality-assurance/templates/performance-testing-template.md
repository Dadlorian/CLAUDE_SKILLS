# Performance Testing Template

Use this template when planning and executing performance testing for applications and APIs.

---

## Project Information

**System Under Test**: _________________
**Type**:
- [ ] Web Application
- [ ] Mobile Application
- [ ] API/Microservices
- [ ] Desktop Application

**Technology Stack**:
- Frontend: _________________
- Backend: _________________
- Database: _________________
- Infrastructure: _________________

---

## Performance Objectives

### Service Level Objectives (SLOs)

**Response Time SLOs**:
- p50 (median): < _____ ms
- p95: < _____ ms
- p99: < _____ ms
- p99.9: < _____ ms

**Throughput SLOs**:
- Requests per second: _____ RPS
- Concurrent users: _____ users
- Data throughput: _____ MB/s

**Availability SLOs**:
- Uptime: _____% (e.g., 99.9% = ~43 min downtime/month)
- Error rate: < _____%

**Resource Limits**:
- CPU utilization: < _____%
- Memory usage: < _____ GB
- Database connections: < _____
- Network bandwidth: < _____ MB/s

---

## Performance Test Types

### 1. Load Testing

**Purpose**: Verify system behavior under expected load

**Configuration**:
```javascript
// K6 Load Test Configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Sustain
    { duration: '2m', target: 200 },   // Step up
    { duration: '5m', target: 200 },   // Sustain
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],  // <1% errors
  },
};
```

**Expected Load**:
- Normal traffic: _____ concurrent users
- Peak traffic: _____ concurrent users
- Duration: _____ minutes

**Success Criteria**:
- [ ] All thresholds met
- [ ] No errors under load
- [ ] Resource utilization acceptable
- [ ] Response times within SLO

---

### 2. Stress Testing

**Purpose**: Find system breaking point

**Configuration**:
```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '5m', target: 500 },   // Push beyond normal
    { duration: '5m', target: 1000 },  // Continue increasing
    { duration: '5m', target: 2000 },  // Breaking point?
    { duration: '2m', target: 0 },
  ],
};
```

**Questions to Answer**:
- At what load does the system start degrading? _____
- Is degradation graceful or catastrophic? _____
- What is the maximum capacity? _____
- How does the system recover? _____

**Success Criteria**:
- [ ] Breaking point identified
- [ ] Graceful degradation observed
- [ ] System recovers after stress
- [ ] Bottlenecks documented

---

### 3. Spike Testing

**Purpose**: Test sudden traffic surges (Black Friday, product launch)

**Configuration**:
```javascript
export const options = {
  stages: [
    { duration: '1m', target: 100 },    // Normal load
    { duration: '10s', target: 5000 },  // Sudden spike!
    { duration: '3m', target: 5000 },   // Sustained spike
    { duration: '10s', target: 100 },   // Drop back
    { duration: '3m', target: 100 },    // Recovery
  ],
};
```

**Spike Scenarios**:
- Product launch: _____x normal traffic
- Flash sale: _____x normal traffic
- Marketing campaign: _____x normal traffic
- Viral content: _____x normal traffic

**Success Criteria**:
- [ ] System handles spike without crashes
- [ ] Auto-scaling kicks in (if applicable)
- [ ] Error rate stays within limits
- [ ] System recovers quickly after spike

---

### 4. Soak/Endurance Testing

**Purpose**: Detect memory leaks and resource exhaustion over time

**Configuration**:
```javascript
export const options = {
  stages: [
    { duration: '5m', target: 200 },    // Ramp up
    { duration: '24h', target: 200 },   // Sustain for long period
    { duration: '5m', target: 0 },      // Ramp down
  ],
};
```

**Duration**: _____ hours (typically 8-24 hours)

**Metrics to Monitor**:
- [ ] Memory usage trend (should be stable)
- [ ] File descriptor usage
- [ ] Database connection pool
- [ ] Cache hit/miss rate
- [ ] Garbage collection metrics
- [ ] Log file growth

**Success Criteria**:
- [ ] No memory leaks detected
- [ ] Resource usage stable over time
- [ ] No performance degradation
- [ ] System remains responsive

---

### 5. Breakpoint Testing

**Purpose**: Determine maximum system capacity

**Configuration**:
```javascript
export const options = {
  executor: 'ramping-arrival-rate',
  startRate: 50,
  timeUnit: '1s',
  preAllocatedVUs: 500,
  maxVUs: 5000,
  stages: [
    { target: 200, duration: '30m' },
    { target: 500, duration: '30m' },
    { target: 1000, duration: '30m' },
    { target: 2000, duration: '30m' },
  ],
};
```

**Maximum Capacity**:
- RPS at failure: _____
- Concurrent users at failure: _____
- Bottleneck identified: _____

**Success Criteria**:
- [ ] Maximum capacity determined
- [ ] Primary bottleneck identified
- [ ] Scaling recommendations documented

---

## Test Scenarios

### Critical User Journeys

**Scenario 1**: _________________
```javascript
export default function() {
  // User journey implementation
  group('Login', () => {
    // Login steps
  });

  group('Browse products', () => {
    // Browse steps
  });

  group('Add to cart', () => {
    // Add to cart steps
  });

  group('Checkout', () => {
    // Checkout steps
  });

  sleep(Math.random() * 3 + 2);  // Think time: 2-5 seconds
}
```

**Scenario 2**: _________________
**Scenario 3**: _________________

### API Endpoints to Test

Priority endpoints (highest traffic/criticality):

1. **Endpoint**: `GET /api/products`
   - Expected RPS: _____
   - SLO: p95 < _____ ms
   - Load pattern: _____

2. **Endpoint**: `POST /api/orders`
   - Expected RPS: _____
   - SLO: p95 < _____ ms
   - Load pattern: _____

3. **Endpoint**: `GET /api/users/{id}`
   - Expected RPS: _____
   - SLO: p95 < _____ ms
   - Load pattern: _____

---

## Test Environment

### Infrastructure Setup

**Test Environment**:
- Environment: _____ (staging, prod-like, dedicated perf env)
- Similarity to production: _____%
- Specifications:
  - CPU: _____
  - Memory: _____
  - Network: _____
  - Database: _____

**Load Generation**:
- Tool: _____ (K6, JMeter, Locust)
- Location: _____ (cloud, on-prem)
- Workers: _____ instances
- Total capacity: _____ virtual users

**Monitoring**:
- APM: _____ (DataDog, New Relic, Grafana)
- Logs: _____ (CloudWatch, ELK, Splunk)
- Infrastructure: _____ (Prometheus, CloudWatch)
- Database: _____ (database monitoring tool)

---

## Performance Testing Implementation

### K6 Complete Test Example

```javascript
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const checkoutDuration = new Trend('checkout_duration');

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{type:api}': ['p(95)<300'],
    errors: ['rate<0.01'],
    checks: ['rate>0.95'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.example.com';

export function setup() {
  // Setup: create test data if needed
  return { token: getAuthToken() };
}

export default function(data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  group('User Login', () => {
    const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
      username: 'testuser',
      password: 'password123'
    }), { headers });

    check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'login response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
  });

  group('Browse Products', () => {
    const productsRes = http.get(`${BASE_URL}/products`, {
      headers,
      tags: { type: 'api' }
    });

    check(productsRes, {
      'products status is 200': (r) => r.status === 200,
      'products returned': (r) => JSON.parse(r.body).length > 0,
    }) || errorRate.add(1);
  });

  group('Add to Cart', () => {
    const cartRes = http.post(`${BASE_URL}/cart`, JSON.stringify({
      productId: 'prod-123',
      quantity: 2
    }), { headers });

    check(cartRes, {
      'add to cart status is 201': (r) => r.status === 201,
    }) || errorRate.add(1);
  });

  group('Checkout', () => {
    const checkoutStart = Date.now();

    const checkoutRes = http.post(`${BASE_URL}/checkout`, JSON.stringify({
      paymentMethod: 'card',
      shippingAddress: 'test address'
    }), { headers });

    const duration = Date.now() - checkoutStart;
    checkoutDuration.add(duration);

    check(checkoutRes, {
      'checkout status is 200': (r) => r.status === 200,
      'order created': (r) => JSON.parse(r.body).orderId !== undefined,
    }) || errorRate.add(1);
  });

  sleep(Math.random() * 3 + 2);  // Think time: 2-5 seconds
}

export function teardown(data) {
  // Cleanup: delete test data if needed
}

function getAuthToken() {
  const res = http.post(`${BASE_URL}/auth/token`, {
    client_id: 'test-client',
    client_secret: 'secret'
  });
  return JSON.parse(res.body).access_token;
}
```

---

## Distributed Load Generation

### Docker Compose Setup

```yaml
version: '3.8'

services:
  influxdb:
    image: influxdb:1.8
    ports:
      - "8086:8086"
    environment:
      - INFLUXDB_DB=k6
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - influxdb

  k6-master:
    image: grafana/k6:latest
    command: run --out influxdb=http://influxdb:8086/k6 /scripts/load-test.js
    volumes:
      - ./scripts:/scripts
    environment:
      - BASE_URL=https://api.example.com
    depends_on:
      - influxdb

  k6-worker-1:
    image: grafana/k6:latest
    command: run --out influxdb=http://influxdb:8086/k6 /scripts/load-test.js
    volumes:
      - ./scripts:/scripts
    environment:
      - BASE_URL=https://api.example.com
    depends_on:
      - influxdb

  k6-worker-2:
    image: grafana/k6:latest
    command: run --out influxdb=http://influxdb:8086/k6 /scripts/load-test.js
    volumes:
      - ./scripts:/scripts
    environment:
      - BASE_URL=https://api.example.com
    depends_on:
      - influxdb
```

---

## Performance Profiling

### Application Profiling

**Node.js**:
```bash
# Using clinic.js
npm install -g clinic
clinic doctor -- node app.js

# Or built-in profiler
node --prof app.js
node --prof-process isolate-*.log > processed.txt
```

**Python**:
```bash
# Using py-spy
pip install py-spy
py-spy top --pid <pid>

# Or cProfile
python -m cProfile -o output.prof app.py
```

**Java**:
```bash
# Using JProfiler or async-profiler
java -agentpath:/path/to/libasyncProfiler.so -jar app.jar
```

### Database Profiling

**PostgreSQL**:
```sql
-- Enable slow query log
ALTER DATABASE mydb SET log_min_duration_statement = 1000;

-- Analyze specific query
EXPLAIN ANALYZE
SELECT * FROM users WHERE created_at > NOW() - INTERVAL '30 days';

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**MySQL**:
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- Analyze query
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

---

## Frontend Performance Testing

### Core Web Vitals

**Targets** (Google recommendations):
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1
- FCP (First Contentful Paint): < 1.8s
- TTFB (Time to First Byte): < 600ms

**Measurement** (Playwright):
```typescript
import { chromium } from 'playwright';
import { onLCP, onFID, onCLS } from 'web-vitals';

async function measureWebVitals(url: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(url);

  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      const vitals = {};
      onLCP((metric) => vitals.LCP = metric.value);
      onFID((metric) => vitals.FID = metric.value);
      onCLS((metric) => vitals.CLS = metric.value);
      setTimeout(() => resolve(vitals), 5000);
    });
  });

  await browser.close();
  return metrics;
}
```

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://staging.example.com
            https://staging.example.com/product
          budgetPath: ./budget.json
          uploadArtifacts: true
```

**Performance Budget** (budget.json):
```json
[
  {
    "path": "/*",
    "timings": [
      { "metric": "interactive", "budget": 3000 },
      { "metric": "first-contentful-paint", "budget": 1500 }
    ],
    "resourceSizes": [
      { "resourceType": "script", "budget": 300 },
      { "resourceType": "image", "budget": 500 },
      { "resourceType": "total", "budget": 1000 }
    ]
  }
]
```

---

## Metrics & Analysis

### Key Metrics to Track

**Response Time**:
- [ ] p50 (median)
- [ ] p95
- [ ] p99
- [ ] p99.9
- [ ] Max

**Throughput**:
- [ ] Requests per second
- [ ] Transactions per second
- [ ] Data throughput (MB/s)

**Error Rate**:
- [ ] HTTP 4xx errors
- [ ] HTTP 5xx errors
- [ ] Timeouts
- [ ] Connection failures

**Resource Utilization**:
- [ ] CPU usage (%)
- [ ] Memory usage (GB)
- [ ] Disk I/O (IOPS)
- [ ] Network I/O (MB/s)
- [ ] Database connections

**Application Metrics**:
- [ ] Garbage collection time
- [ ] Thread pool usage
- [ ] Cache hit rate
- [ ] Database query time
- [ ] External API latency

### Analysis Checklist

After each test:

1. **Response Times**:
   - [ ] Are all percentiles within SLO?
   - [ ] Any spikes or anomalies?
   - [ ] Trend over time?

2. **Error Analysis**:
   - [ ] What caused errors?
   - [ ] Error distribution by endpoint?
   - [ ] Correlation with load level?

3. **Resource Analysis**:
   - [ ] Which resource is the bottleneck?
   - [ ] Resource utilization trend?
   - [ ] Any resource exhaustion?

4. **Bottleneck Identification**:
   - [ ] Application code?
   - [ ] Database queries?
   - [ ] External dependencies?
   - [ ] Infrastructure limits?

5. **Recommendations**:
   - [ ] Optimization opportunities?
   - [ ] Scaling requirements?
   - [ ] Configuration tuning?
   - [ ] Code improvements?

---

## Test Execution Plan

### Pre-Test Checklist

- [ ] Test environment ready and validated
- [ ] Test data prepared
- [ ] Monitoring tools configured
- [ ] Load generation scripts validated
- [ ] Stakeholders notified
- [ ] Baseline metrics captured

### During Test

- [ ] Monitor system health continuously
- [ ] Watch for errors and anomalies
- [ ] Capture metrics in real-time
- [ ] Take notes on observations
- [ ] Save screenshots of dashboards

### Post-Test Checklist

- [ ] Analyze results
- [ ] Generate test report
- [ ] Identify bottlenecks
- [ ] Document findings
- [ ] Create optimization tickets
- [ ] Share results with team

---

## Test Report Template

### Executive Summary

**Test Type**: _________________
**Date**: _________________
**Duration**: _________________
**Environment**: _________________

**Results**: ✅ Pass / ❌ Fail

**Key Findings**:
- Finding 1
- Finding 2
- Finding 3

### Test Configuration

**Load Pattern**:
- Max concurrent users: _____
- Peak RPS: _____
- Test duration: _____

**SLOs**:
- Response time p95: < _____ ms (Actual: _____ ms)
- Error rate: < _____% (Actual: ____%)
- Throughput: > _____ RPS (Actual: _____ RPS)

### Results

**Response Time**:
| Metric | SLO | Actual | Status |
|--------|-----|--------|--------|
| p50 | < ___ ms | ___ ms | ✅/❌ |
| p95 | < ___ ms | ___ ms | ✅/❌ |
| p99 | < ___ ms | ___ ms | ✅/❌ |

**Throughput**:
- Peak RPS: _____
- Average RPS: _____
- Total requests: _____

**Errors**:
- Total errors: _____
- Error rate: _____%
- Error types: _____

**Resource Utilization**:
- Peak CPU: _____%
- Peak Memory: _____ GB
- Peak DB connections: _____

### Bottlenecks Identified

1. **Bottleneck**: _________________
   - **Impact**: _________________
   - **Recommendation**: _________________

2. **Bottleneck**: _________________
   - **Impact**: _________________
   - **Recommendation**: _________________

### Optimization Recommendations

**Priority 1 (Critical)**:
- Recommendation 1
- Recommendation 2

**Priority 2 (High)**:
- Recommendation 3
- Recommendation 4

**Priority 3 (Medium)**:
- Recommendation 5
- Recommendation 6

### Next Steps

- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3
- [ ] Schedule follow-up test

---

## Continuous Performance Testing

### CI/CD Integration

```yaml
# .github/workflows/performance.yml
name: Performance Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly
  workflow_dispatch:     # Manual trigger

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run K6 performance test
        run: |
          docker run --rm -v $(pwd):/scripts grafana/k6 run \
            --out json=results.json \
            /scripts/load-test.js

      - name: Analyze results
        run: |
          python scripts/analyze-perf.py results.json

      - name: Compare to baseline
        run: |
          python scripts/compare-baseline.py \
            results.json baseline.json

      - name: Fail if regression
        run: |
          if [ $? -ne 0 ]; then
            echo "Performance regression detected!"
            exit 1
          fi
```

### Performance Regression Detection

```python
# compare-baseline.py
import json
import sys

def compare_results(current_file, baseline_file):
    with open(current_file) as f:
        current = json.load(f)
    with open(baseline_file) as f:
        baseline = json.load(f)

    regression = False

    # Compare p95 response time
    current_p95 = current['metrics']['http_req_duration']['p95']
    baseline_p95 = baseline['metrics']['http_req_duration']['p95']

    if current_p95 > baseline_p95 * 1.2:  # 20% regression threshold
        print(f"⚠️ p95 regression: {current_p95}ms vs {baseline_p95}ms")
        regression = True

    # Compare error rate
    current_errors = current['metrics']['errors']['rate']
    baseline_errors = baseline['metrics']['errors']['rate']

    if current_errors > baseline_errors * 2:
        print(f"⚠️ Error rate regression: {current_errors} vs {baseline_errors}")
        regression = True

    return 1 if regression else 0

if __name__ == '__main__':
    sys.exit(compare_results(sys.argv[1], sys.argv[2]))
```

---

## Resources

**Tools**:
- K6: https://k6.io/docs/
- JMeter: https://jmeter.apache.org/
- Locust: https://locust.io/
- Gatling: https://gatling.io/

**References**:
- Google SRE Book - Performance chapters
- High Performance Browser Networking
- Web Performance in Action
- Systems Performance (Brendan Gregg)

**Monitoring**:
- Grafana: https://grafana.com/
- DataDog: https://www.datadoghq.com/
- New Relic: https://newrelic.com/

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
