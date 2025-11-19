"""
Access Request and Approval Workflow System
Production-ready system for managing data access requests with approval routing.

Features:
- Role-based access request submission
- Multi-level approval workflows
- Audit trail and compliance tracking
- SLA monitoring
- Automation and notifications
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Levels of data access."""
    VIEWER = "viewer"
    ANALYST = "analyst"
    ENGINEER = "engineer"
    ADMIN = "admin"
    CUSTOM = "custom"


class RequestStatus(Enum):
    """Status of access request."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING_REVIEW = "pending_review"


class ApprovationType(Enum):
    """Types of approvals required."""
    DATA_OWNER = "data_owner"
    SECURITY_REVIEW = "security_review"
    MANAGER_APPROVAL = "manager_approval"
    COMPLIANCE_CHECK = "compliance_check"
    EXECUTIVE_APPROVAL = "executive_approval"


@dataclass
class DatasetAccess:
    """Represents access to a specific dataset."""
    dataset_id: str
    dataset_name: str
    access_level: AccessLevel
    justification: str
    sensitive_data: bool = False
    contains_pii: bool = False
    requires_training: bool = False


@dataclass
class AccessRequest:
    """Represents a request for data access."""
    request_id: str
    requester_email: str
    requester_name: str
    requester_team: str
    manager_email: str
    requested_at: datetime
    datasets: List[DatasetAccess] = field(default_factory=list)
    business_purpose: str = ""
    project_description: str = ""
    expected_duration_days: int = 90
    status: RequestStatus = RequestStatus.DRAFT
    approvals_required: List[ApprovationType] = field(default_factory=list)
    approvals_completed: List[Dict] = field(default_factory=list)
    notes: Optional[str] = None
    expiration_date: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'request_id': self.request_id,
            'requester_email': self.requester_email,
            'requester_name': self.requester_name,
            'requester_team': self.requester_team,
            'manager_email': self.manager_email,
            'requested_at': self.requested_at.isoformat(),
            'datasets': [asdict(d) for d in self.datasets],
            'business_purpose': self.business_purpose,
            'project_description': self.project_description,
            'expected_duration_days': self.expected_duration_days,
            'status': self.status.value,
            'approvals_required': [a.value for a in self.approvals_required],
            'approvals_completed': self.approvals_completed,
            'notes': self.notes,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
        }


class AccessRequestWorkflow:
    """
    Production-grade access request management system.
    Handles submission, routing, approvals, and enforcement.
    """

    def __init__(self, metadata_db_connection, notification_service):
        """
        Initialize workflow engine.

        Args:
            metadata_db_connection: Database connection for persistence
            notification_service: Service for sending notifications
        """
        self.db_conn = metadata_db_connection
        self.notification = notification_service
        self.requests: Dict[str, AccessRequest] = {}
        logger.info("AccessRequestWorkflow initialized")

    def initialize_schema(self) -> bool:
        """Create required database schema."""
        try:
            cursor = self.db_conn.cursor()

            # Access requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_requests (
                    request_id VARCHAR(255) PRIMARY KEY,
                    requester_email VARCHAR(255) NOT NULL,
                    requester_name VARCHAR(255) NOT NULL,
                    requester_team VARCHAR(255) NOT NULL,
                    manager_email VARCHAR(255) NOT NULL,
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    business_purpose TEXT,
                    project_description TEXT,
                    expected_duration_days INT DEFAULT 90,
                    status VARCHAR(50) NOT NULL DEFAULT 'draft',
                    notes TEXT,
                    expiration_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Dataset access items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS request_dataset_access (
                    access_id SERIAL PRIMARY KEY,
                    request_id VARCHAR(255) NOT NULL REFERENCES access_requests(request_id),
                    dataset_id VARCHAR(255) NOT NULL,
                    dataset_name VARCHAR(255) NOT NULL,
                    access_level VARCHAR(50) NOT NULL,
                    justification TEXT,
                    sensitive_data BOOLEAN DEFAULT FALSE,
                    contains_pii BOOLEAN DEFAULT FALSE,
                    requires_training BOOLEAN DEFAULT FALSE
                )
            """)

            # Approval chain tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS approval_chain (
                    approval_id SERIAL PRIMARY KEY,
                    request_id VARCHAR(255) NOT NULL REFERENCES access_requests(request_id),
                    approval_type VARCHAR(50) NOT NULL,
                    approver_email VARCHAR(255) NOT NULL,
                    approver_name VARCHAR(255) NOT NULL,
                    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    approved_at TIMESTAMP,
                    approval_notes TEXT,
                    auto_approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Grant tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_grants (
                    grant_id VARCHAR(255) PRIMARY KEY,
                    request_id VARCHAR(255) REFERENCES access_requests(request_id),
                    user_email VARCHAR(255) NOT NULL,
                    dataset_id VARCHAR(255) NOT NULL,
                    access_level VARCHAR(50) NOT NULL,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    revoked_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_email, dataset_id)
                )
            """)

            # Audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_audit_log (
                    log_id SERIAL PRIMARY KEY,
                    request_id VARCHAR(255),
                    action VARCHAR(100) NOT NULL,
                    performed_by VARCHAR(255) NOT NULL,
                    description TEXT,
                    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details JSONB
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX idx_requests_requester ON access_requests(requester_email)")
            cursor.execute("CREATE INDEX idx_requests_status ON access_requests(status)")
            cursor.execute("CREATE INDEX idx_requests_manager ON access_requests(manager_email)")
            cursor.execute("CREATE INDEX idx_approval_pending ON approval_chain(request_id, approval_status)")
            cursor.execute("CREATE INDEX idx_grants_user ON access_grants(user_email)")
            cursor.execute("CREATE INDEX idx_grants_active ON access_grants(is_active)")

            self.db_conn.commit()
            logger.info("Access request schema initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize schema: {str(e)}")
            self.db_conn.rollback()
            return False

    def create_request(self, access_request: AccessRequest) -> Tuple[bool, str]:
        """
        Create a new access request.

        Args:
            access_request: AccessRequest object

        Returns:
            Tuple of (success, message_or_request_id)
        """
        try:
            # Generate request ID
            request_id = f"AR-{uuid.uuid4().hex[:8].upper()}"
            access_request.request_id = request_id
            access_request.status = RequestStatus.DRAFT

            cursor = self.db_conn.cursor()

            # Insert request
            cursor.execute("""
                INSERT INTO access_requests (
                    request_id, requester_email, requester_name, requester_team,
                    manager_email, business_purpose, project_description,
                    expected_duration_days
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request_id, access_request.requester_email, access_request.requester_name,
                access_request.requester_team, access_request.manager_email,
                access_request.business_purpose, access_request.project_description,
                access_request.expected_duration_days
            ))

            # Insert dataset access items
            for dataset in access_request.datasets:
                cursor.execute("""
                    INSERT INTO request_dataset_access (
                        request_id, dataset_id, dataset_name, access_level,
                        justification, sensitive_data, contains_pii, requires_training
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    request_id, dataset.dataset_id, dataset.dataset_name,
                    dataset.access_level.value, dataset.justification,
                    dataset.sensitive_data, dataset.contains_pii,
                    dataset.requires_training
                ))

            self.db_conn.commit()
            self.requests[request_id] = access_request

            logger.info(f"Access request created: {request_id}")
            return True, request_id

        except Exception as e:
            logger.error(f"Failed to create request: {str(e)}")
            self.db_conn.rollback()
            return False, str(e)

    def submit_request(self, request_id: str, submitted_by: str) -> Tuple[bool, str]:
        """
        Submit an access request for approval.

        Args:
            request_id: ID of request to submit
            submitted_by: Email of person submitting

        Returns:
            Tuple of (success, message)
        """
        try:
            cursor = self.db_conn.cursor()

            # Get request
            cursor.execute("SELECT * FROM access_requests WHERE request_id = %s", (request_id,))
            request_row = cursor.fetchone()

            if not request_row:
                return False, "Request not found"

            # Determine approvals required
            approvals = self._determine_required_approvals(request_id)

            # Update status
            cursor.execute("""
                UPDATE access_requests
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
            """, (RequestStatus.PENDING_REVIEW.value, request_id))

            # Create approval chain
            for approval_type in approvals:
                approver = self._get_approver(approval_type, request_row)
                cursor.execute("""
                    INSERT INTO approval_chain (
                        request_id, approval_type, approver_email, approver_name
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    request_id, approval_type.value, approver['email'], approver['name']
                ))

            # Audit log
            cursor.execute("""
                INSERT INTO access_audit_log (request_id, action, performed_by, description)
                VALUES (%s, %s, %s, %s)
            """, (
                request_id, "SUBMITTED", submitted_by,
                f"Request submitted with {len(approvals)} approvals required"
            ))

            self.db_conn.commit()

            # Send notifications
            self._notify_approvers(request_id, approvals)

            logger.info(f"Request {request_id} submitted for review")
            return True, f"Request submitted. {len(approvals)} approvals required."

        except Exception as e:
            logger.error(f"Failed to submit request: {str(e)}")
            self.db_conn.rollback()
            return False, str(e)

    def approve_request(self, request_id: str, approval_type: ApprovationType,
                       approver_email: str, approver_name: str,
                       notes: str = "") -> Tuple[bool, str]:
        """
        Approve an access request.

        Args:
            request_id: ID of request
            approval_type: Type of approval
            approver_email: Email of approver
            approver_name: Name of approver
            notes: Optional approval notes

        Returns:
            Tuple of (success, message)
        """
        try:
            cursor = self.db_conn.cursor()

            # Record approval
            cursor.execute("""
                UPDATE approval_chain
                SET approval_status = %s, approved_at = CURRENT_TIMESTAMP,
                    approval_notes = %s
                WHERE request_id = %s AND approval_type = %s
                    AND approver_email = %s
            """, (
                "approved", notes, request_id, approval_type.value, approver_email
            ))

            # Check if all approvals completed
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved
                FROM approval_chain
                WHERE request_id = %s
            """, (request_id,))

            total, approved = cursor.fetchone()

            # If all approved, grant access
            if total == approved:
                self._grant_access(request_id, cursor)
                cursor.execute("""
                    UPDATE access_requests
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE request_id = %s
                """, (RequestStatus.APPROVED.value, request_id))

                logger.info(f"Request {request_id} fully approved, access granted")

            # Audit log
            cursor.execute("""
                INSERT INTO access_audit_log (request_id, action, performed_by, description)
                VALUES (%s, %s, %s, %s)
            """, (
                request_id, "APPROVAL", approver_email,
                f"{approval_type.value} approved: {notes}"
            ))

            self.db_conn.commit()
            logger.info(f"Approval recorded: {request_id} - {approval_type.value}")
            return True, f"{approval_type.value} approval recorded"

        except Exception as e:
            logger.error(f"Failed to approve request: {str(e)}")
            self.db_conn.rollback()
            return False, str(e)

    def reject_request(self, request_id: str, rejection_reason: str,
                      rejected_by: str) -> Tuple[bool, str]:
        """Reject an access request."""
        try:
            cursor = self.db_conn.cursor()

            cursor.execute("""
                UPDATE access_requests
                SET status = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
            """, (RequestStatus.REJECTED.value, rejection_reason, request_id))

            cursor.execute("""
                INSERT INTO access_audit_log (request_id, action, performed_by, description)
                VALUES (%s, %s, %s, %s)
            """, (request_id, "REJECTED", rejected_by, rejection_reason))

            self.db_conn.commit()

            # Notify requester
            cursor.execute("SELECT requester_email FROM access_requests WHERE request_id = %s", (request_id,))
            requester = cursor.fetchone()[0]
            self.notification.send_email(
                to=requester,
                subject=f"Access Request {request_id} Rejected",
                body=f"Your access request was rejected. Reason: {rejection_reason}"
            )

            logger.info(f"Request {request_id} rejected")
            return True, "Request rejected"

        except Exception as e:
            logger.error(f"Failed to reject request: {str(e)}")
            self.db_conn.rollback()
            return False, str(e)

    def revoke_access(self, request_id: str, revoke_reason: str,
                     revoked_by: str) -> Tuple[bool, str]:
        """Revoke previously granted access."""
        try:
            cursor = self.db_conn.cursor()

            # Deactivate all grants for this request
            cursor.execute("""
                UPDATE access_grants
                SET revoked_at = CURRENT_TIMESTAMP, is_active = FALSE
                WHERE request_id = %s
            """, (request_id,))

            cursor.execute("""
                UPDATE access_requests
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
            """, (RequestStatus.REVOKED.value, request_id))

            cursor.execute("""
                INSERT INTO access_audit_log (request_id, action, performed_by, description)
                VALUES (%s, %s, %s, %s)
            """, (request_id, "REVOKED", revoked_by, revoke_reason))

            self.db_conn.commit()
            logger.info(f"Access revoked: {request_id}")
            return True, "Access revoked"

        except Exception as e:
            logger.error(f"Failed to revoke access: {str(e)}")
            self.db_conn.rollback()
            return False, str(e)

    def get_pending_approvals(self, approver_email: str) -> List[Dict]:
        """Get pending approvals for a user."""
        try:
            cursor = self.db_conn.cursor()

            cursor.execute("""
                SELECT ar.request_id, ar.requester_email, ar.requester_name,
                       ar.business_purpose, ac.approval_type, COUNT(rda.access_id) as dataset_count
                FROM access_requests ar
                JOIN approval_chain ac ON ar.request_id = ac.request_id
                JOIN request_dataset_access rda ON ar.request_id = rda.request_id
                WHERE ac.approver_email = %s AND ac.approval_status = 'pending'
                GROUP BY ar.request_id, ar.requester_email, ar.requester_name,
                         ar.business_purpose, ac.approval_type
                ORDER BY ar.requested_at DESC
            """, (approver_email,))

            return [dict(zip(['request_id', 'requester_email', 'requester_name',
                            'business_purpose', 'approval_type', 'dataset_count'],
                           row)) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get pending approvals: {str(e)}")
            return []

    # Helper methods
    def _determine_required_approvals(self, request_id: str) -> List[ApprovationType]:
        """Determine what approvals are required based on request."""
        approvals = [ApprovationType.MANAGER_APPROVAL]

        # Check datasets for sensitive data
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM request_dataset_access
            WHERE request_id = %s AND (sensitive_data = TRUE OR contains_pii = TRUE)
        """, (request_id,))

        if cursor.fetchone()[0] > 0:
            approvals.append(ApprovationType.DATA_OWNER)
            approvals.append(ApprovationType.SECURITY_REVIEW)
            approvals.append(ApprovationType.COMPLIANCE_CHECK)

        return approvals

    def _get_approver(self, approval_type: ApprovationType, request_row) -> Dict[str, str]:
        """Determine who should approve based on type."""
        if approval_type == ApprovationType.MANAGER_APPROVAL:
            return {'email': request_row[5], 'name': 'Manager'}  # manager_email
        elif approval_type == ApprovationType.SECURITY_REVIEW:
            return {'email': 'security-team@company.com', 'name': 'Security Team'}
        elif approval_type == ApprovationType.COMPLIANCE_CHECK:
            return {'email': 'compliance-team@company.com', 'name': 'Compliance Team'}
        else:
            return {'email': 'data-admin@company.com', 'name': 'Data Administrator'}

    def _grant_access(self, request_id: str, cursor) -> bool:
        """Grant access to all requested datasets."""
        try:
            cursor.execute("""
                SELECT requester_email, expected_duration_days
                FROM access_requests
                WHERE request_id = %s
            """, (request_id,))

            user_email, duration_days = cursor.fetchone()

            cursor.execute("""
                SELECT dataset_id, access_level
                FROM request_dataset_access
                WHERE request_id = %s
            """, (request_id,))

            expiration = datetime.now() + timedelta(days=duration_days)

            for dataset_id, access_level in cursor.fetchall():
                grant_id = f"GR-{uuid.uuid4().hex[:8].upper()}"
                cursor.execute("""
                    INSERT INTO access_grants (
                        grant_id, request_id, user_email, dataset_id,
                        access_level, expires_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (grant_id, request_id, user_email, dataset_id,
                     access_level, expiration))

            return True

        except Exception as e:
            logger.error(f"Failed to grant access: {str(e)}")
            return False

    def _notify_approvers(self, request_id: str, approvals: List[ApprovationType]):
        """Send notifications to required approvers."""
        for approval in approvals:
            approver = self._get_approver(approval, None)
            self.notification.send_email(
                to=approver['email'],
                subject=f"Access Request {request_id} Awaiting Approval",
                body=f"New access request {request_id} requires {approval.value} approval"
            )


if __name__ == "__main__":
    logger.info("Access request workflow module loaded")
