"""
Opposing Counsel Analysis Module

Provides comprehensive opposing counsel analytics including:
- Opposing counsel profile and history
- Settlement patterns and tendencies
- Win/loss analysis against specific counsel
- Negotiation style analysis
- Opposing counsel reputation scoring
- Historical case outcomes by opponent
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class OpposingCounselAnalytics:
    """Analyze opposing counsel patterns and behavior"""

    def __init__(self, cases_df: pd.DataFrame, counsel_df: pd.DataFrame,
                 settlement_df: pd.DataFrame, litigation_history_df: pd.DataFrame):
        """
        Initialize opposing counsel analytics

        Args:
            cases_df: DataFrame with case information
            counsel_df: DataFrame with counsel information
            settlement_df: DataFrame with settlement data
            litigation_history_df: DataFrame with litigation history
        """
        self.cases = cases_df
        self.counsel = counsel_df
        self.settlements = settlement_df
        self.litigation_history = litigation_history_df

    def calculate_counsel_statistics(self) -> pd.DataFrame:
        """Calculate comprehensive statistics by opposing counsel"""
        counsel_stats = self.litigation_history.groupby('opposing_counsel_id').agg({
            'case_id': 'count',
            'our_outcome_favorable': lambda x: (x == 'Favorable').sum(),
            'our_outcome_unfavorable': lambda x: (x == 'Unfavorable').sum(),
            'settlement_reached': lambda x: (x == 1).sum(),
            'settlement_amount': 'mean',
            'litigation_duration_days': 'mean'
        }).reset_index()

        counsel_stats.rename(columns={'case_id': 'total_cases'}, inplace=True)

        # Calculate win rates
        counsel_stats['win_rate'] = (
            counsel_stats['our_outcome_favorable'] / counsel_stats['total_cases'] * 100
        )

        counsel_stats['settlement_rate'] = (
            counsel_stats['settlement_reached'] / counsel_stats['total_cases'] * 100
        )

        counsel_stats['loss_rate'] = (
            counsel_stats['our_outcome_unfavorable'] / counsel_stats['total_cases'] * 100
        )

        # Merge with counsel info
        counsel_stats = counsel_stats.merge(
            self.counsel[['counsel_id', 'counsel_name', 'firm', 'practice_area']],
            left_on='opposing_counsel_id',
            right_on='counsel_id'
        )

        return counsel_stats.sort_values('total_cases', ascending=False)

    def analyze_by_case_type(self, opposing_counsel_id: str) -> pd.DataFrame:
        """Analyze outcomes against opposing counsel by case type"""
        counsel_cases = self.litigation_history[
            self.litigation_history['opposing_counsel_id'] == opposing_counsel_id
        ].copy()

        case_analysis = counsel_cases.groupby('case_type').agg({
            'case_id': 'count',
            'our_outcome_favorable': lambda x: (x == 'Favorable').sum(),
            'settlement_amount': 'mean'
        }).reset_index()

        case_analysis.rename(columns={'case_id': 'case_count'}, inplace=True)

        case_analysis['win_rate'] = (
            case_analysis['our_outcome_favorable'] / case_analysis['case_count'] * 100
        )

        return case_analysis.sort_values('case_count', ascending=False)

    def calculate_settlement_tendencies(self) -> pd.DataFrame:
        """Calculate settlement tendencies by opposing counsel"""
        settlement_data = self.litigation_history.groupby('opposing_counsel_id').agg({
            'settlement_reached': lambda x: (x == 1).sum(),
            'case_id': 'count',
            'settlement_amount': 'mean',
            'settlement_timeline_days': 'mean'
        }).reset_index()

        settlement_data.rename(columns={'case_id': 'total_cases'}, inplace=True)

        settlement_data['settlement_rate'] = (
            settlement_data['settlement_reached'] / settlement_data['total_cases'] * 100
        )

        # Classify settlement style
        settlement_data['settlement_style'] = pd.cut(
            settlement_data['settlement_rate'],
            bins=[0, 25, 50, 75, 100],
            labels=['Litigious', 'Moderate', 'Settlement-Prone', 'Aggressive Settler']
        )

        settlement_data = settlement_data.merge(
            self.counsel[['counsel_id', 'counsel_name', 'firm']],
            left_on='opposing_counsel_id',
            right_on='counsel_id'
        )

        return settlement_data.sort_values('settlement_rate', ascending=False)

    def identify_settlement_negotiators(self) -> pd.DataFrame:
        """Identify most effective settlement negotiators"""
        negotiators = self.settlements.groupby('opposing_counsel_id').agg({
            'settlement_id': 'count',
            'settlement_amount': ['mean', 'median', 'std'],
            'days_to_settlement': 'mean'
        }).reset_index()

        negotiators.columns = ['opposing_counsel_id', 'settlement_count', 'avg_settlement',
                              'median_settlement', 'settlement_std', 'avg_settlement_days']

        negotiators = negotiators.merge(
            self.counsel[['counsel_id', 'counsel_name', 'firm', 'practice_area']],
            left_on='opposing_counsel_id',
            right_on='counsel_id'
        )

        negotiators['negotiation_style'] = np.where(
            negotiators['avg_settlement_days'] < 60,
            'Quick Negotiator',
            'Lengthy Negotiator'
        )

        return negotiators.sort_values('settlement_count', ascending=False)

    def calculate_counsel_reputation_score(self) -> pd.DataFrame:
        """Calculate overall reputation score for opposing counsel"""
        counsel_stats = self.calculate_counsel_statistics()

        # Calculate reputation components
        counsel_stats['win_score'] = counsel_stats['win_rate']
        counsel_stats['settlement_score'] = counsel_stats['settlement_rate']

        # Calculate overall score
        counsel_stats['reputation_score'] = (
            (counsel_stats['win_score'] * 0.4) +
            (counsel_stats['settlement_score'] * 0.3) +
            (min(counsel_stats['total_cases'] / 10, 100) * 0.3)
        )

        # Classify reputation
        counsel_stats['reputation_level'] = pd.cut(
            counsel_stats['reputation_score'],
            bins=[0, 30, 50, 70, 100],
            labels=['Weak', 'Moderate', 'Strong', 'Elite']
        )

        return counsel_stats[['counsel_name', 'firm', 'practice_area', 'total_cases',
                             'win_rate', 'settlement_rate', 'reputation_score',
                             'reputation_level']].sort_values('reputation_score', ascending=False)

    def identify_tough_opponents(self, min_cases: int = 5) -> pd.DataFrame:
        """Identify most challenging opposing counsel"""
        counsel_stats = self.calculate_counsel_statistics()

        # Filter by minimum cases
        tough = counsel_stats[counsel_stats['total_cases'] >= min_cases].copy()

        # Calculate toughness score
        tough['toughness_score'] = tough['loss_rate'] - tough['win_rate']

        tough = tough[['counsel_name', 'firm', 'practice_area', 'total_cases',
                      'win_rate', 'loss_rate', 'toughness_score']].sort_values(
            'toughness_score', ascending=False
        )

        return tough

    def compare_counsel_head_to_head(self, counsel_id_1: str, counsel_id_2: str) -> Dict:
        """Compare two opposing counsel head-to-head"""
        counsel_1_data = self.litigation_history[
            self.litigation_history['opposing_counsel_id'] == counsel_id_1
        ]

        counsel_2_data = self.litigation_history[
            self.litigation_history['opposing_counsel_id'] == counsel_id_2
        ]

        comparison = {
            'counsel_1_id': counsel_id_1,
            'counsel_2_id': counsel_id_2,
            'counsel_1': {
                'total_cases': len(counsel_1_data),
                'win_rate': (counsel_1_data['our_outcome_favorable'] == 'Favorable').sum() / len(counsel_1_data) * 100,
                'avg_settlement': counsel_1_data['settlement_amount'].mean(),
                'settlement_rate': (counsel_1_data['settlement_reached'] == 1).sum() / len(counsel_1_data) * 100
            },
            'counsel_2': {
                'total_cases': len(counsel_2_data),
                'win_rate': (counsel_2_data['our_outcome_favorable'] == 'Favorable').sum() / len(counsel_2_data) * 100,
                'avg_settlement': counsel_2_data['settlement_amount'].mean(),
                'settlement_rate': (counsel_2_data['settlement_reached'] == 1).sum() / len(counsel_2_data) * 100
            }
        }

        return comparison

    def analyze_negotiation_patterns(self) -> pd.DataFrame:
        """Analyze negotiation patterns by opposing counsel"""
        negotiation_patterns = self.settlements.groupby('opposing_counsel_id').agg({
            'settlement_amount': ['mean', 'median', 'min', 'max'],
            'days_to_settlement': 'mean',
            'settlement_id': 'count',
            'final_demand_adjustment': 'mean'
        }).reset_index()

        negotiation_patterns.columns = ['opposing_counsel_id', 'avg_settlement', 'median_settlement',
                                       'min_settlement', 'max_settlement', 'avg_days_to_settle',
                                       'total_settlements', 'avg_demand_adjustment']

        negotiation_patterns['settlement_range'] = (
            negotiation_patterns['max_settlement'] - negotiation_patterns['min_settlement']
        )

        negotiation_patterns['flexibility'] = np.where(
            negotiation_patterns['avg_demand_adjustment'] > 0.2,
            'Very Flexible',
            'Rigid'
        )

        negotiation_patterns = negotiation_patterns.merge(
            self.counsel[['counsel_id', 'counsel_name', 'firm']],
            left_on='opposing_counsel_id',
            right_on='counsel_id'
        )

        return negotiation_patterns.sort_values('total_settlements', ascending=False)

    def identify_favorable_opponents(self) -> pd.DataFrame:
        """Identify opponents we win against most often"""
        counsel_stats = self.calculate_counsel_statistics()

        favorable = counsel_stats[
            counsel_stats['total_cases'] >= 3
        ][['counsel_name', 'firm', 'practice_area', 'total_cases',
           'win_rate', 'settlement_rate']].sort_values('win_rate', ascending=False).head(20)

        return favorable


def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration"""
    np.random.seed(42)

    # Counsel data
    counsel = pd.DataFrame({
        'counsel_id': [f'OC{i:03d}' for i in range(1, 31)],
        'counsel_name': [f'Counsel {i}' for i in range(1, 31)],
        'firm': [f'Firm {np.random.randint(1, 16)}' for _ in range(30)],
        'practice_area': np.random.choice(['Civil', 'IP', 'Employment', 'Corporate'], 30),
        'experience_years': np.random.randint(5, 30, 30)
    })

    # Cases data
    cases = pd.DataFrame({
        'case_id': [f'C{i:06d}' for i in range(1, 501)],
        'case_type': np.random.choice(['Civil', 'IP', 'Employment', 'Corporate'], 500)
    })

    # Settlement data
    settlements = pd.DataFrame({
        'settlement_id': [f'S{i:06d}' for i in range(1, 201)],
        'opposing_counsel_id': np.random.choice(counsel['counsel_id'], 200),
        'settlement_amount': np.random.uniform(10000, 500000, 200),
        'days_to_settlement': np.random.randint(10, 180, 200),
        'final_demand_adjustment': np.random.uniform(0, 0.5, 200)
    })

    # Litigation history data
    litigation_history = pd.DataFrame({
        'case_id': np.random.choice(cases['case_id'], 600),
        'opposing_counsel_id': np.random.choice(counsel['counsel_id'], 600),
        'case_type': np.random.choice(['Civil', 'IP', 'Employment', 'Corporate'], 600),
        'our_outcome_favorable': np.random.choice(['Favorable', 'Unfavorable', 'Neutral'], 600),
        'settlement_reached': np.random.choice([0, 1], 600, p=[0.4, 0.6]),
        'settlement_amount': np.random.uniform(10000, 500000, 600),
        'settlement_timeline_days': np.random.randint(10, 200, 600),
        'litigation_duration_days': np.random.randint(30, 720, 600)
    })

    return cases, counsel, settlements, litigation_history


if __name__ == "__main__":
    # Create sample data
    cases_df, counsel_df, settlements_df, litigation_history_df = create_sample_data()

    # Initialize analytics
    analytics = OpposingCounselAnalytics(cases_df, counsel_df, settlements_df, litigation_history_df)

    # Calculate metrics
    print("=" * 80)
    print("OPPOSING COUNSEL ANALYTICS")
    print("=" * 80)

    print("\n1. OPPOSING COUNSEL STATISTICS")
    print("-" * 80)
    counsel_stats = analytics.calculate_counsel_statistics()
    print(counsel_stats[['counsel_name', 'firm', 'practice_area', 'total_cases',
                        'win_rate', 'settlement_rate']].head(10).to_string(index=False))

    print("\n2. COUNSEL REPUTATION SCORES")
    print("-" * 80)
    reputation = analytics.calculate_counsel_reputation_score()
    print(reputation.head(10).to_string(index=False))

    print("\n3. SETTLEMENT TENDENCIES")
    print("-" * 80)
    settlement_tendencies = analytics.calculate_settlement_tendencies()
    print(settlement_tendencies[['counsel_name', 'firm', 'total_cases',
                                 'settlement_rate', 'settlement_style']].head(10).to_string(index=False))

    print("\n4. TOUGH OPPONENTS (We lose most against)")
    print("-" * 80)
    tough = analytics.identify_tough_opponents()
    print(tough.to_string(index=False))

    print("\n5. SETTLEMENT NEGOTIATORS")
    print("-" * 80)
    negotiators = analytics.identify_settlement_negotiators()
    print(negotiators[['counsel_name', 'firm', 'settlement_count',
                       'avg_settlement', 'negotiation_style']].head(10).to_string(index=False))

    print("\n6. NEGOTIATION PATTERNS")
    print("-" * 80)
    patterns = analytics.analyze_negotiation_patterns()
    print(patterns[['counsel_name', 'firm', 'avg_settlement', 'avg_days_to_settle',
                    'flexibility']].head(10).to_string(index=False))

    print("\n7. FAVORABLE OPPONENTS (We win most against)")
    print("-" * 80)
    favorable = analytics.identify_favorable_opponents()
    print(favorable.to_string(index=False))
