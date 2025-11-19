"""
Margin & Initial Haircut Calculator

Calculates initial margin and variation margin requirements.
"""

import pandas as pd
import numpy as np


class MarginCalculator:
    """Calculate margin requirements."""

    @staticmethod
    def initial_margin(notional_value, volatility, confidence_level=0.99):
        """
        Calculate initial margin requirement.

        Args:
            notional_value: Contract notional value
            volatility: Expected volatility
            confidence_level: Confidence level

        Returns:
            Initial margin requirement
        """
        # Higher volatility = higher margin
        # Higher confidence = higher margin
        from scipy.stats import norm

        z_score = norm.ppf(confidence_level)
        margin_ratio = z_score * volatility
        margin = notional_value * margin_ratio

        return margin

    @staticmethod
    def variation_margin(contract_value_change):
        """
        Calculate variation margin (daily P&L adjustment).

        Args:
            contract_value_change: Change in contract value

        Returns:
            Variation margin due
        """
        # Positive change: margin surplus (return to counterparty)
        # Negative change: margin call (collect from counterparty)
        return -contract_value_change

    @staticmethod
    def haircut_adjusted_value(collateral_value, haircut_pct):
        """
        Calculate haircut-adjusted collateral value.

        Args:
            collateral_value: Market value of collateral
            haircut_pct: Haircut percentage (0-100)

        Returns:
            Available collateral value
        """
        available = collateral_value * (1 - haircut_pct / 100)
        return available

    @staticmethod
    def daily_margin_settlement(daily_valuations, contract_value_changes):
        """
        Calculate daily margin settlements.

        Args:
            daily_valuations: Array of daily valuations
            contract_value_changes: Array of daily value changes

        Returns:
            DataFrame with daily margin activity
        """
        settlements = []

        for i, change in enumerate(contract_value_changes):
            var_margin = MarginCalculator.variation_margin(change)
            settlements.append({
                'Day': i + 1,
                'Contract_Value_Change': change,
                'Variation_Margin': var_margin,
            })

        return pd.DataFrame(settlements)


# Example usage
if __name__ == "__main__":
    # Initial margin for interest rate swap
    notional = 100_000_000
    volatility = 0.05  # 5% volatility
    initial_margin = MarginCalculator.initial_margin(notional, volatility)
    print(f"Initial Margin Required: ${initial_margin:,.0f}")

    # Daily margin settlement
    daily_changes = [-500_000, 1_000_000, -200_000, 300_000, -100_000]
    settlements = MarginCalculator.daily_margin_settlement(
        [notional] * 5,
        daily_changes
    )

    print("\nDaily Margin Settlements:")
    print(settlements)

    # Haircut calculation
    collateral = 1_000_000
    haircut = 10  # 10% haircut
    available = MarginCalculator.haircut_adjusted_value(collateral, haircut)
    print(f"\nCollateral: ${collateral:,.0f}")
    print(f"After {haircut}% haircut: ${available:,.0f}")
