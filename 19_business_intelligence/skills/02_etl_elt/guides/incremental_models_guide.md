# Incremental Models in dbt: Complete Guide

## What Are Incremental Models?

Incremental models only process new or changed data since the last run, dramatically improving performance for large tables.

### When to Use Incremental Models
- Large fact tables (millions+ rows)
- Event/log data that only grows
- Tables with reliable update timestamps
- Long-running transformations

### When NOT to Use
- Small dimension tables (<100K rows)
- Tables without update timestamps
- Rapidly changing data requiring full refresh

## Basic Incremental Model

```sql
-- models/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='sync_all_columns'
    )
}}

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    updated_at
FROM {{ source('ecommerce', 'orders') }}

{% if is_incremental() %}
    -- Only process records updated since last run
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

## Configuration Options

### unique_key
```sql
-- Single column
{{ config(unique_key='id') }}

-- Multiple columns (composite key)
{{ config(unique_key=['customer_id', 'order_date']) }}

-- Expression
{{ config(unique_key="date_trunc('day', created_at)") }}
```

### on_schema_change
```sql
{{ config(
    on_schema_change='sync_all_columns'  -- Default: Add new columns
    -- or 'append_new_columns'            -- Only add, don't remove
    -- or 'fail'                          -- Fail on schema change
    -- or 'ignore'                        -- Ignore schema changes
) }}
```

## Incremental Strategies

### Merge (Default for most warehouses)
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge'
) }}

-- Behavior:
-- UPDATE rows where key matches
-- INSERT rows where key doesn't match
-- Good for: SCD Type 1 dimensions, fact tables with updates
```

### Delete+Insert
```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='delete+insert'
) }}

-- Behavior:
-- DELETE rows with matching keys
-- INSERT all new rows
-- Good for: Redshift, when merge is slow
```

### Append (No Deduplication)
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

-- Behavior:
-- INSERT all new rows (no updates/deletes)
-- Good for: Immutable event logs, guaranteed unique data
```

### Insert_Overwrite (BigQuery)
```sql
{{ config(
    materialized='incremental',
    unique_key='date',
    incremental_strategy='insert_overwrite',
    partition_by={'field': 'date', 'data_type': 'date'}
) }}

-- Behavior:
-- Replaces entire partitions
-- Good for: Daily aggregations, partitioned tables
```

## Advanced Patterns

### Lookback Window
```sql
-- Process last 7 days to catch late-arriving data
{% if is_incremental() %}
    WHERE updated_at > (
        SELECT DATEADD(day, -7, MAX(updated_at))
        FROM {{ this }}
    )
{% endif %}
```

### Multiple Timestamp Columns
```sql
{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
       OR created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Incremental with Partitions
```sql
{{ config(
    materialized='incremental',
    partition_by={'field': 'event_date', 'data_type': 'date'},
    cluster_by=['user_id', 'event_type'],
    incremental_strategy='insert_overwrite'
) }}

SELECT *
FROM {{ source('events', 'user_events') }}

{% if is_incremental() %}
    WHERE event_date >= _dbt_max_partition
{% endif %}
```

## Testing Incremental Models

### Validate Full Refresh Matches Incremental
```bash
# Run full refresh
dbt run --models fct_orders --full-refresh

# Save results
dbt run-operation save_results --args '{model: "fct_orders", alias: "full_refresh"}'

# Run incremental (after data changes)
dbt run --models fct_orders

# Compare results
SELECT COUNT(*) FROM fct_orders
EXCEPT
SELECT COUNT(*) FROM fct_orders_full_refresh
-- Should return 0 rows
```

### Test Idempotency
```bash
# Run twice, results should match
dbt run --models fct_orders
dbt run --models fct_orders

# Check for duplicates
SELECT order_id, COUNT(*)
FROM fct_orders
GROUP BY order_id
HAVING COUNT(*) > 1
-- Should return 0 rows
```

## Common Issues & Solutions

### Issue: Duplicates in Incremental Table
**Cause**: unique_key not configured or incorrect
```sql
-- Solution: Set proper unique_key
{{ config(unique_key='order_id') }}
```

### Issue: Missing Recent Data
**Cause**: Timestamp filter too restrictive
```sql
-- Solution: Add lookback window
WHERE updated_at > (
    SELECT DATEADD(hour, -2, MAX(updated_at))
    FROM {{ this }}
)
```

### Issue: Schema Drift
**Cause**: Source schema changed
```sql
-- Solution: Set on_schema_change
{{ config(on_schema_change='sync_all_columns') }}

-- Or run full refresh
dbt run --models fct_orders --full-refresh
```

## Best Practices

1. **Always set unique_key** for deduplication
2. **Use lookback windows** for late-arriving data
3. **Test both incremental and full refresh** match
4. **Monitor run times** - should be much faster
5. **Full refresh periodically** (weekly/monthly)
6. **Document incremental logic** in model description

## Resources

- **dbt Docs**: https://docs.getdbt.com/docs/build/incremental-models
- **Incremental Strategies**: https://docs.getdbt.com/docs/build/incremental-strategy
