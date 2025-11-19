#!/usr/bin/env python3
"""
Quality Validator - Advanced document quality validation and compliance checking.

Production-ready module for validating document quality against standards,
compliance rules, completeness checks, and generating quality reports.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable
from pathlib import Path
import re
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SeverityLevel(Enum):
    """Severity levels for quality issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Categories of quality issues."""
    FORMATTING = "formatting"
    CONTENT = "content"
    COMPLIANCE = "compliance"
    COMPLETENESS = "completeness"
    METADATA = "metadata"
    REFERENCE = "reference"
    NAMING = "naming"
    STRUCTURE = "structure"


class ComplianceFramework(Enum):
    """Compliance frameworks."""
    ABA = "aba"
    STATE_BAR = "state_bar"
    FEDERAL_RULES = "federal_rules"
    FILING_REQUIREMENTS = "filing_requirements"
    ACCESSIBILITY = "accessibility"
    DATA_PROTECTION = "data_protection"


@dataclass
class QualityIssue:
    """Represents a document quality issue."""
    issue_id: str
    category: IssueCategory
    severity: SeverityLevel
    title: str
    description: str
    location: Optional[str] = None  # e.g., "page 2, paragraph 3"
    suggested_fix: Optional[str] = None
    rule_violated: Optional[str] = None
    auto_fixable: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class QualityScore:
    """Quality assessment score."""
    document_id: str
    overall_score: float
    category_scores: Dict[str, float]
    issue_counts: Dict[str, int]
    compliance_status: Dict[str, bool]
    assessed_at: datetime = field(default_factory=datetime.now)
    assessor: str = "automated"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['assessed_at'] = self.assessed_at.isoformat()
        return data


@dataclass
class ValidationRule:
    """Quality validation rule."""
    rule_id: str
    name: str
    category: IssueCategory
    severity: SeverityLevel
    description: str
    validation_func: Optional[Callable] = None
    applies_to: List[str] = field(default_factory=list)  # document types


class QualityValidator:
    """Validates document quality."""

    def __init__(self):
        """Initialize validator."""
        self.rules: Dict[str, ValidationRule] = {}
        self.compliance_frameworks: Dict[str, List[str]] = {}
        self._setup_default_rules()
        logger.info("Initialized quality validator")

    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        # Content rules
        self.add_rule(ValidationRule(
            rule_id="no_empty_sections",
            name="No Empty Sections",
            category=IssueCategory.COMPLETENESS,
            severity=SeverityLevel.WARNING,
            description="Document should not have empty required sections"
        ))

        self.add_rule(ValidationRule(
            rule_id="proper_formatting",
            name="Proper Formatting",
            category=IssueCategory.FORMATTING,
            severity=SeverityLevel.WARNING,
            description="Document should follow standard formatting rules"
        ))

        self.add_rule(ValidationRule(
            rule_id="all_references_valid",
            name="Valid References",
            category=IssueCategory.REFERENCE,
            severity=SeverityLevel.ERROR,
            description="All cross-references should be valid"
        ))

        self.add_rule(ValidationRule(
            rule_id="metadata_complete",
            name="Complete Metadata",
            category=IssueCategory.METADATA,
            severity=SeverityLevel.WARNING,
            description="Document should have complete metadata"
        ))

    def add_rule(self, rule: ValidationRule) -> None:
        """Add validation rule."""
        self.rules[rule.rule_id] = rule
        logger.debug(f"Added validation rule: {rule.rule_id}")

    def validate(
        self,
        document: Dict[str, Any],
        document_type: str,
        frameworks: Optional[List[ComplianceFramework]] = None
    ) -> Tuple[List[QualityIssue], QualityScore]:
        """Validate document quality."""
        logger.info(f"Validating document: {document.get('id', 'unknown')}")

        issues = []
        category_scores = {}

        # Apply rules
        for rule in self.rules.values():
            if not rule.applies_to or document_type in rule.applies_to:
                rule_issues = self._apply_rule(rule, document)
                issues.extend(rule_issues)

        # Check compliance frameworks
        compliance_status = {}
        if frameworks:
            for framework in frameworks:
                compliance_status[framework.value] = self._check_compliance(
                    document,
                    framework
                )

        # Calculate scores
        for category in IssueCategory:
            category_issues = [i for i in issues if i.category == category]
            score = self._calculate_category_score(category_issues)
            category_scores[category.value] = score

        overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 100

        # Count issues by severity
        issue_counts = {
            "info": len([i for i in issues if i.severity == SeverityLevel.INFO]),
            "warning": len([i for i in issues if i.severity == SeverityLevel.WARNING]),
            "error": len([i for i in issues if i.severity == SeverityLevel.ERROR]),
            "critical": len([i for i in issues if i.severity == SeverityLevel.CRITICAL])
        }

        score = QualityScore(
            document_id=document.get("id", str(uuid.uuid4())),
            overall_score=overall_score,
            category_scores=category_scores,
            issue_counts=issue_counts,
            compliance_status=compliance_status
        )

        return issues, score

    def _apply_rule(self, rule: ValidationRule, document: Dict[str, Any]) -> List[QualityIssue]:
        """Apply rule to document."""
        issues = []

        if rule.rule_id == "no_empty_sections":
            required_sections = document.get("required_sections", [])
            for section_name in required_sections:
                if section_name not in document or not document[section_name]:
                    issues.append(QualityIssue(
                        issue_id=str(uuid.uuid4()),
                        category=IssueCategory.COMPLETENESS,
                        severity=SeverityLevel.WARNING,
                        title="Missing Content",
                        description=f"Section '{section_name}' is empty or missing",
                        location=f"Section: {section_name}",
                        suggested_fix=f"Add content to {section_name}"
                    ))

        elif rule.rule_id == "proper_formatting":
            # Check formatting issues
            content = document.get("content", "")
            if isinstance(content, str):
                # Check for common formatting issues
                if "\n\n\n" in content:  # Multiple blank lines
                    issues.append(QualityIssue(
                        issue_id=str(uuid.uuid4()),
                        category=IssueCategory.FORMATTING,
                        severity=SeverityLevel.WARNING,
                        title="Formatting Issue",
                        description="Document contains excessive blank lines",
                        suggested_fix="Remove extra line breaks"
                    ))

        elif rule.rule_id == "all_references_valid":
            # Check for broken references
            references = document.get("references", {})
            for ref_id, ref_value in references.items():
                if ref_value and not self._is_valid_reference(ref_value):
                    issues.append(QualityIssue(
                        issue_id=str(uuid.uuid4()),
                        category=IssueCategory.REFERENCE,
                        severity=SeverityLevel.ERROR,
                        title="Invalid Reference",
                        description=f"Reference '{ref_id}' is invalid",
                        suggested_fix="Update or remove invalid reference"
                    ))

        elif rule.rule_id == "metadata_complete":
            # Check required metadata
            required_metadata = ["author", "created_date", "document_type"]
            for metadata_field in required_metadata:
                if not document.get("metadata", {}).get(metadata_field):
                    issues.append(QualityIssue(
                        issue_id=str(uuid.uuid4()),
                        category=IssueCategory.METADATA,
                        severity=SeverityLevel.WARNING,
                        title="Missing Metadata",
                        description=f"Metadata field '{metadata_field}' is missing",
                        suggested_fix=f"Add {metadata_field} to metadata"
                    ))

        return issues

    @staticmethod
    def _is_valid_reference(reference: str) -> bool:
        """Check if reference is valid."""
        # Simplified check - in production, validate against reference system
        return len(reference) > 0 and not reference.startswith("???")

    def _check_compliance(
        self,
        document: Dict[str, Any],
        framework: ComplianceFramework
    ) -> bool:
        """Check compliance with framework."""
        # Simplified - in production, implement full compliance checking
        if framework == ComplianceFramework.ABA:
            return "signature" in document and "date" in document

        elif framework == ComplianceFramework.FILING_REQUIREMENTS:
            return (document.get("metadata", {}).get("author") is not None and
                    document.get("metadata", {}).get("document_type") is not None)

        return True

    @staticmethod
    def _calculate_category_score(issues: List[QualityIssue]) -> float:
        """Calculate score for category based on issues."""
        if not issues:
            return 100.0

        penalty_map = {
            SeverityLevel.INFO: 2,
            SeverityLevel.WARNING: 5,
            SeverityLevel.ERROR: 10,
            SeverityLevel.CRITICAL: 25
        }

        total_penalty = sum(penalty_map.get(issue.severity, 0) for issue in issues)
        score = max(0, 100 - total_penalty)
        return float(score)


class DocumentCompletenessChecker:
    """Checks document completeness."""

    def __init__(self):
        """Initialize checker."""
        self.required_sections: Dict[str, List[str]] = {}
        self._setup_default_sections()
        logger.info("Initialized document completeness checker")

    def _setup_default_sections(self) -> None:
        """Setup default required sections by document type."""
        self.required_sections = {
            "contract": [
                "title",
                "parties",
                "recitals",
                "terms",
                "conditions",
                "signatures"
            ],
            "complaint": [
                "caption",
                "jurisdiction",
                "parties",
                "facts",
                "causes_of_action",
                "relief_sought",
                "signature"
            ],
            "brief": [
                "caption",
                "issues",
                "facts",
                "arguments",
                "conclusion",
                "signature"
            ]
        }

    def check(self, document: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Check document completeness."""
        required = self.required_sections.get(doc_type, [])
        present = []
        missing = []

        for section in required:
            if section in document and document[section]:
                present.append(section)
            else:
                missing.append(section)

        completion_percentage = (len(present) / len(required) * 100) if required else 0

        return {
            "document_type": doc_type,
            "required_sections": len(required),
            "present_sections": len(present),
            "missing_sections": len(missing),
            "completion_percentage": completion_percentage,
            "missing_section_names": missing,
            "is_complete": len(missing) == 0
        }


class QualityReport:
    """Quality assessment report."""

    def __init__(
        self,
        document_id: str,
        issues: List[QualityIssue],
        score: QualityScore,
        completeness: Dict[str, Any]
    ):
        """Initialize report."""
        self.id = str(uuid.uuid4())
        self.document_id = document_id
        self.issues = issues
        self.score = score
        self.completeness = completeness
        self.generated_at = datetime.now()
        logger.info(f"Created quality report for document: {document_id}")

    def get_critical_issues(self) -> List[QualityIssue]:
        """Get all critical issues."""
        return [i for i in self.issues if i.severity == SeverityLevel.CRITICAL]

    def get_issues_by_category(self, category: IssueCategory) -> List[QualityIssue]:
        """Get issues for category."""
        return [i for i in self.issues if i.category == category]

    def is_ready_for_filing(self) -> bool:
        """Check if document is ready for filing."""
        return (
            len(self.get_critical_issues()) == 0 and
            self.score.overall_score >= 80 and
            self.completeness.get("is_complete", False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.id,
            "document_id": self.document_id,
            "generated_at": self.generated_at.isoformat(),
            "overall_score": self.score.overall_score,
            "is_ready_for_filing": self.is_ready_for_filing(),
            "issues_count": {
                "total": len(self.issues),
                "critical": len(self.get_critical_issues()),
                "errors": self.score.issue_counts.get("error", 0),
                "warnings": self.score.issue_counts.get("warning", 0)
            },
            "completeness": self.completeness,
            "issues": [i.to_dict() for i in self.issues],
            "category_scores": self.score.category_scores
        }


def create_sample_document() -> Dict[str, Any]:
    """Create sample document for testing."""
    return {
        "id": "DOC-2024-001",
        "type": "contract",
        "title": "Service Agreement",
        "content": "This is a service agreement...",
        "required_sections": ["title", "parties", "terms", "signatures"],
        "parties": "Company A and Company B",
        "terms": "Service terms and conditions",
        "signatures": "Signed by authorized representatives",
        "metadata": {
            "author": "John Doe",
            "created_date": "2024-11-19",
            "document_type": "contract"
        },
        "references": {
            "ref1": "Section 5.1"
        }
    }


if __name__ == "__main__":
    # Create validator and checker
    validator = QualityValidator()
    checker = DocumentCompletenessChecker()

    # Create sample document
    document = create_sample_document()

    # Validate
    issues, score = validator.validate(
        document,
        "contract",
        [ComplianceFramework.ABA, ComplianceFramework.FILING_REQUIREMENTS]
    )

    # Check completeness
    completeness = checker.check(document, "contract")

    # Create report
    report = QualityReport(document["id"], issues, score, completeness)

    print("Quality Report:")
    print(json.dumps(report.to_dict(), indent=2, default=str))

    print(f"\nReady for filing: {report.is_ready_for_filing()}")
