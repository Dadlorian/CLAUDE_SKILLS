# Market Risk Management

## Definition & Scope
Market risk is the risk of losses due to changes in market prices: interest rates, foreign exchange rates, equity prices, commodity prices, and volatility. It primarily affects trading portfolios.

## Market Risk Categories

### 1. Interest Rate Risk
**Definition**: Risk that changes in interest rates reduce portfolio value.

**Components**:
- **Parallel Shift**: Entire yield curve moves up/down
- **Twist**: Long-term rates move differently than short-term
- **Butterfly**: Change in curve convexity (long rates move differently than medium-term)
- **Non-parallel Moves**: Any yield curve reshaping

**Measurement**:
- **DV01 (Dollar Value of 1bps)**: Change in portfolio value from 1 basis point yield move
- **Duration**: Weighted average time to cash flows; sensitivity to parallel shifts
- **Key Rate Durations**: Sensitivity to specific points on yield curve
- **Convexity**: Second-order sensitivity (gamma) to yield changes

**Example**:
- Bond DV01: $10,000
- Yield moves up 5 bps
- Loss = $10,000 × 5 = $50,000

### 2. Foreign Exchange (FX) Risk
**Definition**: Risk from exposure to changes in exchange rates.

**Types**:
- **Translation Risk**: Risk to reported earnings from consolidating foreign subsidiaries
- **Transaction Risk**: Risk to cash flows from foreign transactions
- **Economic Risk**: Risk to competitiveness from FX moves
- **Volatility Risk**: Risk from changes in FX volatility

**Measurement**:
- **Delta**: FX exposure in base currency
- **FX Volatility**: Standard deviation of FX returns
- **Correlation**: Correlation between FX pairs

**Hedging**:
- Forward contracts: Lock in exchange rate
- Currency swaps: Exchange notional and cash flows
- Options: Downside protection with upside participation

### 3. Equity Risk
**Definition**: Risk from exposure to changes in equity prices.

**Components**:
- **Market Beta**: Sensitivity to overall market (market risk)
- **Alpha**: Return unrelated to market beta (idiosyncratic risk)
- **Volatility**: Variability of stock returns

**Measurement**:
- **Delta**: Exposure amount
- **Beta**: Sensitivity to market index (≈1.0 × market move)
- **Gamma**: Convexity (acceleration of losses in declining market)
- **Vega**: Sensitivity to equity volatility

**Example**:
- Long 100 shares of stock worth $50
- Portfolio delta: 100 shares × $50 = $5,000
- 10% market decline = -$500 loss

### 4. Commodity Risk
**Definition**: Risk from exposure to commodity price changes (oil, metals, agricultural).

**Characteristics**:
- **Mean Reversion**: Commodity prices tend to revert to long-term average
- **Seasonality**: Prices vary by season
- **Convenience Yield**: Benefit of holding physical commodity
- **Volatility**: Higher than financial assets

**Measurement**:
- **Spot Price Exposure**: Direct exposure to current prices
- **Basis Risk**: Difference between spot and futures prices
- **Term Structure Risk**: Changes in forward curve shape
- **Correlations**: Cross-commodity correlations

### 5. Volatility Risk
**Definition**: Risk from changes in market price volatility.

**Volatility Characteristics**:
- **Mean Reversion**: Volatility tends to revert to long-term average
- **Clustering**: High volatility clusters together over time
- **Leverage Effect**: Negative returns increase volatility more than positive returns
- **Smile/Skew**: Implied volatility varies with strike price

**Measurement**:
- **Vega**: Sensitivity to changes in implied volatility
- **Gamma**: Exposure to realized volatility
- **Vega Decay**: Loss if volatility compresses

## Greek Risk Measures

### Delta (Δ)
**Definition**: Change in option price for 1-unit change in underlying price.

**Interpretation**:
- Call Delta: 0 to 1 (long call = long stock)
- Put Delta: -1 to 0 (long put = short stock)
- ATM Call Delta ≈ 0.5
- Delta changes with underlying price (gamma) and time (theta)

### Gamma (Γ)
**Definition**: Change in delta for 1-unit change in underlying price; convexity risk.

**Interpretation**:
- Long options: Positive gamma (delta increases as stock rises)
- Short options: Negative gamma (delta decreases as stock rises)
- Gamma largest for ATM options
- Gamma largest when time to expiration decreases

**Trading Implication**:
- Long gamma = profit from volatility (long straddle/strangle)
- Short gamma = lose from volatility (short straddle/strangle)

### Vega (ν)
**Definition**: Change in option price for 1% change in implied volatility.

**Interpretation**:
- Long options: Positive vega (profit from increased volatility)
- Short options: Negative vega (lose from increased volatility)
- Vega largest for ATM options
- Vega largest when time to expiration increases

### Theta (Θ)
**Definition**: Change in option price for 1 day passage of time.

**Interpretation**:
- Long options: Negative theta (lose value as time passes)
- Short options: Positive theta (gain value as time passes)
- Theta accelerates as expiration approaches
- Theta larger for OTM options

### Rho (ρ)
**Definition**: Change in option price for 1% change in interest rates.

**Interpretation**:
- Call options: Positive rho
- Put options: Negative rho
- Less important than delta, gamma, vega, theta

## Value at Risk (VaR)

### Definition
VaR is the maximum loss that a portfolio is expected to incur with a given probability (confidence level) over a specific time horizon.

**Standard Definition**:
- 95% VaR (1-day): Maximum loss expected 95% of the time over 1 day
- 99% VaR (1-day): Maximum loss expected 99% of the time over 1 day

### Interpretation
- 95% VaR of $1M means there's a 5% chance of losing more than $1M in one day
- 99% VaR of $2M means there's a 1% chance of losing more than $2M in one day

### Approaches

#### 1. Parametric VaR (Delta-Normal)
Assumes returns are normally distributed.

```
VaR = Portfolio Value × Z × Std Dev × √Time

Where:
Z = Z-score for confidence level (1.645 for 95%, 2.326 for 99%)
Std Dev = Standard deviation of returns
Time = Time horizon in years
```

**Advantages**:
- Simple to calculate
- Fast for large portfolios
- Useful for linear positions

**Disadvantages**:
- Assumes normal distribution (underestimates tail risk)
- Doesn't capture non-linear risks (gamma)

#### 2. Historical Simulation VaR
Uses historical returns to estimate loss distribution.

**Process**:
1. Collect historical daily returns (typically 1-2 years)
2. Apply historical returns to current portfolio
3. Sort resulting P&L from worst to best
4. VaR = loss at percentile (e.g., 5th percentile for 95% VaR)

**Advantages**:
- Captures actual distribution shape
- No distributional assumptions
- Handles non-linear risks better

**Disadvantages**:
- Requires long history of data
- Past may not predict future
- Computational intensity for large portfolios

#### 3. Monte Carlo VaR
Simulates thousands of potential future market scenarios.

**Process**:
1. Specify stochastic model for each risk factor
2. Generate random scenarios for future market states
3. Reprice portfolio for each scenario
4. Sort P&L and determine loss at percentile

**Advantages**:
- Handles complex non-linear products
- Flexible modeling assumptions
- Captures tail risk better

**Disadvantages**:
- Computationally intensive
- Model risk in assumptions
- Convergence issues for tail percentiles

### Backtesting VaR
Compare VaR estimates to actual outcomes to validate model.

**Traffic Light Approach**:
- Green Zone (0-4 exceptions): Model adequate
- Yellow Zone (5-9 exceptions): Model questioned
- Red Zone (10+ exceptions): Model rejected

**Example**:
- 250 trading days per year
- 99% VaR should have ~2.5 exceptions
- Green zone: 0-4 exceptions
- Yellow zone: 5-9 exceptions
- Red zone: 10+ exceptions

## Stress Testing

**Purpose**: Understand portfolio behavior under extreme market conditions.

**Approaches**:
- **Historical Scenarios**: 1987 Black Monday, 2008 Crisis, 2011 Flash Crash
- **Hypothetical Scenarios**: 100 bps parallel shift, 50% equity decline, widening credit spreads
- **Sensitivity Analysis**: Vary one risk factor, hold others constant

**Example**:
- Current portfolio value: $100M
- VaR 99% (1-day): $2M
- Stress test (2008 scenario): -$15M
- Stress loss is 7.5x VaR, showing tail risk

## Risk Limits

### Trading Limits
- **VaR Limit**: Maximum daily VaR by desk/trader
- **Notional Limit**: Maximum notional exposure
- **Sector Limit**: Maximum exposure by sector
- **Counterparty Limit**: Maximum exposure by counterparty

### Greeks Limits
- **Delta Limit**: Maximum delta exposure
- **Gamma Limit**: Maximum gamma exposure
- **Vega Limit**: Maximum vega exposure
- **Basis Point Value Limit**: Maximum DV01 exposure

## Correlation & Correlation Breakdown

**Normal Correlation**:
- Stock-stock correlations: 0.2-0.8 (average ~0.5)
- Bond-stock correlation: -0.3 to 0 (diversification benefit)

**Correlation Breakdown**:
- During crises, correlations increase toward 1
- Traditional diversification fails when most needed
- Liquidity dries up, no buyers for distressed securities
- Credit spreads widen as credit risk reprices

**2008 Example**:
- Before crisis: Stock-Bond correlation ≈ -0.3
- During crisis: Stock-Bond correlation ≈ +0.5
- Diversification benefit disappeared
