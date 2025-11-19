"""
Consent Tracking - Production-Ready Implementation

This module implements comprehensive consent management including:
- Consent record creation and validation
- Multi-consent tracking for different purposes
- Withdrawal management
- Consent audit trails
- Granular consent control
- Compliance reporting

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


class ConsentType(Enum):
    """Types of consent."""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PROFILING = "profiling"
    THIRD_PARTY_SHARING = "third_party_sharing"
    AUTOMATED_DECISION = "automated_decision"
    NEWSLETTER = "newsletter"
    COOKIES = "cookies"
    PHONE = "phone"
    SMS = "sms"


class ConsentChannel(Enum):
    """Consent collection channels."""
    WEB_FORM = "web_form"
    MOBILE_APP = "mobile_app"
    EMAIL = "email"
    PHONE = "phone"
    IN_PERSON = "in_person"
    PAPER = "paper"
    VOICE_ASSISTANT = "voice_assistant"


class ConsentStatus(Enum):
    """Status of consent."""
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING_VERIFICATION = "pending_verification"
    INVALID = "invalid"


@dataclass
class ConsentRecordEntry:
    """Represents a consent record entry."""
    record_id: str
    individual_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    channel: ConsentChannel
    version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    document_hash: Optional[str] = None
    expiry_date: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = {
            'record_id': self.record_id,
            'individual_id': self.individual_id,
            'consent_type': self.consent_type.value,
            'granted': self.granted,
            'timestamp': self.timestamp.isoformat(),
            'channel': self.channel.value,
            'version': self.version,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'document_hash': self.document_hash,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'metadata': self.metadata
        }
        return data

    def get_status(self) -> ConsentStatus:
        """Determine current consent status."""
        if not self.granted:
            return ConsentStatus.INVALID
        if self.expiry_date and datetime.now() > self.expiry_date:
            return ConsentStatus.EXPIRED
        return ConsentStatus.ACTIVE


@dataclass
class ConsentWithdrawal:
    """Represents a consent withdrawal."""
    withdrawal_id: str
    record_id: str
    individual_id: str
    withdrawal_timestamp: datetime
    channel: ConsentChannel
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    verified: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'withdrawal_id': self.withdrawal_id,
            'record_id': self.record_id,
            'individual_id': self.individual_id,
            'withdrawal_timestamp': self.withdrawal_timestamp.isoformat(),
            'channel': self.channel.value,
            'reason': self.reason,
            'ip_address': self.ip_address,
            'verified': self.verified
        }


@dataclass
class ConsentAuditLog:
    """Audit log entry for consent operations."""
    audit_id: str
    timestamp: datetime
    operation: str  # 'create', 'update', 'withdraw', 'verify'
    record_id: str
    individual_id: str
    actor: str  # 'system' or user identifier
    status: str
    details: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'audit_id': self.audit_id,
            'timestamp': self.timestamp.isoformat(),
            'operation': self.operation,
            'record_id': self.record_id,
            'individual_id': self.individual_id,
            'actor': self.actor,
            'status': self.status,
            'details': self.details
        }


class ConsentTracker(ABC):
    """Abstract base class for consent tracking."""

    @abstractmethod
    def create_consent(self, record: ConsentRecordEntry) -> str:
        """Create a new consent record."""
        pass

    @abstractmethod
    def withdraw_consent(self, record_id: str, reason: Optional[str] = None) -> str:
        """Withdraw consent."""
        pass

    @abstractmethod
    def verify_consent(self, record_id: str) -> bool:
        """Verify consent validity."""
        pass


class ComplianceConsentTracker(ConsentTracker):
    """
    Comprehensive consent tracking system.

    Provides:
    - Consent record management
    - Withdrawal tracking
    - Audit logging
    - Compliance reporting
    - Data subject queries
    """

    def __init__(self):
        """Initialize consent tracker."""
        self.consent_records: Dict[str, ConsentRecordEntry] = {}
        self.withdrawals: Dict[str, ConsentWithdrawal] = {}
        self.audit_logs: List[ConsentAuditLog] = []
        self.logger = logger

    def create_consent(self, record: ConsentRecordEntry) -> str:
        """
        Create a new consent record.

        Args:
            record: ConsentRecordEntry instance

        Returns:
            Record ID
        """
        self.consent_records[record.record_id] = record

        # Log to audit trail
        audit = ConsentAuditLog(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            operation='create',
            record_id=record.record_id,
            individual_id=record.individual_id,
            actor='system',
            status='success',
            details={
                'consent_type': record.consent_type.value,
                'channel': record.channel.value
            }
        )
        self.audit_logs.append(audit)

        self.logger.info(f"Created consent record: {record.record_id}")
        return record.record_id

    def withdraw_consent(
        self,
        record_id: str,
        reason: Optional[str] = None,
        channel: ConsentChannel = ConsentChannel.WEB_FORM,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Withdraw consent.

        Args:
            record_id: ID of consent record to withdraw
            reason: Reason for withdrawal
            channel: Withdrawal channel
            ip_address: IP address of withdrawal

        Returns:
            Withdrawal ID
        """
        if record_id not in self.consent_records:
            raise ValueError(f"Consent record not found: {record_id}")

        record = self.consent_records[record_id]
        withdrawal_id = str(uuid.uuid4())

        withdrawal = ConsentWithdrawal(
            withdrawal_id=withdrawal_id,
            record_id=record_id,
            individual_id=record.individual_id,
            withdrawal_timestamp=datetime.now(),
            channel=channel,
            reason=reason,
            ip_address=ip_address,
            verified=False
        )

        self.withdrawals[withdrawal_id] = withdrawal

        # Log to audit trail
        audit = ConsentAuditLog(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            operation='withdraw',
            record_id=record_id,
            individual_id=record.individual_id,
            actor='system',
            status='pending_verification',
            details={
                'withdrawal_id': withdrawal_id,
                'reason': reason
            }
        )
        self.audit_logs.append(audit)

        self.logger.info(f"Initiated withdrawal for record: {record_id}")
        return withdrawal_id

    def verify_consent(self, record_id: str) -> bool:
        """
        Verify consent validity.

        Args:
            record_id: ID of consent record to verify

        Returns:
            True if valid, False otherwise
        """
        if record_id not in self.consent_records:
            return False

        record = self.consent_records[record_id]
        status = record.get_status()

        # Check if there's an active withdrawal
        for withdrawal in self.withdrawals.values():
            if withdrawal.record_id == record_id and withdrawal.verified:
                return False

        is_valid = status == ConsentStatus.ACTIVE

        # Log to audit trail
        audit = ConsentAuditLog(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            operation='verify',
            record_id=record_id,
            individual_id=record.individual_id,
            actor='system',
            status='success',
            details={'consent_valid': is_valid}
        )
        self.audit_logs.append(audit)

        return is_valid

    def get_individual_consents(self, individual_id: str) -> Dict[str, ConsentRecordEntry]:
        """
        Get all consents for an individual.

        Args:
            individual_id: ID of individual

        Returns:
            Dictionary of consent records
        """
        return {
            rid: record
            for rid, record in self.consent_records.items()
            if record.individual_id == individual_id
        }

    def get_individual_withdrawals(self, individual_id: str) -> List[ConsentWithdrawal]:
        """
        Get all withdrawals for an individual.

        Args:
            individual_id: ID of individual

        Returns:
            List of withdrawals
        """
        return [
            w for w in self.withdrawals.values()
            if w.individual_id == individual_id
        ]

    def verify_withdrawal(self, withdrawal_id: str) -> bool:
        """
        Verify a withdrawal request.

        Args:
            withdrawal_id: ID of withdrawal

        Returns:
            True if verified, False otherwise
        """
        if withdrawal_id not in self.withdrawals:
            return False

        withdrawal = self.withdrawals[withdrawal_id]
        withdrawal.verified = True

        # Log to audit trail
        audit = ConsentAuditLog(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            operation='verify_withdrawal',
            record_id=withdrawal.record_id,
            individual_id=withdrawal.individual_id,
            actor='system',
            status='success'
        )
        self.audit_logs.append(audit)

        self.logger.info(f"Verified withdrawal: {withdrawal_id}")
        return True

    def generate_consent_report(self, individual_id: str) -> Dict:
        """
        Generate consent report for individual.

        Args:
            individual_id: ID of individual

        Returns:
            Consent report dictionary
        """
        consents = self.get_individual_consents(individual_id)
        withdrawals = self.get_individual_withdrawals(individual_id)

        return {
            'timestamp': datetime.now().isoformat(),
            'individual_id': individual_id,
            'total_consents': len(consents),
            'active_consents': sum(
                1 for c in consents.values()
                if c.get_status() == ConsentStatus.ACTIVE
            ),
            'withdrawn_consents': sum(
                1 for c in consents.values()
                if c.get_status() == ConsentStatus.WITHDRAWN
            ),
            'expired_consents': sum(
                1 for c in consents.values()
                if c.get_status() == ConsentStatus.EXPIRED
            ),
            'consent_details': [c.to_dict() for c in consents.values()],
            'withdrawals': [w.to_dict() for w in withdrawals]
        }

    def generate_audit_report(self, days: int = 30) -> Dict:
        """
        Generate audit report for specified period.

        Args:
            days: Number of days to include in report

        Returns:
            Audit report dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = [
            log for log in self.audit_logs
            if log.timestamp >= cutoff_date
        ]

        operations_count = {}
        for log in recent_logs:
            op = log.operation
            operations_count[op] = operations_count.get(op, 0) + 1

        return {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'total_operations': len(recent_logs),
            'operations_by_type': operations_count,
            'logs': [log.to_dict() for log in recent_logs]
        }

    def get_compliance_status(self) -> Dict:
        """
        Get overall consent compliance status.

        Returns:
            Compliance status dictionary
        """
        total_records = len(self.consent_records)
        active_records = sum(
            1 for r in self.consent_records.values()
            if r.get_status() == ConsentStatus.ACTIVE
        )
        withdrawn_records = len(self.withdrawals)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_consent_records': total_records,
            'active_consents': active_records,
            'withdrawn_consents': withdrawn_records,
            'pending_verifications': sum(
                1 for w in self.withdrawals.values()
                if not w.verified
            ),
            'compliance_rate': (
                (active_records / total_records * 100) if total_records > 0 else 0
            )
        }


def main():
    """Example usage and demonstration."""
    # Initialize tracker
    tracker = ComplianceConsentTracker()

    # Create consent records
    consent1 = ConsentRecordEntry(
        record_id=str(uuid.uuid4()),
        individual_id='IND001',
        consent_type=ConsentType.MARKETING,
        granted=True,
        timestamp=datetime.now(),
        channel=ConsentChannel.WEB_FORM,
        ip_address='192.168.1.100',
        user_agent='Mozilla/5.0...'
    )
    tracker.create_consent(consent1)

    consent2 = ConsentRecordEntry(
        record_id=str(uuid.uuid4()),
        individual_id='IND001',
        consent_type=ConsentType.ANALYTICS,
        granted=True,
        timestamp=datetime.now(),
        channel=ConsentChannel.WEB_FORM
    )
    tracker.create_consent(consent2)

    # Verify consent
    is_valid = tracker.verify_consent(consent1.record_id)
    print(f"Consent verification result: {is_valid}")

    # Withdraw consent
    withdrawal_id = tracker.withdraw_consent(
        consent1.record_id,
        reason='No longer interested in marketing'
    )
    print(f"Initiated withdrawal: {withdrawal_id}")

    # Generate reports
    print("\n" + "=" * 80)
    print("CONSENT REPORT FOR INDIVIDUAL")
    print("=" * 80)
    consent_report = tracker.generate_consent_report('IND001')
    print(json.dumps(consent_report, indent=2))

    print("\n" + "=" * 80)
    print("COMPLIANCE STATUS")
    print("=" * 80)
    status = tracker.get_compliance_status()
    print(json.dumps(status, indent=2))

    print("\n" + "=" * 80)
    print("AUDIT REPORT")
    print("=" * 80)
    audit_report = tracker.generate_audit_report(days=30)
    print(json.dumps(audit_report, indent=2))


if __name__ == '__main__':
    main()
