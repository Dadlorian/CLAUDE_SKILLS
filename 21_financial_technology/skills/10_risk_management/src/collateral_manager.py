"""
Collateral Management System

Manages collateral, haircuts, and margin calculations.
"""

import pandas as pd
import numpy as np


class CollateralManager:
    """Manage collateral and margin requirements."""

    # Default haircuts by collateral type
    HAIRCUTS = {
        'Cash': 0.00,
        'Govt_Bonds': 0.05,
        'AAA_Corporate': 0.10,
        'Investment_Grade': 0.15,
        'High_Yield': 0.30,
        'Equities': 0.25,
        'Real_Estate': 0.20,
    }

    def __init__(self):
        self.collateral_positions = {}

    def add_collateral(self, collateral_id, collateral_type, market_value):
        """Add collateral position."""
        haircut = self.HAIRCUTS.get(collateral_type, 0.30)
        available_value = market_value * (1 - haircut)

        self.collateral_positions[collateral_id] = {
            'Type': collateral_type,
            'Market_Value': market_value,
            'Haircut': haircut,
            'Available_Value': available_value,
        }

    def calculate_margin_call(self, exposure, available_collateral):
        """
        Calculate margin call if any.

        Args:
            exposure: Current exposure/loan amount
            available_collateral: Available collateral value

        Returns:
            Margin call amount (positive = call due)
        """
        margin_call = max(0, exposure - available_collateral)
        return margin_call

    def stress_haircuts(self, stress_scenario='moderate'):
        """
        Apply stress haircuts to collateral.

        Args:
            stress_scenario: 'mild', 'moderate', 'severe'

        Returns:
            Updated haircuts
        """
        stress_multipliers = {
            'mild': 1.5,
            'moderate': 2.0,
            'severe': 3.0,
        }

        multiplier = stress_multipliers.get(stress_scenario, 1.0)
        stressed_haircuts = {}

        for collateral_id, data in self.collateral_positions.items():
            base_haircut = data['Haircut']
            stressed_haircut = min(base_haircut * multiplier, 1.0)
            stressed_value = data['Market_Value'] * (1 - stressed_haircut)
            stressed_haircuts[collateral_id] = stressed_value

        return stressed_haircuts


# Example usage
if __name__ == "__main__":
    manager = CollateralManager()

    # Add collateral
    manager.add_collateral('Bond_1', 'Investment_Grade', 1_000_000)
    manager.add_collateral('Real_Estate_1', 'Real_Estate', 5_000_000)
    manager.add_collateral('Equity_1', 'Equities', 500_000)

    # Calculate available collateral
    total_available = sum([v['Available_Value'] for v in manager.collateral_positions.values()])
    print(f"Total Available Collateral: ${total_available:,.0f}")

    # Margin call check
    exposure = 5_500_000
    margin_call = manager.calculate_margin_call(exposure, total_available)
    print(f"Margin Call Required: ${margin_call:,.0f}")

    # Stress scenario
    stressed = manager.stress_haircuts('moderate')
    total_stressed = sum(stressed.values())
    print(f"Stressed Available Collateral: ${total_stressed:,.0f}")
