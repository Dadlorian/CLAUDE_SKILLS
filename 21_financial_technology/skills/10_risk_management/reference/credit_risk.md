# Credit Risk Fundamentals

## Definition & Scope
Credit risk is the potential for loss due to a counterparty's failure to meet their financial obligations. It's the largest source of losses in most banks.

## Credit Risk Elements

### 1. Probability of Default (PD)
**Definition**: Probability that a counterparty will default within a specific time horizon (typically 1 year).

**Estimation Approaches**:
- **Through-the-Cycle (TTC)**: Long-term average default rate, smoothing economic cycles
- **Point-in-Time (PIT)**: Current default probability reflecting current economic conditions
- **Empirical**: Using historical default rates from credit rating agencies
- **Structural**: Based on firm value models (Merton model)
- **Reduced-Form**: Using bond yields and CDS spreads

**Key Factors**:
- Credit rating
- Industry and business cycle
- Macroeconomic conditions
- Company financials (leverage, liquidity, profitability)
- Management quality
- Competitive position

### 2. Loss Given Default (LGD)
**Definition**: Percentage of exposure lost if default occurs, accounting for recoveries.

**Formula**: LGD = 1 - Recovery Rate

**Recovery Drivers**:
- **Collateral Value**: Type, amount, quality of collateral pledged
- **Seniority**: Senior vs. subordinated claims
- **Jurisdiction**: Legal system, bankruptcy laws
- **Time to Recovery**: Duration of recovery process
- **Economic Conditions**: Market conditions affect collateral values

**Recovery Rates by Product**:
- Senior Secured (Mortgages): 50-90%
- Senior Unsecured (Bonds): 30-50%
- Subordinated Debt: 10-30%
- Equity: 0-10%

### 3. Exposure at Default (EAD)
**Definition**: Gross amount of credit exposure when counterparty defaults.

**Components**:
- **Drawn Amount**: Current usage/borrowing
- **Undrawn Commitments**: Available credit not yet used
- **Accrued Interest**: Interest owed up to default
- **Fees**: Prepaid fees and penalties

**EAD Factors**:
- **Utilization Rate**: % of available credit used
- **Credit Conversion Factor (CCF)**: % of undrawn commitment that becomes exposure
- **Future Exposure**: For derivatives, uncertainty in future values

**CCF Rates**:
- Revolving Facilities: 50-100%
- Non-revolving Facilities: 25-50%
- Letters of Credit: 20-50%

## Credit Risk Measurement

### Expected Loss (EL)
**Formula**: EL = PD × LGD × EAD

**Interpretation**: Average loss expected from credit exposures over time horizon.

**Example**:
- Loan Amount: $1,000,000
- PD: 2% (1 in 50 chance of default)
- LGD: 40% (recover 60%)
- EAD: $1,000,000 (fully drawn)
- EL = 0.02 × 0.40 × $1,000,000 = $8,000

### Unexpected Loss (UL)
**Definition**: Standard deviation of loss distribution; captures tail risk.

**Formula**: UL = √[PD(1-PD)LGD²EAD²] (simplified)

**Interpretation**: 1-standard deviation loss; used for capital allocation.

### Capital Requirement (K)
**Basel III Standardized Approach**: K = LGD × [N(√(1/1-ρ) × N⁻¹(PD) + √(ρ/(1-ρ)) × N⁻¹(0.999)) - PD]

Where:
- N(): Cumulative normal distribution
- ρ: Asset correlation (varies by exposure type)
- 0.999: 99.9% confidence level

## Credit Risk Assessment

### Traditional Approach
1. **Financial Analysis**: Leverage, profitability, liquidity ratios
2. **Industry Analysis**: Industry prospects, competitive position
3. **Management Assessment**: Quality, experience, strategic direction
4. **Collateral Analysis**: Type, value, enforceability
5. **Legal Structure**: Documentation, covenants, subordination

### Quantitative Approach
1. **Scoring Models**: Assign score based on financial metrics
2. **Rating Models**: Translate scores to rating (AAA to D)
3. **PD Estimation**: Calculate PD from rating/score
4. **Monitoring**: Track changes in metrics over time

## Credit Risk Limits

### Single-Name Limits
- **Absolute Limit**: Maximum exposure to single counterparty
- **Percentage Limit**: Maximum % of capital
- **Sector Limit**: Maximum exposure per sector
- **Grade Limit**: Different limits by credit rating

### Approval Authorities
- **Board**: Exposures above $500M
- **Credit Committee**: $100M-$500M
- **Line Officers**: Below $100M

### Limit Breaches
- Monitored daily
- Must be escalated and remediated
- May require additional capital or collateral

## Credit Risk Mitigation

### Collateral
**Purpose**: Reduce LGD by providing secondary repayment source.

**Types**:
- **Mortgages**: Real estate, primary residence or commercial
- **Securities**: Stocks, bonds, investment grade only
- **Cash**: Cash deposits, letters of credit
- **Guarantees**: Third-party guarantees or insurance

**Haircuts**:
- Applied to collateral value for volatility, liquidity
- Cash: 0%, AAA Bonds: 1%, BBB Bonds: 5%, Equities: 15-25%

### Netting Agreements
- **Bilateral Netting**: Offset assets/liabilities with counterparty
- **Novation**: New single contract replaces multiple trades
- **Legally Binding**: Reduces exposure in default

### Credit Derivatives
- **Credit Default Swap (CDS)**: Buy protection against default
- **Synthetic Securitization**: Transfer credit risk via securities

## Credit Concentrations

### Single-Name Concentration
**Measurement**:
- **Absolute Exposure**: Dollar amount
- **% of Capital**: Exposure / equity capital
- **% of Portfolio**: Exposure / total credit portfolio

**Limits**:
- Typically 10-15% of capital for top exposures
- 5% for single counterparty (Basel III)

### Sector Concentration
**Measurement**:
- Sum of exposures in sector as % of portfolio

**Common Sectors**:
- Real Estate
- Oil & Gas
- Retail/Consumer
- Manufacturing
- Financial Services

### Geographic Concentration
**Measurement**:
- Sum of exposures in geography as % of portfolio

**Key Factors**:
- Economic conditions
- Regulatory environment
- Macroeconomic correlation

## Rating Systems

### External Ratings
- **Moody's**: Aaa to C
- **S&P**: AAA to D
- **Fitch**: AAA to D
- **DBRS**: AAA to D

### Internal Ratings
- **Scale**: Typically 1-20 grades
- **Mapping**: Map internal to external for consistency
- **Validation**: Backtest ratings against defaults

### Rating Migration
**Transition Matrix**: Shows % moving from one rating to another over time period.

**Example**:
```
From/To    AAA    AA    A    BBB    BB    B    CCC    D
AAA       98.0   1.5  0.3   0.1   0.0  0.0  0.0   0.1
AA         0.5  96.0  2.5   0.8   0.1  0.0  0.0   0.1
A          0.1   2.0 94.0   3.2   0.5  0.1  0.0   0.1
BBB        0.0   0.2  4.0  90.0   4.5  1.0  0.2   0.1
BB         0.0   0.0  0.5   5.5  85.0  7.5  1.0   0.5
B          0.0   0.0  0.1   0.5   7.0 80.0  10.0  2.4
CCC        0.0   0.0  0.0   0.3   1.0  10.0  60.0  28.7
```

## Expected Credit Loss (ECL) - IFRS 9

### Three Stages
1. **Stage 1**: No significant credit risk increase - 12-month ECL
2. **Stage 2**: Significant credit risk increase - Lifetime ECL
3. **Stage 3**: Credit-impaired - Lifetime ECL with loss allowance

### Calculation
ECL = Probability-weighted average of outcome scenarios

**Formula**:
```
ECL = Σ(Probability_i × Loss_i)

Where:
Loss_i = EAD × LGD × (1 - Recovery_rate) for scenario i
```

### Macroeconomic Scenarios
- **Base Case**: Most likely scenario (50% weight)
- **Upside Case**: Positive scenario (25% weight)
- **Downside Case**: Negative scenario (25% weight)
