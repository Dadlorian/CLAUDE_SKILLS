# LookML Development Guide

## Project Structure Best Practices

```
looker-project/
├── models/
│   ├── prod.model.lkml          # Production model
│   └── dev.model.lkml           # Development model
├── views/
│   ├── base/                    # Base views
│   │   ├── orders.view.lkml
│   │   └── customers.view.lkml
│   ├── derived/                 # Derived tables
│   │   └── user_facts.view.lkml
│   └── refinements/             # View extensions
│       └── orders_extended.view.lkml
├── dashboards/
│   └── sales_overview.dashboard.lookml
├── manifest.lkml
└── README.md
```

## Development Workflow

1. **Create Branch**: `git checkout -b feature/new-metric`
2. **Dev Mode**: Enable in Looker UI
3. **Make Changes**: Edit LookML files
4. **Validate**: LookML validator
5. **Test**: Run queries, check results
6. **Commit**: `git commit -m "Add revenue metric"`
7. **Pull Request**: Code review
8. **Merge**: To production branch
9. **Deploy**: Deploy to production in Looker

## Common Patterns

### Reusable Dimensions
```lookml
view: base_dates {
  extension: required

  dimension_group: created {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
  }
}

# Use in other views
view: orders {
  extends: [base_dates]
}
```

### Dynamic Measures
```lookml
parameter: metric_selector {
  type: unquoted
  allowed_value: { value: "revenue" }
  allowed_value: { value: "profit" }
}

measure: dynamic_value {
  type: number
  sql:
    {% if metric_selector._parameter_value == 'revenue' %}
      ${revenue}
    {% else %}
      ${profit}
    {% endif %} ;;
}
```

## Testing Strategy

### Data Tests
```lookml
# In view file
view: orders {
  dimension: order_id {
    primary_key: yes
    tests: [unique, not_null]
  }
  
  measure: total_revenue {
    type: sum
    sql: ${amount} ;;
    tests: [
      {assert: total_revenue >= 0}
    ]
  }
}
```

## Performance Optimization

- Use PDTs for complex transformations
- Index PDT columns used in joins
- Leverage aggregate_table for large datasets
- Set appropriate datagroups
- Monitor query performance

## Resources
- LookML Reference: https://cloud.google.com/looker/docs/reference
- Best Practices: https://cloud.google.com/looker/docs/best-practices
