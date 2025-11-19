# Risk Modeling Fundamentals

## Overview
Risk models are quantitative frameworks that estimate the magnitude and probability of losses from various sources. They form the foundation for risk management decisions, capital allocation, and pricing.

## Model Development Process

### 1. Problem Definition
**Step 1: Identify the Risk**
- What could go wrong?
- Magnitude and likelihood?
- What are we trying to measure?
- Who will use the model?
- For what decisions?

**Example - Credit Risk**:
- Problem: Portfolio of 1,000 loans to small businesses
- Concern: How many will default in next year?
- Use: Calculate capital requirement, price loans, set limits
- Users: Credit committee, risk committee, regulators

### 2. Conceptual Framework
**Step 2: Theory and Assumptions**

**Theory** (why the risk exists):
- Credit risk: Firms have uncertain future cash flows
- Market risk: Prices driven by supply/demand and fundamentals
- Liquidity risk: Funding gaps can emerge during stress

**Assumptions** (simplify reality):
- Probability of default follows logistic distribution
- Returns are normally distributed
- Correlations are stable over time
- Default events are independent

### 3. Data Collection & Preparation
**Step 3: Gather Historical Data**

**Data Requirements**:
- Default data: When did borrowers default? (for PD models)
- Recovery data: How much was recovered? (for LGD models)
- Market prices: Historical prices of tradeable instruments
- Macroeconomic: GDP, unemployment, interest rates
- Internal data: Bank transactions, relationships

**Data Quality**:
- Completeness: No missing values
- Accuracy: Correct classification, amounts
- Consistency: Uniform definitions over time
- Representativeness: Data relevant to current portfolio

**Example - PD Model Development**:
```
Loan origination database: 50,000 mortgages since 1995
Sample period: 2000-2020 (to capture 2008 crisis)
Target variable: Default (1) or not (0) within 1 year
Predictor variables:
- FICO score (700-800 range)
- Loan-to-value ratio (60-100%)
- Debt-to-income ratio (20-50%)
- Interest rate (3-8%)
- Property type (single-family, condo, etc.)

Data cleaning:
- Remove 500 loans with missing FICO (0.5% loss)
- Flag 200 with extreme values (LTV > 100% = data error)
- Adjust for recession periods (increased defaults)

Final sample: 49,300 loans
```

### 4. Model Estimation
**Step 4: Fit the Model to Data**

**Logistic Regression Example**:
```
Model: P(Default=1 | FICO, LTV, DTI, Rate) = e^z / (1 + e^z)

z = β₀ + β₁×FICO + β₂×LTV + β₃×DTI + β₄×Rate

Estimate coefficients using Maximum Likelihood Estimation:
β₀ = -8.5 (intercept)
β₁ = -0.003 (FICO: higher score = lower default)
β₂ = 0.02 (LTV: higher LTV = higher default)
β₃ = 0.05 (DTI: higher DTI = higher default)
β₄ = 0.1 (Rate: higher rate = higher default)

Standard errors and p-values:
β₁: -0.003 ± 0.0005, t-stat = -6.0 ✓ Significant
β₂: 0.02 ± 0.003, t-stat = 6.7 ✓ Significant
β₃: 0.05 ± 0.02, t-stat = 2.5 ✓ Significant
β₄: 0.1 ± 0.08, t-stat = 1.25 ✗ Not significant (remove)

Revised model without rate:
β₀ = -8.3
β₁ = -0.003
β₂ = 0.02
β₃ = 0.05
```

### 5. Model Validation
**Step 5: Test Model Performance**

**In-Sample Testing** (on development data):
```
Correctly classified: 95% of loans
Sensitivity: 65% of actual defaults identified
Specificity: 98% of non-defaults identified
AUC: 0.82 (good discrimination)
```

**Out-of-Sample Testing** (on holdout data):
```
Same metrics on 20% holdout sample:
Correctly classified: 93% of loans
Sensitivity: 62% of defaults identified
Specificity: 97% of non-defaults identified
AUC: 0.80 (similar to in-sample ✓)

Conclusion: Model generalizes well, not overfit
```

**Calibration Testing**:
```
Score deciles and actual default rates:

Decile    Score Range    Predicted PD    Actual DR    Status
1 (Best)  800-900        0.5%           0.3%         ✓
2         750-799        1.2%           1.1%         ✓
3         700-749        2.5%           2.4%         ✓
...
10 (Worst) <600          15.0%          16.2%        ✓

Conclusion: Well-calibrated model
Predicted PD ≈ Actual default rate
```

### 6. Implementation & Monitoring
**Step 6: Deploy and Track**

**Implementation**:
- Score new applicants
- Make credit decisions
- Price loans based on risk score
- Set credit limits
- Allocate capital

**Monitoring**:
- Track actual vs. predicted defaults monthly
- Calculate Population Stability Index (PSI)
- Monitor coefficient stability
- Regular backtesting (annual or more frequently)
- Refresh data and retrain periodically

## Model Risk Management

### Key Risks in Modeling

#### 1. Model Risk
**Definition**: Risk that model doesn't accurately represent reality.

**Sources**:
- Specification risk: Wrong functional form
- Parameter risk: Incorrect parameter estimates
- Assumption risk: Key assumptions violated
- Data risk: Poor quality data leads to poor estimates

**Example**:
```
Model assumes normal distribution of returns
Reality: Returns have fat tails
Result: VaR underestimates tail losses
Solution: Use historical simulation or non-normal distributions
```

#### 2. Data Risk
**Definition**: Risk that historical data doesn't represent future.

**Sources**:
- Sample selection bias: Development sample not representative
- Survivorship bias: Only existing firms in data (failed firms removed)
- Look-ahead bias: Using information not available at decision time
- Concept drift: Relationships change over time

**Example - Survivorship Bias**:
```
Backtest performance: 20% annual return
Reality: 12% annual return
Why? Model backtested on funds that survived
Failed funds removed from database
Actual investors had to pick funds without knowing which survived
```

#### 3. Parameter Risk
**Definition**: Risk that parameters estimated on sample don't apply to future.

**Sources**:
- Estimation error from finite sample
- Structural breaks (regime changes)
- Correlation changes in stress
- Volatility increases in crises

**Example - Correlation Risk**:
```
Normal correlation (equity-bond): -0.3
2008 Crisis correlation: -0.1 (diversification failed)
Model assumed -0.3, underestimated loss
Result: Portfolio diversification didn't provide expected benefit
```

### Model Governance Framework

```
1. Model Approval
   - All models must be approved by Risk Committee
   - Documentation required before use
   - Clear methodology and rationale
   - Sign-off from independent validators

2. Model Ownership
   - Developer: Creates and maintains
   - Owner: Business unit responsible for use
   - Validator: Independent testing (may be external)
   - Consumer: Uses model for decisions

3. Model Monitoring
   - Performance tracking (backtesting)
   - Stability monitoring (PSI, coefficient changes)
   - Performance vs. alternatives
   - Regulatory feedback

4. Model Updating
   - Data refresh: Incorporate new observations
   - Retraining: Periodically retrain (annual minimum)
   - Changes: Document all changes, revalidate
   - Governance: Changes require re-approval

5. Model Retirement
   - When assumptions significantly violated
   - When replaced by better model
   - When regulatory requirements change
   - Proper documentation of retirement
```

## Statistical Foundations

### Probability Distributions

#### Normal Distribution
**Uses**: Market risk (returns), credit losses in large portfolios

**Characteristics**:
- Bell curve, symmetric
- Defined by mean (μ) and standard deviation (σ)
- 68% within ±1σ, 95% within ±2σ, 99.7% within ±3σ
- Tail risk underestimated (light tails)

**PDF**: f(x) = (1/(σ√(2π))) × e^(-(x-μ)²/(2σ²))

#### Student's t-Distribution
**Uses**: Financial data (fat tails), risk measurement

**Characteristics**:
- Similar to normal but with heavier tails
- Defined by degrees of freedom (df)
- As df → ∞, approaches normal
- Better captures extreme events

#### Beta Distribution
**Uses**: Probabilities (0-1), recovery rates (LGD), default probabilities

**Characteristics**:
- Bounded [0,1]
- Flexible shape (skewed, bimodal)
- Can model non-symmetric distributions

#### Exponential Distribution
**Uses**: Time to default (survival analysis), severity of operational losses

**Characteristics**:
- Only defined for positive values
- Memoryless property
- Decreasing probability over time

### Correlation & Dependence

#### Pearson Correlation
**Definition**: Measures linear relationship between two variables.

```
ρ = Cov(X,Y) / (σ_X × σ_Y)

Ranges from -1 (perfect negative) to +1 (perfect positive)
0 = no linear relationship

Example:
Two stocks with correlation 0.6:
If stock A up 10%, stock B likely up 6% on average
```

**Limitations**:
- Only captures linear relationships
- Pearson ρ = 0 doesn't mean independent
- Ignores tail dependence

#### Spearman Rank Correlation
**Definition**: Correlation of ranks, not values.

**Advantages**:
- Captures non-linear monotonic relationships
- More robust to outliers
- Better for non-normal data

#### Copulas
**Definition**: Describes dependence structure separately from marginal distributions.

**Advantage**: Captures tail dependence (how often both variables extreme simultaneously).

**Types**:
- Gaussian copula: Normal dependence (2008 crisis: not fat-tailed enough)
- t-copula: Heavier tails, better for crisis modeling
- Clayton, Gumbel, etc.: Asymmetric tail dependence

## Model Validation Techniques

### Backtesting
**Definition**: Compare model predictions to actual outcomes.

**Process**:
1. Generate predictions
2. Record actual outcomes
3. Calculate exceptions/errors
4. Statistical test for model accuracy

**Example - Credit Model**:
```
Score 500 loans as 2% PD each
Expected defaults: 500 × 2% = 10
Actual defaults: 8
Binomial test: Consistent with 2% PD ✓
```

### Sensitivity Analysis
**Definition**: Vary input assumptions, observe output changes.

```
VaR Model Sensitivity:

Current: 99% VaR (1-day) = $2M
Confidence level → 95%: VaR = $1.2M
Confidence level → 99.9%: VaR = $3.5M

Data period → 1 year: VaR = $1.8M
Data period → 3 years: VaR = $2.3M (includes 2008 crisis)

Volatility → -10%: VaR = $1.8M
Volatility → +10%: VaR = $2.2M

Conclusion: VaR sensitive to assumptions
Need to stress test key assumptions
```

### Stress Testing
**Definition**: Test model behavior under extreme scenarios.

```
Credit model stress test:
Base case PD: 2%
Economic downturn: PD → 3.5%
Deep recession: PD → 6%
Depression: PD → 10%

Conclusion: PD could increase 3-5x in stress
Capital planning should account for this
```

### Reverse Engineering
**Definition**: Test if output is reasonable for given inputs.

```
Credit scorecard output: PD = 0.5% for applicant
Expected: Strong financials, excellent history
Actual: Weak financials, bad payment history

Question: Why is PD so low?
Investigation: Data entry error, bad coefficient
Action: Fix and revalidate
```
