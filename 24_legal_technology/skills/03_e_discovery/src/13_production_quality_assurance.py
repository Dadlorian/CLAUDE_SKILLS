"""
Production Quality Assurance Example
Demonstrates QA procedures for document production
"""

from typing import List, Dict, Tuple
import random
from collections import defaultdict

class ProductionQAValidator:
    """Validates production quality and completeness"""

    def __init__(self, sample_size: int = 100):
        """
        Initialize QA validator

        Args:
            sample_size: Number of documents to sample for QA
        """
        self.sample_size = sample_size
        self.qa_results = []

    def perform_qa_review(self, production_documents: List[Dict],
                         sample_size: int = None) -> Dict:
        """
        Perform quality assurance review on production

        Args:
            production_documents: Full list of documents being produced
            sample_size: Number of documents to sample (uses default if None)

        Returns:
            QA results and recommendations
        """
        if sample_size is None:
            sample_size = min(self.sample_size, len(production_documents))

        # Random sample
        sample = random.sample(production_documents, min(sample_size, len(production_documents)))

        qa_checks = {
            "completeness": self._check_completeness(sample),
            "metadata_accuracy": self._check_metadata_accuracy(sample),
            "file_integrity": self._check_file_integrity(sample),
            "bates_numbering": self._check_bates_numbering(sample),
            "privilege_markings": self._check_privilege_markings(sample),
            "redaction_quality": self._check_redactions(sample)
        }

        # Calculate pass rate
        total_issues = sum(len(v.get('issues', [])) for v in qa_checks.values())
        pass_rate = max(0, 100 - (total_issues / len(sample) * 100)) if sample else 100

        return {
            "sample_size": len(sample),
            "total_universe": len(production_documents),
            "pass_rate": round(pass_rate, 1),
            "checks": qa_checks,
            "recommendation": "PASS" if pass_rate >= 95 else "REVIEW"
        }

    @staticmethod
    def _check_completeness(sample: List[Dict]) -> Dict:
        """Check document completeness"""
        required_fields = ['DocumentID', 'Author', 'DateCreated', 'Pages']
        issues = []

        for doc in sample:
            for field in required_fields:
                if field not in doc or not doc[field]:
                    issues.append({
                        "document_id": doc.get('DocumentID'),
                        "issue_type": "missing_field",
                        "field": field
                    })

        return {
            "total_checks": len(sample) * len(required_fields),
            "passed": len(sample) * len(required_fields) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _check_metadata_accuracy(sample: List[Dict]) -> Dict:
        """Check metadata accuracy and formatting"""
        issues = []

        for doc in sample:
            # Check date format
            date_created = doc.get('DateCreated')
            if date_created and not ProductionQAValidator._is_valid_date(date_created):
                issues.append({
                    "document_id": doc.get('DocumentID'),
                    "issue_type": "invalid_date_format",
                    "field": "DateCreated",
                    "value": date_created
                })

            # Check page count
            try:
                pages = int(doc.get('Pages', 0))
                if pages <= 0:
                    issues.append({
                        "document_id": doc.get('DocumentID'),
                        "issue_type": "invalid_page_count",
                        "value": pages
                    })
            except (ValueError, TypeError):
                issues.append({
                    "document_id": doc.get('DocumentID'),
                    "issue_type": "non_numeric_pages"
                })

        return {
            "total_checks": len(sample),
            "passed": len(sample) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _check_file_integrity(sample: List[Dict]) -> Dict:
        """Check file presence and integrity"""
        issues = []

        for doc in sample:
            image_file = doc.get('ImageFileName')
            native_file = doc.get('NativeFileName')

            # At least one file should be present
            if not image_file and not native_file:
                issues.append({
                    "document_id": doc.get('DocumentID'),
                    "issue_type": "no_files_present"
                })

        return {
            "total_checks": len(sample),
            "passed": len(sample) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _check_bates_numbering(sample: List[Dict]) -> Dict:
        """Check Bates numbering consistency"""
        issues = []
        bates_numbers = []

        for doc in sample:
            bates = doc.get('BatesNumber')
            if not bates:
                issues.append({
                    "document_id": doc.get('DocumentID'),
                    "issue_type": "missing_bates"
                })
            else:
                bates_numbers.append(bates)

        # Check for duplicates
        if len(bates_numbers) != len(set(bates_numbers)):
            duplicate_bates = [b for b in bates_numbers if bates_numbers.count(b) > 1]
            for bates in set(duplicate_bates):
                issues.append({
                    "issue_type": "duplicate_bates",
                    "bates_number": bates
                })

        return {
            "total_checks": len(sample),
            "passed": len(sample) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _check_privilege_markings(sample: List[Dict]) -> Dict:
        """Check privilege designations"""
        issues = []

        for doc in sample:
            privilege = doc.get('Privilege', 'No')

            # If marked privileged, should have privilege log entry
            if privilege.lower() != 'no':
                privilege_log_entry = doc.get('PrivilegeLogEntry')
                if not privilege_log_entry:
                    issues.append({
                        "document_id": doc.get('DocumentID'),
                        "issue_type": "privileged_without_log_entry",
                        "privilege": privilege
                    })

        return {
            "total_checks": len(sample),
            "passed": len(sample) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _check_redactions(sample: List[Dict]) -> Dict:
        """Check redaction quality and visibility"""
        issues = []

        for doc in sample:
            has_redactions = doc.get('HasRedactions', 'No').lower() == 'yes'

            if has_redactions:
                redaction_reason = doc.get('RedactionReason')
                if not redaction_reason:
                    issues.append({
                        "document_id": doc.get('DocumentID'),
                        "issue_type": "redacted_without_reason"
                    })

                # Check redaction marking
                redaction_visible = doc.get('RedactionVisible', 'Yes').lower() == 'yes'
                if not redaction_visible:
                    issues.append({
                        "document_id": doc.get('DocumentID'),
                        "issue_type": "invisible_redaction"
                    })

        return {
            "total_checks": len(sample),
            "passed": len(sample) - len(issues),
            "issues": issues
        }

    @staticmethod
    def _is_valid_date(date_string: str) -> bool:
        """Validate date format"""
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]
        for fmt in formats:
            try:
                from datetime import datetime
                datetime.strptime(date_string, fmt)
                return True
            except (ValueError, TypeError):
                continue
        return False


class ProductionDeliverables:
    """Manages production deliverable documentation"""

    @staticmethod
    def generate_production_summary(documents: List[Dict],
                                   production_name: str) -> Dict:
        """
        Generate production summary report

        Args:
            documents: Produced documents
            production_name: Name of production

        Returns:
            Summary report
        """
        custodians = set()
        responsive_count = 0
        privileged_count = 0
        redacted_count = 0

        for doc in documents:
            if doc.get('Custodian'):
                custodians.add(doc['Custodian'])

            if doc.get('Responsive') == 'Responsive':
                responsive_count += 1

            if doc.get('Privilege') and doc.get('Privilege').lower() != 'no':
                privileged_count += 1

            if doc.get('HasRedactions', 'No').lower() == 'yes':
                redacted_count += 1

        return {
            "production_name": production_name,
            "date_generated": str(datetime.now().isoformat()),
            "total_documents": len(documents),
            "responsive_documents": responsive_count,
            "privileged_documents": privileged_count,
            "redacted_documents": redacted_count,
            "unique_custodians": len(custodians),
            "custodian_breakdown": {custodian: sum(1 for doc in documents if doc.get('Custodian') == custodian)
                                   for custodian in custodians}
        }

    @staticmethod
    def generate_privilege_log(documents: List[Dict]) -> List[Dict]:
        """
        Generate privilege log for privileged documents

        Args:
            documents: All produced documents

        Returns:
            Privilege log entries
        """
        privilege_log = []

        for doc in documents:
            if doc.get('Privilege') and doc.get('Privilege').lower() != 'no':
                entry = {
                    "document_id": doc.get('DocumentID'),
                    "bates_number": doc.get('BatesNumber'),
                    "privilege_type": doc.get('Privilege'),
                    "date": doc.get('DateCreated'),
                    "author": doc.get('Author'),
                    "recipients": ", ".join(doc.get('To', []) + doc.get('Cc', [])),
                    "subject": doc.get('Subject'),
                    "basis_for_assertion": doc.get('PrivilegeBasis', 'Legal advice sought/provided'),
                    "withheld": 'Yes'
                }
                privilege_log.append(entry)

        return privilege_log

    @staticmethod
    def generate_search_term_report(documents: List[Dict],
                                   search_terms: List[str]) -> Dict:
        """
        Generate report of search term hits

        Args:
            documents: Produced documents
            search_terms: List of search terms used

        Returns:
            Search term hit report
        """
        from collections import defaultdict

        hit_counts = defaultdict(int)

        for term in search_terms:
            term_lower = term.lower()
            for doc in documents:
                # Check in searchable fields
                searchable_text = " ".join([
                    str(doc.get('Subject', '')),
                    str(doc.get('Body', '')),
                    str(doc.get('Author', ''))
                ]).lower()

                if term_lower in searchable_text:
                    hit_counts[term] += 1

        return {
            "search_terms": [
                {
                    "term": term,
                    "hits": hit_counts[term],
                    "percentage": round(hit_counts[term] / len(documents) * 100, 1)
                }
                for term in search_terms
            ],
            "total_documents_searched": len(documents)
        }


from datetime import datetime

# Example usage
if __name__ == "__main__":
    # Sample production
    documents = [
        {
            "DocumentID": "001",
            "Author": "john@company.com",
            "DateCreated": "2024-01-15",
            "Pages": "1",
            "Responsive": "Responsive",
            "Privilege": "No",
            "HasRedactions": "No"
        }
    ]

    validator = ProductionQAValidator()
    qa_results = validator.perform_qa_review(documents, sample_size=1)

    print(f"QA Results: Pass Rate = {qa_results['pass_rate']}%")

    summary = ProductionDeliverables.generate_production_summary(documents, "Production 1")
    print(f"Summary: {summary['total_documents']} documents")
