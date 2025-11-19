# Southbound and Northbound Protocols

## Architecture Overview

```
Northbound Layer
    Applications (Orchestration, Management, Security)
          ↑
          ↓ Northbound Protocol

    SDN Controller
          ↓ Southbound Protocol
          ↑
    Network Devices (Switches, Routers, VNFs)
```

---

## Southbound Protocols

Southbound protocols enable the SDN controller to communicate with and control network devices.

### OpenFlow

#### Overview
- **Standard**: Open Networking Foundation (ONF)
- **Version**: 1.0 - 1.5+ (latest)
- **Layer**: Layer 2-3 control
- **State**: Industry standard

#### Connection
```
Controller (port 6653)  ←SSH/TLS→  Switch (OpenFlow agent)
```

#### Key Messages
**Controller → Switch**:
- `FLOW_MOD`: Install/modify/delete flow rules
- `GROUP_MOD`: Group table operations
- `PORT_MOD`: Port configuration
- `METER_MOD`: Rate limiting
- `PACKET_OUT`: Send packet to switch

**Switch → Controller**:
- `PACKET_IN`: Packet without matching rule
- `FLOW_REMOVED`: Rule expired
- `PORT_STATUS`: Port state change
- `STATS_REPLY`: Statistics
- `ERROR`: Error notification

#### Flow Table Structure
```
Match Fields + Priority → Instructions
├─ Apply-Actions
├─ Goto-Table
├─ Write-Metadata
└─ Meter
```

#### Advantages
- Standardized and vendor-neutral
- Mature ecosystem
- Multiple controller support
- Widely deployed

#### Limitations
- Stateless (controller-computed paths)
- Latency in reactive mode
- Limited flexibility in older versions
- Hardware implementation constraints

#### Use Cases
- Traditional data center SDN
- OpenFlow-only environments
- Network testing and simulation

---

### NETCONF

#### Overview
- **Standard**: IETF RFC 6241
- **Protocol**: XML over SSH
- **Configuration**: Network device configuration
- **Model**: YANG (RFC 6020/7950)

#### Connection
```
Controller (SSH client) ←SSH→ Device (NETCONF server)
Port 830 or 22
```

#### Key Operations

**Get-Config**: Retrieve current configuration
```xml
<rpc message-id="1">
  <get-config>
    <source>
      <running/>
    </source>
    <filter type="subtree">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
    </filter>
  </get-config>
</rpc>
```

**Edit-Config**: Modify configuration
```xml
<rpc message-id="2">
  <edit-config>
    <target>
      <running/>
    </target>
    <default-operation>merge</default-operation>
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>eth0</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
  </edit-config>
</rpc>
```

**Operation**: One-time actions
```xml
<rpc message-id="3">
  <reboot xmlns="urn:ietf:params:netconf:capability:writable-running:1.0"/>
</rpc>
```

#### Data Stores
- **Running**: Active configuration
- **Startup**: Boot configuration
- **Candidate**: Proposed configuration (not committed)

#### Advantages
- Comprehensive device configuration
- Atomic operations with rollback
- YANG model validation
- Industry standard
- Vendor support across all major vendors

#### Limitations
- XML overhead (verbose)
- Slower than binary protocols
- Complexity for simple operations
- Steeper learning curve

#### Use Cases
- Device configuration management
- Comprehensive network automation
- Network-wide change coordination
- Enterprise deployments

---

### RESTCONF

#### Overview
- **Standard**: IETF RFC 8040
- **Protocol**: HTTP/HTTPS (REST)
- **Model**: YANG
- **Advantage**: REST simplicity + NETCONF power

#### Endpoints
```
GET    /restconf/data/{YANG-path}      → Retrieve data
POST   /restconf/data/{YANG-path}      → Create resource
PUT    /restconf/data/{YANG-path}      → Replace resource
PATCH  /restconf/data/{YANG-path}      → Modify resource
DELETE /restconf/data/{YANG-path}      → Delete resource
POST   /restconf/operations/{RPC-name} → Execute RPC
```

#### Example
```
GET /restconf/data/ietf-interfaces:interfaces/interface=eth0

Response:
{
  "ietf-interfaces:interface": {
    "name": "eth0",
    "type": "ethernetCsmacd",
    "enabled": true,
    "mtu": 1500
  }
}
```

#### Advantages
- Familiar REST paradigm
- JSON and XML support
- Simpler than NETCONF for basic operations
- Easier learning curve

#### Limitations
- No atomic multi-step operations
- Less transaction support than NETCONF
- Newer standard (less deployed)

#### Use Cases
- Modern API-first environments
- Cloud-native orchestration
- Simple to moderate configuration needs

---

### gNMI (gRPC Network Management Interface)

#### Overview
- **Standard**: OpenConfig (IETF draft)
- **Protocol**: gRPC (HTTP/2)
- **Serialization**: Protocol Buffers
- **Performance**: High-speed management

#### Operations
```protobuf
service gNMI {
  rpc Capabilities(CapabilityRequest) returns (CapabilityResponse);
  rpc Get(GetRequest) returns (GetResponse);
  rpc Set(SetRequest) returns (SetResponse);
  rpc Subscribe(SubscribeRequest) returns (stream SubscribeResponse);
}
```

#### Subscribe (Telemetry)
```protobuf
SubscribeRequest:
├─ subscription {
│  ├─ path: "/interfaces/interface[name=eth0]/state"
│  ├─ mode: TARGET_DEFINED (streaming)
│  └─ sample_interval: 10000000000  (10 seconds)
└─ mode: STREAM
```

#### Advantages
- Binary protocol (small payload)
- HTTP/2 multiplexing
- Bidirectional streaming
- Modern, designed for telemetry
- High performance

#### Limitations
- Newer (less mature)
- Requires gRPC infrastructure
- Fewer device implementations

#### Use Cases
- High-speed telemetry collection
- Cloud-native environments
- Real-time monitoring
- Modern data center operations

---

### Vendor-Specific Southbound

#### Cisco Proprietary
- **EEM (Embedded Event Manager)**: Script-based automation
- **RESTAPI**: Proprietary REST endpoints
- **SNMP**: Read-only information

#### Arista EOS
- **eAPI**: Proprietary REST API
- **gNMI**: Supported
- **CloudVision**: Proprietary control

#### Juniper
- **Netconf**: Primary protocol
- **gNMI**: Emerging support
- **PyEZ**: Python library

---

## Northbound Protocols

Northbound protocols enable applications to communicate with the SDN controller and request network services.

### REST API

#### Overview
- **Standard**: HTTP/HTTPS
- **Data**: JSON/XML
- **Methods**: GET, POST, PUT, DELETE, PATCH
- **State**: Stateless (each request independent)

#### Endpoint Structure
```
Base URL: https://controller:8080/api/v1

Resources:
/devices          → List of network devices
/devices/{id}     → Specific device
/flows            → Flow management
/intents          → Intent definitions
/topology         → Network topology
/hosts            → Connected hosts
/services         → Available services
```

#### Example: ONOS
```bash
# Get all devices
GET /onos/v1/devices
Authorization: Basic onos:rocks

# Install flow rule
POST /onos/v1/flows/of:0000000000000001
Content-Type: application/json

{
  "priority": 40000,
  "timeout": 0,
  "isPermanent": true,
  "deviceId": "of:0000000000000001",
  "selector": {...},
  "treatment": {...}
}

# Get statistics
GET /onos/v1/flows/stats
```

#### Authentication
- **Basic Auth**: HTTP standard
- **Token/OAuth**: Modern approach
- **API Key**: Service accounts
- **mTLS**: Mutual certificate validation

#### Response Codes
```
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error
503 Service Unavailable
```

#### Advantages
- Universally understood
- Easy to test (curl, browser)
- Widely tooling support
- Low barrier to entry

#### Limitations
- Inefficient for streaming
- Polling required for updates
- JSON/XML overhead
- Stateless (no persistent context)

---

### gRPC

#### Overview
- **Standard**: IETF (gRPC)
- **Protocol**: HTTP/2
- **Serialization**: Protocol Buffers
- **Performance**: 10x faster than REST

#### Service Definition
```protobuf
service NetworkService {
  rpc GetDevices(Empty) returns (DeviceList);
  rpc InstallFlow(FlowRequest) returns (FlowResponse);
  rpc SubscribeToEvents(Empty) returns (stream NetworkEvent);
}
```

#### Client Example (Python)
```python
import grpc
import network_pb2
import network_pb2_grpc

channel = grpc.secure_channel(
  'controller:50051',
  grpc.ssl_channel_credentials()
)
stub = network_pb2_grpc.NetworkServiceStub(channel)

# Unary RPC
response = stub.GetDevices(network_pb2.Empty())

# Server streaming
for event in stub.SubscribeToEvents(network_pb2.Empty()):
    print(event)
```

#### Advantages
- Binary format (efficient)
- Bidirectional streaming
- HTTP/2 multiplexing
- Strong typing
- Excellent performance

#### Limitations
- Learning curve (protobuf)
- Less browser-friendly
- Fewer tooling options than REST

---

### Event/Pub-Sub

#### Overview
- **Pattern**: Publisher/Subscriber
- **Transport**: Kafka, RabbitMQ, MQTT
- **Delivery**: Asynchronous
- **Persistence**: Optional message queue

#### Architecture
```
Controller (Publisher)
    ├─ publishes to topic: "interface-events"
    │
Kafka/RabbitMQ (Message Broker)
    │
    ├─ Application-1 subscribes to "interface-events"
    ├─ Application-2 subscribes to "link-events"
    └─ Application-3 subscribes to "device-events"
```

#### Event Types
- Device state changes
- Link state changes
- Flow creation/deletion
- Packet arrival
- Topology changes
- Statistics updates

#### Message Format (JSON)
```json
{
  "eventType": "interface-down",
  "timestamp": 1640000000,
  "deviceId": "of:0000000000000001",
  "interface": "eth0",
  "reason": "link-loss"
}
```

#### Advantages
- Asynchronous (non-blocking)
- Decoupled (publisher ≠ subscriber)
- Scalable (many consumers)
- Real-time updates

#### Use Cases
- Event-driven architecture
- Distributed applications
- Multiple independent consumers
- Streaming analytics

---

### WebSocket

#### Overview
- **Standard**: RFC 6455
- **Protocol**: Persistent HTTP upgrade
- **Direction**: Bidirectional
- **Latency**: Low (persistent connection)

#### Example: Real-time Dashboard
```javascript
// Client
const ws = new WebSocket('ws://controller:8080/api/events');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  updateDashboard(message);
};
ws.send(JSON.stringify({action: 'subscribe', topic: 'topology'}));
```

#### Advantages
- Real-time updates
- Lower overhead than polling
- Full-duplex communication

#### Use Cases
- Real-time dashboards
- Live traffic monitoring
- Interactive applications

---

## Protocol Comparison

| Aspect | REST | gRPC | NETCONF | RESTCONF | gNMI | Pub/Sub |
|--------|------|------|---------|----------|------|---------|
| **Performance** | Good | Excellent | Fair | Good | Excellent | Good |
| **Learning Curve** | Low | Medium | High | Low-Medium | Medium | Medium |
| **Streaming** | Polling | Native | No | No | Native | Native |
| **Data Format** | JSON/XML | Protobuf | XML | JSON/XML | Protobuf | JSON |
| **Standardization** | HTTP | gRPC | IETF | IETF | OpenConfig | Various |
| **Maturity** | Mature | Emerging | Mature | Growing | Growing | Mature |
| **Adoption** | Very High | Growing | High | Growing | Growing | High |

---

## Selection Guidelines

### Choose REST if:
- Simple requirements
- Need browser compatibility
- Team comfortable with HTTP
- Throughput not critical

### Choose gRPC if:
- High performance needed
- Real-time streaming important
- Microservices architecture
- Internal APIs (not browser-facing)

### Choose NETCONF if:
- Comprehensive device configuration needed
- Atomic transactions required
- Vendor support essential
- Traditional deployments

### Choose RESTCONF if:
- YANG models available
- REST familiar to team
- Moderate complexity
- Modern cloud-native

### Choose gNMI if:
- Telemetry focus
- High-speed management
- Modern architecture
- OpenConfig adoption

### Choose Pub/Sub if:
- Event-driven architecture
- Multiple consumers needed
- Asynchronous processing
- Scalability important

---

## Best Practices

### Implementation
1. **Start Simple**: Begin with REST, add complexity as needed
2. **Authentication First**: Secure all protocols
3. **Error Handling**: Proper error codes and messages
4. **Versioning**: API versions for backward compatibility
5. **Documentation**: Clear, comprehensive API docs

### Performance
1. **Choose Right Protocol**: Match use case to protocol
2. **Optimize Payloads**: Filter/compress data
3. **Caching**: Where appropriate
4. **Connection Pooling**: Reduce overhead

### Security
1. **Encryption**: TLS for all protocols
2. **Authentication**: Multi-factor where possible
3. **Rate Limiting**: Prevent abuse
4. **Audit Logging**: Track all access

### Operations
1. **Monitoring**: API response times
2. **Alerting**: Failed requests
3. **Load Balancing**: Distribute controller load
4. **Redundancy**: Multiple controller instances
