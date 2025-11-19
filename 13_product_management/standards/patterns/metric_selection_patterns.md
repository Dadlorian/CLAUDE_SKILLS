# Metric Selection Patterns
## Choosing the Right Metrics and North Star Frameworks

**Version**: 1.0
**Last Updated**: 2025-11-19
**Authority**: Patterns from Spotify, Airbnb, Amazon, Google, Netflix, and leading data-driven product organizations

---

## Overview

Choosing the right metrics is one of the highest-leverage PM decisions. The metrics you track shape what teams optimize for, which shapes product direction, which shapes company success.

**Core Principles**:
- One North Star metric per product
- Leading indicators paired with lagging indicators
- Align incentives through metrics
- Measure outcomes, not outputs
- Revisit metrics as product evolves
- Act on metrics (don't just measure)

---

## Table of Contents

1. [The Metric Framework](#the-metric-framework)
2. [North Star Metrics](#north-star-metrics)
3. [Leading vs Lagging Indicators](#leading-vs-lagging-indicators)
4. [Pirate Metrics (AARRR)](#pirate-metrics-aarrr)
5. [Metric Categories](#metric-categories)
6. [Metric Selection Process](#metric-selection-process)
7. [Common Metric Mistakes](#common-metric-mistakes)
8. [Metric Trees](#metric-trees)
9. [Dashboarding](#dashboarding)
10. [Metric Evolution](#metric-evolution)

---

## The Metric Framework

### Hierarchy of Metrics

```
        North Star Metric
              ↓
    Key Performance Indicators (KPIs)
         ↙         ↓        ↘
    Acquisition  Engagement  Retention
         ↓         ↓        ↓
     Sub-metrics Sub-metrics Sub-metrics
     (detailed)  (detailed)  (detailed)
```

### North Star Metric Definition

**North Star**: Single metric that represents success of your product

**Characteristics**:
- Directly impacts revenue/viability
- Customers want what drives this metric
- Teams across company can influence it
- Measurable and understandable
- Stable (doesn't change every quarter)

---

## North Star Metrics

### Examples of Great North Stars

**Spotify**: Monthly Active Users (MAU) with usage frequency
- Why: If users listen to Spotify monthly, they're engaged
- Teams aligned: Content drives discovery (more listening)
  UX reduces friction (more listening), Ads/Premium monetize (more listening)

**Airbnb**: Nights Booked
- Why: Direct proxy for marketplace health and revenue
- Teams aligned: Host growth (more supply), Guest acquisition (more demand)
  Quality/trust (more willingness to book), Pricing (optimizes bookings)

**Netflix**: Streaming Hours
- Why: Direct proxy for user engagement and retention
- Teams aligned: Content (better shows = more hours)
  UX (better recommendations = more hours)
  International expansion (grow the base watching)

**Amazon**: Customer Orders
- Why: Fundamental unit of business success
- Teams aligned: Selection/Search (more orders), Price (competitive)
  Logistics (fast = more orders), Prime (lock-in = more orders)

**Slack**: Daily Active Users (DAU) / Monthly Active Users (MAU)
- Why: Engaged teams mean stickiness
- Teams aligned: Features (more useful = daily use)
  Performance (faster = more daily use)
  Integrations (more value = daily use)

**Figma**: Projects Created + Collaborative Sessions
- Why: Indicates adoption and team usage
- Teams aligned: Feature completeness (more projects created)
  Collaboration (team sessions)
  Performance (fast = more frequent use)

### North Star Anti-Patterns

❌ **Too many North Stars**:
```
Problem: "MAU, DAU, engagement, revenue, retention, NPS"
Issue: Can't optimize for 6 things, team confused on priorities

Solution: One primary North Star, others are supporting KPIs
```

❌ **Vanity metric as North Star**:
```
Problem: Traffic, page views, signups
Issue: Easy to game, doesn't correlate with real success

Example: 1M signups but 0% activation = meaningless
Solution: Choose metric that requires real value delivery
```

❌ **Metric not controllable by team**:
```
Problem: "Stock price" as product team North Star
Issue: Stock price driven by many factors, can't control it

Solution: Choose metric product team can directly influence
```

❌ **Too granular**:
```
Problem: "Checkout button clicks in US on Safari on weekdays"
Issue: Too specific, hard to trend, noisy

Solution: Use cohort analysis instead (by geography, browser)
```

---

## Leading vs Lagging Indicators

### Key Concept

**Lagging indicators**: Measure outcomes (past results)
- Revenue
- Customer churn
- Retention at 30 days

**Leading indicators**: Predict future outcomes
- Feature adoption rate
- NPS scores
- Time to first value

### Example: E-commerce

```
Leading Indicators                 Lagging Indicators
(predict success)                  (measure success)
     ↓                                    ↓

Product page views                 Monthly revenue
    ↓ (improves)                       ↑
    │
    ├─→ Cart adds increase             │
    │   ↓ (improves)                   │
    │                                   │
    ├─→ Checkout completion            │
    │   ↓ (improves)                   │
    │                                   │
    └──→ Orders increase    ──────────→ │
         (lagging indicator catches up)
```

**Why both matter**:
- **Leading indicators**: Fast feedback (daily), guide actions
- **Lagging indicators**: True success measure, confirm leading indicators

### Airbnb Example

**Leading indicators**:
- Host response time to messages (predicts booking completion)
- Review quality (predicts future bookings)
- Photo quality (predicts click-through to booking)

**Lagging indicators**:
- Booking conversion rate (2+ week lag)
- Revenue per host (1+ month lag)

**Process**:
1. Improve photo AI → Leading indicator improves (next day)
2. Watch → Booking conversion improves (1-2 week lag)
3. Confirm → Revenue grows (1+ month lag)

---

## Pirate Metrics (AARRR)

**Framework**: Track full customer journey

```
Awareness → Acquisition → Activation → Retention → Revenue
(where do     (how do     (do they   (do they   (are they
 people learn people    use the    come back? paying?)
 about us?)  sign up?) product?)
```

### Detailed Breakdown

**Awareness**:
- How do people discover your product?
- Metrics: Website traffic sources, organic search visibility, brand awareness

**Example - Figma**:
- Organic search for "design tool" (60% of new users)
- Designer community recommendations (30%)
- Company website (10%)

**Acquisition**:
- How many people sign up?
- Metrics: Signups per week, signup conversion rate by source, CAC (customer acquisition cost)

**Example - Slack**:
- 500K signups/week (enterprise and teams)
- Freemium → paid conversion rate: 5%
- CAC: $50 (organic majority, very efficient)

**Activation**:
- What fraction actually use the product?
- Metrics: % who complete onboarding, time to first value, activation rate by cohort

**Example - Notion**:
- Template gallery usage (drives faster activation)
- Database creation (core value unlocked)
- Invite teammates (activates full value)
- Activation rate: 40% of signups become active within 1 week

**Retention**:
- Do users come back?
- Metrics: Day 1/7/30 retention, churn rate, cohort analysis

**Example - Netflix**:
- Day 1 retention: 65%
- Day 7 retention: 45%
- Day 30 retention: 30%
- Annual retention: 15% (highly engaged, subscribed)

**Revenue**:
- Are they paying?
- Metrics: ARPU (average revenue per user), LTV (lifetime value), payback period

**Example - Spotify**:
- ARPU: $5.25 (mix of free/premium)
- Premium ARPU: $9.60
- Avg customer lifetime: 3 years = $29 LTV
- CAC: $1-3 (very efficient)

---

## Metric Categories

### Engagement Metrics

**What they measure**: How actively users use your product

**Common metrics**:
- Daily/Monthly Active Users (DAU/MAU)
- Session frequency (sessions per user per week)
- Session length (minutes per session)
- Feature adoption rate (% using feature)
- NPS (Net Promoter Score, -100 to +100)

**When to use**:
- Early stage (before revenue)
- Assessing product value
- Measuring feature impact

**Example metrics**:
```
Netflix: Streaming hours per user per month
  Industry benchmark: 5-10 hours
  Healthy Netflix: 15+ hours
  Shows content resonates

Slack: Messages per user per day
  Industry benchmark: 10-20 messages
  Healthy Slack workspace: 50+ messages
  Shows team is actually using
```

### Retention Metrics

**What they measure**: Do customers stick around?

**Common metrics**:
- Retention rate (% of users active after X days)
- Cohort retention (track specific user cohorts over time)
- Churn rate (inverse of retention)
- Customer lifetime value (LTV)
- Return user rate

**Cohort Analysis**:

```
Sign-up cohort    Day 1    Day 7    Day 30    Day 90
Jan 2024 cohort   100%     45%      22%       8%
Feb 2024 cohort   100%     47%      24%       9%
Mar 2024 cohort   100%     46%      23%       8%

Interpretation: Retention stable (not degrading)
Opportunity: D30 retention 22% is low (industry avg 40%)
Action: Improve onboarding → activate more users → improve retention
```

**Why cohorts matter**:
- Isolates user group effects
- Shows if product improving or degrading
- Reveals when key moments happen

### Conversion Metrics

**What they measure**: What % move to next stage?

**Common metrics**:
- Conversion rate (% completing action)
- Funnel drop-off (where do people abandon?)
- Task completion rate

**Funnel Analysis**:

```
Awareness → Landing page → Signup → Activation → Payment → Customer
100%            80%          15%       8%         3%        1.2%

Bottlenecks:
- Landing page: 20% drop (is page unclear?)
- Signup → Activation: 45% don't activate (onboarding broken?)
- Activation → Payment: 60% don't convert (value proposition unclear?)

Opportunities (by impact):
1. Fix onboarding → 5% absolute improvement in D1 activation
2. Simplify signup → 2% absolute improvement
3. Better free trial messaging → 1% absolute improvement
```

### Growth Metrics

**What they measure**: How fast is business growing?

**Common metrics**:
- Monthly recurring revenue (MRR)
- Annual run rate (ARR)
- Growth rate (% month-over-month or year-over-year)
- Net revenue retention (NRR, for SaaS)
- Market share

**Net Revenue Retention**:
```
NRR = (Beginning MRR + New MRR - Churned MRR) / Beginning MRR × 100

Example:
- Jan MRR: $1M
- New customers (Feb): +$200K
- Churn (Feb): -$50K
- Feb MRR: $1.15M
- NRR = (1M + 200K - 50K) / 1M = 115%

Interpretation: For every $100 of current business, adding $15 net.
This is very healthy (over 100% is growing despite churn)
```

---

## Metric Selection Process

### Step 1: Define Goals

**Ask yourself**:
- What is the product trying to accomplish?
- How will we know if we're successful?
- What does a healthy product look like?

**Example - Slack**:
```
Goal: Build tool that replaces email for team communication
Success: Teams use Slack daily instead of email
Healthy product: High DAU/MAU ratio (40%+)
```

### Step 2: Identify Key Behaviors

**List behaviors that indicate success**:

Example - Notion:
```
Success behaviors:
- User creates a page (proof of value)
- User invites teammates (validates use case)
- User returns weekly (stickiness)
- User upgrades to paid (monetization)
- User shares publicly (advocacy)
```

### Step 3: Choose North Star

**Pick one metric that best indicates overall success**

**Process**:
- List candidate metrics
- Score each on: customer value, team controllability, measurability, stability
- Choose highest score

**Notion example**:
```
Candidates:
1. Pages created - shows value, controllable, easy to measure ✓✓✓
2. Revenue - easy to measure, not controllable by product team ✗
3. NPS - customer value clear, hard to measure precisely
4. DAU/MAU - shows engagement, impacted by feature/marketing

Winner: Pages created + collaborative spaces
Why: Best indicator that teams finding value
```

### Step 4: Define Supporting KPIs

**Choose 5-7 metrics that contribute to North Star**

Example - Spotify:

```
North Star: Monthly Streaming Hours

Supporting KPIs:
1. New user activation (% who stream in first 7 days) - acquisition
2. Content library growth (songs/artists) - supply-side
3. Playlist creation rate - engagement/usage
4. Social shares (% of users sharing playlists) - retention/growth
5. Premium subscriber churn rate - revenue
6. Discovery playlist effectiveness (discovery weekly plays/total plays) - retention
```

**For each KPI**:
- Metric definition (exactly how calculated)
- Measurement method (where tracked)
- Healthy target (what's "good")
- Owner (which team drives this)

### Step 5: Implement & Monitor

**Set up dashboards**:
- Daily view of North Star
- Weekly view of KPIs
- Monthly deep-dive analysis

**Review cadence**:
- Daily: Check for anomalies
- Weekly: Team standup reviews
- Monthly: Deep analysis + decisions
- Quarterly: Strategic review + adjustments

---

## Common Metric Mistakes

### ❌ Mistake 1: Vanity Metrics

**Problem**: Tracking metrics that look good but don't mean much

**Examples**:
- Total signups (without activation)
- Page views (without action)
- Email opens (without conversions)

**Why it's wrong**:
- Can grow without building value
- Deceives leadership and investors
- Wrong incentives for team

**Example**:
```
"We grew signups 50%!"
But: 95% don't activate
Reality: Not actually growing
```

**Solution**: Combine with engagement metric
```
"We grew activated users 20%"
(Only counts users who found value)
```

### ❌ Mistake 2: Too Many Metrics

**Problem**: Tracking 30+ metrics

**Why it's wrong**:
- Team confused on priorities
- Hard to impact everything at once
- Analysis paralysis

**Solution**:
- 1 North Star
- 5-7 Supporting KPIs
- 3-5 Deep-dive metrics (specific to current initiative)

### ❌ Mistake 3: Metric Not Causally Related

**Problem**: Tracking "email opens" as success when goal is "bookings"

**Why it's wrong**:
- Optimizing metric ≠ optimizing business
- Example: "Better email subject lines" → more opens, but wrong audience
  Result: Opens up, conversions down

**Solution**: Validate causation
```
If we improve [metric], does [outcome] improve?

Test: Improve email subject lines
Check: Do opens increase? (measure)
Check: Do clicks increase? (measure)
Check: Do bookings increase? (validate causation)
```

### ❌ Mistake 4: Metric Becomes Gamed

**Problem**: Optimizing metric in unintended way

**Example**:
```
Metric: Time spent in product
Unintended behavior: Add animations, slow things down, dark colors
Real impact: Worse UX, lower retention (metric wrong!)
```

**Solution**: Have guardrail metrics
```
North Star: Engagement

But also watch:
- User satisfaction (NPS)
- Core task completion time (don't slow it down)
- Error rates (don't break things to add time)
```

### ❌ Mistake 5: Not Measuring What Matters

**Problem**: Measuring outputs ("features shipped") not outcomes ("revenue growth")

**Examples**:
```
❌ 5 features shipped this quarter
✓ Conversion increased 3% this quarter

❌ 1000 emails sent
✓ 50 new customers from campaign
```

**Solution**: Always ask "So what?"

When proposing metric, ask:
- "Why do we care about this?"
- "How does it impact revenue/retention/satisfaction?"
- "Who owns improving this?"

---

## Metric Trees

### What is a Metric Tree?

Visual breakdown of North Star into components

```
                        Streaming Hours
                             ↓
              _______________┼_______________
             ↓               ↓               ↓
          DAU            Hours/DAU      Listener Growth
          ↓                ↓               ↓
     New users    ├─ Playlist   ├─ New users
     Retained      │ listening  ├─ Activation
     users         │            └─ Retention
                   ├─ Discover
                   │ playlist
                   └─ Radio
```

### Building a Metric Tree

**Step 1: Start with North Star**
Example: Streaming hours per month

**Step 2: Break into components**
```
Streaming hours = DAU × Hours per DAU × Month duration
               = DAU × (Playlist hours + Radio hours + Other hours)
```

**Step 3: Further decompose**
```
DAU = New users + Retained users
    = New users from signup + New users from reinstall + Retained from prev day

Playlist hours = Playlists created × Average hours per playlist × Share
```

**Step 4: Identify opportunities**
```
Growing streaming hours through:
- Grow DAU (acquisition + retention) ✓
- Increase hours per user (better playlists, recommendations) ✓
- Shift to paid tier (more generous with time? no) ✗
```

### Netflix Streaming Tree

```
Streaming Hours
├─ Subscribers × Hours per subscriber
├─ Subscribers = Gross adds - Churn
│  ├─ Gross adds: Marketing + word-of-mouth (growth team owns)
│  └─ Churn: Content satisfaction, account issues (product owns)
│
└─ Hours per subscriber = Sessions × Hours per session
   ├─ Sessions: Engagement, login frequency (UX owns)
   └─ Hours per session: Content choice, satisfaction (content owns)
```

### Using Trees for Decisions

**Scenario: Growth slowing**
```
Streaming hours down 5%
├─ Check DAU: Down 10% (bigger problem!)
│  └─ Root cause: Churn up (new content being released late)
│     Action: Prioritize content scheduling
│
└─ Check Hours/DAU: Up 5% (compensating)
   └─ Insight: Existing users loving content, just not acquiring enough
```

---

## Dashboarding

### Essential Dashboard Components

**Daily Metrics Dashboard** (for quick pulse):

```
North Star: Monthly Streaming Hours
├─ Current month: 12.5B hours (Target: 13B hours) [-4%]
├─ Trend: Last 7 days average, vs. previous 7 days [icon: trending up]

Key Metrics (Today vs. Yesterday):
├─ DAU: 45M [+2%] ↑
├─ MAU: 150M [-0.5%] ↓
├─ New signups: 200K [+10%] ↑
├─ Churn rate: 2.1% [+0.1%] ↓ (bad)

Alerts:
⚠ Churn spiked (2.1% vs. normal 1.8%)
⚠ Premium signup conversion dropped 15%
✓ New user DAU-next-day retention up 3%
```

**Weekly Analytics Deep-dive**:

```
Metric                  This Week    Last Week    Trend    YoY
DAU (millions)          45.2         44.8         +0.9%    +15%
MAU (millions)          150.3        151.2        -0.6%    +12%
Streaming hours (B)     3.1          3.0          +3%      +18%
New user retention D1   68%          66%          +2pp     +3pp
Premium conversion      5.2%         5.8%         -10%     -15%
```

**Cohort Analysis**:

```
Signup Month    D1    D7    D30    D90    NRR
Jan 2024        100%  45%   20%    8%     N/A
Feb 2024        100%  47%   22%    9%     N/A
Mar 2024        100%  46%   21%    8%     95%
Apr 2024        100%  48%   23%    -      [current]

Interpretation: Retention stable, slight improvement in Mar-Apr
```

### Tools for Dashboarding

**Options**:
- Looker (Google's tool, free for internal use)
- Tableau (powerful, excellent visualizations)
- Amplitude (built-in product analytics + dashboards)
- Metabase (open source, easy setup)
- Grafana (real-time metrics)

**Best practice**:
- One source of truth (shared dashboards)
- Accessible to entire company (not just PMs/data)
- Auto-updated daily
- Comments/annotations for context

---

## Metric Evolution

### When to Change North Star

**Red flags**:
- Product fundamentally changed
- Business model shifted
- North Star hitting ceiling (saturating)
- Metric no longer correlates with success

**Example: Slack evolution**

```
Stage 1 (2013): Signups per day
└─ Problem: Signups growing, but activation was low

Stage 2 (2014): DAU (moving to engaged users)
└─ Better, but needed to understand quality

Stage 3 (2015): DAU / Workspace size (engagement per team)
└─ Current: Engaged teams = stickiest, most valuable
```

### Process for Changing North Star

**Step 1: Identify limitation of current metric**
```
"DAU is at 50M, but we want to grow and measure monetization"
```

**Step 2: Propose candidate replacement**
```
Candidates:
- Revenue (direct, but not controllable by product team)
- Premium DAU (engaged + paying, product team can influence)
- Net Revenue Retention (compound metric, hard to debug)
```

**Step 3: Validate candidate**
```
Hypothesize: If Premium DAU grows, NRR improves
Test: Run experiment
Measure: Does revenue follow Premium DAU growth?
```

**Step 4: Transition**

Don't change overnight. Instead:
```
Month 1: Introduce new metric alongside old
Month 2: Start communicating using new metric
Month 3: Phase out old metric, focus on new
```

---

## Summary

**Metric Selection Best Practices**:

1. **Choose one North Star**: Not a portfolio of metrics
2. **Align with customer value**: Metric should reflect what customers care about
3. **Team controllable**: Product team should be able to influence
4. **Pair leading with lagging**: Fast feedback + true validation
5. **Use metric trees**: Decompose to find improvement opportunities
6. **Have guardrails**: Don't optimize one metric at expense of others
7. **Measure outcomes**: "Bookings" not "pages visited"
8. **Review regularly**: Weekly/monthly to stay current
9. **Act on metrics**: Metrics inform decisions and priorities
10. **Communicate widely**: Everyone should understand metrics

**Remember**: The goal is not perfect metrics. The goal is to align teams around what matters and measure progress toward that outcome.

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Next Review**: 2025-02-19

**Further Reading**:
- "Lean Analytics" by Alistair Croll & Benjamin Yoskovitz
- Spotify Labs blog on streaming metrics
- Airbnb's NDW (N-Day Weighted) retention analysis
- "Measuring and Maximizing Impact" - a16z growth blog
- Netflix's culture deck on metrics
