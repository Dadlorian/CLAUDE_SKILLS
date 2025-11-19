# 5G Architecture Reference

## 5G Network Architecture Overview

### 5G Core (5GC) Architecture

The 5G Core Network is a completely redesigned architecture compared to 4G LTE, providing:
- Service-based architecture (SBA)
- Cloud-native design
- Network function virtualization
- Microservices-based implementation

### Key Network Functions (NFs)

#### User Plane Functions (UPF)
- **User Plane Function (UPF)** - Data packet processing
  - IP routing
  - QoS handling
  - DNN (Data Network Name) routing
  - Charging data collection
  - Traffic redirection to edge

#### Control Plane Functions

**Access and Mobility Management Function (AMF)**
- UE attachment/registration
- Connection management
- Reachability management
- Mobility management
- Access authentication/authorization

**Session Management Function (SMF)**
- Session establishment/modification/termination
- UE IP allocation
- DNN selection
- UPF selection and control
- QoS policy enforcement

**Authentication Server Function (AUSF)**
- Authentication procedures
- SUPI concealment
- 5G-AKA authentication
- 5G-EAP authentication

**Network Slice Selection Function (NSSF)**
- Network slice selection
- Slice availability management
- Slice-specific AMF assignment
- S-NSSAI assignment

**Network Exposure Function (NEF)**
- Application API exposure
- Network traffic rules
- Analytics exposure
- Policy and charging exposure

#### Support Functions

**Unified Data Management (UDM)**
- Subscriber information management
- Authentication data management
- Master data management
- Subscription data cache

**User Plane Function Repository (UPFR)**
- Manages UPF repository
- UPF discovery and selection

**Policy Control Function (PCF)**
- Policy rules creation
- Policy rules enforcement
- QoS policy definition
- Charging policy definition

### 5G RAN (Radio Access Network)

#### gNodeB (5G Base Station)
- Centralized processing unit (gNB-CU)
- Distributed processing unit (gNB-DU)
- Radio unit (RU)
- Fronthaul/Midhaul/Backhaul connectivity

#### Spectrum Bands
- FR1 (Sub-6 GHz): 450 MHz - 6 GHz
- FR2 (mmWave): 24 GHz - 100 GHz
- CBRS (3.5-3.7 GHz)

#### RAN Technologies
- 3GPP Release 15+ (5G NR)
- Dual connectivity (EN-DC)
- Carrier aggregation
- MIMO (Massive MIMO)

### Connection Flows

#### UE Registration
1. UE sends Registration Request to gNodeB
2. gNodeB forwards to AMF
3. AMF performs authentication via AUSF
4. NSSF selects appropriate network slice
5. SMF creates session with UPF

#### Data Session Setup
1. SMF selects appropriate UPF
2. SMF configures QoS rules
3. UPF establishes data path
4. Traffic routed through UPF

### Service-Based Architecture (SBA)

- **Producer services** - Expose operations
- **Consumer services** - Invoke operations
- **Service discovery** - DNS, repository
- **Message routing** - HTTP/2, gRPC
- **Security** - OAuth 2.0, mTLS

### Network Slicing

**Network Slice Instance (NSI)**
- Composed of multiple network functions
- Supports specific service requirements
- Isolated from other slices
- Can span multiple operators

**Network Slice Subnet Instance (NSSI)**
- Subnet instances for control/user plane
- Shared or dedicated resources

### Deployment Models

#### Non-Standalone (NSA)
- Uses 4G LTE core
- 5G NR serves as secondary
- Transitional deployment model
- Option 3/3a/3x

#### Standalone (SA)
- Pure 5G core network
- Full 5G NR coverage required
- Option 2/5
- Complete 5G experience

### Quality of Service (QoS)

#### QoS Flows
- **GFBR (Guaranteed Flow Bit Rate)** - GBR flows
- **MFBR (Maximum Flow Bit Rate)** - Maximum rate
- **Priority** - 1-9 levels
- **Averaging window** - Time window for GBR

#### QoS Class Indicators (QCIs)
- 1-4: GBR flows (real-time)
- 5-9: Non-GBR flows (best-effort)

### Security in 5G

#### Key Security Procedures
- **5G-AKA** - Authentication protocol
- **SUPI Concealment** - Privacy protection
- **Network Access Control** - Initial access control
- **Authentication with EAP** - Flexible authentication

#### Encryption
- **NEA1/NEA2/NEA3** - Algorithm suites
- **User plane encryption**
- **Control plane encryption**

### Edge Computing Integration

#### MEC (Multi-access Edge Computing)
- UPF co-location at edge
- Low-latency applications
- Service area routing
- Local breakout

### Roaming

#### 5G Roaming Models
- **Home Routed** - Traffic through home network
- **Local Breakout** - Local traffic routing
- **Non-home Routed** - Visited network core

### Performance Indicators

#### Key Metrics
- **Latency** - <1ms RTT possible
- **Throughput** - Up to 20 Gbps
- **Bandwidth** - Up to 800 MHz
- **Reliability** - 99.9999%
- **Energy Efficiency** - Improved 90%

### Virtualization & Cloud-Native

#### Containerization
- Network functions as containers
- Kubernetes orchestration
- Helm charts for deployment
- Service mesh integration

#### Scaling
- Horizontal scaling of NFs
- Auto-scaling policies
- Resource optimization
- Multi-cloud deployment

---

**Reference:** 3GPP TS 23.501, 3GPP TS 38.300
**Last Updated:** 2025-11-19
