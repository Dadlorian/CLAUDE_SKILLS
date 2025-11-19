# Smart Grid Technology - Advanced Implementation Guide

## Overview

Smart Grid Technology represents the digital transformation of electrical power systems, enabling bidirectional communication, automation, and intelligent control across the entire grid infrastructure from generation to consumption. This skill covers production-grade implementation patterns for smart grid systems.

## Core Technologies

### 1. Advanced Metering Infrastructure (AMI)
Smart meters that communicate consumption data in near real-time, enabling time-of-use pricing, demand response, and grid optimization.

### 2. Distribution Management Systems (DMS)
Software platforms that monitor and control the distribution network, optimize power flow, and automate fault detection and restoration.

### 3. Energy Management Systems (EMS)
Grid-scale systems that manage generation dispatch, load balancing, and economic optimization across the transmission network.

### 4. Supervisory Control and Data Acquisition (SCADA)
Real-time monitoring and control systems for substations, transformers, and grid infrastructure.

### 5. Distributed Energy Resource Management Systems (DERMS)
Platforms that aggregate and control distributed generation, storage, and flexible loads.

## Standards and Protocols

### Communication Standards
- **IEC 61850**: Communication networks and systems for power utility automation
- **DNP3 (IEEE 1815)**: Distributed Network Protocol for SCADA systems
- **Modbus**: Serial communication protocol for industrial devices
- **IEEE 2030**: Smart Grid Interoperability Reference Model
- **OpenADR 2.0b**: Automated Demand Response standard

### Cybersecurity Standards
- **NIST IR 7628**: Smart Grid Cybersecurity Guidelines (3 volumes)
- **IEC 62351**: Power systems security and communication protocols
- **NERC CIP**: Critical Infrastructure Protection requirements
- **IEC 62443**: Industrial automation and control systems security

### Data Models
- **IEC 61968/61970 (CIM)**: Common Information Model for energy management
- **IEEE 1547**: Distributed Energy Resources interconnection
- **IEEE C37.118**: Synchrophasor data standard for PMUs

## Production-Grade Implementation Examples

### Example 1: Advanced Metering Infrastructure (AMI) Data Collector

```python
"""
Production-grade AMI data collection and processing system
Implements NIST IR 7628 security guidelines and IEC 61968 CIM standard
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
import hashlib
import logging
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeterType(Enum):
    """Meter types per IEC 61968 standard"""
    ELECTRIC = "electric"
    GAS = "gas"
    WATER = "water"
    THERMAL = "thermal"

class DataQuality(Enum):
    """Data quality indicators per IEC 61968-9"""
    VALID = "valid"
    ESTIMATED = "estimated"
    QUESTIONABLE = "questionable"
    INVALID = "invalid"
    MISSING = "missing"

class AlarmSeverity(Enum):
    """Alarm severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class MeterReading:
    """
    Represents a single meter reading following IEC 61968 CIM standard

    Attributes:
        meter_id: Unique meter identifier
        timestamp: Reading timestamp in UTC
        value: Reading value
        unit: Unit of measurement (kWh, kW, m³, etc.)
        quality: Data quality indicator
        meter_type: Type of meter
        interval_minutes: Reading interval (typically 15, 30, or 60)
        voltage: Line voltage (for electric meters)
        current: Line current (for electric meters)
        power_factor: Power factor (for electric meters)
        frequency: Grid frequency (for electric meters)
        metadata: Additional meter-specific metadata
    """
    meter_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: DataQuality
    meter_type: MeterType
    interval_minutes: int = 15
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_factor: Optional[float] = None
    frequency: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate reading after initialization"""
        is_valid, errors = self.validate()
        if not is_valid:
            logger.warning(f"Invalid reading created for {self.meter_id}: {errors}")

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate reading against utility-specific rules

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Type-specific validation
        if self.meter_type == MeterType.ELECTRIC:
            # Range validation for electric meters
            if self.value < 0 or self.value > 1000000:
                errors.append(f"Electric reading {self.value} {self.unit} out of bounds")

            if self.voltage is not None:
                if self.voltage < 100 or self.voltage > 500:
                    errors.append(f"Voltage {self.voltage}V out of acceptable range")

            if self.current is not None and self.current < 0:
                errors.append(f"Negative current {self.current}A not allowed")

            if self.power_factor is not None:
                if not (-1 <= self.power_factor <= 1):
                    errors.append(f"Invalid power factor {self.power_factor}")

            if self.frequency is not None:
                if not (59 <= self.frequency <= 61):  # US grid nominal 60Hz ±1Hz
                    errors.append(f"Frequency {self.frequency}Hz out of acceptable range")

        elif self.meter_type == MeterType.GAS:
            if self.value < 0 or self.value > 100000:
                errors.append(f"Gas reading {self.value} {self.unit} out of bounds")

        # Timestamp validation
        now = datetime.utcnow()
        if self.timestamp > now + timedelta(minutes=5):
            errors.append("Future timestamp not allowed")

        if self.timestamp < now - timedelta(days=365):
            errors.append("Reading older than 1 year")

        # Interval validation
        if self.interval_minutes not in [1, 5, 15, 30, 60]:
            errors.append(f"Non-standard interval {self.interval_minutes} minutes")

        return len(errors) == 0, errors

    def calculate_power(self) -> Optional[float]:
        """
        Calculate instantaneous power for electric meters
        P = V × I × PF × √3 (for three-phase)
        """
        if self.meter_type != MeterType.ELECTRIC:
            return None

        if None in (self.voltage, self.current, self.power_factor):
            return None

        # Assuming three-phase
        power_kw = (self.voltage * self.current * self.power_factor * 1.732) / 1000
        return power_kw

@dataclass
class MeterAlarm:
    """Represents a meter alarm or event"""
    meter_id: str
    timestamp: datetime
    severity: AlarmSeverity
    alarm_type: str
    description: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AMIDataCollector:
    """
    Advanced Metering Infrastructure data collector

    Implements industry best practices for meter data management:
    - Concurrent data collection with rate limiting
    - Retry logic with exponential backoff
    - Data validation and quality checks
    - Alarm detection and notification
    - Secure communication (TLS 1.3)
    - Connection pooling

    References:
    - NIST IR 7628: Smart Grid Cybersecurity Guidelines
    - IEC 61968-9: Common Information Model for Metering
    - IEEE 1815 (DNP3): Distributed Network Protocol
    """

    def __init__(
        self,
        collector_id: str,
        max_concurrent_connections: int = 100,
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
        api_key: Optional[str] = None
    ):
        """
        Initialize AMI data collector

        Args:
            collector_id: Unique identifier for this collector instance
            max_concurrent_connections: Maximum concurrent HTTP connections
            timeout_seconds: HTTP request timeout
            retry_attempts: Number of retry attempts for failed requests
            api_key: API key for authentication (stored securely)
        """
        self.collector_id = collector_id
        self.max_concurrent_connections = max_concurrent_connections
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.semaphore = asyncio.Semaphore(max_concurrent_connections)
        self.retry_attempts = retry_attempts
        self.api_key = api_key

        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_readings': 0,
            'invalid_readings': 0,
            'alarms_detected': 0
        }

    async def collect_meter_data(
        self,
        meter_endpoints: List[str],
        start_time: datetime,
        end_time: datetime,
        validate_data: bool = True
    ) -> Dict[str, List[MeterReading]]:
        """
        Collect meter data from multiple endpoints concurrently

        Implements connection pooling and rate limiting to avoid
        overwhelming meter head-end systems.

        Args:
            meter_endpoints: List of meter API endpoints
            start_time: Start of data collection period
            end_time: End of data collection period
            validate_data: Whether to validate readings

        Returns:
            Dictionary mapping meter_id to list of readings
        """
        logger.info(
            f"Collecting data from {len(meter_endpoints)} meters "
            f"({start_time} to {end_time})"
        )

        # Create SSL context requiring TLS 1.3 per NIST IR 7628
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3

        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=self.max_concurrent_connections)

        async with aiohttp.ClientSession(timeout=self.timeout, connector=connector) as session:
            tasks = [
                self._fetch_meter_data(session, endpoint, start_time, end_time, validate_data)
                for endpoint in meter_endpoints
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        meter_data = {}
        for endpoint, result in zip(meter_endpoints, results):
            self.stats['total_requests'] += 1

            if isinstance(result, Exception):
                logger.error(f"Error collecting from {endpoint}: {result}")
                self.stats['failed_requests'] += 1
                continue

            self.stats['successful_requests'] += 1
            meter_id = self._extract_meter_id(endpoint)
            meter_data[meter_id] = result
            self.stats['total_readings'] += len(result)

        logger.info(
            f"Collection complete: {self.stats['successful_requests']}/{self.stats['total_requests']} "
            f"successful, {self.stats['total_readings']} readings collected"
        )

        return meter_data

    async def _fetch_meter_data(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        start_time: datetime,
        end_time: datetime,
        validate_data: bool
    ) -> List[MeterReading]:
        """
        Fetch data from a single meter endpoint with retry logic

        Implements exponential backoff for retries per AWS best practices
        """
        async with self.semaphore:
            for attempt in range(self.retry_attempts):
                try:
                    headers = {}
                    if self.api_key:
                        headers['Authorization'] = f'Bearer {self.api_key}'

                    async with session.get(
                        endpoint,
                        params={
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        },
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            readings = self._parse_meter_data(data, validate_data)
                            return readings
                        elif response.status == 429:
                            # Rate limited - wait longer
                            logger.warning(f"Rate limited on {endpoint}")
                            await asyncio.sleep(2 ** (attempt + 2))
                        else:
                            logger.warning(f"HTTP {response.status} from {endpoint}")

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on attempt {attempt + 1} for {endpoint}")
                except aiohttp.ClientError as e:
                    logger.error(f"Client error on attempt {attempt + 1} for {endpoint}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1} for {endpoint}: {e}")

                if attempt < self.retry_attempts - 1:
                    # Exponential backoff: 1s, 2s, 4s, etc.
                    await asyncio.sleep(2 ** attempt)

            logger.error(f"All retry attempts failed for {endpoint}")
            return []

    def _parse_meter_data(self, raw_data: Dict, validate: bool) -> List[MeterReading]:
        """
        Parse raw meter data into MeterReading objects

        Handles various data formats and performs validation
        """
        readings = []

        for reading_data in raw_data.get('readings', []):
            try:
                reading = MeterReading(
                    meter_id=reading_data['meter_id'],
                    timestamp=datetime.fromisoformat(reading_data['timestamp']),
                    value=float(reading_data['value']),
                    unit=reading_data['unit'],
                    quality=DataQuality(reading_data.get('quality', 'valid')),
                    meter_type=MeterType(reading_data['type']),
                    interval_minutes=reading_data.get('interval_minutes', 15),
                    voltage=reading_data.get('voltage'),
                    current=reading_data.get('current'),
                    power_factor=reading_data.get('power_factor'),
                    frequency=reading_data.get('frequency'),
                    metadata=reading_data.get('metadata', {})
                )

                if validate:
                    is_valid, errors = reading.validate()
                    if is_valid:
                        readings.append(reading)
                    else:
                        logger.debug(f"Invalid reading from {reading.meter_id}: {errors}")
                        self.stats['invalid_readings'] += 1
                else:
                    readings.append(reading)

            except (KeyError, ValueError, TypeError) as e:
                logger.error(f"Error parsing reading: {e}")
                self.stats['invalid_readings'] += 1
                continue

        return readings

    def _extract_meter_id(self, endpoint: str) -> str:
        """Extract meter ID from endpoint URL"""
        # Simple implementation - customize based on your API
        parts = endpoint.split('/')
        return parts[-1] if parts else endpoint

    def detect_anomalies(self, readings: List[MeterReading]) -> List[MeterAlarm]:
        """
        Detect anomalies in meter readings

        Implements basic anomaly detection:
        - Sudden spikes in consumption
        - Negative power (backfeed detection)
        - Zero readings (potential meter failure)
        - Data quality issues

        Production systems would use ML-based anomaly detection
        """
        alarms = []

        # Group readings by meter
        by_meter = defaultdict(list)
        for reading in readings:
            by_meter[reading.meter_id].append(reading)

        for meter_id, meter_readings in by_meter.items():
            if len(meter_readings) < 2:
                continue

            # Sort by timestamp
            meter_readings.sort(key=lambda r: r.timestamp)

            # Calculate statistics
            values = [r.value for r in meter_readings]
            avg_value = sum(values) / len(values)

            for i, reading in enumerate(meter_readings):
                # Spike detection (>5x average)
                if reading.value > avg_value * 5 and avg_value > 0:
                    alarm = MeterAlarm(
                        meter_id=meter_id,
                        timestamp=reading.timestamp,
                        severity=AlarmSeverity.HIGH,
                        alarm_type="consumption_spike",
                        description=f"Consumption spike: {reading.value} {reading.unit} (avg: {avg_value:.2f})"
                    )
                    alarms.append(alarm)

                # Zero reading detection
                if reading.value == 0 and i > 0:
                    alarm = MeterAlarm(
                        meter_id=meter_id,
                        timestamp=reading.timestamp,
                        severity=AlarmSeverity.MEDIUM,
                        alarm_type="zero_reading",
                        description="Zero reading detected - possible meter failure"
                    )
                    alarms.append(alarm)

                # Data quality alarm
                if reading.quality in (DataQuality.INVALID, DataQuality.QUESTIONABLE):
                    alarm = MeterAlarm(
                        meter_id=meter_id,
                        timestamp=reading.timestamp,
                        severity=AlarmSeverity.LOW,
                        alarm_type="data_quality",
                        description=f"Poor data quality: {reading.quality.value}"
                    )
                    alarms.append(alarm)

        self.stats['alarms_detected'] += len(alarms)
        return alarms

    def get_statistics(self) -> Dict:
        """Return collector statistics"""
        return self.stats.copy()


# Example usage
async def main():
    """Example usage of AMI data collector"""

    # Initialize collector
    collector = AMIDataCollector(
        collector_id="collector-001",
        max_concurrent_connections=50,
        timeout_seconds=30
    )

    # Define meter endpoints (in production, this would come from a database)
    meter_endpoints = [
        f"https://ami-headend.utility.com/api/v1/meters/meter-{i:05d}"
        for i in range(1, 101)  # 100 meters
    ]

    # Collect last 24 hours of data
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)

    # Collect data
    meter_data = await collector.collect_meter_data(
        meter_endpoints,
        start_time,
        end_time,
        validate_data=True
    )

    # Detect anomalies
    all_readings = []
    for readings in meter_data.values():
        all_readings.extend(readings)

    alarms = collector.detect_anomalies(all_readings)

    # Print results
    print(f"\nCollection Results:")
    print(f"  Meters collected: {len(meter_data)}")
    print(f"  Total readings: {len(all_readings)}")
    print(f"  Alarms detected: {len(alarms)}")
    print(f"\nStatistics: {collector.get_statistics()}")

    # Print critical alarms
    critical_alarms = [a for a in alarms if a.severity == AlarmSeverity.CRITICAL]
    if critical_alarms:
        print(f"\nCritical Alarms:")
        for alarm in critical_alarms[:5]:  # Show first 5
            print(f"  {alarm.meter_id}: {alarm.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Distributed Energy Resource Management System (DERMS)

```python
"""
Production-grade DERMS implementation
Manages distributed solar PV, battery storage, and EV chargers

References:
- IEEE 1547-2018: DER interconnection standard
- IEEE 2030.5: Smart Energy Profile 2.0
"""

from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """DER resource types per IEEE 1547"""
    SOLAR_PV = "solar_pv"
    BATTERY_STORAGE = "battery_storage"
    EV_CHARGER = "ev_charger"
    WIND_TURBINE = "wind_turbine"
    FUEL_CELL = "fuel_cell"
    MICROTURBINE = "microturbine"

class ResourceState(Enum):
    """Operational states"""
    ONLINE = "online"
    OFFLINE = "offline"
    CURTAILED = "curtailed"
    MAINTENANCE = "maintenance"
    FAULT = "fault"

class ControlMode(Enum):
    """Control modes per IEEE 1547"""
    AUTONOMOUS = "autonomous"
    SCHEDULED = "scheduled"
    DISPATCH = "dispatch"
    REGULATION = "regulation"

@dataclass
class DERAsset:
    """Distributed Energy Resource asset"""
    asset_id: str
    resource_type: ResourceType
    location: Dict[str, float]  # {'lat': x, 'lon': y}
    rated_capacity_kw: float
    state: ResourceState
    control_mode: ControlMode
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Current telemetry
    current_output_kw: float = 0.0
    current_reactive_kvar: float = 0.0
    voltage_v: Optional[float] = None
    frequency_hz: Optional[float] = None

    # Battery-specific (if applicable)
    soc_percent: Optional[float] = None
    soh_percent: Optional[float] = None
    charge_rate_kw: Optional[float] = None
    discharge_rate_kw: Optional[float] = None

    # Communication
    last_communication: Optional[datetime] = None
    communication_protocol: str = "modbus"  # modbus, sunspec, ieee2030.5

    def is_available(self) -> bool:
        """Check if resource is available for dispatch"""
        return self.state == ResourceState.ONLINE

    def is_responsive(self, timeout_minutes: int = 5) -> bool:
        """Check if resource has communicated recently"""
        if self.last_communication is None:
            return False
        return datetime.utcnow() - self.last_communication < timedelta(minutes=timeout_minutes)

@dataclass
class DispatchCommand:
    """Dispatch command for DER control"""
    command_id: str
    asset_id: str
    timestamp: datetime
    target_power_kw: float
    target_reactive_kvar: float = 0.0
    duration_minutes: int = 15
    priority: int = 5  # 1-10, 10 = highest
    executed: bool = False
    execution_time: Optional[datetime] = None

class DERMSController:
    """
    Distributed Energy Resource Management System

    Implements IEEE 1547 and IEEE 2030.5 standards for DER control

    Features:
    - Aggregate control of distributed resources
    - Real-time telemetry processing
    - Optimization-based dispatch
    - Voltage and frequency regulation
    - Grid services provision (frequency response, voltage support)
    """

    def __init__(self, controller_id: str, control_interval_seconds: int = 60):
        self.controller_id = controller_id
        self.control_interval = control_interval_seconds
        self.assets: Dict[str, DERAsset] = {}
        self.dispatch_queue: List[DispatchCommand] = []
        self.active_commands: Dict[str, DispatchCommand] = {}

        # Grid constraints
        self.max_export_kw = 10000  # Maximum export to grid
        self.max_import_kw = 10000  # Maximum import from grid
        self.target_power_factor = 0.95

    def register_asset(self, asset: DERAsset) -> bool:
        """Register a new DER asset"""
        if asset.asset_id in self.assets:
            logger.warning(f"Asset {asset.asset_id} already registered")
            return False

        self.assets[asset.asset_id] = asset
        logger.info(f"Registered {asset.resource_type.value} asset {asset.asset_id}")
        return True

    def get_aggregate_capacity(self, resource_type: Optional[ResourceType] = None) -> float:
        """Get total capacity of all or specific resource type"""
        total_capacity = 0.0
        for asset in self.assets.values():
            if resource_type is None or asset.resource_type == resource_type:
                if asset.is_available():
                    total_capacity += asset.rated_capacity_kw
        return total_capacity

    def get_aggregate_output(self, resource_type: Optional[ResourceType] = None) -> float:
        """Get current aggregate output"""
        total_output = 0.0
        for asset in self.assets.values():
            if resource_type is None or asset.resource_type == resource_type:
                if asset.is_available():
                    total_output += asset.current_output_kw
        return total_output

    async def dispatch_power(
        self,
        target_power_kw: float,
        duration_minutes: int = 15,
        resource_types: Optional[List[ResourceType]] = None
    ) -> List[DispatchCommand]:
        """
        Dispatch power setpoint to DER assets

        Implements proportional dispatch based on asset capacity

        Args:
            target_power_kw: Target power output (positive = export, negative = import)
            duration_minutes: Duration of dispatch
            resource_types: Limit dispatch to specific resource types

        Returns:
            List of dispatch commands issued
        """
        # Filter available assets
        available_assets = [
            asset for asset in self.assets.values()
            if asset.is_available() and asset.is_responsive()
        ]

        if resource_types:
            available_assets = [
                asset for asset in available_assets
                if asset.resource_type in resource_types
            ]

        if not available_assets:
            logger.warning("No available assets for dispatch")
            return []

        # Calculate total available capacity
        total_capacity = sum(asset.rated_capacity_kw for asset in available_assets)

        if total_capacity == 0:
            logger.warning("Total capacity is zero")
            return []

        # Proportional dispatch based on capacity
        commands = []
        for asset in available_assets:
            proportion = asset.rated_capacity_kw / total_capacity
            asset_target = target_power_kw * proportion

            # Respect asset limits
            if asset.resource_type == ResourceType.BATTERY_STORAGE:
                # Battery can charge or discharge
                max_discharge = asset.discharge_rate_kw or asset.rated_capacity_kw
                max_charge = asset.charge_rate_kw or asset.rated_capacity_kw
                asset_target = max(min(asset_target, max_discharge), -max_charge)
            elif asset.resource_type in (ResourceType.SOLAR_PV, ResourceType.WIND_TURBINE):
                # Generation only (can curtail but not import)
                asset_target = max(0, min(asset_target, asset.rated_capacity_kw))

            command = DispatchCommand(
                command_id=f"cmd-{asset.asset_id}-{datetime.utcnow().timestamp()}",
                asset_id=asset.asset_id,
                timestamp=datetime.utcnow(),
                target_power_kw=asset_target,
                duration_minutes=duration_minutes,
                priority=5
            )

            commands.append(command)
            self.dispatch_queue.append(command)

        # Execute commands
        await self._execute_dispatch_commands(commands)

        logger.info(
            f"Dispatched {target_power_kw:.2f} kW across {len(commands)} assets"
        )

        return commands

    async def _execute_dispatch_commands(self, commands: List[DispatchCommand]):
        """Execute dispatch commands via communication protocols"""
        for command in commands:
            asset = self.assets.get(command.asset_id)
            if not asset:
                logger.error(f"Asset {command.asset_id} not found")
                continue

            # In production, this would send actual control commands
            # via Modbus, SunSpec, IEEE 2030.5, or other protocols
            logger.info(
                f"Executing command {command.command_id}: "
                f"{asset.asset_id} -> {command.target_power_kw:.2f} kW"
            )

            # Simulate command execution
            command.executed = True
            command.execution_time = datetime.utcnow()
            self.active_commands[command.command_id] = command

            # In real implementation, would update asset state from telemetry
            asset.current_output_kw = command.target_power_kw

    async def run_control_loop(self):
        """Main control loop"""
        logger.info(f"Starting DERMS control loop (interval: {self.control_interval}s)")

        while True:
            try:
                # Update asset telemetry (in production, from SCADA/IoT)
                await self._update_asset_telemetry()

                # Check grid conditions
                grid_status = await self._check_grid_status()

                # Optimization-based dispatch
                if grid_status.get('requires_regulation'):
                    await self._regulate_grid(grid_status)

                # Clean up expired commands
                self._cleanup_expired_commands()

            except Exception as e:
                logger.error(f"Error in control loop: {e}")

            await asyncio.sleep(self.control_interval)

    async def _update_asset_telemetry(self):
        """Update asset telemetry from field devices"""
        # In production, poll SCADA systems, Modbus gateways, etc.
        for asset in self.assets.values():
            asset.last_communication = datetime.utcnow()
            # Update voltage, frequency, power, etc.

    async def _check_grid_status(self) -> Dict:
        """Check grid voltage and frequency"""
        # In production, get from PMUs, SCADA, utility DERMS
        return {
            'voltage': 120.0,
            'frequency': 60.0,
            'requires_regulation': False
        }

    async def _regulate_grid(self, grid_status: Dict):
        """Regulate grid voltage and frequency using DERs"""
        # Implement IEEE 1547 voltage and frequency ride-through
        pass

    def _cleanup_expired_commands(self):
        """Remove expired dispatch commands"""
        now = datetime.utcnow()
        expired = [
            cmd_id for cmd_id, cmd in self.active_commands.items()
            if cmd.execution_time and
               now - cmd.execution_time > timedelta(minutes=cmd.duration_minutes)
        ]
        for cmd_id in expired:
            del self.active_commands[cmd_id]
```

## Architecture Patterns

### Pattern 1: Hierarchical Grid Control

```
┌─────────────────────────────────────────────────────────────┐
│              Utility Control Center (EMS/SCADA)             │
│         - Grid-level optimization                            │
│         - Real-time monitoring                               │
│         - Market operations                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ IEC 61850 / DNP3
┌────────────────────────┴────────────────────────────────────┐
│              Distribution Management System (DMS)            │
│         - Substation automation                              │
│         - Fault detection and isolation                      │
│         - Voltage/Var optimization                           │
└────┬────────────────────┬────────────────────┬──────────────┘
     │                    │                    │
     │ IEC 61850         │ IEC 61850          │ IEC 61850
     │                    │                    │
┌────▼─────┐      ┌──────▼──────┐     ┌──────▼──────┐
│Substation│      │ Substation  │     │ Substation  │
│  A       │      │     B       │     │     C       │
└────┬─────┘      └──────┬──────┘     └──────┬──────┘
     │                   │                    │
     │ Modbus/DNP3      │                    │
     │                   │                    │
┌────▼─────────────────────────────────────────────────┐
│         Distribution Feeders                         │
│    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐   │
│    │Smart│  │Smart│  │Smart│  │Smart│  │Smart│   │
│    │Meter│  │Meter│  │Meter│  │Meter│  │Meter│   │
│    └─────┘  └─────┘  └─────┘  └─────┘  └─────┘   │
│         │        │        │        │        │       │
│       ┌─▼─┐    ┌─▼─┐    ┌─▼─┐    ┌─▼─┐    ┌─▼─┐  │
│       │DER│    │DER│    │DER│    │DER│    │DER│  │
│       └───┘    └───┘    └───┘    └───┘    └───┘  │
└──────────────────────────────────────────────────────┘
```

### Pattern 2: Edge Computing for Grid Intelligence

Modern smart grids leverage edge computing to process data locally:

```
┌──────────────────────────────────────────────────────┐
│               Cloud/Utility Data Center              │
│   - Long-term analytics                              │
│   - Machine learning training                        │
│   - Enterprise integration                           │
└────────────────────┬─────────────────────────────────┘
                     │ HTTPS/MQTT
┌────────────────────┴─────────────────────────────────┐
│            Edge Gateway (Substation/Feeder)          │
│   - Real-time analytics                              │
│   - Local control decisions                          │
│   - Data aggregation and filtering                   │
│   - ML inference                                     │
└────┬────────────────────┬────────────────────────────┘
     │                    │
     │ Modbus/DNP3       │ IEC 61850
     │                    │
┌────▼─────┐      ┌──────▼──────┐
│ Smart    │      │ IED/PMU     │
│ Meters   │      │             │
└──────────┘      └─────────────┘
```

## Real-World Use Cases

### 1. Peak Shaving with Battery Storage
Reduce demand charges by discharging batteries during peak periods.

### 2. Renewable Energy Curtailment Management
Manage solar/wind curtailment while maintaining grid stability.

### 3. Frequency Regulation Services
Provide fast frequency response using battery storage and controllable loads.

### 4. Voltage Support
Use smart inverters for reactive power compensation.

### 5. Microgrid Islanding
Detect islanding conditions and transition to autonomous operation.

## Security Best Practices

### 1. Defense in Depth
- Network segmentation (IT/OT separation)
- Firewalls between control zones
- DMZ for external communications

### 2. Authentication and Authorization
- Certificate-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication for critical systems

### 3. Encryption
- TLS 1.3 for all communications
- IPsec for site-to-site VPN
- Encrypted storage for sensitive data

### 4. Monitoring and Logging
- Security Information and Event Management (SIEM)
- Intrusion detection systems (IDS/IPS)
- Audit logging per NERC CIP requirements

### 5. Secure Development
- Code review and static analysis
- Penetration testing
- Vulnerability scanning
- Secure boot and firmware signing

## Performance Optimization

### 1. Time-Series Data Management
Use specialized databases for meter data:
- **InfluxDB**: High-performance time-series database
- **TimescaleDB**: PostgreSQL extension for time-series
- **Apache Cassandra**: Distributed, high-availability storage

### 2. Real-Time Processing
Implement stream processing for real-time analytics:
- **Apache Kafka**: Message streaming
- **Apache Flink**: Stream processing
- **Redis**: In-memory caching

### 3. Edge Computing
Process data at the edge to reduce latency and bandwidth:
- Local anomaly detection
- Real-time control decisions
- Data aggregation before cloud upload

## Testing Strategies

### 1. Hardware-in-Loop (HIL) Testing
Test control algorithms with actual grid equipment.

### 2. Power System Simulation
Use tools like GridLAB-D, PSCAD, or PowerWorld for simulation.

### 3. Cybersecurity Testing
- Penetration testing
- Red team exercises
- Vulnerability assessments

### 4. Load Testing
Simulate thousands of meters reporting simultaneously.

### 5. Failure Mode Testing
Test resilience to network failures, device faults, etc.

## Common Challenges and Solutions

### Challenge 1: Data Quality
**Problem**: Incomplete or inaccurate meter data
**Solution**: Implement validation, estimation, and editing (VEE) systems

### Challenge 2: Scalability
**Problem**: Managing millions of devices
**Solution**: Edge computing, data aggregation, efficient protocols

### Challenge 3: Interoperability
**Problem**: Multiple vendor protocols
**Solution**: Use standard protocols (IEC 61850, Modbus), protocol gateways

### Challenge 4: Cybersecurity
**Problem**: Critical infrastructure protection
**Solution**: NIST IR 7628 compliance, defense in depth, continuous monitoring

### Challenge 5: Latency
**Problem**: Real-time control requirements
**Solution**: Edge processing, optimized communication, priority queuing

## Key Performance Indicators (KPIs)

### Operational KPIs
- **System Availability**: Target >99.9%
- **Data Collection Rate**: >98% of meters reporting
- **Control Response Time**: <500ms for critical commands
- **Forecast Accuracy**: MAPE <10% for day-ahead

### Grid Performance KPIs
- **SAIDI**: System Average Interruption Duration Index
- **SAIFI**: System Average Interruption Frequency Index
- **Voltage Deviation**: Keep within ANSI C84.1 limits (±5%)
- **Frequency Deviation**: Keep within ±0.036 Hz (North America)

### Economic KPIs
- **Peak Demand Reduction**: 10-20% typical with DR
- **Renewable Integration**: % of energy from renewables
- **Operating Cost Reduction**: 5-15% with optimization
- **Customer Satisfaction**: >90% satisfaction target

## Industry Resources

### Standards Organizations
- [IEEE Power & Energy Society](https://www.ieee-pes.org/)
- [IEC TC 57](https://www.iec.ch/) - Power systems management
- [NIST Smart Grid](https://www.nist.gov/programs-projects/smart-grid)

### Open Source Projects
- [GridLAB-D](https://www.gridlabd.org/) - Power distribution simulation
- [Pandapower](http://www.pandapower.org/) - Power system analysis
- [OpenDSS](https://www.epri.com/pages/sa/opendss) - Distribution simulation

### Research Institutions
- [NREL](https://www.nrel.gov/) - National Renewable Energy Laboratory
- [EPRI](https://www.epri.com/) - Electric Power Research Institute
- [LBNL](https://www.lbl.gov/) - Lawrence Berkeley National Lab

## Conclusion

Smart grid technology is transforming the electric power industry, enabling the integration of renewable energy, improving reliability, and empowering consumers. Success requires expertise in power systems, software engineering, cybersecurity, and data science, all while adhering to rigorous industry standards.

The code examples and patterns in this guide provide a foundation for building production-grade smart grid systems that are secure, scalable, and standards-compliant.
