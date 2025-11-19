"""
Cohort Retention Analysis Tool for Growth Marketing

This script analyzes user cohorts by signup date, calculates retention curves,
identifies churn patterns, and compares cohort performance. Includes visualization
with matplotlib, export to CSV, and actionable insights generation.

Usage:
    python cohort_analysis.py --input users.csv --output cohort_report.html
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class CohortAnalyzer:
    """
    Comprehensive cohort analysis for growth marketing insights.

    Analyzes user retention, engagement, and revenue by cohort groups.
    """

    def __init__(self, user_data: pd.DataFrame):
        """
        Initialize cohort analyzer with user activity data.

        Args:
            user_data: DataFrame with columns ['user_id', 'signup_date', 'activity_date', 'revenue']
        """
        self.user_data = user_data.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prepare and clean data for cohort analysis."""
        # Convert dates to datetime
        self.user_data['signup_date'] = pd.to_datetime(self.user_data['signup_date'])
        self.user_data['activity_date'] = pd.to_datetime(self.user_data['activity_date'])

        # Extract cohort month (first day of signup month)
        self.user_data['cohort_month'] = self.user_data['signup_date'].dt.to_period('M')

        # Calculate days since signup
        self.user_data['days_since_signup'] = (
            self.user_data['activity_date'] - self.user_data['signup_date']
        ).dt.days

        # Create period buckets (weeks)
        self.user_data['period'] = (self.user_data['days_since_signup'] / 7).astype(int)

    def calculate_retention_cohorts(self) -> pd.DataFrame:
        """
        Calculate retention rates by cohort.

        Returns:
            DataFrame with cohort retention rates over time periods
        """
        # Group by cohort and period
        cohort_data = self.user_data.groupby(['cohort_month', 'period']).agg({
            'user_id': 'nunique'
        }).rename(columns={'user_id': 'active_users'}).reset_index()

        # Get cohort sizes (period 0)
        cohort_sizes = cohort_data[cohort_data['period'] == 0].set_index('cohort_month')['active_users']

        # Calculate retention percentage
        cohort_data['cohort_size'] = cohort_data['cohort_month'].map(cohort_sizes)
        cohort_data['retention_rate'] = (cohort_data['active_users'] / cohort_data['cohort_size'] * 100).round(2)

        # Pivot to create retention matrix
        retention_matrix = cohort_data.pivot_table(
            index='cohort_month',
            columns='period',
            values='retention_rate',
            fill_value=0
        )

        return retention_matrix

    def calculate_revenue_cohorts(self) -> pd.DataFrame:
        """
        Calculate cumulative revenue by cohort.

        Returns:
            DataFrame with cumulative revenue per cohort over time
        """
        if 'revenue' not in self.user_data.columns:
            raise ValueError("Revenue column required for revenue cohort analysis")

        # Calculate cumulative revenue by cohort and period
        revenue_data = self.user_data.groupby(['cohort_month', 'period']).agg({
            'revenue': 'sum'
        }).reset_index()

        # Calculate cumulative revenue
        revenue_data['cumulative_revenue'] = revenue_data.groupby('cohort_month')['revenue'].cumsum()

        # Get cohort sizes for per-user metrics
        cohort_sizes = self.user_data.groupby('cohort_month')['user_id'].nunique()
        revenue_data['cohort_size'] = revenue_data['cohort_month'].map(cohort_sizes)
        revenue_data['arpu'] = (revenue_data['cumulative_revenue'] / revenue_data['cohort_size']).round(2)

        # Pivot for visualization
        revenue_matrix = revenue_data.pivot_table(
            index='cohort_month',
            columns='period',
            values='arpu',
            fill_value=0
        )

        return revenue_matrix

    def identify_churn_patterns(self) -> Dict[str, any]:
        """
        Identify patterns in user churn behavior.

        Returns:
            Dictionary with churn insights and metrics
        """
        retention_matrix = self.calculate_retention_cohorts()

        insights = {
            'critical_periods': [],
            'avg_retention_by_period': {},
            'churn_velocity': {},
            'cohort_comparison': {}
        }

        # Calculate average retention by period across all cohorts
        for period in retention_matrix.columns:
            avg_retention = retention_matrix[period].mean()
            insights['avg_retention_by_period'][f'week_{period}'] = round(avg_retention, 2)

        # Find critical drop-off periods (>20% drop week-over-week)
        for i in range(1, len(retention_matrix.columns)):
            prev_retention = retention_matrix[i-1].mean()
            curr_retention = retention_matrix[i].mean()
            drop = prev_retention - curr_retention

            if drop > 20:
                insights['critical_periods'].append({
                    'period': f'week_{i-1}_to_{i}',
                    'retention_drop': round(drop, 2),
                    'action': 'High priority intervention needed'
                })

        # Calculate churn velocity (how fast users leave)
        for cohort in retention_matrix.index:
            week_1 = retention_matrix.loc[cohort, 1] if 1 in retention_matrix.columns else 100
            week_4 = retention_matrix.loc[cohort, 4] if 4 in retention_matrix.columns else 0
            velocity = week_1 - week_4
            insights['churn_velocity'][str(cohort)] = round(velocity, 2)

        # Compare recent cohorts vs older cohorts
        if len(retention_matrix) >= 3:
            recent_cohorts = retention_matrix.iloc[-3:].mean()
            older_cohorts = retention_matrix.iloc[:-3].mean() if len(retention_matrix) > 3 else retention_matrix.mean()

            for period in retention_matrix.columns[:5]:  # First 5 weeks
                if period in recent_cohorts.index and period in older_cohorts.index:
                    diff = recent_cohorts[period] - older_cohorts[period]
                    insights['cohort_comparison'][f'week_{period}'] = {
                        'recent_avg': round(recent_cohorts[period], 2),
                        'older_avg': round(older_cohorts[period], 2),
                        'improvement': round(diff, 2)
                    }

        return insights

    def calculate_ltv_estimates(self, avg_revenue_per_period: float = None) -> pd.DataFrame:
        """
        Estimate customer lifetime value by cohort.

        Args:
            avg_revenue_per_period: Average revenue per active period (if not in data)

        Returns:
            DataFrame with LTV estimates by cohort
        """
        retention_matrix = self.calculate_retention_cohorts()

        # Estimate LTV based on retention curve
        ltv_data = []

        for cohort in retention_matrix.index:
            retention_curve = retention_matrix.loc[cohort].values

            # Calculate expected number of periods active
            expected_periods = np.sum(retention_curve / 100)

            # Estimate LTV (simplified model)
            if 'revenue' in self.user_data.columns:
                cohort_revenue = self.user_data[
                    self.user_data['cohort_month'] == cohort
                ]['revenue'].sum()
                cohort_size = self.user_data[
                    self.user_data['cohort_month'] == cohort
                ]['user_id'].nunique()
                avg_ltv = cohort_revenue / cohort_size if cohort_size > 0 else 0
            else:
                avg_ltv = expected_periods * (avg_revenue_per_period or 10)

            ltv_data.append({
                'cohort': cohort,
                'expected_periods_active': round(expected_periods, 2),
                'estimated_ltv': round(avg_ltv, 2)
            })

        return pd.DataFrame(ltv_data)

    def visualize_retention_heatmap(self, save_path: str = None):
        """
        Create retention heatmap visualization.

        Args:
            save_path: Path to save the figure (optional)
        """
        retention_matrix = self.calculate_retention_cohorts()

        plt.figure(figsize=(14, 8))
        sns.heatmap(
            retention_matrix,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=50,
            vmin=0,
            vmax=100,
            cbar_kws={'label': 'Retention Rate (%)'}
        )
        plt.title('Cohort Retention Analysis - Week-over-Week Retention', fontsize=16, pad=20)
        plt.xlabel('Weeks Since Signup', fontsize=12)
        plt.ylabel('Cohort (Signup Month)', fontsize=12)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def visualize_retention_curves(self, save_path: str = None):
        """
        Create retention curves by cohort.

        Args:
            save_path: Path to save the figure (optional)
        """
        retention_matrix = self.calculate_retention_cohorts()

        plt.figure(figsize=(12, 7))
        for cohort in retention_matrix.index:
            plt.plot(
                retention_matrix.columns,
                retention_matrix.loc[cohort],
                marker='o',
                label=str(cohort),
                linewidth=2,
                markersize=6
            )

        plt.title('Retention Curves by Cohort', fontsize=16, pad=20)
        plt.xlabel('Weeks Since Signup', fontsize=12)
        plt.ylabel('Retention Rate (%)', fontsize=12)
        plt.legend(title='Cohort', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def generate_insights_report(self) -> str:
        """
        Generate actionable insights report from cohort analysis.

        Returns:
            Formatted text report with key insights and recommendations
        """
        retention_matrix = self.calculate_retention_cohorts()
        churn_patterns = self.identify_churn_patterns()
        ltv_estimates = self.calculate_ltv_estimates()

        report = []
        report.append("=" * 70)
        report.append("COHORT ANALYSIS INSIGHTS REPORT")
        report.append("=" * 70)
        report.append("")

        # Overall retention trends
        report.append("1. RETENTION OVERVIEW")
        report.append("-" * 70)
        avg_week1 = retention_matrix[1].mean() if 1 in retention_matrix.columns else 0
        avg_week4 = retention_matrix[4].mean() if 4 in retention_matrix.columns else 0
        avg_week12 = retention_matrix[12].mean() if 12 in retention_matrix.columns else 0

        report.append(f"   Average Week 1 Retention: {avg_week1:.1f}%")
        report.append(f"   Average Week 4 Retention: {avg_week4:.1f}%")
        report.append(f"   Average Week 12 Retention: {avg_week12:.1f}%")
        report.append("")

        # Critical periods
        if churn_patterns['critical_periods']:
            report.append("2. CRITICAL CHURN PERIODS (>20% drop)")
            report.append("-" * 70)
            for period in churn_patterns['critical_periods']:
                report.append(f"   {period['period']}: {period['retention_drop']:.1f}% drop")
                report.append(f"   → {period['action']}")
            report.append("")

        # Cohort comparison
        if churn_patterns['cohort_comparison']:
            report.append("3. RECENT vs HISTORICAL COHORTS")
            report.append("-" * 70)
            for week, data in list(churn_patterns['cohort_comparison'].items())[:3]:
                report.append(f"   {week}:")
                report.append(f"      Recent: {data['recent_avg']:.1f}% | Historical: {data['older_avg']:.1f}%")
                improvement = "improved" if data['improvement'] > 0 else "declined"
                report.append(f"      Status: {improvement} by {abs(data['improvement']):.1f}%")
            report.append("")

        # LTV insights
        report.append("4. LIFETIME VALUE ESTIMATES")
        report.append("-" * 70)
        avg_ltv = ltv_estimates['estimated_ltv'].mean()
        best_cohort = ltv_estimates.loc[ltv_estimates['estimated_ltv'].idxmax()]
        report.append(f"   Average LTV across cohorts: ${avg_ltv:.2f}")
        report.append(f"   Best performing cohort: {best_cohort['cohort']} (${best_cohort['estimated_ltv']:.2f})")
        report.append("")

        # Recommendations
        report.append("5. RECOMMENDED ACTIONS")
        report.append("-" * 70)

        if avg_week1 < 40:
            report.append("   🔴 LOW WEEK 1 RETENTION:")
            report.append("      - Review onboarding flow for friction points")
            report.append("      - Optimize time-to-first-value (TTFV)")
            report.append("      - Implement activation email sequence")
            report.append("")

        if avg_week4 < 20:
            report.append("   🔴 LOW WEEK 4 RETENTION:")
            report.append("      - Launch re-engagement campaigns")
            report.append("      - Identify and promote sticky features")
            report.append("      - Build habit-forming product loops")
            report.append("")

        if churn_patterns['critical_periods']:
            report.append("   ⚠️  HIGH CHURN PERIODS DETECTED:")
            report.append("      - Focus interventions on identified drop-off windows")
            report.append("      - A/B test retention tactics during critical periods")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def export_to_csv(self, output_path: str):
        """
        Export cohort analysis results to CSV.

        Args:
            output_path: Path for output CSV file
        """
        retention_matrix = self.calculate_retention_cohorts()
        retention_matrix.to_csv(output_path)
        print(f"Cohort analysis exported to: {output_path}")


def generate_sample_data(n_users: int = 10000, n_months: int = 6) -> pd.DataFrame:
    """
    Generate sample user activity data for testing.

    Args:
        n_users: Number of users to generate
        n_months: Number of months of data

    Returns:
        DataFrame with sample user activity
    """
    np.random.seed(42)

    data = []
    start_date = datetime.now() - timedelta(days=30*n_months)

    for user_id in range(n_users):
        # Random signup date
        signup_offset = np.random.randint(0, 30*n_months)
        signup_date = start_date + timedelta(days=signup_offset)

        # Simulate retention (decreasing probability over time)
        current_date = signup_date
        active = True
        week = 0

        while active and current_date <= datetime.now():
            # Add activity record
            data.append({
                'user_id': f'user_{user_id}',
                'signup_date': signup_date,
                'activity_date': current_date,
                'revenue': np.random.choice([0, 0, 0, 10, 25, 50], p=[0.7, 0.1, 0.1, 0.05, 0.03, 0.02])
            })

            # Determine if user continues (retention curve)
            retention_prob = max(0.1, 0.8 - (week * 0.05))
            active = np.random.random() < retention_prob

            current_date += timedelta(days=7)
            week += 1

    return pd.DataFrame(data)


# Example usage
if __name__ == "__main__":
    print("Cohort Analysis Tool - Growth Marketing")
    print("=" * 70)
    print()

    # Generate sample data
    print("Generating sample user data...")
    sample_data = generate_sample_data(n_users=5000, n_months=6)
    print(f"Generated {len(sample_data)} activity records for {sample_data['user_id'].nunique()} users")
    print()

    # Initialize analyzer
    analyzer = CohortAnalyzer(sample_data)

    # Calculate retention cohorts
    print("Calculating retention cohorts...")
    retention_matrix = analyzer.calculate_retention_cohorts()
    print(retention_matrix.head())
    print()

    # Identify churn patterns
    print("Analyzing churn patterns...")
    churn_insights = analyzer.identify_churn_patterns()
    print(f"Found {len(churn_insights['critical_periods'])} critical churn periods")
    print()

    # Generate insights report
    print(analyzer.generate_insights_report())

    # Create visualizations
    print("\nGenerating visualizations...")
    analyzer.visualize_retention_heatmap(save_path='cohort_heatmap.png')
    analyzer.visualize_retention_curves(save_path='retention_curves.png')
    print("Visualizations saved!")

    # Export to CSV
    analyzer.export_to_csv('cohort_analysis_results.csv')
    print("\nAnalysis complete!")