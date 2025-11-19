"""
Document Comparison
Compares two legal documents to identify differences and track changes.

Dependencies: difflib, python-docx
Install: pip install python-docx
"""

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import difflib
from enum import Enum


class ChangeType(Enum):
    """Types of document changes."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class DocumentChange:
    """Represents a single change in document."""
    change_type: ChangeType
    line_number: int
    original_text: str
    new_text: str
    context: str = ""
    timestamp: datetime = None
    author: str = "Unknown"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class DocumentComparator:
    """Compares two legal documents and identifies changes."""

    def __init__(self, doc1_text: str, doc2_text: str, doc1_name: str = "Document 1",
                 doc2_name: str = "Document 2"):
        """Initialize comparator with two documents."""
        self.doc1_text = doc1_text
        self.doc2_text = doc2_text
        self.doc1_name = doc1_name
        self.doc2_name = doc2_name
        self.doc1_lines = doc1_text.split('\n')
        self.doc2_lines = doc2_text.split('\n')
        self.changes: List[DocumentChange] = []

    def compare(self) -> List[DocumentChange]:
        """Compare documents and return list of changes."""
        differ = difflib.Differ()
        diff = differ.compare(self.doc1_lines, self.doc2_lines)

        changes = []
        line_number = 0

        for change_line in diff:
            if change_line.startswith('- '):
                # Removed line
                original_text = change_line[2:].rstrip('\n')
                changes.append(DocumentChange(
                    change_type=ChangeType.REMOVED,
                    line_number=line_number,
                    original_text=original_text,
                    new_text="",
                    context="Line removed"
                ))
            elif change_line.startswith('+ '):
                # Added line
                new_text = change_line[2:].rstrip('\n')
                changes.append(DocumentChange(
                    change_type=ChangeType.ADDED,
                    line_number=line_number,
                    original_text="",
                    new_text=new_text,
                    context="Line added"
                ))
            elif change_line.startswith('? '):
                # Change indicator (skip)
                continue
            else:
                # Unchanged line
                line_number += 1

        self.changes = changes
        return changes

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of changes."""
        if not self.changes:
            self.compare()

        added = sum(1 for c in self.changes if c.change_type == ChangeType.ADDED)
        removed = sum(1 for c in self.changes if c.change_type == ChangeType.REMOVED)

        return {
            'total_changes': len(self.changes),
            'lines_added': added,
            'lines_removed': removed,
            'modification_percentage': self._calculate_modification_percentage()
        }

    def _calculate_modification_percentage(self) -> float:
        """Calculate percentage of document modified."""
        total_lines = max(len(self.doc1_lines), len(self.doc2_lines))
        if total_lines == 0:
            return 0.0
        changes = len(self.changes)
        return round((changes / total_lines) * 100, 2)

    def get_change_report(self) -> str:
        """Generate human-readable change report."""
        if not self.changes:
            self.compare()

        report = f"""
{'='*60}
DOCUMENT COMPARISON REPORT
{'='*60}

Comparing:
  - {self.doc1_name}
  - {self.doc2_name}

Comparison Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'-'*60}
SUMMARY
{'-'*60}
"""

        summary = self.get_summary()
        report += f"""
Total Changes: {summary['total_changes']}
Lines Added: {summary['lines_added']}
Lines Removed: {summary['lines_removed']}
Modification: {summary['modification_percentage']}%

{'-'*60}
DETAILED CHANGES
{'-'*60}
"""

        for i, change in enumerate(self.changes, 1):
            if change.change_type == ChangeType.ADDED:
                report += f"\n[{i}] ADDED (Line {change.line_number})\n"
                report += f"    {change.new_text}\n"
            elif change.change_type == ChangeType.REMOVED:
                report += f"\n[{i}] REMOVED (Line {change.line_number})\n"
                report += f"    {change.original_text}\n"

        report += f"\n{'='*60}\n"
        return report

    def get_side_by_side_comparison(self) -> str:
        """Generate side-by-side comparison."""
        matcher = difflib.SequenceMatcher(None, self.doc1_text, self.doc2_text)
        output = f"""
{'='*80}
SIDE-BY-SIDE COMPARISON
{'='*80}

{self.doc1_name.ljust(40)} | {self.doc2_name.ljust(40)}
{'-'*80}
"""

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                original = self.doc1_text[i1:i2][:35].ljust(40)
                new = self.doc2_text[j1:j2][:35].ljust(40)
                output += f"{original} | {new}\n"
            elif tag == 'delete':
                original = self.doc1_text[i1:i2][:35].ljust(40)
                output += f"{original} | [REMOVED]\n"
            elif tag == 'insert':
                new = self.doc2_text[j1:j2][:35].ljust(40)
                output += f"{'[ADDED]'.ljust(40)} | {new}\n"

        output += f"\n{'='*80}\n"
        return output

    def get_redline_version(self) -> str:
        """Generate redline version with track changes."""
        redline = f"REDLINE VERSION: {self.doc2_name}\n"
        redline += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        redline += "-" * 60 + "\n\n"

        if not self.changes:
            self.compare()

        for change in self.changes:
            if change.change_type == ChangeType.REMOVED:
                redline += f"[DELETED] {change.original_text}\n"
            elif change.change_type == ChangeType.ADDED:
                redline += f"[ADDED] {change.new_text}\n"

        return redline


class VersionControl:
    """Tracks document versions and their changes."""

    def __init__(self):
        """Initialize version control."""
        self.versions: List[Dict[str, Any]] = []

    def add_version(self, document_text: str, version_number: int,
                   description: str = "", author: str = "Unknown"):
        """Add new document version."""
        version = {
            'version': version_number,
            'text': document_text,
            'description': description,
            'author': author,
            'timestamp': datetime.now(),
            'hash': hash(document_text)
        }
        self.versions.append(version)

    def compare_versions(self, version1: int, version2: int) -> DocumentComparator:
        """Compare two versions."""
        doc1 = None
        doc2 = None

        for v in self.versions:
            if v['version'] == version1:
                doc1 = v['text']
            if v['version'] == version2:
                doc2 = v['text']

        if not doc1 or not doc2:
            raise ValueError("Version not found")

        return DocumentComparator(
            doc1, doc2,
            f"Version {version1}",
            f"Version {version2}"
        )

    def get_version_history(self) -> str:
        """Get version history."""
        history = "VERSION HISTORY\n"
        history += "=" * 60 + "\n\n"

        for v in sorted(self.versions, key=lambda x: x['version']):
            history += f"Version {v['version']}: {v['description']}\n"
            history += f"  Author: {v['author']}\n"
            history += f"  Date: {v['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            history += f"  Size: {len(v['text'])} characters\n\n"

        return history


def example_compare_contracts():
    """Example: Compare two versions of a contract."""

    contract_v1 = """
SERVICE AGREEMENT

This Agreement is entered into between Client and Provider.

1. SERVICES
Provider agrees to provide the following services:
- Legal consultation
- Document drafting
- Research

2. FEES
Hourly Rate: $250/hour
Payment Terms: Due within 30 days

3. TERM
Duration: 1 year
Termination: 30 days notice
"""

    contract_v2 = """
SERVICE AGREEMENT

This Agreement is entered into between Client LLC and Professional Services Inc.

1. SERVICES
Provider agrees to provide the following services:
- Legal consultation
- Document drafting
- Research
- Compliance consulting

2. FEES
Hourly Rate: $300/hour
Monthly Retainer: $5,000
Payment Terms: Due within 15 days

3. TERM
Duration: 2 years
Termination: 60 days notice

4. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality.
"""

    comparator = DocumentComparator(contract_v1, contract_v2, "Contract v1.0", "Contract v1.1")
    changes = comparator.compare()

    print("CONTRACT COMPARISON")
    print(comparator.get_change_report())
    print(comparator.get_side_by_side_comparison())

    with open('/tmp/contract_redline.txt', 'w') as f:
        f.write(comparator.get_redline_version())

    return comparator


def example_version_tracking():
    """Example: Track multiple document versions."""

    vc = VersionControl()

    v1 = "Initial contract draft"
    v2 = "Initial contract draft with added confidentiality clause"
    v3 = "Initial contract draft with added confidentiality clause and updated fees"

    vc.add_version(v1, 1, "Initial draft", "John Lawyer")
    vc.add_version(v2, 2, "Added confidentiality", "Jane Legal")
    vc.add_version(v3, 3, "Updated fees", "John Lawyer")

    print("\n" + vc.get_version_history())

    # Compare versions
    comparator = vc.compare_versions(1, 3)
    print("VERSION 1 to 3 COMPARISON:")
    print(comparator.get_change_report())

    return vc


if __name__ == "__main__":
    example_compare_contracts()
    example_version_tracking()
    print("\nDocument comparison examples completed!")
