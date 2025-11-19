"""
Patent Citation Analysis Example
Analyzes patent citations and impact
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import networkx as nx

class CitationAnalyzer:
    """Analyze patent citations and citation networks"""

    def __init__(self):
        self.citation_graph = nx.DiGraph()
        self.patent_metadata = {}

    def add_patent(self, patent_number: str, title: str,
                   cited_patents: List[str], citations_received: List[str] = None):
        """Add patent to the citation network"""
        self.citation_graph.add_node(patent_number)
        self.patent_metadata[patent_number] = {
            'title': title,
            'cited_patents': cited_patents,
            'citations_received': citations_received or []
        }

        # Add edges for cited patents (backward citations)
        for cited in cited_patents:
            self.citation_graph.add_edge(patent_number, cited)

    def calculate_h_index(self, patent_number: str) -> int:
        """
        Calculate h-index for a patent
        H-index is the largest h such that the patent was cited by h patents
        that were each cited by at least h patents
        """
        # Get all patents that cite this one
        citing_patents = list(self.citation_graph.predecessors(patent_number))

        if not citing_patents:
            return 0

        # Count citations for each citing patent
        citation_counts = []
        for citing in citing_patents:
            in_degree = self.citation_graph.in_degree(citing)
            citation_counts.append(in_degree)

        # Sort in descending order
        citation_counts.sort(reverse=True)

        # Calculate h-index
        h_index = 0
        for i, count in enumerate(citation_counts):
            if count >= i + 1:
                h_index = i + 1
            else:
                break

        return h_index

    def get_pagerank_scores(self) -> Dict[str, float]:
        """
        Calculate PageRank scores for all patents
        Higher scores indicate more influential patents
        """
        if len(self.citation_graph) == 0:
            return {}

        return nx.pagerank(self.citation_graph)

    def find_influential_patents(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find most influential patents by PageRank"""
        scores = self.get_pagerank_scores()
        sorted_patents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_patents[:top_n]

    def analyze_citation_timeline(self, patent_number: str) -> Dict:
        """
        Analyze how many times a patent was cited over time
        """
        # This would require date information
        # Placeholder for actual timeline analysis
        return {
            'patent_number': patent_number,
            'total_citations': len(self.patent_metadata.get(patent_number, {}).get('citations_received', []))
        }

    def detect_technology_clusters(self) -> List[Set[str]]:
        """
        Detect clusters of related technologies using citation patterns
        """
        # Use community detection algorithm
        communities = nx.community.greedy_modularity_communities(self.citation_graph.to_undirected())

        return [set(community) for community in communities]

    def find_common_references(self, patent_list: List[str]) -> List[str]:
        """
        Find patents commonly cited by a group of patents
        Useful for identifying related prior art
        """
        if not patent_list:
            return []

        # Get citations for each patent
        all_citations = []
        for patent in patent_list:
            citations = self.patent_metadata.get(patent, {}).get('cited_patents', [])
            all_citations.append(set(citations))

        if not all_citations:
            return []

        # Find intersection (common citations)
        common = all_citations[0]
        for citations in all_citations[1:]:
            common = common.intersection(citations)

        return list(common)

    def get_citation_distance(self, source_patent: str, target_patent: str) -> int:
        """
        Calculate shortest citation path between two patents
        """
        try:
            return nx.shortest_path_length(self.citation_graph, source_patent, target_patent)
        except nx.NetworkXNoPath:
            return -1  # No path exists
        except nx.NodeNotFound:
            return -1  # Patent not found

    def analyze_patent_impact(self, patent_number: str) -> Dict:
        """Comprehensive impact analysis of a patent"""
        in_degree = self.citation_graph.in_degree(patent_number)
        out_degree = self.citation_graph.out_degree(patent_number)

        pagerank = self.get_pagerank_scores().get(patent_number, 0)
        h_index = self.calculate_h_index(patent_number)

        return {
            'patent_number': patent_number,
            'times_cited': in_degree,
            'cites_others': out_degree,
            'page_rank': pagerank,
            'h_index': h_index,
            'impact_score': in_degree * pagerank  # Simple combined metric
        }

    def get_citation_network_stats(self) -> Dict:
        """Get overall statistics about the citation network"""
        if len(self.citation_graph) == 0:
            return {}

        return {
            'total_patents': len(self.citation_graph),
            'total_citations': len(self.citation_graph.edges()),
            'network_density': nx.density(self.citation_graph),
            'avg_citations_per_patent': len(self.citation_graph.edges()) / len(self.citation_graph)
        }


# Example usage
if __name__ == "__main__":
    analyzer = CitationAnalyzer()

    # Add some patents to the network
    analyzer.add_patent("US7123456", "Neural Network Patent",
                       cited_patents=["US5000001", "US5000002"])
    analyzer.add_patent("US7123457", "Deep Learning Patent",
                       cited_patents=["US7123456", "US5000001"])
    analyzer.add_patent("US5000001", "Baseline Algorithm",
                       cited_patents=[])

    # Find influential patents
    influential = analyzer.find_influential_patents(3)
    print("Influential patents:", influential)

    # Analyze citation network
    stats = analyzer.get_citation_network_stats()
    print("Network stats:", stats)

    # Analyze specific patent
    impact = analyzer.analyze_patent_impact("US7123456")
    print("Patent impact:", impact)
