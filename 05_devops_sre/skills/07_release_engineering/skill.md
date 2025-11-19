# Release Engineering - Elite Professional Practices

**Deployment strategies, progressive delivery, and zero-downtime releases at scale**

---

## Overview

Release Engineering manages the planning, execution, and validation of software releases. It encompasses deployment strategies, rollback procedures, and risk mitigation techniques that enable safe, frequent deployments to production without customer-facing downtime.

You are an expert in release engineering practices that enable organizations to deploy hundreds of times per day while maintaining high reliability and minimizing deployment risk.

## Core Principles

### 1. Decouple Deployment from Release

**Deployment**: Getting code into production
**Release**: Making features available to users

```
# Anti-pattern: Deployment = Release
Deploy v1.5 -> Users immediately see changes
Any bugs affect all users instantly
Must be perfect before deploying

# Best practice: Decouple via feature flags
Deploy v1.5 (feature flag OFF) -> No user impact
Test in production with flag OFF
Enable flag for 1% of users
Monitor for issues
Gradually increase to 100%
Rollback is one flag flip
```

**Benefits**:
- Deploy code before it's ready for users
- Test in production safely
- Instant rollback without redeployment
- Gradual rollout for confidence building

### 2. Progressive Delivery

Rolling out changes gradually with monitoring and automatic rollback.

```
Rollout phases:
Week 1: 1% of users (early adopters)
Week 2: 5% of users (more confidence)
Week 3: 25% of users (real-world validation)
Week 4: 100% of users (full rollout)

At each phase:
- Monitor error rates
- Monitor latency/performance
- Monitor business metrics
- If degradation: STOP and rollback
```

## Deployment Strategies

### 1. Blue-Green Deployment

```
Two identical production environments: Blue and Green

Current state: Blue is live (100% traffic)
Deployment:
1. Deploy to Green (no traffic)
2. Run smoke tests against Green
3. When ready: Switch router to Green (atomic)
4. Blue is now idle (ready for next deployment)

Advantages:
- Zero-downtime deployment
- Instant rollback (switch back to Blue)
- Full environment test before switch
- No gradual rollout (all-or-nothing)

Disadvantages:
- Requires 2x infrastructure
- Database migrations still risky
- No gradual validation
```

```yaml
# Kubernetes Blue-Green deployment example
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    version: blue  # Currently pointing to blue
  ports:
  - port: 80
    targetPort: 8080

---
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  selector:
    matchLabels:
      app: myapp
      version: blue
  replicas: 3
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1.2.3

---
# Green deployment (new, not yet receiving traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  selector:
    matchLabels:
      app: myapp
      version: green
  replicas: 3
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:v1.3.0

# When ready to switch:
# kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'
```

### 2. Canary Deployment

```yaml
# Flagger canary deployment (progressive delivery)
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  progressDeadlineSeconds: 60
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5      # Rollback if error rate > 5%
    maxWeight: 50
    stepWeight: 5     # Increase traffic 5% every minute
    metrics:
    - name: error_rate
      thresholdRange:
        max: 1        # Allow max 1% error rate
      interval: 1m
    - name: request_duration
      thresholdRange:
        max: 500      # Allow max 500ms p95 latency
      interval: 1m
  webhooks:
  - name: smoke tests
    url: http://flagger-loadtester/
    timeout: 30s
    metadata:
      type: smoke
      cmd: "curl -s http://app-canary:8080/health"

# Rollout progression:
# Min: 5% -> Metric analysis -> OK -> 10% -> Metric analysis -> OK -> 15% ... -> 100%
# If metric fails: STOP and rollback
```

### 3. Rolling Deployment

```
Traditional Kubernetes deployment strategy.

Start:     [Pod1:v1] [Pod2:v1] [Pod3:v1]
Step 1:    [Pod1:v2] [Pod2:v1] [Pod3:v1]
Step 2:    [Pod1:v2] [Pod2:v2] [Pod3:v1]
Step 3:    [Pod1:v2] [Pod2:v2] [Pod3:v2]

Advantages:
- No extra infrastructure needed
- Gradual rollout
- Old and new versions coexist
- Easy rollback (scale up old version)

Disadvantages:
- Brief period with mixed versions
- Database schema changes risky
- Gradual validation (errors spread)
- Slower than blue-green
```

## Database Migration Strategy

Migrations are the riskiest part of releases. Must be backward-compatible.

```
# Anti-pattern: Big bang migration
Deploy code change that requires schema change
Run migration script
If bad: Data loss, can't rollback

# Best practice: Backward-compatible migrations
Old schema: users(id, name, email)
New schema: users(id, name, email, phone)

Step 1: Add column (no code change)
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

Code deploys with:
- Can read phone (null at first)
- Writes to phone when provided
- Still works if phone is NULL

Step 2: Populate data
UPDATE users SET phone = ... (gradual)

Step 3: Code change
No nullability check needed
phone always available
Rollback safe: code still handles nulls
```

**Migration Patterns**:
```
Expanding (safe):
- Add column (nullable)
- Add table
- Add index

Data migration (safe):
- Copy data
- Fill defaults
- Gradual backfill

Contracting (risky):
- Remove column (wait for code to stop using)
- Remove table
- Drop index (verify no queries use)
```

## Technology Stack

### Spinnaker (Netflix)

**Enterprise CD platform with advanced deployment strategies**

```
Features:
- Blue-green deployments
- Canary analysis (automated rollback)
- Traffic management
- Multi-cloud support
- Pipeline orchestration
- Deployment verification
```

### Flagger

**Progressive delivery operator for Kubernetes**

```
Features:
- Canary deployments
- A/B testing
- Traffic mirroring
- Automatic rollback
- Service mesh integration (Istio, Linkerd)
- Webhook for custom checks
```

### ArgoCD

**GitOps continuous delivery for Kubernetes**

```
Features:
- Declarative deployments
- Git as source of truth
- Sync to cluster
- Rollback via Git revert
- Multi-cluster support
- Progressive sync strategy
```

## Implementation Patterns

### Deployment Checklist

```
Pre-deployment:
- [ ] Code reviewed and approved
- [ ] All tests passing
- [ ] Security scanning clear
- [ ] Database migrations tested
- [ ] Rollback procedure documented and tested
- [ ] Monitoring/alerting ready
- [ ] Feature flags configured
- [ ] Communication plan (status page, team, customers)

Deployment:
- [ ] Minimal traffic time window chosen
- [ ] Backup taken (database)
- [ ] Database migration applied to staging first
- [ ] Deploy to staging and validate
- [ ] Run smoke tests
- [ ] Deploy to production (canary/blue-green)
- [ ] Monitor metrics during rollout
- [ ] Gradually increase traffic/percentage

Post-deployment:
- [ ] Verify all metrics normal
- [ ] Customer feedback monitored
- [ ] Documentation updated
- [ ] Lessons learned captured
```

### Deployment Verification

```bash
#!/bin/bash
# Automated deployment verification

# Health check
curl -f https://api.example.com/health || exit 1

# Critical business transactions
response=$(curl -s -X POST https://api.example.com/checkout \
  -d '{"items":[{"id":1,"qty":1}]}')
echo $response | jq '.total' > /dev/null || exit 1

# Latency check
start=$(date +%s%N)
curl -s https://api.example.com/products > /dev/null
elapsed=$(($(date +%s%N) - start))
# Check under 500ms (in nanoseconds: 500,000,000)
[ $elapsed -lt 500000000 ] || exit 1

# Error rate check
errors=$(curl -s https://api.example.com/metrics | grep http_requests_total)
error_rate=$(echo $errors | awk '{print $NF}')
[ $(echo "$error_rate < 0.01" | bc) -eq 1 ] || exit 1

echo "All checks passed"
```

## Best Practices

### 1. Database Migrations

```python
# Always write migrations that can be rolled back
# Safe migration: Add nullable column, backfill gradually, make required later

# alembic migration (SQLAlchemy)
def upgrade():
    op.add_column('users',
        sa.Column('phone', sa.String(20), nullable=True))
    # Later migration makes not null after data backfilled

def downgrade():
    op.drop_column('users', 'phone')

# Unsafe: Don't do this
def upgrade():
    op.alter_column('users', 'status',
        existing_type=sa.String(50),
        type_=sa.Enum(StatusEnum))
    # Can't rollback enum changes easily
```

### 2. Rollback Procedures

```bash
# Always test rollback procedure before deploying

# Option 1: Rollback via code revert
git revert HEAD
git push
kubectl set image deployment/app app=myapp:v1.2.2

# Option 2: Rollback via Kubernetes
kubectl rollout undo deployment/app

# Option 3: Database schema rollback
alembic downgrade -1

# Important: Test all options in staging first
```

### 3. Feature Flags for Quick Rollback

```python
# Instead of rolling back code:
@app.route('/checkout')
def checkout():
    if feature_flag('new_checkout_v2'):
        return new_checkout_handler()
    else:
        return legacy_checkout_handler()

# Problem: Payment error in new checkout
# Rollback: Flip feature flag OFF (instant, no redeployment)
```

### 4. Deployment Window Management

```
Guidelines:
- Avoid deployments during peak usage hours
- Avoid deployments Friday afternoon (no weekend support)
- Never deploy on-call engineer should be present
- Deployments during business hours better (can revert quickly)
- Schedule large/risky deployments during low-traffic windows

Example safe times:
- Tuesday-Thursday 10am-2pm (business hours, mid-week)
- Never: Friday 5pm-Sunday (no support)
- Never: Known product events/launches
```

### 5. Communication

```
During deployment:
- Status page: "Deploying new checkout v1.3"
- Team chat: Announce deployment start/finish
- Customer notification: Only if customer-facing change

Post-deployment:
- Update deployment log
- Document any issues encountered
- Update runbook if process changed
- Share learnings with team
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Netflix Spinnaker, Google, Amazon deployment practices
