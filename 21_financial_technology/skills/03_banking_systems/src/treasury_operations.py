from decimal import Decimal
from typing import Dict, List

class TreasuryOperations:
    def __init__(self):
        self.positions = {}
        self.interest_rates = {}

    def record_investment(self, security_id: str, amount: Decimal, rate: Decimal):
        self.positions[security_id] = {
            'amount': amount,
            'rate': rate,
            'date_purchased': None
        }

    def calculate_portfolio_value(self) -> Decimal:
        total = Decimal('0')
        for position in self.positions.values():
            total += position['amount']
        return total

    def manage_liquidity(self, target_buffer: Decimal, current_cash: Decimal):
        if current_cash > target_buffer:
            return current_cash - target_buffer
        return Decimal('0')
