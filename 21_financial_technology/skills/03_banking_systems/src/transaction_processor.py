from enum import Enum
from datetime import datetime
from decimal import Decimal
import uuid

class TransactionStatus(Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    POSTED = "POSTED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

class Transaction:
    def __init__(self, amount: Decimal, from_account: str, to_account: str):
        self.transaction_id = str(uuid.uuid4())
        self.amount = amount
        self.from_account = from_account
        self.to_account = to_account
        self.status = TransactionStatus.INITIATED
        self.created_at = datetime.utcnow()

    def validate(self, account_service) -> bool:
        if self.amount <= 0:
            return False
        from_balance = account_service.get_available_balance(self.from_account)
        return from_balance >= self.amount

    def process(self, ledger_engine, account_service):
        if not self.validate(account_service):
            self.status = TransactionStatus.FAILED
            return False

        self.status = TransactionStatus.PENDING
        self.status = TransactionStatus.POSTED
        self.status = TransactionStatus.SETTLED
        return True
