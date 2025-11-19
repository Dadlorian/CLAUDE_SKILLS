# Product Writing Style Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [PRD Writing Standards](#prd-writing-standards)
4. [Strategy Document Guidelines](#strategy-document-guidelines)
5. [Update and Announcement Writing](#update-and-announcement-writing)
6. [Technical Writing Best Practices](#technical-writing-best-practices)
7. [Examples and Templates](#examples-and-templates)
8. [Do's and Don'ts](#dos-and-donts)

## Overview

This style guide establishes standards for all product management written communications, including Product Requirement Documents (PRDs), strategy documents, status updates, and executive announcements. Consistency in writing style enhances clarity, maintains professional standards, and ensures stakeholder understanding.

**Target Audience**: Product managers, designers, engineers, executives, and stakeholders
**Purpose**: Provide clear, actionable product guidance and strategic direction

## Core Principles

### 1. Clarity First
- Use simple, direct language
- Avoid jargon unless necessary; define technical terms
- One idea per sentence
- Shorter paragraphs (3-4 sentences maximum)

### 2. Audience-Centric Writing
- Tailor tone and detail level to your audience
- Executive summary for C-level: high-level impact and business outcomes
- Technical details for engineering: specifications and constraints
- Strategic context for product team: competitive advantages and long-term vision

### 3. Structured Organization
- Use clear headings and subheadings
- Implement logical progression from problem to solution
- Include table of contents for documents over 5 pages
- Use numbered lists for sequential steps; bulleted lists for non-sequential items

### 4. Data-Driven Content
- Support claims with research, metrics, or user feedback
- Cite sources for external data
- Include confidence levels for estimates
- Distinguish between facts, assumptions, and hypotheses

### 5. Active Voice
- Prefer active voice: "We will launch in Q3" not "The launch will occur in Q3"
- Exception: passive voice acceptable for process descriptions: "Requirements are reviewed before implementation"

### 6. Consistent Terminology
- Define key terms in a glossary if document exceeds 10 pages
- Use the same term consistently throughout (not "client," "customer," "user" interchangeably)
- Use title case for proper nouns and product names

## PRD Writing Standards

### Structure and Sections

#### Executive Summary (150-250 words)
**Purpose**: Enable quick understanding without reading full document
**Contains**:
- One-sentence problem statement
- Proposed solution overview
- Expected business impact
- Timeline
- Required resources

**Example**:
"Customers are unable to track subscription renewals, causing 15% churn rate. We will introduce renewal reminders delivered via email and in-app notifications 7, 3, and 1 day before renewal. Expected impact: 3-5% reduction in churn, affecting $2M annual revenue. Estimated effort: 8 weeks. Required: Backend services, Email infrastructure, Analytics instrumentation."

#### Problem Statement (200-300 words)
**Content**:
- User pain point or business challenge
- Current impact with quantified metrics
- Affected user segments or business metrics
- Root cause analysis

**Do's**:
- Base on real user research, support tickets, analytics
- Quantify impact (percentage, absolute numbers, revenue impact)
- Explain why existing solutions are insufficient

**Don'ts**:
- Assume the problem without evidence
- Focus on solution before fully defining the problem
- Include solution ideation in this section

#### Goals and Success Metrics (150-200 words)
**Structure**:
- 2-5 primary success metrics
- Definition: What is being measured and how
- Target: Quantified goal (e.g., "from 15% to 10%")
- Measurement method: How data will be collected
- Timeline: When success will be evaluated

**Example**:

| Metric | Definition | Current State | Target | Timeline |
|--------|-----------|----------------|--------|----------|
| Churn Rate | % of active subscriptions ended in given month | 15% | 10% | 6 months post-launch |
| Email Open Rate | % of reminder emails opened | N/A | 35%+ | Ongoing |
| Conversion Rate | % of users who renewed post-reminder | 65% | 75% | 3 months post-launch |

#### Solution Overview (300-400 words)
**Components**:
- High-level description of solution
- User experience flow
- Key features and capabilities
- Why this solution addresses the problem
- Differentiation from competitive solutions

**Format**:
- Lead with benefits, not features
- Use simple diagrams or wireframe references
- Explain the "why" behind design decisions
- Include constraints considered

#### Out of Scope (100-150 words)
**Purpose**: Set clear boundaries on what will NOT be included
**Include**:
- Features considered but deferred
- Integrations not included in initial version
- User segments not prioritized in Phase 1
- Technical limitations to be addressed later

**Example**:
"Version 1 will not include: SMS reminders (expanding to Phase 2), mobile app notifications (requires mobile app development), integration with third-party email services (planned Q3), customizable reminder timing (MVP uses fixed schedule), subscription management UI for end users (out of scope)."

#### User Flows and Interactions (250-350 words)
**Content**:
- Step-by-step user journey
- System interactions and data flows
- Edge cases and error handling
- User personas addressed

**Format**:
- Use numbered steps for clarity
- Reference diagrams or prototypes
- Include decision points and branches
- Describe fallback scenarios

**Example**:
1. User subscribes to service (active subscription created)
2. System calculates renewal date
3. At renewal date - 7 days: System generates renewal reminder
4. Reminder sent via email with "Renew Now" button
5. User clicks button → redirected to renewal checkout
6. User completes or skips renewal
7. Status recorded in analytics

#### Technical Specifications (200-300 words)
**Content**:
- Architecture overview
- API endpoints or database schema requirements
- Integration points with existing systems
- Performance requirements (latency, throughput)
- Security and compliance considerations
- Data retention and privacy requirements

**Format**:
- Use tables for specifications
- Include code examples for API design
- Reference design docs for detailed technical decisions
- Call out dependencies on other teams

#### Implementation Plan (150-250 words)
**Content**:
- Phased rollout approach
- Key milestones and dates
- Resource requirements
- Dependencies and risks
- Launch criteria and go/no-go decisions

**Table Format**:
| Phase | Features | Timeline | Dependencies | Owner |
|-------|----------|----------|--------------|-------|
| Phase 1 | Email reminders | Weeks 1-4 | Email service API | Engineering |
| Phase 2 | In-app notifications | Weeks 5-8 | Mobile app update | Mobile + Backend |
| Phase 3 | SMS reminders | Weeks 9-12 | SMS provider integration | Backend + Comms |

#### Risk Assessment and Mitigation (150-250 words)
**Structure for each risk**:
- Risk description
- Likelihood (high/medium/low)
- Impact (critical/major/minor)
- Mitigation strategy
- Contingency plan

**Example**:
| Risk | Likelihood | Impact | Mitigation | Contingency |
|------|-----------|--------|-----------|------------|
| Email deliverability issues | Medium | Critical | Pre-delivery testing with multiple ISPs | Partner with email specialist vendor |
| User finds reminders annoying | Medium | Major | A/B test frequency settings | Adjust cadence based on feedback |
| Integration with payment system delayed | Low | Critical | Early API integration testing | Manual reminder workflow |

#### Appendix
- Glossary of terms
- Reference data and research
- Competitive analysis
- User feedback quotes
- Related documentation links

### Tone and Voice for PRDs

**Tone**: Professional, confident, evidence-based
**Voice**: Direct and clear, avoid hedging language
- Weak: "It might be beneficial to consider reminders"
- Strong: "We will implement renewal reminders to reduce churn"

**Formality Level**: Medium-formal
- Appropriate for cross-functional audience
- Avoid excessive technical jargon for non-technical readers
- Use defined terms consistently

## Strategy Document Guidelines

### Document Length and Structure
- **Length**: 5,000-8,000 words for comprehensive strategy
- **Read time**: 30-45 minutes
- **Structure**: Executive summary + 8-12 main sections

### Key Sections

#### Market Context and Opportunity (600-800 words)
- Total addressable market (TAM) analysis
- Market trends and growth drivers
- Competitive landscape
- Customer pain points and unmet needs
- Market segment definitions

#### Product Vision (400-500 words)
- 3-5 year vision statement
- Long-term goals and impact
- Strategic pillars (2-4 main themes)
- Connection to company mission

#### Strategic Priorities (500-700 words)
- 2-3 year roadmap at high level
- Priority ranking and rationale
- Strategic initiatives and their outcomes
- Resource allocation approach

#### Competitive Strategy (400-600 words)
- Competitive positioning
- Differentiation strategy
- Competitive advantages
- Defensibility and moat-building

#### Success Definition (300-400 words)
- Strategic metrics (not just feature metrics)
- Business outcome targets (revenue, market share, growth)
- Customer success metrics
- Financial projections

### Style Guidelines for Strategy Docs
- Use scenario planning or "branching path" approach for uncertain futures
- Include key assumptions and confidence levels
- Separate facts from strategic interpretations
- Use forward-looking language: "We will," "We envision"
- Connect strategy to company values and mission

## Update and Announcement Writing

### Status Update Format (150-400 words)

**Structure**:
1. **Opening**: What period does this cover?
2. **Highlights**: 2-3 key accomplishments with impact
3. **Progress**: What's on track, what needs attention
4. **Blockers**: Any issues preventing progress (with mitigation)
5. **Coming Up**: Next priorities and timeline
6. **Metrics Summary**: Key metrics and trends

**Example Structure**:

```
PRODUCT UPDATE - October 2024

HIGHLIGHTS
✓ Launched renewal reminders feature (estimated 3% churn reduction)
✓ Achieved 98.5% email deliverability rate
✓ Integrated with Stripe payment system

ON TRACK
• In-app notification development (70% complete, ships next week)
• Analytics dashboard expansion (scheduled for November launch)
• Customer success training materials (completion on track for Dec)

NEEDS ATTENTION
• SMS integration delayed by vendor API issues
  - Impact: 2-week delay
  - Mitigation: Prioritizing email-first approach; SMS in Phase 2

NEXT UP
• Deploy in-app notifications (Week 1-2 November)
• Begin A/B testing reminder frequency (Week 3 November)
• Customer feedback synthesis (Ongoing)

KEY METRICS
Renewal Rate: 75% (+5% from last month) | Churn: 11% (-4% from launch)
```

### Announcement Guidelines
- **Subject line**: Action or key result first
- **Opening sentence**: One-sentence summary of news
- **Details**: Context, impact, what's next
- **Call to action**: What do stakeholders need to do?
- **Contact**: Who to reach out to with questions

## Technical Writing Best Practices

### Writing for Clarity
1. **Use the Pyramid Principle**: Lead with conclusions, support with evidence
2. **Front-load important information**: Main idea in first sentence
3. **Use short sentences**: Average 15-20 words
4. **Avoid nominalization**: "Review the requirements" not "The review of requirements"
5. **Use parallel structure**: List items with consistent grammar

### Formatting for Scannability
- Use descriptive headings (not "Overview" but "Market Opportunity for Enterprise Segment")
- Bold key terms and metrics
- Use white space effectively
- Limit paragraph length to 3-4 sentences
- Use bulleted lists for non-sequential information
- Use numbered lists for sequential steps

### Data Presentation
- Explain what data means, not just presenting numbers
- Use tables for comparison, charts for trends
- Include data source and date
- Highlight key findings in caption or surrounding text
- Use consistent color coding (red = concern, green = positive)

### Avoiding Common Pitfalls
- **Ambiguity**: "Several teams" - specify number and names
- **Passive construction**: "It was decided" - by whom, when?
- **Hedging language**: "It seems," "possibly," "may" - be definitive if confident
- **Jargon without definition**: Define industry acronyms on first use
- **Mixed metaphors**: Stick to one conceptual framework

## Examples and Templates

### PRD Template Header

```markdown
# Product Requirement Document: [Feature Name]

**Document Version**: 1.0
**Last Updated**: [DATE]
**Owner**: [Product Manager Name]
**Stakeholders**: Engineering, Design, Marketing, Customer Success
**Status**: [Draft / In Review / Approved / In Development]

## Executive Summary
[50-100 word problem statement and solution overview]

## Problem Statement
[Detailed problem with quantified impact]

## Goals and Success Metrics
[Table with metrics, targets, and measurement methods]
```

### Strategy Document Template

```markdown
# [Product Name] Product Strategy: FY2025-2027

**Version**: 1.0
**Prepared by**: [Product Leader Name]
**Review Cycle**: Quarterly
**Last Updated**: [DATE]

## Executive Summary
[200-250 word overview of strategy direction]

## Market Opportunity
[Analysis of TAM, growth drivers, competitive landscape]

## Product Vision
[3-5 sentence vision statement for long-term direction]

## Strategic Priorities
[2-3 year roadmap with prioritization rationale]

## Success Metrics
[Strategic and financial metrics with targets]
```

### Status Update Template

```markdown
# [Product Area] Update - [Month/Quarter]

**Reporting Period**: [Dates]
**Owner**: [Name]
**Status**: [On Track / At Risk / Off Track]

## Key Achievements
- [Achievement 1 with quantified impact]
- [Achievement 2 with quantified impact]
- [Achievement 3 with quantified impact]

## Progress Dashboard
| Initiative | Status | Progress | Notes |
|-----------|--------|----------|-------|

## Blockers and Risks
| Issue | Impact | Owner | ETA Resolution |
|-------|--------|-------|-----------------|

## Coming Up
- [Next priority with target date]
- [Next priority with target date]

## Metrics Summary
[Key metrics table with trends]
```

## Do's and Don'ts

### DO's

- **DO** start with the business impact: Lead with "why" this matters
- **DO** use specific numbers: "15% churn rate" not "high churn"
- **DO** define acronyms on first use: "Product Requirement Document (PRD)"
- **DO** use consistent terminology throughout documents
- **DO** cite your sources: "Research from Q3 user interviews (20 users surveyed)"
- **DO** include context in tables and charts: "Metric definition: Daily active users, calculated as..."
- **DO** use active voice in most contexts
- **DO** break up long documents with clear section breaks
- **DO** include a document history showing versions and updates
- **DO** review from the reader's perspective: What do they need to know?
- **DO** bold key metrics and important takeaways
- **DO** use present tense for current state, future for planned work
- **DO** include success criteria and go/no-go decision points

### DON'Ts

- **DON'T** use marketing language in PRDs: Avoid "amazing," "revolutionary," superlatives
- **DON'T** include the solution before fully defining the problem
- **DON'T** bury important information in paragraphs: Use headers and bullets
- **DON'T** use unexplained jargon or internal terminology
- **DON'T** mix assumptions with facts: Clearly label speculations
- **DON'T** write in overly formal or stuffy language: Stay accessible
- **DON'T** use vague metrics: "Improve user experience" not "Improve UX significantly"
- **DON'T** make claims without evidence: Every assertion should have basis
- **DON'T** write excessively long paragraphs: Keep them to 3-4 sentences
- **DON'T** skip the "why" behind decisions
- **DON'T** update documents without changing the version number and date
- **DON'T** include sensitive competitive data without clear classification
- **DON'T** write in first person singular: Use "we" and "our team"
- **DON'T** create documents without clear owners and review stakeholders

### Tone Don'ts

- DON'T: "This feature could potentially help with churn."
  - DO: "This feature will reduce churn by an estimated 3-5%."

- DON'T: "We feel that customers need better renewal flows."
  - DO: "Customer interviews (Q3, n=15) identified renewal flows as top pain point."

- DON'T: "The product strategy kind of focuses on enterprise."
  - DO: "The product strategy prioritizes enterprise segment, representing 70% of ARR."

- DON'T: "We might want to consider measuring..."
  - DO: "We will measure success via three primary metrics:"

## Document Governance

### Version Control
- Use semantic versioning: Major.Minor.Patch
- Update version number with any substantial changes
- Include "Last Updated" date in every document

### Review and Approval
- PRDs require approval from: Product Owner, Engineering Lead, Design Lead
- Strategy docs require: VP Product, CFO (for financial projections), relevant team leads
- Status updates for review by: Direct stakeholders, executive sponsors

### Archival
- Store superseded documents with date suffix: "feature_name_archived_2024_11_15.md"
- Maintain decision log showing what was attempted and outcomes
- Link new documents to replaced ones for context

### Distribution
- PRDs: Shared with all implementation team members + stakeholders
- Strategy docs: Executive team + extended product/engineering leadership
- Status updates: Weekly for teams, monthly for executives
- Use templates for consistency across all formats
