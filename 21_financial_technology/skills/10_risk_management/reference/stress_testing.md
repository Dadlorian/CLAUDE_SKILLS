# Stress Testing Framework

## Overview
Stress testing is a risk management technique to understand portfolio behavior under extreme scenarios. Unlike VaR which shows normal-time risk, stress testing shows what happens when markets break down.

## Stress Testing Types

### 1. Historical Scenarios
Use actual past crisis events as templates.

**Major Events**:
- **2008 Financial Crisis**: Credit spreads widen 500+ bps, equities fall 50%, volatility spikes
- **1987 Black Monday**: Equities fall 22% in single day
- **2011 European Debt Crisis**: Sovereigns fail, peripheral rates spike
- **2020 COVID Shock**: Equity decline, volatility spike, credit spread widening
- **Russian Default (1998)**: Emerging market contagion
- **Asian Flu (1997)**: Regional spread to emerging markets

**Characteristics**:
- Based on actual data
- Realistic correlation changes
- Includes market panic dynamics
- Widely used for regulatory stress tests

**Example - 2008 Scenario**:
```
Changes:
- US Equities: -48%
- European Equities: -52%
- US Credit (IG): +300 bps
- US Credit (HY): +600 bps
- Emerging Markets: -60%
- Volatility Index: 88 (vs. normal 20)
- VIX: 82 (vs. normal 18)

Apply to current portfolio:
- 20% US Equity allocation: -9.6%
- 10% EM allocation: -6%
- 30% Credit allocation: ~0% (spread widening offsets carry)
- 40% Bonds: +5% (flight to safety)
Portfolio overall: -8.5%

Current portfolio value: $100M
Estimated loss in 2008 scenario: $8.5M
```

### 2. Hypothetical Scenarios
Construct plausible but non-historical scenarios.

**Advantages**:
- Explore tail risks not in historical data
- Test specific risks
- Can be more severe than historical
- Tailored to current portfolio

**Examples**:
- Parallel yield curve shift: All yields up/down by 100 bps
- Equity market crash: 20%, 30%, 50% decline
- Credit spread widening: 100, 200, 500 bps
- Volatility spike: VIX 40, 50, 60+
- Currency devaluation: 10%, 20%, 50% depreciation
- Commodity shock: 30% price spike/decline
- Liquidity crisis: Bid-ask spreads widen 10x, volumes 1/10th

**Example - Interest Rate Shock**:
```
Scenario: Parallel upward shift of 200 bps
- All yields increase by 200 basis points
- 2-year yield: 1% → 3%
- 5-year yield: 1.5% → 3.5%
- 10-year yield: 2% → 4%
- 30-year yield: 2.5% → 4.5%

Portfolio: $500M in bonds
- Duration: 5 years
- DV01: $25,000 (per 1 bp)
- Loss from 200 bp: $25,000 × 200 = $5M

Interpretation: 200 bps adverse move losses $5M
```

### 3. Reverse Stress Testing
Identify what market moves would cause unacceptable losses.

**Process**:
1. Define unacceptable loss (e.g., 10% of capital)
2. Work backward to find market scenarios
3. Assess likelihood of scenarios
4. Evaluate mitigation strategies

**Example**:
```
Maximum acceptable loss: $10M (10% of $100M capital)
Portfolio: 50% equities, 50% bonds
Question: What % equity decline triggers $10M loss?

Sensitivity: 1% equity decline = $500k loss
To get $10M loss: 20% equity decline

Likelihood assessment:
- 20% decline: Happens every 10-15 years historically
- Acceptable? Risk managers and board must assess

Decision: Either accept the risk or hedge
```

## Regulatory Stress Testing

### CCAR/DFAST (US)
**Supervisory Stress Test for Large Banks**

**Timeline**:
- November: Fed releases scenarios
- December-January: Banks run internal stress tests
- February: Banks submit results
- March: Fed publishes results
- May: Banks announce capital distributions (dividends, buybacks)

**Scenarios**:
1. **Baseline**: Fed forecasts for coming year
2. **Adverse**: Moderate recession
3. **Severe Adverse**: Deep recession, financial crisis

**Example Severe Adverse Scenario**:
```
Unemployment: 6% → 8.5%
Real GDP: +2% → -4%
Stock Market: 0% → -55%
House Prices: +0% → -20%
10-year Yield: 2.5% → 0.5%
3-month Yield: 1.5% → 0.2%
VIX: 18 → 40
CDS Spreads: BBB 100 bps → 300 bps
```

**Regulatory Capital Requirement**:
After applying stress scenario to portfolio:
- Banks must maintain CET1 ratio ≥ 4.5%
- If projected CET1 falls below 4.5%, capital actions denied (no dividends, no buybacks)

### EBA Stress Test (EU)
Similar approach to US but for European banks.

**Scenarios**: Baseline, Adverse, Severe Adverse

**Sample Results** (2021 EBA Stress Test):
```
Bank X
- Capital ratio without stress: 15%
- Capital ratio in adverse scenario: 12%
- Capital ratio in severe scenario: 9.5%
- Result: Passes (above 6% minimum for severe)
```

### Bank of England Stress Test (UK)
For UK-regulated banks.

**Focus Areas**:
- Interest rate risk
- Credit risk
- Market risk
- Liquidity risk

## Stress Testing Methodology

### Sensitivity Analysis
Vary one risk factor, holding others constant.

```
Scenario: US Equity Market Shock

Market moves:
- US Equities: -10%, -20%, -30%, -40%, -50%
- Other factors: Unchanged

Portfolio Impact:
                US Equities  Estimated P&L   % of Capital
Base (0%)       $50M        $0              0%
-10%            $45M        -$5M            -5%
-20%            $40M        -$10M           -10%
-30%            $35M        -$15M           -15%
-40%            $30M        -$20M           -20%
-50%            $25M        -$25M           -25%

Risk assessment: Portfolio can withstand up to ~25% equity decline before exceeding risk appetite
```

### Scenario Analysis
Multiple risk factors move simultaneously.

```
Scenario: Credit Crisis

Market moves:
- US Equities: -30%
- Investment Grade Credit Spreads: +250 bps
- High Yield Spreads: +600 bps
- Emerging Markets: -40%
- Volatility: +30 points
- USD: +5% (safe haven)

Portfolio: 20% US Equity, 15% EM, 40% Bonds (mix IG/HY), 25% Cash/Stable

P&L Impact:
- US Equities: 20% × -30% = -6%
- EM: 15% × -40% = -6%
- Bonds: 40% × (+1% capital appreciation from flight-to-safety, -2% from spread widening) = -0.4%
- Cash: 25% × 0% = 0%
Portfolio Loss: -6% - 6% - 0.4% = -12.4%

On $100M: -$12.4M (12.4% of capital)
```

### Correlation Breakdown
Model assumptions that correlations change in stress.

```
Normal Correlation Matrix:
         Equities  Bonds  Credit  Commodities
Equities    1.0    -0.3    0.5       0.3
Bonds      -0.3     1.0   -0.2      -0.2
Credit      0.5    -0.2    1.0       0.3
Commodities 0.3    -0.2    0.3       1.0

Stress Correlation Matrix (2008 Crisis):
         Equities  Bonds  Credit  Commodities
Equities    1.0    -0.1    0.8       0.7
Bonds      -0.1     1.0    0.4       0.1
Credit      0.8     0.4    1.0       0.6
Commodities 0.7     0.1    0.6       1.0

Key changes:
- Equity-Bond correlation: -0.3 → -0.1 (diversification fails)
- Equity-Credit correlation: 0.5 → 0.8 (credit follows equities)
- Everything correlates positive (risk-on/off behavior)
```

## Liquidity in Stress Testing

### Bid-Ask Spread Widening
```
Normal Bid-Ask Spreads:
- Large-cap equities: 1-2 bps
- Government bonds: 1-2 bps
- Corporate bonds: 5-10 bps
- High-yield bonds: 20-50 bps

Stress Bid-Ask Spreads (2008 Crisis):
- Large-cap equities: 5-20 bps
- Government bonds: 5-10 bps
- Corporate bonds: 50-200 bps
- High-yield bonds: 200-500 bps

Impact on liquidation:
Position: $10M corporate bonds
Normal execution cost: $10M × 0.075% = $7,500
Stress execution cost: $10M × 1.25% = $125,000
Additional cost: $117,500
```

### Volume Constraints
```
Normal Daily Volume: $1B in municipal bonds
Stress Daily Volume: $100M (10x reduction)

Position to Liquidate: $500M municipal bonds
Normal Timeline: 1 week at $1B/day
Stress Timeline: 50 days at $100M/day

If needed in 1 week:
- Must sell at discount (market impact)
- Price concession: 2-5% loss
- Loss: $500M × 3% = $15M
```

## Stress Testing Governance

### Frequency & Timing
- **Annual**: Major regulatory stress tests (CCAR, EBA)
- **Quarterly**: Internal stress tests across all businesses
- **Ad-hoc**: In response to market events (election, geopolitical)

### Documentation
- Clear scenario definitions
- Methodology fully documented
- Assumptions listed and justified
- Results tracked over time
- Limitations acknowledged

### Escalation & Decision-Making
- Results reviewed by risk committee
- Escalated if losses exceed thresholds
- Board informed of major findings
- Strategic decisions made based on results

## Stress Testing vs. VaR

| Aspect | VaR | Stress Testing |
|--------|-----|-----------------|
| **Confidence Level** | 95-99% | Tail (1-2%) or worse |
| **Time Horizon** | 1-10 days | 1 day to 1 year |
| **Methodology** | Probabilistic | Deterministic |
| **Assumptions** | Distribution shape | Scenario definitions |
| **Purpose** | Routine risk monitoring | Understanding tail risk |
| **Frequency** | Daily | Quarterly/Annual |
| **Regulatory Use** | Capital requirements | Stress test capital |

**Key Insight**: VaR and stress testing are complementary.
- VaR: What's normal-time risk?
- Stress Test: What happens if things go wrong?
