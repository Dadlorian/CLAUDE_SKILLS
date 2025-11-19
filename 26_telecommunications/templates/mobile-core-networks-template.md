# Mobile Core Networks Architecture & Implementation

## Table of Contents
1. [EPC Architecture](#epc-architecture)
2. [5G Core Architecture](#5g-core-architecture)
3. [Control and User Plane Separation (CUPS)](#cups)
4. [Network Slicing](#network-slicing)
5. [Policy and Charging Control](#policy-charging)
6. [Session and Mobility Management](#session-mobility)
7. [Roaming and Interconnection](#roaming)
8. [Core Network Dimensioning](#dimensioning)
9. [High Availability & Disaster Recovery](#ha-dr)
10. [4G to 5G Migration](#migration)

---

## EPC Architecture {#epc-architecture}

### 1.1 EPC Components Overview

**Mobility Management Entity (MME)**
- Handles UE connection setup and tear-down
- Manages authentication and authorization
- Controls mobility (handovers between cells)
- Manages UE attach/detach procedures
- Handles paging and location updates

**Serving Gateway (SGW)**
- Anchor point for intra-LTE mobility
- Packet router and forwarder
- Manages bearer creation and modification
- Handles inter-PLMN mobility via S3 interface
- Rate limiting and charging correlation

**Packet Data Network Gateway (PGW)**
- Connects to external PDN networks
- Allocates IP addresses to UEs
- Packet filtering and gating
- Acts as anchor for inter-3GPP mobility
- Generates charging data records (CDRs)

**Home Subscriber Server (HSS)**
- Master database for user subscription info
- Stores authentication vectors and keys
- Maintains UE IMSI and MSISDN mappings
- Manages service authorization
- Subscriber policy data repository

**Policy and Charging Rules Function (PCRF)**
- Service-aware policy control
- QoS policy enforcement
- Charging rule application
- Subscriber and service charging policies
- Real-time charging decisions

### 1.2 EPC Protocol Flows

#### Attach Procedure
```
UE         eNodeB        MME         SGW         PGW         HSS
|            |            |           |           |           |
|--Attach Req-->|          |           |           |           |
|            |--S1-Setup-->|           |           |           |
|            |            |--Auth-Req-->           |           |
|            |            |                        |<--S6a-Auth--|
|            |            |<--Auth-Resp--          |--S6a-Auth-->|
|            |            |--Create Session Req------>           |
|            |            |           |--S5-Create Req-->PGW      |
|            |            |           |<--S5-Create Resp--|       |
|            |            |<--Session Created---|               |
|            |<--Attach Accept--|                               |
|<--Attach Complete--|                                          |
```

#### Detach Procedure
```
UE         eNodeB        MME         SGW         PGW         HSS
|            |            |           |           |           |
|--Detach Req-->|          |           |           |           |
|            |--S1-Release-->          |           |           |
|            |            |--Delete Session Req-->|             |
|            |            |           |--S5-Delete-->           |
|            |            |           |<--S5-Delete-Resp-|      |
|            |            |<--Session Deleted----|               |
|            |<--Detach Accept--|                               |
```

#### Handover (Intra-LTE)
```
UE      Source-eNB   Target-eNB    MME        SGW
|           |            |         |          |
|<--MeasReport|           |         |          |
|--HO Prep Req-->|         |         |          |
|            |--HO Req-->  |         |          |
|            |    |--Modify Bearer Req-->      |
|            |    |        |<--Modify Bearer Resp--|
|            |<--HO Ack----|         |          |
|--HO Command-->|          |         |          |
|            |--HO Command-->        |          |
|<--RRCReconfig-->|         |         |          |
|--HO Complete-->|         |          |          |
|            |--HO Complete-->       |          |
|            |    |--Path Switch Req-->         |
|            |    |        |<--Path Switch Resp--|
```

---

## 5G Core Architecture {#5g-core-architecture}

### 2.1 Service-Based Architecture (SBA)

**Network Functions (NFs)**

| Function | Abbreviation | Purpose |
|----------|--------------|---------|
| Access and Mobility Manager | AMF | Handles connection/mobility management |
| User Plane Function | UPF | Forwards user plane traffic (like PGW-U) |
| Session Management Function | SMF | Manages PDU sessions (like PGWC/MME) |
| Authentication Server Function | AUSF | Handles authentication procedures |
| Unified Data Management | UDM | Centralized subscription data (like HSS) |
| Policy Control Function | PCF | Policy decisions (like PCRF) |
| Network Repository Function | NRF | Service discovery and registration |
| Network Exposure Function | NEF | Exposes network capabilities to third parties |
| Charging Function | CHF | Online/offline charging |
| Application Function | AF | Controls service aspects |

### 2.2 5G Protocol Flows

#### PDU Session Establishment (NR)
```
UE      gNodeB      AMF      SMF      UPF      UDM      PCF
|         |         |        |        |        |        |
|--Registration Req-->|       |        |        |        |
|         |--N1 Msg-->|       |        |        |        |
|         |         |--Auth Req-->    |        |<-S6m---|
|         |         |        |        |        |--S6m-->|
|         |         |--SM Context Create Req-->          |
|         |         |        |--Session Est Req-->|      |
|         |         |        |        |<--Session Est Response--|
|         |         |        |<--SM Response-|          |
|         |<--N2 SM Info--|   |        |        |        |
|<--RRCSetup/DLInfo--|         |        |        |        |
|--RRCSetupComplete-->|        |        |        |        |
|         |--N1 Msg-->|        |        |        |        |
|         |         |--SM Context Complete Req-->       |
|         |         |        |<--SM Context Complete Resp--|
```

#### Mobility (Handover across gNodeBs)
```
UE      Source-gNB   Target-gNB    AMF      SMF      UPF
|           |            |         |        |        |
|<--MeasReport|           |         |        |        |
|--HO Prep Req-->|        |         |        |        |
|            |--HO Req Prep-->      |        |        |
|            |    |--N2 HO Req Ack--|        |        |
|            |    |<--N2 HO Cmd Ack-|        |        |
|            |<--HO Prep Complete--->        |        |
|--HO Complete-->|        |         |        |        |
|            |--HO Complete-->      |        |        |
|            |    |--Update UPF Info Req-->  |
|            |    |        |<--UPF Updated--|
```

---

## Control and User Plane Separation (CUPS) {#cups}

### 3.1 CUPS Architecture

**Control Plane (CP) Elements**
- MME (4G) / AMF (5G)
- SGW-C (SGW Control Plane)
- PGW-C (PGW Control Plane) / SMF (5G)
- PCRF / PCF
- HSS / UDM

**User Plane (UP) Elements**
- SGW-U (SGW User Plane)
- PGW-U (PGW User Plane) / UPF (5G)

### 3.2 CUPS Benefits

- Independent scaling of control and user plane
- Reduced latency in user plane
- Simplified deployment and virtualization
- Better resource utilization
- Easier capacity planning

### 3.3 S8 CUPS Protocol Flow

```
UE      eNodeB      MME       SGW-C     SGW-U     PGW-C     PGW-U     HSS
|         |         |         |         |         |         |         |
|--Attach Req-->|   |         |         |         |         |         |
|         |--S1-Setup-->|      |         |         |         |         |
|         |         |--Auth Req-->                          |         |
|         |         |                                       |<--Auth---|
|         |         |--Create Session Req-->|              |          |
|         |         |                    |--S5-C Req-->    |          |
|         |         |                       |<--S5-C Resp--|          |
|         |         |                    |--S8-U Req-->|   |          |
|         |         |                       |<--S8-U Resp--|          |
|         |         |<--Create Session Resp-|              |          |
```

---

## Network Slicing {#network-slicing}

### 4.1 Slice Types and Characteristics

**EMBB (Enhanced Mobile Broadband)**
- High bandwidth requirement
- Lower latency tolerance
- Use cases: Video streaming, AR/VR
- Target: <10ms latency, >100Mbps throughput

**URLLC (Ultra-Reliable Low Latency)**
- Strict latency requirements (<1ms)
- Lower bandwidth needs
- High reliability (99.999%)
- Use cases: Industrial control, autonomous vehicles

**mMTC (Massive Machine-Type Communications)**
- Massive connectivity (millions of devices)
- Lower bandwidth
- Relaxed latency (seconds acceptable)
- Use cases: IoT, smart meters

### 4.2 Slice Configuration Example

```yaml
Slice_Configuration:
  - Slice_ID: eMBB-001
    S_NSSAI:
      SST: 1                    # Slice/Service Type
      SD: 000001               # Slice Differentiator
    AMF_Region: region-1
    Allocated_Resources:
      RAN_Resources: 60%
      CN_Resources: 50%
    QoS_Profile:
      5QI: 7
      Priority: High
      GFBR: 0                  # No guaranteed flow rate
      MFBR: 1000Mbps

  - Slice_ID: URLLC-001
    S_NSSAI:
      SST: 2
      SD: 000002
    AMF_Region: region-1
    Allocated_Resources:
      RAN_Resources: 30%
      CN_Resources: 40%
    QoS_Profile:
      5QI: 82
      Priority: Critical
      GFBR: 10Mbps
      MFBR: 100Mbps
      Delay_Budget: 1ms
      Loss_Rate: 1e-5
```

### 4.3 Slice Isolation

- RAN Resource Isolation: Separate PRBs for each slice
- CN Resource Isolation: Dedicated UPF instances
- Service Isolation: Network policies enforce boundaries
- Measurement Isolation: Per-slice KPIs

---

## Policy and Charging Control {#policy-charging}

### 5.1 Policy Architecture

**Policy Decision Function (PCRF/PCF)**
- Service data flows (SDFs) identification
- QoS policies per SDF
- Charging parameters
- Access control policies

**Policy Enforcement Point (PEP)**
- Apply policies at gateway (PGW-C/SMF)
- Enforce QoS and charging rules
- Report usage to PCRF/PCF

### 5.2 Charging Models

#### Offline Charging
```
Gateway -> Charging Function
  |
  +-> Generate CDR
  +-> Rate and Bill
  +-> Store for later billing
```

#### Online Charging
```
Gateway <-> OCS (Online Charging System)
  |
  +-> Request Units (quota)
  +-> Consume Units
  +-> Renew when depleted
  +-> Debit based on usage
```

### 5.3 QoS Policy Configuration

```yaml
QoS_Policy:
  Service_Flow_1:
    Service_Identifier: VoIP
    Flow_Direction: Uplink
    Protocol: UDP
    Port: 5060
    QoS_Class:
      5QI: 1                    # Voice
      Priority: 20
      GFBR: 12.2kbps           # Guaranteed Flow Bit Rate
      MFBR: 100kbps            # Maximum Flow Bit Rate
      Delay_Budget: 100ms
      Packet_Loss_Rate: 1e-2

  Service_Flow_2:
    Service_Identifier: Video
    Flow_Direction: Downlink
    Protocol: TCP/UDP
    Port: 80,443,1935
    QoS_Class:
      5QI: 7                    # EMBB
      Priority: 70
      GFBR: 0
      MFBR: 10000kbps
      Delay_Budget: 300ms
      Packet_Loss_Rate: 1e-4
```

---

## Session and Mobility Management {#session-mobility}

### 6.1 Session Management (SMF/PGW-C)

**PDU Session States**
```
INACTIVE
    |
    ↓ (PDU Session Creation)
ACTIVE
    |
    ├─→ (Modification)
    |
    ↓ (PDU Session Release)
INACTIVE
```

**Session State Machine**
```
[IDLE]
  ↓ (Session Create Request)
[WAIT_SETUP_ACK]
  ↓ (UPF Established)
[ESTABLISHED]
  ↓ (Modify Session)
[MODIFICATION_IN_PROGRESS]
  ↓ (Confirmed)
[ESTABLISHED]
  ↓ (Release Request)
[WAIT_RELEASE_ACK]
  ↓ (Released)
[IDLE]
```

### 6.2 Mobility Management (AMF/MME)

**Registration States**
- RM-DEREGISTERED: Not registered
- RM-REGISTERED: Normal state
- RM-REGISTERED-SUSPENDED: Due to 5G CN limitation

**Connection Management States**
- CM-IDLE: No active connections
- CM-CONNECTED: Active connection to AMF

**Handover Procedures**

| Type | Description | Delay |
|------|-------------|-------|
| Intra-NR | Within 5G RAN | <10ms |
| NR-to-LTE | 5G to 4G | <100ms |
| LTE-to-NR | 4G to 5G (ENDC) | <100ms |

### 6.3 Mobility Protocol Flow (ENDC Handover)

```
UE      gNodeB(LTE)   gNodeB(NR)    AMF      SMF      UPF
|           |             |         |        |        |
|<--SgNB Add Req           |         |        |        |
|            |--HO Prep Req-->      |        |        |
|            |    |<--HO Ack------->|        |        |
|--RRCReconfig-->|         |         |        |        |
|            |    |--N2 HO Req----->|        |        |
|            |    |        |<--N2 HO Ack-|   |        |
|            |<--HO Ack----|         |        |        |
|--HO Complete-->|         |         |        |        |
|            |    |--HO Complete--->|        |        |
|            |    |        |--Update UPF-->  |
```

---

## Roaming and Interconnection {#roaming}

### 7.1 Roaming Architecture

**Home Public Land Mobile Network (HPLMN)**
- Subscriber's home network
- Controls HSS/UDM
- Hosts PCRF/PCF
- Performs charging

**Visited Public Land Mobile Network (VPLMN)**
- Network where UE is roaming
- Provides RAN and access
- Hosts local AMF/SMF
- Reports usage to HPLMN

### 7.2 Roaming Models

#### National Roaming
```
VPLMN_RAN
    |
    ↓
VPLMN_AMF/SMF
    |
    ↓ (S6a/S6c interface)
HPLMN_HSS/UDM
    |
    ↓ (Gy interface)
HPLMN_PCRF/PCF
    |
    ↓
VPLMN_UPF → PDN/Internet
```

#### International Roaming (LTE)
```
Visited Network               Home Network
├─ eNodeB/gNodeB            ├─ HSS/UDM
├─ MME/AMF ──S6a/S6c────→ (via secure tunnel)
├─ SGW-C
├─ SGW-U
├─ PGW-C ───S7/S9────→ PCRF/PCF
└─ PGW-U                   └─ Charging Function
```

### 7.3 Inter-operator Traffic (IOT)

**Gateway Location Rules (GLR)**
- Subscriber location registration
- Roaming restrictions enforcement
- Charging reference setup

**Intra-PLMN vs Inter-PLMN**
```
Intra-PLMN: Within same operator
├─ Direct signaling paths
├─ Single charging system
└─ Operator-specific policies

Inter-PLMN: Between operators
├─ Roaming agreements required
├─ Intercarrier settlements
└─ Service Level Agreements (SLAs)
```

---

## Core Network Dimensioning {#dimensioning}

### 8.1 Capacity Planning Parameters

**Traffic Models**
```
Peak Hour Traffic = Erlang B Formula Application
Erlang B = (λ^N / N!) / Σ(λ^i / i!) for i=0 to N

Where:
λ = Average call arrival rate (calls/hour)
N = Number of channels
```

**Dimensioning Example**

```yaml
Network_Dimension:
  Target_KPIs:
    Call_Blocking_Probability: 0.01%        # 1 in 10,000
    Handover_Success_Rate: 99.5%
    Service_Availability: 99.95%

  Subscriber_Base:
    Total_Subscribers: 5,000,000
    Active_Peak_Hour: 35%                   # 1,750,000
    Average_Session_Duration: 3.5 minutes
    Average_Data_Rate: 2.5 Mbps per user

  Traffic_Calculation:
    Peak_Hour_Sessions: 5M × 0.35 × 60min / 3.5min = 3.03M
    Required_MME_Capacity: 3.03M / 60 = 50,500 attach/sec
    Required_SGW_Capacity: 3.03M × 2.5Mbps = 7,575 Gbps total

  Equipment_Sizing:
    MME_Nodes: 50,500 / 1,500 per node = 34 nodes (+ 2 spare)
    SGW_Nodes: 7,575Gbps / 100Gbps per node = 76 nodes (+ 4 spare)
    PGW_Nodes: 7,575Gbps / 150Gbps per node = 51 nodes (+ 3 spare)
```

### 8.2 Control Plane Dimensioning

**MME/AMF Sizing**
```
Metric: Attach/Detach rate
Formula: Subscribers × Churn Rate / 24 hours

Example:
5M subscribers × 0.3% daily churn = 15,000 changes/day
= 0.17 changes/sec baseline
+ Peak factor (typically 5-10x)
= 0.85-1.7 changes/sec
+ Handover signaling (10-50x attach rate)
= 17-85 signaling ops/sec total

Per Node Capacity: 1,500 ops/sec
Required Nodes: 85 / 1,500 = 0.057, round to 3 (+ 1 spare)
```

**SGW-C/SMF Sizing**
```
Metric: Session Create/Modify/Delete rate
Formula: Active Sessions × 2 (setup + teardown) / Session Duration

Example:
3M concurrent sessions
3M × 2 / 210 seconds = 28,571 operations/sec
Per Node Capacity: 5,000 ops/sec
Required Nodes: 28,571 / 5,000 = 5.7, round to 8 (+ 1 spare)
```

### 8.3 User Plane Dimensioning

**Throughput Calculation**
```
Subscriber Throughput:
Peak Hour Users: 1,750,000
Average Usage: 2.5 Mbps per user
Peak Concurrent Usage: 30% simultaneity
Total Peak Throughput: 1,750,000 × 2.5Mbps × 0.30 = 1,312.5 Tbps

But practical dimensioning:
- Account for compression ratios
- VoIP overhead reduction
- Video streaming optimizations
- HTTP keep-alives

Practical Aggregate: ~70% of theoretical
Required Capacity: 1,312.5 Tbps × 0.7 = 917 Tbps

With 400Gbps per UPF node: 917 Tbps / 400 Gbps = 2,293 nodes
```

### 8.4 Growth Planning

```
Year 1: 5M subscribers, 2.5Mbps avg (baseline)
Year 2: 6M subscribers, 3.5Mbps avg (+40% capacity)
Year 3: 7.5M subscribers, 5Mbps avg (+43% capacity)
Year 4: 9M subscribers, 7Mbps avg (+26% capacity)
Year 5: 10.5M subscribers, 10Mbps avg (+43% capacity)

5-Year Growth: 110% subscriber growth, 300% capacity growth
Annual Infrastructure Budget: 20-25% increase
```

---

## High Availability & Disaster Recovery {#ha-dr}

### 9.1 HA Architecture

**Active-Active Configuration**
```
      ┌─────────────┐
      │  Load       │
      │ Balancer    │
      └──────┬──────┘
      ┌──────┴──────┐
      ↓             ↓
    ┌────┐       ┌────┐
    │ AMF│       │ AMF│
    │ 1  │       │ 2  │
    └────┘       └────┘
      │             │
      └──────┬──────┘
             ↓
         Database
       (Redundant)
```

**Recovery Time Objectives (RTO)**
```
Component          RTO Target    Method
─────────────────────────────────────────
eNodeB/gNodeB      <1 second      Automatic failover
MME/AMF            <5 seconds     Active-Active or Active-Standby
SGW-C/SMF          <5 seconds     Load-balanced pool
PGW-C/UPF          <5 seconds     Load-balanced pool
HSS/UDM            <10 seconds    Database replication
PCRF/PCF           <10 seconds    Load-balanced + redundancy
```

### 9.2 Database Replication

**Synchronous Replication (Zero Data Loss)**
```
Transaction Flow:
1. Write to Primary DB
2. Wait for Replica ACK
3. Confirm to application
4. Low latency penalty (5-10%)
```

**Asynchronous Replication (High Performance)**
```
Transaction Flow:
1. Write to Primary DB
2. Confirm to application immediately
3. Replicate to Replica asynchronously
4. Risk: Recent transactions on failure
```

**Hybrid (Semi-Synchronous)**
```
Transaction Flow:
1. Write to Primary DB
2. Wait for ACK from at least 1 replica
3. Confirm to application
4. Balance: Performance + reliability
```

### 9.3 Disaster Recovery Plan

```yaml
DR_Strategy:
  RPO_Target: 5 minutes         # Recovery Point Objective
  RTO_Target: 15 minutes        # Recovery Time Objective

  Backup_Sites:
    Primary:
      Location: Data Center A
      Replication_Type: Synchronous
      Distance: Local (same city)

    Disaster_Recovery:
      Location: Data Center B
      Distance: 200+ km
      Replication_Type: Asynchronous
      Update_Frequency: Every 5 min

  Failure_Scenarios:
    - Single_Node_Failure:
        Detection_Time: <10 seconds
        Failover_Time: <30 seconds
        Action: Automatic to hot-spare

    - Site_Failure:
        Detection_Time: <60 seconds
        Failover_Time: <5 minutes
        Action: Manual activation of DR site

    - Data_Corruption:
        Detection_Time: Immediate
        Recovery_Time: 5-15 minutes
        Action: Restore from backup tape
```

### 9.4 Service Redundancy

**N+1 Redundancy**
- N active nodes + 1 spare
- Example: 5 SGW nodes + 1 spare = 6 total
- Load distributed across N nodes
- Spare takes over if any node fails

**N+2 Redundancy**
- Critical for essential functions (HSS, PCRF)
- Handles simultaneous failure of 1 node
- Cost: 33% overhead vs. N+1

---

## Migration Strategies (4G to 5G) {#migration}

### 10.1 Phased Migration Approach

**Phase 1: Foundation (Months 0-6)**
```
Activities:
├─ Deploy 5G RAN in pilot areas
├─ Establish 5G Core (AMF, UPF, SMF)
├─ Integrate HSS/UDM
├─ Setup NSSF for network slicing
├─ Pilot with limited users (1,000-10,000)
│
Resources:
├─ Capital: $50-100M for initial deployment
├─ Personnel: 50-100 engineers
└─ Timeline: 6 months
```

**Phase 2: Expansion (Months 6-18)**
```
Activities:
├─ Expand 5G RAN to 30-40% coverage
├─ Dual connectivity (ENDC) optimization
├─ Legacy 4G optimization for ENDC
├─ Scale 5G Core architecture
├─ Migrate 10-15% of subscribers
│
Resources:
├─ Capital: $100-200M incremental
├─ Personnel: 100-150 engineers
└─ Timeline: 12 months
```

**Phase 3: Dominance (Months 18-36)**
```
Activities:
├─ 5G RAN to 70-80% coverage
├─ Full network slicing operational
├─ SGW offload optimization
├─ Migrate 50-70% of subscribers
├─ Plan 4G sunset
│
Resources:
├─ Capital: $200-300M incremental
├─ Personnel: 150-200 engineers
└─ Timeline: 18 months
```

**Phase 4: Consolidation (Months 36+)**
```
Activities:
├─ 5G RAN near 100% coverage
├─ Retire legacy 4G infrastructure
├─ Migrate remaining subscribers
├─ Decommission old core elements
│
Resources:
├─ Capital: Cost savings period
├─ Personnel: 50-100 engineers (operational)
└─ Timeline: 12+ months
```

### 10.2 Dual Connectivity (ENDC)

**Dual Connectivity Architecture**
```
UE connected to both:
├─ Master Node (MN): LTE eNodeB
│   └─ Provides primary connectivity
│
└─ Secondary Node (SN): gNodeB
    └─ Provides supplemental capacity
```

**ENDC Protocol Flow**
```
UE        eNB(LTE)    gNB(NR)      AMF       SMF        UPF
|           |           |          |         |          |
|--Attach on LTE---->|            |         |          |
|         |--Auth-->|             |         |          |
|         |<--Auth Response        |         |          |
|         |--SgNB Add Request----->|         |          |
|         |        |<--Ack-------->|         |          |
|<--Reconfigure--->|         |     |         |          |
|         |--RAN Sharing Activated         |          |
|         |        |--N2 Message---->      |          |
|         |        |               |--Session Setup-->|
|         |        |               |<--Session ACK-|  |
```

### 10.3 Network Slicing Introduction

**Gradual Slicing Rollout**

```yaml
Timeline:
  Month 0-3:
    - Implement NSSF (Network Slice Selection Function)
    - Define URLLC slice (isolated for launch)
    - eMBB slice shares initial network
    Status: Pilot with enterprise customers

  Month 3-9:
    - Segregate eMBB and mMTC slices
    - Dedicated UPF per slice type
    - RAN resource partitioning
    Status: Roll out to 20-30% of 5G users

  Month 9-18:
    - Advanced network slicing optimizations
    - Per-customer slicing capability
    - Service Level Agreement (SLA) enforced
    Status: 70-90% of 5G users

  Month 18+:
    - Dynamic slice creation
    - AI-based slice optimization
    - 100% support
```

### 10.4 4G Core Optimization During Migration

**SGW Offload (User Plane)**
```
Before SGW Offload:
eNB → SGW → PGW → Internet

After SGW Offload (DECOR):
eNB → PGW (direct path)
└─ SGW bypass for same operator PDN
└─ Reduced latency: 15-20ms → 5-10ms
└─ SGW resources freed for other functions
```

**Control Plane Optimization**
```
Legacy Traffic Engineering:
├─ All attach/detach through centralized MME
├─ Single point of failure
├─ Geographic latency issues

Optimized:
├─ Distributed MME clusters
├─ Local SGW placement
├─ Direct tunneling (S1-U direct)
├─ Reduced signaling load
```

### 10.5 Migration KPIs

```
Tracking Metrics:
├─ 5G RAN Coverage: 0% → 100%
├─ 5G Subscriber Penetration: 0% → 100%
├─ Network Performance:
│  ├─ Average Latency: <150ms
│  ├─ Data Speed: >100 Mbps (30th percentile)
│  └─ Service Availability: >99.95%
├─ Cost per GB: Monitor reduction
├─ Energy per GB: Monitor reduction
├─ Core Network Load:
│  ├─ 4G: 100% → 20%
│  └─ 5G: 0% → 80%
└─ Subscriber Satisfaction: NPS >50
```

---

## Implementation Checklist

- [ ] Document existing 4G core topology
- [ ] Define 5G core design with SBA principles
- [ ] Plan CUPS separation for 4G
- [ ] Define network slicing strategy
- [ ] Establish PCRF/PCF policy framework
- [ ] Design HA/DR architecture
- [ ] Create migration roadmap (phases)
- [ ] Setup testing environment
- [ ] Conduct pilot deployments
- [ ] Establish KPI monitoring
- [ ] Document runbooks for operations
- [ ] Train support teams
- [ ] Execute phased rollout
- [ ] Monitor and optimize performance

---

## References and Standards

- 3GPP TS 23.002: Network Architecture
- 3GPP TS 23.401: EPC Overall Architecture
- 3GPP TS 23.501: 5G System Architecture
- 3GPP TS 23.502: Procedures for 5G System
- 3GPP TS 29.002: Mobile Application Protocol (MAP)
- 3GPP TS 29.244: Interface between CP and UP
- IETF RFC 7296: Internet Key Exchange (IKEv2)
- ITU-T Y.3100: Network 2030
- GSMA Guidelines for Network Slicing
- TM Forum Network Function Virtualization
