# SDN APIs Reference

## API Architecture Overview

```
SDN Applications
    ↓ (Northbound API)
SDN Controller
    ├─ REST API
    ├─ gRPC API
    └─ Event-driven API
        ↓ (Southbound API)
    Network Devices
```

## Northbound APIs

### REST API (HTTP-based)

#### Characteristics
- **Standard**: HTTP/HTTPS
- **Data Format**: JSON/XML
- **Methods**: GET, POST, PUT, DELETE
- **Stateless**: Each request self-contained
- **Advantages**: Simple, widely supported, browser-friendly

#### Common Controllers
- OpenDaylight
- ONOS
- Cisco APIC
- VMware NSX

#### Example: ONOS Intent API
```
POST /onos/v1/intents
{
  "type": "HostToHostIntent",
  "appId": "org.onlab.app.bar",
  "priority": 100,
  "one": {
    "mac": "00:00:00:00:00:01",
    "vlan": 100
  },
  "two": {
    "mac": "00:00:00:00:00:02",
    "vlan": 100
  }
}
```

#### REST Methods
```
Create: POST /api/resource
        {data}

Read:   GET /api/resource/id

Update: PUT /api/resource/id
        {updated_data}

Delete: DELETE /api/resource/id
```

#### Response Codes
- **2xx**: Success
- **4xx**: Client error (bad request, not found)
- **5xx**: Server error (internal error)

#### Authentication
- **Basic Auth**: Username/password (base64 encoded)
- **Token Auth**: API key in header
- **OAuth 2.0**: Modern authentication

### gRPC API

#### Characteristics
- **Protocol**: HTTP/2 binary
- **Serialization**: Protocol Buffers (protobuf)
- **Performance**: 10x faster than REST
- **Streaming**: Bidirectional real-time updates
- **Type-Safe**: Schema-defined contracts

#### Use Cases
- High-performance requirements
- Real-time telemetry
- Streaming updates
- Machine-to-machine communication

#### Example: telemetry.proto
```protobuf
service Telemetry {
  rpc Subscribe(SubscriptionRequest) returns (stream TelemetryData);
  rpc Get(GetRequest) returns (GetResponse);
}

message TelemetryData {
  uint64 timestamp = 1;
  repeated Sample samples = 2;
}

message Sample {
  string path = 1;
  string value = 2;
}
```

#### Advantages Over REST
- Binary format (smaller payload)
- HTTP/2 multiplexing
- Server push capability
- Better for mobile

### Event-Driven APIs

#### Pub/Sub Model
```
Application 1: Subscribe to "interface-down"
Application 2: Subscribe to "link-congestion"
Application 3: Subscribe to "new-flow"
                    ↓
              Event Bus (Kafka/RabbitMQ)
                    ↓
Controller publishes events
```

#### Event Types
- Device events (up/down, config change)
- Link events (up/down, metric change)
- Flow events (added/removed/expired)
- Packet events (packet-in from switch)

#### Implementation
**Topic Subscription**:
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('network_events')
for event in consumer:
    process_event(event)
```

### WebSocket API

#### Characteristics
- **Connection**: Persistent, two-way
- **Use Case**: Real-time updates
- **Overhead**: Lower than polling

#### Example: Browser Dashboard Update
```javascript
// Client side
const ws = new WebSocket('ws://controller:8080/api/events');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};
```

---

## Southbound APIs

### OpenFlow

#### Message Types
**Controller → Switch**:
- **Flow_Mod**: Add/delete/modify flow rules
- **Group_Mod**: Group table operations
- **Port_Mod**: Port configuration
- **Meter_Mod**: Rate limiting config

**Switch → Controller**:
- **Packet_In**: Packet without matching flow
- **Flow_Removed**: Flow expired
- **Port_Status**: Port state change
- **Stats_Reply**: Statistics response

#### Example Flow Installation
```
Controller (Cisco APIC/VMware NSX)
    → Flow_Mod (add)
    {
      "match": {
        "in_port": 1,
        "eth_dst": "00:00:00:00:00:02"
      },
      "instructions": [
        {
          "type": "apply_actions",
          "actions": [
            {"type": "output", "port": 2}
          ]
        }
      ]
    }
    → Sent to Switch
```

### NETCONF (Network Configuration Protocol)

#### Characteristics
- **Protocol**: XML over SSH
- **Model**: YANG data models
- **Operations**: Get, Get-Config, Edit-Config, Delete-Config
- **Persistence**: Persistent configuration storage
- **Transactions**: Atomic operations with rollback

#### NETCONF Operations
```xml
<rpc>
  <edit-config>
    <target><running/></target>
    <config>
      <interface>
        <name>eth0</name>
        <enabled>true</enabled>
        <mtu>1500</mtu>
      </interface>
    </config>
  </edit-config>
</rpc>
```

#### Use Cases
- Device configuration (not just policies)
- Vendor-specific features
- Complex multi-step configurations

### RESTCONF (REST for NETCONF)

#### Characteristics
- **Protocol**: HTTP/HTTPS
- **Model**: YANG data models
- **Operations**: RESTful (GET, POST, PUT, DELETE)
- **Data Format**: JSON/XML
- **Advantage**: Combines REST simplicity with NETCONF power

#### Example
```
GET /restconf/data/ietf-interfaces:interfaces/interface=eth0

Response:
{
  "interface": {
    "name": "eth0",
    "enabled": true,
    "mtu": 1500,
    "statistics": {
      "in-packets": 1000000,
      "out-packets": 950000
    }
  }
}
```

### YANG Data Models

#### Structure
```
module ietf-interfaces {
  container interfaces {
    list interface {
      key "name";
      leaf name {
        type string;
      }
      leaf enabled {
        type boolean;
      }
      leaf mtu {
        type uint16;
      }
    }
  }
}
```

#### Key Concepts
- **Containers**: Grouping of data
- **Leaves**: Scalar data elements
- **Lists**: Multiple instances (keyed)
- **RPC**: Remote procedure calls
- **Augment**: Extend existing models

#### Standard Models
- IETF (vendor-neutral): ietf-interfaces, ietf-routing
- OpenConfig: Network device configuration
- Vendor-specific: Cisco, Juniper, Arista

### gNMI (gRPC Network Management Interface)

#### Characteristics
- **Protocol**: gRPC (HTTP/2)
- **Serialization**: Protocol Buffers
- **Model**: YANG
- **Streaming**: Real-time telemetry

#### Operations
```protobuf
// Subscribe to telemetry
rpc Subscribe(SubscribeRequest) returns (stream SubscribeResponse);

// Get current state
rpc Get(GetRequest) returns (GetResponse);

// Set configuration
rpc Set(SetRequest) returns (SetResponse);
```

#### Use Cases
- High-speed device management
- Real-time telemetry collection
- Cloud-native orchestration

### gNOI (gRPC Network Operations Interface)

#### Common Operations
- **System**: Reboot, reload, traceroute
- **Certificate**: Install, rotate certificates
- **File**: Copy files to/from device
- **Optical**: Optical interface control

---

## API Comparison

| Feature | REST | gRPC | NETCONF | RESTCONF | gNMI |
|---------|------|------|---------|----------|------|
| **Performance** | Good | Excellent | Fair | Good | Excellent |
| **Simplicity** | High | Medium | Low | High | Medium |
| **Streaming** | Polling | Native | No | No | Native |
| **Data Format** | JSON/XML | Protobuf | XML | JSON/XML | Protobuf |
| **Security** | HTTPS | TLS | SSH | HTTPS | TLS |
| **Standards** | HTTP | IETF | IETF | IETF | IETF |
| **Adoption** | Very High | Growing | High | Growing | Growing |

---

## Authentication & Security

### API Authentication Methods

#### Basic Authentication
```
Authorization: Basic base64(username:password)
```
**Advantages**: Simple
**Disadvantages**: Password in every request (use HTTPS!)

#### Token-Based (OAuth 2.0)
```
1. POST /api/auth/login
   {username, password}
2. Response: {token: "xyz123"}
3. Authorization: Bearer xyz123
```
**Advantages**: Stateless, expiration, revocation

#### Certificate-Based (mTLS)
```
Client Certificate → Server verifies
Server Certificate → Client verifies
Mutual TLS encryption
```
**Advantages**: Strongest security, no password needed

#### API Key
```
X-API-Key: long-random-string
```
**Advantages**: Simple for service accounts
**Disadvantages**: Single-use, not rotatable

### RBAC (Role-Based Access Control)
```
User → Role → Permissions
  admin  → full_access
  operator → read_only
  guest → limited_read
```

### Rate Limiting
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000

If exceeded: HTTP 429 (Too Many Requests)
```

---

## Practical Examples

### Python SDK Example (ONOS)
```python
import requests
import json

# Configuration
controller_ip = "10.0.0.1"
username = "onos"
password = "rocks"
auth = (username, password)

# Get devices
url = f"http://{controller_ip}:8181/onos/v1/devices"
response = requests.get(url, auth=auth)
devices = response.json()['devices']

# Install flow rule
flow = {
    "priority": 40000,
    "timeout": 0,
    "isPermanent": True,
    "deviceId": "of:0000000000000001",
    "treatment": {
        "instructions": [
            {"type": "OUTPUT", "port": "1"}
        ]
    },
    "selector": {
        "criteria": [
            {"type": "IN_PORT", "port": "2"},
            {"type": "ETH_DST", "mac": "00:00:00:00:00:02"}
        ]
    }
}

url = f"http://{controller_ip}:8181/onos/v1/flows/{flow['deviceId']}"
requests.post(url, json=flow, auth=auth)
```

### Ansible Integration
```yaml
---
- name: Configure SDN network
  hosts: sdn_controller
  gather_facts: false
  tasks:
    - name: Create logical network
      community.network.onos_app:
        url: "{{ controller_url }}"
        username: "{{ controller_user }}"
        password: "{{ controller_pass }}"
        app_name: "org.onlab.app.firewall"
        state: present
```

---

## API Discovery & Documentation

### OpenAPI (Swagger)
**Standard**: OpenAPI 3.0
**Auto-generated**: Most modern controllers
**Endpoint**: `/swagger-ui.html` or `/api/docs`

### YANG Browser
**Purpose**: Explore YANG models
**Tools**: Netbox, OpenDaylight YANG UI
**Benefits**: Visual model navigation

---

## Best Practices

### API Design
- Use consistent naming conventions
- Version APIs (/v1/, /v2/)
- Document thoroughly
- Support content negotiation (JSON/XML)

### Error Handling
- Use appropriate HTTP status codes
- Return detailed error messages
- Include error IDs for tracking
- Log all errors server-side

### Performance
- Implement pagination for lists
- Use filtering (reduce payload)
- Cache where appropriate
- Consider gRPC for high-performance

### Security
- Always use HTTPS/TLS
- Implement rate limiting
- Validate all inputs
- Rotate credentials regularly
- Audit API access

### Testing
- Unit tests for API logic
- Integration tests with devices
- Load testing before production
- Test error scenarios
