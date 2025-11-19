"""
Scenario Generator

Generate stress scenarios for testing and analysis.
"""

import numpy as np
import pandas as pd


class ScenarioGenerator:
    """Generate stress scenarios."""

    # Predefined scenario templates
    SCENARIOS = {
        'Recession': {
            'equity_return': -0.25,
            'credit_spread': 0.02,
            'interest_rates': -0.02,
            'unemployment': 0.03,
        },
        'Credit_Crisis': {
            'equity_return': -0.40,
            'credit_spread': 0.05,
            'interest_rates': -0.03,
            'unemployment': 0.05,
        },
        'Rate_Shock': {
            'equity_return': -0.15,
            'credit_spread': 0.01,
            'interest_rates': 0.02,
            'unemployment': 0.01,
        },
    }

    @staticmethod
    def create_scenario(scenario_name, **overrides):
        """
        Create scenario with optional overrides.

        Args:
            scenario_name: Name of base scenario
            overrides: Custom values to override

        Returns:
            Scenario dictionary
        """
        scenario = ScenarioGenerator.SCENARIOS.get(scenario_name, {}).copy()
        scenario.update(overrides)
        return scenario

    @staticmethod
    def simulate_paths(n_paths, n_periods, drift=0.0001, volatility=0.015):
        """
        Simulate return paths using Geometric Brownian Motion.

        Args:
            n_paths: Number of simulation paths
            n_periods: Number of time periods
            drift: Expected drift
            volatility: Volatility

        Returns:
            Array of simulated prices (shape: n_periods x n_paths)
        """
        dt = 1.0  # Daily steps
        paths = np.zeros((n_periods, n_paths))
        paths[0, :] = 1.0  # Starting price = 1

        for t in range(1, n_periods):
            dW = np.random.normal(0, np.sqrt(dt), n_paths)
            paths[t, :] = paths[t-1, :] * np.exp(
                (drift - 0.5 * volatility ** 2) * dt + volatility * dW
            )

        return paths

    @staticmethod
    def monte_carlo_scenarios(n_scenarios, asset_volatilities):
        """
        Generate Monte Carlo scenarios for multiple assets.

        Args:
            n_scenarios: Number of scenarios to generate
            asset_volatilities: Dict of asset volatilities

        Returns:
            DataFrame with scenarios
        """
        scenarios = []

        for _ in range(n_scenarios):
            scenario = {}
            for asset, vol in asset_volatilities.items():
                # Random return from normal distribution
                return_val = np.random.normal(0, vol)
                scenario[asset] = return_val

            scenarios.append(scenario)

        return pd.DataFrame(scenarios)


# Example usage
if __name__ == "__main__":
    gen = ScenarioGenerator()

    # Create recession scenario
    recession = gen.create_scenario('Recession', unemployment=0.04)
    print("Recession Scenario:")
    print(recession)

    # Simulate price paths
    paths = gen.simulate_paths(n_paths=100, n_periods=250)
    print(f"\nSimulated Paths Shape: {paths.shape}")
    print(f"Final prices range: {paths[-1, :].min():.3f} - {paths[-1, :].max():.3f}")

    # Monte Carlo scenarios
    volatilities = {'Equities': 0.20, 'Bonds': 0.05, 'FX': 0.10}
    mc_scenarios = gen.monte_carlo_scenarios(5, volatilities)
    print(f"\nMonte Carlo Scenarios:")
    print(mc_scenarios)
