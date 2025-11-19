# Compliance Frameworks Reference

## Introduction

Compliance frameworks provide structured approaches to implementing security controls and demonstrating regulatory adherence. This reference covers major compliance frameworks relevant to cloud computing: SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR, and FedRAMP.

## SOC 2 (Service Organization Control 2)

### Overview
- **Purpose**: Assurance on security, availability, processing integrity, confidentiality, and privacy
- **Issuer**: American Institute of CPAs (AICPA)
- **Scope**: Service organizations (SaaS, cloud providers, data centers)
- **Types**: Type I (point-in-time), Type II (3-12 month period)

### Trust Services Criteria (TSC)

**CC1: Control Environment**
- Integrity and ethical values
- Board oversight
- Organizational structure and assignment of authority
- Commitment to competence
- Accountability

**CC2: Communication and Information**
- Information quality and communication
- Internal communication
- External communication

**CC3: Risk Assessment**
- Risk identification and assessment
- Fraud risk assessment
- Significant changes assessment

**CC4: Monitoring Activities**
- Ongoing and separate evaluations
- Remediation of deficiencies

**CC5: Control Activities**
- Selection and development of control activities
- Technology controls
- Policies and procedures deployment

**CC6: Logical and Physical Access Controls**
- Access control policies and procedures
- Authorization and provisioning
- Authentication and access management
- Removal of access rights
- Physical access controls
- Logical access controls

**CC7: System Operations**
- System operation management
- System monitoring and incident detection
- System backup and recovery
- Configuration management

**CC8: Change Management**
- Change management procedures
- Change authorization and testing
- Emergency change procedures

**CC9: Risk Mitigation**
- Risk identification and mitigation
- Vendor and business partner management
- System integrity and security breaches

### Cloud-Relevant Controls

**Identity and Access Management** (CC6):
- Implement MFA for all users
- Least privilege access control
- Regular access reviews (quarterly)
- Deactivate accounts promptly when access no longer required
- Strong password policies

**Example Implementation**:
```
Control: CC6.1 - Authentication
Implementation:
- MFA enforced via Azure AD Conditional Access
- Password policy: 12+ characters, complexity, 90-day expiration
- Failed login monitoring and account lockout (5 attempts)
- SSO via SAML 2.0 for employee access
```

**Encryption** (CC6.7, A1.2):
- Data at rest encryption (AES-256)
- Data in transit encryption (TLS 1.2+)
- Key management procedures
- Encryption key rotation

**Monitoring and Logging** (CC7.2):
- Centralized logging (SIEM)
- Log retention (minimum 1 year)
- Security event monitoring and alerting
- Log integrity protection

**Incident Response** (CC7.3):
- Documented incident response plan
- Incident detection and escalation procedures
- Post-incident review and lessons learned
- Communication plan (internal and external)

### SOC 2 Audit Process
1. **Planning** (1-2 months): Scope definition, control selection, readiness assessment
2. **Readiness Assessment** (2-4 months): Gap analysis, control implementation, evidence collection
3. **Type I Audit** (Optional): Point-in-time assessment, control design evaluation
4. **Observation Period** (3-12 months): Controls operating effectively, evidence collection
5. **Type II Audit**: Operating effectiveness testing, final report issuance
6. **Ongoing Compliance**: Continuous monitoring, annual re-certification

### Cloud Mapping
- **AWS**: AWS Artifact for SOC 2 reports, AWS Config for control validation
- **Azure**: Microsoft Compliance Manager, Azure Policy
- **GCP**: GCP Compliance Reports Manager, Asset Inventory

## ISO 27001:2022

### Overview
- **Purpose**: Information Security Management System (ISMS) certification
- **Issuer**: International Organization for Standardization (ISO)
- **Scope**: Any organization managing sensitive information
- **Certification**: Third-party audit, 3-year validity with annual surveillance audits

### ISO 27001 Structure

**Clause 4-10** (Main Requirements):
- 4: Context of the organization
- 5: Leadership
- 6: Planning (risk assessment and treatment)
- 7: Support (resources, competence, awareness, communication)
- 8: Operation (risk treatment implementation)
- 9: Performance evaluation (monitoring, measurement, analysis, evaluation, internal audit, management review)
- 10: Improvement (nonconformity and corrective action, continual improvement)

**Annex A Controls** (93 controls in 4 categories):

**A.5: Organizational Controls (37 controls)**
- A.5.1: Information security policies
- A.5.7: Threat intelligence
- A.5.8: Information security in project management
- A.5.10: Acceptable use of information and assets
- A.5.15: Access control
- A.5.23: Information security for use of cloud services

**A.6: People Controls (8 controls)**
- A.6.1: Screening
- A.6.2: Terms and conditions of employment
- A.6.3: Information security awareness, education, and training
- A.6.5: Responsibilities after termination or change of employment

**A.7: Physical Controls (14 controls)**
- A.7.1: Physical security perimeters
- A.7.2: Physical entry
- A.7.4: Physical security monitoring
- A.7.7: Clear desk and clear screen

**A.8: Technological Controls (34 controls)**
- A.8.1: User endpoint devices
- A.8.5: Secure authentication
- A.8.9: Configuration management
- A.8.10: Information deletion
- A.8.16: Monitoring activities
- A.8.23: Web filtering
- A.8.24: Use of cryptography
- A.8.26: Application security requirements

### Key Cloud Controls

**A.5.23: Information security for use of cloud services**:
- Cloud service provider (CSP) security evaluation
- Shared responsibility model understanding
- Data location and sovereignty
- Service agreement and SLAs

**A.8.24: Use of cryptography**:
- Encryption policy and procedures
- Key management lifecycle
- Cryptographic algorithms (approved standards)
- Cloud KMS usage (AWS KMS, Azure Key Vault, GCP Cloud KMS)

**A.8.16: Monitoring activities**:
- Security monitoring and logging
- SIEM implementation (AWS Security Hub, Azure Sentinel, Chronicle)
- Anomaly detection
- Audit trail retention

**A.8.5: Secure authentication**:
- MFA enforcement
- SSO implementation
- Password policies
- Service account management

### Risk Treatment Plan (Required)

**Risk Assessment**:
```
Risk ID: RISK-001
Asset: Customer PII in S3 bucket
Threat: Unauthorized access due to misconfiguration
Likelihood: Medium
Impact: High
Risk Level: High

Treatment: Accept / Mitigate / Transfer / Avoid
Selected: Mitigate

Controls:
- A.8.24: Enable S3 bucket encryption (SSE-KMS)
- A.5.15: Implement bucket policy (deny public access)
- A.8.16: Enable CloudTrail logging for bucket access
- A.8.10: Implement lifecycle policy for data deletion

Residual Risk: Low
```

### ISO 27001 Certification Process
1. **Gap Analysis**: Compare current state to ISO 27001 requirements
2. **ISMS Implementation**: Establish policies, procedures, controls
3. **Risk Assessment**: Identify risks and define treatment plan
4. **Internal Audit**: Validate control implementation and effectiveness
5. **Management Review**: Senior leadership review of ISMS
6. **Stage 1 Audit**: Documentation review by certification body
7. **Stage 2 Audit**: On-site assessment of control effectiveness
8. **Certification**: 3-year certificate issued
9. **Surveillance Audits**: Annual audits to maintain certification
10. **Recertification**: Full audit every 3 years

### Cloud Mapping
- **AWS**: ISO 27001 certified, reports in AWS Artifact
- **Azure**: ISO 27001 certified, Service Trust Portal
- **GCP**: ISO 27001 certified, Compliance Reports Manager

## PCI DSS (Payment Card Industry Data Security Standard)

### Overview
- **Purpose**: Protect cardholder data
- **Issuer**: PCI Security Standards Council
- **Scope**: Organizations storing, processing, or transmitting cardholder data
- **Levels**: 1-4 based on transaction volume
- **Version**: 4.0 (March 2024 compliance required)

### PCI DSS Requirements

**1. Install and Maintain Network Security Controls**
- 1.1: Network security controls (firewalls, network segmentation)
- 1.2: Network security controls applied to all components
- 1.3: Network access to/from CDE restricted
- 1.4: Network security controls between trusted/untrusted networks
- 1.5: Network security controls manage risks from computing devices

**2. Apply Secure Configurations**
- 2.1: Secure configuration processes maintained
- 2.2: Secure configurations applied to all components
- 2.3: Wireless security controls
- 2.4: Primary account numbers (PAN) protected

**3. Protect Stored Account Data**
- 3.1: SAD (Sensitive Authentication Data) retention and disposal
- 3.2: SAD not stored after authorization
- 3.3: PAN secured when stored
- 3.4: PAN protected with cryptography
- 3.5: Encryption keys protected
- 3.6: Cryptographic key management

**4. Protect Cardholder Data in Transit**
- 4.1: PAN transmission risk management
- 4.2: PAN protected with cryptography during transmission (TLS 1.2+)

**5. Protect Systems from Malicious Software**
- 5.1: Malware protection maintained
- 5.2: Malware protection deployed
- 5.3: Anti-malware kept current
- 5.4: Anti-malware protection cannot be disabled

**6. Develop and Maintain Secure Systems**
- 6.1: Security vulnerability management
- 6.2: Bespoke/custom software securely developed
- 6.3: Security vulnerabilities identified and addressed
- 6.4: Web applications protected from attacks (WAF)
- 6.5: Changes to system components managed securely

**7. Restrict Access to System Components and Cardholder Data**
- 7.1: Access to system components and data limited by business need to know
- 7.2: User access assigned and managed
- 7.3: Access to system components and data by application and system accounts

**8. Identify Users and Authenticate Access**
- 8.1: User identification management
- 8.2: User authentication management
- 8.3: MFA for access to CDE
- 8.4: MFA implementation for all access
- 8.5: MFA systems securely configured
- 8.6: Authentication credentials management

**9. Restrict Physical Access to Cardholder Data**
- 9.1: Physical access controls
- 9.2: Physical access controls for sensitive areas
- 9.3: Physical access for personnel and visitors
- 9.4: Media physically secured
- 9.5: Point-of-interaction (POI) devices protected

**10. Log and Monitor All Access**
- 10.1: Logging processes and mechanisms
- 10.2: Audit logs capture activity
- 10.3: Audit logs protected from destruction
- 10.4: Audit logs reviewed
- 10.5: Audit log history retained and available
- 10.6: Time synchronization mechanisms
- 10.7: Detection and response to security failures

**11. Test Security of Systems and Networks**
- 11.1: Security testing procedures
- 11.2: Wireless access points detected and monitored
- 11.3: Vulnerabilities identified and addressed
- 11.4: Internal and external penetration testing
- 11.5: Intrusion detection/prevention deployed
- 11.6: Unauthorized changes detected and alerted

**12. Support Information Security with Organizational Policies**
- 12.1: Information security policy
- 12.2: Acceptable use policies
- 12.3: Risk assessment processes
- 12.4: PCI DSS compliance managed
- 12.5: PCI DSS scope documented
- 12.6: Security awareness training
- 12.7: Personnel screening
- 12.8: Risk to service providers managed
- 12.9: TPSPs (Third Party Service Providers) acknowledge responsibility
- 12.10: Incident response plan

### Cloud-Specific Requirements

**Network Segmentation (Req 1.3)**:
```
Internet → WAF → ALB (Public Subnet)
                   ↓
           App Servers (Private Subnet, CDE)
                   ↓
           RDS (Isolated Subnet, CDE)

Non-CDE resources in separate VPC
VPC Peering with specific security group rules
```

**Encryption (Req 3.4, 4.2)**:
- AES-256 for data at rest (RDS, EBS, S3)
- TLS 1.2+ for data in transit
- Strong cryptography (no deprecated algorithms)
- Key management with AWS KMS/Azure Key Vault/GCP Cloud KMS

**Access Control (Req 7, 8)**:
- Individual user accounts (no shared credentials)
- MFA for all CDE access
- Least privilege IAM policies
- Role-based access control
- Access reviews every 6 months

**Logging (Req 10)**:
- CloudTrail/Activity Logs/Cloud Audit Logs enabled
- 1-year retention minimum
- Centralized logging (CloudWatch/Azure Monitor/Cloud Logging)
- Log review (daily for critical systems)
- Time synchronization (NTP)

**Vulnerability Management (Req 6, 11)**:
- Quarterly vulnerability scans (ASV approved vendor)
- Annual penetration testing
- Patch management (critical patches within 30 days)
- Web application security (OWASP Top 10)
- Change management procedures

### PCI DSS Validation
- **Level 1**: Annual Report on Compliance (ROC) by QSA, quarterly ASV scans
- **Level 2-4**: Self-Assessment Questionnaire (SAQ), quarterly ASV scans
- **Merchants**: Level based on annual transaction volume
- **Service Providers**: Level based on stored/transmitted transactions

### Cloud Mapping
- **AWS**: PCI DSS Level 1 Service Provider, Artifact for AOC
- **Azure**: PCI DSS Level 1 Service Provider, Service Trust Portal
- **GCP**: PCI DSS Level 1 Service Provider, Compliance Reports Manager

## HIPAA (Health Insurance Portability and Accountability Act)

### Overview
- **Purpose**: Protect patient health information (PHI)
- **Issuer**: U.S. Department of Health and Human Services (HHS)
- **Scope**: Covered entities (healthcare providers, health plans, clearinghouses) and business associates
- **Enforcement**: OCR (Office for Civil Rights), penalties up to $1.5M per violation category per year

### HIPAA Security Rule

**Administrative Safeguards** (§164.308):
- (a)(1) Security Management Process: Risk analysis, risk management, sanction policy, information system activity review
- (a)(2) Assigned Security Responsibility
- (a)(3) Workforce Security: Authorization/supervision, clearance procedure, termination procedures
- (a)(4) Information Access Management: Isolate healthcare clearinghouse functions, access authorization, access establishment/modification
- (a)(5) Security Awareness and Training
- (a)(6) Security Incident Procedures
- (a)(7) Contingency Plan: Data backup, disaster recovery, emergency mode, testing/revision, applications and data criticality analysis
- (a)(8) Evaluation
- (a)(9) Business Associate Contracts

**Physical Safeguards** (§164.310):
- (a) Facility Access Controls: Contingency operations, facility security plan, access control/validation procedures
- (b) Workstation Use and Security
- (c) Device and Media Controls: Disposal, media re-use, accountability, data backup/storage

**Technical Safeguards** (§164.312):
- (a)(1) Access Control: Unique user identification (R), emergency access (R), automatic logoff (A), encryption and decryption (A)
- (a)(2) Audit Controls: Hardware, software, procedures to record/examine access and activity
- (c) Integrity Controls: Mechanisms to authenticate ePHI
- (d) Person or Entity Authentication: Verify identity before granting access
- (e) Transmission Security: Integrity controls (A), encryption (A)

**Legend**: R = Required, A = Addressable (implement or document why alternative is equivalent or why not reasonable/appropriate)

### Cloud Implementation

**Encryption** (§164.312(a)(2)(iv), §164.312(e)(2)(ii)):
- **At Rest**: RDS encryption, EBS encryption, S3 encryption (AES-256, KMS)
- **In Transit**: TLS 1.2+, VPN, Direct Connect/ExpressRoute/Interconnect
- **Addressable**: Document encryption implementation or alternative safeguards

**Access Controls** (§164.312(a)):
- Unique user IDs (IAM users, Azure AD, Google Cloud Identity)
- MFA for all users accessing ePHI
- Role-based access control (least privilege)
- Automatic logoff (session timeouts)
- Emergency access procedures (break-glass accounts)

**Audit Logging** (§164.312(b)):
- Enable CloudTrail/Activity Logs/Cloud Audit Logs
- Log all access to ePHI
- Centralized logging (CloudWatch/Azure Monitor/Cloud Logging)
- 6-year retention (match HIPAA record retention)
- Regular log review

**Integrity Controls** (§164.312(c)):
- Checksums and hashing (S3 ETags, Azure Blob checksums)
- Version control for ePHI modifications
- Detect unauthorized alterations
- CloudTrail integrity validation

**Disaster Recovery** (§164.308(a)(7)):
- Automated backups (RDS, Azure SQL, Cloud SQL)
- Multi-region replication
- Recovery time objective (RTO): Document acceptable downtime
- Recovery point objective (RPO): Document acceptable data loss
- Regular backup testing

**Business Associate Agreement (BAA)**:
- Required for covered entities using cloud services with PHI
- **AWS**: BAA available via AWS Artifact
- **Azure**: BAA via Microsoft Online Services Terms
- **GCP**: BAA via GCP BAA form
- Cloud provider responsibilities and covered entity responsibilities

### HIPAA Breach Notification

**Breach Definition**: Unauthorized acquisition, access, use, or disclosure of PHI that compromises security or privacy

**Notification Requirements**:
- **Individuals**: Within 60 days of breach discovery
- **HHS**: Within 60 days (500+ individuals) or annually (fewer than 500)
- **Media**: If breach affects 500+ residents of a state or jurisdiction
- **Business Associates**: Notify covered entity within 60 days

**Cloud Incident Response**:
1. Detection: GuardDuty, Defender, SCC, CloudTrail anomalies
2. Investigation: Scope determination, affected PHI
3. Containment: Isolate affected systems, revoke credentials
4. Notification: Follow HIPAA timelines
5. Remediation: Fix vulnerabilities, enhance controls
6. Post-incident: Lessons learned, update procedures

### HIPAA Compliance Validation
- Self-assessment using HHS audit protocol
- Risk analysis (annual, after significant changes)
- Third-party HIPAA audit (optional, recommended)
- OCR audits (random or complaint-driven)

## GDPR (General Data Protection Regulation)

### Overview
- **Purpose**: Protect EU data subjects' personal data
- **Issuer**: European Union
- **Scope**: Organizations processing EU residents' personal data (regardless of location)
- **Enforcement**: Data Protection Authorities (DPAs), fines up to €20M or 4% of annual global turnover

### Key Principles (Article 5)

1. **Lawfulness, Fairness, Transparency**: Lawful basis for processing, transparent privacy notices
2. **Purpose Limitation**: Collect for specified, explicit, legitimate purposes
3. **Data Minimization**: Adequate, relevant, limited to necessary
4. **Accuracy**: Accurate and kept up to date
5. **Storage Limitation**: Kept only as long as necessary
6. **Integrity and Confidentiality**: Appropriate security measures
7. **Accountability**: Demonstrate compliance

### Data Subject Rights

- **Right to Access** (Article 15): Copy of personal data, processing information
- **Right to Rectification** (Article 16): Correct inaccurate data
- **Right to Erasure** (Article 17): "Right to be forgotten"
- **Right to Restrict Processing** (Article 18)
- **Right to Data Portability** (Article 20): Machine-readable format
- **Right to Object** (Article 21): Object to processing
- **Rights related to Automated Decision Making** (Article 22)

### Cloud Security Measures (Article 32)

**Security of Processing**:
- Pseudonymization and encryption of personal data
- Ongoing confidentiality, integrity, availability, resilience
- Ability to restore availability and access in timely manner
- Regular testing, assessment, evaluation of effectiveness

**Cloud Implementation**:
```
Encryption:
- At Rest: AES-256 (KMS/Key Vault/Cloud KMS)
- In Transit: TLS 1.3
- Pseudonymization: Tokenization, data masking

Access Controls:
- RBAC with least privilege
- MFA enforcement
- Regular access reviews
- Audit logging (who accessed what data)

Data Residency:
- EU-region storage (eu-west-1, westeurope, europe-west1)
- No cross-border transfers without safeguards
- Standard Contractual Clauses (SCCs) when needed

Availability and Resilience:
- Multi-AZ/zone deployment
- Automated backups
- Disaster recovery plan
- Incident response plan
```

### Data Processing Agreement (DPA)

**Required Elements**:
- Subject matter and duration of processing
- Nature and purpose of processing
- Type of personal data and categories of data subjects
- Controller and processor obligations and rights
- Sub-processor requirements
- Security measures
- Data breach notification procedures
- Assistance with data subject requests
- Deletion or return of data after termination

**Cloud Provider DPAs**:
- **AWS**: AWS GDPR Data Processing Addendum
- **Azure**: Microsoft Online Services DPA
- **GCP**: Google Cloud Data Processing Addendum

### Cross-Border Data Transfers

**Transfer Mechanisms**:
1. **Adequacy Decision**: EU Commission determines non-EU country has adequate protection
2. **Standard Contractual Clauses (SCCs)**: EU Commission-approved contract templates
3. **Binding Corporate Rules (BCRs)**: Internal rules for multinational companies
4. **Derogations**: Explicit consent, performance of contract, legal claims

**Post-Schrems II**:
- Transfer Impact Assessment (TIA) required
- Assess if recipient country's laws allow government access
- Implement supplementary measures (encryption, access controls)

### Data Protection Impact Assessment (DPIA)

**When Required** (Article 35):
- Systematic and extensive profiling with legal effects
- Processing special categories of data at large scale
- Systematic monitoring of publicly accessible areas at large scale
- High risk to rights and freedoms

**DPIA Contents**:
1. Description of processing operations and purposes
2. Assessment of necessity and proportionality
3. Assessment of risks to data subjects
4. Measures to address risks
5. Safeguards, security measures, mechanisms

### GDPR Compliance Steps
1. **Data Mapping**: Identify what personal data you process, where, why, who has access
2. **Lawful Basis**: Determine lawful basis for each processing activity
3. **Privacy Notices**: Transparent, clear privacy policy
4. **Consent Management**: If using consent, implement consent capture and withdrawal
5. **Data Subject Requests**: Implement procedures for all rights
6. **DPAs**: Ensure all processors have signed DPAs
7. **Security Measures**: Implement Article 32 technical and organizational measures
8. **Breach Notification**: 72-hour notification to DPA, procedures in place
9. **DPO**: Appoint DPO if required
10. **DPIA**: Conduct for high-risk processing
11. **Data Transfers**: Implement transfer mechanisms for non-EU transfers
12. **Records of Processing**: Maintain Article 30 records

## FedRAMP (Federal Risk and Authorization Management Program)

### Overview
- **Purpose**: Standardized approach to security assessment, authorization, and continuous monitoring for cloud products and services used by U.S. federal agencies
- **Issuer**: U.S. General Services Administration (GSA)
- **Scope**: Cloud service providers (CSPs) offering services to U.S. federal government
- **Levels**: Low, Moderate, High (based on impact)

### Impact Levels

**Low Impact**: Loss of confidentiality, integrity, or availability has limited adverse effect
- FIPS 199 Low categorization
- 125 security controls (NIST 800-53 Rev 5)
- Annual assessment

**Moderate Impact**: Loss has serious adverse effect
- FIPS 199 Moderate categorization
- 325+ security controls
- Annual assessment, most common level

**High Impact**: Loss has severe or catastrophic adverse effect
- FIPS 199 High categorization
- 421 security controls
- Significant controls enhancement
- More stringent requirements

### Authorization Paths

**1. Agency Authorization**:
- Specific agency grants FedRAMP authorization (ATO)
- Other agencies can leverage authorization
- Faster, less expensive than JAB

**2. JAB Provisional Authorization (P-ATO)**:
- Joint Authorization Board (DoD, DHS, GSA)
- More rigorous review process
- Higher market recognition
- Baseline authorization, agencies still need ATO

**3. CSP Supplied Package**:
- CSP completes security package
- Reviewed by FedRAMP PMO
- Agencies can use for authorization
- Least recognition, most flexibility

### Key Security Controls (Sample)

**AC-2: Account Management**:
- Automated account provisioning/deprovisioning
- Account review every 90 days
- Privileged account management
- Automated disabling of inactive accounts (90 days)

**IA-2: Identification and Authentication**:
- Unique user identification
- MFA for privileged access (High: all access)
- PIV/CAC card support for federal users
- Re-authentication (High: every 30 minutes)

**AU-2: Audit Logging**:
- Comprehensive audit logging
- Centralized log management
- Log retention (High: 1 year online, 3 years archive)
- Automated log analysis and alerting

**SC-7: Boundary Protection**:
- Network segmentation
- Deny by default, allow by exception
- DMZ architecture
- Encryption for external communications (FIPS 140-2 validated)

**CP-9: System Backup**:
- Automated backups
- Test restoration quarterly
- Offsite storage (separate location)
- Backup encryption

### FIPS 140-2 Requirements

**High Impact**:
- FIPS 140-2 Level 3 for key management
- FIPS 140-2 Level 2 for other cryptographic modules

**Moderate Impact**:
- FIPS 140-2 Level 2 overall acceptable
- FIPS 140-2 validated modules for all cryptographic operations

**Cloud Provider Support**:
- **AWS**: AWS KMS (FIPS 140-2 Level 2), CloudHSM (Level 3)
- **Azure**: Key Vault (Level 2), Managed HSM (Level 3)
- **GCP**: Cloud KMS (Level 3), Cloud HSM (Level 3)

### Continuous Monitoring

**Monthly**:
- Vulnerability scanning
- POA&M updates
- Significant change reporting

**Quarterly**:
- Updated security control inventory
- Updated system security plan

**Annually**:
- Full security assessment by 3PAO
- Penetration testing
- Security plan review

### FedRAMP Authorization Process
1. **Preparation**: Understand requirements, gap analysis, select 3PAO
2. **Documentation**: Develop SSP, PTA, Policy documents, Procedures
3. **FedRAMP Review**: FedRAMP PMO reviews SSP (CSP Supplied Path)
4. **Assessment**: 3PAO performs assessment, produces SAR
5. **Remediation**: Address findings, update POA&M
6. **Authorization**: Agency or JAB grants ATO/P-ATO
7. **Continuous Monitoring**: Monthly vulnerability scans, annual assessments
8. **Ongoing**: Maintain authorization, report changes, address findings

### Cloud Mapping
- **AWS GovCloud**: Designed for FedRAMP compliance
- **Azure Government**: FedRAMP High authorized
- **GCP (Google Government Cloud)**: FedRAMP Moderate and High services

## Compliance Comparison Matrix

| Aspect | SOC 2 | ISO 27001 | PCI DSS | HIPAA | GDPR | FedRAMP |
|--------|-------|-----------|---------|-------|------|---------|
| **Geography** | Global | Global | Global | U.S. | EU/EEA | U.S. Federal |
| **Scope** | Service orgs | Any org | Card data | PHI/ePHI | Personal data | Cloud CSPs |
| **Certification** | Report (not cert) | Certificate | Validation | Self-assessment | Self-assessment | ATO/P-ATO |
| **Validity** | 12 months | 3 years | 12 months | Ongoing | Ongoing | 3 years |
| **Audit Frequency** | Annual | Annual surv. + 3yr | Annual/Quarterly | As needed | As needed | Annual |
| **Penalties** | Contractual | Certification loss | Fines, card suspension | Up to $1.5M/yr | Up to 4% revenue | Loss of ATO |
| **Encryption Req** | Addressable | Required | Required | Addressable | Required | Required (FIPS) |
| **MFA Requirement** | Addressable | Recommended | Required (CDE) | Addressable | Recommended | Required |
| **Log Retention** | 1 year | Risk-based | 1 year (3 months online) | 6 years | Per purpose | 1-3 years |

## Multi-Framework Compliance

### Overlapping Controls
Many controls satisfy multiple frameworks simultaneously:

**MFA Implementation**:
- ✅ SOC 2: CC6.1
- ✅ ISO 27001: A.8.5
- ✅ PCI DSS: Requirement 8.3-8.5
- ✅ HIPAA: §164.312(a)(2)(i)
- ✅ GDPR: Article 32 (security measures)
- ✅ FedRAMP: IA-2

**Encryption at Rest**:
- ✅ SOC 2: CC6.7, A1.2
- ✅ ISO 27001: A.8.24
- ✅ PCI DSS: Requirement 3.4
- ✅ HIPAA: §164.312(a)(2)(iv)
- ✅ GDPR: Article 32
- ✅ FedRAMP: SC-13, SC-28

**Audit Logging**:
- ✅ SOC 2: CC7.2
- ✅ ISO 27001: A.8.16
- ✅ PCI DSS: Requirement 10
- ✅ HIPAA: §164.312(b)
- ✅ GDPR: Article 32
- ✅ FedRAMP: AU family

### Control Mapping Strategy
1. Identify all applicable frameworks
2. Map controls across frameworks
3. Implement superset of requirements (highest bar)
4. Document how each control satisfies multiple frameworks
5. Single evidence collection for multiple audits

## Resources

### Official Standards
- SOC 2: https://www.aicpa.org/soc4so
- ISO 27001: https://www.iso.org/standard/27001
- PCI DSS: https://www.pcisecuritystandards.org/
- HIPAA: https://www.hhs.gov/hipaa/
- GDPR: https://gdpr.eu/
- FedRAMP: https://www.fedramp.gov/

### Cloud Provider Compliance
- AWS Compliance: https://aws.amazon.com/compliance/
- Azure Compliance: https://docs.microsoft.com/azure/compliance/
- GCP Compliance: https://cloud.google.com/security/compliance

### Assessment Tools
- AWS Audit Manager, AWS Config
- Microsoft Compliance Manager, Azure Policy
- GCP Security Command Center, Asset Inventory
- Third-party: Vanta, Drata, Secureframe, Tugboat Logic
