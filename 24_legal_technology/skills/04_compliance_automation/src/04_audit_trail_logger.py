#!/usr/bin/env python3
"""
Audit Trail Logger
Comprehensive logging system for compliance audit trails
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

class AuditEventType(Enum):
    """Types of events to audit"""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONSENT_CHANGE = "consent_change"
    USER_AUTHENTICATION = "user_authentication"
    PERMISSION_CHANGE = "permission_change"
    POLICY_UPDATE = "policy_update"
    CONFIGURATION_CHANGE = "configuration_change"
    BREACH_DETECTION = "breach_detection"
    COMPLIANCE_REPORT = "compliance_report"

class AuditTrailLogger:
    """Comprehensive audit trail logging for compliance"""

    def __init__(self, log_store: Optional[Dict] = None):
        self.logs: List[Dict] = []
        self.log_store = log_store or {}
        self.integrity_chain = []

    def log_event(self, event_type: AuditEventType, user_id: str, resource_id: str,
                 description: str, data_elements_affected: Optional[List[str]] = None,
                 metadata: Optional[Dict] = None, ip_address: Optional[str] = None) -> str:
        """
        Log a compliance-relevant event

        Args:
            event_type: Type of event
            user_id: User performing action (hashed)
            resource_id: Resource affected
            description: Event description
            data_elements_affected: List of data elements affected
            metadata: Additional metadata
            ip_address: Source IP address

        Returns:
            Event ID
        """
        event_id = self._generate_event_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        log_entry = {
            'event_id': event_id,
            'timestamp': timestamp,
            'event_type': event_type.value,
            'user_id': self._hash_user_id(user_id),
            'resource_id': resource_id,
            'description': description,
            'data_elements_affected': data_elements_affected or [],
            'ip_address': self._hash_ip(ip_address) if ip_address else None,
            'metadata': metadata or {},
            'previous_hash': self.integrity_chain[-1] if self.integrity_chain else None
        }

        # Calculate hash for integrity verification
        log_entry['entry_hash'] = self._calculate_entry_hash(log_entry)

        # Add to integrity chain
        self.integrity_chain.append(log_entry['entry_hash'])

        # Store log
        self.logs.append(log_entry)
        self._persist_log(event_id, log_entry)

        return event_id

    def log_data_subject_access_request(self, request_id: str, subject_id: str,
                                       data_retrieved: List[str], processed_by: str) -> str:
        """Log data subject access request"""
        return self.log_event(
            AuditEventType.DATA_ACCESS,
            user_id=processed_by,
            resource_id=request_id,
            description=f'Data subject access request processed',
            data_elements_affected=data_retrieved,
            metadata={
                'request_type': 'subject_access_request',
                'subject_id_hash': hashlib.sha256(subject_id.encode()).hexdigest(),
                'data_provided': len(data_retrieved),
                'response_method': 'email'
            }
        )

    def log_data_deletion_request(self, request_id: str, subject_id: str,
                                 systems_affected: List[str], processed_by: str) -> str:
        """Log data deletion (right to be forgotten) request"""
        return self.log_event(
            AuditEventType.DATA_DELETION,
            user_id=processed_by,
            resource_id=request_id,
            description='Data deletion request processed',
            data_elements_affected=systems_affected,
            metadata={
                'request_type': 'deletion_request',
                'subject_id_hash': hashlib.sha256(subject_id.encode()).hexdigest(),
                'systems_processed': systems_affected,
                'deletion_status': 'completed'
            }
        )

    def log_consent_change(self, consent_id: str, user_id: str, consent_type: str,
                          granted: bool, previous_state: str) -> str:
        """Log consent change event"""
        return self.log_event(
            AuditEventType.CONSENT_CHANGE,
            user_id=user_id,
            resource_id=consent_id,
            description=f'Consent {consent_type} {"granted" if granted else "withdrawn"}',
            metadata={
                'consent_type': consent_type,
                'new_state': 'granted' if granted else 'withdrawn',
                'previous_state': previous_state,
                'ip_address': '0.0.0.0'  # Would be captured in real scenario
            }
        )

    def log_breach_detection(self, breach_id: str, affected_individuals: int,
                           data_categories: List[str], severity: str,
                           detected_by: str) -> str:
        """Log breach detection event"""
        return self.log_event(
            AuditEventType.BREACH_DETECTION,
            user_id=detected_by,
            resource_id=breach_id,
            description=f'Data breach detected - severity: {severity}',
            data_elements_affected=data_categories,
            metadata={
                'breach_id': breach_id,
                'affected_individuals': affected_individuals,
                'severity': severity,
                'detection_method': 'automated_monitoring',
                'containment_status': 'in_progress'
            }
        )

    def log_policy_update(self, policy_name: str, changes: Dict, updated_by: str) -> str:
        """Log policy update event"""
        return self.log_event(
            AuditEventType.POLICY_UPDATE,
            user_id=updated_by,
            resource_id=policy_name,
            description=f'Policy updated: {policy_name}',
            metadata={
                'policy_name': policy_name,
                'changes_summary': str(changes),
                'effective_date': datetime.now(timezone.utc).isoformat(),
                'review_required': 'yes'
            }
        )

    def log_authentication_event(self, user_id: str, success: bool,
                                ip_address: Optional[str] = None,
                                method: str = 'password') -> str:
        """Log authentication event"""
        return self.log_event(
            AuditEventType.USER_AUTHENTICATION,
            user_id=user_id,
            resource_id=f'auth_{user_id}',
            description=f'Authentication {"successful" if success else "failed"}',
            metadata={
                'success': success,
                'method': method,
                'ip_address': ip_address
            },
            ip_address=ip_address
        )

    def generate_audit_report(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            event_type_filter: Optional[str] = None) -> Dict:
        """Generate audit report for compliance"""
        filtered_logs = self.logs

        # Filter by date range
        if start_date:
            start = datetime.fromisoformat(start_date)
            filtered_logs = [l for l in filtered_logs
                           if datetime.fromisoformat(l['timestamp']) >= start]

        if end_date:
            end = datetime.fromisoformat(end_date)
            filtered_logs = [l for l in filtered_logs
                           if datetime.fromisoformat(l['timestamp']) <= end]

        # Filter by event type
        if event_type_filter:
            filtered_logs = [l for l in filtered_logs
                           if l['event_type'] == event_type_filter]

        # Aggregate statistics
        event_type_counts = {}
        for log in filtered_logs:
            event_type = log['event_type']
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        return {
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'period': {
                'start': start_date,
                'end': end_date
            },
            'total_events': len(filtered_logs),
            'event_type_summary': event_type_counts,
            'events': filtered_logs,
            'integrity_verified': self._verify_audit_trail_integrity()
        }

    def verify_audit_trail_integrity(self) -> Dict:
        """Verify audit trail has not been tampered with"""
        return {
            'integrity_verified': self._verify_audit_trail_integrity(),
            'total_entries': len(self.logs),
            'integrity_chain_length': len(self.integrity_chain),
            'last_verified': datetime.now(timezone.utc).isoformat()
        }

    def export_for_regulatory_submission(self, regulatory_body: str) -> Dict:
        """Export audit logs formatted for regulatory submission"""
        return {
            'submission_date': datetime.now(timezone.utc).isoformat(),
            'regulatory_body': regulatory_body,
            'audit_logs': self.logs,
            'integrity_verification': self.verify_audit_trail_integrity(),
            'custodian': 'Data Protection Officer',
            'certification': f'Certified as accurate and complete on {datetime.now().date()}'
        }

    def search_logs(self, event_type: Optional[str] = None,
                   user_id_hash: Optional[str] = None,
                   resource_id: Optional[str] = None) -> List[Dict]:
        """Search audit logs"""
        results = self.logs

        if event_type:
            results = [l for l in results if l['event_type'] == event_type]

        if user_id_hash:
            results = [l for l in results if l['user_id'] == user_id_hash]

        if resource_id:
            results = [l for l in results if l['resource_id'] == resource_id]

        return results

    def get_user_activity_history(self, user_id_hash: str) -> Dict:
        """Get complete activity history for a user"""
        user_logs = self.search_logs(user_id_hash=user_id_hash)

        return {
            'user_id_hash': user_id_hash,
            'total_events': len(user_logs),
            'first_event': user_logs[0]['timestamp'] if user_logs else None,
            'last_event': user_logs[-1]['timestamp'] if user_logs else None,
            'activities_by_type': self._count_by_type(user_logs),
            'events': user_logs
        }

    # Private helper methods
    @staticmethod
    def _generate_event_id() -> str:
        """Generate unique event ID"""
        import uuid
        return f"EVT_{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def _hash_user_id(user_id: str) -> str:
        """Hash user ID for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    @staticmethod
    def _hash_ip(ip_address: str) -> str:
        """Hash IP address for privacy"""
        return hashlib.sha256(ip_address.encode()).hexdigest()[:16]

    @staticmethod
    def _calculate_entry_hash(entry: Dict) -> str:
        """Calculate hash of log entry for integrity verification"""
        entry_str = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(entry_str.encode()).hexdigest()

    def _verify_audit_trail_integrity(self) -> bool:
        """Verify audit trail has not been modified"""
        for i, log in enumerate(self.logs):
            # Recalculate hash
            entry_copy = {k: v for k, v in log.items() if k != 'entry_hash'}
            expected_hash = self._calculate_entry_hash(entry_copy)

            if expected_hash != log['entry_hash']:
                return False

            # Verify chain
            if i > 0 and log['previous_hash'] != self.logs[i-1]['entry_hash']:
                return False

        return True

    def _persist_log(self, event_id: str, log_entry: Dict) -> None:
        """Persist log entry (would write to secure storage)"""
        self.log_store[event_id] = log_entry

    @staticmethod
    def _count_by_type(logs: List[Dict]) -> Dict:
        """Count logs by event type"""
        counts = {}
        for log in logs:
            event_type = log['event_type']
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts


def main():
    logger = AuditTrailLogger()

    # Log various compliance events
    logger.log_authentication_event('user_001', success=True, ip_address='192.168.1.100')
    logger.log_data_subject_access_request('req_001', 'subject_123', ['name', 'email'], 'admin_001')
    logger.log_consent_change('cons_001', 'user_001', 'marketing_email', True, 'unknown')
    logger.log_breach_detection('breach_2024_001', 5000, ['name', 'email', 'phone'], 'high', 'security_team')
    logger.log_policy_update('privacy_policy', {'version': '2.1', 'effective_date': '2024-02-01'}, 'dpo_001')

    # Generate report
    report = logger.generate_audit_report()
    print(json.dumps(report, indent=2, default=str))

    # Verify integrity
    integrity = logger.verify_audit_trail_integrity()
    print(json.dumps(integrity, indent=2, default=str))


if __name__ == '__main__':
    main()
