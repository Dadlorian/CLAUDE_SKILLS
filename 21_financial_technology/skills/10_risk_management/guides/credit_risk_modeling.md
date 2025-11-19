# Credit Risk Modeling Guide

## Step-by-Step Implementation

### Phase 1: Problem Definition & Data Preparation

**Step 1: Define the Modeling Objective**
```
Example: Build PD model for corporate loans

Scope:
- Exposure type: Corporate loans
- Portfolio: $5B in loans
- Model use: Capital calculation, pricing, limits
- Time horizon: 1-year default probability
- Target audience: Credit committee, regulators
- Required accuracy: 90%+ correct classification

Documentation:
- Create model charter
- Identify key stakeholders
- Define success metrics
```

**Step 2: Gather Historical Default Data**
```
Data requirements:
- Loan originations (last 5-10 years)
- Default events (with default date)
- Maturity and prepayment dates
- Covariates (financial metrics, industry, rating)

Example data structure:
Loan_ID  Orig_Date  Maturity  Default_Flag  Default_Date  Industry  PD_Grade
001      2012-01-15 2017-01-15 0           NULL          Tech      A
002      2012-02-20 2022-02-20 1           2015-08-10    Energy    BB
003      2012-03-10 2017-03-10 0           NULL          Finance   A
...

Sample size: 10,000+ loans minimum (50+ defaults needed for modeling)
```

**Step 3: Data Quality & Preprocessing**
```
Check for:
- Missing values (handle by imputation or removal)
- Duplicates (remove)
- Outliers (flag or cap)
- Incorrect classifications

Example cleaning:
- Loans with NULL industry: Remove (5% of sample)
- Loans with leverage > 10x: Flag as outlier (investigate)
- Loans with negative cash flow: Investigate, likely data error
- Missing financial metrics: Impute with median by industry

Result: Clean dataset ready for analysis
```

### Phase 2: Exploratory Data Analysis

**Step 4: Understand Default Distribution**
```
Calculate default rates:
Total loans: 10,000
Defaults: 150
Overall default rate: 1.5%

By industry:
- Technology: 50/2000 = 2.5%
- Finance: 30/2000 = 1.5%
- Energy: 40/1500 = 2.7%
- Retail: 20/2000 = 1.0%
- Manufacturing: 10/1500 = 0.7%

Key insight: Technology and Energy have higher default rates
Model must capture industry effect

By rating:
- A: 10/4000 = 0.25% (low risk)
- BBB: 40/4000 = 1.0%
- BB: 60/1500 = 4.0%
- B: 40/500 = 8.0% (high risk)

Key insight: Clear relationship between rating and default
Rating will be important model variable
```

**Step 5: Correlation Analysis**
```
Calculate correlation with default:

Variable              Correlation with Default
Leverage (Debt/EBITDA)    +0.45 (positive, higher leverage = higher default)
Interest Coverage         -0.50 (negative, lower coverage = higher default)
Return on Assets          -0.55 (lower ROA = higher default)
Debt/Equity               +0.40 (higher D/E = higher default)
Industry BBB Rating       -0.60 (rating strong predictor)
Firm Age                  -0.30 (older firms safer)
Loan Size                 -0.10 (weak effect)

Remove highly correlated variables:
- Leverage and Debt/Equity highly correlated (use one)
- Interest Coverage and ROA correlated (use one)
- Keep variables with good discrimination and low correlation
```

### Phase 3: Model Development

**Step 6: Variable Transformation & Selection**
```
Transform continuous variables:
- Financial ratios often non-linear
- Create bins/categories for interpretation
- Example: Leverage (Debt/EBITDA)
  * Low: < 1.5x (lowest default risk)
  * Medium: 1.5x - 3.0x (medium default risk)
  * High: 3.0x - 5.0x (higher default risk)
  * Very High: > 5.0x (highest default risk)

Final variable set:
- Leverage (binned)
- Interest Coverage (binned)
- Return on Assets (binned)
- Industry
- Rating (A, BBB, BB, B)
- Firm Age (years)
- Loan Amount (log scale)

Information Value testing:
Calculate IV for each variable
- IV > 0.3: Excellent predictor
- IV 0.1-0.3: Good predictor
- IV < 0.1: Poor predictor
```

**Step 7: Logistic Regression Estimation**
```
Development sample split:
- 70% for training: 7,000 loans
- 30% for validation: 3,000 loans

Estimate logistic regression:
PD = e^z / (1 + e^z)
z = β0 + β1×Leverage + β2×Interest_Coverage + ... + β6×Age

Results:
Variable            Coefficient   Std Error   t-stat    p-value
Intercept           -3.50         0.25        -14.0     0.000***
Leverage High       0.80          0.15        5.3       0.000***
Leverage Very High  1.80          0.20        9.0       0.000***
Interest Coverage   -0.12         0.02        -6.0      0.000***
ROA                 -0.15         0.03        -5.0      0.000***
Industry Energy     0.50          0.18        2.8       0.005**
Industry Tech       0.45          0.17        2.6       0.009**
Rating BB           0.70          0.15        4.7       0.000***
Rating B            1.50          0.22        6.8       0.000***
Age                 -0.02         0.01        -2.0      0.045*

Model diagnostics:
- AIC: 5,200 (good model fit)
- Log likelihood: -2,400
- Concordance: 0.78 (78% correct ranking)
```

**Step 8: Model Performance on Training Data**
```
Classify loans by predicted PD:
- PD < 1%: Class 1 (safe)
- PD 1-3%: Class 2 (acceptable)
- PD 3-8%: Class 3 (risky)
- PD > 8%: Class 4 (very risky)

Classification table:
             Actual Non-Default  Actual Default  Total
Predicted 1  2,800               5              2,805
Predicted 2  2,600               40             2,640
Predicted 3  1,400               75             1,475
Predicted 4  800                80             880

Correctly classified: (2800+40+75+80) / 7000 = 93%

Sensitivity: 280 / 200 = 84% (correctly identify defaults)
Specificity: 7280 / 6800 = 98% (correctly identify non-defaults)

Model is performing well
```

### Phase 4: Validation Testing

**Step 9: Out-of-Sample Validation**
```
Test on 30% holdout sample (3,000 loans):

Same metrics on holdout:
- Correctly classified: 91% (vs. 93% in-sample)
- Sensitivity: 80% (vs. 84% in-sample)
- Specificity: 97% (vs. 98% in-sample)

Conclusion: Model performs well on new data
Not overfitted (performance similar in-sample and out-of-sample)

Calculate AUC (Area Under Curve):
- Training AUC: 0.82
- Validation AUC: 0.80
- Good discrimination, similar on both samples
```

**Step 10: Calibration Check**
```
Sort validation sample by PD decile:
Calculate actual default rate by decile

Decile  PD Range    Model PD  Count  Actual Defaults  Actual Rate  Diff
1       < 0.1%      0.08%     300    0               0.0%         -0.08%
2       0.1%-0.3%   0.20%     300    0               0.0%         -0.20%
3       0.3%-0.6%   0.45%     300    2               0.7%         +0.25%
4       0.6%-1.0%   0.85%     300    4               1.3%         +0.45%
5       1.0%-1.5%   1.25%     300    5               1.7%         +0.45%
6       1.5%-2.5%   2.00%     300    8               2.7%         +0.70%
7       2.5%-4.0%   3.20%     300    12              4.0%         +0.80%
8       4.0%-6.0%   5.00%     300    18              6.0%         +1.00%
9       6.0%-10.0%  8.00%     300    20              6.7%         -1.30%
10      > 10.0%     15.00%    300    26              8.7%         -6.30%

Observation: Model overpredicts in top decile
May need adjustment for very high risk loans

Probability plot: Plot actual vs. predicted
Straight 45-degree line = perfect calibration
Our model slightly above line (overestimate slightly)
But generally good calibration
```

### Phase 5: Implementation

**Step 11: Score Mapping to PD Ratings**
```
Transform model coefficients to scorecard:

Raw score: e^z / (1+e^z) ranges from 0 to 1
Scale to 0-1000 scale:
Scaled Score = (Raw Score / 0.001) capped at 1000

Map scores to ratings:
Score       Rating    PD    Action
800-1000    AAA/AA    <0.5% Auto-approve
700-799     A         0.5%-1% Approve
650-699     BBB       1%-2%   Approve
600-649     BB        2%-5%   Review
550-599     B         5%-10%  Likely decline
<550        CCC+      >10%    Decline

Example loan:
Leverage: High (0.80)
Interest Coverage: Medium (coefficient = -0.12 × medium value)
ROA: Low
Industry: Energy
Rating: BB

z = -3.50 + 0.80 + (-0.12×3) + (-0.15×2) + 0.50 + 0.70 = -1.2
PD = e^(-1.2) / (1 + e^(-1.2)) = 0.231 / 1.231 = 18.8%
Scaled Score = (0.188 / 0.001) = 188 → capped at 1000, shows very high risk
Rating: CCC+ (Decline)
```

**Step 12: Implementation Testing**
```
System validation:
- Score 100 test loans manually
- Compare with system output
- Verify 100% match
- Test edge cases (missing data, boundary values)

Performance testing:
- Scoring speed: Should process 10,000 loans in < 1 minute
- System uptime: > 99.9%
- Error handling: Should handle data errors gracefully

Documentation:
- Scorecard card with coefficients
- Variable definitions
- Decile distribution chart
- User guide for credit officers
```

## Ongoing Management

### Monthly Monitoring
```
Track model performance:
- Default rate in each score bucket
- Compare actual vs. predicted
- Flag if actual > predicted (overperforming) or predicted > actual (underperforming)
- Calculate Population Stability Index (PSI)

Example PSI calculation:
Score Decile  Baseline %  Current %   PSI Contribution
High (>800)   10%         12%         +0.024
Mid-High      15%         18%         +0.018
Mid            25%         22%         -0.019
Mid-Low        25%         23%         -0.014
Low (<600)    25%         25%         0.000

Total PSI = 0.009 = 0.9% → No action needed (< 5%)
```

### Annual Retraining
```
Incorporate new data:
- Last year's new defaults
- Latest financial data
- Market developments

Compare model performance:
- Model v3.0 (current): AUC = 0.80
- Model v3.1 (retrained): AUC = 0.81

Decision:
- If improvement significant: Update to new model
- If no improvement: Keep current model
- If degradation: Investigate cause

Revalidation:
- Run full validation on new holdout sample
- Check calibration
- Backtest on latest defaults
```

## Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Overfitting (high training, low validation AUC) | Simplify model, reduce variables, regularization |
| Sample selection bias (old data not representative) | Use recent data, stratified sampling |
| Low sensitivity (missing actual defaults) | Lower threshold, adjust cost weights |
| Calibration issues (predicted ≠ actual PD) | Adjust intercept, recalibrate by segment |
| Missing data problems | Use imputation, create "missing" indicator |
| Unstable coefficients | Check for multicollinearity, remove correlated variables |
