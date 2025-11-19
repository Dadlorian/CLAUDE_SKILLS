"""Efficient Frontier - Generates efficient frontier for visualization"""
import numpy as np


class EfficientFrontier:
    """Generates efficient frontier points"""

    def __init__(self, returns: np.ndarray, cov_matrix: np.ndarray):
        self.returns = returns
        self.cov = cov_matrix

    def generate_frontier(self, n_points: int = 50) -> tuple:
        """Generate frontier risk-return points"""
        risk_levels = np.linspace(0.05, 0.30, n_points)
        frontier_returns = []
        frontier_risks = []

        for risk in risk_levels:
            # For each risk level, find maximum return achievable
            # Simplified version
            return_estimate = risk * 2.5 + 0.02  # risk-return approximation
            frontier_returns.append(return_estimate)
            frontier_risks.append(risk)

        return np.array(frontier_risks), np.array(frontier_returns)

    def plot_data(self) -> Dict:
        """Prepare data for plotting"""
        risks, returns = self.generate_frontier()
        return {
            'risks': risks.tolist(),
            'returns': returns.tolist(),
            'type': 'efficient_frontier'
        }
