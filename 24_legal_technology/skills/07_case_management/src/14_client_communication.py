"""
Client Communication - Practice Management Automation

Manages client communications, tracks correspondence, and generates
status updates and engagement letters automatically.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict
import json


class CommunicationType(Enum):
    """Types of client communications"""
    EMAIL = "email"
    PHONE = "phone"
    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"
    STATUS_UPDATE = "status_update"
    LETTER = "letter"
    SMS = "sms"


class CommunicationStatus(Enum):
    """Status of communication"""
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"
    ARCHIVED = "archived"


@dataclass
class Communication:
    """Record of client communication"""
    comm_id: str
    matter_id: str
    client_id: str
    comm_type: CommunicationType
    subject: str
    message: str
    sent_by: str
    sent_date: datetime
    status: CommunicationStatus = CommunicationStatus.DRAFT
    recipient_email: Optional[str] = None
    phone_number: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    next_action: Optional[str] = None

    def to_dict(self):
        return {
            "comm_id": self.comm_id,
            "matter_id": self.matter_id,
            "client_id": self.client_id,
            "type": self.comm_type.value,
            "subject": self.subject,
            "status": self.status.value,
            "sent_by": self.sent_by,
            "sent_date": self.sent_date.isoformat(),
            "recipient_email": self.recipient_email,
            "attachments": len(self.attachments)
        }


@dataclass
class StatusUpdate:
    """Automated status update for client"""
    update_id: str
    matter_id: str
    client_id: str
    update_date: datetime
    summary: str
    next_steps: List[str]
    estimated_timeline: str
    outstanding_items: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)


class ClientCommunicationManager:
    """Manages all client communications"""

    def __init__(self):
        self.communications: List[Communication] = []
        self.templates: Dict[str, str] = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize communication templates"""
        return {
            "engagement_letter": """
Dear {client_name},

This letter confirms our engagement to represent you in {matter_type}.

Our hourly rate is ${hourly_rate} and we estimate this matter will require approximately {estimated_hours} hours.

We will keep you updated on the progress of your matter.

Best regards,
{attorney_name}
            """,
            "status_update": """
Dear {client_name},

Here is your status update for {matter_description}:

Summary: {summary}

Next Steps:
{next_steps}

Estimated Timeline: {estimated_timeline}

Please contact us if you have any questions.

Regards,
{attorney_name}
            """,
            "case_closure": """
Dear {client_name},

We are pleased to inform you that your matter has been concluded.

Final Outcome: {outcome}

Please find attached your final billing statement and documentation.

Thank you for allowing us to represent you.

Best regards,
{attorney_name}
            """
        }

    def create_communication(self, communication: Communication) -> str:
        """Create a new communication record"""
        self.communications.append(communication)
        return communication.comm_id

    def send_communication(self, comm_id: str) -> bool:
        """Mark communication as sent"""
        for comm in self.communications:
            if comm.comm_id == comm_id:
                comm.status = CommunicationStatus.SENT
                comm.sent_date = datetime.now()
                return True
        return False

    def get_communications_for_matter(self, matter_id: str) -> List[Communication]:
        """Get all communications for a matter"""
        return [c for c in self.communications if c.matter_id == matter_id]

    def get_communications_by_type(self, matter_id: str, comm_type: CommunicationType) -> List[Communication]:
        """Get communications of specific type for a matter"""
        return [c for c in self.communications
                if c.matter_id == matter_id and c.comm_type == comm_type]

    def get_pending_communications(self) -> List[Communication]:
        """Get all communications not yet sent"""
        return [c for c in self.communications if c.status == CommunicationStatus.DRAFT]

    def generate_engagement_letter(self, matter_id: str, client_name: str, attorney_name: str,
                                   matter_type: str, hourly_rate: str, estimated_hours: str) -> str:
        """Generate engagement letter from template"""
        template = self.templates["engagement_letter"]
        letter = template.format(
            client_name=client_name,
            matter_type=matter_type,
            hourly_rate=hourly_rate,
            estimated_hours=estimated_hours,
            attorney_name=attorney_name
        )
        return letter

    def generate_status_update(self, update: StatusUpdate, client_name: str, attorney_name: str) -> str:
        """Generate status update from template"""
        template = self.templates["status_update"]
        next_steps_text = "\n".join([f"- {step}" for step in update.next_steps])

        update_text = template.format(
            client_name=client_name,
            matter_description="your matter",
            summary=update.summary,
            next_steps=next_steps_text,
            estimated_timeline=update.estimated_timeline,
            attorney_name=attorney_name
        )
        return update_text

    def create_status_update_communication(self, update: StatusUpdate, client_email: str,
                                          attorney_id: str) -> str:
        """Create and send status update as communication"""
        content = self.generate_status_update(update, "Client", "Attorney")

        comm = Communication(
            comm_id=f"COMM-{update.matter_id}-{update.update_date.strftime('%Y%m%d%H%M%S')}",
            matter_id=update.matter_id,
            client_id="",
            comm_type=CommunicationType.STATUS_UPDATE,
            subject=f"Status Update - {update.matter_id}",
            message=content,
            sent_by=attorney_id,
            sent_date=update.update_date,
            recipient_email=client_email,
            attachments=update.attachments,
            next_action="Review response"
        )

        return self.create_communication(comm)

    def get_communication_statistics(self, matter_id: str) -> Dict:
        """Get communication statistics for a matter"""
        comms = self.get_communications_for_matter(matter_id)

        stats = {
            "matter_id": matter_id,
            "total_communications": len(comms),
            "by_type": {},
            "by_status": {},
            "with_attachments": len([c for c in comms if c.attachments])
        }

        for comm_type in CommunicationType:
            count = len([c for c in comms if c.comm_type == comm_type])
            if count > 0:
                stats["by_type"][comm_type.value] = count

        for status in CommunicationStatus:
            count = len([c for c in comms if c.status == status])
            if count > 0:
                stats["by_status"][status.value] = count

        return stats

    def export_communications(self, matter_id: str) -> str:
        """Export communications as JSON"""
        comms = self.get_communications_for_matter(matter_id)
        data = {
            "matter_id": matter_id,
            "export_date": datetime.now().isoformat(),
            "total_communications": len(comms),
            "communications": [c.to_dict() for c in comms]
        }
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    manager = ClientCommunicationManager()

    comm = Communication(
        comm_id="COMM-001",
        matter_id="MAT-2024-001",
        client_id="CLI-001",
        comm_type=CommunicationType.STATUS_UPDATE,
        subject="Case Status Update",
        message="Here is your case status...",
        sent_by="ATT-001",
        sent_date=datetime.now(),
        recipient_email="client@example.com"
    )

    comm_id = manager.create_communication(comm)
    manager.send_communication(comm_id)

    stats = manager.get_communication_statistics("MAT-2024-001")
    print(f"Communication Statistics: {stats}")
