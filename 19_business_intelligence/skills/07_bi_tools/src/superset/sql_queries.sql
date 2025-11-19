-- Apache Superset SQL Examples

-- ================================================
-- BASIC METRICS
-- ================================================

-- Total Revenue
SELECT SUM(amount) AS total_revenue
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days';

-- Active Customers
SELECT COUNT(DISTINCT customer_id) AS active_customers
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days';

-- Average Order Value
SELECT AVG(amount) AS avg_order_value
FROM sales
WHERE status = 'completed';

-- ================================================
-- TIME SERIES
-- ================================================

-- Daily Sales Trend
SELECT
    DATE(order_date) AS date,
    SUM(amount) AS daily_revenue,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(order_date)
ORDER BY date;

-- Month-over-Month Growth
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS revenue
    FROM sales
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prior_month_revenue,
    ((revenue - LAG(revenue) OVER (ORDER BY month)) / 
     LAG(revenue) OVER (ORDER BY month)) * 100 AS growth_pct
FROM monthly_sales
ORDER BY month DESC;

-- ================================================
-- COHORT ANALYSIS
-- ================================================

-- Customer Cohorts by First Purchase Month
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM sales
    GROUP BY customer_id
),
cohort_data AS (
    SELECT
        c.cohort_month,
        DATE_TRUNC('month', s.order_date) AS order_month,
        EXTRACT(MONTH FROM AGE(s.order_date, c.cohort_month)) AS months_since_first,
        COUNT(DISTINCT s.customer_id) AS active_customers
    FROM sales s
    JOIN cohorts c ON s.customer_id = c.customer_id
    GROUP BY c.cohort_month, DATE_TRUNC('month', s.order_date)
)
SELECT
    cohort_month,
    months_since_first,
    active_customers,
    FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month ORDER BY months_since_first
    ) AS cohort_size,
    (active_customers::FLOAT / FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month ORDER BY months_since_first
    )) * 100 AS retention_pct
FROM cohort_data
ORDER BY cohort_month DESC, months_since_first;

-- ================================================
-- PRODUCT ANALYSIS
-- ================================================

-- Top Products by Revenue
SELECT
    p.product_name,
    p.category,
    SUM(s.quantity) AS units_sold,
    SUM(s.amount) AS total_revenue,
    AVG(s.amount / s.quantity) AS avg_unit_price
FROM sales s
JOIN products p ON s.product_id = p.id
WHERE s.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- Product Affinity (Frequently Bought Together)
SELECT
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(*) AS times_purchased_together
FROM sales s1
JOIN sales s2 ON s1.order_id = s2.order_id AND s1.product_id < s2.product_id
JOIN products p1 ON s1.product_id = p1.id
JOIN products p2 ON s2.product_id = p2.id
GROUP BY p1.product_name, p2.product_name
HAVING COUNT(*) >= 10
ORDER BY times_purchased_together DESC
LIMIT 20;

-- ================================================
-- RLS (Row-Level Security) Example
-- ================================================

-- Filter by user's region (use Jinja templating in Superset)
SELECT
    order_date,
    customer_name,
    amount,
    region
FROM sales
WHERE region = '{{ cache_key_wrapper(current_user_region) }}'
  AND order_date >= CURRENT_DATE - INTERVAL '90 days';
