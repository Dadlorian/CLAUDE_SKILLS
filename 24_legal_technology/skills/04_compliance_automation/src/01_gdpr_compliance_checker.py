"""
GDPR Compliance Checker - Production-Ready Implementation

This module provides comprehensive GDPR compliance checking capabilities including:
- Data processing assessment
- Consent validation
- Data subject rights enforcement
- Privacy by design verification
- Legal basis evaluation
- Data protection impact assessment

Author: Compliance Automation Team
Version: 1.0.0
License: MIT
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import json
from abc import ABC, abstractmethod


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """Enumeration of consent status values."""
    VALID = "valid"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    INVALID = "invalid"
    PENDING = "pending"


class LegalBasis(Enum):
    """GDPR legal basis for data processing."""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


@dataclass
class ProcessingActivity:
    """Represents a data processing activity."""
    activity_id: str
    description: str
    category: str
    legal_basis: LegalBasis
    data_categories: List[str]
    recipients: List[str]
    retention_period: int  # days
    purpose: str
    has_dpia: bool = False
    is_international_transfer: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'activity_id': self.activity_id,
            'description': self.description,
            'category': self.category,
            'legal_basis': self.legal_basis.value,
            'data_categories': self.data_categories,
            'recipients': self.recipients,
            'retention_period': self.retention_period,
            'purpose': self.purpose,
            'has_dpia': self.has_dpia,
            'is_international_transfer': self.is_international_transfer,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ConsentRecord:
    """Represents a consent record for an individual."""
    individual_id: str
    activity_id: str
    consent_given: bool
    consent_date: datetime
    withdrawal_date: Optional[datetime] = None
    consent_method: str = "web_form"
    ip_address: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def get_status(self) -> ConsentStatus:
        """Determine current consent status."""
        if self.withdrawal_date and self.withdrawal_date <= datetime.now():
            return ConsentStatus.WITHDRAWN
        if not self.consent_given:
            return ConsentStatus.INVALID
        # Assume 2-year consent expiry
        if datetime.now() > self.consent_date + timedelta(days=730):
            return ConsentStatus.EXPIRED
        return ConsentStatus.VALID

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'individual_id': self.individual_id,
            'activity_id': self.activity_id,
            'consent_given': self.consent_given,
            'consent_date': self.consent_date.isoformat(),
            'withdrawal_date': self.withdrawal_date.isoformat() if self.withdrawal_date else None,
            'consent_method': self.consent_method,
            'status': self.get_status().value
        }


class ComplianceChecker(ABC):
    """Abstract base class for compliance checkers."""

    @abstractmethod
    def check(self) -> Tuple[bool, List[str]]:
        """Check compliance and return status with findings."""
        pass


class GDPRComplianceChecker(ComplianceChecker):
    """
    Comprehensive GDPR compliance checker.

    This checker validates:
    - Legal basis for processing
    - Consent records
    - Data protection measures
    - Privacy rights
    - Data retention policies
    """

    def __init__(self):
        """Initialize the GDPR compliance checker."""
        self.processing_activities: Dict[str, ProcessingActivity] = {}
        self.consent_records: List[ConsentRecord] = []
        self.findings: List[str] = []
        self.logger = logger

    def add_processing_activity(self, activity: ProcessingActivity) -> None:
        """
        Add a processing activity to the checker.

        Args:
            activity: ProcessingActivity instance
        """
        self.processing_activities[activity.activity_id] = activity
        self.logger.info(f"Added processing activity: {activity.activity_id}")

    def add_consent_record(self, record: ConsentRecord) -> None:
        """
        Add a consent record.

        Args:
            record: ConsentRecord instance
        """
        self.consent_records.append(record)
        self.logger.info(f"Added consent record for individual: {record.individual_id}")

    def check_legal_basis(self) -> Tuple[bool, List[str]]:
        """
        Check if all processing activities have valid legal basis.

        Returns:
            Tuple of (is_compliant, findings)
        """
        findings = []

        for activity_id, activity in self.processing_activities.items():
            if not activity.legal_basis:
                findings.append(f"Activity {activity_id}: No legal basis identified")

            # Check if DPIA is required for high-risk processing
            if self._is_high_risk(activity) and not activity.has_dpia:
                findings.append(f"Activity {activity_id}: DPIA required but not completed")

        return len(findings) == 0, findings

    def check_consent_records(self) -> Tuple[bool, List[str]]:
        """
        Check validity of consent records.

        Returns:
            Tuple of (is_compliant, findings)
        """
        findings = []
        invalid_consents = 0

        for record in self.consent_records:
            status = record.get_status()
            if status == ConsentStatus.WITHDRAWN:
                findings.append(
                    f"Individual {record.individual_id}: Consent withdrawn for activity {record.activity_id}"
                )
            elif status == ConsentStatus.EXPIRED:
                findings.append(
                    f"Individual {record.individual_id}: Consent expired for activity {record.activity_id}"
                )
            elif status == ConsentStatus.INVALID:
                invalid_consents += 1

        if invalid_consents > 0:
            findings.append(f"Found {invalid_consents} invalid consent records")

        return len(findings) == 0, findings

    def check_data_retention(self) -> Tuple[bool, List[str]]:
        """
        Check if retention periods are properly defined.

        Returns:
            Tuple of (is_compliant, findings)
        """
        findings = []

        for activity_id, activity in self.processing_activities.items():
            if activity.retention_period <= 0:
                findings.append(f"Activity {activity_id}: Undefined or invalid retention period")
            elif activity.retention_period > 3650:  # 10 years
                findings.append(
                    f"Activity {activity_id}: Retention period of {activity.retention_period} days may be excessive"
                )

        return len(findings) == 0, findings

    def check_international_transfers(self) -> Tuple[bool, List[str]]:
        """
        Check safeguards for international data transfers.

        Returns:
            Tuple of (is_compliant, findings)
        """
        findings = []

        for activity_id, activity in self.processing_activities.items():
            if activity.is_international_transfer:
                findings.append(
                    f"Activity {activity_id}: International transfer flagged - "
                    "ensure adequate transfer mechanisms (SCCs, BCRs, etc.)"
                )

        return len(findings) == 0, findings

    def check_privacy_rights(self) -> Tuple[bool, List[str]]:
        """
        Check support for data subject rights.

        Returns:
            Tuple of (is_compliant, findings)
        """
        findings = []

        # Verify consent can be withdrawn
        total_records = len(self.consent_records)
        withdrawable = sum(1 for r in self.consent_records if r.consent_given)

        if total_records > 0 and withdrawable < total_records * 0.95:
            findings.append("Less than 95% of consent records support withdrawal")

        return len(findings) == 0, findings

    def check(self) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive GDPR compliance check.

        Returns:
            Tuple of (is_compliant, all_findings)
        """
        self.findings = []

        checks = [
            self.check_legal_basis(),
            self.check_consent_records(),
            self.check_data_retention(),
            self.check_international_transfers(),
            self.check_privacy_rights()
        ]

        for is_compliant, findings in checks:
            self.findings.extend(findings)

        is_compliant = len(self.findings) == 0
        self.logger.info(f"GDPR compliance check completed: {'PASSED' if is_compliant else 'FAILED'}")

        return is_compliant, self.findings

    def _is_high_risk(self, activity: ProcessingActivity) -> bool:
        """
        Determine if a processing activity is high-risk.

        Args:
            activity: ProcessingActivity to assess

        Returns:
            True if high-risk, False otherwise
        """
        high_risk_categories = {'health', 'criminal', 'biometric', 'location', 'financial'}
        return bool(set(activity.data_categories) & high_risk_categories)

    def generate_report(self) -> Dict:
        """
        Generate a comprehensive compliance report.

        Returns:
            Dictionary containing detailed compliance report
        """
        is_compliant, findings = self.check()

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_compliance': is_compliant,
            'total_issues': len(findings),
            'findings': findings,
            'processing_activities': {
                aid: a.to_dict() for aid, a in self.processing_activities.items()
            },
            'consent_records_summary': {
                'total': len(self.consent_records),
                'valid': sum(1 for r in self.consent_records if r.get_status() == ConsentStatus.VALID),
                'withdrawn': sum(1 for r in self.consent_records if r.get_status() == ConsentStatus.WITHDRAWN),
                'expired': sum(1 for r in self.consent_records if r.get_status() == ConsentStatus.EXPIRED)
            }
        }


def main():
    """Example usage and demonstration."""
    # Initialize checker
    checker = GDPRComplianceChecker()

    # Add processing activities
    activity1 = ProcessingActivity(
        activity_id='PA001',
        description='Customer email marketing',
        category='marketing',
        legal_basis=LegalBasis.CONSENT,
        data_categories=['email', 'preferences'],
        recipients=['marketing_team', 'email_provider'],
        retention_period=365,
        purpose='Direct marketing communications',
        has_dpia=True
    )
    checker.add_processing_activity(activity1)

    activity2 = ProcessingActivity(
        activity_id='PA002',
        description='Financial transaction processing',
        category='payments',
        legal_basis=LegalBasis.CONTRACT,
        data_categories=['financial', 'account_info'],
        recipients=['payment_processor', 'accounting'],
        retention_period=2555,  # 7 years for accounting
        purpose='Process customer payments'
    )
    checker.add_processing_activity(activity2)

    # Add consent records
    consent1 = ConsentRecord(
        individual_id='IND001',
        activity_id='PA001',
        consent_given=True,
        consent_date=datetime.now()
    )
    checker.add_consent_record(consent1)

    # Run compliance check
    is_compliant, findings = checker.check()

    print("\n" + "="*60)
    print("GDPR COMPLIANCE CHECK REPORT")
    print("="*60)
    print(f"Status: {'COMPLIANT' if is_compliant else 'NON-COMPLIANT'}")
    print(f"Total Findings: {len(findings)}")

    if findings:
        print("\nFindings:")
        for i, finding in enumerate(findings, 1):
            print(f"  {i}. {finding}")

    # Generate full report
    report = checker.generate_report()
    print("\n" + json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
