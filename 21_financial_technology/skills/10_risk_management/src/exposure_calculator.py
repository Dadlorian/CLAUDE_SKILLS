"""
Exposure Calculation and Aggregation

Calculate and aggregate exposures across portfolio.
"""

import pandas as pd
import numpy as np


class ExposureCalculator:
    """Calculate and aggregate portfolio exposures."""

    @staticmethod
    def calculate_gross_exposure(positions_df):
        """Calculate gross exposure (sum of absolute values)."""
        return positions_df['amount'].abs().sum()

    @staticmethod
    def calculate_net_exposure(positions_df):
        """Calculate net exposure (sum with signs)."""
        return positions_df['amount'].sum()

    @staticmethod
    def calculate_net_exposure_with_netting(positions_df, netting_rules=None):
        """
        Calculate net exposure with bilateral netting.

        Args:
            positions_df: DataFrame with positions
            netting_rules: Dict of netting rules

        Returns:
            Net exposure after netting
        """
        if netting_rules is None:
            # Default: Assets and liabilities to same counterparty net
            net_by_counterparty = positions_df.groupby('counterparty')['amount'].sum()
            return net_by_counterparty.abs().sum()
        else:
            # Apply custom netting rules
            return positions_df['amount'].sum()

    @staticmethod
    def exposure_by_category(positions_df, category_column):
        """Aggregate exposure by category."""
        return positions_df.groupby(category_column)['amount'].sum()

    @staticmethod
    def exposure_concentration(positions_df):
        """Calculate concentration of exposures."""
        total = positions_df['amount'].abs().sum()
        sorted_exposures = positions_df['amount'].abs().sort_values(ascending=False)
        cumsum = sorted_exposures.cumsum()

        return {
            'Total': total,
            'Top_1_%': (sorted_exposures.iloc[0] / total) if len(sorted_exposures) > 0 else 0,
            'Top_10_Pct': (cumsum.iloc[min(9, len(cumsum)-1)] / total) if len(cumsum) > 0 else 0,
        }


# Example usage
if __name__ == "__main__":
    positions = pd.DataFrame({
        'counterparty': ['Bank A', 'Bank A', 'Corp B', 'Corp C', 'Corp B'],
        'amount': [50_000_000, -30_000_000, 40_000_000, 20_000_000, -15_000_000],
        'asset_class': ['Equities', 'Bonds', 'Equities', 'Bonds', 'Equities']
    })

    calc = ExposureCalculator()

    # Gross vs. Net
    gross = calc.calculate_gross_exposure(positions)
    net = calc.calculate_net_exposure(positions)
    print(f"Gross Exposure: ${gross:,.0f}")
    print(f"Net Exposure: ${net:,.0f}")

    # Net with netting
    net_netting = calc.calculate_net_exposure_with_netting(positions)
    print(f"Net with Bilateral Netting: ${net_netting:,.0f}")

    # By asset class
    by_class = calc.exposure_by_category(positions, 'asset_class')
    print(f"\nExposure by Asset Class:")
    print(by_class)

    # Concentration
    concentration = calc.exposure_concentration(positions)
    print(f"\nConcentration Metrics:")
    print(concentration)
