# Executive Dashboards - Complete Implementation Guide

## Overview

Executive dashboards serve C-suite and senior leadership with high-level strategic KPIs. They answer the question: "How is the business performing?"

**Key Characteristics**:
- 5-7 KPIs maximum
- Minimal detail, maximum clarity
- Mobile-optimized (executives are often on-the-go)
- Glanceable in 10-30 seconds
- Action-oriented

---

## Design Principles for Executive Dashboards

### 1. Extreme Simplicity

**Less is More** - Each metric must earn its place.

**Test**: If executive can't understand metric in 3 seconds, remove or clarify it.

### 2. Answer Strategic Questions

Common executive questions:
- Are we hitting our targets?
- Where should I focus attention?
- What trends should I be aware of?
- Are there emerging issues?

### 3. Exception-Based Design

**Highlight what needs attention, not everything.**

Normal metrics → Gray, subtle
Problem metrics → Color, prominent
Critical alerts → Top of dashboard

---

## The 5-Metric Executive Dashboard

### Metric 1: Primary Business Health Indicator

**For SaaS**: ARR or MRR
**For E-commerce**: GMV or Revenue
**For Services**: Revenue or Billable Hours

**Display Format**:
```
Annual Recurring Revenue
$12.3M
120% of $10.2M annual target ✓
+18% YoY

[━━━━━━━━━━━━━━] 12-month trend
```

**Components**:
- Current value (large, bold)
- Target comparison (context)
- Year-over-year growth (trend direction)
- Sparkline (visual confirmation)

### Metric 2: Growth Indicator

**Customer Acquisition, Revenue Growth, User Growth**

**Display**:
```
New Customers (This Quarter)
1,234
+15% vs Q3 ▲
On track for annual goal

Target: 1,200 [███████████░░] 103%
```

### Metric 3: Efficiency/Profitability

**Gross Margin, EBITDA Margin, Unit Economics**

**Display**:
```
Gross Margin
62%
Target: 60% (+2pp) ✓
Industry Avg: 58%

[Bullet chart showing vs target and industry]
```

### Metric 4: Customer Health

**NPS, Churn Rate, Customer Satisfaction**

**Display**:
```
Net Promoter Score
45
Target: 40+ ✓
Improved from 42 last quarter ▲

Promoters 50% | Passive 40% | Detractors 10%
```

### Metric 5: Critical Leading Indicator

**Pipeline, Engagement, Key Usage Metric**

**Display**:
```
Sales Pipeline
$15.2M
Weighted: $6.1M (40% probability)
↗ Growing 8% MoM

Coverage: 3.0x quarterly quota ✓
```

---

## Layout Templates

### Template A: KPI Hero

**Best For**: Single most important metric

```
┌────────────────────────────────────────┐
│  Executive Dashboard      [Export ▾]   │
├────────────────────────────────────────┤
│                                        │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│  ┃  Annual Recurring Revenue       ┃ │
│  ┃                                 ┃ │
│  ┃      $12.3M                     ┃ │
│  ┃      120% of target ✓           ┃ │
│  ┃                                 ┃ │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                        │
│  [12-month trend - large line chart]   │
│                                        │
│  ┌──────────┬──────────┬──────────┐  │
│  │ Growth   │ Margin   │ NPS      │  │
│  │ +15% ▲   │ 62% ✓    │ 45 ✓     │  │
│  │ [Trend]  │ [Bullet] │ [Gauge]  │  │
│  └──────────┴──────────┴──────────┘  │
│                                        │
└────────────────────────────────────────┘
```

### Template B: Balanced View

**Best For**: Multiple equally-important metrics

```
┌────────────────────────────────────────┐
│  Q4 Executive Summary    [Filters ▾]   │
├────────────────────────────────────────┤
│                                        │
│  ┌────────────┬────────────┬────────┐ │
│  │ Revenue    │ Customers  │ NPS    │ │
│  │ $12.3M     │ 1,234      │ 45     │ │
│  │ 120% ✓     │ +15% ▲     │ ✓      │ │
│  │ [Trend]    │ [Trend]    │ [Dist] │ │
│  └────────────┴────────────┴────────┘ │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ Key Trends & Insights           │  │
│  │ [Annotated multi-series chart]  │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌────────────┬─────────────────────┐ │
│  │ Pipeline   │  Critical Alerts    │ │
│  │ $15.2M     │  • SMB churn up    │ │
│  │ [Funnel]   │  • Deal cycle +5d  │ │
│  └────────────┴─────────────────────┘ │
│                                        │
└────────────────────────────────────────┘
```

### Template C: Scorecard

**Best For**: Tracking many KPIs against targets

```
┌────────────────────────────────────────┐
│  Monthly Business Review - November    │
├────────────────────────────────────────┤
│                                        │
│  Metric              Actual  Target    │
│  ─────────────────────────────────────│
│  Revenue             ✓ $1.2M  $1.0M   │
│  [██████████████░░] 120%              │
│                                        │
│  New Customers       ✓  234    200    │
│  [███████████████░] 117%              │
│                                        │
│  Churn Rate          ⚠  2.3%  <2.0%   │
│  [█████████████████] 115% (bad)       │
│                                        │
│  NPS                 ✓  45     40+    │
│  [█████████████░░░]  113%             │
│                                        │
│  Gross Margin        ✓  62%    60%    │
│  [██████████████░░] 103%              │
│                                        │
└────────────────────────────────────────┘
```

---

## Mobile-First Executive Dashboard

**Challenge**: Executives are mobile - dashboard must work on phone

**Mobile Layout** (375px wide):
```
┌───────────────────┐
│ ☰ Q4 Dashboard    │
├───────────────────┤
│                   │
│ PRIMARY KPI       │
│                   │
│   $12.3M          │ ← Large, bold
│   120% of target ✓│
│   +18% YoY ▲      │
│                   │
│ [━━━━━━━━━━━━━]  │ ← Sparkline
│                   │
├───────────────────┤
│                   │
│ New Customers     │
│ 1,234 (+15% ▲)    │
│ [━━━━━━━━━━━━━]  │
│                   │
├───────────────────┤
│                   │
│ Gross Margin      │
│ 62% (✓ Target)    │
│ [━━━━━━━━━━━━━]  │
│                   │
├───────────────────┤
│                   │
│ NPS: 45 (✓)       │
│ Pipeline: $15.2M  │
│                   │
├───────────────────┤
│                   │
│ [View Details →]  │
│                   │
└───────────────────┘

Scroll for more details
```

**Key Features**:
- Vertical stack
- One metric per screen section
- Large, readable numbers
- Simplified sparklines
- Link to detailed dashboard

---

## Alert Design for Executives

### Alert Levels

**Critical (Red)** - Immediate action required
```
🔴 CRITICAL: Churn rate 4.5% (Target: <2%)
   Impact: $200K ARR at risk
   Action: Emergency customer success review
```

**Warning (Orange)** - Attention needed
```
🟠 WARNING: Deal cycle extended to 50 days (from 45)
   Impact: May miss Q4 target
   Action: Review pipeline with sales VP
```

**Info (Blue)** - Notable but not urgent
```
🔵 INFO: New customer acquisition 5% above plan
   Impact: Positive momentum
   Action: Continue current marketing strategy
```

### Alert Placement

**Option 1: Top Banner** (if active alerts)
```
┌────────────────────────────────────────┐
│ ⚠ 2 ITEMS NEED ATTENTION              │
│ • Churn rate elevated (4.5%)          │
│ • Deal cycle slowing (+5 days)        │
│ [View All Alerts]                     │
├────────────────────────────────────────┤
│ [Rest of dashboard]                    │
```

**Option 2: Alert Card** (always visible)
```
┌────────────────────────────────────────┐
│ [KPI cards]                            │
├────────────────────────────────────────┤
│  🔔 ALERTS & ITEMS FOR ATTENTION       │
│  ─────────────────────────────────────│
│  🔴 Churn elevated (action required)  │
│  🟠 Pipeline coverage low (watch)     │
│  ✓ All other metrics on track         │
└────────────────────────────────────────┘
```

---

## Storytelling for Executives

### Narrative Structure

**1. Headline** - The punchline first
```
✓ STRONG QUARTER
On track to exceed annual target by 20%
```

**2. Evidence** - Visual proof
```
[Chart showing consistent growth, crossing target line]
```

**3. Insight** - What's driving it
```
💡 KEY DRIVERS:
• Enterprise segment +40% (new sales team)
• Product adoption +25% (feature launch)
• Churn reduced to 2.0% (CS investment paying off)
```

**4. Concerns** - Don't hide problems
```
⚠ WATCH AREAS:
• SMB acquisition slowing (-12%)
• Sales cycle lengthening (+5 days)
```

**5. Action** - What to do
```
🎯 PRIORITIES:
1. Invest in SMB marketing
2. Streamline sales process
3. Continue enterprise momentum
```

### Example: Complete Executive Narrative Dashboard

```
┌────────────────────────────────────────────────┐
│  Q4 BUSINESS REVIEW                            │
├────────────────────────────────────────────────┤
│                                                │
│  ✓ EXCEEDING TARGETS                          │
│  Annual Recurring Revenue: $12.3M (120%)       │
│  Gross Margin: 62% (Target: 60%)              │
│                                                │
│  [Growth chart showing upward trend]           │
│                                                │
│  💡 WHAT'S WORKING:                            │
│  • Enterprise sales up 40%                    │
│  • Customer retention at 98%                   │
│  • New product driving 25% of growth          │
│                                                │
│  ⚠ WHAT TO WATCH:                             │
│  • SMB acquisition down 12%                   │
│  • Deal cycle extended (+5 days)              │
│                                                │
│  🎯 NEXT QUARTER PRIORITIES:                  │
│  1. Launch SMB self-service offering          │
│  2. Streamline enterprise sales process        │
│  3. Expand into European market               │
│                                                │
│  [Detailed Metrics →]                          │
└────────────────────────────────────────────────┘
```

---

## Implementation Checklist

### Pre-Design
- [ ] Interview executives on key questions
- [ ] Identify single most important metric
- [ ] Document 5-7 critical KPIs
- [ ] Define "success" vs "concern" thresholds
- [ ] Understand viewing context (device, frequency)

### Design
- [ ] Maximum 7 KPIs on main view
- [ ] All metrics show target/comparison
- [ ] Visual hierarchy clear (most important = largest)
- [ ] Alerts/exceptions highlighted
- [ ] Mobile layout designed
- [ ] Load time <2 seconds

### Content
- [ ] Each metric has clear label
- [ ] Context provided (target, previous, benchmark)
- [ ] Trend direction shown (▲▼─)
- [ ] Sparklines for quick trend recognition
- [ ] Data freshness timestamp

### Accessibility
- [ ] Works on mobile devices
- [ ] High contrast for readability
- [ ] Large enough for viewing in meetings
- [ ] Printable if needed

### Testing
- [ ] 10-second test (can grasp status in 10s)
- [ ] Decision test (clear what action to take)
- [ ] Mobile test (works on executive's phone)
- [ ] Meeting test (readable on large screen)

---

## Common Mistakes to Avoid

❌ **Too many metrics** (15+ KPIs)
✓ Limit to 5-7 most critical

❌ **Operational details** (individual transactions)
✓ Strategic summary only

❌ **No context** (just numbers)
✓ Always show target, previous, benchmark

❌ **Cluttered design** (chartjunk)
✓ Clean, minimal, focused

❌ **Desktop-only** (doesn't work on mobile)
✓ Mobile-first design

❌ **Static numbers** (no trend)
✓ Show direction with sparklines

❌ **No narrative** (just data dump)
✓ Tell the story: status → insight → action

---

## Case Studies

### Case Study 1: SaaS Company Executive Dashboard

**Audience**: CEO, CFO, Board
**Frequency**: Daily (CEO), Weekly (Board)
**Device**: Mobile (CEO), Presentation (Board)

**5 Key Metrics**:
1. ARR: $12.3M (120% of plan)
2. Net Revenue Retention: 105%
3. New Customers: 1,234 (+15%)
4. Gross Margin: 62%
5. Cash Runway: 18 months

**Layout**: KPI Hero (ARR primary)
**Mobile**: Yes
**Result**: CEO checks in 90 seconds each morning

### Case Study 2: E-commerce Executive Dashboard

**Audience**: CEO, COO
**Frequency**: Real-time during events, Daily otherwise
**Device**: Desktop, Large Display

**5 Key Metrics**:
1. GMV: $2.3M (this month)
2. Conversion Rate: 3.2%
3. Average Order Value: $87
4. Customer Acquisition Cost: $23
5. Return Rate: 8%

**Layout**: Balanced View
**Features**: Real-time updates during sales events
**Result**: Immediate visibility during Black Friday

---

## References

- Stephen Few: "Information Dashboard Design" - Chapter 4: Executive Dashboards
- Gartner: "How to Design Dashboards for C-Suite Executives"
- Harvard Business Review: "How to Design a Dashboard Your CEO Will Use"
