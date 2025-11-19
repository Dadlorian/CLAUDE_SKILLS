"""
Correlation and Copula Calculations

Calculate correlations and dependencies between risk factors.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau


class CorrelationCalculator:
    """Calculate correlations and copulas."""

    @staticmethod
    def pearson_correlation(returns_df):
        """Calculate Pearson correlation matrix."""
        return returns_df.corr(method='pearson')

    @staticmethod
    def spearman_correlation(returns_df):
        """Calculate Spearman (rank) correlation."""
        return returns_df.corr(method='spearman')

    @staticmethod
    def rolling_correlation(series1, series2, window=30):
        """
        Calculate rolling correlation between two series.

        Args:
            series1: First return series
            series2: Second return series
            window: Rolling window size

        Returns:
            Series of rolling correlations
        """
        rolling_corr = pd.Series([
            series1.iloc[i:i+window].corr(series2.iloc[i:i+window])
            for i in range(len(series1) - window + 1)
        ])
        return rolling_corr

    @staticmethod
    def correlation_stress(normal_corr, stress_scenario='crisis'):
        """
        Adjust correlation for stress scenarios.

        Args:
            normal_corr: Normal correlation matrix
            stress_scenario: Stress type ('mild', 'crisis', 'systemic')

        Returns:
            Stressed correlation matrix
        """
        if stress_scenario == 'crisis':
            # Correlations increase toward 1 in crisis
            stressed = normal_corr * 0.7 + 0.3  # 30% shift toward 1
        elif stress_scenario == 'systemic':
            # All correlations become highly positive
            stressed = np.ones_like(normal_corr) * 0.8
            np.fill_diagonal(stressed, 1.0)
        else:
            stressed = normal_corr

        return stressed

    @staticmethod
    def tail_correlation(returns_df, tail_pct=5):
        """
        Calculate correlation in tail events (extreme losses).

        Args:
            returns_df: Returns dataframe
            tail_pct: Percentile for tail definition

        Returns:
            Tail correlation matrix
        """
        threshold = returns_df.quantile(tail_pct / 100)
        tail_returns = returns_df[returns_df <= threshold]

        if len(tail_returns) > 2:
            tail_corr = tail_returns.corr()
        else:
            tail_corr = returns_df.corr()

        return tail_corr


# Example usage
if __name__ == "__main__":
    # Create sample returns
    np.random.seed(42)
    returns = pd.DataFrame({
        'Stock_A': np.random.normal(0.0001, 0.015, 250),
        'Stock_B': np.random.normal(0.0001, 0.015, 250),
        'Bond_Index': np.random.normal(0.00005, 0.005, 250),
    })

    calc = CorrelationCalculator()

    # Pearson correlation
    pearson = calc.pearson_correlation(returns)
    print("Pearson Correlation:")
    print(pearson)

    # Stressed correlation
    stressed = calc.correlation_stress(pearson.values, 'crisis')
    print("\nStressed Correlation (Crisis):")
    print(stressed)

    # Tail correlation
    tail_corr = calc.tail_correlation(returns)
    print("\nTail Correlation (5th percentile):")
    print(tail_corr)
