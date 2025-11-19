"""Currency conversion and FX management"""
import logging
from decimal import Decimal

class CurrencyConverter:
    def __init__(self, fx_provider):
        self.fx = fx_provider
        self.logger = logging.getLogger(__name__)

    async def convert(self, amount, from_currency, to_currency, direction='sell'):
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount
        
        rate = await self._get_rate(from_currency, to_currency)
        
        if direction == 'sell':
            rate = rate['bid']  # Use bid if selling to bank
        else:
            rate = rate['ask']  # Use ask if buying from bank
        
        return Decimal(str(amount)) * Decimal(str(rate))

    async def _get_rate(self, from_currency, to_currency):
        return await self.fx.get_rate(f"{from_currency}/{to_currency}")

    async def lock_forward_rate(self, amount, from_currency, to_currency, days=30):
        """Lock exchange rate for future date"""
        rate_data = await self.fx.get_forward_rate(
            from_currency, to_currency, days
        )
        
        locked_amount = Decimal(str(amount)) * Decimal(str(rate_data['rate']))
        
        return {
            'locked_amount': locked_amount,
            'rate': rate_data['rate'],
            'expiry_days': days,
            'cost': rate_data['cost']
        }
