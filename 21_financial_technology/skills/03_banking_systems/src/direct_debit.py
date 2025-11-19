from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from datetime import datetime

class DirectDebitStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"

@dataclass
class DirectDebit:
    mandate_id: str
    creditor_id: str
    account_id: str
    amount: Decimal
    frequency: str  # DAILY, WEEKLY, MONTHLY
    next_due_date: datetime
    status: DirectDebitStatus

class DirectDebitManager:
    def setup_mandate(self, creditor_id: str, account_id: str, amount: Decimal) -> str:
        # Create and return mandate ID
        return 'mandate-001'

    def process_direct_debit(self, mandate_id: str) -> bool:
        # Process payment
        return True

    def cancel_mandate(self, mandate_id: str):
        # Cancel direct debit
        pass
