"""
Rate Analysis Module
Analyzes attorney hourly rates, billing rates, and rate benchmarks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, List


class RateAnalyzer:
    """Analyzes legal billing rates and rate structures."""

    def __init__(self):
        """Initialize rate analyzer."""
        self.invoices = None
        self.attorney_rates = None

    def generate_rate_data(self, num_invoices: int = 500) -> pd.DataFrame:
        """Generate attorney billing data."""
        np.random.seed(42)

        firms = ['White & Case', 'Simpson Thacher', 'Skadden Arps', 'Davis Polk', 'Sullivan Cromwell']
        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax']
        seniority_levels = ['Partner', 'Counsel', 'Senior Associate', 'Associate', 'Junior Associate']

        # Rate structure by seniority
        rate_map = {
            'Partner': (600, 900),
            'Counsel': (450, 650),
            'Senior Associate': (300, 450),
            'Associate': (200, 300),
            'Junior Associate': (100, 200)
        }

        data = {
            'invoice_id': [f'INV-{i:06d}' for i in range(num_invoices)],
            'law_firm': np.random.choice(firms, num_invoices),
            'practice_area': np.random.choice(practice_areas, num_invoices),
            'attorney_seniority': np.random.choice(list(rate_map.keys()), num_invoices),
            'hours_billed': np.random.uniform(5, 100, num_invoices),
            'invoice_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(num_invoices)],
        }

        df = pd.DataFrame(data)

        # Assign rates based on seniority
        df['hourly_rate'] = df['attorney_seniority'].apply(
            lambda x: np.random.uniform(rate_map[x][0], rate_map[x][1])
        )

        df['invoice_amount'] = df['hours_billed'] * df['hourly_rate']

        self.invoices = df
        return df

    def rate_by_seniority(self) -> pd.DataFrame:
        """Analyze rates by attorney seniority level."""
        analysis = self.invoices.groupby('attorney_seniority').agg({
            'hourly_rate': ['mean', 'median', 'min', 'max', 'std'],
            'hours_billed': 'mean',
            'invoice_amount': 'mean',
            'invoice_id': 'count'
        }).round(2)

        analysis.columns = ['avg_rate', 'median_rate', 'min_rate', 'max_rate', 'rate_std',
                           'avg_hours', 'avg_invoice', 'num_invoices']

        return analysis.sort_values('avg_rate', ascending=False)

    def rate_by_firm(self) -> pd.DataFrame:
        """Analyze rates by law firm."""
        analysis = self.invoices.groupby('law_firm').agg({
            'hourly_rate': ['mean', 'median', 'count'],
            'hours_billed': 'mean',
            'invoice_amount': ['sum', 'mean']
        }).round(2)

        analysis.columns = ['avg_rate', 'median_rate', 'num_rates', 'avg_hours_per_invoice',
                           'total_billed', 'avg_invoice']

        return analysis.sort_values('avg_rate', ascending=False)

    def rate_by_practice_area(self) -> pd.DataFrame:
        """Analyze rates by practice area."""
        analysis = self.invoices.groupby('practice_area').agg({
            'hourly_rate': ['mean', 'median', 'min', 'max'],
            'invoice_amount': ['sum', 'count'],
            'hours_billed': 'sum'
        }).round(2)

        analysis.columns = ['avg_rate', 'median_rate', 'min_rate', 'max_rate',
                           'total_billed', 'invoice_count', 'total_hours']

        return analysis.sort_values('avg_rate', ascending=False)

    def rate_benchmarking(self) -> pd.DataFrame:
        """Generate rate benchmarks by firm and seniority."""
        benchmark = self.invoices.groupby(['law_firm', 'attorney_seniority']).agg({
            'hourly_rate': ['mean', 'count'],
            'invoice_amount': 'mean'
        }).round(2)

        benchmark.columns = ['benchmark_rate', 'num_entries', 'avg_invoice']

        return benchmark.sort_values('benchmark_rate', ascending=False)

    def rate_trend_analysis(self) -> pd.DataFrame:
        """Analyze rate trends over time."""
        df = self.invoices.copy()
        df['month'] = df['invoice_date'].dt.to_period('M')

        trends = df.groupby('month').agg({
            'hourly_rate': 'mean',
            'invoice_amount': 'mean',
            'hours_billed': 'mean',
            'invoice_id': 'count'
        }).round(2)

        trends.columns = ['avg_rate', 'avg_invoice', 'avg_hours', 'invoice_count']

        return trends

    def rate_increase_analysis(self) -> Dict:
        """Analyze rate increases across firms and practices."""
        df = self.invoices.copy()
        df['month'] = df['invoice_date'].dt.to_period('M')

        analysis = {}

        for firm in df['law_firm'].unique():
            firm_data = df[df['law_firm'] == firm].copy()
            monthly_rates = firm_data.groupby('month')['hourly_rate'].mean()

            if len(monthly_rates) > 1:
                rate_increase = ((monthly_rates.iloc[-1] - monthly_rates.iloc[0]) / monthly_rates.iloc[0] * 100)
                analysis[firm] = {
                    'start_avg_rate': monthly_rates.iloc[0],
                    'end_avg_rate': monthly_rates.iloc[-1],
                    'increase_pct': rate_increase
                }

        return analysis

    def excessive_rate_analysis(self, threshold_percentile: float = 95) -> pd.DataFrame:
        """Identify unusually high billing rates."""
        threshold = np.percentile(self.invoices['hourly_rate'], threshold_percentile)

        excessive = self.invoices[self.invoices['hourly_rate'] >= threshold].copy()

        return excessive.sort_values('hourly_rate', ascending=False)[
            ['invoice_id', 'law_firm', 'attorney_seniority', 'hourly_rate', 'hours_billed', 'invoice_amount']
        ]

    def billing_efficiency_by_rate(self) -> pd.DataFrame:
        """Analyze hours billed across different rate tiers."""
        df = self.invoices.copy()
        df['rate_tier'] = pd.cut(df['hourly_rate'],
                                 bins=[0, 200, 400, 600, 1000],
                                 labels=['Budget', 'Standard', 'Premium', 'Elite'])

        efficiency = df.groupby('rate_tier').agg({
            'hours_billed': ['mean', 'sum', 'count'],
            'hourly_rate': 'mean',
            'invoice_amount': 'mean'
        }).round(2)

        efficiency.columns = ['avg_hours', 'total_hours', 'num_invoices', 'avg_rate', 'avg_invoice']

        return efficiency

    def export_analysis(self, output_dir: str = './') -> None:
        """Export rate analysis to files."""
        self.rate_by_seniority().to_csv(f'{output_dir}rates_by_seniority.csv')
        self.rate_by_firm().to_csv(f'{output_dir}rates_by_firm.csv')
        self.rate_by_practice_area().to_csv(f'{output_dir}rates_by_practice.csv')
        self.rate_benchmarking().to_csv(f'{output_dir}rate_benchmarks.csv')
        self.excessive_rate_analysis().to_csv(f'{output_dir}excessive_rates.csv')

        print(f"Rate analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    analyzer = RateAnalyzer()

    print("Generating rate data...")
    analyzer.generate_rate_data(500)

    print("\n=== RATES BY SENIORITY ===")
    print(analyzer.rate_by_seniority())

    print("\n=== RATES BY FIRM ===")
    print(analyzer.rate_by_firm())

    print("\n=== RATES BY PRACTICE AREA ===")
    print(analyzer.rate_by_practice_area())

    print("\n=== RATE BENCHMARKS (Top 10) ===")
    print(analyzer.rate_benchmarking().head(10))

    print("\n=== RATE INCREASE ANALYSIS ===")
    increases = analyzer.rate_increase_analysis()
    for firm, data in increases.items():
        print(f"{firm}: {data['increase_pct']:.2f}% increase")

    print("\n=== BILLING EFFICIENCY BY RATE TIER ===")
    print(analyzer.billing_efficiency_by_rate())
