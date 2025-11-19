"""
Judge Analytics Module

Provides comprehensive judge and court analytics including:
- Judge decision patterns and tendencies
- Case outcome prediction by judge
- Judge-specific metrics and statistics
- Court scheduling analysis
- Judge assignments and workload
- Historical case outcomes by judge
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


class JudgeAnalytics:
    """Analyze judge behavior and decision patterns"""

    def __init__(self, cases_df: pd.DataFrame, judges_df: pd.DataFrame,
                 judge_decisions_df: pd.DataFrame, court_schedule_df: pd.DataFrame):
        """
        Initialize judge analytics

        Args:
            cases_df: DataFrame with case information
            judges_df: DataFrame with judge information
            judge_decisions_df: DataFrame with judge decisions and outcomes
            court_schedule_df: DataFrame with court schedules and hearings
        """
        self.cases = cases_df
        self.judges = judges_df
        self.judge_decisions = judge_decisions_df
        self.court_schedule = court_schedule_df

    def calculate_judge_statistics(self) -> pd.DataFrame:
        """Calculate comprehensive statistics by judge"""
        judge_stats = self.judge_decisions.groupby('judge_id').agg({
            'case_id': 'count',
            'decision_favorable': lambda x: (x == 'Favorable').sum(),
            'decision_unfavorable': lambda x: (x == 'Unfavorable').sum(),
            'decision_settled': lambda x: (x == 'Settled').sum(),
            'decision_other': lambda x: (x == 'Other').sum(),
            'avg_decision_time_days': 'mean',
            'appeal_rate': 'mean'
        }).reset_index()

        judge_stats.rename(columns={'case_id': 'total_cases'}, inplace=True)

        # Calculate win rates
        judge_stats['favorable_rate'] = (
            judge_stats['decision_favorable'] / judge_stats['total_cases'] * 100
        )

        judge_stats['settlement_rate'] = (
            judge_stats['decision_settled'] / judge_stats['total_cases'] * 100
        )

        judge_stats['unfavorable_rate'] = (
            judge_stats['decision_unfavorable'] / judge_stats['total_cases'] * 100
        )

        # Merge with judge info
        judge_stats = judge_stats.merge(
            self.judges[['judge_id', 'judge_name', 'court', 'experience_years']],
            on='judge_id'
        )

        return judge_stats.sort_values('total_cases', ascending=False)

    def analyze_by_case_type(self, judge_id: str) -> pd.DataFrame:
        """Analyze judge decisions by case type"""
        judge_cases = self.judge_decisions[self.judge_decisions['judge_id'] == judge_id].copy()

        case_analysis = judge_cases.groupby('case_type').agg({
            'case_id': 'count',
            'decision_favorable': lambda x: (x == 'Favorable').sum(),
            'avg_decision_time_days': 'mean'
        }).reset_index()

        case_analysis.rename(columns={'case_id': 'case_count'}, inplace=True)

        case_analysis['favorable_rate'] = (
            case_analysis['decision_favorable'] / case_analysis['case_count'] * 100
        )

        return case_analysis.sort_values('case_count', ascending=False)

    def identify_judge_biases(self) -> pd.DataFrame:
        """Identify potential judge biases or patterns"""
        judge_stats = self.calculate_judge_statistics()

        # Compare favorable rates across judges
        mean_favorable_rate = judge_stats['favorable_rate'].mean()
        std_favorable_rate = judge_stats['favorable_rate'].std()

        # Identify outliers
        judge_stats['favorable_zscore'] = (
            (judge_stats['favorable_rate'] - mean_favorable_rate) / std_favorable_rate
        )

        judge_stats['bias_indicator'] = pd.cut(
            judge_stats['favorable_zscore'],
            bins=[-np.inf, -1, 1, np.inf],
            labels=['Plaintiff-Favorable', 'Neutral', 'Defense-Favorable']
        )

        return judge_stats[['judge_id', 'judge_name', 'favorable_rate', 'bias_indicator',
                           'favorable_zscore']].sort_values('favorable_zscore', ascending=False)

    def calculate_appeal_rates(self) -> pd.DataFrame:
        """Calculate appeal rates by judge"""
        appeal_data = self.judge_decisions.groupby('judge_id').agg({
            'appeal_rate': 'mean',
            'case_id': 'count'
        }).reset_index()

        appeal_data.rename(columns={'case_id': 'total_cases'}, inplace=True)

        appeal_data = appeal_data.merge(
            self.judges[['judge_id', 'judge_name', 'court']],
            on='judge_id'
        )

        appeal_data['appeal_percentage'] = appeal_data['appeal_rate'] * 100

        return appeal_data.sort_values('appeal_percentage', ascending=False)

    def analyze_decision_speed(self) -> pd.DataFrame:
        """Analyze decision speed by judge"""
        speed_analysis = self.judge_decisions.groupby('judge_id').agg({
            'avg_decision_time_days': 'mean',
            'case_id': 'count',
            'decision_time_std': ('avg_decision_time_days', lambda x: np.std(x))
        }).reset_index()

        speed_analysis.rename(columns={'case_id': 'total_cases'}, inplace=True)

        speed_analysis = speed_analysis.merge(
            self.judges[['judge_id', 'judge_name', 'court']],
            on='judge_id'
        )

        # Classify speed
        speed_analysis['decision_speed'] = pd.cut(
            speed_analysis['avg_decision_time_days'],
            bins=[0, 30, 90, 180, np.inf],
            labels=['Very Fast', 'Fast', 'Moderate', 'Slow']
        )

        return speed_analysis.sort_values('avg_decision_time_days').head(20)

    def predict_case_outcome(self, case_type: str, judge_id: str,
                            party_type: str = 'Plaintiff') -> Dict:
        """Predict likely case outcome for specific judge"""
        # Get judge stats for case type
        judge_case_stats = self.analyze_by_case_type(judge_id)

        case_data = judge_case_stats[judge_case_stats['case_type'] == case_type]

        if len(case_data) == 0:
            return {'error': f'No cases for {case_type} with judge {judge_id}'}

        favorable_rate = case_data.iloc[0]['favorable_rate']
        avg_time = case_data.iloc[0]['avg_decision_time_days']

        # Calculate confidence level based on sample size
        sample_size = case_data.iloc[0]['case_count']
        confidence = min(100, (sample_size / 10) * 100)

        return {
            'judge_id': judge_id,
            'case_type': case_type,
            'predicted_favorable_rate': favorable_rate,
            'expected_decision_time_days': avg_time,
            'prediction_confidence': confidence,
            'recommendation': 'Favorable outlook' if favorable_rate > 50 else 'Consider settlement'
        }

    def compare_judges_by_court(self) -> pd.DataFrame:
        """Compare judge performance by court"""
        court_analysis = self.judge_decisions.groupby(['judge_id', 'court']).agg({
            'case_id': 'count',
            'decision_favorable': lambda x: (x == 'Favorable').sum(),
            'avg_decision_time_days': 'mean'
        }).reset_index()

        court_analysis.rename(columns={'case_id': 'case_count'}, inplace=True)

        court_analysis['favorable_rate'] = (
            court_analysis['decision_favorable'] / court_analysis['case_count'] * 100
        )

        return court_analysis.sort_values(['court', 'favorable_rate'], ascending=[True, False])

    def analyze_judge_workload(self) -> pd.DataFrame:
        """Analyze judge workload and scheduling"""
        judge_workload = self.court_schedule.groupby('judge_id').agg({
            'hearing_id': 'count',
            'hearing_duration_hours': 'sum'
        }).reset_index()

        judge_workload.rename(columns={
            'hearing_id': 'total_hearings',
            'hearing_duration_hours': 'total_hours'
        }, inplace=True)

        judge_workload['avg_hours_per_hearing'] = (
            judge_workload['total_hours'] / judge_workload['total_hearings']
        )

        judge_workload = judge_workload.merge(
            self.judges[['judge_id', 'judge_name', 'court']],
            on='judge_id'
        )

        return judge_workload.sort_values('total_hearings', ascending=False)

    def identify_favorable_judges(self, case_type: str, min_cases: int = 10) -> pd.DataFrame:
        """Identify judges most favorable for specific case type"""
        # Filter to specific case type
        case_judges = self.judge_decisions[
            self.judge_decisions['case_type'] == case_type
        ]

        favorable_judges = case_judges.groupby('judge_id').agg({
            'case_id': 'count',
            'decision_favorable': lambda x: (x == 'Favorable').sum()
        }).reset_index()

        favorable_judges.rename(columns={'case_id': 'case_count'}, inplace=True)

        # Filter by minimum cases
        favorable_judges = favorable_judges[favorable_judges['case_count'] >= min_cases]

        favorable_judges['favorable_rate'] = (
            favorable_judges['decision_favorable'] / favorable_judges['case_count'] * 100
        )

        favorable_judges = favorable_judges.merge(
            self.judges[['judge_id', 'judge_name', 'court']],
            on='judge_id'
        )

        return favorable_judges.sort_values('favorable_rate', ascending=False)


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Judges data
    judges = pd.DataFrame({
        'judge_id': [f'J{i:03d}' for i in range(1, 21)],
        'judge_name': [f'Judge {i}' for i in range(1, 21)],
        'court': np.random.choice(['US District Court', 'State Supreme Court', 'Appellate Court'], 20),
        'experience_years': np.random.randint(5, 30, 20)
    })

    # Cases data
    cases = pd.DataFrame({
        'case_id': [f'C{i:06d}' for i in range(1, 501)],
        'judge_id': np.random.choice(judges['judge_id'], 500),
        'case_type': np.random.choice(['Civil', 'Criminal', 'IP', 'Employment'], 500),
        'filed_date': pd.date_range('2020-01-01', periods=500, freq='3D')
    })

    # Judge decisions data
    judge_decisions = pd.DataFrame({
        'decision_id': [f'D{i:06d}' for i in range(1, 1001)],
        'judge_id': np.random.choice(judges['judge_id'], 1000),
        'case_id': np.random.choice(cases['case_id'], 1000),
        'case_type': np.random.choice(['Civil', 'Criminal', 'IP', 'Employment'], 1000),
        'decision_favorable': np.random.choice(['Favorable', 'Unfavorable', 'Settled', 'Other'], 1000),
        'avg_decision_time_days': np.random.randint(15, 180, 1000),
        'appeal_rate': np.random.uniform(0, 0.3, 1000)
    })

    # Court schedule data
    court_schedule = pd.DataFrame({
        'hearing_id': [f'H{i:06d}' for i in range(1, 501)],
        'judge_id': np.random.choice(judges['judge_id'], 500),
        'hearing_duration_hours': np.random.uniform(1, 8, 500),
        'hearing_date': pd.date_range('2023-01-01', periods=500, freq='D')
    })

    return cases, judges, judge_decisions, court_schedule


if __name__ == "__main__":
    # Create sample data
    cases_df, judges_df, judge_decisions_df, court_schedule_df = create_sample_data()

    # Initialize analytics
    analytics = JudgeAnalytics(cases_df, judges_df, judge_decisions_df, court_schedule_df)

    # Calculate metrics
    print("=" * 80)
    print("JUDGE ANALYTICS")
    print("=" * 80)

    print("\n1. JUDGE STATISTICS AND PERFORMANCE")
    print("-" * 80)
    judge_stats = analytics.calculate_judge_statistics()
    print(judge_stats[['judge_name', 'court', 'total_cases', 'favorable_rate',
                       'settlement_rate', 'avg_decision_time_days']].head(10).to_string(index=False))

    print("\n2. JUDGE BIAS ANALYSIS")
    print("-" * 80)
    biases = analytics.identify_judge_biases()
    print(biases.to_string(index=False))

    print("\n3. APPEAL RATES BY JUDGE")
    print("-" * 80)
    appeals = analytics.calculate_appeal_rates()
    print(appeals.head(10).to_string(index=False))

    print("\n4. DECISION SPEED ANALYSIS")
    print("-" * 80)
    speed = analytics.analyze_decision_speed()
    print(speed.to_string(index=False))

    print("\n5. JUDGES BY COURT COMPARISON")
    print("-" * 80)
    court_comparison = analytics.compare_judges_by_court()
    print(court_comparison.head(10).to_string(index=False))

    print("\n6. JUDGE WORKLOAD AND SCHEDULING")
    print("-" * 80)
    workload = analytics.analyze_judge_workload()
    print(workload.head(10).to_string(index=False))

    print("\n7. FAVORABLE JUDGES FOR CASE TYPE 'Civil'")
    print("-" * 80)
    favorable = analytics.identify_favorable_judges('Civil', min_cases=5)
    print(favorable.to_string(index=False))

    print("\n8. CASE OUTCOME PREDICTION SAMPLE")
    print("-" * 80)
    prediction = analytics.predict_case_outcome('Civil', 'J001')
    print(f"Predicted favorable rate: {prediction['predicted_favorable_rate']:.2f}%")
    print(f"Expected decision time: {prediction['expected_decision_time_days']:.1f} days")
    print(f"Recommendation: {prediction['recommendation']}")
