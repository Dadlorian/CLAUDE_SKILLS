# Model Validation Guide

## Validation Process

### 1. Conceptual Soundness
```
Questions:
- Is the economic theory correct?
- Are the assumptions reasonable?
- Have we identified all key drivers?
- Do coefficients have intuitive signs?

Example: PD Model
- Higher leverage → Higher PD? YES (correct)
- Lower profitability → Higher PD? YES (correct)
- Older firm → Lower PD? YES (makes sense)
- Larger firm → Lower PD? MAYBE (needs investigation)

If any relationship counterintuitive:
→ Investigate data for errors
→ Reconsider variable definition
→ Check for multicollinearity
```

### 2. Data Quality Testing
```
Completeness:
- % missing values: Should be < 5%
- % defaults in sample: Should be 1-5%

Accuracy:
- Range checks: Values in reasonable ranges
- Outliers: Flag and investigate
- Duplicates: Remove

Consistency:
- Year-over-year: Variables consistent
- Cross-variable: No contradictions
- Historical: Long enough sample (5+ years)

Result: Approve for modeling if:
✓ >95% completeness
✓ Defaults 1-5% of sample
✓ <2% outliers
```

### 3. Statistical Testing
```
Goodness of Fit:
- R² or Pseudo R² > 0.20 (good model)
- AIC/BIC scores (lower is better)
- Log likelihood (higher magnitude is better)

Coefficient Significance:
- t-stat > 1.96 (95% significant)
- p-value < 0.05 (significant)
- Remove non-significant variables

Multicollinearity:
- VIF < 5 for each variable
- Correlation < 0.7 between variables
- Condition index < 30

Normality of Residuals:
- Plot residuals
- Shapiro-Wilk test
- Q-Q plot comparison
```

### 4. Backtesting
```
Method 1: In-sample vs. Out-of-sample
- Calculate performance metrics on both
- Should be similar (not overfitted)
- If out-of-sample much worse: Model overfit

Example:
                Development   Validation
Sensitivity    85%           82%         ✓ Similar
Specificity    97%           96%         ✓ Similar
AUC            0.820         0.810       ✓ Similar

Conclusion: Model generalizes well

Method 2: Population Stability Index
- Score current population
- Compare to development population
- PSI > 10%: Model not valid for current portfolio

Method 3: Default Rate by Decile
- For each score bucket, calculate actual default rate
- Should match predicted PD
- Smooth, monotonic increase across deciles
```

### 5. Sensitivity & Stress Testing
```
Vary key assumptions:
- Sample period: 2005-2015 vs. 2010-2015
- Model form: Logistic vs. probit vs. neural net
- Variables: With/without each major variable
- Thresholds: 0.5 vs. 0.4 vs. 0.6 cutoff

Results:
- If minor changes cause large variance: Unstable
- If robust to changes: Reliable
- Compare to alternatives

Example:
PD model score distribution:
- Current model: Mean 5%, Std Dev 3%
- Without leverage variable: Mean 5.2%, Std Dev 2.8%
- Removal of 1 variable: Only 5% change ✓ Robust

Market risk VaR:
- Parametric VaR: $2.0M
- Historical simulation: $2.1M
- Monte Carlo: $1.95M
- Range narrow: $1.95M-$2.1M ✓ Robust
```

### 6. Independent Validation
```
By: Independent risk validation team (not model developers)

Checklist:
□ Methodology documented and reviewed
□ Sample size adequate (>50 defaults for PD)
□ Development vs. holdout properly split
□ Backtesting comprehensive
□ Performance metrics acceptable
□ Sensitivity analysis complete
□ Business logic sound
□ Governance framework in place

Report: Approve, Conditional, Reject

Approve: Model ready for use
Conditional: Approve if changes made (list required changes)
Reject: Model not acceptable (explain concerns)
```

## Validation Frequency

| Model Type | Frequency | Minimum | Required Actions |
|----------|-----------|---------|------------------|
| PD Model | Annual | Semi-annual | Backtest, recalibrate |
| VaR Model | Monthly | Monthly | Backtest, exception analysis |
| Pricing Model | Quarterly | Quarterly | Compare to market |
| LGD Model | Annual | Semi-annual | Test with new defaults |
| Capital Model | Annual | Annual | Regulatory submission |

## Common Validation Issues

| Issue | Solution |
|-------|----------|
| High p-values (not significant) | Remove variable, use LASSO/regularization |
| Overfitting (high R² in-sample, low out-of-sample) | Simplify model, regularize |
| Unstable coefficients | Check multicollinearity, larger sample |
| Poor discrimination (AUC <0.70) | Add new variables, try different model |
| Calibration issues | Recalibrate, adjust intercept |
| Data quality problems | Clean data, handle missing values |
