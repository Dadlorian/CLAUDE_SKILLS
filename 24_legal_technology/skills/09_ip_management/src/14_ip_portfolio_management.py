"""
IP Portfolio Management Example
Manages overall IP portfolio and strategic planning
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class IPAssetStatus(Enum):
    """Status of IP asset"""
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"
    ABANDONED = "abandoned"
    LICENSED = "licensed"

@dataclass
class IPAsset:
    """Represents an IP asset in portfolio"""
    asset_id: str
    asset_type: str  # patent, trademark, copyright, trade_secret
    title: str
    status: IPAssetStatus
    filing_date: str
    registration_date: Optional[str]
    expiration_date: Optional[str]
    jurisdictions: List[str] = field(default_factory=list)
    annual_cost: float = 0.0
    estimated_value: float = 0.0
    business_relevance: str = "Medium"  # Low, Medium, High, Critical
    enforcement_potential: str = "Low"  # Low, Medium, High
    notes: Optional[str] = None

class IPPortfolioManager:
    """Manage IP portfolio strategically"""

    def __init__(self, company_name: str):
        self.company_name = company_name
        self.assets: Dict[str, IPAsset] = {}
        self.portfolio_strategy = None

    def add_asset(self, asset: IPAsset):
        """Add IP asset to portfolio"""
        self.assets[asset.asset_id] = asset

    def remove_asset(self, asset_id: str):
        """Remove asset from portfolio"""
        if asset_id in self.assets:
            del self.assets[asset_id]

    def get_portfolio_summary(self) -> Dict:
        """Get high-level portfolio summary"""
        if not self.assets:
            return {'total_assets': 0}

        # Count by type
        by_type = {}
        by_status = {}
        by_relevance = {}

        for asset in self.assets.values():
            # By type
            by_type[asset.asset_type] = by_type.get(asset.asset_type, 0) + 1

            # By status
            by_status[asset.status.value] = by_status.get(asset.status.value, 0) + 1

            # By business relevance
            by_relevance[asset.business_relevance] = by_relevance.get(asset.business_relevance, 0) + 1

        # Calculate costs and values
        total_annual_cost = sum(asset.annual_cost for asset in self.assets.values())
        total_estimated_value = sum(asset.estimated_value for asset in self.assets.values())

        return {
            'total_assets': len(self.assets),
            'by_type': by_type,
            'by_status': by_status,
            'by_business_relevance': by_relevance,
            'total_annual_cost': total_annual_cost,
            'total_estimated_value': total_estimated_value,
            'average_asset_value': total_estimated_value / len(self.assets) if self.assets else 0
        }

    def analyze_portfolio_risk(self) -> Dict:
        """Identify portfolio risks"""
        risks = {
            'total_at_risk': 0,
            'expiring_soon': [],
            'high_cost_low_value': [],
            'enforcement_weak': [],
            'jurisdiction_gaps': []
        }

        today = datetime.now()

        for asset in self.assets.values():
            # Check expiration
            if asset.expiration_date:
                exp_date = datetime.strptime(asset.expiration_date, '%Y-%m-%d')
                days_until_expiration = (exp_date - today).days

                if 0 < days_until_expiration < 365:
                    risks['expiring_soon'].append({
                        'asset_id': asset.asset_id,
                        'days_remaining': days_until_expiration
                    })
                    risks['total_at_risk'] += 1

            # Check cost vs value
            if asset.annual_cost > 0 and asset.estimated_value < (asset.annual_cost * 10):
                risks['high_cost_low_value'].append(asset.asset_id)
                risks['total_at_risk'] += 1

            # Check enforcement potential
            if asset.enforcement_potential == "Low":
                risks['enforcement_weak'].append(asset.asset_id)

        return risks

    def identify_optimization_opportunities(self) -> Dict:
        """Identify opportunities to optimize portfolio"""
        opportunities = {
            'candidates_for_abandonment': [],
            'expansion_opportunities': [],
            'consolidation_candidates': [],
            'licensing_candidates': []
        }

        for asset in self.assets.values():
            # Low value, high cost = candidate for abandonment
            if asset.estimated_value < 10000 and asset.annual_cost > 5000:
                opportunities['candidates_for_abandonment'].append(asset.asset_id)

            # High value, active, strong enforcement = licensing candidate
            if asset.estimated_value > 100000 and asset.status == IPAssetStatus.ACTIVE and asset.enforcement_potential == "High":
                opportunities['licensing_candidates'].append(asset.asset_id)

            # Active, critical relevance = expansion opportunity
            if asset.business_relevance == "Critical" and asset.status == IPAssetStatus.ACTIVE:
                # Check if could be expanded to more jurisdictions
                if len(asset.jurisdictions) < 5:
                    opportunities['expansion_opportunities'].append(asset.asset_id)

        return opportunities

    def get_jurisdiction_coverage(self) -> Dict:
        """Analyze geographic jurisdiction coverage"""
        jurisdiction_assets = {}

        for asset in self.assets.values():
            for jurisdiction in asset.jurisdictions:
                if jurisdiction not in jurisdiction_assets:
                    jurisdiction_assets[jurisdiction] = []
                jurisdiction_assets[jurisdiction].append(asset.asset_id)

        return {
            'total_jurisdictions': len(jurisdiction_assets),
            'coverage_by_jurisdiction': {
                jurisdiction: len(assets)
                for jurisdiction, assets in sorted(jurisdiction_assets.items(), key=lambda x: len(x[1]), reverse=True)
            },
            'major_markets_coverage': 'US' in jurisdiction_assets and 'EU' in jurisdiction_assets and 'CN' in jurisdiction_assets
        }

    def calculate_portfolio_roi(self) -> Dict:
        """Calculate return on investment for portfolio"""
        total_cost = sum(asset.annual_cost for asset in self.assets.values())
        total_value = sum(asset.estimated_value for asset in self.assets.values())

        if total_cost == 0:
            roi_percentage = 0
        else:
            roi_percentage = ((total_value - total_cost) / total_cost) * 100

        # By asset type
        roi_by_type = {}
        for asset_type in set(a.asset_type for a in self.assets.values()):
            type_assets = [a for a in self.assets.values() if a.asset_type == asset_type]
            type_cost = sum(a.annual_cost for a in type_assets)
            type_value = sum(a.estimated_value for a in type_assets)

            if type_cost > 0:
                roi_by_type[asset_type] = ((type_value - type_cost) / type_cost) * 100
            else:
                roi_by_type[asset_type] = 0

        return {
            'total_annual_cost': total_cost,
            'total_portfolio_value': total_value,
            'overall_roi_percentage': roi_percentage,
            'roi_by_type': roi_by_type,
            'cost_effectiveness': "Good" if roi_percentage > 50 else "Fair" if roi_percentage > 0 else "Poor"
        }

    def get_strategic_recommendations(self) -> List[str]:
        """Get strategic recommendations for portfolio management"""
        recommendations = []

        summary = self.get_portfolio_summary()
        risks = self.analyze_portfolio_risk()
        opportunities = self.identify_optimization_opportunities()
        roi = self.calculate_portfolio_roi()

        # Cost efficiency
        if roi['overall_roi_percentage'] < 0:
            recommendations.append(f"Portfolio ROI is negative ({roi['overall_roi_percentage']:.1f}%). Consider divesting low-value assets.")

        # Expiration risks
        if risks['expiring_soon']:
            recommendations.append(f"{len(risks['expiring_soon'])} assets expiring soon. Prioritize renewal decisions.")

        # Jurisdiction coverage
        coverage = self.get_jurisdiction_coverage()
        if not coverage['major_markets_coverage']:
            recommendations.append("Expand geographic coverage to key markets (US, EU, China).")

        # Portfolio balance
        if summary['by_relevance'].get('Critical', 0) == 0:
            recommendations.append("Portfolio lacks critical strategic assets. Consider targeted filing strategy.")

        # Abandonment candidates
        if opportunities['candidates_for_abandonment']:
            recommendations.append(f"Consider abandoning {len(opportunities['candidates_for_abandonment'])} low-value, high-cost assets.")

        # Licensing opportunities
        if opportunities['licensing_candidates']:
            recommendations.append(f"Explore licensing {len(opportunities['licensing_candidates'])} valuable assets for revenue generation.")

        return recommendations


# Example usage
if __name__ == "__main__":
    manager = IPPortfolioManager("TechCorp Inc")

    # Add assets
    patent1 = IPAsset(
        "US10000001", "patent", "Machine Learning Algorithm",
        IPAssetStatus.ACTIVE, "2015-01-01", "2020-01-01", "2035-01-01",
        jurisdictions=["US", "EU", "CN"],
        annual_cost=3000,
        estimated_value=500000,
        business_relevance="Critical",
        enforcement_potential="High"
    )
    manager.add_asset(patent1)

    # Get summary
    summary = manager.get_portfolio_summary()
    print(f"Total assets: {summary['total_assets']}")
    print(f"Total annual cost: ${summary['total_annual_cost']:,.0f}")

    # Get recommendations
    recommendations = manager.get_strategic_recommendations()
    print("\nStrategic recommendations:")
    for rec in recommendations:
        print(f"  - {rec}")
