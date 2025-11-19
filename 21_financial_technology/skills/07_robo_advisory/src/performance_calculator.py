"""Performance Calculator - Computes returns and risk metrics"""
import numpy as np
from typing import List, Tuple


class PerformanceCalculator:
    """Calculates performance metrics"""

    def __init__(self, returns: List[float], benchmark_returns: List[float]):
        self.returns = np.array(returns)
        self.benchmark = np.array(benchmark_returns)

    def total_return(self) -> float:
        """Calculate cumulative return"""
        return (np.prod(1 + self.returns) - 1) * 100

    def annualized_return(self, years: int) -> float:
        """Calculate annualized return"""
        total = self.total_return() / 100
        return ((1 + total) ** (1 / years) - 1) * 100

    def volatility(self) -> float:
        """Calculate annual volatility"""
        return np.std(self.returns) * np.sqrt(252) * 100

    def sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess = np.mean(self.returns) - (risk_free_rate / 252)
        return (excess * 252) / (np.std(self.returns) * np.sqrt(252))

    def maximum_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumprod(1 + self.returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown) * 100

    def information_ratio(self) -> float:
        """Calculate information ratio"""
        excess_return = self.returns - self.benchmark
        return np.mean(excess_return) / np.std(excess_return) * np.sqrt(252)

    def benchmark_outperformance(self) -> float:
        """Calculate excess return vs benchmark"""
        portfolio_return = self.total_return()
        benchmark_return = np.prod(1 + self.benchmark) - 1
        return (portfolio_return - benchmark_return * 100)
