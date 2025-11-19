"""
Lobbying Expenditure Tracker Module

Tracks lobbying spending, registrations, and disclosures at federal and state
levels. Integrates with LDA (Lobbying Disclosure Act) filings and supports
expenditure analysis, client tracking, and transparency reporting.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

logger = logging.getLogger(__name__)


class LobbyingLevel(Enum):
    """Lobbying jurisdiction levels."""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"


class LobbyingActivityType(Enum):
    """Types of lobbying activities."""
    DIRECT_LOBBYING = "direct_lobbying"
    GRASSROOTS_LOBBYING = "grassroots_lobbying"
    PAID_ADVERTISEMENT = "paid_advertisement"
    COALITION_WORK = "coalition_work"
    COALITION_FUNDING = "coalition_funding"


@dataclass
class LobbyingRegistrant:
    """Registered lobbyist information."""
    registrant_id: str
    firm_name: str
    principal_client: str
    registration_date: str
    contact_person: str
    email: str
    phone: str
    address: str
    jurisdiction_level: str  # federal, state, local
    issues_lobbied: List[str]
    registration_status: str  # active, terminated, amended
    lobbying_experience: str
    estimated_compensation: Optional[Decimal]


@dataclass
class LobbyingExpenditure:
    """Individual lobbying expenditure record."""
    expenditure_id: str
    registrant_id: str
    client_name: str
    activity_type: str
    amount: Decimal
    date: str
    quarter: str  # Q1, Q2, Q3, Q4
    year: int
    recipient_name: str
    recipient_type: str  # Member of Congress, Agency Official, etc.
    purpose: str
    disclosure_form: str  # LDA, State Form, etc.
    jurisdiction: str
    metrics: Dict = field(default_factory=dict)


@dataclass
class LobbyistProfile:
    """Profile of individual lobbyist."""
    lobbyist_id: str
    full_name: str
    current_firm: str
    previous_firms: List[str]
    registration_date: str
    principal_clients: List[str]
    revolving_door_background: Optional[Dict]  # Government experience
    issue_expertise: List[str]
    disclosure_filings: int
    total_compensation_tracked: Decimal
    active_registrations: int


@dataclass
class LobbyingClient:
    """Lobbying client (principal) profile."""
    client_id: str
    client_name: str
    industry_sector: str
    headquarters: str
    lobbying_budget_estimate: Decimal
    current_registrants: List[str]
    issues_of_interest: List[str]
    jurisdictions_lobbied: List[str]
    annual_filings: List[str]
    first_filing_date: str
    last_filing_date: str
    transparency_score: float


class LobbyingExpenditureTracker:
    """
    Comprehensive lobbying expenditure tracking and analysis system.

    Features:
    - Registration and registrant management
    - Expenditure tracking and reporting
    - Client lobbying profile monitoring
    - Revolving door analysis (government-to-lobbyist transitions)
    - Transparency and disclosure compliance
    - Spending pattern analysis
    """

    def __init__(self):
        """Initialize tracking system."""
        self.registrants: Dict[str, LobbyingRegistrant] = {}
        self.expenditures: Dict[str, LobbyingExpenditure] = {}
        self.lobbyists: Dict[str, LobbyistProfile] = {}
        self.clients: Dict[str, LobbyingClient] = {}
        self.disclosure_filings: List[Dict] = []
        logger.info("Lobbying Expenditure Tracker initialized")

    def register_registrant(self, registrant: LobbyingRegistrant) -> str:
        """Register a lobbying entity."""
        if registrant.registrant_id in self.registrants:
            logger.warning(f"Registrant {registrant.registrant_id} already registered")
            return registrant.registrant_id

        self.registrants[registrant.registrant_id] = registrant
        logger.info(f"Registrant registered: {registrant.firm_name}")

        return registrant.registrant_id

    def record_expenditure(
        self,
        expenditure: LobbyingExpenditure,
        validate_disclosure: bool = True
    ) -> str:
        """
        Record a lobbying expenditure.

        Args:
            expenditure: Expenditure details
            validate_disclosure: Whether to validate against disclosure requirements

        Returns:
            Expenditure ID
        """
        if validate_disclosure:
            if not self._validate_disclosure_requirements(expenditure):
                logger.warning(f"Expenditure {expenditure.expenditure_id} may not meet disclosure requirements")

        self.expenditures[expenditure.expenditure_id] = expenditure
        logger.info(f"Expenditure recorded: {expenditure.expenditure_id}")

        return expenditure.expenditure_id

    def _validate_disclosure_requirements(self, expenditure: LobbyingExpenditure) -> bool:
        """Validate expenditure meets LDA disclosure thresholds."""
        # Federal LDA threshold: $3,000 per quarter
        federal_threshold = Decimal("3000")

        if expenditure.jurisdiction == "federal":
            return expenditure.amount >= federal_threshold

        return True

    def register_lobbyist(self, lobbyist: LobbyistProfile) -> str:
        """Register individual lobbyist profile."""
        if lobbyist.lobbyist_id in self.lobbyists:
            logger.warning(f"Lobbyist {lobbyist.lobbyist_id} already registered")
            return lobbyist.lobbyist_id

        self.lobbyists[lobbyist.lobbyist_id] = lobbyist
        logger.info(f"Lobbyist registered: {lobbyist.full_name}")

        return lobbyist.lobbyist_id

    def register_client(self, client: LobbyingClient) -> str:
        """Register lobbying client (principal)."""
        if client.client_id in self.clients:
            logger.warning(f"Client {client.client_id} already registered")
            return client.client_id

        self.clients[client.client_id] = client
        logger.info(f"Client registered: {client.client_name}")

        return client.client_id

    def get_total_spending_by_client(
        self,
        client_name: str,
        year: Optional[int] = None
    ) -> Dict:
        """Get total lobbying spending by client."""
        matching_expenditures = [
            exp for exp in self.expenditures.values()
            if exp.client_name == client_name and (year is None or exp.year == year)
        ]

        total = sum(exp.amount for exp in matching_expenditures)

        return {
            "client_name": client_name,
            "year": year,
            "total_spending": total,
            "expenditure_count": len(matching_expenditures),
            "breakdown_by_activity": self._breakdown_by_field(
                matching_expenditures,
                "activity_type"
            ),
            "top_recipients": self._get_top_recipients(matching_expenditures, 5)
        }

    def get_total_spending_by_registrant(
        self,
        registrant_id: str,
        year: Optional[int] = None
    ) -> Dict:
        """Get total spending by registrant/firm."""
        matching_expenditures = [
            exp for exp in self.expenditures.values()
            if exp.registrant_id == registrant_id and (year is None or exp.year == year)
        ]

        total = sum(exp.amount for exp in matching_expenditures)
        registrant = self.registrants.get(registrant_id)

        return {
            "registrant_id": registrant_id,
            "registrant_name": registrant.firm_name if registrant else "Unknown",
            "year": year,
            "total_spending": total,
            "client_count": len(set(exp.client_name for exp in matching_expenditures)),
            "clients": list(set(exp.client_name for exp in matching_expenditures)),
            "quarterly_breakdown": self._breakdown_by_field(
                matching_expenditures,
                "quarter"
            )
        }

    def get_spending_by_issue(
        self,
        issue: str,
        year: Optional[int] = None
    ) -> Dict:
        """Get lobbying spending by policy issue."""
        matching_registrants = [
            reg for reg in self.registrants.values()
            if any(iss.lower() == issue.lower() for iss in reg.issues_lobbied)
        ]

        relevant_ids = {reg.registrant_id for reg in matching_registrants}
        matching_expenditures = [
            exp for exp in self.expenditures.values()
            if exp.registrant_id in relevant_ids and (year is None or exp.year == year)
        ]

        return {
            "issue": issue,
            "year": year,
            "total_spending": sum(exp.amount for exp in matching_expenditures),
            "registrant_count": len(matching_registrants),
            "expenditure_count": len(matching_expenditures),
            "top_clients": self._get_top_clients_for_issue(
                matching_expenditures,
                5
            )
        }

    def identify_revolving_door_lobbyists(self) -> List[Dict]:
        """
        Identify lobbyists with government backgrounds (revolving door).

        Returns list of lobbyists with prior government service.
        """
        revolving_door = []

        for lobbyist in self.lobbyists.values():
            if lobbyist.revolving_door_background:
                background = lobbyist.revolving_door_background
                revolving_door.append({
                    "lobbyist_name": lobbyist.full_name,
                    "current_firm": lobbyist.current_firm,
                    "government_position": background.get("position"),
                    "government_agency": background.get("agency"),
                    "government_service_end": background.get("end_date"),
                    "years_since_government": self._calculate_years_since(
                        background.get("end_date")
                    ),
                    "lobbying_clients": lobbyist.principal_clients
                })

        return sorted(
            revolving_door,
            key=lambda x: x.get("years_since_government", float("inf"))
        )

    def _calculate_years_since(self, date_str: Optional[str]) -> Optional[float]:
        """Calculate years elapsed since a date."""
        if not date_str:
            return None

        try:
            past_date = datetime.fromisoformat(date_str)
            delta = datetime.now() - past_date
            return delta.days / 365.25
        except ValueError:
            return None

    def generate_disclosure_filing_report(
        self,
        quarter: str,
        year: int,
        jurisdiction: str = "federal"
    ) -> Dict:
        """
        Generate disclosure filing report for a period.

        Args:
            quarter: Q1, Q2, Q3, Q4
            year: Fiscal year
            jurisdiction: federal, state, local

        Returns:
            Comprehensive filing report
        """
        period_expenditures = [
            exp for exp in self.expenditures.values()
            if exp.quarter == quarter and exp.year == year and exp.jurisdiction == jurisdiction
        ]

        if not period_expenditures:
            return {
                "period": f"{quarter} {year}",
                "jurisdiction": jurisdiction,
                "total_filings": 0,
                "total_spending": Decimal(0)
            }

        return {
            "period": f"{quarter} {year}",
            "jurisdiction": jurisdiction,
            "total_filings": len(set(exp.registrant_id for exp in period_expenditures)),
            "total_spending": sum(exp.amount for exp in period_expenditures),
            "expenditure_count": len(period_expenditures),
            "spending_by_registrant": self._spending_summary(period_expenditures),
            "spending_by_activity_type": self._breakdown_by_field(
                period_expenditures,
                "activity_type"
            ),
            "filing_compliance_rate": self._calculate_compliance_rate(
                period_expenditures,
                jurisdiction
            )
        }

    def _spending_summary(
        self,
        expenditures: List[LobbyingExpenditure]
    ) -> Dict[str, Dict]:
        """Summarize spending by registrant."""
        summary = {}

        for exp in expenditures:
            if exp.registrant_id not in summary:
                summary[exp.registrant_id] = {
                    "total": Decimal(0),
                    "count": 0
                }

            summary[exp.registrant_id]["total"] += exp.amount
            summary[exp.registrant_id]["count"] += 1

        return summary

    def _breakdown_by_field(
        self,
        expenditures: List[LobbyingExpenditure],
        field: str
    ) -> Dict:
        """Break down expenditures by a specific field."""
        breakdown = {}

        for exp in expenditures:
            key = getattr(exp, field, "Unknown")
            if key not in breakdown:
                breakdown[key] = {"total": Decimal(0), "count": 0}

            breakdown[key]["total"] += exp.amount
            breakdown[key]["count"] += 1

        return breakdown

    def _get_top_recipients(
        self,
        expenditures: List[LobbyingExpenditure],
        limit: int
    ) -> List[Dict]:
        """Get top lobbying recipients."""
        recipients = {}

        for exp in expenditures:
            if exp.recipient_name not in recipients:
                recipients[exp.recipient_name] = {
                    "name": exp.recipient_name,
                    "type": exp.recipient_type,
                    "total": Decimal(0)
                }

            recipients[exp.recipient_name]["total"] += exp.amount

        sorted_recipients = sorted(
            recipients.values(),
            key=lambda x: x["total"],
            reverse=True
        )

        return sorted_recipients[:limit]

    def _get_top_clients_for_issue(
        self,
        expenditures: List[LobbyingExpenditure],
        limit: int
    ) -> List[Dict]:
        """Get top clients spending on an issue."""
        clients = {}

        for exp in expenditures:
            if exp.client_name not in clients:
                clients[exp.client_name] = {
                    "name": exp.client_name,
                    "total": Decimal(0)
                }

            clients[exp.client_name]["total"] += exp.amount

        sorted_clients = sorted(
            clients.values(),
            key=lambda x: x["total"],
            reverse=True
        )

        return sorted_clients[:limit]

    def _calculate_compliance_rate(
        self,
        expenditures: List[LobbyingExpenditure],
        jurisdiction: str
    ) -> float:
        """Calculate percentage of expenditures meeting disclosure requirements."""
        if not expenditures:
            return 100.0

        threshold = Decimal("3000") if jurisdiction == "federal" else Decimal("0")
        compliant = sum(
            1 for exp in expenditures
            if exp.amount >= threshold and exp.disclosure_form
        )

        return (compliant / len(expenditures)) * 100

    def get_transparency_score(self, client_id: str) -> float:
        """
        Calculate transparency score for client (0-100).

        Based on completeness of disclosures and filing history.
        """
        if client_id not in self.clients:
            return 0.0

        client = self.clients[client_id]
        score = 50.0

        # Bonus for recent filings
        if client.last_filing_date:
            try:
                last_filing = datetime.fromisoformat(client.last_filing_date)
                days_since = (datetime.now() - last_filing).days

                if days_since < 90:
                    score += 20
                elif days_since < 180:
                    score += 10
            except ValueError:
                pass

        # Bonus for consistent filing history
        if client.annual_filings and len(client.annual_filings) >= 3:
            score += 20

        # Bonus for public issue disclosures
        if client.issues_of_interest and len(client.issues_of_interest) > 0:
            score += 10

        return min(100.0, score)

    def export_spending_analysis(self, format: str = "json") -> str:
        """Export comprehensive spending analysis."""
        analysis = {
            "generated": datetime.now().isoformat(),
            "total_registrants": len(self.registrants),
            "total_expenditures": len(self.expenditures),
            "total_spending": sum(
                exp.amount for exp in self.expenditures.values()
            ),
            "unique_clients": len(set(
                exp.client_name for exp in self.expenditures.values()
            )),
            "top_spending_registrants": self._get_top_spending_registrants(5),
            "top_spending_clients": self._get_top_spending_clients(5)
        }

        if format == "json":
            return json.dumps(analysis, indent=2, default=str)

        return ""

    def _get_top_spending_registrants(self, limit: int) -> List[Dict]:
        """Get registrants with highest total spending."""
        registrant_totals = {}

        for exp in self.expenditures.values():
            if exp.registrant_id not in registrant_totals:
                registrant_totals[exp.registrant_id] = Decimal(0)

            registrant_totals[exp.registrant_id] += exp.amount

        sorted_totals = sorted(
            registrant_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "registrant_id": reg_id,
                "firm_name": self.registrants.get(reg_id, {}).firm_name if reg_id in self.registrants else "Unknown",
                "total_spending": amount
            }
            for reg_id, amount in sorted_totals[:limit]
        ]

    def _get_top_spending_clients(self, limit: int) -> List[Dict]:
        """Get clients with highest total spending."""
        client_totals = {}

        for exp in self.expenditures.values():
            if exp.client_name not in client_totals:
                client_totals[exp.client_name] = Decimal(0)

            client_totals[exp.client_name] += exp.amount

        sorted_totals = sorted(
            client_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "client_name": client_name,
                "total_spending": amount
            }
            for client_name, amount in sorted_totals[:limit]
        ]


if __name__ == "__main__":
    # Example usage
    tracker = LobbyingExpenditureTracker()

    # Register a lobbying firm
    registrant = LobbyingRegistrant(
        registrant_id="FIRM_001",
        firm_name="Policy Solutions LLC",
        principal_client="Tech Inc",
        registration_date="2024-01-15",
        contact_person="Jane Doe",
        email="jane@policysolutions.com",
        phone="202-555-0100",
        address="Washington, DC 20001",
        jurisdiction_level="federal",
        issues_lobbied=["Technology Policy", "Data Privacy"],
        registration_status="active",
        lobbying_experience="15 years",
        estimated_compensation=Decimal("500000")
    )

    tracker.register_registrant(registrant)

    # Record an expenditure
    expenditure = LobbyingExpenditure(
        expenditure_id="EXP_001",
        registrant_id="FIRM_001",
        client_name="Tech Inc",
        activity_type=LobbyingActivityType.DIRECT_LOBBYING.value,
        amount=Decimal("50000"),
        date="2024-01-20",
        quarter="Q1",
        year=2024,
        recipient_name="Rep. John Smith",
        recipient_type="House Member",
        purpose="Discuss data privacy legislation",
        disclosure_form="LDA",
        jurisdiction="federal"
    )

    tracker.record_expenditure(expenditure)

    # Get spending summary
    spending = tracker.get_total_spending_by_registrant("FIRM_001", 2024)
    print(json.dumps(spending, indent=2, default=str))
