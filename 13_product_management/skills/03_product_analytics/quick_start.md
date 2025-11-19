# Product Analytics: 30-Minute Quick Start Guide

Track what matters, find the bottlenecks, and drive data-informed decisions.

---

## Your 30-Minute Roadmap

- **Minutes 1-5**: Understand the AARRR metrics framework
- **Minutes 6-15**: Build your first dashboard tracking core metrics
- **Minutes 16-25**: Find your biggest opportunity (funnel analysis)
- **Minutes 26-30**: Set up weekly metrics reviews

---

## 5 Essential Concepts Every PM Needs

### 1. AARRR: The Metrics that Matter
Track the complete user lifecycle with five key areas. Focus on metrics that drive business outcomes, not vanity metrics.

**Acquisition**: How users find you (new signups, traffic sources, CAC)
**Activation**: Whether users realize value (onboarding completion, first action, "aha" moment)
**Retention**: Whether users return (DAU/MAU ratio, monthly churn, cohort retention curves)
**Revenue**: How you capture value (ARPU, LTV, conversion rate, expansion revenue)
**Referral**: How satisfied users drive growth (NPS, viral coefficient, word-of-mouth lift)

**Actionable**: Choose one metric from each category. Track these five metrics weekly.

### 2. Funnels Reveal Where Users Drop Off
A funnel shows sequential steps users must complete to achieve a goal. Every drop-off represents an opportunity.

**Example**: Sign-up → Email verification → Profile setup → Invite users → First collaboration = Activation funnel

**Actionable**: Identify your activation funnel (the steps to reach "aha moment"). Calculate drop-off at each step. Where do you lose the most users?

### 3. Cohort Analysis Shows If You're Improving
Compare groups of users (cohorts) by signup date. Are newer cohorts behaving better than older ones? If not, your product isn't improving.

**Actionable**: Pull last 3 months of signups. Compare retention curves. Are recent users more retained than users from 3 months ago?

### 4. Causation is Hard; Correlation is Your Starting Point
You can't prove one change caused a metric shift (without A/B testing). But if metric drops right after a change, you have a strong signal.

**Actionable**: When a metric changes unexpectedly, ask: "What product or marketing changes happened in the past 2 weeks that could explain this?"

### 5. Segment Your Data
Your overall metrics hide important patterns. Break down metrics by:
- User cohort (when they signed up)
- Geography (US vs. EU vs. other)
- Product plan (free vs. paid)
- Use case (users vs. admins)
- Acquisition source (organic vs. paid)

**Actionable**: Pick one metric you care about. Segment by 2-3 variables. Where's your biggest weakness? Focus there.

---

## First Steps Checklist

### Week 1: Set Up Analytics Foundation
- [ ] Identify your analytics tool (Amplitude, Mixpanel, Segment, Google Analytics, custom)
- [ ] Ensure events are properly tracked (signup, login, key feature use, etc.)
- [ ] Audit: Are you tracking the right actions? Missing key events?
- [ ] Create a shared metrics definition document (ARPU = X, churn = Y)

### Week 1-2: Build Your Dashboard
- [ ] Create one dashboard with your core 5-7 metrics (AARRR framework)
- [ ] Add your activation funnel (steps to "aha moment")
- [ ] Add your monetization funnel if applicable (free → paid → expansion)
- [ ] Add a retention cohort chart (are recent cohorts retaining better?)
- [ ] Set weekly review meeting (Mondays or end of week)

### Week 2: Analyze Current State
- [ ] Calculate current metrics:
  - Monthly Active Users (MAU) and Daily Active Users (DAU)
  - DAU/MAU ratio (engagement indicator; healthy is 20-40%)
  - Monthly churn rate (how many users drop off)
  - Activation rate (% of new users reaching "aha moment")
  - Revenue metrics (ARPU, LTV if applicable)
- [ ] Create baseline report: "State of product health today"

### Week 3: Identify Top Bottleneck
- [ ] Look at your funnels. Where's the biggest drop-off?
- [ ] Hypothesis: Why are users dropping off here?
- [ ] Action: Plan to investigate (user research interviews, user session replays, A/B test)
- [ ] Set baseline: What's the current conversion rate at this step?

### Week 4: Establish Weekly Rhythm
- [ ] 30-min weekly metrics review: What changed? Why? What's next?
- [ ] Monthly deep-dive: Cohort analysis, segment breakdowns, win/loss analysis
- [ ] Quarterly: Set targets for each metric (our goal for next quarter)

---

## Common Mistakes to Avoid

### Mistake 1: Tracking Too Many Metrics
If you track 50 metrics, you track none. Focus on 5-7 core metrics that drive business.

**Fix**: AARRR framework keeps you focused. One metric per category minimum.

### Mistake 2: Vanity Metrics
Total signups, downloads, or pageviews sound good but don't correlate with business success.

**Fix**: Focus on engagement (DAU/MAU), retention, revenue. These metrics predict long-term success.

### Mistake 3: Not Segmenting Your Data
"Our churn is 5%" masks the fact that free users churn at 10% and paid users churn at 2%.

**Fix**: Always segment by cohort, geography, and plan. Find where you're weakest.

### Mistake 4: Setting Targets Without Understanding Baseline
"Our goal is 50% activation" might be unrealistic without knowing current state.

**Fix**: Establish baseline metrics first. Then set targets as incremental improvements (not wild jumps).

### Mistake 5: Ignoring External Factors
You changed onboarding flow (positive +5% activation) but also did a big marketing campaign (inflated traffic with less qualified users).

**Fix**: When analyzing changes, ask "What else happened at the same time?" Segment by acquisition source to isolate impact.

---

## Metrics Definitions to Use Right Now

```
ACQUISITION
- New Users (Month): Total first-time signups
- CAC (Cost per Acquisition): Total marketing spend / New customers

ACTIVATION
- Activation Rate: % of new users who reach "aha moment" within 7 days
- Onboarding Completion: % of signups who complete full onboarding
- Time to First Action: Days from signup to meaningful action

RETENTION
- DAU (Daily Active Users): Users active in the last 24 hours
- MAU (Monthly Active Users): Users active in the last 30 days
- DAU/MAU Ratio: Engagement proxy (30% = good, 5% = poor)
- Churn Rate (monthly): (Users at start - Users at end) / Users at start
- Cohort Retention: % of cohort still active after 30/60/90 days

REVENUE
- ARPU (Average Revenue Per User): Total revenue / Total users
- LTV (Lifetime Value): Total revenue from user over lifetime
- Conversion Rate: % of free → paid
- Expansion Revenue: Revenue from existing customers (upsells, upgrades)

REFERRAL
- NPS (Net Promoter Score): "How likely to recommend?" (0-10)
- Viral Coefficient: New users acquired per existing user
```

---

## Finding Your Biggest Opportunity: Funnel Analysis

### Step 1: Map Your Activation Funnel
```
Sign-up (100%) → Email Verify (80%) → Profile Complete (70%)
→ First Collaboration (40%) → Weekly Return (20%)
```

### Step 2: Calculate Drop-Off at Each Step
- Sign-up to Email: 20% drop (biggest problem!)
- Email to Profile: 10% drop
- Profile to Collaboration: 30% drop (second priority)
- Collaboration to Weekly Return: 80% drop (retention issue)

### Step 3: Investigate Top Bottleneck
**Biggest drop: Sign-up to Email (20% lost)**
- User research: Why don't people verify email?
- Session replay: Do they get the email? Click confirmation link?
- A/B test: What if we send reminder email 1 hour after signup?
- Goal: Increase email verification to 90%+ (could improve overall activation by 2-5%)

### Step 4: Iterate and Measure
- Implement fix (reminder email, clearer instructions, etc.)
- Measure impact after 1 week
- Did we improve? Move to next bottleneck
- If no improvement, try different hypothesis

---

## Dashboard You Can Build Today

### Create in spreadsheet or analytics tool:

| Metric | Current | Target | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|---------|--------|--------|--------|--------|--------|
| MAU | 10,000 | 12,000 | 10,200 | 10,400 | 10,600 | 10,800 |
| DAU/MAU | 25% | 30% | 25% | 26% | 27% | 28% |
| Churn | 8% | 6% | 8% | 7.8% | 7.6% | 7.4% |
| Activation | 40% | 50% | 40% | 42% | 44% | 46% |
| ARPU | $15 | $18 | $15 | $15.20 | $15.40 | $15.60 |

---

## Success Metrics

- [ ] You review 5-7 core metrics weekly
- [ ] You understand why each metric matters to business
- [ ] You can explain your funnels (where users drop off)
- [ ] Your activation/retention curves are improving quarter-over-quarter
- [ ] Product decisions are based on metrics, not hunches
- [ ] Your team can read the dashboard and understand product health

---

## Next Steps

1. **This week**: Set up analytics tool, audit event tracking, create baseline metrics
2. **Next week**: Build dashboard with AARRR metrics
3. **Week 3**: Identify top funnel bottleneck, plan investigation
4. **Week 4**: Share metrics with team, establish weekly review cadence

---

**Remember**: Data without context is meaningless. Use metrics to guide questions ("Why did churn increase?"), not as conclusions. Always follow up numbers with customer conversations.

