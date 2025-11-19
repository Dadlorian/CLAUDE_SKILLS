# GameDay Planning Guide

## Overview

A GameDay (also called a Chaos Day, Failure Friday, or Resilience Exercise) is a scheduled, team-wide chaos engineering event where you deliberately introduce failures into your system to test resilience, improve incident response, and build team confidence. This guide covers everything you need to plan and execute successful GameDays.

## What is a GameDay?

**Definition**: A planned event where teams intentionally inject failures into a system to validate resilience, practice incident response, and discover weaknesses in a controlled environment.

**Key Characteristics**:
- Scheduled in advance (not surprise)
- All relevant stakeholders participate
- Runs during business hours
- Simulates real-world failure scenarios
- Focuses on learning, not blame
- Documented with action items

**GameDay vs. Regular Chaos Experiments**:

| Aspect | Regular Chaos | GameDay |
|--------|---------------|---------|
| Frequency | Continuous/Daily | Monthly/Quarterly |
| Scope | Single experiment | Multiple scenarios |
| Participation | 1-2 engineers | Entire team |
| Duration | Minutes | 2-4 hours |
| Complexity | Simple failures | Complex scenarios |
| Focus | Automation | Team response |
| Documentation | Experiment log | Full after-action report |

---

## Benefits of GameDays

### Technical Benefits
- Validate disaster recovery procedures
- Test monitoring and alerting
- Verify auto-scaling and healing
- Practice incident response
- Discover unknown dependencies
- Validate runbooks

### Team Benefits
- Build confidence in system resilience
- Practice communication during incidents
- Cross-train team members
- Reduce incident stress
- Improve collaboration
- Build shared mental models

### Organizational Benefits
- Demonstrate proactive reliability investment
- Reduce MTTR (Mean Time To Recovery)
- Lower incident frequency
- Improve customer experience
- Build customer trust
- Meet compliance requirements

---

## GameDay Types

### 1. Internal GameDay
**Purpose**: Test technical systems and team response
**Participants**: Engineering team, SRE, platform team
**Scope**: Infrastructure and application failures
**Duration**: 2-3 hours

### 2. Cross-Team GameDay
**Purpose**: Test coordination between multiple teams
**Participants**: Multiple engineering teams, DevOps, SRE
**Scope**: Multi-service failures, cascading failures
**Duration**: 3-4 hours

### 3. Full-Scale GameDay
**Purpose**: Test entire organization's incident response
**Participants**: Engineering, Support, Customer Success, Leadership
**Scope**: Major outage scenarios, region failures
**Duration**: 4-8 hours (sometimes full day)

### 4. Compliance GameDay
**Purpose**: Demonstrate disaster recovery capabilities
**Participants**: Engineering, Security, Compliance, Auditors
**Scope**: Regulatory required scenarios
**Duration**: Varies (often 2-4 hours)

### 5. External GameDay (Advanced)
**Purpose**: Test with real customer impact
**Participants**: All stakeholders + selected customers
**Scope**: Controlled production failures with customer awareness
**Duration**: Varies

---

## GameDay Planning Timeline

### 6-8 Weeks Before: Initial Planning

**Define Objectives**:
```
□ What do we want to learn?
□ What scenarios should we test?
□ What systems are in scope?
□ What is out of scope?
□ What success looks like?
```

**Select Scenarios**:
```
Choose 3-5 scenarios based on:
- Highest risk to business
- Most likely to occur
- Never tested before
- Recent incidents to replay
- Regulatory requirements
```

**Form GameDay Team**:
```
Roles needed:
- GameDay Leader (orchestrates entire event)
- Chaos Operators (execute failures)
- Observers (monitor systems)
- Scribes (document events)
- Subject Matter Experts (domain knowledge)
- Executive Sponsor (provides air cover)
```

### 4 Weeks Before: Detailed Planning

**Create Scenario Scripts**:
```markdown
# Scenario Template
## Scenario: Database Primary Failure

### Objective
Test automatic failover to database replica

### Duration
15 minutes

### Failure Injection
- Action: Force failover of RDS primary
- Tool: AWS FIS
- Blast radius: Production database (multi-AZ)

### Expected Behavior
- Automatic failover completes in < 60 seconds
- Application reconnects automatically
- No manual intervention required
- < 1 minute of degraded service

### Success Criteria
- Failover completes successfully
- Data consistency maintained
- Application recovers without restart
- MTTR < 2 minutes

### Rollback Plan
- Promote original primary back
- Verify replication sync
- Manual application restart if needed
```

**Logistics Planning**:
```
□ Book conference room / video call
□ Reserve time on team calendars
□ Prepare required tools and access
□ Set up monitoring dashboards
□ Prepare communication templates
□ Order food/refreshments (if in-person)
```

### 2 Weeks Before: Dry Run

**Test Your Tests**:
```
□ Run all scenarios in staging
□ Verify monitoring captures events
□ Test rollback procedures
□ Validate communication channels
□ Time each scenario
□ Adjust scenarios based on results
```

**Communication**:
```
Notify:
□ Engineering teams
□ Customer support
□ Product management
□ Executive leadership
□ Any external stakeholders
```

### 1 Week Before: Final Prep

**Pre-GameDay Checklist**:
```
□ All scenarios tested in staging
□ Team roles assigned
□ Tools and access verified
□ Dashboards configured
□ Communication channels set up
□ Runbooks accessible
□ Incident response procedures reviewed
□ Observers trained
□ Recording tools ready (screen recording, notes)
```

**Pre-GameDay Email Template**:
```
Subject: GameDay - [Date] - [Time] - Final Reminder

Team,

Our GameDay is scheduled for [Date] at [Time].

What: Chaos Engineering GameDay
When: [Date], [Start Time] - [End Time]
Where: [Room/Video Link]

Objectives:
1. Test database failover procedures
2. Validate multi-region routing
3. Practice incident communication

Scenarios (3 planned):
1. Database primary failure (15 min)
2. Availability zone outage (20 min)
3. API dependency failure (15 min)

What to bring:
- Laptop with production access
- Monitoring dashboards bookmarked
- Runbooks accessible

Important:
- This is a LEARNING exercise, not a test
- Blameless environment
- Ask questions and speak up
- Document everything

See you there!
[Your Name]
```

---

## GameDay Day-Of Structure

### Pre-GameDay (30 minutes before)

**Setup Checklist**:
```
□ All participants joined
□ Dashboards projected/shared
□ Communication channels open (Slack, Teams)
□ Recording started
□ Roles confirmed
□ Tools ready
□ Last-minute system health check
```

### Kickoff (15 minutes)

**Agenda**:
```
1. Welcome and objectives (5 min)
2. Review GameDay principles (3 min)
3. Explain scenarios (5 min)
4. Answer questions (2 min)
```

**GameDay Principles to Emphasize**:
```
1. Blameless environment - focus on systems, not people
2. Speak up immediately if you see issues
3. Document everything
4. It's OK to pause or stop scenarios
5. Learning is the goal
6. Have fun!
```

**Kickoff Script Example**:
```
"Welcome everyone! Today we're running a GameDay to test our
system's resilience and practice our incident response.

We have 3 scenarios planned over the next 2 hours. Each scenario
will simulate a real failure that could happen in production.

Remember:
- This is about learning, not pointing fingers
- Speak up if you see anything concerning
- We can stop at any time
- Take notes on what works and what doesn't

Our objectives today are:
1. Verify our database failover works as expected
2. Test our multi-region failover procedures
3. Validate our API dependency circuit breakers

Let's begin with a system health check..."
```

### Scenario Execution (Loop for Each Scenario)

**Scenario Pattern** (20 minutes per scenario):

**1. Pre-Scenario Brief (3 minutes)**:
```
- Describe the scenario
- State expected behavior
- Identify key metrics to watch
- Review abort conditions
- Answer questions
```

**2. Inject Failure (1 minute)**:
```
- Announce "Injecting failure NOW"
- Execute chaos action
- Note exact timestamp
- Confirm failure is active
```

**3. Observe and Respond (10 minutes)**:
```
- Watch dashboards
- Monitor alerts
- Follow incident response procedures
- Document observations
- Allow team to respond naturally
```

**4. Recovery (3 minutes)**:
```
- Stop chaos injection
- Verify system recovery
- Check all metrics return to normal
- Confirm no residual effects
```

**5. Debrief (3 minutes)**:
```
- What happened?
- Expected vs. actual behavior
- What worked well?
- What needs improvement?
- Capture action items
```

### Observer Responsibilities During Scenarios

**Real-Time Observation Checklist**:
```
□ Timestamp when failure injected
□ Timestamp when alerts fired
□ Timestamp when team acknowledged
□ Actions taken by team
□ Communication quality
□ Metrics during failure
□ Unexpected behaviors
□ Time to recovery
□ Manual interventions needed
```

**Observer Note Template**:
```
Scenario: [Name]
Start Time: [HH:MM:SS]
End Time: [HH:MM:SS]

Timeline:
- [HH:MM:SS] Failure injected
- [HH:MM:SS] Alert fired (which alert?)
- [HH:MM:SS] Team acknowledged
- [HH:MM:SS] [Action taken]
- [HH:MM:SS] System recovered

Observations:
- [What worked]
- [What didn't work]
- [Surprises]
- [Communication notes]

Metrics:
- Error rate: [normal] → [peak] → [recovery]
- Latency: [normal] → [peak] → [recovery]
- MTTR: [X minutes]

Action Items:
- [ ] [Fix/improvement needed]
```

### Mid-GameDay Break (15 minutes)

**After 2 scenarios, take a break**:
```
- Stretch break
- Discuss findings so far
- Adjust remaining scenarios if needed
- Re-energize the team
```

### Wrap-Up (15 minutes)

**Immediate Retrospective**:
```
1. Review all scenarios (5 min)
2. Capture top learnings (5 min)
3. Identify action items (3 min)
4. Thank participants (2 min)
```

**Questions to Discuss**:
```
- What surprised us today?
- What worked better than expected?
- What worked worse than expected?
- What should we do differently?
- What should we test next time?
- How did our team communication work?
```

---

## GameDay Roles and Responsibilities

### GameDay Leader
**Before**:
- Plan scenarios and logistics
- Coordinate with stakeholders
- Ensure tools and access ready

**During**:
- Facilitate entire event
- Keep to schedule
- Make go/no-go decisions
- Manage discussions
- Ensure safety

**After**:
- Lead retrospective
- Compile findings
- Track action items

### Chaos Operator
**Before**:
- Prepare chaos scripts
- Test in staging
- Verify rollback procedures

**During**:
- Execute failure injection
- Monitor chaos tools
- Perform rollback if needed
- Announce actions clearly

**After**:
- Document technical details
- Review tool effectiveness

### Observer
**Before**:
- Understand scenarios
- Prepare note-taking templates
- Set up monitoring views

**During**:
- Take detailed notes
- Timestamp all events
- Record metrics
- Don't intervene (pure observation)

**After**:
- Compile observations
- Contribute to report

### Incident Responder (Team Members)
**Before**:
- Review runbooks
- Understand system architecture
- Have access ready

**During**:
- Respond to failures naturally
- Follow incident procedures
- Communicate clearly
- Ask questions

**After**:
- Share experience
- Suggest improvements

### Scribe
**Before**:
- Prepare documentation template
- Set up shared doc

**During**:
- Real-time documentation
- Capture quotes
- Note decisions made
- Record timing

**After**:
- Clean up notes
- Distribute to team

### Executive Observer (Optional)
**Before**:
- Understand GameDay goals
- Review scenarios

**During**:
- Observe team dynamics
- Ask clarifying questions
- Provide business context

**After**:
- Provide leadership perspective
- Support action items

---

## Sample GameDay Schedule

### Standard 2.5 Hour GameDay

```
09:00 - 09:15  Pre-GameDay Setup
09:15 - 09:30  Kickoff and Introductions
09:30 - 09:50  Scenario 1: Database Failover
               - Brief (3 min)
               - Execute (10 min)
               - Recover (3 min)
               - Debrief (4 min)
09:50 - 10:10  Scenario 2: AZ Outage
               - Brief (3 min)
               - Execute (10 min)
               - Recover (3 min)
               - Debrief (4 min)
10:10 - 10:25  Break
10:25 - 10:45  Scenario 3: API Dependency Failure
               - Brief (3 min)
               - Execute (10 min)
               - Recover (3 min)
               - Debrief (4 min)
10:45 - 11:00  Wrap-up and Retrospective
11:00 - 11:30  (Optional) Extended discussion
```

---

## Scenario Ideas by System Type

### Web Application GameDays

**Scenario 1: Load Balancer Failure**
```
Failure: Terminate load balancer
Expected: Traffic routes to backup LB
Duration: 10 minutes
```

**Scenario 2: Cache Complete Failure**
```
Failure: Stop all Redis instances
Expected: App degrades gracefully, uses DB
Duration: 15 minutes
```

**Scenario 3: CDN Outage**
```
Failure: Block CDN domains
Expected: Fallback to origin, slower but functional
Duration: 10 minutes
```

### Microservices GameDays

**Scenario 1: Service Mesh Failure**
```
Failure: Kill Istio/Linkerd control plane
Expected: Data plane continues working
Duration: 15 minutes
```

**Scenario 2: Cascading Timeout**
```
Failure: Slow down backend service
Expected: Circuit breakers prevent cascade
Duration: 20 minutes
```

**Scenario 3: Service Discovery Failure**
```
Failure: Stop Consul/etcd
Expected: Services use cached endpoints
Duration: 10 minutes
```

### Data Platform GameDays

**Scenario 1: Primary Database Failure**
```
Failure: Failover RDS/Postgres
Expected: Automatic failover, brief downtime
Duration: 15 minutes
```

**Scenario 2: Kafka Broker Loss**
```
Failure: Stop 2 out of 5 Kafka brokers
Expected: Topic partitions re-replicate
Duration: 20 minutes
```

**Scenario 3: ETL Pipeline Failure**
```
Failure: Stop Airflow scheduler
Expected: Jobs queue and execute when recovered
Duration: 15 minutes
```

### Cloud Infrastructure GameDays

**Scenario 1: Availability Zone Outage**
```
Failure: Terminate all instances in one AZ
Expected: Multi-AZ setup maintains service
Duration: 20 minutes
```

**Scenario 2: Region Failover**
```
Failure: Change Route53 to mark region unhealthy
Expected: Traffic routes to secondary region
Duration: 30 minutes
```

**Scenario 3: S3 Access Failure**
```
Failure: Block S3 access via security group
Expected: App uses local cache, retries
Duration: 15 minutes
```

---

## Post-GameDay Activities

### Immediate (Same Day)

**Quick Retrospective**:
```
30 minutes after GameDay ends:
- What went well?
- What went poorly?
- Top 3 action items
- Top 3 learnings
```

**Communicate Results**:
```
Send summary to:
- All participants
- Team leadership
- Other engineering teams
- Customer support (if relevant)
```

**Email Template**:
```
Subject: GameDay Results - [Date]

Team,

Thanks for participating in today's GameDay! Here's a quick summary:

Scenarios Tested:
✓ Database failover
✓ AZ outage simulation
✓ API dependency failure

Key Findings:
- Database failover worked perfectly (MTTR: 47 seconds)
- AZ outage revealed monitoring gap (action item created)
- Circuit breakers prevented API cascade

Action Items Created:
1. Add monitoring for cross-AZ traffic (Priority: High)
2. Update runbook for database failover (Priority: Medium)
3. Review circuit breaker thresholds (Priority: Medium)

Great job everyone! Next GameDay: [Date]

Detailed report to follow by EOW.
```

### Week 1: Detailed Analysis

**Create Comprehensive Report**:

```markdown
# GameDay Report: [Date]

## Executive Summary
[2-3 paragraph overview]

## Objectives
1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

## Scenarios Executed

### Scenario 1: Database Primary Failure
**Status**: Success ✓

**Timeline**:
- 09:30:00 - Failure injected
- 09:30:12 - Alert fired (database_connection_failed)
- 09:30:18 - Team acknowledged in PagerDuty
- 09:30:47 - Automatic failover completed
- 09:31:05 - Application reconnected
- 09:31:30 - All metrics returned to normal

**Expected Behavior**: Automatic failover in < 60 seconds
**Actual Behavior**: Failover in 47 seconds ✓

**Observations**:
- Failover worked flawlessly
- Monitoring captured all events
- Team response was quick
- No manual intervention needed

**Issues Found**: None

**Action Items**: None

---

### Scenario 2: Availability Zone Outage
**Status**: Partial Success ⚠

**Timeline**:
- 09:50:00 - AZ failure injected (us-east-1a)
- 09:50:15 - Error rate spiked to 5%
- 09:50:45 - Team investigating
- 09:51:20 - Identified stale health checks
- 09:52:00 - Manual intervention: updated LB config
- 09:53:00 - Error rate returned to normal

**Expected Behavior**: Automatic traffic shift, no errors
**Actual Behavior**: 5% error rate for 3 minutes, manual fix ⚠

**Observations**:
- Load balancer health checks were stale
- Took 3 minutes to identify root cause
- Manual intervention required
- MTTR: 3 minutes (target was 1 minute)

**Issues Found**:
1. Health check interval too long (60s → should be 10s)
2. No monitoring for cross-AZ traffic distribution
3. Runbook doesn't cover AZ failure

**Action Items**:
- [ ] Reduce LB health check interval to 10s (HIGH)
- [ ] Add monitoring for AZ traffic distribution (HIGH)
- [ ] Update runbook with AZ failure procedure (MEDIUM)

---

## Overall Results

### Successes
- 2 out of 3 scenarios worked as expected
- Team communication was excellent
- Runbooks were helpful
- MTTR average: 2 minutes

### Areas for Improvement
- Health check configuration
- Cross-AZ monitoring
- Runbook completeness

### Learnings
1. Automatic failover works well when properly configured
2. Monitoring is comprehensive
3. Team is well-prepared for common failures
4. Need to improve AZ-level resilience

## Action Items Summary

| Priority | Action | Owner | Deadline |
|----------|--------|-------|----------|
| HIGH | Reduce LB health check interval | @ops-team | 1 week |
| HIGH | Add AZ traffic monitoring | @sre-team | 1 week |
| MEDIUM | Update runbook | @platform-team | 2 weeks |

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Scenarios Completed | 3 | 3 | ✓ |
| Scenarios Successful | 3 | 2 | ⚠ |
| Average MTTR | < 2 min | 2 min | ✓ |
| Manual Interventions | 0 | 1 | ⚠ |

## Next GameDay
**Date**: [One month from now]
**Focus**: Multi-region failover and data replication
```

### Month 1: Execute Action Items

**Track Progress**:
```
□ Assign owners to all action items
□ Set deadlines (1-4 weeks)
□ Create tickets/issues
□ Review progress weekly
□ Verify fixes in staging
□ Re-test in next GameDay
```

### Month 2+: Continuous Improvement

**Regular Schedule**:
```
Monthly GameDays:
- First Tuesday of each month
- 2-3 hour duration
- Rotate scenarios
- Include previous action items

Quarterly Major GameDays:
- Full day event
- Cross-team participation
- Complex scenarios
- Executive participation
```

---

## Common GameDay Pitfalls

### Pitfall 1: Over-Ambitious Scenarios
**Problem**: Too many or too complex scenarios
**Solution**: Start with 3 simple scenarios, expand over time

### Pitfall 2: Insufficient Preparation
**Problem**: Scenarios not tested in staging
**Solution**: Always dry-run in staging first

### Pitfall 3: Blame Culture
**Problem**: Pointing fingers when things go wrong
**Solution**: Establish blameless culture, focus on systems

### Pitfall 4: No Follow-Through
**Problem**: Action items never completed
**Solution**: Track action items like production incidents

### Pitfall 5: Too Rare
**Problem**: GameDays only once or twice per year
**Solution**: Monthly cadence builds muscle memory

### Pitfall 6: Lack of Variety
**Problem**: Same scenarios every GameDay
**Solution**: Rotate scenarios, increase complexity

### Pitfall 7: Poor Communication
**Problem**: Teams not aware of GameDay happening
**Solution**: Communicate early and often

---

## GameDay Maturity Model

### Level 1: First GameDay
- 1-2 simple scenarios
- Single team
- 2 hour duration
- Quarterly

### Level 2: Regular GameDays
- 3-4 scenarios
- Multiple teams
- Monthly cadence
- Documented results

### Level 3: Advanced GameDays
- Complex multi-stage scenarios
- Cross-team coordination
- Automated chaos injection
- Action items tracked and resolved

### Level 4: Continuous Chaos
- GameDays integrate with continuous chaos
- Executive participation
- Customer-facing (with transparency)
- Chaos as cultural norm

---

## Resources and Templates

### GameDay Planning Checklist

```
□ Define objectives and scope
□ Select scenarios (3-5)
□ Assign roles and responsibilities
□ Schedule date and time
□ Book room / set up video call
□ Prepare tools and scripts
□ Dry run all scenarios in staging
□ Notify all stakeholders
□ Set up dashboards and monitoring
□ Prepare communication templates
□ Review runbooks
□ Verify rollback procedures
□ Order food/refreshments (if in-person)
□ Set up recording (screen + audio)
□ Create shared documentation
□ Send final reminder 24 hours before
□ Day-of setup 30 minutes early
```

### GameDay Announcement Template

See "Pre-GameDay Email Template" in Planning section above

### Scenario Script Template

See "Scenario Template" in Planning section above

---

## Conclusion

GameDays are one of the most effective ways to build confidence in your system's resilience and improve your team's incident response capabilities. The key to successful GameDays is:

1. **Thorough Planning**: Don't wing it
2. **Psychological Safety**: Blameless environment
3. **Clear Objectives**: Know what you're testing
4. **Realistic Scenarios**: Based on real risks
5. **Strong Facilitation**: Keep things moving
6. **Detailed Documentation**: Capture everything
7. **Action Follow-Through**: Fix what you find
8. **Regular Cadence**: Make it a habit

Start simple, learn continuously, and gradually increase complexity. Over time, GameDays will become a valued and anticipated part of your reliability practice.

Good luck with your first GameDay!
