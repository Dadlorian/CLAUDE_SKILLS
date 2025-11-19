# GDPR Compliance for Financial Services

## GDPR Basics for Financial Institutions

### Scope and Applicability

```
GEOGRAPHIC SCOPE:
├── Applies to all EU/EEA residents
├── EU establishment of organization
├── Offering services to EU residents
├── Monitoring behavior of EU residents
└── Extraterritorial application

PERSONAL DATA DEFINITION:
├── Any information relating to identified person
├── Identifiable person (directly or indirectly)
├── Name, ID number, location data
├── Factors specific to identity
├── Physical, physiological, genetic, mental, economic,
    cultural, or social identity
└── Financial account information

PROCESSING DEFINITION:
├── Any operation on personal data:
│   ├── Collection
│   ├── Recording
│   ├── Organization
│   ├── Structuring
│   ├── Storage
│   ├── Adaptation
│   ├── Retrieval
│   ├── Consultation
│   ├── Use
│   ├── Disclosure
│   ├── Erasure
│   └── Destruction
└── Can be automated or manual
```

### Key Concepts

```
CONTROLLER:
├── Determines purposes and means of processing
├── Typically: Financial institution
├── Responsible for compliance
├── Must implement safeguards
├── Liable for breaches
└── Must appoint DPO (if required)

PROCESSOR:
├── Processes data on behalf of controller
├── Typically: Third-party vendor
├── Bound by contract to follow controller instructions
├── Must implement technical/organizational measures
├── Liable for own breaches
└── Limited independent processing

DATA PROTECTION OFFICER (DPO):
├── Required if:
│   ├── Public authority/body
│   ├── Core activity is monitoring individuals
│   ├── Large-scale systematic monitoring
│   └── Some financial institutions
├── Responsibilities:
│   ├── Monitor GDPR compliance
│   ├── Cooperate with supervisory authority
│   ├── Point of contact for data subjects
│   ├── Assist with DPIAs
│   ├── Handle data breach notification
│   └── Provide compliance advice
└── Must be independent, cannot have conflicting roles
```

## Lawful Basis for Financial Services AML Processing

### Article 6(1)(c) - Legal Obligation

```
MOST RELEVANT FOR REGTECH:

Legal Basis: Law requires processing
Examples:
├── AML regulations require KYC
├── Sanctions laws require screening
├── CTR/SAR reporting requirements
├── FATCA/CRS reporting obligations
├── Beneficial ownership regulations
├── Transaction monitoring requirements
├── Regulatory examination cooperation
└── Law enforcement cooperation

Compliance Requirements:
├── Processing must be necessary
├── Must be proportionate to purpose
├── Data minimization still applies
├── Retention periods must be reasonable
├── Purpose cannot be exceeded
├── Must respect data subject rights (except erasure)
└── Transparency still required

Data Subject Rights Impact:
├── Limited right to erasure (competing obligation)
├── Right to access still applies
├── Right to correction still applies
├── Right to restriction still applies
├── Right to data portability still applies
├── Right to object with limitations
└── Right to human review still applies (with exceptions)

Key Principle:
├── Regulatory requirement overrides consent
├── But financial institution still must:
│   ├── Minimize data collection
│   ├── Restrict to necessary scope
│   ├── Limit retention period
│   ├── Maintain confidentiality
│   ├── Provide transparency
│   └── Respect other rights
```

## Financial Sector GDPR Considerations

### Customer Due Diligence Under GDPR

```
KYC DATA PROCESSING:

Personal Data Types:
├── Identity: Name, DOB, passport number, national ID
├── Contact: Address, phone, email
├── Financial: Account information, transaction history
├── Beneficial owner data: Ownership structure details
├── Employment: Job title, company, income
├── Source of funds: Business details, wealth source
└── Biometric data: Photo, fingerprint, facial recognition

Lawful Basis: Article 6(1)(c) - Legal Obligation
├── AML/CFT laws require identification
├── Sanctions screening mandatory
├── Beneficial ownership identification required
├── Ongoing monitoring obligations
└── Enhanced due diligence for high-risk

Processing Limitations:
├── Collect only what's necessary
├── Don't combine with non-regulated purposes
├── Maintain separate processing for AML vs. marketing
├── Limit access to compliance personnel only
├── Minimize retention to regulatory requirement
├── Encrypt and secure sensitive data
└── Document lawful basis

Data Subject Rights:
├── Right to know: Provide privacy notice with funding
├── Right of access: Provide data within 30 days
├── Right to rectification: Correct data timely
├── Right to erasure: Limited by regulatory retention
├── Right to restrict: Cannot fully restrict AML processing
├── Right to portability: Limited for regulated data
├── Right to object: Limited effect given legal obligation
└── Right to human review: Limited by law enforcement exception
```

### Biometric Data in Financial Services

```
FACIAL RECOGNITION FOR ID VERIFICATION:

Legal Framework:
├── Article 9(2)(a): Explicit consent
├── Article 9(2)(h): Employment context (for employees)
├── Article 9(2)(f): Legal obligation (if in regulation)
├── Special category data (requires heightened protection)
└── Some jurisdictions: Article 89 research exception

Implementation Requirements:
├── Purpose: Identity verification only
├── Must be explicit consent (not consent to T&Cs)
├── Easy withdrawal mechanism
├── Cannot condition service on consent
├── Must provide alternative methods
└── Data minimization (photo only while needed)

Storage and Retention:
├── Minimum necessary for verification purpose
├── Typically 30 days (completion of KYC)
├── Longer if dispute or regulatory investigation
├── Encrypted storage
├── Limited access (compliance staff only)
├── Secure deletion when no longer needed
└── Cannot use for other purposes (cross-selling, etc.)

Data Subject Rights:
├── Right to know: Explicit in privacy notice
├── Right of access: Provide facial images
├── Right to delete: After KYC completion
├── Right to restrict: Can object to processing
├── Right to object: Can challenge use
└── Right to human review: Available
```

### Transaction Data and GDPR

```
TRANSACTION MONITORING PRIVACY ISSUES:

Personal Data Elements:
├── Transacting individual data
├── Beneficiary/counterparty data
├── Behavioral/pattern data
├── Location data
├── Device data
├── Network analysis data
└── Historical transaction data

Lawful Basis: Article 6(1)(c) - Legal Obligation
├── Monitoring required by AML law
├── SAR/CTR filing requirements
├── Sanctions screening requirements
├── No consent required (legal obligation basis)
└── Processing can be mandatory

Privacy Concerns:
├── Behavioral tracking and profiling
├── Automated decision-making
├── Risk scoring and customer segmentation
├── Cross-border data transfers
├── Long-term retention
└── Mass surveillance concerns

Mitigation Measures:
├── Data minimization: Only transaction data, not personal
├── Purpose limitation: AML/CFT only
├── Access limitation: Compliance staff only
├── Retention limitation: 5-7 years regulatory requirement
├── Encryption: At rest and in transit
├── Audit trails: Who accessed what, when
├── Transparency: Clear privacy notice
├── Rights: Exercise data subject rights (with limits)
└── DPIA: Document privacy impact assessment
```

## GDPR-AML Compliance Balancing

### When Rights Conflict with Regulatory Obligations

```
SCENARIO 1: Right to Erasure vs. Regulatory Retention

Customer Request: "Delete all my data"
Regulatory Requirement: Keep KYC records 7 years

Resolution:
├── Explain legal retention requirement
├── Keep data in secure, encrypted storage
├── Limit access to regulatory/audit functions
├── Restrict use for non-regulatory purposes
├── Provide written explanation with reference
├── Cannot honor deletion request
├── No penalty for non-compliance with request
└── Document decision and notification

Legal Basis:
├── Article 17(3)(b): Legal obligation exception
├── Article 17(3)(e): Public task exception
├── Regulatory retention overrides right
├── Still must respect other rights (access, correction)
└── Still must minimize other processing
```

```
SCENARIO 2: Right to Portability vs. Regulated Data

Customer Request: "Provide my data in machine-readable format"
Data Type: Sanctions screening results, risk assessment

Resolution:
├── Provide all personal data held
├── Include transaction history
├── Include risk scores and assessment
├── Include screening match results
├── Provide in structured format (CSV, JSON)
├── Machine-readable and transferable format
├── Cannot refuse based on regulatory nature
├── May limit if:
│   ├── Impacts other individuals' data
│   ├── Affects third-party intellectual property
│   └── Would undermine security

Implementation:
├── Provide within 30 days
├── No fee required (free)
├── Multiple formats: PDF, CSV, JSON
├── Include explanations of risk scores
├── Include supporting documentation
└── Document provision
```

```
SCENARIO 3: Automated Decision-Making in Risk Scoring

Customer Right: Right to human review (Article 22)
Automated Risk Score: ML-generated customer risk rating

Resolution:
├── Explain automated risk scoring
├── Provide transparency on factors
├── Provide recourse mechanism
├── Human review available upon request
├── Can override automated score
├── Cannot make credit decisions solely on automation
├── Must provide option for human interaction
└── Exception: If automated scoring necessary for contract

Implementation:
├── Provide explanation of score factors
├── Explain weights and algorithm (conceptually)
├── Allow manual reconsideration
├── Escalation procedure documented
├── Document human review decision
└── Allow appeal/challenge mechanism
```

## GDPR Compliance Procedures for Financial Institutions

### Privacy Notice Requirements

```
MANDATORY DISCLOSURE (ARTICLES 13-14):

Information to Provide:
├── Identity and contact of controller
├── Contact of DPO (if appointed)
├── Purpose of processing
├── Lawful basis (Article 6 reference)
├── Legitimate interests pursued (if applicable)
├── Recipients of data:
│   ├── Regulatory authorities
│   ├── Law enforcement
│   ├── Other financial institutions
│   ├── Service providers
│   └── Beneficial owners (if applicable)
├── Retention period
├── Data subject rights:
│   ├── Right of access
│   ├── Right of rectification
│   ├── Right to erasure (with limits)
│   ├── Right to restrict
│   ├── Right to portability
│   ├── Right to object
│   └── Right to withdraw consent
├── Complaint procedure to authority
├── Information about automated decision making
│   ├── Whether used
│   ├── Logic and consequences
│   ├── Right to human review
│   └── Opportunity to express views
└── Source of data (if not from data subject)

Timing:
├── At time of collection (from data subject)
├── Within 1 month (if not from data subject)
└── Before first communication (if not from data subject)

Format:
├── Clear, transparent language
├── Separate from other terms
├── Easily accessible
├── Concise, intelligible
├── Avoid legal jargon
├── Multiple languages (regional)
└── Written and/or electronic
```

### International Data Transfers

```
ARTICLE 45: ADEQUACY DECISIONS

Transfers Permitted To:
├── EU adequacy decision jurisdictions:
│   ├── EEA countries (Iceland, Liechtenstein, Norway)
│   ├── Canada (with limitations)
│   ├── Japan
│   ├── South Korea
│   ├── UK (post-Brexit)
│   └── Other GDPR equivalent jurisdictions
├── Standard Contractual Clauses (SCCs) required
└── Binding Corporate Rules (BCRs) required

Standard Contractual Clauses (SCCs):
├── Provides contractual safeguards
├── Approved by EU Commission
├── Inserted in processor agreements
├── Applies to controller-to-processor transfers
├── Applies to controller-to-controller transfers
├── May require additional safeguards (supplementary measures)
└── May require adequacy assessment

For Financial Institution Compliance:
├── If customer data transferred to US: SCCs required
├── If customer data to non-EU processors: SCCs required
├── If customer data to parent company (non-EU): SCCs required
├── If sanctions screening vendor outside EU: SCCs required
├── Document all transfers in Data Processing Inventory
└── Assess supplementary safeguards
```

## GDPR Audit and Compliance Checklist

```
GOVERNANCE:
☐ Data Protection Officer appointed (if required)
☐ GDPR compliance program established
☐ Policy and procedures updated for GDPR
☐ Staff GDPR training completed
☐ Third-party processors assessed for GDPR compliance
☐ Documentation of lawful basis for processing
☐ Records of consent (if used)

DATA PROTECTION IMPACT ASSESSMENT (DPIA):
☐ DPIA conducted for high-risk processing
☐ Risks identified and documented
☐ Mitigation measures identified
☐ DPO consulted (if required)
☐ Authority consultation if residual risk

PERSONAL DATA INVENTORY:
☐ Categories of data subject documented
☐ Categories of personal data documented
☐ Processing purposes documented
☐ Retention periods documented
☐ Recipients documented
☐ Technical and organizational measures documented
☐ Lawful basis for each processing documented

LAWFUL BASIS:
☐ Consent properly documented (if used)
☐ Consent clearly separate from other terms
☐ Withdrawal mechanism easy to use
☐ Legal obligation processing documented
☐ Legitimate interest assessment completed
☐ Processing necessary for contract
☐ Vital interest protection documented

DATA SUBJECT RIGHTS IMPLEMENTATION:
☐ Right of access: Process and respond (30 days)
☐ Right of rectification: Correction mechanism established
☐ Right to erasure: Balanced with retention obligations
☐ Right to restrict: Process and flag data
☐ Right to portability: Provision mechanism established
☐ Right to object: Process and document
☐ Automated decision: Transparency and human review
☐ Complaint mechanism: Supervisory authority contact

DATA SECURITY:
☐ Encryption implemented (at rest and in transit)
☐ Access controls (RBAC, MFA)
☐ Audit trails maintained
☐ Regular security assessments conducted
☐ Incident response procedures established
☐ Breach notification procedures (72 hours)
☐ Third-party security requirements in contracts
☐ Employee confidentiality obligations

INTERNATIONAL TRANSFERS:
☐ Adequacy decisions identified
☐ Standard Contractual Clauses in place
☐ Supplementary safeguards documented
☐ Transfer impact assessments completed
☐ Sub-processor authorization obtained
☐ Recipient country risk assessed

VENDOR MANAGEMENT:
☐ Data Processing Agreements with all processors
☐ Processor GDPR compliance certified
☐ Sub-processor authorization obtained
☐ Security requirements specified
☐ Regular vendor assessments conducted
☐ Audit/inspection rights reserved
☐ Breach notification requirements
☐ Data return/deletion procedures

DOCUMENTATION:
☐ Processing activity records maintained
☐ Consent records (if applicable)
☐ DPIA documentation
☐ Risk assessment documentation
☐ Data subject request logs
☐ Breach incident records
☐ Training records
☐ Third-party audit reports

SUPERVISORY AUTHORITY COOPERATION:
☐ Contact information for DPA provided
☐ Complaint procedures explained
☐ Cooperation procedures documented
☐ Breach notification procedures
☐ Prior consultation procedures (if required)
☐ Emergency contact procedures
```

## GDPR Penalties and Enforcement

### Administrative Fines

```
CATEGORY 1 (Articles 32, 33, 34):
├── Data security failures
├── Breach notification failures
├── Data subject notification failures
├── Maximum fine: €10,000,000 or 2% of annual revenue
└── Whichever is higher

CATEGORY 2 (Articles 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15-22, 24, 25, 26, 27, 28, 29, 30, 32):
├── Lack of consent
├── Lack of lawful basis
├── Insufficient transparency
├── Failure to provide required information
├── Failure to honor data subject rights
├── Insufficient safeguards
├── Failure to appoint DPO
├── Maximum fine: €20,000,000 or 4% of annual revenue
└── Whichever is higher
```

## Best Practices for GDPR-Compliant RegTech

1. **Lawful Basis First** - Establish clear legal obligation for AML processing
2. **Data Minimization** - Collect only necessary data
3. **Transparency** - Clear privacy notices
4. **Security by Default** - Encryption and access controls
5. **Rights Respect** - Honor data subject rights within limits
6. **Vendor Oversight** - Strong processor contracts and oversight
7. **Documentation** - Complete record of compliance measures
8. **Incident Response** - 72-hour breach notification procedures
9. **DPIA** - Assess privacy impacts for high-risk processing
10. **Continuous Monitoring** - Regular audits and updates
