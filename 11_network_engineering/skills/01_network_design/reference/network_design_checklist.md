# Network Design Checklist

## Pre-Design Phase

### Business Requirements
- [ ] Document organizational size and growth projections (3-5 year)
- [ ] Identify business-critical applications
- [ ] Define uptime requirements (SLA targets)
- [ ] List regulatory/compliance requirements (HIPAA, SOC2, PCI-DSS)
- [ ] Determine budget constraints
- [ ] Identify stakeholders and approval authority
- [ ] Define project timeline and milestones
- [ ] Assess current infrastructure (age, vendor lock-in)

### Network Assessment
- [ ] Conduct network baseline audit
- [ ] Document existing topology (as-built diagrams)
- [ ] Identify current bottlenecks
- [ ] Document current security posture
- [ ] List end-of-life systems
- [ ] Analyze current traffic patterns (NetFlow)
- [ ] Evaluate existing staff skills
- [ ] Document integration points with business systems

## Design Phase - Campus Network

### Access Layer Design
- [ ] Determine switch count needed (users / switch capacity)
- [ ] Select access layer platforms
- [ ] Plan power and cooling requirements
- [ ] Define port allocation (devices per switch)
- [ ] Plan uplink redundancy (dual 10G minimum)
- [ ] Design PoE budget and allocation
- [ ] Plan wireless AP placement and backhaul
- [ ] Create building-level topology diagram
- [ ] Calculate oversubscription ratios
- [ ] Identify high-density areas (labs, trading floors)

### Distribution Layer Design
- [ ] Design N+1 distribution redundancy
- [ ] Select distribution platform (throughput, features)
- [ ] Plan gateway redundancy (HSRP/VRRP)
- [ ] Design core interconnect (number of links)
- [ ] Create VLAN routing strategy
- [ ] Plan inter-VLAN policy enforcement
- [ ] Define STP root bridge selection
- [ ] Design uplink to core (bandwidth, redundancy)
- [ ] Plan for multi-site aggregation
- [ ] Document distribution-to-core link speeds

### Core Layer Design
- [ ] Determine core switch count (usually 2-4)
- [ ] Select core platform (backplane throughput)
- [ ] Plan full mesh topology
- [ ] Design BGP AS numbering
- [ ] Define core redundancy (dual supervisors, dual fabric)
- [ ] Plan management network architecture
- [ ] Design core-to-WAN interconnect
- [ ] Document core switching latency requirements
- [ ] Identify potential bottlenecks
- [ ] Plan for future expansion capacity

## Design Phase - IP Addressing

### IPv4 Planning
- [ ] Select RFC 1918 private space (Class A, B, or C)
- [ ] Document address space hierarchy
- [ ] Define departmental subnet allocation
- [ ] Plan building/floor subnetting
- [ ] Reserve space for growth (30% minimum)
- [ ] Allocate special-use addresses (management, guest)
- [ ] Design point-to-point link addressing (/31)
- [ ] Plan loopback addresses (routers, devices)
- [ ] Document DNS namespace strategy
- [ ] Create IP allocation spreadsheet with owner tracking

### IPv6 Planning
- [ ] Request Global Unicast Prefix (GUA) allocation
- [ ] Design IPv6 subnet hierarchy
- [ ] Plan DHCPv6 vs SLAAC deployment
- [ ] Define link-local addressing scheme
- [ ] Plan IPv4-to-IPv6 transition (dual-stack or tunneling)
- [ ] Document IPv6 routing policy
- [ ] Reserve IPv6 space for growth
- [ ] Plan multicast addressing (if needed)
- [ ] Create IPv6 address allocation document

### VLAN Planning
- [ ] Define VLAN numbering scheme (range allocation by function)
- [ ] Document VLAN naming convention
- [ ] Assign VLANs to departments/functions
- [ ] Plan VLAN size (subnet /24, /25, /27, etc.)
- [ ] Allocate voice VLAN with QoS priority
- [ ] Allocate guest VLAN with isolation
- [ ] Plan management VLAN access restrictions
- [ ] Define inter-VLAN routing strategy
- [ ] Plan VLAN trunking (allowed list)
- [ ] Create VLAN allocation spreadsheet with owner tracking

## Design Phase - Redundancy and High Availability

### Gateway Redundancy
- [ ] Select redundancy protocol (HSRP, VRRP, GLBP)
- [ ] Design virtual gateway IP addressing
- [ ] Document priority assignment logic
- [ ] Plan preemption configuration
- [ ] Create backup gateway failover procedure
- [ ] Plan monitoring/alerting for gateway state
- [ ] Document failover testing procedures

### Link Redundancy
- [ ] Design dual uplinks (access to distribution)
- [ ] Plan link aggregation (EtherChannel, LACP)
- [ ] Document load balancing algorithm
- [ ] Plan failover convergence time (<50ms preferred)
- [ ] Design redundant core interconnects
- [ ] Plan redundant WAN circuits
- [ ] Document backup link activation triggers

### Device Redundancy
- [ ] Plan N+1 distribution layer redundancy
- [ ] Plan dual supervisors on distribution/core
- [ ] Design N+1 fabric redundancy (core switches)
- [ ] Plan power supply redundancy
- [ ] Design cooling redundancy (hot/cold aisle)
- [ ] Document failover recovery procedures
- [ ] Plan quarterly failover testing schedule

### Data Center Redundancy
- [ ] Plan multi-pod architecture
- [ ] Design pod-to-pod interconnection
- [ ] Plan inter-data center connectivity (if multiple)
- [ ] Design replication lag tolerance
- [ ] Document RTO (Recovery Time Objective)
- [ ] Document RPO (Recovery Point Objective)
- [ ] Plan disaster recovery site connectivity

## Design Phase - WAN

### Topology Selection
- [ ] Select WAN topology (hub-spoke, mesh, hybrid)
- [ ] Document site count and location
- [ ] Plan traffic flow patterns
- [ ] Define critical path vs backup paths
- [ ] Calculate oversubscription at hub site
- [ ] Plan redundant WAN links per site
- [ ] Document WAN circuit speeds by site
- [ ] Plan backup connectivity options (failover)

### WAN Technology Selection
- [ ] Decide MPLS vs Internet VPN vs SD-WAN vs dedicated
- [ ] Document technology pros/cons for organization
- [ ] Plan provider selection criteria
- [ ] Define SLA requirements (latency, jitter, loss)
- [ ] Plan QoS policy for WAN traffic
- [ ] Document fallback/failover mechanisms
- [ ] Plan traffic shaping/policing rules

### Branch Connectivity
- [ ] Plan primary circuit type/speed per branch
- [ ] Plan backup circuit type/speed per branch
- [ ] Define failover timing and behavior
- [ ] Plan CPE device selection
- [ ] Design branch local network architecture
- [ ] Plan branch security (firewall, IPS)
- [ ] Document branch-to-HQ QoS policies

## Design Phase - Security Segmentation

### Network Segmentation
- [ ] Define security zones (DMZ, internal, guest)
- [ ] Document inter-zone traffic policies
- [ ] Plan isolated VLAN for sensitive data
- [ ] Design management network isolation
- [ ] Plan PCI-DSS compliance networks (if needed)
- [ ] Document network access control (NAC) strategy
- [ ] Plan 802.1X authentication deployment (optional)

### Firewall/Security Placement
- [ ] Identify core security appliance placement
- [ ] Plan east-west inspection (internal traffic)
- [ ] Design North-South inspection (perimeter)
- [ ] Plan IDS/IPS deployment strategy
- [ ] Document DDoS mitigation approach
- [ ] Plan WAF (Web Application Firewall) placement
- [ ] Design security policy enforcement points

## Design Phase - Management and Monitoring

### Management Network
- [ ] Design dedicated management VLAN
- [ ] Plan management network IP addresses
- [ ] Document access restrictions to management
- [ ] Plan out-of-band management access (IPMI, console)
- [ ] Design NTP synchronization source
- [ ] Plan DNS infrastructure (internal vs external)
- [ ] Document DHCP scope allocation

### Monitoring and Alerting
- [ ] Select monitoring platform (Cisco Prime, SolarWinds, Splunk)
- [ ] Plan NetFlow collection strategy
- [ ] Define monitoring KPIs (interface utilization, latency, loss)
- [ ] Document alerting thresholds (yellow, red)
- [ ] Plan escalation procedures
- [ ] Design syslog/logging infrastructure
- [ ] Plan SNMP community strings/authentication
- [ ] Document backup monitoring (if primary fails)

### Documentation Standards
- [ ] Define diagram standards (symbols, colors, fonts)
- [ ] Plan documentation repository (wiki, SharePoint, Git)
- [ ] Document naming conventions (devices, interfaces, VLANs)
- [ ] Create as-built topology diagrams
- [ ] Document equipment inventory (make, model, serial)
- [ ] Create IP allocation spreadsheet (IPAM)
- [ ] Document VLAN allocation spreadsheet
- [ ] Create WAN circuit inventory (provider, circuit ID, speed)
- [ ] Document design decision rationale

## Design Validation

### Design Review
- [ ] Present design to stakeholders
- [ ] Review against business requirements
- [ ] Validate cost against budget
- [ ] Confirm timeline feasibility
- [ ] Review SLA compliance
- [ ] Confirm regulatory requirement satisfaction
- [ ] Document design approvals
- [ ] Identify design risks and mitigation

### Capacity Validation
- [ ] Calculate 3-year growth projection
- [ ] Validate interface port count adequacy
- [ ] Validate switch throughput adequacy
- [ ] Validate WAN circuit bandwidth adequacy
- [ ] Verify power budget adequacy
- [ ] Verify cooling capacity adequacy
- [ ] Document capacity assumptions

### Performance Simulation
- [ ] Create network simulation model (GNS3, Cisco Packet Tracer)
- [ ] Simulate traffic patterns
- [ ] Validate latency assumptions
- [ ] Validate failover behavior
- [ ] Test routing convergence time
- [ ] Validate VLAN routing paths
- [ ] Document simulation results

## Pre-Implementation Phase

### Pilot Planning
- [ ] Identify pilot site (low-risk, representative)
- [ ] Plan pilot scope and duration
- [ ] Define pilot success criteria
- [ ] Plan pilot-to-production transition
- [ ] Document lessons learned process

### Procurement
- [ ] Create RFQ with detailed specifications
- [ ] Evaluate vendor quotes and capabilities
- [ ] Negotiate pricing and terms
- [ ] Place purchase orders
- [ ] Track delivery status
- [ ] Conduct equipment inspection on arrival
- [ ] Verify serial numbers and warranty
- [ ] Plan spare parts allocation

### Implementation Planning
- [ ] Create detailed implementation timeline
- [ ] Identify implementation team members
- [ ] Schedule training for network team
- [ ] Plan change management approvals
- [ ] Create rollback procedures
- [ ] Plan testing procedures per phase
- [ ] Document known issues and workarounds
- [ ] Schedule implementation windows

### Configuration Template Development
- [ ] Create switch configuration templates (IOS-XE, EOS, etc.)
- [ ] Create router configuration templates
- [ ] Create VLAN configuration templates
- [ ] Create security policy templates
- [ ] Create monitoring configuration templates
- [ ] Create documentation templates
- [ ] Version control all templates

## Implementation Phase

### Build Verification
- [ ] Verify physical connectivity (link lights)
- [ ] Verify interface speed/duplex (no mismatches)
- [ ] Test console/management connectivity
- [ ] Verify spanning tree operation (no loops)
- [ ] Test VLAN trunking (VLAN passage)
- [ ] Verify IP connectivity (ping between devices)
- [ ] Test gateway redundancy failover
- [ ] Test link redundancy failover

### Routing Verification
- [ ] Verify BGP sessions establish
- [ ] Verify routing table population
- [ ] Verify inter-VLAN routing
- [ ] Test route failover
- [ ] Verify ECMP load balancing (if used)
- [ ] Test default route redundancy
- [ ] Verify WAN routing

### Application Testing
- [ ] Test end-user connectivity
- [ ] Test server access from all VLANs
- [ ] Test VoIP call quality
- [ ] Test video conferencing
- [ ] Test file transfer performance
- [ ] Test cloud application access
- [ ] Test backup network traffic
- [ ] Load test critical applications

## Post-Implementation Phase

### Performance Baseline
- [ ] Establish baseline utilization metrics
- [ ] Document baseline latency
- [ ] Document baseline packet loss
- [ ] Create performance baseline report
- [ ] Set utilization threshold alerts
- [ ] Plan quarterly baseline reviews

### Operations Transfer
- [ ] Complete network team training
- [ ] Provide comprehensive documentation
- [ ] Establish escalation procedures
- [ ] Document known limitations
- [ ] Plan ongoing support model
- [ ] Schedule quarterly architecture reviews
- [ ] Plan annual capacity reviews

### Lessons Learned
- [ ] Conduct post-implementation review
- [ ] Document what went well
- [ ] Document challenges and resolutions
- [ ] Document future improvement ideas
- [ ] Update design standards based on learnings
- [ ] Archive all design documentation

## Ongoing Maintenance

### Regular Tasks
- [ ] Monthly: Review device health status
- [ ] Monthly: Review bandwidth utilization
- [ ] Quarterly: Test failover procedures
- [ ] Quarterly: Review capacity trending
- [ ] Semi-annual: Security policy review
- [ ] Annual: Design architecture review
- [ ] Annual: Disaster recovery testing
- [ ] Annual: Capacity planning update

### Monitoring Checklist
- [ ] Device CPU utilization < 75%
- [ ] Device memory utilization < 80%
- [ ] Interface utilization < 70% peak
- [ ] Link packet loss < 0.1%
- [ ] Latency to critical sites < 200ms
- [ ] Spanning tree stable (no topology changes)
- [ ] BGP sessions stable
- [ ] VLAN routing operational
- [ ] Security policies enforced
- [ ] Backup systems operational

---

**Checklist Version:** 1.0
**Last Updated:** November 2025
**Purpose:** Comprehensive design validation and implementation guide
