{{
    config(
        materialized='ephemeral'
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

enriched_orders AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.product_id,
        p.product_name,
        p.category,
        o.quantity,
        o.unit_price,
        o.total_amount,
        (o.unit_price - p.cost) * o.quantity AS gross_margin

    FROM orders o
    LEFT JOIN products p ON o.product_id = p.product_id
)

SELECT * FROM enriched_orders
