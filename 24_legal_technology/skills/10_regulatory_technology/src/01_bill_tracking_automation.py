"""
Bill Tracking Automation Module

Monitors legislative bills at federal, state, and local levels with real-time
updates, sponsor tracking, committee assignments, and action notifications.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Configure logging
logger = logging.getLogger(__name__)


class BillStatus(Enum):
    """Legislative bill status enumeration."""
    INTRODUCED = "introduced"
    IN_COMMITTEE = "in_committee"
    COMMITTEE_PASSED = "committee_passed"
    FLOOR_DEBATE = "floor_debate"
    PASSED_CHAMBER = "passed_chamber"
    SENT_TO_OTHER_CHAMBER = "sent_to_other_chamber"
    ENACTED = "enacted"
    DIED = "died"
    VETOED = "vetoed"


class Legislative_Level(Enum):
    """Scope of legislation."""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"


@dataclass
class BillSponsor:
    """Bill sponsor information."""
    member_id: str
    name: str
    party: str
    chamber: str
    district: str
    email: str
    phone: str


@dataclass
class BillAction:
    """Legislative action on a bill."""
    date: str
    chamber: str
    action_type: str
    description: str
    status_change: Optional[str]
    notes: Optional[str]


@dataclass
class Bill:
    """Comprehensive bill tracking data."""
    bill_id: str
    number: str
    title: str
    description: str
    level: str  # federal, state, local
    jurisdiction: str  # e.g., "US Federal", "CA State", "NYC Local"
    status: str
    introduced_date: str
    sponsors: List[BillSponsor]
    cosponsors: List[BillSponsor]
    committee_assignments: List[Dict]
    fiscal_impact: Optional[float]
    status_history: List[BillAction]
    documents: List[Dict]
    last_updated: str
    next_action_date: Optional[str]
    tracking_keywords: List[str]
    industry_impact: Optional[str]


class BillTrackingAutomation:
    """
    Automates monitoring and tracking of legislative bills.

    Features:
    - Real-time bill status monitoring
    - Sponsor and committee tracking
    - Action history and timeline management
    - Impact assessment and keyword matching
    - Notification and alert generation
    """

    def __init__(self, db_path: str = None):
        """Initialize bill tracking system."""
        self.db_path = db_path
        self.bills: Dict[str, Bill] = {}
        self.tracked_keywords: List[str] = []
        self.jurisdictions: List[str] = []
        self.notification_handlers: List = []
        logger.info("Bill Tracking Automation initialized")

    def add_bill_to_track(self, bill: Bill, keywords: List[str] = None) -> str:
        """
        Add a bill to the tracking system.

        Args:
            bill: Bill object to track
            keywords: Keywords for impact assessment

        Returns:
            Bill ID for reference
        """
        if bill.bill_id in self.bills:
            logger.warning(f"Bill {bill.bill_id} already tracked")
            return bill.bill_id

        if keywords:
            bill.tracking_keywords = keywords

        self.bills[bill.bill_id] = bill
        logger.info(f"Bill {bill.bill_id} added to tracking")

        return bill.bill_id

    def update_bill_status(
        self,
        bill_id: str,
        new_status: BillStatus,
        action: BillAction,
        send_notification: bool = True
    ) -> bool:
        """
        Update bill status and record action.

        Args:
            bill_id: Bill identifier
            new_status: New status enumeration
            action: Action details
            send_notification: Whether to notify subscribers

        Returns:
            Success indicator
        """
        if bill_id not in self.bills:
            logger.error(f"Bill {bill_id} not found in tracking")
            return False

        bill = self.bills[bill_id]
        old_status = bill.status
        bill.status = new_status.value
        bill.status_history.append(action)
        bill.last_updated = datetime.now().isoformat()

        # Trigger notifications
        if send_notification:
            self._notify_subscribers(
                bill_id,
                f"Status change: {old_status} -> {new_status.value}",
                bill
            )

        logger.info(f"Bill {bill_id} status updated to {new_status.value}")
        return True

    def get_bills_by_sponsor(self, member_id: str) -> List[Bill]:
        """Retrieve all bills sponsored by a member."""
        return [
            bill for bill in self.bills.values()
            if any(sponsor.member_id == member_id for sponsor in bill.sponsors)
        ]

    def get_bills_by_committee(self, committee_name: str) -> List[Bill]:
        """Get bills assigned to a specific committee."""
        matching_bills = []
        for bill in self.bills.values():
            if any(
                c.get("name") == committee_name
                for c in bill.committee_assignments
            ):
                matching_bills.append(bill)
        return matching_bills

    def get_bills_by_status(self, status: BillStatus) -> List[Bill]:
        """Retrieve bills by current status."""
        return [
            bill for bill in self.bills.values()
            if bill.status == status.value
        ]

    def get_bills_by_jurisdiction(self, jurisdiction: str) -> List[Bill]:
        """Get bills from specific jurisdiction."""
        return [
            bill for bill in self.bills.values()
            if bill.jurisdiction == jurisdiction
        ]

    def detect_related_bills(self, bill_id: str) -> List[Tuple[str, float]]:
        """
        Detect bills with similar content or sponsors.

        Returns list of (bill_id, similarity_score) tuples.
        """
        if bill_id not in self.bills:
            return []

        source_bill = self.bills[bill_id]
        related = []
        source_keywords = set(source_bill.tracking_keywords)

        for other_id, other_bill in self.bills.items():
            if other_id == bill_id:
                continue

            # Check keyword overlap
            keyword_overlap = len(
                source_keywords & set(other_bill.tracking_keywords)
            ) / len(source_keywords) if source_keywords else 0

            # Check sponsor overlap
            source_sponsors = {s.member_id for s in source_bill.sponsors}
            other_sponsors = {s.member_id for s in other_bill.sponsors}
            sponsor_overlap = len(
                source_sponsors & other_sponsors
            ) / len(source_sponsors) if source_sponsors else 0

            # Combined similarity score
            similarity = (keyword_overlap * 0.6) + (sponsor_overlap * 0.4)

            if similarity > 0.3:
                related.append((other_id, similarity))

        return sorted(related, key=lambda x: x[1], reverse=True)

    def generate_status_report(
        self,
        jurisdiction: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive bill tracking report.

        Args:
            jurisdiction: Filter by jurisdiction (optional)

        Returns:
            Report dictionary with statistics and summaries
        """
        bills_to_report = (
            [b for b in self.bills.values() if b.jurisdiction == jurisdiction]
            if jurisdiction else list(self.bills.values())
        )

        if not bills_to_report:
            return {"total_bills": 0, "bills_by_status": {}}

        status_counts = {}
        high_impact_bills = []

        for bill in bills_to_report:
            status = bill.status
            status_counts[status] = status_counts.get(status, 0) + 1

            # Identify high-impact bills
            if bill.fiscal_impact and bill.fiscal_impact > 1_000_000:
                high_impact_bills.append({
                    "bill_id": bill.bill_id,
                    "title": bill.title,
                    "fiscal_impact": bill.fiscal_impact
                })

        return {
            "total_bills": len(bills_to_report),
            "bills_by_status": status_counts,
            "high_impact_bills": sorted(
                high_impact_bills,
                key=lambda x: x["fiscal_impact"],
                reverse=True
            ),
            "jurisdictions": list(set(b.jurisdiction for b in bills_to_report)),
            "last_generated": datetime.now().isoformat()
        }

    def get_action_timeline(self, bill_id: str) -> List[Dict]:
        """Get chronological action timeline for a bill."""
        if bill_id not in self.bills:
            return []

        bill = self.bills[bill_id]
        timeline = [
            {
                "date": action.date,
                "action": action.description,
                "chamber": action.chamber,
                "status_change": action.status_change
            }
            for action in sorted(
                bill.status_history,
                key=lambda a: a.date
            )
        ]

        return timeline

    def identify_priority_bills(
        self,
        criteria: Dict
    ) -> List[Bill]:
        """
        Identify bills matching priority criteria.

        Criteria keys: fiscal_impact_min, status, keywords, sponsors
        """
        priority_bills = list(self.bills.values())

        if "fiscal_impact_min" in criteria:
            priority_bills = [
                b for b in priority_bills
                if b.fiscal_impact and b.fiscal_impact >= criteria["fiscal_impact_min"]
            ]

        if "status" in criteria:
            priority_bills = [
                b for b in priority_bills
                if b.status == criteria["status"]
            ]

        if "keywords" in criteria:
            keyword_set = set(criteria["keywords"])
            priority_bills = [
                b for b in priority_bills
                if any(kw in keyword_set for kw in b.tracking_keywords)
            ]

        if "sponsors" in criteria:
            sponsor_ids = set(criteria["sponsors"])
            priority_bills = [
                b for b in priority_bills
                if any(s.member_id in sponsor_ids for s in b.sponsors)
            ]

        return priority_bills

    def _notify_subscribers(
        self,
        bill_id: str,
        message: str,
        bill: Bill
    ) -> None:
        """Send notifications to registered handlers."""
        for handler in self.notification_handlers:
            try:
                handler({
                    "bill_id": bill_id,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "status": bill.status,
                    "title": bill.title
                })
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")

    def export_tracked_bills(self, format: str = "json") -> str:
        """Export all tracked bills in specified format."""
        bills_data = [asdict(bill) for bill in self.bills.values()]

        if format == "json":
            return json.dumps(bills_data, indent=2, default=str)
        elif format == "csv":
            # Simplified CSV export
            if not bills_data:
                return ""

            headers = list(bills_data[0].keys())
            csv_lines = [",".join(headers)]
            for bill in bills_data:
                csv_lines.append(
                    ",".join(str(bill.get(h, "")) for h in headers)
                )
            return "\n".join(csv_lines)

        return ""


if __name__ == "__main__":
    # Example usage
    tracker = BillTrackingAutomation()

    # Create sample bill
    sample_bill = Bill(
        bill_id="HR_2024_001",
        number="HR 1234",
        title="Climate Action and Clean Energy Act",
        description="Comprehensive legislation for climate mitigation",
        level=Legislative_Level.FEDERAL.value,
        jurisdiction="US Federal",
        status=BillStatus.IN_COMMITTEE.value,
        introduced_date="2024-01-15",
        sponsors=[
            BillSponsor(
                member_id="HOUSE_001",
                name="Rep. John Smith",
                party="Democrat",
                chamber="House",
                district="CA-12",
                email="john.smith@house.gov",
                phone="202-555-0100"
            )
        ],
        cosponsors=[],
        committee_assignments=[{"name": "Energy and Commerce", "assigned_date": "2024-01-20"}],
        fiscal_impact=5_000_000.00,
        status_history=[
            BillAction(
                date="2024-01-15",
                chamber="House",
                action_type="introduced",
                description="Bill introduced in House",
                status_change=BillStatus.INTRODUCED.value,
                notes=None
            )
        ],
        documents=[{"name": "Bill Text", "url": "https://example.com/bill.pdf"}],
        last_updated=datetime.now().isoformat(),
        next_action_date="2024-02-01",
        tracking_keywords=["climate", "energy", "emissions"],
        industry_impact="Energy sector"
    )

    # Track the bill
    bill_id = tracker.add_bill_to_track(
        sample_bill,
        keywords=["climate", "energy", "renewable"]
    )
    print(f"Tracking bill: {bill_id}")

    # Generate report
    report = tracker.generate_status_report()
    print(json.dumps(report, indent=2))
