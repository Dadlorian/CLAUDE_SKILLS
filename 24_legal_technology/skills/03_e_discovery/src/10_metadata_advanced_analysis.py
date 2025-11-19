"""
Advanced Metadata Analysis Example
Demonstrates complex metadata analysis and pattern detection
"""

from typing import Dict, List, Set
from collections import defaultdict, Counter
from datetime import datetime
import statistics

class MetadataAnalyzer:
    """Performs advanced analysis on document metadata"""

    @staticmethod
    def analyze_communication_patterns(metadata_list: List[Dict]) -> Dict:
        """
        Analyze communication patterns from metadata

        Args:
            metadata_list: List of document metadata

        Returns:
            Communication analysis
        """
        sender_counts = Counter()
        recipient_counts = Counter()
        sender_recipient_pairs = Counter()
        communication_by_date = defaultdict(int)

        for metadata in metadata_list:
            author = metadata.get('author')
            participants = metadata.get('participants', [])
            date_created = metadata.get('date_created')

            if author and metadata.get('document_type') == 'Email':
                sender_counts[author] += 1

                for participant in participants:
                    if participant != author:
                        recipient_counts[participant] += 1
                        pair = (author, participant)
                        sender_recipient_pairs[pair] += 1

            if date_created:
                date_only = date_created.split('T')[0]
                communication_by_date[date_only] += 1

        return {
            "top_senders": dict(sender_counts.most_common(10)),
            "top_recipients": dict(recipient_counts.most_common(10)),
            "most_frequent_pairs": [
                {"from": pair[0], "to": pair[1], "count": count}
                for pair, count in sender_recipient_pairs.most_common(10)
            ],
            "total_unique_senders": len(sender_counts),
            "total_unique_recipients": len(recipient_counts),
            "communication_dates": dict(sorted(communication_by_date.items()))
        }

    @staticmethod
    def identify_custodian_patterns(metadata_list: List[Dict]) -> Dict:
        """
        Analyze patterns by custodian

        Args:
            metadata_list: List of metadata

        Returns:
            Custodian analysis
        """
        custodian_stats = defaultdict(lambda: {
            "document_count": 0,
            "document_types": Counter(),
            "total_size": 0,
            "date_range": {"min": None, "max": None},
            "communications": set()
        })

        for metadata in metadata_list:
            custodian = metadata.get('custodian')
            if not custodian:
                continue

            stats = custodian_stats[custodian]
            stats["document_count"] += 1
            stats["document_types"][metadata.get('document_type')] += 1
            stats["total_size"] += metadata.get('size_bytes', 0)

            # Track date range
            date_created = metadata.get('date_created')
            if date_created:
                if not stats["date_range"]["min"] or date_created < stats["date_range"]["min"]:
                    stats["date_range"]["min"] = date_created
                if not stats["date_range"]["max"] or date_created > stats["date_range"]["max"]:
                    stats["date_range"]["max"] = date_created

            # Track communications
            for participant in metadata.get('participants', []):
                if participant != metadata.get('author'):
                    stats["communications"].add(participant)

        # Convert to serializable format
        result = {}
        for custodian, stats in custodian_stats.items():
            result[custodian] = {
                "document_count": stats["document_count"],
                "document_types": dict(stats["document_types"]),
                "total_size_bytes": stats["total_size"],
                "avg_doc_size": stats["total_size"] / stats["document_count"]
                if stats["document_count"] > 0 else 0,
                "date_range": stats["date_range"],
                "unique_communications": len(stats["communications"])
            }

        return result

    @staticmethod
    def detect_document_anomalies(metadata_list: List[Dict]) -> List[Dict]:
        """
        Identify unusual documents that may warrant review

        Args:
            metadata_list: List of metadata

        Returns:
            List of anomalies
        """
        anomalies = []

        # Calculate statistics
        sizes = [m.get('size_bytes', 0) for m in metadata_list]
        avg_size = statistics.mean(sizes) if sizes else 0
        stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0

        participant_counts = [len(m.get('participants', [])) for m in metadata_list]
        avg_participants = statistics.mean(participant_counts) if participant_counts else 0

        for metadata in metadata_list:
            # Unusually large files
            if stdev_size > 0 and metadata.get('size_bytes', 0) > avg_size + (3 * stdev_size):
                anomalies.append({
                    "document_id": metadata.get('document_id'),
                    "anomaly_type": "unusually_large",
                    "size_bytes": metadata.get('size_bytes'),
                    "average_size": int(avg_size)
                })

            # Unusually many recipients
            num_participants = len(metadata.get('participants', []))
            if num_participants > avg_participants + 5:
                anomalies.append({
                    "document_id": metadata.get('document_id'),
                    "anomaly_type": "many_recipients",
                    "recipient_count": num_participants,
                    "average_recipients": int(avg_participants)
                })

            # Documents with multiple recipients but small size (potential blast email)
            if num_participants > 10 and metadata.get('size_bytes', 0) < avg_size * 0.1:
                anomalies.append({
                    "document_id": metadata.get('document_id'),
                    "anomaly_type": "blast_communication",
                    "recipients": num_participants
                })

        return anomalies

    @staticmethod
    def analyze_temporal_patterns(metadata_list: List[Dict]) -> Dict:
        """
        Analyze temporal patterns in document creation

        Args:
            metadata_list: List of metadata

        Returns:
            Temporal analysis
        """
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        weekly_distribution = defaultdict(int)

        for metadata in metadata_list:
            date_created = metadata.get('date_created')
            if not date_created:
                continue

            try:
                dt = datetime.fromisoformat(date_created)
                hourly_distribution[dt.hour] += 1
                daily_distribution[dt.strftime('%A')] += 1
                weekly_distribution[dt.strftime('%Y-W%W')] += 1
            except (ValueError, AttributeError):
                continue

        return {
            "by_hour": dict(sorted(hourly_distribution.items())),
            "by_day_of_week": dict(daily_distribution),
            "by_week": dict(sorted(weekly_distribution.items())),
            "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0]
            if hourly_distribution else None,
            "peak_day": max(daily_distribution.items(), key=lambda x: x[1])[0]
            if daily_distribution else None
        }


class MetadataQualityAssessment:
    """Assesses metadata completeness and quality"""

    @staticmethod
    def assess_metadata_completeness(metadata_list: List[Dict]) -> Dict:
        """
        Evaluate completeness of metadata fields

        Args:
            metadata_list: List of metadata

        Returns:
            Completeness report
        """
        required_fields = [
            'document_id', 'document_type', 'date_created',
            'author', 'size_bytes'
        ]

        optional_fields = [
            'title', 'custodian', 'participants', 'hash_value'
        ]

        if not metadata_list:
            return {}

        field_completeness = {}

        for field in required_fields + optional_fields:
            populated = sum(1 for m in metadata_list if m.get(field))
            completeness = populated / len(metadata_list) * 100
            field_completeness[field] = {
                "populated": populated,
                "total": len(metadata_list),
                "percentage": round(completeness, 1)
            }

        # Overall completeness
        required_populated = sum(
            field_completeness[f]["populated"] for f in required_fields
        )
        required_total = len(required_fields) * len(metadata_list)
        overall = required_populated / required_total * 100 if required_total > 0 else 0

        return {
            "field_completeness": field_completeness,
            "overall_completeness": round(overall, 1),
            "quality_assessment": "complete" if overall > 90 else "partial"
            if overall > 70 else "incomplete"
        }

    @staticmethod
    def validate_metadata(metadata: Dict) -> List[str]:
        """
        Validate individual metadata record

        Args:
            metadata: Metadata dictionary

        Returns:
            List of validation errors
        """
        errors = []

        # Required fields
        if not metadata.get('document_id'):
            errors.append("Missing document_id")

        if not metadata.get('document_type'):
            errors.append("Missing document_type")

        # Date validation
        date_created = metadata.get('date_created')
        if date_created:
            try:
                datetime.fromisoformat(date_created)
            except (ValueError, TypeError):
                errors.append(f"Invalid date_created format: {date_created}")

        # Size validation
        size = metadata.get('size_bytes', 0)
        if not isinstance(size, int) or size < 0:
            errors.append("Invalid size_bytes")

        # Email validation for emails
        if metadata.get('document_type') == 'Email':
            author = metadata.get('author')
            if author and '@' not in str(author):
                errors.append("Invalid email format in author field")

        return errors


# Example usage
if __name__ == "__main__":
    # Sample metadata
    metadata = [
        {
            "document_id": 1,
            "document_type": "Email",
            "author": "john@company.com",
            "participants": ["john@company.com", "manager@company.com"],
            "date_created": "2024-01-15T10:30:00",
            "size_bytes": 5000,
            "custodian": "john@company.com"
        },
        {
            "document_id": 2,
            "document_type": "Email",
            "author": "manager@company.com",
            "participants": ["john@company.com", "manager@company.com", "legal@company.com"],
            "date_created": "2024-01-15T11:00:00",
            "size_bytes": 3000,
            "custodian": "manager@company.com"
        },
    ]

    analyzer = MetadataAnalyzer()
    patterns = analyzer.analyze_communication_patterns(metadata)

    print("Communication Patterns:")
    print(f"  Top Senders: {patterns['top_senders']}")
    print(f"  Most Frequent Pairs: {patterns['most_frequent_pairs'][:2]}")
