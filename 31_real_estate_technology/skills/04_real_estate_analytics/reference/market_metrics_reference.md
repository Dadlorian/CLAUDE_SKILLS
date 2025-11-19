# Market Metrics Reference

## Price Metrics
- **Median Sale Price**: Middle value of all sales
- **Mean Sale Price**: Average (affected by outliers)
- **Price per Square Foot**: $/sqft benchmark
- **List-to-Sale Ratio**: Sale price / list price
- **Price Growth**: YoY percentage change

## Inventory Metrics
- **Active Listings**: Currently for sale
- **New Listings**: Added this month
- **Pending Sales**: Under contract
- **Sold**: Closed transactions
- **Withdrawn/Expired**: Off market

## Velocity Metrics
- **Days on Market (DOM)**: Days until sale/pending
- **Months of Inventory**: Active / (Sold/12)
- **Absorption Rate**: Sales/month / active
- **List-to-Pending**: Days until offer accepted

## Market Temperature
- **Hot**: < 3 months inventory, DOM < 30
- **Balanced**: 4-6 months inventory
- **Cold**: > 6 months inventory, DOM > 60

## Calculations
```python
median_price = np.median(sales['price'])
price_per_sqft = sales['price'].sum() / sales['sqft'].sum()
months_inventory = active_count / (sales_per_month)
yoy_growth = (current_price - prior_year_price) / prior_year_price
```

## See Also
- valuation_methods.md
- forecasting_models.md
