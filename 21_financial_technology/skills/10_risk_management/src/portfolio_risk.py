"""
Portfolio Risk Analysis

Comprehensive portfolio risk analysis and optimization.
"""

import numpy as np
import pandas as pd


class PortfolioRisk:
    """Calculate and analyze portfolio risk."""

    @staticmethod
    def portfolio_variance(weights, cov_matrix):
        """Calculate portfolio variance."""
        variance = np.dot(weights, np.dot(cov_matrix, weights))
        return variance

    @staticmethod
    def portfolio_volatility(weights, cov_matrix):
        """Calculate portfolio standard deviation."""
        variance = PortfolioRisk.portfolio_variance(weights, cov_matrix)
        return np.sqrt(variance)

    @staticmethod
    def portfolio_expected_return(weights, returns):
        """Calculate portfolio expected return."""
        return np.dot(weights, returns)

    @staticmethod
    def sharpe_ratio(portfolio_return, portfolio_volatility, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        return (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

    @staticmethod
    def var_contribution(weights, cov_matrix, confidence_level=0.95):
        """
        Calculate Value at Risk contribution of each position.

        Args:
            weights: Position weights
            cov_matrix: Covariance matrix
            confidence_level: Confidence level

        Returns:
            VaR contribution per position
        """
        from scipy.stats import norm

        z_score = norm.ppf(confidence_level)
        portfolio_vol = PortfolioRisk.portfolio_volatility(weights, cov_matrix)
        marginal_var = np.dot(cov_matrix, weights) / portfolio_vol
        var_contrib = z_score * marginal_var

        return var_contrib

    @staticmethod
    def diversification_ratio(weights, volatilities, correlation_matrix):
        """Calculate diversification ratio."""
        weighted_vol = np.sum(weights * volatilities)
        portfolio_vol = PortfolioRisk.portfolio_volatility(weights, correlation_matrix)

        if portfolio_vol > 0:
            return weighted_vol / portfolio_vol
        else:
            return 0


# Example usage
if __name__ == "__main__":
    # Portfolio composition
    weights = np.array([0.6, 0.3, 0.1])  # 60% stocks, 30% bonds, 10% cash
    expected_returns = np.array([0.10, 0.04, 0.02])  # Expected returns

    # Covariance matrix
    cov_matrix = np.array([
        [0.04, -0.01, 0.0],
        [-0.01, 0.01, 0.0],
        [0.0, 0.0, 0.0]
    ])

    pr = PortfolioRisk()

    # Calculate metrics
    portfolio_return = pr.portfolio_expected_return(weights, expected_returns)
    portfolio_vol = pr.portfolio_volatility(weights, cov_matrix)
    sharpe = pr.sharpe_ratio(portfolio_return, portfolio_vol)

    print(f"Portfolio Expected Return: {portfolio_return:.2%}")
    print(f"Portfolio Volatility: {portfolio_vol:.2%}")
    print(f"Sharpe Ratio: {sharpe:.3f}")

    # VaR contribution
    var_contrib = pr.var_contribution(weights, cov_matrix)
    print(f"\nVaR Contribution by Position:")
    for i, contrib in enumerate(var_contrib):
        print(f"  Position {i+1}: {contrib:.4f}")
