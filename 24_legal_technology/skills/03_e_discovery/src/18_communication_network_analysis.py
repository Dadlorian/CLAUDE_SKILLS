"""
Communication Network Analysis Example
Demonstrates analyzing communication patterns and relationships
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import json

class CommunicationNetworkAnalyzer:
    """Analyzes communication networks in documents"""

    def __init__(self):
        """Initialize network analyzer"""
        self.nodes = set()  # Participants
        self.edges = defaultdict(int)  # Communication pairs

    def build_network(self, documents: List[Dict]) -> Dict:
        """
        Build communication network from documents

        Args:
            documents: List of email documents

        Returns:
            Network structure
        """
        for doc in documents:
            from_addr = doc.get('From')
            to_list = doc.get('To', [])
            cc_list = doc.get('Cc', [])

            if from_addr:
                self.nodes.add(from_addr)

            # Add edges for all recipients
            for recipient in to_list + cc_list:
                if recipient:
                    self.nodes.add(recipient)
                    # Create edge from sender to recipient
                    pair = (from_addr, recipient) if from_addr < recipient else (recipient, from_addr)
                    self.edges[pair] += 1

        return {
            "nodes": list(self.nodes),
            "node_count": len(self.nodes),
            "edges": dict(self.edges),
            "edge_count": len(self.edges)
        }

    def identify_key_players(self, top_n: int = 10) -> List[Dict]:
        """
        Identify most central participants

        Args:
            top_n: Number of top participants to return

        Returns:
            List of key participants with metrics
        """
        participant_scores = defaultdict(int)

        for (p1, p2), count in self.edges.items():
            participant_scores[p1] += count
            participant_scores[p2] += count

        sorted_participants = sorted(
            participant_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "participant": participant,
                "communication_count": score,
                "rank": i + 1
            }
            for i, (participant, score) in enumerate(sorted_participants[:top_n])
        ]

    def find_communication_clusters(self) -> List[Set]:
        """
        Identify clusters of frequently communicating people

        Returns:
            List of participant clusters
        """
        # Simple clustering: group by connection strength
        clusters = []
        processed = set()

        # Sort edges by weight
        sorted_edges = sorted(
            self.edges.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for (p1, p2), count in sorted_edges:
            # Skip if already in cluster
            in_existing = False
            for cluster in clusters:
                if p1 in cluster or p2 in cluster:
                    cluster.add(p1)
                    cluster.add(p2)
                    in_existing = True
                    break

            if not in_existing:
                clusters.append({p1, p2})

        return clusters

    def analyze_communication_hierarchy(self) -> Dict:
        """
        Analyze hierarchical structure of communications

        Returns:
            Hierarchy analysis
        """
        # Identify central hub participants
        participant_scores = defaultdict(int)
        for (p1, p2), count in self.edges.items():
            participant_scores[p1] += count
            participant_scores[p2] += count

        # Define levels
        total_score = sum(participant_scores.values())
        avg_score = total_score / len(participant_scores) if participant_scores else 0

        executives = [p for p, score in participant_scores.items() if score > avg_score * 1.5]
        managers = [p for p, score in participant_scores.items()
                   if avg_score * 0.8 <= score <= avg_score * 1.5]
        staff = [p for p, score in participant_scores.items() if score < avg_score * 0.8]

        return {
            "executives": executives,
            "managers": managers,
            "staff": staff,
            "total_levels": 3 if all([executives, managers, staff]) else 2 if all([executives, managers]) else 1
        }


class CorrespondenceAnalysis:
    """Analyzes specific correspondence patterns"""

    @staticmethod
    def analyze_correspondence_frequency(documents: List[Dict]) -> Dict:
        """
        Analyze frequency of correspondence over time

        Args:
            documents: List of documents

        Returns:
            Frequency analysis
        """
        from collections import defaultdict

        frequency = defaultdict(int)

        for doc in documents:
            date = doc.get('DateCreated')
            if date:
                date_only = date.split('T')[0]
                frequency[date_only] += 1

        return {
            "by_date": dict(sorted(frequency.items())),
            "total_documents": sum(frequency.values()),
            "busiest_date": max(frequency.items(), key=lambda x: x[1])[0]
            if frequency else None,
            "average_per_day": sum(frequency.values()) / len(frequency) if frequency else 0
        }

    @staticmethod
    def identify_correspondence_threads(documents: List[Dict]) -> Dict:
        """
        Identify main topics of correspondence

        Args:
            documents: List of documents

        Returns:
            Topic analysis
        """
        from collections import Counter

        subjects = [doc.get('Subject', 'No Subject') for doc in documents]
        subject_counts = Counter(subjects)

        # Get top subjects
        top_subjects = subject_counts.most_common(10)

        return {
            "unique_subjects": len(subject_counts),
            "top_subjects": [
                {"subject": subject, "count": count}
                for subject, count in top_subjects
            ],
            "total_documents": len(documents)
        }

    @staticmethod
    def analyze_response_patterns(documents: List[Dict]) -> Dict:
        """
        Analyze response patterns and timing

        Args:
            documents: List of documents sorted by date

        Returns:
            Response pattern analysis
        """
        response_times = []
        person_response_rates = defaultdict(lambda: {"total": 0, "responses": 0})

        for i in range(len(documents) - 1):
            current = documents[i]
            next_doc = documents[i + 1]

            current_from = current.get('From')
            next_from = next_doc.get('From')

            # Check if next message is from different person
            if current_from and next_from and current_from != next_from:
                person_response_rates[next_from]["total"] += 1

                # Simple response indicator
                if next_from != current_from:
                    person_response_rates[next_from]["responses"] += 1

        response_rates = {}
        for person, stats in person_response_rates.items():
            if stats["total"] > 0:
                rate = stats["responses"] / stats["total"]
                response_rates[person] = round(rate, 2)

        return {
            "response_rates": response_rates,
            "most_responsive": max(response_rates.items(), key=lambda x: x[1])[0]
            if response_rates else None,
            "average_response_rate": sum(response_rates.values()) / len(response_rates)
            if response_rates else 0
        }


class RelationshipMapping:
    """Maps relationships between participants"""

    @staticmethod
    def create_relationship_matrix(documents: List[Dict],
                                   participants: List[str] = None) -> Dict:
        """
        Create matrix showing communication relationships

        Args:
            documents: List of documents
            participants: List of specific participants to include

        Returns:
            Relationship matrix
        """
        from_counts = defaultdict(lambda: defaultdict(int))

        for doc in documents:
            from_addr = doc.get('From')
            to_list = doc.get('To', []) + doc.get('Cc', [])

            if from_addr:
                for recipient in to_list:
                    from_counts[from_addr][recipient] += 1

        # Filter to specific participants if provided
        if participants:
            filtered = {k: {r: c for r, c in v.items() if r in participants}
                       for k, v in from_counts.items() if k in participants}
        else:
            filtered = from_counts

        return {
            "matrix": dict(filtered),
            "total_relationships": sum(
                len(v) for v in filtered.values()
            )
        }

    @staticmethod
    def identify_key_relationships(documents: List[Dict],
                                  min_communications: int = 5) -> List[Dict]:
        """
        Identify significant relationships

        Args:
            documents: List of documents
            min_communications: Minimum communications to be significant

        Returns:
            List of key relationships
        """
        relationships = defaultdict(int)

        for doc in documents:
            from_addr = doc.get('From')
            to_list = doc.get('To', []) + doc.get('Cc', [])

            for to_addr in to_list:
                if from_addr and to_addr and from_addr != to_addr:
                    pair = (from_addr, to_addr) if from_addr < to_addr else (to_addr, from_addr)
                    relationships[pair] += 1

        # Filter by minimum communications
        significant = [
            {
                "participant_1": pair[0],
                "participant_2": pair[1],
                "communication_count": count
            }
            for pair, count in relationships.items()
            if count >= min_communications
        ]

        return sorted(significant, key=lambda x: x['communication_count'], reverse=True)


# Example usage
if __name__ == "__main__":
    analyzer = CommunicationNetworkAnalyzer()

    # Sample documents
    docs = [
        {"From": "john@company.com", "To": ["manager@company.com"], "Cc": []},
        {"From": "manager@company.com", "To": ["john@company.com", "legal@company.com"], "Cc": []},
        {"From": "legal@company.com", "To": ["manager@company.com"], "Cc": []},
    ]

    network = analyzer.build_network(docs)
    print(f"Network Nodes: {network['node_count']}")
    print(f"Network Edges: {network['edge_count']}")

    key_players = analyzer.identify_key_players(top_n=3)
    print(f"Key Players: {key_players}")

    # Relationship analysis
    relationships = RelationshipMapping.identify_key_relationships(docs)
    print(f"Key Relationships: {len(relationships)}")
