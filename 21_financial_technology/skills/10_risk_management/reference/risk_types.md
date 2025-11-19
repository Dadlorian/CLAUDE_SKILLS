# Risk Types in Financial Institutions

## Overview
Financial institutions face multiple categories of risk that must be identified, measured, and managed. These risks are interconnected and require comprehensive management frameworks.

## Credit Risk

### Definition
The risk that a counterparty fails to meet its obligations, resulting in financial loss.

### Components
- **Default Risk**: Counterparty unable or unwilling to pay
- **Recovery Risk**: Uncertainty in recovery rates and timing
- **Exposure Risk**: Uncertainty in future exposure amount
- **Concentration Risk**: Over-exposure to specific borrowers or sectors

### Types
- **Wholesale Credit Risk**: Loans to corporations, financial institutions, sovereigns
- **Retail Credit Risk**: Mortgages, consumer loans, credit cards
- **Counterparty Risk**: Exposure in derivatives, securities lending, repo
- **Sovereign Risk**: Risk of government default
- **Sub-sovereign Risk**: Risk of regional/local government default

### Metrics
- **Probability of Default (PD)**: % chance counterparty defaults in 1 year
- **Loss Given Default (LGD)**: % of exposure lost if default occurs
- **Exposure at Default (EAD)**: Amount exposed at time of default
- **Expected Loss (EL)**: EL = PD × LGD × EAD

## Market Risk

### Definition
Risk of losses due to changes in market prices (interest rates, FX, equities, commodities).

### Components
- **Interest Rate Risk**: Exposure to yield curve changes
- **Foreign Exchange Risk**: Exposure to FX rate changes
- **Equity Risk**: Exposure to equity price changes
- **Commodity Risk**: Exposure to commodity price changes
- **Volatility Risk**: Exposure to changes in price volatility
- **Correlation Risk**: Exposure to changes in correlations between assets

### Sub-categories
- **Trading Book Risk**: Risk in positions held for trading
- **Banking Book Risk**: Risk in long-term loans and deposits
- **Basis Risk**: Risk from imperfect hedges
- **Liquidity Risk**: Risk from inability to trade at normal prices

### Metrics
- **Value at Risk (VaR)**: Maximum loss at confidence level over time horizon
- **Greeks**: Delta, gamma, vega, theta for derivatives
- **DV01**: Dollar value of 1 basis point move in yields
- **CS01**: Credit spread value of 1 basis point move

## Operational Risk

### Definition
Risk of losses from inadequate/failed processes, people, systems, or external events.

### Categories
1. **People Risk**: Fraud, misconduct, incompetence, turnover
2. **Process Risk**: Inefficient processes, control failures, documentation
3. **Systems Risk**: IT failures, cyber attacks, obsolete systems
4. **External Risk**: Vendor failures, legal/regulatory, natural disasters
5. **Compliance Risk**: Violation of regulations, policies
6. **Reputational Risk**: Damage to brand/trust from various causes

### Loss Events
- **Internal Fraud**: Employee theft, unauthorized trading, embezzlement
- **External Fraud**: Fraud by external parties, cyber theft
- **Employment Practices & Workplace Safety**: Labor disputes, discrimination
- **Clients, Products & Business Practices**: Product defects, compliance failures
- **Damage to Physical Assets**: Natural disasters, terrorism, vandalism
- **Business Disruption & Systems Failures**: IT outages, data loss
- **Execution, Delivery & Process Management**: Failed transactions, reconciliation errors

### Metrics
- **Loss Frequency**: Number of loss events in period
- **Loss Severity**: Size/impact of each loss event
- **Operational Risk Charge**: Capital requirement for operational risk
- **Operational Risk Indicators (KRIs)**: Leading indicators of operational risk

## Liquidity Risk

### Definition
Risk that institution cannot meet cash obligations without incurring unacceptable losses.

### Types

#### Funding Liquidity Risk
Risk that funding needs cannot be met at all or at acceptable costs.

- **Deposit Volatility**: Unpredictable deposit withdrawals
- **Wholesale Funding Risk**: Access to money markets, repo markets
- **Maturity Mismatch**: Short-term funding, long-term assets
- **Rollover Risk**: Inability to refinance maturing debt

#### Market Liquidity Risk
Risk that positions cannot be liquidated at reasonable prices due to market conditions.

- **Bid-Ask Spread**: Cost of trading in illiquid markets
- **Market Impact**: Price movement from own trading
- **Fire Sale Loss**: Loss from forced liquidation
- **Correlation Breakdown**: Illiquidity spreads across assets

### Metrics
- **Liquidity Coverage Ratio (LCR)**: High-quality liquid assets / net cash outflows
- **Net Stable Funding Ratio (NSFR)**: Available stable funding / required stable funding
- **Liquidity Mismatch Ratios**: Funding gaps by time bucket
- **Days Sales Outstanding (DSO)**: Days to convert receivables to cash

## Concentration Risk

### Definition
Risk arising from excessive exposure to specific borrowers, sectors, geographies, or products.

### Dimensions
- **Single-Name Concentration**: Exposure to individual counterparties
- **Sector Concentration**: Exposure to specific industries
- **Geographic Concentration**: Exposure to specific regions/countries
- **Product Concentration**: Exposure to specific product types
- **Collateral Concentration**: Heavy reliance on specific collateral types
- **Funding Concentration**: Dependence on specific funding sources

### Metrics
- **Concentration Ratio**: Top N counterparties as % of portfolio
- **Herfindahl Index**: Sum of squared portfolio weights
- **Limit Utilization**: Exposure as % of limit
- **Correlation-Adjusted Exposure**: Exposure adjusted for default correlations

## Interest Rate Risk in Banking Book

### Definition
Risk that interest rate changes reduce net interest income and equity.

### Components
- **Repricing Risk**: Assets/liabilities reprice at different rates
- **Yield Curve Risk**: Changes in yield curve shape
- **Basis Risk**: Different basis point moves across products
- **Optionality Risk**: Embedded options (prepayment, early withdrawal)

### Metrics
- **Interest Rate Sensitivity**: Change in NII for parallel rate shift
- **Duration Gap**: Difference between asset/liability durations
- **Key Rate Duration**: Sensitivity to specific points on yield curve
- **Economic Value of Equity (EVE)**: Change in equity from rate changes

## Regulatory & Compliance Risk

### Definition
Risk of penalties, fines, or business loss from non-compliance with regulations.

### Areas
- **Regulatory Capital**: Insufficient capital ratios
- **Anti-Money Laundering (AML)**: Failure to prevent money laundering
- **Know Your Customer (KYC)**: Inadequate customer identification
- **Data Protection**: Privacy violations, GDPR non-compliance
- **Consumer Protection**: Unfair lending, disclosure violations
- **Sanctions**: Transactions with sanctioned parties

### Metrics
- **Regulatory Capital Ratios**: CET1, Tier 1, Total CAR
- **Compliance Exceptions**: Number of control failures
- **Audit Findings**: Internal and external audit observations
- **Regulatory Correspondence**: Regulatory inquiries and responses

## Reputational Risk

### Definition
Risk of damage to brand/trust from negative events or perceptions.

### Sources
- **Operational Failures**: Service disruptions, data breaches
- **Misconduct**: Employee fraud, compliance violations
- **Product Issues**: Product failures, poor outcomes
- **Market Events**: Participation in controversial activities
- **Social/Environmental**: ESG concerns, environmental damage
- **Media/Public Opinion**: Negative press, social media

### Mitigation
- **Strong Governance**: Transparent policies and decision-making
- **Customer Service**: Prompt resolution of customer issues
- **Stakeholder Communication**: Clear communication with regulators, investors
- **ESG Focus**: Commitment to ethical practices
- **Crisis Management**: Prepared response to reputational events

## Interconnections

### Credit-Market Risk
Counterparty exposure in derivatives creates credit risk that increases with market moves.

### Liquidity-Credit Risk
Credit events can trigger liquidity crises due to funding market stress.

### Market-Operational Risk
Market stress can trigger operational failures (systems, processes) under high load.

### Concentration-All Risks
Concentration amplifies impact of other risks - defaults hit harder, market moves worse, etc.

## Risk Aggregation

Risks must be aggregated at portfolio, business unit, and enterprise levels:
- **Standalone Risk**: Individual risk component
- **Diversification Benefit**: Reduction from correlations across risks
- **Risk-Adjusted Return (RAROC)**: Return above risk-free rate per unit of risk
- **Capital Allocation**: Distribution of capital across risks and business units
