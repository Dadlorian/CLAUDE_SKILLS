# Event Stream Analytics Guide

## Real-Time Funnel Analysis
```sql
-- Flink SQL
CREATE VIEW conversion_funnel AS
SELECT
    user_id,
    COUNT(CASE WHEN event_type = 'page_view' THEN 1 END) as views,
    COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) as adds,
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases
FROM events
GROUP BY TUMBLE(event_time, INTERVAL '1' HOUR), user_id;
```

## Session Analytics
```java
events
    .keyBy(Event::getUserId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .aggregate(new SessionAggregator());
```

## Cohort Analysis
```sql
SELECT
    toStartOfWeek(first_purchase_date) AS cohort,
    COUNT(DISTINCT user_id) AS cohort_size,
    SUM(revenue) AS total_revenue
FROM user_purchases
GROUP BY cohort;
```

## Real-Time Anomaly Detection
```java
events
    .keyBy(Event::getMetricName)
    .flatMap(new AnomalyDetector());
```
