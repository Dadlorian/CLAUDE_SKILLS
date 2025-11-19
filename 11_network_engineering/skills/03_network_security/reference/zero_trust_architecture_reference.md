# Zero Trust Architecture Reference

## Core Principles

### Principle 1: Never Trust, Always Verify
```
Traditional Model:
- Trust based on network location
- Interior = trusted
- Exterior = untrusted

Zero Trust Model:
- Trust = verification
- Every access request verified
- Every user, device, application scrutinized
- Breach assumption: assume compromise
```

### Principle 2: Least Privilege Access
```
Grant minimum necessary permissions:
- User gets access to exactly what needed
- Application gets minimum required API calls
- Device accesses only authorized networks
- Service connects to only required services
- No "full network access"
```

### Principle 3: Assume Breach
```
Security mindset:
- Network already compromised
- Lateral movement expected
- Design for containment
- Segment thoroughly
- Monitor constantly
- Respond fast
```

### Principle 4: Verify Every Request
```
Authentication:
- User identity (who)
- Device identity (what)
- Context (where, when, how)
- Application identity
- Encryption status
- Compliance status
```

### Principle 5: Secure Every Access
```
Encryption:
- In transit: TLS 1.2 minimum
- At rest: AES-256 minimum
- End-to-end for sensitive data
- Perfect forward secrecy
- Key management standards
```

## Implementation Architecture

### Pillars of Zero Trust

```
┌─────────────────────────────────────────────────────────┐
│                   Zero Trust Architecture               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌──────────────────┐            │
│  │   Identity &    │  │   Device         │            │
│  │ Access Control  │  │  Compliance      │            │
│  └────────┬────────┘  └────────┬─────────┘            │
│           │                     │                       │
│           └────────┬────────────┘                       │
│                    │                                    │
│                    ▼                                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │        Policy Decision Point (PDP)                │ │
│  │  - Verify all context                            │ │
│  │  - Apply security policies                       │ │
│  │  - Grant/deny access                             │ │
│  └────────┬────────────────────┬────────────────────┘ │
│           │                    │                       │
│           ▼                    ▼                        │
│  ┌─────────────────┐  ┌──────────────────┐            │
│  │  Micro-         │  │  Threat          │            │
│  │  Segmentation   │  │  Detection       │            │
│  │  & Network      │  │  & Response      │            │
│  │  Control        │  │                  │            │
│  └─────────────────┘  └──────────────────┘            │
│           │                    │                       │
│           └────────┬───────────┘                       │
│                    │                                    │
│                    ▼                                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │        Continuous Monitoring & Logging            │ │
│  │  - Track all access                              │ │
│  │  - Log security events                           │ │
│  │  - Analyze anomalies                             │ │
│  │  - Trigger incident response                     │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Identity and Access Control

### Authentication Framework

#### Multi-Factor Authentication (MFA)
```
Factor 1: Something You Know
- Password
- PIN
- Security questions

Factor 2: Something You Have
- Hardware token
- Mobile device
- Smart card

Factor 3: Something You Are
- Biometrics (fingerprint, face)
- Voice recognition
- Behavioral patterns

Example:
1. Username + Password (Factor 1)
2. Mobile device notification approval (Factor 2)
3. Location verification (Factor 3 contextual)
```

#### Passwordless Authentication
```
FIDO2/WebAuthn:
- Hardware security key
- Biometric on device
- Windows Hello
- Platform authenticator

Advantages:
- No password compromise
- Fast authentication
- User-friendly
- Phishing resistant

Implementation:
- Register security keys
- Support multiple keys
- Backup mechanisms
- Graceful degradation
```

### Identity Repository

```
Central Identity Provider:
├── Azure AD / Okta / Ping
├── User profiles
├── Group memberships
├── MFA enrollment
├── Device registrations
├── Application assignments
└── Access policies

Attributes tracked:
- User ID (samAccountName)
- Email address
- Department
- Job title
- Manager
- Device types
- Group memberships
- Risk score
```

### Dynamic Access Policies

#### User Context
```
Who: User identity
- Primary identity
- Delegated access
- Service accounts
- Bot identity

When: Access timing
- Business hours
- Time zone
- Day of week
- Exception windows

Where: Location
- Office network
- Home network
- Public network
- Datacenter

How: Access method
- Direct connection
- VPN tunnel
- Proxy gateway
- Browser only

Device: Device context
- Device type
- OS version
- Encryption status
- Antivirus status
- Patch level
```

#### Access Decision Logic
```
IF user MFA_verified
  AND device compliant
  AND location approved
  AND access during business hours
  AND no risk indicators
THEN:
  Grant access to resource
  Apply rate limiting
  Enable monitoring
  Set session timeout

IF user MFA_verified
  AND device non-compliant
  OR location suspicious
  OR outside business hours
THEN:
  Require additional verification
  Limit access scope
  Enable enhanced logging
  Short session timeout

IF user identity suspicious
  OR device compromised
  OR multiple failed attempts
THEN:
  Block access
  Trigger incident response
  Require re-authentication
  Notify security team
```

## Device Compliance and Posture

### Device Inventory
```
Register all devices:
- Corporate-owned
- BYOD (Bring Your Own Device)
- Guest devices
- IoT devices

Track attributes:
- Device ID (UUID)
- Device type (laptop, mobile, etc.)
- OS and version
- Installed software
- Configuration
- Owner/user
```

### Compliance Checking

#### Windows Devices
```
Intune/Microsoft Endpoint Manager:
- Windows Defender active
- Windows Update current
- Disk encryption enabled
- Firewall enabled
- TLS 1.2 minimum
- Password policy enforcement
- Device risk level
```

#### macOS Devices
```
MDM Management:
- FileVault disk encryption
- Firewall enabled
- Updates current
- XProtect active
- Gatekeeper enabled
- System Integrity Protection enabled
- Compliance status
```

#### Mobile Devices (iOS/Android)
```
MDM Management:
- Passcode enabled
- Encryption enabled
- No jailbreak/root
- OS version current
- App restrictions enforced
- Location tracking
- Remote wipe capability
```

### Non-Compliant Device Handling

```
Compliant Device:
✓ Full access to resources
✓ Normal session timeout
✓ Standard policies apply

Non-Compliant but Trusted Device:
⚠ Limited resource access
⚠ Short session timeout
⚠ Enhanced monitoring
⚠ Restricted network access
⚠ User notified to remediate

Unknown/Untrusted Device:
✗ Deny all access
✗ User must remediate
✗ Re-register device
✗ Compliance verification
```

## Microsegmentation

### Network Segmentation Strategy
```
Traditional Firewall:
Perimeter-based (outside = untrusted, inside = trusted)
Flat internal network
All internal devices can access all services

Zero Trust Segmentation:
- Every segment protected
- Intra-segment filtering
- Service-level policies
- Application-aware controls
- Encrypted communication
```

### Segmentation Models

#### Application-Based Segments
```
Segment 1: User Workstations
├── Access: Internal applications
├── Restrictions: No direct database access
├── Monitoring: User activity tracking
└── Isolation: From other user segments

Segment 2: Web Servers
├── Access: HTTP/HTTPS inbound only
├── Restrictions: No outbound except approved
├── Monitoring: Request/response logging
└── Isolation: From database segment

Segment 3: Application Servers
├── Access: From web servers only
├── Restrictions: Limited database access
├── Monitoring: API call tracking
└── Isolation: From user segment

Segment 4: Database Servers
├── Access: From app servers only
├── Restrictions: Encrypted connections
├── Monitoring: Query logging
└── Isolation: From all others
```

#### Service-Based Segments
```
Each service gets dedicated segment:
- Email service: Segment A
- File sharing: Segment B
- Collaboration: Segment C
- Financial systems: Segment D
- HR systems: Segment E

Rules:
- Service A cannot access Service D
- Cross-service access requires gateway
- Service-to-service auth required
- Encrypted channels mandatory
```

### Lateral Movement Prevention

```
Attack Flow Prevention:

Scenario: Workstation compromised
│
├─ Without Segmentation:
│  └─ Attacker can access: File servers → App servers → Databases
│
├─ With Segmentation:
│  ├─ Workstation segment blocked from accessing file servers
│  ├─ File server segment blocked from accessing app servers
│  └─ App server segment can access databases only on specific ports

Implementation:
- VLAN isolation
- Firewall filtering
- Network ACLs
- Zero-trust policies
- Monitoring and alerting
```

## Continuous Verification

### Session Management
```
Traditional: Verify once at login, trust for duration

Zero Trust: Continuously verify throughout session

Verification Points:
1. Initial login: Full authentication
2. During idle: Verify context hasn't changed
3. On access request: Verify current device status
4. On privilege elevation: Re-authenticate
5. On sensitive access: Additional verification
6. Periodic (hourly): Re-verify everything
```

### Behavioral Analytics
```
Establish baseline user behavior:
- Typical login times
- Typical devices used
- Typical access patterns
- Typical data usage
- Typical communication partners

Detect anomalies:
- Login at unusual time
- Login from unusual location
- Access to unusual resources
- High volume of data access
- Failed login attempts
- Changes in behavior pattern
```

### Risk Scoring
```
Calculate dynamic risk score:

User Risk:
+ 0 if MFA enabled
+ 10 if no MFA
+ 20 if password weak
+ 30 if recent password breach

Device Risk:
+ 0 if compliant
+ 10 if non-compliant
+ 20 if jailbroken/rooted
+ 15 if antivirus disabled

Access Context Risk:
+ 0 if during business hours, office network
+ 5 if evening, office network
+ 10 if during business hours, home network
+ 20 if unusual location
+ 30 if international location change

Total Risk Score:
0-20: Low risk → Grant access
20-50: Medium risk → Additional verification
50-100: High risk → Deny or short-lived access
100+: Critical risk → Block, investigate
```

## Data Protection

### Classification
```
Public Data:
- Publicly available information
- Marketing materials
- Published documentation
- No special protection needed

Internal Data:
- Company policies
- Internal announcements
- General business information
- Standard encryption

Confidential Data:
- Financial information
- Strategic plans
- Employee information
- Requires encryption, access control

Restricted Data:
- Credit card data (PCI)
- Healthcare data (HIPAA)
- Personal identifying information (PII)
- Highest protection level
```

### Encryption Strategies
```
Data in Transit:
- TLS 1.2 minimum (1.3 preferred)
- Perfect Forward Secrecy
- Strong cipher suites
- Certificate validation
- Mutual TLS for service-to-service

Data at Rest:
- AES-256 encryption
- Separate key management
- Key rotation policies
- Hardware security module (HSM)
- Access control to keys
```

### Data Loss Prevention (DLP)
```
Monitor and control:
- File transfers
- Email attachments
- Cloud uploads
- Print operations
- Copy/paste operations
- Removable media access

Enforcement:
- Block prohibited actions
- Alert on suspicious activity
- Log all data access
- Quarantine suspect files
- Notify security team
```

## Threat Detection and Response

### Detection Systems

#### Endpoint Detection and Response (EDR)
```
On each device:
- Monitor process execution
- Track file access
- Monitor network connections
- Detect malicious activity
- Collect forensic data
- Enable threat hunting
```

#### Network Detection and Response (NDR)
```
Network traffic analysis:
- Packet inspection
- Flow analysis
- Anomaly detection
- Protocol anomalies
- Data exfiltration detection
- Malware detection
```

#### Security Information Event Management (SIEM)
```
Centralized logging:
- Authentication logs
- Authorization logs
- Network traffic logs
- Application logs
- Endpoint logs
- Correlation and analysis
```

### Incident Response

```
Incident detection:
├─ Alert generated
├─ Severity assessment
├─ Initial investigation
└─ Escalation if needed

Incident containment:
├─ Isolate affected user/device
├─ Revoke tokens
├─ Block network access
├─ Prevent lateral movement
└─ Preserve evidence

Incident eradication:
├─ Remove malware
├─ Patch vulnerabilities
├─ Reset credentials
├─ Rebuild systems
└─ Restore from clean backups

Post-incident:
├─ Root cause analysis
├─ Policy improvements
├─ Security training
├─ Enhanced monitoring
└─ Communication
```

## Implementation Roadmap

### Phase 1: Foundation (Months 1-3)
```
- Establish identity governance
- Deploy MFA globally
- Create device inventory
- Assess current segmentation
- Plan architecture
```

### Phase 2: Identity (Months 3-6)
```
- Implement centralized identity
- Deploy SSO
- Enforce MFA everywhere
- Create group policies
- Establish compliance checks
```

### Phase 3: Verification (Months 6-9)
```
- Deploy conditional access
- Implement device compliance
- Enable continuous monitoring
- Set up analytics
- Create policies
```

### Phase 4: Segmentation (Months 9-12)
```
- Deploy microsegmentation pilots
- Test segmentation policies
- Implement VLAN isolation
- Deploy network controls
- Monitor and refine
```

### Phase 5: Detection (Months 12-15)
```
- Deploy EDR solutions
- Implement SIEM
- Enable threat detection
- Create playbooks
- Training and exercises
```

### Phase 6: Optimization (Months 15+)
```
- Fine-tune policies
- Reduce false positives
- Optimize performance
- Continuous improvement
- Advanced threat hunting
```
