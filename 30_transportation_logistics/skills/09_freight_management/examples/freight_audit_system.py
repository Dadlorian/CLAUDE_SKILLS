"""
Freight Audit and Payment System

Automated freight invoice validation, audit, and payment processing
to identify overcharges and ensure accurate freight billing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date
from enum import Enum
import re


class InvoiceStatus(Enum):
    """Invoice processing status"""
    RECEIVED = "received"
    VALIDATING = "validating"
    APPROVED = "approved"
    DISPUTED = "disputed"
    PAID = "paid"
    REJECTED = "rejected"


class DisputeReason(Enum):
    """Common dispute reasons"""
    INCORRECT_RATE = "incorrect_rate"
    DUPLICATE_CHARGE = "duplicate_charge"
    INCORRECT_WEIGHT = "incorrect_weight"
    INCORRECT_DIMENSIONS = "incorrect_dimensions"
    UNAUTHORIZED_ACCESSORIAL = "unauthorized_accessorial"
    INCORRECT_FUEL_SURCHARGE = "incorrect_fuel_surcharge"
    INCORRECT_ZIP_CODE = "incorrect_zip_code"
    SERVICE_NOT_PROVIDED = "service_not_provided"


@dataclass
class ContractRate:
    """Contracted freight rate"""
    carrier: str
    origin_zip: str
    dest_zip: str
    service_level: str
    min_weight: float
    max_weight: float
    rate_per_cwt: float  # Per hundred weight
    fuel_surcharge_pct: float
    effective_date: date
    expiration_date: date
    accessorial_rates: Dict[str, float] = field(default_factory=dict)


@dataclass
class InvoiceLineItem:
    """Individual charge line item on invoice"""
    line_number: int
    charge_type: str
    description: str
    rate: float
    quantity: float
    amount: float
    is_accessorial: bool = False


@dataclass
class FreightInvoice:
    """Freight invoice to be audited"""
    invoice_id: str
    carrier: str
    invoice_date: date
    tracking_number: str
    pro_number: Optional[str]  # Bill of lading / PRO number

    # Shipment details
    origin_zip: str
    dest_zip: str
    service_level: str
    ship_date: date
    delivery_date: Optional[date]

    # Charges
    weight: float
    dimensions: Optional[Dict[str, float]]  # L, W, H
    line_items: List[InvoiceLineItem]
    total_charges: float

    # Status
    status: InvoiceStatus = InvoiceStatus.RECEIVED

    # Audit results
    expected_charges: Optional[float] = None
    variance: Optional[float] = None
    disputes: List[Dict] = field(default_factory=list)
    audit_notes: str = ""


@dataclass
class AuditResult:
    """Result of invoice audit"""
    invoice_id: str
    status: InvoiceStatus
    invoiced_amount: float
    expected_amount: float
    variance: float
    variance_pct: float
    disputes: List[Dict]
    is_overcharged: bool
    recommended_payment: float
    audit_timestamp: datetime


class FreightAuditEngine:
    """
    Automated freight invoice audit engine.
    Validates invoices against contracted rates and business rules.
    """

    def __init__(self):
        self.contract_rates: List[ContractRate] = []
        self.business_rules: List = []
        self.tolerance_pct = 2.0  # Allow 2% variance without dispute

    def add_contract_rate(self, rate: ContractRate):
        """Add contracted rate for audit reference"""
        self.contract_rates.append(rate)

    def audit_invoice(self, invoice: FreightInvoice) -> AuditResult:
        """
        Audit freight invoice for accuracy.
        Returns audit result with any discrepancies.
        """
        print(f"Auditing invoice {invoice.invoice_id}...")

        # Find applicable contract rate
        contract_rate = self._find_contract_rate(
            carrier=invoice.carrier,
            origin=invoice.origin_zip,
            destination=invoice.dest_zip,
            weight=invoice.weight,
            ship_date=invoice.ship_date
        )

        if not contract_rate:
            # No contract rate found - flag for manual review
            invoice.status = InvoiceStatus.DISPUTED
            invoice.disputes.append({
                "reason": "no_contract_rate_found",
                "description": "No applicable contract rate found for this shipment",
                "severity": "high"
            })
            return self._create_audit_result(invoice, 0, [])

        # Calculate expected charges
        expected_charges = self._calculate_expected_charges(invoice, contract_rate)

        # Validate line items
        disputes = []

        # Check base rate
        base_charge = self._find_line_item(invoice, "BASE_CHARGE")
        if base_charge:
            expected_base = self._calculate_base_charge(invoice.weight, contract_rate)
            variance = abs(base_charge.amount - expected_base)

            if variance > expected_base * (self.tolerance_pct / 100):
                disputes.append({
                    "line_number": base_charge.line_number,
                    "reason": DisputeReason.INCORRECT_RATE.value,
                    "description": f"Base charge mismatch: Invoiced ${base_charge.amount:.2f}, Expected ${expected_base:.2f}",
                    "invoiced_amount": base_charge.amount,
                    "expected_amount": expected_base,
                    "variance": variance,
                    "severity": "high" if variance > 50 else "medium"
                })

        # Check fuel surcharge
        fuel_charge = self._find_line_item(invoice, "FUEL_SURCHARGE")
        if fuel_charge:
            expected_fuel = self._calculate_fuel_surcharge(
                base_amount=expected_charges["base"],
                surcharge_pct=contract_rate.fuel_surcharge_pct
            )
            variance = abs(fuel_charge.amount - expected_fuel)

            if variance > expected_fuel * (self.tolerance_pct / 100):
                disputes.append({
                    "line_number": fuel_charge.line_number,
                    "reason": DisputeReason.INCORRECT_FUEL_SURCHARGE.value,
                    "description": f"Fuel surcharge mismatch: Invoiced ${fuel_charge.amount:.2f}, Expected ${expected_fuel:.2f}",
                    "invoiced_amount": fuel_charge.amount,
                    "expected_amount": expected_fuel,
                    "variance": variance,
                    "severity": "medium"
                })

        # Check accessorial charges
        accessorial_disputes = self._audit_accessorial_charges(invoice, contract_rate)
        disputes.extend(accessorial_disputes)

        # Check for duplicate charges
        duplicate_disputes = self._check_duplicate_charges(invoice)
        disputes.extend(duplicate_disputes)

        # Check weight/dimensions
        validation_disputes = self._validate_shipment_details(invoice)
        disputes.extend(validation_disputes)

        # Calculate total expected amount
        total_expected = sum(expected_charges.values())

        # Update invoice with audit results
        invoice.expected_charges = total_expected
        invoice.variance = invoice.total_charges - total_expected
        invoice.disputes = disputes

        if disputes:
            invoice.status = InvoiceStatus.DISPUTED
        elif abs(invoice.variance) < self.tolerance_pct * total_expected / 100:
            invoice.status = InvoiceStatus.APPROVED
        else:
            invoice.status = InvoiceStatus.DISPUTED

        # Create audit result
        return self._create_audit_result(invoice, total_expected, disputes)

    def _find_contract_rate(
        self,
        carrier: str,
        origin: str,
        destination: str,
        weight: float,
        ship_date: date
    ) -> Optional[ContractRate]:
        """Find applicable contract rate"""
        for rate in self.contract_rates:
            if (rate.carrier == carrier and
                self._zip_matches(rate.origin_zip, origin) and
                self._zip_matches(rate.dest_zip, destination) and
                rate.min_weight <= weight <= rate.max_weight and
                rate.effective_date <= ship_date <= rate.expiration_date):
                return rate

        return None

    def _zip_matches(self, pattern: str, actual: str) -> bool:
        """Check if ZIP code matches pattern (supports wildcards)"""
        # Support 3-digit ZIP prefix matching
        if len(pattern) == 3:
            return actual.startswith(pattern)
        return pattern == actual

    def _calculate_expected_charges(
        self,
        invoice: FreightInvoice,
        contract_rate: ContractRate
    ) -> Dict[str, float]:
        """Calculate expected charges based on contract"""
        charges = {}

        # Base charge
        base = self._calculate_base_charge(invoice.weight, contract_rate)
        charges["base"] = base

        # Fuel surcharge
        fuel = self._calculate_fuel_surcharge(base, contract_rate.fuel_surcharge_pct)
        charges["fuel"] = fuel

        # Accessorial charges
        for line_item in invoice.line_items:
            if line_item.is_accessorial:
                charge_type = line_item.charge_type
                if charge_type in contract_rate.accessorial_rates:
                    charges[charge_type] = contract_rate.accessorial_rates[charge_type]

        return charges

    def _calculate_base_charge(self, weight: float, contract_rate: ContractRate) -> float:
        """Calculate base freight charge"""
        # Convert weight to CWT (per hundred weight)
        cwt = weight / 100.0
        return cwt * contract_rate.rate_per_cwt

    def _calculate_fuel_surcharge(self, base_amount: float, surcharge_pct: float) -> float:
        """Calculate fuel surcharge"""
        return base_amount * (surcharge_pct / 100.0)

    def _find_line_item(self, invoice: FreightInvoice, charge_type: str) -> Optional[InvoiceLineItem]:
        """Find line item by charge type"""
        for item in invoice.line_items:
            if item.charge_type == charge_type:
                return item
        return None

    def _audit_accessorial_charges(
        self,
        invoice: FreightInvoice,
        contract_rate: ContractRate
    ) -> List[Dict]:
        """Audit accessorial charges"""
        disputes = []

        for line_item in invoice.line_items:
            if not line_item.is_accessorial:
                continue

            charge_type = line_item.charge_type

            # Check if accessorial is in contract
            if charge_type not in contract_rate.accessorial_rates:
                disputes.append({
                    "line_number": line_item.line_number,
                    "reason": DisputeReason.UNAUTHORIZED_ACCESSORIAL.value,
                    "description": f"Unauthorized accessorial charge: {charge_type}",
                    "invoiced_amount": line_item.amount,
                    "expected_amount": 0,
                    "variance": line_item.amount,
                    "severity": "high"
                })
                continue

            # Check if amount matches contract
            expected_amount = contract_rate.accessorial_rates[charge_type]
            variance = abs(line_item.amount - expected_amount)

            if variance > expected_amount * (self.tolerance_pct / 100):
                disputes.append({
                    "line_number": line_item.line_number,
                    "reason": DisputeReason.INCORRECT_RATE.value,
                    "description": f"Accessorial rate mismatch for {charge_type}: Invoiced ${line_item.amount:.2f}, Expected ${expected_amount:.2f}",
                    "invoiced_amount": line_item.amount,
                    "expected_amount": expected_amount,
                    "variance": variance,
                    "severity": "medium"
                })

        return disputes

    def _check_duplicate_charges(self, invoice: FreightInvoice) -> List[Dict]:
        """Check for duplicate line items"""
        disputes = []
        seen_charges = {}

        for line_item in invoice.line_items:
            key = f"{line_item.charge_type}_{line_item.description}"

            if key in seen_charges:
                disputes.append({
                    "line_number": line_item.line_number,
                    "reason": DisputeReason.DUPLICATE_CHARGE.value,
                    "description": f"Duplicate charge: {line_item.description}",
                    "invoiced_amount": line_item.amount,
                    "expected_amount": 0,
                    "variance": line_item.amount,
                    "severity": "high"
                })
            else:
                seen_charges[key] = line_item

        return disputes

    def _validate_shipment_details(self, invoice: FreightInvoice) -> List[Dict]:
        """Validate weight and dimensions"""
        disputes = []

        # Check for reasonable weight (not negative, not excessive)
        if invoice.weight <= 0:
            disputes.append({
                "reason": DisputeReason.INCORRECT_WEIGHT.value,
                "description": f"Invalid weight: {invoice.weight} lbs",
                "severity": "critical"
            })
        elif invoice.weight > 45000:  # Max truckload weight
            disputes.append({
                "reason": DisputeReason.INCORRECT_WEIGHT.value,
                "description": f"Excessive weight: {invoice.weight} lbs (max 45,000 lbs)",
                "severity": "high"
            })

        # Check dimensions if provided
        if invoice.dimensions:
            dims = invoice.dimensions
            if any(v <= 0 for v in dims.values()):
                disputes.append({
                    "reason": DisputeReason.INCORRECT_DIMENSIONS.value,
                    "description": f"Invalid dimensions: {dims}",
                    "severity": "high"
                })

        return disputes

    def _create_audit_result(
        self,
        invoice: FreightInvoice,
        expected_amount: float,
        disputes: List[Dict]
    ) -> AuditResult:
        """Create audit result summary"""
        variance = invoice.total_charges - expected_amount
        variance_pct = (variance / expected_amount * 100) if expected_amount > 0 else 0

        # Recommended payment (deduct disputed amounts)
        disputed_amount = sum(d.get('variance', 0) for d in disputes)
        recommended_payment = invoice.total_charges - disputed_amount

        return AuditResult(
            invoice_id=invoice.invoice_id,
            status=invoice.status,
            invoiced_amount=invoice.total_charges,
            expected_amount=expected_amount,
            variance=variance,
            variance_pct=variance_pct,
            disputes=disputes,
            is_overcharged=variance > 0,
            recommended_payment=recommended_payment,
            audit_timestamp=datetime.now()
        )


class FreightPaymentProcessor:
    """Process approved freight payments"""

    def __init__(self):
        self.pending_payments = []

    def process_payment(self, invoice: FreightInvoice, audit_result: AuditResult):
        """Process payment for audited invoice"""
        if audit_result.status == InvoiceStatus.APPROVED:
            print(f"Processing payment for invoice {invoice.invoice_id}")
            print(f"  Amount: ${audit_result.recommended_payment:.2f}")

            # In production: integrate with accounting system
            self._submit_to_ap_system(invoice, audit_result.recommended_payment)

        elif audit_result.status == InvoiceStatus.DISPUTED:
            print(f"Invoice {invoice.invoice_id} has disputes - holding payment")
            print(f"  Total disputes: {len(audit_result.disputes)}")
            print(f"  Disputed amount: ${audit_result.invoiced_amount - audit_result.recommended_payment:.2f}")

            # Send dispute to carrier
            self._send_dispute_to_carrier(invoice, audit_result)

    def _submit_to_ap_system(self, invoice: FreightInvoice, amount: float):
        """Submit to Accounts Payable system"""
        # Integration with ERP/accounting system
        print(f"Submitted ${amount:.2f} payment to AP system")

    def _send_dispute_to_carrier(self, invoice: FreightInvoice, audit_result: AuditResult):
        """Send dispute notification to carrier"""
        print(f"Sending dispute to {invoice.carrier}")
        for dispute in audit_result.disputes:
            print(f"  - {dispute['reason']}: {dispute['description']}")


# ============================================================================
# Example Usage
# ============================================================================


def example_usage():
    # Set up contract rates
    contract_rate = ContractRate(
        carrier="ABC Freight",
        origin_zip="752",  # 3-digit prefix (Dallas area)
        dest_zip="606",  # 3-digit prefix (Chicago area)
        service_level="Standard LTL",
        min_weight=100,
        max_weight=10000,
        rate_per_cwt=25.50,  # $25.50 per 100 lbs
        fuel_surcharge_pct=18.5,
        effective_date=date(2025, 1, 1),
        expiration_date=date(2025, 12, 31),
        accessorial_rates={
            "LIFTGATE_DELIVERY": 75.00,
            "RESIDENTIAL_DELIVERY": 85.00,
            "INSIDE_DELIVERY": 125.00
        }
    )

    # Create audit engine
    audit_engine = FreightAuditEngine()
    audit_engine.add_contract_rate(contract_rate)

    # Example 1: Clean invoice (no issues)
    clean_invoice = FreightInvoice(
        invoice_id="INV-001",
        carrier="ABC Freight",
        invoice_date=date(2025, 1, 15),
        tracking_number="TRK123456",
        pro_number="PRO789012",
        origin_zip="75201",
        dest_zip="60601",
        service_level="Standard LTL",
        ship_date=date(2025, 1, 10),
        delivery_date=date(2025, 1, 12),
        weight=2000,  # 2000 lbs = 20 CWT
        dimensions={"L": 48, "W": 40, "H": 48},
        line_items=[
            InvoiceLineItem(1, "BASE_CHARGE", "Base Freight Charge", 25.50, 20, 510.00),
            InvoiceLineItem(2, "FUEL_SURCHARGE", "Fuel Surcharge (18.5%)", 18.5, 510, 94.35),
            InvoiceLineItem(3, "LIFTGATE_DELIVERY", "Liftgate Delivery", 75.00, 1, 75.00, is_accessorial=True)
        ],
        total_charges=679.35
    )

    print("=== Example 1: Clean Invoice ===")
    result1 = audit_engine.audit_invoice(clean_invoice)
    print(f"Status: {result1.status.value}")
    print(f"Invoiced: ${result1.invoiced_amount:.2f}")
    print(f"Expected: ${result1.expected_amount:.2f}")
    print(f"Variance: ${result1.variance:.2f} ({result1.variance_pct:.2f}%)")
    print(f"Disputes: {len(result1.disputes)}")

    # Example 2: Invoice with overcharge
    overcharged_invoice = FreightInvoice(
        invoice_id="INV-002",
        carrier="ABC Freight",
        invoice_date=date(2025, 1, 15),
        tracking_number="TRK789012",
        pro_number="PRO345678",
        origin_zip="75201",
        dest_zip="60601",
        service_level="Standard LTL",
        ship_date=date(2025, 1, 10),
        delivery_date=date(2025, 1, 12),
        weight=2000,
        dimensions={"L": 48, "W": 40, "H": 48},
        line_items=[
            InvoiceLineItem(1, "BASE_CHARGE", "Base Freight Charge", 30.00, 20, 600.00),  # Overcharged
            InvoiceLineItem(2, "FUEL_SURCHARGE", "Fuel Surcharge (18.5%)", 18.5, 600, 111.00),
            InvoiceLineItem(3, "RESIDENTIAL_DELIVERY", "Residential Delivery", 85.00, 1, 85.00, is_accessorial=True),
            InvoiceLineItem(4, "INSIDE_DELIVERY", "Inside Delivery", 150.00, 1, 150.00, is_accessorial=True)  # Overcharged
        ],
        total_charges=946.00
    )

    print("\n=== Example 2: Invoice with Overcharges ===")
    result2 = audit_engine.audit_invoice(overcharged_invoice)
    print(f"Status: {result2.status.value}")
    print(f"Invoiced: ${result2.invoiced_amount:.2f}")
    print(f"Expected: ${result2.expected_amount:.2f}")
    print(f"Variance: ${result2.variance:.2f} ({result2.variance_pct:.2f}%)")
    print(f"Disputes: {len(result2.disputes)}")

    if result2.disputes:
        print("\nDispute Details:")
        for dispute in result2.disputes:
            print(f"  - {dispute['reason']}: {dispute['description']}")
            print(f"    Variance: ${dispute.get('variance', 0):.2f}")

    print(f"\nRecommended Payment: ${result2.recommended_payment:.2f}")

    # Process payments
    print("\n=== Payment Processing ===")
    payment_processor = FreightPaymentProcessor()
    payment_processor.process_payment(clean_invoice, result1)
    payment_processor.process_payment(overcharged_invoice, result2)


if __name__ == "__main__":
    example_usage()
