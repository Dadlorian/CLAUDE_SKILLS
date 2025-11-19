from decimal import Decimal
from typing import Dict

class MultiCurrencyManager:
    def __init__(self):
        self.exchange_rates = {
            'USD': Decimal('1.00'),
            'EUR': Decimal('1.10'),
            'GBP': Decimal('1.27'),
            'JPY': Decimal('0.0093')
        }

    def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return amount

        amount_usd = amount / self.exchange_rates[from_currency]
        return amount_usd * self.exchange_rates[to_currency]

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        return self.exchange_rates.get(to_currency, Decimal('1.00'))
