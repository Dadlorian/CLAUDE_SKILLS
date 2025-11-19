"""
Time Tracker - Legal Time Tracking and Billing Integration
Tracks billable hours, integrates with matter records, and generates billing data
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class TimeEntryStatus(Enum):
    """Time entry status"""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    BILLED = "Billed"
    REJECTED = "Rejected"


class ActivityType(Enum):
    """Types of legal activities"""
    CLIENT_MEETING = "Client Meeting"
    RESEARCH = "Research"
    WRITING = "Writing"
    DRAFTING = "Drafting"
    REVIEW = "Review"
    DEPOSITION = "Deposition"
    COURT_APPEARANCE = "Court Appearance"
    NEGOTIATION = "Negotiation"
    PHONE_CALL = "Phone Call"
    EMAIL_CORRESPONDENCE = "Email Correspondence"
    TRAVEL = "Travel"
    ADMINISTRATIVE = "Administrative"


@dataclass
class TimeEntry:
    """Time entry record"""
    date: datetime
    matter_id: str
    attorney_id: str
    duration_hours: float
    activity_type: str
    description: str
    billing_rate: Optional[float] = None
    status: str = TimeEntryStatus.DRAFT.value
    notes: Optional[str] = None


class TimeTracker:
    """Track legal time and manage billing"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize time tracker

        Args:
            api_key: Clio API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.pending_entries = []

    def _make_request(self, method: str, endpoint: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def start_time_entry(self, matter_id: str,
                        attorney_id: str,
                        activity_type: str) -> Dict[str, Any]:
        """
        Start a time entry (timer)

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID
            activity_type: Type of activity

        Returns:
            Time entry record
        """
        entry = {
            "matter_id": matter_id,
            "attorney_id": attorney_id,
            "activity_type": activity_type,
            "start_time": datetime.now().isoformat(),
            "status": "Running"
        }

        return entry

    def stop_time_entry(self, entry: Dict[str, Any],
                       description: str = "",
                       notes: str = "") -> TimeEntry:
        """
        Stop a running time entry

        Args:
            entry: Running time entry
            description: Work description
            notes: Additional notes

        Returns:
            Completed time entry
        """
        start = datetime.fromisoformat(entry["start_time"])
        end = datetime.now()
        duration_hours = (end - start).total_seconds() / 3600

        time_entry = TimeEntry(
            date=start,
            matter_id=entry["matter_id"],
            attorney_id=entry["attorney_id"],
            duration_hours=round(duration_hours, 2),
            activity_type=entry["activity_type"],
            description=description or f"Time entry - {entry['activity_type']}",
            notes=notes
        )

        return time_entry

    def create_time_entry(self, time_entry: TimeEntry) -> Dict[str, Any]:
        """
        Create time entry in system

        Args:
            time_entry: TimeEntry object

        Returns:
            Created time entry record
        """
        # Get attorney billing rate if not provided
        billing_rate = time_entry.billing_rate
        if not billing_rate:
            billing_rate = self._get_attorney_billing_rate(time_entry.attorney_id)

        entry_data = {
            "date": time_entry.date.isoformat(),
            "matter_id": time_entry.matter_id,
            "user_id": time_entry.attorney_id,
            "duration": time_entry.duration_hours,
            "description": time_entry.description,
            "activity_type": time_entry.activity_type,
            "billing_rate": billing_rate,
            "amount": time_entry.duration_hours * billing_rate if billing_rate else 0,
            "status": time_entry.status,
            "notes": time_entry.notes or ""
        }

        result = self._make_request("POST", "/time_entries", data=entry_data)
        self.pending_entries.append(result)

        return result

    def _get_attorney_billing_rate(self, attorney_id: str) -> float:
        """Get billing rate for attorney"""
        try:
            attorney = self._make_request("GET", f"/users/{attorney_id}")
            return attorney.get("billing_rate", 150.0)  # Default rate
        except:
            return 150.0

    def quick_time_entry(self, matter_id: str,
                        attorney_id: str,
                        hours: float,
                        activity_type: str,
                        description: str) -> Dict[str, Any]:
        """
        Create quick time entry without timer

        Args:
            matter_id: Matter ID
            attorney_id: Attorney ID
            hours: Number of hours
            activity_type: Type of activity
            description: Activity description

        Returns:
            Created time entry
        """
        time_entry = TimeEntry(
            date=datetime.now(),
            matter_id=matter_id,
            attorney_id=attorney_id,
            duration_hours=hours,
            activity_type=activity_type,
            description=description
        )

        return self.create_time_entry(time_entry)

    def get_time_entries_for_matter(self, matter_id: str,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get all time entries for a matter

        Args:
            matter_id: Matter ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of time entries
        """
        params = {"matter__id": matter_id, "limit": 500}

        if start_date:
            params["date__gte"] = start_date.isoformat()
        if end_date:
            params["date__lte"] = end_date.isoformat()

        response = self._make_request("GET", "/time_entries", params=params)
        return response.get("data", [])

    def get_attorney_hours(self, attorney_id: str,
                          start_date: datetime,
                          end_date: datetime) -> Dict[str, Any]:
        """
        Get total hours for attorney in period

        Args:
            attorney_id: Attorney ID
            start_date: Start date
            end_date: End date

        Returns:
            Hours summary
        """
        params = {
            "user_id": attorney_id,
            "date__gte": start_date.isoformat(),
            "date__lte": end_date.isoformat(),
            "limit": 500
        }

        response = self._make_request("GET", "/time_entries", params=params)
        entries = response.get("data", [])

        total_hours = sum(e.get("duration", 0) for e in entries)
        billable_hours = sum(
            e.get("duration", 0) for e in entries
            if e.get("billable", True)
        )

        by_activity = {}
        for entry in entries:
            activity = entry.get("activity_type", "Other")
            by_activity[activity] = by_activity.get(activity, 0) + entry.get("duration", 0)

        return {
            "attorney_id": attorney_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_hours": round(total_hours, 2),
            "billable_hours": round(billable_hours, 2),
            "non_billable_hours": round(total_hours - billable_hours, 2),
            "by_activity": {k: round(v, 2) for k, v in by_activity.items()},
            "entry_count": len(entries)
        }

    def calculate_billing_amount(self, matter_id: str,
                                start_date: datetime,
                                end_date: datetime) -> Dict[str, Any]:
        """
        Calculate billing amount for matter period

        Args:
            matter_id: Matter ID
            start_date: Start date
            end_date: End date

        Returns:
            Billing calculation
        """
        entries = self.get_time_entries_for_matter(matter_id, start_date, end_date)

        total_billable = 0
        total_non_billable = 0

        by_attorney = {}

        for entry in entries:
            attorney = entry.get("user_id")
            rate = entry.get("billing_rate", 150.0)
            hours = entry.get("duration", 0)
            amount = hours * rate

            if entry.get("billable", True):
                total_billable += amount
            else:
                total_non_billable += amount

            if attorney not in by_attorney:
                by_attorney[attorney] = {
                    "hours": 0,
                    "amount": 0,
                    "rate": rate
                }

            by_attorney[attorney]["hours"] += hours
            by_attorney[attorney]["amount"] += amount

        return {
            "matter_id": matter_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_billable_amount": round(total_billable, 2),
            "total_non_billable": round(total_non_billable, 2),
            "total_by_attorney": {
                k: {
                    "hours": round(v["hours"], 2),
                    "amount": round(v["amount"], 2),
                    "rate": v["rate"]
                }
                for k, v in by_attorney.items()
            },
            "entry_count": len(entries)
        }

    def submit_time_entries_for_review(self, matter_id: str,
                                       reviewer_id: str) -> Dict[str, Any]:
        """
        Submit time entries for attorney review/approval

        Args:
            matter_id: Matter ID
            reviewer_id: Attorney ID of reviewer

        Returns:
            Submission record
        """
        entries = self.get_time_entries_for_matter(matter_id)

        submission = {
            "matter_id": matter_id,
            "submission_date": datetime.now().isoformat(),
            "reviewer_id": reviewer_id,
            "entries_submitted": len(entries),
            "status": "Pending Review",
            "entry_ids": [e.get("id") for e in entries]
        }

        # Mark entries as submitted
        for entry in entries:
            self._make_request(
                "PUT",
                f"/time_entries/{entry.get('id')}",
                data={"status": TimeEntryStatus.SUBMITTED.value}
            )

        return submission

    def approve_time_entries(self, time_entry_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Approve multiple time entries

        Args:
            time_entry_ids: List of time entry IDs

        Returns:
            List of approved entries
        """
        approved = []

        for entry_id in time_entry_ids:
            result = self._make_request(
                "PUT",
                f"/time_entries/{entry_id}",
                data={
                    "status": TimeEntryStatus.APPROVED.value,
                    "approved_date": datetime.now().isoformat()
                }
            )
            approved.append(result)

        return approved

    def generate_time_summary(self, matters: List[str],
                             start_date: datetime,
                             end_date: datetime) -> Dict[str, Any]:
        """
        Generate time summary for multiple matters

        Args:
            matters: List of matter IDs
            start_date: Period start
            end_date: Period end

        Returns:
            Comprehensive time summary
        """
        summary = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "matters": {},
            "total_billable": 0,
            "total_hours": 0
        }

        for matter_id in matters:
            billing = self.calculate_billing_amount(matter_id, start_date, end_date)
            summary["matters"][matter_id] = billing
            summary["total_billable"] += billing.get("total_billable_amount", 0)
            summary["total_hours"] += sum(
                e.get("duration", 0)
                for e in self.get_time_entries_for_matter(matter_id, start_date, end_date)
            )

        return summary


# Example usage
if __name__ == "__main__":
    tracker = TimeTracker(api_key="your_clio_api_key")

    # Start a timer
    # entry = tracker.start_time_entry("matter_123", "attorney_456", "Research")

    # After work is done, stop timer
    # completed = tracker.stop_time_entry(entry, "Research on contract law")
    # tracker.create_time_entry(completed)

    # Or quick entry without timer
    # time_entry = tracker.quick_time_entry(
    #     "matter_123",
    #     "attorney_456",
    #     2.5,
    #     "Client Meeting",
    #     "Initial client consultation"
    # )

    # Get attorney hours
    # hours = tracker.get_attorney_hours("attorney_456", datetime(2024, 1, 1), datetime.now())
    # print(f"Total hours: {hours['total_hours']}")
