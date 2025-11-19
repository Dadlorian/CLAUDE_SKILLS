# Network Segmentation Guide

## Introduction
This guide covers implementing network segmentation for security, compliance, and operational efficiency.

## Segmentation Concepts

### Goals of Segmentation

```
Security:
  - Limit lateral movement if breach occurs
  - Restrict access to sensitive data
  - Reduce attack surface
  - Implement zero-trust principles

Compliance:
  - PCI-DSS: Segment cardholder data
  - HIPAA: Isolate patient data
  - SOC2: Separate customer data
  - GDPR: Encrypt and isolate PII

Operations:
  - Isolate test/dev from production
  - Separate voice/video from data
  - Manage QoS per segment
  - Simplify troubleshooting

Efficiency:
  - Limit broadcast domains
  - Reduce unnecessary traffic
  - Improve performance
  - Ease resource sharing
```

## Segmentation Models

### User-Based Segmentation

```
Organization structure:

Department VLANs:
  VLAN 10: Executive (sensitive, restricted)
  VLAN 20: Finance (PCI-DSS, restricted)
  VLAN 30: Engineering (open, development)
  VLAN 40: Operations (standard)
  VLAN 50: Sales (standard)
  VLAN 100: Guest (minimal access)

Segmentation policies:

Executive ↔ Finance:
  Permitted: Executive can read Finance (for approval)
  Denied: Finance cannot access Executive

Finance ↔ Engineering:
  Denied: No access (separate functions)

All ↔ Guest:
  Denied: Guest cannot access any internal
  Permitted: Internet access only

Configuration:
  VLAN ACLs block unauthorized inter-VLAN traffic
  Firewall backs up network segmentation
  Logging tracks all policy violations
```

### Function-Based Segmentation

```
Security zones:

DMZ (Demilitarized Zone):
  VLAN 70 - Web servers (public-facing)
  Access: Internet → Web (inbound)
  Access: Web → Internet (outbound)
  Denied: Web → Internal networks (no DB access)
  Database access: Via API gateway only

Application Tier:
  VLAN 71 - Application servers (internal)
  Access: Web → App tier (business logic)
  Access: App → Database (data queries)
  Denied: Internet → App (no direct)

Database Tier:
  VLAN 72 - Database servers (most protected)
  Access: App → Database (queries only)
  Denied: Internet → Database
  Denied: Web → Database (only via app tier)

Backup Tier:
  VLAN 73 - Backup servers
  Access: All servers → Backup (push model)
  Backup → All servers: Backups (pull restore)
  Denied: Internet → Backup

Management:
  VLAN 200 - Network management
  Access: Network team → All switches
  Denied: Users → Management (restricted)
  Access: Management → Internet (limited)
```

### Data-Based Segmentation

```
Sensitivity levels:

Level 1 - Public:
  Data: Public website, marketing materials
  VLAN: 50 (Sales/Marketing)
  Protection: Basic (standard firewall rules)
  Encryption: Not required

Level 2 - Internal:
  Data: Internal documents, employee info
  VLAN: 10-40 (User VLANs)
  Protection: Standard (VLANs + ACLs)
  Encryption: In-transit (TLS)

Level 3 - Sensitive:
  Data: Customer PII, financial data
  VLAN: 60 (Sensitive VLAN, restricted)
  Protection: Enhanced (encryption, access control)
  Encryption: At-rest and in-transit
  Access: Minimal (specific users/groups only)

Level 4 - Highly Restricted:
  Data: Credit cards (PCI-DSS), health records (HIPAA)
  VLAN: 61 (Isolated VLAN)
  Protection: Maximum (air-gapped, encrypted)
  Encryption: Always required
  Access: Manual approval, audit trail
  Network: Separate network segment

Implementation:
  User VLAN → Sensitive VLAN: Via firewall (authentication)
  User VLAN ↔ Public VLAN: Direct (no restriction)
  Public VLAN → Sensitive: Blocked (network layer)
```

## Implementation Methods

### VLAN-Based Segmentation

```
Basic approach using VLANs:

Advantages:
  - Simple to implement
  - Standard feature (all switches support)
  - Low cost
  - Easy to understand

Disadvantages:
  - Limited to same physical network
  - Depends on correct VLAN tagging
  - User can bypass with VLAN hopping (rare)
  - Not foolproof (defense-in-depth needed)

Configuration:

Step 1: Create VLANs
  VLAN 10: Executive
  VLAN 20: Finance
  VLAN 100: Guest

Step 2: Assign ports
  Ports 1-5: VLAN 10
  Ports 6-15: VLAN 20
  Ports 16-24: VLAN 100

Step 3: Enable routing (on distribution)
  interface Vlan 10
    ip address 10.0.10.1 255.255.255.0
  interface Vlan 20
    ip address 10.0.20.1 255.255.255.0
  interface Vlan 100
    ip address 10.0.100.1 255.255.255.0
  ip routing

Step 4: Apply ACLs (default permit, then deny)
  By default: All VLANs can communicate (routing)
  Apply ACL to block unauthorized
```

### Firewall-Based Segmentation

```
Advanced approach using firewalls:

Advantages:
  - More granular control (port/protocol level)
  - Stateful inspection (understands application)
  - Logging/auditing (all connections recorded)
  - Threat protection (IDS/IPS integration)

Disadvantages:
  - More complex to manage
  - Higher cost
  - Single point of failure (if not redundant)
  - Performance impact (all traffic inspected)

Configuration:

Zone 1: Untrusted (Internet)
Zone 2: DMZ (Web servers)
Zone 3: Trust (Internal network)
Zone 4: Database (Most protected)

Rules:
  Internet → DMZ (Web): Allow 80/443
  DMZ → Internet: Allow (stateful)
  DMZ → Trust: Deny
  DMZ → Database: Deny
  Trust → Database: Allow (specific DB port)
  Trust → Internet: Allow

Logging:
  All denied connections: Log (security monitoring)
  Suspicious patterns: Alert (IDS)
  Monthly review: Policy effectiveness
```

### Zero-Trust Segmentation

```
Modern approach: Assume breach, verify everything

Principles:
  - Default deny (nothing allowed until approved)
  - Verify identity (who is it?)
  - Verify device (is it trusted?)
  - Verify location (where is it from?)
  - Verify application (what is it accessing?)

Implementation:

User authentication:
  - User logs in with credentials
  - Credentials verified (AD/LDAP)
  - MFA verification (second factor)
  - Token issued for access

Device verification:
  - Device health checked (antivirus, patches)
  - Device compliance verified (not jailbroken)
  - Device policy enforced (encryption, VPN)

Network access:
  - User authenticated: Access granted
  - User not authenticated: Access denied
  - Device compromised: Access revoked
  - Location suspicious: Challenge

Application access:
  - Application specified (not just network)
  - Port/protocol verified
  - Data classification checked
  - Access logged for audit

Benefits:
  - Breach contained (segmentation tight)
  - Insider threat reduced (verification required)
  - Compliance easier (audit trail complete)
  - Flexibility (users work from anywhere securely)
```

## Segmentation by Scenario

### Healthcare (HIPAA Compliance)

```
Requirement: Patient data isolated and protected

Segmentation:

VLAN 50: Clinical (Protected Health Information - PHI)
  - Electronic health records (EHR)
  - Patient data access
  - Access control: Healthcare professionals only
  - Encryption: Required (in-transit, at-rest)
  - Audit: Complete (who accessed what, when)

VLAN 51: Administrative (PII)
  - Billing, scheduling, insurance
  - Access control: Admin staff only
  - Encryption: Required
  - Audit: Complete

VLAN 52: Research (De-identified data)
  - Research purposes
  - Access control: Researchers only
  - Encryption: Required
  - Audit: Limited (privacy protected)

VLAN 100: Guest
  - Visitor WiFi
  - Internet access only
  - No healthcare data access
  - Standard firewall rules

Enforcement:
  - Network: VLANs separate traffic
  - Firewall: ACLs enforce access
  - Authentication: 802.1X or VPN
  - Encryption: VPN tunnel to clinical VLAN
```

### Financial Services (PCI-DSS)

```
Requirement: Credit card data protected

Segmentation:

VLAN 60: Cardholder Data Environment (CDE)
  - Payment terminals
  - Card readers
  - PCI-DSS compliant systems only
  - Access: Highly restricted
  - Network: Isolated (no internet)
  - Firewall: Stateful inspection required

VLAN 61: Card Database
  - Credit card database
  - Encrypted storage (3DES minimum, AES preferred)
  - Access: Application servers only (via secure channel)
  - Monitoring: Real-time IDS/IPS
  - Audit: Complete transaction logging

VLAN 40: Operations (Non-card)
  - Back office operations
  - Separated from CDE
  - Firewall prevents access to CDE

Compliance requirements:
  - Network segmentation verified (firewall rules)
  - Vulnerability scans monthly (external, internal)
  - Penetration testing annual
  - Audit: 4-6 times per year (assurance)
```

### Enterprise (Multiple Segments)

```
Typical enterprise segmentation:

VLAN 10-19: User access (by department)
VLAN 20-29: Services (printing, conferencing)
VLAN 30-39: Testing/development
VLAN 40-49: Production servers
VLAN 50-59: Database
VLAN 100: Guest
VLAN 110: Voice
VLAN 200: Management

Access controls:

Users → Production: Firewall (limited, task-specific)
Users → Testing: Direct (development purpose)
Testing → Production: Firewall (approve before change)
Production → Database: Direct (same VLAN class)
Database → Internet: Blocked (outbound prevented)
Internet → Database: Blocked (inbound prevented)
Management → All: Direct (for network team)
All → Management: Blocked (except network team)

Result:
  - Users can do their work (via firewall rules)
  - Malware contained (no lateral movement)
  - Testing isolated (no production impact)
  - Database protected (no direct internet)
```

## Testing and Validation

```
Validation procedures:

Step 1: Design verification
  [ ] Segmentation diagram complete
  [ ] All data flows documented
  [ ] ACLs reviewed for correctness
  [ ] Firewall rules validated

Step 2: Configuration verification
  [ ] VLANs created as designed
  [ ] Ports assigned correctly
  [ ] ACLs applied to correct interfaces
  [ ] Firewall rules in place

Step 3: Functional testing
  [ ] Allowed traffic passes (within VLAN)
  [ ] Allowed traffic passes (firewall rules)
  [ ] Blocked traffic blocked (inter-VLAN)
  [ ] Blocked traffic blocked (firewall)

Step 4: Security testing
  [ ] Ping test between VLANs (should fail)
  [ ] Traceroute to blocked destination (stops at firewall)
  [ ] Port scan from user VLAN to database (no results)
  [ ] Intentional policy violation attempt (blocked, logged)

Step 5: Documentation
  [ ] Network diagram with segmentation
  [ ] ACL listing with purpose
  [ ] Access matrix (who can access what)
  [ ] Change log (who made what changes when)
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Advanced
**Compliance:** PCI-DSS, HIPAA, SOC2, GDPR
