# Basel III/IV Framework

## Overview
Basel III is the international regulatory framework for banking capital, developed by the Basel Committee on Banking Supervision (BCBS). It sets minimum capital requirements, liquidity standards, and leverage ratios designed to ensure banking system stability.

## Historical Context

### Basel I (1988)
- First international capital standards
- Simple: 8% of assets weighted by risk
- Credit risk only
- Led to regulatory arbitrage

### Basel II (2004)
- Three pillars approach
- Advanced credit risk models (IRB)
- Market risk models
- Operational risk capital
- Problem: Too complex, allowed too much optimization

### Basel III (2010)
- Post-2008 crisis overhaul
- Higher capital requirements
- Liquidity standards (LCR, NSFR)
- Leverage ratio (non-risk-weighted)
- Implemented 2013-2019

### Basel IV / Basel III Endgame (2024+)
- Final Basel III revisions
- Output floor (internal models can't reduce capital by >25%)
- Stricter operational risk models
- Expected completion by 2025

## Basel III Pillar 1: Minimum Capital Requirements

### Capital Components

#### Tier 1 Capital (8-10.5%)
**Common Equity Tier 1 (CET1)**: Highest quality capital
- Issued share capital
- Retained earnings
- Common stock
- Minus: Intangibles, goodwill, deferred tax assets

**Additional Tier 1**: Hybrid instruments
- Perpetual bonds (no maturity)
- Contingent convertibles (convert to equity if capital falls)
- Cannot have maturity or step-down in coupons

#### Tier 2 Capital (2-5%)
- Subordinated debt (minimum 5-year maturity)
- Loan loss reserves (up to 1.25% of RWA)
- Hybrid instruments with 5+ year maturity

### Capital Buffers

```
Total Capital Requirement = 8% base + buffers

Pillar 1: 8%
Capital Conservation Buffer: 2.5%
Countercyclical Buffer: 0-2.5% (set by regulators)
Systemically Important Buffer (G-SIB): 1-3.5%

Example for large US bank:
Minimum Tier 1: 10.5%
CET1 alone: 7% (of which 2.5% conservation)
Tier 2: 2%
Total: 10.5%

In stress (capital falls):
If capital ratio hits conservation buffer:
- Dividends restricted
- Share buybacks stopped
- Bonus restrictions (banks must retain capital)
```

### Risk-Weighted Assets (RWA) Calculation

**Standardized Approach**:
```
RWA = Σ (EAD × Risk Weight)

Risk weights (examples):
Cash: 0%
Government bonds (AAA): 0%
Government bonds (AA-): 20%
Corporate bonds (A): 50%
Corporate bonds (BBB): 100%
Corporate bonds (BB): 150%
Mortgages (LTV < 80%): 35%
Mortgages (LTV 80-90%): 50%
Mortgages (LTV > 90%): 75%
Equities: 100%

Example:
Assets by type:
- Cash: $50M × 0% = $0M RWA
- Government bonds: $200M × 20% = $40M RWA
- Corporate loans (BBB): $300M × 100% = $300M RWA
- Mortgages: $350M × 50% = $175M RWA
- Equity holdings: $100M × 100% = $100M RWA
Total RWA: $615M

If capital available = $65M:
Capital ratio = $65M / $615M = 10.6%
Requirement = 8% (minimum)
Excess capital: 2.6%
```

**Internal Ratings-Based (IRB) Approach**:
For large banks, use internal credit models.

```
RWA = EAD × Risk Weight

Risk Weight formula (simplified):
K = LGD × [N(√(1/1-ρ) × N⁻¹(PD) + √(ρ/(1-ρ)) × N⁻¹(0.999)) - PD]

Where:
- N() = Cumulative normal distribution
- PD = Probability of default
- LGD = Loss given default
- ρ = Asset correlation (0.12 for corporates, 0.03 for equities)
- 0.999 = 99.9% confidence level

Example for corporate exposure:
PD = 1%
LGD = 45%
ρ = 0.12

K = 0.45 × [N(√(1/0.88) × N⁻¹(0.01) + √(0.12/0.88) × N⁻¹(0.999)) - 0.01]
  = 0.45 × [N(1.065 × (-2.33) + 0.369 × 3.09) - 0.01]
  = 0.45 × [N(-2.48 + 1.14) - 0.01]
  = 0.45 × [N(-1.34) - 0.01]
  = 0.45 × [0.0903 - 0.01]
  = 0.45 × 0.0803
  = 0.036 = 3.6%

RWA = 3.6% × EAD
For $10M exposure: RWA = $360k (vs. $1M under standardized)
```

### Credit Risk Components

#### 1. On-Balance Sheet
- Direct loans
- Bonds and securities held
- Balances due from banks

#### 2. Off-Balance Sheet
- Loan commitments (CCF applied)
- Letters of credit
- Guarantees

#### 3. Counterparty Credit Risk (CCR)
- Derivatives exposure
- Repo/securities lending
- Collateral valuation

**CCR capital = Potential Future Exposure (PFE) × CVA charge**

```
Example - Interest rate swap:
Notional: $100M
Current exposure: $2M
PFE (add-on): 5% of notional = $5M
CVA (credit valuation adjustment): $200k

Total CCR capital = $2M + $5M + $200k = $7.2M
```

### Market Risk Capital

**Regulatory capital for trading positions:**

**Standardized Approach**:
```
Market risk capital = VaR(99%, 10-day) × 3 + Stress Loss

Example:
1-day 99% VaR: $500k
10-day VaR: $500k × √10 = $1.58M
Regulatory VaR charge: $1.58M × 3 = $4.74M

Stress loss (worst historical month): $2M
Total market risk capital: $4.74M + $2M = $6.74M
```

**Internal Models Approach (IMA)**:
Allow banks to use own VaR/stress models if validated.

### Operational Risk Capital

**Standardized Approach**:
```
Op Risk Capital = Σ (Gross Income × Beta)

Business lines and betas:
- Corporate Finance (18%): M&A, IPO
- Trading & Sales (18%): Proprietary trading, sales
- Retail Banking (12%): Consumer lending, deposits
- Commercial Banking (15%): Corporate lending
- Payment & Settlement (18%): Payment processing
- Agency Services (15%): Custody, fund administration
- Asset Management (12%): Fund management

Example Bank:
Corporate Finance gross income: $50M × 18% = $9M
Trading & Sales: $80M × 18% = $14.4M
Retail Banking: $60M × 12% = $7.2M
Total op risk capital: $30.6M
```

## Basel III Pillar 2: Supervisory Review

**Purpose**: Ensure banks assess risks not captured by Pillar 1.

**Key Areas**:
1. **Interest Rate Risk in Banking Book**: Asset-liability management, duration risk
2. **Concentration Risk**: Single-name, sector, geographic
3. **Liquidity Risk**: Funding, market liquidity
4. **Operational Risk**: Cyber, conduct, third-party
5. **Profitability**: Capital adequacy with lower earnings
6. **Model Risk**: Validation, assumptions
7. **Reputational Risk**: Brand damage from events

**Supervisory Process**:
1. Bank self-assessment (ICAAP)
2. Regulator review
3. Capital conversation (if needed)
4. Regulatory decision

## Basel III Pillar 3: Market Discipline

**Disclosure Requirements**:
- Capital structure and adequacy
- Risk management frameworks
- Credit, market, operational risk details
- Leverage ratio
- Liquidity coverage

**Quarterly/Annual Reporting**:
- Published on bank websites
- Required disclosures listed in regulations
- Audit and verification

## Liquidity Standards

### Liquidity Coverage Ratio (LCR)
```
LCR = High-Quality Liquid Assets / Net Cash Outflows ≥ 100%

Requirement: Minimum 1:1 ratio
Phase-in: 100% by 2019

HQLA components:
- Level 1: Cash, government securities (no haircut)
- Level 2A: High-quality corporates (15% haircut)
- Level 2B: Equities, RMBS (25% haircut)

NCO stress assumptions:
- Demand deposits: 5% runoff
- Savings deposits: 25% runoff
- Wholesale deposits: 100% runoff
- Undrawn commitments: 30% drawn
```

### Net Stable Funding Ratio (NSFR)
```
NSFR = Available Stable Funding / Required Stable Funding ≥ 100%

Requirement: Minimum 1:1 ratio by 2018
Longer-term (1 year) maturity focus

ASF:
- Capital: 100%
- Core deposits: 95%
- Less stable deposits: 75%
- Wholesale funding: 0-50%

RSF:
- Cash: 0%
- Loans (mortgages): 35-50%
- Loans (commercial): 50-85%
- Undrawn commitments: 5-10%
```

## Leverage Ratio

**Purpose**: Non-risk-weighted backstop to RWA.

```
Leverage Ratio = Tier 1 Capital / Total Exposure Measure ≥ 3%

Total Exposure = Total assets + off-balance sheet + derivatives

Example:
Tier 1 capital: $100M
Total assets: $2,000M
Derivatives exposure: $500M
Total exposure: $2,500M

Leverage ratio = $100M / $2,500M = 4% ✓ (Above 3% minimum)

Advantage: Cannot be gamed by risk weights
```

## Basel IV / Endgame Features

### Output Floor
```
Internal models capital cannot be <75% of standardized approach

Example:
Standardized Approach RWA: $1,000M
Internal Models RWA: $600M (60% reduction)
Regulatory RWA = MAX($1,000M × 75%, $600M)
             = MAX($750M, $600M)
             = $750M

Effect: Limits optimization of risk weights
```

### Operational Risk Changes
```
Old approach: Beta × gross income

New approach: Individual components + aggregation formula
- Historical loss component (HLC)
- Business indicator component (BIC)
- Internal loss multiplier (ILM)

More granular, harder to optimize
```

### Equity Risk Framework
```
Replacement of complex internal models with standardized buckets
Simplifies equity risk capital
Makes equity positions comparable across banks
```

## Regional Variations

### US Implementation
- Stress testing (CCAR) annually
- Higher capital requirements for largest banks
- Divergent from Basel III (stricter in some areas)

### EU Implementation
- CRR/CRD IV regulatory framework
- EBA guidelines for consistency
- Some divergence in risk weights

### UK Implementation
- PRA framework (more stringent)
- Additional buffers for stability
- Enhanced supervision of systemic banks
