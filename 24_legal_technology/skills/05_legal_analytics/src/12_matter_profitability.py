"""
Matter Profitability Analytics Module

Provides comprehensive matter profitability analysis including:
- Revenue vs. cost analysis
- Margin calculations
- Partner profitability contribution
- Practice area profitability
- Matter stage profitability tracking
- Profitability forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


class MatterProfitabilityAnalytics:
    """Analyze matter profitability and financial performance"""

    def __init__(self, matters_df: pd.DataFrame, timekeeping_df: pd.DataFrame,
                 billing_df: pd.DataFrame, expenses_df: pd.DataFrame):
        """
        Initialize matter profitability analytics

        Args:
            matters_df: DataFrame with matter information
            timekeeping_df: DataFrame with timekeeping entries
            billing_df: DataFrame with billing/revenue data
            expenses_df: DataFrame with expense data
        """
        self.matters = matters_df
        self.timekeeping = timekeeping_df
        self.billing = billing_df
        self.expenses = expenses_df

    def calculate_matter_costs(self) -> pd.DataFrame:
        """Calculate total costs by matter"""
        # Timekeeping costs
        tk_costs = self.timekeeping.groupby('matter_id').agg({
            'total_amount': 'sum',
            'hours': 'sum'
        }).rename(columns={'total_amount': 'labor_cost'}).reset_index()

        # Expense costs
        exp_costs = self.expenses.groupby('matter_id')['amount'].sum().reset_index()
        exp_costs.rename(columns={'amount': 'expense_cost'}, inplace=True)

        # Merge costs
        costs = tk_costs.merge(exp_costs, on='matter_id', how='left')
        costs['expense_cost'] = costs['expense_cost'].fillna(0)
        costs['total_cost'] = costs['labor_cost'] + costs['expense_cost']

        return costs

    def calculate_matter_revenue(self) -> pd.DataFrame:
        """Calculate total revenue by matter"""
        revenue = self.billing.groupby('matter_id').agg({
            'amount': 'sum',
            'invoice_id': 'count'
        }).rename(columns={'amount': 'total_revenue', 'invoice_id': 'invoice_count'}).reset_index()

        return revenue

    def calculate_matter_profitability(self) -> pd.DataFrame:
        """Calculate profitability metrics by matter"""
        costs = self.calculate_matter_costs()
        revenue = self.calculate_matter_revenue()

        # Merge with matter info
        profitability = self.matters[['matter_id', 'matter_name', 'client_id', 'practice_area',
                                       'partner_id', 'matter_status']].copy()

        profitability = profitability.merge(revenue, on='matter_id', how='left')
        profitability = profitability.merge(costs, on='matter_id', how='left')

        # Fill nulls
        profitability['total_revenue'] = profitability['total_revenue'].fillna(0)
        profitability['total_cost'] = profitability['total_cost'].fillna(0)

        # Calculate margins
        profitability['gross_profit'] = profitability['total_revenue'] - profitability['total_cost']
        profitability['profit_margin'] = np.where(
            profitability['total_revenue'] > 0,
            (profitability['gross_profit'] / profitability['total_revenue'] * 100),
            0
        )

        # Classify profitability
        profitability['profitability_category'] = pd.cut(
            profitability['profit_margin'],
            bins=[-np.inf, -10, 0, 20, 40, np.inf],
            labels=['Highly Unprofitable', 'Unprofitable', 'Marginally Profitable', 'Profitable', 'Highly Profitable']
        )

        return profitability.sort_values('gross_profit', ascending=False)

    def analyze_by_practice_area(self) -> pd.DataFrame:
        """Analyze profitability by practice area"""
        profitability = self.calculate_matter_profitability()

        pa_analysis = profitability.groupby('practice_area').agg({
            'matter_id': 'count',
            'total_revenue': 'sum',
            'total_cost': 'sum',
            'gross_profit': 'sum',
            'profit_margin': 'mean'
        }).rename(columns={'matter_id': 'matter_count'}).reset_index()

        pa_analysis['avg_revenue_per_matter'] = pa_analysis['total_revenue'] / pa_analysis['matter_count']
        pa_analysis['avg_cost_per_matter'] = pa_analysis['total_cost'] / pa_analysis['matter_count']

        return pa_analysis.sort_values('gross_profit', ascending=False)

    def analyze_by_partner(self) -> pd.DataFrame:
        """Analyze profitability by partner"""
        profitability = self.calculate_matter_profitability()

        partner_analysis = profitability.groupby('partner_id').agg({
            'matter_id': 'count',
            'total_revenue': 'sum',
            'total_cost': 'sum',
            'gross_profit': 'sum',
            'profit_margin': 'mean'
        }).rename(columns={'matter_id': 'matter_count'}).reset_index()

        partner_analysis['avg_profit_per_matter'] = (
            partner_analysis['gross_profit'] / partner_analysis['matter_count']
        )

        return partner_analysis.sort_values('gross_profit', ascending=False)

    def analyze_by_client(self, top_n: int = 20) -> pd.DataFrame:
        """Analyze profitability by client"""
        profitability = self.calculate_matter_profitability()

        client_analysis = profitability.groupby('client_id').agg({
            'matter_id': 'count',
            'total_revenue': 'sum',
            'total_cost': 'sum',
            'gross_profit': 'sum',
            'profit_margin': 'mean'
        }).rename(columns={'matter_id': 'matter_count'}).reset_index()

        client_analysis['avg_revenue_per_matter'] = (
            client_analysis['total_revenue'] / client_analysis['matter_count']
        )

        return client_analysis.sort_values('gross_profit', ascending=False).head(top_n)

    def identify_unprofitable_matters(self, threshold: float = -10) -> pd.DataFrame:
        """Identify unprofitable matters exceeding cost threshold"""
        profitability = self.calculate_matter_profitability()

        unprofitable = profitability[
            profitability['profit_margin'] < threshold
        ][['matter_id', 'matter_name', 'client_id', 'practice_area', 'partner_id',
           'total_revenue', 'total_cost', 'gross_profit', 'profit_margin']].sort_values('gross_profit')

        return unprofitable

    def calculate_realization_rate(self) -> pd.DataFrame:
        """Calculate billing realization rate by matter"""
        costs = self.calculate_matter_costs()[['matter_id', 'labor_cost', 'hours']]
        revenue = self.calculate_matter_revenue()[['matter_id', 'total_revenue']]

        realization = costs.merge(revenue, on='matter_id', how='left')
        realization['total_revenue'] = realization['total_revenue'].fillna(0)

        # Calculate hourly rates
        realization['avg_cost_per_hour'] = np.where(
            realization['hours'] > 0,
            realization['labor_cost'] / realization['hours'],
            0
        )

        realization['avg_billing_per_hour'] = np.where(
            realization['hours'] > 0,
            realization['total_revenue'] / realization['hours'],
            0
        )

        realization['realization_rate'] = np.where(
            realization['avg_cost_per_hour'] > 0,
            (realization['avg_billing_per_hour'] / realization['avg_cost_per_hour'] * 100),
            0
        )

        return realization[['matter_id', 'hours', 'labor_cost', 'total_revenue',
                           'avg_cost_per_hour', 'avg_billing_per_hour', 'realization_rate']].sort_values(
            'realization_rate', ascending=False
        )

    def forecast_matter_profitability(self, matter_id: str, months_ahead: int = 3) -> Dict:
        """Forecast future profitability for a matter"""
        matter_data = self.timekeeping[self.timekeeping['matter_id'] == matter_id].copy()
        matter_data['date'] = pd.to_datetime(matter_data['date'])
        matter_data['year_month'] = matter_data['date'].dt.to_period('M')

        # Historical monthly costs
        monthly_costs = matter_data.groupby('year_month')['total_amount'].sum()

        if len(monthly_costs) < 2:
            return {'error': 'Insufficient data for forecasting'}

        # Simple linear regression for trend
        x = np.arange(len(monthly_costs))
        y = monthly_costs.values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Forecast
        forecast_x = np.arange(len(monthly_costs), len(monthly_costs) + months_ahead)
        forecast_y = slope * forecast_x + intercept

        return {
            'matter_id': matter_id,
            'historical_trend': monthly_costs.to_dict(),
            'forecast_costs': forecast_y.tolist(),
            'trend_slope': slope,
            'r_squared': r_value ** 2,
            'monthly_forecast': [
                {f'month_{i+1}': cost} for i, cost in enumerate(forecast_y)
            ]
        }


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Matters data
    matters = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 101)],
        'matter_name': [f'Matter {i}' for i in range(1, 101)],
        'client_id': [f'C{np.random.randint(1, 21):03d}' for _ in range(100)],
        'practice_area': np.random.choice(['Corporate', 'Litigation', 'IP', 'Employment'], 100),
        'partner_id': [f'P{np.random.randint(1, 11):02d}' for _ in range(100)],
        'matter_status': np.random.choice(['Active', 'Closed'], 100),
        'created_date': pd.date_range('2023-01-01', periods=100, freq='D')
    })

    # Timekeeping data
    timekeeping = pd.DataFrame({
        'entry_id': [f'TK{i:06d}' for i in range(1, 1001)],
        'matter_id': np.random.choice(matters['matter_id'], 1000),
        'hours': np.random.uniform(0.5, 8, 1000),
        'total_amount': np.random.uniform(500, 5000, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='6H')
    })

    # Billing data
    billing = pd.DataFrame({
        'invoice_id': [f'INV{i:06d}' for i in range(1, 501)],
        'matter_id': np.random.choice(matters['matter_id'], 500),
        'amount': np.random.uniform(5000, 50000, 500),
        'invoice_date': pd.date_range('2023-01-01', periods=500, freq='3D')
    })

    # Expenses data
    expenses = pd.DataFrame({
        'expense_id': [f'EXP{i:06d}' for i in range(1, 301)],
        'matter_id': np.random.choice(matters['matter_id'], 300),
        'amount': np.random.uniform(100, 2000, 300),
        'expense_type': np.random.choice(['Travel', 'Research', 'Expert', 'Filing'], 300),
        'expense_date': pd.date_range('2023-01-01', periods=300, freq='5D')
    })

    return matters, timekeeping, billing, expenses


if __name__ == "__main__":
    # Create sample data
    matters_df, timekeeping_df, billing_df, expenses_df = create_sample_data()

    # Initialize analytics
    analytics = MatterProfitabilityAnalytics(matters_df, timekeeping_df, billing_df, expenses_df)

    # Calculate metrics
    print("=" * 80)
    print("MATTER PROFITABILITY ANALYTICS")
    print("=" * 80)

    print("\n1. TOP PROFITABLE MATTERS")
    print("-" * 80)
    profitability = analytics.calculate_matter_profitability()
    print(profitability[['matter_id', 'matter_name', 'total_revenue', 'total_cost',
                        'gross_profit', 'profit_margin']].head(10).to_string(index=False))

    print("\n2. PROFITABILITY BY PRACTICE AREA")
    print("-" * 80)
    pa_analysis = analytics.analyze_by_practice_area()
    print(pa_analysis.to_string(index=False))

    print("\n3. PROFITABILITY BY PARTNER")
    print("-" * 80)
    partner_analysis = analytics.analyze_by_partner()
    print(partner_analysis.to_string(index=False))

    print("\n4. TOP 10 CLIENTS BY PROFITABILITY")
    print("-" * 80)
    client_analysis = analytics.analyze_by_client(top_n=10)
    print(client_analysis.to_string(index=False))

    print("\n5. UNPROFITABLE MATTERS (< -10% margin)")
    print("-" * 80)
    unprofitable = analytics.identify_unprofitable_matters()
    if len(unprofitable) > 0:
        print(unprofitable.head(10).to_string(index=False))
    else:
        print("No unprofitable matters found")

    print("\n6. BILLING REALIZATION RATES")
    print("-" * 80)
    realization = analytics.calculate_realization_rate()
    print(realization.head(10).to_string(index=False))

    print("\n7. PROFITABILITY FORECAST (Sample Matter)")
    print("-" * 80)
    forecast = analytics.forecast_matter_profitability('M00001')
    print(f"Matter: {forecast['matter_id']}")
    print(f"Trend Slope: {forecast['trend_slope']:.2f}")
    print(f"R-Squared: {forecast['r_squared']:.4f}")
