"""
Patent Landscape Analysis Example
Analyzes patent filing trends, technology distribution, and competitive landscape
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter
import statistics

@dataclass
class PatentData:
    """Patent record data"""
    patent_id: str
    title: str
    filing_date: datetime
    publication_date: datetime
    assignee: str
    ipc_classes: List[str]
    cpc_classes: List[str]
    claims_count: int
    citations_count: int
    cited_by_count: int


class PatentLandscapeAnalyzer:
    """Analyzes patent landscape and trends"""

    def __init__(self):
        self.patents: List[PatentData] = []
        self.technology_trends = defaultdict(int)

    def add_patent(self, patent: PatentData):
        """Add patent to analysis"""
        self.patents.append(patent)

    def analyze_filing_trends(self) -> Dict:
        """
        Analyze patent filing trends over time

        Returns:
            Dictionary with filing statistics by year
        """
        filings_by_year = defaultdict(int)

        for patent in self.patents:
            year = patent.filing_date.year
            filings_by_year[year] += 1

        sorted_years = sorted(filings_by_year.items())

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(sorted_years)):
            prev_count = sorted_years[i-1][1]
            curr_count = sorted_years[i][1]
            if prev_count > 0:
                growth = (curr_count - prev_count) / prev_count
                growth_rates.append(growth)

        return {
            'filings_by_year': dict(sorted_years),
            'average_filings_per_year': statistics.mean(filings_by_year.values()),
            'growth_rates': growth_rates,
            'avg_growth_rate': statistics.mean(growth_rates) if growth_rates else 0,
            'trend': 'increasing' if growth_rates and statistics.mean(growth_rates) > 0 else 'decreasing'
        }

    def analyze_technology_distribution(self) -> Dict:
        """
        Analyze distribution of patents by technology (IPC/CPC classes)

        Returns:
            Dictionary with technology distribution metrics
        """
        ipc_counts = Counter()
        technology_stack = defaultdict(list)

        for patent in self.patents:
            for ipc in patent.ipc_classes:
                ipc_counts[ipc] += 1
                technology_stack[ipc].append(patent.patent_id)

        # Get top technologies
        top_technologies = ipc_counts.most_common(10)

        # Calculate diversity (Herfindahl index)
        total_patents = len(self.patents)
        if total_patents > 0:
            herfindahl = sum((count / total_patents) ** 2 for count in ipc_counts.values())
            diversity_score = 1 - herfindahl  # Closer to 1 = more diverse
        else:
            diversity_score = 0

        return {
            'total_technologies': len(ipc_counts),
            'top_technologies': top_technologies,
            'technology_distribution': dict(ipc_counts),
            'diversity_score': diversity_score,
            'concentration': 1 - diversity_score
        }

    def analyze_competitive_landscape(self) -> Dict:
        """
        Analyze competitive landscape by assignee

        Returns:
            Dictionary with competitive metrics
        """
        assignee_counts = Counter()
        assignee_technologies = defaultdict(set)
        assignee_citations = defaultdict(int)

        for patent in self.patents:
            assignee_counts[patent.assignee] += 1
            for ipc in patent.ipc_classes:
                assignee_technologies[patent.assignee].add(ipc)
            assignee_citations[patent.assignee] += patent.cited_by_count

        # Get top assignees
        top_assignees = assignee_counts.most_common(10)

        # Calculate market concentration (HHI)
        total_patents = len(self.patents)
        if total_patents > 0:
            hhi = sum((count / total_patents) ** 2 for count in assignee_counts.values()) * 10000
        else:
            hhi = 0

        # Calculate strength by assignee (patents + citations)
        assignee_strength = {}
        for assignee in assignee_counts:
            strength = (assignee_counts[assignee] * 0.6 +
                       assignee_citations[assignee] * 0.4)
            assignee_strength[assignee] = strength

        top_competitors = sorted(assignee_strength.items(),
                                key=lambda x: x[1], reverse=True)[:10]

        return {
            'top_assignees': top_assignees,
            'total_assignees': len(assignee_counts),
            'hhi_index': hhi,
            'market_concentration': 'high' if hhi > 2500 else 'moderate' if hhi > 1500 else 'competitive',
            'top_competitors': top_competitors,
            'assignee_technology_breadth': {k: len(v) for k, v in assignee_technologies.items()}
        }

    def analyze_citation_patterns(self) -> Dict:
        """
        Analyze citation patterns and influence

        Returns:
            Dictionary with citation metrics
        """
        citation_counts = [p.citations_count for p in self.patents]
        cited_by_counts = [p.cited_by_count for p in self.patents]

        # Find influential patents
        most_cited = sorted(self.patents,
                           key=lambda p: p.cited_by_count,
                           reverse=True)[:10]

        influential_patents = [
            {
                'patent_id': p.patent_id,
                'title': p.title,
                'cited_by_count': p.cited_by_count
            }
            for p in most_cited
        ]

        return {
            'avg_citations_per_patent': statistics.mean(citation_counts) if citation_counts else 0,
            'avg_cited_by_count': statistics.mean(cited_by_counts) if cited_by_counts else 0,
            'most_cited_patents': influential_patents,
            'citation_range': (min(citation_counts) if citation_counts else 0,
                              max(citation_counts) if citation_counts else 0),
            'cited_by_range': (min(cited_by_counts) if cited_by_counts else 0,
                              max(cited_by_counts) if cited_by_counts else 0)
        }

    def generate_landscape_report(self) -> Dict:
        """
        Generate comprehensive landscape analysis report

        Returns:
            Complete landscape analysis
        """
        return {
            'total_patents': len(self.patents),
            'filing_trends': self.analyze_filing_trends(),
            'technology_landscape': self.analyze_technology_distribution(),
            'competitive_landscape': self.analyze_competitive_landscape(),
            'citation_analysis': self.analyze_citation_patterns(),
            'analysis_date': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    analyzer = PatentLandscapeAnalyzer()

    # Add sample patents
    for i in range(20):
        patent = PatentData(
            patent_id=f"US{7000000 + i}",
            title=f"Patent Title {i}",
            filing_date=datetime(2020 + i // 10, (i % 12) + 1, 1),
            publication_date=datetime(2021 + i // 10, (i % 12) + 1, 1),
            assignee=f"Company {i % 5}",
            ipc_classes=[f"G06F{13+i%10}/00", f"H04L{27+i%10}/00"],
            cpc_classes=[f"G06F17/30"],
            claims_count=20 + i,
            citations_count=5 + i % 10,
            cited_by_count=2 + i % 8
        )
        analyzer.add_patent(patent)

    report = analyzer.generate_landscape_report()
    print("Patent Landscape Analysis Report")
    print(f"Total Patents: {report['total_patents']}")
    print(f"Filing Trend: {report['filing_trends']['trend']}")
    print(f"Technology Diversity: {report['technology_landscape']['diversity_score']:.2f}")
    print(f"Market Concentration (HHI): {report['competitive_landscape']['hhi_index']:.0f}")
