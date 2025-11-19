# Probability of Default (PD) Models

## Overview
PD is the probability that a counterparty will default (fail to meet obligations) within a specific time horizon, typically 1 year. It's a core input to credit risk models, capital calculations, and loan pricing.

## PD Definition & Characteristics

### Mathematical Definition
```
PD_1Y = P(Default in next 12 months | Current state)

Conditional on:
- Current credit rating
- Financial condition
- Macroeconomic state
- Industry/market conditions
```

### Estimation Approaches

#### 1. From Credit Ratings
**Mapping Default Rates to Ratings**:

```
Rating Agency Data (avg annual default rates):
Rating        Moody's    S&P    Fitch
AAA/AAA       0.00%      0.01%  0.02%
AA/AA         0.05%      0.08%  0.10%
A/A           0.10%      0.15%  0.20%
BBB/BBB       0.50%      0.60%  0.70%
BB/BB         2.50%      3.50%  3.80%
B/B           7.50%      9.00%  10.00%
CCC/CCC       25.00%     30.00% 32.00%
D/D           100.00%    100.00% 100.00%
```

**Advantages**:
- Well-validated, historical data
- Widely used, easy to understand
- Available for most corporates

**Disadvantages**:
- Rating changes lag real conditions
- Ratings sticky (slow to change)
- Not available for private companies
- Depends on rating agency

#### 2. From Credit Spreads (CDS)
**Relationship**:
```
CDS Spread ≈ PD × (1 - Recovery Rate)

Rearranging:
PD ≈ CDS Spread / (1 - Recovery Rate)

Example:
5-year CDS spread: 200 bps
Recovery rate assumption: 40%
Implied PD = 200 bps / (1 - 0.40) = 200 / 60 = 3.33% per year
5-year PD ≈ 15-16% cumulative

Calculation:
Cumulative PD = 1 - (1 - 3.33%)^5 = 15.7%
```

**Advantages**:
- Real-time market data
- Forward-looking (reflects market expectations)
- Available for traded credits

**Disadvantages**:
- Only available for publicly traded companies
- Includes liquidity premium (not just PD)
- Spread = PD × LGD × other factors

#### 3. From Structural Models (Merton)
**Concept**: Default occurs when firm value falls below debt value.

**Framework**:
```
Firm value: V_t = Assets
Debt: D (liability)
Equity: E_t = max(0, V_t - D) (option value)

Default event: V_t < D

Equity is a call option on firm value
As firm value declines, probability of default increases

PD_Merton = P(V_t < D | V_0, σ_V, r)
```

**Calculation** (simplified):
```
Input data:
- Stock price: $50
- Stock volatility: 30%
- Debt: $40M
- Risk-free rate: 2%

Step 1: Estimate firm value
Equity value = Stock price × Shares = $50 × 10M = $500M

Step 2: Estimate asset volatility
σ_A = σ_E × (E / (E + D × (1-τ)))
     = 30% × ($500M / ($500M + $40M × 0.8))
     = 30% × 0.942 = 28.3%

Step 3: Calculate distance to default
DD = ln(V/D) + (r - 0.5σ_A²)T / (σ_A√T)
   = ln(500/40) + (0.02 - 0.5×0.283²)×1 / (0.283×1)
   = 2.526 + 0.0160 / 0.283
   = 2.583 / 0.283 = 9.13 standard deviations

Step 4: Convert to PD
PD = N(-DD) = N(-9.13) ≈ 0.00000001 ≈ 0%

Interpretation: Very low default probability (company far from distress)
```

**Advantages**:
- Based on economic theory
- No need for rating history
- Can be calculated frequently

**Disadvantages**:
- Requires stock price data (not available for private firms)
- Asset volatility difficult to estimate
- Not great at predicting actual defaults

#### 4. Logistic Regression (Credit Scoring)
**Model Form**:
```
PD = e^z / (1 + e^z)

Where:
z = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ

X₁, X₂, ..., Xₙ = Financial ratios, payment history, industry
β₀, β₁, ..., βₙ = Coefficients estimated from data
```

**Example - Commercial Loan**:
```
Predictors:
- Leverage (Debt/EBITDA): 2.5x
- Interest Coverage: 3.5x
- ROA: 8%
- Industry: Manufacturing (risky)
- Payment history: 1 year (new)

Estimated coefficients:
β₀ = -2.5
β₁ = 0.8 (leverage)
β₂ = -0.3 (interest coverage)
β₃ = -0.05 (ROA)
β₄ = 0.4 (manufacturing)
β₅ = 0.2 (new customer)

Calculate:
z = -2.5 + 0.8×2.5 + (-0.3)×3.5 + (-0.05)×8 + 0.4×1 + 0.2×1
  = -2.5 + 2.0 - 1.05 - 0.4 + 0.4 + 0.2
  = -1.35

PD = e^(-1.35) / (1 + e^(-1.35)) = 0.259 / 1.259 = 20.6%

Interpretation: 20.6% probability of default within 1 year
```

## PD by Portfolio Segment

### Retail Mortgages
**Typical PD by Credit Score**:
```
Credit Score    PD (annual)
800+            0.10%
750-799         0.25%
700-749         0.50%
650-699         1.50%
600-649         3.00%
<600            8.00%

Portfolio average: 0.50-1.00%
```

### Credit Cards
**Typical PD by Risk Score**:
```
Risk Score      PD (annual)
A (best)        2-3%
B               4-5%
C               6-8%
D               9-12%
E (worst)       15-20%

Portfolio average: 5-8% (higher loss rate)
```

### Commercial Loans
**Typical PD by Rating**:
```
Rating          PD (annual)
Investment Grade:
  AAA           < 0.1%
  AA            0.1-0.3%
  A             0.3-0.8%
  BBB           0.8-2.0%

Non-Investment Grade:
  BB            2.0-5.0%
  B             5.0-15.0%
  CCC+          15.0-30.0%

Portfolio average: 1.5-2.5%
```

### Small Business Loans
**Typical PD by Age & Type**:
```
Vintage     Secured  Unsecured
Year 1      3.0%     8.0%
Year 2      2.5%     6.5%
Year 3      2.0%     5.5%
Year 4+     1.5%     4.0%
Portfolio avg: 2.0-3.0%
```

## Conditional vs. Unconditional PD

### Point-in-Time (PIT) PD
**Definition**: Current PD reflecting current economic conditions.

**Characteristics**:
- Reflects current macro environment
- Changes with economic cycle
- Procyclical (rises in recessions, falls in booms)
- Use for: Current risk assessment, pricing, limits

**Example**:
```
Normal times: PD = 1%
Economic boom (2005): PD = 0.5%
Recession (2009): PD = 3%
Recovery (2015): PD = 0.8%
```

### Through-the-Cycle (TTC) PD
**Definition**: Long-term average PD smoothing the economic cycle.

**Characteristics**:
- Smoothed over full economic cycle
- Relatively stable over time
- Non-procyclical
- Use for: Capital requirements, long-term pricing, internal limits

**Example**:
```
Economic cycle period: 2000-2020
Average PD over cycle: 1.2%
TTC PD = 1.2% (regardless of current conditions)

Use for capital: Even if current PD = 0.5%, use 1.2%
for capital calculation (buffer for downturns)
```

### Conversion: PIT ↔ TTC
```
If current PD (PIT) = 0.8%
And macroeconomic factor impact = -0.3%
TTC PD = 0.8% - (-0.3%) = 1.1%

Or: TTC PD known = 1.1%
In boom (macro factor +0.4%): PIT PD = 1.1% - 0.4% = 0.7%
In recession (macro factor -0.5%): PIT PD = 1.1% + 0.5% = 1.6%
```

## PD Migration & Transition Matrices

### Transition Matrix
**Definition**: Shows how PD ratings change over time.

```
Example: Annual transition matrix for corporates

From/To   AAA    AA    A    BBB   BB    B    CCC   Default
AAA       98.0   1.5  0.3  0.1   0.0   0.0  0.0   0.1
AA        0.5   96.0  2.5  0.8   0.1   0.0  0.0   0.1
A         0.1    2.0  94.0  3.2   0.5   0.1  0.0   0.1
BBB       0.0    0.2  4.0  90.0  4.5   1.0  0.2   0.1
BB        0.0    0.0  0.5  5.5  85.0  7.5  1.0   0.5
B         0.0    0.0  0.1  0.5   7.0  80.0 10.0  2.4
CCC       0.0    0.0  0.0  0.3   1.0  10.0 60.0  28.7

Reading: Starting AAA grade
98% remain AAA
1.5% migrate to AA
0.1% default

Multi-year PD: Use matrix repeatedly
2-year PD = 1 - (1-annual PD)²
If annual PD = 0.1%, then 2-year PD ≈ 0.2%
```

## PD Term Structure

### 1-Year vs. Multi-Year PD
```
Year 1 PD: 1% (next 12 months)
Year 2 PD: 1.1% (months 12-24)
Year 3 PD: 1.2% (months 24-36)

Cumulative 3-year PD:
= 1 - (1-1%) × (1-1.1%) × (1-1.2%)
= 1 - 0.99 × 0.989 × 0.988
= 1 - 0.9679
= 3.21%
```

### Hazard Rate Function
**Definition**: Instantaneous default probability at time t.

```
Cumulative default probability to time T:
P(τ ≤ T) = 1 - exp(-∫₀ᵀ λ(t) dt)

Where λ(t) = hazard rate at time t

For constant hazard rate λ:
P(τ ≤ T) = 1 - e^(-λT)

Example:
If λ = 1% annually, and constant:
1-year PD = 1 - e^(-0.01×1) = 0.995%
5-year PD = 1 - e^(-0.01×5) = 4.88%
```

## PD Backtesting & Validation

### Binomial Test
**Null hypothesis**: True PD = estimated PD

```
Example:
Estimated PD: 2%
Number of exposures: 500
Predicted defaults: 500 × 2% = 10

Actual defaults: 8

Binomial test:
P(X ≤ 8 | n=500, p=0.02) = ?
If p-value > 5%: PD estimate reasonable
If p-value < 5%: PD estimate too high or too low
```

### Population Stability Index (PSI)
**Measures**: Change in default rate distribution over time.

```
PSI = Σ (Rate_current - Rate_baseline) × ln(Rate_current / Rate_baseline)

Example:
PD Grade    Baseline %    Current %    PSI contribution
AAA         2.0%          1.5%         -0.0082
AA          8.0%          7.5%         -0.0064
A          25.0%         24.0%         -0.0400
BBB        40.0%         42.0%         +0.0990
BB         18.0%         19.0%         +0.0549
B+         5.0%           5.5%         +0.0490
B           2.0%          0.5%         -0.2953

Total PSI = 0.053 = 5.3%

Interpretation:
PSI < 5%: PD model still valid
PSI 5-10%: Monitor for changes
PSI > 10%: Model needs retraining
```

## PD in IFRS 9 / Loan Loss Provisioning

### 12-Month ECL
```
IFRS 9 Stage 1 (no significant increase in credit risk)
ECL = PD₁₂ months × LGD × EAD
Booked as: Loan loss reserve / adjustment
```

### Lifetime ECL
```
IFRS 9 Stage 2 & 3 (significant increase in credit risk or default)
ECL = Probability-weighted sum of outcomes
    = Σ P(scenario_i) × Loss_i

Where:
Scenario 1 (prob 40%): Recovery at par
Scenario 2 (prob 50%): Recovery at 80%
Scenario 3 (prob 10%): Total loss

ECL = 0.40×0 + 0.50×20% + 0.10×100% = 20%
```

## PD & Pricing

### Loan Pricing Formula
```
Spread = PD × (1 - Recovery) + Costs + Profit margin

Example:
PD: 2%
Recovery rate: 40% (so loss = 60%)
PD cost: 2% × 60% = 1.2%
Operating cost: 0.8%
Profit margin: 0.5%
Total spread: 2.5% over base rate

If base rate (SOFR): 4%
Loan rate: 4% + 2.5% = 6.5%
```

### Macro Adjustment
```
Base PD: 1.5%
Economic scenario adjustment:
- Baseline: 0%
- Recession: +0.8%
- Boom: -0.3%

Adjusted PD:
- Recession case: 1.5% + 0.8% = 2.3%
- Baseline case: 1.5%
- Boom case: 1.5% - 0.3% = 1.2%
```
