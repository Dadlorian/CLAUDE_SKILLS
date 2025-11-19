# Network Fabric Comparison

## Overview
Comparison of modern network fabric architectures used in data centers and enterprise networks.

## Spine-Leaf Architecture

### Definition
Two-tier Clos topology with spine switches at core and leaf switches at access layer.

```
Spines (Border/Core)
    ┌───┬───┬───┐
    │S1 │S2 │S3 │
    └───┴───┴───┘
     │   │   │
   ┌─┼───┼───┼─┐
   │ │   │   │ │
  L1 L2  L3  L4 L5  (Leaves - Access)
   │  │   │   │  │
  VMs/Containers/Servers
```

### Characteristics
- **Path Count**: Multiple equal-cost paths (4-6 typical)
- **Latency**: Consistent (4 hops maximum)
- **Bandwidth**: No over-subscription (non-blocking)
- **Scaling**: Add leaves horizontally

### Advantages
- Predictable performance
- Equal-cost multipath (ECMP)
- Non-blocking fabric
- Scales to thousands of servers

### Disadvantages
- Higher spine port cost
- More complex topology
- All leaf-to-leaf traffic transits spine

### Use Cases
- Modern data center (best practice)
- Large-scale cloud deployments
- Enterprise fabric

---

## Traditional Three-Tier Architecture

### Structure
```
Core (Router)
      │
  ┌───┴───┐
  │       │
Dist-1  Dist-2  (Distribution)
  │       │
┌─┴─┐   ┌─┴─┐
│   │   │   │
A1  A2  A3  A4  (Access)
```

### Characteristics
- **Oversubscription**: 3:1 or 4:1 typical
- **Spanning Tree**: Complex STP topology
- **Latency**: Variable (depends on path)
- **Scaling**: Difficult, reshuffling required

### Advantages
- Familiar design pattern
- Legacy device support
- Existing skill set available

### Disadvantages
- Spanning tree bottleneck
- Oversubscribed uplinks
- Poor for multi-tenant environments
- Difficult to migrate to cloud-ready

### Use Cases
- Legacy enterprises
- Traditional data centers
- Networks in transition

---

## Fat Tree (Clos)

### Advanced Spine-Leaf
```
Core
├─ Tier 3: Aggregation (pods)
│  ├─ Tier 2: Modular leaf switches
│  └─ Tier 1: Top-of-rack switches
└─ All to all connectivity with equal costs
```

### Full Non-Blocking
- Theoretical: All ports can simultaneously forward
- Practical: With 48-port leaves, oversubscription ~1:1

### Scale
```
4 spines × 48 ports = 192 spine ports
Each spine connects to 48 leaves
Total leaves = 192
Total leaf ports = 192 leaves × 48 = 9,216 ports
```

---

## Full Mesh Architecture

### Concept
Every switch connects to every other switch

```
┌─ S1 ─┐
├─ S2 ─┤
├─ S3 ─┤ (each pair directly connected)
├─ S4 ─┤
└─ S5 ─┘
```

### Characteristics
- **Paths**: One direct path per pair
- **Latency**: Minimal (1 hop)
- **Complexity**: High (mesh complexity)
- **Scale**: Limited (N² connections)

### Use Cases
- Small fabrics (< 10 switches)
- Extreme latency-sensitive
- Small regional networks

---

## Modular/Pod Architecture

### Structure
```
Pod-1           Pod-2           Pod-3
├─ Local Spine  ├─ Local Spine  ├─ Local Spine
├─ Leaves       ├─ Leaves       ├─ Leaves
└─ Servers      └─ Servers      └─ Servers
      ↑              ↑                ↑
      └──────────────┴────────────────┘
         Inter-pod connectivity
```

### Benefits
- **Modularity**: Add pods independently
- **Resilience**: Pod failures isolated
- **Scaling**: Linear scaling with pods
- **Multi-tenancy**: Separate pods per tenant

### Use Cases
- Multi-tenant data centers
- Hyperscale cloud (Google, AWS patterns)
- Distributed data centers

---

## Comparison Matrix

| Aspect | Spine-Leaf | Three-Tier | Fat Tree | Full Mesh | Pod |
|--------|-----------|-----------|----------|-----------|-----|
| **Scalability** | Excellent | Poor | Excellent | Poor | Excellent |
| **Latency** | Consistent | Variable | Consistent | Best | Consistent |
| **Cost** | High (spines) | Lower | High | High | Medium |
| **Complexity** | Medium | Low | High | High | High |
| **Oversubscription** | 1:1 | 3:1-4:1 | 1:1 | None | 1:1 |
| **Operations** | Moderate | Simple | Complex | Complex | Complex |
| **Cloud Ready** | Yes | No | Yes | No | Yes |
| **Vendor Options** | Many | Most | Few | Few | Few |
| **Deployment Time** | Moderate | Fast | Slow | Slow | Long |

---

## Modern Data Center Designs

### Hyperscale Cloud Design (AWS/Google/Azure Pattern)
```
Region
├─ Availability Zone 1
│  ├─ Pod 1 (Spine-Leaf)
│  ├─ Pod 2 (Spine-Leaf)
│  └─ Pod N (Spine-Leaf)
│      ↓
│  Inter-Pod Switch
│      ↓
│  Regional Gateway
├─ Availability Zone 2
└─ Availability Zone 3
```

**Features**:
- ECMP throughout
- Massive scale (100k+ servers per region)
- Auto-scaling
- Fault isolation

### Enterprise Data Center Design (Cisco/VMware Pattern)
```
Two-Pod Architecture
├─ Pod-A (Spine-Leaf)
│  ├─ Spine 1, 2
│  └─ Leaves 1-8
│
├─ Pod-B (Spine-Leaf)
│  ├─ Spine 1, 2
│  └─ Leaves 1-8
│
├─ ACI/NSX Control
└─ Multi-site Gateway
```

**Features**:
- VXLAN overlay
- Multi-site stretch
- Microsegmentation
- Centralized policy

### Software-Defined Fabric (Arista/Juniper Pattern)
```
Fabric OS
├─ Centralized control
├─ Programmable forwarding
└─ Zero-touch deployment

Physical Topology
└─ Standardized hardware (whiteboxes or proprietary)
```

**Features**:
- GitOps for configuration
- Automated provisioning
- Intent-based policies
- Unified analytics

---

## Technology Integration

### Overlay Technologies
```
Physical Spine-Leaf Fabric
       ↓
   VXLAN/Geneve Overlay
       ↓
Logical Networks (VNI-based)
```

### Routing Protocols

#### BGP EVPN
- **Use**: Spine-leaf with VXLAN
- **Advantages**: Scalable, standard
- **BGP Sessions**: Each leaf peers with spines

#### ISIS
- **Use**: Traditional fabrics
- **Advantages**: Converges fast
- **Segment Routing**: Natural fit for SR

#### OSPF
- **Use**: Older deployments
- **Advantages**: Simple
- **Disadvantages**: Flooding overhead

---

## Migration Paths

### Legacy to Spine-Leaf
```
Phase 1: Parallel Operation
├─ Deploy new spine-leaf
├─ Migrate workloads gradually
└─ Keep legacy running

Phase 2: Transition
├─ Move critical applications
├─ Test thoroughly
└─ Maintain fallback

Phase 3: Decommission
├─ Turn off legacy
├─ Recycle hardware
└─ Document lessons learned
```

### Three-Tier to Spine-Leaf
**Challenge**: All traffic flows changing
**Solution**:
1. East-West traffic first
2. North-South traffic gradually
3. Full transition during maintenance window

---

## Performance Characteristics

### Throughput
- **Spine-Leaf**: Full line rate per tier (no over-subscription)
- **Three-Tier**: Limited by oversubscribed uplinks
- **Fat Tree**: Similar to spine-leaf

### Latency
- **Spine-Leaf**: 5-10 microseconds L2, +IP processing
- **Three-Tier**: Variable (depends on tree depth)
- **Direct Paths**: < 5 microseconds possible

### Convergence
- **BGP EVPN**: 1-3 seconds
- **ISIS**: < 1 second
- **Spanning Tree**: 30+ seconds (unacceptable)

---

## Design Considerations

### Port Count Selection
```
How many servers?
    ├─ < 100: Single spine-leaf
    ├─ 100-500: Small fabric (2-4 spines)
    ├─ 500-5000: Medium fabric (4-8 spines)
    └─ 5000+: Large fabric (8+ spines, multiple pods)
```

### Redundancy Strategy
```
No redundancy: Not recommended (production)

Single redundancy: Dual path
├─ 2 spines (each leaf connects to both)
└─ Max downtime: 50% bandwidth loss

N+1 redundancy: Backup resources
├─ 3 spines (2 active, 1 spare)
└─ Survives 1 spine failure

N+2 redundancy: Extra capacity
├─ 4 spines (can lose 2)
└─ Maintains full capacity with 1 failure
```

### Bandwidth Planning
```
Per-Server Allocation
├─ Conservative: 1 Gbps uplink per server
├─ Standard: 10 Gbps uplink per 10-20 servers
├─ High-performance: 1:1 oversubscription or better
└─ Hyperscale: 1:1 (non-blocking)
```

---

## Fabric Comparison for SDN

| Fabric Type | Best SDN Fit | Control Plane | Scaling |
|------------|-------------|---------------|---------|
| **Spine-Leaf** | Excellent | OpenFlow/BGP EVPN | Excellent |
| **Three-Tier** | Poor | OpenFlow (not ideal) | Poor |
| **Fat Tree** | Excellent | BGP EVPN | Excellent |
| **Pod-based** | Excellent | BGP EVPN + local control | Excellent |

---

## Future Trends

### Disaggregation
- Hardware and OS separation
- White-box switches
- Third-party OS (ONOS, stratum)

### Programmability
- P4 (Packet programming)
- Telemetry (in-band)
- Intent-driven configuration

### AI/ML Integration
- Automatic fabric optimization
- Anomaly detection
- Predictive provisioning

### Zero-Touch Networking
- Automated discovery
- Self-configuration
- Self-healing
