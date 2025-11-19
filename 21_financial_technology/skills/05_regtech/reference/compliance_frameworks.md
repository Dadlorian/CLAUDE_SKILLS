# Compliance Frameworks and Models

## Risk-Based Approach Framework

### Definition
A compliance methodology that allocates resources based on identified risks, rather than applying uniform procedures to all customers.

### Risk Assessment Components

```
Customer Risk Profile = f(
  Customer_Type_Risk,
  Geographic_Risk,
  Business_Type_Risk,
  Transaction_Profile_Risk,
  Behavioral_Risk,
  Beneficial_Ownership_Risk
)

Risk Score Range: 0-100
├── 0-25: Low Risk
├── 25-50: Medium Risk
├── 50-75: High Risk
└── 75-100: Very High Risk
```

### Risk Factors

#### Customer Type
```
INDIVIDUALS:
├── Risk: Low to Medium (generally)
├── Considerations: Occupation, wealth source, complexity
└── EDD: If high-profile position or complex structures

SMALL BUSINESSES:
├── Risk: Low to Medium
├── Considerations: Business type, owners, cash intensity
└── EDD: Trade-based ML indicators

MEDIUM ENTERPRISES:
├── Risk: Medium
├── Considerations: Industry, ownership, operations
└── EDD: When ownership structure complex

LARGE CORPORATIONS:
├── Risk: Medium to High (complexity)
├── Considerations: Multiple entities, jurisdictions, ownership
└── EDD: Standard for significant structures

NON-PROFITS:
├── Risk: Medium
├── Considerations: Funding sources, governance, mission
└── EDD: For international funding sources

FINANCIAL INSTITUTIONS:
├── Risk: Low to Medium
├── Considerations: Regulation, oversight, systems
└── EDD: For correspondent banking relationships
```

#### Geographic Risk
```
Very High Risk Jurisdictions:
├── OFAC Embargoed Countries
├── Non-Cooperative Jurisdictions (NCCT designation)
├── High Corruption Index Countries
├── Weak AML/CFT Regime
├── High Terrorist Financing Risk
└── Examples: Iran, North Korea, Syria, Yemen

High Risk Jurisdictions:
├── Significant AML/CFT Deficiencies
├── Major Corruption Issues
├── Weak Political Stability
├── Significant Money Laundering Prevalence
├── FATF Gray List Jurisdictions
└── Examples: Pakistan, Nigeria, Mexico, Russia

Medium Risk Jurisdictions:
├── Developing AML/CFT Systems
├── Moderate Corruption Issues
├── Emerging Market Volatility
├── Limited Transparency
└── Examples: India, Brazil, Southeast Asian countries

Low Risk Jurisdictions:
├── Strong AML/CFT Regime
├── Low Corruption Index
├── Political Stability
├── FATF White List
└── Examples: Canada, Australia, Scandinavia
```

#### Industry Risk
```
HIGH RISK INDUSTRIES:
├── Trade-Based Money Laundering Risk:
│   ├── Precious metals & gems
│   ├── Import/export businesses
│   ├── Antiques & art dealers
│   └── Real estate (especially cash)
├── Cash Intensive:
│   ├── Casinos & gambling
│   ├── Money transfer services
│   ├── Restaurants & retail
│   └── Hotels & hospitality
└── Financial Services:
    ├── Money lenders
    ├── Forex dealers
    ├── Cryptocurrency exchanges
    └── Virtual asset service providers (VASPs)

MEDIUM RISK INDUSTRIES:
├── Insurance
├── Securities
├── Professional services
├── Manufacturing (international)
└── Transportation & logistics

LOW RISK INDUSTRIES:
├── Utilities
├── Healthcare
├── Education
├── Government services
└── Non-profits (domestic)
```

## Basel III/IV Compliance Framework

### Key Pillars

#### Pillar 1: Minimum Capital Requirements
- Common Equity Tier 1 (CET1): 4.5% minimum
- Tier 1 Capital: 6% minimum
- Total Capital: 8% minimum
- Countercyclical buffer: 0-2.5%
- Systemic importance buffer: 0-3.5%

#### Pillar 2: Supervisory Review
- Internal capital adequacy assessment
- Regulatory stress testing
- Supervisory examination
- Prompt corrective action
- Capital planning requirements

#### Pillar 3: Market Discipline
- Public capital adequacy disclosure
- Risk management transparency
- Standardized risk metrics
- Liquidity ratio disclosure
- Leverage ratio publication

### Compliance Requirements
1. Capital calculation and reporting
2. Risk-weighted asset determination
3. Internal models validation
4. Stress testing execution
5. Supervisory reporting
6. Public disclosure

## FATF (Financial Action Task Force) Framework

### 40 + 9 Recommendations

```
LEGAL SYSTEMS (Recommendations 1-3)
├── Money Laundering Offense
├── Terrorist Financing Offense
└── Proceeds of Crime Seizure

INSTITUTIONAL/OPERATIONAL FRAMEWORKS (4-15)
├── AML/CFT Policies & Coordination
├── Financial Intelligence Unit
├── Law Enforcement Cooperation
├── Reporting Entities Designation
├── Customer Due Diligence
├── Enhanced Due Diligence
├── Beneficial Ownership Transparency
├── Enhanced Due Diligence (PEPs)
├── Record Keeping
├── Reporting Obligations
├── Sanctions Compliance
├── Politically Exposed Persons
├── Correspondent Banking
└── Wire Transfer Rules

PREVENTIVE MEASURES (16-22)
├── Customer Due Diligence
├── Enhanced Due Diligence
├── Enhanced Measures for High-Risk
├── Simplified Due Diligence
├── Ongoing Customer Monitoring
├── PEP Screening
└── Beneficial Ownership

TRANSPARENCY/BENEFICIAL OWNERSHIP (23-25)
├── Beneficial Ownership Registers
├── Transparency of Legal Persons
└── Legal Arrangements Transparency

SANCTIONS (26-34)
├── Financial Sanctions (AML/CFT)
├── Asset Freezing Requirements
├── Targeted Financial Sanctions (TFS)
├── De-risking
├── Correspondent Banking
└── Wire Transfer Rules

MONEY LAUNDERING/TERRORIST FINANCING OFFENSES (35-40)
├── Confiscation & Remedies
├── Money Laundering Offense
├── Terrorist Financing Offense
├── Cross-Border Transport Disclosure
└── Penalties

COMBATING TERRORIST FINANCING (9 recommendations)
├── Terrorist Financing Designation
├── Financial Investigations
├── International Cooperation
├── Havala/IVTS Regulation
└── NGO Oversight
```

## Dodd-Frank Act Framework

### Key Provisions

#### 1. Consumer Protection (Title X)
- Consumer Financial Protection Bureau (CFPB)
- Fair lending enforcement
- Data security requirements
- Complaint handling procedures

#### 2. Prudential Supervision (Titles I, VII, XI)
- Systemically Important Financial Institutions (SIFIs)
- Bank Holding Company Regulations
- Enhanced Capital Requirements
- Liquidity Standards
- Stress Testing Requirements

#### 3. Volcker Rule (Section 619)
- Proprietary Trading Restrictions
- Fund Investment Limitations
- Covered Fund Restrictions
- Compliance Programs
- Testing and Monitoring

#### 4. Derivatives Regulation (Titles VII, VIII)
- Central Clearing Requirements
- Exchange Trading Requirements
- Swap Dealer Registration
- Position Limits
- Margin Requirements

#### 5. Whistleblower Programs (Section 922)
- Monetary Awards (10-30% of sanctions)
- Confidential Submission
- Protection from Retaliation
- Anti-Retaliation Provisions

## MiFID II/IFD Framework

### Client Classification

```
Professional Client:
├── Per se: Large enterprises, government, central banks
├── Elective: Institutional investors meeting criteria
├── Criteria: Two of three:
│   ├── Balance sheet > €20M
│   ├── Annual turnover > €40M
│   └── Professional staff > 250

Retail Client:
├── Default classification
├── Higher protections required
├── Reduced disclosure requirements

Counterparties:
├── Qualified counterparties
├── Eligible counterparties
├── Exemptions possible
```

### Conduct of Business Requirements
1. Information and transparency
2. Best execution
3. Conflict of interest management
4. Suitability and appropriateness
5. Client communication
6. Securities financing disclosures

## GDPR Compliance Framework

### Core Principles

#### 1. Lawfulness, Fairness, Transparency
- Legal basis for processing
- Fair and transparent processing
- Clear privacy notices

#### 2. Purpose Limitation
- Specific, explicit, legitimate purposes
- No incompatible further processing
- Exception: Fraud prevention, legal claims

#### 3. Data Minimization
- Only necessary personal data collected
- Limited scope of processing
- Proportionate to purpose

#### 4. Accuracy
- Accurate and current personal data
- Reasonable steps to correct
- Erasure of inaccurate data

#### 5. Storage Limitation
- Retention for no longer than necessary
- Differential retention by purpose
- Legal retention requirements

#### 6. Integrity and Confidentiality
- Secure processing
- Appropriate technical measures
- Data breach notification (72 hours)

#### 7. Accountability
- Data Processing Agreements
- Privacy Impact Assessments
- Records of processing
- Transparency to supervisors

### Key Compliance Activities
1. Data Inventory & Mapping
2. Legal Basis Documentation
3. Privacy Impact Assessments
4. Data Subject Rights Processes
5. Breach Notification Procedures
6. Third-Party Audits
7. Annual Compliance Review

## CCPA/CPRA Framework

### Consumer Rights
- Right to Know: What personal information is collected
- Right to Delete: Deletion of personal information
- Right to Opt-Out: Third-party data sales
- Right to Non-Discrimination: Equal service for exercising rights
- Right to Correct: Correction of inaccurate information (CPRA)

### Business Obligations
1. Privacy Policy Transparency
2. Data Minimization
3. Security Requirements
4. Vendor/Service Provider Agreements
5. Opt-Out Mechanisms
6. Data Broker Registration
7. Retention Limitations

## Compliance Control Framework

```
Compliance Control Hierarchy:

PREVENTIVE CONTROLS (First Line of Defense)
├── Customer Screening
├── Transaction Monitoring
├── Documentation Requirements
├── Training Programs
└── Policy Implementation

DETECTIVE CONTROLS (Second Line of Defense)
├── Internal Audit Reviews
├── Compliance Monitoring
├── Exception Reporting
├── Alert Investigation
└── Case Management

CORRECTIVE CONTROLS (Third Line of Defense)
├── Regulatory Reporting
├── Remediation Actions
├── Staff Discipline
├── System Changes
└── Enhanced Due Diligence
```

## Compliance Culture & Governance

### Three Lines of Defense Model
1. **First Line**: Operational management and staff
2. **Second Line**: Compliance and risk functions
3. **Third Line**: Internal and external auditors

### Key Governance Elements
- Board-level compliance oversight
- Dedicated compliance officer
- Clear escalation procedures
- Documented policies and procedures
- Regular training and certifications
- Performance metrics and KPIs
- Regulatory examination preparation
- Incident response procedures

## Benchmark Compliance Metrics

| Framework | Key Metric | Target | Frequency |
|-----------|-----------|--------|-----------|
| KYC | Coverage Rate | 100% | Quarterly |
| AML | SAR Filing Rate | 2-5% of alerts | Monthly |
| Sanctions | Screening Accuracy | > 99% | Real-time |
| Transaction Monitoring | False Positive Rate | < 10% | Weekly |
| GDPR | Data Breach Response | < 72 hours | As-needed |
| FATF | Risk Assessment Update | Annual | Quarterly |
