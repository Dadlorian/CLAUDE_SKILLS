#!/usr/bin/env python3
"""
Research Analytics: Citation Network Analysis
Advanced bibliometric analysis and visualization tools
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from datetime import datetime

class CitationAnalyzer:
    """Analyze citation patterns and research impact"""

    def __init__(self):
        self.papers = []
        self.citation_graph = nx.DiGraph()

    def add_paper(self, paper_id, title, authors, year, citations=0, references=None):
        """
        Add paper to analysis

        Parameters:
        -----------
        paper_id : str
            Unique identifier (DOI, PubMed ID, etc.)
        title : str
            Paper title
        authors : list
            List of author names
        year : int
            Publication year
        citations : int
            Number of times cited
        references : list, optional
            List of paper_ids this paper cites
        """
        paper = {
            'paper_id': paper_id,
            'title': title,
            'authors': authors,
            'year': year,
            'citations': citations,
            'references': references or []
        }
        self.papers.append(paper)

        # Add to citation graph
        self.citation_graph.add_node(paper_id, **paper)
        for ref_id in (references or []):
            self.citation_graph.add_edge(paper_id, ref_id)

    def calculate_h_index(self, author_papers):
        """
        Calculate h-index for a set of papers

        Parameters:
        -----------
        author_papers : list
            List of citation counts for papers

        Returns:
        --------
        int : h-index
        """
        if not author_papers:
            return 0

        # Sort in descending order
        sorted_citations = sorted(author_papers, reverse=True)

        h_index = 0
        for i, citations in enumerate(sorted_citations, 1):
            if citations >= i:
                h_index = i
            else:
                break

        return h_index

    def calculate_g_index(self, author_papers):
        """
        Calculate g-index (alternative to h-index)

        g-index: g papers have together received at least g² citations
        """
        if not author_papers:
            return 0

        sorted_citations = sorted(author_papers, reverse=True)
        cumulative = 0

        for g, citations in enumerate(sorted_citations, 1):
            cumulative += citations
            if cumulative < g * g:
                return g - 1

        return len(sorted_citations)

    def calculate_i10_index(self, author_papers):
        """Calculate i10-index (number of papers with ≥10 citations)"""
        return sum(1 for c in author_papers if c >= 10)

    def calculate_field_weighted_citation_impact(self, paper_citations, field_average):
        """
        Calculate FWCI (Field-Weighted Citation Impact)

        FWCI = actual citations / expected citations (field average)
        FWCI > 1.0 means above average impact
        """
        if field_average == 0:
            return 0
        return paper_citations / field_average

    def analyze_author_impact(self, author_name):
        """
        Comprehensive author impact analysis

        Returns:
        --------
        dict : Impact metrics including h-index, g-index, i10, etc.
        """
        # Find papers by author
        author_papers = [p for p in self.papers if author_name in p['authors']]

        if not author_papers:
            return {'error': f'No papers found for {author_name}'}

        citations_list = [p['citations'] for p in author_papers]
        total_citations = sum(citations_list)

        return {
            'author': author_name,
            'total_papers': len(author_papers),
            'total_citations': total_citations,
            'average_citations_per_paper': total_citations / len(author_papers),
            'h_index': self.calculate_h_index(citations_list),
            'g_index': self.calculate_g_index(citations_list),
            'i10_index': self.calculate_i10_index(citations_list),
            'most_cited_paper': max(author_papers, key=lambda p: p['citations'])['title'],
            'max_citations': max(citations_list),
            'papers_by_year': Counter(p['year'] for p in author_papers)
        }

    def identify_influential_papers(self, top_n=10):
        """
        Identify most influential papers using PageRank

        Returns:
        --------
        list : Top papers with PageRank scores
        """
        if len(self.citation_graph) == 0:
            return []

        # Calculate PageRank
        pagerank = nx.pagerank(self.citation_graph)

        # Sort by PageRank score
        ranked_papers = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

        results = []
        for paper_id, score in ranked_papers[:top_n]:
            paper_data = self.citation_graph.nodes[paper_id]
            results.append({
                'paper_id': paper_id,
                'title': paper_data.get('title', 'Unknown'),
                'pagerank_score': score,
                'citations': paper_data.get('citations', 0),
                'year': paper_data.get('year', 0)
            })

        return results

    def find_research_communities(self):
        """
        Detect research communities using citation patterns

        Returns:
        --------
        dict : Communities of related papers
        """
        # Convert to undirected for community detection
        undirected = self.citation_graph.to_undirected()

        # Find communities using Louvain method
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(undirected)

        community_info = {}
        for i, comm in enumerate(communities, 1):
            papers_in_community = []
            for paper_id in comm:
                node_data = self.citation_graph.nodes[paper_id]
                papers_in_community.append({
                    'paper_id': paper_id,
                    'title': node_data.get('title', 'Unknown')
                })

            community_info[f'Community {i}'] = {
                'size': len(comm),
                'papers': papers_in_community
            }

        return community_info

    def analyze_collaboration_network(self):
        """
        Build co-authorship network

        Returns:
        --------
        networkx.Graph : Collaboration network
        """
        collab_network = nx.Graph()

        # Build network from papers
        for paper in self.papers:
            authors = paper['authors']
            # Add edges between all co-authors
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    if collab_network.has_edge(author1, author2):
                        collab_network[author1][author2]['weight'] += 1
                    else:
                        collab_network.add_edge(author1, author2, weight=1)

        return collab_network

    def calculate_author_centrality(self, collab_network):
        """
        Calculate centrality metrics for collaboration network

        Returns:
        --------
        dict : Centrality scores for each author
        """
        degree_centrality = nx.degree_centrality(collab_network)
        betweenness_centrality = nx.betweenness_centrality(collab_network)
        closeness_centrality = nx.closeness_centrality(collab_network)

        centrality_scores = {}
        for author in collab_network.nodes():
            centrality_scores[author] = {
                'degree_centrality': degree_centrality[author],
                'betweenness_centrality': betweenness_centrality[author],
                'closeness_centrality': closeness_centrality[author]
            }

        return centrality_scores

    def visualize_citation_network(self, output_file="citation_network.png"):
        """Visualize citation network"""
        plt.figure(figsize=(12, 10))

        # Use spring layout for positioning
        pos = nx.spring_layout(self.citation_graph, k=0.5, iterations=50)

        # Draw nodes
        node_sizes = [self.citation_graph.nodes[node].get('citations', 10) * 20
                      for node in self.citation_graph.nodes()]

        nx.draw_networkx_nodes(self.citation_graph, pos,
                              node_size=node_sizes,
                              node_color='lightblue',
                              alpha=0.7)

        # Draw edges
        nx.draw_networkx_edges(self.citation_graph, pos,
                              alpha=0.3,
                              arrows=True,
                              arrowsize=10)

        # Draw labels (only for highly cited papers)
        high_impact = {node: self.citation_graph.nodes[node].get('title', '')[:30]
                      for node in self.citation_graph.nodes()
                      if self.citation_graph.nodes[node].get('citations', 0) > 50}

        nx.draw_networkx_labels(self.citation_graph, pos,
                               high_impact,
                               font_size=8)

        plt.title("Citation Network\n(Node size = citation count)", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Citation network saved to {output_file}")
        plt.close()

# Example usage and demonstration
if __name__ == "__main__":
    # Create analyzer
    analyzer = CitationAnalyzer()

    # Add example papers
    analyzer.add_paper(
        paper_id="DOI1",
        title="Machine Learning in Healthcare",
        authors=["Smith, J.", "Johnson, M."],
        year=2020,
        citations=150,
        references=[]
    )

    analyzer.add_paper(
        paper_id="DOI2",
        title="Deep Learning for Medical Imaging",
        authors=["Smith, J.", "Lee, K."],
        year=2021,
        citations=200,
        references=["DOI1"]
    )

    analyzer.add_paper(
        paper_id="DOI3",
        title="AI in Radiology: A Review",
        authors=["Johnson, M.", "Chen, L."],
        year=2022,
        citations=75,
        references=["DOI1", "DOI2"]
    )

    analyzer.add_paper(
        paper_id="DOI4",
        title="Explainable AI for Clinical Decision Support",
        authors=["Smith, J.", "Lee, K.", "Chen, L."],
        year=2023,
        citations=50,
        references=["DOI2", "DOI3"]
    )

    # Analyze author impact
    print("="*80)
    print("RESEARCH IMPACT ANALYSIS")
    print("="*80)

    impact = analyzer.analyze_author_impact("Smith, J.")
    print(f"\nAuthor: {impact['author']}")
    print(f"Total Papers: {impact['total_papers']}")
    print(f"Total Citations: {impact['total_citations']}")
    print(f"Average Citations per Paper: {impact['average_citations_per_paper']:.1f}")
    print(f"h-index: {impact['h_index']}")
    print(f"g-index: {impact['g_index']}")
    print(f"i10-index: {impact['i10_index']}")
    print(f"Most Cited Paper: {impact['most_cited_paper']}")

    # Influential papers
    print("\n" + "="*80)
    print("MOST INFLUENTIAL PAPERS (PageRank)")
    print("="*80)

    influential = analyzer.identify_influential_papers(top_n=3)
    for i, paper in enumerate(influential, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   PageRank Score: {paper['pagerank_score']:.4f}")
        print(f"   Citations: {paper['citations']}")
        print(f"   Year: {paper['year']}")

    # Collaboration network
    print("\n" + "="*80)
    print("COLLABORATION NETWORK ANALYSIS")
    print("="*80)

    collab_net = analyzer.analyze_collaboration_network()
    print(f"\nTotal Researchers: {collab_net.number_of_nodes()}")
    print(f"Total Collaborations: {collab_net.number_of_edges()}")

    centrality = analyzer.calculate_author_centrality(collab_net)
    print("\nMost Central Researchers:")
    sorted_centrality = sorted(centrality.items(),
                              key=lambda x: x[1]['degree_centrality'],
                              reverse=True)

    for author, scores in sorted_centrality[:3]:
        print(f"  {author}:")
        print(f"    Degree Centrality: {scores['degree_centrality']:.3f}")
        print(f"    Betweenness Centrality: {scores['betweenness_centrality']:.3f}")

    # Visualize
    analyzer.visualize_citation_network()

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)
