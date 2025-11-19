# Data Quality Testing Guide

## Overview
Data quality testing ensures data meets standards before being used for analytics and decision-making.

## Testing Layers

### 1. Source Quality Tests
```yaml
# models/staging/_sources.yml
sources:
  - name: postgres
    tables:
      - name: orders
        tests:
          - dbt_utils.recency:
              datepart: hour
              field: created_at
              interval: 24
        columns:
          - name: id
            tests:
              - unique
              - not_null
          - name: customer_id
            tests:
              - not_null
              - relationships:
                  to: source('postgres', 'customers')
                  field: id
```

### 2. Transformation Quality Tests
```yaml
# models/marts/schema.yml
models:
  - name: fct_orders
    tests:
      - dbt_utils.equal_rowcount:
          compare_model: source('postgres', 'orders')
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
```

### 3. Business Logic Tests
```sql
-- tests/assert_order_total_matches_line_items.sql
SELECT
    order_id,
    order_total,
    line_items_sum,
    ABS(order_total - line_items_sum) as difference
FROM {{ ref('fct_orders') }}
WHERE ABS(order_total - line_items_sum) > 0.01
-- Returns records where totals don't match
```

## Great Expectations Integration

```python
import great_expectations as gx

context = gx.get_context()

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders_suite"
)

# Completeness
validator.expect_column_values_to_not_be_null(column="order_id")

# Uniqueness
validator.expect_column_values_to_be_unique(column="order_id")

# Validity
validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["pending", "processing", "completed", "cancelled"]
)

# Range
validator.expect_column_values_to_be_between(
    column="amount",
    min_value=0,
    max_value=1000000
)

validator.save_expectation_suite()
```

## Custom Data Tests

```sql
-- tests/generic/test_no_nulls_in_columns.sql
{% test no_nulls_in_columns(model, column_names) %}

WITH validation AS (
    SELECT
        {% for column in column_names %}
        SUM(CASE WHEN {{ column }} IS NULL THEN 1 ELSE 0 END) AS {{ column }}_nulls
        {{ "," if not loop.last }}
        {% endfor %}
    FROM {{ model }}
)

SELECT *
FROM validation
WHERE
    {% for column in column_names %}
    {{ column }}_nulls > 0
    {{ "OR" if not loop.last }}
    {% endfor %}

{% endtest %}

-- Usage
tests:
  - no_nulls_in_columns:
      column_names: ['order_id', 'customer_id', 'amount']
```

## Reconciliation Tests

```sql
-- tests/reconcile_source_to_target.sql
WITH source_summary AS (
    SELECT
        COUNT(*) as record_count,
        SUM(amount) as total_amount
    FROM {{ source('postgres', 'orders') }}
    WHERE DATE(created_at) = CURRENT_DATE - 1
),
target_summary AS (
    SELECT
        COUNT(*) as record_count,
        SUM(amount) as total_amount
    FROM {{ ref('fct_orders') }}
    WHERE order_date = CURRENT_DATE - 1
)
SELECT
    'Record Count Mismatch' as check_name,
    s.record_count - t.record_count as difference
FROM source_summary s
CROSS JOIN target_summary t
WHERE s.record_count != t.record_count

UNION ALL

SELECT
    'Amount Mismatch' as check_name,
    s.total_amount - t.total_amount as difference
FROM source_summary s
CROSS JOIN target_summary t
WHERE ABS(s.total_amount - t.total_amount) > 0.01
```

## Anomaly Detection

```sql
-- tests/detect_anomalies.sql
WITH daily_metrics AS (
    SELECT
        DATE(order_date) as date,
        COUNT(*) as order_count,
        AVG(amount) as avg_amount
    FROM {{ ref('fct_orders') }}
    WHERE order_date >= CURRENT_DATE - 30
    GROUP BY DATE(order_date)
),
baseline AS (
    SELECT
        AVG(order_count) as avg_orders,
        STDDEV(order_count) as stddev_orders
    FROM daily_metrics
    WHERE date < CURRENT_DATE
)
SELECT
    dm.date,
    dm.order_count,
    b.avg_orders,
    ABS(dm.order_count - b.avg_orders) / NULLIF(b.stddev_orders, 0) as z_score
FROM daily_metrics dm
CROSS JOIN baseline b
WHERE dm.date = CURRENT_DATE
  AND ABS(dm.order_count - b.avg_orders) > 3 * b.stddev_orders
```

## Testing Best Practices

1. **Test Early**: Catch issues at source layer
2. **Layer Tests**: Source → Staging → Marts
3. **Document Tests**: Explain what each test validates
4. **Monitor Pass Rates**: Track test failures over time
5. **Set Severity**: Warn vs fail for different tests
6. **Automate**: Run tests in CI/CD
7. **Alert on Failures**: Notify team immediately

## Resources

- **dbt Testing**: https://docs.getdbt.com/docs/build/tests
- **Great Expectations**: https://docs.greatexpectations.io/
- **dbt-expectations**: https://github.com/calogica/dbt-expectations
