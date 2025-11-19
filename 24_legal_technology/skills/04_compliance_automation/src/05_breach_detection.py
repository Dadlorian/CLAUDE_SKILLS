"""
Breach Detection - Production-Ready Implementation

This module implements comprehensive breach detection and response including:
- Suspicious activity detection
- Data loss monitoring
- Incident classification
- Breach assessment
- Notification management
- Incident response tracking

Author: Compliance Automation Team
Version: 1.0.0
License: MIT
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from abc import ABC, abstractmethod
import uuid


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BreachSeverity(Enum):
    """Severity levels for data breaches."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachType(Enum):
    """Types of data breaches."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ACCIDENTAL_DISCLOSURE = "accidental_disclosure"
    RANSOMWARE = "ransomware"
    MALWARE = "malware"
    INSIDER_THREAT = "insider_threat"
    DATA_LOSS = "data_loss"
    CONFIGURATION_ERROR = "configuration_error"
    THIRD_PARTY_BREACH = "third_party_breach"
    CREDENTIAL_COMPROMISE = "credential_compromise"


class BreachStatus(Enum):
    """Status of breach incident."""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class NotificationStatus(Enum):
    """Status of breach notifications."""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class SuspiciousActivity:
    """Represents suspicious activity that may indicate a breach."""
    activity_id: str
    timestamp: datetime
    activity_type: str
    description: str
    affected_data_elements: List[str]
    affected_records_count: int
    source_ip: Optional[str] = None
    user_account: Optional[str] = None
    severity_score: int = 0  # 0-100
    detection_method: str = "automated"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class DataBreach:
    """Represents a confirmed data breach incident."""
    breach_id: str
    breach_type: BreachType
    discovery_date: datetime
    suspected_cause: str
    affected_data_categories: List[str]
    affected_individuals_count: int
    severity: BreachSeverity
    status: BreachStatus = BreachStatus.DETECTED
    description: str = ""
    root_cause: Optional[str] = None
    remediation_steps: List[str] = field(default_factory=list)
    notification_required: bool = False
    third_party_involved: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = {
            'breach_id': self.breach_id,
            'breach_type': self.breach_type.value,
            'discovery_date': self.discovery_date.isoformat(),
            'suspected_cause': self.suspected_cause,
            'affected_data_categories': self.affected_data_categories,
            'affected_individuals_count': self.affected_individuals_count,
            'severity': self.severity.value,
            'status': self.status.value,
            'description': self.description,
            'root_cause': self.root_cause,
            'remediation_steps': self.remediation_steps,
            'notification_required': self.notification_required,
            'third_party_involved': self.third_party_involved,
            'metadata': self.metadata,
            'detected_at': self.detected_at.isoformat()
        }
        return data


@dataclass
class BreachNotification:
    """Represents a breach notification to data subjects or authorities."""
    notification_id: str
    breach_id: str
    recipient_type: str  # 'data_subject', 'authority', 'third_party'
    recipient_email: str
    notification_date: datetime
    status: NotificationStatus
    content: str = ""
    delivery_attempt_count: int = 0
    last_attempt_date: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = {
            'notification_id': self.notification_id,
            'breach_id': self.breach_id,
            'recipient_type': self.recipient_type,
            'recipient_email': self.recipient_email,
            'notification_date': self.notification_date.isoformat(),
            'status': self.status.value,
            'content': self.content,
            'delivery_attempt_count': self.delivery_attempt_count,
            'last_attempt_date': self.last_attempt_date.isoformat() if self.last_attempt_date else None,
            'metadata': self.metadata
        }
        return data


class BreachDetector(ABC):
    """Abstract base class for breach detection."""

    @abstractmethod
    def detect_suspicious_activity(self, activity: SuspiciousActivity) -> Tuple[bool, Optional[str]]:
        """Detect if activity indicates a breach."""
        pass

    @abstractmethod
    def assess_breach(self, breach: DataBreach) -> Dict:
        """Assess breach severity and required actions."""
        pass


class ComplianceBreachDetector(BreachDetector):
    """
    Comprehensive breach detection and response system.

    Provides:
    - Suspicious activity detection
    - Breach classification
    - Impact assessment
    - Notification management
    - Response tracking
    """

    def __init__(self, organization_name: str):
        """
        Initialize breach detector.

        Args:
            organization_name: Name of organization
        """
        self.organization_name = organization_name
        self.suspicious_activities: Dict[str, SuspiciousActivity] = {}
        self.breaches: Dict[str, DataBreach] = {}
        self.notifications: Dict[str, BreachNotification] = {}
        self.logger = logger

    def detect_suspicious_activity(self, activity: SuspiciousActivity) -> Tuple[bool, Optional[str]]:
        """
        Detect if activity indicates a breach.

        Args:
            activity: SuspiciousActivity instance

        Returns:
            Tuple of (is_breach, breach_id or None)
        """
        self.suspicious_activities[activity.activity_id] = activity

        # Calculate breach likelihood
        breach_likelihood = self._calculate_breach_likelihood(activity)

        if breach_likelihood >= 0.7:  # 70% threshold
            # Create breach incident
            breach_id = self._create_breach_from_activity(activity)
            self.logger.warning(f"Breach detected from activity: {activity.activity_id}")
            return True, breach_id

        self.logger.info(f"Suspicious activity recorded: {activity.activity_id}")
        return False, None

    def _calculate_breach_likelihood(self, activity: SuspiciousActivity) -> float:
        """
        Calculate likelihood that activity indicates a breach.

        Args:
            activity: SuspiciousActivity to assess

        Returns:
            Likelihood score (0.0 to 1.0)
        """
        likelihood = 0.0

        # Factor in severity score
        likelihood += (activity.severity_score / 100.0) * 0.6

        # Factor in number of affected records
        if activity.affected_records_count > 1000:
            likelihood += 0.2
        elif activity.affected_records_count > 100:
            likelihood += 0.1

        # Factor in detection method
        if activity.detection_method == "manual_report":
            likelihood += 0.1

        return min(likelihood, 1.0)

    def _create_breach_from_activity(self, activity: SuspiciousActivity) -> str:
        """
        Create a breach incident from suspicious activity.

        Args:
            activity: SuspiciousActivity instance

        Returns:
            Breach ID
        """
        breach_id = str(uuid.uuid4())

        # Determine severity based on activity
        severity = self._determine_severity(activity)

        breach = DataBreach(
            breach_id=breach_id,
            breach_type=self._infer_breach_type(activity),
            discovery_date=activity.timestamp,
            suspected_cause=activity.description,
            affected_data_categories=activity.affected_data_elements,
            affected_individuals_count=activity.affected_records_count,
            severity=severity,
            status=BreachStatus.DETECTED
        )

        self.breaches[breach_id] = breach
        self.logger.info(f"Created breach incident: {breach_id}")
        return breach_id

    def _determine_severity(self, activity: SuspiciousActivity) -> BreachSeverity:
        """Determine breach severity."""
        if activity.severity_score >= 80:
            return BreachSeverity.CRITICAL
        elif activity.severity_score >= 60:
            return BreachSeverity.HIGH
        elif activity.severity_score >= 40:
            return BreachSeverity.MEDIUM
        return BreachSeverity.LOW

    def _infer_breach_type(self, activity: SuspiciousActivity) -> BreachType:
        """Infer breach type from activity."""
        activity_type_lower = activity.activity_type.lower()

        if "ransomware" in activity_type_lower:
            return BreachType.RANSOMWARE
        elif "malware" in activity_type_lower:
            return BreachType.MALWARE
        elif "unauthorized" in activity_type_lower or "access" in activity_type_lower:
            return BreachType.UNAUTHORIZED_ACCESS
        elif "disclosure" in activity_type_lower:
            return BreachType.ACCIDENTAL_DISCLOSURE
        elif "loss" in activity_type_lower or "delete" in activity_type_lower:
            return BreachType.DATA_LOSS
        elif "credential" in activity_type_lower:
            return BreachType.CREDENTIAL_COMPROMISE

        return BreachType.UNAUTHORIZED_ACCESS

    def assess_breach(self, breach: DataBreach) -> Dict:
        """
        Assess breach and determine required actions.

        Args:
            breach: DataBreach instance

        Returns:
            Assessment dictionary
        """
        assessment = {
            'breach_id': breach.breach_id,
            'timestamp': datetime.now().isoformat(),
            'requires_notification': self._requires_notification(breach),
            'notification_deadline': self._get_notification_deadline(breach),
            'authority_notification_required': self._requires_authority_notification(breach),
            'estimated_individuals_affected': breach.affected_individuals_count,
            'risk_level': breach.severity.value,
            'recommended_actions': self._get_recommended_actions(breach),
            'legal_obligations': self._get_legal_obligations(breach)
        }

        # Update breach status based on assessment
        breach.status = BreachStatus.INVESTIGATING

        return assessment

    def _requires_notification(self, breach: DataBreach) -> bool:
        """Determine if notification is required."""
        # Notification required for high-risk breaches
        if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]:
            return True

        # Check if sensitive data categories affected
        sensitive_categories = {'health', 'financial', 'biometric'}
        if any(cat in breach.affected_data_categories for cat in sensitive_categories):
            return True

        return breach.affected_individuals_count > 100

    def _requires_authority_notification(self, breach: DataBreach) -> bool:
        """Determine if authority notification (e.g., DPA) is required."""
        # GDPR: notification required for high risk to data subjects
        if breach.severity == BreachSeverity.CRITICAL:
            return True
        if breach.affected_individuals_count > 500:
            return True
        return False

    def _get_notification_deadline(self, breach: DataBreach) -> str:
        """Get notification deadline for breach."""
        # GDPR: without undue delay, typically 30 days
        deadline = breach.discovery_date + timedelta(days=30)
        return deadline.isoformat()

    def _get_recommended_actions(self, breach: DataBreach) -> List[str]:
        """Get recommended remediation actions."""
        actions = [
            "Immediately investigate the scope of the breach",
            "Collect forensic evidence",
            "Secure affected systems",
            "Review logs for unauthorized access",
            "Reset credentials for affected accounts",
            "Notify affected individuals",
            "Document all remediation steps",
            "Conduct post-incident review"
        ]

        if breach.severity == BreachSeverity.CRITICAL:
            actions.insert(0, "Activate incident response team immediately")

        return actions

    def _get_legal_obligations(self, breach: DataBreach) -> List[str]:
        """Get legal obligations for breach."""
        obligations = []

        # GDPR obligations
        if self._requires_notification(breach):
            obligations.append("GDPR Article 33: Notify data subjects without undue delay")

        if self._requires_authority_notification(breach):
            obligations.append("GDPR Article 34: Notify supervisory authority immediately")

        if breach.affected_individuals_count > 500:
            obligations.append("Public communication may be required")

        return obligations

    def create_notification(
        self,
        breach_id: str,
        recipient_type: str,
        recipient_email: str
    ) -> str:
        """
        Create a breach notification.

        Args:
            breach_id: ID of breach
            recipient_type: Type of recipient
            recipient_email: Email address

        Returns:
            Notification ID
        """
        if breach_id not in self.breaches:
            raise ValueError(f"Breach not found: {breach_id}")

        notification_id = str(uuid.uuid4())
        breach = self.breaches[breach_id]

        notification = BreachNotification(
            notification_id=notification_id,
            breach_id=breach_id,
            recipient_type=recipient_type,
            recipient_email=recipient_email,
            notification_date=datetime.now(),
            status=NotificationStatus.PENDING,
            content=self._generate_notification_content(breach, recipient_type)
        )

        self.notifications[notification_id] = notification
        self.logger.info(f"Created notification: {notification_id}")
        return notification_id

    def _generate_notification_content(self, breach: DataBreach, recipient_type: str) -> str:
        """Generate notification content."""
        if recipient_type == "data_subject":
            return f"""
            Dear Data Subject,

            We are writing to inform you of a data security incident affecting your personal data.

            Incident Details:
            - Date: {breach.discovery_date.strftime('%Y-%m-%d')}
            - Type: {breach.breach_type.value}
            - Data Affected: {', '.join(breach.affected_data_categories)}

            We have taken steps to secure your information and are committed to transparency.

            For more information or to take action, please visit our security page.
            """
        else:
            return f"""
            Regulatory Authority Notification

            Breach ID: {breach.breach_id}
            Type: {breach.breach_type.value}
            Severity: {breach.severity.value}
            Individuals Affected: {breach.affected_individuals_count}
            """

    def mark_notification_sent(self, notification_id: str) -> bool:
        """
        Mark notification as sent.

        Args:
            notification_id: ID of notification

        Returns:
            True if successful
        """
        if notification_id not in self.notifications:
            return False

        notification = self.notifications[notification_id]
        notification.status = NotificationStatus.SENT
        notification.last_attempt_date = datetime.now()
        notification.delivery_attempt_count += 1

        self.logger.info(f"Marked notification as sent: {notification_id}")
        return True

    def generate_breach_report(self, breach_id: str) -> Dict:
        """
        Generate comprehensive breach report.

        Args:
            breach_id: ID of breach

        Returns:
            Breach report dictionary
        """
        if breach_id not in self.breaches:
            raise ValueError(f"Breach not found: {breach_id}")

        breach = self.breaches[breach_id]
        assessment = self.assess_breach(breach)

        related_notifications = [
            n.to_dict() for n in self.notifications.values()
            if n.breach_id == breach_id
        ]

        return {
            'timestamp': datetime.now().isoformat(),
            'breach_details': breach.to_dict(),
            'assessment': assessment,
            'notifications': related_notifications,
            'suspicious_activities': [
                a.to_dict() for a in self.suspicious_activities.values()
                if breach_id in [b.breach_id for b in self.breaches.values()
                                 if a.activity_id in []]
            ]
        }

    def get_compliance_status(self) -> Dict:
        """
        Get breach compliance status.

        Returns:
            Status dictionary
        """
        total_breaches = len(self.breaches)
        critical_breaches = sum(
            1 for b in self.breaches.values()
            if b.severity == BreachSeverity.CRITICAL
        )
        pending_notifications = sum(
            1 for n in self.notifications.values()
            if n.status == NotificationStatus.PENDING
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'total_breaches': total_breaches,
            'critical_breaches': critical_breaches,
            'pending_notifications': pending_notifications,
            'breaches_by_status': {
                status.value: sum(1 for b in self.breaches.values() if b.status == status)
                for status in BreachStatus
            }
        }


def main():
    """Example usage and demonstration."""
    # Initialize detector
    detector = ComplianceBreachDetector("Acme Corporation")

    # Detect suspicious activity
    activity = SuspiciousActivity(
        activity_id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        activity_type='Unauthorized Access',
        description='Multiple failed login attempts followed by successful access from unknown IP',
        affected_data_elements=['customer_email', 'customer_phone'],
        affected_records_count=5000,
        source_ip='203.0.113.45',
        severity_score=85
    )

    is_breach, breach_id = detector.detect_suspicious_activity(activity)
    print(f"Activity Detection Result: {'BREACH' if is_breach else 'SUSPICIOUS'}")

    if is_breach:
        print(f"Breach ID: {breach_id}")

        # Assess breach
        breach = detector.breaches[breach_id]
        assessment = detector.assess_breach(breach)

        print("\n" + "=" * 80)
        print("BREACH ASSESSMENT")
        print("=" * 80)
        print(json.dumps(assessment, indent=2))

        # Create notification
        notif_id = detector.create_notification(
            breach_id,
            'data_subject',
            'customer@example.com'
        )
        detector.mark_notification_sent(notif_id)

    # Generate compliance status
    print("\n" + "=" * 80)
    print("COMPLIANCE STATUS")
    print("=" * 80)
    status = detector.get_compliance_status()
    print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
