# Incident Response Playbook

## Purpose

This playbook provides step-by-step guidance for responding to production incidents from initial detection through resolution and post-mortem. Use this as your reference during high-stress situations.

---

## Quick Reference Card

**In an emergency, remember:**
1. Acknowledge the alert (stop the paging)
2. Assess severity and impact
3. Get help if needed (escalate early)
4. Communicate status regularly
5. Mitigate first, investigate later
6. Document as you go

**Key Contacts:** [Link to your on-call rotation tool]

**Communication Channel:** [Your incident Slack channel or tool]

---

## Phase 1: Detection and Initial Response

### Step 1: Alert Acknowledgment (0-5 minutes)

**When you receive an alert:**

```
☐ Acknowledge the alert in your paging system
☐ Note the time you were paged
☐ Check alert message for:
   - What is alerting
   - Severity/priority
   - Affected service/component
   - Initial symptoms
   - Link to runbook (if provided)
   - Link to dashboard
```

**If alert is unclear:**
- Acknowledge anyway to stop paging
- Investigate to understand the issue
- Escalate if you can't determine the problem

**Acknowledgment means:**
- You've seen the alert
- You're beginning investigation
- NOT that you've fixed it

### Step 2: Initial Assessment (5-15 minutes)

**Triage checklist:**

```
☐ Is this a real issue or false positive?
☐ Are users affected right now?
☐ How many users are affected?
☐ What functionality is impacted?
☐ Is the impact growing or stable?
☐ Is there a known runbook for this issue?
```

**Check these sources:**

1. **Monitoring Dashboards**
   - Service health overview
   - Error rates and latency
   - Traffic patterns
   - Resource utilization

2. **Recent Changes**
   - Deployments in last 1-4 hours
   - Configuration changes
   - Infrastructure changes
   - Dependency updates

3. **User Reports**
   - Customer support tickets
   - Social media mentions
   - Direct reports

4. **System Logs**
   - Application logs
   - Error patterns
   - Stack traces
   - Correlation IDs

**Quick Impact Assessment:**

| Indicator | High Impact | Medium Impact | Low Impact |
|-----------|-------------|---------------|------------|
| Users affected | All/Most | Many | Some/Few |
| Error rate | >50% | 10-50% | <10% |
| Core functionality | Down | Degraded | Minor issues |
| Revenue impact | Direct loss | Potential loss | Minimal |

### Step 3: Severity Classification (Minutes 10-15)

**Determine initial severity using the severity matrix:**

**SEV-1 Indicators:**
- Complete service outage
- Data loss/corruption in progress
- Security breach active
- All users unable to use core features

**SEV-2 Indicators:**
- Significant degradation
- Major features unavailable
- Subset of users severely impacted
- Workaround exists but difficult

**SEV-3 Indicators:**
- Minor degradation
- Non-critical features affected
- Easy workaround available
- Limited user impact

**See:** reference/incident_severity_levels.md for detailed definitions

**Action:** Mentally assign severity (formal declaration comes next)

---

## Phase 2: Incident Declaration and Team Assembly

### Step 4: Declare the Incident (Minutes 15-20)

**For SEV-1 and SEV-2 incidents, formally declare:**

**Declaration checklist:**
```
☐ Create incident in incident management system
☐ Set severity level
☐ Create dedicated incident Slack channel (e.g., #incident-2025-11-19-api-outage)
☐ Post initial status:
   "INCIDENT DECLARED - SEV-[X]
   Service: [name]
   Issue: [brief description]
   Impact: [user impact]
   IC: [your name]
   Status: Investigating"
```

**Use incident declaration template:**
See: templates/incident_declaration_template.md

**For SEV-3/SEV-4:**
- May not require formal declaration
- Create ticket and investigate normally
- Escalate to incident if severity increases

### Step 5: Assemble Response Team (Minutes 15-25)

**For SEV-1 incidents:**

```
☐ Incident Commander: You (or escalate if needed)
☐ Communications Lead: Page on-call comms person or designate someone
☐ Technical Lead: You (if you're technical) or page subject matter expert
☐ Scribe: Designate someone to maintain timeline
☐ Executive Sponsor: Notify leadership (automated for SEV-1)
```

**Page additional help via:**
- Incident management tool escalation
- Direct Slack/phone contact
- Team-specific on-call rotations

**Announce team in incident channel:**
```
"INCIDENT TEAM ASSIGNED:
IC: @alice
Comms Lead: @bob
Tech Lead: @charlie
Scribe: @dana
SME - Database: @eve (joining)"
```

**For SEV-2 incidents:**

```
☐ Incident Commander: You or senior engineer
☐ Communications Lead: Designate from team
☐ Technical Lead: Primary investigator
☐ Scribe: Recommended but optional
```

**Role responsibilities:**
See: reference/incident_roles_reference.md

---

## Phase 3: Investigation and Mitigation

### Step 6: Establish Communication Rhythm (Minutes 20-30)

**IC sets update cadence:**

**SEV-1:**
- Status updates every 30-60 minutes
- Immediate updates for significant developments
- Executive briefings every 1-2 hours

**SEV-2:**
- Status updates every 2-4 hours
- Updates when major progress made

**IC to Comms Lead:**
"Please send status updates every [timeframe]. I'll provide you with status at [specific times]."

**Comms Lead starts customer communication:**
- See: templates/status_update_template.md
- First update within 15 min (SEV-1) or 30 min (SEV-2)

### Step 7: Systematic Investigation (Parallel with Mitigation)

**Investigation framework:**

**1. Form Hypothesis**
   - Based on symptoms and recent changes
   - Start with most likely causes
   - Document hypothesis

**2. Test Hypothesis**
   - Gather evidence (logs, metrics, traces)
   - Execute diagnostic commands
   - Check for confirming/disconfirming evidence

**3. Iterate**
   - If confirmed: Move to mitigation
   - If not: Form new hypothesis
   - Don't thrash - be systematic

**Common investigation paths:**

**Recent Deployment Issues:**
```
☐ Identify recent deployments (last 1-4 hours)
☐ Check deployment logs for errors
☐ Compare error timing to deployment timing
☐ Review changes in the deployment
☐ Consider rollback as mitigation
```

**Resource Exhaustion:**
```
☐ Check CPU, memory, disk, network utilization
☐ Identify resource trends
☐ Look for memory leaks or runaway processes
☐ Check for disk space issues
☐ Review connection pool exhaustion
```

**External Dependency Failure:**
```
☐ Check status pages of third-party services
☐ Review API response times and error rates
☐ Test direct connectivity to dependencies
☐ Check for timeout increases
☐ Review DNS resolution
```

**Database Issues:**
```
☐ Check database connection pool
☐ Review slow query logs
☐ Check for locks or blocking queries
☐ Review database resource utilization
☐ Check for replication lag
```

**Traffic Spike:**
```
☐ Review traffic patterns vs. normal
☐ Identify traffic sources
☐ Check for DDoS indicators
☐ Review auto-scaling behavior
☐ Check rate limiting effectiveness
```

**Investigation best practices:**
- Document commands and results (for Scribe)
- Share findings in incident channel
- Don't go silent - update IC regularly
- Ask for help if stuck

### Step 8: Implement Mitigation (Parallel with Investigation)

**Mitigation priority order:**

**1. Stop the Bleeding**
- Prevent further damage
- Stop data loss/corruption
- Contain security breach

**2. Restore Service**
- Get users back to working state
- Even if not perfect
- Workarounds are acceptable

**3. Investigate Root Cause**
- After service is restored
- During lower-stress period
- For permanent fix

**Common mitigation strategies:**

**Rollback:**
```
When: Recent deployment suspected
Risk: Low if rollback procedure is tested
Speed: Fast (minutes to 10s of minutes)
IC Approval: Required for production rollback
Execution:
☐ Verify rollback target version
☐ Confirm rollback procedure
☐ Get IC approval
☐ Execute rollback
☐ Monitor for recovery
☐ Confirm restoration
```

**Restart/Bounce:**
```
When: Memory leak, stuck processes, zombie connections
Risk: Medium (temporary unavailability during restart)
Speed: Fast (seconds to minutes)
IC Approval: Required if user-facing
Execution:
☐ Identify affected instances
☐ Plan rolling restart (avoid total outage)
☐ Get IC approval
☐ Execute restart
☐ Verify service recovery
```

**Traffic Shift/Failover:**
```
When: Regional issue, specific cluster problems
Risk: Medium (dependent on failover readiness)
Speed: Medium (minutes to hours)
IC Approval: Required
Execution:
☐ Identify healthy region/cluster
☐ Verify capacity in target
☐ Plan traffic shift (gradual vs. immediate)
☐ Get IC approval
☐ Execute traffic shift
☐ Monitor target for issues
```

**Rate Limiting/Throttling:**
```
When: Traffic spike, resource exhaustion
Risk: Low (controlled degradation)
Speed: Fast (minutes)
IC Approval: Required
Execution:
☐ Identify throttling points
☐ Determine appropriate limits
☐ Get IC approval
☐ Implement throttling
☐ Monitor error rates and recovery
```

**Configuration Change:**
```
When: Misconfiguration identified
Risk: Medium (config changes can cause issues)
Speed: Fast to medium
IC Approval: Required
Execution:
☐ Identify correct configuration
☐ Test in non-production (if time allows)
☐ Get IC approval
☐ Apply configuration
☐ Verify application
☐ Monitor for recovery
```

**Feature Flag Disable:**
```
When: New feature causing issues
Risk: Low (controlled fallback)
Speed: Very fast (seconds)
IC Approval: May be delegated to Tech Lead
Execution:
☐ Identify problematic feature flag
☐ Inform IC of plan
☐ Disable feature flag
☐ Monitor for recovery
☐ Notify product team
```

**Mitigation checklist:**
```
☐ Propose mitigation strategy to IC
☐ Get IC approval for risky changes
☐ Document mitigation plan
☐ Execute mitigation
☐ Monitor impact of mitigation
☐ Confirm mitigation effectiveness
☐ Report results to IC
```

---

## Phase 4: Stabilization and Monitoring

### Step 9: Confirm Recovery (Variable timing)

**Recovery verification:**

```
☐ Error rates returned to baseline
☐ Latency returned to normal
☐ User reports decreased
☐ All monitoring dashboards green/normal
☐ No new related alerts firing
☐ System resources at normal levels
```

**Monitor for:**
- Reoccurrence of issue
- Secondary failures
- Degraded performance
- Unusual patterns

**Stabilization period:**
- SEV-1: Monitor for 1-2 hours after mitigation
- SEV-2: Monitor for 30-60 minutes
- Don't declare resolved too quickly

**If issue returns:**
- Mitigation was incomplete or incorrect
- Re-assess and try different approach
- May need to escalate severity

### Step 10: Incident Resolution (When stable)

**IC declares incident resolved when:**

```
☐ Service fully restored
☐ User impact eliminated
☐ Stabilization period completed
☐ No ongoing risk of recurrence (short-term)
☐ Team agrees resolution is appropriate
```

**Resolution announcement:**

```
"INCIDENT RESOLVED - SEV-[X]
Time to resolution: [X hours Y minutes]
Root cause: [brief description or "TBD - under investigation"]
Mitigation: [what we did]
Next steps: Post-mortem scheduled for [date/time]
Thanks to: [acknowledge the team]"
```

**Comms Lead sends final update:**
- See: templates/status_update_template.md (Resolution section)
- Include resolution time
- Thank customers for patience
- Explain mitigation (high level)
- Commit to post-mortem (if applicable)

**Update incident management system:**
```
☐ Mark incident as resolved
☐ Record resolution time
☐ Add final notes
☐ Link to timeline/documentation
```

---

## Phase 5: Handoff and Transition

### Step 11: Shift Change Handoff (If incident spans shifts)

**Outgoing IC to incoming IC:**

```
☐ Current status of incident
☐ Active hypotheses being investigated
☐ Mitigation strategies attempted and results
☐ Team members involved and their roles
☐ Pending actions or decisions
☐ Communication status (what's been sent)
☐ Any blockers or escalations in progress
```

**Formal handoff:**
- Verbal briefing (5-10 minutes)
- Share timeline document
- Introduce new IC to team in incident channel
- Confirm new IC has all access and context

**Announcement in incident channel:**
```
"HANDOFF: @new-ic is now Incident Commander
@old-ic has briefed on current status
@new-ic confirmed ready to proceed"
```

### Step 12: Post-Resolution Follow-Up

**Immediate (same day):**
```
☐ Thank the response team
☐ Ensure timeline is complete and saved
☐ File placeholder tickets for obvious fixes
☐ Schedule post-mortem meeting (if required)
☐ Brief leadership if not already done
```

**Next day:**
```
☐ Review timeline for gaps
☐ Gather additional data for post-mortem
☐ Confirm post-mortem attendees
☐ Begin drafting post-mortem (if facilitator)
```

**Within a week:**
```
☐ Conduct post-mortem meeting
☐ Complete post-mortem document
☐ Create action items from post-mortem
☐ Share learnings with broader team
```

---

## Special Scenarios

### Scenario: Solo Response (Off-Hours, Small Team)

**When you're the only responder:**

1. **Acknowledge and assess** (same as normal)
2. **Decide: Escalate or handle?**
   - Escalate if: Outside expertise, SEV-1, need help
   - Handle if: SEV-2/3 within capability
3. **If handling solo:**
   - You are IC and Tech Lead
   - Self-document in incident channel
   - Set timer to update status regularly
   - Call for help if stuck >30 minutes
4. **After resolution:**
   - Write detailed timeline (you're Scribe too)
   - Ensure follow-up happens

### Scenario: Cascading Failures

**When multiple systems failing:**

1. **Don't panic - be systematic**
2. **Identify primary failure:**
   - What failed first?
   - What is causing subsequent failures?
3. **Prioritize mitigation:**
   - Stop cascade if possible
   - Address root cause first
   - May need to sacrifice non-critical systems
4. **Get help:**
   - Multiple Tech Leads for different systems
   - Escalate to senior leadership
   - Consider splitting into multiple incidents if unrelated
5. **Communication:**
   - Acknowledge complexity in updates
   - Set realistic expectations
   - More frequent updates due to changing situation

### Scenario: Security Incident

**Special considerations:**

1. **Containment first:**
   - Isolate compromised systems
   - Prevent further access
   - Preserve evidence
2. **Limited communication:**
   - Need-to-know basis initially
   - Coordinate with security team
   - Legal may need to be involved
3. **Evidence preservation:**
   - Don't destroy logs
   - Capture system state
   - Document attacker actions
4. **Follow security incident response plan:**
   - Your organization may have specific procedures
   - Security team may take IC role

### Scenario: Data Loss/Corruption

**Critical actions:**

1. **Stop the damage:**
   - Identify and stop data corruption process
   - Take systems offline if necessary
   - Prevent further writes to corrupted data
2. **Assess scope:**
   - How much data affected?
   - Which customers/users?
   - Time range of corruption
3. **Recovery strategy:**
   - Restore from backups (test first!)
   - Replay transactions if possible
   - Manual data recovery if needed
4. **Customer impact:**
   - May need individual customer outreach
   - Legal/compliance implications
   - Regulatory reporting requirements
5. **High-priority post-mortem:**
   - Data incidents require thorough analysis
   - Focus on prevention

---

## Communication Guidelines

### IC Communication with Team

**Effective IC Communication:**

✅ **Do:**
- Use clear, direct language
- Ask questions to confirm understanding
- Set explicit expectations and deadlines
- Acknowledge contributions
- Maintain calm, professional tone
- Make decisions when needed

❌ **Don't:**
- Micromanage technical details
- Make assumptions about progress
- Let silence linger (ask for updates)
- Get pulled into technical rabbit holes
- Blame or criticize during response

**Example IC statements:**
- "Charlie, what's your current hypothesis?"
- "Bob, please send a status update in the next 10 minutes"
- "I need an update from the database team in 15 minutes"
- "Good work isolating that issue, Eve"
- "We're going to roll back. Charlie, please execute."
- "I'm calling in the database SME for additional help"

### Status Update Guidelines

**Internal Updates (to team):**
- Current status
- Latest findings
- Actions being taken
- Blockers or needs
- Next update time

**Stakeholder Updates (to leadership):**
- Business impact
- User impact scope
- Mitigation strategy
- ETA (if available, otherwise next update time)
- What you need from them (if anything)

**Customer Updates (via Comms Lead):**
- See templates/status_update_template.md
- Focus on impact and progress
- Avoid technical jargon
- Be honest about uncertainty
- Provide realistic expectations

---

## Decision-Making Framework

### When to Escalate

**Escalate immediately if:**
- You don't have expertise to resolve
- You don't have access to fix the issue
- Issue severity exceeds your authority
- You're stuck and not making progress
- Multiple critical systems failing
- You need additional resources
- Issue has legal/compliance implications

**How to escalate:**
1. Use incident management tool escalation
2. Direct contact (phone/Slack) if urgent
3. Clearly state: What you need and why
4. Don't apologize for escalating (it's the right move)

### When to Roll Back vs. Forward

**Roll Back When:**
- Recent deployment is suspected cause
- Rollback procedure is tested and safe
- Need fast mitigation
- Investigation can happen post-rollback

**Push Forward When:**
- Rollback not possible (schema migration, etc.)
- Fix is simple and obvious
- Rollback would cause issues
- Already rolled back and issue persists

**IC decides based on:**
- Risk tolerance
- Time pressure
- Confidence in fix
- Rollback safety

### When to Implement Risky Mitigation

**High-risk changes during incidents:**
- Get IC approval always
- Consider if risk is worth it
- Have rollback plan for the mitigation
- Prefer less risky options if available

**IC approval checklist:**
```
"Proposing risky mitigation: [description]
Risk: [what could go wrong]
Benefit: [expected impact]
Rollback: [how to undo]
Alternatives: [other options considered]
Recommendation: [proceed or not]"
```

---

## Tools and Resources

### Essential Tools

**Incident Management:**
- PagerDuty, Opsgenie, VictorOps
- Create incidents, track timeline, manage communication

**Monitoring:**
- Grafana, Datadog, New Relic
- Dashboards, metrics, alerting

**Logging:**
- Splunk, ELK Stack, CloudWatch
- Log search and analysis

**Communication:**
- Slack, Microsoft Teams
- Incident channels, war rooms

**Video Conferencing:**
- Zoom, Google Meet
- Virtual war rooms for complex incidents

**Documentation:**
- Google Docs, Confluence
- Timeline, post-mortem

### Quick Links

**Your Organization's Resources:**
```
[ ] Runbook library: [URL]
[ ] Incident management tool: [URL]
[ ] Monitoring dashboards: [URL]
[ ] On-call schedule: [URL]
[ ] Escalation contacts: [URL]
[ ] Post-mortem template: [URL]
[ ] Status page (internal): [URL]
[ ] Status page (customer): [URL]
```

---

## Incident Response Checklist

### Quick Checklist (Print/Bookmark This)

**Detection (0-15 min)**
```
☐ Acknowledge alert
☐ Assess impact
☐ Determine severity
☐ Check runbook
```

**Declaration (15-25 min)**
```
☐ Declare incident
☐ Create incident channel
☐ Assign roles (IC, Comms, Tech Lead, Scribe)
☐ Post initial status
```

**Response (25+ min)**
```
☐ Establish update cadence
☐ Begin investigation
☐ Implement mitigation
☐ Send status updates
☐ Escalate if needed
```

**Resolution**
```
☐ Confirm service restored
☐ Monitor stabilization period
☐ Declare resolved
☐ Send final status update
☐ Thank the team
```

**Follow-Up**
```
☐ Complete timeline
☐ Schedule post-mortem
☐ Create action items
☐ Share learnings
```

---

## Remember

**Core Principles:**
1. **Safety First:** Prevent further damage before investigating
2. **Users First:** Restore service before perfect understanding
3. **Communicate:** Over-communicate during uncertainty
4. **Escalate Early:** Better to have help available than struggle alone
5. **Document:** Write it down, you won't remember later
6. **Learn:** Every incident is a learning opportunity

**You've Got This:**
- Incidents are stressful, but you're prepared
- Your team is here to support you
- Follow the process, trust your training
- Make decisions with available information
- Learn and improve for next time

---

**Last Updated:** November 2025
**Feedback:** [How to provide feedback on this playbook]
**Questions:** [Slack channel or email for questions]
