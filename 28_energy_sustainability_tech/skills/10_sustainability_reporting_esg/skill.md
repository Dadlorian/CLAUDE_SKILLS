# Sustainability Reporting & ESG - Production Implementation Guide

## Overview

Sustainability Reporting & ESG (Environmental, Social, Governance) systems track, measure, and report organizational sustainability performance to stakeholders including investors, regulators, customers, and employees. This skill covers production-grade implementations of ESG data collection, materiality assessment, framework compliance (CDP, TCFD, GRI, SASB), and automated report generation.

## Core Frameworks

### 1. CDP (Carbon Disclosure Project)
Global disclosure system for environmental impacts (climate, water, forests).

### 2. TCFD (Task Force on Climate-related Financial Disclosures)
Framework for climate-related financial risk disclosure.

### 3. GRI (Global Reporting Initiative)
Comprehensive sustainability reporting standard.

### 4. SASB (Sustainability Accounting Standards Board)
Industry-specific sustainability standards for investors.

### 5. UN Sustainable Development Goals (SDGs)
17 global goals for sustainable development.

### 6. EU Taxonomy
Classification system for sustainable economic activities.

## Production-Grade Implementation Example

```python
"""
Production-grade ESG Reporting & Sustainability Platform

Implements:
- Multi-framework data collection (CDP, TCFD, GRI, SASB)
- Materiality assessment
- Automated report generation
- Science-based target tracking
- Stakeholder engagement
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportingFramework(Enum):
    """ESG reporting frameworks"""
    CDP_CLIMATE = "cdp_climate"
    TCFD = "tcfd"
    GRI = "gri"
    SASB = "sasb"
    SDG = "sdg"
    EU_TAXONOMY = "eu_taxonomy"

class MaterialityLevel(Enum):
    """Materiality assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_MATERIAL = "not_material"

class StakeholderType(Enum):
    """Stakeholder categories"""
    INVESTORS = "investors"
    CUSTOMERS = "customers"
    EMPLOYEES = "employees"
    REGULATORS = "regulators"
    COMMUNITIES = "communities"
    SUPPLIERS = "suppliers"

@dataclass
class ESGMetric:
    """ESG performance metric"""
    metric_id: str
    category: str  # E, S, or G
    sub_category: str
    metric_name: str
    value: float
    unit: str
    reporting_period: str  # 2024, Q1-2024, etc.
    data_source: str
    framework: ReportingFramework
    materiality: MaterialityLevel
    sdg_alignment: List[int] = field(default_factory=list)  # SDG numbers
    verification_status: str = "unverified"  # unverified, internal, third-party

@dataclass
class MaterialityTopic:
    """Material ESG topic for the organization"""
    topic_id: str
    topic_name: str
    description: str
    category: str  # Environmental, Social, or Governance
    materiality_level: MaterialityLevel
    stakeholder_importance: Dict[StakeholderType, int] = field(default_factory=dict)  # 1-5 rating
    business_impact: int = 5  # 1-5, 5=highest
    frameworks: List[ReportingFramework] = field(default_factory=list)
    disclosure_topics: List[str] = field(default_factory=list)

@dataclass
class TCFDRisk:
    """TCFD climate-related risk"""
    risk_id: str
    risk_type: str  # Physical or Transition
    risk_category: str  # Acute, Chronic, Policy, Technology, Market, Reputation
    description: str
    time_horizon: str  # Short (<3y), Medium (3-6y), Long (>6y)
    likelihood: str  # Low, Medium, High
    magnitude: str  # Low, Medium, High
    financial_impact: Optional[float] = None  # $ impact
    mitigation_strategy: str = ""
    metrics: List[str] = field(default_factory=list)

@dataclass
class ScienceBasedTarget:
    """Science-based climate target (SBTi)"""
    target_id: str
    target_description: str
    baseline_year: int
    target_year: int
    baseline_emissions_mt: float
    target_reduction_percent: float
    target_emissions_mt: float
    scope_coverage: List[str]  # ["Scope 1", "Scope 2", "Scope 3"]
    pathway: str  # "1.5C" or "Well-below 2C"
    target_type: str  # "Absolute" or "Intensity"
    approved_by_sbti: bool = False

@dataclass
class ESGScore:
    """ESG rating/score"""
    organization_id: str
    score_date: datetime
    provider: str  # MSCI, Sustainalytics, etc.
    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    rating: str  # AAA, AA, A, BBB, etc. (provider-specific)
    industry_rank_percentile: Optional[float] = None

class ESGReportingPlatform:
    """
    Production-grade ESG Reporting Platform

    Features:
    - Multi-framework data collection
    - Materiality assessment
    - TCFD risk management
    - Science-based target tracking
    - Automated report generation
    - Stakeholder engagement
    - Data verification
    """

    def __init__(self, organization_id: str, organization_name: str):
        self.organization_id = organization_id
        self.organization_name = organization_name
        self.metrics: List[ESGMetric] = []
        self.material_topics: List[MaterialityTopic] = []
        self.tcfd_risks: List[TCFDRisk] = []
        self.science_based_targets: List[ScienceBasedTarget] = []
        self.esg_scores: List[ESGScore] = []

    def conduct_materiality_assessment(
        self,
        topics: List[MaterialityTopic],
        stakeholder_input: Dict[str, Dict[StakeholderType, int]]
    ) -> List[MaterialityTopic]:
        """
        Conduct double materiality assessment

        Double materiality considers:
        1. Financial materiality: Impact on business value
        2. Impact materiality: Organization's impact on society/environment

        Args:
            topics: ESG topics to assess
            stakeholder_input: Stakeholder ratings for each topic

        Returns:
            Prioritized list of material topics
        """

        assessed_topics = []

        for topic in topics:
            # Collect stakeholder importance ratings
            stakeholder_ratings = stakeholder_input.get(topic.topic_id, {})
            avg_stakeholder_importance = (
                sum(stakeholder_ratings.values()) / len(stakeholder_ratings)
                if stakeholder_ratings else 3.0
            )

            # Calculate materiality score (stakeholder importance × business impact)
            materiality_score = avg_stakeholder_importance * topic.business_impact

            # Assign materiality level
            if materiality_score >= 20:
                topic.materiality_level = MaterialityLevel.CRITICAL
            elif materiality_score >= 15:
                topic.materiality_level = MaterialityLevel.HIGH
            elif materiality_score >= 10:
                topic.materiality_level = MaterialityLevel.MEDIUM
            elif materiality_score >= 5:
                topic.materiality_level = MaterialityLevel.LOW
            else:
                topic.materiality_level = MaterialityLevel.NOT_MATERIAL

            topic.stakeholder_importance = stakeholder_ratings
            assessed_topics.append(topic)

            logger.info(
                f"Material Topic: {topic.topic_name} - "
                f"{topic.materiality_level.value} "
                f"(Score: {materiality_score:.1f})"
            )

        # Sort by materiality
        assessed_topics.sort(
            key=lambda t: (
                ['critical', 'high', 'medium', 'low', 'not_material'].index(t.materiality_level.value),
                -t.business_impact
            )
        )

        self.material_topics = assessed_topics
        return assessed_topics

    def assess_tcfd_risks(self) -> List[TCFDRisk]:
        """
        Assess climate-related risks per TCFD framework

        TCFD requires disclosure of:
        - Physical risks (acute and chronic)
        - Transition risks (policy, technology, market, reputation)
        - Time horizons (short, medium, long-term)
        - Financial impacts
        """

        # Example physical risk
        physical_risk = TCFDRisk(
            risk_id="RISK-PHYS-001",
            risk_type="Physical",
            risk_category="Acute",
            description="Increased frequency of extreme weather events disrupting operations",
            time_horizon="Short",
            likelihood="High",
            magnitude="Medium",
            financial_impact=5_000_000,  # $5M potential impact
            mitigation_strategy="Implement business continuity plans, diversify supply chain",
            metrics=["operational_downtime_hours", "supply_chain_disruption_days"]
        )
        self.tcfd_risks.append(physical_risk)

        # Example transition risk
        transition_risk = TCFDRisk(
            risk_id="RISK-TRANS-001",
            risk_type="Transition",
            risk_category="Policy",
            description="Carbon pricing mechanisms increasing operational costs",
            time_horizon="Medium",
            likelihood="High",
            magnitude="High",
            financial_impact=15_000_000,  # $15M potential impact
            mitigation_strategy="Invest in renewable energy, improve energy efficiency",
            metrics=["carbon_price_exposure", "emissions_intensity"]
        )
        self.tcfd_risks.append(transition_risk)

        logger.info(f"Assessed {len(self.tcfd_risks)} TCFD climate risks")
        return self.tcfd_risks

    def track_science_based_target(self, target: ScienceBasedTarget) -> Dict:
        """
        Track progress toward science-based target

        Returns:
            Progress metrics
        """

        # This would integrate with carbon accounting system
        # For demonstration, using simplified calculation

        current_year = datetime.now().year
        years_elapsed = current_year - target.baseline_year
        years_total = target.target_year - target.baseline_year

        # Linear progress expectation
        expected_reduction_percent = (
            target.target_reduction_percent * years_elapsed / years_total
        )

        # Simulate current emissions (in production, pull from carbon system)
        current_emissions_mt = target.baseline_emissions_mt * 0.9  # 10% reduction

        actual_reduction_percent = (
            (target.baseline_emissions_mt - current_emissions_mt) /
            target.baseline_emissions_mt * 100
        )

        on_track = actual_reduction_percent >= expected_reduction_percent

        progress = {
            'target_id': target.target_id,
            'target_description': target.target_description,
            'baseline_year': target.baseline_year,
            'baseline_emissions_mt': target.baseline_emissions_mt,
            'target_year': target.target_year,
            'target_reduction_percent': target.target_reduction_percent,
            'current_year': current_year,
            'current_emissions_mt': current_emissions_mt,
            'actual_reduction_percent': actual_reduction_percent,
            'expected_reduction_percent': expected_reduction_percent,
            'on_track': on_track,
            'pathway': target.pathway
        }

        return progress

    def generate_cdp_climate_response(self, year: int) -> Dict:
        """
        Generate CDP Climate Change questionnaire response

        CDP has 12 modules:
        0. Introduction
        1. Governance
        2. Risks and opportunities
        3. Business strategy
        4. Targets and performance
        5. Emissions methodology
        6. Emissions data (Scope 1, 2, 3)
        7. Emissions breakdown
        8. Energy
        9. Additional metrics
        10. Verification
        11. Carbon pricing
        12. Engagement
        """

        # Collect relevant metrics
        emissions_metrics = [
            m for m in self.metrics
            if 'emissions' in m.metric_name.lower() and m.reporting_period == str(year)
        ]

        response = {
            'reporting_year': year,
            'organization': self.organization_name,
            'response_status': 'complete',
            'modules': {
                'governance': {
                    'board_oversight': True,
                    'management_responsibility': True,
                    'climate_related_incentives': True
                },
                'risks_opportunities': {
                    'risks_assessed': len(self.tcfd_risks),
                    'transition_risks': len([r for r in self.tcfd_risks if r.risk_type == "Transition"]),
                    'physical_risks': len([r for r in self.tcfd_risks if r.risk_type == "Physical"])
                },
                'targets': {
                    'science_based_targets': len(self.science_based_targets),
                    'sbti_approved': any(t.approved_by_sbti for t in self.science_based_targets)
                },
                'emissions': {
                    'scope_1_mt': sum(m.value for m in emissions_metrics if 'scope 1' in m.metric_name.lower()),
                    'scope_2_mt': sum(m.value for m in emissions_metrics if 'scope 2' in m.metric_name.lower()),
                    'scope_3_mt': sum(m.value for m in emissions_metrics if 'scope 3' in m.metric_name.lower())
                }
            }
        }

        logger.info(f"Generated CDP Climate response for {year}")
        return response

    def generate_tcfd_report(self, year: int) -> Dict:
        """
        Generate TCFD report structure

        TCFD has 4 pillars:
        1. Governance
        2. Strategy
        3. Risk Management
        4. Metrics and Targets
        """

        report = {
            'reporting_year': year,
            'organization': self.organization_name,
            'pillars': {
                'governance': {
                    'board_oversight': "Board reviews climate risks quarterly",
                    'management_role': "Chief Sustainability Officer leads climate strategy"
                },
                'strategy': {
                    'climate_risks': [
                        {
                            'description': r.description,
                            'type': r.risk_type,
                            'time_horizon': r.time_horizon,
                            'financial_impact': r.financial_impact
                        }
                        for r in self.tcfd_risks
                    ],
                    'scenario_analysis': "Analyzed 1.5C, 2C, and 4C scenarios"
                },
                'risk_management': {
                    'identification_process': "Annual climate risk assessment",
                    'integration': "Integrated into enterprise risk management"
                },
                'metrics_targets': {
                    'ghg_emissions': "Report Scope 1, 2, 3 annually",
                    'targets': [
                        {
                            'description': t.target_description,
                            'pathway': t.pathway,
                            'reduction': f"{t.target_reduction_percent}% by {t.target_year}"
                        }
                        for t in self.science_based_targets
                    ]
                }
            }
        }

        logger.info(f"Generated TCFD report for {year}")
        return report

    def calculate_esg_score(self) -> ESGScore:
        """
        Calculate internal ESG score

        Real ESG ratings come from providers like:
        - MSCI ESG Ratings
        - Sustainalytics
        - CDP
        - ISS ESG
        """

        # Simplified scoring (production would be more sophisticated)

        # Environmental score (based on emissions, energy, waste metrics)
        env_metrics = [m for m in self.metrics if m.category == 'E']
        environmental_score = 70.0  # Placeholder

        # Social score (based on diversity, safety, community metrics)
        social_metrics = [m for m in self.metrics if m.category == 'S']
        social_score = 75.0  # Placeholder

        # Governance score (based on board diversity, ethics, compliance)
        gov_metrics = [m for m in self.metrics if m.category == 'G']
        governance_score = 80.0  # Placeholder

        # Overall score (weighted average)
        overall_score = (
            environmental_score * 0.4 +
            social_score * 0.3 +
            governance_score * 0.3
        )

        # Convert to rating (simplified MSCI-like scale)
        if overall_score >= 85:
            rating = "AAA"
        elif overall_score >= 80:
            rating = "AA"
        elif overall_score >= 75:
            rating = "A"
        elif overall_score >= 70:
            rating = "BBB"
        else:
            rating = "BB"

        score = ESGScore(
            organization_id=self.organization_id,
            score_date=datetime.now(),
            provider="Internal Assessment",
            overall_score=overall_score,
            environmental_score=environmental_score,
            social_score=social_score,
            governance_score=governance_score,
            rating=rating
        )

        self.esg_scores.append(score)

        logger.info(
            f"ESG Score: {rating} (Overall: {overall_score:.1f}, "
            f"E: {environmental_score:.1f}, S: {social_score:.1f}, G: {governance_score:.1f})"
        )

        return score


# Example usage
def main():
    """Example usage of ESG Reporting Platform"""

    # Initialize platform
    esg_platform = ESGReportingPlatform(
        organization_id="ORG-001",
        organization_name="Sustainable Corp Inc."
    )

    print(f"\n=== ESG Reporting Platform ===")
    print(f"Organization: {esg_platform.organization_name}")

    # Define material topics
    topics = [
        MaterialityTopic(
            topic_id="TOPIC-001",
            topic_name="Climate Change Mitigation",
            description="GHG emissions reduction and climate action",
            category="Environmental",
            materiality_level=MaterialityLevel.HIGH,
            business_impact=5,
            frameworks=[ReportingFramework.CDP_CLIMATE, ReportingFramework.TCFD]
        ),
        MaterialityTopic(
            topic_id="TOPIC-002",
            topic_name="Employee Health & Safety",
            description="Workplace safety and employee wellbeing",
            category="Social",
            materiality_level=MaterialityLevel.HIGH,
            business_impact=5,
            frameworks=[ReportingFramework.GRI, ReportingFramework.SASB]
        ),
        MaterialityTopic(
            topic_id="TOPIC-003",
            topic_name="Board Diversity",
            description="Diversity and inclusion on board of directors",
            category="Governance",
            materiality_level=MaterialityLevel.MEDIUM,
            business_impact=4,
            frameworks=[ReportingFramework.GRI]
        )
    ]

    # Stakeholder input
    stakeholder_input = {
        "TOPIC-001": {
            StakeholderType.INVESTORS: 5,
            StakeholderType.REGULATORS: 5,
            StakeholderType.CUSTOMERS: 4,
            StakeholderType.EMPLOYEES: 4
        },
        "TOPIC-002": {
            StakeholderType.EMPLOYEES: 5,
            StakeholderType.REGULATORS: 5,
            StakeholderType.CUSTOMERS: 3
        },
        "TOPIC-003": {
            StakeholderType.INVESTORS: 4,
            StakeholderType.EMPLOYEES: 4,
            StakeholderType.CUSTOMERS: 3
        }
    }

    # Conduct materiality assessment
    print(f"\n=== Materiality Assessment ===")
    material_topics = esg_platform.conduct_materiality_assessment(topics, stakeholder_input)

    for topic in material_topics[:3]:
        print(f"{topic.topic_name}: {topic.materiality_level.value}")

    # Assess TCFD risks
    print(f"\n=== TCFD Climate Risk Assessment ===")
    risks = esg_platform.assess_tcfd_risks()

    for risk in risks:
        print(
            f"{risk.risk_type} Risk: {risk.description} "
            f"(Likelihood: {risk.likelihood}, Impact: ${risk.financial_impact:,.0f})"
        )

    # Set science-based target
    sbt = ScienceBasedTarget(
        target_id="SBT-001",
        target_description="Reduce absolute Scope 1 and 2 GHG emissions 50% by 2030 from a 2020 base year",
        baseline_year=2020,
        target_year=2030,
        baseline_emissions_mt=10000.0,
        target_reduction_percent=50.0,
        target_emissions_mt=5000.0,
        scope_coverage=["Scope 1", "Scope 2"],
        pathway="1.5C",
        target_type="Absolute",
        approved_by_sbti=True
    )

    esg_platform.science_based_targets.append(sbt)

    # Track progress
    print(f"\n=== Science Based Target Progress ===")
    progress = esg_platform.track_science_based_target(sbt)
    print(f"Target: {progress['target_description']}")
    print(f"Baseline ({progress['baseline_year']}): {progress['baseline_emissions_mt']:,.0f} mt CO2e")
    print(f"Current ({progress['current_year']}): {progress['current_emissions_mt']:,.0f} mt CO2e")
    print(f"Progress: {progress['actual_reduction_percent']:.1f}% (Expected: {progress['expected_reduction_percent']:.1f}%)")
    print(f"On Track: {'✓ Yes' if progress['on_track'] else '✗ No'}")

    # Calculate ESG score
    print(f"\n=== ESG Score ===")
    score = esg_platform.calculate_esg_score()
    print(f"Rating: {score.rating}")
    print(f"Overall Score: {score.overall_score:.1f}")
    print(f"  Environmental: {score.environmental_score:.1f}")
    print(f"  Social: {score.social_score:.1f}")
    print(f"  Governance: {score.governance_score:.1f}")

    # Generate CDP response
    cdp_response = esg_platform.generate_cdp_climate_response(2024)
    print(f"\n=== CDP Climate Response Generated ===")
    print(f"Reporting Year: {cdp_response['reporting_year']}")
    print(f"Status: {cdp_response['response_status']}")

if __name__ == "__main__":
    main()
```

## Key Frameworks Comparison

### CDP vs TCFD vs GRI vs SASB

| Aspect | CDP | TCFD | GRI | SASB |
|--------|-----|------|-----|------|
| **Focus** | Environmental disclosure | Climate financial risk | Broad sustainability | Investor-focused ESG |
| **Audience** | Investors, companies | Financial sector | All stakeholders | Investors |
| **Scope** | Climate, water, forests | Climate-related risks | All sustainability topics | Industry-specific |
| **Mandatory** | Voluntary | Increasingly mandatory | Voluntary | Voluntary |

## Key Performance Indicators

### Reporting Quality
- **Disclosure Score**: % of requested data points disclosed
- **Response Time**: Days to complete disclosure
- **Third-Party Verification**: % of metrics verified
- **Stakeholder Satisfaction**: Survey ratings

### ESG Performance
- **CDP Score**: A, A-, B, B-, C, C-, D, D-
- **MSCI ESG Rating**: AAA to CCC
- **Carbon Intensity**: kg CO2e per unit output
- **Board Diversity**: % diverse board members

## Industry Resources

### Reporting Platforms
- [CDP](https://www.cdp.net/)
- [TCFD](https://www.fsb-tcfd.org/)
- [GRI](https://www.globalreporting.org/)
- [SASB](https://www.sasb.org/)
- [Science Based Targets initiative](https://sciencebasedtargets.org/)

### Rating Providers
- **MSCI ESG Ratings**
- **Sustainalytics**
- **ISS ESG**
- **CDP Ratings**

## Conclusion

Sustainability Reporting & ESG is essential for demonstrating corporate responsibility, managing climate risks, and attracting sustainable investment. Production systems must integrate data from across the organization, ensure accuracy and consistency, and generate reports compliant with multiple frameworks. The trend is toward mandatory climate disclosure and increased scrutiny of ESG claims.
