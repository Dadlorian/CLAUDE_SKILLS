"""
PAC Compliance - Manage Political Action Committee compliance and reporting.
Tracks contributions, disclosures, and FEC regulatory requirements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContributionType(Enum):
    """Types of PAC contributions."""
    MONETARY = "monetary"
    IN_KIND = "in_kind"
    INKIND_SERVICES = "inkind_services"


class ContributorType(Enum):
    """Types of PAC contributors."""
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    LABOR_UNION = "labor_union"
    OTHER_PAC = "other_pac"


class ExpenseType(Enum):
    """Types of PAC expenses."""
    CANDIDATE_SUPPORT = "candidate_support"
    INDEPENDENT_EXPENDITURE = "independent_expenditure"
    ADMINISTRATIVE = "administrative"
    FUNDRAISING = "fundraising"
    OVERHEAD = "overhead"


@dataclass
class Contributor:
    """Represents a PAC contributor."""
    contributor_id: str
    name: str
    contributor_type: ContributorType
    address: str
    occupation: Optional[str] = None
    employer: Optional[str] = None
    contributions: List['Contribution'] = field(default_factory=list)
    total_contributed: Decimal = Decimal('0.00')


@dataclass
class Contribution:
    """Represents a contribution to a PAC."""
    contribution_id: str
    contributor_id: str
    amount: Decimal
    contribution_type: ContributionType
    date_received: datetime
    description: str
    disclosed: bool = False
    disclosure_date: Optional[datetime] = None
    receipt_required: bool = True


@dataclass
class Expenditure:
    """Represents a PAC expenditure."""
    expenditure_id: str
    expense_type: ExpenseType
    amount: Decimal
    payee: str
    date: datetime
    description: str
    candidate: Optional[str] = None
    election: Optional[str] = None
    disclosed: bool = False


@dataclass
class FECReport:
    """Represents an FEC filing report."""
    report_id: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    submission_date: datetime
    report_type: str  # Form 3X, etc.
    contributions: List[Contribution] = field(default_factory=list)
    expenditures: List[Expenditure] = field(default_factory=list)
    cash_beginning: Decimal = Decimal('0.00')
    cash_ending: Decimal = Decimal('0.00')
    certifying_officer: str = ""
    filed: bool = False
    accepted_date: Optional[datetime] = None


class PACComplianceManager:
    """Manage PAC compliance and FEC reporting."""

    FEC_INDIVIDUAL_LIMIT = Decimal('5000.00')  # Per election cycle
    FEC_AGGREGATE_LIMIT = Decimal('50000.00')  # Calendar year
    FEC_REPORTING_THRESHOLD = Decimal('200.00')  # Itemization threshold

    def __init__(self, pac_name: str, fec_id: str):
        """Initialize PAC compliance manager."""
        self.pac_name = pac_name
        self.fec_id = fec_id
        self.contributors: Dict[str, Contributor] = {}
        self.contributions: Dict[str, Contribution] = {}
        self.expenditures: Dict[str, Expenditure] = {}
        self.fec_reports: Dict[str, FECReport] = {}
        self.cash_balance = Decimal('0.00')

    def register_contributor(
        self,
        name: str,
        contributor_type: ContributorType,
        address: str,
        occupation: str = None,
        employer: str = None
    ) -> Contributor:
        """Register a new PAC contributor."""
        contributor_id = f"contrib_{len(self.contributors) + 1}"

        contributor = Contributor(
            contributor_id=contributor_id,
            name=name,
            contributor_type=contributor_type,
            address=address,
            occupation=occupation,
            employer=employer
        )

        self.contributors[contributor_id] = contributor
        logger.info(f"Registered contributor: {name}")
        return contributor

    def record_contribution(
        self,
        contributor_id: str,
        amount: Decimal,
        contribution_type: ContributionType,
        description: str,
        date_received: datetime = None
    ) -> Optional[Contribution]:
        """Record a contribution to the PAC."""
        if contributor_id not in self.contributors:
            logger.error(f"Contributor not found: {contributor_id}")
            return None

        # Check FEC limits
        if not self._check_contribution_limits(contributor_id, amount):
            logger.warning(f"Contribution exceeds FEC limits: {amount}")

        contribution_id = f"contrib_trans_{len(self.contributions) + 1}"
        contributor = self.contributors[contributor_id]

        contribution = Contribution(
            contribution_id=contribution_id,
            contributor_id=contributor_id,
            amount=amount,
            contribution_type=contribution_type,
            date_received=date_received or datetime.now(),
            description=description
        )

        self.contributions[contribution_id] = contribution
        contributor.contributions.append(contribution)
        contributor.total_contributed += amount
        self.cash_balance += amount

        logger.info(f"Recorded contribution: {contributor_id} - ${amount}")
        return contribution

    def _check_contribution_limits(self, contributor_id: str, amount: Decimal) -> bool:
        """Check if contribution complies with FEC limits."""
        contributor = self.contributors.get(contributor_id)
        if not contributor:
            return False

        # Individuals and other PACs have different limits
        if contributor.contributor_type == ContributorType.INDIVIDUAL:
            if contributor.total_contributed + amount > self.FEC_INDIVIDUAL_LIMIT:
                return False

        return True

    def record_expenditure(
        self,
        expense_type: ExpenseType,
        amount: Decimal,
        payee: str,
        description: str,
        candidate: str = None,
        election: str = None
    ) -> Expenditure:
        """Record a PAC expenditure."""
        expenditure_id = f"exp_{len(self.expenditures) + 1}"

        expenditure = Expenditure(
            expenditure_id=expenditure_id,
            expense_type=expense_type,
            amount=amount,
            payee=payee,
            date=datetime.now(),
            description=description,
            candidate=candidate,
            election=election
        )

        self.expenditures[expenditure_id] = expenditure
        self.cash_balance -= amount

        logger.info(f"Recorded expenditure: {payee} - ${amount}")
        return expenditure

    def create_fec_report(
        self,
        reporting_period_start: datetime,
        reporting_period_end: datetime,
        report_type: str = "Form 3X"
    ) -> FECReport:
        """Create an FEC report."""
        report_id = f"fec_report_{len(self.fec_reports) + 1}"

        # Calculate contributions and expenditures in period
        period_contributions = [
            c for c in self.contributions.values()
            if reporting_period_start <= c.date_received <= reporting_period_end
        ]

        period_expenditures = [
            e for e in self.expenditures.values()
            if reporting_period_start <= e.date <= reporting_period_end
        ]

        total_contributions = sum(c.amount for c in period_contributions)
        total_expenditures = sum(e.amount for e in period_expenditures)

        report = FECReport(
            report_id=report_id,
            reporting_period_start=reporting_period_start,
            reporting_period_end=reporting_period_end,
            submission_date=datetime.now(),
            report_type=report_type,
            contributions=period_contributions,
            expenditures=period_expenditures,
            cash_beginning=Decimal('0.00'),  # Should be set from previous report
            cash_ending=self.cash_balance
        )

        self.fec_reports[report_id] = report
        logger.info(f"Created FEC report: {report_id}")
        return report

    def file_fec_report(self, report_id: str, certifying_officer: str) -> bool:
        """File an FEC report."""
        if report_id not in self.fec_reports:
            return False

        report = self.fec_reports[report_id]
        report.filed = True
        report.accepted_date = datetime.now()
        report.certifying_officer = certifying_officer

        logger.info(f"Filed FEC report: {report_id}")
        return True

    def get_disclosure_summary(self) -> Dict:
        """Get PAC disclosure summary."""
        total_contributions = sum(
            c.amount for c in self.contributions.values()
        )
        total_expenditures = sum(
            e.amount for e in self.expenditures.values()
        )

        undisclosed_contributions = [
            c for c in self.contributions.values()
            if not c.disclosed and c.amount >= self.FEC_REPORTING_THRESHOLD
        ]

        return {
            "pac_name": self.pac_name,
            "fec_id": self.fec_id,
            "total_contributions": float(total_contributions),
            "total_expenditures": float(total_expenditures),
            "cash_balance": float(self.cash_balance),
            "contributors": len(self.contributors),
            "contributions_requiring_disclosure": len(undisclosed_contributions),
            "reports_filed": len([r for r in self.fec_reports.values() if r.filed])
        }

    def verify_compliance(self) -> List[str]:
        """Verify PAC compliance status."""
        issues = []

        # Check for undisclosed contributions above threshold
        for contribution in self.contributions.values():
            if not contribution.disclosed and contribution.amount >= self.FEC_REPORTING_THRESHOLD:
                issues.append(
                    f"Contribution {contribution.contribution_id} requires disclosure"
                )

        # Check for filing deadlines
        # This would integrate with FEC deadlines

        return issues
