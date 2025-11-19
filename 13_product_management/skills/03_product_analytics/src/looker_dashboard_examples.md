# Looker Dashboard Examples - LookML Guide

## Overview

This guide provides production-ready LookML examples for building comprehensive analytics dashboards in Looker. Includes metrics definitions, tile configurations, and dashboard layouts for product analytics.

---

## 1. Executive KPI Dashboard

### Dashboard Configuration

```lookml
dashboard: executive_kpi_dashboard {
  title: "Executive KPI Dashboard"
  description: "Real-time key metrics and performance indicators"
  layout: static
  elements_size_preset: medium

  # Tile 1: Monthly Revenue
  element: monthly_revenue {
    title: "Monthly Revenue"
    query: revenue_by_month {
      dimensions: month
      measures: total_revenue
      filters: {
        field: orders.created_date
        value: "1 months"
      }
    }
    visualization: looker_column
    x: 0
    y: 0
    width: 6
    height: 4
  }

  # Tile 2: YoY Growth Rate
  element: yoy_growth {
    title: "Year-over-Year Growth"
    query: revenue_comparison
    visualization: looker_gauge
    x: 6
    y: 0
    width: 6
    height: 4
  }

  # Tile 3: Active Users Trend
  element: active_users {
    title: "Monthly Active Users"
    query: mau_trend
    visualization: looker_line
    x: 0
    y: 4
    width: 6
    height: 4
  }

  # Tile 4: Conversion Rate
  element: conversion_rate {
    title: "Funnel Conversion Rate"
    query: conversion_metrics
    visualization: looker_gauge
    x: 6
    y: 4
    width: 6
    height: 4
  }
}
```

### Revenue by Month Query

```lookml
view: revenue_by_month {
  derived_table: {
    sql: SELECT
      DATE_TRUNC(orders.created_at, MONTH) as month,
      SUM(orders.amount) as total_revenue,
      COUNT(DISTINCT orders.user_id) as unique_customers,
      AVG(orders.amount) as avg_order_value
    FROM orders
    WHERE orders.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
    GROUP BY 1
    ORDER BY 1 DESC
    ;;
  }

  dimension: month {
    type: date
    sql: ${TABLE}.month ;;
  }

  dimension: total_revenue {
    type: number
    sql: ${TABLE}.total_revenue ;;
  }

  measure: revenue_sum {
    type: sum
    sql: ${TABLE}.total_revenue ;;
    value_format_name: usd_large
  }

  measure: customer_count {
    type: sum
    sql: ${TABLE}.unique_customers ;;
  }

  measure: avg_order_value {
    type: average
    sql: ${TABLE}.avg_order_value ;;
    value_format_name: usd
  }
}
```

---

## 2. Conversion Funnel Dashboard

### LookML Definition

```lookml
dashboard: conversion_funnel {
  title: "Conversion Funnel Analysis"
  description: "User journey and drop-off analysis"
  layout: static

  filter: date_range {
    type: date_filters
    default_value: "1 months"
  }

  filter: segment {
    type: field_filter
    explore: users
    field: users.segment
  }

  # Funnel visualization
  element: funnel_viz {
    title: "User Conversion Funnel"
    query: conversion_funnel_query
    visualization: looker_funnel
    x: 0
    y: 0
    width: 12
    height: 6
  }

  # Segment comparison
  element: segment_comparison {
    title: "Segment Performance"
    query: segment_funnel_comparison
    visualization: looker_bar
    x: 0
    y: 6
    width: 12
    height: 6
  }

  # Conversion metrics table
  element: funnel_metrics {
    title: "Detailed Funnel Metrics"
    query: funnel_details
    visualization: looker_grid
    x: 0
    y: 12
    width: 12
    height: 5
  }
}
```

### Funnel Query with CTEs

```lookml
view: conversion_funnel_query {
  derived_table: {
    sql:
    WITH funnel_stages AS (
      SELECT
        'Visitors' as stage,
        1 as stage_order,
        COUNT(DISTINCT user_id) as count
      FROM page_views
      WHERE DATE(created_at) >= CURRENT_DATE() - 30

      UNION ALL

      SELECT
        'Signups' as stage,
        2 as stage_order,
        COUNT(DISTINCT user_id) as count
      FROM users
      WHERE DATE(created_at) >= CURRENT_DATE() - 30
        AND source IS NOT NULL

      UNION ALL

      SELECT
        'Activated' as stage,
        3 as stage_order,
        COUNT(DISTINCT user_id) as count
      FROM users
      WHERE DATE(created_at) >= CURRENT_DATE() - 30
        AND activation_date IS NOT NULL

      UNION ALL

      SELECT
        'Paid Customers' as stage,
        4 as stage_order,
        COUNT(DISTINCT user_id) as count
      FROM orders
      WHERE DATE(created_at) >= CURRENT_DATE() - 30
        AND status = 'completed'

      UNION ALL

      SELECT
        'Retained (30d)' as stage,
        5 as stage_order,
        COUNT(DISTINCT user_id) as count
      FROM orders
      WHERE DATE(created_at) >= CURRENT_DATE() - 60
        AND DATE(created_at) <= CURRENT_DATE() - 30
    )
    SELECT
      stage,
      stage_order,
      count,
      ROUND(100.0 * count / LAG(count) OVER (ORDER BY stage_order) BETWEEN 0 AND 100, 2) as conversion_rate
    FROM funnel_stages
    ORDER BY stage_order
    ;;
  }

  dimension: stage {
    type: string
    sql: ${TABLE}.stage ;;
  }

  measure: user_count {
    type: number
    sql: ${TABLE}.count ;;
  }

  measure: conversion_rate {
    type: number
    sql: ${TABLE}.conversion_rate ;;
    value_format_name: percent_2
  }
}
```

---

## 3. Cohort Analysis Dashboard

### Cohort View Definition

```lookml
view: cohort_analysis {
  derived_table: {
    sql:
    WITH user_cohorts AS (
      SELECT
        user_id,
        DATE_TRUNC(created_at, MONTH) as cohort_month
      FROM users
      WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
    ),
    monthly_activity AS (
      SELECT
        uc.user_id,
        uc.cohort_month,
        DATE_TRUNC(o.created_at, MONTH) as activity_month,
        DATE_DIFF(DATE_TRUNC(o.created_at, MONTH), uc.cohort_month, MONTH) as months_since_signup
      FROM user_cohorts uc
      LEFT JOIN orders o
        ON uc.user_id = o.user_id
      WHERE o.created_at IS NULL OR o.created_at >= uc.created_at
    )
    SELECT
      cohort_month,
      months_since_signup,
      COUNT(DISTINCT user_id) as active_users,
      COUNT(DISTINCT CASE WHEN activity_month IS NOT NULL THEN user_id END) as retained_users
    FROM monthly_activity
    GROUP BY 1, 2
    HAVING months_since_signup IS NOT NULL
    ;;
  }

  dimension: cohort_month {
    type: date
    sql: ${TABLE}.cohort_month ;;
  }

  dimension: months_since_signup {
    type: number
    sql: ${TABLE}.months_since_signup ;;
  }

  measure: cohort_size {
    type: number
    sql: ${TABLE}.active_users ;;
  }

  measure: retained_count {
    type: sum
    sql: ${TABLE}.retained_users ;;
  }

  measure: retention_rate {
    type: number
    sql: ROUND(100.0 * ${retained_count} / ${cohort_size}, 1) ;;
    value_format_name: percent_0
  }
}
```

### Cohort Dashboard

```lookml
dashboard: cohort_retention {
  title: "Cohort Retention Analysis"
  description: "User retention by acquisition cohort"

  element: retention_heatmap {
    title: "Monthly Retention Heatmap"
    query: cohort_retention_query
    visualization: looker_heatmap
    x: 0
    y: 0
    width: 12
    height: 8
  }

  element: cohort_trends {
    title: "Cohort Trend Comparison"
    query: cohort_trend_query
    visualization: looker_line
    x: 0
    y: 8
    width: 12
    height: 6
  }
}
```

---

## 4. Feature Adoption Dashboard

### Feature Usage View

```lookml
view: feature_adoption {
  sql_table_name: feature_events ;;

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }

  dimension: user_id {
    type: number
    sql: ${TABLE}.user_id ;;
  }

  dimension: feature_name {
    type: string
    sql: ${TABLE}.feature_name ;;
  }

  dimension: event_date {
    type: date
    sql: ${TABLE}.created_at ;;
  }

  dimension: event_timestamp {
    type: time
    timeframes: [time, date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
  }

  measure: event_count {
    type: count
    drill_fields: [user_id, feature_name, event_timestamp]
  }

  measure: unique_users {
    type: count_distinct
    sql: ${TABLE}.user_id ;;
  }

  measure: adoption_rate {
    type: number
    sql: ROUND(100.0 * ${unique_users} / (
      SELECT COUNT(DISTINCT user_id)
      FROM users
      WHERE DATE(created_at) <= ${event_date._value}
    ), 2) ;;
    value_format_name: percent_2
  }
}
```

### Feature Adoption Dashboard

```lookml
dashboard: feature_adoption_dashboard {
  title: "Feature Adoption & Usage"
  description: "Track feature adoption rates and usage patterns"

  filter: time_range {
    type: date_filters
    default_value: "last_30_days"
  }

  element: adoption_rates {
    title: "Feature Adoption Rate"
    query: feature_adoption_rates
    visualization: looker_bar
    x: 0
    y: 0
    width: 6
    height: 5
  }

  element: dau_by_feature {
    title: "Daily Active Users by Feature"
    query: feature_dau
    visualization: looker_area
    x: 6
    y: 0
    width: 6
    height: 5
  }

  element: feature_trends {
    title: "Feature Usage Trends (30-day)"
    query: feature_usage_trends
    visualization: looker_line
    x: 0
    y: 5
    width: 12
    height: 6
  }

  element: feature_details {
    title: "Feature Usage Details"
    query: feature_usage_details
    visualization: looker_grid
    x: 0
    y: 11
    width: 12
    height: 6
  }
}
```

---

## 5. Real-Time Operational Dashboard

### Real-Time Metrics View

```lookml
view: realtime_metrics {
  derived_table: {
    sql:
    SELECT
      DATE_TRUNC(CURRENT_TIMESTAMP(), HOUR) as hour,
      COUNT(*) as request_count,
      SUM(CASE WHEN error = true THEN 1 ELSE 0 END) as error_count,
      ROUND(AVG(response_time_ms), 2) as avg_latency,
      MAX(response_time_ms) as max_latency,
      PERCENTILE_CONT(response_time_ms, 0.95) OVER () as p95_latency
    FROM request_logs
    WHERE created_at >= CURRENT_TIMESTAMP() - INTERVAL '24 HOUR'
    GROUP BY 1
    ;;
    datagroup_trigger: realtime_refresh
  }

  dimension: hour {
    type: time
    timeframes: [time, hour, date]
    sql: ${TABLE}.hour ;;
  }

  measure: request_volume {
    type: sum
    sql: ${TABLE}.request_count ;;
    label: "Total Requests"
  }

  measure: error_count {
    type: sum
    sql: ${TABLE}.error_count ;;
  }

  measure: error_rate {
    type: number
    sql: ROUND(100.0 * ${error_count} / ${request_volume}, 2) ;;
    value_format_name: percent_2
  }

  measure: avg_latency {
    type: average
    sql: ${TABLE}.avg_latency ;;
    value_format_name: decimal_2
    label: "Avg Latency (ms)"
  }

  measure: p95_latency {
    type: max
    sql: ${TABLE}.p95_latency ;;
    value_format_name: decimal_2
    label: "P95 Latency (ms)"
  }
}
```

### Real-Time Dashboard

```lookml
dashboard: realtime_operational_monitoring {
  title: "Real-Time Operational Monitoring"
  description: "24-hour system health and performance metrics"
  refresh_interval: 1
  auto_tile_reset: false

  # KPI Cards
  element: current_errors {
    title: "Current Error Rate"
    query: realtime_error_rate
    visualization: looker_single_record
    value_format_name: percent_2
    x: 0
    y: 0
    width: 3
    height: 2
  }

  element: current_latency {
    title: "Current P95 Latency"
    query: realtime_p95_latency
    visualization: looker_single_record
    value_format_name: decimal_0
    x: 3
    y: 0
    width: 3
    height: 2
  }

  element: current_requests {
    title: "Requests (Last Hour)"
    query: realtime_request_volume
    visualization: looker_single_record
    value_format_name: number_with_commas
    x: 6
    y: 0
    width: 3
    height: 2
  }

  element: system_health {
    title: "System Health"
    query: realtime_health_status
    visualization: looker_gauge
    x: 9
    y: 0
    width: 3
    height: 2
  }

  # 24-hour trend charts
  element: request_trend {
    title: "Request Volume (24h)"
    query: realtime_24h_requests
    visualization: looker_column
    x: 0
    y: 2
    width: 6
    height: 4
  }

  element: error_trend {
    title: "Error Rate (24h)"
    visualization: looker_area
    x: 6
    y: 2
    width: 6
    height: 4
  }

  element: latency_trend {
    title: "Latency Percentiles (24h)"
    query: realtime_latency_percentiles
    visualization: looker_line
    x: 0
    y: 6
    width: 12
    height: 5
  }
}
```

---

## 6. User Segmentation Dashboard

### Segment Analysis View

```lookml
view: user_segments {
  derived_table: {
    sql:
    SELECT
      user_id,
      -- Recency (days since last purchase)
      DATE_DIFF(CURRENT_DATE(), MAX(order_date), DAY) as recency_days,
      -- Frequency (number of purchases)
      COUNT(DISTINCT order_id) as purchase_frequency,
      -- Monetary (total revenue)
      SUM(order_amount) as lifetime_value,
      -- Segment assignment using RFM
      CASE
        WHEN DATE_DIFF(CURRENT_DATE(), MAX(order_date), DAY) <= 30
             AND COUNT(DISTINCT order_id) >= 5
             AND SUM(order_amount) >= 1000
        THEN 'VIP'
        WHEN DATE_DIFF(CURRENT_DATE(), MAX(order_date), DAY) <= 90
             AND COUNT(DISTINCT order_id) >= 3
        THEN 'Loyal'
        WHEN DATE_DIFF(CURRENT_DATE(), MAX(order_date), DAY) <= 180
        THEN 'At Risk'
        ELSE 'Inactive'
      END as rfm_segment
    FROM orders
    WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
    GROUP BY user_id
    ;;
  }

  dimension: user_id {
    primary_key: yes
    type: number
    sql: ${TABLE}.user_id ;;
  }

  dimension: recency_days {
    type: number
    sql: ${TABLE}.recency_days ;;
  }

  dimension: purchase_frequency {
    type: number
    sql: ${TABLE}.purchase_frequency ;;
  }

  dimension: lifetime_value {
    type: number
    sql: ${TABLE}.lifetime_value ;;
    value_format_name: usd
  }

  dimension: rfm_segment {
    type: string
    sql: ${TABLE}.rfm_segment ;;
  }

  measure: segment_count {
    type: count_distinct
    sql: ${TABLE}.user_id ;;
    label: "User Count"
  }

  measure: avg_ltv {
    type: average
    sql: ${TABLE}.lifetime_value ;;
    value_format_name: usd
    label: "Average LTV"
  }

  measure: total_revenue {
    type: sum
    sql: ${TABLE}.lifetime_value ;;
    value_format_name: usd_large
  }
}
```

### Segmentation Dashboard

```lookml
dashboard: user_segmentation {
  title: "RFM User Segmentation"
  description: "Customer lifetime value and segment analysis"

  element: segment_distribution {
    title: "User Distribution by Segment"
    query: segment_counts
    visualization: looker_pie
    x: 0
    y: 0
    width: 6
    height: 5
  }

  element: segment_revenue {
    title: "Revenue by Segment"
    query: segment_revenue
    visualization: looker_column
    x: 6
    y: 0
    width: 6
    height: 5
  }

  element: segment_metrics {
    title: "Segment Metrics"
    query: segment_analysis
    visualization: looker_grid
    x: 0
    y: 5
    width: 12
    height: 6
  }
}
```

---

## 7. Best Practices for LookML Dashboards

### Performance Optimization

```lookml
# Use persistent derived tables for complex queries
view: optimized_metrics {
  derived_table: {
    # SQL trigger for daily refresh
    sql_trigger_value: SELECT DATE(CURRENT_TIMESTAMP()) ;;

    indexes: ["cohort_month", "user_id"]

    sql:
    SELECT
      DATE_TRUNC(created_at, DAY) as date,
      user_id,
      COUNT(*) as events
    FROM events
    WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    GROUP BY 1, 2
    ;;
  }
}
```

### Parameterized Dashboards

```lookml
dashboard: parameterized_analytics {
  title: "Parameterized Analytics Dashboard"

  # Filter parameters
  filter: metric_selector {
    type: string
    allowed_value: { label: "Revenue" value: "revenue" }
    allowed_value: { label: "Users" value: "users" }
    allowed_value: { label: "Conversion Rate" value: "conversion" }
    default_value: "revenue"
  }

  filter: date_granularity {
    type: string
    allowed_value: { label: "Daily" value: "day" }
    allowed_value: { label: "Weekly" value: "week" }
    allowed_value: { label: "Monthly" value: "month" }
    default_value: "week"
  }

  # Conditional queries using Liquid
  element: dynamic_metric {
    title: "{% if _filters['metric_selector'] == 'revenue' %}Revenue Trend
            {% elsif _filters['metric_selector'] == 'users' %}User Growth
            {% else %}Conversion Rate{% endif %}"
    query: dynamic_metrics_query
    visualization: looker_line
  }
}
```

---

## Implementation Checklist

- [ ] Define derived tables with appropriate indexing
- [ ] Set up datagroup triggers for refresh cadence
- [ ] Create reusable dimensions and measures
- [ ] Implement row-level security where needed
- [ ] Add drill-down capabilities to tiles
- [ ] Set up alerting thresholds
- [ ] Test dashboard performance
- [ ] Document filter dependencies
- [ ] Create mobile-friendly layouts
- [ ] Enable scheduled email deliveries

---

## Resources

- [Looker LookML Reference](https://cloud.google.com/looker/docs/r/dashboards)
- [Dashboard Best Practices](https://cloud.google.com/looker/docs/dashboards)
- [Performance Optimization](https://cloud.google.com/looker/docs/r/performance)
