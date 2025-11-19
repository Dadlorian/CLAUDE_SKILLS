"""
Legal Citation Parser
Extracts and validates legal citations from text using regex and NLP
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CitationType(Enum):
    """Types of legal citations"""
    CASE = "case"
    STATUTE = "statute"
    REGULATION = "regulation"
    CONSTITUTION = "constitution"
    UNKNOWN = "unknown"


@dataclass
class Citation:
    """Parsed citation"""
    raw_text: str
    citation_type: CitationType
    volume: Optional[str] = None
    reporter: Optional[str] = None
    page: Optional[str] = None
    year: Optional[str] = None
    court: Optional[str] = None
    pinpoint: Optional[str] = None


class LegalCitationParser:
    """
    Parse legal citations from text using regex patterns
    Supports Bluebook citation format
    """

    # Regex patterns for different citation types
    PATTERNS = {
        # Federal case citations: 505 U.S. 144 (1992)
        "federal_case": r'(\d+)\s+(U\.S\.|S\.\s*Ct\.|F\.\s*(?:2d|3d|4th|App\'x|Supp\.(?:\s*2d|3d)?))\s+(\d+)(?:,\s*(\d+))?\s*\((\d{4})\)',

        # State case citations: 123 Cal. App. 4th 567 (2005)
        "state_case": r'(\d+)\s+([A-Z][a-z]+\.(?:\s+App\.)?(?:\s+\d[a-z]{2})?)\s+(\d+)(?:,\s*(\d+))?\s*\((\d{4})\)',

        # U.S. Code: 42 U.S.C. § 1983
        "usc": r'(\d+)\s+U\.S\.C\.\s*§+\s*(\d+[a-z]?(?:\([a-z0-9]+\))*)',

        # Code of Federal Regulations: 29 C.F.R. § 1630.2(g)
        "cfr": r'(\d+)\s+C\.F\.R\.\s*§+\s*(\d+(?:\.\d+)*(?:\([a-z0-9]+\))*)',

        # State statutes: Cal. Civ. Code § 1234
        "state_statute": r'([A-Z][a-z]+\.)\s+([A-Z][a-z]+\.)\s+(?:Code|Stat\.)\s*§+\s*(\d+(?:\.\d+)*)',

        # Constitutional provisions: U.S. Const. art. I, § 8
        "constitution": r'U\.S\.\s+Const\.\s+(?:art\.|amend\.)\s+([IVX]+|[0-9]+)(?:,\s*§\s*(\d+))?'
    }

    def __init__(self):
        """Initialize parser with compiled regex patterns"""
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.PATTERNS.items()
        }

    def extract_citations(self, text: str) -> List[Citation]:
        """
        Extract all citations from text

        Args:
            text: Text to parse

        Returns:
            List of Citation objects
        """
        citations = []

        # Try each pattern
        for pattern_name, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)

            for match in matches:
                citation = self.parse_match(match, pattern_name)
                if citation:
                    citations.append(citation)

        # Deduplicate
        unique_citations = self.deduplicate_citations(citations)

        return unique_citations

    def parse_match(self, match: re.Match, pattern_type: str) -> Optional[Citation]:
        """
        Parse regex match into Citation object

        Args:
            match: Regex match object
            pattern_type: Type of pattern matched

        Returns:
            Citation object or None
        """
        groups = match.groups()

        if pattern_type == "federal_case":
            return Citation(
                raw_text=match.group(0),
                citation_type=CitationType.CASE,
                volume=groups[0],
                reporter=groups[1],
                page=groups[2],
                pinpoint=groups[3] if len(groups) > 3 else None,
                year=groups[4] if len(groups) > 4 else None
            )

        elif pattern_type == "state_case":
            return Citation(
                raw_text=match.group(0),
                citation_type=CitationType.CASE,
                volume=groups[0],
                reporter=groups[1],
                page=groups[2],
                pinpoint=groups[3] if len(groups) > 3 else None,
                year=groups[4] if len(groups) > 4 else None
            )

        elif pattern_type in ["usc", "state_statute"]:
            return Citation(
                raw_text=match.group(0),
                citation_type=CitationType.STATUTE
            )

        elif pattern_type == "cfr":
            return Citation(
                raw_text=match.group(0),
                citation_type=CitationType.REGULATION
            )

        elif pattern_type == "constitution":
            return Citation(
                raw_text=match.group(0),
                citation_type=CitationType.CONSTITUTION
            )

        return None

    @staticmethod
    def deduplicate_citations(citations: List[Citation]) -> List[Citation]:
        """Remove duplicate citations"""
        seen = set()
        unique = []

        for cite in citations:
            if cite.raw_text not in seen:
                seen.add(cite.raw_text)
                unique.append(cite)

        return unique

    def normalize_citation(self, citation: Citation) -> str:
        """
        Normalize citation to standard format

        Args:
            citation: Citation object

        Returns:
            Normalized citation string
        """
        if citation.citation_type == CitationType.CASE:
            parts = [citation.volume, citation.reporter, citation.page]

            if citation.pinpoint:
                parts.append(f", {citation.pinpoint}")

            if citation.year:
                parts.append(f" ({citation.year})")

            return " ".join(filter(None, parts))

        return citation.raw_text

    def validate_citation_format(self, citation: str) -> Tuple[bool, List[str]]:
        """
        Validate citation follows Bluebook format

        Args:
            citation: Citation string

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Extract citation
        citations = self.extract_citations(citation)

        if not citations:
            errors.append("No valid citation found")
            return False, errors

        # Check specific format rules
        parsed = citations[0]

        if parsed.citation_type == CitationType.CASE:
            # Check reporter abbreviation
            if parsed.reporter and not self.is_valid_reporter(parsed.reporter):
                errors.append(f"Invalid reporter abbreviation: {parsed.reporter}")

            # Check year format
            if parsed.year and not re.match(r'^\d{4}$', parsed.year):
                errors.append(f"Invalid year format: {parsed.year}")

        return len(errors) == 0, errors

    @staticmethod
    def is_valid_reporter(reporter: str) -> bool:
        """Check if reporter abbreviation is valid"""
        valid_reporters = [
            "U.S.", "S. Ct.", "F.2d", "F.3d", "F.4th", "F. App'x",
            "F. Supp.", "F. Supp. 2d", "F. Supp. 3d"
        ]
        return reporter in valid_reporters


def main():
    """Example usage"""
    parser = LegalCitationParser()

    # Example text with various citations
    text = """
    The Supreme Court held in Roe v. Wade, 410 U.S. 113 (1973), that privacy rights
    extend to abortion. Later, in Planned Parenthood v. Casey, 505 U.S. 833, 846 (1992),
    the Court modified the standard. See also 42 U.S.C. § 1983 for civil rights actions.
    The regulations at 29 C.F.R. § 1630.2(g) define disability. Under U.S. Const. amend. XIV,
    equal protection is guaranteed.
    """

    citations = parser.extract_citations(text)

    print(f"Found {len(citations)} citations:\n")

    for cite in citations:
        print(f"Citation: {cite.raw_text}")
        print(f"  Type: {cite.citation_type.value}")
        print(f"  Normalized: {parser.normalize_citation(cite)}")
        print()

    # Validate citation format
    test_citation = "505 U.S. 833, 846 (1992)"
    is_valid, errors = parser.validate_citation_format(test_citation)

    print(f"Validation of '{test_citation}':")
    print(f"  Valid: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")


if __name__ == "__main__":
    main()
