"""
Matter Closing Automation - Practice Management Automation

Automates the matter closing process including final billings,
client communications, document archival, and trust account reconciliation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import json


class ClosingStatus(Enum):
    """Status of matter closing process"""
    OPEN = "open"
    CLOSING_INITIATED = "closing_initiated"
    REVIEW_PENDING = "review_pending"
    FINAL_BILLING_SENT = "final_billing_sent"
    DOCUMENTS_ARCHIVED = "documents_archived"
    TRUST_RECONCILED = "trust_reconciled"
    CLOSED = "closed"


class ClosingChecklist(Enum):
    """Checklist items for matter closing"""
    FINAL_INVOICE = "final_invoice"
    TRUST_RECONCILIATION = "trust_reconciliation"
    DOCUMENT_ARCHIVAL = "document_archival"
    CLIENT_LETTER = "client_letter"
    FILE_RETENTION_MEMO = "file_retention_memo"
    CONFLICTS_CHECK = "conflicts_check"
    OUTSTANDING_ITEMS = "outstanding_items"
    LIEN_RESOLUTION = "lien_resolution"
    REFERRAL_LETTERS = "referral_letters"
    MATTER_EVALUATION = "matter_evaluation"


@dataclass
class ClosingItem:
    """Item on matter closing checklist"""
    item_type: ClosingChecklist
    completed: bool = False
    completion_date: Optional[datetime] = None
    notes: str = ""
    responsible_party: str = ""


@dataclass
class MatterClosing:
    """Represents a matter closing process"""
    matter_id: str
    client_id: str
    closing_initiated_date: datetime
    expected_closing_date: datetime
    closing_status: ClosingStatus = ClosingStatus.CLOSING_INITIATED
    checklist_items: Dict[str, ClosingItem] = field(default_factory=dict)
    final_balance_due: float = 0.0
    trust_account_balance: float = 0.0
    closing_notes: str = ""
    outcome: Optional[str] = None
    files_to_retain: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Initialize checklist
        if not self.checklist_items:
            for item_type in ClosingChecklist:
                self.checklist_items[item_type.value] = ClosingItem(item_type=item_type)

    def mark_item_complete(self, item_type: ClosingChecklist) -> None:
        """Mark a closing checklist item as complete"""
        if item_type.value in self.checklist_items:
            self.checklist_items[item_type.value].completed = True
            self.checklist_items[item_type.value].completion_date = datetime.now()

    def get_completion_percentage(self) -> float:
        """Get percentage of closing process completed"""
        if not self.checklist_items:
            return 0.0
        completed = sum(1 for item in self.checklist_items.values() if item.completed)
        return (completed / len(self.checklist_items)) * 100


@dataclass
class ClosingLetter:
    """Final closing letter for client"""
    letter_id: str
    matter_id: str
    client_name: str
    closing_date: datetime
    matter_outcome: str
    final_invoice_amount: float
    trust_refund_amount: float
    items_enclosed: List[str] = field(default_factory=list)
    file_retention_info: str = ""
    contact_info: str = ""


class MatterClosingAutomation:
    """Automates matter closing process"""

    def __init__(self):
        self.closings: Dict[str, MatterClosing] = {}
        self.closing_letters: List[ClosingLetter] = []

    def initiate_closing(self, matter_closing: MatterClosing) -> str:
        """Initiate matter closing process"""
        self.closings[matter_closing.matter_id] = matter_closing
        return matter_closing.matter_id

    def get_closing_status(self, matter_id: str) -> Dict:
        """Get status of matter closing"""
        if matter_id not in self.closings:
            return {}

        closing = self.closings[matter_id]
        incomplete_items = [
            item_type for item_type, item in closing.checklist_items.items()
            if not item.completed
        ]

        return {
            "matter_id": matter_id,
            "status": closing.closing_status.value,
            "completion_percentage": closing.get_completion_percentage(),
            "incomplete_items": incomplete_items,
            "expected_closing_date": closing.expected_closing_date.isoformat(),
            "final_balance_due": closing.final_balance_due
        }

    def perform_trust_reconciliation(self, matter_id: str, final_balance: float) -> bool:
        """Reconcile trust account for matter closing"""
        if matter_id not in self.closings:
            return False

        closing = self.closings[matter_id]
        closing.trust_account_balance = final_balance
        closing.mark_item_complete(ClosingChecklist.TRUST_RECONCILIATION)
        closing.closing_status = ClosingStatus.TRUST_RECONCILED

        return True

    def generate_final_invoice(self, matter_id: str, invoice_details: Dict) -> Dict:
        """Generate final invoice for matter"""
        if matter_id not in self.closings:
            return {}

        closing = self.closings[matter_id]
        final_amount = invoice_details.get("total_due", 0.0)
        closing.final_balance_due = final_amount
        closing.mark_item_complete(ClosingChecklist.FINAL_INVOICE)

        invoice = {
            "invoice_id": f"FIN-{matter_id}-{datetime.now().strftime('%Y%m%d')}",
            "matter_id": matter_id,
            "invoice_date": datetime.now().isoformat(),
            "invoice_type": "final",
            "total_due": final_amount,
            "payment_terms": invoice_details.get("payment_terms", "Due upon receipt"),
            "details": invoice_details.get("details", [])
        }

        return invoice

    def archive_matter_documents(self, matter_id: str, archive_location: str) -> bool:
        """Archive matter documents"""
        if matter_id not in self.closings:
            return False

        closing = self.closings[matter_id]
        closing.files_to_retain.append(archive_location)
        closing.mark_item_complete(ClosingChecklist.DOCUMENT_ARCHIVAL)

        return True

    def generate_closing_letter(self, matter_id: str, client_name: str,
                               outcome: str, final_amount: float) -> str:
        """Generate closing letter for client"""
        if matter_id not in self.closings:
            return ""

        closing = self.closings[matter_id]
        trust_refund = max(0, closing.trust_account_balance - final_amount)

        letter = ClosingLetter(
            letter_id=f"CLT-{matter_id}-{datetime.now().strftime('%Y%m%d')}",
            matter_id=matter_id,
            client_name=client_name,
            closing_date=datetime.now(),
            matter_outcome=outcome,
            final_invoice_amount=final_amount,
            trust_refund_amount=trust_refund,
            items_enclosed=[
                "Final Invoice",
                "Final Accounting Statement",
                "Matter Outcome Summary",
                "Original Documents" if trust_refund > 0 else "Trust Check"
            ],
            file_retention_info="Client documents will be retained for 7 years per state bar rules.",
            contact_info="Please contact us if you have questions about this matter."
        )

        self.closing_letters.append(letter)
        closing.mark_item_complete(ClosingChecklist.CLIENT_LETTER)
        closing.outcome = outcome

        return letter.letter_id

    def validate_closing_readiness(self, matter_id: str) -> Dict:
        """Validate matter is ready to close"""
        if matter_id not in self.closings:
            return {"ready": False, "errors": ["Matter not found"]}

        closing = self.closings[matter_id]
        errors = []

        # Check all critical items are complete
        critical_items = [
            ClosingChecklist.FINAL_INVOICE,
            ClosingChecklist.TRUST_RECONCILIATION,
            ClosingChecklist.DOCUMENT_ARCHIVAL
        ]

        for item_type in critical_items:
            if not closing.checklist_items[item_type.value].completed:
                errors.append(f"{item_type.value} not completed")

        return {
            "matter_id": matter_id,
            "ready": len(errors) == 0,
            "completion_percentage": closing.get_completion_percentage(),
            "errors": errors
        }

    def complete_closing(self, matter_id: str) -> bool:
        """Complete matter closing"""
        if matter_id not in self.closings:
            return False

        # Validate readiness
        validation = self.validate_closing_readiness(matter_id)
        if not validation.get("ready"):
            return False

        closing = self.closings[matter_id]
        closing.closing_status = ClosingStatus.CLOSED

        return True

    def get_matters_ready_to_close(self) -> List[str]:
        """Get matters ready for closing"""
        ready_matters = []
        for matter_id, closing in self.closings.items():
            validation = self.validate_closing_readiness(matter_id)
            if validation.get("ready"):
                ready_matters.append(matter_id)

        return ready_matters

    def export_closing_summary(self, matter_id: str) -> str:
        """Export matter closing summary as JSON"""
        if matter_id not in self.closings:
            return ""

        closing = self.closings[matter_id]

        summary = {
            "matter_id": matter_id,
            "closing_status": closing.closing_status.value,
            "completion_percentage": closing.get_completion_percentage(),
            "outcome": closing.outcome,
            "final_balance_due": closing.final_balance_due,
            "trust_balance": closing.trust_account_balance,
            "closing_date": datetime.now().isoformat(),
            "files_retained": closing.files_to_retain,
            "closing_checklist": {
                item_type: {
                    "completed": item.completed,
                    "completion_date": item.completion_date.isoformat() if item.completion_date else None
                }
                for item_type, item in closing.checklist_items.items()
            }
        }

        return json.dumps(summary, indent=2)


# Example usage
if __name__ == "__main__":
    automation = MatterClosingAutomation()

    closing = MatterClosing(
        matter_id="MAT-2024-001",
        client_id="CLI-001",
        closing_initiated_date=datetime.now(),
        expected_closing_date=datetime(2024, 12, 31)
    )

    automation.initiate_closing(closing)
    automation.generate_final_invoice("MAT-2024-001", {"total_due": 5000.00})
    automation.perform_trust_reconciliation("MAT-2024-001", 1200.00)
    automation.archive_matter_documents("MAT-2024-001", "/archive/MAT-2024-001")

    status = automation.get_closing_status("MAT-2024-001")
    print(f"Closing Status: {status}")
