"""Network Analysis for Transaction Chains"""
from typing import List, Dict

class NetworkAnalyzer:
    """Analyze transaction networks"""
    
    def analyze_transaction_network(self, transactions: List[Dict]) -> dict:
        """Analyze transaction flow network"""
        unique_parties = set()
        total_volume = 0
        transaction_count = len(transactions)
        
        for txn in transactions:
            unique_parties.add(txn.get('beneficiary'))
            total_volume += txn.get('amount', 0)
        
        return {
            'network_nodes': len(unique_parties),
            'total_volume': total_volume,
            'transaction_count': transaction_count,
            'average_transaction': total_volume / transaction_count if transaction_count > 0 else 0,
            'complexity_score': len(unique_parties) * transaction_count
        }
    
    def detect_circular_flow(self, transactions: List[Dict]) -> dict:
        """Detect circular transaction patterns"""
        graph = {}
        for txn in transactions:
            source = txn.get('source')
            dest = txn.get('destination')
            if source not in graph:
                graph[source] = []
            graph[source].append(dest)
        
        # Check for cycles
        cycles_found = 0
        for node in graph:
            if self._has_cycle(graph, node):
                cycles_found += 1
        
        return {
            'circular_patterns_detected': cycles_found > 0,
            'cycle_count': cycles_found,
            'nodes_in_cycles': sum(1 for node in graph if self._has_cycle(graph, node))
        }
    
    def _has_cycle(self, graph: dict, node: str, visited: set = None) -> bool:
        """Check if path has cycle"""
        if visited is None:
            visited = set()
        if node in visited:
            return True
        visited.add(node)
        for neighbor in graph.get(node, []):
            if self._has_cycle(graph, neighbor, visited):
                return True
        return False
