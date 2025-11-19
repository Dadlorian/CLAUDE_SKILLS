# Network Slicing Reference

## Network Slicing Fundamentals

Network Slicing is a fundamental architectural concept that enables multiple logical networks to operate independently within a shared physical infrastructure, each optimized for specific services and requirements.

## Slicing Architecture

### Network Slice Instance (NSI)

A complete logical network comprising:
- Control plane network functions
- User plane network functions
- RAN resources (spectrum, coverage)
- Edge computing resources
- Dedicated or shared infrastructure

### Network Slice Subnet Instance (NSSI)

Instances of network function subnets:
- **Control Plane NSSI** - RAN sharing, AMF/SMF functions
- **User Plane NSSI** - UPF instances, edge processing
- **RAN NSSI** - gNodeB resources, spectrum allocation

## Slice Types

### eMBB (Enhanced Mobile Broadband)
**Use Cases:**
- High-definition video streaming
- Virtual/augmented reality
- Cloud gaming
- Large file downloads

**Characteristics:**
- High bandwidth (100+ Mbps)
- Relaxed latency (50-100ms)
- High capacity
- Best-effort reliability

### URLLC (Ultra-Reliable Low-Latency Communications)
**Use Cases:**
- Industrial automation
- Autonomous vehicles
- Remote surgery
- Real-time control systems

**Characteristics:**
- Ultra-low latency (<1-10ms)
- Ultra-high reliability (99.9999%)
- Low bandwidth requirements
- Predictable performance

### mIoT (Massive IoT)
**Use Cases:**
- Sensor networks
- Smart metering
- Environmental monitoring
- Asset tracking

**Characteristics:**
- Massive connectivity (1M+ devices/km²)
- Low bandwidth (few kbps)
- Long battery life
- Cost-effective

## Network Slice Management

### Slice Lifecycle

#### Creation Phase
1. **Design** - Service requirements definition
2. **Provisioning** - Resource allocation
3. **Composition** - NF assembly
4. **Activation** - Slice enablement

#### Operation Phase
1. **Monitoring** - Performance tracking
2. **Optimization** - Resource tuning
3. **Scaling** - Capacity adjustment
4. **Updates** - Function upgrades

#### Termination Phase
1. **Deactivation** - Stopping slice
2. **Resource Release** - Freeing resources
3. **Deprovisioning** - Resource cleanup

### Resource Isolation

#### Compute Isolation
- **VMs per slice** - Full virtual machines
- **Containers per slice** - Lightweight isolation
- **Functions per slice** - Specific NF assignment

#### Network Isolation
- **Physical separation** - Dedicated hardware
- **Logical separation** - VLAN, VNF partitioning
- **Virtual separation** - Hypervisor-based isolation

#### Storage Isolation
- **Dedicated storage** - Database per slice
- **Shared storage with partitioning** - Multi-tenant database
- **Data encryption** - Cryptographic separation

## Slice Selection (NSSF)

### Selection Criteria

**Service Requirements:**
- QoS requirements (latency, bandwidth, reliability)
- Availability requirements
- Geographical coverage
- Feature requirements

**Subscriber Profile:**
- Subscription agreements
- Pricing tier
- Geographic constraints
- Device capabilities

**Network Conditions:**
- Current slice load
- Available resources
- Network congestion
- Power efficiency targets

### NSSAI (Network Slice Selection Assistance Information)

**S-NSSAI (Single-NSSAI):**
- SST (Slice Service Type): 1-255
- SD (Slice Differentiator): 0-16777215

**Requested NSSAI:**
- Slices requested by UE
- From subscription profile or device

**Allowed NSSAI:**
- Slices AMF can assign
- Subscription-based or network-based

## QoS in Slices

### Slice-Level QoS

**Slice QoS:**
- Guaranteed bandwidth per slice
- Priority for resource allocation
- Isolation from other slices

### Flow-Level QoS

**QoS Flow Levels:**
- GBR (Guaranteed Bit Rate) flows
- DGBR (Delay Critical GBR) flows
- Non-GBR flows

## Slice Examples

### URLLC Slice Example
```
NST: URLLC
SST: 2
SD: 0x010203

Characteristics:
- Latency: <5ms
- Reliability: 99.9999%
- Dedicated UPF instances
- Priority gNodeB resources
- Low bandwidth allocation
```

### eMBB Slice Example
```
NST: eMBB
SST: 1
SD: 0x000001

Characteristics:
- Latency: 50-100ms
- Reliability: 99.9%
- Shared UPF resources
- High bandwidth allocation
- Power efficiency balanced
```

### MIoT Slice Example
```
NST: mIoT
SST: 3
SD: 0x000001

Characteristics:
- Latency: 1-10s
- Reliability: 99%
- Efficiency optimized
- Low data rate
- Extended battery life
```

## Slice Orchestration

### Orchestration Layers

1. **Business Layer** - Service definitions
2. **Orchestration Layer** - Slice management
3. **Network Function Layer** - NF provisioning
4. **Infrastructure Layer** - Physical resources

### Orchestration Tools
- **ONAP** - Open Network Automation Platform
- **OSM** - Open Source Mano
- **Kubernetes** - Container orchestration
- **Terraform** - Infrastructure as Code

## Shared vs Dedicated Resources

### Shared Slice Resources
- **Advantages:** Cost efficiency, flexibility, resource utilization
- **Disadvantages:** Potential interference, isolation challenges
- **Use Cases:** Best-effort services, non-critical applications

### Dedicated Slice Resources
- **Advantages:** Guaranteed performance, isolation, predictability
- **Disadvantages:** Higher cost, lower resource utilization
- **Use Cases:** URLLC, critical services, SLA-required applications

## Monitoring & Management

### Slice Monitoring
- KPI tracking (latency, throughput, reliability)
- Resource utilization monitoring
- Performance anomaly detection
- Capacity planning analytics

### Slice Operations
- Dynamic resource adjustment
- Load balancing across slices
- Slice migration (moving instances)
- Version updates and patches

## Multi-Provider Slicing

### Slice Federation
- Slices spanning multiple operators
- Inter-operator communication
- Shared resource pools
- Roaming with slicing

### Interoperability
- Standard interfaces (3GPP defined)
- Protocol standardization
- Data format consistency
- Service level agreements

---

**Reference:** 3GPP TS 28.801, 3GPP TS 23.501
**Last Updated:** 2025-11-19
