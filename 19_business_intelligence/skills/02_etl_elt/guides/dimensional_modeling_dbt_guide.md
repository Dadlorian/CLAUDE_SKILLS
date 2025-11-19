# Dimensional Modeling in dbt Guide

## Kimball Dimensional Modeling

### Star Schema Components

**Fact Tables**: Measurable events (orders, transactions)
**Dimension Tables**: Descriptive attributes (customers, products, time)

## Building Dimensions in dbt

### Dimension Table Example
```sql
-- models/marts/core/dim_customers.sql
{{
    config(
        materialized='table',
        tags=['dimension']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

customer_metrics AS (
    SELECT
        customer_id,
        COUNT(*) as lifetime_orders,
        SUM(amount) as lifetime_value,
        MIN(order_date) as first_order_date
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
)

SELECT
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['customers.customer_id']) }} as customer_key,

    -- Natural key
    customers.customer_id,

    -- Attributes
    customers.first_name,
    customers.last_name,
    customers.email,
    customers.country,

    -- Derived attributes
    CASE
        WHEN customer_metrics.lifetime_value > 10000 THEN 'VIP'
        WHEN customer_metrics.lifetime_value > 1000 THEN 'Regular'
        ELSE 'Casual'
    END as customer_segment,

    -- Metrics
    COALESCE(customer_metrics.lifetime_orders, 0) as lifetime_orders,
    COALESCE(customer_metrics.lifetime_value, 0) as lifetime_value,

    -- Metadata
    customers.created_at,
    CURRENT_TIMESTAMP as dbt_updated_at

FROM customers
LEFT JOIN customer_metrics USING (customer_id)
```

### Fact Table Example
```sql
-- models/marts/core/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_key',
        tags=['fact']
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT customer_key, customer_id
    FROM {{ ref('dim_customers') }}
),

products AS (
    SELECT product_key, product_id
    FROM {{ ref('dim_products') }}
)

SELECT
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['orders.order_id']) }} as order_key,

    -- Foreign keys to dimensions
    customers.customer_key,
    products.product_key,
    DATE(orders.order_date) as order_date_key,

    -- Degenerate dimensions
    orders.order_id,
    orders.order_number,

    -- Measures
    orders.quantity,
    orders.unit_price,
    orders.discount_amount,
    orders.tax_amount,
    orders.total_amount,

    -- Metadata
    orders.created_at,
    orders.updated_at

FROM orders
LEFT JOIN customers ON orders.customer_id = customers.customer_id
LEFT JOIN products ON orders.product_id = products.product_id
```

## Slowly Changing Dimensions

### Type 1 (Overwrite)
```sql
-- Latest values only, no history
UPDATE dim_customers
SET email = new_email
WHERE customer_id = 123
```

### Type 2 (Add Row)
```sql
-- models/marts/core/dim_customers_scd2.sql
{{
    config(
        materialized='incremental',
        unique_key='customer_key'
    )
}}

WITH current_records AS (
    SELECT *
    FROM {{ ref('stg_customers') }}
),

historical AS (
    SELECT *
    FROM {{ this }}
    WHERE is_current = TRUE
),

changes AS (
    SELECT
        c.*,
        CASE
            WHEN h.customer_id IS NULL THEN 'INSERT'
            WHEN c.email != h.email OR c.address != h.address THEN 'UPDATE'
            ELSE 'NO_CHANGE'
        END as change_type
    FROM current_records c
    LEFT JOIN historical h ON c.customer_id = h.customer_id
)

-- Close out changed records
SELECT
    customer_key,
    customer_id,
    email,
    address,
    valid_from,
    CURRENT_TIMESTAMP as valid_to,
    FALSE as is_current
FROM historical
WHERE customer_id IN (SELECT customer_id FROM changes WHERE change_type = 'UPDATE')

UNION ALL

-- Insert new versions
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id', 'CURRENT_TIMESTAMP']) }} as customer_key,
    customer_id,
    email,
    address,
    CURRENT_TIMESTAMP as valid_from,
    NULL as valid_to,
    TRUE as is_current
FROM changes
WHERE change_type IN ('INSERT', 'UPDATE')
```

### Type 2 with dbt Snapshots
```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

SELECT * FROM {{ source('postgres', 'customers') }}

{% endsnapshot %}
```

## Date Dimension
```sql
-- models/marts/core/dim_date.sql
{{
    config(
        materialized='table'
    )
}}

WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2030-12-31' as date)"
    ) }}
)

SELECT
    DATE(date_day) as date_key,
    date_day,
    EXTRACT(YEAR FROM date_day) as year,
    EXTRACT(QUARTER FROM date_day) as quarter,
    EXTRACT(MONTH FROM date_day) as month,
    EXTRACT(DAY FROM date_day) as day,
    EXTRACT(DAYOFWEEK FROM date_day) as day_of_week,
    EXTRACT(DAYOFYEAR FROM date_day) as day_of_year,
    CASE WHEN EXTRACT(DAYOFWEEK FROM date_day) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend,
    TO_CHAR(date_day, 'Month') as month_name,
    TO_CHAR(date_day, 'Day') as day_name
FROM date_spine
```

## Best Practices

1. **Surrogate Keys**: Generate unique keys, don't use natural keys
2. **Type 2 for History**: Use snapshots or manual SCD2
3. **Denormalize**: Trade storage for query performance
4. **Date Dimensions**: Pre-build date dimensions
5. **Fact Grain**: Choose appropriate level of detail

