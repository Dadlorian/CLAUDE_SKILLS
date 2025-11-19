-- dbt Models Examples for Data Warehouse
-- Description: Production-ready dbt models for dimensional modeling
-- Includes: Staging, Intermediate, Fact, and Dimension models

-- ============================================
-- STAGING MODELS
-- ============================================

-- models/staging/stg_customers.sql
-- {{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('ecommerce', 'raw_customers') }}
),

renamed AS (
    SELECT
        -- Primary Key
        id AS customer_id,

        -- Attributes
        first_name || ' ' || last_name AS customer_name,
        email,
        phone,
        segment AS customer_segment,
        tier AS customer_tier,

        -- Address
        country,
        state,
        city,
        postal_code,

        -- Metadata
        created_at,
        updated_at,
        _fivetran_synced AS last_synced_at

    FROM source
)

SELECT * FROM renamed;

-- ============================================

-- models/staging/stg_orders.sql
-- {{ config(
--     materialized='incremental',
--     unique_key='order_id',
--     on_schema_change='fail'
-- ) }}

WITH source AS (
    SELECT * FROM {{ source('ecommerce', 'raw_orders') }}

    {% if is_incremental() %}
        -- Only load new/updated records on incremental runs
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

renamed AS (
    SELECT
        -- Primary Key
        id AS order_id,

        -- Foreign Keys
        customer_id,

        -- Attributes
        order_number,
        status AS order_status,
        payment_method,
        shipping_method,

        -- Amounts
        subtotal_amount,
        discount_amount,
        tax_amount,
        shipping_amount,
        total_amount,

        -- Dates
        order_date,
        payment_date,
        shipped_date,
        delivered_date,
        cancelled_date,

        -- Metadata
        created_at,
        updated_at

    FROM source
)

SELECT * FROM renamed;

-- ============================================

-- models/staging/stg_order_items.sql
-- {{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('ecommerce', 'raw_order_items') }}
),

renamed AS (
    SELECT
        -- Composite Key
        order_id,
        line_number,

        -- Foreign Keys
        product_id,

        -- Measures
        quantity,
        unit_price,
        discount_percentage,
        discount_amount,
        line_total,

        -- Metadata
        created_at

    FROM source
)

SELECT * FROM renamed;

-- ============================================
-- INTERMEDIATE MODELS
-- ============================================

-- models/intermediate/int_orders_enriched.sql
-- {{ config(materialized='ephemeral') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

order_aggregates AS (
    SELECT
        oi.order_id,
        COUNT(DISTINCT oi.product_id) AS product_count,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.line_total) AS items_total,
        COUNT(*) AS line_item_count
    FROM order_items oi
    GROUP BY oi.order_id
)

SELECT
    o.*,
    oa.product_count,
    oa.total_quantity,
    oa.line_item_count,

    -- Derived flags
    CASE
        WHEN o.order_status = 'delivered' THEN TRUE
        ELSE FALSE
    END AS is_delivered,

    CASE
        WHEN o.cancelled_date IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS is_cancelled,

    -- Calculate fulfillment times
    DATEDIFF('day', o.order_date, o.payment_date) AS days_to_payment,
    DATEDIFF('day', o.payment_date, o.shipped_date) AS days_to_ship,
    DATEDIFF('day', o.shipped_date, o.delivered_date) AS days_to_deliver,
    DATEDIFF('day', o.order_date, o.delivered_date) AS total_fulfillment_days

FROM orders o
LEFT JOIN order_aggregates oa ON o.order_id = oa.order_id;

-- ============================================
-- DIMENSION MODELS
-- ============================================

-- models/marts/core/dim_customers.sql
-- {{ config(
--     materialized='table',
--     tags=['dimension']
-- ) }}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS lifetime_orders,
        SUM(total_amount) AS lifetime_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM {{ ref('stg_orders') }}
    WHERE order_status NOT IN ('cancelled', 'refunded')
    GROUP BY customer_id
)

SELECT
    -- Surrogate Key
    {{ dbt_utils.generate_surrogate_key(['c.customer_id']) }} AS customer_key,

    -- Natural Key
    c.customer_id,

    -- Attributes
    c.customer_name,
    c.email,
    c.phone,
    c.customer_segment,
    c.customer_tier,

    -- Address
    c.country,
    c.state,
    c.city,
    c.postal_code,

    -- Derived Metrics
    COALESCE(co.lifetime_orders, 0) AS lifetime_orders,
    COALESCE(co.lifetime_value, 0) AS lifetime_value,
    co.first_order_date,
    co.last_order_date,

    -- Customer Lifecycle
    CASE
        WHEN co.lifetime_orders IS NULL THEN 'Prospect'
        WHEN co.lifetime_orders = 1 THEN 'New'
        WHEN co.lifetime_orders BETWEEN 2 AND 5 THEN 'Regular'
        WHEN co.lifetime_orders > 5 THEN 'Loyal'
    END AS customer_lifecycle_stage,

    -- Metadata
    c.created_at,
    c.updated_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM customers c
LEFT JOIN customer_orders co ON c.customer_id = co.customer_id;

-- ============================================

-- models/marts/core/dim_products.sql
-- {{ config(
--     materialized='table',
--     tags=['dimension']
-- ) }}

WITH products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

product_sales AS (
    SELECT
        p.product_id,
        COUNT(DISTINCT oi.order_id) AS times_ordered,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.line_total) AS total_revenue
    FROM {{ ref('stg_products') }} p
    LEFT JOIN {{ ref('stg_order_items') }} oi ON p.product_id = oi.product_id
    GROUP BY p.product_id
)

SELECT
    -- Surrogate Key
    {{ dbt_utils.generate_surrogate_key(['p.product_id']) }} AS product_key,

    -- Natural Key
    p.product_id,

    -- Attributes
    p.product_name,
    p.sku,
    p.brand,
    p.category,
    p.subcategory,
    p.department,

    -- Pricing
    p.unit_cost,
    p.unit_price,
    p.unit_price - p.unit_cost AS unit_profit,
    CASE
        WHEN p.unit_price > 0
        THEN ((p.unit_price - p.unit_cost) / p.unit_price) * 100
        ELSE 0
    END AS margin_percentage,

    -- Product Performance
    COALESCE(ps.times_ordered, 0) AS times_ordered,
    COALESCE(ps.total_quantity_sold, 0) AS total_quantity_sold,
    COALESCE(ps.total_revenue, 0) AS total_revenue,

    -- Flags
    p.is_active,

    -- Metadata
    p.created_at,
    p.updated_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM products p
LEFT JOIN product_sales ps ON p.product_id = ps.product_id;

-- ============================================

-- models/marts/core/dim_date.sql
-- {{ config(
--     materialized='table',
--     tags=['dimension']
-- ) }}

{{ dbt_date.get_date_dimension("2020-01-01", "2030-12-31") }}

-- Alternatively, manual date dimension creation:
/*
WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2030-12-31' as date)"
    )}}
)

SELECT
    TO_NUMBER(TO_CHAR(date_day, 'YYYYMMDD')) AS date_key,
    date_day AS date_value,

    -- Day attributes
    DAYOFWEEK(date_day) AS day_of_week,
    DAYNAME(date_day) AS day_name,
    DAYOFMONTH(date_day) AS day_of_month,
    DAYOFYEAR(date_day) AS day_of_year,

    -- Week attributes
    WEEKOFYEAR(date_day) AS week_of_year,

    -- Month attributes
    MONTH(date_day) AS month_number,
    MONTHNAME(date_day) AS month_name,

    -- Quarter attributes
    QUARTER(date_day) AS quarter,
    'Q' || QUARTER(date_day) AS quarter_name,

    -- Year attributes
    YEAR(date_day) AS year,

    -- Flags
    CASE WHEN DAYOFWEEK(date_day) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,

    -- Fiscal calendar (assuming fiscal year starts in July)
    CASE
        WHEN MONTH(date_day) >= 7 THEN YEAR(date_day) + 1
        ELSE YEAR(date_day)
    END AS fiscal_year,

    CASE
        WHEN MONTH(date_day) IN (7, 8, 9) THEN 1
        WHEN MONTH(date_day) IN (10, 11, 12) THEN 2
        WHEN MONTH(date_day) IN (1, 2, 3) THEN 3
        WHEN MONTH(date_day) IN (4, 5, 6) THEN 4
    END AS fiscal_quarter

FROM date_spine
*/

-- ============================================
-- FACT MODELS
-- ============================================

-- models/marts/core/fct_sales.sql
-- {{ config(
--     materialized='incremental',
--     unique_key='sales_key',
--     on_schema_change='sync_all_columns',
--     tags=['fact']
-- ) }}

WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}

    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(order_updated_at) FROM {{ this }})
    {% endif %}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

dim_date AS (
    SELECT * FROM {{ ref('dim_date') }}
),

dim_customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

dim_products AS (
    SELECT * FROM {{ ref('dim_products') }}
)

SELECT
    -- Surrogate Key
    {{ dbt_utils.generate_surrogate_key(['oi.order_id', 'oi.line_number']) }} AS sales_key,

    -- Foreign Keys
    dd.date_key,
    dc.customer_key,
    dp.product_key,

    -- Degenerate Dimensions
    o.order_id,
    oi.line_number,
    o.order_number,

    -- Measures
    oi.quantity,
    oi.unit_price,
    dp.unit_cost,
    oi.line_total AS gross_sales_amount,
    oi.discount_amount,
    oi.line_total - oi.discount_amount AS net_sales_amount,
    (oi.line_total - oi.discount_amount) * 0.08 AS tax_amount,  -- 8% tax
    (oi.quantity * dp.unit_cost) AS total_cost,
    (oi.line_total - oi.discount_amount - (oi.quantity * dp.unit_cost)) AS profit_amount,

    -- Flags
    o.is_delivered,
    o.is_cancelled,

    -- Metadata
    o.order_date,
    o.updated_at AS order_updated_at,
    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN dim_date dd ON o.order_date = dd.date_value
INNER JOIN dim_customers dc ON o.customer_id = dc.customer_id
INNER JOIN dim_products dp ON oi.product_id = dp.product_id;

-- ============================================
-- SNAPSHOT MODELS (SCD Type 2)
-- ============================================

-- snapshots/customers_snapshot.sql
-- {% snapshot customers_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='customer_id',
      strategy='check',
      check_cols=['customer_segment', 'customer_tier', 'city', 'state'],
      invalidate_hard_deletes=True
    )
}}

SELECT * FROM {{ source('ecommerce', 'raw_customers') }}

-- {% endsnapshot %}

-- ============================================
-- AGGREGATE MODELS
-- ============================================

-- models/marts/analytics/fct_daily_sales_summary.sql
-- {{ config(
--     materialized='table',
--     tags=['aggregate']
-- ) }}

SELECT
    date_key,
    customer_key,
    product_key,

    -- Aggregated Measures
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(*) AS line_item_count,
    SUM(quantity) AS total_quantity,
    SUM(gross_sales_amount) AS total_gross_sales,
    SUM(discount_amount) AS total_discount,
    SUM(net_sales_amount) AS total_net_sales,
    SUM(tax_amount) AS total_tax,
    SUM(profit_amount) AS total_profit,

    -- Derived Metrics
    AVG(unit_price) AS avg_unit_price,
    MAX(gross_sales_amount) AS max_transaction_amount,

    CURRENT_TIMESTAMP() AS dbt_updated_at

FROM {{ ref('fct_sales') }}
WHERE is_cancelled = FALSE
GROUP BY date_key, customer_key, product_key;

-- ============================================
-- DATA QUALITY TESTS
-- ============================================

-- tests/assert_valid_order_totals.sql
-- {{ config(severity='error') }}

SELECT
    order_id,
    SUM(line_total) AS calculated_total,
    MAX(order_total) AS reported_total
FROM {{ ref('fct_sales') }} s
JOIN {{ ref('stg_orders') }} o ON s.order_id = o.order_id
GROUP BY order_id, o.total_amount
HAVING ABS(SUM(line_total) - MAX(order_total)) > 0.01;

-- ============================================
-- MACROS
-- ============================================

-- macros/cents_to_dollars.sql
-- {% macro cents_to_dollars(column_name, precision=2) %}
--     ROUND({{ column_name }} / 100, {{ precision }})
-- {% endmacro %}

-- macros/generate_schema_name.sql
-- {% macro generate_schema_name(custom_schema_name, node) -%}
--     {%- set default_schema = target.schema -%}
--     {%- if custom_schema_name is none -%}
--         {{ default_schema }}
--     {%- else -%}
--         {{ custom_schema_name | trim }}
--     {%- endif -%}
-- {%- endmacro %}
