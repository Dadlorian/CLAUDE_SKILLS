# Network Design Documentation Standards

## Overview

This guide establishes comprehensive standards for creating network design documents, including High-Level Designs (HLD), Low-Level Designs (LLD), capacity planning documentation, and network change request formats. Proper design documentation is critical for stakeholder communication, implementation guidance, and long-term network operations.

**Key References:**
- TOGAF (The Open Group Architecture Framework)
- Cisco Enterprise Network Design Guide
- Juniper Enterprise Design Fundamentals
- ITIL Service Design (TSO, 2011)
- "Top-Down Network Design" by Priscilla Oppenheimer (Cisco Press, 3rd Edition)
- "Optimal Routing Design" by Russ White (Cisco Press)
- RFC 2196 - Site Security Handbook

## Document Hierarchy

### Design Document Lifecycle

```
Design Document Flow:

[Business Requirements]
         ↓
[Requirements Analysis Document]
         ↓
[High-Level Design (HLD)]
    ↓           ↓
[Technical     [Capacity
Assessment]    Planning]
    ↓           ↓
[Low-Level Design (LLD)]
         ↓
[Implementation Plan]
         ↓
[Test & Validation Plan]
         ↓
[As-Built Documentation]
         ↓
[Operations Handover]
```

## Requirements Analysis Document

### Business Requirements Section

**Template Structure:**

```markdown
# Requirements Analysis Document (RAD)
## Project: [Network Infrastructure Upgrade]
## Version: 1.0
## Date: 2024-01-15
## Author: Network Architecture Team

### 1. Executive Summary

Brief overview (1-2 paragraphs) of:
- Business driver for the project
- High-level scope
- Expected outcomes
- Timeline and budget constraints

### 2. Business Requirements

#### 2.1 Strategic Objectives
- Support for business growth (e.g., 30% user increase over 2 years)
- New service enablement (e.g., cloud migration, SD-WAN)
- Cost optimization targets (e.g., 20% OPEX reduction)
- Compliance requirements (PCI-DSS, HIPAA, SOX, GDPR)

#### 2.2 Performance Requirements
- Bandwidth requirements per site/user
- Latency requirements for applications
- Availability targets (99.9%, 99.99%, etc.)
- Recovery time objectives (RTO) and recovery point objectives (RPO)

#### 2.3 Security Requirements
- Data classification levels (public, confidential, restricted)
- Regulatory compliance (list specific regulations)
- Access control requirements
- Encryption requirements (data in transit, at rest)

#### 2.4 Scalability Requirements
- Expected growth projections (users, sites, traffic)
- Timeline for scaling needs
- Geographic expansion plans

### 3. Technical Requirements

#### 3.1 Capacity Requirements
| Metric | Current | Year 1 | Year 2 | Year 3 |
|--------|---------|--------|--------|--------|
| Total Users | 5,000 | 6,000 | 7,500 | 9,000 |
| Sites | 50 | 55 | 65 | 75 |
| Data Center Servers | 500 | 650 | 800 | 1,000 |
| Internet Bandwidth (Mbps) | 2,000 | 3,000 | 5,000 | 7,500 |
| WAN Bandwidth (Mbps) | 10,000 | 15,000 | 20,000 | 25,000 |

#### 3.2 Application Requirements
List critical applications with their network requirements:

**Application: Microsoft Teams**
- Protocol: UDP/TCP
- Ports: 80, 443, 3478-3481, 50000-50059
- Bandwidth: 1.5 Mbps per video call
- Latency: < 100ms
- Packet Loss: < 1%
- Jitter: < 30ms
- QoS: DSCP EF (46) for audio, DSCP AF41 (34) for video

**Application: SAP ERP**
- Protocol: TCP
- Ports: 3200-3299, 3300-3399
- Bandwidth: 50-100 Kbps per user
- Latency: < 150ms
- Transaction response time: < 2 seconds
- QoS: DSCP AF31 (26)

#### 3.3 Availability Requirements
- Network uptime: 99.99% (52.56 minutes downtime/year)
- Planned maintenance windows: Monthly, Saturday 2-6 AM
- Redundancy requirements: N+1 for critical infrastructure
- Disaster recovery: Active-active data centers

### 4. Constraints

#### 4.1 Budget Constraints
- Total budget: $2.5M
- CAPEX allocation: $1.8M
- OPEX allocation: $700K annually

#### 4.2 Timeline Constraints
- Design phase: 6 weeks
- Procurement: 8 weeks
- Implementation: 12 weeks
- Testing and cutover: 4 weeks
- Total project duration: 30 weeks

#### 4.3 Technical Constraints
- Must integrate with existing Cisco infrastructure
- Limited rack space in existing data centers
- Cannot disrupt production during business hours
- Must support legacy applications (minimum 2 years)

### 5. Assumptions and Dependencies

**Assumptions:**
- Current network documentation is accurate
- Existing cabling infrastructure is adequate
- Power and cooling capacity available
- ISP circuits can be delivered on schedule

**Dependencies:**
- Data center construction completion (external project)
- Security policy approval from InfoSec team
- Budget approval from finance
- Vendor selection and contract execution

### 6. Success Criteria

- Network availability meets or exceeds 99.99%
- Application performance meets defined SLAs
- Implementation completed on time and within budget
- Zero critical incidents during cutover
- User satisfaction score > 4.5/5.0
- All compliance requirements met

### 7. Stakeholders

| Role | Name | Department | Responsibilities |
|------|------|------------|------------------|
| Executive Sponsor | John Smith | CIO Office | Budget approval, strategic direction |
| Project Manager | Jane Doe | IT PMO | Timeline, resource coordination |
| Network Architect | Bob Johnson | Network Ops | Design, technical decisions |
| Security Architect | Alice Williams | InfoSec | Security requirements, compliance |
| Application Owner | Mike Brown | Business Apps | Application requirements |
```

### Gap Analysis

**Current State vs. Future State Analysis:**

```markdown
## Gap Analysis

### Current State Assessment

**Network Architecture:**
- Three-tier architecture (core/distribution/access)
- Aging hardware (5-7 years old)
- Limited redundancy (single core in some sites)
- Manual configuration management
- Limited monitoring and visibility

**Performance:**
- Average network utilization: 45%
- Peak utilization: 78% (approaching capacity)
- Average latency: 25ms (intra-site), 85ms (inter-site)
- Availability: 99.7% (26 hours downtime/year)

**Challenges:**
- Capacity constraints during peak hours
- Limited scalability for cloud migration
- Manual troubleshooting (high MTTR)
- Inconsistent security policies
- Lack of automation

### Future State Vision

**Network Architecture:**
- Leaf-spine architecture in data centers
- SD-WAN for branch connectivity
- Cloud-integrated hybrid architecture
- Automated configuration management (Ansible/Terraform)
- Comprehensive monitoring (NetFlow, SNMP, streaming telemetry)

**Performance:**
- Network utilization: 30% average (room for growth)
- Sub-millisecond latency (intra-DC)
- Availability: 99.99%
- Automated failover (< 1 second)

**Benefits:**
- 3x capacity headroom
- 50% reduction in MTTR
- 40% reduction in manual configuration tasks
- Consistent security policy enforcement
- Support for cloud-native applications

### Gap Summary

| Category | Current | Target | Gap | Priority |
|----------|---------|--------|-----|----------|
| Availability | 99.7% | 99.99% | 0.29% | Critical |
| Capacity | 2 Gbps | 10 Gbps | 8 Gbps | High |
| Latency (intra-DC) | 5ms | < 1ms | 4ms | Medium |
| Automation | 10% | 80% | 70% | High |
| Security | 60% compliant | 100% | 40% | Critical |
```

## High-Level Design (HLD)

### HLD Document Template

```markdown
# High-Level Design (HLD)
## Project: Next-Generation Campus Network
## Version: 2.0
## Date: 2024-01-20
## Status: Approved

### Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-10 | Network Team | Initial draft |
| 1.5 | 2024-01-15 | Network Team | Incorporated review comments |
| 2.0 | 2024-01-20 | Network Team | Final approved version |

**Reviewers:**
- Network Architecture Team: Approved
- Security Team: Approved with conditions (see section 7.3)
- Infrastructure Team: Approved
- CIO: Approved

**Approvals:**
- Chief Architect: [Signature] Date: 2024-01-20
- CISO: [Signature] Date: 2024-01-20
- VP Infrastructure: [Signature] Date: 2024-01-20

---

## 1. Executive Summary

This High-Level Design describes the architecture for the next-generation campus network
supporting 10,000 users across 5 buildings. The design implements a modern leaf-spine
architecture with full redundancy, automated provisioning, and comprehensive security.

**Key Highlights:**
- 99.99% availability (N+1 redundancy throughout)
- 100 Gbps backbone capacity
- Sub-millisecond intra-campus latency
- Zero-touch provisioning for endpoints
- Integrated security (Cisco TrustSec, 802.1X)
- Full automation with Ansible

**Investment:**
- Total cost: $2.3M
- ROI: 18 months
- Annual OPEX savings: $450K

---

## 2. Architecture Overview

### 2.1 Logical Architecture

                    ┌─────────────────┐
                    │   Internet      │
                    │   (Dual ISPs)   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  Firewall Pair  │
                    │  (Active/Active)│
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   Core Layer    │
                    │  (2x N9K-C9508) │
                    │   vPC Pair      │
                    └────┬──────┬─────┘
                         │      │
              ┌──────────┘      └──────────┐
              │                             │
      ┌───────┴────────┐           ┌───────┴────────┐
      │ Distribution A  │           │ Distribution B  │
      │  (2x N9K-93180) │           │  (2x N9K-93180) │
      │   vPC Pair      │           │   vPC Pair      │
      └────┬──────┬─────┘           └────┬──────┬────┘
           │      │                      │      │
     ┌─────┴─┐ ┌─┴────┐           ┌─────┴─┐ ┌─┴────┐
     │Access │ │Access│           │Access │ │Access│
     │ Sw 1  │ │ Sw 2 │           │ Sw 3  │ │ Sw 4 │
     └───────┘ └──────┘           └───────┘ └──────┘

### 2.2 Design Principles

1. **High Availability**
   - No single point of failure
   - N+1 redundancy for all critical components
   - Sub-second failover times
   - Dual power feeds to all devices

2. **Scalability**
   - Modular design supports 5,000 additional users
   - 50% capacity headroom built-in
   - Easy addition of access layer switches

3. **Security**
   - Defense in depth (multiple security layers)
   - Zero trust network architecture
   - Encrypted management traffic
   - Comprehensive logging and monitoring

4. **Automation**
   - Zero-touch provisioning (ZTP)
   - Automated configuration management
   - Self-healing capabilities
   - Automated compliance checking

5. **Performance**
   - Oversubscription ratios:
     * Access to Distribution: 20:1
     * Distribution to Core: 4:1
     * Core to Internet: 2:1
   - QoS for latency-sensitive applications
   - Traffic engineering with ECMP

---

## 3. Technology Selection

### 3.1 Vendor Selection Criteria

**Evaluation Criteria:**
1. Performance and scalability (40%)
2. Total cost of ownership (25%)
3. Vendor support and services (15%)
4. Feature set and roadmap (10%)
5. Integration with existing infrastructure (10%)

**Vendor Comparison:**

| Vendor | Score | Strengths | Weaknesses |
|--------|-------|-----------|------------|
| Cisco | 92/100 | Market leader, broad portfolio, strong support | Higher cost |
| Arista | 88/100 | Performance, automation, cloud integration | Limited campus portfolio |
| Juniper | 85/100 | Strong routing, competitive pricing | Less familiar to team |

**Decision: Cisco**
- Best alignment with existing infrastructure
- Comprehensive campus and data center portfolio
- Strong automation capabilities (Cisco DNA Center)
- Existing team expertise

### 3.2 Hardware Platform Selection

**Core Layer:**
- Platform: Cisco Nexus 9508
- Line cards: 48-port 100GbE QSFP28
- Supervisors: Redundant supervisor engines
- Quantity: 2 (vPC pair)
- Rationale: Modular chassis supports future growth, line-rate performance

**Distribution Layer:**
- Platform: Cisco Nexus 93180YC-FX
- Ports: 48x 1/10/25G + 6x 40/100G
- Quantity: 4 (2 vPC pairs)
- Rationale: High port density, support for 25G servers

**Access Layer:**
- Platform: Cisco Catalyst 9300-48P
- Ports: 48x 1G PoE+ + 4x 10G uplinks
- Quantity: 20
- Rationale: PoE+ for wireless APs, stackable, DNA Center support

**Wireless:**
- Controller: Cisco Catalyst 9800 (redundant pair)
- Access Points: Cisco Catalyst 9120AXI (Wi-Fi 6)
- Quantity: 150 APs
- Rationale: Wi-Fi 6, high density support

---

## 4. Capacity Planning

### 4.1 Bandwidth Calculations

**User Bandwidth Requirements:**
```
Average bandwidth per user: 2 Mbps
Peak bandwidth per user: 8 Mbps
Total users: 10,000

Average total: 10,000 × 2 Mbps = 20 Gbps
Peak total: 10,000 × 8 Mbps = 80 Gbps

With 50% headroom: 80 Gbps × 1.5 = 120 Gbps
```

**Internet Bandwidth:**
```
Current: 2 Gbps (2x 1G ISP circuits)
Projected peak: 15 Gbps (20% of internal traffic)
Recommended: 2x 10G ISP circuits (20 Gbps total)
Headroom: 33%
```

**Storage Network:**
```
Total servers: 500
Average I/O per server: 500 MB/s
Peak aggregate: 250 GB/s
Network bandwidth: 25G per server (sufficient)
```

### 4.2 Port Capacity Planning

**Access Layer:**
```
Total endpoints: 12,000 (10,000 users + 2,000 devices)
Ports per switch: 48
Required switches: 12,000 / 48 = 250
With 20% spare: 250 × 1.2 = 300 ports

Deployed switches: 20 (960 ports)
Growth capacity: 960 - 250 = 710 ports (284% headroom)
```

**Uplink Capacity:**
```
Access to Distribution:
- Per access switch: 2x 10G (vPC to distribution pair)
- Total 20 switches: 40x 10G = 400 Gbps
- Expected utilization: 30% average

Distribution to Core:
- Per distribution switch: 4x 100G
- Total 4 switches: 16x 100G = 1,600 Gbps
- Expected utilization: 15% average
```

### 4.3 Oversubscription Ratios

```
Access Layer:
- 48x 1G downlinks
- 2x 10G uplinks
- Ratio: 48:20 = 2.4:1 (acceptable for typical office)

Distribution Layer:
- Downlinks: 10x 10G (to access switches)
- Uplinks: 4x 100G (to core)
- Ratio: 100:400 = 1:4 (no oversubscription)

Core Layer:
- Downlinks: 16x 100G (to distribution)
- Uplinks: 2x 100G (to Internet/WAN)
- Ratio: 1,600:200 = 8:1 (acceptable, most traffic is east-west)
```

---

## 5. Routing and Switching Design

### 5.1 Layer 2 Design

**VLAN Strategy:**
- VLANs localized to building/floor (no stretched VLANs)
- 802.1Q trunking between switches
- Native VLAN: 999 (unused VLAN for security)
- Management VLAN: 10 (dedicated, restricted access)

**Spanning Tree:**
- Protocol: Rapid-PVST+ (Rapid Per-VLAN Spanning Tree Plus)
- Root bridge: Primary core switch (priority 4096)
- Secondary root: Secondary core switch (priority 8192)
- Features:
  * PortFast on access ports
  * BPDU Guard on access ports
  * Root Guard on distribution uplinks

**Link Aggregation:**
- vPC (Virtual Port Channel) throughout
- LACP (802.3ad) for standardization
- Dual-homed servers and access switches

### 5.2 Layer 3 Design

**Routing Protocol: OSPF**
- Protocol: OSPFv2 for IPv4, OSPFv3 for IPv6
- Area design:
  * Area 0: Core and distribution (backbone)
  * Area 1: Building A
  * Area 2: Building B
  * Area 3: Building C
- Features:
  * Point-to-point network type for fast convergence
  * BFD (Bidirectional Forwarding Detection) for sub-second failure detection
  * Summarization at area boundaries

**OSPF Timers:**
```
interface GigabitEthernet1/0/1
  ip ospf hello-interval 1
  ip ospf dead-interval 3
  ip ospf network point-to-point
  bfd interval 50 min_rx 50 multiplier 3
```

**First Hop Redundancy:**
- Protocol: HSRP (Hot Standby Router Protocol)
- VLAN gateway: Active-active with load sharing
- Configuration:
  * VLAN 100: Core-1 active (priority 110)
  * VLAN 200: Core-2 active (priority 110)
  * Preemption enabled
  * Subsecond failover

---

## 6. Network Services

### 6.1 DHCP Services

**Architecture:**
- Centralized DHCP servers (Windows Server cluster)
- DHCP relay on distribution layer switches
- Scope design: /22 per building (1,022 usable addresses)
- Lease time: 8 hours
- Options:
  * Option 3: Default gateway
  * Option 6: DNS servers
  * Option 150: TFTP server (for IP phones)

### 6.2 DNS Services

**Architecture:**
- Internal DNS: Windows Active Directory DNS
- External DNS: Cloud-hosted (Cloudflare)
- Forwarding: Internal → External for Internet names
- Split-brain DNS for public services

### 6.3 NTP Services

**Architecture:**
- Tier 1: Public NTP (pool.ntp.org)
- Tier 2: Internal NTP servers (2x Linux appliances)
- Tier 3: All network devices sync to internal NTP
- Stratum 2 accuracy
- Timezone: UTC (standardized)

---

## 7. Security Design

### 7.1 Network Segmentation

**Segmentation Strategy:**
```
Security Zones:
├─ Corporate (10.1.0.0/16)
│  ├─ Users: 10.1.100.0/22
│  ├─ Servers: 10.1.200.0/24
│  └─ VoIP: 10.1.250.0/24
│
├─ Guest (10.2.0.0/16)
│  └─ Guest WiFi: 10.2.100.0/22
│
├─ Management (10.3.0.0/16)
│  ├─ Network Management: 10.3.10.0/24
│  └─ Server Management: 10.3.20.0/24
│
└─ DMZ (172.16.0.0/16)
   ├─ Public Web: 172.16.10.0/24
   └─ Mail Servers: 172.16.20.0/24
```

**Traffic Flow Rules:**
- Corporate → Internet: Allowed (with URL filtering)
- Corporate → DMZ: Allowed (specific ports only)
- Guest → Internet: Allowed (rate limited)
- Guest → Corporate: Denied
- DMZ → Corporate: Denied
- Management → All: Allowed (restricted source IPs)

### 7.2 Access Control

**802.1X Network Access Control:**
- Authentication: RADIUS (Cisco ISE)
- EAP method: EAP-TLS (certificate-based)
- Fallback: MAB (MAC Authentication Bypass) for printers, cameras
- Dynamic VLAN assignment based on user/device posture
- Profiling for automatic device categorization

**Configuration Example:**
```
! Access port with 802.1X
interface GigabitEthernet1/0/5
  description 802.1X Enabled Port
  switchport mode access
  authentication port-control auto
  dot1x pae authenticator
  mab
  spanning-tree portfast
```

### 7.3 Encryption

**Management Plane:**
- SSH only (no Telnet)
- HTTPS only (no HTTP)
- SNMPv3 with AES-256 encryption
- TACACS+ with encrypted communication

**Data Plane:**
- MACsec on critical links (core to distribution)
- IPsec VPN for remote access
- TLS 1.3 for application traffic (policy enforced)

---

## 8. High Availability Design

### 8.1 Redundancy Model

**Component Redundancy:**

| Layer | Redundancy | Failover Time | Method |
|-------|------------|---------------|--------|
| Core | N+1 (vPC pair) | < 1 second | vPC + BFD |
| Distribution | N+1 (vPC pair) | < 1 second | vPC + BFD |
| Access | 1+1 (dual uplinks) | < 1 second | vPC |
| Firewall | Active-Active | < 1 second | Clustering |
| Internet | 1+1 (dual ISPs) | < 30 seconds | BGP |
| Power | 2N (dual feeds) | 0 seconds | UPS transfer |

### 8.2 Failure Scenarios

**Scenario 1: Core Switch Failure**
- Detection: BFD (50ms intervals, 3 failures = 150ms detection)
- Convergence: OSPF + vPC (< 500ms)
- Impact: None (traffic shifts to secondary core)
- Recovery: Automatic

**Scenario 2: Fiber Cut**
- Detection: Physical layer (immediate)
- Convergence: LACP + OSPF (< 1 second)
- Impact: None (redundant paths available)
- Recovery: Automatic

**Scenario 3: Building Power Failure**
- Detection: Immediate
- Mitigation: UPS provides 30 minutes runtime
- Generator: Starts within 60 seconds
- Impact: None if generator successful

---

## 9. Migration Strategy

### 9.1 Phased Approach

**Phase 1: Core Infrastructure (Weeks 1-4)**
- Install new core switches in parallel
- Configure vPC and routing
- Test failover scenarios
- No user impact

**Phase 2: Distribution Layer (Weeks 5-8)**
- Install distribution switches
- Connect to core (parallel running)
- Migrate one building at a time
- Maintenance window: Saturday 2-6 AM

**Phase 3: Access Layer (Weeks 9-16)**
- Deploy access switches building by building
- Cut over users floor by floor
- Validate 802.1X functionality
- Daytime deployment (users can work on WiFi)

**Phase 4: Decommission Old (Weeks 17-20)**
- Remove old equipment
- Reclaim rack space
- Update documentation
- Return leased equipment

### 9.2 Rollback Plan

**Per-Phase Rollback:**
- Keep old equipment in place until phase validation
- Documented rollback procedures for each phase
- 24-hour soak period before next phase
- Rollback decision criteria:
  * Critical incident (P1)
  * > 5% performance degradation
  * Security vulnerability introduced

---

## 10. Monitoring and Management

### 10.1 Network Monitoring

**Tools:**
- SNMP: Centralized monitoring (SolarWinds NPM)
- NetFlow: Traffic analysis and capacity planning
- Syslog: Centralized logging (Splunk)
- Streaming Telemetry: Real-time metrics (Grafana + Prometheus)

**KPIs:**
- Availability: 99.99% target
- Latency: < 5ms (99th percentile)
- Packet loss: < 0.01%
- Interface utilization: < 70% average
- MTTR: < 30 minutes

### 10.2 Network Management

**Cisco DNA Center:**
- Centralized management platform
- Zero-touch provisioning (ZTP)
- Policy-based automation
- Assurance and analytics
- SD-Access fabric management

---

## 11. Disaster Recovery

### 11.1 Backup Strategies

**Configuration Backups:**
- Frequency: Automated daily
- Tool: Oxidized (Git-based)
- Retention: 90 days
- Validation: Weekly restore tests

**Documentation:**
- Stored in Confluence (version controlled)
- Offline copies: Quarterly PDF snapshots
- Physical copies: Stored offsite

### 11.2 Recovery Procedures

**RTO/RPO:**
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 24 hours
- Disaster declaration criteria
- Recovery team contact list

---

## 12. Compliance

### 12.1 Regulatory Requirements

**PCI-DSS:**
- Network segmentation (Requirement 1.2.1)
- Encrypted management (Requirement 2.3)
- Configuration standards (Requirement 2.2)
- Logging and monitoring (Requirement 10)

**HIPAA:**
- Access controls (§164.312(a)(1))
- Transmission security (§164.312(e)(1))
- Audit controls (§164.312(b))

---

## 13. Cost Analysis

### 13.1 Capital Expenditure (CAPEX)

| Category | Item | Quantity | Unit Cost | Total |
|----------|------|----------|-----------|-------|
| Core | Nexus 9508 | 2 | $150,000 | $300,000 |
| Distribution | Nexus 93180 | 4 | $45,000 | $180,000 |
| Access | Catalyst 9300 | 20 | $8,000 | $160,000 |
| Wireless | Catalyst 9800 | 2 | $25,000 | $50,000 |
| Wireless | AP 9120AXI | 150 | $800 | $120,000 |
| Optics | 100G QSFP28 | 32 | $3,000 | $96,000 |
| Optics | 10G SFP+ | 200 | $200 | $40,000 |
| Software | DNA Center | 1 | $100,000 | $100,000 |
| Services | Implementation | 1 | $200,000 | $200,000 |
| **Total CAPEX** | | | | **$1,246,000** |

### 13.2 Operational Expenditure (OPEX)

| Category | Annual Cost |
|----------|-------------|
| SmartNet Support (15% hardware) | $187,000 |
| Software Licenses (DNA) | $50,000 |
| Internet Circuits (2x 10G) | $240,000 |
| Staff Training | $25,000 |
| **Total Annual OPEX** | **$502,000** |

### 13.3 Return on Investment (ROI)

**Cost Savings:**
- Reduced downtime: $300K annually
- Operational efficiency: $150K annually
- Avoided incidents: $100K annually
- Total annual savings: $550K

**ROI Calculation:**
```
Total Investment: $1,246,000 (CAPEX)
Annual Savings: $550,000
Payback Period: 1,246,000 / 550,000 = 2.3 years
3-Year NPV: Positive (@ 8% discount rate)
```

---

## 14. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Extended outage during migration | Medium | High | Phased approach, robust rollback plan |
| Budget overrun | Low | Medium | 15% contingency budget |
| Timeline delay | Medium | Medium | Critical path analysis, buffer time |
| Compatibility issues | Low | High | Lab testing before deployment |
| Staff knowledge gap | Medium | Medium | Training program, vendor support |

---

## 15. Conclusion

This High-Level Design provides a robust, scalable, and secure network infrastructure
that meets current requirements and provides 50% growth headroom. The design follows
industry best practices and aligns with business objectives.

**Next Steps:**
1. Stakeholder approval (2 weeks)
2. Low-Level Design development (4 weeks)
3. Lab validation (2 weeks)
4. Procurement (8 weeks)
5. Implementation (16 weeks)

---

## 16. Appendices

### Appendix A: Reference Documents
- Requirements Analysis Document v1.0
- Current Network Audit Report
- Security Policy Documentation
- Vendor RFP Responses

### Appendix B: Glossary
- BFD: Bidirectional Forwarding Detection
- CAPEX: Capital Expenditure
- vPC: Virtual Port Channel
[etc...]

### Appendix C: Acronyms
- HLD: High-Level Design
- LLD: Low-Level Design
- SLA: Service Level Agreement
[etc...]
```

## Low-Level Design (LLD)

### LLD Document Template

```markdown
# Low-Level Design (LLD)
## Project: Next-Generation Campus Network
## Version: 1.0
## Date: 2024-02-01
## Status: Draft

---

## 1. Introduction

The Low-Level Design provides detailed technical specifications for implementing the
Next-Generation Campus Network as defined in the High-Level Design (HLD v2.0).

This document includes:
- Detailed configuration specifications
- IP addressing schemes
- VLAN assignments
- Routing protocol parameters
- Physical connectivity diagrams
- Rack elevations
- Cable schedules
- Testing procedures

**Target Audience:**
- Network engineers (implementation team)
- Field technicians (installation team)
- Validation engineers (testing team)

---

## 2. Physical Design

### 2.1 Data Center Rack Layout

**Rack A12 - Core Infrastructure**

```
Rack Elevation (42U):
┌─────────────────────────────────────┐
│ U42                                 │ Blank Panel
│ U41                                 │ Blank Panel
│ U40-U37                             │ UPS (4U)
│ U36-U25                             │ Nexus 9508 Core-2 (12U)
│ U24-U13                             │ Nexus 9508 Core-1 (12U)
│ U12                                 │ Cable Management
│ U11-U10                             │ Nexus 93180 Dist-1A (2U)
│ U09-U08                             │ Nexus 93180 Dist-1B (2U)
│ U07                                 │ Cable Management
│ U06-U05                             │ Catalyst 9800 WLC-1 (2U)
│ U04-U03                             │ Catalyst 9800 WLC-2 (2U)
│ U02                                 │ 48-port Patch Panel
│ U01                                 │ Cable Management
└─────────────────────────────────────┘

Power:
- Circuit A: 30A @ 208V (Panel MDP-1, Breaker 12)
- Circuit B: 30A @ 208V (Panel MDP-2, Breaker 12)
- UPS Runtime: 30 minutes @ 80% load

Cooling:
- Cold Aisle: Front of rack faces Row 1
- Airflow: Front-to-back
- Temperature: 68-72°F
```

### 2.2 Physical Connectivity Matrix

**Core-1 to Distribution Connections:**

| Core-1 Port | Optic Type | Cable Type | Length | Dist Switch | Dist Port | Notes |
|-------------|------------|------------|--------|-------------|-----------|-------|
| Eth1/1 | 100G QSFP28 | OM4 Fiber | 15m | Dist-1A | Eth1/49 | vPC peer link |
| Eth1/2 | 100G QSFP28 | OM4 Fiber | 15m | Dist-1A | Eth1/50 | vPC peer link |
| Eth1/3 | 100G QSFP28 | OM4 Fiber | 20m | Dist-1B | Eth1/49 | vPC peer link |
| Eth1/4 | 100G QSFP28 | OM4 Fiber | 20m | Dist-1B | Eth1/50 | vPC peer link |

---

## 3. Logical Design

### 3.1 IP Addressing Plan

**Loopback Addresses:**

| Device | Loopback0 | Purpose |
|--------|-----------|---------|
| NYC-CORE-01 | 10.129.0.1/32 | OSPF Router ID, BGP Router ID |
| NYC-CORE-02 | 10.129.0.2/32 | OSPF Router ID, BGP Router ID |
| NYC-DIST-1A | 10.129.0.11/32 | OSPF Router ID |
| NYC-DIST-1B | 10.129.0.12/32 | OSPF Router ID |

**Point-to-Point Links:**

| Source | Interface | Destination | Interface | Subnet | Notes |
|--------|-----------|-------------|-----------|--------|-------|
| CORE-01 | Eth1/1 | DIST-1A | Eth1/49 | 10.128.0.0/31 | OSPF Area 0 |
| CORE-01 | Eth1/2 | DIST-1B | Eth1/49 | 10.128.0.2/31 | OSPF Area 0 |
| CORE-02 | Eth1/1 | DIST-1A | Eth1/50 | 10.128.0.4/31 | OSPF Area 0 |
| CORE-02 | Eth1/2 | DIST-1B | Eth1/50 | 10.128.0.6/31 | OSPF Area 0 |

**VLAN/SVI Assignments:**

| VLAN | Name | Subnet | HSRP VIP | CORE-01 | CORE-02 | Purpose |
|------|------|--------|----------|---------|---------|---------|
| 10 | MGMT | 10.1.10.0/24 | 10.1.10.1 | 10.1.10.2 (Active) | 10.1.10.3 | Management |
| 100 | USERS-BLDG-A | 10.1.100.0/22 | 10.1.100.1 | 10.1.100.2 (Active) | 10.1.100.3 | Users Building A |
| 200 | VOIP-BLDG-A | 10.1.200.0/24 | 10.1.200.1 | 10.1.200.2 | 10.1.200.3 (Active) | VoIP Building A |
| 300 | SERVERS | 10.1.300.0/24 | 10.1.300.1 | 10.1.300.2 (Active) | 10.1.300.3 | Application Servers |

### 3.2 OSPF Design Details

**OSPF Process Configuration:**
```
Area 0 (Backbone):
- Core switches
- Distribution switches
- Point-to-point links

OSPF Timers:
- Hello interval: 1 second
- Dead interval: 3 seconds
- SPF throttling: 50ms initial, 200ms increment, 5000ms max
- LSA throttling: 50ms initial, 200ms increment, 5000ms max

OSPF Network Types:
- P2P links: point-to-point
- VLANs: broadcast (default)

OSPF Authentication:
- Area 0: MD5 authentication
- Key ID: 1
- Key string: [Stored in password vault]

Reference Bandwidth:
- 100 Gbps (100000 Mbps)
- Ensures accurate cost calculation for 100G links
```

**OSPF Cost Calculation:**

| Interface Type | Bandwidth | Cost | Notes |
|----------------|-----------|------|-------|
| 100 GbE | 100 Gbps | 1 | Core links |
| 40 GbE | 40 Gbps | 2 | Distribution uplinks |
| 10 GbE | 10 Gbps | 10 | Access uplinks |
| 1 GbE | 1 Gbps | 100 | Server connections |

---

## 4. Detailed Device Configurations

### 4.1 Core Switch Configuration (NYC-CORE-01)

```
!============================================================================
! Device: NYC-CORE-01
! Model: Cisco Nexus 9508
! Role: Core Switch (Primary)
! Location: NYC Data Center, Rack A12, U13-U24
! Serial Number: FOC2345ABCD
!============================================================================

version 10.2(3)
hostname NYC-CORE-01

feature vpc
feature ospf
feature hsrp
feature lacp
feature lldp
feature bfd

!=== VPC Domain Configuration ===
vpc domain 1
  role priority 10
  peer-keepalive destination 10.1.10.102 source 10.1.10.101 vrf management
  peer-gateway
  layer3 peer-router
  auto-recovery
  delay restore 150
  ip arp synchronize

!=== VLANs ===
vlan 10
  name MGMT
vlan 100
  name USERS-BLDG-A
vlan 200
  name VOIP-BLDG-A
vlan 300
  name SERVERS

!=== vPC Peer-Link ===
interface port-channel1
  description vPC Peer-Link to NYC-CORE-02
  switchport mode trunk
  switchport trunk allowed vlan 1-4094
  spanning-tree port type network
  vpc peer-link

interface Ethernet1/1-2
  description vPC Peer-Link Member
  switchport mode trunk
  switchport trunk allowed vlan 1-4094
  channel-group 1 mode active
  no shutdown

!=== Loopback ===
interface loopback0
  description OSPF/BGP Router ID
  ip address 10.129.0.1/32
  ip ospf network point-to-point
  ip router ospf 1 area 0.0.0.0

!=== SVIs ===
interface Vlan10
  description MGMT Network
  no shutdown
  ip address 10.1.10.2/24
  no ip redirects
  ip ospf network broadcast
  ip router ospf 1 area 0.0.0.0
  hsrp version 2
  hsrp 10
    preempt
    priority 110
    ip 10.1.10.1

interface Vlan100
  description USERS-BLDG-A
  no shutdown
  ip address 10.1.100.2/22
  no ip redirects
  ip ospf network broadcast
  ip router ospf 1 area 0.0.0.0
  hsrp version 2
  hsrp 100
    preempt
    priority 110
    ip 10.1.100.1

!=== Uplinks to Distribution ===
interface Ethernet1/3
  description P2P to NYC-DIST-1A Eth1/49
  no switchport
  mtu 9216
  ip address 10.128.0.0/31
  ip ospf network point-to-point
  ip router ospf 1 area 0.0.0.0
  ip ospf bfd
  no shutdown

!=== OSPF Configuration ===
router ospf 1
  router-id 10.129.0.1
  log-adjacency-changes
  auto-cost reference-bandwidth 100000 Gbps
  bfd

!=== Logging ===
logging server 10.1.10.30 6 facility local6
logging source-interface loopback0

!=== SNMP ===
snmp-server location NYC Data Center Rack A12 U13-U24
snmp-server contact Network Operations noc@company.com

!=== NTP ===
ntp server 10.1.10.5 prefer use-vrf management
ntp source 10.1.10.101

!=== AAA ===
[See AAA section in configuration standards]

end
```

### 4.2 Distribution Switch Configuration (NYC-DIST-1A)

```
!============================================================================
! Device: NYC-DIST-1A
! Model: Cisco Nexus 93180YC-FX
! Role: Distribution Switch (Building A Primary)
! Location: NYC Data Center, Rack A12, U11-U12
!============================================================================

version 10.2(3)
hostname NYC-DIST-1A

feature vpc
feature ospf
feature lacp

!=== VPC Domain ===
vpc domain 2
  role priority 10
  peer-keepalive destination 10.1.10.112 source 10.1.10.111 vrf management
  peer-gateway
  layer3 peer-router
  auto-recovery

!=== VLANs ===
vlan 10,100,200,300

!=== Uplinks to Core ===
interface Ethernet1/49
  description P2P to NYC-CORE-01 Eth1/3
  no switchport
  mtu 9216
  ip address 10.128.0.1/31
  ip ospf network point-to-point
  ip router ospf 1 area 0.0.0.0
  ip ospf bfd
  no shutdown

interface Ethernet1/50
  description P2P to NYC-CORE-02 Eth1/3
  no switchport
  mtu 9216
  ip address 10.128.0.5/31
  ip ospf network point-to-point
  ip router ospf 1 area 0.0.0.0
  ip ospf bfd
  no shutdown

!=== Downlinks to Access (vPC) ===
interface port-channel10
  description vPC to NYC-ACCESS-01
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200
  vpc 10

interface Ethernet1/1-2
  description vPC Member to NYC-ACCESS-01
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200
  channel-group 10 mode active
  no shutdown

!=== OSPF ===
router ospf 1
  router-id 10.129.0.11
  log-adjacency-changes
  auto-cost reference-bandwidth 100000 Gbps

end
```

### 4.3 Access Switch Configuration (NYC-ACCESS-01)

```
!============================================================================
! Device: NYC-ACCESS-01
! Model: Cisco Catalyst 9300-48P
! Role: Access Switch (Building A, Floor 1)
! Location: Building A IDF, Rack 1
!============================================================================

version 17.6
service timestamps debug datetime msec
service timestamps log datetime msec
hostname NYC-ACCESS-01

!=== VLANs ===
vlan 10
 name MGMT
vlan 100
 name USERS-BLDG-A
vlan 200
 name VOIP-BLDG-A

!=== Uplinks (vPC to Distribution) ===
interface TenGigabitEthernet1/1/1
  description Uplink to NYC-DIST-1A Po10
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200
  channel-group 1 mode active

interface TenGigabitEthernet1/1/2
  description Uplink to NYC-DIST-1B Po10
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200
  channel-group 1 mode active

interface Port-channel1
  description vPC Uplinks to Distribution
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200

!=== Access Ports (Template) ===
interface range GigabitEthernet1/0/1-48
  description User Access Port
  switchport mode access
  switchport access vlan 100
  switchport voice vlan 200
  spanning-tree portfast
  spanning-tree bpduguard enable
  authentication port-control auto
  dot1x pae authenticator
  mab

!=== Management ===
interface Vlan10
  ip address 10.1.10.51 255.255.255.0
  no shutdown

ip default-gateway 10.1.10.1

end
```

---

## 5. QoS Design

### 5.1 Traffic Classification

**QoS Policy:**

| Traffic Type | DSCP | Queue | Bandwidth % | Priority |
|--------------|------|-------|-------------|----------|
| Voice (RTP) | EF (46) | Priority | 20% | Strict |
| Video | AF41 (34) | Queue 4 | 30% | CBWFQ |
| Business Critical | AF31 (26) | Queue 3 | 25% | CBWFQ |
| Best Effort | Default (0) | Queue 0 | 25% | CBWFQ |

### 5.2 QoS Configuration Template

```
! Classification
class-map match-any VOICE
  match dscp ef

class-map match-any VIDEO
  match dscp af41

class-map match-any BUSINESS-CRITICAL
  match dscp af31

! Policy
policy-map WAN-QOS-POLICY
  class VOICE
    priority percent 20
  class VIDEO
    bandwidth percent 30
  class BUSINESS-CRITICAL
    bandwidth percent 25
  class class-default
    bandwidth percent 25
    random-detect

! Apply to interface
interface GigabitEthernet0/0/0
  service-policy output WAN-QOS-POLICY
```

---

## 6. Security Implementation

### 6.1 Access Control Lists (ACLs)

**Management ACL:**
```
ip access-list extended MGMT-ACCESS
  remark Allow SSH from management network
  permit tcp 10.1.10.0 0.0.0.255 any eq 22
  remark Allow SNMP from monitoring servers
  permit udp host 10.1.10.30 any eq snmp
  permit udp host 10.1.10.31 any eq snmp
  remark Deny all other management traffic
  deny ip any any log
```

### 6.2 802.1X Configuration

**ISE Integration:**
```
! Global 802.1X configuration
aaa new-model
aaa authentication dot1x default group ISE-GROUP
aaa authorization network default group ISE-GROUP

! Radius configuration
radius server ISE-1
  address ipv4 10.1.10.20 auth-port 1812 acct-port 1813
  key 7 <encrypted>

! Interface configuration
interface GigabitEthernet1/0/5
  authentication port-control auto
  authentication periodic
  authentication timer reauthenticate 3600
  mab
  dot1x pae authenticator
  dot1x timeout tx-period 5
```

---

## 7. Testing and Validation

### 7.1 Pre-Implementation Testing

**Lab Testing Checklist:**
- [ ] Basic connectivity (ping tests)
- [ ] OSPF neighbor establishment
- [ ] OSPF route propagation
- [ ] vPC peer-link formation
- [ ] vPC member port operation
- [ ] HSRP failover (< 1 second)
- [ ] OSPF convergence (< 1 second with BFD)
- [ ] QoS marking preservation
- [ ] 802.1X authentication
- [ ] Dynamic VLAN assignment
- [ ] Configuration backup/restore

### 7.2 Production Validation Tests

**Post-Implementation Validation:**

```
Test 1: End-to-End Connectivity
└─ Ping from user VLAN to server VLAN
   Expected: < 5ms latency, 0% loss

Test 2: Redundancy Validation
└─ Shutdown primary uplink
   Expected: < 1 second failover, no packet loss

Test 3: OSPF Convergence
└─ Shutdown OSPF neighbor
   Expected: < 500ms reconvergence with BFD

Test 4: QoS Validation
└─ Generate traffic with different DSCP markings
   Expected: Voice gets priority, bandwidth allocation per policy

Test 5: 802.1X Authentication
└─ Connect test device with valid certificate
   Expected: Authentication successful, correct VLAN assignment

Test 6: Performance Baseline
└─ Measure baseline metrics
   Expected: Latency, throughput, CPU utilization documented
```

---

## 8. Implementation Schedule

### 8.1 Detailed Timeline

**Week 1-2: Core Installation**
- Day 1-2: Physical installation (rack, cable, power)
- Day 3-4: Base configuration
- Day 5-7: OSPF, vPC configuration
- Day 8-10: Integration testing

**Week 3-4: Distribution Installation**
- Day 11-13: Physical installation
- Day 14-16: Base configuration, uplink to core
- Day 17-19: vPC configuration
- Day 20-21: Integration testing

**Week 5-8: Access Layer Deployment**
- Week 5: Building A, Floors 1-2
- Week 6: Building A, Floors 3-4
- Week 7: Building B, Floors 1-2
- Week 8: Building B, Floors 3-4

### 8.2 Maintenance Windows

**Scheduled Maintenance:**
- Frequency: Every Saturday
- Time: 02:00 - 06:00 EST
- Duration: 4 hours maximum
- Approval: Required from Change Advisory Board (CAB)

---

## 9. Rollback Procedures

### 9.1 Emergency Rollback

**Core Layer Rollback:**
```
Step 1: Notify stakeholders (NOC, management)
Step 2: Capture current state (show tech-support)
Step 3: Reload to previous configuration
        reload in 10
        configure replace flash:rollback-config force
Step 4: Verify operation
Step 5: Document incident
```

### 9.2 Configuration Snapshots

**Pre-Change Snapshot:**
```bash
#!/bin/bash
# Capture configuration snapshot before change

DEVICE=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/${DEVICE}"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Capture running config
ssh admin@${DEVICE} "show running-config" > ${BACKUP_DIR}/running-${TIMESTAMP}.cfg

# Capture version
ssh admin@${DEVICE} "show version" > ${BACKUP_DIR}/version-${TIMESTAMP}.txt

# Capture interface status
ssh admin@${DEVICE} "show ip interface brief" > ${BACKUP_DIR}/interfaces-${TIMESTAMP}.txt

# Capture routing table
ssh admin@${DEVICE} "show ip route" > ${BACKUP_DIR}/routes-${TIMESTAMP}.txt

# Commit to Git
cd ${BACKUP_DIR}
git add .
git commit -m "Pre-change snapshot for ${DEVICE} at ${TIMESTAMP}"
git push
```

---

## 10. Acceptance Criteria

### 10.1 Technical Acceptance

- [ ] All devices online and accessible
- [ ] All interfaces in expected state (up/up)
- [ ] OSPF neighbors established (full state)
- [ ] vPC peer-link operational
- [ ] HSRP active/standby correct
- [ ] No configuration errors or warnings
- [ ] All VLANs present and active
- [ ] End-to-end connectivity verified
- [ ] Performance meets baseline requirements
- [ ] Security controls operational (802.1X, ACLs)

### 10.2 Operational Acceptance

- [ ] Monitoring configured and operational
- [ ] Alerts configured and tested
- [ ] Configuration backup working
- [ ] Documentation updated
- [ ] Runbooks validated
- [ ] Team training completed
- [ ] Handover to operations complete

---

## 11. Appendices

### Appendix A: Cable Schedule
[Detailed cable schedule with source/destination/type/length]

### Appendix B: IP Address Allocation
[Complete IP address spreadsheet]

### Appendix C: Configuration Templates
[Reusable configuration templates]

### Appendix D: Vendor Documentation
[Links to vendor documentation and whitepapers]
```

## Change Request Documentation

### Network Change Request (NCR) Template

```markdown
# Network Change Request
## NCR-2024-0234

### Change Information

**Change Title:** Add VLAN 400 for New Department
**Change Type:** Standard
**Risk Level:** Low
**Change Owner:** John Smith (Network Engineering)
**Implementation Date:** 2024-02-15 02:00 EST
**Estimated Duration:** 30 minutes
**Backout Duration:** 15 minutes

---

### 1. Change Description

**Summary:**
Add VLAN 400 to core and distribution switches to support new Marketing
department (50 users). VLAN will be added to existing trunk links and
SVI created on core switches for L3 routing.

**Business Justification:**
New Marketing department starting Feb 15, 2024. Department requires
segregated network for confidentiality. No additional hardware required.

---

### 2. Impact Assessment

**Impact Level:** Low

**Affected Systems:**
- NYC-CORE-01 (add VLAN, SVI, OSPF advertisement)
- NYC-CORE-02 (add VLAN, SVI, OSPF advertisement)
- NYC-DIST-1A (add VLAN to trunk)
- NYC-DIST-1B (add VLAN to trunk)
- NYC-ACCESS-05 (add VLAN, configure access ports)

**User Impact:**
- No impact to existing users
- Marketing users cannot connect until change complete

**Service Impact:**
- No service interruption expected
- Existing VLANs unaffected

---

### 3. Implementation Plan

**Pre-Change Checklist:**
- [ ] Configuration backed up (Oxidized automatic backup verified)
- [ ] Change approved by CAB
- [ ] Maintenance window notification sent (24 hours advance)
- [ ] Implementation team briefed
- [ ] Lab testing completed
- [ ] Rollback plan reviewed

**Implementation Steps:**

**Step 1: Create VLAN (NYC-CORE-01)**
```
configure terminal
vlan 400
  name MARKETING
exit
```
**Verification:** show vlan id 400
**Expected result:** VLAN 400 present, active

**Step 2: Create SVI (NYC-CORE-01)**
```
interface Vlan400
  description Marketing Department
  ip address 10.1.400.2 255.255.255.0
  no ip redirects
  ip ospf network broadcast
  ip router ospf 1 area 0.0.0.0
  hsrp version 2
  hsrp 400
    preempt
    priority 110
    ip 10.1.400.1
  no shutdown
```
**Verification:** show ip interface brief vlan 400
**Expected result:** Interface up/up, IP address correct

**Step 3: Verify OSPF Advertisement (NYC-CORE-01)**
```
show ip ospf database
show ip route ospf
```
**Expected result:** 10.1.400.0/24 in OSPF database

**Step 4-6: Repeat Steps 1-3 on NYC-CORE-02**
(with HSRP priority 100 instead of 110)

**Step 7: Add VLAN to Distribution Trunks**
```
! On NYC-DIST-1A and NYC-DIST-1B
configure terminal
interface port-channel1
  switchport trunk allowed vlan add 400
```
**Verification:** show interfaces trunk
**Expected result:** VLAN 400 in allowed list

**Step 8: Configure Access Ports (NYC-ACCESS-05)**
```
configure terminal
interface range GigabitEthernet1/0/25-48
  switchport access vlan 400
  description Marketing Department Users
```
**Verification:** show vlan id 400
**Expected result:** Interfaces assigned to VLAN 400

**Step 9: End-to-End Testing**
```
! From Marketing workstation (connect to Gi1/0/25)
Test 1: DHCP assignment (should get 10.1.400.x)
Test 2: Ping default gateway (10.1.400.1)
Test 3: Ping DNS server (10.1.10.7)
Test 4: Ping Internet (8.8.8.8)
Test 5: Browse Internet
```

---

### 4. Backout Plan

**Rollback Steps:**

If issues occur, execute rollback in reverse order:

**Step 1: Remove Access Port Configuration**
```
configure terminal
interface range GigabitEthernet1/0/25-48
  switchport access vlan 1
  no description
```

**Step 2: Remove VLAN from Trunks**
```
! On distribution switches
interface port-channel1
  switchport trunk allowed vlan remove 400
```

**Step 3: Remove SVI and VLAN from Core Switches**
```
! On both core switches
configure terminal
no interface Vlan400
no vlan 400
```

**Rollback Verification:**
- [ ] VLAN 400 removed from all devices
- [ ] Existing VLANs unaffected
- [ ] No OSPF errors
- [ ] Configuration backed up after rollback

---

### 5. Testing and Validation

**Test Plan:**

| Test | Procedure | Success Criteria |
|------|-----------|------------------|
| VLAN Creation | show vlan id 400 | VLAN present and active |
| SVI Status | show ip interface brief vlan 400 | Interface up/up |
| HSRP | show standby brief | CORE-01 active, CORE-02 standby |
| OSPF | show ip route 10.1.400.0 | Route present via OSPF |
| Connectivity | Ping from user to gateway | 0% loss, <5ms latency |
| DHCP | Connect test device | Receives correct IP |
| DNS | nslookup google.com | Resolves correctly |
| Internet | curl https://www.google.com | Success |

---

### 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Configuration error | Low | Medium | Lab tested, peer review |
| HSRP failover | Very Low | Low | VLAN addition doesn't affect HSRP |
| OSPF issues | Very Low | Low | Simple route addition |
| Trunk saturation | Very Low | Low | Ample bandwidth available |

**Overall Risk:** Low

---

### 7. Communication Plan

**Stakeholders:**
- Marketing Department Manager (Mary Johnson)
- Help Desk (alerts disabled during maintenance)
- NOC (on standby for issues)

**Notifications:**
- T-24 hours: Email notification to stakeholders
- T-1 hour: Reminder email
- T-0: Change begin notification
- T+30min: Change complete notification (success/failure)

---

### 8. Approval

**Change Advisory Board (CAB):**
- Network Architecture: Approved (Bob Smith, 2024-02-10)
- Security: Approved (Alice Johnson, 2024-02-10)
- Infrastructure: Approved (Mike Williams, 2024-02-10)
- Change Manager: Approved (Jane Doe, 2024-02-11)

**Emergency Contact:**
- Primary: John Smith (Network Engineer) - (555) 123-4567
- Secondary: Sarah Connor (Network Engineer) - (555) 123-4568
- Escalation: Bob Johnson (Network Manager) - (555) 123-4569

---

### 9. Post-Implementation Review

**Completion Checklist:**
- [ ] All implementation steps completed successfully
- [ ] All tests passed
- [ ] Configuration backed up
- [ ] Documentation updated (network diagram, IP spreadsheet)
- [ ] Stakeholders notified of completion
- [ ] Change record updated in ITSM
- [ ] Lessons learned documented

**Actual Results:**
[To be filled post-implementation]

**Issues Encountered:**
[To be filled post-implementation]

**Lessons Learned:**
[To be filled post-implementation]
```

## Conclusion

Comprehensive network design documentation ensures successful project delivery, smooth operations, and knowledge preservation. The documentation hierarchy from requirements analysis through HLD, LLD, and change requests provides complete project lifecycle coverage.

**Best Practices Summary:**
1. Start with clear business requirements
2. Develop HLD for stakeholder alignment
3. Create detailed LLD for implementation
4. Use structured change request process
5. Maintain documentation through project lifecycle
6. Update as-built documentation post-implementation
7. Regular documentation reviews and audits
8. Version control all documentation

**Key Documents:**
- Requirements Analysis Document (business/technical requirements)
- High-Level Design (architecture, technology selection)
- Low-Level Design (detailed configurations, testing)
- Change Requests (controlled implementation process)
- As-Built Documentation (actual deployed state)

**Tools and Resources:**
- Confluence/SharePoint (documentation platforms)
- Visio/Lucidchart (diagramming)
- Git (version control)
- ITSM (change management workflow)
- NetBox (source of truth for IP/DCIM)

**References:**
- "Top-Down Network Design" (Priscilla Oppenheimer, Cisco Press)
- Cisco Enterprise Design Guides: https://www.cisco.com/c/en/us/solutions/design-zone.html
- ITIL Service Design: https://www.axelos.com/certifications/itil-service-management
- TOGAF: https://www.opengroup.org/togaf
