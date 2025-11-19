"""
Legal Citation Network Analysis
Build and analyze citation graphs using NetworkX
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set
from collections import Counter


class LegalCitationNetwork:
    """
    Analyze citation networks to identify influential cases
    """

    def __init__(self):
        """Initialize directed graph for citations"""
        self.G = nx.DiGraph()

    def add_case(self, citation: str, metadata: Dict = None):
        """
        Add case to network

        Args:
            citation: Case citation
            metadata: Optional case metadata
        """
        self.G.add_node(citation, **(metadata or {}))

    def add_citation(self, citing_case: str, cited_case: str):
        """
        Add citation relationship

        Args:
            citing_case: Case that cites
            cited_case: Case being cited
        """
        self.G.add_edge(citing_case, cited_case, relationship="cites")

    def build_from_seed(self, seed_case: str, depth: int = 2,
                       get_citing_fn=None, get_cited_fn=None):
        """
        Build network from seed case

        Args:
            seed_case: Starting case
            depth: How many hops to expand
            get_citing_fn: Function to get citing cases
            get_cited_fn: Function to get cited cases
        """
        visited = set()

        def expand(case, current_depth):
            if current_depth > depth or case in visited:
                return

            visited.add(case)
            self.add_case(case)

            # Get cases cited by this case
            if get_cited_fn:
                cited = get_cited_fn(case)
                for cited_case in cited[:20]:  # Limit to top 20
                    self.add_case(cited_case)
                    self.add_citation(case, cited_case)
                    expand(cited_case, current_depth + 1)

            # Get cases citing this case
            if get_citing_fn:
                citing = get_citing_fn(case)
                for citing_case in citing[:20]:
                    self.add_case(citing_case)
                    self.add_citation(citing_case, case)

        expand(seed_case, 1)

    def calculate_influence(self) -> Dict[str, float]:
        """
        Calculate case influence using PageRank

        Returns:
            Dictionary of case -> influence score
        """
        pagerank = nx.pagerank(self.G, alpha=0.85)

        # Sort by influence
        ranked = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return dict(ranked)

    def find_hub_cases(self, top_k: int = 10) -> List[str]:
        """
        Find hub cases (highly connected)

        Args:
            top_k: Number of hubs to return

        Returns:
            List of hub case citations
        """
        # Calculate degree centrality
        centrality = nx.degree_centrality(self.G)

        # Sort by centrality
        hubs = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return [case for case, _ in hubs]

    def detect_communities(self) -> List[Set[str]]:
        """
        Detect citation communities (clusters of related cases)

        Returns:
            List of case communities
        """
        # Convert to undirected for community detection
        G_undirected = self.G.to_undirected()

        # Detect communities using Louvain method
        from networkx.algorithms import community

        communities = community.greedy_modularity_communities(G_undirected)

        return [set(comm) for comm in communities]

    def visualize(self, output_file: str = "citation_network.png"):
        """
        Visualize citation network

        Args:
            output_file: Output filename
        """
        plt.figure(figsize=(12, 8))

        pos = nx.spring_layout(self.G, k=0.5, iterations=50)

        # Color nodes by influence
        influence = self.calculate_influence()
        node_colors = [influence.get(node, 0) * 1000 for node in self.G.nodes()]

        # Draw network
        nx.draw(
            self.G,
            pos,
            node_color=node_colors,
            node_size=500,
            cmap=plt.cm.Reds,
            with_labels=True,
            font_size=8,
            arrows=True,
            edge_color='gray',
            alpha=0.6
        )

        plt.title("Legal Citation Network")
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Network visualization saved to {output_file}")


def main():
    """Example usage"""
    # Create network
    network = LegalCitationNetwork()

    # Add sample cases and citations
    network.add_case("Roe v. Wade, 410 U.S. 113 (1973)")
    network.add_case("Planned Parenthood v. Casey, 505 U.S. 833 (1992)")
    network.add_case("Dobbs v. Jackson, 597 U.S. ___ (2022)")

    network.add_citation(
        "Planned Parenthood v. Casey, 505 U.S. 833 (1992)",
        "Roe v. Wade, 410 U.S. 113 (1973)"
    )

    network.add_citation(
        "Dobbs v. Jackson, 597 U.S. ___ (2022)",
        "Roe v. Wade, 410 U.S. 113 (1973)"
    )

    network.add_citation(
        "Dobbs v. Jackson, 597 U.S. ___ (2022)",
        "Planned Parenthood v. Casey, 505 U.S. 833 (1992)"
    )

    # Calculate influence
    influence = network.calculate_influence()

    print("\nCase Influence (PageRank):")
    for case, score in list(influence.items())[:5]:
        print(f"  {case}: {score:.4f}")

    # Find hubs
    hubs = network.find_hub_cases(top_k=3)

    print("\nHub Cases (Most Connected):")
    for hub in hubs:
        print(f"  {hub}")

    # Visualize
    network.visualize()


if __name__ == "__main__":
    main()
