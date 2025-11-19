"""Execution slippage analysis tool"""
import numpy as np
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    symbol: str
    entry_price: float
    execution_prices: list
    execution_quantities: list
    venue: str

class SlippageAnalyzer:
    def __init__(self):
        self.results = []

    def analyze_execution(self, result: ExecutionResult) -> dict:
        """Analyze slippage for a single execution"""

        # Calculate VWAP
        total_qty = sum(result.execution_quantities)
        vwap = sum(p * q for p, q in zip(
            result.execution_prices,
            result.execution_quantities
        )) / total_qty if total_qty > 0 else 0

        # Calculate slippage
        slippage_dollars = (vwap - result.entry_price) * total_qty
        slippage_bps = (vwap - result.entry_price) / result.entry_price * 10000

        # TWAP
        avg_price = sum(result.execution_prices) / len(result.execution_prices)
        twap_slippage = (avg_price - result.entry_price) * total_qty

        return {
            'symbol': result.symbol,
            'vwap': vwap,
            'vwap_slippage_dollars': slippage_dollars,
            'vwap_slippage_bps': slippage_bps,
            'twap_slippage_dollars': twap_slippage,
            'avg_execution_price': avg_price,
            'venue': result.venue
        }

    def analyze_venue_quality(self, venue: str) -> dict:
        """Analyze execution quality across a venue"""
        venue_results = [r for r in self.results if r['venue'] == venue]

        if not venue_results:
            return {}

        slippages = [r['vwap_slippage_bps'] for r in venue_results]

        return {
            'venue': venue,
            'avg_slippage_bps': np.mean(slippages),
            'median_slippage_bps': np.median(slippages),
            'std_slippage_bps': np.std(slippages),
            'best_execution_bps': np.min(slippages),
            'worst_execution_bps': np.max(slippages),
            'sample_size': len(venue_results)
        }
