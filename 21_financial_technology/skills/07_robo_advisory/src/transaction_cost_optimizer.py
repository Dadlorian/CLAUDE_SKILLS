"""Transaction Cost Optimizer - Minimizes trading costs"""


class TransactionCostOptimizer:
    """Optimizes trade execution to minimize costs"""

    def estimate_trading_costs(self, trades: list, spreads: Dict) -> float:
        """Estimate total trading costs"""
        total_cost = 0

        for trade in trades:
            symbol = trade['symbol']
            amount = abs(trade['amount'])
            spread = spreads.get(symbol, 0.0005)  # Default 5 bps
            cost = amount * spread / 2
            total_cost += cost

        return total_cost

    def optimize_trade_sequence(self, trades: list, spreads: Dict) -> list:
        """Optimize trade order to minimize market impact"""
        # Execute higher spread securities first
        return sorted(trades,
                     key=lambda t: spreads.get(t['symbol'], 0.0005),
                     reverse=True)

    def calculate_cost_impact(self, cost: float, portfolio_value: float) -> float:
        """Calculate cost as percentage of portfolio"""
        return (cost / portfolio_value) * 100 if portfolio_value > 0 else 0
