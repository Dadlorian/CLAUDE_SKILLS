"""
Patent Family Analyzer Example
Analyzes relationships between related patent applications and grants
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum

class FamilyRelationType(Enum):
    """Types of relationships in a patent family"""
    PRIORITY = "priority"  # Claim priority to another application
    CONTINUATION = "continuation"  # Continuation application
    CONTINUATION_IN_PART = "cip"  # Continuation-in-part
    DIVISIONAL = "divisional"  # Divisional application
    REISSUE = "reissue"  # Reissue of granted patent

@dataclass
class PatentApplication:
    """Represents a patent application/grant"""
    number: str
    country_code: str  # US, EP, CN, JP, etc.
    filing_date: str
    publication_date: Optional[str]
    issue_date: Optional[str]
    status: str  # pending, published, granted, abandoned
    title: str

@dataclass
class FamilyRelationship:
    """Represents relationship between two patents"""
    parent_number: str
    child_number: str
    relationship_type: FamilyRelationType

class PatentFamilyAnalyzer:
    """Analyze patent families and relationships"""

    def __init__(self):
        self.patents: Dict[str, PatentApplication] = {}
        self.relationships: List[FamilyRelationship] = []
        self.family_roots: Dict[str, str] = {}  # Maps patent to root family member

    def add_patent(self, app: PatentApplication):
        """Add a patent to the family"""
        self.patents[app.number] = app

    def add_relationship(self, parent_number: str, child_number: str,
                        rel_type: FamilyRelationType):
        """Add a relationship between patents"""
        self.relationships.append(FamilyRelationship(
            parent_number=parent_number,
            child_number=child_number,
            relationship_type=rel_type
        ))

    def get_patent_family(self, patent_number: str) -> Dict:
        """Get all members of a patent family"""
        # Find root patent
        root = self._find_root(patent_number)

        # Get all descendants from root
        family = self._get_all_descendants(root)
        family.add(root)

        # Get all ancestors
        ancestors = self._get_all_ancestors(patent_number)
        family.update(ancestors)

        return {
            'root_patent': root,
            'family_members': sorted(list(family)),
            'total_members': len(family),
            'patents': {num: self.patents[num] for num in family if num in self.patents}
        }

    def _find_root(self, patent_number: str) -> str:
        """Find the root patent in a family (usually earliest priority)"""
        current = patent_number

        while True:
            # Find parent relationship
            parent = None
            for rel in self.relationships:
                if rel.child_number == current:
                    parent = rel.parent_number
                    break

            if parent is None:
                return current  # This is the root

            current = parent

    def _get_all_descendants(self, patent_number: str) -> Set[str]:
        """Get all patents derived from this patent"""
        descendants = set()

        # Find direct children
        children = [rel.child_number for rel in self.relationships
                   if rel.parent_number == patent_number]

        for child in children:
            descendants.add(child)
            # Recursively get grandchildren
            descendants.update(self._get_all_descendants(child))

        return descendants

    def _get_all_ancestors(self, patent_number: str) -> Set[str]:
        """Get all patents this one depends on"""
        ancestors = set()
        current = patent_number

        while True:
            # Find parent
            parent = None
            for rel in self.relationships:
                if rel.child_number == current:
                    parent = rel.parent_number
                    break

            if parent is None:
                break

            ancestors.add(parent)
            current = parent

        return ancestors

    def get_priority_chain(self, patent_number: str) -> List[str]:
        """Get priority chain from earliest filing to patent"""
        chain = [patent_number]

        # Walk back to root following priority relationships
        current = patent_number
        while True:
            parent = None
            for rel in self.relationships:
                if rel.child_number == current and rel.relationship_type == FamilyRelationType.PRIORITY:
                    parent = rel.parent_number
                    break

            if parent is None:
                break

            chain.insert(0, parent)
            current = parent

        return chain

    def analyze_family_strategy(self, patent_number: str) -> Dict:
        """Analyze the patent family strategy"""
        family = self.get_patent_family(patent_number)
        members = family['family_members']

        # Analyze by type
        by_status = {}
        by_country = {}

        for member in members:
            if member in self.patents:
                patent = self.patents[member]
                # Count by status
                by_status[patent.status] = by_status.get(patent.status, 0) + 1
                # Count by country
                by_country[patent.country_code] = by_country.get(patent.country_code, 0) + 1

        return {
            'total_family_members': len(members),
            'by_status': by_status,
            'by_country': by_country,
            'granted_patents': len([m for m in members if self.patents.get(m, {}).status == 'granted']),
            'pending_applications': len([m for m in members if self.patents.get(m, {}).status == 'pending'])
        }

    def find_continuation_opportunities(self, patent_number: str) -> List[str]:
        """
        Identify potential continuation opportunities
        Returns patents that could support continuation filings
        """
        opportunities = []

        # Find issued patents with pending-type relationships available
        if patent_number in self.patents:
            patent = self.patents[patent_number]
            if patent.status == 'granted' and patent.issue_date:
                # Can file continuation within 1 year of issue typically
                opportunities.append(patent_number)

        return opportunities

    def get_geographic_coverage(self, patent_number: str) -> Dict[str, str]:
        """Get geographic coverage of the family"""
        family = self.get_patent_family(patent_number)
        coverage = {}

        for member in family['family_members']:
            if member in self.patents:
                patent = self.patents[member]
                coverage[patent.country_code] = member

        return coverage

    def estimate_family_cost(self, patent_number: str) -> Dict:
        """Estimate total family cost"""
        family = self.get_patent_family(patent_number)

        # Simplified cost estimates (actual costs vary significantly)
        country_costs = {
            'US': 3000,
            'EP': 5000,
            'CN': 2000,
            'JP': 4000,
            'GB': 1500,
            'DE': 1500,
        }

        total_cost = 0
        cost_by_country = {}

        for member in family['family_members']:
            if member in self.patents:
                patent = self.patents[member]
                cost = country_costs.get(patent.country_code, 2000)
                cost_by_country[patent.country_code] = cost_by_country.get(patent.country_code, 0) + cost
                total_cost += cost

        return {
            'total_estimated_cost': total_cost,
            'cost_by_country': cost_by_country,
            'average_cost_per_member': total_cost / len(family['family_members']) if family['family_members'] else 0
        }


# Example usage
if __name__ == "__main__":
    analyzer = PatentFamilyAnalyzer()

    # Add patents
    analyzer.add_patent(PatentApplication(
        "US10000001", "US", "2015-01-01", "2015-07-01", "2017-01-01", "granted",
        "Core Patent"))

    analyzer.add_patent(PatentApplication(
        "US10000002", "US", "2016-01-01", "2016-07-01", "2018-01-01", "granted",
        "Continuation"))

    analyzer.add_patent(PatentApplication(
        "EP3000001", "EP", "2015-01-01", "2016-07-01", "2018-01-01", "granted",
        "European Patent"))

    # Add relationships
    analyzer.add_relationship("US10000001", "US10000002", FamilyRelationType.CONTINUATION)
    analyzer.add_relationship("US10000001", "EP3000001", FamilyRelationType.PRIORITY)

    # Analyze family
    family = analyzer.get_patent_family("US10000002")
    print(f"Family size: {family['total_members']}")
    print(f"Members: {family['family_members']}")

    # Analyze strategy
    strategy = analyzer.analyze_family_strategy("US10000001")
    print(f"Strategy: {strategy}")
