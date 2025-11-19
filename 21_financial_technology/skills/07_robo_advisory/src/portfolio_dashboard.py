"""Portfolio Dashboard - Prepares dashboard data for client portal"""
from typing import Dict


class PortfolioDashboard:
    """Generates dashboard data for client viewing"""

    def __init__(self, portfolio: Dict, benchmark: str = 'SPY'):
        self.portfolio = portfolio
        self.benchmark = benchmark

    def get_summary(self) -> Dict:
        """Get portfolio summary"""
        total_value = sum(h['value'] for h in self.portfolio.values())
        return {
            'portfolio_value': total_value,
            'allocation_count': len(self.portfolio),
            'last_updated': 'today',
            'currency': 'USD'
        }

    def get_allocation_breakdown(self) -> Dict:
        """Get allocation by asset class"""
        total_value = sum(h['value'] for h in self.portfolio.values())
        breakdown = {}

        for symbol, holding in self.portfolio.items():
            weight = holding['value'] / total_value if total_value else 0
            breakdown[symbol] = {
                'value': holding['value'],
                'weight': weight,
                'allocation_pct': weight * 100
            }

        return breakdown

    def get_performance_overview(self, period: str = '1Y') -> Dict:
        """Get performance metrics"""
        # Simplified - would integrate with performance calculator
        return {
            'period': period,
            'return': '7.5%',
            'benchmark_return': '8.0%',
            'excess_return': '-0.5%',
            'volatility': '10.2%',
            'sharpe_ratio': 0.65
        }

    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        return {
            'summary': self.get_summary(),
            'allocation': self.get_allocation_breakdown(),
            'performance': self.get_performance_overview(),
            'last_rebalance': 'Q3 2024',
            'next_review': 'Q4 2024'
        }
