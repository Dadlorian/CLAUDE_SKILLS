# SDN Architecture Overview

## Reference Definition
SDN decouples the control plane from the data plane, enabling centralized network management and programmable forwarding.

## Three-Layer SDN Architecture

### 1. Application Layer
**Role**: Business logic and network requirements
- Application programs (orchestrators, analytics, security)
- Network services (load balancing, firewall, routing)
- Business policy enforcement
- Integration with cloud and DevOps platforms

**Examples**:
- Cloud orchestration platforms
- Network monitoring and analytics
- Security applications
- Traffic engineering applications

### 2. Control Layer
**Role**: Network intelligence and decision-making
- SDN Controller (centralized or distributed)
- Network state management
- Flow computation and optimization
- Policy enforcement

**Components**:
- Control plane processors
- Network state databases
- Topology discovery engines
- Flow rule managers

**Examples**:
- OpenDaylight
- ONOS
- Cisco APIC
- VMware NSX Controller

### 3. Data Layer (Infrastructure)
**Role**: Packet forwarding based on control plane decisions
- Physical and virtual switches
- Routers with OpenFlow support
- Network devices
- Hypervisor virtual switches

**Components**:
- OpenFlow switches
- NETCONF-enabled devices
- VNFs (Virtual Network Functions)
- Hypervisor integration (KVM, VMware)

## Communication Planes

### Southbound Interface
**Purpose**: Controller communicates with network devices
- Carries control commands and flow rules
- Transmits device statistics and notifications
- Protocol: OpenFlow, NETCONF, REST, proprietary

### Northbound Interface
**Purpose**: Applications communicate with controller
- Applications request services and policies
- Controller exposes network state
- Protocols: REST, gRPC, YANG/NETCONF

### East-West Interface
**Purpose**: Multi-controller communication
- Synchronization of network state
- Redundancy and high availability
- Load distribution among controllers

## Deployment Models

### Centralized Control
```
Single Controller ↔ All Network Devices
```
**Advantages**: Simplified management, global view
**Disadvantages**: Single point of failure, scalability limits

### Distributed Control
```
Multiple Controllers ↔ Network Devices
(with synchronization)
```
**Advantages**: High availability, scalability
**Disadvantages**: Consistency management, complexity

### Hierarchical Control
```
Regional Controllers ↔ Parent Controller
Parent Controller ↔ Applications
```
**Advantages**: Scalability, reduced latency, fault isolation

## SDN Controller Functions

### 1. Network Intelligence
- Topology discovery
- Path computation
- Traffic engineering
- QoS management

### 2. State Management
- Device state tracking
- Flow state management
- Consistency across distributed controllers
- Failure detection and recovery

### 3. Southbound Management
- Device provisioning
- Flow rule installation
- Configuration management
- Statistics collection

### 4. Northbound Services
- API exposure to applications
- Service abstraction
- Policy enforcement
- Audit and logging

## Control Plane Architecture

### Reactive Mode
**Process**: Event-driven control
1. Packet arrives at switch
2. No matching flow rule
3. Switch sends packet-in to controller
4. Controller computes path and sends flow rules
5. Switch forwards subsequent packets

**Use Cases**: Traffic engineering, anomaly detection
**Drawback**: Higher latency and controller load

### Proactive Mode
**Process**: Rules installed before traffic arrives
1. Controller pre-installs flow rules
2. Switch forwards packets immediately
3. No packet-in messages required

**Use Cases**: Normal forwarding, predictable traffic
**Benefit**: Lower latency, reduced controller load

## Data Plane Characteristics

### Traditional Switching
- Fixed hardware pipelines
- Limited forwarding behavior
- Proprietary control mechanisms

### OpenFlow Switches
- Programmable flow tables
- Standard forwarding model
- Centralized control

### Programmable Data Plane
- P4-based switches
- User-defined packet processing
- Greater flexibility

## Network Virtualization in SDN

### Concept
Multiple logical networks sharing physical infrastructure
- Tenant isolation
- Dynamic resource allocation
- Simplified operations

### Implementation
- Virtual switches (vSwitch)
- Network overlays (VXLAN, Geneve)
- Segment routing

## SDN Integration Points

### With Cloud
- Integration with OpenStack, Kubernetes
- VM network provisioning
- Container networking

### With NFV
- VNF (Virtual Network Function) orchestration
- Service chaining
- Network services deployment

### With Existing Networks
- Legacy device support via NETCONF
- Gradual migration paths
- Interoperability layers

## Performance Considerations

### Latency
- Controller decision time: 5-50ms typically
- Southbound transmission: <10ms
- First packet delay in reactive mode

### Scalability
- Single controller: ~100K devices
- Distributed controllers: Multi-million devices
- Flow rule density: Device dependent

### Throughput
- Packet-in rate: Controller capacity dependent
- Controller processing: Modern CPUs handle thousands/second
- Southbound bandwidth: Usually not limiting factor

## Security Architecture

### Control Plane Security
- TLS encryption for controller communications
- Authentication (certificates, OAuth)
- Authorization (RBAC)

### Data Plane Security
- Flow-based access control
- Microsegmentation
- DDoS mitigation through policy

### API Security
- API authentication and encryption
- Rate limiting and throttling
- Input validation
