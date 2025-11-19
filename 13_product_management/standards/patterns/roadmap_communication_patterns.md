# Roadmap Communication Patterns
## Communicating Product Direction Effectively

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Patterns from Google, Slack, Notion, Stripe, Microsoft, and leading product communication organizations

---

## Overview

A great roadmap is only powerful if communicated effectively. Roadmap communication is not a one-time document dump—it's an ongoing conversation that aligns teams, customers, and stakeholders around product direction.

**Core Principles**:
- Roadmap is communication tool, not constraint
- Multiple formats for different audiences
- Transparent about priorities and trade-offs
- Clear on confidence levels
- Regular updates and feedback loops
- Narrative more important than Gantt charts

---

## Table of Contents

1. [Roadmap Formats](#roadmap-formats)
2. [Audience-Specific Approaches](#audience-specific-approaches)
3. [Crafting the Narrative](#crafting-the-narrative)
4. [Transparency Patterns](#transparency-patterns)
5. [Feedback Loops](#feedback-loops)
6. [Confidence & Commitment Levels](#confidence--commitment-levels)
7. [Executive Communication](#executive-communication)
8. [Stakeholder Alignment](#stakeholder-alignment)
9. [Customer Roadmap Communication](#customer-roadmap-communication)
10. [Internal Team Communication](#internal-team-communication)
11. [Updating and Iterating](#updating-and-iterating)
12. [Common Roadmap Mistakes](#common-roadmap-mistakes)

---

## Roadmap Formats

### Format 1: The Narrative Roadmap

**Best for**: Explaining "why" and strategy

**Structure**:

```
Product Vision (1 page)
├─ Where we're going and why
├─ 3-year north star
└─ Core customer needs we're solving

Annual Themes (4-6 themes)
├─ Q1 Theme: "Build trust through transparency"
│  ├─ Key initiatives (3-5)
│  ├─ Success metrics
│  └─ Why this matters (customer impact)
├─ Q2 Theme: "Scale collaboration"
│  └─ ... (same structure)
└─ Q3-4 Themes

Quarterly Deep Dive
├─ Current quarter detailed plans
├─ Key bets and hypotheses
└─ Measurable outcomes
```

**Slack's Roadmap Example**:
```
Vision: Make work simpler, more pleasant, and more productive

2024 Themes:
1. "Reduce noise" - Help teams focus (Channel organization, AI filtering)
2. "Deepen integrations" - Connect tools users care about (350+ apps)
3. "Simplify workflows" - Automation without code (Bolt improvements)

Why: Customer feedback shows "too many notifications" and "scattered context"
are top friction points. These themes directly address them.
```

### Format 2: Timeline Roadmap

**Best for**: Visual overview of sequence

**Structure**:

```
Q1 2024          Q2 2024          Q3 2024          Q4 2024
┌──────┐       ┌──────┐         ┌──────┐         ┌──────┐
│ Auth │ ──▶  │Collab│ ──▶    │Mobile│ ──▶    │ API  │
└──────┘       └──────┘         └──────┘         └──────┘
Confidence:     Confidence:      Confidence:     Confidence:
100%            75%              50%              25%
(shipping)      (high likelihood) (exploring)     (future vision)
```

**Includes confidence level** (not promised dates)

### Format 3: Maturity Model Roadmap

**Best for**: Showing evolution of capabilities over time

**Structure**:

```
Payment Processing Evolution

Today:          Next Quarter:    Next 6 months:    Next Year:
Credit cards    ✓ Crypto         ✓ BNPL           ✓ Native currencies
Stripe          ✓ Wallets        ✓ Marketplace
PayPal          ACH transfer     ✓ Escrow

(Shipped)       (In progress)    (Planned)        (Exploring)
```

### Format 4: Problem-Centric Roadmap

**Best for**: Explaining what problems you're solving

**Structure**:

```
Problem: Host onboarding takes 45 minutes (drop-off at 30%)

Q1: Simplify host info collection (reduce to 15 min)
- Status: In progress

Q2: Add property photos with AI suggestions
- Status: Planned

Q3: Auto-fill property details via geolocation
- Status: Exploring

Goal: Reduce onboarding time to 10 min, increase completion to 85%
```

---

## Audience-Specific Approaches

### For Executives/Board

**What they care about**:
- Alignment with company strategy
- Revenue/growth impact
- Competitive positioning
- Risk/bets
- Resource requirements

**Format**: 1-page summary + 5-10 min presentation

**Structure**:

```
1. Context (1 min)
   - Market opportunity
   - Customer needs
   - Competitive landscape

2. Strategy (2 min)
   - What we're focusing on
   - Why (revenue, churn, engagement)
   - What we're deprioritizing

3. Initiatives (3 min)
   - Top 3-5 bets
   - Revenue impact if successful
   - Timeline and confidence

4. Ask (1 min)
   - What resources needed
   - Any decisions required
```

**Example narrative**:
```
"We're seeing enterprise customers struggle with data governance
(regulatory requirement we didn't notice before). This is a $2M ARR
at-risk issue. We're committing Q3-Q4 to native data residency
(initially EU, then APAC). This requires 2 additional engineers
and delays mobile app 6 weeks. Expected impact: save $2M ARR,
enable additional $5M in new enterprise deals."
```

### For Customers

**What they care about**:
- Does roadmap solve their problems?
- When will features they requested ship?
- How does it compare to competitors?

**Format**: Public roadmap + quarterly email + feature voting

**Structure**:

```
Public roadmap (shared link)
├─ Quarterly themes
├─ Key features in-flight
├─ Customer requests being built
└─ Transparency: What's not happening (deprioritization)

Quarterly email to high-value customers
├─ Recap of what shipped last quarter
├─ Rationale for top 3 things coming this quarter
├─ "You asked for X, here's where we are"
└─ Feedback: "What should we prioritize?"

Feature voting (ProductBoard, Canny)
├─ Customers upvote features they want
├─ PM responds: "We're planning this Q2 based on customer demand"
└─ Transparency: "We've decided not to build this, here's why"
```

**Example - Figma's Customer Roadmap**:
- Public roadmap accessible to all users
- Quarterly themes explaining rationale
- Customer comments on each feature (visible)
- PM responses to top questions
- Clear "deprioritized" section (vs. just ignoring)

### For Engineering Teams

**What they care about**:
- Clear specs and requirements
- Dependencies and sequencing
- Tech debt decisions
- Architecture implications

**Format**: Detailed roadmap + design docs + arch review

**Structure**:

```
Quarterly roadmap (high-level)
├─ Key initiatives + business rationale
└─ Why these are sequenced this way

Sprint planning (2-week view)
├─ Detailed spec for each story
├─ Tech debt reduction targets
└─ Infrastructure changes needed

Architecture/Tech Review
├─ Any major tech decisions needed
├─ Implications for future work
└─ Debt paydown plan
```

**Example narrative**:
```
"Q3 focus: Real-time collaboration at scale
- Initiative 1: Rewrite sync engine (improve latency, fix bugs)
  Why: Current Redis approach breaks at 50M concurrent users
  Impact: Unblocks mobile, enterprise deal

- Initiative 2: Add WebSocket support
  Why: Reduces latency from 500ms to 50ms
  Blocker for Asia expansion (high latency regions)

- Deprecation: Remove old REST API (June 30)
  Why: Maintenance burden, only 2% of users still use
  Migration plan: Detailed guide, support window until August
```

### For Sales/Marketing

**What they care about**:
- Customer-facing benefits
- Messaging/positioning
- Timing for campaigns
- Competitive response

**Format**: Benefits-focused summary + messaging guide

**Structure**:

```
Coming next quarter (customer-facing)
├─ Feature name and customer benefit
├─ Why customers want this
├─ How to position vs. competitors
└─ Timing for messaging

Messaging guide
├─ Internal positioning
├─ Customer objections this solves
├─ Talking points for sales calls
└─ Demo script highlights
```

**Example narrative**:
```
"Q3: Offline editing for mobile

Customer benefit: Keep working on flights/trains/low-connectivity areas
Positioning: "Never lose progress, always available"
Competitive: Competitors offer local cache only - ours syncs when online
Messaging angle: "For distributed teams who work anywhere"

Sales talking point: "Address customer objection: 'I work offline a lot,
need to know I won't lose changes'"
```

---

## Crafting the Narrative

### The Power of "Why"

**Weak narrative**: "Q2: Build dark mode, add webhooks, improve search"

**Strong narrative**:
```
"Q2: Delight power users while expanding to new segments

Dark mode: Power users requested heavily (70% of feature requests).
This differentiates us from competitors and improves retention.
Expected impact: +0.8% retention, +$500K ARR from reduced churn.

Webhooks: Enterprise customers need integrations. Currently building
custom integrations takes weeks. Open webhooks let customers build
themselves. Expected impact: 10+ new enterprise customers, $2M ARR.

Search improvements: Analysis shows 20% of DAU frustrated with search
relevance. Rebuilt index with ML ranking. Expected impact: +0.5%
engagement, faster onboarding for new users.
```

### Structure of Strong Narrative

**Opening (Context)**:
- What's the customer need?
- Why is this important?
- What's the opportunity?

**Strategy (Approach)**:
- What are we building?
- Why this approach (vs. alternatives)?
- When?

**Impact (The Ask)**:
- What metrics improve?
- Business impact?
- What resources needed?

**Closing (Why You Should Care)**:
- "This unblocks 3 enterprise deals"
- "This is table-stakes for retention"
- "This is defensive vs. competitor"

### Example: Google's Roadmap Narrative

```
Platform Theme: "AI-First Productivity"

Why: Our research shows knowledge workers spend 3+ hours daily on
context switching (email, calendar, documents, chat). AI can
consolidate this. Early experiments show 15% productivity improvement.
Users increasingly expect AI assistance (Copilot, ChatGPT changing
expectations).

What:
- Smart compose across Gmail, Docs, Slides (Q1-Q2)
- AI search across all workspace apps (Q2-Q3)
- Proactive scheduling/meeting prep (Q3-Q4)

Impact:
- Competitive parity with Microsoft Copilot
- +2% user engagement (estimated from pilots)
- Opens premium tier ("Workspace Intelligence")
- Expected +$2B annual revenue opportunity

Why now: Market momentum, customer demand, technical feasibility
(our ML models are now accurate enough)
```

---

## Transparency Patterns

### Pattern 1: What We're NOT Doing

**Powerful practice**: Explicitly state deprioritizations

**Why**:
- Removes ambiguity (customers know it won't ship)
- Shows honest prioritization
- Prevents false hope
- Demonstrates clear thinking

**Format**:

```
Deprioritized features (decided not to build):

❌ Offline sync for all features
   Why: Only 2% of users need this, high complexity, low ROI
   Alternative: Offline editing for read-only mode (shipping Q2)

❌ Native iPad app
   Why: 70% of mobile users on phones, web app works well
   Focus: Optimize iPad web experience instead

❌ Self-hosted option
   Why: Infrastructure burden >> customer demand
   Customer quote: "Cloud works fine for us"
```

**Slack example**:
Slack is explicit about what they won't build:
- Self-hosted version (once, now cloud-only)
- End-to-end encryption for all messages (enterprise requirement, not general)
- RSS feeds (deprecated, using alternatives like integrations)

### Pattern 2: Confidence Levels

**Don't promise with same confidence level as certainties**

**Framework**:

```
High Confidence (90%+)
├─ "Shipping this quarter" - In progress/final testing
└─ Track: "When exactly will this launch?"

Medium Confidence (60-90%)
├─ "Planned for Q2" - Design approved, building soon
└─ Track: "Q2 early/mid/late"

Low Confidence (30-60%)
├─ "Exploring in Q3" - Hypothesis formed, not yet committed
└─ Track: "We'll decide in Q1 if we build this"

Hypothesis (< 30%)
├─ "We're researching if we should build this"
└─ Track: "Research findings in 4 weeks"
```

**Google's approach**:
- Green (committed, 95%+ probability)
- Yellow (planned, 70-80% probability)
- Red (exploring, 40-50% probability)
- Gray (future vision, <30% probability)

**Customers understand**: "Exploring" ≠ "Coming soon"

### Pattern 3: Change Logs

**Communicate what changed from last roadmap**

**Format**:

```
Quarterly Roadmap - What Changed from Last Quarter

Accelerated:
✓ Dark mode (moved from Q2 → Q1)
  Reason: Customer demand higher than expected, team velocity higher

Delayed:
⏱ Mobile app (moved from Q2 → Q3)
  Reason: Discovered critical architecture gaps, need to refactor

Deprioritized:
✗ Webhooks (removed from roadmap)
  Reason: Built API gateway instead, better customer solution

New:
+ AI-powered suggestions (added this quarter)
  Reason: Customer feedback, competitive response
```

**Why this matters**:
- Shows you listened
- Demonstrates responsiveness
- Sets expectations (things change)
- Shows good judgment (deprioritizations smart)

---

## Confidence & Commitment Levels

### Commitment Matrix

```
                 HIGH COMMITMENT        MEDIUM COMMITMENT      LOW COMMITMENT
                 (Will ship)             (Strong intent)        (Exploring)
────────────────────────────────────────────────────────────────────────────

Timeline:       This quarter            Next 2 quarters        This year

Language:       "Shipping Q1 2"          "Planned Q2-Q3"       "Exploring Q3"
                "Available March 15"     "TBD - depends on X"  "Investigating"

Risk of lag:    Rare                    Possible (20%)        Likely (50%)

What to do
if delayed:     Communicate change      Update quarterly       Move to next year
                immediately              in reviews             review

Track:          Weekly sprint progress   Monthly review         Quarterly survey
```

**Important**: Don't increase commitment to satisfy customers

**Antipattern**:
```
Customer: "When is feature X shipping?"
PM: "Q3" (guessing, actual confidence 40%)
Result: Feature ships Q4 or doesn't ship
Customer: Broken trust, churn risk
```

**Better**:
```
Customer: "When is feature X shipping?"
PM: "We're exploring X. Customer demand is strong. If we decide to
build it, probably Q4. We'll have decision in next 2 months."
Result: Clear expectations, customer understands uncertainty
Outcome: Even if delayed, expectations were set properly
```

---

## Executive Communication

### Quarterly Roadmap Sync with Leadership

**Format**: 20-30 minute meeting quarterly

**Prep**: 1-page summary (sent 48 hours before)

**Structure**:

**1. Opening (2 min)**
- One sentence: "Strategic focus this quarter"
- Example: "Expand enterprise, build for scale, delight power users"

**2. Last Quarter Review (3 min)**
- What shipped: List 3-5 top things
- Impact: Revenue, retention, engagement improvements
- Misses: What was supposed to ship but didn't, why

**3. Strategic Context (3 min)**
- Market changes
- Competitive moves
- Customer feedback themes

**4. Bets & Initiatives (8 min)**
- Top 3-5 initiatives
- For each: Hypothesis, resources needed, confidence, timeline
- Risk assessment: What could go wrong?

**5. Resource Ask (2 min)**
- Headcount: Do we need more people?
- Budget: Special tools, vendor costs?
- Executive decision: Anything blocking us?

**6. Questions & Discussion (5-10 min)**

### One-Pager Template

```
PRODUCT ROADMAP SUMMARY - Q2 2024

Vision:
[One sentence on where we're going]

Strategic Focus This Quarter:
[Two key themes]

Key Initiatives:
1. [Initiative] - [Timeline, Confidence]
   Hypothesis: If we build this, [metric] improves by [X]%
   Business impact: [Revenue/retention/engagement]
   Risk: [What could go wrong]

2. [Initiative] - [Timeline, Confidence]
   ...

Resource Ask:
- Need: [X engineers, Y budget]
- Decision needed: [Any roadblocks?]

Key Metrics We're Watching:
- [Metric 1]: Currently [X], target [Y]
- [Metric 2]: Currently [X], target [Y]
```

---

## Stakeholder Alignment

### Cross-Functional Alignment Rhythm

**Monthly (PM + Engineering lead)**:
- 30 min sync
- Confirm current sprint
- Discuss blockers
- Update staffing estimates

**Quarterly (PM + Eng + Design + Marketing)**:
- 60 min session
- Roadmap review
- Alignment on themes
- Marketing planning for launches

**Semi-Annually (Full leadership)**:
- 90 min session
- Deep strategy alignment
- Resource allocation
- Long-term vision check-in

### Addressing Conflicting Priorities

**Situation**: Sales wants feature X, Engineering wants to refactor Y, CEO wants feature Z

**Framework**:

```
1. Surface all requests explicitly
2. Explain rationale for each
3. Discuss trade-offs openly
4. Make decision together
5. Communicate decision widely
```

**Example dialogue**:

```
Sales: "Enterprise customer wants SSO. Deal is $500K"
Engineering: "System needs refactoring first. Current architecture breaks"
CEO: "We need mobile app to compete"

Decision-making:
- Estimate: SSO = 3 weeks, Refactor = 4 weeks, Mobile = 8 weeks
- Capacity: Team of 6 engineers = 24 weeks/quarter
- Option 1: SSO + Refactor only (7 weeks), delay Mobile (deprioritize)
- Option 2: SSO + Mobile (11 weeks), skip Refactor (technical debt)
- Option 3: SSO in 2 weeks (with hacky solution), commit to Refactor Q2

Decision: Option 3 - Ship SSO quickly to close deal, commit to
refactoring Q2 before it becomes critical.

Communication:
- Sales: "We're shipping SSO in 2 weeks for your deal"
- Eng: "Q2 is refactoring focus, will prevent future technical issues"
- Mobile: "Pushed to Q3, still critical priority"
```

---

## Customer Roadmap Communication

### Public Roadmap Best Practices

**What to include**:
- ✓ Major features being built (quarterly level)
- ✓ Themes explaining rationale
- ✓ Customer feedback being addressed
- ✓ Deprioritized items (what we won't build)

**What NOT to include**:
- ✗ Exact dates (say "Q2" not "May 15")
- ✗ Detailed specs (too much detail, changes often)
- ✗ Engineering-focused items (not customer-relevant)
- ✗ Bugs/maintenance (expected, don't need roadmap)

### Tools for Public Roadmap

**Option 1: ProductBoard**
- Centralized feature request voting
- Roadmap view connecting features to themes
- Customer comments on features
- Integration with public roadmap

**Option 2: Canny**
- Simple voting on feature requests
- Public roadmap display
- Customer engagement

**Option 3: Internal custom site**
- Tailored to your brand
- Full control
- More work to maintain

### Communication Cadence

**Monthly email to customers**:
```
Subject: Product Update - Here's What We Built This Month

Hi [Customer name],

This month, we shipped:
- [Feature A]: Addresses your feedback about [problem]
- [Feature B]: Improves [workflow]

Coming next month:
- [Feature C]: You requested this, excited to show you early next week

Questions? Feedback? Reply to this email, would love to hear from you.

[PM name]
```

**Quarterly webinar**:
- Demo of what shipped
- Explain what's coming
- Q&A from customers

**6-month deep-dive (executive customer meetings)**:
- Review of full roadmap
- "What's important to you?"
- Get feedback on priorities

### Handling Feature Requests

**For requests we're planning**:
```
Thank you for the request! This aligns with customer feedback we've
heard from multiple customers. We're planning to tackle this in Q2.
I'll update you when we start building, and would love to include you
in testing.
```

**For requests we won't build**:
```
Thanks for the suggestion. We decided not to prioritize this because
[reason: low demand, doesn't fit roadmap, alternative exists]. Here's
how you can [workaround/alternative]. Open to discussing if you have
thoughts on [aspect we're considering].
```

**For requests we're exploring**:
```
Great request. This is on our radar as a potential future initiative.
We're currently researching [related feature] which might address your
underlying need. Check back in [timeframe] when we'll have decided if
we're building this.
```

---

## Internal Team Communication

### Weekly Standup Communication

**What to share**:
- What shipped this week
- What's in progress (top 3 items)
- Blockers
- What you need from team

**Example**:
```
Shipped:
- User migration tool (went out in beta)

In progress:
- Dark mode (design finalized, building)
- Webhooks API (50% done, integrations work)
- Search indexing (testing new ML model)

Blockers:
- Need infrastructure approval for database increase
- Waiting on design feedback on payment flow

Need:
- Can someone look at performance regression in search?
```

### Monthly All-Hands Communication

**Content**:
- Recap of month (launched, metrics)
- Themes for coming month
- Recognitions
- Company/market context

**Format**: 30 minute meeting

```
[5 min] Opening & context
        "We're focusing on enterprise growth..."

[10 min] Product recap
         "Last month: shipped mobile, onboarding improved"

[10 min] Roadmap preview
         "Next month: focusing on collaboration, payments"

[5 min] Q&A
```

### Engineering Deep-Dive Meeting

**Quarterly (90 min)**

**Agenda**:
1. **Roadmap overview** (20 min)
   - Themes and top initiatives
   - Why these matter

2. **Technical deep-dives** (50 min)
   - Architecture decisions needed
   - Tech debt paydown plan
   - Infrastructure requirements
   - Skills/learning needed

3. **Q&A and discussion** (20 min)

---

## Updating and Iterating

### Roadmap Review Rhythm

**Monthly (with engineering)**:
- 30 min sync
- Confirm what's in progress
- Update timelines if needed
- Identify risks early

**Quarterly (public update)**:
- Share what's changed
- New items added
- Deprioritized items
- Updated timelines

**Annually (strategic review)**:
- Full roadmap refresh
- Vision check
- Long-term priorities
- Resource allocation

### Communicating Changes

**When shipping early**:
```
"Great news! Dark mode shipped this week (we originally planned Q2).
Team velocity was higher than expected, and we found a clever
architectural approach. Now rolling out to all users."
```

**When pushing back timeline**:
```
"Webhooks update: We discovered our current auth system wasn't designed
for webhooks. Rather than ship a half-solution, we're refactoring first
(3 weeks). Webhooks now ship late April instead of early April."
```

**When deprioritizing**:
```
"Feature decision: We've decided not to build offline sync this year.
Why: Only 5% of users requested it, engineering complexity is high,
and we have higher-impact initiatives. Alternative: We'll improve
caching to reduce data usage in low-connectivity situations."
```

---

## Common Roadmap Mistakes

### ❌ Mistake 1: Too Detailed

**Problem**: Roadmap has 50 items, all with exact dates

**Why it's wrong**:
- Changes constantly (looks unstable)
- Creates false commitment (late items feel failed)
- Too much for people to parse

**Solution**:
- 10-15 items max
- Focus on themes, not list
- Use confidence levels
- Let quarters evolve

### ❌ Mistake 2: No "Why"

**Problem**: "Q2: API improvements, dark mode, performance work"

**Why it's wrong**:
- No context
- Doesn't help people understand priorities
- Hard to decide what to cut

**Solution**:
- Start with "why"
- Customer problems being solved
- Business impact
- Strategic context

### ❌ Mistake 3: Feature List Not Strategy

**Problem**: Roadmap is random list of customer requests

**Why it's wrong**:
- Reactive, not strategic
- No coherent direction
- Doesn't guide difficult trade-offs

**Solution**:
- Organize around themes
- Group features by problem
- Focus on outcomes, not outputs
- Make hard deprioritization choices

### ❌ Mistake 4: Over-promising

**Problem**: "Shipping webhooks, GraphQL, mobile app, redesign Q1"

**Why it's wrong**:
- When invariably delayed, credibility drops
- Team feels pressure to cut quality
- Customers disappointed when reality doesn't match

**Solution**:
- Under-promise, over-deliver
- Be honest about capacity
- Plan for 60-70% of capacity only (meetings, bugs, learning)
- Build buffer for unknowns

### ❌ Mistake 5: Not Transparent About Changes

**Problem**: Different stakeholders get different roadmaps

**Why it's wrong**:
- People feel deceived
- Creates alignment issues
- Prevents good prioritization

**Solution**:
- One roadmap, multiple formats
- Same information to all
- Share change logs (what moved, why)
- Explain trade-offs openly

### ❌ Mistake 6: No Feedback Loop

**Problem**: Share roadmap, then never ask what customers/team thinks

**Why it's wrong**:
- Miss feedback
- People feel unheard
- Roadmap becomes less relevant

**Solution**:
- Ask: "What should we prioritize?"
- Quarterly reviews with customers
- Team retrospectives on roadmap accuracy
- Iterate based on feedback

---

## Summary

**Roadmap Communication Best Practices**:

1. **Start with why**: Explain problems being solved, not just features
2. **Use appropriate detail**: Narrative + visual for different audiences
3. **Be transparent**: Include what you won't build, confidence levels
4. **Update regularly**: Monthly reviews, quarterly major updates
5. **Include feedback loops**: Ask what people think
6. **Tailor by audience**: Executives, engineers, customers see different formats
7. **Communicate changes**: Explain what moved and why
8. **Under-promise, over-deliver**: Build credibility through consistency

**Remember**: Great roadmap communication is about alignment and transparency, not controlling expectations.

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Next Review**: 2025-02-19

**Further Reading**:
- "Radical Candor" by Kim Scott - Transparent communication
- Slack's approach to customer feedback and roadmapping
- Google's quarterly planning and communication
- "The Lean Product Playbook" - Outcome-focused planning
