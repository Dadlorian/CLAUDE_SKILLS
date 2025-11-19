"""
Risk Aggregation Framework

Aggregate risks across portfolio and calculate total risk.
"""

import pandas as pd
import numpy as np


class RiskAggregator:
    """Aggregate risks across dimensions."""

    @staticmethod
    def aggregate_var(risk_components_df):
        """
        Aggregate VaR across risks.

        Args:
            risk_components_df: DataFrame with columns:
                - component: Risk component name
                - var: VaR amount
                - correlation_matrix: Correlation with others

        Returns:
            Aggregated VaR
        """
        vars = risk_components_df['var'].values
        correlations = np.eye(len(vars))  # Simplified: no correlation

        # Aggregate VaR (simplified - assumes 0 correlation)
        aggregated_var = np.sqrt(np.sum(vars ** 2))

        return aggregated_var

    @staticmethod
    def aggregate_by_desk(risk_df, correlation_assumption='low'):
        """
        Aggregate risk by desk with correlation adjustment.

        Args:
            risk_df: DataFrame with columns: desk, var, risk_type
            correlation_assumption: 'low' (0.3), 'medium' (0.5), 'high' (0.8)

        Returns:
            Aggregated VaR by desk
        """
        correlations = {
            'low': 0.3,
            'medium': 0.5,
            'high': 0.8
        }

        corr = correlations.get(correlation_assumption, 0.3)
        aggregated = []

        for desk in risk_df['desk'].unique():
            desk_risks = risk_df[risk_df['desk'] == desk]['var'].values

            if len(desk_risks) == 1:
                var_desk = desk_risks[0]
            else:
                # Aggregate with correlation
                sum_products = 0
                for i in range(len(desk_risks)):
                    for j in range(len(desk_risks)):
                        if i == j:
                            sum_products += desk_risks[i] ** 2
                        else:
                            sum_products += desk_risks[i] * desk_risks[j] * corr

                var_desk = np.sqrt(sum_products)

            aggregated.append({'Desk': desk, 'Aggregated_VaR': var_desk})

        return pd.DataFrame(aggregated)

    @staticmethod
    def diversification_benefit(component_vars, aggregated_var):
        """
        Calculate diversification benefit.

        Args:
            component_vars: Array of component VaRs
            aggregated_var: Aggregated VaR

        Returns:
            Diversification benefit (%)
        """
        sum_components = np.sum(component_vars)
        benefit = (sum_components - aggregated_var) / sum_components
        return benefit


# Example usage
if __name__ == "__main__":
    risk_data = pd.DataFrame({
        'desk': ['Rates', 'Rates', 'Credit', 'Credit', 'Equity'],
        'risk_type': ['DV01', 'Gamma', 'Spread', 'Migration', 'Delta'],
        'var': [35_000_000, 5_000_000, 15_000_000, 8_000_000, 25_000_000]
    })

    agg = RiskAggregator()

    # Aggregate by desk
    by_desk = agg.aggregate_by_desk(risk_data, 'medium')
    print("VaR by Desk (Aggregated):")
    print(by_desk)

    # Diversification benefit
    component_vars = risk_data['var'].values
    aggregated = by_desk['Aggregated_VaR'].sum()
    benefit = agg.diversification_benefit(component_vars, aggregated)
    print(f"\nDiversification Benefit: {benefit:.2%}")
