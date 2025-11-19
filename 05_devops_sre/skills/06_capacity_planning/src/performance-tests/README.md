# Performance Test Scenarios

This directory contains comprehensive performance test scenarios for different application types.

## Available Scenarios

### 1. E-Commerce Scenario (ecommerce-scenario.js)
Simulates realistic e-commerce user journeys including:
- Homepage browsing
- Category and product search
- Product detail viewing
- Add to cart
- Checkout process

**Metrics Tracked:**
- Cart abandonment rate
- Checkout error rate
- Product views
- Response times per stage

**Run:**
```bash
k6 run ecommerce-scenario.js
# With custom URL
k6 run --env BASE_URL=https://shop.example.com ecommerce-scenario.js
```

**Load Profile:**
- Ramp: 0 → 100 → 500 → 1000 users
- Duration: 35 minutes
- Simulates flash sale spike

### 2. Microservices Scenario (microservices-scenario.js)
Tests multiple microservices with different load profiles:
- User service (200 RPS) - High read load
- Order service (50 RPS) - Medium load
- Inventory service (150 RPS) - High read load
- Payment service (20 RPS) - Critical, low load

**Metrics Tracked:**
- Per-service request counts
- Per-service latency (avg, p95)
- Service-specific thresholds

**Run:**
```bash
k6 run microservices-scenario.js
```

**Load Profile:**
- Constant arrival rate per service
- Duration: 10 minutes
- Independent service scaling

### 3. Video Streaming Scenario (video-streaming-scenario.js)
Netflix-inspired video streaming test:
- Catalog browsing
- Video manifest loading
- Adaptive streaming chunks
- Quality adaptation
- Watch time simulation

**Metrics Tracked:**
- Stream start time (p90, p99)
- Rebuffer rate
- Video quality (Mbps)
- Chunk download time

**Run:**
```bash
k6 run video-streaming-scenario.js
# With custom CDN and API URLs
k6 run --env CDN_URL=https://cdn.example.com \
       --env API_URL=https://api.example.com \
       video-streaming-scenario.js
```

**Load Profile:**
- Ramp: 0 → 1K → 5K → 10K concurrent streams
- Duration: 44 minutes
- Simulates prime-time viewing

## Running Tests

### Basic Execution
```bash
k6 run <scenario>.js
```

### With Results Output
```bash
k6 run --out json=results.json <scenario>.js
```

### With InfluxDB + Grafana
```bash
k6 run --out influxdb=http://localhost:8086/k6 <scenario>.js
```

### With Custom Environment
```bash
k6 run --env BASE_URL=https://api.example.com \
       --env CDN_URL=https://cdn.example.com \
       <scenario>.js
```

### Docker Execution
```bash
docker run -i grafana/k6:latest run - <<scenario>.js
```

## Analyzing Results

Each test generates a JSON summary with scenario-specific metrics:

### E-Commerce Results
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "checkout_error_rate": 0.008,
    "cart_abandonment_rate": 0.68,
    "product_views": 15420,
    "response_time": {
      "p95": 487,
      "p99": 923
    }
  }
}
```

### Microservices Results
```json
{
  "services": {
    "user": {
      "calls": 120000,
      "avg_latency": 95,
      "p95_latency": 178
    },
    "payment": {
      "calls": 12000,
      "avg_latency": 450,
      "p95_latency": 892
    }
  }
}
```

### Video Streaming Results
```json
{
  "streaming_metrics": {
    "stream_start_time": {
      "p90": 876,
      "p99": 1543
    },
    "rebuffer_rate": 0.004,
    "avg_quality_mbps": 12.3
  }
}
```

## Customization

### Modify Load Profile
Edit the `options.stages` or `options.scenarios` in each test:

```javascript
export let options = {
  stages: [
    { duration: '5m', target: 200 },   // Adjust target users
    { duration: '10m', target: 500 },  // Adjust duration
    { duration: '5m', target: 0 },
  ],
};
```

### Add Custom Metrics
```javascript
import { Trend, Rate, Counter } from 'k6/metrics';

let customMetric = new Trend('my_custom_metric');
// Later in test
customMetric.add(value);
```

### Adjust Thresholds
```javascript
thresholds: {
  'http_req_duration': ['p(95)<500'],  // Adjust SLA
  'http_req_failed': ['rate<0.01'],    // Adjust error rate
},
```

## Best Practices

1. **Test Environment**: Use production-like environment
2. **Data Volume**: Use realistic data sizes
3. **Think Time**: Include realistic user delays
4. **Ramp Up**: Gradual load increase
5. **Monitoring**: Monitor system resources during test
6. **Baseline**: Establish baseline before changes
7. **Repeatability**: Run tests multiple times

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Performance Test
  run: |
    k6 run --out json=results.json ecommerce-scenario.js
    # Check thresholds
    if [ $? -ne 0 ]; then
      echo "Performance test failed"
      exit 1
    fi
```

### Automated Reporting
```bash
# Run test and generate report
k6 run --out json=results.json ecommerce-scenario.js
python3 analyze_results.py results.json
```

## Troubleshooting

### High Error Rates
- Check application logs
- Verify network connectivity
- Review resource utilization
- Check rate limits

### Inconsistent Results
- Ensure stable test environment
- Check for background processes
- Verify network stability
- Run multiple iterations

### Low Throughput
- Check VU count (may need more)
- Verify think time/sleep values
- Review application bottlenecks
- Check k6 resource limits

## References

- [k6 Documentation](https://k6.io/docs/)
- [k6 Examples](https://k6.io/docs/examples/)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/load-testing-best-practices/)
