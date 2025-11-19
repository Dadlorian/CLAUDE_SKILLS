# Stress Testing Implementation Guide

## Step 1: Define Scenarios

**Historical Scenario - 2008 Financial Crisis**:
```
Market Movements:
- US Equities: -48%
- Credit Spreads: IG +300 bps, HY +600 bps
- VIX: 88
- Emerging Markets: -60%
- USD: +5%

Apply to current portfolio ($100M):
- 20% equities ($20M): Loss = 20M × -48% = -$9.6M
- 40% fixed income ($40M):
  * Government bonds (20M): Slight gain from flight-to-safety = +$0.5M
  * Corporate bonds (15M): Spread widening = -$0.75M (0.5% price decline)
  * High yield (5M): Large spread widening = -$1.25M (2.5% decline)
  Total fixed income: -$1.5M
- 30% cash (30M): No change = $0
- 10% alternatives (10M): Estimated -30% = -$3M

Total stressed loss: -$9.6M - $1.5M - $3M = -$14.1M (14.1% of portfolio)
```

**Hypothetical Scenario - Interest Rate Shock**:
```
Scenario: Fed raises rates 200 bps (parallel shift)

Duration adjusted losses:
- Portfolio duration: 5 years
- DV01 (value of 1 bp): $5,000
- 200 bp move: 200 × $5,000 = -$1,000,000

More detailed:
- 10-year bonds (duration 8): -$1.6M (2% price decline)
- 5-year bonds (duration 4.5): -$0.9M (1.8% price decline)
- 2-year bonds (duration 1.8): -$0.36M (1.8% decline)

Total loss: -$2.86M (2.86% of portfolio)
```

**Reverse Scenario - What Breaks the Bank?**
```
Question: What market move would lose 10% of $100M = $10M?

Work backward:
- If equity position loses $10M for a 50% decline
- Current equity: $10M / 0.50 = $20M
- Current portfolio: 20% in equities ✓ (matches)

Finding: 50% equity decline = $10M loss
Historical precedent: 2000 tech crash (-50%), 2008 (-48%)
Likelihood: Severe but possible every 10-15 years

Action: Acceptable? Board and risk committee assess
```

## Step 2: Quantify Impact

**Method 1: Sensitivity Tables**:
```
Equity Market Shock Scenario:

Equity Move    Portfolio Loss    % of Capital    Likelihood
-10%          -$2.0M            -2%             1x per year
-20%          -$4.0M            -4%             1x per 5 years
-30%          -$6.0M            -6%             1x per 10 years
-40%          -$8.0M            -8%             1x per 20 years
-50%          -$10.0M           -10%            1x per 50 years

Use cases:
- Board risk appetite: Acceptable loss is $5M (5% loss)
- This corresponds to ~30% equity market decline
- Historical precedent: 2008 was -48%
- Keep stress reserve of 10% capital ($10M) to absorb
```

**Method 2: Correlation Changes**:
```
Normal environment correlations:
Equities-Bonds: -0.3 (diversification benefit)
Bond-Credit: -0.2
Stock-Commodity: +0.3

Stress correlations (crisis):
Equities-Bonds: +0.1 (diversification fails!)
Bond-Credit: +0.5 (credit moves with equities)
Stock-Commodity: +0.8 (everything down together)

Impact:
- Normal portfolio loss: $5M (diversification helps)
- Stress portfolio loss: $9M (diversification fails)
- Additional loss from correlation breakdown: $4M
```

## Step 3: Risk Aggregation

**Combine multiple scenarios**:
```
Scenario Analysis: "Multiple Shocks"

Shock 1: Credit Crisis
- Credit spreads +300 bps
- Equity -30%
- Volatility spike
- Liquidity dries up

Shock 2: Funding Crisis
- Deposit withdrawals: -$2B
- Wholesale funding: -50% available
- Repo margins increase: +5%

Shock 3: Interest Rate Shock
- Rates +150 bps (growth concerns fade)
- Volatility continues high
- Risk premium widens

Combined impact:
- Mark-to-market losses: -$15M
- Funding gap: -$2.5B → forced selling
- Collateral haircuts increase → additional margin: -$500M
- Total impact: -$16M + forced $2.5B sale potential

Action needed: Raise capital, sell non-core business, cut costs
```

## Step 4: Historical Scenario Testing

**Recreate 2008 Crisis using current portfolio**:
```
Step 1: Document 2008 movements
- Equities: -48%
- Credit IG: +300 bps
- Credit HY: +600 bps
- Mortgages: -40% in value
- CDS: 500-1000 bps widening
- Volatility: 80 (vs. normal 20)

Step 2: Apply to current portfolio
Current holdings:
- US Equity index funds: $20M
- Corporate bonds (IG): $30M
- High-yield bonds: $15M
- Residential mortgages: $25M
- Cash/Treasuries: $10M

Step 3: Calculate loss for each
- Equities: 20M × -48% = -$9.6M
- IG bonds: 30M × (loss from 300 bps + declining values) ≈ -$1.5M
- HY bonds: 15M × (loss from 600 bps) ≈ -$3M
- Mortgages: 25M × -40% = -$10M (defaults, price collapse)
- Cash: No loss

Total: -$24.1M (24.1% of capital)

Key insights:
- Mortgages largest loss due to collateral collapse
- Credit bonds significant because of spread widening
- 2008 was severe, current diversification helps somewhat
- But still $24M loss is significant
```

## Step 5: Reporting & Governance

**Board Reporting Format**:
```
STRESS TEST RESULTS - CONFIDENTIAL

Scenarios Tested: 5 (Historical, Hypothetical, Reverse)

Key Findings:

1. Base Case (Current position):
   Portfolio value: $100M
   Capital: $10M (10%)

2. Stress Scenario: 2008 Crisis (Probability: 1-2% annually)
   Estimated loss: $24.1M
   Remaining capital: $-14.1M (SHORTFALL)
   Maximum loss tolerance: $10M
   Excess loss: $14.1M

   VERDICT: Current position NOT resilient to 2008-type crisis

3. Moderate Scenario: Mild Recession
   Estimated loss: $8M
   Remaining capital: $2M (adequate)
   VERDICT: Acceptable

4. Reverse Stress Test:
   Maximum acceptable loss: $5M
   Implies: Can withstand ~25% equity decline
   But cannot withstand: 2008-type event

   ACTION REQUIRED: Reduce equity exposure by 50%

Recommendations:
1. Reduce equity from 20% to 10% of portfolio
2. Reduce mortgage exposure (swap for safer collateral)
3. Hedge credit risk using CDS
4. Increase capital buffer to 15%
5. Develop contingency funding plan

Timeline: Implement within 90 days
Board approval: Required before implementation
```

## Step 6: Regular Monitoring

**Monthly Stress Test Execution**:
```
Inputs (update monthly):
- Current portfolio positions
- Current market prices/volatility
- Current credit spreads
- Current correlations

Calculation:
- Run 5 standard scenarios
- Calculate loss for each
- Compare to capital buffer
- Calculate stress VaR (maximum loss)

Reporting:
- If maximum loss < $3M: Green (acceptable)
- If loss $3M-$5M: Yellow (watch)
- If loss > $5M: Red (action required)

Current month:
- Scenario 1 loss: $2.1M ✓ Green
- Scenario 2 loss: $4.8M ⚠ Yellow (close to limit)
- Scenario 3 loss: $8.2M ✗ Red

Action: Reduce positions to get all scenarios green
```

## Step 7: Model Validation

**Backtesting stress scenarios**:
```
Test: Did stress scenarios predict actual crises?

Historical test:
- 2008: Predicted loss = $24M, Actual = $25M ✓ Close
- 2020 COVID: Predicted loss = $12M, Actual = $11M ✓ Close
- 2011 European crisis: Predicted loss = $8M, Actual = $9.5M ✓ Close

Conclusion: Model well-calibrated
Can rely on estimates with confidence

Sensitivity test:
- If spreads 50% less severe than assumed: Loss decreases 20%
- If correlations less broken: Loss decreases 10%
- If recovery faster: Loss decreases 15%

Conservative: Use base case estimates
Aggressive: Use recovery adjusted estimates
