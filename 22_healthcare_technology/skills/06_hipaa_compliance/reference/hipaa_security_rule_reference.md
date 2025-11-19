# HIPAA Security Rule Reference

## Overview

The HIPAA Security Rule (45 CFR Part 160 and Part 164, Subpart C) establishes national standards for protecting electronic Protected Health Information (ePHI). It applies to covered entities and business associates.

## Scope

### Applicability
- Applies ONLY to ePHI (electronic Protected Health Information)
- Does not apply to paper or oral PHI (covered by Privacy Rule)
- Includes ePHI created, received, maintained, or transmitted

### ePHI Definition
Protected Health Information that is:
- Transmitted by electronic media
- Maintained in electronic media
- Examples: EHRs, emails with PHI, databases, portable devices, removable media

## Standard Types

### Required Standards
Must be implemented as specified.

### Addressable Standards
- Assess whether reasonable and appropriate
- If not reasonable/appropriate:
  - Document why not reasonable/appropriate
  - Implement equivalent alternative measure if reasonable/appropriate
  - Document equivalent measure
- If no alternative is reasonable/appropriate:
  - Document why not implementing

## Administrative Safeguards

Standards and implementation specifications for managing security measures.

### 1. Security Management Process (§164.308(a)(1))
**Required Standard**

#### Risk Analysis (Required)
- Conduct accurate and thorough assessment of potential risks and vulnerabilities
- Identify ePHI locations
- Identify threats and vulnerabilities
- Assess current security measures
- Determine likelihood and impact of threats
- Document risk assessment findings

**Elements:**
- Scope definition (systems, applications, data)
- Data collection (asset inventory, data flow diagrams)
- Threat identification (natural, human, environmental)
- Vulnerability identification (technical, administrative, physical)
- Control analysis (existing safeguards)
- Likelihood determination
- Impact analysis
- Risk determination (likelihood × impact)
- Documentation (findings, recommendations, decisions)

#### Risk Management (Required)
- Implement security measures to reduce risks and vulnerabilities
- Prioritize based on risk level
- Develop remediation plan
- Assign responsibilities and timelines
- Allocate resources

#### Sanction Policy (Required)
- Apply appropriate sanctions against workforce members who violate policies
- Progressive discipline approach
- Document violations and sanctions
- Ensure consistent application

#### Information System Activity Review (Required)
- Implement procedures to regularly review records of information system activity
- Audit logs review
- Access reports analysis
- Incident logs examination
- Security alerts monitoring

### 2. Assigned Security Responsibility (§164.308(a)(2))
**Required Standard**

- Designate security official responsible for developing and implementing security policies
- Document designation
- Ensure appropriate authority and resources
- Not necessarily full-time position
- May be same as privacy official

### 3. Workforce Security (§164.308(a)(3))
**Required Standard**

#### Authorization and/or Supervision (Addressable)
- Implement procedures for authorization and/or supervision of workforce members
- Define access authorization process
- Establish supervision requirements
- Document authorization decisions

#### Workforce Clearance Procedure (Addressable)
- Determine workforce members' access based on role and need
- Background checks where appropriate
- Access level determination
- Periodic access review

#### Termination Procedures (Addressable)
- Terminate access when employment ends or when access no longer required
- Disable accounts immediately upon termination
- Retrieve access devices (badges, keys, tokens)
- Change shared passwords
- Remove physical access
- Document termination procedures

### 4. Information Access Management (§164.308(a)(4))
**Required Standard**

#### Isolating Healthcare Clearinghouse Functions (Required)
- If healthcare clearinghouse is part of larger organization, implement policies to protect ePHI from unauthorized access by larger organization

#### Access Authorization (Addressable)
- Implement policies and procedures for granting access to ePHI
- Based on job responsibilities and minimum necessary
- Formal access request and approval process
- Document access decisions

#### Access Establishment and Modification (Addressable)
- Implement procedures to establish, document, review, and modify user access rights
- New user provisioning
- Role changes and transfers
- Periodic access recertification
- Modification documentation

### 5. Security Awareness and Training (§164.308(a)(5))
**Required Standard**

#### Security Reminders (Addressable)
- Periodic security updates and reminders
- Newsletter, emails, posters
- Awareness campaigns
- Emerging threat notifications

#### Protection from Malicious Software (Addressable)
- Procedures for guarding against, detecting, and reporting malicious software
- Anti-virus/anti-malware training
- Phishing awareness
- Safe browsing practices
- Social engineering recognition

#### Log-in Monitoring (Addressable)
- Procedures for monitoring log-in attempts and reporting discrepancies
- Failed login attempt monitoring
- Unusual access pattern detection
- Geographic anomaly detection
- Reporting procedures

#### Password Management (Addressable)
- Procedures for creating, changing, and safeguarding passwords
- Password complexity requirements
- Password change frequency
- Password storage (no written passwords)
- Password sharing prohibition
- Multi-factor authentication

### 6. Security Incident Procedures (§164.308(a)(6))
**Required Standard**

#### Response and Reporting (Required)
- Identify and respond to suspected or known security incidents
- Mitigate harmful effects
- Document incidents and outcomes

**Incident Response Process:**
1. Detection and reporting
2. Incident classification
3. Containment
4. Investigation
5. Eradication
6. Recovery
7. Post-incident review
8. Documentation

### 7. Contingency Plan (§164.308(a)(7))
**Required Standard**

#### Data Backup Plan (Required)
- Establish and implement procedures for backup of exact copies of ePHI
- Frequency: regular and consistent
- Location: secure off-site storage
- Testing: verify recoverability
- Retention: align with legal/business requirements

#### Disaster Recovery Plan (Required)
- Establish and implement procedures to restore lost data
- Recovery procedures documented
- Recovery time objectives (RTO) defined
- Recovery point objectives (RPO) defined
- Annual testing required

#### Emergency Mode Operation Plan (Required)
- Enable continuation of critical business processes for ePHI protection while operating in emergency mode
- Critical function identification
- Alternative processing procedures
- Communication plans
- Resource requirements

#### Testing and Revision Procedures (Addressable)
- Implement procedures for periodic testing and revision of contingency plans
- Annual testing recommended
- Tabletop exercises
- Full-scale testing
- Update based on test results

#### Applications and Data Criticality Analysis (Addressable)
- Assess relative criticality of specific applications and data
- Prioritize systems and data
- Determine recovery priorities
- Support recovery time objectives

### 8. Evaluation (§164.308(a)(8))
**Required Standard**

- Perform periodic technical and nontechnical evaluation
- Based on Security Rule requirements
- Response to environmental or operational changes
- Annual evaluation recommended
- Document evaluation findings

### 9. Business Associate Contracts and Other Arrangements (§164.308(b)(1))
**Required Standard**

#### Written Contract or Other Arrangement (Required)
- Document satisfactory assurances that business associate will appropriately safeguard ePHI

**Required Contract Provisions:**
- Implement administrative, physical, and technical safeguards
- Ensure subcontractors provide same protections
- Report security incidents
- Authorize termination if BA violates contract
- Return or destroy ePHI at contract termination
- For group health plans: ensure plan documents protect ePHI

## Physical Safeguards

Standards for physical access to ePHI and facilities.

### 1. Facility Access Controls (§164.310(a)(1))
**Required Standard**

Limit physical access to electronic information systems and facilities while ensuring authorized access.

#### Contingency Operations (Addressable)
- Establish procedures to allow facility access during emergencies
- Emergency access procedures
- Backup access methods
- Emergency contact lists

#### Facility Security Plan (Addressable)
- Implement policies for safeguarding facility and equipment from unauthorized physical access, tampering, theft
- Perimeter security
- Entry points control
- Visitor management
- Security guards/surveillance
- Intrusion detection systems

#### Access Control and Validation Procedures (Addressable)
- Implement procedures to control and validate physical access to facilities
- Badge/access card systems
- Visitor logs and escort requirements
- Access approval processes
- Physical access reviews

#### Maintenance Records (Addressable)
- Implement policies and procedures to document repairs and modifications to physical components
- Maintenance logs
- Vendor access documentation
- Hardware disposal records

### 2. Workstation Use (§164.310(b))
**Required Standard**

- Implement policies specifying proper functions to be performed and physical environment surrounding workstations
- Clear screen/desk policies
- Positioning to limit viewing by unauthorized persons
- Prohibition of ePHI on personal devices
- Appropriate use policies
- Privacy screens where appropriate

### 3. Workstation Security (§164.310(c))
**Required Standard**

- Implement physical safeguards for workstations accessing ePHI
- Cable locks for laptops
- Secure areas for stationary workstations
- Automatic screen locks
- Prevent theft or unauthorized access

### 4. Device and Media Controls (§164.310(d)(1))
**Required Standard**

#### Disposal (Required)
- Implement policies for final disposal of ePHI and hardware/media
- Degaussing magnetic media
- Shredding paper and media
- Wiping/overwriting electronic media
- Physical destruction (crushing, incinerating)
- Certificate of destruction for sensitive disposals
- Sanitization standards (NIST SP 800-88)

#### Media Re-use (Required)
- Implement procedures for removal of ePHI before reuse
- Secure wiping utilities
- Reformatting multiple times
- Verification of data removal
- Encryption key destruction

#### Accountability (Addressable)
- Maintain record of hardware and media movements
- Chain of custody
- Asset tracking system
- Media inventory
- Check-in/check-out procedures

#### Data Backup and Storage (Addressable)
- Create retrievable exact copy of ePHI before movement of equipment
- Backup before shipping
- Secure backup storage
- Encrypted backups
- Off-site backup storage

## Technical Safeguards

Technology and policies protecting ePHI and controlling access.

### 1. Access Control (§164.312(a)(1))
**Required Standard**

Implement technical policies allowing only authorized persons to access ePHI.

#### Unique User Identification (Required)
- Assign unique name and/or number to identify and track user identity
- No shared accounts
- Individual accountability
- User ID cannot be reused
- Service accounts documented

#### Emergency Access Procedure (Required)
- Establish procedures for obtaining ePHI during emergencies
- Break-glass accounts
- Documented emergency access procedures
- Logging of emergency access
- Post-emergency review

#### Automatic Logoff (Addressable)
- Implement electronic procedures to terminate session after predetermined time of inactivity
- Recommended: 15 minutes or less
- Context-specific timing
- Save work before logoff
- Re-authentication required

#### Encryption and Decryption (Addressable)
- Implement mechanism to encrypt and decrypt ePHI
- Data at rest: AES-256 recommended
- Data in transit: TLS 1.2+ required
- Full disk encryption for mobile devices
- Database encryption
- Key management procedures
- If not implemented, document why not reasonable/appropriate

### 2. Audit Controls (§164.312(b))
**Required Standard**

- Implement hardware, software, and/or procedural mechanisms to record and examine activity in systems containing ePHI

**Requirements:**
- Log all access to ePHI
- Capture user ID, date/time, action, data accessed
- Tamper-resistant logs
- Log retention: minimum 6 years
- Regular log review
- Automated alerting for suspicious activity

**What to Log:**
- User login/logout
- PHI access (view, create, update, delete)
- Permission changes
- System configuration changes
- Failed access attempts
- Administrative actions
- Application errors
- Security incidents

### 3. Integrity (§164.312(c)(1))
**Required Standard**

Implement policies and procedures to protect ePHI from improper alteration or destruction.

#### Mechanism to Authenticate ePHI (Addressable)
- Implement electronic mechanisms to corroborate that ePHI has not been altered or destroyed inappropriately
- Checksums and hash functions
- Digital signatures
- Message authentication codes
- Version control
- Change detection systems

### 4. Person or Entity Authentication (§164.312(d))
**Required Standard**

- Implement procedures to verify person or entity seeking access is who they claim to be

**Authentication Methods:**
- Something you know (password, PIN)
- Something you have (token, smart card, mobile device)
- Something you are (biometric - fingerprint, facial recognition)
- Somewhere you are (geolocation)

**Multi-Factor Authentication (MFA):**
- Required for remote access
- Strongly recommended for all access
- At least two different factor types
- Time-based one-time passwords (TOTP)
- SMS codes (less secure)
- Authenticator apps
- Hardware tokens
- Biometrics + password

### 5. Transmission Security (§164.312(e)(1))
**Required Standard**

Implement technical security measures to guard against unauthorized access to ePHI transmitted over electronic communications network.

#### Integrity Controls (Addressable)
- Implement security measures to ensure electronically transmitted ePHI is not improperly modified without detection
- Network segmentation
- Checksums and error detection
- Digital signatures for messages
- Encrypted communications

#### Encryption (Addressable)
- Implement mechanism to encrypt ePHI whenever deemed appropriate
- TLS 1.2 or higher for web traffic
- VPN for remote access
- Secure email (S/MIME, PGP)
- End-to-end encryption for messaging
- If not implemented, document rationale

## Organizational Requirements

### Business Associate Contracts (§164.314(a))
**Required**

Business associate contracts must ensure:
- Implement appropriate safeguards for ePHI
- Report security incidents to covered entity
- Ensure subcontractors provide same protections
- Return or destroy ePHI at contract end (or retain if required by law)

### Group Health Plan Requirements (§164.314(b))
**Required**

Group health plan documents must:
- Ensure plan documents incorporate provisions for safeguarding ePHI
- Implement administrative, physical, and technical safeguards
- Ensure agents provide reasonable assurances
- Report security incidents

## Policies and Procedures

### Documentation (§164.316(a))
**Required Standard**

Implement reasonable and appropriate policies and procedures to comply with Security Rule.

Must be:
- In written (paper or electronic) form
- Available to workforce members
- Maintained for 6 years from creation or last effective date
- Reviewed and updated regularly

### Time Limit (§164.316(b)(1))
**Required Standard**

Retain documentation for 6 years from:
- Date of creation, OR
- Date when last in effect (whichever is later)

### Availability (§164.316(b)(2)(i))
**Required Standard**

Make documentation available to those responsible for implementing procedures.

### Updates (§164.316(b)(2)(iii))
**Required Standard**

Review and update documentation:
- Periodically
- In response to environmental or operational changes
- When security measures become insufficient

## Flexibility of Approach

### Scalability
- Appropriately sized for organization
- Complexity aligned with size and resources
- Protect against reasonably anticipated threats

### Considerations
1. **Size, Complexity, Capabilities**
   - Large vs. small organizations
   - Resources available
   - Technical capabilities

2. **Technical Infrastructure**
   - Current systems and technologies
   - Legacy system constraints
   - Integration requirements

3. **Cost of Security Measures**
   - Budget constraints
   - Cost-benefit analysis
   - Prioritization based on risk

4. **Probability and Criticality of Risks**
   - Likelihood of threats
   - Potential impact
   - Risk tolerance

## Common Violations

1. **Lack of Risk Analysis**
   - No documented risk assessment
   - Incomplete risk analysis
   - Outdated assessment

2. **Insufficient Access Controls**
   - Shared user credentials
   - No unique user IDs
   - Excessive permissions
   - No access reviews

3. **Missing Audit Controls**
   - No audit logging
   - Insufficient log retention
   - No log review process

4. **Inadequate Encryption**
   - Unencrypted mobile devices
   - Unencrypted data in transit
   - Weak encryption algorithms

5. **No Security Incident Procedures**
   - Undefined incident response
   - No reporting procedures
   - Incidents not documented

6. **Missing or Inadequate BAAs**
   - No business associate agreements
   - Incomplete BAA provisions
   - Outdated agreements

7. **Insufficient Training**
   - No security awareness training
   - Untrained new employees
   - No phishing awareness

8. **Poor Physical Security**
   - Unsecured facilities
   - Uncontrolled workstation access
   - Improper device disposal

## Best Practices

1. Conduct annual comprehensive risk assessments
2. Implement role-based access control (RBAC)
3. Deploy multi-factor authentication
4. Encrypt all ePHI (at rest and in transit)
5. Maintain comprehensive audit logs
6. Review logs regularly with automated alerting
7. Implement automatic session timeout (≤15 minutes)
8. Conduct regular security awareness training
9. Test contingency and disaster recovery plans annually
10. Maintain current business associate agreements
11. Document all security-related decisions and activities
12. Implement defense-in-depth strategy
13. Conduct periodic vulnerability scanning and penetration testing
14. Implement security information and event management (SIEM)
15. Maintain detailed asset inventory
16. Implement patch management program
17. Conduct security evaluations annually
18. Update policies and procedures based on changes
19. Implement network segmentation
20. Use approved encryption algorithms (AES-256, TLS 1.2+)

## Regulatory Citations

- 45 CFR §164.302 - Applicability
- 45 CFR §164.304 - Definitions
- 45 CFR §164.306 - Security standards: General rules
- 45 CFR §164.308 - Administrative safeguards
- 45 CFR §164.310 - Physical safeguards
- 45 CFR §164.312 - Technical safeguards
- 45 CFR §164.314 - Organizational requirements
- 45 CFR §164.316 - Policies and procedures and documentation requirements
- 45 CFR §164.318 - Compliance dates
