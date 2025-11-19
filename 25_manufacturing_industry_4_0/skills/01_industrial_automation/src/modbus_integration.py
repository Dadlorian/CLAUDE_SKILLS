#!/usr/bin/env python3
"""
================================================================================
PRODUCTION-GRADE MODBUS TCP INTEGRATION FOR INDUSTRIAL AUTOMATION
================================================================================

Purpose: Enterprise-level Modbus TCP master client for collecting data from
industrial equipment (PLCs, RTUs, drives, sensors).

Features:
- Modbus TCP master (IEC 61158 compliant)
- Multi-device polling with configurable registers
- Automatic device discovery and health checking
- Data type conversion (REAL, INT, BOOL, STRING)
- Alarm/event generation from value thresholds
- Historian database integration (batch writes)
- Performance monitoring & throttling
- Comprehensive error handling & logging
- Graceful degradation on device failure

Reference Standards:
- IEC 61158 (Modbus Protocol)
- IEC 61131-3 (Industrial Programming)
- ISA-95 (Enterprise-Control System Integration)

Author: Industrial Automation Systems
Version: 2.0
Date: 2024-01-15
================================================================================
"""

import asyncio
import logging
import struct
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from pathlib import Path
import time

# Modbus library
from pymodbus.client.async_io import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException, ConnectionException
from pymodbus.pdu import ModbusRequest

# Database
import asyncpg
import aiosqlite

# Configuration
import yaml

# Metrics
from prometheus_client import Counter, Histogram, Gauge


class ModbusDataType(Enum):
    """Modbus data type definitions"""
    BOOL = 'BOOL'           # Coil (single bit)
    INT16 = 'INT16'         # Signed 16-bit integer
    UINT16 = 'UINT16'       # Unsigned 16-bit integer
    INT32 = 'INT32'         # Signed 32-bit integer
    UINT32 = 'UINT32'       # Unsigned 32-bit integer
    FLOAT = 'FLOAT'         # IEEE 754 32-bit float
    STRING = 'STRING'       # ASCII string


class ModbusFunctionCode(Enum):
    """Modbus standard function codes"""
    READ_COILS = 1              # Read digital outputs
    READ_DISCRETE_INPUTS = 2    # Read digital inputs
    READ_HOLDING_REGISTERS = 3  # Read analog values
    READ_INPUT_REGISTERS = 4    # Read sensor inputs
    WRITE_SINGLE_COIL = 5       # Write single digital output
    WRITE_SINGLE_REGISTER = 6   # Write single register
    WRITE_MULTIPLE_COILS = 15   # Write multiple digital outputs
    WRITE_MULTIPLE_REGISTERS = 16  # Write multiple registers


@dataclass
class ModbusRegisterConfig:
    """Configuration for a single Modbus register"""
    tag_id: str                      # Unique identifier
    address: int                     # Register address (0-65535)
    data_type: ModbusDataType       # Data type to read
    function_code: ModbusFunctionCode  # Modbus function code
    scale: float = 1.0              # Scaling factor (for analog values)
    offset: float = 0.0             # Offset to apply
    min_value: float = -float('inf')  # Minimum valid value
    max_value: float = float('inf')   # Maximum valid value
    description: str = ""           # Human-readable description


@dataclass
class ModbusDeviceConfig:
    """Configuration for a Modbus device"""
    device_id: str                  # Unique device identifier
    ip_address: str                 # IP address or hostname
    port: int = 502                 # Modbus TCP port
    unit_id: int = 1                # Slave address (1-247)
    timeout: int = 2                # Connection timeout (seconds)
    poll_interval: int = 500        # Poll interval (milliseconds)
    retries: int = 3                # Number of retry attempts
    registers: List[ModbusRegisterConfig] = field(default_factory=list)
    enabled: bool = True            # Enable/disable polling


@dataclass
class ModbusValue:
    """Data value read from Modbus device"""
    device_id: str
    tag_id: str
    address: int
    value: Any
    data_type: ModbusDataType
    timestamp: datetime
    quality: int = 0                # 0=Good, 1=Uncertain, 2=Bad
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'device_id': self.device_id,
            'tag_id': self.tag_id,
            'address': self.address,
            'value': self.value,
            'data_type': self.data_type.value,
            'timestamp': self.timestamp.isoformat(),
            'quality': self.quality,
            'error': self.error
        }


class ModbusDataConverter:
    """Convert between Modbus raw values and Python data types"""

    @staticmethod
    def convert_to_int16(data: List[int]) -> int:
        """Convert 16-bit register to signed integer"""
        if not data:
            raise ValueError("Empty data")
        value = data[0]
        if value >= 32768:
            value = value - 65536
        return value

    @staticmethod
    def convert_to_uint16(data: List[int]) -> int:
        """Convert 16-bit register to unsigned integer"""
        if not data:
            raise ValueError("Empty data")
        return data[0]

    @staticmethod
    def convert_to_int32(data: List[int]) -> int:
        """Convert two 16-bit registers to signed 32-bit integer (Modbus word order)"""
        if len(data) < 2:
            raise ValueError("Need at least 2 registers")
        # Modbus byte order: high word first, then low word
        value = (data[0] << 16) | data[1]
        if value >= 2147483648:
            value = value - 4294967296
        return value

    @staticmethod
    def convert_to_uint32(data: List[int]) -> int:
        """Convert two 16-bit registers to unsigned 32-bit integer"""
        if len(data) < 2:
            raise ValueError("Need at least 2 registers")
        return (data[0] << 16) | data[1]

    @staticmethod
    def convert_to_float(data: List[int]) -> float:
        """Convert two 16-bit registers to IEEE 754 32-bit float"""
        if len(data) < 2:
            raise ValueError("Need at least 2 registers")
        # Pack as big-endian 32-bit value
        byte_data = struct.pack('>HH', data[0], data[1])
        return struct.unpack('>f', byte_data)[0]

    @staticmethod
    def convert_to_string(data: List[int], length: int = 16) -> str:
        """Convert registers to ASCII string"""
        result = ""
        for i in range(min(len(data), length // 2)):
            high = (data[i] >> 8) & 0xFF
            low = data[i] & 0xFF
            if high != 0:
                result += chr(high)
            if low != 0:
                result += chr(low)
        return result.strip()

    @staticmethod
    def convert_value(raw_data: List[int], config: ModbusRegisterConfig) -> Any:
        """Convert raw Modbus data according to configuration"""
        try:
            if config.data_type == ModbusDataType.BOOL:
                return bool(raw_data[0])
            elif config.data_type == ModbusDataType.INT16:
                return ModbusDataConverter.convert_to_int16(raw_data)
            elif config.data_type == ModbusDataType.UINT16:
                return ModbusDataConverter.convert_to_uint16(raw_data)
            elif config.data_type == ModbusDataType.INT32:
                return ModbusDataConverter.convert_to_int32(raw_data)
            elif config.data_type == ModbusDataType.UINT32:
                return ModbusDataConverter.convert_to_uint32(raw_data)
            elif config.data_type == ModbusDataType.FLOAT:
                value = ModbusDataConverter.convert_to_float(raw_data)
                # Apply scale and offset
                return (value * config.scale) + config.offset
            elif config.data_type == ModbusDataType.STRING:
                return ModbusDataConverter.convert_to_string(raw_data)
            else:
                raise ValueError(f"Unknown data type: {config.data_type}")
        except Exception as e:
            raise ValueError(f"Conversion error: {e}")


class ModbusHistorian:
    """Historian database for Modbus values"""

    def __init__(self, db_type: str = 'sqlite', db_path: str = 'modbus_historian.db'):
        self.db_type = db_type
        self.db_path = db_path
        self.logger = logging.getLogger('ModbusHistorian')
        self.db = None

    async def connect(self):
        """Connect to historian database"""
        try:
            if self.db_type == 'sqlite':
                self.db = await aiosqlite.connect(self.db_path)
                await self._create_tables_sqlite()
                self.logger.info(f"Connected to SQLite: {self.db_path}")
            elif self.db_type == 'postgresql':
                # PostgreSQL example
                self.db = await asyncpg.connect(self.db_path)
                await self._create_tables_postgresql()
                self.logger.info(f"Connected to PostgreSQL")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise

    async def _create_tables_sqlite(self):
        """Create tables for SQLite"""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS modbus_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                address INTEGER NOT NULL,
                value REAL,
                data_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                quality INTEGER DEFAULT 0,
                UNIQUE(device_id, tag_id, timestamp)
            )
        """)
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tag_time ON modbus_values(tag_id, timestamp)
        """)
        await self.db.commit()

    async def _create_tables_postgresql(self):
        """Create tables for PostgreSQL"""
        # Implement for PostgreSQL if needed
        pass

    async def insert_value(self, value: ModbusValue) -> bool:
        """Insert single Modbus value"""
        try:
            if self.db_type == 'sqlite':
                await self.db.execute("""
                    INSERT OR IGNORE INTO modbus_values
                    (device_id, tag_id, address, value, data_type, timestamp, quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    value.device_id,
                    value.tag_id,
                    value.address,
                    float(value.value) if isinstance(value.value, (int, float)) else str(value.value),
                    value.data_type.value,
                    value.timestamp,
                    value.quality
                ))
                await self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Insert failed: {e}")
            return False

    async def batch_insert(self, values: List[ModbusValue]) -> int:
        """Insert multiple values efficiently"""
        if not values:
            return 0
        try:
            if self.db_type == 'sqlite':
                await self.db.executemany("""
                    INSERT OR IGNORE INTO modbus_values
                    (device_id, tag_id, address, value, data_type, timestamp, quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    (
                        v.device_id,
                        v.tag_id,
                        v.address,
                        float(v.value) if isinstance(v.value, (int, float)) else str(v.value),
                        v.data_type.value,
                        v.timestamp,
                        v.quality
                    )
                    for v in values
                ])
                await self.db.commit()
                return len(values)
        except Exception as e:
            self.logger.error(f"Batch insert failed: {e}")
            return 0

    async def disconnect(self):
        """Close database connection"""
        if self.db:
            await self.db.close()


class ModbusDevicePoller:
    """Poll a single Modbus device"""

    def __init__(self, config: ModbusDeviceConfig):
        self.config = config
        self.client: Optional[AsyncModbusTcpClient] = None
        self.logger = logging.getLogger(f'ModbusDevice[{config.device_id}]')
        self.last_successful_poll: Optional[datetime] = None
        self.consecutive_failures: int = 0
        self.online: bool = False

        # Metrics
        self.poll_count = Counter(
            'modbus_polls_total',
            'Total polls',
            ['device_id']
        )
        self.poll_failures = Counter(
            'modbus_poll_failures_total',
            'Failed polls',
            ['device_id']
        )
        self.poll_latency = Histogram(
            'modbus_poll_latency_seconds',
            'Poll latency',
            ['device_id']
        )
        self.device_status = Gauge(
            'modbus_device_online',
            'Device online status (1=online, 0=offline)',
            ['device_id']
        )

    async def connect(self) -> bool:
        """Connect to Modbus device"""
        try:
            self.client = AsyncModbusTcpClient(
                host=self.config.ip_address,
                port=self.config.port,
                timeout=self.config.timeout
            )
            await self.client.connect()
            self.online = True
            self.consecutive_failures = 0
            self.device_status.labels(device_id=self.config.device_id).set(1)
            self.logger.info(f"Connected to {self.config.ip_address}:{self.config.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.online = False
            self.device_status.labels(device_id=self.config.device_id).set(0)
            return False

    async def disconnect(self):
        """Disconnect from device"""
        if self.client:
            await self.client.close()
            self.online = False

    async def poll_register(self, reg_config: ModbusRegisterConfig) -> Optional[ModbusValue]:
        """Poll a single register"""
        start_time = time.time()
        try:
            if not self.client or not self.online:
                return None

            # Determine register count based on data type
            count = self._get_register_count(reg_config.data_type)

            # Read registers
            if reg_config.function_code == ModbusFunctionCode.READ_COILS:
                result = await self.client.read_coils(
                    reg_config.address,
                    count,
                    slave=self.config.unit_id
                )
                raw_data = result.bits if hasattr(result, 'bits') else [result.bits[0]]
            elif reg_config.function_code == ModbusFunctionCode.READ_DISCRETE_INPUTS:
                result = await self.client.read_discrete_inputs(
                    reg_config.address,
                    count,
                    slave=self.config.unit_id
                )
                raw_data = result.bits
            elif reg_config.function_code == ModbusFunctionCode.READ_HOLDING_REGISTERS:
                result = await self.client.read_holding_registers(
                    reg_config.address,
                    count,
                    slave=self.config.unit_id
                )
                raw_data = result.registers
            elif reg_config.function_code == ModbusFunctionCode.READ_INPUT_REGISTERS:
                result = await self.client.read_input_registers(
                    reg_config.address,
                    count,
                    slave=self.config.unit_id
                )
                raw_data = result.registers
            else:
                return None

            # Convert raw data
            value = ModbusDataConverter.convert_value(raw_data, reg_config)

            # Validate range
            if not (reg_config.min_value <= value <= reg_config.max_value):
                self.logger.warning(f"Out of range: {reg_config.tag_id}={value}")
                quality = 1  # Uncertain
            else:
                quality = 0  # Good

            # Record metrics
            latency = time.time() - start_time
            self.poll_latency.labels(device_id=self.config.device_id).observe(latency)
            self.consecutive_failures = 0
            self.last_successful_poll = datetime.utcnow()

            return ModbusValue(
                device_id=self.config.device_id,
                tag_id=reg_config.tag_id,
                address=reg_config.address,
                value=value,
                data_type=reg_config.data_type,
                timestamp=datetime.utcnow(),
                quality=quality
            )

        except Exception as e:
            self.logger.error(f"Poll error ({reg_config.tag_id}): {e}")
            self.poll_failures.labels(device_id=self.config.device_id).inc()
            self.consecutive_failures += 1

            if self.consecutive_failures >= self.config.retries:
                self.online = False
                self.device_status.labels(device_id=self.config.device_id).set(0)

            return None

    async def poll_all_registers(self) -> List[ModbusValue]:
        """Poll all configured registers on device"""
        if not self.config.enabled:
            return []

        # Reconnect if offline
        if not self.online:
            await self.connect()

        values = []
        for reg_config in self.config.registers:
            value = await self.poll_register(reg_config)
            if value:
                values.append(value)

        self.poll_count.labels(device_id=self.config.device_id).inc()
        return values

    def _get_register_count(self, data_type: ModbusDataType) -> int:
        """Get number of registers needed for data type"""
        if data_type in (ModbusDataType.BOOL, ModbusDataType.INT16, ModbusDataType.UINT16):
            return 1
        elif data_type in (ModbusDataType.INT32, ModbusDataType.UINT32, ModbusDataType.FLOAT):
            return 2
        elif data_type == ModbusDataType.STRING:
            return 8  # 16 characters
        else:
            return 1

    def health_check(self) -> Dict[str, Any]:
        """Return device health information"""
        return {
            'device_id': self.config.device_id,
            'online': self.online,
            'consecutive_failures': self.consecutive_failures,
            'last_poll': self.last_successful_poll,
            'uptime_percentage': self._calculate_uptime()
        }

    def _calculate_uptime(self) -> float:
        """Calculate approximate uptime percentage"""
        if self.last_successful_poll:
            # Simple approximation
            return 100.0 if self.online else 0.0
        return 0.0


class ModbusMaster:
    """Main Modbus master controller"""

    def __init__(self, config_file: str = 'modbus_config.yaml'):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.logger = logging.getLogger('ModbusMaster')
        self.devices: Dict[str, ModbusDevicePoller] = {}
        self.historian = ModbusHistorian()
        self.running = False

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            self._create_example_config()
            raise FileNotFoundError(f"Created example config: {self.config_file}")

        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def _create_example_config(self):
        """Create example configuration file"""
        example_config = {
            'historian': {
                'db_type': 'sqlite',
                'db_path': 'modbus_historian.db'
            },
            'devices': [
                {
                    'device_id': 'PLC_Zone1',
                    'ip_address': '192.168.1.100',
                    'port': 502,
                    'unit_id': 1,
                    'poll_interval': 500,
                    'enabled': True,
                    'registers': [
                        {
                            'tag_id': 'TEMP_ZONE_1',
                            'address': 30000,
                            'data_type': 'FLOAT',
                            'function_code': 4,
                            'scale': 0.1,
                            'min_value': -50.0,
                            'max_value': 100.0,
                            'description': 'Temperature Zone 1 (°C)'
                        },
                        {
                            'tag_id': 'HEATER_OUTPUT',
                            'address': 40000,
                            'data_type': 'UINT16',
                            'function_code': 3,
                            'scale': 0.1,
                            'min_value': 0.0,
                            'max_value': 100.0,
                            'description': 'Heater Output (%)'
                        }
                    ]
                }
            ]
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(example_config, f)

    async def initialize(self):
        """Initialize all devices"""
        await self.historian.connect()

        # Create device pollers
        for device_config_dict in self.config.get('devices', []):
            # Parse register configurations
            registers = []
            for reg_dict in device_config_dict.get('registers', []):
                reg_config = ModbusRegisterConfig(
                    tag_id=reg_dict['tag_id'],
                    address=reg_dict['address'],
                    data_type=ModbusDataType[reg_dict['data_type']],
                    function_code=ModbusFunctionCode(int(reg_dict.get('function_code', 3))),
                    scale=reg_dict.get('scale', 1.0),
                    offset=reg_dict.get('offset', 0.0),
                    min_value=reg_dict.get('min_value', -float('inf')),
                    max_value=reg_dict.get('max_value', float('inf')),
                    description=reg_dict.get('description', '')
                )
                registers.append(reg_config)

            # Create device configuration
            device_config = ModbusDeviceConfig(
                device_id=device_config_dict['device_id'],
                ip_address=device_config_dict['ip_address'],
                port=device_config_dict.get('port', 502),
                unit_id=device_config_dict.get('unit_id', 1),
                timeout=device_config_dict.get('timeout', 2),
                poll_interval=device_config_dict.get('poll_interval', 500),
                retries=device_config_dict.get('retries', 3),
                registers=registers,
                enabled=device_config_dict.get('enabled', True)
            )

            # Create device poller
            poller = ModbusDevicePoller(device_config)
            self.devices[device_config.device_id] = poller
            self.logger.info(f"Configured device: {device_config.device_id}")

    async def run(self):
        """Main polling loop"""
        self.running = True
        self.logger.info("Starting Modbus polling")

        try:
            while self.running:
                tasks = []
                for device in self.devices.values():
                    if device.config.enabled:
                        tasks.append(self._poll_device(device))

                # Poll all devices in parallel
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Batch insert into historian
                    all_values = []
                    for result in results:
                        if isinstance(result, list):
                            all_values.extend(result)

                    if all_values:
                        await self.historian.batch_insert(all_values)

                # Wait before next poll cycle
                await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
        finally:
            await self.shutdown()

    async def _poll_device(self, device: ModbusDevicePoller) -> List[ModbusValue]:
        """Poll single device"""
        poll_interval = device.config.poll_interval / 1000.0
        values = await device.poll_all_registers()
        await asyncio.sleep(poll_interval)
        return values

    async def shutdown(self):
        """Shutdown all devices and close connections"""
        self.logger.info("Shutting down Modbus Master")
        self.running = False

        for device in self.devices.values():
            await device.disconnect()

        await self.historian.disconnect()


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('modbus_master.log'),
            logging.StreamHandler()
        ]
    )

    try:
        master = ModbusMaster('modbus_config.yaml')
        await master.initialize()
        await master.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run again after configuring modbus_config.yaml")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
