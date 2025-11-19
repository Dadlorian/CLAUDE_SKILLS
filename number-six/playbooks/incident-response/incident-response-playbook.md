# Incident Response Playbook
## Comprehensive Guide for Managing Production Incidents

---

## 🎯 Overview

This playbook provides a **structured approach** to handling production incidents, based on Site Reliability Engineering (SRE) practices from Google, Amazon, and other tech leaders.

**Goal**: Minimize impact, restore service quickly, learn from incidents, and prevent recurrence.

---

## 📋 Quick Reference Card

**Print this and keep it handy!**

```markdown
┌─────────────────────────────────────────────────────────┐
│ INCIDENT RESPONSE QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 1. DETECT → Alert received or issue reported            │
│    ↓                                                     │
│ 2. ASSESS → Determine severity (P0-P4)                  │
│    ↓                                                     │
│ 3. RESPOND → Page on-call, assemble team                │
│    ↓                                                     │
│ 4. MITIGATE → Stop the bleeding                         │
│    ↓                                                     │
│ 5. COMMUNICATE → Update status page, notify users       │
│    ↓                                                     │
│ 6. RESOLVE → Fix root cause                             │
│    ↓                                                     │
│ 7. RECOVER → Verify service restored                    │
│    ↓                                                     │
│ 8. LEARN → Post-mortem, prevent recurrence              │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ SEVERITY LEVELS                                          │
├─────────────────────────────────────────────────────────┤
│ P0 (Critical): Complete service outage                  │
│   Response: Immediate (<5 min)                          │
│   Update Frequency: Every 30 min                        │
│                                                          │
│ P1 (High): Major feature down, significant impact       │
│   Response: <15 min                                     │
│   Update Frequency: Every hour                          │
│                                                          │
│ P2 (Medium): Degraded service, limited impact           │
│   Response: <1 hour                                     │
│   Update Frequency: Daily                               │
│                                                          │
│ P3 (Low): Minor issue, workaround available             │
│   Response: Next business day                           │
│   Update Frequency: When resolved                       │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ CONTACTS                                                 │
├─────────────────────────────────────────────────────────┤
│ On-Call: [PagerDuty/Phone]                             │
│ Incident Commander: [Contact]                           │
│ Engineering Manager: [Contact]                          │
│ Status Page: status.example.com                         │
│ Slack Channel: #incidents                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 Severity Levels

### P0 - Critical (SEV-1)

**Definition**: Complete service outage or critical security breach

**Examples**:
- Website/API completely down (500 errors)
- Database inaccessible
- Payment processing broken
- Data breach or security incident
- Complete loss of functionality

**Response**:
- **Page**: Immediately (<5 minutes)
- **Team**: Full incident response team
- **Updates**: Every 30 minutes
- **Escalation**: Auto-escalate to leadership
- **Communication**: Public status page, customer emails

**SLA**: Restore service within 1-2 hours

### P1 - High (SEV-2)

**Definition**: Major feature broken, significant user impact

**Examples**:
- Login system down
- Critical feature unavailable
- Severe performance degradation (>5s response times)
- Partial data loss
- Security vulnerability actively exploited

**Response**:
- **Page**: Within 15 minutes
- **Team**: Incident response team
- **Updates**: Every hour
- **Escalation**: Notify management
- **Communication**: Status page updates

**SLA**: Resolve within 4-8 hours

### P2 - Medium (SEV-3)

**Definition**: Degraded service, limited user impact

**Examples**:
- Non-critical feature broken
- Minor performance issues
- Intermittent errors (<1% requests)
- Workaround available
- Single region affected

**Response**:
- **Page**: Within 1 hour (or next business day)
- **Team**: On-call engineer
- **Updates**: Daily
- **Escalation**: As needed
- **Communication**: Internal only (unless prolonged)

**SLA**: Resolve within 1-2 days

### P3 - Low (SEV-4)

**Definition**: Minor issue, minimal impact

**Examples**:
- Cosmetic UI issues
- Documentation errors
- Low-impact bugs
- Feature requests
- Performance optimization opportunities

**Response**:
- **Page**: Next business day
- **Team**: Regular workflow
- **Updates**: When resolved
- **Escalation**: Not required
- **Communication**: Internal ticket

**SLA**: Resolve within 1 week

---

## 🔄 Incident Response Process

### Phase 1: Detection

**How incidents are detected**:
1. **Automated Monitoring**: Alerts from monitoring tools
2. **Customer Reports**: Support tickets, social media
3. **Internal Discovery**: Team members notice issues

**Immediate Actions**:
```markdown
1. Acknowledge alert (stops paging others)
2. Create incident in tracking system
3. Join incident channel (e.g., #incident-12345)
4. Start incident timeline
```

**Example Slack Message**:
```
🚨 INCIDENT DETECTED: P0 - API Completely Down
Incident ID: INC-2025-001
Started: 2025-11-19 14:30 UTC
Incident Channel: #incident-2025-001
Status: INVESTIGATING
```

### Phase 2: Assessment

**Determine severity**:
```markdown
Ask these questions:
- How many users affected?
- What functionality is broken?
- Is data at risk?
- Is there a security impact?
- What's the business impact?

Then assign severity (P0-P3)
```

**Gather initial information**:
```bash
# Check system health
curl https://api.example.com/health

# Check error rates
datadog-query "error_rate{service:api}" --last 1h

# Check recent deployments
kubectl rollout history deployment/api

# Check logs
kubectl logs -l app=api --tail=100
```

### Phase 3: Response

**Assemble the team**:

**Incident Commander (IC)**:
- Coordinates response
- Makes decisions
- Communicates status
- Usually: On-call engineer or senior engineer

**Technical Lead (TL)**:
- Investigates root cause
- Proposes solutions
- Implements fixes
- Usually: Domain expert

**Communications Lead (CL)**:
- Updates status page
- Notifies customers
- Communicates internally
- Usually: Product manager or support lead

**For P0/P1**: All roles filled
**For P2/P3**: IC might handle all roles

**War Room**:
```markdown
Physical: Conference room (if co-located)
Virtual: Zoom/Meet call + Slack channel

Rules:
- Stay focused on resolution
- One voice (IC) makes decisions
- All updates in incident channel
- Side conversations in threads
```

### Phase 4: Mitigation

**Goal**: Stop the bleeding (not necessarily fix root cause)

**Mitigation strategies**:

1. **Rollback**
```bash
# Rollback deployment
kubectl rollout undo deployment/api

# Verify rollback
kubectl rollout status deployment/api

# Test service
curl https://api.example.com/health
```

2. **Disable Feature**
```bash
# Toggle feature flag
curl -X POST https://feature-flags/api/disable \
  -d '{"feature": "new-checkout"}'
```

3. **Scale Resources**
```bash
# Increase pods
kubectl scale deployment/api --replicas=20

# Increase database connections
# (Update config, redeploy)
```

4. **Redirect Traffic**
```bash
# Switch to backup region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123 \
  --change-batch file://failover.json
```

5. **Rate Limiting**
```bash
# Enable stricter rate limits
redis-cli SET rate_limit:global 100 # Requests per minute
```

**Verify mitigation**:
```markdown
✅ Error rate decreased?
✅ Service responding?
✅ Customers can use the system?
```

### Phase 5: Communication

**Internal Communication** (in incident channel):
```markdown
Every 30 minutes for P0, hourly for P1:

🚨 INCIDENT UPDATE [14:45 UTC]
Status: INVESTIGATING
Impact: API completely down, all users affected
Actions Taken: Rolled back deployment v2.1.5 to v2.1.4
Current Status: Rollback complete, testing in progress
Next Update: 15:15 UTC
IC: @alice
```

**External Communication** (status page):
```markdown
🟥 Major Outage - API Services

We are currently experiencing a major outage affecting our API services.
All users are unable to access the platform.

Our engineering team is actively working on a resolution.
We will provide updates every 30 minutes.

Started: Nov 19, 2025 14:30 UTC
Next Update: Nov 19, 2025 15:00 UTC
```

**Escalation Communication** (to leadership):
```markdown
To: Engineering Director, CTO
Subject: [P0 INCIDENT] API Complete Outage

Critical incident in progress:
- Severity: P0
- Impact: All users unable to access platform
- Start Time: 14:30 UTC (15 minutes ago)
- Current Status: Investigating, rollback in progress
- Estimated Resolution: 30-60 minutes
- Incident Channel: #incident-2025-001
- Incident Commander: Alice Johnson

Will update every 30 minutes.
```

### Phase 6: Resolution

**Fix root cause**:
```markdown
Once service is mitigated:
1. Continue investigation (don't rush fix)
2. Identify root cause
3. Develop proper fix
4. Test fix thoroughly
5. Deploy fix (carefully, with monitoring)
6. Verify issue resolved
```

**Example**:
```markdown
Root Cause Found:
Database connection pool exhausted due to connection leak in new code.

Fix:
1. Increase connection pool size (immediate)
2. Fix connection leak in code (proper fix)
3. Add monitoring for connection pool usage (prevention)

Deployment Plan:
1. Deploy connection pool increase to production
2. Monitor for 30 minutes
3. If stable, deploy code fix to staging
4. Test on staging for 2 hours
5. Deploy to production with canary rollout
```

### Phase 7: Recovery

**Verify service fully restored**:
```bash
# Check all health endpoints
./scripts/check-health.sh

# Verify metrics
- Error rate: < 0.1% ✅
- Response time: < 200ms ✅
- Throughput: Normal ✅
- Database connections: Healthy ✅

# Spot check critical flows
- User login ✅
- Checkout ✅
- API access ✅
```

**Close incident**:
```markdown
🟢 INCIDENT RESOLVED [16:30 UTC]
Incident ID: INC-2025-001
Duration: 2 hours
Root Cause: Database connection pool exhaustion
Resolution: Increased pool size + fixed connection leak
Post-Mortem: Will be published within 48 hours

Thank you to the team:
@alice (IC), @bob (TL), @carol (CL)
```

### Phase 8: Learning (Post-Mortem)

**Blameless post-mortem** (within 48 hours):

**Template**:
```markdown
# Post-Mortem: API Outage (Nov 19, 2025)

## Incident Summary
- **Date**: November 19, 2025
- **Duration**: 2 hours (14:30-16:30 UTC)
- **Severity**: P0
- **Impact**: 100% of users unable to access platform
- **Root Cause**: Database connection pool exhaustion
- **Revenue Impact**: $50,000 estimated

## Timeline
14:30 - Alert triggered: API 500 errors > 50%
14:32 - On-call engineer acknowledged
14:35 - Incident declared (P0)
14:40 - Team assembled in war room
14:45 - Rollback initiated to v2.1.4
15:00 - Rollback complete, service partially restored
15:15 - Root cause identified: connection leak
15:30 - Emergency fix deployed: increased pool size
15:45 - Proper fix deployed: fixed leak in code
16:00 - Monitoring shows healthy metrics
16:30 - Incident resolved

## Root Cause
New feature in v2.1.5 introduced database connection leak.
Under high load, connection pool exhausted, causing all requests to fail.

Specific code:
```typescript
// BAD: Connection never released
async function getUser(id) {
  const conn = await pool.getConnection();
  const user = await conn.query('SELECT * FROM users WHERE id = ?', [id]);
  return user; // Forgot to release connection!
}

// GOOD: Connection properly released
async function getUser(id) {
  const conn = await pool.getConnection();
  try {
    const user = await conn.query('SELECT * FROM users WHERE id = ?', [id]);
    return user;
  } finally {
    conn.release(); // Always release!
  }
}
```

## Contributing Factors
1. Code review didn't catch connection leak
2. Integration tests didn't cover high-load scenario
3. Staging environment has smaller connection pool (didn't surface issue)
4. No monitoring on connection pool usage

## What Went Well
✅ Alert fired immediately (< 2 minutes)
✅ Team responded quickly
✅ Rollback was smooth and restored partial service
✅ Communication was clear and frequent
✅ Root cause identified within 30 minutes

## What Went Wrong
❌ Issue not caught in code review
❌ Tests didn't cover this scenario
❌ Staging environment not representative
❌ No connection pool monitoring
❌ Deployment didn't use canary strategy

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add connection pool monitoring | @bob | Nov 21 | ✅ Done |
| Update code review checklist (resource cleanup) | @alice | Nov 22 | ✅ Done |
| Add load testing to CI/CD | @carol | Dec 1 | 🔄 In Progress |
| Match staging DB pool size to production | @dave | Nov 23 | ✅ Done |
| Implement canary deployments | @eve | Dec 15 | 📝 Planned |
| Add circuit breaker for DB connections | @frank | Dec 10 | 📝 Planned |

## Lessons Learned
1. **Resource cleanup is critical**: Always use try/finally or defer
2. **Test under load**: Integration tests should include load scenarios
3. **Staging parity**: Staging should mirror production configuration
4. **Monitor everything**: Connection pools, thread pools, all resources
5. **Canary deployments**: Would have caught this affecting 5%, not 100%
```

---

## 📊 Incident Metrics

### Track These Metrics

```yaml
Incident Frequency:
  Track: Number of incidents per month by severity
  Target: Decreasing trend

Mean Time to Detect (MTTD):
  Track: Time from start to detection
  Target: < 5 minutes
  Ideal: < 1 minute (automated monitoring)

Mean Time to Acknowledge (MTTA):
  Track: Time from detection to response
  Target: < 5 minutes (P0), < 15 minutes (P1)

Mean Time to Mitigate (MTTM):
  Track: Time from detection to service restored
  Target: < 1 hour (P0), < 4 hours (P1)

Mean Time to Resolve (MTTR):
  Track: Time from detection to permanent fix
  Target: < 4 hours (P0), < 24 hours (P1)

Customer Impact:
  Track: Users affected, revenue lost
  Target: Decreasing trend

Action Item Completion:
  Track: % of post-mortem action items completed
  Target: 100% within due date
```

---

## 🛠️ Incident Response Tools

### Required Tools

```markdown
Monitoring & Alerting:
- Datadog / New Relic (APM)
- PagerDuty / Opsgenie (on-call)
- Prometheus + Grafana (metrics)
- Sentry (error tracking)

Communication:
- Slack (incident channels)
- Zoom / Google Meet (war room)
- StatusPage.io (customer updates)
- Email / SMS (escalations)

Incident Management:
- Jira / Linear (tracking)
- Google Docs (post-mortems)
- Incident.io / FireHydrant (orchestration)

Access & Tooling:
- VPN (secure access)
- kubectl / aws cli (operations)
- Database clients
- Log aggregation (ELK, Splunk)
```

### Runbooks

**Create runbooks for common scenarios**:
```markdown
Runbooks:
- Database connection issues
- High API latency
- Service crashes / restarts
- Memory leaks
- Cache invalidation
- CDN issues
- DNS problems
- Certificate expiration
- Deployment rollback
- Database migration issues
```

**Runbook template**:
```markdown
# Runbook: High API Latency

## Symptoms
- API response time > 1 second
- Alert: "High API Latency"
- Dashboard: https://datadog/api-latency

## Common Causes
1. Database slow queries
2. Downstream service degradation
3. High traffic / DDoS
4. Memory leaks
5. Resource exhaustion

## Diagnostic Steps
1. Check current latency: [dashboard link]
2. Check error rate: [dashboard link]
3. Check database performance: [query]
4. Check downstream services: [status page]
5. Check resource usage: [metrics]

## Resolution Steps

### If Database Slow Queries:
1. Identify slow queries: [query]
2. Check if indexes are used: EXPLAIN query
3. Add missing indexes if needed
4. Consider query optimization

### If Downstream Service Down:
1. Enable circuit breaker
2. Use cached responses
3. Contact downstream team

### If High Traffic:
1. Check if legitimate or attack
2. Enable rate limiting if attack
3. Scale up if legitimate
4. Contact security team if DDoS

### If Memory Leak:
1. Restart affected pods
2. Monitor memory usage
3. Investigate leak (heap dump)
4. Deploy fix

## Escalation
If not resolved in 30 minutes, escalate to:
- Primary: @backend-team
- Secondary: @platform-team
```

---

## 🎓 Best Practices

### Do's ✅

1. **Stay Calm**: Clear thinking is critical
2. **Communicate Frequently**: Over-communicate during incidents
3. **Document Everything**: Timeline, actions, decisions
4. **Focus on Mitigation First**: Stop the bleeding
5. **Blameless Culture**: Focus on systems, not people
6. **Write Post-Mortems**: Learn from every incident
7. **Complete Action Items**: Follow through on improvements
8. **Practice**: Regular incident drills / game days
9. **Update Runbooks**: After every incident
10. **Automate Recovery**: Where possible

### Don'ts ❌

1. **Don't Panic**: Panic leads to mistakes
2. **Don't Blame People**: Systems fail, not people
3. **Don't Skip Post-Mortems**: They prevent recurrence
4. **Don't Rush Fixes**: Hasty fixes cause new incidents
5. **Don't Ignore Metrics**: Data guides decisions
6. **Don't Work Alone**: Collaborate, don't hero
7. **Don't Forget Customers**: Communicate status
8. **Don't Repeat Incidents**: Implement action items
9. **Don't Burn Out On-Call**: Rotate, support team
10. **Don't Skip Drills**: Practice makes perfect

---

## 🔗 Related Resources

- [CI/CD Playbook](../cicd/ci-cd-playbook.md)
- [Deployment Playbook](../deployment/deployment-playbook.md)
- [On-Call Handbook](../onboarding/on-call-handbook.md)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: SRE Team
**Based On**: Google SRE Book, Incident Management for Operations
