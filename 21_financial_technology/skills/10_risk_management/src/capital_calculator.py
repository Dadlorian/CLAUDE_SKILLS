"""
Regulatory Capital Calculator

Calculates Basel III capital requirements.
"""

import numpy as np
import pandas as pd


class CapitalCalculator:
    """Calculate regulatory capital requirements."""

    # Risk weights for standardized approach
    RISK_WEIGHTS = {
        'Cash': 0.00,
        'Govt_Securities': 0.20,
        'AAA_Bonds': 0.20,
        'AA_Bonds': 0.20,
        'A_Bonds': 0.50,
        'BBB_Bonds': 1.00,
        'BB_Bonds': 1.50,
        'Corporate_Loans': 1.00,
        'Mortgages_LTV_80': 0.35,
        'Mortgages_LTV_90': 0.50,
        'Equities': 1.00,
    }

    @staticmethod
    def calculate_rwa(assets_df):
        """
        Calculate Risk-Weighted Assets.

        Args:
            assets_df: DataFrame with columns: asset_class, amount

        Returns:
            Total RWA
        """
        total_rwa = 0

        for _, row in assets_df.iterrows():
            asset_class = row['asset_class']
            amount = row['amount']

            risk_weight = CapitalCalculator.RISK_WEIGHTS.get(asset_class, 1.00)
            rwa = amount * risk_weight
            total_rwa += rwa

        return total_rwa

    @staticmethod
    def calculate_capital_ratios(tier1_capital, tier2_capital, total_capital, rwa):
        """
        Calculate Basel III capital ratios.

        Args:
            tier1_capital: Tier 1 capital
            tier2_capital: Tier 2 capital
            total_capital: Total capital (Tier 1 + Tier 2)
            rwa: Risk-weighted assets

        Returns:
            Dict of capital ratios
        """
        cet1_ratio = tier1_capital / rwa if rwa > 0 else 0
        tier1_ratio = tier1_capital / rwa if rwa > 0 else 0
        total_ratio = total_capital / rwa if rwa > 0 else 0

        return {
            'CET1_Ratio': cet1_ratio,
            'Tier1_Ratio': tier1_ratio,
            'Total_Ratio': total_ratio,
            'CET1_Pct': cet1_ratio * 100,
            'Tier1_Pct': tier1_ratio * 100,
            'Total_Pct': total_ratio * 100,
        }

    @staticmethod
    def capital_adequacy_check(ratios, requirement_buffers=None):
        """
        Check if capital ratios meet regulatory requirements.

        Args:
            ratios: Dict of capital ratios
            requirement_buffers: Dict of required ratios

        Returns:
            Dict with compliance status
        """
        if requirement_buffers is None:
            requirement_buffers = {
                'CET1': 0.045,  # 4.5% minimum
                'Tier1': 0.060,  # 6.0% minimum
                'Total': 0.080,  # 8.0% minimum
            }

        compliance = {
            'CET1_Adequate': ratios['CET1_Ratio'] >= requirement_buffers['CET1'],
            'Tier1_Adequate': ratios['Tier1_Ratio'] >= requirement_buffers['Tier1'],
            'Total_Adequate': ratios['Total_Ratio'] >= requirement_buffers['Total'],
            'Overall_Adequate': all([
                ratios['CET1_Ratio'] >= requirement_buffers['CET1'],
                ratios['Tier1_Ratio'] >= requirement_buffers['Tier1'],
                ratios['Total_Ratio'] >= requirement_buffers['Total'],
            ])
        }

        return compliance


# Example usage
if __name__ == "__main__":
    assets = pd.DataFrame({
        'asset_class': ['Cash', 'Govt_Securities', 'Corporate_Loans', 'Mortgages_LTV_80', 'Equities'],
        'amount': [100_000_000, 200_000_000, 300_000_000, 250_000_000, 100_000_000]
    })

    capital_data = {
        'Tier1': 400_000_000,
        'Tier2': 150_000_000,
    }

    # Calculate RWA
    rwa = CapitalCalculator.calculate_rwa(assets)
    print(f"Total Assets: ${assets['amount'].sum():,.0f}")
    print(f"Risk-Weighted Assets: ${rwa:,.0f}")

    # Calculate ratios
    total_capital = capital_data['Tier1'] + capital_data['Tier2']
    ratios = CapitalCalculator.calculate_capital_ratios(
        capital_data['Tier1'],
        capital_data['Tier2'],
        total_capital,
        rwa
    )

    print(f"\nCapital Ratios:")
    print(f"  CET1 Ratio: {ratios['CET1_Pct']:.2f}%")
    print(f"  Tier1 Ratio: {ratios['Tier1_Pct']:.2f}%")
    print(f"  Total Ratio: {ratios['Total_Pct']:.2f}%")

    # Check compliance
    compliance = CapitalCalculator.capital_adequacy_check(ratios)
    print(f"\nCompliance:")
    print(f"  Overall Adequate: {compliance['Overall_Adequate']}")
