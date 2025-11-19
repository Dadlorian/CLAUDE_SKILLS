# Analytics Specification Template

Use this template to define how a new feature or product change should be measured analytically. Ensures consistent, measurable instrumentation across the team.

---

## 1. Overview

**Feature/Initiative:** [Name of feature or change]

**Owner:** [Name and team]

**Start Date:** [When this launches]

**Last Updated:** [Date this spec was updated]

**Success Criteria Owner:** [Who owns the success metrics]

---

## 2. Business Objective

**What problem does this solve?**
[2-3 sentences describing the user problem or business need]

Example:
"Users struggle to find the right people to collaborate with, leading to low collaboration rates. By suggesting collaborators based on user activity and network, we expect to increase collaboration events and engagement."

**Expected Impact:**
- [Metric 1]: [Expected direction and magnitude]
- [Metric 2]: [Expected direction and magnitude]

Example:
- Daily collaboration events: +20-30%
- User retention day 7: +5-10%
- Monthly active collaborating users: +15-25%

**Why Now?**
[Why launching this feature at this time is important]

Example:
"We've identified through user interviews that discoverability is the #1 blocker to adoption. Previous cohorts had low collaboration rates despite strong individual usage."

---

## 3. Feature Description

**What is the feature?**
[Brief description of what users can do]

**How does it work?**
[User journey/steps to use feature]

**Who can access it?**
- Launch scope: [All users / Specific cohort / Gradual rollout]
- Rollout timeline: [When different user groups get access]
- Device support: [Web / iOS / Android / All]

---

## 4. Key User Journeys

**Describe the main paths users will take:**

### Journey 1: [Name]
1. User does X
2. Feature appears/is discovered
3. User interacts with feature
4. Feature generates value

### Journey 2: [Name]
[Similar format]

---

## 5. Events to Instrument

### 5.1 Discovery Events
[How do users first become aware of the feature?]

| Event Name | When Fired | Key Properties | Owner | Status |
|-----------|-----------|---|---|---|
| feature_suggested | When suggestion appears | suggestion_type, suggestion_source, recipient_count | @engineer | Not Started |
| feature_discovered | When user first sees feature (anywhere) | discovery_method, platform | @engineer | Not Started |
| feature_help_viewed | When user views help/tutorial | help_type | @engineer | Not Started |

### 5.2 Activation Events
[How do users take first action with the feature?]

| Event Name | When Fired | Key Properties | Owner | Status |
|-----------|-----------|---|---|---|
| collaboration_initiated | User starts collaboration | recipient_count, collaboration_type, source | @engineer | Not Started |
| collaborator_added | User adds specific collaborator | collaborator_source, relationship_type | @engineer | Not Started |
| collaborator_suggested_clicked | User clicks suggested collaborator | suggestion_rank, suggestion_rank_percentile | @engineer | Not Started |

### 5.3 Engagement Events
[How do users repeatedly use the feature?]

| Event Name | When Fired | Key Properties | Owner | Status |
|-----------|-----------|---|---|---|
| collaboration_active | During active collaboration session | session_duration, participant_count, collaboration_type | @engineer | Not Started |
| collaboration_message_sent | User sends message in collaboration | message_type, recipients, is_first_message | @engineer | Not Started |
| collaborator_searched | User searches for collaborator | search_query, search_type, results_count | @engineer | Not Started |

### 5.4 Adoption Events
[Milestones showing deepening engagement]

| Event Name | When Fired | Key Properties | Owner | Status |
|-----------|-----------|---|---|---|
| first_collaboration_completed | User completes first collaboration | time_to_completion, participants_count | @engineer | Not Started |
| nth_collaboration | User completes 5th, 10th collaboration | n_value, days_since_first | @engineer | Not Started |
| regular_collaborator | User initiates 3+ collaborations in a week | collaborations_this_week, avg_frequency | @engineer | Not Started |

### 5.5 Quality/Health Events
[Events indicating problems or user satisfaction]

| Event Name | When Fired | Key Properties | Owner | Status |
|-----------|-----------|---|---|---|
| collaboration_abandoned | User starts collaboration but doesn't complete | abandoned_at_step, time_in_feature | @engineer | Not Started |
| collaborator_removed | User removes/cancels collaborator | reason_if_provided, how_long_collaborated | @engineer | Not Started |
| feature_error | Feature generates error | error_type, error_message, recovery_possible | @engineer | Not Started |

---

## 6. Metrics Definition

### Primary Success Metrics

**Metric 1: Daily Collaborators**
- Definition: Unique users who initiate or participate in collaboration daily
- Calculation: COUNT(DISTINCT user_id) WHERE collaboration_initiated OR collaboration_active
- Baseline: [Current value]
- Target: [Expected value]
- Timeline to measure: Launch + 2-4 weeks
- Acceptance criteria: Increase by [X%] or reach [absolute number]

**Metric 2: Collaboration Events Per User**
- Definition: Average number of collaborations initiated per monthly active user
- Calculation: SUM(collaborations) / COUNT(DISTINCT user_id)
- Baseline: [Current value]
- Target: [Expected value]
- Timeline: Launch + 4 weeks
- Acceptance criteria: Increase by [X%]

**Metric 3: Collaboration Completion Rate**
- Definition: % of initiated collaborations that reach completion
- Calculation: Completed collaborations / Initiated collaborations
- Baseline: [Current value]
- Target: [Expected value]
- Timeline: Launch + 2 weeks
- Acceptance criteria: Maintain current level or improve

### Secondary Metrics

**Metric 4: Feature Adoption Rate**
- Definition: % of MAU who use collaboration feature
- Calculation: Users with collaboration events / MAU
- Target: [X%] of MAU within 1 month
- Rationale: Shows if feature is reaching intended audience

**Metric 5: Time to First Collaboration**
- Definition: Median days from signup to first collaboration
- Calculation: PERCENTILE_CONT(50) of days between signup and first_collaboration_initiated
- Target: [Reduce from X to Y days]
- Rationale: Indicates how quickly we drive new users to engagement

**Metric 6: Collaborator Network Size**
- Definition: Average number of unique collaborators per user
- Calculation: SUM(unique_collaborators) / COUNT(user_id)
- Target: Grow by [X] collaborators per user
- Rationale: Larger networks = more engagement opportunity

### Guardrail Metrics

[Metrics we must not harm]

**Guardrail 1: User Retention (7-day)**
- Definition: % of users active on day 7
- Must not decline more than: [2-3 percentage points]
- Rationale: Feature shouldn't distract from core engagement

**Guardrail 2: Core Feature Usage**
- Definition: [Name] events per user
- Must not decline more than: [X%]
- Rationale: New feature shouldn't cannibalize existing core features

**Guardrail 3: Error Rate**
- Definition: % of collaboration sessions with errors
- Must not exceed: [X%]
- Rationale: Feature should be stable

---

## 7. Measurement Plan

### Phase 1: Pre-Launch (Development)
- [ ] Events instrumented in staging
- [ ] Events validated in staging environment
- [ ] QA checklist completed
- [ ] Analytics dashboard created
- [ ] Baseline metrics calculated
- [ ] Target metrics defined
- Timeline: [Date]

### Phase 2: Soft Launch
- [ ] Feature released to [X%] of users
- [ ] Daily monitoring of all metrics
- [ ] QA team validates event firing
- [ ] Bug fixes deployed as needed
- [ ] No major issues detected?
- Timeline: [Dates], Duration: [X days]

### Phase 3: Full Launch
- [ ] Feature released to 100% of users
- [ ] Continue daily monitoring
- [ ] Share weekly results with team
- Timeline: [Date]

### Phase 4: Post-Launch Analysis
- [ ] Full cohort analysis (4+ weeks post-launch)
- [ ] Segment analysis by user type
- [ ] Compare to pre-launch baseline
- [ ] Document learnings
- Timeline: [Date]

---

## 8. Data Quality Checks

**Pre-Launch:**
- [ ] Event firing correctly in staging
- [ ] All properties populated
- [ ] No PII in events
- [ ] Event volume reasonable

**During Launch:**
- [ ] Event volume as expected
- [ ] Error events tracked
- [ ] No spike in null/missing properties
- [ ] Event latency <5 minutes

**Monitoring:**
- Alert if daily event volume drops >30%
- Alert if error rate exceeds [X%]
- Alert if key property completion <95%

---

## 9. Dashboard & Reporting

**Real-Time Monitoring Dashboard:**
- URL: [Link to dashboard]
- Refresh: Every 1 hour
- Key metrics: [List primary metrics]
- Audience: Product team, engineering leads

**Weekly Report:**
- Day/time: Every [Day] at [Time]
- Recipient: [Team distribution list]
- Contains: Progress vs. targets, segment breakdowns, issues

**Monthly Deep Dive:**
- Cohort analysis comparing pre-launch vs. post-launch
- Segment performance comparison
- Learning slides for stakeholders

---

## 10. Decision Criteria

**What constitutes success?**

| Outcome | Criteria | Decision |
|---------|----------|----------|
| Success | Primary metrics improve 15%+, guardrails healthy, adoption >30% MAU in 4 weeks | KEEP - Full rollout, iterate for improvement |
| Partial Success | Primary metrics improve 5-15%, some segments show strong adoption | KEEP - Full rollout but investigate segment gaps |
| Neutral | Primary metrics flat or minor changes (±5%) | MONITOR - Decide if worth iterating or moving on |
| Failure | Primary metrics decline, guardrail metrics hurt, <10% adoption | REVERT - Learn why and iterate on hypothesis |

**Success Timeline:**
- Early indicator (2 weeks): Is adoption happening? Are errors low?
- Decision point (4 weeks): Do primary metrics support hypothesis?
- Learning point (8+ weeks): What drives long-term engagement?

---

## 11. Potential Issues & Mitigation

**Potential Issue 1:** [Issue description]
- Indicator: [How would we detect this?]
- Mitigation: [What we'd do]
- Decision trigger: [When to act]

Example:
**Potential Issue 1:** Low feature discovery - users don't know feature exists
- Indicator: <5% of MAU trigger feature discovery events in first 2 weeks
- Mitigation: Increase visibility (in-app banner, email, feature announcement)
- Decision trigger: If adoption doesn't improve after visibility boost

**Potential Issue 2:** Feature is confusing - high abandonment
- Indicator: >50% of initiators abandon before completion
- Mitigation: Improve UX/onboarding, simplify flow
- Decision trigger: If completion rate doesn't improve after UX fixes

**Potential Issue 3:** Feature causes errors - instability
- Indicator: Error events exceed 5% of collaboration sessions
- Mitigation: Debug and deploy fixes
- Decision trigger: Revert if can't get error rate below 2% in 3 days

---

## 12. Future Analysis & Learnings

**Planned Analysis:**
- [ ] Segment performance by user tenure
- [ ] Segment performance by acquisition channel
- [ ] Correlation with overall retention
- [ ] Long-term LTV impact (3+ months post-launch)
- [ ] Cost analysis (infrastructure, support costs)

**Expected Learnings to Document:**
- Which user segments benefit most?
- What drives successful collaborations?
- What barriers prevent adoption for other segments?
- How does this feature impact overall product health?

---

## 13. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | [Name] | [Signature] | [Date] |
| Analytics Lead | [Name] | [Signature] | [Date] |
| Engineering Lead | [Name] | [Signature] | [Date] |
| VP/Director | [Name] | [Signature] | [Date] |

---

## 14. Appendix: Sample Event JSON

```json
{
  "event_id": "evt_12345678",
  "event_name": "collaboration_initiated",
  "timestamp": "2025-11-19T10:30:45Z",
  "user_id": "user_abc123",
  "session_id": "session_xyz789",
  "properties": {
    "recipient_count": 3,
    "collaboration_type": "document_collaboration",
    "source": "suggested_collaborators",
    "workspace_id": "ws_123",
    "platform": "web",
    "device_type": "desktop",
    "suggestion_rank": 2,
    "is_first_collaboration": true
  },
  "context": {
    "plan_tier": "pro",
    "acquisition_source": "organic_search",
    "user_cohort_date": "2025-09-01",
    "days_since_signup": 79
  }
}
```

---

## 15. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | [Date] | Initial spec | [Name] |
| 1.1 | [Date] | Updated targets based on beta feedback | [Name] |

---

**Notes:**
- Spec reviewed and approved by product, analytics, and engineering
- Implementation tracked in [project management tool]
- Results documented in [shared folder/wiki]
