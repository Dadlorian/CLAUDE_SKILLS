# Cisco ACI Reference

## Application Centric Infrastructure Overview

### Definition
Cisco Application Centric Infrastructure (ACI) is a software-defined networking architecture that places applications at the center of network policy.

### Core Tenets
1. **Application-First**: Policies defined around applications, not networks
2. **Hardware-Based Control**: Control plane on ASIC for performance
3. **Fabric-Based**: Spine-Leaf topology with uniform forwarding
4. **Policy-Driven**: All configuration as policy

## ACI Architecture

### Three-Tier Architecture
```
APIC (Application Policy Infrastructure Controller)
    ├─ Management Plane
    ├─ Control Plane
    └─ Analytics & Telemetry

    ↓

Spine Nodes (Border routers)
    ├─ Inter-pod connectivity
    ├─ External connectivity
    └─ Protocol processing

    ↓

Leaf Nodes (Access switches)
    ├─ VM/Container attachment
    ├─ vPC handling
    └─ Policy enforcement
```

### Cluster Requirements
- **APIC Cluster**: 1, 3, or 5 nodes (odd number for quorum)
- **Fabric**: Minimum 2 spine, 2 leaf (production: 3 spine, 4+ leaf)
- **Management**: Separate management network or in-band

## APIC (Application Policy Infrastructure Controller)

### Functions
- **Policy Management**: Define and manage all network policies
- **Device Management**: Manage all fabric nodes
- **Telemetry**: Collect statistics and health data
- **Multi-Tenancy**: Separate administrative domains
- **GUI & APIs**: Web UI and REST API

### High Availability
```
APIC Node 1 (Leader)
APIC Node 2 (Follower) ─── Heartbeat ─── APIC Node 3 (Follower)
        ↓
    Consensus Database (etcd-based)
```

### Redundancy Types
- **Active-Standby**: One APIC active, others standby
- **Active-Active** (N+N): Available in ACI 5.0+
- **Site Federation**: Multi-APIC coordination

## Fabric Topology

### Spine-Leaf Design
```
                Spines
           ┌─────┴─────┐
           │           │
        Spine1       Spine2
         ╱ │ ╲      ╱ │ ╲
        ╱  │  ╲    ╱  │  ╲
      L1  L2  L3  L4  L5  L6
      ├─ Leaf Nodes
      └─ VM/Container attachment
```

**Benefits**:
- Equal-cost path engineering
- Predictable latency
- Simplified troubleshooting
- Non-blocking fabric

### Link Aggregation
- **VPC (Virtual Port Channel)**: Dual-homing for redundancy
- **LACP**: Active lagging with MLAG semantics
- **Multi-NIC Load Balancing**: Traffic across all NICs

## Policy Model

### Policy Structure
```
APIC
├─ Tenant (Administrative domain)
│  ├─ Application Profile
│  │  ├─ Endpoint Groups (EPG)
│  │  │  └─ Endpoints (VMs, containers)
│  │  └─ Application Service (load balancing, etc.)
│  ├─ Network
│  │  └─ Bridge Domain
│  │     └─ Subnet
│  └─ Contracts (policies)
│     ├─ Subjects
│     └─ Filters
└─ Fabric (system configuration)
```

### Key Concepts

#### Tenant
- Isolated administrative and policy domain
- Contains applications, networks, contracts
- Multi-tenant support for service providers

#### Application Profile
- Collection of endpoint groups that work together
- VRF association
- Bridge domain assignment

#### Endpoint Group (EPG)
- Collection of endpoints with same policy
- VMs, containers, bare-metal servers
- Assigned to bridge domain

#### Contract
- Policy-driven communication rules
- Unidirectional (provider → consumer)
- Explicit allow (default deny)

**Components**:
```
Contract
├─ Subject (defines traffic rules)
│  ├─ Filters (packet match criteria)
│  │  ├─ Source/Dest IP
│  │  ├─ Port ranges
│  │  ├─ Protocol
│  │  └─ Action (permit/deny)
│  └─ Direction (one-way or bi-directional)
└─ Provider/Consumer (EPG binding)
```

#### Bridge Domain
- Layer 2 entity
- Associated subnet(s)
- VRF membership
- Flooding domain definition

#### VRF (Virtual Routing and Forwarding)
- Layer 3 routing domain
- Isolates routing tables
- Multiple per tenant

### Policy Resolution

**Example: Web Tier to DB Tier**
```
Web Tier EPG              DB Tier EPG
├─ VM1                    ├─ DB Server 1
└─ VM2                    └─ DB Server 2

Contract "Web-to-DB"
├─ Subject: Allow TCP/3306
├─ Provider: DB Tier EPG
└─ Consumer: Web Tier EPG

Result: Only traffic on TCP/3306 allowed
```

## Networking Constructs

### External Connectivity

#### Layer 3 Out
- External BGP/OSPF peering
- Static route summary
- Multi-site connectivity
```
L3Out
├─ Logical Node Profile
│  ├─ Interface profile
│  └─ BGP config
├─ External EPG
│  ├─ Subnets
│  └─ Contract association
└─ Route Control (import/export)
```

#### Layer 2 Out
- External VLAN connectivity
- Legacy network integration
- Same VRF fabric-wide

### Service Node Integration
- Load balancers
- Firewalls
- Proxy appliances

**Service Graph**: Define service function chain
```
EPG1 → Firewall → Load Balancer → EPG2
```

## Forwarding and Encapsulation

### VXLAN in ACI
- **VNI Assignment**: Based on EPG
- **VTEP**: Leaf nodes are VTEPs
- **BGP EVPN**: Control plane for MAC/IP distribution

### Traffic Forwarding
```
VM1 in EPG-A on Leaf1
    ↓
Leaf1 classifies packet to EPG-A (VXLAN VNI=123)
    ↓
Encapsulates with VXLAN header
    ↓
Routes to destination leaf via spines
    ↓
Destination leaf decapsulates and delivers to VM
```

### MTU Considerations
- Physical MTU: 1500 bytes
- VXLAN Overhead: ~54 bytes
- Recommended: Configure jumbo MTU 9216 bytes

## Multi-Site Deployments

### Multi-Site Architecture
```
Site-A (APIC-1)         Inter-Site Network         Site-B (APIC-2)
├─ Fabric-A ────────────────────────────────────── Fabric-B
└─ Shared Tenant Config via Multi-Site Orchestrator
```

### MP-BGP Routing
- EVPN between sites
- Stretch EPGs across sites
- Site-local failure independence

### Consistency
- Tenant/Contract/EPG replicated
- Site-specific overrides
- Eventual consistency model

## Advanced Features

### Microsegmentation
- **EPG-based**: Isolate by application
- **Contract-based**: Explicit policies
- **DFW Integration**: Additional filtering

### Load Balancing
- **Service Graph**: Chain load balancer
- **Internal Load Balancer**: ACI-native option
- **PBR (Policy-Based Routing)**: Redirect to load balancer

### Encryption
- **Static Keys**: Pre-shared encryption
- **EX (Encrypted eXchange)**: Auto-negotiated keys
- **IPsec**: Inter-site encryption

### Monitoring
- **Endpoint Tracking**: VM to EPG mapping
- **Contract Counters**: Per-contract statistics
- **Telemetry**: Streaming to external systems

## Deployment Models

### Greenfield
**Scenario**: New deployment
**Advantages**: Optimize for ACI, minimal legacy
**Approach**: Native VXLAN from start

### Brownfield
**Scenario**: Existing network + ACI
**Challenges**: Coexist with legacy VLANs
**Approach**: L2Out for legacy connectivity

### Hybrid
**Scenario**: Gradual migration
**Approach**:
1. Run in parallel
2. Migrate EPGs one by one
3. Phase out legacy devices

## Best Practices

### Tenant Organization
- Separate by customer/application
- Implement RBAC (Role-Based Access Control)
- Document tenant purpose

### Network Design
- Use consistent VRF scheme
- Plan subnetting for growth
- Design L3Out for redundancy

### Contract Design
- Start with most restrictive policies
- Use filters for reusability
- Implement exception processes

### Fabric Scale
- Monitor fabric load
- Scale leaf count, not spine
- Plan for 3-5 year growth

### High Availability
- Multi-node APIC cluster
- Multi-spine fabric
- Dual-homing for hosts
- NTP synchronization

## Troubleshooting

### Common Issues

#### Endpoint Not Attached
- Check EPG assignment
- Verify VLAN/VNI configuration
- Check interface policy

#### Traffic Not Flowing
- Verify contract exists
- Check filter configuration
- Confirm VRF association
- Review ARP entries

#### Policy Not Applied
- Confirm policy pushed from APIC
- Check leaf policy distribution
- Validate EPG in contract

### Tools
- APIC GUI (fabric viewer, topology)
- Leaf CLI (show commands)
- Cisco TAC tools
- Flow tracing utility

## Comparison with Other Solutions

| Aspect | ACI | NSX | Contrail |
|--------|-----|-----|----------|
| Control | Centralized (APIC) | Distributed | Distributed |
| Data Plane | VXLAN | NSX encapsulation | VXLAN |
| Scale | Excellent | Good | Good |
| Hardware | Cisco only | Multi-vendor | Multi-vendor |
| Policy Model | Contract-based | Rule-based | Route-based |
| Cost | High | Very High | Medium |
