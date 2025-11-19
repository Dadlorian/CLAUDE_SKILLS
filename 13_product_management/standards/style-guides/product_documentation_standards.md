# Product Documentation Standards
## Elite Professional Product Management Documentation Guide

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Based on practices from Google, Amazon, Stripe, Airbnb, and SVPG

---

## Table of Contents

1. [Overview](#overview)
2. [Product Requirements Documents (PRDs)](#product-requirements-documents-prds)
3. [Product Strategy Documents](#product-strategy-documents)
4. [User Stories & Acceptance Criteria](#user-stories--acceptance-criteria)
5. [Product Roadmaps](#product-roadmaps)
6. [Product Briefs & One-Pagers](#product-briefs--one-pagers)
7. [Launch Documents](#launch-documents)
8. [Research Reports](#research-reports)
9. [Metrics & Analytics Documentation](#metrics--analytics-documentation)
10. [Decision Logs](#decision-logs)
11. [Writing Style Guidelines](#writing-style-guidelines)

---

## Overview

Product documentation serves multiple purposes:
- **Alignment**: Ensures cross-functional teams work toward the same goals
- **Decision Record**: Documents why decisions were made
- **Communication**: Shares product thinking across the organization
- **Onboarding**: Helps new team members understand product context
- **Accountability**: Creates clear ownership and success criteria

### Core Principles

1. **Clear and Concise**: Respect reader's time, get to the point
2. **Evidence-Based**: Back assertions with data, research, or user feedback
3. **Action-Oriented**: Make next steps and owners explicit
4. **Living Documents**: Update as you learn, mark status clearly
5. **Accessible**: Write for diverse audiences (technical and non-technical)

---

## Product Requirements Documents (PRDs)

### Purpose
Define WHAT will be built, WHY it matters, and HOW success will be measured. PRDs are the single source of truth for product initiatives.

### Standard PRD Template

```markdown
# [Product/Feature Name] - Product Requirements Document

**Status**: [Draft | In Review | Approved | In Development | Shipped]
**Owner**: [Product Manager Name]
**Last Updated**: [Date]
**Target Launch**: [Quarter/Month/Date]

---

## Executive Summary
[2-3 sentences capturing the essence: what we're building, why, expected impact]

Example: "We are building a real-time collaboration feature for enterprise teams to reduce async communication delays by 40%. This addresses the #1 pain point from Q4 2024 enterprise customer research and is expected to reduce churn by 15% and increase NRR by 10 points."

---

## Problem Statement

### User Problem
[Describe the customer problem in their words, using quotes from research]

**Who** experiences this problem?
- Primary: [Primary user persona]
- Secondary: [Secondary personas if applicable]

**What** is the problem?
[Specific, observable problem description]

**When** does this occur?
[Context and frequency]

**Impact** of the problem:
- For users: [Quantified impact on user workflow, time, frustration]
- For business: [Current cost: churn, support tickets, lost deals]

### Evidence
- Customer interviews: [X interviews conducted, link to research]
- Quantitative data: [Usage data, surveys, analytics]
- Support tickets: [Y tickets per month related to this]
- Sales feedback: [Lost deals, feature requests]

---

## Business Objectives

### Primary Objective
[Single most important business goal this feature achieves]

### Success Metrics

**North Star Impact**: How does this move our North Star metric?
[Specific, measurable impact]

**Key Metrics**:
| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| [Metric 1] | [Baseline] | [Goal] | [When] |
| [Metric 2] | [Baseline] | [Goal] | [When] |
| [Metric 3] | [Baseline] | [Goal] | [When] |

**Guardrail Metrics** (ensure we don't harm):
- [Metric to monitor]
- [Metric to monitor]

---

## Proposed Solution

### Overview
[High-level description of the solution]

### User Experience

**User Flow**:
1. [Step 1]: User action and system response
2. [Step 2]: User action and system response
3. [Step N]: User action and system response

[Include wireframes, mockups, or Figma links]

**Key Interactions**:
- [Critical interaction 1]
- [Critical interaction 2]

### User Stories

**Epic**: [Epic name]

**User Stories**:

```
As a [user type],
I want to [action],
So that [benefit/goal].

Acceptance Criteria:
- [Criterion 1]
- [Criterion 2]
- [Criterion N]
```

---

## Technical Approach

[High-level technical design - brief overview, link to detailed tech spec]

**Technical Dependencies**:
- [Dependency 1]
- [Dependency 2]

**API Changes**:
- [New endpoints]
- [Modified endpoints]

**Data Model Changes**:
- [New tables/collections]
- [Schema changes]

**Third-Party Integrations**:
- [Integration 1]
- [Integration 2]

---

## Scope

### In Scope (MVP)
- [Feature 1]
- [Feature 2]
- [Feature N]

### Out of Scope (Future Phases)
- [Future feature 1] - *Reason for deferral*
- [Future feature 2] - *Reason for deferral*

### Open Questions
- [ ] [Question 1] - **Owner**: [Name] - **Due**: [Date]
- [ ] [Question 2] - **Owner**: [Name] - **Due**: [Date]

---

## Go-to-Market Plan

**Target Audience**:
- [Primary audience segment]
- [Secondary audience segment]

**Launch Tier**: [Tier 1 | Tier 2 | Tier 3]

**Marketing Channels**:
- [Channel 1]
- [Channel 2]

**Sales Enablement**:
- [Collateral needed]
- [Training required]

---

## Launch Plan

**Beta Phase**:
- Start: [Date]
- Audience: [Who gets beta access]
- Success Criteria: [What validates we can launch]

**General Availability**:
- Launch Date: [Target date]
- Rollout Strategy: [All at once | Gradual | Feature flag]

**Post-Launch**:
- Week 1 review: [Date]
- Month 1 review: [Date]

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How we'll address] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How we'll address] |

---

## Timeline & Milestones

| Milestone | Owner | Target Date | Status |
|-----------|-------|-------------|--------|
| PRD Approval | [PM] | [Date] | [Status] |
| Design Complete | [Designer] | [Date] | [Status] |
| Tech Spec Complete | [Eng Lead] | [Date] | [Status] |
| Development Complete | [Eng Team] | [Date] | [Status] |
| QA Complete | [QA] | [Date] | [Status] |
| Beta Launch | [PM] | [Date] | [Status] |
| GA Launch | [PM] | [Date] | [Status] |

---

## Appendix

### Research Links
- [User research report]
- [Competitive analysis]
- [Market research]

### Design Links
- [Figma designs]
- [User flow diagrams]
- [Prototype]

### Technical Links
- [Technical specification]
- [Architecture diagrams]
- [API documentation]

---

## Approval

| Stakeholder | Role | Approval Status | Date | Comments |
|-------------|------|----------------|------|----------|
| [Name] | Product VP | Approved | [Date] | [Comments] |
| [Name] | Engineering VP | Approved | [Date] | [Comments] |
| [Name] | Design Lead | Approved | [Date] | [Comments] |
```

### PRD Best Practices

**DO**:
✅ Start with the problem, not the solution
✅ Use data and customer quotes liberally
✅ Define success metrics upfront
✅ Be specific about scope (in and out)
✅ Update PRD as you learn
✅ Link to supporting documents
✅ Include visuals (flows, wireframes, mockups)

**DON'T**:
❌ Write tech specs in PRD (link to separate doc)
❌ Include implementation details beyond high-level approach
❌ Make it overly long (ideal: 3-5 pages)
❌ Use jargon without definition
❌ Forget to update status
❌ Skip the "why" to jump to "what"

---

## Product Strategy Documents

### Purpose
Articulate long-term product vision, strategic bets, and roadmap themes. Strategy docs guide multi-quarter or multi-year direction.

### Strategy Document Template

```markdown
# [Product Area] Strategy - [Year/Time Period]

**Author**: [Product Leader]
**Contributors**: [Team members]
**Last Updated**: [Date]
**Period**: [Time horizon - e.g., "2025-2027"]

---

## Executive Summary
[3-4 sentences: Current state, strategic direction, expected outcome]

---

## Market Context

### Market Size & Opportunity
- **TAM** (Total Addressable Market): $[X]B
- **SAM** (Serviceable Addressable Market): $[X]B
- **SOM** (Serviceable Obtainable Market): $[X]M
- **Current Market Share**: [X%]
- **Growth Rate**: [X% CAGR]

[Include sources and calculation methodology]

### Competitive Landscape

**Direct Competitors**:
| Competitor | Strengths | Weaknesses | Market Share |
|-----------|-----------|------------|--------------|
| [Competitor 1] | [Strengths] | [Weaknesses] | [Share] |
| [Competitor 2] | [Strengths] | [Weaknesses] | [Share] |

**Emerging Threats**:
- [Threat 1]: [Why it matters]
- [Threat 2]: [Why it matters]

### Market Trends
1. [Trend 1]: [Impact on our product]
2. [Trend 2]: [Impact on our product]
3. [Trend 3]: [Impact on our product]

---

## Current State Assessment

### Product Performance
[Key metrics showing current performance]

### Strengths
- [Strength 1]: Evidence
- [Strength 2]: Evidence

### Weaknesses
- [Weakness 1]: Evidence
- [Weakness 2]: Evidence

### Customer Feedback Themes
1. [Theme 1]: "[Customer quote]"
2. [Theme 2]: "[Customer quote]"
3. [Theme 3]: "[Customer quote]"

---

## Product Vision

**Vision Statement** (Where we're going):
[Inspiring 1-2 sentence vision - what does success look like in 3-5 years?]

Example: "We will be the default collaboration platform for 100M+ knowledge workers, making teamwork feel as effortless as thinking alone."

**Mission** (Why we exist):
[Purpose statement]

**Values** (How we work):
- [Value 1]
- [Value 2]
- [Value 3]

---

## Strategic Themes

### Theme 1: [Theme Name]
**Objective**: [What we're trying to achieve]
**Rationale**: [Why this matters now]
**Key Initiatives**:
- [Initiative 1]
- [Initiative 2]
**Expected Impact**: [Business and customer impact]

### Theme 2: [Theme Name]
[Same structure as Theme 1]

### Theme 3: [Theme Name]
[Same structure as Theme 1]

---

## Strategic Roadmap

**Now** (This Quarter):
- [Initiative 1]
- [Initiative 2]

**Next** (Next 2 Quarters):
- [Initiative 1]
- [Initiative 2]

**Later** (Beyond):
- [Opportunity 1]
- [Opportunity 2]

---

## Resource Requirements

**Team**:
- [X] Product Managers
- [Y] Engineers
- [Z] Designers

**Budget**:
- [Budget allocation by theme]

**Dependencies**:
- [Platform/infrastructure needs]
- [Cross-team dependencies]

---

## Success Metrics

**3-Year Goals** (BHAG - Big Hairy Audacious Goal):
- [Ambitious goal 1]
- [Ambitious goal 2]

**Annual OKRs**:

**Year 1 (2025)**:
- Objective 1: [Objective]
  - KR1: [Key Result 1]
  - KR2: [Key Result 2]

**Year 2 (2026)**:
[Similar structure]

---

## Risks & Assumptions

**Key Assumptions**:
- [Assumption 1]: How we'll validate
- [Assumption 2]: How we'll validate

**Strategic Risks**:
- [Risk 1]: Mitigation plan
- [Risk 2]: Mitigation plan

---

## Appendix

### Customer Research
[Links to research, interview summaries]

### Competitive Analysis
[Detailed competitive teardowns]

### Financial Models
[Revenue projections, cost models]
```

---

## User Stories & Acceptance Criteria

### User Story Format

**Standard Format** (As a / I want / So that):

```markdown
As a [user type/persona],
I want to [action/capability],
So that [benefit/value/goal].
```

**Example**:
```markdown
As a team administrator,
I want to bulk invite users via CSV upload,
So that I can onboard my 200-person team in minutes instead of hours.
```

### Acceptance Criteria

**Format**: Use Given/When/Then for clarity

```markdown
**Acceptance Criteria**:

Given [precondition/context],
When [action/trigger],
Then [expected outcome].

**Example**:
Given I am a team admin with upload permissions,
When I upload a CSV file with 100 valid email addresses,
Then all 100 users receive invite emails within 5 minutes,
And I see a confirmation message with the count of sent invitations,
And any invalid emails are listed in an error report.
```

### Detailed Acceptance Criteria Checklist

For each user story, include:

✅ **Functional Requirements**:
- [ ] Core functionality works as described
- [ ] Edge cases handled (empty states, max limits, errors)
- [ ] All user roles/permissions respected

✅ **Non-Functional Requirements**:
- [ ] Performance: [e.g., "Loads in <200ms"]
- [ ] Accessibility: WCAG 2.1 AA compliance
- [ ] Security: [Relevant security requirements]
- [ ] Scalability: [e.g., "Handles 10,000 concurrent users"]

✅ **User Experience**:
- [ ] Error messages are clear and actionable
- [ ] Success states provide clear feedback
- [ ] Loading states for async operations
- [ ] Responsive design (mobile, tablet, desktop)

✅ **Analytics**:
- [ ] Events instrumented: [List key events]
- [ ] Properties tracked: [List properties]

✅ **Testing**:
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Manual QA completed
- [ ] Cross-browser testing completed

---

## Product Roadmaps

### Roadmap Types

#### 1. Now/Next/Later Roadmap

```markdown
## Product Roadmap - [Product Area]

**Now** (Current Quarter - Q1 2025):
- **[Initiative 1]**: [Brief description] - *Expected impact: [metric improvement]*
- **[Initiative 2]**: [Brief description] - *Expected impact: [metric improvement]*

**Next** (Next 1-2 Quarters):
- **[Initiative 3]**: [Brief description] - *Expected impact: [metric improvement]*
- **[Initiative 4]**: [Brief description] - *Expected impact: [metric improvement]*

**Later** (Future - Lower Confidence):
- **[Opportunity 1]**: [Brief description] - *Hypothesis: [expected impact]*
- **[Opportunity 2]**: [Brief description] - *Hypothesis: [expected impact]*
```

#### 2. Theme-Based Roadmap

```markdown
## Product Roadmap - By Strategic Theme

### Theme 1: Enterprise Scalability
**Q1 2025**:
- SSO/SAML integration
- Advanced permissions (RBAC)

**Q2 2025**:
- Audit logs
- Data residency options

### Theme 2: User Activation
**Q1 2025**:
- Onboarding redesign
- Interactive product tour

**Q2 2025**:
- Personalized recommendations
- Gamification elements
```

#### 3. Outcome-Based Roadmap

```markdown
## Product Roadmap - Outcome Focus

**Q1 2025 Outcomes**:
1. **Increase activation rate from 35% to 50%**
   - Potential solutions: Streamlined onboarding, interactive tutorials, better empty states
2. **Reduce enterprise churn by 15%**
   - Potential solutions: Usage analytics for CSMs, proactive health monitoring, advanced integrations
```

### Roadmap Best Practices

**DO**:
✅ Focus on outcomes over features
✅ Maintain flexibility (themes > specific features)
✅ Show confidence levels (committed vs exploring)
✅ Link to strategy and metrics
✅ Update regularly (monthly review minimum)
✅ Communicate changes transparently

**DON'T**:
❌ Commit to specific dates beyond current quarter
❌ Include every small feature
❌ Promise features to close deals (use "themes")
❌ Build roadmap in isolation (collaborate with stakeholders)

---

## Product Briefs & One-Pagers

### Purpose
Quick, executive-friendly summaries of product initiatives. Used for approvals, updates, and cross-functional alignment.

### One-Pager Template

```markdown
# [Feature/Product Name] - Product Brief

**Status**: [Proposed | Approved | In Progress | Shipped]
**Owner**: [PM Name]
**Date**: [Date]

---

## The Opportunity

[2-3 sentences: What problem exists, for whom, and why it matters]

**Evidence**:
- [Data point 1]
- [Customer quote or research finding]
- [Business impact of problem]

---

## Proposed Solution

[2-3 sentences describing the solution]

**Key Capabilities**:
- [Capability 1]
- [Capability 2]
- [Capability 3]

---

## Expected Impact

**For Customers**:
- [Benefit 1]
- [Benefit 2]

**For Business**:
- [Metric 1]: [Current] → [Target]
- [Metric 2]: [Current] → [Target]

---

## Investment Required

**Timeline**: [X weeks/months]
**Team**: [Y engineers, Z designers]
**Dependencies**: [Key dependencies]

---

## Risks

- [Risk 1]: [Mitigation]
- [Risk 2]: [Mitigation]

---

## Next Steps

1. [Step 1] - **Owner**: [Name] - **By**: [Date]
2. [Step 2] - **Owner**: [Name] - **By**: [Date]

---

**Approval needed from**: [List stakeholders]
```

---

## Launch Documents

### Launch Checklist Template

```markdown
# [Feature Name] Launch Checklist

**Launch Date**: [Target date]
**Launch Tier**: [1 | 2 | 3]
**DRI (Directly Responsible Individual)**: [PM Name]

---

## 8 Weeks Before Launch

### Product Readiness
- [ ] Feature development complete - **Owner**: [Eng Lead]
- [ ] QA passed - **Owner**: [QA Lead]
- [ ] Performance tested (load, stress) - **Owner**: [Eng]
- [ ] Security review completed - **Owner**: [Security]
- [ ] Accessibility audit (WCAG 2.1 AA) - **Owner**: [Design/Eng]
- [ ] Analytics instrumented - **Owner**: [Eng/Data]
- [ ] Error monitoring configured - **Owner**: [Eng]
- [ ] Beta program completed - **Owner**: [PM]

### Documentation
- [ ] User documentation written - **Owner**: [PM/TW]
- [ ] Help center articles published - **Owner**: [Support]
- [ ] API documentation updated - **Owner**: [Eng]
- [ ] Internal FAQ created - **Owner**: [PM]

### Go-to-Market
- [ ] Target audience identified - **Owner**: [PM/Marketing]
- [ ] Positioning & messaging finalized - **Owner**: [PM/PMM]
- [ ] Launch tier confirmed - **Owner**: [PM]

---

## 4 Weeks Before Launch

### Marketing & Communications
- [ ] Launch blog post drafted - **Owner**: [PMM]
- [ ] Email campaign created - **Owner**: [Marketing]
- [ ] Social media calendar - **Owner**: [Marketing]
- [ ] Landing page live - **Owner**: [Marketing/Design]
- [ ] In-app announcements prepared - **Owner**: [PM]

### Sales & Support
- [ ] Sales team trained - **Owner**: [Sales Enablement]
- [ ] Demo environment set up - **Owner**: [Eng]
- [ ] Sales collateral ready - **Owner**: [PMM]
- [ ] Support team trained - **Owner**: [Support Lead]
- [ ] Support runbook created - **Owner**: [Support/Eng]

### Internal
- [ ] Executive team briefed - **Owner**: [PM]
- [ ] Company all-hands announcement scheduled - **Owner**: [PM]
- [ ] Cross-functional teams aligned - **Owner**: [PM]

---

## 1 Week Before Launch

- [ ] Final launch readiness review - **Owner**: [PM]
- [ ] Rollback plan documented - **Owner**: [Eng Lead]
- [ ] On-call schedule set - **Owner**: [Eng Manager]
- [ ] Success metrics dashboard live - **Owner**: [Data/PM]
- [ ] Launch communications scheduled - **Owner**: [Marketing]

---

## Launch Day

- [ ] Feature enabled (gradual rollout or feature flag)
- [ ] Monitor error rates and performance
- [ ] Send internal launch announcement
- [ ] Publish external communications
- [ ] Monitor customer feedback channels

---

## Post-Launch (Week 1)

- [ ] Day 1 metrics review
- [ ] Day 3 metrics review
- [ ] Week 1 metrics review
- [ ] Gather qualitative feedback (support, sales, social)
- [ ] Quick iteration planning based on feedback

---

## Post-Launch (Month 1)

- [ ] 30-day metrics review vs goals
- [ ] Launch retrospective with team
- [ ] Customer success stories documented
- [ ] Iteration roadmap defined
```

---

## Research Reports

### User Research Report Template

```markdown
# User Research Report: [Topic]

**Researcher**: [PM/Researcher Name]
**Date**: [Completion date]
**Research Question**: [What we set out to learn]

---

## Executive Summary

[3-4 sentences: What we learned, key findings, recommendations]

---

## Research Objectives

1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

---

## Methodology

**Research Type**: [Interviews | Usability Testing | Survey | Diary Study | etc.]
**Participants**: [N participants, demographics/segmentation]
**Recruitment**: [How participants were recruited]
**Timeline**: [Research conducted from X to Y]

---

## Key Findings

### Finding 1: [Insight Title]

**Evidence**:
- "[Participant quote]" - Participant 1
- "[Participant quote]" - Participant 3
- Observed in X out of Y sessions

**Impact**: [Why this matters]

**Recommendation**: [What we should do]

### Finding 2: [Insight Title]
[Same structure as Finding 1]

### Finding 3: [Insight Title]
[Same structure as Finding 1]

---

## Opportunities

Based on research, we've identified the following opportunities:

1. **[Opportunity 1]**: [Description]
   - **Severity**: High | Medium | Low
   - **Frequency**: How often users encounter this
   - **Potential Impact**: [Expected improvement]

2. **[Opportunity 2]**: [Description]
   [Same structure]

---

## Recommendations

**High Priority** (Do Now):
- [Recommendation 1]
- [Recommendation 2]

**Medium Priority** (Consider for Next Quarter):
- [Recommendation 3]
- [Recommendation 4]

**Low Priority** (Nice to Have):
- [Recommendation 5]

---

## Appendix

### Participant Demographics
[Table with participant info]

### Interview Guide
[Questions asked]

### Raw Notes
[Link to detailed notes in Dovetail/Notion/etc]

### Recordings
[Links to session recordings, if applicable and with consent]
```

---

## Metrics & Analytics Documentation

### Analytics Specification Template

```markdown
# Analytics Specification: [Feature Name]

**Owner**: [PM Name]
**Engineers**: [Eng Names]
**Date**: [Date]
**Status**: [Draft | Implemented | Verified]

---

## Overview

**Purpose**: [Why we're tracking this feature]
**Key Questions We Want to Answer**:
- [Question 1]
- [Question 2]
- [Question 3]

---

## Events to Track

### Event 1: [Event Name]

**Trigger**: [When this event fires]
**Example**: [User clicks "Share" button in document header]

**Properties**:
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| user_id | string | UUID | Unique user identifier |
| document_id | string | UUID | Document being shared |
| share_method | string | email, link, slack | How document is shared |
| recipient_count | integer | 1-N | Number of recipients |
| has_expiration | boolean | true, false | Whether share link expires |

**Implementation Notes**:
[Any specific implementation details]

### Event 2: [Event Name]
[Same structure as Event 1]

---

## Dashboards

### Dashboard 1: [Feature] Adoption

**Metrics**:
- % of users who used feature (overall and by cohort)
- Frequency of use (uses per active user per week)
- Time to first use (from sign-up)

**Segmentation**:
- By user tier (free, pro, enterprise)
- By platform (web, iOS, Android)
- By cohort (weekly cohorts)

### Dashboard 2: [Feature] Funnel

**Steps**:
1. Viewed feature entry point
2. Started feature setup
3. Completed feature setup
4. Used feature first time
5. Used feature 3+ times (activation)

**Conversion Goals**:
- Step 1 → Step 5: [Target %]
- Time to complete: [Target time]

---

## Success Metrics

**Primary Metric**: [Metric name]
- **Current**: [Baseline]
- **Target**: [Goal]
- **Timeline**: [When]

**Secondary Metrics**:
- [Metric 2]: [Current] → [Target]
- [Metric 3]: [Current] → [Target]

**Guardrail Metrics** (monitor for negative impact):
- [Metric to watch]
- [Metric to watch]

---

## Validation

- [ ] Events firing correctly in development
- [ ] Properties captured accurately
- [ ] Dashboard displays correct data
- [ ] PM verified in production
```

---

## Decision Logs

### Decision Log Template

Use for recording important product decisions, especially when there were trade-offs or multiple options.

```markdown
# Decision Log: [Product Area]

---

## Decision: [Decision Title]

**Date**: [Date]
**Decision Maker**: [Name]
**Stakeholders**: [Names]

**Context**:
[What prompted this decision? What was the situation?]

**Options Considered**:

**Option A**: [Description]
- Pros: [List]
- Cons: [List]
- Effort: [Estimate]

**Option B**: [Description]
- Pros: [List]
- Cons: [List]
- Effort: [Estimate]

**Option C**: [Description]
[Same structure]

**Decision**: [Which option was chosen]

**Rationale**:
[Why this option? What were the key factors?]

**Trade-offs Accepted**:
[What we're giving up or deferring with this choice]

**Success Criteria**:
[How we'll know if this was the right decision]

**Review Date**: [When we'll revisit this decision]

---
```

### Example Decision Log Entry

```markdown
## Decision: Roadmap Prioritization Framework

**Date**: 2025-01-15
**Decision Maker**: Jane Doe (VP Product)
**Stakeholders**: Product Leadership Team

**Context**:
We had inconsistent prioritization across product teams, leading to misalignment with company strategy and difficulty explaining decisions to stakeholders.

**Options Considered**:

**Option A**: RICE Scoring
- Pros: Quantitative, well-known framework, includes confidence
- Cons: Can feel overly prescriptive, debates about scores
- Effort: Low (2 days to roll out)

**Option B**: Weighted Scoring (Custom)
- Pros: Tailored to our specific business, flexible
- Cons: More complex, requires training
- Effort: Medium (1 week to design, 2 weeks to train)

**Option C**: Value vs Effort Matrix
- Pros: Simple, visual, quick
- Cons: Less rigorous, harder to compare across teams
- Effort: Low (1 day)

**Decision**: RICE Scoring

**Rationale**:
- Need consistent framework across all product teams
- Confidence component helps surface uncertainty
- Industry-standard, so new PMs will recognize it
- Can be customized with adjustments to Impact scale for our context

**Trade-offs Accepted**:
- May feel rigid initially (will coach teams to use judgment alongside scores)
- Requires training time (worth the investment for long-term consistency)

**Success Criteria**:
- 100% of product teams using RICE for prioritization by March 1
- Stakeholder satisfaction with roadmap explanations improves by 30%
- Product teams report feeling aligned on priorities (survey in Q2)

**Review Date**: 2025-04-01 (after one quarter of use)
```

---

## Writing Style Guidelines

### Voice & Tone

**Product Documentation Voice**:
- **Clear**: Use simple language, avoid jargon
- **Direct**: Get to the point quickly
- **Professional**: Respectful and competent
- **Evidence-Based**: Back claims with data
- **Action-Oriented**: Make next steps explicit

**Tone Variations by Audience**:

| Audience | Tone | Example |
|----------|------|---------|
| Executive Leadership | Strategic, concise, business-focused | "This initiative will increase NRR by 10 points ($2M ARR impact)" |
| Engineering Team | Precise, technical, collaborative | "We'll need to modify the user schema to support..." |
| Customers | Friendly, helpful, benefit-focused | "This new feature saves you hours each week by..." |
| Stakeholders | Transparent, data-driven, inclusive | "Based on customer feedback (15 interviews), we're prioritizing..." |

### Formatting Best Practices

**Use Headings Hierarchically**:
```markdown
# Document Title (H1 - One per document)
## Major Section (H2)
### Subsection (H3)
#### Detail (H4)
```

**Use Lists for Scannability**:
- Bullet points for unordered items
- Numbered lists for sequential steps
- Checkboxes for action items

**Use Tables for Comparison**:
| Feature | Option A | Option B |
|---------|----------|----------|
| Cost | $X | $Y |
| Time | Z weeks | W weeks |

**Emphasize Strategically**:
- **Bold** for key terms and emphasis
- *Italic* for subtle emphasis or notes
- `Code formatting` for technical terms, metrics names, event names

### Writing Tips

**Be Specific with Numbers**:
❌ "Many users complained about this"
✅ "45% of survey respondents (N=200) rated this workflow as 'frustrating'"

**Use Active Voice**:
❌ "The feature was designed to improve retention"
✅ "We designed this feature to improve retention by 15%"

**Front-Load Important Information**:
❌ "After conducting research and analyzing the data, and considering various options, we decided to build X"
✅ "We decided to build X to solve [problem]. This decision is based on [research] showing [evidence]."

**Be Concise**:
- Aim for 3-5 pages for PRDs
- 1 page for briefs
- 2-3 pages for research summaries
- Longer is not better; respect reader time

**Use Consistent Terminology**:
- Create glossary for product-specific terms
- Use the same term throughout (don't alternate synonyms)
- Define acronyms on first use

### Document Maintenance

**Status Indicators**:
Always include document status:
- **Draft**: Work in progress, not for distribution
- **In Review**: Seeking feedback
- **Approved**: Finalized, ready to execute
- **In Progress**: Being implemented
- **Shipped**: Feature live
- **Archived**: Historical reference only

**Version Control**:
- Include "Last Updated" date on all documents
- For major changes, consider version numbers (v1.0, v2.0)
- Log significant changes in a "Revision History" section

**Linking**:
- Link to related documents liberally
- Keep links up to date (check quarterly)
- Use persistent links (avoid temporary meeting notes links)

---

## Document Checklist

Before publishing any product document:

- [ ] **Clear Purpose**: Reader knows why this document exists
- [ ] **Target Audience**: Clear who should read this
- [ ] **Actionable**: Next steps and owners are explicit
- [ ] **Evidence-Based**: Data and research support claims
- [ ] **Scannable**: Headings, lists, tables make it easy to skim
- [ ] **Concise**: No unnecessary words or sections
- [ ] **Formatted**: Consistent use of headings, emphasis, lists
- [ ] **Linked**: References to supporting docs included
- [ ] **Updated**: Last updated date is current
- [ ] **Reviewed**: At least one other person has reviewed
- [ ] **Accessible**: Shared with appropriate permissions

---

## Recommended Tools

- **Collaboration**: Google Docs, Notion, Confluence, Coda
- **Roadmapping**: ProductBoard, Aha!, Jira Product Discovery
- **Wireframing**: Figma, Sketch, Adobe XD
- **User Flows**: Miro, Lucidchart, FigJam
- **Version Control**: Git (for markdown docs), built-in versioning in Google Docs/Notion

---

## References & Further Reading

- **"Good Strategy Bad Strategy"** by Richard Rumelt - Strategy document writing
- **Google's Design Doc Template** - Technical specification format
- **Amazon's PR/FAQ** - Working Backwards documentation approach
- **Atlassian's Decision Log Template** - Decision documentation
- **Stripe's API Documentation** - Gold standard for technical docs
- **SVPG Articles** - Product management best practices

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Next Review**: 2025-02-19

This standard is a living document. Suggest improvements via the Product team's feedback channel.
