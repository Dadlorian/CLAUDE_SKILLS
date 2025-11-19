"""
Vendor Performance Analytics Module

Provides comprehensive vendor performance tracking including:
- Spend analysis by vendor
- Quality metrics (defect rates, revision rates)
- Time efficiency analysis
- Cost trend analysis
- Vendor rating and ranking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class VendorPerformanceAnalytics:
    """Analyze and track vendor performance metrics"""

    def __init__(self, vendors_df: pd.DataFrame, matters_df: pd.DataFrame, timekeeping_df: pd.DataFrame):
        """
        Initialize vendor performance analytics

        Args:
            vendors_df: DataFrame with vendor information
            matters_df: DataFrame with matter data and associated vendors
            timekeeping_df: DataFrame with timekeeping entries
        """
        self.vendors = vendors_df
        self.matters = matters_df
        self.timekeeping = timekeeping_df
        self.metrics = {}

    def calculate_vendor_spend(self, period_days: int = 365) -> pd.DataFrame:
        """Calculate total spend by vendor for recent period"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_tk = self.timekeeping[
            pd.to_datetime(self.timekeeping['date']) >= cutoff_date
        ]

        spend = recent_tk.groupby('vendor_id').agg({
            'total_amount': 'sum',
            'hours': 'sum',
            'entry_id': 'count'
        }).rename(columns={'total_amount': 'total_spend', 'entry_id': 'entry_count'})

        # Merge vendor info
        spend = spend.reset_index()
        spend = spend.merge(self.vendors[['vendor_id', 'vendor_name']], on='vendor_id')

        # Calculate average rate
        spend['avg_hourly_rate'] = spend['total_spend'] / spend['hours'].replace(0, np.nan)

        return spend.sort_values('total_spend', ascending=False)

    def calculate_quality_metrics(self) -> pd.DataFrame:
        """Calculate quality metrics by vendor"""
        # Sample implementation
        quality_df = self.timekeeping.groupby('vendor_id').agg({
            'revision_count': 'mean',
            'defect_count': 'mean',
            'rework_hours': 'sum'
        }).reset_index()

        quality_df = quality_df.merge(
            self.vendors[['vendor_id', 'vendor_name']],
            on='vendor_id'
        )

        # Calculate quality score (0-100)
        quality_df['quality_score'] = (
            100 - (quality_df['revision_count'] * 10 + quality_df['defect_count'] * 15)
        ).clip(0, 100)

        return quality_df.sort_values('quality_score', ascending=False)

    def calculate_on_time_delivery(self, period_days: int = 365) -> pd.DataFrame:
        """Calculate on-time delivery percentage by vendor"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_matters = self.matters[
            pd.to_datetime(self.matters['created_date']) >= cutoff_date
        ]

        matters_by_vendor = recent_matters.groupby('assigned_vendor_id').agg({
            'matter_id': 'count',
            'on_time_delivery': lambda x: (x == 1).sum()
        }).reset_index()

        matters_by_vendor['on_time_percentage'] = (
            matters_by_vendor['on_time_delivery'] / matters_by_vendor['matter_id'] * 100
        )

        matters_by_vendor = matters_by_vendor.merge(
            self.vendors[['vendor_id', 'vendor_name']],
            left_on='assigned_vendor_id',
            right_on='vendor_id'
        )

        return matters_by_vendor[['vendor_name', 'matter_id', 'on_time_percentage']].sort_values(
            'on_time_percentage', ascending=False
        )

    def calculate_compliance_score(self) -> pd.DataFrame:
        """Calculate compliance score for each vendor"""
        compliance_df = self.timekeeping.groupby('vendor_id').agg({
            'compliance_violations': 'sum',
            'total_amount': 'count',
            'audit_findings': 'sum'
        }).reset_index()

        compliance_df['violation_rate'] = (
            compliance_df['compliance_violations'] / compliance_df['total_amount']
        )

        compliance_df['compliance_score'] = (
            100 * (1 - compliance_df['violation_rate'])
        ).clip(0, 100)

        compliance_df = compliance_df.merge(
            self.vendors[['vendor_id', 'vendor_name']],
            on='vendor_id'
        )

        return compliance_df[['vendor_name', 'compliance_score', 'violation_rate']].sort_values(
            'compliance_score', ascending=False
        )

    def generate_vendor_scorecard(self) -> pd.DataFrame:
        """Generate comprehensive vendor scorecard"""
        scorecard = self.calculate_vendor_spend().copy()

        # Add quality metrics
        quality = self.calculate_quality_metrics()[['vendor_id', 'quality_score']]
        scorecard = scorecard.merge(quality, on='vendor_id', how='left')

        # Add on-time delivery
        on_time = self.calculate_on_time_delivery()[['vendor_name', 'on_time_percentage']]
        scorecard = scorecard.merge(on_time, on='vendor_name', how='left')

        # Add compliance
        compliance = self.calculate_compliance_score()[['vendor_name', 'compliance_score']]
        scorecard = scorecard.merge(compliance, on='vendor_name', how='left')

        # Calculate overall score
        scorecard['overall_score'] = (
            scorecard[['quality_score', 'on_time_percentage', 'compliance_score']].mean(axis=1)
        )

        # Assign rating
        scorecard['rating'] = pd.cut(
            scorecard['overall_score'],
            bins=[0, 60, 75, 85, 100],
            labels=['Poor', 'Fair', 'Good', 'Excellent']
        )

        return scorecard.sort_values('overall_score', ascending=False)

    def identify_cost_trends(self, vendor_id: str, periods: int = 12) -> Dict:
        """Identify cost trends for specific vendor"""
        vendor_data = self.timekeeping[self.timekeeping['vendor_id'] == vendor_id].copy()
        vendor_data['date'] = pd.to_datetime(vendor_data['date'])
        vendor_data['year_month'] = vendor_data['date'].dt.to_period('M')

        monthly_spend = vendor_data.groupby('year_month')['total_amount'].sum().tail(periods)

        # Calculate trend
        x = np.arange(len(monthly_spend))
        y = monthly_spend.values
        z = np.polyfit(x, y, 1)
        trend_direction = "increasing" if z[0] > 0 else "decreasing"

        return {
            'vendor_id': vendor_id,
            'trend_direction': trend_direction,
            'monthly_trend': monthly_spend.to_dict(),
            'percent_change': ((y[-1] - y[0]) / y[0] * 100) if y[0] > 0 else 0
        }


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Vendors data
    vendors = pd.DataFrame({
        'vendor_id': [f'V{i:03d}' for i in range(1, 11)],
        'vendor_name': [f'Vendor {i}' for i in range(1, 11)],
        'location': np.random.choice(['New York', 'Los Angeles', 'Chicago'], 10),
        'category': np.random.choice(['Discovery', 'Document Review', 'Litigation Support'], 10)
    })

    # Matters data
    matters = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 101)],
        'assigned_vendor_id': np.random.choice(vendors['vendor_id'], 100),
        'created_date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'on_time_delivery': np.random.choice([0, 1], 100, p=[0.15, 0.85])
    })

    # Timekeeping data
    timekeeping = pd.DataFrame({
        'entry_id': [f'TK{i:06d}' for i in range(1, 1001)],
        'vendor_id': np.random.choice(vendors['vendor_id'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='6H'),
        'hours': np.random.uniform(0.5, 8, 1000),
        'total_amount': np.random.uniform(500, 5000, 1000),
        'revision_count': np.random.randint(0, 3, 1000),
        'defect_count': np.random.randint(0, 2, 1000),
        'rework_hours': np.random.uniform(0, 4, 1000),
        'compliance_violations': np.random.randint(0, 1, 1000),
        'audit_findings': np.random.randint(0, 2, 1000)
    })

    return vendors, matters, timekeeping


if __name__ == "__main__":
    # Create sample data
    vendors_df, matters_df, timekeeping_df = create_sample_data()

    # Initialize analytics
    analytics = VendorPerformanceAnalytics(vendors_df, matters_df, timekeeping_df)

    # Calculate metrics
    print("=" * 80)
    print("VENDOR PERFORMANCE ANALYTICS")
    print("=" * 80)

    print("\n1. VENDOR SPEND ANALYSIS")
    print("-" * 80)
    spend = analytics.calculate_vendor_spend()
    print(spend.to_string(index=False))

    print("\n2. QUALITY METRICS BY VENDOR")
    print("-" * 80)
    quality = analytics.calculate_quality_metrics()
    print(quality.to_string(index=False))

    print("\n3. ON-TIME DELIVERY PERFORMANCE")
    print("-" * 80)
    on_time = analytics.calculate_on_time_delivery()
    print(on_time.to_string(index=False))

    print("\n4. COMPLIANCE SCORES")
    print("-" * 80)
    compliance = analytics.calculate_compliance_score()
    print(compliance.to_string(index=False))

    print("\n5. OVERALL VENDOR SCORECARD")
    print("-" * 80)
    scorecard = analytics.generate_vendor_scorecard()
    print(scorecard.to_string(index=False))

    print("\n6. COST TREND ANALYSIS (Sample Vendor)")
    print("-" * 80)
    trend = analytics.identify_cost_trends('V001')
    print(f"Vendor: {trend['vendor_id']}")
    print(f"Trend Direction: {trend['trend_direction']}")
    print(f"Percent Change: {trend['percent_change']:.2f}%")
