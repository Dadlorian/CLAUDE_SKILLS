# Network Overlay Design Guide

## Overlay Architecture Decision

### Single vs Multi-Tier Overlays

**Single Tier**:
```
VMs/Containers
    ↓
Logical Switch (VXLAN/Geneve)
    ↓
Physical Underlay Network
```
**Use**: Simple deployments, single data center

**Multi-Tier (Typical)**:
```
Pods/VMs (Tier 3)
    ↓
Logical Network (Tier 2) - VXLANs
    ↓
Logical Routers (Tier 2) - Inter-VNI routing
    ↓
Physical Underlay (Tier 1) - IP network
```
**Use**: Production, multi-tenant environments

---

## Underlay Design

### Underlay Network Requirements

```
Characteristics needed:
├─ IP reachability between all VTEPs
├─ MTU >= 1550 (to accommodate VXLAN overhead)
├─ Low latency (<50ms typical)
├─ High availability (redundant paths)
├─ Sufficient bandwidth (at least 2x overlay requirement)
└─ Quality stability (low jitter, low loss)
```

### Underlay Topology Options

**Simple Flat**:
```
VTEP-A ←→ Router ←→ VTEP-B
     └────────────────┘
```
- Easiest to manage
- Suitable for small deployments
- Single point of failure

**Redundant**:
```
VTEP-A ←→ Router-1 ←→ VTEP-B
  └─────────┬──────────┘
            Router-2
```
- N+1 redundancy
- Recommended for production

**Spine-Leaf (Best Practice)**:
```
     Spine-1       Spine-2
       ├─┬─────────┬─┤
       │ │         │ │
    VTEP1 VTEP2 VTEP3 VTEP4
```
- Non-blocking fabric
- Equal-cost paths
- Scales well

### Underlay IP Planning

```
Allocation Scheme:
├─ Loopback (VTEP source IP)
│  └─ 10.0.0.0/24 (one per VTEP)
├─ Point-to-point links
│  └─ 10.1.0.0/22 (p2p subnets)
├─ Management
│  └─ 10.2.0.0/24 (out-of-band)
└─ Overlay
   └─ 10.100.0.0/16 (tenants)

Example:
VTEP-A Loopback: 10.0.0.1
VTEP-B Loopback: 10.0.0.2
VTEP-C Loopback: 10.0.0.3
```

---

## Overlay Network Design

### VNI Planning

```
VNI Allocation:
├─ System/Management: 1-99
│  ├─ 10: Out-of-band management
│  ├─ 20: Infrastructure services
│  └─ 30: Monitoring
├─ Tenant-A: 100-199
│  ├─ 101: Production VLANs
│  ├─ 110: Development VLANs
│  └─ 120: Testing VLANs
├─ Tenant-B: 200-299
│  ├─ 201: Production
│  └─ 210: Development
└─ Tenant-C: 300-399
```

### Segment (L2) Design

```
Logical Network Structure:
├─ VXLAN 1001 (Tenant-A Prod)
│  ├─ Subnet: 10.100.0.0/24
│  ├─ Gateway: 10.100.0.1/24
│  ├─ VTEP Endpoints: VTEP-A, VTEP-B (dual-homing)
│  └─ Security: DFW rules per EPG
├─ VXLAN 1002 (Tenant-A Dev)
│  ├─ Subnet: 10.101.0.0/24
│  └─ Similar structure
└─ VXLAN 2001 (Tenant-B Prod)
```

### Endpoint Density

```
VTEP Capacity Planning:
├─ MAC addresses per VNI: 1000s
├─ VNIs per VTEP: 100-500 (varies by switch)
├─ Total endpoints: VTEP capacity × VNI density
└─ Reserve capacity: Plan for 30% growth
```

---

## Gateway and Routing Design

### Local Gateway (Distributed)

```
VM in Vlan 1001 (10.100.0.10)
    ↓ (needs IP 10.101.0.20 in Vlan 1002)
Hypervisor Router (Distributed)
    ↓ (looks up destination VNI)
VXLAN 1002
    ↓ (forwards to target VM)
Target VM (10.101.0.20)
```

**Advantages**:
- Low latency (no central device)
- Scalable (distributed)
- Symmetric paths

**Configuration**:
```
Logical Router
├─ Interfaces
│  ├─ VXLAN 1001: 10.100.0.1/24
│  └─ VXLAN 1002: 10.101.0.1/24
├─ Routes
│  ├─ 10.100.0.0/24 → VXLAN 1001
│  └─ 10.101.0.0/24 → VXLAN 1002
└─ Enables routing between segments
```

### External Gateway (Centralized)

```
Multi-Site or External Connectivity:
┌─────────────────────────────────────┐
│ Tenant Network                       │
│ (VXLAN 1001, 10.100.0.0/24)        │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │ Edge Gateway│  (Cisco ASA, NSX Edge, etc.)
        └──────┬──────┘
               │
        ┌──────▼──────────────┐
        │ External Network    │
        │ (LAN, Internet, DC) │
        └─────────────────────┘
```

**Use Cases**:
- NAT for external connectivity
- Service insertion (firewall, LB)
- MPLS/BGP peering
- Legacy network integration

---

## High Availability Design

### VTEP Redundancy

**Dual VTEP (Active-Active)**:
```
VM with dual vNICs
├─ vNIC-1 → VTEP-A
├─ vNIC-2 → VTEP-B
└─ Both active simultaneously (load balance)
```

**Active-Passive**:
```
VM with single vNIC
├─ Primary: VTEP-A
└─ Failover: VTEP-B (if VTEP-A fails)
```

### VNI Availability

```
Primary VTEP   Backup VTEP
(VTEP-A)       (VTEP-B)
    ├───────────┤
    VXLAN 1001 (replicated)
    Endpoints can reach via either VTEP
```

---

## Control Plane Design

### Multicast-Based (Simple)

```
Configuration:
├─ VXLAN 1001 → Multicast group 224.1.1.1
├─ VXLAN 1002 → Multicast group 224.1.1.2
└─ VTEPs join multicast groups

Behavior:
├─ Unknown unicast: Flooded via multicast
├─ Broadcast: Flooded via multicast
├─ MAC learning: Dynamic from received traffic
└─ Requires: Multicast routing in underlay
```

### BGP EVPN-Based (Recommended)

```
Architecture:
├─ Spine: Route Reflector
│  ├─ No data plane traffic
│  └─ Acts as BGP server
└─ Leaf (VTEP): eBGP peer
   ├─ Advertises local MACs
   ├─ Learns remote MACs from BGP
   └─ Unicast or replication only

Advantages:
├─ Better control over forwarding
├─ Faster convergence
├─ Scalable (doesn't require multicast)
├─ Standards-based (no vendor lock-in)
└─ Supports IRB (routing) natively
```

### BGP EVPN Configuration

```
Spine (Route Reflector):
router bgp 65000
  address-family l2vpn evpn
    neighbor 10.0.0.1 activate
    neighbor 10.0.0.2 activate
    neighbor 10.0.0.3 activate

Leaf (VTEP):
router bgp 65000
  address-family l2vpn evpn
    neighbor 10.0.1.1 activate
    neighbor 10.0.1.2 activate
    advertise-all-vni
    default-information originate
```

---

## Design Examples

### Example 1: Small Data Center Overlay

```
Requirements:
├─ 100 servers
├─ 5 tenants
├─ Single data center
└─ VXLAN-based

Design:
├─ 2 VTEPs (top-of-rack on each rack)
├─ Multicast for control plane
├─ Per-tenant VXLAN (5 total)
├─ 20-30 servers per tenant
└─ Simple topology (VTEP A & B connected)

Benefits:
├─ Low cost (only 2 VTEPs)
├─ Easy to manage (small scale)
└─ Meets capacity requirements
```

### Example 2: Large Data Center Overlay

```
Requirements:
├─ 5000 servers
├─ 20 tenants
├─ High availability required
└─ Multi-pod data center

Design:
├─ Spine-Leaf topology
│  ├─ 4 Spine switches (VXLAN-capable)
│  └─ 40 Leaf switches (dual uplink)
├─ Every leaf is a VTEP
├─ BGP EVPN control plane
│  └─ Spines as route reflectors
├─ 20 VNIs (one per tenant)
├─ Distributed gateways (per leaf)
└─ External edge routers for NAT/peering

Scaling:
├─ Non-blocking fabric
├─ 250 servers per leaf
├─ Each tenant spans multiple leaves
└─ Scales to 10K+ servers
```

### Example 3: Multi-Site Overlay

```
Requirements:
├─ 3 data centers
├─ Stretched VNI across sites
├─ Low inter-site latency requirement
└─ Avoid replicating traffic between sites

Design:
├─ Each DC has local VXLAN 1001
├─ BGP EVPN across sites
├─ Type 2 routes distributed between DCs
│  └─ Learning optimized per site
├─ Inter-DC gateway for routing
│  ├─ SF → NYC → LA
│  └─ Uses MPLS or direct uplink
└─ Type 5 routes for external destinations

Benefits:
├─ Efficient inter-site traffic
├─ Transparent to VMs (same VXLAN)
├─ Automatic failover between sites
└─ Maintains locality
```

---

## Overlay Performance Tuning

### MTU Optimization

```bash
# Validate MTU throughout path
ip link show  # Check local MTU

# Test with different sizes
ping -M do -s 1472 <remote_vtep>  # Should work if MTU 1550+
ping -M do -s 1500 <remote_vtep>  # May fail with standard MTU

# Configure jumbo frames
Cisco:  mtu 1600
Linux:  ip link set eth0 mtu 1600
VMware: portgroup MTU setting
```

### BUM Optimization

```
Broadcast/Unknown Multicast Handling:
├─ Multicast mode: Uses multicast (requires multicast infra)
├─ Replication: VTEP sends unicast to all VTEPs (CPU cost)
└─ Hybrid: Dynamic selection based on destination

Optimization:
├─ Minimize ARP flooding (use static entries)
├─ Suppress BUM for known destinations
├─ ARP cache/proxy to reduce requests
└─ Limit broadcast domains (per VNI)
```

---

## Troubleshooting Overlay Design

### Issue: Suboptimal Paths

```
Symptom: Traffic between same DC goes through spine unnecessarily

Analysis:
├─ Check VTEP placement
├─ Verify MAC learning (is destination reachable?)
├─ Monitor MTU along path

Solution:
├─ Place VTEPs on leaf where endpoints exist
├─ Use BGP EVPN for efficient destination learning
├─ Enable proxy ARP to reduce flooding
└─ Monitor and adjust VNI placement
```

### Issue: High Latency

```
Symptom: Overlay latency > 10ms when underlay < 5ms

Root Causes:
├─ Encapsulation overhead (5-10%: normal)
├─ Multicast flooding (check multicast latency)
├─ VTEP CPU (high processing delay)
├─ MTU fragmentation (check MTU)

Solutions:
├─ Hardware offload encapsulation
├─ BGP EVPN to reduce BUM traffic
├─ Optimize VTEP placement
└─ Increase physical bandwidth
```

---

## Design Best Practices

### Planning
- **Future growth**: Allocate VNI/subnet space for 3-5 year growth
- **Tenant isolation**: Separate VNI per tenant minimum
- **Redundancy**: Design N+1 minimum for production
- **Testing**: Validate design in simulation before deployment

### Implementation
- **Pilot**: Start small (test data center)
- **Phase rollout**: Gradual expansion
- **Monitoring**: Track overlay metrics from day 1
- **Documentation**: Keep design doc updated

### Operations
- **Automation**: Automate overlay provisioning
- **Monitoring**: Real-time overlay health
- **Capacity**: Track VNI/VTEP utilization
- **Optimization**: Regular performance review

### Scaling
- **Know limits**: VTEP capacity, VNI limits
- **Growth planning**: When to add VTEPs/VNIs
- **Regional design**: Separate overlays per region
- **Federation**: Multi-region coordination

---

## Detailed Design Worksheet

```
Overlay Design Template:

Requirement Analysis:
├─ Number of servers: ___
├─ Number of tenants: ___
├─ Growth projection (3yr): ___
├─ Geographic scope: ___
└─ High availability: Y / N

Underlay Design:
├─ Topology: ☐ Flat ☐ Redundant ☐ Spine-Leaf
├─ Uplink bandwidth: ___ Gbps
├─ MTU configuration: ___ bytes
└─ Latency target: ___ ms

Overlay Design:
├─ Technology: ☐ VXLAN ☐ Geneve ☐ Other
├─ Control plane: ☐ Multicast ☐ BGP EVPN
├─ VTEP count: ___
├─ VNI allocation: Start___ End___
└─ Gateway mode: ☐ Distributed ☐ Centralized

High Availability:
├─ VTEP redundancy: ☐ None ☐ Active-Passive ☐ Active-Active
├─ Gateway redundancy: ☐ Single ☐ N+1 ☐ N+M
└─ Recovery time target: ___ minutes

Performance Targets:
├─ Throughput per VNI: ___ Gbps
├─ Latency SLA: ___ ms
├─ Availability: ___% (nines)
└─ Convergence time: ___ seconds
```
