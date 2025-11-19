"""
Grassroots Platform - Mobilize constituent engagement for policy advocacy.
Manages volunteer networks, communication campaigns, and advocacy actions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of grassroots actions."""
    EMAIL_CONTACT = "email_contact"
    PHONE_CALL = "phone_call"
    LETTER_WRITE = "letter_write"
    PETITION_SIGN = "petition_sign"
    SOCIAL_MEDIA = "social_media"
    DOOR_KNOCK = "door_knock"
    ATTEND_EVENT = "attend_event"
    DONATE = "donate"


class VolunteerLevel(Enum):
    """Volunteer engagement levels."""
    BASIC = "basic"
    ACTIVE = "active"
    LEADER = "leader"
    ORGANIZER = "organizer"


@dataclass
class Volunteer:
    """Represents a grassroots volunteer."""
    volunteer_id: str
    name: str
    email: str
    phone: str
    zip_code: str
    level: VolunteerLevel
    joined_date: datetime
    actions_completed: int = 0
    total_impact: int = 0
    interests: List[str] = field(default_factory=list)
    verified: bool = False
    opt_in_communications: bool = True
    metadata: Dict = field(default_factory=dict)


@dataclass
class CivicAction:
    """Represents a specific civic action."""
    action_id: str
    action_type: ActionType
    title: str
    description: str
    target_legislator: Optional[str]
    target_agency: Optional[str]
    issue: str
    created_date: datetime
    deadline: Optional[datetime]
    impact_description: str
    action_template: Optional[str]  # Template for email, letter, etc.
    completion_count: int = 0
    status: str = "active"


@dataclass
class Campaign:
    """Represents a grassroots campaign."""
    campaign_id: str
    name: str
    description: str
    goal: str
    start_date: datetime
    end_date: datetime
    actions: List[str]  # action_ids
    participants: List[str]  # volunteer_ids
    created_date: datetime
    total_impact: int = 0
    status: str = "active"


class GrassrootsMapper:
    """Map constituents to elected representatives."""

    @staticmethod
    def get_representatives_by_zip(zip_code: str) -> List[Dict]:
        """Get elected representatives for a zip code."""
        # In production, integrate with Google Civic API or similar
        return [
            {
                "name": "Sample Representative",
                "office": "U.S. House of Representatives",
                "email": "rep@house.gov",
                "phone": "202-225-0000"
            }
        ]


class GrassrootsPlatform:
    """Platform for managing grassroots advocacy campaigns."""

    def __init__(self, organization_name: str):
        """Initialize grassroots platform."""
        self.organization_name = organization_name
        self.volunteers: Dict[str, Volunteer] = {}
        self.actions: Dict[str, CivicAction] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.mapper = GrassrootsMapper()

    def register_volunteer(
        self,
        name: str,
        email: str,
        phone: str,
        zip_code: str,
        interests: List[str] = None
    ) -> Volunteer:
        """Register a new volunteer."""
        volunteer_id = str(uuid.uuid4())

        volunteer = Volunteer(
            volunteer_id=volunteer_id,
            name=name,
            email=email,
            phone=phone,
            zip_code=zip_code,
            level=VolunteerLevel.BASIC,
            joined_date=datetime.now(),
            interests=interests or []
        )

        self.volunteers[volunteer_id] = volunteer
        logger.info(f"Registered volunteer: {name}")
        return volunteer

    def verify_volunteer(self, volunteer_id: str) -> bool:
        """Verify volunteer email."""
        if volunteer_id in self.volunteers:
            self.volunteers[volunteer_id].verified = True
            logger.info(f"Verified volunteer: {volunteer_id}")
            return True
        return False

    def promote_volunteer(self, volunteer_id: str, new_level: VolunteerLevel) -> bool:
        """Promote volunteer to new level."""
        if volunteer_id in self.volunteers:
            self.volunteers[volunteer_id].level = new_level
            logger.info(f"Promoted volunteer {volunteer_id} to {new_level.value}")
            return True
        return False

    def create_action(
        self,
        action_type: ActionType,
        title: str,
        description: str,
        issue: str,
        impact_description: str,
        target_legislator: str = None,
        target_agency: str = None,
        deadline: datetime = None,
        template: str = None
    ) -> CivicAction:
        """Create a new civic action."""
        action_id = str(uuid.uuid4())

        action = CivicAction(
            action_id=action_id,
            action_type=action_type,
            title=title,
            description=description,
            target_legislator=target_legislator,
            target_agency=target_agency,
            issue=issue,
            created_date=datetime.now(),
            deadline=deadline,
            impact_description=impact_description,
            action_template=template
        )

        self.actions[action_id] = action
        logger.info(f"Created action: {title}")
        return action

    def record_action_completion(self, action_id: str, volunteer_id: str) -> bool:
        """Record completion of an action by a volunteer."""
        if action_id not in self.actions or volunteer_id not in self.volunteers:
            return False

        action = self.actions[action_id]
        volunteer = self.volunteers[volunteer_id]

        action.completion_count += 1
        volunteer.actions_completed += 1
        volunteer.total_impact += 1

        logger.info(f"Recorded action completion: {volunteer_id} -> {action_id}")
        return True

    def create_campaign(
        self,
        name: str,
        description: str,
        goal: str,
        end_date: datetime,
        action_ids: List[str]
    ) -> Campaign:
        """Create a new campaign."""
        campaign_id = str(uuid.uuid4())

        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            description=description,
            goal=goal,
            start_date=datetime.now(),
            end_date=end_date,
            actions=action_ids,
            participants=[],
            created_date=datetime.now()
        )

        self.campaigns[campaign_id] = campaign
        logger.info(f"Created campaign: {name}")
        return campaign

    def add_volunteer_to_campaign(self, campaign_id: str, volunteer_id: str) -> bool:
        """Add volunteer to campaign."""
        if campaign_id in self.campaigns and volunteer_id in self.volunteers:
            if volunteer_id not in self.campaigns[campaign_id].participants:
                self.campaigns[campaign_id].participants.append(volunteer_id)
            return True
        return False

    def get_personalized_actions(self, volunteer_id: str) -> List[CivicAction]:
        """Get actions personalized for a volunteer's representatives."""
        if volunteer_id not in self.volunteers:
            return []

        volunteer = self.volunteers[volunteer_id]
        representatives = self.mapper.get_representatives_by_zip(volunteer.zip_code)

        # Filter actions relevant to volunteer's interests
        relevant_actions = []
        for action in self.actions.values():
            if any(interest in action.issue for interest in volunteer.interests):
                relevant_actions.append(action)

        return relevant_actions

    def get_campaign_metrics(self, campaign_id: str) -> Dict:
        """Get campaign performance metrics."""
        if campaign_id not in self.campaigns:
            return {}

        campaign = self.campaigns[campaign_id]
        total_impact = 0

        for participant_id in campaign.participants:
            if participant_id in self.volunteers:
                total_impact += self.volunteers[participant_id].total_impact

        return {
            "campaign_name": campaign.name,
            "participants": len(campaign.participants),
            "actions": len(campaign.actions),
            "total_impact": total_impact,
            "status": campaign.status,
            "days_remaining": (campaign.end_date - datetime.now()).days
        }

    def get_volunteer_dashboard(self, volunteer_id: str) -> Dict:
        """Get volunteer dashboard summary."""
        if volunteer_id not in self.volunteers:
            return {}

        volunteer = self.volunteers[volunteer_id]

        return {
            "name": volunteer.name,
            "level": volunteer.level.value,
            "actions_completed": volunteer.actions_completed,
            "total_impact": volunteer.total_impact,
            "verified": volunteer.verified,
            "interests": volunteer.interests
        }
