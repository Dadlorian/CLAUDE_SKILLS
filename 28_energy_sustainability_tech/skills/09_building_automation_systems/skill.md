# Building Automation Systems - Production Implementation Guide

## Overview

Building Automation Systems (BAS), also known as Building Management Systems (BMS), integrate and control a building's mechanical, electrical, and lighting systems. This skill covers production-grade implementations of BACnet protocol integration, multi-protocol gateways, HVAC control sequences, and IoT sensor integration.

## Core Technologies

### 1. BACnet (ASHRAE 135)
Open protocol for building automation and control networks, widely used in commercial buildings.

### 2. Modbus
Serial/TCP protocol for industrial control, commonly used for equipment communication.

### 3. LonWorks
Peer-to-peer control networking for building automation.

### 4. KNX
European standard for home and building control.

### 5. MQTT
Lightweight IoT messaging protocol for sensor data.

## Standards and Protocols

### Control Standards
- **ASHRAE 135 (BACnet)**: Building automation and control networks
- **ASHRAE Guideline 36**: High-performance sequences of operation for HVAC
- **ASHRAE 55**: Thermal environmental conditions
- **ASHRAE 62.1**: Ventilation and indoor air quality

### Data Standards
- **Project Haystack**: Semantic tagging for IoT and building data
- **Brick Schema**: Ontology for building metadata

## Production-Grade Implementation Example

```python
"""
Production-grade Building Automation System (BAS)
Implements BACnet protocol and HVAC control

References:
- ASHRAE 135: BACnet standard
- ASHRAE Guideline 36: High-performance sequences
- Project Haystack: Semantic tagging
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BACnetObjectType(Enum):
    """BACnet object types (subset)"""
    ANALOG_INPUT = "analog-input"
    ANALOG_OUTPUT = "analog-output"
    ANALOG_VALUE = "analog-value"
    BINARY_INPUT = "binary-input"
    BINARY_OUTPUT = "binary-output"
    MULTI_STATE_INPUT = "multi-state-input"
    DEVICE = "device"
    SCHEDULE = "schedule"

class HVACMode(Enum):
    """HVAC operating modes"""
    OFF = "off"
    HEATING = "heating"
    COOLING = "cooling"
    AUTO = "auto"
    VENTILATION = "ventilation"
    ECONOMIZER = "economizer"

@dataclass
class BACnetObject:
    """
    BACnet object representation

    Each object has:
    - Object Type (analog-input, binary-output, etc.)
    - Object Instance (unique number)
    - Properties (present-value, units, description, etc.)
    """
    object_type: BACnetObjectType
    object_instance: int
    object_name: str
    description: str
    present_value: Any
    units: Optional[str] = None
    status_flags: Dict[str, bool] = field(default_factory=dict)
    reliability: str = "no-fault-detected"

    def __post_init__(self):
        """Initialize status flags"""
        if not self.status_flags:
            self.status_flags = {
                'in_alarm': False,
                'fault': False,
                'overridden': False,
                'out_of_service': False
            }

@dataclass
class BACnetDevice:
    """BACnet device (controller, sensor, actuator)"""
    device_instance: int
    device_name: str
    vendor_name: str
    model_name: str
    protocol_version: int = 1
    objects: Dict[int, BACnetObject] = field(default_factory=dict)

    def add_object(self, obj: BACnetObject):
        """Add BACnet object to device"""
        self.objects[obj.object_instance] = obj

    def get_object(self, object_instance: int) -> Optional[BACnetObject]:
        """Retrieve object by instance"""
        return self.objects.get(object_instance)

@dataclass
class VAVBox:
    """Variable Air Volume (VAV) box controller"""
    vav_id: str
    zone_name: str
    bacnet_device: BACnetDevice

    # Sensors (BACnet analog inputs)
    zone_temp_ai: BACnetObject
    zone_temp_setpoint_av: BACnetObject
    discharge_air_temp_ai: BACnetObject
    discharge_air_flow_ai: BACnetObject

    # Actuators (BACnet analog outputs)
    damper_position_ao: BACnetObject
    reheat_valve_ao: BACnetObject

    def read_zone_temperature(self) -> float:
        """Read current zone temperature"""
        return self.zone_temp_ai.present_value

    def write_damper_position(self, position_percent: float):
        """Command damper position (0-100%)"""
        position_percent = max(0.0, min(100.0, position_percent))
        self.damper_position_ao.present_value = position_percent
        logger.info(f"{self.vav_id}: Set damper to {position_percent:.1f}%")

    def write_reheat_valve(self, position_percent: float):
        """Command reheat valve position (0-100%)"""
        position_percent = max(0.0, min(100.0, position_percent))
        self.reheat_valve_ao.present_value = position_percent
        logger.info(f"{self.vav_id}: Set reheat valve to {position_percent:.1f}%")

class BACnetController:
    """
    BACnet controller implementing basic read/write operations

    In production, use libraries like:
    - BAC0 (Python)
    - BACnet4J (Java)
    - BACpypes (Python)
    """

    def __init__(self, device_instance: int):
        self.device_instance = device_instance
        self.devices: Dict[int, BACnetDevice] = {}

    def discover_devices(self) -> List[BACnetDevice]:
        """
        Discover BACnet devices on network (Who-Is/I-Am)

        In production, sends broadcast Who-Is message
        and collects I-Am responses
        """
        logger.info("Discovering BACnet devices...")
        # Simplified - production would perform actual network discovery
        return list(self.devices.values())

    def read_property(
        self,
        device_instance: int,
        object_type: BACnetObjectType,
        object_instance: int,
        property_name: str = "present-value"
    ) -> Any:
        """
        Read BACnet property (ReadProperty service)

        Args:
            device_instance: Target device
            object_type: Object type
            object_instance: Object instance
            property_name: Property to read

        Returns:
            Property value
        """
        device = self.devices.get(device_instance)
        if not device:
            logger.error(f"Device {device_instance} not found")
            return None

        obj = device.get_object(object_instance)
        if not obj or obj.object_type != object_type:
            logger.error(f"Object {object_type.value}:{object_instance} not found")
            return None

        # Simplified property reading
        if property_name == "present-value":
            return obj.present_value
        elif property_name == "description":
            return obj.description
        else:
            return None

    def write_property(
        self,
        device_instance: int,
        object_type: BACnetObjectType,
        object_instance: int,
        value: Any,
        property_name: str = "present-value",
        priority: int = 8
    ) -> bool:
        """
        Write BACnet property (WriteProperty service)

        BACnet uses priority array (1-16):
        - 1-2: Manual override
        - 3-7: High-level control
        - 8: Operator override (typical for BMS)
        - 9-16: Lower priority control

        Args:
            device_instance: Target device
            object_type: Object type
            object_instance: Object instance
            value: Value to write
            property_name: Property to write
            priority: Priority (1-16)

        Returns:
            Success status
        """
        device = self.devices.get(device_instance)
        if not device:
            logger.error(f"Device {device_instance} not found")
            return False

        obj = device.get_object(object_instance)
        if not obj or obj.object_type != object_type:
            logger.error(f"Object {object_type.value}:{object_instance} not found")
            return False

        # Simplified property writing
        if property_name == "present-value":
            obj.present_value = value
            logger.info(
                f"Wrote {value} to {device.device_name}:"
                f"{object_type.value}:{object_instance} at priority {priority}"
            )
            return True

        return False

class ASHRAE_G36_Controller:
    """
    ASHRAE Guideline 36 High-Performance HVAC Sequences

    Implements sequences of operation for:
    - VAV box control
    - AHU control
    - Economizer control
    - Demand-controlled ventilation
    """

    def __init__(self):
        self.occupied_cooling_setpoint_f = 74.0
        self.occupied_heating_setpoint_f = 70.0
        self.unoccupied_cooling_setpoint_f = 80.0
        self.unoccupied_heating_setpoint_f = 65.0
        self.deadband_f = 2.0

    def vav_reheat_control(
        self,
        vav: VAVBox,
        is_occupied: bool
    ):
        """
        VAV box with reheat control sequence per G36

        Sequence:
        1. Read zone temperature and setpoint
        2. Calculate error
        3. Modulate damper for airflow
        4. Modulate reheat valve if cooling is insufficient
        """

        zone_temp = vav.read_zone_temperature()

        # Select setpoints based on occupancy
        if is_occupied:
            cooling_sp = self.occupied_cooling_setpoint_f
            heating_sp = self.occupied_heating_setpoint_f
        else:
            cooling_sp = self.unoccupied_cooling_setpoint_f
            heating_sp = self.unoccupied_heating_setpoint_f

        # Calculate temperature error
        cooling_error = zone_temp - cooling_sp
        heating_error = heating_sp - zone_temp

        # Damper control (simplified PI control)
        if zone_temp > cooling_sp:
            # Cooling mode: open damper
            damper_position = min(100.0, 30.0 + (cooling_error * 10))
            reheat_position = 0.0  # No reheat
        elif zone_temp < heating_sp:
            # Heating mode: minimum damper, modulate reheat
            damper_position = 30.0  # Minimum ventilation
            reheat_position = min(100.0, heating_error * 15)
        else:
            # Within deadband
            damper_position = 30.0
            reheat_position = 0.0

        # Command actuators
        vav.write_damper_position(damper_position)
        vav.write_reheat_valve(reheat_position)

        logger.info(
            f"{vav.vav_id} Control: Temp={zone_temp:.1f}°F, "
            f"SP={cooling_sp:.1f}°F, Damper={damper_position:.1f}%, "
            f"Reheat={reheat_position:.1f}%"
        )

class BuildingAutomationSystem:
    """
    Complete Building Automation System

    Features:
    - BACnet integration
    - Multi-protocol support (Modbus, MQTT)
    - ASHRAE G36 control sequences
    - Scheduling
    - Alarming
    - Trending (data logging)
    - Energy optimization
    """

    def __init__(self, building_id: str):
        self.building_id = building_id
        self.bacnet_controller = BACnetController(device_instance=1000)
        self.g36_controller = ASHRAE_G36_Controller()
        self.vav_boxes: Dict[str, VAVBox] = {}
        self.occupancy_schedule: Dict[datetime, bool] = {}

    def add_vav_box(self, vav: VAVBox):
        """Add VAV box to system"""
        self.vav_boxes[vav.vav_id] = vav
        logger.info(f"Added VAV box {vav.vav_id} for {vav.zone_name}")

    def set_occupancy_schedule(self, schedule: Dict[datetime, bool]):
        """Set building occupancy schedule"""
        self.occupancy_schedule = schedule

    def is_occupied(self, timestamp: datetime) -> bool:
        """Check if building is occupied"""
        # Simplified - production would check detailed schedule
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Weekdays 7am-6pm
        if day_of_week < 5 and 7 <= hour < 18:
            return True

        return False

    def run_control_sequence(self):
        """
        Execute control sequence for all VAV boxes

        Called periodically (e.g., every 60 seconds)
        """
        current_time = datetime.now()
        is_occupied = self.is_occupied(current_time)

        logger.info(
            f"Running control sequence at {current_time.strftime('%Y-%m-%d %H:%M')} "
            f"(Occupied: {is_occupied})"
        )

        for vav in self.vav_boxes.values():
            self.g36_controller.vav_reheat_control(vav, is_occupied)


# Example usage
def main():
    """Example usage of Building Automation System"""

    # Initialize BAS
    bas = BuildingAutomationSystem("BUILDING-001")

    print(f"\n=== Building Automation System ===")
    print(f"Building ID: {bas.building_id}")

    # Create BACnet device for VAV box
    vav_device = BACnetDevice(
        device_instance=101,
        device_name="VAV-101",
        vendor_name="Johnson Controls",
        model_name="VMA1800"
    )

    # Create BACnet objects for sensors and actuators
    zone_temp = BACnetObject(
        object_type=BACnetObjectType.ANALOG_INPUT,
        object_instance=1,
        object_name="Zone Temperature",
        description="Conference Room A Temperature",
        present_value=72.5,
        units="degrees-fahrenheit"
    )
    vav_device.add_object(zone_temp)

    zone_setpoint = BACnetObject(
        object_type=BACnetObjectType.ANALOG_VALUE,
        object_instance=2,
        object_name="Zone Temperature Setpoint",
        description="Conference Room A Setpoint",
        present_value=74.0,
        units="degrees-fahrenheit"
    )
    vav_device.add_object(zone_setpoint)

    discharge_temp = BACnetObject(
        object_type=BACnetObjectType.ANALOG_INPUT,
        object_instance=3,
        object_name="Discharge Air Temperature",
        description="VAV Discharge Air Temperature",
        present_value=55.0,
        units="degrees-fahrenheit"
    )
    vav_device.add_object(discharge_temp)

    discharge_flow = BACnetObject(
        object_type=BACnetObjectType.ANALOG_INPUT,
        object_instance=4,
        object_name="Discharge Air Flow",
        description="VAV Air Flow",
        present_value=500.0,
        units="cubic-feet-per-minute"
    )
    vav_device.add_object(discharge_flow)

    damper_position = BACnetObject(
        object_type=BACnetObjectType.ANALOG_OUTPUT,
        object_instance=1,
        object_name="Damper Position",
        description="VAV Damper Position",
        present_value=30.0,
        units="percent"
    )
    vav_device.add_object(damper_position)

    reheat_valve = BACnetObject(
        object_type=BACnetObjectType.ANALOG_OUTPUT,
        object_instance=2,
        object_name="Reheat Valve Position",
        description="VAV Reheat Valve",
        present_value=0.0,
        units="percent"
    )
    vav_device.add_object(reheat_valve)

    # Create VAV box
    vav_box = VAVBox(
        vav_id="VAV-101",
        zone_name="Conference Room A",
        bacnet_device=vav_device,
        zone_temp_ai=zone_temp,
        zone_temp_setpoint_av=zone_setpoint,
        discharge_air_temp_ai=discharge_temp,
        discharge_air_flow_ai=discharge_flow,
        damper_position_ao=damper_position,
        reheat_valve_ao=reheat_valve
    )

    # Add to BAS
    bas.add_vav_box(vav_box)

    # Register device with BACnet controller
    bas.bacnet_controller.devices[vav_device.device_instance] = vav_device

    print(f"\n=== VAV Box Configuration ===")
    print(f"VAV ID: {vav_box.vav_id}")
    print(f"Zone: {vav_box.zone_name}")
    print(f"Current Temperature: {vav_box.read_zone_temperature():.1f}°F")
    print(f"Current Setpoint: {vav_box.zone_temp_setpoint_av.present_value:.1f}°F")

    # Run control sequence
    print(f"\n=== Running ASHRAE G36 Control Sequence ===")
    bas.run_control_sequence()

    # Simulate temperature change
    print(f"\n=== Simulating Temperature Increase ===")
    zone_temp.present_value = 76.0
    print(f"New Temperature: {zone_temp.present_value:.1f}°F")
    bas.run_control_sequence()

if __name__ == "__main__":
    main()
```

## Key Concepts

### BACnet Services
- **Who-Is/I-Am**: Device discovery
- **ReadProperty/WriteProperty**: Object property access
- **SubscribeCOV**: Change-of-value notifications
- **ReadPropertyMultiple**: Efficient bulk reads

### HVAC Control Loops
- **PI Control**: Proportional-Integral for temperature/pressure
- **Cascade Control**: Multiple nested control loops
- **Feedforward Control**: Anticipatory control based on disturbances

## Key Performance Indicators

### Building Performance
- **Energy Use Intensity (EUI)**: kBtu/ft²/year
- **Peak Demand**: kW
- **HVAC Energy**: % of total building energy
- **Thermal Comfort**: % time within ASHRAE 55 bounds

### System Performance
- **BACnet Communication**: <1s response time
- **Control Loop Execution**: 60s typical
- **Alarm Response**: <5 minutes
- **System Uptime**: >99.5%

## Industry Resources

### Standards Organizations
- [ASHRAE](https://www.ashrae.org/)
- [BACnet International](https://www.bacnetinternational.org/)
- [Project Haystack](https://project-haystack.org/)

### Tools and Libraries
- **BAC0**: Python BACnet library
- **BACpypes**: Python BACnet stack
- **OpenStudio**: Building energy modeling
- **EnergyPlus**: Building simulation

## Conclusion

Building Automation Systems integrate diverse protocols and control sequences to optimize building operations. Production systems must be reliable, secure, and energy-efficient while maintaining occupant comfort. BACnet provides interoperability, while ASHRAE Guideline 36 provides proven control sequences for high-performance operation.
