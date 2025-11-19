"""Transaction cost analysis and optimization"""
import numpy as np

class TransactionCostAnalyzer:
    """Analyze and optimize trading costs"""

    def __init__(self):
        self.trades = []

    def analyze_trade_costs(self, trade):
        """Break down costs for a single trade"""
        costs = {
            'symbol': trade['symbol'],
            'quantity': trade['quantity'],
            'entry_price': trade['entry_price'],
            'execution_price': trade['execution_price'],
            'venue': trade['venue']
        }

        # 1. Explicit costs
        exchange_fee = trade['quantity'] * trade['exchange_fee_per_share']
        broker_fee = trade['quantity'] * trade['broker_fee_per_share']
        costs['explicit_costs'] = exchange_fee + broker_fee
        costs['explicit_bps'] = costs['explicit_costs'] / (
            trade['execution_price'] * trade['quantity']) * 10000

        # 2. Implicit costs - spread
        mid_price = (trade['bid'] + trade['ask']) / 2
        spread_cost = abs(trade['execution_price'] - mid_price) * trade['quantity']
        costs['spread_cost'] = spread_cost
        costs['spread_bps'] = spread_cost / (
            trade['execution_price'] * trade['quantity']) * 10000

        # 3. Implicit costs - market impact
        market_impact = abs(trade['post_trade_mid'] - mid_price) * trade['quantity']
        costs['market_impact'] = market_impact
        costs['market_impact_bps'] = market_impact / (
            trade['execution_price'] * trade['quantity']) * 10000

        # Total
        costs['total_cost'] = (costs['explicit_costs'] +
                              costs['spread_cost'] +
                              costs['market_impact'])
        costs['total_bps'] = (costs['explicit_bps'] +
                             costs['spread_bps'] +
                             costs['market_impact_bps'])

        self.trades.append(costs)
        return costs

    def optimize_execution_timing(self, order_size, market_volume):
        """Suggest optimal execution timing based on volume"""
        # POIV algorithm: execute as % of market volume
        participation_rate = 0.10  # 10% of market volume

        optimal_slice = market_volume * participation_rate
        if optimal_slice < order_size / 100:  # Too small
            participation_rate = 0.20
            optimal_slice = market_volume * participation_rate

        return {
            'optimal_slice_size': int(optimal_slice),
            'participation_rate': participation_rate,
            'expected_duration_minutes': order_size / optimal_slice
        }

    def get_summary_statistics(self):
        """Get summary statistics for all trades"""
        if not self.trades:
            return {}

        total_bps = [t['total_bps'] for t in self.trades]

        return {
            'avg_total_cost_bps': np.mean(total_bps),
            'median_total_cost_bps': np.median(total_bps),
            'std_total_cost_bps': np.std(total_bps),
            'best_execution_bps': np.min(total_bps),
            'worst_execution_bps': np.max(total_bps),
            'total_trades': len(self.trades)
        }
