"""
MES API Integration Module
Provides comprehensive API integration patterns for Manufacturing Execution Systems.
Includes OPC-UA, REST API, MQTT, and database connectivity.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from contextlib import asynccontextmanager

import aiohttp
from opcua import Client as OpcClient
from opcua.ua import NodeId
import paho.mqtt.client as mqtt
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Data Models ====================

class EquipmentStatus(Enum):
    """Equipment operational status."""
    RUNNING = "running"
    IDLE = "idle"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"
    FAULT = "fault"
    OFFLINE = "offline"


class DataSource(Enum):
    """Source of data collection."""
    OPC_UA = "opc_ua"
    REST_API = "rest_api"
    MQTT = "mqtt"
    DATABASE = "database"


@dataclass
class EquipmentParameter:
    """Equipment parameter value with metadata."""
    parameter_name: str
    value: Any
    unit: str
    timestamp: datetime
    source: DataSource
    equipment_id: str
    quality_good: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'parameter_name': self.parameter_name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.value,
            'equipment_id': self.equipment_id,
            'quality_good': self.quality_good,
        }


@dataclass
class WorkOrder:
    """Production work order."""
    work_order_id: str
    product_id: str
    target_quantity: int
    scheduled_start: datetime
    scheduled_end: datetime
    equipment_id: str
    operator_id: Optional[str] = None
    material_lot: Optional[str] = None
    status: str = "pending"
    actual_quantity: int = 0
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['scheduled_start'] = self.scheduled_start.isoformat()
        data['scheduled_end'] = self.scheduled_end.isoformat()
        if self.actual_start:
            data['actual_start'] = self.actual_start.isoformat()
        if self.actual_end:
            data['actual_end'] = self.actual_end.isoformat()
        return data


@dataclass
class ProductionEvent:
    """Production event/alarm."""
    event_id: str
    equipment_id: str
    event_type: str  # "alarm", "status_change", "quality_failure", etc.
    severity: str  # "critical", "high", "medium", "low"
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


# ==================== Database Models ====================

Base = declarative_base()


class EquipmentParameterRecord(Base):
    """Database record for equipment parameters."""
    __tablename__ = 'equipment_parameters'

    id = Column(Integer, primary_key=True)
    equipment_id = Column(String(100), nullable=False, index=True)
    parameter_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=True)
    string_value = Column(String(500), nullable=True)
    unit = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    source = Column(String(50), nullable=False)
    quality_good = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def from_parameter(self, param: EquipmentParameter) -> None:
        """Populate from EquipmentParameter."""
        self.equipment_id = param.equipment_id
        self.parameter_name = param.parameter_name
        self.unit = param.unit
        self.timestamp = param.timestamp
        self.source = param.source.value
        self.quality_good = param.quality_good

        # Store numeric or string value appropriately
        if isinstance(param.value, (int, float)):
            self.value = float(param.value)
        else:
            self.string_value = str(param.value)


class WorkOrderRecord(Base):
    """Database record for work orders."""
    __tablename__ = 'work_orders'

    id = Column(Integer, primary_key=True)
    work_order_id = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(String(100), nullable=False)
    target_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, default=0)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    equipment_id = Column(String(100), nullable=False)
    operator_id = Column(String(100), nullable=True)
    material_lot = Column(String(100), nullable=True)
    status = Column(String(50), default='pending')
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductionEventRecord(Base):
    """Database record for production events."""
    __tablename__ = 'production_events'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    equipment_id = Column(String(100), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    message = Column(String(1000), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    acknowledged = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    resolution_notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== API Clients ====================

class MESDataClient(ABC):
    """Abstract base class for MES data clients."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from data source."""
        pass

    @abstractmethod
    async def get_parameter(self, equipment_id: str, parameter_name: str) -> Optional[EquipmentParameter]:
        """Get single parameter value."""
        pass

    @abstractmethod
    async def get_parameters(self, equipment_id: str) -> List[EquipmentParameter]:
        """Get all parameters for equipment."""
        pass


class OpcUAClient(MESDataClient):
    """OPC-UA client for equipment data collection."""

    def __init__(self, server_url: str, timeout: int = 5):
        """Initialize OPC-UA client.

        Args:
            server_url: OPC-UA server endpoint (e.g., 'opc.tcp://localhost:4840')
            timeout: Connection timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self.client: Optional[OpcClient] = None
        self.connected = False

    async def connect(self) -> None:
        """Connect to OPC-UA server."""
        try:
            self.client = OpcClient(self.server_url, timeout=self.timeout)
            await asyncio.to_thread(self.client.connect)
            self.connected = True
            logger.info(f"Connected to OPC-UA server: {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to OPC-UA server: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from OPC-UA server."""
        if self.client and self.connected:
            await asyncio.to_thread(self.client.disconnect)
            self.connected = False
            logger.info("Disconnected from OPC-UA server")

    async def get_parameter(self, equipment_id: str, parameter_name: str) -> Optional[EquipmentParameter]:
        """Get parameter value from OPC-UA server.

        Args:
            equipment_id: Equipment identifier
            parameter_name: Parameter name/tag

        Returns:
            EquipmentParameter with current value
        """
        if not self.connected or not self.client:
            return None

        try:
            # Construct OPC-UA node path
            node_path = f"ns=2;s={equipment_id}/{parameter_name}"
            node = self.client.get_node(node_path)

            value = await asyncio.to_thread(node.get_value)
            timestamp = datetime.utcnow()

            return EquipmentParameter(
                parameter_name=parameter_name,
                value=value,
                unit="",  # Would be retrieved from node attributes
                timestamp=timestamp,
                source=DataSource.OPC_UA,
                equipment_id=equipment_id
            )
        except Exception as e:
            logger.error(f"Failed to read OPC-UA parameter {equipment_id}/{parameter_name}: {e}")
            return None

    async def get_parameters(self, equipment_id: str) -> List[EquipmentParameter]:
        """Get all parameters for equipment.

        Args:
            equipment_id: Equipment identifier

        Returns:
            List of EquipmentParameter objects
        """
        if not self.connected or not self.client:
            return []

        parameters = []
        # Common industrial parameters
        param_names = ['temperature', 'pressure', 'speed', 'power', 'status', 'cycle_time']

        for param_name in param_names:
            param = await self.get_parameter(equipment_id, param_name)
            if param:
                parameters.append(param)

        return parameters


class RestAPIClient(MESDataClient):
    """REST API client for equipment and system integration."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize REST API client.

        Args:
            base_url: API base URL
            api_key: Optional API authentication key
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def connect(self) -> None:
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        logger.info(f"REST API client initialized: {self.base_url}")

    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("REST API session closed")

    async def get_parameter(self, equipment_id: str, parameter_name: str) -> Optional[EquipmentParameter]:
        """Get parameter from REST API.

        Args:
            equipment_id: Equipment identifier
            parameter_name: Parameter name

        Returns:
            EquipmentParameter with current value
        """
        if not self.session:
            return None

        try:
            url = f"{self.base_url}/equipment/{equipment_id}/parameters/{parameter_name}"
            async with self.session.get(url, headers=self._get_headers()) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return EquipmentParameter(
                        parameter_name=parameter_name,
                        value=data.get('value'),
                        unit=data.get('unit', ''),
                        timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
                        source=DataSource.REST_API,
                        equipment_id=equipment_id,
                        quality_good=data.get('quality_good', True)
                    )
        except Exception as e:
            logger.error(f"Failed to get parameter via REST API: {e}")

        return None

    async def get_parameters(self, equipment_id: str) -> List[EquipmentParameter]:
        """Get all parameters for equipment.

        Args:
            equipment_id: Equipment identifier

        Returns:
            List of EquipmentParameter objects
        """
        if not self.session:
            return []

        try:
            url = f"{self.base_url}/equipment/{equipment_id}/parameters"
            async with self.session.get(url, headers=self._get_headers()) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    parameters = []
                    for param_data in data.get('parameters', []):
                        param = EquipmentParameter(
                            parameter_name=param_data['name'],
                            value=param_data['value'],
                            unit=param_data.get('unit', ''),
                            timestamp=datetime.fromisoformat(param_data.get('timestamp')),
                            source=DataSource.REST_API,
                            equipment_id=equipment_id,
                            quality_good=param_data.get('quality_good', True)
                        )
                        parameters.append(param)
                    return parameters
        except Exception as e:
            logger.error(f"Failed to get parameters via REST API: {e}")

        return []

    async def post_work_order(self, work_order: WorkOrder) -> bool:
        """Post work order to MES system.

        Args:
            work_order: WorkOrder to post

        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            return False

        try:
            url = f"{self.base_url}/work-orders"
            async with self.session.post(
                url,
                json=work_order.to_dict(),
                headers=self._get_headers()
            ) as resp:
                if resp.status in [200, 201]:
                    logger.info(f"Work order posted: {work_order.work_order_id}")
                    return True
                else:
                    logger.error(f"Failed to post work order: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to post work order: {e}")
            return False


class MQTTDataCollector:
    """MQTT client for real-time data collection from sensors."""

    def __init__(self, broker: str, port: int = 1883, client_id: str = "mes-collector"):
        """Initialize MQTT client.

        Args:
            broker: MQTT broker address
            port: MQTT broker port
            client_id: MQTT client identifier
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.data_callbacks: List[Callable[[str, EquipmentParameter], None]] = []

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker: {self.broker}:{self.port}")
            # Subscribe to equipment topics
            client.subscribe("factory/+/+/parameters")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            # Parse topic: factory/equipment_id/parameter_name/value
            parts = msg.topic.split('/')
            if len(parts) >= 3:
                equipment_id = parts[1]
                parameter_name = parts[2]
                value = json.loads(msg.payload.decode())

                param = EquipmentParameter(
                    parameter_name=parameter_name,
                    value=value.get('value'),
                    unit=value.get('unit', ''),
                    timestamp=datetime.utcnow(),
                    source=DataSource.MQTT,
                    equipment_id=equipment_id,
                    quality_good=value.get('quality_good', True)
                )

                # Call registered callbacks
                for callback in self.data_callbacks:
                    callback(equipment_id, param)
        except Exception as e:
            logger.error(f"Failed to process MQTT message: {e}")

    def connect(self) -> None:
        """Connect to MQTT broker."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

    def register_callback(self, callback: Callable[[str, EquipmentParameter], None]) -> None:
        """Register callback for data updates.

        Args:
            callback: Function(equipment_id, parameter) to call on new data
        """
        self.data_callbacks.append(callback)


# ==================== Data Persistence ====================

class MESDatabase:
    """Database persistence layer for MES data."""

    def __init__(self, connection_string: str, pool_size: int = 10):
        """Initialize database connection.

        Args:
            connection_string: SQLAlchemy connection string
            pool_size: Connection pool size
        """
        self.connection_string = connection_string
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=20,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        """Create database tables."""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")

    @asynccontextmanager
    async def get_session(self):
        """Get database session (async context manager)."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    async def save_parameter(self, param: EquipmentParameter) -> bool:
        """Save equipment parameter to database.

        Args:
            param: EquipmentParameter to save

        Returns:
            True if successful
        """
        try:
            record = EquipmentParameterRecord()
            record.from_parameter(param)

            session = self.SessionLocal()
            session.add(record)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save parameter: {e}")
            return False

    async def save_work_order(self, work_order: WorkOrder) -> bool:
        """Save work order to database.

        Args:
            work_order: WorkOrder to save

        Returns:
            True if successful
        """
        try:
            record = WorkOrderRecord(
                work_order_id=work_order.work_order_id,
                product_id=work_order.product_id,
                target_quantity=work_order.target_quantity,
                actual_quantity=work_order.actual_quantity,
                scheduled_start=work_order.scheduled_start,
                scheduled_end=work_order.scheduled_end,
                actual_start=work_order.actual_start,
                actual_end=work_order.actual_end,
                equipment_id=work_order.equipment_id,
                operator_id=work_order.operator_id,
                material_lot=work_order.material_lot,
                status=work_order.status
            )

            session = self.SessionLocal()
            session.add(record)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save work order: {e}")
            return False

    async def get_work_order(self, work_order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve work order from database.

        Args:
            work_order_id: Work order identifier

        Returns:
            Work order data dictionary or None
        """
        try:
            session = self.SessionLocal()
            record = session.query(WorkOrderRecord).filter_by(
                work_order_id=work_order_id
            ).first()
            session.close()

            if record:
                return {
                    'work_order_id': record.work_order_id,
                    'product_id': record.product_id,
                    'status': record.status,
                    'actual_quantity': record.actual_quantity,
                    'created_at': record.created_at.isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to retrieve work order: {e}")

        return None

    async def get_equipment_parameters(
        self,
        equipment_id: str,
        parameter_name: Optional[str] = None,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get equipment parameter history.

        Args:
            equipment_id: Equipment identifier
            parameter_name: Optional specific parameter
            hours_back: Historical data to retrieve (hours)

        Returns:
            List of parameter records
        """
        try:
            session = self.SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

            query = session.query(EquipmentParameterRecord).filter(
                EquipmentParameterRecord.equipment_id == equipment_id,
                EquipmentParameterRecord.timestamp >= cutoff_time
            )

            if parameter_name:
                query = query.filter(
                    EquipmentParameterRecord.parameter_name == parameter_name
                )

            records = query.order_by(EquipmentParameterRecord.timestamp.desc()).all()

            results = [
                {
                    'parameter_name': r.parameter_name,
                    'value': r.value or r.string_value,
                    'unit': r.unit,
                    'timestamp': r.timestamp.isoformat(),
                    'quality_good': r.quality_good
                }
                for r in records
            ]

            session.close()
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve parameter history: {e}")
            return []


# ==================== Integration Orchestrator ====================

class MESIntegrator:
    """High-level orchestrator for MES integration."""

    def __init__(self, db: MESDatabase):
        """Initialize integrator.

        Args:
            db: MESDatabase instance
        """
        self.db = db
        self.clients: Dict[str, MESDataClient] = {}
        self.mqtt: Optional[MQTTDataCollector] = None

    async def register_opc_client(self, name: str, server_url: str) -> None:
        """Register OPC-UA client.

        Args:
            name: Client name
            server_url: OPC-UA server endpoint
        """
        client = OpcUAClient(server_url)
        await client.connect()
        self.clients[name] = client

    async def register_rest_client(self, name: str, base_url: str, api_key: Optional[str] = None) -> None:
        """Register REST API client.

        Args:
            name: Client name
            base_url: API base URL
            api_key: Optional API key
        """
        client = RestAPIClient(base_url, api_key)
        await client.connect()
        self.clients[name] = client

    def register_mqtt_collector(self, broker: str, port: int = 1883) -> None:
        """Register MQTT data collector.

        Args:
            broker: MQTT broker address
            port: MQTT broker port
        """
        self.mqtt = MQTTDataCollector(broker, port)
        self.mqtt.register_callback(self._on_mqtt_data)
        self.mqtt.connect()

    def _on_mqtt_data(self, equipment_id: str, param: EquipmentParameter) -> None:
        """Handle MQTT data updates."""
        asyncio.create_task(self.db.save_parameter(param))
        logger.debug(f"Received MQTT data: {equipment_id}/{param.parameter_name}={param.value}")

    async def collect_equipment_data(self, equipment_id: str, client_name: str) -> List[EquipmentParameter]:
        """Collect data from equipment.

        Args:
            equipment_id: Equipment identifier
            client_name: Registered client name

        Returns:
            List of collected parameters
        """
        if client_name not in self.clients:
            logger.error(f"Client not registered: {client_name}")
            return []

        client = self.clients[client_name]
        parameters = await client.get_parameters(equipment_id)

        # Persist parameters
        for param in parameters:
            await self.db.save_parameter(param)

        return parameters

    async def post_production_data(self, work_order: WorkOrder, client_name: str) -> bool:
        """Post production data to MES system.

        Args:
            work_order: WorkOrder to post
            client_name: REST API client name

        Returns:
            True if successful
        """
        if client_name not in self.clients:
            logger.error(f"Client not registered: {client_name}")
            return False

        client = self.clients[client_name]
        if not isinstance(client, RestAPIClient):
            logger.error(f"Client is not REST API: {client_name}")
            return False

        # Save locally first
        await self.db.save_work_order(work_order)

        # Post to MES system
        return await client.post_work_order(work_order)

    async def cleanup(self) -> None:
        """Clean up resources."""
        for client in self.clients.values():
            await client.disconnect()

        if self.mqtt:
            self.mqtt.disconnect()


# ==================== Example Usage ====================

async def main():
    """Example usage of MES integration."""

    # Initialize database
    db = MESDatabase("sqlite:///mes_data.db")
    db.create_tables()

    # Create integrator
    integrator = MESIntegrator(db)

    try:
        # Register data sources
        await integrator.register_rest_client(
            "main_mes",
            "http://localhost:8080/api",
            api_key="your-api-key"
        )

        integrator.register_mqtt_collector("mqtt.example.com", 1883)

        # Collect equipment data
        equipment_data = await integrator.collect_equipment_data(
            "Line1-Machine1",
            "main_mes"
        )

        logger.info(f"Collected {len(equipment_data)} parameters")

        # Create and post work order
        work_order = WorkOrder(
            work_order_id="WO-2024-001",
            product_id="Widget-A",
            target_quantity=500,
            scheduled_start=datetime.utcnow(),
            scheduled_end=datetime.utcnow() + timedelta(hours=2),
            equipment_id="Line1-Machine1",
            operator_id="john.smith",
            material_lot="Lot-2024-5670"
        )

        success = await integrator.post_production_data(work_order, "main_mes")
        logger.info(f"Work order post: {'successful' if success else 'failed'}")

        # Retrieve work order
        saved_order = await db.get_work_order("WO-2024-001")
        logger.info(f"Saved work order: {saved_order}")

        # Get parameter history
        history = await db.get_equipment_parameters(
            "Line1-Machine1",
            "temperature",
            hours_back=1
        )
        logger.info(f"Parameter history: {len(history)} records")

    finally:
        await integrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
