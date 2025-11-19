"""
Exposure at Default (EAD) Calculator

Calculates exposure at default including undrawn commitments.
"""

import numpy as np
import pandas as pd


class EADCalculator:
    """Calculate Exposure at Default."""

    # Credit Conversion Factors (CCF) by product
    CCF_DEFAULTS = {
        'Term_Loan': 0.0,
        'Revolving_Credit': 0.75,
        'Credit_Card': 0.75,
        'Committed_LC': 0.75,
        'Uncomitted_LC': 0.25,
        'Derivatives': 0.50,
    }

    @staticmethod
    def calculate_ead(drawn_amount, undrawn_commitment, ccf, product_type=None):
        """
        Calculate EAD including undrawn commitments.

        Args:
            drawn_amount: Currently drawn amount
            undrawn_commitment: Available but undrawn commitment
            ccf: Credit conversion factor (0-1)
            product_type: Product type for default CCF if not provided

        Returns:
            Exposure at Default
        """
        if ccf is None and product_type:
            ccf = EADCalculator.CCF_DEFAULTS.get(product_type, 0.50)

        expected_undrawn = undrawn_commitment * ccf
        ead = drawn_amount + expected_undrawn

        return ead

    @staticmethod
    def ccf_by_utilization(utilization_rate, product_type='Revolving_Credit'):
        """
        Determine CCF based on utilization rate.

        Args:
            utilization_rate: Drawn / Total commitment (0-1)
            product_type: Type of credit product

        Returns:
            CCF (0-1)
        """
        if product_type == 'Revolving_Credit':
            if utilization_rate < 0.2:
                ccf = 0.40
            elif utilization_rate < 0.5:
                ccf = 0.65
            elif utilization_rate < 0.8:
                ccf = 0.80
            else:
                ccf = 0.90
        else:
            ccf = EADCalculator.CCF_DEFAULTS.get(product_type, 0.50)

        return ccf

    @staticmethod
    def ead_with_collateral(ead, collateral_amount, haircut=0.10):
        """
        Adjust EAD for collateral posted.

        Args:
            ead: Gross exposure at default
            collateral_amount: Amount of collateral
            haircut: Haircut on collateral value

        Returns:
            Net EAD after collateral
        """
        collateral_value = collateral_amount * (1 - haircut)
        net_ead = max(ead - collateral_value, 0)
        return net_ead

    @staticmethod
    def ead_portfolio(exposures_df):
        """
        Calculate portfolio EAD.

        Args:
            exposures_df: DataFrame with columns:
                - drawn_amount
                - undrawn_commitment
                - ccf
                - collateral_amount
                - haircut

        Returns:
            Total portfolio EAD
        """
        total_ead = 0
        for _, row in exposures_df.iterrows():
            ead = EADCalculator.calculate_ead(
                row['drawn_amount'],
                row['undrawn_commitment'],
                row.get('ccf', 0.50)
            )
            net_ead = EADCalculator.ead_with_collateral(
                ead,
                row.get('collateral_amount', 0),
                row.get('haircut', 0.10)
            )
            total_ead += net_ead

        return total_ead


# Example usage
if __name__ == "__main__":
    # Example 1: Credit card
    drawn = 5000
    undrawn = 15000
    ccf = 0.75
    ead = EADCalculator.calculate_ead(drawn, undrawn, ccf)
    print(f"Credit Card EAD: ${ead:,.0f}")

    # Example 2: Revolver with utilization
    utilization = 0.60
    ccf_util = EADCalculator.ccf_by_utilization(utilization)
    ead_util = EADCalculator.calculate_ead(drawn, undrawn, ccf_util)
    print(f"Revolver EAD (60% util): ${ead_util:,.0f}")

    # Example 3: With collateral
    collateral = 10000
    haircut = 0.10
    net_ead = EADCalculator.ead_with_collateral(ead, collateral, haircut)
    print(f"EAD after collateral: ${net_ead:,.0f}")
