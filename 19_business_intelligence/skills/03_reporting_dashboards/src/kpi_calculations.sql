-- KPI SQL Calculations for Dashboards
-- Common business metrics with proper aggregation and optimization

-- ============================================================================
-- REVENUE METRICS
-- ============================================================================

-- Monthly Recurring Revenue (MRR)
SELECT
  DATE_TRUNC('month', subscription_start_date) AS month,
  SUM(monthly_amount) AS mrr,
  COUNT(DISTINCT customer_id) AS customer_count,
  SUM(monthly_amount) / COUNT(DISTINCT customer_id) AS arpu
FROM subscriptions
WHERE status = 'active'
  AND subscription_start_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY 1
ORDER BY 1;

-- Annual Recurring Revenue (ARR)
SELECT
  SUM(monthly_amount) * 12 AS arr,
  SUM(CASE WHEN customer_segment = 'Enterprise' THEN monthly_amount * 12 ELSE 0 END) AS enterprise_arr,
  SUM(CASE WHEN customer_segment = 'SMB' THEN monthly_amount * 12 ELSE 0 END) AS smb_arr
FROM subscriptions
WHERE status = 'active';

-- Revenue Growth Rate (MoM, QoQ, YoY)
WITH monthly_revenue AS (
  SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(revenue) AS revenue
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '24 months'
  GROUP BY 1
)
SELECT
  month,
  revenue,
  LAG(revenue, 1) OVER (ORDER BY month) AS prev_month,
  ((revenue - LAG(revenue, 1) OVER (ORDER BY month)) / LAG(revenue, 1) OVER (ORDER BY month) * 100) AS mom_growth_pct,
  LAG(revenue, 3) OVER (ORDER BY month) AS prev_quarter,
  ((revenue - LAG(revenue, 3) OVER (ORDER BY month)) / LAG(revenue, 3) OVER (ORDER BY month) * 100) AS qoq_growth_pct,
  LAG(revenue, 12) OVER (ORDER BY month) AS prev_year,
  ((revenue - LAG(revenue, 12) OVER (ORDER BY month)) / LAG(revenue, 12) OVER (ORDER BY month) * 100) AS yoy_growth_pct
FROM monthly_revenue
ORDER BY month DESC;

-- ============================================================================
-- CUSTOMER METRICS
-- ============================================================================

-- Customer Acquisition (New Customers by Month)
SELECT
  DATE_TRUNC('month', first_order_date) AS cohort_month,
  COUNT(DISTINCT customer_id) AS new_customers,
  SUM(first_order_revenue) AS cohort_revenue,
  AVG(first_order_revenue) AS avg_first_order
FROM (
  SELECT
    customer_id,
    MIN(order_date) AS first_order_date,
    (
      SELECT revenue
      FROM orders o2
      WHERE o2.customer_id = o1.customer_id
      ORDER BY order_date
      LIMIT 1
    ) AS first_order_revenue
  FROM orders o1
  GROUP BY customer_id
) first_orders
WHERE first_order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;

-- Monthly Churn Rate
WITH monthly_customers AS (
  SELECT
    DATE_TRUNC('month', date) AS month,
    COUNT(DISTINCT customer_id) AS active_customers
  FROM subscriptions
  WHERE status = 'active'
  GROUP BY 1
),
monthly_churned AS (
  SELECT
    DATE_TRUNC('month', churned_date) AS month,
    COUNT(DISTINCT customer_id) AS churned_customers
  FROM subscriptions
  WHERE churned_date IS NOT NULL
  GROUP BY 1
)
SELECT
  c.month,
  c.active_customers,
  COALESCE(ch.churned_customers, 0) AS churned_customers,
  (COALESCE(ch.churned_customers, 0)::FLOAT / NULLIF(c.active_customers, 0) * 100) AS churn_rate_pct
FROM monthly_customers c
LEFT JOIN monthly_churned ch ON c.month = ch.month
ORDER BY c.month DESC;

-- Net Revenue Retention (NRR)
WITH monthly_cohort_revenue AS (
  SELECT
    DATE_TRUNC('month', first_order_date) AS cohort_month,
    DATE_TRUNC('month', order_date) AS revenue_month,
    customer_id,
    SUM(revenue) AS revenue
  FROM orders
  JOIN (
    SELECT customer_id, MIN(order_date) AS first_order_date
    FROM orders
    GROUP BY customer_id
  ) cohorts USING (customer_id)
  GROUP BY 1, 2, 3
)
SELECT
  cohort_month,
  SUM(CASE WHEN revenue_month = cohort_month THEN revenue ELSE 0 END) AS starting_mrr,
  SUM(CASE WHEN revenue_month = cohort_month + INTERVAL '1 month' THEN revenue ELSE 0 END) AS month_1_mrr,
  (
    SUM(CASE WHEN revenue_month = cohort_month + INTERVAL '1 month' THEN revenue ELSE 0 END) /
    NULLIF(SUM(CASE WHEN revenue_month = cohort_month THEN revenue ELSE 0 END), 0) * 100
  ) AS nrr_pct
FROM monthly_cohort_revenue
WHERE cohort_month >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;

-- Customer Lifetime Value (LTV)
WITH customer_metrics AS (
  SELECT
    customer_id,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(revenue) AS total_revenue,
    AVG(revenue) AS avg_order_value,
    EXTRACT(DAYS FROM (MAX(order_date) - MIN(order_date))) AS customer_age_days
  FROM orders
  GROUP BY customer_id
)
SELECT
  AVG(total_revenue) AS avg_ltv,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_revenue) AS median_ltv,
  AVG(customer_age_days / 30.0) AS avg_lifetime_months,
  AVG(total_revenue / NULLIF(customer_age_days / 30.0, 0)) AS avg_monthly_value
FROM customer_metrics
WHERE customer_age_days >= 30; -- At least 30 days old

-- ============================================================================
-- ENGAGEMENT METRICS
-- ============================================================================

-- Daily/Monthly Active Users (DAU/MAU)
-- Assuming events table with user_id and event_timestamp
SELECT
  DATE_TRUNC('day', event_timestamp) AS date,
  COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1
ORDER BY 1 DESC;

-- MAU and Stickiness Ratio (DAU/MAU)
WITH daily_active AS (
  SELECT
    DATE_TRUNC('day', event_timestamp) AS date,
    COUNT(DISTINCT user_id) AS dau
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY 1
),
monthly_active AS (
  SELECT
    DATE_TRUNC('month', event_timestamp) AS month,
    COUNT(DISTINCT user_id) AS mau
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY 1
)
SELECT
  d.date,
  d.dau,
  m.mau,
  (d.dau::FLOAT / NULLIF(m.mau, 0) * 100) AS stickiness_ratio
FROM daily_active d
JOIN monthly_active m ON DATE_TRUNC('month', d.date) = m.month
ORDER BY d.date DESC;

-- ============================================================================
-- OPERATIONAL METRICS
-- ============================================================================

-- Sales Pipeline Value
SELECT
  stage,
  COUNT(DISTINCT opportunity_id) AS opportunity_count,
  SUM(amount) AS total_value,
  SUM(amount * probability / 100.0) AS weighted_value,
  AVG(amount) AS avg_deal_size,
  AVG(EXTRACT(DAYS FROM (CURRENT_DATE - created_date))) AS avg_age_days
FROM opportunities
WHERE status = 'open'
GROUP BY stage
ORDER BY
  CASE stage
    WHEN 'Qualified' THEN 1
    WHEN 'Proposal' THEN 2
    WHEN 'Negotiation' THEN 3
    WHEN 'Closed Won' THEN 4
  END;

-- Win Rate by Period
WITH closed_opportunities AS (
  SELECT
    DATE_TRUNC('month', closed_date) AS month,
    status,
    COUNT(*) AS count,
    SUM(amount) AS value
  FROM opportunities
  WHERE status IN ('Closed Won', 'Closed Lost')
    AND closed_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY 1, 2
)
SELECT
  month,
  SUM(CASE WHEN status = 'Closed Won' THEN count ELSE 0 END) AS won_count,
  SUM(CASE WHEN status = 'Closed Lost' THEN count ELSE 0 END) AS lost_count,
  SUM(count) AS total_count,
  (SUM(CASE WHEN status = 'Closed Won' THEN count ELSE 0 END)::FLOAT / NULLIF(SUM(count), 0) * 100) AS win_rate_pct,
  SUM(CASE WHEN status = 'Closed Won' THEN value ELSE 0 END) AS won_value
FROM closed_opportunities
GROUP BY 1
ORDER BY 1 DESC;

-- Average Sales Cycle Length
SELECT
  DATE_TRUNC('month', closed_date) AS month,
  AVG(EXTRACT(DAYS FROM (closed_date - created_date))) AS avg_sales_cycle_days,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(DAYS FROM (closed_date - created_date))) AS median_sales_cycle_days,
  MIN(EXTRACT(DAYS FROM (closed_date - created_date))) AS min_days,
  MAX(EXTRACT(DAYS FROM (closed_date - created_date))) AS max_days
FROM opportunities
WHERE status = 'Closed Won'
  AND closed_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1 DESC;

-- ============================================================================
-- SUPPORT METRICS
-- ============================================================================

-- Support Ticket Metrics
SELECT
  DATE_TRUNC('day', created_at) AS date,
  COUNT(*) AS total_tickets,
  COUNT(*) FILTER (WHERE priority = 'High') AS high_priority,
  COUNT(*) FILTER (WHERE status = 'Open') AS open_tickets,
  COUNT(*) FILTER (WHERE status = 'Resolved') AS resolved_tickets,
  AVG(EXTRACT(EPOCH FROM (first_response_at - created_at)) / 3600.0) AS avg_first_response_hours,
  AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0) FILTER (WHERE status = 'Resolved') AS avg_resolution_hours,
  AVG(csat_score) FILTER (WHERE csat_score IS NOT NULL) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1
ORDER BY 1 DESC;

-- SLA Compliance
WITH sla_metrics AS (
  SELECT
    ticket_id,
    priority,
    EXTRACT(EPOCH FROM (first_response_at - created_at)) / 3600.0 AS first_response_hours,
    CASE priority
      WHEN 'Critical' THEN 1
      WHEN 'High' THEN 4
      WHEN 'Medium' THEN 24
      WHEN 'Low' THEN 48
    END AS sla_hours
  FROM tickets
  WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    AND first_response_at IS NOT NULL
)
SELECT
  priority,
  COUNT(*) AS total_tickets,
  COUNT(*) FILTER (WHERE first_response_hours <= sla_hours) AS sla_met,
  COUNT(*) FILTER (WHERE first_response_hours > sla_hours) AS sla_breached,
  (COUNT(*) FILTER (WHERE first_response_hours <= sla_hours)::FLOAT / NULLIF(COUNT(*), 0) * 100) AS sla_compliance_pct
FROM sla_metrics
GROUP BY priority
ORDER BY priority;

-- ============================================================================
-- PRODUCT METRICS
-- ============================================================================

-- Feature Adoption Rate
SELECT
  feature_name,
  COUNT(DISTINCT user_id) AS users_adopted,
  (
    SELECT COUNT(DISTINCT user_id)
    FROM users
    WHERE status = 'active'
  ) AS total_active_users,
  (COUNT(DISTINCT user_id)::FLOAT / (SELECT COUNT(DISTINCT user_id) FROM users WHERE status = 'active') * 100) AS adoption_rate_pct,
  DATE_TRUNC('month', MIN(first_used_at)) AS launch_month
FROM feature_usage
GROUP BY feature_name
ORDER BY adoption_rate_pct DESC;

-- ============================================================================
-- FINANCIAL METRICS
-- ============================================================================

-- Gross Margin
SELECT
  DATE_TRUNC('month', order_date) AS month,
  SUM(revenue) AS revenue,
  SUM(cogs) AS cogs,
  SUM(revenue - cogs) AS gross_profit,
  ((SUM(revenue - cogs) / NULLIF(SUM(revenue), 0)) * 100) AS gross_margin_pct
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '24 months'
GROUP BY 1
ORDER BY 1 DESC;

-- Customer Acquisition Cost (CAC)
WITH marketing_spend AS (
  SELECT
    DATE_TRUNC('month', spend_date) AS month,
    SUM(amount) AS marketing_spend
  FROM marketing_expenses
  GROUP BY 1
),
new_customers AS (
  SELECT
    DATE_TRUNC('month', first_order_date) AS month,
    COUNT(DISTINCT customer_id) AS new_customers
  FROM (
    SELECT
      customer_id,
      MIN(order_date) AS first_order_date
    FROM orders
    GROUP BY customer_id
  ) cohorts
  GROUP BY 1
)
SELECT
  m.month,
  m.marketing_spend,
  n.new_customers,
  (m.marketing_spend / NULLIF(n.new_customers, 0)) AS cac
FROM marketing_spend m
JOIN new_customers n USING (month)
WHERE m.month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY m.month DESC;

-- LTV:CAC Ratio
WITH ltv AS (
  SELECT
    DATE_TRUNC('month', first_order_date) AS cohort_month,
    AVG(total_revenue) AS avg_ltv
  FROM (
    SELECT
      customer_id,
      MIN(order_date) AS first_order_date,
      SUM(revenue) AS total_revenue
    FROM orders
    GROUP BY customer_id
  ) customer_revenue
  GROUP BY 1
),
cac AS (
  SELECT
    DATE_TRUNC('month', spend_date) AS month,
    SUM(amount) / NULLIF(COUNT(DISTINCT customer_id), 0) AS avg_cac
  FROM marketing_expenses
  JOIN customer_acquisitions USING (campaign_id)
  GROUP BY 1
)
SELECT
  ltv.cohort_month,
  ltv.avg_ltv,
  cac.avg_cac,
  (ltv.avg_ltv / NULLIF(cac.avg_cac, 0)) AS ltv_cac_ratio
FROM ltv
JOIN cac ON ltv.cohort_month = cac.month
WHERE ltv.cohort_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY ltv.cohort_month DESC;

-- ============================================================================
-- OPTIMIZATION TIPS
-- ============================================================================

-- 1. Use indexes on frequently filtered columns:
-- CREATE INDEX idx_orders_order_date ON orders(order_date);
-- CREATE INDEX idx_orders_customer_id ON orders(customer_id);
-- CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- 2. Create materialized views for expensive calculations:
-- CREATE MATERIALIZED VIEW mv_monthly_revenue AS [query];
-- Refresh: REFRESH MATERIALIZED VIEW mv_monthly_revenue;

-- 3. Use partitioning for large tables:
-- CREATE TABLE orders_2024_01 PARTITION OF orders
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 4. Limit result sets in dashboards:
-- Add: LIMIT 1000 to prevent runaway queries

-- 5. Use EXPLAIN ANALYZE to optimize queries:
-- EXPLAIN ANALYZE [your query];
