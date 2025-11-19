# VLAN Strategy Guide

## Introduction
This guide covers developing comprehensive VLAN strategies that balance usability, performance, and security.

## Step 1: Determine VLAN Strategy

### Strategy Options

```
Option 1: Department-based VLANs

Structure:
  VLAN 10 - Finance
  VLAN 20 - Engineering
  VLAN 30 - Operations
  VLAN 40 - Sales
  VLAN 50 - Executive

Pros:
  - Easy to understand (maps to org)
  - Easy to implement
  - Natural alignment with policies
  - Simple ACLs (block certain departments)

Cons:
  - Difficult to change when org restructures
  - Multiple departments in same VLAN complex
  - Inter-department traffic requires routing

Best for: Stable organization structure

Example: Traditional enterprise with fixed departments


Option 2: Location-based VLANs

Structure:
  VLAN 110 - Building A, Floor 1
  VLAN 111 - Building A, Floor 2
  VLAN 120 - Building B, Floor 1
  VLAN 121 - Building B, Floor 2

Pros:
  - Aligns with network topology
  - Easy to manage per-location
  - Accommodates multiple departments per location
  - Flexible for reorganization

Cons:
  - Less semantic meaning
  - Department policies harder to enforce
  - More complex ACLs needed

Best for: Multi-building, multi-tenant environments


Option 3: Function-based VLANs

Structure:
  VLAN 10-19 - User access (by tier/priority)
  VLAN 20-29 - Storage/servers
  VLAN 30-39 - Management/monitoring
  VLAN 40-49 - IoT/sensors
  VLAN 50-59 - Wireless
  VLAN 60-69 - Voice/VoIP
  VLAN 70-79 - Guest

Pros:
  - Very flexible
  - Clear function separation
  - Scales easily
  - Policies easy to implement per function

Cons:
  - Most complex to understand
  - Harder to initially map devices
  - Requires clear classification

Best for: Large, complex organizations
         Cloud-native, modern deployments

Recommendation: Hybrid approach (combining multiple strategies)
  - User access: Department-based (VLANs 10-50)
  - Services: Function-based (VLANs 100+)
  - Management: Separate (VLANs 200+)
```

## Step 2: VLAN Design for Campus

### User Access VLANs

```
Core VLANs:

VLAN 10 - Executive/Admin
  Subnet: 10.0.10.0/24
  Gateway: 10.0.10.1
  Users: 50
  Access: HQ buildings only
  Policy: Higher priority, enhanced security

VLAN 20 - Finance/Accounting
  Subnet: 10.0.20.0/24
  Gateway: 10.0.20.1
  Users: 85
  Access: All Finance dept locations
  Policy: Access to finance servers, SEC compliance

VLAN 30 - Engineering
  Subnet: 10.0.30.0/24
  Gateway: 10.0.30.1
  Users: 120
  Access: All Engineering offices
  Policy: Access to engineering resources

VLAN 40 - Sales
  Subnet: 10.0.40.0/24
  Gateway: 10.0.40.1
  Users: 75
  Access: All Sales locations
  Policy: Access to CRM, customer data

VLAN 50 - Operations
  Subnet: 10.0.50.0/24
  Gateway: 10.0.50.1
  Users: 95
  Access: Operations centers
  Policy: Access to operational data
```

### Service VLANs

```
VLAN 100 - Guest WiFi
  Subnet: 10.0.100.0/24
  Gateway: 10.0.100.1
  Purpose: Guest internet access
  Isolation: Complete (no internal access)
  Rate limit: 25 Mbps per user
  Features: Portal authentication, logging

VLAN 110 - Voice/VoIP
  Subnet: 10.0.110.0/24
  Gateway: 10.0.110.1
  Purpose: IP phones
  QoS: High priority (PCP 5)
  Bandwidth: Reserved 30 Mbps
  VLAN tagging: Native VLAN on phone ports

VLAN 120 - Printers
  Subnet: 10.0.120.0/24
  Gateway: 10.0.120.1
  Purpose: Network printers
  Access: All users (VLAN routing)
  Management: Print server on this VLAN
  IP pool: DHCP 10.0.120.100-200 (static for printers)

VLAN 200 - Management
  Subnet: 10.0.200.0/24
  Gateway: 10.0.200.1
  Purpose: Network device management
  Access: Network team only (restricted)
  Authentication: SSH/HTTPS only
  Logging: Audit trail of all changes

VLAN 210 - Server/Storage
  Subnet: 10.0.210.0/24
  Gateway: 10.0.210.1
  Purpose: Internal servers
  Access: Restricted (ACL enforced)
  Performance: Jumbo frames (MTU 9000)
  Backup: Separate VLAN 211 for backup traffic
```

## Step 3: VLAN Allocation Rules

### Port Assignment Logic

```
Port Gi0/0/1:
  Device type: Desktop PC
  Assignment: VLAN 20 (Finance, based on location)
  Configuration: Access mode, VLAN 20
  Port security: Max 2 MAC addresses

Port Gi0/0/2:
  Device type: IP Phone
  Assignment: VLAN 110 (Voice)
  Configuration: Access mode, VLAN 110
  Voice VLAN: 110
  Port security: Specific phone MAC

Port Gi0/0/3:
  Device type: Printer
  Assignment: VLAN 120 (Printers)
  Configuration: Access mode, VLAN 120
  Port security: Printer MAC

Port Gi0/0/4:
  Device type: WiFi AP
  Assignment: VLANs 10,20,30,40,50,100,110 (trunk)
  Configuration: Trunk mode
  Native VLAN: 100 (Guest)
  Allowed VLANs: List above
  Port security: N/A (AP connects via EtherChannel usually)

Port Gi0/0/48:
  Device type: Uplink to Distribution
  Assignment: All VLANs
  Configuration: Trunk mode
  Native VLAN: 1
  Allowed VLANs: All active
  Port security: N/A
```

### VLAN Membership Automation

```
Option 1: Manual assignment
  - Network admin assigns VLAN per port
  - Works: Small networks (<100 switches)
  - Scalability: Poor (time-consuming)

Option 2: Location-based (port template)
  - Switch assigned to location (Building A, Floor 1)
  - All ports default to Building A VLAN
  - User can override (place phone in VLAN 110)

Option 3: 802.1X (dynamic VLAN assignment)
  - Switch: User must authenticate
  - User credentials: Mapped to VLAN
  - VLAN: Assigned on authentication
  - Complexity: High
  - Benefit: Maximum security, full automation

Recommended: Hybrid
  - Default: Location-based VLAN (user access)
  - Special devices: Static VLAN (phones, printers)
  - Guests: Guest VLAN access
  - High-security: 802.1X if available
```

## Step 4: Broadcast Domain Management

### VLAN Isolation

```
Problem: Broadcast traffic flooding network

Solution: VLAN isolation

Each VLAN = separate broadcast domain
Broadcast frames: Do not cross VLAN boundaries
Multi-cast: Controlled per VLAN

Configuration:
  Spanning Tree: Per-VLAN (PVST+)
    Each VLAN has independent STP
    Root bridge: Different per VLAN (load balance)

  VLAN 10: Root on Dist-A (priority 24576)
  VLAN 20: Root on Dist-B (priority 24576)
  VLAN 30: Root on Dist-A
  VLAN 40: Root on Dist-B
  (Alternate load across distribution pair)

Benefits:
  - Broadcast limited to VLAN
  - No network-wide broadcast storm possible
  - No single broadcast causing outage
```

### VLAN Sizing for Broadcast

```
ARP broadcast example:

VLAN 20 (Finance) - 254 usable IPs
  Devices: 85 actual + 50 reserved = 135 devices
  Broadcast utilization: ~135 / 254 = 53% (acceptable)

If undersized:
  VLAN 20 - 10.0.20.0/25 (126 usable) = 85 / 126 = 67% (high)
  Problem: Broadcast domain smaller, broadcast overhead higher
  Solution: Use /24 minimum (50% broadcast overhead acceptable)

Never use /26 or smaller for user VLANs
  - Broadcast storms from ARP
  - DHCP inefficient
  - Limited growth room
  - Poor scalability
```

## Step 5: Inter-VLAN Routing

### Routing Configuration

```
Scenario: Finance user (VLAN 20) accessing server (VLAN 210)

VLAN 20: 10.0.20.0/24 (Finance users)
VLAN 210: 10.0.210.0/24 (Servers)

Routing setup (on Distribution switch):

interface Vlan 20
  ip address 10.0.20.1 255.255.255.0
  description Finance Users

interface Vlan 210
  ip address 10.0.210.1 255.255.255.0
  description Internal Servers

ip routing (enable routing globally)

Traffic flow:
  Finance PC: Destination IP 10.0.210.50 (server)
  PC sends to gateway: 10.0.20.1 (distribution)
  Distribution looks up: 10.0.210.0/24 → VLAN 210 interface
  Distribution forwards: Out VLAN 210 interface
  Server receives: From VLAN 210 subnet
  Server responds: To Finance PC via VLAN 20
```

### Access Control Lists

```
ACL for VLAN restrictions:

Allow Finance access to Finance servers only:

ip access-list extended FINANCE_ACCESS
  permit ip 10.0.20.0 0.0.0.255 10.0.210.0 0.0.0.255
  permit ip 10.0.20.0 0.0.0.255 10.0.120.0 0.0.0.255
  deny ip 10.0.20.0 0.0.0.255 10.0.10.0 0.0.0.255
  deny ip 10.0.20.0 0.0.0.255 10.0.30.0 0.0.0.255
  permit ip any any (allow to internet)

interface Vlan 20
  ip access-group FINANCE_ACCESS in

Result: Finance users can:
  - Access finance servers (permitted)
  - Access printers (permitted)
  - Cannot access executive (denied)
  - Cannot access engineering (denied)
  - Can access internet (permitted by default)
```

## Step 6: VLAN Trunking

### Trunk Configuration

```
Between Access and Distribution:

Access-A1 ←→ Distribution-A (trunk link)

Port-channel configuration (active-active):

interface Port-channel 1
  switchport mode trunk
  switchport trunk allowed vlan 10,20,30,40,50,100,110,120
  switchport trunk native vlan 1
  no shut

interface Gi0/0/47
  channel-group 1 mode active
  no shut

interface Gi0/0/48
  channel-group 1 mode active
  no shut

Result:
  - All specified VLANs pass through trunk
  - All frames tagged (except native)
  - Native VLAN (1): Untagged (for management)
  - Load balance: Flows distributed across members

Best practice:
  - List only needed VLANs (security)
  - Never allow all VLANs (10-4094)
  - Document trunk members
  - Test trunk on spare ports before deployment
```

## Step 7: Special Scenarios

### Multiple Departments Per Floor

```
Building A, Floor 1:
  Finance and Engineering teams collocated

Option 1: Both in same VLAN
  VLAN 10: Finance + Engineering
  Problem: Broadcast domain mixed, policies hard to enforce
  Not recommended

Option 2: Separate VLANs per department
  Finance ports: VLAN 20 (Finance VLAN)
  Engineering ports: VLAN 30 (Engineering VLAN)
  Routing: Inter-VLAN routing enables communication
  Benefit: Policies per VLAN, traffic isolated, easy to enforce
  Recommended

Configuration:
  Port Gi0/0/1-6: VLAN 20 (Finance)
  Port Gi0/0/7-12: VLAN 30 (Engineering)
  Port Gi0/0/13-24: Mix (based on team)
  Uplinks: Gi0/0/47-48 (trunk to distribution)
```

### Guest Network with Internet Access

```
VLAN 100 - Guest WiFi

Requirements:
  - Internet access only
  - No internal resource access
  - No inter-guest communication (optional)
  - Limited bandwidth

Configuration:

interface Vlan 100
  ip address 10.0.100.1 255.255.255.0
  ip helper-address 10.0.200.10 (DHCP server)

ip access-list extended GUEST_ALLOW
  permit tcp 10.0.100.0 0.0.0.255 any eq 80
  permit tcp 10.0.100.0 0.0.0.255 any eq 443
  permit tcp 10.0.100.0 0.0.0.255 any eq 53
  permit udp 10.0.100.0 0.0.0.255 any eq 53
  deny ip 10.0.100.0 0.0.0.255 10.0.0.0 0.0.255.255
  permit ip any any

interface Vlan 100
  ip access-group GUEST_ALLOW out

Result:
  - Guest DHCP: 10.0.100.100-200
  - Guest internet: Available
  - Guest to internal: Blocked by ACL
  - Internet to guest: Blocked by firewall (return traffic only)
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Intermediate
**Technologies:** IEEE 802.1Q, HSRP, VRRP, Spanning Tree
