"""
Deadline Calculator - Automatic Calculation of Legal Deadlines
Calculates deadlines based on jurisdictions, rules, and event dates
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum


class JurisdictionType(Enum):
    """Jurisdiction types"""
    FEDERAL = "Federal"
    STATE = "State"
    COURT = "Court"
    AGENCY = "Agency"


class DeadlineType(Enum):
    """Types of legal deadlines"""
    STATUTE_OF_LIMITATIONS = "Statute of Limitations"
    DISCOVERY_DEADLINE = "Discovery Deadline"
    MOTION_DEADLINE = "Motion Deadline"
    FILING_DEADLINE = "Filing Deadline"
    RESPONSE_DEADLINE = "Response Deadline"
    APPEAL_DEADLINE = "Appeal Deadline"
    PAYMENT_DEADLINE = "Payment Deadline"
    COMPLIANCE_DEADLINE = "Compliance Deadline"


class DeadlineCalculator:
    """Calculate legal deadlines based on jurisdiction rules"""

    # Jurisdiction-specific rules (simplified examples)
    JURISDICTION_RULES = {
        "federal": {
            "response_to_complaint": 21,  # days
            "motion_to_dismiss": 21,
            "discovery_initial": 30,
            "discovery_response": 30,
            "trial_motion": 28,
            "appeal": 30,
            "business_days": False
        },
        "ca": {
            "response_to_complaint": 30,
            "motion_to_dismiss": 30,
            "discovery_initial": 10,
            "discovery_response": 30,
            "trial_motion": 16,
            "appeal": 60,
            "business_days": False
        },
        "ny": {
            "response_to_complaint": 30,
            "motion_to_dismiss": 30,
            "discovery_initial": 20,
            "discovery_response": 30,
            "trial_motion": 35,
            "appeal": 30,
            "business_days": True
        },
        "tx": {
            "response_to_complaint": 21,
            "motion_to_dismiss": 21,
            "discovery_initial": 28,
            "discovery_response": 30,
            "trial_motion": 21,
            "appeal": 30,
            "business_days": True
        }
    }

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize deadline calculator

        Args:
            api_key: API key for legal research service
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def calculate_deadline(self, start_date: datetime,
                          days: int,
                          jurisdiction: str = "federal",
                          use_business_days: bool = None,
                          exclude_holidays: bool = True) -> datetime:
        """
        Calculate deadline from start date

        Args:
            start_date: Starting date (event that triggers deadline)
            days: Number of days allowed
            jurisdiction: Jurisdiction code (federal, ca, ny, tx, etc.)
            use_business_days: If True, exclude weekends; if None, use jurisdiction default
            exclude_holidays: If True, exclude holidays from count

        Returns:
            Calculated deadline datetime
        """
        if use_business_days is None:
            use_business_days = self.JURISDICTION_RULES.get(
                jurisdiction.lower(),
                {}
            ).get("business_days", False)

        current_date = start_date
        days_counted = 0

        while days_counted < days:
            current_date += timedelta(days=1)

            # Check if day should be counted
            if use_business_days:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() >= 5:
                    continue

            if exclude_holidays:
                # Skip holidays
                if self._is_holiday(current_date):
                    continue

            days_counted += 1

        return current_date

    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a federal holiday"""
        # Simplified federal holidays
        holidays = [
            (1, 1),    # New Year's Day
            (1, 20),   # MLK Day
            (2, 17),   # Presidents Day
            (5, 26),   # Memorial Day
            (7, 4),    # Independence Day
            (9, 7),    # Labor Day
            (10, 12),  # Columbus Day
            (11, 11),  # Veterans Day
            (11, 23),  # Thanksgiving
            (12, 25),  # Christmas
        ]

        return (date.month, date.day) in holidays

    def calculate_statute_of_limitations(self, incident_date: datetime,
                                         claim_type: str,
                                         jurisdiction: str) -> Dict[str, Any]:
        """
        Calculate statute of limitations deadline

        Args:
            incident_date: Date of incident
            claim_type: Type of claim (e.g., contract, personal_injury, property)
            jurisdiction: Jurisdiction

        Returns:
            Statute of limitations information
        """
        # Simplified SOL periods by claim type
        sol_periods = {
            "contract": 4,  # years
            "personal_injury": 3,
            "medical_malpractice": 3,
            "property_damage": 3,
            "fraud": 3,
            "breach_of_warranty": 4,
            "workers_compensation": 1,
            "product_liability": 3
        }

        years = sol_periods.get(claim_type.lower(), 3)
        deadline = incident_date + timedelta(days=365 * years)

        today = datetime.now()
        days_remaining = (deadline - today).days

        return {
            "incident_date": incident_date.isoformat(),
            "claim_type": claim_type,
            "jurisdiction": jurisdiction,
            "sol_period_years": years,
            "deadline": deadline.isoformat(),
            "days_remaining": max(0, days_remaining),
            "status": "CRITICAL" if days_remaining < 30 else ("WARNING" if days_remaining < 90 else "OK"),
            "expired": days_remaining < 0
        }

    def calculate_case_deadlines(self, matter_id: str,
                                 event_date: datetime,
                                 event_type: str,
                                 jurisdiction: str) -> Dict[str, Any]:
        """
        Calculate all related case deadlines from a triggering event

        Args:
            matter_id: Matter ID
            event_date: Date of triggering event
            event_type: Type of event (e.g., "service_of_complaint")
            jurisdiction: Jurisdiction

        Returns:
            Dictionary of calculated deadlines
        """
        rules = self.JURISDICTION_RULES.get(jurisdiction.lower(), {})
        deadlines = {}

        # Map event types to deadline rules
        deadline_mappings = {
            "service_of_complaint": [
                ("response_to_complaint", DeadlineType.RESPONSE_DEADLINE),
                ("motion_to_dismiss", DeadlineType.MOTION_DEADLINE)
            ],
            "discovery_request": [
                ("discovery_response", DeadlineType.DISCOVERY_DEADLINE)
            ],
            "trial_date_set": [
                ("trial_motion", DeadlineType.MOTION_DEADLINE)
            ],
            "judgment": [
                ("appeal", DeadlineType.APPEAL_DEADLINE)
            ]
        }

        if event_type in deadline_mappings:
            for rule_key, deadline_type in deadline_mappings[event_type]:
                if rule_key in rules:
                    days = rules[rule_key]
                    deadline_date = self.calculate_deadline(
                        event_date,
                        days,
                        jurisdiction,
                        rules.get("business_days", False)
                    )

                    deadlines[rule_key] = {
                        "type": deadline_type.value,
                        "deadline_date": deadline_date.isoformat(),
                        "days_allowed": days,
                        "event_date": event_date.isoformat(),
                        "jurisdiction": jurisdiction
                    }

        return {
            "matter_id": matter_id,
            "event": event_type,
            "event_date": event_date.isoformat(),
            "jurisdiction": jurisdiction,
            "calculated_deadlines": deadlines,
            "calculation_date": datetime.now().isoformat()
        }

    def create_deadline_tasks(self, matter_id: str,
                             deadline_data: Dict[str, Any],
                             attorney_id: str,
                             lead_time_days: int = 7) -> List[Dict[str, Any]]:
        """
        Create tasks for deadline reminders

        Args:
            matter_id: Matter ID
            deadline_data: Calculated deadline data
            attorney_id: Responsible attorney ID
            lead_time_days: Days before deadline to create task

        Returns:
            List of created task records
        """
        tasks = []

        for deadline_key, deadline_info in deadline_data.get("calculated_deadlines", {}).items():
            deadline_date = datetime.fromisoformat(deadline_info["deadline_date"])
            task_due_date = deadline_date - timedelta(days=lead_time_days)

            task = {
                "matter_id": matter_id,
                "title": f"DEADLINE: {deadline_info['type']} - {deadline_key}",
                "description": f"""
Deadline Type: {deadline_info['type']}
Jurisdiction: {deadline_info['jurisdiction']}
Days Allowed: {deadline_info['days_allowed']}
Event Date: {deadline_info['event_date']}
FINAL DEADLINE: {deadline_info['deadline_date']}
                """,
                "due_date": task_due_date.isoformat(),
                "final_deadline": deadline_info["deadline_date"],
                "priority": "High",
                "assigned_to": attorney_id,
                "status": "Open",
                "category": "Deadline Reminder"
            }

            tasks.append(task)

        return tasks

    def check_deadline_proximity(self, deadline_date: datetime,
                                warning_threshold_days: int = 7) -> Dict[str, Any]:
        """
        Check if deadline is approaching

        Args:
            deadline_date: Deadline date
            warning_threshold_days: Days until deadline to issue warning

        Returns:
            Deadline proximity status
        """
        today = datetime.now()
        days_until = (deadline_date - today).days

        if days_until < 0:
            status = "OVERDUE"
            alert_level = "CRITICAL"
        elif days_until == 0:
            status = "TODAY"
            alert_level = "CRITICAL"
        elif days_until <= warning_threshold_days:
            status = "APPROACHING"
            alert_level = "HIGH"
        else:
            status = "OK"
            alert_level = "NORMAL"

        return {
            "deadline_date": deadline_date.isoformat(),
            "days_until": max(0, days_until),
            "status": status,
            "alert_level": alert_level,
            "check_date": today.isoformat()
        }

    def bulk_calculate_deadlines(self, matters: List[Dict[str, Any]],
                                jurisdiction: str) -> List[Dict[str, Any]]:
        """
        Calculate deadlines for multiple matters

        Args:
            matters: List of matter data with event information
            jurisdiction: Jurisdiction for all matters

        Returns:
            List of deadline calculations for each matter
        """
        results = []

        for matter in matters:
            try:
                deadlines = self.calculate_case_deadlines(
                    matter.get("id"),
                    datetime.fromisoformat(matter.get("event_date")),
                    matter.get("event_type"),
                    jurisdiction
                )
                results.append(deadlines)
            except Exception as e:
                results.append({
                    "matter_id": matter.get("id"),
                    "error": str(e)
                })

        return results


# Example usage
if __name__ == "__main__":
    calculator = DeadlineCalculator(api_key="your_api_key")

    # Calculate statute of limitations
    incident_date = datetime(2021, 6, 15)
    sol = calculator.calculate_statute_of_limitations(
        incident_date,
        "personal_injury",
        "ca"
    )
    print(f"Statute of Limitations: {sol['deadline']}")

    # Calculate response deadline
    service_date = datetime.now()
    response_deadline = calculator.calculate_deadline(
        service_date,
        21,  # Federal rules
        "federal"
    )
    print(f"Response Deadline: {response_deadline.date()}")

    # Calculate multiple deadlines
    case_deadlines = calculator.calculate_case_deadlines(
        "matter_123",
        datetime.now(),
        "service_of_complaint",
        "federal"
    )
    print(f"Case Deadlines: {case_deadlines}")
