# Audit Logging and Compliance Patterns

## Table of Contents
1. [Overview](#overview)
2. [Compliance Requirements](#compliance-requirements)
3. [Audit Trail Architecture](#audit-trail-architecture)
4. [Immutable Logging](#immutable-logging)
5. [Sensitive Data Handling](#sensitive-data-handling)
6. [Regulatory Patterns](#regulatory-patterns)
7. [Implementation Examples](#implementation-examples)
8. [Monitoring & Alerting](#monitoring--alerting)

## Overview

Audit logging is the foundation of financial compliance. Every action that affects financial data must be recorded, traceable, and immutable. This pattern details how to build production-grade audit systems for banking, payments, and fintech applications.

### Why Audit Logging Matters

```
Regulatory Requirements:
├─ PCI-DSS (Payment Cards)
│  └─ Log all access to cardholder data
├─ SOX (Public Companies)
│  └─ Audit trail for financial transactions
├─ GDPR (Privacy)
│  └─ Track data access and modifications
├─ HIPAA (Healthcare)
│  └─ Patient data access logging
└─ FinCEN (Anti-Money Laundering)
   └─ Transaction monitoring and reporting

Business Requirements:
├─ Fraud Detection
├─ Dispute Resolution
├─ Tax Compliance
├─ Internal Audits
└─ Regulatory Exams
```

## Compliance Requirements

### Framework Comparison

```
PCI-DSS:
- Log all access to cardholder data
- Protect audit logs from modification
- Keep logs for at least 1 year (6 months online)
- Review logs for anomalies

SOX (Sarbanes-Oxley):
- Maintain complete audit trail of financial transactions
- Document who changed what, when, and why
- Preserve logs for 7+ years
- Segregation of duties

GDPR (GDPR):
- Log data subject access
- Track consent changes
- Document data processing
- Right to be forgotten considerations

HIPAA (Healthcare):
- Audit logs for 6+ years
- Track access to PHI (Protected Health Information)
- Activity monitoring and reporting
```

## Audit Trail Architecture

### Immutable Append-Only Log

```
┌────────────────────────────────────────────┐
│        Immutable Audit Log (WORM)          │
│   Write Once, Read Many                    │
├────────────────────────────────────────────┤
│                                             │
│  Entry 1: Transfer initiated                │
│  ├─ Timestamp: 2024-01-15 10:23:45         │
│  ├─ User: alice@company.com                │
│  ├─ Action: transfer                       │
│  ├─ Amount: $1000                          │
│  ├─ Hash: 0x3f4a5b...                      │
│  └─ PrevHash: 0xd2e1f8...                  │
│                                             │
│  Entry 2: Transfer authorized               │
│  ├─ Timestamp: 2024-01-15 10:24:12         │
│  ├─ User: bob@company.com                  │
│  ├─ Action: authorize                      │
│  ├─ Approver: system_admin                 │
│  ├─ Hash: 0x5c7a9e...                      │
│  └─ PrevHash: 0x3f4a5b...  ◄─ Chains back │
│                                             │
│  Entry 3: Transfer completed                │
│  ├─ Timestamp: 2024-01-15 10:25:00         │
│  ├─ User: processor@system.com             │
│  ├─ Action: complete                       │
│  ├─ Status: succeeded                      │
│  ├─ Hash: 0x8b2e4f...                      │
│  └─ PrevHash: 0x5c7a9e...  ◄─ Chains back │
│                                             │
└────────────────────────────────────────────┘
```

### Architecture Components

```
┌──────────────────────────────────────────────────────────┐
│            Transaction Processing                        │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │   Audit Event Generator  │
        │ - User/service identity  │
        │ - Action details         │
        │ - Timestamp              │
        │ - Request metadata       │
        └──────────────┬───────────┘
                       │
        ┌──────────────▼───────────┐
        │ Data Classification      │
        │ - Sensitive/non-sensitive│
        │ - PII/non-PII            │
        │ - Cardholder data        │
        └──────────────┬───────────┘
                       │
    ┌──────────────────┴──────────────────┐
    ▼                                      ▼
┌──────────────────────┐      ┌──────────────────────┐
│  Write to Local Log  │      │  Stream to Central   │
│  (Redundancy)        │      │  Audit Service       │
└──────────────┬───────┘      └──────────────┬───────┘
               │                             │
               └──────────────┬──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Immutable Store  │
                    │  (Event Store)    │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
       ┌────────┐        ┌────────┐        ┌────────┐
       │Backup  │        │Archival│        │Alerts  │
       │Storage │        │System  │        │Engine  │
       └────────┘        └────────┘        └────────┘
```

## Immutable Logging

### Write-Once-Read-Many (WORM) Store

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json
from enum import Enum

class LogLevel(Enum):
    CRITICAL = "CRITICAL"  # Regulatory requirement
    HIGH = "HIGH"           # Important compliance event
    MEDIUM = "MEDIUM"       # Normal audit event
    LOW = "LOW"             # Informational

class DataClassification(Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"  # Payment card data, PII

@dataclass
class AuditLogEntry:
    entry_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    changes: Dict[str, Any]
    status: str  # 'success', 'failure'
    previous_hash: str = None  # Chain to previous entry
    current_hash: str = None   # This entry's hash
    classification: DataClassification = DataClassification.CONFIDENTIAL
    log_level: LogLevel = LogLevel.MEDIUM
    metadata: Dict[str, Any] = None

    def compute_hash(self) -> str:
        """Compute immutable hash of this entry"""
        content = {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'changes': self.changes,
            'previous_hash': self.previous_hash
        }

        # Create canonical JSON representation
        canonical = json.dumps(content, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

class ImmutableAuditStore:
    """Write-Once-Read-Many audit log storage"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        """Create immutable audit log schema"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                entry_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                changes JSONB NOT NULL,
                status TEXT NOT NULL,
                classification TEXT NOT NULL,
                log_level TEXT NOT NULL,
                previous_hash TEXT,
                current_hash TEXT NOT NULL UNIQUE,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (created_at = CURRENT_TIMESTAMP)
            );

            -- Immutable: no updates, only inserts
            CREATE RULE audit_log_no_update AS
            ON UPDATE TO audit_log DO INSTEAD NOTHING;

            CREATE RULE audit_log_no_delete AS
            ON DELETE TO audit_log DO INSTEAD NOTHING;

            -- Indexes for compliance queries
            CREATE INDEX idx_user_id ON audit_log(user_id);
            CREATE INDEX idx_resource ON audit_log(resource_type, resource_id);
            CREATE INDEX idx_timestamp ON audit_log(timestamp DESC);
            CREATE INDEX idx_action ON audit_log(action);
            CREATE INDEX idx_classification ON audit_log(classification);
        ''')

    def append_entry(self, entry: AuditLogEntry) -> bool:
        """Append entry to immutable log"""

        # Compute hash
        entry.current_hash = entry.compute_hash()

        try:
            self.db.execute('''
                INSERT INTO audit_log (
                    entry_id, timestamp, user_id, action,
                    resource_type, resource_id, changes, status,
                    classification, log_level, previous_hash,
                    current_hash, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                entry.entry_id,
                entry.timestamp,
                entry.user_id,
                entry.action,
                entry.resource_type,
                entry.resource_id,
                json.dumps(entry.changes),
                entry.status,
                entry.classification.value,
                entry.log_level.value,
                entry.previous_hash,
                entry.current_hash,
                json.dumps(entry.metadata or {})
            ))

            return True

        except Exception as e:
            raise Exception(f"Failed to append audit entry: {str(e)}")

    def verify_chain_integrity(self) -> bool:
        """Verify cryptographic chain integrity"""

        entries = self.db.query('''
            SELECT entry_id, previous_hash, current_hash
            FROM audit_log
            ORDER BY timestamp ASC
        ''')

        for i, entry in enumerate(entries):
            if i > 0:
                # Verify this entry links to previous
                prev_entry = entries[i-1]
                if entry['previous_hash'] != prev_entry['current_hash']:
                    return False  # Chain broken!

        return True  # Chain intact

    def get_entry_by_id(self, entry_id: str) -> Optional[Dict]:
        """Get specific audit entry"""
        result = self.db.query('''
            SELECT * FROM audit_log WHERE entry_id = %s
        ''', (entry_id,))

        return result[0] if result else None

    def audit_trail_for_resource(self, resource_type: str,
                                 resource_id: str) -> list:
        """Get full audit trail for a resource"""
        return self.db.query('''
            SELECT * FROM audit_log
            WHERE resource_type = %s AND resource_id = %s
            ORDER BY timestamp ASC
        ''', (resource_type, resource_id))
```

## Sensitive Data Handling

### Data Masking and Tokenization

```python
import re

class SensitiveDataMasker:
    """Mask sensitive data in audit logs"""

    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """Mask credit card number"""
        if not card_number or len(card_number) < 4:
            return "****"
        return f"****{card_number[-4:]}"

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""
        if '@' not in email:
            return "***@***"
        name, domain = email.split('@')
        masked_name = name[0] + '*' * (len(name)-2) + name[-1]
        return f"{masked_name}@{domain}"

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """Mask SSN (US Social Security Number)"""
        if not ssn or len(ssn) < 4:
            return "***-**-****"
        return f"***-**-{ssn[-4:]}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 4:
            return "***-****"
        return f"***-***-{digits[-4:]}"

    @staticmethod
    def mask_bank_account(account: str) -> str:
        """Mask bank account number"""
        if len(account) < 4:
            return "****"
        return f"****{account[-4:]}"

    @staticmethod
    def mask_changes(changes: dict) -> dict:
        """Mask sensitive fields in change log"""
        sensitive_fields = {
            'credit_card_number', 'ssn', 'password',
            'email', 'phone', 'bank_account', 'token'
        }

        masked = {}
        for key, value in changes.items():
            if key.lower() in sensitive_fields or any(
                s in key.lower() for s in sensitive_fields
            ):
                # Mask value
                if isinstance(value, str):
                    if 'credit_card' in key.lower():
                        masked[key] = SensitiveDataMasker.mask_credit_card(value)
                    elif 'email' in key.lower():
                        masked[key] = SensitiveDataMasker.mask_email(value)
                    elif 'ssn' in key.lower():
                        masked[key] = SensitiveDataMasker.mask_ssn(value)
                    elif 'phone' in key.lower():
                        masked[key] = SensitiveDataMasker.mask_phone(value)
                    elif 'account' in key.lower():
                        masked[key] = SensitiveDataMasker.mask_bank_account(value)
                    else:
                        masked[key] = "***"
                else:
                    masked[key] = "***"
            else:
                masked[key] = value

        return masked

class AuditLogGenerator:
    """Generate audit logs with data masking"""

    def __init__(self, audit_store: ImmutableAuditStore,
                 data_masker: SensitiveDataMasker):
        self.audit_store = audit_store
        self.masker = data_masker

    def log_payment(self, user_id: str, payment_id: str,
                   amount: float, card_last4: str, status: str):
        """Log payment with masked sensitive data"""

        # Mask sensitive fields
        changes = {
            'payment_id': payment_id,
            'amount': amount,
            'card': self.masker.mask_credit_card(f"****{card_last4}"),
            'status': status
        }

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action='process_payment',
            resource_type='payment',
            resource_id=payment_id,
            changes=changes,
            status='success',
            classification=DataClassification.RESTRICTED,
            log_level=LogLevel.HIGH
        )

        self.audit_store.append_entry(entry)

    def log_customer_access(self, user_id: str, customer_id: str,
                           fields_accessed: list):
        """Log customer data access"""

        # Mask sensitive fields accessed
        masked_fields = [
            f for f in fields_accessed
            if f not in ['id', 'name', 'created_at']
        ]

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action='access_customer',
            resource_type='customer',
            resource_id=customer_id,
            changes={'fields_accessed': masked_fields},
            status='success',
            classification=DataClassification.CONFIDENTIAL,
            log_level=LogLevel.MEDIUM
        )

        self.audit_store.append_entry(entry)
```

## Regulatory Patterns

### PCI-DSS Compliance Pattern

```python
class PCIComplianceAuditor:
    """Ensure PCI-DSS compliance"""

    def __init__(self, audit_store: ImmutableAuditStore):
        self.audit_store = audit_store

    def verify_cardholder_data_access(self, time_window_days: int = 1) -> dict:
        """Verify all cardholder data access is logged"""

        # Query for payment card operations
        start_date = datetime.utcnow() - timedelta(days=time_window_days)

        entries = self.audit_store.db.query('''
            SELECT * FROM audit_log
            WHERE classification = 'RESTRICTED'
            AND action IN ('process_payment', 'store_card', 'access_card')
            AND timestamp >= %s
        ''', (start_date,))

        report = {
            'total_cardholder_operations': len(entries),
            'unique_users': len(set(e['user_id'] for e in entries)),
            'operations_by_type': {},
            'failed_operations': 0,
            'compliance_check': 'PASS'
        }

        for entry in entries:
            action = entry['action']
            report['operations_by_type'][action] = \
                report['operations_by_type'].get(action, 0) + 1

            if entry['status'] != 'success':
                report['failed_operations'] += 1

        # Compliance check: all operations logged?
        if report['total_cardholder_operations'] == 0:
            report['compliance_check'] = 'FAIL - No cardholder operations logged'

        return report

    def generate_pci_report(self, start_date: datetime,
                           end_date: datetime) -> str:
        """Generate PCI-DSS compliance report"""

        entries = self.audit_store.db.query('''
            SELECT COUNT(*) as total, classification
            FROM audit_log
            WHERE timestamp BETWEEN %s AND %s
            GROUP BY classification
        ''', (start_date, end_date))

        report = f"""
PCI-DSS AUDIT REPORT
Generated: {datetime.utcnow()}
Period: {start_date} - {end_date}

SUMMARY
=======
Total Audit Entries: {sum(e['total'] for e in entries)}
"""

        for entry in entries:
            report += f"\n{entry['classification']}: {entry['total']}"

        return report
```

### GDPR Right to Be Forgotten

```python
class GDPRDataController:
    """Handle GDPR compliance"""

    def __init__(self, audit_store: ImmutableAuditStore, database):
        self.audit_store = audit_store
        self.db = database

    def process_right_to_be_forgotten(self, data_subject_id: str) -> bool:
        """Handle GDPR right to be forgotten"""

        # Step 1: Create audit entry documenting the request
        audit_entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id='gdpr_processor',
            action='right_to_be_forgotten',
            resource_type='data_subject',
            resource_id=data_subject_id,
            changes={'status': 'requested'},
            status='success',
            classification=DataClassification.RESTRICTED,
            log_level=LogLevel.CRITICAL
        )

        self.audit_store.append_entry(audit_entry)

        # Step 2: Delete personal data (but audit trail remains)
        self.db.execute('''
            DELETE FROM customers WHERE id = %s
        ''', (data_subject_id,))

        # Step 3: Create completion entry
        completion_entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id='gdpr_processor',
            action='right_to_be_forgotten',
            resource_type='data_subject',
            resource_id=data_subject_id,
            changes={'status': 'completed'},
            status='success',
            classification=DataClassification.RESTRICTED,
            log_level=LogLevel.CRITICAL
        )

        self.audit_store.append_entry(completion_entry)

        return True

    def export_user_data(self, data_subject_id: str) -> dict:
        """GDPR: Right to data portability"""

        # Get all audit entries related to this subject
        entries = self.audit_store.audit_trail_for_resource(
            'customer',
            data_subject_id
        )

        export = {
            'data_subject_id': data_subject_id,
            'export_date': datetime.utcnow().isoformat(),
            'audit_trail': entries
        }

        return export
```

## Implementation Examples

### Complete Audit Service

```python
class ComprehensiveAuditService:
    """Production-grade audit service"""

    def __init__(self, database, encryption_service=None):
        self.audit_store = ImmutableAuditStore(database)
        self.masker = SensitiveDataMasker()
        self.encryption = encryption_service
        self.db = database

    def log_transaction(self, transaction: dict, user_id: str,
                       status: str = 'success', error: str = None):
        """Log financial transaction"""

        changes = {
            'transaction_id': transaction['id'],
            'amount': transaction['amount'],
            'from_account': self.masker.mask_bank_account(transaction['from']),
            'to_account': self.masker.mask_bank_account(transaction['to']),
            'type': transaction['type']
        }

        if error:
            changes['error'] = error

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action='execute_transaction',
            resource_type='transaction',
            resource_id=transaction['id'],
            changes=changes,
            status=status,
            classification=DataClassification.RESTRICTED,
            log_level=LogLevel.HIGH
        )

        self.audit_store.append_entry(entry)

    def log_account_change(self, account_id: str, user_id: str,
                          old_values: dict, new_values: dict):
        """Log account changes"""

        changes = {}
        for key in new_values:
            if key in old_values and old_values[key] != new_values[key]:
                changes[key] = {
                    'old': old_values[key],
                    'new': new_values[key]
                }

        # Mask sensitive changes
        masked_changes = self.masker.mask_changes(
            {k: str(v) for k, v in changes.items()}
        )

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action='update_account',
            resource_type='account',
            resource_id=account_id,
            changes=masked_changes,
            status='success',
            classification=DataClassification.CONFIDENTIAL,
            log_level=LogLevel.HIGH
        )

        self.audit_store.append_entry(entry)

    def log_policy_change(self, policy_id: str, user_id: str,
                         old_policy: dict, new_policy: dict):
        """Log policy/configuration changes"""

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action='update_policy',
            resource_type='policy',
            resource_id=policy_id,
            changes={
                'old': old_policy,
                'new': new_policy
            },
            status='success',
            classification=DataClassification.INTERNAL,
            log_level=LogLevel.HIGH,
            metadata={'requires_approval': True}
        )

        self.audit_store.append_entry(entry)
```

## Monitoring & Alerting

### Compliance Monitoring

```python
class ComplianceMonitor:
    """Monitor compliance violations"""

    def __init__(self, audit_store: ImmutableAuditStore):
        self.audit_store = audit_store

    def detect_unusual_access(self) -> list:
        """Detect unusual data access patterns"""

        # Get access patterns for last 24 hours
        start_date = datetime.utcnow() - timedelta(hours=24)

        entries = self.audit_store.db.query('''
            SELECT user_id, COUNT(*) as access_count
            FROM audit_log
            WHERE action IN ('access_customer', 'access_account')
            AND timestamp >= %s
            GROUP BY user_id
            ORDER BY access_count DESC
        ''', (start_date,))

        # Calculate baseline (mean + 2 * std_dev)
        access_counts = [e['access_count'] for e in entries]
        mean = sum(access_counts) / len(access_counts) if access_counts else 0
        variance = sum((x - mean)**2 for x in access_counts) / len(access_counts)
        std_dev = variance ** 0.5

        threshold = mean + (2 * std_dev)

        # Flag unusual access
        unusual = []
        for entry in entries:
            if entry['access_count'] > threshold:
                unusual.append({
                    'user_id': entry['user_id'],
                    'access_count': entry['access_count'],
                    'threshold': threshold,
                    'severity': 'HIGH' if entry['access_count'] > (threshold * 2) else 'MEDIUM'
                })

        return unusual

    def detect_failed_operations(self) -> list:
        """Detect repeated failed operations"""

        # Get failed operations in last hour
        start_date = datetime.utcnow() - timedelta(hours=1)

        entries = self.audit_store.db.query('''
            SELECT user_id, action, COUNT(*) as failure_count
            FROM audit_log
            WHERE status = 'failure'
            AND timestamp >= %s
            GROUP BY user_id, action
            HAVING COUNT(*) > 3
        ''', (start_date,))

        return [
            {
                'user_id': e['user_id'],
                'action': e['action'],
                'failure_count': e['failure_count'],
                'severity': 'HIGH' if e['failure_count'] > 10 else 'MEDIUM',
                'action_needed': 'Investigate account lockout or malicious activity'
            }
            for e in entries
        ]

    def alert_on_policy_violations(self) -> list:
        """Alert on policy changes"""

        recent_policy_changes = self.audit_store.db.query('''
            SELECT * FROM audit_log
            WHERE action = 'update_policy'
            AND timestamp >= NOW() - INTERVAL '1 hour'
        ''')

        alerts = []
        for change in recent_policy_changes:
            alerts.append({
                'alert_id': str(uuid.uuid4()),
                'severity': 'CRITICAL',
                'message': f"Policy {change['resource_id']} changed by {change['user_id']}",
                'timestamp': change['timestamp'],
                'requires_review': True
            })

        return alerts
```

### Audit Report Generation

```python
class AuditReportGenerator:
    """Generate audit reports for compliance"""

    def __init__(self, audit_store: ImmutableAuditStore):
        self.audit_store = audit_store

    def generate_daily_summary(self, report_date: datetime) -> dict:
        """Generate daily audit summary"""

        start = datetime.combine(report_date, datetime.min.time())
        end = datetime.combine(report_date, datetime.max.time())

        entries = self.audit_store.db.query('''
            SELECT action, status, COUNT(*) as count
            FROM audit_log
            WHERE timestamp BETWEEN %s AND %s
            GROUP BY action, status
        ''', (start, end))

        summary = {
            'report_date': report_date.isoformat(),
            'total_entries': 0,
            'successful': 0,
            'failed': 0,
            'by_action': {}
        }

        for entry in entries:
            summary['total_entries'] += entry['count']

            if entry['status'] == 'success':
                summary['successful'] += entry['count']
            else:
                summary['failed'] += entry['count']

            if entry['action'] not in summary['by_action']:
                summary['by_action'][entry['action']] = 0

            summary['by_action'][entry['action']] += entry['count']

        return summary

    def generate_compliance_report(self, start_date: datetime,
                                   end_date: datetime) -> str:
        """Generate formal compliance report"""

        report = f"""
AUDIT COMPLIANCE REPORT
=======================
Period: {start_date.date()} to {end_date.date()}
Generated: {datetime.utcnow().isoformat()}

EXECUTIVE SUMMARY
-----------------
"""

        # Get summary stats
        entries = self.audit_store.db.query('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT resource_type) as resource_types
            FROM audit_log
            WHERE timestamp BETWEEN %s AND %s
        ''', (start_date, end_date))

        if entries:
            e = entries[0]
            report += f"""
Total Audit Entries: {e['total']}
Successful Operations: {e['successful']}
Unique Users: {e['unique_users']}
Resource Types: {e['resource_types']}

COMPLIANCE STATUS: PASS ✓

RECOMMENDATIONS
----------------
- Continue monitoring for unusual access patterns
- Review high-risk operations monthly
- Archive logs beyond retention period
"""

        return report
```

## Conclusion

Audit logging patterns provide:

1. **Immutable records** that cannot be tampered with
2. **Chain integrity** verification using cryptographic hashing
3. **Data masking** to protect sensitive information
4. **Regulatory compliance** for PCI-DSS, GDPR, SOX, HIPAA
5. **Monitoring and alerting** for policy violations
6. **Comprehensive reporting** for audits and exams

Key principles:

- **Write-Once**: Audit logs cannot be modified or deleted
- **Comprehensive**: Every action that affects financial data is logged
- **Verifiable**: Logs can be cryptographically verified for tampering
- **Accessible**: Authorized parties can query and export logs
- **Retained**: Logs are kept per regulatory requirements (typically 7 years for financial data)
