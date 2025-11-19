# Chaos Engineering Principles

## Overview

Chaos Engineering is the discipline of experimenting on a system to build confidence in the system's capability to withstand turbulent conditions in production. This reference covers the foundational principles established by Netflix and the broader chaos engineering community.

## Core Definition

**Chaos Engineering**: The discipline of experimenting on a distributed system in order to build confidence in the system's capability to withstand turbulent and unexpected conditions.

## Netflix Principles of Chaos Engineering

Netflix pioneered chaos engineering with their Chaos Monkey tool and established these foundational principles:

### 1. Build a Hypothesis Around Steady State Behavior

**Principle**: Define "steady state" as some measurable output of a system that indicates normal behavior.

**Key Concepts**:
- Focus on the measurable output of a system (throughput, error rates, latency percentiles)
- Don't focus on internal system attributes
- Steady state represents normal business operations
- Use metrics that matter to the business (e.g., orders per second, stream starts per minute)

**Example Metrics**:
```
- Request success rate: > 99.9%
- p99 latency: < 200ms
- Throughput: 1000 requests/second
- Error rate: < 0.1%
- Database connection pool utilization: < 80%
```

### 2. Hypothesize that Steady State Will Continue in Both Control and Experimental Groups

**Principle**: For each experiment, create a hypothesis that assumes the steady state will continue in both the control group (normal) and experimental group (with chaos).

**Experiment Structure**:
```
Given: A distributed system in steady state
When: We introduce [specific failure condition]
Then: The system will maintain [specific steady state metric]
      within [acceptable threshold]
```

**Example Hypothesis**:
```
Given: Shopping cart service processing 5000 orders/min
When: We terminate 2 out of 10 service instances
Then: Order processing rate will remain > 4500 orders/min
      AND p99 latency will remain < 500ms
      AND error rate will remain < 1%
```

### 3. Vary Real-World Events

**Principle**: Chaos variables reflect real-world events, prioritized by either potential impact or estimated frequency.

**Categories of Real-World Events**:

#### Hardware Failures
- Server crashes
- Hard drive failures
- Network hardware failures
- Power outages
- Rack failures

#### Software Failures
- Service crashes
- Memory leaks
- Dependency failures
- Configuration errors
- Deployment failures

#### Network Events
- Network partitions (split-brain scenarios)
- High latency
- Packet loss
- DNS failures
- Load balancer failures

#### Resource Exhaustion
- CPU saturation
- Memory exhaustion
- Disk space exhaustion
- File descriptor limits
- Connection pool exhaustion

#### Upstream/Downstream Dependencies
- Third-party API failures
- Database failures
- Cache failures
- Message queue failures
- Authentication service failures

### 4. Run Experiments in Production

**Principle**: Systems behave differently depending on environment and traffic patterns. To fully understand how the system behaves, you must experiment where the system is used.

**Why Production?**:
- Real traffic patterns cannot be perfectly simulated
- Real data volumes and distributions differ from test environments
- Real user behavior is unpredictable
- Dependencies behave differently under real load
- State accumulation reveals different failure modes

**Production Safety Measures**:
```
1. Start with lowest risk experiments
2. Limit blast radius (percentage of traffic)
3. Have abort mechanisms ready
4. Run during business hours with full team available
5. Monitor closely during experiments
6. Have rollback plans prepared
7. Get organizational buy-in and communicate plans
```

**Progressive Rollout**:
```
Phase 1: Single instance, development environment
Phase 2: Staging environment with production-like load
Phase 3: Production, 1% of traffic, short duration
Phase 4: Production, 5% of traffic, extended duration
Phase 5: Production, 25% of traffic
Phase 6: Production, full rollout (continuous chaos)
```

### 5. Automate Experiments to Run Continuously

**Principle**: Running experiments manually is labor-intensive and ultimately unsustainable. Automate experiments and run them continuously.

**Automation Benefits**:
- Consistent execution
- Continuous validation
- Regression detection
- Reduced human error
- Scales with system growth

**Automation Levels**:

**Level 1: Manual Execution**
```
- Engineer manually triggers experiments
- Manual observation and analysis
- One-off experiments
```

**Level 2: Scheduled Automation**
```
- Experiments run on schedule
- Automated monitoring
- Manual analysis of results
```

**Level 3: Continuous Chaos**
```
- Experiments run continuously
- Automated analysis and alerting
- Self-healing validation
- Regression detection
```

**Level 4: Adaptive Chaos**
```
- System learns from experiments
- Automatically adjusts blast radius
- Self-optimizing experiment parameters
- Predictive failure injection
```

### 6. Minimize Blast Radius

**Principle**: Experiments must be designed to minimize potential customer impact while still producing valid results.

**Blast Radius Control Techniques**:

**Traffic Percentage**:
```
- Start with 1% of production traffic
- Gradually increase if no issues detected
- Use feature flags to control exposure
```

**Time Boxing**:
```
- Run experiments for minimal time needed
- Set maximum duration limits
- Have automated abort conditions
```

**Geographic Isolation**:
```
- Start with single region or AZ
- Avoid critical regions initially
- Distribute risk across boundaries
```

**User Segmentation**:
```
- Use internal users first
- Beta user groups
- Non-premium customers
- Gradual rollout to all users
```

## Netflix Chaos Monkey Practices

### Original Chaos Monkey (2010)

**Purpose**: Randomly terminate EC2 instances during business hours to ensure services are resilient to instance failures.

**Key Characteristics**:
- Runs during business hours (9am-3pm Pacific)
- Terminates one instance at a time
- Only affects production environment
- Teams must build resilience or face frequent outages

**Design Philosophy**:
```
"If we aren't constantly testing our ability to succeed despite failure,
then it isn't likely to work when it matters most – in the event of an
unexpected outage."
```

### Simian Army Evolution

Netflix expanded beyond Chaos Monkey to create the Simian Army:

**Chaos Monkey**: Terminates instances
**Chaos Gorilla**: Simulates entire AWS availability zone failure
**Chaos Kong**: Simulates entire AWS region failure
**Latency Monkey**: Introduces artificial delays
**Conformity Monkey**: Finds instances that don't adhere to best practices
**Doctor Monkey**: Finds unhealthy instances
**Janitor Monkey**: Finds and removes unused resources
**Security Monkey**: Finds security violations
**10-18 Monkey**: Detects configuration/runtime issues in different geographic regions

### Modern Chaos Engineering at Netflix (ChAP)

**ChAP (Chaos Automation Platform)**: Next-generation platform replacing Simian Army

**Capabilities**:
- Failure injection (FIT - Failure Injection Testing)
- Automated experiment orchestration
- Multi-dimensional blast radius control
- Real-time impact analysis
- Automated rollback
- Integration with CI/CD pipelines

## Experiment Design Methodology

### Scientific Method Applied to Chaos

```
1. Observe the system
   ↓
2. Form a hypothesis
   ↓
3. Design the experiment
   ↓
4. Define abort conditions
   ↓
5. Run the experiment
   ↓
6. Measure and observe
   ↓
7. Analyze results
   ↓
8. Document learnings
   ↓
9. Expand or iterate
```

### Experiment Template

```markdown
# Experiment: [Name]

## Metadata
- **Date**: YYYY-MM-DD
- **Owner**: Team/Person
- **Duration**: X minutes
- **Blast Radius**: X% of traffic/instances

## Hypothesis
Given: [Current state]
When: [Failure injection]
Then: [Expected outcome]

## Steady State Definition
- Metric 1: [metric] [operator] [threshold]
- Metric 2: [metric] [operator] [threshold]
- ...

## Failure Injection
- Type: [network/compute/resource/etc]
- Target: [specific service/component]
- Method: [how failure is introduced]
- Scope: [percentage/instances affected]

## Abort Conditions
- Condition 1: [metric] [operator] [threshold]
- Condition 2: [metric] [operator] [threshold]
- Maximum duration exceeded

## Monitoring
- Dashboard: [link]
- Key metrics: [list]
- Alerts: [configured alerts]

## Results
- Hypothesis validated: [Yes/No]
- Observations: [what happened]
- Metrics during experiment: [data]

## Learnings
- What worked well
- What needs improvement
- Action items

## Follow-up Experiments
- [List of next experiments]
```

### Experiment Progression

**Week 1-2: Discovery**
```
- Identify critical user journeys
- Map dependencies
- Establish steady state metrics
- Design initial low-risk experiments
```

**Week 3-4: Initial Experiments**
```
- Single instance failures
- Non-production experiments
- Short duration
- Manual execution
```

**Month 2-3: Production Experiments**
```
- Small blast radius (1-5%)
- Critical path testing
- Dependency failure testing
- Automated monitoring
```

**Month 4-6: Advanced Experiments**
```
- Multi-component failures
- Cascading failures
- State-dependent failures
- Larger blast radius (10-25%)
```

**Month 7+: Continuous Chaos**
```
- Automated continuous execution
- Full coverage of failure modes
- GameDay exercises
- Chaos as a service
```

## Advanced Principles

### Principle: Test on Real Dependencies

Don't mock dependencies in chaos experiments. Test against real services to discover:
- Actual timeout behavior
- Real retry logic effectiveness
- Actual circuit breaker performance
- True fallback behavior

### Principle: Chaos Engineering ≠ Testing

**Testing**: Validates known behavior, expects specific outcomes
**Chaos Engineering**: Explores unknown behavior, discovers emergent properties

```
Testing asks: "Does the system work as designed?"
Chaos asks: "What happens when things go wrong?"
```

### Principle: Embrace the Blast Radius

While you minimize blast radius for safety, embrace that some customer impact is necessary for valid experiments:
```
- Synthetic traffic doesn't reveal real issues
- Canary deployments aren't the same as chaos
- Real failures teach real lessons
```

### Principle: Make Chaos Part of Development

Integrate chaos early in the development lifecycle:
```
- Unit tests: Test individual component resilience
- Integration tests: Test service interaction failures
- Staging: Run automated chaos experiments
- Production: Continuous chaos validation
```

### Principle: Build Observability First

You cannot do chaos engineering without excellent observability:
```
Required capabilities:
- Real-time metrics with <1 minute granularity
- Distributed tracing
- Structured logging
- Alerting and anomaly detection
- Business metric dashboards
```

## Measuring Chaos Engineering Success

### Lagging Indicators
- Reduced MTTR (Mean Time To Recovery)
- Reduced incident frequency
- Improved SLA/SLO compliance
- Reduced customer impact from incidents

### Leading Indicators
- Number of experiments conducted
- Coverage of failure modes
- Number of weaknesses discovered
- Number of resilience improvements made
- Time from experiment to remediation

### Cultural Indicators
- Team confidence in production deployments
- Reduced incident stress
- Faster incident response
- Proactive vs reactive incident management
- Cross-team collaboration on resilience

## Common Anti-Patterns

### Anti-Pattern 1: Testing Without Hypothesis
**Problem**: Running chaos "to see what happens"
**Solution**: Always form a hypothesis based on system understanding

### Anti-Pattern 2: Blame Culture
**Problem**: Using chaos to point fingers at teams
**Solution**: Focus on system improvement, not individual blame

### Anti-Pattern 3: Chaos Theater
**Problem**: Running experiments for show without real risk
**Solution**: Ensure experiments have meaningful blast radius

### Anti-Pattern 4: Set and Forget
**Problem**: Running same experiments without evolution
**Solution**: Continuously expand experiment scope and complexity

### Anti-Pattern 5: Post-Incident Only
**Problem**: Only doing chaos after major incidents
**Solution**: Make chaos a continuous practice

### Anti-Pattern 6: Ignoring Results
**Problem**: Running experiments but not fixing discovered issues
**Solution**: Track findings and remediation as first-class work

## References and Further Reading

**Original Papers**:
- "Principles of Chaos Engineering" - Netflix (2012)
- "Chaos Engineering: Building Confidence in System Behavior" - O'Reilly (2017)

**Netflix Engineering Blog**:
- "The Netflix Simian Army" (2011)
- "FIT: Failure Injection Testing" (2014)
- "ChAP: Chaos Automation Platform" (2016)
- "Chaos Engineering: the history, principles, and practice" (2018)

**Community Resources**:
- Chaos Engineering Community: principlesofchaos.org
- Awesome Chaos Engineering: github.com/dastergon/awesome-chaos-engineering
- CNCF Chaos Engineering Working Group

**Books**:
- "Chaos Engineering" by Casey Rosenthal and Nora Jones (O'Reilly, 2020)
- "Learning Chaos Engineering" by Russ Miles (O'Reilly, 2019)
- "Site Reliability Engineering" by Beyer et al. (O'Reilly, 2016) - Chapter 32

## Summary

Chaos Engineering, pioneered by Netflix, represents a fundamental shift from reactive to proactive reliability engineering. By deliberately introducing failures in controlled experiments, teams build confidence in their systems' resilience and discover weaknesses before they cause customer-impacting incidents.

The key is starting small, building organizational trust, and progressively expanding both the scope and automation of chaos experiments until it becomes a natural part of the development and operations lifecycle.
