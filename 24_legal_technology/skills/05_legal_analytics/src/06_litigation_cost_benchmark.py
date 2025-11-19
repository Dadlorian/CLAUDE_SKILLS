"""
Litigation Cost Benchmarking Module
Benchmarks litigation costs against industry standards
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class LitigationBenchmark:
    """Benchmarks litigation costs and outcomes."""

    def __init__(self):
        """Initialize benchmarking analyzer."""
        self.litigation_data = None
        self.benchmarks = None

    def generate_litigation_data(self, num_cases: int = 200) -> pd.DataFrame:
        """Generate litigation case data."""
        np.random.seed(42)

        case_types = ['Product Liability', 'Contract', 'IP Infringement', 'Employment', 'Antitrust']
        claim_amounts = [100000, 500000, 1000000, 5000000, 10000000]
        outcomes = ['Favorable', 'Unfavorable', 'Settled', 'Dismissed']
        court_levels = ['District Court', 'Appeals Court', 'Supreme Court']

        data = {
            'case_id': [f'CASE-{i:05d}' for i in range(num_cases)],
            'case_type': np.random.choice(case_types, num_cases),
            'claim_amount': np.random.choice(claim_amounts, num_cases),
            'litigation_duration_months': np.random.randint(6, 60, num_cases),
            'defense_cost': None,
            'recovery_amount': None,
            'num_depositions': np.random.randint(2, 20, num_cases),
            'num_experts': np.random.randint(1, 8, num_cases),
            'document_count': np.random.randint(1000, 100000, num_cases),
            'appeal_level': np.random.choice(court_levels, num_cases),
            'case_outcome': np.random.choice(outcomes, num_cases),
            'discovery_disputes': np.random.randint(0, 5, num_cases),
            'motions_count': np.random.randint(0, 15, num_cases),
        }

        df = pd.DataFrame(data)

        # Calculate costs
        df['defense_cost'] = (
            df['num_depositions'] * 5000 +
            df['num_experts'] * 50000 +
            df['document_count'] / 100 * 50 +
            df['litigation_duration_months'] * 15000 +
            np.random.normal(0, 50000, num_cases)
        ).clip(lower=20000)

        # Calculate recovery
        df['recovery_amount'] = df.apply(
            lambda row: row['claim_amount'] * np.random.uniform(0.4, 0.95) if row['case_outcome'] == 'Favorable'
            else (row['claim_amount'] * 0.1) if row['case_outcome'] == 'Unfavorable'
            else row['claim_amount'] * np.random.uniform(0.3, 0.8),
            axis=1
        )

        self.litigation_data = df
        return df

    def benchmark_by_case_type(self) -> pd.DataFrame:
        """Benchmark costs by case type."""
        benchmark = self.litigation_data.groupby('case_type').agg({
            'claim_amount': ['mean', 'median'],
            'defense_cost': ['mean', 'median', 'min', 'max'],
            'litigation_duration_months': 'mean',
            'recovery_amount': 'mean',
            'num_depositions': 'mean',
            'num_experts': 'mean',
            'case_id': 'count'
        }).round(0)

        benchmark.columns = ['avg_claim', 'median_claim', 'avg_defense', 'median_defense',
                            'min_defense', 'max_defense', 'avg_duration', 'avg_recovery',
                            'avg_depositions', 'avg_experts', 'num_cases']

        benchmark['cost_per_month'] = (benchmark['avg_defense'] / benchmark['avg_duration']).round(0)
        benchmark['recovery_rate'] = (benchmark['avg_recovery'] / benchmark['avg_claim'] * 100).round(2)

        return benchmark.sort_values('avg_defense', ascending=False)

    def cost_by_claim_size(self) -> pd.DataFrame:
        """Analyze costs by claim amount."""
        df = self.litigation_data.copy()
        df['claim_size_tier'] = pd.cut(df['claim_amount'],
                                       bins=[0, 500000, 1000000, 5000000, 100000000],
                                       labels=['Small', 'Medium', 'Large', 'Very Large'])

        analysis = df.groupby('claim_size_tier').agg({
            'claim_amount': ['mean', 'count'],
            'defense_cost': ['mean', 'median'],
            'litigation_duration_months': 'mean',
            'recovery_amount': 'mean'
        }).round(0)

        analysis.columns = ['avg_claim', 'num_cases', 'avg_defense', 'median_defense',
                           'avg_duration', 'avg_recovery']

        analysis['cost_as_pct_of_claim'] = (analysis['avg_defense'] / analysis['avg_claim'] * 100).round(2)

        return analysis

    def efficiency_metrics(self) -> pd.DataFrame:
        """Calculate litigation efficiency metrics."""
        efficiency = self.litigation_data.groupby('case_type').agg({
            'defense_cost': 'mean',
            'litigation_duration_months': 'mean',
            'num_depositions': 'mean',
            'num_experts': 'mean',
            'document_count': 'mean',
            'recovery_amount': 'mean',
            'case_id': 'count'
        }).round(2)

        efficiency.columns = ['avg_cost', 'avg_duration', 'avg_depositions', 'avg_experts',
                             'avg_documents', 'avg_recovery', 'num_cases']

        efficiency['cost_per_deposition'] = (efficiency['avg_cost'] / efficiency['avg_depositions']).round(0)
        efficiency['cost_per_expert'] = (efficiency['avg_cost'] / efficiency['avg_experts']).round(0)
        efficiency['cost_per_month'] = (efficiency['avg_cost'] / efficiency['avg_duration']).round(0)

        return efficiency

    def outcome_analysis(self) -> pd.DataFrame:
        """Analyze costs and outcomes."""
        outcomes = self.litigation_data.groupby('case_outcome').agg({
            'defense_cost': ['mean', 'median', 'std'],
            'recovery_amount': 'mean',
            'litigation_duration_months': 'mean',
            'claim_amount': 'mean',
            'case_id': 'count'
        }).round(0)

        outcomes.columns = ['avg_cost', 'median_cost', 'cost_std', 'avg_recovery',
                           'avg_duration', 'avg_claim', 'num_cases']

        outcomes['net_result'] = (outcomes['avg_recovery'] - outcomes['avg_cost']).round(0)
        outcomes['roi'] = ((outcomes['avg_recovery'] - outcomes['avg_cost']) / outcomes['avg_cost'] * 100).round(2)

        return outcomes

    def predictive_cost_model(self) -> Dict:
        """Create simplified predictive cost model."""
        model_data = self.litigation_data.groupby('case_type').agg({
            'defense_cost': 'mean',
            'litigation_duration_months': 'mean',
            'num_depositions': 'mean',
            'num_experts': 'mean',
            'document_count': 'mean'
        })

        model = {}

        for case_type in model_data.index:
            base_cost = 50000  # Base litigation cost
            monthly_cost = model_data.loc[case_type, 'litigation_duration_months'] * 10000
            deposition_cost = model_data.loc[case_type, 'num_depositions'] * 5000
            expert_cost = model_data.loc[case_type, 'num_experts'] * 40000
            doc_cost = model_data.loc[case_type, 'document_count'] / 1000 * 50

            predicted_cost = base_cost + monthly_cost + deposition_cost + expert_cost + doc_cost

            model[case_type] = {
                'predicted_avg_cost': predicted_cost,
                'actual_avg_cost': model_data.loc[case_type, 'defense_cost'],
                'variance_pct': ((model_data.loc[case_type, 'defense_cost'] - predicted_cost) / predicted_cost * 100)
            }

        return model

    def benchmark_against_industry(self) -> Dict:
        """Compare internal benchmarks to industry standards."""
        industry_benchmarks = {
            'Product Liability': {'avg_cost': 350000, 'avg_duration': 24},
            'Contract': {'avg_cost': 150000, 'avg_duration': 18},
            'IP Infringement': {'avg_cost': 400000, 'avg_duration': 30},
            'Employment': {'avg_cost': 100000, 'avg_duration': 12},
            'Antitrust': {'avg_cost': 500000, 'avg_duration': 36}
        }

        internal_benchmark = self.benchmark_by_case_type()

        comparison = {}

        for case_type in industry_benchmarks.keys():
            if case_type in internal_benchmark.index:
                internal_cost = internal_benchmark.loc[case_type, 'avg_defense']
                industry_cost = industry_benchmarks[case_type]['avg_cost']

                comparison[case_type] = {
                    'internal_cost': internal_cost,
                    'industry_cost': industry_cost,
                    'variance_pct': ((internal_cost - industry_cost) / industry_cost * 100),
                    'status': 'Below Market' if internal_cost < industry_cost else 'Above Market'
                }

        return comparison

    def export_benchmark(self, output_dir: str = './') -> None:
        """Export benchmarking analysis."""
        self.benchmark_by_case_type().to_csv(f'{output_dir}benchmark_by_case_type.csv')
        self.cost_by_claim_size().to_csv(f'{output_dir}cost_by_claim_size.csv')
        self.efficiency_metrics().to_csv(f'{output_dir}efficiency_metrics.csv')
        self.outcome_analysis().to_csv(f'{output_dir}outcome_analysis.csv')

        print(f"Benchmarking analysis exported to {output_dir}")


# Example usage
if __name__ == "__main__":
    benchmark = LitigationBenchmark()

    print("Generating litigation data...")
    benchmark.generate_litigation_data(200)

    print("\n=== LITIGATION BENCHMARKS BY CASE TYPE ===")
    print(benchmark.benchmark_by_case_type())

    print("\n=== COST BY CLAIM SIZE ===")
    print(benchmark.cost_by_claim_size())

    print("\n=== EFFICIENCY METRICS ===")
    print(benchmark.efficiency_metrics())

    print("\n=== OUTCOME ANALYSIS ===")
    print(benchmark.outcome_analysis())

    print("\n=== INDUSTRY COMPARISON ===")
    comparison = benchmark.benchmark_against_industry()
    for case_type, data in comparison.items():
        print(f"\n{case_type}:")
        print(f"  Internal: ${data['internal_cost']:,.0f}, Industry: ${data['industry_cost']:,.0f}")
        print(f"  Variance: {data['variance_pct']:.1f}% ({data['status']})")
