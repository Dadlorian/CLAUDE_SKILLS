# Data Quality Implementation Guide

## 2-Week Quick Start

### Week 1: Setup Testing Framework

```yaml
Day 1-2: Choose Tool
  dbt Tests (if using dbt):
    Pros: Integrated, version controlled, free
    Cons: Limited to dbt models

  Great Expectations:
    Pros: Comprehensive, flexible, Python
    Cons: Steeper learning curve

  Monte Carlo:
    Pros: ML-powered, automated, easy
    Cons: Expensive

Recommendation: Start with dbt tests if using dbt
```

#### dbt Tests Setup
```yaml
# models/schema.yml
version: 2

models:
  - name: dim_customers
    description: Customer dimension table
    columns:
      - name: customer_id
        description: Unique customer identifier
        tests:
          - unique
          - not_null

      - name: email
        description: Customer email
        tests:
          - not_null
          - dbt_utils.email_format

      - name: signup_date
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: "2020-01-01"
              max_value: "{{ current_date }}"

    tests:
      - dbt_utils.row_count_in_range:
          min_value: 10000
          max_value: 1000000
```

### Week 2: Implement Monitoring

```yaml
Day 1-2: Freshness Checks
  # sources.yml
  sources:
    - name: production
      tables:
        - name: orders
          freshness:
            warn_after: {count: 1, period: hour}
            error_after: {count: 2, period: hour}
          loaded_at_field: updated_at

Day 3-4: Quality Dashboard
  - Pass/fail rate by table
  - Failed tests detail
  - Freshness compliance
  - Trend over time

Day 5: Alerting
  - Slack notifications
  - Email for critical failures
  - PagerDuty for outages
```

## Essential Quality Tests

```yaml
Completeness:
  - not_null on required fields
  - row_count_in_range

Accuracy:
  - accepted_range (e.g., amount > 0)
  - regex_match (email format)
  - relationships (foreign keys)

Consistency:
  - unique (primary keys)
  - no_duplicates
  - cross_table_equality

Timeliness:
  - freshness checks
  - update_timestamp validation

Validity:
  - accepted_values (status in ['active', 'inactive'])
  - data_type validation
```

## Quality Score Calculation

```sql
CREATE VIEW data_quality_scores AS
SELECT
  table_name,
  -- Completeness (25%)
  (100 - null_percentage) * 0.25 as completeness_score,

  -- Accuracy (30%)
  (passed_validations / total_validations * 100) * 0.30 as accuracy_score,

  -- Freshness (20%)
  CASE
    WHEN data_age_minutes <= sla_minutes THEN 100
    WHEN data_age_minutes <= sla_minutes * 1.5 THEN 75
    ELSE 50
  END * 0.20 as freshness_score,

  -- Uniqueness (15%)
  (100 - duplicate_percentage) * 0.15 as uniqueness_score,

  -- Consistency (10%)
  referential_integrity_score * 0.10 as consistency_score,

  -- Overall
  completeness_score + accuracy_score + freshness_score +
  uniqueness_score + consistency_score as overall_score

FROM quality_metrics;
```

## Quick Wins

```yaml
Week 1:
  □ NOT NULL on all primary keys
  □ UNIQUE on primary keys
  □ Freshness checks on critical tables
  □ Row count thresholds

Week 2:
  □ Foreign key relationships
  □ Accepted values for enums
  □ Range checks on amounts/dates
  □ Email/phone format validation

Week 3:
  □ Quality dashboard live
  □ Slack alerts configured
  □ Quality scores in catalog
  □ Documentation updated

Week 4:
  □ Advanced tests added
  □ Cross-table validations
  □ SLA monitoring
  □ Incident response process
```
