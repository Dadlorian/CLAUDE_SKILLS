# Market Analysis Guide

## Monthly Market Report

### 1. Collect Data
```sql
SELECT 
    COUNT(*) as sales_count,
    MEDIAN(sale_price) as median_price,
    AVG(days_on_market) as avg_dom
FROM sales
WHERE sale_date >= '2025-01-01'
  AND sale_date < '2025-02-01'
  AND property_type = 'Single Family'
```

### 2. Calculate Metrics
```python
current_month = get_sales(month=1, year=2025)
prior_month = get_sales(month=12, year=2024)
prior_year = get_sales(month=1, year=2024)

metrics = {
    'median_price': np.median(current_month['price']),
    'mom_change': calculate_change(current_month, prior_month),
    'yoy_change': calculate_change(current_month, prior_year),
    'active_listings': get_active_count(),
    'months_inventory': calculate_months_inventory()
}
```

### 3. Generate Report
- Price trends (chart)
- Inventory levels
- Days on market
- Market temperature indicator
- Forecast

## See Also
- market_metrics_reference.md
- forecasting_models.md
