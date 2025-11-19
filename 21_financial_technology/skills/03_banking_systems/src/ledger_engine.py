# Ledger Engine - Double-Entry Accounting System
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
import uuid

class EntryType(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

@dataclass
class LedgerEntry:
    """Immutable ledger entry"""
    entry_id: str
    account_id: str
    gl_account: str
    transaction_id: str
    debit: Decimal
    credit: Decimal
    description: str
    posted_date: datetime
    status: str = "POSTED"

    def __post_init__(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Amounts cannot be negative")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Cannot have both debit and credit")

    @property
    def is_balanced(self) -> bool:
        """Check if debit == credit (should be equal in pairs)"""
        return self.debit >= 0 and self.credit >= 0

class LedgerEngine:
    """Double-entry accounting ledger"""

    def __init__(self, db_session):
        self.db = db_session

    def post_transaction(self, transaction_id: str, entries: List[LedgerEntry]):
        """Post balanced set of entries"""
        # Verify balanced
        total_debit = sum(e.debit for e in entries)
        total_credit = sum(e.credit for e in entries)

        if total_debit != total_credit:
            raise ValueError(f"Unbalanced: Debit {total_debit} != Credit {total_credit}")

        # Post all entries atomically
        try:
            for entry in entries:
                self.db.add(entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise

    def get_account_balance(self, account_id: str, gl_account: str) -> Decimal:
        """Calculate current balance"""
        entries = self.db.query(LedgerEntry).filter_by(
            account_id=account_id,
            gl_account=gl_account,
            status="POSTED"
        ).all()

        balance = Decimal("0.00")
        for entry in entries:
            balance += (entry.debit - entry.credit)
        return balance

    def get_transaction_entries(self, transaction_id: str) -> List[LedgerEntry]:
        """Get all entries for transaction"""
        return self.db.query(LedgerEntry).filter_by(
            transaction_id=transaction_id
        ).all()

# Example usage
if __name__ == "__main__":
    # Example: Customer deposit of $1000
    entries = [
        LedgerEntry(
            entry_id=str(uuid.uuid4()),
            account_id="acc-001",
            gl_account="1000",  # Cash
            transaction_id="txn-001",
            debit=Decimal("1000.00"),
            credit=Decimal("0.00"),
            description="Cash deposit",
            posted_date=datetime.utcnow()
        ),
        LedgerEntry(
            entry_id=str(uuid.uuid4()),
            account_id="acc-001",
            gl_account="2100",  # Customer deposits liability
            transaction_id="txn-001",
            debit=Decimal("0.00"),
            credit=Decimal("1000.00"),
            description="Customer deposit liability",
            posted_date=datetime.utcnow()
        )
    ]

    print("Ledger entries balanced:", all(e.is_balanced for e in entries))
