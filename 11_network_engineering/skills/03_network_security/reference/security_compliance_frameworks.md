# Security Compliance Frameworks Reference

## Overview of Frameworks

### Regulatory vs Framework

**Regulatory Standards (Mandatory)**
- PCI-DSS: Payment card processing
- HIPAA: Healthcare data
- GDPR: European data protection
- CCPA: California consumer privacy

**Framework Standards (Best Practices)**
- NIST Cybersecurity Framework
- ISO 27001: Information Security
- CIS Benchmarks
- COBIT: Governance

## PCI-DSS (Payment Card Industry Data Security Standard)

### Applicability

```
Who must comply:
- Credit card processors
- Merchants handling cards
- Any business storing/transmitting card data
- Acquirers, issuers, networks
- Service providers

Scope: Cardholder Data Environment (CDE)
- Systems storing/processing card data
- Not just point-of-sale

Level Determination:
- Level 1: >6M transactions/year (highest compliance)
- Level 2: 1-6M transactions/year
- Level 3: 20K-1M debit transactions/year
- Level 4: <20K transactions/year
```

### Key Requirements

#### Requirement 1: Firewall Configuration
```
Controls:
- Firewall architecture required
- DMZ for card processing
- Firewall rules documented
- Tested annual
```

#### Requirement 2: No Default Passwords
```
Controls:
- Change vendor defaults
- Remove unnecessary accounts
- Document all credentials
```

#### Requirement 3: Data Protection
```
Controls:
- Encryption in transit
- Encryption at rest
- Key management
- Data minimization
```

#### Requirement 4: Access Control
```
Controls:
- Unique user IDs
- Strong passwords
- Restrict by role
- Physical access controls
```

#### Requirement 5: Monitoring & Testing
```
Controls:
- Antivirus required
- Malware scanning
- Vulnerability scans
- Penetration testing (annually)
- Log monitoring
```

#### Requirement 6: Change Management
```
Controls:
- Configuration management
- Patch management
- Code reviews
- Test environments
- Change approval process
```

#### Requirement 7: Audit Logging
```
Controls:
- Log all access to CDE
- Centralized log management
- Regular log review
- Automated analysis
- 1-year retention (3 months online)
```

#### Requirement 8: Compliance Validation
```
Controls:
- Document scope
- Annual audits
- Quarterly scans
- Attestation of compliance
- Maintain documentation
```

### Network Segmentation for PCI-DSS

```
CDE (Cardholder Data Environment):
- Separate VLAN
- Firewall-protected
- Limited access
- Encrypted channels
- Dedicated systems

Example Network:
┌─────────────────────────────────┐
│ External Network                │
└────────────┬────────────────────┘
             │ [Firewall - rules logged]
             ▼
┌─────────────────────────────────┐
│ DMZ (Payment Gateway)           │
│ - Web servers receiving cards   │
│ - Tokenization system           │
│ - PCI-DSS scoped               │
└────────────┬────────────────────┘
             │ [Internal Firewall]
             ▼
┌─────────────────────────────────┐
│ Internal Database               │
│ - Vault with encrypted data     │
│ - Limited access (DBAs only)    │
│ - Encrypted connections         │
│ - Audit logging                 │
└─────────────────────────────────┘
```

## HIPAA (Health Insurance Portability and Accountability Act)

### HIPAA Components

#### 1. Privacy Rule
```
Protects: Protected Health Information (PHI)
Applies to: Healthcare providers, plans, clearinghouses
Requirements:
- Notice of privacy practices
- Patient rights enforcement
- Authorized use/disclosure
- Individual access rights
```

#### 2. Security Rule
```
Protects: Electronic PHI (ePHI)
Applies to: Systems handling ePHI
Requirements:
- Administrative safeguards
- Physical safeguards
- Technical safeguards
- Organizational policies
```

#### 3. Breach Notification Rule
```
Requirement: Notify individuals of breach
Timeline: 60 days
Content: Breach description, types of data
Who: Affected individuals, Secretary of HHS, media
```

### Security Rule Requirements

#### Administrative Safeguards
```
1. Compliance Officer Designation
2. Risk Assessment (annual)
3. Risk Management Plan
4. System Audit Controls
5. Staff Security Awareness/Training
6. Information Access Management
7. Security Awareness/Training
8. Security Incident Procedures
9. Contingency Planning
10. Business Associate Agreements (BAAs)
11. Workforce Security
```

#### Physical Safeguards
```
1. Facility Access Controls
   - Visitor logs
   - Badge/key systems
   - Surveillance

2. Workstation Security
   - Physical locks
   - Screen placement
   - Monitor privacy filters

3. Workstation Use Policy
   - Approved use
   - User responsibilities

4. Device & Media Controls
   - Inventory tracking
   - Disposal procedures
   - Encryption for transport
```

#### Technical Safeguards
```
1. Access Controls
   - Unique user IDs
   - Emergency access
   - Encryption/decryption
   - Authentication (passwords, tokens)

2. Audit Controls
   - Logging (access, changes)
   - Log retention (6 years)
   - Real-time monitoring

3. Integrity Controls
   - Checksums
   - Digital signatures
   - Hash algorithms
   - Data integrity verification

4. Transmission Security
   - Encryption in transit
   - TLS 1.2 minimum
   - Certificates
   - Secure channels
```

## GDPR (General Data Protection Regulation)

### Scope
```
Applicability:
- Organizations processing EU residents' data
- Applies globally (if serving EU)
- "Data" = any personal information
- Extraterritorial reach
```

### Key Principles

#### 1. Lawfulness, Fairness, Transparency
```
Requirement:
- Legal basis for processing
- Fair to individuals
- Transparent about use
- Clear policies
```

#### 2. Purpose Limitation
```
Requirement:
- Collected for specific purpose
- Cannot repurpose without consent
- Secondary use limited
- Document purposes clearly
```

#### 3. Data Minimization
```
Requirement:
- Collect only necessary data
- Minimize data retention
- Delete when no longer needed
- Regular review/purge
```

#### 4. Accuracy
```
Requirement:
- Keep data accurate
- Up-to-date
- Allow corrections
- Remove inaccurate data
```

#### 5. Storage Limitation
```
Requirement:
- Retention periods defined
- Automatic deletion
- Regular reviews
- Audit trails maintained
```

#### 6. Integrity and Confidentiality
```
Requirement:
- Encryption in transit
- Encryption at rest
- Access controls
- Secure processing
- Incident procedures
```

#### 7. Accountability
```
Requirement:
- Document compliance
- Privacy impact assessments
- Data Processing Agreements
- Breach notification (72 hours)
- Maintain records
```

### Technical and Organizational Measures

```
Required:
- Encryption (AES-256+)
- Access controls (MFA)
- Audit logging
- Intrusion detection
- Regular security assessment
- Staff training
- Incident response plan
- Data Protection Officer
```

## CCPA (California Consumer Privacy Act)

### Covered Entities
```
Applies if:
- Collect personal information
- From California residents
- For business purposes
- Meet thresholds:
  * $25M+ revenue, OR
  * Buy/sell data on 100k+ people, OR
  * Buy/sell 25%+ revenue from data
```

### Consumer Rights

#### Right to Know
```
Consumers can request:
- Specific information collected
- Categories of sources
- Business purposes
- Recipients of information
```

#### Right to Delete
```
Consumers can request deletion:
- Personal information collected
- Exceptions:
  * Required by law
  * Fraud prevention
  * Security purposes
  * Aggregate reporting
```

#### Right to Opt-Out
```
Right to opt-out of:
- Sale of personal information
- Sharing for cross-context behavioral advertising
```

#### Right to Non-Discrimination
```
No discrimination for:
- Exercising privacy rights
- Different prices/terms
- Unless justified (cost, risk)
```

## NIST Cybersecurity Framework

### Framework Structure

```
┌──────────────────────────────────────────┐
│         Core Functions                   │
├──────────────────────────────────────────┤
│ 1. Identify   (Asset management)         │
│ 2. Protect   (Access, encryption)        │
│ 3. Detect    (Monitoring, detection)     │
│ 4. Respond   (Incident response)         │
│ 5. Recover   (Restoration, lessons)      │
└──────────────────────────────────────────┘
```

### Identify Function
```
Asset Management:
- Document assets
- Document data flows
- Know criticality
- Know interdependencies

Governance:
- Policies and procedures
- Risk management
- Leadership oversight
- Accountability

Risks Assessed:
- Vulnerability assessments
- Threat analysis
- Risk evaluation
- Impact analysis
```

### Protect Function
```
Access Control:
- Identity verification
- Authorization (RBAC)
- Physical access
- Least privilege

System Hardening:
- Baseline configurations
- Security patching
- Firewall rules
- Encryption

Data Security:
- Classification
- Encryption (transit/rest)
- Data loss prevention
- Secure disposal
```

### Detect Function
```
Continuous Monitoring:
- Log monitoring
- Network traffic analysis
- System monitoring
- File integrity monitoring

Detection Procedures:
- Anomaly detection
- Signature-based detection
- Alert tuning
- Escalation procedures

Awareness:
- Staff training
- Suspicious activity reporting
```

### Respond Function
```
Preparation:
- Incident response plan
- Roles and responsibilities
- Playbooks
- Communication procedures

Response:
- Detection and analysis
- Containment
- Eradication
- Recovery
```

### Recover Function
```
Restoration:
- Restore systems
- Verify integrity
- Resume operations
- Validate security

Improvement:
- Root cause analysis
- Process updates
- Policy improvements
- Training updates
```

## ISO 27001 (Information Security)

### Control Areas

#### A.5: Organizational Controls
```
- Policies and procedures
- Information security roles
- Awareness and training
- Supplier relationships
```

#### A.6: People Controls
```
- Screening
- Confidentiality agreements
- Discipline procedures
- Termination procedures
```

#### A.7: Asset Controls
```
- Asset classification
- Media handling
- Disposal procedures
- Removal of access rights
```

#### A.8: Access Controls
```
- User registration
- Access rights management
- Password policy
- Physical access
- Network access
```

#### A.9: Cryptography
```
- Encryption policy
- Key management
- Algorithm selection
- Secure communication
```

#### A.10: Physical & Environmental
```
- Secure perimeters
- Physical entry
- Utilities
- Equipment maintenance
- Clear desk/screen policy
```

#### A.11: Operations
```
- Operational procedures
- Separation of duties
- Change management
- Logging and monitoring
- Protection of systems
```

#### A.12: Communications
```
- Network security
- Network access control
- Web application security
- Email security
- Data transfer
```

#### A.13: Systems Development
```
- Secure development
- Change control
- Testing
- Vulnerability management
- Secure coding
```

#### A.14: Supplier Relations
```
- Requirements in contracts
- Information security reviews
- Incident management cooperation
```

## Compliance Assessment

### Assessment Process

```
Step 1: Scope Definition
- Identify applicable frameworks
- Determine requirements
- Document scope boundaries

Step 2: Gap Analysis
- Current state assessment
- Requirement mapping
- Identify gaps
- Prioritize remediation

Step 3: Remediation
- Design improvements
- Implement controls
- Test controls
- Document changes

Step 4: Validation
- Internal audit
- External assessment
- Address findings
- Continuous monitoring

Step 5: Maintenance
- Monitor compliance
- Update policies
- Annual reviews
- Continuous improvement
```

### Common Assessment Tools

```
PCI-DSS:
- Annual audit required
- Qualified Security Assessor (QSA)
- Vulnerability scanning (quarterly)
- Penetration testing (annually)

HIPAA:
- Security Risk Assessment (annual)
- Penetration testing recommended
- Vulnerability scanning
- System audit logs review

GDPR:
- Data Protection Impact Assessment (DPIA)
- Privacy by design
- Regular risk assessments
- Third-party audits
```

## Compliance Management

### Documentation Requirements

```
Keep records of:
- Policies and procedures
- Risk assessments
- Audit results
- Incident reports
- Training records
- Third-party agreements
- System configurations
- Log files
- Change records
```

### Retention Periods

```
PCI-DSS: 1 year + 3 months online
HIPAA: 6 years minimum
GDPR: As long as necessary
SOC 2: 1 year
GDPR Logs: Not specified (security focused)
```

### Continuous Improvement

```
Processes:
1. Collect metrics
2. Analyze trends
3. Identify improvements
4. Implement changes
5. Verify effectiveness
6. Document lessons learned
7. Update procedures
```
