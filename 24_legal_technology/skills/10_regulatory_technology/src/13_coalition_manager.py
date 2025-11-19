"""
Coalition Manager - Manage stakeholder coalitions for policy advocacy.
Coordinates member communications, positions, and collaborative efforts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class OrganizationType(Enum):
    """Types of organizations in coalition."""
    CORPORATION = "corporation"
    NGO = "ngo"
    ASSOCIATION = "association"
    TRADE_GROUP = "trade_group"
    THINK_TANK = "think_tank"
    LABOR = "labor"


class PositionType(Enum):
    """Coalition position types."""
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"
    CONDITIONAL = "conditional"


@dataclass
class CoalitionMember:
    """Represents a member organization in a coalition."""
    member_id: str
    name: str
    organization_type: OrganizationType
    contact_email: str
    contact_name: str
    address: str
    website: str
    joined_date: datetime
    is_active: bool = True
    annual_revenue: Optional[float] = None
    employees: Optional[int] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class CoalitionPosition:
    """Represents a coalition position on an issue."""
    position_id: str
    issue: str
    position_type: PositionType
    description: str
    member_positions: Dict[str, PositionType]  # member_id -> position
    creation_date: datetime
    last_updated: datetime
    supporting_documents: List[str] = field(default_factory=list)


@dataclass
class CoalitionCampaign:
    """Represents a coordinated campaign."""
    campaign_id: str
    name: str
    objective: str
    start_date: datetime
    end_date: Optional[datetime]
    participating_members: List[str]
    activities: List[Dict] = field(default_factory=list)
    budget: Optional[float] = None
    status: str = "active"


class CoalitionManager:
    """Manage stakeholder coalitions for policy advocacy."""

    def __init__(self, coalition_name: str):
        """Initialize coalition manager."""
        self.coalition_name = coalition_name
        self.members: Dict[str, CoalitionMember] = {}
        self.positions: Dict[str, CoalitionPosition] = {}
        self.campaigns: Dict[str, CoalitionCampaign] = {}
        self.created_date = datetime.now()

    def add_member(
        self,
        name: str,
        org_type: OrganizationType,
        contact_email: str,
        contact_name: str,
        address: str,
        website: str = None,
        annual_revenue: float = None,
        employees: int = None
    ) -> CoalitionMember:
        """Add a new member to the coalition."""
        member_id = f"member_{len(self.members) + 1}"

        member = CoalitionMember(
            member_id=member_id,
            name=name,
            organization_type=org_type,
            contact_email=contact_email,
            contact_name=contact_name,
            address=address,
            website=website or "",
            joined_date=datetime.now(),
            annual_revenue=annual_revenue,
            employees=employees
        )

        self.members[member_id] = member
        logger.info(f"Added member: {name}")
        return member

    def remove_member(self, member_id: str) -> bool:
        """Remove member from coalition."""
        if member_id in self.members:
            member = self.members.pop(member_id)
            logger.info(f"Removed member: {member.name}")
            return True
        return False

    def create_position(
        self,
        issue: str,
        position_type: PositionType,
        description: str
    ) -> CoalitionPosition:
        """Create a coalition position on an issue."""
        position_id = f"position_{len(self.positions) + 1}"

        position = CoalitionPosition(
            position_id=position_id,
            issue=issue,
            position_type=position_type,
            description=description,
            member_positions={},
            creation_date=datetime.now(),
            last_updated=datetime.now()
        )

        self.positions[position_id] = position
        logger.info(f"Created position on {issue}")
        return position

    def set_member_position(
        self,
        position_id: str,
        member_id: str,
        position_type: PositionType
    ) -> bool:
        """Set a member's position on a coalition issue."""
        if position_id not in self.positions or member_id not in self.members:
            return False

        position = self.positions[position_id]
        position.member_positions[member_id] = position_type
        position.last_updated = datetime.now()
        return True

    def get_coalition_alignment(self, position_id: str) -> Dict:
        """Get alignment summary for a position."""
        if position_id not in self.positions:
            return {}

        position = self.positions[position_id]
        alignment = {
            "support": 0,
            "oppose": 0,
            "neutral": 0,
            "conditional": 0
        }

        for pos_type in position.member_positions.values():
            alignment[pos_type.value] += 1

        total = sum(alignment.values())
        if total > 0:
            alignment["support_percent"] = (alignment["support"] / total) * 100
            alignment["oppose_percent"] = (alignment["oppose"] / total) * 100

        return alignment

    def create_campaign(
        self,
        name: str,
        objective: str,
        end_date: datetime = None,
        budget: float = None
    ) -> CoalitionCampaign:
        """Create a new coordinated campaign."""
        campaign_id = f"campaign_{len(self.campaigns) + 1}"

        campaign = CoalitionCampaign(
            campaign_id=campaign_id,
            name=name,
            objective=objective,
            start_date=datetime.now(),
            end_date=end_date,
            participating_members=list(self.members.keys()),
            budget=budget
        )

        self.campaigns[campaign_id] = campaign
        logger.info(f"Created campaign: {name}")
        return campaign

    def add_campaign_activity(
        self,
        campaign_id: str,
        activity_type: str,
        description: str,
        assigned_members: List[str] = None
    ) -> bool:
        """Add activity to a campaign."""
        if campaign_id not in self.campaigns:
            return False

        activity = {
            "type": activity_type,
            "description": description,
            "assigned_members": assigned_members or [],
            "created_date": datetime.now().isoformat(),
            "status": "pending"
        }

        self.campaigns[campaign_id].activities.append(activity)
        return True

    def get_member_summary(self) -> Dict:
        """Get summary of coalition membership."""
        return {
            "total_members": len(self.members),
            "by_type": {
                org_type.value: sum(
                    1 for m in self.members.values()
                    if m.organization_type == org_type
                )
                for org_type in OrganizationType
            },
            "active_members": sum(1 for m in self.members.values() if m.is_active),
            "total_reach": sum(m.employees or 0 for m in self.members.values())
        }

    def export_coalition_data(self) -> Dict:
        """Export coalition data for reporting."""
        return {
            "coalition_name": self.coalition_name,
            "created_date": self.created_date.isoformat(),
            "members": len(self.members),
            "positions": len(self.positions),
            "campaigns": len(self.campaigns),
            "membership_summary": self.get_member_summary()
        }
