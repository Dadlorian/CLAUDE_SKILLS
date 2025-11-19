# Post-Mortem Process Reference

## Overview

Post-mortems (also called incident reviews or retrospectives) are structured learning opportunities following significant incidents. This reference outlines a blameless post-mortem framework based on Google SRE and industry best practices.

---

## Core Principles

### 1. Blameless Culture

**Definition:** Focus on system failures and process gaps, not individual mistakes.

**Why Blameless Matters:**
- Humans will make mistakes; systems should be resilient to human error
- Blame discourages honesty and transparency
- Fear of blame leads to hiding problems
- System improvements prevent recurrence better than punishing individuals

**What Blameless Means:**
- Assume good intentions
- Focus on "what happened" not "who did it"
- Ask "how did the system allow this?" not "why did you do that?"
- Identify contributing factors, not single causes
- Celebrate learning and transparency

**What Blameless Does NOT Mean:**
- Absence of accountability
- Ignoring negligence or malicious behavior
- Avoiding difficult conversations
- Lowering standards or expectations

### 2. Learning Over Punishment

**Goals of Post-Mortems:**
1. Understand what happened and why
2. Prevent recurrence through system improvements
3. Share knowledge across the organization
4. Improve incident response processes
5. Build organizational resilience

**Not Goals:**
- Find someone to blame
- Satisfy executive anger
- Create appearance of control
- Produce documentation no one reads

### 3. Action-Oriented Outcomes

**Every post-mortem should produce:**
- Clear timeline of events
- Root cause analysis (often multiple contributing factors)
- Actionable items with owners and deadlines
- Lessons that can be applied to other systems

**Follow-Through:**
- Action items must be tracked and completed
- Review action item completion rate as team metric
- Incomplete action items indicate process failure

---

## When to Conduct Post-Mortems

### Required Post-Mortems

**Always conduct post-mortem for:**
- SEV-1 incidents (within 48 hours)
- SEV-2 incidents (within 1 week)
- Any incident with customer data loss or exposure
- Security incidents or breaches
- SLA/SLO violations
- Incidents causing significant business impact

**Consider post-mortem for:**
- SEV-3 incidents with interesting lessons
- Near-misses that could have been severe
- Repeated issues indicating systemic problems
- Novel failure modes
- Incidents revealing documentation or process gaps

**Skip post-mortem for:**
- Routine SEV-3/SEV-4 incidents
- Issues with clear cause and simple fix already implemented
- Incidents with no broader lessons to learn

### Timing

**Ideal Timeline:**
- **SEV-1:** Post-mortem meeting within 2-3 business days
- **SEV-2:** Post-mortem meeting within 5 business days
- **SEV-3:** Optional, schedule as needed

**Why Not Immediate:**
- Allow time for stress to subside
- Gather complete data and logs
- Prepare draft timeline
- Schedule attendees thoughtfully

**Why Not Too Late:**
- Memory fades quickly
- Details become unclear
- Urgency diminishes
- People move to other priorities

---

## Post-Mortem Process

### Phase 1: Preparation (Before the Meeting)

**Assign Facilitator:**
- Should NOT be the Incident Commander (potential bias)
- Trained in facilitation and blameless culture
- Responsible for keeping discussion productive
- Typically: SRE lead, engineering manager, or designated facilitator

**Draft Timeline:**
- Scribe provides detailed timeline from incident
- Include: timestamps, actions taken, decisions made, communications sent
- Note: hypotheses tested, dead ends, discoveries
- Attach: relevant graphs, logs, screenshots

**Gather Data:**
```
☐ Complete incident timeline
☐ Alert and monitoring data
☐ System metrics and graphs
☐ Logs from affected systems
☐ Communication transcripts
☐ Customer impact data
☐ Configuration changes made
☐ Deployment/change history
```

**Invite Attendees:**
- Incident response team (IC, Tech Leads, Comms Lead)
- Subject matter experts
- Engineering leadership
- Representatives from affected teams
- Optional: Broader team for learning (view-only)

**Typical attendee size:** 6-12 active participants

**Distribute Pre-Read:**
- Send draft timeline 24-48 hours before meeting
- Include preliminary data and graphs
- Set expectation: attendees should review before meeting

### Phase 2: The Post-Mortem Meeting

**Duration:** 60-90 minutes (schedule 2 hours for SEV-1)

**Agenda:**

**1. Set the Stage (5 minutes)**
- Facilitator reminds everyone: blameless culture
- Review goals: learn, improve, prevent recurrence
- Establish ground rules for discussion
- Note: meeting is confidential safe space (if appropriate)

**2. Timeline Review (15-20 minutes)**
- Walk through incident from detection to resolution
- Clarify any timeline gaps or uncertainties
- Ensure shared understanding of what happened
- Focus on facts, not interpretations yet

**3. Root Cause Analysis (20-30 minutes)**
- Discuss contributing factors (usually multiple)
- Use "5 Whys" or similar techniques
- Identify system weaknesses exposed
- Discuss what went well (positive patterns to reinforce)
- Document assumptions that proved incorrect

**4. What Went Well (10 minutes)**
- Acknowledge effective responses
- Identify practices to preserve and amplify
- Recognize team members who helped (without blame to others)
- Examples: good communication, effective escalation, quick mitigation

**5. What Could Be Improved (15-20 minutes)**
- Brainstorm improvements (don't edit ideas yet)
- Consider: detection, response, recovery, communication
- Think broadly: tools, processes, documentation, architecture
- Capture all ideas, prioritize later

**6. Action Items (15-20 minutes)**
- Convert improvements into specific, actionable items
- Assign owner to each action item
- Set realistic deadlines
- Categorize by priority (critical, important, nice-to-have)
- Identify quick wins vs. longer-term efforts

**7. Lessons Learned (5-10 minutes)**
- Summarize key takeaways
- Identify knowledge to share more broadly
- Note: patterns that might apply to other systems
- Determine what to include in written post-mortem

**Facilitator Responsibilities:**
```
- Keep discussion on track and on time
- Intervene if discussion becomes blameful
- Ensure all voices are heard
- Park off-topic discussions for later
- Manage strong personalities
- Draw out quiet participants
- Capture action items clearly
- End on positive note
```

### Phase 3: Documentation (After the Meeting)

**Written Post-Mortem Template:**
(See templates/post_mortem_template.md for full template)

**Key Sections:**
1. **Summary:** High-level overview (2-3 paragraphs)
2. **Impact:** Quantify customer and business impact
3. **Timeline:** Detailed sequence of events
4. **Root Cause:** Contributing factors (often multiple)
5. **What Went Well:** Effective responses and patterns
6. **What Went Wrong:** Failures and gaps
7. **Action Items:** Specific improvements with owners and deadlines
8. **Lessons Learned:** Broader takeaways

**Writing Best Practices:**
- Use clear, objective language
- Avoid blame or judgment
- Be specific with facts and data
- Include visuals (graphs, diagrams)
- Make it skimmable (use headers, bullets, formatting)
- Link to supporting materials

**Review Process:**
```
1. Draft author (often facilitator or IC): Initial draft
2. Incident response team: Review for accuracy
3. Engineering leadership: Review for completeness
4. Broader team: Optional review for clarity
5. Final approval and publication
```

**Timeline for Publication:**
- Draft within 2-3 days of post-mortem meeting
- Reviews complete within 1 week
- Published within 10 days of incident for SEV-1
- Published within 2 weeks for SEV-2

### Phase 4: Sharing and Learning

**Internal Distribution:**
- Email to engineering organization
- Post in team wiki or knowledge base
- Announce in engineering all-hands
- Discuss in team meetings

**Optional External Distribution:**
- Public blog post (sanitized for proprietary information)
- Conference presentation
- Industry post-mortem sharing (SREcon, etc.)

**Learning Activities:**
- Include in onboarding materials for new engineers
- Reference in architecture reviews
- Use in training and GameDay scenarios
- Build pattern library of common failure modes

### Phase 5: Action Item Tracking

**Tracking System:**
- Create tickets in project management system
- Tag with "post-mortem" and incident ID
- Assign owners (already determined in meeting)
- Set deadlines (already determined in meeting)
- Link back to post-mortem document

**Follow-Up:**
- Review action items in weekly team meetings
- Monthly report on action item completion rate
- Escalate blocked or overdue items
- Celebrate completed improvements

**Accountability:**
- Action item completion is part of team metrics
- Low completion rate is a red flag
- Engineering leadership should remove blockers
- Re-prioritize other work if needed to complete action items

---

## Root Cause Analysis Techniques

### The 5 Whys

**Process:**
1. Start with the problem
2. Ask "Why did this happen?"
3. Ask "Why?" again for each answer
4. Continue 5 levels deep (or until you reach root cause)
5. Identify actionable improvements at multiple levels

**Example:**
```
Problem: Service went down
Why? Database ran out of connections
Why? Connection pool was exhausted
Why? Application wasn't closing connections properly
Why? Recent code change introduced connection leak
Why? Code review didn't catch the leak
Root causes to address:
- Fix the connection leak (immediate)
- Add connection leak detection to tests (short-term)
- Improve code review process for resource management (long-term)
- Add alerting for connection pool exhaustion (prevention)
```

**Pitfalls:**
- Stopping too early ("human error" is not a root cause)
- Assuming single root cause (usually multiple)
- Focusing on blame instead of systems

### Fishbone (Ishikawa) Diagram

**Categories:**
- People
- Process
- Technology
- Environment
- Management

**Process:**
1. Draw main problem at "head" of fish
2. Draw "bones" for each category
3. Brainstorm contributing factors in each category
4. Identify which factors to address

**Best For:** Complex incidents with multiple contributing factors

### Timeline Analysis

**Process:**
1. Create detailed timeline
2. Identify critical decision points
3. Note what information was available at each point
4. Identify where different decisions could have changed outcome
5. Focus improvements on decision points

**Best For:** Understanding incident response effectiveness

### Fault Tree Analysis

**Process:**
1. Start with the failure event
2. Identify immediate causes
3. For each cause, identify its causes
4. Continue building tree until reaching root causes
5. Calculate probabilities (if data available)
6. Prioritize addressing high-probability paths

**Best For:** Systematic failure analysis, prevention planning

---

## Common Post-Mortem Anti-Patterns

### 1. The Blame Game

**Symptoms:**
- Focus on who made the mistake
- Defensive behavior from participants
- Reluctance to share information
- "Scapegoat" identified

**Remediation:**
- Facilitator intervenes immediately
- Redirect to system failures
- Reinforce blameless culture
- Private coaching for blameful participants

### 2. The Rubber Stamp

**Symptoms:**
- Surface-level analysis
- Action items are vague or token gestures
- No real commitment to change
- Post-mortem viewed as checkbox exercise

**Remediation:**
- Leadership demonstrates commitment to learning
- Track and review action item completion
- Celebrate when action items prevent future incidents
- Hold teams accountable for shallow post-mortems

### 3. The Novel

**Symptoms:**
- Post-mortem document is 20+ pages
- Excessive technical detail
- No one reads it
- Key insights buried in minutiae

**Remediation:**
- Use executive summary
- Separate detailed timeline into appendix
- Focus on learning and actions
- Use visual aids instead of dense text

### 4. The Action Item Graveyard

**Symptoms:**
- Long list of action items
- No clear owners or deadlines
- Action items never completed
- Same issues recur in future incidents

**Remediation:**
- Limit action items to realistic number (5-10 max)
- Ensure clear ownership
- Track completion as team metric
- Review incomplete action items monthly

### 5. The Blame-the-Tools Fallacy

**Symptoms:**
- Everything blamed on tooling
- No examination of processes or architecture
- Action items are all "buy new tools"
- Ignore human factors and design issues

**Remediation:**
- Look deeper than tools
- Consider process and architecture
- Examine how tools are used, not just what tools exist
- Balance tool improvements with other changes

### 6. The Hindsight Hero

**Symptoms:**
- Analysis based on information not available during incident
- "Should have known" statements
- Unrealistic expectations for responders
- Ignore time pressure and uncertainty during incident

**Remediation:**
- Clearly distinguish information available at each point
- Acknowledge uncertainty responders faced
- Focus on improving information availability
- Avoid "should have" language

---

## Measuring Post-Mortem Effectiveness

### Process Metrics

**Completion Metrics:**
```
- % of SEV-1/SEV-2 incidents with completed post-mortems
- Average time from incident to post-mortem publication
- Action item completion rate
- Average number of action items per post-mortem
```

**Targets:**
- 100% of SEV-1/SEV-2 have post-mortems
- Published within 2 weeks
- >80% action item completion within deadline
- 5-10 action items per post-mortem (Goldilocks zone)

### Outcome Metrics

**Learning Indicators:**
```
- Reduction in repeat incidents
- Decreased time to mitigation (learning applied)
- Increased incident detection speed
- Improved response coordination
```

**Cultural Indicators:**
```
- Team participation in post-mortems
- Candor and honesty in discussions
- Willingness to admit mistakes
- Positive feedback on process
```

### Quality Assessment

**Post-Mortem Quality Rubric:**

**Excellent (5/5):**
- Clear, complete timeline
- Thorough root cause analysis
- Specific, actionable improvements
- Blameless and honest
- Broader lessons identified
- Action items completed

**Good (4/5):**
- Complete timeline
- Root cause identified
- Clear action items
- Blameless tone
- Most action items completed

**Adequate (3/5):**
- Timeline present
- Some analysis
- Action items listed
- Generally blameless
- Some action items completed

**Poor (2/5):**
- Incomplete timeline
- Shallow analysis
- Vague action items
- Hints of blame
- Few action items completed

**Inadequate (1/5):**
- Minimal documentation
- No real analysis
- No action items or all incomplete
- Blameful or defensive

---

## Special Post-Mortem Scenarios

### Security Incidents

**Additional Considerations:**
- Confidentiality and need-to-know
- Legal and compliance requirements
- Customer notification obligations
- Law enforcement involvement
- External disclosure timing

**Modified Process:**
- Limit attendees to cleared personnel
- Sanitize documentation before broader sharing
- Coordinate with legal, compliance, security teams
- May require separate internal and external post-mortems

### Customer Data Loss/Exposure

**Additional Focus:**
- Extent of data impact (quantify precisely)
- Customer notification requirements
- Regulatory reporting (GDPR, etc.)
- Credit monitoring or remediation offers
- PR and communications strategy

**Action Item Priorities:**
- Immediate: Prevent further exposure
- Short-term: Customer remediation
- Long-term: Architectural improvements

### Third-Party/Vendor Outages

**Special Considerations:**
- Limited control over root cause
- Focus on resilience and dependency management
- Vendor communication and post-mortem sharing

**Action Items Focus:**
- Improve monitoring of third-party dependencies
- Build resilience to third-party failures
- Establish vendor SLAs and escalation paths
- Consider redundancy or alternatives

### Multi-Team Incidents

**Facilitation Challenges:**
- Larger group dynamics
- Different team cultures
- Cross-team blame potential
- Shared ownership of action items

**Best Practices:**
- Neutral facilitator (not from involved teams)
- Emphasize cross-team learning
- Create action items for each team
- Follow up on cross-team coordination improvements

---

## Building Post-Mortem Culture

### Leadership Role

**Leaders Should:**
- Participate in post-mortems (not just delegate)
- Model blameless behavior
- Allocate time for action item completion
- Celebrate learning and transparency
- Share their own mistakes and lessons

**Leaders Should NOT:**
- Use post-mortems to assign blame
- Pressure teams to minimize severity or impact
- Ignore action items or treat them as optional
- Punish honesty or transparency

### Training and Enablement

**Facilitator Training:**
- Blameless culture principles
- Meeting facilitation skills
- Root cause analysis techniques
- Conflict resolution
- Bias awareness

**Team Training:**
- Why blameless culture matters
- How to participate effectively
- Root cause analysis basics
- Writing clear action items

### Celebrating Learning

**Recognition:**
- Highlight great post-mortems in all-hands
- Share interesting lessons broadly
- Reward teams that improve based on learnings
- Celebrate prevented incidents (action items that worked)

**Knowledge Sharing:**
- Monthly "post-mortem highlights" newsletter
- Quarterly learning sessions
- Annual "best of" post-mortem review
- Public blog posts (with permission)

---

## Templates and Tools

### Documentation Templates
- See: templates/post_mortem_template.md
- Customize for your organization
- Include required fields for compliance
- Balance structure with flexibility

### Facilitation Tools
- **Shared Documents:** Google Docs, Confluence
- **Collaboration:** Mural, Miro for virtual workshops
- **Timeline Tools:** Incident.io, FireHydrant
- **Action Tracking:** Jira, Linear, GitHub Issues

### Recommended Reading
- **Google SRE Book:** "Postmortem Culture: Learning from Failure"
- **Etsy's Debriefing Facilitation Guide**
- **"The Field Guide to Understanding Human Error"** by Sidney Dekker
- **"Seeking SRE"** - Chapter on Learning from Failure

---

## Continuous Improvement

### Review Your Post-Mortem Process

**Quarterly Reviews:**
```
☐ Review post-mortem completion rates
☐ Assess action item completion rates
☐ Gather team feedback on process
☐ Identify common failure patterns
☐ Update templates and guidelines
☐ Recognize great post-mortems
```

**Annual Deep Dive:**
```
☐ Analyze all post-mortems from the year
☐ Identify systemic patterns
☐ Assess cultural health
☐ Update training materials
☐ Benchmark against industry practices
☐ Set goals for next year
```

### Meta-Learning

**Questions to Ask:**
- Are we learning from incidents?
- Are repeat incidents decreasing?
- Is our incident response improving?
- Are teams engaged in the process?
- Are action items making a difference?

**Adapt and Evolve:**
- No single process fits all organizations
- Tailor to your team size, maturity, culture
- Experiment with improvements
- Measure and iterate

---

## Appendix: Post-Mortem Checklist

### Preparation
```
☐ Assign facilitator
☐ Draft timeline from incident notes
☐ Gather all relevant data and artifacts
☐ Invite appropriate attendees
☐ Distribute pre-read materials 24-48h before
☐ Schedule 90-120 minutes
☐ Book room/video conference
```

### Meeting
```
☐ Set blameless tone
☐ Review timeline
☐ Conduct root cause analysis
☐ Discuss what went well
☐ Identify improvement areas
☐ Create action items with owners and deadlines
☐ Summarize lessons learned
```

### Documentation
```
☐ Write post-mortem document
☐ Review with incident response team
☐ Review with leadership
☐ Publish to knowledge base
☐ Share with broader organization
```

### Follow-Up
```
☐ Create tickets for all action items
☐ Track action items in team meetings
☐ Review monthly completion rate
☐ Celebrate improvements implemented
☐ Reference in future similar incidents
```

---

**Last Updated:** November 2025
**Review Frequency:** Quarterly
**Owned By:** SRE Leadership Team
