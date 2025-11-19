# Zero Trust Network Access (ZTNA) Implementation Guide

## Overview
Implement zero trust principles for network access with continuous verification, device posture checking, and micro-segmentation.

## Phase 1: Foundation Assessment

### Current State Analysis

```
Existing Security Model (Castle-and-Moat):
  - Perimeter firewall (main defense)
  - Network segmentation (VLAN-based)
  - All internal traffic trusted
  - VPN for remote access
  - Limited monitoring

Security Gaps:
  - Lateral movement possible
  - Compromised internal device = full access
  - No continuous verification
  - Historical breach data shows need for change
  - Regulatory requirements for zero trust
```

### Zero Trust Target State

```
New Model (Zero Trust):
  - Identity verification for every access
  - Device posture verification
  - Application-level access control
  - Encryption mandatory
  - Continuous monitoring and response
  - Assume breach posture
```

## Phase 2: Identity Foundation

### IAM Implementation

**Azure AD / Okta Setup**

```
Step 1: Configure Identity Provider
  - Centralized user directory
  - MFA enforcement
  - Conditional access policies
  - Session management

Step 2: Enable MFA
  - Hardware token (FIDO2 preferred)
  - Software token (Authenticator app)
  - SMS OTP (backup only, less secure)
  - Biometric (Windows Hello, fingerprint)

Step 3: Conditional Access Policies
  Policy 1 - Admin Access
    Requires:
      - MFA mandatory
      - Compliant device only
      - Known location or no new location
      - Risk-based re-authentication

  Policy 2 - General User Access
    Requires:
      - MFA (configurable)
      - Device compliance check
      - Suspicious activity blocking
      - Session timeout (30 minutes)

  Policy 3 - Sensitive Data Access
    Requires:
      - MFA mandatory
      - Compliant device
      - Approved application only
      - Geo-fencing enforcement
```

**Directory Configuration**

```
User Attributes:
  - Department
  - Manager
  - Job Title
  - Security Group Membership
  - Device Registration Status
  - Compliance Status

Group Policies:
  - Finance: Access to financial applications
  - Engineering: Access to development tools
  - Sales: Access to CRM and collaboration
  - IT: Full administrative access
  - Contractors: Limited, time-bound access
```

## Phase 3: Device Trust

### Device Registration and Enrollment

**Windows Device Setup**

```
1. Azure AD Join
   Settings > System > About
   Access work or school > Connect
   Sign with corporate account
   Complete registration

2. Mobile Device Management (MDM) Enrollment
   Portal: https://enrollment.manage.microsoft.com
   Platform: Intune
   Enroll company-owned and personal devices
   Apply security baseline

3. Compliance Policies
   - OS Version: Windows 10 version 1909+
   - Antivirus: Defender or Symantec running
   - Firewall: Windows Defender Firewall enabled
   - Disk Encryption: BitLocker enabled
   - Patches: Current within 30 days
```

**Mobile Device Enrollment**

```
iOS:
  1. Download Microsoft Intune Company Portal
  2. Sign in with corporate account
  3. Enroll device
  4. Install compliance policies
  5. Configure mail, VPN, apps

Android:
  1. Google Play: Install Intune Company Portal
  2. Sign in with corporate account
  3. Enroll device
  4. Apply security profiles
  5. Enable required applications

macOS:
  1. Apple App Store: Install Intune Company Portal
  2. Sign in with work account
  3. Register device
  4. Accept management profile
  5. Apply compliance policies
```

### Compliance Configuration

**Intune Compliance Policy**

```
Windows Compliance Policy: Corporate-Standard
  OS Requirement: Windows 10 version 1909 or later
  Antivirus: Required, must be running
  Antispyware: Required, must be running
  Firewall: Required, must be enabled
  Disk Encryption: Required (BitLocker)
  Password Requirement: 12 characters, complexity
  Password Age: 60 days maximum
  Device Security: Secure boot enabled
  Threat Detection: Required

Non-Compliant Actions:
  - Grace Period: 7 days
  - Email notification: Automatic
  - Remediation: Display guidance
  - Access Block: After grace period
```

## Phase 4: Access Gateway Deployment

### Palo Alto Prisma Access Setup

**Architecture**

```
Components:
  1. Prisma Access (Cloud): Centralized access control
  2. Mobile User Security: Client protection
  3. Remote Networks: Site-to-cloud connectivity
  4. Secure Web Gateway: Traffic inspection

Deployment Mode:
  - Cloud-based (no on-premises infrastructure)
  - Distributed globally (180+ PoPs)
  - Automatic failover and load balancing
  - Zero trust enforcement
```

**Configuration Steps**

```
1. Administrative Setup
   Prisma Access > Setup > Locations
   Location Name: Primary-DC
   Address: Internal data center
   Subnets: 10.0.0.0/8, 192.168.0.0/16

2. Identity Integration
   Settings > Identity & Access > IdP Configuration
   Provider: Azure AD (or Okta)
   Tenant ID: [Azure tenant ID]
   Application ID: [Registered application]
   Secret: [App secret]

3. Access Policies
   Monitor > Security > Access Control
   Rules:
     Rule 1: Allow AD users to cloud apps (O365, Salesforce)
     Rule 2: Block non-compliant devices
     Rule 3: Allow office network to internal apps
     Rule 4: Block unknown locations

4. Device Compliance
   Advanced > Device Profiles
   Profile: Corporate-Compliance
     Antivirus: Required (Defender, Symantec)
     Firewall: Windows Defender or McAfee
     Disk Encryption: BitLocker or Filevault
     OS Patches: Current within 30 days
     Max OS Age: 5 years
```

## Phase 5: Micro-Segmentation

### Application-Level Access Control

**Segmentation Policy**

```
Segment 1: Finance Applications
  Resources:
    - SAP Finance module
    - Oracle Accounting
    - Tax software
  Access:
    - Finance department staff
    - Compliant devices
    - Business hours (M-F, 7 AM-6 PM)
    - No external access
  Rules:
    - Encryption: TLS 1.3
    - MFA: Required
    - Session timeout: 30 minutes
    - Re-authentication: Every 4 hours

Segment 2: Engineering Development
  Resources:
    - Source code repository (GitHub)
    - CI/CD pipeline (Jenkins, Azure DevOps)
    - Development databases
    - Test environments
  Access:
    - Engineering team + approved contractors
    - Company-owned devices or compliant BYOD
    - No time restrictions (dev work is 24/7)
    - VPN required for remote access
  Rules:
    - Encryption: IPsec or WireGuard
    - MFA: Required for sensitive repositories
    - Device: Must have 2FA enabled
    - Audit: All commands logged

Segment 3: HR Systems
  Resources:
    - Payroll system
    - Benefits management
    - Employee records
  Access:
    - HR staff + system administrators
    - Compliant devices only
    - Internal network only
    - Geofencing to office location
  Rules:
    - Encryption: Mandatory TLS 1.3
    - MFA: Hardware token required
    - Device: Corporate-issued only
    - Monitoring: Real-time user behavior
```

### Network Micro-Segmentation

**Policy-Based Architecture**

```
Traditional (VLAN-based):
  - Segment by network location
  - Limited granularity
  - Difficult to scale
  - Lateral movement possible

Zero Trust (Policy-based):
  - Segment by application
  - User identity-driven
  - Device posture verified
  - Behavioral monitoring

Implementation:
  1. Identify Critical Assets
     - Finance databases
     - Intellectual property
     - Customer data
     - Admin accounts

  2. Create Security Zones
     - High Risk: External systems
     - Medium Risk: User workstations
     - Low Risk: Collaboration tools
     - High Security: Finance, HR, R&D

  3. Define Allowed Connections
     - Source: User + device combination
     - Destination: Specific application
     - Authentication: MFA required
     - Encryption: Mandatory
     - Monitoring: All traffic logged

  4. Enforce with Firewall Rules
     crypto map, security groups, network policies
```

## Phase 6: Continuous Monitoring

### Real-time Threat Detection

**Behavioral Analytics**

```
User Behavior Baseline:
  - Login times and locations
  - Applications accessed
  - Files accessed
  - Data download patterns
  - Peer group analysis

Anomaly Detection:
  1. Impossible Travel
     Alert: User in NYC at 10 AM, London at 11 AM
     Response: Re-authenticate, block high-risk activity

  2. Unusual Data Access
     Alert: Finance user accessing HR database
     Response: Context check, challenge with MFA

  3. Off-hours Access
     Alert: Engineer accessing code at 3 AM
     Response: Notify manager, investigate

  4. Privilege Escalation
     Alert: Regular user attempting admin access
     Response: Block, escalate, investigate

  5. Credential Usage
     Alert: Credentials used from unknown device
     Response: Force password reset, revoke sessions
```

**Threat Intelligence Integration**

```
External Feeds:
  - Known compromised credentials
  - Malware signatures
  - Suspicious IP addresses
  - Botnet indicators
  - Zero-day exploits

Response Actions:
  - Block suspicious IPs automatically
  - Force re-authentication for compromised credentials
  - Quarantine infected devices
  - Isolate high-risk users
  - Alert security team
```

### Logging and Audit

**Centralized Logging**

```
Event Categories:
  1. Authentication Events
     - Successful login
     - Failed login attempts
     - MFA success/failure
     - Session creation/termination

  2. Authorization Events
     - Access granted
     - Access denied
     - Policy violations
     - Permission changes

  3. Data Access Events
     - File access (read, write, delete)
     - Database queries
     - API calls
     - Report generation

  4. System Events
     - Device registration
     - Policy enforcement
     - Compliance status changes
     - Software updates

Log Retention:
  - Real-time analysis: 30 days hot
  - Operational: 1 year warm
  - Compliance/forensics: 7 years archived
  - Immutable storage: Secure backup

SIEM Integration:
  - Aggregate from multiple sources
  - Real-time correlation
  - Custom alert rules
  - Automated response workflows
```

## Phase 7: Incident Response

### Preparation

**Incident Response Team**
```
- Security lead (escalation)
- Network engineer (containment)
- System administrator (remediation)
- Compliance officer (reporting)
- Communications (notification)
```

**Response Playbooks**

```
Playbook 1: Credential Compromise
  1. Detect: Flag in threat intelligence
  2. Alert: Immediate notification
  3. Containment: Revoke all sessions
  4. Investigation: Review access logs
  5. Remediation: Force password reset
  6. Recovery: Monitor for reuse
  7. Communication: Notify user
  8. Lessons: Adjust MFA policies

Playbook 2: Malware Detection
  1. Detect: AV alert on endpoint
  2. Contain: Isolate device from network
  3. Investigate: Analyze malware
  4. Clean: Remove malware, restore OS
  5. Verify: Clean file and behavioral scans
  6. Re-enroll: Device in MDM
  7. Update: Threat signatures distributed
  8. Communication: Notify user and management

Playbook 3: Unauthorized Access Attempt
  1. Detect: Access denied alert
  2. Investigate: Review context and intent
  3. Contact: Reach out to user for verification
  4. Response: Increase monitoring, challenge future access
  5. If Malicious: Block account, investigate device
  6. Communication: Notify manager and user
  7. Follow-up: Additional training for user
```

## Phase 8: Deployment and Rollout

### Phased Implementation

**Phase 1: Foundation (Months 1-2)**
- [ ] Azure AD/Okta deployment and configuration
- [ ] MFA rollout (hardware tokens for admins)
- [ ] Device registration/enrollment
- [ ] Compliance policy creation
- [ ] Audit baseline of access patterns

**Phase 2: Access Gateway (Months 3-4)**
- [ ] Prisma Access deployment
- [ ] Identity provider integration
- [ ] Access policy creation
- [ ] Remote user migration
- [ ] Performance optimization

**Phase 3: Micro-Segmentation (Months 5-6)**
- [ ] Critical asset identification
- [ ] Policy definition for each segment
- [ ] Firewall rule implementation
- [ ] Testing in audit mode
- [ ] Gradual enforcement

**Phase 4: Monitoring (Months 7-8)**
- [ ] SIEM deployment
- [ ] Log aggregation setup
- [ ] Alerting configuration
- [ ] Threat intelligence integration
- [ ] IR playbook documentation

**Phase 5: Optimization (Ongoing)**
- [ ] Policy tuning based on alerts
- [ ] User feedback incorporation
- [ ] Performance optimization
- [ ] Regular security assessments
- [ ] Technology updates

### User Communication

```
Week 1: Announcement
  - Explain zero trust concept
  - Benefits of new security model
  - Timeline for implementation
  - FAQ document published

Week 2: Training
  - MFA enrollment instructions
  - Device registration walkthrough
  - Compliance requirement details
  - Support contact information

Week 3: Pilot
  - 10% of users in pilot
  - Daily check-ins
  - Feedback collection
  - Issue resolution

Week 4+: Gradual Rollout
  - 20% per week
  - Ongoing support
  - Update communications
  - Celebrate milestones
```

## Phase 9: Ongoing Operations

### Monthly Reviews

```
Metrics to Track:
  - Authentication success rate
  - MFA adoption rate
  - Device compliance percentage
  - Blocked access attempts
  - Policy violation count
  - Incident response time

Reviews:
  - Identify trends
  - Adjust thresholds
  - Update policies
  - Plan optimizations
```

### Quarterly Assessment

```
Security Posture:
  - Penetration testing
  - Vulnerability scanning
  - Policy effectiveness review
  - Incident trend analysis
  - Compliance verification
```

## Best Practices Checklist

- [ ] MFA enforced for all users
- [ ] Device compliance mandatory
- [ ] Continuous authentication
- [ ] Encryption for all traffic
- [ ] Comprehensive logging
- [ ] Real-time threat detection
- [ ] Regular policy reviews
- [ ] User training program
- [ ] Incident response procedures
- [ ] Quarterly security assessments
- [ ] Vendor security management
- [ ] Disaster recovery planning
- [ ] Regular backup testing
- [ ] Supply chain security review
