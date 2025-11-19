# On-Call Best Practices Reference

## Overview

Sustainable on-call practices are essential for maintaining both system reliability and engineer well-being. This reference provides best practices based on Google SRE principles and industry experience.

---

## Core Principles

### 1. On-Call is a Necessary Cost of Production Services
- Every production service requires humans available to respond
- On-call burden should be distributed fairly across the team
- If a service can't support on-call rotation, question if it should be in production

### 2. Sustainable On-Call is a Priority
- Burned-out engineers make mistakes and quit
- Long-term reliability requires healthy, rested responders
- Organization must invest in reducing toil and improving systems

### 3. On-Call Should Be Rare and Well-Compensated
- Goal: Minimize alerts and pages through automation
- When pages occur, they should matter
- Engineers should be compensated fairly for on-call duty

---

## On-Call Rotation Design

### Rotation Schedule Best Practices

**Rotation Duration:**
- **Recommended:** 1 week rotations
- **Acceptable:** 2 week rotations for smaller teams
- **Avoid:** Daily or <4 day rotations (too disruptive)
- **Avoid:** >2 week rotations (burnout risk)

**Team Size:**
- **Minimum:** 8 people for sustainable 24/7 rotation
  - Allows for: vacations, training, illness, attrition buffer
- **Ideal:** 10-12 people
- **Multi-tiered:** Consider primary/secondary on-call for larger teams

**Coverage Model:**

**Follow-the-Sun (Preferred for Global Teams):**
```
Region A: 08:00-20:00 local time
Region B: 08:00-20:00 local time (overlapping handoff)
Region C: 08:00-20:00 local time
```
Benefits: Business hours only, better work-life balance

**24/7 Individual Rotation:**
```
Primary on-call: 7 days, 24 hours/day
Secondary on-call: Escalation after 15-30 minutes
```
Benefits: Simpler for small/single-location teams

**Hybrid Model:**
```
Business hours: Primary on-call
Nights/weekends: Escalation from automated systems only
Critical alerts only outside business hours
```
Benefits: Reduces night/weekend burden

### Handoff Procedures

**Scheduled Handoff Times:**
- Same time each day (e.g., 9:00 AM in primary timezone)
- 15-30 minute overlap for handoff
- Document in team calendar and on-call tool

**Handoff Checklist:**
```
☐ Review ongoing incidents (if any)
☐ Review open tickets/alerts from rotation
☐ Highlight known issues or upcoming changes
☐ Confirm contact info and escalation paths
☐ Verify access to all required systems
☐ Review upcoming deployments or maintenance
☐ Transfer any in-flight investigations
```

**Documentation:**
- Handoff notes in shared document or wiki
- Timeline of significant events during rotation
- Recommendations for next on-call

---

## Alert Hygiene and Quality

### The Alert Fatigue Problem

**Symptoms:**
- Ignoring or silencing alerts
- Delayed response times
- Autopilot acknowledgment without investigation
- Low morale and high stress

**Root Causes:**
- Too many alerts
- Low signal-to-noise ratio
- Alert fatigue from non-actionable pages
- Unclear alert messages

### Principles of Good Alerts

**Every Alert Should Be:**

1. **Actionable**
   - Clear action required from on-call engineer
   - If no action possible, it's not an alert (use logging/metrics)

2. **Timely**
   - Requires immediate or near-immediate response
   - If it can wait until tomorrow, use ticket system

3. **User-Impacting**
   - Actual or imminent user impact
   - Internal-only issues should be lower priority

4. **Novel**
   - Not redundant with other alerts
   - Avoid alert storms for same root cause

**Alert Message Components:**
```
[SEVERITY] [SERVICE] [ISSUE]
What: Clear description of the problem
Impact: User/business impact
Action: First troubleshooting step or runbook link
Context: Recent changes, relevant dashboards
```

**Example Good Alert:**
```
[SEV-2] [API] High Error Rate on /checkout endpoint

What: 15% error rate on /checkout (threshold: 1%)
Impact: ~500 customers/minute unable to complete purchases
Action: Check runbook: https://wiki/runbooks/api-errors
Context:
- Started: 2025-11-19 14:23 UTC
- Recent deploy: v2.4.1 at 14:15 UTC
- Dashboard: https://grafana/api-health
```

### Alert Tuning Guidelines

**Alert Review Cadence:**
- Weekly: Review all alerts from past week
- Monthly: Analyze alert patterns and trends
- Quarterly: Deep dive on alert quality metrics

**Metrics to Track:**
```
- Pages per on-call shift
- Pages requiring action vs. false positives
- Time to acknowledge
- Time to resolution
- Alert suppression rate
- Repeat alerts for same issue
```

**Target Metrics (Google SRE Recommendations):**
- **Goal:** <2 pages per 12-hour on-call shift
- **Maximum sustainable:** <5 pages per 12-hour shift
- **Alert precision:** >75% require action

**When to Delete/Modify Alerts:**
- False positive rate >25%
- No action taken in response to alert >3 times
- Alert fires but issue self-resolves before response
- Duplicate alerts for same root cause
- Alert threshold inappropriate (too sensitive or not sensitive enough)

---

## Runbook Best Practices

### Purpose of Runbooks
- Reduce time to mitigation
- Standardize response procedures
- Enable less experienced engineers to respond effectively
- Document tribal knowledge

### Runbook Structure

**Essential Components:**
```markdown
# [Service/Component Name] - [Issue Type]

## Overview
Brief description of the issue and typical causes

## Symptoms
- How this issue manifests
- Related alerts that may fire
- User-visible impact

## Severity
Typical severity level (with conditions for escalation)

## Immediate Actions
Step-by-step first response:
1. Verify issue is occurring [command/dashboard]
2. Check for known causes [locations to check]
3. Attempt mitigation [safe first steps]

## Investigation
- Where to look for root cause
- Common culprits
- Relevant logs and metrics

## Mitigation
- Short-term fixes to restore service
- Rollback procedures
- Safe mode operations

## Escalation
When to escalate and to whom

## Post-Incident
- What to document
- Follow-up actions required
- Links to relevant post-mortems

## Related Runbooks
Links to related procedures
```

**Example Commands:**
- Include full commands, not just fragments
- Specify which host/environment
- Show expected output
- Explain what to look for

### Runbook Maintenance

**Ownership:**
- Every runbook has a designated owner
- Owner reviews quarterly or after major changes
- On-call feedback drives updates

**Testing:**
- Test runbooks during GameDay exercises
- Update based on actual incident usage
- Remove outdated information promptly

**Discoverability:**
- Linked from alerts
- Searchable wiki or documentation system
- Index page of all runbooks
- Tagged by service and issue type

---

## On-Call Preparedness

### Before Your Rotation Starts

**Technical Readiness:**
```
☐ Test pager/alert delivery (phone, Slack, email)
☐ Verify VPN access and credentials
☐ Confirm access to all production systems
☐ Test SSH keys and bastion host access
☐ Verify access to incident management tools
☐ Review monitoring dashboards
☐ Check out on-call laptop (if provided)
☐ Test video conferencing tools
```

**Knowledge Readiness:**
```
☐ Review recent incidents and post-mortems
☐ Check for scheduled maintenance or deployments
☐ Review updated runbooks
☐ Identify who to escalate to for each component
☐ Review architecture docs for recent changes
☐ Note any degraded systems or known issues
```

**Logistical Readiness:**
```
☐ Block calendar for on-call
☐ Notify family/friends of on-call duty
☐ Plan for reliable internet access
☐ Know backup phone/contact options
☐ Prepare workspace (if working from home)
☐ Arrange childcare backup (if needed)
```

### During Your Rotation

**Response Expectations:**
```
Acknowledge: < 5 minutes (SEV-1), < 15 minutes (SEV-2)
Initial assessment: Within 15 minutes of acknowledgment
Status update: Every 30-60 minutes during active incident
```

**Best Practices:**
- Stay near reliable internet and phone
- Limit alcohol consumption
- Keep laptop charged and accessible
- Maintain situational awareness of system health
- Don't start risky personal activities (e.g., long hikes)

**Work Balance:**
- Defer non-urgent work during on-call
- Use business hours to prepare for potential incidents
- Take breaks and maintain self-care
- Don't hesitate to escalate if overwhelmed

### After Your Rotation

**Handoff:**
- Complete handoff procedure (see above)
- Document lessons learned
- File tickets for issues to address
- Update runbooks based on experience

**Recovery:**
- Take compensatory time off if heavily paged
- Debrief with manager if rotation was problematic
- Contribute to alert tuning efforts
- Participate in post-mortem reviews

---

## Escalation Procedures

### When to Escalate

**Always Escalate When:**
- You don't have access to fix the issue
- You don't have expertise in the affected system
- Issue severity exceeds your authority level
- Multiple systems failing simultaneously
- You're overwhelmed or uncertain how to proceed
- Issue persists beyond reasonable investigation time

**Escalation is Not Failure:**
- Escalating promptly is the right choice
- Better to over-escalate than under-escalate
- Experienced engineers escalate frequently

### Escalation Paths

**Tiered Escalation:**
```
Level 1: On-call engineer
Level 2: On-call lead/senior engineer
Level 3: Team lead/manager
Level 4: Engineering director/VP
Level 5: CTO/executives
```

**Domain-Based Escalation:**
```
Database issues → DBA team
Network issues → Network engineering
Security issues → Security team
Infrastructure → Platform team
Application → Service team
```

**Escalation Contacts:**
- Maintain current contact list in on-call tool
- Include primary and backup contacts
- Test contact information quarterly
- Include timezone information for global teams

---

## Compensation and Time Off

### On-Call Compensation Models

**Financial Compensation:**
- On-call stipend (flat rate per day/week)
- Incident response pay (per incident or per hour)
- Overtime pay for after-hours incidents
- Differential pay for nights/weekends

**Time Off Compensation:**
- Compensatory time off for incidents
- Extra PTO for on-call rotation
- Flexible scheduling around on-call

**Google SRE Model:**
- 25% or less of time on on-call duties
- If exceeding 25%, hire more people or reduce service scope
- On-call rotation only for SRE-approved services

### Time-Off Policies

**During On-Call:**
- Clarify expectations for incidents during business hours
- Ensure ability to respond if working on other tasks
- Define "working hours" clearly for distributed teams

**PTO During Rotation:**
- Find coverage or swap rotation
- Don't schedule PTO during on-call without coverage plan
- Team process for PTO swap requests

**Post-Incident Recovery:**
- After major incident (>4 hours): rest of day off
- After overnight incident: following day off
- After weekend incident: comp day during week

---

## Reducing On-Call Burden

### Automation Strategies

**Self-Healing Systems:**
- Auto-restart failed services
- Auto-scale based on load
- Automatic failover to healthy instances
- Circuit breakers to prevent cascade failures

**Reduce Toil:**
- Automate repetitive manual tasks
- Eliminate repetitive tickets through tooling
- Build self-service tools for common requests

**Improved Monitoring:**
- Better signal-to-noise ratio
- Predictive alerts instead of reactive
- Automated remediation for known issues

### System Reliability Investments

**Priority Order:**
1. Eliminate single points of failure
2. Implement automated failover
3. Improve observability and debugging tools
4. Build rollback automation
5. Create comprehensive runbooks
6. Practice incident response through GameDays

### Team Process Improvements

**Post-Mortem Action Items:**
- Prioritize automation opportunities
- Address recurring incidents
- Invest in monitoring and alerting improvements

**On-Call Retrospectives:**
- Monthly review of on-call experience
- Identify sources of toil
- Propose improvements to tools and processes

**SLO-Driven Development:**
- Define error budgets
- Use error budget to prioritize reliability work
- Slow feature development if reliability suffers

---

## Mental Health and Well-Being

### Recognizing Burnout

**Warning Signs:**
- Dreading on-call rotations
- Anxiety about alerts
- Sleep disruption
- Decreased job satisfaction
- Physical symptoms (headaches, stomach issues)
- Irritability or cynicism

### Preventing Burnout

**Team Practices:**
- Fair rotation distribution
- Respect time off
- Celebrate successful incident response
- Share knowledge to reduce single points of failure
- Normalize escalation and asking for help

**Individual Practices:**
- Set boundaries (e.g., laptop away during off-hours when not on-call)
- Exercise and maintain physical health
- Maintain social connections
- Practice stress-reduction techniques
- Seek support when needed

**Organizational Support:**
- Provide EAP or mental health resources
- Train managers to recognize burnout
- Create psychologically safe environment
- Invest in reliability to reduce pages
- Offer on-call coaching and mentorship

### When to Speak Up

**Talk to Your Manager If:**
- On-call burden feels unsustainable
- You're consistently getting paged outside reasonable limits
- You feel unprepared or unsupported
- Personal circumstances make on-call difficult
- You need a break from rotation

**It's Okay to Ask For:**
- Temporary removal from rotation
- Additional training or support
- Process improvements
- Team expansion to share load

---

## On-Call Metrics and KPIs

### Health Metrics

**On-Call Load:**
```
- Pages per shift (target: <2 per 12h shift)
- After-hours pages (target: minimize)
- Time spent on incidents per rotation
- False positive rate (target: <25%)
```

**Response Quality:**
```
- Time to acknowledge
- Time to mitigate
- Escalation rate
- Incident resolution rate
```

**Team Health:**
```
- Burnout survey scores
- Rotation coverage gaps
- Voluntary rotation participation
- Attrition rate of on-call engineers
```

### Using Metrics

**Red Flags:**
- Pages per shift trending upward
- Increasing time to acknowledge
- High engineer turnover in on-call rotation
- Difficulty finding rotation coverage
- Frequent escalations due to lack of knowledge

**Actions Based on Metrics:**
- High page volume → Alert tuning sprint
- Knowledge gaps → Training and documentation
- Coverage issues → Hire or reduce service scope
- Burnout indicators → Immediate intervention

---

## Building On-Call Culture

### Cultural Principles

1. **Blameless Response**
   - Focus on systems, not individuals
   - Normalize mistakes and learning
   - Psychological safety to escalate

2. **Shared Responsibility**
   - Everyone participates in on-call
   - Including senior engineers and managers
   - No "elite" exemptions from rotation

3. **Continuous Improvement**
   - Every incident is learning opportunity
   - Invest in reliability based on pain points
   - Measure and track improvements

4. **Work-Life Balance**
   - Respect personal time
   - Sustainable pace is a feature, not a luxury
   - Organization supports healthy boundaries

### New Engineer Onboarding

**On-Call Readiness Timeline:**
```
Week 1-2: Shadow experienced on-call
Week 3-4: Reverse shadow (they watch you)
Week 5-6: Backup on-call with mentor available
Week 7+: Primary on-call rotation
```

**Training Requirements:**
```
☐ Complete architecture overview training
☐ Review all major runbooks
☐ Access to all required systems verified
☐ Participate in GameDay exercise
☐ Shadow at least one real incident
☐ Demonstrate basic troubleshooting skills
☐ Manager sign-off on on-call readiness
```

---

## GameDays and Practice

### Purpose of GameDays
- Practice incident response in low-stakes environment
- Test runbooks and procedures
- Train new engineers
- Identify gaps in documentation
- Build team cohesion

### GameDay Format

**Frequency:** Monthly or quarterly

**Structure:**
```
1. Pre-announce (or surprise, but announce type in advance)
2. Inject realistic failure scenario
3. Team responds as they would to real incident
4. Observers note process gaps
5. Debrief and document lessons
6. Create action items for improvements
```

**Scenario Ideas:**
- Database failover
- Regional outage
- Cascading failure
- Security incident
- Third-party service outage
- Deployment gone wrong

---

## Tools and Technology

### On-Call Management Tools

**Features to Look For:**
- Rotation scheduling
- Multi-channel alerting (phone, SMS, app, email)
- Escalation policies
- Integration with monitoring systems
- Mobile app with reliable notifications
- Incident timeline and collaboration
- Post-mortem integration

**Popular Tools:**
- PagerDuty
- Opsgenie
- VictorOps (Splunk On-Call)
- Google Cloud Incident Response

### Monitoring and Observability

**Essential Capabilities:**
- Real-time metrics dashboards
- Log aggregation and search
- Distributed tracing
- Alert management
- Service dependency mapping
- Incident correlation

### Communication Tools

**During Incidents:**
- Dedicated Slack/Teams channel per incident
- Video conferencing for war rooms
- Shared document for timeline (Google Docs, Confluence)
- Status page for customer communications

---

## References and Resources

### Foundational Reading
- **Google SRE Book** - "Being On-Call" chapter
- **Site Reliability Engineering Workbook** - "On-Call" chapter
- **The Phoenix Project** - DevOps narrative
- **Seeking SRE** - Various on-call perspectives

### Industry Resources
- PagerDuty Incident Response Guide
- Atlassian Incident Management Handbook
- FireHydrant Blog on Incident Management
- Honeycomb.io Observability Best Practices

### Continued Learning
- SREcon presentations (USENIX)
- DevOps Enterprise Summit talks
- Company post-mortem databases
- Peer company sharing (SRE Slack communities)

---

**Last Updated:** November 2025
**Review Frequency:** Quarterly
**Owned By:** SRE Leadership Team
