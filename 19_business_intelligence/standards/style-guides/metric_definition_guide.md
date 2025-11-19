# Metric Definition Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Metric Taxonomy](#metric-taxonomy)
3. [Dimensions vs Measures](#dimensions-vs-measures)
4. [Metric Versioning and Evolution](#metric-versioning-and-evolution)
5. [Calculation Logic Documentation](#calculation-logic-documentation)
6. [Business vs Technical Definitions](#business-vs-technical-definitions)
7. [Metric Certification Process](#metric-certification-process)
8. [Slowly Changing Dimensions in Metrics](#slowly-changing-dimensions-in-metrics)
9. [Metric Stores and Semantic Layers](#metric-stores-and-semantic-layers)
10. [Industry Examples](#industry-examples)
11. [Anti-Patterns and Pitfalls](#anti-patterns-and-pitfalls)

---

## Introduction

### The Metric Crisis

Organizations often suffer from:
- **Multiple versions of truth**: Different teams calculate "revenue" differently
- **Tribal knowledge**: Only one person knows how a metric is really calculated
- **Metric proliferation**: 500+ metrics with 90% unused
- **No lineage**: Can't trace metric back to source data
- **No governance**: Anyone can create metrics without review

### The Solution: Metric Definition Standards

A well-defined metric has:
1. **Single source of truth**: One canonical definition
2. **Clear ownership**: Someone responsible for accuracy
3. **Complete documentation**: Business + technical definitions
4. **Version control**: Changes tracked and communicated
5. **Validation**: Tested and certified
6. **Discoverability**: Searchable and well-tagged

### Metric Lifecycle

```
Create → Document → Validate → Certify → Monitor → Evolve → Deprecate
   ↑                                                             ↓
   └─────────────────────────────────────────────────────────────┘
                    Continuous improvement loop
```

---

## Metric Taxonomy

### Classification by Type

#### 1. Counters (Additive Metrics)

**Definition**: Simple counts that can be summed across any dimension.

**Examples**:
- Number of orders
- Number of sign-ups
- Number of page views
- Number of errors

**Properties**:
- Integer values (usually)
- Always ≥ 0
- Additive across time and dimensions
- Can be used in ratio calculations

**SQL Pattern**:
```sql
SELECT
    COUNT(*) AS order_count,
    COUNT(DISTINCT order_id) AS distinct_order_count
FROM orders
WHERE order_date = '2024-03-20'
```

**Documentation Template**:
```yaml
metric_name: order_count
type: counter
aggregation: count
grain: daily
additivity: fully_additive
nullable: false
valid_range: [0, null]
```

#### 2. Gauges (Point-in-Time Metrics)

**Definition**: Snapshot values at a specific point in time. NOT additive across time.

**Examples**:
- Current inventory level
- Active user count (at time T)
- Account balance
- Queue depth

**Properties**:
- Can increase or decrease
- Time-dependent
- NOT additive across time periods
- Can be additive across dimensions

**SQL Pattern**:
```sql
-- Snapshot at end of day
SELECT
    COUNT(*) AS active_users
FROM users
WHERE status = 'active'
    AND created_at <= '2024-03-20 23:59:59'
    AND (deleted_at IS NULL OR deleted_at > '2024-03-20 23:59:59')
```

**Common Mistake**:
```sql
-- WRONG: Summing daily snapshots
SELECT SUM(daily_active_users) FROM daily_snapshots  -- Meaningless!

-- RIGHT: Use snapshot at specific time or average
SELECT AVG(daily_active_users) FROM daily_snapshots  -- Average DAU
```

#### 3. Ratios

**Definition**: Division of two metrics. Units depend on numerator/denominator.

**Examples**:
- Conversion rate (orders / visitors)
- Click-through rate (clicks / impressions)
- Average order value (revenue / orders)
- Margin (profit / revenue)

**Properties**:
- Can be percentage or decimal
- NOT directly additive (must recalculate from components)
- Sensitive to denominators of zero
- May need weighting for aggregation

**SQL Pattern**:
```sql
-- Calculate ratio from components
SELECT
    order_date,
    SUM(revenue) / COUNT(DISTINCT order_id) AS average_order_value,
    COUNT(DISTINCT order_id)::FLOAT / COUNT(DISTINCT visitor_id) AS conversion_rate
FROM orders
GROUP BY order_date
```

**Weighted Average**:
```sql
-- WRONG: Average of daily conversion rates
SELECT AVG(daily_conversion_rate) FROM daily_metrics;  -- Not weighted!

-- RIGHT: Recalculate from totals
SELECT
    SUM(orders)::FLOAT / SUM(visitors) AS overall_conversion_rate
FROM daily_metrics;
```

#### 4. Cumulative Metrics

**Definition**: Running totals over time.

**Examples**:
- Total revenue to date
- Cumulative sign-ups
- Lifetime value
- Year-to-date sales

**SQL Pattern**:
```sql
SELECT
    order_date,
    revenue,
    SUM(revenue) OVER (ORDER BY order_date) AS cumulative_revenue
FROM daily_revenue
ORDER BY order_date
```

#### 5. Delta Metrics (Change Metrics)

**Definition**: Change in a metric over time.

**Examples**:
- Daily new users (change in total users)
- Revenue growth (change in revenue)
- Inventory delta (change in inventory)

**SQL Pattern**:
```sql
SELECT
    metric_date,
    metric_value,
    metric_value - LAG(metric_value) OVER (ORDER BY metric_date) AS day_over_day_change,
    (metric_value - LAG(metric_value) OVER (ORDER BY metric_date))
        / NULLIF(LAG(metric_value) OVER (ORDER BY metric_date), 0) AS day_over_day_pct_change
FROM daily_metrics
```

### Classification by Business Function

#### Revenue Metrics
- **ARR** (Annual Recurring Revenue)
- **MRR** (Monthly Recurring Revenue)
- **ARPU** (Average Revenue Per User)
- **LTV** (Lifetime Value)

#### Engagement Metrics
- **DAU** (Daily Active Users)
- **MAU** (Monthly Active Users)
- **Session Duration**
- **Stickiness** (DAU/MAU)

#### Acquisition Metrics
- **CAC** (Customer Acquisition Cost)
- **Sign-up Rate**
- **Organic vs. Paid Mix**
- **Time to Convert**

#### Retention Metrics
- **Churn Rate**
- **Retention Rate**
- **Cohort Retention**
- **Net Revenue Retention (NRR)**

#### Operational Metrics
- **Order Fulfillment Time**
- **Error Rate**
- **Uptime / Availability**
- **Support Ticket Volume**

---

## Dimensions vs Measures

### Measures (Metrics)

**Definition**: Quantitative values that can be aggregated.

**Characteristics**:
- Numeric
- Aggregatable (sum, avg, count, etc.)
- Answer "how much?" or "how many?"

**Examples**:
```sql
-- Measures
SUM(revenue) AS total_revenue
COUNT(DISTINCT user_id) AS user_count
AVG(session_duration_seconds) AS avg_session_duration
MAX(order_timestamp) AS last_order_time
```

**Aggregation Types**:
- **Sum**: Total revenue, total orders
- **Count**: Number of users, number of events
- **Average**: Average order value, average rating
- **Min/Max**: Lowest price, highest temperature
- **Median/Percentile**: P50 latency, P95 load time
- **Standard Deviation**: Variability in prices
- **Distinct Count**: Unique users, unique products

### Dimensions (Attributes)

**Definition**: Categorical or descriptive data used to slice/filter measures.

**Characteristics**:
- Categorical, date, or text
- Used for grouping
- Answer "who?", "what?", "where?", "when?"

**Examples**:
```sql
-- Dimensions
GROUP BY
    order_date,           -- Date dimension
    product_category,     -- Categorical dimension
    customer_segment,     -- Categorical dimension
    country_code         -- Geographic dimension
```

**Dimension Types**:

#### 1. Categorical Dimensions
```yaml
dimension: product_category
type: string
cardinality: low  # 10-20 unique values
values: [Electronics, Apparel, Home, Sports, Books]
```

#### 2. Date/Time Dimensions
```yaml
dimension: order_date
type: date
granularity: [day, week, month, quarter, year]
fiscal_calendar: true  # Has fiscal year variant
```

#### 3. Geographic Dimensions
```yaml
dimension: geography
type: geographic
hierarchy:
  - country
  - region
  - state
  - city
  - postal_code
```

#### 4. Hierarchical Dimensions
```yaml
dimension: organization
type: hierarchical
levels:
  - company
  - division
  - department
  - team
drill_down_enabled: true
```

### Dimension Drill Paths

**Example**: Date Dimension
```
Year: 2024
  ↓ (drill down)
Quarter: Q1 2024
  ↓
Month: March 2024
  ↓
Week: Week of March 18
  ↓
Day: March 20, 2024
  ↓
Hour: 2pm - 3pm
```

**SQL Implementation**:
```sql
SELECT
    -- Hierarchical date dimensions
    DATE_TRUNC('year', order_timestamp) AS year,
    DATE_TRUNC('quarter', order_timestamp) AS quarter,
    DATE_TRUNC('month', order_timestamp) AS month,
    DATE_TRUNC('week', order_timestamp) AS week,
    DATE_TRUNC('day', order_timestamp) AS day,

    -- Measures
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT order_id) AS order_count

FROM orders
GROUP BY 1, 2, 3, 4, 5
```

### Dimension Slicing and Dicing

**Slice**: Filter to one value of a dimension
```sql
-- Slice: Only "Electronics" category
SELECT
    order_date,
    SUM(revenue) AS revenue
FROM orders
WHERE product_category = 'Electronics'
GROUP BY order_date
```

**Dice**: Filter to multiple dimensions
```sql
-- Dice: Electronics in North America during Q1 2024
SELECT
    order_date,
    SUM(revenue) AS revenue
FROM orders
WHERE product_category = 'Electronics'
    AND region = 'North America'
    AND order_date BETWEEN '2024-01-01' AND '2024-03-31'
GROUP BY order_date
```

**Pivot**: Rotate dimensions
```sql
-- Pivot: Categories as columns instead of rows
SELECT
    order_date,
    SUM(CASE WHEN product_category = 'Electronics' THEN revenue ELSE 0 END) AS electronics_revenue,
    SUM(CASE WHEN product_category = 'Apparel' THEN revenue ELSE 0 END) AS apparel_revenue,
    SUM(CASE WHEN product_category = 'Home' THEN revenue ELSE 0 END) AS home_revenue
FROM orders
GROUP BY order_date
```

---

## Metric Versioning and Evolution

### Semantic Versioning for Metrics

Following semantic versioning principles (MAJOR.MINOR.PATCH):

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking change (definition changes fundamentally)
- **MINOR**: Enhancement (new dimension, filter, but backward compatible)
- **PATCH**: Bug fix (correcting calculation error)

**Examples**:

```yaml
# Version 1.0.0 → 1.0.1 (PATCH)
# Fixed bug in timezone handling
changes:
  - Fixed: Corrected UTC to PST conversion

# Version 1.0.1 → 1.1.0 (MINOR)
# Added new dimension
changes:
  - Added: platform dimension (web, ios, android)
  - Backward compatible: Existing queries still work

# Version 1.1.0 → 2.0.0 (MAJOR)
# Changed definition (breaking change)
changes:
  - Changed: Modified lookback window from 6 to 7 days
  - Breaking: Historical values will differ
  - Migration: Old metric available as weekly_active_users_v1
```

### Version Migration Strategy

#### 1. Parallel Running

Run both old and new versions simultaneously for transition period:

```sql
-- Both versions available
CREATE VIEW weekly_active_users AS
SELECT * FROM weekly_active_users_v2;

CREATE VIEW weekly_active_users_v1 AS
-- Legacy definition (6-day window)
SELECT
    activity_date,
    COUNT(DISTINCT user_id) AS wau
FROM events
WHERE event_timestamp >= activity_date - INTERVAL '6 days'
    AND event_timestamp < activity_date
GROUP BY activity_date;

CREATE VIEW weekly_active_users_v2 AS
-- New definition (7-day window)
SELECT
    activity_date,
    COUNT(DISTINCT user_id) AS wau
FROM events
WHERE event_timestamp >= activity_date - INTERVAL '7 days'
    AND event_timestamp < activity_date
GROUP BY activity_date;
```

#### 2. Deprecation Warnings

```sql
-- Add deprecation warning to old version
CREATE VIEW weekly_active_users_v1 AS
SELECT
    activity_date,
    wau,
    'DEPRECATED: Use weekly_active_users_v2. This version will be removed on 2024-06-30.' AS deprecation_notice
FROM weekly_active_users_v1_calc;
```

#### 3. Communication Plan

```markdown
# Metric Change Notification

**Metric**: Weekly Active Users (WAU)
**Change Type**: Breaking Change (v1.1.0 → v2.0.0)
**Effective Date**: 2024-04-01
**Deprecation Date**: 2024-06-30

## What's Changing
The lookback window is changing from 6 days to 7 days to align with
industry standard definition of "weekly".

## Impact
- Metric values will increase by ~3% on average
- All historical data has been backfilled with new calculation
- Dashboards using this metric will update automatically

## Action Required
- Review any alerts/thresholds that may need adjustment
- Update documentation/presentations with new definition
- Test downstream reports for expected changes

## Timeline
- 2024-03-15: Announcement sent
- 2024-03-20: Both versions available (v1 and v2)
- 2024-04-01: Default changes to v2
- 2024-06-30: v1 removed

## Questions?
Contact: analytics-team@company.com
Slack: #analytics-support
```

### Handling Historical Data

#### Option 1: Backfill (Recommended)

Recalculate historical data with new definition:

```sql
-- Backfill historical data with new logic
INSERT INTO weekly_active_users_v2_historical
SELECT
    activity_date,
    COUNT(DISTINCT user_id) AS wau
FROM events
WHERE event_timestamp >= '2020-01-01'  -- Backfill from start
GROUP BY activity_date;
```

**Pros**: Consistent time series, apples-to-apples comparisons
**Cons**: Computationally expensive, may not be possible for all metrics

#### Option 2: As-of Versioning

Preserve how metric was calculated at each point in time:

```sql
-- Track which version was active when
CREATE TABLE metric_history (
    metric_date DATE,
    metric_value DECIMAL,
    metric_version VARCHAR,
    calculated_at TIMESTAMP
);

-- Query shows metric as it was reported at the time
SELECT * FROM metric_history
WHERE metric_date = '2024-01-15'
    AND metric_version = '1.0.0';
```

**Pros**: Historical accuracy (what was reported)
**Cons**: Time series not comparable

#### Option 3: Append-Only with Version Column

```sql
CREATE TABLE weekly_active_users (
    activity_date DATE,
    wau INTEGER,
    metric_version VARCHAR,
    calculated_at TIMESTAMP,
    is_current BOOLEAN
);

-- Get current values
SELECT * FROM weekly_active_users WHERE is_current = TRUE;

-- Get historical as-reported values
SELECT * FROM weekly_active_users WHERE metric_version = '1.0.0';
```

---

## Calculation Logic Documentation

### Step-by-Step Calculation

Every metric should document calculation steps:

```yaml
metric_name: customer_lifetime_value_90day
display_name: Customer Lifetime Value (90-day)

calculation_steps:
  - step: 1
    description: Identify cohort of customers who signed up in target month
    sql: |
      SELECT DISTINCT user_id, DATE_TRUNC('month', signup_date) AS cohort_month
      FROM users
      WHERE signup_date >= '2024-01-01'

  - step: 2
    description: Calculate revenue per customer in 90 days after signup
    sql: |
      SELECT
          u.user_id,
          u.cohort_month,
          COALESCE(SUM(o.revenue), 0) AS revenue_90day
      FROM user_cohorts u
      LEFT JOIN orders o
          ON u.user_id = o.user_id
          AND o.order_date >= u.signup_date
          AND o.order_date < u.signup_date + INTERVAL '90 days'
      GROUP BY 1, 2

  - step: 3
    description: Average revenue across cohort
    sql: |
      SELECT
          cohort_month,
          AVG(revenue_90day) AS avg_ltv_90day,
          COUNT(*) AS cohort_size
      FROM customer_revenue
      GROUP BY 1

validation:
  - Revenue should be >= 0
  - Cohort size should match signup count
  - LTV trend should align with business changes
```

### Dependency Graph

Document which metrics depend on others:

```
revenue_per_user
    ↑
    ├── total_revenue (dependency)
    └── active_user_count (dependency)
            ↑
            └── user_activity_events (data source)
```

**Metadata**:
```yaml
metric_name: revenue_per_user
depends_on:
  metrics:
    - total_revenue
    - active_user_count
  tables:
    - prod.analytics.daily_revenue
    - prod.analytics.daily_active_users
```

### Edge Cases and Exclusions

Document all data quality decisions:

```yaml
metric_name: daily_active_users

filters:
  - condition: user_type != 'test'
    reason: Exclude internal test accounts
  - condition: user_status != 'deleted'
    reason: Exclude soft-deleted users
  - condition: event_timestamp IS NOT NULL
    reason: Data quality - events without timestamps are invalid

edge_cases:
  - case: User performs action at 23:59:59 UTC
    handling: Included in that day's count (not next day)
  - case: Duplicate events (same user_id + timestamp + event_type)
    handling: Deduplicated before counting
  - case: User in multiple segments
    handling: Counted in each segment separately
  - case: Zero active users on holiday
    handling: Valid state - do not backfill with nulls

null_handling:
  user_id: Exclude (anonymous users not counted)
  platform: Default to 'unknown' (still counted)
  country: Default to 'unknown' (still counted)
```

### Calculation Complexity Levels

**Level 1: Simple Aggregation**
```sql
-- Sum of a column
SELECT SUM(revenue) AS total_revenue FROM orders;
```

**Level 2: Filtered Aggregation**
```sql
-- Sum with conditions
SELECT SUM(revenue) AS total_revenue
FROM orders
WHERE order_status = 'completed'
    AND order_date >= '2024-01-01';
```

**Level 3: Multi-Table Join**
```sql
-- Joining multiple sources
SELECT
    SUM(o.revenue) AS total_revenue
FROM orders o
INNER JOIN users u ON o.user_id = u.user_id
WHERE u.user_type = 'premium';
```

**Level 4: Window Functions**
```sql
-- Running calculations
SELECT
    order_date,
    revenue,
    AVG(revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7day_avg
FROM daily_revenue;
```

**Level 5: Complex Business Logic**
```sql
-- Multi-step calculation with CTEs, window functions, and business rules
WITH cohorts AS (...),
     retention AS (...),
     revenue AS (...)
SELECT ... FROM cohorts
JOIN retention ... JOIN revenue ...;
```

---

## Business vs Technical Definitions

### Two-Level Definition Strategy

Every metric needs BOTH business and technical definitions.

#### Example: Monthly Recurring Revenue (MRR)

**Business Definition** (for executives, PMs, stakeholders):
```markdown
## Monthly Recurring Revenue (MRR)

**What it is**:
MRR represents the predictable revenue we expect each month from active
subscriptions. It's the heartbeat of our SaaS business health.

**Why it matters**:
- Forecasting: Predicts future revenue
- Growth tracking: Shows momentum (new vs. expansion vs. churn)
- Valuation: Key metric for company valuation (typically 8-12x MRR)

**What's included**:
- All active paid subscriptions
- Normalized to monthly amount (annual plans divided by 12)

**What's excluded**:
- One-time fees (setup, implementation)
- Usage-based charges (these are tracked separately)
- Trials and free plans

**How to interpret**:
- Healthy growth: 5-10% month-over-month
- Watch for: Churned MRR exceeding new MRR (negative growth)
- Benchmark: $100k MRR milestone typically enables Series A fundraising

**Related metrics**:
- ARR (Annual Recurring Revenue): MRR × 12
- Net MRR Churn: (Churned MRR - Expansion MRR) / Starting MRR
```

**Technical Definition** (for analysts, engineers, data scientists):
```yaml
metric_name: monthly_recurring_revenue
metric_id: mrr_001
version: 2.1.0

calculation:
  formula: SUM(subscription_mrr_amount)

  detailed_logic: |
    1. Start with all subscription records
    2. Filter to active subscriptions (status = 'active')
    3. Normalize billing amounts to monthly:
       - Monthly plans: use plan_amount as-is
       - Quarterly plans: plan_amount / 3
       - Annual plans: plan_amount / 12
    4. Sum all normalized amounts
    5. Snapshot at last day of each month

data_sources:
  primary: prod.stripe.subscriptions
  joined_tables:
    - prod.stripe.plans
    - prod.crm.accounts

sql_query: |
  SELECT
      DATE_TRUNC('month', snapshot_date) AS month,
      SUM(
          CASE
              WHEN p.billing_interval = 'month' THEN s.plan_amount
              WHEN p.billing_interval = 'quarter' THEN s.plan_amount / 3.0
              WHEN p.billing_interval = 'year' THEN s.plan_amount / 12.0
          END
      ) AS mrr
  FROM prod.stripe.subscriptions s
  INNER JOIN prod.stripe.plans p ON s.plan_id = p.plan_id
  WHERE s.status = 'active'
      AND s.snapshot_date = LAST_DAY(s.snapshot_date)
  GROUP BY 1

filters:
  - status = 'active'
  - trial_end_date IS NULL OR trial_end_date < snapshot_date
  - deleted_at IS NULL

exclusions:
  - One-time charges (charge_type != 'recurring')
  - Metered/usage-based subscriptions (plan_type != 'fixed')
  - Internal test accounts (account_type != 'test')

grain: monthly snapshot (last day of month)
update_frequency: daily
latency: 1 hour after midnight UTC

validation_rules:
  - mrr >= 0
  - mrr <= total_arr / 12 * 1.1  # Allow 10% variance
  - month_over_month_change < 50%  # Flag unusual spikes

known_limitations:
  - Pro-rated amounts for mid-month changes not reflected until month-end
  - Currency conversion uses end-of-month rates (intra-month fluctuations ignored)
  - Downgrade MRR counted immediately, but revenue may be recognized later (timing difference)
```

### When Definitions Diverge

Sometimes business and technical definitions intentionally differ:

**Example: "Active User"**

**Business Definition**:
> "A user who logged in during the period"

**Technical Definition**:
> "A user with at least one event of type ['login', 'search', 'view_product', 'add_to_cart', 'purchase'] during the period, excluding events from:
> - Test accounts (email ending in @company.com)
> - Deleted accounts (deleted_at IS NOT NULL)
> - Automated bots (user_agent matching bot patterns)
> - Events older than 90 days at query time (data retention)"

**Why they differ**:
- Business definition is simplified for communication
- Technical definition handles data quality and edge cases
- Both are correct for their audiences

**Best practice**: Document both and explain any differences.

---

## Metric Certification Process

### Three-Tier Certification System

Inspired by Airbnb's Minerva and Uber's uMetric:

#### Tier 1: Certified (Gold)

**Requirements**:
- [ ] Reviewed by data governance committee
- [ ] Validated against source system (< 1% variance)
- [ ] Complete documentation (business + technical)
- [ ] Automated data quality tests
- [ ] SLA defined and monitored
- [ ] Used in executive reporting
- [ ] Owner assigned and acknowledged

**SLA Example**:
```yaml
tier: tier_1
sla:
  freshness: "Data must be available by 8am UTC"
  accuracy: "±0.5% variance from source system"
  availability: "99.9% uptime"
  support: "2-hour response time for issues"
```

**Indicates**: Production-grade, business-critical metric

#### Tier 2: Trusted (Silver)

**Requirements**:
- [ ] Documented (may be less comprehensive)
- [ ] Spot-checked for accuracy (< 5% variance)
- [ ] Basic data quality tests
- [ ] Owner assigned
- [ ] Used by multiple teams

**SLA Example**:
```yaml
tier: tier_2
sla:
  freshness: "Data available by noon UTC"
  accuracy: "±2% variance acceptable"
  availability: "99% uptime"
  support: "24-hour response time"
```

**Indicates**: Reliable for analysis, not mission-critical

#### Tier 3: Experimental (Bronze)

**Requirements**:
- [ ] Basic documentation
- [ ] Not validated
- [ ] No SLA
- [ ] May change without notice

**Warning Label**:
```yaml
tier: tier_3
warning: |
  This metric is experimental and may change or be deprecated without notice.
  Not recommended for executive reporting or automated decision-making.
  Contact owner before using in production.
```

**Indicates**: Prototype, exploratory, or deprecated

### Certification Checklist

**For Tier 1 Certification**:

```markdown
# Metric Certification: [Metric Name]

## Documentation (20 points)
- [ ] Business definition (non-technical language)
- [ ] Technical definition (SQL + calculation logic)
- [ ] Owner identified (name + email)
- [ ] Data sources documented
- [ ] Edge cases documented
- [ ] Related metrics listed

## Validation (30 points)
- [ ] Spot-checked against source system (10 random dates)
- [ ] Variance < 1% from source
- [ ] Extreme value analysis completed (no unexpected outliers)
- [ ] Historical trend review (aligns with known business events)
- [ ] Peer review by senior analyst

## Data Quality (20 points)
- [ ] Automated tests implemented (dbt tests or equivalent)
- [ ] Null handling defined
- [ ] Duplicate prevention logic
- [ ] Late-arriving data strategy

## Governance (15 points)
- [ ] Reviewed by data governance committee
- [ ] Approved by business stakeholder
- [ ] SLA defined
- [ ] Monitoring/alerting configured

## Discoverability (15 points)
- [ ] Published in data catalog
- [ ] Tagged appropriately (domain, use case, certification tier)
- [ ] Example usage provided
- [ ] Linked to relevant dashboards

**Total Score**: ___/100 (Minimum 80 required for Tier 1)

**Certified By**: ________________
**Date**: ________________
**Next Review**: ________________ (annual review required)
```

### Annual Recertification

Tier 1 metrics must be reviewed annually:

```markdown
# Annual Recertification: [Metric Name]

**Last Certified**: 2024-03-20
**Current Review**: 2025-03-20

## Review Checklist
- [ ] Metric still relevant to business
- [ ] No changes in underlying data sources
- [ ] Calculation logic still valid
- [ ] SLA still achievable (check actual performance)
- [ ] Owner still valid (or reassign)
- [ ] Documentation up to date
- [ ] No major data quality incidents in past year

## Changes Since Last Review
- None / [List changes]

## Recommendation
- [ ] Recertify as Tier 1
- [ ] Downgrade to Tier 2 (reason: ___________)
- [ ] Deprecate (reason: ___________)

**Reviewer**: ________________
**Date**: ________________
```

---

## Slowly Changing Dimensions in Metrics

### The Problem

User attributes change over time:
- User upgrades from Free → Pro → Enterprise
- User moves from New York → San Francisco
- Product price changes from $10 → $15

**Question**: When analyzing historical data, which value do we use?

### SCD Types

#### Type 0: Retain Original

Never update - keep original value.

**Example**: User's original signup source
```sql
CREATE TABLE users (
    user_id INT,
    signup_date DATE,
    original_signup_source VARCHAR  -- Never changes
);
```

**Use case**: Attribution analysis (always use first touchpoint)

#### Type 1: Overwrite

Update in place - lose history.

**Example**: User's current email
```sql
UPDATE users
SET email = 'new_email@example.com'
WHERE user_id = 12345;
```

**Impact on metrics**:
```sql
-- All historical analysis uses current email
SELECT
    email,
    COUNT(*) AS historical_orders
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_date >= '2020-01-01'
GROUP BY email;
```

**Use case**: Corrections, current state reporting

#### Type 2: Add New Row

Keep full history with version records.

**Example**: User subscription tier
```sql
CREATE TABLE user_subscription_history (
    user_id INT,
    subscription_tier VARCHAR,
    valid_from DATE,
    valid_to DATE,      -- NULL = current
    is_current BOOLEAN
);

-- User's subscription history
-- user_id | tier       | valid_from | valid_to   | is_current
-- 12345   | Free       | 2023-01-01 | 2023-06-30 | FALSE
-- 12345   | Pro        | 2023-07-01 | 2024-01-31 | FALSE
-- 12345   | Enterprise | 2024-02-01 | NULL       | TRUE
```

**Point-in-time join**:
```sql
-- What tier was user in when they made each order?
SELECT
    o.order_date,
    o.order_id,
    sh.subscription_tier
FROM orders o
INNER JOIN user_subscription_history sh
    ON o.user_id = sh.user_id
    AND o.order_date >= sh.valid_from
    AND (o.order_date < sh.valid_to OR sh.valid_to IS NULL)
```

**Use case**: Cohort analysis, retention tracking

#### Type 3: Add New Column

Keep current + one previous value.

**Example**: User's current and previous tier
```sql
CREATE TABLE users (
    user_id INT,
    current_tier VARCHAR,
    previous_tier VARCHAR,
    tier_changed_at DATE
);
```

**Use case**: Simple before/after analysis

### Best Practices for Metrics with SCDs

#### 1. Define "As-of-When" Clearly

```yaml
metric_name: revenue_by_user_segment

dimension_timestamp_logic:
  user_segment:
    method: as_of_event  # Use segment at time of order
    # OR
    method: as_of_query  # Use current segment

  geography:
    method: as_of_event  # Use location at time of order
```

#### 2. Default to "As-of-Event" for Historical Analysis

**Example**: Retention by signup tier

```sql
-- WRONG: Uses current tier for all historical cohorts
SELECT
    DATE_TRUNC('month', u.signup_date) AS cohort_month,
    u.current_tier,  -- Current tier (Type 1 SCD)
    COUNT(DISTINCT u.user_id) AS cohort_size
FROM users u
GROUP BY 1, 2;

-- RIGHT: Uses tier at time of signup
SELECT
    DATE_TRUNC('month', u.signup_date) AS cohort_month,
    sh.subscription_tier,  -- Tier at signup (Type 2 SCD)
    COUNT(DISTINCT u.user_id) AS cohort_size
FROM users u
INNER JOIN user_subscription_history sh
    ON u.user_id = sh.user_id
    AND u.signup_date >= sh.valid_from
    AND (u.signup_date < sh.valid_to OR sh.valid_to IS NULL)
GROUP BY 1, 2;
```

#### 3. Use "As-of-Query" for Current State Reporting

**Example**: Current MRR by segment

```sql
-- Use current segment for MRR breakdown
SELECT
    u.current_tier,
    SUM(s.mrr_amount) AS total_mrr
FROM subscriptions s
INNER JOIN users u ON s.user_id = u.user_id
WHERE s.status = 'active'
GROUP BY u.current_tier;
```

---

## Metric Stores and Semantic Layers

### What is a Metric Store?

**Definition**: A centralized repository for metric definitions that acts as a single source of truth.

**Benefits**:
- **Consistency**: Everyone uses the same definition
- **Discoverability**: Searchable catalog of all metrics
- **Governance**: Controlled creation and certification process
- **Lineage**: Track metric → SQL → tables → source systems
- **Version control**: Change history and rollback

### Architecture Patterns

#### Pattern 1: dbt Semantic Layer

**How it works**: Define metrics in YAML, query via API

```yaml
# models/metrics/revenue_metrics.yml

semantic_models:
  - name: orders
    model: ref('fct_orders')
    entities:
      - name: order_id
        type: primary
      - name: user_id
        type: foreign

    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day

      - name: product_category
        type: categorical

    measures:
      - name: revenue
        agg: sum
        expr: order_total_amount_usd

      - name: order_count
        agg: count
        expr: order_id

metrics:
  - name: total_revenue
    type: simple
    label: Total Revenue (USD)
    type_params:
      measure: revenue

  - name: average_order_value
    type: ratio
    label: Average Order Value
    type_params:
      numerator: revenue
      denominator: order_count
```

**Query API**:
```python
# Query metrics via Python API
from dbt_semantic_interfaces import query

result = query.execute(
    metrics=["total_revenue", "average_order_value"],
    group_by=["order_date", "product_category"],
    where="order_date >= '2024-01-01'"
)
```

**Benefits**:
- Metrics defined in version-controlled YAML
- Automatic SQL generation
- Consistent across all BI tools
- Built-in governance (metrics must be in repo)

#### Pattern 2: Transform Metric Store

**How it works**: Centralized metric definitions with headless BI

```yaml
# transform.yaml

datasources:
  - name: analytics_db
    type: snowflake
    connection: prod

models:
  - name: orders
    sql_table: prod.analytics.fct_orders

metrics:
  - name: revenue
    type: measure
    sql: SUM(${orders.order_total_amount_usd})
    model: orders

  - name: order_count
    type: measure
    sql: COUNT(${orders.order_id})
    model: orders

  - name: average_order_value
    type: derived
    sql: ${revenue} / NULLIF(${order_count}, 0)
```

**Query via API**:
```bash
curl -X POST https://api.transform.co/mql/query \
  -d '{
    "metrics": ["revenue", "average_order_value"],
    "dimensions": ["orders.order_date"],
    "where": "orders.order_date >= '\''2024-01-01'\''"
  }'
```

#### Pattern 3: Cube.dev Semantic Layer

**How it works**: Define data model with measures and dimensions

```javascript
// cube.js

cube('Orders', {
  sql: `SELECT * FROM prod.analytics.fct_orders`,

  dimensions: {
    orderId: {
      sql: `order_id`,
      type: `string`,
      primaryKey: true
    },

    orderDate: {
      sql: `order_date`,
      type: `time`
    },

    productCategory: {
      sql: `product_category`,
      type: `string`
    }
  },

  measures: {
    count: {
      type: `count`
    },

    revenue: {
      sql: `order_total_amount_usd`,
      type: `sum`,
      format: `currency`
    },

    averageOrderValue: {
      sql: `${revenue} / NULLIF(${count}, 0)`,
      type: `number`,
      format: `currency`
    }
  }
});
```

**Query via GraphQL**:
```graphql
query {
  cube(
    measures: ["Orders.revenue", "Orders.averageOrderValue"]
    timeDimensions: [{
      dimension: "Orders.orderDate"
      granularity: "day"
    }]
  ) {
    orderDate
    revenue
    averageOrderValue
  }
}
```

### Metric Store Features Comparison

| Feature | dbt Semantic Layer | Transform | Cube.dev | LookML (Looker) |
|---------|-------------------|-----------|----------|-----------------|
| **Language** | YAML | YAML | JavaScript | LookML |
| **Version Control** | ✓ Git | ✓ Git | ✓ Git | ✓ Git |
| **Headless BI** | ✓ API | ✓ API | ✓ API | ✗ (Looker-only) |
| **Caching** | ✓ | ✓ | ✓ Advanced | ✓ |
| **Pre-aggregation** | ✓ | ✓ | ✓ Advanced | ✓ Aggregate tables |
| **Access Control** | Via dbt Cloud | ✓ | ✓ | ✓ |
| **Lineage** | ✓ | ✓ | ✓ | ✓ |
| **Open Source** | ✓ | ✗ | ✓ | ✗ |
| **Multi-BI Support** | ✓ | ✓ | ✓ | ✗ |

---

## Industry Examples

### Airbnb's Minerva

**Overview**: Centralized metric platform at Airbnb

**Key Features**:
1. **Metric Certification**: Three tiers (Gold, Silver, Bronze)
2. **Metadata**: Every metric has owner, SLA, dependencies
3. **Lineage**: Full traceability from metric → SQL → tables
4. **Discovery**: Search for metrics by name, description, tags
5. **Validation**: Automated testing against source systems

**Example Metric**:
```yaml
metric_id: minerva.core.bookings
display_name: Bookings
tier: gold
owner: data-eng@airbnb.com

business_definition: |
  Number of reservations confirmed by both guest and host.
  A booking is counted when the host accepts or instant-books.

technical_definition: |
  COUNT(DISTINCT reservation_id)
  WHERE reservation_status = 'confirmed'
  AND created_at >= analysis_start_date

dimensions:
  - market (country, region, city)
  - property_type
  - booking_channel
  - user_segment

data_sources:
  - minerva.core.reservations
  - minerva.core.users

sla:
  latency: 2_hours
  accuracy: 99.9_percent

tags:
  - core_metric
  - north_star
  - exec_dashboard
```

### Uber's uMetric

**Overview**: Uber's unified metrics platform

**Key Features**:
1. **Centralized definitions**: One definition per metric across all of Uber
2. **Automatic computation**: Metrics computed on schedule, not ad-hoc
3. **Self-service**: Non-technical users can create metric combinations
4. **Anomaly detection**: Automatic alerts for metric anomalies
5. **A/B testing integration**: Metrics auto-used in experiments

**Architecture**:
```
Data Sources → uMetric Platform → Metric Store → Consumers
                     ↓                               ↓
              [Calculation Engine]           [Dashboards]
              [Validation]                   [Notebooks]
              [Alerting]                     [A/B Platform]
                                             [ML Models]
```

**Example**:
- **Metric**: Trip completion rate
- **Owner**: Rider experience team
- **Computation**: Hourly
- **Dimensions**: City, product (UberX, Pool, etc.), time of day
- **Alerts**: <95% triggers investigation
- **Used by**: 50+ dashboards, 200+ experiments

### Netflix Experimentation Metrics

**Overview**: Standardized metrics for A/B testing

**Key Principles**:
1. **Guardrail metrics**: Must not regress (sign-ups, streaming hours)
2. **Primary metrics**: What test is optimizing for
3. **Secondary metrics**: Additional insights
4. **Heterogeneous treatment effects**: Breakdowns by segment

**Metric Example**:
```yaml
metric: session_duration
type: primary
business_question: "Does this feature increase engagement?"

calculation:
  numerator: Total streaming minutes
  denominator: Number of sessions
  unit: minutes per session

statistical_properties:
  distribution: log-normal
  outlier_threshold: 99.5_percentile
  minimum_detectable_effect: 0.5_percent
  power: 0.8

segments:
  - new_users
  - returning_users
  - heavy_users (>20 hrs/week)
  - light_users (<5 hrs/week)

guardrails:
  - sign_ups (must not decrease)
  - error_rate (must not increase)
```

---

## Anti-Patterns and Pitfalls

### Anti-Pattern 1: Vanity Metrics

**Problem**: Metrics that look impressive but don't drive decisions.

**Examples**:
- Total registered users (includes inactive, deleted)
- Total page views (includes bots, auto-refresh)
- Social media followers (bought followers)

**Better alternatives**:
- Active users (engaged in last 30 days)
- Engaged page views (>10 seconds time on page)
- Engaged followers (likes, comments, shares)

**Fix**:
```yaml
# Bad
metric: total_users
sql: COUNT(*) FROM users

# Good
metric: monthly_active_users
sql: |
  COUNT(DISTINCT user_id)
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - 30
  AND user_type != 'test'
  AND event_type IN ('login', 'core_action')
```

### Anti-Pattern 2: Metric Proliferation

**Problem**: Creating too many similar metrics.

**Symptoms**:
- 10+ versions of "revenue" (revenue, net revenue, gross revenue, adjusted revenue, ...)
- No one knows which to use
- Impossible to maintain

**Fix**:
1. **Audit existing metrics**: Identify duplicates
2. **Consolidate**: Choose one canonical definition
3. **Deprecate others**: Remove after migration period
4. **Governance**: Require approval for new metrics

**Example**:
```markdown
# Before: 8 revenue metrics
- revenue
- net_revenue
- gross_revenue
- adjusted_revenue
- revenue_usd
- total_revenue
- revenue_excl_tax
- revenue_incl_shipping

# After: 2 revenue metrics + dimensions
- gross_revenue (before tax, shipping)
  - Dimensions: currency, include_shipping (yes/no), include_tax (yes/no)
- net_revenue (after refunds, discounts)
```

### Anti-Pattern 3: Non-Additive Metric Summation

**Problem**: Summing metrics that shouldn't be summed.

**Examples**:

**BAD - Summing averages**:
```sql
-- WRONG
SELECT SUM(daily_avg_order_value) FROM daily_metrics;
```

**Good - Recalculate from components**:
```sql
-- RIGHT
SELECT SUM(revenue) / SUM(order_count) AS avg_order_value
FROM daily_metrics;
```

**BAD - Summing ratios**:
```sql
-- WRONG
SELECT SUM(daily_conversion_rate) FROM daily_metrics;
```

**Good - Calculate from totals**:
```sql
-- RIGHT
SELECT
    SUM(conversions)::FLOAT / SUM(visitors) AS overall_conversion_rate
FROM daily_metrics;
```

### Anti-Pattern 4: Ignoring Seasonality

**Problem**: Comparing metrics without accounting for seasonality.

**Example**:
```
"Revenue is down 30% vs. last month!"
(Comparing December to January - holiday vs. post-holiday)
```

**Fix**: Compare to same period last year or use seasonally-adjusted metrics

```sql
-- Better comparisons
SELECT
    current_month_revenue,
    prior_month_revenue,
    same_month_last_year_revenue,

    -- Month-over-month (beware seasonality)
    (current_month_revenue - prior_month_revenue) / prior_month_revenue AS mom_change,

    -- Year-over-year (accounts for seasonality)
    (current_month_revenue - same_month_last_year_revenue) / same_month_last_year_revenue AS yoy_change
FROM revenue_comparison;
```

### Anti-Pattern 5: Hardcoded Date Filters

**Problem**: Queries with hardcoded dates break over time.

**BAD**:
```sql
WHERE order_date >= '2024-01-01'  -- Will be outdated
```

**Good**:
```sql
-- Relative date ranges
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)
WHERE order_date >= DATE_TRUNC('year', CURRENT_DATE)
```

### Anti-Pattern 6: Mixing Grains

**Problem**: Joining data at different grains without aggregation.

**Example**:
```sql
-- WRONG: User-level table joined to order-level table
SELECT
    u.user_id,
    u.signup_date,
    o.order_id,           -- Multiple rows per user!
    u.total_orders        -- This will be duplicated
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id;
```

**Fix**: Aggregate to matching grain
```sql
-- RIGHT: Aggregate orders to user level first
WITH user_orders AS (
    SELECT
        user_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
)
SELECT
    u.user_id,
    u.signup_date,
    uo.order_count
FROM users u
LEFT JOIN user_orders uo ON u.user_id = uo.user_id;
```

### Anti-Pattern 7: No Null Handling

**Problem**: Failing to handle nulls leads to incorrect calculations.

**Examples**:

**Division by zero**:
```sql
-- BAD
SELECT revenue / order_count AS avg_order_value;  -- Error if order_count = 0

-- GOOD
SELECT revenue / NULLIF(order_count, 0) AS avg_order_value;
```

**Null in aggregation**:
```sql
-- Nulls are ignored in aggregations (may or may not be desired)
SELECT AVG(session_duration) FROM events;  -- Excludes null durations

-- Be explicit
SELECT AVG(COALESCE(session_duration, 0)) FROM events;  -- Treats null as 0
```

### Anti-Pattern 8: Premature Optimization

**Problem**: Overly complex metrics before understanding need.

**Example**:
```sql
-- Overly complex before anyone asks for it
SELECT
    user_id,
    -- 50 different window functions
    SUM(...) OVER (...),
    AVG(...) OVER (...),
    -- 20 different aggregations
    -- 30 dimensions
FROM ...;
```

**Fix**: Start simple, add complexity as needed
```sql
-- Start here
SELECT
    user_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY user_id;

-- Add complexity only when requested
```

### Anti-Pattern 9: Unclear Ownership

**Problem**: No one responsible when metric breaks.

**Symptom**:
```
Slack: "@channel The revenue metric looks wrong"
Response: "I don't own that"
Response: "Not my table"
Response: "I just inherited this"
```

**Fix**:
```yaml
# Every metric must have owner
metric: revenue
owner:
  team: finance_analytics
  primary_contact: jane.smith@company.com
  backup_contact: analytics-team@company.com
  slack_channel: "#analytics-finance"

escalation:
  - After 2 hours: Page on-call analyst
  - After 4 hours: Page director of analytics
```

### Anti-Pattern 10: No Validation

**Problem**: Metrics go into production without validation.

**Fix**: Implement validation at multiple levels

```sql
-- Level 1: Range checks
SELECT *
FROM daily_metrics
WHERE daily_active_users < 0  -- Should never be negative
   OR daily_active_users > 10000000;  -- Unrealistically high

-- Level 2: Trend checks
SELECT *
FROM (
    SELECT
        metric_date,
        daily_active_users,
        LAG(daily_active_users) OVER (ORDER BY metric_date) AS prior_day_dau,
        (daily_active_users - LAG(daily_active_users) OVER (ORDER BY metric_date))
            / LAG(daily_active_users) OVER (ORDER BY metric_date) AS pct_change
    FROM daily_metrics
)
WHERE ABS(pct_change) > 0.5;  -- Flag >50% day-over-day change

-- Level 3: Reconciliation with source
SELECT
    dbt.metric_date,
    dbt.total_revenue AS dbt_revenue,
    src.total_revenue AS source_revenue,
    ABS(dbt.total_revenue - src.total_revenue) / src.total_revenue AS variance_pct
FROM dbt_metrics dbt
INNER JOIN source_system src USING (metric_date)
WHERE variance_pct > 0.01;  -- Flag >1% variance
```

---

## Appendix: Metric Documentation Template

### Complete Metric Documentation

```yaml
################################################################################
# METRIC METADATA
################################################################################

metric_id: mrr_001
metric_name: monthly_recurring_revenue
display_name: Monthly Recurring Revenue (MRR)
version: 2.1.0
status: active  # active | deprecated | experimental
tier: tier_1    # tier_1 (certified) | tier_2 (trusted) | tier_3 (experimental)

created_date: 2024-01-15
last_modified: 2024-03-20
deprecated_date: null
scheduled_deprecation: null

################################################################################
# OWNERSHIP
################################################################################

owner:
  team: finance_analytics
  primary_contact: jane.smith@company.com
  backup_contact: analytics-team@company.com
  slack_channel: "#analytics-finance"

stakeholders:
  - CFO
  - VP Finance
  - Revenue Operations

################################################################################
# BUSINESS DEFINITION
################################################################################

business_definition: |
  Monthly Recurring Revenue (MRR) represents the predictable, recurring revenue
  generated from active subscriptions, normalized to a monthly amount.

  MRR is the primary metric for tracking SaaS business health and growth.
  It excludes one-time charges and usage-based fees.

why_it_matters: |
  - Forecasting: Predicts future revenue with high accuracy
  - Growth tracking: Shows momentum via New, Expansion, Churned MRR
  - Valuation: Key metric for company valuation (8-12x MRR multiple)
  - Resource planning: Informs hiring and investment decisions

interpretation_guide: |
  - Healthy growth: 5-10% month-over-month MRR growth
  - Watch for: Churned MRR exceeding New MRR (negative net growth)
  - Benchmark: $100k MRR enables Series A; $1M enables Series B

################################################################################
# TECHNICAL DEFINITION
################################################################################

calculation:
  type: sum
  formula: SUM(subscription_mrr_amount)

  detailed_steps:
    - step: 1
      description: Filter to active subscriptions
      sql: WHERE status = 'active' AND trial_end_date < snapshot_date

    - step: 2
      description: Normalize billing amounts to monthly
      sql: |
        CASE
          WHEN billing_interval = 'month' THEN plan_amount
          WHEN billing_interval = 'quarter' THEN plan_amount / 3.0
          WHEN billing_interval = 'year' THEN plan_amount / 12.0
        END

    - step: 3
      description: Sum all normalized amounts
      sql: SUM(normalized_amount)

    - step: 4
      description: Snapshot at month-end
      sql: WHERE snapshot_date = LAST_DAY_OF_MONTH(snapshot_date)

sql_query: |
  SELECT
      DATE_TRUNC('month', snapshot_date) AS month,
      SUM(
          CASE
              WHEN p.billing_interval = 'month' THEN s.plan_amount
              WHEN p.billing_interval = 'quarter' THEN s.plan_amount / 3.0
              WHEN p.billing_interval = 'year' THEN s.plan_amount / 12.0
          END
      ) AS mrr
  FROM {{ ref('subscriptions') }} s
  INNER JOIN {{ ref('plans') }} p ON s.plan_id = p.plan_id
  WHERE s.status = 'active'
      AND (s.trial_end_date IS NULL OR s.trial_end_date < s.snapshot_date)
      AND s.deleted_at IS NULL
      AND s.snapshot_date = LAST_DAY_OF_MONTH(s.snapshot_date)
  GROUP BY 1

################################################################################
# DATA SOURCES
################################################################################

data_sources:
  primary_table: prod.stripe.subscriptions
  joined_tables:
    - prod.stripe.plans
    - prod.crm.accounts

  dependencies:
    metrics: []
    models:
      - ref('subscriptions')
      - ref('plans')

grain: monthly (snapshot at last day of month)
update_frequency: daily at 2am UTC
data_latency: 1 hour after midnight

################################################################################
# DIMENSIONS
################################################################################

dimensions:
  - name: subscription_tier
    type: categorical
    cardinality: low
    values: [starter, professional, enterprise]

  - name: billing_interval
    type: categorical
    values: [monthly, quarterly, annual]

  - name: customer_segment
    type: categorical
    values: [smb, mid_market, enterprise]

  - name: geography
    type: geographic
    hierarchy: [country, region]

################################################################################
# FILTERS & EXCLUSIONS
################################################################################

filters:
  - condition: status = 'active'
    reason: Only active subscriptions count toward MRR

  - condition: trial_end_date IS NULL OR trial_end_date < snapshot_date
    reason: Exclude active trials (not yet paying)

  - condition: deleted_at IS NULL
    reason: Exclude soft-deleted subscriptions

exclusions:
  - One-time charges (charge_type != 'recurring')
  - Usage-based charges (plan_type = 'metered')
  - Internal test accounts (account_type = 'test')
  - Accounts with $0 plan amount

edge_cases:
  - case: Mid-month subscription start
    handling: Included at full monthly amount (no proration for MRR metric)

  - case: Mid-month cancellation
    handling: Excluded from month-end snapshot (MRR measures only active)

  - case: Plan change mid-month
    handling: Month-end snapshot reflects final plan amount

  - case: Multiple subscriptions per customer
    handling: Each subscription counted separately

null_handling:
  plan_amount: Must not be null (validation rule)
  billing_interval: Must not be null (validation rule)
  snapshot_date: Must not be null (validation rule)

################################################################################
# VALIDATION & QUALITY
################################################################################

validation_rules:
  - rule: mrr >= 0
    severity: critical

  - rule: mrr <= total_arr / 12 * 1.1
    severity: warning
    note: Allow 10% variance due to timing

  - rule: month_over_month_change < 0.5
    severity: warning
    note: Flag unusual spikes (>50% change)

  - rule: mrr / active_subscription_count BETWEEN 10 AND 10000
    severity: warning
    note: Sanity check on average subscription value

data_quality_tests:
  - not_null: [month, mrr]
  - unique: [month]
  - accepted_range:
      field: mrr
      min: 0
      max: 100000000
  - reconciliation:
      source: stripe.monthly_reports
      tolerance: 0.01  # 1%

known_limitations:
  - Pro-rated amounts for mid-month changes not reflected until month-end
  - Currency conversion uses end-of-month rates (intra-month volatility ignored)
  - Downgrade MRR counted immediately, revenue may be recognized over time

################################################################################
# SLA & MONITORING
################################################################################

sla:
  freshness: Data available by 8am UTC
  accuracy: ±0.5% variance from Stripe reporting
  availability: 99.9% uptime
  support_response: 2 hours for Tier 1 incidents

monitoring:
  alerts:
    - condition: Data not updated by 10am UTC
      severity: critical
      channel: pagerduty

    - condition: Month-over-month change > 50%
      severity: warning
      channel: slack

    - condition: Variance from Stripe > 1%
      severity: warning
      channel: email

################################################################################
# VERSIONING
################################################################################

changelog:
  - version: 2.1.0
    date: 2024-03-20
    type: minor
    changes:
      - Added geography dimension
      - Improved currency conversion logic
    migration: Automatic (backward compatible)

  - version: 2.0.0
    date: 2024-02-15
    type: major
    changes:
      - Changed trial exclusion logic
      - Added soft-delete filter
    migration: Historical backfill completed
    breaking: true

  - version: 1.0.0
    date: 2024-01-15
    type: initial
    changes:
      - Initial metric definition

previous_versions:
  - name: monthly_recurring_revenue_v1
    available_until: 2024-06-30
    deprecation_reason: Updated trial handling logic

################################################################################
# DISCOVERABILITY
################################################################################

tags:
  - revenue
  - kpi
  - saas
  - executive_dashboard
  - board_metrics

related_metrics:
  - arr (Annual Recurring Revenue)
  - new_mrr (New MRR from new subscriptions)
  - expansion_mrr (MRR increase from upgrades)
  - churned_mrr (MRR lost from cancellations)
  - net_mrr_churn_rate

documentation_links:
  - https://wiki.company.com/metrics/mrr
  - https://wiki.company.com/saas-metrics-guide

dashboard_links:
  - https://tableau.company.com/executive-dashboard
  - https://mode.company.com/saas-metrics

example_usage: |
  # Get MRR trend
  SELECT month, mrr
  FROM {{ ref('mrr_monthly') }}
  WHERE month >= '2023-01-01'
  ORDER BY month;

  # MRR by tier
  SELECT subscription_tier, SUM(mrr) AS total_mrr
  FROM {{ ref('mrr_monthly') }}
  WHERE month = LAST_MONTH()
  GROUP BY subscription_tier;

################################################################################
# CERTIFICATION
################################################################################

certification:
  certified_by: jane.smith@company.com
  certification_date: 2024-03-01
  reviewed_by: data_governance_committee
  next_review_date: 2025-03-01

  validation_results:
    variance_from_source: 0.3%  # < 1% threshold
    data_quality_score: 98/100
    documentation_completeness: 100%
```

---

## Further Reading

### Books & Papers
- **"Lean Analytics"** - Alistair Croll & Benjamin Yoskovitz (metric selection)
- **"Measure What Matters"** - John Doerr (OKRs and goal metrics)
- **"Data Quality: The Accuracy Dimension"** - Jack E. Olson
- **"The Data Warehouse Toolkit"** - Ralph Kimball (dimensions and measures)

### Industry Resources
- **Locally Optimistic**: Analytics engineering blog (metric stores)
- **dbt Blog**: Metric definition best practices
- **Uber Engineering Blog**: uMetric platform architecture
- **Airbnb Data Blog**: Minerva and data quality
- **Netflix Tech Blog**: Experimentation metrics

### Communities
- **dbt Slack**: #metrics-layer channel
- **Locally Optimistic Slack**: Metric discussions
- **Data Council**: Conference talks on metric platforms
