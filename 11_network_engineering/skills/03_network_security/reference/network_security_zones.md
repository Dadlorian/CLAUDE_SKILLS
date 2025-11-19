# Network Security Zones Reference

## Zone Architecture Framework

### Traditional Three-Tier Model

```
┌─────────────────────────────────────────────────┐
│ EXTERNAL ZONE (Internet)                        │
│ - Untrusted                                     │
│ - Public access                                 │
│ - Threats: Any                                  │
└────────────────┬────────────────────────────────┘
                 │ [Perimeter Firewall]
                 ▼
┌─────────────────────────────────────────────────┐
│ PERIMETER ZONE (DMZ)                            │
│ - Semi-trusted                                  │
│ - Public services                               │
│ - Threats: Compromised systems                  │
└────────────────┬────────────────────────────────┘
                 │ [Internal Firewall]
                 ▼
┌─────────────────────────────────────────────────┐
│ INTERNAL ZONE                                   │
│ - More trusted                                  │
│ - Corporate systems                             │
│ - Threats: Insider, lateral movement           │
└─────────────────────────────────────────────────┘
```

## Zone Definitions and Characteristics

### EXTERNAL ZONE

#### Definition
```
Internet-facing networks and systems
No trust assumptions
Completely untrusted
Full threat surface
```

#### Characteristics
```
Access:
- Inbound: Filtered at perimeter
- Outbound: Any
- Internal: None

Trust Level: Zero
Threat Level: Maximum
Data Classification: None
```

#### Controls
```
Network Level:
- DDoS mitigation
- Ingress filtering (BCP 38)
- Rate limiting
- Protocol validation
- Stateful inspection

Application Level:
- Input validation
- Output encoding
- Authentication (MFA)
- TLS enforcement
- Security headers
```

#### Typical Components
- ISP networks
- Internet backbone
- CDNs
- Public clouds
- Partner networks

### DMZ (PERIMETER ZONE)

#### Definition
```
Buffer zone between Internet and internal network
Public-facing services
Higher security than internet
Lower security than internal
```

#### Architecture

```
┌─────────────────────────────────────┐
│      Internet                       │
└──────────────┬──────────────────────┘
               │
         [Perimeter FW]
               │
     ┌─────────┴──────────┐
     │ DMZ                │
     │ ┌────────────────┐ │
     │ │ Web Servers    │ │
     │ └────────────────┘ │
     │ ┌────────────────┐ │
     │ │ Mail Servers   │ │
     │ └────────────────┘ │
     │ ┌────────────────┐ │
     │ │ DNS Servers    │ │
     │ └────────────────┘ │
     │ ┌────────────────┐ │
     │ │ VPN Endpoint   │ │
     │ └────────────────┘ │
     └─────────┬──────────┘
               │
         [Internal FW]
               │
        [Internal Network]
```

#### Access Rules

```
To DMZ:
From Internet:
  - HTTP/HTTPS (port 80, 443) to web servers
  - SMTP (port 25) to mail servers
  - DNS (port 53) to DNS servers
From Internal:
  - Management (SSH, RDP) to all
  - Specific applications as needed

From DMZ:
To Internet:
  - Limited outbound (firewall policy)
  - Some services allowed (updates, time sync)
To Internal:
  - Very restricted
  - Only backend connections (database)
  - Encrypted channels preferred
  - Authenticated connections
```

#### DMZ Hosts

**Web/Application Servers**
```
Services:
- HTTP/HTTPS
- Application code
- Static content
- API endpoints

Restrictions:
- No internet access (except updates)
- Limited internal access
- Database access only to specific DB
- No direct access to file servers
- No administrative access
```

**Mail Servers**
```
Services:
- SMTP (inbound/outbound)
- POP3/IMAP (mail retrieval)
- Sieve/ManageSieve (filters)

Restrictions:
- Limited internet access (mail relay)
- Backend DB access (user lookup)
- No access to internal file systems
- No access to other internal systems
```

**DNS Servers**
```
Services:
- DNS recursive (if authoritative)
- DNS responses
- DNS updates

Restrictions:
- Public zone only
- Limited queries
- Rate limiting
- No zone transfers (except secondary)
```

**VPN/Remote Access**
```
Services:
- SSL VPN (port 443)
- IPsec (port 500, 4500)
- IKE (port 500)
- Authentication

Restrictions:
- Encryption required
- MFA required
- Access to specific internal resources
- Connection logging
- Session timeouts
```

### INTERNAL ZONE

#### Definition
```
Corporate network systems
Employee workstations
Internal services
File and application servers
Higher trust but still monitored
```

#### Segmentation

```
┌──────────────────────────────────────────────┐
│ INTERNAL NETWORK                             │
├──────────────────────────────────────────────┤
│ ┌──────────────┐   ┌──────────────┐          │
│ │ User VLAN    │   │ Guest VLAN   │          │
│ │ 10.1.10.0/24 │   │ 10.1.12.0/24 │          │
│ └──────────────┘   └──────────────┘          │
│                                              │
│ ┌──────────────────┐  ┌─────────────────┐   │
│ │ APP VLAN         │  │ DATABASE VLAN    │   │
│ │ 10.1.20.0/24    │  │ 10.1.30.0/24    │   │
│ └──────────────────┘  └─────────────────┘   │
│                                              │
│ ┌──────────────────────────────────────┐    │
│ │ MANAGEMENT VLAN                      │    │
│ │ 10.1.100.0/24                        │    │
│ └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

#### Controls

```
Network Controls:
- VLAN segmentation
- Access control lists
- Inter-VLAN routing restrictions
- Firewall policies
- Port security

Host Controls:
- Personal firewall
- Antivirus/EDR
- Patch management
- Device compliance
- Disk encryption

Application Controls:
- Authentication (AD/LDAP)
- Authorization (role-based)
- Data classification
- DLP policies
- Session timeout
```

### RESTRICTED ZONE

#### Definition
```
Highly sensitive data systems
Financial systems
Healthcare records
Payment processing
Maximum security
Minimum access
```

#### Access Model

```
Access Decision:
IF user in APPROVED_GROUP
  AND user MFA verified
  AND device compliant
  AND time in BUSINESS_HOURS
  AND no security incidents
  AND encrypted connection required
THEN grant access

ELSE deny access
```

#### Examples

**Payment Card Industry (PCI)**
```
VLAN 30: PCI Zone
10.1.30.0/24

Access:
- Specific servers only (payment processors)
- Specific users only (finance team)
- MFA required
- Encrypted connection (TLS 1.2+)
- All access logged
- Quarterly audits

Restrictions:
- No shared credentials
- No wireless access
- No removable media
- No print/copy allowed
- Separate management network
```

**Healthcare (PHI)**
```
VLAN 31: PHI Zone
10.1.31.0/24

Access:
- Authorized healthcare providers
- Patient data access only (job role)
- Encryption mandatory
- Access logging
- Annual training

Restrictions:
- No data export without approval
- No external USB/CD
- Automatic logout (15 min idle)
- Strong password (complexity, history)
- No local admin access
```

**Financial Systems**
```
VLAN 32: Financial Zone
10.1.32.0/24

Access:
- Finance department only
- Transaction approval required
- Dual authentication for high-value
- Everything logged
- Compliance monitoring

Restrictions:
- Change control required
- Segregation of duties
- Multi-approval workflow
- Regular reconciliation
- Audit trails immutable
```

### MANAGEMENT ZONE

#### Definition
```
Administrative access
Device management
Security monitoring
Out-of-band network
Highly restricted
Privileged access
```

#### Segregation

```
In-Band Management (on production network):
- SSH to network devices
- HTTPS to web interfaces
- Requires VPN access
- Access logged

Out-of-Band Management (separate network):
- Separate network interface
- Separate switch infrastructure
- Serial console access
- Emergency access
- Physical isolation
```

#### Architecture

```
┌──────────────────────────────┐
│ Management VLAN (10.1.100.0) │
│                              │
│  Devices:                    │
│  - Switch management IPs     │
│  - Firewall management IPs   │
│  - RADIUS servers            │
│  - Syslog servers            │
│  - NTP servers               │
│                              │
│  Access:                     │
│  - Jump host for SSH/RDP     │
│  - HTTPS only (TLS 1.2+)     │
│  - MFA required              │
│  - Source IP restricted      │
│  - Session logging           │
│  - Encryption required       │
└──────────────────────────────┘
```

#### Controls

```
Authentication:
- MFA required
- Account lockout after 3 failures
- Password policy (complexity, history)
- No shared accounts
- Session recording

Authorization:
- Role-based access control (RBAC)
- Principle of least privilege
- Temporary elevated rights
- Regular access review
- Segregation of duties

Encryption:
- TLS 1.2 minimum
- SSH with key-based auth
- No telnet/http
- VPN for remote access
- Encrypted logs transmission
```

### GUEST ZONE

#### Definition
```
Visitor and contractor access
Isolated from corporate network
Monitored access
Limited connectivity
Time-based access
```

#### Characteristics

```
Network: 10.1.12.0/24 (separate)
Access:
- Internet connectivity only
- No internal network access
- No internal service access
- No resource access

Restrictions:
- Bandwidth limited
- Time-limited (2 hours)
- MAC filtering option
- Captive portal
- Usage monitoring
```

#### Implementation

```
Guest Network Setup:
1. Separate VLAN for guests
2. Separate firewall zone
3. Internet-only access
4. Captive portal (authentication)
5. Usage agreement
6. Bandwidth limiting
7. Content filtering
8. Disconnect on timeout

Security:
- WPA2/WPA3 encryption
- Guest SSID only
- Regular deprovisioning
- Monitoring
- Incident response
```

## Cross-Zone Communication

### Allow Rules (Explicit)
```
DMZ Web Server → Internal Database
Source: 10.1.11.0/24 (DMZ Web VLAN)
Destination: 10.1.30.5 (DB Server)
Protocol: TCP
Port: 3306 (MySQL)
Action: ALLOW
Log: Yes

Rationale: Web app needs database access
```

### Deny Rules (Default)
```
Default: Deny all inter-zone traffic
Exception: Create explicit allow rules
Review: Quarterly
Documentation: Required for each exception
```

### Logging

```
Log Policy:
- Log all zone transitions
- Log denied traffic
- Compress old logs
- Centralize to SIEM
- Retention: 1+ year
- Compliance: Regulatory requirements
```

## Zone Implementation Checklist

```
Design Phase:
☐ Identify zones needed
☐ Document zone purpose
☐ Define security level
☐ Plan VLAN allocation
☐ Design firewall rules
☐ Plan redundancy

Implementation Phase:
☐ Configure VLAN infrastructure
☐ Configure firewall zones
☐ Configure zone interfaces
☐ Configure inter-zone policies
☐ Configure access controls
☐ Configure logging

Testing Phase:
☐ Test intra-zone communication
☐ Test inter-zone communication
☐ Test denied communication
☐ Verify logging
☐ Performance testing
☐ Failover testing

Operations Phase:
☐ Monitor traffic patterns
☐ Review firewall logs
☐ Periodic rule review
☐ Update policies as needed
☐ Compliance verification
☐ Incident response
```
