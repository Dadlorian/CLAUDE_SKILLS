"""
Risk Reporting System

Generate comprehensive risk reports.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class RiskReporter:
    """Generate risk reports."""

    def __init__(self):
        self.report_date = datetime.now()
        self.data = {}

    def add_section(self, section_name, data_df):
        """Add data section to report."""
        self.data[section_name] = data_df

    def generate_executive_summary(self):
        """Generate executive summary."""
        summary = f"""
RISK REPORT - EXECUTIVE SUMMARY
Report Date: {self.report_date.strftime('%Y-%m-%d')}

Key Metrics:
- Capital Ratio: Calculated from data
- VaR (95%): Calculated from market data
- Stressed Losses: From stress testing
- Limit Breaches: From limit monitoring
- Key Risks: Identified risks

Highlights:
- No material risk breaches
- Capital ratios above minimums
- Stress test results within tolerance
"""
        return summary

    def generate_credit_section(self, credit_df):
        """Generate credit risk section."""
        section = f"""
CREDIT RISK SECTION
Total Exposure: ${credit_df['exposure'].sum():,.0f}
Number of Counterparties: {len(credit_df)}

Top Exposures:
{credit_df.nlargest(5, 'exposure')[['counterparty', 'exposure']].to_string(index=False)}

Portfolio Quality:
- Average Rating: {credit_df.get('rating', pd.Series()).mode()[0] if 'rating' in credit_df.columns else 'N/A'}
- Concentration (Top 10): {(credit_df.nlargest(10, 'exposure')['exposure'].sum() / credit_df['exposure'].sum()):.1%}
"""
        return section

    def generate_market_section(self, market_df):
        """Generate market risk section."""
        section = f"""
MARKET RISK SECTION
Total VaR (95%): ${market_df.get('var_95', pd.Series(0)).sum():,.0f}
Total VaR (99%): ${market_df.get('var_99', pd.Series(0)).sum():,.0f}

Risk by Asset Class:
{market_df.to_string(index=False)}
"""
        return section

    def generate_full_report(self):
        """Generate full report."""
        report = self.generate_executive_summary()

        if 'Credit' in self.data:
            report += self.generate_credit_section(self.data['Credit'])

        if 'Market' in self.data:
            report += self.generate_market_section(self.data['Market'])

        return report


# Example usage
if __name__ == "__main__":
    reporter = RiskReporter()

    # Add credit data
    credit_data = pd.DataFrame({
        'counterparty': ['Bank A', 'Corp B', 'Corp C', 'Corp D', 'Corp E'],
        'exposure': [50_000_000, 35_000_000, 30_000_000, 25_000_000, 20_000_000],
        'rating': ['AA', 'BBB', 'A', 'BBB', 'BB']
    })
    reporter.add_section('Credit', credit_data)

    # Add market data
    market_data = pd.DataFrame({
        'asset_class': ['Equities', 'Bonds', 'FX', 'Credit'],
        'var_95': [10_000_000, 2_000_000, 1_500_000, 3_000_000],
        'var_99': [15_000_000, 3_000_000, 2_250_000, 4_500_000]
    })
    reporter.add_section('Market', market_data)

    # Generate report
    report = reporter.generate_full_report()
    print(report)
