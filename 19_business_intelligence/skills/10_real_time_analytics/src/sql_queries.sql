-- Real-Time Analytics SQL Queries

-- Hourly event counts
SELECT
    toStartOfHour(event_time) AS hour,
    event_type,
    count() AS event_count,
    sum(revenue) AS total_revenue,
    uniq(user_id) AS unique_users
FROM events
WHERE event_time >= now() - INTERVAL 24 HOUR
GROUP BY hour, event_type
ORDER BY hour DESC;

-- User cohort analysis
SELECT
    toMonday(first_event_date) AS cohort_week,
    COUNT(DISTINCT user_id) AS cohort_size,
    AVG(total_revenue) AS avg_revenue_per_user
FROM (
    SELECT
        user_id,
        min(event_time) AS first_event_date,
        sum(revenue) AS total_revenue
    FROM events
    GROUP BY user_id
)
GROUP BY cohort_week
ORDER BY cohort_week DESC;

-- Real-time funnel
WITH funnel AS (
    SELECT
        user_id,
        countIf(event_type = 'page_view') AS views,
        countIf(event_type = 'add_to_cart') AS adds,
        countIf(event_type = 'purchase') AS purchases
    FROM events
    WHERE event_time >= now() - INTERVAL 1 HOUR
    GROUP BY user_id
)
SELECT
    COUNT(*) AS total_users,
    countIf(views > 0) AS viewed,
    countIf(adds > 0) AS added_to_cart,
    countIf(purchases > 0) AS purchased,
    countIf(adds > 0) / countIf(views > 0) * 100 AS view_to_cart_rate,
    countIf(purchases > 0) / countIf(adds > 0) * 100 AS cart_to_purchase_rate
FROM funnel;
