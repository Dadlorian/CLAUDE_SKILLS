# Risk Metrics & KRIs

## Overview
Risk metrics quantify the risk profile of an institution, portfolio, or position. Key Risk Indicators (KRIs) are forward-looking metrics that warn of elevated risk levels.

## Key Risk Metrics

### Concentration Metrics

#### 1. Concentration Ratio
**Definition**: Sum of exposures to top N counterparties as percentage of total exposure.

```
CR(N) = (Sum of top N exposures) / Total exposures × 100%

Example:
Total credit exposure: $1,000M
Top 10 exposures: $300M
CR(10) = 30% of portfolio concentrated in top 10

Typical limits:
CR(1) < 5% (largest single exposure)
CR(10) < 25% (top 10 exposures)
CR(100) < 60% (top 100 exposures)
```

#### 2. Herfindahl-Hirschman Index (HHI)
**Definition**: Sum of squared portfolio weights; measures concentration inequality.

```
HHI = Σ (Wᵢ)²

Where:
Wᵢ = Weight of exposure i
Ranges from 0 (perfect diversification) to 1 (single exposure)

Example:
Portfolio of 3 exposures:
- Counterparty A: 50% → weight = 0.5
- Counterparty B: 30% → weight = 0.3
- Counterparty C: 20% → weight = 0.2

HHI = (0.5)² + (0.3)² + (0.2)² = 0.25 + 0.09 + 0.04 = 0.38

Interpretation:
HHI < 0.2: Low concentration
0.2 < HHI < 0.5: Moderate concentration
HHI > 0.5: High concentration
```

#### 3. Portfolio Concentration Index
**Definition**: Ratio of actual concentration to maximum possible concentration.

```
PCI = HHI_actual / HHI_max

Where:
HHI_max = 1 (single counterparty)

For equally-weighted portfolio of N exposures:
HHI_equal = 1/N
PCI_equal = (1/N) / 1 = 1/N

For above example with 3 counterparties:
Max HHI = 1
PCI = 0.38 / 1 = 0.38 = 38% of maximum

Alternative interpretation:
Equivalent to HHI / max(HHI) = 0.38
```

### Leverage Ratios

#### 1. Loan-to-Value (LTV)
**Definition**: Loan amount as percentage of collateral value.

```
LTV = Loan Amount / Collateral Value × 100%

Example - Mortgage:
Home value: $500,000
Loan amount: $400,000
LTV = 400,000 / 500,000 = 80%

Typical limits:
LTV < 80%: Standard loans
LTV 80-90%: Higher risk
LTV > 90%: Premium insurance required
LTV > 100%: Negative equity (underwater)
```

#### 2. Debt-to-Income (DTI)
**Definition**: Total debt payments as percentage of income.

```
DTI = (Monthly debt payments) / (Monthly income) × 100%

Example:
Monthly income: $5,000
Monthly debt payments:
- Mortgage: $2,000
- Car loan: $500
- Credit card: $200
- Student loan: $300
Total: $3,000

DTI = 3,000 / 5,000 = 60%

Acceptable ranges:
DTI < 36%: Low risk
36% < DTI < 43%: Moderate risk
DTI > 43%: High risk (borrower stretched)
```

#### 3. Loan-to-Deposit Ratio (LTD)
**Definition**: Total loans as percentage of total deposits; funding risk metric.

```
LTD = Total Loans / Total Deposits × 100%

Example:
Total loans: $800M
Total deposits: $1,000M
LTD = 80%

Interpretation:
LTD < 80%: Conservative (low funding risk)
80% < LTD < 100%: Moderate (normal)
LTD > 100%: High (loans exceed deposits, need wholesale funding)

Stress test:
If 30% of deposits withdrawn:
Available funds: $700M
Loan portfolio: $800M
Shortfall: $100M
```

### Profitability & Return Metrics

#### 1. Risk-Adjusted Return on Capital (RAROC)
**Definition**: Return on capital adjusted for risk; used to price products and allocate capital.

```
RAROC = Net Income / Economic Capital

Or more detailed:
RAROC = (Net Revenue - Operating Costs - Expected Loss) / Economic Capital

Example:
Product: Corporate loan
Loan amount: $100M
Interest rate: 5%
Annual net revenue: $5M
Expected Loss: $0.5M (5% probability of default × 10% loss given default)
Operating cost: $1M
Economic Capital (at 99% confidence): $8M (8% of loan)

RAROC = ($5M - $1M - $0.5M) / $8M = $3.5M / $8M = 43.75%

Interpretation:
Positive RAROC: Creates value
RAROC > cost of capital (typically 10-15%): Good business
RAROC < cost of capital: Lose value
Use RAROC to prioritize business activities
```

#### 2. Return on Risk-Adjusted Capital (RORAC)
**Definition**: Actual return achieved per unit of capital deployed.

```
RORAC = Annual Profit / Capital Allocated

Example:
Capital allocated to credit portfolio: $100M
Annual profit from credit portfolio: $15M
RORAC = 15% / 100M = 15%

Vs. cost of capital: 12%
Creates 3% spread (15% - 12% = 3%)
```

### Duration & Sensitivity Metrics

#### 1. Duration
**Definition**: Weighted average time to receive cash flows; sensitivity to parallel yield shifts.

```
Duration = Σ (t × CF_t) / Σ CF_t / (1+y)^t

Where:
t = time period
CF_t = cash flow in period t
y = yield

Example - Bond with 5-year maturity:
Year 1: $5 coupon
Year 2: $5 coupon
Year 3: $5 coupon
Year 4: $5 coupon
Year 5: $5 coupon + $100 principal

Modified Duration ≈ 4 years

Interpretation:
Bond price sensitivity = -Duration × Δy
1% yield increase → ~4% price decline
```

#### 2. Key Rate Duration
**Definition**: Sensitivity to changes at specific points on yield curve.

```
Example - Bond portfolio:
2Y KRD: +0.5 (positive sensitivity to 2Y rates)
5Y KRD: +2.5
10Y KRD: +1.0
30Y KRD: +0.3

If 2Y rates up 50 bps: -0.5 × 0.5% = -0.25% loss
If 5Y rates up 50 bps: -2.5 × 0.5% = -1.25% loss
```

#### 3. Basis Point Value (BPV) / DV01
**Definition**: Dollar change in value for 1 basis point yield move.

```
DV01 = -Duration × Portfolio Value × 0.01%

Example:
Portfolio value: $1,000,000
Duration: 5 years
DV01 = -5 × $1,000,000 × 0.0001 = -$500

Interpretation:
1 bp yield increase → $500 loss
100 bp yield increase → $50,000 loss

Risk limit: DV01 < $10,000 (trader limit)
Current position: DV01 = $8,500 ✓ Within limit
```

### Credit Risk Metrics

#### 1. Probability of Default (PD)
**Definition**: Probability counterparty defaults within 1 year.

```
PD estimation:
- From rating: AAA=0.03%, AA=0.1%, A=0.3%, BBB=1%, BB=3%, B=8%
- From spread: CDS spread proxy to PD
- From model: Credit scoring model output

Example:
Loan to company rated BBB
PD = 1% (from rating)
```

#### 2. Loss Given Default (LGD)
**Definition**: Percentage of exposure lost if default occurs.

```
LGD = 1 - Recovery Rate

Recovery rate varies by:
- Seniority: Senior 80%, Subordinated 20%
- Collateral: Mortgages (LGD 20%), Unsecured (LGD 60%)

Example:
Mortgage with 80% LTV
Collateral recovery: 95% of LTV = 76%
LGD = 1 - 0.76 = 24%
```

#### 3. Expected Loss (EL)
**Definition**: Average loss from credit portfolio.

```
EL = PD × LGD × EAD

Example:
PD = 1%
LGD = 40%
EAD = $1,000,000
EL = 0.01 × 0.40 × $1,000,000 = $4,000

Interpretation: Expect to lose $4,000 on average from this loan
```

#### 4. Unexpected Loss (UL) / Risk
**Definition**: Standard deviation of loss distribution; capital requirement.

```
UL ≈ √[PD(1-PD)] × LGD × EAD

Example:
PD = 1%
LGD = 40%
EAD = $1,000,000
UL = √[0.01 × 0.99] × 0.40 × $1,000,000
   = 0.0995 × 0.40 × $1,000,000
   = $39,800

Interpretation: 1-standard deviation loss is $39,800
99% confidence capital requirement ≈ $100,000
```

## Key Risk Indicators (KRIs)

### KRI Framework
KRIs are forward-looking indicators that signal elevated risk before actual losses occur.

**Characteristics**:
- Early warning signal
- Actionable (can respond to prevent losses)
- Readily available data
- Clear ownership
- Defined thresholds (green/yellow/red)

### Example KRI Portfolio

#### Credit Risk KRIs
```
1. PD Grade Migration
   Target: % upgrading > % downgrading
   Red if: Downgrades exceed upgrades by >5%

2. Loan Loss Provisions
   Target: In line with economic cycle
   Red if: Provisions increase > 20% YoY unexpectedly

3. Non-Performing Loan (NPL) Ratio
   Target: NPL ratio < 1%
   Yellow if: NPL ratio 1-2%
   Red if: NPL ratio > 2%

4. Delinquency Ratio
   Target: 30+ days delinquent < 1%
   Yellow if: 30+ delinquent 1-2%
   Red if: 30+ delinquent > 2%

5. Credit Spread CDS
   Target: Stable or tightening spreads
   Red if: CDS spread widens > 50 bps in month
```

#### Market Risk KRIs
```
1. Value at Risk (VaR)
   Target: VaR < $100M
   Yellow if: VaR $100M-$150M
   Red if: VaR > $150M

2. Stress Test Loss
   Target: Stress loss < 10% of capital
   Yellow if: Loss 10-15% of capital
   Red if: Loss > 15% of capital

3. Greeks Limits
   Target: Delta < $50M, Gamma < $10M, Vega < $5M
   Red if: Any limit exceeded

4. Limit Utilization
   Target: Utilization < 80%
   Yellow if: 80-95%
   Red if: > 95%
```

#### Liquidity Risk KRIs
```
1. Liquidity Coverage Ratio (LCR)
   Target: LCR > 100%
   Yellow if: 90-100%
   Red if: < 90%

2. Net Stable Funding Ratio (NSFR)
   Target: NSFR > 100%
   Yellow if: 90-100%
   Red if: < 90%

3. Deposit Outflows
   Target: Deposit growth > 0%
   Yellow if: Decline 0-5%
   Red if: Decline > 5% MoM

4. Funding Concentration
   Target: Top 10 depositors < 25%
   Yellow if: 25-30%
   Red if: > 30%
```

#### Operational Risk KRIs
```
1. Employee Turnover
   Target: Turnover < 10% annually
   Yellow if: 10-15%
   Red if: > 15%
   (Key risk roles: even lower thresholds)

2. Systems Availability
   Target: Uptime > 99.9%
   Yellow if: 99.0-99.9%
   Red if: < 99.0%

3. Regulatory Exceptions
   Target: < 5 exceptions
   Yellow if: 5-10
   Red if: > 10

4. Model Backtesting Exceptions
   Target: Within normal range (Green Zone)
   Yellow if: Yellow Zone
   Red if: Red Zone (>10 exceptions in 250 days)
```

### KRI Governance
```
1. Definition: Clear definition of calculation
2. Owner: Assigned to specific manager
3. Frequency: Daily, weekly, or monthly reporting
4. Thresholds: Green/Yellow/Red levels defined
5. Escalation: Clear escalation if threshold breached
6. Review: Regular (monthly/quarterly) review of appropriateness
7. Documentation: KRI register with all KRIs listed

Example KRI Register:
┌──────────────────────┬────────────┬────────────┬─────────────────┐
│ KRI Name             │ Owner      │ Frequency  │ Review Cycle    │
├──────────────────────┼────────────┼────────────┼─────────────────┤
│ NPL Ratio            │ Credit SVP │ Monthly    │ Quarterly       │
│ VaR                  │ Market RO  │ Daily      │ Monthly         │
│ Deposit Outflows     │ Treasury   │ Daily      │ Weekly          │
│ Employee Turnover    │ HR         │ Quarterly  │ Annually        │
└──────────────────────┴────────────┴────────────┴─────────────────┘
```

## Regulatory Risk Metrics

### Capital Ratios
```
Regulatory Capital Requirement (Basel III):

1. Common Equity Tier 1 (CET1) Ratio
   Requirement: ≥ 4.5%
   Definition: CET1 capital / Risk-weighted assets (RWA)

2. Tier 1 Ratio
   Requirement: ≥ 6%
   Definition: (CET1 + Additional Tier 1) / RWA

3. Total Capital Ratio
   Requirement: ≥ 8%
   Definition: (Tier 1 + Tier 2) / RWA

4. Leverage Ratio
   Requirement: ≥ 3%
   Definition: Tier 1 capital / Total assets (non-risk-weighted)

Example:
Bank with $1,000M RWA and $100M capital:
Capital ratio = $100M / $1,000M = 10% ✓ (Above 8% minimum)

If RWA increases to $1,200M (due to loan growth):
Capital ratio = $100M / $1,200M = 8.3% ✓ (Still adequate)
But if RWA increases to $1,400M:
Capital ratio = $100M / $1,400M = 7.1% ✗ (Below 8% minimum)
```

### Asset Quality Ratios
```
1. Non-Performing Loan Ratio
   NPL% = Non-performing loans / Total loans
   Target: < 1%

2. Loan Loss Reserve Ratio
   LLRR = Loan loss reserves / Total loans
   Target: Adequate to cover expected losses

3. Coverage Ratio
   CR = Loan loss reserves / Non-performing loans
   Target: > 100% (reserves > NPLs)
```
