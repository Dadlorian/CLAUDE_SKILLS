# HIPAA Compliance Reference

## Health Insurance Portability and Accountability Act (HIPAA)

### Overview

HIPAA is a U.S. federal law enacted in 1996 to protect sensitive patient health information from being disclosed without the patient's consent or knowledge. The HITECH Act of 2009 significantly strengthened HIPAA's privacy and security protections.

### Applicability

#### Covered Entities
**Healthcare Providers:**
- Doctors, clinics, psychologists, dentists, chiropractors
- Nursing homes, pharmacies
- Any provider that transmits health information electronically

**Health Plans:**
- Health insurance companies
- HMOs, Medicare, Medicaid
- Employer-sponsored health plans
- Government programs paying for healthcare

**Healthcare Clearinghouses:**
- Entities processing nonstandard health information from another entity into standard format
- Billing services, repricing companies
- Community health information systems

#### Business Associates
Any entity that:
- Performs functions or activities on behalf of covered entity involving PHI
- Provides services to covered entity involving PHI access
- Examples: IT providers, billing companies, cloud storage providers, consultants, attorneys, accountants, shredding services

**Subcontractors:**
- Business associates of business associates
- Subject to HIPAA requirements

### Protected Health Information (PHI)

#### Definition
Individually identifiable health information held or transmitted by covered entity or business associate:
- Created or received by healthcare provider, health plan, employer, or clearinghouse
- Relates to past, present, or future physical or mental health or condition
- Relates to provision of healthcare
- Relates to payment for healthcare
- Identifies the individual or could reasonably be used to identify

#### 18 HIPAA Identifiers
1. Names
2. Geographic subdivisions smaller than state (except first 3 digits of ZIP if area has >20,000 people)
3. Dates (except year) directly related to individual (birth, admission, discharge, death)
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers and serial numbers (including license plates)
13. Device identifiers and serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers (fingerprints, voiceprints)
17. Full-face photographs and comparable images
18. Any other unique identifying number, characteristic, or code

#### Electronic Protected Health Information (ePHI)
PHI that is created, stored, transmitted, or received electronically.

### HIPAA Privacy Rule (45 CFR Part 160 and Part 164, Subparts A and E)

#### Purpose
Establishes national standards for protection of health information privacy.

#### Key Requirements

**Notice of Privacy Practices (NPP):**
- Must provide to patients at first service delivery
- Describe uses and disclosures of PHI
- Patient rights
- Covered entity's legal duties
- Complaint procedures
- Must be written in plain language
- Post prominently and make available
- Good faith effort to obtain written acknowledgment

**Permitted Uses and Disclosures:**

**Without Authorization:**
- **Treatment:** Provision, coordination, or management of healthcare
- **Payment:** Billing and reimbursement activities
- **Healthcare Operations:** Quality improvement, training, accreditation, business management

**Other Permitted Disclosures (without authorization):**
- To individual or personal representative
- For treatment, payment, operations (with minimum necessary)
- Opportunity to agree or object (directory, family/friends)
- Incidental disclosures (secondary to permitted use)
- Public interest and benefit activities:
  - Required by law
  - Public health activities
  - Victims of abuse, neglect, or domestic violence
  - Health oversight activities
  - Judicial and administrative proceedings
  - Law enforcement purposes
  - Decedents (coroners, medical examiners, funeral directors)
  - Organ donation
  - Research (with IRB waiver or deceased persons)
  - Serious threat to health or safety
  - Essential government functions
  - Workers' compensation

**Required Authorizations:**
- Psychotherapy notes
- Marketing (with exceptions)
- Sale of PHI
- Other uses not covered by NPP

**Authorization Requirements:**
- Core elements (description of PHI, persons authorized, purpose, expiration)
- Plain language
- Copy to individual
- Right to revoke
- Specific for marketing and sale of PHI

**Minimum Necessary Standard:**
- Use, disclose, request only minimum necessary to accomplish purpose
- Does not apply to: treatment, disclosures to individual, authorized uses/disclosures, required by law, compliance activities
- Implement policies and procedures
- Reasonable reliance on requests from other covered entities or public officials

**Individual Rights:**

1. **Right to Access (45 CFR 164.524)**
   - Inspect and obtain copy of PHI in designated record set
   - Within 30 days (extendable 30 days)
   - Reasonable cost-based fees allowed
   - Copy in requested format if readily producible
   - Denial rights in limited circumstances (may be reviewable)

2. **Right to Amend (45 CFR 164.526)**
   - Request amendment of inaccurate or incomplete PHI
   - Within 60 days (extendable 30 days)
   - Can deny if not created by entity, not in designated record set, not available for access, or already accurate/complete
   - Must provide denial reason and appeal rights

3. **Right to Accounting of Disclosures (45 CFR 164.528)**
   - List of disclosures made in past 6 years (excluding treatment, payment, operations, to individual, authorized, incidental, etc.)
   - Within 60 days (extendable 30 days)
   - First accounting in 12-month period free
   - Must include: date, recipient, description of PHI, purpose

4. **Right to Request Restrictions (45 CFR 164.522(a))**
   - Request restrictions on uses and disclosures for treatment, payment, operations
   - Not required to agree (except out-of-pocket payment restriction)
   - If agree, must comply (except for emergency treatment)
   - **Required restriction:** If patient pays out-of-pocket in full, must restrict disclosure to health plan (unless required by law)

5. **Right to Request Confidential Communications (45 CFR 164.522(b))**
   - Request communications by alternative means or at alternative locations
   - Must accommodate reasonable requests
   - Cannot require explanation

6. **Right to Notification of Breach (45 CFR 164.404-414)**
   - Notification without unreasonable delay, no later than 60 days after discovery
   - Written notification to affected individuals
   - Media notification if breach affects 500+ residents of a state
   - HHS notification (immediately if 500+, annually if <500)

### HIPAA Security Rule (45 CFR Part 160 and Part 164, Subpart C)

#### Purpose
Establishes national standards for protecting ePHI.

#### Applicability
- Covered entities and business associates
- Only applies to ePHI (not paper PHI)

#### Administrative Safeguards (45 CFR 164.308)

**Security Management Process (Required):**
- Risk Analysis (Required): Identify and assess risks and vulnerabilities
- Risk Management (Required): Implement security measures to reduce risks to reasonable and appropriate level
- Sanction Policy (Required): Apply sanctions against workforce members who violate policies
- Information System Activity Review (Required): Review logs, reports, incident tracking

**Assigned Security Responsibility (Required):**
- Designate security official responsible for security policies and procedures

**Workforce Security (Required):**
- Authorization/Supervision (Addressable): Procedures for authorization and supervision
- Workforce Clearance (Addressable): Clearance procedures
- Termination Procedures (Addressable): Terminate access upon employment end

**Information Access Management (Required):**
- Isolating Healthcare Clearinghouse Functions (Required): If clearinghouse is part of larger organization
- Access Authorization (Addressable): Policies and procedures for access authorizations
- Access Establishment and Modification (Addressable): Establish, document, review, modify access

**Security Awareness and Training (Required):**
- Security Reminders (Addressable): Periodic security updates and reminders
- Protection from Malicious Software (Addressable): Procedures for malware detection, protection, reporting
- Log-in Monitoring (Addressable): Procedures for monitoring log-in attempts and reporting discrepancies
- Password Management (Addressable): Creating, changing, safeguarding passwords

**Security Incident Procedures (Required):**
- Response and Reporting (Required): Identify and respond to security incidents, mitigate harmful effects, document

**Contingency Plan (Required):**
- Data Backup Plan (Required): Procedures for creating and maintaining exact copies of ePHI
- Disaster Recovery Plan (Required): Procedures to restore lost data
- Emergency Mode Operation Plan (Required): Continue critical business processes while operating in emergency mode
- Testing and Revision Procedures (Addressable): Test and revise contingency plans
- Applications and Data Criticality Analysis (Addressable): Assess criticality of applications and data

**Evaluation (Required):**
- Periodic technical and nontechnical evaluation based on standards in Security Rule

**Business Associate Contracts and Other Arrangements (Required):**
- Written contract or other arrangement with business associates
- BA must implement appropriate safeguards
- Report security incidents
- Ensure subcontractors comply
- Authorize termination if material breach

#### Physical Safeguards (45 CFR 164.310)

**Facility Access Controls (Required):**
- Contingency Operations (Addressable): Facility access procedures for restoring lost data under disaster recovery and emergency operations
- Facility Security Plan (Addressable): Policies for safeguarding facility and equipment from unauthorized physical access, tampering, theft
- Access Control and Validation Procedures (Addressable): Procedures to control and validate person's access based on role or function
- Maintenance Records (Addressable): Document repairs and modifications to physical components of facility

**Workstation Use (Required):**
- Policies and procedures for workstation use and proper functions

**Workstation Security (Required):**
- Physical safeguards for workstations with ePHI to restrict access to authorized users

**Device and Media Controls (Required):**
- Disposal (Required): Policies for final disposition of ePHI and hardware/media
- Media Re-use (Required): Procedures for removing ePHI before re-use
- Accountability (Addressable): Maintain record of movements of hardware and media containing ePHI
- Data Backup and Storage (Addressable): Create retrievable exact copy of ePHI before movement

#### Technical Safeguards (45 CFR 164.312)

**Access Control (Required):**
- Unique User Identification (Required): Unique user ID for identifying and tracking user identity
- Emergency Access Procedure (Required): Procedures for obtaining ePHI during emergency
- Automatic Logoff (Addressable): Terminate session after predetermined time of inactivity
- Encryption and Decryption (Addressable): Mechanism to encrypt and decrypt ePHI

**Audit Controls (Required):**
- Hardware, software, and/or procedural mechanisms to record and examine access and activity in systems with ePHI

**Integrity (Required):**
- Mechanism to Authenticate ePHI (Addressable): Electronic mechanisms to corroborate ePHI has not been altered or destroyed

**Person or Entity Authentication (Required):**
- Procedures to verify person or entity seeking access to ePHI is the one claimed

**Transmission Security (Required):**
- Integrity Controls (Addressable): Security measures to ensure electronically transmitted ePHI is not improperly modified
- Encryption (Addressable): Mechanism to encrypt ePHI whenever deemed appropriate

#### Required vs. Addressable Implementation Specifications

**Required:**
- Must implement

**Addressable:**
- Assess whether reasonable and appropriate for organization
- If reasonable and appropriate, implement
- If not, document why not and implement equivalent alternative (if reasonable and appropriate)
- If no alternative, document why not

### HIPAA Breach Notification Rule (45 CFR 164, Subpart D)

#### Breach Definition
Acquisition, access, use, or disclosure of PHI in a manner not permitted under Privacy Rule that compromises security or privacy of PHI.

**Exceptions (not a breach):**
1. Unintentional acquisition, access, or use by workforce member or person acting under authority of covered entity/BA if in good faith and within scope of authority, and does not result in further impermissible use or disclosure
2. Inadvertent disclosure from authorized person to another authorized person at same organization, and information is not further used or disclosed impermissibly
3. Disclosure where covered entity/BA has good faith belief that unauthorized person to whom disclosure was made would not reasonably have been able to retain information

#### Breach Risk Assessment
Must conduct risk assessment for impermissible use or disclosure to determine if breach occurred:
- Nature and extent of PHI involved
- Unauthorized person who used PHI or to whom disclosure was made
- Whether PHI was actually acquired or viewed
- Extent to which risk to PHI has been mitigated

#### Notification Requirements

**To Individuals (45 CFR 164.404):**
- Without unreasonable delay, no later than 60 days after discovery
- Written notice (first-class mail or email if individual agreed)
- Substitute notice if contact information insufficient
- Content requirements: description of breach, types of PHI involved, steps individuals should take, what entity is doing, contact procedures

**To Media (45 CFR 164.406):**
- If breach affects 500+ residents of state or jurisdiction
- Notice to prominent media outlets serving the area
- Without unreasonable delay, no later than 60 days after discovery

**To HHS (45 CFR 164.408):**
- **Breaches of 500+:** Contemporaneous with individual notice
- **Breaches of <500:** Annual log submitted within 60 days of end of calendar year

**Business Associates:**
- Must notify covered entity without unreasonable delay, no later than 60 days after discovery

### HITECH Act Enhancements (2009)

#### Breach Notification
- Established breach notification requirements
- Four-tier penalty structure

#### Business Associate Direct Liability
- Business associates directly liable for HIPAA violations
- Required business associate agreements (BAAs)

#### Enhanced Penalties
- Increased penalty amounts
- Mandatory penalties in some cases

#### Individual Right to ePHI Copy
- Right to receive ePHI in electronic format

#### Restrictions on Sale of PHI
- Prohibition on sale of PHI without authorization

#### Marketing Restrictions
- Enhanced requirements for marketing authorizations

#### Accounting of Disclosures
- Enhanced accounting requirements (partially not implemented)

### HIPAA Omnibus Rule (2013)

#### Business Associate Definition Expansion
- Subcontractors of business associates covered
- Data transmission and storage services included

#### Genetic Information
- Genetic information is health information
- Prohibition on health plans using or disclosing for underwriting

#### Marketing and Fundraising
- Stricter marketing authorization requirements
- Enhanced fundraising opt-out rights

#### Individual Rights
- Right to restrict disclosures to health plan if paid out-of-pocket in full
- Right to request copy of ePHI in electronic format

#### Breach Notification
- "Harm" standard replaced with "Risk Assessment" standard
- Presumption of breach unless low probability that PHI compromised

### Enforcement and Penalties

#### Enforcement Agency
Office for Civil Rights (OCR), U.S. Department of Health and Human Services

#### Civil Monetary Penalties (Tier Structure)

**Tier 1: Did Not Know**
- $100 - $50,000 per violation
- Annual maximum: $1.5 million per violation type

**Tier 2: Reasonable Cause**
- $1,000 - $50,000 per violation
- Annual maximum: $1.5 million per violation type

**Tier 3: Willful Neglect - Corrected**
- $10,000 - $50,000 per violation
- Annual maximum: $1.5 million per violation type
- Must correct within 30 days

**Tier 4: Willful Neglect - Not Corrected**
- $50,000 per violation (minimum and maximum)
- Annual maximum: $1.5 million per violation type

#### Criminal Penalties (Enforced by Department of Justice)
- **Knowing Obtaining or Disclosure:** Up to $50,000 and 1 year imprisonment
- **Under False Pretenses:** Up to $100,000 and 5 years imprisonment
- **With Intent to Sell, Transfer, or Use for Commercial Advantage, Personal Gain, or Malicious Harm:** Up to $250,000 and 10 years imprisonment

#### Enforcement Process
1. **Complaint:** Filed with OCR
2. **Investigation:** OCR investigates if has jurisdiction
3. **Resolution:**
   - Informal resolution
   - Corrective action plan
   - Resolution agreement
   - Civil monetary penalty
4. **Audit:** OCR conducts random audits

### HIPAA Compliance Automation Opportunities

#### Privacy Compliance
- Automated Notice of Privacy Practices generation and distribution
- Patient consent and authorization tracking
- Minimum necessary access controls and monitoring
- Individual rights request portal (access, amendment, restriction, accounting)
- Automated accounting of disclosures
- Psychotherapy notes segregation and protection

#### Security Compliance
- Automated risk analysis and vulnerability scanning
- Access control automation (unique user IDs, role-based access, automatic logoff)
- Audit log collection and analysis
- Encryption of ePHI at rest and in transit
- Automated patch management
- Security incident detection and response
- Compliance monitoring dashboards

#### Breach Management
- Breach detection and alerting
- Automated risk assessment workflows
- Breach notification timeline tracking (60-day deadline)
- Template-based notification generation
- HHS breach reporting automation
- Breach log maintenance

#### Business Associate Management
- BAA repository and tracking
- BA compliance assessment
- BA onboarding and offboarding
- Subcontractor identification and tracking
- BAA renewal reminders
- BA breach notification tracking

#### Training and Awareness
- HIPAA training assignment and tracking
- Annual training requirement monitoring
- Role-based training content
- Training completion reporting
- Security reminders and communications
- Phishing simulation and awareness

#### Documentation and Policies
- Policy and procedure repository
- Automated policy acknowledgment
- Document version control
- Compliance documentation retention
- Audit readiness documentation
- Security Rule implementation documentation

#### Contingency Planning
- Automated backup monitoring
- Disaster recovery testing tracking
- Emergency mode procedures
- Business continuity planning
- Data recovery automation

### HIPAA Compliance Best Practices

1. **Conduct Regular Risk Assessments:** Annual or when significant changes occur
2. **Implement Strong Access Controls:** Role-based access, least privilege, unique user IDs
3. **Encrypt ePHI:** At rest and in transit
4. **Train Workforce Regularly:** Annual training minimum, role-based content
5. **Maintain Business Associate Agreements:** Current BAAs with all BAs and subcontractors
6. **Monitor and Audit:** Regular auditing of access logs and system activity
7. **Incident Response Plan:** Written plan, regular testing, swift response
8. **Document Everything:** Policies, procedures, risk assessments, training, incidents
9. **Secure Physical Locations:** Facility access controls, workstation security, device controls
10. **Plan for Contingencies:** Regular backups, disaster recovery, business continuity

### HIPAA Compliance Checklist

#### Privacy Rule
- [ ] Develop and implement privacy policies and procedures
- [ ] Create and distribute Notice of Privacy Practices
- [ ] Designate Privacy Officer
- [ ] Implement individual rights processes (access, amendment, accounting, restrictions, confidential communications)
- [ ] Implement minimum necessary policies
- [ ] Obtain authorizations where required
- [ ] Implement breach notification procedures
- [ ] Train workforce on privacy requirements

#### Security Rule
- [ ] Designate Security Officer
- [ ] Conduct comprehensive risk analysis
- [ ] Develop and implement risk management plan
- [ ] Implement administrative safeguards (policies, training, incident response, contingency planning)
- [ ] Implement physical safeguards (facility access, workstation security, device controls)
- [ ] Implement technical safeguards (access control, audit controls, integrity controls, authentication, transmission security)
- [ ] Document security measures
- [ ] Evaluate compliance periodically

#### Business Associates
- [ ] Identify all business associates
- [ ] Execute written business associate agreements
- [ ] Obtain satisfactory assurances from business associates
- [ ] Monitor business associate compliance
- [ ] Terminate relationship if material breach and not cured

#### Breach Notification
- [ ] Implement breach detection mechanisms
- [ ] Establish breach response procedures
- [ ] Conduct breach risk assessments
- [ ] Implement notification procedures (individuals, HHS, media)
- [ ] Maintain breach log
- [ ] Train workforce on breach response

#### Training and Awareness
- [ ] Develop HIPAA training program
- [ ] Conduct training for all workforce members
- [ ] Provide training at hire and annually
- [ ] Document training completion
- [ ] Provide role-specific training
- [ ] Conduct security awareness communications

#### Documentation and Retention
- [ ] Document all policies and procedures
- [ ] Maintain documentation for 6 years
- [ ] Implement version control
- [ ] Maintain compliance documentation
- [ ] Document risk assessments
- [ ] Document training activities
- [ ] Maintain audit logs

---

*Reference for HIPAA compliance automation and implementation*
