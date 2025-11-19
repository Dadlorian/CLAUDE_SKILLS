-- Self-Service Analytics SQL Examples
-- Common patterns for business users

-- ====================
-- 1. BASIC AGGREGATIONS
-- ====================

-- Total revenue by month
SELECT
  DATE_TRUNC('month', order_date) as month,
  SUM(order_amount) as total_revenue,
  COUNT(*) as order_count,
  AVG(order_amount) as avg_order_value
FROM fct_orders
WHERE order_date >= '2024-01-01'
GROUP BY 1
ORDER BY 1;

-- Count customers by segment
SELECT
  customer_segment,
  COUNT(*) as customer_count,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM dim_customers
WHERE account_status = 'active'
GROUP BY 1
ORDER BY customer_count DESC;

-- ====================
-- 2. JOINS
-- ====================

-- Orders with customer details
SELECT
  o.order_id,
  o.order_date,
  o.order_amount,
  c.customer_id,
  c.email,
  c.customer_segment
FROM fct_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= CURRENT_DATE - 30
ORDER BY o.order_date DESC;

-- ====================
-- 3. COHORT ANALYSIS
-- ====================

-- Monthly retention cohort
WITH user_cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', MIN(signup_date)) as cohort_month
  FROM dim_customers
  GROUP BY 1
),
monthly_activity AS (
  SELECT
    user_id,
    DATE_TRUNC('month', activity_date) as activity_month
  FROM fct_user_events
  WHERE event_type = 'session_start'
)
SELECT
  c.cohort_month,
  a.activity_month,
  COUNT(DISTINCT a.user_id) as active_users,
  COUNT(DISTINCT a.user_id) * 100.0 / 
    COUNT(DISTINCT c.user_id) as retention_rate
FROM user_cohorts c
LEFT JOIN monthly_activity a ON c.user_id = a.user_id
GROUP BY 1, 2
ORDER BY 1, 2;

-- ====================
-- 4. WINDOW FUNCTIONS
-- ====================

-- Running total of revenue
SELECT
  order_date,
  order_amount,
  SUM(order_amount) OVER (
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as running_total
FROM fct_orders
ORDER BY order_date;

-- Previous month comparison
SELECT
  DATE_TRUNC('month', order_date) as month,
  SUM(order_amount) as current_revenue,
  LAG(SUM(order_amount)) OVER (ORDER BY DATE_TRUNC('month', order_date)) as prev_month_revenue,
  (SUM(order_amount) / LAG(SUM(order_amount)) OVER (ORDER BY DATE_TRUNC('month', order_date)) - 1) * 100 as growth_pct
FROM fct_orders
GROUP BY 1
ORDER BY 1;

-- ====================
-- 5. FUNNEL ANALYSIS
-- ====================

-- Conversion funnel
SELECT
  'Step 1: Visit' as step,
  COUNT(DISTINCT user_id) as users,
  100.0 as conversion_rate
FROM fct_events
WHERE event_type = 'page_view' AND event_date = CURRENT_DATE

UNION ALL

SELECT
  'Step 2: Signup Start' as step,
  COUNT(DISTINCT user_id) as users,
  COUNT(DISTINCT user_id) * 100.0 / (
    SELECT COUNT(DISTINCT user_id)
    FROM fct_events
    WHERE event_type = 'page_view' AND event_date = CURRENT_DATE
  ) as conversion_rate
FROM fct_events
WHERE event_type = 'signup_start' AND event_date = CURRENT_DATE

UNION ALL

SELECT
  'Step 3: Signup Complete' as step,
  COUNT(DISTINCT user_id) as users,
  COUNT(DISTINCT user_id) * 100.0 / (
    SELECT COUNT(DISTINCT user_id)
    FROM fct_events
    WHERE event_type = 'page_view' AND event_date = CURRENT_DATE
  ) as conversion_rate
FROM fct_events
WHERE event_type = 'signup_complete' AND event_date = CURRENT_DATE;

-- ====================
-- 6. TOP N ANALYSIS
-- ====================

-- Top 10 products by revenue
SELECT
  product_id,
  product_name,
  SUM(order_amount) as total_revenue,
  COUNT(*) as order_count
FROM fct_orders o
JOIN dim_products p ON o.product_id = p.product_id
WHERE order_date >= CURRENT_DATE - 90
GROUP BY 1, 2
ORDER BY total_revenue DESC
LIMIT 10;

-- ====================
-- 7. TIME COMPARISONS
-- ====================

-- Year-over-year comparison
SELECT
  DATE_TRUNC('month', order_date) as month,
  SUM(order_amount) as current_year_revenue,
  SUM(CASE 
    WHEN YEAR(order_date) = YEAR(CURRENT_DATE) - 1 
    THEN order_amount 
  END) as previous_year_revenue,
  (SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE) THEN order_amount END) /
   SUM(CASE WHEN YEAR(order_date) = YEAR(CURRENT_DATE) - 1 THEN order_amount END) - 1) * 100 as yoy_growth
FROM fct_orders
WHERE YEAR(order_date) IN (YEAR(CURRENT_DATE), YEAR(CURRENT_DATE) - 1)
GROUP BY 1
ORDER BY 1;

-- ====================
-- 8. CONDITIONAL AGGREGATION
-- ====================

-- Revenue by product category and region
SELECT
  product_category,
  SUM(CASE WHEN region = 'North America' THEN order_amount END) as north_america_revenue,
  SUM(CASE WHEN region = 'Europe' THEN order_amount END) as europe_revenue,
  SUM(CASE WHEN region = 'Asia' THEN order_amount END) as asia_revenue,
  SUM(order_amount) as total_revenue
FROM fct_orders o
JOIN dim_products p ON o.product_id = p.product_id
WHERE order_date >= CURRENT_DATE - 30
GROUP BY 1
ORDER BY total_revenue DESC;
