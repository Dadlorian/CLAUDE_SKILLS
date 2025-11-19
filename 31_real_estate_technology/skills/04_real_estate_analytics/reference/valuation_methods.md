# Valuation Methods Reference

## Sales Comparison Approach
1. Find comparable sales
2. Adjust for differences
3. Weight by similarity
4. Calculate value estimate

## Cost Approach
```
Value = Land Value + (Replacement Cost - Depreciation)
```

## Income Approach
```
Value = Net Operating Income / Cap Rate
```

## Automated Valuation Model (AVM)
- Hedonic regression
- Repeat sales
- Machine learning (XGBoost, RF)
- Ensemble methods

## Adjustment Grid Example
| Feature | Subject | Comp 1 | Comp 2 | Comp 3 |
|---------|---------|--------|--------|--------|
| Sale Price | ? | $450K | $475K | $440K |
| Bedrooms | 3 | 3 (0) | 4 (-$15K) | 3 (0) |
| Sqft | 2000 | 1900 (+$10K) | 2100 (-$10K) | 2000 (0) |
| Adjusted | ? | $460K | $450K | $440K |

**Estimated Value**: $450K (weighted median)

## See Also
- market_metrics_reference.md
- ml_models_reference.md
