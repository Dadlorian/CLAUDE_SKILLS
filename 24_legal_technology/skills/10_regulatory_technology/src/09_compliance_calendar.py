"""
Compliance Calendar Module

Regulatory compliance event management and deadline tracking including:
- Filing deadline management
- Certification renewal tracking
- Regulatory examination schedules
- Comment period deadlines
- Reporting requirement tracking
- Automated reminders and alerts
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ComplianceEventType(Enum):
    """Types of compliance events."""
    FILING_DEADLINE = "filing_deadline"
    CERTIFICATION_RENEWAL = "certification_renewal"
    REGULATORY_EXAM = "regulatory_exam"
    COMMENT_PERIOD = "comment_period"
    REPORTING_REQUIREMENT = "reporting_requirement"
    LICENSE_RENEWAL = "license_renewal"
    AUDIT = "audit"
    INSPECTION = "inspection"
    TRAINING_REQUIREMENT = "training_requirement"
    POLICY_UPDATE = "policy_update"


class PriorityLevel(Enum):
    """Priority levels for compliance events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Status of compliance event."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ReminderFrequency(Enum):
    """Reminder notification frequency."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ComplianceDocument:
    """Document required for compliance event."""
    document_id: str
    document_type: str
    description: str
    required: bool
    submission_deadline: str
    status: str  # not_started, in_progress, completed, submitted
    document_url: Optional[str]
    preparer: str
    reviewer: Optional[str]


@dataclass
class ComplianceEvent:
    """Single compliance event or deadline."""
    event_id: str
    event_type: str
    title: str
    description: str
    responsible_party: str
    responsible_email: str
    jurisdiction: str
    regulatory_body: str
    due_date: str
    start_date: Optional[str]
    submission_method: Optional[str]
    priority: str
    status: str
    required_documents: List[ComplianceDocument] = field(default_factory=list)
    penalties_for_noncompliance: Optional[Dict] = None
    renewal_frequency_months: Optional[int] = None
    recurring: bool = False
    notes: Optional[str] = None
    last_completed_date: Optional[str] = None
    completion_date: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ComplianceReminder:
    """Reminder for compliance event."""
    reminder_id: str
    event_id: str
    reminder_type: str  # email, sms, in_app, webhook
    reminder_time_before_days: int
    frequency: str
    recipients: List[str]
    message_template: str
    last_sent_date: Optional[str]
    is_active: bool


@dataclass
class ComplianceAudit:
    """Audit of compliance record."""
    audit_id: str
    event_id: str
    audit_date: str
    auditor: str
    findings: List[str]
    compliance_status: str  # compliant, non_compliant, partial
    corrective_actions: List[str]
    follow_up_date: Optional[str]


class ComplianceCalendar:
    """
    Comprehensive compliance calendar and deadline management system.

    Features:
    - Multi-jurisdiction compliance tracking
    - Recurring event management
    - Automated reminder system
    - Document preparation tracking
    - Audit and compliance history
    - Dashboard and reporting
    """

    def __init__(self):
        """Initialize compliance calendar."""
        self.events: Dict[str, ComplianceEvent] = {}
        self.reminders: Dict[str, ComplianceReminder] = {}
        self.audits: Dict[str, ComplianceAudit] = {}
        self.event_history: List[Dict] = []
        logger.info("Compliance Calendar initialized")

    def add_event(self, event: ComplianceEvent) -> str:
        """Add compliance event to calendar."""
        if event.event_id in self.events:
            logger.warning(f"Event {event.event_id} already exists")
            return event.event_id

        self.events[event.event_id] = event
        logger.info(f"Compliance event added: {event.event_id}")

        return event.event_id

    def schedule_reminders(
        self,
        event_id: str,
        reminder_times: List[int],  # Days before deadline
        recipients: List[str],
        reminder_type: str = "email"
    ) -> List[str]:
        """Schedule reminders for compliance event."""
        if event_id not in self.events:
            logger.error(f"Event {event_id} not found")
            return []

        event = self.events[event_id]
        reminder_ids = []

        for i, days_before in enumerate(reminder_times):
            reminder_id = f"REMIND_{event_id}_{days_before}d_{i}"

            reminder = ComplianceReminder(
                reminder_id=reminder_id,
                event_id=event_id,
                reminder_type=reminder_type,
                reminder_time_before_days=days_before,
                frequency=ReminderFrequency.ONCE.value if not event.recurring else ReminderFrequency.MONTHLY.value,
                recipients=recipients,
                message_template=self._generate_reminder_template(event, days_before),
                is_active=True
            )

            self.reminders[reminder_id] = reminder
            reminder_ids.append(reminder_id)

        logger.info(f"Scheduled {len(reminder_ids)} reminders for event {event_id}")

        return reminder_ids

    def _generate_reminder_template(
        self,
        event: ComplianceEvent,
        days_before: int
    ) -> str:
        """Generate reminder message template."""
        return f"""
        COMPLIANCE REMINDER

        Event: {event.title}
        Due Date: {event.due_date}
        Days Until Due: {days_before}
        Priority: {event.priority}

        Responsible Party: {event.responsible_party}
        Jurisdiction: {event.jurisdiction}

        Required Documents: {len(event.required_documents)}

        Please ensure all necessary documents are prepared for timely submission.
        """

    def add_required_document(
        self,
        event_id: str,
        document: ComplianceDocument
    ) -> bool:
        """Add required document to compliance event."""
        if event_id not in self.events:
            logger.error(f"Event {event_id} not found")
            return False

        self.events[event_id].required_documents.append(document)
        logger.info(f"Document added to event {event_id}")

        return True

    def get_upcoming_deadlines(
        self,
        days_ahead: int = 30,
        jurisdiction: Optional[str] = None,
        priority_filter: Optional[str] = None
    ) -> List[ComplianceEvent]:
        """Get upcoming compliance deadlines."""
        today = datetime.now()
        cutoff_date = today + timedelta(days=days_ahead)

        upcoming = []

        for event in self.events.values():
            if event.status == EventStatus.COMPLETED.value:
                continue

            try:
                due_date = datetime.fromisoformat(event.due_date)

                # Filter by date range
                if not (today <= due_date <= cutoff_date):
                    continue

                # Filter by jurisdiction
                if jurisdiction and event.jurisdiction != jurisdiction:
                    continue

                # Filter by priority
                if priority_filter and event.priority != priority_filter:
                    continue

                upcoming.append(event)

            except ValueError:
                logger.warning(f"Invalid date format for event {event.event_id}")

        # Sort by due date
        upcoming.sort(key=lambda e: e.due_date)

        return upcoming

    def get_overdue_events(self) -> List[ComplianceEvent]:
        """Get overdue compliance events."""
        overdue = []

        for event in self.events.values():
            if event.status in [EventStatus.COMPLETED.value, EventStatus.CANCELLED.value]:
                continue

            try:
                due_date = datetime.fromisoformat(event.due_date)

                if due_date < datetime.now():
                    event.status = EventStatus.OVERDUE.value
                    overdue.append(event)

            except ValueError:
                logger.warning(f"Invalid date format for event {event.event_id}")

        return overdue

    def update_event_status(
        self,
        event_id: str,
        new_status: EventStatus,
        completion_notes: Optional[str] = None
    ) -> bool:
        """Update compliance event status."""
        if event_id not in self.events:
            logger.error(f"Event {event_id} not found")
            return False

        event = self.events[event_id]
        old_status = event.status
        event.status = new_status.value

        if new_status == EventStatus.COMPLETED:
            event.completion_date = datetime.now().isoformat()
            event.last_completed_date = datetime.now().isoformat()

        self.event_history.append({
            "event_id": event_id,
            "date": datetime.now().isoformat(),
            "old_status": old_status,
            "new_status": new_status.value,
            "notes": completion_notes
        })

        logger.info(f"Event {event_id} status updated to {new_status.value}")

        return True

    def mark_document_complete(
        self,
        event_id: str,
        document_id: str,
        submission_url: Optional[str] = None
    ) -> bool:
        """Mark compliance document as complete."""
        if event_id not in self.events:
            logger.error(f"Event {event_id} not found")
            return False

        event = self.events[event_id]

        for doc in event.required_documents:
            if doc.document_id == document_id:
                doc.status = "completed"
                if submission_url:
                    doc.document_url = submission_url

                logger.info(f"Document {document_id} marked complete")

                # Check if all documents complete
                if all(d.status == "completed" for d in event.required_documents):
                    logger.info(f"All documents complete for event {event_id}")

                return True

        return False

    def get_document_status(self, event_id: str) -> Dict:
        """Get document completion status for event."""
        if event_id not in self.events:
            return {}

        event = self.events[event_id]

        total_docs = len(event.required_documents)
        completed_docs = sum(1 for d in event.required_documents if d.status == "completed")

        return {
            "event_id": event_id,
            "event_title": event.title,
            "total_documents": total_docs,
            "completed_documents": completed_docs,
            "pending_documents": total_docs - completed_docs,
            "completion_percentage": (completed_docs / total_docs * 100) if total_docs > 0 else 0,
            "documents": [
                {
                    "document_id": d.document_id,
                    "type": d.document_type,
                    "status": d.status,
                    "deadline": d.submission_deadline,
                    "preparer": d.preparer
                }
                for d in event.required_documents
            ]
        }

    def record_audit(
        self,
        event_id: str,
        auditor: str,
        findings: List[str],
        compliance_status: str,
        corrective_actions: List[str] = None
    ) -> str:
        """Record compliance audit."""
        if event_id not in self.events:
            logger.error(f"Event {event_id} not found")
            return ""

        audit_id = f"AUDIT_{event_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        audit = ComplianceAudit(
            audit_id=audit_id,
            event_id=event_id,
            audit_date=datetime.now().isoformat(),
            auditor=auditor,
            findings=findings,
            compliance_status=compliance_status,
            corrective_actions=corrective_actions or []
        )

        self.audits[audit_id] = audit
        logger.info(f"Audit recorded: {audit_id}")

        return audit_id

    def get_compliance_rate(
        self,
        jurisdiction: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> float:
        """Calculate compliance rate for events."""
        filtered_events = list(self.events.values())

        if jurisdiction:
            filtered_events = [e for e in filtered_events if e.jurisdiction == jurisdiction]

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        if not filtered_events:
            return 0.0

        completed = sum(
            1 for e in filtered_events
            if e.status == EventStatus.COMPLETED.value
        )

        return (completed / len(filtered_events)) * 100

    def get_compliance_dashboard(
        self,
        jurisdiction: Optional[str] = None
    ) -> Dict:
        """Generate compliance dashboard."""
        all_events = (
            [e for e in self.events.values() if e.jurisdiction == jurisdiction]
            if jurisdiction else list(self.events.values())
        )

        upcoming = self.get_upcoming_deadlines(30, jurisdiction)
        overdue = [e for e in all_events if e.status == EventStatus.OVERDUE.value]

        status_counts = {}
        for event in all_events:
            status = event.status
            status_counts[status] = status_counts.get(status, 0) + 1

        event_type_counts = {}
        for event in all_events:
            etype = event.event_type
            event_type_counts[etype] = event_type_counts.get(etype, 0) + 1

        return {
            "jurisdiction": jurisdiction or "All",
            "total_events": len(all_events),
            "events_by_status": status_counts,
            "events_by_type": event_type_counts,
            "upcoming_30_days": len(upcoming),
            "overdue_events": len(overdue),
            "compliance_rate": self.get_compliance_rate(jurisdiction),
            "dashboard_date": datetime.now().isoformat(),
            "critical_alerts": {
                "overdue": len(overdue),
                "upcoming_this_week": len([e for e in upcoming if (datetime.fromisoformat(e.due_date) - datetime.now()).days <= 7]),
                "high_priority_pending": len([
                    e for e in all_events
                    if e.priority == PriorityLevel.HIGH.value
                    and e.status in [EventStatus.SCHEDULED.value, EventStatus.ACTIVE.value]
                ])
            }
        }

    def schedule_recurring_event(
        self,
        base_event: ComplianceEvent,
        frequency_months: int,
        occurrences: int
    ) -> List[str]:
        """Schedule recurring compliance event."""
        base_event.recurring = True
        base_event.renewal_frequency_months = frequency_months

        event_ids = []
        base_date = datetime.fromisoformat(base_event.due_date)

        for i in range(occurrences):
            new_due_date = base_date + timedelta(days=frequency_months * 30)

            new_event = ComplianceEvent(
                event_id=f"{base_event.event_id}_REC_{i + 1}",
                event_type=base_event.event_type,
                title=base_event.title,
                description=base_event.description,
                responsible_party=base_event.responsible_party,
                responsible_email=base_event.responsible_email,
                jurisdiction=base_event.jurisdiction,
                regulatory_body=base_event.regulatory_body,
                due_date=new_due_date.isoformat(),
                start_date=base_event.start_date,
                submission_method=base_event.submission_method,
                priority=base_event.priority,
                status=EventStatus.SCHEDULED.value,
                required_documents=base_event.required_documents.copy(),
                penalties_for_noncompliance=base_event.penalties_for_noncompliance,
                renewal_frequency_months=frequency_months,
                recurring=True,
                notes=base_event.notes
            )

            self.add_event(new_event)
            event_ids.append(new_event.event_id)

            base_date = new_due_date

        logger.info(f"Scheduled {occurrences} recurring events")

        return event_ids

    def export_calendar(self, format: str = "json") -> str:
        """Export compliance calendar."""
        if format == "json":
            events_data = []

            for event in self.events.values():
                events_data.append({
                    "event_id": event.event_id,
                    "title": event.title,
                    "type": event.event_type,
                    "due_date": event.due_date,
                    "status": event.status,
                    "priority": event.priority,
                    "jurisdiction": event.jurisdiction,
                    "responsible_party": event.responsible_party
                })

            return json.dumps(events_data, indent=2)

        return ""

    def get_statistics(self) -> Dict:
        """Generate compliance calendar statistics."""
        return {
            "total_events": len(self.events),
            "completed_events": sum(1 for e in self.events.values() if e.status == EventStatus.COMPLETED.value),
            "overdue_events": len(self.get_overdue_events()),
            "upcoming_30_days": len(self.get_upcoming_deadlines(30)),
            "total_reminders": len(self.reminders),
            "active_reminders": sum(1 for r in self.reminders.values() if r.is_active),
            "total_audits": len(self.audits),
            "average_compliance_rate": self.get_compliance_rate(),
            "last_updated": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    calendar = ComplianceCalendar()

    # Create compliance event
    event = ComplianceEvent(
        event_id="COMP_001",
        event_type=ComplianceEventType.FILING_DEADLINE.value,
        title="Q1 Regulatory Filing",
        description="Quarterly regulatory compliance filing",
        responsible_party="Compliance Manager",
        responsible_email="compliance@company.com",
        jurisdiction="US Federal",
        regulatory_body="SEC",
        due_date="2024-04-30",
        start_date="2024-04-01",
        submission_method="EDGAR",
        priority=PriorityLevel.HIGH.value,
        status=EventStatus.SCHEDULED.value,
        renewal_frequency_months=3,
        recurring=True
    )

    calendar.add_event(event)

    # Add required document
    document = ComplianceDocument(
        document_id="DOC_001",
        document_type="Form 10-Q",
        description="Quarterly Report",
        required=True,
        submission_deadline="2024-04-30",
        status="not_started",
        preparer="Accounting Team"
    )

    calendar.add_required_document("COMP_001", document)

    # Schedule reminders
    calendar.schedule_reminders("COMP_001", [30, 14, 7, 1], ["compliance@company.com"])

    # Get upcoming deadlines
    upcoming = calendar.get_upcoming_deadlines(30)
    print(f"Upcoming deadlines: {len(upcoming)}")

    # Get dashboard
    dashboard = calendar.get_compliance_dashboard()
    print(json.dumps(dashboard, indent=2))
