"""
Accessibility Checker for Legal Documents
Checks documents for accessibility compliance (WCAG, ADA, Section 508).

Dependencies: None (standard library)
Install: No additional dependencies required
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import re


class SeverityLevel(Enum):
    """Severity of accessibility issue."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AccessibilityIssueType(Enum):
    """Types of accessibility issues."""
    MISSING_ALT_TEXT = "missing_alt_text"
    POOR_COLOR_CONTRAST = "poor_color_contrast"
    MISSING_HEADINGS = "missing_headings"
    INVALID_HEADING_STRUCTURE = "invalid_heading_structure"
    MISSING_DOCUMENT_TITLE = "missing_document_title"
    POOR_FORMATTING = "poor_formatting"
    INACCESSIBLE_TABLE = "inaccessible_table"
    MISSING_LINK_TEXT = "missing_link_text"
    FONTS_TOO_SMALL = "fonts_too_small"
    INSUFFICIENT_LINE_SPACING = "insufficient_line_spacing"
    WALL_OF_TEXT = "wall_of_text"
    MISSING_PAGE_NUMBERS = "missing_page_numbers"


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue."""
    issue_type: AccessibilityIssueType
    severity: SeverityLevel
    page_number: int
    location: str
    description: str
    recommendation: str

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.issue_type.value}: {self.description}"


class AccessibilityChecker:
    """Checks documents for accessibility compliance."""

    def __init__(self, document_text: str):
        """Initialize checker with document text."""
        self.document_text = document_text
        self.lines = document_text.split('\n')
        self.issues: List[AccessibilityIssue] = []
        self.page_count = self._estimate_page_count()

    def check_all(self) -> List[AccessibilityIssue]:
        """Run all accessibility checks."""
        self.check_document_title()
        self.check_heading_structure()
        self.check_text_formatting()
        self.check_font_sizes()
        self.check_line_spacing()
        self.check_wall_of_text()
        self.check_link_accessibility()
        self.check_list_formatting()
        self.check_table_accessibility()
        self.check_page_numbers()

        return self.issues

    def check_document_title(self) -> None:
        """Check if document has a title."""
        if not self.lines or len(self.lines[0].strip()) == 0:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.MISSING_DOCUMENT_TITLE,
                severity=SeverityLevel.ERROR,
                page_number=1,
                location="Document start",
                description="Document is missing a clear title",
                recommendation="Add a descriptive title at the beginning of the document"
            ))

    def check_heading_structure(self) -> None:
        """Check heading hierarchy."""
        headings = []
        current_level = 0

        for i, line in enumerate(self.lines):
            # Count hash marks for markdown-style headings
            match = re.match(r'^(#+)\s+(.+)', line)
            if match:
                level = len(match.group(1))
                text = match.group(2)
                headings.append((i, level, text))

        if not headings:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.MISSING_HEADINGS,
                severity=SeverityLevel.WARNING,
                page_number=1,
                location="Document structure",
                description="Document lacks structured headings",
                recommendation="Add hierarchical headings (H1, H2, H3) to organize content"
            ))

        # Check for proper hierarchy
        for i, (line_num, level, text) in enumerate(headings):
            if i == 0 and level != 1:
                self.issues.append(AccessibilityIssue(
                    issue_type=AccessibilityIssueType.INVALID_HEADING_STRUCTURE,
                    severity=SeverityLevel.WARNING,
                    page_number=1,
                    location=f"Line {line_num}",
                    description=f"First heading should be H1, not H{level}",
                    recommendation="Start with H1 heading and follow proper hierarchy"
                ))

            if i > 0:
                prev_level = headings[i-1][1]
                if level > prev_level + 1:
                    self.issues.append(AccessibilityIssue(
                        issue_type=AccessibilityIssueType.INVALID_HEADING_STRUCTURE,
                        severity=SeverityLevel.WARNING,
                        page_number=1,
                        location=f"Line {line_num}",
                        description=f"Heading jumps from H{prev_level} to H{level}",
                        recommendation="Follow logical heading hierarchy without skipping levels"
                    ))

    def check_text_formatting(self) -> None:
        """Check for proper text formatting."""
        # Check for italicized text without semantic purpose
        italic_pattern = r'\*{1}[^*]+\*{1}|_{1}[^_]+_{1}'
        italic_count = len(re.findall(italic_pattern, self.document_text))

        if italic_count > 10:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.POOR_FORMATTING,
                severity=SeverityLevel.INFO,
                page_number=1,
                location="Throughout document",
                description="Excessive italicized text may reduce readability",
                recommendation="Use bold sparingly for emphasis and plain text for body content"
            ))

    def check_font_sizes(self) -> None:
        """Check for minimum font size."""
        # This is a heuristic check for short lines indicating small fonts
        short_lines = sum(1 for line in self.lines if len(line.strip()) < 20)

        if short_lines > len(self.lines) * 0.3:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.FONTS_TOO_SMALL,
                severity=SeverityLevel.WARNING,
                page_number=1,
                location="Throughout document",
                description="Many short lines suggest small font sizes",
                recommendation="Use minimum 12pt font for body text, 16pt+ for headings"
            ))

    def check_line_spacing(self) -> None:
        """Check for adequate line spacing."""
        # Count average blank lines
        blank_lines = sum(1 for line in self.lines if line.strip() == '')

        if blank_lines < len(self.lines) * 0.1:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.INSUFFICIENT_LINE_SPACING,
                severity=SeverityLevel.WARNING,
                page_number=1,
                location="Throughout document",
                description="Document may have insufficient line spacing",
                recommendation="Use 1.5 or double spacing for better readability"
            ))

    def check_wall_of_text(self) -> None:
        """Check for overly long paragraphs."""
        current_paragraph_length = 0
        max_paragraph_length = 0

        for line in self.lines:
            if line.strip():
                current_paragraph_length += 1
            else:
                max_paragraph_length = max(max_paragraph_length, current_paragraph_length)
                current_paragraph_length = 0

        if max_paragraph_length > 15:
            self.issues.append(AccessibilityIssue(
                issue_type=AccessibilityIssueType.WALL_OF_TEXT,
                severity=SeverityLevel.WARNING,
                page_number=1,
                location="Document body",
                description="Very long paragraphs reduce readability",
                recommendation="Break long paragraphs into shorter ones (3-5 sentences max)"
            ))

    def check_link_accessibility(self) -> None:
        """Check for accessible link text."""
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, self.document_text)

        generic_text = ['click here', 'link', 'read more', 'more information']

        for text, url in links:
            if text.lower() in generic_text:
                self.issues.append(AccessibilityIssue(
                    issue_type=AccessibilityIssueType.MISSING_LINK_TEXT,
                    severity=SeverityLevel.WARNING,
                    page_number=1,
                    location=f"Link: {url}",
                    description=f"Link text '{text}' is not descriptive",
                    recommendation="Use descriptive link text that explains the destination"
                ))

    def check_list_formatting(self) -> None:
        """Check for proper list formatting."""
        numbered_lists = len(re.findall(r'^\d+\.\s+', self.document_text, re.MULTILINE))
        bulleted_lists = len(re.findall(r'^[\-\*]\s+', self.document_text, re.MULTILINE))

        if numbered_lists == 0 and bulleted_lists == 0:
            # Check for comma-separated items that should be lists
            long_items = re.findall(r'.*,\s+.*,\s+.*,', self.document_text)
            if len(long_items) > 2:
                self.issues.append(AccessibilityIssue(
                    issue_type=AccessibilityIssueType.POOR_FORMATTING,
                    severity=SeverityLevel.INFO,
                    page_number=1,
                    location="Throughout document",
                    description="Comma-separated items should be formatted as lists",
                    recommendation="Use bulleted or numbered lists for items"
                ))

    def check_table_accessibility(self) -> None:
        """Check for accessible table formatting."""
        # Simple check for pipe-delimited tables
        table_lines = [line for line in self.lines if '|' in line]

        if len(table_lines) > 0:
            # Check if first row has header indicators
            if table_lines and '---' not in table_lines[1:2]:
                self.issues.append(AccessibilityIssue(
                    issue_type=AccessibilityIssueType.INACCESSIBLE_TABLE,
                    severity=SeverityLevel.WARNING,
                    page_number=1,
                    location="Table",
                    description="Table lacks clear header row",
                    recommendation="Mark header rows clearly and use table markup"
                ))

    def check_page_numbers(self) -> None:
        """Check for page numbers."""
        if self.page_count > 1:
            page_pattern = r'(Page \d+|Page \d+ of \d+)'
            if not re.search(page_pattern, self.document_text, re.IGNORECASE):
                self.issues.append(AccessibilityIssue(
                    issue_type=AccessibilityIssueType.MISSING_PAGE_NUMBERS,
                    severity=SeverityLevel.WARNING,
                    page_number=1,
                    location="Header/Footer",
                    description="Multi-page document lacks page numbers",
                    recommendation="Add page numbers to all pages for easy navigation"
                ))

    def _estimate_page_count(self) -> int:
        """Estimate page count (lines per page ~50)."""
        return max(1, len(self.lines) // 50)

    def get_report(self) -> str:
        """Generate accessibility report."""
        if not self.issues:
            self.check_all()

        # Group by severity
        errors = [i for i in self.issues if i.severity == SeverityLevel.ERROR]
        warnings = [i for i in self.issues if i.severity == SeverityLevel.WARNING]
        infos = [i for i in self.issues if i.severity == SeverityLevel.INFO]

        report = f"""
{'='*70}
ACCESSIBILITY COMPLIANCE REPORT
{'='*70}

Document Statistics:
  Estimated Pages: {self.page_count}
  Total Lines: {len(self.lines)}
  Total Characters: {len(self.document_text)}

Compliance Summary:
  Errors: {len(errors)}
  Warnings: {len(warnings)}
  Information: {len(infos)}
  Total Issues: {len(self.issues)}

Compliance Score: {self._calculate_score()}%

{'-'*70}
CRITICAL ERRORS (Must Fix)
{'-'*70}
"""

        if errors:
            for issue in errors:
                report += f"\n{issue}\n"
                report += f"  Location: {issue.location}\n"
                report += f"  Recommendation: {issue.recommendation}\n"
        else:
            report += "\nNo critical errors found.\n"

        report += f"\n{'-'*70}\n"
        report += "WARNINGS (Should Fix)\n"
        report += f"{'-'*70}\n"

        if warnings:
            for issue in warnings:
                report += f"\n{issue}\n"
                report += f"  Location: {issue.location}\n"
                report += f"  Recommendation: {issue.recommendation}\n"
        else:
            report += "\nNo warnings.\n"

        report += f"\n{'-'*70}\n"
        report += "TIPS FOR IMPROVEMENT\n"
        report += f"{'-'*70}\n"

        if infos:
            for issue in infos:
                report += f"\n{issue}\n"
                report += f"  Recommendation: {issue.recommendation}\n"

        report += f"\n{'='*70}\n"
        return report

    def _calculate_score(self) -> int:
        """Calculate accessibility compliance score."""
        base_score = 100
        base_score -= len(self.issues) * 5  # 5 points per issue
        return max(0, base_score)


def example_check_contract():
    """Example: Check contract for accessibility."""

    contract = """
# SERVICE AGREEMENT

This Service Agreement is entered into between Client and Provider.

## 1. Services

Provider agrees to provide the following services:
- Legal consultation
- Document drafting
- Research

## 2. Fees

Hourly Rate: $250/hour

## 3. Term

Duration: 1 year
"""

    checker = AccessibilityChecker(contract)
    issues = checker.check_all()

    report = checker.get_report()
    print(report)

    with open('/tmp/accessibility_report.txt', 'w') as f:
        f.write(report)

    return checker


def example_check_legal_document():
    """Example: Check legal document for accessibility issues."""

    document = """LEGAL NOTICE

This is a legal notice to inform you of the following matter which is of great importance
and requires your immediate attention. We have determined that there are certain issues
that need to be addressed and resolved in a timely manner. Please read this document
carefully as it contains important information about your rights and obligations. The
information provided herein is confidential and should not be shared with unauthorized
parties. If you have any questions please contact our office immediately. This is a
lengthy paragraph that goes on and on without proper breaks which makes it difficult to
read and understand the content being presented in this notice.

Please note the following items: legal requirements, compliance matters, procedural rules
and regulatory standards.

Thank you for your attention.
"""

    checker = AccessibilityChecker(document)
    print("\n" + checker.get_report())

    return checker


if __name__ == "__main__":
    example_check_contract()
    example_check_legal_document()
    print("\nAccessibility checking examples completed!")
