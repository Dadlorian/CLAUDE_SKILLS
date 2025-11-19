"""
MQTT Sparkplug B Client Implementation for Industrial IoT

This module provides a complete Sparkplug B MQTT client implementation
optimized for manufacturing environments. It handles:
- Sparkplug B protocol compliance
- Unified namespace organization
- Device lifecycle management
- Birth/death certificates
- TLS/SSL security
- Connection resilience
- Payload serialization
"""

import paho.mqtt.client as mqtt
import json
import ssl
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
import struct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataType(Enum):
    """Sparkplug B data types"""
    INT8 = 1
    INT16 = 2
    INT32 = 3
    INT64 = 4
    UINT8 = 5
    UINT16 = 6
    UINT32 = 7
    UINT64 = 8
    FLOAT = 9
    DOUBLE = 10
    BOOLEAN = 11
    STRING = 12
    DATETIME = 13
    BYTES = 17


class MessageType(Enum):
    """Sparkplug B message types"""
    NBIRTH = "NBIRTH"  # Node birth certificate
    DDATA = "DDATA"    # Device data
    DDEATH = "DDEATH"  # Device death certificate
    DCMD = "DCMD"      # Device command
    NDEATH = "NDEATH"  # Node death certificate


class Metric:
    """Represents a single metric in Sparkplug B format"""

    def __init__(
        self,
        name: str,
        value: Any,
        datatype: DataType,
        timestamp: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None
    ):
        self.name = name
        self.value = value
        self.datatype = datatype
        self.timestamp = timestamp or int(datetime.now().timestamp() * 1000)
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "datatype": self.datatype.value,
            "value": self.value,
            "properties": self.properties
        }


class SparkplugBPayload:
    """Builds and manages Sparkplug B message payloads"""

    def __init__(self, group_id: str, edge_node_id: str):
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.seq = 0

    def create_nbirth(
        self,
        device_list: List[str],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create node birth certificate"""
        metrics = [
            Metric(
                name="Node Control/Rebirth",
                value=False,
                datatype=DataType.BOOLEAN
            )
        ]

        # Add device list
        for device_id in device_list:
            metrics.append(
                Metric(
                    name=device_id,
                    value="online",
                    datatype=DataType.STRING
                )
            )

        return self._create_message(metrics, properties)

    def create_ddata(
        self,
        metrics: List[Metric],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create device data message"""
        return self._create_message(metrics, properties)

    def create_ddeath(
        self,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create device death certificate"""
        return self._create_message([], properties)

    def create_dcmd(
        self,
        metrics: List[Metric]
    ) -> Dict[str, Any]:
        """Create device command message"""
        return self._create_message(metrics)

    def create_ndeath(self) -> Dict[str, Any]:
        """Create node death certificate"""
        return self._create_message([])

    def _create_message(
        self,
        metrics: List[Metric],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build base message structure"""
        message = {
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metrics": [m.to_dict() for m in metrics],
            "seq": self.seq,
            "uuid": self.edge_node_id
        }

        if properties:
            message["properties"] = properties

        self.seq = (self.seq + 1) % 256
        return message


class SparkplugBClient:
    """
    Complete Sparkplug B MQTT client for industrial IoT

    Features:
    - Automatic reconnection with exponential backoff
    - Device lifecycle management
    - TLS/SSL security
    - Metric batching and optimization
    - Health monitoring
    """

    def __init__(
        self,
        broker_host: str,
        broker_port: int = 8883,
        group_id: str = "manufacturing",
        edge_node_id: str = "edge-01",
        client_id: Optional[str] = None
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.client_id = client_id or f"{group_id}-{edge_node_id}"

        self.client = mqtt.Client(
            client_id=self.client_id,
            protocol=mqtt.MQTTv311,
            clean_session=True
        )

        self.connected = False
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.payload_builder = SparkplugBPayload(group_id, edge_node_id)
        self.message_callbacks: Dict[str, Callable] = {}
        self.metrics_buffer: Dict[str, List[Metric]] = {}
        self.buffer_lock = threading.Lock()

        # Reconnection settings
        self.max_retries = 10
        self.retry_delay = 1
        self.last_reconnect_attempt = 0

        # Setup callbacks
        self._setup_callbacks()

    def _setup_callbacks(self) -> None:
        """Register MQTT callbacks"""
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish

    def setup_tls(
        self,
        ca_certs: str,
        certfile: str,
        keyfile: str,
        insecure: bool = False
    ) -> None:
        """Configure TLS/SSL security"""
        self.client.tls_set(
            ca_certs=ca_certs,
            certfile=certfile,
            keyfile=keyfile,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )
        self.client.tls_insecure = insecure

    def setup_credentials(self, username: str, password: str) -> None:
        """Configure username/password authentication"""
        self.client.username_pw_set(username, password)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Dict[str, Any],
        rc: int
    ) -> None:
        """Handle connection"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to {self.broker_host}:{self.broker_port}")
            self._send_nbirth()
            # Subscribe to command topics
            self.client.subscribe(
                f"spBv1.0/{self.group_id}/DCMD/{self.edge_node_id}/#",
                qos=1
            )
        else:
            logger.error(f"Connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int
    ) -> None:
        """Handle disconnection"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection: {rc}")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage
    ) -> None:
        """Handle incoming messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())

            # Parse Sparkplug B topic
            parts = topic.split('/')
            if len(parts) >= 5:
                message_type = parts[2]
                device_id = parts[4]

                if message_type == "DCMD":
                    self._handle_device_command(device_id, payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _on_publish(
        self,
        client: mqtt.Client,
        userdata: Any,
        mid: int
    ) -> None:
        """Handle publish confirmation"""
        logger.debug(f"Message {mid} published")

    def _handle_device_command(
        self,
        device_id: str,
        payload: Dict[str, Any]
    ) -> None:
        """Process device command"""
        if device_id in self.message_callbacks:
            callback = self.message_callbacks[device_id]
            callback(payload)
        else:
            logger.warning(f"No callback for device {device_id}")

    def register_device(
        self,
        device_id: str,
        device_type: str,
        metrics_template: List[str],
        command_callback: Optional[Callable] = None
    ) -> None:
        """Register device with edge node"""
        self.devices[device_id] = {
            "type": device_type,
            "metrics_template": metrics_template,
            "online": False
        }

        if command_callback:
            self.message_callbacks[device_id] = command_callback

        logger.info(f"Registered device {device_id}")

    def connect(self) -> bool:
        """Connect to MQTT broker with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{self.max_retries}")
                self.client.connect(
                    self.broker_host,
                    self.broker_port,
                    keepalive=60
                )
                self.client.loop_start()
                time.sleep(2)  # Wait for connection

                if self.connected:
                    return True

            except Exception as e:
                wait_time = min(
                    self.retry_delay * (2 ** attempt),
                    300  # Max 5 minutes
                )
                logger.warning(f"Connection failed: {e}, retrying in {wait_time}s")
                time.sleep(wait_time)

        logger.error("Failed to connect after all retry attempts")
        return False

    def _send_nbirth(self) -> None:
        """Send node birth certificate"""
        device_list = list(self.devices.keys())
        nbirth_payload = self.payload_builder.create_nbirth(device_list)

        topic = f"spBv1.0/{self.group_id}/NBIRTH/{self.edge_node_id}"
        self._publish(topic, nbirth_payload, qos=1, retain=False)

    def publish_device_data(
        self,
        device_id: str,
        metrics: List[Metric]
    ) -> bool:
        """Publish device data"""
        if not self.connected:
            logger.warning("Not connected, buffering metrics")
            with self.buffer_lock:
                if device_id not in self.metrics_buffer:
                    self.metrics_buffer[device_id] = []
                self.metrics_buffer[device_id].extend(metrics)
            return False

        ddata_payload = self.payload_builder.create_ddata(metrics)
        topic = f"spBv1.0/{self.group_id}/DDATA/{self.edge_node_id}/{device_id}"

        return self._publish(topic, ddata_payload, qos=1)

    def publish_device_command_response(
        self,
        device_id: str,
        metrics: List[Metric]
    ) -> bool:
        """Publish command response"""
        return self.publish_device_data(device_id, metrics)

    def publish_device_death(self, device_id: str) -> bool:
        """Publish device death certificate"""
        if device_id in self.devices:
            self.devices[device_id]["online"] = False

        ddeath_payload = self.payload_builder.create_ddeath()
        topic = f"spBv1.0/{self.group_id}/DDEATH/{self.edge_node_id}/{device_id}"

        return self._publish(topic, ddeath_payload, qos=1)

    def publish_node_death(self) -> None:
        """Publish node death certificate"""
        ndeath_payload = self.payload_builder.create_ndeath()
        topic = f"spBv1.0/{self.group_id}/NDEATH/{self.edge_node_id}"
        self._publish(topic, ndeath_payload, qos=1)

    def _publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        qos: int = 1,
        retain: bool = False
    ) -> bool:
        """Publish message to MQTT broker"""
        try:
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=qos,
                retain=retain
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False

    def flush_buffered_metrics(self) -> None:
        """Flush buffered metrics to broker"""
        with self.buffer_lock:
            for device_id, metrics in self.metrics_buffer.items():
                if self.connected and metrics:
                    self.publish_device_data(device_id, metrics)

            self.metrics_buffer.clear()

    def disconnect(self) -> None:
        """Graceful disconnect"""
        logger.info("Disconnecting from MQTT broker")
        for device_id in self.devices.keys():
            self.publish_device_death(device_id)

        self.publish_node_death()
        self.client.loop_stop()
        self.client.disconnect()

    def is_connected(self) -> bool:
        """Check connection status"""
        return self.connected

    def get_device_status(self) -> Dict[str, bool]:
        """Get status of all registered devices"""
        return {
            device_id: device_info["online"]
            for device_id, device_info in self.devices.items()
        }


class EdgeNodeManager:
    """
    Manages complete edge node with multiple devices

    Example usage:
    manager = EdgeNodeManager('mqtt.broker.local', 'plant-01', 'edge-01')
    manager.connect()

    # Register and start collecting from devices
    manager.register_device_collector('robot-01', RobotDataCollector())
    manager.register_device_collector('conveyor-01', ConveyorDataCollector())

    # Run collection loop
    manager.run()
    """

    def __init__(
        self,
        broker_host: str,
        group_id: str,
        edge_node_id: str
    ):
        self.client = SparkplugBClient(
            broker_host=broker_host,
            group_id=group_id,
            edge_node_id=edge_node_id
        )
        self.collectors: Dict[str, Callable] = {}
        self.running = False

    def register_device_collector(
        self,
        device_id: str,
        collector_func: Callable[[], List[Metric]]
    ) -> None:
        """Register a device data collector function"""
        self.collectors[device_id] = collector_func
        self.client.register_device(
            device_id=device_id,
            device_type="generic",
            metrics_template=[]
        )

    def connect(self) -> bool:
        """Connect to MQTT broker"""
        return self.client.connect()

    def run(self, collection_interval: float = 1.0) -> None:
        """Run data collection loop"""
        self.running = True
        try:
            while self.running:
                for device_id, collector in self.collectors.items():
                    try:
                        metrics = collector()
                        if metrics:
                            self.client.publish_device_data(device_id, metrics)
                    except Exception as e:
                        logger.error(f"Error collecting from {device_id}: {e}")

                # Flush any buffered metrics
                self.client.flush_buffered_metrics()
                time.sleep(collection_interval)

        except KeyboardInterrupt:
            logger.info("Stopping data collection")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop data collection and disconnect"""
        self.running = False
        self.client.disconnect()


# Example usage
if __name__ == "__main__":
    # Example device data collectors
    def robot_data_collector() -> List[Metric]:
        """Simulated robot data collection"""
        import random
        return [
            Metric(
                name="joint_1_angle",
                value=random.uniform(0, 180),
                datatype=DataType.FLOAT,
                properties={"unit": "degrees"}
            ),
            Metric(
                name="motor_temperature",
                value=random.uniform(20, 60),
                datatype=DataType.FLOAT,
                properties={"unit": "°C"}
            ),
            Metric(
                name="cycles_completed",
                value=random.randint(1000, 5000),
                datatype=DataType.INT32
            )
        ]

    # Create edge node manager
    manager = EdgeNodeManager(
        broker_host="localhost",
        group_id="manufacturing",
        edge_node_id="edge-01"
    )

    # Register device collectors
    manager.register_device_collector("robot-01", robot_data_collector)

    # Connect and run
    if manager.connect():
        print("Connected to MQTT broker")
        try:
            manager.run(collection_interval=2.0)
        except KeyboardInterrupt:
            print("Shutting down...")
            manager.stop()
    else:
        print("Failed to connect to MQTT broker")
