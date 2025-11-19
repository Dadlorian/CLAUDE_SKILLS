# LookML Model Example: E-Commerce Analytics

connection: "production_db"

include: "/views/**/*.view.lkml"
include: "/dashboards/*.dashboard.lookml"

datagroup: daily_refresh {
  sql_trigger: SELECT MAX(updated_at) FROM orders ;;
  max_cache_age: "24 hours"
}

persist_with: daily_refresh

explore: orders {
  label: "Sales Orders"
  description: "Order transactions and customer analysis"

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

  join: user_order_facts {
    type: left_outer
    sql_on: ${orders.user_id} = ${user_order_facts.user_id} ;;
    relationship: many_to_one
  }

  # Row-level security
  access_filter: {
    field: users.region
    user_attribute: allowed_regions
  }
}

explore: inventory {
  label: "Inventory Management"
  
  join: products {
    sql_on: ${inventory.product_id} = ${products.id} ;;
    relationship: many_to_one
  }
}
