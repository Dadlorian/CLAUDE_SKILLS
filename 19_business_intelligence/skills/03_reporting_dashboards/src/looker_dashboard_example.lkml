# Looker Dashboard - Executive Summary
# Based on Few-Tufte principles

- dashboard: executive_summary
  title: Executive Summary - Q4 2024
  layout: newspaper
  preferred_viewer: dashboards-next
  description: "High-level business metrics for C-suite"
  
  # Filters
  filters:
  - name: date_range
    title: "Date Range"
    type: date_filter
    default_value: "last 30 days"
    
  - name: region
    title: "Region"
    type: field_filter
    explore: sales
    field: sales.region
    default_value: "All"

  # Primary KPI - Hero Element
  elements:
  - name: arr_kpi
    title: "Annual Recurring Revenue"
    model: business_model
    explore: subscriptions
    type: single_value
    fields: [subscriptions.arr, subscriptions.arr_target, subscriptions.arr_yoy_growth]
    filters:
      subscriptions.status: "active"
    limit: 1
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: true
    comparison_type: progress_percentage
    comparison_reverse_colors: false
    show_comparison_label: true
    series_types: {}
    hidden_fields: []
    listen:
      date_range: subscriptions.date_range
      region: subscriptions.region
    row: 0
    col: 0
    width: 24
    height: 4

  # Supporting KPIs - Row of 3
  - name: new_customers
    title: "New Customers"
    model: business_model
    explore: customers
    type: single_value
    fields: [customers.new_customer_count, customers.target]
    filters:
      customers.acquisition_date: "this month"
    limit: 1
    show_comparison: true
    listen:
      region: customers.region
    row: 4
    col: 0
    width: 8
    height: 3

  - name: gross_margin
    title: "Gross Margin"
    model: business_model
    explore: financials
    type: single_value
    fields: [financials.gross_margin_pct, financials.target_margin]
    limit: 1
    show_comparison: true
    row: 4
    col: 8
    width: 8
    height: 3

  - name: nps
    title: "Net Promoter Score"
    model: business_model
    explore: surveys
    type: single_value
    fields: [surveys.nps, surveys.nps_target]
    filters:
      surveys.survey_date: "this quarter"
    limit: 1
    show_comparison: true
    row: 4
    col: 16
    width: 8
    height: 3

  # Main Trend Chart
  - name: revenue_trend
    title: "Revenue Trend - Last 12 Months"
    model: business_model
    explore: sales
    type: looker_line
    fields: [sales.month, sales.total_revenue, sales.revenue_target]
    fill_fields: [sales.month]
    filters:
      sales.month: "12 months"
    sorts: [sales.month asc]
    limit: 500
    x_axis_gridlines: false
    y_axis_gridlines: false
    show_view_names: false
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: false
    show_x_axis_ticks: true
    y_axis_scale_mode: linear
    x_axis_reversed: false
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    limit_displayed_rows: false
    legend_position: center
    point_style: none
    show_value_labels: false
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    show_null_points: true
    interpolation: linear
    color_application:
      collection_id: few-recommended
      palette_id: few-recommended-categorical-0
    series_colors:
      sales.total_revenue: "#2171B5"
      sales.revenue_target: "#CCCCCC"
    series_types: {}
    listen:
      region: sales.region
    row: 7
    col: 0
    width: 24
    height: 6

  # Breakdown Charts - Row of 2
  - name: revenue_by_segment
    title: "Revenue by Customer Segment"
    model: business_model
    explore: sales
    type: looker_bar
    fields: [sales.customer_segment, sales.total_revenue, sales.growth_pct]
    sorts: [sales.total_revenue desc]
    limit: 10
    x_axis_gridlines: false
    y_axis_gridlines: false
    show_view_names: false
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    show_x_axis_label: false
    show_x_axis_ticks: true
    x_axis_scale: auto
    y_axis_scale_mode: linear
    x_axis_reversed: false
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    limit_displayed_rows: false
    legend_position: center
    series_types: {}
    point_style: none
    color_application:
      collection_id: few-recommended
      palette_id: few-recommended-categorical-0
    series_colors:
      sales.total_revenue: "#4D4D4D"
    show_value_labels: true
    label_density: 25
    listen:
      date_range: sales.date
      region: sales.region
    row: 13
    col: 0
    width: 12
    height: 6

  - name: pipeline_status
    title: "Sales Pipeline Status"
    model: business_model
    explore: opportunities
    type: looker_column
    fields: [opportunities.stage, opportunities.count, opportunities.total_value]
    filters:
      opportunities.status: "Open"
    sorts: [opportunities.stage]
    limit: 500
    x_axis_gridlines: false
    y_axis_gridlines: false
    show_view_names: false
    series_types: {}
    color_application:
      collection_id: few-recommended
      palette_id: few-recommended-categorical-0
    listen:
      region: opportunities.region
    row: 13
    col: 12
    width: 12
    height: 6
