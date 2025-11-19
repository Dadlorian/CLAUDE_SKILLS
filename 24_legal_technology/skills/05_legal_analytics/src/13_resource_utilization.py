"""
Resource Utilization Analytics Module

Provides comprehensive resource utilization analysis including:
- Billable vs. non-billable hours tracking
- Utilization rate calculations
- Resource capacity planning
- Attorney workload analysis
- Skill-based resource allocation
- Utilization trend analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')


class ResourceUtilizationAnalytics:
    """Analyze and optimize resource utilization"""

    def __init__(self, staff_df: pd.DataFrame, timekeeping_df: pd.DataFrame, capacity_df: pd.DataFrame):
        """
        Initialize resource utilization analytics

        Args:
            staff_df: DataFrame with staff information
            timekeeping_df: DataFrame with timekeeping entries
            capacity_df: DataFrame with capacity/availability data
        """
        self.staff = staff_df
        self.timekeeping = timekeeping_df
        self.capacity = capacity_df

    def calculate_utilization_rates(self, period_days: int = 30) -> pd.DataFrame:
        """Calculate utilization rates by resource"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Filter recent timekeeping
        recent_tk = self.timekeeping[
            pd.to_datetime(self.timekeeping['date']) >= cutoff_date
        ].copy()

        # Calculate billable vs non-billable
        billable = recent_tk[recent_tk['is_billable'] == True].groupby('staff_id')['hours'].sum()
        non_billable = recent_tk[recent_tk['is_billable'] == False].groupby('staff_id')['hours'].sum()

        # Expected hours (from capacity)
        capacity_hours = self.capacity.groupby('staff_id')['available_hours'].sum()

        # Create utilization dataframe
        util = pd.DataFrame({
            'staff_id': self.staff['staff_id'],
            'staff_name': self.staff['staff_name'],
            'position': self.staff['position']
        }).set_index('staff_id')

        util['billable_hours'] = billable
        util['non_billable_hours'] = non_billable
        util['available_hours'] = capacity_hours
        util['billable_hours'] = util['billable_hours'].fillna(0)
        util['non_billable_hours'] = util['non_billable_hours'].fillna(0)
        util['available_hours'] = util['available_hours'].fillna(0)

        # Calculate rates
        util['total_hours'] = util['billable_hours'] + util['non_billable_hours']
        util['billable_rate'] = np.where(
            util['total_hours'] > 0,
            (util['billable_hours'] / util['total_hours'] * 100),
            0
        )

        util['utilization_rate'] = np.where(
            util['available_hours'] > 0,
            (util['total_hours'] / util['available_hours'] * 100),
            0
        )

        return util.reset_index().sort_values('utilization_rate', ascending=False)

    def calculate_workload_distribution(self, period_days: int = 30) -> pd.DataFrame:
        """Calculate workload distribution across resources"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_tk = self.timekeeping[
            pd.to_datetime(self.timekeeping['date']) >= cutoff_date
        ].copy()

        workload = recent_tk.groupby('staff_id').agg({
            'hours': 'sum',
            'matter_id': 'nunique',
            'task_id': 'nunique'
        }).reset_index()

        workload.rename(columns={
            'hours': 'total_hours',
            'matter_id': 'matters_assigned',
            'task_id': 'tasks_assigned'
        }, inplace=True)

        # Merge with staff info
        workload = workload.merge(
            self.staff[['staff_id', 'staff_name', 'position']],
            on='staff_id'
        )

        workload['avg_hours_per_matter'] = workload['total_hours'] / workload['matters_assigned']
        workload['avg_hours_per_task'] = workload['total_hours'] / workload['tasks_assigned']

        return workload.sort_values('total_hours', ascending=False)

    def analyze_by_position(self, period_days: int = 30) -> pd.DataFrame:
        """Analyze utilization by position level"""
        util = self.calculate_utilization_rates(period_days)

        position_analysis = util.groupby('position').agg({
            'staff_id': 'count',
            'billable_hours': 'mean',
            'billable_rate': 'mean',
            'utilization_rate': 'mean',
            'total_hours': 'mean'
        }).rename(columns={'staff_id': 'staff_count'}).reset_index()

        position_analysis = position_analysis.sort_values('utilization_rate', ascending=False)

        return position_analysis

    def identify_over_allocated(self, threshold: float = 120) -> pd.DataFrame:
        """Identify over-allocated resources"""
        util = self.calculate_utilization_rates()

        over_allocated = util[
            util['utilization_rate'] > threshold
        ][['staff_id', 'staff_name', 'position', 'total_hours', 'available_hours', 'utilization_rate']].sort_values(
            'utilization_rate', ascending=False
        )

        return over_allocated

    def identify_under_utilized(self, threshold: float = 60) -> pd.DataFrame:
        """Identify under-utilized resources"""
        util = self.calculate_utilization_rates()

        under_utilized = util[
            util['utilization_rate'] < threshold
        ][['staff_id', 'staff_name', 'position', 'total_hours', 'available_hours', 'utilization_rate']].sort_values(
            'utilization_rate'
        )

        return under_utilized

    def calculate_skill_based_utilization(self) -> pd.DataFrame:
        """Calculate utilization by skill set"""
        # Get skills from staff
        skills_data = self.staff[['staff_id', 'staff_name', 'primary_skill', 'position']].copy()

        # Merge with utilization
        util = self.calculate_utilization_rates()
        skills_data = skills_data.merge(
            util[['staff_id', 'billable_hours', 'utilization_rate']],
            on='staff_id'
        )

        # Aggregate by skill
        skill_util = skills_data.groupby('primary_skill').agg({
            'staff_id': 'count',
            'billable_hours': 'sum',
            'utilization_rate': 'mean'
        }).rename(columns={'staff_id': 'staff_count'}).reset_index()

        return skill_util.sort_values('utilization_rate', ascending=False)

    def project_capacity_needs(self, months_ahead: int = 3) -> Dict:
        """Project future capacity needs based on trends"""
        recent_util = self.calculate_utilization_rates(period_days=90)

        # Calculate average utilization
        avg_util = recent_util['utilization_rate'].mean()
        std_util = recent_util['utilization_rate'].std()

        # Identify positions at risk
        position_util = self.analyze_by_position(period_days=90)

        capacity_needs = {
            'current_avg_utilization': avg_util,
            'utilization_volatility': std_util,
            'positions_at_capacity': position_util[position_util['utilization_rate'] > 100].to_dict('records'),
            'recommendation': 'Increase headcount' if avg_util > 85 else 'Current capacity adequate'
        }

        return capacity_needs

    def calculate_bench_time(self, period_days: int = 30) -> pd.DataFrame:
        """Calculate bench time (non-billable hours) by resource"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_tk = self.timekeeping[
            pd.to_datetime(self.timekeeping['date']) >= cutoff_date
        ].copy()

        bench = recent_tk.groupby('staff_id').agg({
            'hours': 'sum',
            'time_type': lambda x: (x == 'bench').sum()
        }).reset_index()

        bench.rename(columns={'hours': 'total_hours', 'time_type': 'bench_hours'}, inplace=True)

        bench['bench_percentage'] = np.where(
            bench['total_hours'] > 0,
            (bench['bench_hours'] / bench['total_hours'] * 100),
            0
        )

        bench = bench.merge(
            self.staff[['staff_id', 'staff_name', 'position']],
            on='staff_id'
        )

        return bench.sort_values('bench_percentage', ascending=False)

    def analyze_matter_coverage(self) -> pd.DataFrame:
        """Analyze resource coverage on matters"""
        coverage = self.timekeeping.groupby('matter_id').agg({
            'staff_id': 'nunique',
            'hours': 'sum'
        }).reset_index()

        coverage.rename(columns={
            'staff_id': 'resource_count',
            'hours': 'total_hours'
        }, inplace=True)

        coverage['avg_hours_per_resource'] = coverage['total_hours'] / coverage['resource_count']

        return coverage.sort_values('total_hours', ascending=False).head(20)


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Staff data
    staff = pd.DataFrame({
        'staff_id': [f'S{i:04d}' for i in range(1, 51)],
        'staff_name': [f'Attorney {i}' for i in range(1, 51)],
        'position': np.random.choice(['Partner', 'Senior Associate', 'Associate', 'Junior Associate'], 50),
        'primary_skill': np.random.choice(['Corporate', 'Litigation', 'IP', 'Employment'], 50)
    })

    # Capacity data
    capacity = pd.DataFrame({
        'staff_id': np.repeat(staff['staff_id'], 12),  # 12 months
        'month': [f'2023-{i:02d}' for i in range(1, 13)] * 50,
        'available_hours': np.random.uniform(120, 160, 600)
    })

    # Timekeeping data
    timekeeping = pd.DataFrame({
        'entry_id': [f'TK{i:06d}' for i in range(1, 2001)],
        'staff_id': np.random.choice(staff['staff_id'], 2000),
        'matter_id': [f'M{np.random.randint(1, 101):05d}' for _ in range(2000)],
        'task_id': [f'T{np.random.randint(1, 501):05d}' for _ in range(2000)],
        'hours': np.random.uniform(0.5, 8, 2000),
        'is_billable': np.random.choice([True, False], 2000, p=[0.75, 0.25]),
        'time_type': np.random.choice(['billable', 'admin', 'bench'], 2000),
        'date': pd.date_range('2023-01-01', periods=2000, freq='3H')
    })

    return staff, timekeeping, capacity


if __name__ == "__main__":
    # Create sample data
    staff_df, timekeeping_df, capacity_df = create_sample_data()

    # Initialize analytics
    analytics = ResourceUtilizationAnalytics(staff_df, timekeeping_df, capacity_df)

    # Calculate metrics
    print("=" * 80)
    print("RESOURCE UTILIZATION ANALYTICS")
    print("=" * 80)

    print("\n1. TOP UTILIZED RESOURCES (Last 30 days)")
    print("-" * 80)
    util = analytics.calculate_utilization_rates()
    print(util[['staff_id', 'staff_name', 'position', 'billable_hours', 'utilization_rate']].head(10).to_string(index=False))

    print("\n2. WORKLOAD DISTRIBUTION")
    print("-" * 80)
    workload = analytics.calculate_workload_distribution()
    print(workload.head(10).to_string(index=False))

    print("\n3. UTILIZATION BY POSITION")
    print("-" * 80)
    position_analysis = analytics.analyze_by_position()
    print(position_analysis.to_string(index=False))

    print("\n4. OVER-ALLOCATED RESOURCES (> 120%)")
    print("-" * 80)
    over_allocated = analytics.identify_over_allocated()
    if len(over_allocated) > 0:
        print(over_allocated.to_string(index=False))
    else:
        print("No over-allocated resources")

    print("\n5. UNDER-UTILIZED RESOURCES (< 60%)")
    print("-" * 80)
    under_utilized = analytics.identify_under_utilized()
    if len(under_utilized) > 0:
        print(under_utilized.to_string(index=False))
    else:
        print("No under-utilized resources")

    print("\n6. UTILIZATION BY SKILL")
    print("-" * 80)
    skill_util = analytics.calculate_skill_based_utilization()
    print(skill_util.to_string(index=False))

    print("\n7. BENCH TIME ANALYSIS")
    print("-" * 80)
    bench = analytics.calculate_bench_time()
    print(bench.head(10).to_string(index=False))

    print("\n8. CAPACITY NEEDS PROJECTION")
    print("-" * 80)
    capacity = analytics.project_capacity_needs()
    print(f"Average Utilization: {capacity['current_avg_utilization']:.2f}%")
    print(f"Utilization Volatility: {capacity['utilization_volatility']:.2f}%")
    print(f"Recommendation: {capacity['recommendation']}")
