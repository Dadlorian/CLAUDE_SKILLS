-- Data Quality Test Queries
-- Run these regularly to ensure data integrity

-- ================================================
-- COMPLETENESS TESTS
-- ================================================

-- Check for null values in critical columns
SELECT
    'fact_sales' AS table_name,
    'product_key' AS column_name,
    COUNT(*) AS null_count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_sales) AS null_percentage
FROM fact_sales
WHERE product_key IS NULL

UNION ALL

SELECT
    'fact_sales',
    'customer_key',
    COUNT(*),
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_sales)
FROM fact_sales
WHERE customer_key IS NULL;

-- Orphaned records (referential integrity check)
SELECT
    'Orphaned sales records (invalid product)' AS issue,
    COUNT(*) AS count
FROM fact_sales s
LEFT JOIN dim_product p ON s.product_key = p.product_key
WHERE p.product_key IS NULL;

-- ================================================
-- ACCURACY TESTS
-- ================================================

-- Revenue calculation accuracy
SELECT
    order_id,
    SUM(quantity * unit_price) AS calculated_revenue,
    SUM(total_amount) AS stored_revenue,
    ABS(SUM(quantity * unit_price) - SUM(total_amount)) AS variance
FROM fact_sales
GROUP BY order_id
HAVING ABS(SUM(quantity * unit_price) - SUM(total_amount)) > 0.01
LIMIT 100;

-- Profit calculation check
SELECT
    COUNT(*) AS invalid_profit_count
FROM fact_sales
WHERE profit_amount <> (total_amount - cost_amount);

-- ================================================
-- CONSISTENCY TESTS
-- ================================================

-- Compare fact totals with source system
WITH fact_totals AS (
    SELECT
        DATE(d.date_value) AS sale_date,
        SUM(total_amount) AS fact_total
    FROM fact_sales s
    JOIN dim_date d ON s.date_key = d.date_key
    WHERE d.date_value >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE(d.date_value)
),
source_totals AS (
    SELECT
        DATE(order_date) AS sale_date,
        SUM(amount) AS source_total
    FROM source_system.orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE(order_date)
)
SELECT
    COALESCE(f.sale_date, s.sale_date) AS sale_date,
    f.fact_total,
    s.source_total,
    ABS(COALESCE(f.fact_total, 0) - COALESCE(s.source_total, 0)) AS variance,
    CASE
        WHEN ABS(COALESCE(f.fact_total, 0) - COALESCE(s.source_total, 0)) > 100 THEN 'FAIL'
        ELSE 'PASS'
    END AS test_result
FROM fact_totals f
FULL OUTER JOIN source_totals s ON f.sale_date = s.sale_date
ORDER BY sale_date;

-- ================================================
-- TIMELINESS TESTS
-- ================================================

-- Check data freshness
SELECT
    'fact_sales' AS table_name,
    MAX(d.date_value) AS latest_date,
    CURRENT_DATE - MAX(d.date_value) AS days_old,
    CASE
        WHEN CURRENT_DATE - MAX(d.date_value) > 1 THEN 'FAIL - Data stale'
        ELSE 'PASS'
    END AS freshness_check
FROM fact_sales s
JOIN dim_date d ON s.date_key = d.date_key;

-- ================================================
-- UNIQUENESS TESTS
-- ================================================

-- Check for duplicates in dimension tables
SELECT
    'dim_product' AS table_name,
    product_id,
    COUNT(*) AS duplicate_count
FROM dim_product
WHERE is_current = TRUE
GROUP BY product_id
HAVING COUNT(*) > 1;

-- Check for duplicate transactions
SELECT
    order_id,
    line_number,
    COUNT(*) AS duplicate_count
FROM fact_sales
GROUP BY order_id, line_number
HAVING COUNT(*) > 1;

-- ================================================
-- VALIDITY TESTS
-- ================================================

-- Check for invalid date keys
SELECT
    'Invalid date keys in fact_sales' AS issue,
    COUNT(*) AS count
FROM fact_sales s
LEFT JOIN dim_date d ON s.date_key = d.date_key
WHERE d.date_key IS NULL;

-- Negative quantities or amounts
SELECT
    'Negative values detected' AS issue,
    COUNT(*) AS count
FROM fact_sales
WHERE quantity < 0
   OR unit_price < 0
   OR total_amount < 0;

-- Future dates
SELECT
    'Future dates detected' AS issue,
    COUNT(*) AS count
FROM fact_sales s
JOIN dim_date d ON s.date_key = d.date_key
WHERE d.date_value > CURRENT_DATE;
