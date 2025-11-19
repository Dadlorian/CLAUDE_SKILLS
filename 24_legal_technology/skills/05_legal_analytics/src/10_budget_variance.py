"""
Budget Variance Analysis Module
Analyzes budget vs. actual spending and variance trends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class BudgetVarianceAnalyzer:
    """Analyzes legal matter budget variance and forecasting."""

    def __init__(self):
        """Initialize budget variance analyzer."""
        self.budget_data = None
        self.variance_analysis = None

    def generate_budget_data(self, num_matters: int = 300) -> pd.DataFrame:
        """Generate legal matter budget and actual spend data."""
        np.random.seed(42)

        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax']
        matter_types = ['M&A', 'Contract', 'Litigation', 'IPR', 'Employment']
        statuses = ['Closed', 'Active', 'On Hold']

        data = {
            'matter_id': [f'MAT-{i:05d}' for i in range(num_matters)],
            'practice_area': np.random.choice(practice_areas, num_matters),
            'matter_type': np.random.choice(matter_types, num_matters),
            'status': np.random.choice(statuses, num_matters),
            'original_budget': np.random.uniform(50000, 500000, num_matters),
            'revised_budget': None,
            'actual_spend': None,
            'estimated_completion': None,
            'start_date': [datetime.now() - timedelta(days=np.random.randint(30, 730)) for _ in range(num_matters)],
            'completion_date': None,
            'attorney_count': np.random.randint(1, 10, num_matters),
            'complexity_level': np.random.choice(['Low', 'Medium', 'High', 'Very High'], num_matters),
            'contingency_reserve': None,
        }

        df = pd.DataFrame(data)

        # Set revised budgets (some matters get revised)
        df['revised_budget'] = df['original_budget'].copy()
        revised_mask = np.random.random(num_matters) > 0.7
        df.loc[revised_mask, 'revised_budget'] = df.loc[revised_mask, 'original_budget'] * np.random.uniform(0.8, 1.5, revised_mask.sum())

        # Calculate actual spend with variance
        df['actual_spend'] = df['revised_budget'].copy()
        variance_pcts = np.random.normal(0, 0.2, num_matters)  # Normal distribution around budget
        df['actual_spend'] = df['revised_budget'] * (1 + variance_pcts)
        df['actual_spend'] = df['actual_spend'].clip(lower=10000)

        # Set contingency reserve (typically 10-20% of budget)
        df['contingency_reserve'] = df['revised_budget'] * np.random.uniform(0.1, 0.2, num_matters)

        # Set completion dates for closed matters
        closed_mask = df['status'] == 'Closed'
        df.loc[closed_mask, 'completion_date'] = df.loc[closed_mask, 'start_date'] + pd.to_timedelta(
            np.random.randint(30, 730), unit='D'
        )

        # Set estimated completion for active matters
        active_mask = df['status'] == 'Active'
        df.loc[active_mask, 'estimated_completion'] = datetime.now() + pd.to_timedelta(
            np.random.randint(30, 365), unit='D'
        )

        self.budget_data = df
        return df

    def calculate_variance(self) -> pd.DataFrame:
        """Calculate budget variance metrics."""
        df = self.budget_data.copy()

        # Variance calculations
        df['absolute_variance'] = df['actual_spend'] - df['revised_budget']
        df['variance_pct'] = (df['absolute_variance'] / df['revised_budget'] * 100)
        df['budget_remaining'] = df['revised_budget'] - df['actual_spend']
        df['contingency_used'] = df['actual_spend'] - df['revised_budget'] + df['contingency_reserve']

        # Variance status
        df['variance_status'] = df['variance_pct'].apply(lambda x:
            'Over Budget (>10%)' if x > 10
            else 'Over Budget (0-10%)' if x > 0
            else 'Under Budget (0-10%)' if x > -10
            else 'Under Budget (<-10%)'
        )

        self.variance_analysis = df

        return df[['matter_id', 'practice_area', 'status', 'revised_budget', 'actual_spend',
                  'absolute_variance', 'variance_pct', 'variance_status']]

    def variance_by_practice_area(self) -> pd.DataFrame:
        """Analyze variance by practice area."""
        df = self.calculate_variance()

        variance = self.budget_data.groupby('practice_area').agg({
            'revised_budget': 'sum',
            'actual_spend': 'sum',
            'matter_id': 'count'
        }).round(0)

        variance.columns = ['total_budget', 'total_spend', 'num_matters']

        variance['total_variance'] = (variance['total_spend'] - variance['total_budget']).round(0)
        variance['variance_pct'] = ((variance['total_variance'] / variance['total_budget']) * 100).round(2)
        variance['overbudget_matters'] = df[df['variance_pct'] > 0].groupby('practice_area').size()
        variance['avg_variance_pct'] = df.groupby('practice_area')['variance_pct'].mean().round(2)

        return variance.sort_values('variance_pct', ascending=False)

    def variance_by_matter_type(self) -> pd.DataFrame:
        """Analyze variance by matter type."""
        variance = self.budget_data.groupby('matter_type').agg({
            'revised_budget': ['sum', 'mean', 'count'],
            'actual_spend': ['sum', 'mean']
        }).round(0)

        variance.columns = ['total_budget', 'avg_budget', 'num_matters', 'total_spend', 'avg_spend']

        variance['total_variance'] = (variance['total_spend'] - variance['total_budget']).round(0)
        variance['variance_pct'] = ((variance['total_variance'] / variance['total_budget']) * 100).round(2)
        variance['avg_variance_per_matter'] = (variance['total_variance'] / variance['num_matters']).round(0)

        return variance.sort_values('variance_pct', ascending=False)

    def variance_by_complexity(self) -> pd.DataFrame:
        """Analyze variance by matter complexity."""
        variance = self.budget_data.groupby('complexity_level').agg({
            'revised_budget': ['sum', 'mean', 'count'],
            'actual_spend': ['sum', 'mean'],
            'attorney_count': 'mean'
        }).round(2)

        variance.columns = ['total_budget', 'avg_budget', 'num_matters', 'total_spend',
                           'avg_spend', 'avg_attorneys']

        variance['total_variance'] = (variance['total_spend'] - variance['total_budget']).round(0)
        variance['variance_pct'] = ((variance['total_variance'] / variance['total_budget']) * 100).round(2)

        return variance.sort_values('variance_pct', ascending=False)

    def overbudget_analysis(self, threshold_pct: float = 0) -> pd.DataFrame:
        """Identify overbudget matters."""
        if self.variance_analysis is None:
            self.calculate_variance()

        overbudget = self.variance_analysis[self.variance_analysis['variance_pct'] > threshold_pct].copy()

        return overbudget.sort_values('variance_pct', ascending=False)[
            ['matter_id', 'practice_area', 'revised_budget', 'actual_spend', 'absolute_variance', 'variance_pct']
        ]

    def budget_forecast(self) -> pd.DataFrame:
        """Generate budget forecast for active matters."""
        active_matters = self.budget_data[self.budget_data['status'] == 'Active'].copy()

        if len(active_matters) == 0:
            return pd.DataFrame()

        # Simple linear projection based on spent percentage and timeline
        active_matters['days_active'] = (datetime.now() - active_matters['start_date']).dt.days
        active_matters['estimated_total_days'] = (active_matters['estimated_completion'] - active_matters['start_date']).dt.days
        active_matters['progress_pct'] = (active_matters['days_active'] / active_matters['estimated_total_days'] * 100).clip(0, 100)

        # Project final spend
        active_matters['projected_spend'] = (active_matters['actual_spend'] / (active_matters['progress_pct'] / 100)).clip(lower=active_matters['actual_spend'])
        active_matters['projected_variance'] = active_matters['projected_spend'] - active_matters['revised_budget']
        active_matters['projected_variance_pct'] = (active_matters['projected_variance'] / active_matters['revised_budget'] * 100)

        return active_matters[['matter_id', 'practice_area', 'revised_budget', 'actual_spend',
                              'progress_pct', 'projected_spend', 'projected_variance', 'projected_variance_pct']].round(2)

    def contingency_analysis(self) -> pd.DataFrame:
        """Analyze contingency reserve utilization."""
        df = self.budget_data.copy()

        df['contingency_percent_used'] = ((df['actual_spend'] - (df['revised_budget'] - df['contingency_reserve'])) /
                                         df['contingency_reserve'] * 100)
        df['contingency_percent_used'] = df['contingency_percent_used'].clip(lower=0)

        analysis = df.groupby('practice_area').agg({
            'contingency_reserve': 'sum',
            'contingency_percent_used': 'mean',
            'matter_id': 'count'
        }).round(2)

        analysis.columns = ['total_contingency', 'avg_pct_used', 'num_matters']

        return analysis.sort_values('avg_pct_used', ascending=False)

    def variance_trend(self) -> pd.DataFrame:
        """Analyze variance trends over time."""
        df = self.budget_data[self.budget_data['status'] == 'Closed'].copy()

        df['completion_month'] = df['completion_date'].dt.to_period('M')

        trends = df.groupby('completion_month').agg({
            'revised_budget': 'sum',
            'actual_spend': 'sum',
            'matter_id': 'count'
        }).round(0)

        trends.columns = ['total_budget', 'total_spend', 'num_matters']
        trends['variance'] = (trends['total_spend'] - trends['total_budget']).round(0)
        trends['variance_pct'] = ((trends['variance'] / trends['total_budget']) * 100).round(2)

        return trends

    def high_risk_matters(self) -> pd.DataFrame:
        """Identify high-risk matters (high variance or near contingency limits)."""
        if self.variance_analysis is None:
            self.calculate_variance()

        # Risk criteria: >20% over budget or approaching contingency limits
        high_variance = self.variance_analysis[self.variance_analysis['variance_pct'] > 20]

        active_high_risk = self.budget_forecast()
        if len(active_high_risk) > 0:
            active_high_risk = active_high_risk[active_high_risk['projected_variance_pct'] > 15]

        return pd.concat([
            high_variance[['matter_id', 'practice_area', 'variance_pct']].rename(columns={'variance_pct': 'risk_level'}),
            active_high_risk[['matter_id', 'practice_area', 'projected_variance_pct']].rename(columns={'projected_variance_pct': 'risk_level'})
        ]).drop_duplicates('matter_id').sort_values('risk_level', ascending=False)

    def get_summary_report(self) -> Dict:
        """Generate comprehensive budget variance summary."""
        if self.variance_analysis is None:
            self.calculate_variance()

        report = {
            'total_budget': self.budget_data['revised_budget'].sum(),
            'total_actual_spend': self.budget_data['actual_spend'].sum(),
            'overall_variance': self.budget_data['actual_spend'].sum() - self.budget_data['revised_budget'].sum(),
            'overall_variance_pct': ((self.budget_data['actual_spend'].sum() - self.budget_data['revised_budget'].sum()) /
                                    self.budget_data['revised_budget'].sum() * 100),
            'num_matters': len(self.budget_data),
            'overbudget_count': (self.variance_analysis['absolute_variance'] > 0).sum(),
            'overbudget_pct': ((self.variance_analysis['absolute_variance'] > 0).sum() / len(self.variance_analysis) * 100),
            'avg_variance_pct': self.variance_analysis['variance_pct'].mean(),
            'median_variance_pct': self.variance_analysis['variance_pct'].median(),
            'max_variance_pct': self.variance_analysis['variance_pct'].max(),
            'total_contingency': self.budget_data['contingency_reserve'].sum()
        }

        return report

    def export_analysis(self, output_dir: str = './') -> None:
        """Export budget variance analysis."""
        self.variance_by_practice_area().to_csv(f'{output_dir}variance_by_practice.csv')
        self.variance_by_matter_type().to_csv(f'{output_dir}variance_by_matter_type.csv')
        self.variance_by_complexity().to_csv(f'{output_dir}variance_by_complexity.csv')
        self.overbudget_analysis().to_csv(f'{output_dir}overbudget_matters.csv')
        self.budget_forecast().to_csv(f'{output_dir}budget_forecast.csv')

        print(f"Budget variance analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    analyzer = BudgetVarianceAnalyzer()

    print("Generating budget data...")
    analyzer.generate_budget_data(300)

    print("\n=== BUDGET VARIANCE SUMMARY ===")
    summary = analyzer.get_summary_report()
    for key, value in summary.items():
        if isinstance(value, float) and abs(value) > 100:
            print(f"{key}: ${value:,.0f}")
        elif isinstance(value, float):
            print(f"{key}: {value:.2f}%")
        else:
            print(f"{key}: {value}")

    print("\n=== VARIANCE BY PRACTICE AREA ===")
    print(analyzer.variance_by_practice_area())

    print("\n=== VARIANCE BY MATTER TYPE ===")
    print(analyzer.variance_by_matter_type())

    print("\n=== VARIANCE BY COMPLEXITY LEVEL ===")
    print(analyzer.variance_by_complexity())

    print("\n=== HIGH-RISK MATTERS ===")
    high_risk = analyzer.high_risk_matters()
    print(high_risk.head(10))

    print("\n=== CONTINGENCY ANALYSIS ===")
    print(analyzer.contingency_analysis())

    print("\n=== ACTIVE MATTERS FORECAST ===")
    forecast = analyzer.budget_forecast()
    if len(forecast) > 0:
        print(forecast.head(10))
