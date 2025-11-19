"""
Document Analytics and Reporting Example
Demonstrates analytics and comprehensive reporting
"""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime
import json

class DocumentAnalytics:
    """Provides analytics on document collections"""

    @staticmethod
    def calculate_collection_statistics(documents: List[Dict]) -> Dict:
        """
        Calculate comprehensive collection statistics

        Args:
            documents: List of documents

        Returns:
            Statistics dictionary
        """
        if not documents:
            return {}

        # Basic counts
        total_docs = len(documents)
        total_size = sum(doc.get('size_bytes', 0) for doc in documents)

        # Document types
        doc_types = defaultdict(int)
        for doc in documents:
            doc_type = doc.get('FileType', 'Unknown')
            doc_types[doc_type] += 1

        # Date range
        dates = [doc.get('DateCreated') for doc in documents if doc.get('DateCreated')]
        earliest_date = min(dates) if dates else None
        latest_date = max(dates) if dates else None

        # Custodians
        custodians = set(doc.get('Custodian') for doc in documents if doc.get('Custodian'))

        # Responsiveness
        responsive_count = len([d for d in documents if d.get('Responsive') == 'Responsive'])
        privileged_count = len([d for d in documents if d.get('Privilege') != 'No'])

        return {
            "total_documents": total_docs,
            "total_size_bytes": total_size,
            "average_size_bytes": total_size / total_docs if total_docs > 0 else 0,
            "document_types": dict(doc_types),
            "unique_document_types": len(doc_types),
            "earliest_date": earliest_date,
            "latest_date": latest_date,
            "date_range_days": (datetime.fromisoformat(latest_date) -
                              datetime.fromisoformat(earliest_date)).days if latest_date and earliest_date else 0,
            "unique_custodians": len(custodians),
            "responsive_documents": responsive_count,
            "responsive_percentage": round(responsive_count / total_docs * 100, 1) if total_docs > 0 else 0,
            "privileged_documents": privileged_count,
            "privilege_percentage": round(privileged_count / total_docs * 100, 1) if total_docs > 0 else 0
        }

    @staticmethod
    def analyze_custodian_data(documents: List[Dict]) -> Dict:
        """
        Analyze documents by custodian

        Args:
            documents: List of documents

        Returns:
            Custodian analysis
        """
        custodian_stats = defaultdict(lambda: {
            "document_count": 0,
            "total_size": 0,
            "file_types": defaultdict(int),
            "responsive_count": 0,
            "date_range": {"min": None, "max": None}
        })

        for doc in documents:
            custodian = doc.get('Custodian', 'Unknown')
            stats = custodian_stats[custodian]

            stats["document_count"] += 1
            stats["total_size"] += doc.get('size_bytes', 0)
            stats["file_types"][doc.get('FileType', 'Unknown')] += 1

            if doc.get('Responsive') == 'Responsive':
                stats["responsive_count"] += 1

            date = doc.get('DateCreated')
            if date:
                if not stats["date_range"]["min"] or date < stats["date_range"]["min"]:
                    stats["date_range"]["min"] = date
                if not stats["date_range"]["max"] or date > stats["date_range"]["max"]:
                    stats["date_range"]["max"] = date

        # Convert defaultdict to regular dict
        result = {}
        for custodian, stats in custodian_stats.items():
            result[custodian] = {
                "document_count": stats["document_count"],
                "total_size_bytes": stats["total_size"],
                "average_size_bytes": stats["total_size"] / stats["document_count"]
                if stats["document_count"] > 0 else 0,
                "file_types": dict(stats["file_types"]),
                "responsive_count": stats["responsive_count"],
                "responsive_percentage": round(
                    stats["responsive_count"] / stats["document_count"] * 100, 1
                ) if stats["document_count"] > 0 else 0,
                "date_range": stats["date_range"]
            }

        return result

    @staticmethod
    def analyze_time_distribution(documents: List[Dict]) -> Dict:
        """
        Analyze distribution of documents over time

        Args:
            documents: List of documents

        Returns:
            Time distribution analysis
        """
        monthly_counts = defaultdict(int)
        yearly_counts = defaultdict(int)

        for doc in documents:
            date = doc.get('DateCreated')
            if date:
                dt = datetime.fromisoformat(date)
                month_key = dt.strftime('%Y-%m')
                year_key = dt.strftime('%Y')

                monthly_counts[month_key] += 1
                yearly_counts[year_key] += 1

        return {
            "by_month": dict(sorted(monthly_counts.items())),
            "by_year": dict(sorted(yearly_counts.items())),
            "peak_month": max(monthly_counts.items(), key=lambda x: x[1])[0]
            if monthly_counts else None,
            "peak_year": max(yearly_counts.items(), key=lambda x: x[1])[0]
            if yearly_counts else None
        }


class ReportGenerator:
    """Generates comprehensive reports"""

    @staticmethod
    def generate_executive_summary(documents: List[Dict]) -> str:
        """
        Generate executive summary report

        Args:
            documents: List of documents

        Returns:
            Summary report text
        """
        stats = DocumentAnalytics.calculate_collection_statistics(documents)

        summary = f"""
EXECUTIVE SUMMARY - E-DISCOVERY COLLECTION

Collection Overview:
- Total Documents: {stats['total_documents']:,}
- Collection Date: {datetime.now().strftime('%Y-%m-%d')}
- Date Range: {stats['earliest_date']} to {stats['latest_date']}
- Total Data Volume: {stats['total_size_bytes'] / (1024**3):.2f} GB

Key Metrics:
- Unique Custodians: {stats['unique_custodians']}
- Document Types: {stats['unique_document_types']}
- Responsive Documents: {stats['responsive_documents']:,} ({stats['responsive_percentage']}%)
- Privileged Documents: {stats['privileged_documents']:,} ({stats['privilege_percentage']}%)

Next Steps:
1. Processing and normalization
2. Deduplication and threading
3. Early case assessment
4. Technology-assisted review implementation
"""
        return summary

    @staticmethod
    def generate_detailed_report(documents: List[Dict]) -> Dict:
        """
        Generate detailed analytics report

        Args:
            documents: List of documents

        Returns:
            Detailed report dictionary
        """
        return {
            "report_date": datetime.now().isoformat(),
            "collection_statistics": DocumentAnalytics.calculate_collection_statistics(documents),
            "custodian_analysis": DocumentAnalytics.analyze_custodian_data(documents),
            "time_distribution": DocumentAnalytics.analyze_time_distribution(documents)
        }

    @staticmethod
    def generate_json_report(documents: List[Dict],
                            output_path: str) -> bool:
        """
        Generate JSON format report

        Args:
            documents: List of documents
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            report = ReportGenerator.generate_detailed_report(documents)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            return True
        except IOError as e:
            print(f"Error writing report: {e}")
            return False


class VisualizationDataProvider:
    """Provides data formatted for visualization"""

    @staticmethod
    def get_timeline_data(documents: List[Dict]) -> List[Dict]:
        """
        Get data for timeline visualization

        Args:
            documents: List of documents

        Returns:
            Timeline data points
        """
        from collections import defaultdict

        timeline = defaultdict(int)

        for doc in documents:
            date = doc.get('DateCreated')
            if date:
                date_only = date.split('T')[0]
                timeline[date_only] += 1

        return [
            {"date": date, "count": count}
            for date, count in sorted(timeline.items())
        ]

    @staticmethod
    def get_custodian_distribution(documents: List[Dict]) -> List[Dict]:
        """
        Get data for custodian distribution chart

        Args:
            documents: List of documents

        Returns:
            Custodian distribution data
        """
        from collections import Counter

        custodians = Counter(doc.get('Custodian', 'Unknown') for doc in documents)

        return [
            {"custodian": custodian, "count": count}
            for custodian, count in custodians.most_common(20)
        ]

    @staticmethod
    def get_file_type_distribution(documents: List[Dict]) -> List[Dict]:
        """
        Get data for file type distribution

        Args:
            documents: List of documents

        Returns:
            File type distribution data
        """
        from collections import Counter

        file_types = Counter(doc.get('FileType', 'Unknown') for doc in documents)

        return [
            {"file_type": ftype, "count": count, "percentage": round(count/len(documents)*100, 1)}
            for ftype, count in file_types.most_common()
        ]


# Example usage
if __name__ == "__main__":
    docs = [
        {
            "DocumentID": 1,
            "Custodian": "john@company.com",
            "DateCreated": "2024-01-15T10:00:00",
            "FileType": "Email",
            "Responsive": "Responsive",
            "size_bytes": 5000
        },
        {
            "DocumentID": 2,
            "Custodian": "jane@company.com",
            "DateCreated": "2024-01-16T14:00:00",
            "FileType": "Document",
            "Responsive": "Non-Responsive",
            "size_bytes": 50000
        }
    ]

    stats = DocumentAnalytics.calculate_collection_statistics(docs)
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Responsive %: {stats['responsive_percentage']}%")

    summary = ReportGenerator.generate_executive_summary(docs)
    print(summary)
