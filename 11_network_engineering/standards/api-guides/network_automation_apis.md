# Network Automation APIs Standards

## Executive Summary

This document establishes comprehensive standards for network device APIs, including gNMI (gRPC Network Management Interface), gRPC, and vendor-specific APIs. These standards enable modern network automation, real-time monitoring, and programmatic device management across heterogeneous network environments.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: gNMI RFC, gRPC, Cisco Device APIs, Juniper gNMI, Arista eAPI

---

## 1. gNMI (gRPC Network Management Interface)

### 1.1 gNMI Overview

gNMI is a modern API framework built on gRPC for network device management and telemetry. It provides fast, secure, and efficient communication for both configuration and streaming telemetry.

**Key Characteristics**:
- Built on gRPC protocol (over HTTP/2)
- Binary encoding (Protocol Buffers)
- Bidirectional streaming support
- 100x+ faster than RESTCONF (typical benchmarks)
- Low-latency telemetry (subscription model)
- Vendor-agnostic (OpenConfig compatible)

**gNMI Service Methods**:

| Method | Purpose | Streaming |
|--------|---------|-----------|
| Capabilities | Query device models and supported features | No |
| Get | Retrieve state/configuration data | No |
| Set | Modify device configuration | No |
| Subscribe | Stream telemetry/state changes (push model) | Yes |
| Poll | Client-initiated streaming (pull model) | Yes |

### 1.2 gNMI Protocol Architecture

```
┌─────────────────────────────────────────┐
│  gNMI Client (management station)       │
│  ├─ Ansible/Python/Go script            │
│  ├─ Network monitoring tool             │
│  └─ Orchestration platform              │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ gRPC over HTTP/2 │
        │  (TLS encrypted) │
        └────────┬─────────┘
                 │
┌────────────────▼──────────────────────┐
│  gNMI Service (network device)        │
│  ├─ Cisco IOS XR 6.5+                 │
│  ├─ Juniper Junos 18.1+               │
│  ├─ Arista EOS 4.22+                  │
│  └─ Nokia SR OS 19.5+                 │
│                                       │
│  OpenConfig Data Models               │
│  ├─ VLAN configuration                │
│  ├─ BGP state/config                  │
│  ├─ Interface metrics                 │
│  └─ Route information                 │
└───────────────────────────────────────┘
```

### 1.3 gNMI Message Structure

**Capabilities Request** (discover supported models):
```protobuf
message CapabilityRequest {
}

message CapabilityResponse {
  repeated ModelData supported_models = 1;
  string gNMI_version = 2;
}

// Example response
{
  "supported_models": [
    {
      "name": "openconfig-interfaces",
      "organization": "OpenConfig",
      "version": "2021-01-01"
    },
    {
      "name": "openconfig-bgp",
      "organization": "OpenConfig",
      "version": "2021-01-01"
    },
    {
      "name": "openconfig-platform",
      "organization": "OpenConfig",
      "version": "2021-01-01"
    }
  ],
  "gNMI_version": "0.9.0"
}
```

**Get Request** (retrieve data):
```protobuf
message GetRequest {
  Encoding encoding = 1;  // JSON, PROTO, etc.
  repeated Path path = 2; // YANG paths to retrieve
}

message GetResponse {
  repeated Notification notification = 1;
}

// Example Get request (OpenConfig BGP state)
{
  "path": [
    {
      "elem": [
        {"name": "openconfig-bgp:bgp"},
        {"name": "neighbors"},
        {"name": "neighbor", "key": {"neighbor-address": "10.0.1.2"}},
        {"name": "state"},
        {"name": "session-state"}
      ]
    }
  ]
}
```

**Set Request** (modify configuration):
```protobuf
message SetRequest {
  string prefix = 1;       // Path prefix for all operations
  repeated Update update = 2;
  repeated Path delete = 3;
  repeated Path replace = 4;
}

message Update {
  Path path = 1;
  TypedValue val = 2;
}

// Example Set request (configure BGP router-id)
{
  "update": [
    {
      "path": {
        "elem": [
          {"name": "openconfig-bgp:bgp"},
          {"name": "global"},
          {"name": "config"},
          {"name": "router-id"}
        ]
      },
      "val": {
        "string_val": "10.0.1.1"
      }
    }
  ]
}
```

**Subscribe Request** (streaming telemetry):
```protobuf
message SubscribeRequest {
  repeated Subscription subscribe = 1;
  string prefix = 2;
  qos.Mode qos = 3;
  Mode mode = 4;  // STREAM, ONCE, POLL
  uint64 allow_aggregation = 5;
  uint64 use_aliases = 6;
}

enum Mode {
  STREAM = 0;  // Server streams updates on value change
  ONCE = 1;    // Server streams current values once
  POLL = 2;    // Client polls for updates
}

// Example Subscribe request (interface stats stream)
{
  "subscription": [
    {
      "path": {
        "elem": [
          {"name": "openconfig-interfaces:interfaces"},
          {"name": "interface"},
          {"name": "state"},
          {"name": "statistics"}
        ]
      },
      "mode": "STREAM"
    }
  ],
  "mode": "STREAM",
  "qos": {
    "marking": 20
  }
}
```

### 1.4 gNMI Encoding Options

**JSON Encoding** (human-readable):
```json
{
  "openconfig-interfaces:interfaces": {
    "interface": [
      {
        "name": "GigabitEthernet0/0/1",
        "state": {
          "admin-status": "UP",
          "oper-status": "UP",
          "counters": {
            "in-pkts": 1024500,
            "out-pkts": 987230,
            "in-octets": 2048000000,
            "out-octets": 1974000000,
            "in-errors": 5,
            "out-errors": 0
          }
        }
      }
    ]
  }
}
```

**Protobuf Encoding** (binary, efficient):
```
0a 4c 0a 2f 2f 6f 70 65 6e 63 6f 6e 66 69 67 2d 69 6e 74 65 72 66 61 63 65 73 ...
(Binary protobuf format - not human readable)
```

**ASCII Encoding** (legacy):
```
/openconfig-interfaces:interfaces/interface[name=GigabitEthernet0/0/1]/state
```

---

## 2. gRPC Framework

### 2.1 gRPC Overview

gRPC is a high-performance RPC (Remote Procedure Call) framework built on HTTP/2, enabling efficient bidirectional communication.

**Key Features**:
- HTTP/2 multiplexing (multiple streams over single connection)
- Protocol Buffers for serialization (smaller payloads than JSON)
- Automatic code generation from service definitions
- Bidirectional streaming
- Built-in flow control and back-pressure handling
- Connection pooling and keepalive

### 2.2 gRPC Service Definition (proto3)

```protobuf
// gnmi.proto - gNMI Service Definition

syntax = "proto3";
package gnmi;

service gNMI {
  rpc Capabilities(CapabilityRequest) returns (CapabilityResponse);
  rpc Get(GetRequest) returns (GetResponse);
  rpc Set(SetRequest) returns (SetResponse);
  rpc Subscribe(stream SubscribeRequest) returns (stream SubscribeResponse);
}

message CapabilityRequest {
}

message CapabilityResponse {
  repeated ModelData supported_models = 1;
  string gNMI_version = 2;
}

message ModelData {
  string name = 1;
  string organization = 2;
  string version = 3;
}

message Path {
  string target = 1;
  repeated PathElem elem = 2;
}

message PathElem {
  string name = 1;
  map<string, string> key = 2;
}

message TypedValue {
  oneof value {
    string string_val = 1;
    int64 int_val = 2;
    uint64 uint_val = 3;
    bool bool_val = 4;
    bytes bytes_val = 5;
    float float_val = 6;
    Decimal64 decimal_val = 7;
    ScalarArray leaflist_val = 8;
  }
}

message GetRequest {
  Encoding encoding = 1;
  Path prefix = 2;
  repeated Path path = 3;
}

message GetResponse {
  repeated Notification notification = 1;
}

message SetRequest {
  Path prefix = 1;
  repeated Update update = 2;
  repeated Path delete = 3;
  repeated Path replace = 4;
}

message SetResponse {
  Path prefix = 1;
  repeated Result result = 2;
}

message SubscribeRequest {
  oneof request {
    SubscriptionList subscribe = 1;
    Poll poll = 2;
    Aliases aliases = 3;
  }
}

message Subscription {
  Path path = 1;
  SubscriptionMode mode = 2;
  uint64 sample_interval = 3;
  uint64 heartbeat_interval = 4;
  bool suppress_redundant = 5;
}

message SubscribeResponse {
  oneof response {
    Notification update = 1;
    SyncResponse sync_response = 2;
    Error error = 3;
  }
}
```

### 2.3 gRPC Code Generation

**Generate Python bindings**:
```bash
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  gnmi.proto

# Generates:
# gnmi_pb2.py (message definitions)
# gnmi_pb2_grpc.py (service stubs)
```

**Generate Go bindings**:
```bash
protoc \
  -I. \
  --go_out=. \
  --go-grpc_out=. \
  gnmi.proto

# Generates:
# gnmi_pb2.go (message definitions)
# gnmi_grpc.pb.go (service stubs)
```

---

## 3. Cisco Device APIs

### 3.1 Cisco IOS XR NETCONF/gNMI

**Device Support**:
- IOS XR 6.5+: Full NETCONF/YANG support
- IOS XR 7.0+: gNMI support
- IOS XE 16.12+: Model-Driven Telemetry (MDT)
- ASA 9.12+: RESTCONF support

**Enable NETCONF on IOS XR**:
```
configure
  netconf-yang agent ssh
  commit
exit

! Verify
show netconf-yang agent status
show netconf-yang agent ssh

! SSH port is 830 (default)
```

**Enable gNMI on IOS XR**:
```
configure
  grpc
    port 57400
    address-family ipv4
    ssl
    !
  !
  commit
exit

! Verify
show grpc status
```

**gNMI Capabilities Query**:
```bash
gnmi-cli -addr 10.1.4.1:57400 \
  -username admin \
  -password password \
  -capabilities
```

**Cisco IOS XR Telemetry Paths** (gNMI Subscribe):
```
/Cisco-IOS-XR-interfaces-oper:interfaces/interface[name=GigabitEthernet0/0/0]/state
/Cisco-IOS-XR-bgp-oper:bgp/instances/instance[instance-name=default]/instance-active/vrf-table/vrf[vrf-name=default]/afs/af[af-name=ipv4-unicast]/bgp-route-table/bgp-route[route-key=10.0.0.0/24]
/Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface[interface-name=GigabitEthernet0/0/0]/latest
```

**Configure Model-Driven Telemetry (MDT)** (IOS XR):
```
configure
  telemetry model-driven
    destination-group GNMI-DEST
      address-family ipv4 10.1.4.100 port 57400
      encoding self-describing-gpb
      transport grpc
    !
    sensor-group BGP-STATS
      sensor-path /Cisco-IOS-XR-bgp-oper:bgp
    !
    subscription BGP-STREAM
      sensor-group-id BGP-STATS sample-interval 30000
      destination-id GNMI-DEST
    !
  commit
exit
```

### 3.2 Cisco IOS XE NETCONF/Telemetry

**Enable NETCONF on IOS XE**:
```
configure terminal
  netconf-yang agent ssh
  exit

! Verify
show netconf-yang agent statistics
```

**Cisco IOS XE Telemetry Configuration**:
```
configure terminal
  telemetry ietf subscription 100
    receiver name gnmi-receiver
      address 10.1.4.100
      port 57400
      protocol grpc-tcp
    !
    source address 10.1.4.51
    source vrf Mgmt-intf
    filter xpath /interfaces-state/interface[name='GigabitEthernet0/0/0']/statistics
    stream NETCONF
    encoding encode-kvgpb
  !
end

! Verify subscription
show telemetry ietf subscription all
show telemetry ietf subscription 100 detail
```

### 3.3 Cisco NX-OS gNMI/NETCONF

**Enable gNMI on Nexus**:
```
configure terminal
  feature gnmi
  gnmi
    port 50051
    ssl-key-file bootflash:///keys/gnmi.key
    ssl-cert-file bootflash:///keys/gnmi.crt
    secure-server
  exit
end

! Verify
show gnmi
show feature gnmi
```

---

## 4. Juniper Junos gNMI/NETCONF

### 4.1 Junos Configuration

**Enable gNMI on Junos**:
```
set system services netconf ssh
set system services netconf rfc-compliant
set system services grpc port 50051
set system services grpc ssl
set system services grpc ssl-certificate-id jnpr-cert
set system login user automation class super-user authentication encrypted-password ""

commit
show system services
```

**Juniper YANG Models for gNMI**:
```
/configuration/system/host-name
/configuration/interfaces/interface[name=ge-0/0/0]/unit[name=0]/family/inet/address
/junos:configuration/protocols/bgp/group[name=DFW-PEERS]/neighbor[name=10.0.1.2]
/junos:routing-engines/routing-engine/cpu-temperature
```

**Subscribe to Interface Statistics**:
```
gnmi-cli -addr 10.1.4.1:50051 \
  -username netadmin \
  -password password \
  -subscribe "/junos:operational/junos:interfaces-statistics/junos:interface[name=ge-0/0/0]/junos:transit-statistics/junos:input/junos:packets" \
  -mode STREAM
```

---

## 5. Arista eAPI

### 5.1 Arista eAPI Overview

Arista eAPI is a JSON-RPC API for network device control and monitoring, built on HTTP.

**Key Characteristics**:
- JSON-RPC 2.0 protocol over HTTPS
- Simple HTTP-based transport (no complex serialization)
- Command execution model (similar to CLI)
- Native VXLAN/EVPN support
- CloudVision integration

### 5.2 eAPI Configuration

**Enable eAPI on Arista**:
```
configure terminal
  management api http-commands
    protocol https
    certificate /etc/pki/tls/certs/arista.crt
    key /etc/pki/tls/private/arista.key
    port 8443
    no shutdown
  !
end

! Verify
show management api http-commands
```

### 5.3 eAPI Request/Response

**eAPI Request Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "runCommands",
  "params": {
    "version": 1,
    "cmds": [
      "enable",
      "show version",
      "show interfaces Ethernet1/1 status"
    ],
    "format": "json"
  },
  "id": "arista-eapi-1"
}
```

**eAPI Response Example**:
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "modelName": "DCS-7050TX3-48C6",
      "internalVersion": "4.30.2F",
      "serialNumber": "SN12345",
      "systemMacAddress": "08:00:27:00:01:01",
      "hardwareRevision": "02.00",
      "version": "4.30.2F"
    },
    {},
    {
      "interfaceStatuses": {
        "Ethernet1/1": {
          "vlanInformation": {
            "vlanId": "1"
          },
          "bandwidth": 100000000000,
          "description": "Link to spine",
          "isConnected": true,
          "lineProtocolStatus": "up",
          "interfaceStatus": "up"
        }
      }
    }
  ],
  "id": "arista-eapi-1"
}
```

### 5.4 Arista Configuration via eAPI

**Configure BGP**:
```bash
curl --insecure --request POST \
  --url https://10.1.4.101:8443/command-api \
  --header 'content-type: application/json' \
  --data '{
    "jsonrpc": "2.0",
    "method": "runCommands",
    "params": {
      "version": 1,
      "cmds": [
        "enable",
        "configure terminal",
        "router bgp 65001",
        "router-id 10.0.1.5",
        "neighbor 10.0.1.6 remote-as 65001",
        "end"
      ],
      "format": "json"
    },
    "id": "bgp-config-1"
  }' \
  -u admin:password
```

---

## 6. Network Automation Integration

### 6.1 Python gNMI Client Example

```python
#!/usr/bin/env python3
"""
gNMI network device client for configuration and telemetry
"""

import grpc
import json
from concurrent import futures
import gnmi_pb2
import gnmi_pb2_grpc
from google.protobuf.json_format import MessageToJson
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class gNMIClient:
    def __init__(self, host, port, username, password, insecure=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.insecure = insecure
        self.channel = None
        self.stub = None

    def connect(self):
        """Establish gNMI gRPC connection"""
        if self.insecure:
            self.channel = grpc.aio.secure_channel(
                f"{self.host}:{self.port}",
                grpc.ssl_channel_credentials()
            )
        else:
            self.channel = grpc.aio.secure_channel(
                f"{self.host}:{self.port}",
                grpc.ssl_channel_credentials()
            )

        self.stub = gnmi_pb2_grpc.gNMIStub(self.channel)
        logger.info(f"Connected to {self.host}:{self.port}")

    async def get_capabilities(self):
        """Retrieve device capabilities"""
        try:
            request = gnmi_pb2.CapabilityRequest()
            response = await self.stub.Capabilities(request)
            logger.info(f"Device gNMI version: {response.gNMI_version}")
            logger.info(f"Supported models: {len(response.supported_models)}")

            for model in response.supported_models[:5]:
                logger.info(f"  - {model.name}@{model.version} ({model.organization})")

            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()}: {e.details()}")
            raise

    async def get_data(self, paths):
        """Retrieve configuration and state data"""
        try:
            # Build Get request
            get_request = gnmi_pb2.GetRequest()
            get_request.encoding = gnmi_pb2.Encoding.JSON

            for path_str in paths:
                path = self._string_to_path(path_str)
                get_request.path.append(path)

            # Execute Get RPC
            response = await self.stub.Get(get_request)

            results = []
            for notification in response.notification:
                for update in notification.update:
                    results.append({
                        'path': self._path_to_string(update.path),
                        'value': self._typed_value_to_json(update.val)
                    })

            return results
        except grpc.RpcError as e:
            logger.error(f"Get failed: {e.details()}")
            raise

    async def set_data(self, updates):
        """Modify device configuration"""
        try:
            set_request = gnmi_pb2.SetRequest()

            for path_str, value in updates.items():
                path = self._string_to_path(path_str)
                typed_val = gnmi_pb2.TypedValue()

                # Infer type from value
                if isinstance(value, bool):
                    typed_val.bool_val = value
                elif isinstance(value, int):
                    typed_val.int_val = value
                elif isinstance(value, str):
                    typed_val.string_val = value
                else:
                    typed_val.string_val = json.dumps(value)

                update = gnmi_pb2.Update(path=path, val=typed_val)
                set_request.update.append(update)

            # Execute Set RPC
            response = await self.stub.Set(set_request)
            logger.info(f"Set operation completed: {len(response.result)} results")

            return response
        except grpc.RpcError as e:
            logger.error(f"Set failed: {e.details()}")
            raise

    async def subscribe(self, paths, mode='STREAM', sample_interval=30000):
        """Subscribe to telemetry stream"""
        try:
            # Create subscription
            subscriptions = []
            for path_str in paths:
                path = self._string_to_path(path_str)
                subscription = gnmi_pb2.Subscription(
                    path=path,
                    mode=gnmi_pb2.SubscriptionMode.ON_CHANGE,
                    sample_interval=sample_interval
                )
                subscriptions.append(subscription)

            # Create subscribe request
            sub_list = gnmi_pb2.SubscriptionList(subscription=subscriptions)
            sub_request = gnmi_pb2.SubscribeRequest(subscribe=sub_list)

            # Stream responses
            async with self.stub.Subscribe() as call:
                await call.write(sub_request)

                async for response in call:
                    if response.HasField('update'):
                        updates = response.update
                        for update in updates.update:
                            logger.info(f"Update: {self._path_to_string(update.path)}")
                            logger.info(f"Value: {self._typed_value_to_json(update.val)}")

        except grpc.RpcError as e:
            logger.error(f"Subscribe failed: {e.details()}")
            raise

    def _string_to_path(self, path_str):
        """Convert YANG path string to gNMI Path message"""
        path = gnmi_pb2.Path()

        # Simple parser for paths like /interfaces/interface[name=eth0]/state
        parts = path_str.strip('/').split('/')
        for part in parts:
            elem = gnmi_pb2.PathElem()

            if '[' in part:
                # Handle key-value pairs
                name, keys = part.split('[', 1)
                elem.name = name
                key_pairs = keys.rstrip(']').split(',')

                for key_pair in key_pairs:
                    key_name, key_val = key_pair.split('=')
                    elem.key[key_name] = key_val
            else:
                elem.name = part

            path.elem.append(elem)

        return path

    def _path_to_string(self, path):
        """Convert gNMI Path message to string"""
        parts = []
        for elem in path.elem:
            if elem.key:
                keys = ','.join([f"{k}={v}" for k, v in elem.key.items()])
                parts.append(f"{elem.name}[{keys}]")
            else:
                parts.append(elem.name)

        return '/' + '/'.join(parts)

    def _typed_value_to_json(self, val):
        """Convert TypedValue to JSON-serializable format"""
        if val.HasField('string_val'):
            return val.string_val
        elif val.HasField('int_val'):
            return val.int_val
        elif val.HasField('uint_val'):
            return val.uint_val
        elif val.HasField('bool_val'):
            return val.bool_val
        elif val.HasField('bytes_val'):
            return val.bytes_val.hex()
        elif val.HasField('float_val'):
            return val.float_val
        else:
            return None

    async def close(self):
        """Close gNMI connection"""
        if self.channel:
            await self.channel.close()
            logger.info("Connection closed")

# Usage example
async def main():
    import asyncio

    # Create client
    client = gNMIClient("10.1.4.1", 57400, "admin", "password")
    client.connect()

    # Query capabilities
    capabilities = await client.get_capabilities()

    # Retrieve interface data
    paths = [
        "/openconfig-interfaces:interfaces/interface[name=GigabitEthernet0/0/0]/state"
    ]
    data = await client.get_data(paths)
    print(json.dumps(data, indent=2))

    # Subscribe to telemetry
    await client.subscribe(paths)

    await client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 6.2 Ansible gNMI Module Example

```yaml
---
- hosts: network_devices
  gather_facts: no
  vars:
    ansible_connection: local

  tasks:
    - name: Query gNMI capabilities
      gnmi_get:
        host: "{{ inventory_hostname }}"
        port: 57400
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        paths:
          - /
        mode: STREAM
      register: gnmi_capabilities

    - name: Get BGP state via gNMI
      gnmi_get:
        host: "{{ inventory_hostname }}"
        port: 57400
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        paths:
          - "/openconfig-bgp:bgp/global/state"
      register: bgp_state

    - name: Configure interface via gNMI
      gnmi_set:
        host: "{{ inventory_hostname }}"
        port: 57400
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        update:
          "/openconfig-interfaces:interfaces/interface[name=GigabitEthernet0/0/0]/config/mtu": 9216

    - name: Subscribe to telemetry
      gnmi_subscribe:
        host: "{{ inventory_hostname }}"
        port: 57400
        username: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        subscriptions:
          - path: "/openconfig-interfaces:interfaces/interface/state/statistics"
            mode: STREAM
            sample_interval: 30000
```

---

## 7. API Security Standards

### 7.1 Authentication Methods

**gNMI/gRPC Authentication**:
```protobuf
// Metadata-based authentication
metadata:
  - authorization: Bearer <JWT_TOKEN>
  - username: netadmin
  - password: secure-password
```

**Certificate-Based Authentication** (mutual TLS):
```bash
# Generate client certificate
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr
openssl x509 -req -in client.csr \
  -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt \
  -days 365

# Connect with client certificate
grpc_client.secure_channel(
  "10.1.4.1:57400",
  grpc.ssl_channel_credentials(
    root_certificates=open('ca.crt').read(),
    private_key=open('client.key').read(),
    certificate_chain=open('client.crt').read()
  )
)
```

### 7.2 RBAC and Authorization

**gNMI RBAC Example**:
```
configure terminal
  aaa new-model
  aaa authentication login default local

  aaa authorization commands exec default local

  username netadmin privilege 15 secret <password>
  username gnmi-reader privilege 1 secret <password>

  aaa authorization exec default local
    role-based
    permit role "gnmi-admin" all
    permit role "gnmi-reader" get-only
```

---

## 8. Monitoring and Observability

### 8.1 gNMI Metrics Collection

**Key Telemetry Paths** (OpenConfig):
```
Interface Metrics:
  /openconfig-interfaces:interfaces/interface/state/statistics/in-pkts
  /openconfig-interfaces:interfaces/interface/state/statistics/out-pkts
  /openconfig-interfaces:interfaces/interface/state/statistics/in-octets
  /openconfig-interfaces:interfaces/interface/state/statistics/out-octets
  /openconfig-interfaces:interfaces/interface/state/statistics/in-errors
  /openconfig-interfaces:interfaces/interface/state/statistics/out-errors

BGP Metrics:
  /openconfig-bgp:bgp/global/state/total-paths
  /openconfig-bgp:bgp/global/state/total-prefixes
  /openconfig-bgp:bgp/neighbors/neighbor/state/session-state
  /openconfig-bgp:bgp/neighbors/neighbor/state/messages/sent
  /openconfig-bgp:bgp/neighbors/neighbor/state/messages/received

System Metrics:
  /openconfig-platform:components/component/state/temperature
  /openconfig-platform:components/component/state/cpu-utilization
  /openconfig-platform:components/component/state/memory-available
```

---

## 9. Troubleshooting and Diagnostics

### 9.1 Common gNMI Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Connection refused | gNMI not enabled | Enable with `grpc port 57400` |
| Certificate error | Invalid/untrusted cert | Add to trusted CA store or use insecure mode (lab) |
| Path not found | Incorrect YANG path | Verify with device capabilities query |
| Permission denied | RBAC restrictions | Check user privileges, increase role permissions |
| Timeout | Device busy/network latency | Increase timeout, check device resources |

### 9.2 Debugging Commands

**Cisco IOS XR**:
```
show grpc status
show grpc statistics
debug grpc level all
debug netconf level all
```

**Junos**:
```
show system services grpc
show task grpc
request shell command "netstat -an | grep 50051"
```

**Arista**:
```
show management api http-commands
show management api http-commands history
```

---

## 10. Standards Compliance

**Reference Standards**:
- **gNMI**: openconfig.net/gnmi
- **gRPC**: grpc.io
- **Protocol Buffers**: developers.google.com/protocol-buffers
- **OpenConfig**: github.com/openconfig/public
- **Cisco**: developer.cisco.com/docs/
- **Juniper**: juniper.net/documentation/
- **Arista**: aristanetworks.com/en/support/

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Automation and Architecture Team
