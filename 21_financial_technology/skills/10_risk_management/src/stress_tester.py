"""
Stress Testing Framework

Applies stress scenarios to portfolios and calculates potential losses.
"""

import numpy as np
import pandas as pd


class StressTester:
    """Apply stress scenarios to portfolios."""

    # Pre-defined historical scenarios
    SCENARIOS = {
        '2008_Crisis': {
            'equities': -0.48,
            'ig_spreads': 0.03,
            'hy_spreads': 0.06,
            'mortgages': -0.40,
            'usd': 0.05,
        },
        '2020_COVID': {
            'equities': -0.35,
            'ig_spreads': 0.02,
            'hy_spreads': 0.05,
            'mortgages': -0.05,
            'volatility': 0.50,
        },
    }

    @staticmethod
    def apply_scenario(portfolio, scenario):
        """
        Apply stress scenario to portfolio.

        Args:
            portfolio: Dict with asset classes and amounts
            scenario: Dict with market moves for each asset class

        Returns:
            Stressed portfolio and losses
        """
        stressed_portfolio = {}
        losses = {}

        for asset_class, value in portfolio.items():
            if asset_class in scenario:
                move = scenario[asset_class]
                new_value = value * (1 + move)
                loss = new_value - value
            else:
                new_value = value
                loss = 0

            stressed_portfolio[asset_class] = new_value
            losses[asset_class] = loss

        total_loss = sum(losses.values())
        return stressed_portfolio, losses, total_loss

    @staticmethod
    def scenario_analysis(portfolio, scenarios_dict):
        """
        Run multiple scenarios.

        Args:
            portfolio: Portfolio composition
            scenarios_dict: Dict of scenarios

        Returns:
            DataFrame with results
        """
        results = []

        for scenario_name, scenario_moves in scenarios_dict.items():
            _, losses, total_loss = StressTester.apply_scenario(portfolio, scenario_moves)
            results.append({
                'Scenario': scenario_name,
                'Total_Loss': total_loss,
                'Loss_Pct': total_loss / sum(portfolio.values()),
                'Losses': losses
            })

        return pd.DataFrame(results)

    @staticmethod
    def reverse_stress_test(portfolio, max_acceptable_loss, scenarios_dict):
        """
        Find scenarios that exceed max acceptable loss.

        Args:
            portfolio: Portfolio composition
            max_acceptable_loss: Maximum acceptable loss amount
            scenarios_dict: Dict of scenarios

        Returns:
            List of unacceptable scenarios
        """
        results = StressTester.scenario_analysis(portfolio, scenarios_dict)
        unacceptable = results[results['Total_Loss'] > max_acceptable_loss]
        return unacceptable


# Example usage
if __name__ == "__main__":
    portfolio = {
        'equities': 200_000,
        'ig_bonds': 300_000,
        'hy_bonds': 150_000,
        'mortgages': 250_000,
        'cash': 100_000,
    }

    # Test 2008 scenario
    scenario_2008 = {
        'equities': -0.48,
        'ig_bonds': 0.00,  # flight to safety
        'hy_bonds': -0.25,  # from spread widening
        'mortgages': -0.40,
        'cash': 0.00,
    }

    stressed, losses, total_loss = StressTester.apply_scenario(portfolio, scenario_2008)
    print(f"2008 Crisis Impact:")
    print(f"  Total Loss: ${total_loss:,.0f}")
    print(f"  Loss %: {total_loss / sum(portfolio.values()):.2%}")

    # Test multiple scenarios
    scenarios = {
        '2008_Crisis': scenario_2008,
        'Mild_Recession': {
            'equities': -0.20,
            'ig_bonds': 0.01,
            'hy_bonds': -0.05,
            'mortgages': -0.10,
            'cash': 0.00,
        }
    }

    results = StressTester.scenario_analysis(portfolio, scenarios)
    print("\nScenario Analysis:")
    print(results[['Scenario', 'Total_Loss', 'Loss_Pct']])
