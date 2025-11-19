# Network Segmentation Reference

## Overview

Complete guide to network segmentation strategies, security zone design, and VLAN implementation for enterprise networks.

## Segmentation Models

### Traditional Perimeter Model
```
Internet
    |
    | (Firewall)
    |
    +------ DMZ
    |        (Web, Mail, DNS servers)
    |
    +------ Internal Network
             (Workstations, servers, databases)
```

**Characteristics**
- Single perimeter defense
- Limited internal segmentation
- Single point of failure
- No lateral movement prevention

**Issues**
- Compromised internal host can access any resource
- Slow breach detection
- Difficult to contain incidents
- Legacy model, still common

### Multi-Tier Segmentation Model
```
Internet
    |
    | (Perimeter Firewall)
    |
    +------ DMZ (Tier 1)
    |        |-- Web Servers
    |        |-- Mail Servers
    |        |-- DNS Servers
    |
    | (Internal Firewall)
    |
    +------ Application Tier (Tier 2)
    |        |-- Application Servers
    |        |-- Integration Services
    |
    | (Database Firewall)
    |
    +------ Database Tier (Tier 3)
             |-- Primary DB
             |-- Secondary DB
             |-- Backup Services
```

**Characteristics**
- Multiple security boundaries
- Explicit inter-tier communication rules
- Controlled data flow
- Breach containment

**Advantages**
- Limits lateral movement
- Clear security policies
- Easier incident response
- Better compliance alignment

### Zero Trust Segmentation Model
```
Perimeter
    |
    +------ User Zone
    |
    +------ Device Zone
    |
    +------ Service Zone 1
    |
    +------ Service Zone 2
    |
    +------ Data Zone
    |
    +------ Management Zone

All zones protected with:
- Identity verification
- Device compliance checks
- Continuous monitoring
- Microsegmentation rules
```

**Characteristics**
- No implicit trust zones
- Identity-centric access
- Continuous verification
- Microsegmentation

## Security Zones

### Zone Types and Responsibilities

#### Internet/Untrusted Zone
```
Characteristics:
- Highest risk
- No trust assumptions
- Incoming traffic scrutinized
- All inbound traffic denied by default

Controls:
- DDoS protection
- Ingress filtering
- Protocol validation
- Rate limiting
```

#### DMZ (Demilitarized Zone)
```
Purpose: Public-facing services
Access:
- Inbound: Specific ports from Internet
- Outbound: Limited internal access
- Internal: Restricted management only

Services:
- Web servers (HTTP/HTTPS)
- Mail servers (SMTP, POP3, IMAP)
- DNS servers
- VPN endpoints
- Proxy servers

Controls:
- Host-based firewall
- Antivirus protection
- Log monitoring
- Intrusion detection
```

#### Internal Zone
```
Purpose: Corporate services and users
Access:
- Outbound to DMZ and Internet
- Limited external inbound
- Controlled internal access
- User workstations

Services:
- File servers
- Print servers
- Collaboration tools
- Directory services

Controls:
- Network segmentation (VLANs)
- Access control
- Antivirus/Anti-malware
- Endpoint detection and response
```

#### Restricted/Database Zone
```
Purpose: Sensitive business data
Access:
- Highly restricted inbound
- Specific source validation
- Encrypted communications
- Audit logging

Services:
- Database servers
- Financial systems
- Healthcare records (PHI)
- Payment processing

Controls:
- Encryption at rest and in transit
- Multi-factor authentication
- Detailed audit logging
- Data loss prevention (DLP)
- Regular security assessments
```

#### Management Zone
```
Purpose: Administrative access
Access:
- Out-of-band management
- Separate network preferred
- Encrypted protocols only
- Multi-factor authentication

Services:
- SSH/Telnet servers
- HTTPS management interfaces
- Monitoring systems
- Patch management

Controls:
- Bastion hosts
- Jump servers
- Session recording
- MFA enforcement
```

#### Guest/External Zone
```
Purpose: Visitors and contractors
Access:
- Isolated from internal
- Internet-only access
- Time-limited
- Monitored access

Services:
- Guest Wi-Fi
- Contractor access
- Partner connections
- Public services

Controls:
- Captive portal
- Bandwidth limiting
- DLP enforcement
- Session timeout
```

## VLAN-Based Segmentation

### VLAN Segmentation Model

```
Physical Network:
Multiple devices on same switch

VLAN Segmentation:
Switch Port Configuration:
|
+-- Port 1-5: VLAN 10 (Users)
|
+-- Port 6-10: VLAN 20 (Servers)
|
+-- Port 11-15: VLAN 30 (Management)
|
+-- Port 16-20: VLAN 40 (Guest)

Trunk Port: Carries all VLANs to core switch

Core Switch:
|
+-- VLAN 10: 10.1.1.0/24 (Users)
+-- VLAN 20: 10.1.2.0/24 (Servers)
+-- VLAN 30: 10.1.3.0/24 (Management)
+-- VLAN 40: 10.1.4.0/24 (Guest)

Inter-VLAN Routing:
Router or Layer 3 Switch enforces access control
```

### VLAN Configuration Best Practices

#### Numbering Scheme
```
VLAN 1: Default (disable)
VLAN 2-9: Reserved/Unused
VLAN 10-49: User segments
VLAN 50-99: Server segments
VLAN 100-149: Management/Administration
VLAN 150-199: Guest/External
VLAN 200-299: Temporary/Lab
VLAN 999: Native VLAN (unused)
VLAN 1000-4094: Extended range

Example:
VLAN 10: Office Users - 10.1.10.0/24
VLAN 11: Remote Workers - 10.1.11.0/24
VLAN 12: Guest Users - 10.1.12.0/24
VLAN 50: Web Servers - 10.1.50.0/24
VLAN 51: App Servers - 10.1.51.0/24
VLAN 52: Database - 10.1.52.0/24
VLAN 100: Management - 10.1.100.0/24
VLAN 101: Switches - 10.1.101.0/24
VLAN 102: Firewalls - 10.1.102.0/24
```

#### Configuration Template
```
! Create VLAN
vlan 10
 name USERS_VLAN
 description Office Users Segment

! Assign ports to VLAN
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
 description User Workstations

! Create trunk for multi-VLAN
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50,100
 switchport nonegotiate
 description Link to Core Switch

! Configure VLAN interface (SVI)
interface Vlan10
 name USERS_VLAN
 ip address 10.1.10.1 255.255.255.0
 description Gateway for VLAN 10
```

## Firewall-Based Segmentation

### Zone-Based Firewall Model
```
Zone Definitions:
|
+-- OUTSIDE (Internet)
+-- DMZ
+-- INSIDE
+-- RESTRICTED

Policy Rules:
|
+-- OUTSIDE -> DMZ: Allow web services only
+-- OUTSIDE -> INSIDE: Deny all
+-- OUTSIDE -> RESTRICTED: Deny all
+-- DMZ -> INSIDE: Allow application traffic only
+-- INSIDE -> RESTRICTED: Allow specific queries only
+-- INSIDE -> OUTSIDE: Allow specific services
+-- RESTRICTED -> anything: Deny all
```

### Inter-Zone Policies

```
Class Map (Traffic Classification):
class-map type inspect match-any WEB_SERVICES
 match protocol http
 match protocol https

Policy Map (Zone Pair Rules):
policy-map type inspect OUTSIDE_TO_DMZ
 class WEB_SERVICES
  inspect
 class class-default
  drop

! Apply to zone pair
zone-pair security OUTSIDE-DMZ source OUTSIDE destination DMZ
 service-policy type inspect OUTSIDE_TO_DMZ
```

## Microsegmentation

### Concept
- Extreme granularity in network segmentation
- Segment at application/service level
- Not just network boundaries
- Zero trust at network layer

### Implementation Approaches

#### Host-Based Approach
```
Individual host firewall rules
Each server: specific incoming/outgoing ports
Service-level firewall rules
Requires:
- Host-based agents
- Centralized management
- Detailed inventory
```

#### Network-Based Approach
```
IP subnet segmentation
Very specific network ranges
Firewall rules per subnet pair
Requires:
- Dense firewall rulesets
- More network overhead
- Precise IP planning
```

#### Software-Defined Approach
```
Network policies through orchestration
API-driven segmentation
Automated policy application
Requires:
- SDN controllers
- Network virtualization
- API integration
```

### Example: Database Microsegmentation

```
Without Microsegmentation:
- All app servers can access all databases
- Lateral movement possible
- Breach scope is large

With Microsegmentation:
- App Server 1 -> DB Instance 1 only (port 3306)
- App Server 2 -> DB Instance 2 only (port 5432)
- App Server 3 -> DB Instance 1,2 (specific ports only)
- No app server can access other app servers
- DBA admin access via jump host only
```

## DMZ Architecture

### Single-Tier DMZ
```
Internet
    |
  [Firewall]
    |
   DMZ  (Single tier)
    |  All public services
    |  - Web servers
    |  - Mail servers
    |  - DNS servers
    |
  [Firewall]
    |
   Internal
```

**Advantages**: Simplicity
**Disadvantages**: Limited segregation, single point of failure

### Multi-Tier DMZ
```
Internet
    |
  [Firewall]
    |
   DMZ Tier 1 (Web)
    |  HTTP/HTTPS servers
    |
  [Firewall]
    |
   DMZ Tier 2 (Application)
    |  App servers
    |  API servers
    |
  [Firewall]
    |
   DMZ Tier 3 (Support Services)
    |  DNS, Mail, NTP
    |
  [Firewall]
    |
   Internal
```

**Advantages**: Better control, easier containment
**Disadvantages**: More complexity, more firewalls

### Screened Subnet Architecture
```
Internet
    |
  [Firewall] (Outer)
    |
  DMZ
    +-- Public servers
    |
  [Firewall] (Inner)
    |
  Internal
```

## Segmentation Rules Examples

### Rule Set: DMZ to Internal
```
# Allow only specific application traffic
Source: DMZ Tier 1 (Web Servers)
Destination: Internal Application Servers
Protocol: TCP
Port: 8080, 8443 (application ports)
Action: ALLOW

# Deny database access directly
Source: DMZ Tier 1
Destination: Database Servers
Action: DENY

# Allow DNS and NTP
Source: Any DMZ
Destination: Internal DNS/NTP
Protocol: UDP
Port: 53, 123
Action: ALLOW
```

### Rule Set: Internal to Restricted
```
# Allow specific application to database
Source: Internal Application Servers only
Destination: Database Server 192.168.1.50
Protocol: TCP
Port: 3306 (MySQL)
Action: ALLOW

# Require encryption
Encryption: TLS required

# Deny other internal to database
Source: Any other internal
Destination: Database
Action: DENY

# Allow DBA access via jump host
Source: Jump Host 10.1.100.10
Destination: Database Servers
Protocol: TCP
Port: 3306, 5432
Require: MFA authentication
Action: ALLOW
```

## Segmentation Monitoring and Enforcement

### Monitoring
```
Flow logging between segments
Track allowed and denied traffic
Alert on policy violations
Detect lateral movement attempts
Identify unauthorized access patterns
```

### Enforcement
```
Firewall rules automation
Policy as Code
Regular validation
Compliance verification
Incident response integration
```

## Migration to Segmentation

### Phase 1: Assessment
- Document current network
- Identify critical assets
- Map data flows
- Define security zones

### Phase 2: Planning
- Design segmentation model
- Plan VLAN allocation
- Define firewall policies
- Identify dependencies

### Phase 3: Implementation
- Deploy in lab first
- Test thoroughly
- Implement in phases
- Minimize business disruption

### Phase 4: Monitoring
- Monitor for issues
- Fine-tune policies
- Document changes
- Plan optimization
