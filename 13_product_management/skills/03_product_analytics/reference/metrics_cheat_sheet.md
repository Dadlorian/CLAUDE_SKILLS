# Product Analytics Metrics Cheat Sheet

Quick reference for the most important product analytics metrics, definitions, formulas, and benchmarks.

## Acquisition Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Conversion Rate (Sign-up) | Sign-ups / Visitors | % of visitors who sign up | 2-5% SaaS | Higher = better top-of-funnel |
| Cost Per Acquisition (CPA) | Total spend / New users | Cost to acquire one user | Depends on LTV | Lower = more efficient, but quality matters |
| Cost Per Click (CPC) | Ad spend / Clicks | Paid acquisition cost per click | $0.50-$5.00 | Varies by platform and industry |
| Cost Per Lead (CPL) | Lead gen spend / Leads | Soft-conversion cost | $5-$500+ | Depends on lead quality |
| Click-through Rate (CTR) | Clicks / Impressions | % who click on ad/link | 0.5-2% | Platform dependent |
| Return on Ad Spend (ROAS) | Revenue from ads / Ad spend | Revenue generated per $ spent | 2:1 - 5:1 | Higher = more efficient |

## Engagement Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Daily Active Users (DAU) | Unique users active today | Users engaging daily | N/A | Absolute measure of active base |
| Monthly Active Users (MAU) | Unique users in month | Users engaging monthly | N/A | Month-over-month trend critical |
| DAU/MAU Ratio | DAU / MAU | % of monthly users active daily | 20-60% | Higher = more habitual/sticky |
| Weekly Active Users (WAU) | Unique users in week | Users engaging weekly | N/A | Useful for weekly-cadence products |
| Session Length | Total time / Sessions | Average duration per session | 2-10 min | Product dependent |
| Session Frequency | Sessions / Days | Sessions per user per day | 0.5-5x | Indicates usage intensity |
| Feature Adoption | Users using feature / Total users | % who tried new feature | 30-70% after launch | Higher = better feature relevance |
| Feature Stickiness | Sessions with feature / Total sessions | % of engagement that uses feature | >15% critical features | Core features should be highly sticky |
| Pages per Session | Total pages / Sessions | Average pages viewed | 5-15 | Navigation/exploration indicator |
| Scroll Depth | % who reach bottom / Total visits | Engagement with content | 30-50% | 25% is concerning |

## Retention & Churn Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Day 1 Retention | Day 1 active / Day 0 active | % returning next day | 20-45% | First signal of product fit |
| Day 7 Retention | Day 7 active / Day 0 active | % returning after 1 week | 15-35% | Shows sustained value |
| Day 30 Retention | Day 30 active / Day 0 active | % returning after 1 month | 10-25% | Long-term engagement signal |
| Churn Rate (Monthly) | (Start - End) / Start | % of users lost per month | 5-10% SaaS | <5% is excellent |
| Churn Rate (Annual) | 1 - (1 - Monthly Churn)^12 | Annual equivalent | 40-70% | Impacts growth rate |
| Rolling Retention | Users in period N who were active N-1 | % retained from previous period | Variable | Monitors ongoing trend |
| Reactivation Rate | Inactive users returning | % of churned users who return | 5-20% | Indicates product-market fit |

## Monetization Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Average Revenue Per User (ARPU) | Total revenue / Users | Average revenue contribution | Varies | Critical for forecasting |
| ARPU Growth | (ARPU now - ARPU before) / Before | % change in ARPU | 5-15% YoY | Shows monetization improvement |
| Average Revenue Per Paying User (ARPPU) | Revenue from payers / Paying users | Average from monetized segment | 10x+ ARPU | Shows pricing effectiveness |
| Lifetime Value (LTV) | ARPU * Expected customer lifetime | Total revenue per user over life | 3x-10x CAC | Most important unit metric |
| LTV:CAC Ratio | LTV / CAC | Revenue per $ spent on acquisition | 3:1+ | <2:1 = business doesn't work |
| Payback Period | CAC / Monthly revenue per user | Months to recover acquisition cost | 12-24 months | Faster = more capital efficient |
| Monthly Recurring Revenue (MRR) | Predictable monthly subscriptions | Recurring revenue base | N/A | Month-over-month growth critical |
| MRR Growth Rate | (MRR current - MRR previous) / MRR previous | % change in MRR | 5-10% MoM growth | Shows business momentum |
| Annual Recurring Revenue (ARR) | MRR * 12 | Annualized revenue | N/A | Often used for reporting |
| Net Revenue Retention (NRR) | (Ending MRR - Churned MRR + Expansion) / Starting MRR | Revenue retention + expansion | 100-150% | >100% = growing with existing customers |
| Gross Revenue Retention (GRR) | (Ending MRR - Churned MRR) / Starting MRR | Only retention, no expansion | 70-90% | How well product retains customers |
| Expansion Revenue | Upsell + Cross-sell + Usage growth | Revenue growth from existing customers | 20-40% of growth | Shows land-and-expand success |
| Customer Concentration | % of revenue from top X customers | Revenue risk | <10% single customer | High concentration = risk |

## Conversion & Funnel Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Top-to-Bottom Conversion | Final step / Starting step | Overall funnel conversion | 1-5% typical | Product dependent |
| Step Conversion Rate | Step completers / Step entrants | Conversion at specific step | 30-80% | High drop-off = friction point |
| Drop-off Rate | (Step - Final) / Step | % lost at specific step | 20-70% per step | Indicates friction |
| Conversion Velocity | Average time step-to-step | Speed through funnel | Hours to weeks | Faster = less friction |
| Assisted Conversion | Conversions influenced not attributed | Halo effect of touchpoints | N/A | Shows content/channel influence |
| Abandonment Rate | Started but didn't complete / Started | % not finishing process | 70-95% checkout | Signals friction or cost factors |

## Traffic & Audience Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Unique Visitors | Count distinct users per period | Total people visiting | N/A | Raw reach metric |
| Pageviews | Total page views | Engagement volume | 2-5 per visitor | Navigation pattern |
| Bounce Rate | Single-page sessions / Sessions | % leaving without interaction | 20-50% | Lower = better content fit |
| Exit Rate | Exits from page / Pageviews | % leaving site from page | 10-30% per page | High = poor content or CTA |
| Traffic by Source | Visitors from each channel | Distribution of traffic | N/A | Identifies best channels |
| Direct Traffic | Visits with no referrer | Returning users and bookmarks | 20-40% | Indicates loyalty |
| Organic Traffic | Visits from search engines | SEO effectiveness | 30-60% ideal | Free, high-intent traffic |
| Paid Traffic | Visits from ads | Ad campaign reach | 10-40% | Cost-dependent |
| Referral Traffic | Visits from external links | Earned reach | 5-20% | Shows external interest |

## Quality & Health Metrics

| Metric | Formula | What It Measures | Benchmark | Interpretation |
|--------|---------|------------------|-----------|-----------------|
| Net Promoter Score (NPS) | % Promoters (9-10) - % Detractors (0-6) | Customer willingness to recommend | 0-70+ | Correlates with retention |
| Customer Satisfaction (CSAT) | % Satisfied / Total responses | Satisfaction with product | 70-90% | Immediate sentiment |
| Customer Effort Score (CES) | % Easy to use / Total responses | Ease of use perception | 70-90% | Operationally important |
| Error Rate | Errors / Transactions | % of failures | <0.1% | Stability indicator |
| Page Speed (Load Time) | Time to fully load | Performance perception | <3 seconds | >3 sec = engagement loss |
| Uptime | Available time / Total time | System reliability | 99.9%+ | Downtime hurts retention |
| Support Ticket Rate | Support tickets / Active users | Product usability issues | 1 per 50-500 users | Lower = better quality |
| First Response Time | Average time to first support response | Support responsiveness | <24 hours | Affects satisfaction |
| Resolution Rate | Resolved / Total tickets | % resolving issues | 80-95% | Shows support effectiveness |

## Cohort Analysis Metrics

| Metric | Definition | Use Case | Benchmark |
|--------|-----------|----------|-----------|
| Cohort Retention | % of cohort returning by week/month N | Measure product improvement over time | See retention benchmarks |
| Cohort LTV | Revenue per user from cohort | Compare acquisition quality | Newer vs older cohorts |
| Cohort Churn | % lost from cohort | Predict runway and forecast | Varies by product |
| Cohort Size | Users acquired in period | Compare volumes | Trends indicate growth |
| Cohort Cost | Total CAC for cohort | Assess channel efficiency | Compare by channel |

## Experimentation Metrics

| Metric | Definition | Importance | Standard |
|--------|-----------|-----------|----------|
| Statistical Significance | Probability result isn't due to chance | Must have for any decision | 95% confidence (p<0.05) |
| Confidence Interval | Range of likely true effect | Shows precision of estimate | ±2-5% typical |
| Relative Lift | (Variant - Control) / Control * 100% | Shows practical improvement | 5%+ usually meaningful |
| Effect Size | Magnitude of actual difference | Practical significance | Typically 2-20% |
| Statistical Power | Probability of detecting real effect | Ability to find true differences | 80% standard |
| Sample Size | Users per variant | Required for statistical validity | 1,000-10,000+ per arm |
| Test Duration | Days to run experiment | Capture weekly patterns | Minimum 7-14 days |
| Minimum Detectable Effect | Smallest change we can reliably detect | Test design parameter | 5-10% for most metrics |

## Quick Calculation Reference

### Unit Economics
- **LTV = ARPU × Customer Lifetime (years)**
- **CAC Payback Period = CAC ÷ (ARPU per month)**
- **Viral Coefficient = Invites sent per user × Conversion to user**
- **Viral Loop Duration = Time from signup to invite creation to new user signup**

### Retention
- **Annualized Churn = 1 - (1 - Monthly Churn)^12**
- **Retention Half-life = Time to lose 50% of cohort**
- **Stable Retention Rate = Retention in week N and beyond**

### Growth
- **Month-over-Month Growth = (Current - Previous) / Previous**
- **Compounded Annual Growth Rate = (Ending / Beginning)^(1/years) - 1**
- **Doubling Time = ln(2) / ln(1 + growth rate)**

### Funnel
- **Funnel Conversion = End step / Start step**
- **Drop-off Rate = (Entrants - Completers) / Entrants**
- **Weighted Funnel = Accounts for multiple paths**

## Metric Selection Framework

**Choose metrics based on:**
1. **Strategic relevance**: Does it directly impact business goals?
2. **Actionability**: Can we actually influence this metric?
3. **Lag time**: Does it provide timely feedback for decisions?
4. **Precision**: Is it measurable and reliable?
5. **Contextual**: Does it require explanation with other metrics?

**Typical Dashboard Structure:**
- **1 North Star**: Overall product health (e.g., MAU, Transactions/User, Engagement Score)
- **3-5 Key Results**: Sub-dimensions of north star
- **8-12 Core Metrics**: Weekly tracking of key business drivers
- **20+ Diagnostic**: Deep-dive analysis when needed

## Industry Benchmarks

### SaaS Metrics
- Conversion (visitor to sign-up): 2-5%
- Activation (sign-up to paying): 20-50%
- Monthly Churn: 5-10%
- Net Revenue Retention: 90-130%
- Payback Period: 12-24 months
- Magic Number (MRR growth / Sales & Marketing spend): 0.7-1.0

### Mobile App Metrics
- Day 1 Retention: 20-45%
- Day 30 Retention: 10-25%
- Monthly Churn: 40-60%
- DAU/MAU: 15-35%

### E-commerce Metrics
- Conversion Rate: 1-3%
- Cart Abandonment: 70-75%
- Customer Repeat Purchase Rate: 20-45%
- Churn/Return Rate: 50-70% annually
- AOV (Average Order Value): Varies by category

### Marketplace Metrics
- Supply/Demand Balance: Critical metric
- Take Rate: 15-30% typical
- Frequency of Transactions: Key engagement metric
- NPS: 40-70+ indicates healthy marketplace

## Red Flags and Early Warnings

| Warning Sign | Potential Issue | Action |
|--------------|-----------------|--------|
| Day 1 retention <20% | Product isn't delivering value quickly | Improve onboarding, reduce friction |
| Day 7 retention declining week-to-week | Engagement drop after initial novelty | Test retention hypothesis, user research |
| Increasing support ticket rate | Product quality or usability issues | Audit error rate and user feedback |
| Increasing acquisition cost, same cohort quality | Market saturation or channel fatigue | Diversify channels, improve organic |
| Declining feature adoption despite launch | Feature doesn't solve real problem | User research, test hypothesis |
| Expansion revenue declining | Lack of land-and-expand opportunity | Pricing model or product strategy issue |
| NPS declining 10+ points | Customer satisfaction dropping | Diagnose satisfaction drivers |
| Bounce rate >70% | Content/targeting mismatch | Audit landing page and traffic source |

## Metric Correlation Matrix

**Metrics that typically correlate:**
- DAU ↔ Retention curves
- Feature adoption ↔ Overall retention
- NPS ↔ Churn rate (inverse)
- ARPU ↔ Customer satisfaction
- CAC payback ↔ Revenue growth potential
- Error rate ↔ Support volume
- Load time ↔ Bounce rate

**Metrics that DON'T necessarily correlate (careful with these):**
- Signups ↔ Revenue (quality matters)
- Page views ↔ Engagement (scrolling isn't value)
- Features shipped ↔ Retention (user adoption matters)
- Market size ↔ Addressable users (need product fit)
- Funding raised ↔ Unit economics (wrong correlation entirely)
