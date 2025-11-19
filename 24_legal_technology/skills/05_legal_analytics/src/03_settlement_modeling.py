"""
Settlement Modeling Module
Analyzes settlement data and provides negotiation analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from typing import Dict, List, Tuple


class SettlementAnalyzer:
    """Analyzes settlement negotiations and outcomes."""

    def __init__(self):
        """Initialize settlement analyzer."""
        self.settlements = None
        self.negotiations = None

    def generate_settlement_data(self, num_settlements: int = 200) -> pd.DataFrame:
        """Generate historical settlement data."""
        np.random.seed(42)

        claim_types = ['Product Liability', 'Employment', 'Contract', 'IP Infringement', 'Auto']
        outcomes = ['Settled', 'Withdrawn', 'Pending', 'Trial']

        data = {
            'settlement_id': [f'SETTLE-{i:05d}' for i in range(num_settlements)],
            'claim_type': np.random.choice(claim_types, num_settlements),
            'original_claim_amount': np.random.uniform(50000, 5000000, num_settlements),
            'initial_offer': np.random.uniform(20000, 3000000, num_settlements),
            'final_settlement_amount': None,
            'defense_cost': np.random.uniform(10000, 200000, num_settlements),
            'claim_reserve': np.random.uniform(30000, 3500000, num_settlements),
            'negotiation_duration_months': np.random.randint(1, 60, num_settlements),
            'num_settlement_conferences': np.random.randint(1, 10, num_settlements),
            'mediator_involved': np.random.choice([0, 1], num_settlements),
            'expert_witnesses': np.random.randint(0, 5, num_settlements),
            'settlement_date': [datetime.now() - timedelta(days=np.random.randint(0, 730)) for _ in range(num_settlements)],
            'outcome': np.random.choice(outcomes, num_settlements)
        }

        df = pd.DataFrame(data)

        # Calculate settlement amounts
        df['final_settlement_amount'] = df.apply(
            lambda row: row['original_claim_amount'] * np.random.uniform(0.3, 0.9) if row['outcome'] == 'Settled' else np.nan,
            axis=1
        )

        self.settlements = df
        return df

    def settlement_success_rate(self) -> Dict:
        """Calculate settlement success metrics."""
        settled = (self.settlements['outcome'] == 'Settled').sum()
        total = len(self.settlements)

        metrics = {
            'settlement_rate': settled / total,
            'total_settlements': settled,
            'total_cases': total,
            'average_duration_months': self.settlements['negotiation_duration_months'].mean(),
            'median_duration_months': self.settlements['negotiation_duration_months'].median()
        }

        return metrics

    def recovery_analysis(self) -> pd.DataFrame:
        """Analyze settlement recovery rates by claim type."""
        settled = self.settlements[self.settlements['outcome'] == 'Settled'].copy()

        recovery = settled.groupby('claim_type').agg({
            'original_claim_amount': 'mean',
            'final_settlement_amount': 'mean',
            'defense_cost': 'mean',
            'negotiation_duration_months': 'mean',
            'settlement_id': 'count'
        }).round(0)

        recovery.columns = ['avg_claim', 'avg_settlement', 'avg_defense_cost', 'avg_duration_months', 'count']
        recovery['recovery_rate'] = (recovery['avg_settlement'] / recovery['avg_claim'] * 100).round(2)
        recovery['net_recovery'] = (recovery['avg_settlement'] - recovery['avg_defense_cost']).round(0)

        return recovery.sort_values('recovery_rate', ascending=False)

    def negotiation_efficiency(self) -> pd.DataFrame:
        """Analyze settlement negotiation efficiency."""
        settled = self.settlements[self.settlements['outcome'] == 'Settled'].copy()

        efficiency = settled.groupby('claim_type').agg({
            'num_settlement_conferences': 'mean',
            'mediator_involved': 'mean',
            'expert_witnesses': 'mean',
            'negotiation_duration_months': 'mean',
            'final_settlement_amount': 'mean'
        }).round(2)

        efficiency.columns = ['avg_conferences', 'mediator_rate', 'avg_experts', 'avg_duration', 'avg_settlement']
        efficiency['efficiency_score'] = (100 - (efficiency['avg_duration'] * 2) - (efficiency['avg_experts'] * 5)).round(2)

        return efficiency

    def settlement_variance_analysis(self) -> Dict:
        """Analyze variance between claim and settlement amounts."""
        settled = self.settlements[self.settlements['outcome'] == 'Settled'].copy()

        settled['variance_pct'] = ((settled['final_settlement_amount'] - settled['original_claim_amount']) /
                                  settled['original_claim_amount'] * 100)

        analysis = {
            'mean_variance_pct': settled['variance_pct'].mean(),
            'median_variance_pct': settled['variance_pct'].median(),
            'std_deviation': settled['variance_pct'].std(),
            'min_variance_pct': settled['variance_pct'].min(),
            'max_variance_pct': settled['variance_pct'].max(),
            'high_variance_cases': (settled['variance_pct'].abs() > 50).sum()
        }

        return analysis

    def claim_type_performance(self) -> pd.DataFrame:
        """Analyze settlement performance by claim type."""
        settled = self.settlements[self.settlements['outcome'] == 'Settled'].copy()

        performance = settled.groupby('claim_type').agg({
            'settlement_id': 'count',
            'original_claim_amount': ['mean', 'sum'],
            'final_settlement_amount': ['mean', 'sum'],
            'defense_cost': 'sum',
            'negotiation_duration_months': ['mean', 'min', 'max']
        }).round(0)

        performance.columns = ['cases', 'avg_claim', 'total_claim', 'avg_settlement', 'total_settlement',
                              'total_defense_cost', 'avg_duration', 'min_duration', 'max_duration']

        performance['net_value'] = (performance['total_settlement'] - performance['total_defense_cost']).round(0)

        return performance

    def predictive_settlement_analysis(self) -> Dict:
        """Identify factors correlating with favorable settlements."""
        settled = self.settlements[self.settlements['outcome'] == 'Settled'].copy()

        settled['favorable_settlement'] = settled['final_settlement_amount'] > settled['original_claim_amount'] * 0.5

        correlation_factors = {
            'mediator_improvement': (settled[settled['mediator_involved'] == 1]['favorable_settlement'].mean() -
                                    settled[settled['mediator_involved'] == 0]['favorable_settlement'].mean()),
            'short_negotiation_success': settled[settled['negotiation_duration_months'] <= 6]['favorable_settlement'].mean(),
            'long_negotiation_success': settled[settled['negotiation_duration_months'] > 6]['favorable_settlement'].mean(),
            'expert_witness_impact': stats.pointbiserialr(settled['expert_witnesses'], settled['favorable_settlement'])[0]
        }

        return correlation_factors

    def export_report(self, output_dir: str = './') -> None:
        """Export settlement analysis to files."""
        recovery = self.recovery_analysis()
        recovery.to_csv(f'{output_dir}recovery_analysis.csv')

        efficiency = self.negotiation_efficiency()
        efficiency.to_csv(f'{output_dir}negotiation_efficiency.csv')

        performance = self.claim_type_performance()
        performance.to_csv(f'{output_dir}claim_type_performance.csv')

        print(f"Settlement analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    analyzer = SettlementAnalyzer()

    print("Generating settlement data...")
    analyzer.generate_settlement_data(200)

    print("\n=== SETTLEMENT SUCCESS RATES ===")
    print(analyzer.settlement_success_rate())

    print("\n=== RECOVERY ANALYSIS BY CLAIM TYPE ===")
    print(analyzer.recovery_analysis())

    print("\n=== NEGOTIATION EFFICIENCY ===")
    print(analyzer.negotiation_efficiency())

    print("\n=== SETTLEMENT VARIANCE ANALYSIS ===")
    variance = analyzer.settlement_variance_analysis()
    for key, value in variance.items():
        print(f"{key}: {value:.2f}%")

    print("\n=== PREDICTIVE FACTORS ===")
    factors = analyzer.predictive_settlement_analysis()
    for key, value in factors.items():
        print(f"{key}: {value:.4f}")
