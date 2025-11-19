# Capacity Planning Skill

Comprehensive reference materials and practical examples for capacity planning, load testing, and autoscaling in cloud-native environments.

## Directory Structure

```
06_capacity_planning/
├── reference/                          # Reference documentation
│   ├── load_testing_reference.md      # k6, JMeter, Gatling, Locust comparison
│   ├── autoscaling_reference.md       # HPA, VPA, Cluster Autoscaler, Karpenter
│   └── performance_metrics.md         # Key performance indicators and SLOs
│
├── guides/                            # Step-by-step guides
│   ├── load_testing_with_k6.md       # Complete k6 load testing guide
│   ├── implementing_autoscaling.md   # Kubernetes autoscaling setup
│   └── capacity_planning_process.md  # Forecasting and planning workflows
│
└── src/                              # Code examples and configurations
    ├── k6/                           # k6 load test scripts
    │   ├── smoke-test.js
    │   ├── load-test.js
    │   ├── stress-test.js
    │   ├── spike-test.js
    │   └── README.md
    │
    ├── jmeter/                       # JMeter test plans
    │   ├── basic-load-test.jmx
    │   └── README.md
    │
    ├── autoscaling/                  # Kubernetes autoscaling examples
    │   ├── hpa-cpu-basic.yaml
    │   ├── hpa-multi-metric.yaml
    │   ├── vpa-recommendations.yaml
    │   ├── vpa-auto.yaml
    │   ├── complete-autoscaling-example.yaml
    │   └── README.md
    │
    └── performance-tests/            # Advanced test scenarios
        ├── ecommerce-scenario.js
        ├── microservices-scenario.js
        ├── video-streaming-scenario.js
        └── README.md
```

## Quick Start

### 1. Load Testing

**Run a basic k6 test:**
```bash
cd src/k6/
k6 run smoke-test.js
```

**Run with custom endpoint:**
```bash
k6 run --env BASE_URL=https://api.example.com load-test.js
```

### 2. Autoscaling

**Deploy basic HPA:**
```bash
cd src/autoscaling/
kubectl apply -f hpa-cpu-basic.yaml
```

**Monitor HPA:**
```bash
kubectl get hpa --watch
```

### 3. Performance Testing

**Run e-commerce scenario:**
```bash
cd src/performance-tests/
k6 run ecommerce-scenario.js
```

## Reference Materials

### Load Testing Tools
- **[load_testing_reference.md](reference/load_testing_reference.md)** - Comprehensive comparison of k6, JMeter, Gatling, and Locust
  - Feature comparison matrix
  - Use case recommendations
  - Industry best practices from Netflix and Amazon

### Autoscaling Mechanisms
- **[autoscaling_reference.md](reference/autoscaling_reference.md)** - Complete guide to Kubernetes autoscaling
  - HPA (Horizontal Pod Autoscaler)
  - VPA (Vertical Pod Autoscaler)
  - Cluster Autoscaler
  - Karpenter (next-generation)
  - Combined strategies

### Performance Metrics
- **[performance_metrics.md](reference/performance_metrics.md)** - Key performance indicators
  - Application metrics (response time, throughput, error rate)
  - Infrastructure metrics (CPU, memory, network, disk)
  - Business metrics (conversion rate, revenue per request)
  - Netflix and Amazon-specific metrics

## Guides

### Load Testing with k6
- **[load_testing_with_k6.md](guides/load_testing_with_k6.md)** - Complete k6 tutorial
  - Installation and setup
  - Test scenarios (smoke, load, stress, spike, soak)
  - Advanced features (custom metrics, scenarios)
  - CI/CD integration
  - Real-world examples

### Implementing Autoscaling
- **[implementing_autoscaling.md](guides/implementing_autoscaling.md)** - Step-by-step autoscaling setup
  - Prerequisites (Metrics Server, Prometheus)
  - HPA implementation with examples
  - VPA setup and configuration
  - Cluster Autoscaler on AWS/GKE
  - Karpenter advanced configuration
  - Monitoring and troubleshooting

### Capacity Planning Process
- **[capacity_planning_process.md](guides/capacity_planning_process.md)** - Complete planning workflow
  - Framework and methodology
  - Data collection and analysis
  - Forecasting methods (linear, time series, ML)
  - Load testing validation
  - Cost optimization strategies
  - Netflix and Amazon practices
  - Event-driven planning

## Code Examples

### k6 Load Tests
- **smoke-test.js** - Minimal load test (1 VU, 1 minute)
- **load-test.js** - Standard load test with gradual ramp-up
- **stress-test.js** - Find breaking point
- **spike-test.js** - Test sudden traffic spikes

### JMeter Test Plans
- **basic-load-test.jmx** - Basic API load test (100 users, 10 minutes)

### Autoscaling Configurations
- **hpa-cpu-basic.yaml** - Simple CPU-based HPA
- **hpa-multi-metric.yaml** - Advanced multi-metric HPA
- **vpa-recommendations.yaml** - VPA in recommendations mode
- **vpa-auto.yaml** - VPA with automatic application
- **complete-autoscaling-example.yaml** - Full stack with Deployment, HPA, VPA, PDB

### Performance Test Scenarios
- **ecommerce-scenario.js** - Complete e-commerce user journey
  - Homepage → Search → Product → Cart → Checkout
  - Tracks cart abandonment, checkout errors

- **microservices-scenario.js** - Multiple services with different loads
  - User, Order, Inventory, Payment services
  - Independent load profiles per service

- **video-streaming-scenario.js** - Netflix-inspired streaming test
  - Catalog browsing → Video playback → Chunk streaming
  - Tracks stream start time, rebuffer rate, quality

## Industry Best Practices

### Netflix Approach
- **Regional Failover**: 3x capacity for multi-region resilience
- **Chaos Engineering**: Combine with load testing
- **Continuous Testing**: Production load testing
- **Advanced Metrics**: Stream quality, rebuffer rates

### Amazon Approach
- **GameDays**: Scheduled capacity testing events
- **Incremental Load**: Gradual capacity validation
- **Cell-Based Architecture**: Isolated failure domains
- **Predictive Scaling**: Pre-scale for known events

## Key Concepts

### Safety Factors
- **Netflix**: 3x (regional failover + spikes)
- **Amazon**: 2x (peak event preparation)
- **Standard**: 1.5x (cost-performance balance)

### SLO Examples
```yaml
Availability: 99.99% uptime
Response Time:
  p95: < 500ms
  p99: < 1000ms
Throughput: 100,000+ RPS capacity
Error Rate: < 0.1%
```

### Autoscaling Best Practices
1. Always set resource requests
2. Use PodDisruptionBudgets
3. Avoid VPA + HPA on same metric
4. Monitor scaling behavior
5. Test thoroughly with load tests

### Load Testing Types
- **Smoke Test**: Minimal load, verify functionality
- **Load Test**: Expected peak load
- **Stress Test**: Find breaking point
- **Spike Test**: Sudden traffic increases
- **Soak Test**: Long-term stability (24+ hours)

## Getting Help

### Troubleshooting Resources
- Check README files in each directory
- Review reference documentation
- Examine example configurations
- Test with smoke tests first
- Monitor metrics during tests

### Common Issues
- **HPA not scaling**: Check Metrics Server, resource requests
- **VPA conflicts**: Use recommendations mode with HPA
- **High error rates**: Review application logs, increase capacity
- **Slow autoscaling**: Adjust HPA behavior policies

## Tools Required

### Load Testing
- k6 (recommended)
- JMeter (enterprise standard)
- Docker (for containerized testing)

### Kubernetes
- kubectl
- Metrics Server
- Prometheus (for custom metrics)
- VPA components

### Monitoring
- Prometheus
- Grafana
- InfluxDB (optional)

## Next Steps

1. **Learn**: Read reference materials
2. **Practice**: Run example tests
3. **Implement**: Deploy autoscaling
4. **Validate**: Run load tests
5. **Optimize**: Adjust based on results
6. **Automate**: Integrate with CI/CD

## Contributing

When adding new examples or documentation:
1. Follow existing structure
2. Include README files
3. Add comprehensive comments
4. Provide usage examples
5. Document prerequisites
6. Include troubleshooting tips

## References

- [k6 Documentation](https://k6.io/docs/)
- [Kubernetes Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Karpenter](https://karpenter.sh/)
- [Netflix Tech Blog](https://netflixtechblog.com/)
- [AWS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Google SRE Book](https://sre.google/sre-book/)
