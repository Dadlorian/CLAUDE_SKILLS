# Healthcare Security Patterns & Architecture

**Version**: 2.1.0
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: HIPAA, NIST SP 800-66, HITRUST CSF, ISO 27001

---

## Executive Summary

This guide documents proven security architecture patterns, threat mitigation strategies, and implementation best practices for healthcare IT systems. It provides reusable security blueprints addressing common healthcare threats.

---

## 1. Defense-in-Depth Architecture

### 1.1 Layered Security Model

**Multi-Layer Security Approach:**

```
┌──────────────────────────────────────────────┐
│ Layer 1: Perimeter (Network Edge)            │
│ - Firewall rules                             │
│ - VPN gateway                                │
│ - DDoS protection                            │
│ - IDS/IPS (Intrusion Detection/Prevention)   │
│ - WAF (Web Application Firewall)             │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────v─────────────────────────┐
│ Layer 2: Application (API Gateway)           │
│ - OAuth 2.0 authentication                   │
│ - Rate limiting                              │
│ - Request validation                         │
│ - API versioning control                     │
│ - Request logging/auditing                   │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────v─────────────────────────┐
│ Layer 3: Service (Business Logic)            │
│ - Authorization checks (RBAC)                │
│ - Input validation                           │
│ - Data classification                        │
│ - Audit logging                              │
│ - Encryption (application-level)             │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────v─────────────────────────┐
│ Layer 4: Data (Database & Storage)           │
│ - Encryption at rest (AES-256)               │
│ - Column-level encryption (PII)              │
│ - Database access controls                   │
│ - Backup encryption                          │
│ - Immutable audit trails                     │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────v─────────────────────────┐
│ Layer 5: Infrastructure (Security Ops)       │
│ - Vulnerability scanning                     │
│ - Patch management                           │
│ - Security monitoring (SIEM)                 │
│ - Incident response                          │
│ - Backup/disaster recovery                   │
└──────────────────────────────────────────────┘
```

**Defense-in-Depth Benefits:**

```
Single Layer Fails: Attackers breach
Multiple Layers: Each failure is detected & mitigated
Complete Failure: Unlikely (layered detection)

Example: Ransomware Attack Progression

Attack Vector: Phishing email with malware attachment
  ↓
Layer 1 (Email gateway): Detects known malware signature
  → Email blocked, attack contained

If Layer 1 Fails:
  ↓
Layer 2 (Endpoint detection): Antivirus detects suspicious file
  → File quarantined, attack contained

If Layer 2 Fails:
  ↓
Layer 3 (Behavioral analysis): UEBA detects unusual file access
  → Process killed, attacker contained

If Layer 3 Fails:
  ↓
Layer 4 (Encryption): Data encrypted, but immutable backups exist
  → Restore from backup, minimal impact

If All Layers Fail:
  ↓
Layer 5 (Forensics): Incident response logs all activities
  → Investigation reveals attack vector
  → Improvements made to prevent recurrence
```

---

## 2. Authentication & Identity Management Patterns

### 2.1 Zero Trust Architecture

**Never Trust, Always Verify:**

```
Traditional Model:
  Perimeter: Firewall (trust inside network)
  Users inside network: Trusted
  Problem: Insider threats, lateral movement

Zero Trust Model:
  Principle: Verify every access request
  Trust boundary: Around individual user/device
  Continuous verification

Zero Trust Architecture:
┌──────────────────────────────────────────────┐
│ User/Device                                   │
│ ┌─────────────────────────────────────────┐  │
│ │ Identity Verification                   │  │
│ │ - MFA required                          │  │
│ │ - Device health check                   │  │
│ │ - Risk assessment                       │  │
│ └─────────────────────────────────────────┘  │
│                    │                          │
│                    v                          │
│ ┌─────────────────────────────────────────┐  │
│ │ Policy Engine                           │  │
│ │ - Verify identity                       │  │
│ │ - Check device compliance               │  │
│ │ - Assess risk                           │  │
│ │ - Grant minimum access needed (least    │  │
│ │   privilege)                            │  │
│ └─────────────────────────────────────────┘  │
│                    │                          │
│                    v                          │
│ ┌─────────────────────────────────────────┐  │
│ │ Micro-Segmentation                      │  │
│ │ - Resource isolation                    │  │
│ │ - Network segmentation                  │  │
│ │ - User/role segregation                 │  │
│ └─────────────────────────────────────────┘  │
│                    │                          │
│                    v                          │
│ ┌─────────────────────────────────────────┐  │
│ │ Continuous Monitoring                   │  │
│ │ - Verify ongoing access                 │  │
│ │ - Anomaly detection                     │  │
│ │ - Behavior analysis (UEBA)              │  │
│ │ - Automatic remediation                 │  │
│ └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Zero Trust Implementation:**

```
Step 1: Identify Protect Surface
  ✓ Critical assets (EHR, databases, pharmacy system)
  ✓ Sensitive data (patient records, financial)
  ✓ Privileged access points (admin functions)

Step 2: Map Transactions
  ✓ User to resource flows
  ✓ Device to application
  ✓ Service to service
  ✓ External integrations

Step 3: Build Micro-Segmentation
  ✓ Segment network by resource type
  ✓ Separate clinical from administrative
  ✓ Isolate development/test from production
  ✓ VLANs/firewall rules enforce boundaries

Step 4: Implement Continuous Monitoring
  ✓ Log all access requests
  ✓ Analyze for anomalies
  ✓ Adaptive authentication (higher risk = stronger MFA)
  ✓ Real-time alerting on policy violation

Step 5: Enforce Least Privilege
  ✓ Default: DENY all access
  ✓ Exception: ALLOW only what's needed
  ✓ Principle: Minimum access for minimum time
  ✓ Dynamic permissions: Revoke when no longer needed
```

### 2.2 Identity Provider (IdP) Architecture

**Healthcare Identity Management:**

```
┌─────────────────────────────────────────┐
│ User Directory                          │
│ - Employee records                      │
│ - Credentials                           │
│ - Role assignments                      │
│ - Status (active/inactive)              │
│ (LDAP/AD)                               │
└────────────────┬────────────────────────┘
                 │
      ┌──────────v──────────┐
      │ Identity Provider   │
      │ (SAML/OpenID)       │
      │ ┌────────────────┐  │
      │ │ Authentication │  │
      │ │ - Username     │  │
      │ │ - Password     │  │
      │ │ - MFA          │  │
      │ └────────────────┘  │
      │                     │
      │ ┌────────────────┐  │
      │ │ Authorization  │  │
      │ │ - Groups/Roles │  │
      │ │ - Attributes   │  │
      │ │ - Permissions  │  │
      │ └────────────────┘  │
      └──────────┬──────────┘
                 │
      ┌──────────v──────────┐
      │ Token Generation    │
      │ - JWT access token  │
      │ - Claims (groups)   │
      │ - Signature         │
      │ - Expiration        │
      └──────────┬──────────┘
                 │
      ┌──────────v──────────┐
      │ Applications        │
      │ - Validate token    │
      │ - Check permissions │
      │ - Grant access      │
      │ - Log access        │
      └─────────────────────┘
```

**User Provisioning Workflow:**

```
New Employee Hired:
  │
  ├─ HR system creates employee record
  │  └─ Employee ID, department, role
  │
  ├─ Automated provisioning workflow triggered
  │  ├─ Create directory account
  │  ├─ Assign to security groups
  │  ├─ Create email account
  │  ├─ Assign hospital ID badge
  │  ├─ Enroll in MFA
  │  └─ Grant initial permissions
  │
  ├─ Manager reviews & approves access
  │  └─ Email for manager confirmation
  │
  ├─ System provisions access
  │  ├─ Active Directory groups
  │  ├─ Application role assignments
  │  ├─ Database permissions
  │  └─ VPN access (if remote)
  │
  └─ User notified of access

Employee Role Change:
  │
  ├─ Manager updates employee record
  │  └─ Approves role change
  │
  ├─ Automated deprovisioning workflow
  │  ├─ Remove from old groups
  │  ├─ Remove old permissions
  │  └─ Remove application access
  │
  ├─ Automated reprovisioning workflow
  │  ├─ Add to new groups
  │  ├─ Assign new permissions
  │  └─ Grant new application access
  │
  └─ Access recertified

Employee Termination:
  │
  ├─ HR notifies system
  │  └─ Termination date
  │
  ├─ On termination date, automated workflow:
  │  ├─ Disable directory account
  │  ├─ Disable all access
  │  ├─ Revoke VPN access
  │  ├─ Remove group memberships
  │  ├─ Archive email
  │  ├─ Deactivate badge
  │  └─ Log final access
  │
  └─ Completed within 2 hours
```

---

## 3. Encryption & Key Management Patterns

### 3.1 Encryption Lifecycle

**Full Encryption Lifecycle:**

```
KEY GENERATION
  │
  ├─ Cryptographically secure random generation
  ├─ NIST SP 800-90A compliant
  ├─ Key length: 256-bit (AES) minimum
  ├─ Generated in HSM (Hardware Security Module)
  │
  v

KEY STORAGE
  │
  ├─ HSM-backed keystore
  ├─ Never in plain text in application/database
  ├─ Encrypted at rest with master key
  ├─ Access restricted to authorized services
  ├─ Audit logged for every key access
  │
  v

KEY ROTATION
  │
  ├─ Schedule: Every 90 days
  ├─ Automated via key management service
  ├─ New key: AES-256 generated
  ├─ Old key: Retained for decryption of old data
  ├─ No manual handling of key material
  │
  v

KEY USAGE
  │
  ├─ Application requests key from KMS
  ├─ KMS validates request (who, what, when)
  ├─ KMS returns decrypted key (never persists)
  ├─ Application uses key for crypto operation
  ├─ Key never stored in application memory
  │
  v

KEY REVOCATION
  │
  ├─ Compromised key: Immediate revocation
  ├─ Cryptographic erasure: Overwrite 3x
  ├─ Certification: Destruction documented
  ├─ Audit trail: Retained 7 years
  │
  v

KEY DECOMMISSIONING
  │
  ├─ After retention window expires
  ├─ Secure destruction procedure
  ├─ Hardware destruction certificate
  └─ Archive metadata for compliance
```

### 3.2 Data Classification & Encryption Strategy

**Encryption by Data Type:**

```
Data Classification    Encryption at Rest    Encryption in Transit
─────────────────────────────────────────────────────────────────────
HIGHLY SENSITIVE
  - SSN                AES-256 (HSM)         TLS 1.2+
  - Payment card       Column-level          Certificate pinning
  - Account passwords  Tokenization          Mutual TLS
  Storage: HSM, immutable audit trail

SENSITIVE
  - MRN                AES-256               TLS 1.2+
  - Name/Address       Column-level
  - DOB                Database-level
  - Insurance          Tokenization
  Storage: Encrypted database

INTERNAL
  - Diagnosis codes    AES-128 minimum       HTTPS
  - Medication names   Database-level
  - Lab results        (whole database)
  Storage: Encrypted database

PUBLIC
  - Hospital name      Plain text OK         HTTPS (still)
  - General health info No encryption needed
  Storage: Standard storage

Encryption Implementation:

┌────────────────────────────────────────┐
│ Application Layer Encryption           │
│ - Application encrypts before database │
│ - Application holds encryption key     │
│ - Database cannot decrypt (blind)      │
│ - Use case: Cloud database (untrusted) │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Database Layer Encryption              │
│ - Database encrypts all data at rest   │
│ - Database manages keys                │
│ - Use case: On-premise database        │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Storage Layer Encryption               │
│ - Storage device encrypts all data     │
│ - Transparent to application           │
│ - Use case: Additional protection      │
└────────────────────────────────────────┘

RECOMMENDED: Layer 1 + Layer 2 (Defense-in-depth)
```

---

## 4. Data Protection Patterns

### 4.1 Backup & Disaster Recovery

**Backup Strategy (3-2-1 Rule):**

```
3-2-1 Backup Rule:
  3 copies of data
  2 different storage types
  1 offsite copy

Healthcare Implementation:

PRIMARY DATABASE (Production)
  │
  ├─ Local Snapshot (Hourly)
  │  └─ Storage: SAN/NAS (same location)
  │  └─ Retention: 7 days
  │  └─ Recovery time: < 1 hour
  │
  ├─ Daily Backup (Full)
  │  └─ Storage: Tape (on-site)
  │  └─ Retention: 30 days
  │  └─ Recovery time: < 4 hours
  │
  ├─ Weekly Backup (Full)
  │  └─ Storage: Cloud (offsite)
  │  └─ Retention: 90 days
  │  └─ Recovery time: < 24 hours
  │
  └─ Monthly Archive (Full)
     └─ Storage: Archive system (offsite)
     └─ Retention: 7 years
     └─ Recovery time: 1-7 days

BACKUP PROTECTION:

Encryption:
  ✓ All backups encrypted with AES-256
  ✓ Keys stored separately from backups
  ✓ Key recovery documented
  ✓ Secure deletion on expiration

Access Control:
  ✓ Only IT/backup team can access
  ✓ MFA required for restoration
  ✓ Audit logging of all access
  ✓ Separation of duties

Integrity:
  ✓ Checksums for each backup
  ✓ Cryptographic signatures
  ✓ Regular integrity verification
  ✓ Detection of corruption

Testing:
  ✓ Monthly restore test (sample data)
  ✓ Annual full restore test
  ✓ RTO/RPO validation
  ✓ Documented procedures

DISASTER RECOVERY TARGETS:

RTO (Recovery Time Objective):
  Database: 4 hours (maximum acceptable downtime)
  Applications: 2 hours
  Email: 8 hours
  Non-critical: 24 hours

RPO (Recovery Point Objective):
  Database: 1 hour (maximum data loss acceptable)
  Applications: 4 hours
  Email: 4 hours
  Non-critical: 24 hours
```

### 4.2 Access Control & Data Masking

**Row-Level Security Pattern:**

```
Scenario: Different users see different data

Patient Portal (Patient View):
  - See only own records
  - Cannot see other patients
  - Physician: Must select patient first

Clinician View (Physician):
  - See own patients only
  - Cannot browse all patients
  - Cardiology specialist: See cardiology cases
  - Primary care: See all assigned patients

Administrative View (Billing):
  - See diagnosis/procedure codes (for billing)
  - Cannot see clinical notes/sensitive details
  - See only assigned facilities

Researcher View (Research):
  - De-identified data only
  - Patient identifiers removed/encrypted
  - Complies with HIPAA research waiver
  - Explicit audit logging

Database Implementation:

CREATE POLICY patient_isolation AS (
  USING (patient_id IN (
    SELECT patient_id FROM access_control
    WHERE user_id = CURRENT_USER
  ))
);

-- When query executed, WHERE clause automatically applied:
SELECT * FROM patient_data
WHERE (patient_id IN select_allowed_patients)

MASKED DATA:

PII Data Masking:
  Original:  SSN = 123-45-6789
  Masked:    SSN = XXX-XX-6789 (last 4 visible)

  Original:  DOB = 1970-03-15
  Masked:    DOB = 1970-03-** (year/month visible)

  Original:  Address = 123 Main St, Springfield, IL 62701
  Masked:    Address = ******* , Springfield, IL (ZIP visible)

Dynamic Masking:
  Rule: If user = "BILLING" THEN hide clinical notes
  Rule: If user = "RESEARCH" THEN hide patient ID
  Rule: If user = "CLINICIAN" THEN show all
  Rule: If user = "PATIENT" THEN hide peer patients

Audit Trail:
  ✓ Log all access to unmasked data
  ✓ Log all access to masked data
  ✓ Alert on suspicious patterns
  ✓ Management review of access
```

---

## 5. Incident Response & Forensics

### 5.1 Incident Response Plan

**Incident Response Workflow:**

```
DETECTION (Minutes 0-15)
  │
  ├─ Alert from security system detected
  ├─ False positive check
  ├─ Incident severity determined
  │  ├─ CRITICAL: Immediate activation
  │  ├─ HIGH: Within 15 minutes
  │  ├─ MEDIUM: Within 1 hour
  │  └─ LOW: Within 4 hours
  │
  └─ Incident response team assembled

CONTAINMENT (Minutes 15-60)
  │
  ├─ Isolate affected systems
  │  └─ Disconnect from network (if needed)
  │  └─ Preserve evidence (don't reboot)
  │  └─ Document isolation actions
  │
  ├─ Stop the attack
  │  └─ Disable compromised accounts
  │  └─ Revoke access tokens
  │  └─ Block malicious IPs
  │  └─ Kill suspicious processes
  │
  └─ Prevent spread
     └─ Segment network (if not already)
     └─ Monitor for lateral movement
     └─ Alert on similar indicators

INVESTIGATION (Hours 1-24)
  │
  ├─ Gather forensic evidence
  │  └─ Disk images (from-the-wire)
  │  └─ Memory dumps (if still running)
  │  └─ Network traffic captures (PCAP)
  │  └─ Log aggregation (centralized SIEM)
  │
  ├─ Timeline reconstruction
  │  └─ When attack started
  │  └─ Attack progression
  │  └─ What systems compromised
  │  └─ What data accessed
  │
  ├─ Root cause analysis
  │  └─ How did attacker gain access?
  │  └─ What was the entry point?
  │  └─ How long were they present?
  │  └─ What was the objective?
  │
  └─ Impact assessment
     └─ What data was affected?
     └─ How many patients?
     └─ Severity of exposure?
     └─ Regulatory reporting needed?

ERADICATION (Hours 24-72)
  │
  ├─ Remove malware
  │  └─ Malware scanning all systems
  │  └─ Confirm clean (multiple scans)
  │  └─ Update signatures
  │
  ├─ Patch vulnerability
  │  └─ Apply security patch
  │  └─ Test in non-production first
  │  └─ Deploy to production
  │  └─ Verify remediation
  │
  ├─ Reset credentials
  │  └─ Force password change (admin accounts)
  │  └─ Revoke old tokens
  │  └─ Verify MFA still enabled
  │
  └─ Close backdoors
     └─ Disable unauthorized accounts
     └─ Remove SSH keys
     └─ Check for persistence

RECOVERY (Days 3-7)
  │
  ├─ Restore from backups (if needed)
  │  └─ Restore to clean backup (pre-attack)
  │  └─ Verify no re-infection
  │  └─ Restore incrementally
  │
  ├─ Restore services
  │  └─ Restore in order of criticality
  │  └─ EHR first (patient care)
  │  └─ Supporting systems next
  │  └─ Administrative systems last
  │
  ├─ Verify functionality
  │  └─ System health checks
  │  └─ Application testing
  │  └─ Database consistency
  │  └─ Data integrity verification
  │
  └─ Monitor for relapse
     └─ Enhanced monitoring 30 days
     └─ Daily log reviews
     └─ Alert thresholds lowered

POST-INCIDENT (Days 7-30)
  │
  ├─ Forensic analysis complete
  ├─ Final root cause documented
  ├─ Lessons learned identified
  ├─ Preventive measures implemented
  ├─ Staff training conducted
  ├─ Incident report completed
  ├─ Management briefing
  └─ Regulatory notification (if required)
```

### 5.2 Breach Notification Checklist

**Regulatory Notification Requirements:**

```
Breach Determination (HIPAA Rule):
  ✓ Establish that breach occurred
  ✓ Assess risk of harm:
    - Probability of access
    - Use/disclosure likelihood
    - Sensitivity of information
    - Security measures in place
    - Whether actually accessed

Low Risk = No Notification Required:
  Example: Encrypted device lost
  Reason: Data cannot be accessed (encryption strong)

High Risk = Notification Required:
  Example: Unencrypted database exposed
  Reason: Data can be accessed

Notification Timeline:

Within 60 Days:
  □ Notify affected individuals
  □ Notify media (if >500 state residents)
  □ Notify HHS Office for Civil Rights

Notification Content:
  • Description of breach
  • Types of information involved
  • Steps being taken to investigate
  • What individuals should do
  • What organization is doing
  • Contact information
  • Free credit monitoring offer

Documentation:
  □ Retain notification letters
  □ Maintain log of individuals notified
  □ Document notification methods
  □ Retain evidence for 6 years
```

---

## 6. Vulnerability Management

### 6.1 Vulnerability Assessment Framework

**Continuous Vulnerability Management:**

```
IDENTIFICATION (Ongoing)
  │
  ├─ Vulnerability scanning
  │  └─ Network scanner (Nessus, OpenVAS)
  │  └─ Application scanner (Burp Suite)
  │  └─ Dependency scanner (SAST)
  │  └─ Container scanner (DockerBench)
  │
  ├─ Threat intelligence
  │  └─ NVD (National Vulnerability Database)
  │  └─ Vendor security bulletins
  │  └─ Security researcher reports
  │  └─ Industry threat feeds
  │
  └─ Penetration testing
     └─ Annual external test
     └─ Annual internal test
     └─ Post-deployment testing

PRIORITIZATION (Weekly)
  │
  ├─ CVSS score calculation
  │  └─ Low (0.0-3.9): Nice-to-fix
  │  └─ Medium (4.0-6.9): Should-fix
  │  └─ High (7.0-8.9): Must-fix
  │  └─ Critical (9.0-10.0): Fix immediately
  │
  ├─ Context assessment
  │  └─ Is system internet-facing?
  │  └─ Does system have patient data?
  │  └─ Can vulnerability be exploited?
  │  └─ Are exploits known/available?
  │
  └─ Business impact
     └─ Patient safety impact?
     └─ Regulatory requirement?
     └─ Business-critical system?

REMEDIATION (Based on Priority)
  │
  ├─ Critical (SLA: 24 hours)
  │  ├─ Emergency change control process
  │  ├─ Patch deployed within 24 hours
  │  ├─ Testing minimal (security vs. stability trade-off)
  │  └─ Verify patch effectiveness
  │
  ├─ High (SLA: 30 days)
  │  ├─ Standard change control process
  │  ├─ Test in staging environment
  │  ├─ Schedule downtime if needed
  │  └─ Verify patch applied to all instances
  │
  ├─ Medium (SLA: 90 days)
  │  ├─ Standard process
  │  ├─ Batch with other patches
  │  ├─ Plan deployment window
  │  └─ Monitor post-deployment
  │
  └─ Low (SLA: 1 year)
     ├─ Include in regular maintenance
     ├─ No special prioritization
     └─ Track for remediation

VERIFICATION (Post-Patching)
  │
  ├─ Rescan to confirm patch
  ├─ Vulnerability should no longer be reported
  ├─ Monitor for regression
  ├─ Update asset inventory
  └─ Document remediation in system

REPORTING (Monthly)
  │
  ├─ Vulnerability metrics dashboard
  ├─ Aging vulnerabilities (not yet patched)
  ├─ Patch deployment rate
  ├─ SLA compliance
  └─ Trending analysis
```

---

## Appendix: Security Control Checklist

**Essential Healthcare Security Controls:**

```
Network Security
  □ Firewall blocking all inbound traffic
  □ VPN for remote access
  □ Network segmentation (clinical vs. admin)
  □ Intrusion detection/prevention (IDS/IPS)
  □ DDoS protection
  □ DNS filtering (malicious sites blocked)

Endpoint Security
  □ Antivirus/anti-malware on all devices
  □ Endpoint detection & response (EDR)
  □ Host-based firewall enabled
  □ Automatic security updates
  □ Encrypted storage (full-disk or file-level)
  □ USB/external media restrictions

Access Management
  □ Unique IDs for all users
  □ MFA for remote access
  □ MFA for privileged accounts (required)
  □ Password policy enforced
  □ Automatic logoff (< 30 min)
  □ Privileged access management (PAM)

Data Protection
  □ Encryption at rest (AES-256)
  □ Encryption in transit (TLS 1.2+)
  □ Key management system (HSM)
  □ Secure key storage
  □ Regular key rotation
  □ Data classification policy

Monitoring & Logging
  □ Centralized logging (SIEM)
  □ Log retention (minimum 1 year)
  □ Audit trail for PHI access
  □ Real-time alerting
  □ 24/7 security operations center (SOC)
  □ Incident response procedures

Backup & Recovery
  □ Daily backups
  □ Offsite backup copy
  □ Encrypted backups
  □ Tested recovery procedures
  □ RTO/RPO defined & met
  □ Business continuity plan

Vendor Management
  □ Business Associate Agreements (BAAs)
  □ Security assessments of vendors
  □ Regular audit/recertification
  □ Data handling agreements
  □ Incident notification requirements
  □ Subcontractor oversight

Training & Awareness
  □ Annual security training (all staff)
  □ Role-specific training
  □ Phishing simulation program
  □ Incident reporting procedures
  □ Clean desk policy
  □ Secure disposal procedures
```

---

**Contact**: Healthcare Security & Risk Management
**Last Reviewed**: 2025-11-19
**Next Review**: 2026-05-19
**Classification**: Internal Use - Healthcare Professionals
