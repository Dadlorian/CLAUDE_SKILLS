"""
Tableau Dashboard Generator Module
Creates data for interactive legal analytics dashboards
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List


class TableauDashboardGenerator:
    """Generates formatted data for Tableau dashboards."""

    def __init__(self):
        """Initialize dashboard generator."""
        self.legal_data = None
        self.dashboard_data = {}

    def generate_comprehensive_legal_data(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate comprehensive legal department data."""
        np.random.seed(42)

        firms = ['White & Case', 'Simpson Thacher', 'Skadden Arps', 'Davis Polk']
        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax']
        matter_types = ['M&A', 'Contract', 'Litigation', 'IPR', 'Employment']
        regions = ['North America', 'EMEA', 'APAC']

        data = {
            'invoice_id': [f'INV-{i:06d}' for i in range(num_records)],
            'matter_id': [f'MAT-{np.random.randint(1000, 5000)}' for _ in range(num_records)],
            'law_firm': np.random.choice(firms, num_records),
            'practice_area': np.random.choice(practice_areas, num_records),
            'matter_type': np.random.choice(matter_types, num_records),
            'region': np.random.choice(regions, num_records),
            'invoice_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(num_records)],
            'invoice_amount': np.random.uniform(5000, 100000, num_records),
            'hours_billed': np.random.uniform(10, 150, num_records),
            'matter_budget': np.random.uniform(50000, 500000, num_records),
            'client_satisfaction': np.random.randint(1, 10, num_records),
            'on_time_delivery': np.random.choice([0, 1], num_records, p=[0.15, 0.85]),
            'quality_issues': np.random.randint(0, 3, num_records),
        }

        self.legal_data = pd.DataFrame(data)
        return self.legal_data

    def create_spend_dashboard_data(self) -> Dict:
        """Create data for spend analysis dashboard."""
        dashboard = {
            'total_spend': self.legal_data['invoice_amount'].sum(),
            'total_invoices': len(self.legal_data),
            'avg_invoice': self.legal_data['invoice_amount'].mean(),
            'by_firm': {},
            'by_practice_area': {},
            'by_region': {},
            'monthly_trend': {}
        }

        # By firm
        firm_data = self.legal_data.groupby('law_firm').agg({
            'invoice_amount': 'sum',
            'invoice_id': 'count',
            'hours_billed': 'sum'
        }).to_dict('index')

        for firm, data in firm_data.items():
            dashboard['by_firm'][firm] = {
                'total_spend': data['invoice_amount'],
                'invoice_count': data['invoice_id'],
                'total_hours': data['hours_billed'],
                'blended_rate': data['invoice_amount'] / data['hours_billed']
            }

        # By practice area
        practice_data = self.legal_data.groupby('practice_area').agg({
            'invoice_amount': 'sum',
            'invoice_id': 'count',
            'hours_billed': 'sum'
        }).to_dict('index')

        for practice, data in practice_data.items():
            dashboard['by_practice_area'][practice] = {
                'total_spend': data['invoice_amount'],
                'invoice_count': data['invoice_id'],
                'total_hours': data['hours_billed']
            }

        # By region
        region_data = self.legal_data.groupby('region').agg({
            'invoice_amount': 'sum',
            'invoice_id': 'count'
        }).to_dict('index')

        for region, data in region_data.items():
            dashboard['by_region'][region] = {
                'total_spend': data['invoice_amount'],
                'invoice_count': data['invoice_id']
            }

        # Monthly trend
        self.legal_data['month'] = self.legal_data['invoice_date'].dt.to_period('M')
        monthly_data = self.legal_data.groupby('month').agg({
            'invoice_amount': ['sum', 'count', 'mean'],
            'hours_billed': 'sum'
        }).to_dict('index')

        for month, data in monthly_data.items():
            dashboard['monthly_trend'][str(month)] = {
                'total_spend': data[('invoice_amount', 'sum')],
                'invoice_count': data[('invoice_amount', 'count')],
                'avg_invoice': data[('invoice_amount', 'mean')],
                'total_hours': data[('hours_billed', 'sum')]
            }

        self.dashboard_data['spend'] = dashboard
        return dashboard

    def create_performance_dashboard_data(self) -> Dict:
        """Create data for firm performance dashboard."""
        dashboard = {
            'overall_satisfaction': self.legal_data['client_satisfaction'].mean(),
            'on_time_delivery_rate': self.legal_data['on_time_delivery'].mean() * 100,
            'avg_quality_issues': self.legal_data['quality_issues'].mean(),
            'by_firm': {},
            'by_practice_area': {},
            'satisfaction_distribution': {}
        }

        # By firm performance
        firm_perf = self.legal_data.groupby('law_firm').agg({
            'client_satisfaction': 'mean',
            'on_time_delivery': 'mean',
            'quality_issues': 'mean',
            'invoice_id': 'count'
        }).to_dict('index')

        for firm, data in firm_perf.items():
            dashboard['by_firm'][firm] = {
                'avg_satisfaction': data['client_satisfaction'],
                'on_time_pct': data['on_time_delivery'] * 100,
                'avg_quality_issues': data['quality_issues'],
                'matters': data['invoice_id']
            }

        # By practice area performance
        practice_perf = self.legal_data.groupby('practice_area').agg({
            'client_satisfaction': 'mean',
            'on_time_delivery': 'mean',
            'invoice_id': 'count'
        }).to_dict('index')

        for practice, data in practice_perf.items():
            dashboard['by_practice_area'][practice] = {
                'avg_satisfaction': data['client_satisfaction'],
                'on_time_pct': data['on_time_delivery'] * 100,
                'matters': data['invoice_id']
            }

        # Satisfaction distribution
        satisfaction_dist = self.legal_data['client_satisfaction'].value_counts().to_dict()
        dashboard['satisfaction_distribution'] = satisfaction_dist

        self.dashboard_data['performance'] = dashboard
        return dashboard

    def create_budget_dashboard_data(self) -> Dict:
        """Create data for budget variance dashboard."""
        data = self.legal_data.copy()
        data['budget_variance'] = data['invoice_amount'] / data['matter_budget']
        data['variance_pct'] = ((data['invoice_amount'] - data['matter_budget']) / data['matter_budget'] * 100)

        dashboard = {
            'total_budget': data['matter_budget'].sum(),
            'total_spend': data['invoice_amount'].sum(),
            'overall_variance_pct': ((data['invoice_amount'].sum() - data['matter_budget'].sum()) / data['matter_budget'].sum() * 100),
            'by_firm': {},
            'by_practice_area': {},
            'variance_categories': {}
        }

        # By firm budget
        firm_budget = data.groupby('law_firm').agg({
            'matter_budget': 'sum',
            'invoice_amount': 'sum',
            'invoice_id': 'count'
        })

        for firm in firm_budget.index:
            budget = firm_budget.loc[firm, 'matter_budget']
            spend = firm_budget.loc[firm, 'invoice_amount']
            dashboard['by_firm'][firm] = {
                'total_budget': budget,
                'total_spend': spend,
                'variance_pct': ((spend - budget) / budget * 100),
                'matters': int(firm_budget.loc[firm, 'invoice_id'])
            }

        # Variance categories
        under_budget = (data['variance_pct'] < -10).sum()
        on_budget = ((data['variance_pct'] >= -10) & (data['variance_pct'] <= 10)).sum()
        over_budget = (data['variance_pct'] > 10).sum()

        dashboard['variance_categories'] = {
            'under_budget': under_budget,
            'on_budget': on_budget,
            'over_budget': over_budget
        }

        self.dashboard_data['budget'] = dashboard
        return dashboard

    def export_dashboard_json(self, output_path: str = './dashboard_data.json') -> None:
        """Export all dashboard data to JSON format."""
        self.create_spend_dashboard_data()
        self.create_performance_dashboard_data()
        self.create_budget_dashboard_data()

        # Convert float32 to float for JSON serialization
        def convert_floats(obj):
            if isinstance(obj, dict):
                return {k: convert_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats(item) for item in obj]
            elif isinstance(obj, (np.floating, np.integer)):
                return float(obj)
            return obj

        data_to_export = convert_floats(self.dashboard_data)

        with open(output_path, 'w') as f:
            json.dump(data_to_export, f, indent=2, default=str)

        print(f"Dashboard data exported to {output_path}")

    def export_dashboard_csv(self, output_dir: str = './') -> None:
        """Export dashboard data to CSV format for Tableau."""
        self.legal_data.to_csv(f'{output_dir}legal_transactions.csv', index=False)

        # Create aggregated files
        firm_summary = self.legal_data.groupby('law_firm').agg({
            'invoice_amount': ['sum', 'mean', 'count'],
            'hours_billed': 'sum',
            'client_satisfaction': 'mean',
            'on_time_delivery': 'mean'
        }).round(2)

        firm_summary.to_csv(f'{output_dir}firm_summary.csv')

        print(f"Dashboard CSV data exported to {output_dir}")

    def get_kpi_summary(self) -> Dict:
        """Get key performance indicators for dashboard display."""
        kpis = {
            'total_legal_spend': self.legal_data['invoice_amount'].sum(),
            'total_matters': self.legal_data['matter_id'].nunique(),
            'average_invoice_size': self.legal_data['invoice_amount'].mean(),
            'blended_hourly_rate': self.legal_data['invoice_amount'].sum() / self.legal_data['hours_billed'].sum(),
            'client_satisfaction_score': self.legal_data['client_satisfaction'].mean(),
            'on_time_delivery_pct': self.legal_data['on_time_delivery'].mean() * 100,
            'total_outside_counsel_firms': self.legal_data['law_firm'].nunique(),
            'total_invoices': len(self.legal_data)
        }

        return kpis


# Example usage
if __name__ == "__main__":
    generator = TableauDashboardGenerator()

    print("Generating comprehensive legal data...")
    generator.generate_comprehensive_legal_data(1000)

    print("\n=== SPEND DASHBOARD DATA ===")
    spend = generator.create_spend_dashboard_data()
    print(f"Total Spend: ${spend['total_spend']:,.0f}")
    print(f"Total Invoices: {spend['total_invoices']}")

    print("\n=== PERFORMANCE DASHBOARD DATA ===")
    perf = generator.create_performance_dashboard_data()
    print(f"Avg Satisfaction: {perf['overall_satisfaction']:.2f}/10")
    print(f"On-Time Delivery: {perf['on_time_delivery_rate']:.1f}%")

    print("\n=== KPI SUMMARY ===")
    kpis = generator.get_kpi_summary()
    for key, value in kpis.items():
        if isinstance(value, float) and value > 100:
            print(f"{key}: ${value:,.0f}")
        elif isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    print("\n=== EXPORTING DATA ===")
    generator.export_dashboard_csv('./')
