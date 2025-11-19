# Incremental Loading Strategies Reference

## Overview
Incremental loading extracts only changed data since the last load, dramatically improving efficiency compared to full refreshes.

## Strategy Comparison

| Strategy | Detects | Performance | Complexity | Deletes | Best For |
|----------|---------|-------------|------------|---------|----------|
| **Timestamp** | Inserts, Updates | Excellent | Low | ❌ | Most tables |
| **Auto-incrementing ID** | Inserts | Excellent | Low | ❌ | Append-only logs |
| **CDC (Log-based)** | All changes | Excellent | High | ✅ | Critical data |
| **Hash/Checksum** | Updates | Poor | Medium | ❌ | Small tables |
| **Trigger-based** | All changes | Good | High | ✅ | Legacy systems |
| **Version columns** | Updates | Excellent | Low | ❌ | Version-tracked tables |
| **Partition-based** | By partition | Excellent | Low | ❌ | Time-series data |

## Timestamp-Based Incremental

### Basic Pattern
```sql
-- dbt incremental model
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

SELECT
    id,
    customer_id,
    order_date,
    amount,
    updated_at
FROM {{ source('ecommerce', 'orders') }}

{% if is_incremental() %}
    -- Only load records updated since last run
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### With Buffer/Lookback Window
```sql
-- Include 2-hour lookback to catch late-arriving updates
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

SELECT *
FROM {{ source('ecommerce', 'orders') }}

{% if is_incremental() %}
    WHERE updated_at > (
        SELECT DATEADD(hour, -2, MAX(updated_at))
        FROM {{ this }}
    )
{% endif %}
```

### Multiple Timestamp Columns
```sql
-- Check both created and updated timestamps
{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
       OR created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Partition-Aware Incremental
```sql
-- BigQuery partitioned table
{{ config(
    materialized='incremental',
    unique_key='id',
    partition_by={
        'field': 'order_date',
        'data_type': 'date',
        'granularity': 'day'
    },
    cluster_by=['customer_id', 'status']
) }}

SELECT *
FROM {{ source('ecommerce', 'orders') }}

{% if is_incremental() %}
    -- Only scan recent partitions
    WHERE order_date > _dbt_max_partition
{% endif %}
```

## Auto-Incrementing ID Strategy

### Sequential ID Pattern
```sql
-- Efficient for append-only tables
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

SELECT
    id,
    event_name,
    user_id,
    event_timestamp,
    properties
FROM {{ source('events', 'user_events') }}

{% if is_incremental() %}
    WHERE id > (SELECT COALESCE(MAX(id), 0) FROM {{ this }})
{% endif %}
ORDER BY id  -- Important for efficient processing
```

### Composite Key (ID + Timestamp)
```sql
-- Use both for reliability
{% if is_incremental() %}
    WHERE id > (SELECT MAX(id) FROM {{ this }})
       OR (id = (SELECT MAX(id) FROM {{ this }})
           AND created_at > (SELECT MAX(created_at) FROM {{ this }}))
{% endif %}
```

## CDC-Based Incremental

### Using Airbyte CDC
```sql
-- dbt model on Airbyte raw table
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

WITH cdc_data AS (
    SELECT
        (_airbyte_data::json->>'id')::BIGINT as id,
        (_airbyte_data::json->>'customer_id')::BIGINT as customer_id,
        (_airbyte_data::json->>'status')::VARCHAR as status,
        (_airbyte_data::json->>'amount')::DECIMAL as amount,
        _airbyte_emitted_at,
        -- CDC metadata
        CASE _airbyte_data::json->>'_ab_cdc_deleted_at'
            WHEN NULL THEN FALSE
            ELSE TRUE
        END as is_deleted
    FROM {{ source('airbyte', '_airbyte_raw_orders') }}

    {% if is_incremental() %}
        WHERE _airbyte_emitted_at > (SELECT MAX(_airbyte_emitted_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM cdc_data WHERE NOT is_deleted
```

### Handling CDC Deletes
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    on_schema_change='sync_all_columns'
) }}

-- Merge strategy to handle deletes
{% if is_incremental() %}

    -- Delete removed records
    DELETE FROM {{ this }}
    WHERE id IN (
        SELECT id FROM {{ source('cdc', 'orders_changes') }}
        WHERE operation = 'DELETE'
          AND cdc_timestamp > (SELECT MAX(updated_at) FROM {{ this }})
    );

    -- Upsert changed records
    MERGE INTO {{ this }} target
    USING (
        SELECT * FROM {{ source('cdc', 'orders_changes') }}
        WHERE operation IN ('INSERT', 'UPDATE')
          AND cdc_timestamp > (SELECT MAX(updated_at) FROM {{ this }})
    ) source
    ON target.id = source.id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *;

{% else %}
    SELECT * FROM {{ source('ecommerce', 'orders') }}
{% endif %}
```

## Hash-Based Change Detection

### MD5 Checksum Pattern
```sql
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

WITH source_data AS (
    SELECT
        id,
        customer_id,
        status,
        amount,
        -- Hash of business columns
        MD5(CONCAT(
            COALESCE(customer_id::VARCHAR, ''),
            COALESCE(status, ''),
            COALESCE(amount::VARCHAR, '')
        )) as row_hash,
        updated_at
    FROM {{ source('ecommerce', 'orders') }}

    {% if is_incremental() %}
        WHERE updated_at >= (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
)

{% if is_incremental() %}
    -- Only include records where hash changed
    SELECT s.*
    FROM source_data s
    LEFT JOIN {{ this }} t ON s.id = t.id
    WHERE t.row_hash IS NULL
       OR s.row_hash != t.row_hash
{% else %}
    SELECT * FROM source_data
{% endif %}
```

### Snowflake Hash Diff
```sql
WITH source_with_hash AS (
    SELECT
        *,
        HASH(*) as row_hash  -- Snowflake HASH function on all columns
    FROM {{ source('ecommerce', 'orders') }}
    WHERE updated_at >= CURRENT_DATE - 7  -- 7-day lookback
),
target_hashes AS (
    SELECT id, row_hash
    FROM {{ this }}
    WHERE updated_at >= CURRENT_DATE - 7
)
SELECT s.*
FROM source_with_hash s
LEFT JOIN target_hashes t ON s.id = t.id
WHERE t.row_hash IS NULL OR s.row_hash != t.row_hash
```

## Partition-Based Incremental

### Date Partition Strategy
```sql
-- Load only recent date partitions
{{ config(
    materialized='incremental',
    unique_key='id',
    partition_by={
        'field': 'event_date',
        'data_type': 'date'
    }
) }}

SELECT
    id,
    event_name,
    user_id,
    DATE(event_timestamp) as event_date,
    event_timestamp
FROM {{ source('events', 'user_events') }}

{% if is_incremental() %}
    -- Only load last 3 days (captures late data)
    WHERE DATE(event_timestamp) >= CURRENT_DATE - 3
{% endif %}
```

### Delete and Reload Partition
```sql
-- BigQuery specific: replace partition strategy
{{ config(
    materialized='incremental',
    unique_key='event_date',
    partition_by={
        'field': 'event_date',
        'data_type': 'date'
    },
    incremental_strategy='insert_overwrite'  -- Replace partitions
) }}

SELECT *
FROM {{ source('events', 'user_events') }}

{% if is_incremental() %}
    WHERE event_date IN (
        -- Reload last 7 days of partitions
        SELECT DISTINCT event_date
        FROM UNNEST(GENERATE_DATE_ARRAY(CURRENT_DATE - 7, CURRENT_DATE)) as event_date
    )
{% endif %}
```

## Incremental Strategies by Warehouse

### Snowflake: Merge Strategy
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge',
    merge_update_columns=['status', 'amount', 'updated_at']
) }}

-- Snowflake will generate:
-- MERGE INTO target USING source ON target.id = source.id
-- WHEN MATCHED THEN UPDATE SET status = source.status, ...
-- WHEN NOT MATCHED THEN INSERT ...
```

### BigQuery: Merge Strategy
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge',
    merge_exclude_columns=['created_at']  -- Don't update these
) }}

-- BigQuery optimizations
{{ config(
    partition_by={
        'field': 'created_date',
        'data_type': 'date'
    },
    cluster_by=['customer_id', 'status'],
    require_partition_filter=true
) }}
```

### Redshift: Delete+Insert Strategy
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='delete+insert',
    dist_key='customer_id',
    sort_key=['created_at']
) }}

-- Redshift will:
-- 1. DELETE FROM target WHERE id IN (SELECT id FROM source)
-- 2. INSERT INTO target SELECT * FROM source
```

### Postgres: Append Strategy
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='append',
    indexes=[
        {'columns': ['customer_id']},
        {'columns': ['created_at']}
    ]
) }}

-- Simple INSERT (no deduplication)
-- Use when source is guaranteed unique
```

## Complex Incremental Patterns

### Multi-Source Incremental
```sql
{{ config(
    materialized='incremental',
    unique_key=['source_system', 'source_id']
) }}

WITH combined_sources AS (
    -- Source 1: Database
    SELECT
        'postgres' as source_system,
        id as source_id,
        customer_id,
        amount,
        updated_at
    FROM {{ source('postgres', 'orders') }}
    {% if is_incremental() %}
        WHERE updated_at > (
            SELECT MAX(updated_at)
            FROM {{ this }}
            WHERE source_system = 'postgres'
        )
    {% endif %}

    UNION ALL

    -- Source 2: API
    SELECT
        'shopify' as source_system,
        order_id as source_id,
        customer_id,
        total as amount,
        updated_at
    FROM {{ source('shopify', 'orders') }}
    {% if is_incremental() %}
        WHERE updated_at > (
            SELECT MAX(updated_at)
            FROM {{ this }}
            WHERE source_system = 'shopify'
        )
    {% endif %}
)

SELECT * FROM combined_sources
```

### SCD Type 2 Incremental
```sql
{{ config(
    materialized='incremental',
    unique_key='surrogate_key'
) }}

WITH source_data AS (
    SELECT
        id,
        customer_id,
        email,
        name,
        updated_at
    FROM {{ source('crm', 'customers') }}
    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(valid_from) FROM {{ this }})
    {% endif %}
),

{% if is_incremental() %}
    -- Close out existing current records
    updates AS (
        UPDATE {{ this }} SET
            valid_to = s.updated_at,
            is_current = FALSE
        FROM source_data s
        WHERE {{ this }}.id = s.id
          AND {{ this }}.is_current = TRUE
          AND (
              {{ this }}.email != s.email OR
              {{ this }}.name != s.name
          )
    ),
{% endif %}

new_records AS (
    SELECT
        {{ dbt_utils.surrogate_key(['id', 'updated_at']) }} as surrogate_key,
        id,
        customer_id,
        email,
        name,
        updated_at as valid_from,
        NULL as valid_to,
        TRUE as is_current
    FROM source_data
)

SELECT * FROM new_records
```

### Incremental with Late-Arriving Dimensions
```sql
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

WITH fact_data AS (
    SELECT
        order_id,
        customer_id,
        product_id,
        amount,
        order_date
    FROM {{ source('sales', 'orders') }}
    {% if is_incremental() %}
        WHERE order_date >= CURRENT_DATE - 30  -- 30-day lookback
    {% endif %}
),

-- Enrich with dimensions (may arrive late)
enriched AS (
    SELECT
        f.order_id,
        COALESCE(c.customer_key, -1) as customer_key,  -- Unknown key
        COALESCE(p.product_key, -1) as product_key,
        f.amount,
        f.order_date
    FROM fact_data f
    LEFT JOIN {{ ref('dim_customers') }} c
        ON f.customer_id = c.customer_id
        AND f.order_date BETWEEN c.valid_from AND COALESCE(c.valid_to, '9999-12-31')
    LEFT JOIN {{ ref('dim_products') }} p
        ON f.product_id = p.product_id
)

SELECT * FROM enriched
```

## Performance Optimization

### Batch Processing
```sql
-- Process in daily batches for very large tables
{{ config(
    materialized='incremental',
    unique_key='id'
) }}

{% if is_incremental() %}
    {% set last_load_date = run_query("SELECT MAX(DATE(loaded_at)) FROM " ~ this) %}
    {% set dates_to_load = dbt_utils.get_date_array(last_load_date, 'CURRENT_DATE') %}

    {% for batch_date in dates_to_load %}
        SELECT *
        FROM {{ source('events', 'user_events') }}
        WHERE DATE(event_timestamp) = '{{ batch_date }}'

        {% if not loop.last %}UNION ALL{% endif %}
    {% endfor %}
{% else %}
    SELECT * FROM {{ source('events', 'user_events') }}
{% endif %}
```

### Parallel Incremental Loads
```python
# Airflow dynamic task generation
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(schedule_interval='@daily', start_date=datetime(2024, 1, 1))
def incremental_loads():

    @task
    def get_tables_to_load():
        return ['orders', 'customers', 'products', 'inventory']

    @task
    def load_incremental(table_name: str):
        """Run dbt for specific model"""
        import subprocess
        subprocess.run([
            'dbt', 'run',
            '--models', f'staging.stg_{table_name}',
            '--target', 'prod'
        ], check=True)

    tables = get_tables_to_load()
    load_incremental.expand(table_name=tables)

dag = incremental_loads()
```

## Error Handling & Recovery

### Checkpoint Table Pattern
```sql
-- Track successful loads
CREATE TABLE etl.load_checkpoints (
    table_name VARCHAR(255),
    last_successful_load TIMESTAMP,
    last_loaded_id BIGINT,
    last_loaded_timestamp TIMESTAMP,
    rows_loaded BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Use checkpoint in incremental logic
{% set checkpoint = run_query(
    "SELECT last_loaded_timestamp FROM etl.load_checkpoints WHERE table_name = 'orders'"
) %}

SELECT *
FROM {{ source('ecommerce', 'orders') }}
WHERE updated_at > '{{ checkpoint.rows[0][0] if checkpoint else '1970-01-01' }}'
```

### Idempotent Incremental
```sql
-- Safe to re-run for same date
{% if is_incremental() %}
    -- Delete data for reload window first
    DELETE FROM {{ this }}
    WHERE event_date >= CURRENT_DATE - 7;

    -- Then insert fresh data
    INSERT INTO {{ this }}
    SELECT *
    FROM {{ source('events', 'user_events') }}
    WHERE event_date >= CURRENT_DATE - 7;
{% endif %}
```

## Monitoring & Validation

### Incremental Load Metrics
```sql
-- Track incremental load performance
CREATE VIEW etl.incremental_load_metrics AS
WITH load_stats AS (
    SELECT
        model_name,
        run_started_at,
        rows_affected,
        execution_time,
        LAG(run_started_at) OVER (PARTITION BY model_name ORDER BY run_started_at) as previous_run,
        LAG(rows_affected) OVER (PARTITION BY model_name ORDER BY run_started_at) as previous_rows
    FROM dbt_run_results
    WHERE materialization = 'incremental'
)
SELECT
    model_name,
    run_started_at,
    EXTRACT(EPOCH FROM (run_started_at - previous_run)) / 3600 as hours_since_last_run,
    rows_affected,
    rows_affected - COALESCE(previous_rows, 0) as row_delta,
    execution_time,
    ROUND(rows_affected::NUMERIC / NULLIF(execution_time, 0), 2) as rows_per_second
FROM load_stats;
```

### Data Freshness Check
```sql
-- Alert on stale incremental models
SELECT
    table_name,
    MAX(updated_at) as last_record_update,
    CURRENT_TIMESTAMP - MAX(updated_at) as data_age,
    CASE
        WHEN CURRENT_TIMESTAMP - MAX(updated_at) > INTERVAL '2 hours'
        THEN 'STALE'
        ELSE 'FRESH'
    END as freshness_status
FROM analytics.incremental_models
GROUP BY table_name
HAVING CURRENT_TIMESTAMP - MAX(updated_at) > INTERVAL '2 hours';
```

## Best Practices Checklist

- [ ] Use timestamp columns with indexes for efficiency
- [ ] Include lookback window to catch late-arriving data
- [ ] Implement idempotent logic (safe to re-run)
- [ ] Choose appropriate `unique_key` for deduplication
- [ ] Set `on_schema_change` strategy
- [ ] Monitor incremental load performance
- [ ] Test full refresh vs incremental results match
- [ ] Document incremental logic in model description
- [ ] Handle edge cases (nulls, timezone issues)
- [ ] Set up freshness alerts
- [ ] Use appropriate incremental strategy for your warehouse
- [ ] Consider partition pruning for cost optimization

## Resources

- **dbt Incremental Models**: https://docs.getdbt.com/docs/build/incremental-models
- **dbt Incremental Strategies**: https://docs.getdbt.com/docs/build/incremental-strategy
- **Discourse on Incremental Models**: https://discourse.getdbt.com/tag/incremental
