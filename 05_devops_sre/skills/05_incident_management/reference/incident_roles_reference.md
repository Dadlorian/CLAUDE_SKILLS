# Incident Response Roles Reference

## Overview

Effective incident response requires clear role definition and separation of concerns. This reference defines standard incident response roles based on Google SRE and PagerDuty best practices.

## Core Principle: Separation of Concerns

Each role has distinct responsibilities to prevent cognitive overload and ensure effective incident resolution. **No single person should perform multiple core roles simultaneously** during SEV-1/SEV-2 incidents.

---

## Incident Commander (IC)

### Primary Responsibility
Overall incident coordination and decision-making authority.

### Key Duties

**During Active Incident:**
- Declare incident and assign severity level
- Assemble and delegate to response team
- Maintain incident timeline and decision log
- Make strategic decisions on mitigation vs. root cause investigation
- Call for additional resources when needed
- Decide when to escalate or de-escalate severity
- Determine when incident is resolved
- Ensure smooth handoff if incident spans multiple shifts

**Decision Authority:**
- Final authority on all incident-related decisions
- Can override technical decisions if needed for resolution
- Determines when to implement risky mitigation strategies
- Authorizes emergency changes and bypasses normal processes

**Communication:**
- Establish communication channels
- Set update cadence for stakeholders
- Approve major communications before sending
- Interface with executives during major incidents
- Does NOT write detailed updates (delegates to Comms Lead)

### Skills Required
- Strong leadership and decision-making under pressure
- Broad technical knowledge (not necessarily deepest expert)
- Excellent communication skills
- Experience with incident patterns
- Ability to delegate effectively
- Comfort with ambiguity and incomplete information

### What the IC Does NOT Do
- Does NOT directly troubleshoot technical issues
- Does NOT write code or run debugging commands (except in solo response)
- Does NOT write customer communications (delegates to Comms Lead)
- Does NOT take detailed notes (delegates to Scribe)

### IC Best Practices

1. **Stay Above the Fray**
   - Resist the urge to dive into technical details
   - Trust your technical leads to investigate
   - Focus on coordination, not implementation

2. **Maintain Clear Communication**
   - Use clear, direct language
   - Confirm understanding of assignments
   - Set explicit deadlines for updates

3. **Make Timely Decisions**
   - Better to make a decision and adjust than to delay
   - Document reasoning for major decisions
   - Don't let perfect be the enemy of good enough

4. **Know When to Escalate**
   - Call for help before you're overwhelmed
   - Escalate severity if uncertainty persists
   - Bring in additional expertise proactively

5. **Care for Your Team**
   - Ensure people take breaks during long incidents
   - Watch for fatigue and cognitive overload
   - Rotate roles if incident extends beyond 4-6 hours

### IC Rotation Eligibility
- Senior engineers with 2+ years experience
- Completion of IC training program
- Shadow experience in 3+ major incidents
- Demonstrated leadership and communication skills
- On-call rotation participation

---

## Communications Lead (Comms Lead)

### Primary Responsibility
All stakeholder communication and status updates.

### Key Duties

**Internal Communications:**
- Post regular updates to internal incident channel
- Notify stakeholders based on severity level
- Coordinate with executive team during major incidents
- Update status pages and monitoring dashboards
- Manage incident Slack channel or war room

**External Communications:**
- Draft customer-facing status updates
- Update public status page
- Coordinate with customer support team
- Prepare and send customer notifications
- Monitor social media for customer reports (or delegate)

**Communication Management:**
- Establish update cadence with IC
- Gather information from Technical Leads for updates
- Translate technical details into business impact
- Maintain consistent messaging across channels
- Track questions from stakeholders and get answers

### Skills Required
- Excellent written communication
- Ability to translate technical concepts for non-technical audiences
- Calm under pressure
- Strong organizational skills
- Customer empathy and brand awareness

### Communication Templates and Timing

**SEV-1 Updates:**
- First update within 15 minutes of declaration
- Updates every 30-60 minutes minimum
- Include: current status, impact, next steps, ETA if available

**SEV-2 Updates:**
- First update within 30 minutes
- Updates every 2-4 hours
- Include: impact scope, progress, workarounds

**Update Components:**
```
1. Current Status (what's happening now)
2. Customer Impact (who is affected and how)
3. What We're Doing (actions being taken)
4. Next Update (when to expect more information)
5. Workarounds (if available)
```

### Comms Lead Best Practices

1. **Accuracy Over Speed (but be fast)**
   - Verify information before broadcasting
   - Better to delay 5 minutes than send incorrect info
   - Clearly mark estimates as estimates

2. **Appropriate Detail Level**
   - External: Business impact, not technical details
   - Internal Technical: Root cause investigation progress
   - Executive: Business impact + mitigation strategy

3. **Consistent Voice**
   - Use company communication guidelines
   - Maintain professional, empathetic tone
   - Avoid technical jargon in customer communications

4. **Proactive Communication**
   - Don't wait to be asked for updates
   - Over-communicate during major incidents
   - Acknowledge uncertainty when present

5. **Track Commitments**
   - Log all public ETAs and commitments
   - Ensure IC is aware of promises made
   - Follow up on all communication commitments

---

## Technical Lead (Tech Lead)

### Primary Responsibility
Hands-on investigation and resolution of technical issues.

### Key Duties

**Investigation:**
- Perform technical troubleshooting and debugging
- Form and test hypotheses about root cause
- Gather system state information and logs
- Execute diagnostic commands and queries
- Coordinate with other engineers on investigation

**Mitigation:**
- Implement fixes and workarounds
- Deploy emergency changes
- Roll back problematic deployments
- Modify system configurations
- Execute recovery procedures

**Reporting:**
- Provide regular updates to IC (not Comms Lead directly)
- Report findings, hypotheses, and progress
- Estimate time to resolution when possible
- Request additional resources if needed
- Recommend mitigation vs. investigation trade-offs

**Documentation:**
- Document commands executed and results
- Record configuration changes made
- Note dead-end investigations to avoid repetition
- Preserve evidence for post-mortem

### Skills Required
- Deep technical expertise in relevant systems
- Strong troubleshooting methodology
- Ability to work under pressure
- Clear communication of technical concepts
- Experience with production systems

### Multiple Technical Leads

For complex incidents, multiple Tech Leads may be needed:

- **Primary Tech Lead**: Coordinates technical investigation
- **Domain Specialists**: Database, networking, security, etc.
- Each reports to IC, Primary Tech Lead coordinates if needed

### Tech Lead Best Practices

1. **Systematic Investigation**
   - Form hypotheses before jumping to solutions
   - Document what you've tried
   - Avoid thrashing between different theories
   - Know when to call for specialized help

2. **Communication Discipline**
   - Give IC concise, clear updates
   - Separate facts from speculation
   - Provide realistic time estimates
   - Speak up if you're stuck

3. **Balance Speed and Safety**
   - Understand risk tolerance for mitigation strategies
   - Get IC approval for high-risk changes
   - Take calculated risks when appropriate
   - Know rollback procedures before deploying

4. **Preserve Evidence**
   - Don't destroy logs during investigation
   - Capture system state before making changes
   - Document unexpected behavior
   - Save debugging artifacts for post-mortem

5. **Know Your Limits**
   - Request help when needed
   - Don't pretend to understand what you don't
   - Suggest bringing in domain experts
   - Take breaks during extended incidents

---

## Scribe

### Primary Responsibility
Maintain detailed, timestamped incident timeline and documentation.

### Key Duties

**Timeline Management:**
- Record all significant events with timestamps
- Document decisions made and by whom
- Log communications sent
- Note when people join/leave incident response
- Track mitigation attempts and results
- Record system state observations

**Information Capture:**
- Commands executed (or at least significant ones)
- Configuration changes made
- Hypotheses proposed and tested
- Dead ends and ruled-out causes
- External factors discovered
- Escalations and resource requests

**Real-Time Documentation:**
- Maintain shared document or incident management tool
- Ensure IC and team can reference timeline during incident
- Organize information for easy reference
- Flag important discoveries or decisions

**Post-Incident:**
- Provide complete timeline for post-mortem
- Help fill in gaps in incident narrative
- Contribute to post-mortem documentation

### Skills Required
- Excellent attention to detail
- Fast, accurate typing
- Ability to listen and document simultaneously
- Understanding of technical concepts (to know what's important)
- Organizational skills

### Scribe Best Practices

1. **Timestamp Everything**
   - Use consistent timezone (usually UTC)
   - Precision to the minute is sufficient
   - Note major events to the second if critical

2. **Capture Decisions and Rationale**
   - "IC decided to roll back deployment due to..."
   - "Tech Lead chose to restart service because..."
   - Document what was considered but not done

3. **Use Clear, Concise Language**
   - Avoid ambiguity
   - Use direct quotes for critical statements
   - Paraphrase routine updates

4. **Organize for Real-Time Use**
   - Use headers/sections for different threads
   - Highlight critical information
   - Make it easy to skim

5. **Don't Interrupt the Flow**
   - Ask for clarification in side channels if possible
   - Focus on capturing what's said, not questioning it
   - Flag items for post-incident follow-up

### Sample Timeline Format

```
[2025-11-19 14:23 UTC] Incident declared SEV-2 by @alice
[2025-11-19 14:24 UTC] IC: @alice, Comms: @bob, Tech Lead: @charlie
[2025-11-19 14:25 UTC] Charlie: Observing 50% error rate on API endpoint /checkout
[2025-11-19 14:27 UTC] Charlie: Hypothesis - recent deployment v2.4.1 introduced regression
[2025-11-19 14:28 UTC] Alice (IC): Approved rollback to v2.4.0
[2025-11-19 14:30 UTC] Bob (Comms): First customer update sent
[2025-11-19 14:35 UTC] Charlie: Rollback complete, monitoring error rates
[2025-11-19 14:40 UTC] Charlie: Error rate returned to baseline, incident mitigated
[2025-11-19 14:42 UTC] Alice (IC): Declared incident resolved, transitioning to post-mortem
```

---

## Supporting Roles

### Subject Matter Expert (SME)
- Called in for specific domain expertise
- Reports to Tech Lead or IC
- Provides specialized knowledge (database, security, networking)
- May rotate into Tech Lead role if appropriate

### Customer Support Liaison
- Bridges incident response and customer support teams
- Provides customer impact reports
- Helps prioritize based on customer feedback
- Manages support ticket volume during incident

### Executive Sponsor
- Senior leader overseeing major incidents
- Provides business context and decision support
- Interfaces with external stakeholders (board, major customers)
- Approves major risk decisions
- Does NOT direct technical response (supports IC)

---

## Role Assignment Guidelines

### SEV-1 Incidents
**Required Roles:**
- Incident Commander
- Communications Lead
- Technical Lead (often multiple)
- Scribe
- Executive Sponsor

**Additional as Needed:**
- Subject Matter Experts
- Customer Support Liaison
- Additional Tech Leads

### SEV-2 Incidents
**Required Roles:**
- Incident Commander
- Communications Lead
- Technical Lead
- Scribe (recommended)

### SEV-3 Incidents
**Minimum Roles:**
- Incident Commander (may be the on-call engineer)
- Technical Lead (often same person as IC)
- Scribe (optional)

### SEV-4 Incidents
- Normal ticket assignment
- No formal incident roles

---

## Role Transitions and Handoffs

### When to Hand Off a Role

**Planned:**
- Shift changes during extended incidents
- Person better suited to role becomes available
- Initial responder hands off to designated role after startup

**Unplanned:**
- Role holder experiencing fatigue or stress
- Conflict of interest discovered
- Person needed in different role more urgently
- Emergency personal situation

### Handoff Best Practices

1. **Formal Announcement**
   - IC announces handoff to full team
   - Clear "I am now IC" or "Alice is now IC"

2. **State Transfer**
   - Outgoing role provides brief summary
   - Review current hypotheses and actions in flight
   - Transfer any private context

3. **Confirmation**
   - New role holder confirms understanding
   - IC (if not the one handing off) approves transition

4. **Documentation**
   - Scribe records handoff in timeline
   - Update incident management tool

---

## Training for Incident Roles

### IC Training Path
1. Incident response fundamentals training
2. Shadow experienced ICs (3-5 incidents)
3. Reverse shadow (experienced IC observes you)
4. Solo IC for lower severity incidents
5. Ongoing: quarterly IC simulation exercises

### Tech Lead Development
- Develop through on-call rotation
- Participate in production reviews
- Practice troubleshooting methodology
- Build expertise in critical systems

### Comms Lead Training
- Communication best practices workshop
- Review past incident communications
- Practice translating technical to business impact
- Shadow experienced Comms Leads

### Scribe Training
- Learn incident management tools
- Practice timeline creation
- Understand technical context
- Shadow experienced Scribes

---

## Role Anti-Patterns to Avoid

### The Hero IC
- IC diving into technical details instead of coordinating
- Results in: Poor coordination, delayed decisions, burnout

### The Silent Tech Lead
- Tech Lead not providing updates to IC
- Results in: IC uncertainty, poor decisions, stakeholder confusion

### The Opinion-Sharing Scribe
- Scribe offering solutions instead of documenting
- Results in: Distraction, incomplete timeline, confusion

### The Absent Comms Lead
- Comms Lead waiting to be told instead of proactively gathering info
- Results in: Late updates, poor stakeholder experience

### The Micromanaging IC
- IC dictating specific technical approaches
- Results in: Slower resolution, demoralized team, IC overload

---

## Cultural Norms for Role Success

1. **Respect Role Boundaries**: Don't do others' jobs
2. **Trust Your Teammates**: IC trusts Tech Leads to investigate
3. **Communicate Explicitly**: Don't assume, verify
4. **No Blame During Response**: Focus on resolution, not fault
5. **Empower Decision-Making**: IC has authority, team supports
6. **Practice Together**: Regular drills and simulations
7. **Continuous Improvement**: Learn from every incident

---

## References

- Google SRE Book - "Managing Incidents"
- PagerDuty Incident Response Guide
- Incident Review and Post-mortem Best Practices (Etsy)
- Atlassian Incident Management Handbook

**Last Updated:** November 2025
**Review Frequency:** Quarterly
