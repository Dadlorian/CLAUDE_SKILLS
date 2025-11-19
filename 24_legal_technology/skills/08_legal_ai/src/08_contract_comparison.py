"""
Contract Comparison and Redlining
Compare contract versions and generate redlines
"""

from difflib import SequenceMatcher, unified_diff
from typing import List, Tuple

class ContractComparator:
    """Compare and redline contracts"""

    def __init__(self):
        pass

    def compare_contracts(self, original: str, revised: str) -> List[Dict]:
        """Compare two contract versions"""

        # Split into lines
        original_lines = original.splitlines()
        revised_lines = revised.splitlines()

        # Use SequenceMatcher
        matcher = SequenceMatcher(None, original_lines, revised_lines)

        changes = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    "type": "modified",
                    "original_lines": original_lines[i1:i2],
                    "revised_lines": revised_lines[j1:j2],
                    "line_number": i1
                })
            elif tag == 'delete':
                changes.append({
                    "type": "deleted",
                    "original_lines": original_lines[i1:i2],
                    "line_number": i1
                })
            elif tag == 'insert':
                changes.append({
                    "type": "added",
                    "revised_lines": revised_lines[j1:j2],
                    "line_number": i1
                })

        return changes

    def generate_redline(self, original: str, revised: str) -> str:
        """Generate redline markup"""

        diff = list(unified_diff(
            original.splitlines(),
            revised.splitlines(),
            lineterm=''
        ))

        redline = []
        for line in diff:
            if line.startswith('-'):
                redline.append(f"[DELETED: {line[1:]}]")
            elif line.startswith('+'):
                redline.append(f"[ADDED: {line[1:]}]")
            elif not line.startswith('@@') and not line.startswith('---') and not line.startswith('+++'):
                redline.append(line)

        return '\n'.join(redline)

    def count_material_changes(self, changes: List[Dict]) -> int:
        """Count material changes (non-formatting)"""

        material_keywords = [
            'liability', 'indemnif', 'payment', 'termination',
            'price', 'deadline', 'warranty', 'obligation'
        ]

        material_count = 0

        for change in changes:
            text = ' '.join(change.get('original_lines', []) + change.get('revised_lines', []))
            if any(keyword in text.lower() for keyword in material_keywords):
                material_count += 1

        return material_count
