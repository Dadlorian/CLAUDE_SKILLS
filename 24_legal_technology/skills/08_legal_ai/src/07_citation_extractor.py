"""
Legal Citation Extraction
Extract and validate legal citations from documents
"""

import re
from typing import List, Dict

class LegalCitationExtractor:
    """Extract legal citations from text"""

    def __init__(self):
        # Citation patterns
        self.patterns = {
            "us_supreme_court": r'\d+\s+U\.S\.\s+\d+',
            "federal_reporter": r'\d+\s+F\.\d+[d]?\s+\d+',
            "supreme_court_reporter": r'\d+\s+S\.Ct\.\s+\d+',
            "federal_supplement": r'\d+\s+F\.\s*Supp\.\d+[d]?\s+\d+',
            "state_reporter": r'\d+\s+[A-Z][A-Za-z\.]+\d+[d]?\s+\d+',
            "usc": r'\d+\s+U\.S\.C\.\s+§?\s*\d+'
        }

    def extract_citations(self, text: str) -> List[Dict]:
        """Extract all legal citations from text"""

        citations = []

        for citation_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    "citation": match.group(),
                    "type": citation_type,
                    "start": match.start(),
                    "end": match.end()
                })

        return citations

    def format_bluebook(self, citation: str) -> str:
        """Format citation in Bluebook style"""

        # Basic formatting
        citation = re.sub(r'\s+', ' ', citation)
        return citation.strip()
