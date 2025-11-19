"""
Legal Knowledge Graph
Builds and manages knowledge graphs of legal concepts, cases, and relationships
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Node:
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    node_type: str  # case, statute, concept, court, etc.
    properties: Dict[str, any] = field(default_factory=dict)


@dataclass
class Edge:
    """Represents a relationship between nodes"""
    source_id: str
    target_id: str
    relation_type: str  # cites, overrules, interprets, etc.
    weight: float = 1.0
    properties: Dict[str, any] = field(default_factory=dict)


class LegalKnowledgeGraph:
    """
    Knowledge graph for legal research
    """

    # Relation types
    RELATION_TYPES = {
        "cites": "references or cites",
        "overrules": "overrules or reverses",
        "affirms": "affirms or upholds",
        "distinguishes": "distinguishes from",
        "interprets": "interprets statute",
        "applies_to": "applies to situation",
        "related_to": "related concept",
        "contradicts": "contradicts",
    }

    def __init__(self):
        """Initialize knowledge graph"""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency_list: Dict[str, List[str]] = {}

    def add_node(self, node_id: str, label: str, node_type: str,
                 properties: Optional[Dict] = None):
        """
        Add node to graph

        Args:
            node_id: Unique identifier for node
            label: Human-readable label
            node_type: Type of node
            properties: Additional properties
        """
        node = Node(
            id=node_id,
            label=label,
            node_type=node_type,
            properties=properties or {}
        )
        self.nodes[node_id] = node
        self.adjacency_list[node_id] = []
        logger.info(f"Added node: {node_id}")

    def add_edge(self, source_id: str, target_id: str, relation_type: str,
                 weight: float = 1.0, properties: Optional[Dict] = None):
        """
        Add edge to graph

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relationship
            weight: Edge weight
            properties: Additional properties
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"Cannot add edge: nodes {source_id} or {target_id} not found")
            return

        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            properties=properties or {}
        )
        self.edges.append(edge)
        self.adjacency_list[source_id].append(target_id)
        logger.info(f"Added edge: {source_id} -{relation_type}-> {target_id}")

    def get_neighbors(self, node_id: str, relation_type: Optional[str] = None) -> List[str]:
        """
        Get neighbors of a node

        Args:
            node_id: Node ID
            relation_type: Filter by relation type

        Returns:
            List of neighbor node IDs
        """
        neighbors = []

        for edge in self.edges:
            if edge.source_id == node_id:
                if relation_type is None or edge.relation_type == relation_type:
                    neighbors.append(edge.target_id)

        return neighbors

    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> Optional[List[str]]:
        """
        Find shortest path between two nodes using BFS

        Args:
            start_id: Start node ID
            end_id: End node ID
            max_depth: Maximum search depth

        Returns:
            Path as list of node IDs, or None if no path found
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        queue = [(start_id, [start_id])]
        visited = {start_id}
        depth = 0

        while queue and depth < max_depth:
            current, path = queue.pop(0)

            if current == end_id:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

            depth += 1

        return None

    def find_related_cases(self, case_id: str, max_distance: int = 2) -> List[Tuple[str, str]]:
        """
        Find related cases through citation network

        Args:
            case_id: Case ID to start from
            max_distance: Maximum relationship distance

        Returns:
            List of (case_id, relation_type) tuples
        """
        related = []
        visited = {case_id}
        queue = [(case_id, 0)]

        while queue:
            current_id, distance = queue.pop(0)

            if distance > 0:
                node = self.nodes.get(current_id)
                if node and node.node_type == "case":
                    relation = None
                    for edge in self.edges:
                        if edge.target_id == current_id:
                            relation = edge.relation_type
                            break
                    related.append((current_id, relation or "related"))

            if distance < max_distance:
                for neighbor in self.get_neighbors(current_id):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, distance + 1))

        return related

    def get_citation_network(self, case_id: str) -> Dict[str, List[str]]:
        """
        Get citation network for a case

        Args:
            case_id: Case ID

        Returns:
            Dictionary with citing and cited cases
        """
        citing = []
        cited = []

        for edge in self.edges:
            if edge.target_id == case_id and edge.relation_type == "cites":
                citing.append(edge.source_id)
            elif edge.source_id == case_id and edge.relation_type == "cites":
                cited.append(edge.target_id)

        return {
            "citing_cases": citing,
            "cited_cases": cited,
            "total_citations": len(citing) + len(cited)
        }

    def find_contradictions(self) -> List[Tuple[str, str]]:
        """
        Find contradictory relationships in graph

        Args:
            None

        Returns:
            List of (node1, node2) pairs with contradictory relations
        """
        contradictions = []

        for i, edge1 in enumerate(self.edges):
            for edge2 in self.edges[i+1:]:
                # Check if same nodes with opposite relations
                if (edge1.source_id == edge2.source_id and
                    edge1.target_id == edge2.target_id):
                    if edge1.relation_type == "affirms" and edge2.relation_type == "overrules":
                        contradictions.append((edge1.source_id, edge1.target_id))

        return contradictions

    def export_graph_data(self) -> Dict:
        """
        Export graph as dictionary for serialization

        Args:
            None

        Returns:
            Dictionary representation of graph
        """
        return {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type,
                    "properties": node.properties
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "relation": edge.relation_type,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }

    def get_statistics(self) -> Dict[str, any]:
        """
        Get graph statistics

        Args:
            None

        Returns:
            Dictionary with graph statistics
        """
        node_types = {}
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1

        relation_types = {}
        for edge in self.edges:
            relation_types[edge.relation_type] = relation_types.get(edge.relation_type, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "relation_types": relation_types,
            "average_degree": (2 * len(self.edges)) / len(self.nodes) if self.nodes else 0
        }


# Usage example
if __name__ == "__main__":
    kg = LegalKnowledgeGraph()

    # Add nodes
    kg.add_node("case_001", "Marbury v. Madison", "case", {"year": 1803})
    kg.add_node("case_002", "McCulloch v. Maryland", "case", {"year": 1819})
    kg.add_node("statute_001", "42 U.S.C. § 1983", "statute")
    kg.add_node("concept_001", "Judicial Review", "concept")

    # Add edges
    kg.add_edge("case_002", "case_001", "cites")
    kg.add_edge("case_001", "concept_001", "establishes")
    kg.add_edge("statute_001", "case_001", "related_to")

    # Query graph
    related = kg.find_related_cases("case_001")
    print(f"Related cases: {related}")

    # Get statistics
    stats = kg.get_statistics()
    print(f"Graph statistics: {stats}")
