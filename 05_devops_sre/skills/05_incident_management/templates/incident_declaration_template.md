# Incident Declaration Template

## Purpose

Use this template when formally declaring a SEV-1 or SEV-2 incident. This ensures consistent communication and sets up the response team for success.

---

## Initial Incident Declaration

### In Incident Management System

```
Incident ID: [Auto-generated or create new]
Severity: SEV-[1/2/3]
Service/Component: [Affected service name]
Status: Investigating

Title: [Brief, descriptive title]
Example: "API /checkout endpoint returning 50% errors"

Description:
What: [What is happening - symptoms]
When: [When did this start - timestamp in UTC]
Impact: [Who/what is affected]
Initial Response: [What you're doing right now]
```

### In Slack/Teams (Incident Channel)

**Create dedicated incident channel:**
```
Channel name: #incident-[YYYY-MM-DD]-[short-description]
Example: #incident-2025-11-19-api-checkout-errors
```

**Initial announcement template:**

```
🚨 INCIDENT DECLARED - SEV-[X] 🚨

INCIDENT ID: [INC-12345]
SERVICE: [Service/Component name]
DECLARED BY: @[your-name]
DECLARED AT: [HH:MM UTC]

ISSUE:
[1-2 sentence description of what is happening]

IMPACT:
Users Affected: [All / Most / Many / Some / Estimated number]
Functionality: [What users cannot do]
Severity Rationale: [Why this severity level]

CURRENT STATUS: Investigating

TEAM ASSIGNED:
IC: @[Incident Commander]
Comms Lead: @[Communications Lead]
Tech Lead: @[Technical Lead]
Scribe: @[Scribe]

COMMUNICATION:
Status updates every [30-60 minutes for SEV-1, 2-4 hours for SEV-2]
Customer communication: [Comms Lead name] handling

RESOURCES:
Dashboard: [Link]
Runbook: [Link if applicable]
Incident Doc: [Link to collaborative timeline]
```

---

## Example: SEV-1 Declaration

```
🚨 INCIDENT DECLARED - SEV-1 🚨

INCIDENT ID: INC-20251119-001
SERVICE: Payment API
DECLARED BY: @alice
DECLARED AT: 14:23 UTC

ISSUE:
Payment API /checkout endpoint is returning 502 errors for all requests.
Complete checkout functionality is unavailable.

IMPACT:
Users Affected: All users attempting to checkout
Functionality: Unable to complete purchases or process payments
Severity Rationale: SEV-1 - Complete outage of revenue-generating functionality

CURRENT STATUS: Investigating

TEAM ASSIGNED:
IC: @alice
Comms Lead: @bob
Tech Lead: @charlie
Scribe: @dana
SME - Payments: @eve (paged, joining)

COMMUNICATION:
Status updates every 30-60 minutes
Customer communication: @bob handling, first update sent at 14:30 UTC

RESOURCES:
Dashboard: https://grafana.example.com/payment-api
Runbook: https://wiki.example.com/runbooks/payment-api-errors
Incident Doc: https://docs.google.com/document/d/xyz123
```

---

## Example: SEV-2 Declaration

```
🚨 INCIDENT DECLARED - SEV-2 🚨

INCIDENT ID: INC-20251119-002
SERVICE: Search Service
DECLARED BY: @frank
DECLARED AT: 09:15 UTC

ISSUE:
Search functionality is returning results 5-10 seconds slower than normal.
Average search response time: 8s (normal: 500ms)

IMPACT:
Users Affected: Estimated 30% of users experiencing slow search
Functionality: Search works but significantly degraded performance
Severity Rationale: SEV-2 - Major feature degraded, significant user impact

CURRENT STATUS: Investigating

TEAM ASSIGNED:
IC: @frank
Comms Lead: @grace
Tech Lead: @henry
Scribe: (team will document in incident doc)

COMMUNICATION:
Status updates every 2-4 hours
Customer communication: @grace will send first update within 30 minutes

RESOURCES:
Dashboard: https://grafana.example.com/search-service
Runbook: https://wiki.example.com/runbooks/search-performance
Incident Doc: https://docs.google.com/document/d/abc456
```

---

## Incident Channel Setup Checklist

**When creating incident channel:**

```
☐ Create channel with naming convention: #incident-YYYY-MM-DD-description
☐ Post initial incident declaration (use template above)
☐ Pin incident declaration message
☐ Set channel topic: "SEV-X: Brief description | IC: @name"
☐ Invite response team members
☐ Link to incident doc in channel description
☐ Pin links to relevant dashboards and runbooks
☐ Configure notifications (all messages = notify for SEV-1)
```

---

## What NOT to Include Initially

**Don't speculate:**
- ❌ "This is probably caused by..." (unless confirmed)
- ✅ "Investigating potential causes including..."

**Don't assign blame:**
- ❌ "Recent deployment by @person broke this"
- ✅ "Recent deployment at HH:MM may be related, investigating"

**Don't provide ETAs unless confident:**
- ❌ "Will be fixed in 30 minutes"
- ✅ "Next update in 30 minutes with progress"

**Don't include excessive technical detail:**
- ❌ "Database query SELECT * FROM users WHERE id IN (SELECT... is timing out"
- ✅ "Database queries are timing out, investigating root cause"

---

## Severity Quick Reference

**When declaring, ask yourself:**

| Question | SEV-1 | SEV-2 | SEV-3 |
|----------|-------|-------|-------|
| Can users use core features? | No | Degraded | Yes (mostly) |
| How many users affected? | All/Most | Many | Some |
| Is revenue directly impacted? | Yes | Possibly | Unlikely |
| Is there a workaround? | No | Difficult | Yes |
| Is data being lost? | Yes/Risk | No | No |

**See:** reference/incident_severity_levels.md for complete definitions

**When in doubt:** Start with higher severity, downgrade if appropriate

---

## Role Assignment Quick Guide

### Who Should Be IC?

**For SEV-1:**
- Experienced engineer with IC training
- First on-call engineer starts, may hand off to designated IC
- Should NOT be deeply involved in technical investigation

**For SEV-2:**
- On-call engineer or experienced team member
- Can serve as IC and Tech Lead if needed (smaller incidents)

### Who Should Be Comms Lead?

**Characteristics:**
- Strong written communication skills
- Can translate technical → business impact
- Not needed for hands-on technical investigation
- Calm under pressure

**Can be:**
- Dedicated comms rotation
- Product/project manager
- Engineering manager
- Designated team member

### Who Should Be Tech Lead?

**Characteristics:**
- Deep expertise in affected system
- Strong troubleshooting skills
- Available to focus on investigation

**Can be:**
- On-call engineer
- Subject matter expert
- Multiple tech leads for complex incidents

### Who Should Be Scribe?

**Characteristics:**
- Good attention to detail
- Fast, accurate note-taking
- Understands technical context

**Can be:**
- Junior engineer (good learning opportunity)
- IC in smaller incidents
- Dedicated scribe for major SEV-1

---

## After Declaration: Next Steps

**Immediate (0-15 minutes):**
```
☐ Ensure incident is created in incident management system
☐ Incident channel created and team invited
☐ Initial declaration posted
☐ Roles clearly assigned and acknowledged
☐ Comms Lead preparing first customer update
☐ Tech Lead beginning investigation
☐ Scribe ready to document timeline
```

**Within 30 minutes:**
```
☐ First customer communication sent (SEV-1)
☐ Investigation progressing
☐ Timeline being documented
☐ Any additional resources called in
☐ Leadership notified (automatic for SEV-1)
```

**Ongoing:**
```
☐ Regular status updates per cadence
☐ Timeline continuously updated
☐ Communication flowing effectively
☐ Decisions documented
☐ Progress toward resolution
```

---

## Declaration Message Templates by Severity

### SEV-1: Complete Outage

```
🚨 INCIDENT DECLARED - SEV-1 🚨

INCIDENT ID: [ID]
SERVICE: [Service name]
DECLARED: [Time UTC] by @[name]

ISSUE: [Service/feature] is completely unavailable

IMPACT:
• All users unable to [core functionality]
• [Business impact - revenue, SLA, etc.]
• Duration: [how long so far]

STATUS: All hands investigating

TEAM:
IC: @[name] | Comms: @[name] | Tech Lead: @[name] | Scribe: @[name]

UPDATES: Every 30-60 minutes

RESOURCES:
📊 Dashboard: [link]
📖 Runbook: [link]
📝 Timeline: [link]
```

### SEV-2: Major Degradation

```
🚨 INCIDENT DECLARED - SEV-2 🚨

INCIDENT ID: [ID]
SERVICE: [Service name]
DECLARED: [Time UTC] by @[name]

ISSUE: [Service/feature] is significantly degraded

IMPACT:
• [Percentage/description] of users experiencing [issue]
• [Specific functionality affected]
• Workaround: [if available]

STATUS: Investigating

TEAM:
IC: @[name] | Comms: @[name] | Tech Lead: @[name]

UPDATES: Every 2-4 hours

RESOURCES:
📊 Dashboard: [link]
📖 Runbook: [link]
📝 Timeline: [link]
```

### SEV-3: Minor Issues

```
INCIDENT DECLARED - SEV-3

INCIDENT ID: [ID]
SERVICE: [Service name]
DECLARED: [Time UTC] by @[name]

ISSUE: [Non-critical feature/issue description]

IMPACT:
• Limited users affected
• [Description of impact]
• Workaround: [available workaround]

STATUS: Investigating during business hours

OWNER: @[name]

Note: May not require formal incident channel for SEV-3
```

---

## Modification: Severity Change

**If escalating or de-escalating severity:**

```
⚠️ SEVERITY CHANGED ⚠️

Previous: SEV-[X]
New: SEV-[Y]

REASON:
[Why severity changed - impact expanded/reduced, new information, etc.]

UPDATED RESPONSE:
[Any changes to team, communication cadence, etc.]

TIME: [HH:MM UTC]
UPDATED BY: @[IC name]
```

---

## Modification: Incident Resolved

**When incident is resolved:**

```
✅ INCIDENT RESOLVED ✅

INCIDENT ID: [ID]
RESOLVED: [Time UTC]
DURATION: [Total time from declaration to resolution]

RESOLUTION:
[Brief description of what was done to resolve]

ROOT CAUSE:
[If known - or "Under investigation, post-mortem scheduled"]

IMPACT SUMMARY:
[Final count of affected users, duration, any data loss, etc.]

POST-INCIDENT:
Post-mortem scheduled: [Date/Time]
Action items: [Will be tracked in post-mortem]

THANKS:
Thanks to @[team members] for rapid response and resolution

This incident channel will remain for reference and post-mortem discussion.
```

---

## Tips for Effective Declarations

### Do:
✅ Declare formally when you meet severity criteria
✅ Be clear and concise
✅ Use objective, factual language
✅ Include all essential information
✅ Assign roles explicitly
✅ Link to resources (dashboards, runbooks)
✅ Set clear communication expectations

### Don't:
❌ Delay declaration waiting for perfect information
❌ Downplay impact or severity
❌ Assign blame in initial declaration
❌ Make promises you can't keep (ETAs)
❌ Use excessive technical jargon
❌ Forget to notify stakeholders per severity level

### Remember:
- Better to over-declare and downgrade than under-respond
- Declaration is about mobilizing response, not assigning blame
- Clear communication sets the tone for the entire incident
- Document as you go - you won't remember later

---

**Template Version:** 1.0
**Last Updated:** November 2025
**Feedback:** [How to suggest improvements to this template]
