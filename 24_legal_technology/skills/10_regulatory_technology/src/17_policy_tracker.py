"""
Policy Tracker - Track policy initiatives and advocacy progress.
Monitors policy positions, advocacy metrics, and stakeholder alignment.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class PolicyPhase(Enum):
    """Phases of policy development."""
    RESEARCH = "research"
    PROPOSAL = "proposal"
    ADVOCACY = "advocacy"
    NEGOTIATION = "negotiation"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"


class AdvocacyTactic(Enum):
    """Types of advocacy tactics."""
    DIRECT_LOBBYING = "direct_lobbying"
    GRASSROOTS = "grassroots"
    COALITION_BUILDING = "coalition_building"
    PUBLIC_COMMENT = "public_comment"
    MEDIA_OUTREACH = "media_outreach"
    RESEARCH_PUBLICATION = "research_publication"
    LEGAL_CHALLENGE = "legal_challenge"
    REGULATORY_PETITION = "regulatory_petition"


@dataclass
class PolicyInitiative:
    """Represents a policy initiative being tracked."""
    initiative_id: str
    title: str
    description: str
    area: str  # e.g., "Technology", "Environment", "Finance"
    phase: PolicyPhase
    created_date: datetime
    target_completion: datetime
    organizations_involved: List[str] = field(default_factory=list)
    key_stakeholders: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    status: str = "active"
    priority: int = 1  # 1=highest, 5=lowest
    metadata: Dict = field(default_factory=dict)


@dataclass
class AdvocacyActivity:
    """Represents advocacy activity."""
    activity_id: str
    initiative_id: str
    activity_type: AdvocacyTactic
    title: str
    description: str
    date_completed: datetime
    responsible_parties: List[str] = field(default_factory=list)
    outcome: str = ""
    success: bool = False
    cost: Optional[float] = None
    reach_metrics: Dict = field(default_factory=dict)  # e.g., {"emails_sent": 1000}


@dataclass
class PolicyPosition:
    """Represents a stakeholder position on a policy."""
    position_id: str
    initiative_id: str
    stakeholder: str
    position: str  # "support", "oppose", "neutral"
    rationale: str
    intensity: int  # 1-10 scale
    last_updated: datetime
    supporting_documents: List[str] = field(default_factory=list)


@dataclass
class PolicyMetric:
    """Represents a metric for tracking policy progress."""
    metric_id: str
    initiative_id: str
    metric_type: str
    value: float
    target_value: float
    unit: str
    measurement_date: datetime
    notes: str = ""


class PolicyTracker:
    """Track policy initiatives and advocacy progress."""

    def __init__(self, organization_name: str):
        """Initialize policy tracker."""
        self.organization_name = organization_name
        self.initiatives: Dict[str, PolicyInitiative] = {}
        self.activities: Dict[str, AdvocacyActivity] = {}
        self.positions: Dict[str, PolicyPosition] = {}
        self.metrics: Dict[str, PolicyMetric] = {}

    def create_initiative(
        self,
        title: str,
        description: str,
        area: str,
        target_completion: datetime,
        priority: int = 1
    ) -> PolicyInitiative:
        """Create a new policy initiative."""
        initiative_id = str(uuid.uuid4())

        initiative = PolicyInitiative(
            initiative_id=initiative_id,
            title=title,
            description=description,
            area=area,
            phase=PolicyPhase.RESEARCH,
            created_date=datetime.now(),
            target_completion=target_completion,
            priority=priority
        )

        self.initiatives[initiative_id] = initiative
        logger.info(f"Created policy initiative: {title}")
        return initiative

    def update_initiative_phase(self, initiative_id: str, new_phase: PolicyPhase) -> bool:
        """Update initiative phase."""
        if initiative_id not in self.initiatives:
            return False

        self.initiatives[initiative_id].phase = new_phase
        logger.info(f"Updated initiative {initiative_id} to phase: {new_phase.value}")
        return True

    def add_stakeholder(self, initiative_id: str, stakeholder: str) -> bool:
        """Add stakeholder to initiative."""
        if initiative_id not in self.initiatives:
            return False

        initiative = self.initiatives[initiative_id]
        if stakeholder not in initiative.key_stakeholders:
            initiative.key_stakeholders.append(stakeholder)

        return True

    def add_success_metric(self, initiative_id: str, metric: str) -> bool:
        """Add success metric to initiative."""
        if initiative_id not in self.initiatives:
            return False

        self.initiatives[initiative_id].success_metrics.append(metric)
        return True

    def record_activity(
        self,
        initiative_id: str,
        activity_type: AdvocacyTactic,
        title: str,
        description: str,
        responsible_parties: List[str],
        success: bool = False,
        outcome: str = "",
        cost: float = None
    ) -> Optional[AdvocacyActivity]:
        """Record advocacy activity."""
        if initiative_id not in self.initiatives:
            return None

        activity_id = str(uuid.uuid4())

        activity = AdvocacyActivity(
            activity_id=activity_id,
            initiative_id=initiative_id,
            activity_type=activity_type,
            title=title,
            description=description,
            date_completed=datetime.now(),
            responsible_parties=responsible_parties,
            success=success,
            outcome=outcome,
            cost=cost
        )

        self.activities[activity_id] = activity
        logger.info(f"Recorded activity: {title}")
        return activity

    def record_reach_metric(
        self,
        activity_id: str,
        metric_name: str,
        value: int
    ) -> bool:
        """Record reach metric for activity."""
        if activity_id not in self.activities:
            return False

        self.activities[activity_id].reach_metrics[metric_name] = value
        return True

    def record_stakeholder_position(
        self,
        initiative_id: str,
        stakeholder: str,
        position: str,
        rationale: str,
        intensity: int = 5
    ) -> Optional[PolicyPosition]:
        """Record stakeholder position on policy."""
        if initiative_id not in self.initiatives:
            return None

        position_id = str(uuid.uuid4())

        policy_position = PolicyPosition(
            position_id=position_id,
            initiative_id=initiative_id,
            stakeholder=stakeholder,
            position=position,
            rationale=rationale,
            intensity=intensity,
            last_updated=datetime.now()
        )

        self.positions[position_id] = policy_position
        logger.info(f"Recorded position for {stakeholder} on initiative")
        return policy_position

    def record_metric(
        self,
        initiative_id: str,
        metric_type: str,
        value: float,
        target_value: float,
        unit: str,
        notes: str = ""
    ) -> Optional[PolicyMetric]:
        """Record progress metric."""
        if initiative_id not in self.initiatives:
            return None

        metric_id = str(uuid.uuid4())

        metric = PolicyMetric(
            metric_id=metric_id,
            initiative_id=initiative_id,
            metric_type=metric_type,
            value=value,
            target_value=target_value,
            unit=unit,
            measurement_date=datetime.now(),
            notes=notes
        )

        self.metrics[metric_id] = metric
        logger.info(f"Recorded metric: {metric_type}")
        return metric

    def get_initiative_status(self, initiative_id: str) -> Optional[Dict]:
        """Get detailed status of an initiative."""
        if initiative_id not in self.initiatives:
            return None

        initiative = self.initiatives[initiative_id]

        # Get related activities
        related_activities = [
            a for a in self.activities.values()
            if a.initiative_id == initiative_id
        ]

        # Get stakeholder positions
        stakeholder_positions = [
            p for p in self.positions.values()
            if p.initiative_id == initiative_id
        ]

        # Get metrics
        related_metrics = [
            m for m in self.metrics.values()
            if m.initiative_id == initiative_id
        ]

        # Calculate alignment
        support_count = len([p for p in stakeholder_positions if p.position == "support"])
        oppose_count = len([p for p in stakeholder_positions if p.position == "oppose"])
        neutral_count = len([p for p in stakeholder_positions if p.position == "neutral"])

        return {
            "initiative_id": initiative_id,
            "title": initiative.title,
            "phase": initiative.phase.value,
            "priority": initiative.priority,
            "created_date": initiative.created_date.isoformat(),
            "target_completion": initiative.target_completion.isoformat(),
            "activities_count": len(related_activities),
            "activities_successful": len([a for a in related_activities if a.success]),
            "stakeholders": {
                "total": len(stakeholder_positions),
                "support": support_count,
                "oppose": oppose_count,
                "neutral": neutral_count
            },
            "metrics": {
                "total_recorded": len(related_metrics),
                "on_track": sum(1 for m in related_metrics if m.value >= m.target_value * 0.8)
            }
        }

    def get_portfolio_overview(self) -> Dict:
        """Get overview of all policy initiatives."""
        by_phase = {}
        for phase in PolicyPhase:
            count = len([i for i in self.initiatives.values() if i.phase == phase])
            by_phase[phase.value] = count

        by_area = {}
        for initiative in self.initiatives.values():
            by_area[initiative.area] = by_area.get(initiative.area, 0) + 1

        total_activities = len(self.activities)
        successful_activities = len([a for a in self.activities.values() if a.success])

        return {
            "total_initiatives": len(self.initiatives),
            "by_phase": by_phase,
            "by_area": by_area,
            "total_activities": total_activities,
            "activity_success_rate": (
                successful_activities / total_activities if total_activities > 0 else 0
            ),
            "total_stakeholders": len(set(p.stakeholder for p in self.positions.values()))
        }

    def get_high_priority_initiatives(self) -> List[PolicyInitiative]:
        """Get high priority initiatives."""
        return sorted(
            [i for i in self.initiatives.values() if i.priority <= 2],
            key=lambda x: x.priority
        )

    def get_at_risk_initiatives(self) -> List[Dict]:
        """Get initiatives at risk of missing deadlines."""
        at_risk = []
        now = datetime.now()

        for initiative in self.initiatives.values():
            if initiative.status == "active":
                days_remaining = (initiative.target_completion - now).days
                if 0 <= days_remaining <= 30:
                    at_risk.append({
                        "initiative_id": initiative.initiative_id,
                        "title": initiative.title,
                        "days_remaining": days_remaining,
                        "phase": initiative.phase.value
                    })

        return at_risk
