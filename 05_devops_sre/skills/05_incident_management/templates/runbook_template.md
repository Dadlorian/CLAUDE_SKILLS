# Runbook: [Service/Component Name] - [Issue Type]

**Service:** [Service name]
**Component:** [Specific component if applicable]
**Issue Type:** [e.g., High Error Rate, Performance Degradation, Service Unavailable]
**Typical Severity:** SEV-[X] (may vary based on impact)
**Owner:** @[team-name] / @[individual-name]
**Last Updated:** [YYYY-MM-DD]
**Last Tested:** [YYYY-MM-DD]
**Version:** [1.0]

---

## Quick Reference

**When to use this runbook:**
[One-line description of when this runbook applies]

**Expected time to resolve:** [X minutes to Y hours]

**Prerequisites:**
- Access: [What access is needed]
- Tools: [Required tools]
- Knowledge: [Required background knowledge]

**Emergency contacts:**
- Primary: @[name] ([contact-method])
- Secondary: @[name] ([contact-method])
- Escalation: @[team/person] ([contact-method])

---

## Overview

### Description

[2-3 paragraph description of this issue type]

**What is this issue?**
[Clear explanation of the problem]

**Why does it happen?**
[Common root causes]

**How does it manifest?**
[Symptoms and indicators]

### User Impact

**When this occurs, users experience:**
- [Impact 1]
- [Impact 2]
- [Impact 3]

**Typical business impact:**
[Revenue, SLA, reputation implications]

---

## Symptoms and Detection

### How This Issue Presents

**Alerts that may fire:**
- [Alert name 1]: [What it indicates]
- [Alert name 2]: [What it indicates]
- [Alert name 3]: [What it indicates]

**Dashboard indicators:**
- [Dashboard]: [Link] - Look for [specific metric/pattern]
- [Dashboard]: [Link] - Look for [specific metric/pattern]

**Log patterns:**
```
[Example log pattern to look for]
[Example error message]
```

**Metrics to check:**
- [Metric name]: Normal range [X-Y], alert threshold [Z]
- [Metric name]: Normal range [X-Y], alert threshold [Z]

**User-visible symptoms:**
- [What users see/experience]
- [Error messages or behavior]

---

## Immediate Actions

**Time-sensitive first steps to take immediately upon detection.**

### Step 1: Verify the Issue

**Confirm this is actually happening:**

```bash
# Check service health
[command to check service status]

# Check error rates
[command or dashboard link]

# Check recent deployments
[command to check deployment history]
```

**Expected output:**
```
[What you should see if issue is confirmed]
```

**If output shows [X]:** This is confirmed, proceed to Step 2
**If output shows [Y]:** This may be a false positive, investigate [alternative]

### Step 2: Assess Impact

**Determine severity and scope:**

```bash
# Check how many instances/users affected
[command]

# Check geographic distribution if relevant
[command]

# Check duration
[command or dashboard]
```

**Severity decision tree:**
- If [condition]: SEV-1 - Declare incident immediately
- If [condition]: SEV-2 - Declare incident
- If [condition]: SEV-3 - Create ticket, investigate

**See:** reference/incident_severity_levels.md

### Step 3: Immediate Mitigation (if applicable)

**Safe, quick actions to reduce impact:**

**Option A: [Mitigation name]**
```bash
# [Description of what this does]
[command 1]
[command 2]

# Verify mitigation
[verification command]
```

**When to use:** [Circumstances]
**Risk:** [Low/Medium/High] - [Why]
**Rollback:** [How to undo if needed]

**Option B: [Alternative mitigation]**
```bash
[commands]
```

**When to use:** [Circumstances]
**Risk:** [Low/Medium/High] - [Why]
**Rollback:** [How to undo if needed]

### Step 4: Notify and Escalate

**For SEV-1/SEV-2:** Declare incident
```
See: templates/incident_declaration_template.md
```

**Who to notify:**
- [Role/Person]: [When/Why]
- [Role/Person]: [When/Why]

**Escalation criteria:**
- Escalate to [person/team] if [condition]
- Escalate to [person/team] if [condition]

---

## Investigation

**Systematic approach to identifying root cause.**

### Common Causes (Check in this order)

#### 1. Recent Deployments

**Check for recent code/config changes:**

```bash
# List recent deployments
[command to check deployment history]

# Check specific deployment details
[command to see what changed]
```

**If deployment is suspected:**
→ Go to "Rollback Procedure" section below

**Look for:**
- Deployments in last [X hours]
- Configuration changes
- Database migrations
- Infrastructure changes

#### 2. Resource Exhaustion

**Check system resources:**

```bash
# Check CPU utilization
[command]

# Check memory usage
[command]

# Check disk space
[command]

# Check network connections
[command]

# Check database connections
[command]
```

**Normal ranges:**
- CPU: [X-Y%]
- Memory: [X-Y%]
- Disk: [X-Y%]
- Connections: [X-Y]

**If resources are exhausted:**
→ Go to "Resource Scaling Procedure" section

#### 3. External Dependencies

**Check third-party services:**

```bash
# Check [dependency name] status
curl [status page URL]

# Check API response times
[command]

# Check error rates from dependencies
[command or dashboard]
```

**Known dependencies:**
- [Dependency 1]: [Status page link] | [Fallback if down]
- [Dependency 2]: [Status page link] | [Fallback if down]

**If dependency is down:**
→ Go to "Dependency Failure Procedure" section

#### 4. Database Issues

**Check database health:**

```bash
# Check database connections
[command]

# Check for slow queries
[command]

# Check for locks
[command]

# Check replication lag
[command]
```

**If database issues found:**
→ Escalate to DBA team OR go to "Database Recovery" section

#### 5. Traffic Patterns

**Check for unusual traffic:**

```bash
# Check current request rate
[command or dashboard]

# Compare to baseline
[command or dashboard]

# Check for specific high-volume endpoints
[command]

# Check for potential DDoS
[command or dashboard]
```

**Normal traffic:** [X requests/second]
**Peak traffic:** [Y requests/second]

**If traffic spike detected:**
→ Go to "Traffic Management Procedure" section

### Investigation Tools and Resources

**Dashboards:**
- Service Overview: [Link]
- Performance Metrics: [Link]
- Error Tracking: [Link]
- Infrastructure: [Link]

**Log Sources:**
```bash
# Application logs
[command or link]

# System logs
[command or link]

# Access logs
[command or link]
```

**Tracing:**
- Distributed tracing: [Link to tool]
- Example trace query: [query]

**Database:**
- Query analytics: [Link or command]
- Slow query log: [Command]

---

## Mitigation Procedures

### Rollback Procedure

**When:** Recent deployment suspected as cause
**Time to execute:** [X minutes]
**Risk:** Low (if rollback is tested)

**Prerequisites:**
- Identify target rollback version
- Verify rollback version is stable
- Get IC approval (for production)

**Steps:**

```bash
# 1. Identify current version
[command to check current version]

# 2. Identify rollback target (usually previous version)
[command to find previous stable version]

# 3. Execute rollback
[command to rollback]
# Example:
# kubectl rollout undo deployment/[service-name] -n [namespace]

# 4. Monitor rollback progress
[command to monitor]

# 5. Verify rollback success
[verification commands]

# 6. Check error rates return to normal
[dashboard link or command]
```

**Expected duration:** [X minutes]

**Verification:**
- Error rate returns to <[threshold]
- [Metric] returns to normal range
- No new errors in logs

**If rollback doesn't resolve:** Issue was not deployment-related, investigate other causes

### Service Restart Procedure

**When:** Suspected memory leak, stuck processes, connection issues
**Time to execute:** [X minutes]
**Risk:** Medium (brief service disruption)

**Prerequisites:**
- Understand current traffic levels
- Get IC approval for production restart
- Have rollback plan if restart fails

**Steps:**

**Option A: Rolling Restart (Preferred - zero downtime)**

```bash
# 1. Restart instances one at a time
[command to restart single instance]

# 2. Wait for instance to be healthy
[command to check health]

# 3. Verify traffic is serving correctly
[command or dashboard]

# 4. Repeat for each instance
[loop or script]

# 5. Verify all instances healthy
[verification command]
```

**Option B: Full Restart (if rolling restart not possible)**

```bash
# WARNING: This will cause brief downtime

# 1. Put service in maintenance mode (if applicable)
[command]

# 2. Stop service
[command]

# 3. Verify service stopped
[command]

# 4. Start service
[command]

# 5. Verify service started and healthy
[command]

# 6. Remove maintenance mode
[command]

# 7. Monitor error rates
[dashboard or command]
```

**Verification:**
- All instances showing healthy
- Error rates normal
- Response times normal
- No crash loops in logs

### Traffic Shift / Failover Procedure

**When:** Regional outage, specific cluster issues, need to shift load
**Time to execute:** [X-Y minutes]
**Risk:** Medium (dependent on failover readiness)

**Prerequisites:**
- Verify target region/cluster has capacity
- Understand traffic distribution
- Get IC approval

**Steps:**

```bash
# 1. Check target region/cluster health
[command]

# 2. Verify capacity in target
[command to check capacity]

# 3. Gradually shift traffic (e.g., 10%, 50%, 100%)
[command to shift traffic percentage]

# 4. Monitor target region for issues
[dashboard or command]

# 5. If successful, complete traffic shift
[command]

# 6. If issues in target, rollback traffic shift
[command to rollback]

# 7. Monitor both regions
[dashboard links]
```

**Verification:**
- Traffic successfully shifted
- Target region handling load
- Error rates normal in target
- Source region traffic dropped as expected

### Rate Limiting / Throttling Procedure

**When:** Traffic spike, resource exhaustion, need to protect service
**Time to execute:** [X minutes]
**Risk:** Low (controlled degradation)

**Prerequisites:**
- Understand current rate limits
- Determine appropriate new limits
- Get IC approval

**Steps:**

```bash
# 1. Check current rate limits
[command or config file]

# 2. Determine new limits based on capacity
# Current capacity: [X req/sec]
# Proposed limit: [Y req/sec]

# 3. Apply rate limiting
[command to apply rate limit]

# 4. Monitor error rates and throttled requests
[dashboard or command]

# 5. Adjust limits as needed
[command to adjust]

# 6. Document limits applied for later removal
[where to document]
```

**Verification:**
- Rate limits applied
- Service stability improved
- Throttled requests logged
- Monitor for impact on critical users

### Feature Flag Disable Procedure

**When:** New feature causing issues
**Time to execute:** [Seconds to minutes]
**Risk:** Low (controlled fallback)

**Steps:**

```bash
# 1. Identify problematic feature flag
[dashboard or config]

# 2. Check current feature flag state
[command]

# 3. Disable feature flag
[command]
# Example:
# feature-flag disable [flag-name]

# 4. Verify flag disabled
[command]

# 5. Monitor for service recovery
[dashboard or command]

# 6. Notify product team
[communication channel]
```

**Verification:**
- Feature flag disabled
- Error rates return to normal
- Users no longer see feature
- No new errors related to feature

---

## Recovery and Verification

### Confirming Resolution

**Check these indicators to confirm issue is resolved:**

```bash
# 1. Error rates returned to baseline
[command or dashboard link]
# Expected: <[threshold]

# 2. Latency/performance normal
[command or dashboard link]
# Expected: p99 <[X]ms

# 3. All instances healthy
[command]
# Expected: [X/X] healthy

# 4. No relevant alerts firing
[command or dashboard]
# Expected: No active alerts

# 5. User reports decreased/stopped
[support ticket system or channel]
```

**Stabilization period:** Monitor for [X minutes] after apparent resolution

**If issue returns:**
- Mitigation was incomplete
- Different root cause
- Need deeper investigation

### Post-Resolution

**Immediate (within 1 hour):**
```
☐ Document what was done in incident timeline
☐ Update this runbook if new information learned
☐ File tickets for identified issues
☐ Brief team on what happened
```

**Follow-up (within 24 hours):**
```
☐ Review logs and metrics for additional insights
☐ Identify action items to prevent recurrence
☐ Update monitoring or alerting if gaps found
☐ Schedule post-mortem if SEV-1/SEV-2
```

---

## Prevention and Monitoring

### Preventing This Issue

**Proactive monitoring:**
- [Metric to monitor]: Alert if [condition]
- [Metric to monitor]: Alert if [condition]

**Best practices to avoid:**
- [Practice 1]
- [Practice 2]
- [Practice 3]

**Architecture improvements:**
- [Recommendation 1]
- [Recommendation 2]

**Process improvements:**
- [Recommendation 1]
- [Recommendation 2]

### Recommended Monitoring

**Critical metrics to monitor:**

| Metric | Normal Range | Warning Threshold | Critical Threshold | Alert Severity |
|--------|--------------|-------------------|-------------------|----------------|
| [Metric 1] | [X-Y] | [Z] | [A] | SEV-2 |
| [Metric 2] | [X-Y] | [Z] | [A] | SEV-1 |

**Recommended alerts:**
```
Alert: [Name]
Condition: [Metric] [operator] [threshold] for [duration]
Severity: SEV-[X]
Notification: [Who/what]
Runbook: [This runbook link]
```

---

## Related Information

### Related Runbooks

- [Runbook name]: [Link] - [When to use instead]
- [Runbook name]: [Link] - [When to use in addition]

### Architecture Documentation

- Service architecture: [Link]
- Data flow diagram: [Link]
- Dependency map: [Link]
- Capacity planning: [Link]

### Historical Incidents

**Previous incidents of this type:**
- [INC-YYYYMMDD-###]: [Brief description] - [Link to post-mortem]
- [INC-YYYYMMDD-###]: [Brief description] - [Link to post-mortem]

**Lessons learned:**
- [Key lesson 1]
- [Key lesson 2]

### Configuration and Code

**Relevant configuration files:**
- [File/path]: [Purpose]
- [File/path]: [Purpose]

**Relevant code:**
- [Component/path]: [What it does]
- [Component/path]: [What it does]

**Deployment process:**
- Deployment documentation: [Link]
- Rollback documentation: [Link]

---

## Runbook Maintenance

### Testing This Runbook

**This runbook should be tested:**
- Frequency: [Quarterly / After major changes]
- Method: [GameDay exercise / Production test]
- Last tested: [YYYY-MM-DD]
- Test results: [Pass/Fail and notes]

**To test this runbook:**
1. [Step to simulate the issue in test environment]
2. [Follow runbook steps]
3. [Verify resolution]
4. [Document any gaps or inaccuracies]

### Update History

| Date | Version | Updated By | Changes |
|------|---------|------------|---------|
| YYYY-MM-DD | 1.0 | @name | Initial creation |
| YYYY-MM-DD | 1.1 | @name | [Description of changes] |

### Review Schedule

**Owner:** @[person/team]
**Review frequency:** [Quarterly / Semi-annually]
**Next review:** [YYYY-MM-DD]

**Review checklist:**
```
☐ Commands still accurate
☐ Links still valid
☐ Thresholds still appropriate
☐ Contacts still current
☐ Incorporated learnings from recent incidents
☐ Tested within last [timeframe]
☐ Reflects current architecture
```

---

## Appendix

### Command Reference

**Quick command reference for copy-paste:**

```bash
# Service health check
[command]

# Check logs
[command]

# Restart service
[command]

# Check metrics
[command]

# Rollback deployment
[command]
```

### Access Requirements

**To execute this runbook, you need:**

**System access:**
- [System name]: [Type of access]
- [System name]: [Type of access]

**Tools required:**
- [Tool]: [Version/How to install]
- [Tool]: [Version/How to install]

**How to get access:**
- [System]: [Process to request access]

### Glossary

**Terms used in this runbook:**

- **[Term]:** [Definition]
- **[Term]:** [Definition]
- **[Acronym]:** [What it stands for and means]

---

## Feedback

**This runbook helped me:** [Feedback form or channel]
**This runbook needs improvement:** [Feedback form or channel]
**I found an error:** [How to report]

**Runbook template version:** 1.0
**Last template update:** November 2025

---

## Notes for Runbook Authors

**When creating a runbook:**

✅ **Do:**
- Be specific and detailed with commands
- Include expected outputs
- Explain why, not just what
- Test commands before publishing
- Include rollback procedures
- Link to relevant resources
- Keep it updated

❌ **Don't:**
- Assume knowledge or context
- Use vague language ("check the thing")
- Skip verification steps
- Forget to include prerequisites
- Leave out contact information
- Let it become outdated

**Good runbook practices:**
- Commands should be copy-pasteable
- Include full paths, not relative
- Show expected output
- Explain what to look for
- Provide decision trees
- Link to related runbooks
- Test regularly

**Remember:** Someone waking up at 3 AM to page should be able to follow this runbook successfully.
