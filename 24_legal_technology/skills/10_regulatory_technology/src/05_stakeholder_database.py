"""
Stakeholder Database Module

Comprehensive database and relationship management for regulatory stakeholders:
- Legislators and government officials
- Industry representatives
- Non-profit and advocacy organizations
- Media contacts
- Constituent relationships
- Engagement history tracking
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class StakeholderType(Enum):
    """Types of regulatory stakeholders."""
    LEGISLATOR = "legislator"
    EXECUTIVE_OFFICIAL = "executive_official"
    AGENCY_STAFF = "agency_staff"
    INDUSTRY_REPRESENTATIVE = "industry_representative"
    ADVOCACY_ORGANIZATION = "advocacy_organization"
    ACADEMIC = "academic"
    MEDIA = "media"
    CONSTITUENT = "constituent"
    FOREIGN_AGENT = "foreign_agent"
    CONSULTANT = "consultant"


class PoliticalParty(Enum):
    """Political party affiliations."""
    DEMOCRAT = "democrat"
    REPUBLICAN = "republican"
    INDEPENDENT = "independent"
    OTHER = "other"


class EngagementType(Enum):
    """Types of stakeholder engagement."""
    MEETING = "meeting"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    CONFERENCE = "conference"
    TESTIMONY = "testimony"
    REPORT_SUBMISSION = "report_submission"
    FORMAL_LETTER = "formal_letter"
    MEDIA_ENGAGEMENT = "media_engagement"
    SOCIAL_MEDIA = "social_media"


@dataclass
class ContactInformation:
    """Contact details for stakeholder."""
    email: str
    phone_primary: str
    phone_secondary: Optional[str]
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    office_address: Optional[str]
    social_media_handles: Dict[str, str] = field(default_factory=dict)


@dataclass
class GovernmentPosition:
    """Government position information."""
    position_title: str
    agency_or_body: str
    office_or_district: str
    start_date: str
    end_date: Optional[str]
    office_phone: str
    office_address: str
    staff_members: List[str] = field(default_factory=list)
    committee_assignments: List[str] = field(default_factory=list)


@dataclass
class Stakeholder:
    """Core stakeholder profile."""
    stakeholder_id: str
    first_name: str
    last_name: str
    title: Optional[str]
    organization: str
    stakeholder_type: str
    contact_info: ContactInformation
    political_party: Optional[str]
    position_history: List[GovernmentPosition] = field(default_factory=list)
    current_position: Optional[GovernmentPosition] = None
    biography: Optional[str] = None
    areas_of_influence: List[str] = field(default_factory=list)
    policy_interests: List[str] = field(default_factory=list)
    funding_sources: List[str] = field(default_factory=list)
    known_positions: Dict[str, str] = field(default_factory=dict)  # Issue -> position
    rating_score: float = 5.0  # 1-10 scale
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Engagement:
    """Record of stakeholder engagement."""
    engagement_id: str
    stakeholder_id: str
    engagement_type: str
    date: str
    time_spent_minutes: Optional[int]
    participants: List[str]  # Internal team members involved
    topics_discussed: List[str]
    outcomes: List[str]
    follow_up_required: bool
    next_follow_up_date: Optional[str]
    notes: str
    attachments: List[str] = field(default_factory=list)


@dataclass
class Relationship:
    """Relationship between stakeholders."""
    relationship_id: str
    stakeholder_id_1: str
    stakeholder_id_2: str
    relationship_type: str  # Colleagues, Spouse, Donor, etc.
    relationship_strength: int  # 1-5 scale
    notes: Optional[str]
    established_date: str


class StakeholderDatabase:
    """
    Comprehensive stakeholder management system with:
    - Detailed profiles and position tracking
    - Engagement history
    - Relationship mapping
    - Influence analysis
    - Policy position tracking
    - Automated alerts and updates
    """

    def __init__(self):
        """Initialize stakeholder database."""
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.engagements: Dict[str, Engagement] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.engagement_log: List[Dict] = []
        logger.info("Stakeholder Database initialized")

    def add_stakeholder(self, stakeholder: Stakeholder) -> str:
        """Add new stakeholder to database."""
        if stakeholder.stakeholder_id in self.stakeholders:
            logger.warning(f"Stakeholder {stakeholder.stakeholder_id} already exists")
            return stakeholder.stakeholder_id

        self.stakeholders[stakeholder.stakeholder_id] = stakeholder
        logger.info(f"Stakeholder added: {stakeholder.first_name} {stakeholder.last_name}")

        return stakeholder.stakeholder_id

    def update_stakeholder(self, stakeholder: Stakeholder) -> bool:
        """Update stakeholder profile."""
        if stakeholder.stakeholder_id not in self.stakeholders:
            logger.error(f"Stakeholder {stakeholder.stakeholder_id} not found")
            return False

        stakeholder.last_updated = datetime.now().isoformat()
        self.stakeholders[stakeholder.stakeholder_id] = stakeholder
        logger.info(f"Stakeholder updated: {stakeholder.stakeholder_id}")

        return True

    def get_stakeholder(self, stakeholder_id: str) -> Optional[Stakeholder]:
        """Retrieve stakeholder profile."""
        return self.stakeholders.get(stakeholder_id)

    def search_stakeholders(
        self,
        criteria: Dict
    ) -> List[Stakeholder]:
        """
        Search stakeholders by various criteria.

        Criteria: name, organization, type, policy_interests, party, tags
        """
        results = list(self.stakeholders.values())

        if "name" in criteria:
            name_lower = criteria["name"].lower()
            results = [
                s for s in results
                if name_lower in f"{s.first_name} {s.last_name}".lower()
            ]

        if "organization" in criteria:
            org_lower = criteria["organization"].lower()
            results = [
                s for s in results
                if org_lower in s.organization.lower()
            ]

        if "type" in criteria:
            results = [
                s for s in results
                if s.stakeholder_type == criteria["type"]
            ]

        if "policy_interests" in criteria:
            interests = set(criteria["policy_interests"])
            results = [
                s for s in results
                if any(interest in s.policy_interests for interest in interests)
            ]

        if "party" in criteria:
            results = [
                s for s in results
                if s.political_party == criteria["party"]
            ]

        if "tags" in criteria:
            tag_set = set(criteria["tags"])
            results = [
                s for s in results
                if any(tag in s.tags for tag in tag_set)
            ]

        return results

    def record_engagement(self, engagement: Engagement) -> str:
        """Record stakeholder engagement."""
        if engagement.engagement_id in self.engagements:
            logger.warning(f"Engagement {engagement.engagement_id} already exists")
            return engagement.engagement_id

        self.engagements[engagement.engagement_id] = engagement
        self.engagement_log.append({
            "engagement_id": engagement.engagement_id,
            "stakeholder_id": engagement.stakeholder_id,
            "date": engagement.date,
            "type": engagement.engagement_type
        })

        logger.info(f"Engagement recorded: {engagement.engagement_id}")

        return engagement.engagement_id

    def get_engagement_history(
        self,
        stakeholder_id: str,
        days_back: int = 365
    ) -> List[Engagement]:
        """Get engagement history for stakeholder."""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        engagements = [
            e for e in self.engagements.values()
            if e.stakeholder_id == stakeholder_id and e.date >= cutoff_date
        ]

        return sorted(engagements, key=lambda e: e.date, reverse=True)

    def establish_relationship(self, relationship: Relationship) -> str:
        """Establish relationship between stakeholders."""
        rel_id = relationship.relationship_id

        if rel_id in self.relationships:
            logger.warning(f"Relationship {rel_id} already exists")
            return rel_id

        self.relationships[rel_id] = relationship
        logger.info(f"Relationship established: {rel_id}")

        return rel_id

    def find_related_stakeholders(
        self,
        stakeholder_id: str,
        degrees: int = 1
    ) -> List[Tuple[str, str]]:
        """Find related stakeholders within specified degrees of separation."""
        related = set()
        current_level = {stakeholder_id}

        for _ in range(degrees):
            next_level = set()

            for rel in self.relationships.values():
                if rel.stakeholder_id_1 in current_level:
                    next_level.add(rel.stakeholder_id_2)
                    related.add((rel.stakeholder_id_2, rel.relationship_type))
                elif rel.stakeholder_id_2 in current_level:
                    next_level.add(rel.stakeholder_id_1)
                    related.add((rel.stakeholder_id_1, rel.relationship_type))

            current_level = next_level

        return list(related)

    def get_stakeholders_by_type(self, stakeholder_type: StakeholderType) -> List[Stakeholder]:
        """Get all stakeholders of a specific type."""
        return [
            s for s in self.stakeholders.values()
            if s.stakeholder_type == stakeholder_type.value
        ]

    def get_stakeholders_by_policy_interest(self, policy_issue: str) -> List[Stakeholder]:
        """Get stakeholders interested in specific policy issue."""
        return [
            s for s in self.stakeholders.values()
            if any(issue.lower() == policy_issue.lower() for issue in s.policy_interests)
        ]

    def get_legislators_by_district(self, state: str, district: str = None) -> List[Stakeholder]:
        """Get legislators by state and optional district."""
        results = [
            s for s in self.stakeholders.values()
            if s.stakeholder_type == StakeholderType.LEGISLATOR.value
            and s.contact_info.state.upper() == state.upper()
        ]

        if district:
            results = [
                s for s in results
                if s.current_position and district in s.current_position.office_or_district
            ]

        return results

    def identify_key_influencers(
        self,
        policy_issue: str,
        min_rating: float = 7.0
    ) -> List[Stakeholder]:
        """Identify key stakeholders with influence on policy issue."""
        candidates = [
            s for s in self.stakeholders.values()
            if policy_issue in s.policy_interests
            and s.rating_score >= min_rating
        ]

        # Sort by rating and engagement frequency
        candidates.sort(key=lambda s: (
            s.rating_score,
            len(self.get_engagement_history(s.stakeholder_id, 90))
        ), reverse=True)

        return candidates

    def get_stakeholder_network_map(
        self,
        central_stakeholder_id: str
    ) -> Dict:
        """Generate network map showing stakeholder relationships."""
        primary = self.stakeholders.get(central_stakeholder_id)
        if not primary:
            return {}

        network = {
            "primary": {
                "id": primary.stakeholder_id,
                "name": f"{primary.first_name} {primary.last_name}",
                "organization": primary.organization,
                "type": primary.stakeholder_type
            },
            "connections": []
        }

        # Find direct connections
        for rel in self.relationships.values():
            if rel.stakeholder_id_1 == central_stakeholder_id:
                other_id = rel.stakeholder_id_2
            elif rel.stakeholder_id_2 == central_stakeholder_id:
                other_id = rel.stakeholder_id_1
            else:
                continue

            other = self.stakeholders.get(other_id)
            if other:
                network["connections"].append({
                    "stakeholder_id": other_id,
                    "name": f"{other.first_name} {other.last_name}",
                    "organization": other.organization,
                    "relationship_type": rel.relationship_type,
                    "relationship_strength": rel.relationship_strength
                })

        return network

    def get_engagement_frequency(
        self,
        stakeholder_id: str,
        days: int = 90
    ) -> Dict:
        """Analyze engagement frequency."""
        recent_engagements = self.get_engagement_history(stakeholder_id, days)

        if not recent_engagements:
            return {
                "stakeholder_id": stakeholder_id,
                "period_days": days,
                "total_engagements": 0,
                "frequency_per_month": 0.0
            }

        engagement_types = {}
        for eng in recent_engagements:
            eng_type = eng.engagement_type
            engagement_types[eng_type] = engagement_types.get(eng_type, 0) + 1

        return {
            "stakeholder_id": stakeholder_id,
            "period_days": days,
            "total_engagements": len(recent_engagements),
            "frequency_per_month": (len(recent_engagements) / days) * 30,
            "engagement_types": engagement_types,
            "last_engagement": recent_engagements[0].date if recent_engagements else None
        }

    def identify_pending_follow_ups(self) -> List[Dict]:
        """Identify engagements requiring follow-up."""
        pending = []

        for engagement in self.engagements.values():
            if engagement.follow_up_required:
                stakeholder = self.stakeholders.get(engagement.stakeholder_id)
                if stakeholder:
                    pending.append({
                        "engagement_id": engagement.engagement_id,
                        "stakeholder": f"{stakeholder.first_name} {stakeholder.last_name}",
                        "stakeholder_id": engagement.stakeholder_id,
                        "engagement_type": engagement.engagement_type,
                        "engagement_date": engagement.date,
                        "next_follow_up": engagement.next_follow_up_date,
                        "topics": engagement.topics_discussed
                    })

        return sorted(pending, key=lambda x: x.get("next_follow_up") or "")

    def get_influence_ranking(self, policy_issue: str) -> List[Dict]:
        """Rank stakeholders by influence on policy issue."""
        influencers = self.identify_key_influencers(policy_issue)

        ranked = []
        for rank, stakeholder in enumerate(influencers, 1):
            engagement_freq = self.get_engagement_frequency(stakeholder.stakeholder_id)

            ranked.append({
                "rank": rank,
                "stakeholder_id": stakeholder.stakeholder_id,
                "name": f"{stakeholder.first_name} {stakeholder.last_name}",
                "organization": stakeholder.organization,
                "rating_score": stakeholder.rating_score,
                "engagement_frequency": engagement_freq["frequency_per_month"],
                "type": stakeholder.stakeholder_type
            })

        return ranked

    def export_stakeholders(self, format: str = "json") -> str:
        """Export stakeholder database."""
        if format == "json":
            stakeholders_data = [asdict(s) for s in self.stakeholders.values()]
            return json.dumps(stakeholders_data, indent=2, default=str)

        return ""

    def get_database_statistics(self) -> Dict:
        """Generate database statistics."""
        type_counts = {}
        for stakeholder in self.stakeholders.values():
            stype = stakeholder.stakeholder_type
            type_counts[stype] = type_counts.get(stype, 0) + 1

        party_counts = {}
        for stakeholder in self.stakeholders.values():
            if stakeholder.political_party:
                party = stakeholder.political_party
                party_counts[party] = party_counts.get(party, 0) + 1

        return {
            "total_stakeholders": len(self.stakeholders),
            "stakeholders_by_type": type_counts,
            "stakeholders_by_party": party_counts,
            "total_engagements": len(self.engagements),
            "total_relationships": len(self.relationships),
            "average_rating": sum(
                s.rating_score for s in self.stakeholders.values()
            ) / len(self.stakeholders) if self.stakeholders else 0
        }


if __name__ == "__main__":
    # Example usage
    db = StakeholderDatabase()

    # Create a stakeholder
    legislator = Stakeholder(
        stakeholder_id="LEG_001",
        first_name="John",
        last_name="Smith",
        title="Representative",
        organization="US House of Representatives",
        stakeholder_type=StakeholderType.LEGISLATOR.value,
        contact_info=ContactInformation(
            email="john.smith@house.gov",
            phone_primary="202-555-0100",
            phone_secondary=None,
            address="Washington, DC",
            city="Washington",
            state="DC",
            zip_code="20001",
            country="USA",
            office_address="House Office Building",
            social_media_handles={"twitter": "@JohnSmith"}
        ),
        political_party=PoliticalParty.DEMOCRAT.value,
        areas_of_influence=["Technology Policy", "Data Privacy"],
        policy_interests=["Data Privacy", "Consumer Protection"],
        known_positions={"Data Privacy": "Strong Advocate"}
    )

    db.add_stakeholder(legislator)

    # Record engagement
    engagement = Engagement(
        engagement_id="ENG_001",
        stakeholder_id="LEG_001",
        engagement_type=EngagementType.MEETING.value,
        date=datetime.now().isoformat(),
        time_spent_minutes=30,
        participants=["Jane Doe", "John Johnson"],
        topics_discussed=["Data Privacy Bill", "GDPR Compliance"],
        outcomes=["Legislator expressed support for privacy bill"],
        follow_up_required=True,
        next_follow_up_date=(datetime.now() + timedelta(days=7)).isoformat(),
        notes="Productive meeting. Legislator interested in co-sponsoring privacy bill."
    )

    db.record_engagement(engagement)

    # Get statistics
    stats = db.get_database_statistics()
    print(json.dumps(stats, indent=2))
