# Performance Attribution and Analytics

## Performance Attribution Definition

Performance attribution analyzes the sources of portfolio returns, separating returns into:
1. Asset allocation decisions (strategic)
2. Security selection decisions (tactical)
3. Market exposure effects
4. Factor exposures

This helps identify which decisions contributed to outperformance or underperformance.

## Single-Period Attribution: Brinson-Fachler Model

### Framework

The Brinson-Fachler model decomposes return into allocation and selection effects:

```
Total Return = Return from Market Exposure + Return from Tactical Decisions

Excess Return = Allocation Effect + Selection Effect + Interaction Effect
```

### Allocation Effect

**Definition**: Impact of over/underweighting asset classes vs benchmark

**Formula**:
```
Allocation Effect = Σ (wp,i - wb,i) × (rb,i - rb) × 100 basis points

Where:
wp,i = portfolio weight in asset class i
wb,i = benchmark weight in asset class i
rb,i = benchmark return of asset class i
rb = total benchmark return
```

**Example**:
```
Asset Class: US Equities
Portfolio Weight: 65%
Benchmark Weight: 60%
Asset Class Return: 10%
Total Benchmark Return: 8%

Allocation Effect = (65% - 60%) × (10% - 8%) = 5% × 2% = 0.10%
(Positive effect from overweight in outperforming class)
```

### Selection Effect

**Definition**: Impact of outperformance/underperformance of selected securities vs benchmark in each asset class

**Formula**:
```
Selection Effect = Σ wb,i × (rp,i - rb,i) × 100 basis points

Where:
wb,i = benchmark weight in asset class i
rp,i = portfolio return in asset class i
rb,i = benchmark return in asset class i
```

**Example**:
```
Asset Class: US Equities
Benchmark Weight: 60%
Portfolio Return (equities): 11%
Benchmark Return (equities): 10%

Selection Effect = 60% × (11% - 10%) = 60% × 1% = 0.60%
(Positive effect from security selection)
```

### Combined Analysis

**Example Attribution Report**:
```
Portfolio Return: 9.5%
Benchmark Return: 8.0%
Excess Return: 1.5% (150 basis points)

Attribution:
Allocation Effect: +0.50%
  - Overweight US Equities: +0.10%
  - Underweight Bonds: +0.30%
  - International Underweight: +0.10%

Selection Effect: +0.85%
  - US Equities Selection: +0.60%
  - Bond Selection: +0.20%
  - International Selection: +0.05%

Interaction Effect: +0.15%
Total Excess Return: +1.50%
```

## Multi-Period Attribution

### Linking Single-Period Returns

For multiple periods, use geometric linking:

```
Cumulative Return = (1 + R1) × (1 + R2) × ... × (1 + Rn) - 1

Example: Returns of 5%, 3%, -2%
Cumulative Return = (1.05) × (1.03) × (0.98) - 1 = 6.07%
```

### Smoothing Methods

**Simple Average**: Not appropriate (ignores compounding)
**Geometric Linking**: Standard approach (accounts for compounding)
**Money-Weighted Return**: Accounts for timing of cash flows (internal rate of return)

## Risk-Adjusted Performance Measures

### Sharpe Ratio

**Definition**: Risk-adjusted return per unit of risk

**Formula**:
```
Sharpe Ratio = (Rp - Rf) / σp

Where:
Rp = Portfolio return
Rf = Risk-free rate
σp = Portfolio volatility (standard deviation)
```

**Interpretation**:
- Higher ratio = better risk-adjusted returns
- >1.0: Excellent risk-adjusted performance
- 0.5-1.0: Good performance
- <0.5: Poor performance
- Assumes risk measured by volatility

**Limitations**:
- Assumes volatility = risk (not always true)
- Penalizes upside volatility
- Sensitive to risk-free rate choice
- May not reflect downside risk

### Sortino Ratio

**Definition**: Risk-adjusted return using downside volatility only

**Formula**:
```
Sortino Ratio = (Rp - Rf) / σd

Where:
σd = Downside volatility (volatility of negative returns only)
```

**Advantage**: Focuses on downside risk (losses), not upside volatility

**Example**:
```
Sharpe Ratio: 0.80 (includes all volatility)
Sortino Ratio: 1.20 (only counts downside volatility)
Interpretation: Portfolio does better on downside-adjusted basis
```

### Treynor Ratio

**Definition**: Risk-adjusted return per unit of systematic risk (beta)

**Formula**:
```
Treynor Ratio = (Rp - Rf) / β

Where:
β = Beta (systematic risk)
```

**Use Case**: Evaluate managers or portfolios with different systematic risks
**Interpretation**: Higher is better

### Information Ratio

**Definition**: Excess return per unit of tracking error

**Formula**:
```
Information Ratio = (Rp - Rb) / TE

Where:
Rp = Portfolio return
Rb = Benchmark return
TE = Tracking Error (standard deviation of excess returns)
```

**Interpretation**:
- >0.5: Good active management
- 0.3-0.5: Reasonable active management
- <0.3: May not justify active management fees

**Example**:
```
Portfolio Return: 9%
Benchmark Return: 8%
Tracking Error: 3%
Information Ratio = (9% - 8%) / 3% = 0.33
(Reasonable but not excellent active performance)
```

## Factor Attribution

### Factor Decomposition

**Approach**: Decompose portfolio return into factor exposures

**Factors Analyzed**:
- **Market Factor**: Overall market risk exposure (beta)
- **Value Factor**: Exposure to low P/E, high book value
- **Momentum Factor**: Exposure to price trends
- **Quality Factor**: Exposure to profitable, stable companies
- **Size Factor**: Small-cap vs large-cap exposure
- **Low Volatility Factor**: Lower beta stocks

**Model**:
```
Rp = αp + β_market × Rm + β_value × RV + β_momentum × RM + ...

Where:
αp = Alpha (unexplained return)
β = Factor loading (exposure)
R = Factor return
```

**Example Attribution**:
```
Portfolio Return: 12%

Factor Attribution:
Market exposure: +8% (0.8 beta × 10% market return)
Value factor: +2% (overweight value by 10%, factor return 20%)
Momentum factor: +1% (overweight momentum by 5%, factor return 20%)
Alpha (unexplained): +1%

Total: +12%
```

## Style Analysis

### Equity Style Box

**Dimensions**:
- **Market Cap**: Large, mid, small
- **Style**: Value, blend, growth

**9-Box Grid**:
```
              Large      Mid      Small
Value       □           □         □
Blend       □           □         □
Growth      □           □         □
```

**Analysis**:
- Identify style drift
- Compare to benchmark
- Monitor unintended exposures
- Assess diversification

### Fixed Income Attribution

**Key Dimensions**:
- **Duration**: Average maturity
- **Credit Quality**: Investment-grade vs high-yield
- **Sectors**: Treasuries, corporates, municipals
- **Geographic**: Domestic vs international

**Attribution Sources**:
- Duration effect: Changes in interest rates
- Credit effect: Changes in credit spreads
- Sector allocation: Over/underweight sectors
- Selection effect: Individual bond performance

## Benchmark Selection and Comparison

### Appropriate Benchmark Criteria

**1. Investability**:
- Can actually invest in benchmark holdings
- Represents investable universe
- Not theoretical or custom-created

**2. Representativeness**:
- Reflects portfolio strategy and constraints
- Similar asset classes and style
- Geographic and sector representation

**3. Measurability**:
- Returns easily calculated
- Objective and transparent methodology
- Public data available

**4. Appropriateness**:
- Similar risk profile to portfolio
- Same investment objectives
- Comparable time horizon

### Common Benchmarks

**US Equities**:
- S&P 500: Large-cap growth-biased
- Russell 2000: Small-cap
- Total Market: All US stocks

**Fixed Income**:
- Bloomberg Aggregate Bond Index: Overall bond market
- Barclays US Aggregate: Investment-grade bonds
- High Yield Index: Below-investment-grade bonds

**International**:
- MSCI EAFE: Developed international
- MSCI Emerging Markets: Developing countries

**Multi-Asset**:
- 60/40 Index: 60% stocks, 40% bonds
- Custom Blended: Client-specific blend

## Excess Return Analysis

### Decomposition

**Excess Return Sources**:
```
Total Excess Return = Allocation Effect + Selection Effect + Fees Effect

Where:
Fees Effect = Negative (management fees reduce returns)
Selection Effect = Security selection skill
Allocation Effect = Tactical allocation decisions
```

### Persistence Analysis

**Question**: Do good past returns persist?

**Methodology**:
- Rank managers by performance
- Track top/bottom quartile in future periods
- Measure persistence coefficient

**Findings**:
- Passive management shows no persistence (expected)
- Active management shows limited persistence
- After fees, most underperform benchmarks
- Short-term persistence may exist but reverse

## Performance Reporting

### Client Dashboard Metrics

**Key Measures**:
1. **Total Return**: Period-to-date and year-to-date
2. **vs Benchmark**: Return comparison and excess return
3. **Volatility**: Standard deviation and downside deviation
4. **Risk Metrics**: Sharpe ratio, Sortino ratio, max drawdown
5. **Attribution**: Allocation and selection effects

**Visual Presentation**:
```
Year-to-Date Performance: +6.5%
Benchmark Return: +6.0%
Excess Return: +0.5%

Annualized Return (3-year): 8.2%
Benchmark Return: 7.8%
Annualized Volatility: 10.3%
Sharpe Ratio: 0.68

Performance Attribution:
- Allocation Effect: +0.30%
- Selection Effect: +0.20%
- Total Excess Return: +0.50%
```

### Peer Comparison

**Metrics**:
- Return percentile vs peers
- Risk percentile vs peers
- Sharpe ratio ranking
- Consistency of performance

**Interpretation**:
- Top quartile: Outperforming most peers
- Median: Average performance
- Bottom quartile: Underperforming most peers

## Performance Analysis Limitations

1. **Survivorship Bias**: Closed funds excluded from analysis
2. **Backfill Bias**: New funds report only successful track records
3. **Selection Bias**: Manager selection affects returns
4. **Timing Effects**: Lucky vs skillful performance hard to distinguish
5. **Cost Omission**: Pre-fee vs after-fee returns
6. **Short Measurement Periods**: Noise dominates signal
7. **Benchmark Mismatch**: Inappropriate benchmarks mislead

## Practical Implementation

### Technology Requirements
- Return and position tracking systems
- Factor data integration
- Attribution calculation engines
- Reporting dashboards
- Compliance and audit trails

### Frequency and Reporting
- Daily: Position-level tracking
- Weekly: Performance summaries
- Monthly: Detailed attribution analysis
- Quarterly: Comprehensive performance review
- Annual: Detailed reporting and strategy review

### Advisor Interpretation

**Key Points to Communicate**:
- Excess return comes from decisions (allocation + selection)
- Fees reduce returns (hidden drag)
- Benchmarks should match strategy
- Short-term returns are noisy
- Focus on long-term, risk-adjusted performance
- Consistency matters more than single periods
