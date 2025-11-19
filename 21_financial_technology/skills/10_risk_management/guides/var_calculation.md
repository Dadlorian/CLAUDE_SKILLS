# VaR Calculation Guide

## Three Approaches Compared

### Approach 1: Parametric (Delta-Normal) VaR

**Best for**: Linear portfolios, equities, bonds, daily monitoring

**Steps**:

1. **Calculate portfolio daily returns**
```
Portfolio value over 250 days:
Day 1: $1,000,000
Day 2: $1,005,000 (return = 0.5%)
Day 3: $1,000,000 (return = -0.497%)
...
Day 250: $1,015,000

Calculate standard deviation of returns:
Mean return: 0.02% daily
Standard deviation: 1.25% daily
```

2. **Determine confidence level & time horizon**
```
Common levels:
- 95% VaR (1-day): Daily risk monitoring
- 99% VaR (1-day): Regulatory capital
- 99% VaR (10-day): Regulatory capital (Basel III)

Z-scores:
- 95% confidence: Z = 1.645
- 99% confidence: Z = 2.326
- 99.9% confidence: Z = 3.09
```

3. **Calculate VaR**
```
VaR = Portfolio Value × Z × Std Dev × √Time

Example:
- Portfolio: $1,000,000
- Std Dev: 1.25% daily
- 95% confidence: Z = 1.645
- Time: 1 day

VaR = $1,000,000 × 1.645 × 0.0125 × √1
    = $1,000,000 × 1.645 × 0.0125
    = $20,563

Interpretation: 95% chance of not losing more than $20,563 in one day
Or: 5% chance of losing > $20,563
```

4. **Scale to different time horizons**
```
10-day VaR = 1-day VaR × √10

Example:
1-day 99% VaR: $30,000
10-day 99% VaR: $30,000 × √10 = $94,868

Used for regulatory capital:
Basel III requires 10-day 99% VaR for capital calculation
```

**Advantages & Disadvantages**:
```
Advantages:
✓ Simple, fast calculation
✓ Easy to understand and communicate
✓ Analytical solution
✓ Good for linear portfolios

Disadvantages:
✗ Assumes normal distribution (underestimates tail risk)
✗ Cannot handle non-linear instruments (options)
✗ Correlation assumption may be incorrect
✗ Underperforms in crisis (correlations break down)
```

### Approach 2: Historical Simulation VaR

**Best for**: Any portfolio type, capture empirical distributions

**Steps**:

1. **Collect historical returns**
```
Data: Last 250 trading days (1 year)
Get daily returns for each position:

Date        Stock A     Stock B     Bond Fund
2024-01-01  +0.75%     -0.25%      +0.10%
2024-01-02  -0.50%     +0.30%      +0.05%
2024-01-03  +1.20%     +0.40%      -0.15%
...
2024-12-31  -0.25%     +0.15%      +0.08%
```

2. **Calculate portfolio P&L for each historical return**
```
Portfolio (current):
- Stock A: $400,000
- Stock B: $300,000
- Bond Fund: $300,000
- Total: $1,000,000

Apply historical returns:

Scenario 1 (2024-01-01 returns):
- Stock A: $400,000 × 0.75% = +$3,000
- Stock B: $300,000 × (-0.25%) = -$750
- Bonds: $300,000 × 0.10% = +$300
- Portfolio P&L: +$2,550

Scenario 2 (2024-01-02 returns):
- Stock A: $400,000 × (-0.50%) = -$2,000
- Stock B: $300,000 × 0.30% = +$900
- Bonds: $300,000 × 0.05% = +$150
- Portfolio P&L: -$950

... (repeat for all 250 days)
```

3. **Sort P&Ls from worst to best**
```
Rank   P&L
1      -$45,000  (worst day)
2      -$40,000
3      -$38,000
4      -$35,000
5      -$32,000
...
125    -$500
126    +$100
...
245    +$35,000
246    +$38,000
247    +$40,000
248    +$42,000
249    +$45,000
250    +$48,000  (best day)
```

4. **Extract percentile for VaR**
```
95% VaR: 5th percentile = Rank 13 = -$25,000
99% VaR: 1st percentile = Rank 3 = -$38,000

Interpretation:
- 95% of the time, portfolio loses less than $25,000
- 5% of the time, portfolio loses more than $25,000
- Only 1% of the time does it lose more than $38,000
```

**Advantages & Disadvantages**:
```
Advantages:
✓ No distributional assumptions
✓ Captures actual return shape
✓ Handles fat tails (if in history)
✓ Non-linear products work

Disadvantages:
✗ Requires long history (250+ days minimum)
✗ Past may not predict future
✗ Tail estimates based on limited events
✗ Computationally intensive
✗ Poor for rare events (hasn't happened yet)
```

### Approach 3: Monte Carlo VaR

**Best for**: Complex portfolios, forward-looking, tail risk

**Steps**:

1. **Specify stochastic model for risk factors**
```
Risk factor: Equity Index
Model: Geometric Brownian Motion
dS/S = μ dt + σ dW

Where:
μ = drift (expected return) = 2% annually = 0.008% daily
σ = volatility = 20% annually = 1.26% daily
dt = 1 day
dW = random normal increment
```

2. **Generate random scenarios**
```
Generate 10,000 random paths, 1-day horizon:

For each scenario:
Random shock: Z ~ N(0,1)
Price change: ΔS/S = μ×dt + σ×√dt×Z
             = 0.008% + 1.26%×Z

Scenario 1: Z = -2.5, ΔS/S = 0.008% - 3.15% = -3.14%
Scenario 2: Z = +0.5, ΔS/S = 0.008% + 0.63% = 0.64%
...
Scenario 10,000: Z = +1.8, ΔS/S = 0.008% + 2.27% = 2.28%

New stock price (current $100):
Scenario 1: $100 × (1 - 0.0314) = $96.86
Scenario 2: $100 × (1 + 0.0064) = $100.64
...
```

3. **Reprice portfolio for each scenario**
```
Portfolio:
- Stock position: 1,000 shares × $100 = $100,000
- Bond position: $900,000

For each scenario:
- Calculate new stock price
- Bond price changes less (lower volatility)
- Calculate new portfolio value
- Calculate P&L = New Value - Current Value

Example:
Scenario 1:
- Stock new price: $96.86
- Stock value: 1,000 × $96.86 = $96,860
- Bond value: ~$899,100 (bonds down slightly due to correlations)
- New portfolio: $95,960
- P&L: -$4,040

Scenario 2:
- Stock new price: $100.64
- Stock value: $100,640
- Bond value: ~$900,900
- New portfolio: $1,001,540
- P&L: +$1,540
```

4. **Sort P&Ls and extract percentile**
```
Sort 10,000 P&Ls from worst to best:
5% of 10,000 = 500
99% of 10,000 = 100

95% VaR = P&L at position 500 = -$25,300
99% VaR = P&L at position 100 = -$38,500
```

**Advantages & Disadvantages**:
```
Advantages:
✓ Handles complex products (options, exotic derivatives)
✓ Can model correlations dynamically
✓ Can incorporate jumps, regime changes
✓ Forward-looking (not based on history)
✓ Flexible modeling assumptions

Disadvantages:
✗ Computationally intensive (slow)
✗ Model risk in assumptions
✗ Convergence issues for tail (need many scenarios)
✗ Random noise in estimates
✗ Black box (hard to understand why result)
```

## Comparison Example

**Portfolio**: $10M total
- 60% stocks (high volatility, 20% annual)
- 40% bonds (low volatility, 5% annual)
- Correlation: -0.3

**Results comparison**:
```
Approach           1-day 95% VaR   1-day 99% VaR   Computation Time
Parametric         $245,000        $366,000        < 1 second
Historical Sim     $265,000        $380,000        1-2 seconds
Monte Carlo        $260,000        $375,000        2-5 seconds

Differences explained:
- Parametric lowest: Assumes normal distribution (lighter tails)
- Historical: Based on actual observed returns
- Monte Carlo: Simulated futures, can capture tail risk
- All reasonable, choose based on use case
```

## Best Practices

### Calculation Frequency
```
Daily: For risk monitoring and trader limits
- Calculate during market hours
- Report before end of day
- Used to set next day's limits

Weekly: For management reporting
- Summary by desk, product, business line
- Stress test results
- Comparison to limits

Monthly: For board reporting
- Executive summary
- Trend analysis
- Backtesting results
```

### Validation & Backtesting
```
Monthly backtesting (250 trading days data):

Expected exceptions at 95% VaR: 5% of 250 = 12-13 days
Expected exceptions at 99% VaR: 1% of 250 = 2-3 days

Count actual days where loss > VaR:
Month 1: 3 exceptions at 95% ✓ (expect 12)
Month 2: 5 exceptions at 95% ✓
...
After 12 months: 8 total exceptions ✓ (expect ~13)

If too many exceptions: Model underestimates risk
If too few exceptions: Model overstates risk
Adjust model or underlying assumptions
```

### Common Pitfalls

| Issue | Solution |
|-------|----------|
| Not updating data | Refresh historical data monthly |
| Wrong confidence level | Use 99% for capital (Basel III), 95% for monitoring |
| Ignoring non-linear risk | Use Monte Carlo or historical simulation for options |
| Not backtesting | Mandatory monthly backtesting |
| Ignoring correlation changes | Use stress test with changed correlations |
| Concentration risk hidden | Break down VaR by position, desk, product |
