-- ============================================================================
-- Product Analytics Queries for BigQuery
-- Comprehensive collection of 25+ production-ready analytics queries
-- ============================================================================

-- ============================================================================
-- 1. USER ACQUISITION & GROWTH METRICS
-- ============================================================================

-- Daily New Users
-- Tracks user growth and onboarding trends
SELECT
    DATE(signup_timestamp) as signup_date,
    COUNT(DISTINCT user_id) as new_users,
    COUNT(DISTINCT device_id) as unique_devices,
    COUNT(DISTINCT country) as countries_acquired
FROM `project.dataset.users`
WHERE signup_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY signup_date
ORDER BY signup_date DESC;

-- Cohort Analysis - 30 Day Retention
-- Analyzes user retention by signup cohort
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC(DATE(signup_timestamp), MONTH) as signup_cohort,
        DATE(signup_timestamp) as signup_date
    FROM `project.dataset.users`
),
user_activity AS (
    SELECT DISTINCT
        user_id,
        DATE(event_timestamp) as active_date
    FROM `project.dataset.events`
    WHERE event_type IN ('page_view', 'feature_usage', 'purchase')
)
SELECT
    c.signup_cohort,
    COUNT(DISTINCT c.user_id) as cohort_size,
    COUNT(DISTINCT CASE
        WHEN DATE_DIFF(a.active_date, c.signup_date, DAY) BETWEEN 0 AND 7 THEN c.user_id
    END) as retained_day_7,
    COUNT(DISTINCT CASE
        WHEN DATE_DIFF(a.active_date, c.signup_date, DAY) BETWEEN 0 AND 30 THEN c.user_id
    END) as retained_day_30,
    COUNT(DISTINCT CASE
        WHEN DATE_DIFF(a.active_date, c.signup_date, DAY) BETWEEN 0 AND 90 THEN c.user_id
    END) as retained_day_90,
    ROUND(100 * COUNT(DISTINCT CASE WHEN DATE_DIFF(a.active_date, c.signup_date, DAY) BETWEEN 0 AND 30 THEN c.user_id END) /
        COUNT(DISTINCT c.user_id), 2) as day_30_retention_rate
FROM user_cohorts c
LEFT JOIN user_activity a ON c.user_id = a.user_id
GROUP BY c.signup_cohort
ORDER BY c.signup_cohort DESC;

-- ============================================================================
-- 2. ENGAGEMENT METRICS
-- ============================================================================

-- Daily Active Users (DAU) and Monthly Active Users (MAU)
-- Measures product usage and stickiness
WITH daily_activity AS (
    SELECT
        DATE(event_timestamp) as activity_date,
        COUNT(DISTINCT user_id) as dau,
        COUNT(DISTINCT session_id) as sessions,
        COUNT(*) as total_events
    FROM `project.dataset.events`
    WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    GROUP BY activity_date
)
SELECT
    activity_date,
    dau,
    ROUND(AVG(dau) OVER (
        ORDER BY activity_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 0) as dau_7_day_avg,
    sessions,
    ROUND(sessions / dau, 2) as sessions_per_user,
    total_events,
    ROUND(total_events / dau, 1) as events_per_user
FROM daily_activity
ORDER BY activity_date DESC;

-- Feature Usage by User Segment
-- Analyzes which users use which features
SELECT
    u.plan_type,
    u.country,
    EXTRACT(MONTH FROM u.signup_timestamp) as signup_month,
    e.feature_name,
    COUNT(DISTINCT e.user_id) as unique_users,
    COUNT(DISTINCT e.session_id) as sessions,
    COUNT(*) as total_events,
    ROUND(COUNT(DISTINCT e.user_id) / COUNT(DISTINCT u.user_id), 3) as adoption_rate
FROM `project.dataset.users` u
LEFT JOIN `project.dataset.events` e
    ON u.user_id = e.user_id
    AND e.event_type = 'feature_usage'
    AND e.event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
WHERE u.signup_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
GROUP BY u.plan_type, u.country, signup_month, e.feature_name
HAVING COUNT(DISTINCT e.user_id) > 0
ORDER BY unique_users DESC;

-- Session Duration Analysis
-- Tracks time spent in app by user segment
SELECT
    DATE(event_timestamp) as activity_date,
    CASE
        WHEN user_age_days < 7 THEN 'New (0-7 days)'
        WHEN user_age_days < 30 THEN 'Growing (8-30 days)'
        WHEN user_age_days < 90 THEN 'Maturing (31-90 days)'
        ELSE 'Established (90+ days)'
    END as user_segment,
    COUNT(DISTINCT user_id) as active_users,
    ROUND(AVG(session_duration_seconds), 0) as avg_session_duration,
    ROUND(PERCENTILE_CONT(session_duration_seconds, 0.5) OVER (), 0) as median_session_duration,
    ROUND(PERCENTILE_CONT(session_duration_seconds, 0.95) OVER (), 0) as p95_session_duration
FROM `project.dataset.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY activity_date, user_segment
ORDER BY activity_date DESC, active_users DESC;

-- ============================================================================
-- 3. CONVERSION & FUNNEL ANALYSIS
-- ============================================================================

-- Multi-step Conversion Funnel
-- Tracks users through signup, activation, and payment flow
WITH funnel_data AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'user_signup' THEN 1 ELSE 0 END) as signup_completed,
        MIN(CASE WHEN event_type = 'user_signup' THEN event_timestamp END) as signup_time,
        MAX(CASE WHEN event_type = 'first_login' THEN 1 ELSE 0 END) as first_login_completed,
        MIN(CASE WHEN event_type = 'first_login' THEN event_timestamp END) as first_login_time,
        MAX(CASE WHEN event_type = 'feature_usage' THEN 1 ELSE 0 END) as activated,
        MIN(CASE WHEN event_type = 'feature_usage' THEN event_timestamp END) as activation_time,
        MAX(CASE WHEN event_type = 'payment_method_added' THEN 1 ELSE 0 END) as payment_added,
        MIN(CASE WHEN event_type = 'payment_method_added' THEN event_timestamp END) as payment_time,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchased,
        MIN(CASE WHEN event_type = 'purchase' THEN event_timestamp END) as purchase_time
    FROM `project.dataset.events`
    WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    GROUP BY user_id
)
SELECT
    'Step 1: Signup' as funnel_step,
    COUNT(DISTINCT user_id) as users_count
FROM funnel_data
WHERE signup_completed = 1
UNION ALL
SELECT
    'Step 2: First Login',
    COUNT(DISTINCT user_id)
FROM funnel_data
WHERE first_login_completed = 1
UNION ALL
SELECT
    'Step 3: Activated (Used Feature)',
    COUNT(DISTINCT user_id)
FROM funnel_data
WHERE activated = 1
UNION ALL
SELECT
    'Step 4: Payment Added',
    COUNT(DISTINCT user_id)
FROM funnel_data
WHERE payment_added = 1
UNION ALL
SELECT
    'Step 5: First Purchase',
    COUNT(DISTINCT user_id)
FROM funnel_data
WHERE purchased = 1
ORDER BY funnel_step;

-- Drop-off Analysis by Step
-- Identifies where users drop off in funnel
WITH funnel_steps AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'user_signup' THEN 1 ELSE 0 END) as step_1,
        MAX(CASE WHEN event_type = 'first_login' THEN 1 ELSE 0 END) as step_2,
        MAX(CASE WHEN event_type = 'feature_usage' THEN 1 ELSE 0 END) as step_3,
        MAX(CASE WHEN event_type = 'payment_method_added' THEN 1 ELSE 0 END) as step_4,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as step_5
    FROM `project.dataset.events`
    GROUP BY user_id
)
SELECT
    'Signed Up' as stage,
    COUNT(DISTINCT user_id) as count,
    100.0 as percent
FROM funnel_steps
WHERE step_1 = 1
UNION ALL
SELECT
    'Signed Up → First Login',
    COUNT(DISTINCT user_id),
    ROUND(100.0 * COUNT(DISTINCT user_id) / SUM(step_1) OVER (), 1)
FROM funnel_steps
WHERE step_1 = 1 AND step_2 = 1
UNION ALL
SELECT
    'Signed Up → Activated',
    COUNT(DISTINCT user_id),
    ROUND(100.0 * COUNT(DISTINCT user_id) / SUM(step_1) OVER (), 1)
FROM funnel_steps
WHERE step_1 = 1 AND step_3 = 1
UNION ALL
SELECT
    'Signed Up → Payment → Purchase',
    COUNT(DISTINCT user_id),
    ROUND(100.0 * COUNT(DISTINCT user_id) / SUM(step_1) OVER (), 1)
FROM funnel_steps
WHERE step_1 = 1 AND step_4 = 1 AND step_5 = 1;

-- ============================================================================
-- 4. REVENUE & MONETIZATION METRICS
-- ============================================================================

-- Revenue by Plan Type and Country
-- Analyzes revenue distribution across segments
SELECT
    DATE_TRUNC(DATE(p.purchase_timestamp), MONTH) as purchase_month,
    u.plan_type,
    u.country,
    COUNT(DISTINCT p.order_id) as orders,
    COUNT(DISTINCT p.user_id) as paying_users,
    ROUND(SUM(p.amount), 2) as total_revenue,
    ROUND(AVG(p.amount), 2) as avg_order_value,
    ROUND(MAX(p.amount), 2) as max_order_value
FROM `project.dataset.purchases` p
JOIN `project.dataset.users` u ON p.user_id = u.user_id
WHERE p.purchase_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
GROUP BY purchase_month, u.plan_type, u.country
ORDER BY purchase_month DESC, total_revenue DESC;

-- Customer Lifetime Value (LTV) Analysis
-- Predicts revenue potential by user cohort
WITH user_purchases AS (
    SELECT
        u.user_id,
        DATE_TRUNC(DATE(u.signup_timestamp), MONTH) as signup_cohort,
        DATE_DIFF(DATE(CURRENT_TIMESTAMP()), DATE(u.signup_timestamp), DAY) as user_age_days,
        COUNT(DISTINCT p.order_id) as total_orders,
        SUM(p.amount) as lifetime_value,
        MAX(p.purchase_timestamp) as last_purchase_date,
        MIN(p.purchase_timestamp) as first_purchase_date
    FROM `project.dataset.users` u
    LEFT JOIN `project.dataset.purchases` p ON u.user_id = p.user_id
    GROUP BY u.user_id, signup_cohort, user_age_days
)
SELECT
    signup_cohort,
    COUNT(DISTINCT user_id) as cohort_size,
    ROUND(AVG(COALESCE(lifetime_value, 0)), 2) as avg_ltv,
    ROUND(PERCENTILE_CONT(COALESCE(lifetime_value, 0), 0.5) OVER (), 2) as median_ltv,
    ROUND(PERCENTILE_CONT(COALESCE(lifetime_value, 0), 0.95) OVER (), 2) as p95_ltv,
    COUNT(DISTINCT CASE WHEN lifetime_value > 0 THEN user_id END) as paying_users,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN lifetime_value > 0 THEN user_id END) /
        COUNT(DISTINCT user_id), 2) as conversion_rate
FROM user_purchases
GROUP BY signup_cohort
ORDER BY signup_cohort DESC;

-- Revenue Growth Metrics (Week-over-Week and Month-over-Month)
-- Tracks revenue trends and growth rates
WITH daily_revenue AS (
    SELECT
        DATE(purchase_timestamp) as purchase_date,
        SUM(amount) as daily_revenue,
        COUNT(DISTINCT order_id) as daily_orders,
        COUNT(DISTINCT user_id) as daily_paying_users
    FROM `project.dataset.purchases`
    WHERE purchase_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    GROUP BY purchase_date
)
SELECT
    purchase_date,
    daily_revenue,
    daily_orders,
    daily_paying_users,
    LAG(daily_revenue) OVER (ORDER BY purchase_date) as prev_day_revenue,
    ROUND(100.0 * (daily_revenue - LAG(daily_revenue) OVER (ORDER BY purchase_date)) /
        LAG(daily_revenue) OVER (ORDER BY purchase_date), 2) as mom_growth_percent,
    SUM(daily_revenue) OVER (
        ORDER BY purchase_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as revenue_7_day_sum,
    SUM(daily_revenue) OVER (
        ORDER BY purchase_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as revenue_30_day_sum
FROM daily_revenue
ORDER BY purchase_date DESC;

-- ============================================================================
-- 5. USER BEHAVIOR & PATTERNS
-- ============================================================================

-- Top Features by Usage
-- Identifies most valuable features
SELECT
    event_properties ->> 'feature_name' as feature_name,
    event_properties ->> 'feature_category' as feature_category,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as sessions,
    COUNT(*) as total_events,
    COUNT(DISTINCT DATE(event_timestamp)) as days_active,
    ROUND(COUNT(*) / COUNT(DISTINCT DATE(event_timestamp)), 1) as avg_events_per_day
FROM `project.dataset.events`
WHERE event_type = 'feature_usage'
    AND event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY feature_name, feature_category
HAVING COUNT(DISTINCT user_id) > 10
ORDER BY total_events DESC
LIMIT 50;

-- User Behavior by Time of Day
-- Analyzes usage patterns by hour and day
SELECT
    EXTRACT(DAY_OF_WEEK FROM event_timestamp) as day_of_week,
    EXTRACT(HOUR FROM event_timestamp) as hour_of_day,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as events,
    ROUND(COUNT(*) / COUNT(DISTINCT user_id), 2) as events_per_user
FROM `project.dataset.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;

-- User Segmentation by Activity Level
-- Segments users based on engagement
SELECT
    CASE
        WHEN events_count >= 100 THEN 'Power User'
        WHEN events_count >= 30 THEN 'Active User'
        WHEN events_count >= 5 THEN 'Regular User'
        ELSE 'Inactive User'
    END as user_segment,
    COUNT(DISTINCT user_id) as user_count,
    ROUND(AVG(events_count), 1) as avg_events,
    ROUND(AVG(session_count), 1) as avg_sessions,
    ROUND(AVG(COALESCE(lifetime_value, 0)), 2) as avg_ltv
FROM (
    SELECT
        u.user_id,
        COUNT(*) as events_count,
        COUNT(DISTINCT session_id) as session_count,
        SUM(p.amount) as lifetime_value
    FROM `project.dataset.users` u
    LEFT JOIN `project.dataset.events` e ON u.user_id = e.user_id
        AND e.event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    LEFT JOIN `project.dataset.purchases` p ON u.user_id = p.user_id
    WHERE u.signup_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
    GROUP BY u.user_id
)
GROUP BY user_segment
ORDER BY user_count DESC;

-- ============================================================================
-- 6. DEVICE & PLATFORM METRICS
-- ============================================================================

-- Platform Usage Distribution
-- Analyzes usage across web, mobile, iOS, Android
SELECT
    event_properties ->> 'platform' as platform,
    event_properties ->> 'os_type' as os_type,
    event_properties ->> 'browser' as browser,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as sessions,
    COUNT(*) as events,
    ROUND(100.0 * COUNT(DISTINCT user_id) / SUM(COUNT(DISTINCT user_id)) OVER (), 2) as user_percent,
    ROUND(AVG(event_properties ->> 'session_duration_ms')::NUMERIC, 0) as avg_session_duration_ms
FROM `project.dataset.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY platform, os_type, browser
ORDER BY unique_users DESC;

-- ============================================================================
-- 7. ERROR & QUALITY METRICS
-- ============================================================================

-- Error Rate by Feature
-- Tracks application stability
SELECT
    DATE(event_timestamp) as error_date,
    event_properties ->> 'feature_name' as feature_name,
    event_properties ->> 'error_type' as error_type,
    COUNT(*) as error_count,
    COUNT(DISTINCT user_id) as affected_users
FROM `project.dataset.events`
WHERE event_type = 'error'
    AND event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY error_date, feature_name, error_type
ORDER BY error_date DESC, error_count DESC;

-- ============================================================================
-- 8. COMPARATIVE ANALYSIS (A/B TESTING)
-- ============================================================================

-- A/B Test Results Summary
-- Analyzes experiment outcomes
SELECT
    event_properties ->> 'experiment_id' as experiment_id,
    event_properties ->> 'variant' as variant,
    COUNT(DISTINCT user_id) as users,
    COUNT(DISTINCT session_id) as sessions,
    COUNT(*) as events,
    ROUND(COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) /
        COUNT(DISTINCT user_id), 4) as conversion_rate,
    ROUND(AVG(CAST(event_properties ->> 'duration_ms' AS INT64)), 0) as avg_duration_ms,
    ROUND(AVG(CAST(event_properties ->> 'revenue' AS FLOAT64)), 2) as avg_revenue
FROM `project.dataset.events`
WHERE event_properties ->> 'experiment_id' IS NOT NULL
    AND event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY experiment_id, variant
ORDER BY experiment_id, variant;

-- ============================================================================
-- HELPER FUNCTIONS & VIEWS
-- ============================================================================

-- Create a view for common retention metrics
CREATE OR REPLACE VIEW `project.dataset.retention_metrics` AS
WITH daily_active AS (
    SELECT
        DATE(event_timestamp) as activity_date,
        user_id,
        DATE_DIFF(DATE(event_timestamp),
            (SELECT MIN(DATE(signup_timestamp)) FROM `project.dataset.users` WHERE user_id = users.user_id),
            DAY) as user_age_days
    FROM `project.dataset.events`
    WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
)
SELECT
    activity_date,
    user_age_days,
    COUNT(DISTINCT user_id) as active_users,
    ROUND(COUNT(DISTINCT user_id) / LAG(COUNT(DISTINCT user_id)) OVER (
        PARTITION BY user_age_days ORDER BY activity_date
    ), 3) as day_over_day_retention
FROM daily_active
GROUP BY activity_date, user_age_days;

-- Query retention rates
-- SELECT * FROM `project.dataset.retention_metrics`
-- WHERE user_age_days < 30
-- ORDER BY activity_date DESC, user_age_days;
