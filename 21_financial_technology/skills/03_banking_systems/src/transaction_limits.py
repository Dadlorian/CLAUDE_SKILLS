from decimal import Decimal
from typing import Dict

class TransactionLimits:
    def __init__(self, account_type: str):
        self.account_type = account_type
        self.daily_limit = self._get_daily_limit()
        self.transaction_limit = self._get_transaction_limit()

    def _get_daily_limit(self) -> Decimal:
        limits = {
            'CHECKING': Decimal('10000'),
            'SAVINGS': Decimal('5000'),
            'MONEY_MARKET': Decimal('25000')
        }
        return limits.get(self.account_type, Decimal('5000'))

    def _get_transaction_limit(self) -> Decimal:
        limits = {
            'CHECKING': Decimal('50000'),
            'SAVINGS': Decimal('25000'),
            'MONEY_MARKET': Decimal('100000')
        }
        return limits.get(self.account_type, Decimal('25000'))

    def check_limit(self, amount: Decimal, daily_used: Decimal) -> bool:
        if amount > self.transaction_limit:
            return False
        if daily_used + amount > self.daily_limit:
            return False
        return True
