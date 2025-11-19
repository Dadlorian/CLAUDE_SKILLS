# Deployment Strategies Reference

## Overview
This reference covers the most common deployment strategies used in modern release engineering, including their advantages, disadvantages, and use cases.

---

## 1. Blue-Green Deployment

### Description
Blue-green deployment maintains two identical production environments (Blue and Green). Only one environment serves live production traffic at any time. The inactive environment is used for the new release.

### Process
1. Deploy new version to inactive environment (Green)
2. Test thoroughly in Green environment
3. Switch traffic from Blue to Green
4. Keep Blue environment as instant rollback option
5. Once stable, Blue becomes the next staging environment

### Advantages
- **Zero Downtime**: Instant cutover between environments
- **Easy Rollback**: Simple DNS/load balancer switch back
- **Full Testing**: Complete production-like environment for validation
- **Safe**: No risk to current production during deployment

### Disadvantages
- **Resource Intensive**: Requires 2x infrastructure
- **Database Challenges**: Schema changes need backward compatibility
- **Stateful Applications**: Session management complexity
- **Cost**: Double infrastructure costs during deployment

### Use Cases
- Mission-critical applications requiring zero downtime
- Applications with complex state that need full validation
- When quick rollback is essential
- Services with sufficient infrastructure budget

### Implementation Considerations
- Load balancer configuration for traffic switching
- Database migration strategies
- Shared resources (databases, caches) compatibility
- Session handling during cutover

### Example Traffic Switch Methods
```yaml
# DNS-based switch
# Update DNS A/AAAA records
blue.production.example.com  -> 10.0.1.0 (old)
green.production.example.com -> 10.0.2.0 (new)

# Load Balancer switch
# Update target groups
production-lb -> blue-target-group (old)
production-lb -> green-target-group (new)
```

### Netflix Practice
Netflix uses a variant called "Red-Black" deployment:
- Automated via Spinnaker
- Leverages AWS Auto Scaling Groups
- Red (old) and Black (new) ASGs
- Gradual traffic shift with monitoring
- Automated rollback on metric anomalies

---

## 2. Canary Deployment

### Description
Canary deployment releases the new version to a small subset of users before rolling out to the entire infrastructure. Named after "canary in a coal mine" - early detection of problems.

### Process
1. Deploy new version to small percentage of servers (e.g., 5%)
2. Monitor metrics, errors, and user feedback
3. Gradually increase percentage (10% → 25% → 50% → 100%)
4. Rollback if issues detected
5. Complete rollout when confident

### Advantages
- **Risk Mitigation**: Limited user exposure to potential issues
- **Real Production Testing**: Real users, real data
- **Gradual Rollout**: Controlled increase in exposure
- **Early Detection**: Problems found before full deployment

### Disadvantages
- **Complexity**: Requires sophisticated traffic routing
- **Longer Deployment**: Takes more time than all-at-once
- **Monitoring Required**: Need robust observability
- **Version Compatibility**: Multiple versions running simultaneously

### Use Cases
- High-traffic consumer applications
- When user impact must be minimized
- Services with unpredictable load patterns
- Applications with complex dependencies

### Canary Stages (Netflix Model)
```
1% → 5% → 10% → 25% → 50% → 100%
└─────┘   └──────┘    └───────┘
  Early    Growth     Complete
 Detection Validation  Rollout
```

### Key Metrics to Monitor
- Error rates (2xx, 4xx, 5xx response codes)
- Latency (p50, p95, p99)
- CPU and memory utilization
- Custom business metrics
- User engagement metrics

### Facebook Practice
Facebook's "Gatekeeper" system:
- Internal feature flagging system
- Phased rollout to employee → 1% → 10% → 50% → 100%
- Per-user and per-request controls
- Real-time metric dashboards
- Automated rollback on threshold breaches

---

## 3. Rolling Deployment

### Description
Rolling deployment incrementally updates servers/containers one at a time or in small batches, maintaining service availability throughout the deployment.

### Process
1. Take subset of servers out of load balancer
2. Deploy new version to those servers
3. Health check and validation
4. Return servers to load balancer
5. Repeat until all servers updated

### Advantages
- **Resource Efficient**: No additional infrastructure needed
- **Simple**: Straightforward implementation
- **Gradual**: Controlled pace of rollout
- **Available**: Service remains available throughout

### Disadvantages
- **Slow**: Can take significant time for large fleets
- **Mixed Versions**: Multiple versions running simultaneously
- **Rollback Complexity**: Must roll back incrementally
- **Stateful Challenges**: Session affinity issues

### Use Cases
- Resource-constrained environments
- Stateless applications
- When infrastructure doubling isn't feasible
- Services with moderate traffic

### Rolling Update Configuration (Kubernetes)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # Max pods above desired count
    maxUnavailable: 25%  # Max pods unavailable during update
```

### Batch Sizing Strategies
- **Conservative**: 10% batches, longer deployment
- **Aggressive**: 33% batches, faster deployment
- **Adaptive**: Adjust batch size based on success

---

## 4. Recreate Deployment

### Description
Recreate deployment terminates all running instances of the old version before starting the new version. Also called "Big Bang" deployment.

### Process
1. Stop all old version instances
2. Deploy new version
3. Start new version instances
4. Service becomes available

### Advantages
- **Simple**: Easiest to implement
- **Clean State**: No mixed versions
- **Resource Efficient**: No additional resources needed
- **Clear Cutover**: Distinct old→new transition

### Disadvantages
- **Downtime**: Service unavailable during deployment
- **High Risk**: All-or-nothing deployment
- **No Gradual Testing**: Full user exposure immediately
- **Difficult Rollback**: Requires full redeployment

### Use Cases
- Development/staging environments
- Maintenance windows acceptable
- Stateful applications requiring clean restart
- Small user bases tolerant of downtime

### Downtime Calculation
```
Downtime = Shutdown Time + Deployment Time + Startup Time + Health Check Time

Example:
- Shutdown: 30s
- Deployment: 2m
- Startup: 1m
- Health checks: 30s
Total: ~4 minutes
```

---

## 5. Shadow/Dark Launch

### Description
Shadow deployment runs the new version alongside the old version, duplicating production traffic to the new version without serving responses to users. Used for testing at production scale.

### Process
1. Deploy new version in shadow mode
2. Duplicate production traffic to new version
3. Compare responses/metrics with old version
4. Discard shadow responses (don't serve to users)
5. When confident, switch to new version

### Advantages
- **Production Scale Testing**: Real load, real data
- **Zero User Risk**: Users never see shadow version
- **Performance Validation**: Real-world performance metrics
- **Comparison**: Direct A/B comparison possible

### Disadvantages
- **Infrastructure Cost**: Running both versions at scale
- **Complexity**: Traffic duplication infrastructure
- **Side Effects**: Must prevent shadow version side effects
- **Limited Validation**: Can't test user experience

### Use Cases
- Critical systems requiring production validation
- Performance-sensitive applications
- When A/B testing isn't sufficient
- Services with complex load patterns

### Netflix Practice
- Used for critical path services
- Shadow traffic mirrored via Zuul (API Gateway)
- Metrics compared in real-time
- Decision to promote based on performance data

---

## 6. A/B Testing Deployment

### Description
A/B testing deployment serves different versions to different user segments to compare business metrics and user behavior.

### Process
1. Deploy version A and version B
2. Route users to versions based on criteria
3. Collect metrics for each version
4. Analyze results statistically
5. Choose winning version

### Advantages
- **Data-Driven**: Decisions based on real user data
- **Business Metrics**: Optimize for conversions, engagement
- **User Segmentation**: Target specific user groups
- **Scientific**: Statistical significance testing

### Disadvantages
- **Complexity**: Requires experimentation framework
- **Time**: Needs sufficient data collection period
- **Consistency**: User experience may vary
- **Analysis**: Requires statistical expertise

### Use Cases
- User interface changes
- Feature optimization
- Business metric optimization
- User experience improvements

### Facebook A/B Testing
- Thousands of experiments running simultaneously
- Sophisticated experiment framework
- Automated statistical analysis
- Per-user and per-session targeting

---

## 7. Progressive Delivery

### Description
Progressive delivery combines canary deployments, feature flags, and observability to gradually release features with fine-grained control and automatic rollback.

### Components
1. **Feature Flags**: Toggle features independently of deployment
2. **Canary Deployment**: Gradual traffic shift
3. **Observability**: Metrics, logs, traces
4. **Automated Analysis**: Automatic promotion/rollback
5. **Blast Radius Control**: Limit impact of failures

### Process
1. Deploy code with feature flagged off
2. Enable feature for internal users
3. Gradual rollout with canary pattern
4. Monitor metrics continuously
5. Automated rollback on anomalies
6. Full rollout when validated

### Advantages
- **Fine-Grained Control**: Feature-level, not just deployment
- **Decouple Deploy from Release**: Deploy anytime, release when ready
- **Safety**: Multiple layers of protection
- **Fast Rollback**: Instant flag toggle

### Tools
- Flagger (Kubernetes)
- Argo Rollouts
- Spinnaker
- LaunchDarkly + CD pipeline

---

## Comparison Matrix

| Strategy | Downtime | Resource Cost | Rollback Speed | Complexity | Risk |
|----------|----------|---------------|----------------|------------|------|
| Blue-Green | None | High (2x) | Instant | Medium | Low |
| Canary | None | Low-Medium | Fast | High | Very Low |
| Rolling | None | Low | Slow | Medium | Medium |
| Recreate | High | Low | Slow | Low | High |
| Shadow | None | High (2x) | N/A | High | Very Low |
| A/B Testing | None | Medium | Fast | High | Low |
| Progressive | None | Medium | Instant | Very High | Very Low |

---

## Selection Decision Tree

```
Is downtime acceptable?
├─ Yes → Recreate (simplest)
└─ No
   └─ Can you double infrastructure?
      ├─ Yes → Blue-Green (safest)
      └─ No
         └─ Need production scale testing?
            ├─ Yes → Shadow (before promotion)
            └─ No
               └─ High-risk change?
                  ├─ Yes → Canary + Feature Flags (Progressive Delivery)
                  └─ No → Rolling (balanced approach)
```

---

## Industry Best Practices

### Netflix
- Red-Black (Blue-Green variant) as default
- Automated via Spinnaker
- Chaos Engineering during deployments
- Automated rollback on metric anomalies
- Regional traffic shifting for global services

### Facebook
- Feature flags for all changes
- Gradual rollout: employees → 1% → 10% → 50% → 100%
- Real-time metric dashboards
- Automated experiment analysis
- Dark launches for infrastructure changes

### Google
- Rolling deployments with advanced health checking
- Gradual traffic shifting in GFE (Global Front End)
- Extensive staging environments (prod-like)
- Automated canary analysis
- Version compatibility requirements (n-1, n, n+1)

### Amazon
- Two-pizza team ownership
- Independent service deployments
- Regional rollouts (region-by-region)
- Automatic rollback on CloudWatch alarms
- GameDay exercises for deployment validation

---

## Key Takeaways

1. **No one-size-fits-all**: Choose based on risk tolerance, resources, and requirements
2. **Observability is critical**: Can't manage what you can't measure
3. **Automate rollback**: Manual rollback is too slow
4. **Test in production**: Staging never matches production perfectly
5. **Gradual is safer**: Limit blast radius of failures
6. **Decouple deploy from release**: Feature flags enable this
7. **Practice**: Regular deployments build muscle memory

---

## Additional Resources

- Martin Fowler's Continuous Delivery: https://martinfowler.com/bliki/BlueGreenDeployment.html
- Google SRE Book - Release Engineering: https://sre.google/sre-book/release-engineering/
- Netflix Tech Blog: https://netflixtechblog.com/
- Spinnaker Documentation: https://spinnaker.io/docs/
- Flagger Documentation: https://flagger.app/
