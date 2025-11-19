"""Portfolio Analytics - Comprehensive portfolio analysis"""
import numpy as np
from typing import Dict


class PortfolioAnalytics:
    """Provides detailed portfolio analytics"""

    def __init__(self, holdings: Dict):
        self.holdings = holdings  # {symbol: {'quantity': x, 'price': y, 'cost': z}}

    def calculate_metrics(self) -> Dict:
        """Calculate key portfolio metrics"""
        total_market_value = sum(h['quantity'] * h['price'] for h in self.holdings.values())
        total_cost = sum(h['quantity'] * h['cost'] for h in self.holdings.values())
        
        return {
            'total_value': total_market_value,
            'total_cost_basis': total_cost,
            'unrealized_gain': total_market_value - total_cost,
            'gain_percent': (total_market_value - total_cost) / total_cost if total_cost else 0,
            'num_positions': len(self.holdings)
        }

    def concentration_analysis(self) -> Dict:
        """Analyze position concentration"""
        total_value = sum(h['quantity'] * h['price'] for h in self.holdings.values())
        
        concentrations = {}
        for symbol, holding in self.holdings.items():
            position_value = holding['quantity'] * holding['price']
            weight = position_value / total_value if total_value else 0
            concentrations[symbol] = weight

        top_5 = sorted(concentrations.items(), key=lambda x: x[1], reverse=True)[:5]
        top_5_pct = sum(w for _, w in top_5)

        return {
            'concentrations': concentrations,
            'top_5': dict(top_5),
            'top_5_percent': top_5_pct
        }

    def dividend_analysis(self) -> Dict:
        """Analyze dividend income"""
        dividend_yields = {}
        total_income = 0

        for symbol, holding in self.holdings.items():
            # Simplified - in practice would use actual dividend data
            yield_estimate = 0.02  # 2% average yield
            position_value = holding['quantity'] * holding['price']
            income = position_value * yield_estimate
            total_income += income
            dividend_yields[symbol] = income

        return {
            'annual_dividend_income': total_income,
            'position_income': dividend_yields,
            'portfolio_yield': total_income / sum(h['quantity'] * h['price'] for h in self.holdings.values())
        }
