"""
Portfolio Optimizer - Mean-Variance and Black-Litterman Optimization
Implements efficient frontier and optimal portfolio construction algorithms
"""

import numpy as np
from scipy.optimize import minimize
from typing import Tuple, Dict, List


class PortfolioOptimizer:
    """Mean-variance portfolio optimization"""

    def __init__(self, expected_returns: np.ndarray, cov_matrix: np.ndarray,
                 asset_names: List[str] = None):
        """
        Initialize optimizer with return expectations and covariance matrix
        """
        self.mu = expected_returns
        self.cov = cov_matrix
        self.n_assets = len(expected_returns)
        self.asset_names = asset_names or [f"Asset_{i}" for i in range(self.n_assets)]

    def portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float]:
        """Calculate portfolio return and volatility"""
        ret = np.sum(weights * self.mu)
        var = np.dot(weights, np.dot(self.cov, weights))
        return ret, np.sqrt(var)

    def optimize_min_variance(self) -> np.ndarray:
        """Find minimum variance portfolio"""
        def objective(w):
            return np.dot(w, np.dot(self.cov, w))

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        init_guess = np.array([1/self.n_assets] * self.n_assets)

        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=constraints)
        return result.x if result.success else None

    def optimize_sharpe_ratio(self, risk_free_rate: float = 0.02) -> np.ndarray:
        """Find portfolio with maximum Sharpe ratio"""
        def objective(w):
            ret, std = self.portfolio_stats(w)
            return -(ret - risk_free_rate) / std if std > 0 else 1e10

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        init_guess = np.array([1/self.n_assets] * self.n_assets)

        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=constraints)
        return result.x if result.success else None

    def efficient_frontier(self, n_points: int = 50) -> Tuple[List, List, List]:
        """Generate efficient frontier points"""
        min_ret = np.min(self.mu)
        max_ret = np.max(self.mu)
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier_weights, frontier_returns, frontier_risks = [], [], []

        for target_ret in target_returns:
            def objective(w):
                return np.dot(w, np.dot(self.cov, w))

            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.sum(w * self.mu) - target_ret}
            ]

            bounds = tuple((0, 1) for _ in range(self.n_assets))
            init_guess = np.array([1/self.n_assets] * self.n_assets)

            result = minimize(objective, init_guess, method='SLSQP',
                             bounds=bounds, constraints=constraints)

            if result.success:
                ret, risk = self.portfolio_stats(result.x)
                frontier_weights.append(result.x)
                frontier_returns.append(ret)
                frontier_risks.append(risk)

        return frontier_weights, frontier_returns, frontier_risks

    def optimize_with_constraints(self, constraints: Dict) -> np.ndarray:
        """Optimize portfolio with practical constraints"""
        def objective(w):
            return np.dot(w, np.dot(self.cov, w))

        scipy_constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]

        bounds = []
        max_position = constraints.get('max_position', 0.20)

        for _ in range(self.n_assets):
            bounds.append((0, max_position))

        init_guess = np.array([1/self.n_assets] * self.n_assets)
        result = minimize(objective, init_guess, method='SLSQP',
                         bounds=bounds, constraints=scipy_constraints)

        return result.x if result.success else None
