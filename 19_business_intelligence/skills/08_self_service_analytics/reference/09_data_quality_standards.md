# Data Quality Standards Reference

## Overview

High data quality is essential for self-service analytics success. Users must trust the data they access. This reference outlines comprehensive quality standards based on practices from leading data organizations.

## Data Quality Dimensions

### 1. Completeness

```yaml
Definition:
  The extent to which all required data is present

Metrics:
  - Null percentage per column
  - Missing record counts
  - Required field population rate

Acceptable Thresholds:
  Critical Fields: 100% populated
  Important Fields: >98% populated
  Nice-to-Have Fields: >90% populated

Tests:
  - NOT NULL constraints
  - Row count expectations
  - Required field checks
```

#### Completeness Tests

```sql
-- dbt test: check for nulls in critical fields
SELECT
  '{{ column_name }}' as column_name,
  COUNT(*) as null_count,
  COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {{ ref('customers') }}) as null_percentage
FROM {{ ref('customers') }}
WHERE {{ column_name }} IS NULL
HAVING COUNT(*) > 0;

-- Great Expectations
expect_column_values_to_not_be_null(
    column="customer_id",
    mostly=1.0  -- 100% non-null
)

expect_table_row_count_to_be_between(
    min_value=90000,
    max_value=110000  -- Expected range
)
```

### 2. Accuracy

```yaml
Definition:
  Data correctly represents the real-world entity or event

Metrics:
  - Error rate vs. source system
  - Reconciliation match rate
  - Manual validation pass rate

Acceptable Thresholds:
  Financial Data: >99.9% accurate
  Operational Data: >99% accurate
  Analytical Data: >95% accurate

Tests:
  - Range validations
  - Format checks
  - Cross-system reconciliation
  - Statistical distribution checks
```

#### Accuracy Tests

```sql
-- Range validation
SELECT COUNT(*)
FROM orders
WHERE order_amount NOT BETWEEN 0 AND 1000000
  OR order_date > CURRENT_DATE
  OR order_date < '2020-01-01';

-- Reconciliation with source
SELECT
  'Warehouse' as source,
  COUNT(*) as order_count,
  SUM(amount) as total_revenue
FROM warehouse.orders
WHERE order_date = CURRENT_DATE - 1

UNION ALL

SELECT
  'Source System' as source,
  COUNT(*) as order_count,
  SUM(amount) as total_revenue
FROM source.orders
WHERE order_date = CURRENT_DATE - 1;

-- Great Expectations
expect_column_values_to_be_between(
    column="order_amount",
    min_value=0,
    max_value=1000000
)

expect_column_values_to_match_regex(
    column="email",
    regex="^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
)
```

### 3. Consistency

```yaml
Definition:
  Data is uniform across systems and over time

Metrics:
  - Cross-table consistency rate
  - Format standardization compliance
  - Duplicate record rate

Acceptable Thresholds:
  Duplicate Rate: <0.1%
  Format Compliance: >99%
  Cross-System Match: >99%

Tests:
  - Referential integrity checks
  - Duplicate detection
  - Format standardization
  - Naming convention compliance
```

#### Consistency Tests

```sql
-- Referential integrity
SELECT o.order_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Duplicate detection
SELECT
  customer_email,
  COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_email
HAVING COUNT(*) > 1;

-- Format consistency
SELECT COUNT(*)
FROM customers
WHERE phone_number NOT LIKE '___-___-____'  -- Expected format

-- Cross-table consistency
SELECT
  SUM(CASE WHEN c.total_orders != o.order_count THEN 1 ELSE 0 END) as inconsistent_count
FROM customers c
LEFT JOIN (
  SELECT customer_id, COUNT(*) as order_count
  FROM orders
  GROUP BY customer_id
) o ON c.customer_id = o.customer_id;
```

### 4. Timeliness/Freshness

```yaml
Definition:
  Data is available when needed and up-to-date

Metrics:
  - Data latency (time from event to availability)
  - SLA compliance rate
  - Refresh frequency adherence

SLA Examples:
  Real-Time Data: <5 minutes
  Hourly Updates: <15 minutes past hour
  Daily Updates: By 6 AM daily
  Weekly Updates: Monday by 9 AM

Tests:
  - Freshness checks
  - Update timestamp validation
  - Gap detection
```

#### Freshness Tests

```sql
-- Check last update time
SELECT
  table_name,
  MAX(updated_at) as last_update,
  CURRENT_TIMESTAMP - MAX(updated_at) as age_minutes
FROM (
  SELECT 'orders' as table_name, MAX(updated_at) as updated_at FROM orders
  UNION ALL
  SELECT 'customers', MAX(updated_at) FROM customers
  UNION ALL
  SELECT 'products', MAX(updated_at) FROM products
) tables
GROUP BY table_name
HAVING age_minutes > 60;  -- Alert if > 60 minutes old

-- dbt freshness test (in sources.yml)
sources:
  - name: production
    tables:
      - name: orders
        freshness:
          warn_after: {count: 1, period: hour}
          error_after: {count: 2, period: hour}

-- Gap detection
SELECT
  DATE(order_date) as date,
  COUNT(*) as order_count
FROM orders
WHERE order_date >= CURRENT_DATE - 30
GROUP BY DATE(order_date)
HAVING COUNT(*) < 100;  -- Alert if unusually low
```

### 5. Validity

```yaml
Definition:
  Data conforms to defined business rules and constraints

Metrics:
  - Schema compliance rate
  - Business rule violation rate
  - Data type conformance

Acceptable Thresholds:
  Schema Compliance: 100%
  Business Rules: >99%
  Type Conformance: 100%

Tests:
  - Data type validation
  - Enum/domain checks
  - Business rule assertions
  - Constraint validation
```

#### Validity Tests

```sql
-- Enum validation
SELECT COUNT(*)
FROM orders
WHERE status NOT IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled');

-- Business rule: order amount = sum of line items
SELECT o.order_id
FROM orders o
JOIN (
  SELECT
    order_id,
    SUM(quantity * unit_price) as calculated_total
  FROM order_items
  GROUP BY order_id
) li ON o.order_id = li.order_id
WHERE ABS(o.order_amount - li.calculated_total) > 0.01;

-- Great Expectations
expect_column_values_to_be_in_set(
    column="order_status",
    value_set=['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
)

expect_column_values_to_be_of_type(
    column="order_amount",
    type_="DECIMAL"
)
```

### 6. Uniqueness

```yaml
Definition:
  No unintended duplicate records exist

Metrics:
  - Primary key uniqueness rate
  - Duplicate record percentage
  - Near-duplicate detection

Acceptable Thresholds:
  Primary Keys: 100% unique
  Natural Keys: >99.9% unique
  Overall Duplicates: <0.1%

Tests:
  - Primary key uniqueness
  - Unique constraint validation
  - Fuzzy duplicate detection
```

#### Uniqueness Tests

```sql
-- Primary key uniqueness
SELECT
  order_id,
  COUNT(*) as duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- dbt test
SELECT order_id
FROM {{ ref('orders') }}
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Great Expectations
expect_column_values_to_be_unique(
    column="order_id"
)

-- Near-duplicate detection
SELECT
  a.customer_id as id1,
  b.customer_id as id2,
  a.email as email1,
  b.email as email2
FROM customers a
JOIN customers b
  ON LOWER(TRIM(a.email)) = LOWER(TRIM(b.email))
  AND a.customer_id < b.customer_id;
```

## Quality Scoring

### Overall Quality Score

```yaml
Calculation:
  quality_score = (
    (completeness_score * 0.25) +
    (accuracy_score * 0.30) +
    (consistency_score * 0.20) +
    (freshness_score * 0.15) +
    (validity_score * 0.10)
  )

Scoring Thresholds:
  Excellent: 95-100
  Good: 85-94
  Fair: 70-84
  Poor: <70

Display:
  - Overall score badge
  - Dimension breakdown
  - Trend over time
  - Issue list
```

### Quality Scorecard

```sql
CREATE VIEW data_quality_scorecard AS
SELECT
  table_name,
  -- Completeness score
  100 - (null_count * 100.0 / total_fields) as completeness_score,

  -- Accuracy score
  (passed_validations * 100.0 / total_validations) as accuracy_score,

  -- Freshness score
  CASE
    WHEN data_age_minutes <= sla_minutes THEN 100
    WHEN data_age_minutes <= sla_minutes * 1.5 THEN 75
    WHEN data_age_minutes <= sla_minutes * 2 THEN 50
    ELSE 0
  END as freshness_score,

  -- Uniqueness score
  100 - (duplicate_count * 100.0 / total_records) as uniqueness_score,

  -- Overall score
  (
    (100 - (null_count * 100.0 / total_fields)) * 0.25 +
    (passed_validations * 100.0 / total_validations) * 0.30 +
    CASE
      WHEN data_age_minutes <= sla_minutes THEN 100
      WHEN data_age_minutes <= sla_minutes * 1.5 THEN 75
      ELSE 50
    END * 0.15 +
    (100 - (duplicate_count * 100.0 / total_records)) * 0.10
  ) as overall_quality_score

FROM data_quality_metrics;
```

## Quality Monitoring

### Automated Monitoring

```yaml
Monitoring Approach:

  Continuous Monitoring:
    - Run tests on every data refresh
    - Immediate alerts on failures
    - Auto-quarantine bad data
    - Notify data owners

  Scheduled Monitoring:
    - Daily: All critical tables
    - Hourly: Real-time datasets
    - Weekly: Less critical tables
    - On-demand: Ad-hoc checks

  Anomaly Detection:
    - Statistical outliers
    - Distribution shifts
    - Volume anomalies
    - Pattern changes
```

#### Monitoring Implementation

```yaml
# Monte Carlo - Automated Monitoring
monitors:
  - type: freshness
    table: orders
    threshold: 2 hours
    severity: high

  - type: volume
    table: orders
    comparison: day_over_day
    threshold: 20%
    severity: medium

  - type: field_quality
    table: customers
    field: email
    rule: null_rate < 0.01
    severity: high

  - type: schema
    table: products
    alert_on: column_addition, column_deletion
    severity: medium

  - type: distribution
    table: orders
    field: order_amount
    comparison: day_over_day
    threshold: 3 std_devs
    severity: low
```

### Alerting Strategy

```yaml
Alert Severity Levels:

  Critical:
    Description: Data outage, major quality issue
    Examples:
      - No data refreshed in 4+ hours
      - >10% null rate in critical field
      - Complete pipeline failure
    Response:
      - Page on-call engineer
      - Incident ticket created
      - Status page updated
      - Stakeholders notified

  High:
    Description: Significant quality degradation
    Examples:
      - 2-4 hour data delay
      - 5-10% null rate increase
      - Failed critical test
    Response:
      - Slack alert
      - Email to data team
      - Investigation within 1 hour
      - Escalate if unresolved

  Medium:
    Description: Noticeable but not blocking
    Examples:
      - 1-2 hour delay
      - Minor quality degradation
      - Non-critical test failure
    Response:
      - Slack notification
      - Review next business day
      - Add to backlog

  Low:
    Description: Informational
    Examples:
      - Minor anomaly detected
      - Warning threshold reached
      - Best practice violation
    Response:
      - Log for review
      - Weekly summary
      - Optional investigation
```

## Quality Incident Response

### Incident Workflow

```yaml
1. Detection:
   - Automated monitoring alert
   - User report
   - Manual discovery

2. Triage:
   - Assess severity
   - Identify affected data
   - Estimate impact
   - Assign owner

3. Investigation:
   - Root cause analysis
   - Impact assessment
   - Affected users/dashboards
   - Timeline reconstruction

4. Communication:
   - Notify affected users
   - Update status page
   - Provide workarounds
   - Set expectations

5. Resolution:
   - Fix root cause
   - Backfill data if needed
   - Validate fix
   - Resume normal operations

6. Post-Mortem:
   - Document incident
   - Identify improvements
   - Update runbooks
   - Implement preventions
```

### Incident Communication Template

```markdown
Subject: [DATA QUALITY] Issue with {table_name} - {Status}

Severity: {Critical | High | Medium | Low}
Status: {Investigating | Identified | Fixing | Resolved}
Affected Data: {table_name}
Impact: {description}
First Detected: {timestamp}

## Summary
Brief description of the issue.

## Impact
- Affected dashboards: [list]
- Affected users: [count/list]
- Time period affected: [range]
- Data accuracy: [description]

## Current Status
What we're doing to resolve it.

## Workaround
If available, how to get accurate data in the meantime.

## Next Update
When we'll provide the next update.

## Questions
Contact: {name} via {Slack channel / email}
```

## Quality Improvement Process

### Continuous Improvement Cycle

```yaml
1. Measure:
   - Collect quality metrics
   - Identify problem areas
   - Benchmark against targets
   - Trend analysis

2. Analyze:
   - Root cause analysis
   - Pattern identification
   - Impact assessment
   - Prioritization

3. Improve:
   - Implement fixes
   - Add new tests
   - Update processes
   - Enhance monitoring

4. Control:
   - Monitor improvements
   - Validate effectiveness
   - Prevent regression
   - Document learnings

5. Repeat:
   - Continuous cycle
   - Regular reviews
   - Ongoing optimization
```

### Quality SLAs

```yaml
Service Level Agreements:

Tier 1 (Critical):
  Tables: Revenue, customers, core metrics
  Freshness: <30 minutes
  Accuracy: >99.9%
  Completeness: >99.5%
  Tests: Comprehensive
  Monitoring: Continuous
  Support: 24/7

Tier 2 (Important):
  Tables: Product, marketing, operational
  Freshness: <2 hours
  Accuracy: >99%
  Completeness: >98%
  Tests: Extensive
  Monitoring: Hourly
  Support: Business hours

Tier 3 (Standard):
  Tables: Supporting, derived
  Freshness: <24 hours
  Accuracy: >95%
  Completeness: >95%
  Tests: Basic
  Monitoring: Daily
  Support: Best effort
```

## Quality Documentation

### Dataset Quality Profile

```yaml
Table: fact_orders
Quality Score: 94/100

Completeness: 98/100
  - order_id: 100% (required)
  - customer_id: 100% (required)
  - order_date: 100% (required)
  - order_amount: 99% (1% null, acceptable)
  - shipping_address: 95% (5% null, tracking improvement)

Accuracy: 97/100
  - Daily reconciliation: 99.8% match with source
  - Range validations: 100% pass
  - Format validations: 95% pass (improving)

Freshness: 95/100
  - SLA: Hourly updates
  - Compliance: 98% on-time
  - Last updated: 15 minutes ago

Consistency: 90/100
  - Referential integrity: 100%
  - Duplicate rate: 0.02%
  - Format consistency: 88% (improving)

Known Issues:
  - Some legacy orders missing shipping address (backfill planned)
  - Occasional duplicates from source system (being addressed)

Tests:
  - 45 automated tests
  - Last run: 10 minutes ago
  - Pass rate: 44/45 (97.8%)
  - 1 known acceptable failure

Contact:
  Owner: data-platform-team@company.com
  On-call: data-oncall@company.com
```

## Tools & Technologies

### Data Quality Platforms

```yaml
Great Expectations:
  Type: Open source
  Strengths: Flexible, code-based, comprehensive
  Best For: Engineering-led teams

dbt Tests:
  Type: Built into dbt
  Strengths: Integrated with transformations, simple
  Best For: dbt users

Monte Carlo:
  Type: Commercial
  Strengths: ML-powered, automated, easy setup
  Best For: Mature data teams with budget

Soda:
  Type: Commercial + OSS
  Strengths: YAML-based, data contracts, good balance
  Best For: Balanced approach

Datafold:
  Type: Commercial
  Strengths: Data diffing, CI/CD integration
  Best For: Change validation

Anomalo:
  Type: Commercial
  Strengths: Automated monitoring, ML detection
  Best For: Large-scale monitoring
```

## References

- "The Data Quality Framework" by DAMA
- Great Expectations Documentation
- dbt Testing Best Practices
- Monte Carlo Data Quality Dimensions
- "Data Quality for Analytics" by Barr Moses
