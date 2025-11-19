"""
Legal Spend Analysis Module
Analyzes total legal department spending patterns across matters and vendors
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple


class LegalSpendAnalyzer:
    """Analyzes legal spend across matters, firms, and practice areas."""

    def __init__(self, data_source: str = None):
        """Initialize analyzer with optional data source."""
        self.data = None
        self.spend_summary = None
        self.data_source = data_source

    def load_spend_data(self, filepath: str) -> pd.DataFrame:
        """Load legal spend data from CSV or database."""
        try:
            self.data = pd.read_csv(filepath)
            self.data['invoice_date'] = pd.to_datetime(self.data['invoice_date'])
            self.data['year_month'] = self.data['invoice_date'].dt.to_period('M')
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def generate_mock_data(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate mock legal spend data for testing."""
        np.random.seed(42)

        firms = ['White & Case', 'Simpson Thacher', 'Skadden Arps', 'Davis Polk']
        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax']
        matter_types = ['M&A', 'Contract Review', 'Litigation', 'Compliance']

        data = {
            'invoice_id': [f'INV-{i:06d}' for i in range(num_records)],
            'invoice_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(num_records)],
            'law_firm': np.random.choice(firms, num_records),
            'practice_area': np.random.choice(practice_areas, num_records),
            'matter_type': np.random.choice(matter_types, num_records),
            'matter_id': [f'MAT-{np.random.randint(1000, 9999)}' for _ in range(num_records)],
            'invoice_amount': np.random.uniform(1000, 50000, num_records),
            'hours_billed': np.random.uniform(10, 200, num_records),
        }

        self.data = pd.DataFrame(data)
        self.data['hourly_rate'] = self.data['invoice_amount'] / self.data['hours_billed']
        self.data['year_month'] = self.data['invoice_date'].dt.to_period('M')

        return self.data

    def analyze_by_firm(self) -> pd.DataFrame:
        """Analyze spending by law firm."""
        firm_analysis = self.data.groupby('law_firm').agg({
            'invoice_amount': ['sum', 'mean', 'count'],
            'hours_billed': 'sum',
            'hourly_rate': 'mean'
        }).round(2)

        firm_analysis.columns = ['total_spend', 'avg_invoice', 'invoice_count',
                                 'total_hours', 'avg_hourly_rate']
        firm_analysis['total_spend_pct'] = (firm_analysis['total_spend'] /
                                           firm_analysis['total_spend'].sum() * 100).round(2)

        return firm_analysis.sort_values('total_spend', ascending=False)

    def analyze_by_practice_area(self) -> pd.DataFrame:
        """Analyze spending by practice area."""
        practice_analysis = self.data.groupby('practice_area').agg({
            'invoice_amount': ['sum', 'mean', 'count'],
            'hours_billed': 'sum'
        }).round(2)

        practice_analysis.columns = ['total_spend', 'avg_invoice', 'invoice_count', 'total_hours']
        practice_analysis['avg_hours_per_invoice'] = (practice_analysis['total_hours'] /
                                                      practice_analysis['invoice_count']).round(2)

        return practice_analysis.sort_values('total_spend', ascending=False)

    def analyze_monthly_trends(self) -> pd.DataFrame:
        """Analyze spending trends over time."""
        monthly_spend = self.data.groupby('year_month').agg({
            'invoice_amount': ['sum', 'count', 'mean'],
            'hours_billed': 'sum'
        }).round(2)

        monthly_spend.columns = ['total_spend', 'invoice_count', 'avg_invoice', 'total_hours']
        monthly_spend['avg_invoice_size'] = (monthly_spend['total_spend'] /
                                            monthly_spend['invoice_count']).round(2)

        return monthly_spend

    def identify_outliers(self, threshold_pct: float = 95) -> pd.DataFrame:
        """Identify high-value invoices (outliers)."""
        percentile = np.percentile(self.data['invoice_amount'], threshold_pct)
        outliers = self.data[self.data['invoice_amount'] >= percentile].copy()

        return outliers.sort_values('invoice_amount', ascending=False)

    def calculate_cost_per_matter(self) -> pd.DataFrame:
        """Calculate total cost per matter."""
        matter_costs = self.data.groupby('matter_id').agg({
            'invoice_amount': 'sum',
            'hours_billed': 'sum',
            'law_firm': 'nunique',
            'practice_area': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
        }).round(2)

        matter_costs.columns = ['total_cost', 'total_hours', 'firm_count', 'primary_practice_area']
        matter_costs['avg_cost_per_hour'] = (matter_costs['total_cost'] /
                                            matter_costs['total_hours']).round(2)

        return matter_costs.sort_values('total_cost', ascending=False)

    def generate_summary_report(self) -> Dict:
        """Generate comprehensive spend analysis report."""
        report = {
            'total_spend': self.data['invoice_amount'].sum(),
            'total_invoices': len(self.data),
            'avg_invoice_amount': self.data['invoice_amount'].mean(),
            'median_invoice_amount': self.data['invoice_amount'].median(),
            'total_hours_billed': self.data['hours_billed'].sum(),
            'blended_rate': self.data['invoice_amount'].sum() / self.data['hours_billed'].sum(),
            'num_firms': self.data['law_firm'].nunique(),
            'num_matters': self.data['matter_id'].nunique(),
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }

        return report

    def export_analysis(self, output_dir: str = './') -> None:
        """Export analysis results to CSV files."""
        self.analyze_by_firm().to_csv(f'{output_dir}spend_by_firm.csv')
        self.analyze_by_practice_area().to_csv(f'{output_dir}spend_by_practice_area.csv')
        self.analyze_monthly_trends().to_csv(f'{output_dir}monthly_trends.csv')
        self.calculate_cost_per_matter().to_csv(f'{output_dir}cost_per_matter.csv')
        print(f"Analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    analyzer = LegalSpendAnalyzer()

    # Generate sample data
    analyzer.generate_mock_data(1000)

    # Run analyses
    print("\n=== LEGAL SPEND ANALYSIS ===\n")
    print("Summary Report:")
    print(analyzer.generate_summary_report())

    print("\n\nSpend by Firm:")
    print(analyzer.analyze_by_firm())

    print("\n\nSpend by Practice Area:")
    print(analyzer.analyze_by_practice_area())

    print("\n\nMonthly Trends:")
    print(analyzer.analyze_monthly_trends())

    print("\n\nTop 10 Matters by Cost:")
    print(analyzer.calculate_cost_per_matter().head(10))

    print("\n\nHigh-Value Invoices (95th percentile):")
    print(analyzer.identify_outliers(95).head(10)[['invoice_id', 'law_firm', 'invoice_amount']])
