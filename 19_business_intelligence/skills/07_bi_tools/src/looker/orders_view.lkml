# LookML View: Orders

view: orders {
  sql_table_name: public.orders ;;

  # Primary Key
  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}.id ;;
  }

  # Foreign Keys
  dimension: user_id {
    type: number
    hidden: yes
    sql: ${TABLE}.user_id ;;
  }

  dimension: product_id {
    type: number
    hidden: yes
    sql: ${TABLE}.product_id ;;
  }

  # Dates
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

  # Dimensions
  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
  }

  dimension: amount {
    type: number
    sql: ${TABLE}.amount ;;
    value_format_name: usd
  }

  # Calculated Dimensions
  dimension: is_returned {
    type: yesno
    sql: ${TABLE}.status = 'returned' ;;
  }

  dimension: order_value_tier {
    type: tier
    tiers: [0, 50, 100, 500, 1000]
    style: integer
    sql: ${amount} ;;
  }

  # Measures
  measure: count {
    type: count
    drill_fields: [detail*]
  }

  measure: total_revenue {
    type: sum
    sql: ${amount} ;;
    value_format_name: usd
    drill_fields: [detail*]
  }

  measure: average_order_value {
    type: average
    sql: ${amount} ;;
    value_format_name: usd_0
  }

  measure: cumulative_revenue {
    type: running_total
    sql: ${total_revenue} ;;
    value_format_name: usd
  }

  # Drill Fields
  set: detail {
    fields: [
      id,
      created_date,
      users.name,
      products.name,
      amount,
      status
    ]
  }
}
