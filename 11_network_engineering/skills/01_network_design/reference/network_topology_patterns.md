# Network Topology Patterns

## Introduction
Network topology patterns are proven architectural designs that address common networking challenges. These patterns provide blueprints for building scalable, resilient, and efficient networks.

## 1. Three-Tier Hierarchical Topology

### Core Layer
The core layer serves as the backbone of the network, providing high-speed connectivity between distribution nodes.

**Characteristics:**
- Ultra-high throughput (100 Gbps+)
- Minimal packet processing
- Redundant interconnections
- Cross-functional aggregate traffic
- Strategic node placement

**Technology:**
```
Core switches: Cisco Nexus 9516, Arista 7368 (300+ Tbps)
Interface speeds: 400G, 200G, 100G
Connectivity: Full mesh or near-full mesh
Protocol: BGP for core routing
```

### Distribution Layer
The distribution layer aggregates access layer traffic and applies policies.

**Characteristics:**
- Moderate to high throughput (40-100 Gbps)
- Policy enforcement (QoS, ACLs)
- VLAN routing and aggregation
- Redundant links to core
- Segmentation enforcement

**Technology:**
```
Distribution switches: Cisco Catalyst 9500, Arista 7050
Interface speeds: 40G, 100G
Connectivity: Dual links to core (2+1 N+1)
Protocol: OSPF or EIGRP with static routes
```

### Access Layer
The access layer provides end-user connectivity.

**Characteristics:**
- User device connections
- VLAN assignment
- PoE delivery (optional)
- Port security
- Link aggregation to distribution

**Technology:**
```
Access switches: Cisco Catalyst 9200L, Arista 7050SX
Port speeds: 1G, 10G access uplinks
Interface count: 24-48 ports
Protocol: VLAN trunking to distribution
```

## 2. Spine-and-Leaf (Clos) Topology

### Architecture Overview
The spine-and-leaf architecture is optimized for data center environments with predictable bandwidth oversubscription and equal-cost multi-path (ECMP) routing.

```
        +-----+     +-----+     +-----+     +-----+
        |Spine|     |Spine|     |Spine|     |Spine|
        |  1  |     |  2  |     |  3  |     |  4  |
        +-----+     +-----+     +-----+     +-----+
         / | \       / | \       / | \       / | \
        /  |  \     /  |  \     /  |  \     /  |  \
       /   |   \   /   |   \   /   |   \   /   |   \
    +---+  +---+ +---+ +---+ +---+ +---+ +---+ +---+
    | L1 | | L2| | L3| | L4| | L5| | L6| | L7| | L8|
    +---+  +---+ +---+ +---+ +---+ +---+ +---+ +---+
     |      |     |     |     |     |     |     |
    Servers/VMs/Containers attached to each Leaf
```

### Design Characteristics
- **Leaf switches:** Connect to servers (north-south traffic)
- **Spine switches:** Aggregate all leaf traffic (east-west traffic)
- **Bandwidth oversubscription:** Typically 1:4 or 1:8
- **ECMP routing:** All paths equally utilized
- **Non-blocking fabric:** Up to leaf density limits

### Calculation Example
```
Configuration:
- 8 spine switches with 100G interfaces
- 64 leaf switches, each with 32x100G uplinks
- Each spine connects to all 64 leaves

Spine uplink bandwidth: 8 spines × 32 × 100G = 25.6 Tbps
Leaf uplink capacity: 64 leaves × 32 × 100G = 204.8 Tbps
Oversubscription ratio: 204.8 / 25.6 = 8:1

With 64 servers per leaf at 25G each:
- Per-leaf server bandwidth: 64 × 25G = 1.6 Tbps
- Leaf-to-spine uplink: 32 × 100G = 3.2 Tbps
- Leaf oversubscription: 1.6 / 3.2 = 1:2
```

## 3. Hub-and-Spoke WAN Topology

### Central Hub
- Centralized data center
- Single point of internet connectivity
- VPN termination
- Policy enforcement

### Spoke Sites
- Branch offices
- Remote locations
- Backup connectivity via internet
- Direct internet optional

### Advantages
- Simplified management
- Centralized security
- Lower WAN costs for small branches
- Easy to add new branches

### Disadvantages
- Hub becomes bottleneck
- Single point of failure
- Higher latency for spoke-to-spoke
- Hub link utilization high

## 4. Full Mesh WAN Topology

### Characteristics
- Direct connections between all sites
- Maximum redundancy
- Lowest latency for all connections
- Complex management
- Higher cost

### Formula for Link Count
```
N sites = N × (N-1) / 2 direct links

Example: 5 sites
Links = 5 × 4 / 2 = 10 direct connections
```

### Use Cases
- Financial networks (trading floors)
- Real-time collaboration needs
- Small number of sites (3-5)

## 5. Partial Mesh WAN Topology

### Hybrid Approach
- Strategic full mesh between critical sites
- Hub-and-spoke for remaining sites
- Cost optimization with redundancy

### Design Pattern
```
Critical Sites (Tier 1): Full mesh with each other
Secondary Sites (Tier 2): Multiple connections to Tier 1
Branch Sites (Tier 3): Single or dual connection to nearest Tier 1

Example:
- 2 data centers: Full mesh (1 link)
- 4 regional hubs: Connected to both data centers (2 links each)
- 20 branches: Each connected to nearest regional hub (1 link each)
```

## 6. Ring Topology (WAN)

### Structure
```
Site A --- Site B
|           |
|           |
Site D --- Site C
```

### Characteristics
- Redundancy per link
- Self-healing with certain protocols
- Linear cost increase
- Moderate complexity

### MPLS Ring Example
```
MPLS LSPs around ring for redundancy
Primary path: A→B→C→D→A
Backup path: A→D→C→B→A
Convergence time: <50ms
```

## 7. Multi-Tier Data Center Topology

### Tier 0: Aggregation
- Multiple data centers
- Geographic distribution
- Disaster recovery capability

### Tier 1: Core
- High-speed interconnects
- BGP routing
- Load distribution

### Tier 2: Pod Design
- Spine-and-leaf per pod
- Pod-to-pod redundancy
- Contained failure domains

### Tier 3: Rack Level
- Top-of-rack switches
- Server aggregation
- Single-hop to spine

## 8. Hybrid Cloud Network Topology

### On-Premises
- Campus network
- Data center core

### Cloud Provider
- Virtual networks (VNets/VPCs)
- Public endpoints

### Connectivity
```
On-Prem DC --- [Express Route/Direct Connect] --- Cloud VNet
Campus --- [Internet/VPN] --- Cloud Services
   |
   +--- [Firewall] --- [SD-WAN] --- Branch Sites
```

## Best Practice Patterns Summary

| Pattern | Bandwidth | Redundancy | Complexity | Cost | Use Case |
|---------|-----------|------------|-----------|------|----------|
| 3-Tier | Scalable | High | Moderate | Low | Campus |
| Spine-Leaf | High | Very High | Moderate | Moderate | Data Center |
| Hub-Spoke | Moderate | Low | Low | Low | Small WAN |
| Full Mesh | Very High | Very High | High | Very High | Critical Sites |
| Partial Mesh | High | High | Moderate | Moderate | Medium WAN |
| Ring | Moderate | Moderate | Low | Moderate | Regional |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** Cisco, RFC 3021, IEEE 802.1Q
