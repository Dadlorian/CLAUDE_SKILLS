# Data Center Fabric Designs

## Introduction
Data center fabric designs optimize east-west traffic patterns and provide scalable, non-blocking architectures for modern cloud infrastructure.

## Spine-and-Leaf (Clos) Architecture

### Design Principles

```
Core Concepts:
1. All traffic between servers goes through exactly 2 hops (leaf + spine)
2. Equal-Cost Multi-Path (ECMP) routing across all spine switches
3. Non-oversubscribed (for typical server/storage patterns)
4. Uniform hop count regardless of spine choice
5. Scales from 2-layer to N-layer Clos fabrics

Benefits over traditional architecture:
Traditional 3-tier: Server can take 5-7 hops to reach another server
Clos fabric: Server always takes 2 hops to reach another server
```

### Two-Tier Clos Topology

```
Typical Small Data Center (8 Spines, 64 Leaves):

        Spine Layer
     ┌──┬──┬──┬──┬──┬──┬──┬──┐
     S1 S2 S3 S4 S5 S6 S7 S8
     └─┬┼┬┼┬┼┬┼┬┼┬┼┬┼┬┼┬┼┬┼┬┼┐
       │├┤├┤├┤├┤├┤├┤├┤├┤├┤├┤├┤│
       │└┘└┘└┘└┘└┘└┘└┘└┘└┘└┘└┘│
       │                       │
    ┌──┴────────────────────────┴───┐
    │                               │
 ┌──────────────┐             ┌──────────────┐
 │Leaf Switches │   ...       │Leaf Switches │
 │(1-32)        │             │(33-64)       │
 └──────────────┘             └──────────────┘
    │    │                       │    │
    ├─┬──┤                       ├─┬──┤
    │ │  │                       │ │  │
  Server Pod 1               Server Pod 32

Pod Configuration (typical):
  - 64 physical servers per leaf switch
  - 25-40 Gbps interface per server
  - Each server has single connection to leaf
  - Servers reach any other server via 2 hops (leaf + spine)

Bandwidth calculation:
  - Per leaf: 64 servers × 25G = 1,600 Gbps downlink
  - Per leaf uplinks: 8 spines × 100G = 800 Gbps
  - Oversubscription: 1,600 / 800 = 2:1
  - Server bandwidth: 25G each (East-West: 50Gbps max)
```

### Three-Tier Clos Topology

```
Super-Spine Layer (Top of Fabric)
           ┌──┬──┬──┐
           │T1│T2│T3│
           └──┴──┴──┘
             ↑   ↑   ↑
   ┌────────┼───┼───┼────────┐
   │        │   │   │        │
  Spine1  Spine2...        Spine32
   │ │      │ │ │ │        │ │
   ├─┼──────┼─┼─┼─┼────────┼─┤
   │        │ │ │ │        │
  Leaf Switches (256 total)
   │  │    │  │ │  │    │   │
 ┌──────┐ ┌──────┐     ┌──────┐
 │Servers│ │Servers    │Servers
 └──────┘ └──────┘     └──────┘

Scaling example:
- 256 leaf switches × 64 servers = 16,384 servers
- 32 spine switches for aggregation
- 3 top-of-fabric switches for inter-pod connectivity

Pod count: 8 logical pods (32 leaves per pod)
Pod-to-pod throughput: Via Top-of-Fabric spines
Convergence domain: One pod autonomous
Failure isolation: Pod independent
```

### Pod-Based Design

```
Data Center divided into Logical Pods:

Pod-1: Customers A, B (Leaves 1-4)
  - Subnet: 10.100.0.0/18
  - Spines: Local (Spine 1-8)
  - Servers: 256

Pod-2: Customer C (Leaves 5-8)
  - Subnet: 10.100.64.0/18
  - Spines: Local (Spine 1-8)
  - Servers: 256

Pod-3: Shared Services (Leaves 9-12)
  - Subnet: 10.100.128.0/18
  - Spines: Local (Spine 1-8)
  - Services: NTP, DNS, DHCP, NMS, Backup

Inter-Pod Communication:
  Pod-1 Server → Top-of-Fabric Spine → Pod-2 Spine → Pod-2 Leaf → Server

Advantages:
- Failure isolation (network issues in Pod-1 don't affect Pod-2)
- Independent scaling (can add more pods)
- Separate billing (multi-tenant)
- Reduced broadcast domain
```

## Routing in Data Center Fabrics

### BGP Configuration

```
Typical BGP configuration for Spine-Leaf:

Numbering Scheme:
  Spines: Loopback 10.255.1.1 - 10.255.1.32 (ASN 65000)
  Leaves: Loopback 10.255.2.1 - 10.255.2.256 (ASN varies per rack)

Leaf Configuration:
  router bgp 65101
    neighbor 10.255.1.0 remote-as 65000
    neighbor 10.255.1.1 remote-as 65000
    neighbor 10.255.1.2 remote-as 65000
    !
    address-family ipv4 unicast
      neighbor 10.255.1.0 route-reflector-client
      neighbor 10.255.1.1 route-reflector-client
      neighbor 10.255.1.2 route-reflector-client
      !
      network 10.100.0.0 mask 255.255.0.0
      !
      maximum-paths 64

ECMP Load Distribution:
  - Hash function: (SrcIP, DstIP, SrcPort, DstPort) % spine_count
  - Per-flow load balancing
  - All spines equally utilized
  - Convergence time: <3 seconds (BGP failover)
```

### Link-Local Addressing

```
Modern DC design uses link-local addressing with BGP:

Leaf-01 to Spine-01:
  Leaf side: 169.254.1.1/31 (unnumbered, BGP over IPv6)
  Spine side: 169.254.1.0/31

Leaf-01 to Spine-02:
  Leaf side: 169.254.1.3/31
  Spine side: 169.254.1.2/31

BGP Configuration (IPv6):
  router bgp 65101
    address-family ipv6 unicast
      neighbor fe80::1%eth1 remote-as 65000
      neighbor fe80::2%eth2 remote-as 65000
      !
    !

Benefits:
- Reduced IPv4 space usage
- Automatic link-local generation
- Standard for modern DC fabrics
```

## Oversubscription and Bandwidth Planning

### Oversubscription Ratio

```
Definition: (Downlink capacity) / (Uplink capacity)

Example 1: 64 servers per leaf, 25G each
  Downlink: 64 × 25G = 1,600 Gbps
  Uplinks: 8 × 100G = 800 Gbps
  Ratio: 1,600 / 800 = 2:1 (2 to 1 oversubscription)
  Interpretation: All servers can't simultaneously max out uplinks

Example 2: Higher density servers (100G each)
  Downlink: 32 × 100G = 3,200 Gbps
  Uplinks: 8 × 100G = 800 Gbps
  Ratio: 3,200 / 800 = 4:1
  Interpretation: 4 servers max out 1 spine connection

East-West Traffic Consideration:
  Non-blocking (1:1) is expensive but necessary for:
  - Real-time applications
  - HPC/AI workloads
  - Large data transfers
  - Database replication
```

### Typical Oversubscription Ratios

```
Ratio Type | Configuration | Use Case | Cost |
-----------|---------------|----------|------|
Non-blocking (1:1) | Equal up/down | HPC, Real-time | Very High |
2:1 | 2 down per 1 up | Enterprise | High |
4:1 | 4 down per 1 up | Web, General | Medium |
8:1 | 8 down per 1 up | Batch, Test | Low |

Recommendation:
- Measure actual traffic patterns (East-West %)
- Size for peak expected traffic
- Plan for 30% growth
- Use 2:1 or 3:1 for production
```

## Fabric Implementation Options

### Spine-Leaf Platforms

**Cisco Nexus 9500-GX Series:**
```
Spine Switch (9508):
  - 288 x 100G interfaces (or 144 x 400G)
  - Throughput: 25.6 Tbps
  - Latency: <500ns
  - Power: 25 kW
  - Price: $400,000-$600,000

Leaf Switch (9364C):
  - 48 x 100G interfaces
  - Throughput: 19.2 Tbps
  - Latency: <500ns
  - Power: 8 kW
  - Price: $250,000-$350,000
```

**Arista 7368SX:**
```
Spine/Leaf capable:
  - 32 x 100G + 8 x 400G
  - Throughput: 12.8 Tbps
  - Latency: <400ns
  - Power: 4.5 kW
  - Price: $200,000-$300,000
```

**Juniper QFX10002-72Q:**
```
Leaf switch:
  - 72 x 100G QSFP interfaces
  - Throughput: 14.4 Tbps
  - Latency: <500ns
  - Power: 8 kW
  - Price: $300,000-$400,000
```

## Multi-Pod and Multi-Tier Designs

### Multi-Pod Architecture

```
Multiple Independent Data Centers:

DC-A (US-East):
  - Spine-Leaf fabric
  - 512 servers
  - Pod 1-4

DC-B (US-West):
  - Spine-Leaf fabric
  - 512 servers
  - Pod 5-8

Interconnection:
  DC-A Core Router ←100G Dark Fiber→ DC-B Core Router
         │                               │
    Multi-layer router (Layer 3)    Multi-layer router
         │                               │
    Data synchronization:
    - Active-Active replication
    - BGP for dynamic failover
    - Heartbeat monitoring

Latency requirements:
  - Intra-DC: <1ms (local spine-leaf)
  - Inter-DC: <10ms (preferred)
  - Acceptable: <50ms (with replication protocols)
```

### Collapsed Core Design

```
For smaller data centers (<500 servers):

Collapse core and spine functions:

  Core/Spine Layer (4 switches)
  ┌────────────────────────────┐
  │  Collapsed Spine (12x100G) │
  │  + Core routing (BGP)      │
  └────────────────────────────┘
         ↑  ↑  ↑  ↑
         │  │  │  │
  ┌──────┴──┴──┴──┴────────┐
  │     Leaf Switches      │
  │  (32 servers each)     │
  └────────────────────────┘
    │  │  │  │  │
 Servers...

Benefits:
- Lower cost (4 vs 40+ switches)
- Still supports ECMP
- Still provides 2-hop latency
- Limitations: Lower throughput, less scalability
```

## Overlay Networks

### VXLAN Fabric Design

```
Virtual eXtensible LAN for logical networks:

Physical Fabric (Spine-Leaf):
  - IP routing between leaves
  - VLAN 1:1 not supported across pods
  - BGP for fabric routing

Virtual Overlay:
  - VXLAN creates L2 domains over L3
  - Tenant 1 VLAN 100 → VXLAN VNI 10100
  - Tenant 2 VLAN 100 → VXLAN VNI 10200
  - Same VLAN ID, different VNIs
  - Complete isolation

Configuration (on Leaf):
  interface Vlan 100
   vn-segment 10100

  evpn-gateway ip routing

  interface nve1
   no shutdown
   source-interface Loopback0
   member L3 associate vrf Tenant1
    vni 50001
   member L2
    vni 10100 associate-vrf

Benefits:
- Multitenant networks
- Flexible VLAN numbering
- Transparent workload mobility
- Network virtualization
```

## Design Selection Criteria

| Criteria | Clos | Collapsed | Multi-Tier |
|----------|------|-----------|-----------|
| Max servers | 16,384+ | 512 | 4,096 |
| Cost per server | Medium | Low | High |
| Latency | <1ms | <1ms | 1-5ms |
| Oversubscription | 1:1 to 8:1 | 2:1 to 4:1 | 4:1 to 16:1 |
| Complexity | High | Low | High |
| East-West optimized | Yes | Yes | No |
| Recommended for | Enterprise | Small | Legacy |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** RFC 7348 (VXLAN), Cisco, Arista, Juniper
