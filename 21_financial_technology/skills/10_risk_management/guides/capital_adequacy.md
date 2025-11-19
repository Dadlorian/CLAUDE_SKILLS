# Capital Adequacy Calculation Guide

## Step 1: Calculate Risk-Weighted Assets (RWA)

**Standardized Approach (Most banks)**:

```
Step 1: Classify assets by type
Asset Type                Amount      Risk Weight
Cash                      $100M       0%
Government securities     $200M       20%
AAA corporate bonds       $150M       20%
BBB corporate loans       $300M       100%
Mortgages (LTV<80%)      $250M       35%
Mortgages (LTV 80-90%)   $150M       50%
Equities held             $100M       100%
Off-balance commitments  $500M × CCF  0-50%
Derivatives exposure      $50M        varies

Step 2: Calculate RWA
RWA = Σ (Asset Amount × Risk Weight)

Calculation:
- Cash: $100M × 0% = $0M
- Govt bonds: $200M × 20% = $40M
- AAA bonds: $150M × 20% = $30M
- BBB loans: $300M × 100% = $300M
- Mortgages 1: $250M × 35% = $87.5M
- Mortgages 2: $150M × 50% = $75M
- Equities: $100M × 100% = $100M
- Commitments: $500M × 25% CCF × 40% RW = $50M
- Derivatives: $50M × 100% = $50M

Total RWA: $732.5M
```

## Step 2: Calculate Capital Components

**Capital Structure**:

```
Tier 1 Capital (Core capital):
+ Common Equity Tier 1 (CET1):
  - Issued share capital      $200M
  - Retained earnings         $150M
  - Common stock              $0M
  Subtotal CET1:             $350M

+ Additional Tier 1:
  - Hybrid bonds (perpetual)  $50M
  Total Tier 1:              $400M

Tier 2 Capital (Supplementary):
+ Subordinated debt          $150M
+ Loan loss reserves (capped) $50M
Total Tier 2:               $200M

Total Capital:              $600M
```

## Step 3: Calculate Capital Ratios

**Basel III Requirements**:

```
CET1 Ratio = CET1 / RWA
           = $350M / $732.5M
           = 47.8%  ← EXCEEDS 4.5% minimum ✓

Tier 1 Ratio = Tier 1 Capital / RWA
             = $400M / $732.5M
             = 54.6%  ← EXCEEDS 6% minimum ✓

Total Capital Ratio = Total Capital / RWA
                    = $600M / $732.5M
                    = 81.9%  ← EXCEEDS 8% minimum ✓

Leverage Ratio = Tier 1 Capital / Total Assets
               = $400M / $2,000M
               = 20%  ← EXCEEDS 3% minimum ✓

All ratios exceed regulatory minimums ✓
Bank has comfortable capital cushion
```

## Step 4: Apply Capital Buffers

**Basel III Buffer Structure**:

```
Minimum Capital Requirement:
- CET1: 4.5%
- Tier 1: 6.0%
- Total: 8.0%

Capital Buffers:
+ Capital Conservation Buffer: 2.5%
+ Countercyclical Buffer: 0-2.5% (regulator set)
+ G-SIB Buffer: 1-3.5% (if systemically important)
Total Buffers: 3.5% - 8.5%

Example for large bank:
Required Minimum CET1: 4.5% + 2.5% (conservation) = 7.0%
If G-SIB add-on: 7.0% + 2.5% (G-SIB) = 9.5%

Actual CET1: 47.8%  ← Far exceeds 9.5% requirement ✓

Consequence if CET1 falls below buffers:
- CET1 7-9.5%: Dividend restrictions, limited buybacks
- CET1 < 7%: Significant restrictions, regulatory intervention
```

## Step 5: Stress Test Capital Adequacy

**CCAR/DFAST Severe Adverse Scenario**:

```
Baseline Capital:
- CET1 Ratio: 47.8%
- Tier 1 Ratio: 54.6%
- Total Ratio: 81.9%

Apply stress scenario (2008-type):
- Unemployment: 6% → 8.5%
- GDP growth: +2% → -4%
- Equities: -55%
- House prices: -20%
- Credit spreads: +300 bps (IG), +600 bps (HY)

Stressed credit losses (increase PD, LGD):
- Mortgages: Additional $50M provisions
- Commercial loans: Additional $75M provisions
- Credit cards: Additional $25M provisions
Total provisions needed: $150M
Reduces retained earnings/CET1

Stressed market losses:
- Equity holdings: -55% = -$55M
- Bond portfolio: -$30M (from spread widening, rates up)
Total market losses: $85M
Reduces equity value

Stressed capital reduction:
- Credit losses: $150M
- Market losses: $85M
- Tax/other impacts: $35M
Total capital reduction: $270M

Stressed CET1:
= ($350M - $270M) / $732.5M × 1.10 (higher RWA in stress)
= $80M / $806M
= 9.9%  ← Still above 7% minimum ✓

Bank survives stress with 2.9% buffer over minimum
Acceptable for CCAR (must be > 5.125% minimum)
```

## Step 6: Monitor Capital Trends

**Monthly Capital Monitoring**:

```
Dashboard - Capital Tracking:

Date        CET1        Tier 1      Total       Status
2024-01-31  12.5%       14.0%       16.5%       ✓ Strong
2024-02-28  12.3%       13.9%       16.3%       ✓ Strong
2024-03-31  12.1%       13.7%       16.1%       ✓ Strong

Movements:
- Earnings increase capital: +0.2% per month
- Dividend paid: -0.1% per month
- Net increase: +0.1% per month
- Loan growth increases RWA: -0.1% per month

Net: Stable at 12-12.5%

Factors affecting capital:
1. Earnings generation: +capital
2. Dividend/buybacks: -capital
3. Asset growth: -capital (increases RWA faster than capital if not profitable)
4. Credit losses: -capital
5. Market losses: -capital (if securities decline)
6. Risk weight changes: Affects RWA

Management actions if capital declining:
1. Reduce dividends (less payout)
2. Cut buybacks
3. Grow equity capital (if market conditions allow)
4. Reduce risk-weighted assets (sell businesses, reduce lending)
5. Increase profitability (reduce costs, increase fees)
```

## Step 7: Internal Capital Adequacy Process (ICAAP)

**Annual ICAAP Submission to Regulators**:

```
Bank submits:
1. Current capital adequacy assessment
2. ICAAP methodology
3. Stress test results
4. Capital plan (3-year projection)
5. Recovery & resolution plans

Example 3-year capital plan:
Year 1 (2024):
- Starting CET1: 12.5%
- Earnings projection: +0.5%
- Dividend/buyback: -0.2%
- Loan growth: -0.3% (RWA increase)
- Target: 12.5%

Year 2 (2025):
- Earnings: +0.5%
- Dividend/buyback: -0.3%
- Loan growth: -0.4%
- Target: 12.3%

Year 3 (2026):
- Earnings: +0.5%
- Dividend/buyback: -0.3%
- Loan growth: -0.4%
- Target: 12.1%

Regulatory review:
- Are capital targets adequate?
- Are stress scenarios realistic?
- Is capital plan achievable?
- Any concerns with approach?

Regulator decision:
✓ Approved (capital plan acceptable)
⚠ Approved with concerns (provide more details)
✗ Not approved (need higher capital targets)

Banks with regulator concerns must:
- Increase capital targets
- Reduce dividends/buybacks
- Prove capital adequacy at higher levels
- Potential enforcement action
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Not accounting for off-balance sheet | Include loan commitments with CCF |
| Wrong risk weight | Use correct Basel classification |
| RWA increases faster than capital | Monitor asset growth vs. profitability |
| Failing stress test | Build capital buffer above minimum |
| Not monitoring monthly | Establish capital dashboard |
| Not stress testing | Required by regulators (CCAR/DFAST) |
