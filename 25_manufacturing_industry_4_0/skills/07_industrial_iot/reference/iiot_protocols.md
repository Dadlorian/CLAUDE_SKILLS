# Industrial IoT Protocols Reference

## Protocol Comparison Matrix

| Feature | MQTT | OPC UA | AMQP | DDS | CoAP |
|---------|------|--------|------|-----|------|
| **Overhead** | Very Low (2B) | High (100B+) | Medium (50B) | Low (20B) | Low (4B) |
| **Latency** | <50ms | <100ms | <100ms | <1ms | <50ms |
| **Real-time** | Good | Excellent | Good | Excellent | Good |
| **Security** | TLS/SSL | Encrypted | TLS/SSL | DTLS | DTLS |
| **Broker** | Centralized | P2P Option | Centralized | P2P | P2P |
| **Scalability** | Millions | Thousands | Millions | Millions | Millions |
| **Complexity** | Low | High | Medium | High | Low |
| **Wireless** | Good | Poor | Poor | Medium | Good |
| **Learning Curve** | Beginner | Expert | Intermediate | Expert | Beginner |

## 1. MQTT (Message Queuing Telemetry Transport)

### Protocol Specifications

**Version History:**
- MQTT 3.1: Original specification
- MQTT 3.1.1: Current stable version (RFC 6755)
- MQTT 5.0: Latest with enhanced features

**Packet Structure:**
```
Fixed Header (2 bytes minimum)
├── Byte 1: Message Type (4 bits) + Flags (4 bits)
├── Byte 2+: Remaining Length (variable)
Variable Header (depends on message type)
├── Protocol name
├── Protocol level
├── Connect flags
└── Keep alive
Payload (varies)
├── Client ID
├── Username
├── Password
└── Topic/Message content
```

### Quality of Service (QoS)

```
QoS 0: At Most Once
Device → Broker → Subscriber
(Fire and forget, no acknowledgment)

QoS 1: At Least Once
Device → Broker → Broker ACKs → Subscriber → Subscriber ACKs
(Guaranteed delivery, may duplicate)

QoS 2: Exactly Once
Device → Broker → (handshake) → Subscriber → (handshake)
(Guaranteed single delivery, more overhead)
```

### MQTT Connection Lifecycle

```
1. CONNECT
   ├── Client ID
   ├── Clean Session flag
   ├── Keep Alive (seconds)
   ├── Username/Password
   └── Will Message (LWT)

2. CONNACK (server response)
   ├── Return Code
   └── Session Present flag

3. SUBSCRIBE/PUBLISH
   └── Topic operations

4. DISCONNECT
   └── Graceful shutdown
```

### Topic Structure Best Practices

```
# Recommended Structure
manufacturing/site/department/equipment/metric

# Examples
manufacturing/plant-01/assembly/robot-01/position
manufacturing/plant-01/assembly/robot-01/temperature
manufacturing/plant-01/assembly/robot-01/cycle-time
manufacturing/plant-01/painting/conveyor-01/speed
manufacturing/plant-02/warehouse/agv-01/battery-level

# Poor Structure (avoid)
data/stuff/value1
test/abc/xyz
```

### Broker Configuration

```
# Mosquitto Example (mosquitto.conf)
listener 1883
protocol mqtt

listener 8883
protocol mqtt
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Logging
log_dest syslog
log_type all
log_timestamp true

# Performance
max_connections -1
max_queued_messages 1000
```

### Persistence and Buffers

```
Client-Side Buffering:
- Local queue on device
- Retry on connection loss
- Exponential backoff
- Maximum retry attempts

Server-Side Persistence:
- Durable message storage
- Subscription recovery
- QoS 1 & 2 message replay
- Clean session handling
```

### Security Implementation

```python
import paho.mqtt.client as mqtt
import ssl

class SecureMQTTClient:
    def __init__(self, broker, port=8883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port

    def setup_tls(self, ca_cert, client_cert, client_key):
        """Configure TLS/SSL encryption"""
        self.client.tls_set(
            ca_certs=ca_cert,
            certfile=client_cert,
            keyfile=client_key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )
        self.client.tls_insecure = False

    def setup_authentication(self, username, password):
        """Configure username/password authentication"""
        self.client.username_pw_set(username, password)

    def setup_callbacks(self):
        """Register callback functions"""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully")
            client.subscribe("manufacturing/#")
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        print(f"Received {msg.topic}: {payload}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection: {rc}")

    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def publish(self, topic, payload, qos=1, retain=False):
        result = self.client.publish(topic, payload, qos=qos, retain=retain)
        return result.rc
```

### Advanced Features

**Last Will and Testament (LWT):**
```python
# Client sets will message before connecting
client.will_set(
    topic="manufacturing/alerts/device01",
    payload="Device01 offline",
    qos=1,
    retain=True
)
# Broker publishes this if client disconnects unexpectedly
```

**Message Retention:**
```python
# Publish with retain flag
client.publish(
    "manufacturing/device01/status",
    payload="running",
    retain=True  # Last value kept by broker
)
# New subscribers receive last retained value
```

## 2. Sparkplug B (MQTT Specification for IIoT)

### Unified Namespace (UNS) Organization

```
spBv1.0/[group_id]/[message_type]/[edge_node_id]/[device_id]

Example:
spBv1.0/manufacturing/NBIRTH/edge-01/device-001
spBv1.0/manufacturing/DDATA/edge-01/device-001
spBv1.0/manufacturing/DCMD/edge-01/device-001
spBv1.0/manufacturing/NDEATH/edge-01
spBv1.0/manufacturing/DDEATH/edge-01/device-001
```

### Message Types

**NBIRTH (Node Birth):**
```json
{
  "timestamp": 1665432000000,
  "metrics": [
    {
      "name": "Device001",
      "type": "String",
      "value": "online"
    },
    {
      "name": "DeviceMetadata",
      "type": "Object",
      "value": {
        "serialNumber": "SN123456",
        "manufacturer": "Siemens",
        "model": "S7-1200"
      }
    }
  ],
  "seq": 0,
  "uuid": "edge-node-01",
  "properties": {
    "IsConnected": true
  }
}
```

**DDATA (Device Data):**
```json
{
  "timestamp": 1665432001000,
  "metrics": [
    {
      "name": "Temperature",
      "timestamp": 1665432001000,
      "datatype": 9,
      "value": 45.5,
      "properties": {
        "engineeringUnits": "°C"
      }
    },
    {
      "name": "Pressure",
      "timestamp": 1665432001000,
      "datatype": 9,
      "value": 2.5,
      "properties": {
        "engineeringUnits": "bar"
      }
    }
  ],
  "seq": 1,
  "uuid": "edge-node-01"
}
```

**DCMD (Device Command):**
```json
{
  "timestamp": 1665432002000,
  "metrics": [
    {
      "name": "StartProduction",
      "value": true,
      "datatype": 11
    },
    {
      "name": "ProductionMode",
      "value": 2,
      "datatype": 5
    }
  ],
  "seq": 2,
  "uuid": "edge-node-01"
}
```

### Data Types in Sparkplug B

```
1:   Int8
2:   Int16
3:   Int32
4:   Int64
5:   UInt8
6:   UInt16
7:   UInt32
8:   UInt64
9:   Float
10:  Double
11:  Boolean
12:  String
13:  DateTime
14:  Text (legacy)
15:  UUID
16:  DataSet
17:  Bytes
18:  File (binary large object)
19:  Template
```

### Device Lifecycle Management

```
Device Status Flow:

1. Edge Node Comes Online
   └── NBIRTH published (contains device list)

2. Device Comes Online
   └── DDATA published with initial values

3. Normal Operation
   └── DDATA published on changes or interval

4. Device Command Received
   └── DCMD processed
   └── DDATA published with command response

5. Device Goes Offline
   └── DDEATH published

6. Edge Node Goes Offline
   └── NDEATH published (or connection timeout)
```

### Advantages Over Standard MQTT

| Aspect | MQTT | Sparkplug B |
|--------|------|-------------|
| Data Typing | None (strings) | Full type support |
| Metadata | Manual implementation | Built-in properties |
| Device Hierarchy | Topic-based | Explicit structure |
| Serialization | JSON/msgpack (manual) | Binary (efficient) |
| Lifecycle | Manual handling | Birth/death certificates |
| Interoperability | Vendor-dependent | Standardized |

## 3. OPC UA (OLE for Process Control Unified Architecture)

### Connection Models

**Client-Server (Request-Response):**
```
Client → Read/Write Request → Server
Server → Response with data → Client
(Synchronous, blocking)
```

**Subscribe-Publish:**
```
Client → Subscribe Request → Server
Server → Monitored Item Notifications → Client
(Asynchronous, event-driven)
```

### Information Model

```
┌─ BaseObject
│  ├─ FolderType
│  │  ├─ ObjectsFolder
│  │  │  ├─ ServerFolder
│  │  │  ├─ TypesFolder
│  │  │  └─ ViewsFolder
│  │  └─ DeviceFolder
│  │
│  └─ DeviceType
│     ├─ Properties (DataVariables)
│     │  ├─ SerialNumber
│     │  ├─ Manufacturer
│     │  └─ Model
│     ├─ Parameters (DataVariables)
│     │  ├─ Temperature
│     │  ├─ Pressure
│     │  └─ Speed
│     └─ Methods
│        ├─ StartProduction()
│        ├─ StopProduction()
│        └─ ResetCounters()
│
└─ EventType
   ├─ SystemEventType
   ├── AlarmConditionType
   │  └─ AlertType
   └─ AuditEventType
```

### Security Model

**Endpoint Security:**
```
SecurityMode: None
SecurityMode: Sign
├─ Signing algorithms
├─ Message encryption
└─ Timestamp validation

SecurityMode: SignAndEncrypt
├─ Full encryption
├─ Message integrity
└─ Key exchange mechanisms
```

**Authentication Methods:**
```
Anonymous
├─ No credentials required
└─ Limited access

User Name/Password
├─ Username and password
├─ Hash-based verification
└─ Policy enforcement

Certificate (X.509)
├─ Public key infrastructure
├─ Mutual authentication
└─ No password exposure
```

### Python Implementation

```python
from opcua import Client, Server
from opcua.common import NumericNodeId
from datetime import datetime

class OPCUAServer:
    def __init__(self, url="opc.tcp://localhost:4840"):
        self.server = Server()
        self.server.set_endpoint(url)

    def setup_namespace(self):
        """Create information model"""
        # Create namespace
        uri = "http://example.com/manufacturing"
        idx = self.server.register_namespace(uri)

        # Create objects
        objects = self.server.get_objects_node()

        # Create equipment folder
        equipment_folder = objects.add_folder(idx, "Equipment")

        # Create device
        device = equipment_folder.add_object(idx, "Motor01")

        # Add properties
        device.add_variable(idx, "Temperature", 45.5)
        device.add_variable(idx, "Speed", 1500)
        device.add_variable(idx, "Power", 125.8)

        # Add method
        method = device.add_method(idx, "Start", self.start_motor)
        method_args = [
            ("mode", NumericNodeId(7, 0)),  # UInt16
            ("delay", NumericNodeId(7, 0))   # UInt16
        ]

        return device

    def start_motor(self, parent, mode, delay):
        """Method implementation"""
        print(f"Starting motor with mode={mode}, delay={delay}")
        return 0

    def start(self):
        with self.server:
            print("OPC UA Server started")
            self.server.start()

class OPCUAClient:
    def __init__(self, url="opc.tcp://localhost:4840"):
        self.client = Client(url)

    def connect(self):
        self.client.connect()
        print("Connected to OPC UA server")

    def read_variable(self, node_id):
        """Read variable value"""
        node = self.client.get_node(node_id)
        return node.get_value()

    def write_variable(self, node_id, value):
        """Write variable value"""
        node = self.client.get_node(node_id)
        node.set_value(value)

    def call_method(self, object_id, method_name, *args):
        """Call method on object"""
        obj = self.client.get_node(object_id)
        method = obj.get_child([method_name])
        return obj.call_method(method, *args)

    def subscribe_to_changes(self, node_id, callback):
        """Subscribe to value changes"""
        node = self.client.get_node(node_id)
        subscription = self.client.create_subscription(100, callback)
        subscription.subscribe_data_change(node)

    def disconnect(self):
        self.client.disconnect()
```

## 4. AMQP (Advanced Message Queuing Protocol)

### Message Model

```
Exchange (Routing logic)
    ↓
Routing Key Matching
    ↓
Queue (Message storage)
    ↓
Consumer (Processing)
```

### Exchange Types

**Direct Exchange:**
```
Producer → Exchange → Routing Key Match → Queue → Consumer
Exact topic matching
```

**Fanout Exchange:**
```
Producer → Exchange → All Queues → Consumers
Broadcast to all subscribers
```

**Topic Exchange:**
```
Producer → Exchange → Wildcard Matching → Queue → Consumer
Pattern-based routing
Examples:
  manufacturing.*.alerts
  manufacturing.plant01.*
```

**Headers Exchange:**
```
Producer → Exchange → Header Matching → Queue → Consumer
Route based on message headers
```

### RabbitMQ Configuration for Manufacturing

```python
import pika
from pika import credentials, connection

class ManufacturingAMQPBroker:
    def __init__(self, host, user, password):
        self.credentials = credentials.PlainCredentials(user, password)
        self.connection_params = pika.ConnectionParameters(
            host=host,
            credentials=self.credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    def setup_topology(self):
        """Create exchanges and queues"""
        # Create exchanges
        self.channel.exchange_declare(
            exchange='manufacturing',
            exchange_type='topic',
            durable=True
        )

        # Create queues
        self.channel.queue_declare(
            queue='alerts',
            durable=True
        )
        self.channel.queue_declare(
            queue='analytics',
            durable=True
        )

        # Create bindings
        self.channel.queue_bind(
            exchange='manufacturing',
            queue='alerts',
            routing_key='*.alerts.*'
        )
        self.channel.queue_bind(
            exchange='manufacturing',
            queue='analytics',
            routing_key='data.*'
        )

    def publish_message(self, routing_key, message, properties=None):
        """Publish message to exchange"""
        if properties is None:
            properties = pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )

        self.channel.basic_publish(
            exchange='manufacturing',
            routing_key=routing_key,
            body=message,
            properties=properties
        )

    def consume_messages(self, queue_name, callback):
        """Consume messages from queue"""
        def wrapper(ch, method, properties, body):
            callback(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper
        )

        print(f"Consuming from {queue_name}")
        self.channel.start_consuming()
```

## 5. DDS (Data Distribution Service)

### Communication Model

```
┌──────────────────┐
│  DataWriter      │
│  (Publisher)     │
└────────┬─────────┘
         │ Publish
    ┌────▼─────────────────────┐
    │  Global Data Space (GDS) │
    │  (Distributed middleware) │
    └────┬─────────────────────┘
         │ Subscribe
┌────────▼──────────┐
│  DataReader       │
│  (Subscriber)     │
└───────────────────┘
```

### QoS Policies

```python
from dds import DDSDataWriter, DDSDataReader, QoSProfile

# Reliability QoS
reliable = QoSProfile(
    reliability="RELIABLE",
    max_blocking_time=1000  # milliseconds
)

# Real-time QoS
realtime = QoSProfile(
    deadline=10,  # milliseconds
    latency_budget=5,
    liveliness="AUTOMATIC"
)

# Throughput QoS
throughput = QoSProfile(
    durability="TRANSIENT",
    batch_size=1000
)
```

## 6. Protocol Selection Guide

### Use MQTT When:
- Bandwidth is constrained
- Many devices on unreliable networks
- Need simple publish-subscribe pattern
- Lower cost of implementation
- Standard format (Sparkplug B) required
- Edge computing deployment

### Use OPC UA When:
- Complex hierarchical data needed
- Strong security requirements
- Integration with industrial systems (SCADA)
- Need semantic interoperability
- Reliable network available
- Legacy system support

### Use AMQP When:
- Complex routing logic needed
- Enterprise messaging required
- High reliability essential
- MES integration needed
- Multi-tenant systems
- Message persistence critical

### Use DDS When:
- Real-time performance critical (< 1ms latency)
- Peer-to-peer communication needed
- High data throughput required
- Deterministic behavior essential
- Motion control or safety systems
- Resource-constrained processing

### Use CoAP When:
- Extremely constrained devices (8-bit microcontrollers)
- UDP network conditions acceptable
- Minimal battery consumption critical
- Simple request-response needed
- REST-like interface desired

## 7. Hybrid Protocol Architectures

### Multi-Protocol Gateway Pattern

```
Legacy Equipment (Modbus)
    ↓
Protocol Gateway
├─ Modbus RTU Input
├─ Data Transformation
├─ MQTT Sparkplug B Output
    ↓
MQTT Broker
├─ Message routing
├─ Persistence
├─ Historical buffering
    ↓
Cloud Platform & Applications
```

### Implementation Example

```python
from pymodbus.client.serial import ModbusSerialClient
import paho.mqtt.client as mqtt
import json

class ModbusToMQTTGateway:
    def __init__(self, modbus_port, mqtt_broker):
        self.modbus_client = ModbusSerialClient(
            method='rtu',
            port=modbus_port,
            baudrate=9600
        )
        self.mqtt_client = mqtt.Client()
        self.mqtt_broker = mqtt_broker

    def start(self):
        self.modbus_client.connect()
        self.mqtt_client.connect(self.mqtt_broker)
        self.mqtt_client.loop_start()

    def poll_and_publish(self):
        """Poll Modbus and publish to MQTT"""
        # Read Modbus registers
        result = self.modbus_client.read_holding_registers(
            address=0,
            count=10,
            unit=1
        )

        if result.isError():
            print(f"Modbus error: {result}")
            return

        # Transform to Sparkplug B format
        timestamp = int(time.time() * 1000)
        payload = {
            "timestamp": timestamp,
            "metrics": [
                {
                    "name": f"Register_{i}",
                    "timestamp": timestamp,
                    "datatype": 7,  # UInt32
                    "value": result.registers[i]
                }
                for i in range(len(result.registers))
            ],
            "seq": 0,
            "uuid": "gateway-01"
        }

        # Publish to MQTT
        topic = "spBv1.0/manufacturing/DDATA/gateway-01/device-01"
        self.mqtt_client.publish(topic, json.dumps(payload))
```

## Conclusion

Each protocol serves specific industrial IoT needs. MQTT with Sparkplug B is rapidly becoming the standard for brownfield manufacturing IoT due to its efficiency, standardization, and interoperability. OPC UA remains essential for complex hierarchical data and deep system integration. AMQP excels in enterprise messaging. DDS serves real-time critical systems. Understanding when to use each protocol is key to designing effective IIoT solutions.
