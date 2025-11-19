# Data Center Network Design Guide

## Introduction
This guide covers designing modern data center networks optimized for east-west traffic, virtualization, and cloud workloads using spine-and-leaf architectures.

## Step 1: Assess Requirements

### Server and Workload Assessment

```
Data collection:

Physical inventory:
  - Number of physical servers: 200
  - Number of racks: 16
  - Avg servers per rack: 12
  - Network ports per server: 2 (redundancy)

Virtualization metrics:
  - Virtual machines: 1,200
  - Avg VM density: 6 VMs per physical server
  - Storage servers: 8 (with replication)

Network requirements:
  - VM-to-VM traffic ratio: 80% (east-west)
  - VM-to-Internet traffic: 15% (north-south)
  - Backup traffic: 5%

Application types:
  - Web tier (stateless): 400 VMs
  - Database tier (stateful): 300 VMs
  - Storage tier: 8 physical + 40 VMs
  - Management/admin: 50 VMs
```

### Performance Requirements

```
Traffic characteristics:

Peak throughput needed:
  VMs active: 1,000
  Avg bandwidth per VM: 100 Mbps
  Peak ratio: 2x average = 200 Mbps
  Total peak: 1,000 × 200 Mbps = 200 Gbps

Latency targets:
  Intra-pod: <1ms (same rack)
  Intra-pod cross-rack: <5ms
  Inter-pod: <10ms (acceptable)
  to-Internet: <50ms

Uptime requirement:
  Target: 99.99% (52.6 min/year downtime)
  Implication: N+1 redundancy mandatory, N+2 preferred
```

## Step 2: Design Fabric Topology

### Determine Tier Model

```
Small data center (< 100 servers):
  → Collapsed spine-leaf (16-24 spines)
  → Cost: Lower
  → Complexity: Moderate

Medium data center (100-500 servers):
  → Full 2-tier spine-leaf (32-64 spines)
  → Cost: Moderate
  → Complexity: Standard

Large data center (> 500 servers):
  → 3-tier with super-spines
  → Cost: High
  → Complexity: Advanced

Multi-pod (> 1,000 servers):
  → Multiple independent fabrics
  → Pod-to-pod over super-spines
  → Cost: Very High
  → Complexity: Very Advanced
```

### Design 2-Tier Clos (Typical)

```
Sizing example: 512 servers in 8 racks

Architecture:
  64 leaf switches (8 per rack)
  32 spine switches
  Full connectivity between all leaves and spines

Bandwidth calculation:
  Per leaf: 48 × 25G = 1,200 Gbps downlink (servers)
  Per leaf: 32 × 100G = 3,200 Gbps uplinks (spines)
  Oversubscription: 1,200 / 3,200 = 0.375:1 (non-blocking)

Scale capacity:
  Total server ports: 64 × 48 = 3,072 ports (3,072 servers)
  Total spine capacity: 32 × 48 = 1,536 × 100G = 153.6 Tbps
  Total leaf capacity: 64 × 48 = 3,072 × 25G = 76.8 Tbps
  Actual serving: ~3,000 servers @ 25-40G each = 75-120 Tbps
```

### Network Diagram

```
Spine Layer (32 switches)
        S1  S2  S3  ...S32
        ││││││││││││││││││
        ││││││││││││││││││
        ││││││││││││││││││
Leaf Layer (64 switches)
   L1  L2  L3  L4  ...L64
   │   │   │   │      │
  [R1 [R2 [R3 [R4  ...[R8]
   │]  │]  │]  │]     │]
   │   │   │   │      │
  Servers  Servers  Servers
  (48/leaf) (48/leaf) (48/leaf)

Per Leaf Connection Pattern:
  - Leaf connects to ALL spine switches
  - Leaf-1 to Spine-1,2,3,...32 (32 connections)
  - Each connection: 100G (fiber optic)
  - Redundancy: Full (any spine fails, others handle load)
  - Latency: Consistent (always 2 hops for leaf-to-leaf)
```

## Step 3: Routing Design

### BGP Configuration

```
Addressing scheme:

Spine loopback addresses:
  10.255.0.1/32 - Spine-1
  10.255.0.2/32 - Spine-2
  ...
  10.255.0.32/32 - Spine-32

Leaf loopback addresses:
  10.255.1.1/32 - Leaf-1
  10.255.1.2/32 - Leaf-2
  ...
  10.255.1.64/32 - Leaf-64

Link-local addressing (per RFC 5549):
  Leaf-Spine links: fe80::/10 (automatic)
  BGP over IPv6 link-local (preferred)
  Benefits: No IPv4 planning needed, standard practice

Server networks:
  Pod-1: 10.1.0.0/20 (Leaves 1-4)
  Pod-2: 10.1.16.0/20 (Leaves 5-8)
  Pod-3: 10.1.32.0/20 (Leaves 9-12)
  ...
```

### BGP Routing Policy

```
Leaf configuration (example):

router bgp 65100 (per-rack ASN, or 65100 for all)
  neighbor 10.255.0.1 remote-as 65000
  neighbor 10.255.0.2 remote-as 65000
  ... (connect to all spines)

  address-family ipv4 unicast
    neighbor 10.255.0.0/24 activate
    network 10.1.0.0 mask 255.255.240.0 (pod subnet)
    maximum-paths 32 (ECMP across all spines)

Spine configuration:

router bgp 65000
  neighbor 10.255.1.0/24 remote-as 65100 (all leaves)

  address-family ipv4 unicast
    neighbor 10.255.1.0/24 activate
    neighbor 10.255.1.0/24 route-reflector-client
    network 10.0.0.0 mask 255.0.0.0 (all pod subnets)
```

### Load Balancing

```
ECMP with per-flow hashing:

Hash input: (Source IP, Dest IP, Source Port, Dest Port)
Distribution: Hash % 32 spines (uniform across all paths)

Example traffic:
  VM1 (10.1.1.10) → VM2 (10.1.16.10)
  Flow hash determines: Leaf-1 → Spine-7 → Leaf-5 → VM2

  VM1 (10.1.1.11) → VM2 (10.1.16.10)
  Different source, different hash: Leaf-1 → Spine-22 → Leaf-5 → VM2

Benefits:
  - All spines utilized simultaneously
  - No single bottleneck
  - Multiple flows between same VMs distributed
  - Convergence on spine failure: <3 seconds
```

## Step 4: VLAN and Overlay Design

### Pod-Based Segmentation

```
Logical pod structure:

Pod-1 (Customers A, B):
  VLAN: 1001-1010
  Subnet: 10.1.0.0/20
  Leaves: 1-4
  Isolation: L3 routed

Pod-2 (Customer C):
  VLAN: 2001-2010
  Subnet: 10.1.16.0/20
  Leaves: 5-8
  Isolation: L3 routed

Shared Services Pod:
  VLAN: 3001-3010
  Subnet: 10.1.32.0/20
  Services: NTP, DNS, DHCP, NMS

Inter-pod communication:
  Through spine layer (normal L3 routing)
  Policies: Allow customer-service, restrict customer-customer
```

### VXLAN for Multi-tenancy

```
Deployment (optional, for cloud environments):

Tenant-A Network 1:
  VLAN 100 (local) → VXLAN VNI 10100
  Subnet: 10.100.0.0/24
  Isolation: Complete (different VXLAN namespace)

Tenant-A Network 2:
  VLAN 200 (local) → VXLAN VNI 10200
  Subnet: 10.100.1.0/24

Tenant-B Network 1:
  VLAN 100 (local) → VXLAN VNI 20100
  Subnet: 10.101.0.0/24
  (Same VLAN ID, different VNI, complete isolation)

Benefits:
  - Same VLAN ID can mean different networks
  - Transparent VM mobility
  - Multi-tenant security
  - Unlimited scalability
```

## Step 5: High Availability Design

### Redundancy Strategy

```
Server-to-leaf redundancy:
  - Each server: Dual NICs
  - Active-Active load balancing (bonding/LAG)
  - One NIC fails: Continue on other
  - Both NICs fail: Server unreachable
  - Expected: Rare failure

Leaf-to-spine redundancy:
  - Each leaf: 32 connections (all spines)
  - One spine fails: Load shifts to 31 others
  - Failover time: <100ms (BGP convergence)
  - Expected: Once per 2-3 years

Spine layer:
  - No single point of failure
  - Total spine bandwidth: 32 × 48 × 100G = 153.6 Tbps
  - One spine failure: Capacity = 31 × 48 × 100G = 148.8 Tbps
  - Loss: 3% (acceptable)

Data center layer:
  - Multiple data centers (active-active)
  - VM replication: Synchronous (zero loss)
  - Storage replication: Asynchronous (acceptable lag)
  - Network: Direct fiber link or IPsec
```

### Disaster Recovery

```
For critical applications:

Synchronous replication:
  - Write confirmed only after reaching both DCs
  - RPO (Recovery Point Objective): Zero
  - RTO (Recovery Time Objective): <1 minute
  - Technology: Storage-based or app-level
  - Bandwidth: 2x normal traffic

Asynchronous replication:
  - Write confirmed after primary write
  - Replica in secondary DC (lag: 1-60 seconds)
  - RPO: Data loss possible (~last 60 seconds)
  - RTO: 5-15 minutes
  - Bandwidth: 1.5x traffic (compression)

Design: Mix of both
  - Critical: Sync (databases, key services)
  - Non-critical: Async (test/dev, caches)
  - Cost: ~30% additional infrastructure
```

## Step 6: Performance Optimization

### Traffic Engineering

```
Objective: Avoid congestion hotspots

Monitoring:
  - Track interface utilization (all spine uplinks)
  - Alert if > 80% sustained
  - Trend analysis for growth

Optimization techniques:

1. VM placement awareness:
   - Communicate busy VMs placement
   - Group communicating VMs on same leaf
   - Reduces spine traffic

2. Load balancing:
   - Multi-path routing (ECMP) distributes load
   - Hash algorithm ensures consistent (no reordering)
   - Per-flow balancing (not per-packet)

3. Oversubscription acceptance:
   - 2:1 oversubscription: East-West typical pattern
   - Some flows peak, others low (statistical multiplexing)
   - Design for 95th percentile, not 100th percentile

Example:
  Peak individual flow: 25 Gbps
  But not all flows peak simultaneously
  95th percentile aggregate: 80 Gbps (with 100 flows)
  Design capacity: 100 Gbps (2:1 oversubscription)
```

## Implementation Checklist

```
Phase 1: Hardware Setup (Week 1-2)
  [ ] Racks installed and powered
  [ ] Spine switches installed and powered
  [ ] Leaf switches installed in each rack
  [ ] Transceiver inventory verified
  [ ] Fiber cables cut and labeled
  [ ] All connections made (physical)
  [ ] Link lights verified (all up)

Phase 2: Basic Configuration (Week 3)
  [ ] Device base configs (hostname, management)
  [ ] Interface configuration (IP, loopback)
  [ ] BGP sessions established (all spine-leaf)
  [ ] Routing table populated
  [ ] Ping tests between all devices
  [ ] Management access verified

Phase 3: Pod Configuration (Week 4)
  [ ] VLANs created on all leaves
  [ ] VLAN SVI routing enabled
  [ ] Pod subnets allocated
  [ ] DHCP scopes configured
  [ ] NTP synchronized
  [ ] DNS resolving

Phase 4: Testing (Week 5)
  [ ] Server connectivity verified
  [ ] VM-to-VM latency tested (<5ms)
  [ ] Bandwidth tests between pods
  [ ] Spine failure simulation (automatic failover)
  [ ] Leaf failure simulation
  [ ] Load balancing verification (traffic across spines)
  [ ] High availability testing

Phase 5: Production Migration (Week 6-8)
  [ ] Parallel operation with old network
  [ ] Gradual VM migration to new fabric
  [ ] Performance monitoring during transition
  [ ] Rollback plan in place
  [ ] Final cutover and old network decommission
```

## Troubleshooting Guide

### Connectivity Issues

```
VM can't reach another VM:

Checklist:
1. Both on same leaf?
   → Direct L2 switching (vlan lookup)
   → Check: show vlan id <vlan> | include interfaces

2. Different leaves?
   → Routing lookup
   → Check: show ip route <destination>

3. BGP route exists but traffic fails?
   → Check for ACLs blocking
   → Check for spanning tree misconfiguration
   → Verify VLAN is routed (SVI exists)

4. Intermittent connectivity?
   → Check for packet loss (ECMP imbalance)
   → Check for MTU mismatch (jumbo frames vs standard)
   → Verify no link flapping
```

### Performance Issues

```
Slow VM-to-VM communication:

Checklist:
1. Check interface utilization:
   → show interface stats
   → If spine uplink > 85%, likely congestion

2. Check for errors:
   → show interface errors
   → Errors indicate physical problems
   → FCS errors: Cable issues
   → Late collisions: Speed mismatch

3. Latency high (>10ms):
   → Check hop count (should be 2 for leaf-to-leaf)
   → Verify ECMP load balanced (not all traffic 1 path)
   → Check for slower spine switch (performance issue)

4. Packet loss:
   → Check buffer utilization
   → Monitor drops on spines during peak
   → May need to reduce oversubscription
```

## Capacity Planning

```
Growth planning:

Current: 512 servers
Growth: 50% annually

Year 1: 768 servers (384 servers added)
  - Can fit with 2-tier design (1,536 leaf uplinks available)
  - No hardware changes needed

Year 2: 1,152 servers (576 servers added)
  - Approaching limit of 2-tier
  - Plan for 3-tier super-spine

Year 3: 1,728 servers (576 servers added)
  - Requires 3-tier implementation
  - Add 3-4 super-spine switches
  - Add 2-3 additional spine tiers

Timeline:
  - Monitor 3-tier requirements starting Month 12
  - Procurement lead time: 2-3 months
  - Implementation: 1-2 months
  - No production downtime (parallel build)
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Advanced
**Infrastructure:** Cisco, Arista, Juniper
