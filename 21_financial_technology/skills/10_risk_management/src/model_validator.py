"""
Model Validation Framework

Validates risk models through backtesting and other methods.
"""

import numpy as np
import pandas as pd
from scipy.stats import binom_test


class ModelValidator:
    """Validate risk models."""

    @staticmethod
    def backtest_var(var_estimates, actual_returns, confidence_level=0.95):
        """
        Backtest VaR model.

        Args:
            var_estimates: Array of VaR estimates
            actual_returns: Array of actual returns
            confidence_level: Confidence level (0.95, 0.99, etc.)

        Returns:
            Number of exceptions and test result
        """
        expected_exceptions_pct = 1 - confidence_level
        exceptions = (actual_returns < -var_estimates).sum()
        total_days = len(actual_returns)
        expected_exceptions = total_days * expected_exceptions_pct

        return {
            'Exceptions': exceptions,
            'Expected': expected_exceptions,
            'Total_Days': total_days,
        }

    @staticmethod
    def traffic_light(exceptions, total_days, confidence_level=0.95):
        """
        Traffic light test for VaR model.

        Args:
            exceptions: Number of VaR exceptions
            total_days: Total number of days in test period
            confidence_level: Confidence level

        Returns:
            Traffic light color (Green, Yellow, Red)
        """
        expected_pct = 1 - confidence_level

        # Typical 250 trading days, 95% VaR
        # Green: 0-4 exceptions
        # Yellow: 5-9 exceptions
        # Red: 10+ exceptions

        if confidence_level == 0.95:
            if exceptions <= 4:
                return 'Green'
            elif exceptions <= 9:
                return 'Yellow'
            else:
                return 'Red'
        else:
            return 'Unknown'

    @staticmethod
    def psi_calculation(baseline_distribution, current_distribution):
        """
        Calculate Population Stability Index (PSI).

        Args:
            baseline_distribution: Baseline score distribution (%)
            current_distribution: Current score distribution (%)

        Returns:
            PSI value
        """
        psi = np.sum((current_distribution - baseline_distribution) * 
                     np.log(current_distribution / baseline_distribution))
        return psi


# Example usage
if __name__ == "__main__":
    # Test VaR backtest
    np.random.seed(42)
    var_estimates = np.random.uniform(1000, 3000, 250)
    actual_returns = np.random.normal(-500, 2000, 250)

    backtest = ModelValidator.backtest_var(var_estimates, actual_returns)
    print("VaR Backtest Results:")
    print(f"  Exceptions: {backtest['Exceptions']}")
    print(f"  Expected: {backtest['Expected']:.1f}")

    # Traffic light
    light = ModelValidator.traffic_light(backtest['Exceptions'], backtest['Total_Days'])
    print(f"  Traffic Light: {light}")

    # PSI calculation
    baseline = np.array([0.10, 0.15, 0.25, 0.40, 0.10])  # Score distribution
    current = np.array([0.08, 0.14, 0.26, 0.42, 0.10])
    psi = ModelValidator.psi_calculation(baseline, current)
    print(f"\nPSI: {psi:.3f} (Stable if < 0.10)")
