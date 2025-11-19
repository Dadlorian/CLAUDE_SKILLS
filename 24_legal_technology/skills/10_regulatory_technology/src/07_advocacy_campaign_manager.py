"""
Advocacy Campaign Manager Module

Comprehensive advocacy campaign management including:
- Campaign planning and strategy
- Stakeholder targeting and coordination
- Message development and tracking
- Campaign timeline and milestone management
- Impact measurement and reporting
- Coalition management
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class CampaignPhase(Enum):
    """Phases of advocacy campaign."""
    PLANNING = "planning"
    RESEARCH = "research"
    COALITION_BUILDING = "coalition_building"
    MESSAGE_DEVELOPMENT = "message_development"
    STAKEHOLDER_ENGAGEMENT = "stakeholder_engagement"
    IMPLEMENTATION = "implementation"
    EVALUATION = "evaluation"


class CampaignStatus(Enum):
    """Overall campaign status."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AdvocacyGoalType(Enum):
    """Types of advocacy goals."""
    LEGISLATION_PASSAGE = "legislation_passage"
    LEGISLATION_DEFEAT = "legislation_defeat"
    RULE_CHANGE = "rule_change"
    POLICY_POSITION = "policy_position"
    FUNDING_ALLOCATION = "funding_allocation"
    PUBLIC_AWARENESS = "public_awareness"


@dataclass
class AdvocacyGoal:
    """Specific advocacy objective."""
    goal_id: str
    goal_type: str
    description: str
    target_audience: List[str]
    success_criteria: List[str]
    priority_level: int  # 1-5
    estimated_timeline_days: int
    responsible_party: str
    status: str  # not_started, in_progress, completed, failed
    start_date: str
    target_completion_date: str


@dataclass
class CampaignMessage:
    """Key message for campaign."""
    message_id: str
    title: str
    primary_message: str
    supporting_points: List[str]
    target_audience_segment: str
    message_variants: Dict[str, str]  # Medium -> variant text
    call_to_action: str
    evidence_base: List[str]
    effectiveness_score: Optional[float]
    created_date: str


@dataclass
class CampaignActivity:
    """Specific campaign activity."""
    activity_id: str
    activity_type: str  # Letter, Call, Meeting, Event, Media, etc.
    description: str
    date_scheduled: str
    date_completed: Optional[str]
    responsible_party: str
    target_stakeholder: str
    message_id: str
    expected_reach: int
    actual_reach: Optional[int]
    outcomes: List[str] = field(default_factory=list)
    success_metric: Optional[float] = None


@dataclass
class AdvocacyCampaign:
    """Complete advocacy campaign."""
    campaign_id: str
    campaign_name: str
    campaign_type: str  # Legislative, Regulatory, Public Awareness, etc.
    description: str
    jurisdiction: str
    policy_focus: str
    campaign_status: str
    current_phase: str
    launch_date: str
    target_completion_date: str
    annual_budget: float
    goals: List[AdvocacyGoal] = field(default_factory=list)
    messages: List[CampaignMessage] = field(default_factory=list)
    activities: List[CampaignActivity] = field(default_factory=list)
    coalition_members: List[str] = field(default_factory=list)
    stakeholder_targets: List[Dict] = field(default_factory=list)
    key_contacts: List[Dict] = field(default_factory=list)
    campaign_budget_spent: float = 0.0
    expected_impact: Optional[Dict] = None
    actual_impact: Optional[Dict] = None
    success_probability: float = 0.5  # 0-1


class AdvocacyCampaignManager:
    """
    Comprehensive advocacy campaign management system.

    Features:
    - Campaign creation and planning
    - Message development and tracking
    - Stakeholder targeting and coordination
    - Activity scheduling and execution
    - Impact measurement
    - Coalition management
    - Budget tracking
    """

    def __init__(self):
        """Initialize campaign manager."""
        self.campaigns: Dict[str, AdvocacyCampaign] = {}
        self.messages: Dict[str, CampaignMessage] = {}
        self.activities: Dict[str, CampaignActivity] = {}
        self.coalitions: Dict[str, Dict] = {}
        self.activity_log: List[Dict] = []
        logger.info("Advocacy Campaign Manager initialized")

    def create_campaign(
        self,
        campaign_name: str,
        campaign_type: str,
        description: str,
        jurisdiction: str,
        policy_focus: str,
        target_completion_date: str,
        annual_budget: float
    ) -> str:
        """Create new advocacy campaign."""
        campaign_id = self._generate_campaign_id(campaign_name)

        campaign = AdvocacyCampaign(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            campaign_type=campaign_type,
            description=description,
            jurisdiction=jurisdiction,
            policy_focus=policy_focus,
            campaign_status=CampaignStatus.PROPOSED.value,
            current_phase=CampaignPhase.PLANNING.value,
            launch_date=datetime.now().isoformat(),
            target_completion_date=target_completion_date,
            annual_budget=annual_budget
        )

        self.campaigns[campaign_id] = campaign
        logger.info(f"Campaign created: {campaign_id}")

        return campaign_id

    def _generate_campaign_id(self, campaign_name: str) -> str:
        """Generate unique campaign identifier."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_hash = hashlib.md5(campaign_name.encode()).hexdigest()[:6]
        return f"CAMP_{name_hash}_{timestamp}"

    def add_goal(
        self,
        campaign_id: str,
        goal: AdvocacyGoal
    ) -> bool:
        """Add goal to campaign."""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return False

        self.campaigns[campaign_id].goals.append(goal)
        logger.info(f"Goal added to campaign {campaign_id}")

        return True

    def develop_message(
        self,
        campaign_id: str,
        message: CampaignMessage
    ) -> str:
        """Develop campaign message."""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return ""

        self.campaigns[campaign_id].messages.append(message)
        self.messages[message.message_id] = message

        logger.info(f"Message developed: {message.message_id}")

        return message.message_id

    def schedule_activity(
        self,
        campaign_id: str,
        activity: CampaignActivity
    ) -> str:
        """Schedule campaign activity."""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return ""

        self.campaigns[campaign_id].activities.append(activity)
        self.activities[activity.activity_id] = activity

        self.activity_log.append({
            "activity_id": activity.activity_id,
            "campaign_id": campaign_id,
            "date_scheduled": activity.date_scheduled,
            "status": "scheduled"
        })

        logger.info(f"Activity scheduled: {activity.activity_id}")

        return activity.activity_id

    def update_activity_status(
        self,
        activity_id: str,
        date_completed: str,
        actual_reach: int,
        outcomes: List[str],
        success_metric: Optional[float] = None
    ) -> bool:
        """Update activity completion status."""
        if activity_id not in self.activities:
            logger.error(f"Activity {activity_id} not found")
            return False

        activity = self.activities[activity_id]
        activity.date_completed = date_completed
        activity.actual_reach = actual_reach
        activity.outcomes = outcomes
        activity.success_metric = success_metric

        logger.info(f"Activity completed: {activity_id}")

        return True

    def form_coalition(
        self,
        coalition_id: str,
        coalition_name: str,
        lead_organization: str,
        policy_focus: str,
        member_organizations: List[str]
    ) -> str:
        """Form advocacy coalition."""
        coalition = {
            "coalition_id": coalition_id,
            "coalition_name": coalition_name,
            "lead_organization": lead_organization,
            "policy_focus": policy_focus,
            "members": member_organizations,
            "formation_date": datetime.now().isoformat(),
            "status": "active",
            "coordinated_campaigns": []
        }

        self.coalitions[coalition_id] = coalition
        logger.info(f"Coalition formed: {coalition_id}")

        return coalition_id

    def add_coalition_to_campaign(
        self,
        campaign_id: str,
        coalition_id: str
    ) -> bool:
        """Link coalition to campaign."""
        if campaign_id not in self.campaigns or coalition_id not in self.coalitions:
            logger.error("Campaign or coalition not found")
            return False

        campaign = self.campaigns[campaign_id]
        coalition = self.coalitions[coalition_id]

        if coalition_id not in campaign.coalition_members:
            campaign.coalition_members.append(coalition_id)
            if campaign_id not in coalition["coordinated_campaigns"]:
                coalition["coordinated_campaigns"].append(campaign_id)

        return True

    def add_stakeholder_targets(
        self,
        campaign_id: str,
        stakeholders: List[Dict]
    ) -> bool:
        """Add stakeholder targets to campaign."""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return False

        self.campaigns[campaign_id].stakeholder_targets.extend(stakeholders)
        return True

    def assess_success_probability(self, campaign_id: str) -> float:
        """
        Calculate campaign success probability based on:
        - Budget adequacy
        - Goal clarity
        - Stakeholder engagement
        - Timeline feasibility
        """
        if campaign_id not in self.campaigns:
            return 0.0

        campaign = self.campaigns[campaign_id]
        score = 0.5  # Base score

        # Assess goals
        if campaign.goals:
            score += 0.1  # Goals defined

            completed_goals = sum(
                1 for g in campaign.goals
                if g.status == "completed"
            )
            if len(campaign.goals) > 0:
                score += (completed_goals / len(campaign.goals)) * 0.1

        # Assess messages
        if campaign.messages:
            score += 0.05

            avg_effectiveness = sum(
                m.effectiveness_score or 0.5
                for m in campaign.messages
            ) / len(campaign.messages)
            score += avg_effectiveness * 0.05

        # Assess stakeholder engagement
        engagement_count = len(campaign.stakeholder_targets)
        if engagement_count > 0:
            score += min(0.15, engagement_count * 0.03)

        # Assess coalition support
        if campaign.coalition_members:
            score += 0.15

        # Assess timeline feasibility
        remaining_days = (
            datetime.fromisoformat(campaign.target_completion_date) - datetime.now()
        ).days

        if remaining_days > 30:
            score += 0.05
        elif remaining_days < 0:
            score -= 0.2

        campaign.success_probability = min(1.0, max(0.0, score))
        return campaign.success_probability

    def get_activity_timeline(self, campaign_id: str) -> List[Dict]:
        """Get chronological timeline of campaign activities."""
        if campaign_id not in self.campaigns:
            return []

        campaign = self.campaigns[campaign_id]
        timeline = []

        for activity in sorted(
            campaign.activities,
            key=lambda a: a.date_scheduled
        ):
            timeline.append({
                "activity_id": activity.activity_id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "date_scheduled": activity.date_scheduled,
                "date_completed": activity.date_completed,
                "status": "completed" if activity.date_completed else "pending",
                "reach": activity.actual_reach or activity.expected_reach
            })

        return timeline

    def measure_campaign_impact(self, campaign_id: str) -> Dict:
        """Measure and report campaign impact."""
        if campaign_id not in self.campaigns:
            return {}

        campaign = self.campaigns[campaign_id]

        # Calculate impact metrics
        total_reach = sum(
            a.actual_reach or a.expected_reach
            for a in campaign.activities
            if a.date_completed
        )

        completed_goals = sum(
            1 for g in campaign.goals
            if g.status == "completed"
        )

        avg_activity_effectiveness = 0.0
        completed_activities = [a for a in campaign.activities if a.date_completed]

        if completed_activities:
            avg_activity_effectiveness = sum(
                a.success_metric or 0.5
                for a in completed_activities
            ) / len(completed_activities)

        impact = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "total_reach": total_reach,
            "activities_completed": len(completed_activities),
            "activities_total": len(campaign.activities),
            "goals_completed": completed_goals,
            "goals_total": len(campaign.goals),
            "average_activity_effectiveness": avg_activity_effectiveness,
            "coalition_members_engaged": len(campaign.coalition_members),
            "budget_spent": campaign.campaign_budget_spent,
            "budget_total": campaign.annual_budget,
            "success_probability": self.assess_success_probability(campaign_id),
            "measurement_date": datetime.now().isoformat()
        }

        campaign.actual_impact = impact
        return impact

    def get_campaign_status_report(self, campaign_id: str) -> Dict:
        """Generate comprehensive campaign status report."""
        if campaign_id not in self.campaigns:
            return {}

        campaign = self.campaigns[campaign_id]

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.campaign_name,
            "status": campaign.campaign_status,
            "current_phase": campaign.current_phase,
            "policy_focus": campaign.policy_focus,
            "goals": [
                {
                    "description": g.description,
                    "status": g.status,
                    "target_date": g.target_completion_date
                }
                for g in campaign.goals
            ],
            "activities": self.get_activity_timeline(campaign_id),
            "coalition_size": len(campaign.coalition_members),
            "stakeholders_engaged": len(campaign.stakeholder_targets),
            "success_probability": campaign.success_probability,
            "budget_utilization": {
                "total_budget": campaign.annual_budget,
                "amount_spent": campaign.campaign_budget_spent,
                "percentage_spent": (
                    campaign.campaign_budget_spent / campaign.annual_budget * 100
                    if campaign.annual_budget > 0 else 0
                )
            },
            "timeline": {
                "launch_date": campaign.launch_date,
                "target_completion": campaign.target_completion_date,
                "days_remaining": (
                    datetime.fromisoformat(campaign.target_completion_date) - datetime.now()
                ).days
            },
            "key_metrics": self.measure_campaign_impact(campaign_id)
        }

    def get_message_performance(self, campaign_id: str) -> List[Dict]:
        """Get performance metrics for campaign messages."""
        if campaign_id not in self.campaigns:
            return []

        campaign = self.campaigns[campaign_id]
        performance = []

        for message in campaign.messages:
            # Count activities using this message
            message_activities = [
                a for a in campaign.activities
                if a.message_id == message.message_id and a.date_completed
            ]

            effectiveness = 0.0
            if message_activities:
                effectiveness = sum(
                    a.success_metric or 0.5
                    for a in message_activities
                ) / len(message_activities)

            performance.append({
                "message_id": message.message_id,
                "title": message.title,
                "target_audience": message.target_audience_segment,
                "times_used": len(message_activities),
                "effectiveness": effectiveness,
                "call_to_action": message.call_to_action
            })

        return sorted(
            performance,
            key=lambda x: x["effectiveness"],
            reverse=True
        )

    def export_campaign_data(self, campaign_id: str, format: str = "json") -> str:
        """Export campaign data."""
        if campaign_id not in self.campaigns:
            return ""

        campaign = self.campaigns[campaign_id]

        if format == "json":
            export_data = {
                "campaign_id": campaign_id,
                "campaign_name": campaign.campaign_name,
                "status": campaign.campaign_status,
                "goals_count": len(campaign.goals),
                "messages_count": len(campaign.messages),
                "activities_count": len(campaign.activities),
                "coalition_members": campaign.coalition_members,
                "budget": campaign.annual_budget,
                "budget_spent": campaign.campaign_budget_spent,
                "success_probability": campaign.success_probability,
                "impact": campaign.actual_impact
            }

            return json.dumps(export_data, indent=2, default=str)

        return ""


if __name__ == "__main__":
    # Example usage
    manager = AdvocacyCampaignManager()

    # Create campaign
    campaign_id = manager.create_campaign(
        "Data Privacy Protection Act Campaign",
        "Legislative",
        "Campaign to advance comprehensive data privacy legislation",
        "US Federal",
        "Data Privacy",
        "2024-12-31",
        500000
    )

    # Add goal
    goal = AdvocacyGoal(
        goal_id="GOAL_1",
        goal_type=AdvocacyGoalType.LEGISLATION_PASSAGE.value,
        description="Pass comprehensive data privacy legislation",
        target_audience=["House Members", "Senate Members"],
        success_criteria=["Bill introduced", "Committee hearing held", "Vote scheduled"],
        priority_level=5,
        estimated_timeline_days=365,
        responsible_party="Campaign Manager",
        status="in_progress",
        start_date=datetime.now().isoformat(),
        target_completion_date=(datetime.now() + timedelta(days=365)).isoformat()
    )

    manager.add_goal(campaign_id, goal)

    # Develop message
    message = CampaignMessage(
        message_id="MSG_1",
        title="Privacy as a Right",
        primary_message="Data privacy is a fundamental right that must be protected",
        supporting_points=[
            "72% of Americans support comprehensive privacy law",
            "Data breaches cost economy billions annually"
        ],
        target_audience_segment="General Public",
        message_variants={
            "social_media": "Your data, your right. Support #PrivacyNow",
            "email": "Tell Congress to pass comprehensive privacy protection"
        },
        call_to_action="Contact your representative",
        evidence_base=["Survey Data 2024", "Economic Impact Study"],
        effectiveness_score=None,
        created_date=datetime.now().isoformat()
    )

    manager.develop_message(campaign_id, message)

    # Get status report
    report = manager.get_campaign_status_report(campaign_id)
    print(json.dumps(report, indent=2, default=str))
