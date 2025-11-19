{{
    config(
        materialized='ephemeral',
        tags=['intermediate']
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customer_metrics AS (
    SELECT
        customer_id,
        COUNT(*) AS lifetime_orders,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS avg_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        MAX(created_at) AS last_updated_at

    FROM orders
    GROUP BY customer_id
)

SELECT * FROM customer_metrics
