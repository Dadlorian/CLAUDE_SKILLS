"""Benchmark Comparison - Compares portfolio to benchmarks"""


class BenchmarkComparison:
    """Compares portfolio performance to benchmarks"""

    def get_appropriate_benchmark(self, allocation: Dict) -> str:
        """Determine appropriate benchmark"""
        equity_pct = allocation.get('equities', 0)

        if equity_pct > 0.75:
            return 'SPY'  # S&P 500
        elif equity_pct > 0.40:
            return 'VBTLX'  # 60/40 blend
        else:
            return 'BND'  # Bonds

    def calculate_excess_return(self, portfolio_return: float,
                               benchmark_return: float) -> float:
        """Calculate outperformance/underperformance"""
        return portfolio_return - benchmark_return

    def generate_comparison_report(self, portfolio_return: float,
                                  benchmark_return: float) -> Dict:
        """Generate comparison report"""
        excess = self.calculate_excess_return(portfolio_return, benchmark_return)

        return {
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'excess_return': excess,
            'performance': 'OUTPERFORMING' if excess > 0 else 'UNDERPERFORMING'
        }
