# Risk Management Expert

## Overview
This skill provides expert-level guidance on financial risk management, including quantitative modeling, stress testing, regulatory capital requirements, and portfolio risk analysis. It covers credit risk, market risk, operational risk, and liquidity risk across banking, trading, and investment sectors.

## Core Competencies

### 1. Quantitative Risk Modeling
- **Credit Risk Models**: Probability of Default (PD), Loss Given Default (LGD), Exposure at Default (EAD)
- **Value at Risk (VaR)**: Historical simulation, parametric, and Monte Carlo approaches
- **Credit Scoring**: Logistic regression, machine learning, behavioral scoring
- **Risk Metrics**: Expected Loss (EL), Unexpected Loss (UL), Risk-Adjusted Return on Capital (RAROC)

### 2. Stress Testing & Scenario Analysis
- **Stress Testing Frameworks**: Historical, hypothetical, and reverse stress testing
- **Scenario Analysis**: Macroeconomic scenarios, geopolitical events, market shocks
- **Extreme Value Theory (EVT)**: Tail risk estimation and modeling
- **Reverse Stress Testing**: Identifying business model vulnerabilities

### 3. Regulatory Capital
- **Basel III Framework**: Pillar 1 (minimum capital), Pillar 2 (supervisory review), Pillar 3 (market discipline)
- **Capital Adequacy Ratio (CAR)**: Calculation, components, regulatory requirements
- **Internal Models Approach (IMA)**: Advanced approaches for credit and market risk
- **Counterparty Credit Risk**: CCR charges, CVA, IMM

### 4. Credit Risk Management
- **Credit Analysis**: Fundamental and behavioral assessment
- **Credit Limits**: Portfolio limits, single-name limits, sector limits
- **Collateral Management**: Haircuts, recovery rates, netting agreements
- **Probability of Default**: Structural models, reduced-form models, empirical approaches

### 5. Market Risk Management
- **VAR Calculation**: Delta-normal, historical simulation, Monte Carlo
- **Greeks & Sensitivities**: Delta, gamma, vega, theta risk factors
- **Interest Rate Risk**: DV01, key rate durations, basis risk
- **Correlation & Concentration**: Dependency modeling, concentration metrics

### 6. Operational Risk
- **Operational Risk Framework**: People, process, systems, external risks
- **Loss Data Collection**: Historical loss analysis, scenario analysis
- **Risk Indicators**: KPIs for operational risk monitoring
- **Capital Allocation**: Basic Indicator Approach, Standardized Approach

### 7. Liquidity Risk
- **Liquidity Coverage Ratio (LCR)**: High-quality liquid assets, net cash outflows
- **Net Stable Funding Ratio (NSFR)**: Available vs. required stable funding
- **Liquidity Buffers**: Stress liquidity buffers, contingency funding plans
- **Intra-day Liquidity**: Real-time liquidity monitoring

### 8. Risk Governance
- **Risk Governance Structure**: Board, ALCO, risk committees
- **Risk Policies**: Credit, market, operational, liquidity risk policies
- **Model Risk Management**: Model validation, approval, monitoring
- **Risk Reporting**: Dashboards, KRIs, escalation procedures

## Use Cases

1. **Credit Risk Modeling**: Build PD/LGD/EAD models, calculate expected loss, price credit products
2. **Portfolio Risk Assessment**: Calculate VaR, stress test portfolios, identify concentration
3. **Capital Planning**: Calculate minimum capital ratios, optimize capital allocation
4. **Risk Monitoring**: Real-time risk dashboards, limit monitoring, KRI tracking
5. **Regulatory Reporting**: Generate risk reports, submit to regulators, manage compliance
6. **Model Validation**: Backtesting, sensitivity analysis, model governance
7. **Stress Testing**: Historical scenarios, hypothetical scenarios, reverse stress tests

## Key Frameworks & Standards

- **Basel III/IV**: International regulatory framework for banking
- **CCAR/DFAST**: Capital stress testing for large banks
- **EBA Guidelines**: European regulatory guidelines
- **GARP Standards**: Global Association of Risk Professionals standards
- **Dodd-Frank Act**: Post-crisis regulation in the US
- **IFRS 9**: Loan loss provisioning standards

## Technical Skills

- **Statistical Methods**: Regression analysis, classification models, survival analysis
- **Optimization**: Portfolio optimization, capital allocation optimization
- **Simulation**: Monte Carlo simulation, scenario generation
- **Data Engineering**: Data pipelines, quality assurance, governance
- **Visualization**: Risk dashboards, stress testing results
- **Tools**: Python (pandas, numpy, scikit-learn), R, SQL, Excel VBA

## Technology Stack

### Languages & Frameworks
- **Python**: Pandas, NumPy, scikit-learn for model development
- **R**: QuantLib, lattice, survival analysis packages
- **SQL**: Data aggregation, feature engineering, reporting
- **VBA/Excel**: Quick calculations, legacy systems
- **C++**: High-performance risk calculations
- **Java**: Enterprise risk systems and integration

### Risk Management Tools
- **Risk Platforms**: MSCI RiskManager, Axioma, Bloomberg PORT
- **Data Management**: Alteryx, Informatica, custom ETL
- **Visualization**: Tableau, Power BI, Grafana
- **Statistical Tools**: STATA, SAS, Python ML libraries
- **Backtesting**: QuantConnect, Backtrader, custom frameworks

## Risk Modeling Deep Dive

### Credit Risk Models
- **Structural Models**: Merton-based default probability estimation
- **Reduced-Form Models**: Intensity-based default modeling
- **Empirical Models**: Machine learning approaches using transaction history
- **PD Calibration**: Through-the-cycle vs point-in-time adjustments
- **LGD Estimation**: Recovery rate modeling and collateral valuation
- **EAD Calculation**: Exposure forecasting for derivatives and credit lines
- **Portfolio Credit Risk**: Correlated default modeling, concentration metrics

### Market Risk Models
- **VaR Calculation Methods**: Parametric (delta-normal), historical, Monte Carlo
- **Parametric VaR**: Assumes normal distribution, sensitive to volatility estimates
- **Historical VaR**: Non-parametric, uses historical returns as scenarios
- **Monte Carlo VaR**: Flexible, computationally intensive, accurate for derivatives
- **Expected Shortfall**: Captures tail risk beyond VaR
- **Stress Testing**: Historical and hypothetical scenarios
- **Greeks Calculation**: Delta, gamma, vega, theta, rho for derivatives

### Operational Risk Models
- **Scenarios-Based**: Expert elicitation of extreme loss events
- **Loss Distribution Approach (LDA)**: Statistical modeling of loss frequency and severity
- **Key Risk Indicators (KRIs)**: Early warning indicators of emerging risks
- **Control Self-Assessment (CSA)**: Internal evaluation of control effectiveness
- **Risk Maps**: Heatmaps showing likelihood and impact

## Risk Management Frameworks

### Pre-Trade Risk Management
- Order validation and pre-trade limit checks
- Exposure aggregation across accounts and traders
- Margin requirement calculation
- Stop-loss and kill-switch mechanisms
- Counterparty credit limits

### Post-Trade Risk Management
- Position reconciliation and settlement
- Mark-to-market valuation
- MTM P&L monitoring
- Counterparty exposure tracking
- Collateral management and optimization

### Limit Monitoring
- Single-name concentration limits
- Sector limits and diversification
- Regional exposure limits
- Counterparty credit limits
- Liquidity limits
- VaR/Expected Shortfall limits
- Greeks limits for derivatives

## Best Practices

### Model Development
1. **Data Quality**: Ensure accurate, complete, and timely data
2. **Feature Selection**: Relevant features that drive risk predictions
3. **Model Validation**: Backtesting, stress testing, sensitivity analysis
4. **Documentation**: Clear documentation of assumptions and methodology
5. **Independence Review**: Third-party validation and challenge
6. **Governance Approval**: Model governance framework for model approval
7. **Monitoring**: Continuous monitoring of model performance and recalibration

### Risk Governance
1. **Three Lines of Defense**: Business units, risk function, internal audit
2. **Independent Risk Function**: Separate from business lines
3. **Board Oversight**: Risk committee oversight and board reporting
4. **Risk Policies**: Clear risk policies and procedures
5. **Escalation Procedures**: Clear escalation for limit breaches
6. **Committee Structure**: ALCO, risk committee, credit committee
7. **Regular Reporting**: Daily/weekly/monthly risk reporting

### Regulatory Compliance
1. **Basel III Implementation**: Capital requirement calculations
2. **Regulatory Reporting**: Timely and accurate regulatory submissions
3. **Documentation**: Complete documentation for examiner review
4. **Model Validation**: Internal review and external validation
5. **Stress Testing**: CCAR/DFAST compliance for large banks
6. **IFRS 9 Compliance**: Expected credit loss provisioning

## Learning Resources

This skill includes:
- **Reference Materials**: 15 comprehensive reference guides on all risk topics
- **Practical Guides**: 15 step-by-step guides for implementing risk processes
- **Code Examples**: 20 Python implementations of key risk calculations and models
- **Best Practices**: Industry standards, regulatory requirements, implementation tips
- **Case Studies**: Real-world examples of risk management implementations
- **Regulatory Documents**: Basel III, CCAR, IFRS 9, MiFID II requirements

## Typical Questions Answered

1. How do I calculate VaR for a portfolio using different methods?
2. What's the difference between parametric, historical, and Monte Carlo VaR?
3. How do I build a credit scoring model for mortgage origination?
4. What's the proper way to stress test a credit portfolio under recession?
5. How do I calculate capital requirements under Basel III/IV framework?
6. What are the key drivers of concentration risk and how to measure it?
7. How do I implement limit monitoring and escalation procedures?
8. What's the best approach for PD/LGD/EAD modeling in retail?
9. How do I validate a risk model through backtesting?
10. How do I set up a comprehensive risk governance framework?
11. How do I handle model risk in alternative assets?
12. What's the appropriate stress testing methodology for my organization?

## Performance Metrics & Benchmarks

### Model Performance
- **Accuracy**: Prediction accuracy and classification metrics
- **Discrimination**: ROC/AUC for binary classification models
- **Calibration**: Predicted vs actual default rates
- **Stability**: Consistent performance across time periods
- **Backtesting**: VaR exceptions at appropriate frequency

### Risk Reporting Metrics
- **Capital Ratios**: CET1, Tier 1, Total Capital ratios
- **VaR**: Daily VaR and limit utilization
- **Concentration**: Top counterparty exposure, sector concentration
- **Liquidity**: LCR, NSFR, liquidity gap analysis
- **Stress Tests**: Scenario outcomes and capital impact

## Success Criteria

- Accurate risk quantification with proper confidence intervals
- Compliant regulatory reporting and capital calculations
- Comprehensive stress testing covering tail risks and edge cases
- Effective governance and policy frameworks with clear accountability
- Clear risk communication and escalation procedures
- Continuous model validation, improvement, and model governance
- Real-time risk monitoring and proactive limit management
- Executive-ready dashboards and reporting

## When to Engage This Skill

Use this skill when you need to:
- Design and implement risk management systems
- Develop quantitative risk models (credit, market, operational)
- Calculate regulatory capital requirements
- Conduct stress testing and scenario analysis
- Build risk governance frameworks
- Create risk dashboards and reporting
- Validate and audit existing risk models
- Implement limit monitoring systems
- Manage counterparty credit risk
- Perform portfolio risk analysis
- Ensure regulatory compliance for risk management

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Domain**: Risk Management & Quantitative Modeling
**Expertise Level**: Elite Professional
