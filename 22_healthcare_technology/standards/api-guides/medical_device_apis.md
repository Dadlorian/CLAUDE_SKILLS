# Medical Device API Design Guide

## Executive Summary

This guide establishes production-grade standards for designing APIs that enable safe, secure, and reliable connectivity with medical devices. These standards ensure compliance with regulatory requirements, interoperability, and patient safety.

---

## 1. Architecture Overview

### 1.1 Medical Device Integration Stack

```
┌─────────────────────────────────────┐
│   Healthcare IT Systems             │
│   (EHR, EMR, Care Coordination)     │
└────────────┬────────────────────────┘
             │
      ┌──────▼──────┐
      │  API Gateway│
      │  (Security, │
      │   Rate Limit│
      │   Logging)  │
      └──────┬──────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──┐         ┌────▼────┐
│ REST │         │ HL7/    │
│ APIs │         │ FHIR    │
└───┬──┘         └────┬────┘
    │                 │
┌───▼─────────────────▼───┐
│  Device Integration     │
│  Service (DIS)          │
│  - Protocol Translation │
│  - Data Validation      │
│  - State Management     │
└───┬─────────────────────┘
    │
┌───▴────────────────────────┐
│   Device Communication     │
│   ├─ Serial/USB           │
│   ├─ Bluetooth/BLE        │
│   ├─ WiFi                 │
│   └─ Cellular             │
└────────────────────────────┘
```

### 1.2 Design Principles

1. **Safety First**: All design decisions prioritize patient safety
2. **Interoperability**: Support multiple device types and protocols
3. **Reliability**: Ensure data integrity and device availability
4. **Security**: Implement defense-in-depth
5. **Auditability**: Complete audit trails for all operations
6. **Real-time Capability**: Support low-latency critical operations

---

## 2. Core API Specifications

### 2.1 Device Connection Management

#### 2.1.1 API Specification

```yaml
POST /v1/devices/connect
Description: Establish connection with medical device
Parameters:
  device_id: Device identifier (UUID)
  device_type: Type of device (ECG, Ventilator, Monitor, etc.)
  protocol: Connection protocol (Serial, BLE, HTTP, HL7)
  authentication_token: Device authentication credential

Response:
  connection_id: Unique session identifier
  status: CONNECTED | CONNECTING | ERROR
  supported_operations: List of available operations
  capabilities: Device capabilities and limits

Errors:
  400: Invalid device configuration
  401: Authentication failed
  503: Device unreachable
  504: Device timeout
```

#### 2.1.2 Implementation

```python
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class DeviceProtocol(Enum):
    """Supported device communication protocols"""
    SERIAL = "SERIAL"
    BLE = "BLE"
    HTTP_REST = "HTTP_REST"
    HL7 = "HL7"
    MQTT = "MQTT"
    COAP = "COAP"
    PROPRIETARY = "PROPRIETARY"

class DeviceType(Enum):
    """Medical device classifications"""
    ECG_MONITOR = "ECG_MONITOR"
    VENTILATOR = "VENTILATOR"
    INFUSION_PUMP = "INFUSION_PUMP"
    PATIENT_MONITOR = "PATIENT_MONITOR"
    DEFIBRILLATOR = "DEFIBRILLATOR"
    PULSE_OXIMETER = "PULSE_OXIMETER"
    CAPNOGRAPHY = "CAPNOGRAPHY"
    IMAGING_DEVICE = "IMAGING_DEVICE"
    LAB_ANALYZER = "LAB_ANALYZER"

@dataclass
class DeviceCapabilities:
    """Device capabilities and specifications"""
    sampling_rate: int  # Hz
    data_points_per_transmission: int
    measurement_types: List[str]
    accuracy_specification: Dict[str, str]
    battery_status_available: bool
    remote_control_capable: bool
    firmware_version: str
    max_connections: int

@dataclass
class ConnectionSession:
    """Represents an active device connection"""
    connection_id: str
    device_id: str
    device_type: DeviceType
    protocol: DeviceProtocol
    status: str  # CONNECTED, CONNECTING, DISCONNECTED, ERROR
    established_at: datetime
    last_heartbeat: datetime
    capabilities: DeviceCapabilities

    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """Check if connection is still active"""
        elapsed = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return elapsed < timeout_seconds

class DeviceConnectionManager:
    """Manages medical device connections"""

    def __init__(self, device_registry: dict, connection_pool: dict):
        self.device_registry = device_registry  # Device configurations
        self.connection_pool = connection_pool  # Active connections
        self.logger = logger

    def connect_device(
        self,
        device_id: str,
        device_type: str,
        protocol: str,
        authentication_token: str,
        connection_timeout: int = 10
    ) -> Dict:
        """
        Establish connection with medical device

        Args:
            device_id: Unique device identifier
            device_type: Type of medical device
            protocol: Communication protocol
            authentication_token: Device authentication credential
            connection_timeout: Timeout in seconds

        Returns:
            dict: Connection details and capabilities

        Raises:
            DeviceNotFoundException: Device not configured
            AuthenticationException: Authentication failed
            ConnectionTimeoutException: Connection failed within timeout
        """

        connection_id = str(uuid.uuid4())

        try:
            # Validate device configuration
            device_config = self._validate_device_config(
                device_id,
                device_type,
                protocol
            )

            # Authenticate device
            self._authenticate_device(device_id, authentication_token)

            # Initialize protocol-specific connector
            connector = self._get_protocol_connector(protocol)

            # Establish physical connection
            device_connection = connector.connect(
                device_id=device_id,
                device_type=device_type,
                timeout=connection_timeout
            )

            # Query device capabilities
            capabilities = self._query_device_capabilities(device_connection)

            # Create session
            session = ConnectionSession(
                connection_id=connection_id,
                device_id=device_id,
                device_type=DeviceType[device_type],
                protocol=DeviceProtocol[protocol],
                status="CONNECTED",
                established_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
                capabilities=capabilities
            )

            # Store in pool
            self.connection_pool[connection_id] = {
                'session': session,
                'connector': device_connection
            }

            self.logger.info(
                f"Device connected: {device_id} (connection_id={connection_id})"
            )

            return {
                'connection_id': connection_id,
                'status': 'CONNECTED',
                'device_id': device_id,
                'device_type': device_type,
                'protocol': protocol,
                'capabilities': asdict(capabilities),
                'supported_operations': self._get_supported_operations(device_type),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Connection failed for {device_id}: {str(e)}")
            return {
                'status': 'ERROR',
                'error_code': 'CONNECTION_FAILED',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def disconnect_device(self, connection_id: str) -> Dict:
        """Safely disconnect device"""

        if connection_id not in self.connection_pool:
            return {'status': 'ERROR', 'message': 'Connection not found'}

        try:
            pool_entry = self.connection_pool[connection_id]
            connector = pool_entry['connector']

            # Graceful disconnection
            connector.disconnect()

            # Remove from pool
            del self.connection_pool[connection_id]

            self.logger.info(f"Device disconnected: {connection_id}")

            return {
                'status': 'DISCONNECTED',
                'connection_id': connection_id,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Disconnection error: {str(e)}")
            return {'status': 'ERROR', 'message': str(e)}

    def get_connection_status(self, connection_id: str) -> Dict:
        """Get current connection status"""

        if connection_id not in self.connection_pool:
            return {'status': 'NOT_FOUND'}

        session = self.connection_pool[connection_id]['session']

        return {
            'connection_id': connection_id,
            'device_id': session.device_id,
            'status': session.status,
            'is_alive': session.is_alive(),
            'established_at': session.established_at.isoformat(),
            'last_heartbeat': session.last_heartbeat.isoformat(),
            'uptime_seconds': (datetime.utcnow() - session.established_at).total_seconds()
        }

    def _validate_device_config(
        self,
        device_id: str,
        device_type: str,
        protocol: str
    ) -> dict:
        """Validate device configuration"""

        if device_id not in self.device_registry:
            raise ValueError(f"Device {device_id} not configured")

        config = self.device_registry[device_id]

        if device_type not in [dt.name for dt in DeviceType]:
            raise ValueError(f"Invalid device type: {device_type}")

        if protocol not in [dp.name for dp in DeviceProtocol]:
            raise ValueError(f"Invalid protocol: {protocol}")

        return config

    def _authenticate_device(self, device_id: str, token: str) -> bool:
        """Authenticate device using token"""

        # Implementation varies based on auth scheme
        # Could be: certificate, API key, HMAC, JWT, etc.

        device_config = self.device_registry.get(device_id)
        if not device_config:
            raise Exception("Device not found")

        # Validate token against device configuration
        stored_token = device_config.get('auth_token_hash')

        # Use secure comparison
        import hmac
        if not hmac.compare_digest(token, stored_token):
            raise Exception("Authentication failed")

        return True

    def _get_protocol_connector(self, protocol: str):
        """Get appropriate protocol connector"""

        connectors = {
            'SERIAL': SerialConnector,
            'BLE': BLEConnector,
            'HTTP_REST': HTTPConnector,
            'HL7': HL7Connector,
            'MQTT': MQTTConnector,
        }

        connector_class = connectors.get(protocol)
        if not connector_class:
            raise ValueError(f"Unsupported protocol: {protocol}")

        return connector_class()

    def _query_device_capabilities(self, device_connection) -> DeviceCapabilities:
        """Query device for capabilities"""

        # Protocol-specific capability query
        capabilities_data = device_connection.query_capabilities()

        return DeviceCapabilities(
            sampling_rate=capabilities_data.get('sampling_rate', 0),
            data_points_per_transmission=capabilities_data.get('data_points', 0),
            measurement_types=capabilities_data.get('measurements', []),
            accuracy_specification=capabilities_data.get('accuracy', {}),
            battery_status_available=capabilities_data.get('has_battery', False),
            remote_control_capable=capabilities_data.get('remote_control', False),
            firmware_version=capabilities_data.get('firmware_version', 'unknown'),
            max_connections=capabilities_data.get('max_connections', 1)
        )

    def _get_supported_operations(self, device_type: str) -> List[str]:
        """Get supported operations for device type"""

        operations_map = {
            'ECG_MONITOR': ['get_waveform', 'get_vital_signs', 'set_alarms'],
            'VENTILATOR': ['get_parameters', 'set_mode', 'alarm_settings', 'waveforms'],
            'INFUSION_PUMP': ['get_rate', 'set_rate', 'start', 'stop', 'alarm_settings'],
            'PATIENT_MONITOR': ['get_vitals', 'get_alarms', 'trending'],
        }

        return operations_map.get(device_type, [])
```

### 2.2 Real-time Data Streaming

#### 2.2.1 WebSocket API for Live Data

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Callable
import json
import asyncio

class DeviceDataStreamManager:
    """Manages real-time data streaming from devices"""

    def __init__(self):
        self.active_subscriptions = {}  # connection_id -> list of subscribers
        self.data_buffers = {}  # connection_id -> circular buffer

    async def subscribe_to_device_data(
        self,
        websocket: WebSocket,
        connection_id: str,
        data_types: List[str]  # e.g., ['waveform', 'vitals']
    ):
        """
        Subscribe to real-time device data via WebSocket

        Args:
            websocket: WebSocket connection
            connection_id: Device connection ID
            data_types: Types of data to receive
        """

        await websocket.accept()

        subscription_id = str(uuid.uuid4())

        try:
            # Register subscription
            if connection_id not in self.active_subscriptions:
                self.active_subscriptions[connection_id] = []

            subscription = {
                'id': subscription_id,
                'websocket': websocket,
                'data_types': data_types,
                'created_at': datetime.utcnow()
            }

            self.active_subscriptions[connection_id].append(subscription)

            # Send initial confirmation
            await websocket.send_json({
                'type': 'subscription_established',
                'subscription_id': subscription_id,
                'data_types': data_types,
                'timestamp': datetime.utcnow().isoformat()
            })

            # Keep connection alive
            while True:
                # Receive heartbeat/commands from client
                data = await websocket.receive_text()
                command = json.loads(data)

                await self._handle_stream_command(command, subscription)

        except WebSocketDisconnect:
            # Cleanup subscription
            if connection_id in self.active_subscriptions:
                self.active_subscriptions[connection_id] = [
                    s for s in self.active_subscriptions[connection_id]
                    if s['id'] != subscription_id
                ]

    async def broadcast_device_data(
        self,
        connection_id: str,
        data: dict,
        data_type: str
    ):
        """
        Broadcast device data to all subscribed clients

        Args:
            connection_id: Device connection ID
            data: Measurement data
            data_type: Type of data (waveform, vitals, etc.)
        """

        if connection_id not in self.active_subscriptions:
            return

        message = {
            'type': 'device_data',
            'data_type': data_type,
            'connection_id': connection_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'sequence': self._get_next_sequence(connection_id)
        }

        # Send to all subscribers interested in this data type
        subscriptions = self.active_subscriptions[connection_id]
        disconnected = []

        for subscription in subscriptions:
            if data_type not in subscription['data_types']:
                continue

            try:
                await subscription['websocket'].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send data: {str(e)}")
                disconnected.append(subscription)

        # Clean up disconnected subscriptions
        for sub in disconnected:
            subscriptions.remove(sub)

    async def _handle_stream_command(
        self,
        command: dict,
        subscription: dict
    ):
        """Handle commands from streaming client"""

        cmd_type = command.get('type')

        if cmd_type == 'heartbeat':
            # Acknowledge heartbeat
            await subscription['websocket'].send_json({
                'type': 'heartbeat_ack',
                'timestamp': datetime.utcnow().isoformat()
            })

        elif cmd_type == 'update_subscriptions':
            # Update subscribed data types
            subscription['data_types'] = command.get('data_types', [])

        elif cmd_type == 'device_command':
            # Forward command to device
            await self._execute_device_command(
                command.get('device_command'),
                command.get('connection_id')
            )

    def _get_next_sequence(self, connection_id: str) -> int:
        """Get next sequence number for data stream"""

        if connection_id not in self.data_buffers:
            self.data_buffers[connection_id] = {'sequence': 0}

        self.data_buffers[connection_id]['sequence'] += 1
        return self.data_buffers[connection_id]['sequence']
```

### 2.3 Device Command Execution

#### 2.3.1 Command API

```yaml
POST /v1/devices/{connection_id}/commands
Description: Execute command on medical device
Parameters:
  command_type: Type of command (SET_PARAMETER, ALARM_CONFIG, MODE_CHANGE)
  command_payload: Command-specific parameters
  priority: CRITICAL | HIGH | NORMAL | LOW

Response:
  command_id: Unique command identifier
  status: ACCEPTED | IN_PROGRESS | COMPLETED | FAILED
  result: Command execution result

Errors:
  400: Invalid command
  403: Unauthorized device operation
  504: Device timeout
  423: Device busy
```

#### 2.3.2 Implementation

```python
from enum import Enum
from typing import Any, Optional

class CommandPriority(Enum):
    """Command execution priority"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class DeviceCommandExecutor:
    """Executes commands on medical devices safely"""

    def __init__(self, command_validator, connection_pool):
        self.validator = command_validator
        self.connection_pool = connection_pool
        self.command_history = []  # Audit trail

    def execute_command(
        self,
        connection_id: str,
        command_type: str,
        command_payload: dict,
        priority: str = 'NORMAL',
        request_user_id: str = None
    ) -> Dict:
        """
        Execute command on device with safety checks

        Args:
            connection_id: Device connection ID
            command_type: Type of command
            command_payload: Command parameters
            priority: Execution priority
            request_user_id: User requesting command

        Returns:
            dict: Command execution result
        """

        command_id = str(uuid.uuid4())

        try:
            # Verify connection is active
            if connection_id not in self.connection_pool:
                raise ValueError("Connection not found or inactive")

            # Validate command
            self.validator.validate_command(
                command_type,
                command_payload,
                connection_id
            )

            # Check authorization
            self._check_authorization(request_user_id, command_type)

            # Log command for audit trail
            self._audit_log(
                command_id,
                connection_id,
                command_type,
                request_user_id,
                'INITIATED'
            )

            # Execute command
            connector = self.connection_pool[connection_id]['connector']
            result = connector.execute_command(
                command_type,
                command_payload,
                timeout=5  # seconds
            )

            # Log result
            self._audit_log(
                command_id,
                connection_id,
                command_type,
                request_user_id,
                'COMPLETED',
                result
            )

            return {
                'command_id': command_id,
                'status': 'COMPLETED',
                'command_type': command_type,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")

            self._audit_log(
                command_id,
                connection_id,
                command_type,
                request_user_id,
                'FAILED',
                {'error': str(e)}
            )

            return {
                'command_id': command_id,
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _check_authorization(
        self,
        user_id: str,
        command_type: str
    ) -> bool:
        """Check user authorization for command"""

        # Check role-based access control
        restricted_commands = {
            'MODE_CHANGE': ['CLINICIAN', 'PHYSICIAN'],
            'ALARM_CONFIG': ['TECHNICIAN', 'CLINICIAN', 'PHYSICIAN'],
            'DEVICE_RESET': ['BIOMEDICAL_ENGINEER'],
        }

        required_roles = restricted_commands.get(command_type, [])

        if required_roles:
            user_roles = self._get_user_roles(user_id)
            if not any(role in user_roles for role in required_roles):
                raise PermissionError(f"User not authorized for {command_type}")

        return True

    def _audit_log(
        self,
        command_id: str,
        connection_id: str,
        command_type: str,
        user_id: str,
        status: str,
        result: Optional[dict] = None
    ):
        """Log command execution for audit trail"""

        audit_entry = {
            'command_id': command_id,
            'connection_id': connection_id,
            'command_type': command_type,
            'user_id': user_id,
            'status': status,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.command_history.append(audit_entry)

        # Persist to audit database
        # self.audit_db.insert(audit_entry)
```

---

## 3. Data Format Specifications

### 3.1 Vital Signs Data Model

```python
@dataclass
class VitalSign:
    """Standard vital signs measurement"""
    measurement_type: str  # ECG, SpO2, NIBP, Temperature, etc.
    value: float
    unit: str  # mmHg, bpm, %, °C
    timestamp: datetime
    device_id: str
    quality_indicator: str  # EXCELLENT, GOOD, FAIR, POOR

    def to_fhir(self) -> dict:
        """Convert to FHIR Observation resource"""

        loinc_codes = {
            'ECG': '8867-4',
            'HEART_RATE': '8867-4',
            'SpO2': '2708-6',
            'NIBP_SYSTOLIC': '8480-6',
            'NIBP_DIASTOLIC': '8462-4',
            'TEMPERATURE': '8310-5',
        }

        return {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {
                'coding': [{
                    'system': 'http://loinc.org',
                    'code': loinc_codes.get(self.measurement_type),
                    'display': self.measurement_type
                }]
            },
            'effectiveDateTime': self.timestamp.isoformat(),
            'valueQuantity': {
                'value': self.value,
                'unit': self.unit
            },
            'device': {
                'reference': f'Device/{self.device_id}'
            }
        }

class VitalSignsAggregator:
    """Aggregates vital signs from multiple devices"""

    def __init__(self):
        self.buffer = []
        self.aggregation_interval = 60  # seconds

    def add_vital_sign(self, vital: VitalSign):
        """Add measurement to buffer"""
        self.buffer.append(vital)

    def get_latest_vitals(self, device_id: str = None) -> Dict:
        """Get latest vital signs"""

        # Filter by device if specified
        vitals = self.buffer
        if device_id:
            vitals = [v for v in vitals if v.device_id == device_id]

        # Group by measurement type
        latest = {}
        for vital in vitals:
            if vital.measurement_type not in latest or \
               vital.timestamp > latest[vital.measurement_type].timestamp:
                latest[vital.measurement_type] = vital

        return {
            'measurements': [asdict(v) for v in latest.values()],
            'timestamp': datetime.utcnow().isoformat()
        }
```

### 3.2 Waveform Data Streaming

```python
@dataclass
class WaveformData:
    """ECG/physiological waveform data"""
    waveform_type: str  # ECG, SpO2_Pleth, Respiration
    sampling_rate: int  # Hz
    samples: List[float]  # Raw waveform samples
    timestamp: datetime
    device_id: str
    lead_configuration: Optional[str] = None  # For ECG: I, II, III, etc.

    def to_hl7(self) -> str:
        """Convert to HL7 OBX segment"""

        # Serialize samples as base64 for transmission
        import base64
        import struct

        # Pack samples as 16-bit integers
        packed = struct.pack(f'>{len(self.samples)}h',
                            *[int(s) for s in self.samples])
        encoded = base64.b64encode(packed).decode('ascii')

        # HL7 OBX segment
        return (
            f"OBX|1|waveform|{self.waveform_type}||"
            f"^{self.sampling_rate}^{encoded}|"
            f"|||||{self.timestamp.isoformat()}"
        )

class WaveformStreamer:
    """Handles high-frequency waveform streaming"""

    def __init__(self, buffer_size: int = 10000):
        self.buffer = []
        self.buffer_size = buffer_size
        self.subscribers = []

    async def stream_waveform(
        self,
        connection_id: str,
        waveform_data: WaveformData,
        compression: str = 'none'  # none, gzip, deflate
    ):
        """
        Stream waveform data to subscribers

        Args:
            connection_id: Device connection ID
            waveform_data: Waveform measurement
            compression: Data compression method
        """

        # Add to buffer
        self.buffer.append(waveform_data)

        # Maintain buffer size
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

        # Compress if requested
        if compression == 'gzip':
            import gzip
            serialized = json.dumps(asdict(waveform_data)).encode()
            compressed = gzip.compress(serialized)
            data_to_send = compressed
        else:
            data_to_send = asdict(waveform_data)

        # Send to all subscribers
        for subscriber in self.subscribers:
            try:
                await subscriber(
                    connection_id,
                    data_to_send,
                    waveform_data.waveform_type
                )
            except Exception as e:
                logger.error(f"Failed to stream waveform: {str(e)}")
```

---

## 4. Error Handling & Reliability

### 4.1 Error Classification

```python
class DeviceErrorCode(Enum):
    """Standardized device error codes"""

    # Communication errors
    CONNECTION_LOST = "DEV_001"
    TIMEOUT = "DEV_002"
    PROTOCOL_ERROR = "DEV_003"

    # Device errors
    DEVICE_ERROR = "DEV_101"
    DEVICE_NOT_READY = "DEV_102"
    SENSOR_DISCONNECTED = "DEV_103"
    LOW_BATTERY = "DEV_104"

    # Data errors
    DATA_VALIDATION_FAILED = "DEV_201"
    CHECKSUM_ERROR = "DEV_202"
    DATA_OUT_OF_RANGE = "DEV_203"

    # Safety errors
    PATIENT_DISCONNECT = "DEV_301"
    CRITICAL_ALARM = "DEV_302"
    DEVICE_MALFUNCTION = "DEV_303"

class DeviceException(Exception):
    """Base exception for device operations"""

    def __init__(
        self,
        error_code: DeviceErrorCode,
        message: str,
        details: dict = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_response(self) -> dict:
        """Convert to API error response"""
        return {
            'error_code': self.error_code.value,
            'message': self.message,
            'details': self.details,
            'timestamp': datetime.utcnow().isoformat()
        }

class ConnectionRecoveryManager:
    """Manages automatic reconnection to devices"""

    def __init__(self, max_retries: int = 5, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.reconnection_tasks = {}

    async def handle_disconnection(
        self,
        connection_id: str,
        reason: str
    ):
        """
        Handle unexpected device disconnection with auto-recovery

        Args:
            connection_id: Device connection ID
            reason: Disconnection reason
        """

        logger.warning(
            f"Device disconnected: {connection_id}, reason: {reason}"
        )

        # Notify subscribers
        await self._notify_subscribers(
            connection_id,
            'disconnected',
            {'reason': reason}
        )

        # Attempt recovery
        if connection_id not in self.reconnection_tasks:
            task = asyncio.create_task(
                self._reconnect_with_backoff(connection_id)
            )
            self.reconnection_tasks[connection_id] = task

    async def _reconnect_with_backoff(self, connection_id: str):
        """Reconnect with exponential backoff"""

        for attempt in range(self.max_retries):
            wait_time = min(300, (2 ** attempt) * self.backoff_factor)

            logger.info(
                f"Reconnection attempt {attempt + 1}/{self.max_retries} "
                f"for {connection_id} in {wait_time}s"
            )

            await asyncio.sleep(wait_time)

            try:
                # Get device configuration
                device_config = self._get_device_config(connection_id)

                # Attempt reconnection
                result = await self._reconnect_device(
                    device_config['device_id'],
                    device_config['device_type'],
                    device_config['protocol']
                )

                if result['status'] == 'CONNECTED':
                    logger.info(f"Successfully reconnected: {connection_id}")
                    await self._notify_subscribers(
                        connection_id,
                        'reconnected',
                        {}
                    )
                    del self.reconnection_tasks[connection_id]
                    return

            except Exception as e:
                logger.error(
                    f"Reconnection attempt {attempt + 1} failed: {str(e)}"
                )

        logger.error(f"Failed to reconnect {connection_id} after {self.max_retries} attempts")
        await self._notify_subscribers(
            connection_id,
            'reconnection_failed',
            {'max_retries': self.max_retries}
        )
```

---

## 5. Security Implementation

### 5.1 TLS/Mutual Authentication

```python
import ssl
import certifi

class DeviceSecurityManager:
    """Manages secure device communications"""

    @staticmethod
    def create_ssl_context(
        client_cert_path: str,
        client_key_path: str,
        ca_cert_path: str = None
    ) -> ssl.SSLContext:
        """
        Create SSL context for mutual TLS authentication

        Args:
            client_cert_path: Path to client certificate (PEM)
            client_key_path: Path to client private key (PEM)
            ca_cert_path: Path to CA certificate bundle

        Returns:
            ssl.SSLContext: Configured SSL context
        """

        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=ca_cert_path or certifi.where()
        )

        # Load client certificate and key
        context.load_cert_chain(
            certfile=client_cert_path,
            keyfile=client_key_path
        )

        # Enforce TLS 1.2 minimum
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        # Disable weak ciphers
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL')

        return context

    @staticmethod
    def validate_device_certificate(
        cert_path: str,
        expected_cn: str
    ) -> bool:
        """
        Validate device certificate

        Args:
            cert_path: Path to device certificate
            expected_cn: Expected Common Name

        Returns:
            bool: True if certificate is valid
        """

        import OpenSSL
        from datetime import datetime

        with open(cert_path, 'rb') as f:
            cert_data = f.read()

        cert = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM,
            cert_data
        )

        # Check CN
        subject = cert.get_subject()
        if subject.CN != expected_cn:
            raise ValueError(f"Certificate CN mismatch: {subject.CN}")

        # Check expiry
        not_after = cert.gmtime_adj_notAfter(0)
        if datetime.utcnow() > datetime.strptime(
            not_after.decode(), '%b %d %H:%M:%S %Y %Z'
        ):
            raise ValueError("Certificate expired")

        return True
```

### 5.2 Device Authentication

```python
class DeviceAuthenticator:
    """Authenticates medical devices"""

    def __init__(self, device_registry: dict):
        self.device_registry = device_registry

    def authenticate_device(
        self,
        device_id: str,
        auth_method: str,
        credentials: dict
    ) -> bool:
        """
        Authenticate device using multiple methods

        Args:
            device_id: Device identifier
            auth_method: API_KEY | CERTIFICATE | HMAC | JWT
            credentials: Authentication credentials

        Returns:
            bool: True if authentication succeeds
        """

        device = self.device_registry.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        if auth_method == 'API_KEY':
            return self._verify_api_key(device, credentials)
        elif auth_method == 'CERTIFICATE':
            return self._verify_certificate(device, credentials)
        elif auth_method == 'HMAC':
            return self._verify_hmac(device, credentials)
        elif auth_method == 'JWT':
            return self._verify_jwt(device, credentials)
        else:
            raise ValueError(f"Unsupported auth method: {auth_method}")

    def _verify_api_key(self, device: dict, credentials: dict) -> bool:
        """Verify API key authentication"""

        import hmac
        import hashlib

        provided_key = credentials.get('api_key')
        stored_key_hash = device.get('api_key_hash')

        # Use constant-time comparison
        key_hash = hashlib.sha256(provided_key.encode()).hexdigest()

        return hmac.compare_digest(key_hash, stored_key_hash)

    def _verify_jwt(self, device: dict, credentials: dict) -> bool:
        """Verify JWT token"""

        import jwt

        token = credentials.get('token')
        secret = device.get('jwt_secret')

        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])

            # Verify device_id claim
            if payload.get('device_id') != device['device_id']:
                return False

            # Verify expiration
            if 'exp' in payload:
                from datetime import datetime
                if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                    return False

            return True

        except jwt.InvalidTokenError:
            return False
```

---

## 6. Monitoring & Alerting

### 6.1 Device Health Monitoring

```python
class DeviceHealthMonitor:
    """Monitors medical device health and status"""

    def __init__(self):
        self.device_states = {}  # connection_id -> health metrics
        self.thresholds = {
            'error_rate': 0.05,  # 5%
            'latency_ms': 1000,
            'battery_percent': 20,
            'memory_usage_percent': 85
        }

    async def monitor_device(
        self,
        connection_id: str,
        metrics: dict
    ):
        """
        Monitor device health metrics

        Args:
            connection_id: Device connection ID
            metrics: Health metrics from device
        """

        # Update state
        if connection_id not in self.device_states:
            self.device_states[connection_id] = {
                'metrics_history': [],
                'alerts': []
            }

        state = self.device_states[connection_id]
        state['metrics_history'].append({
            'metrics': metrics,
            'timestamp': datetime.utcnow()
        })

        # Keep history limited
        if len(state['metrics_history']) > 1000:
            state['metrics_history'].pop(0)

        # Check thresholds
        alerts = self._check_thresholds(connection_id, metrics)

        # Trigger alerts if needed
        for alert in alerts:
            await self._trigger_alert(alert)

    def _check_thresholds(
        self,
        connection_id: str,
        metrics: dict
    ) -> List[dict]:
        """Check if metrics exceed thresholds"""

        alerts = []

        # Error rate check
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'type': 'HIGH_ERROR_RATE',
                'connection_id': connection_id,
                'value': metrics['error_rate'],
                'threshold': self.thresholds['error_rate'],
                'severity': 'WARNING'
            })

        # Battery check
        if metrics.get('battery_percent', 100) < self.thresholds['battery_percent']:
            alerts.append({
                'type': 'LOW_BATTERY',
                'connection_id': connection_id,
                'value': metrics['battery_percent'],
                'threshold': self.thresholds['battery_percent'],
                'severity': 'CRITICAL'
            })

        # Memory check
        if metrics.get('memory_usage_percent', 0) > self.thresholds['memory_usage_percent']:
            alerts.append({
                'type': 'HIGH_MEMORY_USAGE',
                'connection_id': connection_id,
                'value': metrics['memory_usage_percent'],
                'threshold': self.thresholds['memory_usage_percent'],
                'severity': 'WARNING'
            })

        return alerts

    async def _trigger_alert(self, alert: dict):
        """Trigger alerting mechanism"""

        severity = alert['severity']
        alert_message = f"{alert['type']}: {alert['connection_id']}"

        if severity == 'CRITICAL':
            logger.critical(alert_message)
            # Send to alerting system (PagerDuty, etc.)
        elif severity == 'WARNING':
            logger.warning(alert_message)
```

---

## 7. Compliance & Standards

### 7.1 Required Standards Compliance

- **FDA 21 CFR Part 11**: Electronic records, electronic signatures
- **HIPAA**: Patient privacy and data security
- **HITECH Act**: Breach notification and penalties
- **FDA Software Validation**: IEC 62304
- **Medical Device Software Lifecycle**: IEC 62304
- **Cybersecurity**: AAMI/FDA Premarket Cybersecurity Guidance

### 7.2 Audit Logging

```python
class AuditLogger:
    """Maintains comprehensive audit logs for regulatory compliance"""

    def __init__(self, database):
        self.db = database

    def log_access(
        self,
        user_id: str,
        resource_id: str,
        action: str,
        timestamp: datetime = None
    ):
        """Log resource access"""

        if timestamp is None:
            timestamp = datetime.utcnow()

        self.db.insert('audit_logs', {
            'user_id': user_id,
            'resource_id': resource_id,
            'action': action,
            'timestamp': timestamp,
            'ip_address': self._get_client_ip(),
            'user_agent': self._get_user_agent()
        })

    def log_data_modification(
        self,
        user_id: str,
        record_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any
    ):
        """Log data changes"""

        self.db.insert('audit_logs_detailed', {
            'user_id': user_id,
            'record_id': record_id,
            'field_name': field_name,
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': datetime.utcnow()
        })
```

---

## References

- [FDA Software Validation Guidance](https://www.fda.gov/media/87081/download)
- [ASTM F2761 - Medical Device Interoperability](https://www.astm.org/)
- [IEEE 802.11 Wireless Security](https://standards.ieee.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Document Version:** 1.0
**Last Updated:** 2024-01-15
**Status:** Production Ready
**Classification:** Healthcare Technology Standards
