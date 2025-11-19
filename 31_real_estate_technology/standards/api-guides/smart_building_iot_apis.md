# Smart Building IoT APIs

**Version:** 2.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Authority:** PropTech IoT Standards Committee
**References:** BACnet, MQTT, AWS IoT Core, Azure IoT Hub, Honeywell Forge, Siemens Desigo, Cisco DNA Spaces

## Table of Contents

1. [Overview](#overview)
2. [BACnet Protocol Integration](#bacnet-protocol-integration)
3. [MQTT Patterns for Sensors](#mqtt-patterns-for-sensors)
4. [Device Authentication and Provisioning](#device-authentication-and-provisioning)
5. [Time-Series Data APIs](#time-series-data-apis)
6. [Command and Control APIs](#command-and-control-apis)
7. [Real-Time Streaming Patterns](#real-time-streaming-patterns)
8. [Edge Computing Integration](#edge-computing-integration)
9. [Security and Compliance](#security-and-compliance)
10. [Vendor Integration Patterns](#vendor-integration-patterns)

## Overview

Smart buildings integrate IoT devices for HVAC, lighting, access control, occupancy sensing, and energy management. This guide covers API patterns for building automation systems drawing from Honeywell Forge, Siemens Desigo CC, Johnson Controls Metasys, and Cisco DNA Spaces.

### Common IoT Device Types

| Device Category | Examples | Data Types | Update Frequency |
|----------------|----------|------------|------------------|
| **HVAC** | Thermostats, RTUs, chillers | Temperature, humidity, setpoints | 1-5 min |
| **Lighting** | Smart switches, dimmer controls | On/off, brightness level | Real-time |
| **Occupancy** | PIR sensors, CO2 sensors | Presence, count | 30 sec - 5 min |
| **Energy** | Smart meters, sub-meters | kWh consumption, demand | 15 min |
| **Access** | Door locks, card readers | Access events, battery level | Real-time (events) |
| **Water** | Leak detectors, flow meters | Flow rate, leak detection | 5-15 min |
| **Environmental** | Air quality sensors | CO2, VOC, PM2.5 | 5-15 min |

### Architecture Patterns

```
┌─────────────────────────────────────────────────┐
│            Cloud Platform (AWS/Azure)           │
│  ┌──────────────┐  ┌──────────────────────┐   │
│  │ IoT Hub/Core │  │ Time-Series Database │   │
│  └──────────────┘  └──────────────────────┘   │
└──────────────┬─────────────────┬────────────────┘
               │                 │
      ┌────────┴────────┐   ┌───┴───────┐
      │  Edge Gateway   │   │  Mobile   │
      │  (Raspberry Pi) │   │  Devices  │
      └────────┬────────┘   └───────────┘
               │
    ┌──────────┴──────────────┐
    │                         │
┌───┴────┐  ┌────┴─────┐  ┌──┴────┐
│ BACnet │  │   MQTT   │  │ Modbus│
│ Devices│  │  Sensors │  │ Sensors│
└────────┘  └──────────┘  └────────┘
```

## BACnet Protocol Integration

### BACnet Overview

**BACnet (Building Automation and Control Network)** is the ASHRAE, ANSI, ISO standard protocol for building automation.

**Versions:** BACnet/IP (UDP), BACnet/SC (secure WebSocket)

**Common Object Types:**
- **Analog Input (AI)**: Temperature sensor, humidity sensor
- **Analog Output (AO)**: Damper position, valve position
- **Analog Value (AV)**: Computed values, setpoints
- **Binary Input (BI)**: Occupancy status, door status
- **Binary Output (BO)**: On/off commands
- **Multi-State Input (MI)**: Mode indicator
- **Device Object**: BACnet device metadata

### BACnet Discovery

```python
import BAC0
from BAC0.core.devices.Device import Device

class BACnetGateway:
    def __init__(self, interface="eth0", network="192.168.1.0/24"):
        # Initialize BACnet/IP connection
        self.bacnet = BAC0.lite(ip=interface)

    def discover_devices(self):
        """
        Discover BACnet devices on network using WhoIs broadcast
        """
        # Send WhoIs broadcast
        self.bacnet.whois()

        # Wait for IAm responses
        time.sleep(5)

        # Get discovered devices
        devices = []
        for device_id in self.bacnet.devices:
            device_info = {
                "device_id": device_id,
                "device_name": self.bacnet.read(f"{device_id} device objectName"),
                "vendor_name": self.bacnet.read(f"{device_id} device vendorName"),
                "model_name": self.bacnet.read(f"{device_id} device modelName"),
                "ip_address": self.bacnet.devices[device_id].address
            }
            devices.append(device_info)

        return devices

    def read_device_objects(self, device_id):
        """
        Read all objects (points) from a BACnet device
        """
        # Get object list
        object_list = self.bacnet.read(f"{device_id} device objectList")

        points = []
        for obj_type, obj_id in object_list:
            try:
                # Read object name and present value
                point = {
                    "object_type": obj_type,
                    "object_id": obj_id,
                    "object_name": self.bacnet.read(f"{device_id} {obj_type} {obj_id} objectName"),
                    "present_value": self.bacnet.read(f"{device_id} {obj_type} {obj_id} presentValue"),
                    "units": self.bacnet.read(f"{device_id} {obj_type} {obj_id} units")
                }
                points.append(point)
            except Exception as e:
                print(f"Error reading {obj_type}:{obj_id}: {e}")

        return points

    def read_temperature(self, device_id, object_id):
        """
        Read temperature from analog input
        """
        # Read present value
        temp = self.bacnet.read(f"{device_id} analogInput {object_id} presentValue")
        units = self.bacnet.read(f"{device_id} analogInput {object_id} units")

        return {"temperature": temp, "units": units}

    def write_setpoint(self, device_id, object_id, value):
        """
        Write setpoint to analog value
        """
        # Write to present value
        self.bacnet.write(
            f"{device_id} analogValue {object_id} presentValue",
            value,
            priority=8  # Manual operator (priority 1-16, lower = higher)
        )

    def subscribe_to_cov(self, device_id, object_type, object_id, callback):
        """
        Subscribe to Change-of-Value (COV) notifications
        """
        # Subscribe to COV
        self.bacnet.cov(
            device_id,
            object_type,
            object_id,
            callback=callback,
            lifetime=3600  # Subscription lifetime in seconds
        )
```

### BACnet REST API Wrapper

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
bacnet_gateway = BACnetGateway()

class SetpointRequest(BaseModel):
    device_id: int
    object_id: int
    value: float

@app.get("/devices")
async def list_devices():
    """
    List all discovered BACnet devices
    """
    devices = bacnet_gateway.discover_devices()
    return {"devices": devices}

@app.get("/devices/{device_id}/points")
async def list_device_points(device_id: int):
    """
    List all points for a device
    """
    points = bacnet_gateway.read_device_objects(device_id)
    return {"device_id": device_id, "points": points}

@app.get("/devices/{device_id}/temperature/{object_id}")
async def read_temperature(device_id: int, object_id: int):
    """
    Read temperature from sensor
    """
    reading = bacnet_gateway.read_temperature(device_id, object_id)
    return reading

@app.post("/devices/{device_id}/setpoint/{object_id}")
async def write_setpoint(device_id: int, object_id: int, request: SetpointRequest):
    """
    Write setpoint value
    """
    try:
        bacnet_gateway.write_setpoint(device_id, object_id, request.value)
        return {"success": True, "device_id": device_id, "object_id": object_id, "value": request.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## MQTT Patterns for Sensors

### MQTT Overview

**MQTT (Message Queuing Telemetry Transport)** is a lightweight pub/sub protocol ideal for IoT sensors.

**Advantages:**
- Low bandwidth usage
- Persistent connections
- Quality of Service (QoS) levels
- Retained messages
- Last Will and Testament (LWT)

### Topic Structure

```
Standard Topic Hierarchy:

{organization}/{site}/{building}/{floor}/{room}/{device_type}/{device_id}/{metric}

Examples:
proptech/hq/building-a/floor-3/conference-room-301/temperature-sensor/ts-12345/reading
proptech/hq/building-a/floor-3/conference-room-301/occupancy-sensor/occ-67890/count
proptech/hq/building-a/hvac/rtu-1/status
proptech/hq/building-a/lighting/zone-3a/command
```

### MQTT Publisher (Sensor)

```python
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class TemperatureSensor:
    def __init__(self, mqtt_broker, mqtt_port, device_id, location):
        self.device_id = device_id
        self.location = location
        self.topic = f"proptech/hq/building-a/{location}/temperature-sensor/{device_id}/reading"

        # MQTT client setup
        self.client = mqtt.Client(client_id=device_id)
        self.client.username_pw_set("username", "password")
        self.client.tls_set()  # Enable TLS

        # Connect to broker
        self.client.connect(mqtt_broker, mqtt_port, keepalive=60)
        self.client.loop_start()

    def read_temperature(self):
        """
        Simulate reading temperature from sensor
        """
        import random
        return 68.0 + random.uniform(-2, 2)

    def publish_reading(self):
        """
        Publish temperature reading
        """
        temperature = self.read_temperature()

        payload = {
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "temperature": temperature,
            "units": "fahrenheit",
            "location": self.location
        }

        # Publish with QoS 1 (at least once delivery)
        result = self.client.publish(
            self.topic,
            payload=json.dumps(payload),
            qos=1,
            retain=False
        )

        return result.is_published()

    def run(self, interval_seconds=60):
        """
        Continuously publish readings
        """
        while True:
            self.publish_reading()
            time.sleep(interval_seconds)

# Usage
sensor = TemperatureSensor(
    mqtt_broker="mqtt.proptech.com",
    mqtt_port=8883,
    device_id="ts-12345",
    location="floor-3/conference-room-301"
)
sensor.run(interval_seconds=60)
```

### MQTT Subscriber (Cloud Service)

```python
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class IoTDataIngestion:
    def __init__(self, mqtt_broker, mqtt_port, database):
        self.db = database

        # MQTT client setup
        self.client = mqtt.Client(client_id="cloud-ingestion-service")
        self.client.username_pw_set("username", "password")
        self.client.tls_set()

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect
        self.client.connect(mqtt_broker, mqtt_port, keepalive=60)

    def on_connect(self, client, userdata, flags, rc):
        """
        Called when connected to MQTT broker
        """
        print(f"Connected to MQTT broker with result code {rc}")

        # Subscribe to all temperature sensors
        client.subscribe("proptech/hq/+/+/+/temperature-sensor/+/reading")

        # Subscribe to all occupancy sensors
        client.subscribe("proptech/hq/+/+/+/occupancy-sensor/+/count")

    def on_message(self, client, userdata, msg):
        """
        Called when message received
        """
        try:
            # Parse topic
            topic_parts = msg.topic.split("/")
            building = topic_parts[2]
            location = "/".join(topic_parts[3:6])
            device_type = topic_parts[6]
            device_id = topic_parts[7]
            metric = topic_parts[8]

            # Parse payload
            payload = json.loads(msg.payload.decode())

            # Store in time-series database
            self.store_reading(
                device_id=device_id,
                device_type=device_type,
                building=building,
                location=location,
                metric=metric,
                value=payload.get("temperature") or payload.get("count"),
                timestamp=payload["timestamp"]
            )

        except Exception as e:
            print(f"Error processing message: {e}")

    def store_reading(self, device_id, device_type, building, location, metric, value, timestamp):
        """
        Store reading in time-series database (InfluxDB, TimescaleDB)
        """
        self.db.write_point(
            measurement=device_type,
            tags={
                "device_id": device_id,
                "building": building,
                "location": location,
                "metric": metric
            },
            fields={"value": value},
            timestamp=timestamp
        )

    def run(self):
        """
        Start listening for messages
        """
        self.client.loop_forever()

# Usage
ingestion = IoTDataIngestion(
    mqtt_broker="mqtt.proptech.com",
    mqtt_port=8883,
    database=InfluxDBClient()
)
ingestion.run()
```

### MQTT Command Pattern

```python
class HVACController:
    def __init__(self, mqtt_broker, mqtt_port):
        self.client = mqtt.Client()
        self.client.username_pw_set("username", "password")
        self.client.tls_set()
        self.client.connect(mqtt_broker, mqtt_port)
        self.client.loop_start()

    def set_temperature_setpoint(self, building, zone, setpoint):
        """
        Send command to set temperature setpoint
        """
        command_topic = f"proptech/hq/{building}/hvac/{zone}/command"

        command = {
            "command": "set_temperature",
            "setpoint": setpoint,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.client.publish(
            command_topic,
            payload=json.dumps(command),
            qos=1  # Ensure delivery
        )

    def set_mode(self, building, zone, mode):
        """
        Set HVAC mode (heat, cool, auto, off)
        """
        command_topic = f"proptech/hq/{building}/hvac/{zone}/command"

        command = {
            "command": "set_mode",
            "mode": mode,  # heat, cool, auto, off
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.client.publish(command_topic, payload=json.dumps(command), qos=1)
```

## Device Authentication and Provisioning

### X.509 Certificate Authentication (AWS IoT Core)

```python
import boto3
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

class DeviceProvisioning:
    def __init__(self):
        self.iot_client = boto3.client('iot')

    def provision_device(self, device_id, device_type, location):
        """
        Provision new IoT device with certificate
        """
        # 1. Create IoT Thing
        thing_response = self.iot_client.create_thing(
            thingName=device_id,
            attributePayload={
                'attributes': {
                    'device_type': device_type,
                    'location': location
                }
            }
        )

        # 2. Create keys and certificate
        cert_response = self.iot_client.create_keys_and_certificate(
            setAsActive=True
        )

        certificate_pem = cert_response['certificatePem']
        private_key = cert_response['keyPair']['PrivateKey']
        certificate_arn = cert_response['certificateArn']

        # 3. Create and attach policy
        policy_name = f"{device_id}-policy"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["iot:Connect"],
                    "Resource": [f"arn:aws:iot:*:*:client/{device_id}"]
                },
                {
                    "Effect": "Allow",
                    "Action": ["iot:Publish"],
                    "Resource": [f"arn:aws:iot:*:*:topic/proptech/hq/+/+/+/{device_id}/*"]
                },
                {
                    "Effect": "Allow",
                    "Action": ["iot:Subscribe", "iot:Receive"],
                    "Resource": [f"arn:aws:iot:*:*:topicfilter/proptech/hq/+/+/+/{device_id}/command"]
                }
            ]
        }

        self.iot_client.create_policy(
            policyName=policy_name,
            policyDocument=json.dumps(policy_document)
        )

        # 4. Attach policy to certificate
        self.iot_client.attach_policy(
            policyName=policy_name,
            target=certificate_arn
        )

        # 5. Attach certificate to thing
        self.iot_client.attach_thing_principal(
            thingName=device_id,
            principal=certificate_arn
        )

        return {
            "device_id": device_id,
            "certificate_pem": certificate_pem,
            "private_key": private_key,
            "endpoint": self.get_iot_endpoint()
        }

    def get_iot_endpoint(self):
        """
        Get AWS IoT Core endpoint
        """
        response = self.iot_client.describe_endpoint(
            endpointType='iot:Data-ATS'
        )
        return response['endpointAddress']
```

### Device Connection with Certificate

```python
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

class SecureIoTDevice:
    def __init__(self, device_id, endpoint, certificate_path, private_key_path, root_ca_path):
        self.device_id = device_id

        # Initialize MQTT client
        self.mqtt_client = AWSIoTMQTTClient(device_id)
        self.mqtt_client.configureEndpoint(endpoint, 8883)
        self.mqtt_client.configureCredentials(
            root_ca_path,
            private_key_path,
            certificate_path
        )

        # Configure connection
        self.mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite
        self.mqtt_client.configureDrainingFrequency(2)
        self.mqtt_client.configureConnectDisconnectTimeout(10)
        self.mqtt_client.configureMQTTOperationTimeout(5)

    def connect(self):
        """
        Connect to AWS IoT Core
        """
        self.mqtt_client.connect()
        print(f"Device {self.device_id} connected to AWS IoT Core")

    def publish_telemetry(self, sensor_type, value):
        """
        Publish telemetry data
        """
        topic = f"proptech/hq/building-a/floor-3/{self.device_id}/{sensor_type}"

        payload = {
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sensor_type": sensor_type,
            "value": value
        }

        self.mqtt_client.publish(topic, json.dumps(payload), 1)
```

## Time-Series Data APIs

### TimescaleDB Schema

```sql
-- Hypertable for sensor readings
CREATE TABLE sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    device_type TEXT NOT NULL,
    building TEXT NOT NULL,
    location TEXT NOT NULL,
    metric TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    units TEXT
);

-- Convert to hypertable (automatically partitions by time)
SELECT create_hypertable('sensor_readings', 'time');

-- Create indexes
CREATE INDEX idx_sensor_readings_device_id ON sensor_readings (device_id, time DESC);
CREATE INDEX idx_sensor_readings_location ON sensor_readings (building, location, time DESC);

-- Continuous aggregates (materialized views)
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    device_type,
    building,
    location,
    metric,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS reading_count
FROM sensor_readings
GROUP BY bucket, device_id, device_type, building, location, metric;

-- Refresh policy (auto-refresh every hour)
SELECT add_continuous_aggregate_policy('sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Data retention policy (drop data older than 2 years)
SELECT add_retention_policy('sensor_readings', INTERVAL '2 years');
```

### Time-Series Query API

```python
from fastapi import FastAPI, Query
from datetime import datetime, timedelta
import psycopg2

app = FastAPI()

@app.get("/api/v1/sensors/{device_id}/readings")
async def get_sensor_readings(
    device_id: str,
    start_time: datetime = Query(..., description="Start time (ISO 8601)"),
    end_time: datetime = Query(..., description="End time (ISO 8601)"),
    metric: str = Query(None, description="Metric name (temperature, humidity, etc.)"),
    aggregation: str = Query("raw", description="raw, 1m, 5m, 1h, 1d")
):
    """
    Retrieve sensor readings for time range
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if aggregation == "raw":
        # Raw data
        query = """
        SELECT time, value, units
        FROM sensor_readings
        WHERE device_id = %s
          AND time >= %s
          AND time <= %s
          AND (%s IS NULL OR metric = %s)
        ORDER BY time ASC
        """
        cursor.execute(query, (device_id, start_time, end_time, metric, metric))

    else:
        # Aggregated data
        interval = aggregation  # "1m", "5m", "1h", "1d"
        query = """
        SELECT
            time_bucket(%s, time) AS bucket,
            AVG(value) AS avg_value,
            MIN(value) AS min_value,
            MAX(value) AS max_value
        FROM sensor_readings
        WHERE device_id = %s
          AND time >= %s
          AND time <= %s
          AND (%s IS NULL OR metric = %s)
        GROUP BY bucket
        ORDER BY bucket ASC
        """
        cursor.execute(query, (interval, device_id, start_time, end_time, metric, metric))

    readings = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        "device_id": device_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "aggregation": aggregation,
        "readings": [
            {
                "timestamp": row[0].isoformat(),
                "value": row[1],
                "units": row[2] if aggregation == "raw" else None
            }
            for row in readings
        ]
    }

@app.get("/api/v1/buildings/{building_id}/energy-consumption")
async def get_energy_consumption(
    building_id: str,
    start_date: datetime,
    end_date: datetime
):
    """
    Get energy consumption for building
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        time_bucket('1 hour', time) AS hour,
        SUM(value) AS total_kwh
    FROM sensor_readings
    WHERE building = %s
      AND device_type = 'energy_meter'
      AND metric = 'kwh'
      AND time >= %s
      AND time <= %s
    GROUP BY hour
    ORDER BY hour ASC
    """

    cursor.execute(query, (building_id, start_date, end_date))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        "building_id": building_id,
        "total_kwh": sum(row[1] for row in results),
        "hourly_consumption": [
            {"hour": row[0].isoformat(), "kwh": row[1]}
            for row in results
        ]
    }
```

## Command and Control APIs

### REST API for Device Control

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

class HVACMode(str, Enum):
    HEAT = "heat"
    COOL = "cool"
    AUTO = "auto"
    OFF = "off"

class SetTemperatureCommand(BaseModel):
    setpoint: float
    mode: HVACMode = HVACMode.AUTO

class SetLightingCommand(BaseModel):
    brightness: int  # 0-100
    color_temperature: int = None  # 2700-6500 Kelvin

@app.post("/api/v1/devices/hvac/{device_id}/set-temperature")
async def set_hvac_temperature(device_id: str, command: SetTemperatureCommand):
    """
    Set HVAC temperature setpoint
    """
    # Validate setpoint range
    if not 60 <= command.setpoint <= 85:
        raise HTTPException(status_code=400, detail="Setpoint must be between 60-85°F")

    # Send command via MQTT
    mqtt_client = get_mqtt_client()
    command_topic = f"proptech/hq/building-a/hvac/{device_id}/command"

    payload = {
        "command": "set_temperature",
        "setpoint": command.setpoint,
        "mode": command.mode.value,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    mqtt_client.publish(command_topic, json.dumps(payload), qos=1)

    # Log command in database
    log_device_command(device_id, "set_temperature", payload)

    return {
        "device_id": device_id,
        "command": "set_temperature",
        "setpoint": command.setpoint,
        "mode": command.mode.value,
        "status": "sent"
    }

@app.post("/api/v1/devices/lighting/{device_id}/set-brightness")
async def set_lighting_brightness(device_id: str, command: SetLightingCommand):
    """
    Set lighting brightness and color temperature
    """
    if not 0 <= command.brightness <= 100:
        raise HTTPException(status_code=400, detail="Brightness must be 0-100")

    mqtt_client = get_mqtt_client()
    command_topic = f"proptech/hq/building-a/lighting/{device_id}/command"

    payload = {
        "command": "set_brightness",
        "brightness": command.brightness,
        "color_temperature": command.color_temperature,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    mqtt_client.publish(command_topic, json.dumps(payload), qos=1)

    return {
        "device_id": device_id,
        "command": "set_brightness",
        "brightness": command.brightness,
        "status": "sent"
    }

@app.post("/api/v1/devices/access/{device_id}/unlock")
async def unlock_door(device_id: str, duration_seconds: int = 10):
    """
    Remotely unlock door
    """
    # Verify user has permission
    if not user_has_access(get_current_user(), device_id):
        raise HTTPException(status_code=403, detail="Access denied")

    mqtt_client = get_mqtt_client()
    command_topic = f"proptech/hq/building-a/access/{device_id}/command"

    payload = {
        "command": "unlock",
        "duration_seconds": duration_seconds,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    mqtt_client.publish(command_topic, json.dumps(payload), qos=1)

    # Log access event
    log_access_event(device_id, get_current_user(), "remote_unlock")

    return {
        "device_id": device_id,
        "command": "unlock",
        "duration_seconds": duration_seconds,
        "status": "sent"
    }
```

## Real-Time Streaming Patterns

### WebSocket API for Live Data

```python
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import asyncio
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/sensors/{device_id}")
async def sensor_stream(websocket: WebSocket, device_id: str):
    """
    Stream real-time sensor data via WebSocket
    """
    await manager.connect(websocket)

    try:
        # Subscribe to MQTT topic for this device
        mqtt_client = get_mqtt_client()
        topic = f"proptech/hq/+/+/+/{device_id}/+"

        def mqtt_callback(client, userdata, msg):
            payload = json.loads(msg.payload.decode())
            asyncio.create_task(websocket.send_json(payload))

        mqtt_client.subscribe(topic)
        mqtt_client.message_callback_add(topic, mqtt_callback)

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo or process commands

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        mqtt_client.unsubscribe(topic)
```

## Edge Computing Integration

### AWS IoT Greengrass Configuration

```python
import greengrasssdk
import json

# Initialize Greengrass SDK
iot_client = greengrasssdk.client('iot-data')

def lambda_handler(event, context):
    """
    Edge Lambda function for local processing
    """
    # Process sensor reading locally
    device_id = event['device_id']
    temperature = event['temperature']

    # Local decision making (no cloud required)
    if temperature > 78:
        # Send command to HVAC to increase cooling
        command = {
            "command": "set_mode",
            "mode": "cool",
            "setpoint": 72
        }

        iot_client.publish(
            topic=f"proptech/hq/building-a/hvac/zone-1/command",
            payload=json.dumps(command)
        )

    # Forward to cloud for analytics
    iot_client.publish(
        topic=f"cloud/analytics/{device_id}",
        payload=json.dumps(event)
    )

    return {"statusCode": 200}
```

## Security and Compliance

### Device Shadow Pattern

```python
# AWS IoT Device Shadow for state synchronization
class DeviceShadow:
    def __init__(self, iot_client, thing_name):
        self.iot_client = iot_client
        self.thing_name = thing_name

    def update_reported_state(self, state):
        """
        Device reports current state
        """
        shadow_update = {
            "state": {
                "reported": state
            }
        }

        self.iot_client.update_thing_shadow(
            thingName=self.thing_name,
            payload=json.dumps(shadow_update)
        )

    def update_desired_state(self, state):
        """
        Application requests state change
        """
        shadow_update = {
            "state": {
                "desired": state
            }
        }

        self.iot_client.update_thing_shadow(
            thingName=self.thing_name,
            payload=json.dumps(shadow_update)
        )

    def get_shadow(self):
        """
        Get current shadow state
        """
        response = self.iot_client.get_thing_shadow(
            thingName=self.thing_name
        )

        shadow = json.loads(response['payload'].read())
        return shadow['state']
```

## Vendor Integration Patterns

### Honeywell Forge API Integration

```python
class HoneywellForgeClient:
    def __init__(self, api_key, site_id):
        self.api_key = api_key
        self.site_id = site_id
        self.base_url = "https://api.honeywell.com/v1"

    def get_buildings(self):
        """
        Retrieve buildings for site
        """
        response = requests.get(
            f"{self.base_url}/sites/{self.site_id}/buildings",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

    def get_equipment_list(self, building_id):
        """
        Get HVAC equipment
        """
        response = requests.get(
            f"{self.base_url}/buildings/{building_id}/equipment",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

    def get_sensor_data(self, equipment_id, start_time, end_time):
        """
        Retrieve sensor data
        """
        params = {
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat()
        }

        response = requests.get(
            f"{self.base_url}/equipment/{equipment_id}/data",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params=params
        )

        return response.json()
```

---

## References

1. **BACnet Standard**: http://www.bacnet.org/
2. **MQTT Specification**: https://mqtt.org/mqtt-specification/
3. **AWS IoT Core**: https://aws.amazon.com/iot-core/
4. **Azure IoT Hub**: https://azure.microsoft.com/en-us/services/iot-hub/
5. **Honeywell Forge**: https://forge.honeywell.com/
6. **Siemens Desigo**: https://new.siemens.com/global/en/products/buildings/automation.html
7. **TimescaleDB**: https://docs.timescale.com/

---

*This document is maintained by the PropTech IoT Standards Committee. For questions or updates, contact iot@proptech.com.*
