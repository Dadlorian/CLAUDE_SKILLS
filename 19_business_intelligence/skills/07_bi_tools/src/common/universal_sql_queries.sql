-- Universal SQL Queries (Work across most databases with minor syntax changes)

-- ================================================
-- BASIC AGGREGATIONS
-- ================================================

-- Revenue by month
SELECT
    DATE_TRUNC('month', order_date) AS month,  -- PostgreSQL/Redshift
    -- DATEADD(month, DATEDIFF(month, 0, order_date), 0) AS month,  -- SQL Server
    -- DATE_FORMAT(order_date, '%Y-%m-01') AS month,  -- MySQL
    SUM(amount) AS total_revenue,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- ================================================
-- WINDOW FUNCTIONS
-- ================================================

-- Running total
SELECT
    order_date,
    amount,
    SUM(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM sales
ORDER BY order_date;

-- Ranking
SELECT
    product_name,
    category,
    total_sales,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_sales DESC) AS rank_in_category,
    RANK() OVER (ORDER BY total_sales DESC) AS overall_rank
FROM (
    SELECT
        product_name,
        category,
        SUM(amount) AS total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.id
    GROUP BY product_name, category
) AS product_sales;

-- Moving average (3-period)
SELECT
    order_date,
    daily_sales,
    AVG(daily_sales) OVER (
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3day
FROM (
    SELECT
        DATE(order_date) AS order_date,
        SUM(amount) AS daily_sales
    FROM sales
    GROUP BY DATE(order_date)
) AS daily_summary;

-- ================================================
-- CUSTOMER ANALYSIS
-- ================================================

-- Customer lifetime value
SELECT
    customer_id,
    customer_name,
    MIN(order_date) AS first_purchase_date,
    MAX(order_date) AS last_purchase_date,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(amount) AS lifetime_value,
    AVG(amount) AS avg_order_value
FROM sales s
JOIN customers c ON s.customer_id = c.id
GROUP BY customer_id, customer_name
ORDER BY lifetime_value DESC;

-- RFM Analysis
WITH rfm_data AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(amount) AS monetary
    FROM sales
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        DATEDIFF(day, last_order_date, CURRENT_DATE) AS recency_days,
        NTILE(5) OVER (ORDER BY DATEDIFF(day, last_order_date, CURRENT_DATE) DESC) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary) AS monetary_score
    FROM rfm_data
)
SELECT
    customer_id,
    recency_days,
    recency_score,
    frequency_score,
    monetary_score,
    CAST(recency_score AS VARCHAR) || CAST(frequency_score AS VARCHAR) || CAST(monetary_score AS VARCHAR) AS rfm_segment,
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'Recent Customers'
        WHEN recency_score <= 2 THEN 'At Risk'
        ELSE 'Other'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary_score DESC, frequency_score DESC, recency_score DESC;

-- ================================================
-- SALES FUNNEL
-- ================================================

SELECT
    'Visitors' AS stage,
    COUNT(DISTINCT session_id) AS count,
    100.0 AS conversion_pct
FROM web_sessions
WHERE session_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
    'Add to Cart' AS stage,
    COUNT(DISTINCT session_id) AS count,
    COUNT(DISTINCT session_id) * 100.0 / (
        SELECT COUNT(DISTINCT session_id)
        FROM web_sessions
        WHERE session_date >= CURRENT_DATE - INTERVAL '30 days'
    ) AS conversion_pct
FROM cart_events
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
    'Checkout' AS stage,
    COUNT(DISTINCT session_id) AS count,
    COUNT(DISTINCT session_id) * 100.0 / (
        SELECT COUNT(DISTINCT session_id)
        FROM web_sessions
        WHERE session_date >= CURRENT_DATE - INTERVAL '30 days'
    ) AS conversion_pct
FROM checkout_events
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT
    'Purchase' AS stage,
    COUNT(DISTINCT order_id) AS count,
    COUNT(DISTINCT order_id) * 100.0 / (
        SELECT COUNT(DISTINCT session_id)
        FROM web_sessions
        WHERE session_date >= CURRENT_DATE - INTERVAL '30 days'
    ) AS conversion_pct
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days';
