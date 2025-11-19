from decimal import Decimal
from datetime import datetime

class FXRateProvider:
    def __init__(self):
        self.rates = {}
        self.last_update = None

    def fetch_rates(self) -> Dict:
        # Fetch from provider (OpenExchangeRates, ECB, etc.)
        self.last_update = datetime.utcnow()
        return self.rates

    def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        key = f"{from_currency}/{to_currency}"
        return self.rates.get(key, Decimal('1.00'))

    def quote_exchange(self, amount: Decimal, from_curr: str, to_curr: str):
        rate = self.get_rate(from_curr, to_curr)
        converted = amount * rate
        spread = converted * Decimal('0.001')  # 0.1% spread
        return {
            'original_amount': amount,
            'from_currency': from_curr,
            'to_currency': to_curr,
            'rate': rate,
            'converted_amount': converted,
            'fee': spread,
            'total': converted - spread
        }
