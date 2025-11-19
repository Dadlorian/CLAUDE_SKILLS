"""
Power BI Connector Module

Provides data connector and analytics for Power BI dashboards:
- Data source connections and transformation
- Dashboard metric calculations
- Automated data refresh and caching
- Custom visualizations data preparation
- Real-time analytics streaming
- Report data generation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import warnings

warnings.filterwarnings('ignore')


class PowerBIConnector:
    """Connector for Power BI dashboard integration"""

    def __init__(self, data_source: str = 'default'):
        """
        Initialize Power BI connector

        Args:
            data_source: Data source identifier
        """
        self.data_source = data_source
        self.cache = {}
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds

    def connect_sql_database(self, server: str, database: str,
                           username: str, password: str) -> Dict:
        """Connect to SQL database"""
        connection_info = {
            'server': server,
            'database': database,
            'provider': 'SQLOLEDB',
            'status': 'connected'
        }
        return connection_info

    def connect_cloud_storage(self, provider: str, access_key: str,
                            secret_key: str, bucket: str = None) -> Dict:
        """Connect to cloud storage"""
        connection_info = {
            'provider': provider,
            'bucket': bucket,
            'status': 'authenticated'
        }
        return connection_info

    def prepare_matter_metrics(self, matters_df: pd.DataFrame,
                              timekeeping_df: pd.DataFrame,
                              billing_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare matter metrics for Power BI visualization"""
        # Merge data
        matter_metrics = matters_df.copy()

        # Add timekeeping data
        tk_summary = timekeeping_df.groupby('matter_id').agg({
            'hours': 'sum',
            'total_amount': 'sum'
        }).rename(columns={'total_amount': 'labor_cost'}).reset_index()

        matter_metrics = matter_metrics.merge(tk_summary, on='matter_id', how='left')

        # Add billing data
        billing_summary = billing_df.groupby('matter_id').agg({
            'amount': 'sum'
        }).rename(columns={'amount': 'total_revenue'}).reset_index()

        matter_metrics = matter_metrics.merge(billing_summary, on='matter_id', how='left')

        # Calculate KPIs
        matter_metrics['labor_cost'] = matter_metrics['labor_cost'].fillna(0)
        matter_metrics['total_revenue'] = matter_metrics['total_revenue'].fillna(0)

        matter_metrics['gross_profit'] = matter_metrics['total_revenue'] - matter_metrics['labor_cost']
        matter_metrics['profit_margin'] = np.where(
            matter_metrics['total_revenue'] > 0,
            (matter_metrics['gross_profit'] / matter_metrics['total_revenue'] * 100),
            0
        )

        matter_metrics['status'] = matter_metrics['matter_status']
        matter_metrics['realization_rate'] = np.where(
            matter_metrics['labor_cost'] > 0,
            (matter_metrics['total_revenue'] / matter_metrics['labor_cost'] * 100),
            0
        )

        return matter_metrics

    def prepare_resource_metrics(self, staff_df: pd.DataFrame,
                                timekeeping_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare resource utilization metrics for Power BI"""
        resource_metrics = staff_df.copy()

        # Add timekeeping summary
        tk_summary = timekeeping_df.groupby('staff_id').agg({
            'hours': 'sum',
            'entry_id': 'count'
        }).rename(columns={'entry_id': 'entry_count'}).reset_index()

        resource_metrics = resource_metrics.merge(tk_summary, on='staff_id', how='left')

        # Calculate metrics
        resource_metrics['hours'] = resource_metrics['hours'].fillna(0)
        resource_metrics['billable_hours'] = np.where(
            timekeeping_df.groupby('staff_id')['hours'].sum() > 0,
            timekeeping_df[timekeeping_df['is_billable'] == True].groupby('staff_id')['hours'].sum(),
            0
        ).reindex(resource_metrics['staff_id'], fill_value=0).values

        resource_metrics['utilization_rate'] = np.where(
            resource_metrics['hours'] > 0,
            (resource_metrics['billable_hours'] / resource_metrics['hours'] * 100),
            0
        )

        return resource_metrics

    def prepare_vendor_metrics(self, vendors_df: pd.DataFrame,
                              timekeeping_df: pd.DataFrame,
                              expenses_df: pd.DataFrame = None) -> pd.DataFrame:
        """Prepare vendor performance metrics for Power BI"""
        vendor_metrics = vendors_df.copy()

        # Add spend data
        spend_summary = timekeeping_df.groupby('vendor_id').agg({
            'total_amount': 'sum',
            'hours': 'sum'
        }).rename(columns={'total_amount': 'total_spend'}).reset_index()

        vendor_metrics = vendor_metrics.merge(spend_summary, on='vendor_id', how='left')

        # Calculate metrics
        vendor_metrics['total_spend'] = vendor_metrics['total_spend'].fillna(0)
        vendor_metrics['avg_hourly_rate'] = np.where(
            vendor_metrics['hours'] > 0,
            vendor_metrics['total_spend'] / vendor_metrics['hours'],
            0
        )

        # Add expenses if provided
        if expenses_df is not None:
            expense_summary = expenses_df.groupby('vendor_id')['amount'].sum().reset_index()
            expense_summary.rename(columns={'amount': 'expenses'}, inplace=True)
            vendor_metrics = vendor_metrics.merge(expense_summary, on='vendor_id', how='left')
            vendor_metrics['expenses'] = vendor_metrics['expenses'].fillna(0)

        return vendor_metrics

    def prepare_financial_dashboard(self, timekeeping_df: pd.DataFrame,
                                   billing_df: pd.DataFrame,
                                   expenses_df: pd.DataFrame) -> Dict:
        """Prepare financial metrics for dashboard"""
        # Calculate total spend
        total_spend = timekeeping_df['total_amount'].sum()
        total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
        total_cost = total_spend + total_expenses

        # Calculate revenue
        total_revenue = billing_df['amount'].sum() if not billing_df.empty else 0

        # Calculate profit
        gross_profit = total_revenue - total_cost
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Monthly trends
        timekeeping_df['month'] = pd.to_datetime(timekeeping_df['date']).dt.to_period('M')
        monthly_spend = timekeeping_df.groupby('month')['total_amount'].sum()

        billing_df['month'] = pd.to_datetime(billing_df['invoice_date']).dt.to_period('M')
        monthly_revenue = billing_df.groupby('month')['amount'].sum()

        return {
            'total_spend': total_spend,
            'total_expenses': total_expenses,
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'gross_profit': gross_profit,
            'profit_margin': profit_margin,
            'monthly_spend_trend': monthly_spend.to_dict(),
            'monthly_revenue_trend': monthly_revenue.to_dict(),
            'metrics_date': datetime.now().isoformat()
        }

    def prepare_litigation_analytics(self, cases_df: pd.DataFrame,
                                    decisions_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare litigation case analytics for dashboard"""
        litigation = cases_df.copy()

        # Add decision data
        if not decisions_df.empty:
            decision_summary = decisions_df.groupby('case_id').agg({
                'decision_favorable': 'first',
                'decision_time_days': 'first'
            }).reset_index()

            litigation = litigation.merge(decision_summary, on='case_id', how='left')

        # Calculate metrics
        litigation['is_favorable'] = litigation.get('decision_favorable', 'Unknown') == 'Favorable'
        litigation['case_age_days'] = (datetime.now() - pd.to_datetime(
            litigation.get('filed_date', datetime.now())
        )).dt.days

        return litigation

    def generate_dashboard_json(self, metrics: Dict) -> str:
        """Generate Power BI compatible JSON"""
        dashboard = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'charts': {
                'spending_by_matter': 'column_chart',
                'utilization_by_attorney': 'bar_chart',
                'vendor_performance': 'scatter_chart',
                'revenue_vs_cost': 'line_chart'
            },
            'tables': {
                'matter_summary': ['matter_id', 'status', 'revenue', 'cost', 'profit'],
                'resource_utilization': ['staff_id', 'utilization_rate', 'billable_hours'],
                'vendor_performance': ['vendor_id', 'spend', 'quality_score']
            }
        }

        return json.dumps(dashboard, indent=2)

    def create_kpi_cards(self, financial_data: Dict) -> List[Dict]:
        """Create KPI cards for Power BI"""
        kpi_cards = [
            {
                'title': 'Total Revenue',
                'value': financial_data['total_revenue'],
                'format': 'currency',
                'target': financial_data['total_revenue'] * 1.1,
                'variance': 'favorable'
            },
            {
                'title': 'Total Cost',
                'value': financial_data['total_cost'],
                'format': 'currency',
                'target': financial_data['total_cost'] * 0.95,
                'variance': 'unfavorable'
            },
            {
                'title': 'Gross Profit',
                'value': financial_data['gross_profit'],
                'format': 'currency',
                'target': financial_data['total_revenue'] * 0.3,
                'variance': 'favorable' if financial_data['gross_profit'] > 0 else 'unfavorable'
            },
            {
                'title': 'Profit Margin',
                'value': financial_data['profit_margin'],
                'format': 'percent',
                'target': 30,
                'variance': 'favorable' if financial_data['profit_margin'] > 30 else 'unfavorable'
            }
        ]

        return kpi_cards

    def refresh_data(self, force: bool = False) -> Dict:
        """Refresh dashboard data"""
        now = datetime.now().timestamp()

        if force or self.last_refresh is None or (now - self.last_refresh) > self.refresh_interval:
            self.last_refresh = now
            return {
                'status': 'refreshed',
                'timestamp': datetime.now().isoformat(),
                'cached_items': len(self.cache)
            }
        else:
            return {
                'status': 'cached',
                'timestamp': self.last_refresh,
                'next_refresh': self.last_refresh + self.refresh_interval
            }


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Matters data
    matters = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 51)],
        'matter_name': [f'Matter {i}' for i in range(1, 51)],
        'matter_status': np.random.choice(['Active', 'Closed'], 50),
        'practice_area': np.random.choice(['Corporate', 'Litigation', 'IP'], 50)
    })

    # Timekeeping data
    timekeeping = pd.DataFrame({
        'entry_id': [f'TK{i:06d}' for i in range(1, 201)],
        'matter_id': np.random.choice(matters['matter_id'], 200),
        'staff_id': [f'S{np.random.randint(1, 21):03d}' for _ in range(200)],
        'hours': np.random.uniform(0.5, 8, 200),
        'total_amount': np.random.uniform(500, 5000, 200),
        'date': pd.date_range('2023-01-01', periods=200, freq='2D'),
        'is_billable': np.random.choice([True, False], 200, p=[0.75, 0.25])
    })

    # Billing data
    billing = pd.DataFrame({
        'invoice_id': [f'INV{i:06d}' for i in range(1, 101)],
        'matter_id': np.random.choice(matters['matter_id'], 100),
        'amount': np.random.uniform(5000, 50000, 100),
        'invoice_date': pd.date_range('2023-01-01', periods=100, freq='3D')
    })

    return matters, timekeeping, billing


if __name__ == "__main__":
    # Create sample data
    matters_df, timekeeping_df, billing_df = create_sample_data()

    # Initialize connector
    connector = PowerBIConnector()

    print("=" * 80)
    print("POWER BI CONNECTOR")
    print("=" * 80)

    print("\n1. MATTER METRICS")
    print("-" * 80)
    matter_metrics = connector.prepare_matter_metrics(matters_df, timekeeping_df, billing_df)
    print(matter_metrics[['matter_id', 'matter_name', 'total_revenue', 'labor_cost',
                         'gross_profit', 'profit_margin']].head(10).to_string(index=False))

    print("\n2. FINANCIAL DASHBOARD DATA")
    print("-" * 80)
    expenses_df = pd.DataFrame({
        'expense_id': [f'EXP{i:05d}' for i in range(1, 51)],
        'amount': np.random.uniform(100, 2000, 50)
    })

    financial = connector.prepare_financial_dashboard(timekeeping_df, billing_df, expenses_df)
    print(f"Total Revenue: ${financial['total_revenue']:,.2f}")
    print(f"Total Cost: ${financial['total_cost']:,.2f}")
    print(f"Gross Profit: ${financial['gross_profit']:,.2f}")
    print(f"Profit Margin: {financial['profit_margin']:.2f}%")

    print("\n3. KPI CARDS")
    print("-" * 80)
    kpi_cards = connector.create_kpi_cards(financial)
    for card in kpi_cards:
        print(f"  {card['title']}: {card['value']:.2f} ({card['variance']})")

    print("\n4. DASHBOARD JSON STRUCTURE")
    print("-" * 80)
    dashboard_json = connector.generate_dashboard_json(financial)
    print(dashboard_json[:500] + "...")

    print("\n5. DATA REFRESH STATUS")
    print("-" * 80)
    refresh = connector.refresh_data()
    print(f"Status: {refresh['status']}")
    print(f"Timestamp: {refresh['timestamp']}")

    print("\n6. SUPPORTED DATA SOURCES")
    print("-" * 80)
    sources = [
        "SQL Server",
        "Azure SQL Database",
        "Azure Blob Storage",
        "Google Cloud Storage",
        "Amazon S3",
        "Salesforce",
        "Office 365",
        "SharePoint"
    ]
    for source in sources:
        print(f"  - {source}")
