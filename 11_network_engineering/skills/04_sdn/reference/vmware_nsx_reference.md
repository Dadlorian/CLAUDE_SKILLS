# VMware NSX Reference

## Overview
NSX is VMware's network virtualization platform, providing comprehensive network and security services. NSX-T (NSX Transformers) is the modern version supporting multi-hypervisor and Kubernetes environments.

## NSX-T Architecture

### Components

#### NSX Manager
**Role**: Management and control plane
```
NSX Manager
├─ API Server (REST API)
├─ Policy Engine
├─ Configuration Management
└─ Clustering (3-node or HA)
```

#### NSX Controller Cluster
**Role**: Distributed control plane
```
NSX Controller Nodes (3 or 6)
├─ BUM (Broadcast/Unknown Unicast/Multicast) handling
├─ Logical switch control
├─ VNI assignment
└─ Multicast control
```

#### Transport Nodes
**Role**: Data plane (hypervisor and TOR switch)
- Hypervisor: N-VDS (NSX Virtual Distributed Switch)
- TOR: N-VDS plugin
- Bare Metal: NSX Virtual Adapter (NSX-VA)

```
Hypervisor (vSphere)
├─ vSAN
├─ N-VDS
│  ├─ Logical Switches
│  ├─ Logical Routers
│  └─ Traffic control
└─ VMs
```

#### NSX Edge
**Role**: Advanced services (routing, firewall, VPN, LB)
```
NSX Edge VM/Appliance
├─ Tier-0 Router (external connectivity)
├─ Tier-1 Router (tenant routing)
├─ Service Engines (Load balancing)
├─ VPN Server
└─ Firewall
```

## Network Virtualization

### Logical Switch (vSphere Distributed Switch)
```
Logical Switch
├─ MAC Learning (dynamic and static)
├─ VXLAN encapsulation (or Geneve)
├─ Flooding (multicast or replication)
└─ Attached Ports (VM virtual NICs)
```

**Configuration**:
- **VLAN Mode**: Native or trunk
- **MTU**: Must match underlay
- **Replication**: Multicast or Hybrid

### Logical Routers

#### Tier-0 Router
- **Role**: Default gateway for Tier-1 routers and external connectivity
- **Redundancy**: Active-Active or Active-Standby
- **Functions**: BGP, OSPF, static routing
- **Edge Nodes**: Must be deployed on edges

```
External Network ←→ Tier-0 Router ←→ Tier-1 Routers ←→ Logical Switches
```

#### Tier-1 Router
- **Role**: Tenant/application routing
- **Redundancy**: Active-Active (with Tier-0 failover)
- **Attachment**: To Tier-0 for external connectivity
- **DHCP**: Local DHCP relay capability

```
Tier-1-A
├─ Logical Switch A (10.0.1.0/24)
├─ Logical Switch B (10.0.2.0/24)
└─ Default GW to Tier-0
```

### Routing Protocols

**BGP Configuration**:
```
Tier-0 Router
├─ AS Number: 65001
├─ Neighbor: External Router (AS 65000)
├─ Route Redistribution
│  ├─ Connected subnets
│  ├─ Static routes
│  └─ Learned routes
└─ BFD for fast detection
```

## Distributed Firewall (DFW)

### Architecture
```
Hypervisor Kernel
├─ N-VDS
│  ├─ L4 Firewall Rules (kernel)
│  ├─ Logical Switch (forwarding)
│  └─ Logical Router (routing)
└─ VM
```

### Rule Structure
```
Rule
├─ Name
├─ Source (VMs, Security Groups, IPs, NSGs)
├─ Destination (VMs, Security Groups, IPs)
├─ Service (protocol/port)
├─ Action (Allow, Drop, Reject)
├─ Logging (enabled/disabled)
└─ Direction (In, Out, Intra-VM)
```

### Stateful Inspection
- **Connection Tracking**: Per-connection state
- **Timeout**: Configurable idle timeout
- **Asymmetric Filtering**: Separate rules for directions

### Security Groups
**Concept**: Dynamic EPG-like grouping
```
Security Group "Web Servers"
├─ Membership Rules (VM tag matching)
├─ Policy Association
└─ Dynamic membership

Rule: "Web-Servers" can access "DB-Servers" on TCP/3306
```

## Gateway Firewall

### Tier-0 Gateway Firewall
- North-South traffic control
- Stateful firewall rules
- NAT/DNAT capability

### Tier-1 Gateway Firewall
- Per-tenant traffic control
- Separation of concerns

## Load Balancing

### NSX Load Balancer
```
NSX Load Balancer
├─ Virtual Server (listens on IP:Port)
├─ Server Pool (backend servers)
├─ Health Monitors (active/passive checks)
└─ Load Balancing Algorithms
   ├─ Round Robin
   ├─ Least Connections
   ├─ IP Hash
   └─ Weighted
```

**Deployment**:
- **Service Engines**: Distributed across edges
- **Active-Active**: Scale horizontally

### Session Persistence
- Source IP
- Cookie-based
- Custom persistence

## VPN Services

### IPsec VPN
```
Site-A (NSX Edge)  ═══ IPsec Tunnel ═══  Site-B (NSX Edge)
Local Network     (Phase 1 & 2)         Remote Network
10.0.0.0/8                             172.16.0.0/8
```

### SSL VPN (L2TP/IPsec)
- Remote access capability
- User-based authentication
- VPN client requirement

## Container Networking

### Kubernetes Integration
```
Kubernetes Cluster
├─ NSX-NCP (Kubernetes plugin)
├─ Container Network Interface (CNI)
│  ├─ Pod IP allocation
│  ├─ Pod-to-Pod networking
│  └─ Service networking
└─ Pods (with NSX isolation)
```

**Features**:
- **Pod Security Policy**: NSX firewall enforcement
- **Microservice Isolation**: NSX DFW for pods
- **Ingress Networking**: NSX Load Balancer integration

## Advanced Features

### Tenant Isolation
```
Tenant-A              Tenant-B
├─ Tier-1 Router    ├─ Tier-1 Router
├─ Logical Switches ├─ Logical Switches
└─ DFW Rules        └─ DFW Rules
     ↓                  ↓
   Shared Tier-0 (no cross-tenant traffic)
```

### NSX Edges High Availability
```
Edge Cluster
├─ Edge Node 1 (Active)
├─ Edge Node 2 (Standby)
├─ Edge Node 3 (Standby)
└─ Shared Virtual IP (management)
```

### Performance Tuning
- **MTU**: Ensure underlay supports
- **CPU**: Allocate adequate resources
- **Monitoring**: Track edge utilization

## Multi-Site Deployments

### Federation
```
Site-A NSX      Federation Link      Site-B NSX
├─ Global Manager ←────────────→ Global Manager
├─ Local Manager                ├─ Local Manager
└─ Fabric                       └─ Fabric
```

**Features**:
- Stretched logical switches
- Stretched Tier-1 routers
- Local services per site
- Cross-site routing

### IP Prefixes
- Global VRF for inter-site traffic
- Site-local prefixes
- Overlapping address space support

## Deployments & Operations

### Deployment Steps
1. Deploy NSX Manager (3 appliances)
2. Configure Compute Managers (vCenter)
3. Deploy NSX Controllers (3 appliances)
4. Prepare Transport Nodes
   - Install N-VDS
   - Configure VLAN/MTU
5. Create Transport Zones
6. Deploy NSX Edges
7. Configure routing/security policies

### Scaling Considerations
- **Manager Cluster**: 3 for HA (supports 10K+ nodes)
- **Controller Cluster**: 3-6 nodes (1.8M VMs per 3 nodes)
- **Edges**: Scale horizontally for service chaining
- **Transport Nodes**: Add as infrastructure grows

## Performance Characteristics

### Throughput
- **Per Edge**: 5-40 Gbps (depending on model)
- **Distributed Firewall**: Line rate filtering
- **Load Balancer**: 10-100 Gbps aggregate

### Latency
- **Logical Switching**: Hypervisor level (<1ms)
- **Routing**: ECMP latency (< 5ms)
- **DFW**: Kernel-based filtering (<100us)

### Scalability
- **Logical Switches**: Thousands per deployment
- **Logical Routers**: Thousands per deployment
- **Firewall Rules**: Hundreds of thousands

## Troubleshooting

### Common Issues

#### Connectivity Issues
1. Check Transport Node status
2. Verify logical switch configuration
3. Confirm router attachment
4. Check DFW rules

#### Performance Degradation
1. Monitor CPU/Memory on edges
2. Check bandwidth utilization
3. Verify no packet loss
4. Review MTU configuration

#### Controller Issues
1. Check controller quorum
2. Verify clustering health
3. Check network connectivity
4. Review logs

### Tools
- NSX Manager UI
- REST API (curl/Postman)
- CLI on NSX appliances
- Log aggregation (syslog)

## Comparison with Other Solutions

| Feature | NSX-T | ACI | Contrail |
|---------|-------|-----|----------|
| Hypervisor Support | Multi (vSphere, KVM) | N/A | Multi |
| Control Plane | Distributed | Centralized | Distributed |
| Scale | Very High | High | High |
| DFW | Excellent | Good | Good |
| Container Native | Yes | No | Yes |
| Integration | VMware | Cisco | Juniper |
| Cost | Very High | High | Medium |

## Best Practices

### Design
- Plan segment (VLAN) layout
- Design Tier-0 redundancy
- Allocate Edge resources
- Document routing scheme

### Security
- Implement defense in depth
- Use Security Groups
- Enable DFW logging
- Separate north-south from east-west

### Operations
- Monitor edge utilization
- Regular controller backups
- Performance baselining
- Alert on anomalies

### Migration
- Pilot deployment
- Parallel run with legacy
- Gradual workload migration
- Rollback procedures
