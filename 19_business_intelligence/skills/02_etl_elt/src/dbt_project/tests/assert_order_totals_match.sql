-- Validate that order totals match sum of line items

SELECT
    order_id,
    total_amount,
    (quantity * unit_price) + tax_amount - discount_amount AS calculated_total,
    ABS(total_amount - ((quantity * unit_price) + tax_amount - discount_amount)) AS difference

FROM {{ ref('fct_orders') }}

WHERE ABS(total_amount - ((quantity * unit_price) + tax_amount - discount_amount)) > 0.01
