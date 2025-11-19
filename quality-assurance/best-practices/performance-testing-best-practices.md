# Performance Testing Best Practices

## Load Test Design

### DO ✅
- Define clear performance SLOs
- Model realistic user behavior
- Include think time (2-5 seconds)
- Ramp up gradually
- Test at expected and peak load

### DON'T ❌
- Test only happy path
- Spike from 0 to max instantly
- Use constant load (unrealistic)
- Ignore resource utilization
- Test in dev environment

## Metrics Collection

### DO ✅
- Track response time percentiles (p50, p95, p99)
- Monitor error rates
- Measure throughput (RPS, TPS)
- Track resource usage (CPU, memory)
- Establish baseline first

### DON'T ❌
- Only look at average response time
- Ignore errors during testing
- Test without monitoring
- Compare different environments
- Skip baseline measurement

## Test Execution

### DO ✅
- Run from production-like environment
- Use production-like data volume
- Test all critical endpoints
- Run during off-peak hours
- Automate test execution

### DON'T ❌
- Run from laptop/local network
- Use tiny datasets
- Test only one endpoint
- Disrupt production users
- Only run tests manually
