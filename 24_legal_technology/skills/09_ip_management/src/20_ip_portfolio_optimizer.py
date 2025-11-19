"""
IP Portfolio Optimization Example
Optimizes IP portfolio composition and maintenance strategy
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics


class OptimizationStrategy(Enum):
    """Portfolio optimization strategies"""
    COST_MINIMIZATION = "cost_minimization"
    VALUE_MAXIMIZATION = "value_maximization"
    BALANCED = "balanced"
    GROWTH_FOCUSED = "growth_focused"
    MAINTENANCE_FOCUSED = "maintenance_focused"


@dataclass
class IPAsset:
    """IP asset for optimization"""
    asset_id: str
    asset_type: str  # patent, trademark, copyright
    acquisition_date: datetime
    acquisition_cost: float
    annual_maintenance_cost: float
    estimated_current_value: float
    jurisdiction_count: int
    citation_count: int  # For patents
    licensing_potential: float  # 0-1 scale
    renewal_years_remaining: int
    associated_revenue: float  # Annual revenue it generates
    enforcement_risk: float  # 0-1 scale


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    strategy: OptimizationStrategy
    assets_to_retain: List[str]
    assets_to_abandon: List[str]
    assets_to_license: List[str]
    assets_to_expand: List[str]
    estimated_cost_savings: float
    estimated_value_gain: float
    annual_maintenance_reduction: float
    expected_roi_improvement: float


class IPPortfolioOptimizer:
    """Optimize IP portfolio"""

    def __init__(self):
        self.assets: Dict[str, IPAsset] = {}
        self.historical_performance = defaultdict(list)

    def add_asset(self, asset: IPAsset):
        """Add asset to portfolio"""
        self.assets[asset.asset_id] = asset

    def calculate_asset_score(self, asset: IPAsset,
                             strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> float:
        """
        Calculate composite score for asset

        Args:
            asset: IP asset
            strategy: Optimization strategy

        Returns:
            Score from 0-100
        """
        scores = {
            'value': self._score_value(asset),
            'licensing': self._score_licensing_potential(asset),
            'maintenance': self._score_maintenance_efficiency(asset),
            'revenue': self._score_revenue_generation(asset),
            'enforcement': self._score_enforcement_value(asset)
        }

        if strategy == OptimizationStrategy.VALUE_MAXIMIZATION:
            weights = {'value': 0.40, 'licensing': 0.25, 'maintenance': 0.10, 'revenue': 0.20, 'enforcement': 0.05}
        elif strategy == OptimizationStrategy.COST_MINIMIZATION:
            weights = {'value': 0.20, 'licensing': 0.10, 'maintenance': 0.50, 'revenue': 0.15, 'enforcement': 0.05}
        elif strategy == OptimizationStrategy.GROWTH_FOCUSED:
            weights = {'value': 0.30, 'licensing': 0.35, 'maintenance': 0.10, 'revenue': 0.20, 'enforcement': 0.05}
        elif strategy == OptimizationStrategy.MAINTENANCE_FOCUSED:
            weights = {'value': 0.25, 'licensing': 0.15, 'maintenance': 0.30, 'revenue': 0.25, 'enforcement': 0.05}
        else:  # BALANCED
            weights = {'value': 0.25, 'licensing': 0.20, 'maintenance': 0.25, 'revenue': 0.20, 'enforcement': 0.10}

        composite_score = sum(scores[key] * weights[key] for key in scores)
        return composite_score

    def _score_value(self, asset: IPAsset) -> float:
        """Score asset value (0-100)"""
        if asset.estimated_current_value > 500000:
            return 90
        elif asset.estimated_current_value > 200000:
            return 75
        elif asset.estimated_current_value > 50000:
            return 60
        elif asset.estimated_current_value > 10000:
            return 40
        else:
            return 20

    def _score_licensing_potential(self, asset: IPAsset) -> float:
        """Score licensing potential (0-100)"""
        return asset.licensing_potential * 100

    def _score_maintenance_efficiency(self, asset: IPAsset) -> float:
        """Score maintenance efficiency (0-100)"""
        if asset.estimated_current_value <= 0:
            return 0

        cost_to_value_ratio = asset.annual_maintenance_cost / asset.estimated_current_value

        if cost_to_value_ratio < 0.05:  # Less than 5% of value
            return 90
        elif cost_to_value_ratio < 0.10:
            return 70
        elif cost_to_value_ratio < 0.20:
            return 50
        else:
            return 20

    def _score_revenue_generation(self, asset: IPAsset) -> float:
        """Score revenue generation (0-100)"""
        if asset.associated_revenue > 500000:
            return 100
        elif asset.associated_revenue > 100000:
            return 80
        elif asset.associated_revenue > 10000:
            return 60
        elif asset.associated_revenue > 1000:
            return 40
        else:
            return 10

    def _score_enforcement_value(self, asset: IPAsset) -> float:
        """Score enforcement value (0-100)"""
        enforcement_score = (1 - asset.enforcement_risk) * 100
        return enforcement_score

    def identify_candidates_for_abandonment(self) -> List[Tuple[str, float]]:
        """
        Identify candidates for abandonment

        Returns:
            List of (asset_id, score) tuples, lowest scores first
        """
        candidates = []

        for asset_id, asset in self.assets.items():
            # Red flags for abandonment
            red_flags = 0

            # High maintenance relative to value
            if asset.annual_maintenance_cost > asset.estimated_current_value * 0.15:
                red_flags += 2

            # Near end of life
            if asset.renewal_years_remaining < 2:
                red_flags += 1

            # No associated revenue
            if asset.associated_revenue == 0:
                red_flags += 1

            # Low licensing potential
            if asset.licensing_potential < 0.2:
                red_flags += 1

            # Low value
            if asset.estimated_current_value < 10000:
                red_flags += 1

            if red_flags >= 3:
                score = red_flags * 10
                candidates.append((asset_id, score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def identify_candidates_for_licensing(self) -> List[Tuple[str, float]]:
        """
        Identify candidates for licensing

        Returns:
            List of (asset_id, score) tuples, highest scores first
        """
        candidates = []

        for asset_id, asset in self.assets.items():
            # Positive indicators for licensing
            licensing_score = asset.licensing_potential * 100

            # Bonus for high value
            if asset.estimated_current_value > 100000:
                licensing_score += 20

            # Bonus for multiple jurisdictions
            if asset.jurisdiction_count >= 3:
                licensing_score += 15

            # Penalty for high enforcement risk
            if asset.enforcement_risk > 0.7:
                licensing_score -= 20

            if licensing_score > 50:
                candidates.append((asset_id, licensing_score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def identify_candidates_for_expansion(self) -> List[Tuple[str, float]]:
        """
        Identify candidates for geographic expansion

        Returns:
            List of (asset_id, score) tuples
        """
        candidates = []

        for asset_id, asset in self.assets.items():
            # High value assets with limited geographic coverage
            if asset.estimated_current_value > 100000 and asset.jurisdiction_count < 3:
                expansion_score = asset.estimated_current_value / 50000
                expansion_score += (3 - asset.jurisdiction_count) * 10
                candidates.append((asset_id, expansion_score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def optimize_portfolio(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> OptimizationResult:
        """
        Optimize portfolio based on strategy

        Args:
            strategy: Optimization strategy

        Returns:
            Optimization recommendations
        """
        # Score all assets
        scored_assets = []
        for asset_id, asset in self.assets.items():
            score = self.calculate_asset_score(asset, strategy)
            scored_assets.append((asset_id, score, asset))

        # Sort by score
        scored_assets.sort(key=lambda x: x[1], reverse=True)

        # Determine percentile thresholds
        if len(scored_assets) > 0:
            top_third = len(scored_assets) // 3 + 1
            bottom_third = len(scored_assets) - (len(scored_assets) // 3)
        else:
            top_third = 1
            bottom_third = 1

        # Categorize assets
        assets_to_retain = [a[0] for a in scored_assets[:top_third]]
        assets_to_review = [a[0] for a in scored_assets[top_third:bottom_third]]
        assets_to_abandon_candidates = [a[0] for a in scored_assets[bottom_third:]]

        # Further refine abandon candidates
        abandonment_candidates = self.identify_candidates_for_abandonment()
        assets_to_abandon = [a[0] for a in abandonment_candidates if a[0] in assets_to_abandon_candidates]

        # Licensing candidates
        licensing_candidates = self.identify_candidates_for_licensing()
        assets_to_license = [a[0] for a in licensing_candidates if a[0] in assets_to_review]

        # Expansion candidates
        expansion_candidates = self.identify_candidates_for_expansion()
        assets_to_expand = [a[0] for a in expansion_candidates if a[0] in assets_to_retain]

        # Calculate financial impact
        cost_savings = sum(
            self.assets[aid].annual_maintenance_cost
            for aid in assets_to_abandon
        )

        maintenance_reduction = sum(
            self.assets[aid].annual_maintenance_cost * 0.3  # Estimate 30% reduction from optimization
            for aid in assets_to_review
            if aid not in assets_to_license
        )

        licensing_revenue_potential = sum(
            self.assets[aid].estimated_current_value * 0.05  # Estimate 5% annual licensing revenue
            for aid in assets_to_license
        )

        expansion_cost = sum(
            self.assets[aid].acquisition_cost * 0.3  # Estimate 30% of original cost for expansion
            for aid in assets_to_expand
        )

        value_gain = licensing_revenue_potential * 10  # 10x multiplier for value

        return OptimizationResult(
            strategy=strategy,
            assets_to_retain=assets_to_retain,
            assets_to_abandon=assets_to_abandon,
            assets_to_license=assets_to_license,
            assets_to_expand=assets_to_expand,
            estimated_cost_savings=cost_savings,
            estimated_value_gain=value_gain,
            annual_maintenance_reduction=maintenance_reduction,
            expected_roi_improvement=((licensing_revenue_potential - expansion_cost) / self._get_total_investment() * 100) if self._get_total_investment() > 0 else 0
        )

    def _get_total_investment(self) -> float:
        """Get total annual investment in portfolio"""
        return sum(a.annual_maintenance_cost for a in self.assets.values())

    def generate_optimization_scenarios(self) -> Dict:
        """
        Generate optimization scenarios for different strategies

        Returns:
            Scenarios for all strategies
        """
        scenarios = {}

        for strategy in OptimizationStrategy:
            result = self.optimize_portfolio(strategy)
            scenarios[strategy.value] = {
                'assets_to_retain': result.assets_to_retain,
                'assets_to_abandon': result.assets_to_abandon,
                'assets_to_license': result.assets_to_license,
                'assets_to_expand': result.assets_to_expand,
                'cost_savings': result.estimated_cost_savings,
                'value_gain': result.estimated_value_gain,
                'maintenance_reduction': result.annual_maintenance_reduction,
                'roi_improvement': result.expected_roi_improvement
            }

        return scenarios

    def calculate_portfolio_health_metrics(self) -> Dict:
        """
        Calculate portfolio health metrics

        Returns:
            Health metrics
        """
        if not self.assets:
            return {}

        values = [a.estimated_current_value for a in self.assets.values()]
        maintenance_costs = [a.annual_maintenance_cost for a in self.assets.values()]
        revenue = [a.associated_revenue for a in self.assets.values()]

        total_value = sum(values)
        total_maintenance = sum(maintenance_costs)
        total_revenue = sum(revenue)

        # Portfolio diversity
        avg_value = statistics.mean(values) if values else 0
        concentration = (max(values) / total_value * 100) if total_value > 0 else 0

        return {
            'total_portfolio_value': total_value,
            'average_asset_value': avg_value,
            'portfolio_concentration_percent': concentration,
            'total_annual_maintenance': total_maintenance,
            'maintenance_to_value_ratio': (total_maintenance / total_value) if total_value > 0 else 0,
            'total_annual_revenue': total_revenue,
            'roi_percent': ((total_revenue - total_maintenance) / total_maintenance * 100) if total_maintenance > 0 else 0,
            'number_of_assets': len(self.assets),
            'avg_jurisdiction_coverage': statistics.mean([a.jurisdiction_count for a in self.assets.values()])
        }

    def generate_optimization_report(self) -> Dict:
        """
        Generate comprehensive optimization report

        Returns:
            Complete optimization analysis
        """
        return {
            'report_date': datetime.now().isoformat(),
            'portfolio_health': self.calculate_portfolio_health_metrics(),
            'optimization_scenarios': self.generate_optimization_scenarios(),
            'abandonment_candidates': self.identify_candidates_for_abandonment()[:5],
            'licensing_candidates': self.identify_candidates_for_licensing()[:5],
            'expansion_candidates': self.identify_candidates_for_expansion()[:5],
            'recommended_strategy': OptimizationStrategy.BALANCED.value
        }


from collections import defaultdict

# Example usage
if __name__ == "__main__":
    optimizer = IPPortfolioOptimizer()

    # Add sample assets
    for i in range(10):
        asset = IPAsset(
            asset_id=f"ASSET{i}",
            asset_type="patent" if i < 7 else "trademark",
            acquisition_date=datetime.now(),
            acquisition_cost=100000 + i*10000,
            annual_maintenance_cost=5000 + i*500,
            estimated_current_value=150000 + i*20000,
            jurisdiction_count=2 + (i % 3),
            citation_count=10 + i*2,
            licensing_potential=0.5 + (i % 5) * 0.1,
            renewal_years_remaining=10 - (i % 10),
            associated_revenue=50000 + i*5000,
            enforcement_risk=0.2 + (i % 5) * 0.1
        )
        optimizer.add_asset(asset)

    # Generate report
    report = optimizer.generate_optimization_report()
    print("IP Portfolio Optimization Report")
    print(f"Total Portfolio Value: ${report['portfolio_health']['total_portfolio_value']:,.0f}")
    print(f"Annual Maintenance: ${report['portfolio_health']['total_annual_maintenance']:,.0f}")
    print(f"Portfolio ROI: {report['portfolio_health']['roi_percent']:.1f}%")
    print(f"Assets Recommended for Abandonment: {len(report['abandonment_candidates'])}")
    print(f"Assets Recommended for Licensing: {len(report['licensing_candidates'])}")
