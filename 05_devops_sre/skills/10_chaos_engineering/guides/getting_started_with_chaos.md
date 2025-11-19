# Getting Started with Chaos Engineering

## Overview

This guide provides a practical, step-by-step approach to implementing chaos engineering in your organization. Whether you're just learning about chaos engineering or ready to run your first experiment, this guide will help you get started safely and effectively.

## Prerequisites

Before starting chaos engineering, ensure you have:

**Technical Prerequisites**:
- Monitoring and observability in place
- Basic incident response procedures
- Understanding of your system architecture
- Ability to deploy changes to non-production environments
- Basic knowledge of your infrastructure (cloud provider, Kubernetes, etc.)

**Organizational Prerequisites**:
- Management buy-in for chaos engineering
- Dedicated time for experiments (not just "when we have time")
- Blameless culture for discussing failures
- Team members willing to learn and experiment

**Observability Requirements** (Critical!):
```
✓ Metrics collection (Prometheus, CloudWatch, Datadog, etc.)
✓ Distributed tracing (Jaeger, Zipkin, AWS X-Ray)
✓ Centralized logging (ELK, Splunk, CloudWatch Logs)
✓ Real-time dashboards
✓ Alerting system
✓ SLI/SLO definitions
```

> Without good observability, you cannot do chaos engineering safely or effectively!

---

## Phase 1: Education and Planning (Week 1)

### Day 1-2: Learn the Fundamentals

**Read**:
1. Principles of Chaos Engineering (principlesofchaos.org)
2. Netflix blog posts on chaos engineering
3. Your system's architecture documentation

**Watch**:
- "Chaos Engineering" by Netflix on YouTube
- AWS re:Invent talks on chaos engineering
- CNCF chaos engineering presentations

**Action Items**:
```
□ Read chaos engineering principles
□ Watch 2-3 introductory videos
□ Review your system architecture diagrams
□ Identify your critical user journeys
□ List your dependencies (databases, APIs, caches, etc.)
```

### Day 3-4: Assess Your Current State

**Map Your System**:
```
1. Critical Services
   - User authentication
   - Payment processing
   - Order fulfillment
   - [Your critical services]

2. Dependencies
   - Databases (PostgreSQL, MySQL, MongoDB)
   - Caches (Redis, Memcached)
   - Message queues (Kafka, RabbitMQ, SQS)
   - External APIs (Stripe, Twilio, etc.)
   - Cloud services (S3, RDS, etc.)

3. Infrastructure
   - Compute (EC2, Kubernetes, serverless)
   - Network (VPC, load balancers, service mesh)
   - Storage (EBS, S3, NFS)
```

**Assess Resilience Mechanisms**:
```
□ Circuit breakers implemented?
□ Retry logic with backoff?
□ Timeout configurations?
□ Health checks?
□ Auto-scaling?
□ Multi-region/AZ deployment?
□ Database replication?
□ Backup and restore procedures?
```

### Day 5: Define Success Metrics

**Establish Baseline Metrics**:

**System Health Indicators (SLIs)**:
```yaml
Availability:
  - Service uptime: 99.9%
  - Request success rate: > 99.5%

Performance:
  - p50 latency: < 100ms
  - p99 latency: < 500ms
  - p99.9 latency: < 2000ms

Throughput:
  - Requests per second: 1000-5000 RPS
  - Orders per minute: 100 OPM

Error Rates:
  - 4xx errors: < 1%
  - 5xx errors: < 0.1%
```

**Business Metrics**:
```yaml
User Experience:
  - Cart abandonment rate: < 10%
  - Checkout success rate: > 95%
  - Page load time: < 3 seconds

Revenue:
  - Orders per hour
  - Revenue per minute
  - Conversion rate
```

**Action Items**:
```
□ Document steady state metrics
□ Create dashboards for key metrics
□ Set up baseline alerts
□ Run baseline load tests
□ Document current performance
```

---

## Phase 2: First Experiments in Non-Production (Week 2-3)

### Choose Your First Tool

**For Kubernetes Users**:
- **Litmus Chaos**: Free, cloud-native, good community
- **Chaos Mesh**: Free, excellent UI, good for complex scenarios

**For AWS Users**:
- **AWS FIS**: Managed, easy to start, AWS-native

**For Multi-Cloud or VMs**:
- **Gremlin**: Best UI/UX, easiest to learn (free tier available)

### Install Your Chaos Tool

#### Option A: Litmus (Kubernetes)

```bash
# Add Litmus Helm repo
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm repo update

# Create namespace
kubectl create namespace litmus

# Install Litmus
helm install chaos litmuschaos/litmus \
  --namespace litmus \
  --set portal.frontend.service.type=LoadBalancer

# Install chaos experiments
kubectl apply -f https://hub.litmuschaos.io/api/chaos/master?file=charts/generic/experiments.yaml

# Get admin credentials
kubectl get secret litmus-portal-admin-secret \
  -n litmus \
  -o jsonpath="{.data.JWT_ADMIN_PASSWORD}" | base64 -d
```

#### Option B: Chaos Mesh (Kubernetes)

```bash
# Install Chaos Mesh
curl -sSL https://mirrors.chaos-mesh.org/v2.6.0/install.sh | bash

# Verify installation
kubectl get pods -n chaos-mesh

# Access dashboard (port-forward)
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333

# Access at http://localhost:2333
```

#### Option C: Gremlin (Any platform)

```bash
# Sign up at https://app.gremlin.com (free tier available)

# Install agent on Linux
curl https://rpm.gremlin.com/gremlin.repo -o /etc/yum.repos.d/gremlin.repo
yum install -y gremlin gremlind

# Configure with your credentials (from Gremlin web UI)
gremlin init

# Start Gremlin daemon
systemctl enable gremlind
systemctl start gremlind

# Verify
gremlin check
```

### Experiment 1: Pod/Instance Deletion (Simplest Start)

**Objective**: Verify that deleting a single instance doesn't cause service disruption.

**Pre-experiment Checklist**:
```
□ Dashboard open and monitoring key metrics
□ Alert channels active (Slack, PagerDuty, etc.)
□ Team aware and available
□ Runbook ready for rollback
□ At least 3 healthy instances running
□ Auto-scaling enabled
```

**Hypothesis**:
```
Given: API service has 5 replicas running
When: We delete 1 random pod/instance
Then:
  - Service maintains > 99% success rate
  - p99 latency remains < 500ms
  - New pod is scheduled within 30 seconds
  - Load balancer updates within 10 seconds
```

**Kubernetes (Litmus)**:
```yaml
# pod-delete-experiment.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: first-chaos-experiment
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: 'app=api-server'
    appkind: deployment
  engineState: active
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            # Delete only 1 pod
            - name: TOTAL_CHAOS_DURATION
              value: '30'

            # Wait 30 seconds (just one deletion)
            - name: CHAOS_INTERVAL
              value: '30'

            # Graceful termination
            - name: FORCE
              value: 'false'

            # Target 1 pod
            - name: PODS_AFFECTED_PERC
              value: '20'  # 1 out of 5
```

**Execute**:
```bash
# Apply the experiment
kubectl apply -f pod-delete-experiment.yaml

# Watch pods
kubectl get pods -n staging -w -l app=api-server

# Check experiment status
kubectl get chaosengine -n staging

# View logs
kubectl logs -n litmus -l app=chaos-operator
```

**During Experiment - Monitor**:
```
1. Open Grafana/Datadog dashboard
2. Watch these metrics:
   - Request success rate
   - Latency percentiles (p50, p99, p999)
   - Active pod count
   - Error logs
3. Check load balancer status
4. Verify no alerts fired
```

**Post-Experiment Analysis**:
```bash
# Check if hypothesis was validated
□ Success rate maintained?
□ Latency acceptable?
□ Pod replaced quickly?
□ No manual intervention needed?

# Document findings
□ What worked well?
□ What was surprising?
□ What needs improvement?
□ Follow-up experiments?
```

### Experiment 2: Network Latency (Introduce Variability)

**Objective**: Test application behavior under network delays.

**Hypothesis**:
```
Given: Frontend service calling backend with 50ms avg latency
When: We add 200ms network latency to 50% of pods
Then:
  - Frontend timeout settings prevent cascading failures
  - Circuit breaker does NOT trip (latency, not failures)
  - User experience degrades gracefully
  - p99 latency increases but stays under 1000ms
```

**Chaos Mesh**:
```yaml
# network-latency-experiment.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-latency-test
  namespace: chaos-mesh
spec:
  action: delay
  mode: fixed-percent
  value: "50"  # Affect 50% of pods

  selector:
    namespaces:
      - staging
    labelSelectors:
      app: backend-api

  delay:
    latency: '200ms'
    correlation: '0'
    jitter: '50ms'

  duration: '2m'

  # Only affect traffic TO this service
  direction: to
```

**Execute**:
```bash
# Apply
kubectl apply -f network-latency-experiment.yaml

# Monitor
kubectl get networkchaos -n chaos-mesh -w

# Check affected pods
kubectl get pods -n staging -l app=backend-api
```

**Expected Observations**:
```
✓ Latency increases visible in metrics
✓ Some requests slower, some normal
✓ No timeouts or errors
✓ Circuit breaker stays closed
✓ Auto-recovery after 2 minutes
```

### Experiment 3: CPU Stress (Resource Constraint)

**Objective**: Verify auto-scaling triggers under CPU pressure.

**Hypothesis**:
```
Given: Service has HPA (Horizontal Pod Autoscaler) targeting 70% CPU
When: We stress CPU to 90% on existing pods
Then:
  - HPA scales out within 60 seconds
  - New pods are scheduled and become ready
  - Service maintains acceptable performance
  - No manual intervention required
```

**Litmus**:
```yaml
# cpu-stress-experiment.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: cpu-stress-test
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: 'app=worker-service'
    appkind: deployment
  engineState: active
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-cpu-hog
      spec:
        components:
          env:
            - name: CPU_CORES
              value: '2'

            - name: TOTAL_CHAOS_DURATION
              value: '180'  # 3 minutes

            - name: CPU_LOAD
              value: '90'

            - name: PODS_AFFECTED_PERC
              value: '100'  # All pods
```

**Monitor Auto-Scaling**:
```bash
# Watch HPA
kubectl get hpa -n staging -w

# Watch pod count
kubectl get pods -n staging -l app=worker-service -w

# Check events
kubectl get events -n staging --sort-by='.lastTimestamp'
```

---

## Phase 3: Building Confidence (Week 4-6)

### Expand Experiment Variety

**Week 4: Stateful Service Testing**
```
Experiments:
1. Database connection failure (block port 5432)
2. Redis cache deletion
3. Message queue delays
```

**Week 5: Combined Failures**
```
Experiments:
1. Pod deletion + network latency
2. CPU stress + memory pressure
3. Multi-service cascading scenario
```

**Week 6: Advanced Scenarios**
```
Experiments:
1. Availability zone failure simulation
2. Database failover
3. Complete service dependency failure
```

### Example: Database Failover Test

```yaml
# postgres-failover.yaml (AWS FIS for RDS)
{
  "description": "Test application behavior during RDS failover",
  "targets": {
    "db-cluster": {
      "resourceType": "aws:rds:cluster",
      "resourceArns": ["arn:aws:rds:us-east-1:123456789012:cluster:staging-db"],
      "selectionMode": "ALL"
    }
  },
  "actions": {
    "failover": {
      "actionId": "aws:rds:failover-db-cluster",
      "description": "Failover database to replica",
      "targets": {
        "Clusters": "db-cluster"
      }
    }
  },
  "stopConditions": [
    {
      "source": "aws:cloudwatch:alarm",
      "value": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:AppErrorRateHigh"
    }
  ],
  "roleArn": "arn:aws:iam::123456789012:role/FISRole"
}
```

**Pre-Experiment**:
```
□ Verify database replication is healthy
□ Check application connection pooling config
□ Review retry and timeout settings
□ Ensure monitoring captures connection errors
□ Alert team of upcoming experiment
```

**Expected Behavior**:
```
✓ Brief connection failures (< 30 seconds)
✓ Application retries succeed after failover
✓ No data loss
✓ Automatic reconnection to new primary
✓ Metrics show spike then recovery
```

---

## Phase 4: Production Readiness (Week 7-8)

### Before Running Chaos in Production

**Prerequisites**:
```
✓ Successful experiments in staging/dev
✓ Team trained and comfortable with chaos
✓ Comprehensive observability
✓ Incident response procedures tested
✓ Rollback mechanisms proven
✓ Management approval obtained
✓ Customer communication plan (if needed)
```

### Start with Lowest Risk

**Progressive Production Rollout**:

**Week 7: Single Instance, Short Duration**
```yaml
Experiment: Pod delete
Blast Radius: 1 pod out of 20 (5%)
Duration: 30 seconds
Time: Tuesday 10am (business hours, team available)
Stakeholders: Notified in advance
```

**Week 8: Increased Scope**
```yaml
Experiment: Pod delete + Network latency
Blast Radius: 10% of pods
Duration: 2 minutes
Time: Tuesday 2pm
Stakeholders: Notified
```

### Production Experiment Checklist

**Pre-Flight**:
```
□ Experiment plan reviewed by team
□ Hypothesis clearly defined
□ Abort conditions configured
□ Dashboards open and ready
□ Team in Slack/Teams channel
□ Customer support team notified
□ Status page prepared (if needed)
□ Runbook accessible
□ Recent backup verified (for data stores)
```

**During Experiment**:
```
□ Monitor metrics in real-time
□ Watch for unexpected behavior
□ Check error logs continuously
□ Monitor social media/support tickets
□ Be ready to abort immediately
□ Document observations
```

**Post-Experiment**:
```
□ Verify system returned to steady state
□ Check for delayed effects (15-30 min after)
□ Review all metrics and logs
□ Document findings
□ Share results with team
□ Create action items for improvements
□ Update runbooks if needed
```

---

## Common First Experiment Mistakes

### Mistake 1: No Baseline Metrics
**Problem**: Running chaos without knowing normal behavior.
**Solution**: Collect 1-2 weeks of baseline metrics first.

### Mistake 2: Insufficient Observability
**Problem**: Can't see what's happening during chaos.
**Solution**: Implement comprehensive monitoring before any chaos.

### Mistake 3: Too Large Blast Radius
**Problem**: First experiment affects 50% of production.
**Solution**: Start with 1 instance, 30 seconds, in non-production.

### Mistake 4: No Abort Conditions
**Problem**: Experiment continues even when causing harm.
**Solution**: Always configure automatic stop conditions.

### Mistake 5: Running Alone
**Problem**: Solo experiment without team awareness.
**Solution**: Always inform team, run during business hours.

### Mistake 6: Ignoring Results
**Problem**: Running experiments but not fixing discovered issues.
**Solution**: Track findings, prioritize fixes, re-test after fixes.

### Mistake 7: One-and-Done
**Problem**: Single experiment then abandoning chaos engineering.
**Solution**: Make chaos a continuous practice, not a project.

---

## Your First 90 Days - Roadmap

### Month 1: Foundation
```
Week 1: Education and planning
Week 2: Tool installation and first experiment (non-prod)
Week 3: 3-5 more experiments (non-prod)
Week 4: Review findings and improve system
```

### Month 2: Expansion
```
Week 5-6: Expand experiment types
Week 7-8: First production experiments (low risk)
```

### Month 3: Maturity
```
Week 9-10: Regular production experiments
Week 11-12: Automation and GameDays
```

### Month 4+: Continuous Practice
```
- Automated daily/weekly experiments
- Monthly GameDays
- Chaos as part of development lifecycle
- Team chaos champions
```

---

## Quick Start Templates

### Template 1: First Pod Delete

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: my-first-chaos
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: 'app=<YOUR-APP>'
    appkind: deployment
  engineState: active
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '30'
            - name: CHAOS_INTERVAL
              value: '30'
            - name: FORCE
              value: 'false'
```

### Template 2: First Network Latency

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: my-first-latency
  namespace: chaos-mesh
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - staging
    labelSelectors:
      app: <YOUR-APP>
  delay:
    latency: '100ms'
  duration: '1m'
```

### Template 3: Experiment Log

```markdown
# Experiment: [Name]
**Date**: YYYY-MM-DD
**Engineer**: [Your Name]
**Environment**: Staging

## Hypothesis
Given: [Current state]
When: [Chaos injection]
Then: [Expected outcome]

## Configuration
- Tool: Litmus/Chaos Mesh/Gremlin
- Target: [Service name]
- Duration: X minutes
- Blast radius: X%

## Results
- Hypothesis validated: Yes/No
- Observations:
  - [What happened]
  - [Unexpected behaviors]
  - [Metrics during experiment]

## Action Items
- [ ] Fix: [Issue found]
- [ ] Improve: [Enhancement needed]
- [ ] Next experiment: [Follow-up test]
```

---

## Getting Help

### Community Resources
- **Chaos Engineering Slack**: chaosengineering.slack.com
- **CNCF Chaos Engineering WG**: github.com/cncf/tag-app-delivery
- **Awesome Chaos Engineering**: github.com/dastergon/awesome-chaos-engineering

### Tool-Specific
- **Litmus**: litmuschaos.io, Slack: litmuschaos.slack.com
- **Chaos Mesh**: chaos-mesh.org, Slack: cloud-native.slack.com #project-chaos-mesh
- **Gremlin**: gremlin.com/docs, support@gremlin.com

### Books
- "Chaos Engineering" by Casey Rosenthal & Nora Jones (O'Reilly)
- "Learning Chaos Engineering" by Russ Miles (O'Reilly)

---

## Key Takeaways

1. **Start Small**: One instance, short duration, non-production
2. **Observability First**: You can't do chaos without good monitoring
3. **Hypothesis-Driven**: Always know what you're testing
4. **Safety First**: Abort conditions and blast radius control
5. **Learn and Improve**: Fix what you find, then test again
6. **Make it Continuous**: Chaos is a practice, not a project
7. **Involve the Team**: Chaos is a team sport

## Next Steps

After completing your first experiments:
1. Read the "Chaos in Production" guide
2. Plan your first GameDay (see GameDay Planning Guide)
3. Start building your chaos experiment library
4. Share your learnings with the team
5. Make chaos part of your regular workflow

Remember: The goal of chaos engineering isn't to break things—it's to build confidence in your system's ability to handle failure. Start small, learn continuously, and gradually expand your chaos practice. Welcome to chaos engineering!
