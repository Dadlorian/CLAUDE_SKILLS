# Citation Network Analysis Guide

## Overview

Citation network analysis applies graph theory and network science to legal research, revealing influential cases, precedent clusters, and hidden relationships in case law.

## Building Citation Networks

### Graph Representation

```python
import networkx as nx
import matplotlib.pyplot as plt

class LegalCitationNetwork:
    def __init__(self):
        self.G = nx.DiGraph()  # Directed graph (cites -> cited)

    def add_case(self, case_citation, metadata=None):
        """Add case as node"""
        self.G.add_node(case_citation, **(metadata or {}))

    def add_citation(self, citing_case, cited_case):
        """Add citation edge"""
        self.G.add_edge(citing_case, cited_case, relationship="cites")

    def build_from_seed(self, seed_case, depth=2):
        """Build network from seed case"""
        self.add_case(seed_case)

        def expand(case, current_depth):
            if current_depth > depth:
                return

            # Get citing and cited cases
            cited_by_case = get_authorities_cited_in(case)
            citing_case = get_cases_citing(case)

            for cited in cited_by_case[:20]:
                self.add_case(cited)
                self.add_citation(case, cited)
                expand(cited, current_depth + 1)

            for citing in citing_case[:20]:
                self.add_case(citing)
                self.add_citation(citing, case)

        expand(seed_case, 1)

        return self.G

# Usage
network = LegalCitationNetwork()
graph = network.build_from_seed("Miranda v. Arizona, 384 U.S. 436 (1966)")
```

## Network Analysis Metrics

### PageRank (Case Influence)

```python
def calculate_case_influence(citation_network):
    """Calculate influence using PageRank"""
    pagerank_scores = nx.pagerank(citation_network, alpha=0.85)

    # Rank cases by influence
    ranked = sorted(
        pagerank_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked

# Interpretation:
# Higher PageRank = More influential case (cited by important cases)
```

### Centrality Measures

```python
def analyze_case_centrality(citation_network, case):
    """Multiple centrality measures"""
    return {
        "degree_centrality": nx.degree_centrality(citation_network)[case],
        "betweenness": nx.betweenness_centrality(citation_network)[case],
        "closeness": nx.closeness_centrality(citation_network)[case],
        "eigenvector": nx.eigenvector_centrality(citation_network)[case]
    }

# Degree: How many citations (in + out)
# Betweenness: Bridge between different case clusters
# Closeness: How "close" to all other cases
# Eigenvector: Connected to other important cases
```

### Community Detection

```python
from networkx.algorithms import community

def identify_case_clusters(citation_network):
    """Find clusters of related cases"""
    # Convert to undirected for community detection
    G_undirected = citation_network.to_undirected()

    # Detect communities
    communities = community.greedy_modularity_communities(G_undirected)

    return [
        {
            "cluster_id": i,
            "cases": list(comm),
            "size": len(comm),
            "topic": infer_cluster_topic(comm)
        }
        for i, comm in enumerate(communities)
    ]

# Example output:
# Cluster 1: Criminal procedure cases (Miranda warnings)
# Cluster 2: Evidence admissibility
# Cluster 3: 4th Amendment search cases
```

## Visualization Techniques

### Interactive Network Visualization

```python
import plotly.graph_objects as go

def visualize_citation_network(citation_network):
    """Create interactive network visualization"""
    pos = nx.spring_layout(citation_network)

    # Extract node and edge information
    edge_x, edge_y = [], []
    for edge in citation_network.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y = [], []
    for node in citation_network.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            size=10,
            color=[citation_network.degree(node) for node in citation_network.nodes()],
            colorscale='YlOrRd',
            showscale=True
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.show()
```

## Research Applications

### Finding Hidden Authorities

```python
def find_overlooked_authorities(citation_network, known_authorities):
    """Discover important but overlooked cases"""
    # Calculate influence
    pagerank = nx.pagerank(citation_network)

    # Find high-influence cases not in known_authorities
    overlooked = [
        (case, score)
        for case, score in pagerank.items()
        if case not in known_authorities and score > 0.01
    ]

    return sorted(overlooked, key=lambda x: x[1], reverse=True)
```

### Precedent Evolution Tracking

```python
def track_precedent_evolution(citation_network, doctrine):
    """Track how legal doctrine evolved over time"""
    # Filter to relevant cases
    relevant_cases = [
        node for node in citation_network.nodes()
        if doctrine in get_case_summary(node)
    ]

    # Create subgraph
    subgraph = citation_network.subgraph(relevant_cases)

    # Analyze temporal progression
    cases_by_year = group_by_year(subgraph.nodes())

    evolution = []
    for year in sorted(cases_by_year.keys()):
        year_cases = cases_by_year[year]
        evolution.append({
            "year": year,
            "case_count": len(year_cases),
            "key_developments": identify_key_developments(year_cases),
            "trend": analyze_trend(year_cases)
        })

    return evolution
```

---

*Citation network analysis reveals the structure and evolution of legal precedent through computational methods.*
