"""
Load File Reconciliation Example
Demonstrates comparing and reconciling load files
"""

from typing import List, Dict, Set, Tuple
import difflib

class LoadFileReconciler:
    """Reconciles and compares load files"""

    def __init__(self, file1_documents: List[Dict],
                 file2_documents: List[Dict]):
        """
        Initialize reconciler with two load files

        Args:
            file1_documents: First set of documents
            file2_documents: Second set of documents
        """
        self.file1 = file1_documents
        self.file2 = file2_documents
        self.reconciliation_report = None

    def reconcile_documents(self, key_field: str = 'DocumentID') -> Dict:
        """
        Reconcile documents between two load files

        Args:
            key_field: Field to use as unique identifier

        Returns:
            Reconciliation report
        """
        # Build document maps
        file1_map = {doc.get(key_field): doc for doc in self.file1}
        file2_map = {doc.get(key_field): doc for doc in self.file2}

        # Find differences
        only_in_file1 = set(file1_map.keys()) - set(file2_map.keys())
        only_in_file2 = set(file2_map.keys()) - set(file2_map.keys())
        in_both = set(file1_map.keys()) & set(file2_map.keys())

        # Find field differences in common documents
        field_differences = []
        for doc_id in in_both:
            doc1 = file1_map[doc_id]
            doc2 = file2_map[doc_id]

            for field in set(list(doc1.keys()) + list(doc2.keys())):
                val1 = doc1.get(field)
                val2 = doc2.get(field)

                if val1 != val2:
                    field_differences.append({
                        "document_id": doc_id,
                        "field": field,
                        "file1_value": val1,
                        "file2_value": val2
                    })

        self.reconciliation_report = {
            "file1_total": len(self.file1),
            "file2_total": len(self.file2),
            "documents_in_both": len(in_both),
            "only_in_file1": list(only_in_file1),
            "only_in_file2": list(only_in_file2),
            "field_differences": field_differences,
            "reconciliation_status": "complete" if not only_in_file1 and not only_in_file2
            and not field_differences else "issues_found"
        }

        return self.reconciliation_report

    def get_reconciliation_summary(self) -> Dict:
        """
        Get summary of reconciliation results

        Returns:
            Summary statistics
        """
        if not self.reconciliation_report:
            return {}

        report = self.reconciliation_report

        return {
            "total_documents_file1": report['file1_total'],
            "total_documents_file2": report['file2_total'],
            "matching_documents": report['documents_in_both'],
            "missing_from_file2": len(report['only_in_file1']),
            "extra_in_file2": len(report['only_in_file2']),
            "field_discrepancies": len(report['field_differences']),
            "match_percentage": round(
                report['documents_in_both'] / max(report['file1_total'], report['file2_total']) * 100, 1
            ) if max(report['file1_total'], report['file2_total']) > 0 else 0,
            "status": report['reconciliation_status']
        }

    def generate_exception_report(self) -> Dict:
        """
        Generate report of exceptions found

        Returns:
            Detailed exception report
        """
        if not self.reconciliation_report:
            return {}

        report = self.reconciliation_report
        exceptions = {
            "missing_documents": [
                {
                    "document_id": doc_id,
                    "missing_from": "file2",
                    "status": "document_not_produced"
                }
                for doc_id in report['only_in_file1']
            ],
            "extra_documents": [
                {
                    "document_id": doc_id,
                    "extra_in": "file2",
                    "status": "unexpected_document"
                }
                for doc_id in report['only_in_file2']
            ],
            "field_discrepancies": report['field_differences']
        }

        return {
            "total_exceptions": (len(exceptions['missing_documents']) +
                               len(exceptions['extra_documents']) +
                               len(exceptions['field_discrepancies'])),
            "exceptions": exceptions
        }


class LoadFileComparator:
    """Compares specific fields across load files"""

    @staticmethod
    def compare_field_values(documents1: List[Dict],
                            documents2: List[Dict],
                            field_name: str,
                            key_field: str = 'DocumentID') -> Dict:
        """
        Compare values of specific field between load files

        Args:
            documents1: First document set
            documents2: Second document set
            field_name: Field to compare
            key_field: Unique identifier field

        Returns:
            Comparison results
        """
        map1 = {doc.get(key_field): doc.get(field_name) for doc in documents1}
        map2 = {doc.get(key_field): doc.get(field_name) for doc in documents2}

        mismatches = []
        for doc_id in set(map1.keys()) & set(map2.keys()):
            if map1[doc_id] != map2[doc_id]:
                mismatches.append({
                    "document_id": doc_id,
                    "file1_value": map1[doc_id],
                    "file2_value": map2[doc_id]
                })

        return {
            "field": field_name,
            "total_compared": len(set(map1.keys()) & set(map2.keys())),
            "matching": len(set(map1.keys()) & set(map2.keys())) - len(mismatches),
            "mismatches": len(mismatches),
            "mismatch_details": mismatches,
            "match_rate": round(
                (len(set(map1.keys()) & set(map2.keys())) - len(mismatches)) /
                max(len(set(map1.keys()) & set(map2.keys())), 1) * 100, 1
            )
        }

    @staticmethod
    def verify_field_consistency(documents: List[Dict],
                                field_name: str) -> Dict:
        """
        Verify consistency of field values within single load file

        Args:
            documents: Documents to check
            field_name: Field to verify

        Returns:
            Consistency report
        """
        from collections import Counter

        values = [doc.get(field_name) for doc in documents]
        value_counts = Counter(values)

        most_common = value_counts.most_common(5)

        return {
            "field": field_name,
            "total_documents": len(documents),
            "unique_values": len(value_counts),
            "most_common_values": [
                {"value": v, "count": c, "percentage": round(c/len(documents)*100, 1)}
                for v, c in most_common
            ],
            "consistency_assessment": "consistent" if len(value_counts) <= 5
            else "varied" if len(value_counts) <= 20 else "highly_varied"
        }


class DataValidationFramework:
    """Framework for validating load file data"""

    @staticmethod
    def validate_range(documents: List[Dict],
                       field_name: str,
                       min_value=None,
                       max_value=None) -> Dict:
        """
        Validate field values are within range

        Args:
            documents: Documents to validate
            field_name: Field to validate
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value

        Returns:
            Validation results
        """
        violations = []

        for doc in documents:
            value = doc.get(field_name)

            try:
                num_value = float(value) if value else None
                if num_value is None:
                    continue

                if min_value is not None and num_value < min_value:
                    violations.append({
                        "document_id": doc.get('DocumentID'),
                        "field": field_name,
                        "value": value,
                        "violation": f"below minimum ({min_value})"
                    })

                if max_value is not None and num_value > max_value:
                    violations.append({
                        "document_id": doc.get('DocumentID'),
                        "field": field_name,
                        "value": value,
                        "violation": f"above maximum ({max_value})"
                    })
            except (ValueError, TypeError):
                violations.append({
                    "document_id": doc.get('DocumentID'),
                    "field": field_name,
                    "value": value,
                    "violation": "non-numeric value"
                })

        return {
            "field": field_name,
            "total_documents": len(documents),
            "violations": len(violations),
            "validation_status": "pass" if not violations else "fail",
            "details": violations[:10]  # Limit to first 10
        }

    @staticmethod
    def validate_required_values(documents: List[Dict],
                                required_fields: List[str]) -> Dict:
        """
        Validate required fields have values

        Args:
            documents: Documents to validate
            required_fields: Fields that must be populated

        Returns:
            Validation results
        """
        violations = []

        for doc in documents:
            for field in required_fields:
                if field not in doc or not doc[field]:
                    violations.append({
                        "document_id": doc.get('DocumentID'),
                        "field": field,
                        "violation": "missing_required_value"
                    })

        return {
            "required_fields": required_fields,
            "total_documents": len(documents),
            "violations": len(violations),
            "validation_status": "pass" if not violations else "fail",
            "violation_details": violations[:10]
        }


# Example usage
if __name__ == "__main__":
    # Sample data
    file1 = [
        {"DocumentID": "001", "Author": "john@company.com", "Pages": "1"},
        {"DocumentID": "002", "Author": "jane@company.com", "Pages": "3"}
    ]

    file2 = [
        {"DocumentID": "001", "Author": "john@company.com", "Pages": "1"},
        {"DocumentID": "002", "Author": "jane@company.com", "Pages": "5"}  # Mismatch
    ]

    reconciler = LoadFileReconciler(file1, file2)
    report = reconciler.reconcile_documents()

    summary = reconciler.get_reconciliation_summary()
    print(f"Reconciliation: {summary['match_percentage']}% match")
    print(f"Field Discrepancies: {summary['field_discrepancies']}")

    if report['field_differences']:
        print(f"Differences found: {report['field_differences']}")
