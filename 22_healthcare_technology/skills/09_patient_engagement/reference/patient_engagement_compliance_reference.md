# Patient Engagement Compliance Reference

## Regulatory Framework Overview

### Federal Regulations

**HIPAA (45 CFR Parts 160 and 164)**
- Patient Access Rights (164.524)
- Privacy Rule (164.500 et seq.)
- Security Rule (164.302 et seq.)
- Breach Notification (164.400 et seq.)

**21st Century Cures Act (2016)**
- Information Blocking Prohibition (21 CFR Part 2)
- FHIR API Requirements
- USCDI Data Elements
- Patient Data Access Rights

**ONC Rules (45 CFR Part 171)**
- EHR Certification Requirements
- API Publication Requirement
- Patient Access via Standards
- Developer Documentation

**FDA Regulations**
- Medical Device Classification (21 CFR Part 860)
- Clinical Decision Support (FDA Guidance)
- Software as Medical Device (SaMD) Framework
- Cybersecurity Requirements

## Patient Rights Framework

### Right to Access (45 CFR 164.524)

**Scope:**
- Patient right to access own PHI
- Must be provided in timely manner (30 days default)
- Can request in format of choice (paper, electronic)
- Can request electronic copy at reasonable cost

**Implementation Requirements:**
```
Portal/System Must Provide:
├─ Authentication (strong identification)
├─ Authorization (verify patient accessing own record)
├─ Complete Medical Information
│  ├─ Clinical notes
│  ├─ Lab results
│  ├─ Imaging reports
│  ├─ Medications
│  ├─ Allergies
│  ├─ Problems
│  └─ All clinical information
├─ Multiple Formats
│  ├─ PDF/human-readable
│  ├─ CCDA/structured XML
│  ├─ FHIR/structured JSON
│  └─ Paper on request
└─ Metadata (dates, providers, authors)
```

**Exceptions (limited):**
- Psychotherapy notes (provider can deny)
- Information compiled for legal proceedings
- Information from non-HIPAA sources
- Federal regulations (some drug treatment records)

### Right to Restrict (45 CFR 164.522(a))

**Patient Can Request:**
- Restrict use/disclosure of PHI
- Restriction on particular provider or vendor
- Restriction by type of service
- Restrict disclosures to insurance (out-of-pocket)

**System Requirements:**
- Track all patient-requested restrictions
- Enforce restrictions in data sharing
- Audit compliance with restrictions
- Document restrictions in EHR

### Right to Amend (45 CFR 164.526)

**Patient Can Request:**
- Correct inaccurate PHI
- Add missing information
- Supplement incomplete records
- Document patient's disputes

**System Requirements:**
- Accept amendment requests
- Review for validity (reasonable vs. unreasonable)
- Accept if agrees with need to amend
- Add amendment to record permanently
- Notify affected parties of amendment
- Track amendment requests and decisions

### Right to Accounting of Disclosures (45 CFR 164.528)

**What Must Be Tracked:**
- Every PHI access and disclosure
- Date and purpose of disclosure
- Recipient information
- Scope of information disclosed

**Exemptions:**
- Treatment, payment, healthcare operations
- Patient-authorized uses
- Required by law
- De-identified information

**System Requirements:**
- Audit log all PHI accesses
- Generate reports for patient requests
- Provide within 30 days (60 days allowable)
- Free first request yearly; reasonable cost thereafter

## Information Blocking Regulations (21 CFR Part 2)

### Definition of Information Blocking

**Information Blocking Occurs When:**
- Provider, vendor, or other actor interferes with timely access
- Prevents transmission in usable/interoperable format
- Has no reasonable justification
- Results in harm to individual

**Prohibited Practices:**
```
Data Access Blocking:
├─ Delaying access to data
├─ Refusing to provide data
├─ Charging excessive fees
└─ Limiting data access

Format Blocking:
├─ Refusing to export in standard format
├─ Exporting in proprietary format only
├─ Limiting data elements exported
└─ Failing to include metadata

System Blocking:
├─ Disabling API functionality
├─ Limiting API response scope
├─ Charging for API usage
└─ Requiring proprietary integrations

Interoperability Blocking:
├─ Failing to use standards
├─ Using standards incompletely
├─ Creating artificial barriers
└─ Prioritizing proprietary solutions
```

### Legitimate Exceptions to Blocking Rules

**Security:**
- Blocking to prevent breaches
- Documented security risk assessment
- Implement minimum necessary restrictions

**Privacy:**
- Blocking non-consented disclosure
- Protecting third-party privacy
- Honoring patient restrictions

**Safety:**
- Blocking harmful data access
- Preventing misuse of data
- Documented safety concern

**Business Operations:**
- Blocking intra-organizational access (limited)
- Documented business justification

**Requirements:**
- Exceptions must be narrow and documented
- Regular review of legitimacy
- Not blocking for business advantage

### Penalties

**Civil Penalties:**
- Up to $300 per violation
- Can accumulate to millions for systematic blocking
- Enforced by ONC through CMS

**Enforcement Actions:**
- Warning letters
- Corrective action plans
- Decertification for EHRs
- Civil litigation

## HIPAA Privacy and Security Compliance

### Privacy Rule Compliance

**Required Elements in Patient Portal:**
```
Notice of Privacy Practices (NPP)
├─ Available at portal login
├─ Updated annually or with material changes
├─ Documents:
│  ├─ Uses and disclosures
│  ├─ Patient rights
│  ├─ Contact information
│  ├─ Complaint procedures
│  └─ Link to full policy

Authorization Management
├─ Patient can authorize specific disclosures
├─ Revoke previous authorizations
├─ Track all authorizations
└─ Respect restrictions

Marketing Prohibition
├─ No unsolicited marketing emails
├─ Educational content is NOT marketing
├─ Treatment communications allowed
├─ Patient opt-out capability

Fund-Raising Restriction
├─ Can share relevant health information
├─ Must allow opt-out
├─ Cannot condition treatment on participation
```

### Security Rule Compliance

**Administrative Safeguards:**
- Security management process with risk assessment
- Security officer designation
- Workforce security (access controls)
- Information access management
- Security awareness and training
- Security incident procedures
- Business associate agreements

**Physical Safeguards:**
- Facility access controls
- Workstation use policies
- Workstation security
- Device and media controls

**Technical Safeguards:**
- Access controls (authentication, authorization)
- Audit controls and logging
- Integrity controls (checksums, digital signatures)
- Transmission security (encryption)

**Implementation:**
```
Portal Security Checklist:
├─ Encryption
│  ├─ TLS 1.2+ for all data in transit
│  ├─ AES-256 for data at rest
│  └─ Encrypted backups
├─ Authentication
│  ├─ Username/password requirements
│  ├─ Multi-factor authentication recommended
│  └─ Session timeouts (15 min inactivity)
├─ Authorization
│  ├─ Role-based access control
│  ├─ Principle of least privilege
│  └─ Granular consent management
├─ Audit Logging
│  ├─ Log all PHI access
│  ├─ Retain logs 6 years minimum
│  ├─ Regular log review
│  └─ Tamper-evident storage
├─ Availability
│  ├─ Business continuity plan
│  ├─ Disaster recovery procedures
│  ├─ Backup and restore capability
│  └─ 99.9% uptime target
└─ Ongoing Monitoring
   ├─ Vulnerability assessments
   ├─ Penetration testing
   ├─ Security updates and patches
   └─ Incident response procedures
```

## Accessibility Compliance

### Americans with Disabilities Act (ADA)

**Applicability:**
- Portal must be accessible to persons with disabilities
- Applies to all patient-facing systems
- No separate system for disabled patients

**Required Accommodations:**
- Website accessibility (WCAG 2.1 AA minimum)
- Accessible documentation
- Auxiliary aids (interpreters, large print)
- Alternative formats

### WCAG 2.1 AA Standards

**Perceivable:**
```
1.1.1 Non-Text Content (A)
- All images have alt text
- Captions for video
- Transcripts for audio

1.4.3 Contrast (AA)
- Minimum 4.5:1 contrast ratio for text
- 3:1 for large text (18pt+)

1.4.4 Resize Text (AA)
- Text resizable up to 200%
- No loss of functionality
```

**Operable:**
```
2.1.1 Keyboard (A)
- All functionality operable via keyboard
- No keyboard traps
- Focus indicators visible

2.4.3 Focus Order (A)
- Logical tab order
- Focus visible at all times
- No keyboard shortcuts conflicting
```

**Understandable:**
```
3.1.1 Language of Page (A)
- HTML lang attribute set
- Page language identified

3.2.1 On Focus (A)
- No unexpected context changes
- Focus doesn't trigger submission
```

**Robust:**
```
4.1.1 Parsing (A)
- Valid HTML
- Proper element nesting

4.1.2 Name, Role, Value (A)
- Form labels properly associated
- Error messages clear
- ARIA landmarks used correctly
```

## FDA Clinical Decision Support Compliance

### FDA Guidance Requirements

**Non-FDA Regulated CDS:**
```
CDS Software NOT Regulated If:
├─ Provides information to support decision
├─ Practitioner retains full control
├─ No automatic execution
├─ Not required to follow recommendation
├─ Clearly labeled as informational
├─ Based on accurate information
├─ No marketing claims of diagnosis/treatment

Example: Medication interaction checker
- Alerts on potential interactions
- Provider decides action
- Not controlling treatment
```

**FDA-Regulated CDS:**
```
CDS Software REGULATED If:
├─ Controls clinical process/outcome
├─ Override not practically possible
├─ Intended to diagnose/treat/prevent disease
├─ Replaces practitioner judgment
├─ Makes diagnostic determination
├─ Provides treatment recommendation as primary function

Example: Diagnostic AI system
- Reads imaging and diagnoses condition
- Determines treatment
- Intended to control outcome
```

### Compliance Approach

```
If NOT Regulated CDS:
1. Document intended use (informational only)
2. Ensure content accuracy
3. Clear labeling provided
4. Provider education on proper use
5. Disclosure of data sources
6. Maintenance of accuracy over time

If Regulated CDS:
1. Determine regulatory classification
2. Identify predicate device (if 510(k))
3. Develop comprehensive submission
4. Clinical validation studies
5. Software documentation
6. User training and labeling
7. FDA pre-market review and approval
```

## State Privacy Laws Compliance

### California Privacy Rights (CCPA/CPRA)

**Applicability:**
- Applies to for-profit entities
- Processing data of California residents
- Annual gross revenues >$25M
- OR collect data from 100,000+ consumers
- OR derive 50%+ revenue from data sale

**Patient Rights:**
- Right to know data collected
- Right to delete collected data
- Right to correct inaccurate data
- Right to opt-out of data sales
- Right to nondiscrimination

**Implementation:**
```
CCPA/CPRA Requirements:
├─ Privacy Policy (detailed)
├─ Data request fulfillment (45 days)
├─ Deletion capability (45 days)
├─ Opt-out links prominent
├─ No higher prices for opting out
├─ Biometric data extra protection
├─ Sensitive data requires explicit consent
└─ Health/medical data (sensitive category)
```

### Virginia VCDPA and Similar Laws

**Consumer Rights:**
- Access personal data
- Delete personal data
- Correct inaccurate data
- Data portability
- Opt-out of targeted advertising/sale

**Business Requirements:**
- Purpose limitation
- Data minimization
- Reasonable security measures
- Privacy impact assessments

### Health-Specific State Laws

**Massachusetts 201 CMR 17.00:**
- Comprehensive cybersecurity standards
- Written security program
- Risk assessments
- Secure user authentication
- Monitoring and incident response

**New York SHIELD Act:**
- Notification within 60 days of breach
- Reasonable security measures
- Incident response plan

**Other State Breach Notification Laws:**
- Most states require 30-60 day notification
- Notification to affected individuals
- Notification to state attorney general
- News media notification (if >500 affected)

## Third-Party App Governance

### App Vetting Requirements

**Security Assessment:**
```
Vulnerability Scanning:
├─ OWASP Top 10 testing
├─ Dependency vulnerability scanning
├─ Code quality analysis
├─ Penetration testing
├─ Cryptography review
└─ Documentation of findings

Risk Score:
├─ CVSS vulnerability score
├─ Overall risk rating
├─ Conditional approval capability
└─ Annual re-assessment required
```

**Privacy Evaluation:**
```
Privacy Policy Review:
├─ Data collection transparency
├─ Use and sharing limitations
├─ Retention and deletion policies
├─ User consent and control
├─ Contact information
└─ Legal compliance statement

Data Handling:
├─ Patient PHI protection
├─ Encryption standards
├─ Access logging
├─ Data breach procedures
└─ User data minimization
```

**Clinical/Safety Review:**
```
Clinical Appropriateness:
├─ Scope of intended use
├─ Accuracy of clinical content
├─ Safety of recommendations
├─ Research basis
└─ Limitations and disclaimers
```

### App Management Platform Requirements

```
App Management System:
├─ Registry of approved applications
├─ Automated vetting workflow
├─ Continuous monitoring
├─ Annual recertification
├─ User feedback collection
├─ Incident response capability
├─ Removal procedures
└─ Documentation and audit trail
```

## Compliance Audit Preparation

### Pre-Audit Assessment

```
60 Days Before Audit:
├─ Review all engagement technology
├─ Verify HIPAA compliance
├─ Check accessibility (WCAG)
├─ Audit third-party apps
├─ Review policies and procedures
├─ Assess staff training
├─ Confirm encryption standards
└─ Test disaster recovery

30 Days Before:
├─ Address identified gaps
├─ Update documentation
├─ Train audit coordinators
├─ Prepare evidence packages
├─ Schedule policy reviews
└─ Test audit response procedures
```

### Documentation and Evidence

**Required Documentation:**
- Privacy and Security Policies (current versions)
- Risk Assessment Reports (annual)
- Business Associate Agreements (all active)
- Audit Logs (6 years retention)
- Training Records (documented completion)
- Breach Investigation Reports (if applicable)
- HIPAA Policies and Procedures Manual
- Privacy Notice and Acknowledgment Forms
- Authorization Forms and Tracking
- Incident Response Plan and Testing Records

**Evidence of Compliance:**
- System screenshots (security controls)
- Configuration documentation
- Penetration test reports
- Vulnerability remediation records
- Encryption verification
- Access control audits
- Staff training materials and records
- Patient education materials
- Complaint log and resolution

## Compliance Monitoring and Maintenance

### Continuous Compliance Program

```
Monthly Activities:
├─ Review security incidents
├─ Audit log sampling and review
├─ Access control review
└─ Compliance dashboard monitoring

Quarterly:
├─ Security event review
├─ Policy compliance assessment
├─ Training status review
├─ Vulnerability scanning
└─ Backup and recovery testing

Annually:
├─ Comprehensive risk assessment
├─ Security audit by internal/external party
├─ All policies review and update
├─ Workforce training completion
├─ BAA review and renewal
├─ Third-party app recertification
├─ Disaster recovery plan testing
└─ Compliance audit preparation
```

### Non-Compliance Response

**Issues Identified:**
1. Assess severity and risk
2. Develop corrective action plan
3. Assign responsibility and timeline
4. Implement fixes
5. Test and verify
6. Document resolution
7. Monitor for recurrence
8. Report to leadership

**Documentation:**
- Date identified
- Issue description
- Risk assessment
- Corrective action taken
- Completion date
- Verification method
- Responsible party
- Follow-up timeline
