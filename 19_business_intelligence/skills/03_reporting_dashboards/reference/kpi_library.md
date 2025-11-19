# KPI Library - Common Business Metrics

## How to Display KPIs (Stephen Few Method)

### KPI Components
1. **Primary Value**: The actual metric (large, prominent)
2. **Comparison Context**: Target, previous period, or benchmark
3. **Trend Indicator**: Direction and magnitude of change
4. **Time Period**: When this metric applies
5. **Sparkline** (optional): Recent trend visualization

### Display Format (Bullet Chart Preferred)
```
Revenue: $1.2M
Target: $1.0M (+20%)
QoQ: +15% ▲
[━━━━━━━━━━░░] Sparkline showing trend
```

## Financial KPIs

### Revenue Metrics

**Revenue (Total/Recurring/One-time)**
- **Formula**: Sum of all sales
- **Display**: Currency, with comparison to target and prior period
- **Frequency**: Daily/Weekly/Monthly
- **Context**: Include MoM, QoQ, or YoY change
```
Visualization: Bullet chart or large number + trend line
Grouping: By product, region, customer segment
```

**Revenue Growth Rate**
- **Formula**: ((Current Period - Previous Period) / Previous Period) × 100
- **Display**: Percentage with trend indicator
- **Frequency**: Monthly/Quarterly
- **Benchmark**: Industry average, target growth rate
```
Visualization: Line chart over time + current value
Alert: <5% (warning), <0% (critical)
```

**Average Revenue Per User (ARPU)**
- **Formula**: Total Revenue / Number of Users
- **Display**: Currency per user
- **Frequency**: Monthly
- **Context**: Compare across cohorts, segments
```
Visualization: Trend line + cohort comparison
Segmentation: By acquisition channel, tenure, plan type
```

**Annual Recurring Revenue (ARR)**
- **Formula**: Monthly Recurring Revenue × 12
- **Display**: Large currency value
- **Frequency**: Monthly
- **Context**: MRR trend, churn impact
```
Visualization: Waterfall chart showing adds/churns
Components: New ARR, Expansion, Contraction, Churn
```

### Profitability Metrics

**Gross Profit Margin**
- **Formula**: ((Revenue - COGS) / Revenue) × 100
- **Display**: Percentage
- **Frequency**: Monthly
- **Target**: Industry-dependent (often 60-80% for SaaS)
```
Visualization: Bullet chart with industry benchmark
Trend: Line chart over 12-24 months
```

**EBITDA**
- **Formula**: Earnings Before Interest, Taxes, Depreciation, Amortization
- **Display**: Currency
- **Frequency**: Monthly/Quarterly
- **Context**: EBITDA margin % alongside
```
Visualization: Stacked bar showing revenue, expenses, EBITDA
Breakdown: By business unit or product line
```

**Customer Acquisition Cost (CAC)**
- **Formula**: Sales & Marketing Expenses / New Customers Acquired
- **Display**: Currency per customer
- **Frequency**: Monthly
- **Critical Ratio**: LTV:CAC should be >3:1
```
Visualization: Trend line + LTV comparison
Breakdown: By channel (paid, organic, referral)
```

**Lifetime Value (LTV)**
- **Formula**: (ARPU × Gross Margin) / Churn Rate
- **Display**: Currency
- **Frequency**: Quarterly
- **Context**: CAC, LTV:CAC ratio
```
Visualization: Bar chart by cohort
Trend: LTV over time by acquisition cohort
```

## Customer Metrics

### Acquisition

**Customer Acquisition Rate**
- **Formula**: New Customers in Period
- **Display**: Count with growth %
- **Frequency**: Daily/Weekly/Monthly
- **Context**: By channel, campaign
```
Visualization: Stacked bar by acquisition channel
Trend: Line chart with seasonality annotation
```

**Conversion Rate (Funnel)**
- **Formula**: (Conversions / Total Visitors) × 100
- **Display**: Percentage per funnel stage
- **Frequency**: Daily
- **Benchmark**: Industry standard, historical best
```
Visualization: Funnel chart or slope chart
Stages: Visitor → Lead → Opportunity → Customer
```

**Cost Per Acquisition (CPA) by Channel**
- **Formula**: Channel Spend / Conversions from Channel
- **Display**: Currency, with channel comparison
- **Frequency**: Weekly
- **Action**: Pause channels with CPA > target
```
Visualization: Horizontal bar chart (descending by efficiency)
Comparison: Actual vs. target CPA line
```

### Retention

**Customer Churn Rate**
- **Formula**: (Customers Lost / Starting Customers) × 100
- **Display**: Percentage
- **Frequency**: Monthly
- **Critical Alert**: >5% monthly for SaaS
```
Visualization: Line chart with benchmark
Cohort Analysis: Churn by acquisition cohort
```

**Net Revenue Retention (NRR)**
- **Formula**: ((Starting MRR + Expansion - Contraction - Churn) / Starting MRR) × 100
- **Display**: Percentage
- **Frequency**: Monthly
- **Target**: >100% (negative churn)
```
Visualization: Waterfall chart showing components
Trend: Monthly NRR over time
```

**Customer Lifetime (Average)**
- **Formula**: 1 / Churn Rate
- **Display**: Months or years
- **Frequency**: Quarterly
- **Use**: Input for LTV calculation
```
Visualization: Trend line by cohort
Segmentation: By product, plan, segment
```

### Engagement

**Daily/Monthly Active Users (DAU/MAU)**
- **Formula**: Count of unique active users
- **Display**: Number, with DAU/MAU ratio
- **Frequency**: Daily
- **Context**: Stickiness ratio (DAU/MAU)
```
Visualization: Dual-axis line chart (DAU + MAU)
Stickiness: DAU/MAU as secondary metric
```

**Feature Adoption Rate**
- **Formula**: (Users Using Feature / Total Users) × 100
- **Display**: Percentage per feature
- **Frequency**: Weekly
- **Target**: Varies by feature criticality
```
Visualization: Horizontal bar chart of features
Trend: Adoption curve over time since launch
```

**Net Promoter Score (NPS)**
- **Formula**: % Promoters - % Detractors
- **Display**: Score (-100 to +100)
- **Frequency**: Quarterly
- **Benchmark**: Industry NPS
```
Visualization: Gauge or bullet chart
Distribution: Stacked bar showing promoters/passive/detractors
```

## Operational Metrics

### Sales

**Sales Pipeline Value**
- **Formula**: Sum of (Opportunity Value × Probability)
- **Display**: Currency
- **Frequency**: Daily/Weekly
- **Context**: By stage, rep, product
```
Visualization: Stacked bar by pipeline stage
Trend: Pipeline growth over time
```

**Win Rate**
- **Formula**: (Closed-Won / Total Closed) × 100
- **Display**: Percentage
- **Frequency**: Monthly
- **Context**: By rep, product, deal size
```
Visualization: Line chart by cohort
Comparison: Rep performance distribution
```

**Sales Cycle Length**
- **Formula**: Average days from lead to close
- **Display**: Days
- **Frequency**: Monthly
- **Target**: Minimize while maintaining quality
```
Visualization: Box plot by product/segment
Trend: Median cycle length over time
```

**Average Deal Size**
- **Formula**: Total Contract Value / Number of Deals
- **Display**: Currency
- **Frequency**: Monthly
- **Context**: By segment, product
```
Visualization: Histogram of deal sizes
Trend: Median and mean over time
```

### Support

**First Response Time**
- **Formula**: Average time from ticket creation to first response
- **Display**: Hours or minutes
- **Frequency**: Daily
- **SLA**: Often <1 hour for critical, <24 for normal
```
Visualization: Line chart with SLA threshold
Distribution: Histogram of response times
```

**Resolution Time**
- **Formula**: Average time from ticket creation to resolution
- **Display**: Hours or days
- **Frequency**: Daily
- **Context**: By priority, category
```
Visualization: Box plot by ticket category
Trend: Median resolution time
```

**Customer Satisfaction (CSAT)**
- **Formula**: (Positive Ratings / Total Ratings) × 100
- **Display**: Percentage or score out of 5
- **Frequency**: Daily
- **Target**: >90% or >4.5/5
```
Visualization: Trend line + distribution
Breakdown: By support channel, issue type
```

**Ticket Volume**
- **Formula**: Count of tickets created
- **Display**: Number with trend
- **Frequency**: Daily
- **Context**: By category, priority
```
Visualization: Stacked area by category
Pattern: Identify spikes and trends
```

### Product/Engineering

**System Uptime**
- **Formula**: (Total Time - Downtime) / Total Time × 100
- **Display**: Percentage (e.g., 99.95%)
- **Frequency**: Real-time
- **SLA**: Often 99.9% or 99.99%
```
Visualization: Status indicator + uptime trend
Incidents: Annotated timeline of outages
```

**API Response Time (p95, p99)**
- **Formula**: 95th/99th percentile of response times
- **Display**: Milliseconds
- **Frequency**: Real-time/Hourly
- **Target**: <200ms (p95), <500ms (p99)
```
Visualization: Line chart with threshold
Heatmap: Response time by endpoint and time
```

**Deployment Frequency**
- **Formula**: Number of deployments per period
- **Display**: Count per day/week
- **Frequency**: Weekly
- **DORA Metric**: Elite = multiple per day
```
Visualization: Bar chart by week
Trend: Deployment frequency over time
```

**Change Failure Rate**
- **Formula**: (Failed Changes / Total Changes) × 100
- **Display**: Percentage
- **Frequency**: Weekly
- **DORA Metric**: Elite = 0-15%
```
Visualization: Line chart with target band
Context: Severity of failures
```

## Marketing Metrics

**Website Traffic**
- **Formula**: Unique visitors to site
- **Display**: Number with growth %
- **Frequency**: Daily/Weekly
- **Context**: By source, landing page
```
Visualization: Stacked area by traffic source
Conversion: Overlay conversion rate
```

**Lead Generation Rate**
- **Formula**: Marketing Qualified Leads (MQLs) generated
- **Display**: Count with cost per lead
- **Frequency**: Weekly
- **Context**: By campaign, channel
```
Visualization: Bar chart by channel
Efficiency: Cost per lead trend
```

**Email Open/Click Rates**
- **Formula**: (Opens or Clicks / Delivered) × 100
- **Display**: Percentage
- **Frequency**: Per campaign
- **Benchmark**: Industry standards (20% open, 3% click)
```
Visualization: Scatter plot (open vs click rate)
Trend: Performance by campaign type
```

**Marketing ROI**
- **Formula**: (Revenue from Marketing - Marketing Cost) / Marketing Cost × 100
- **Display**: Percentage or ratio
- **Frequency**: Monthly/Quarterly
- **Target**: Positive ROI, ideally >300%
```
Visualization: Bar chart by channel/campaign
Trend: ROI improvement over time
```

## KPI Dashboard Design Principles

### Few's Rules for KPI Display

1. **Context is Essential**
   - Always show comparison (target, benchmark, prior period)
   - Never show a metric in isolation
   - Use bullet charts for performance vs target

2. **Trends Matter**
   - Include sparklines for quick trend recognition
   - Show direction and magnitude of change
   - Annotate significant events

3. **Alert Appropriately**
   - Use color sparingly for exceptions
   - Define clear thresholds
   - Make required actions obvious

4. **Keep It Simple**
   - One primary value per KPI
   - Minimize supporting text
   - No decoration

### KPI Organization

**By User Type:**
- Executive: 5-7 strategic KPIs
- Manager: 10-15 tactical KPIs
- Analyst: 20-30 detailed metrics

**By Update Frequency:**
- Real-time: Operational metrics
- Daily: Sales, support, product metrics
- Weekly: Marketing, engagement
- Monthly: Financial, customer retention
- Quarterly: Strategic, cohort analysis

**By Department:**
- Finance: Revenue, profitability, cash flow
- Sales: Pipeline, win rate, quota attainment
- Marketing: Acquisition cost, leads, ROI
- Product: Engagement, adoption, retention
- Support: CSAT, response time, resolution
- Engineering: Uptime, performance, velocity

## KPI Calculation SQL Templates

See `/src/kpi_calculations.sql` for complete SQL implementations of all KPIs with proper aggregation, windowing, and optimization.

## References
- Stephen Few: "Information Dashboard Design"
- Lean Analytics (Croll & Yoskovitz)
- Measure What Matters (John Doerr - OKRs)
- SaaS Metrics 2.0 (David Skok)
