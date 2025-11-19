# Building Data Pipelines Guide

## Pipeline Architecture

```
┌──────────────┐
│   Sources    │ (Databases, APIs, Files)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Extraction  │ (Airbyte, Fivetran, Custom)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Raw Storage  │ (Data Lake/Warehouse)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Transformation│ (dbt)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Analytics   │ (BI Tools, ML)
└──────────────┘

Orchestrated by: Airflow/dbt Cloud
Quality: Great Expectations/dbt tests
```

## Step-by-Step Pipeline

### 1. Define Requirements
- Data sources needed
- Update frequency
- Data freshness SLAs
- Business logic rules
- Quality requirements

### 2. Set Up Extraction
```yaml
# Airbyte connection
source: postgres_prod
destination: snowflake_raw
sync_mode: incremental_cdc
schedule: hourly
```

### 3. Build dbt Models

**Staging Layer**:
```sql
-- models/staging/stg_orders.sql
SELECT
    id as order_id,
    customer_id,
    order_date,
    amount,
    status
FROM {{ source('postgres', 'orders') }}
```

**Intermediate Layer**:
```sql
-- models/intermediate/int_customer_orders.sql
SELECT
    customer_id,
    COUNT(*) as total_orders,
    SUM(amount) as lifetime_value
FROM {{ ref('stg_orders') }}
GROUP BY customer_id
```

**Marts Layer**:
```sql
-- models/marts/dim_customers.sql
SELECT
    c.*,
    o.total_orders,
    o.lifetime_value
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('int_customer_orders') }} o
USING (customer_id)
```

### 4. Add Quality Tests
```yaml
# models/schema.yml
models:
  - name: dim_customers
    tests:
      - dbt_utils.equal_rowcount:
          compare_model: source('postgres', 'customers')
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
```

### 5. Orchestrate with Airflow
```python
with DAG('customer_pipeline', ...) as dag:
    extract = BashOperator(
        task_id='trigger_airbyte_sync',
        bash_command='airbyte sync --connection-id abc123'
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --models +dim_customers'
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --models dim_customers'
    )

    extract >> dbt_run >> dbt_test
```

### 6. Monitor and Alert
```python
def send_failure_alert(context):
    # Send Slack/email alert
    pass

task = BashOperator(
    task_id='dbt_run',
    bash_command='dbt run',
    on_failure_callback=send_failure_alert
)
```

## Best Practices

1. **Start Simple**: Build incrementally
2. **Test Early**: Add tests from the start
3. **Document**: Explain business logic
4. **Monitor**: Track performance and failures
5. **Version Control**: Git for all code
6. **Modular Design**: Reusable components

