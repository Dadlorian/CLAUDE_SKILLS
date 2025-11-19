# Solvency Requirements

## Solvency Overview

Solvency requirements exist to protect policyholders by ensuring insurance companies maintain sufficient capital and reserves to pay claims. Regulatory solvency requirements are fundamental to insurance supervision.

## Solvency Concept

### Key Definitions

**Solvency**:
- Insurance company can meet all financial obligations
- Assets exceed liabilities
- Can pay claims as they fall due
- Maintains adequate capital buffer

**Insolvency**:
- Cannot meet financial obligations
- Liabilities exceed assets
- Cannot pay claims
- May require regulatory intervention

### Why Solvency Matters

**Consumer Protection**:
- Protects policyholders' claims
- Ensures premiums aren't wasted
- Provides financial security
- Protects beneficiaries

**Financial Stability**:
- Maintains market confidence
- Prevents systemic risk
- Protects interconnected financial system
- Prevents cascading failures

**Economic Impact**:
- Unpaid claims create economic dislocation
- Business interruption from unpaid claims
- Contagion risk to other insurers
- Cost to state guarantee funds

## U.S. Risk-Based Capital (RBC) System

### RBC Framework

**Components**:
```
RBC = Required Capital for:
      ├── Investment Risk (IRisk)
      ├── Insurance Risk (C0Risk)
      ├── Interest Rate Risk (C1Risk)
      ├── Credit Risk (C2Risk)
      ├── Off-Balance Sheet Risk (C3Risk)
      └── Other Risk (C4Risk)

Total RBC = √(sum of squared risks)
```

**Risk Factors**:
- **Underwriting Risk**: Risk of adverse claims experience
- **Investment Risk**: Risk of asset value decline
- **Credit Risk**: Risk of counterparty default
- **Affiliate Risk**: Risk from affiliated companies
- **Off-Balance Sheet**: Risk from contingent liabilities

### RBC Calculation Example

**Hypothetical Auto Insurer**:

```
Investment Risk:
  Fixed Income Securities: $100M × 0.3% = $300K
  Equity Securities: $50M × 3% = $1,500K
  Investment Risk Total = $1,800K

Underwriting Risk (Auto):
  Premium Risk: $500M × 0.08 = $40,000K
  Reserve Risk: $200M × 0.10 = $20,000K
  Underwriting Risk Total = $60,000K

Total RBC = √($1,800K² + $60,000K²) = $60,027K

Current Capital: $120,000K
RBC Ratio: $120,000K / $60,027K = 199% (Normal Range 150-200%)
```

### RBC Action Levels

**Four Regulatory Action Levels**:

1. **Normal Range** (>200% RBC)
   - No regulatory action
   - Continue normal operations
   - Annual/quarterly reporting

2. **Company Action Level** (150-200% RBC)
   - Company must submit plan to regulator
   - Regulator reviews plan
   - Increased reporting required
   - Management action suggested

3. **Regulatory Action Level** (100-150% RBC)
   - Regulator may take action
   - May order rehabilitation plan
   - Increased supervision
   - Stricter operational controls

4. **Mandatory Action Level** (<100% RBC)
   - Regulator takes mandatory action
   - May order receivership
   - Company seizure
   - Claims paying obligations transferable

### RBC vs. Statutory Capital

**Statutory Capital (Minimum)**:
- Minimum capital/surplus required
- Fixed amount by company size/type
- Typically $500K to $5M+
- Not risk-adjusted

**RBC (Risk-Based)**:
- Adjusted for actual risk profile
- Takes into account asset risk, underwriting risk
- Dynamic - changes with company risk
- Typically higher than minimum capital

## European Solvency II Framework

### Solvency II Overview

**Effective**: January 1, 2016
**Coverage**: All EU insurance companies
**Purpose**: Risk-based capital requirement
**Three Pillars**: Quantitative (capital), Qualitative (governance), Disclosure

### Three Pillar Structure

**Pillar 1: Quantitative Requirements**

*Solvency Capital Requirement (SCR)*:
- Amount of capital needed to cover 99.5% of losses over 1 year
- Calculated using Standard Formula or Internal Models
- Risk-based, forward-looking
- Higher than Minimum Capital Requirement

*Minimum Capital Requirement (MCR)*:
- Absolute minimum capital threshold
- Approximately 25-45% of SCR
- Breaching MCR triggers intervention
- Absolute minimum enforcement trigger

*Capital Composition*:
- Tier 1: Highest quality capital (equity, retained earnings)
- Tier 2: Subordinated debt and hybrid instruments
- Tier 3: Other eligible items

**Example Calculation**:
```
Solvency II Positions:
Market Risk: €50M
Credit Risk: €20M
Life Underwriting Risk: €80M
Health Underwriting Risk: €15M
Operational Risk: €10M

SCR = €155M (simplified sum)
MCR = €40M (approximately 25% of SCR)

Current Capital: €200M
Ratio = €200M / €155M = 129% (Adequate, but not excessive)
```

**Pillar 2: Governance Requirements**

*System of Governance*:
- Board oversight of solvency
- Internal audit function
- Compliance function
- Risk management function
- Actuarial function

*Fit & Proper*:
- Board members must be fit and proper
- Demonstrate competence and integrity
- Annual fit and proper assessment
- Change of control approval

*Risk Management*:
- Identify and monitor key risks
- Report risks to management
- Implement risk mitigation
- Capital management plan
- Stress testing and scenario analysis

**Pillar 3: Transparency and Disclosure**

*Supervisory Reporting*:
- Regular reporting to regulator
- Quarterly quantitative reporting
- Annual qualitative reporting
- Capital adequacy reports
- Regulatory filing system (XBRL)

*Public Disclosure*:
- Annual public disclosure
- Management comment (Pillar 3 report)
- Summary of capital and solvency
- Non-commercial information only
- Three-year comparative data

### Internal Models in Solvency II

**Standard Formula**:
- Regulatory-prescribed formula
- Pre-defined risk factors
- Applies to most companies
- Conservative approach

**Internal Models**:
- Company-developed models
- Approved by regulators
- More sophisticated approach
- Must meet validation standards
- Higher capital efficiency possible

## Solvency Stress Testing

### Regulatory Stress Tests

**Purpose**:
- Assess capital adequacy under stress
- Identify vulnerabilities
- Ensure preparedness
- Inform management decisions
- Regulatory oversight

**Scenarios**:

*Interest Rate Shock*:
- Rate increase/decrease by specified amount
- Impact on asset values
- Impact on liability values
- Example: -100 bps to +100 bps

*Market Shock*:
- Stock market decline 30-50%
- Bond spread widening 100+ bps
- Real estate value decline
- Property value decline

*Underwriting Shock*:
- Loss experience worse than expected
- Claims inflation
- Frequency increase
- Severity increase

*Catastrophe Scenarios*:
- Hurricane
- Earthquake
- Pandemic
- Terrorism

**Example Stress Test**:
```
Baseline Capital: €200M

Scenario 1: Interest Rate +300 bps
Asset Impact: -€30M (bonds decline)
Liability Impact: +€5M (increase in reserves)
Net Capital: €175M (87.5% of baseline)

Scenario 2: Equity Market -40%
Asset Impact: -€40M (stocks decline)
Liability Impact: €0
Net Capital: €160M (80% of baseline)

Scenario 3: Combined Stress
Combined Impact: -€80M
Net Capital: €120M (60% of baseline)

Conclusion: Company maintains adequate capital under all scenarios
```

## Solvency Monitoring and Compliance

### Continuous Monitoring
- **Dashboard Metrics**: Real-time monitoring
- **RBC Ratio Tracking**: Monthly or quarterly
- **Reserve Adequacy**: Quarterly reserve analysis
- **Investment Exposure**: Asset concentration monitoring
- **Reinsurance**: Reinsurer credit monitoring

### Reporting to Regulators
- **Annual Statement**: Comprehensive annual filing
- **Quarterly Reports**: Summary financial reports
- **Solvency Filings**: RBC, Solvency II reports
- **Significant Events**: Material developments
- **Management Changes**: Board/officer changes

### Regulatory Response to Insolvency
- **Supervision**: Increased regulatory supervision
- **Plans**: Company must submit remediation plan
- **Restricted Activities**: Restrictions on new business
- **Rehabilitation**: Formal rehabilitation plan
- **Receivership**: Court-ordered receivership
- **Liquidation**: Orderly wind-down

## Guarantee Funds

### State Guarantee Funds (US)

**Purpose**:
- Final safety net for unpaid claims
- Protect policyholders
- Pool risk across insurers
- Insurer-funded (not taxpayer)

**Coverage Limits**:
- Property & Casualty: $100K-$300K per claim
- Life Insurance: $250K-$300K per person
- Health Insurance: Varies by state
- Usually per claim, not per person

**Funding**:
- Assessments on solvent insurers
- Post-assessment after insolvency
- Recovery mechanism for future earnings
- Premium surcharges

## International Solvency Frameworks

### IAIS Insurance Core Principles

**Core Principles**:
- Capital adequacy based on risks
- Transparent capital requirements
- Regular review and monitoring
- Disclosure to policyholders
- Coordination among regulators

### G-20 Financial Stability Board (FSB)

**Insurance Regulation Reform**:
- Improve policyholder protection
- Enhance financial stability
- Promote sound capital frameworks
- Increase regulatory coordination
- Systemically important firms (G-SIIs)

### Insurance Capital Standard (ICS)

**Global Framework**:
- Developing global solvency framework
- Convergence across jurisdictions
- Risk-based capital requirements
- Applies to internationally active insurers (IAIs)
- Baseline capital requirement (BCR) and minimum capital requirement (MCR)

## Emerging Solvency Considerations

### Climate Risk
- **Physical Risk**: Asset damage from climate change
- **Transition Risk**: Economic impact of climate transition
- **Stranded Assets**: Assets becoming worthless
- **Stress Testing**: Climate scenarios in stress tests

### Cybersecurity Risk
- **Operational Risk**: System outages
- **Data Risk**: Data breach impact
- **Reputational Risk**: Reputation damage
- **Financial Impact**: Claims and recovery costs

### Pandemic Risk
- **Exposure**: Health insurance exposure
- **Mortality**: Excess mortality risk
- **Economic**: Economic disruption impact
- **Correlation**: Correlation across businesses
