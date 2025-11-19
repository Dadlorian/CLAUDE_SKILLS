"""Monte Carlo Simulator - Projects portfolio outcomes"""
import numpy as np
from typing import Dict


class MonteCarloSimulator:
    """Runs Monte Carlo simulations for outcome projection"""

    def __init__(self, initial_value: float, annual_return: float,
                 volatility: float, n_simulations: int = 10000):
        self.initial = initial_value
        self.return_rate = annual_return
        self.volatility = volatility
        self.n_simulations = n_simulations
        self.simulations = []

    def run_simulation(self, years: int) -> Dict:
        """Run Monte Carlo simulations"""
        np.random.seed(42)
        simulations = []
        final_values = []

        for _ in range(self.n_simulations):
            value = self.initial
            path = [value]

            for year in range(years):
                # Random annual return
                annual_return = np.random.normal(self.return_rate, self.volatility)
                value *= (1 + annual_return)
                path.append(value)

            simulations.append(path)
            final_values.append(value)

        self.simulations = simulations
        final_values = np.array(final_values)

        return {
            'median': np.median(final_values),
            'mean': np.mean(final_values),
            'percentile_10': np.percentile(final_values, 10),
            'percentile_90': np.percentile(final_values, 90),
            'min': np.min(final_values),
            'max': np.max(final_values),
            'std_dev': np.std(final_values)
        }

    def probability_of_success(self, target_value: float) -> float:
        """Calculate probability of achieving target"""
        if not self.simulations:
            return 0

        final_values = [sim[-1] for sim in self.simulations]
        success_count = sum(1 for v in final_values if v >= target_value)
        return success_count / len(final_values)
