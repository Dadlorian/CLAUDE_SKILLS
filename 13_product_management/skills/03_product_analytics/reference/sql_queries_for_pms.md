# SQL Queries for Product Managers

Essential SQL queries for analyzing product analytics data. Use with Snowflake, BigQuery, Redshift, or similar data warehouses.

## Setup and Assumptions

**Standard Tables:**
- `events`: user_id, event_name, event_timestamp, properties (JSON), platform
- `users`: user_id, created_at, signup_date, plan_tier, cohort_date, source
- `transactions`: transaction_id, user_id, amount, created_at, type (subscription, purchase)

## DAU/MAU Metrics

### Daily Active Users (DAU)
```sql
-- Simple DAU count
SELECT
  DATE(event_timestamp) AS event_date,
  COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(event_timestamp)
ORDER BY event_date DESC;

-- DAU by platform
SELECT
  DATE(event_timestamp) AS event_date,
  COALESCE(properties.platform, 'unknown') AS platform,
  COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY event_date, platform
ORDER BY event_date DESC, platform;
```

### Monthly Active Users (MAU)
```sql
-- Monthly active users
SELECT
  DATE_TRUNC('month', event_timestamp) AS month,
  COUNT(DISTINCT user_id) AS mau
FROM events
WHERE event_timestamp >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY DATE_TRUNC('month', event_timestamp)
ORDER BY month DESC;

-- DAU/MAU ratio
WITH dau_data AS (
  SELECT
    DATE(event_timestamp) AS event_date,
    COUNT(DISTINCT user_id) AS dau
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY DATE(event_timestamp)
),
mau_data AS (
  SELECT
    DATE_TRUNC('month', DATE(event_timestamp)) AS month,
    COUNT(DISTINCT user_id) AS mau
  FROM events
  WHERE event_timestamp >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
  GROUP BY DATE_TRUNC('month', DATE(event_timestamp))
)
SELECT
  d.event_date,
  d.dau,
  m.mau,
  ROUND(100.0 * d.dau / m.mau, 2) AS dau_mau_ratio
FROM dau_data d
LEFT JOIN mau_data m ON DATE_TRUNC('month', d.event_date) = m.month
ORDER BY d.event_date DESC;
```

## Acquisition Metrics

### Sign-up Conversion Rate
```sql
-- Daily sign-up conversion
WITH traffic AS (
  SELECT
    DATE(event_timestamp) AS event_date,
    COUNT(DISTINCT session_id) AS sessions
  FROM events
  WHERE event_name IN ('page_view', 'landing_page_view')
    AND event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(event_timestamp)
),
signups AS (
  SELECT
    DATE(u.created_at) AS signup_date,
    COUNT(DISTINCT u.user_id) AS new_users
  FROM users u
  WHERE u.created_at >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(u.created_at)
)
SELECT
  t.event_date,
  t.sessions,
  s.new_users,
  ROUND(100.0 * COALESCE(s.new_users, 0) / t.sessions, 2) AS conversion_rate_pct
FROM traffic t
LEFT JOIN signups s ON t.event_date = s.signup_date
ORDER BY t.event_date DESC;

-- Conversion by traffic source
SELECT
  COALESCE(properties.utm_source, 'direct') AS source,
  COUNT(DISTINCT session_id) AS sessions,
  COUNT(DISTINCT CASE WHEN event_name = 'user_signup' THEN user_id END) AS signups,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN event_name = 'user_signup' THEN user_id END) /
    COUNT(DISTINCT session_id), 2) AS conversion_rate_pct
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY source
ORDER BY signups DESC;
```

### Cost Per Acquisition (CPA)
```sql
-- CPA by channel
SELECT
  DATE_TRUNC('week', acquisition_date) AS week,
  utm_source,
  marketing_spend,
  new_users,
  ROUND(marketing_spend / new_users, 2) AS cpa
FROM (
  SELECT
    DATE(u.created_at) AS acquisition_date,
    DATE_TRUNC('week', u.created_at) AS week,
    COALESCE(u.utm_source, 'direct') AS utm_source,
    COUNT(DISTINCT u.user_id) AS new_users,
    SUM(COALESCE(m.spend, 0)) AS marketing_spend
  FROM users u
  LEFT JOIN marketing_spend m
    ON m.source = u.utm_source
    AND DATE(m.date) = DATE(u.created_at)
  WHERE u.created_at >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY week, acquisition_date, utm_source
)
WHERE new_users > 0
ORDER BY week DESC, cpa;
```

## Retention Metrics

### Day N Retention
```sql
-- Day 1 Retention
WITH user_signups AS (
  SELECT
    user_id,
    DATE(created_at) AS signup_date
  FROM users
  WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
),
active_d1 AS (
  SELECT DISTINCT
    user_id,
    DATE(event_timestamp) AS active_date
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
    AND event_timestamp >= (SELECT MIN(created_at) FROM users
        WHERE created_at >= CURRENT_DATE - INTERVAL '90 days')
)
SELECT
  u.signup_date,
  COUNT(DISTINCT u.user_id) AS cohort_size,
  COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 1
    THEN u.user_id
  END) AS day_1_active,
  ROUND(100.0 * COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 1
    THEN u.user_id
  END) / COUNT(DISTINCT u.user_id), 2) AS day_1_retention_pct
FROM user_signups u
LEFT JOIN active_d1 a ON u.user_id = a.user_id
GROUP BY u.signup_date
ORDER BY u.signup_date DESC
LIMIT 30;

-- Day 7 Retention
WITH user_signups AS (
  SELECT
    user_id,
    DATE(created_at) AS signup_date
  FROM users
),
active_users AS (
  SELECT DISTINCT
    user_id,
    DATE(event_timestamp) AS active_date
  FROM events
)
SELECT
  u.signup_date,
  COUNT(DISTINCT u.user_id) AS cohort_size,
  COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 7
    THEN u.user_id
  END) AS day_7_active,
  ROUND(100.0 * COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 7
    THEN u.user_id
  END) / COUNT(DISTINCT u.user_id), 2) AS day_7_retention_pct
FROM user_signups u
LEFT JOIN active_users a ON u.user_id = a.user_id
GROUP BY u.signup_date
ORDER BY u.signup_date DESC
LIMIT 30;

-- Day 30 Retention (Monthly)
WITH user_signups AS (
  SELECT
    user_id,
    DATE(created_at) AS signup_date,
    DATE_TRUNC('month', created_at) AS signup_month
  FROM users
),
active_users AS (
  SELECT DISTINCT
    user_id,
    DATE(event_timestamp) AS active_date
  FROM events
)
SELECT
  u.signup_date,
  u.signup_month,
  COUNT(DISTINCT u.user_id) AS cohort_size,
  COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 30
    THEN u.user_id
  END) AS day_30_active,
  ROUND(100.0 * COUNT(DISTINCT CASE
    WHEN DATE_DIFF(day, u.signup_date, a.active_date) = 30
    THEN u.user_id
  END) / COUNT(DISTINCT u.user_id), 2) AS day_30_retention_pct
FROM user_signups u
LEFT JOIN active_users a ON u.user_id = a.user_id
GROUP BY u.signup_date, u.signup_month
ORDER BY u.signup_month DESC, u.signup_date DESC;
```

### Cohort Retention Matrix
```sql
-- Monthly cohort retention table
WITH user_signups AS (
  SELECT
    user_id,
    DATE_TRUNC('month', created_at) AS cohort_month
  FROM users
),
active_months AS (
  SELECT DISTINCT
    user_id,
    DATE_TRUNC('month', event_timestamp) AS active_month
  FROM events
)
SELECT
  u.cohort_month,
  DATE_DIFF(month, u.cohort_month, a.active_month) AS months_since_cohort,
  COUNT(DISTINCT u.user_id) AS cohort_size,
  COUNT(DISTINCT a.user_id) AS active_users,
  ROUND(100.0 * COUNT(DISTINCT a.user_id) /
    COUNT(DISTINCT u.user_id), 1) AS retention_pct
FROM user_signups u
LEFT JOIN active_months a ON u.user_id = a.user_id
  AND a.active_month >= u.cohort_month
WHERE u.cohort_month >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '24 months')
GROUP BY u.cohort_month, months_since_cohort
ORDER BY u.cohort_month DESC, months_since_cohort;
```

### Monthly Churn
```sql
-- Monthly churn calculation
WITH monthly_active AS (
  SELECT
    DATE_TRUNC('month', event_timestamp) AS month,
    COUNT(DISTINCT user_id) AS active_users
  FROM events
  GROUP BY DATE_TRUNC('month', event_timestamp)
),
monthly_retained AS (
  SELECT
    DATE_TRUNC('month', e.event_timestamp) AS current_month,
    DATE_TRUNC('month', LAG(e.event_timestamp) OVER (PARTITION BY e.user_id ORDER BY DATE_TRUNC('month', e.event_timestamp))) AS previous_month,
    COUNT(DISTINCT e.user_id) AS retained_users
  FROM events e
  GROUP BY e.user_id, DATE_TRUNC('month', e.event_timestamp)
)
SELECT
  m.month,
  m.active_users,
  COALESCE(mr.retained_users, 0) AS users_from_previous_month,
  ROUND(100.0 * (m.active_users - COALESCE(mr.retained_users, 0)) / m.active_users, 2) AS churn_rate_pct
FROM monthly_active m
LEFT JOIN monthly_retained mr ON m.month = mr.current_month
ORDER BY m.month DESC;
```

## Funnel Analysis

### Multi-step Funnel
```sql
-- Sign-up → Email verification → Setup complete → First action
WITH funnel_events AS (
  SELECT
    user_id,
    event_name,
    event_timestamp,
    ROW_NUMBER() OVER (PARTITION BY user_id, event_name ORDER BY event_timestamp) AS event_order
  FROM events
  WHERE event_name IN ('user_signup', 'email_verified', 'setup_complete', 'first_action')
),
funnel_summary AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name = 'user_signup' THEN 1 ELSE 0 END) AS step_1_signup,
    MAX(CASE WHEN event_name = 'email_verified' THEN 1 ELSE 0 END) AS step_2_verified,
    MAX(CASE WHEN event_name = 'setup_complete' THEN 1 ELSE 0 END) AS step_3_setup,
    MAX(CASE WHEN event_name = 'first_action' THEN 1 ELSE 0 END) AS step_4_action
  FROM funnel_events
  WHERE event_order = 1
  GROUP BY user_id
)
SELECT
  COUNT(*) AS total_users,
  SUM(step_1_signup) AS step_1_signups,
  SUM(step_2_verified) AS step_2_verified,
  SUM(step_3_setup) AS step_3_setup,
  SUM(step_4_action) AS step_4_action,
  ROUND(100.0 * SUM(step_1_signup) / COUNT(*), 1) AS step_1_pct,
  ROUND(100.0 * SUM(step_2_verified) / SUM(step_1_signup), 1) AS step_2_pct,
  ROUND(100.0 * SUM(step_3_setup) / SUM(step_2_verified), 1) AS step_3_pct,
  ROUND(100.0 * SUM(step_4_action) / SUM(step_3_setup), 1) AS step_4_pct,
  ROUND(100.0 * SUM(step_4_action) / COUNT(*), 1) AS overall_conversion_pct
FROM funnel_summary;

-- Funnel by cohort
WITH funnel_events AS (
  SELECT
    u.user_id,
    u.cohort_month,
    e.event_name,
    ROW_NUMBER() OVER (PARTITION BY e.user_id, e.event_name ORDER BY e.event_timestamp) AS event_order
  FROM events e
  JOIN users u ON e.user_id = u.user_id
  WHERE e.event_name IN ('user_signup', 'email_verified', 'setup_complete', 'first_action')
),
funnel_summary AS (
  SELECT
    cohort_month,
    user_id,
    MAX(CASE WHEN event_name = 'user_signup' THEN 1 ELSE 0 END) AS step_1,
    MAX(CASE WHEN event_name = 'email_verified' THEN 1 ELSE 0 END) AS step_2,
    MAX(CASE WHEN event_name = 'setup_complete' THEN 1 ELSE 0 END) AS step_3,
    MAX(CASE WHEN event_name = 'first_action' THEN 1 ELSE 0 END) AS step_4
  FROM funnel_events
  WHERE event_order = 1
  GROUP BY cohort_month, user_id
)
SELECT
  cohort_month,
  COUNT(*) AS cohort_size,
  SUM(step_1) AS s1_signup,
  SUM(step_2) AS s2_verified,
  SUM(step_3) AS s3_setup,
  SUM(step_4) AS s4_action,
  ROUND(100.0 * SUM(step_2) / SUM(step_1), 1) AS s1_to_s2_pct,
  ROUND(100.0 * SUM(step_3) / SUM(step_2), 1) AS s2_to_s3_pct,
  ROUND(100.0 * SUM(step_4) / SUM(step_3), 1) AS s3_to_s4_pct,
  ROUND(100.0 * SUM(step_4) / COUNT(*), 1) AS overall_pct
FROM funnel_summary
WHERE cohort_month IS NOT NULL
GROUP BY cohort_month
ORDER BY cohort_month DESC;
```

### Time-based Funnel Analysis
```sql
-- Funnel with time between steps
WITH funnel_events AS (
  SELECT
    user_id,
    event_name,
    event_timestamp,
    LEAD(event_name) OVER (PARTITION BY user_id ORDER BY event_timestamp) AS next_step,
    LEAD(event_timestamp) OVER (PARTITION BY user_id ORDER BY event_timestamp) AS next_timestamp
  FROM events
  WHERE event_name IN ('user_signup', 'email_verified', 'setup_complete', 'first_action')
)
SELECT
  CASE
    WHEN event_name = 'user_signup' AND next_step = 'email_verified' THEN 'signup_to_verify'
    WHEN event_name = 'email_verified' AND next_step = 'setup_complete' THEN 'verify_to_setup'
    WHEN event_name = 'setup_complete' AND next_step = 'first_action' THEN 'setup_to_action'
  END AS transition,
  COUNT(*) AS conversions,
  ROUND(AVG(EXTRACT(EPOCH FROM (next_timestamp - event_timestamp)) / 3600), 2) AS avg_hours,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (next_timestamp - event_timestamp)) / 3600), 2) AS median_hours
FROM funnel_events
WHERE CASE
  WHEN event_name = 'user_signup' AND next_step = 'email_verified' THEN 1
  WHEN event_name = 'email_verified' AND next_step = 'setup_complete' THEN 1
  WHEN event_name = 'setup_complete' AND next_step = 'first_action' THEN 1
  ELSE 0
END = 1
GROUP BY transition
ORDER BY transition;
```

## Revenue and Monetization

### Monthly Recurring Revenue (MRR)
```sql
-- Current MRR
SELECT
  DATE_TRUNC('month', CURRENT_DATE) AS current_month,
  COUNT(DISTINCT user_id) AS paying_users,
  SUM(monthly_amount) AS mrr,
  ROUND(AVG(monthly_amount), 2) AS arpu
FROM (
  SELECT
    user_id,
    COALESCE(plan_amount, 0) AS monthly_amount
  FROM users
  WHERE plan_status = 'active'
    AND created_at <= CURRENT_DATE
) paid_users
GROUP BY current_month;

-- MRR Cohort Analysis
SELECT
  DATE_TRUNC('month', u.created_at) AS cohort_month,
  DATE_TRUNC('month', t.created_at) AS transaction_month,
  COUNT(DISTINCT u.user_id) AS users_with_revenue,
  SUM(CASE WHEN t.type = 'subscription' THEN COALESCE(t.amount, 0) ELSE 0 END) AS subscription_revenue,
  SUM(CASE WHEN t.type = 'purchase' THEN COALESCE(t.amount, 0) ELSE 0 END) AS purchase_revenue
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
  AND t.created_at >= DATE_TRUNC('month', u.created_at)
WHERE u.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '24 months')
GROUP BY cohort_month, transaction_month
ORDER BY cohort_month DESC, transaction_month DESC;
```

### Lifetime Value (LTV)
```sql
-- LTV by cohort
SELECT
  DATE_TRUNC('month', u.created_at) AS cohort_month,
  COUNT(DISTINCT u.user_id) AS cohort_size,
  ROUND(SUM(COALESCE(t.amount, 0)) / COUNT(DISTINCT u.user_id), 2) AS ltv_per_user,
  ROUND(SUM(COALESCE(t.amount, 0)), 0) AS total_revenue
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
WHERE u.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '24 months')
GROUP BY cohort_month
ORDER BY cohort_month DESC;

-- LTV by acquisition channel
SELECT
  COALESCE(u.utm_source, 'direct') AS channel,
  COUNT(DISTINCT u.user_id) AS users,
  ROUND(SUM(COALESCE(t.amount, 0)) / COUNT(DISTINCT u.user_id), 2) AS ltv_per_user
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY channel
ORDER BY ltv_per_user DESC;
```

### Net Revenue Retention (NRR)
```sql
-- Monthly NRR calculation
WITH starting_mrr AS (
  SELECT
    DATE_TRUNC('month', created_at) AS month,
    SUM(COALESCE(plan_amount, 0)) AS mrr_start
  FROM users
  WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', DATE_ADD(CURRENT_DATE, '-1 month'))
  GROUP BY DATE_TRUNC('month', created_at)
),
ending_mrr AS (
  SELECT
    DATE_TRUNC('month', CURRENT_DATE) AS month,
    SUM(CASE WHEN plan_status = 'active' THEN COALESCE(plan_amount, 0) ELSE 0 END) AS mrr_end,
    SUM(CASE WHEN DATE_TRUNC('month', cancelled_at) = DATE_TRUNC('month', CURRENT_DATE)
         THEN COALESCE(plan_amount, 0) ELSE 0 END) AS churned_mrr,
    SUM(CASE WHEN DATE_TRUNC('month', upgrade_date) = DATE_TRUNC('month', CURRENT_DATE)
         THEN COALESCE(upgrade_amount, 0) ELSE 0 END) AS expansion_mrr
  FROM users
  WHERE created_at <= CURRENT_DATE
)
SELECT
  e.month,
  s.mrr_start,
  e.mrr_end,
  e.churned_mrr,
  e.expansion_mrr,
  ROUND(100.0 * (e.mrr_end) / s.mrr_start, 1) AS nrr_pct
FROM starting_mrr s
JOIN ending_mrr e ON 1=1;
```

## Feature Adoption

### Feature Adoption Rate
```sql
-- Feature adoption by cohort
WITH feature_adoption AS (
  SELECT
    u.cohort_month,
    COUNT(DISTINCT u.user_id) AS cohort_size,
    COUNT(DISTINCT CASE WHEN f.user_id IS NOT NULL THEN u.user_id END) AS users_adopted,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN f.user_id IS NOT NULL THEN u.user_id END) /
      COUNT(DISTINCT u.user_id), 1) AS adoption_rate
  FROM users u
  LEFT JOIN events f ON u.user_id = f.user_id
    AND f.event_name = 'feature_x_used'
    AND f.event_timestamp <= CURRENT_DATE
  WHERE u.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
  GROUP BY u.cohort_month
)
SELECT
  cohort_month,
  cohort_size,
  users_adopted,
  adoption_rate
FROM feature_adoption
ORDER BY cohort_month DESC;

-- Time to feature adoption
WITH first_adoption AS (
  SELECT
    u.user_id,
    u.created_at AS signup_date,
    MIN(e.event_timestamp) AS first_use_date,
    DATE_DIFF(day, u.created_at, MIN(e.event_timestamp)) AS days_to_adoption
  FROM users u
  JOIN events e ON u.user_id = e.user_id
    AND e.event_name = 'feature_x_used'
  WHERE u.created_at >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY u.user_id, u.created_at
)
SELECT
  CASE
    WHEN days_to_adoption = 0 THEN 'Day 0'
    WHEN days_to_adoption = 1 THEN 'Day 1'
    WHEN days_to_adoption <= 7 THEN 'Day 2-7'
    WHEN days_to_adoption <= 30 THEN 'Day 8-30'
    ELSE '30+ days'
  END AS adoption_window,
  COUNT(*) AS users,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct_of_adopters
FROM first_adoption
GROUP BY adoption_window
ORDER BY adoption_window;
```

## Segmentation Analysis

### User Segmentation
```sql
-- User segments by characteristics
SELECT
  u.user_id,
  CASE
    WHEN u.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 'New (0-30d)'
    WHEN u.created_at >= CURRENT_DATE - INTERVAL '90 days' THEN 'Recent (30-90d)'
    ELSE 'Established (90d+)'
  END AS user_segment,
  COALESCE(u.utm_source, 'direct') AS acquisition_channel,
  COALESCE(u.plan_tier, 'free') AS plan_tier,
  COUNT(DISTINCT CASE WHEN e.event_timestamp >= CURRENT_DATE - INTERVAL '7 days' THEN DATE(e.event_timestamp) END) AS days_active_last_week
FROM users u
LEFT JOIN events e ON u.user_id = e.user_id
GROUP BY u.user_id, user_segment, acquisition_channel, plan_tier;

-- Segment performance summary
WITH user_segments AS (
  SELECT
    user_id,
    CASE
      WHEN days_since_signup <= 30 THEN 'New'
      WHEN days_since_signup <= 90 THEN 'Growing'
      WHEN days_since_signup <= 365 THEN 'Established'
      ELSE 'Mature'
    END AS segment
  FROM (
    SELECT
      user_id,
      DATE_DIFF(day, created_at, CURRENT_DATE) AS days_since_signup
    FROM users
  )
)
SELECT
  s.segment,
  COUNT(DISTINCT s.user_id) AS segment_size,
  COUNT(DISTINCT CASE WHEN e.event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
    THEN s.user_id END) AS active_last_7_days,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
    THEN s.user_id END) / COUNT(DISTINCT s.user_id), 1) AS activity_rate
FROM user_segments s
LEFT JOIN events e ON s.user_id = e.user_id
GROUP BY s.segment
ORDER BY segment;
```

## Diagnostics and Debugging

### Anomaly Detection - DAU Drop
```sql
-- Detect unusual drops in DAU
WITH daily_dau AS (
  SELECT
    DATE(event_timestamp) AS event_date,
    COUNT(DISTINCT user_id) AS dau
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY DATE(event_timestamp)
)
SELECT
  event_date,
  dau,
  LAG(dau) OVER (ORDER BY event_date) AS prev_dau,
  ROUND(100.0 * (dau - LAG(dau) OVER (ORDER BY event_date)) /
    LAG(dau) OVER (ORDER BY event_date), 2) AS day_over_day_change_pct,
  AVG(dau) OVER (ORDER BY event_date ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg_14d_prev,
  CASE
    WHEN dau < AVG(dau) OVER (ORDER BY event_date ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) * 0.85
      THEN 'ANOMALY - Drop'
    ELSE 'Normal'
  END AS status
FROM daily_dau
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY event_date DESC;
```

### Conversion Rate by Cohort and Traffic Source
```sql
-- Detailed acquisition funnel analysis
SELECT
  DATE_TRUNC('week', u.created_at) AS signup_week,
  COALESCE(u.utm_source, 'direct') AS source,
  COALESCE(u.utm_medium, 'none') AS medium,
  COUNT(DISTINCT u.user_id) AS signups,
  COUNT(DISTINCT CASE WHEN e.event_name = 'email_verified' THEN u.user_id END) AS activated,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'email_verified' THEN u.user_id END) /
    COUNT(DISTINCT u.user_id), 1) AS activation_rate
FROM users u
LEFT JOIN events e ON u.user_id = e.user_id
  AND e.event_name = 'email_verified'
WHERE u.created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY signup_week, source, medium
ORDER BY signup_week DESC, signups DESC;
```

## Performance Tips

1. **Use DATE() or DATE_TRUNC()** consistently for grouping
2. **Filter by date early** to reduce data scanned
3. **Use DISTINCT** efficiently; COUNT(DISTINCT) on indexed columns is faster
4. **Partition window functions** by user_id or other key dimension
5. **Pre-aggregate data** in underlying tables/views if possible
6. **Create materialized views** for common metrics dashboards
7. **Index event_timestamp and user_id** for fast filtering
8. **Archive old data** to separate cold storage after 12-24 months
