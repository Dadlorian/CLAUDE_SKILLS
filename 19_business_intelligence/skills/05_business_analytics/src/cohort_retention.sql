-- Cohort Retention Analysis
-- Calculate monthly retention rates for user cohorts

WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date) AS cohort_month
    FROM users
),
monthly_activity AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', activity_date) AS activity_month
    FROM user_activities
    WHERE activity_type IN ('login', 'purchase', 'engagement')
),
cohort_activity AS (
    SELECT
        uc.cohort_month,
        ma.activity_month,
        EXTRACT(MONTH FROM AGE(ma.activity_month, uc.cohort_month)) AS months_since_signup,
        COUNT(DISTINCT ma.user_id) AS active_users
    FROM user_cohorts uc
    LEFT JOIN monthly_activity ma ON uc.user_id = ma.user_id
    WHERE ma.activity_month >= uc.cohort_month
    GROUP BY 1, 2, 3
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM user_cohorts
    GROUP BY 1
)
SELECT
    ca.cohort_month,
    ca.months_since_signup,
    cs.cohort_size,
    ca.active_users,
    ROUND(ca.active_users * 100.0 / cs.cohort_size, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.months_since_signup;
