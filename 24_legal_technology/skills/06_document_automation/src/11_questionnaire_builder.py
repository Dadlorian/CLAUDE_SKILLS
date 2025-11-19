#!/usr/bin/env python3
"""
Questionnaire Builder - Dynamic legal document questionnaire generation.

Production-ready module for creating adaptive questionnaires based on
user responses, case type, and jurisdiction requirements.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """Enumeration of question types."""
    TEXT = "text"
    MULTILINE = "multiline"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    DATE = "date"
    CURRENCY = "currency"
    CONDITIONAL = "conditional"


class QuestionnaireStatus(Enum):
    """Enumeration of questionnaire statuses."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class QuestionOption:
    """Represents a single answer option."""
    id: str
    label: str
    value: Any
    triggers_followup: Optional[List[str]] = None
    requires_explanation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Question:
    """Represents a single questionnaire question."""
    id: str
    text: str
    question_type: QuestionType
    required: bool = True
    options: List[QuestionOption] = field(default_factory=list)
    conditional_parent: Optional[str] = None
    conditional_value: Optional[Any] = None
    help_text: Optional[str] = None
    validation_regex: Optional[str] = None
    max_length: Optional[int] = None
    depends_on: List[str] = field(default_factory=list)
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['question_type'] = self.question_type.value
        data['options'] = [opt.to_dict() for opt in self.options]
        return data


@dataclass
class QuestionnaireSection:
    """Represents a section of related questions."""
    id: str
    title: str
    description: str
    questions: List[Question] = field(default_factory=list)
    order: int = 0
    completion_percentage: float = 0.0

    def get_total_questions(self) -> int:
        """Get total number of questions."""
        return len(self.questions)

    def get_answered_questions(self, responses: Dict[str, Any]) -> int:
        """Get count of answered questions."""
        return sum(1 for q in self.questions if q.id in responses)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['questions'] = [q.to_dict() for q in self.questions]
        return data


class QuestionnaireTemplate:
    """Dynamic legal questionnaire template."""

    def __init__(
        self,
        name: str,
        case_type: str,
        jurisdiction: str,
        version: str = "1.0",
        description: str = ""
    ):
        """Initialize questionnaire template."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.case_type = case_type
        self.jurisdiction = jurisdiction
        self.version = version
        self.description = description
        self.sections: List[QuestionnaireSection] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = QuestionnaireStatus.DRAFT
        logger.info(f"Initialized questionnaire: {self.name} ({self.id})")

    def add_section(self, section: QuestionnaireSection) -> None:
        """Add a section to the questionnaire."""
        if not isinstance(section, QuestionnaireSection):
            raise TypeError("Section must be QuestionnaireSection instance")
        self.sections.append(section)
        self.updated_at = datetime.now()
        logger.debug(f"Added section: {section.id}")

    def add_question_to_section(
        self,
        section_id: str,
        question: Question
    ) -> None:
        """Add a question to a specific section."""
        section = self._get_section(section_id)
        if not section:
            raise ValueError(f"Section not found: {section_id}")
        section.questions.append(question)
        self.updated_at = datetime.now()
        logger.debug(f"Added question: {question.id} to section: {section_id}")

    def _get_section(self, section_id: str) -> Optional[QuestionnaireSection]:
        """Get section by ID."""
        return next((s for s in self.sections if s.id == section_id), None)

    def get_visible_questions(
        self,
        responses: Dict[str, Any]
    ) -> List[Question]:
        """Get questions visible based on current responses."""
        visible = []
        for section in self.sections:
            for question in section.questions:
                if self._is_question_visible(question, responses):
                    visible.append(question)
        return visible

    def _is_question_visible(
        self,
        question: Question,
        responses: Dict[str, Any]
    ) -> bool:
        """Check if question is visible based on conditions."""
        if not question.conditional_parent:
            return True

        parent_response = responses.get(question.conditional_parent)
        return parent_response == question.conditional_value

    def validate_responses(
        self,
        responses: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate questionnaire responses."""
        errors = []
        visible_questions = self.get_visible_questions(responses)

        for question in visible_questions:
            if question.required and question.id not in responses:
                errors.append(f"Question '{question.text}' is required")

            if question.id in responses:
                value = responses[question.id]
                # Type validation
                if question.question_type == QuestionType.CURRENCY:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Invalid currency value for {question.id}")

                # Length validation
                if question.max_length and isinstance(value, str):
                    if len(value) > question.max_length:
                        errors.append(
                            f"Answer to '{question.text}' exceeds max length"
                        )

        return len(errors) == 0, errors

    def get_completion_status(
        self,
        responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get questionnaire completion status."""
        total_visible = len(self.get_visible_questions(responses))
        answered = sum(1 for q in self.get_visible_questions(responses)
                      if q.id in responses)

        return {
            "total_visible_questions": total_visible,
            "answered_questions": answered,
            "completion_percentage": (answered / total_visible * 100) if total_visible > 0 else 0,
            "status": "complete" if answered == total_visible else "in_progress"
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "case_type": self.case_type,
            "jurisdiction": self.jurisdiction,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "sections": [s.to_dict() for s in self.sections],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def save_to_file(self, file_path: Path) -> None:
        """Save questionnaire to JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Questionnaire saved to: {file_path}")

    @classmethod
    def load_from_file(cls, file_path: Path) -> "QuestionnaireTemplate":
        """Load questionnaire from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded questionnaire from: {file_path}")
        # Reconstruction logic would go here
        return cls(
            name=data['name'],
            case_type=data['case_type'],
            jurisdiction=data['jurisdiction'],
            version=data.get('version', '1.0')
        )


class QuestionnaireBuilder:
    """Builder for constructing questionnaires."""

    def __init__(self, name: str, case_type: str, jurisdiction: str):
        """Initialize builder."""
        self.questionnaire = QuestionnaireTemplate(
            name=name,
            case_type=case_type,
            jurisdiction=jurisdiction
        )

    def add_section(self, section: QuestionnaireSection) -> "QuestionnaireBuilder":
        """Add section and return self for chaining."""
        self.questionnaire.add_section(section)
        return self

    def add_question(self, section_id: str, question: Question) -> "QuestionnaireBuilder":
        """Add question and return self for chaining."""
        self.questionnaire.add_question_to_section(section_id, question)
        return self

    def build(self) -> QuestionnaireTemplate:
        """Build and return questionnaire."""
        self.questionnaire.status = QuestionnaireStatus.ACTIVE
        logger.info(f"Built questionnaire: {self.questionnaire.name}")
        return self.questionnaire


def create_sample_questionnaire() -> QuestionnaireTemplate:
    """Create a sample questionnaire for demonstration."""
    builder = QuestionnaireBuilder(
        "Personal Injury Claim",
        "personal_injury",
        "US_CA"
    )

    # Create first section
    plaintiff_section = QuestionnaireSection(
        id="plaintiff_info",
        title="Plaintiff Information",
        description="Basic information about the claimant",
        order=1
    )

    # Add questions
    name_question = Question(
        id="plaintiff_name",
        text="Full Legal Name",
        question_type=QuestionType.TEXT,
        required=True,
        help_text="As it appears on official documents",
        max_length=100
    )

    injury_type = Question(
        id="injury_type",
        text="Type of Injury",
        question_type=QuestionType.MULTIPLE_CHOICE,
        required=True,
        options=[
            QuestionOption("1", "Physical Injury", "physical"),
            QuestionOption("2", "Emotional Distress", "emotional"),
            QuestionOption("3", "Both", "both")
        ]
    )

    damage_amount = Question(
        id="damage_amount",
        text="Estimated Damages",
        question_type=QuestionType.CURRENCY,
        required=True,
        conditional_parent="injury_type",
        conditional_value="physical"
    )

    builder.add_section(plaintiff_section)
    builder.add_question("plaintiff_info", name_question)
    builder.add_question("plaintiff_info", injury_type)
    builder.add_question("plaintiff_info", damage_amount)

    return builder.build()


if __name__ == "__main__":
    # Create and test questionnaire
    questionnaire = create_sample_questionnaire()
    print(json.dumps(questionnaire.to_dict(), indent=2))

    # Test validation
    test_responses = {
        "plaintiff_name": "John Doe",
        "injury_type": "physical",
        "damage_amount": "50000"
    }

    is_valid, errors = questionnaire.validate_responses(test_responses)
    print(f"\nValidation result: {is_valid}")
    if errors:
        print("Errors:", errors)

    # Test completion status
    print("\nCompletion status:", questionnaire.get_completion_status(test_responses))
