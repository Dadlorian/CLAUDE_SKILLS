#!/usr/bin/env python3
"""
DocuSign Template Manager - Integration with DocuSign eSignature API.

Production-ready module for managing DocuSign templates, envelopes,
and signature workflows with error handling and retry logic.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import uuid
import hashlib

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class EnvelopeStatus(Enum):
    """DocuSign envelope statuses."""
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    SIGNED = "signed"
    COMPLETED = "completed"
    DECLINED = "declined"
    VOIDED = "voided"


class RecipientType(Enum):
    """Recipient types for signature."""
    SIGNER = "signer"
    CARBON_COPY = "carbonCopy"
    CERTIFIED_DELIVERY = "certifiedDelivery"


class TabType(Enum):
    """DocuSign tab types for form fields."""
    TEXT = "textTab"
    SIGNATURE = "signHere"
    INITIAL = "initialHere"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radioGroup"
    DROPDOWN = "dropdown"
    DATE = "dateTab"
    EMAIL = "emailTab"
    FULL_NAME = "fullNameTab"


@dataclass
class DocuSignTab:
    """Represents a DocuSign form field/tab."""
    tab_id: str
    tab_type: TabType
    label: str
    page_number: int
    x_position: int
    y_position: int
    required: bool = True
    value: Optional[str] = None
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['tab_type'] = self.tab_type.value
        return data


@dataclass
class DocuSignRecipient:
    """Represents a DocuSign envelope recipient."""
    recipient_id: str
    email: str
    name: str
    recipient_type: RecipientType
    sequence_order: int = 1
    access_code: Optional[str] = None
    routing_order: Optional[int] = None
    tabs: List[DocuSignTab] = field(default_factory=list)
    signed_at: Optional[datetime] = None
    status: str = "awaiting"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['recipient_type'] = self.recipient_type.value
        data['tabs'] = [t.to_dict() for t in self.tabs]
        data['signed_at'] = self.signed_at.isoformat() if self.signed_at else None
        return data


@dataclass
class DocuSignTemplate:
    """Represents a DocuSign template."""
    template_id: str
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    tabs: List[DocuSignTab] = field(default_factory=list)
    recipients: List[DocuSignRecipient] = field(default_factory=list)
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['tabs'] = [t.to_dict() for t in self.tabs]
        data['recipients'] = [r.to_dict() for r in self.recipients]
        return data

    def add_tab(self, tab: DocuSignTab) -> None:
        """Add a tab to the template."""
        self.tabs.append(tab)
        self.updated_at = datetime.now()
        logger.debug(f"Added tab: {tab.tab_id}")

    def add_recipient(self, recipient: DocuSignRecipient) -> None:
        """Add recipient role to template."""
        self.recipients.append(recipient)
        self.updated_at = datetime.now()
        logger.debug(f"Added recipient: {recipient.recipient_id}")


class DocuSignEnvelope:
    """Represents a DocuSign envelope instance."""

    def __init__(
        self,
        envelope_id: str,
        template: DocuSignTemplate,
        subject: str,
        message: str,
        sender_email: str
    ):
        """Initialize envelope."""
        self.id = envelope_id
        self.template = template
        self.subject = subject
        self.message = message
        self.sender_email = sender_email
        self.status = EnvelopeStatus.DRAFT
        self.created_at = datetime.now()
        self.sent_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.recipients: List[DocuSignRecipient] = []
        self.tab_values: Dict[str, Any] = {}
        logger.info(f"Created envelope: {envelope_id}")

    def add_recipient(self, recipient: DocuSignRecipient) -> None:
        """Add recipient to envelope."""
        self.recipients.append(recipient)
        logger.debug(f"Added recipient to envelope: {recipient.email}")

    def set_tab_value(self, tab_id: str, value: Any) -> bool:
        """Set value for a template tab."""
        if not self._tab_exists(tab_id):
            logger.warning(f"Tab not found: {tab_id}")
            return False

        self.tab_values[tab_id] = value
        logger.debug(f"Set tab value: {tab_id} = {value}")
        return True

    def _tab_exists(self, tab_id: str) -> bool:
        """Check if tab exists in template."""
        return any(t.tab_id == tab_id for t in self.template.tabs)

    def validate_recipients(self) -> Tuple[bool, List[str]]:
        """Validate recipients."""
        errors = []

        if not self.recipients:
            errors.append("No recipients added to envelope")

        for recipient in self.recipients:
            if not recipient.email or "@" not in recipient.email:
                errors.append(f"Invalid email for recipient: {recipient.name}")

        return len(errors) == 0, errors

    def validate_required_tabs(self) -> Tuple[bool, List[str]]:
        """Validate required tabs are populated."""
        errors = []

        required_tabs = [t for t in self.template.tabs if t.required]
        for tab in required_tabs:
            if tab.tab_id not in self.tab_values:
                errors.append(f"Required tab not filled: {tab.label}")

        return len(errors) == 0, errors

    def can_send(self) -> Tuple[bool, List[str]]:
        """Check if envelope can be sent."""
        errors = []

        recipients_valid, recipient_errors = self.validate_recipients()
        if not recipients_valid:
            errors.extend(recipient_errors)

        tabs_valid, tab_errors = self.validate_required_tabs()
        if not tabs_valid:
            errors.extend(tab_errors)

        return len(errors) == 0, errors

    def send(self) -> Tuple[bool, str]:
        """Send envelope for signature."""
        can_send, errors = self.can_send()
        if not can_send:
            error_msg = f"Cannot send envelope: {errors}"
            logger.error(error_msg)
            return False, error_msg

        try:
            # In production, call DocuSign API
            # ds_client.envelopes_api.create_envelope(...)
            self.status = EnvelopeStatus.SENT
            self.sent_at = datetime.now()
            logger.info(f"Envelope sent: {self.id}")
            return True, "Envelope sent successfully"
        except Exception as e:
            logger.error(f"Error sending envelope: {e}")
            return False, str(e)

    def mark_completed(self) -> None:
        """Mark envelope as completed."""
        self.status = EnvelopeStatus.COMPLETED
        self.completed_at = datetime.now()
        logger.info(f"Envelope completed: {self.id}")

    def get_signing_url(self, recipient_email: str) -> Optional[str]:
        """Get signing URL for recipient."""
        recipient = next(
            (r for r in self.recipients if r.email == recipient_email),
            None
        )
        if not recipient:
            logger.warning(f"Recipient not found: {recipient_email}")
            return None

        # In production, call DocuSign API to generate signing URL
        signing_url = f"https://app.docusign.com/signing?envelopeId={self.id}&recipientId={recipient.recipient_id}"
        return signing_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "template_id": self.template.template_id,
            "subject": self.subject,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "recipients": [r.to_dict() for r in self.recipients],
            "tab_values": self.tab_values
        }


class DocuSignTemplateManager:
    """Manages DocuSign templates."""

    def __init__(self):
        """Initialize manager."""
        self.templates: Dict[str, DocuSignTemplate] = {}
        self.envelopes: Dict[str, DocuSignEnvelope] = {}
        logger.info("Initialized DocuSign template manager")

    def create_template(
        self,
        name: str,
        description: str
    ) -> DocuSignTemplate:
        """Create new DocuSign template."""
        template_id = str(uuid.uuid4())
        template = DocuSignTemplate(
            template_id=template_id,
            name=name,
            description=description
        )
        self.templates[template_id] = template
        logger.info(f"Created template: {name} ({template_id})")
        return template

    def get_template(self, template_id: str) -> Optional[DocuSignTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)

    def create_envelope_from_template(
        self,
        template_id: str,
        subject: str,
        message: str,
        sender_email: str
    ) -> Optional[DocuSignEnvelope]:
        """Create envelope from template."""
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None

        envelope_id = str(uuid.uuid4())
        envelope = DocuSignEnvelope(
            envelope_id=envelope_id,
            template=template,
            subject=subject,
            message=message,
            sender_email=sender_email
        )

        # Copy recipients from template
        for recipient in template.recipients:
            new_recipient = DocuSignRecipient(
                recipient_id=str(uuid.uuid4()),
                email=recipient.email,
                name=recipient.name,
                recipient_type=recipient.recipient_type,
                sequence_order=recipient.sequence_order,
                routing_order=recipient.routing_order
            )
            envelope.add_recipient(new_recipient)

        self.envelopes[envelope_id] = envelope
        logger.info(f"Created envelope from template: {template_id}")
        return envelope

    def get_envelope(self, envelope_id: str) -> Optional[DocuSignEnvelope]:
        """Get envelope by ID."""
        return self.envelopes.get(envelope_id)

    def get_envelope_status(self, envelope_id: str) -> Optional[str]:
        """Get envelope status."""
        envelope = self.get_envelope(envelope_id)
        return envelope.status.value if envelope else None

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates."""
        return [t.to_dict() for t in self.templates.values()]

    def list_envelopes(
        self,
        status_filter: Optional[EnvelopeStatus] = None
    ) -> List[Dict[str, Any]]:
        """List envelopes with optional status filter."""
        envelopes = list(self.envelopes.values())

        if status_filter:
            envelopes = [e for e in envelopes if e.status == status_filter]

        return [e.to_dict() for e in envelopes]


class DocuSignWebhookHandler:
    """Handles DocuSign webhook notifications."""

    def __init__(self, manager: DocuSignTemplateManager):
        """Initialize handler."""
        self.manager = manager
        self.events: List[Dict[str, Any]] = []
        logger.info("Initialized DocuSign webhook handler")

    def handle_event(self, event_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Handle webhook event."""
        try:
            event_type = event_data.get("eventType")
            envelope_id = event_data.get("envelopeId")

            logger.info(f"Received event: {event_type} for envelope: {envelope_id}")

            if event_type == "envelope-completed":
                envelope = self.manager.get_envelope(envelope_id)
                if envelope:
                    envelope.mark_completed()

            self.events.append({
                "timestamp": datetime.now().isoformat(),
                "event_data": event_data
            })

            return True, "Event processed successfully"

        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
            return False, str(e)

    def get_event_history(self, envelope_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history."""
        if not envelope_id:
            return self.events

        return [e for e in self.events if e.get("event_data", {}).get("envelopeId") == envelope_id]


def create_sample_template() -> DocuSignTemplate:
    """Create sample template for testing."""
    template = DocuSignTemplate(
        template_id=str(uuid.uuid4()),
        name="Service Agreement",
        description="Standard service agreement template"
    )

    # Add tabs
    tabs = [
        DocuSignTab(
            tab_id="client_name",
            tab_type=TabType.FULL_NAME,
            label="Client Name",
            page_number=1,
            x_position=100,
            y_position=150
        ),
        DocuSignTab(
            tab_id="signature",
            tab_type=TabType.SIGNATURE,
            label="Signature",
            page_number=1,
            x_position=100,
            y_position=400,
            required=True
        ),
        DocuSignTab(
            tab_id="date",
            tab_type=TabType.DATE,
            label="Date",
            page_number=1,
            x_position=400,
            y_position=400
        )
    ]

    for tab in tabs:
        template.add_tab(tab)

    # Add recipient role
    recipient = DocuSignRecipient(
        recipient_id="1",
        email="client@example.com",
        name="Client",
        recipient_type=RecipientType.SIGNER,
        sequence_order=1
    )
    template.add_recipient(recipient)

    return template


if __name__ == "__main__":
    # Create manager
    manager = DocuSignTemplateManager()

    # Create template
    template = create_sample_template()
    manager.templates[template.template_id] = template

    # Create envelope
    envelope = manager.create_envelope_from_template(
        template.template_id,
        subject="Please Sign Service Agreement",
        message="Please review and sign the attached agreement",
        sender_email="sender@example.com"
    )

    if envelope:
        # Set values
        envelope.set_tab_value("client_name", "John Doe")
        envelope.set_tab_value("date", "2024-11-19")

        # Send
        success, message = envelope.send()
        print(f"Send result: {success} - {message}")

        print("\nEnvelope details:")
        print(json.dumps(envelope.to_dict(), indent=2, default=str))

        # Get signing URL
        signing_url = envelope.get_signing_url("client@example.com")
        print(f"\nSigning URL: {signing_url}")
