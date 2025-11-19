"""
Compliance and Defensibility Example
Demonstrates ensuring compliant and defensible e-discovery processes
"""

from typing import List, Dict, Optional
from datetime import datetime
import json

class ComplianceFramework:
    """Manages compliance requirements for e-discovery"""

    def __init__(self):
        """Initialize compliance framework"""
        self.compliance_requirements = {
            "federal": [
                "FRCP Rule 26 - Proportionality",
                "FRCP Rule 33 - Interrogatories",
                "FRCP Rule 34 - Document Production"
            ],
            "state": [
                "State-specific discovery rules",
                "Local court rules"
            ],
            "industry": [
                "HIPAA - Healthcare data",
                "GLBA - Financial data",
                "CCPA - Consumer privacy"
            ]
        }
        self.compliance_documentation = {}

    def assess_compliance_requirements(self, case_jurisdiction: str,
                                      industry_type: str = None) -> Dict:
        """
        Assess applicable compliance requirements

        Args:
            case_jurisdiction: Court jurisdiction
            industry_type: Industry type if applicable

        Returns:
            Applicable requirements
        """
        requirements = {
            "federal_rules": self.compliance_requirements["federal"],
            "jurisdiction_rules": f"Rules applicable to {case_jurisdiction}",
            "applicable_requirements": []
        }

        # Add industry-specific requirements
        if industry_type == "healthcare":
            requirements["applicable_requirements"].extend([
                "HIPAA Compliance",
                "HITECH Act",
                "Patient Privacy Protection"
            ])
        elif industry_type == "financial":
            requirements["applicable_requirements"].extend([
                "GLBA Compliance",
                "SOX Requirements",
                "Financial Privacy Rules"
            ])

        return requirements

    def document_methodology(self, methodology_description: str) -> Dict:
        """
        Document e-discovery methodology for defensibility

        Args:
            methodology_description: Description of process

        Returns:
            Methodology documentation record
        """
        doc_id = len(self.compliance_documentation) + 1

        documentation = {
            "id": doc_id,
            "date_documented": datetime.now().isoformat(),
            "methodology": methodology_description,
            "documented_by": "E-Discovery Team",
            "approval_status": "pending_review",
            "document_type": "Methodology"
        }

        self.compliance_documentation[doc_id] = documentation
        return documentation


class DefensibilityChecker:
    """Evaluates defensibility of e-discovery processes"""

    @staticmethod
    def evaluate_collection_defensibility(collection_details: Dict) -> Dict:
        """
        Evaluate defensibility of collection methodology

        Args:
            collection_details: Details about collection process

        Returns:
            Defensibility assessment
        """
        checklist = {
            "documented_methodology": bool(collection_details.get('methodology')),
            "defined_scope": bool(collection_details.get('scope')),
            "identified_custodians": bool(collection_details.get('custodians')),
            "chain_of_custody": bool(collection_details.get('chain_of_custody')),
            "hash_verification": bool(collection_details.get('hash_verification')),
            "collection_certification": bool(collection_details.get('certification')),
            "litigation_hold_proper": bool(collection_details.get('hold_compliance')),
            "search_term_tested": bool(collection_details.get('search_testing'))
        }

        # Calculate defensibility score
        passed = sum(1 for v in checklist.values() if v)
        total = len(checklist)
        score = (passed / total * 100) if total > 0 else 0

        return {
            "defensibility_score": round(score, 1),
            "assessment": "defensible" if score >= 80 else "questionable" if score >= 60 else "indefensible",
            "checklist": checklist,
            "gaps": [k for k, v in checklist.items() if not v],
            "recommendations": DefensibilityChecker._get_recommendations(checklist)
        }

    @staticmethod
    def evaluate_review_defensibility(review_details: Dict) -> Dict:
        """
        Evaluate defensibility of review process

        Args:
            review_details: Review process details

        Returns:
            Review defensibility assessment
        """
        checklist = {
            "review_protocol_documented": bool(review_details.get('protocol')),
            "reviewer_training_documented": bool(review_details.get('training')),
            "quality_assurance_performed": bool(review_details.get('qa_samples')),
            "privilege_log_maintained": bool(review_details.get('privilege_log')),
            "workflow_tracked": bool(review_details.get('workflow_log')),
            "supervisor_review": bool(review_details.get('supervisor_approval')),
            "audit_trail_preserved": bool(review_details.get('audit_trail')),
            "tar_methodology_documented": bool(review_details.get('tar_documentation'))
        }

        passed = sum(1 for v in checklist.values() if v)
        total = len(checklist)
        score = (passed / total * 100) if total > 0 else 0

        return {
            "defensibility_score": round(score, 1),
            "assessment": "defensible" if score >= 80 else "questionable" if score >= 60 else "needs_improvement",
            "checklist": checklist,
            "gaps": [k for k, v in checklist.items() if not v]
        }

    @staticmethod
    def _get_recommendations(checklist: Dict) -> List[str]:
        """Generate recommendations based on gaps"""
        recommendations = []

        gaps = [k for k, v in checklist.items() if not v]

        if 'documented_methodology' in gaps:
            recommendations.append("Document collection methodology comprehensively")

        if 'hash_verification' in gaps:
            recommendations.append("Implement hash verification for all collected documents")

        if 'chain_of_custody' in gaps:
            recommendations.append("Create and maintain chain of custody documentation")

        if 'search_term_tested' in gaps:
            recommendations.append("Test all search terms for effectiveness and precision")

        return recommendations


class AuditTrail:
    """Maintains audit trail for e-discovery activities"""

    def __init__(self):
        """Initialize audit trail"""
        self.events = []

    def log_event(self, event_type: str, description: str,
                 user: str, document_id: str = None) -> Dict:
        """
        Log an e-discovery event

        Args:
            event_type: Type of event (collection, review, production, etc.)
            description: Event description
            user: User performing action
            document_id: Document affected

        Returns:
            Event record
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "user": user,
            "document_id": document_id,
            "event_id": len(self.events) + 1
        }

        self.events.append(event)
        return event

    def get_audit_report(self, start_date: str = None,
                        end_date: str = None) -> Dict:
        """
        Generate audit trail report

        Args:
            start_date: Filter from date (ISO format)
            end_date: Filter to date (ISO format)

        Returns:
            Audit report
        """
        filtered_events = self.events

        if start_date:
            filtered_events = [e for e in filtered_events if e['timestamp'] >= start_date]

        if end_date:
            filtered_events = [e for e in filtered_events if e['timestamp'] <= end_date]

        # Summarize by event type
        event_summary = {}
        for event in filtered_events:
            event_type = event['event_type']
            event_summary[event_type] = event_summary.get(event_type, 0) + 1

        return {
            "total_events": len(filtered_events),
            "event_types": event_summary,
            "events": filtered_events
        }

    def verify_integrity(self) -> Dict:
        """
        Verify audit trail integrity

        Returns:
            Integrity check results
        """
        issues = []

        # Check for missing event IDs
        event_ids = [e.get('event_id') for e in self.events]
        if len(event_ids) != len(set(event_ids)):
            issues.append("Duplicate event IDs detected")

        # Check timestamp order
        for i in range(1, len(self.events)):
            prev_time = self.events[i-1]['timestamp']
            curr_time = self.events[i]['timestamp']
            if curr_time < prev_time:
                issues.append(f"Timestamp out of order at event {i}")

        return {
            "total_events": len(self.events),
            "integrity_status": "intact" if not issues else "compromised",
            "issues": issues
        }


class DocumentationFramework:
    """Manages required documentation for compliance"""

    def __init__(self):
        """Initialize documentation framework"""
        self.documents = {}

    def add_documentation(self, doc_type: str, title: str,
                         content: str) -> Dict:
        """
        Add documentation record

        Args:
            doc_type: Type of documentation
            title: Document title
            content: Document content

        Returns:
            Documentation record
        """
        doc_id = len(self.documents) + 1

        doc_record = {
            "id": doc_id,
            "type": doc_type,
            "title": title,
            "content": content,
            "date_created": datetime.now().isoformat(),
            "status": "active"
        }

        self.documents[doc_id] = doc_record
        return doc_record

    def get_required_documentation_checklist(self) -> List[Dict]:
        """
        Get checklist of required documentation

        Returns:
            List of required documentation items
        """
        required_docs = [
            {
                "type": "Litigation Hold Notice",
                "description": "Notice to preserve documents",
                "required": True
            },
            {
                "type": "Collection Protocol",
                "description": "Documented collection methodology",
                "required": True
            },
            {
                "type": "Privilege Log",
                "description": "Log of withheld privileged documents",
                "required": True
            },
            {
                "type": "Production Specifications",
                "description": "Specifications for document production",
                "required": True
            },
            {
                "type": "QA Report",
                "description": "Quality assurance review results",
                "required": True
            },
            {
                "type": "Search Term Documentation",
                "description": "Search terms and testing results",
                "required": True
            },
            {
                "type": "Privilege Waiver Log",
                "description": "Log of any inadvertent disclosures",
                "required": False
            },
            {
                "type": "Deduplication Report",
                "description": "Documentation of duplicate handling",
                "required": True
            }
        ]

        return required_docs

    def verify_documentation_completeness(self) -> Dict:
        """
        Verify all required documentation is complete

        Returns:
            Completeness verification results
        """
        required = self.get_required_documentation_checklist()
        doc_types = {doc['type'] for doc in self.documents.values()}

        missing = []
        for req_doc in required:
            if req_doc['required'] and req_doc['type'] not in doc_types:
                missing.append(req_doc['type'])

        return {
            "total_required": len([r for r in required if r['required']]),
            "completed": len(doc_types),
            "missing": missing,
            "status": "complete" if not missing else "incomplete"
        }


# Example usage
if __name__ == "__main__":
    framework = ComplianceFramework()

    # Assess requirements
    requirements = framework.assess_compliance_requirements(
        case_jurisdiction="Federal Court",
        industry_type="healthcare"
    )

    print(f"Applicable Requirements: {requirements['applicable_requirements']}")

    # Check defensibility
    collection_details = {
        "methodology": "Described collection process",
        "scope": "Defined scope",
        "custodians": "Identified custodians",
        "chain_of_custody": "Maintained chain of custody",
        "hash_verification": "Verified hashes"
    }

    defensibility = DefensibilityChecker.evaluate_collection_defensibility(collection_details)
    print(f"Defensibility Score: {defensibility['defensibility_score']}%")
    print(f"Assessment: {defensibility['assessment']}")

    if defensibility['gaps']:
        print(f"Gaps: {defensibility['gaps']}")
