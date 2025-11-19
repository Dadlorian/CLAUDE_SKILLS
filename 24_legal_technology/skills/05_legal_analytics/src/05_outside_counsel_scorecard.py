"""
Outside Counsel Scorecard Module
Evaluates and scores outside law firms on multiple performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class OutsideCounselScorecard:
    """Evaluates outside counsel performance against defined metrics."""

    def __init__(self):
        """Initialize scorecard."""
        self.firm_data = None
        self.scorecard = None

    def generate_firm_performance_data(self, num_matters: int = 300) -> pd.DataFrame:
        """Generate outside counsel performance data."""
        np.random.seed(42)

        firms = ['White & Case', 'Simpson Thacher', 'Skadden Arps', 'Davis Polk', 'Sullivan Cromwell']
        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor']

        data = {
            'matter_id': [f'MAT-{i:05d}' for i in range(num_matters)],
            'law_firm': np.random.choice(firms, num_matters),
            'practice_area': np.random.choice(practice_areas, num_matters),
            'matter_cost': np.random.uniform(10000, 500000, num_matters),
            'matter_budget': np.random.uniform(20000, 600000, num_matters),
            'budget_variance_pct': None,
            'matter_duration_months': np.random.randint(1, 24, num_matters),
            'client_satisfaction_score': np.random.randint(1, 10, num_matters),
            'on_time_delivery': np.random.choice([0, 1], num_matters, p=[0.2, 0.8]),
            'quality_issues_count': np.random.randint(0, 5, num_matters),
            'reusable_work_product': np.random.choice([0, 1], num_matters, p=[0.4, 0.6]),
            'discovery_disputes': np.random.randint(0, 3, num_matters),
            'associate_utilization_pct': np.random.uniform(0.3, 1.0, num_matters),
            'innovation_initiatives': np.random.randint(0, 5, num_matters),
            'communication_rating': np.random.randint(1, 10, num_matters),
        }

        df = pd.DataFrame(data)
        df['budget_variance_pct'] = ((df['matter_cost'] - df['matter_budget']) / df['matter_budget'] * 100)

        self.firm_data = df
        return df

    def calculate_firm_scores(self) -> pd.DataFrame:
        """Calculate composite scores for each firm."""
        firm_metrics = self.firm_data.groupby('law_firm').agg({
            'matter_cost': 'mean',
            'matter_budget': 'mean',
            'budget_variance_pct': 'mean',
            'client_satisfaction_score': 'mean',
            'on_time_delivery': 'mean',
            'quality_issues_count': 'mean',
            'reusable_work_product': 'mean',
            'discovery_disputes': 'mean',
            'associate_utilization_pct': 'mean',
            'innovation_initiatives': 'mean',
            'communication_rating': 'mean',
            'matter_id': 'count'
        }).round(2)

        firm_metrics.columns = ['avg_cost', 'avg_budget', 'avg_budget_var', 'satisfaction',
                               'on_time_pct', 'quality_issues', 'reusable_product_pct',
                               'discovery_disputes', 'utilization_pct', 'innovation_count',
                               'communication', 'num_matters']

        # Calculate weighted scores (0-100)
        firm_metrics['cost_efficiency_score'] = ((100 - abs(firm_metrics['avg_budget_var']) / 10).clip(0, 100))
        firm_metrics['quality_score'] = ((100 - (firm_metrics['quality_issues'] * 10)).clip(0, 100))
        firm_metrics['delivery_score'] = (firm_metrics['on_time_pct'] * 100)
        firm_metrics['satisfaction_score'] = (firm_metrics['satisfaction'] * 10)
        firm_metrics['innovation_score'] = (firm_metrics['innovation_count'] * 20).clip(0, 100)
        firm_metrics['communication_score'] = (firm_metrics['communication'] * 10)

        # Composite score
        firm_metrics['composite_score'] = (
            firm_metrics['cost_efficiency_score'] * 0.25 +
            firm_metrics['quality_score'] * 0.25 +
            firm_metrics['delivery_score'] * 0.2 +
            firm_metrics['satisfaction_score'] * 0.15 +
            firm_metrics['innovation_score'] * 0.1 +
            firm_metrics['communication_score'] * 0.05
        ).round(2)

        self.scorecard = firm_metrics

        return firm_metrics.sort_values('composite_score', ascending=False)

    def cost_efficiency_analysis(self) -> pd.DataFrame:
        """Analyze cost efficiency by firm."""
        efficiency = self.firm_data.groupby('law_firm').agg({
            'matter_cost': 'mean',
            'matter_budget': 'mean',
            'budget_variance_pct': ['mean', 'std'],
            'matter_id': 'count'
        }).round(2)

        efficiency.columns = ['avg_cost', 'avg_budget', 'avg_variance', 'variance_std', 'matters']
        efficiency['cost_overrun_rate'] = (self.firm_data[self.firm_data['budget_variance_pct'] > 0].groupby('law_firm').size() /
                                          self.firm_data.groupby('law_firm').size() * 100).round(2)
        efficiency['avg_overrun_amount'] = (self.firm_data[self.firm_data['budget_variance_pct'] > 0].groupby('law_firm')['budget_variance_pct'].mean() * self.firm_data.groupby('law_firm')['matter_budget'].mean() / 100).round(0)

        return efficiency.sort_values('avg_variance')

    def quality_performance(self) -> pd.DataFrame:
        """Analyze quality metrics by firm."""
        quality = self.firm_data.groupby('law_firm').agg({
            'quality_issues_count': 'mean',
            'reusable_work_product': 'mean',
            'discovery_disputes': 'mean',
            'client_satisfaction_score': 'mean',
            'communication_rating': 'mean',
            'matter_id': 'count'
        }).round(2)

        quality.columns = ['avg_quality_issues', 'reusable_product_pct', 'avg_disputes',
                          'satisfaction', 'communication', 'num_matters']

        return quality.sort_values('satisfaction', ascending=False)

    def practice_area_performance(self) -> pd.DataFrame:
        """Analyze performance by practice area and firm."""
        performance = self.firm_data.groupby(['law_firm', 'practice_area']).agg({
            'budget_variance_pct': 'mean',
            'client_satisfaction_score': 'mean',
            'on_time_delivery': 'mean',
            'quality_issues_count': 'mean',
            'matter_id': 'count'
        }).round(2)

        performance.columns = ['budget_variance', 'satisfaction', 'on_time_rate',
                              'quality_issues', 'num_matters']

        return performance

    def generate_scorecard_report(self) -> Dict:
        """Generate comprehensive scorecard report."""
        if self.scorecard is None:
            self.calculate_firm_scores()

        report = {
            'top_performer': self.scorecard.index[0],
            'top_score': self.scorecard['composite_score'].iloc[0],
            'average_score': self.scorecard['composite_score'].mean(),
            'lowest_performer': self.scorecard.index[-1],
            'lowest_score': self.scorecard['composite_score'].iloc[-1],
            'score_range': self.scorecard['composite_score'].max() - self.scorecard['composite_score'].min(),
            'firms_evaluated': len(self.scorecard)
        }

        return report

    def generate_recommendations(self) -> Dict:
        """Generate recommendations based on performance."""
        if self.scorecard is None:
            self.calculate_firm_scores()

        recommendations = {}

        for firm in self.scorecard.index:
            firm_data = self.scorecard.loc[firm]
            score = firm_data['composite_score']

            if score >= 80:
                recommendation = 'MAINTAIN - Strong performance across all metrics'
            elif score >= 65:
                recommendation = 'MONITOR - Address specific performance gaps'
            elif score >= 50:
                recommendation = 'IMPROVE - Develop performance improvement plan'
            else:
                recommendation = 'REVIEW - Consider relationship alternatives'

            recommendations[firm] = {
                'score': score,
                'recommendation': recommendation,
                'priority_areas': []
            }

            # Identify priority areas
            if firm_data['cost_efficiency_score'] < 70:
                recommendations[firm]['priority_areas'].append('Cost Control')
            if firm_data['quality_score'] < 70:
                recommendations[firm]['priority_areas'].append('Quality Improvement')
            if firm_data['delivery_score'] < 70:
                recommendations[firm]['priority_areas'].append('On-Time Delivery')
            if firm_data['satisfaction_score'] < 70:
                recommendations[firm]['priority_areas'].append('Client Communication')

        return recommendations

    def export_scorecard(self, output_dir: str = './') -> None:
        """Export scorecard to files."""
        self.calculate_firm_scores().to_csv(f'{output_dir}firm_scorecard.csv')
        self.cost_efficiency_analysis().to_csv(f'{output_dir}cost_efficiency.csv')
        self.quality_performance().to_csv(f'{output_dir}quality_performance.csv')

        print(f"Scorecard exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    scorecard = OutsideCounselScorecard()

    print("Generating firm performance data...")
    scorecard.generate_firm_performance_data(300)

    print("\n=== OUTSIDE COUNSEL SCORECARD ===")
    print(scorecard.calculate_firm_scores())

    print("\n=== SCORECARD SUMMARY ===")
    summary = scorecard.generate_scorecard_report()
    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\n=== RECOMMENDATIONS ===")
    recommendations = scorecard.generate_recommendations()
    for firm, rec in recommendations.items():
        print(f"\n{firm}: {rec['recommendation']} (Score: {rec['score']:.2f})")
        if rec['priority_areas']:
            print(f"  Priority areas: {', '.join(rec['priority_areas'])}")
