"""
Tax-Loss Harvester - Identifies and executes tax loss harvesting
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class TaxLossHarvester:
    """Identifies and executes tax-loss harvesting"""

    def __init__(self, portfolio: List[Dict], lookback_days: int = 30):
        self.portfolio = portfolio
        self.lookback_days = lookback_days
        self.wash_sale_window = 61  # 30 days before and after

    def identify_losses(self, current_date: datetime) -> List[Dict]:
        """Identify positions with unrealized losses"""
        harvestable = []
        
        for position in self.portfolio:
            unrealized_loss = position['cost_basis'] - position['current_value']

            if unrealized_loss > 100:  # Minimum $100 loss
                if not self.violates_wash_sale(position, current_date):
                    harvestable.append({
                        'symbol': position['symbol'],
                        'loss': unrealized_loss,
                        'cost_basis': position['cost_basis'],
                        'current_value': position['current_value']
                    })

        return sorted(harvestable, key=lambda x: x['loss'], reverse=True)

    def violates_wash_sale(self, position: Dict, current_date: datetime) -> bool:
        """Check if position violates wash-sale rules"""
        last_purchase = position.get('last_purchase_date')
        if not last_purchase:
            return False

        days_since = (current_date - last_purchase).days
        return days_since < self.lookback_days

    def calculate_tax_benefit(self, loss: float, tax_rate: float = 0.25) -> float:
        """Calculate tax benefit of harvesting loss"""
        return loss * tax_rate

    def find_replacement_security(self, symbol: str) -> str:
        """Find suitable replacement security to maintain exposure"""
        replacements = {
            'AAPL': ['VTI', 'VOO'],  # S&P 500
            'BND': ['SCHZ', 'AGG'],  # Alternative bond fund
            'VEA': ['VXUS', 'IEFA'],  # Alternative international
        }
        return replacements.get(symbol, ['VTI'])[0]
