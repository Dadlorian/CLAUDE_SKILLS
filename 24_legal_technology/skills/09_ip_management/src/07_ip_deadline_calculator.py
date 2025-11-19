"""
IP Deadline Calculator
Calculates key deadlines for patent and trademark applications globally
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class DeadlineType(Enum):
    """Types of IP deadlines"""
    FILING = "filing"
    PUBLICATION = "publication"
    EXAMINATION = "examination"
    RESPONSE = "response"
    OPPOSITION = "opposition"
    RENEWAL = "renewal"
    PCT_PHASES = "pct_phases"
    PRIORITY = "priority"


@dataclass
class Deadline:
    """IP deadline details"""
    description: str
    due_date: datetime
    deadline_type: DeadlineType
    jurisdiction: str
    is_critical: bool = False
    grace_period: Optional[timedelta] = None
    notes: Optional[str] = None

    @property
    def days_until(self) -> int:
        """Days until deadline"""
        return (self.due_date - datetime.now()).days

    @property
    def is_overdue(self) -> bool:
        """Check if deadline is overdue"""
        return self.days_until < 0

    @property
    def status(self) -> str:
        """Get deadline status"""
        if self.is_overdue:
            return "overdue"
        elif self.days_until <= 7:
            return "urgent"
        elif self.days_until <= 30:
            return "approaching"
        else:
            return "normal"


class DeadlineCalculator:
    """Calculate IP deadlines"""

    def __init__(self):
        """Initialize deadline calculator"""
        self.rules = self._load_deadline_rules()

    def calculate_patent_deadlines(
        self,
        filing_date: datetime,
        jurisdiction: str = "US"
    ) -> List[Deadline]:
        """
        Calculate key deadlines for patent application

        Args:
            filing_date: Patent filing date
            jurisdiction: Country code (US, EP, etc.)

        Returns:
            List of deadlines
        """
        deadlines = []

        try:
            if jurisdiction == "US":
                deadlines = self._calculate_us_patent_deadlines(filing_date)
            elif jurisdiction == "EP":
                deadlines = self._calculate_ep_patent_deadlines(filing_date)
            elif jurisdiction == "PCT":
                deadlines = self._calculate_pct_deadlines(filing_date)
            elif jurisdiction == "JP":
                deadlines = self._calculate_jp_patent_deadlines(filing_date)
            elif jurisdiction == "CN":
                deadlines = self._calculate_cn_patent_deadlines(filing_date)
            else:
                logger.warning(f"Unknown jurisdiction: {jurisdiction}")

            return deadlines

        except Exception as e:
            logger.error(f"Failed to calculate deadlines: {e}")
            return []

    def calculate_trademark_deadlines(
        self,
        filing_date: datetime,
        jurisdiction: str = "US"
    ) -> List[Deadline]:
        """
        Calculate key deadlines for trademark application

        Args:
            filing_date: Trademark filing date
            jurisdiction: Country code

        Returns:
            List of deadlines
        """
        deadlines = []

        try:
            if jurisdiction == "US":
                deadlines = self._calculate_us_trademark_deadlines(filing_date)
            elif jurisdiction == "EU":
                deadlines = self._calculate_eu_trademark_deadlines(filing_date)
            elif jurisdiction == "WIPO":
                deadlines = self._calculate_wipo_deadlines(filing_date)
            else:
                logger.warning(f"Unknown jurisdiction: {jurisdiction}")

            return deadlines

        except Exception as e:
            logger.error(f"Failed to calculate trademark deadlines: {e}")
            return []

    def _calculate_us_patent_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate US patent deadlines"""
        deadlines = []

        # Publication deadline (18 months from earliest filing date)
        publication_date = filing_date + timedelta(days=18*30)
        deadlines.append(Deadline(
            description="Patent Publication (18-month rule)",
            due_date=publication_date,
            deadline_type=DeadlineType.PUBLICATION,
            jurisdiction="US",
            is_critical=True,
            notes="Unless non-publication request made"
        ))

        # Response to office action (typically 3 months)
        response_date = filing_date + timedelta(days=90)
        deadlines.append(Deadline(
            description="Response to First Office Action",
            due_date=response_date,
            deadline_type=DeadlineType.RESPONSE,
            jurisdiction="US",
            is_critical=True,
            grace_period=timedelta(days=30)
        ))

        # Final office action response (3 months)
        final_response = filing_date + timedelta(days=180)
        deadlines.append(Deadline(
            description="Response to Final Office Action",
            due_date=final_response,
            deadline_type=DeadlineType.RESPONSE,
            jurisdiction="US",
            is_critical=True
        ))

        # Issue fee (3 months from notice of allowance)
        issue_fee_date = filing_date + timedelta(days=730)
        deadlines.append(Deadline(
            description="Issue Fee Payment",
            due_date=issue_fee_date,
            deadline_type=DeadlineType.FILING,
            jurisdiction="US",
            is_critical=True
        ))

        # Maintenance fees
        maintenance_fees = [
            (3.5 * 365, "First Maintenance Fee (3.5 years)"),
            (7 * 365, "Second Maintenance Fee (7 years)"),
            (11.5 * 365, "Third Maintenance Fee (11.5 years)"),
        ]

        for days_offset, description in maintenance_fees:
            deadlines.append(Deadline(
                description=description,
                due_date=filing_date + timedelta(days=days_offset),
                deadline_type=DeadlineType.RENEWAL,
                jurisdiction="US",
                is_critical=True,
                grace_period=timedelta(days=180)
            ))

        return deadlines

    def _calculate_ep_patent_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate European patent deadlines"""
        deadlines = []

        # Examination request (before expiration of 19 months from filing)
        exam_request = filing_date + timedelta(days=19*30)
        deadlines.append(Deadline(
            description="Examination Request",
            due_date=exam_request,
            deadline_type=DeadlineType.EXAMINATION,
            jurisdiction="EP",
            is_critical=True
        ))

        # Response to examination report (typically 6 months)
        response_date = filing_date + timedelta(days=19*30 + 180)
        deadlines.append(Deadline(
            description="Response to Examination Report",
            due_date=response_date,
            deadline_type=DeadlineType.RESPONSE,
            jurisdiction="EP",
            is_critical=True,
            grace_period=timedelta(days=30)
        ))

        # Renewal fees (annual from 3rd year)
        for year in range(3, 21):
            renewal_date = filing_date + timedelta(days=year*365)
            deadlines.append(Deadline(
                description=f"Renewal Fee (Year {year})",
                due_date=renewal_date,
                deadline_type=DeadlineType.RENEWAL,
                jurisdiction="EP",
                is_critical=True,
                grace_period=timedelta(days=180)
            ))

        return deadlines

    def _calculate_pct_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate PCT (Patent Cooperation Treaty) deadlines"""
        deadlines = []

        # International publication (18 months)
        pub_date = filing_date + timedelta(days=18*30)
        deadlines.append(Deadline(
            description="International Publication",
            due_date=pub_date,
            deadline_type=DeadlineType.PUBLICATION,
            jurisdiction="PCT",
            is_critical=True
        ))

        # International Search Report (typically 9 months)
        search_report = filing_date + timedelta(days=9*30)
        deadlines.append(Deadline(
            description="International Search Report",
            due_date=search_report,
            deadline_type=DeadlineType.EXAMINATION,
            jurisdiction="PCT",
            is_critical=False
        ))

        # Entry into national phase (30 months from priority date)
        national_phase = filing_date + timedelta(days=30*30)
        deadlines.append(Deadline(
            description="Entry into National Phase",
            due_date=national_phase,
            deadline_type=DeadlineType.FILING,
            jurisdiction="PCT",
            is_critical=True,
            notes="Can extend to 31 months for some offices"
        ))

        return deadlines

    def _calculate_jp_patent_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate Japanese patent deadlines"""
        deadlines = []

        # Examination request (3 years)
        exam_request = filing_date + timedelta(days=3*365)
        deadlines.append(Deadline(
            description="Examination Request",
            due_date=exam_request,
            deadline_type=DeadlineType.EXAMINATION,
            jurisdiction="JP",
            is_critical=True
        ))

        # Response to office action
        response_date = filing_date + timedelta(days=90)
        deadlines.append(Deadline(
            description="Response to Office Action",
            due_date=response_date,
            deadline_type=DeadlineType.RESPONSE,
            jurisdiction="JP",
            is_critical=True
        ))

        return deadlines

    def _calculate_cn_patent_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate Chinese patent deadlines"""
        deadlines = []

        # Substantive examination request (within 3 years)
        exam_request = filing_date + timedelta(days=3*365)
        deadlines.append(Deadline(
            description="Substantive Examination Request",
            due_date=exam_request,
            deadline_type=DeadlineType.EXAMINATION,
            jurisdiction="CN",
            is_critical=True
        ))

        return deadlines

    def _calculate_us_trademark_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate US trademark deadlines"""
        deadlines = []

        # Use statement (6 months or intent to use)
        use_deadline = filing_date + timedelta(days=6*30)
        deadlines.append(Deadline(
            description="Use Statement or Extension Request",
            due_date=use_deadline,
            deadline_type=DeadlineType.FILING,
            jurisdiction="US",
            is_critical=True,
            grace_period=timedelta(days=30)
        ))

        # Publication for opposition (typically 12-18 months)
        pub_date = filing_date + timedelta(days=15*30)
        deadlines.append(Deadline(
            description="Publication for Opposition",
            due_date=pub_date,
            deadline_type=DeadlineType.PUBLICATION,
            jurisdiction="US",
            is_critical=False
        ))

        # Renewal (every 10 years)
        renewal_dates = [
            (5*365, "First Renewal"),
            (10*365, "Second Renewal"),
        ]

        for days_offset, description in renewal_dates:
            deadlines.append(Deadline(
                description=description,
                due_date=filing_date + timedelta(days=days_offset),
                deadline_type=DeadlineType.RENEWAL,
                jurisdiction="US",
                is_critical=True,
                grace_period=timedelta(days=180)
            ))

        return deadlines

    def _calculate_eu_trademark_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate EU trademark deadlines"""
        deadlines = []

        # Opposition period (3 months from publication)
        opposition_deadline = filing_date + timedelta(days=18*30 + 90)
        deadlines.append(Deadline(
            description="Opposition Deadline",
            due_date=opposition_deadline,
            deadline_type=DeadlineType.OPPOSITION,
            jurisdiction="EU",
            is_critical=True,
            grace_period=timedelta(days=180)
        ))

        # Renewal (every 10 years)
        renewal_date = filing_date + timedelta(days=10*365)
        deadlines.append(Deadline(
            description="First Renewal",
            due_date=renewal_date,
            deadline_type=DeadlineType.RENEWAL,
            jurisdiction="EU",
            is_critical=True,
            grace_period=timedelta(days=180)
        ))

        return deadlines

    def _calculate_wipo_deadlines(self, filing_date: datetime) -> List[Deadline]:
        """Calculate WIPO (Madrid Protocol) deadlines"""
        deadlines = []

        # International registration (provisional 18 months)
        intl_reg = filing_date + timedelta(days=18*30)
        deadlines.append(Deadline(
            description="International Registration",
            due_date=intl_reg,
            deadline_type=DeadlineType.FILING,
            jurisdiction="WIPO",
            is_critical=True
        ))

        # Renewal (every 10 years)
        renewal_date = filing_date + timedelta(days=10*365)
        deadlines.append(Deadline(
            description="First Renewal",
            due_date=renewal_date,
            deadline_type=DeadlineType.RENEWAL,
            jurisdiction="WIPO",
            is_critical=True
        ))

        return deadlines

    def get_upcoming_deadlines(
        self,
        deadlines: List[Deadline],
        days_ahead: int = 90
    ) -> List[Deadline]:
        """
        Filter deadlines that are upcoming

        Args:
            deadlines: List of all deadlines
            days_ahead: Number of days to look ahead

        Returns:
            Filtered list of upcoming deadlines
        """
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        upcoming = [d for d in deadlines if now <= d.due_date <= future]
        upcoming.sort(key=lambda x: x.due_date)

        return upcoming

    def get_critical_deadlines(self, deadlines: List[Deadline]) -> List[Deadline]:
        """Get only critical deadlines"""
        return [d for d in deadlines if d.is_critical]

    def _load_deadline_rules(self) -> Dict[str, any]:
        """Load deadline rules for different jurisdictions"""
        return {}


class DeadlineReminder:
    """Manage deadline reminders"""

    def __init__(self, calculator: DeadlineCalculator):
        """
        Initialize reminder

        Args:
            calculator: DeadlineCalculator instance
        """
        self.calculator = calculator
        self.reminders = []

    def add_reminder(
        self,
        deadline: Deadline,
        reminder_days: int = 30
    ) -> None:
        """
        Add reminder for deadline

        Args:
            deadline: Deadline to remind
            reminder_days: Days before deadline to remind
        """
        reminder_date = deadline.due_date - timedelta(days=reminder_days)
        self.reminders.append({
            "deadline": deadline,
            "reminder_date": reminder_date,
            "sent": False
        })

    def get_due_reminders(self) -> List[Deadline]:
        """Get reminders that are due"""
        now = datetime.now()
        due = []

        for reminder in self.reminders:
            if reminder["reminder_date"] <= now and not reminder["sent"]:
                due.append(reminder["deadline"])
                reminder["sent"] = True

        return due


class DeadlineReport:
    """Generate deadline reports"""

    def __init__(self, deadlines: List[Deadline]):
        """Initialize report"""
        self.deadlines = deadlines

    def generate_summary(self) -> str:
        """Generate summary report"""
        # Sort by urgency
        sorted_deadlines = sorted(
            self.deadlines,
            key=lambda x: (x.is_overdue, x.days_until)
        )

        report = "IP DEADLINE REPORT\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        critical = [d for d in sorted_deadlines if d.is_critical]
        if critical:
            report += "CRITICAL DEADLINES:\n"
            for deadline in critical[:5]:
                report += f"- {deadline.description}: {deadline.due_date.strftime('%Y-%m-%d')} "
                report += f"({deadline.days_until} days) [{deadline.status}]\n"

        return report

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "total_deadlines": len(self.deadlines),
            "critical_count": sum(1 for d in self.deadlines if d.is_critical),
            "urgent_count": sum(1 for d in self.deadlines if d.days_until <= 7),
            "overdue_count": sum(1 for d in self.deadlines if d.is_overdue),
            "deadlines": [
                {
                    "description": d.description,
                    "due_date": d.due_date.isoformat(),
                    "days_until": d.days_until,
                    "status": d.status,
                    "type": d.deadline_type.value,
                    "jurisdiction": d.jurisdiction
                }
                for d in sorted(self.deadlines, key=lambda x: x.due_date)
            ]
        }


def main():
    """Example usage"""
    calculator = DeadlineCalculator()

    # Calculate US patent deadlines
    filing_date = datetime(2023, 1, 15)
    us_deadlines = calculator.calculate_patent_deadlines(filing_date, "US")

    print("US Patent Deadlines:")
    for deadline in us_deadlines[:3]:
        print(f"  {deadline.description}: {deadline.due_date.strftime('%Y-%m-%d')}")

    # Get upcoming deadlines
    upcoming = calculator.get_upcoming_deadlines(us_deadlines, days_ahead=365)
    print(f"\nUpcoming deadlines (next 365 days): {len(upcoming)}")

    # Generate report
    report = DeadlineReport(us_deadlines)
    print(report.generate_summary())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
