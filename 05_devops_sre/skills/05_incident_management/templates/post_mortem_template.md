# Post-Mortem: [Incident Title]

**Incident ID:** [INC-YYYYMMDD-###]
**Date of Incident:** [YYYY-MM-DD]
**Severity:** SEV-[1/2/3]
**Duration:** [X hours Y minutes]
**Author:** [Name]
**Reviewers:** [Names]
**Status:** [Draft / In Review / Published]
**Last Updated:** [YYYY-MM-DD]

---

## Executive Summary

[2-4 paragraph summary covering: what happened, impact, root cause, and key actions being taken]

**What Happened:**
[Brief description of the incident in plain language]

**Impact:**
[High-level impact on customers and business]

**Root Cause:**
[Primary contributing factors - often multiple]

**Resolution:**
[How it was resolved]

**Prevention:**
[Key actions being taken to prevent recurrence]

---

## Impact

### User Impact

**Users Affected:**
- Total affected: [Number or percentage]
- User segments: [Which customer types/tiers]
- Geographic distribution: [If relevant]

**Impact Duration:**
- Started: [YYYY-MM-DD HH:MM UTC]
- Detected: [YYYY-MM-DD HH:MM UTC]
- Mitigated: [YYYY-MM-DD HH:MM UTC]
- Resolved: [YYYY-MM-DD HH:MM UTC]
- Total duration: [X hours Y minutes]
- Time to detection: [X minutes]
- Time to mitigation: [X minutes]

**Functionality Impact:**
- [Feature/capability]: [Complete outage / Degraded / Unavailable]
- [Feature/capability]: [Impact description]
- [Feature/capability]: [Impact description]

**User Experience:**
[Description of what users experienced - error messages, slow performance, etc.]

### Business Impact

**Revenue:**
- Estimated revenue impact: [$X or "Not applicable"]
- Calculation method: [How estimated]

**SLA/SLO:**
- SLA status: [Met / Violated]
- SLO impact: [% of error budget consumed]
- Contractual obligations: [Any commitments violated]

**Reputation:**
- Customer escalations: [Number and severity]
- Social media mentions: [Summary if significant]
- Press coverage: [If applicable]
- Support tickets: [Number related to incident]

**Other Impacts:**
- [Any other business impacts - partnerships, compliance, etc.]

---

## Timeline

**All times in UTC. Key: 🔴 Critical moment | 🔧 Action taken | 📢 Communication sent | ✅ Resolution**

| Time (UTC) | Event | Details |
|------------|-------|---------|
| HH:MM | 🔴 **Incident began** | [Initial triggering event] |
| HH:MM | Alert fired | [Which alert, who was paged] |
| HH:MM | Acknowledged | [Who acknowledged] |
| HH:MM | 🔴 **Incident declared** | [Severity, IC assigned] |
| HH:MM | Investigation started | [Initial hypothesis] |
| HH:MM | 📢 First customer update | [Comms Lead sent initial status] |
| HH:MM | 🔧 [Action] | [Mitigation attempt, result] |
| HH:MM | Discovery | [Key finding or realization] |
| HH:MM | Escalation | [Additional help called in] |
| HH:MM | 🔧 [Action] | [Another attempt] |
| HH:MM | 📢 Status update | [Update sent to customers] |
| HH:MM | 🔴 **Mitigation applied** | [What was done] |
| HH:MM | ✅ **Service restored** | [Confirmation of recovery] |
| HH:MM | Monitoring | [Stabilization period] |
| HH:MM | ✅ **Incident resolved** | [Formal resolution declared] |
| HH:MM | 📢 Final update | [Resolution communicated] |

### Detailed Timeline Narrative

[Narrative description of the incident, expanding on the table above. Include:]

**Detection:**
[How the issue was discovered - alert, customer report, monitoring]

**Investigation:**
[What the team investigated, hypotheses formed and tested, dead ends encountered]

**Mitigation:**
[What actions were taken to restore service, what worked and what didn't]

**Resolution:**
[Final state and how stability was confirmed]

---

## Root Cause Analysis

### Contributing Factors

[List ALL contributing factors - incidents rarely have a single cause]

**Primary Technical Cause:**
[The immediate technical reason for the failure]

**Example:**
> Database connection pool was exhausted, causing application servers to be unable to process requests, resulting in 502 errors to users.

**Contributing Factor: [Category]**
[Description of this contributing factor]

**Why it contributed:**
[Explanation of how this factor enabled or worsened the incident]

**Example Contributing Factors to Include:**

1. **System Design / Architecture**
   - Single point of failure
   - Missing redundancy
   - Insufficient capacity
   - Design assumptions violated

2. **Code / Application**
   - Bug introduced in recent change
   - Connection leak
   - Memory leak
   - Error handling gap

3. **Change Management**
   - Insufficient testing
   - Deployment process gap
   - Rollback capability missing
   - Change window timing

4. **Monitoring / Alerting**
   - Missing monitoring
   - Alert threshold incorrect
   - Delayed detection
   - Alert fatigue

5. **Process**
   - Runbook outdated or missing
   - Unclear escalation path
   - Communication breakdown
   - Knowledge gap

6. **Human Factors**
   - Cognitive load during incident
   - Information not readily available
   - Training or experience gap
   - Reasonable mistake under pressure

7. **External / Environmental**
   - Third-party service degradation
   - Unexpected traffic pattern
   - Resource exhaustion
   - Infrastructure issue

### 5 Whys Analysis

[Optional - use if helpful for root cause analysis]

**Problem Statement:** [The incident]

1. **Why did [problem] occur?**
   - [Answer]

2. **Why did [answer from #1] occur?**
   - [Answer]

3. **Why did [answer from #2] occur?**
   - [Answer]

4. **Why did [answer from #3] occur?**
   - [Answer]

5. **Why did [answer from #4] occur?**
   - [Answer]

**Root causes identified:** [Summary]

### What Was Affected and Why

**System Components:**
- Component: [Name] | Impact: [How it was affected] | Why: [Reason]
- Component: [Name] | Impact: [How it was affected] | Why: [Reason]

**Dependencies:**
- Dependency: [Name] | Impact: [How it impacted the incident] | Why: [Reason]

---

## What Went Well

[Acknowledge effective responses and processes that should be preserved]

### Effective Responses

**Detection:**
- [What helped us detect the issue quickly or effectively]

**Investigation:**
- [What made investigation effective]

**Mitigation:**
- [What helped resolve the incident]

**Communication:**
- [What communication practices worked well]

**Example:**

> **Effective rollback process:** Our automated rollback procedure allowed us to revert the deployment in under 5 minutes, minimizing user impact.
>
> **Cross-team collaboration:** Platform and application teams collaborated effectively in the incident channel, sharing context and coordinating investigation.
>
> **Clear communication:** Communications Lead provided clear, timely updates to customers every 30 minutes, managing expectations effectively.

---

## What Could Be Improved

[Areas for improvement - these inform action items]

### Detection & Monitoring

**Gaps identified:**
- [What monitoring or alerting was missing]
- [What would have helped detect sooner]
- [What indicators we should have noticed]

### Investigation & Response

**Challenges faced:**
- [What made investigation difficult]
- [What information was hard to find]
- [What tools or access were needed]

### Process & Documentation

**Gaps identified:**
- [Runbook gaps or inaccuracies]
- [Process confusion or missing procedures]
- [Documentation needs]

### System Design & Architecture

**Weaknesses exposed:**
- [Architectural issues revealed by incident]
- [Design assumptions that failed]
- [Missing safeguards or resilience]

---

## Action Items

[Specific, actionable improvements to prevent recurrence and improve response]

### Critical Priority

**Action items that directly prevent recurrence of this specific incident.**

| # | Action Item | Owner | Due Date | Status | Success Criteria |
|---|-------------|-------|----------|--------|------------------|
| 1 | [Specific action] | @name | YYYY-MM-DD | Open | [How we know it's done] |
| 2 | [Specific action] | @name | YYYY-MM-DD | Open | [How we know it's done] |

### High Priority

**Action items that significantly improve detection, response, or resilience.**

| # | Action Item | Owner | Due Date | Status | Success Criteria |
|---|-------------|-------|----------|--------|------------------|
| 3 | [Specific action] | @name | YYYY-MM-DD | Open | [How we know it's done] |
| 4 | [Specific action] | @name | YYYY-MM-DD | Open | [How we know it's done] |

### Medium Priority

**Incremental improvements to processes, documentation, or systems.**

| # | Action Item | Owner | Due Date | Status | Success Criteria |
|---|-------------|-------|----------|--------|------------------|
| 5 | [Specific action] | @name | YYYY-MM-DD | Open | [How we know it's done] |

### Examples of Good Action Items

**Bad (vague):**
> "Improve monitoring"

**Good (specific):**
> "Add alerting for database connection pool utilization >80% with 5-minute sustained threshold"
> - Owner: @alice
> - Due: 2025-12-01
> - Success: Alert fires in test, runbook linked, team trained

**Bad (no owner):**
> "The team should update the runbook"

**Good (clear owner):**
> "Update API deployment runbook to include connection pool verification step"
> - Owner: @bob (single person accountable)
> - Due: 2025-11-25
> - Success: Runbook updated, reviewed by team, used in next deployment

---

## Lessons Learned

[Broader insights that apply beyond this specific incident]

### Technical Lessons

1. **[Lesson]:** [Description and broader applicability]
   - **Applied to:** [Other systems or services where this applies]
   - **Recommendation:** [General guidance]

2. **[Lesson]:** [Description]

### Process Lessons

1. **[Lesson]:** [Description]

2. **[Lesson]:** [Description]

### Organizational Lessons

1. **[Lesson]:** [Description]

2. **[Lesson]:** [Description]

### Examples

> **Lesson: Connection pool monitoring is critical**
> - **Description:** Lack of visibility into connection pool utilization allowed the issue to escalate to complete failure before detection.
> - **Applied to:** All services using database connection pools (identified 7 other services)
> - **Recommendation:** Standard monitoring for all connection pools across the organization
>
> **Lesson: Deployment canary windows should match traffic patterns**
> - **Description:** Our 30-minute canary deployment occurred during low traffic, missing the load-related issue that manifested under high traffic.
> - **Applied to:** All production deployments
> - **Recommendation:** Either extend canary window or deploy during representative traffic periods

---

## Supporting Information

### Graphs and Visualizations

[Include key graphs showing the incident]

**[Graph Title]:**
[Link to graph or embed image]
**Description:** [What this shows]

**Example graphs to include:**
- Error rate over time
- Latency/performance over time
- Resource utilization (CPU, memory, connections)
- Traffic patterns
- Relevant business metrics (transactions, revenue, etc.)

### Related Incidents

**Previous Similar Incidents:**
- [INC-YYYYMMDD-###]: [Brief description] - [Link to post-mortem]
- [INC-YYYYMMDD-###]: [Brief description] - [Link to post-mortem]

**Related Issues:**
- [TICKET-###]: [Description and relevance]

### External References

**Vendor/Third-Party Status:**
- [If relevant, link to external status pages or communications]

**Documentation:**
- Architecture diagram: [Link]
- Runbook: [Link]
- Monitoring dashboard: [Link]
- Code changes: [PR/commit links]

---

## Appendix

### Participants

**Incident Response Team:**
- Incident Commander: [Name]
- Communications Lead: [Name]
- Technical Lead: [Name, Name]
- Scribe: [Name]
- Subject Matter Experts: [Name, Name]

**Post-Mortem Participants:**
- Facilitator: [Name]
- Attendees: [Names]

### Communication Log

**Internal Communications:**
- [HH:MM UTC]: [Summary of internal update]

**Customer Communications:**
- [HH:MM UTC]: [Summary of customer-facing message]
- [Link to status page updates]

### Commands and Queries Executed

[Optional: Include significant diagnostic commands or queries run during investigation]

```
[Timestamp] [Command/Query]
Result: [Summary of result]
```

### Configuration Changes

[List any configuration changes made during incident]

| Component | Change | Timestamp | Changed By |
|-----------|--------|-----------|------------|
| [Name] | [Description] | HH:MM UTC | [Name] |

### Deployment History

[Relevant deployments before and during incident]

| Service | Version | Deployed | Deployed By | Rollback |
|---------|---------|----------|-------------|----------|
| [Name] | [Version] | HH:MM UTC | [Name] | HH:MM UTC |

---

## Sign-off

**Reviewed and Approved:**

- **Technical Accuracy:** [Name, Title] - [Date]
- **Action Items:** [Name, Title] - [Date]
- **Engineering Leadership:** [Name, Title] - [Date]

**Distribution:**
- Engineering team: [Date]
- Leadership: [Date]
- Company-wide: [Date]
- External/Public: [Date or N/A]

---

## Follow-Up

**Action Item Tracking:**
- Tickets created: [Link to project/board]
- Review cadence: [Weekly in team meeting]
- Completion target: [Date]

**Post-Mortem Review:**
- Scheduled for: [1 month after incident]
- Review status: [Link or meeting notes]

**Metrics:**
- Time to mitigation: [X minutes]
- Action items completed: [X/Y]
- Repeat incidents prevented: [Tracking]

---

## Template Usage Notes

**When completing this template:**

✅ **Do:**
- Be thorough and specific
- Use blameless language
- Include data and evidence
- Link to supporting materials
- Make action items concrete
- Think about broader lessons

❌ **Don't:**
- Use blame or judgmental language
- Include personally identifying information unnecessarily
- Make excuses or minimize impact
- Create vague action items
- Skip difficult sections
- Rush the process

**Sections you may customize:**
- Add sections specific to your organization's needs
- Remove sections not applicable to your incident
- Adjust detail level based on severity (SEV-1 = most detailed)
- Include compliance or regulatory sections if required

**Review process:**
1. Technical team reviews for accuracy
2. Engineering leadership reviews for completeness
3. Broader team reviews for clarity
4. Publish and distribute

**Remember:** The goal is learning and improvement, not checking a box.

---

**Template Version:** 1.0
**Last Updated:** November 2025
**Maintained By:** [Team/Person]
**Feedback:** [How to suggest improvements]

**Related Resources:**
- Post-mortem process: reference/post_mortem_process.md
- Facilitator guide: guides/running_effective_post_mortems.md
- Incident response playbook: guides/incident_response_playbook.md
