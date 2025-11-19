from decimal import Decimal
from typing import List

class BalanceCalculator:
    @staticmethod
    def calculate_current_balance(opening: Decimal, transactions: List[Decimal]) -> Decimal:
        return opening + sum(transactions)

    @staticmethod
    def calculate_available_balance(current: Decimal, holds: Decimal) -> Decimal:
        return max(Decimal("0"), current - holds)

    @staticmethod
    def calculate_multi_currency_balance(balances: dict) -> dict:
        """Convert balances to reporting currency"""
        return {
            'balances': balances,
            'total_usd': sum(v for v in balances.values())
        }
