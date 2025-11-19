# MQTT and Sparkplug B Implementation Guide

## MQTT Fundamentals for Manufacturing

### MQTT Connection Establishment

#### 1. Client Setup and Connection

```python
import paho.mqtt.client as mqtt
import ssl
import json
from datetime import datetime

class ManufacturingMQTTClient:
    def __init__(self, broker_host, broker_port=8883, client_id="device-001"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        self.connected = False

    def setup_security(self, ca_cert, client_cert, client_key):
        """Configure TLS/SSL security"""
        self.client.tls_set(
            ca_certs=ca_cert,
            certfile=client_cert,
            keyfile=client_key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )
        self.client.tls_insecure = False

    def setup_callbacks(self):
        """Register event callbacks"""
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe

    def _on_connect(self, client, userdata, flags, rc):
        """Connection callback"""
        if rc == 0:
            self.connected = True
            print(f"Connected to {self.broker_host}:{self.broker_port}")
            # Subscribe to command topics
            self.client.subscribe("manufacturing/commands/#", qos=1)
        else:
            print(f"Connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Disconnection callback"""
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection: {rc}")

    def _on_message(self, client, userdata, msg):
        """Message received callback"""
        try:
            payload = msg.payload.decode()
            print(f"Received on {msg.topic}: {payload}")
            # Process message
            self.process_command(msg.topic, payload)
        except Exception as e:
            print(f"Error processing message: {e}")

    def _on_publish(self, client, userdata, mid):
        """Message published callback"""
        print(f"Message {mid} published successfully")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Subscription callback"""
        print(f"Subscribed with QoS {granted_qos}")

    def connect(self):
        """Establish connection to broker"""
        try:
            self.client.connect(
                self.broker_host,
                self.broker_port,
                keepalive=60
            )
            self.client.loop_start()
        except Exception as e:
            print(f"Connection error: {e}")

    def publish_message(self, topic, payload, qos=1, retain=False):
        """Publish message to topic"""
        if not self.connected:
            print("Not connected to broker")
            return False

        try:
            result = self.client.publish(
                topic,
                payload,
                qos=qos,
                retain=retain
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Publish error: {e}")
            return False

    def process_command(self, topic, payload):
        """Process received commands"""
        # Implement command handling
        pass

    def disconnect(self):
        """Graceful disconnect"""
        self.client.loop_stop()
        self.client.disconnect()
```

### MQTT QoS Implementation

#### QoS 0: Fire and Forget

```python
def publish_with_qos0(client, topic, message):
    """
    At Most Once - No acknowledgment
    Best for: Non-critical telemetry
    """
    client.publish(
        topic,
        message,
        qos=0,
        retain=False
    )
    # Message may be lost if connection drops
```

#### QoS 1: At Least Once

```python
def publish_with_qos1(client, topic, message):
    """
    At Least Once - Broker acknowledges receipt
    Best for: Important measurements
    May result in duplicates if client loses ACK
    """
    client.publish(
        topic,
        message,
        qos=1,
        retain=False
    )
    # Broker will store message in queue if client disconnects
    # Client must acknowledge broker's ACK
```

#### QoS 2: Exactly Once

```python
def publish_with_qos2(client, topic, message):
    """
    Exactly Once - Guaranteed single delivery
    Best for: Critical alerts, billing data
    Highest overhead due to 4-way handshake
    """
    client.publish(
        topic,
        message,
        qos=2,
        retain=False
    )
    # 4-way handshake ensures exactly-once delivery
    # Higher latency and network overhead
```

### Last Will and Testament (LWT)

```python
class ReliableMQTTClient:
    def __init__(self, client_id):
        self.client = mqtt.Client(client_id=client_id)

    def setup_will_message(self, equipment_id, device_type):
        """Setup LWT for equipment offline detection"""
        will_topic = f"manufacturing/status/{equipment_id}/online"
        will_payload = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "online": False,
            "equipment_id": equipment_id,
            "device_type": device_type,
            "reason": "ungraceful_disconnect"
        })

        # Set will message (sent if client disconnects unexpectedly)
        self.client.will_set(
            topic=will_topic,
            payload=will_payload,
            qos=1,
            retain=True
        )

    def on_connect(self, client, userdata, flags, rc):
        """Handle connection and publish birth certificate"""
        if rc == 0:
            # Publish birth certificate (online state)
            birth_message = {
                "timestamp": datetime.now().isoformat(),
                "online": True,
                "equipment_id": self.equipment_id,
                "version": "1.0"
            }
            client.publish(
                f"manufacturing/status/{self.equipment_id}/online",
                json.dumps(birth_message),
                qos=1,
                retain=True
            )
```

## Sparkplug B Implementation

### Unified Namespace Structure

#### Topic Organization

```
spBv1.0/[group_id]/[message_type]/[edge_node_id]/[device_id]

Manufacturing Example:
spBv1.0/plant-01/NBIRTH/edge-01                           # Edge node birth
spBv1.0/plant-01/DDATA/edge-01/robot-01                   # Robot data
spBv1.0/plant-01/DDATA/edge-01/conveyor-01                # Conveyor data
spBv1.0/plant-01/DCMD/edge-01/robot-01                    # Robot command
spBv1.0/plant-01/DDEATH/edge-01/robot-01                  # Robot offline
spBv1.0/plant-01/NDEATH/edge-01                           # Edge node offline
```

### NBIRTH Message Implementation

```python
import struct
import json
from datetime import datetime

class SparkplugBMessage:
    """Sparkplug B message builder"""

    # Data types
    DATATYPE_INT8 = 1
    DATATYPE_INT16 = 2
    DATATYPE_INT32 = 3
    DATATYPE_INT64 = 4
    DATATYPE_UINT8 = 5
    DATATYPE_UINT16 = 6
    DATATYPE_UINT32 = 7
    DATATYPE_UINT64 = 8
    DATATYPE_FLOAT = 9
    DATATYPE_DOUBLE = 10
    DATATYPE_BOOLEAN = 11
    DATATYPE_STRING = 12
    DATATYPE_DATETIME = 13
    DATATYPE_BYTES = 17

    def __init__(self, group_id, edge_node_id):
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.seq = 0

    def create_nbirth_message(self, device_list):
        """Create node birth certificate message"""
        metrics = []

        # Add device list
        for device_id in device_list:
            metrics.append({
                "name": device_id,
                "datatype": self.DATATYPE_STRING,
                "value": f"online"
            })

        # Add edge node properties
        metrics.append({
            "name": "Node Control/Rebirth",
            "datatype": self.DATATYPE_BOOLEAN,
            "value": False
        })

        return {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": metrics,
            "seq": 0,
            "uuid": self.edge_node_id,
            "properties": {
                "IsConnected": True,
                "IsStaleness": False
            }
        }

    def create_ddata_message(self, device_id, metrics_data):
        """Create device data message"""
        metrics = []

        for metric_name, value, datatype in metrics_data:
            metrics.append({
                "name": metric_name,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "datatype": datatype,
                "value": value,
                "properties": {
                    "engineeringUnits": self._get_units(metric_name)
                }
            })

        self.seq = (self.seq + 1) % 256

        return {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": metrics,
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

    def create_dcmd_message(self, command_name, parameters):
        """Create device command message"""
        self.seq = (self.seq + 1) % 256

        return {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": [
                {
                    "name": command_name,
                    "datatype": self.DATATYPE_BOOLEAN,
                    "value": parameters.get("value", True)
                }
            ],
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

    def _get_units(self, metric_name):
        """Get engineering units for metric"""
        units_map = {
            "temperature": "°C",
            "pressure": "bar",
            "speed": "rpm",
            "power": "kW",
            "current": "A",
            "voltage": "V"
        }
        return units_map.get(metric_name, "")
```

### Complete Sparkplug B Implementation

```python
class SparkplugBClient:
    def __init__(self, broker_host, group_id, edge_node_id):
        self.broker_host = broker_host
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.devices = {}
        self.seq = 0

        self.client = mqtt.Client(
            client_id=f"{group_id}-{edge_node_id}",
            protocol=mqtt.MQTTv311,
            clean_session=True
        )

        self.setup_callbacks()

    def setup_callbacks(self):
        """Setup MQTT callbacks"""
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        """On connection, send NBIRTH"""
        if rc == 0:
            print("Connected, sending NBIRTH")
            self.send_nbirth()
            # Subscribe to command topics
            self.client.subscribe(
                f"spBv1.0/{self.group_id}/DCMD/{self.edge_node_id}/#",
                qos=1
            )

    def _on_message(self, client, userdata, msg):
        """Handle incoming DCMD messages"""
        topic = msg.topic
        payload = json.loads(msg.payload)

        # Parse topic
        parts = topic.split('/')
        if len(parts) >= 5:
            device_id = parts[4]
            self.handle_device_command(device_id, payload)

    def send_nbirth(self):
        """Send node birth certificate"""
        nbirth_message = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": [
                {
                    "name": "Node Control/Rebirth",
                    "datatype": 11,  # Boolean
                    "value": False
                }
            ] + [
                {
                    "name": device_id,
                    "datatype": 12,  # String
                    "value": "online"
                }
                for device_id in self.devices.keys()
            ],
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

        self.seq = (self.seq + 1) % 256

        topic = f"spBv1.0/{self.group_id}/NBIRTH/{self.edge_node_id}"
        self.client.publish(topic, json.dumps(nbirth_message), qos=1)

    def send_device_data(self, device_id, metrics):
        """Send device data"""
        ddata_message = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": metrics,
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

        self.seq = (self.seq + 1) % 256

        topic = f"spBv1.0/{self.group_id}/DDATA/{self.edge_node_id}/{device_id}"
        self.client.publish(topic, json.dumps(ddata_message), qos=1)

    def send_device_death(self, device_id):
        """Send device death certificate"""
        topic = f"spBv1.0/{self.group_id}/DDEATH/{self.edge_node_id}/{device_id}"
        message = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "seq": self.seq,
            "uuid": self.edge_node_id
        }
        self.seq = (self.seq + 1) % 256

        self.client.publish(topic, json.dumps(message), qos=1)

    def send_node_death(self):
        """Send node death certificate"""
        topic = f"spBv1.0/{self.group_id}/NDEATH/{self.edge_node_id}"
        message = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

        self.client.publish(topic, json.dumps(message), qos=1)

    def register_device(self, device_id, device_type, metrics_template):
        """Register device with edge node"""
        self.devices[device_id] = {
            "type": device_type,
            "metrics_template": metrics_template
        }

    def handle_device_command(self, device_id, command):
        """Process command for device"""
        print(f"Received command for {device_id}: {command}")
        # Implement command handling logic

    def connect(self):
        """Connect to MQTT broker"""
        self.client.connect(self.broker_host, 1883, keepalive=60)
        self.client.loop_start()

    def disconnect(self):
        """Graceful disconnect"""
        self.send_node_death()
        self.client.loop_stop()
        self.client.disconnect()
```

## MQTT Broker Configuration

### Mosquitto Configuration for Manufacturing

```
# /etc/mosquitto/mosquitto.conf

# Port configuration
listener 1883
protocol mqtt

listener 8883
protocol mqtt
cafile /etc/mosquitto/ca.crt
certfile /etc/mosquitto/server.crt
keyfile /etc/mosquitto/server.key

# WebSocket support (for browsers and remote monitoring)
listener 9001
protocol websockets

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Message routing and filtering
# Allow clients to access only their device topics
acl_file /etc/mosquitto/acl.conf

# Performance tuning
max_connections -1
max_queued_messages 1000
message_size_limit 0

# Topic-based access control
allow_anonymous false
password_file /etc/mosquitto/passwd

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_dest syslog
log_timestamp true
log_type all

# Enable debugging (disable in production)
#debug_subscribe true
#debug_unsubscribe true

# Keep-alive interval (seconds)
#keep_alive_interval 60
```

### Access Control List (ACL)

```
# /etc/mosquitto/acl.conf

# Default deny all
pattern read $SYS/#
pattern write $SYS/#

# Broker system messages
pattern read $SYS/broker/clients/connected
pattern read $SYS/broker/clients/disconnected

# Device patterns
pattern write spBv1.0/+/DDATA/+/+
pattern write spBv1.0/+/DDEATH/+/+
pattern write spBv1.0/+/NBIRTH/+
pattern write spBv1.0/+/NDEATH/+

pattern read spBv1.0/+/DCMD/+/+
pattern read spBv1.0/+/DCMD/+

# Specific user permissions
user device-001
topic write spBv1.0/plant-01/DDATA/edge-01/robot-01
topic read spBv1.0/plant-01/DCMD/edge-01/robot-01
topic write spBv1.0/plant-01/DDEATH/edge-01/robot-01

user device-002
topic write spBv1.0/plant-01/DDATA/edge-01/conveyor-01
topic read spBv1.0/plant-01/DCMD/edge-01/conveyor-01
```

### HiveMQ Configuration (Enterprise)

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<hivemq xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="config.xsd">

    <listeners>
        <tcp-listener>
            <port>1883</port>
            <bind-address>0.0.0.0</bind-address>
        </tcp-listener>

        <tls-tcp-listener>
            <port>8883</port>
            <bind-address>0.0.0.0</bind-address>
            <tls>
                <keystore>
                    <path>/opt/hivemq/certs/server.jks</path>
                    <password>changeit</password>
                </keystore>
            </tls>
        </tls-tcp-listener>

        <websocket-listener>
            <port>8000</port>
            <path>/mqtt</path>
        </websocket-listener>
    </listeners>

    <!-- Performance settings -->
    <mqtt>
        <session-expiry-interval>7200</session-expiry-interval>
        <message-expiry-interval>3600</message-expiry-interval>
        <max-packet-size>268435455</max-packet-size>
        <max-topic-alias>10</max-topic-alias>
    </mqtt>

    <!-- Clustering for high availability -->
    <cluster>
        <replication>
            <replica-count>2</replica-count>
        </replication>
    </cluster>

    <!-- Extensions for authentication/authorization -->
    <extensions>
        <extension>
            <name>hivemq-mqtt-authentication-extension</name>
            <enabled>true</enabled>
        </extension>
    </extensions>
</hivemq>
```

## Performance Optimization

### Message Batching

```python
class BatchedSparkplugPublisher:
    def __init__(self, client, group_id, edge_node_id, batch_size=100, batch_timeout=5):
        self.client = client
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.buffer = []
        self.last_flush = time.time()
        self.seq = 0

    def add_metric(self, device_id, metric_name, value, datatype):
        """Add metric to batch buffer"""
        self.buffer.append({
            "device_id": device_id,
            "metric_name": metric_name,
            "value": value,
            "datatype": datatype
        })

        # Flush if buffer is full
        if len(self.buffer) >= self.batch_size:
            self.flush()
        # Or flush on timeout
        elif time.time() - self.last_flush > self.batch_timeout:
            self.flush()

    def flush(self):
        """Flush buffered metrics"""
        if not self.buffer:
            return

        # Group by device
        by_device = {}
        for item in self.buffer:
            device = item['device_id']
            if device not in by_device:
                by_device[device] = []
            by_device[device].append(item)

        # Publish per device
        for device_id, metrics in by_device.items():
            metrics_list = [
                {
                    "name": m["metric_name"],
                    "timestamp": int(time.time() * 1000),
                    "datatype": m["datatype"],
                    "value": m["value"]
                }
                for m in metrics
            ]

            message = {
                "timestamp": int(time.time() * 1000),
                "metrics": metrics_list,
                "seq": self.seq,
                "uuid": self.edge_node_id
            }

            self.seq = (self.seq + 1) % 256

            topic = f"spBv1.0/{self.group_id}/DDATA/{self.edge_node_id}/{device_id}"
            self.client.publish(topic, json.dumps(message), qos=1)

        self.buffer = []
        self.last_flush = time.time()
```

### Connection Management with Reconnection

```python
import time
import random

class RobustMQTTClient:
    def __init__(self, broker, client_id):
        self.broker = broker
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.max_retries = 10
        self.retry_delay = 1

    def connect_with_retry(self):
        """Connect with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                self.client.connect(self.broker, 1883, keepalive=60)
                self.client.loop_start()
                self.connected = True
                print(f"Connected after {attempt} attempts")
                return True
            except Exception as e:
                wait_time = min(
                    self.retry_delay * (2 ** attempt) + random.uniform(0, 1),
                    300  # Max 5 minutes
                )
                print(f"Connection failed: {e}, retrying in {wait_time:.1f}s")
                time.sleep(wait_time)

        print("Failed to connect after all retries")
        return False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Successfully connected")
        else:
            self.connected = False
            print(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection, reconnecting...")
            self.connect_with_retry()
```

## Testing and Validation

### MQTT Testing with Mosquitto

```bash
# Install MQTT client tools
sudo apt-get install mosquitto-clients

# Subscribe to all topics (for testing)
mosquitto_sub -h localhost -p 1883 -t '#' -v

# Publish test message
mosquitto_pub -h localhost -p 1883 \
  -t 'spBv1.0/test/DDATA/edge-01/device-01' \
  -m '{"timestamp": 1234567890, "metrics": [{"name": "temperature", "value": 45.5}]}'

# Test with authentication
mosquitto_pub -h localhost -p 8883 \
  -u username -P password \
  --cafile ca.crt \
  --cert client.crt \
  --key client.key \
  -t 'manufacturing/test' \
  -m 'test message'
```

### Load Testing MQTT

```python
import concurrent.futures
import time

def load_test_mqtt(broker, num_devices, messages_per_device):
    """Load test MQTT broker"""
    def publish_messages(device_id):
        client = mqtt.Client(client_id=f"test-{device_id}")
        client.connect(broker, 1883)
        client.loop_start()

        for i in range(messages_per_device):
            topic = f"test/device-{device_id}/metric-{i % 10}"
            message = {
                "value": float(i),
                "timestamp": int(time.time() * 1000)
            }
            client.publish(topic, json.dumps(message), qos=1)
            time.sleep(0.01)  # 10ms between messages

        client.loop_stop()
        client.disconnect()

    # Execute in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(publish_messages, device_id)
            for device_id in range(num_devices)
        ]
        concurrent.futures.wait(futures)

    print(f"Completed: {num_devices} devices x {messages_per_device} messages")
```

## Conclusion

MQTT with Sparkplug B provides a powerful, standardized foundation for manufacturing IoT. By following these implementation patterns and best practices, you can build reliable, scalable, and maintainable systems that serve as the backbone of Industry 4.0 operations.

Key takeaways:
- Choose appropriate QoS levels for your data
- Use Sparkplug B for semantic standardization
- Implement robust error handling and reconnection logic
- Properly configure broker security and access control
- Test thoroughly before production deployment
- Monitor and optimize for your specific load patterns
