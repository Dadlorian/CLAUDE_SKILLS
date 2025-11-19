# Valuation Methodologies Reference

## 1. Sales Comparison Approach
**Process**:
1. Find 3-6 comparable sales
2. Adjust for differences
3. Weight by similarity/recency
4. Calculate value

**Adjustments**:
- Size: ±$50-100/sqft
- Bedrooms: ±$10K-15K each
- Bathrooms: ±$5K-10K each
- Condition: ±5-10% of value
- Location: ±10-20% of value

## 2. Cost Approach
```
Value = Land Value + (Replacement Cost - Depreciation)

Replacement Cost = Sqft × Cost/Sqft
Depreciation = Physical + Functional + Economic
```

## 3. Income Approach
```
Value = NOI / Cap Rate

NOI = Gross Rent - Operating Expenses
Cap Rate = Market-derived rate for property type
```

## 4. Automated Valuation Model
- Hedonic regression
- Machine learning (XGBoost, RF)
- Neural networks
- Ensemble methods

## Accuracy Metrics
- MAE: Mean absolute error ($)
- MAPE: Mean absolute percentage error (%)
- Within 5%: Percentage within 5% of actual
- Within 10%: Percentage within 10% of actual

## See Also
- comp_selection.md
- ml_models_reference.md
