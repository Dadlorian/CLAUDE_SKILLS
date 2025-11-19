# Account Service - Core Banking Account Management
# Production-ready Python service for managing customer accounts

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class AccountStatus(Enum):
    """Account status enumeration"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"
    DORMANT = "DORMANT"
    PENDING = "PENDING"


class AccountType(Enum):
    """Account type enumeration"""
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEY_MARKET"
    CD = "CD"
    LOAN = "LOAN"
    INVESTMENT = "INVESTMENT"


@dataclass
class Account:
    """Account data class"""
    account_id: str
    customer_id: str
    account_type: AccountType
    account_number: str
    account_name: str
    status: AccountStatus
    current_balance: Decimal
    available_balance: Decimal
    currency: str
    opened_date: datetime
    closed_date: Optional[datetime] = None
    interest_rate: Decimal = Decimal("0.00")
    monthly_fee: Decimal = Decimal("0.00")
    min_balance: Decimal = Decimal("0.00")
    product_id: Optional[str] = None

    def __post_init__(self):
        """Validate account invariants"""
        if self.current_balance < 0:
            raise ValueError("Current balance cannot be negative")
        if self.available_balance > self.current_balance:
            raise ValueError("Available balance cannot exceed current balance")
        if self.status == AccountStatus.CLOSED and self.closed_date is None:
            raise ValueError("Closed accounts must have a closed_date")


class AccountRepository:
    """Repository for account persistence"""

    def __init__(self, db_session):
        """Initialize with database session"""
        self.db = db_session

    def create_account(self, account: Account) -> Account:
        """Create a new account"""
        try:
            logger.info(f"Creating account {account.account_id} for customer {account.customer_id}")

            # Validate account number uniqueness
            existing = self.db.query(AccountModel).filter_by(
                account_number=account.account_number
            ).first()

            if existing:
                raise ValueError(f"Account number {account.account_number} already exists")

            # Create database record
            db_account = AccountModel(
                account_id=account.account_id,
                customer_id=account.customer_id,
                account_type=account.account_type.value,
                account_number=account.account_number,
                account_name=account.account_name,
                status=account.status.value,
                current_balance=account.current_balance,
                available_balance=account.available_balance,
                currency=account.currency,
                opened_date=account.opened_date,
                interest_rate=account.interest_rate,
                monthly_fee=account.monthly_fee,
                min_balance=account.min_balance,
                product_id=account.product_id
            )

            self.db.add(db_account)
            self.db.commit()

            logger.info(f"Account {account.account_id} created successfully")
            return account

        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            self.db.rollback()
            raise

    def get_account(self, account_id: str) -> Optional[Account]:
        """Retrieve account by ID"""
        try:
            db_account = self.db.query(AccountModel).filter_by(
                account_id=account_id
            ).first()

            if not db_account:
                logger.warning(f"Account {account_id} not found")
                return None

            return self._db_to_domain(db_account)

        except Exception as e:
            logger.error(f"Error retrieving account: {str(e)}")
            raise

    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        """Retrieve all accounts for a customer"""
        try:
            db_accounts = self.db.query(AccountModel).filter_by(
                customer_id=customer_id
            ).all()

            return [self._db_to_domain(acc) for acc in db_accounts]

        except Exception as e:
            logger.error(f"Error retrieving customer accounts: {str(e)}")
            raise

    def update_account_balance(self, account_id: str, new_balance: Decimal) -> Account:
        """Update account balance with validation"""
        try:
            db_account = self.db.query(AccountModel).filter_by(
                account_id=account_id
            ).first()

            if not db_account:
                raise ValueError(f"Account {account_id} not found")

            if new_balance < 0:
                raise ValueError("Balance cannot be negative")

            db_account.current_balance = new_balance
            db_account.updated_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"Account {account_id} balance updated to {new_balance}")
            return self._db_to_domain(db_account)

        except Exception as e:
            logger.error(f"Error updating balance: {str(e)}")
            self.db.rollback()
            raise

    def close_account(self, account_id: str) -> Account:
        """Close an account"""
        try:
            db_account = self.db.query(AccountModel).filter_by(
                account_id=account_id
            ).first()

            if not db_account:
                raise ValueError(f"Account {account_id} not found")

            # Verify zero balance
            if db_account.current_balance != 0:
                raise ValueError("Cannot close account with non-zero balance")

            db_account.status = AccountStatus.CLOSED.value
            db_account.closed_date = datetime.utcnow()
            db_account.updated_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"Account {account_id} closed successfully")
            return self._db_to_domain(db_account)

        except Exception as e:
            logger.error(f"Error closing account: {str(e)}")
            self.db.rollback()
            raise

    @staticmethod
    def _db_to_domain(db_account) -> Account:
        """Convert database model to domain model"""
        return Account(
            account_id=db_account.account_id,
            customer_id=db_account.customer_id,
            account_type=AccountType(db_account.account_type),
            account_number=db_account.account_number,
            account_name=db_account.account_name,
            status=AccountStatus(db_account.status),
            current_balance=Decimal(str(db_account.current_balance)),
            available_balance=Decimal(str(db_account.available_balance)),
            currency=db_account.currency,
            opened_date=db_account.opened_date,
            closed_date=db_account.closed_date,
            interest_rate=Decimal(str(db_account.interest_rate)),
            monthly_fee=Decimal(str(db_account.monthly_fee)),
            min_balance=Decimal(str(db_account.min_balance)),
            product_id=db_account.product_id
        )


class AccountService:
    """Service for account operations"""

    def __init__(self, repository: AccountRepository):
        """Initialize with repository"""
        self.repository = repository

    def open_account(
        self,
        customer_id: str,
        account_type: AccountType,
        account_name: str,
        currency: str = "USD",
        initial_balance: Decimal = Decimal("0.00"),
        product_id: Optional[str] = None
    ) -> Account:
        """Open a new account"""

        # Generate unique account ID and number
        account_id = str(uuid.uuid4())
        account_number = self._generate_account_number()

        # Create account
        account = Account(
            account_id=account_id,
            customer_id=customer_id,
            account_type=account_type,
            account_number=account_number,
            account_name=account_name,
            status=AccountStatus.ACTIVE,
            current_balance=initial_balance,
            available_balance=initial_balance,
            currency=currency,
            opened_date=datetime.utcnow(),
            product_id=product_id
        )

        # Persist
        return self.repository.create_account(account)

    def get_account_balance(self, account_id: str) -> Decimal:
        """Get current account balance"""
        account = self.repository.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        return account.current_balance

    def get_available_balance(self, account_id: str) -> Decimal:
        """Get available balance (excluding holds)"""
        account = self.repository.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        return account.available_balance

    def list_customer_accounts(self, customer_id: str) -> List[Account]:
        """List all accounts for customer"""
        return self.repository.get_customer_accounts(customer_id)

    def close_account_safely(self, account_id: str) -> Account:
        """Close account after verification"""
        account = self.repository.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if account.status == AccountStatus.CLOSED:
            raise ValueError("Account is already closed")

        # Must have zero balance to close
        if account.current_balance != 0:
            raise ValueError(f"Cannot close account with balance {account.current_balance}")

        return self.repository.close_account(account_id)

    @staticmethod
    def _generate_account_number() -> str:
        """Generate unique account number"""
        return str(uuid.uuid4())[:12]


# Example usage
if __name__ == "__main__":
    from unittest.mock import MagicMock

    # Mock database session
    mock_db = MagicMock()
    repo = AccountRepository(mock_db)
    service = AccountService(repo)

    # Open account
    account = service.open_account(
        customer_id="cust-001",
        account_type=AccountType.CHECKING,
        account_name="Primary Checking",
        currency="USD",
        initial_balance=Decimal("1000.00")
    )

    print(f"Account opened: {account.account_id}")
    print(f"Account number: {account.account_number}")
    print(f"Balance: {account.current_balance}")
