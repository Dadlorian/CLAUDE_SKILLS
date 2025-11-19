# Network Segmentation Guide

## Planning Phase

### 1. Current State Assessment

```
Information Gathering:
- Network diagram (current)
- IP addressing scheme
- VLAN configuration (if exists)
- Traffic flows
- Critical systems
- Data classification
- Compliance requirements
- Security incident history

Documentation:
- Systems per network
- Data flows between systems
- User populations
- Applications and ports
- Dependencies
- Criticality levels
```

### 2. Security Zone Definition

```
Define Zones:
1. Identify business domains
   - Finance
   - Healthcare
   - HR
   - Operations
   - Customer-facing

2. Identify security levels
   - Public (Internet-facing)
   - Trusted (Employee)
   - Internal (Backend systems)
   - Restricted (Sensitive data)

3. Map systems to zones
   - Web servers → DMZ
   - Databases → Restricted
   - Workstations → Trusted
   - DNS/DHCP → Management

4. Define inter-zone communication
   - Explicit allow lists
   - Document business justification
   - Minimize connections
```

### 3. VLAN Planning

```
VLAN Numbering Scheme:

User VLANs (10-49):
- 10: Office Users (10.1.10.0/24)
- 11: Remote Users (10.1.11.0/24)
- 12: Guest/Contractors (10.1.12.0/24)

Server VLANs (50-99):
- 50: Web Servers (10.1.50.0/24)
- 51: Application Servers (10.1.51.0/24)
- 52: Database Servers (10.1.52.0/24)
- 53: Storage/Backup (10.1.53.0/24)

Management VLANs (100-149):
- 100: Switch/Router Mgmt (10.1.100.0/24)
- 101: Firewall Mgmt (10.1.101.0/24)
- 102: Monitoring (10.1.102.0/24)

Restricted VLANs (150-199):
- 150: PCI Systems (10.1.150.0/24)
- 151: PHI Systems (10.1.151.0/24)
- 152: Financial Systems (10.1.152.0/24)
```

## Switch Configuration

### Basic VLAN Setup

```
Create VLANs:
vlan 10
 name OFFICE_USERS
 description Office Users 10.1.10.0/24

vlan 50
 name WEB_SERVERS
 description Web Servers 10.1.50.0/24

vlan 100
 name MANAGEMENT
 description Management Network 10.1.100.0/24

Assign Ports to VLANs:
interface FastEthernet0/1
 description Office User Port
 switchport mode access
 switchport access vlan 10

interface FastEthernet0/25
 description Web Server Port
 switchport mode access
 switchport access vlan 50

Create Trunk for Core:
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,50,100
 switchport nonegotiate
 description Trunk to Core Switch

Assign Management Interface:
interface Vlan100
 ip address 10.1.100.2 255.255.255.0
 description Management Interface
```

### Advanced Features

#### VLAN Security

```
Port Security:
interface FastEthernet0/1
 switchport port-security
 switchport port-security mac-address sticky
 switchport port-security maximum 1
 switchport port-security violation shutdown

BPDU Guard (prevent spanning tree attacks):
interface FastEthernet0/1
 spanning-tree bpduguard enable

DHCP Snooping:
ip dhcp snooping
ip dhcp snooping vlan 10,50,100
interface FastEthernet0/1
 ip dhcp snooping trust

Dynamic ARP Inspection:
ip arp inspection vlan 10,50,100
interface GigabitEthernet0/1
 ip arp inspection trust
```

## Firewall Configuration

### Inter-VLAN Routing and Filtering

```
Create Zones:

Zone USERS:
 - VLAN 10, 11, 12
 - Security level: 50

Zone SERVERS:
 - VLAN 50, 51, 53
 - Security level: 70

Zone RESTRICTED:
 - VLAN 150, 151, 152
 - Security level: 90

Zone MANAGEMENT:
 - VLAN 100, 101, 102
 - Security level: 80

Create Interfaces:
interface Vlan10
 nameif users
 security-level 50
 ip address 10.1.10.1 255.255.255.0

interface Vlan50
 nameif servers
 security-level 70
 ip address 10.1.50.1 255.255.255.0

interface Vlan150
 nameif restricted
 security-level 90
 ip address 10.1.150.1 255.255.255.0
```

### Access Control Lists

```
Users to Web Servers:
access-list USERS_TO_WEB extended permit tcp
 object-group network OFFICE_USERS
 object-group network WEB_SERVERS
 object-group service WEB_SERVICES

Web Servers to Database:
access-list WEB_TO_DB extended permit tcp
 object-group network WEB_SERVERS
 10.1.52.5
 eq 3306

Deny Restricted Access:
access-list ANY_TO_RESTRICTED extended deny ip any
 object-group network RESTRICTED_SYSTEMS
 log

Management Access:
access-list MGMT_ACCESS extended permit tcp
 any
 object-group network MGMT_SERVERS
 eq 22
 ! Requires VPN

Apply Rules:
access-group USERS_TO_WEB in interface users
access-group WEB_TO_DB in interface servers
access-group ANY_TO_RESTRICTED in interface restricted
access-group MGMT_ACCESS in interface users
```

## Microsegmentation Implementation

### Host-Based Approach

```
Windows Firewall Configuration:

Inbound Rules (Group Policy):
- Allow RDP only from management subnet
- Allow NTP from specified servers
- Allow DNS from specified servers
- Block all others by default

Example PowerShell Rule:
New-NetFirewallRule -DisplayName "Allow SQL from App Servers" `
  -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 1433 `
  -RemoteAddress "10.1.51.0/24"

Linux Host-Based Firewall (iptables/ufw):

Default deny all:
ufw default deny incoming
ufw default allow outgoing

Allow specific:
ufw allow from 10.1.51.0/24 to any port 3306 proto tcp

Allow SSH (management):
ufw allow from 10.1.100.0/24 to any port 22
```

## Migration Strategy

### Phase 1: Planning & Lab Testing (Week 1-2)

```
Activities:
- Finalize network design
- Create test topology
- Validate firewall rules
- Test connectivity flows
- Verify performance
- Prepare rollback plan

Deliverables:
- Validated configuration
- Test report
- Rollback procedure
- Communication plan
```

### Phase 2: Pilot Implementation (Week 3-4)

```
Scope: Small non-critical segment

Activities:
- Implement test VLAN
- Configure test servers
- Apply firewall rules
- Monitor for issues
- Gather feedback
- Document issues

Success Criteria:
- No production impact
- Proper segmentation
- All traffic flows work
- Performance acceptable
```

### Phase 3: Phased Rollout (Week 5-12)

```
Phase 3A (Week 5-6): User VLANs
- Implement VLAN 10, 11, 12
- Migrate user groups
- Test access to services
- Validate no disruption

Phase 3B (Week 7-8): Server VLANs
- Implement VLAN 50-53
- Migrate servers
- Update firewall rules
- Validate connections

Phase 3C (Week 9-10): Management
- Implement VLAN 100-102
- Migrate management systems
- Restrict access
- Verify monitoring

Phase 3D (Week 11-12): Restricted
- Implement VLAN 150-152
- Highest security controls
- Multi-factor auth
- Audit logging
```

### Phase 4: Optimization (Week 13+)

```
Activities:
- Monitor performance
- Review firewall logs
- Tune rules
- Remove workarounds
- Document final state
- Provide training
- Ongoing maintenance
```

## Validation and Testing

### Connectivity Tests

```
Test All Inter-Zone Traffic:

Users ↔ Web Servers:
- Windows user ping web server
- Windows user RDP to web server
- Web services accessible

Web Servers ↔ Database:
- telnet web_server_ip 3306
- Query database from web server
- Connection logged

Users ↔ Management:
- SSH to management server
- Should require VPN first
- Failed direct attempts logged
```

### Rule Verification

```
Validate Rules:

Test Denied Traffic:
- User to database: DENIED (logged)
- User to restricted: DENIED (logged)
- Server to user: DENIED (logged)

Test Allowed Traffic:
- User to web: ALLOWED
- Web to database: ALLOWED (specific port)
- Admin to all: ALLOWED (authenticated)

Validate Logging:
- Check firewall logs
- Verify denied traffic captured
- Verify allowed traffic pattern
- Monitor for false positives
```

## Ongoing Management

### Monitoring and Maintenance

```
Daily:
- Monitor firewall logs
- Check for alerts
- Verify tunnel/connectivity status

Weekly:
- Review denied traffic trends
- Identify new communication patterns
- Assess rule effectiveness

Monthly:
- Full firewall log review
- Rule usage analysis
- Permission audit
- Update threat intelligence

Quarterly:
- Comprehensive review
- New systems assessment
- Rule cleanup
- Performance review

Annually:
- Full security audit
- Compliance verification
- Capacity planning
- Update architecture
```

### Documentation

```
Keep Updated:
- Network diagram (quarterly)
- VLAN assignment (current)
- Firewall rules (with change tracking)
- Security policies (as updated)
- Access control matrix (user changes)
- Incident history (security events)
- Change log (all modifications)
```

## Common Challenges and Solutions

### Challenge 1: Overly Restrictive Rules

```
Problem: Legitimate traffic blocked

Solution:
1. Review firewall logs
2. Identify legitimate traffic
3. Create exception rules
4. Test thoroughly
5. Document justification
6. Set review date for rule

Prevention:
- Involve app owners in planning
- Test before deploying
- Leave monitoring window
- Plan for exceptions
```

### Challenge 2: Performance Degradation

```
Problem: Segmentation causes latency

Causes:
- Firewall bottleneck
- MTU issues
- QoS not configured

Solutions:
1. Check firewall CPU/memory
2. Optimize rule order
3. Enable hardware acceleration
4. Verify MTU (1500 bytes default)
5. Configure QoS
6. Upgrade if needed
```

### Challenge 3: User Access Issues

```
Problem: Users cannot access needed services

Solutions:
1. Verify segmentation design
2. Check firewall rules
3. Test connectivity
4. Review application requirements
5. Create necessary exceptions
6. Document justification
7. Update access control matrix

Prevention:
- Involve users in planning
- Identify all applications first
- Allow time for adjustments
- Provide communication/training
```
