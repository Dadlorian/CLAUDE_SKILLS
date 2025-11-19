# LookML Syntax Reference

## LookML Fundamentals

### Project Structure
```
my_project/
├── models/
│   └── ecommerce.model.lkml
├── views/
│   ├── orders.view.lkml
│   ├── users.view.lkml
│   └── products.view.lkml
├── dashboards/
│   └── sales_overview.dashboard.lookml
└── manifest.lkml
```

### Model File
```lookml
# ecommerce.model.lkml
connection: "production_db"

include: "/views/*.view.lkml"
include: "/dashboards/*.dashboard.lookml"

datagroup: daily_refresh {
  sql_trigger: SELECT MAX(updated_at) FROM orders ;;
  max_cache_age: "24 hours"
}

persist_with: daily_refresh

explore: orders {
  label: "Sales Orders"

  join: users {
    type: left_outer
    sql_on: ${orders.user_id} = ${users.id} ;;
    relationship: many_to_one
  }

  join: products {
    type: left_outer
    sql_on: ${orders.product_id} = ${products.id} ;;
    relationship: many_to_one
  }
}

explore: +orders {
  # Extension/refinement of orders explore
  join: user_facts {
    type: left_outer
    sql_on: ${orders.user_id} = ${user_facts.user_id} ;;
    relationship: many_to_one
  }
}
```

## View Definitions

### Basic View
```lookml
# orders.view.lkml
view: orders {
  sql_table_name: public.orders ;;

  # Primary key
  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }

  # Dimensions
  dimension: user_id {
    type: number
    hidden: yes  # Don't show in field picker
    sql: ${TABLE}.user_id ;;
  }

  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
  }

  dimension_group: created {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.created_at ;;
  }

  # Measures
  measure: count {
    type: count
    drill_fields: [detail*]
  }

  measure: total_amount {
    type: sum
    sql: ${amount} ;;
    value_format_name: usd
  }

  measure: average_amount {
    type: average
    sql: ${amount} ;;
    value_format_name: usd_0
  }

  # Drill fields
  set: detail {
    fields: [
      id,
      created_date,
      user.name,
      amount
    ]
  }
}
```

### Dimension Types
```lookml
view: examples {

  # String dimension
  dimension: name {
    type: string
    sql: ${TABLE}.name ;;
  }

  # Number dimension
  dimension: quantity {
    type: number
    sql: ${TABLE}.quantity ;;
  }

  # Date/time dimensions
  dimension_group: order {
    type: time
    timeframes: [date, week, month, year]
    sql: ${TABLE}.order_date ;;
  }

  # Duration (between two times)
  dimension: days_since_order {
    type: duration_day
    sql_start: ${order_raw} ;;
    sql_end: CURRENT_TIMESTAMP ;;
  }

  # Yesno (boolean)
  dimension: is_cancelled {
    type: yesno
    sql: ${TABLE}.status = 'cancelled' ;;
  }

  # Tier (bucketing)
  dimension: amount_tier {
    type: tier
    tiers: [0, 10, 50, 100, 500]
    style: integer
    sql: ${amount} ;;
  }

  # Location (for mapping)
  dimension: location {
    type: location
    sql_latitude: ${TABLE}.latitude ;;
    sql_longitude: ${TABLE}.longitude ;;
  }

  # Zipcode (geographic)
  dimension: zip {
    type: zipcode
    sql: ${TABLE}.zipcode ;;
  }
}
```

### Calculated Dimensions
```lookml
view: calculated_examples {

  dimension: full_name {
    type: string
    sql: CONCAT(${TABLE}.first_name, ' ', ${TABLE}.last_name) ;;
  }

  dimension: age {
    type: number
    sql: DATEDIFF(year, ${TABLE}.birth_date, CURRENT_DATE) ;;
  }

  dimension: age_group {
    type: string
    sql:
      CASE
        WHEN ${age} < 18 THEN 'Under 18'
        WHEN ${age} < 35 THEN '18-34'
        WHEN ${age} < 55 THEN '35-54'
        ELSE '55+'
      END ;;
  }

  dimension: profit_margin {
    type: number
    sql: 1.0 * (${TABLE}.revenue - ${TABLE}.cost) / NULLIF(${TABLE}.revenue, 0) ;;
    value_format_name: percent_2
  }

  # Using liquid templating
  dimension: dynamic_timeframe {
    type: string
    sql:
      {% if orders.created_date._is_selected %}
        ${created_date}
      {% elsif orders.created_week._is_selected %}
        ${created_week}
      {% else %}
        ${created_month}
      {% endif %} ;;
  }
}
```

### Measure Types
```lookml
view: measure_examples {

  # Count measures
  measure: count {
    type: count
  }

  measure: distinct_count {
    type: count_distinct
    sql: ${user_id} ;;
  }

  # Aggregation measures
  measure: total_revenue {
    type: sum
    sql: ${revenue} ;;
    value_format_name: usd
  }

  measure: average_revenue {
    type: average
    sql: ${revenue} ;;
    value_format_name: usd_0
  }

  measure: min_price {
    type: min
    sql: ${price} ;;
  }

  measure: max_price {
    type: max
    sql: ${price} ;;
  }

  measure: median_price {
    type: median
    sql: ${price} ;;
  }

  # Percentile
  measure: price_95th_percentile {
    type: percentile
    percentile: 95
    sql: ${price} ;;
  }

  # Custom SQL measure
  measure: conversion_rate {
    type: number
    sql: 1.0 * ${orders.count} / NULLIF(${sessions.count}, 0) ;;
    value_format_name: percent_2
  }

  # Measure with filters
  measure: high_value_orders {
    type: count
    filters: [amount: ">100"]
  }

  measure: electronics_revenue {
    type: sum
    sql: ${revenue} ;;
    filters: [category: "Electronics"]
  }

  # Running total (requires pivot/table calc in UI)
  measure: running_total_revenue {
    type: running_total
    sql: ${total_revenue} ;;
  }
}
```

## Derived Tables

### SQL Derived Table
```lookml
view: user_order_facts {
  derived_table: {
    sql:
      SELECT
        user_id,
        MIN(created_at) AS first_order_date,
        MAX(created_at) AS latest_order_date,
        COUNT(*) AS lifetime_orders,
        SUM(amount) AS lifetime_revenue
      FROM orders
      GROUP BY user_id ;;
  }

  dimension: user_id {
    primary_key: yes
    type: number
    sql: ${TABLE}.user_id ;;
  }

  dimension_group: first_order {
    type: time
    timeframes: [date, week, month]
    sql: ${TABLE}.first_order_date ;;
  }

  dimension: lifetime_orders {
    type: number
    sql: ${TABLE}.lifetime_orders ;;
  }

  measure: average_lifetime_revenue {
    type: average
    sql: ${TABLE}.lifetime_revenue ;;
    value_format_name: usd
  }
}
```

### Persistent Derived Table (PDT)
```lookml
view: daily_sales_summary {
  derived_table: {
    sql:
      SELECT
        DATE(created_at) AS sale_date,
        product_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_revenue
      FROM orders
      GROUP BY 1, 2 ;;

    # PDT configuration
    sql_trigger_value: SELECT CURRENT_DATE ;;
    # OR
    datagroup_trigger: daily_refresh

    # Indexes for performance
    indexes: ["sale_date", "product_id"]

    # Distribution/sorting (for certain databases)
    distribution: "product_id"
    sortkeys: ["sale_date"]
  }

  dimension: sale_date {
    type: date
    sql: ${TABLE}.sale_date ;;
  }

  dimension: product_id {
    type: number
    sql: ${TABLE}.product_id ;;
  }

  measure: total_order_count {
    type: sum
    sql: ${TABLE}.order_count ;;
  }
}
```

### Native Derived Table (NDT)
```lookml
view: user_aggregates {
  derived_table: {
    explore_source: orders {
      column: user_id {}
      column: total_revenue { field: orders.total_amount }
      column: order_count { field: orders.count }

      filters: [
        orders.created_date: "30 days"
      ]
    }
  }

  dimension: user_id {
    type: number
  }

  dimension: total_revenue {
    type: number
    value_format_name: usd
  }

  dimension: order_count {
    type: number
  }
}
```

## Advanced LookML Patterns

### Extends and Refinements
```lookml
# Base view
view: base_orders {
  sql_table_name: public.orders ;;

  dimension: id {
    primary_key: yes
    type: number
  }

  dimension: amount {
    type: number
  }
}

# Extended view
view: orders {
  extends: [base_orders]

  # Add new dimensions
  dimension: amount_tier {
    type: tier
    tiers: [10, 50, 100]
    sql: ${amount} ;;
  }

  # Add measures
  measure: count {
    type: count
  }
}

# Refinement (modify existing explore)
explore: +orders {
  # Add new join
  join: order_items {
    sql_on: ${orders.id} = ${order_items.order_id} ;;
    relationship: one_to_many
  }

  # Modify existing fields
  fields: [
    orders.id,
    orders.created_date,
    orders.total_amount,
    users.name
  ]
}
```

### Parameters
```lookml
view: dynamic_analysis {
  parameter: metric_selector {
    type: unquoted
    allowed_value: {
      label: "Revenue"
      value: "revenue"
    }
    allowed_value: {
      label: "Profit"
      value: "profit"
    }
    allowed_value: {
      label: "Order Count"
      value: "orders"
    }
  }

  measure: dynamic_metric {
    type: number
    sql:
      {% if metric_selector._parameter_value == 'revenue' %}
        SUM(${TABLE}.revenue)
      {% elsif metric_selector._parameter_value == 'profit' %}
        SUM(${TABLE}.profit)
      {% else %}
        COUNT(*)
      {% endif %} ;;
  }

  parameter: date_granularity {
    type: unquoted
    allowed_value: { value: "day" }
    allowed_value: { value: "week" }
    allowed_value: { value: "month" }
    default_value: "day"
  }

  dimension: dynamic_date {
    sql:
      {% if date_granularity._parameter_value == 'day' %}
        ${created_date}
      {% elsif date_granularity._parameter_value == 'week' %}
        ${created_week}
      {% else %}
        ${created_month}
      {% endif %} ;;
  }
}
```

### Liquid Variables
```lookml
view: liquid_examples {

  # Conditional logic
  dimension: filtered_revenue {
    type: number
    sql:
      {% if _user_attributes['department'] == 'Finance' %}
        ${TABLE}.revenue
      {% else %}
        NULL
      {% endif %} ;;
  }

  # Date range logic
  measure: revenue_in_period {
    type: sum
    sql: ${revenue} ;;
    filters: [
      created_date: "{% parameter date_range %}"
    ]
  }

  # Dynamic group by
  dimension: dynamic_grouping {
    type: string
    sql:
      {% if _view._name == 'orders' %}
        ${TABLE}.order_category
      {% else %}
        ${TABLE}.product_category
      {% endif %} ;;
  }

  # User attribute filtering
  sql_always_where:
    {% if _user_attributes['region'] != 'All' %}
      ${region} = '{{ _user_attributes["region"] }}'
    {% endif %} ;;
}
```

### Templated Filters
```lookml
view: advanced_filters {

  filter: date_filter {
    type: date
    default_value: "30 days"
  }

  dimension: in_date_range {
    type: yesno
    sql: {% condition date_filter %} ${created_raw} {% endcondition %} ;;
  }

  measure: filtered_count {
    type: count
    filters: [in_date_range: "yes"]
  }

  # Multi-value filter
  filter: status_filter {
    type: string
    suggest_dimension: status
  }

  measure: count_filtered_status {
    type: count
    sql: ${TABLE}.id ;;
    filters: [
      status: "{% parameter status_filter %}"
    ]
  }
}
```

## Access Control and Security

### Access Grants
```lookml
# In model file
access_grant: finance_only {
  user_attribute: department
  allowed_values: ["Finance", "Executive"]
}

explore: orders {
  required_access_grants: [finance_only]

  join: revenue_details {
    required_access_grants: [finance_only]
    # ...
  }
}
```

### Row-Level Security
```lookml
# In model file
explore: orders {
  access_filter: {
    field: region
    user_attribute: allowed_regions
  }

  sql_always_where: ${user_id} IN (
    SELECT user_id
    FROM user_permissions
    WHERE permission_user = '{{ _user_attributes["email"] }}'
  ) ;;
}

# In view
view: orders {
  sql_table_name:
    (SELECT *
     FROM orders
     WHERE {% condition region_filter %} region {% endcondition %}
    ) ;;

  filter: region_filter {
    type: string
    default_value: "{{ _user_attributes['region'] }}"
  }
}
```

## Performance Optimization

### Aggregate Awareness
```lookml
view: orders {
  sql_table_name: public.orders ;;

  # Use aggregate table when appropriate
  aggregate_table: daily_rollup {
    query: {
      dimensions: [created_date, category]
      measures: [total_amount, count]
    }

    materialization: {
      sql_trigger_value: SELECT CURRENT_DATE ;;
    }
  }

  dimension: created_date {
    type: date
    sql: ${TABLE}.created_date ;;
  }

  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
  }

  measure: total_amount {
    type: sum
    sql: ${amount} ;;
  }
}
```

### Persistent Derived Table Strategy
```lookml
# Incremental PDT
view: orders_incremental {
  derived_table: {
    sql:
      SELECT *
      FROM orders
      WHERE
        {% if orders_incremental._in_query %}
          created_at >= (
            SELECT MAX(created_at)
            FROM ${SQL_TABLE_NAME}
          )
        {% else %}
          created_at >= DATEADD(day, -30, CURRENT_DATE)
        {% endif %} ;;

    sql_trigger_value: SELECT DATE_TRUNC('hour', CURRENT_TIMESTAMP) ;;

    increment_key: "created_at"
    increment_offset: 3
  }
}
```

### Caching Strategy
```lookml
# In model file
datagroup: hourly_refresh {
  sql_trigger: SELECT DATE_TRUNC('hour', CURRENT_TIMESTAMP) ;;
  max_cache_age: "1 hour"
}

datagroup: nightly_refresh {
  sql_trigger: SELECT DATE_TRUNC('day', CURRENT_TIMESTAMP) ;;
  max_cache_age: "24 hours"
}

persist_with: hourly_refresh

explore: orders {
  persist_with: nightly_refresh  # Override default
}
```

## Dashboard LookML

### Basic Dashboard
```lookml
- dashboard: sales_overview
  title: Sales Overview
  layout: newspaper

  elements:
  - title: Total Revenue
    name: total_revenue
    model: ecommerce
    explore: orders
    type: single_value
    fields: [orders.total_amount]
    limit: 500

  - title: Revenue by Category
    name: revenue_by_category
    model: ecommerce
    explore: orders
    type: looker_column
    fields: [products.category, orders.total_amount]
    sorts: [orders.total_amount desc]
    limit: 10

  - title: Orders Over Time
    name: orders_over_time
    model: ecommerce
    explore: orders
    type: looker_line
    fields: [orders.created_date, orders.count]
    fill_fields: [orders.created_date]
    filters:
      orders.created_date: 30 days
```

## Common Patterns Reference

### Cohort Analysis
```lookml
view: user_cohorts {
  derived_table: {
    sql:
      SELECT
        user_id,
        DATE_TRUNC('month', MIN(created_at)) AS cohort_month
      FROM orders
      GROUP BY 1 ;;
  }

  dimension: cohort_month {
    type: date_month
    sql: ${TABLE}.cohort_month ;;
  }
}

view: cohort_analysis {
  dimension: months_since_cohort {
    type: number
    sql: DATEDIFF(month, ${user_cohorts.cohort_month}, ${orders.created_month}) ;;
  }

  measure: retention_rate {
    type: number
    sql:
      1.0 * COUNT(DISTINCT ${orders.user_id}) /
      NULLIF(COUNT(DISTINCT CASE WHEN ${months_since_cohort} = 0
                                   THEN ${orders.user_id} END), 0) ;;
    value_format_name: percent_2
  }
}
```

### Window Functions
```lookml
view: ranked_products {
  derived_table: {
    sql:
      SELECT
        product_id,
        revenue,
        ROW_NUMBER() OVER (
          PARTITION BY category
          ORDER BY revenue DESC
        ) AS rank_in_category
      FROM product_revenue ;;
  }

  dimension: rank_in_category {
    type: number
    sql: ${TABLE}.rank_in_category ;;
  }
}
```

## Resources
- LookML Reference: https://cloud.google.com/looker/docs/reference/lookml-quick-reference
- LookML Best Practices: https://cloud.google.com/looker/docs/best-practices/lookml-project-structure
- Liquid Reference: https://cloud.google.com/looker/docs/liquid-variable-reference
