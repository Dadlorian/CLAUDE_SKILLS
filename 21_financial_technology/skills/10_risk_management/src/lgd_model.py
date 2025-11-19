"""
Loss Given Default (LGD) Model

Calculates expected loss given default based on collateral and seniority.
"""

import numpy as np
import pandas as pd


class LGDModel:
    """Calculate Loss Given Default."""

    # Default recovery rates by collateral type
    RECOVERY_RATES = {
        'Mortgages': 0.85,
        'Auto_Loans': 0.75,
        'Equipment': 0.70,
        'Unsecured': 0.30,
        'Subordinated': 0.20,
    }

    @staticmethod
    def calculate_lgd(collateral_value, loan_amount, collateral_type='Unsecured'):
        """
        Calculate LGD for a loan.

        Args:
            collateral_value: Market value of collateral
            loan_amount: Amount of loan/exposure
            collateral_type: Type of collateral

        Returns:
            LGD (0-1)
        """
        recovery_rate = LGDModel.RECOVERY_RATES.get(collateral_type, 0.30)
        recovery_amount = min(collateral_value * recovery_rate, loan_amount)
        lgd = max(1 - (recovery_amount / loan_amount), 0)
        return lgd

    @staticmethod
    def ltv_adjusted_lgd(ltv_ratio, collateral_type='Mortgages'):
        """
        Calculate LGD based on Loan-to-Value ratio.

        Args:
            ltv_ratio: Loan amount / Collateral value
            collateral_type: Type of collateral

        Returns:
            LGD (0-1)
        """
        # LGD increases with LTV
        base_lgd = {
            'Mortgages': 0.05,
            'Auto_Loans': 0.10,
            'Commercial_RE': 0.15,
        }.get(collateral_type, 0.20)

        # Add LTV component (each 10% LTV above 50% adds 5% LGD)
        if ltv_ratio > 0.50:
            lgd = base_lgd + (ltv_ratio - 0.50) * 0.50
        else:
            lgd = base_lgd

        return min(lgd, 1.0)  # Cap at 100%

    @staticmethod
    def downturn_lgd(base_lgd, collateral_decline=0.30):
        """
        Calculate downturned LGD for stress testing.

        Args:
            base_lgd: Base case LGD
            collateral_decline: Expected collateral value decline in stress

        Returns:
            Stressed LGD
        """
        # Downturn LGD increases as collateral becomes less valuable
        downturn = base_lgd + (1 - base_lgd) * collateral_decline * 0.5
        return min(downturn, 1.0)

    @staticmethod
    def lgd_by_seniority(base_lgd, seniority='Senior'):
        """
        Adjust LGD by seniority in capital structure.

        Args:
            base_lgd: Base unsecured LGD
            seniority: Seniority level

        Returns:
            Adjusted LGD
        """
        seniority_adjustment = {
            'Senior': 0.7,      # Get 70% in recovery
            'Unsecured': 1.0,   # No adjustment
            'Subordinated': 1.5  # Get less (150% of unsecured loss)
        }

        adjustment = seniority_adjustment.get(seniority, 1.0)
        lgd = base_lgd * adjustment
        return min(lgd, 1.0)


# Example usage
if __name__ == "__main__":
    # Example 1: Mortgage
    collateral_value = 500_000
    loan_amount = 400_000
    lgd = LGDModel.calculate_lgd(collateral_value, loan_amount, 'Mortgages')
    print(f"Mortgage LGD: {lgd:.2%}")

    # Example 2: LTV-based
    ltv = 0.80
    lgd_ltv = LGDModel.ltv_adjusted_lgd(ltv, 'Mortgages')
    print(f"LGD at 80% LTV: {lgd_ltv:.2%}")

    # Example 3: Downturn
    downturn = LGDModel.downturn_lgd(lgd, 0.30)
    print(f"Stressed LGD (30% collateral decline): {downturn:.2%}")
