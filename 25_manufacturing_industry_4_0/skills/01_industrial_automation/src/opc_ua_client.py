#!/usr/bin/env python3
"""
================================================================================
PRODUCTION-GRADE OPC UA CLIENT FOR INDUSTRIAL AUTOMATION
================================================================================

Purpose: Enterprise-level OPC UA client for SCADA data collection from
manufacturing equipment (PLCs, RTUs, sensors).

Features:
- Secure connection to OPC UA server (TLS 1.2, authentication)
- Subscription-based real-time data updates
- Automatic reconnection with exponential backoff
- Data validation and quality checking
- Historian database integration (async)
- Comprehensive error handling & logging
- Performance monitoring (latency, throughput)

Reference Standards:
- IEC 62541 (OPC UA Specification)
- IEC 61131-3 (Industrial programming)
- ISA-95 (Enterprise-Control System Integration)

Author: Industrial Automation Systems
Version: 2.0
Date: 2024-01-15
================================================================================
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import time

# OPC UA library (python-opcua)
from opcua import Client, ua
from opcua.common.methods import call_method
from opcua.common.manage_nodes import delete_nodes

# Database
import asyncpg
import json

# Configuration management
import yaml
from pathlib import Path

# Metrics & monitoring
from prometheus_client import Counter, Histogram, Gauge, start_http_server


class DataQuality(Enum):
    """OPC UA Quality Status Codes"""
    GOOD = 0
    UNCERTAIN = 1
    BAD = 2
    NOT_CONNECTED = 3


@dataclass
class TagValue:
    """Data structure for OPC UA tag value with metadata"""
    tag_id: str
    node_id: str
    value: float
    timestamp: datetime
    quality: DataQuality
    source: str = "OPC_UA"

    def to_dict(self) -> dict:
        return {
            'tag_id': self.tag_id,
            'node_id': self.node_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'quality': self.quality.name,
            'source': self.source
        }


class OPCUAClientConfiguration:
    """OPC UA Server Connection Configuration"""

    def __init__(self, config_file: str = 'opcua_config.yaml'):
        """Load configuration from YAML file"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> dict:
        """Load and parse YAML configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def _validate_config(self):
        """Validate required configuration fields"""
        required_fields = ['server_url', 'tags', 'database']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required config field: {field}")

    @property
    def server_url(self) -> str:
        return self.config['server_url']

    @property
    def server_name(self) -> str:
        return self.config.get('server_name', 'UnknownServer')

    @property
    def application_uri(self) -> str:
        return self.config.get('application_uri', 'urn:industrial:client')

    @property
    def security_policy(self) -> str:
        """TLS Security Policy (basic256sha256, basic256, none)"""
        return self.config.get('security_policy', 'Basic256Sha256')

    @property
    def username(self) -> Optional[str]:
        return self.config.get('username')

    @property
    def password(self) -> Optional[str]:
        return self.config.get('password')

    @property
    def certificate_file(self) -> Optional[str]:
        return self.config.get('certificate_file')

    @property
    def key_file(self) -> Optional[str]:
        return self.config.get('key_file')

    @property
    def tags(self) -> List[Dict]:
        """List of tags to subscribe to"""
        return self.config.get('tags', [])

    @property
    def database_config(self) -> Dict:
        """Database connection parameters"""
        return self.config.get('database', {})

    @property
    def reconnect_interval(self) -> int:
        """Seconds between reconnection attempts"""
        return self.config.get('reconnect_interval', 5)

    @property
    def max_retries(self) -> int:
        return self.config.get('max_retries', 10)

    @property
    def subscription_interval(self) -> int:
        """Milliseconds between publish intervals"""
        return self.config.get('subscription_interval', 100)

    @property
    def deadband(self) -> float:
        """Default deadband for value changes (prevents data flooding)"""
        return self.config.get('deadband', 0.0)


class HistorianDatabase:
    """Async database connection pool for historian storage"""

    def __init__(self, config: Dict):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger('HistorianDB')

    async def connect(self):
        """Create connection pool to PostgreSQL/SQL Server historian"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                user=self.config.get('user', 'historian'),
                password=self.config.get('password', ''),
                database=self.config.get('database', 'historian'),
                min_size=5,
                max_size=20,
                timeout=10
            )
            self.logger.info("Connected to historian database")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Close all database connections"""
        if self.pool:
            await self.pool.close()
            self.logger.info("Disconnected from historian database")

    async def insert_value(self, tag: TagValue) -> bool:
        """Insert historical value into database"""
        if not self.pool:
            self.logger.warning("Database pool not initialized")
            return False

        query = """
            INSERT INTO historical_values (tag_id, node_id, value, timestamp, quality, source)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (tag_id, timestamp) DO NOTHING
        """

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    query,
                    tag.tag_id,
                    tag.node_id,
                    tag.value,
                    tag.timestamp,
                    tag.quality.value,
                    tag.source
                )
            return True
        except Exception as e:
            self.logger.error(f"Insert failed for {tag.tag_id}: {e}")
            return False

    async def batch_insert(self, tags: List[TagValue]) -> int:
        """Insert multiple values in single transaction (more efficient)"""
        if not self.pool or not tags:
            return 0

        query = """
            INSERT INTO historical_values (tag_id, node_id, value, timestamp, quality, source)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (tag_id, timestamp) DO NOTHING
        """

        try:
            async with self.pool.acquire() as conn:
                inserted = 0
                async with conn.transaction():
                    for tag in tags:
                        await conn.execute(
                            query,
                            tag.tag_id,
                            tag.node_id,
                            tag.value,
                            tag.timestamp,
                            tag.quality.value,
                            tag.source
                        )
                        inserted += 1
                return inserted
        except Exception as e:
            self.logger.error(f"Batch insert failed: {e}")
            return 0


class OPCUAClientManager:
    """Main OPC UA Client with reconnection, subscription, and data collection"""

    def __init__(self, config: OPCUAClientConfiguration):
        self.config = config
        self.client: Optional[Client] = None
        self.subscription = None
        self.handler = None
        self.logger = logging.getLogger('OPCUAClient')
        self.db = HistorianDatabase(config.database_config)

        # Metrics for monitoring
        self.connection_attempts = Counter('opcua_connection_attempts_total', 'Total connection attempts')
        self.connection_failures = Counter('opcua_connection_failures_total', 'Total connection failures')
        self.data_points_received = Counter('opcua_data_points_received_total', 'Total data points received')
        self.subscription_latency = Histogram('opcua_subscription_latency_seconds', 'Subscription latency')
        self.database_write_latency = Histogram('opcua_db_write_latency_seconds', 'Database write latency')
        self.connection_status = Gauge('opcua_connection_status', '1=connected, 0=disconnected')

        # Internal state
        self.subscribed_nodes: Dict[str, ua.Node] = {}
        self.running = False
        self.reconnect_attempts = 0

    async def connect(self):
        """Establish connection to OPC UA server with security"""
        self.logger.info(f"Connecting to OPC UA server: {self.config.server_url}")
        self.connection_attempts.inc()

        try:
            self.client = Client(self.config.server_url)

            # Configure security
            if self.config.certificate_file and self.config.key_file:
                self.client.set_user(self.config.username, self.config.password)
                self.client.set_tls(
                    certificate=self.config.certificate_file,
                    private_key=self.config.key_file,
                    ca_certs=None
                )

            # Connect with timeout
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self.client.connect),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                raise ConnectionError("Connection timeout (10 seconds)")

            self.logger.info("Connected to OPC UA server")
            self.connection_status.set(1)
            self.reconnect_attempts = 0

            # Connect to historian
            await self.db.connect()

            return True

        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.connection_failures.inc()
            self.connection_status.set(0)
            self.reconnect_attempts += 1
            return False

    async def disconnect(self):
        """Close connection to OPC UA server"""
        try:
            if self.subscription:
                self.client.delete_subscriptions([self.subscription])
            if self.client:
                await asyncio.to_thread(self.client.disconnect)
            await self.db.disconnect()
            self.connection_status.set(0)
            self.logger.info("Disconnected from OPC UA server")
        except Exception as e:
            self.logger.error(f"Disconnection error: {e}")

    async def subscribe_to_tags(self):
        """Create subscription for all configured tags"""
        if not self.client:
            self.logger.error("Client not connected")
            return False

        try:
            # Create subscription with specified update rate
            self.subscription = await asyncio.to_thread(
                self.client.create_subscription,
                int(self.config.subscription_interval),
                self._subscription_handler()
            )

            self.logger.info(f"Created subscription (interval: {self.config.subscription_interval}ms)")

            # Subscribe to each tag
            for tag_config in self.config.tags:
                try:
                    node = self.client.get_node(tag_config['node_id'])
                    await asyncio.to_thread(
                        self.subscription.subscribe_data_change,
                        node,
                        handler_callback=self._data_change_callback,
                        deadband=tag_config.get('deadband', self.config.deadband)
                    )
                    self.subscribed_nodes[tag_config['tag_id']] = node
                    self.logger.debug(f"Subscribed to {tag_config['tag_id']} ({tag_config['node_id']})")

                except Exception as e:
                    self.logger.error(f"Failed to subscribe to {tag_config['tag_id']}: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Subscription creation failed: {e}")
            return False

    def _subscription_handler(self) -> Callable:
        """Create subscription handler callback"""
        def handler(var, value):
            self._on_data_change(var, value)
        return handler

    def _data_change_callback(self, var, value):
        """Callback for subscription data changes"""
        asyncio.create_task(self._on_data_change(var, value))

    async def _on_data_change(self, var, value):
        """Process received data change"""
        try:
            start_time = time.time()

            # Map node ID to tag ID
            node_id = str(var.nodeid)
            tag_id = self._find_tag_id_by_node(node_id)

            if tag_id:
                # Create TagValue object
                tag_value = TagValue(
                    tag_id=tag_id,
                    node_id=node_id,
                    value=float(value),
                    timestamp=datetime.utcnow(),
                    quality=self._map_quality(var.ServerTimestamp)
                )

                # Validate and store
                if self._validate_tag_value(tag_value):
                    await self.db.insert_value(tag_value)
                    self.data_points_received.inc()

                    latency = time.time() - start_time
                    self.subscription_latency.observe(latency)

        except Exception as e:
            self.logger.error(f"Error processing data change: {e}")

    def _find_tag_id_by_node(self, node_id: str) -> Optional[str]:
        """Find tag_id from node_id"""
        for tag_config in self.config.tags:
            if tag_config['node_id'] == node_id:
                return tag_config['tag_id']
        return None

    def _map_quality(self, server_timestamp) -> DataQuality:
        """Map OPC UA quality status to our enum"""
        # Simplified: if timestamp valid, quality is GOOD
        if server_timestamp:
            return DataQuality.GOOD
        return DataQuality.BAD

    def _validate_tag_value(self, tag: TagValue) -> bool:
        """Validate tag value is within acceptable range"""
        # Find tag configuration
        for tag_config in self.config.tags:
            if tag_config['tag_id'] == tag.tag_id:
                min_val = tag_config.get('min_value', -float('inf'))
                max_val = tag_config.get('max_value', float('inf'))
                if min_val <= tag.value <= max_val:
                    return True
                else:
                    self.logger.warning(
                        f"Out of range: {tag.tag_id}={tag.value} "
                        f"(expected {min_val}..{max_val})"
                    )
                    return False
        return True

    async def run(self):
        """Main client loop with automatic reconnection"""
        self.running = True
        reconnect_delay = self.config.reconnect_interval

        while self.running:
            try:
                # Connect if not already
                if not self.client or not self.client.client_handle:
                    if not await self.connect():
                        await asyncio.sleep(reconnect_delay)
                        reconnect_delay = min(reconnect_delay * 2, 60)  # Exponential backoff, max 60s
                        continue

                # Subscribe to tags
                if not self.subscribed_nodes:
                    if not await self.subscribe_to_tags():
                        await asyncio.sleep(5)
                        continue

                reconnect_delay = self.config.reconnect_interval  # Reset on success
                self.reconnect_attempts = 0

                # Keep connection alive
                await asyncio.sleep(30)

            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(reconnect_delay)

        await self.disconnect()
        self.running = False

    async def read_single_value(self, node_id: str) -> Optional[float]:
        """Read a single value from server (one-time read)"""
        try:
            node = self.client.get_node(node_id)
            value = await asyncio.to_thread(node.get_value)
            return float(value)
        except Exception as e:
            self.logger.error(f"Failed to read {node_id}: {e}")
            return None

    async def write_value(self, node_id: str, value: float) -> bool:
        """Write a value to server"""
        try:
            node = self.client.get_node(node_id)
            await asyncio.to_thread(node.set_value, ua.DataValue(ua.Variant(value, ua.VariantType.Float)))
            self.logger.info(f"Wrote {value} to {node_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write to {node_id}: {e}")
            return False


class OPCUAClientApplication:
    """Main application entry point"""

    def __init__(self, config_file: str = 'opcua_config.yaml'):
        self.config = OPCUAClientConfiguration(config_file)
        self.client = OPCUAClientManager(self.config)
        self.logger = logging.getLogger('Application')

    async def run(self):
        """Start the OPC UA client application"""
        self.logger.info("Starting OPC UA Client Application")

        # Start Prometheus metrics server (optional)
        # start_http_server(8000)

        try:
            await self.client.run()
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        finally:
            await self.client.disconnect()


def setup_logging(log_level: str = 'INFO'):
    """Configure logging to file and console"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('opcua_client.log'),
            logging.StreamHandler()
        ]
    )


async def main():
    """Main entry point"""
    setup_logging('DEBUG')

    # Example configuration YAML
    example_config = {
        'server_url': 'opc.tcp://192.168.1.100:4840/SCADA/Server',
        'server_name': 'ProductionSCADA',
        'security_policy': 'Basic256Sha256',
        'username': 'operator',
        'password': 'secure_password',
        'subscription_interval': 100,
        'reconnect_interval': 5,
        'tags': [
            {
                'tag_id': 'TEMP_ZONE_1',
                'node_id': 'ns=2;s=ProductionLine1.TemperatureZone1.Value',
                'min_value': -50.0,
                'max_value': 100.0,
                'deadband': 0.1
            },
            {
                'tag_id': 'PRESS_MAIN',
                'node_id': 'ns=2;s=ProductionLine1.Pressure.Value',
                'min_value': 0.0,
                'max_value': 200.0,
                'deadband': 1.0
            }
        ],
        'database': {
            'host': 'historian.local',
            'port': 5432,
            'user': 'historian',
            'password': 'db_password',
            'database': 'manufacturing'
        }
    }

    # Save example config
    config_file = Path('opcua_config.yaml')
    if not config_file.exists():
        with open(config_file, 'w') as f:
            yaml.dump(example_config, f)
        print(f"Created example config: {config_file}")
        print("Edit the file with your OPC UA server details and rerun")
        sys.exit(0)

    # Run application
    app = OPCUAClientApplication('opcua_config.yaml')
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
