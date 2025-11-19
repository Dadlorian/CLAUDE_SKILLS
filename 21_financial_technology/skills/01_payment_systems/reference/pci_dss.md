# PCI-DSS (Payment Card Industry Data Security Standard) Reference

## Overview

PCI-DSS is a set of security standards for organizations that handle payment card information. It applies to any entity that stores, processes, or transmits credit/debit card data.

**Current Version**: 3.2.1 (PCI-DSS 4.0 effective March 2024)

**Governance**: PCI Security Standards Council (Visa, Mastercard, Amex, Discover, JCB)

## Scope

### Who Must Comply
```
Level 1: >= 6 million transactions/year
Level 2: 1-6 million transactions/year
Level 3: 20,000-1 million e-commerce transactions/year
Level 4: < 20,000 e-commerce transactions/year (if not breached)
        > 1 million total transactions/year
        Any merchant with history of breach
```

### In-Scope Systems
- Any system that stores, processes, or transmits cardholder data
- Network components with access to cardholder data
- Systems connected to in-scope systems
- Wireless networks

### Out-of-Scope Systems
- Systems completely isolated from cardholder data
- Office networks with no access to cardholder data
- Non-payment applications

## The 12 Core Requirements

### 1. Install and Maintain Firewall Configuration

```
Requirements:
- Define firewall rules and policies
- Document firewall configuration standards
- Restrict inbound/outbound traffic to business need
- Default deny unless explicitly allowed
- No direct routing from untrusted networks to cardholder data environment

Implementation:
- Configure firewalls at network perimeter
- Separate DMZ for public-facing systems
- Restrict cardholder data network
- Monitor firewall logs
- Review configuration quarterly

Example Architecture:
Internet -> WAF -> Load Balancer -> Web Servers (DMZ)
                                  -> Payment Gateway (Secure Network)
                                  -> Database (Highly Restricted)
```

### 2. Do Not Use Vendor-Supplied Defaults

```
Requirements:
- Change default passwords on all systems
- Configure systems according to hardening guides
- Remove unnecessary services
- Disable default accounts

Implementation:
- Change all default credentials immediately upon deployment
- Document configuration baselines
- Regular security hardening assessments
- Remove unused accounts and services

Checklist:
- [ ] Default admin passwords changed
- [ ] Default database passwords changed
- [ ] SSH keys configured (not passwords)
- [ ] Default web server configurations hardened
- [ ] Unnecessary services disabled
- [ ] Default accounts disabled
```

### 3. Protect Stored Cardholder Data

```
Sub-Requirement 3.1: Render primary account number (PAN) unreadable
Methods (choose one or more):
a) Encryption (AES-256 minimum)
b) Tokenization
c) Hashing (with salt, not PAN alone)
d) Truncation (if never need full PAN)
e) Masking

Sub-Requirement 3.2: Do not store sensitive authentication data
NEVER STORE AFTER AUTHORIZATION:
- Full magnetic stripe data
- CAV2/CVC2 codes
- Full PINs
- Chip unique data
- PIN blocks

Sub-Requirement 3.3: Render PAN unreadable in logs
- Application logs must not contain full PAN
- Use tokenization in log entries
- Last 4 digits acceptable for reference

Sub-Requirement 3.4: Limit PAN retention
- Define data retention policy
- Secure deletion after retention period
- Document retention justification

Implementation:
Data Classification:
- Level 1 (Highly Sensitive): Full PAN, CVV, PIN
  Storage: Encrypted vault only
  Access: Minimal (production systems only)
  Retention: As short as possible (hours, not days)

- Level 2 (Sensitive): Last 4 digits, Brand, Expiry
  Storage: Standard encrypted database
  Access: Application servers
  Retention: As per business requirements

- Level 3 (Non-sensitive): Token, Fingerprint
  Storage: Standard database
  Access: All systems
  Retention: Indefinite (for audit trail)
```

### 4. Encrypt Transmission of Cardholder Data

```
Requirements:
- Encrypt all transmission over public networks
- Use strong cryptography (TLS 1.2 minimum)
- Authenticate endpoints
- Use valid certificates only

Implementation:
TLS Configuration:
- Protocol: TLS 1.2 or 1.3 only
- Cipher Suites: AES-256-GCM recommended
- Certificate: Valid, not self-signed
- Key: 2048-bit minimum for RSA
- HSTS: Enable with long max-age

Example (Node.js):
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert'),
  minVersion: 'TLSv1.2',
  ciphers: [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256'
  ].join(':')
};

https.createServer(options, app).listen(443);

Testing:
curl --tlsv1.2 -I https://example.com
nmap --script ssl-enum-ciphers https://example.com
sslscan example.com
```

### 5. Protect Against Malware

```
Requirements:
- Install and maintain anti-virus software
- Keep anti-virus signatures current
- Generate logs and alerts for anti-virus
- Restrict ability to disable anti-virus

Implementation:
- Deploy anti-virus on all systems handling cardholder data
- Enable real-time scanning
- Enable logging of all scans and detections
- Configure alerts for suspicious activity
- Regular vulnerability scanning
- Penetration testing (annual minimum)

Example Deployment:
Windows Servers: Windows Defender + SIEM integration
Linux Servers: ClamAV + fail2ban + OSSEC
All Systems: Regular vulnerability scanning (Nessus, Qualys)
```

### 6. Develop and Maintain Secure Systems

```
Sub-Requirement 6.1: Establish secure development process
- Define security requirements
- Establish code review process
- Testing before production
- Security standards and guidelines

Sub-Requirement 6.2: Implement changes securely
- Testing of all changes
- Change management process
- Separation of duties
- Production access controls

Sub-Requirement 6.3: Prevent common vulnerabilities
- Address OWASP Top 10
- Input validation
- Output encoding
- Prevention of injection attacks
- Secure authentication and session management

Sub-Requirement 6.4: Address vulnerabilities promptly
- Patch management process
- Regular security testing
- Document patching timeline
- Emergency patching process

Implementation (Example):

Secure Development Lifecycle:
1. Design Phase
   - Security threat modeling
   - Architecture review
   - Define security requirements

2. Development Phase
   - Code review (peer + security)
   - Static code analysis (SonarQube, Checkmarx)
   - Secure coding practices training

3. Testing Phase
   - Functional testing
   - Security testing
   - Penetration testing
   - Vulnerability scanning

4. Deployment Phase
   - Change control approval
   - Staged rollout (dev -> staging -> prod)
   - Monitoring and rollback plan

5. Maintenance Phase
   - Continuous monitoring
   - Vulnerability management
   - Incident response capability

Code Review Checklist:
- [ ] Input validation for all user inputs
- [ ] Output encoding to prevent XSS
- [ ] Parameterized queries (prevent SQL injection)
- [ ] No hardcoded credentials
- [ ] No debug code left in production
- [ ] Error handling (no sensitive data in errors)
- [ ] Security headers present
- [ ] Authentication properly implemented
- [ ] Authorization properly enforced
- [ ] No public/internal API key exposure
```

### 7. Restrict Access by Business Need to Know

```
Requirements:
- Limit access to cardholder data on need-to-know basis
- Restrict access by job function
- Default deny access
- Document access requirements

Implementation:
Access Control Model:
- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews
- Segregation of duties

Example Roles:
- Payment Processor: Full access to payment data, no admin access
- Developer: Access to non-production systems only
- Administrator: System administration, limited payment data access
- Auditor: Read-only access to audit logs
- QA: Access to test systems and anonymized production data

Access Control List:
Resource: Payment Database
- Payment Processor: READ, WRITE (live transactions only)
- Batch Processor: READ, WRITE (batch jobs only)
- Developer: READ (test data only)
- DBA: ADMIN (maintenance, no data access)
- Auditor: READ (audit logs)

Implementation (Code Example):
// Enforce authorization at API level
const authorizePaymentAccess = (requiredRole) => {
  return (req, res, next) => {
    const userRole = req.user.role;
    const allowedRoles = getRolesForPaymentAccess(requiredRole);

    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required_role: requiredRole,
        user_role: userRole
      });
    }
    next();
  };
};

app.get('/api/payments/:id',
  authenticateToken,
  authorizePaymentAccess('PAYMENT_PROCESSOR'),
  getPayment
);
```

### 8. Identify and Authenticate Access

```
Requirements:
- Assign unique user ID to each user
- Use strong authentication
- Track and monitor access
- Use MFA for remote access

Implementation:
User Identification:
- Unique employee/contractor ID
- Unique service account names
- Log all access by user

Strong Authentication:
- Minimum 7 characters
- Mix of uppercase, lowercase, numbers, special chars
- Regular password changes (90 days)
- History (don't reuse last 4 passwords)
- Account lockout (6 attempts, 30 minutes)

Example (Python):
import re
from datetime import datetime, timedelta

class PasswordValidator:
    MIN_LENGTH = 12
    COMPLEXITY_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{12,}$'
    )

    def validate(self, password):
        if not self.COMPLEXITY_PATTERN.match(password):
            raise ValueError(
                'Password must contain uppercase, lowercase, digit, symbol'
            )
        return True

    def check_history(self, user_id, new_password):
        # Ensure not reusing last 4 passwords
        historical = get_password_history(user_id, limit=4)
        for old_hash in historical:
            if verify_password(new_password, old_hash):
                raise ValueError('Cannot reuse recent passwords')

# MFA Implementation
class MFAManager:
    def require_mfa(self, user_id):
        # Generate TOTP secret
        secret = pyotp.random_base32()
        qr_code = generate_qr_code(secret)
        return {
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': generate_backup_codes(8)
        }

    def verify_mfa(self, user_id, token):
        secret = get_user_mfa_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
```

### 9. Restrict Physical Access

```
Requirements:
- Limit physical access to cardholder data systems
- Implement access controls
- Identify visitors
- Monitor physical access

Implementation:
- Badge/keycard access to data centers
- Visitor log (check-in/check-out)
- Surveillance cameras in sensitive areas
- Clear desk policy (no cardholder data visible)
- Secure storage of media and documents
- Locked rooms for network equipment
```

### 10. Track and Monitor Access

```
Requirements:
- Implement audit logging for all access
- Protect logs from tampering
- Review logs regularly
- Retain logs for at least one year

Implementation:
What to Log:
- User access (login, logout, failed attempts)
- Administrative actions (config changes, privilege escalation)
- Invalid access attempts
- Use of identification and authentication mechanisms
- All access to cardholder data
- Changes to user accounts
- Creation/alteration/deletion of cardholder data
- System alerts and failures

Where to Log:
- Application logs (payment transactions)
- Database audit logs (cardholder data changes)
- System logs (login/logout, privilege escalation)
- Network logs (firewall, IDS alerts)
- Web server logs (HTTP requests)

Log Protection:
- Centralized logging (syslog, Splunk, ELK, CloudWatch)
- Restricted access (read-only for most users)
- Encryption in transit (TLS)
- Encryption at rest (AES-256)
- No deletion, only archival
- Tamper detection

Example Log Entry:
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "event_type": "AUTHORIZATION_REQUEST",
  "user_id": "USR_12345",
  "user_role": "PAYMENT_PROCESSOR",
  "action": "AUTHORIZE_PAYMENT",
  "merchant_id": "MERCH_ABC123",
  "amount": "99.99",
  "currency": "USD",
  "card_token": "tok_1A2B3C4D5E6F",
  "card_last4": "4242",
  "result": "APPROVED",
  "response_code": "00",
  "processor": "STRIPE",
  "processing_time_ms": 245,
  "client_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "fraud_score": 0.05,
  "transaction_id": "txn_xyz789",
  "audit_log_id": "audit_123456789"
}

Log Review Process:
- Automated alerts for suspicious patterns
- Daily review of failed transactions
- Weekly review of admin activities
- Monthly comprehensive review
- Annual audit by third party
```

### 11. Test Security Systems Regularly

```
Requirements:
- Regular security testing
- Vulnerability scanning
- Penetration testing
- Annual third-party assessment

Implementation:
Vulnerability Scanning:
- Quarterly network scans
- Monthly application scans
- Remediation within 30 days (critical)
- Remediation within 90 days (high)

Penetration Testing:
- Annual comprehensive penetration test
- Target payment processing systems
- Include social engineering
- Document findings and remediation

Example Vulnerability Management Process:
1. Scan (quarterly)
2. Report (identify vulnerabilities)
3. Categorize (CVSS severity)
4. Remediate (patch/mitigate)
5. Retest (confirm fix)
6. Report (document completion)

Tools:
- Vulnerability Scanning: Nessus, Qualys, Rapid7
- Web App Scanning: Burp Suite, OWASP ZAP
- Penetration Testing: Metasploit, Cobalt Strike
- SAST: SonarQube, Checkmarx, Fortify
- DAST: Acunetix, IBM AppScan
```

### 12. Maintain Information Security Policy

```
Requirements:
- Document security policies
- Communicate policies to employees
- Review and update annually
- Training and awareness

Implementation:
Core Policies:
- Information Security Policy
- Acceptable Use Policy
- Incident Response Plan
- Business Continuity Plan
- Disaster Recovery Plan
- Data Retention Policy
- Vendor Management Policy
- Third-Party Vendor Assessment Policy

Policy Components:
- Purpose and scope
- Responsible parties
- Specific requirements
- Enforcement mechanisms
- Review schedule
- Approval authority

Awareness Training:
- Annual security training for all staff
- Role-specific training (developers, admins, etc.)
- Payment security fundamentals
- Phishing awareness
- Incident reporting procedures
- Documentation of training completion
```

## Compliance Levels and Requirements

### Attestation of Compliance

```
Level 1-2: Annual audit by Qualified Security Assessor (QSA)
Level 3-4: Annual self-assessment questionnaire

Level 1 Audit Includes:
- Complete infrastructure review
- Systems testing and verification
- Code review
- Penetration testing
- Compliance report generation
- Report submitted to acquiring bank

Cost: $15,000-50,000 per year
Time: 2-4 weeks on-site
Frequency: Annual
```

## PCI-DSS 4.0 Key Changes

### Focus Areas
```
1. Encryption Strength
   - TLS 1.2 minimum (now 1.3 recommended)
   - Strong cipher suites mandated
   - Key management formalized

2. Vulnerability Management
   - More aggressive patching timelines
   - Automated vulnerability scanning
   - Third-party component management

3. Access Control
   - Multi-factor authentication (MFA) expanded
   - Privileged Access Management (PAM) requirements
   - Segregation of duties formalized

4. Monitoring and Detection
   - Advanced threat detection required
   - Automated log analysis
   - Incident detection within 7 days

5. Secure Development
   - Secure coding practices formalized
   - DevSecOps integration
   - Third-party library management
```

## Common Compliance Mistakes

### 1. Insufficient Encryption
```
WRONG:
- Using outdated TLS 1.0/1.1
- Using weak cipher suites
- Self-signed certificates

CORRECT:
- TLS 1.2+ only
- Strong cipher suites (AES-256-GCM)
- Valid, trusted certificates
```

### 2. Poor Log Management
```
WRONG:
- Logs not retained (deleted after 30 days)
- Logs stored in normal database
- No integrity controls

CORRECT:
- Logs retained 1 year minimum
- Centralized immutable logging
- Encryption and access controls
- Regular automated analysis
```

### 3. Inadequate Access Controls
```
WRONG:
- Shared credentials
- Excessive access to cardholder data
- No MFA for privileged access

CORRECT:
- Unique user IDs for all users
- Principle of least privilege
- MFA for all remote access
```

### 4. Missing Third-Party Assessment
```
WRONG:
- Payment processor chosen without security review
- No vendor SLAs
- No breach notification clauses

CORRECT:
- Vendor security assessment
- SLA commitments
- Breach notification requirements
- Regular vendor re-assessment
```

## Cost of Non-Compliance

### Breach Fines
```
Per Card: $100-500 per record (up to millions)
Maximum: Millions per incident
Examples:
- Target (2013): 40 million cards, $18.5 million settlement
- Equifax (2017): 147 million records, $700 million settlement
- Capital One (2019): 106 million records, $80 million settlement
```

### Non-Breach Violations
```
Per Violation: $100-150 per month
Annual: $1,200-1,800 per violation
Card Network Fines: $5,000-100,000 per violation
Loss of Payment Processing: Account closure
```

### Remediation Costs
```
Incident Response: $200,000-2,000,000
Legal/Regulatory: $100,000-1,000,000
System Upgrades: $500,000-5,000,000
Notification/Credit Monitoring: $50,000-500,000
```
