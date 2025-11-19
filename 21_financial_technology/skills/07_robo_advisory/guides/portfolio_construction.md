# Portfolio Construction Guide for Robo-Advisors

## Portfolio Construction Framework

Portfolio construction is the process of selecting specific investments and allocating capital to create a portfolio aligned with client objectives, risk tolerance, and constraints.

## Step 1: Asset Class Selection

### Equity Allocation

**US Equity Components**:
1. **Large-Cap Core** (40-45% of equities)
   - Index: S&P 500
   - Funds: VOO (Vanguard), IVV (iShares)
   - Rationale: Stable, diversified, liquid

2. **International Developed** (20-25% of equities)
   - Index: MSCI EAFE
   - Funds: VEA (Vanguard), IEFA (iShares)
   - Rationale: Geographic diversification, valuations

3. **Emerging Markets** (10-15% of equities)
   - Index: MSCI Emerging Markets
   - Funds: VWO (Vanguard), IEMG (iShares)
   - Rationale: Growth potential, emerging economies

4. **Small-Cap** (5-10% of equities)
   - Index: Russell 2000
   - Funds: VB (Vanguard), IJR (iShares)
   - Rationale: Growth and diversification

**Total Equity Allocation Examples**:
- Conservative Portfolio: 30% equities
- Moderate Portfolio: 60% equities
- Aggressive Portfolio: 85% equities

### Fixed Income Allocation

**US Fixed Income Components**:
1. **Core Bond Fund** (50-60% of bonds)
   - Index: Bloomberg Aggregate Bond Index
   - Funds: BND (Vanguard), AGG (iShares)
   - Rationale: Broad exposure, intermediate duration

2. **Short-Term Bonds** (20-30% of bonds)
   - Index: Bloomberg US 1-3 Year Bond Index
   - Funds: SHV (Vanguard), SHY (iShares)
   - Rationale: Lower interest rate risk

3. **TIPS** (10-20% of bonds)
   - Index: FTSE US Treasury Inflation-Linked Bond Index
   - Funds: VTIP (Vanguard), SCHP (Schwab)
   - Rationale: Inflation protection

4. **Alternative Bonds** (0-15% of bonds)
   - Options: High-yield bonds, municipal bonds, international bonds
   - Rationale: Enhanced yield, diversification

**Total Fixed Income Examples**:
- Conservative Portfolio: 60% fixed income
- Moderate Portfolio: 35% fixed income
- Aggressive Portfolio: 12% fixed income

### Alternative Investments

**Real Estate**:
- REIT allocation: 5% (conservative), 10% (moderate), 5% (aggressive)
- Fund: VNQ (Vanguard), SCHH (Schwab)
- Rationale: Inflation hedge, income, diversification

**Commodities** (Optional):
- Allocation: 2-5% for diversification
- Fund: GSG (commodities basket), GLD (gold)
- Rationale: Inflation protection, crisis hedge

**Private Alternatives** (For high-net-worth):
- Private Equity: 5-15% for HNW
- Hedge Funds: 5-10% for HNW
- Rationale: Absolute returns, diversification

### Cash Position

**Typical Allocations**:
- Conservative: 3-5%
- Moderate: 2-3%
- Aggressive: 1-2%

**Rationale**:
- Liquidity buffer
- Upcoming distributions
- Rebalancing source
- Client psychology

## Step 2: Security Selection

### Selection Criteria

**1. Cost/Efficiency Metrics**
```
Ranking Priority:
1. Expense Ratio (primary)
2. Bid-Ask Spread (trading costs)
3. Tracking Error (for index funds)
4. Turnover (tax implications)
```

**2. Quality Assessment**
- Provider reputation (Vanguard, Schwab, iShares)
- Fund size and history (>5 years preferred)
- AUM ($100M+ preferred)
- Stability and viability

**3. Characteristics**
- Holdings concentration
- Geographic diversification
- Sector allocation
- Holdings quality

### Security Selection Process

**Step 1: Category Definition**
```
Need: US Large-Cap Index Exposure
Requirements:
- Low cost (<0.10% ER)
- High liquidity (>1M shares/day volume)
- Minimum $500M AUM
- Broad-based index
```

**Step 2: Candidate Screening**
```
Candidates:
- SPY (SPDR S&P 500) - 0.09%, Highest volume, $400B+
- VOO (Vanguard S&P 500) - 0.03%, $300B+
- IVV (iShares Core S&P 500) - 0.03%, $250B+
- RSP (Invesco S&P 500 Equal Weight) - 0.20%, Different weighting

Preferred: VOO (lowest cost, institutional quality)
```

**Step 3: Fund Analysis**
- Holdings overlap assessment
- Tax efficiency comparison
- Dividend treatment
- Historical performance vs benchmark

**Step 4: Implementation**
- Select specific securities
- Document selection rationale
- Set rebalancing parameters

## Step 3: Allocation Modeling

### Model Portfolio Examples

**Conservative Portfolio (Risk Score: 1-3)**

Allocation:
```
US Equities (25%):
- 15% Large-Cap (VOO)
- 7% International (VEA)
- 3% Emerging Markets (VWO)

Fixed Income (70%):
- 40% Core Bonds (BND)
- 20% Short-Term Bonds (SHV)
- 10% TIPS (VTIP)

Alternatives (5%):
- 5% REITs (VNQ)

Cash (5%)
```

**Moderate Portfolio (Risk Score: 4-6)**

Allocation:
```
US Equities (55%):
- 35% Large-Cap (VOO)
- 12% International (VEA)
- 8% Emerging Markets (VWO)

Fixed Income (35%):
- 20% Core Bonds (BND)
- 10% Short-Term Bonds (SHV)
- 5% TIPS (VTIP)

Alternatives (10%):
- 8% REITs (VNQ)
- 2% Commodities (GSG)

Cash (2%)
```

**Aggressive Portfolio (Risk Score: 7-10)**

Allocation:
```
US Equities (75%):
- 45% Large-Cap (VOO)
- 18% International (VEA)
- 12% Emerging Markets (VWO)

Fixed Income (12%):
- 8% Core Bonds (BND)
- 4% TIPS (VTIP)

Alternatives (11%):
- 8% REITs (VNQ)
- 3% Commodities (GSG)

Cash (2%)
```

### Monte Carlo Analysis

**Process**:
1. Define expected returns for each asset class (conservative estimates)
2. Define standard deviations (historical volatility)
3. Define correlations (historical relationships)
4. Run 10,000 simulations of 10-year returns
5. Calculate success rate and return distribution

**Example Output**:
```
Conservative Portfolio - 10-Year Projection:
Expected Return: 4.5% annually
10th Percentile: 2.5% annually
Median: 4.5% annually
90th Percentile: 6.5% annually
Drawdown Risk: Maximum -12% in down year

Success Rate (Goal: $1M→$1.55M): 95%
Interpretation: Very likely to achieve goal
```

## Step 4: Risk Management

### Portfolio Risk Metrics

**Standard Deviation (Volatility)**:
```
Conservative Portfolio: 4-6%
Moderate Portfolio: 10-12%
Aggressive Portfolio: 16-18%
```

**Sharpe Ratio** (Risk-Adjusted Return):
```
Conservative: 0.4-0.6
Moderate: 0.5-0.8
Aggressive: 0.4-0.7
```

**Maximum Drawdown** (Worst historical decline):
```
Conservative: -10% to -15%
Moderate: -20% to -30%
Aggressive: -40% to -50%
```

### Concentration Limits

**By Asset Class**:
- Single asset class: Max 85% (equities in aggressive)
- Single fund: Max 20%

**By Sector** (implicit in funds):
- Tech-heavy sectors: Monitor overlap
- Energy exposure: Varies by market conditions

**By Geography**:
- International minimum: 15% of equities
- US maximum: 85% of equities

### Downside Protection

**Defensive Measures**:
1. **Bond Allocation**: Primary downside protection
2. **Diversification**: Across asset classes and geographies
3. **Rebalancing**: Automatic buy-low mechanism
4. **Volatility Monitoring**: Track and report

## Step 5: Implementation and Execution

### Account Setup

**Initial Investment Strategy**:
```
Account Funding Amount: $100,000
Recommended Execution Timeline:

Day 1:
- Open account
- Complete KYC/AML
- Link bank account
- Submit funding

Day 2-3:
- Verify funding
- Initiate 40% investment
- Place buy orders

Day 4-5:
- Execute trades
- Settlement

Day 6-10:
- Continue with remaining funds
- Complete portfolio construction

Day 15:
- Final settlement
- Portfolio complete
```

**Dollar-Cost Averaging**:
- Benefits: Reduces timing risk for large lump sum
- Timeline: 2-4 weeks typical
- Tradeoff: Small cash drag from staging

### Fractional Share Implementation

**Advantages**:
- Perfect allocation to target percentages
- No cash drag (all funds invested)
- Lower minimum account sizes
- Simplifies rebalancing math

**Example**:
```
$100,000 allocation to 10 holdings:
Conservative Portfolio

VOO (15% = $15,000): Buy exactly 51.724 shares
VEA (7% = $7,000): Buy exactly 20.833 shares
VWO (3% = $3,000): Buy exactly 10.204 shares
BND (40% = $40,000): Buy exactly 400.00 shares
...
Total: $100,000 with no cash drag
```

### Trading Execution

**Trade Optimization**:
1. **Grouping**: Batch trades by asset class
2. **Timing**: Execute during liquid hours (9:30 AM - 3:30 PM ET)
3. **Slippage**: Minimize market impact
4. **Routing**: Best execution across custodians

## Step 6: Ongoing Portfolio Management

### Monitoring Frequency

**Daily**:
- Position tracking
- Risk metrics calculation
- Market monitoring

**Weekly**:
- Performance tracking
- Holdings review
- Allocation monitoring

**Monthly**:
- Performance reporting
- Client communications
- Drift analysis

**Quarterly**:
- Formal rebalancing review
- Performance attribution
- Strategy adjustment evaluation

**Annual**:
- Full portfolio review
- Risk profile reassessment
- Strategy adjustment
- Tax planning

### Allocation Drift Monitoring

**Tracking**:
```
Target Allocation: 60% stocks, 40% bonds
Current Allocation: 65% stocks, 35% bonds
Drift: +5% in stocks, -5% in bonds

Rebalancing Decision:
Drift Threshold: 10%
Actual Drift: 5%
Action: Hold (below threshold)
```

### Adjustment Triggers

**When to Modify Allocations**:
1. **Life Events**: Marriage, children, inheritance, job change
2. **Financial Goals**: Change in goals or timeline
3. **Time Horizon**: Approaching milestone (5 years to retirement)
4. **Risk Tolerance**: Investor discomfort with volatility
5. **Market Extremes**: Significant market movements

## Step 7: Tax Optimization

### Tax-Aware Construction

**Placement Strategy**:
```
Tax-Advantaged Accounts:
- High-dividend stocks
- High-yield bonds
- REITs (tax-inefficient)
- Actively-managed funds

Taxable Accounts:
- Low-turnover index funds
- Municipal bonds
- Growth stocks (long-term gains)
- International stocks
```

### Tax-Loss Harvesting Integration

**Identification**:
- Run daily/weekly harvesting scan
- Identify all loss positions
- Calculate tax benefits
- Track wash-sale windows

**Implementation**:
- Sell security at loss
- Buy similar (but not identical) security
- Track 31-day windows
- Utilize losses for tax reduction

## Documentation and Compliance

### Investment Policy Statement (IPS)

Key Sections:
```
1. Client Profile:
   - Risk tolerance
   - Time horizon
   - Financial situation
   - Constraints and restrictions

2. Investment Objectives:
   - Total return target
   - Income requirement
   - Capital appreciation goal

3. Asset Allocation:
   - Target allocation
   - Acceptable ranges (bands)
   - Rebalancing policy

4. Benchmark Selection:
   - Appropriate benchmarks
   - Performance measurement
   - Attribution analysis

5. Rebalancing Policy:
   - Frequency
   - Methods
   - Triggers

6. Risk Management:
   - Risk tolerance limits
   - Diversification requirements
   - Constraints and restrictions

7. Fees and Costs:
   - Fee schedule
   - Cost disclosure
   - Tax efficiency considerations
```

## Common Portfolio Construction Mistakes

1. **Over-Concentration**: Too few securities or asset classes
2. **Under-Diversification**: Avoiding international or small-cap
3. **Overly Complex**: Too many holdings or strategies
4. **Cost Ignorance**: Ignoring fees and expense ratios
5. **Benchmark Mismatch**: Inappropriate performance benchmarks
6. **Insufficient Rebalancing**: Allowing significant drift
7. **Tax Inefficiency**: Not considering tax implications
8. **Poor Documentation**: Insufficient IPS and policy records
9. **Inflexibility**: Not adjusting for life changes
10. **Neglecting Risk**: Insufficient focus on downside protection

## Conclusion

Effective portfolio construction requires balancing asset allocation theory, practical implementation constraints, tax efficiency, and ongoing monitoring. A well-constructed portfolio aligned with client objectives and properly managed should provide competitive returns with appropriate risk management.
