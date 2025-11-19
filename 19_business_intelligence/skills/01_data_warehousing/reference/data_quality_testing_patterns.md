# Data Quality Testing Patterns

Quick reference for data quality testing patterns, validation checks, and testing frameworks for data warehouses.

## Data Quality Dimensions

### Completeness
**Definition**: All required data is present

**Tests**:
```sql
-- NULL checks
SELECT COUNT(*) as null_count
FROM customers
WHERE email IS NULL;

-- Should return 0 for required columns

-- Completeness ratio
SELECT
    COUNT(*) as total_rows,
    COUNT(phone) as phone_populated,
    ROUND(100.0 * COUNT(phone) / COUNT(*), 2) as phone_completeness_pct
FROM customers;

-- Target: 100% for critical fields, 80%+ for optional fields
```

### Accuracy
**Definition**: Data correctly represents real-world values

**Tests**:
```sql
-- Range checks
SELECT COUNT(*) as invalid_count
FROM orders
WHERE order_amount < 0 OR order_amount > 1000000;

-- Date validity
SELECT COUNT(*) as invalid_dates
FROM customers
WHERE birth_date > CURRENT_DATE()
   OR birth_date < '1900-01-01';

-- Email format validation
SELECT COUNT(*) as invalid_emails
FROM customers
WHERE email NOT LIKE '%_@__%.__%';

-- Phone format validation (US example)
SELECT COUNT(*) as invalid_phones
FROM customers
WHERE phone NOT REGEXP '^[0-9]{3}-[0-9]{3}-[0-9]{4}$';
```

### Consistency
**Definition**: Data is consistent across systems and tables

**Tests**:
```sql
-- Cross-table consistency
SELECT
    o.customer_id,
    COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
GROUP BY o.customer_id;

-- Should return 0 (referential integrity)

-- Aggregate consistency
WITH order_summary AS (
    SELECT
        customer_id,
        SUM(amount) as calculated_total
    FROM orders
    GROUP BY customer_id
)
SELECT COUNT(*) as mismatches
FROM customer_totals ct
JOIN order_summary os ON ct.customer_id = os.customer_id
WHERE ABS(ct.total_amount - os.calculated_total) > 0.01;

-- Cross-system reconciliation
SELECT
    'Source' as system,
    COUNT(*) as record_count,
    SUM(amount) as total_amount
FROM source_system.orders
UNION ALL
SELECT
    'Warehouse' as system,
    COUNT(*) as record_count,
    SUM(amount) as total_amount
FROM warehouse.orders;

-- Counts and totals should match
```

### Uniqueness
**Definition**: No duplicate records where uniqueness expected

**Tests**:
```sql
-- Primary key uniqueness
SELECT customer_id, COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Should return 0 rows

-- Business key uniqueness
SELECT email, COUNT(*) as duplicate_count
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;

-- Composite key uniqueness
SELECT
    customer_id,
    order_date,
    COUNT(*) as duplicate_count
FROM orders
GROUP BY customer_id, order_date
HAVING COUNT(*) > 1;
```

### Timeliness
**Definition**: Data is up-to-date and fresh

**Tests**:
```sql
-- Data freshness check
SELECT
    table_name,
    MAX(created_timestamp) as last_record,
    DATEDIFF(hour, MAX(created_timestamp), CURRENT_TIMESTAMP()) as hours_old
FROM (
    SELECT 'orders' as table_name, created_timestamp FROM orders
    UNION ALL
    SELECT 'customers' as table_name, created_timestamp FROM customers
    UNION ALL
    SELECT 'products' as table_name, created_timestamp FROM products
) all_tables
GROUP BY table_name;

-- Alert if hours_old > threshold

-- Pipeline execution freshness
SELECT
    pipeline_name,
    MAX(execution_timestamp) as last_run,
    DATEDIFF(hour, MAX(execution_timestamp), CURRENT_TIMESTAMP()) as hours_since_run
FROM pipeline_logs
GROUP BY pipeline_name
HAVING hours_since_run > 24;
```

### Validity
**Definition**: Data conforms to defined formats and rules

**Tests**:
```sql
-- Enumerated value validation
SELECT status, COUNT(*) as count
FROM orders
WHERE status NOT IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
GROUP BY status;

-- Should return 0 rows

-- Data type validation (after loading)
SELECT COUNT(*) as type_errors
FROM staging.orders
WHERE TRY_CAST(amount AS DECIMAL(10,2)) IS NULL
  AND amount IS NOT NULL;

-- Foreign key validation
SELECT COUNT(*) as fk_violations
FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM customers c
    WHERE c.customer_id = o.customer_id
);
```

## Testing Patterns

### Schema Tests

```sql
-- Column existence test
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'customers'
  AND column_name IN ('customer_id', 'email', 'created_timestamp');

-- Should return all expected columns

-- Data type test
SELECT
    column_name,
    data_type,
    CASE
        WHEN column_name = 'customer_id' AND data_type != 'NUMBER' THEN 'FAIL'
        WHEN column_name = 'email' AND data_type != 'VARCHAR' THEN 'FAIL'
        WHEN column_name = 'created_timestamp' AND data_type != 'TIMESTAMP_NTZ' THEN 'FAIL'
        ELSE 'PASS'
    END as test_result
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'customers'
  AND column_name IN ('customer_id', 'email', 'created_timestamp');

-- Primary key constraint test
SELECT constraint_name, column_name
FROM information_schema.key_column_usage
WHERE table_schema = 'public'
  AND table_name = 'customers'
  AND constraint_name LIKE '%PK%';
```

### Row Count Tests

```sql
-- Minimum row count test
SELECT
    COUNT(*) as row_count,
    CASE
        WHEN COUNT(*) >= 1000 THEN 'PASS'
        ELSE 'FAIL'
    END as test_result
FROM orders;

-- Row count growth test (should increase over time)
WITH daily_counts AS (
    SELECT
        DATE(created_timestamp) as date,
        COUNT(*) as daily_count
    FROM orders
    WHERE created_timestamp >= CURRENT_DATE() - 30
    GROUP BY DATE(created_timestamp)
)
SELECT
    date,
    daily_count,
    LAG(daily_count) OVER (ORDER BY date) as prev_day_count,
    CASE
        WHEN daily_count >= LAG(daily_count) OVER (ORDER BY date) THEN 'PASS'
        WHEN daily_count >= 0.8 * LAG(daily_count) OVER (ORDER BY date) THEN 'WARN'
        ELSE 'FAIL'
    END as test_result
FROM daily_counts
ORDER BY date DESC;

-- Row count equality test (source vs target)
SELECT
    ABS(src.count - tgt.count) as count_difference,
    CASE
        WHEN ABS(src.count - tgt.count) = 0 THEN 'PASS'
        WHEN ABS(src.count - tgt.count) < 10 THEN 'WARN'
        ELSE 'FAIL'
    END as test_result
FROM
    (SELECT COUNT(*) as count FROM source.orders) src,
    (SELECT COUNT(*) as count FROM target.orders) tgt;
```

### Aggregate Tests

```sql
-- Sum test (amounts should be positive)
SELECT
    SUM(order_amount) as total_amount,
    CASE
        WHEN SUM(order_amount) > 0 THEN 'PASS'
        ELSE 'FAIL'
    END as test_result
FROM orders;

-- Average within range test
SELECT
    AVG(order_amount) as avg_amount,
    CASE
        WHEN AVG(order_amount) BETWEEN 10 AND 500 THEN 'PASS'
        ELSE 'FAIL'
    END as test_result
FROM orders;

-- Standard deviation test (detect anomalies)
SELECT
    AVG(order_amount) as mean,
    STDDEV(order_amount) as stddev,
    AVG(order_amount) + 3 * STDDEV(order_amount) as upper_bound,
    AVG(order_amount) - 3 * STDDEV(order_amount) as lower_bound,
    COUNT(*) FILTER (WHERE order_amount > AVG(order_amount) + 3 * STDDEV(order_amount))
        as outliers_above,
    COUNT(*) FILTER (WHERE order_amount < AVG(order_amount) - 3 * STDDEV(order_amount))
        as outliers_below
FROM orders;
```

### Relationship Tests

```sql
-- One-to-many relationship test
SELECT
    o.customer_id,
    COUNT(DISTINCT c.customer_id) as customer_count,
    CASE
        WHEN COUNT(DISTINCT c.customer_id) = 1 THEN 'PASS'
        WHEN COUNT(DISTINCT c.customer_id) = 0 THEN 'ORPHAN'
        ELSE 'DUPLICATE'
    END as test_result
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id
HAVING COUNT(DISTINCT c.customer_id) != 1;

-- Many-to-many relationship test
SELECT
    customer_id,
    product_id,
    COUNT(*) as relationship_count,
    CASE
        WHEN COUNT(*) = 1 THEN 'PASS'
        ELSE 'FAIL'
    END as test_result
FROM customer_product_preferences
GROUP BY customer_id, product_id
HAVING COUNT(*) > 1;
```

## dbt Testing Patterns

### Built-in Tests (schema.yml)

```yaml
version: 2

models:
  - name: customers
    description: "Customer dimension table"
    tests:
      # Table-level tests
      - dbt_utils.equal_rowcount:
          compare_model: ref('stg_customers')
    columns:
      - name: customer_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'pending']
      - name: created_timestamp
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2020-01-01'"

  - name: orders
    description: "Orders fact table"
    tests:
      # Relationship test
      - dbt_utils.relationships_where:
          to: ref('customers')
          field: customer_id
          where: "status != 'cancelled'"
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('customers')
              field: customer_id
      - name: order_amount
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
      - name: order_date
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "<= current_date"
```

### Custom Data Tests

```sql
-- tests/assert_positive_revenue.sql
-- Returns records that fail the test

{{ config(severity = 'error') }}

select
    order_date,
    sum(order_amount) as daily_revenue
from {{ ref('fct_orders') }}
group by order_date
having sum(order_amount) < 0
```

```sql
-- tests/assert_no_future_dates.sql

select *
from {{ ref('fct_orders') }}
where order_date > current_date
```

```sql
-- tests/assert_order_customer_match.sql

select
    o.order_id,
    o.customer_id
from {{ ref('fct_orders') }} o
left join {{ ref('dim_customers') }} c
    on o.customer_id = c.customer_id
where c.customer_id is null
```

### Custom Generic Tests

```sql
-- macros/test_is_positive.sql

{% test is_positive(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

```yaml
# Usage in schema.yml
columns:
  - name: order_amount
    tests:
      - is_positive
```

## Great Expectations Patterns

```python
# Example expectation suite

import great_expectations as ge

# Load data
df = ge.read_csv('data/orders.csv')

# Expect column to exist
df.expect_column_to_exist('order_id')

# Expect values to be unique
df.expect_column_values_to_be_unique('order_id')

# Expect no NULL values
df.expect_column_values_to_not_be_null('customer_id')

# Expect values in set
df.expect_column_values_to_be_in_set(
    'status',
    ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
)

# Expect values to be between
df.expect_column_values_to_be_between(
    'order_amount',
    min_value=0,
    max_value=10000
)

# Expect column mean to be between
df.expect_column_mean_to_be_between(
    'order_amount',
    min_value=50,
    max_value=500
)

# Expect table row count to be between
df.expect_table_row_count_to_be_between(
    min_value=1000,
    max_value=1000000
)

# Expect column to match regex
df.expect_column_values_to_match_regex(
    'email',
    r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
)

# Expect recent data
df.expect_column_max_to_be_between(
    'order_date',
    min_value=datetime.now() - timedelta(days=1),
    max_value=datetime.now()
)
```

## Testing Framework

### Test Levels

**Level 1: Source Data Quality**
```sql
-- Run on raw source data
SELECT 'source_orders' as test, COUNT(*) as failures
FROM raw.orders
WHERE order_id IS NULL
UNION ALL
SELECT 'source_orders' as test, COUNT(*) as failures
FROM raw.orders
WHERE order_amount < 0;
```

**Level 2: Staging Layer Quality**
```sql
-- Run after cleaning/standardization
SELECT 'stg_orders_unique' as test, COUNT(*) - COUNT(DISTINCT order_id) as failures
FROM staging.orders
UNION ALL
SELECT 'stg_orders_valid_status' as test, COUNT(*) as failures
FROM staging.orders
WHERE status NOT IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
```

**Level 3: Business Logic Quality**
```sql
-- Run on final business-ready tables
SELECT 'fct_orders_revenue' as test,
    CASE WHEN SUM(order_amount) > 0 THEN 0 ELSE 1 END as failures
FROM mart.fct_orders
UNION ALL
SELECT 'dim_customer_orphans' as test, COUNT(*) as failures
FROM mart.fct_orders o
LEFT JOIN mart.dim_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

### Test Execution Schedule

**Daily Tests**:
- Row counts
- NULL checks on critical columns
- Data freshness
- Key metric totals

**Weekly Tests**:
- Schema validation
- Relationship integrity
- Aggregate value ranges
- Historical trend analysis

**Monthly Tests**:
- Full data profiling
- Cross-system reconciliation
- Performance benchmarks
- Storage growth analysis

## Data Quality Dashboard

```sql
-- Summary metrics for monitoring

CREATE OR REPLACE VIEW data_quality_summary AS
WITH test_results AS (
    -- Combine all test results
    SELECT 'customers_unique_ids' as test_name, COUNT(*) - COUNT(DISTINCT customer_id) as failures
    FROM customers
    UNION ALL
    SELECT 'customers_null_emails', COUNT(*) FROM customers WHERE email IS NULL
    UNION ALL
    SELECT 'orders_negative_amounts', COUNT(*) FROM orders WHERE order_amount < 0
    UNION ALL
    SELECT 'orders_future_dates', COUNT(*) FROM orders WHERE order_date > CURRENT_DATE()
    UNION ALL
    SELECT 'orders_orphan_customers', COUNT(*)
    FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
)
SELECT
    test_name,
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        WHEN failures < 10 THEN 'WARN'
        ELSE 'FAIL'
    END as status,
    CURRENT_TIMESTAMP() as test_timestamp
FROM test_results;

-- Query dashboard
SELECT * FROM data_quality_summary
WHERE status IN ('WARN', 'FAIL')
ORDER BY failures DESC;
```

## Alerting and Monitoring

```sql
-- Critical data quality alerts

-- Alert 1: Orphaned records
CREATE OR REPLACE ALERT orphaned_orders
    WAREHOUSE = monitoring_wh
    SCHEDULE = '60 MINUTE'
AS
SELECT COUNT(*) as orphan_count
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
HAVING COUNT(*) > 0;

-- Alert 2: Data freshness
CREATE OR REPLACE ALERT stale_data
    WAREHOUSE = monitoring_wh
    SCHEDULE = '15 MINUTE'
AS
SELECT
    table_name,
    hours_old
FROM (
    SELECT
        'orders' as table_name,
        DATEDIFF(hour, MAX(created_timestamp), CURRENT_TIMESTAMP()) as hours_old
    FROM orders
)
WHERE hours_old > 2;

-- Alert 3: Aggregate anomaly
CREATE OR REPLACE ALERT revenue_anomaly
    WAREHOUSE = monitoring_wh
    SCHEDULE = 'USING CRON 0 9 * * * America/New_York'
AS
WITH daily_revenue AS (
    SELECT
        DATE(order_date) as date,
        SUM(order_amount) as revenue
    FROM orders
    WHERE order_date >= CURRENT_DATE() - 30
    GROUP BY DATE(order_date)
)
SELECT
    date,
    revenue,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) as avg_7day,
    STDDEV(revenue) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) as stddev_7day
FROM daily_revenue
WHERE date = CURRENT_DATE() - 1
  AND ABS(revenue - avg_7day) > 2 * stddev_7day;
```

## Best Practices

### Test Design
1. **Start with critical fields**: Primary keys, foreign keys, required fields
2. **Test at source**: Catch issues early in pipeline
3. **Automate everything**: Manual testing doesn't scale
4. **Document expectations**: Clear definition of "valid"
5. **Version control tests**: Tests in git with transformations

### Test Execution
1. **Fail fast**: Stop pipeline on critical errors
2. **Warn on anomalies**: Alert but continue for non-critical
3. **Test incrementally**: Only test new/changed data when possible
4. **Log all results**: Maintain test execution history
5. **Monitor trends**: Track failure rates over time

### Remediation
1. **Clear ownership**: Who fixes data quality issues?
2. **Incident tracking**: Log all DQ incidents
3. **Root cause analysis**: Fix source, not symptoms
4. **Preventive measures**: Add tests to prevent recurrence
5. **Communication**: Alert stakeholders of issues

### Continuous Improvement
1. **Review test coverage**: Quarterly audit
2. **Add new tests**: As new issues discovered
3. **Remove obsolete tests**: Clean up unused tests
4. **Performance optimization**: Keep tests fast
5. **User feedback**: Incorporate data consumer input
