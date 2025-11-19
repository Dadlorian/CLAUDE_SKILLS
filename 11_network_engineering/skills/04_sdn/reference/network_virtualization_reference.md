# Network Virtualization Reference

## Definition
Network virtualization abstracts physical network resources to create multiple independent logical networks on shared infrastructure, enabling multi-tenancy and agile service delivery.

## Core Concepts

### Logical vs Physical Networks
```
Physical Infrastructure:
├─ Switches
├─ Routers
├─ Cables
└─ Servers

Logical Networks (on top):
├─ Tenant-A VLAN 101
├─ Tenant-B VLAN 201
├─ Tenant-C VLAN 301
└─ Shared Services VLAN 401
```

### Key Benefits
- **Multi-Tenancy**: Multiple isolated networks on single infrastructure
- **Agility**: Fast provisioning of new networks
- **Scalability**: Decoupled from physical limitations
- **Portability**: Virtual networks move with workloads
- **Efficiency**: Optimized resource utilization

## Network Virtualization Technologies

### 1. VLAN (Traditional)
**Scope**: Single data center, Layer 2 isolation
**Limitation**: 4094 VLANs maximum
**Use**: Legacy enterprise networks
**State**: Mature, well-established

### 2. VXLAN (Modern Overlay)
**Scope**: Multi-site, global scale
**Capability**: 16M virtual networks
**Use**: Cloud, modern data centers
**State**: Industry standard for overlays

### 3. Geneve (Generic Network Virtualization Encapsulation)
**RFC**: 8926
**Flexibility**: Variable-length option headers
**Advantages**: More extensible than VXLAN
**Status**: Emerging, gaining adoption

### 4. Segment Routing (SR)
**Concept**: Network processing encoded in packet header
**Benefit**: Simplified operations, traffic engineering without RSVP
**Scope**: Intra-domain and inter-domain routing
**State**: Standardized, being deployed

### 5. SRv6 (Segment Routing for IPv6)
**RFC 8754**: SRH (Segment Routing Header) in IPv6
**Advantage**: Native IPv6 traffic engineering
**Use**: Greenfield deployments, modern infrastructure
**State**: Early adoption

### 6. Service Function Chaining
**Concept**: Dynamic service insertion into traffic flows
**Use**: Security services, load balancing, optimization
**Protocol**: NSH (Network Service Header)

## Network Virtualization Models

### Traditional VLAN Model
```
Infrastructure
├─ VLAN 10 (HR)
├─ VLAN 20 (Finance)
├─ VLAN 30 (Engineering)
└─ Trunk links between switches

Limitations:
- Layer 2 boundary at switch
- Cannot scale beyond data center
- Complex spanning tree
```

### Overlay Network Model
```
Underlay (Physical Network)
├─ Spine switches
├─ Leaf switches
├─ Standard IP routing

Overlay (Logical Networks)
├─ VXLAN Segment A
├─ VXLAN Segment B
├─ VXLAN Segment C
└─ Independent of physical topology
```

### Segment Routing Model
```
Underlay:
├─ Node Segment IDs (labels per router)
├─ Adjacency Segment IDs (labels per link)
└─ Standard IGP (ISIS, OSPF)

Overlay (Traffic Engineering):
├─ Explicit paths as SID lists
├─ Dynamic path computation
└─ No per-flow state on routers
```

## Data Plane Virtualization

### vSwitch Technology
**Open vSwitch (OVS)**: Linux-based virtual switch
```
Physical NIC
    ↓
    └─→ OVS
        ├─ Bridge br0
        │  ├─ Port eth0 (physical)
        │  ├─ Port vnet0 (VM1)
        │  └─ Port vnet1 (VM2)
        └─ Flow tables
```

**DPDK Acceleration**: Data Plane Development Kit
- Kernel bypass for performance
- 10+ Gbps per CPU core possible
- OVS with DPDK for high throughput

### Container Networking
**CNI (Container Network Interface)**: Kubernetes network plugin standard
```
Kubernetes
├─ CNI Plugin
│  ├─ Calico (BGP-based)
│  ├─ Flannel (VXLAN/UDP)
│  ├─ Weave (VXLAN)
│  ├─ Cilium (eBPF-based)
│  └─ Multus (multiple networks)
└─ Pods connected via CNI
```

## Control Plane Virtualization

### Distributed Control Plane
**Concept**: Control logic distributed across multiple controllers
```
ONOS Cluster
├─ Node 1 (Leader)
├─ Node 2 (Follower)
└─ Node 3 (Follower)

Synchronization:
└─ Consensus protocol (RAFT, Paxos)
```

### Hierarchical Control
```
Regional Controllers
    ├─ Controller-1 (Region-A)
    ├─ Controller-2 (Region-B)
    └─ Controller-3 (Region-C)
        ↓
    Master Controller
        ↓
    Applications
```

## Management Virtualization

### Intent-Based Management
**Traditional**: Administrator specifies "how" (configure device)
**Intent-Based**: Administrator specifies "what" (desired state)

```
Traditional:
Admin → Device Config → Specific settings on each device

Intent-Based:
Admin → "Isolate Tenant A traffic" → System translates to policies
```

### Policy-Based Virtualization
- Centralized policy definition
- Automatic translation to device configurations
- Dynamic policy enforcement
- Audit and compliance tracking

## Service Chaining

### Network Services
```
User Traffic
    ↓
[Firewall] → [IDS] → [Load Balancer] → [NAT] → [Destination]
```

### NSH (Network Service Header) - RFC 8300
**Purpose**: Service function path identification
**Components**:
- Service Path Identifier (SPI): 24-bit path ID
- Service Index (SI): 8-bit hop counter
- Context Headers: Custom data per service

### Implementation Methods
1. **Physical**: Manual chaining with routing
2. **Overlay**: Encapsulation-based (NSH)
3. **Underlay**: SR-based path engineering

## Security Virtualization

### Microsegmentation
**Concept**: Granular network isolation per workload
```
Traditional Firewall:
┌─────────────────────┐
│  Firewall          │
│  Server Network    │
│  ├─ VM1            │ All internal = trusted
│  ├─ VM2            │
│  └─ VM3            │
└─────────────────────┘

Distributed Firewall:
VM1 ═══════╦═══════ VM3
           ║
          DFW        VM2 can't talk to VM1 even on same network
           ║
          VM2
```

### Zero-Trust Architecture
**Principle**: Verify every connection regardless of location
```
1. User/Device
2. Authentication (identity verification)
3. Authorization (permission check)
4. Encrypted Tunnel
5. Continuous Monitoring
6. Access grant/deny
```

## Performance Implications

### Throughput Impact
- **Hardware Offload**: <1% impact
- **Software Implementation**: 10-20% reduction
- **Encryption Overhead**: 10-30% depending on algorithm

### Latency Impact
- **Encapsulation**: 1-5 microseconds
- **Policy Lookup**: 1-10 microseconds
- **Buffer Operations**: < 1 microsecond

### CPU Utilization
- **40% per core**: ~10 Gbps (software)
- **5% per core**: ~100 Gbps (hardware offload)

## Network Virtualization at Scale

### Multi-Site Deployments
```
Data Center A          WAN            Data Center B
├─ Tenant-A           ════           ├─ Tenant-A
├─ Tenant-B    (L3 Underlay)        ├─ Tenant-B
└─ Shared      (VXLAN/Geneve)       └─ Shared
```

### Considerations
- Underlay MTU (jumbo frames recommended)
- WAN optimization
- Consistent policies across sites
- High availability of control plane

## Emerging Technologies

### Segment Routing PE (SRv6)
- Simplifies service chaining
- No separate NSH header
- Integrated with IPv6

### P4 Programmable Data Planes
- User-defined packet processing
- Fine-grained traffic steering
- Custom encapsulation

### eBPF-Based Networking
- Kernel-native programmability
- Low-latency policy enforcement
- Container and serverless support
