"""
Patent XML Parser Example
Parses USPTO patent XML documents
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PatentClaim:
    """Represents a single patent claim"""
    claim_number: int
    claim_type: str  # independent or dependent
    claim_text: str
    dependent_on: Optional[int] = None

@dataclass
class Patent:
    """Represents parsed patent data"""
    application_number: str
    patent_number: str
    title: str
    abstract: str
    filing_date: str
    issue_date: str
    inventors: List[str]
    assignees: List[str]
    claims: List[PatentClaim]
    cpc_classifications: List[str]
    ipc_classifications: List[str]

class PatentXMLParser:
    """Parse USPTO patent XML files"""

    @staticmethod
    def parse_patent_xml(xml_file_path: str) -> Patent:
        """
        Parse a patent XML file

        Args:
            xml_file_path: Path to XML file

        Returns:
            Patent object with extracted data
        """
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Extract basic information
        app_number = PatentXMLParser._extract_text(root, './/application-reference/document-id/doc-number')
        patent_number = PatentXMLParser._extract_text(root, './/publication-reference/document-id/doc-number')
        title = PatentXMLParser._extract_text(root, './/invention-title')
        abstract = PatentXMLParser._extract_text(root, './/abstract/paragraph')
        filing_date = PatentXMLParser._extract_text(root, './/application-reference/document-id/date')
        issue_date = PatentXMLParser._extract_text(root, './/publication-reference/document-id/date')

        # Extract inventors
        inventors = PatentXMLParser._extract_inventors(root)

        # Extract assignees
        assignees = PatentXMLParser._extract_assignees(root)

        # Extract claims
        claims = PatentXMLParser._extract_claims(root)

        # Extract classifications
        cpc_classifications = PatentXMLParser._extract_cpc_classifications(root)
        ipc_classifications = PatentXMLParser._extract_ipc_classifications(root)

        return Patent(
            application_number=app_number,
            patent_number=patent_number,
            title=title,
            abstract=abstract,
            filing_date=filing_date,
            issue_date=issue_date,
            inventors=inventors,
            assignees=assignees,
            claims=claims,
            cpc_classifications=cpc_classifications,
            ipc_classifications=ipc_classifications
        )

    @staticmethod
    def _extract_text(element, xpath: str) -> str:
        """Extract text from element using XPath"""
        found = element.find(xpath)
        return found.text if found is not None else ""

    @staticmethod
    def _extract_inventors(root) -> List[str]:
        """Extract inventor names"""
        inventors = []
        for inventor in root.findall('.//inventors/inventor'):
            name = inventor.find('.//inventor-name/name')
            if name is not None:
                inventors.append(name.text)
        return inventors

    @staticmethod
    def _extract_assignees(root) -> List[str]:
        """Extract assignee names"""
        assignees = []
        for assignee in root.findall('.//assignees/assignee'):
            name = assignee.find('.//assignee-name')
            if name is not None:
                assignees.append(name.text)
        return assignees

    @staticmethod
    def _extract_claims(root) -> List[PatentClaim]:
        """Extract patent claims"""
        claims = []
        for claim_elem in root.findall('.//claims/claim'):
            claim_num = int(claim_elem.get('num', 0))
            claim_type = claim_elem.get('type', 'independent')
            claim_text = ''.join(claim_elem.itertext()).strip()

            # Check for dependency
            dependent = claim_elem.find('.//claim-ref')
            dependent_on = None
            if dependent is not None:
                dependent_on = int(dependent.get('idref', 0))

            claims.append(PatentClaim(
                claim_number=claim_num,
                claim_type=claim_type,
                claim_text=claim_text,
                dependent_on=dependent_on
            ))

        return claims

    @staticmethod
    def _extract_cpc_classifications(root) -> List[str]:
        """Extract CPC classifications"""
        cpc_codes = []
        for cpc in root.findall('.//classification-cpc'):
            code = cpc.find('.//cpc-text')
            if code is not None:
                cpc_codes.append(code.text)
        return cpc_codes

    @staticmethod
    def _extract_ipc_classifications(root) -> List[str]:
        """Extract IPC classifications"""
        ipc_codes = []
        for ipc in root.findall('.//classification-ipc'):
            code = ipc.find('.//ipc-text')
            if code is not None:
                ipc_codes.append(code.text)
        return ipc_codes


# Example usage
if __name__ == "__main__":
    parser = PatentXMLParser()

    # Parse a patent file
    patent = parser.parse_patent_xml("/path/to/patent.xml")

    print(f"Patent Number: {patent.patent_number}")
    print(f"Title: {patent.title}")
    print(f"Inventors: {', '.join(patent.inventors)}")
    print(f"Assignees: {', '.join(patent.assignees)}")
    print(f"Number of claims: {len(patent.claims)}")
    print(f"CPC Classifications: {', '.join(patent.cpc_classifications)}")
