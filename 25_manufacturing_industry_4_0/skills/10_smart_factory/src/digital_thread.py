"""
Digital Thread Implementation

This module provides a framework for implementing a Digital Thread in Smart Factory
operations. The Digital Thread is the connected flow of product, process, and equipment
data across the entire value stream from design through production, service, and disposal.

Key Features:
- Product lineage tracking
- Complete audit trail
- Multi-dimensional data linking
- Real-time event logging
- Advanced traceability
- Compliance and auditing
- Root cause analysis support

Author: Smart Factory Expert
Version: 1.0
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class EventType(Enum):
    """Digital Thread event types"""
    DESIGN_CREATED = "design_created"
    DESIGN_APPROVED = "design_approved"
    BOM_CREATED = "bom_created"
    WORK_ORDER_CREATED = "work_order_created"
    PRODUCTION_STARTED = "production_started"
    QUALITY_CHECK = "quality_check"
    DEFECT_DETECTED = "defect_detected"
    REWORK_STARTED = "rework_started"
    REWORK_COMPLETED = "rework_completed"
    PRODUCTION_COMPLETED = "production_completed"
    SHIPPED = "shipped"
    SERVICE_EVENT = "service_event"
    END_OF_LIFE = "end_of_life"


class QualityStatus(Enum):
    """Product quality status"""
    PENDING = "pending"
    GOOD = "good"
    SUSPECT = "suspect"
    DEFECTIVE = "defective"
    REWORKED = "reworked"
    SCRAPPED = "scrapped"


@dataclass
class ProductDesign:
    """Design phase information"""
    design_id: str
    product_name: str
    version: str
    creation_date: str
    designer: str
    specifications: Dict[str, Any] = field(default_factory=dict)
    bom_id: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class WorkOrder:
    """Production work order"""
    work_order_id: str
    product_id: str
    design_id: str
    quantity: int
    scheduled_start: str
    scheduled_end: str
    equipment_assignment: Dict[str, str] = field(default_factory=dict)  # workstation -> equipment_id
    operator: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProductInstance:
    """Individual product instance in production"""
    product_id: str
    product_name: str
    serial_number: str
    work_order_id: str
    design_id: str
    batch_id: str
    created_timestamp: int

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DigitalThreadEvent:
    """
    Event in the Digital Thread

    Represents a significant event in a product's lifecycle
    """
    event_id: str
    product_id: str
    event_type: EventType
    timestamp: int
    location: str  # Site/Area/Line/Workstation
    equipment_id: str
    operator_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    quality_status: QualityStatus = QualityStatus.PENDING
    notes: str = ""
    related_events: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data_copy = asdict(self)
        data_copy["event_type"] = self.event_type.value
        data_copy["quality_status"] = self.quality_status.value
        return data_copy

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class QualityMeasurement:
    """Quality measurement/inspection result"""
    measurement_id: str
    product_id: str
    measurement_timestamp: int
    location: str
    equipment_id: str
    parameter_name: str
    measured_value: float
    specification_min: float
    specification_max: float
    unit: str
    measurement_device: str = ""
    status: QualityStatus = QualityStatus.PENDING

    @property
    def is_in_spec(self) -> bool:
        """Check if measurement is within specification"""
        return self.specification_min <= self.measured_value <= self.specification_max

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class MaintenanceRecord:
    """Equipment maintenance record linked to production"""
    maintenance_id: str
    equipment_id: str
    timestamp: int
    maintenance_type: str  # preventive, corrective, predictive
    description: str
    technician: str
    duration_minutes: int
    affected_products: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class DigitalThreadManager:
    """
    Manager for Digital Thread operations

    Maintains the complete lineage and history of products through manufacturing
    """

    def __init__(self):
        """Initialize Digital Thread Manager"""
        self.products: Dict[str, ProductInstance] = {}  # product_id -> ProductInstance
        self.events: Dict[str, List[DigitalThreadEvent]] = {}  # product_id -> [events]
        self.designs: Dict[str, ProductDesign] = {}  # design_id -> ProductDesign
        self.work_orders: Dict[str, WorkOrder] = {}  # work_order_id -> WorkOrder
        self.quality_measurements: Dict[str, List[QualityMeasurement]] = {}  # product_id -> [measurements]
        self.maintenance_records: List[MaintenanceRecord] = []

    def register_product_design(self, design: ProductDesign):
        """
        Register a product design

        Args:
            design: Product design information
        """
        self.designs[design.design_id] = design

    def create_work_order(self, work_order: WorkOrder):
        """
        Create a work order for production

        Args:
            work_order: Work order details
        """
        self.work_orders[work_order.work_order_id] = work_order

    def create_product_instance(self, product: ProductInstance) -> str:
        """
        Create a new product instance (physical unit)

        Args:
            product: Product instance information

        Returns:
            Product ID for the created instance
        """
        self.products[product.product_id] = product
        self.events[product.product_id] = []
        self.quality_measurements[product.product_id] = []

        # Log creation event
        creation_event = DigitalThreadEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            event_type=EventType.DESIGN_CREATED,
            timestamp=product.created_timestamp,
            location="manufacturing",
            equipment_id="",
            operator_id="",
            data={
                "serial_number": product.serial_number,
                "batch_id": product.batch_id,
                "design_id": product.design_id
            }
        )
        self.log_event(creation_event)

        return product.product_id

    def log_event(self, event: DigitalThreadEvent):
        """
        Log an event in the Digital Thread

        Args:
            event: Event to log
        """
        if event.product_id not in self.events:
            self.events[event.product_id] = []

        self.events[event.product_id].append(event)

    def log_quality_measurement(self, measurement: QualityMeasurement):
        """
        Log a quality measurement

        Args:
            measurement: Quality measurement
        """
        if measurement.product_id not in self.quality_measurements:
            self.quality_measurements[measurement.product_id] = []

        self.quality_measurements[measurement.product_id].append(measurement)

        # Determine quality status based on measurement
        if measurement.is_in_spec:
            measurement.status = QualityStatus.GOOD
        else:
            measurement.status = QualityStatus.DEFECTIVE

        # Log quality check event
        quality_event = DigitalThreadEvent(
            event_id=str(uuid.uuid4()),
            product_id=measurement.product_id,
            event_type=EventType.QUALITY_CHECK,
            timestamp=measurement.measurement_timestamp,
            location=measurement.location,
            equipment_id=measurement.equipment_id,
            operator_id="",
            data={
                "parameter": measurement.parameter_name,
                "value": measurement.measured_value,
                "min": measurement.specification_min,
                "max": measurement.specification_max,
                "unit": measurement.unit
            },
            quality_status=measurement.status
        )
        self.log_event(quality_event)

    def log_maintenance(self, maintenance: MaintenanceRecord):
        """
        Log maintenance activity

        Args:
            maintenance: Maintenance record
        """
        self.maintenance_records.append(maintenance)

        # Link maintenance to affected products
        for product_id in maintenance.affected_products:
            if product_id in self.events:
                maintenance_event = DigitalThreadEvent(
                    event_id=str(uuid.uuid4()),
                    product_id=product_id,
                    event_type=EventType.SERVICE_EVENT,
                    timestamp=maintenance.timestamp,
                    location="",
                    equipment_id=maintenance.equipment_id,
                    operator_id=maintenance.technician,
                    data={
                        "maintenance_id": maintenance.maintenance_id,
                        "maintenance_type": maintenance.maintenance_type,
                        "duration_minutes": maintenance.duration_minutes
                    },
                    notes=maintenance.description
                )
                self.log_event(maintenance_event)

    def get_product_history(self, product_id: str) -> Dict[str, Any]:
        """
        Get complete history for a product

        Args:
            product_id: Product identifier

        Returns:
            Complete product history
        """
        if product_id not in self.products:
            return {}

        product = self.products[product_id]
        events = self.events.get(product_id, [])
        measurements = self.quality_measurements.get(product_id, [])

        # Determine overall quality status
        quality_status = QualityStatus.GOOD
        if any(m.status == QualityStatus.DEFECTIVE for m in measurements):
            quality_status = QualityStatus.DEFECTIVE
        elif any(m.status == QualityStatus.SUSPECT for m in measurements):
            quality_status = QualityStatus.SUSPECT

        return {
            "product": product.to_dict(),
            "quality_status": quality_status.value,
            "events": [event.to_dict() for event in sorted(
                events,
                key=lambda e: e.timestamp
            )],
            "quality_measurements": [m.to_dict() for m in measurements],
            "event_timeline": self._build_timeline(product_id)
        }

    def _build_timeline(self, product_id: str) -> List[Dict]:
        """Build a chronological timeline of events"""
        events = self.events.get(product_id, [])
        timeline = []

        for event in sorted(events, key=lambda e: e.timestamp):
            timeline.append({
                "timestamp": datetime.fromtimestamp(event.timestamp / 1000).isoformat(),
                "event_type": event.event_type.value,
                "location": event.location,
                "equipment_id": event.equipment_id,
                "details": event.data
            })

        return timeline

    def get_root_cause_analysis(self, product_id: str) -> Dict[str, Any]:
        """
        Perform root cause analysis for a defective product

        Args:
            product_id: Product identifier

        Returns:
            Root cause analysis results
        """
        history = self.get_product_history(product_id)

        if not history:
            return {"status": "product_not_found"}

        # Find quality issues
        defective_measurements = [
            m for m in history.get("quality_measurements", [])
            if QualityStatus(m["status"]) == QualityStatus.DEFECTIVE
        ]

        if not defective_measurements:
            return {"status": "no_defects_found"}

        # Trace back to production events
        analysis = {
            "product_id": product_id,
            "defective_measurements": defective_measurements,
            "related_events": [],
            "potential_causes": [],
            "equipment_involved": set(),
            "operators_involved": set(),
            "timeline": history.get("event_timeline", [])
        }

        # Find related production events
        for event in history.get("events", []):
            if event["event_type"] in ["production_started", "production_completed"]:
                analysis["related_events"].append(event)
                if event.get("equipment_id"):
                    analysis["equipment_involved"].add(event["equipment_id"])
                if event.get("operator_id"):
                    analysis["operators_involved"].add(event["operator_id"])

        # Suggest potential causes based on equipment and parameters
        defective_param = defective_measurements[0].get("parameter")
        if defective_param == "temperature":
            analysis["potential_causes"].append("Temperature control failure")
        elif defective_param == "pressure":
            analysis["potential_causes"].append("Pressure regulation failure")
        elif defective_param == "dimension":
            analysis["potential_causes"].append("Tool wear or calibration drift")
        elif defective_param == "surface_finish":
            analysis["potential_causes"].append("Tool condition degradation")

        # Convert sets to lists for JSON serialization
        analysis["equipment_involved"] = list(analysis["equipment_involved"])
        analysis["operators_involved"] = list(analysis["operators_involved"])

        return analysis

    def trace_supplier_quality(self, product_id: str) -> Dict[str, Any]:
        """
        Trace quality back to supplier materials

        Args:
            product_id: Product identifier

        Returns:
            Supplier quality information
        """
        product = self.products.get(product_id)
        if not product:
            return {}

        work_order = self.work_orders.get(product.work_order_id)
        if not work_order:
            return {}

        # In a full implementation, this would query supplier quality data
        # and material certifications linked to the batch
        return {
            "product_id": product_id,
            "batch_id": product.batch_id,
            "work_order_id": work_order.work_order_id,
            "design_id": product.design_id,
            "note": "Supplier traceability would query material certifications"
        }

    def generate_traceability_report(self, batch_id: str) -> Dict[str, Any]:
        """
        Generate traceability report for entire batch

        Args:
            batch_id: Batch identifier

        Returns:
            Batch traceability report
        """
        batch_products = [
            p for p in self.products.values()
            if p.batch_id == batch_id
        ]

        report = {
            "batch_id": batch_id,
            "total_units": len(batch_products),
            "product_summary": {},
            "quality_summary": {},
            "defect_summary": {}
        }

        for product in batch_products:
            measurements = self.quality_measurements.get(product.product_id, [])

            # Count by status
            good_count = sum(1 for m in measurements if m.is_in_spec)
            defect_count = sum(1 for m in measurements if not m.is_in_spec)

            report["product_summary"][product.product_id] = {
                "serial_number": product.serial_number,
                "good_measurements": good_count,
                "defect_measurements": defect_count
            }

        # Calculate totals
        total_good = sum(
            p.get("good_measurements", 0)
            for p in report["product_summary"].values()
        )
        total_defect = sum(
            p.get("defect_measurements", 0)
            for p in report["product_summary"].values()
        )

        report["quality_summary"] = {
            "total_measurements": total_good + total_defect,
            "good": total_good,
            "defect": total_defect,
            "yield": f"{total_good / (total_good + total_defect) * 100:.1f}%"
        }

        return report

    def export_digital_thread(self, product_id: str) -> str:
        """
        Export Digital Thread as JSON for archival/transmission

        Args:
            product_id: Product identifier

        Returns:
            JSON representation of Digital Thread
        """
        history = self.get_product_history(product_id)
        return json.dumps(history, indent=2)

    def get_equipment_impact_analysis(self, equipment_id: str,
                                     start_timestamp: int,
                                     end_timestamp: int) -> Dict[str, Any]:
        """
        Analyze impact of equipment issues on product quality

        Args:
            equipment_id: Equipment identifier
            start_timestamp: Analysis start time (milliseconds)
            end_timestamp: Analysis end time (milliseconds)

        Returns:
            Impact analysis results
        """
        affected_products = []
        defect_count = 0

        # Find all products affected by this equipment during time window
        for product_id, events in self.events.items():
            for event in events:
                if (event.equipment_id == equipment_id and
                    start_timestamp <= event.timestamp <= end_timestamp):
                    affected_products.append(product_id)
                    break

        # Check quality of affected products
        for product_id in affected_products:
            measurements = self.quality_measurements.get(product_id, [])
            defects = [m for m in measurements if not m.is_in_spec]
            defect_count += len(defects)

        return {
            "equipment_id": equipment_id,
            "analysis_period": {
                "start": start_timestamp,
                "end": end_timestamp
            },
            "affected_products": affected_products,
            "total_affected": len(affected_products),
            "defects_detected": defect_count,
            "defect_rate": f"{defect_count / len(affected_products) * 100:.1f}%" if affected_products else "N/A"
        }


# Example usage and demonstration
if __name__ == "__main__":

    # Initialize Digital Thread Manager
    dtm = DigitalThreadManager()

    # Register product design
    design = ProductDesign(
        design_id="DESIGN_001",
        product_name="Hydraulic Valve Assembly",
        version="2.1",
        creation_date="2024-01-15",
        designer="John Smith",
        specifications={
            "max_pressure": 350,
            "flow_rate": "25 l/min",
            "material": "Ductile Iron",
            "surface_finish": "Ra 0.8"
        }
    )
    dtm.register_product_design(design)

    # Create work order
    work_order = WorkOrder(
        work_order_id="WO_20241119_001",
        product_id="PROD_001_BATCH_001",
        design_id="DESIGN_001",
        quantity=100,
        scheduled_start="2024-11-19 08:00",
        scheduled_end="2024-11-19 16:00",
        equipment_assignment={
            "workstation_1": "MILL_001",
            "workstation_2": "BORE_001",
            "workstation_3": "TEST_001"
        },
        operator="Jane Doe",
        parameters={
            "spindle_speed": 1200,
            "feed_rate": 200,
            "coolant": "standard"
        }
    )
    dtm.create_work_order(work_order)

    # Create product instance
    product = ProductInstance(
        product_id="PROD_001_001",
        product_name="Hydraulic Valve Assembly",
        serial_number="HVA-2024-001",
        work_order_id="WO_20241119_001",
        design_id="DESIGN_001",
        batch_id="BATCH_001",
        created_timestamp=int(datetime.now().timestamp() * 1000)
    )
    dtm.create_product_instance(product)

    # Log quality measurements
    measurements = [
        QualityMeasurement(
            measurement_id="QM_001",
            product_id="PROD_001_001",
            measurement_timestamp=int(datetime.now().timestamp() * 1000),
            location="Area A, Line 1, Station 3",
            equipment_id="TEST_001",
            parameter_name="pressure",
            measured_value=345,
            specification_min=340,
            specification_max=360,
            unit="bar"
        ),
        QualityMeasurement(
            measurement_id="QM_002",
            product_id="PROD_001_001",
            measurement_timestamp=int(datetime.now().timestamp() * 1000),
            location="Area A, Line 1, Station 2",
            equipment_id="BORE_001",
            parameter_name="dimension",
            measured_value=25.02,
            specification_min=25.00,
            specification_max=25.05,
            unit="mm"
        )
    ]

    for measurement in measurements:
        dtm.log_quality_measurement(measurement)

    # Get product history
    history = dtm.get_product_history("PROD_001_001")
    print("Product History:")
    print(json.dumps(history, indent=2))

    # Generate traceability report
    print("\nTraceability Report:")
    report = dtm.generate_traceability_report("BATCH_001")
    print(json.dumps(report, indent=2))
