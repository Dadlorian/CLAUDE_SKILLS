# LookML Persistent Derived Table: User Facts

view: user_order_facts {
  derived_table: {
    sql:
      SELECT
        user_id,
        MIN(created_at) AS first_order_date,
        MAX(created_at) AS latest_order_date,
        COUNT(*) AS lifetime_orders,
        SUM(amount) AS lifetime_revenue,
        AVG(amount) AS average_order_value
      FROM orders
      GROUP BY user_id ;;
    
    # Make persistent
    sql_trigger_value: SELECT DATE(CURRENT_TIMESTAMP) ;;
    
    # Index for performance
    indexes: ["user_id"]
    
    # Distribution key (for certain databases)
    distribution: "user_id"
  }

  dimension: user_id {
    primary_key: yes
    type: number
    hidden: yes
    sql: ${TABLE}.user_id ;;
  }

  dimension_group: first_order {
    type: time
    timeframes: [date, week, month, year]
    sql: ${TABLE}.first_order_date ;;
  }

  dimension_group: latest_order {
    type: time
    timeframes: [date, week, month]
    sql: ${TABLE}.latest_order_date ;;
  }

  dimension: lifetime_orders {
    type: number
    sql: ${TABLE}.lifetime_orders ;;
  }

  dimension: lifetime_revenue {
    type: number
    sql: ${TABLE}.lifetime_revenue ;;
    value_format_name: usd
  }

  dimension: customer_segment {
    type: string
    sql:
      CASE
        WHEN ${lifetime_revenue} >= 10000 THEN 'VIP'
        WHEN ${lifetime_revenue} >= 1000 THEN 'High Value'
        WHEN ${lifetime_revenue} >= 100 THEN 'Regular'
        ELSE 'New'
      END ;;
  }

  measure: average_lifetime_revenue {
    type: average
    sql: ${lifetime_revenue} ;;
    value_format_name: usd_0
  }
}
