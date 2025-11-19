"""
Case Summarizer
Summarizes court opinions and extracts key case information
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CaseSummary:
    """Structured case summary"""
    citation: str
    case_name: str
    court: str
    year: int
    parties: Dict[str, str]  # plaintiff, defendant, etc.
    facts: str
    procedural_history: str
    legal_issue: str
    holding: str
    reasoning: str
    dissent: Optional[str] = None
    concurrence: Optional[str] = None
    keywords: List[str] = None
    citations: List[str] = None


class CaseSummarizer:
    """
    Summarizes court opinions
    """

    def __init__(self):
        """Initialize summarizer"""
        self.section_indicators = {
            "facts": r"(?:facts|background|procedural history|as follows|the record shows)",
            "procedure": r"(?:procedural history|procedural background|on (?:appeal|review))",
            "issue": r"(?:the (?:legal\s+)?issue|the question (?:is|presented)|we consider)",
            "holding": r"(?:held|we (?:hold|affirm|reverse|vacate)|judgment|decision|holding)",
            "reasoning": r"(?:reasoning|analysis|discussion|we believe|the court)",
            "concurrence": r"(?:concurrence|concurring opinion|Justice.*concurring)",
            "dissent": r"(?:dissent|dissenting opinion|Justice.*dissenting)"
        }

    def summarize_opinion(self, opinion_text: str, citation: str = "") -> CaseSummary:
        """
        Summarize a court opinion

        Args:
            opinion_text: Full text of court opinion
            citation: Case citation

        Returns:
            CaseSummary object
        """
        # Extract basic information
        case_name = self._extract_case_name(opinion_text)
        court = self._extract_court(opinion_text)
        year = self._extract_year(opinion_text)
        parties = self._extract_parties(case_name)

        # Extract sections
        facts = self._extract_section(opinion_text, "facts", 300)
        procedure = self._extract_section(opinion_text, "procedure", 200)
        issue = self._extract_section(opinion_text, "issue", 150)
        holding = self._extract_holding(opinion_text)
        reasoning = self._extract_section(opinion_text, "reasoning", 400)
        dissent = self._extract_section(opinion_text, "dissent", 200)
        concurrence = self._extract_section(opinion_text, "concurrence", 200)

        # Extract metadata
        keywords = self._extract_keywords(opinion_text)
        citations = self._extract_citations(opinion_text)

        summary = CaseSummary(
            citation=citation,
            case_name=case_name,
            court=court,
            year=year,
            parties=parties,
            facts=facts,
            procedural_history=procedure,
            legal_issue=issue,
            holding=holding,
            reasoning=reasoning,
            dissent=dissent,
            concurrence=concurrence,
            keywords=keywords,
            citations=citations
        )

        logger.info(f"Summarized case: {case_name}")
        return summary

    @staticmethod
    def _extract_case_name(text: str) -> str:
        """Extract case name from opinion"""
        # Look for "v." pattern
        match = re.search(r"([A-Z][a-z\.\s]+?)\s+v\.(?:\s+|$)([A-Z][a-z\.\s]+?)(?:\s*,|\s*$)", text[:500])
        if match:
            return f"{match.group(1).strip()} v. {match.group(2).strip()}"
        return "Unknown Case"

    @staticmethod
    def _extract_court(text: str) -> str:
        """Extract court name from opinion"""
        courts = [
            "United States Supreme Court",
            r"U\.S\. Court of Appeals",
            r"(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Federal|DC|D\.C\.)\s+Circuit",
            r"United States District Court",
            r"[A-Z][a-z]+\s+(?:Court of Appeals|Superior Court|District Court)"
        ]

        for court_pattern in courts:
            match = re.search(court_pattern, text[:1000])
            if match:
                return match.group(0)

        return "Unknown Court"

    @staticmethod
    def _extract_year(text: str) -> int:
        """Extract year from opinion"""
        matches = re.findall(r"(?:decided|filed|delivered|handed down).*?(\d{4})", text[:500], re.IGNORECASE)
        if matches:
            return int(matches[0])

        # Try to find year in parentheses at end
        year_match = re.search(r"\((\d{4})\)\s*$", text.strip())
        if year_match:
            return int(year_match.group(1))

        return 2024

    @staticmethod
    def _extract_parties(case_name: str) -> Dict[str, str]:
        """Extract parties from case name"""
        parts = case_name.split(" v. ")
        return {
            "plaintiff": parts[0] if len(parts) > 0 else "Unknown",
            "defendant": parts[1] if len(parts) > 1 else "Unknown"
        }

    def _extract_section(self, text: str, section_type: str, max_words: int) -> str:
        """Extract a section of opinion"""
        pattern = self.section_indicators.get(section_type)
        if not pattern:
            return ""

        # Find the section start
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ""

        start_pos = match.start()
        section_text = text[start_pos:]

        # Find section boundary (next major section indicator)
        boundary_match = re.search(r"\n\n(?:I{1,3}\.|\d+\.|\*\*)", section_text[50:])
        if boundary_match:
            section_text = section_text[:boundary_match.start() + 50]

        # Limit word count
        words = section_text.split()[:max_words]
        return " ".join(words)

    @staticmethod
    def _extract_holding(text: str) -> str:
        """Extract main holding from opinion"""
        holding_patterns = [
            r"(?:the court\s+)?affirm(?:ed|s)?.*?\.",
            r"(?:the judgment is )?reversed.*?\.",
            r"held:?\s+([^.]+)\.",
            r"we (?:hold|affirm|reverse|vacate)\s+([^.]+)\."
        ]

        for pattern in holding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)

        return "Judgment affirmed/reversed (specific holding not extracted)"

    @staticmethod
    def _extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
        """Extract key legal terms from opinion"""
        # Legal keywords
        legal_terms = [
            "breach", "contract", "tort", "negligence", "liability",
            "damages", "injunction", "statute", "regulation", "constitutional",
            "due process", "equal protection", "probable cause", "warrant",
            "discovery", "hearsay", "jurisdiction", "venue"
        ]

        found_terms = [term for term in legal_terms if term in text.lower()]
        return found_terms[:num_keywords]

    @staticmethod
    def _extract_citations(text: str) -> List[str]:
        """Extract citations from opinion"""
        citation_pattern = r"(\d+\s+[A-Z\.]+\s+\d+(?:\s*\(\w+\s+\d{4}\))?)"
        citations = re.findall(citation_pattern, text)
        return list(set(citations))[:20]

    def format_summary(self, summary: CaseSummary) -> str:
        """
        Format summary for reading

        Args:
            summary: CaseSummary object

        Returns:
            Formatted summary text
        """
        formatted = f"""
CASE SUMMARY
============

Case: {summary.case_name}
Citation: {summary.citation}
Court: {summary.court}
Year: {summary.year}

PARTIES
-------
Plaintiff: {summary.parties.get('plaintiff')}
Defendant: {summary.parties.get('defendant')}

FACTS
-----
{summary.facts}

PROCEDURE
---------
{summary.procedural_history}

LEGAL ISSUE
-----------
{summary.legal_issue}

HOLDING
-------
{summary.holding}

REASONING
---------
{summary.reasoning}

KEYWORDS
--------
{', '.join(summary.keywords or [])}
"""

        if summary.dissent:
            formatted += f"\nDISSENT\n-------\n{summary.dissent}"

        return formatted


# Usage example
if __name__ == "__main__":
    sample_opinion = """
    Marbury v. Madison
    United States Supreme Court
    Decided February 24, 1803

    FACTS: William Marbury was appointed Justice of the Peace by President John Adams
    in his final days in office. However, his commission was not delivered before
    Thomas Jefferson became president. Jefferson's Secretary of State, James Madison,
    refused to deliver the commission.

    ISSUE: Does the Supreme Court have the authority to issue a writ of mandamus
    compelling Madison to deliver Marbury's commission?

    HOLDING: The Court held that while Marbury had a right to his commission and
    the law provided a remedy, the Supreme Court lacked the authority to issue a
    writ of mandamus in this case under its original jurisdiction.

    REASONING: Chief Justice Marshall reasoned that the Judiciary Act of 1789 was
    unconstitutional as it expanded the Supreme Court's original jurisdiction beyond
    what the Constitution allowed. This established the principle of judicial review.
    """

    summarizer = CaseSummarizer()
    summary = summarizer.summarize_opinion(sample_opinion, "5 U.S. (1 Cranch) 137 (1803)")

    print(summarizer.format_summary(summary))
