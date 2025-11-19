# Campus Network Design Guide

## Introduction
This guide walks you through designing a production-grade campus network from requirements through implementation. It covers the end-to-end process with real-world examples.

## Phase 1: Assessment and Requirements

### Business Requirements Gathering

Start with understanding the organization's needs:

```
Interview Questions:

1. Current State
   - How many buildings do you have?
   - How many users per building?
   - What's your growth projection (3-5 years)?
   - Current network problems?

2. Applications
   - What critical applications run?
   - Are you moving to cloud?
   - Do you need VoIP?
   - Any special protocols (trading, video)?

3. Availability
   - What's your acceptable downtime?
   - How many 9s do you need (99.9%)?
   - Do you need active redundancy?

4. Security
   - Any compliance requirements (HIPAA, PCI)?
   - Do you need network segmentation?
   - WiFi included?

5. Budget and Timeline
   - Hardware budget?
   - Installation budget?
   - Timeline for deployment?
   - Phased vs. all-at-once?
```

### Network Assessment

Understand the current state:

```bash
# Collect baseline data

Device inventory:
  - Count desktops/laptops per building
  - Count IP phones
  - Count printers
  - Count wireless APs
  - Count servers
  - Count IoT devices

Traffic analysis:
  - Enable NetFlow on core switches
  - Capture 1 week of data
  - Identify peak hours
  - Identify application breakdown

Infrastructure audit:
  - Walk each building
  - Document cable runs
  - Note any physical constraints
  - Take photos of current equipment
  - Check power availability
```

## Phase 2: Design Architecture

### Determine Tier Model

For most organizations, use the three-tier model:

```
Decision Tree:

Small office (< 50 users)?
  YES → Collapsed 2-tier (Access + Core combined)
  NO  → Continue

Medium campus (50-1000 users)?
  YES → Standard 3-tier
  NO  → Continue

Large enterprise (> 1000 users)?
  YES → 3-tier with multiple distribution pairs
  NO  → Continue

Multi-campus?
  YES → Distributed 3-tier with WAN
  NO  → Single location 3-tier
```

### Access Layer Design Process

Step 1: Count total devices

```
User count: 500
Avg devices per user: 2.5 (laptop, phone, iPad)
+ Printers: 40
+ Servers/appliances: 10
+ IoT/sensors: 50
+ Spare ports (20%): 250

Total port requirement: ~1,540 ports
```

Step 2: Select switch model

```
Catalyst 9200L: 48 ports per switch
Switches needed: 1,540 / 48 = 32 switches

Allocation by building:
  Building A (200 users): 12 switches
  Building B (150 users): 9 switches
  Building C (100 users): 6 switches
  Building D (50 users): 3 switches
  Total: 32 switches
```

Step 3: Plan placement and redundancy

```
Building A Layout:
  Floor 1: Access-A1, Access-A2 (dual for redundancy)
  Floor 2: Access-A3, Access-A4
  Floor 3: Access-A5, Access-A6

  Each pair connects via EtherChannel to Distribution-A
  Backup path: Distribution-B (automatic failover via STP)
```

Step 4: Configure uplinks

```
Access switch uplink configuration:

Switch: Access-A1
  Interface Po1 (Port-Channel 1)
    Member 1: Gi0/0/47
    Member 2: Gi0/0/48
    Mode: Trunk
    Allowed VLANs: 10,20,30,40,50,100,110,120

  Spanning Tree:
    Portfast: Enabled on access ports
    BPDU Guard: Enabled
    Root bridge: Distribution-A (priority 24576)
```

### Distribution Layer Design

Step 1: Determine pair count

```
Rule: One distribution pair per building or per 8-10 access switches

Building A (12 access switches):
  Distribution-A and Distribution-B (one pair)

Building B (9 access switches):
  Distribution-B and Distribution-C (one pair for each building)

OR combine if same location:
  Distribution pair serves multiple buildings
```

Step 2: Select platform

```
Requirements:
  - 48+ 10G/25G uplink ports
  - Throughput: >10 Tbps
  - Redundancy: Dual supervisors required
  - VLAN support: 4,000+

Recommended: Catalyst 9500 or Catalyst 9300
  9500: Large campuses (>500 users)
  9300: Medium campuses (200-500 users)
```

Step 3: Design gateway redundancy

```
HSRP Configuration for Building A:

VLAN 10 - Finance (10.10.10.0/24):
  Distribution-A (primary): 10.10.10.2 (HSRP priority 150)
  Distribution-B (backup): 10.10.10.3 (HSRP priority 100)
  Virtual gateway: 10.10.10.1

VLAN 20 - Engineering (10.10.20.0/24):
  Distribution-A (backup): 10.10.20.2 (HSRP priority 100)
  Distribution-B (primary): 10.10.20.3 (HSRP priority 150)
  Virtual gateway: 10.10.20.1

Load balancing:
  - 50% of VLANs active on Distribution-A
  - 50% of VLANs active on Distribution-B
  - Both handle failover traffic if one fails
```

### Core Layer Design

For most campuses, use collapsed core (distribution switches provide core function):

```
Exception cases (need dedicated core):
  - > 5,000 users
  - > 100 Mbps sustained inter-building traffic
  - > 10 VLANs with heavy cross-VLAN traffic
  - 24/7 uptime criticality

For dedicated core:
  Topology: 2x core switches, full mesh to distribution
  Platform: Catalyst 9500 or Nexus 9300
  Link speeds: 100G minimum
  Redundancy: Dual supervisors, N+1 fabric
```

## Phase 3: IP and VLAN Design

### VLAN Design

Determine VLAN strategy:

```
Option 1: Department-based (simple, typical)
  VLAN 10 - Finance
  VLAN 20 - Engineering
  VLAN 30 - Operations
  VLAN 40 - Sales
  VLAN 50 - Executive
  VLAN 100 - Guest WiFi
  VLAN 110 - Voice
  VLAN 120 - Printers

  Pros: Easy to understand, matches org structure
  Cons: Difficult to change if org reorganizes

Option 2: Building-based
  VLAN 100-110: Building A
  VLAN 200-210: Building B
  VLAN 300-310: Building C

  Pros: Scales better for multi-building
  Cons: Less semantic meaning

Option 3: Functional (advanced)
  VLAN 10-19: User access (by priority)
  VLAN 20-29: Storage/servers
  VLAN 30-39: Management
  VLAN 40-49: IoT/devices
  VLAN 50-59: Wireless

  Pros: Flexible, allows policy per function
  Cons: Most complex to manage
```

### IP Address Design

Hierarchical approach:

```
10.0.0.0/8 - Campus network

10.10.0.0/16 - Building A
  10.10.1.0/24 - Floor 1
  10.10.2.0/24 - Floor 2
  10.10.3.0/24 - Floor 3

10.20.0.0/16 - Building B
  10.20.1.0/24 - Floor 1
  10.20.2.0/24 - Floor 2
  10.20.3.0/24 - Floor 3

Department within building (alternate):
  10.10.10.0/24 - Finance (10.10.x where x=department)
  10.10.20.0/24 - Engineering
  10.10.30.0/24 - Operations

Special VLANs:
  10.10.100.0/24 - Guest WiFi
  10.10.110.0/24 - Voice
  10.10.120.0/24 - Printers
  10.10.200.0/24 - Management
```

## Phase 4: Redundancy Planning

### Link Redundancy

```
Topology:

    Distribution-A    Distribution-B
      /    \            /    \
     /      \          /      \
  Access-1  Access-2  Access-3  Access-4

Link redundancy:
  - Access-1 primary → Distribution-A
  - Access-1 backup → Distribution-B
  - All access switches have dual uplinks
  - STP blocks backup path until primary fails

Failover time: 30-50 seconds (STP reconvergence)
```

### Gateway Redundancy

```
HSRP Design:

For all user VLANs:
  - Dual HSRP instance on distribution pair
  - One acts as active (primary)
  - One acts as standby (backup)
  - Automatic failover on primary failure
  - Failover time: <3 seconds
```

## Phase 5: Security Design

### Network Segmentation

```
Recommended VLANs:

Guest: VLAN 100
  - Cannot access internal resources
  - Direct internet gateway
  - Limited to 25 Mbps per user

Management: VLAN 200
  - Restricted access (only network team)
  - SSH/HTTPS only
  - Logging enabled

Voice: VLAN 110
  - QoS priority high
  - Separate from data
  - Call admission control

Production: VLANs 10-50
  - Standard user access
  - Policy-based routing optional

Lab/Test: VLAN 180
  - Isolated from production
  - Can have experimental configs
```

### Access Control

```
ACL Strategy:

Allow traffic:
  - Within same VLAN (switched locally)
  - From user VLANs to servers (routing decision)
  - From user VLANs to internet (firewall)

Block traffic:
  - Guest VLAN to internal VLANs
  - Intra-VLAN except same department (if needed)
  - Management VLAN to user VLANs
```

## Phase 6: Implementation

### Pilot Phase (Recommended)

Start with one building or site:

```
Week 1-2: Install physical equipment
  - Rack distribution switches
  - Install access switches in building
  - Run uplinks (fiber preferred)
  - Verify physical connectivity

Week 3-4: Configure and test
  - Configure all device base configs
  - Enable routing and VLAN trunking
  - Test end-user connectivity
  - Verify gateway redundancy
  - Load test critical paths

Week 5-6: User migration and cutover
  - Migrate test users first
  - Monitor for issues (have rollback plan)
  - Gradually migrate production users
  - Verify application access
  - Conduct user training
```

### Rollout Phase

Repeat pilot process for remaining buildings:

```
Timeline:
  Building A: Pilot (6 weeks)
  Building B: Week 7-12 (production rollout)
  Building C: Week 13-18
  Building D: Week 19-24

Parallel operation:
  - Run both old and new network during transition
  - Dual routing to same destinations
  - Gradual user cutover
  - Minimize service disruption
```

## Configuration Examples

### Access Switch

```
Switch: Access-A1
Hostname: Access-A1

vlan 1-20
 name User_VLANs
!

interface Gi0/0/1
 description Desktop PC
 switchport mode access
 switchport access vlan 10
 switchport port-security
 !

interface Gi0/0/24
 description Wireless AP Floor 1
 switchport mode access
 switchport access vlan 100
 power inline auto
 !

interface Port-channel 1
 description Uplink to Distribution
 switchport mode trunk
 switchport trunk allowed vlan 1-50,100,110,120
 !

interface Gi0/0/47
 channel-group 1 mode active
 !

interface Gi0/0/48
 channel-group 1 mode active
 !
```

### Distribution Switch

```
Switch: Distribution-A
Hostname: Distribution-A

vlan 10,20,30,40,50,100,110,120,200

interface Vlan 10
 ip address 10.10.10.2 255.255.255.0
 standby 10 ip 10.10.10.1
 standby 10 priority 150
 standby 10 preempt
 !

interface Port-channel 1
 description To Core Switches
 switchport mode trunk
 !

ip routing
```

## Validation and Testing

### Pre-implementation Testing

```
Checklist:
  [ ] All interfaces up and negotiated correctly
  [ ] Spanning tree converged (no loops)
  [ ] VLANs passing traffic (vlan test)
  [ ] Gateway redundancy tested (unplug primary)
  [ ] Uplink failover tested
  [ ] DNS resolution working
  [ ] DHCP scope configured and working
  [ ] NTP synchronized on devices
  [ ] Syslog configured and working
  [ ] SNMP configured for monitoring
```

### User Acceptance Testing

```
Test Plan:
  [ ] User can connect to network (WiFi and wired)
  [ ] User can access file servers
  [ ] User can access cloud apps (O365, Salesforce)
  [ ] User can access internet
  [ ] IP phones working (if applicable)
  [ ] Video conferencing working
  [ ] Bandwidth adequate for large file transfers
  [ ] Guest WiFi isolated
  [ ] VPN working (if applicable)
```

## Troubleshooting Common Issues

### Users can't connect

```
Check list:
  1. Is access port up? (show int status)
  2. Is correct VLAN assigned? (show port security)
  3. Is switch port-security enabled? (might be max MAC reached)
  4. Is VLAN routing enabled? (check distribution switch)
  5. Is gateway reachable? (ping from switch)
  6. Is DHCP working? (check DHCP logs)
```

### Slow network speed

```
Check list:
  1. Check link speed (should be full speed, no half-duplex)
  2. Check interface utilization (show int stats)
  3. Check for errors/collisions (show int errors)
  4. Check for packet loss (ping remote device)
  5. Check spanning tree (might have suboptimal path)
  6. Check for duplex mismatch (1G/1G or 10G/10G)
  7. Check for misconfigured QoS
```

## Ongoing Operations

### Daily Monitoring

```
Checklist:
  - Check device health (memory, CPU)
  - Verify no critical alarms
  - Check for interface errors
  - Verify backup completion
```

### Weekly Tasks

```
- Review capacity trending
- Check for unusual traffic patterns
- Verify all failover links operational
- Review syslog for warnings
```

### Monthly Tasks

```
- Capacity review meeting
- Review growth trending
- Plan for next upgrade phase
- Update documentation
```

### Quarterly Tasks

```
- Test failover procedures
- Update network diagrams
- Review security policies
- Plan major maintenance windows
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Intermediate to Advanced
