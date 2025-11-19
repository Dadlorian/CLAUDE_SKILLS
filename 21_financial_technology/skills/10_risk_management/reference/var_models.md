# Value at Risk (VaR) Models

## Overview
VaR quantifies the maximum loss expected at a given confidence level over a specific time horizon. It's the standard risk metric across the financial industry, used for both regulatory capital and internal risk management.

## VaR Definition & Interpretation

### Mathematical Definition
```
P(Loss > VaR_α) = α

Where:
P() = Probability
α = Confidence level (e.g., 0.05 for 95% VaR, 0.01 for 99% VaR)
```

### Example
- Portfolio value: $100M
- 95% VaR (1-day): $2M
- Interpretation: There's a 95% probability the portfolio won't lose more than $2M in one day
- Or: We expect to lose more than $2M about 1 day per 20 trading days

### Time Horizon Scaling
VaR scales with time horizon assuming independent returns:
```
VaR(T days) = VaR(1 day) × √T

Example:
- 1-day 99% VaR: $2M
- 10-day 99% VaR: $2M × √10 = $6.32M
```

## VaR Approaches

### 1. Parametric VaR (Variance-Covariance / Delta-Normal)

**Assumption**: Returns are normally distributed.

**Formula**:
```
VaR = Portfolio Value × Z_α × σ

Where:
Z_α = Z-score for confidence level
σ = Standard deviation of returns
```

**Z-scores**:
- 90% VaR: 1.282
- 95% VaR: 1.645
- 97.5% VaR: 1.96
- 99% VaR: 2.326
- 99.9% VaR: 3.09

**Example**:
```
Portfolio: 100 shares of stock worth $50 = $5,000
Historical volatility: 2% daily
95% VaR: $5,000 × 1.645 × 0.02 = $164.50

Interpretation: 95% of the time, maximum 1-day loss is $164.50
Or: On average, lose more than $164.50 once every 20 days
```

**Multi-asset Example**:
```
Portfolio:
- $1M in US Equities (volatility 1.5%, weight 0.5)
- $1M in Bonds (volatility 0.5%, weight 0.5)
- Correlation: 0.3

Std Dev = √[(0.5×0.015)² + (0.5×0.005)² + 2×0.5×0.015×0.5×0.005×0.3]
        = √[0.0000563 + 0.0000063 + 0.0000113]
        = 0.00950 = 0.95%

99% VaR (1-day) = $2M × 2.326 × 0.00950 = $44,194
```

**Advantages**:
- Simple, fast calculation
- Works well for linear portfolios
- Analytical solution
- Easy to understand

**Disadvantages**:
- Assumes normal distribution (underestimates tail risk)
- Normal distribution has light tails
- Cannot capture skewness (asymmetry)
- Cannot capture fat tails (excess kurtosis)
- Poor for non-linear instruments (options)

### 2. Historical Simulation VaR

**Approach**: Use actual historical returns to estimate loss distribution.

**Process**:
1. Collect historical daily returns (typically 1-3 years of data)
2. Revalue portfolio with historical returns
3. Calculate P&L for each historical return
4. Sort P&Ls from worst to best
5. VaR = Loss at specified percentile

**Example**:
```
Historical returns data: Last 250 trading days

Sort P&Ls (worst to best):
Rank   Return    P&L
1      -3.5%     -$175k    ← Worst day
2      -3.2%     -$160k
3      -3.0%     -$150k
4      -2.8%     -$140k
5      -2.5%     -$125k
...
10     -1.8%     -$90k
...
245    +2.8%     +$140k
246    +3.0%     +$150k
247    +3.2%     +$160k
248    +3.5%     +$175k    ← Best day
249    +3.7%     +$185k
250    +4.0%     +$200k

95% VaR = Loss at 5th percentile = Rank 13 loss = -$105k
99% VaR = Loss at 1st percentile = Rank 3 loss = -$150k
```

**Advantages**:
- No distributional assumptions
- Captures actual return shape
- Handles fat tails better than parametric
- Incorporates correlations naturally
- Works for non-linear products

**Disadvantages**:
- Requires significant historical data
- Past may not predict future
- Computationally intensive for large portfolios
- Tail estimates based on limited historical events
- Long lookback period might include irrelevant old data

### 3. Monte Carlo VaR

**Approach**: Simulate thousands of potential future scenarios using stochastic models.

**Process**:
1. Specify stochastic model for each risk factor
   - Geometric Brownian Motion for equities
   - Vasicek model for interest rates
   - Jump-diffusion for credit spreads
2. Generate random scenarios (e.g., 10,000 paths)
3. Revalue portfolio for each scenario
4. Calculate P&L for each scenario
5. Sort P&Ls and extract percentile

**Example - Single Stock**:
```
Equity Spot Price: $100
Volatility: 20% annual (1.26% daily)
Risk-free rate: 2% annual (0.008% daily)

Geometric Brownian Motion:
dS/S = r dt + σ dW

Generate 10,000 random paths for 1 day:
Path 1: S = 100 × exp((0.0002 - 0.5×0.0126²) + 0.0126×Z₁) = $99.45, P&L = -$55
Path 2: S = 100 × exp((0.0002 - 0.5×0.0126²) + 0.0126×Z₂) = $100.85, P&L = +$85
...
Path 10,000: S = ... P&L = ...

Sort by P&L:
95% VaR = 5th percentile loss = -$305
99% VaR = 1st percentile loss = -$510
```

**Multi-asset with Correlations**:
```
Portfolio: 50% equities, 50% bonds
Equity volatility: 20%
Bond volatility: 5%
Correlation: -0.3

Generate correlated random paths:
Z₁ ~ N(0,1) for equities
Z₂ = ρ×Z₁ + √(1-ρ²)×Z₃ for bonds
Z₃ ~ N(0,1)

With ρ = -0.3:
Z₂ = -0.3×Z₁ + √(1-0.09)×Z₃ = -0.3×Z₁ + 0.954×Z₃
```

**Advantages**:
- Handles complex non-linear products (options, bonds with embedded options)
- Flexible modeling assumptions
- Captures full distribution
- Can incorporate jumps, regime changes
- Can model correlations dynamically

**Disadvantages**:
- Computationally intensive
- Model risk in assumptions
- Convergence issues (need many scenarios for tail)
- Random noise in estimates
- Difficult to debug/understand

## VaR Limitations

### 1. Sub-additivity Violation
VaR is not sub-additive, meaning:
```
VaR(Portfolio A + B) > VaR(A) + VaR(B)

This violates portfolio diversification principle
```

**Example**:
- Position A: 95% VaR = $1M
- Position B: 95% VaR = $1M
- A + B together: 95% VaR might be > $2M

### 2. Tail Risk Not Fully Captured
VaR only shows maximum loss at a percentile, not magnitude of worse losses.

**Example**:
- 99% VaR = $2M (1% chance of loss > $2M)
- But that 1% could be $2M, $5M, $20M, or unlimited
- VaR doesn't differentiate

### 3. Assumption Dependence
Results highly dependent on model assumptions:
- Distribution assumption (normal, t-distribution, historical)
- Historical period (1 year, 2 years, 5 years)
- Correlations (dynamic or static)
- Risk factors (full revaluation vs. sensitivities)

### 4. Crisis Conditions
VaR poorly predicts losses in stress:
- Assumes correlations stable (they break in crises)
- Assumes distribution shape constant (tails thicken in crises)
- Assumes liquidity (disappears in crises)

**2008 Crisis Example**:
- Mortgage-backed securities had low historical volatility
- Parametric VaR underestimated risk
- Actual losses far exceeded VaR estimates
- Models failed because distribution changed

## Enhanced Risk Measures

### Expected Shortfall (ES) / Conditional VaR (CVaR)
**Definition**: Average loss exceeding VaR.

**Formula**:
```
ES_α = E[Loss | Loss > VaR_α]

Example:
99% VaR = $2M
99% ES = Average of all losses > $2M = $3.2M
```

**Advantage**: Captures tail severity better than VaR.

### Incremental VaR (IVaR)
**Definition**: Change in portfolio VaR from adding/removing position.

**Formula**:
```
IVaR = VaR(Portfolio) - VaR(Portfolio w/o Position)
```

**Use**: Calculate marginal risk contribution of each position.

### Marginal VaR (MVaR)
**Definition**: Partial derivative of portfolio VaR with respect to position size.

**Use**: Approximate impact of small changes in position.

### Component VaR (CVaR)
**Definition**: Allocated portion of portfolio VaR to each position.

**Property**: Sum of component VaRs = Total VaR

**Use**: Risk attribution, limit allocation

## VaR Backtesting

### Purpose
Compare VaR estimates to actual outcomes to validate model accuracy.

**Target**: For 250 trading days, 95% VaR should have ~13 exceptions (5% of 250).

### Traffic Light Approach (Basel)
```
Green Zone (0-4 exceptions):
- Model acceptable
- No capital add-on

Yellow Zone (5-9 exceptions):
- Model questioned
- 40-100% capital add-on depending on exceptions

Red Zone (10+ exceptions):
- Model rejected
- 100% capital add-on (must use standardized approach)
```

### Example:
```
250 trading days of data
95% VaR estimated daily
Actual exceptions: 8 days where loss exceeded 95% VaR

Traffic Light Result: Yellow Zone
- Model is somewhat accurate but overly optimistic
- Increase capital requirement
```

### Types of Backtests
- **Unconditional Coverage**: Do we have right number of exceptions?
- **Conditional Coverage**: Are exceptions clustered (suggesting model breaks in stress)?
- **Independence Test**: Are exceptions randomly distributed?

## VaR Implementation Considerations

### Calculation Frequency
- Daily: Standard for regulatory capital
- Intra-day: For high-risk operations
- Period-end: For reporting

### Confidence Level & Time Horizon
- Regulatory Capital: 99% confidence, 10 days
- Internal Limit Monitoring: 95% confidence, 1 day
- Stress Testing: 99.9% confidence, historical scenarios

### Portfolio Granularity
- By trading desk
- By product type
- By risk factor
- Total enterprise

### Documentation & Governance
- Methodology clearly documented
- Assumptions reviewed periodically
- Backtesting results tracked
- Governance approvals in place
