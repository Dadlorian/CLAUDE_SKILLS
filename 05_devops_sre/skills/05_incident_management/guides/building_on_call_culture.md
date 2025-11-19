# Building On-Call Culture: A Leadership Guide

## Purpose

This guide helps engineering leaders build and maintain a sustainable, healthy on-call culture. Whether you're establishing on-call for the first time or improving an existing program, this guide provides practical strategies and frameworks.

---

## Why On-Call Culture Matters

### The Stakes

**When on-call culture is unhealthy:**
- Engineers burn out and quit
- Incident response quality suffers
- Service reliability degrades
- Team morale plummets
- Recruitment and retention become difficult
- Innovation slows (too much firefighting)

**When on-call culture is healthy:**
- Engineers feel supported and valued
- Incident response is effective
- System reliability improves over time
- Team morale is strong
- Engineers want to join and stay
- Balance between firefighting and building

**The Bottom Line:**
Sustainable on-call is not a luxury—it's essential for long-term reliability and team health.

---

## Core Principles of Healthy On-Call Culture

### 1. On-Call Should Be Rare and Meaningful

**Every alert should be:**
- Actionable: Requires human intervention
- Timely: Needs immediate or near-immediate response
- Novel: Not redundant with other alerts
- User-impacting: Actual or imminent customer impact

**Target:** <2 pages per 12-hour on-call shift (Google SRE recommendation)

**This means:**
- Aggressive alert tuning
- Automation of routine issues
- Investment in reliability
- Elimination of false positives

### 2. On-Call Burden Should Be Fairly Distributed

**Fair distribution means:**
- Everyone participates (including senior engineers and managers)
- Rotation is balanced and predictable
- PTO and life events are respected
- No single points of failure (bus factor)

**Exemptions from on-call indicate:**
- Team is too small
- Insufficient knowledge sharing
- Unclear service ownership
- Cultural problems

### 3. Engineers Should Be Set Up for Success

**Success requires:**
- Comprehensive runbooks
- Effective monitoring and debugging tools
- Clear escalation paths
- Adequate training and onboarding
- Access to all necessary systems
- Support from team and leadership

**Engineers should never feel:**
- Alone and unsupported
- Unprepared or undertrained
- Unable to get help
- Blamed for escalating
- Punished for mistakes made during incidents

### 4. Investment in Reliability is a Priority

**Reducing toil means:**
- Prioritize automation and self-healing
- Fix recurring incidents
- Invest in monitoring and observability
- Improve deployment safety
- Address technical debt affecting reliability

**When engineers spend >25% of time on on-call work:**
- Hire more people, OR
- Reduce service scope, OR
- Invest heavily in reliability improvements

### 5. Blameless Culture Extends to On-Call

**Blamelessness means:**
- Mistakes during incidents are learning opportunities
- Escalating is encouraged and normalized
- Post-mortems focus on systems, not people
- Psychological safety to admit uncertainty
- Recognition for transparency and honesty

---

## Establishing On-Call: A Roadmap

### Phase 1: Assess Readiness (Before implementing on-call)

**Service readiness checklist:**
```
☐ Service is business-critical (on-call is justified)
☐ Monitoring and alerting are in place
☐ Basic runbooks exist for common issues
☐ Deployment and rollback processes are documented
☐ Architecture documentation is available
☐ Incident response process is defined
☐ Team has at least 8-10 people for rotation
☐ Leadership committed to supporting on-call
```

**If not ready:**
- Invest in readiness before implementing on-call
- Consider temporary coverage models
- Plan timeline to readiness

### Phase 2: Design Your On-Call System

**Key decisions:**

**1. Rotation model:**

**Option A: Follow-the-Sun (for global teams)**
```
Benefits:
- Business hours only for each region
- Better work-life balance
- Natural handoffs

Requirements:
- Teams in multiple regions
- Documented handoff process
- Overlapping hours for handoff

Challenges:
- Coordination across regions
- Knowledge sharing
- Time zone complexity
```

**Option B: 24/7 Individual Rotation**
```
Benefits:
- Simpler for single-location teams
- Clear ownership

Requirements:
- Compensation for after-hours
- At least 8-10 people
- Clear escalation paths

Challenges:
- Night/weekend burden
- Sustainability concerns
```

**Option C: Hybrid Model**
```
Business hours: Primary on-call
Nights/weekends: Critical alerts only, escalation model

Benefits:
- Reduced burden
- Focus on truly urgent issues

Requirements:
- Clear severity definitions
- Automated escalation
- Executive buy-in
```

**2. Rotation length:**
- **Recommended:** 1 week
- **Acceptable:** 2 weeks for smaller teams
- **Avoid:** <4 days or >2 weeks

**3. Escalation tiers:**
- Primary on-call
- Secondary on-call (escalation after 15-30 min)
- Manager escalation
- Executive escalation (for SEV-1)

**4. Compensation model:**
- On-call stipend (flat rate per shift/week)
- Incident response pay (per incident or per hour)
- Compensatory time off
- Combination approach

### Phase 3: Build Foundations

**1. Create runbooks:**
```
Priority runbooks to create first:
☐ Deployment rollback
☐ Service restart procedure
☐ Database failover
☐ Traffic routing/failover
☐ Top 5 most common alerts
☐ Escalation procedures
☐ Access and tool guide
```

**See:** templates/runbook_template.md

**2. Set up monitoring and alerting:**
```
☐ Service health dashboards
☐ Alerting rules configured
☐ Alert messages are clear and actionable
☐ Runbooks linked from alerts
☐ Test alert delivery to all team members
```

**3. Document the process:**
```
☐ On-call rotation schedule
☐ Response time expectations
☐ Incident severity definitions
☐ Escalation paths and contacts
☐ Communication procedures
☐ Post-incident follow-up process
```

**4. Set up tools:**
```
☐ On-call scheduling tool (PagerDuty, Opsgenie, etc.)
☐ Incident management system
☐ Communication channels (Slack, etc.)
☐ Monitoring and observability tools
☐ Access management (VPN, SSH, etc.)
```

### Phase 4: Train Your Team

**Training curriculum:**

**1. Technical training:**
- Service architecture overview
- Common failure modes
- Debugging and troubleshooting techniques
- Tool usage (monitoring, logging, tracing)
- Deployment and rollback procedures

**2. Process training:**
- Incident response playbook
- Severity assessment
- When and how to escalate
- Communication best practices
- Post-incident procedures

**3. Hands-on practice:**
- Shadow experienced on-call engineers
- Participate in GameDay exercises
- Walk through runbooks
- Practice using tools
- Mock incident response

**Onboarding timeline for new on-call engineers:**
```
Week 1-2: Shadow experienced on-call (observe)
Week 3-4: Reverse shadow (they watch you)
Week 5-6: Backup on-call with mentor available
Week 7+: Primary on-call rotation
```

**Ongoing training:**
- Monthly GameDay exercises
- Quarterly on-call retrospectives
- Post-mortem review sessions
- Architecture deep dives

### Phase 5: Launch and Iterate

**Soft launch:**
- Start with secondary on-call only
- Primary on-call handled by experienced engineers
- Build confidence before full rotation

**Phased rollout:**
```
Week 1-2: Experienced engineers only
Week 3-4: Add trained engineers to rotation
Week 5-8: Expand rotation as training completes
Week 9+: Full team rotation with ongoing improvements
```

**Early feedback loops:**
- Weekly on-call retrospectives
- Survey after each rotation
- Monthly metrics review
- Rapid iteration on process

---

## Maintaining Healthy On-Call Culture

### Regular Health Checks

**Weekly:**
```
☐ Review pages from past week
☐ Identify false positives or low-value alerts
☐ Check for repeat issues
☐ Gather feedback from on-call engineer
☐ Review any escalations
```

**Monthly:**
```
☐ Analyze on-call metrics and trends
☐ Review action items from post-mortems
☐ Assess runbook usage and updates needed
☐ Conduct team on-call retrospective
☐ Review compensation and fairness
☐ Check rotation coverage and gaps
```

**Quarterly:**
```
☐ Deep dive on on-call health metrics
☐ Survey team on on-call experience
☐ Review and update on-call documentation
☐ Assess training effectiveness
☐ Benchmark against industry standards
☐ Set goals for next quarter
```

### Key Metrics to Track

**Workload Metrics:**
```
- Pages per on-call shift
  Target: <2 per 12-hour shift
  Alert: >5 per 12-hour shift

- After-hours pages (nights/weekends)
  Target: Minimize
  Alert: Increasing trend

- Time spent on incidents per rotation
  Target: <25% of shift time
  Alert: >50% of shift time

- False positive rate
  Target: <25%
  Alert: >40%
```

**Response Quality Metrics:**
```
- Time to acknowledge alert
  Target: <5 min (SEV-1), <15 min (SEV-2)

- Time to mitigation
  Track trend over time

- Escalation rate
  Track and understand why

- Runbook usage rate
  Target: Runbooks used in majority of incidents
```

**Team Health Metrics:**
```
- On-call satisfaction score (1-5)
  Target: >3.5
  Alert: <3.0 or declining trend

- Burnout indicators (survey)
  Monitor closely

- Rotation coverage gaps
  Target: <5% of shifts uncovered

- Voluntary participation in rotation
  Alert: Difficulty finding coverage

- Attrition rate of on-call engineers
  Alert: Higher than non-on-call peers
```

**Improvement Metrics:**
```
- Alert tuning rate
  Track alerts removed or improved

- Runbook creation/updates
  Track completeness and freshness

- Automation implementations
  Track toil reduction

- Post-mortem action item completion
  Target: >80% within deadline
```

### Alert Tuning and Maintenance

**Continuous improvement:**

**Weekly alert review:**
```
1. Review all alerts from past week
2. For each alert:
   - Was it actionable?
   - Did it require immediate response?
   - Was the impact user-facing?
   - Did it page the right severity?
3. Tune, remove, or improve alerts
```

**Monthly alert health:**
```
☐ Identify noisy alerts (high volume, low value)
☐ Remove or aggregate low-value alerts
☐ Adjust thresholds based on data
☐ Improve alert messages for clarity
☐ Add runbook links where missing
☐ Review alert fatigue feedback
```

**Alert tuning principles:**
```
Delete: Alert has no value (>75% false positives)
Aggregate: Multiple alerts for same issue
Adjust: Threshold too sensitive or not sensitive enough
Enhance: Add context, runbook link, suggested action
Automate: Issue can be auto-remediated
```

### Runbook Maintenance

**Keep runbooks current:**

**After each incident:**
- Update runbook if process changed
- Add new runbooks for novel issues
- Note what worked and what didn't

**Monthly runbook review:**
```
☐ Identify most-used runbooks
☐ Update based on recent incidents
☐ Remove outdated information
☐ Fill gaps in coverage
☐ Test runbooks for accuracy
```

**Quarterly comprehensive review:**
```
☐ Review all runbooks
☐ Archive obsolete runbooks
☐ Standardize format and structure
☐ Ensure ownership assigned
☐ Test critical runbooks in GameDay
```

**Runbook quality metrics:**
```
- % of alerts with runbook links
  Target: 100% for recurring alerts

- Runbook usage in incidents
  Target: >80% of incidents

- Runbook effectiveness feedback
  Gather from on-call engineers

- Time since last update
  Flag runbooks >6 months old
```

---

## Addressing Common Challenges

### Challenge: Alert Fatigue and High Page Volume

**Symptoms:**
- Frequent pages (>5 per shift)
- Many false positives
- Engineers ignoring or auto-acknowledging alerts
- Declining response times
- Frustration and complaints

**Root causes:**
- Over-alerting on non-critical issues
- Alert thresholds too sensitive
- Lack of aggregation or deduplication
- No investment in alert quality
- Alert sprawl over time

**Solutions:**

**1. Alert quality sprint (2-4 weeks):**
```
☐ Catalog all alerts
☐ Classify by actionability and value
☐ Delete low-value alerts (be aggressive)
☐ Adjust thresholds based on data
☐ Aggregate related alerts
☐ Add auto-remediation where possible
☐ Improve alert messages
```

**2. Establish alert standards:**
```
Every alert must:
- Be actionable (human intervention required)
- Be timely (needs immediate response)
- Have user impact (actual or imminent)
- Have clear message and runbook
- Have appropriate severity
```

**3. Ongoing alert governance:**
- New alerts must be reviewed and approved
- Regular alert audits
- Metrics on alert quality
- Team accountability for alert volume

### Challenge: Knowledge Gaps and Insufficient Training

**Symptoms:**
- Frequent escalations due to lack of knowledge
- Long time to resolution
- Engineers feeling unprepared
- Repeat questions in incidents
- Heavy reliance on specific experts

**Root causes:**
- Insufficient onboarding
- Poor documentation
- Knowledge silos
- Lack of architectural understanding
- Limited hands-on practice

**Solutions:**

**1. Improve onboarding:**
```
☐ Structured on-call training program
☐ Required shadowing period
☐ Hands-on exercises and GameDays
☐ Architecture deep dives
☐ Tool and process training
☐ Certification before on-call eligibility
```

**2. Better documentation:**
```
☐ Comprehensive runbooks
☐ Architecture documentation
☐ Troubleshooting guides
☐ Post-mortem database
☐ Frequently asked questions
☐ Video walkthroughs
```

**3. Knowledge sharing:**
```
☐ Regular architecture reviews
☐ Post-mortem learning sessions
☐ On-call experience sharing
☐ Lunch-and-learns from incidents
☐ Pairing and mentorship
☐ Cross-team exposure
```

**4. Normalize escalation:**
- Make it clear escalation is encouraged
- Remove stigma from asking for help
- Celebrate good escalation decisions
- Track escalations to identify training needs

### Challenge: Burnout and Unsustainable Workload

**Symptoms:**
- Pages exceeding sustainable levels (>5 per shift)
- Frequent night/weekend pages
- Engineers dreading on-call
- Physical or emotional exhaustion
- Increased attrition
- Declining incident response quality

**Root causes:**
- System reliability issues
- Understaffing
- Lack of investment in reliability
- Unrealistic expectations
- Insufficient compensation or recovery time

**Solutions:**

**1. Immediate interventions:**
```
☐ Temporarily reduce rotation frequency
☐ Add secondary on-call support
☐ Bring in additional help (contractors, other teams)
☐ Provide mental health resources
☐ Allow engineers to opt out temporarily
☐ Increase compensation
```

**2. Reduce page volume:**
```
☐ Aggressive alert tuning
☐ Fix recurring incidents (root cause)
☐ Implement auto-remediation
☐ Improve system reliability
☐ Defer non-critical alerts to business hours
```

**3. Structural changes:**
```
☐ Hire more engineers for rotation
☐ Reduce service scope
☐ Implement follow-the-sun model
☐ Change to hybrid on-call model
☐ Split services for separate rotations
```

**4. Recovery and support:**
```
☐ Compensatory time off after incidents
☐ Mental health and wellness programs
☐ Regular check-ins with on-call engineers
☐ Normalize taking breaks from rotation
☐ Celebrate and recognize on-call work
```

**Leadership responsibility:**
- Acknowledge the problem openly
- Take concrete action quickly
- Invest in long-term reliability
- Protect team well-being
- Be willing to slow feature development if needed

### Challenge: Rotation Coverage Gaps

**Symptoms:**
- Difficulty finding coverage for shifts
- PTO causing coverage problems
- Last-minute scrambling for coverage
- Same engineers covering repeatedly
- Resentment about unfair distribution

**Root causes:**
- Team too small
- Inadequate training pipeline
- Unfair distribution
- Lack of process for coverage
- Engineers avoiding on-call

**Solutions:**

**1. Grow the rotation:**
```
☐ Accelerate onboarding/training
☐ Hire with on-call in mind
☐ Reduce exemptions
☐ Include senior engineers and managers
☐ Cross-train from related teams
```

**2. Improve coverage process:**
```
☐ Clear policy for PTO and coverage
☐ Swap process in on-call tool
☐ Advance notice requirements
☐ Team calendar visibility
☐ Coverage "marketplace" or board
```

**3. Make on-call more attractive:**
```
☐ Improve compensation
☐ Reduce page volume
☐ Better training and support
☐ Recognition and appreciation
☐ Career benefits for participation
```

**4. Fair distribution:**
```
☐ Track shifts per person over time
☐ Identify and address imbalances
☐ Rotate undesirable shifts (holidays)
☐ No permanent exemptions without reason
```

### Challenge: Poor Incident Response Coordination

**Symptoms:**
- Confusion during incidents
- Unclear roles and responsibilities
- Poor communication
- Delayed decisions
- Chaotic response

**Root causes:**
- Unclear incident response process
- Lack of role definitions
- Insufficient IC training
- No practice or drills
- Cultural resistance to process

**Solutions:**

**1. Define clear process:**
```
☐ Document incident response playbook
☐ Define roles (IC, Tech Lead, Comms, Scribe)
☐ Create severity definitions
☐ Establish communication patterns
☐ Set escalation criteria
```

**See:** guides/incident_response_playbook.md

**2. Train incident commanders:**
```
☐ IC training program
☐ Shadowing and mentorship
☐ Practice drills
☐ Debrief after incidents
☐ Resources and support
```

**See:** reference/incident_roles_reference.md

**3. Practice regularly:**
```
☐ Monthly or quarterly GameDays
☐ Simulated incidents
☐ Role rotation practice
☐ Test communication channels
☐ Review and improve
```

**4. Improve during incidents:**
```
☐ IC explicitly assigns roles
☐ Clear communication channel
☐ Regular status updates
☐ Document decisions and actions
☐ Debrief after resolution
```

---

## Building Cultural Practices

### Blameless Post-Mortems

**Why it matters:**
- Encourages honesty and transparency
- Focuses on system improvements
- Builds psychological safety
- Enables learning
- Reduces fear and stress

**How to build blameless culture:**

**1. Leadership modeling:**
- Leaders acknowledge their own mistakes
- Leaders participate in post-mortems
- Leaders enforce blamelessness
- Leaders invest in learning

**2. Training and education:**
- Explain why blameless matters
- Train facilitators
- Provide examples
- Practice in low-stakes situations

**3. Process and structure:**
- Use blameless post-mortem template
- Trained facilitators
- Focus on contributing factors, not individuals
- Action items on systems, not people

**4. Consistency:**
- Every post-mortem is blameless
- Intervene when blame appears
- Reinforce regularly
- No exceptions

**See:** reference/post_mortem_process.md and guides/running_effective_post_mortems.md

### GameDays and Practice

**Purpose:**
- Practice incident response in low-stakes environment
- Test runbooks and procedures
- Train new engineers
- Identify gaps
- Build team cohesion and confidence

**GameDay format:**

**Preparation:**
```
☐ Choose realistic failure scenario
☐ Prepare environment
☐ Assign roles (or let team self-organize)
☐ Set up monitoring and communication
☐ Designate observers
☐ Schedule debrief time
```

**Execution:**
```
1. Inject failure (announced or surprise)
2. Team responds as they would to real incident
3. Observers note process gaps and effectiveness
4. Allow scenario to play out
5. Resolve or call time after learning achieved
```

**Debrief:**
```
☐ What went well?
☐ What was challenging?
☐ What did we learn?
☐ What should we improve?
☐ Action items
```

**Frequency:**
- Monthly for teams new to on-call
- Quarterly for established teams
- After major process changes
- Before high-traffic periods (holiday prep)

**Scenarios to practice:**
```
- Database failover
- Regional outage
- Cascading failure
- Deployment rollback
- Traffic spike/DDoS
- Third-party service outage
- Security incident
- Data corruption
```

### Recognition and Appreciation

**Why it matters:**
- On-call is demanding and often thankless
- Recognition builds morale
- Appreciation encourages participation
- Celebrates good behavior

**How to recognize:**

**During incidents:**
- IC thanks team at resolution
- Public appreciation in incident channel
- Acknowledge good escalation decisions
- Recognize effective collaboration

**After incidents:**
- Shout-outs in team meetings
- Recognition in post-mortems (what went well)
- Thank individuals personally
- Highlight in retrospectives

**Ongoing:**
- Monthly on-call MVP or highlight
- Share great incident responses broadly
- Include in performance reviews
- Celebrate reliability improvements from action items

**Compensation and benefits:**
- Fair financial compensation
- Generous time-off policies
- Flexibility in work schedule
- Career development opportunities
- Special perks (meals, transportation)

### Continuous Learning

**Build learning into the culture:**

**1. Post-mortem database:**
- Searchable repository of all post-mortems
- Tagged by service, root cause, patterns
- Used in onboarding and training
- Referenced in similar incidents

**2. Learning sessions:**
- Monthly "Interesting Incidents" meeting
- Share lessons across teams
- Discuss patterns and trends
- Celebrate good learnings

**3. Documentation culture:**
- Writing runbooks is valued work
- Time allocated for documentation
- Documentation quality recognized
- Gaps identified and filled

**4. Knowledge sharing:**
- Architecture deep dives
- Tool and technique sharing
- Cross-team learning
- External learning (conferences, blogs)

---

## Leadership Responsibilities

### What Engineering Leaders Must Do

**1. Set the tone:**
```
☐ Model blameless culture
☐ Participate in on-call (at appropriate level)
☐ Prioritize reliability work
☐ Celebrate learning and transparency
☐ Protect team well-being
```

**2. Provide resources:**
```
☐ Adequate staffing for sustainable rotation
☐ Budget for tools and training
☐ Time for reliability improvements
☐ Support during incidents
☐ Fair compensation
```

**3. Monitor health:**
```
☐ Review on-call metrics regularly
☐ Talk to on-call engineers
☐ Act on feedback quickly
☐ Intervene when problems emerge
☐ Balance reliability and feature work
```

**4. Drive improvement:**
```
☐ Follow up on post-mortem action items
☐ Invest in automation and tooling
☐ Remove barriers and blockers
☐ Allocate time for training
☐ Measure and track progress
```

**5. Build culture:**
```
☐ Recognize and appreciate on-call work
☐ Normalize escalation and asking for help
☐ Encourage learning and experimentation
☐ Create psychological safety
☐ Foster team cohesion
```

### Red Flags to Watch For

**Immediate action needed:**
- Engineer burnout or mental health crisis
- Sustained high page volume (>5 per shift)
- Multiple engineers wanting to leave rotation
- Safety or security incidents due to fatigue
- Team morale collapse

**Address promptly:**
- Increasing page volume trend
- Rising false positive rate
- Coverage gaps becoming frequent
- On-call satisfaction scores declining
- Action items not being completed
- Repeat incidents not being fixed

**Monitor and improve:**
- Escalation rate increasing
- Time to mitigation increasing
- Runbooks becoming outdated
- Training pipeline slowing
- Alert quality degrading

---

## Measuring Success

### Healthy On-Call Looks Like

**Quantitative indicators:**
```
✓ Pages per shift: <2 per 12 hours
✓ False positive rate: <25%
✓ On-call satisfaction: >3.5/5
✓ Action item completion: >80%
✓ Coverage gaps: <5%
✓ Escalation success: Issues resolved effectively
✓ Time to mitigation: Stable or decreasing
```

**Qualitative indicators:**
```
✓ Engineers willing to participate in rotation
✓ Positive feedback about on-call experience
✓ Team feels supported and prepared
✓ Learning from incidents happens consistently
✓ Blameless culture is strong
✓ New engineers ramping successfully
✓ Work-life balance is maintained
```

### Long-Term Goals

**Year 1:**
- Establish sustainable rotation
- Build comprehensive runbooks
- Tune alerts to reasonable volume
- Train full team
- Blameless culture taking root

**Year 2:**
- Significant automation implemented
- Page volume declining
- Incident response highly effective
- Team satisfaction high
- Reliability improving measurably

**Year 3:**
- On-call is rarely disruptive
- Most issues self-heal
- Incidents are learning opportunities
- Team is proud of reliability
- Industry-leading practices

---

## Resources and Templates

### Internal Resources
```
☐ Incident response playbook: guides/incident_response_playbook.md
☐ Post-mortem process: reference/post_mortem_process.md
☐ On-call best practices: reference/on_call_best_practices.md
☐ Severity definitions: reference/incident_severity_levels.md
☐ Role definitions: reference/incident_roles_reference.md
```

### External Resources

**Books:**
- "Site Reliability Engineering" (Google)
- "The Site Reliability Workbook" (Google)
- "Seeking SRE" (Various authors)
- "The Phoenix Project" (Gene Kim)

**Online:**
- PagerDuty Incident Response Documentation
- Atlassian Incident Management Handbook
- Etsy Debriefing Facilitation Guide
- Honeycomb.io Blog on Observability

**Communities:**
- SREcon conferences (USENIX)
- DevOps Enterprise Summit
- SRE Slack communities
- Local SRE meetups

---

## Summary: Building Blocks of Healthy On-Call

**Foundation:**
1. Adequate team size (8-10+ people)
2. Fair rotation and compensation
3. Clear process and documentation
4. Effective tools and monitoring

**Culture:**
1. Blameless post-mortems
2. Psychological safety
3. Learning mindset
4. Recognition and appreciation

**Continuous Improvement:**
1. Regular metrics review
2. Alert tuning and automation
3. Runbook maintenance
4. Training and GameDays

**Leadership:**
1. Model desired behavior
2. Provide resources
3. Monitor and intervene
4. Celebrate and recognize

**The Goal:**
On-call that is sustainable, effective, and respected—where engineers feel prepared, supported, and valued, and where incidents drive continuous improvement in reliability.

---

**Last Updated:** November 2025
**Questions or Feedback:** [Your internal contact]
**Review Frequency:** Quarterly
