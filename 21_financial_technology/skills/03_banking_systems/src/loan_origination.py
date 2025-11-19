from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

class LoanStatus(Enum):
    APPLICATION = "APPLICATION"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    FUNDED = "FUNDED"

@dataclass
class LoanApplication:
    application_id: str
    customer_id: str
    amount: Decimal
    term_months: int
    purpose: str
    status: LoanStatus

class LoanOriginator:
    def apply_for_loan(self, customer_id: str, amount: Decimal, term: int) -> LoanApplication:
        app = LoanApplication(
            application_id='app-001',
            customer_id=customer_id,
            amount=amount,
            term_months=term,
            purpose='personal',
            status=LoanStatus.APPLICATION
        )
        return app

    def approve_loan(self, application_id: str) -> LoanApplication:
        # Implement approval logic
        pass
