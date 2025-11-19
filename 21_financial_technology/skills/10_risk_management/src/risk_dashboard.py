"""
Risk Dashboard

Real-time risk monitoring and reporting.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class RiskDashboard:
    """Risk monitoring dashboard."""

    def __init__(self):
        self.positions = {}
        self.limits = {}
        self.var_estimates = {}

    def add_position(self, name, value, limit, risk_metric='VaR'):
        """Add position to dashboard."""
        self.positions[name] = {
            'Value': value,
            'Limit': limit,
            'Risk_Metric': risk_metric,
            'Timestamp': datetime.now()
        }

    def update_var(self, name, var_amount):
        """Update VaR estimate."""
        self.var_estimates[name] = var_amount

    def generate_report(self):
        """Generate risk dashboard report."""
        report_data = []

        for name, data in self.positions.items():
            limit = data['Limit']
            var = self.var_estimates.get(name, 0)
            utilization = (var / limit * 100) if limit > 0 else 0

            # Determine status
            if utilization <= 80:
                status = 'Green'
            elif utilization <= 100:
                status = 'Yellow'
            else:
                status = 'Red'

            report_data.append({
                'Position': name,
                'Value': data['Value'],
                'Limit': limit,
                'VaR': var,
                'Utilization_%': utilization,
                'Status': status
            })

        df = pd.DataFrame(report_data)
        return df

    def summary_statistics(self):
        """Generate summary statistics."""
        df = self.generate_report()

        summary = {
            'Total_Value': df['Value'].sum(),
            'Total_Limit': df['Limit'].sum(),
            'Total_VaR': df['VaR'].sum(),
            'Avg_Utilization': df['Utilization_%'].mean(),
            'Red_Count': (df['Status'] == 'Red').sum(),
            'Yellow_Count': (df['Status'] == 'Yellow').sum(),
        }

        return summary


# Example usage
if __name__ == "__main__":
    dashboard = RiskDashboard()

    # Add positions
    dashboard.add_position('Rates_Desk', 50_000_000, 50_000_000)
    dashboard.add_position('Credit_Desk', 40_000_000, 40_000_000)
    dashboard.add_position('Equity_Desk', 30_000_000, 30_000_000)

    # Update VaRs
    dashboard.update_var('Rates_Desk', 35_000_000)
    dashboard.update_var('Credit_Desk', 32_000_000)
    dashboard.update_var('Equity_Desk', 28_000_000)

    # Generate reports
    print("Risk Dashboard Report:")
    print(dashboard.generate_report())

    print("\nSummary Statistics:")
    summary = dashboard.summary_statistics()
    for key, value in summary.items():
        print(f"  {key}: {value}")
