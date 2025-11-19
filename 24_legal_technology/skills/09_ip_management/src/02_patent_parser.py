"""
Patent Parser for extracting and parsing patent document information
Handles USPTO XML, PDF, and JSON formats
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from xml.etree import ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


class PatentFormat(Enum):
    """Supported patent document formats"""
    XML = "xml"
    JSON = "json"
    TEXT = "text"
    PDF = "pdf"


@dataclass
class PatentClaim:
    """Patent claim structure"""
    claim_number: int
    claim_type: str  # independent or dependent
    text: str
    depends_on: Optional[int] = None
    antecedent_basis: List[str] = None

    def __post_init__(self):
        if self.antecedent_basis is None:
            self.antecedent_basis = []


@dataclass
class PatentInventor:
    """Patent inventor information"""
    name: str
    city: str
    state: str
    country: str
    sequence: int


@dataclass
class PatentApplication:
    """Patent application details"""
    application_number: str
    filing_date: datetime
    publication_number: Optional[str] = None
    publication_date: Optional[datetime] = None
    issue_date: Optional[datetime] = None
    patent_number: Optional[str] = None


@dataclass
class PatentDocument:
    """Complete patent document structure"""
    patent_number: str
    application: PatentApplication
    title: str
    abstract: str
    claims: List[PatentClaim]
    inventors: List[PatentInventor]
    assignee: Optional[str]
    assignee_country: Optional[str]
    filing_date: datetime
    ipc_class: List[str]
    cpc_class: List[str]
    uspc_class: List[str]
    references_cited: List[Dict[str, Any]]
    drawings: List[str]
    description: Optional[str] = None


class PatentParser:
    """Main patent parser class"""

    def __init__(self):
        """Initialize patent parser"""
        self.claim_pattern = re.compile(
            r'(?:Claim\s+)?(\d+)\.\s*(A method|A system|The .*?:|[A-Z].*?)[\n\r]+(.*?)(?=(?:Claim|Description|\Z))',
            re.IGNORECASE | re.DOTALL
        )
        self.depends_pattern = re.compile(r'The claim of claim (\d+)', re.IGNORECASE)
        self.indentation_pattern = re.compile(r'^(\s+)', re.MULTILINE)

    def parse_patent(self, content: str, format_type: PatentFormat) -> Optional[PatentDocument]:
        """
        Parse patent document in specified format

        Args:
            content: Patent document content
            format_type: Format of the patent document

        Returns:
            PatentDocument object or None if parsing fails
        """
        try:
            if format_type == PatentFormat.XML:
                return self._parse_xml(content)
            elif format_type == PatentFormat.JSON:
                return self._parse_json(content)
            elif format_type == PatentFormat.TEXT:
                return self._parse_text(content)
            else:
                logger.error(f"Unsupported format: {format_type}")
                return None
        except Exception as e:
            logger.error(f"Error parsing patent: {e}")
            return None

    def _parse_xml(self, xml_content: str) -> Optional[PatentDocument]:
        """Parse USPTO XML patent format"""
        try:
            root = ET.fromstring(xml_content)

            # Extract patent metadata
            patent_number = self._extract_xml_text(root, ".//patent-number")
            application_number = self._extract_xml_text(root, ".//application-number")
            title = self._extract_xml_text(root, ".//title")
            abstract = self._extract_xml_text(root, ".//abstract")

            # Extract dates
            filing_date = self._parse_date(
                self._extract_xml_text(root, ".//filing-date")
            )
            issue_date = self._parse_date(
                self._extract_xml_text(root, ".//issue-date")
            )

            # Extract inventors
            inventors = self._parse_inventors_xml(root)

            # Extract claims
            claims = self._parse_claims_xml(root)

            # Extract classifications
            ipc_class = self._extract_xml_list(root, ".//ipc-class")
            cpc_class = self._extract_xml_list(root, ".//cpc-class")
            uspc_class = self._extract_xml_list(root, ".//uspc-class")

            # Extract citations
            references = self._parse_references_xml(root)

            # Create patent document
            application = PatentApplication(
                application_number=application_number or "",
                filing_date=filing_date or datetime.now(),
                patent_number=patent_number
            )

            return PatentDocument(
                patent_number=patent_number or "",
                application=application,
                title=title or "",
                abstract=abstract or "",
                claims=claims,
                inventors=inventors,
                assignee=self._extract_xml_text(root, ".//assignee"),
                assignee_country=self._extract_xml_text(root, ".//assignee-country"),
                filing_date=filing_date or datetime.now(),
                ipc_class=ipc_class,
                cpc_class=cpc_class,
                uspc_class=uspc_class,
                references_cited=references,
                drawings=self._extract_xml_list(root, ".//drawing-reference-number"),
                description=self._extract_xml_text(root, ".//description")
            )

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return None

    def _parse_json(self, json_content: str) -> Optional[PatentDocument]:
        """Parse patent in JSON format"""
        try:
            data = json.loads(json_content)

            # Extract basic information
            patent_number = data.get("patentNumber", "")
            application_number = data.get("applicationNumber", "")
            title = data.get("title", "")
            abstract = data.get("abstract", "")

            # Parse dates
            filing_date = self._parse_date(data.get("filingDate"))
            issue_date = self._parse_date(data.get("issueDate"))

            # Parse inventors
            inventors = [
                PatentInventor(
                    name=inv.get("name", ""),
                    city=inv.get("city", ""),
                    state=inv.get("state", ""),
                    country=inv.get("country", ""),
                    sequence=inv.get("sequence", 0)
                )
                for inv in data.get("inventors", [])
            ]

            # Parse claims
            claims = [
                PatentClaim(
                    claim_number=claim.get("claimNumber", 0),
                    claim_type=claim.get("claimType", "independent"),
                    text=claim.get("text", ""),
                    depends_on=claim.get("dependsOn"),
                )
                for claim in data.get("claims", [])
            ]

            # Create application
            application = PatentApplication(
                application_number=application_number,
                filing_date=filing_date or datetime.now(),
                patent_number=patent_number,
                issue_date=issue_date
            )

            return PatentDocument(
                patent_number=patent_number,
                application=application,
                title=title,
                abstract=abstract,
                claims=claims,
                inventors=inventors,
                assignee=data.get("assignee"),
                assignee_country=data.get("assigneeCountry"),
                filing_date=filing_date or datetime.now(),
                ipc_class=data.get("ipcClass", []),
                cpc_class=data.get("cpcClass", []),
                uspc_class=data.get("uspcClass", []),
                references_cited=data.get("references", []),
                drawings=data.get("drawings", []),
                description=data.get("description")
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None

    def _parse_text(self, text_content: str) -> Optional[PatentDocument]:
        """Parse patent in plain text format"""
        try:
            # Extract patent number
            patent_match = re.search(r'Patent.*?(\d{7,})', text_content)
            patent_number = patent_match.group(1) if patent_match else ""

            # Extract title
            title_match = re.search(r'Title:?\s*(.+?)[\n\r]', text_content, re.IGNORECASE)
            title = title_match.group(1) if title_match else ""

            # Extract abstract
            abstract_match = re.search(
                r'Abstract:?\s*(.+?)(?=Claims:|Description:|\Z)',
                text_content,
                re.IGNORECASE | re.DOTALL
            )
            abstract = abstract_match.group(1).strip() if abstract_match else ""

            # Parse claims
            claims = self._parse_claims_text(text_content)

            # Parse dates
            filing_date = self._extract_date(text_content, r'Filing Date:?\s*(\d{1,2}/\d{1,2}/\d{4})')
            issue_date = self._extract_date(text_content, r'Issue Date:?\s*(\d{1,2}/\d{1,2}/\d{4})')

            # Parse inventors
            inventors = self._parse_inventors_text(text_content)

            application = PatentApplication(
                application_number="",
                filing_date=filing_date or datetime.now(),
                patent_number=patent_number,
                issue_date=issue_date
            )

            return PatentDocument(
                patent_number=patent_number,
                application=application,
                title=title,
                abstract=abstract,
                claims=claims,
                inventors=inventors,
                assignee="",
                assignee_country="",
                filing_date=filing_date or datetime.now(),
                ipc_class=[],
                cpc_class=[],
                uspc_class=[],
                references_cited=[],
                drawings=[]
            )

        except Exception as e:
            logger.error(f"Text parsing error: {e}")
            return None

    def _parse_claims_text(self, text: str) -> List[PatentClaim]:
        """Extract claims from text format"""
        claims = []
        claim_matches = re.finditer(
            r'(\d+)\.\s*(A|The|An|Said)\s+(.+?)(?=\n\d+\.|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )

        for idx, match in enumerate(claim_matches, 1):
            claim_num = int(match.group(1))
            claim_text = match.group(0).strip()

            # Determine if dependent claim
            depends_match = self.depends_pattern.search(claim_text)
            depends_on = int(depends_match.group(1)) if depends_match else None
            claim_type = "dependent" if depends_on else "independent"

            claims.append(PatentClaim(
                claim_number=claim_num,
                claim_type=claim_type,
                text=claim_text,
                depends_on=depends_on
            ))

        return claims

    def _parse_claims_xml(self, root: ET.Element) -> List[PatentClaim]:
        """Extract claims from XML"""
        claims = []

        for claim_elem in root.findall(".//claim"):
            claim_num = int(claim_elem.get("id", "0"))
            claim_type = claim_elem.get("type", "independent")
            claim_text = self._extract_xml_text(claim_elem, "claim-text")
            depends_on_str = claim_elem.get("depends-on")
            depends_on = int(depends_on_str) if depends_on_str else None

            claims.append(PatentClaim(
                claim_number=claim_num,
                claim_type=claim_type,
                text=claim_text or "",
                depends_on=depends_on
            ))

        return claims

    def _parse_inventors_text(self, text: str) -> List[PatentInventor]:
        """Extract inventors from text"""
        inventors = []
        inventor_section = re.search(
            r'Inventors?:?\s*(.+?)(?=Assignee:|References:|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if inventor_section:
            inventor_text = inventor_section.group(1)
            # Split by semicolon or newline
            names = re.split(r'[;\n]', inventor_text)

            for idx, name in enumerate(names, 1):
                if name.strip():
                    inventors.append(PatentInventor(
                        name=name.strip(),
                        city="",
                        state="",
                        country="",
                        sequence=idx
                    ))

        return inventors

    def _parse_inventors_xml(self, root: ET.Element) -> List[PatentInventor]:
        """Extract inventors from XML"""
        inventors = []

        for idx, inv_elem in enumerate(root.findall(".//inventor"), 1):
            name = self._extract_xml_text(inv_elem, "name")
            city = self._extract_xml_text(inv_elem, "city")
            state = self._extract_xml_text(inv_elem, "state")
            country = self._extract_xml_text(inv_elem, "country")

            if name:
                inventors.append(PatentInventor(
                    name=name,
                    city=city or "",
                    state=state or "",
                    country=country or "",
                    sequence=idx
                ))

        return inventors

    def _parse_references_xml(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract cited references from XML"""
        references = []

        for ref_elem in root.findall(".//citation"):
            citation_data = {
                "type": ref_elem.get("type", ""),
                "number": self._extract_xml_text(ref_elem, "patent-number"),
                "date": self._extract_xml_text(ref_elem, "date"),
                "inventor": self._extract_xml_text(ref_elem, "inventor"),
                "title": self._extract_xml_text(ref_elem, "title"),
            }
            references.append(citation_data)

        return references

    def _extract_xml_text(self, element: ET.Element, path: str) -> Optional[str]:
        """Extract text from XML element by path"""
        found = element.find(path)
        return found.text if found is not None else None

    def _extract_xml_list(self, element: ET.Element, path: str) -> List[str]:
        """Extract list of text values from XML"""
        result = []
        for elem in element.findall(path):
            if elem.text:
                result.append(elem.text)
        return result

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string"""
        if not date_str:
            return None

        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y%m%d",
            "%B %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _extract_date(self, text: str, pattern: str) -> Optional[datetime]:
        """Extract and parse date from text"""
        match = re.search(pattern, text)
        if match:
            return self._parse_date(match.group(1))
        return None

    def to_dict(self, patent: PatentDocument) -> Dict[str, Any]:
        """Convert PatentDocument to dictionary"""
        return asdict(patent)

    def to_json(self, patent: PatentDocument) -> str:
        """Convert PatentDocument to JSON string"""
        return json.dumps(self.to_dict(patent), default=str)


def main():
    """Example usage"""
    parser = PatentParser()

    # Example XML parsing
    sample_xml = """
    <patent>
        <patent-number>10000000</patent-number>
        <title>Example Patent</title>
        <abstract>This is an example</abstract>
        <filing-date>2020-01-15</filing-date>
        <inventor>
            <name>John Doe</name>
            <city>San Francisco</city>
            <state>CA</state>
            <country>US</country>
        </inventor>
        <claim id="1" type="independent">
            <claim-text>A method comprising...</claim-text>
        </claim>
    </patent>
    """

    patent = parser.parse_patent(sample_xml, PatentFormat.XML)
    if patent:
        print(f"Parsed patent: {patent.title}")
        print(f"Patent number: {patent.patent_number}")
        print(f"Claims: {len(patent.claims)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
