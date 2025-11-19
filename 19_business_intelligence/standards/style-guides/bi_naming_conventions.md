# BI Naming Conventions

## Overview

This guide establishes naming standards for all Business Intelligence objects to ensure consistency, discoverability, and maintainability across the data stack.

**Key References:**
- dbt Labs Style Guide
- GitLab Data Team Handbook
- Brooklyn Data Co. SQL Style Guide
- Fishtown Analytics Engineering Best Practices

---

## Table of Contents

1. [Table Naming Conventions](#table-naming-conventions)
2. [Column Naming Patterns](#column-naming-patterns)
3. [Dashboard and Report Naming](#dashboard-and-report-naming)
4. [Metric Naming Standards](#metric-naming-standards)
5. [dbt Model Naming Conventions](#dbt-model-naming-conventions)
6. [File and Folder Organization](#file-and-folder-organization)
7. [Consistency Across BI Stack](#consistency-across-bi-stack)

---

## Table Naming Conventions

### General Principles

```yaml
Format: [layer]_[source]__[entity][_descriptor]

Rules:
  - Use snake_case (all lowercase, underscore separators)
  - Be descriptive but concise
  - Use plural for fact tables (orders, events)
  - Use singular for dimension tables (customer, product)
  - Prefix with layer designation
  - Use double underscore (__) to separate source from entity
```

### Layer Prefixes

#### Raw/Source Layer

**Pattern**: `raw_[source_system]_[object]` or `[source].[schema].[table]`

```sql
-- Fivetran/Stitch synced tables
raw.salesforce.account
raw.salesforce.opportunity
raw.stripe.invoice
raw.stripe.subscription
raw.segment.tracks
raw.segment.identifies

-- Alternative pattern (single database)
raw_salesforce_account
raw_stripe_invoice
raw_segment_tracks
```

**Best Practices:**
- Never query raw tables directly in dashboards
- Document sync method (Fivetran, Airbyte, custom)
- Include sync timestamp columns

#### Staging Layer

**Pattern**: `stg_[source]__[entity]`

```sql
-- Staging models (light transformation)
staging.stg_salesforce__accounts
staging.stg_salesforce__opportunities
staging.stg_stripe__invoices
staging.stg_stripe__subscriptions
staging.stg_segment__events
staging.stg_ga4__sessions

-- For single-source entities, source prefix optional
staging.stg_customers  (if only one customer source)
```

**Purpose:**
- Rename columns to standard naming
- Basic type casting
- Minimal business logic
- Deduplication
- Timezone normalization

**Example:**

```sql
-- models/staging/salesforce/stg_salesforce__accounts.sql

SELECT
    -- Primary key
    id AS account_id,
    
    -- Attributes (renamed to snake_case)
    name AS account_name,
    type AS account_type,
    industry AS industry_vertical,
    
    -- Timestamps (converted to UTC)
    createddate AS created_at_utc,
    systemmodstamp AS updated_at_utc,
    
    -- Metadata
    isdeleted AS is_deleted

FROM {{ source('salesforce', 'account') }}
WHERE isdeleted = FALSE
```

#### Intermediate Layer

**Pattern**: `int_[entity]_[transformation]`

```sql
-- Intermediate models (complex logic, not exposed)
intermediate.int_orders_enriched
intermediate.int_customer_lifecycle_stages
intermediate.int_revenue_allocations
intermediate.int_subscription_events
intermediate.int_user_cohorts_daily

-- Join tables
intermediate.int_orders_joined
intermediate.int_customers_enhanced
```

**Purpose:**
- Complex business logic
- Joins across multiple sources
- Calculated fields
- Not exposed to end users

#### Marts Layer (Analytics/Dimensional)

**Fact Tables** - `fct_[plural_entity]`

```sql
analytics.fct_orders
analytics.fct_subscriptions
analytics.fct_events
analytics.fct_transactions
analytics.fct_page_views
analytics.fct_support_tickets
```

**Dimension Tables** - `dim_[singular_entity]`

```sql
analytics.dim_customer
analytics.dim_product
analytics.dim_date
analytics.dim_geography
analytics.dim_account
analytics.dim_user
```

**Aggregate Tables** - `agg_[entity]_[grain]`

```sql
analytics.agg_daily_revenue
analytics.agg_monthly_mrr
analytics.agg_hourly_events
analytics.agg_weekly_retention
```

**Wide Marts** - `mart_[use_case]`

```sql
analytics.mart_customer_360
analytics.mart_product_analytics
analytics.mart_revenue_recognition
analytics.mart_executive_metrics
```

### Dimensional Modeling Patterns

#### Fact Table Naming

```sql
-- Transaction facts (event-based)
fct_orders           -- One row per order
fct_payments         -- One row per payment
fct_clicks           -- One row per click event

-- Periodic snapshot facts (point-in-time)
fct_inventory_daily  -- Daily inventory snapshot
fct_account_balance_monthly

-- Accumulating snapshot facts (process-based)
fct_order_fulfillment  -- Tracks order through lifecycle
```

#### Dimension Table Naming

```sql
-- Conformed dimensions (shared across facts)
dim_customer
dim_product
dim_date
dim_geography

-- Role-playing dimensions
dim_date AS order_date
dim_date AS ship_date
dim_date AS delivery_date

-- Junk dimensions (miscellaneous flags)
dim_order_flags
dim_transaction_indicators

-- Degenerate dimensions (stored in fact)
-- No separate table, just column in fact: order_number
```

#### Slowly Changing Dimensions

```sql
-- Type 1 (overwrite - no history)
dim_customer  -- current values only

-- Type 2 (add row - full history)
dim_customer_history
  - customer_key (surrogate key)
  - customer_id (natural key)
  - valid_from_date
  - valid_to_date
  - is_current

-- Type 3 (add column - limited history)
dim_customer
  - current_tier
  - previous_tier
  - tier_changed_at
```

### Special Purpose Tables

```sql
-- Snapshots
snapshot.orders_snapshot_daily
snapshot.customers_snapshot_monthly

-- Audit/Logging
audit.dbt_run_log
audit.data_quality_checks
audit.refresh_history

-- Reference/Seed Data
seed.country_codes
seed.industry_categories
seed.fiscal_calendar
seed.exchange_rates

-- Temporary/Staging Work
temp.tmp_revenue_calc
temp.tmp_dedup_work
work.wip_new_customer_model
```

---

## Column Naming Patterns

### General Rules

```yaml
Format: [entity_]descriptor[_qualifier][_unit]

Rules:
  - Use snake_case
  - Be explicit and descriptive
  - Include units where applicable
  - Use standard suffixes for types
  - Avoid abbreviations unless very common
```

### Primary and Foreign Keys

```sql
-- Primary keys: [entity]_id or [entity]_key
customer_id
order_id
product_id
transaction_id

-- Surrogate keys (Type 2 SCD)
customer_key  -- Auto-incrementing
customer_id   -- Natural business key

-- Foreign keys: Same as referenced table
customer_id   -- FK to dim_customer.customer_id
product_id    -- FK to dim_product.product_id

-- Composite keys
order_id, order_line_number
```

### Timestamps and Dates

```sql
-- Timestamps: [event]_at or [event]_timestamp
created_at
updated_at
deleted_at
order_placed_at
subscription_started_at
last_login_at

-- Dates: [event]_date
order_date
signup_date
first_purchase_date
subscription_end_date

-- Time components
order_hour
order_day_of_week
order_month
order_fiscal_quarter
order_year

-- Avoid ambiguous names
❌ date, timestamp, time
✅ order_date, created_at, event_timestamp
```

### Boolean Flags

```sql
-- Prefix with is_, has_, was_, should_
is_active
is_deleted
is_trial
has_subscription
has_mobile_app
was_churned
should_send_email

-- Avoid ambiguous names
❌ active (could be verb)
❌ deleted (could be past tense verb)
✅ is_active
✅ is_deleted
```

### Counts and Quantities

```sql
-- Suffix with _count
order_count
customer_count
event_count
page_view_count
items_per_order_count

-- Avoid ambiguous names
❌ orders (could be table reference)
❌ customers (plural is confusing)
✅ order_count
✅ customer_count
```

### Monetary Values

```sql
-- Include currency code and units
order_total_usd
revenue_usd
monthly_recurring_revenue_usd
customer_lifetime_value_usd

-- For multi-currency scenarios
order_total_local
order_total_local_currency_code
order_total_usd  -- Converted to USD

-- Avoid ambiguous names
❌ amount, total, revenue (what currency?)
✅ order_total_usd
✅ revenue_usd
```

### Percentages and Rates

```sql
-- Suffix with _rate or _pct or _percent
conversion_rate          -- 0.15 (decimal)
conversion_pct           -- 15.0 (percentage)
churn_rate
growth_rate
click_through_rate
discount_percent

-- Be consistent across organization
-- Choose either _rate or _pct, not both
```

### Measurements and Units

```sql
-- Always include unit
duration_seconds
duration_minutes
session_length_seconds
distance_miles
distance_kilometers
weight_pounds
weight_kg
temperature_fahrenheit
temperature_celsius

-- Avoid ambiguous names
❌ duration (seconds? minutes?)
❌ distance (miles? km?)
✅ duration_seconds
✅ distance_miles
```

### Calculated/Derived Fields

```sql
-- Descriptive names indicating calculation
days_since_last_order
months_since_signup
customer_tenure_days
order_recency_days

-- Running totals
running_total_revenue
cumulative_orders
year_to_date_revenue

-- Aggregations
avg_order_value
total_revenue_by_customer
max_order_amount
```

### Categorical Fields

```sql
-- Singular, descriptive names
customer_segment  -- not customer_segments
product_category
order_status
subscription_tier
user_role
country_code

-- Enumerations should be documented
order_status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')
```

### Address and Location Fields

```sql
-- Be specific about components
billing_address_line_1
billing_address_line_2
billing_city
billing_state_code
billing_postal_code
billing_country_code

shipping_address_line_1
shipping_city
shipping_state_code

-- Geo coordinates
latitude_decimal
longitude_decimal
geohash
```

### Personal Information (PII)

```sql
-- Prefix with pii_ if contains sensitive data
pii_email
pii_phone_number
pii_ssn_last_four
pii_full_name

-- Hash/encrypt in non-prod
pii_email_hashed
pii_phone_number_encrypted

-- Track PII for compliance
column metadata:
  contains_pii: true
  pii_type: email
  gdpr_applicable: true
```

---

## Dashboard and Report Naming

### Dashboard Naming Convention

**Format**: `[Department] - [Subject] - [Type/Granularity]`

```
Examples:

Executive Dashboards:
- Executive - Company Overview - KPI Summary
- Executive - Financial Performance - Monthly
- Executive - Sales & Marketing - Weekly Snapshot

Departmental Dashboards:
- Sales - Pipeline Analysis - Real-time
- Sales - Revenue Performance - Regional Breakdown
- Marketing - Campaign Attribution - Multi-touch
- Marketing - Acquisition Funnel - Weekly Cohorts
- Finance - P&L Statement - Monthly Reporting
- Finance - Cash Flow - Daily Monitoring
- Product - Usage Analytics - Feature Adoption
- Product - Experimentation - A/B Test Results
- Operations - Inventory Levels - Real-time
- Operations - Supply Chain - Daily Performance
- Customer Success - Health Score - Account View
- Customer Success - Churn Risk - Predictive

Analytical/Ad-hoc:
- Analytics - Customer Segmentation - RFM Analysis
- Analytics - Cohort Retention - Monthly Cohorts
- Data Quality - Pipeline Monitoring - dbt Tests
- Data Quality - Source System Health - SLA Tracking
```

### Report Naming Convention

**Format**: `[Type]_[Subject]_[Frequency]_[YYYYMMDD]`

```
Scheduled Reports:
- report_executive_summary_weekly_20240115.pdf
- report_sales_performance_monthly_202401.xlsx
- report_marketing_roi_quarterly_2024Q1.pdf

Automated Emails:
- email_daily_revenue_summary
- email_weekly_product_metrics
- email_monthly_customer_churn

Exports:
- export_customer_list_20240115.csv
- export_transaction_history_202401.csv
- export_product_catalog_20240115.xlsx
```

### Folder Organization

```
dashboards/
  executive/
    - Executive - Company KPIs - Daily.twb
    - Executive - Board Metrics - Monthly.twb
  sales/
    - Sales - Pipeline - Real-time.twb
    - Sales - Performance - Regional.twb
  marketing/
    - Marketing - Attribution - Multi-touch.twb
  finance/
    - Finance - Revenue Recognition - Monthly.twb
  deprecated/
    - [Archive old dashboards here with sunset dates]
```

---

## Metric Naming Standards

### Metric Naming Pattern

**Format**: `[aggregation]_[entity]_[timeframe]_[unit]`

```sql
-- Examples:
total_revenue_usd
total_orders_count
avg_order_value_usd
median_session_duration_seconds

daily_active_users
monthly_active_users
weekly_retention_rate

cumulative_revenue_usd
year_to_date_sales_usd
month_to_date_orders_count
```

### Common Metric Patterns

#### Revenue Metrics

```sql
-- Basic revenue
total_revenue_usd
net_revenue_usd  -- After refunds/discounts
gross_revenue_usd  -- Before refunds/discounts

-- Subscription metrics
monthly_recurring_revenue_usd  -- MRR
annual_recurring_revenue_usd   -- ARR
average_revenue_per_user_usd   -- ARPU
average_revenue_per_account_usd  -- ARPA

-- Growth metrics
new_mrr_usd
expansion_mrr_usd
churned_mrr_usd
contraction_mrr_usd
net_new_mrr_usd
```

#### Customer Metrics

```sql
-- Counts
total_customers_count
new_customers_count
active_customers_count
churned_customers_count

-- Lifetime value
customer_lifetime_value_usd  -- LTV or CLV
customer_lifetime_value_90day_usd
customer_lifetime_value_365day_usd

-- Acquisition
customer_acquisition_cost_usd  -- CAC
ltv_to_cac_ratio
payback_period_months
```

#### Engagement Metrics

```sql
-- Active users
daily_active_users  -- DAU
weekly_active_users  -- WAU
monthly_active_users  -- MAU

-- Stickiness
stickiness_ratio  -- DAU/MAU
engagement_rate
avg_sessions_per_user
avg_session_duration_seconds
```

#### Retention Metrics

```sql
-- Rates
retention_rate_day_7
retention_rate_day_30
retention_rate_month_1
retention_rate_month_6

churn_rate_monthly
churn_rate_annual

-- Revenue retention
gross_revenue_retention_rate  -- GRR
net_revenue_retention_rate    -- NRR
```

#### Conversion Metrics

```sql
-- Funnel conversions
visitor_to_signup_conversion_rate
signup_to_activation_conversion_rate
trial_to_paid_conversion_rate
free_to_paid_conversion_rate

-- E-commerce
cart_abandonment_rate
checkout_completion_rate
```

### Metric Abbreviations (Use Sparingly)

```sql
-- Common abbreviations (acceptable)
mrr  -- Monthly Recurring Revenue
arr  -- Annual Recurring Revenue
ltv  -- Lifetime Value
cac  -- Customer Acquisition Cost
arpu -- Average Revenue Per User
dau  -- Daily Active Users
mau  -- Monthly Active Users

-- Define all abbreviations in documentation
-- Always provide full name in dashboard titles
```

---

## dbt Model Naming Conventions

### dbt Project Structure

```
models/
├── staging/
│   ├── salesforce/
│   │   ├── _salesforce__models.yml
│   │   ├── _salesforce__sources.yml
│   │   ├── stg_salesforce__accounts.sql
│   │   ├── stg_salesforce__opportunities.sql
│   │   └── stg_salesforce__users.sql
│   ├── stripe/
│   │   ├── _stripe__models.yml
│   │   ├── _stripe__sources.yml
│   │   ├── stg_stripe__invoices.sql
│   │   └── stg_stripe__subscriptions.sql
│   └── segment/
│       ├── _segment__models.yml
│       ├── _segment__sources.yml
│       └── stg_segment__events.sql
├── intermediate/
│   ├── finance/
│   │   ├── _int_finance__models.yml
│   │   ├── int_revenue_daily.sql
│   │   └── int_subscription_events.sql
│   └── marketing/
│       ├── _int_marketing__models.yml
│       └── int_campaign_attribution.sql
├── marts/
│   ├── finance/
│   │   ├── _finance__models.yml
│   │   ├── fct_orders.sql
│   │   ├── dim_customer.sql
│   │   └── mart_revenue_dashboard.sql
│   └── marketing/
│       ├── _marketing__models.yml
│       ├── fct_campaigns.sql
│       └── mart_acquisition_metrics.sql
└── metrics/
    ├── revenue_metrics.yml
    └── customer_metrics.yml
```

### Model File Naming

```sql
-- Staging models
stg_[source]__[entity].sql
  stg_salesforce__accounts.sql
  stg_stripe__invoices.sql

-- Intermediate models
int_[entity]_[description].sql
  int_orders_enriched.sql
  int_customers_joined.sql
  int_subscription_events.sql

-- Fact tables
fct_[entity_plural].sql
  fct_orders.sql
  fct_events.sql
  fct_subscriptions.sql

-- Dimension tables
dim_[entity_singular].sql
  dim_customer.sql
  dim_product.sql
  dim_date.sql

-- Aggregate tables
agg_[grain]_[entity].sql
  agg_daily_revenue.sql
  agg_monthly_cohorts.sql

-- Wide marts
mart_[use_case].sql
  mart_customer_360.sql
  mart_executive_metrics.sql
```

### Schema File Naming

```yaml
-- Pattern: _[folder/source]__models.yml

staging/salesforce/_salesforce__models.yml
staging/salesforce/_salesforce__sources.yml
intermediate/finance/_int_finance__models.yml
marts/finance/_finance__models.yml

-- Underscore prefix ensures alphabetical sorting puts
-- schema files at top of directory
```

### Macro Naming

```sql
-- Pattern: [action]_[object].sql

-- Date macros
get_fiscal_year.sql
get_date_spine.sql
get_quarter_start.sql

-- Aggregation macros
calculate_retention_rate.sql
pivot_metric_by_dimension.sql

-- Utility macros
safe_divide.sql
cents_to_dollars.sql
remove_pii.sql
```

### Test Naming

```sql
-- Generic tests (in tests/generic/)
test_not_null_where.sql
test_valid_email_format.sql
test_future_date_not_allowed.sql

-- Singular tests (in tests/)
assert_revenue_reconciliation.sql
assert_unique_customer_emails.sql
assert_orders_have_valid_status.sql
```

---

## File and Folder Organization

### Repository Structure

```
analytics-repo/
├── models/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── metrics/
├── macros/
│   ├── date/
│   ├── aggregation/
│   └── utility/
├── tests/
│   ├── generic/
│   └── singular/
├── seeds/
│   ├── reference_data/
│   └── mappings/
├── snapshots/
├── analyses/
│   ├── ad_hoc/
│   └── investigations/
├── docs/
│   ├── metrics/
│   ├── dashboards/
│   └── guides/
└── dbt_project.yml
```

### Naming Conventions Summary

```yaml
# Quick Reference

Tables:
  raw: raw_[source]_[object]
  staging: stg_[source]__[entity]
  intermediate: int_[entity]_[desc]
  fact: fct_[entity_plural]
  dimension: dim_[entity_singular]
  aggregate: agg_[grain]_[entity]
  mart: mart_[use_case]

Columns:
  primary_key: [entity]_id
  foreign_key: [entity]_id
  timestamp: [event]_at
  date: [event]_date
  boolean: is_[state] / has_[attribute]
  count: [entity]_count
  monetary: [desc]_[currency]
  rate: [metric]_rate
  measurement: [desc]_[unit]

Dashboards:
  format: "[Dept] - [Subject] - [Type]"
  
Metrics:
  format: "[agg]_[entity]_[time]_[unit]"
  
Files:
  models: [prefix]_[source]__[entity].sql
  schemas: _[folder]__models.yml
  macros: [verb]_[object].sql
  tests: assert_[condition].sql
```

---

## Consistency Across BI Stack

### Cross-Tool Naming Standards

Maintain consistent naming across all BI tools:

```yaml
# Same metric across tools

dbt (definition):
  name: monthly_recurring_revenue_usd
  
Looker:
  name: Monthly Recurring Revenue (USD)
  field: monthly_recurring_revenue_usd
  
Tableau:
  name: Monthly Recurring Revenue (USD)
  field: [monthly_recurring_revenue_usd]
  
Mode:
  name: Monthly Recurring Revenue (USD)
  field: monthly_recurring_revenue_usd
  
Metabase:
  name: Monthly Recurring Revenue (USD)
  field: monthly_recurring_revenue_usd
```

### Glossary Mapping

Create central glossary mapping technical to business names:

```yaml
glossary:
  - technical_name: monthly_recurring_revenue_usd
    business_name: Monthly Recurring Revenue (USD)
    abbreviation: MRR
    definition: Total predictable revenue from active subscriptions...
    
  - technical_name: customer_acquisition_cost_usd
    business_name: Customer Acquisition Cost (USD)
    abbreviation: CAC
    definition: Average cost to acquire a new paying customer...
    
  - technical_name: customer_lifetime_value_usd
    business_name: Customer Lifetime Value (USD)
    abbreviation: LTV or CLV
    definition: Predicted net revenue from customer relationship...
```

### Reserved Words to Avoid

```sql
-- SQL reserved words (avoid as column names)
❌ user, date, timestamp, order, group, limit, offset, table, column

-- Use qualified versions instead
✅ user_id, order_date, event_timestamp, order_id, user_group

-- Platform-specific reserved words
-- Check documentation for: Snowflake, BigQuery, Redshift, Postgres
```

---

## Enforcement and Governance

### Automated Checks

Implement linting and validation:

```yaml
# sqlfluff configuration
[sqlfluff]
dialect = snowflake
templater = dbt

[sqlfluff:rules:L014]
# Unquoted identifiers must be lowercase
extended_capitalisation_policy = lower

[sqlfluff:rules:L029]
# Keywords should not be used as identifiers
unquoted_identifiers_policy = all
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.0.0
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix
        
  - repo: local
    hooks:
      - id: check-model-naming
        name: Check dbt model naming conventions
        entry: scripts/check_naming.py
        language: python
```

### Documentation Requirements

```markdown
Every new table/model must include:

- [ ] Name follows convention (stg_, int_, fct_, dim_, etc.)
- [ ] Schema documentation in .yml file
- [ ] All columns documented
- [ ] Primary key(s) identified
- [ ] Foreign keys documented
- [ ] Update frequency specified
- [ ] Owner assigned
- [ ] Tests configured (uniqueness, not_null, etc.)
```

---

## References and Further Reading

1. **dbt Style Guides**
   - [dbt Labs Style Guide](https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md)
   - [GitLab Data Team Handbook](https://about.gitlab.com/handbook/business-technology/data-team/)
   - [Brooklyn Data Co. Style Guide](https://github.com/brooklyn-data/co/blob/main/sql_style_guide.md)

2. **Dimensional Modeling**
   - "The Data Warehouse Toolkit" by Ralph Kimball
   - "Star Schema: The Complete Reference" by Christopher Adamson

3. **Data Governance**
   - DAMA-DMBOK: Data Management Body of Knowledge
   - "Data Governance: How to Design, Deploy and Sustain..." by John Ladley

---

**Document Version:** 1.0.0
**Last Updated:** 2024-01-15
**Maintained By:** Data Platform Team
**Review Frequency:** Quarterly
