"""
IP Docketing System Example
Manages IP deadlines and events
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class IPType(Enum):
    """Types of intellectual property"""
    PATENT = "patent"
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    TRADE_SECRET = "trade_secret"

class EventType(Enum):
    """Types of IP events"""
    FILING = "filing"
    PUBLICATION = "publication"
    OFFICE_ACTION = "office_action"
    RESPONSE_DUE = "response_due"
    ISSUANCE = "issuance"
    RENEWAL = "renewal"
    ASSIGNMENT = "assignment"
    MAINTENANCE_FEE = "maintenance_fee"

@dataclass
class DocketedEvent:
    """Represents a docketed event"""
    case_number: str
    event_type: EventType
    due_date: datetime
    description: str
    responsible_party: str
    status: str  # pending, completed, overdue
    priority: int  # 1-5, 5 highest
    notes: Optional[str] = None

class IPDocketingSystem:
    """Manage IP deadlines and docketing"""

    def __init__(self):
        self.dockets: Dict[str, List[DocketedEvent]] = {}
        self.ip_assets: Dict[str, Dict] = {}
        self.alert_lead_time_days = 30  # Alert N days before deadline

    def register_ip_asset(self, case_number: str, ip_type: IPType,
                         title: str, jurisdiction: str = "US"):
        """Register an IP asset in the system"""
        self.ip_assets[case_number] = {
            'ip_type': ip_type,
            'title': title,
            'jurisdiction': jurisdiction,
            'created_date': datetime.now()
        }
        self.dockets[case_number] = []

    def add_event(self, case_number: str, event_type: EventType,
                 due_date: datetime, description: str,
                 responsible_party: str, priority: int = 3,
                 notes: Optional[str] = None):
        """Add a docketed event"""
        if case_number not in self.dockets:
            raise ValueError(f"Case {case_number} not registered")

        event = DocketedEvent(
            case_number=case_number,
            event_type=event_type,
            due_date=due_date,
            description=description,
            responsible_party=responsible_party,
            status="pending",
            priority=priority,
            notes=notes
        )

        self.dockets[case_number].append(event)

    def get_upcoming_deadlines(self, days: int = 30) -> List[DocketedEvent]:
        """Get deadlines due within specified days"""
        today = datetime.now()
        cutoff_date = today + timedelta(days=days)

        upcoming = []
        for case_events in self.dockets.values():
            for event in case_events:
                if event.status == "pending" and today <= event.due_date <= cutoff_date:
                    upcoming.append(event)

        # Sort by due date
        upcoming.sort(key=lambda x: x.due_date)

        return upcoming

    def get_overdue_events(self) -> List[DocketedEvent]:
        """Get all overdue events"""
        today = datetime.now()
        overdue = []

        for case_events in self.dockets.values():
            for event in case_events:
                if event.status == "pending" and event.due_date < today:
                    overdue.append(event)
                    # Mark as overdue
                    event.status = "overdue"

        return overdue

    def mark_event_completed(self, case_number: str, event_type: EventType):
        """Mark an event as completed"""
        if case_number in self.dockets:
            for event in self.dockets[case_number]:
                if event.event_type == event_type and event.status == "pending":
                    event.status = "completed"

    def get_patent_maintenance_schedule(self, patent_number: str,
                                       issue_date: datetime) -> List[DocketedEvent]:
        """
        Generate maintenance fee schedule for a patent

        US patent maintenance fees due at:
        - 3.5 years after issuance
        - 7.5 years after issuance
        - 11.5 years after issuance
        """
        maintenance_schedule = []

        # Fee 1: 3.5 years
        fee1_date = issue_date + timedelta(days=1277)  # ~3.5 years
        maintenance_schedule.append(DocketedEvent(
            case_number=patent_number,
            event_type=EventType.MAINTENANCE_FEE,
            due_date=fee1_date,
            description="First maintenance fee",
            responsible_party="Patent Counsel",
            status="pending",
            priority=4
        ))

        # Fee 2: 7.5 years
        fee2_date = issue_date + timedelta(days=2739)  # ~7.5 years
        maintenance_schedule.append(DocketedEvent(
            case_number=patent_number,
            event_type=EventType.MAINTENANCE_FEE,
            due_date=fee2_date,
            description="Second maintenance fee",
            responsible_party="Patent Counsel",
            status="pending",
            priority=4
        ))

        # Fee 3: 11.5 years
        fee3_date = issue_date + timedelta(days=4200)  # ~11.5 years
        maintenance_schedule.append(DocketedEvent(
            case_number=patent_number,
            event_type=EventType.MAINTENANCE_FEE,
            due_date=fee3_date,
            description="Third maintenance fee",
            responsible_party="Patent Counsel",
            status="pending",
            priority=4
        ))

        return maintenance_schedule

    def get_case_summary(self, case_number: str) -> Dict:
        """Get summary of case including upcoming events"""
        if case_number not in self.ip_assets:
            return {}

        asset = self.ip_assets[case_number]
        events = self.dockets.get(case_number, [])

        # Separate by status
        pending_events = [e for e in events if e.status == "pending"]
        completed_events = [e for e in events if e.status == "completed"]
        overdue_events = [e for e in events if e.status == "overdue"]

        # Find next deadline
        next_deadline = None
        if pending_events:
            next_deadline = min(pending_events, key=lambda x: x.due_date)

        return {
            'case_number': case_number,
            'ip_type': asset['ip_type'].value,
            'title': asset['title'],
            'next_deadline': next_deadline.due_date if next_deadline else None,
            'pending_count': len(pending_events),
            'completed_count': len(completed_events),
            'overdue_count': len(overdue_events),
            'all_events': events
        }

    def generate_alert_report(self) -> Dict:
        """Generate alert report for upcoming and overdue items"""
        overdue = self.get_overdue_events()
        upcoming = self.get_upcoming_deadlines(self.alert_lead_time_days)

        # Group by priority
        alerts = {
            'critical': [e for e in overdue if e.priority >= 4],
            'important': [e for e in upcoming if e.priority >= 4],
            'standard': [e for e in upcoming if e.priority < 4],
            'overdue': overdue
        }

        return alerts


# Example usage
if __name__ == "__main__":
    system = IPDocketingSystem()

    # Register a patent
    system.register_ip_asset("US20210123456", IPType.PATENT,
                            "Machine Learning Patent")

    # Add events
    filing_date = datetime(2021, 1, 15)
    issue_date = datetime(2023, 6, 1)

    system.add_event("US20210123456", EventType.FILING,
                    filing_date, "Patent application filed",
                    "Patent Attorney", priority=5)

    system.add_event("US20210123456", EventType.ISSUANCE,
                    issue_date, "Patent issued",
                    "Patent Attorney", priority=5)

    # Add maintenance fees
    maintenance_events = system.get_patent_maintenance_schedule(
        "US20210123456", issue_date)
    for event in maintenance_events:
        system.dockets["US20210123456"].append(event)

    # Get upcoming deadlines
    upcoming = system.get_upcoming_deadlines(365)
    print(f"Upcoming deadlines in next year: {len(upcoming)}")

    # Get case summary
    summary = system.get_case_summary("US20210123456")
    print(f"Case: {summary['title']}")
    print(f"Pending items: {summary['pending_count']}")
