"""
Disclosure Report Generator Module

Automated generation of regulatory disclosures and compliance reports including:
- LDA (Lobbying Disclosure Act) filings
- Conflict of interest declarations
- Financial disclosures
- Government ethics reports
- Public transparency reports
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from decimal import Decimal
import hashlib

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of disclosure reports."""
    LOBBYING_DISCLOSURE = "lobbying_disclosure"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    FINANCIAL_DISCLOSURE = "financial_disclosure"
    ETHICS_FILING = "ethics_filing"
    PUBLIC_TRANSPARENCY = "public_transparency"
    GIFT_DISCLOSURE = "gift_disclosure"
    TRAVEL_DISCLOSURE = "travel_disclosure"


class FilingFrequency(Enum):
    """Report filing frequencies."""
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    BIENNIAL = "biennial"
    ON_DEMAND = "on_demand"


@dataclass
class DiscloseableEntity:
    """Entity making disclosure."""
    entity_id: str
    entity_name: str
    entity_type: str  # Individual, Organization, Firm
    registration_number: Optional[str]
    jurisdiction: str
    primary_contact: str
    contact_email: str
    contact_phone: str
    address: str


@dataclass
class FinancialInterest:
    """Financial interest disclosure."""
    interest_id: str
    description: str
    value_range: str  # e.g., "$50,001 - $100,000"
    asset_type: str  # Stock, Real Estate, Business, etc.
    issuer_name: str
    acquisition_date: Optional[str]
    disposition_date: Optional[str]
    relationship: Optional[str]  # Spouse, Dependent, etc.
    disclosure_required: bool


@dataclass
class Activity:
    """Disclosed activity (lobbying, consulting, etc.)."""
    activity_id: str
    activity_type: str
    date: str
    description: str
    value: Optional[Decimal]
    recipient_name: str
    recipient_type: str
    jurisdiction: str
    issues_affected: List[str]


@dataclass
class Disclosure:
    """Comprehensive disclosure record."""
    disclosure_id: str
    disclosing_entity: DiscloseableEntity
    report_type: str
    report_period_start: str
    report_period_end: str
    filing_date: str
    financial_interests: List[FinancialInterest] = field(default_factory=list)
    activities: List[Activity] = field(default_factory=list)
    certifications: Dict = field(default_factory=dict)
    amendments: List[Dict] = field(default_factory=list)
    filing_status: str = "draft"  # draft, submitted, certified, amended
    certification_date: Optional[str] = None
    certifier_name: Optional[str] = None
    certifier_title: Optional[str] = None
    notes: Optional[str] = None


class DisclosureReportGenerator:
    """
    Generates compliance and disclosure reports with automatic:
    - Data validation
    - Template population
    - Signature and certification
    - Filing status tracking
    - Amendment management
    """

    def __init__(self):
        """Initialize report generator."""
        self.disclosures: Dict[str, Disclosure] = {}
        self.filing_requirements: Dict[str, Dict] = self._load_filing_requirements()
        self.report_templates: Dict[str, str] = self._load_report_templates()
        logger.info("Disclosure Report Generator initialized")

    def _load_filing_requirements(self) -> Dict[str, Dict]:
        """Load regulatory filing requirements by jurisdiction and type."""
        return {
            "federal_lobbying": {
                "frequency": FilingFrequency.QUARTERLY.value,
                "threshold": Decimal("3000"),
                "certifications_required": True,
                "amendment_deadline_days": 90
            },
            "federal_conflict": {
                "frequency": FilingFrequency.ANNUAL.value,
                "threshold": Decimal("0"),
                "certifications_required": True,
                "amendment_deadline_days": 30
            },
            "federal_financial": {
                "frequency": FilingFrequency.ANNUAL.value,
                "threshold": Decimal("0"),
                "certifications_required": True,
                "amendment_deadline_days": 30
            },
            "state_lobbying": {
                "frequency": FilingFrequency.QUARTERLY.value,
                "threshold": Decimal("500"),
                "certifications_required": True,
                "amendment_deadline_days": 60
            }
        }

    def _load_report_templates(self) -> Dict[str, str]:
        """Load report generation templates."""
        return {
            "lobbying_disclosure": """
            LOBBYING DISCLOSURE ACT FORM

            Registrant: {registrant_name}
            Period: {report_period_start} to {report_period_end}
            Filed: {filing_date}

            ACTIVITIES REPORTED:
            {activities_summary}

            FINANCIAL INFORMATION:
            Total Expenditures: {total_expenditures}

            CERTIFICATIONS:
            {certifications}
            """,
            "conflict_of_interest": """
            CONFLICT OF INTEREST DISCLOSURE

            Filer: {entity_name}
            Position: {certifier_title}
            Filing Date: {filing_date}

            FINANCIAL INTERESTS:
            {financial_interests_summary}

            POTENTIAL CONFLICTS:
            {conflicts_identified}

            CERTIFICATION:
            {certifications}
            """,
            "financial_disclosure": """
            FINANCIAL DISCLOSURE REPORT

            Filer: {entity_name}
            Report Period: {report_period_start} to {report_period_end}
            Filed: {filing_date}

            ASSETS AND LIABILITIES:
            {assets_summary}

            FINANCIAL INTERESTS:
            {financial_interests_summary}

            VERIFICATION:
            {certifications}
            """
        }

    def create_disclosure(
        self,
        entity: DiscloseableEntity,
        report_type: ReportType,
        period_start: str,
        period_end: str
    ) -> str:
        """Create new disclosure record."""
        disclosure_id = self._generate_disclosure_id(entity, report_type)

        disclosure = Disclosure(
            disclosure_id=disclosure_id,
            disclosing_entity=entity,
            report_type=report_type.value,
            report_period_start=period_start,
            report_period_end=period_end,
            filing_date=datetime.now().isoformat()
        )

        self.disclosures[disclosure_id] = disclosure
        logger.info(f"Disclosure created: {disclosure_id}")

        return disclosure_id

    def _generate_disclosure_id(
        self,
        entity: DiscloseableEntity,
        report_type: ReportType
    ) -> str:
        """Generate unique disclosure identifier."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        entity_hash = hashlib.md5(entity.entity_id.encode()).hexdigest()[:6]
        return f"DISCL_{report_type.value[:4].upper()}_{entity_hash}_{timestamp}"

    def add_financial_interest(
        self,
        disclosure_id: str,
        interest: FinancialInterest
    ) -> bool:
        """Add financial interest to disclosure."""
        if disclosure_id not in self.disclosures:
            logger.error(f"Disclosure {disclosure_id} not found")
            return False

        disclosure = self.disclosures[disclosure_id]
        disclosure.financial_interests.append(interest)

        logger.info(f"Financial interest added to {disclosure_id}")
        return True

    def add_activity(
        self,
        disclosure_id: str,
        activity: Activity
    ) -> bool:
        """Add activity to disclosure."""
        if disclosure_id not in self.disclosures:
            logger.error(f"Disclosure {disclosure_id} not found")
            return False

        disclosure = self.disclosures[disclosure_id]
        disclosure.activities.append(activity)

        logger.info(f"Activity added to {disclosure_id}")
        return True

    def validate_disclosure(self, disclosure_id: str) -> Dict[str, Any]:
        """
        Validate disclosure for completeness and regulatory compliance.

        Returns validation report with errors and warnings.
        """
        if disclosure_id not in self.disclosures:
            return {"valid": False, "errors": ["Disclosure not found"]}

        disclosure = self.disclosures[disclosure_id]
        errors = []
        warnings = []

        # Check required fields
        if not disclosure.disclosing_entity.entity_name:
            errors.append("Entity name is required")

        if not disclosure.financial_interests and disclosure.report_type == ReportType.FINANCIAL_DISCLOSURE.value:
            warnings.append("No financial interests reported")

        if not disclosure.activities and disclosure.report_type == ReportType.LOBBYING_DISCLOSURE.value:
            warnings.append("No activities reported")

        # Check filing requirements
        req_key = self._get_requirement_key(disclosure.report_type)
        if req_key in self.filing_requirements:
            requirement = self.filing_requirements[req_key]

            # Validate threshold
            if disclosure.report_type == ReportType.LOBBYING_DISCLOSURE.value:
                total_value = sum(
                    a.value or Decimal(0) for a in disclosure.activities
                )
                if total_value < requirement["threshold"]:
                    warnings.append(
                        f"Total activity value ${total_value} below "
                        f"filing threshold ${requirement['threshold']}"
                    )

        # Validate certifications
        if requirement.get("certifications_required", False):
            if not disclosure.certifications or not disclosure.certifier_name:
                errors.append("Certification information is required")

        # Check for conflicts of interest
        conflicts = self._identify_potential_conflicts(disclosure)
        if conflicts:
            warnings.extend(conflicts)

        return {
            "valid": len(errors) == 0,
            "disclosure_id": disclosure_id,
            "errors": errors,
            "warnings": warnings,
            "validation_date": datetime.now().isoformat(),
            "review_required": len(errors) > 0 or len(warnings) > 0
        }

    def _get_requirement_key(self, report_type: str) -> str:
        """Get filing requirement key for report type."""
        type_mapping = {
            ReportType.LOBBYING_DISCLOSURE.value: "federal_lobbying",
            ReportType.CONFLICT_OF_INTEREST.value: "federal_conflict",
            ReportType.FINANCIAL_DISCLOSURE.value: "federal_financial"
        }
        return type_mapping.get(report_type, "")

    def _identify_potential_conflicts(self, disclosure: Disclosure) -> List[str]:
        """Identify potential conflicts of interest in disclosure."""
        conflicts = []

        # Check for overlapping activities and financial interests
        for interest in disclosure.financial_interests:
            for activity in disclosure.activities:
                if interest.issuer_name and activity.recipient_name:
                    if interest.issuer_name.lower() in activity.recipient_name.lower():
                        conflicts.append(
                            f"Potential conflict: Activity involving {activity.recipient_name} "
                            f"while holding financial interest in {interest.issuer_name}"
                        )

        return conflicts

    def certify_disclosure(
        self,
        disclosure_id: str,
        certifier_name: str,
        certifier_title: str,
        certification_text: str
    ) -> bool:
        """Certify disclosure as accurate and complete."""
        if disclosure_id not in self.disclosures:
            logger.error(f"Disclosure {disclosure_id} not found")
            return False

        disclosure = self.disclosures[disclosure_id]

        # Validate before certification
        validation = self.validate_disclosure(disclosure_id)
        if not validation["valid"]:
            logger.warning(
                f"Cannot certify {disclosure_id} - validation errors present"
            )
            return False

        disclosure.certifications = {
            "text": certification_text,
            "date": datetime.now().isoformat(),
            "statement": f"I certify that the information contained in this disclosure is "
                         f"true, accurate, and complete to the best of my knowledge."
        }
        disclosure.certification_date = datetime.now().isoformat()
        disclosure.certifier_name = certifier_name
        disclosure.certifier_title = certifier_title
        disclosure.filing_status = "certified"

        logger.info(f"Disclosure {disclosure_id} certified by {certifier_name}")
        return True

    def amend_disclosure(
        self,
        disclosure_id: str,
        amendment_details: Dict
    ) -> str:
        """File amendment to previously submitted disclosure."""
        if disclosure_id not in self.disclosures:
            logger.error(f"Disclosure {disclosure_id} not found")
            return ""

        disclosure = self.disclosures[disclosure_id]

        # Create amendment record
        amendment = {
            "amendment_date": datetime.now().isoformat(),
            "reason": amendment_details.get("reason"),
            "changes": amendment_details.get("changes", []),
            "certifier_name": amendment_details.get("certifier_name"),
            "certifier_title": amendment_details.get("certifier_title")
        }

        disclosure.amendments.append(amendment)
        disclosure.filing_status = "amended"

        logger.info(f"Amendment filed for disclosure {disclosure_id}")
        return disclosure_id

    def generate_report(
        self,
        disclosure_id: str,
        format: str = "text"
    ) -> str:
        """Generate formatted disclosure report."""
        if disclosure_id not in self.disclosures:
            logger.error(f"Disclosure {disclosure_id} not found")
            return ""

        disclosure = self.disclosures[disclosure_id]
        template_key = self._get_template_key(disclosure.report_type)

        if template_key not in self.report_templates:
            logger.error(f"Template not found for {disclosure.report_type}")
            return ""

        template = self.report_templates[template_key]

        # Prepare template variables
        context = {
            "entity_name": disclosure.disclosing_entity.entity_name,
            "registrant_name": disclosure.disclosing_entity.entity_name,
            "report_period_start": disclosure.report_period_start,
            "report_period_end": disclosure.report_period_end,
            "filing_date": disclosure.filing_date,
            "certifier_title": disclosure.certifier_title or "Not Certified",
            "activities_summary": self._format_activities(disclosure.activities),
            "financial_interests_summary": self._format_financial_interests(
                disclosure.financial_interests
            ),
            "total_expenditures": self._calculate_total_expenditures(disclosure.activities),
            "assets_summary": self._format_assets_summary(disclosure.financial_interests),
            "conflicts_identified": self._identify_potential_conflicts(disclosure),
            "certifications": disclosure.certifications.get("text", "Not certified")
        }

        # Format report
        report = template.format(**context)

        if format == "json":
            return json.dumps(asdict(disclosure), indent=2, default=str)

        return report

    def _get_template_key(self, report_type: str) -> str:
        """Get template key for report type."""
        type_mapping = {
            ReportType.LOBBYING_DISCLOSURE.value: "lobbying_disclosure",
            ReportType.CONFLICT_OF_INTEREST.value: "conflict_of_interest",
            ReportType.FINANCIAL_DISCLOSURE.value: "financial_disclosure"
        }
        return type_mapping.get(report_type, "")

    def _format_activities(self, activities: List[Activity]) -> str:
        """Format activities for report display."""
        if not activities:
            return "No activities reported"

        formatted = []
        for activity in activities:
            formatted.append(
                f"  - {activity.description} ({activity.activity_type}): "
                f"${activity.value if activity.value else 'N/A'}"
            )

        return "\n".join(formatted)

    def _format_financial_interests(self, interests: List[FinancialInterest]) -> str:
        """Format financial interests for report display."""
        if not interests:
            return "No financial interests reported"

        formatted = []
        for interest in interests:
            formatted.append(
                f"  - {interest.asset_type}: {interest.issuer_name} "
                f"(Value: {interest.value_range})"
            )

        return "\n".join(formatted)

    def _format_assets_summary(self, interests: List[FinancialInterest]) -> str:
        """Format assets summary for financial disclosure."""
        if not interests:
            return "No assets reported"

        assets_by_type = {}
        for interest in interests:
            asset_type = interest.asset_type
            if asset_type not in assets_by_type:
                assets_by_type[asset_type] = []
            assets_by_type[asset_type].append(interest)

        formatted = []
        for asset_type, items in assets_by_type.items():
            formatted.append(f"\n  {asset_type}s ({len(items)}):")
            for item in items:
                formatted.append(f"    - {item.issuer_name}: {item.value_range}")

        return "".join(formatted)

    def _calculate_total_expenditures(self, activities: List[Activity]) -> Decimal:
        """Calculate total expenditures from activities."""
        return sum(activity.value or Decimal(0) for activity in activities)

    def get_filing_deadline(
        self,
        jurisdiction: str,
        report_type: ReportType
    ) -> Optional[str]:
        """Get filing deadline for a disclosure type."""
        # Simplified deadline calculation
        deadline_map = {
            "federal_lobbying": {"frequency_days": 90},
            "federal_conflict": {"frequency_days": 365},
            "federal_financial": {"frequency_days": 365},
            "state_lobbying": {"frequency_days": 90}
        }

        key = self._get_requirement_key(report_type.value)
        if key not in deadline_map:
            return None

        deadline_days = deadline_map[key]["frequency_days"]
        deadline_date = datetime.now() + timedelta(days=deadline_days)

        return deadline_date.isoformat()

    def export_disclosures(self, format: str = "json") -> str:
        """Export all disclosures."""
        if format == "json":
            disclosures_data = []
            for disclosure in self.disclosures.values():
                disclosures_data.append(asdict(disclosure))

            return json.dumps(disclosures_data, indent=2, default=str)

        return ""


if __name__ == "__main__":
    # Example usage
    generator = DisclosureReportGenerator()

    # Create an entity
    entity = DiscloseableEntity(
        entity_id="ENTITY_001",
        entity_name="Policy Solutions LLC",
        entity_type="Organization",
        registration_number="LDA12345",
        jurisdiction="federal",
        primary_contact="Jane Doe",
        contact_email="jane@policysolutions.com",
        contact_phone="202-555-0100",
        address="Washington, DC 20001"
    )

    # Create disclosure
    disclosure_id = generator.create_disclosure(
        entity,
        ReportType.LOBBYING_DISCLOSURE,
        "2024-01-01",
        "2024-03-31"
    )

    # Add activity
    activity = Activity(
        activity_id="ACT_001",
        activity_type="Direct Lobbying",
        date="2024-02-15",
        description="Lobbying effort regarding data privacy legislation",
        value=Decimal("50000"),
        recipient_name="House Ways and Means Committee",
        recipient_type="Congressional Committee",
        jurisdiction="federal",
        issues_affected=["Data Privacy", "Consumer Protection"]
    )

    generator.add_activity(disclosure_id, activity)

    # Certify disclosure
    generator.certify_disclosure(
        disclosure_id,
        "Jane Doe",
        "CEO",
        "I certify that the information provided is accurate and complete."
    )

    # Generate report
    report = generator.generate_report(disclosure_id)
    print(report)
