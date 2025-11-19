# Routing & Switching - Advanced Network Infrastructure

## Skill Overview

Expert-level mastery of enterprise routing and switching technologies, protocols, and design patterns. This skill encompasses the core technologies that enable modern network infrastructure, from Layer 2 switching fundamentals to advanced Layer 3 routing architectures.

## Core Competencies

### Interior Gateway Protocols (IGPs)

#### OSPF (Open Shortest Path First)
- Single-area and multi-area OSPF deployments
- Area types: backbone, standard, stub, totally stubby, NSSA
- Router roles: ABR, ASBR, designated router concepts
- OSPF authentication: plain-text, MD5, SHA authentication
- Cost calculation and metric manipulation
- OSPF timers optimization for convergence
- Virtual links for non-contiguous areas

#### EIGRP (Enhanced Interior Gateway Routing Protocol)
- Classic mode vs. Named mode configuration
- K-values and metric calculation
- Feasible distance and advertised distance concepts
- EIGRP authentication: MD5 and SHA
- Unequal cost load balancing
- EIGRP stub routing
- Route summarization and auto-summarization
- EIGRP for IPv4 and IPv6

#### BGP (Border Gateway Protocol)
- eBGP and iBGP neighbor relationships
- BGP states and timers
- BGP attributes: weight, local preference, AS-path, origin, communities
- Route filtering and prefix-lists
- Route manipulation: AS-path prepending, local preference manipulation
- Route reflectors and confederations
- BGP route dampening
- BGP community filtering and RT/ET concepts
- Multi-path eBGP load balancing

### Layer 2 Switching Technologies

#### VLAN and Trunk Configuration
- VLAN creation and management
- 802.1Q and ISL tagging protocols
- Native VLAN configuration
- Voice VLANs and access mode configuration
- VLAN trunking across multiple switches
- VLAN security and VLAN hopping prevention
- Private VLANs (PVLANs) for traffic isolation
- Dynamic VLAN assignment (802.1X)

#### Spanning Tree Protocol (STP)
- STP, RSTP (802.1w), and MSTP (802.1s)
- Root bridge and path cost calculation
- Bridge priority and port priority
- BPDU handling and timers
- PortFast, BPDU Guard, Root Guard
- STP convergence optimization
- Multiple Spanning Tree (MST) configuration
- Rapid RSTP convergence mechanisms

#### EtherChannel
- Link Aggregation Control Protocol (LACP)
- Port Aggregation Protocol (PAgP)
- Static EtherChannel configuration
- Load balancing algorithms (L2-L4)
- EtherChannel guard and error recovery
- Cross-stack EtherChannel in stackable switches
- LACP rate and timeout configuration

### Layer 3 Advanced Technologies

#### First Hop Redundancy Protocols (FHRP)
- HSRP (Hot Standby Router Protocol) configuration and timers
- VRRP (Virtual Router Redundancy Protocol) for multi-vendor environments
- GLBP (Gateway Load Balancing Protocol) for active-active scenarios
- Priority and tracking mechanisms
- Authentication in HSRP and VRRP
- IPv6 support in FHRP protocols

#### Route Redistribution
- Redistribution between RIP, OSPF, EIGRP, BGP
- Metric conversion and default metrics
- ACL-based selective redistribution
- Tag-based redistribution for loop prevention
- Mutual redistribution and default routes
- Passive interface usage in redistribution

#### Policy-Based Routing (PBR)
- Route maps for traffic engineering
- Set-based operations (next-hop, interface, AS-path)
- Match criteria: access-lists, length, QoS marking
- PBR on egress interfaces
- Traffic classification and forwarding decisions

#### Multicast Routing
- IGMP (Internet Group Management Protocol) versions
- PIM Sparse Mode (PIM-SM) and Dense Mode (PIM-DM)
- Rendezvous Points (RP) and RP discovery mechanisms
- MSDP (Multicast Source Discovery Protocol)
- Multicast VRF support
- Multicast traffic flow optimization

#### VRF and VRF-Lite
- VRF instantiation and interface assignment
- Static and dynamic routing in VRF context
- VRF route leaking and interconnection
- MPLS VPN fundamentals
- VRF-aware service implementations

### Layer 2 Security

#### Switch Port Security
- Port security configuration and violation actions
- MAC address learning and aging
- Sticky MAC addresses
- DHCP snooping and source-guard
- Dynamic ARP Inspection (DAI)
- BPDU filtering and BPDU guard

#### Advanced VLAN Security
- VLAN access control lists (VACLs)
- Private VLAN implementation
- MAC-based VLAN assignment
- 802.1X port-based network access control
- Guest VLAN and critical authentication bypass

### Advanced Topics

#### Network Convergence
- BFD (Bidirectional Forwarding Detection) for fast failover
- BGP graceful restart
- OSPF graceful restart
- EIGRP graceful shutdown
- Preemption and non-preemption in HSRP/VRRP

#### Route Optimization
- Route summarization techniques
- Manual and auto-summarization
- Prefix aggregation strategies
- Route tagging and filtering

#### QoS and Traffic Engineering
- Quality of Service in OSPF and BGP
- DiffServ and DSCP marking propagation
- Traffic engineering with MPLS (TE-MPLS)
- Bandwidth reservation in routing protocols

## Learning Paths

### Path 1: IGP Specialization
1. Master OSPF fundamentals and advanced features
2. Implement OSPF in multi-area environments
3. Design OSPF networks for scalability
4. Advanced EIGRP configuration and optimization
5. BGP fundamentals and eBGP peering
6. BGP best practices and policy implementation

### Path 2: Switching Specialization
1. Master VLAN design and implementation
2. Implement and optimize Spanning Tree Protocol
3. Configure EtherChannel for redundancy
4. Layer 2 security and attack prevention
5. Advanced switching architectures
6. High-availability switching designs

### Path 3: Enterprise Design
1. Design scalable IGP networks
2. Implement BGP in enterprise environments
3. Design multi-layer campus networks
4. Implement redundancy and high availability
5. Advanced routing policy implementation
6. Network convergence optimization

## Key Resources

### Reference Materials
- ospf_quick_reference.md - OSPF protocol essentials
- bgp_quick_reference.md - BGP attributes and operations
- eigrp_quick_reference.md - EIGRP metrics and configuration
- vlan_trunking_reference.md - VLAN tagging and trunk configuration
- spanning_tree_reference.md - STP costs, timers, and port roles
- etherchannel_reference.md - EtherChannel protocols and load-balancing
- routing_protocol_comparison.md - Comparative analysis of IGPs
- bgp_attributes_reference.md - BGP attribute manipulation techniques
- route_redistribution_reference.md - Redistribution matrix and metrics
- layer2_security_reference.md - Layer 2 security mechanisms
- first_hop_redundancy_reference.md - FHRP comparison and features
- multicast_routing_reference.md - Multicast protocols and concepts

### Implementation Guides
- ospf_design_and_deployment.md - Design patterns and best practices
- bgp_best_practices_guide.md - BGP operational excellence
- eigrp_configuration_guide.md - EIGRP from basic to advanced
- vlan_design_implementation.md - Strategic VLAN architectures
- spanning_tree_optimization.md - STP convergence and efficiency
- etherchannel_configuration_guide.md - EtherChannel deployment
- route_redistribution_guide.md - Seamless protocol transitions
- policy_based_routing_guide.md - Advanced traffic engineering
- bgp_route_filtering_guide.md - Route filtering strategies
- vrf_configuration_guide.md - VRF design and implementation
- multicast_deployment_guide.md - Multicast network architecture
- routing_troubleshooting_guide.md - Diagnostic and resolution methods

### Configuration Examples (src/)
- OSPF single-area and multi-area configurations
- BGP eBGP and iBGP with route reflectors
- EIGRP named mode configuration
- VLAN and trunk configurations
- STP optimization for convergence
- LACP EtherChannel configuration
- HSRP and VRRP redundancy
- Route redistribution between protocols
- Policy-Based Routing implementation
- VRF-Lite configuration
- BGP filtering and prefix-list examples
- Multicast PIM Sparse Mode setup
- Layer 2 security (port security, DHCP snooping, DAI)
- Private VLAN configuration

## Certification Alignment

- **CCNA Routing & Switching** - Core foundational knowledge
- **CCNP Enterprise** - Advanced routing and switching
- **CCIE Enterprise Infrastructure** - Expert-level mastery

## Industry Standards

- IEEE 802.1D/802.1w/802.1s - Spanning Tree Protocol families
- RFC 2178 - OSPF Version 2
- RFC 4271 - BGP-4
- RFC 7868 - EIGRP Named Mode
- IEEE 802.1Q - VLAN Tagging
- RFC 2281 - HSRP
- RFC 5798 - VRRP Version 3
- RFC 5059 - BGP Route Reflection
- RFC 7911 - Advertisement of Multiple Paths in BGP

## Target Use Cases

1. **Enterprise Campus Networks** - Multi-building switching and routing designs
2. **Service Provider Networks** - BGP-based inter-AS connectivity
3. **Data Center Networking** - High-performance switching and routing
4. **WAN Design** - IGP-based enterprise-wide connectivity
5. **Network Segmentation** - VLAN and VRF-based isolation
6. **High Availability** - Redundancy and fast convergence
7. **Traffic Engineering** - Advanced routing policies and load balancing
8. **Network Migration** - Route redistribution and protocol transitions

---

**Last Updated:** 2025-11-19
**Skill Level:** Advanced (CCNP/CCIE)
**Domain:** Network Engineering
