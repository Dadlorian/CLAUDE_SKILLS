"""
Unified Namespace (UNS) Implementation

This module provides a framework for implementing a Unified Namespace for Smart Factory
operations. The Unified Namespace acts as the single source of truth for all manufacturing
data, providing real-time visibility and eliminating data silos.

Key Features:
- MQTT-based hierarchical topic structure
- Message validation and data quality flagging
- Real-time data synchronization
- Subscription management
- Event-driven architecture
- Data persistence and archival

Author: Smart Factory Expert
Version: 1.0
"""

import json
import uuid
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
from datetime import datetime
import hashlib
import hmac


class DataQuality(Enum):
    """Data quality indicators"""
    CERTIFIED = "0_certified"      # Validated, ready for analysis
    SUSPECT = "1_suspect"          # Minor issues, use with caution
    BAD = "2_bad"                  # Invalid or missing
    UNKNOWN = "3_unknown"          # Cannot determine quality


class OperatingState(Enum):
    """Equipment operating states"""
    IDLE = "idle"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    ALARM = "alarm"
    STOPPED = "stopped"


@dataclass
class DataPoint:
    """
    Unified Namespace data point

    Attributes:
        namespace: Full MQTT topic path
        metric: Name of the metric
        timestamp: Unix timestamp in milliseconds
        value: The actual value
        unit: Unit of measurement
        quality: Data quality indicator
        source: Source identifier (sensor ID, system name)
        signature: HMAC signature for integrity verification
    """
    namespace: str
    metric: str
    timestamp: int
    value: Any
    unit: str
    quality: DataQuality = DataQuality.CERTIFIED
    source: str = ""
    signature: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "namespace": self.namespace,
            "metric": self.metric,
            "timestamp": self.timestamp,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality.value,
            "source": self.source,
            "signature": self.signature
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    def compute_signature(self, secret: str) -> str:
        """
        Compute HMAC-SHA256 signature for data integrity

        Args:
            secret: Shared secret for HMAC computation

        Returns:
            HMAC hex digest
        """
        data = f"{self.namespace}{self.metric}{self.timestamp}{self.value}{self.unit}"
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, secret: str) -> bool:
        """
        Verify data integrity using HMAC

        Args:
            secret: Shared secret for verification

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = self.compute_signature(secret)
        return hmac.compare_digest(self.signature, expected_signature)


@dataclass
class EquipmentMetadata:
    """Equipment metadata in the Unified Namespace"""
    equipment_id: str
    equipment_type: str
    manufacturer: str
    model: str
    serial_number: str
    location: str
    installation_date: str
    capabilities: List[str] = field(default_factory=list)
    maintenance_interval_hours: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


class UnifiedNamespaceManager:
    """
    Manager for Unified Namespace operations

    This class provides:
    - Topic hierarchy management
    - Data validation
    - Quality assurance
    - Subscription management
    - Event publishing
    """

    # MQTT topic hierarchy structure
    TOPIC_HIERARCHY = {
        "level_0": "factory",
        "level_1": "site",
        "level_2": "area",
        "level_3": "line",
        "level_4": "workstation",
        "level_5": "equipment",
        "level_6": "metric"
    }

    def __init__(self, secret_key: str = ""):
        """
        Initialize Unified Namespace Manager

        Args:
            secret_key: Secret key for HMAC signatures
        """
        self.secret_key = secret_key
        self.subscribers: Dict[str, List[Callable]] = {}  # topic -> [callbacks]
        self.data_store: Dict[str, DataPoint] = {}  # topic -> latest value
        self.metadata_store: Dict[str, EquipmentMetadata] = {}  # equipment_id -> metadata
        self.quality_rules: Dict[str, Dict] = {}  # metric -> validation rules
        self._setup_default_quality_rules()

    def _setup_default_quality_rules(self):
        """Setup default data quality validation rules"""
        self.quality_rules = {
            "temperature": {
                "min": -50,
                "max": 200,
                "rate_of_change": 10,  # degrees per minute
                "timeout_minutes": 5
            },
            "pressure": {
                "min": 0,
                "max": 1000,
                "rate_of_change": 50,  # bar per minute
                "timeout_minutes": 5
            },
            "vibration": {
                "min": 0,
                "max": 100,
                "rate_of_change": 30,  # mm/s per minute
                "timeout_minutes": 5
            },
            "throughput": {
                "min": 0,
                "max": 10000,
                "rate_of_change": 500,  # units per minute
                "timeout_minutes": 60
            }
        }

    def build_topic(self, site: str, area: str, line: str,
                   workstation: str, equipment: str, metric: str) -> str:
        """
        Build a full MQTT topic path

        Args:
            site: Site identifier
            area: Area identifier
            line: Production line identifier
            workstation: Workstation identifier
            equipment: Equipment identifier
            metric: Metric name

        Returns:
            Full topic path
        """
        return f"factory/{site}/{area}/{line}/{workstation}/{equipment}/{metric}"

    def register_equipment(self, equipment_id: str, metadata: EquipmentMetadata):
        """
        Register equipment metadata in the Unified Namespace

        Args:
            equipment_id: Unique equipment identifier
            metadata: Equipment metadata
        """
        self.metadata_store[equipment_id] = metadata

    def get_equipment_metadata(self, equipment_id: str) -> Optional[EquipmentMetadata]:
        """Retrieve equipment metadata"""
        return self.metadata_store.get(equipment_id)

    def validate_data_quality(self, topic: str, data_point: DataPoint) -> DataQuality:
        """
        Validate data quality based on rules

        Args:
            topic: MQTT topic
            data_point: Data point to validate

        Returns:
            Quality indicator
        """
        # Extract metric name from topic
        metric_name = topic.split("/")[-1]

        # Check if metric has validation rules
        if metric_name not in self.quality_rules:
            return DataQuality.CERTIFIED

        rules = self.quality_rules[metric_name]

        # Range validation
        if "min" in rules and data_point.value < rules["min"]:
            return DataQuality.BAD
        if "max" in rules and data_point.value > rules["max"]:
            return DataQuality.BAD

        # Rate of change validation
        if topic in self.data_store:
            previous = self.data_store[topic]
            time_delta_seconds = (data_point.timestamp - previous.timestamp) / 1000
            if time_delta_seconds > 0:
                value_delta = abs(data_point.value - previous.value)
                rate_of_change = value_delta / (time_delta_seconds / 60)

                if "rate_of_change" in rules:
                    if rate_of_change > rules["rate_of_change"]:
                        return DataQuality.SUSPECT

        return DataQuality.CERTIFIED

    def publish_data(self, topic: str, data_point: DataPoint) -> bool:
        """
        Publish data to the Unified Namespace

        Args:
            topic: MQTT topic
            data_point: Data point to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate quality
            quality = self.validate_data_quality(topic, data_point)
            data_point.quality = quality

            # Sign if secret key provided
            if self.secret_key:
                data_point.signature = data_point.compute_signature(self.secret_key)

            # Store in memory
            self.data_store[topic] = data_point

            # Notify subscribers
            self._notify_subscribers(topic, data_point)

            return True

        except Exception as e:
            print(f"Error publishing data: {e}")
            return False

    def subscribe(self, topic_pattern: str, callback: Callable):
        """
        Subscribe to topics matching a pattern

        Args:
            topic_pattern: MQTT topic pattern (supports wildcards + and #)
            callback: Function to call when data is published
        """
        if topic_pattern not in self.subscribers:
            self.subscribers[topic_pattern] = []
        self.subscribers[topic_pattern].append(callback)

    def _notify_subscribers(self, topic: str, data_point: DataPoint):
        """Notify subscribers of new data"""
        for pattern, callbacks in self.subscribers.items():
            if self._topic_matches(topic, pattern):
                for callback in callbacks:
                    try:
                        callback(topic, data_point)
                    except Exception as e:
                        print(f"Error in subscriber callback: {e}")

    @staticmethod
    def _topic_matches(topic: str, pattern: str) -> bool:
        """
        Check if topic matches MQTT pattern

        Args:
            topic: Actual topic
            pattern: Pattern with + (single level) and # (multiple levels)

        Returns:
            True if matches
        """
        topic_parts = topic.split("/")
        pattern_parts = pattern.split("/")

        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == "#":
                return True
            if i >= len(topic_parts):
                return False
            if pattern_part != "+" and pattern_part != topic_parts[i]:
                return False

        return len(topic_parts) == len(pattern_parts)

    def get_latest_value(self, topic: str) -> Optional[DataPoint]:
        """Get the latest value for a topic"""
        return self.data_store.get(topic)

    def get_metrics_for_equipment(self, equipment_id: str) -> Dict[str, DataPoint]:
        """
        Get all metrics for a specific equipment

        Args:
            equipment_id: Equipment identifier

        Returns:
            Dictionary of metric name -> DataPoint
        """
        prefix = equipment_id
        return {
            topic: data_point
            for topic, data_point in self.data_store.items()
            if prefix in topic
        }

    def export_data_snapshot(self, site: Optional[str] = None) -> Dict:
        """
        Export current data snapshot

        Args:
            site: Optional site filter

        Returns:
            Dictionary of all current data
        """
        snapshot = {
            "timestamp": int(time.time() * 1000),
            "data": {}
        }

        for topic, data_point in self.data_store.items():
            if site is None or f"/{site}/" in topic:
                snapshot["data"][topic] = data_point.to_dict()

        return snapshot

    def import_data_snapshot(self, snapshot: Dict):
        """Import a data snapshot"""
        for topic, data_dict in snapshot.get("data", {}).items():
            data_point = DataPoint(
                namespace=data_dict["namespace"],
                metric=data_dict["metric"],
                timestamp=data_dict["timestamp"],
                value=data_dict["value"],
                unit=data_dict["unit"],
                quality=DataQuality(data_dict.get("quality", "0_certified")),
                source=data_dict.get("source", ""),
                signature=data_dict.get("signature", "")
            )
            self.data_store[topic] = data_point

    def get_equipment_status_summary(self, site: str, area: str) -> Dict:
        """
        Get summary of equipment status in an area

        Args:
            site: Site identifier
            area: Area identifier

        Returns:
            Summary of equipment statuses
        """
        prefix = f"factory/{site}/{area}"
        summary = {
            "total_equipment": 0,
            "running": 0,
            "idle": 0,
            "alarm": 0,
            "maintenance": 0,
            "equipment_details": []
        }

        equipment_states = {}

        for topic, data_point in self.data_store.items():
            if prefix in topic and "state" in topic:
                parts = topic.split("/")
                equipment_id = parts[5] if len(parts) > 5 else "unknown"

                if equipment_id not in equipment_states:
                    equipment_states[equipment_id] = {
                        "equipment_id": equipment_id,
                        "state": data_point.value,
                        "timestamp": data_point.timestamp,
                        "metrics": {}
                    }
                    summary["total_equipment"] += 1

                # Count by state
                state_value = str(data_point.value).lower()
                if state_value == "running":
                    summary["running"] += 1
                elif state_value == "idle":
                    summary["idle"] += 1
                elif state_value == "alarm":
                    summary["alarm"] += 1
                elif state_value == "maintenance":
                    summary["maintenance"] += 1

        summary["equipment_details"] = list(equipment_states.values())
        return summary


# Example usage and demonstration
if __name__ == "__main__":

    # Initialize Unified Namespace Manager
    uns = UnifiedNamespaceManager(secret_key="smart_factory_secret_2024")

    # Register equipment
    press_metadata = EquipmentMetadata(
        equipment_id="PRESS_001",
        equipment_type="Hydraulic Press",
        manufacturer="Siemens",
        model="SIPRESS 2000",
        serial_number="SN123456",
        location="Site A, Area 1, Line 1",
        installation_date="2018-03-15",
        capabilities=["pressure_monitoring", "temperature_monitoring", "predictive_maintenance"],
        maintenance_interval_hours=500
    )
    uns.register_equipment("PRESS_001", press_metadata)

    # Define topic
    topic = uns.build_topic(
        site="site_A",
        area="area_1",
        line="line_1",
        workstation="station_01",
        equipment="press_001",
        metric="temperature"
    )

    # Subscribe to updates
    def temperature_alert_handler(topic: str, data_point: DataPoint):
        if data_point.value > 80:
            print(f"ALERT: High temperature {data_point.value}°C on {topic}")

    uns.subscribe("factory/site_A/area_1/line_1/station_01/press_001/+",
                  temperature_alert_handler)

    # Publish sample data
    print("Publishing sample data...")
    for temp in [25.0, 30.5, 40.2, 75.8, 82.3]:
        data_point = DataPoint(
            namespace="factory/site_A/area_1/line_1/station_01/press_001",
            metric="temperature",
            timestamp=int(time.time() * 1000),
            value=temp,
            unit="celsius",
            source="sensor_temp_01"
        )
        uns.publish_data(topic, data_point)
        time.sleep(0.1)

    # Get latest value
    latest = uns.get_latest_value(topic)
    print(f"\nLatest temperature: {latest.value}°C (Quality: {latest.quality.value})")

    # Get equipment summary
    summary = uns.get_equipment_status_summary("site_A", "area_1")
    print(f"\nEquipment Summary: {json.dumps(summary, indent=2)}")
