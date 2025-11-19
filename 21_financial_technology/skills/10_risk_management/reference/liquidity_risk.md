# Liquidity Risk Management

## Definition & Scope
Liquidity risk is the risk that an institution cannot meet cash obligations as they come due, or can only meet them at excessive cost. It involves both funding liquidity risk and market liquidity risk.

## Funding Liquidity Risk

### Definition
Risk that the institution cannot obtain sufficient funding to meet payment obligations, or can only do so at prohibitive cost.

### Causes

#### 1. Balance Sheet Maturity Mismatch
**Issue**: Short-term funding, long-term assets.

**Example**:
- Mortgage loans (30-year) funded by deposits (can be withdrawn anytime)
- Asset-backed securities funded by commercial paper (270-day)

**Risk**: When short-term funding matures, must refinance or liquidate assets.

#### 2. Deposit Instability
**Characteristics**:
- Core deposits: More stable (salaries, operational needs)
- Non-core deposits: Volatile (broker deposits, hot money)
- High rates: Can attract/retain deposits in competition
- Reputation/ratings: Downgrades trigger deposit flight

**Measurement**:
- Core deposit ratio: % of core vs. total deposits
- Deposit concentration: % from top 10 depositors
- Deposit beta: % increase in rates needed to retain 1% of deposits

#### 3. Wholesale Funding Stress
**When Access Dries Up**:
- Repo market stress
- Money market fund outflows
- Commercial paper market freezes
- Bond market dislocations
- Counterparty concerns

**Example - 2008 Crisis**:
- Lehman collapse triggered repo market freeze
- Money market funds faced withdrawals
- Commercial paper market dislocated
- Asset-backed securities illiquid

#### 4. Contingent Funding Needs
**Off-balance Sheet Obligations**:
- Loan commitments: Must fund if drawn
- Revolving credit facilities: Customer drawdowns
- Backup funding: Securities lending, derivatives collateral
- Guarantees: Must fund if guaranteed party defaults

**Example**:
- $1B of unfunded loan commitments
- If 10% drawn during stress: $100M funding need
- Must be in liquidity buffer

### Liquidity Coverage Ratio (LCR)

**Definition**: Basel III liquidity standard introduced post-2008 crisis.

**Formula**:
```
LCR = High-Quality Liquid Assets (HQLA) / Net Cash Outflows (NCO)
Target: ≥ 100% (minimum 1:1)
```

**High-Quality Liquid Assets (HQLA)**:

Level 1 (no haircut):
- Cash
- Central bank reserves
- Government securities (AAA/AA rated)

Level 2A (15% haircut):
- Government securities (A to AA-)
- Corporate bonds (AAA to AA-)

Level 2B (25% haircut):
- Corporate bonds (A+)
- Equities in major indices
- RMBS (AAA/AA rated)

**Net Cash Outflows (NCO)**:

Outflows (stress assumptions):
- Deposits: 5% demand, 25% savings, 100% wholesale (no collateral)
- Wholesale funding: 100% if not collateralized by HQLA
- Margin/collateral: 20% increase in haircuts
- Debt maturity: 100% of maturing debt
- Lines of credit: 30% assumed drawn

Inflows (no more than 75%):
- Maturing loans: Principal repayment (75% max)
- Maturing securities: Proceeds received
- CB deposits: Limited benefits

**Example**:
```
HQLA:
  Level 1: $200M
  Level 2A: $100M (15% haircut = $85M)
  Level 2B: $50M (25% haircut = $37.5M)
  Total: $322.5M

Outflows:
  Demand deposits: $300M × 5% = $15M
  Savings deposits: $200M × 25% = $50M
  Wholesale deposits: $100M × 100% = $100M
  Maturing wholesale funding: $150M × 100% = $150M
  Undrawn commitments: $500M × 30% = $150M
  Total: $465M

Inflows (75% cap):
  Loan repayments: $200M
  Applied (capped): $200M × 75% = $150M

NCO = $465M - $150M = $315M

LCR = $322.5M / $315M = 102.4% ✓ (Above 100%)
```

### Net Stable Funding Ratio (NSFR)

**Definition**: Basel III medium-term (1 year) liquidity standard.

**Formula**:
```
NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF)
Target: ≥ 100% (minimum 1:1)
```

**Available Stable Funding (ASF)**:
- Capital: 100%
- Deposits (retail, stable): 95%
- Deposits (retail, less stable): 75%
- Wholesale deposits (AA+ or better): 50%
- Wholesale deposits (below AA+): 0%
- Other liabilities: 0-25% depending on maturity

**Required Stable Funding (RSF)**:
- Cash, loans to financial institutions: 0%
- Residential mortgages (secured): 35-50%
- Commercial loans: 50-85%
- Undrawn commitments: 5-10%
- Other assets: 100%

**Example**:
```
Available Stable Funding:
  Capital/Retained earnings: $50M (100%) = $50M
  Core deposits: $400M (95%) = $380M
  Other deposits: $100M (75%) = $75M
  Wholesale (AA+): $150M (50%) = $75M
  Total ASF: $580M

Required Stable Funding:
  Cash/CB reserves: $50M (0%) = $0M
  Residential mortgages: $300M (50%) = $150M
  Commercial loans: $200M (75%) = $150M
  Other assets: $50M (100%) = $50M
  Undrawn commitments: $100M (10%) = $10M
  Total RSF: $360M

NSFR = $580M / $360M = 161% ✓ (Above 100%)
```

## Market Liquidity Risk

### Definition
Risk that an institution cannot liquidate positions without significant price concessions (losses).

### Characteristics

**Illiquidity Measures**:
- **Bid-Ask Spread**: Difference between buying and selling price
  - Treasury bonds: 1-2 bps
  - Corporate bonds: 5-50 bps
  - Junk bonds: 50-500 bps
  - Equities: 1-5 bps
  - Derivatives: Wider in stress

- **Market Impact**: Price move from own trading
  - Small orders: Minimal impact
  - Large orders: Significant impact
  - Market stress: Impact multiplies

- **Turnover/Volume**: How easily positions can be traded
  - High volume: Liquid
  - Low volume: Illiquid
  - Volume dries up in stress

### Correlation Breakdown
**Key Risk**: During market stress, correlations change, reducing diversification.

**Examples**:
- 2008 Crisis: "Risk-on/Risk-off" environment
  - All risky assets sold simultaneously
  - Correlations → 1, diversification fails
  - Collateral values decline
  - Margin calls force forced selling

**Metrics**:
- **Correlation Clustering**: Measure high-correlation periods
- **Stress Correlation Matrix**: Correlations during crises (often 0.8+)

### Fire Sales & Contagion
**Mechanism**:
1. Initial shock (bank failure, geopolitical event)
2. Margin calls force selling
3. Prices decline
4. Margin calls spread
5. Contagion across markets

**Example - 1998 Russian Crisis & LTCM**:
1. Russia defaults on domestic debt
2. Foreign investors sell Russian bonds
3. LTCM had massive bet on convergence
4. LTCM faces margin calls
5. LTCM forced to sell positions
6. Prices collapse across markets
7. Contagion spreads to US credit markets

## Liquidity Risk Measurement

### Liquidity Stress Scenarios

#### Mild Stress (LCR)
- 5% increase in demand deposits
- Deposits flee gradually
- Margin increase: 20%

#### Severe Stress (Historical scenarios)
- 2008 Financial Crisis
- 1998 Russian Crisis + LTCM
- 2011 European Debt Crisis
- 2020 COVID Shock

#### Firm-Specific Stress
- Downgrade by rating agencies
- Earnings miss
- Executive resignation
- Competitor failure

### Stress Testing

**Approach 1: Scenario Analysis**
- Define stress scenario
- Estimate funding flows under scenario
- Estimate market value changes
- Calculate liquidity position under stress

**Approach 2: Sensitivity Analysis**
- Vary deposit retention: -25%, -50%, -75%
- Vary asset prices: -10%, -25%, -50%
- Vary funding spreads: +100bps, +200bps, +500bps
- Estimate liquidity pressure for each sensitivity

**Example Stress Test Result**:
```
Scenario: Firm-specific downgrade
- Deposits withdraw: 20% (500M of 2.5B)
- HQLA value drops: 10%
- Wholesale funding unavailable: 50% ($500M)
- Resulting liquidity need: $1.0B
- Available liquidity buffer: $320M
- Shortfall: $680M
- Mitigation: Sell securities, attract deposits, reduce lending

Conclusion: 3-5 days of liquidity under severe stress
Should extend to 10+ days per regulatory guidance
```

## Liquidity Risk Management

### Liquidity Buffers
**Purpose**: Absorb funding shocks without forced asset sales.

**Components**:
- Cash on hand
- Central bank eligible collateral
- Securities readily convertible to cash
- Standby borrowing facilities

**Target**: 7-14 days of funding need for institution

### Diversified Funding
**Goal**: Multiple funding sources reduce dependence on single source.

**Funding Mix**:
- Retail deposits: Stable but rate-sensitive
- Wholesale deposits: More expensive, volatile
- Wholesale borrowing: Repo, CD, bonds
- Secured funding: Repo (cheaper)
- Unsecured funding: Bonds, CD (more expensive)

**Metrics**:
- % from top 10 depositors (low is better)
- % maturing in each time period (balanced)
- % by funding source (diversified)

### Contingency Funding Plan (CFP)
**Purpose**: Pre-planned response to liquidity stress.

**Components**:
1. **Triggers**: Identify when to activate plan
   - Firm-specific: Downgrade, earnings miss
   - Market-wide: Credit spread widening, equity sell-off
   - Systemic: Competitor failure, central bank actions

2. **Actions**: Response options
   - Reduce lending: Slow down new originations
   - Attract deposits: Increase rates
   - Liquidate securities: Sell from buffer
   - Draw credit facilities: Access backup funding
   - Sell businesses: Divest non-core operations

3. **Governance**: Who decides, approval authorities

4. **Communication**: How to communicate with stakeholders

### Intra-day Liquidity
**Definition**: Management of liquidity needs within a single day.

**Challenges**:
- Settlement systems operate on schedule
- Large payments may be time-specific
- Must be ready to pay at exact time
- Cannot wait for inflow if outflow due

**Solutions**:
- Real-time liquidity monitoring
- Prioritize payments in sequence
- Arrange in-day borrowing if needed
- Keep backup payment methods

## Liquidity Risk Governance

### Board Oversight
- Approve liquidity policy and risk appetite
- Review LCR, NSFR monthly
- Approve contingency funding plan
- Review stress test results

### Management Committee
- Monitor LCR/NSFR daily
- Manage funding operations
- Escalate liquidity stress
- Implement contingency plan if needed

### Recovery and Resolution Planning (RRP)
- Identify liquidity-enhancing actions
- Test feasibility of actions
- Ensure can survive 6-12 months of stress
- Pre-position collateral at central banks
