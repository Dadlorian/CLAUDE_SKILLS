# Credit Scoring Models

## Overview
Credit scoring models predict the probability of default for loan applicants or existing borrowers. They convert financial and behavioral data into a risk score, which drives pricing, limits, and portfolio management decisions.

## Scoring Model Methodologies

### 1. Logistic Regression
**Most Common Approach in Banking**

**Model Form**:
```
Probability of Default = e^z / (1 + e^z)

Where:
z = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ
X₁, X₂, ..., Xₙ = Predictor variables
β₀, β₁, ..., βₙ = Coefficients estimated from data
```

**Example: Personal Credit Score**:
```
Predictors:
- Annual Income (X₁): $60,000
- Years Employment (X₂): 5 years
- Credit Card Utilization (X₃): 45%
- Payment History (X₄): 8 (0-10 scale, 10=excellent)
- Debt-to-Income (X₅): 35%

Model coefficients (estimated from training data):
β₀ = -3.5 (intercept)
β₁ = 0.00002 (income coefficient)
β₂ = -0.15 (employment coefficient)
β₃ = 0.03 (utilization coefficient)
β₄ = -0.25 (payment history coefficient)
β₅ = 0.02 (debt-to-income coefficient)

Calculate:
z = -3.5 + (0.00002 × 60,000) + (-0.15 × 5) + (0.03 × 45) + (-0.25 × 8) + (0.02 × 35)
  = -3.5 + 1.2 - 0.75 + 1.35 - 2.0 + 0.7
  = -3.0

PD = e^(-3.0) / (1 + e^(-3.0)) = 0.0498 / 1.0498 = 4.74%

Interpretation: Applicant has ~4.74% probability of default
```

**Advantages**:
- Simple, interpretable
- Fast to implement
- Well-understood statistically
- Easy to monitor (coefficient stability)
- Standard in banks

**Disadvantages**:
- Assumes linear relationship on logit scale
- Requires sufficient samples of defaults
- Sensitive to sample bias
- Cannot capture complex interactions

### 2. Decision Trees / Random Forests

**Decision Tree Example**:
```
Root: Annual Income
├── < $30,000
│   └── Credit History
│       ├── Excellent (0-1 delinquencies): PD = 2%
│       ├── Good (2-3 delinquencies): PD = 5%
│       └── Poor (4+ delinquencies): PD = 15%
└── ≥ $30,000
    └── Employment Stability
        ├── Employed 5+ years
        │   └── PD = 1.5%
        └── Employed < 5 years
            └── Credit History
                ├── Excellent: PD = 3%
                └── Poor: PD = 8%
```

**Random Forest**:
- Train multiple decision trees on random subsets
- Combine predictions (average for regression/probability)
- Reduces overfitting from single tree

**Advantages**:
- Captures non-linear relationships
- Handles interactions automatically
- Robust to outliers
- Less sensitive to sample imbalances

**Disadvantages**:
- Less interpretable (black box)
- Slower to train and score
- Harder to monitor stability
- Requires more development data
- Model validation more complex

### 3. Support Vector Machines (SVM)

**Concept**: Find optimal hyperplane separating defaults from non-defaults in high-dimensional space.

**Advantages**:
- Excellent for binary classification
- Works well in high dimensions
- Good generalization to new data

**Disadvantages**:
- Black box (hard to interpret)
- Requires parameter tuning
- Slower to train
- Not commonly used in traditional banking

### 4. Neural Networks / Deep Learning

**Multi-layer Neural Network**:
```
Input Layer → Hidden Layers → Output Layer
Income, Employment, Credit History → [Neurons] → PD Probability
Debt-to-Income, Savings → [Neurons]
Payment History → [Neurons]
```

**Advantages**:
- Captures very complex patterns
- State-of-the-art performance on large datasets
- Can handle unstructured data (text, images)

**Disadvantages**:
- Requires massive datasets
- Extremely difficult to interpret
- Regulatory concerns (model risk, explainability)
- Computationally expensive
- Slow adoption in traditional banking

## Model Development Process

### 1. Data Preparation

**Data Sources**:
- Application data: Income, employment, assets
- Credit bureau data: Payment history, credit utilization
- Bank internal data: Account behavior, profitability
- Macroeconomic data: Unemployment, GDP, interest rates
- Alternative data: Rent payments, utility bills, social media

**Data Cleaning**:
- Handle missing values (imputation or removal)
- Remove outliers (e.g., unusually high income)
- Standardize/normalize variables
- Verify data quality

**Sample**:
- Development sample: 70% of data (for training)
- Validation sample: 30% of data (for testing)
- Both must have sufficient defaults (at least 50-100)

### 2. Variable Selection

**Statistical Tests**:
- **Information Value (IV)**: Measures predictive power
  ```
  IV = Σ (% of Defaults - % of Non-defaults) × ln(% of Defaults / % of Non-defaults)

  IV < 0.02: Weak predictor
  0.02 < IV < 0.1: Fair predictor
  0.1 < IV < 0.3: Good predictor
  IV > 0.3: Excellent predictor
  ```

- **Correlation Analysis**: Remove highly correlated variables
- **Univariate Regression**: Check each variable's significance

**Expert Judgment**:
- Business relevance (variable makes sense)
- Data availability (can be collected at application)
- Stability (won't change dramatically)
- Non-discrimination (legally acceptable)

### 3. Model Estimation

**Logistic Regression**:
```
Step 1: Estimate coefficients using maximum likelihood estimation (MLE)
Step 2: Calculate standard errors and t-statistics
Step 3: Test significance of each coefficient
Step 4: Remove non-significant variables
Step 5: Reestimate with significant variables only

Example Output:
Variable            Coefficient  Std Error  t-stat   p-value
Income              0.000020     0.000003   6.67     0.000***
Employment Years   -0.150000     0.025000  -6.00     0.000***
Credit Utilization  0.030000     0.015000   2.00     0.046*
Payment History    -0.250000     0.040000  -6.25     0.000***
Debt-to-Income      0.020000     0.015000   1.33     0.183

***p<0.001, **p<0.01, *p<0.05
Remove Debt-to-Income (p=0.183), reestimate
```

### 4. Model Performance Testing

**Development Sample Performance**:
```
Gini Coefficient: 0.65 (0=random, 1=perfect)
KS Statistic: 0.45 (0=random, 1=perfect)
AUC: 0.825 (0.5=random, 1.0=perfect)
```

**Validation Sample Performance**:
```
Gini Coefficient: 0.63 (Good - similar to development)
KS Statistic: 0.43 (Good - similar to development)
AUC: 0.815 (Good - similar to development)

Interpretation: Model performs well on new data,
not overfitted to development sample
```

**Calibration Test**:
```
Score Range    Model PD    Actual PD    Count
750-1000       1.2%        1.3%         2,000
700-749        2.5%        2.6%         3,000
650-699        5.0%        5.2%         4,000
600-649        8.0%        7.8%         3,000
550-599       12.0%       12.5%         2,000
< 550         18.0%       17.2%         1,000

Interpretation: Model is well-calibrated
(predicted PD close to actual PD in each bucket)
```

## Credit Score to Rating Assignment

### Score Mapping
```
Score Range    Rating    Typical PD    Action
800+          AAA       < 0.5%        Approved
750-799       AA        0.5%-1%       Approved
700-749       A         1%-2%         Approved
650-699       BBB       2%-5%         Approved
600-649       BB        5%-8%         Reviewed
550-599       B         8%-15%        Likely Decline
< 550         CCC       > 15%         Decline
```

### Score Calculation
```
Raw Score: Weighted sum of variables
z = β₀ + β₁X₁ + ... + βₙXₙ

PD: e^z / (1 + e^z)

Scaled Score (0-1000):
Score = 1000 × PD

Example:
If z = -3.0, PD = 4.74%
Scaled Score = 1000 × 0.0474 = 47.4 ≈ 500
```

## Model Monitoring & Validation

### Population Stability Index (PSI)
Measures distribution shift of scores over time.

```
PSI = Σ (% current - % baseline) × ln(% current / % baseline)

PSI < 5%: No action needed
5% < PSI < 10%: Monitor
PSI > 10%: Model retrain recommended

Example calculation:
Score Range    Baseline %    Current %    Contribution
800+           10%           8%           -0.024
700-799        25%           23%          -0.016
600-699        40%           42%          +0.010
500-599        20%           22%          +0.010
< 500          5%            5%           0.000

PSI = 0.024 + 0.016 + 0.010 + 0.010 = 0.060 = 6.0%
Conclusion: Monitor, model still reasonable
```

### Discrimination Power Stability
Monitor KS, Gini, AUC quarterly.

```
Initial Model (Development):
KS = 0.45, Gini = 0.65, AUC = 0.825

Q1: KS = 0.44, Gini = 0.64, AUC = 0.820 ✓ Stable
Q2: KS = 0.43, Gini = 0.63, AUC = 0.815 ✓ Stable
Q3: KS = 0.40, Gini = 0.60, AUC = 0.800 ⚠ Declining
Q4: KS = 0.37, Gini = 0.55, AUC = 0.775 ✗ Significant decline

Recommendation: Model needs retraining
```

### Default Rate Prediction Accuracy
Track actual vs. predicted defaults by score.

```
Score Bucket    Predicted PD    Actual DR    Backtest Verdict
High (800+)     1.0%           1.2%         ✓ Acceptable
Medium (650-799) 3.0%          2.8%         ✓ Acceptable
Low (< 650)     10.0%          12.5%        ✗ Underestimating

Action: Recalibrate low-score bucket
```

## Regulatory Considerations

### Non-Discrimination
- Cannot use prohibited factors (race, gender, religion, nationality)
- Protected classes cannot have disparate impact
- Regular disparate impact testing required

### Model Risk Management
- Model documentation (rationale, methodology, limitations)
- Independent validation
- Approval by senior management
- Monitoring and regular updates
- Clear governance

### Explainability
- Increasingly required by regulators
- Must explain score to applicants (if declined)
- Must show key negative factors
- GDPR right to explanation (EU)
