# Legacy Protocol Modernization

## Executive Summary

This document provides comprehensive strategies for replacing legacy routing and network protocols with modern, scalable alternatives. It covers migration from RIPv1/RIPv2, IGRP, ISIS, and proprietary protocols to standards-based solutions like OSPF, BGP, and segment routing.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: RFC 2453 (RIP), RFC 2328 (OSPF), RFC 4271 (BGP), RFC 7426 (ISIS)

---

## 1. Legacy Protocol Analysis

### 1.1 RIPv1 Assessment

**RIPv1 Characteristics**:
- Maximum hop count: 15 (limits network size)
- Update interval: 30 seconds (slow convergence)
- Classful routing (no VLSM support)
- No authentication mechanism
- High bandwidth usage (full routing table sent every 30s)
- Metric: Hop count only (no link cost optimization)

**Legacy Deployment Example**:
```
BRANCH OFFICE NETWORK (RIPv1)
────────────────────────────

Branch-Router-01 (RIPv1)
  ↓
  └─ Network 192.168.1.0/24 (Branch subnet)
     └─ Connected to HQ via serial line (56K modem)

HQ-Router-01 (RIPv1)
  ├─ 10.0.0.0/24 (HQ subnet)
  ├─ 172.16.0.0/24 (DMZ)
  └─ 192.168.10.0/24 (Guest network)

RIPv1 Issues in this network:
  ✗ 56K modem saturated by RIP updates (512 bytes every 30s)
  ✗ Hop count limit prevents adding more remote sites
  ✗ No VLSM support forces inefficient subnetting
  ✗ No authentication allows unauthorized devices to advertise routes
  ✗ Convergence time on link failure: 3-5 minutes
```

**RIPv1 Support in Modern Devices**:
- Cisco IOS: Still supported, but deprecated
- Cisco IOS XE: Still supported, but not recommended
- Cisco IOS XR: Removed (not supported)
- Juniper Junos: Still supported for compatibility
- Modern vendors: Actively discouraging new deployments

### 1.2 RIPv2 Assessment

**RIPv2 Improvements**:
- VLSM support (variable length subnet masks)
- Authentication (MD5 or simple password)
- Multicast updates (224.0.0.9 instead of broadcast)
- Subnet mask field in routes
- Still limited to 15 hops
- Still 30-second convergence time

**Typical RIPv2 Deployment**:
```
SMALL ENTERPRISE NETWORK (RIPv2)
────────────────────────────────

Site-A-Router (RIPv2)
  Networks:
    10.0.0.0/24
    10.0.1.0/24
    10.0.2.0/24

Site-B-Router (RIPv2)
  Networks:
    172.16.0.0/24
    172.16.1.0/24

RIPv2 Update: Site-B-Router receives
  "Route to 10.0.0.0/24 via Site-A-Router (metric: 1)"
  "Route to 10.0.1.0/24 via Site-A-Router (metric: 1)"
  etc...

Problems:
  ✗ Unequal cost load balancing not supported
  ✗ No traffic engineering possible
  ✗ Difficult to implement redundant paths
  ✗ Not scalable beyond 15 hops (limits topology)
  ✗ High bandwidth for frequent updates
```

### 1.3 IGRP Assessment

**IGRP Characteristics** (Cisco Proprietary):
- Metric: Bandwidth, delay, reliability, load, MTU
- Maximum hop count: 100 (vs RIP's 15)
- Update interval: 90 seconds
- Cisco proprietary (not interoperable with other vendors)
- Classful routing (no VLSM)
- Successor and feasible successor concept (loop prevention)

**IGRP to EIGRP Evolution**:
```
IGRP-only network (legacy):
  Cisco-only routers
  Limited to Cisco ecosystem
  IGRP and EIGRP cannot peer
  Convergence: 3-5 minutes (slow)

Modern requirement:
  Interoperable network (Juniper, Arista, etc.)
  Cisco EIGRP AS upgrade required
  Gradual migration path needed
  Faster convergence (sub-second)

Note: IGRP end-of-life: January 2023 (Cisco)
```

---

## 2. OSPF Migration Strategy

### 2.1 OSPF Advantages Over Legacy Protocols

```
FEATURE COMPARISON
═════════════════════════════════════════════

Feature                 RIPv2           OSPF
────────────────────    ─────────────   ──────────────
Max hop count           15              Unlimited
Convergence time        3-5 min         <30 seconds
Metric                  Hop count       Bandwidth-based (1-65535)
Update interval         30 seconds      Triggered (LSA floods)
VLSM support            Yes             Yes
Authentication          MD5             MD5, SHA-256
Bandwidth usage         High (periodic) Low (triggered events)
Area hierarchy          No              Yes (OSPF areas)
Load balancing          Single path     Equal-cost multipath (ECMP)
Traffic engineering     No              Limited (via cost adjustment)
Scalability             Poor (max 15)   Excellent (thousands of routes)
Convergence guaranteed  No              Yes (SPF algorithm)

PRACTICAL IMPACT:
  ✓ OSPF can support networks > 100 routers
  ✓ OSPF converges in < 5 seconds (vs IGRP 5 minutes)
  ✓ OSPF uses 90% less bandwidth than RIP for same network
  ✓ OSPF can load-balance across 16 equal-cost paths
  ✓ OSPF's SPF algorithm guarantees loop-free routing
```

### 2.2 RIPv2 to OSPF Migration

**Phase 1: Design OSPF Areas**

```
EXISTING RIPv2 NETWORK
──────────────────────
        Corp-Router-01 (HQ)
        /            \
    Branch-01    Branch-02
    (5 routers)  (3 routers)

Total routers: 11
Total subnets: 45
Typical network size

OSPF DESIGN
────────────
Area 0 (Backbone):
  ├─ Corp-Router-01 (ABR - Area Border Router)
  └─ Core-Router-01 (ABR)

Area 1 (HQ):
  ├─ HQ-Router-01 (connects to backbone)
  ├─ HQ-Router-02 (redundant)
  └─ 15 subnets

Area 2 (Branch-01):
  ├─ Branch-Router-01 (ABR, connects to Area 0)
  ├─ Branch-Router-02 (internal)
  ├─ Branch-Router-03 (internal)
  └─ 10 subnets

Area 3 (Branch-02):
  ├─ Branch-Router-01 (ABR)
  └─ Branch-Router-02 (internal)
  └─ 8 subnets

Benefits of this design:
  ✓ Area 0 handles inter-area routing (reduces LSA flooding)
  ✓ Branch areas only flood local LSAs
  ✓ Scalable to 200+ routers with same design
  ✓ Easy to add new branches (new area)
```

**Phase 2: Parallel RIP/OSPF Coexistence**

```
YEAR 1 - COEXISTENCE PHASE
──────────────────────────

All routers run both RIPv2 and OSPF:

Router running:
  ✓ RIPv2 on uplink to RIP-only devices
  ✓ OSPF on links to OSPF-enabled devices
  ✓ Redistribution: RIP → OSPF (one direction)
     "Import external routes from RIP to OSPF"

Example: Branch-Router-01 configuration
```
router rip
  version 2
  network 192.168.100.0
!
router ospf 1
  network 10.0.0.0 0.255.255.255 area 0
  redistribute rip subnets
    metric-type 2
!
route-map RIP-TO-OSPF
  set metric 1000
  set metric-type type-2
!
router ospf 1
  redistribute rip subnets route-map RIP-TO-OSPF
```

Coexistence rules:
  ✓ One-way redistribution (RIP → OSPF only)
  ✓ OSPF preferred as primary IGP
  ✓ RIP routes tagged as external (E2)
  ✓ Default route points to OSPF
  ✓ RIP gradually disabled as endpoints migrate
```

**Phase 3: Complete OSPF Migration**

```
YEAR 2 - OSPF-ONLY PHASE
─────────────────────────

Progression:
  Week 1: Migrate Branch-02 routers to OSPF-only
  Week 2: Migrate Branch-01 routers to OSPF-only
  Week 3: Verify all internal routes via OSPF
  Week 4: Migrate HQ routers to OSPF-only
  Week 5: Disable RIP completely
  Week 6: Verify and stabilize

Post-migration benefits realized:
  ✓ Convergence time: < 5 seconds (was 3-5 minutes)
  ✓ Network bandwidth: 10x reduction in IGP traffic
  ✓ Scalability: Can now support 200+ routers
  ✓ Reliability: SPF guarantees loop-free topology
  ✓ Management: Single IGP to monitor/troubleshoot
```

### 2.3 IGRP to OSPF Migration (Cisco Networks)

**Challenge**: IGRP and OSPF cannot coexist on same link easily

**Solution: EIGRP as Intermediate Step**

```
MIGRATION PATH: IGRP → EIGRP → OSPF
═══════════════════════════════════════

PHASE 1: IGRP-only (current state)
  All routers: Cisco IOS running IGRP AS 100
  Convergence: Slow (3-5 minutes on failure)

PHASE 2: IGRP + EIGRP (transition)
  Configure EIGRP AS 100 (same AS)
  Routers run both protocols
  EIGRP and IGRP automatically redistribute
  Convergence: Sub-second (EIGRP takes over)
  Duration: 6 months (allows stabilization)

PHASE 3: EIGRP-only (intermediate state)
  Remove IGRP from all routers
  EIGRP AS 100 primary IGP
  Allows Cisco-only network to stabilize
  Duration: 1-2 years

PHASE 4: EIGRP + OSPF (multi-vendor readiness)
  Introduce Juniper/Arista routers running OSPF
  Configure redistribution EIGRP ↔ OSPF
  Parallel operation (6-12 months)
  Duration: 12 months

PHASE 5: OSPF-only (vendor-agnostic)
  Remove EIGRP from all routers
  Pure OSPF network (vendor-independent)
  Final state: Can add any vendor devices
  Duration: Ongoing

Timeline: 3-4 years total for complete transition
```

---

## 3. BGP Migration Strategy

### 3.1 When to Migrate to BGP

**BGP Use Cases**:
- Multi-vendor environment (requires vendor-neutral routing)
- Internet connectivity (BGP is the standard)
- Complex traffic engineering (policy-based routing)
- Interconnection with partner networks
- Large-scale networks (1000+ routes)

**Typical BGP Migration Trigger**:
```
DECISION MATRIX: Should we use BGP?
───────────────────────────────────

Current IGP: OSPF (internal routing works well)
Use case: Adding internet connectivity
        ↓
        BGP is appropriate

Current IGP: RIPv2 (limited scalability)
Use case: Merge two companies' networks
        ↓
        BGP + OSPF hybrid approach

Current IGP: IGRP (Cisco-only)
Use case: Adding Juniper routers
        ↓
        OSPF preferred (simpler than BGP for internal use)

Current IGP: OSPF
Use case: Provide connectivity to customers
        ↓
        BGP required (standard for AS interconnection)
```

### 3.2 OSPF to BGP Transition

**Architecture Change**:
```
INTERNAL ROUTING (OSPF) + EXTERNAL ROUTING (BGP)
════════════════════════════════════════════════

BEFORE: Single OSPF network
─────────────────────────────

        Campus Network
        (OSPF AS N/A)
            |
        Core Routers
            |
        Internet (ISP)

Issues:
  ✗ Campus network exposed to internet instability
  ✗ Internet route flapping affects internal users
  ✗ No traffic engineering with ISP
  ✗ Routing decisions tied to hop count


AFTER: BGP for Internet + OSPF for Internal
─────────────────────────────────────────────

        Campus Network
        (OSPF Area 0-3)
            |
        Border Routers (OSPF + BGP)
            |  ↑
            | BGP session
            v  |
        Internet (ISP)

Benefits:
  ✓ Internal network stable regardless of internet
  ✓ Border routers filter BGP routes
  ✓ Traffic engineering via BGP AS-path prepending
  ✓ Policy-based routing decisions
  ✓ More predictable convergence
```

**Implementation Steps**:

```
STEP 1: Configure BGP on border routers (6-month preparation)
────────────────────────────────────────

! Core-Router-01 (OSPF + BGP)
router ospf 1
  network 10.0.0.0 0.255.255.255 area 0
!
router bgp 65001
  neighbor 192.0.2.1 remote-as 64000
  address-family ipv4
    neighbor 192.0.2.1 activate
    no neighbor 192.0.2.1 send-community
  !
exit

! Static route to ISP (temporary)
ip route 0.0.0.0 0.0.0.0 192.0.2.1

Results:
  ✓ BGP session up with ISP
  ✓ Border router learns ISP routes via BGP
  ✓ Default route still static (temporary)
  ✓ All traffic through OSPF (BGP in parallel)

STEP 2: Enable BGP on backup border router (Month 6-9)
──────────────────────────────────────────

! Core-Router-02 (backup)
router bgp 65001
  neighbor 192.0.2.5 remote-as 64000
!

Now:
  ✓ Two BGP sessions to ISP
  ✓ Redundant internet connectivity
  ✓ OSPF still primary internal IGP

STEP 3: Switch default route from static to BGP (Month 9-12)
──────────────────────────────────────────────

! Remove static route
no ip route 0.0.0.0 0.0.0.0

! BGP now advertises 0.0.0.0/0
router bgp 65001
  address-family ipv4
    redistribute connected subnets
    neighbor 192.0.2.1 send-community
  !
exit

Results:
  ✓ All internet traffic via BGP
  ✓ Dynamic failover if ISP link fails
  ✓ Convergence time < 1 second
  ✓ No static routes needed

STEP 4: Publish internal routes via BGP (Optional, Month 12+)
─────────────────────────────────────────────

If network becomes service provider:
  router bgp 65001
    address-family ipv4
      redistribute ospf 1 subnets
    !
  exit

Now external networks can reach your subnets via BGP
```

---

## 4. Segment Routing (SR) Introduction

### 4.1 Segment Routing Overview

Segment Routing simplifies network operations by encoding path information in packet headers.

**Key Concept**:
```
Traditional OSPF/ISIS:
  Each router independently computes paths
  Complex state machine
  Difficult to engineer traffic

Segment Routing:
  Ingress router encodes path in packet header
  Intermediate routers follow instructions
  Simple forwarding logic
  Easy traffic engineering

Example:
Traditional:
  Packet: [Source IP: 10.1.1.1] [Dest IP: 10.3.3.3]
  Router A: Compute path to 10.3.3.3 via OSPF
  Router A: Send to next hop (Router B)
  Router B: Independently compute path via OSPF
  Router B: Send to next hop (Router D)
  Router D: Send directly to destination

Segment Routing:
  Packet: [IP Header] [SR Header: [Router-B, Router-D, Router-F]]
  Router A: Follow first instruction → forward to Router B
  Router B: Remove self from header → forward to Router D
  Router D: Remove self from header → forward to Router F
  Router F: Remove header, forward normally
```

### 4.2 SR Benefits Over Traditional Routing

```
FEATURE COMPARISON: Traditional vs Segment Routing
══════════════════════════════════════════════════

Feature                 OSPF/ISIS       Segment Routing
────────────────────    ─────────────   ──────────────────
Path computation        Distributed     Centralized/Ingress
Configuration           OSPF metrics    SR policy (simple)
Traffic engineering     Complex ACLs    SR path labels
Convergence             Seconds         Sub-second
Operational overhead    High            Low
Vendor dependencies     High (vendor)   Low (standard)
Multi-path routing      ECMP (auto)     Explicit paths
Failure recovery        Automatic       Planned alternatives
Bandwidth optimization  Limited         Full control
Fast reroute            Basic           Optimal alternatives

REAL WORLD EXAMPLE:
  Network requirement: "Route video traffic via high-bandwidth path"

  Traditional OSPF:
    Set interface metric to low value (encourage path selection)
    Hope other administrators make same decisions
    Complex change procedure
    Difficult to roll back if issues occur

  Segment Routing:
    Define path: [Node-A] → [Node-C] → [Node-F] (direct high-speed)
    Apply to video traffic (IP prefix or MPLS label)
    Simple configuration change
    Immediate rollback if needed
```

---

## 5. Implementation Roadmap

### 5.1 Complete Protocol Modernization Timeline

```
NETWORK PROTOCOL MODERNIZATION ROADMAP
═══════════════════════════════════════════════════════════

YEAR 1: ASSESSMENT AND PLANNING
──────────────────────────────

Q1: Inventory and Analysis
  □ Identify all legacy protocols in use
  □ Map dependencies and criticality
  □ Analyze vendor support timelines
  □ Assess team expertise gaps

Q2: Design and Procurement
  □ Design modern network architecture
  □ Procure OSPF/BGP-capable hardware
  □ Plan phased transition approach
  □ Order lab equipment for testing

Q3: Lab and Testing
  □ Build lab network with legacy + modern protocols
  □ Test migration procedures
  □ Train network staff on new protocols
  □ Validate interoperability

Q4: Preparation
  □ Complete documentation
  □ Prepare runbooks and procedures
  □ Notify stakeholders of changes
  □ Conduct dry-run migrations


YEAR 2: INITIAL MIGRATION
──────────────────────────

Q1: Branch Sites (Non-critical)
  □ Migrate Branch-Office-01: RIPv2 → OSPF
  □ Migrate Branch-Office-02: RIPv2 → OSPF
  □ Validate and stabilize
  □ Document lessons learned

Q2: Secondary Sites (Medium-critical)
  □ Migrate Regional-Office-01: IGRP → EIGRP
  □ Introduce first non-Cisco device (Juniper)
  □ Begin EIGRP → OSPF planning
  □ Validate multi-vendor operation

Q3: Internet Connectivity
  □ Deploy BGP on border routers
  □ Establish BGP sessions with ISP
  □ Test failover scenarios
  □ Monitor BGP stability

Q4: Central Sites
  □ Prepare for primary data center migration
  □ Complete OSPF area design
  □ Validate convergence timing
  □ Finalize cutover procedures


YEAR 3: COMPLETION AND OPTIMIZATION
───────────────────────────────────

Q1: Primary Data Center
  □ Migrate main site: IGRP/RIP → OSPF
  □ Decommission legacy protocols
  □ Validate complete network stability
  □ Optimize OSPF metrics

Q2: Advanced Features
  □ Implement BGP traffic engineering
  □ Deploy segment routing in lab
  □ Plan segment routing rollout
  □ Optimize network performance

Q3: Vendor Consolidation
  □ Decommission legacy Cisco-only features
  □ Standardize on vendor-neutral protocols
  □ Reduce support contracts
  □ Optimize operational procedures

Q4: Post-Migration
  □ Complete network documentation
  □ Conduct lessons-learned review
  □ Update training materials
  □ Plan future improvements (SD-WAN, etc.)


MILESTONES:
  Month 6:   50% of network sites modernized
  Month 12:  100% of sites using OSPF or BGP
  Month 18:  Complete decommissioning of legacy protocols
  Month 24:  Full segment routing deployment (if applicable)
```

---

## 6. Protocol Feature Comparison

### 6.1 Comprehensive Feature Matrix

```
ROUTING PROTOCOL FEATURE MATRIX
═══════════════════════════════════════════════════════════

FEATURE                    RIPv2    OSPF    BGP     SR
────────────────────────── ────────────────────────────
Scalability                Poor     Good    Excel   Excel
Convergence time           3-5 min  <30s    <1s     <1s
Metric type                Hop      Bandwidth Cost    Label
VLSM support               Yes      Yes     Yes     Yes
Authentication             MD5      MD5     MD5     MD5
Vendor support             Limited  Excel   Excel   Growing
Multi-vendor ready         Yes      Yes     Yes     Yes
Area/Level support         No       Yes     No      No
Load balancing             1 path   ECMP    ECMP    Explicit
BGP community support      No       No      Yes     N/A
QoS integration            Limited  Good    Excel   Excel
Traffic engineering        Limited  Limited Excel   Excel
Fast failover              No       Loops   N/A     Optimal
API/Programmable           No       No      Yes     Yes
Segment routing support    No       No      No      Yes
Future vendor focus        Low      High    Excel   Excel


RECOMMENDATION BY NETWORK SIZE:

< 20 routers, single site:
  ✓ OSPF or RIPv2 (if legacy equipment required)
  ✗ BGP (overkill)
  ✗ SR (not needed)

20-100 routers, multiple sites:
  ✓ OSPF (industry standard)
  ~ BGP (if internet connectivity needed)
  ✗ SR (consider for large deployments)

100-1000 routers, complex topology:
  ✓ BGP for external connectivity
  ✓ OSPF for internal routing
  ~ SR (evaluate for traffic engineering needs)

1000+ routers, service provider:
  ✓ BGP + SR (optimal for scale)
  ~ OSPF (if existing)
  ✗ RIP/IGRP (not suitable)
```

---

## 7. Testing and Validation

### 7.1 Protocol Interoperability Testing

```
TESTING MATRIX: Protocol Transitions
════════════════════════════════════════════════════════

TEST SCENARIO 1: RIPv2 and OSPF Coexistence
──────────────────────────────────────────

Setup:
  Router A: RIPv2 only
  Router B: RIPv2 + OSPF (redistribution)
  Router C: OSPF only

Test cases:
  ✓ Router B receives RIP route from A
  ✓ Router B redistributes to OSPF
  ✓ Router C learns route via OSPF
  ✓ Verify metric conversion correct
  ✓ Test failure recovery (B fails)
    Expected: A → C route via OSPF
  ✓ Load balance across both protocols
  ✓ Verify no routing loops occur

Success criteria:
  ✓ All routes converge correctly
  ✓ No loops detected (trace route)
  ✓ Failover working as expected
  ✓ Performance acceptable


TEST SCENARIO 2: OSPF and BGP Interaction
──────────────────────────────────────────

Setup:
  Router A: OSPF area 0 (internal)
  Router B: OSPF + BGP (border router)
  Router C: BGP only (ISP router)
  Router D: OSPF area 0 (destination)

Test cases:
  ✓ Router B receives external route from C via BGP
  ✓ Router B redistributes BGP to OSPF
  ✓ Router A and D learn external route
  ✓ Verify external route tag (E1 or E2)
  ✓ Test BGP failover to backup link
  ✓ Verify OSPF prefers internal routes over external
  ✓ Test convergence time on BGP session flap

Success criteria:
  ✓ External routes reachable from internal network
  ✓ Convergence < 5 seconds
  ✓ No routing loops
  ✓ BGP backup link works automatically


TEST SCENARIO 3: Multi-Protocol Load Balancing
────────────────────────────────────────────

Setup:
  Network A (source) to Network D (destination)
  Primary path: A → B → D (via OSPF)
  Secondary path: A → C → D (via BGP)

Test cases:
  ✓ Configure equal-cost load balancing (ECMP)
  ✓ Send traffic from A to D
  ✓ Verify load balanced on both paths
  ✓ Fail primary path, verify fallback to secondary
  ✓ Restore primary, verify balanced again
  ✓ Monitor per-flow consistency (not per-packet)

Success criteria:
  ✓ Traffic distributed 50/50 on both paths
  ✓ Failover automatic and lossless
  ✓ Recovery quick (< 2 seconds)
```

---

## 8. Operational Procedures

### 8.1 Decommissioning Legacy Protocols

```
PROTOCOL DECOMMISSIONING CHECKLIST
═════════════════════════════════════════════════════

PHASE 1: Preparation (1 month before shutdown)
──────────────────────────────────────────────

□ Document all devices still running legacy protocol
□ Verify all routes learned via modern protocol
□ Identify any devices that CANNOT migrate
□ Plan exceptions (if needed)
□ Notify all stakeholders of decommissioning date
□ Schedule maintenance window


PHASE 2: Pre-Shutdown Validation (1 week before)
───────────────────────────────────────────────

□ Disable legacy protocol on one test device
□ Verify all routes still reachable via modern protocol
□ Monitor for convergence issues
□ Re-enable legacy protocol on test device
□ Repeat for each device type in network


PHASE 3: Shutdown (Scheduled maintenance window)
───────────────────────────────────────────

Devices: [List all devices to modify]

Device 1: Remote-Router-01
  Time: 22:00 UTC
  Action: configure terminal
           no router rip
           end
  Verify: show routing table (only OSPF routes)
  Confirm: 5 minutes before moving to next

Device 2: Branch-Router-02
  Time: 22:05 UTC
  [Same procedure]

... [repeat for all devices]

PHASE 4: Post-Shutdown Verification (30 minutes)
───────────────────────────────────────────────

□ Verify all routing tables converged
□ Test east-west traffic (between sites)
□ Test north-south traffic (to internet)
□ Test redundancy failover
□ Monitor for any late-converging routes
□ Check CPU/memory not elevated
□ Confirm users reporting no connectivity issues
□ Monitor for 2 hours post-shutdown


PHASE 5: Documentation and Closure
──────────────────────────────────

□ Update network topology documentation
□ Archive old configurations
□ Record shutdown completion
□ Notify stakeholders of success
□ Schedule follow-up optimization review
□ Plan for next protocol modernization phase
```

---

## 9. Troubleshooting Protocol Issues

### 9.1 Common Issues During Migration

```
TROUBLESHOOTING GUIDE
═════════════════════════════════════════════════════

ISSUE: Suboptimal routing path after migration
─────────────────────────────────────────────────

Symptom:
  Traffic taking longer path after OSPF enabled
  Example: Before OSPF: 3 hops, After: 5 hops
  Latency increased 20ms

Root cause analysis:
  1. Check OSPF cost calculation
     ! RIP used hop count (1 metric per hop)
     ! OSPF uses bandwidth-based cost
     ! Formula: cost = 100,000,000 / bandwidth (kbps)

  2. Example:
     Link A: 1 Gbps → cost = 100,000,000 / 1,000,000 = 100
     Link B: 10 Mbps → cost = 100,000,000 / 10,000 = 10,000

     RIP metric: Both links = 1 hop
     OSPF metric: Link B = 100x more expensive!

     Solution: Adjust OSPF cost on slower links

Fix procedure:
  interface Serial0/0/0
    bandwidth 10000  (Set actual bandwidth)
    ip ospf cost 1000 (Or manually adjust cost)
  exit

  Verification:
    show ip ospf interface Serial0/0/0
    show ip ospf neighbor
    show ip route ospf (verify new path)


ISSUE: Routing loops during RIPv2/OSPF coexistence
──────────────────────────────────────────────────

Symptom:
  Traceroute shows: Router A → Router B → Router A (loop)
  Packet counters increasing on interfaces
  Device CPU high

Root cause:
  Bidirectional redistribution configured
  RIP route → OSPF → back to RIP → loop created

Prevention:
  1. Configure one-way redistribution ONLY
     router ospf 1
       redistribute rip subnets
     ! (RIP to OSPF direction)

     no redistribute ospf from OSPF area back to RIP

  2. Increase RIP metrics to prefer native protocol
     route-map RIP-TO-OSPF
      set metric 16  (16 = unreachable in RIP)
     !
     router ospf 1
      redistribute rip subnets route-map RIP-TO-OSPF

  3. Use distribute lists to block routes
     access-list 10 deny any  (Block all RIP routes)
     router rip
      distribute-list 10 out ospf 1

Fix procedure:
  1. Identify and remove problematic redistribution
  2. Wait 3 minutes for convergence
  3. Verify no loops with traceroute
  4. Implement proper filters
  5. Gradually migrate devices to eliminate RIP entirely


ISSUE: BGP session flaps after OSPF migration
─────────────────────────────────────────────

Symptom:
  BGP neighbor status oscillates between UP and DOWN
  Routes disappear and reappear every 30 seconds
  Users report intermittent connectivity

Root cause:
  1. BGP uses OSPF learned loopback addresses
  2. OSPF convergence slower than expected
  3. BGP session lost → neighbor down → reconverge

  Timeline:
    00:00:00 - OSPF link down
    00:00:05 - OSPF reconverges
    00:00:08 - BGP loopback reachable again
    00:00:09 - BGP session re-establishes
    00:00:15 - BGP routes re-advertised
    Total disruption: 15 seconds

Fix procedure:
  1. Increase BGP holddown timer temporarily
     router bgp 65001
      timers connect 30 60 60  (reduce reconnect attempts)

  2. Verify BGP loopback reachable
     ping 10.0.1.1 (source 10.0.1.2)

  3. Check OSPF convergence with SPF logs
     debug ip ospf spf statistics

  4. Increase OSPF priority to stabilize network
     interface Loopback0
      ip ospf priority 200  (higher = used for SPF root)

  5. Monitor convergence time
     show ip ospf statistics
     SPF event triggered every X seconds
     (Should be < 1 second with stable network)
```

---

## 10. References and Standards

- **RFC 2453**: RIP Version 2 (Informational)
- **RFC 2328**: OSPF Version 2
- **RFC 4271**: Border Gateway Protocol 4 (BGP-4)
- **RFC 7426**: Segment Routing Architecture
- **RFC 3031**: Multiprotocol Label Switching Architecture

**Vendor Documentation**:
- **Cisco**: BGP Configuration, OSPF Design Guide
- **Juniper**: Segment Routing Implementation
- **Arista**: OSPF and BGP Configuration

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Architecture and Operations Team
