"""
Comment Letter Automation Module

Automated generation and management of regulatory comment letters including:
- Docket discovery and deadline tracking
- Comment template generation
- Multi-stakeholder comment coordination
- Comments.gov integration
- Comment tracking and response monitoring
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class CommentStatus(Enum):
    """Status of regulatory comment."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    SUBMITTED = "submitted"
    POSTED = "posted"
    ACKNOWLEDGED = "acknowledged"
    INCORPORATED = "incorporated"


class DocketType(Enum):
    """Types of regulatory dockets."""
    RULEMAKING = "rulemaking"
    PETITION = "petition"
    ADVISORY = "advisory"
    ENVIRONMENTAL = "environmental"
    SAFETY = "safety"


@dataclass
class RegulatoryDocket:
    """Regulatory docket information."""
    docket_id: str
    agency: str
    title: str
    description: str
    docket_type: str
    document_url: str
    comment_start_date: str
    comment_deadline: str
    proposed_rule_summary: str
    estimated_impact: Optional[Dict]
    keywords: List[str]
    related_dockets: List[str] = field(default_factory=list)
    agency_contact: Optional[str] = None
    submission_instructions: str = ""


@dataclass
class CommentSection:
    """Section of a comment letter."""
    section_id: str
    section_title: str
    content: str
    supporting_evidence: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    data_references: List[Dict] = field(default_factory=list)


@dataclass
class CommentLetter:
    """Complete regulatory comment letter."""
    comment_id: str
    docket_id: str
    submitting_organization: str
    primary_contact: str
    contact_email: str
    contact_phone: str
    comment_status: str
    submission_date: Optional[str]
    sections: List[CommentSection] = field(default_factory=list)
    executive_summary: str = ""
    key_recommendations: List[str] = field(default_factory=list)
    compliance_references: List[str] = field(default_factory=list)
    attachments: List[Dict] = field(default_factory=list)
    signatory_name: Optional[str] = None
    signatory_title: Optional[str] = None
    document_hash: Optional[str] = None
    submission_method: str = "regulations.gov"
    tracking_number: Optional[str] = None
    agency_response: Optional[Dict] = None


@dataclass
class CommentCoordination:
    """Coordination of joint/coalition comments."""
    coordination_id: str
    docket_id: str
    lead_organization: str
    coalition_name: Optional[str]
    participating_organizations: List[str]
    coordination_date: str
    joint_comment_id: Optional[str]
    individual_comment_ids: List[str] = field(default_factory=list)
    coordination_status: str = "forming"


class CommentLetterGenerator:
    """
    Automates comment letter generation and submission.

    Features:
    - Docket discovery and deadline tracking
    - Template-based comment generation
    - Multi-stakeholder coordination
    - Submission tracking
    - Response monitoring and incorporation tracking
    """

    def __init__(self):
        """Initialize comment letter generator."""
        self.dockets: Dict[str, RegulatoryDocket] = {}
        self.comments: Dict[str, CommentLetter] = {}
        self.coordinations: Dict[str, CommentCoordination] = {}
        self.comment_templates: Dict[str, str] = self._load_templates()
        self.submission_log: List[Dict] = []
        logger.info("Comment Letter Generator initialized")

    def _load_templates(self) -> Dict[str, str]:
        """Load comment letter templates."""
        return {
            "standard_comment": """
COMMENT ON {docket_id}
Submitted by: {submitting_organization}
Date: {submission_date}

EXECUTIVE SUMMARY
{executive_summary}

I. INTRODUCTION
[Organization name] respectfully submits this comment on the proposed rule.
This comment addresses key concerns and recommends improvements to the regulatory approach.

II. BACKGROUND
[Details on regulatory context and impacts]

III. SUBSTANTIVE COMMENTS
{sections}

IV. RECOMMENDATIONS
{recommendations}

V. CONCLUSION
[Organization name] appreciates the opportunity to comment and requests consideration
of the recommendations presented herein.

Respectfully submitted,
{signatory_name}
{signatory_title}
{submitting_organization}
            """,
            "scientific_comment": """
SCIENTIFIC AND TECHNICAL COMMENT ON {docket_id}
Submitted by: {submitting_organization}
Date: {submission_date}

EXECUTIVE SUMMARY
{executive_summary}

I. TECHNICAL BACKGROUND
[Technical analysis and context]

II. DATA AND EVIDENCE ANALYSIS
[Detailed analysis of evidence]

III. METHODOLOGICAL CONCERNS
{sections}

IV. RECOMMENDATIONS BASED ON EVIDENCE
{recommendations}

Respectfully submitted,
{signatory_name}, Ph.D.
{submitting_organization}
            """
        }

    def register_docket(self, docket: RegulatoryDocket) -> str:
        """Register regulatory docket for tracking."""
        if docket.docket_id in self.dockets:
            logger.warning(f"Docket {docket.docket_id} already registered")
            return docket.docket_id

        self.dockets[docket.docket_id] = docket
        logger.info(f"Docket registered: {docket.docket_id}")

        return docket.docket_id

    def create_comment_letter(
        self,
        docket_id: str,
        organization: str,
        primary_contact: str,
        contact_email: str,
        contact_phone: str,
        template_type: str = "standard_comment"
    ) -> str:
        """Create new comment letter."""
        if docket_id not in self.dockets:
            logger.error(f"Docket {docket_id} not found")
            return ""

        comment_id = self._generate_comment_id(docket_id, organization)

        comment = CommentLetter(
            comment_id=comment_id,
            docket_id=docket_id,
            submitting_organization=organization,
            primary_contact=primary_contact,
            contact_email=contact_email,
            contact_phone=contact_phone,
            comment_status=CommentStatus.DRAFT.value
        )

        self.comments[comment_id] = comment
        logger.info(f"Comment letter created: {comment_id}")

        return comment_id

    def _generate_comment_id(self, docket_id: str, organization: str) -> str:
        """Generate unique comment identifier."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        org_hash = hashlib.md5(organization.encode()).hexdigest()[:6]
        return f"COMMENT_{docket_id}_{org_hash}_{timestamp}"

    def add_comment_section(
        self,
        comment_id: str,
        section: CommentSection
    ) -> bool:
        """Add section to comment letter."""
        if comment_id not in self.comments:
            logger.error(f"Comment {comment_id} not found")
            return False

        comment = self.comments[comment_id]
        comment.sections.append(section)
        logger.info(f"Section added to comment {comment_id}")

        return True

    def set_executive_summary(
        self,
        comment_id: str,
        summary: str
    ) -> bool:
        """Set executive summary for comment."""
        if comment_id not in self.comments:
            logger.error(f"Comment {comment_id} not found")
            return False

        self.comments[comment_id].executive_summary = summary
        return True

    def add_recommendations(
        self,
        comment_id: str,
        recommendations: List[str]
    ) -> bool:
        """Add recommendations to comment."""
        if comment_id not in self.comments:
            logger.error(f"Comment {comment_id} not found")
            return False

        self.comments[comment_id].key_recommendations.extend(recommendations)
        return True

    def validate_comment(self, comment_id: str) -> Dict:
        """Validate comment for submission readiness."""
        if comment_id not in self.comments:
            return {"valid": False, "errors": ["Comment not found"]}

        comment = self.comments[comment_id]
        errors = []
        warnings = []

        # Check required fields
        if not comment.submitting_organization:
            errors.append("Organization name is required")

        if not comment.primary_contact:
            errors.append("Primary contact is required")

        if not comment.contact_email:
            errors.append("Contact email is required")

        if not comment.sections:
            warnings.append("No substantive sections added")

        if not comment.executive_summary:
            warnings.append("Executive summary not provided")

        # Check deadline
        if comment_id in self.comments:
            docket = self.dockets.get(comment.docket_id)
            if docket:
                deadline = datetime.fromisoformat(docket.comment_deadline)
                if datetime.now() > deadline:
                    errors.append(f"Comment deadline has passed ({docket.comment_deadline})")

        # Check length
        total_content = sum(len(s.content) for s in comment.sections)
        if total_content > 50000:  # 50KB limit
            warnings.append("Comment may exceed typical length limits")

        return {
            "valid": len(errors) == 0,
            "comment_id": comment_id,
            "errors": errors,
            "warnings": warnings,
            "ready_for_submission": len(errors) == 0
        }

    def generate_comment_text(
        self,
        comment_id: str,
        template_type: str = "standard_comment"
    ) -> str:
        """Generate formatted comment text."""
        if comment_id not in self.comments:
            logger.error(f"Comment {comment_id} not found")
            return ""

        comment = self.comments[comment_id]
        docket = self.dockets.get(comment.docket_id)

        if not docket or template_type not in self.comment_templates:
            return ""

        template = self.comment_templates[template_type]

        # Format sections
        sections_text = ""
        for i, section in enumerate(comment.sections, 1):
            sections_text += f"\n{i}. {section.section_title}\n{section.content}\n"

        # Format recommendations
        recommendations_text = ""
        for i, rec in enumerate(comment.key_recommendations, 1):
            recommendations_text += f"{i}. {rec}\n"

        # Populate template
        formatted = template.format(
            docket_id=docket.docket_id,
            submitting_organization=comment.submitting_organization,
            submission_date=datetime.now().strftime("%B %d, %Y"),
            executive_summary=comment.executive_summary,
            sections=sections_text,
            recommendations=recommendations_text,
            signatory_name=comment.signatory_name or "Authorized Representative",
            signatory_title=comment.signatory_title or "Submitted on behalf of"
        )

        return formatted

    def submit_comment(
        self,
        comment_id: str,
        submission_method: str = "regulations.gov"
    ) -> Tuple[bool, str]:
        """
        Submit comment for filing.

        Returns (success, tracking_number)
        """
        if comment_id not in self.comments:
            return False, ""

        # Validate before submission
        validation = self.validate_comment(comment_id)
        if not validation["valid"]:
            logger.error(f"Cannot submit comment {comment_id} - validation errors")
            return False, ""

        comment = self.comments[comment_id]

        # Generate tracking number
        tracking_number = self._generate_tracking_number(comment_id)

        # Record submission
        comment.submission_date = datetime.now().isoformat()
        comment.comment_status = CommentStatus.SUBMITTED.value
        comment.tracking_number = tracking_number
        comment.submission_method = submission_method

        self.submission_log.append({
            "comment_id": comment_id,
            "tracking_number": tracking_number,
            "submission_date": comment.submission_date,
            "method": submission_method
        })

        logger.info(f"Comment {comment_id} submitted with tracking #{tracking_number}")
        return True, tracking_number

    def _generate_tracking_number(self, comment_id: str) -> str:
        """Generate submission tracking number."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TRK-{comment_id[:10]}-{timestamp}"

    def coordinate_joint_comment(
        self,
        docket_id: str,
        lead_organization: str,
        coalition_name: Optional[str],
        participating_organizations: List[str]
    ) -> str:
        """Initiate coordination for joint/coalition comment."""
        coordination_id = f"COORD_{docket_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        coordination = CommentCoordination(
            coordination_id=coordination_id,
            docket_id=docket_id,
            lead_organization=lead_organization,
            coalition_name=coalition_name,
            participating_organizations=participating_organizations,
            coordination_date=datetime.now().isoformat()
        )

        self.coordinations[coordination_id] = coordination
        logger.info(f"Comment coordination initiated: {coordination_id}")

        return coordination_id

    def link_coordination_comment(
        self,
        coordination_id: str,
        comment_id: str,
        is_joint: bool = False
    ) -> bool:
        """Link comment to coordination effort."""
        if coordination_id not in self.coordinations:
            logger.error(f"Coordination {coordination_id} not found")
            return False

        coordination = self.coordinations[coordination_id]

        if is_joint:
            coordination.joint_comment_id = comment_id
        else:
            coordination.individual_comment_ids.append(comment_id)

        return True

    def get_upcoming_deadlines(
        self,
        days_ahead: int = 30
    ) -> List[Dict]:
        """Get dockets with upcoming comment deadlines."""
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        upcoming = []

        for docket in self.dockets.values():
            deadline = datetime.fromisoformat(docket.comment_deadline)
            if datetime.now() < deadline < datetime.fromisoformat(cutoff_date):
                days_until = (deadline - datetime.now()).days

                upcoming.append({
                    "docket_id": docket.docket_id,
                    "agency": docket.agency,
                    "title": docket.title,
                    "deadline": docket.comment_deadline,
                    "days_until_deadline": days_until,
                    "comments_filed": len([
                        c for c in self.comments.values()
                        if c.docket_id == docket.docket_id
                        and c.comment_status in [CommentStatus.SUBMITTED.value, CommentStatus.POSTED.value]
                    ])
                })

        return sorted(upcoming, key=lambda x: x["days_until_deadline"])

    def track_comment_status(self, comment_id: str) -> Dict:
        """Track status of submitted comment."""
        if comment_id not in self.comments:
            return {}

        comment = self.comments[comment_id]
        docket = self.dockets.get(comment.docket_id)

        return {
            "comment_id": comment_id,
            "docket_id": comment.docket_id,
            "organization": comment.submitting_organization,
            "status": comment.comment_status,
            "submission_date": comment.submission_date,
            "tracking_number": comment.tracking_number,
            "agency_response": comment.agency_response,
            "docket_title": docket.title if docket else "Unknown",
            "status_history": self._get_status_history(comment_id)
        }

    def _get_status_history(self, comment_id: str) -> List[Dict]:
        """Get status change history for comment."""
        # In production, would query database for status changes
        return [
            {
                "status": CommentStatus.DRAFT.value,
                "date": self.comments[comment_id].submission_date or ""
            }
        ]

    def export_comments(self, format: str = "json") -> str:
        """Export all comments."""
        if format == "json":
            comments_data = []
            for comment in self.comments.values():
                comments_data.append({
                    "comment_id": comment.comment_id,
                    "docket_id": comment.docket_id,
                    "organization": comment.submitting_organization,
                    "status": comment.comment_status,
                    "submission_date": comment.submission_date,
                    "tracking_number": comment.tracking_number
                })

            return json.dumps(comments_data, indent=2)

        return ""

    def get_filing_statistics(self) -> Dict:
        """Generate comment filing statistics."""
        statuses = {}
        for comment in self.comments.values():
            status = comment.comment_status
            statuses[status] = statuses.get(status, 0) + 1

        submitted = [
            c for c in self.comments.values()
            if c.comment_status in [CommentStatus.SUBMITTED.value, CommentStatus.POSTED.value]
        ]

        return {
            "total_comments": len(self.comments),
            "comments_by_status": statuses,
            "comments_submitted": len(submitted),
            "dockets_tracked": len(self.dockets),
            "coordinations_active": sum(
                1 for c in self.coordinations.values()
                if c.coordination_status == "forming"
            ),
            "upcoming_deadlines_30_days": len(self.get_upcoming_deadlines(30))
        }


if __name__ == "__main__":
    # Example usage
    generator = CommentLetterGenerator()

    # Register docket
    docket = RegulatoryDocket(
        docket_id="EPA-2024-0001",
        agency="EPA",
        title="Air Quality Standards Rule",
        description="Proposed updates to National Ambient Air Quality Standards",
        docket_type=DocketType.RULEMAKING.value,
        document_url="https://regulations.gov/docket/EPA-2024-0001",
        comment_start_date="2024-02-01",
        comment_deadline="2024-04-01",
        proposed_rule_summary="Updates to NAAQS for ozone and particulate matter",
        estimated_impact={"regulated_entities": 5000, "annual_cost": 500000000},
        keywords=["Air Quality", "Environmental", "Standards"]
    )

    generator.register_docket(docket)

    # Create comment
    comment_id = generator.create_comment_letter(
        "EPA-2024-0001",
        "Environmental Group Inc",
        "Jane Smith",
        "jane@envgroup.org",
        "202-555-0100"
    )

    # Add sections
    section = CommentSection(
        section_id="SEC_1",
        section_title="Existing Data Supports Stricter Standards",
        content="Recent studies demonstrate health impacts from current pollution levels...",
        supporting_evidence=["Study 1", "Study 2"],
        citations=["EPA Health Report 2023"]
    )

    generator.add_comment_section(comment_id, section)

    # Add recommendations
    generator.add_recommendations(comment_id, [
        "Strengthen ozone standards to 70 ppb",
        "Implement accelerated compliance timeline"
    ])

    # Validate
    validation = generator.validate_comment(comment_id)
    print(json.dumps(validation, indent=2))
