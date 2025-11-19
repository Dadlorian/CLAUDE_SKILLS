"""
Audit Trail Generator - Production-Ready Implementation

This module implements comprehensive audit trail generation including:
- Event logging
- Access tracking
- Data modification logging
- Compliance event recording
- Audit trail queries
- Tamper detection

Author: Compliance Automation Team
Version: 1.0.0
License: MIT
"""

import logging
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import uuid


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    CONSENT_ACTION = "consent_action"
    POLICY_CHANGE = "policy_change"
    AUDIT_ACCESS = "audit_access"


class AuditEventStatus(Enum):
    """Status of audit events."""
    SUCCESS = "success"
    FAILURE = "failure"
    UNAUTHORIZED = "unauthorized"
    ERROR = "error"


class SensitivityLevel(Enum):
    """Sensitivity level of audit events."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AuditEvent:
    """Represents an audit trail event."""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: str
    resource_id: str
    resource_type: str
    action: str
    status: AuditEventStatus
    result: str  # 'success', 'failure', etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    affected_data_categories: List[str] = field(default_factory=list)
    sensitivity_level: SensitivityLevel = SensitivityLevel.MEDIUM
    details: Dict = field(default_factory=dict)
    location: Optional[str] = None
    session_id: Optional[str] = None
    change_before: Optional[Dict] = None
    change_after: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'action': self.action,
            'status': self.status.value,
            'result': self.result,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'affected_data_categories': self.affected_data_categories,
            'sensitivity_level': self.sensitivity_level.value,
            'details': self.details,
            'location': self.location,
            'session_id': self.session_id,
            'change_before': self.change_before,
            'change_after': self.change_after,
            'metadata': self.metadata
        }
        return data

    def calculate_hash(self) -> str:
        """Calculate hash of event for integrity verification."""
        event_string = f"{self.event_id}{self.timestamp}{self.user_id}{self.resource_id}{self.action}"
        return hashlib.sha256(event_string.encode()).hexdigest()


@dataclass
class AuditTrail:
    """Represents a series of audit events."""
    trail_id: str
    resource_id: str
    resource_type: str
    created_at: datetime
    events: List[AuditEvent] = field(default_factory=list)
    chain_hash: str = ""  # For tamper detection

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'trail_id': self.trail_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'created_at': self.created_at.isoformat(),
            'event_count': len(self.events),
            'events': [e.to_dict() for e in self.events],
            'chain_hash': self.chain_hash
        }

    def calculate_chain_hash(self) -> str:
        """Calculate chain hash for integrity verification."""
        hashes = [e.calculate_hash() for e in self.events]
        chain_string = "".join(hashes)
        return hashlib.sha256(chain_string.encode()).hexdigest()


class AuditLogger(ABC):
    """Abstract base class for audit logging."""

    @abstractmethod
    def log_event(self, event: AuditEvent) -> str:
        """Log an audit event."""
        pass

    @abstractmethod
    def query_events(self, **kwargs) -> List[AuditEvent]:
        """Query audit events."""
        pass


class ComplianceAuditLogger(AuditLogger):
    """
    Comprehensive audit logging system.

    Provides:
    - Event logging
    - Audit trail tracking
    - Event querying
    - Integrity verification
    - Tamper detection
    - Compliance reporting
    """

    def __init__(self, organization_name: str):
        """
        Initialize audit logger.

        Args:
            organization_name: Name of organization
        """
        self.organization_name = organization_name
        self.events: Dict[str, AuditEvent] = {}
        self.trails: Dict[str, AuditTrail] = {}
        self.logger = logger

    def log_event(self, event: AuditEvent) -> str:
        """
        Log an audit event.

        Args:
            event: AuditEvent instance

        Returns:
            Event ID
        """
        self.events[event.event_id] = event

        # Update or create trail
        trail_key = f"{event.resource_type}:{event.resource_id}"
        if trail_key not in self.trails:
            self.trails[trail_key] = AuditTrail(
                trail_id=str(uuid.uuid4()),
                resource_id=event.resource_id,
                resource_type=event.resource_type,
                created_at=datetime.now()
            )

        trail = self.trails[trail_key]
        trail.events.append(event)
        trail.chain_hash = trail.calculate_chain_hash()

        self.logger.info(f"Logged audit event: {event.event_id} - {event.event_type.value}")
        return event.event_id

    def log_data_access(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        data_categories: List[str],
        status: AuditEventStatus,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Log data access event.

        Args:
            user_id: ID of user accessing data
            resource_id: ID of resource accessed
            resource_type: Type of resource
            data_categories: Categories of data accessed
            status: Status of access
            ip_address: IP address of access
            session_id: Session ID

        Returns:
            Event ID
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action='read',
            status=status,
            result='success' if status == AuditEventStatus.SUCCESS else 'failure',
            ip_address=ip_address,
            affected_data_categories=data_categories,
            session_id=session_id,
            sensitivity_level=self._determine_sensitivity(data_categories)
        )

        return self.log_event(event)

    def log_data_modification(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        action: str,
        data_categories: List[str],
        change_before: Optional[Dict] = None,
        change_after: Optional[Dict] = None,
        status: AuditEventStatus = AuditEventStatus.SUCCESS,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Log data modification event.

        Args:
            user_id: ID of user modifying data
            resource_id: ID of resource modified
            resource_type: Type of resource
            action: Action performed (create, update, delete)
            data_categories: Categories of data modified
            change_before: Data before modification
            change_after: Data after modification
            status: Status of operation
            ip_address: IP address

        Returns:
            Event ID
        """
        event_type = AuditEventType.DATA_DELETION if action == 'delete' else AuditEventType.DATA_MODIFICATION

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            status=status,
            result='success' if status == AuditEventStatus.SUCCESS else 'failure',
            ip_address=ip_address,
            affected_data_categories=data_categories,
            change_before=change_before,
            change_after=change_after,
            sensitivity_level=SensitivityLevel.HIGH
        )

        return self.log_event(event)

    def log_user_login(
        self,
        user_id: str,
        status: AuditEventStatus,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Log user login event.

        Args:
            user_id: ID of user
            status: Login status
            ip_address: IP address
            user_agent: User agent string
            location: Login location

        Returns:
            Event ID
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=AuditEventType.USER_LOGIN,
            user_id=user_id,
            resource_id=user_id,
            resource_type='user',
            action='login',
            status=status,
            result='success' if status == AuditEventStatus.SUCCESS else 'failure',
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            sensitivity_level=SensitivityLevel.MEDIUM
        )

        return self.log_event(event)

    def log_permission_change(
        self,
        user_id: str,
        target_user_id: str,
        permissions_before: List[str],
        permissions_after: List[str],
        ip_address: Optional[str] = None
    ) -> str:
        """
        Log permission change event.

        Args:
            user_id: ID of user making change
            target_user_id: ID of affected user
            permissions_before: Permissions before change
            permissions_after: Permissions after change
            ip_address: IP address

        Returns:
            Event ID
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=AuditEventType.PERMISSION_CHANGE,
            user_id=user_id,
            resource_id=target_user_id,
            resource_type='user',
            action='modify_permissions',
            status=AuditEventStatus.SUCCESS,
            result='success',
            ip_address=ip_address,
            change_before={'permissions': permissions_before},
            change_after={'permissions': permissions_after},
            sensitivity_level=SensitivityLevel.HIGH
        )

        return self.log_event(event)

    def log_security_event(
        self,
        event_type: AuditEventType,
        severity: SensitivityLevel,
        description: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> str:
        """
        Log security event.

        Args:
            event_type: Type of security event
            severity: Severity level
            description: Event description
            user_id: ID of involved user
            resource_id: ID of involved resource
            details: Additional details

        Returns:
            Event ID
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id or 'system',
            resource_id=resource_id or 'N/A',
            resource_type='security',
            action='security_alert',
            status=AuditEventStatus.ERROR,
            result='alert',
            sensitivity_level=severity,
            details=details or {'description': description}
        )

        return self.log_event(event)

    def query_events(self, **kwargs) -> List[AuditEvent]:
        """
        Query audit events.

        Supports filtering by:
        - user_id
        - resource_id
        - event_type
        - status
        - date_from
        - date_to
        - sensitivity_level

        Args:
            **kwargs: Filter parameters

        Returns:
            List of matching events
        """
        results = list(self.events.values())

        # Filter by user_id
        if 'user_id' in kwargs:
            results = [e for e in results if e.user_id == kwargs['user_id']]

        # Filter by resource_id
        if 'resource_id' in kwargs:
            results = [e for e in results if e.resource_id == kwargs['resource_id']]

        # Filter by event_type
        if 'event_type' in kwargs:
            event_type = kwargs['event_type']
            if isinstance(event_type, str):
                event_type = AuditEventType[event_type]
            results = [e for e in results if e.event_type == event_type]

        # Filter by status
        if 'status' in kwargs:
            status = kwargs['status']
            if isinstance(status, str):
                status = AuditEventStatus[status]
            results = [e for e in results if e.status == status]

        # Filter by date range
        if 'date_from' in kwargs:
            date_from = kwargs['date_from']
            results = [e for e in results if e.timestamp >= date_from]

        if 'date_to' in kwargs:
            date_to = kwargs['date_to']
            results = [e for e in results if e.timestamp <= date_to]

        # Filter by sensitivity
        if 'sensitivity_level' in kwargs:
            sensitivity = kwargs['sensitivity_level']
            results = [e for e in results if e.sensitivity_level == sensitivity]

        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results

    def get_user_activity_report(self, user_id: str, days: int = 30) -> Dict:
        """
        Get activity report for user.

        Args:
            user_id: ID of user
            days: Number of days to include

        Returns:
            Activity report
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        events = self.query_events(
            user_id=user_id,
            date_from=cutoff_date
        )

        activity_by_type = {}
        for event in events:
            event_type = event.event_type.value
            if event_type not in activity_by_type:
                activity_by_type[event_type] = 0
            activity_by_type[event_type] += 1

        return {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'period_days': days,
            'total_events': len(events),
            'activity_by_type': activity_by_type,
            'events': [e.to_dict() for e in events]
        }

    def get_audit_trail(self, resource_id: str, resource_type: str) -> Dict:
        """
        Get complete audit trail for resource.

        Args:
            resource_id: ID of resource
            resource_type: Type of resource

        Returns:
            Audit trail dictionary
        """
        trail_key = f"{resource_type}:{resource_id}"
        if trail_key not in self.trails:
            return {'error': 'Trail not found'}

        trail = self.trails[trail_key]
        return trail.to_dict()

    def verify_trail_integrity(self, trail_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify integrity of audit trail.

        Args:
            trail_id: ID of trail to verify

        Returns:
            Tuple of (is_valid, message)
        """
        for trail in self.trails.values():
            if trail.trail_id == trail_id:
                current_hash = trail.calculate_chain_hash()
                if current_hash != trail.chain_hash:
                    return False, "Trail integrity compromised - hash mismatch"
                return True, "Trail integrity verified"

        return False, "Trail not found"

    def get_compliance_report(self, days: int = 90) -> Dict:
        """
        Generate compliance audit report.

        Args:
            days: Number of days to include

        Returns:
            Compliance report
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        all_events = self.query_events(date_from=cutoff_date)

        high_sensitivity_events = [
            e for e in all_events
            if e.sensitivity_level in [SensitivityLevel.CRITICAL, SensitivityLevel.HIGH]
        ]

        failed_events = [e for e in all_events if e.status == AuditEventStatus.FAILURE]

        return {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'total_events': len(all_events),
            'high_sensitivity_events': len(high_sensitivity_events),
            'failed_operations': len(failed_events),
            'events_by_type': self._count_by_type(all_events),
            'high_sensitivity_details': [e.to_dict() for e in high_sensitivity_events[:10]]
        }

    def _count_by_type(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for event in events:
            event_type = event.event_type.value
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts

    def _determine_sensitivity(self, data_categories: List[str]) -> SensitivityLevel:
        """Determine sensitivity level based on data categories."""
        sensitive_categories = {'health', 'financial', 'biometric', 'criminal'}
        if any(cat in data_categories for cat in sensitive_categories):
            return SensitivityLevel.HIGH
        return SensitivityLevel.MEDIUM


def main():
    """Example usage and demonstration."""
    # Initialize logger
    logger_instance = ComplianceAuditLogger("Acme Corporation")

    # Log user login
    login_event_id = logger_instance.log_user_login(
        user_id='USER001',
        status=AuditEventStatus.SUCCESS,
        ip_address='192.168.1.100',
        location='Office'
    )
    print(f"Login event logged: {login_event_id}")

    # Log data access
    access_event_id = logger_instance.log_data_access(
        user_id='USER001',
        resource_id='CUST001',
        resource_type='customer',
        data_categories=['email', 'phone', 'address'],
        status=AuditEventStatus.SUCCESS,
        ip_address='192.168.1.100'
    )
    print(f"Data access logged: {access_event_id}")

    # Log data modification
    modify_event_id = logger_instance.log_data_modification(
        user_id='USER001',
        resource_id='CUST001',
        resource_type='customer',
        action='update',
        data_categories=['phone'],
        change_before={'phone': '555-0100'},
        change_after={'phone': '555-0101'}
    )
    print(f"Data modification logged: {modify_event_id}")

    # Log permission change
    perm_event_id = logger_instance.log_permission_change(
        user_id='ADMIN001',
        target_user_id='USER001',
        permissions_before=['read', 'write'],
        permissions_after=['read', 'write', 'admin']
    )
    print(f"Permission change logged: {perm_event_id}")

    # Query events
    print("\n" + "=" * 80)
    print("USER ACTIVITY REPORT")
    print("=" * 80)
    activity = logger_instance.get_user_activity_report('USER001')
    print(json.dumps(activity, indent=2))

    # Get audit trail
    print("\n" + "=" * 80)
    print("AUDIT TRAIL FOR RESOURCE")
    print("=" * 80)
    trail = logger_instance.get_audit_trail('CUST001', 'customer')
    print(json.dumps(trail, indent=2))

    # Generate compliance report
    print("\n" + "=" * 80)
    print("COMPLIANCE AUDIT REPORT")
    print("=" * 80)
    compliance_report = logger_instance.get_compliance_report(days=90)
    print(json.dumps(compliance_report, indent=2))


if __name__ == '__main__':
    main()
