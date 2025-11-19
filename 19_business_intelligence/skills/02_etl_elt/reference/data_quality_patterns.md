# Data Quality Patterns Reference

## Quality Dimensions

### 1. Completeness
Data is present and not missing.

```sql
-- Check for NULL values
SELECT
    COUNT(*) as total_rows,
    COUNT(customer_id) as non_null_customer_id,
    COUNT(*) - COUNT(customer_id) as null_customer_id,
    ROUND(100.0 * COUNT(customer_id) / COUNT(*), 2) as completeness_pct
FROM orders;

-- dbt test
version: 2
models:
  - name: orders
    columns:
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('customers')
              field: id
```

### 2. Accuracy
Data correctly represents the real-world entity.

```sql
-- Check for valid email format
SELECT
    COUNT(*) as total,
    SUM(CASE
        WHEN email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        THEN 1 ELSE 0
    END) as valid_emails,
    SUM(CASE
        WHEN email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        THEN 1 ELSE 0
    END) as invalid_emails
FROM customers;

-- Great Expectations
expect_column_values_to_match_regex(
    column='email',
    regex='^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
)
```

### 3. Consistency
Data is consistent across systems and over time.

```sql
-- Check consistency between systems
WITH source_counts AS (
    SELECT 'source_db' as system, COUNT(*) as cnt
    FROM source_db.orders
    WHERE date = CURRENT_DATE
),
warehouse_counts AS (
    SELECT 'warehouse' as system, COUNT(*) as cnt
    FROM warehouse.orders
    WHERE date = CURRENT_DATE
)
SELECT
    s.cnt as source_count,
    w.cnt as warehouse_count,
    ABS(s.cnt - w.cnt) as difference,
    ROUND(100.0 * ABS(s.cnt - w.cnt) / NULLIF(s.cnt, 0), 2) as diff_pct
FROM source_counts s
CROSS JOIN warehouse_counts w;
```

### 4. Timeliness
Data is up-to-date and available when needed.

```sql
-- Check data freshness
SELECT
    table_name,
    MAX(updated_at) as last_update,
    CURRENT_TIMESTAMP - MAX(updated_at) as staleness,
    CASE
        WHEN CURRENT_TIMESTAMP - MAX(updated_at) > INTERVAL '1 hour'
        THEN 'STALE'
        ELSE 'FRESH'
    END as freshness_status
FROM information_schema.tables
WHERE table_schema = 'analytics'
GROUP BY table_name;

-- dbt freshness check
version: 2
sources:
  - name: postgres
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    tables:
      - name: orders
        loaded_at_field: updated_at
```

### 5. Validity
Data conforms to defined formats and rules.

```sql
-- Check for valid status values
SELECT
    status,
    COUNT(*) as count
FROM orders
WHERE status NOT IN ('pending', 'processing', 'completed', 'cancelled')
GROUP BY status;

-- dbt test
tests:
  - accepted_values:
      values: ['pending', 'processing', 'completed', 'cancelled']
```

### 6. Uniqueness
No duplicate records exist.

```sql
-- Find duplicates
SELECT
    order_id,
    COUNT(*) as duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- dbt test
tests:
  - unique
  - dbt_utils.unique_combination_of_columns:
      combination_of_columns:
        - order_id
        - line_item_id
```

## Testing Frameworks

### dbt Tests

#### Schema Tests
```yaml
# models/schema.yml
version: 2

models:
  - name: customers
    description: Customer dimension table
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null

      - name: email
        description: Customer email
        tests:
          - unique
          - not_null

      - name: created_at
        description: Account creation timestamp
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "<= current_timestamp"

      - name: lifetime_value
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: true

      - name: status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'suspended']

      - name: country_code
        tests:
          - relationships:
              to: ref('countries')
              field: code
```

#### Data Tests (Custom SQL)
```sql
-- tests/assert_positive_order_amounts.sql
SELECT
    order_id,
    amount
FROM {{ ref('orders') }}
WHERE amount <= 0

-- If this returns rows, the test fails

-- tests/assert_valid_date_range.sql
SELECT *
FROM {{ ref('orders') }}
WHERE order_date > CURRENT_DATE
   OR order_date < '2020-01-01'
```

#### Generic Tests
```sql
-- macros/test_no_nulls_in_columns.sql
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

-- Usage in schema.yml
models:
  - name: orders
    tests:
      - no_nulls_in_columns:
          column_names: ['order_id', 'customer_id', 'order_date']
```

### Great Expectations

#### Expectations Suite
```python
# great_expectations/expectations/orders_suite.json
import great_expectations as gx

# Initialize context
context = gx.get_context()

# Create expectation suite
suite = context.create_expectation_suite(
    expectation_suite_name="orders_suite",
    overwrite_existing=True
)

# Add expectations
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders_suite"
)

# Completeness
validator.expect_column_values_to_not_be_null(column="order_id")
validator.expect_column_values_to_not_be_null(column="customer_id")

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

# Type
validator.expect_column_values_to_be_of_type(
    column="order_date",
    type_="DATE"
)

# Regex
validator.expect_column_values_to_match_regex(
    column="email",
    regex="^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
)

# Relationships
validator.expect_column_pair_values_to_be_equal(
    column_A="order_total",
    column_B="sum_of_line_items"
)

# Statistical
validator.expect_column_mean_to_be_between(
    column="amount",
    min_value=50,
    max_value=500
)

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

#### Checkpoint Configuration
```yaml
# great_expectations/checkpoints/daily_validation.yml
name: daily_validation
config_version: 1.0
class_name: SimpleCheckpoint
run_name_template: "%Y%m%d-%H%M%S"

validations:
  - batch_request:
      datasource_name: postgres_datasource
      data_connector_name: default_runtime_data_connector
      data_asset_name: orders
    expectation_suite_name: orders_suite

action_list:
  - name: store_validation_result
    action:
      class_name: StoreValidationResultAction

  - name: update_data_docs
    action:
      class_name: UpdateDataDocsAction

  - name: send_slack_notification
    action:
      class_name: SlackNotificationAction
      slack_webhook: ${SLACK_WEBHOOK}
      notify_on: failure
```

### Soda Core

#### Soda Checks (YAML)
```yaml
# checks/orders_checks.yml
checks for orders:
  # Completeness
  - missing_count(order_id) = 0
  - missing_count(customer_id) = 0
  - missing_percent(email) < 5%

  # Validity
  - invalid_count(email) = 0:
      valid format: email
  - invalid_count(phone) = 0:
      valid regex: ^\+?[1-9]\d{1,14}$

  # Accepted values
  - invalid_count(status) = 0:
      valid values: [pending, processing, completed, cancelled]

  # Numeric ranges
  - invalid_count(amount) = 0:
      valid min: 0
      valid max: 1000000

  # Row count anomaly
  - row_count > 1000
  - change for row_count < 50%

  # Freshness
  - freshness(updated_at) < 1h

  # Duplicates
  - duplicate_count(order_id) = 0

  # Schema
  - schema:
      fail:
        when required column missing: [order_id, customer_id, amount]
        when wrong column type:
          order_id: integer
          amount: numeric

  # Custom SQL
  - failed rows:
      name: Orders with negative amounts
      fail query: |
        SELECT *
        FROM orders
        WHERE amount < 0
```

## Quality Check Patterns

### Pattern 1: Layered Quality Checks
```sql
-- Layer 1: Source Quality (Raw Layer)
CREATE OR REPLACE VIEW quality.source_orders_check AS
SELECT
    'source_orders' as table_name,
    CURRENT_TIMESTAMP as check_time,
    COUNT(*) as row_count,
    COUNT(DISTINCT order_id) as unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id) as duplicate_orders,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_order_ids,
    SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) as null_amounts,
    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) as negative_amounts
FROM raw.orders;

-- Layer 2: Transformation Quality (Staging Layer)
CREATE OR REPLACE VIEW quality.staging_orders_check AS
SELECT
    'staging_orders' as table_name,
    CURRENT_TIMESTAMP as check_time,
    COUNT(*) as row_count,
    -- Should have no nulls after cleaning
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_order_ids,
    -- Should have no duplicates after dedup
    COUNT(*) - COUNT(DISTINCT order_id) as duplicate_orders,
    -- Reconciliation with source
    (SELECT COUNT(*) FROM raw.orders) as source_count,
    COUNT(*) - (SELECT COUNT(*) FROM raw.orders) as reconciliation_diff
FROM staging.orders;

-- Layer 3: Business Logic Quality (Marts Layer)
CREATE OR REPLACE VIEW quality.marts_orders_check AS
SELECT
    'marts_orders' as table_name,
    CURRENT_TIMESTAMP as check_time,
    -- Business rule validations
    SUM(CASE WHEN total_amount != line_items_sum THEN 1 ELSE 0 END) as amount_mismatch,
    SUM(CASE WHEN order_date > ship_date THEN 1 ELSE 0 END) as date_logic_errors,
    -- Referential integrity
    SUM(CASE WHEN customer_id NOT IN (SELECT id FROM dim_customers) THEN 1 ELSE 0 END) as orphaned_orders
FROM marts.fact_orders;
```

### Pattern 2: Reconciliation Checks
```sql
-- Source-to-Target Reconciliation
WITH source_summary AS (
    SELECT
        DATE(created_at) as date,
        COUNT(*) as record_count,
        SUM(amount) as total_amount,
        MD5(STRING_AGG(CAST(order_id AS VARCHAR), ',' ORDER BY order_id)) as hash_value
    FROM source_system.orders
    WHERE DATE(created_at) = CURRENT_DATE - 1
    GROUP BY DATE(created_at)
),
target_summary AS (
    SELECT
        order_date as date,
        COUNT(*) as record_count,
        SUM(amount) as total_amount,
        MD5(STRING_AGG(CAST(order_id AS VARCHAR), ',' ORDER BY order_id)) as hash_value
    FROM warehouse.orders
    WHERE order_date = CURRENT_DATE - 1
    GROUP BY order_date
)
SELECT
    s.date,
    s.record_count as source_records,
    t.record_count as target_records,
    s.record_count - t.record_count as record_diff,
    s.total_amount as source_amount,
    t.total_amount as target_amount,
    s.total_amount - t.total_amount as amount_diff,
    CASE
        WHEN s.hash_value = t.hash_value THEN 'MATCH'
        ELSE 'MISMATCH'
    END as hash_comparison
FROM source_summary s
FULL OUTER JOIN target_summary t ON s.date = t.date;
```

### Pattern 3: Anomaly Detection
```sql
-- Statistical Anomaly Detection
WITH daily_metrics AS (
    SELECT
        DATE(order_date) as date,
        COUNT(*) as order_count,
        AVG(amount) as avg_amount,
        STDDEV(amount) as stddev_amount
    FROM orders
    WHERE order_date >= CURRENT_DATE - 30
    GROUP BY DATE(order_date)
),
baseline AS (
    SELECT
        AVG(order_count) as avg_orders,
        STDDEV(order_count) as stddev_orders,
        AVG(avg_amount) as avg_avg_amount,
        STDDEV(avg_amount) as stddev_avg_amount
    FROM daily_metrics
    WHERE date < CURRENT_DATE
)
SELECT
    dm.date,
    dm.order_count,
    b.avg_orders,
    -- Flag if more than 3 standard deviations from mean
    CASE
        WHEN ABS(dm.order_count - b.avg_orders) > 3 * b.stddev_orders
        THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as order_count_status,
    dm.avg_amount,
    CASE
        WHEN ABS(dm.avg_amount - b.avg_avg_amount) > 3 * b.stddev_avg_amount
        THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as avg_amount_status
FROM daily_metrics dm
CROSS JOIN baseline b
WHERE dm.date = CURRENT_DATE;
```

### Pattern 4: Schema Evolution Detection
```sql
-- Track schema changes
CREATE TABLE quality.schema_history (
    table_name VARCHAR(255),
    column_name VARCHAR(255),
    data_type VARCHAR(50),
    is_nullable BOOLEAN,
    column_default VARCHAR(255),
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detect new columns
INSERT INTO quality.schema_history
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable = 'YES' as is_nullable,
    column_default,
    CURRENT_TIMESTAMP
FROM information_schema.columns
WHERE table_schema = 'analytics'
  AND (table_name, column_name) NOT IN (
      SELECT table_name, column_name
      FROM quality.schema_history
  );

-- Alert on schema changes
SELECT
    table_name,
    column_name,
    data_type,
    discovered_at
FROM quality.schema_history
WHERE discovered_at > CURRENT_TIMESTAMP - INTERVAL '1 day'
ORDER BY discovered_at DESC;
```

## Airflow Integration

### Quality Check DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

def run_great_expectations():
    import great_expectations as gx
    context = gx.get_context()
    result = context.run_checkpoint(checkpoint_name="daily_validation")
    if not result["success"]:
        raise ValueError("Data quality checks failed")

with DAG(
    'data_quality_checks',
    default_args={
        'owner': 'data_team',
        'depends_on_past': False,
        'email_on_failure': True,
        'email': ['data-alerts@company.com'],
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Daily data quality validation',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # dbt tests
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /dbt && dbt test --target prod',
    )

    # Great Expectations
    ge_validation = PythonOperator(
        task_id='great_expectations_validation',
        python_callable=run_great_expectations,
    )

    # Custom SQL checks
    reconciliation_check = PostgresOperator(
        task_id='reconciliation_check',
        sql='sql/reconciliation_checks.sql',
        postgres_conn_id='postgres_prod',
    )

    # Quality metrics
    capture_metrics = PostgresOperator(
        task_id='capture_quality_metrics',
        sql='''
            INSERT INTO quality.daily_metrics
            SELECT
                CURRENT_DATE as check_date,
                table_name,
                check_name,
                check_value,
                CASE WHEN check_value > threshold THEN 'FAIL' ELSE 'PASS' END
            FROM quality.run_all_checks();
        ''',
        postgres_conn_id='postgres_prod',
    )

    dbt_test >> ge_validation >> reconciliation_check >> capture_metrics
```

## Monitoring Dashboard

### Quality Metrics Table
```sql
CREATE TABLE quality.metrics (
    id SERIAL PRIMARY KEY,
    check_date DATE NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC,
    threshold_value NUMERIC,
    status VARCHAR(20),  -- PASS, WARN, FAIL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality score view
CREATE VIEW quality.quality_score AS
SELECT
    table_name,
    DATE(check_date) as date,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as passed_checks,
    ROUND(100.0 * SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) / COUNT(*), 2) as quality_score
FROM quality.metrics
WHERE check_date >= CURRENT_DATE - 30
GROUP BY table_name, DATE(check_date)
ORDER BY date DESC, table_name;
```

## Best Practices

1. **Test at Multiple Layers**: Raw, staging, and marts
2. **Automate All Checks**: Integrate with CI/CD and orchestration
3. **Monitor Trends**: Track quality metrics over time
4. **Set Clear Thresholds**: Define PASS/WARN/FAIL criteria
5. **Document Expectations**: Make quality requirements explicit
6. **Fail Fast**: Catch issues early in the pipeline
7. **Reconcile Regularly**: Verify source-to-target accuracy
8. **Version Quality Rules**: Track changes to quality definitions

## Resources

- **dbt Testing**: https://docs.getdbt.com/docs/building-a-dbt-project/tests
- **Great Expectations**: https://docs.greatexpectations.io/
- **Soda Core**: https://docs.soda.io/
- **dbt-utils**: https://hub.getdbt.com/dbt-labs/dbt_utils/
