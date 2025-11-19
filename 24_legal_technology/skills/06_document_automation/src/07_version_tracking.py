"""
Version Tracking and Change Management
Tracks document versions with metadata, history, and audit trails.

Dependencies: json, hashlib
Install: No additional dependencies required
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import hashlib
from pathlib import Path


class ApprovalStatus(Enum):
    """Document approval status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_NEGOTIATION = "in_negotiation"


@dataclass
class Revision:
    """Represents a document revision."""
    revision_number: int
    timestamp: str
    author: str
    description: str
    change_summary: str
    approval_status: ApprovalStatus
    approver: Optional[str] = None
    approval_date: Optional[str] = None
    content_hash: str = ""
    file_size: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['approval_status'] = self.approval_status.value
        return data


@dataclass
class AuditLog:
    """Audit log entry."""
    timestamp: str
    action: str
    user: str
    description: str
    revision_number: int
    details: Dict[str, Any]


class VersionManager:
    """Manages document versions with full audit trail."""

    def __init__(self, document_id: str, document_name: str):
        """Initialize version manager."""
        self.document_id = document_id
        self.document_name = document_name
        self.revisions: List[Revision] = []
        self.audit_logs: List[AuditLog] = []
        self.current_revision = 0
        self.creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def create_revision(self, content: str, author: str, description: str,
                       change_summary: str, notes: str = "") -> Revision:
        """Create new document revision."""
        self.current_revision += 1

        # Calculate content hash for integrity checking
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        file_size = len(content)

        revision = Revision(
            revision_number=self.current_revision,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            author=author,
            description=description,
            change_summary=change_summary,
            approval_status=ApprovalStatus.DRAFT,
            content_hash=content_hash,
            file_size=file_size,
            notes=notes
        )

        self.revisions.append(revision)

        # Log the action
        self._log_action(
            'REVISION_CREATED',
            author,
            f"Created revision {self.current_revision}",
            {
                'content_hash': content_hash,
                'file_size': file_size,
                'summary': change_summary
            }
        )

        return revision

    def submit_for_review(self, revision_number: int, submitter: str) -> bool:
        """Submit revision for review."""
        revision = self._get_revision(revision_number)
        if not revision:
            return False

        revision.approval_status = ApprovalStatus.PENDING_REVIEW

        self._log_action(
            'SUBMITTED_FOR_REVIEW',
            submitter,
            f"Submitted revision {revision_number} for review",
            {'status': 'pending_review'}
        )

        return True

    def approve_revision(self, revision_number: int, approver: str,
                        approval_notes: str = "") -> bool:
        """Approve a revision."""
        revision = self._get_revision(revision_number)
        if not revision:
            return False

        revision.approval_status = ApprovalStatus.APPROVED
        revision.approver = approver
        revision.approval_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        revision.notes = approval_notes

        self._log_action(
            'REVISION_APPROVED',
            approver,
            f"Approved revision {revision_number}",
            {
                'approved_by': approver,
                'approval_date': revision.approval_date,
                'notes': approval_notes
            }
        )

        return True

    def reject_revision(self, revision_number: int, reviewer: str,
                       rejection_reason: str) -> bool:
        """Reject a revision."""
        revision = self._get_revision(revision_number)
        if not revision:
            return False

        revision.approval_status = ApprovalStatus.REJECTED
        revision.notes = rejection_reason

        self._log_action(
            'REVISION_REJECTED',
            reviewer,
            f"Rejected revision {revision_number}",
            {
                'rejected_by': reviewer,
                'reason': rejection_reason
            }
        )

        return True

    def start_negotiation(self, revision_number: int, party: str) -> bool:
        """Mark revision as in negotiation."""
        revision = self._get_revision(revision_number)
        if not revision:
            return False

        revision.approval_status = ApprovalStatus.IN_NEGOTIATION

        self._log_action(
            'NEGOTIATION_STARTED',
            party,
            f"Revision {revision_number} moved to negotiation",
            {'party': party}
        )

        return True

    def _get_revision(self, revision_number: int) -> Optional[Revision]:
        """Get revision by number."""
        for rev in self.revisions:
            if rev.revision_number == revision_number:
                return rev
        return None

    def _log_action(self, action: str, user: str, description: str,
                   details: Dict[str, Any]) -> None:
        """Log an action to audit trail."""
        log = AuditLog(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            action=action,
            user=user,
            description=description,
            revision_number=self.current_revision,
            details=details
        )
        self.audit_logs.append(log)

    def get_revision_history(self) -> str:
        """Get formatted revision history."""
        history = f"""
{'='*70}
REVISION HISTORY: {self.document_name}
{'='*70}

Document ID: {self.document_id}
Created: {self.creation_date}
Total Revisions: {self.current_revision}

{'-'*70}
"""

        for rev in self.revisions:
            history += f"""
Revision {rev.revision_number}
Author: {rev.author}
Date: {rev.timestamp}
Status: {rev.approval_status.value.upper()}
Description: {rev.description}
Changes: {rev.change_summary}
Size: {rev.file_size} bytes
Hash: {rev.content_hash[:16]}...
"""
            if rev.approver:
                history += f"Approved by: {rev.approver} on {rev.approval_date}\n"
            if rev.notes:
                history += f"Notes: {rev.notes}\n"
            history += "-" * 70 + "\n"

        return history

    def get_audit_trail(self) -> str:
        """Get formatted audit trail."""
        trail = f"""
{'='*70}
AUDIT TRAIL: {self.document_name}
{'='*70}

Document ID: {self.document_id}
Total Actions: {len(self.audit_logs)}

{'-'*70}
"""

        for log in self.audit_logs:
            trail += f"""
Timestamp: {log.timestamp}
Action: {log.action}
User: {log.user}
Description: {log.description}
Revision: {log.revision_number}
Details: {json.dumps(log.details, indent=2)}

{'-'*70}
"""

        return trail

    def get_approval_workflow_status(self) -> Dict[str, Any]:
        """Get approval workflow status."""
        draft = sum(1 for r in self.revisions if r.approval_status == ApprovalStatus.DRAFT)
        pending = sum(1 for r in self.revisions if r.approval_status == ApprovalStatus.PENDING_REVIEW)
        approved = sum(1 for r in self.revisions if r.approval_status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self.revisions if r.approval_status == ApprovalStatus.REJECTED)
        negotiation = sum(1 for r in self.revisions if r.approval_status == ApprovalStatus.IN_NEGOTIATION)

        return {
            'total_revisions': self.current_revision,
            'draft': draft,
            'pending_review': pending,
            'approved': approved,
            'rejected': rejected,
            'in_negotiation': negotiation,
            'last_approved': self._get_last_approved_revision()
        }

    def _get_last_approved_revision(self) -> Optional[int]:
        """Get the most recent approved revision number."""
        for rev in reversed(self.revisions):
            if rev.approval_status == ApprovalStatus.APPROVED:
                return rev.revision_number
        return None

    def export_to_json(self, filename: str) -> None:
        """Export version history to JSON."""
        data = {
            'document_id': self.document_id,
            'document_name': self.document_name,
            'creation_date': self.creation_date,
            'current_revision': self.current_revision,
            'revisions': [rev.to_dict() for rev in self.revisions],
            'audit_logs': [
                {
                    'timestamp': log.timestamp,
                    'action': log.action,
                    'user': log.user,
                    'description': log.description,
                    'revision_number': log.revision_number,
                    'details': log.details
                }
                for log in self.audit_logs
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Version history exported to {filename}")


def example_contract_version_tracking():
    """Example: Track contract revisions through approval workflow."""

    # Initialize version manager
    vm = VersionManager("CONTRACT-2024-001", "Service Agreement v1.0")

    # Create initial draft
    contract_v1 = "SERVICE AGREEMENT\n\nParties: Client and Provider\n\nServices: Legal consultation"
    rev1 = vm.create_revision(
        contract_v1,
        "John Smith",
        "Initial contract draft",
        "Created complete draft with basic terms",
        "First version from template"
    )

    # Submit for review
    vm.submit_for_review(1, "John Smith")

    # Create revised version with feedback
    contract_v2 = """SERVICE AGREEMENT

Parties: ABC Corporation and XYZ Legal Services

Services:
- Legal consultation
- Document drafting
- Contract review

Fees:
- Hourly Rate: $250/hour
- Monthly Retainer: $5,000

Term: 1 year"""

    rev2 = vm.create_revision(
        contract_v2,
        "Jane Doe",
        "Incorporated client feedback",
        "Added detailed fee structure and service list",
        "Feedback from client review"
    )

    vm.submit_for_review(2, "Jane Doe")
    vm.approve_revision(2, "Legal Manager", "Looks good, approved for execution")

    # Create final version
    contract_v3 = """SERVICE AGREEMENT

Parties: ABC Corporation and XYZ Legal Services Inc.

Services:
- Legal consultation
- Document drafting
- Contract review
- Compliance consulting

Fees:
- Hourly Rate: $250/hour
- Monthly Retainer: $5,000
- Minimum monthly hours: 20

Term: 1 year
Renewal: Auto-renews annually unless 90 days notice

Confidentiality: 3-year confidentiality period

Governing Law: California"""

    rev3 = vm.create_revision(
        contract_v3,
        "Jane Doe",
        "Final version with all terms",
        "Added confidentiality clause and renewal terms",
        "Ready for execution"
    )

    vm.submit_for_review(3, "Jane Doe")
    vm.approve_revision(3, "Legal Manager", "Approved for execution - all terms finalized")

    # Print history and status
    print(vm.get_revision_history())
    print(vm.get_audit_trail())

    # Get workflow status
    print("\nAPPROVAL WORKFLOW STATUS:")
    status = vm.get_approval_workflow_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Export to JSON
    vm.export_to_json('/tmp/contract_version_history.json')

    return vm


def example_negotiation_tracking():
    """Example: Track document through negotiation."""

    vm = VersionManager("LEASE-2024-001", "Commercial Lease Agreement")

    # Initial draft
    lease_v1 = "LEASE: 24-month commercial property lease\nMonthly rent: $5,000"
    vm.create_revision(lease_v1, "Landlord Legal", "Initial lease draft", "First draft")
    vm.submit_for_review(1, "Landlord Legal")

    # Tenant feedback - start negotiation
    vm.start_negotiation(1, "Tenant's Counsel")

    # Landlord revision
    lease_v2 = """LEASE: Commercial Property Lease

Property: 123 Business Avenue
Monthly Rent: $4,500 (negotiated)
Term: 24 months
Renewal: 2 x 12 month renewal options

Tenant Improvements: Landlord provides $20,000 allowance"""

    vm.create_revision(lease_v2, "Landlord Legal", "Revised per tenant request",
                      "Adjusted rent and added improvement allowance")
    vm.start_negotiation(2, "Tenant's Counsel")

    # Final approval
    lease_v3 = """LEASE: Commercial Property Lease

Property: 123 Business Avenue, Suite 100
Monthly Rent: $4,500
Deposit: $9,000 (2 months)
Term: 24 months
Renewal: 2 x 12 month renewal options @ 3% increase

Tenant Improvements: Landlord provides $25,000 allowance
Insurance: Tenant maintains $2M liability
Maintenance: Landlord responsible for structural"""

    vm.create_revision(lease_v3, "Landlord Legal", "Final lease agreement",
                      "All terms finalized with tenant agreement")
    vm.submit_for_review(3, "Landlord Legal")
    vm.approve_revision(3, "Real Estate Manager", "Final lease approved for execution")

    print(vm.get_revision_history())

    return vm


if __name__ == "__main__":
    example_contract_version_tracking()
    print("\n" + "="*70 + "\n")
    example_negotiation_tracking()
    print("\nVersion tracking examples completed!")
