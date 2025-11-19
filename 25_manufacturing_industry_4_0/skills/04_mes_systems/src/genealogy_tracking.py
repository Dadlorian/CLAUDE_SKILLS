"""
Product Genealogy Tracking Module
Comprehensive forward and backward traceability for manufacturing.
Enables impact analysis for defects, recalls, and compliance investigations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenealogyDirection(Enum):
    """Direction of genealogy query."""
    FORWARD = "forward"  # Materials → Finished Product
    BACKWARD = "backward"  # Finished Product → Materials


class MaterialType(Enum):
    """Type of material in genealogy."""
    RAW_MATERIAL = "raw_material"
    COMPONENT = "component"
    SUBASSEMBLY = "subassembly"
    FINISHED_PRODUCT = "finished_product"
    CONSUMABLE = "consumable"


@dataclass
class MaterialLot:
    """Material lot or batch."""
    lot_number: str
    material_id: str
    material_description: str
    material_type: MaterialType
    supplier_id: Optional[str] = None
    received_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    quantity_received: float = 0.0
    unit: str = "units"
    specification_version: str = ""
    quarantined: bool = False
    quarantine_reason: Optional[str] = None

    def is_expired(self, check_date: datetime = None) -> bool:
        """Check if lot is expired.

        Args:
            check_date: Date to check against (default: now)

        Returns:
            True if lot is expired
        """
        if not self.expiration_date:
            return False
        if check_date is None:
            check_date = datetime.utcnow()
        return check_date > self.expiration_date

    def is_available(self, check_date: datetime = None) -> bool:
        """Check if lot is available for use.

        Args:
            check_date: Date to check against

        Returns:
            True if lot is available and not expired/quarantined
        """
        return not self.quarantined and not self.is_expired(check_date)


@dataclass
class ProductionBatch:
    """Production batch/lot record."""
    batch_id: str
    product_id: str
    product_description: str
    target_quantity: float
    actual_quantity: float
    unit: str = "units"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    equipment_id: Optional[str] = None
    operator_id: Optional[str] = None
    status: str = "in_process"  # "in_process", "complete", "failed", "rework"
    quality_approved: bool = False
    notes: str = ""
    metadata: Dict = field(default_factory=dict)

    @property
    def yield_percentage(self) -> float:
        """Calculate batch yield percentage."""
        if self.target_quantity == 0:
            return 0.0
        return (self.actual_quantity / self.target_quantity) * 100


@dataclass
class GenealogyRecord:
    """Record linking materials to production."""
    genealogy_id: str
    input_lot: MaterialLot
    output_batch: ProductionBatch
    quantity_used: float
    unit: str = "units"
    consumption_timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class TraceabilityPath:
    """Represents a genealogy path (forward or backward)."""
    start_id: str
    start_type: MaterialType  # or batch
    direction: GenealogyDirection
    path: List[Tuple[str, str, MaterialType]] = field(default_factory=list)  # (id, description, type)
    genealogy_records: List[GenealogyRecord] = field(default_factory=list)


class GenealogyTracker:
    """Track forward and backward product genealogy."""

    def __init__(self):
        """Initialize genealogy tracker."""
        self.material_lots: Dict[str, MaterialLot] = {}
        self.production_batches: Dict[str, ProductionBatch] = {}
        self.genealogy_records: Dict[str, List[GenealogyRecord]] = defaultdict(list)

        # Indices for fast lookup
        self.material_to_batches: Dict[str, List[str]] = defaultdict(list)  # lot→batches
        self.batch_to_materials: Dict[str, List[str]] = defaultdict(list)    # batch→lots

    def register_material_lot(self, lot: MaterialLot) -> None:
        """Register a material lot.

        Args:
            lot: MaterialLot to register
        """
        self.material_lots[lot.lot_number] = lot
        logger.info(f"Material lot registered: {lot.lot_number} ({lot.material_id})")

    def register_production_batch(self, batch: ProductionBatch) -> None:
        """Register a production batch.

        Args:
            batch: ProductionBatch to register
        """
        self.production_batches[batch.batch_id] = batch
        logger.info(f"Production batch registered: {batch.batch_id}")

    def record_material_consumption(
        self,
        genealogy_id: str,
        input_lot_number: str,
        output_batch_id: str,
        quantity_used: float,
        notes: str = "",
        metadata: Dict = None
    ) -> bool:
        """Record material consumption in production.

        Args:
            genealogy_id: Unique identifier for this genealogy record
            input_lot_number: Lot number of material used
            output_batch_id: Batch ID of production
            quantity_used: Quantity of material consumed
            notes: Optional notes
            metadata: Optional metadata

        Returns:
            True if successful
        """
        if input_lot_number not in self.material_lots:
            logger.error(f"Material lot not found: {input_lot_number}")
            return False

        if output_batch_id not in self.production_batches:
            logger.error(f"Production batch not found: {output_batch_id}")
            return False

        input_lot = self.material_lots[input_lot_number]
        output_batch = self.production_batches[output_batch_id]

        genealogy_record = GenealogyRecord(
            genealogy_id=genealogy_id,
            input_lot=input_lot,
            output_batch=output_batch,
            quantity_used=quantity_used,
            metadata=metadata or {}
        )

        self.genealogy_records[genealogy_id].append(genealogy_record)

        # Update indices
        self.material_to_batches[input_lot_number].append(output_batch_id)
        self.batch_to_materials[output_batch_id].append(input_lot_number)

        logger.info(f"Material consumption recorded: {input_lot_number} → {output_batch_id}")
        return True

    def trace_forward(self, material_lot_number: str, max_depth: int = 10) -> TraceabilityPath:
        """Trace material forward to finished products.

        Forward traceability: Raw Material → Components → Sub-assemblies → Finished Product

        Args:
            material_lot_number: Starting material lot number
            max_depth: Maximum genealogy depth to trace

        Returns:
            TraceabilityPath object with path information
        """
        path = TraceabilityPath(
            start_id=material_lot_number,
            start_type=MaterialType.RAW_MATERIAL,
            direction=GenealogyDirection.FORWARD
        )

        if material_lot_number not in self.material_lots:
            logger.warning(f"Material lot not found: {material_lot_number}")
            return path

        visited = set()
        queue = deque([(material_lot_number, 0)])

        while queue:
            current_lot, depth = queue.popleft()

            if depth > max_depth or current_lot in visited:
                continue

            visited.add(current_lot)

            # Find all batches that used this material
            related_batches = self.material_to_batches.get(current_lot, [])

            for batch_id in related_batches:
                if batch_id in self.production_batches:
                    batch = self.production_batches[batch_id]
                    material = self.material_lots[current_lot]

                    # Add to path
                    path.path.append((
                        batch_id,
                        f"{batch.product_description} (Batch {batch_id})",
                        MaterialType.FINISHED_PRODUCT
                    ))

                    # Get genealogy records for this material → batch connection
                    for gr_id, gr_list in self.genealogy_records.items():
                        for gr in gr_list:
                            if gr.input_lot.lot_number == current_lot and \
                               gr.output_batch.batch_id == batch_id:
                                path.genealogy_records.append(gr)

                    # Continue tracing from the batch outputs
                    # (batches can feed into other batches)
                    queue.append((batch_id, depth + 1))

        logger.info(f"Forward traceability traced: {material_lot_number} → {len(set(p[0] for p in path.path))} batches")
        return path

    def trace_backward(self, production_batch_id: str, max_depth: int = 10) -> TraceabilityPath:
        """Trace production backward to source materials.

        Backward traceability: Finished Product ← Components ← Raw Materials

        Args:
            production_batch_id: Starting production batch ID
            max_depth: Maximum genealogy depth to trace

        Returns:
            TraceabilityPath object with path information
        """
        path = TraceabilityPath(
            start_id=production_batch_id,
            start_type=MaterialType.FINISHED_PRODUCT,
            direction=GenealogyDirection.BACKWARD
        )

        if production_batch_id not in self.production_batches:
            logger.warning(f"Production batch not found: {production_batch_id}")
            return path

        visited = set()
        queue = deque([(production_batch_id, 0)])

        while queue:
            current_batch, depth = queue.popleft()

            if depth > max_depth or current_batch in visited:
                continue

            visited.add(current_batch)

            # Find all materials used in this batch
            related_lots = self.batch_to_materials.get(current_batch, [])

            for lot_number in related_lots:
                if lot_number in self.material_lots:
                    material = self.material_lots[lot_number]

                    # Add to path
                    path.path.append((
                        lot_number,
                        f"{material.material_description} (Lot {lot_number})",
                        material.material_type
                    ))

                    # Get genealogy records
                    for gr_id, gr_list in self.genealogy_records.items():
                        for gr in gr_list:
                            if gr.input_lot.lot_number == lot_number and \
                               gr.output_batch.batch_id == current_batch:
                                path.genealogy_records.append(gr)

                    # Continue tracing from material sources
                    queue.append((lot_number, depth + 1))

        logger.info(f"Backward traceability traced: {production_batch_id} ← {len(set(p[0] for p in path.path))} materials")
        return path

    def perform_impact_analysis(self, defect_material: str) -> Dict:
        """Analyze impact of defective material on finished products.

        Args:
            defect_material: Material lot number with defect

        Returns:
            Impact analysis results
        """
        logger.warning(f"Impact analysis initiated for defective material: {defect_material}")

        affected_batches = set()
        affected_products = defaultdict(int)
        total_units_affected = 0

        # Find all production batches that used this material
        related_batches = self.material_to_batches.get(defect_material, [])

        for batch_id in related_batches:
            if batch_id in self.production_batches:
                batch = self.production_batches[batch_id]
                affected_batches.add(batch_id)

                # Count affected units
                if batch.quality_approved:
                    units = batch.actual_quantity
                    total_units_affected += units
                    affected_products[batch.product_id] += units

        logger.warning(f"Impact analysis complete: {len(affected_batches)} batches, "
                      f"{total_units_affected} units affected")

        return {
            'defect_material': defect_material,
            'affected_batches': list(affected_batches),
            'affected_products': dict(affected_products),
            'total_units_affected': total_units_affected,
            'impact_severity': self._assess_severity(total_units_affected, len(affected_batches))
        }

    def _assess_severity(self, units_affected: float, batch_count: int) -> str:
        """Assess severity of defect impact.

        Args:
            units_affected: Number of units affected
            batch_count: Number of batches affected

        Returns:
            Severity level: "critical", "high", "medium", "low"
        """
        if units_affected > 10000 or batch_count > 10:
            return "critical"
        elif units_affected > 1000 or batch_count > 3:
            return "high"
        elif units_affected > 100:
            return "medium"
        else:
            return "low"

    def identify_safe_lots(self, defect_material: str) -> List[MaterialLot]:
        """Identify material lots NOT affected by defect.

        Args:
            defect_material: Defective material lot number

        Returns:
            List of unaffected material lots
        """
        defect_produced_in_batches = set(
            self.material_to_batches.get(defect_material, [])
        )

        safe_lots = []
        for lot_number, lot in self.material_lots.items():
            if lot_number != defect_material:
                # Check if this lot was used in any affected batches
                lot_used_in = set(self.material_to_batches.get(lot_number, []))
                if not lot_used_in.intersection(defect_produced_in_batches):
                    safe_lots.append(lot)

        logger.info(f"Identified {len(safe_lots)} safe material lots")
        return safe_lots

    def get_genealogy_report(self, batch_id: str) -> Dict:
        """Generate comprehensive genealogy report for a batch.

        Args:
            batch_id: Production batch ID

        Returns:
            Detailed genealogy report
        """
        if batch_id not in self.production_batches:
            return {'error': f'Batch not found: {batch_id}'}

        batch = self.production_batches[batch_id]
        input_materials = self.batch_to_materials.get(batch_id, [])

        materials_info = []
        for lot_number in input_materials:
            if lot_number in self.material_lots:
                material = self.material_lots[lot_number]
                # Find consumption record
                consumption = None
                for gr_id, gr_list in self.genealogy_records.items():
                    for gr in gr_list:
                        if gr.input_lot.lot_number == lot_number and \
                           gr.output_batch.batch_id == batch_id:
                            consumption = {
                                'quantity_used': gr.quantity_used,
                                'unit': gr.unit,
                                'timestamp': gr.consumption_timestamp.isoformat()
                            }
                            break

                materials_info.append({
                    'lot_number': lot_number,
                    'material_id': material.material_id,
                    'description': material.material_description,
                    'supplier': material.supplier_id,
                    'type': material.material_type.value,
                    'consumption': consumption,
                    'available': material.is_available()
                })

        return {
            'batch_id': batch_id,
            'product_id': batch.product_id,
            'product_description': batch.product_description,
            'status': batch.status,
            'quantity_produced': batch.actual_quantity,
            'yield': batch.yield_percentage,
            'quality_approved': batch.quality_approved,
            'production_date': batch.start_time.isoformat() if batch.start_time else None,
            'equipment_used': batch.equipment_id,
            'operator': batch.operator_id,
            'input_materials': materials_info,
            'notes': batch.notes
        }

    def get_quarantine_impact(self) -> Dict:
        """Analyze impact of all quarantined materials.

        Returns:
            Report of quarantined materials and their impact
        """
        quarantined_lots = [
            lot for lot in self.material_lots.values()
            if lot.quarantined
        ]

        impact_analysis = {}
        total_affected_units = 0

        for lot in quarantined_lots:
            impact = self.perform_impact_analysis(lot.lot_number)
            impact_analysis[lot.lot_number] = impact
            total_affected_units += impact['total_units_affected']

        logger.warning(f"Quarantine impact report: {len(quarantined_lots)} lots, "
                      f"{total_affected_units} units affected")

        return {
            'quarantined_materials': [
                {
                    'lot_number': lot.lot_number,
                    'material_id': lot.material_id,
                    'description': lot.material_description,
                    'quarantine_reason': lot.quarantine_reason
                }
                for lot in quarantined_lots
            ],
            'impact_analysis': impact_analysis,
            'total_units_at_risk': total_affected_units
        }

    def export_genealogy_csv(self, batch_id: str) -> List[str]:
        """Export genealogy data as CSV format.

        Args:
            batch_id: Production batch ID

        Returns:
            List of CSV lines
        """
        report = self.get_genealogy_report(batch_id)

        lines = [
            'Genealogy Report',
            f'Batch ID,{batch_id}',
            f'Product,{report.get("product_description", "")}',
            f'Status,{report.get("status", "")}',
            f'Quantity Produced,{report.get("quantity_produced", "")}',
            f'Yield %,{report.get("yield", ""):.1f}',
            '',
            'Input Materials',
            'Lot Number,Material ID,Description,Supplier,Type,Quantity Used,Unit,Timestamp,Available'
        ]

        for material in report.get('input_materials', []):
            consumption = material.get('consumption', {})
            lines.append(
                f'{material["lot_number"]},'
                f'{material["material_id"]},'
                f'{material["description"]},'
                f'{material.get("supplier", "")},'
                f'{material["type"]},'
                f'{consumption.get("quantity_used", "")},'
                f'{consumption.get("unit", "")},'
                f'{consumption.get("timestamp", "")},'
                f'{material["available"]}'
            )

        return lines


# ==================== Example Usage ====================

def main():
    """Example usage of genealogy tracking."""

    tracker = GenealogyTracker()

    # Register materials
    material_a = MaterialLot(
        lot_number="Lot-2024-5670",
        material_id="Steel-001",
        material_description="Steel Component A",
        material_type=MaterialType.RAW_MATERIAL,
        supplier_id="Supplier-ABC",
        received_date=datetime(2024, 11, 1),
        quantity_received=1000
    )

    material_b = MaterialLot(
        lot_number="Lot-2024-5671",
        material_id="Fastener-002",
        material_description="M6 Bolts",
        material_type=MaterialType.COMPONENT,
        supplier_id="Supplier-DEF",
        received_date=datetime(2024, 11, 5),
        quantity_received=5000
    )

    tracker.register_material_lot(material_a)
    tracker.register_material_lot(material_b)

    # Register production batch
    batch = ProductionBatch(
        batch_id="Batch-2024-1456",
        product_id="Widget-A",
        product_description="Standard Widget Assembly",
        target_quantity=500,
        actual_quantity=495,
        start_time=datetime(2024, 11, 19, 8, 0),
        end_time=datetime(2024, 11, 19, 10, 0),
        equipment_id="Line1-Machine1",
        operator_id="john.smith",
        status="complete",
        quality_approved=True
    )

    tracker.register_production_batch(batch)

    # Record material consumption
    tracker.record_material_consumption(
        genealogy_id="GEN-2024-001",
        input_lot_number="Lot-2024-5670",
        output_batch_id="Batch-2024-1456",
        quantity_used=500,
        notes="Normal consumption"
    )

    tracker.record_material_consumption(
        genealogy_id="GEN-2024-002",
        input_lot_number="Lot-2024-5671",
        output_batch_id="Batch-2024-1456",
        quantity_used=2500,
        notes="Normal consumption"
    )

    # Perform traceability queries
    print("\n=== Genealogy Tracking Demo ===\n")

    # Forward traceability
    print("Forward Traceability (Lot-2024-5670 → Products):")
    forward_path = tracker.trace_forward("Lot-2024-5670")
    for item_id, description, item_type in forward_path.path:
        print(f"  → {description} [{item_type.value}]")

    # Backward traceability
    print("\nBackward Traceability (Batch-2024-1456 ← Materials):")
    backward_path = tracker.trace_backward("Batch-2024-1456")
    for item_id, description, item_type in backward_path.path:
        print(f"  ← {description} [{item_type.value}]")

    # Impact analysis
    print("\nImpact Analysis (if Lot-2024-5670 was defective):")
    impact = tracker.perform_impact_analysis("Lot-2024-5670")
    print(f"  Affected Batches: {len(impact['affected_batches'])}")
    print(f"  Units Affected: {impact['total_units_affected']}")
    print(f"  Severity: {impact['impact_severity']}")

    # Genealogy report
    print("\nDetailed Genealogy Report:")
    report = tracker.get_genealogy_report("Batch-2024-1456")
    print(f"  Product: {report['product_description']}")
    print(f"  Status: {report['status']}")
    print(f"  Yield: {report['yield']:.1f}%")
    print(f"  Input Materials: {len(report['input_materials'])}")
    for material in report['input_materials']:
        print(f"    - {material['lot_number']}: {material['description']}")

    # Export CSV
    print("\nCSV Export (first 5 lines):")
    csv_lines = tracker.export_genealogy_csv("Batch-2024-1456")
    for line in csv_lines[:5]:
        print(f"  {line}")


if __name__ == "__main__":
    main()
