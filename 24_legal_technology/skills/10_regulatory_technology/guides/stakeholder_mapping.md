# Stakeholder Mapping Guide

## Table of Contents
1. [Executive Overview](#executive-overview)
2. [Stakeholder Identification](#stakeholder-identification)
3. [Analysis Frameworks](#analysis-frameworks)
4. [Influence Mapping](#influence-mapping)
5. [Interest Assessment](#interest-assessment)
6. [Engagement Strategy Development](#engagement-strategy-development)
7. [Collaboration Systems](#collaboration-systems)
8. [Monitoring and Updates](#monitoring-and-updates)
9. [Implementation Workflow](#implementation-workflow)
10. [Best Practices](#best-practices)

## Executive Overview

Stakeholder mapping is the systematic process of identifying, analyzing, and developing strategies for engaging individuals and organizations that affect or are affected by regulatory and legislative issues. Effective stakeholder mapping enables organizations to:

- Identify all relevant parties to engage on policy issues
- Understand stakeholder positions, interests, and influence
- Develop targeted engagement strategies
- Build coalitions with aligned stakeholders
- Anticipate opposition and develop responses
- Prioritize engagement resources
- Track engagement effectiveness

### Key Objectives
- Comprehensive identification of all stakeholders (target: 95%+ coverage)
- Accurate assessment of influence and interests
- Data-driven engagement prioritization
- Real-time coalition tracking
- Predictive analytics for stakeholder behavior
- ROI measurement for engagement activities

### Success Metrics
- Stakeholder coverage: 95%+ of relevant parties identified
- Prediction accuracy: 80%+ for stakeholder positions
- Coalition effectiveness: 70%+ coalition support rate for key issues
- Engagement ROI: Positive impact on policy outcomes
- Data quality: 90%+ accuracy of stakeholder data

## Stakeholder Identification

### Stakeholder Categories and Classification

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class StakeholderType(Enum):
    """Primary stakeholder categories"""

    # Government entities
    GOVERNMENT_OFFICIAL = "government_official"
    GOVERNMENT_AGENCY = "government_agency"
    LEGISLATIVE_STAFF = "legislative_staff"

    # Business entities
    COMPETITOR = "competitor"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    BUSINESS_ASSOCIATION = "business_association"

    # Advocacy organizations
    ADVOCACY_GROUP = "advocacy_group"
    INDUSTRY_ASSOCIATION = "industry_association"
    TRADE_ASSOCIATION = "trade_association"
    ENVIRONMENTAL_GROUP = "environmental_group"
    CONSUMER_ADVOCATE = "consumer_advocate"

    # Academic/Research
    RESEARCH_INSTITUTE = "research_institute"
    UNIVERSITY = "university"
    THINK_TANK = "think_tank"

    # Public entities
    MEDIA = "media"
    PUBLIC_INTEREST_GROUP = "public_interest_group"
    LABOR_UNION = "labor_union"

    # Other
    CONSULTANT = "consultant"
    LAW_FIRM = "law_firm"
    COMMUNITY_ORGANIZATION = "community_organization"

class StakeholderRole(Enum):
    """Role in policy process"""

    DECISION_MAKER = "decision_maker"  # Has voting or approval power
    INFLUENCER = "influencer"  # Influences decision makers
    SUPPORTER = "supporter"  # Advocates for position
    OPPONENT = "opponent"  # Advocates against position
    NEUTRAL = "neutral"  # No clear position
    STAKEHOLDER = "stakeholder"  # Affected but not decision maker
    IMPLEMENTER = "implementer"  # Implements policy decisions

class StakeholderStatus(Enum):
    """Engagement status"""

    UNAWARE = "unaware"  # Unaware of issue
    AWARE = "aware"  # Aware but uncommitted
    ENGAGED = "engaged"  # Actively engaged
    ALLIED = "allied"  # Aligned with position
    OPPOSED = "opposed"  # Opposed to position
    NEUTRAL_OBSERVED = "neutral_observed"  # Observing, no stance

@dataclass
class Stakeholder:
    """Represents a stakeholder"""

    stakeholder_id: str
    name: str
    organization: str
    stakeholder_type: StakeholderType
    location: str  # Geographic location
    contact_information: Dict

    # Relationship to issue
    issue_id: str
    current_role: StakeholderRole
    current_status: StakeholderStatus

    # Interests and position
    primary_interests: List[str]
    position_statement: Optional[str]
    stated_position: str  # 'support', 'oppose', 'monitor', 'neutral'

    # Characteristics
    influence_level: int  # 1-10
    resource_level: int  # 1-10 (funding, staff, etc.)
    media_presence: int  # 1-10
    coalition_likelihood: float  # 0-1

    # Relationships
    allies: List[str]  # Stakeholder IDs
    opponents: List[str]  # Stakeholder IDs
    neutral_relationships: List[str]

    # Engagement history
    engagement_history: List['EngagementRecord']
    last_contact_date: Optional[datetime]
    engagement_level: str  # 'high', 'medium', 'low'

    # Data management
    data_quality_score: float
    created_at: datetime
    last_updated: datetime
    owner: str

class StakeholderIdentificationEngine:
    """Identifies stakeholders for policy issues"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.identification_patterns = self._load_patterns()

    def identify_stakeholders(self, issue_id: str) -> List[Stakeholder]:
        """Identify all stakeholders for an issue"""

        issue = self.db.query_issue(issue_id)
        stakeholders = []

        # Government stakeholders
        government_stakeholders = self._identify_government_stakeholders(issue)
        stakeholders.extend(government_stakeholders)

        # Business stakeholders
        business_stakeholders = self._identify_business_stakeholders(issue)
        stakeholders.extend(business_stakeholders)

        # Advocacy stakeholders
        advocacy_stakeholders = self._identify_advocacy_stakeholders(issue)
        stakeholders.extend(advocacy_stakeholders)

        # Academic/Research stakeholders
        academic_stakeholders = self._identify_academic_stakeholders(issue)
        stakeholders.extend(academic_stakeholders)

        # Media stakeholders
        media_stakeholders = self._identify_media_stakeholders(issue)
        stakeholders.extend(media_stakeholders)

        return stakeholders

    def _identify_government_stakeholders(self, issue: Dict) -> List[Stakeholder]:
        """Identify government entity stakeholders"""

        stakeholders = []
        jurisdiction = issue.get('jurisdiction', 'federal')

        # Find committees with jurisdiction
        committees = self.db.query("""
            SELECT * FROM committees
            WHERE jurisdiction = %s
            AND policy_area IN (%s)
        """, [jurisdiction, ','.join(issue.get('policy_areas', []))])

        for committee in committees:
            # Add committee chair as stakeholder
            chair = self.db.query_one(
                "SELECT * FROM government_officials WHERE committee_id = %s AND role = 'Chair'",
                [committee['committee_id']]
            )

            if chair:
                stakeholders.append(Stakeholder(
                    stakeholder_id=f"GOV-{chair['official_id']}",
                    name=f"{chair['first_name']} {chair['last_name']}",
                    organization=committee['committee_name'],
                    stakeholder_type=StakeholderType.GOVERNMENT_OFFICIAL,
                    location=chair.get('jurisdiction'),
                    contact_information=self._extract_contact_info(chair),
                    issue_id=issue['issue_id'],
                    current_role=StakeholderRole.DECISION_MAKER,
                    current_status=StakeholderStatus.AWARE,
                    primary_interests=committee.get('policy_areas', []),
                    stated_position='neutral',
                    influence_level=9,
                    resource_level=10,
                    media_presence=6,
                    coalition_likelihood=0.5,
                    allies=[],
                    opponents=[],
                    neutral_relationships=[],
                    engagement_history=[],
                    last_contact_date=None,
                    engagement_level='low',
                    data_quality_score=0.95,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    owner='Identification Engine'
                ))

        return stakeholders

    def _identify_business_stakeholders(self, issue: Dict) -> List[Stakeholder]:
        """Identify business entity stakeholders"""

        stakeholders = []

        # Find companies in affected industries
        industries = issue.get('affected_industries', [])

        if industries:
            companies = self.db.query(f"""
                SELECT DISTINCT c.* FROM companies c
                WHERE c.primary_industry IN ({','.join(['%s'] * len(industries))})
                AND c.headquarters_state = %s
            """, industries + [issue.get('jurisdiction')])

            for company in companies:
                stakeholder = Stakeholder(
                    stakeholder_id=f"BUS-{company['company_id']}",
                    name=company['company_name'],
                    organization=company['company_name'],
                    stakeholder_type=StakeholderType.CUSTOMER
                        if issue.get('affects_customers') else StakeholderType.COMPETITOR,
                    location=company.get('headquarters_state'),
                    contact_information=self._extract_contact_info(company),
                    issue_id=issue['issue_id'],
                    current_role=StakeholderRole.STAKEHOLDER,
                    current_status=StakeholderStatus.UNAWARE,
                    primary_interests=[issue.get('policy_area', '')],
                    stated_position='neutral',
                    influence_level=self._assess_company_influence(company),
                    resource_level=self._assess_company_resources(company),
                    media_presence=self._assess_media_presence(company),
                    coalition_likelihood=0.6,
                    allies=[],
                    opponents=[],
                    neutral_relationships=[],
                    engagement_history=[],
                    last_contact_date=None,
                    engagement_level='low',
                    data_quality_score=0.85,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    owner='Identification Engine'
                )
                stakeholders.append(stakeholder)

        return stakeholders

    def _identify_advocacy_stakeholders(self, issue: Dict) -> List[Stakeholder]:
        """Identify advocacy organization stakeholders"""

        stakeholders = []

        # Find relevant advocacy groups
        advocacy_groups = self.db.query("""
            SELECT * FROM advocacy_organizations
            WHERE policy_focus IN (%s)
            ORDER BY influence_score DESC
            LIMIT 20
        """, [','.join(issue.get('policy_areas', []))])

        for group in advocacy_groups:
            stakeholder = Stakeholder(
                stakeholder_id=f"ADV-{group['organization_id']}",
                name=group['organization_name'],
                organization=group['organization_name'],
                stakeholder_type=self._classify_advocacy_type(group),
                location=group.get('headquarters_state'),
                contact_information=self._extract_contact_info(group),
                issue_id=issue['issue_id'],
                current_role=StakeholderRole.INFLUENCER,
                current_status=StakeholderStatus.AWARE,
                primary_interests=group.get('policy_focus', []),
                stated_position=group.get('typical_position', 'neutral'),
                influence_level=group.get('influence_score', 5),
                resource_level=group.get('funding_level', 5),
                media_presence=group.get('media_presence_score', 5),
                coalition_likelihood=0.7,
                allies=[],
                opponents=[],
                neutral_relationships=[],
                engagement_history=[],
                last_contact_date=None,
                engagement_level='medium',
                data_quality_score=0.90,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                owner='Identification Engine'
            )
            stakeholders.append(stakeholder)

        return stakeholders

    def _load_patterns(self) -> Dict:
        """Load identification patterns from database"""

        return {
            'government': self._government_identification_rules(),
            'business': self._business_identification_rules(),
            'advocacy': self._advocacy_identification_rules()
        }

    def _government_identification_rules(self) -> Dict:
        """Rules for identifying government stakeholders"""

        return {
            'primary': ['committees_with_jurisdiction', 'regulatory_agencies'],
            'secondary': ['related_committees', 'relevant_staff'],
            'criteria': ['policy_area_match', 'budget_impact', 'constituent_impact']
        }

    def _business_identification_rules(self) -> Dict:
        """Rules for identifying business stakeholders"""

        return {
            'primary': ['directly_affected_industries', 'supply_chain_impact'],
            'secondary': ['indirect_impacts', 'competitors'],
            'criteria': ['revenue_impact', 'compliance_cost', 'market_share_impact']
        }

    def _advocacy_identification_rules(self) -> Dict:
        """Rules for identifying advocacy stakeholders"""

        return {
            'primary': ['policy_area_focus', 'constituent_alignment'],
            'secondary': ['adjacent_issues', 'coalition_history'],
            'criteria': ['mission_relevance', 'track_record', 'resources']
        }
```

## Analysis Frameworks

### Stakeholder Interest and Influence Matrix

```python
import math

class StakeholderAnalyzer:
    """Analyzes stakeholder positions and influence"""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_power_interest_matrix(self, stakeholders: List[Stakeholder]) -> Dict:
        """Create power/interest matrix for stakeholders"""

        matrix = {
            'high_power_high_interest': [],
            'high_power_low_interest': [],
            'low_power_high_interest': [],
            'low_power_low_interest': [],
            'metadata': {}
        }

        for stakeholder in stakeholders:
            # Estimate influence (power)
            power_score = self._calculate_power_score(stakeholder)

            # Estimate interest based on direct stakes
            interest_score = self._calculate_interest_score(stakeholder)

            # Categorize
            if power_score >= 0.5 and interest_score >= 0.5:
                category = 'high_power_high_interest'
            elif power_score >= 0.5 and interest_score < 0.5:
                category = 'high_power_low_interest'
            elif power_score < 0.5 and interest_score >= 0.5:
                category = 'low_power_high_interest'
            else:
                category = 'low_power_low_interest'

            matrix[category].append({
                'stakeholder_id': stakeholder.stakeholder_id,
                'name': stakeholder.name,
                'power_score': power_score,
                'interest_score': interest_score,
                'recommended_strategy': self._recommend_strategy(power_score, interest_score)
            })

        # Calculate metadata
        matrix['metadata'] = {
            'total_stakeholders': len(stakeholders),
            'high_power_high_interest_count': len(matrix['high_power_high_interest']),
            'distribution': {
                'high_power_high_interest': len(matrix['high_power_high_interest']) / len(stakeholders),
                'high_power_low_interest': len(matrix['high_power_low_interest']) / len(stakeholders),
                'low_power_high_interest': len(matrix['low_power_high_interest']) / len(stakeholders),
                'low_power_low_interest': len(matrix['low_power_low_interest']) / len(stakeholders)
            }
        }

        return matrix

    def _calculate_power_score(self, stakeholder: Stakeholder) -> float:
        """Calculate power/influence score for stakeholder"""

        # Components of influence
        formal_authority = self._assess_formal_authority(stakeholder)  # 0-1
        resources = stakeholder.resource_level / 10  # 0-1
        media_influence = stakeholder.media_presence / 10  # 0-1
        coalition_strength = len(stakeholder.allies) / 10  # 0-1

        # Weighted calculation
        weights = {
            'formal_authority': 0.4,
            'resources': 0.25,
            'media_influence': 0.2,
            'coalition_strength': 0.15
        }

        power_score = (
            formal_authority * weights['formal_authority'] +
            resources * weights['resources'] +
            media_influence * weights['media_influence'] +
            coalition_strength * weights['coalition_strength']
        )

        return min(1.0, max(0.0, power_score))

    def _calculate_interest_score(self, stakeholder: Stakeholder) -> float:
        """Calculate interest/stakes score"""

        # Determine financial impact
        financial_impact = self._estimate_financial_impact(stakeholder)  # 0-1

        # Determine mission alignment
        mission_alignment = self._estimate_mission_alignment(stakeholder)  # 0-1

        # Determine visibility to constituency
        visibility = self._estimate_constituency_visibility(stakeholder)  # 0-1

        # Weighted calculation
        interest_score = (
            financial_impact * 0.4 +
            mission_alignment * 0.4 +
            visibility * 0.2
        )

        return min(1.0, max(0.0, interest_score))

    def _assess_formal_authority(self, stakeholder: Stakeholder) -> float:
        """Assess formal decision-making authority"""

        if stakeholder.current_role == StakeholderRole.DECISION_MAKER:
            return 0.9
        elif stakeholder.current_role == StakeholderRole.INFLUENCER:
            return 0.7
        elif stakeholder.current_role == StakeholderRole.SUPPORTER:
            return 0.5
        else:
            return 0.2

    def _recommend_strategy(self, power_score: float, interest_score: float) -> str:
        """Recommend engagement strategy based on power/interest"""

        if power_score >= 0.5 and interest_score >= 0.5:
            return "Manage Closely - Key Stakeholder"
        elif power_score >= 0.5 and interest_score < 0.5:
            return "Keep Satisfied - Monitor for increased interest"
        elif power_score < 0.5 and interest_score >= 0.5:
            return "Keep Informed - Build support base"
        else:
            return "Monitor - May become relevant"

    def predict_stakeholder_position(self, stakeholder: Stakeholder,
                                    issue: Dict) -> Dict:
        """Predict stakeholder's likely position on issue"""

        prediction = {
            'stakeholder_id': stakeholder.stakeholder_id,
            'issue_id': issue['issue_id'],
            'predicted_position': '',
            'confidence': 0.0,
            'reasoning': [],
            'key_factors': []
        }

        # Analyze based on similar past positions
        similar_issues = self._find_similar_issues(issue)
        past_positions = self._get_past_positions(stakeholder, similar_issues)

        if past_positions:
            # Use historical pattern
            most_common = max(set(past_positions), key=past_positions.count)
            prediction['predicted_position'] = most_common
            prediction['confidence'] = len(past_positions) / len(similar_issues)
            prediction['reasoning'].append(f"Historical pattern on similar issues")

        # Analyze based on stated interests
        interest_alignment = self._assess_interest_alignment(stakeholder, issue)

        if interest_alignment > 0.7:
            prediction['predicted_position'] = 'support'
            prediction['confidence'] = max(prediction['confidence'], 0.8)
            prediction['key_factors'].append('Strong interest alignment')

        elif interest_alignment < 0.3:
            prediction['predicted_position'] = 'oppose'
            prediction['confidence'] = max(prediction['confidence'], 0.75)
            prediction['key_factors'].append('Interest misalignment')

        else:
            prediction['predicted_position'] = 'neutral'
            prediction['confidence'] = 0.5
            prediction['key_factors'].append('Mixed interests')

        return prediction

    def _find_similar_issues(self, issue: Dict) -> List[Dict]:
        """Find issues similar to given issue"""

        return self.db.query("""
            SELECT * FROM issues
            WHERE policy_area = %s
            AND issue_id != %s
            AND resolved = TRUE
            ORDER BY resolution_date DESC
            LIMIT 5
        """, [issue['policy_area'], issue['issue_id']])

    def _get_past_positions(self, stakeholder: Stakeholder,
                           issues: List[Dict]) -> List[str]:
        """Get stakeholder's past positions on similar issues"""

        positions = []

        for issue in issues:
            past_engagement = self.db.query_one("""
                SELECT stated_position FROM stakeholder_engagements
                WHERE stakeholder_id = %s AND issue_id = %s
            """, [stakeholder.stakeholder_id, issue['issue_id']])

            if past_engagement:
                positions.append(past_engagement['stated_position'])

        return positions

    def _assess_interest_alignment(self, stakeholder: Stakeholder,
                                  issue: Dict) -> float:
        """Assess how much stakeholder's interests align with issue"""

        alignment_score = 0.0
        matches = 0

        for interest in stakeholder.primary_interests:
            if interest in issue.get('policy_areas', []):
                alignment_score += 0.5
                matches += 1

            # Check for related interests
            if self._interests_related(interest, issue.get('policy_areas', [])):
                alignment_score += 0.3
                matches += 1

        if matches == 0:
            return 0.0

        return min(1.0, alignment_score / matches)

    def _interests_related(self, interest: str, policy_areas: List[str]) -> bool:
        """Check if interests are related"""

        # Would use relationship graph in real implementation
        related_pairs = {
            'environment': ['energy', 'sustainability', 'climate'],
            'labor': ['employment', 'worker_rights', 'wages'],
            'consumer': ['privacy', 'competition', 'quality']
        }

        for area in policy_areas:
            if interest in related_pairs.get(area, []) or area in related_pairs.get(interest, []):
                return True

        return False
```

## Interest Assessment

### Detailed Interest Analysis

```python
class InterestAssessment:
    """Assesses and tracks stakeholder interests"""

    def __init__(self, db_connection):
        self.db = db_connection

    def conduct_interest_analysis(self, stakeholder: Stakeholder,
                                 issue: Dict) -> Dict:
        """Conduct detailed analysis of stakeholder's interests"""

        analysis = {
            'stakeholder_id': stakeholder.stakeholder_id,
            'issue_id': issue['issue_id'],
            'analysis_date': datetime.now(),
            'interest_dimensions': {},
            'overall_interest_level': 0.0,
            'likely_position': '',
            'engagement_potential': ''
        }

        # Financial interests
        financial = self._analyze_financial_interests(stakeholder, issue)
        analysis['interest_dimensions']['financial'] = financial

        # Regulatory interests
        regulatory = self._analyze_regulatory_interests(stakeholder, issue)
        analysis['interest_dimensions']['regulatory'] = regulatory

        # Mission/values interests
        values = self._analyze_values_interests(stakeholder, issue)
        analysis['interest_dimensions']['values'] = values

        # Political interests
        political = self._analyze_political_interests(stakeholder, issue)
        analysis['interest_dimensions']['political'] = political

        # Calculate overall interest
        interest_weights = {
            'financial': 0.35,
            'regulatory': 0.3,
            'values': 0.2,
            'political': 0.15
        }

        overall = (
            financial['score'] * interest_weights['financial'] +
            regulatory['score'] * interest_weights['regulatory'] +
            values['score'] * interest_weights['values'] +
            political['score'] * interest_weights['political']
        )

        analysis['overall_interest_level'] = overall

        # Determine engagement potential
        if overall > 0.75:
            analysis['engagement_potential'] = 'high'
        elif overall > 0.5:
            analysis['engagement_potential'] = 'medium'
        else:
            analysis['engagement_potential'] = 'low'

        return analysis

    def _analyze_financial_interests(self, stakeholder: Stakeholder,
                                    issue: Dict) -> Dict:
        """Analyze financial impacts"""

        return {
            'score': self._estimate_financial_impact(stakeholder, issue),
            'impact_type': 'positive' if issue.get('benefits_alignment') else 'negative',
            'estimated_impact': issue.get('estimated_financial_impact', 'Unknown'),
            'affected_revenue_streams': issue.get('affected_revenue', []),
            'cost_implications': issue.get('cost_implications', [])
        }

    def _analyze_regulatory_interests(self, stakeholder: Stakeholder,
                                     issue: Dict) -> Dict:
        """Analyze regulatory/compliance interests"""

        return {
            'score': self._estimate_regulatory_impact(stakeholder, issue),
            'compliance_burden': issue.get('compliance_burden', 'Unknown'),
            'reporting_requirements': issue.get('new_reporting', []),
            'operational_impact': issue.get('operational_changes', []),
            'timeline': issue.get('implementation_timeline', 'Unknown')
        }

    def _analyze_values_interests(self, stakeholder: Stakeholder,
                                 issue: Dict) -> Dict:
        """Analyze mission/values alignment"""

        return {
            'score': self._estimate_mission_alignment(stakeholder, issue),
            'mission_alignment': 'aligned' if self._is_mission_aligned(stakeholder, issue) else 'misaligned',
            'constituencies_affected': issue.get('affected_constituencies', []),
            'values_at_stake': issue.get('values_questions', [])
        }

    def _analyze_political_interests(self, stakeholder: Stakeholder,
                                    issue: Dict) -> Dict:
        """Analyze political interests"""

        return {
            'score': self._estimate_political_interest(stakeholder, issue),
            'coalition_positioning': self._analyze_coalition_position(stakeholder, issue),
            'public_positioning': self._analyze_public_position(stakeholder),
            'election_implications': issue.get('election_year', False)
        }

    def _estimate_financial_impact(self, stakeholder: Stakeholder,
                                  issue: Dict) -> float:
        """Estimate financial impact on stakeholder"""

        # Would need detailed financial modeling in production
        impact_score = 0.0

        # Higher impact if directly in affected industry
        if issue.get('affected_industries') and \
           stakeholder.organization in issue.get('affected_industries', []):
            impact_score += 0.6

        # Higher impact if major cost/revenue implications
        if issue.get('estimated_cost', 0) > 1000000:  # $1M+
            impact_score += 0.3

        return min(1.0, impact_score)

    def _estimate_regulatory_impact(self, stakeholder: Stakeholder,
                                   issue: Dict) -> float:
        """Estimate regulatory compliance impact"""

        impact_score = 0.0

        # Higher impact if substantial new requirements
        if len(issue.get('new_reporting', [])) > 5:
            impact_score += 0.5

        # Higher impact if short implementation timeline
        days_to_compliance = issue.get('days_to_compliance', 365)
        if days_to_compliance < 90:
            impact_score += 0.4

        return min(1.0, impact_score)

    def _estimate_mission_alignment(self, stakeholder: Stakeholder,
                                   issue: Dict) -> float:
        """Estimate mission/values alignment"""

        alignment_score = 0.0

        # Check stated interests
        for interest in stakeholder.primary_interests:
            if interest in issue.get('policy_areas', []):
                alignment_score += 0.5

        return min(1.0, alignment_score)

    def _is_mission_aligned(self, stakeholder: Stakeholder,
                           issue: Dict) -> bool:
        """Check if issue aligns with stakeholder mission"""

        return self._estimate_mission_alignment(stakeholder, issue) > 0.5
```

## Engagement Strategy Development

### Targeted Engagement Planning

```python
class EngagementStrategy:
    """Develops targeted engagement strategies for stakeholders"""

    def __init__(self, db_connection):
        self.db = db_connection

    def develop_engagement_plan(self, stakeholders: List[Stakeholder],
                               issue: Dict) -> Dict:
        """Develop comprehensive engagement plan"""

        plan = {
            'issue_id': issue['issue_id'],
            'created_at': datetime.now(),
            'engagement_goals': self._define_goals(issue),
            'stakeholder_strategies': {},
            'timeline': self._develop_timeline(issue),
            'resource_allocation': {},
            'success_metrics': self._define_metrics()
        }

        # Develop strategy for each stakeholder
        for stakeholder in stakeholders:
            strategy = self._develop_stakeholder_strategy(stakeholder, issue)
            plan['stakeholder_strategies'][stakeholder.stakeholder_id] = strategy

        # Allocate resources
        plan['resource_allocation'] = self._allocate_resources(
            stakeholders,
            issue,
            plan['stakeholder_strategies']
        )

        return plan

    def _develop_stakeholder_strategy(self, stakeholder: Stakeholder,
                                     issue: Dict) -> Dict:
        """Develop engagement strategy for individual stakeholder"""

        # Assess current position
        predicted_position = self._predict_position(stakeholder, issue)

        # Determine engagement goal
        engagement_goal = self._determine_goal(stakeholder, predicted_position)

        # Select engagement channels
        channels = self._select_channels(stakeholder, engagement_goal)

        # Develop messaging
        messaging = self._develop_messaging(stakeholder, issue, engagement_goal)

        # Set frequency
        frequency = self._determine_contact_frequency(stakeholder, engagement_goal)

        return {
            'stakeholder_id': stakeholder.stakeholder_id,
            'stakeholder_name': stakeholder.name,
            'predicted_position': predicted_position,
            'engagement_goal': engagement_goal,
            'strategy': self._describe_strategy(engagement_goal),
            'channels': channels,
            'messaging': messaging,
            'contact_frequency': frequency,
            'key_contacts': self._identify_key_contacts(stakeholder),
            'success_indicators': self._define_success_indicators(engagement_goal),
            'contingencies': self._develop_contingencies(stakeholder, issue)
        }

    def _determine_goal(self, stakeholder: Stakeholder, predicted_position: str) -> str:
        """Determine engagement goal based on predicted position"""

        if predicted_position == 'support':
            return 'maintain_support'
        elif predicted_position == 'oppose':
            return 'convert_or_neutralize'
        else:
            return 'build_support'

    def _select_channels(self, stakeholder: Stakeholder, goal: str) -> List[str]:
        """Select engagement channels"""

        channels = []

        # Government officials: focus on meetings and briefings
        if stakeholder.stakeholder_type == StakeholderType.GOVERNMENT_OFFICIAL:
            channels = ['office_meeting', 'briefing', 'phone_call', 'email']

        # Advocacy groups: focus on coalition and public messaging
        elif stakeholder.stakeholder_type in [
            StakeholderType.ADVOCACY_GROUP,
            StakeholderType.INDUSTRY_ASSOCIATION
        ]:
            channels = ['meeting', 'coalition', 'social_media', 'event', 'press_release']

        # Media: focus on news and editorial
        elif stakeholder.stakeholder_type == StakeholderType.MEDIA:
            channels = ['press_release', 'media_briefing', 'op_ed', 'interview']

        # Business: focus on direct engagement
        elif stakeholder.stakeholder_type in [
            StakeholderType.COMPETITOR,
            StakeholderType.SUPPLIER,
            StakeholderType.CUSTOMER
        ]:
            channels = ['meeting', 'email', 'industry_event', 'survey']

        return channels

    def _develop_messaging(self, stakeholder: Stakeholder, issue: Dict,
                          goal: str) -> Dict:
        """Develop tailored messaging for stakeholder"""

        base_message = issue.get('organization_position', '')

        # Tailor message based on stakeholder interests
        tailored_messages = {}

        if goal == 'maintain_support':
            tailored_messages['primary'] = self._craft_reinforcement_message(
                stakeholder, issue, base_message
            )

        elif goal == 'convert_or_neutralize':
            tailored_messages['primary'] = self._craft_persuasion_message(
                stakeholder, issue
            )

        else:  # build_support
            tailored_messages['primary'] = self._craft_persuasion_message(
                stakeholder, issue
            )

        # Develop talking points
        tailored_messages['talking_points'] = self._develop_talking_points(
            stakeholder, issue
        )

        # Develop counter-arguments
        tailored_messages['counters'] = self._develop_counter_arguments(
            stakeholder, issue
        )

        return tailored_messages

    def _craft_reinforcement_message(self, stakeholder: Stakeholder,
                                    issue: Dict, base_message: str) -> str:
        """Craft message to reinforce existing support"""

        # Focus on shared values and alignment
        message = f"""
We appreciate your support on {issue['title']}.

This issue aligns with our shared commitment to {stakeholder.primary_interests[0]}.

Key points of alignment:
- {issue.get('key_benefit_1', 'Alignment point 1')}
- {issue.get('key_benefit_2', 'Alignment point 2')}

We look forward to continuing our collaboration.
"""
        return message

    def _craft_persuasion_message(self, stakeholder: Stakeholder,
                                 issue: Dict) -> str:
        """Craft message to persuade or convert"""

        message = f"""
We wanted to discuss {issue['title']} with you.

We believe this issue is relevant to your interests in {stakeholder.primary_interests[0]}.

Specific points of relevance:
- {self._identify_relevant_point(stakeholder, issue, 1)}
- {self._identify_relevant_point(stakeholder, issue, 2)}

We welcome the opportunity to discuss your perspective and concerns.
"""
        return message

    def _determine_contact_frequency(self, stakeholder: Stakeholder,
                                    goal: str) -> str:
        """Determine appropriate contact frequency"""

        # Higher priority stakeholders
        if stakeholder.current_role == StakeholderRole.DECISION_MAKER:
            return 'bi-weekly'

        # Medium priority
        elif stakeholder.current_role in [
            StakeholderRole.INFLUENCER,
            StakeholderRole.SUPPORTER
        ]:
            return 'monthly'

        # Lower priority
        else:
            return 'quarterly'

    def _identify_key_contacts(self, stakeholder: Stakeholder) -> List[Dict]:
        """Identify key individuals to contact within stakeholder organization"""

        if stakeholder.stakeholder_type == StakeholderType.GOVERNMENT_OFFICIAL:
            return [{
                'name': stakeholder.name,
                'title': stakeholder.primary_interests[0],
                'role': 'primary'
            }]

        else:
            # Would query for other key contacts
            return [{
                'name': 'TBD',
                'title': 'Executive Leadership',
                'role': 'primary'
            }]
```

## Monitoring and Updates

### Stakeholder Position Tracking

```python
class StakeholderMonitoring:
    """Monitors stakeholder positions and activities"""

    def __init__(self, db_connection):
        self.db = db_connection

    def update_stakeholder_position(self, stakeholder_id: str, issue_id: str,
                                   position_update: Dict) -> None:
        """Update stakeholder's position on an issue"""

        update_record = {
            'stakeholder_id': stakeholder_id,
            'issue_id': issue_id,
            'previous_position': self._get_current_position(stakeholder_id, issue_id),
            'new_position': position_update.get('position'),
            'update_date': datetime.now(),
            'source': position_update.get('source', 'unknown'),
            'confidence': position_update.get('confidence', 0.5),
            'evidence': position_update.get('evidence', []),
            'change_reason': position_update.get('reason', ''),
            'updated_by': position_update.get('updated_by', 'System')
        }

        # Store position update
        self.db.insert_position_update(update_record)

        # Update stakeholder record
        self.db.update_stakeholder(stakeholder_id, {
            'stated_position': update_record['new_position'],
            'last_updated': datetime.now()
        })

        # Notify relevant parties if major change
        if update_record['previous_position'] != update_record['new_position']:
            self._notify_stakeholder_change(update_record)

    def track_engagement_activity(self, activity: Dict) -> str:
        """Track engagement activity with stakeholder"""

        engagement_record = {
            'engagement_id': self._generate_id(),
            'stakeholder_id': activity.get('stakeholder_id'),
            'issue_id': activity.get('issue_id'),
            'activity_type': activity.get('activity_type'),  # 'meeting', 'call', 'email'
            'activity_date': activity.get('date', datetime.now()),
            'duration_minutes': activity.get('duration', 30),
            'participants_org': activity.get('org_participants', []),
            'participants_stakeholder': activity.get('stakeholder_participants', []),
            'topics': activity.get('topics', []),
            'outcomes': activity.get('outcomes', []),
            'next_steps': activity.get('next_steps', []),
            'sentiment': activity.get('sentiment', 'neutral'),
            'notes': activity.get('notes', ''),
            'follow_up_required': activity.get('follow_up', False),
            'recorded_by': activity.get('recorded_by', 'Unknown'),
            'created_at': datetime.now()
        }

        self.db.insert_engagement(engagement_record)

        return engagement_record['engagement_id']

    def generate_stakeholder_scorecard(self, stakeholder_id: str,
                                      issue_id: str) -> Dict:
        """Generate scorecard of stakeholder engagement"""

        scorecard = {
            'stakeholder_id': stakeholder_id,
            'issue_id': issue_id,
            'generated_at': datetime.now(),
            'engagement_metrics': {},
            'position_strength': 0.0,
            'engagement_effectiveness': 0.0,
            'recommendations': []
        }

        # Get all engagement activities
        activities = self.db.query("""
            SELECT * FROM engagement_activities
            WHERE stakeholder_id = %s AND issue_id = %s
            ORDER BY activity_date DESC
        """, [stakeholder_id, issue_id])

        # Calculate metrics
        scorecard['engagement_metrics'] = {
            'total_engagements': len(activities),
            'last_engagement': activities[0]['activity_date'] if activities else None,
            'engagement_frequency': self._calculate_frequency(activities),
            'average_sentiment': self._calculate_avg_sentiment(activities),
            'positive_engagements': len([a for a in activities if a['sentiment'] == 'positive']),
            'neutral_engagements': len([a for a in activities if a['sentiment'] == 'neutral']),
            'negative_engagements': len([a for a in activities if a['sentiment'] == 'negative'])
        }

        # Assess position strength
        current_position = self._get_current_position(stakeholder_id, issue_id)
        position_changes = self._track_position_changes(stakeholder_id, issue_id)

        scorecard['position_strength'] = self._assess_position_strength(
            current_position,
            position_changes,
            activities
        )

        # Calculate engagement effectiveness
        scorecard['engagement_effectiveness'] = self._calculate_engagement_effectiveness(
            activities,
            current_position
        )

        # Generate recommendations
        scorecard['recommendations'] = self._generate_recommendations(
            scorecard,
            current_position
        )

        return scorecard
```

## Implementation Workflow

### Complete Stakeholder Mapping Workflow

```python
class StakeholderMappingWorkflow:
    """End-to-end stakeholder mapping workflow"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.identifier = StakeholderIdentificationEngine(db_connection)
        self.analyzer = StakeholderAnalyzer(db_connection)
        self.strategy_developer = EngagementStrategy(db_connection)
        self.monitor = StakeholderMonitoring(db_connection)

    def execute_complete_mapping(self, issue_id: str) -> Dict:
        """Execute complete stakeholder mapping for issue"""

        workflow_result = {
            'issue_id': issue_id,
            'workflow_status': 'in_progress',
            'stages_completed': [],
            'stakeholders_identified': 0,
            'engagement_plan': None
        }

        issue = self.db.query_issue(issue_id)

        # Stage 1: Identify stakeholders
        print("Stage 1: Identifying stakeholders...")
        stakeholders = self.identifier.identify_stakeholders(issue_id)
        workflow_result['stakeholders_identified'] = len(stakeholders)
        workflow_result['stages_completed'].append('identification')

        # Stage 2: Analyze stakeholder positions
        print("Stage 2: Analyzing positions...")
        for stakeholder in stakeholders:
            analysis = self.analyzer.predict_stakeholder_position(stakeholder, issue)
            self.db.update_stakeholder(
                stakeholder.stakeholder_id,
                {'stated_position': analysis['predicted_position']}
            )
        workflow_result['stages_completed'].append('position_analysis')

        # Stage 3: Create power/interest matrix
        print("Stage 3: Creating power/interest matrix...")
        power_interest = self.analyzer.create_power_interest_matrix(stakeholders)
        workflow_result['power_interest_matrix'] = power_interest
        workflow_result['stages_completed'].append('power_analysis')

        # Stage 4: Develop engagement strategies
        print("Stage 4: Developing engagement strategies...")
        engagement_plan = self.strategy_developer.develop_engagement_plan(
            stakeholders,
            issue
        )
        workflow_result['engagement_plan'] = engagement_plan
        workflow_result['stages_completed'].append('strategy_development')

        # Stage 5: Generate stakeholder map visualization data
        print("Stage 5: Preparing visualization...")
        visualization_data = self._prepare_visualization(stakeholders, issue)
        workflow_result['visualization'] = visualization_data
        workflow_result['stages_completed'].append('visualization')

        workflow_result['workflow_status'] = 'completed'
        workflow_result['completion_time'] = datetime.now()

        return workflow_result

    def _prepare_visualization(self, stakeholders: List[Stakeholder],
                              issue: Dict) -> Dict:
        """Prepare data for stakeholder map visualization"""

        # Organize by position
        supporters = [s for s in stakeholders if s.stated_position == 'support']
        opponents = [s for s in stakeholders if s.stated_position == 'oppose']
        neutral = [s for s in stakeholders if s.stated_position == 'neutral']

        return {
            'supporters': len(supporters),
            'opponents': len(opponents),
            'neutral': len(neutral),
            'supporter_names': [s.name for s in supporters[:10]],
            'opponent_names': [s.name for s in opponents[:10]],
            'key_decision_makers': self._identify_key_decision_makers(stakeholders),
            'coalition_opportunities': self._identify_coalition_opportunities(stakeholders)
        }

    def _identify_key_decision_makers(self, stakeholders: List[Stakeholder]) -> List[Dict]:
        """Identify key decision makers"""

        decision_makers = [
            s for s in stakeholders
            if s.current_role == StakeholderRole.DECISION_MAKER
        ]

        return [
            {
                'name': dm.name,
                'organization': dm.organization,
                'influence_level': dm.influence_level,
                'position': dm.stated_position
            }
            for dm in sorted(
                decision_makers,
                key=lambda x: x.influence_level,
                reverse=True
            )[:10]
        ]

    def _identify_coalition_opportunities(self, stakeholders: List[Stakeholder]) -> List[Dict]:
        """Identify potential coalition partners"""

        supporters = [s for s in stakeholders if s.stated_position == 'support']

        coalitions = []

        for supporter in supporters:
            if supporter.current_role in [
                StakeholderRole.DECISION_MAKER,
                StakeholderRole.INFLUENCER
            ]:
                coalition = {
                    'anchor': supporter.name,
                    'type': 'anchored',
                    'potential_members': [
                        s.name for s in supporters
                        if s.stakeholder_type == supporter.stakeholder_type
                        and s.stakeholder_id != supporter.stakeholder_id
                    ][:5]
                }
                coalitions.append(coalition)

        return coalitions[:5]
```

## Best Practices

### Excellence in Stakeholder Mapping

1. **Comprehensive Identification**
   - Cast wide net initially
   - Include secondary and tertiary stakeholders
   - Update regularly as issue evolves
   - Monitor for new stakeholders

2. **Accurate Assessment**
   - Use multiple data sources
   - Verify stakeholder information
   - Update positions based on new evidence
   - Document assumptions

3. **Strategic Engagement**
   - Tailor approach to each stakeholder
   - Focus resources on key influencers
   - Build relationships before crisis
   - Maintain regular contact

4. **Effective Communication**
   - Listen before talking
   - Acknowledge stakeholder interests
   - Provide credible information
   - Establish trust

5. **Coalition Building**
   - Identify common interests
   - Facilitate stakeholder connections
   - Provide value to coalition members
   - Maintain coalition cohesion

6. **Monitoring and Adaptation**
   - Track position changes
   - Monitor opposition activities
   - Adjust strategies as needed
   - Document lessons learned

## Conclusion

Effective stakeholder mapping provides the foundation for successful government relations and policy engagement. Organizations that systematically identify, analyze, and engage stakeholders gain significant advantages in achieving policy objectives and managing regulatory relationships.
