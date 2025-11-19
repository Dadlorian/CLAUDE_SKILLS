"""
Billing Rules Engine - Practice Management Automation

Manages billing rules and rate structures for matter billing.
Handles hourly rates, flat fees, contingency arrangements, and retainers.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal


class BillingType(Enum):
    """Types of billing arrangements"""
    HOURLY = "hourly"
    FLAT_FEE = "flat_fee"
    CONTINGENCY = "contingency"
    RETAINER = "retainer"
    BLENDED = "blended"


class BillingStatus(Enum):
    """Status of a billing entry"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    BILLED = "billed"
    PAID = "paid"


@dataclass
class TimeEntry:
    """Represents billable time"""
    attorney_id: str
    matter_id: str
    hours: Decimal
    date: datetime
    description: str
    rate: Decimal = None


@dataclass
class BillingRate:
    """Billing rate for an attorney"""
    attorney_id: str
    hourly_rate: Decimal
    matter_type: str
    effective_date: datetime
    expiration_date: Optional[datetime] = None
    discount_percent: Decimal = Decimal(0)

    def get_effective_rate(self) -> Decimal:
        """Calculate rate after discount"""
        discount_amount = self.hourly_rate * (self.discount_percent / 100)
        return self.hourly_rate - discount_amount


@dataclass
class BillingRule:
    """Rule defining billing calculation logic"""
    rule_id: str
    matter_id: str
    billing_type: BillingType
    amount: Decimal
    description: str
    active: bool = True
    created_date: datetime = None

    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()


class BillingRulesEngine:
    """Engine for calculating and managing billing"""

    def __init__(self):
        self.rules: Dict[str, List[BillingRule]] = {}
        self.rates: List[BillingRate] = []
        self.time_entries: List[TimeEntry] = []
        self.invoices: List[Dict] = []

    def add_billing_rule(self, rule: BillingRule) -> None:
        """Add a billing rule for a matter"""
        if rule.matter_id not in self.rules:
            self.rules[rule.matter_id] = []
        self.rules[rule.matter_id].append(rule)

    def add_billing_rate(self, rate: BillingRate) -> None:
        """Add or update attorney billing rate"""
        # Remove expired rates
        self.rates = [r for r in self.rates if r.expiration_date is None or r.expiration_date > datetime.now()]
        self.rates.append(rate)

    def add_time_entry(self, entry: TimeEntry) -> None:
        """Record billable time"""
        if entry.rate is None:
            entry.rate = self._get_attorney_rate(entry.attorney_id, entry.matter_id)
        self.time_entries.append(entry)

    def _get_attorney_rate(self, attorney_id: str, matter_id: str) -> Decimal:
        """Get applicable hourly rate for attorney"""
        applicable_rates = [
            r for r in self.rates
            if r.attorney_id == attorney_id and (
                r.expiration_date is None or r.expiration_date > datetime.now()
            )
        ]

        if applicable_rates:
            return applicable_rates[0].get_effective_rate()
        return Decimal(250)  # Default rate

    def calculate_hourly_billing(self, matter_id: str) -> Decimal:
        """Calculate total hours for a matter at applicable rates"""
        matter_entries = [e for e in self.time_entries if e.matter_id == matter_id]
        total = sum(e.hours * (e.rate or Decimal(0)) for e in matter_entries)
        return total

    def calculate_flat_fee_billing(self, matter_id: str) -> Decimal:
        """Get flat fee amount for a matter"""
        matter_rules = self.rules.get(matter_id, [])
        flat_fee_rules = [r for r in matter_rules if r.billing_type == BillingType.FLAT_FEE]

        if flat_fee_rules:
            return flat_fee_rules[0].amount
        return Decimal(0)

    def calculate_contingency_amount(self, matter_id: str, settlement_amount: Decimal) -> Decimal:
        """Calculate contingency fee based on settlement"""
        matter_rules = self.rules.get(matter_id, [])
        contingency_rules = [r for r in matter_rules if r.billing_type == BillingType.CONTINGENCY]

        if contingency_rules:
            percentage = contingency_rules[0].amount  # Stored as percentage
            return settlement_amount * (percentage / 100)
        return Decimal(0)

    def calculate_retainer_billing(self, matter_id: str) -> Decimal:
        """Get retainer amount for a matter"""
        matter_rules = self.rules.get(matter_id, [])
        retainer_rules = [r for r in matter_rules if r.billing_type == BillingType.RETAINER]

        if retainer_rules:
            return retainer_rules[0].amount
        return Decimal(0)

    def generate_invoice(self, matter_id: str, invoice_date: datetime) -> Dict:
        """Generate invoice for a matter"""
        hourly_charges = self.calculate_hourly_billing(matter_id)
        flat_fee = self.calculate_flat_fee_billing(matter_id)
        retainer = self.calculate_retainer_billing(matter_id)

        invoice = {
            "invoice_id": f"INV-{matter_id}-{invoice_date.strftime('%Y%m%d')}",
            "matter_id": matter_id,
            "invoice_date": invoice_date.isoformat(),
            "hourly_charges": str(hourly_charges),
            "flat_fee": str(flat_fee),
            "retainer": str(retainer),
            "total_due": str(hourly_charges + flat_fee + retainer),
            "status": BillingStatus.PENDING.value
        }

        self.invoices.append(invoice)
        return invoice

    def get_matter_billing_summary(self, matter_id: str) -> Dict:
        """Get billing summary for a matter"""
        return {
            "matter_id": matter_id,
            "hourly_total": str(self.calculate_hourly_billing(matter_id)),
            "flat_fee": str(self.calculate_flat_fee_billing(matter_id)),
            "retainer": str(self.calculate_retainer_billing(matter_id)),
            "time_entries": len([e for e in self.time_entries if e.matter_id == matter_id])
        }


# Example usage
if __name__ == "__main__":
    engine = BillingRulesEngine()

    # Add billing rate for attorney
    rate = BillingRate(
        attorney_id="ATT-001",
        hourly_rate=Decimal(350),
        matter_type="litigation",
        effective_date=datetime(2024, 1, 1),
        discount_percent=Decimal(10)
    )
    engine.add_billing_rate(rate)

    # Add time entry
    time_entry = TimeEntry(
        attorney_id="ATT-001",
        matter_id="MAT-2024-001",
        hours=Decimal(8.5),
        date=datetime(2024, 1, 15),
        description="Deposition preparation and attendance"
    )
    engine.add_time_entry(time_entry)

    # Generate invoice
    invoice = engine.generate_invoice("MAT-2024-001", datetime.now())
    print(f"Invoice generated: {invoice['invoice_id']}")
    print(f"Total due: ${invoice['total_due']}")
