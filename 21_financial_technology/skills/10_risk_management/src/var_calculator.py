"""
Value at Risk (VaR) Calculator

Implements three VaR calculation approaches: Parametric, Historical Simulation, and Monte Carlo.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


class VaRCalculator:
    """Calculate Value at Risk using multiple methods."""

    @staticmethod
    def parametric_var(portfolio_value, returns_std, confidence_level=0.95, time_horizon=1):
        """
        Calculate Parametric (Delta-Normal) VaR.

        Args:
            portfolio_value: Current portfolio value
            returns_std: Standard deviation of returns (daily)
            confidence_level: Confidence level (0.95, 0.99, etc.)
            time_horizon: Time horizon in days

        Returns:
            VaR amount (positive = potential loss)
        """
        z_score = norm.ppf(1 - confidence_level)
        # Scale for time horizon
        time_factor = np.sqrt(time_horizon)
        var = portfolio_value * abs(z_score) * returns_std * time_factor
        return var

    @staticmethod
    def historical_var(returns, confidence_level=0.95, time_horizon=1):
        """
        Calculate Historical Simulation VaR.

        Args:
            returns: Array of historical returns
            confidence_level: Confidence level
            time_horizon: Time horizon in days

        Returns:
            VaR amount (positive = potential loss)
        """
        # Calculate portfolio values
        portfolio_values = 1 + returns.cumsum()

        # Find percentile for VaR
        percentile = (1 - confidence_level) * 100
        var_1day = np.abs(np.percentile(returns, percentile))

        # Scale for time horizon
        var = var_1day * np.sqrt(time_horizon)
        return var

    @staticmethod
    def monte_carlo_var(portfolio_value, returns_mean, returns_std, 
                       confidence_level=0.95, time_horizon=1, n_simulations=10000):
        """
        Calculate Monte Carlo VaR.

        Args:
            portfolio_value: Current portfolio value
            returns_mean: Mean return (daily)
            returns_std: Standard deviation of returns (daily)
            confidence_level: Confidence level
            time_horizon: Time horizon in days
            n_simulations: Number of simulations

        Returns:
            VaR amount (positive = potential loss)
        """
        # Generate random returns
        random_shocks = np.random.normal(0, 1, n_simulations)
        simulated_returns = returns_mean * time_horizon + returns_std * np.sqrt(time_horizon) * random_shocks

        # Calculate P&L
        simulated_pnl = portfolio_value * simulated_returns

        # Find VaR percentile
        percentile = (1 - confidence_level) * 100
        var = np.abs(np.percentile(simulated_pnl, percentile))

        return var

    @staticmethod
    def compare_methods(portfolio_value, returns_data, confidence_level=0.95):
        """
        Compare VaR across three methods.

        Args:
            portfolio_value: Current portfolio value
            returns_data: Historical returns data
            confidence_level: Confidence level

        Returns:
            Dictionary with VaR estimates from each method
        """
        returns_std = np.std(returns_data)
        returns_mean = np.mean(returns_data)

        results = {
            'Parametric': VaRCalculator.parametric_var(
                portfolio_value, returns_std, confidence_level
            ),
            'Historical Simulation': VaRCalculator.historical_var(
                returns_data, confidence_level
            ) * portfolio_value,
            'Monte Carlo': VaRCalculator.monte_carlo_var(
                portfolio_value, returns_mean, returns_std, confidence_level
            )
        }
        return results


# Example usage
if __name__ == "__main__":
    portfolio_value = 1_000_000
    
    # Generate sample returns
    np.random.seed(42)
    returns = np.random.normal(0.0002, 0.015, 250)  # 250 trading days
    
    # Calculate VaR
    calc = VaRCalculator()
    
    # Method 1: Parametric
    returns_std = np.std(returns)
    var_parametric = calc.parametric_var(portfolio_value, returns_std, 0.95)
    print(f"95% VaR (Parametric): ${var_parametric:,.2f}")
    
    # Method 2: Historical Simulation
    var_historical = calc.historical_var(returns, 0.95)
    print(f"95% VaR (Historical): ${var_historical * portfolio_value:,.2f}")
    
    # Method 3: Monte Carlo
    var_mc = calc.monte_carlo_var(
        portfolio_value, np.mean(returns), returns_std, 0.95
    )
    print(f"95% VaR (Monte Carlo): ${var_mc:,.2f}")
