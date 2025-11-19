"""
Citation Validator
Validates legal citations for proper formatting and accuracy
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CitationValidationResult:
    """Result of citation validation"""
    citation: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    normalized_form: Optional[str] = None
    suggested_fix: Optional[str] = None


class CitationFormat(Enum):
    """Supported citation formats"""
    BLUEBOOK = "bluebook"
    ALWD = "alwd"
    VENDOR = "vendor"


class LegalCitationValidator:
    """
    Validates legal citations according to Bluebook standards
    """

    # Case citation patterns
    CASE_PATTERNS = {
        "federal": r"(\d+)\s+(U\.S\.|S\.\s*Ct\.|L\.\s*Ed\.(?:\s*2d)?|F\.(?:\s*2d|3d|4th)?)(\s+)(\d+)",
        "reporter": r"(\d+)\s+([A-Z]{1,3}(?:\.\s*[A-Z]{1,3})*)\s+(\d+)",
        "parallel": r"(\d+)\s+([A-Z\.]+)\s+(\d+),\s+(\d+)\s+([A-Z\.]+)\s+(\d+)"
    }

    # Statute patterns
    STATUTE_PATTERNS = {
        "usc": r"(\d+)\s+U\.S\.C\.(?:\s+§+\s*)(\d+)",
        "cfr": r"(\d+)\s+C\.F\.R\.(?:\s+§+\s*)(\d+(?:\.\d+)*)",
        "state": r"([A-Z][a-z]+\.)\s+([A-Z][a-z]+\.)\s+(Code|Stat\.)(?:\s+§+\s*)(\d+)"
    }

    def __init__(self, citation_format: CitationFormat = CitationFormat.BLUEBOOK):
        """
        Initialize validator

        Args:
            citation_format: Citation format standard to validate against
        """
        self.citation_format = citation_format
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, pattern in {**self.CASE_PATTERNS, **self.STATUTE_PATTERNS}.items()
        }
        self.reporter_abbreviations = self._load_reporter_abbreviations()
        self.court_abbreviations = self._load_court_abbreviations()

    @staticmethod
    def _load_reporter_abbreviations() -> Dict[str, str]:
        """Load common reporter abbreviations"""
        return {
            "U.S.": "United States Reports",
            "S.Ct.": "Supreme Court Reporter",
            "L.Ed.": "Lawyers' Edition",
            "F.": "Federal Reporter",
            "F.2d": "Federal Reporter, Second Series",
            "F.3d": "Federal Reporter, Third Series",
            "F.Supp.": "Federal Supplement",
            "F.Supp.2d": "Federal Supplement, Second Series",
            "F.Supp.3d": "Federal Supplement, Third Series",
        }

    @staticmethod
    def _load_court_abbreviations() -> Dict[str, str]:
        """Load court abbreviations"""
        return {
            "U.S.": "United States",
            "1st Cir.": "First Circuit",
            "2d Cir.": "Second Circuit",
            "3d Cir.": "Third Circuit",
            "4th Cir.": "Fourth Circuit",
            "9th Cir.": "Ninth Circuit",
        }

    def validate(self, citation: str) -> CitationValidationResult:
        """
        Validate a single citation

        Args:
            citation: Citation text to validate

        Returns:
            CitationValidationResult
        """
        citation = citation.strip()
        errors = []
        warnings = []
        is_valid = True
        normalized_form = None

        # Check basic formatting
        if not citation:
            errors.append("Citation cannot be empty")
            is_valid = False

        # Check for common formatting errors
        if "  " in citation:
            warnings.append("Multiple spaces detected")
            citation = re.sub(r'\s+', ' ', citation)

        # Validate against patterns
        matches = False
        for pattern_type, pattern in self.compiled_patterns.items():
            if pattern.search(citation):
                matches = True
                normalized_form = self._normalize_citation(citation, pattern_type)
                break

        if not matches and is_valid:
            warnings.append("Citation format not recognized")

        # Validate specific elements
        if "§" in citation or "&" in citation.replace("amp;", " "):
            # Check section number formatting
            section_match = re.search(r'§+\s*(\d+[a-z]?(?:\([a-z0-9]+\))*)', citation)
            if not section_match:
                warnings.append("Section number formatting may be incorrect")

        # Validate year in parentheses
        year_match = re.search(r'\((\d{4})\)', citation)
        if year_match:
            year = int(year_match.group(1))
            if year < 1800 or year > 2100:
                errors.append(f"Year {year} appears invalid")
                is_valid = False

        # Check for common typos
        typos = self._check_for_typos(citation)
        warnings.extend(typos)

        return CitationValidationResult(
            citation=citation,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            normalized_form=normalized_form,
            suggested_fix=self._suggest_fix(citation, errors) if errors else None
        )

    def validate_batch(self, citations: List[str]) -> List[CitationValidationResult]:
        """
        Validate multiple citations

        Args:
            citations: List of citations to validate

        Returns:
            List of validation results
        """
        return [self.validate(citation) for citation in citations]

    @staticmethod
    def _normalize_citation(citation: str, pattern_type: str) -> str:
        """
        Normalize citation to standard form

        Args:
            citation: Citation to normalize
            pattern_type: Type of citation

        Returns:
            Normalized citation
        """
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', citation)

        # Standardize section symbol
        normalized = normalized.replace("&sect;", "§").replace("&", "§")

        # Standardize reporter abbreviations
        normalized = re.sub(r'\bU\s*S\s*C\b', 'U.S.C.', normalized)

        return normalized

    @staticmethod
    def _check_for_typos(citation: str) -> List[str]:
        """Check for common citation typos"""
        warnings = []

        # Check for common abbreviation typos
        if re.search(r'\bU\.S\.C\s+§', citation):
            warnings.append("Missing period after 'C' in U.S.C")

        if re.search(r'§+\s*§+', citation):
            warnings.append("Duplicate section symbols")

        if re.search(r'\(\s*\d{4}\s*\)\s+\d{4}', citation):
            warnings.append("Possible duplicate year formatting")

        return warnings

    @staticmethod
    def _suggest_fix(citation: str, errors: List[str]) -> str:
        """Suggest citation fix based on errors"""
        if not errors:
            return citation

        fixed = citation

        # Fix spacing
        fixed = re.sub(r'\s+', ' ', fixed)

        # Fix missing periods
        fixed = fixed.replace("U S C", "U.S.C.")
        fixed = fixed.replace("F Supp", "F. Supp.")

        return fixed

    def compare_citations(self, citation1: str, citation2: str) -> bool:
        """
        Check if two citations refer to the same work

        Args:
            citation1: First citation
            citation2: Second citation

        Returns:
            True if citations refer to same work
        """
        result1 = self.validate(citation1)
        result2 = self.validate(citation2)

        if result1.normalized_form and result2.normalized_form:
            return result1.normalized_form == result2.normalized_form

        return citation1 == citation2

    def extract_citation_elements(self, citation: str) -> Dict[str, str]:
        """
        Extract individual elements from citation

        Args:
            citation: Citation to parse

        Returns:
            Dictionary of citation elements
        """
        elements = {}

        # Extract volume
        volume_match = re.search(r'^(\d+)\s+', citation)
        if volume_match:
            elements['volume'] = volume_match.group(1)

        # Extract reporter
        reporter_match = re.search(r'(\d+\s+)?([A-Z\.]+\s+[A-Z\.]+|[A-Z\.]+)\s+(\d+)', citation)
        if reporter_match:
            elements['reporter'] = reporter_match.group(2).strip()

        # Extract page
        page_match = re.search(r'[A-Z\.]+(2d|3d|4th)?\s+(\d+)', citation)
        if page_match:
            elements['page'] = page_match.group(2)

        # Extract year
        year_match = re.search(r'\((\d{4})\)', citation)
        if year_match:
            elements['year'] = year_match.group(1)

        # Extract court
        court_match = re.search(r'\(([A-Z\d\. ]+)\s+(\d{4})\)', citation)
        if court_match:
            elements['court'] = court_match.group(1)

        return elements


# Usage example
if __name__ == "__main__":
    validator = LegalCitationValidator()

    # Test citations
    test_citations = [
        "123 U.S. 456 (2020)",
        "42 U.S.C. § 1983",
        "123F.3d456(9thCir.2020)",
        "Invalid Citation Here"
    ]

    for citation in test_citations:
        result = validator.validate(citation)
        print(f"\nCitation: {citation}")
        print(f"Valid: {result.is_valid}")
        if result.warnings:
            print(f"Warnings: {', '.join(result.warnings)}")
        if result.errors:
            print(f"Errors: {', '.join(result.errors)}")
