# Dashboard Design Examples

Reference designs for building effective product analytics dashboards across different scenarios.

---

## 1. Core Metrics Dashboard (Daily Standup)

**Purpose:** Quick view of product health for daily team sync

**Audience:** Entire product team (PMs, engineers, design)

**Refresh Rate:** Every hour

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCT HEALTH DASHBOARD                  │
│                     Updated: 2:45 PM UTC                     │
├─────────────────────────────────────────────────────────────┤
│
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  │   NORTH STAR     │  │   SECONDARY 1    │  │ SECONDARY 2  │
│  │  Monthly Active  │  │  Daily Active    │  │  Day 7 Ret   │
│  │   Users (MAU)    │  │    Users (DAU)   │  │   Retention  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤
│  │    2,450,123     │  │     485,239      │  │     32.4%    │
│  │                  │  │                  │  │              │
│  │  ↑ 2.1% vs last  │  │  ↑ 1.3% vs YTD   │  │  ↓ 1.2% vs   │
│  │       month      │  │       avg        │  │   4w avg     │
│  │                  │  │                  │  │              │
│  │  Target: 2.5M   │  │  Target: 500k    │  │ Target: 34%  │
│  │  Status: 98%    │  │  Status: 97%     │  │ Status: 95%  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘
│
├─────────────────────────────────────────────────────────────┤
│
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  │ METRIC TREND     │  │ METRIC TREND     │  │ METRIC TREND │
│  │                  │  │                  │  │              │
│  │ MAU - Last 90d   │  │ DAU - Last 90d   │  │ Ret - 90d    │
│  │                  │  │                  │  │              │
│  │ [Line chart      │  │ [Line chart      │  │ [Line chart] │
│  │  trending up]    │  │  trending up]    │  │              │
│  │                  │  │                  │  │              │
│  │ Jan 1   Feb 1... │  │ Jan 1   Feb 1... │  │ Jan 1 Feb 1  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘
│
├─────────────────────────────────────────────────────────────┤
│ ALERTS & ISSUES
├─────────────────────────────────────────────────────────────┤
│
│  ✓ All systems normal
│  ⚠ Email verification rate down 3% (88%) - monitor tomorrow
│
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

1. **North Star + Key Secondaries** (Top row)
   - Current value, prominent display
   - Day-over-day or week-over-week change
   - Target vs. actual
   - Status indicator (green/yellow/red)

2. **Trend Charts** (Bottom row)
   - 90-day view for context
   - Help spot trends early
   - Immediate visual feedback

3. **Alert Section**
   - Any metrics outside acceptable range
   - Actionable issues only
   - Suppressed if all green

**Dashboard Details:**

| Component | Metric | Target | Current | Status |
|-----------|--------|--------|---------|--------|
| North Star | MAU | 2.5M | 2.45M | 98% ✓ |
| Secondary 1 | DAU | 500k | 485k | 97% ✓ |
| Secondary 2 | Day 7 Ret | 34% | 32.4% | 95% ⚠ |
| Core 1 | Day 1 Ret | 40% | 38% | 95% ⚠ |
| Core 2 | Sign-up Rate | 8% | 7.9% | 99% ✓ |
| Core 3 | ARPU | $12 | $11.80 | 98% ✓ |
| Core 4 | Email Verify | 85% | 88% | 104% ✓ |
| Core 5 | Feature X Use | 45% | 43% | 96% ⚠ |

---

## 2. Acquisition & Growth Dashboard

**Purpose:** Deep dive into how users discover and join product

**Audience:** Growth PM, marketing, product leadership

**Refresh Rate:** Daily

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│              ACQUISITION & GROWTH DASHBOARD                  │
├─────────────────────────────────────────────────────────────┤
│
│  ┌─────────────────────────────────────────────────────────┐
│  │ NEW SIGNUPS - Last 30 Days                              │
│  ├─────────────────────────────────────────────────────────┤
│  │ [Area chart showing daily signups by channel]           │
│  │                                                         │
│  │ ■ Organic Search  ■ Paid  ■ Referral  ■ Social  ■ Other│
│  │                                                         │
│  │ Total: 12,450 signups this month                        │
│  │ Day average: 415/day (↑18% vs previous month)           │
│  └─────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────┐  ┌──────────────────────────────┐
│  │ SIGNUPS BY CHANNEL   │  │ CONVERSION TO ACTIVATION     │
│  ├──────────────────────┤  ├──────────────────────────────┤
│  │ Organic: 6,225 (50%) │  │ Organic:        58% → 42%    │
│  │ Paid:    3,735 (30%) │  │ Paid:           45% → 22%    │
│  │ Referral:1,240 (10%) │  │ Referral:       72% → 58%    │
│  │ Social:   1,245 (10%)│  │ Social:         52% → 35%    │
│  │                      │  │ Other:          38% → 18%    │
│  │ Total:  12,450       │  │                              │
│  └──────────────────────┘  └──────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ SIGNUP-TO-PAYMENT FUNNEL                                │
│  ├──────────────────────────────────────────────────────────┤
│  │                                                          │
│  │ All Signups (30 days)     12,450 (100%)                 │
│  │       ↓ [85% convert]                                    │
│  │ Email Verified            10,582 (85%)                   │
│  │       ↓ [45% convert]                                    │
│  │ Setup Complete             4,762 (45%)                   │
│  │       ↓ [42% convert]                                    │
│  │ Payment Entered            2,000 (42%)                   │
│  │       ↓ [95% convert]                                    │
│  │ First Paid Subscriber      1,900 (15% of signups!)      │
│  │                                                          │
│  │ Key Drop-off: Email Verification (15% loss)             │
│  │ Opportunity: Improve verification flow                  │
│  │                                                          │
│  └──────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ COST ANALYSIS                                            │
│  ├──────────────────────────────────────────────────────────┤
│  │ Channel          | Spend    | Signups | CPA   | Tier   │
│  │ ─────────────────┼──────────┼─────────┼───────┼────────│
│  │ Organic          | $0       | 6,225   | $0    | ★★★★★ │
│  │ Referral         | $0       | 1,240   | $0    | ★★★★★ │
│  │ Paid Search      | $8,500   | 2,135   | $4    | ★★★★  │
│  │ Social Ads       | $5,200   | 1,600   | $3    | ★★★★  │
│  │ Partnership      | $2,100   | 1,235   | $2    | ★★★★★ │
│  │ ─────────────────┼──────────┼─────────┼───────┼────────│
│  │ TOTAL            | $15,800  | 12,435  | $1.27 |        │
│  │                                                          │
│  │ Avg CAC → Payment: $8.32 (spend ÷ paid signups)          │
│  └──────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**Key Metrics to Track:**

| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|--------|
| Daily Signups | 415 | 351 | 400 | ✓ |
| Week 1 Activation Rate | 42% | 39% | 45% | ⚠ |
| CPA | $1.27 | $1.45 | $1.00 | ⚠ |
| Organic % of Signups | 50% | 45% | 55% | ⚠ |
| Paid CAC Payback | 8.2mo | 9.1mo | 6mo | ✗ |

---

## 3. Engagement & Retention Dashboard

**Purpose:** Monitor user engagement and predict churn

**Audience:** Product manager, retention specialist

**Refresh Rate:** Daily

```
┌─────────────────────────────────────────────────────────────┐
│            ENGAGEMENT & RETENTION DASHBOARD                  │
├─────────────────────────────────────────────────────────────┤
│
│  ┌─────────────────────────────────────────────────────────┐
│  │ COHORT RETENTION TABLE (Last 30 days)                   │
│  ├─────────────────────────────────────────────────────────┤
│  │ Cohort    │  D0   │ D1  │ D7  │ D14 │ D30 │ D60 Status   │
│  │ ──────────┼───────┼─────┼─────┼─────┼─────┼──────────────│
│  │ Oct 20-26 │ 1,523 │ 45% │ 28% │ 18% │ 12% │ ✓ STABLE    │
│  │ Oct 27... │ 1,689 │ 46% │ 29% │ 19% │ 13% │ ✓ IMPROVING │
│  │ Nov 03-09 │ 1,834 │ 48% │ 31% │ 21% │ 14% │ ✓ IMPROVING │
│  │ Nov 10-16 │ 1,956 │ 49% │ 33% │ 22% │  -  │ ↑ TREND OK  │
│  │ Nov 17... │ 2,145 │ 51% │  -  │  -  │  -  │ ✓ STRONG D1 │
│  │                                                          │
│  │ Key Finding: New cohorts 5% better - recent changes    │
│  │             helping retention. Continue monitoring.     │
│  └─────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────┐  ┌──────────────────────────────┐
│  │ DAU/MAU RATIO TREND  │  │ ENGAGEMENT DISTRIBUTION      │
│  ├──────────────────────┤  ├──────────────────────────────┤
│  │                      │  │ Active Today:        485k    │
│  │ 50%                  │  │ Active This Week:    845k    │
│  │ ├───────────────     │  │ Active This Month: 2,450k    │
│  │ 40%                  │  │                              │
│  │ ├────────────────    │  │ DAU/MAU: 20% (stable)       │
│  │ 30%                  │  │ WAU/MAU: 35% (↑2%)          │
│  │ └────────────────    │  │                              │
│  │ Jan Feb Mar Apr...   │  │ % Using Core Feature:   67%  │
│  │                      │  │ % Using Feature X:      23%  │
│  │ Current: 20%         │  │ % Using Premium Feature: 8%  │
│  │ Target:  22%         │  │                              │
│  └──────────────────────┘  └──────────────────────────────┘
│
│  ┌──────────────────────┐  ┌──────────────────────────────┐
│  │ CHURN EARLY WARNING  │  │ FEATURE STICKINESS MATRIX    │
│  ├──────────────────────┤  ├──────────────────────────────┤
│  │ Days Since Last Use  │  │ Feature      │ Adoption │ Use │
│  │ ─────────────────────│  │ ─────────────┼──────────┼────-│
│  │ 0 days:  485,239     │  │ Search       │  92%     │ 78% │
│  │ 1-7:     360,145     │  │ Share        │  87%     │ 65% │
│  │ 8-14:    145,233     │  │ Collaboration│  45%     │ 22% │
│  │ 15-30:    89,456     │  │ Analytics    │  18%     │ 3%  │
│  │ 30+:      45,123     │  │ Mobile Push  │  12%     │ 1%  │
│  │ CHURN:    374,907    │  │                              │
│  │                      │  │ Action: Collaboration needs  │
│  │ At Risk (8-14d):     │  │ better onboarding           │
│  │ 145k users (15%)     │  │                              │
│  └──────────────────────┘  └──────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ CHURN SIGNALS & RECOMMENDATIONS                         │
│  ├──────────────────────────────────────────────────────────┤
│  │ • 145k users haven't returned in 8-14 days (churn risk) │
│  │   Action: Send re-engagement email                      │
│  │                                                          │
│  │ • Feature X adoption declining (43% → 38% this month)   │
│  │   Action: Review onboarding flow, check for bugs        │
│  │                                                          │
│  │ • Day 1 retention stable but Day 7 declining (↓2%)       │
│  │   Action: Investigate what happens day 2-7              │
│  │                                                          │
│  │ • Premium feature usage extremely low (3% adopters)     │
│  │   Action: Consider onboarding or discoverability issue  │
│  └──────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**Retention Table Details:**

| Cohort | D0 | D1 | D7 | D14 | D30 | Trend |
|--------|----|----|----|----|-----|-------|
| Oct 20 | 100% | 45% | 28% | 18% | 12% | Baseline |
| Oct 27 | 100% | 46% | 29% | 19% | 13% | ↑ +1% |
| Nov 3 | 100% | 48% | 31% | 21% | 14% | ↑ +2% |
| Nov 10 | 100% | 49% | 33% | 22% | - | ↑ +3% |
| Nov 17 | 100% | 51% | - | - | - | ↑ +4% improving |

---

## 4. Revenue & Monetization Dashboard

**Purpose:** Track revenue drivers and unit economics

**Audience:** Finance, executives, product leadership

**Refresh Rate:** Daily

```
┌─────────────────────────────────────────────────────────────┐
│           REVENUE & MONETIZATION DASHBOARD                   │
├─────────────────────────────────────────────────────────────┤
│
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  │ MONTHLY MRR      │  │ NRR (Expansion)  │  │  PAID USERS  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤
│  │   $1,245,890     │  │      115%        │  │   18,450     │
│  │                  │  │                  │  │              │
│  │  ↑ 3.2% vs last  │  │  ↑ 2% vs last    │  │ ↑ 4.1% vs    │
│  │      month       │  │      month       │  │   1 month    │
│  │                  │  │                  │  │              │
│  │ Target: $1.3M    │  │ Target: 120%     │  │ Target: 19k  │
│  │ Progress: 96%    │  │ Progress: 96%    │  │ Progress: 97%│
│  └──────────────────┘  └──────────────────┘  └──────────────┘
│
│  ┌──────────────────────┐  ┌──────────────────────────────┐
│  │ ARPU BY SEGMENT      │  │ MRR MOVEMENT (Month-over-MO) │
│  ├──────────────────────┤  ├──────────────────────────────┤
│  │                      │  │ Starting MRR:    $1,208,450  │
│  │ Enterprise: $3,200   │  │ New MRR:           $185,200  │
│  │ Mid-market: $1,450   │  │ Expansion MRR:     $98,340   │
│  │ SMB:          $245   │  │ Churn MRR:        -$42,100   │
│  │ Freemium:      $12   │  │ Ending MRR:      $1,449,890  │
│  │                      │  │                              │
│  │ Blended ARPU: $67.50 │  │ Growth: +$241,440 (+20%)     │
│  │ Target: $70          │  │ NRR: (1.245M - 42k) / 1.208M │
│  │ Progress: 96%        │  │     = 115% ✓                 │
│  └──────────────────────┘  └──────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ CONVERSION FUNNEL: SIGNUPS → PAYING CUSTOMER             │
│  ├──────────────────────────────────────────────────────────┤
│  │                                                          │
│  │ Signups (30d):       12,450  (100%)                      │
│  │       ↓ [85% convert]                                    │
│  │ Email Verified:      10,582  (85%)                       │
│  │       ↓ [45% convert]                                    │
│  │ Setup Complete:       4,762  (45%)                       │
│  │       ↓ [42% convert]                                    │
│  │ Trial Started:        2,000  (16%)                       │
│  │       ↓ [95% convert]                                    │
│  │ First Payment:        1,900  (15%)  🎯                   │
│  │                                                          │
│  │ Signup-to-Payment Conversion: 15% (target 18%)          │
│  │ Key bottleneck: Email Verification (15% drop)           │
│  │                                                          │
│  └──────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ LTV & PAYBACK PERIOD BY ACQUISITION CHANNEL              │
│  ├──────────────────────────────────────────────────────────┤
│  │ Channel          │  CAC  │  LTV  │ LTV:CAC │ Payback     │
│  │ ─────────────────┼───────┼───────┼─────────┼──────────   │
│  │ Organic          │ $0    │ $425  │ ∞:1     │ Immediate   │
│  │ Referral         │ $0    │ $475  │ ∞:1     │ Immediate   │
│  │ Paid Search      │ $4    │ $380  │ 95:1    │ 1.2 months  │
│  │ Social Ads       │ $3    │ $350  │ 117:1   │ 1.1 months  │
│  │ Partnership      │ $2    │ $420  │ 210:1   │ 0.6 months  │
│  │ ─────────────────┼───────┼───────┼─────────┼──────────   │
│  │ Blended          │ $1.27 │ $425  │ 335:1   │ 1.3 months  │
│  │ Target Payback   │       │       │         │ <6 months   │
│  │ Status           │       │       │         │ ✓ HEALTHY   │
│  └──────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────────┐
│  │ CHURN ANALYSIS (Monthly Churn Rate)                      │
│  ├──────────────────────────────────────────────────────────┤
│  │                                                          │
│  │ Starting Users:     18,250                               │
│  │ Churned This Month:    485  (2.7% churn)                 │
│  │ Downgraded:           145                                │
│  │ Ending Users:       18,450  (↑ 200 net)                  │
│  │                                                          │
│  │ By Plan Tier:                                            │
│  │ Enterprise: 0.5% churn (excellent)                       │
│  │ Mid-Market: 2.3% churn (good)                            │
│  │ SMB:        5.8% churn (concerning)                      │
│  │ Freemium:  28.4% churn (expected)                        │
│  │                                                          │
│  │ Action: Focus retention efforts on SMB segment           │
│  │                                                          │
│  └──────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**Revenue Metrics Summary:**

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Monthly Recurring Revenue (MRR) | $1.245M | $1.3M | 96% ✓ |
| Net Revenue Retention | 115% | 120% | 96% ✓ |
| ARPU | $67.50 | $70 | 96% ⚠ |
| Churn Rate | 2.7% | <3.0% | ✓ |
| Payback Period | 1.3 mo | <6 mo | ✓ |
| New MRR | $185k | $200k | 92% ⚠ |
| Expansion MRR | $98k | $150k | 65% ✗ |

---

## 5. Experiment & A/B Test Dashboard

**Purpose:** Track all active and historical A/B tests

**Audience:** Product team, analytics, executives

**Refresh Rate:** Real-time during test, daily after completion

```
┌─────────────────────────────────────────────────────────────┐
│           EXPERIMENTS & A/B TESTS DASHBOARD                  │
├─────────────────────────────────────────────────────────────┤
│
│  ┌─────────────────────────────────────────────────────────┐
│  │ ACTIVE EXPERIMENTS                                      │
│  ├─────────────────────────────────────────────────────────┤
│  │
│  │ Exp 1: Simplified Sign-Up Form (Day 11 of 14)
│  │ ├─ Primary: Sign-up completion rate
│  │ ├─ Control: 5.0% (1,245 converters / 24,900 visitors)
│  │ ├─ Variant: 5.4% (1,356 converters / 25,111 visitors)
│  │ ├─ Relative Lift: +8%
│  │ ├─ P-value: 0.086 (not yet significant, but trending)
│  │ ├─ 95% CI: [-0.5%, 1.8%]
│  │ ├─ Status: RUNNING - Need 3 more days
│  │ └─ Owner: @sarah_pm
│  │
│  │ Exp 2: New Onboarding Flow (Day 5 of 14)
│  │ ├─ Primary: Day 7 Retention
│  │ ├─ Control: 32.1% (8,456 / 26,345)
│  │ ├─ Variant: 33.8% (8,921 / 26,387)
│  │ ├─ Relative Lift: +5.3%
│  │ ├─ P-value: 0.245 (not significant)
│  │ ├─ 95% CI: [-1.2%, 2.8%]
│  │ ├─ Status: RUNNING - Too early to call
│  │ └─ Owner: @marcus_eng
│  │
│  │ Exp 3: Recommendation Algorithm v2 (Day 3 of 21)
│  │ ├─ Primary: Items Per Session
│  │ ├─ Control: 4.2 items/session
│  │ ├─ Variant: 4.8 items/session (+14%)
│  │ ├─ Status: RUNNING - Very early stage
│  │ └─ Owner: @david_ml
│  │
│  └─────────────────────────────────────────────────────────┘
│
│  ┌─────────────────────────────────────────────────────────┐
│  │ RECENT COMPLETED EXPERIMENTS (Last 30 Days)             │
│  ├─────────────────────────────────────────────────────────┤
│  │
│  │ ✓ LAUNCHED: Longer Free Trial (30d → 45d)
│  │   Metric: Trial-to-Paid Conversion
│  │   Result: 18% → 21% (+16.7%, p=0.018)
│  │   Impact: +$47k MRR from this change
│  │   Launched: 4 days ago - confirming in production
│  │
│  │ ✓ LAUNCHED: Better Onboarding Copy
│  │   Metric: Email Verification Rate
│  │   Result: 85% → 87% (+2.4%, p=0.032)
│  │   Impact: +420 users retained per cohort
│  │   Launched: 2 weeks ago - sustained in new cohorts
│  │
│  │ ✗ REVERTED: "Gamification" Feature
│  │   Metric: Daily Active Users
│  │   Result: 485k → 472k (-2.7%, p=0.041)
│  │   Finding: Users found badges confusing/distracting
│  │   Learning: Simpler is better for this demographic
│  │   Next: Consider for advanced users only
│  │
│  │ ⏸ PAUSED: New Search Filter UI
│  │   Metric: Search Refinement Rate
│  │   Result: Inconclusive (p=0.34, needs more data)
│  │   Plan: Continue test for 1 more week
│  │   Current: 12 days into 14-day test
│  │
│  └─────────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────┐  ┌──────────────────────┐
│  │ EXPERIMENT VELOCITY          │  │ TEST IDEAS BACKLOG   │
│  ├──────────────────────────────┤  ├──────────────────────┤
│  │ Tests Launched (90 days): 12 │  │ Waiting to Test:  8  │
│  │ Tests Completed:           9 │  │ In Design:        5  │
│  │ Tests Won (positive):      6 │  │ High Priority:    3  │
│  │ Tests Lost (negative):     2 │  │                      │
│  │ Tests Inconclusive:        1 │  │ Next Test:        3  │
│  │                              │  │ weeks out            │
│  │ Win Rate: 67%                │  │                      │
│  │ Avg Duration: 12 days        │  │                      │
│  │ Avg Sample Size: 8,500/arm   │  │                      │
│  └──────────────────────────────┘  └──────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**Active Tests Table:**

| Experiment | Day | Primary Metric | Control | Variant | Lift | P-Value | Status |
|-----------|-----|---|---|---|---|---|---|
| Sign-Up Form | 11/14 | Completion Rate | 5.0% | 5.4% | +8% | 0.086 | Running |
| Onboarding | 5/14 | Day 7 Ret | 32.1% | 33.8% | +5% | 0.245 | Running |
| Recommend Algo | 3/21 | Items/Session | 4.2 | 4.8 | +14% | - | Early |

---

## 6. Executive Summary Dashboard (Monthly)

**Purpose:** Share key results and trends with leadership

**Audience:** CEO, CFO, VP product, board

**Refresh Rate:** Monthly

```
┌────────────────────────────────────────────────────────────────┐
│              MONTHLY EXECUTIVE SUMMARY REPORT                   │
│                     November 2025                              │
├────────────────────────────────────────────────────────────────┤
│
│  KEY PERFORMANCE INDICATORS
│  ─────────────────────────────────────────────────────────────
│
│  Metric                  │ Nov    │ Oct    │ Target │ YTD   │ Trend
│  ───────────────────────┼────────┼────────┼────────┼───────┼──────
│  Monthly Active Users    │ 2.45M  │ 2.40M  │ 2.50M  │ 2.45M │ ↑
│  Daily Active Users      │ 485k   │ 477k   │ 500k   │ 475k  │ ↑
│  New Paying Users        │ 1,900  │ 1,780  │ 2,000  │18.4k  │ ↑
│  Monthly Recurring Rev   │$1.245M │$1.207M │$1.30M  │$14.2M │ ↑
│  Net Revenue Retention   │  115%  │  112%  │  120%  │  114% │ ↑
│  Customer Churn Rate     │  2.7%  │  3.1%  │ <3.0%  │  2.9% │ ↓
│  Day 7 Retention         │ 32.4%  │ 33.4%  │ 34.0%  │ 32.8% │ ↓
│  ARPU                    │ $67.50 │ $65.80 │ $70.00 │$65.20 │ ↑
│
│  ─────────────────────────────────────────────────────────────
│
│  RESULTS SUMMARY
│
│  ✓ STRONG PERFORMANCE
│  • MAU +2.1% MoM, tracking to annual target
│  • 115% NRR achieved, expansion revenue growing
│  • Paid user acquisition up 6.7% MoM
│  • 3 major features launched, positive early signals
│
│  ⚠ AREAS TO MONITOR
│  • Day 7 retention down 1.0pp - investigating cause
│  • Feature X adoption plateaued at 43%
│  • SMB churn rate elevated at 5.8% vs. 3.0% enterprise
│  • Paid CAC payback at 1.3mo, target is 1.0mo
│
│  ACTION ITEMS
│  1. Launch improved onboarding (A/B test passed)
│  2. Investigate Day 7 retention drop
│  3. Run retention test for SMB segment
│  4. Double down on expansion revenue initiatives
│
│  ─────────────────────────────────────────────────────────────
│
│  YEAR-TO-DATE PROGRESS
│
│  Target: $20M ARR by year-end
│  Current MRR: $1.245M x 12 = $14.94M ARR
│  Progress: 75% of target
│  Runway: 6 weeks of data → 12% implied growth needed
│
│  Marketing & Acquisition
│  • Total Paid Spend: $450k YTD
│  • Blended CAC: $1.27
│  • Blended Payback: 1.3 months
│  • LTV:CAC Ratio: 335:1 (target 200:1+) ✓
│
│  Product Development
│  • A/B Tests Run: 12 (Win rate: 67%)
│  • Features Launched: 8 major features
│  • Retention Improvement: +1.2pp since July
│  • Engagement Improvement: DAU/MAU +3pp
│
│  ─────────────────────────────────────────────────────────────
│
│  STRATEGIC PRIORITIES FOR NEXT MONTH
│
│  1. Fix Day 7 retention gap (target: +2pp)
│  2. Launch SMB-optimized onboarding flow
│  3. Improve Feature X discovery and adoption
│  4. Invest in expansion revenue program
│  5. Maintain velocity: 2-3 A/B tests per week
│
└────────────────────────────────────────────────────────────────┘
```

---

## Design Best Practices

### 1. Information Hierarchy
- Most important metrics largest/first
- Supporting metrics smaller/grouped
- Trends and context visible at a glance

### 2. Visual Clarity
- Use colors: Green (good), Yellow (caution), Red (alert)
- Numbers prominent, comparisons clear
- Trend arrows (↑ ↓ →) immediately obvious

### 3. Actionability
- Show not just metrics but implications
- Include recommended actions/next steps
- Highlight anomalies and red flags

### 4. Appropriate Segmentation
- Break down by meaningful dimensions
- Show segment-level performance
- Identify outlier segments

### 5. Context and Benchmarks
- Current value vs. target clearly marked
- Trend context (vs. last period, YTD)
- Benchmarks to industry/competitors

### 6. Accessibility
- Large, readable fonts
- Color-blind friendly (avoid red/green only)
- Printable if needed
- Mobile-responsive view

---

## Tools to Build These Dashboards

- **Amplitude:** Native dashboards for adoption/retention
- **Mixpanel:** Detailed funnel and behavioral analytics
- **Looker:** Custom dashboards, flexible BI
- **Tableau:** Enterprise visualization and dashboarding
- **Metabase:** SQL-based, self-service analytics
- **Google Data Studio:** Free, easy to build, integrated with Google products
- **Grafana:** More technical, real-time monitoring
