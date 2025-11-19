# Telecommunications Cloud Skill

## Table of Contents

1. [Overview](#overview)
2. [Domain Scope](#domain-scope)
3. [When to Use This Skill](#when-to-use-this-skill)
4. [Prerequisites](#prerequisites)
5. [Getting Started](#getting-started)
6. [Usage Instructions](#usage-instructions)
7. [Core Use Cases](#core-use-cases)
8. [Template Reference](#template-reference)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Standards and Specifications](#standards-and-specifications)
12. [Glossary](#glossary)
13. [Additional Resources](#additional-resources)

---

## Overview

The Telecommunications Cloud Skill is a specialized AI assistant designed to help telecommunications professionals, network architects, and engineers tackle complex challenges in modern telecom infrastructure. This skill provides expert guidance on 5G network deployment, Network Functions Virtualization (NFV), Software-Defined Networking (SDN), billing system implementation, and carrier-grade network operations.

### What This Skill Covers

**5G and Next-Generation Networks**
- 5G Core (5GC) architecture and deployment
- Radio Access Network (RAN) planning and optimization
- Network slicing implementation
- Multi-access Edge Computing (MEC)
- Non-Standalone (NSA) and Standalone (SA) deployment strategies
- Massive MIMO and beamforming configurations

**Network Functions Virtualization (NFV)**
- Virtual Network Functions (VNF) design and deployment
- NFV Infrastructure (NFVI) architecture
- NFV Management and Orchestration (MANO)
- Container-based Network Functions (CNF)
- Service Function Chaining (SFC)
- NFV performance optimization and troubleshooting

**Telecommunications Billing and OSS/BSS**
- Convergent charging systems
- Online Charging System (OCS) and Offline Charging System (OFCS)
- Revenue Management and Billing Mediation
- Policy and Charging Rules Function (PCRF/PCF)
- Customer Relationship Management (CRM) integration
- TM Forum Open Digital Architecture (ODA) frameworks

**Legacy and Core Network Technologies**
- IP Multimedia Subsystem (IMS)
- Evolved Packet Core (EPC) for LTE
- Circuit-switched fallback (CSFB) and Voice over LTE (VoLTE)
- Signaling System 7 (SS7) and Diameter protocol
- Session Initiation Protocol (SIP) and Real-time Transport Protocol (RTP)
- Multi-Protocol Label Switching (MPLS) and Segment Routing

---

## Domain Scope

### 5G Network Architecture

The Fifth Generation (5G) of mobile networks represents a fundamental shift in telecommunications architecture. Unlike previous generations, 5G is designed as a cloud-native, service-based architecture (SBA) that supports diverse use cases ranging from enhanced Mobile Broadband (eMBB) to Ultra-Reliable Low-Latency Communications (URLLC) and massive Machine-Type Communications (mMTC).

**5G Core Network Functions:**

- **AMF (Access and Mobility Management Function)**: Handles connection and mobility management, registration, and reachability
- **SMF (Session Management Function)**: Manages session establishment, modification, and release
- **UPF (User Plane Function)**: Processes user plane traffic and acts as the PDU session anchor
- **PCF (Policy Control Function)**: Provides policy rules for service data flow and QoS control
- **UDM (Unified Data Management)**: Stores subscriber data and profiles
- **AUSF (Authentication Server Function)**: Handles authentication for 3GPP and non-3GPP access
- **NSSF (Network Slice Selection Function)**: Selects network slice instances for devices
- **NRF (Network Repository Function)**: Supports service discovery and network function registration
- **NEF (Network Exposure Function)**: Exposes capabilities and events to external applications

### Network Functions Virtualization

NFV decouples network functions from proprietary hardware, enabling them to run on standard servers using virtualization technology. This transformation allows telecommunications operators to:

- Deploy services faster with software-based approaches
- Scale network functions dynamically based on demand
- Reduce Capital Expenditure (CapEx) through commercial off-the-shelf (COTS) hardware
- Improve Operational Expenditure (OpEx) through automation and orchestration
- Enhance network agility and innovation velocity

**NFV Architectural Framework (ETSI NFV):**

- **VNF (Virtual Network Function)**: Software implementation of network functions
- **NFVI (NFV Infrastructure)**: Compute, storage, and network resources
- **MANO (Management and Orchestration)**:
  - NFVO (NFV Orchestrator): Network service lifecycle management
  - VNFM (VNF Manager): VNF lifecycle management
  - VIM (Virtualized Infrastructure Manager): NFVI resource management

### Billing and Revenue Management

Modern telecommunications billing systems must handle complex scenarios including convergent charging (voice, data, SMS), real-time charging for prepaid services, postpaid billing cycles, and interconnect settlement. These systems integrate with network elements through standardized protocols like Diameter (Ro, Gy, Gx interfaces) and REST APIs.

**Key Billing Components:**

- **Mediation**: Collects and processes usage data (CDRs, UDRs, EDRs)
- **Rating**: Applies pricing rules to usage records
- **Charging**: Implements real-time (OCS) and offline (OFCS) charging
- **Billing**: Generates invoices and manages customer accounts
- **Policy Management**: Controls QoS and service access (PCRF/PCF)
- **Revenue Assurance**: Detects revenue leakage and ensures data integrity

---

## When to Use This Skill

### Ideal Scenarios

Use the Telecommunications Cloud Skill when you need expertise in:

1. **5G Network Planning and Deployment**
   - Designing 5G Core network architecture for greenfield or brownfield deployments
   - Planning RAN infrastructure with coverage and capacity analysis
   - Implementing network slicing for enterprise customers or vertical industries
   - Deploying MEC platforms for low-latency applications
   - Migrating from 4G EPC to 5G SA core network

2. **NFV and Cloud-Native Transformation**
   - Virtualizing legacy network functions (vIMS, vEPC, vBNG)
   - Designing CNF-based network services for Kubernetes
   - Implementing MANO platforms (OSM, ONAP, Cloudify)
   - Optimizing VNF performance and resource allocation
   - Troubleshooting NFV infrastructure and orchestration issues

3. **Billing System Implementation**
   - Designing convergent charging systems for multi-service operators
   - Implementing real-time charging for prepaid services
   - Integrating billing with network policy enforcement (PCRF/PCF)
   - Developing custom rating plans and promotional campaigns
   - Ensuring billing accuracy and revenue assurance

4. **Network Protocol Analysis**
   - Debugging SIP signaling issues in IMS/VoLTE deployments
   - Analyzing Diameter protocol exchanges (Gx, Gy, S6a interfaces)
   - Troubleshooting GTP-C/GTP-U tunneling in mobile core networks
   - Investigating SS7 security vulnerabilities and implementing protections
   - Optimizing SCTP and QUIC performance for signaling and data

5. **Standards Compliance and Interoperability**
   - Ensuring 3GPP specification compliance for network elements
   - Validating ETSI NFV architectural alignment
   - Implementing TM Forum Open APIs (TMF APIs)
   - Achieving MEF 3.0 SD-WAN certification requirements
   - Following O-RAN Alliance specifications for open RAN deployments

6. **Performance Optimization**
   - Tuning 5G QoS parameters for different service types (eMBB, URLLC, mMTC)
   - Optimizing VNF placement and resource allocation in NFV environments
   - Analyzing and improving network KPIs (latency, throughput, packet loss)
   - Capacity planning for peak traffic scenarios (major events, network holidays)
   - Implementing traffic engineering and load balancing strategies

---

## Prerequisites

### Required Knowledge

To effectively use this skill, you should have familiarity with:

**Fundamental Networking**
- TCP/IP protocol suite (IPv4/IPv6, TCP, UDP, ICMP)
- Routing protocols (BGP, OSPF, IS-IS)
- Switching technologies (VLANs, VXLAN, EVPN)
- Network security (IPsec, TLS, firewalls, NAT)
- Quality of Service (QoS) mechanisms (DiffServ, IntServ, traffic shaping)

**Mobile Network Basics**
- 3GPP architecture evolution (2G → 3G → 4G → 5G)
- Mobile network elements (NodeB, eNodeB, gNodeB, MME, HSS, etc.)
- Radio access technologies (GSM, UMTS, LTE, NR)
- Core network protocols (GTP, Diameter, SIP, SCTP)
- Mobility management and session management concepts

**Virtualization and Cloud Technologies**
- Hypervisor technologies (KVM, VMware ESXi, Xen)
- Container platforms (Docker, Kubernetes, containerd)
- Infrastructure as Code (Terraform, Ansible, CloudFormation)
- Cloud platforms (OpenStack, AWS, Azure, Google Cloud)
- Software-Defined Networking (OpenFlow, ONOS, ODL)

**Telecommunications Standards**
- 3GPP specifications (TS 23.501, TS 23.502, TS 29.500 series)
- ETSI NFV standards (GS NFV-MAN 001, GS NFV-INF 003)
- TM Forum frameworks (Frameworx, Open APIs, ODA)
- ITU-T recommendations (Q.700 series, E.800 series)
- IETF RFCs (SIP, Diameter, HTTP/2, QUIC)

### Recommended Experience

- **Network Operations**: Experience operating carrier-grade networks with 99.999% availability requirements
- **System Integration**: Integrating multi-vendor network elements and OSS/BSS systems
- **Programming**: Proficiency in Python, Go, or Java for automation and tooling
- **DevOps Practices**: CI/CD pipelines, automated testing, infrastructure as code
- **Troubleshooting**: Packet capture analysis (Wireshark, tcpdump), log analysis, root cause analysis

### Tools and Environment

Familiarity with the following tools will enhance your experience:

- **Network Simulators**: ns-3, OMNeT++, 5G-LENA
- **Protocol Analyzers**: Wireshark, tshark, ngrep, tcpdump
- **Testing Tools**: SIPp, iperf3, hping3, ab (Apache Bench)
- **Orchestration**: Kubernetes, OpenStack Heat, TOSCA templates
- **Monitoring**: Prometheus, Grafana, ELK Stack, Nagios
- **API Testing**: Postman, curl, HTTPie, REST clients

---

## Getting Started

### Installation

The Telecommunications Cloud Skill is available as part of the Claude Code skill ecosystem. No additional installation is required beyond access to Claude Code.

### Quick Start

1. **Activate the Skill**: Invoke the telecommunications skill when working on telecom-related projects
2. **Define Your Context**: Provide specific details about your network architecture, technology stack, and objectives
3. **Ask Specific Questions**: Frame questions with technical details, protocols, and standards references
4. **Iterate and Refine**: Build upon responses to dive deeper into implementation details

### Example Quick Start Session

```bash
# Example 1: 5G Core Architecture Design
"I need to design a 5G Standalone core network for a regional mobile operator
serving 500,000 subscribers. The deployment should support eMBB and initial
IoT services. What architecture should I use, and what are the key
considerations for network function sizing and placement?"

# Example 2: NFV Migration Planning
"We're migrating our legacy IMS from physical appliances to VNFs. Our current
deployment handles 200,000 VoLTE subscribers with 4,000 BHCA (Busy Hour Call
Attempts). What's the recommended approach for NFV infrastructure sizing,
redundancy, and migration strategy to minimize service disruption?"

# Example 3: Billing System Integration
"I need to integrate our OCS with the 5G PCF for policy-based charging.
We need to support usage-based billing, speed throttling after quota
exhaustion, and sponsored data scenarios. Which Diameter interfaces should
I implement, and what are the critical AVPs for these use cases?"
```

---

## Usage Instructions

### Basic Workflow

1. **Provide Context**
   - Network topology and architecture
   - Technology stack (vendors, software versions)
   - Scale parameters (subscribers, throughput, geographic coverage)
   - Constraints (budget, timeline, regulatory requirements)

2. **Specify Requirements**
   - Functional requirements (features, capabilities)
   - Non-functional requirements (performance, availability, scalability)
   - Compliance requirements (3GPP release, ETSI specifications)
   - Integration requirements (existing systems, APIs, protocols)

3. **Request Assistance**
   - Architecture design and review
   - Protocol analysis and troubleshooting
   - Configuration guidance and best practices
   - Implementation planning and migration strategies

4. **Validate and Iterate**
   - Review recommendations against your specific constraints
   - Ask follow-up questions for clarification
   - Request alternative approaches or trade-off analysis
   - Dive deeper into specific technical areas

### Advanced Usage Patterns

#### Protocol Deep Dives

When troubleshooting protocol issues, provide:
- Packet captures (sanitized) or protocol traces
- Specific error messages or failure symptoms
- Network element logs (sanitized)
- Sequence diagrams of expected vs. actual behavior

Example:
```
"I'm seeing SIP 488 Not Acceptable Here responses during VoLTE call setup.
The INVITE contains SDP with AMR-WB codec (octect-align=1), EVS codec support,
and MTSI parameters. The P-CSCF forwards to I-CSCF, which queries HSS via
Diameter S-CSCF assignment, but the subsequent I-CSCF to S-CSCF INVITE fails.
S-CSCF logs show 'codec negotiation failure'. What could cause this, and
how do I debug further?"
```

#### Architecture Reviews

For architecture validation, provide:
- High-level architecture diagram (describe or reference)
- Network function inventory with versions and capacities
- Interface matrix (which NFs communicate via which protocols)
- Scaling assumptions and growth projections
- Availability and disaster recovery strategy

Example:
```
"Please review our 5G NSA architecture:
- EPC with MME (Ericsson vMME), SGW (Nokia vSGW), PGW (Cisco vPGW)
- 5G NR RAN (Samsung gNodeB) connected to EPC via S1-U/X2
- IMS for VoNR over EPS fallback
- Target: 1M subscribers, 40 Gbps aggregate throughput
- Geographic redundancy across 2 data centers (active-standby)

Is this architecture aligned with 3GPP standards? What are potential
bottlenecks or single points of failure?"
```

#### Performance Optimization

For performance tuning, provide:
- Current KPIs and metrics (latency, throughput, error rates)
- Performance targets and SLAs
- Resource utilization (CPU, memory, network bandwidth)
- Traffic patterns and busy hour characteristics
- Current configuration parameters

Example:
```
"Our UPF is experiencing high latency (50ms average, 95th percentile 120ms)
during peak hours. Target is <10ms average. Current deployment:
- VNF on OpenStack (16 vCPUs, 32GB RAM, SR-IOV NICs)
- Handling 10 Gbps throughput, 500K active sessions
- CPU utilization peaks at 75% across vCPUs
- DPDK enabled with 4 worker threads
What optimizations can reduce latency? Should we scale horizontally or
vertically?"
```

---

## Core Use Cases

### Use Case 1: 5G Standalone Network Deployment

#### Scenario

A mobile network operator wants to deploy a 5G Standalone (SA) core network to support consumer 5G services and prepare for enterprise verticals (smart manufacturing, connected vehicles). The deployment must support:

- 2 million subscribers initially, scaling to 10 million
- Network slicing for differentiated services
- Edge computing capabilities for low-latency applications
- Interworking with existing 4G EPC for seamless mobility
- Cloud-native architecture on Kubernetes

#### Implementation Approach

**Phase 1: Architecture Design**

Design a cloud-native 5G Core using CNFs:

```yaml
# 5G Core Network Functions Deployment
Network Functions:
  - AMF (Access and Mobility Management Function)
    - Instances: 6 (3 per site for N+K redundancy)
    - Capacity: 500K subscribers per instance
    - Resources: 8 vCPUs, 16GB RAM per instance

  - SMF (Session Management Function)
    - Instances: 8 (4 per site)
    - Capacity: 250K sessions per instance
    - Resources: 12 vCPUs, 24GB RAM per instance

  - UPF (User Plane Function)
    - Instances: 20 (10 per site + 10 edge locations)
    - Throughput: 10 Gbps per instance
    - Resources: 16 vCPUs, 32GB RAM, SR-IOV/DPDK

  - PCF (Policy Control Function)
    - Instances: 4 (2 per site)
    - Capacity: 1M policy rules, 500K concurrent sessions
    - Resources: 8 vCPUs, 32GB RAM per instance

  - UDM/UDR (Unified Data Management/Repository)
    - Instances: 6 (3 per site, database sharding)
    - Capacity: 10M subscriber profiles
    - Resources: 8 vCPUs, 64GB RAM, SSD storage

  - AUSF (Authentication Server Function)
    - Instances: 4 (2 per site)
    - Capacity: 10K auth requests/second
    - Resources: 4 vCPUs, 8GB RAM per instance
```

**Phase 2: Network Slicing Configuration**

Implement three initial network slices:

1. **eMBB Slice** (Enhanced Mobile Broadband)
   - SST: 1, SD: 000001
   - Target: High throughput for consumer services
   - QoS: 5QI 9 (default bearer), 5QI 1 (GBR for premium)
   - UPF placement: Central data centers

2. **URLLC Slice** (Ultra-Reliable Low-Latency)
   - SST: 2, SD: 000001
   - Target: Industrial automation, remote control
   - QoS: 5QI 82 (1ms latency, 99.999% reliability)
   - UPF placement: Edge locations (MEC)

3. **mMTC Slice** (Massive Machine-Type Communications)
   - SST: 3, SD: 000001
   - Target: IoT sensors, smart meters
   - QoS: 5QI 8 (delay-tolerant, high connection density)
   - UPF placement: Central data centers with session aggregation

**Phase 3: Service-Based Interfaces (SBI) Configuration**

Configure HTTP/2-based SBI communication:

```yaml
# NRF Service Registration Example
NRF Configuration:
  - Service Registry: Consul or etcd-based
  - Load Balancing: Round-robin with health checks
  - Security: OAuth 2.0 token-based authentication, mTLS

Service Discovery:
  - AMF discovers SMF instances via NRF
  - SMF discovers UPF instances via NRF
  - All NFs publish heartbeats every 30 seconds

API Gateway:
  - Kong or Nginx for external API exposure
  - Rate limiting: 1000 requests/second per API
  - Monitoring: Prometheus metrics on all endpoints
```

**Phase 4: Interworking with 4G EPC**

Implement EPC-5GC interworking for mobility:

- **N26 Interface**: Enable AMF-MME signaling for idle mode mobility
- **Dual Registration**: Support simultaneous 4G/5G registration for seamless handover
- **Session Continuity**: Maintain PDU sessions during inter-RAT handover
- **HSS-UDM Interworking**: Deploy HSS+UDM consolidated function or sync data

**Phase 5: Edge Computing (MEC) Integration**

Deploy Multi-access Edge Computing platforms:

```
MEC Architecture:
  - Edge Locations: 10 sites co-located with major cell towers
  - UPF Deployment: Local UPF instances at each MEC site
  - Traffic Steering: Local breakout via UPF for edge applications
  - Platform: Kubernetes clusters with GPU support
  - Applications: AR/VR streaming, video analytics, cloud gaming

Traffic Routing:
  - DNS-based selection for edge application discovery
  - ULCL (Uplink Classifier) in UPF for traffic splitting
  - N9 tunneling between central and edge UPFs for session continuity
```

#### Validation and Testing

Key tests to perform:

1. **Registration and Authentication**: Verify AUSF/UDM authentication for 5G subscribers
2. **Session Establishment**: Test PDU session creation with different SST/SD combinations
3. **Mobility**: Validate handover between cells, gNodeBs, and 4G-5G inter-RAT
4. **Network Slicing**: Confirm isolation and QoS differentiation between slices
5. **Load Testing**: Stress test with 10K registrations/second, 50K session setups/second
6. **Failover**: Simulate NF failures and validate service continuity

#### Expected Outcomes

- 5G SA core network serving 2M+ subscribers with sub-10ms latency
- Three operational network slices supporting diverse use cases
- Seamless mobility between 4G and 5G networks
- Edge computing platform ready for third-party application deployment
- Cloud-native architecture enabling rapid service innovation

---

### Use Case 2: NFV Migration of Legacy IMS

#### Scenario

A telecommunications carrier operates a legacy IMS (IP Multimedia Subsystem) platform on proprietary hardware for VoLTE and VoWiFi services. The platform is end-of-life, expensive to maintain, and lacks scalability. The goal is to migrate to a virtualized IMS (vIMS) platform on NFV infrastructure with minimal service disruption.

**Current State:**
- Physical IMS with P/I/S-CSCF, HSS, BGCF, MGCF, AS (Application Servers)
- 1.2M VoLTE subscribers, 300K VoWiFi subscribers
- Peak load: 15,000 BHCA (Busy Hour Call Attempts)
- Average call duration: 3.5 minutes
- Required availability: 99.999% (5.26 minutes downtime/year)

#### Migration Strategy

**Phase 1: Assessment and Planning**

Conduct thorough assessment:

1. **Traffic Analysis**
   - Call Detail Records (CDRs) for past 12 months
   - Busy hour patterns, seasonal variations
   - Geographic distribution of subscribers
   - Service usage patterns (voice, video, messaging)

2. **Dependency Mapping**
   - Integration points with EPC (P-GW, PCRF)
   - Interconnections with PSTN gateways
   - Roaming partner SIP trunks
   - Value-added services (conference, voicemail)

3. **Capacity Planning**
   - Current: 15K BHCA = ~6,500 concurrent sessions (assuming 3.5 min duration)
   - vIMS Sizing: Target 30K BHCA for 100% growth headroom
   - Resource calculation: ~20-30 vCPUs per 10K BHCA for CSCF functions

**Phase 2: NFV Infrastructure Preparation**

Deploy NFVI using OpenStack:

```yaml
NFVI Architecture:
  Compute Nodes:
    - Quantity: 30 servers (15 per data center)
    - Specs: 2x Intel Xeon Gold 6140 (36 cores total), 384GB RAM
    - NUMA topology: Optimized for VNF placement
    - CPU pinning: Reserved cores for VNF workloads

  Network:
    - Provider Networks: SR-IOV for data plane (SIP signaling, RTP media)
    - Overlay Networks: VXLAN for control plane and management
    - Bandwidth: 2x 25Gbps NICs per server

  Storage:
    - Ceph distributed storage for VNF images and databases
    - SSD-based HSS database for low-latency subscriber queries
    - Backup: Daily snapshots with 30-day retention

  Orchestration:
    - MANO: Deploy ONAP or OSM for VNF orchestration
    - VIM: OpenStack Ussuri with Neutron ML2/OVS
    - VNFM: Vendor-specific managers for vCSCF, vHSS
```

**Phase 3: vIMS Deployment (Parallel Run)**

Deploy vIMS in parallel with legacy IMS:

```
vIMS Components:
  - vP-CSCF (Proxy-CSCF): Entry point for SIP signaling
    Instances: 6 (3 per site, N+1 redundancy)
    Capacity: 10K BHCA per instance

  - vI-CSCF (Interrogating-CSCF): Routes to appropriate S-CSCF
    Instances: 4 (2 per site)
    Capacity: 15K queries/second per instance

  - vS-CSCF (Serving-CSCF): Session control and service logic
    Instances: 8 (4 per site)
    Capacity: 5K BHCA per instance, 50K registered users

  - vHSS (Home Subscriber Server): Subscriber data repository
    Instances: 4 (2 per site, database replication)
    Capacity: 2M subscriber profiles, 20K TPS

  - vAS (Application Servers): Supplementary services
    Types: Telephony AS (TAS), Rich Communication Services (RCS)
    Instances: 4 (2 per site per AS type)

  - vSBC (Session Border Controller): Border security and interworking
    Instances: 6 (3 per site, high availability)
    Capacity: 10K concurrent sessions per instance
```

**Phase 4: Migration Execution**

Execute phased migration with fallback capability:

1. **Week 1-2: Pilot Migration (1% of users)**
   - Select 10,000 low-risk subscribers (non-premium, recent registrations)
   - Update HSS to point these subscribers to vIMS (S-CSCF assignment)
   - Monitor call success rate, audio quality (MOS scores), signaling latency
   - Rollback plan: HSS update to revert to legacy IMS

2. **Week 3-4: Early Adopters (10% of users)**
   - Migrate 120,000 subscribers across diverse demographics
   - Include premium subscribers and heavy users
   - 24/7 monitoring with incident response team
   - A/B testing: Compare KPIs between legacy and vIMS groups

3. **Week 5-8: Bulk Migration (80% of users)**
   - Migrate in batches of 100K subscribers per day
   - Automated HSS updates with validation scripts
   - Real-time dashboards tracking migration progress and health

4. **Week 9-10: Final Migration and Legacy Decommission (9% remaining)**
   - Migrate final 135,000 subscribers
   - Maintain legacy IMS on standby for 2 weeks
   - Conduct comprehensive testing (disaster recovery, failover, load)
   - Decommission legacy hardware after validation period

**Phase 5: Optimization and Automation**

Post-migration optimization:

- **Auto-Scaling**: Configure VNF auto-scaling based on BHCA and CPU utilization
- **Performance Tuning**: Optimize SIP session timers, database query caching
- **Monitoring**: Deploy distributed tracing (Jaeger) for end-to-end call flow visibility
- **Healing**: Implement auto-healing policies for VNF instance failures

#### Troubleshooting During Migration

Common issues and resolutions:

**Issue 1: High SIP Registration Failures**
- Symptom: 5% registration failure rate on vIMS vs. 0.1% on legacy
- Root Cause: vP-CSCF insufficient CPU during peak hours
- Resolution: Increase vP-CSCF instances from 6 to 9, enable CPU pinning

**Issue 2: Audio Quality Degradation**
- Symptom: MOS score drops from 4.2 to 3.6 on vIMS calls
- Root Cause: RTP packet loss due to NFVI network congestion
- Resolution: Enable SR-IOV for vSBC, implement QoS policies on NFVI network

**Issue 3: HSS Query Latency Spikes**
- Symptom: S-CSCF to HSS queries exceeding 100ms (target: <10ms)
- Root Cause: Database not using SSD storage, inefficient queries
- Resolution: Migrate HSS DB to SSD-backed Ceph pool, add database indexes

#### Expected Outcomes

- Successfully migrated 1.5M subscribers to vIMS with zero service outages
- Reduced operational costs by 40% (eliminated hardware maintenance)
- Improved scalability: Can now support 5M subscribers on same infrastructure
- Enhanced agility: New services deployed in days instead of months
- Achieved 99.999% availability with automated failover and healing

---

### Use Case 3: Convergent Billing System Implementation

#### Scenario

A mobile virtual network operator (MVNO) needs to implement a convergent billing system that supports prepaid and postpaid subscribers, real-time charging for data services, and flexible promotional campaigns. The system must integrate with the mobile core network (4G EPC and 5G Core) and support TM Forum Open API standards.

**Requirements:**
- Support 500K prepaid subscribers, 200K postpaid subscribers
- Real-time charging with subsecond response times
- Convergent charging: Voice (per minute), SMS (per message), Data (per MB/GB)
- Promotional capabilities: Data bundles, time-based promotions, loyalty programs
- Revenue assurance and fraud detection
- Integration with CRM, payment gateway, tax systems

#### Implementation Approach

**Phase 1: Architecture Design**

Design modular billing architecture:

```
Billing System Components:

1. Mediation Layer
   - Function: Collect usage data from network elements
   - Inputs: CDRs from MSC/MGW, UDRs from PGW/UPF, SMSC records
   - Processing: Parse, validate, enrich, correlate, deduplicate
   - Output: Normalized usage records (XDRs)
   - Technology: Apache NiFi or custom mediation with Kafka

2. Rating Engine
   - Function: Apply pricing rules to usage records
   - Inputs: XDRs from mediation, rate plans from product catalog
   - Processing: Rate lookup, tier calculation, discount application
   - Output: Rated records with monetary values
   - Technology: Drools rule engine or custom rating service

3. Online Charging System (OCS)
   - Function: Real-time balance management for prepaid
   - Protocol: Diameter Ro/Gy interface with PGW/UPF
   - Operations: Reserve quota, deduct balance, terminate on depletion
   - Response Time: <100ms for charging requests
   - Technology: Custom OCS or commercial (Ericsson ECM, Nokia OCCM)

4. Offline Charging System (OFCS)
   - Function: Post-processing of usage for postpaid
   - Inputs: CDRs from network, rated XDRs
   - Processing: Aggregation, billing cycle management
   - Output: Invoice-ready billing data
   - Technology: Custom batch processing or commercial billing engine

5. Product Catalog
   - Function: Define rate plans, bundles, promotions
   - Data Model: TM Forum Product Catalog (TMF620)
   - Features: Versioning, validity periods, complex bundling rules
   - Technology: Commercial catalog (Salesforce, Amdocs) or custom

6. Customer Account Management
   - Function: Manage subscriber accounts, balances, billing cycles
   - Data Model: TM Forum Customer Management (TMF629)
   - Features: Multi-wallet balances, payment history, credit limits
   - Technology: Integrated with CRM system

7. Billing and Invoicing
   - Function: Generate invoices, apply taxes, payment processing
   - Cycles: Monthly postpaid billing, prepaid recharges
   - Output: PDF invoices, electronic bills, tax reports
   - Technology: Jasper Reports or commercial invoice engine

8. Policy Control (PCRF/PCF)
   - Function: Enforce usage policies based on balance
   - Integration: Gx interface to PGW (4G), N7 interface to UPF (5G)
   - Policies: Speed throttling, content filtering, fair use
   - Technology: Open5GS PCF, commercial PCRF, or custom
```

**Phase 2: Network Integration**

Implement Diameter interfaces for charging:

**Gy Interface (OCS to PGW) - Prepaid Charging**

```
Diameter Credit Control Request (CCR)
Message Flow:
  1. Subscriber initiates data session
  2. PGW sends CCR-Initial to OCS
     AVPs:
       - Session-Id: Unique session identifier
       - Subscription-Id: IMSI or MSISDN
       - Requested-Service-Unit: Data volume requested (e.g., 10 MB)
       - Rating-Group: Service identifier (e.g., 1=Internet, 2=MMS)

  3. OCS processes request:
     - Validate subscriber account status
     - Check available balance
     - Reserve quota from balance
     - Apply rating rules for requested service

  4. OCS sends CCA-Initial (Credit Control Answer)
     AVPs:
       - Granted-Service-Unit: Approved quota (e.g., 10 MB)
       - Validity-Time: Duration quota is valid (e.g., 3600 seconds)
       - Result-Code: 2001 (Success) or error code

  5. During session: PGW sends CCR-Update when quota depleted or validity expires

  6. Session end: PGW sends CCR-Terminate with final usage
     OCS finalizes charges and returns final CCA

Policy Enforcement:
  - If balance insufficient: OCS returns Final-Unit-Indication
  - PGW redirects subscriber to portal or blocks service
  - Subscriber recharges, triggers immediate quota grant
```

**Gx Interface (PCRF to PGW) - Policy Control**

```
Diameter Credit Control Request (CCR) for Policy
Message Flow:
  1. PGW sends CCR-Initial to PCRF when session established
     AVPs:
       - Session-Id, Subscription-Id, IP-CAN-Type, RAT-Type
       - Called-Station-Id: APN (e.g., internet.mvno.com)

  2. PCRF queries subscriber profile (SPR) and OCS for balance

  3. PCRF sends CCA with Policy and Charging Control (PCC) rules
     AVPs:
       - Charging-Rule-Install: List of rules to apply
       - QoS-Information: QCI, ARP, bandwidth limits
       - Usage-Monitoring-Information: Quota and thresholds

  4. Dynamic policy updates:
     - Balance depletion: PCRF sends RAR (Re-Auth Request) to downgrade QoS
     - Promotional activation: PCRF sends RAR to upgrade QoS or remove limits
     - Time-based: PCRF sends RAR for happy hour promotions
```

**Phase 3: Rating Plan Configuration**

Define flexible rating plans:

```yaml
# Example: Prepaid Data Bundle
Product: "5GB Monthly Bundle"
  Price: $25
  Validity: 30 days
  Quota: 5 GB (5,368,709,120 bytes)

  Rating Rules:
    - In-Bundle Usage:
        Rate: $0/MB (included in bundle)
        Condition: Total usage < 5 GB AND within validity

    - Out-of-Bundle Usage:
        Rate: $0.10/MB
        Condition: Total usage > 5 GB OR after validity expiry

    - Speed Throttling:
        Trigger: 80% of quota consumed (4 GB)
        Action: Reduce speed to 512 Kbps
        Notification: Send SMS alert to subscriber

    - Rollover Policy:
        Condition: Renew before expiry
        Action: Rollover unused quota (max 2 GB) to next cycle

# Example: Postpaid Voice Plan
Product: "Unlimited Talk 500"
  Monthly Fee: $40
  Included Minutes: 500 minutes domestic voice

  Rating Rules:
    - Domestic Calls (In-Plan):
        Rate: $0/minute
        Condition: Monthly usage < 500 minutes

    - Domestic Calls (Overage):
        Rate: $0.25/minute
        Condition: Monthly usage > 500 minutes

    - International Calls:
        Rate: Zone-based ($0.50-$3.00/minute)
        Zones: [North America, Europe, Asia, ROW]

    - Roaming Calls:
        Rate: $1.50/minute outbound, $0.75/minute inbound

# Example: Promotional Campaign
Campaign: "Happy Hour Data"
  Schedule: Daily 2:00 AM - 6:00 AM
  Benefit: Unlimited data (no quota consumption)

  Implementation:
    - PCRF monitors time-of-day
    - During happy hour: Install PCC rule with zero rating
    - OCS does not decrement balance for usage in this period
    - Mediation tags records for reporting (no charge)
```

**Phase 4: Real-Time Charging Workflows**

Implement prepaid charging scenarios:

**Scenario 1: Standard Data Session**
```
Timeline:
T=0:    Subscriber enables mobile data
T=1s:   PGW → OCS: CCR-Initial requesting 10 MB quota
T=1.05s: OCS processes (50ms): Check balance ($10), reserve $1 for 10 MB
T=1.1s: OCS → PGW: CCA-Initial granting 10 MB, validity 1 hour
T=300s: Subscriber consumes 10 MB
T=300s: PGW → OCS: CCR-Update requesting additional quota
T=300.05s: OCS grants another 10 MB, reserves $1
T=1800s: Subscriber idle, session timeout
T=1800s: PGW → OCS: CCR-Terminate with final usage (23 MB)
T=1800.05s: OCS finalizes charge ($2.30), returns unused reservation
Result: Subscriber charged $2.30, balance reduced to $7.70
```

**Scenario 2: Balance Depletion Mid-Session**
```
Timeline:
T=0:    Subscriber balance: $0.50
T=1s:   PGW → OCS: CCR-Initial requesting 10 MB quota
T=1.05s: OCS checks balance, insufficient for 10 MB
        OCS grants partial quota: 5 MB (matches $0.50 balance)
        OCS includes Final-Unit-Indication AVP in CCA
T=1.1s: OCS → PGW: CCA with 5 MB quota and final unit action
T=1.1s: PGW applies FUI action: Allow 5 MB, then redirect to portal
T=300s: Subscriber consumes 5 MB
T=300s: PGW redirects subscriber to recharge portal (captive portal)
T=600s: Subscriber recharges $10 via portal
T=600s: Recharge system → OCS: Add $10 to balance
T=600.1s: OCS → PCRF: Notify balance replenished
T=600.2s: PCRF → PGW: RAR to restore service
T=600.3s: PGW → PCRF: RAA confirming service restored
T=600.4s: Subscriber resumes data session with new quota
```

**Phase 5: Revenue Assurance and Fraud Detection**

Implement controls to prevent revenue leakage:

```
Revenue Assurance Checks:

1. Reconciliation
   - Network Records vs. Billed Records: Daily comparison
   - Threshold: >1% discrepancy triggers investigation
   - Common issues: Lost CDRs, mediation errors, rating mismatches

2. Duplicate Detection
   - CDR Deduplication: Hash-based (IMSI+timestamp+duration)
   - Prevents: Double-charging from redundant network elements

3. Roaming Data Validation
   - Cross-check: Roaming partner TAP files vs. local CDRs
   - Prevents: Unbilled roaming usage, fraud via TAP manipulation

4. Fraud Detection Patterns
   - SIM Box Fraud: High volume of short-duration calls from single IMSI
   - Subscription Fraud: Multiple high-value recharges followed by heavy usage
   - International Revenue Share Fraud (IRSF): Calls to premium rate numbers
   - Wangiri Fraud: One-ring scam detection (sub-5 second calls, no answer)

5. Real-Time Alerts
   - Usage threshold breached: >10 GB in 1 hour (potential fraud or system error)
   - Geographic anomaly: IMSI active in two countries simultaneously
   - Velocity check: >100 voice calls per hour from single subscriber
```

#### Integration with External Systems

**CRM Integration (TM Forum TMF629 Customer Management API)**

```json
POST /customerManagement/v4/customer
{
  "name": "John Doe",
  "customerAccount": [{
    "accountBalance": {
      "amount": 50.00,
      "currency": "USD"
    },
    "billingCycle": {
      "dayOfMonth": 1,
      "frequency": "monthly"
    }
  }],
  "contactMedium": [{
    "type": "email",
    "medium": {
      "emailAddress": "john.doe@example.com"
    }
  }],
  "productOffering": [{
    "id": "PROD_5GB_MONTHLY",
    "name": "5GB Monthly Bundle"
  }]
}
```

**Payment Gateway Integration**

```
Payment Flow:
1. Subscriber initiates recharge via mobile app or USSD
2. Billing system → Payment Gateway: Tokenized payment request
3. Payment Gateway → Card Network: Authorization request
4. Card Network → Issuing Bank: Validate and approve
5. Issuing Bank → Card Network → Payment Gateway: Approval code
6. Payment Gateway → Billing system: Success notification
7. Billing system → OCS: Credit subscriber account
8. OCS → PCRF → PGW: Restore or upgrade service
9. Billing system → Subscriber: SMS confirmation with new balance

Security:
- PCI DSS compliance for card data handling
- Tokenization: Store tokens, not card numbers
- 3D Secure for online transactions
- Fraud scoring on recharge patterns
```

#### Expected Outcomes

- Convergent billing system supporting 700K subscribers with 99.9% uptime
- Real-time charging with average response time <50ms
- Flexible product catalog enabling rapid launch of new plans and promotions
- Revenue assurance achieving <0.5% leakage rate
- Fraud detection preventing $2M+ annual losses
- TM Forum Open API compliance enabling ecosystem partnerships

---

## Template Reference

The telecommunications skill includes templates for common scenarios. These templates provide starting configurations and best practices.

### Available Templates

**Note**: Templates are located in `/home/user/CLAUDE_SKILLS/26_telecommunications/templates/`

1. **5G Core Network Architecture**
   - Description: Reference architecture for 5G SA deployment
   - Includes: NF sizing, interface definitions, Kubernetes manifests
   - Use when: Planning greenfield 5G core deployment

2. **NFV Infrastructure Blueprint**
   - Description: OpenStack-based NFVI configuration
   - Includes: Nova, Neutron, Ceph configurations, SR-IOV setup
   - Use when: Building NFV infrastructure for VNF hosting

3. **VoLTE IMS Configuration**
   - Description: Complete IMS setup for VoLTE services
   - Includes: CSCF configurations, SIP routing, codec policies
   - Use when: Deploying or troubleshooting VoLTE services

4. **Diameter Routing Agent (DRA) Config**
   - Description: DRA for Diameter signaling routing
   - Includes: Routing tables, load balancing, failover rules
   - Use when: Implementing Diameter routing in core network

5. **Charging System Integration**
   - Description: OCS and PCRF integration templates
   - Includes: Diameter AVP mappings, PCC rules, quota management
   - Use when: Integrating billing with network policy control

6. **Network Slicing Template**
   - Description: Configuration for 5G network slicing
   - Includes: Slice definitions (SST/SD), QoS profiles, AMF configurations
   - Use when: Implementing differentiated network slices

7. **MANO TOSCA Templates**
   - Description: TOSCA-based VNF descriptors for orchestration
   - Includes: VNFD, NSD, scaling policies, healing policies
   - Use when: Deploying VNFs via MANO platforms (ONAP, OSM)

8. **Monitoring and Telemetry**
   - Description: Prometheus exporters and Grafana dashboards
   - Includes: KPI definitions, alert rules, visualization templates
   - Use when: Setting up observability for telecom networks

### Template Usage

Templates are provided as starting points and must be customized for your specific environment. Always:

- Review and understand all configuration parameters
- Validate against your network architecture and scale requirements
- Test in non-production environment before production deployment
- Consult vendor documentation for version-specific parameters
- Comply with regulatory and security requirements

---

## Best Practices

### 5G Network Design

1. **Cloud-Native Principles**
   - Deploy NFs as microservices with independent scaling
   - Use stateless design where possible (state in external databases)
   - Implement health checks and readiness probes for all NFs
   - Design for failure: Assume any component can fail at any time

2. **Security**
   - Implement zero-trust network architecture (mTLS between all NFs)
   - Use HTTPS/2 for all Service-Based Interfaces (SBI)
   - Enable OAuth 2.0 for API authentication
   - Encrypt signaling (IPsec) and user plane data (DTLS for SRTP)
   - Regularly patch and update NF software

3. **Performance Optimization**
   - Use SR-IOV or DPDK for high-throughput UPF instances
   - Enable CPU pinning and NUMA awareness for VNFs/CNFs
   - Implement connection pooling for database access (UDR, UDSF)
   - Cache frequently accessed data (subscriber profiles, policy rules)
   - Monitor and tune garbage collection for Java-based NFs

4. **High Availability**
   - Deploy NFs in N+K redundancy model (minimum N+1, prefer N+2)
   - Use geographic redundancy across multiple data centers
   - Implement stateless NFs with session continuity mechanisms
   - Configure automatic failover with health monitoring
   - Design for graceful degradation under partial failure

### NFV Best Practices

1. **Resource Management**
   - Implement resource quotas per VNF to prevent resource monopolization
   - Use anti-affinity rules to distribute VNF instances across hosts
   - Monitor resource utilization and set auto-scaling policies
   - Reserve dedicated cores for DPDK-based VNFs (avoid sharing)
   - Implement huge pages for memory-intensive VNFs

2. **Lifecycle Management**
   - Version control all VNF descriptors (VNFD, NSD) in Git
   - Implement blue-green or canary deployment strategies
   - Test VNF upgrades in staging environment before production
   - Automate rollback procedures for failed deployments
   - Maintain VNF image repository with versioning and security scanning

3. **Monitoring and Observability**
   - Collect metrics from NFVI, VNFs, and MANO layers
   - Implement distributed tracing for cross-VNF transactions
   - Set up alerting with clear escalation procedures
   - Create runbooks for common failure scenarios
   - Conduct regular chaos engineering exercises

### Billing System Best Practices

1. **Data Integrity**
   - Implement end-to-end checksums for CDR transmission
   - Use database transactions with ACID properties
   - Maintain audit logs for all balance modifications
   - Implement reconciliation between network and billing systems
   - Retain raw CDRs for regulatory compliance (typically 7 years)

2. **Performance and Scalability**
   - Partition databases by subscriber ID or date ranges
   - Use asynchronous processing for non-critical operations
   - Implement caching for frequently accessed data (rate plans, balances)
   - Design for horizontal scalability (shard OCS by subscriber ranges)
   - Optimize database queries with proper indexing

3. **Compliance and Security**
   - Comply with PCI DSS for payment card data handling
   - Implement encryption at rest and in transit for sensitive data
   - Maintain audit trails for all financial transactions
   - Implement role-based access control (RBAC) for billing systems
   - Regularly audit for compliance with local regulations (tax, data privacy)

---

## Troubleshooting

### Common Issues and Resolutions

#### Issue 1: High UE Registration Failure Rate in 5G

**Symptoms:**
- UEs unable to register with 5G network (Registration Reject messages)
- AMF logs show "Authentication failure" or "Subscription not found"
- Dashboard shows >5% registration failure rate (normal: <0.5%)

**Diagnosis:**

```bash
# Check AMF logs for failure reasons
kubectl logs -n telco deployment/amf-deployment | grep "Registration Reject"

# Common Result-Cause values:
# - 5GMM cause #7: 5GS services not allowed
# - 5GMM cause #11: PLMN not allowed
# - 5GMM cause #15: No suitable cells in tracking area

# Query UDM for subscriber data
curl -X GET https://udm.example.com/nudm-uecm/v1/imsi-001010000000001/registrations

# Check AUSF authentication logs
tail -f /var/log/ausf/authentication.log | grep FAILED
```

**Root Cause Analysis:**

1. **UDM/UDR Issues**
   - Subscriber profile not provisioned or incorrect
   - UDM unable to reach UDR (database connectivity)
   - Subscription data missing required fields (SUPI, PLMN, AMF info)

2. **Authentication Failures**
   - AUSF unable to verify credentials with UDM
   - 5G AKA authentication timeout (slow HSS/UDM response)
   - Incorrect K/OPc keys in subscriber profile

3. **Network Configuration**
   - AMF PLMN configuration mismatch with UE SIM
   - Tracking Area Code (TAC) not configured in AMF
   - NRF service discovery failure (AMF cannot find UDM/AUSF)

**Resolution Steps:**

```bash
# Step 1: Verify subscriber provisioning
# Check if subscriber exists in UDM
mysql -h udr-db -u admin -p -e "SELECT * FROM subscribers WHERE imsi='001010000000001';"

# Step 2: Test authentication path
# Send test registration via simulator
./5g-ue-simulator --imsi 001010000000001 --plmn 00101 --register

# Step 3: Check NRF service registry
curl https://nrf.example.com/nnrf-nfm/v1/nf-instances?nf-type=UDM

# Step 4: Verify AMF configuration
cat /etc/amf/amf.conf | grep -A 10 "PLMN"
# Ensure PLMN matches SIM card configuration

# Step 5: Increase logging for detailed diagnostics
kubectl edit deployment amf-deployment
# Set log level to DEBUG, restart AMF pods
```

**Prevention:**
- Implement automated subscriber provisioning with validation
- Set up monitoring alerts for registration failure rate >1%
- Conduct regular end-to-end testing with test SIMs
- Maintain consistency between AMF PLMN config and SIM provisioning

---

#### Issue 2: VoLTE Call Setup Failures

**Symptoms:**
- Calls failing to establish (SIP 4xx/5xx errors)
- One-way audio or no audio on established calls
- High Post-Dial Delay (PDD) >3 seconds (target: <1 second)

**Diagnosis:**

```bash
# Capture SIP signaling with tcpdump
tcpdump -i any -n port 5060 -w volte_debug.pcap

# Analyze with tshark
tshark -r volte_debug.pcap -Y sip -T fields -e sip.Method -e sip.Status-Code -e sip.r-uri

# Check P-CSCF logs for failures
tail -f /var/log/pcscf/sip.log | grep "INVITE\|BYE\|488\|500\|503"

# Verify IMS registration
./sipp_client --imsi 001010000000001 --register
# Should receive SIP 200 OK
```

**Common Failure Scenarios:**

**Scenario A: SIP 488 Not Acceptable Here**
```
Problem: Codec negotiation failure
Cause: P-CSCF and UE have incompatible codec lists

# Inspect SDP offer in INVITE
tshark -r volte_debug.pcap -Y "sip.Method == INVITE" -T fields -e sdp.media.format

# Expected: AMR-WB (octect-align=1), AMR-NB
# If missing: Check P-CSCF codec policy configuration

Resolution:
1. Update P-CSCF codec policy to include AMR-WB
2. Ensure SDP interworking function is enabled
3. Configure TrFO (Transcoding Free Operation) for optimal audio
```

**Scenario B: SIP 503 Service Unavailable**
```
Problem: S-CSCF cannot be reached
Cause: I-CSCF cannot find appropriate S-CSCF or S-CSCF overloaded

# Check I-CSCF to S-CSCF routing
curl -X POST https://hss.example.com/s6a/user-authorization-request \
  -d '{"imsi": "001010000000001"}'
# Should return assigned S-CSCF name

# Verify S-CSCF availability
curl https://scscf-1.ims.example.com:8080/health
# Should return 200 OK

Resolution:
1. Check S-CSCF capacity (current sessions vs. max sessions)
2. Scale S-CSCF if overloaded (add instances via MANO)
3. Verify I-CSCF load balancing configuration
4. Check HSS S-CSCF assignment logic
```

**Scenario C: One-Way Audio or No Audio**
```
Problem: RTP media stream not established
Cause: NAT traversal failure, firewall blocking RTP ports, or wrong IP in SDP

# Capture RTP packets
tcpdump -i any -n udp portrange 50000-60000 -w rtp_debug.pcap

# Analyze RTP streams
tshark -r rtp_debug.pcap -q -z rtp,streams

# Check SDP for correct IP addresses
tshark -r volte_debug.pcap -Y sdp -T fields -e sdp.connection_info.address

Resolution:
1. Verify P-CSCF is inserting correct IP in SDP (should be UE IP from PDP context)
2. Enable ICE (Interactive Connectivity Establishment) for NAT traversal
3. Configure SBC (Session Border Controller) for media anchoring
4. Check firewall rules allow RTP port range (typically UDP 50000-60000)
```

**Root Cause: Bearer Establishment Failure**
```
Problem: SIP call proceeds, but no QoS bearer established
Cause: PGW unable to create dedicated bearer due to PCRF policy or resource limits

# Check PCRF logs for policy decision
tail -f /var/log/pcrf/gx.log | grep "CCR\|CCA\|IMS"

# Verify Gx interface between PGW and PCRF
tshark -i any -d tcp.port==3868,diameter -Y diameter.cmd.code==272

# Expected: PCRF sends CCA with QCI=1 (Conversational Voice) and guaranteed bitrate

Resolution:
1. Verify PCRF has correct policy for IMS voice (QCI=1, ARP=2)
2. Check PGW capacity for dedicated bearers
3. Ensure subscriber profile in SPR has IMS service enabled
4. Validate P-CSCF sends correct AF signaling to PCRF (Rx interface)
```

**Prevention:**
- Implement SIP ladder diagram monitoring for call flow visibility
- Set up synthetic testing: Automated test calls every 5 minutes
- Monitor call setup success rate (target: >99%)
- Configure alerts for PDD >2 seconds or MOS <3.5

---

#### Issue 3: NFV Performance Degradation

**Symptoms:**
- VNF CPU utilization >90% but throughput is low
- High latency for VNF processing (>50ms)
- Packet drops observed in VNF virtual interfaces
- Inconsistent performance across VNF instances

**Diagnosis:**

```bash
# Check VNF resource allocation
openstack server show vnf-instance-1 | grep flavor
nova flavor-show <flavor-id>

# Verify CPU pinning
virsh vcpupin vnf-instance-1

# Check for CPU steal time (indicates overcommitment)
ssh vnf-instance-1
top
# Look at "%st" column - should be <1%

# Monitor NFVI resource utilization
openstack hypervisor stats show
# Check vcpus_used vs. vcpus (should have headroom)

# Inspect SR-IOV configuration
openstack port show <port-id> | grep vnic_type
# Should show "vnic_type = direct" for SR-IOV

# Check for NUMA placement issues
virsh numatune vnf-instance-1
# Verify VNF is pinned to specific NUMA node
```

**Common Root Causes:**

**Cause A: CPU Overcommitment**
```
Problem: Too many vCPUs allocated vs. physical cores
Detection:
  - High CPU steal time (>5%)
  - Inconsistent performance across instances
  - Load average >2x number of cores

Resolution:
# Adjust Nova CPU allocation ratio
openstack-config --set /etc/nova/nova.conf DEFAULT cpu_allocation_ratio 1.0
# Default is 16.0 (massive overcommit), set to 1.0 for VNFs

systemctl restart openstack-nova-compute

# Enable dedicated CPU policy for VNF flavor
openstack flavor set vnf-flavor --property hw:cpu_policy=dedicated
```

**Cause B: Insufficient Huge Pages**
```
Problem: VNF using standard 4KB pages instead of huge pages
Detection:
  cat /proc/meminfo | grep HugePages
  # HugePages_Free should be >0 and sufficient for VNFs

Resolution:
# Configure huge pages on compute nodes
echo 1024 > /proc/sys/vm/nr_hugepages
# Add to /etc/sysctl.conf for persistence
vm.nr_hugepages = 1024

# Update VNF flavor to require huge pages
openstack flavor set vnf-flavor --property hw:mem_page_size=large

# Restart VNF instances to apply
```

**Cause C: Network Bottlenecks**
```
Problem: Virtual switch (OVS) becoming bottleneck
Detection:
  ovs-vsctl show
  # Check port stats for drops
  ovs-ofctl dump-ports br-int | grep drop

Resolution:
# Enable DPDK for OVS
systemctl enable openvswitch
systemctl start openvswitch
ovs-vsctl set Open_vSwitch . other_config:dpdk-init=true
systemctl restart openvswitch

# Assign dedicated cores to OVS-DPDK
ovs-vsctl set Open_vSwitch . other_config:pmd-cpu-mask=0xF
# 0xF = cores 0-3 dedicated to Poll Mode Drivers

# Use SR-IOV to bypass OVS entirely for data plane
openstack network create --provider-physical-network physnet1 --provider-network-type vlan sriov-net
```

**Cause D: NUMA Mismatch**
```
Problem: VNF vCPUs and memory on different NUMA nodes
Detection:
  numastat -c vnf-process
  # High remote memory access indicates NUMA mismatch

Resolution:
# Configure NUMA topology awareness
openstack flavor set vnf-flavor --property hw:numa_nodes=1
# Force VNF to single NUMA node

# Pin VNF to specific NUMA node matching NICs
openstack flavor set vnf-flavor --property hw:numa_cpus.0=0,1,2,3,4,5,6,7
openstack flavor set vnf-flavor --property hw:numa_mem.0=16384
```

**Prevention:**
- Size NFVI with 20-30% headroom for bursts
- Implement resource tagging (dedicated vs. shared compute nodes)
- Monitor NFVI telemetry (CPU steal, memory pressure, network drops)
- Conduct regular performance testing and capacity planning
- Use placement groups to optimize VNF-to-physical-host mapping

---

#### Issue 4: Network Slice Isolation Failure

**Symptoms:**
- Traffic from one slice affecting another slice's performance
- QoS policies not being enforced correctly
- Slice SLA violations (latency, throughput below guaranteed levels)

**Diagnosis:**

```bash
# Verify slice configuration in AMF
kubectl exec -it amf-pod -- cat /config/slices.yaml

# Check if UE is associated with correct slice
curl https://amf.example.com/namf-comm/v1/ue-contexts/imsi-001010000000001
# Verify S-NSSAI (SST and SD values)

# Inspect UPF routing and QoS enforcement
kubectl exec -it upf-pod -- upfctl session list | grep <PDU-session-id>
# Verify QFI (QoS Flow Identifier) and 5QI values

# Check SMF session management logs
kubectl logs -n telco deployment/smf | grep "PDU Session Establishment"
```

**Root Cause Analysis:**

**Scenario A: Incorrect Slice Selection**
```
Problem: NSSF selecting wrong slice for UE
Cause: Subscriber profile missing or incorrect S-NSSAI configuration

Resolution:
# Update UDM subscriber profile
PUT /nudm-sdm/v2/imsi-001010000000001/am-data
{
  "nssai": {
    "defaultSingleNssais": [
      {"sst": 1, "sd": "000001"},  // eMBB slice
      {"sst": 2, "sd": "000001"}   // URLLC slice
    ],
    "allowedNssai": [
      {"sst": 1, "sd": "000001"},
      {"sst": 2, "sd": "000001"},
      {"sst": 3, "sd": "000001"}
    ]
  }
}

# Configure NSSF selection criteria
# Priority: URLLC (SST=2) over eMBB (SST=1) for enterprise subscribers
```

**Scenario B: QoS Policy Not Enforced**
```
Problem: UPF not differentiating traffic between slices
Cause: PCF not sending correct PCC rules or UPF not implementing them

Resolution:
# Verify PCF policy configuration for each slice
GET /npcf-smpolicycontrol/v1/sm-policies/<policy-id>

# Expected for URLLC slice (SST=2):
{
  "pccRules": {
    "rule-urllc-1": {
      "qosData": {
        "5qi": 82,  // URLLC QoS
        "maxbrUl": "100 Mbps",
        "maxbrDl": "100 Mbps"
      }
    }
  }
}

# Test QoS enforcement
# Generate traffic and measure latency
iperf3 -c upf-edge.example.com -t 60 -b 50M
# URLLC traffic should have <5ms latency, eMBB allows 50ms
```

**Scenario C: Resource Contention**
```
Problem: Slices sharing same UPF instance, no resource isolation
Cause: Inadequate infrastructure resource partitioning

Resolution:
# Deploy dedicated UPF instances per slice
kubectl label nodes edge-node-1 slice=urllc
kubectl label nodes central-node-1 slice=embb

# Update UPF deployment with node affinity
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upf-urllc
spec:
  template:
    spec:
      nodeSelector:
        slice: urllc
      containers:
      - name: upf
        resources:
          requests:
            memory: "32Gi"
            cpu: "16"
          limits:
            memory: "32Gi"
            cpu: "16"

# Configure CPU and memory quotas per slice
kubectl create quota slice-urllc --namespace=urllc-slice \
  --hard=requests.cpu=100,requests.memory=200Gi,limits.cpu=100,limits.memory=200Gi
```

**Prevention:**
- Implement strict resource quotas per network slice
- Use dedicated UPF instances for critical slices (URLLC)
- Monitor slice SLA compliance with per-slice dashboards
- Conduct regular slice isolation testing
- Implement admission control to prevent slice oversubscription

---

## Standards and Specifications

### 3GPP Specifications

The telecommunications industry relies heavily on 3GPP (3rd Generation Partnership Project) specifications. Key document series:

**5G System Architecture (Series 23)**

- **TS 23.501**: System architecture for the 5G System (5GS)
  - Defines 5G Core architecture, network functions, service-based architecture
  - Reference point representations, roaming architecture
  - Current Release: 3GPP Release 18

- **TS 23.502**: Procedures for the 5G System (5GS)
  - Registration, mobility, session management procedures
  - Interworking with EPC, service continuity
  - Network slicing procedures, policy control

- **TS 23.503**: Policy and charging control framework for the 5G System
  - PCF functionality, policy control, QoS framework
  - Charging architecture, sponsored connectivity

- **TS 23.548**: 5G System Enhancements for Edge Computing
  - Multi-access Edge Computing (MEC) architecture
  - Traffic steering, DNS handling, edge application enablement

**5G Network Interfaces (Series 29)**

- **TS 29.500**: 5G System - Technical Realization of Service Based Architecture
  - HTTP/2 binding for SBI, service discovery, security
  - Common data types, error handling

- **TS 29.502**: Session Management Services (Nsmf)
  - SMF services exposed via SBI
  - PDU session management APIs

- **TS 29.503**: Unified Data Management Services (Nudm)
  - UDM services for subscriber data retrieval
  - Authentication, registration management

- **TS 29.571**: Common Data Types for Service Based Interfaces
  - Standardized data structures used across all NF services

**Charging and Billing (Series 32)**

- **TS 32.240**: Charging architecture and principles
  - Offline and online charging architecture
  - Charging data function, charging trigger function

- **TS 32.251**: Packet Switched (PS) domain charging
  - CDR formats, charging information for data sessions
  - Applicable to 4G EPC and 5G charging

- **TS 32.298**: Charging Data Record (CDR) parameter description
  - Detailed CDR field definitions
  - Used by billing mediation systems

**IMS and VoLTE (Series 24)**

- **TS 24.229**: IP Multimedia Call Control Protocol (SIP)
  - SIP procedures for IMS
  - Registration, session establishment, mobility

- **TS 24.301**: EPS Mobility Management (EMM) and Session Management (ESM)
  - Bearer establishment for VoLTE
  - QoS procedures, dedicated bearer setup

### ETSI Standards

**NFV Specifications (GS NFV series)**

- **GS NFV 002**: NFV Architectural Framework
  - Defines VNF, NFVI, MANO components
  - Reference architecture for NFV deployments

- **GS NFV-MAN 001**: NFV Management and Orchestration
  - MANO functional blocks: NFVO, VNFM, VIM
  - Interfaces: Or-Vi, Ve-Vnfm, Or-Vnfm

- **GS NFV-INF 003**: NFV Infrastructure Compute Domain
  - Compute node requirements, hypervisor specifications
  - Performance and resource management

- **GS NFV-INF 004**: NFV Infrastructure Hypervisor Domain
  - Hypervisor capabilities, resource abstraction
  - Support for SR-IOV, NUMA, huge pages

- **GS NFV-TST 001**: Pre-deployment Testing; Report on Validation of NFV Environments
  - Test methodologies for NFV infrastructure
  - Performance benchmarking, interoperability testing

**MEC Specifications (GS MEC series)**

- **GS MEC 003**: Multi-access Edge Computing Framework
  - MEC architecture, MEC platform, MEC applications
  - Integration with NFV MANO

- **GS MEC 010**: Mobile Edge Management
  - MEC platform manager, lifecycle management
  - Service registry, traffic rules control

### TM Forum Frameworks

**Open APIs (TMF APIs)**

- **TMF620**: Product Catalog Management API
  - Define and manage product offerings
  - Bundling, pricing, lifecycle management

- **TMF629**: Customer Management API
  - Customer account management
  - Contact information, billing accounts

- **TMF633**: Service Catalog Management API
  - Service specifications, service offerings
  - SLA templates, service dependencies

- **TMF634**: Resource Catalog Management API
  - Physical and virtual resource definitions
  - Network elements, compute, storage

- **TMF635**: Usage Management API
  - Usage record collection and aggregation
  - Integration with mediation and billing

- **TMF637**: Product Inventory Management API
  - Track product instances assigned to customers
  - Product lifecycle states, configurations

- **TMF641**: Service Ordering API
  - Service order creation, tracking, completion
  - Order orchestration workflows

- **TMF678**: Customer Bill Management API
  - Bill generation, bill presentation
  - Payment application, balance management

**Open Digital Architecture (ODA)**

- Component-based architecture for telecom BSS/OSS
- Microservices-based, cloud-native design
- Standardized component interfaces (Open APIs)
- Canvas: Visual representation of ODA components and their interactions

**Frameworx**

- Business Process Framework (eTOM): Process reference model
- Information Framework (SID): Data and information model
- Application Framework (TAM): Application component model

### Other Relevant Standards

**IETF RFCs**

- **RFC 3261**: SIP (Session Initiation Protocol)
- **RFC 6733**: Diameter Base Protocol
- **RFC 7540**: HTTP/2 (used in 5G SBI)
- **RFC 9000**: QUIC (used for low-latency transport)
- **RFC 4960**: SCTP (Stream Control Transmission Protocol)

**ITU-T Recommendations**

- **Q.1912.5**: Interworking between SIP and ISUP/BICC
- **E.164**: International public telecommunication numbering plan
- **E.800 series**: Quality of Service and performance

**MEF Standards**

- **MEF 3.0**: SD-WAN service definitions
- **MEF 70**: SD-WAN Service Attributes and Services
- Used for enterprise connectivity and managed services

---

## Glossary

**3GPP**: 3rd Generation Partnership Project - Standards body for mobile telecommunications

**5GC**: 5G Core network - Core network for 5G systems

**5QI**: 5G QoS Identifier - QoS level indicator in 5G (similar to QCI in 4G)

**AMF**: Access and Mobility Management Function - Handles UE registration and mobility in 5G

**BHCA**: Busy Hour Call Attempts - Peak call volume metric

**BSS**: Business Support Systems - Billing, CRM, and customer-facing systems

**CDR**: Call Detail Record - Record of call/session usage for billing

**CNF**: Containerized Network Function - Network function running in containers (Kubernetes)

**CSCF**: Call Session Control Function - IMS components (P-CSCF, I-CSCF, S-CSCF)

**eMBB**: Enhanced Mobile Broadband - 5G use case for high-speed data

**EPC**: Evolved Packet Core - 4G LTE core network

**GTP**: GPRS Tunneling Protocol - Protocol for mobile user plane data encapsulation

**IMS**: IP Multimedia Subsystem - Framework for delivering multimedia services over IP

**MANO**: Management and Orchestration - NFV orchestration framework

**MEC**: Multi-access Edge Computing - Computing capabilities at network edge

**MME**: Mobility Management Entity - Control plane element in 4G EPC

**mMTC**: Massive Machine-Type Communications - 5G use case for IoT

**NFV**: Network Functions Virtualization - Virtualization of network services

**NFVI**: NFV Infrastructure - Compute, storage, and network resources for NFV

**OCS**: Online Charging System - Real-time charging for prepaid services

**OFCS**: Offline Charging System - Post-processing charging for postpaid

**OSS**: Operations Support Systems - Network management and operations systems

**PCRF**: Policy and Charging Rules Function - Policy control in 4G (replaced by PCF in 5G)

**PCF**: Policy Control Function - Policy control in 5G

**PDU**: Protocol Data Unit - Data packet in 5G (PDU Session = data connection)

**PGW**: Packet Data Network Gateway - 4G EPC gateway to external networks

**RAN**: Radio Access Network - Radio base stations and controllers

**SBA**: Service-Based Architecture - 5G core architecture using HTTP/2-based services

**SBI**: Service-Based Interface - HTTP/2 interfaces in 5G core

**SDP**: Session Description Protocol - Describes media sessions (codecs, IP addresses)

**SGW**: Serving Gateway - 4G EPC gateway routing user plane data

**SIP**: Session Initiation Protocol - Signaling protocol for IMS/VoIP

**SMF**: Session Management Function - Session management in 5G

**S-NSSAI**: Single Network Slice Selection Assistance Information - Identifies network slice (SST + SD)

**URLLC**: Ultra-Reliable Low-Latency Communications - 5G use case for mission-critical applications

**UDM**: Unified Data Management - Subscriber data management in 5G (replaces HSS)

**UPF**: User Plane Function - User data forwarding in 5G (replaces SGW/PGW)

**VNF**: Virtual Network Function - Virtualized network function

**VNFM**: VNF Manager - Manages VNF lifecycle (MANO component)

**VoLTE**: Voice over LTE - Voice calls over 4G LTE network using IMS

**VoNR**: Voice over New Radio - Voice calls over 5G NR using IMS

---

## Additional Resources

### Official Documentation

**3GPP Specifications Portal**
- URL: https://www.3gpp.org/specifications
- Access to all 3GPP technical specifications and reports
- Search by release, series number, or keyword

**ETSI NFV Portal**
- URL: https://www.etsi.org/technologies/nfv
- NFV specifications, white papers, and proof of concepts
- NFV Industry Specification Group (ISG) publications

**TM Forum**
- URL: https://www.tmforum.org
- Open API specifications, ODA documentation
- Best practices and use cases from operators

### Open Source Projects

**Open5GS**
- URL: https://open5gs.org
- Open-source 5G Core and EPC implementation
- Suitable for testing, research, and small-scale deployments

**free5GC**
- URL: https://free5gc.org
- Open-source 5G core network implementation
- Written in Go, supports network slicing and UPF

**ONAP (Open Network Automation Platform)**
- URL: https://www.onap.org
- Comprehensive open-source MANO platform
- Used by major operators for NFV orchestration

**OSM (Open Source MANO)**
- URL: https://osm.etsi.org
- ETSI-hosted open-source MANO project
- Lightweight alternative to ONAP

**Kamailio**
- URL: https://www.kamailio.org
- Open-source SIP server
- Used for building IMS components (P-CSCF, I-CSCF, S-CSCF)

**OpenStack**
- URL: https://www.openstack.org
- Open-source cloud platform for NFVI
- Widely adopted VIM for NFV deployments

**Kubernetes**
- URL: https://kubernetes.io
- Container orchestration platform
- Foundation for CNF deployments

### Learning Resources

**3GPP Portal - Introductions**
- URL: https://www.3gpp.org/technologies
- High-level overviews of 5G, LTE, IMS technologies

**Telecom Infra Project (TIP)**
- URL: https://telecominfraproject.com
- Open RAN, vRAN, and Open Optical & Packet Transport projects
- Collaboration on disaggregated telecom infrastructure

**GSMA (GSM Association)**
- URL: https://www.gsma.com
- Mobile industry insights, roaming agreements
- IoT and mobile money initiatives

**O-RAN Alliance**
- URL: https://www.o-ran.org
- Open Radio Access Network specifications
- Intelligent RAN controllers and RAN automation

**Linux Foundation Networking**
- URL: https://www.lfnetworking.org
- Hosts multiple telecom open-source projects (ONAP, Tungsten Fabric, Akraino)

### Testing and Validation Tools

**SIPp**
- URL: http://sipp.sourceforge.net
- SIP protocol testing and traffic generation
- Essential for IMS/VoLTE testing

**iperf3**
- URL: https://iperf.fr
- Network throughput testing
- Validate UPF/PGW user plane performance

**Wireshark**
- URL: https://www.wireshark.org
- Protocol analyzer supporting SIP, Diameter, GTP, HTTP/2
- Indispensable for telecom troubleshooting

**tcpdump**
- Standard packet capture tool
- Lightweight alternative to Wireshark for headless servers

**Diameter Stack (freeDiameter)**
- URL: http://www.freediameter.net
- Open-source Diameter protocol implementation
- Used for building Diameter clients and testing

### Community and Forums

**Stack Overflow - Tags**
- [5g], [lte], [sip], [ims], [nfv], [telecom]
- Active community for Q&A

**Reddit Communities**
- r/networking, r/telecom, r/kubernetes
- Discussions on implementations and troubleshooting

**TelecomEngine Forums**
- Various vendor-specific and technology forums
- Hands-on experience sharing from practitioners

### Training and Certification

**3GPP Training**
- Offered by various providers (Tonex, Telcoma, EXFO University)
- Covers 5G, LTE, IMS, core network technologies

**Cloud Native Computing Foundation (CNCF) Certifications**
- Certified Kubernetes Administrator (CKA)
- Certified Kubernetes Application Developer (CKAD)
- Relevant for CNF deployments

**OpenStack Certification**
- Certified OpenStack Administrator (COA)
- Useful for NFVI management

**TM Forum Certifications**
- Frameworx certification programs
- OSS/BSS architecture and best practices

---

## Getting Help

For assistance with the Telecommunications Cloud Skill:

1. **Provide Detailed Context**: Share your network architecture, software versions, error messages, and what you've already tried
2. **Include Relevant Logs**: Sanitize and include relevant log excerpts showing the issue
3. **Specify Standards Compliance**: Mention which 3GPP release, ETSI specifications, or TM Forum APIs you're targeting
4. **Ask Specific Questions**: Frame questions with technical details rather than general inquiries

Example of a well-formed question:
```
"I'm deploying a 5G SA core network based on 3GPP Release 16. My AMF (v2.4.3) is unable
to complete UE registration for subscribers with slice SST=2 (URLLC). The AMF logs show
'NSSF returned empty allowed NSSAI' for these subscribers, but SST=1 (eMBB) registrations
work fine. I've verified the UDM subscriber profiles include both slices in allowedNssai.
My NSSF is v2.3.1, and the configuration includes both slice definitions. What could be
causing NSSF to filter out SST=2, and how do I debug the NSSF selection logic?"
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: Claude Code Telecommunications Skill Team
**License**: For use with Claude Code skills ecosystem

**Feedback**: This is a living document. If you identify gaps, errors, or have suggestions for improvement, please provide feedback for future updates.

---

## Conclusion

The Telecommunications Cloud Skill is designed to be your expert companion for navigating the complex world of modern telecommunications infrastructure. Whether you're deploying a 5G network, migrating to NFV, implementing billing systems, or troubleshooting protocol issues, this skill provides the knowledge and guidance needed to succeed.

Remember to always validate recommendations against your specific requirements, test thoroughly in non-production environments, and consult official standards documentation for definitive guidance. The telecommunications field evolves rapidly, so stay current with the latest 3GPP releases, ETSI specifications, and industry best practices.

Welcome to the future of telecommunications engineering with AI-assisted expertise.
