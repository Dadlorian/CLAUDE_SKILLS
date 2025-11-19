"""
Portfolio Rebalancer - Automated rebalancing with tax and cost optimization
"""
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


class PortfolioRebalancer:
    """Automates rebalancing with optimization"""

    def __init__(self, portfolio: Dict, target_allocation: Dict):
        self.portfolio = portfolio
        self.target = target_allocation
        self.trades = []

    def calculate_drift(self) -> Dict:
        """Calculate current drift from target allocation"""
        total_value = sum(self.portfolio.values())
        drift = {}
        for asset, value in self.portfolio.items():
            current_weight = value / total_value
            target_weight = self.target[asset]
            drift[asset] = current_weight - target_weight
        return drift

    def should_rebalance(self, threshold: float = 0.05) -> bool:
        """Check if rebalancing is needed"""
        drift = self.calculate_drift()
        max_drift = max(abs(d) for d in drift.values())
        return max_drift > threshold

    def generate_trades(self) -> List[Dict]:
        """Generate trades to rebalance portfolio"""
        total_value = sum(self.portfolio.values())
        trades = []
        
        for asset, target_weight in self.target.items():
            target_value = total_value * target_weight
            current_value = self.portfolio[asset]
            trade_amount = target_value - current_value

            if abs(trade_amount) > 1:  # Minimum trade size
                trades.append({
                    'asset': asset,
                    'amount': trade_amount,
                    'action': 'BUY' if trade_amount > 0 else 'SELL'
                })

        self.trades = trades
        return trades

    def optimize_for_costs(self, bid_ask_spreads: Dict) -> List[Dict]:
        """Optimize trade sequence to minimize costs"""
        trades = sorted(self.trades, 
                       key=lambda t: bid_ask_spreads.get(t['asset'], 0.0005),
                       reverse=True)
        return trades
