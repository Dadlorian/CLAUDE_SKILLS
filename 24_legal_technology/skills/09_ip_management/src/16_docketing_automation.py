"""
IP Docketing Automation System Example
Automates critical deadline tracking and filing management
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class DocketType(Enum):
    """Types of docket entries"""
    PATENT_APPLICATION = "patent_application"
    PATENT_GRANT = "patent_grant"
    TRADEMARK_APPLICATION = "trademark_application"
    TRADEMARK_REGISTRATION = "trademark_registration"
    MAINTENANCE_FEE = "maintenance_fee"
    ANNUITY_FEE = "annuity_fee"
    RENEWAL = "renewal"
    OFFICE_ACTION_DUE = "office_action_due"
    IDS_SUBMISSION = "ids_submission"
    APPEAL = "appeal"


class DocketStatus(Enum):
    """Status of docket item"""
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"


@dataclass
class DocketEntry:
    """Individual docket entry"""
    docket_id: str
    asset_id: str
    asset_type: str  # patent, trademark
    docket_type: DocketType
    description: str
    due_date: datetime
    jurisdiction: str
    responsible_party: str
    status: DocketStatus
    priority: int  # 1-5, 1 being highest
    created_date: datetime
    completion_date: Optional[datetime] = None
    notes: str = ""
    related_dockets: List[str] = field(default_factory=list)


@dataclass
class AutomationRule:
    """Rule for automating docket creation"""
    rule_id: str
    trigger_event: str  # 'filing', 'grant', 'office_action'
    action: str  # docket type to create
    days_ahead: int  # how many days before deadline
    enabled: bool = True


class DocketingAutomationSystem:
    """Automate IP docketing and deadline tracking"""

    def __init__(self):
        self.dockets: Dict[str, DocketEntry] = {}
        self.automation_rules: List[AutomationRule] = []
        self.docket_counter = 0
        self.calendar = defaultdict(list)  # date -> list of dockets

    def add_docket(self, docket: DocketEntry):
        """Add docket entry"""
        self.dockets[docket.docket_id] = docket
        calendar_key = docket.due_date.strftime("%Y-%m-%d")
        self.calendar[calendar_key].append(docket.docket_id)

    def add_automation_rule(self, rule: AutomationRule):
        """Add automation rule"""
        self.automation_rules.append(rule)

    def process_filing_event(self, asset_id: str, asset_type: str,
                             filing_date: datetime, jurisdiction: str) -> List[str]:
        """
        Process filing event and create associated dockets

        Args:
            asset_id: Asset ID
            asset_type: Type of asset
            filing_date: Filing date
            jurisdiction: Jurisdiction

        Returns:
            List of created docket IDs
        """
        created_dockets = []

        # Define standard docket events for filing
        filing_events = [
            {
                'type': DocketType.OFFICE_ACTION_DUE,
                'days_ahead': 120,
                'description': 'Respond to Office Action'
            },
            {
                'type': DocketType.MAINTENANCE_FEE,
                'days_ahead': 365 * 3,  # 3 years
                'description': 'Pay Maintenance Fee (3.5 years)'
            },
            {
                'type': DocketType.MAINTENANCE_FEE,
                'days_ahead': 365 * 7,  # 7 years
                'description': 'Pay Maintenance Fee (7.5 years)'
            },
            {
                'type': DocketType.MAINTENANCE_FEE,
                'days_ahead': 365 * 11,  # 11 years
                'description': 'Pay Maintenance Fee (11.5 years)'
            }
        ]

        for event in filing_events:
            due_date = filing_date + timedelta(days=event['days_ahead'])

            docket = DocketEntry(
                docket_id=f"DOCKET_{self.docket_counter}",
                asset_id=asset_id,
                asset_type=asset_type,
                docket_type=event['type'],
                description=event['description'],
                due_date=due_date,
                jurisdiction=jurisdiction,
                responsible_party="IP Team",
                status=DocketStatus.PENDING,
                priority=1 if (due_date - datetime.now()).days < 180 else 2,
                created_date=datetime.now()
            )

            self.docket_counter += 1
            self.add_docket(docket)
            created_dockets.append(docket.docket_id)

        return created_dockets

    def get_urgent_dockets(self, days_ahead: int = 30) -> List[DocketEntry]:
        """
        Get urgent dockets coming due

        Args:
            days_ahead: Days to look ahead

        Returns:
            List of urgent dockets
        """
        urgent = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        for docket in self.dockets.values():
            if (docket.status in [DocketStatus.PENDING, DocketStatus.IN_PROGRESS] and
                docket.due_date <= cutoff_date):
                urgent.append(docket)

        return sorted(urgent, key=lambda x: (x.priority, x.due_date))

    def check_overdue_dockets(self) -> List[DocketEntry]:
        """
        Check for overdue dockets

        Returns:
            List of overdue dockets
        """
        overdue = []

        for docket in self.dockets.values():
            if docket.status == DocketStatus.PENDING and docket.due_date < datetime.now():
                overdue.append(docket)

        return sorted(overdue, key=lambda x: x.due_date)

    def generate_docket_calendar(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Generate calendar view of dockets

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Calendar of dockets
        """
        calendar_view = {}
        current_date = start_date

        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            day_dockets = []

            for docket_id in self.calendar.get(date_key, []):
                if docket_id in self.dockets:
                    docket = self.dockets[docket_id]
                    if docket.status in [DocketStatus.PENDING, DocketStatus.IN_PROGRESS]:
                        day_dockets.append({
                            'docket_id': docket.docket_id,
                            'asset_id': docket.asset_id,
                            'type': docket.docket_type.value,
                            'description': docket.description,
                            'priority': docket.priority,
                            'status': docket.status.value
                        })

            if day_dockets:
                calendar_view[date_key] = sorted(day_dockets, key=lambda x: x['priority'])

            current_date += timedelta(days=1)

        return calendar_view

    def update_docket_status(self, docket_id: str, status: DocketStatus,
                            completion_date: Optional[datetime] = None):
        """
        Update docket status

        Args:
            docket_id: Docket ID
            status: New status
            completion_date: Completion date if applicable
        """
        if docket_id in self.dockets:
            self.dockets[docket_id].status = status
            if status == DocketStatus.COMPLETED:
                self.dockets[docket_id].completion_date = completion_date or datetime.now()

    def get_dockets_by_asset(self, asset_id: str) -> List[DocketEntry]:
        """
        Get all dockets for an asset

        Args:
            asset_id: Asset ID

        Returns:
            List of dockets for asset
        """
        return [d for d in self.dockets.values() if d.asset_id == asset_id]

    def get_dockets_by_jurisdiction(self, jurisdiction: str) -> List[DocketEntry]:
        """
        Get dockets by jurisdiction

        Args:
            jurisdiction: Jurisdiction code

        Returns:
            List of dockets in jurisdiction
        """
        return [d for d in self.dockets.values() if d.jurisdiction == jurisdiction]

    def calculate_docket_metrics(self) -> Dict:
        """
        Calculate key docket metrics

        Returns:
            Dictionary with metrics
        """
        total_dockets = len(self.dockets)
        pending_count = sum(1 for d in self.dockets.values() if d.status == DocketStatus.PENDING)
        overdue_count = sum(1 for d in self.dockets.values() if d.status == DocketStatus.OVERDUE)
        completed_count = sum(1 for d in self.dockets.values() if d.status == DocketStatus.COMPLETED)

        # Dockets due in next 30 days
        upcoming_30 = self.get_urgent_dockets(30)

        # Breakdown by type
        type_breakdown = defaultdict(int)
        for docket in self.dockets.values():
            type_breakdown[docket.docket_type.value] += 1

        return {
            'total_dockets': total_dockets,
            'pending': pending_count,
            'overdue': overdue_count,
            'completed': completed_count,
            'completion_rate': (completed_count / total_dockets * 100) if total_dockets > 0 else 0,
            'upcoming_30_days': len(upcoming_30),
            'type_breakdown': dict(type_breakdown),
            'priority_distribution': {
                'critical': sum(1 for d in self.dockets.values() if d.priority == 1),
                'high': sum(1 for d in self.dockets.values() if d.priority == 2),
                'medium': sum(1 for d in self.dockets.values() if d.priority == 3),
                'low': sum(1 for d in self.dockets.values() if d.priority >= 4)
            }
        }

    def generate_docketing_report(self) -> Dict:
        """
        Generate comprehensive docketing report

        Returns:
            Complete docking analysis
        """
        return {
            'report_date': datetime.now().isoformat(),
            'metrics': self.calculate_docket_metrics(),
            'urgent_dockets': [
                {
                    'docket_id': d.docket_id,
                    'asset_id': d.asset_id,
                    'description': d.description,
                    'due_date': d.due_date.isoformat(),
                    'days_remaining': (d.due_date - datetime.now()).days,
                    'priority': d.priority
                }
                for d in self.get_urgent_dockets(30)
            ],
            'overdue_dockets': [
                {
                    'docket_id': d.docket_id,
                    'asset_id': d.asset_id,
                    'description': d.description,
                    'due_date': d.due_date.isoformat(),
                    'days_overdue': (datetime.now() - d.due_date).days
                }
                for d in self.check_overdue_dockets()
            ]
        }


# Example usage
if __name__ == "__main__":
    system = DocketingAutomationSystem()

    # Process filing events
    filing_date = datetime.now() - timedelta(days=100)
    created = system.process_filing_event("US7234567", "patent", filing_date, "US")
    print(f"Created {len(created)} dockets from filing event")

    # Generate report
    report = system.generate_docketing_report()
    print("\nDocketing Report")
    print(f"Total Dockets: {report['metrics']['total_dockets']}")
    print(f"Pending: {report['metrics']['pending']}")
    print(f"Due in 30 days: {report['metrics']['upcoming_30_days']}")
    print(f"Overdue: {len(report['overdue_dockets'])}")
