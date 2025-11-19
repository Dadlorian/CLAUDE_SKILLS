"""
Citation Analysis for Patents
Analyzes patent citations, builds citation networks, and tracks citation metrics
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CitationType(Enum):
    """Types of patent citations"""
    SELF = "self"  # Citations by same applicant
    BACKWARD = "backward"  # Cited patents (prior art)
    FORWARD = "forward"  # Patents citing this patent
    CROSS_REFERENCE = "cross_reference"  # Related applications


@dataclass
class Citation:
    """Patent citation"""
    patent_number: str
    title: str
    issue_date: Optional[datetime]
    citation_type: CitationType
    cited_by: str  # Patent that cites this one
    cite_position: Optional[str] = None  # Location in document
    examiner_cited: bool = False  # Whether cited by examiner
    applicant_cited: bool = False  # Whether cited by applicant


@dataclass
class CitationMetrics:
    """Citation metrics for a patent"""
    patent_number: str
    total_citations_given: int = 0
    total_citations_received: int = 0
    examiner_citations: int = 0
    applicant_citations: int = 0
    h_index: float = 0.0
    m_index: float = 0.0  # m-index (h-index / career length)
    self_citation_rate: float = 0.0
    citation_recency: float = 0.0  # Average age of citations


@dataclass
class CitationNetwork:
    """Citation network structure"""
    root_patent: str
    patents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, to, type)
    depth: int = 0


class CitationAnalyzer:
    """Analyze patent citations and citation networks"""

    def __init__(self):
        """Initialize citation analyzer"""
        self.citation_cache = {}
        self.metrics_cache = {}

    def get_patent_citations(self, patent_number: str) -> List[Citation]:
        """
        Get all citations made by a patent

        Args:
            patent_number: Patent number to analyze

        Returns:
            List of citations made by the patent
        """
        try:
            if patent_number in self.citation_cache:
                return self.citation_cache[patent_number]

            citations = []

            # In production, would query USPTO database
            citations = self._fetch_backward_citations(patent_number)

            self.citation_cache[patent_number] = citations
            return citations

        except Exception as e:
            logger.error(f"Failed to retrieve citations for {patent_number}: {e}")
            return []

    def get_citing_patents(self, patent_number: str) -> List[Citation]:
        """
        Get patents that cite a given patent

        Args:
            patent_number: Patent to find citations for

        Returns:
            List of patents citing the given patent
        """
        try:
            # Placeholder for forward citation retrieval
            logger.info(f"Retrieving citing patents for {patent_number}")

            citing = []
            # Would query database
            citing = self._fetch_forward_citations(patent_number)

            return citing

        except Exception as e:
            logger.error(f"Failed to retrieve citing patents: {e}")
            return []

    def calculate_metrics(self, patent_number: str) -> CitationMetrics:
        """
        Calculate citation metrics for a patent

        Args:
            patent_number: Patent number to analyze

        Returns:
            CitationMetrics object
        """
        try:
            if patent_number in self.metrics_cache:
                return self.metrics_cache[patent_number]

            # Get citations
            backward_citations = self.get_patent_citations(patent_number)
            forward_citations = self.get_citing_patents(patent_number)

            # Calculate basic metrics
            metrics = CitationMetrics(
                patent_number=patent_number,
                total_citations_given=len(backward_citations),
                total_citations_received=len(forward_citations),
            )

            # Calculate self-citation rate
            self_citations = sum(
                1 for c in backward_citations if c.citation_type == CitationType.SELF
            )
            if backward_citations:
                metrics.self_citation_rate = self_citations / len(backward_citations)

            # Calculate examiner vs applicant citations
            metrics.examiner_citations = sum(
                1 for c in backward_citations if c.examiner_cited
            )
            metrics.applicant_citations = sum(
                1 for c in backward_citations if c.applicant_cited
            )

            # Calculate h-index
            metrics.h_index = self._calculate_h_index(forward_citations)

            self.metrics_cache[patent_number] = metrics
            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return CitationMetrics(patent_number=patent_number)

    def build_citation_network(
        self,
        patent_number: str,
        depth: int = 2,
        direction: str = "both"
    ) -> CitationNetwork:
        """
        Build citation network around a patent

        Args:
            patent_number: Central patent
            depth: Depth of network to build
            direction: "backward", "forward", or "both"

        Returns:
            CitationNetwork object
        """
        network = CitationNetwork(root_patent=patent_number, depth=depth)
        visited = set()
        queue = deque([(patent_number, 0)])

        try:
            while queue:
                current_patent, current_depth = queue.popleft()

                if current_patent in visited or current_depth >= depth:
                    continue

                visited.add(current_patent)

                # Add patent to network
                network.patents[current_patent] = {
                    "depth": current_depth,
                    "metrics": self.calculate_metrics(current_patent)
                }

                # Add backward citations
                if direction in ["backward", "both"]:
                    citations = self.get_patent_citations(current_patent)
                    for citation in citations:
                        if citation.patent_number not in visited:
                            network.edges.append((current_patent, citation.patent_number, "cites"))
                            queue.append((citation.patent_number, current_depth + 1))

                # Add forward citations
                if direction in ["forward", "both"]:
                    citing = self.get_citing_patents(current_patent)
                    for patent in citing:
                        if patent.patent_number not in visited:
                            network.edges.append((patent.patent_number, current_patent, "cited_by"))
                            queue.append((patent.patent_number, current_depth + 1))

            return network

        except Exception as e:
            logger.error(f"Failed to build citation network: {e}")
            return network

    def find_citation_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        """
        Find citation paths between two patents

        Args:
            source: Source patent number
            target: Target patent number
            max_depth: Maximum path length

        Returns:
            List of paths (each path is a list of patent numbers)
        """
        paths = []
        visited = set()

        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth or current in visited:
                return

            if current == target:
                paths.append(path + [current])
                return

            visited.add(current)

            # Follow citations
            citations = self.get_patent_citations(current)
            for citation in citations:
                dfs(citation.patent_number, target, path + [current], depth + 1)

            # Follow citing patents
            citing = self.get_citing_patents(current)
            for patent in citing:
                dfs(patent.patent_number, target, path + [current], depth + 1)

            visited.remove(current)

        dfs(source, target, [], 0)
        return paths

    def analyze_citation_trends(self, patents: List[str]) -> Dict[str, Any]:
        """
        Analyze citation trends across multiple patents

        Args:
            patents: List of patent numbers

        Returns:
            Citation trend analysis
        """
        total_cites = 0
        total_cited = 0
        avg_age = 0
        citation_years = defaultdict(int)

        try:
            for patent in patents:
                metrics = self.calculate_metrics(patent)
                total_cites += metrics.total_citations_given
                total_cited += metrics.total_citations_received

                # Analyze citation dates
                citations = self.get_patent_citations(patent)
                for citation in citations:
                    if citation.issue_date:
                        citation_years[citation.issue_date.year] += 1

            avg_cites = total_cites / len(patents) if patents else 0
            avg_cited = total_cited / len(patents) if patents else 0

            return {
                "total_patents": len(patents),
                "total_citations_made": total_cites,
                "total_citations_received": total_cited,
                "avg_citations_per_patent": avg_cites,
                "avg_cited_per_patent": avg_cited,
                "citation_distribution": dict(citation_years)
            }

        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {}

    def identify_influential_patents(self, patents: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Identify most influential patents by citation count

        Args:
            patents: List of patent numbers to analyze
            top_n: Number of top patents to return

        Returns:
            List of (patent_number, influence_score) tuples
        """
        scores = []

        for patent in patents:
            metrics = self.calculate_metrics(patent)
            # Simple influence score: h-index
            score = metrics.h_index
            scores.append((patent, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_n]

    def compare_patents_by_citations(self, patent1: str, patent2: str) -> Dict[str, Any]:
        """
        Compare two patents based on citation metrics

        Args:
            patent1: First patent
            patent2: Second patent

        Returns:
            Comparison data
        """
        metrics1 = self.calculate_metrics(patent1)
        metrics2 = self.calculate_metrics(patent2)

        return {
            "patent1": {
                "number": patent1,
                "citations_given": metrics1.total_citations_given,
                "citations_received": metrics1.total_citations_received,
                "h_index": metrics1.h_index,
            },
            "patent2": {
                "number": patent2,
                "citations_given": metrics2.total_citations_given,
                "citations_received": metrics2.total_citations_received,
                "h_index": metrics2.h_index,
            },
            "difference": {
                "citations_received_diff": metrics1.total_citations_received - metrics2.total_citations_received,
                "h_index_diff": metrics1.h_index - metrics2.h_index,
            }
        }

    def _fetch_backward_citations(self, patent_number: str) -> List[Citation]:
        """Fetch backward citations (patents cited by this patent)"""
        # Placeholder for database query
        mock_citations = [
            Citation(
                patent_number="9000000",
                title="Solar Cell Technology",
                issue_date=datetime(2015, 3, 1),
                citation_type=CitationType.BACKWARD,
                cited_by=patent_number,
                examiner_cited=True
            ),
            Citation(
                patent_number="8500000",
                title="Photovoltaic Panels",
                issue_date=datetime(2012, 6, 15),
                citation_type=CitationType.BACKWARD,
                cited_by=patent_number,
                applicant_cited=True
            ),
        ]
        return mock_citations

    def _fetch_forward_citations(self, patent_number: str) -> List[Citation]:
        """Fetch forward citations (patents that cite this patent)"""
        # Placeholder for database query
        mock_citing = [
            Citation(
                patent_number="10000001",
                title="Advanced Solar Tracking",
                issue_date=datetime(2020, 1, 15),
                citation_type=CitationType.FORWARD,
                cited_by="10000001"
            ),
        ]
        return mock_citing

    def _calculate_h_index(self, citations: List[Citation]) -> float:
        """
        Calculate h-index from citation data

        The h-index is the largest number h such that at least h patents
        have at least h citations each.

        Args:
            citations: List of citations

        Returns:
            h-index value
        """
        if not citations:
            return 0.0

        # Count citation frequency
        citation_counts = defaultdict(int)
        for citation in citations:
            citation_counts[citation.patent_number] += 1

        # Sort by citation count
        counts = sorted(citation_counts.values(), reverse=True)

        # Calculate h-index
        h_index = 0
        for i, count in enumerate(counts, 1):
            if count >= i:
                h_index = i
            else:
                break

        return float(h_index)


class CitationReport:
    """Generate citation analysis reports"""

    def __init__(self, patent_number: str, analyzer: CitationAnalyzer):
        """
        Initialize citation report

        Args:
            patent_number: Patent to report on
            analyzer: CitationAnalyzer instance
        """
        self.patent_number = patent_number
        self.analyzer = analyzer
        self.metrics = analyzer.calculate_metrics(patent_number)

    def generate_summary(self) -> str:
        """Generate summary report"""
        report = f"""
        CITATION ANALYSIS REPORT
        Patent: {self.patent_number}
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        METRICS:
        - Citations Made: {self.metrics.total_citations_given}
        - Citations Received: {self.metrics.total_citations_received}
        - Examiner Citations: {self.metrics.examiner_citations}
        - Applicant Citations: {self.metrics.applicant_citations}
        - Self Citation Rate: {self.metrics.self_citation_rate:.1%}
        - h-index: {self.metrics.h_index:.1f}
        """

        return report

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "patent": self.patent_number,
            "generated": datetime.now().isoformat(),
            "metrics": {
                "citations_given": self.metrics.total_citations_given,
                "citations_received": self.metrics.total_citations_received,
                "h_index": self.metrics.h_index,
                "self_citation_rate": self.metrics.self_citation_rate,
            }
        }


def main():
    """Example usage"""
    analyzer = CitationAnalyzer()

    # Analyze specific patent
    patent_metrics = analyzer.calculate_metrics("10000000")
    print(f"Patent 10000000 metrics:")
    print(f"  Citations given: {patent_metrics.total_citations_given}")
    print(f"  Citations received: {patent_metrics.total_citations_received}")
    print(f"  h-index: {patent_metrics.h_index}")

    # Build citation network
    network = analyzer.build_citation_network("10000000", depth=2)
    print(f"\nCitation network built with {len(network.patents)} patents")

    # Generate report
    report = CitationReport("10000000", analyzer)
    print(report.generate_summary())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
