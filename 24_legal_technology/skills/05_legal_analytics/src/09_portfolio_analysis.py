#!/usr/bin/env python3
"""
Portfolio Analytics Engine
Comprehensive analysis of legal matter portfolios
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics

class PortfolioAnalyzer:
    """Analyze legal matter portfolios"""

    def __init__(self, matters_data, financial_data):
        """Initialize with matter and financial data"""
        self.matters = pd.read_csv(matters_data) if isinstance(matters_data, str) else matters_data
        self.financials = pd.read_csv(financial_data) if isinstance(financial_data, str) else financial_data
        self.matters['open_date'] = pd.to_datetime(self.matters['open_date'])
        self.matters['close_date'] = pd.to_datetime(self.matters['close_date'], errors='coerce')

    def portfolio_overview(self):
        """Get overview of entire portfolio"""

        overview = {
            'total_matters': len(self.matters),
            'active_matters': len(self.matters[self.matters['status'] == 'Active']),
            'closed_matters': len(self.matters[self.matters['status'] == 'Closed']),
            'total_exposure': self.matters['claim_amount'].sum(),
            'total_revenue': self.financials['billed_amount'].sum(),
            'total_cost': self.financials['cost'].sum(),
            'avg_matter_value': self.matters['claim_amount'].mean(),
            'median_matter_value': self.matters['claim_amount'].median(),
        }

        overview['portfolio_profit'] = overview['total_revenue'] - overview['total_cost']
        overview['portfolio_margin'] = (overview['portfolio_profit'] / overview['total_revenue'] * 100) if overview['total_revenue'] > 0 else 0

        return overview

    def risk_analysis(self):
        """Analyze portfolio risk"""

        risk = pd.DataFrame({
            'risk_level': self.matters['risk_level'].unique()
        })

        risk_breakdown = []
        for level in risk['risk_level']:
            matters_in_level = self.matters[self.matters['risk_level'] == level]
            risk_breakdown.append({
                'risk_level': level,
                'count': len(matters_in_level),
                'pct_of_portfolio': len(matters_in_level) / len(self.matters) * 100,
                'total_exposure': matters_in_level['claim_amount'].sum(),
                'avg_exposure': matters_in_level['claim_amount'].mean(),
                'win_probability': matters_in_level['win_probability'].mean()
            })

        return pd.DataFrame(risk_breakdown)

    def expected_value_analysis(self):
        """Calculate expected value across portfolio"""

        self.matters['expected_value'] = self.matters['claim_amount'] * self.matters['win_probability']

        ev_summary = {
            'total_exposure': self.matters['claim_amount'].sum(),
            'expected_value': self.matters['expected_value'].sum(),
            'probability_weighted_exposure': self.matters['expected_value'].sum(),
            'expected_profit': self.matters['expected_value'].sum() - self.financials['cost'].sum(),
        }

        return ev_summary

    def concentration_analysis(self):
        """Analyze concentration of portfolio value"""

        sorted_matters = self.matters.sort_values('claim_amount', ascending=False)
        sorted_matters['cumulative_value'] = sorted_matters['claim_amount'].cumsum()
        sorted_matters['cumulative_pct'] = sorted_matters['cumulative_value'] / sorted_matters['claim_amount'].sum() * 100

        # 80/20 analysis
        top_20_pct_count = int(len(sorted_matters) * 0.20)
        top_20_matters = sorted_matters.head(top_20_pct_count)
        top_20_value_pct = (top_20_matters['claim_amount'].sum() / sorted_matters['claim_amount'].sum()) * 100

        # Top 10 matters
        top_10_matters = sorted_matters.head(10)

        concentration = {
            'top_10_matters': len(top_10_matters),
            'top_10_value': top_10_matters['claim_amount'].sum(),
            'top_10_pct_of_portfolio': (top_10_matters['claim_amount'].sum() / sorted_matters['claim_amount'].sum()) * 100,
            'concentration_ratio_80_20': top_20_value_pct,
            'gini_coefficient': self._calculate_gini(sorted_matters['claim_amount'].values),
            'herfindahl_index': self._calculate_herfindahl(sorted_matters['claim_amount'].values)
        }

        return concentration

    def _calculate_gini(self, values):
        """Calculate Gini coefficient for concentration"""
        sorted_vals = np.sort(values)
        n = len(sorted_vals)
        cumsum = np.cumsum(sorted_vals)
        return (2 * np.sum(np.arange(1, n + 1) * sorted_vals)) / (n * np.sum(sorted_vals)) - (n + 1) / n

    def _calculate_herfindahl(self, values):
        """Calculate Herfindahl-Hirschman index"""
        total = np.sum(values)
        shares = values / total
        hhi = np.sum(shares ** 2)
        return hhi * 10000

    def duration_analysis(self):
        """Analyze case durations"""

        closed = self.matters[self.matters['status'] == 'Closed'].copy()
        closed['duration_days'] = (closed['close_date'] - closed['open_date']).dt.days
        closed['duration_months'] = closed['duration_days'] / 30

        duration_stats = {
            'avg_duration_months': closed['duration_months'].mean(),
            'median_duration_months': closed['duration_months'].median(),
            'min_duration_months': closed['duration_months'].min(),
            'max_duration_months': closed['duration_months'].max(),
            'stdev_duration_months': closed['duration_months'].std()
        }

        return duration_stats

    def outcome_analysis(self):
        """Analyze case outcomes"""

        closed = self.matters[self.matters['status'] == 'Closed']

        outcomes = closed['outcome'].value_counts().to_dict()
        outcome_success_rate = len(closed[closed['outcome'] == 'Win']) / len(closed) * 100

        # By matter type
        outcome_by_type = closed.groupby('matter_type')['outcome'].value_counts().unstack(fill_value=0)

        return {
            'total_closed': len(closed),
            'outcomes': outcomes,
            'success_rate_pct': outcome_success_rate,
            'outcome_by_type': outcome_by_type
        }

    def cash_flow_forecast(self, months_ahead=12):
        """Forecast cash flow from settlement/judgment"""

        forecasts = []

        for month in range(1, months_ahead + 1):
            expected_resolutions = len(self.matters[
                (self.matters['expected_resolution_month'] <= month) &
                (self.matters['status'] == 'Active')
            ])

            expected_revenue = self.matters[
                (self.matters['expected_resolution_month'] <= month) &
                (self.matters['status'] == 'Active')
            ]['expected_value'].sum()

            forecasts.append({
                'month': month,
                'expected_resolutions': expected_resolutions,
                'expected_revenue': expected_revenue
            })

        return pd.DataFrame(forecasts)

    def generate_portfolio_report(self):
        """Generate comprehensive portfolio report"""

        overview = self.portfolio_overview()
        risk = self.risk_analysis()
        ev = self.expected_value_analysis()
        concentration = self.concentration_analysis()
        duration = self.duration_analysis()
        outcomes = self.outcome_analysis()

        report = f"""
LEGAL PORTFOLIO ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
=================
Total Active Matters: {overview['active_matters']}
Total Closed Matters: {overview['closed_matters']}
Total Portfolio Value: ${overview['total_exposure']:,.0f}
Expected Portfolio Value: ${ev['expected_value']:,.0f}

Financial Performance:
- Total Revenue: ${overview['total_revenue']:,.0f}
- Total Cost: ${overview['total_cost']:,.0f}
- Portfolio Profit: ${overview['portfolio_profit']:,.0f}
- Portfolio Margin: {overview['portfolio_margin']:.1f}%

RISK ANALYSIS
=============
{risk.to_string(index=False)}

CONCENTRATION ANALYSIS
======================
Top 10 Matters: {concentration['top_10_pct_of_portfolio']:.1f}% of portfolio value
80/20 Concentration: {concentration['concentration_ratio_80_20']:.1f}%
Gini Coefficient: {concentration['gini_coefficient']:.3f} (0=even, 1=concentrated)
Assessment: {'Highly concentrated - mitigate concentration risk' if concentration['gini_coefficient'] > 0.6 else 'Well diversified'}

CASE DURATION STATISTICS
========================
Average Duration: {duration['avg_duration_months']:.1f} months
Median Duration: {duration['median_duration_months']:.1f} months
Range: {duration['min_duration_months']:.1f} - {duration['max_duration_months']:.1f} months

OUTCOME ANALYSIS
================
Total Closed: {outcomes['total_closed']}
Success Rate: {outcomes['success_rate_pct']:.1f}%

Outcomes:
{pd.Series(outcomes['outcomes']).to_string()}

EXPECTED VALUE SUMMARY
======================
Total Exposure: ${ev['total_exposure']:,.0f}
Probability-Adjusted Value: ${ev['expected_value']:,.0f}
Expected Profit (after costs): ${ev['expected_profit']:,.0f}

CASH FLOW FORECAST (Next 6 Months)
==================================
{self.cash_flow_forecast(6).to_string(index=False)}

RECOMMENDATIONS
===============
1. Portfolio Concentration: {'Reduce concentration by settling or dismissing large matters' if concentration['gini_coefficient'] > 0.6 else 'Concentration within acceptable range'}
2. Settlement Strategy: Focus on high-value matters for risk mitigation
3. Resource Allocation: {'Accelerate trial prep for high-value matters' if outcomes['success_rate_pct'] > 70 else 'Review case strategy and resource allocation'}
4. Duration Management: Average case taking {duration['avg_duration_months']:.0f} months - implement timeline optimization
        """

        return report


if __name__ == "__main__":
    # Sample data
    import numpy as np

    matters_data = {
        'matter_id': [f'MATTER-{i:03d}' for i in range(1, 51)],
        'matter_type': np.random.choice(['Litigation', 'Transaction', 'Regulatory'], 50),
        'status': np.random.choice(['Active', 'Closed'], 50, p=[0.7, 0.3]),
        'claim_amount': np.random.uniform(100000, 10000000, 50),
        'win_probability': np.random.uniform(0.2, 0.95, 50),
        'risk_level': np.random.choice(['High', 'Medium', 'Low'], 50),
        'open_date': pd.date_range('2022-01-01', periods=50, freq='W'),
        'close_date': [pd.Timestamp('2024-01-01') if np.random.random() > 0.7 else pd.NaT for _ in range(50)],
        'outcome': [np.random.choice(['Win', 'Lose', 'Settle'], 1)[0] if np.random.random() > 0.7 else None for _ in range(50)],
        'expected_resolution_month': np.random.randint(1, 13, 50)
    }

    financials_data = {
        'matter_id': [f'MATTER-{i:03d}' for i in range(1, 51)],
        'billed_amount': np.random.uniform(50000, 500000, 50),
        'cost': np.random.uniform(30000, 400000, 50)
    }

    matters_df = pd.DataFrame(matters_data)
    financials_df = pd.DataFrame(financials_data)

    analyzer = PortfolioAnalyzer(matters_df, financials_df)
    print(analyzer.generate_portfolio_report())
