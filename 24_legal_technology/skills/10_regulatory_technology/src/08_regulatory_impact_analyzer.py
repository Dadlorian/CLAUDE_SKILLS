"""
Regulatory Impact Analyzer Module

Analyzes regulatory impacts including:
- Cost-benefit analysis
- Compliance impact assessment
- Industry sector impact modeling
- Stakeholder impact identification
- Market effects prediction
- Timeline and implementation analysis
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import statistics

logger = logging.getLogger(__name__)


class ImpactCategory(Enum):
    """Categories of regulatory impact."""
    COMPLIANCE_COSTS = "compliance_costs"
    OPERATIONAL_CHANGES = "operational_changes"
    COMPETITIVE_EFFECTS = "competitive_effects"
    CONSUMER_IMPACTS = "consumer_impacts"
    ENVIRONMENTAL = "environmental"
    ECONOMIC = "economic"
    EMPLOYMENT = "employment"
    HEALTH_SAFETY = "health_safety"


class SeverityLevel(Enum):
    """Severity levels for impacts."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    MAJOR = "major"
    CRITICAL = "critical"


class StakeholderCategory(Enum):
    """Categories of stakeholders affected."""
    LARGE_ENTERPRISE = "large_enterprise"
    SMALL_BUSINESS = "small_business"
    STARTUPS = "startups"
    CONSUMERS = "consumers"
    WORKERS = "workers"
    GOVERNMENT = "government"
    NONPROFITS = "nonprofits"
    ACADEMIC = "academic"


@dataclass
class ImpactEstimate:
    """Impact assessment for regulation."""
    impact_id: str
    regulation_id: str
    category: str
    description: str
    affected_parties: List[str]
    severity: str
    quantified_impact: Optional[float]
    impact_unit: str
    time_to_impact_months: int
    confidence_level: float  # 0-1
    analysis_date: str
    supporting_data: List[Dict] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)


@dataclass
class ComplianceCost:
    """Compliance cost analysis."""
    cost_id: str
    regulation_id: str
    cost_category: str
    cost_type: str  # One-time, Annual, Per-unit
    estimated_cost: Decimal
    cost_unit: str
    affected_entities: int
    total_cost_estimate: Decimal
    implementation_timeline_months: int
    confidence_level: float
    cost_drivers: List[str] = field(default_factory=list)
    cost_variance_range: Tuple[Decimal, Decimal] = field(default_factory=lambda: (Decimal(0), Decimal(0)))


@dataclass
class StakeholderImpactProfile:
    """Impact profile for specific stakeholder group."""
    stakeholder_id: str
    stakeholder_category: str
    number_affected: int
    primary_impacts: List[str]
    financial_impact_estimate: Optional[Decimal]
    operational_burden_score: float  # 1-10
    time_to_compliance_months: int
    competitive_advantage_change: Optional[float]  # Positive or negative
    disproportionate_impact: bool
    mitigation_options: List[Dict] = field(default_factory=list)
    regional_variations: Dict = field(default_factory=dict)


@dataclass
class RegulatoryImpactAnalysis:
    """Comprehensive impact analysis of regulation."""
    analysis_id: str
    regulation_id: str
    regulation_title: str
    regulation_summary: str
    issuing_agency: str
    effective_date: str
    analysis_date: str
    impacts: List[ImpactEstimate] = field(default_factory=list)
    compliance_costs: List[ComplianceCost] = field(default_factory=list)
    stakeholder_impacts: List[StakeholderImpactProfile] = field(default_factory=list)
    total_estimated_cost: Decimal = Decimal(0)
    total_estimated_benefit: Decimal = Decimal(0)
    net_benefit_estimate: Decimal = Decimal(0)
    benefit_cost_ratio: Optional[float] = None
    affected_industries: List[str] = field(default_factory=list)
    implementation_requirements: List[Dict] = field(default_factory=list)
    risk_assessment: Optional[Dict] = None
    recommendations: List[str] = field(default_factory=list)


class RegulatoryImpactAnalyzer:
    """
    Analyzes regulatory impacts across multiple dimensions.

    Features:
    - Multi-stakeholder impact assessment
    - Cost-benefit analysis
    - Compliance burden quantification
    - Industry sector impact modeling
    - Comparative analysis
    - Scenario modeling
    """

    def __init__(self):
        """Initialize impact analyzer."""
        self.analyses: Dict[str, RegulatoryImpactAnalysis] = {}
        self.impact_estimates: Dict[str, ImpactEstimate] = {}
        self.compliance_costs: Dict[str, ComplianceCost] = {}
        self.stakeholder_profiles: Dict[str, StakeholderImpactProfile] = {}
        logger.info("Regulatory Impact Analyzer initialized")

    def create_analysis(
        self,
        regulation_id: str,
        regulation_title: str,
        regulation_summary: str,
        issuing_agency: str,
        effective_date: str,
        affected_industries: List[str]
    ) -> str:
        """Create new regulatory impact analysis."""
        analysis_id = f"IMPACT_{regulation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        analysis = RegulatoryImpactAnalysis(
            analysis_id=analysis_id,
            regulation_id=regulation_id,
            regulation_title=regulation_title,
            regulation_summary=regulation_summary,
            issuing_agency=issuing_agency,
            effective_date=effective_date,
            analysis_date=datetime.now().isoformat(),
            affected_industries=affected_industries
        )

        self.analyses[analysis_id] = analysis
        logger.info(f"Impact analysis created: {analysis_id}")

        return analysis_id

    def add_impact_estimate(
        self,
        analysis_id: str,
        impact: ImpactEstimate
    ) -> bool:
        """Add impact estimate to analysis."""
        if analysis_id not in self.analyses:
            logger.error(f"Analysis {analysis_id} not found")
            return False

        analysis = self.analyses[analysis_id]
        analysis.impacts.append(impact)
        self.impact_estimates[impact.impact_id] = impact

        logger.info(f"Impact estimate added: {impact.impact_id}")

        return True

    def add_compliance_cost(
        self,
        analysis_id: str,
        cost: ComplianceCost
    ) -> bool:
        """Add compliance cost estimate."""
        if analysis_id not in self.analyses:
            logger.error(f"Analysis {analysis_id} not found")
            return False

        analysis = self.analyses[analysis_id]
        analysis.compliance_costs.append(cost)
        analysis.total_estimated_cost += cost.total_cost_estimate

        self.compliance_costs[cost.cost_id] = cost

        logger.info(f"Compliance cost added: {cost.cost_id}")

        return True

    def add_stakeholder_impact(
        self,
        analysis_id: str,
        stakeholder_impact: StakeholderImpactProfile
    ) -> bool:
        """Add stakeholder impact profile."""
        if analysis_id not in self.analyses:
            logger.error(f"Analysis {analysis_id} not found")
            return False

        analysis = self.analyses[analysis_id]
        analysis.stakeholder_impacts.append(stakeholder_impact)
        self.stakeholder_profiles[stakeholder_impact.stakeholder_id] = stakeholder_impact

        logger.info(f"Stakeholder impact added: {stakeholder_impact.stakeholder_id}")

        return True

    def calculate_cost_benefit_ratio(self, analysis_id: str) -> Optional[float]:
        """Calculate benefit-to-cost ratio."""
        if analysis_id not in self.analyses:
            return None

        analysis = self.analyses[analysis_id]

        if analysis.total_estimated_cost == Decimal(0):
            return None

        ratio = float(analysis.total_estimated_benefit / analysis.total_estimated_cost)
        analysis.benefit_cost_ratio = ratio

        return ratio

    def estimate_small_business_impact(
        self,
        analysis_id: str
    ) -> Dict:
        """Analyze disproportionate impact on small businesses."""
        if analysis_id not in self.analyses:
            return {}

        analysis = self.analyses[analysis_id]

        small_biz_impacts = [
            s for s in analysis.stakeholder_impacts
            if s.stakeholder_category == StakeholderCategory.SMALL_BUSINESS.value
        ]

        if not small_biz_impacts:
            return {
                "analysis_id": analysis_id,
                "small_business_count": 0,
                "disproportionate_impact": False
            }

        total_affected = sum(s.number_affected for s in small_biz_impacts)
        avg_financial_impact = Decimal(0)

        for impact in small_biz_impacts:
            if impact.financial_impact_estimate:
                avg_financial_impact += impact.financial_impact_estimate

        return {
            "analysis_id": analysis_id,
            "small_business_count": total_affected,
            "average_financial_impact": avg_financial_impact / len(small_biz_impacts) if small_biz_impacts else Decimal(0),
            "average_compliance_burden": statistics.mean([s.operational_burden_score for s in small_biz_impacts]),
            "disproportionate_impact": any(s.disproportionate_impact for s in small_biz_impacts),
            "mitigation_needed": any(s.disproportionate_impact for s in small_biz_impacts)
        }

    def identify_high_impact_stakeholders(
        self,
        analysis_id: str,
        threshold_financial: Decimal = Decimal(1000000)
    ) -> List[Dict]:
        """Identify stakeholders with significant financial impact."""
        if analysis_id not in self.analyses:
            return []

        analysis = self.analyses[analysis_id]

        high_impact = [
            {
                "stakeholder_category": s.stakeholder_category,
                "number_affected": s.number_affected,
                "financial_impact": s.financial_impact_estimate,
                "burden_score": s.operational_burden_score,
                "per_entity_impact": (
                    s.financial_impact_estimate / s.number_affected
                    if s.financial_impact_estimate and s.number_affected > 0
                    else Decimal(0)
                )
            }
            for s in analysis.stakeholder_impacts
            if s.financial_impact_estimate and s.financial_impact_estimate >= threshold_financial
        ]

        return sorted(
            high_impact,
            key=lambda x: x["financial_impact"],
            reverse=True
        )

    def estimate_implementation_timeline(
        self,
        analysis_id: str
    ) -> Dict:
        """Estimate implementation timeline and milestones."""
        if analysis_id not in self.analyses:
            return {}

        analysis = self.analyses[analysis_id]

        # Group compliance costs by timeline
        timeline_phases = {}

        for cost in analysis.compliance_costs:
            phase = cost.implementation_timeline_months

            if phase not in timeline_phases:
                timeline_phases[phase] = {
                    "months_from_effective": phase,
                    "costs": Decimal(0),
                    "affected_entities": 0
                }

            timeline_phases[phase]["costs"] += cost.total_cost_estimate
            timeline_phases[phase]["affected_entities"] += cost.affected_entities

        # Sort by timeline
        sorted_phases = sorted(timeline_phases.items(), key=lambda x: x[0])

        return {
            "analysis_id": analysis_id,
            "implementation_phases": [
                {
                    "months_from_effective": phase_months,
                    "estimated_cost": phase_data["costs"],
                    "estimated_affected_entities": phase_data["affected_entities"]
                }
                for phase_months, phase_data in sorted_phases
            ],
            "total_implementation_timeline_months": max([p[0] for p in sorted_phases]) if sorted_phases else 0
        }

    def perform_scenario_analysis(
        self,
        analysis_id: str,
        scenarios: Dict[str, float]  # Scenario name -> cost multiplier
    ) -> Dict:
        """Perform scenario analysis with different cost assumptions."""
        if analysis_id not in self.analyses:
            return {}

        analysis = self.analyses[analysis_id]
        scenario_results = {}

        base_cost = analysis.total_estimated_cost
        base_benefit = analysis.total_estimated_benefit

        for scenario_name, multiplier in scenarios.items():
            scenario_cost = base_cost * Decimal(str(multiplier))
            scenario_benefit = base_benefit

            net_benefit = scenario_benefit - scenario_cost

            scenario_results[scenario_name] = {
                "total_cost": scenario_cost,
                "total_benefit": scenario_benefit,
                "net_benefit": net_benefit,
                "benefit_cost_ratio": float(
                    scenario_benefit / scenario_cost
                ) if scenario_cost > Decimal(0) else None
            }

        return {
            "analysis_id": analysis_id,
            "base_case": {
                "total_cost": base_cost,
                "total_benefit": base_benefit,
                "net_benefit": base_benefit - base_cost
            },
            "scenarios": scenario_results
        }

    def compare_regulatory_alternatives(
        self,
        analysis_ids: List[str]
    ) -> Dict:
        """Compare impacts across alternative regulatory approaches."""
        analyses = [self.analyses.get(aid) for aid in analysis_ids]
        analyses = [a for a in analyses if a is not None]

        if not analyses:
            return {}

        comparison = {
            "compared_analyses": len(analyses),
            "comparison_date": datetime.now().isoformat(),
            "alternatives": []
        }

        for analysis in analyses:
            alternative = {
                "analysis_id": analysis.analysis_id,
                "regulation_title": analysis.regulation_title,
                "total_cost": analysis.total_estimated_cost,
                "total_benefit": analysis.total_estimated_benefit,
                "net_benefit": analysis.net_benefit_estimate,
                "benefit_cost_ratio": analysis.benefit_cost_ratio,
                "affected_stakeholders": len(analysis.stakeholder_impacts),
                "small_business_impact": self.estimate_small_business_impact(analysis.analysis_id)
            }

            comparison["alternatives"].append(alternative)

        # Rank alternatives
        comparison["ranked_by_net_benefit"] = sorted(
            comparison["alternatives"],
            key=lambda x: x["net_benefit"],
            reverse=True
        )

        return comparison

    def identify_regulatory_gaps(
        self,
        analysis_id: str
    ) -> List[Dict]:
        """Identify potential regulatory gaps and unintended consequences."""
        if analysis_id not in self.analyses:
            return []

        analysis = self.analyses[analysis_id]
        gaps = []

        # Identify stakeholders without impact assessments
        assessed_categories = {s.stakeholder_category for s in analysis.stakeholder_impacts}
        all_categories = {cat.value for cat in StakeholderCategory}

        missing_assessments = all_categories - assessed_categories
        if missing_assessments:
            gaps.append({
                "type": "Missing Impact Assessment",
                "detail": f"No impact assessment for: {', '.join(missing_assessments)}",
                "severity": SeverityLevel.MODERATE.value
            })

        # Identify high-cost items with low confidence
        low_confidence_costs = [
            c for c in analysis.compliance_costs
            if c.confidence_level < 0.5
        ]

        if low_confidence_costs:
            gaps.append({
                "type": "High Uncertainty Costs",
                "detail": f"{len(low_confidence_costs)} cost estimates have low confidence",
                "severity": SeverityLevel.SIGNIFICANT.value
            })

        return gaps

    def generate_impact_report(self, analysis_id: str) -> Dict:
        """Generate comprehensive impact report."""
        if analysis_id not in self.analyses:
            return {}

        analysis = self.analyses[analysis_id]

        # Calculate cost benefit
        self.calculate_cost_benefit_ratio(analysis_id)

        # Calculate net benefit
        analysis.net_benefit_estimate = analysis.total_estimated_benefit - analysis.total_estimated_cost

        # Generate executive summary
        summary = {
            "analysis_id": analysis_id,
            "regulation": {
                "title": analysis.regulation_title,
                "issuing_agency": analysis.issuing_agency,
                "effective_date": analysis.effective_date
            },
            "financial_summary": {
                "total_estimated_cost": analysis.total_estimated_cost,
                "total_estimated_benefit": analysis.total_estimated_benefit,
                "net_benefit": analysis.net_benefit_estimate,
                "benefit_cost_ratio": analysis.benefit_cost_ratio
            },
            "affected_parties": {
                "total_stakeholder_groups": len(analysis.stakeholder_impacts),
                "total_estimated_affected": sum(s.number_affected for s in analysis.stakeholder_impacts),
                "high_impact_stakeholders": self.identify_high_impact_stakeholders(analysis_id),
                "small_business_impact": self.estimate_small_business_impact(analysis_id)
            },
            "implementation": self.estimate_implementation_timeline(analysis_id),
            "identified_gaps": self.identify_regulatory_gaps(analysis_id),
            "recommendations": analysis.recommendations,
            "report_date": datetime.now().isoformat()
        }

        return summary

    def export_analysis(self, analysis_id: str, format: str = "json") -> str:
        """Export analysis."""
        if analysis_id not in self.analyses:
            return ""

        analysis = self.analyses[analysis_id]

        if format == "json":
            # Generate report first to ensure all calculated fields are set
            self.generate_impact_report(analysis_id)

            return json.dumps({
                "analysis_id": analysis.analysis_id,
                "regulation_id": analysis.regulation_id,
                "total_cost": str(analysis.total_estimated_cost),
                "total_benefit": str(analysis.total_estimated_benefit),
                "net_benefit": str(analysis.net_benefit_estimate),
                "benefit_cost_ratio": analysis.benefit_cost_ratio,
                "stakeholders_analyzed": len(analysis.stakeholder_impacts),
                "compliance_requirements": len(analysis.compliance_costs)
            }, indent=2)

        return ""


if __name__ == "__main__":
    # Example usage
    analyzer = RegulatoryImpactAnalyzer()

    # Create analysis
    analysis_id = analyzer.create_analysis(
        "EPA-2024-0001",
        "Air Quality Standards Update",
        "Updates to National Ambient Air Quality Standards",
        "EPA",
        "2024-06-01",
        ["Energy", "Manufacturing", "Transportation"]
    )

    # Add compliance cost
    cost = ComplianceCost(
        cost_id="COST_1",
        regulation_id="EPA-2024-0001",
        cost_category="Equipment Upgrade",
        cost_type="One-time",
        estimated_cost=Decimal("50000"),
        cost_unit="per facility",
        affected_entities=5000,
        total_cost_estimate=Decimal("250000000"),
        implementation_timeline_months=12,
        confidence_level=0.8,
        cost_drivers=["New monitoring equipment", "Installation costs"]
    )

    analyzer.add_compliance_cost(analysis_id, cost)

    # Add stakeholder impact
    stakeholder_impact = StakeholderImpactProfile(
        stakeholder_id="SMALL_BIZ_001",
        stakeholder_category=StakeholderCategory.SMALL_BUSINESS.value,
        number_affected=2000,
        primary_impacts=["Compliance costs", "Equipment costs"],
        financial_impact_estimate=Decimal("50000"),
        operational_burden_score=7.5,
        time_to_compliance_months=12,
        competitive_advantage_change=None,
        disproportionate_impact=True
    )

    analyzer.add_stakeholder_impact(analysis_id, stakeholder_impact)

    # Generate report
    report = analyzer.generate_impact_report(analysis_id)
    print(json.dumps(report, indent=2, default=str))
