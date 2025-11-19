#!/usr/bin/env python3
"""
Court Form Automation - Automated generation and validation of court forms.

Production-ready module for managing court form templates, validation rules,
and submission workflows for various court systems and jurisdictions.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Pattern
from pathlib import Path
import re
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CourtJurisdiction(Enum):
    """Court jurisdictions."""
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    MUNICIPAL = "municipal"
    APPELLATE = "appellate"
    SUPREME = "supreme"


class CourtType(Enum):
    """Types of courts."""
    DISTRICT = "district"
    CIRCUIT = "circuit"
    SUPERIOR = "superior"
    SUPREME = "supreme"
    BANKRUPTCY = "bankruptcy"
    TAX = "tax"
    FAMILY = "family"
    SMALL_CLAIMS = "small_claims"


class FormType(Enum):
    """Types of court forms."""
    COMPLAINT = "complaint"
    ANSWER = "answer"
    MOTION = "motion"
    PETITION = "petition"
    BRIEF = "brief"
    JUDGMENT = "judgment"
    NOTICE = "notice"
    SUMMONS = "summons"
    SUBPOENA = "subpoena"
    AFFIDAVIT = "affidavit"


class ValidationRule(Enum):
    """Validation rule types."""
    REQUIRED = "required"
    PATTERN = "pattern"
    LENGTH = "length"
    NUMERIC = "numeric"
    DATE = "date"
    JURISDICTION_SPECIFIC = "jurisdiction_specific"


@dataclass
class CourtFormField:
    """Field in a court form."""
    field_id: str
    name: str
    label: str
    field_type: str
    required: bool = True
    validation_rules: List[Tuple[ValidationRule, Any]] = field(default_factory=list)
    help_text: Optional[str] = None
    instructions: Optional[str] = None
    example: Optional[str] = None
    page_number: int = 1
    line_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['validation_rules'] = [(rule.value, value) for rule, value in self.validation_rules]
        return data


@dataclass
class CourtFormTemplate:
    """Template for a court form."""
    form_id: str
    name: str
    form_type: FormType
    jurisdiction: CourtJurisdiction
    court_type: CourtType
    form_number: str
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fields: List[CourtFormField] = field(default_factory=list)
    instructions: str = ""
    page_count: int = 1
    is_active: bool = True

    def add_field(self, field: CourtFormField) -> None:
        """Add field to form."""
        self.fields.append(field)
        logger.debug(f"Added field to form: {field.field_id}")

    def get_fields_for_page(self, page_number: int) -> List[CourtFormField]:
        """Get fields for a specific page."""
        return [f for f in self.fields if f.page_number == page_number]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['form_type'] = self.form_type.value
        data['jurisdiction'] = self.jurisdiction.value
        data['court_type'] = self.court_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['fields'] = [f.to_dict() for f in self.fields]
        return data


@dataclass
class CourtFormValidationError:
    """Validation error in court form."""
    field_id: str
    field_name: str
    error_message: str
    rule_violated: ValidationRule
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['rule_violated'] = self.rule_violated.value
        return data


class CourtFormValidator:
    """Validates court forms against rules and requirements."""

    def __init__(self):
        """Initialize validator."""
        self.jurisdiction_rules: Dict[str, Dict[str, Any]] = {}
        self._setup_jurisdiction_rules()
        logger.info("Initialized court form validator")

    def _setup_jurisdiction_rules(self) -> None:
        """Setup jurisdiction-specific validation rules."""
        self.jurisdiction_rules = {
            "federal": {
                "min_page_count": 1,
                "required_signature_count": 1,
                "filing_fee_required": True
            },
            "state": {
                "min_page_count": 1,
                "required_signature_count": 1,
                "filing_fee_required": True
            },
            "county": {
                "min_page_count": 1,
                "required_signature_count": 1,
                "filing_fee_required": True
            }
        }

    def validate(
        self,
        form_template: CourtFormTemplate,
        form_data: Dict[str, Any]
    ) -> Tuple[bool, List[CourtFormValidationError]]:
        """Validate form against template."""
        logger.info(f"Validating form: {form_template.name}")
        errors = []

        for field in form_template.fields:
            value = form_data.get(field.field_id)

            # Check required
            if field.required and (value is None or value == ""):
                errors.append(CourtFormValidationError(
                    field_id=field.field_id,
                    field_name=field.name,
                    error_message=f"Field '{field.label}' is required",
                    rule_violated=ValidationRule.REQUIRED,
                    suggested_fix=f"Enter a value for {field.label}"
                ))
                continue

            if value is None or value == "":
                continue

            # Validate against rules
            for rule_type, rule_value in field.validation_rules:
                field_errors = self._validate_field_rule(
                    field,
                    value,
                    rule_type,
                    rule_value
                )
                errors.extend(field_errors)

        return len(errors) == 0, errors

    def _validate_field_rule(
        self,
        field: CourtFormField,
        value: Any,
        rule_type: ValidationRule,
        rule_value: Any
    ) -> List[CourtFormValidationError]:
        """Validate single field rule."""
        errors = []

        if rule_type == ValidationRule.PATTERN:
            pattern: Pattern = rule_value
            if not pattern.match(str(value)):
                errors.append(CourtFormValidationError(
                    field_id=field.field_id,
                    field_name=field.name,
                    error_message=f"Invalid format for {field.label}",
                    rule_violated=ValidationRule.PATTERN,
                    suggested_fix=f"Use format: {field.example}"
                ))

        elif rule_type == ValidationRule.LENGTH:
            min_len, max_len = rule_value
            value_len = len(str(value))
            if value_len < min_len or value_len > max_len:
                errors.append(CourtFormValidationError(
                    field_id=field.field_id,
                    field_name=field.name,
                    error_message=f"Length must be between {min_len} and {max_len}",
                    rule_violated=ValidationRule.LENGTH
                ))

        elif rule_type == ValidationRule.NUMERIC:
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(CourtFormValidationError(
                    field_id=field.field_id,
                    field_name=field.name,
                    error_message=f"Field must be numeric",
                    rule_violated=ValidationRule.NUMERIC
                ))

        elif rule_type == ValidationRule.DATE:
            if not self._is_valid_date(str(value)):
                errors.append(CourtFormValidationError(
                    field_id=field.field_id,
                    field_name=field.name,
                    error_message="Invalid date format",
                    rule_violated=ValidationRule.DATE,
                    suggested_fix="Use format: YYYY-MM-DD"
                ))

        return errors

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Check if valid date."""
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class CourtFormFiller:
    """Fills court forms with data."""

    def __init__(self, template: CourtFormTemplate, validator: CourtFormValidator):
        """Initialize filler."""
        self.template = template
        self.validator = validator
        self.filled_data: Dict[str, Any] = {}
        self.errors: List[CourtFormValidationError] = []
        logger.info(f"Initialized court form filler for: {template.name}")

    def fill(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Fill form with data."""
        logger.info(f"Filling form: {self.template.name}")

        # Validate
        is_valid, errors = self.validator.validate(self.template, data)
        self.errors = errors

        if not is_valid:
            logger.warning(f"Form validation failed: {len(errors)} errors")
            return False, {}

        # Fill
        for field in self.template.fields:
            if field.field_id in data:
                self.filled_data[field.field_id] = data[field.field_id]

        logger.info(f"Form filled successfully")
        return True, self.filled_data

    def get_field_value(self, field_id: str) -> Optional[Any]:
        """Get filled field value."""
        return self.filled_data.get(field_id)

    def export_to_dict(self) -> Dict[str, Any]:
        """Export form to dictionary."""
        return {
            "form_id": self.template.form_id,
            "form_name": self.template.name,
            "form_type": self.template.form_type.value,
            "jurisdiction": self.template.jurisdiction.value,
            "filled_at": datetime.now().isoformat(),
            "data": self.filled_data,
            "validation_errors": [e.to_dict() for e in self.errors]
        }


class CourtFormLibrary:
    """Library of court form templates."""

    def __init__(self):
        """Initialize library."""
        self.templates: Dict[str, CourtFormTemplate] = {}
        self.created_at = datetime.now()
        logger.info("Initialized court form library")

    def add_template(self, template: CourtFormTemplate) -> None:
        """Add template to library."""
        self.templates[template.form_id] = template
        logger.debug(f"Added template: {template.form_id}")

    def get_template(self, form_id: str) -> Optional[CourtFormTemplate]:
        """Get template by ID."""
        return self.templates.get(form_id)

    def find_templates(
        self,
        form_type: Optional[FormType] = None,
        jurisdiction: Optional[CourtJurisdiction] = None,
        court_type: Optional[CourtType] = None
    ) -> List[CourtFormTemplate]:
        """Find templates by criteria."""
        results = list(self.templates.values())

        if form_type:
            results = [t for t in results if t.form_type == form_type]

        if jurisdiction:
            results = [t for t in results if t.jurisdiction == jurisdiction]

        if court_type:
            results = [t for t in results if t.court_type == court_type]

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        return {
            "total_templates": len(self.templates),
            "created_at": self.created_at.isoformat(),
            "templates_by_type": self._count_by_type(),
            "templates_by_jurisdiction": self._count_by_jurisdiction()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count templates by type."""
        counts = {}
        for template in self.templates.values():
            key = template.form_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_by_jurisdiction(self) -> Dict[str, int]:
        """Count templates by jurisdiction."""
        counts = {}
        for template in self.templates.values():
            key = template.jurisdiction.value
            counts[key] = counts.get(key, 0) + 1
        return counts


def create_sample_form() -> CourtFormTemplate:
    """Create sample court form template."""
    form = CourtFormTemplate(
        form_id=str(uuid.uuid4()),
        name="Civil Complaint",
        form_type=FormType.COMPLAINT,
        jurisdiction=CourtJurisdiction.FEDERAL,
        court_type=CourtType.DISTRICT,
        form_number="AO 440"
    )

    # Add fields
    fields = [
        CourtFormField(
            field_id="plaintiff_name",
            name="plaintiff_name",
            label="Plaintiff Name",
            field_type="text",
            required=True,
            validation_rules=[
                (ValidationRule.REQUIRED, True),
                (ValidationRule.LENGTH, (1, 100))
            ]
        ),
        CourtFormField(
            field_id="defendant_name",
            name="defendant_name",
            label="Defendant Name",
            field_type="text",
            required=True,
            validation_rules=[
                (ValidationRule.REQUIRED, True),
                (ValidationRule.LENGTH, (1, 100))
            ]
        ),
        CourtFormField(
            field_id="filing_date",
            name="filing_date",
            label="Filing Date",
            field_type="date",
            required=True,
            validation_rules=[
                (ValidationRule.REQUIRED, True),
                (ValidationRule.DATE, None)
            ]
        ),
        CourtFormField(
            field_id="case_amount",
            name="case_amount",
            label="Amount in Controversy",
            field_type="currency",
            required=False,
            validation_rules=[
                (ValidationRule.NUMERIC, True)
            ]
        )
    ]

    for field in fields:
        form.add_field(field)

    return form


if __name__ == "__main__":
    # Create form
    form = create_sample_form()

    # Create validator and filler
    validator = CourtFormValidator()
    filler = CourtFormFiller(form, validator)

    # Fill form
    test_data = {
        "plaintiff_name": "John Doe",
        "defendant_name": "Jane Smith",
        "filing_date": "2024-11-19",
        "case_amount": "500000"
    }

    success, filled = filler.fill(test_data)
    print(f"Fill successful: {success}")
    print("\nFilled form:")
    print(json.dumps(filler.export_to_dict(), indent=2, default=str))

    # Create library
    library = CourtFormLibrary()
    library.add_template(form)

    print("\nLibrary statistics:")
    print(json.dumps(library.get_statistics(), indent=2))
