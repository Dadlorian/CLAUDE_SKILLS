# Banking Regulations and Compliance

## Global Regulatory Framework

### United States Regulations

#### Dodd-Frank Wall Street Reform Act (2010)
- **Purpose**: Prevent financial crisis recurrence
- **Key Provisions**:
  - Consumer protection and financial stability
  - Capital and liquidity requirements
  - Systemic risk designation for large institutions
  - Volcker Rule (proprietary trading restrictions)
  - Derivatives regulation and central clearing
- **Regulatory Bodies**: Fed, FDIC, OCC, CFTC, SEC

#### Regulation E (Electronic Funds Transfers)
- **Scope**: Protects consumers in electronic fund transfers
- **Coverage**: ATM, debit cards, ACH, online banking
- **Requirements**:
  - Clear disclosure of terms
  - Error resolution procedures
  - Dispute resolution timelines
  - Liability limits for unauthorized transfers

#### Regulation Z (Truth in Lending)
- **Purpose**: Ensures clear credit disclosure
- **Coverage**: Mortgages, auto loans, credit cards
- **Requirements**:
  - APR disclosure
  - Finance charges
  - Annual percentage rate comparisons
  - Truth in advertising

#### Bank Secrecy Act (BSA) and Anti-Money Laundering (AML)
- **Purpose**: Prevent money laundering and financial crimes
- **Key Requirements**:
  - Know Your Customer (KYC) procedures
  - Customer Due Diligence (CDD)
  - Suspicious Activity Reports (SAR)
  - Currency Transaction Reports (CTR)
  - Sanctions screening and OFAC compliance
- **Penalties**: Up to $100,000+ per violation

#### Fair Credit Reporting Act (FCRA)
- **Purpose**: Regulate credit reporting and consumer information
- **Requirements**:
  - Proper use of credit reports
  - Accuracy verification
  - Dispute resolution procedures
  - Adverse action notices
  - Credit score disclosure

#### Gramm-Leach-Bliley Act (GLBA)
- **Purpose**: Privacy and data protection
- **Requirements**:
  - Privacy notices to customers
  - Opt-out mechanisms for information sharing
  - Physical and electronic security measures
  - Employee training and certification
  - Breach notification requirements

#### Community Reinvestment Act (CRA)
- **Purpose**: Ensure fair lending and community banking
- **Requirements**:
  - Fair lending practices
  - Community development lending
  - Service to all populations
  - Monitoring and reporting

### European Union Regulations

#### Payment Services Directive 2 (PSD2)
- **Scope**: Regulation of payment services in EU
- **Key Requirements**:
  - **Open Banking**: Access to account data via APIs
  - **Strong Customer Authentication (SCA)**: Multi-factor auth required
  - **Account Information Services (AIS)**: Third-party data access
  - **Payment Initiation Services (PIS)**: Third-party payment initiation
  - **Transparency Requirements**: Clear fee disclosure
  - **PSD2 Compliance**: Separate authentication per transaction
- **Timeline**: Implementation by end of 2025

#### General Data Protection Regulation (GDPR)
- **Scope**: Data protection for EU residents
- **Key Requirements**:
  - **Consent**: Explicit opt-in for data collection
  - **Data Minimization**: Collect only necessary data
  - **Right to Access**: Customers can request their data
  - **Right to Erasure**: "Right to be forgotten"
  - **Data Portability**: Customers can export their data
  - **Privacy by Design**: Build privacy into systems
  - **Breach Notification**: Notify within 72 hours
- **Penalties**: Up to €20M or 4% of revenue

#### Markets in Crypto-Assets Regulation (MiCA)
- **Scope**: Crypto asset service providers
- **Requirements**:
  - Wallet providers must be authorized
  - Stablecoin issuers regulated
  - Custody requirements
  - AML/KYC obligations
  - Operational resilience

#### Markets in Financial Instruments Directive 2 (MiFID II)
- **Scope**: Securities trading and investment services
- **Requirements**:
  - Investor protection
  - Market transparency
  - Best execution requirements
  - Transaction reporting
  - Conduct of business rules

### United Kingdom Regulations

#### FCA Senior Managers Regime (SMR)
- **Scope**: Accountability of senior management
- **Requirements**:
  - Individual accountability for decisions
  - Criminal liability for reckless management
  - Certification regime for key staff
  - Fitness and propriety tests
  - Regular training and competency

#### Open Banking Standard
- **Purpose**: API-based banking for UK
- **Requirements**:
  - API access to account and transaction data
  - Payment initiation capabilities
  - Third-party integration support
  - Security standards (MTLS, OAuth)
  - Customer authentication

## Capital Requirements

### Basel III Framework
Global banking standard for capital adequacy

#### Capital Tiers
```
Tier 1 Capital (Core Capital)
├── Common Equity Tier 1 (CET1): 4.5% minimum
└── Tier 1: 6% minimum

Tier 2 Capital
└── Total Capital: 8% minimum + 2.5% buffer

Additional Capital Buffers
├── Capital Conservation Buffer: 2.5%
├── Cyclical Buffer: 0-2.5%
├── Systemic Risk Buffer: 1%+
└── G-SIB surcharge: 1-3.5%
```

#### Risk-Weighted Assets (RWA)
```
Calculation:
Capital Ratio = Capital / Risk-Weighted Assets

Risk Weights (Examples):
├── Cash: 0% weight
├── Government securities: 0-100%
├── Customer loans: 35-150%
└── Equities: 100-150%
```

## Liquidity Requirements

### Liquidity Coverage Ratio (LCR)
```
Formula: High-Quality Liquid Assets / Net Cash Outflows ≥ 100%

High-Quality Liquid Assets:
├── Level 1 (unrestricted): Cash, government bonds
└── Level 2 (up to 40%): Corporate bonds, equities

Net Cash Outflows (30-day stress scenario):
├── Retail deposit outflows
├── Wholesale funding outflows
└── Derivative and contingent outflows
```

### Net Stable Funding Ratio (NSFR)
```
Formula: Available Stable Funding / Required Stable Funding ≥ 100%

Ensures adequate medium/long-term funding
Applies to 1-year horizon
Prevents over-reliance on short-term wholesale funding
```

## KYC/AML Compliance

### Know Your Customer (KYC)

#### Customer Identification Program (CIP)
```
Required Information:
├── Name
├── Date of birth
├── Address
├── Identification document (ID/passport)
└── Verification of identity

Verification Methods:
├── Documentary evidence
├── Non-documentary evidence
├── Combination approach
```

#### Customer Due Diligence (CDD)
```
Required Information:
├── Source of funds/wealth
├── Nature and purpose of account
├── Business activities
├── Beneficial ownership (>25%)
└── Risk categorization

Timing:
├── Completed before account opening
├── May continue after account opening
└── Updated periodically
```

#### Enhanced Due Diligence (EDD)
```
For High-Risk Customers:
├── Politically exposed persons (PEPs)
├── Non-resident aliens
├── Correspondent banking
├── Unusual transaction patterns
├── Higher-risk jurisdictions

Additional Information Required:
├── Detailed source of funds verification
├── Enhanced beneficial ownership verification
├── Business purpose verification
└── Enhanced ongoing monitoring
```

### Anti-Money Laundering (AML)

#### Suspicious Activity Reports (SAR)
```
Triggers for SAR Filing:
├── Transactions >$5,000 matching suspicious patterns
├── Structuring to avoid reporting thresholds
├── Unusual account activity
├── Known criminal involvement
├── Sanction list matches

Filing Requirements:
├── File within 30 days of detection
├── Report to FinCEN
├── Maintain confidentiality (no tipping off)
├── Retain records 5 years
```

#### Currency Transaction Reports (CTR)
```
Triggers:
├── Transactions >$10,000 in currency
├── Include all related transactions same day
├── Include currency purchase patterns
└── Multiple transactions by same customer

Reporting:
├── File with FinCEN
├── File within 15 days
├── Include customer identification
└── Retain 5 years
```

#### Sanctions Compliance (OFAC)
```
Requirements:
├── Screen all customers against OFAC lists
├── SDN (Specially Designated Nationals) list
├── HQA (Historically Targeted Agencies) list
├── Screen ongoing transactions
├── Block sanctioned transaction attempts
├── Report blocking to OFAC

Failure Penalties:
├── Per violation: up to $20,000+
├── Criminal penalties: up to $1M+ and imprisonment
└── Reputational damage
```

## Consumer Protection

### Fair Lending Requirements
```
Prohibitions:
├── Discrimination based on protected characteristics
│   ├── Race, color, religion
│   ├── National origin
│   ├── Sex, marital status
│   └── Age, disability
├── Redlining (geographic discrimination)
├── Disparate treatment
└── Disparate impact

Compliance Measures:
├── Written lending policies
├── Training programs
├── Monitoring and testing
├── Record keeping
└── Self-assessment and audits
```

### Truth in Lending Requirements
```
Mortgage Disclosures:
├── Loan Estimate (within 3 days of application)
├── Closing Disclosure (3 days before closing)
└── Annual disclosure updates

Required Information:
├── Loan terms
├── Annual percentage rate (APR)
├── Finance charges
├── Payment schedule
└── Prepayment penalties
```

## Operational Resilience

### Business Continuity and Disaster Recovery
```
Requirements:
├── Business continuity plans
├── Disaster recovery procedures
├── Regular testing (at least annually)
├── Recovery time objectives (RTO)
├── Recovery point objectives (RPO)
├── Offsite backup and recovery facilities
├── Third-party vendor resilience
└── Communication procedures
```

### Cybersecurity Requirements
```
Controls Required:
├── Access controls and authentication
├── Encryption (in transit and at rest)
├── Network segmentation
├── Intrusion detection/prevention
├── Malware protection
├── Vulnerability management
├── Incident response procedures
├── Audit logging and monitoring
└── Regular security testing
```

## Regulatory Reporting

### Call Reports (FFIEC)
- **Frequency**: Quarterly
- **Contents**: Balance sheet, income statement, capital ratios
- **Scope**: All insured depository institutions
- **Public Availability**: Published for transparency

### Stress Testing
- **Frequency**: Annual (at minimum)
- **Requirement**: Stress test capital adequacy
- **Scenarios**: Adverse economic scenarios
- **Result**: Report to regulators (Federal Reserve)

### Regulatory Filings
```
Common Reports:
├── Quarterly Call Reports (Y-9C for holding companies)
├── Annual Consolidated Financial Statements (10-K)
├── Quarterly SEC Filings (10-Q)
├── AML Suspicious Activity Reports (SARs)
├── Currency Transaction Reports (CTRs)
├── Liquidity Coverage Ratio (LCR) reporting
├── Net Stable Funding Ratio (NSFR) reporting
└── Consumer Complaint Database submissions
```

## Regulatory Examination

### Examination Process
```
Phases:
├── Pre-Examination Planning
│   ├── Scoping and risk assessment
│   └── Document requests
│
├── Examination
│   ├── On-site review
│   ├── Document review
│   ├── Interviews
│   └── Testing and sampling
│
├── Findings and Recommendations
│   ├── Issues identified
│   ├── Severity rating
│   ├── Recommendations
│   └── Manager discussion
│
└── Follow-Up
    ├── Corrective action plans
    ├── Timeline for remediation
    └── Subsequent examination verification
```

### Regulatory Ratings (CAMELS)
```
Rating Categories:
C - Capital Adequacy
A - Asset Quality
M - Management Quality
E - Earnings
L - Liquidity
S - Sensitivity to Market Risk

Ratings: 1 (Strong) to 5 (Critical)
Composite Rating: 1-5 (lower is better)
Rating 1-2: Well-capitalized and sound
Rating 3: Satisfactory with concerns
Rating 4-5: Significant concerns, may require action
```

## Enforcement Actions

### Enforcement Remedies
```
Available to Regulators:
├── Warning letters
├── Cease and desist orders
├── Removal and prohibition orders
├── Civil money penalties
├── Restitution to customers
├── Consent orders with conditions
├── Charter revocation (ultimate penalty)
└── Criminal referrals
```

### Penalties
```
Civil Penalties:
├── Per violation: $1,000-$25,000+
├── For false/misleading statements: $5,000-$50,000+ per day
└── For discrimination: Actual damages + punitive damages

Criminal Penalties:
├── Imprisonment up to 30 years (for financial fraud)
├── Fines up to $1M+
└── Professional sanctions
```

## Compliance Program Elements

### Required Components
```
Effective Compliance Program:
├── Board and management oversight
├── Written policies and procedures
├── Designated compliance officer
├── Staff training and education
├── Independent audit and testing
├── Record keeping and documentation
├── Incident reporting procedures
├── Corrective action processes
└── Vendor management and oversight
```

## Emerging Regulatory Trends

### Real-Time Payments Regulation
- Instant payment service requirements
- Fraud and error handling in real-time context
- Consumer protection in instant payments
- International standards alignment

### Climate Risk Regulation
- Climate risk disclosure requirements
- Physical and transition risk assessment
- Portfolio climate risk analysis
- Scenario analysis and stress testing

### Algorithmic Accountability
- AI/ML fairness and bias testing
- Explainability requirements
- Human oversight requirements
- Regular validation and monitoring

## Conclusion
Banking regulations are extensive and constantly evolving. Financial institutions must maintain comprehensive compliance programs covering capital adequacy, liquidity, consumer protection, AML/KYC, lending practices, and operational resilience. Regular regulatory examinations and self-assessments ensure ongoing compliance with these requirements.
