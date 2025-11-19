{{
    config(
        materialized='incremental',
        unique_key='order_key',
        on_schema_change='sync_all_columns',
        tags=['fact', 'core', 'daily']
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
    SELECT product_id, product_name, category, cost
    FROM {{ ref('stg_products') }}
)

SELECT
    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key(['orders.order_id']) }} AS order_key,

    -- Foreign keys
    customers.customer_key,
    DATE(orders.order_date) AS order_date_key,

    -- Degenerate dimensions
    orders.order_id,
    orders.order_number,
    orders.product_id,
    products.product_name,
    products.category,

    -- Measures
    orders.quantity,
    orders.unit_price,
    orders.discount_amount,
    orders.tax_amount,
    orders.total_amount,

    -- Calculated measures
    (orders.unit_price - products.cost) * orders.quantity AS gross_margin,
    orders.total_amount - orders.discount_amount - orders.tax_amount AS net_revenue,

    -- Status
    orders.status,

    -- Metadata
    orders.created_at,
    orders.updated_at

FROM orders
LEFT JOIN customers ON orders.customer_id = customers.customer_id
LEFT JOIN products ON orders.product_id = products.product_id
