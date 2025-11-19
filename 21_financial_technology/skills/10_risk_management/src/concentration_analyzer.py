"""
Concentration Risk Analysis

Measure and monitor portfolio concentration.
"""

import numpy as np
import pandas as pd


class ConcentrationAnalyzer:
    """Analyze portfolio concentration."""

    @staticmethod
    def concentration_ratio(exposures, n=10):
        """
        Calculate concentration ratio (Top N as % of total).

        Args:
            exposures: Array or Series of exposures
            n: Number of top exposures to sum

        Returns:
            Concentration ratio (0-1)
        """
        sorted_exposures = np.sort(exposures)[::-1]
        total = np.sum(exposures)
        cr = np.sum(sorted_exposures[:n]) / total
        return cr

    @staticmethod
    def herfindahl_index(exposures):
        """
        Calculate Herfindahl-Hirschman Index (HHI).

        Args:
            exposures: Array or Series of exposures

        Returns:
            HHI (0-1), higher = more concentrated
        """
        total = np.sum(exposures)
        weights = exposures / total
        hhi = np.sum(weights ** 2)
        return hhi

    @staticmethod
    def concentration_metrics(portfolio_df):
        """
        Calculate comprehensive concentration metrics.

        Args:
            portfolio_df: DataFrame with 'exposure' and 'counterparty' columns

        Returns:
            Dict with concentration metrics
        """
        exposures = portfolio_df['exposure'].values
        total = exposures.sum()

        cr_10 = ConcentrationAnalyzer.concentration_ratio(exposures, 10)
        hhi = ConcentrationAnalyzer.herfindahl_index(exposures)
        max_exposure = exposures.max() / total
        top_concentration = exposures.max()

        return {
            'Total': total,
            'CR_10': cr_10,
            'HHI': hhi,
            'Max_Exposure_%': max_exposure * 100,
            'Top_Exposure': top_concentration,
        }

    @staticmethod
    def limit_utilization(portfolio_df, limits_dict):
        """
        Check exposure limits.

        Args:
            portfolio_df: DataFrame with exposures
            limits_dict: Dict of limits by counterparty/sector

        Returns:
            DataFrame with limit utilization
        """
        results = []

        for counterparty, exposure in zip(portfolio_df['counterparty'], portfolio_df['exposure']):
            limit = limits_dict.get(counterparty, np.inf)
            utilization = (exposure / limit * 100) if limit < np.inf else 0

            results.append({
                'Counterparty': counterparty,
                'Exposure': exposure,
                'Limit': limit,
                'Utilization_%': utilization
            })

        return pd.DataFrame(results)


# Example usage
if __name__ == "__main__":
    portfolio = pd.DataFrame({
        'counterparty': ['Bank A', 'Corp B', 'Corp C', 'Corp D', 'Corp E'],
        'exposure': [50_000_000, 35_000_000, 30_000_000, 25_000_000, 20_000_000]
    })

    # Concentration metrics
    metrics = ConcentrationAnalyzer.concentration_metrics(portfolio)
    print("Concentration Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # Limit utilization
    limits = {
        'Bank A': 50_000_000,
        'Corp B': 40_000_000,
        'Corp C': 50_000_000,
    }

    utilization = ConcentrationAnalyzer.limit_utilization(portfolio, limits)
    print("\nLimit Utilization:")
    print(utilization)
