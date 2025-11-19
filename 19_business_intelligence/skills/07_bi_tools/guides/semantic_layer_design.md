# Semantic Layer Design Guide

## What is a Semantic Layer?

```
Raw Database Tables
       ↓
  Semantic Layer (Business Logic)
  ├─ Friendly names
  ├─ Calculated metrics
  ├─ Business rules
  └─ Access control
       ↓
  BI Tools / End Users
```

## Benefits

- **Single Source of Truth**: One definition per metric
- **Business-Friendly**: No SQL knowledge required
- **Consistency**: Same calculations everywhere
- **Governance**: Centralized access control
- **Agility**: Change once, update everywhere

## Implementation Patterns

### Pattern 1: dbt Semantic Layer
```yaml
# metrics.yml
metrics:
  - name: revenue
    label: Total Revenue
    type: simple
    type_params:
      measure: revenue_sum
    
  - name: average_order_value
    label: Average Order Value
    type: ratio
    type_params:
      numerator: revenue
      denominator: order_count
```

### Pattern 2: Looker LookML
```lookml
view: orders {
  dimension: order_id {
    primary_key: yes
    type: number
  }
  
  measure: total_revenue {
    type: sum
    sql: ${amount} ;;
    value_format_name: usd
    description: "Sum of all order amounts"
  }
  
  measure: average_order_value {
    type: average
    sql: ${amount} ;;
    value_format_name: usd_0
  }
}
```

### Pattern 3: Power BI Tabular Model
```dax
// Measures table
Total Revenue = SUM(Sales[Amount])

Average Order Value =
DIVIDE(
    [Total Revenue],
    DISTINCTCOUNT(Sales[OrderID])
)

// Time intelligence
Revenue YTD =
CALCULATE(
    [Total Revenue],
    DATESYTD('Date'[Date])
)
```

## Design Principles

### 1. Business Language
```
❌ Technical: sum_amt_usd
✓ Business: Total Revenue

❌ Technical: cust_cnt_dst
✓ Business: Unique Customers

❌ Technical: pct_chg_wow
✓ Business: Week-over-Week Growth %
```

### 2. Metric Hierarchy
```
Atomic Metrics (base):
├─ Order Count
├─ Revenue
└─ Cost

Derived Metrics:
├─ Average Order Value = Revenue / Order Count
├─ Profit = Revenue - Cost
└─ Profit Margin = Profit / Revenue

Composite Metrics:
├─ Customer Lifetime Value
├─ Net Promoter Score
└─ Cohort Retention Rate
```

### 3. Consistent Definitions
```yaml
# Metric catalog
revenue:
  definition: "Sum of all completed order amounts"
  calculation: "SUM(orders.amount WHERE status = 'completed')"
  owner: "Finance Team"
  approved: true
  last_updated: "2024-11-15"
  
active_customer:
  definition: "Customer with order in last 90 days"
  calculation: "COUNT(DISTINCT customer_id WHERE order_date >= TODAY() - 90)"
  owner: "Product Team"
  approved: true
```

## Best Practices

### Documentation
- Clear descriptions for each metric
- Business owner assigned
- Calculation formula
- Example values
- Known limitations

### Version Control
- Git repository for definitions
- Code review for changes
- Changelog for updates
- Deprecation warnings

### Testing
```sql
-- Metric validation tests
SELECT
    SUM(amount) as total_revenue,
    123456.78 as expected_revenue
FROM orders
WHERE order_date = '2024-11-01'
HAVING ABS(total_revenue - expected_revenue) > 0.01;
-- Should return 0 rows
```

### Performance
- Pre-aggregate when possible
- Index underlying tables
- Cache frequently used metrics
- Monitor query times

## Tools Comparison

| Tool | Type | Strength |
|------|------|----------|
| dbt | Code-first | Versioning, testing |
| Looker | Code-first | Exploration, caching |
| Power BI | Model-based | Microsoft integration |
| Tableau | Visual | User-friendly |
| AtScale | Universal | Multi-platform |

## Resources
- dbt Metrics: https://docs.getdbt.com/docs/build/metrics
- LookML: https://cloud.google.com/looker/docs/what-is-lookml
- Headless BI: https://www.getdbt.com/analytics-engineering/transformation/metrics-layer/
