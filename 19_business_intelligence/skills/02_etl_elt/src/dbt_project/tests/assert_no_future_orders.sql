-- No orders should have future dates

SELECT
    order_id,
    order_date,
    CURRENT_DATE AS today

FROM {{ ref('fct_orders') }}

WHERE DATE(order_date) > CURRENT_DATE
