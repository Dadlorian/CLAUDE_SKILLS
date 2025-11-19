"""
Graph Analyzer - Detect fraud rings using network analysis
"""

from typing import Dict, Set, List


class GraphAnalyzer:
    """Analyze entity relationships for fraud rings"""

    def __init__(self, graph_db):
        self.graph = graph_db

    def detect_fraud_ring(self, customer_id: str) -> Dict:
        """Detect if customer is part of fraud ring"""
        # Get connected nodes
        neighbors = self.graph.get_neighbors(customer_id)

        # Count fraud connections
        fraud_neighbors = [n for n in neighbors if n.get('fraud_flag')]

        ring_likelihood = len(fraud_neighbors) / max(len(neighbors), 1)

        return {
            'customer_id': customer_id,
            'neighbors': len(neighbors),
            'fraud_neighbors': len(fraud_neighbors),
            'ring_likelihood': ring_likelihood,
            'is_ring_member': ring_likelihood > 0.3
        }

    def get_device_network(self, device_id: str) -> Dict:
        """Get all customers using device"""
        customers = self.graph.get_customers_by_device(device_id)

        fraud_customers = [c for c in customers if c.get('fraud_flag')]

        return {
            'device_id': device_id,
            'customer_count': len(customers),
            'fraud_customers': len(fraud_customers),
            'risk': 'high' if len(fraud_customers) > 2 else 'medium'
            if len(fraud_customers) > 0 else 'low'
        }
