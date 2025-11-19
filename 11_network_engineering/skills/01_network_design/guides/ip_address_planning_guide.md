# IP Address Planning Guide

## Introduction
This guide covers systematic IP address planning for optimal network design, delegation, and management.

## Step 1: Assess Available Space

### IPv4 Private Space

```
RFC 1918 allocations:

Class A (10.0.0.0/8):
  Total addresses: 16,777,216
  Usable subnets: 65,536 × /24 subnets
  Best for: Large enterprises, multi-region networks
  Recommendation: Enterprise default

Class B (172.16.0.0/12):
  Total addresses: 1,048,576
  Usable subnets: 4,096 × /24 subnets
  Best for: Medium enterprises, single region
  Recommendation: Limited deployment

Class C (192.168.0.0/16):
  Total addresses: 65,536
  Usable subnets: 256 × /24 subnets
  Best for: Small businesses, branch offices
  Recommendation: Avoid for enterprises (too small)
```

### Selection Process

```
Decision tree:

Network type: Campus or Enterprise?
  YES - Use Class A (10.0.0.0/8)
        (Plenty of space, industry standard)

Expectation: Single building < 1,000 users?
  YES - Use Class C (192.168.0.0/16)
        (Sufficient space, simple management)
  NO  - Use Class A (10.0.0.0/8)
        (Industry standard, future-proof)

Multi-region or multi-cloud?
  YES - Use Class A (10.0.0.0/8)
        (Supports global expansion)
  NO  - Use Class B (172.16.0.0/12)
        (Middle ground option)

Selected: 10.0.0.0/8 (enterprise standard)
```

## Step 2: Design Hierarchy

### Three-Level Hierarchy

```
Level 1: Region/Site (first 8 bits)
  10.0.0.0/8 ÷ into regions
  Region A: 10.0.0.0/10 (0-63)
  Region B: 10.64.0.0/10 (64-127)
  Region C: 10.128.0.0/10 (128-191)
  Region D: 10.192.0.0/10 (192-255)

Level 2: Building/Pod (next 8 bits)
  Region A: 10.0.0.0/10 ÷ into buildings
  Building A1: 10.0.0.0/16
  Building A2: 10.1.0.0/16
  Building A3: 10.2.0.0/16
  ...
  Building A63: 10.63.0.0/16

Level 3: Function/VLAN (last 8 bits)
  Building A1: 10.0.0.0/16 ÷ into functions
  Floor 1: 10.0.1.0/24 (Finance)
  Floor 2: 10.0.2.0/24 (Engineering)
  Floor 3: 10.0.3.0/24 (Operations)
  ...
  Services: 10.0.100.0/24 (Printers)
  Voice: 10.0.110.0/24 (VoIP)
  Guest: 10.0.200.0/24 (WiFi Guest)

Benefit: Hierarchical routing, easy subnetting, clear organization
```

## Step 3: Functional Area Allocation

### Campus Network Allocation

```
10.0.0.0/8 - Enterprise network

10.0.0.0/9 - Building A (HQ)
  10.0.0.0/16 - Building A East
    10.0.0.0/20 - Floor 1 User VLAN
      10.0.0.0/24 - Finance (10.0.0.1-254)
      10.0.1.0/24 - Sales (10.0.1.1-254)
      10.0.2.0/24 - HR (10.0.2.1-254)
    10.0.16.0/20 - Floor 2 User VLAN
      10.0.16.0/24 - Engineering
      10.0.17.0/24 - Operations
    10.0.32.0/20 - Services VLAN
      10.0.32.0/24 - Servers
      10.0.33.0/24 - Storage
      10.0.34.0/24 - Management
  10.0.64.0/16 - Building A West
    (Similar structure)

10.0.128.0/9 - Building B (Regional)
  10.0.128.0/16 - Building B
    (Similar structure)

10.64.0.0/9 - Building C (Remote)
10.128.0.0/9 - Data Center Primary
10.192.0.0/10 - Data Center Secondary/Reserved
```

### Data Center Allocation

```
10.128.0.0/16 - Data Center Primary

10.128.0.0/18 - Pod 1 (Customers A, B)
  10.128.0.0/20 - Customer A
    10.128.0.0/22 - VLAN 100 (Web tier)
    10.128.4.0/22 - VLAN 101 (App tier)
    10.128.8.0/22 - VLAN 102 (DB tier)
  10.128.16.0/20 - Customer B
    10.128.16.0/22 - VLAN 200 (Web tier)
    10.128.20.0/22 - VLAN 201 (App tier)
    10.128.24.0/22 - VLAN 202 (DB tier)

10.128.64.0/18 - Pod 2 (Customer C)
10.128.128.0/18 - Pod 3 (Shared Services)
  10.128.128.0/24 - NTP, DNS, DHCP
  10.128.129.0/24 - Management network
  10.128.130.0/24 - Backup network

10.129.0.0/16 - Data Center Secondary (Replication)
```

## Step 4: Sizing Individual Subnets

### Subnet Size Selection

```
User density formula:

Users needed = Current + Growth (% × years)

Example: Finance VLAN
  Current users: 50
  Growth: 20% annually
  Planning horizon: 3 years
  Needed: 50 × (1.2^3) = 50 × 1.728 = 86.4 ≈ 100 users

Add overhead:
  Users: 100
  Devices (PC, phone, printer): 150 total
  Reserved (5%): 7.5
  Broadcast/network/gateway: 4
  Target: 160 usable addresses

Subnet options:
  /25: 126 usable (TOO SMALL)
  /24: 254 usable (GOOD)
  /23: 510 usable (OVERSIZED but acceptable)

Selection: Use /24 (254 usable) for Finance VLAN
```

### Growth Accommodation

```
Common mistake: Size exactly for current need

Correct approach: Size for 3-5 year growth

VLAN 10 Finance: 50 users current
  Incorrect: 10.0.10.0/27 (30 usable, 10.0.10.1-30)
  Problem: Full in 1 year, requires renumbering
  Cost: High (migration, configuration change, user disruption)

Correct: 10.0.10.0/24 (254 usable, 10.0.10.1-254)
  Sufficient: 50 current, 200+ available
  Cost of change: Lower (years before needed)

Rule: Minimum /24 for any user VLAN
      /25 only for special services (printers, management)
      /26 and smaller only for point-to-point links

Justification: Cost of changing addresses >> cost of unused addresses
```

## Step 5: Special-Use Addresses

### Reserved Ranges

```
10.0.0.0/8 allocation:

Loopback addresses:
  10.255.0.0/16 - Device loopback IPs (never change)
  10.255.1.0/24 - Spines (10.255.1.1 - 10.255.1.254)
  10.255.2.0/24 - Leaves (10.255.2.1 - 10.255.2.254)
  10.255.3.0/24 - Campus core (10.255.3.1 - 10.255.3.3)

Management network:
  10.255.4.0/22 - Out-of-band management
  10.255.4.0/24 - Switch management IPs
  10.255.5.0/24 - Server IPMI/iLO IPs
  10.255.6.0/24 - Printer management IPs
  10.255.7.0/24 - Camera management IPs

Point-to-point links (/31):
  10.254.0.0/16 - WAN links
  10.254.0.0/31 - Link to Site-B router
  10.254.0.2/31 - Link to Site-C router
  10.254.0.4/31 - Link to ISP-A
  10.254.0.6/31 - Link to ISP-B

Benefits:
  - Loopbacks: Stable, BGP NEXT-HOP uses loopback
  - Management: Separate from user VLANs
  - P2P links: Efficient /31 usage (RFC 3021)
  - Reserved ranges: Clear, easy to understand
```

## Step 6: Documentation and Tracking

### IP Address Management (IPAM)

```
Spreadsheet template:

VLAN | Name | Subnet | Gateway | Usable | Current Use | Status | Owner
-----|------|--------|---------|--------|------------|--------|-------
10   | Exec | 10.0.10.0/24 | 10.0.10.1 | 1-254 | 40 | Active | CFO
20   | Fin  | 10.0.20.0/24 | 10.0.20.1 | 1-254 | 85 | Active | Controller
30   | Eng  | 10.0.30.0/24 | 10.0.30.1 | 1-254 | 120 | Active | CTO
40   | Ops  | 10.0.40.0/24 | 10.0.40.1 | 1-254 | 60 | Active | VP Ops
50   | Sales| 10.0.50.0/24 | 10.0.50.1 | 1-254 | 75 | Active | VP Sales
100  | Guest| 10.0.100.0/24 | 10.0.100.1 | 1-254 | 20 | Active | Network
110  | Voice| 10.0.110.0/24 | 10.0.110.1 | 1-254 | 85 | Active | PBX Admin

Manual tracking avoids:
- Accidental overlaps
- Loss of address space
- Confusion about ownership
- Difficulty planning growth
```

### Reserved/Future Planning

```
Document unallocated space:

10.0.0.0/8 - Total: 16,777,216 addresses
10.0.0.0/9 - Building A (allocated): 8,388,608
10.64.0.0/9 - Building B (allocated): 8,388,608
10.128.0.0/10 - DC Primary (allocated): 4,194,304
10.192.0.0/10 - Reserved for future: 4,194,304

Available for growth:
  - Campus expansion: Can add 10.64.0.0-10.127.255.255
  - Data center expansion: Can add within 10.128-10.191
  - WAN/cloud: Can add 10.192-10.255

5-year outlook:
  Current utilization: 16.8M / 16.7M = 100% allocated (but not all used)
  Actual IP usage: ~2M IPs (12% of available)
  Headroom: Excellent (plenty of space)
  Next review: Year 4 (reevaluate growth rate)
```

## Step 7: IPv6 Planning

### IPv6 Address Structure

```
Global Unicast Address allocation:

Request from RIR: 2001:db8::/48 (assuming documentation example)
  Provides: 65,536 /64 subnets (huge space)

Allocation strategy:

2001:db8:0::/48 - Campus network (16 bits available for subnets)
  2001:db8:0:1::/64 - Building A, Floor 1
  2001:db8:0:2::/64 - Building A, Floor 2
  2001:db8:0:3::/64 - Building A, Floor 3
  2001:db8:0:4::/64 - Building B, Floor 1
  ...
  2001:db8:0:100::/64 - Guest WiFi
  2001:db8:0:110::/64 - Voice VLAN
  2001:db8:0:200::/64 - Management

2001:db8:1::/48 - Data Center Primary
  2001:db8:1:1::/64 - Pod 1 Customer A
  2001:db8:1:2::/64 - Pod 1 Customer B
  ...

Benefits:
  - Massive address space (no scarcity)
  - Automatic host generation (EUI-64)
  - No subnet calculation needed
  - Hierarchical for easy routing
```

### Dual-Stack Configuration

```
Implement both IPv4 and IPv6:

Network interface:
  IPv4: 10.0.10.50
  IPv6: 2001:db8:0:1::50 (derived)
  Both active simultaneously
  Applications can use either

Advantages:
  - Future-proof (IPv6 ready)
  - No forced migration
  - Gradual transition possible
  - Supports IPv6-native applications

Timeline:
  Years 0-3: IPv4 primary, IPv6 parallel
  Years 3-5: IPv6 becoming primary for new services
  Year 5+: IPv4 secondary (but maintained)
  Year 10+: Potentially IPv4-free (if industry allows)
```

## Common Mistakes to Avoid

```
Mistake 1: Too-small subnets
  Problem: Requires renumbering in 1-2 years
  Solution: Minimum /24 for user VLANs
  Cost avoidance: Significant (hours to renumber, user disruption)

Mistake 2: Non-hierarchical design
  Problem: Routing summarization impossible, large routing tables
  Solution: Hierarchical allocation (site/building/function)
  Benefit: Efficient routing, easier troubleshooting

Mistake 3: No growth buffer
  Problem: Planning grows into allocated space, cascading changes
  Solution: Allocate 30-50% buffer for growth
  Cost: Small (unused IP space) vs. Large (renumbering)

Mistake 4: Mixing public and private
  Problem: Confusing, difficult to secure, hard to expand
  Solution: Use RFC 1918 consistently, NAT at edges
  Benefit: Clear separation, easier to manage

Mistake 5: Poor documentation
  Problem: Loss of address space, accidental overlaps, confusion
  Solution: Central IPAM system, clear ownership
  Cost: Worth it (prevents costly mistakes)
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Intermediate
**Standards:** RFC 1918, RFC 3021, RFC 3986
