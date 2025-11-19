# High Availability Network Design Guide

## Introduction
This guide covers designing networks that meet stringent uptime requirements (99.99% or higher) through strategic redundancy and failover mechanisms.

## Understanding Availability Targets

### SLA Definitions

```
99.0% (Two Nines):
  Downtime: 87.6 hours/year (3.65 days/month)
  Acceptable for: Non-critical, internal-only services
  Requirement: Basic redundancy

99.9% (Three Nines):
  Downtime: 8.76 hours/year (43.8 minutes/month)
  Acceptable for: Standard business services
  Requirement: Redundant links + failover

99.99% (Four Nines):
  Downtime: 52.6 minutes/year (4.4 minutes/month)
  Acceptable for: Critical business services
  Requirement: N+1 redundancy, fast failover

99.999% (Five Nines):
  Downtime: 5.26 minutes/year (26 seconds/month)
  Acceptable for: Mission-critical services
  Requirement: N+2 redundancy, sub-second failover

99.9999% (Six Nines):
  Downtime: 31 seconds/year (2.6 seconds/month)
  Acceptable for: Carrier-grade services
  Requirement: Complex redundancy, automatic rerouting
```

## Design Principle 1: Link Redundancy

### Dual Uplink Strategy

```
Basic dual uplink:

Access-1
  ├─ Primary: To Distribution-A (active)
  └─ Backup: To Distribution-B (standby via STP)

Traffic flow:
  Normal: Access-1 → Distribution-A → Core
  If Dist-A fails: Access-1 → Distribution-B (STP blocks alternate path)
  Failover time: 30-50 seconds (STP reconvergence)

Limitation: Long convergence time (50 seconds = 52.6 min/year lost)
```

### Active-Active Link Aggregation

```
EtherChannel (Link Aggregation Group):

Access-1
  ├─ Member-1: 10G to Distribution-A
  ├─ Member-2: 10G to Distribution-A
  ├─ Member-3: 10G to Distribution-B
  └─ Member-4: 10G to Distribution-B
  (4 × 10G = 40 Gbps total, full active-active)

Traffic distribution:
  Flow hash determines which member link
  If any link fails: Other 3 carry traffic (75% capacity)
  Failover time: <50ms (hardware detection)
  Convergence: Automatic, no protocol involvement

Port-Channel configuration:
  interface Port-channel 1
    switchport trunk allowed vlan 1-100
    spanning-tree cost 1000
  !
  interface Gi0/0/1
    channel-group 1 mode active
  interface Gi0/0/2
    channel-group 1 mode active
  (Members load balance traffic automatically)

Failure scenarios:
  - One link down: 75% capacity, no service disruption
  - Two links down: 50% capacity, continued service
  - Three links down: 25% capacity, service degraded but online
  - All four links down: Complete failure (unlikely)
```

## Design Principle 2: Gateway Redundancy

### HSRP (Cisco)

```
Scenario: Access users, single logical gateway

Virtual gateway IP: 10.10.1.1 (virtual)
Active router: Distribution-A (10.10.1.2)
Standby router: Distribution-B (10.10.1.3)

HSRP state machine:
  Normal:
    Distribution-A = ACTIVE (sends hellos every 3 sec)
    Distribution-B = STANDBY (listens)
    Users: Route via 10.10.1.1 → ARP to Dist-A MAC

  Dist-A fails:
    Dist-B stops receiving hellos (3 sec timeout × 3 = 9 sec max)
    Dist-B transitions to ACTIVE
    Dist-B starts responding to ARP for 10.10.1.1
    New gateway: 10.10.1.1 → ARP to Dist-B MAC
    Failover time: <10 seconds (typical 3-5 seconds)

Configuration:
  interface Vlan 10
    ip address 10.10.1.2 255.255.255.0
    standby 10 ip 10.10.1.1
    standby 10 priority 150 (Dist-A higher priority)
    standby 10 preempt (if higher priority comes up, take over)
    standby 10 timers 3 10 (hello every 3, dead after 10)
```

### VRRP (Multi-vendor)

```
Virtual Router Redundancy Protocol (RFC 5798):

Virtual IP: 10.10.1.1
Master router: Distribution-A (priority 100)
Backup router: Distribution-B (priority 99)

State transitions:
  Master sends VRRP advertisements every 1 second
  Backup waits for 3 advertisements to timeout
  Backup becomes master after 3 seconds (default)
  No manual preemption configuration

Configuration (Arista):
  interface Vlan 10
    ip address 10.10.1.2/24
    ip virtual-router address 10.10.1.1
    ip virtual-router mac-address 00:00:5e:00:01:0a
    vrrp 10 priority 100
    vrrp 10 advertisement-interval 1000

Advantages:
  - Standard (not vendor-specific)
  - Faster failover (1 second detect)
  - Simpler configuration
```

## Design Principle 3: Network Redundancy

### Core Layer Redundancy

```
Full mesh core:

        ┌─────────┐
        │ Core-1  │
        └────┬────┘
             │ 100G
         ┌───┴────┐
         │        │
    ┌────┴───┐ ┌─┴────┐
    │ Core-2 │ │Core-3│
    └────────┘ └──────┘

All cores connected to all others
Single core failure: 66% capacity remains
Double core failure: 33% capacity remains (if 3 cores)

BGP load balancing:
  router bgp 65001
    maximum-paths 2 (load balance across multiple paths)

Convergence:
  Any core failure: BGP reconverges (<30 seconds)
  For faster convergence: Configure BFD
  interface Gi0/0/1
    ip address 10.0.0.1 255.255.255.0
    bfd interval 300 min_rx 300 multiplier 3
    (detect failure in <1 second)
```

### WAN Link Redundancy

```
Dual ISP design:

        ┌─────────────────────────────────┐
        │   HQ Network                    │
        │   Core Router                   │
        └────────┬────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    ┌────┴──┐       ┌───┴────┐
    │ ISP A │       │ ISP B  │
    │ 1 Gbps│       │ 1 Gbps │
    │BGP AS │       │BGP AS  │
    │65100  │       │ 65101  │
    └───────┘       └────────┘

BGP failover:
  Primary route (ISP A): Local Preference 200
  Backup route (ISP B): Local Preference 100

  Normal: All traffic via ISP A (200 > 100)
  ISP A fails: BGP withdraws route, fails to ISP B (automatic)
  Convergence: 3-30 seconds (depends on BGP timers)

Faster convergence with BFD:
  BFD detects failure: <1 second
  BGP reacts immediately
  Traffic rerouted: 1-2 seconds

Configuration:
  neighbor 198.51.100.1 remote-as 65100 (ISP A)
  neighbor 203.0.113.1 remote-as 65101 (ISP B)
  !
  address-family ipv4
    neighbor 198.51.100.1 route-map RM-ISP-A in
    neighbor 203.0.113.1 route-map RM-ISP-B in

  route-map RM-ISP-A permit 10
    set local-preference 200

  route-map RM-ISP-B permit 10
    set local-preference 100
```

## Design Principle 4: Device Redundancy

### Modular Redundancy

```
Supervisor card redundancy:

Chassis: Catalyst 9500 (modular)

Scenario 1: Single supervisor (no redundancy)
  If supervisor fails: Complete switch failure
  Recovery: Manual, requires replacement
  Downtime: 1-4 hours (full switch replacement)
  Cost: Lower hardware cost

Scenario 2: Dual supervisors (Stateful Switchover)
  Active supervisor: Processes all traffic
  Standby supervisor: Mirrors state, ready to take over
  If active fails: Standby becomes active
  Convergence: <30 seconds (full traffic recovery)
  Downtime: Negligible for most applications
  Cost: +$20,000 per switch

Scenario 3: N+1 Fabric (Nexus 9516)
  Scenario: 6 line cards, 2 fabric cards (N+1)
  If fabric card fails: Other takes over (transparent)
  No traffic loss, no convergence time
  Redundancy: Highest level
  Cost: +$50,000 per chassis
```

### Switch Redundancy

```
Stacking (smaller switches):

Virtual Chassis (larger switches):
  - Up to 9 switches appear as one
  - Any switch failure: Others absorb traffic
  - Bandwidth maintained (minus failed switch)
  - Seamless failover

Distributed architecture:
  - Each switch independent
  - Load balance across switches
  - Any failure: Traffic shifts to others
  - No complexity of stacking

Recommended: Distributed (more resilient)
```

## Design Principle 5: Failure Domain Isolation

### Limiting Blast Radius

```
Problem: Single failure cascades to multiple services

Solution 1: Separate failure domains
  Campus-A devices: Only affect Campus-A users
  Campus-B devices: Only affect Campus-B users
  Data Center-1: Only affects that data center

  Core switch failure:
    Affects: All users (worst case)
    Mitigation: Dual core with load balancing
    Impact when fails: Reroute via other core (<5sec)

Solution 2: Geographic redundancy
  Data Center-1 (Primary):
    Location: East coast
    Users: Eastern sites directly
    Serves: Primary database

  Data Center-2 (Backup):
    Location: West coast
    Users: Western sites directly
    Serves: Replicated database

  Failure: DC-1 fails
  Impact: East coast users fail over to DC-2
  Latency: May increase 50-100ms (acceptable)
  Data: Replicated, zero loss (sync replication)
```

## Calculating Overall Availability

### Redundancy Effectiveness

```
Single device:
  MTBF (Mean Time Between Failures): 100,000 hours
  MTTR (Mean Time To Repair): 4 hours
  Availability = MTBF / (MTBF + MTTR) = 100,000 / 100,004 = 99.996%

With N+1 redundancy:
  - Device 1 fails: Device 2 handles (automatic failover)
  - Both must fail for actual outage
  - Probability of both failing simultaneously: 0.0001 × 0.0001 = 0.00000001
  - Availability ≈ 99.9999% (6 nines)

With N+2 redundancy:
  - Need all 3 to fail for outage
  - Three simultaneous failures: virtually impossible
  - Availability: Approaches 6-7 nines

Practical example:
  Network requirements: 99.99% (4 nines, 52.6 min/year)

  Solution:
  - Dual ISP (99.99% each): 99.9999% combined
  - Dual core switches: 99.9999% combined
  - Dual distribution switches: 99.9999% combined
  - Dual access switches: 99.99% combined
  - Overall: 99.9999%+ achieved (well above target)

  Cost: +50-100% infrastructure cost for redundancy
  Benefit: Meets SLA with high confidence
```

## Implementation Roadmap

```
Phase 1 (Foundation): Achieve 99.9%
  - Implement dual uplinks per access switch
  - Implement HSRP/VRRP on distribution
  - Implement EtherChannel for aggregation
  - Cost: Base infrastructure + 20% redundancy
  - Downtime: 8.76 hours/year acceptable

Phase 2 (Enhanced): Achieve 99.99%
  - Dual distribution switches per building
  - Implement link aggregation (active-active)
  - Implement BFD for fast convergence
  - Implement dual ISP
  - Cost: +40% additional infrastructure
  - Downtime: 52.6 minutes/year

Phase 3 (Resilient): Achieve 99.999%
  - Dual core switches (full mesh)
  - N+1 supervisor redundancy
  - N+2 fabric redundancy (if available)
  - Triple diversity (3 ISPs or paths)
  - Geographic distribution
  - Cost: +80-100% additional infrastructure
  - Downtime: 5.26 minutes/year
```

## Testing Redundancy

```
Failover testing (quarterly):

1. Link failover:
   [ ] Unplug one link in EtherChannel
   [ ] Verify traffic continues on other links
   [ ] Monitor for errors or drops

2. Device failover:
   [ ] Unplug primary distribution switch
   [ ] Verify failover to backup (<10 seconds)
   [ ] Verify user connectivity restored
   [ ] Replug and verify failback

3. ISP failover:
   [ ] Simulate ISP failure (null route)
   [ ] Verify traffic shifts to backup ISP
   [ ] Verify convergence time (<30 seconds)
   [ ] Restore and verify automatic failback

4. Data center failover:
   [ ] Fail over VM to secondary data center
   [ ] Verify application availability
   [ ] Verify data consistency
   [ ] Monitor cross-DC latency
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Advanced
**Focus:** 99.99% to 99.999% Uptime (4-5 Nines)
