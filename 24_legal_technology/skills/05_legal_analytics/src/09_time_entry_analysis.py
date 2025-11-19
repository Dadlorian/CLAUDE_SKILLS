"""
Time Entry Analysis Module
Analyzes attorney time entries and utilization metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class TimeEntryAnalyzer:
    """Analyzes attorney time entries and utilization."""

    def __init__(self):
        """Initialize time entry analyzer."""
        self.time_entries = None
        self.utilization_metrics = None

    def generate_time_entry_data(self, num_entries: int = 2000) -> pd.DataFrame:
        """Generate attorney time entry data."""
        np.random.seed(42)

        attorneys = [f'Attorney_{i}' for i in range(1, 51)]
        firms = ['White & Case', 'Simpson Thacher', 'Skadden Arps', 'Davis Polk']
        seniorities = ['Partner', 'Counsel', 'Senior Associate', 'Associate', 'Junior Associate']
        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax']
        matter_types = ['M&A', 'Contract', 'Litigation', 'IPR', 'Compliance']

        data = {
            'entry_id': [f'TIME-{i:06d}' for i in range(num_entries)],
            'attorney_id': np.random.choice(attorneys, num_entries),
            'law_firm': np.random.choice(firms, num_entries),
            'seniority_level': np.random.choice(seniorities, num_entries),
            'practice_area': np.random.choice(practice_areas, num_entries),
            'matter_id': [f'MAT-{np.random.randint(1000, 5000)}' for _ in range(num_entries)],
            'matter_type': np.random.choice(matter_types, num_entries),
            'hours_worked': np.random.uniform(0.5, 8, num_entries),
            'hours_billable': None,
            'entry_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(num_entries)],
            'task_description': np.random.choice(['Research', 'Writing', 'Drafting', 'Review', 'Client Call', 'Court Work'], num_entries),
            'billability_flag': np.random.choice([0, 1], num_entries, p=[0.15, 0.85]),
        }

        df = pd.DataFrame(data)

        # Calculate billable hours
        seniority_rates = {
            'Partner': (600, 900),
            'Counsel': (450, 650),
            'Senior Associate': (300, 450),
            'Associate': (200, 300),
            'Junior Associate': (100, 200)
        }

        df['hourly_rate'] = df['seniority_level'].apply(
            lambda x: np.random.uniform(seniority_rates[x][0], seniority_rates[x][1])
        )

        df['hours_billable'] = df['hours_worked'] * df['billability_flag']
        df['amount_billed'] = df['hours_billable'] * df['hourly_rate']

        self.time_entries = df
        return df

    def utilization_by_attorney(self) -> pd.DataFrame:
        """Analyze utilization metrics by attorney."""
        utilization = self.time_entries.groupby(['attorney_id', 'seniority_level', 'law_firm']).agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'amount_billed': 'sum',
            'entry_id': 'count',
            'matter_id': 'nunique',
            'hourly_rate': 'mean'
        }).round(2)

        utilization.columns = ['total_hours', 'billable_hours', 'total_billed', 'num_entries',
                              'num_matters', 'avg_hourly_rate']

        # Calculate utilization percentage
        utilization['utilization_pct'] = (utilization['billable_hours'] / utilization['total_hours'] * 100).round(2)
        utilization['hours_per_entry'] = (utilization['total_hours'] / utilization['num_entries']).round(2)
        utilization['revenue_per_hour'] = (utilization['total_billed'] / utilization['total_hours']).round(2)

        return utilization.sort_values('billable_hours', ascending=False)

    def utilization_by_seniority(self) -> pd.DataFrame:
        """Analyze utilization by attorney seniority level."""
        utilization = self.time_entries.groupby('seniority_level').agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'billability_flag': 'mean',
            'amount_billed': 'sum',
            'entry_id': 'count',
            'attorney_id': 'nunique',
            'hourly_rate': 'mean'
        }).round(2)

        utilization.columns = ['total_hours', 'billable_hours', 'billability_rate', 'total_revenue',
                              'num_entries', 'num_attorneys', 'avg_hourly_rate']

        utilization['utilization_pct'] = (utilization['billability_rate'] * 100).round(2)
        utilization['revenue_per_hour'] = (utilization['total_revenue'] / utilization['total_hours']).round(2)
        utilization['avg_hours_per_entry'] = (utilization['total_hours'] / utilization['num_entries']).round(2)

        return utilization

    def utilization_by_practice_area(self) -> pd.DataFrame:
        """Analyze utilization by practice area."""
        utilization = self.time_entries.groupby('practice_area').agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'amount_billed': 'sum',
            'entry_id': 'count',
            'attorney_id': 'nunique',
            'hourly_rate': 'mean'
        }).round(2)

        utilization.columns = ['total_hours', 'billable_hours', 'total_revenue', 'num_entries',
                              'num_attorneys', 'avg_hourly_rate']

        utilization['utilization_pct'] = (utilization['billable_hours'] / utilization['total_hours'] * 100).round(2)
        utilization['revenue_per_hour'] = (utilization['total_revenue'] / utilization['total_hours']).round(2)

        return utilization.sort_values('total_revenue', ascending=False)

    def monthly_utilization_trend(self) -> pd.DataFrame:
        """Analyze utilization trends over time."""
        df = self.time_entries.copy()
        df['month'] = df['entry_date'].dt.to_period('M')

        trends = df.groupby('month').agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'amount_billed': 'sum',
            'entry_id': 'count',
            'attorney_id': 'nunique'
        }).round(2)

        trends.columns = ['total_hours', 'billable_hours', 'revenue', 'num_entries', 'num_attorneys']
        trends['utilization_pct'] = (trends['billable_hours'] / trends['total_hours'] * 100).round(2)
        trends['avg_hours_per_attorney'] = (trends['total_hours'] / trends['num_attorneys']).round(2)

        return trends

    def non_billable_analysis(self) -> pd.DataFrame:
        """Analyze non-billable time allocation."""
        non_billable = self.time_entries[self.time_entries['billability_flag'] == 0].copy()

        analysis = non_billable.groupby(['seniority_level', 'task_description']).agg({
            'hours_worked': 'sum',
            'entry_id': 'count',
            'attorney_id': 'nunique'
        }).round(2)

        analysis.columns = ['total_hours', 'num_entries', 'num_attorneys']

        return analysis.sort_values('total_hours', ascending=False)

    def firm_utilization_comparison(self) -> pd.DataFrame:
        """Compare utilization across firms."""
        comparison = self.time_entries.groupby('law_firm').agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'amount_billed': 'sum',
            'entry_id': 'count',
            'attorney_id': 'nunique',
            'hourly_rate': 'mean'
        }).round(2)

        comparison.columns = ['total_hours', 'billable_hours', 'total_revenue', 'num_entries',
                             'num_attorneys', 'avg_hourly_rate']

        comparison['utilization_pct'] = (comparison['billable_hours'] / comparison['total_hours'] * 100).round(2)
        comparison['revenue_per_attorney'] = (comparison['total_revenue'] / comparison['num_attorneys']).round(0)
        comparison['hours_per_attorney'] = (comparison['total_hours'] / comparison['num_attorneys']).round(2)

        return comparison

    def underutilized_attorneys(self, threshold_pct: float = 60) -> pd.DataFrame:
        """Identify underutilized attorneys."""
        utilization = self.utilization_by_attorney()

        underutilized = utilization[utilization['utilization_pct'] < threshold_pct].copy()

        return underutilized.sort_values('utilization_pct')

    def matter_allocation(self) -> pd.DataFrame:
        """Analyze time allocation across matters."""
        allocation = self.time_entries.groupby(['matter_id', 'matter_type']).agg({
            'hours_worked': 'sum',
            'hours_billable': 'sum',
            'amount_billed': 'sum',
            'attorney_id': 'nunique',
            'seniority_level': 'nunique'
        }).round(2)

        allocation.columns = ['total_hours', 'billable_hours', 'total_revenue',
                             'num_attorneys', 'num_seniority_levels']

        allocation['utilization_pct'] = (allocation['billable_hours'] / allocation['total_hours'] * 100).round(2)
        allocation['avg_cost_per_hour'] = (allocation['total_revenue'] / allocation['total_hours']).round(2)

        return allocation.sort_values('total_hours', ascending=False)

    def get_utilization_summary(self) -> Dict:
        """Get overall utilization summary statistics."""
        total_hours = self.time_entries['hours_worked'].sum()
        billable_hours = self.time_entries['hours_billable'].sum()

        summary = {
            'total_hours_recorded': total_hours,
            'total_billable_hours': billable_hours,
            'overall_utilization_pct': (billable_hours / total_hours * 100) if total_hours > 0 else 0,
            'total_revenue_generated': self.time_entries['amount_billed'].sum(),
            'avg_hourly_rate': self.time_entries['hourly_rate'].mean(),
            'blended_hourly_rate': self.time_entries['amount_billed'].sum() / billable_hours if billable_hours > 0 else 0,
            'num_attorneys': self.time_entries['attorney_id'].nunique(),
            'num_matters': self.time_entries['matter_id'].nunique(),
            'num_time_entries': len(self.time_entries)
        }

        return summary

    def export_analysis(self, output_dir: str = './') -> None:
        """Export time entry analysis."""
        self.utilization_by_attorney().to_csv(f'{output_dir}attorney_utilization.csv')
        self.utilization_by_seniority().to_csv(f'{output_dir}seniority_utilization.csv')
        self.utilization_by_practice_area().to_csv(f'{output_dir}practice_area_utilization.csv')
        self.firm_utilization_comparison().to_csv(f'{output_dir}firm_comparison.csv')
        self.matter_allocation().to_csv(f'{output_dir}matter_allocation.csv')

        print(f"Time entry analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    analyzer = TimeEntryAnalyzer()

    print("Generating time entry data...")
    analyzer.generate_time_entry_data(2000)

    print("\n=== OVERALL UTILIZATION SUMMARY ===")
    summary = analyzer.get_utilization_summary()
    for key, value in summary.items():
        if isinstance(value, float) and value > 100:
            print(f"{key}: ${value:,.0f}")
        elif isinstance(value, float):
            print(f"{key}: {value:.2f}%")
        else:
            print(f"{key}: {value}")

    print("\n=== UTILIZATION BY SENIORITY ===")
    print(analyzer.utilization_by_seniority())

    print("\n=== UTILIZATION BY PRACTICE AREA ===")
    print(analyzer.utilization_by_practice_area())

    print("\n=== TOP 10 ATTORNEYS BY BILLABLE HOURS ===")
    print(analyzer.utilization_by_attorney().head(10))

    print("\n=== FIRM UTILIZATION COMPARISON ===")
    print(analyzer.firm_utilization_comparison())

    print("\n=== UNDERUTILIZED ATTORNEYS (< 60%) ===")
    print(analyzer.underutilized_attorneys(60))
