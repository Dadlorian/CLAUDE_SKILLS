{{
    config(
        materialized='table',
        tags=['dimension', 'core', 'daily']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

customer_orders AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
)

SELECT
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['customers.customer_id']) }} AS customer_key,

    -- Natural key
    customers.customer_id,

    -- Attributes
    customers.first_name,
    customers.last_name,
    customers.first_name || ' ' || customers.last_name AS full_name,
    customers.email,
    customers.phone,
    customers.address,
    customers.city,
    customers.state,
    customers.zip_code,
    customers.country,

    -- Metrics from orders
    COALESCE(customer_orders.lifetime_orders, 0) AS lifetime_orders,
    COALESCE(customer_orders.lifetime_value, 0) AS lifetime_value,
    COALESCE(customer_orders.avg_order_value, 0) AS avg_order_value,
    customer_orders.first_order_date,
    customer_orders.last_order_date,

    -- Derived attributes
    CASE
        WHEN customer_orders.lifetime_value >= 10000 THEN 'VIP'
        WHEN customer_orders.lifetime_value >= 1000 THEN 'Regular'
        WHEN customer_orders.lifetime_value > 0 THEN 'Casual'
        ELSE 'Never Purchased'
    END AS customer_segment,

    DATEDIFF('day', customer_orders.last_order_date, CURRENT_DATE) AS days_since_last_order,

    -- Metadata
    customers.created_at,
    CURRENT_TIMESTAMP AS dbt_updated_at

FROM customers
LEFT JOIN customer_orders USING (customer_id)
