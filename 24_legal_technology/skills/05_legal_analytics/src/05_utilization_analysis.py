#!/usr/bin/env python3
"""
Legal Department Utilization Analysis
Analyzes billable hours, utilization rates, and capacity planning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

class UtilizationAnalyzer:
    """Analyze lawyer and staff utilization"""

    def __init__(self, timesheet_data):
        """Initialize with timesheet data"""
        self.df = pd.read_csv(timesheet_data) if isinstance(timesheet_data, str) else timesheet_data
        self.df['entry_date'] = pd.to_datetime(self.df['entry_date'])

        # Constants
        self.working_days_per_year = 250
        self.hours_per_day = 8
        self.vacation_days_per_year = 20
        self.training_days_per_year = 5
        self.admin_days_per_year = 10

    def calculate_available_hours(self, staff_level='associate'):
        """Calculate available billable hours per year"""

        available_days = self.working_days_per_year - self.vacation_days_per_year

        # Reduce for training/admin based on level
        if staff_level == 'partner':
            available_days -= 15  # Partners spend more time on non-billable work
        elif staff_level == 'counsel':
            available_days -= 10
        elif staff_level == 'associate':
            available_days -= self.training_days_per_year + self.admin_days_per_year
        else:
            available_days -= 10

        return available_days * self.hours_per_day

    def calculate_utilization_rates(self):
        """Calculate utilization rates by staff member"""

        utilization = self.df.groupby('staff_id').agg({
            'billable_hours': 'sum',
            'staff_name': 'first',
            'staff_level': 'first',
            'entry_date': ['count', 'min', 'max']
        })

        utilization.columns = ['billable_hours', 'staff_name', 'staff_level', 'days_worked', 'start_date', 'end_date']

        # Calculate available hours based on period and level
        utilization['available_hours'] = utilization.apply(
            lambda row: self._calculate_available_for_period(row['start_date'], row['end_date'], row['staff_level']),
            axis=1
        )

        utilization['utilization_rate'] = (utilization['billable_hours'] / utilization['available_hours'] * 100).round(1)

        return utilization.sort_values('utilization_rate', ascending=False)

    def _calculate_available_for_period(self, start_date, end_date, level):
        """Calculate available hours for specific period"""

        days_period = (end_date - start_date).days / 365.25  # Annualize

        available = self.calculate_available_hours(level)
        return available * days_period

    def utilization_by_department(self):
        """Get utilization rates by department"""

        dept_util = self.df.groupby('department').agg({
            'billable_hours': 'sum',
            'staff_id': 'nunique',
            'total_hours': 'sum'
        })

        dept_util.columns = ['billable_hours', 'staff_count', 'total_hours']
        dept_util['utilization_rate'] = (dept_util['billable_hours'] / dept_util['total_hours'] * 100).round(1)
        dept_util['billable_per_person'] = (dept_util['billable_hours'] / dept_util['staff_count']).round(0)

        return dept_util.sort_values('utilization_rate', ascending=False)

    def utilization_by_practice_area(self):
        """Get utilization by practice area"""

        practice_util = self.df.groupby('practice_area').agg({
            'billable_hours': 'sum',
            'staff_id': 'nunique',
            'total_hours': 'sum',
            'hourly_rate': 'mean'
        })

        practice_util.columns = ['billable_hours', 'staff_count', 'total_hours', 'avg_rate']
        practice_util['utilization_rate'] = (practice_util['billable_hours'] / practice_util['total_hours'] * 100).round(1)
        practice_util['revenue'] = practice_util['billable_hours'] * practice_util['avg_rate']

        return practice_util.sort_values('billable_hours', ascending=False)

    def capacity_planning(self, target_utilization=0.80):
        """Identify capacity gaps"""

        util_rates = self.calculate_utilization_rates()

        capacity = pd.DataFrame({
            'understaffed': util_rates[util_rates['utilization_rate'] > target_utilization * 100].shape[0],
            'optimal': util_rates[(util_rates['utilization_rate'] >= target_utilization * 0.9 * 100) &
                                   (util_rates['utilization_rate'] <= target_utilization * 100)].shape[0],
            'overstaffed': util_rates[util_rates['utilization_rate'] < target_utilization * 0.9 * 100].shape[0],
            'total_staff': len(util_rates)
        })

        return capacity

    def bench_time_analysis(self):
        """Analyze unallocated ('bench') time"""

        total_time = self.df['total_hours'].sum()
        billable_time = self.df['billable_hours'].sum()
        bench_time = total_time - billable_time

        bench_df = self.df.groupby('staff_id').agg({
            'staff_name': 'first',
            'staff_level': 'first',
            'billable_hours': 'sum',
            'total_hours': 'sum'
        })

        bench_df['bench_hours'] = bench_df['total_hours'] - bench_df['billable_hours']
        bench_df['bench_pct'] = (bench_df['bench_hours'] / bench_df['total_hours'] * 100).round(1)

        return bench_df.sort_values('bench_hours', ascending=False)

    def revenue_per_fte(self):
        """Calculate revenue per FTE"""

        # Total billable hours * average rate
        revenue_per_person = self.df.groupby('staff_id').agg({
            'staff_name': 'first',
            'staff_level': 'first',
            'billable_hours': 'sum',
            'hourly_rate': 'mean'
        })

        revenue_per_person['annual_revenue'] = revenue_per_person['billable_hours'] * revenue_per_person['hourly_rate']

        return revenue_per_person.sort_values('annual_revenue', ascending=False)

    def billable_hour_targets(self):
        """Define billable hour targets by level"""

        targets = {
            'partner': {
                'minimum': 1500,
                'target': 1800,
                'stretch': 2000,
                'reason': 'Partners typically have higher non-billable work'
            },
            'counsel': {
                'minimum': 1600,
                'target': 1900,
                'stretch': 2100,
                'reason': 'Balance of billable and mentoring'
            },
            'associate': {
                'minimum': 1800,
                'target': 2000,
                'stretch': 2200,
                'reason': 'High billable expectations'
            },
            'paralegal': {
                'minimum': 1600,
                'target': 1800,
                'stretch': 2000,
                'reason': 'Administrative support and training'
            }
        }

        return targets

    def forecast_annual_hours(self, months_completed=6):
        """Forecast annual billable hours based on YTD performance"""

        recent_months = self.df[self.df['entry_date'] >= datetime.now() - timedelta(days=months_completed * 30)]

        forecast = recent_months.groupby('staff_id').agg({
            'staff_name': 'first',
            'billable_hours': 'sum'
        })

        forecast['ytd_hours'] = forecast['billable_hours']
        forecast['projected_annual'] = forecast['billable_hours'] * (12 / months_completed)
        forecast['vs_target'] = forecast['projected_annual'] - 1900  # Assume 1900 as baseline

        return forecast.sort_values('vs_target', ascending=False)

    def generate_utilization_report(self):
        """Generate comprehensive utilization report"""

        report = f"""
LEGAL DEPARTMENT UTILIZATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d')}

SUMMARY STATISTICS
==================
Total Staff: {self.df['staff_id'].nunique()}
Reporting Period: {self.df['entry_date'].min().date()} to {self.df['entry_date'].max().date()}

Overall Metrics:
- Total Billable Hours: {self.df['billable_hours'].sum():,.0f}
- Total Hours Recorded: {self.df['total_hours'].sum():,.0f}
- Overall Utilization Rate: {self.df['billable_hours'].sum() / self.df['total_hours'].sum() * 100:.1f}%
- Average per Person: {self.df['billable_hours'].sum() / self.df['staff_id'].nunique():,.0f} hours

UTILIZATION BY DEPARTMENT
==========================
{self.utilization_by_department().to_string()}

UTILIZATION BY PRACTICE AREA
============================
{self.utilization_by_practice_area().to_string()}

CAPACITY ASSESSMENT
===================
{self.capacity_planning().to_string()}

TOP PERFORMERS (Highest Utilization)
====================================
{self.calculate_utilization_rates().head(10).to_string()}

BENCH TIME ANALYSIS
===================
Total Bench Hours: {self.df['total_hours'].sum() - self.df['billable_hours'].sum():,.0f}
Bench Time %: {(self.df['total_hours'].sum() - self.df['billable_hours'].sum()) / self.df['total_hours'].sum() * 100:.1f}%

Staff with Highest Bench Time:
{self.bench_time_analysis().head(5).to_string()}

REVENUE PER FTE (Top 10)
=======================
{self.revenue_per_fte().head(10).to_string()}

RECOMMENDATIONS
===============
- Review staff with utilization >90% for burnout risk
- Investigate bench time >15% for capacity issues
- Reallocate work from understaffed to overstaffed areas
- Consider hiring if demand exceeds capacity
        """

        return report


if __name__ == "__main__":
    # Sample data
    sample_data = {
        'staff_id': np.tile(np.arange(1, 11), 12),
        'staff_name': np.tile(['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown',
                               'Charlie Davis', 'Diana Wilson', 'Edward Moore', 'Fiona Taylor',
                               'George Anderson', 'Hannah Thomas'], 12),
        'staff_level': np.tile(['partner', 'partner', 'counsel', 'counsel', 'counsel',
                                'associate', 'associate', 'associate', 'paralegal', 'paralegal'], 12),
        'department': np.tile(['litigation', 'corporate', 'litigation', 'corporate', 'regulatory',
                               'litigation', 'corporate', 'ip', 'litigation', 'corporate'], 12),
        'practice_area': np.tile(['Litigation', 'M&A', 'Litigation', 'Corporate', 'Regulatory',
                                  'Litigation', 'Corporate', 'IP', 'Litigation', 'Corporate'], 12),
        'entry_date': pd.date_range('2024-01-01', periods=120, freq='W'),
        'billable_hours': np.random.uniform(30, 60, 120),
        'total_hours': np.random.uniform(35, 70, 120),
        'hourly_rate': np.random.choice([400, 350, 300, 250, 200, 150], 120)
    }

    df = pd.DataFrame(sample_data)
    analyzer = UtilizationAnalyzer(df)

    print(analyzer.generate_utilization_report())
