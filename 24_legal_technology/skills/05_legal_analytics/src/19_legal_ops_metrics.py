"""
Legal Operations Metrics Module

Provides comprehensive legal operations key performance indicators including:
- Legal operations KPI dashboard
- Process efficiency metrics
- Compliance and risk metrics
- Client satisfaction metrics
- Matter management metrics
- Case volume and cycle time analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class LegalOpsMetrics:
    """Calculate and track legal operations KPIs"""

    def __init__(self, matters_df: pd.DataFrame, timekeeping_df: pd.DataFrame,
                 matters_opened_closed: pd.DataFrame, client_feedback_df: pd.DataFrame = None):
        """
        Initialize legal ops metrics

        Args:
            matters_df: DataFrame with matter information
            timekeeping_df: DataFrame with timekeeping entries
            matters_opened_closed: DataFrame with matter open/close dates
            client_feedback_df: DataFrame with client feedback
        """
        self.matters = matters_df
        self.timekeeping = timekeeping_df
        self.matters_opened_closed = matters_opened_closed
        self.client_feedback = client_feedback_df

    def calculate_case_volume(self, period_days: int = 365) -> Dict:
        """Calculate case volume metrics"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Cases opened
        opened = self.matters_opened_closed[
            pd.to_datetime(self.matters_opened_closed['opened_date']) >= cutoff_date
        ]

        # Cases closed
        closed = self.matters_opened_closed[
            pd.to_datetime(self.matters_opened_closed['closed_date']) >= cutoff_date
        ]

        # Current active cases
        active_cases = self.matters[
            self.matters['matter_status'] == 'Active'
        ]

        return {
            'cases_opened': len(opened),
            'cases_closed': len(closed),
            'cases_active': len(active_cases),
            'period_days': period_days,
            'avg_cases_per_month': len(opened) / (period_days / 30)
        }

    def calculate_matter_cycle_time(self) -> pd.DataFrame:
        """Calculate average cycle time for matters"""
        cycle_times = self.matters_opened_closed.copy()

        # Calculate cycle time
        cycle_times['opened_date'] = pd.to_datetime(cycle_times['opened_date'])
        cycle_times['closed_date'] = pd.to_datetime(cycle_times['closed_date'])

        cycle_times['cycle_time_days'] = (
            cycle_times['closed_date'] - cycle_times['opened_date']
        ).dt.days

        # Only include closed matters
        closed_matters = cycle_times[cycle_times['cycle_time_days'] > 0]

        summary = {
            'avg_cycle_time_days': closed_matters['cycle_time_days'].mean(),
            'median_cycle_time_days': closed_matters['cycle_time_days'].median(),
            'min_cycle_time_days': closed_matters['cycle_time_days'].min(),
            'max_cycle_time_days': closed_matters['cycle_time_days'].max(),
            'std_dev_cycle_time': closed_matters['cycle_time_days'].std()
        }

        return closed_matters, summary

    def calculate_staffing_efficiency(self) -> pd.DataFrame:
        """Calculate staffing and resource efficiency metrics"""
        # Hours per matter
        hours_per_matter = self.timekeeping.groupby('matter_id')['hours'].sum().reset_index()
        hours_per_matter.rename(columns={'hours': 'total_hours'}, inplace=True)

        # Matter count per staff
        staff_workload = self.timekeeping.groupby('staff_id').agg({
            'matter_id': 'nunique',
            'hours': 'sum'
        }).reset_index()

        staff_workload['avg_hours_per_matter'] = (
            staff_workload['hours'] / staff_workload['matter_id']
        )

        staff_workload.rename(columns={
            'matter_id': 'matters_assigned',
            'hours': 'total_hours'
        }, inplace=True)

        return staff_workload

    def calculate_client_satisfaction(self) -> Dict:
        """Calculate client satisfaction metrics"""
        if self.client_feedback is None or self.client_feedback.empty:
            return {'error': 'No client feedback data available'}

        satisfaction = {
            'avg_satisfaction_score': self.client_feedback['satisfaction_score'].mean(),
            'median_satisfaction_score': self.client_feedback['satisfaction_score'].median(),
            'nps_score': self._calculate_nps(self.client_feedback['satisfaction_score']),
            'total_responses': len(self.client_feedback),
            'positive_feedback_percent': (
                (self.client_feedback['satisfaction_score'] >= 4).sum() /
                len(self.client_feedback) * 100
            )
        }

        return satisfaction

    @staticmethod
    def _calculate_nps(scores: pd.Series) -> float:
        """Calculate Net Promoter Score"""
        promoters = (scores >= 9).sum()
        detractors = (scores <= 6).sum()
        total = len(scores)

        if total == 0:
            return 0

        nps = ((promoters - detractors) / total) * 100
        return nps

    def calculate_process_metrics(self, period_days: int = 30) -> Dict:
        """Calculate process efficiency metrics"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_tk = self.timekeeping[
            pd.to_datetime(self.timekeeping['date']) >= cutoff_date
        ]

        metrics = {
            'total_hours_logged': recent_tk['hours'].sum(),
            'avg_entry_duration': recent_tk['hours'].mean(),
            'total_entries': len(recent_tk),
            'entries_per_day': len(recent_tk) / period_days,
            'matters_active': self.matters[self.matters['matter_status'] == 'Active'].shape[0],
            'period_days': period_days
        }

        return metrics

    def calculate_compliance_metrics(self, period_days: int = 365) -> Dict:
        """Calculate compliance and risk metrics"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_matters = self.matters[
            pd.to_datetime(self.matters['created_date']) >= cutoff_date
        ]

        # Compliance calculations
        at_risk = recent_matters[recent_matters['risk_level'].isin(['High', 'Critical'])].shape[0]
        overdue_matters = recent_matters[recent_matters['is_overdue'] == True].shape[0]

        compliance = {
            'total_matters': len(recent_matters),
            'high_risk_matters': at_risk,
            'high_risk_percent': (at_risk / len(recent_matters) * 100) if len(recent_matters) > 0 else 0,
            'overdue_matters': overdue_matters,
            'on_time_percent': (
                (len(recent_matters) - overdue_matters) / len(recent_matters) * 100
            ) if len(recent_matters) > 0 else 0,
            'period_days': period_days
        }

        return compliance

    def calculate_billing_efficiency(self) -> Dict:
        """Calculate billing and realization metrics"""
        # Calculate realization rate
        billable_tk = self.timekeeping[self.timekeeping['is_billable'] == True]
        total_billable_hours = billable_tk['hours'].sum()
        total_billable_amount = billable_tk['total_amount'].sum()

        # Billing rate
        avg_billing_rate = (
            total_billable_amount / total_billable_hours
            if total_billable_hours > 0 else 0
        )

        # Non-billable analysis
        non_billable_tk = self.timekeeping[self.timekeeping['is_billable'] == False]
        non_billable_hours = non_billable_tk['hours'].sum()

        total_hours = self.timekeeping['hours'].sum()
        billable_percentage = (total_billable_hours / total_hours * 100) if total_hours > 0 else 0

        return {
            'total_billable_hours': total_billable_hours,
            'total_billable_amount': total_billable_amount,
            'avg_billing_rate': avg_billing_rate,
            'billable_percentage': billable_percentage,
            'non_billable_hours': non_billable_hours,
            'non_billable_percentage': 100 - billable_percentage
        }

    def generate_ops_dashboard(self) -> Dict:
        """Generate comprehensive ops dashboard"""
        case_volume = self.calculate_case_volume()
        closed_matters, cycle_times = self.calculate_matter_cycle_time()
        staffing = self.calculate_staffing_efficiency()
        process = self.calculate_process_metrics()
        compliance = self.calculate_compliance_metrics()
        billing = self.calculate_billing_efficiency()

        satisfaction = {}
        if self.client_feedback is not None and not self.client_feedback.empty:
            satisfaction = self.calculate_client_satisfaction()

        return {
            'timestamp': datetime.now().isoformat(),
            'case_volume': case_volume,
            'cycle_time': cycle_times,
            'staffing_efficiency': {
                'avg_matters_per_staff': staffing['matters_assigned'].mean(),
                'avg_hours_per_matter': staffing['avg_hours_per_matter'].mean()
            },
            'process_metrics': process,
            'compliance': compliance,
            'billing_efficiency': billing,
            'client_satisfaction': satisfaction
        }

    def identify_bottlenecks(self) -> List[Dict]:
        """Identify operational bottlenecks"""
        bottlenecks = []

        # High cycle time matters
        closed_matters, cycle_times = self.calculate_matter_cycle_time()
        high_cycle = closed_matters[
            closed_matters['cycle_time_days'] > cycle_times['avg_cycle_time_days'] * 1.5
        ]

        if len(high_cycle) > 0:
            bottlenecks.append({
                'type': 'High Cycle Time',
                'severity': 'Medium',
                'count': len(high_cycle),
                'recommendation': 'Review matters with extended timelines'
            })

        # Overdue matters
        overdue = self.matters[self.matters['is_overdue'] == True]
        if len(overdue) > 0:
            bottlenecks.append({
                'type': 'Overdue Matters',
                'severity': 'High',
                'count': len(overdue),
                'recommendation': 'Prioritize overdue matter completion'
            })

        # Low billing efficiency
        billing = self.calculate_billing_efficiency()
        if billing['billable_percentage'] < 70:
            bottlenecks.append({
                'type': 'Low Billable Percentage',
                'severity': 'Medium',
                'billable_percent': billing['billable_percentage'],
                'recommendation': 'Reduce non-billable time allocations'
            })

        return bottlenecks

    def forecast_workload(self, months_ahead: int = 3) -> Dict:
        """Forecast future workload"""
        case_volume = self.calculate_case_volume()
        avg_monthly_volume = case_volume['avg_cases_per_month']

        forecast = {
            'forecast_months': months_ahead,
            'avg_monthly_case_volume': avg_monthly_volume,
            'forecasted_volume': [
                {f'month_{i+1}': int(avg_monthly_volume)} for i in range(months_ahead)
            ],
            'total_forecasted_cases': int(avg_monthly_volume * months_ahead),
            'staffing_recommendation': self._get_staffing_recommendation(avg_monthly_volume)
        }

        return forecast

    @staticmethod
    def _get_staffing_recommendation(monthly_volume: float) -> str:
        """Get staffing recommendation based on volume"""
        if monthly_volume < 5:
            return "Current staffing adequate"
        elif monthly_volume < 10:
            return "Monitor staffing levels"
        elif monthly_volume < 20:
            return "Increase staffing by 1-2 FTE"
        else:
            return "Significant staffing increase required"


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Matters data
    matters = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 101)],
        'matter_status': np.random.choice(['Active', 'Closed'], 100),
        'risk_level': np.random.choice(['Low', 'Medium', 'High', 'Critical'], 100),
        'is_overdue': np.random.choice([True, False], 100, p=[0.15, 0.85]),
        'created_date': pd.date_range('2022-01-01', periods=100, freq='3D')
    })

    # Matters opened/closed
    matters_opened_closed = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 101)],
        'opened_date': pd.date_range('2022-01-01', periods=100, freq='3D'),
        'closed_date': pd.date_range('2023-01-01', periods=100, freq='3D')
    })

    # Timekeeping data
    timekeeping = pd.DataFrame({
        'entry_id': [f'TK{i:06d}' for i in range(1, 501)],
        'matter_id': np.random.choice(matters['matter_id'], 500),
        'staff_id': [f'S{np.random.randint(1, 21):03d}' for _ in range(500)],
        'hours': np.random.uniform(0.5, 8, 500),
        'total_amount': np.random.uniform(500, 5000, 500),
        'is_billable': np.random.choice([True, False], 500, p=[0.75, 0.25]),
        'date': pd.date_range('2023-01-01', periods=500, freq='6H')
    })

    # Client feedback data
    client_feedback = pd.DataFrame({
        'feedback_id': [f'FB{i:06d}' for i in range(1, 51)],
        'satisfaction_score': np.random.randint(1, 11, 50),
        'client_id': [f'C{np.random.randint(1, 21):03d}' for _ in range(50)],
        'feedback_date': pd.date_range('2023-01-01', periods=50, freq='7D')
    })

    return matters, timekeeping, matters_opened_closed, client_feedback


if __name__ == "__main__":
    # Create sample data
    matters_df, timekeeping_df, matters_oc_df, feedback_df = create_sample_data()

    # Initialize metrics
    metrics = LegalOpsMetrics(matters_df, timekeeping_df, matters_oc_df, feedback_df)

    print("=" * 80)
    print("LEGAL OPERATIONS METRICS")
    print("=" * 80)

    print("\n1. CASE VOLUME METRICS")
    print("-" * 80)
    case_vol = metrics.calculate_case_volume()
    print(f"Cases Opened (Last 365 days): {case_vol['cases_opened']}")
    print(f"Cases Closed (Last 365 days): {case_vol['cases_closed']}")
    print(f"Currently Active Cases: {case_vol['cases_active']}")
    print(f"Average Cases per Month: {case_vol['avg_cases_per_month']:.1f}")

    print("\n2. MATTER CYCLE TIME")
    print("-" * 80)
    closed, cycle = metrics.calculate_matter_cycle_time()
    print(f"Average Cycle Time: {cycle['avg_cycle_time_days']:.1f} days")
    print(f"Median Cycle Time: {cycle['median_cycle_time_days']:.1f} days")
    print(f"Min Cycle Time: {cycle['min_cycle_time_days']:.1f} days")
    print(f"Max Cycle Time: {cycle['max_cycle_time_days']:.1f} days")

    print("\n3. STAFFING EFFICIENCY")
    print("-" * 80)
    staffing = metrics.calculate_staffing_efficiency()
    print(f"Total Staff with Assignments: {len(staffing)}")
    print(f"Average Matters per Staff: {staffing['matters_assigned'].mean():.1f}")
    print(f"Average Hours per Matter: {staffing['avg_hours_per_matter'].mean():.1f}")

    print("\n4. CLIENT SATISFACTION")
    print("-" * 80)
    satisfaction = metrics.calculate_client_satisfaction()
    print(f"Average Satisfaction Score: {satisfaction['avg_satisfaction_score']:.1f}/10")
    print(f"NPS Score: {satisfaction['nps_score']:.1f}")
    print(f"Positive Feedback: {satisfaction['positive_feedback_percent']:.1f}%")

    print("\n5. PROCESS METRICS")
    print("-" * 80)
    process = metrics.calculate_process_metrics()
    print(f"Total Hours Logged (30 days): {process['total_hours_logged']:.1f}")
    print(f"Total Entries: {process['total_entries']}")
    print(f"Average Entry Duration: {process['avg_entry_duration']:.2f} hours")
    print(f"Entries per Day: {process['entries_per_day']:.1f}")

    print("\n6. COMPLIANCE METRICS")
    print("-" * 80)
    compliance = metrics.calculate_compliance_metrics()
    print(f"Total Matters: {compliance['total_matters']}")
    print(f"High Risk Matters: {compliance['high_risk_matters']} ({compliance['high_risk_percent']:.1f}%)")
    print(f"On-Time Completion: {compliance['on_time_percent']:.1f}%")
    print(f"Overdue Matters: {compliance['overdue_matters']}")

    print("\n7. BILLING EFFICIENCY")
    print("-" * 80)
    billing = metrics.calculate_billing_efficiency()
    print(f"Total Billable Hours: {billing['total_billable_hours']:.1f}")
    print(f"Total Billable Amount: ${billing['total_billable_amount']:,.2f}")
    print(f"Average Billing Rate: ${billing['avg_billing_rate']:.2f}/hour")
    print(f"Billable Percentage: {billing['billable_percentage']:.1f}%")

    print("\n8. OPERATIONAL BOTTLENECKS")
    print("-" * 80)
    bottlenecks = metrics.identify_bottlenecks()
    if bottlenecks:
        for bn in bottlenecks:
            print(f"  Type: {bn['type']} (Severity: {bn['severity']})")
            print(f"  Recommendation: {bn.get('recommendation', 'N/A')}")
    else:
        print("No significant bottlenecks identified")

    print("\n9. WORKLOAD FORECAST (3 months)")
    print("-" * 80)
    forecast = metrics.forecast_workload(months_ahead=3)
    print(f"Forecasted Monthly Volume: {forecast['avg_monthly_case_volume']:.1f} cases")
    print(f"Total Forecasted Cases: {forecast['total_forecasted_cases']} cases")
    print(f"Staffing Recommendation: {forecast['staffing_recommendation']}")
