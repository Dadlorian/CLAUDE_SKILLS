"""
Deadline Calculator - Automated legal deadline calculation for multiple jurisdictions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json


class JurisdictionType(Enum):
    """Jurisdiction types"""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"


class DeadlineType(Enum):
    """Types of legal deadlines"""
    MOTION_RESPONSE = "motion_response"
    DISCOVERY_RESPONSE = "discovery_response"
    APPEAL = "appeal"
    ANSWER = "answer"
    REPLY = "reply"
    SUMMARY_JUDGMENT = "summary_judgment"
    TRIAL_BRIEF = "trial_brief"


class ServiceMethod(Enum):
    """Methods of service"""
    PERSONAL = "personal"
    MAIL = "mail"
    ELECTRONIC = "electronic"
    PUBLICATION = "publication"


class HolidayCalendar:
    """Holiday calendar for deadline calculation"""

    FEDERAL_HOLIDAYS = {
        "01-01": "New Year's Day",
        "01-21": "MLK Day",
        "02-18": "Presidents Day",
        "05-27": "Memorial Day",
        "06-19": "Juneteenth",
        "07-04": "Independence Day",
        "09-02": "Labor Day",
        "10-14": "Columbus Day",
        "11-11": "Veterans Day",
        "11-28": "Thanksgiving",
        "12-25": "Christmas"
    }

    def __init__(self, state_holidays: Optional[Dict[str, str]] = None,
                 court_closures: Optional[List[datetime]] = None):
        """
        Initialize holiday calendar

        Args:
            state_holidays: State-specific holidays (MMDD: "Holiday Name")
            court_closures: List of specific court closure dates
        """
        self.holidays = self.FEDERAL_HOLIDAYS.copy()
        if state_holidays:
            self.holidays.update(state_holidays)
        self.closures = court_closures or []

    def is_holiday(self, date: datetime) -> bool:
        """Check if date is a federal or state holiday"""
        month_day = date.strftime("%m-%d")
        return month_day in self.holidays

    def is_court_closed(self, date: datetime) -> bool:
        """Check if court is closed on date"""
        return date in self.closures

    def is_business_day(self, date: datetime) -> bool:
        """Check if date is a business day"""
        # Exclude weekends (Saturday=5, Sunday=6)
        if date.weekday() >= 5:
            return False
        # Exclude holidays
        if self.is_holiday(date):
            return False
        # Exclude court closures
        if self.is_court_closed(date):
            return False
        return True


class DeadlineRule:
    """Deadline calculation rule"""

    def __init__(self, rule_name: str, rule_code: str, jurisdiction: str,
                 base_days: int, service_addition_days: int = 0,
                 excludes_weekends: bool = True, excludes_holidays: bool = True):
        """
        Initialize deadline rule

        Args:
            rule_name: Human-readable rule name
            rule_code: Rule code (e.g., "FRCP 6")
            jurisdiction: Jurisdiction (federal, state, local)
            base_days: Base number of days
            service_addition_days: Additional days for service method
            excludes_weekends: Whether rule excludes weekends
            excludes_holidays: Whether rule excludes holidays
        """
        self.name = rule_name
        self.code = rule_code
        self.jurisdiction = jurisdiction
        self.base_days = base_days
        self.service_addition_days = service_addition_days
        self.excludes_weekends = excludes_weekends
        self.excludes_holidays = excludes_holidays


class DeadlineCalculator:
    """Calculates legal deadlines based on rules and calendars"""

    # Define common rules
    RULES = {
        "frcp_6_motion_response": DeadlineRule(
            "FRCP 6 - Motion Response",
            "FRCP 6",
            "federal",
            base_days=14,
            service_addition_days=3,
            excludes_weekends=True,
            excludes_holidays=True
        ),
        "frcp_26_discovery": DeadlineRule(
            "FRCP 26 - Discovery Response",
            "FRCP 26",
            "federal",
            base_days=30,
            service_addition_days=3,
            excludes_weekends=True,
            excludes_holidays=True
        ),
        "frcp_12_answer": DeadlineRule(
            "FRCP 12 - Answer",
            "FRCP 12",
            "federal",
            base_days=21,
            service_addition_days=3,
            excludes_weekends=True,
            excludes_holidays=True
        ),
        "frap_4_appeal": DeadlineRule(
            "FRAP 4 - Appeal",
            "FRAP 4",
            "federal",
            base_days=30,
            excludes_weekends=True,
            excludes_holidays=True
        )
    }

    def __init__(self, holiday_calendar: HolidayCalendar):
        """
        Initialize deadline calculator

        Args:
            holiday_calendar: HolidayCalendar instance
        """
        self.calendar = holiday_calendar

    def calculate_deadline(self, trigger_date: datetime, rule_code: str,
                          service_method: ServiceMethod = ServiceMethod.PERSONAL,
                          buffer_days: int = 0) -> Dict:
        """
        Calculate deadline based on trigger date and rule

        Args:
            trigger_date: Date that triggers the deadline (event date)
            rule_code: Rule code (key in RULES dictionary)
            service_method: Method of service
            buffer_days: Additional buffer days to add (internal safety margin)

        Returns:
            Deadline calculation result
        """
        if rule_code not in self.RULES:
            raise ValueError(f"Unknown rule code: {rule_code}")

        rule = self.RULES[rule_code]

        # Calculate deadline
        # Start from day after trigger event
        current_date = trigger_date + timedelta(days=1)
        days_counted = 0
        target_days = rule.base_days

        # Add service days if applicable
        if service_method == ServiceMethod.MAIL:
            target_days += 3
        elif service_method == ServiceMethod.ELECTRONIC:
            target_days += 3
        elif service_method == ServiceMethod.PUBLICATION:
            target_days += 30

        # Count business days until deadline
        while days_counted < target_days:
            if rule.excludes_weekends and current_date.weekday() >= 5:
                # Skip weekends
                current_date += timedelta(days=1)
                continue
            if rule.excludes_holidays and self.calendar.is_holiday(current_date):
                # Skip holidays
                current_date += timedelta(days=1)
                continue
            if self.calendar.is_court_closed(current_date):
                # Skip court closures
                current_date += timedelta(days=1)
                continue

            days_counted += 1
            if days_counted < target_days:
                current_date += timedelta(days=1)

        deadline_date = current_date

        # Add buffer
        buffer_date = deadline_date - timedelta(days=buffer_days)

        # Create reminder schedule
        reminders = self._create_reminder_schedule(deadline_date)

        return {
            "trigger_date": trigger_date.isoformat(),
            "rule": rule.code,
            "rule_name": rule.name,
            "service_method": service_method.value,
            "calendar_days": (deadline_date - trigger_date).days,
            "business_days": days_counted,
            "deadline_date": deadline_date.isoformat(),
            "buffer_date": buffer_date.isoformat(),
            "buffer_days": buffer_days,
            "reminders": reminders,
            "calculation_date": datetime.now().isoformat()
        }

    def _create_reminder_schedule(self, deadline_date: datetime) -> Dict[str, str]:
        """Create reminder schedule for deadline"""
        return {
            "60_days_before": (deadline_date - timedelta(days=60)).isoformat(),
            "30_days_before": (deadline_date - timedelta(days=30)).isoformat(),
            "14_days_before": (deadline_date - timedelta(days=14)).isoformat(),
            "7_days_before": (deadline_date - timedelta(days=7)).isoformat(),
            "3_days_before": (deadline_date - timedelta(days=3)).isoformat(),
            "1_day_before": (deadline_date - timedelta(days=1)).isoformat(),
            "deadline": deadline_date.isoformat()
        }

    def calculate_multiple_deadlines(self, trigger_date: datetime,
                                    rule_codes: List[str]) -> List[Dict]:
        """Calculate multiple deadlines for different rules"""
        results = []
        for rule_code in rule_codes:
            result = self.calculate_deadline(trigger_date, rule_code)
            results.append(result)
        return results

    def verify_deadline_compliance(self, submission_date: datetime,
                                  deadline_date: datetime) -> Dict:
        """Verify if submission meets deadline"""
        is_met = submission_date <= deadline_date
        days_remaining = (deadline_date - submission_date).days

        return {
            "deadline_date": deadline_date.isoformat(),
            "submission_date": submission_date.isoformat(),
            "deadline_met": is_met,
            "days_early": days_remaining if days_remaining > 0 else 0,
            "days_late": abs(days_remaining) if days_remaining < 0 else 0,
            "status": "COMPLIANT" if is_met else "LATE"
        }


class MultiJurisdictionDeadlineManager:
    """Manages deadlines across multiple jurisdictions"""

    def __init__(self):
        """Initialize multi-jurisdiction deadline manager"""
        # Initialize different calendars for different jurisdictions
        self.federal_calendar = HolidayCalendar()

        # State-specific calendars can be added
        self.state_calendars = {}

        self.calculators = {
            "federal": DeadlineCalculator(self.federal_calendar),
            "state": {}
        }

    def add_state_calendar(self, state: str, state_holidays: Dict[str, str],
                          court_closures: Optional[List[datetime]] = None) -> None:
        """Add state-specific calendar"""
        calendar = HolidayCalendar(state_holidays, court_closures)
        self.state_calendars[state] = calendar
        self.calculators["state"][state] = DeadlineCalculator(calendar)

    def calculate_across_jurisdictions(self, trigger_date: datetime,
                                      jurisdictions: List[str]) -> Dict:
        """Calculate same deadline across multiple jurisdictions"""
        results = {}

        for jurisdiction in jurisdictions:
            if jurisdiction == "federal":
                calc = self.calculators["federal"]
            elif jurisdiction.startswith("state_"):
                state = jurisdiction.split("_")[1]
                if state in self.state_calendars:
                    calc = self.calculators["state"][state]
                else:
                    continue
            else:
                continue

            # Use motion response rule as example
            result = calc.calculate_deadline(trigger_date, "frcp_6_motion_response")
            results[jurisdiction] = result

        return results


# Example usage
if __name__ == "__main__":
    # Initialize calendar
    calendar = HolidayCalendar()

    # Initialize calculator
    calculator = DeadlineCalculator(calendar)

    # Example trigger event: Motion filed today
    trigger_date = datetime(2025, 1, 15)

    # Calculate motion response deadline (14 days)
    result = calculator.calculate_deadline(
        trigger_date=trigger_date,
        rule_code="frcp_6_motion_response",
        service_method=ServiceMethod.PERSONAL,
        buffer_days=3  # Add 3 days internal buffer
    )

    print("Motion Response Deadline Calculation:")
    print(f"  Trigger Date: {result['trigger_date']}")
    print(f"  Rule: {result['rule_name']}")
    print(f"  Calendar Days: {result['calendar_days']}")
    print(f"  Business Days: {result['business_days']}")
    print(f"  Deadline Date: {result['deadline_date']}")
    print(f"  Buffer Date: {result['buffer_date']}")
    print("\nReminder Schedule:")
    for reminder, date in result['reminders'].items():
        print(f"  {reminder}: {date}")

    # Calculate multiple deadlines
    print("\n\nMultiple Deadlines from Same Trigger:")
    multiple_results = calculator.calculate_multiple_deadlines(
        trigger_date=trigger_date,
        rule_codes=["frcp_6_motion_response", "frcp_26_discovery", "frcp_12_answer"]
    )

    for result in multiple_results:
        print(f"  {result['rule_name']}: {result['deadline_date']}")

    # Verify compliance
    submission_date = datetime(2025, 1, 27)
    compliance = calculator.verify_deadline_compliance(submission_date,
                                                       datetime.fromisoformat(result['deadline_date']))
    print(f"\n\nCompliance Check:")
    print(f"  Status: {compliance['status']}")
    print(f"  Days Early: {compliance['days_early']}")
