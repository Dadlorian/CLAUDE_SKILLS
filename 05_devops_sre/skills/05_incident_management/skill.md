# Incident Management - Elite Professional Practices

**Structured response, mitigation, and organizational learning from production incidents**

---

## Overview

Incident Management is the process of responding to unplanned interruptions or reductions in quality of IT services. It encompasses detection, response, mitigation, recovery, and post-incident learning. This covers practices from Google SRE, PagerDuty, Facebook, Amazon, and other organizations managing massive-scale infrastructure.

You are an expert in designing incident management processes that minimize impact to customers, enable rapid response, reduce mean time to recovery (MTTR), and systematically improve system reliability through blameless analysis.

## Core Principles

### 1. Rapid Detection and Alerting

**Automated Detection**:
- Monitoring systems detect anomalies and failures
- Alerts sent immediately to on-call engineers
- Escalation policies ensure coverage

```yaml
# Alert configuration example
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 1%"
    duration: "5 minutes"
    severity: "critical"
    route: "on_call_primary"

  - name: "Database Connection Pool Exhaustion"
    condition: "active_connections > 90% of pool"
    duration: "2 minutes"
    severity: "critical"
    route: "on_call_primary"

  - name: "API Latency"
    condition: "p95_latency > 500ms"
    duration: "10 minutes"
    severity: "warning"
    route: "on_call_secondary"
```

**Detection Tools**:
- Prometheus/Grafana for metrics-based alerts
- Splunk/ELK for log-based alerts
- Synthetic monitoring for synthetic transactions
- User impact monitoring for real user experience

### 2. Incident Severity Levels

Clear severity classification guides response and communication:

```
SEVERITY 1 (Critical):
- Complete service outage or major functionality unavailable
- Affects all or most customers
- Revenue impact
- Response: Page on-call immediately, all hands on deck
- Communication: Update status page every 10 minutes

SEVERITY 2 (Major):
- Significant functionality degraded or some customers affected
- Limited business impact
- Response: Page on-call, dedicated responders
- Communication: Update status page every 15 minutes

SEVERITY 3 (Minor):
- Minor functionality affected, workaround available
- Limited customer impact
- Response: Investigate within SLO, may not need immediate page
- Communication: Email notification, update status page

SEVERITY 4 (Informational):
- No customer impact, infrastructure issue detected
- Proactive fix before impact
- Response: Ticket in queue, fixed during regular work
- Communication: Internal notification only
```

### 3. Incident Roles and Responsibilities

**Incident Commander (IC)**:
- Overall incident lead and decision maker
- Coordinates all response efforts
- Responsible for escalation and keeping stakeholders informed
- Final authority on mitigation decisions

```yaml
# Incident Commander Responsibilities
- Set incident severity
- Establish war room and communication channels
- Coordinate different teams (backend, frontend, database, etc.)
- Make go/no-go decisions for mitigation steps
- Authorize rollbacks, restarts, traffic shifts
- Keep executives informed of status
- Decide when incident is resolved
- Ensure post-mortem is scheduled
```

**Technical Lead**:
- Directs technical investigation and mitigation
- Root cause analysis
- Validates fixes before deployment
- Works with IC on mitigation strategies

**Communications Lead**:
- Updates status page regularly
- Communicates with customers via email/tweets
- Manages internal escalations and stakeholder updates
- Translates technical details for non-technical audiences

**Scribe**:
- Documents timeline of events
- Records actions taken and decisions made
- Captures root cause discussion
- Creates post-mortem document

## Incident Response Process

### Detection and Triage (Ideal: < 5 minutes)

```
1. Alert fires (automated detection)
   ↓
2. Engineer notified via PagerDuty/Opsgenie
   ↓
3. Engineer acks alert and opens incident channel (Slack, Teams)
   ↓
4. Engineer performs initial triage:
   - Verify incident is real (not alert misconfiguration)
   - Set severity level
   - Identify affected systems/customers
   - Estimate scope and impact
   ↓
5. If critical/major: Page Incident Commander
```

**Triage Checklist**:
- [ ] Service actually down/degraded (not false alarm)
- [ ] Severity correctly classified
- [ ] Appropriate people paged
- [ ] War room created and communication channels established
- [ ] Initial status update posted

### Response and Mitigation (Varies: minutes to hours)

```
1. IC calls war room, sets objectives
   "We have a database connection pool exhaustion issue
    affecting checkout. Timeline says degradation started 5 min ago.
    Goal: Restore checkout service. Everyone introduce yourselves."

2. Parallel investigation and mitigation
   - Technical lead: "What changed in last 30 minutes?"
   - Database: "Checking for slow queries, locked tables"
   - Application: "Analyzing connection pool metrics"
   - Infrastructure: "Checking database server resources"

3. Update status page every 10 minutes
   "We are investigating elevated errors on checkout.
    Approximately 5% of transactions affected. ETA: 15 min"

4. Implement mitigation when identified
   Option 1: "Restart database connection pool" (risk: brief disruption)
   Option 2: "Scale up database read replicas" (slower but safer)
   Option 3: "Failover to backup database" (if available)

5. Validate fix
   - Monitor error rates, latency
   - Check customer-facing metrics
   - Ensure no cascading issues
```

### Recovery and Verification (Ideal: < 1 hour total)

```
1. Confirm incident resolved
   - Error rate back to normal
   - Latency normal
   - Transactions processing
   - Customer reports positive

2. Verify no secondary issues
   - Check backup systems
   - Monitor for anomalies
   - Run smoke tests

3. Update status page
   "Incident resolved. Checkout service fully restored.
    Monitoring for any remaining issues."

4. Plan post-mortem meeting
   "Post-mortem scheduled for tomorrow 2pm.
    Please attend if you were involved."
```

### Post-Incident Review (Within 48-72 hours)

**Blameless Post-Mortem**:
- Focus on systems and processes, not individuals
- "Why" investigation (root cause, not blame)
- Identify contributing factors
- Generate action items to prevent recurrence

```markdown
## Incident Post-Mortem Report

### Summary
On 2025-03-15 at 14:23 UTC, a database connection pool exhaustion
caused a 45-minute outage affecting checkout service.
Approximately 15,000 customers affected.

### Timeline
14:23 - Monitoring alert: high error rate on checkout
14:25 - Incident declared, IC paged
14:28 - Identified: connection pool exhausted (500/500 connections)
14:35 - Temporary mitigation: restarted application servers
14:45 - Permanent mitigation: deployed connection pool monitoring
15:08 - Service fully restored

### Root Cause
A code change in the previous deploy introduced a connection leak
in the cart service. Under high load (morning traffic spike),
connections exhausted within minutes.

### Contributing Factors
- No automated testing for connection pool leaks
- Monitoring didn't alert on connection pool utilization (only errors)
- Load test environment uses smaller pool, didn't catch issue
- No connection pool metrics exposed in CI/CD

### What Went Well
- Alert triggered quickly
- IC coordinated effectively across teams
- Engineering identified root cause in 12 minutes
- Rollback plan ready and executed smoothly

### What Could Be Better
- Earlier detection via connection pool monitoring
- Load test environment should match production
- Connection pool leak tests in CI/CD

### Action Items
1. [Engineering] Add connection pool metrics to monitoring (due: 3/20)
2. [QA] Add connection leak tests to test suite (due: 3/20)
3. [DevOps] Update load test environment to match production (due: 3/25)
4. [Engineering] Code review checklist: check for resource leaks (due: 3/15)
5. [On-Call] Schedule connection pool training (due: 3/18)
```

## On-Call Practices

### Sustainable On-Call Rotations

**Anti-patterns**:
- Single person on-call for extended periods
- On-call engineer expected to write code during shift
- No compensation or recovery time
- On-call duties in addition to regular job

**Best Practices**:

```
# Weekly rotation with escalation
Week 1: Engineer A (primary), Engineer B (secondary)
Week 2: Engineer C (primary), Engineer D (secondary)
Week 3: Engineer E (primary), Engineer F (secondary)
Week 4: Engineer A (primary), Engineer B (secondary)

# Clear escalation path
Primary page -> respond within 15 min
If no response after 5 min -> page secondary
If still no response -> page manager

# Coverage
- Weekday on-call: 9am-9pm local time
- Weekend on-call: 24 hours
- Holidays: shared coverage, extra compensation

# Recovery time
- If paged <2 hours after last sleep: given next day off
- If paged multiple times per night: next day off
- Burnout prevention over heroics
```

### On-Call Tools and Setup

```bash
# Local development setup for on-call engineer
- Code repository cloned and updated
- SSH keys configured for production access
- VPN configured and tested
- PagerDuty mobile app installed with notifications enabled
- Slack configured for incident channels
- Common runbooks and scripts in easy-to-access location
- Terminal colors and fonts optimized for night shifts
```

## Technology Stack

### PagerDuty

**Incident Management and On-Call Scheduling**

```
Features:
- Escalation policies (who to page if no response)
- Schedule management (rotations, on-call coverage)
- Incident timeline and audit trail
- Integration with monitoring and alerting systems
- Customizable incident workflows
- Analytics on incident response times
```

### OpsGenie (Atlassian)

**Lightweight Alternative to PagerDuty**

```
Features:
- On-call scheduling
- Escalation and notification rules
- Team management
- Analytics
- Jira integration
```

### Statuspage

**Public Status Communication**

```
Features:
- Public status page for customers
- Incident timeline and updates
- Component health status
- Scheduled maintenance announcements
- Customer notifications via email/SMS/Twitter
- Historical incident data
```

### Splunk / ELK Stack

**Log Analysis for Incident Investigation**

```
# Quick log analysis during incident
GET /logs?q=error +database +pool +exhausted
Shows: 1,200 errors starting at 14:23 UTC
Filters to: CartService container restarting

GET /logs?q=stack_trace +"connection"
Shows: "Could not get connection: resource exhausted"
```

## Metrics and KPIs

### MTTR (Mean Time To Recovery)

```
Calculation: (Detection Time + Response Time + Mitigation Time)

Goal for Severity 1: < 30 minutes
Goal for Severity 2: < 2 hours
Goal for Severity 3: < 8 hours

Example:
Detection: 14:23 (alert fired immediately)
Response: 14:25 (engineer acked alert)
Mitigation: 14:35 (fix deployed)
Resolution: 15:08 (confirmed recovered)

MTTR = 14:23 -> 15:08 = 45 minutes
```

### MTTF (Mean Time To Failure)

```
How often do critical incidents occur?

Elite teams: < 1 per month
Good teams: 2-3 per month
Average: weekly
Poor: daily

Tracked to identify trends and improvement areas
```

### Incident Response Metrics

```
- Alert-to-page time: How fast alerts reach on-call
- Page-to-response time: How fast engineer starts responding
- Response-to-mitigation time: How long to fix/mitigate
- MTTR: Total time from detection to recovery
- Incident frequency: How many incidents per month
- False alert rate: % of alerts that are not real incidents
```

## Common Incident Scenarios

### Database Performance Degradation

**Symptoms**: High query latency, timeout errors, connection pool issues

**Investigation**:
```sql
-- Check for long-running queries
SELECT pid, query, query_start, state
FROM pg_stat_activity
WHERE state != 'idle'
AND query_start < NOW() - INTERVAL '5 minutes';

-- Check for table locks
SELECT * FROM pg_locks
WHERE NOT granted;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

**Mitigation Options**:
1. Kill long-running query (brief disruption)
2. Restart database connection pool
3. Failover to read replica
4. Increase connection pool size
5. Scale database vertically/horizontally

### Memory/Resource Exhaustion

**Symptoms**: Out of memory errors, GC pauses, application crashes

**Investigation**:
```bash
# Check memory usage
free -h
# Check per-process memory
ps aux | sort -k +4 -nr | head -20

# Check disk usage
df -h
du -sh /* | sort -rh

# Check CPU usage
top -b -n 1
```

**Mitigation Options**:
1. Restart affected service/container
2. Scale up instance/pod resources
3. Enable autoscaling if under-provisioned
4. Identify memory leak and fix

### Dependency Failure (API, Database, Cache)

**Symptoms**: Timeout errors, degraded performance, cascading failures

**Investigation**:
```bash
# Test connectivity to dependency
curl -v https://api.dependency.com/health

# Check network connectivity
traceroute api.dependency.com
mtr api.dependency.com

# Check DNS resolution
nslookup api.dependency.com
dig api.dependency.com
```

**Mitigation Options**:
1. Enable circuit breaker (fail fast rather than timeout)
2. Activate fallback/degraded mode
3. Increase timeout/retry limits
4. Route around failed dependency if possible
5. Cache responses if available

## Best Practices

### 1. Incident Documentation

- Keep detailed timeline of events
- Document what was tried and results
- Record decisions and rationale
- Capture exact error messages and logs

### 2. Communication

- Transparent and frequent updates
- Avoid technical jargon for non-technical audiences
- Acknowledge customer impact
- Never blame external parties publicly

### 3. Blameless Culture

```
GOOD: "The alert didn't trigger because we weren't monitoring X"
BAD: "The engineer didn't notice the alert"

GOOD: "The code didn't have a test for this condition"
BAD: "The engineer wrote bad code"

GOOD: "Our deployment process didn't catch this regression"
BAD: "The engineer deployed broken code"
```

### 4. Runbooks and Playbooks

Pre-written procedures for common incidents:

```markdown
## Runbook: Database Connection Pool Exhaustion

1. Identify affected service
   - Check which service has exhausted pool
   - Check application logs for connection errors

2. Assess impact
   - How many requests affected
   - Are customers noticing impact
   - How many transactions queued

3. Immediate mitigation (pick one)
   Option A: Restart affected service
   Command: kubectl rollout restart deployment/checkout-api -n prod

   Option B: Increase pool size
   Command: kubectl set env deployment/checkout-api CONNECTION_POOL_SIZE=100

   Option C: Scale horizontally
   Command: kubectl scale deployment checkout-api --replicas=5 -n prod

4. Monitor and verify
   - Watch error rate drop
   - Confirm latency returns to normal
   - Check queue drains

5. Root cause investigation
   - Look for code change in last 24 hours
   - Check for new queries or connection usage
   - Review application logs for exceptions
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Google SRE, PagerDuty, Amazon, Facebook incident practices
