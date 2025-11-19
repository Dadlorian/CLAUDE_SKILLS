"""
Probability of Default (PD) Model

Implements structural and empirical PD models.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


class PDModel:
    """Calculate and estimate probability of default."""

    @staticmethod
    def merton_pd(firm_value, debt_level, volatility, risk_free_rate, time_horizon=1):
        """
        Calculate PD using Merton structural model.

        Args:
            firm_value: Current firm value (assets)
            debt_level: Total debt outstanding
            volatility: Asset volatility
            risk_free_rate: Risk-free rate
            time_horizon: Time in years

        Returns:
            Probability of default (0-1)
        """
        # Distance to default
        numerator = np.log(firm_value / debt_level) + (risk_free_rate - 0.5 * volatility**2) * time_horizon
        denominator = volatility * np.sqrt(time_horizon)

        distance_to_default = numerator / denominator

        # PD = N(-DD)
        pd = norm.cdf(-distance_to_default)

        return pd

    @staticmethod
    def rating_to_pd(rating, through_the_cycle=True):
        """
        Convert credit rating to PD.

        Args:
            rating: Credit rating (AAA, AA, A, BBB, BB, B, CCC, D)
            through_the_cycle: If True, use TTC PD; else use PIT

        Returns:
            Probability of default
        """
        # Historical average PDs (through-the-cycle)
        ttc_pds = {
            'AAA': 0.0005,
            'AA': 0.0010,
            'A': 0.0030,
            'BBB': 0.0100,
            'BB': 0.0350,
            'B': 0.0900,
            'CCC': 0.2500,
            'D': 1.0000
        }

        # Point-in-time adjustment (reduce during booms, increase during recessions)
        pit_adjustment = 0.0  # 0% during neutral times, -50% in boom, +100% in recession

        pd = ttc_pds.get(rating, 0.5000)

        if not through_the_cycle:
            pd = pd * (1 + pit_adjustment)

        return pd

    @staticmethod
    def pd_from_cds(cds_spread, recovery_rate):
        """
        Estimate PD from CDS spread.

        Args:
            cds_spread: CDS spread in basis points
            recovery_rate: Expected recovery rate (0-1)

        Returns:
            Implied probability of default
        """
        # Approximate relationship: CDS ≈ PD × (1 - Recovery)
        pd = (cds_spread / 10000) / (1 - recovery_rate)
        return min(pd, 1.0)  # Cap at 100%

    @staticmethod
    def empirical_pd(historical_defaults, total_borrowers, confidence_interval=0.95):
        """
        Calculate empirical PD from historical data.

        Args:
            historical_defaults: Number of historical defaults
            total_borrowers: Total number of borrowers in sample
            confidence_interval: Confidence level for interval

        Returns:
            PD and confidence interval
        """
        pd = historical_defaults / total_borrowers

        # Binomial confidence interval (Wilson score)
        z = norm.ppf((1 + confidence_interval) / 2)
        denominator = 1 + z**2 / total_borrowers
        center = (pd + z**2 / (2 * total_borrowers)) / denominator
        margin = z * np.sqrt(pd * (1 - pd) / total_borrowers + z**2 / (4 * total_borrowers**2)) / denominator

        return {
            'pd': pd,
            'lower_bound': max(center - margin, 0),
            'upper_bound': min(center + margin, 1)
        }


# Example usage
if __name__ == "__main__":
    # Merton model
    firm_value = 500_000_000
    debt_level = 200_000_000
    volatility = 0.30
    risk_free_rate = 0.02

    pd_merton = PDModel.merton_pd(firm_value, debt_level, volatility, risk_free_rate)
    print(f"Merton PD: {pd_merton:.2%}")

    # Rating-based PD
    pd_bbb = PDModel.rating_to_pd('BBB')
    print(f"BBB Rating PD: {pd_bbb:.2%}")

    # CDS-based PD
    cds_spread = 200  # basis points
    recovery = 0.40
    pd_cds = PDModel.pd_from_cds(cds_spread, recovery)
    print(f"CDS-implied PD: {pd_cds:.2%}")

    # Empirical PD
    empirical = PDModel.empirical_pd(150, 10000)
    print(f"Empirical PD: {empirical['pd']:.2%} [CI: {empirical['lower_bound']:.2%}-{empirical['upper_bound']:.2%}]")
