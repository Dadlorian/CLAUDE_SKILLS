"""
BACnet Integration for Building Automation

Comprehensive BACnet/IP and MS/TP integration library for reading and controlling
building automation devices including thermostats, VAV boxes, sensors, and controllers.

Dependencies:
    pip install BAC0 pandas influxdb-client python-dotenv

BACnet Overview:
- BACnet (Building Automation and Control networks) is the industry standard protocol
- Supports multiple network types: IP, MS/TP, Ethernet, LonTalk
- Object-based architecture: Analog Input, Analog Output, Binary Input, Binary Output, etc.
- Priority array (1-16) for write operations (lower number = higher priority)
"""

import BAC0
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BACnetObjectType(Enum):
    """Common BACnet object types"""
    ANALOG_INPUT = 'analogInput'
    ANALOG_OUTPUT = 'analogOutput'
    ANALOG_VALUE = 'analogValue'
    BINARY_INPUT = 'binaryInput'
    BINARY_OUTPUT = 'binaryOutput'
    BINARY_VALUE = 'binaryValue'
    MULTI_STATE_INPUT = 'multiStateInput'
    MULTI_STATE_OUTPUT = 'multiStateOutput'
    MULTI_STATE_VALUE = 'multiStateValue'


class BACnetPriority(Enum):
    """BACnet priority array levels (1=highest, 16=lowest)"""
    MANUAL_LIFE_SAFETY = 1
    AUTO_LIFE_SAFETY = 2
    AVAILABLE_3 = 3
    AVAILABLE_4 = 4
    CRITICAL_EQUIPMENT = 5
    MINIMUM_ON_OFF = 6
    AVAILABLE_7 = 7
    MANUAL_OPERATOR = 8  # Typical BMS override
    AVAILABLE_9 = 9
    AVAILABLE_10 = 10
    AVAILABLE_11 = 11
    AVAILABLE_12 = 12
    AVAILABLE_13 = 13
    AVAILABLE_14 = 14
    AVAILABLE_15 = 15
    AVAILABLE_16 = 16  # Lowest priority (schedule)


@dataclass
class BACnetDevice:
    """Represents a discovered BACnet device"""
    device_id: int
    name: str
    vendor: str
    model: str
    ip_address: Optional[str] = None
    objects: Optional[List] = None


@dataclass
class ZoneData:
    """Zone sensor and control data"""
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2: Optional[float] = None
    occupancy: Optional[bool] = None
    setpoint: Optional[float] = None
    heating_output: Optional[float] = None
    cooling_output: Optional[float] = None
    fan_speed: Optional[float] = None
    damper_position: Optional[float] = None


class BACnetController:
    """
    Production-ready BACnet controller for reading sensors and writing commands

    Features:
    - Device discovery and inventory
    - Bulk read operations
    - COV (Change of Value) subscriptions
    - Error handling and retry logic
    - Data validation and conversion
    - Logging and monitoring
    """

    def __init__(self, ip_address: str, port: int = 47808, device_id: int = 999999):
        """
        Initialize BACnet controller

        Args:
            ip_address: Local IP address and subnet (e.g., '192.168.1.10/24')
            port: UDP port for BACnet/IP (default 47808)
            device_id: Device ID for this client (should be unique on network)
        """
        try:
            self.bacnet = BAC0.connect(ip=ip_address, port=port, bbmdAddress=None)
            self.devices: Dict[int, BACnetDevice] = {}
            self.subscriptions = {}
            logger.info(f"BACnet controller initialized on {ip_address}")
        except Exception as e:
            logger.error(f"Failed to initialize BACnet controller: {e}")
            raise

    def discover_devices(self, timeout: int = 10) -> Dict[int, BACnetDevice]:
        """
        Discover all BACnet devices on network using WhoIs broadcast

        Args:
            timeout: Seconds to wait for device responses

        Returns:
            Dictionary of device_id -> BACnetDevice
        """
        logger.info("Starting device discovery...")
        self.bacnet.whois()
        time.sleep(timeout)

        for device in self.bacnet.devices:
            try:
                device_info = BACnetDevice(
                    device_id=device.properties.device_id,
                    name=device.properties.objectName or f"Device_{device.properties.device_id}",
                    vendor=device.properties.vendorName or "Unknown",
                    model=device.properties.modelName or "Unknown",
                    ip_address=device.properties.address if hasattr(device.properties, 'address') else None
                )
                self.devices[device_info.device_id] = device_info
                logger.info(f"Discovered: {device_info.name} (ID: {device_info.device_id})")
            except Exception as e:
                logger.warning(f"Error reading device properties: {e}")

        logger.info(f"Discovery complete. Found {len(self.devices)} devices")
        return self.devices

    def read_point(self, device_id: int, object_type: str, object_id: int,
                   property_name: str = 'presentValue', retry: int = 3) -> Optional[Any]:
        """
        Read a single point from BACnet device with retry logic

        Args:
            device_id: BACnet device ID
            object_type: Object type (analogInput, binaryOutput, etc.)
            object_id: Object instance number
            property_name: Property to read (default: presentValue)
            retry: Number of retry attempts

        Returns:
            Point value or None if failed
        """
        point_address = f'{device_id}:{object_type} {object_id} {property_name}'

        for attempt in range(retry):
            try:
                value = self.bacnet.read(point_address)
                return value
            except Exception as e:
                logger.warning(f"Read attempt {attempt+1}/{retry} failed for {point_address}: {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        logger.error(f"Failed to read {point_address} after {retry} attempts")
        return None

    def write_point(self, device_id: int, object_type: str, object_id: int,
                    value: Any, priority: int = 8, retry: int = 3) -> bool:
        """
        Write a value to BACnet point with priority

        Args:
            device_id: BACnet device ID
            object_type: Object type (analogOutput, binaryOutput, analogValue, etc.)
            object_id: Object instance number
            value: Value to write
            priority: Priority level (1-16, default 8 for manual operator)
            retry: Number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        point_address = f'{device_id}:{object_type} {object_id} presentValue {value} - {priority}'

        for attempt in range(retry):
            try:
                self.bacnet.write(point_address)
                logger.info(f"Wrote {value} to {device_id}:{object_type} {object_id} @ priority {priority}")
                return True
            except Exception as e:
                logger.warning(f"Write attempt {attempt+1}/{retry} failed: {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        logger.error(f"Failed to write {point_address} after {retry} attempts")
        return False

    def release_point(self, device_id: int, object_type: str, object_id: int, priority: int = 8) -> bool:
        """
        Release a priority level (write NULL to priority slot)

        Args:
            device_id: BACnet device ID
            object_type: Object type
            object_id: Object instance number
            priority: Priority level to release

        Returns:
            True if successful
        """
        point_address = f'{device_id}:{object_type} {object_id} presentValue null - {priority}'
        try:
            self.bacnet.write(point_address)
            logger.info(f"Released priority {priority} on {device_id}:{object_type} {object_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to release point: {e}")
            return False

    def read_zone_data(self, device_id: int, config: Optional[Dict] = None) -> ZoneData:
        """
        Read comprehensive zone data (temperature, humidity, CO2, occupancy, etc.)

        Args:
            device_id: BACnet device ID (typically a VAV box or zone controller)
            config: Optional configuration mapping for object IDs
                   Example: {'temperature': ('analogInput', 1), 'setpoint': ('analogValue', 1)}

        Returns:
            ZoneData object with all available readings
        """
        # Default point mapping (can be customized per device type)
        default_config = {
            'temperature': ('analogInput', 1),
            'humidity': ('analogInput', 2),
            'co2': ('analogInput', 3),
            'occupancy': ('binaryInput', 1),
            'setpoint': ('analogValue', 1),
            'heating_output': ('analogOutput', 1),
            'cooling_output': ('analogOutput', 2),
            'fan_speed': ('analogOutput', 3),
            'damper_position': ('analogOutput', 4)
        }

        point_config = config or default_config
        data = ZoneData(timestamp=datetime.now())

        for field, (obj_type, obj_id) in point_config.items():
            try:
                value = self.read_point(device_id, obj_type, obj_id)
                setattr(data, field, value)
            except Exception as e:
                logger.debug(f"Could not read {field} from device {device_id}: {e}")

        return data

    def bulk_read(self, point_list: List[tuple]) -> Dict[str, Any]:
        """
        Read multiple points efficiently

        Args:
            point_list: List of tuples (device_id, object_type, object_id, alias)
                       Example: [(100, 'analogInput', 1, 'zone1_temp'), ...]

        Returns:
            Dictionary of alias -> value
        """
        results = {}
        for device_id, obj_type, obj_id, alias in point_list:
            value = self.read_point(device_id, obj_type, obj_id)
            results[alias] = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'device_id': device_id,
                'object': f'{obj_type} {obj_id}'
            }
        return results

    def subscribe_cov(self, device_id: int, object_type: str, object_id: int,
                      callback: Callable, lifetime: int = 3600) -> bool:
        """
        Subscribe to Change of Value (COV) notifications

        Args:
            device_id: BACnet device ID
            object_type: Object type
            object_id: Object instance
            callback: Function to call when value changes
            lifetime: Subscription lifetime in seconds

        Returns:
            True if subscription successful
        """
        point_address = f'{device_id}:{object_type} {object_id}'
        try:
            self.bacnet.subscribe_cov(point_address, callback=callback, lifetime=lifetime)
            self.subscriptions[point_address] = {
                'callback': callback,
                'subscribed_at': datetime.now(),
                'lifetime': lifetime
            }
            logger.info(f"Subscribed to COV for {point_address}")
            return True
        except Exception as e:
            logger.error(f"COV subscription failed for {point_address}: {e}")
            return False

    def unsubscribe_cov(self, device_id: int, object_type: str, object_id: int) -> bool:
        """Unsubscribe from COV notifications"""
        point_address = f'{device_id}:{object_type} {object_id}'
        try:
            self.bacnet.unsubscribe_cov(point_address)
            if point_address in self.subscriptions:
                del self.subscriptions[point_address]
            logger.info(f"Unsubscribed from {point_address}")
            return True
        except Exception as e:
            logger.error(f"Unsubscribe failed: {e}")
            return False

    def get_priority_array(self, device_id: int, object_type: str, object_id: int) -> Dict[int, Any]:
        """
        Read the priority array to see all active write values

        Returns:
            Dictionary of priority -> value (None means no write at that priority)
        """
        try:
            priority_array = self.bacnet.read(f'{device_id}:{object_type} {object_id} priorityArray')
            return {i+1: val for i, val in enumerate(priority_array) if val is not None}
        except Exception as e:
            logger.error(f"Failed to read priority array: {e}")
            return {}

    def disconnect(self):
        """Clean disconnect from BACnet network"""
        try:
            # Unsubscribe from all COV subscriptions
            for point_address in list(self.subscriptions.keys()):
                parts = point_address.split(':')
                device_id = int(parts[0])
                obj_parts = parts[1].split()
                self.unsubscribe_cov(device_id, obj_parts[0], int(obj_parts[1]))

            self.bacnet.disconnect()
            logger.info("BACnet controller disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")


# Example usage and testing
if __name__ == '__main__':
    # Initialize controller
    controller = BACnetController('192.168.1.10/24')

    # Discover all devices on network
    devices = controller.discover_devices(timeout=10)
    print(f"\nFound {len(devices)} devices:")
    for dev_id, device in devices.items():
        print(f"  {dev_id}: {device.name} ({device.vendor} {device.model})")

    # Example: Read zone data from a VAV controller (device ID 100)
    if 100 in devices:
        zone_data = controller.read_zone_data(100)
        print(f"\nZone 100 Data:")
        print(f"  Temperature: {zone_data.temperature}°F")
        print(f"  Humidity: {zone_data.humidity}% RH")
        print(f"  CO2: {zone_data.co2} ppm")
        print(f"  Occupancy: {zone_data.occupancy}")
        print(f"  Setpoint: {zone_data.setpoint}°F")

    # Example: Write temperature setpoint
    success = controller.write_point(
        device_id=100,
        object_type='analogValue',
        object_id=1,
        value=72.0,
        priority=8
    )
    print(f"\nSetpoint write: {'Success' if success else 'Failed'}")

    # Example: Bulk read multiple points
    point_list = [
        (100, 'analogInput', 1, 'zone1_temp'),
        (100, 'analogInput', 2, 'zone1_humidity'),
        (101, 'analogInput', 1, 'zone2_temp'),
        (102, 'binaryInput', 1, 'ahu_status')
    ]
    bulk_data = controller.bulk_read(point_list)
    print(f"\nBulk Read Results:")
    for alias, data in bulk_data.items():
        print(f"  {alias}: {data['value']} @ {data['timestamp']}")

    # Example: COV subscription with callback
    def temp_change_callback(value):
        print(f"Temperature changed to {value}°F at {datetime.now()}")

    controller.subscribe_cov(
        device_id=100,
        object_type='analogInput',
        object_id=1,
        callback=temp_change_callback,
        lifetime=3600
    )

    # Keep alive for COV notifications (in production, this would be in a loop)
    print("\nMonitoring for 60 seconds...")
    time.sleep(60)

    # Clean disconnect
    controller.disconnect()
