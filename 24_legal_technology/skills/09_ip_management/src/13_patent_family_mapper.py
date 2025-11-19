"""
Patent Family Mapper Example
Maps patent family relationships and analyzes portfolio structure
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque


@dataclass
class PatentFamily:
    """Patent family structure"""
    family_id: str
    parent_patent_id: str
    related_patents: List[str] = field(default_factory=list)
    jurisdictions: Set[str] = field(default_factory=set)
    filing_dates: Dict[str, datetime] = field(default_factory=dict)
    first_filing_date: Optional[datetime] = None
    priority_claims: Dict[str, str] = field(default_factory=dict)
    total_members: int = 0


@dataclass
class PatentNode:
    """Individual patent in family"""
    patent_id: str
    jurisdiction: str
    application_number: str
    filing_date: datetime
    publication_date: Optional[datetime]
    grant_date: Optional[datetime]
    status: str
    assignee: str
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)


class PatentFamilyMapper:
    """Maps and analyzes patent family relationships"""

    def __init__(self):
        self.patent_nodes: Dict[str, PatentNode] = {}
        self.families: Dict[str, PatentFamily] = {}
        self.family_map = defaultdict(list)  # patent_id -> family_ids

    def add_patent(self, patent: PatentNode):
        """Add patent to the mapper"""
        self.patent_nodes[patent.patent_id] = patent

    def build_family(self, parent_id: str, related_ids: List[str]):
        """
        Build a patent family relationship

        Args:
            parent_id: Primary patent ID
            related_ids: List of related patent IDs
        """
        family_id = f"FAMILY_{parent_id}"

        if parent_id in self.patent_nodes:
            parent = self.patent_nodes[parent_id]
            first_filing = parent.filing_date

            family = PatentFamily(
                family_id=family_id,
                parent_patent_id=parent_id,
                first_filing_date=first_filing
            )

            all_members = [parent_id] + related_ids

            for patent_id in all_members:
                if patent_id in self.patent_nodes:
                    node = self.patent_nodes[patent_id]
                    family.related_patents.append(patent_id)
                    family.jurisdictions.add(node.jurisdiction)
                    family.filing_dates[patent_id] = node.filing_date
                    family.total_members += 1
                    self.family_map[patent_id].append(family_id)

                    # Update parent-child relationships
                    if patent_id != parent_id and parent_id in self.patent_nodes:
                        self.patent_nodes[patent_id].parent_id = parent_id
                        self.patent_nodes[parent_id].children_ids.append(patent_id)

            self.families[family_id] = family

    def analyze_family_structure(self, family_id: str) -> Dict:
        """
        Analyze structure of a patent family

        Returns:
            Dictionary with family structure metrics
        """
        if family_id not in self.families:
            return {}

        family = self.families[family_id]

        # Analyze maturity
        jurisdictions_count = len(family.jurisdictions)
        filing_timeline = sorted(family.filing_dates.values())

        # Calculate family span
        if filing_timeline:
            family_span = (filing_timeline[-1] - filing_timeline[0]).days

        granted_count = sum(
            1 for pid in family.related_patents
            if self.patent_nodes[pid].status.lower() == 'granted'
        )

        pending_count = family.total_members - granted_count

        return {
            'family_id': family_id,
            'parent_patent': family.parent_patent_id,
            'total_members': family.total_members,
            'jurisdictions': list(family.jurisdictions),
            'jurisdiction_count': jurisdictions_count,
            'granted_patents': granted_count,
            'pending_patents': pending_count,
            'grant_rate': granted_count / family.total_members if family.total_members > 0 else 0,
            'family_age_days': (datetime.now() - family.first_filing_date).days if family.first_filing_date else 0,
            'filing_span_days': family_span,
            'filing_timeline': [d.isoformat() for d in filing_timeline]
        }

    def calculate_family_value_indicator(self, family_id: str) -> float:
        """
        Calculate value indicator for patent family

        Args:
            family_id: Family ID

        Returns:
            Value score (0-100)
        """
        if family_id not in self.families:
            return 0

        family = self.families[family_id]
        score = 0

        # Size component (up to 30 points)
        size_bonus = min(family.total_members * 3, 30)
        score += size_bonus

        # Geographic coverage component (up to 25 points)
        jurisdictions_bonus = min(len(family.jurisdictions) * 5, 25)
        score += jurisdictions_bonus

        # Grant rate component (up to 25 points)
        grant_rate = sum(
            1 for pid in family.related_patents
            if self.patent_nodes[pid].status.lower() == 'granted'
        ) / family.total_members if family.total_members > 0 else 0
        grant_bonus = grant_rate * 25
        score += grant_bonus

        # Age component (up to 20 points)
        family_age = (datetime.now() - family.first_filing_date).days / 365
        age_bonus = min(family_age * 2, 20)
        score += age_bonus

        return min(score, 100)

    def identify_prosecution_gaps(self) -> List[Dict]:
        """
        Identify prosecution gaps in families

        Returns:
            List of families with potential prosecution issues
        """
        gaps = []

        for family_id, family in self.families.items():
            # Check for abandoned applications
            abandoned = [
                pid for pid in family.related_patents
                if self.patent_nodes[pid].status.lower() == 'abandoned'
            ]

            # Check for long prosecution times
            slow_prosecutions = []
            for pid in family.related_patents:
                node = self.patent_nodes[pid]
                if node.grant_date:
                    prosecution_time = (node.grant_date - node.filing_date).days
                    if prosecution_time > 1825:  # 5 years
                        slow_prosecutions.append({
                            'patent_id': pid,
                            'jurisdiction': node.jurisdiction,
                            'prosecution_days': prosecution_time
                        })

            if abandoned or slow_prosecutions:
                gaps.append({
                    'family_id': family_id,
                    'abandoned_count': len(abandoned),
                    'slow_prosecutions': slow_prosecutions,
                    'action_recommended': len(abandoned) > 0 or len(slow_prosecutions) > 2
                })

        return gaps

    def map_family_genealogy(self, family_id: str) -> Dict:
        """
        Generate genealogy map for family showing relationships

        Args:
            family_id: Family ID

        Returns:
            Dictionary with genealogy structure
        """
        if family_id not in self.families:
            return {}

        family = self.families[family_id]
        genealogy = {
            'root': family.parent_patent_id,
            'tree': self._build_tree(family.parent_patent_id),
            'all_patents': []
        }

        for pid in family.related_patents:
            node = self.patent_nodes[pid]
            genealogy['all_patents'].append({
                'patent_id': pid,
                'jurisdiction': node.jurisdiction,
                'status': node.status,
                'filing_date': node.filing_date.isoformat(),
                'parent_id': node.parent_id,
                'children_count': len(node.children_ids)
            })

        return genealogy

    def _build_tree(self, root_id: str, visited: Set[str] = None) -> Dict:
        """Build tree structure starting from root"""
        if visited is None:
            visited = set()

        if root_id in visited or root_id not in self.patent_nodes:
            return {}

        visited.add(root_id)
        node = self.patent_nodes[root_id]

        tree = {
            'id': root_id,
            'jurisdiction': node.jurisdiction,
            'status': node.status,
            'children': []
        }

        for child_id in node.children_ids:
            if child_id not in visited:
                tree['children'].append(self._build_tree(child_id, visited))

        return tree

    def generate_family_portfolio_summary(self) -> Dict:
        """
        Generate summary of all patent families in portfolio

        Returns:
            Portfolio-level summary
        """
        family_analyses = {}
        total_patents = 0
        total_value = 0
        jurisdictions_set = set()

        for family_id in self.families:
            analysis = self.analyze_family_structure(family_id)
            value = self.calculate_family_value_indicator(family_id)
            family_analyses[family_id] = {
                'structure': analysis,
                'value_score': value
            }
            total_patents += analysis['total_members']
            total_value += value
            jurisdictions_set.update(analysis['jurisdictions'])

        avg_value = total_value / len(self.families) if self.families else 0

        return {
            'total_families': len(self.families),
            'total_patents': total_patents,
            'avg_family_size': total_patents / len(self.families) if self.families else 0,
            'unique_jurisdictions': list(jurisdictions_set),
            'avg_family_value_score': avg_value,
            'prosecution_gaps': self.identify_prosecution_gaps(),
            'families': family_analyses
        }


# Example usage
if __name__ == "__main__":
    mapper = PatentFamilyMapper()

    # Add sample patents
    for i in range(15):
        node = PatentNode(
            patent_id=f"US{7000000 + i}",
            jurisdiction="US" if i < 5 else "EP" if i < 10 else "JP",
            application_number=f"APP{1000000 + i}",
            filing_date=datetime(2020, 1, 1),
            publication_date=datetime(2021, 1, 1),
            grant_date=datetime(2022, 1, 1) if i < 10 else None,
            status="granted" if i < 10 else "pending",
            assignee="TechCorp Inc",
            parent_id="US7000000" if i > 0 else None
        )
        mapper.add_patent(node)

    # Build family
    mapper.build_family("US7000000", [f"US{7000000 + i}" for i in range(1, 15)])

    # Generate report
    summary = mapper.generate_family_portfolio_summary()
    print("Patent Family Mapping Report")
    print(f"Total Families: {summary['total_families']}")
    print(f"Total Patents: {summary['total_patents']}")
    print(f"Jurisdictions: {summary['unique_jurisdictions']}")
    print(f"Average Family Value Score: {summary['avg_family_value_score']:.1f}")
