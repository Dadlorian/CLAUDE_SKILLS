# CCPA/CPRA Framework Reference

## California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA)

### Overview

The California Consumer Privacy Act (CCPA) became effective on January 1, 2020, establishing comprehensive privacy rights for California consumers. The California Privacy Rights Act (CPRA), passed in November 2020 and effective January 1, 2023, significantly amended and expanded the CCPA.

### Applicability

CCPA/CPRA applies to for-profit businesses that:
- Do business in California, AND
- Meet one or more thresholds:
  1. Annual gross revenues > $25 million
  2. Buy, sell, or share personal information of 100,000+ California consumers or households (CPRA changed from 50,000)
  3. Derive 50%+ of annual revenues from selling or sharing personal information

**CPRA additional applicability:**
- Contractors and service providers of covered businesses
- Third parties receiving personal information

### Key Definitions

#### Personal Information (PI)
Information that identifies, relates to, describes, is reasonably capable of being associated with, or could reasonably be linked to a particular consumer or household.

**Categories (CCPA § 1798.140):**
1. Identifiers (name, email, IP address, etc.)
2. Personal information categories (CA Customer Records statute)
3. Protected classification characteristics
4. Commercial information
5. Biometric information
6. Internet or network activity
7. Geolocation data
8. Sensory data (audio, visual, thermal, olfactory)
9. Professional or employment information
10. Non-public education information
11. Inferences drawn from PI

#### Sensitive Personal Information (SPI) - CPRA Addition
- Social Security, driver's license, passport numbers
- Account credentials
- Precise geolocation
- Racial or ethnic origin, religious or philosophical beliefs, union membership
- Mail, email, text messages content (not directed to business)
- Genetic data
- Biometric data for unique identification
- Personal information collected about health
- Personal information collected about sex life or sexual orientation

#### Sale of Personal Information
Selling, renting, releasing, disclosing, disseminating, making available, transferring, or otherwise communicating orally, in writing, or by electronic or other means, a consumer's personal information by the business to a third party for monetary or other valuable consideration.

#### Sharing (CPRA Addition)
Sharing, renting, releasing, disclosading, disseminating, making available, transferring, or otherwise communicating orally, in writing, or by electronic means, a consumer's personal information by the business to a third party for cross-context behavioral advertising.

#### Service Provider
An entity that processes personal information on behalf of a business for a business purpose pursuant to a written contract.

#### Contractor (CPRA Addition)
Person or entity that processes personal information on behalf of a business and is not a service provider.

#### Third Party
A person or entity not:
- The business collecting personal information
- A person to whom the business discloses a consumer's personal information for a business purpose pursuant to a written contract

### Consumer Rights

#### 1. Right to Know (§ 1798.100, 1798.110, 1798.115)

**General Right to Know:**
- Categories of PI collected
- Categories of sources
- Business or commercial purpose
- Categories of third parties to whom PI disclosed
- Specific pieces of PI collected

**Right to Know About Sales/Sharing:**
- Categories of PI sold or shared
- Categories of third parties to whom sold or shared
- By category of PI

**Lookback Period:** 12 months

**Response Time:** 45 days (extendable to 90 days with notice)

**Delivery:** By mail or electronically (consumer's choice)

**Verification Required:** Reasonable verification of consumer identity

#### 2. Right to Delete (§ 1798.105)

Consumer can request deletion of PI collected from consumer.

**Exceptions (business not required to delete):**
1. Complete transaction, provide goods/services, or reasonably anticipated within context
2. Detect security incidents, protect against malicious/illegal activity
3. Debug to identify and repair errors
4. Exercise free speech or another's right to free speech
5. Comply with California Electronic Communications Privacy Act
6. Engage in public or peer-reviewed scientific, historical, or statistical research in public interest
7. Enable solely internal uses reasonably aligned with consumer expectations
8. Comply with legal obligation
9. Make other internal and lawful uses compatible with context

**Response Time:** 45 days (extendable to 90 days)

**Verification Required:** Reasonable verification of consumer identity

#### 3. Right to Correct (CPRA Addition - § 1798.106)

Consumer can request correction of inaccurate personal information.

**Requirements:**
- Business must use commercially reasonable efforts
- Take into account nature of PI and purposes of processing
- Response time: 45 days (extendable to 90 days)

#### 4. Right to Opt-Out of Sale/Sharing (§ 1798.120)

Consumers have the right to opt-out of:
- Sale of their personal information
- Sharing for cross-context behavioral advertising (CPRA)

**Implementation:**
- "Do Not Sell or Share My Personal Information" link on homepage
- Accept user-enabled global privacy controls (GPC) as valid opt-out
- Cannot require account creation to opt-out
- Wait 12 months before asking to opt back in

#### 5. Right to Limit Use of Sensitive Personal Information (CPRA - § 1798.121)

Consumer can limit use and disclosure of SPI to:
- Providing goods/services reasonably expected
- Other enumerated purposes in regulations

**Implementation:**
- "Limit the Use of My Sensitive Personal Information" link (if applicable)
- Accept global privacy controls
- Does not apply if SPI used only for permitted purposes

#### 6. Right to Non-Discrimination (§ 1798.125)

Business cannot discriminate against consumers for exercising rights:
- Cannot deny goods or services
- Cannot charge different prices or rates
- Cannot provide different level or quality of goods or services

**Financial Incentive Programs Allowed:**
- Must be reasonably related to value of consumer's data
- Must provide notice and obtain opt-in consent
- Consumer can revoke consent at any time

### Business Obligations

#### Privacy Notice Requirements

**At Collection Notice:**
- Categories of PI to be collected
- Purposes for each category
- Whether PI is sold or shared
- How long PI retained (CPRA)
- Link to privacy policy

**Privacy Policy (§ 1798.130):**
- Categories of PI collected (last 12 months)
- Categories of sources
- Business or commercial purposes
- Categories of third parties PI shared with
- Categories of PI sold or shared (if applicable) and categories of recipients
- Consumer rights and how to exercise them
- Contact information for inquiries
- Date privacy policy last updated
- Description of verification process
- If selling/sharing minors' PI, process for opting in

**Notice of Right to Opt-Out:**
- "Do Not Sell or Share My Personal Information" link on homepage
- Must honor global privacy control signals (GPC)

**Notice of Financial Incentive:**
- Material terms of financial incentive program
- How to opt-in
- How to revoke consent

#### Contracts with Service Providers and Contractors (§ 1798.100(d))

Written contracts must:
- Prohibit selling or sharing PI
- Prohibit retaining, using, or disclosing PI except for specific business purpose in contract
- Prohibit combining PI with other PI (with exceptions)
- Grant audit rights to business
- Require service provider/contractor to comply with CCPA
- Certify understanding of restrictions and compliance

#### Reasonable Security (§ 1798.150)

Businesses must implement and maintain reasonable security procedures and practices appropriate to the nature of the personal information.

**Private Right of Action:**
- Statutory damages for data breaches: $100-$750 per consumer per incident or actual damages, whichever is greater
- 30-day cure period (if curable)
- Class action lawsuits allowed

#### Data Protection Assessments (CPRA - § 1798.185(a)(15))

Required for processing that presents significant risk to consumers' privacy or security:
- Regular and systematic disclosure of SPI to third parties
- Processing for targeted advertising
- Sale of PI
- Profiling

**Assessment must identify and weigh:**
- Benefits of processing
- Potential risks to privacy and freedom
- Safeguards to mitigate risks

**Confidential and exempt from public records requests**

#### Data Minimization and Purpose Limitation (CPRA)

- Collect PI reasonably necessary and proportionate to purposes
- Not collect additional categories without notice
- Limit retention to reasonably necessary
- Prohibition on secondary use without notice

### Special Provisions

#### Minors Under 16 (§ 1798.120(d))

**Opt-In Required:**
- Consumers 13-15: Affirmative authorization by consumer
- Consumers under 13: Affirmative authorization by parent/guardian
- Applies to businesses with actual knowledge consumer is under 16

**No Sale/Sharing without opt-in**

#### Employee and B2B Exemptions (Partial - Expiring)

CCPA initially exempted employee and B2B data with sunset dates. CPRA made these fully subject to CCPA effective January 1, 2023.

**Current Status:**
- Employee data: Fully subject to CCPA/CPRA
- B2B data: Fully subject to CCPA/CPRA

#### Household Information (§ 1798.145(a)(1))

Exemptions for:
- Publicly available information from government records
- Deidentified or aggregate consumer information
- Information covered by sector-specific privacy laws (HIPAA, GLBA, FCRA, etc.)

### Enforcement

#### California Privacy Protection Agency (CPPA)

Created by CPRA, operational July 1, 2021.

**Powers:**
- Rulemaking authority
- Enforcement authority
- Administrative fines
- Investigations and audits

**Prior to CPPA:** Attorney General enforcement

#### Administrative Fines (§ 1798.155)

- **Unintentional violations:** Up to $2,500 per violation
- **Intentional violations:** Up to $7,500 per violation
- 30-day cure period for violations (if curable)

**CPRA Enhancement:**
- Violations involving minors: Up to $7,500 per violation (no intent required)

#### Private Right of Action (§ 1798.150)

Limited to data breaches resulting from failure to maintain reasonable security:
- Statutory damages: $100-$750 per consumer per incident
- Or actual damages, whichever is greater
- 30-day notice and opportunity to cure
- Class action lawsuits allowed

### CPRA Key Changes and Additions

#### New Agency
- California Privacy Protection Agency (CPPA)
- Dedicated privacy enforcement agency
- Rulemaking and enforcement powers

#### Expanded Rights
- Right to correct inaccurate information
- Right to limit use of sensitive personal information
- Extended opt-out to "sharing" for cross-context ads

#### New Obligations
- Data minimization and purpose limitation
- Data protection assessments
- Retention limits disclosure
- Service provider/contractor distinctions

#### Sensitive Personal Information
- New category with enhanced protections
- Right to limit use and disclosure
- Stricter requirements

#### Global Privacy Controls
- Must honor user-enabled GPC as valid opt-out
- Browser-level privacy signals

#### Employee and B2B Data
- Exemptions expired
- Now fully covered under CPRA

#### Enhanced Penalties
- Increased fines for violations involving minors
- Stricter enforcement by CPPA

### Compliance Automation Opportunities

#### Consumer Rights Management
- Self-service request portal
- Automated verification processes
- Multi-system data discovery and collection
- Deadline tracking (45/90 days)
- Response generation and delivery
- Audit trail and documentation

#### Opt-Out and Preference Management
- "Do Not Sell or Share" mechanism
- Global Privacy Control (GPC) detection and honoring
- "Limit Use of SPI" mechanism
- Preference center implementation
- Opt-out list maintenance
- Cross-channel synchronization

#### Notice and Disclosure Management
- Privacy policy generation and versioning
- At-collection notice management
- Category-based disclosure tracking
- Automated updates based on processing changes
- Multi-language support
- Distribution and acknowledgment tracking

#### Data Inventory and Mapping
- Personal information inventory by category
- Sensitive personal information identification
- Data flow mapping and visualization
- Source and third-party tracking
- Retention period documentation
- Processing purpose mapping

#### Contract and Vendor Management
- Service provider agreement templates
- Contractor agreement templates
- Third-party identification and tracking
- Contract compliance monitoring
- Vendor assessment and audits
- Certification collection and tracking

#### Data Protection Assessments
- Risk assessment questionnaires
- Automated risk scoring
- Assessment workflow and approvals
- Documentation repository
- Regular review triggers
- Confidential storage

#### Security and Breach Response
- Security controls monitoring
- Breach detection and alerting
- Incident response workflow
- Private right of action assessment
- Cure period tracking
- Notification and documentation

#### Compliance Monitoring and Reporting
- Compliance dashboard and KPIs
- Regulatory update tracking
- Training completion monitoring
- Audit readiness documentation
- CPPA examination preparation
- Executive reporting

### CCPA/CPRA vs. GDPR Comparison

| Aspect | CCPA/CPRA | GDPR |
|--------|-----------|------|
| **Scope** | California consumers | EU/EEA data subjects |
| **Applicability** | Revenue/volume thresholds | Territorial and targeting |
| **Legal Basis** | Not required (notice-based) | Required (6 legal bases) |
| **Consent** | Opt-out (except minors <16) | Opt-in for most processing |
| **Right to Access** | Categories + specific pieces | Full access to all PI |
| **Right to Delete** | Yes, with broad exceptions | Yes, with narrower exceptions |
| **Right to Portability** | No specific right | Yes, machine-readable format |
| **Right to Correct** | Yes (CPRA) | Yes |
| **Right to Opt-Out** | Sale and sharing | Direct marketing and profiling |
| **Sensitive Data** | SPI with limit right (CPRA) | Special categories, prohibited |
| **DPO/Privacy Officer** | Not required | Required in some cases |
| **DPIA** | Data protection assessment (CPRA) | DPIA for high-risk processing |
| **Breach Notification** | Private right of action only | 72-hour to authority, high risk to subjects |
| **Fines** | Up to $7,500 per violation | Up to 4% global revenue or €20M |
| **Private Right** | Data breaches only | No private right (through SA) |
| **Minors** | Opt-in under 16 | Parental consent under 13-16 |

### CCPA/CPRA Compliance Checklist

- [ ] Determine if CCPA/CPRA applies to your business
- [ ] Identify all personal information processing
- [ ] Classify sensitive personal information (SPI)
- [ ] Update privacy policy with required disclosures
- [ ] Implement "at collection" notices
- [ ] Add "Do Not Sell or Share" link to homepage (if applicable)
- [ ] Add "Limit Use of SPI" link (if applicable)
- [ ] Implement global privacy control (GPC) detection
- [ ] Create consumer rights request processes (know, delete, correct, opt-out, limit)
- [ ] Implement verification procedures
- [ ] Update service provider and contractor agreements
- [ ] Identify and document third parties
- [ ] Implement processes for minors under 16 (if applicable)
- [ ] Conduct data protection assessments (if required)
- [ ] Implement data minimization and retention limits
- [ ] Establish reasonable security measures
- [ ] Create audit trail and documentation systems
- [ ] Train employees on CCPA/CPRA compliance
- [ ] Establish ongoing compliance monitoring
- [ ] Prepare for CPPA examinations and enforcement

### Key CCPA/CPRA Resources

**Official Sources:**
- CCPA Text: https://oag.ca.gov/privacy/ccpa
- CPRA Text: https://cppa.ca.gov/
- California Privacy Protection Agency: https://cppa.ca.gov/
- CPPA Regulations: https://cppa.ca.gov/regulations/

**Regulatory Materials:**
- Attorney General Regulations (pre-CPRA)
- CPPA Final and Proposed Regulations
- CPPA Guidance and FAQs

**Industry Resources:**
- IAPP CCPA/CPRA resources
- Industry association guidance
- Legal analysis and updates

---

*Reference for CCPA/CPRA compliance automation and implementation*
