# Performance Testing Guide
## Comprehensive Performance & Load Testing Strategy

---

## 🎯 Overview

Performance testing ensures your application can handle expected (and unexpected) load while maintaining acceptable response times. Based on practices from Netflix, Amazon, Google, and high-scale systems.

**Goal**: Deliver fast, reliable, scalable applications that meet performance SLAs.

---

## 📊 Performance Testing Types

### 1. Load Testing

**What**: Test system behavior under expected load

**When**: Before each major release

**Goal**: Verify system meets performance SLAs under normal conditions

**Example Scenario**:
```yaml
Test: E-commerce Site Black Friday
Users: 10,000 concurrent
Duration: 2 hours
Ramp-up: 10 minutes
Acceptance Criteria:
  - p95 response time < 500ms
  - p99 response time < 1s
  - Error rate < 0.1%
  - Throughput > 5000 req/s
```

### 2. Stress Testing

**What**: Test system behavior beyond normal load to find breaking point

**When**: Quarterly, before scaling events

**Goal**: Identify maximum capacity and failure modes

**Example Scenario**:
```yaml
Test: Find Breaking Point
Users: Start at 1,000, increase by 1,000 every 5 min
Stop When: Error rate > 5% or response time > 10s
Goal: Identify bottlenecks and maximum capacity
```

### 3. Spike Testing

**What**: Test sudden increases in load

**When**: Before marketing campaigns, product launches

**Goal**: Verify autoscaling and resilience

**Example Scenario**:
```yaml
Test: Product Launch
Baseline: 100 users
Spike: 10,000 users in 1 minute
Duration: 10 minutes at peak
Return: Back to 100 users in 1 minute
Check: System recovers gracefully
```

### 4. Soak Testing (Endurance)

**What**: Test system stability over extended period

**When**: Before major releases

**Goal**: Find memory leaks, resource exhaustion

**Example Scenario**:
```yaml
Test: 24-Hour Soak
Users: 1,000 constant
Duration: 24 hours
Monitor:
  - Memory usage (should be stable)
  - Database connections (no leaks)
  - CPU usage (should not degrade)
  - Response time (should not increase)
```

### 5. Scalability Testing

**What**: Test how system scales with increased resources

**When**: Architecture changes, before scaling

**Goal**: Verify linear scalability

**Example Scenario**:
```yaml
Test: Horizontal Scaling
Baseline: 2 servers, 1,000 users
Test 1: 4 servers, 2,000 users (expect 2x throughput)
Test 2: 8 servers, 4,000 users (expect 4x throughput)
Verify: Linear scaling (doubling servers doubles capacity)
```

---

## 🛠️ Performance Testing Tools

### Recommended Tools

**k6 (Recommended)**
```javascript
// Load test with k6
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 },  // Ramp up
    { duration: '10m', target: 100 }, // Stay at 100
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% < 500ms
    http_req_failed: ['rate<0.01'],     // < 1% errors
  },
};

export default function () {
  const response = http.get('https://api.example.com/products');

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1); // Think time
}
```

**Artillery**
```yaml
# artillery-config.yml
config:
  target: 'https://api.example.com'
  phases:
    - duration: 300
      arrivalRate: 20
      name: "Warm up"
    - duration: 600
      arrivalRate: 50
      name: "Sustained load"

scenarios:
  - name: "Browse products"
    flow:
      - get:
          url: "/products"
      - think: 2
      - get:
          url: "/products/{{ $randomNumber(1, 100) }}"
```

**JMeter** (Traditional, GUI-based)
```xml
<!-- Good for complex scenarios, recording -->
<!-- Enterprise standard, extensive plugins -->
```

**Gatling** (Scala-based)
```scala
// High performance, developer-friendly
scenario("E-commerce")
  .exec(http("Homepage").get("/"))
  .pause(2)
  .exec(http("Products").get("/products"))
```

---

## 📈 Key Performance Metrics

### Response Time Metrics

```yaml
p50 (Median):
  Meaning: 50% of requests faster than this
  Target: < 200ms
  Use: Typical user experience

p95 (95th Percentile):
  Meaning: 95% of requests faster than this
  Target: < 500ms
  Use: SLA metric (catches most outliers)

p99 (99th Percentile):
  Meaning: 99% of requests faster than this
  Target: < 1s
  Use: Tail latency (worst case for most users)

p99.9 (99.9th Percentile):
  Meaning: 99.9% of requests faster than this
  Target: < 2s
  Use: Rare but possible worst case

Max:
  Meaning: Slowest request
  Use: Debugging (often outlier/anomaly)
```

**Why Percentiles > Averages**:
```markdown
Scenario: 100 requests
- 95 requests: 100ms
- 4 requests: 500ms
- 1 request: 10,000ms (10s)

Average: 190ms (looks great!) ❌
p95: 500ms (more realistic)
p99: 10s (shows the problem!) ✅

Average hides outliers. Use percentiles!
```

### Throughput Metrics

```yaml
Requests per Second (RPS):
  Measure: Total successful requests / time
  Target: Varies by endpoint
  Use: Capacity planning

Transactions per Second (TPS):
  Measure: Completed business transactions / time
  Target: Varies by business
  Use: Business metrics

Bandwidth:
  Measure: MB/s transferred
  Target: < Network capacity
  Use: Network planning
```

### Error Metrics

```yaml
Error Rate:
  Formula: (Failed Requests / Total Requests) * 100
  Target: < 0.1%
  Critical: > 1%

Error Types:
  4xx: Client errors (rate limit, auth, validation)
  5xx: Server errors (bugs, timeouts, crashes)

Timeout Rate:
  Formula: (Timeouts / Total Requests) * 100
  Target: < 0.05%
```

### Resource Metrics

```yaml
CPU Usage:
  Target: < 70% average, < 90% peak
  Warning: > 80% sustained
  Critical: > 95%

Memory Usage:
  Target: < 70% average
  Warning: > 85%
  Critical: > 95%

Database Connections:
  Target: < 70% of pool size
  Warning: Pool exhaustion
  Monitor: Connection leaks

Network I/O:
  Monitor: Throughput, packet loss
  Warning: > 70% capacity
```

---

## 🎯 Creating Performance Tests

### Step 1: Define SLAs (Service Level Agreements)

```yaml
# performance-slas.yml

Endpoints:
  GET /api/products:
    p95: 200ms
    p99: 500ms
    throughput: 1000 req/s
    error_rate: < 0.1%

  POST /api/orders:
    p95: 500ms
    p99: 1s
    throughput: 100 req/s
    error_rate: < 0.01%

  GET /api/search:
    p95: 300ms
    p99: 800ms
    throughput: 500 req/s
    error_rate: < 0.5%

System-wide:
  Availability: 99.9%
  Concurrent Users: 10,000
  Peak Load: 5,000 req/s
```

### Step 2: Create Test Scenarios

**Realistic User Behavior**:
```javascript
// k6 scenario - E-commerce user journey
import { check, sleep } from 'k6';
import http from 'k6/http';

export default function () {
  // 1. Homepage
  let res = http.get('https://example.com/');
  check(res, { 'homepage loaded': (r) => r.status === 200 });
  sleep(randomIntBetween(2, 5)); // User reads page

  // 2. Browse products
  res = http.get('https://example.com/api/products');
  check(res, { 'products loaded': (r) => r.status === 200 });
  sleep(randomIntBetween(3, 7));

  // 3. View product detail
  const productId = randomIntBetween(1, 100);
  res = http.get(`https://example.com/api/products/${productId}`);
  check(res, { 'product detail loaded': (r) => r.status === 200 });
  sleep(randomIntBetween(5, 10));

  // 4. Add to cart (30% of users)
  if (Math.random() < 0.3) {
    res = http.post('https://example.com/api/cart', JSON.stringify({
      productId,
      quantity: 1,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    check(res, { 'added to cart': (r) => r.status === 200 });
    sleep(randomIntBetween(2, 4));

    // 5. Checkout (50% of cart additions = 15% of all users)
    if (Math.random() < 0.5) {
      res = http.post('https://example.com/api/checkout', JSON.stringify({
        paymentMethod: 'credit_card',
      }), {
        headers: { 'Content-Type': 'application/json' },
      });
      check(res, { 'checkout completed': (r) => r.status === 200 });
    }
  }
}

function randomIntBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}
```

### Step 3: Run Tests

```bash
# Load test with k6
k6 run \
  --vus 100 \           # 100 virtual users
  --duration 10m \      # Run for 10 minutes
  --out json=results.json \
  load-test.js

# Stress test (find breaking point)
k6 run \
  --stages '5m:100,5m:500,5m:1000,5m:2000' \
  --out json=stress-results.json \
  load-test.js

# Spike test
k6 run \
  --stages '1m:100,1m:5000,5m:5000,1m:100' \
  --out json=spike-results.json \
  load-test.js

# Soak test (24 hours)
k6 run \
  --vus 100 \
  --duration 24h \
  --out json=soak-results.json \
  load-test.js
```

### Step 4: Analyze Results

```bash
# Generate HTML report (k6)
k6 run --out json=results.json load-test.js
cat results.json | jq -r '[.metric.name, .value] | @csv'

# Key metrics to check:
# 1. Response time percentiles
jq '.metrics.http_req_duration' results.json

# 2. Error rate
jq '.metrics.http_req_failed.values.rate' results.json

# 3. Throughput
jq '.metrics.http_reqs.values.rate' results.json
```

---

## 🔍 Performance Profiling

### Application Profiling

**Node.js**:
```bash
# CPU profiling
node --prof app.js
# Generate report
node --prof-process isolate-*-v8.log > processed.txt

# Heap snapshots
node --inspect app.js
# Open Chrome DevTools → Memory → Take snapshot
```

**Python**:
```python
import cProfile
import pstats

# Profile function
cProfile.run('main()', 'profile_stats')

# Analyze
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Go**:
```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()

// Access profiling at http://localhost:6060/debug/pprof/
```

### Database Profiling

**PostgreSQL**:
```sql
-- Enable slow query log
ALTER DATABASE mydb SET log_min_duration_statement = 1000; -- Log queries > 1s

-- Analyze query
EXPLAIN ANALYZE
SELECT * FROM users
WHERE email = 'user@example.com';

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**MongoDB**:
```javascript
// Enable profiling
db.setProfilingLevel(1, { slowms: 100 }); // Log queries > 100ms

// View slow queries
db.system.profile.find().sort({ ts: -1 }).limit(5).pretty();

// Explain query
db.users.find({ email: 'user@example.com' }).explain('executionStats');
```

### Frontend Performance

**Core Web Vitals**:
```javascript
// Measure with Web Vitals library
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(console.log); // Cumulative Layout Shift
getFID(console.log); // First Input Delay
getLCP(console.log); // Largest Contentful Paint

// Targets:
// LCP < 2.5s
// FID < 100ms
// CLS < 0.1
```

**Chrome DevTools**:
```markdown
1. Lighthouse:
   - Run audit
   - Check Performance score (target: > 90)

2. Performance Tab:
   - Record loading
   - Identify bottlenecks
   - Check JavaScript execution time

3. Network Tab:
   - Check request waterfall
   - Identify slow requests
   - Check resource sizes
```

---

## 🎯 Performance Optimization Checklist

### Backend Optimization

```markdown
Database:
- [ ] Add indexes on frequently queried columns
- [ ] Eliminate N+1 queries
- [ ] Use connection pooling
- [ ] Enable query caching
- [ ] Optimize slow queries (EXPLAIN ANALYZE)
- [ ] Use read replicas for read-heavy workloads

Caching:
- [ ] Implement Redis/Memcached
- [ ] Cache database queries
- [ ] Cache API responses
- [ ] Use CDN for static assets
- [ ] Set appropriate cache headers

API:
- [ ] Use pagination for large result sets
- [ ] Implement field filtering (GraphQL-style)
- [ ] Compress responses (gzip/brotli)
- [ ] Use HTTP/2
- [ ] Implement rate limiting

Code:
- [ ] Profile and optimize hot paths
- [ ] Use async/parallel processing
- [ ] Optimize algorithms (O(n) vs O(n²))
- [ ] Lazy load heavy operations
- [ ] Use background jobs for long tasks
```

### Frontend Optimization

```markdown
Loading:
- [ ] Code splitting (dynamic imports)
- [ ] Lazy load images (Intersection Observer)
- [ ] Preload critical resources
- [ ] Use WebP images
- [ ] Minimize JavaScript bundle size

Rendering:
- [ ] Virtual scrolling for long lists
- [ ] Debounce/throttle expensive operations
- [ ] Use React.memo / useMemo
- [ ] Avoid unnecessary re-renders
- [ ] Optimize CSS (critical CSS inline)

Assets:
- [ ] Compress images (TinyPNG, ImageOptim)
- [ ] Use SVG for icons
- [ ] Serve responsive images (srcset)
- [ ] Minify CSS/JS
- [ ] Use CDN for static assets
```

---

## 📊 Performance Testing in CI/CD

```yaml
# .github/workflows/performance-test.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 0 * * 0' # Weekly on Sunday
  workflow_dispatch: # Manual trigger

jobs:
  performance-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load test
        run: |
          k6 run \
            --vus 50 \
            --duration 5m \
            --out json=results.json \
            tests/load-test.js

      - name: Check thresholds
        run: |
          # Parse results and fail if thresholds not met
          python scripts/check-performance-thresholds.py results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: results.json

      - name: Comment on PR (if applicable)
        if: github.event_name == 'pull_request'
        run: |
          # Post performance metrics as PR comment
          python scripts/comment-performance.py
```

---

## 🎓 Best Practices

### Do's ✅

1. **Test early and often**
2. **Use realistic scenarios** (user behavior)
3. **Monitor during tests** (CPU, memory, DB)
4. **Test from multiple regions**
5. **Baseline before changes** (compare performance)
6. **Use percentiles, not averages**
7. **Automate performance tests**
8. **Profile before optimizing**
9. **Set clear SLAs**
10. **Test gradual load increase**

### Don'ts ❌

1. **Don't test in production** (use staging)
2. **Don't ignore tail latency** (p99, p99.9)
3. **Don't optimize prematurely**
4. **Don't test with synthetic data** (use realistic data)
5. **Don't ignore database** (often the bottleneck)
6. **Don't skip soak tests** (find memory leaks)
7. **Don't assume linear scaling**
8. **Don't test without monitoring**
9. **Don't ignore network latency**
10. **Don't forget cleanup** (stop load generators)

---

## 🔗 Related Resources

- [Load Testing Guide](load-testing-guide.md)
- [Profiling Guide](profiling-guide.md)
- [Optimization Checklist](optimization-checklist.md)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Based On**: Google SRE, Netflix Performance Engineering
