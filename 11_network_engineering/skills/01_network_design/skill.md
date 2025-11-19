# Network Design Skill

## Overview
Network Design is the foundational discipline for creating scalable, reliable, and efficient network architectures that support organizational requirements from campus environments to distributed data centers and wide-area networks. This skill enables professionals to architect networks that balance performance, availability, security, and cost optimization.

## Core Competencies

### 1. Campus Network Architecture

#### Hierarchical Three-Layer Design
- **Access Layer**: End-user and device connectivity, edge switching
- **Distribution Layer**: Policy application, VLAN routing, traffic aggregation
- **Core Layer**: High-speed backbone, redundancy, inter-site connectivity
- **Layer Interdependencies**: Traffic flow, bottleneck avoidance
- **Scalability Considerations**: Growing from small to large campuses

#### Access Layer Design
- **Switch Selection**: Port density, power consumption, available features
- **Port Density**: Number of ports per switch, oversubscription ratio
- **PoE (Power over Ethernet)**: Supporting wireless APs, VoIP phones, IoT devices
- **Uplink Speed**: Access-to-distribution bandwidth requirements
- **Redundancy**: Dual uplinks for high availability

#### Distribution Layer Functions
- **Aggregation**: Combining access layer switches
- **VLAN Routing**: Inter-VLAN communication and policy enforcement
- **QoS Implementation**: Marking, queuing, policing
- **Filtering**: Access control lists for security policies
- **Redundancy**: Dual distribution switches with active-active or active-passive

#### Core Layer Design
- **High-Speed Switching**: 100Gbps or higher throughput
- **Minimal Hops**: Reducing latency through design
- **Redundancy**: Active-active topologies, rapid failover
- **Reliability**: High MTBF, proven platforms
- **Bandwidth**: Overprovisioning for future growth

#### Switching Technologies
- **Ethernet Standards**: 1GbE, 10GbE, 40GbE, 100GbE
- **Switching Fabric**: Blocking vs. non-blocking architectures
- **Forwarding Rates**: Measuring switch throughput (Mpps)
- **Latency**: Cut-through vs. store-and-forward switching
- **Buffer Memory**: Handling traffic bursts

#### VLAN Design
- **VLAN Planning**: Organizing users and resources
- **VLAN Numbering**: Consistent numbering schemes
- **VLAN Segmentation**: Security boundaries and broadcast domains
- **Native VLAN**: Purpose and security considerations
- **Trunk Design**: Link-to-link VLAN communication

#### Spanning Tree Protocol (STP)
- **Root Bridge Election**: Topology stability
- **Path Cost Calculation**: Link speed and optimization
- **Convergence Time**: STP, RSTP, MSTP comparisons
- **Loop Prevention**: Detecting and blocking forwarding loops
- **PortFast**: Reducing convergence for edge ports

### 2. Data Center Network Design

#### Spine-and-Leaf Architecture
- **Topology Structure**: Leaf switches, spine switches, complete connectivity
- **Oversubscription**: Calculating from TOR to spine
- **CLOS Fabric**: Mathematical model for non-blocking switch fabric
- **East-West Traffic**: Server-to-server communication optimization
- **North-South Traffic**: Server-to-external communication

#### East-West vs. North-South
- **East-West Traffic**: Increasing percentage in modern data centers
- **Server-to-Server Communication**: Data replication, database synchronization
- **North-South Traffic**: Internet-facing services
- **Traffic Patterns**: Understanding for design optimization
- **Bandwidth Allocation**: Per-direction bandwidth provisioning

#### Server-to-Server Communication
- **Layer 2 Adjacency**: Requirements and limitations
- **Virtual Machine Mobility**: Live migration support
- **VXLAN and Overlays**: Creating virtual networks
- **Traffic Engineering**: Distributing flows efficiently
- **Performance Optimization**: Minimizing latency

#### High-Density Connectivity
- **Port Density**: Maximizing connections per rack
- **Cable Management**: Organizing high volume of cables
- **Bandwidth Density**: Gbps per unit of space
- **Power Consumption**: Supporting dense deployments
- **Cooling Requirements**: Managing heat from dense equipment

#### Multi-Pod Data Center Design
- **Pod Separation**: Logical data center divisions
- **Inter-Pod Connectivity**: Linking pods efficiently
- **Pod Isolation**: Failure containment within pods
- **Redundancy**: Cross-pod redundancy

#### Multi-Tier Data Center Design
- **Tier 1-4 Definitions**: Uptime Institute classifications
- **Availability Requirements**: Four-nines vs. five-nines
- **Redundancy Components**: Generators, UPS, networking
- **Failover Scenarios**: Testing and validation
- **Compliance Requirements**: Meeting SLAs

#### Network Virtualization
- **Overlay Networks**: Creating virtual networks on physical infrastructure
- **VXLAN**: Virtual extensible LAN for multi-tenancy
- **Network Function Virtualization (NFV)**: Virtual appliances
- **Tenant Isolation**: Logical network separation
- **Scale**: Supporting thousands of virtual networks

### 3. Wide Area Network (WAN) Design

#### WAN Topology Options
- **Hub-and-Spoke**: Central site with branch connections
- **Full Mesh**: Every site connects to every other site
- **Partial Mesh**: Selected site-to-site connectivity with hub backup
- **Ring Topology**: Circular connectivity for redundancy
- **Hybrid Topologies**: Combining topology types

#### Circuit-Switched Architectures
- **Dedicated Circuits**: Leased lines with guaranteed bandwidth
- **MPLS VPNs**: Multi-Protocol Label Switching for service provider VPNs
- **Quality of Service**: Guaranteed SLAs
- **Cost**: High fixed costs
- **Scalability**: Limited by circuit availability

#### Packet-Switched Architectures
- **Internet VPN**: Using public internet with IPsec encryption
- **SD-WAN**: Software-defined WAN for dynamic path selection
- **Hybrid WAN**: Combining circuit and packet approaches
- **Bandwidth Utilization**: Dynamic allocation
- **Cost**: Lower per-Mbps costs

#### MPLS Technology
- **Label Switching**: Quick forwarding using labels
- **MPLS VPN**: Creating secure VPNs across provider networks
- **Traffic Engineering**: Steering traffic on specific paths
- **QoS Support**: Per-tunnel SLA guarantees
- **Complexity**: Requires provider support

#### SD-WAN Technology
- **Software-Defined**: Decoupled control and data planes
- **Multi-WAN**: Using multiple WAN links
- **Application-Aware**: Routing based on application needs
- **Zero-Touch Provisioning**: Automated device onboarding
- **Cost Optimization**: Using cheaper broadband links

#### Bandwidth Provisioning
- **Capacity Planning**: Matching bandwidth to requirements
- **Overprovisioning**: Planning for growth
- **Traffic Shaping**: Managing peak demand
- **Burst Capability**: Temporary bandwidth increases
- **Cost Optimization**: Balancing capacity and cost

#### Branch Connectivity
- **Hub Sites**: Central branch locations
- **Spoke Sites**: Smaller branch offices
- **Remote Users**: Individual remote worker access
- **Scalability**: Supporting 100s or 1000s of branches
- **Failover**: Backup connectivity for critical sites

#### Disaster Recovery
- **RPO (Recovery Point Objective)**: Acceptable data loss
- **RTO (Recovery Time Objective)**: Acceptable downtime
- **Geographic Distribution**: Distributing across locations
- **Failover Mechanisms**: Automatic switching
- **Testing**: Regular DR drills and validation

### 4. IP Addressing and VLAN Strategy

#### IPv4 Address Planning
- **Private Address Spaces**: RFC 1918 ranges
- **Public Addressing**: Internet-routable addresses
- **Address Hierarchy**: Aggregation and summarization
- **Subnetting**: Dividing address space
- **Address Conservation**: Efficient IP usage

#### IPv6 Address Planning
- **IPv6 Transition**: From IPv4 to IPv6
- **Global Unicast Addresses**: Internet-routable IPv6
- **Unique Local Addresses**: Private IPv6
- **Link-Local Addresses**: Automatic node communication
- **Address Aggregation**: Reducing routing table size

#### Subnetting Design
- **Subnet Masks**: Variable-length subnet masks (VLSM)
- **Subnet Sizing**: Matching subnet size to device count
- **Aggregation**: Summarizing multiple subnets
- **Supernetting**: Combining multiple networks
- **Address Planning Tools**: IP address management systems

#### VLAN Design for Scalability
- **VLAN Distribution**: How many VLANs per switch
- **VLAN Trunking**: Inter-switch VLAN communication
- **VLAN Scalability**: Supporting hundreds of VLANs
- **VLAN Pruning**: Optimizing trunk bandwidth
- **Voice and Video VLANs**: Special handling for time-sensitive traffic

#### VLAN Design for Security
- **DMZ VLAN**: Internet-facing servers
- **Management VLAN**: Administrative access
- **User VLANs**: Different departments or user groups
- **Guest VLANs**: Visitor network isolation
- **IoT VLANs**: IoT device segregation

#### Inter-VLAN Routing
- **Router-on-a-Stick**: Single router interface routing multiple VLANs
- **SVI (Switched Virtual Interface)**: VLAN routing on switches
- **Layer 3 Switching**: Distributed routing
- **Routing Protocols**: OSPF, BGP, EIGRP for VLAN routing
- **Policy-Based Routing**: Conditional routing rules

#### Private IP Space Allocation
- **Class A Private (10.0.0.0/8)**: Large organizations
- **Class B Private (172.16.0.0/12)**: Medium organizations
- **Class C Private (192.168.0.0/16)**: Small organizations
- **Avoiding Conflicts**: Coordination between departments
- **Future Growth**: Planning for expansion

#### NAT and PAT Planning
- **Static NAT**: One-to-one IP mapping
- **Dynamic NAT**: Many-to-many IP mapping
- **PAT (Port Address Translation)**: Many-to-one with port translation
- **NAT Hairpinning**: Internal servers accessed via external addresses
- **Logging and Troubleshooting**: Understanding translated traffic

### 5. Network Redundancy and High Availability

#### Redundant Link Design
- **Dual Uplinks**: From access to distribution
- **Loop Prevention**: STP to prevent broadcast storms
- **Link Aggregation**: Combining multiple links for bandwidth
- **Active-Active**: Both links carrying traffic
- **Active-Passive**: One link active, one standby

#### Gateway Redundancy Protocols
- **HSRP (Hot Standby Router Protocol)**: Cisco proprietary
- **VRRP (Virtual Router Redundancy Protocol)**: Open standard
- **GLBP (Gateway Load Balancing Protocol)**: Active-active load balancing
- **Protocol Selection**: Vendor independence and feature comparison
- **Failover Speed**: Sub-second failover capability

#### Multi-Path Forwarding
- **Equal-Cost Multipath (ECMP)**: Load balancing across equal paths
- **Unequal-Cost Load Balancing**: Using non-equal cost paths
- **EIGRP Feasible Successor**: Fast convergence alternative
- **BGP Multipath**: BGP-based ECMP
- **Traffic Distribution**: Balancing flows across paths

#### Failover Mechanisms
- **Convergence Time**: How quickly network detects failure
- **Fast Failover**: Sub-second failure detection
- **BFD (Bidirectional Forwarding Detection)**: Rapid failure detection
- **Hello Intervals**: Protocol-specific keepalive timing
- **Hold Timers**: Detection of unresponsive neighbors

#### Load Balancing Strategies
- **Server Load Balancing**: Distributing client requests
- **Network Load Balancing**: Round-robin and other algorithms
- **Application Load Balancing**: Layer 7 awareness
- **Geographic Load Balancing**: Distributing across locations
- **Session Affinity**: Maintaining client-server connections

#### Disaster Recovery Site Connectivity
- **Synchronous Replication**: Waiting for remote confirmation
- **Asynchronous Replication**: Not waiting for remote confirmation
- **Bandwidth Requirements**: Replication traffic sizing
- **Failover Testing**: Regular DR drills
- **Recovery Procedures**: Documented failback process

### 6. Network Capacity Planning

#### Traffic Analysis
- **Baseline Measurement**: Establishing normal traffic patterns
- **Peak Analysis**: Understanding peak usage times
- **Growth Trends**: Historical traffic growth
- **Application Profiling**: Understanding traffic by application
- **Predictive Models**: Forecasting future traffic

#### Traffic Forecasting
- **Linear Growth**: Simple growth models
- **Exponential Growth**: Rapid growth scenarios
- **Seasonal Patterns**: Predictable seasonal changes
- **Business Growth**: Expansion plans and staffing changes
- **Uncertainty**: Planning for variable growth

#### Link Utilization Optimization
- **Target Utilization**: Industry recommendations
- **Peak vs. Average**: Different utilization targets
- **Congestion Points**: Identifying bottlenecks
- **Load Balancing**: Distributing traffic evenly
- **Optimization Techniques**: Steering and engineering

#### Bottleneck Identification
- **Link Oversubscription**: Links approaching capacity
- **Switch Buffer Exhaustion**: Packet drops
- **CPU Constraints**: Processor limitations
- **Throughput vs. Latency**: Trade-offs
- **Application Patterns**: Understanding traffic sources

#### Growth Capacity Modeling
- **3-Year Plan**: Mid-range planning horizon
- **5-Year Plan**: Long-range planning
- **Technology Changes**: Faster switching speeds, new standards
- **Business Scenarios**: Different growth assumptions
- **Cost-Benefit Analysis**: Investment timing

#### QoS Considerations
- **Traffic Classification**: Identifying traffic types
- **Priority Queuing**: Giving priority to critical traffic
- **Bandwidth Reservation**: Guaranteeing minimum bandwidth
- **Congestion Avoidance**: Preventing packet drops
- **SLA Compliance**: Meeting service level agreements

#### Cost Optimization Strategies
- **Bandwidth Efficiency**: Maximizing use of purchased bandwidth
- **Equipment Consolidation**: Reducing hardware footprint
- **Power Efficiency**: Reducing operational costs
- **Vendor Negotiations**: Achieving volume discounts
- **Life Cycle Costing**: Total cost of ownership analysis

### 7. Network Hardware Selection

#### Switch Platform Selection
- **Core Switches**: High-speed backbone switching
- **Distribution Switches**: Policy application and aggregation
- **Access Switches**: Edge connectivity
- **Feature Comparison**: Determining required features
- **Future-Proofing**: Planning for upgrades

#### Router Selection Criteria
- **Throughput**: Forwarding performance
- **Interface Options**: Available connection types
- **Routing Scale**: Number of routes supported
- **Feature Set**: Advanced routing capabilities
- **Hardware Redundancy**: Built-in failover

#### Module and Linecards
- **Modular Design**: Upgrading without replacing
- **Interface Modules**: Adding new connection types
- **Service Modules**: Adding specialized functions
- **Compatibility**: Ensuring module-chassis compatibility
- **Cost**: Module cost vs. dedicated appliance

#### Power and Cooling
- **Power Consumption**: Watts per device
- **UPS Capacity**: Backup power requirements
- **PDU Distribution**: Power distribution units
- **Airflow**: Intake and exhaust air management
- **Thermal Monitoring**: Temperature sensors and alerts

#### Throughput and Switching Fabric
- **Switching Fabric Bandwidth**: Total fabric capacity
- **Blocking Characteristics**: Non-blocking vs. oversubscribed
- **Forwarding Rate**: Packets per second (pps)
- **Backplane**: Data transfer speed
- **Oversubscription Ratio**: Accepted contention level

#### Port Density and Interface Options
- **Port Count**: Available ports per device
- **Port Speeds**: 1Gbps, 10Gbps, 40Gbps, 100Gbps options
- **Interface Types**: RJ45, SFP, QSFP, etc.
- **Uplink Modules**: Converting port speeds
- **Future Expansion**: Room for growth

### 8. Network Documentation

#### Design Documentation Standards
- **Document Types**: Architecture, detailed design, implementation
- **Audience**: Different versions for different stakeholders
- **Version Control**: Tracking design changes
- **Approval Process**: Sign-offs and authorization
- **Change Log**: Recording modifications over time

#### Network Topology Diagrams
- **Physical Topology**: Physical connections and locations
- **Logical Topology**: Traffic flows and relationships
- **Layer Diagrams**: Separating by OSI layer
- **Site Diagrams**: Individual location details
- **WAN Diagram**: Geographic site connections

#### Configuration Templates
- **Standard Configurations**: Approved baseline configs
- **Device Roles**: Role-based configuration templates
- **Security Hardening**: Security baseline templates
- **Consistency**: Reducing configuration errors
- **Automation**: Using templates for deployment

#### Change Management
- **Change Requests**: Formal change process
- **Impact Analysis**: Understanding change effects
- **Testing**: Pre-production validation
- **Rollback Plans**: Recovery from failed changes
- **Communication**: Notifying affected parties

#### Design Decision Rationale
- **Architecture Choices**: Why certain decisions were made
- **Trade-offs**: Documented compromises
- **Requirements Mapping**: Linking design to requirements
- **Alternatives Considered**: Why alternatives were rejected
- **Future Flexibility**: How design accommodates changes

## Learning Objectives

By mastering Network Design, you will be able to:
- Design scalable three-tier campus networks
- Create optimal data center fabric architectures
- Plan global WAN infrastructures
- Develop comprehensive IP addressing schemes
- Implement redundancy and high availability
- Optimize network capacity and performance
- Select appropriate network hardware
- Document designs professionally

## Skill Progression

### Foundational
- Understand hierarchical network design models
- Learn basic VLAN design principles
- Study IP addressing fundamentals
- Explore standard network topologies

### Intermediate
- Design multi-building campus networks
- Implement complex VLAN strategies
- Plan WAN topologies for medium enterprises
- Apply redundancy best practices

### Advanced
- Design multi-site data center networks
- Plan global enterprise WAN architectures
- Optimize network designs for specific use cases
- Develop organizational network standards

## Related Skills
- Network Automation (11.5) - Implementation of designed networks
- Network Security (11.3) - Security segmentation in designs
- Network Monitoring (11.9) - Performance validation of designs
- 5G Cloud Networks (11.10) - Modern cloud-native designs

## Key Tools and Technologies
- Network design software (Lucidchart, Visio, Draw.io)
- VLAN and IP management tools
- Simulation platforms (Cisco Packet Tracer, GNS3)
- Configuration templates and version control
- Network documentation systems

## Industry Standards and Frameworks
- Cisco Three-Tier Hierarchical Model
- RFC 1918 - Private Internet Addressing
- RFC 3021 - Using /31 IPv4 Prefixes on Links
- RFC 8200 - Internet Protocol, Version 6 (IPv6)
- IEEE 802.1Q - VLAN Tagging
- IEEE 802.3 - Ethernet Standards

## Common Design Scenarios

### Enterprise Campus
- Multi-building connectivity
- Wireless integration
- Guest network isolation
- IoT network segmentation
- Voice over IP integration

### Data Center
- Virtual machine traffic patterns
- Storage network design
- Management network separation
- Security zones and DMZ
- Multi-tenant architectures

### Wide Area Network
- Branch office connectivity
- Remote site access
- Backup and disaster recovery
- Global expansion support
- Performance optimization

## Practical Applications

### Small Business Network (50-200 users)
- Simple two-tier design
- Single internet connection
- Basic VLAN segmentation
- Direct internet WAN connectivity

### Medium Enterprise (500-2000 users)
- Full three-tier campus
- Multiple internet connections
- Advanced VLAN strategies
- MPLS-based WAN
- Redundant core

### Large Enterprise (5000+ users)
- Multi-campus connectivity
- Complex WAN topology
- Multiple data centers
- Advanced redundancy
- Global network design

## Success Metrics

When you've mastered Network Design, you'll be able to:
- Create designs that scale to support organization growth
- Implement networks with 99.99% availability
- Optimize network costs while maintaining performance
- Document designs that others can implement consistently
- Adapt designs for specific organizational requirements
- Make informed technology and architecture trade-offs

## Resource Categories

This skill includes resources for:
- Understanding network topology patterns
- Planning IP addressing schemes
- Designing VLAN architectures
- Implementing redundancy patterns
- Architecting campus networks
- Creating data center fabric designs
- Planning WAN architectures
- Capacity planning and optimization
- Hardware selection criteria
- Design checklists and validation

---

**Last Updated:** November 2025
**Skill Version:** 1.0
**Domain:** Network Engineering (11)
**Certification:** Aligns with CCNA Enterprise Network Architecture
