# Data Subject Rights Automation Guide

## Executive Summary

This guide covers automated systems for fulfilling data subject rights under GDPR and similar privacy regulations. It addresses the technical and legal requirements for automating access, deletion, rectification, and portability requests.

## Table of Contents

1. [Introduction](#introduction)
2. [Data Subject Rights Overview](#data-subject-rights-overview)
3. [Rights Management System Architecture](#rights-management-system-architecture)
4. [Request Processing Workflows](#request-processing-workflows)
5. [Verification and Authentication](#verification-and-authentication)
6. [Code Implementation](#code-implementation)
7. [Audit Trails and Evidence](#audit-trails-and-evidence)
8. [Deadline Management](#deadline-management)

## Introduction

Data subject rights automation ensures:

- Consistent, timely fulfillment of requests
- Compliance with legal deadlines (typically 30 days)
- Comprehensive audit trails
- Proper verification of requesters
- Documentation for regulatory inspection

## Data Subject Rights Overview

### Right to Access (Article 15)

Data subjects can request:
- Confirmation of whether their data is processed
- Purposes of processing
- Categories of data
- Recipients of data
- Retention period or criteria for deletion
- Data subject's rights
- Right to lodge complaint

**Timeline**: 30 days from request (extendable by 2 months for complex requests)

### Right to Rectification (Article 16)

Data subjects can request correction of:
- Inaccurate data
- Incomplete data

**Timeline**: Without undue delay, preferably within 30 days

### Right to Erasure "Right to Be Forgotten" (Article 17)

Data subjects can request deletion when:
- Data no longer necessary
- Consent withdrawn
- Object to processing
- Data processed unlawfully
- Legal obligation to erase

**Exceptions** (data must be retained):
- Legal obligations
- Public interest archiving
- Exercising freedom of expression
- Detecting, investigating crimes
- Public health in public interest
- Vital interests

**Timeline**: Without undue delay, typically within 30 days

### Right to Restrict Processing (Article 18)

Data subjects can request:
- Temporary limitation of processing
- Preservation of data without active use
- Pending verification of accuracy

**Timeline**: Without undue delay

### Right to Data Portability (Article 20)

Data subjects can request:
- Personal data in structured format
- Machine-readable, widely-used format (CSV, JSON, XML)
- Direct transmission to another controller if feasible

**Timeline**: Within 30 days

### Right to Object (Article 21)

Data subjects can object to:
- Legitimate interests processing
- Direct marketing
- Automated profiling

**Timeline**: Respond without undue delay

## Rights Management System Architecture

### 1. Request Intake and Validation

```python
import uuid
import hashlib
from datetime import datetime, timedelta
from enum import Enum

class RequestType(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICT = "restrict"
    PORTABILITY = "portability"
    OBJECT = "object"
    WITHDRAW_CONSENT = "withdraw_consent"

class DSRRequestValidator:
    """
    Validate and intake data subject rights requests.
    """

    def __init__(self, database, identity_service):
        self.db = database
        self.identity_service = identity_service
        self.valid_request_types = [rt.value for rt in RequestType]

    def intake_request(self, request_data, source='web_portal'):
        """
        Process incoming data subject rights request.
        """
        # Validate request format
        validation = self._validate_format(request_data)
        if not validation['valid']:
            return {
                'status': 'rejected',
                'errors': validation['errors'],
                'timestamp': datetime.now().isoformat()
            }

        # Create request record
        request_id = str(uuid.uuid4())
        request_record = {
            'id': request_id,
            'created_at': datetime.now(),
            'source': source,
            'type': request_data.get('request_type'),
            'data_subject_identifier': request_data.get('email') or request_data.get('user_id'),
            'request_details': request_data,
            'status': 'intake_received',
            'deadline': self._calculate_deadline(request_data.get('request_type')),
            'verification_status': 'pending'
        }

        # Store request
        self.db.store_dsr_request(request_record)

        # Initiate verification
        verification_task = self._initiate_verification(request_record)

        return {
            'status': 'received',
            'request_id': request_id,
            'deadline': request_record['deadline'].isoformat(),
            'next_step': 'verification',
            'verification_method': verification_task['method']
        }

    def _validate_format(self, request_data):
        """Validate request contains required information."""
        errors = []

        if 'request_type' not in request_data:
            errors.append('Missing request type')
        elif request_data['request_type'] not in self.valid_request_types:
            errors.append(f"Invalid request type: {request_data['request_type']}")

        # Verify requestor identification
        if not request_data.get('email') and not request_data.get('user_id'):
            errors.append('No identification method provided (email or user_id required)')

        # For rectification, need to specify what to correct
        if request_data.get('request_type') == 'rectification':
            if not request_data.get('corrections'):
                errors.append('Rectification request must specify corrections')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _calculate_deadline(self, request_type):
        """Calculate response deadline based on request type."""
        if request_type in ['access', 'erasure', 'portability']:
            base_deadline = 30
        else:
            base_deadline = 30

        deadline = datetime.now() + timedelta(days=base_deadline)
        return deadline

    def _initiate_verification(self, request_record):
        """Start identity verification process."""
        email = request_record['data_subject_identifier']
        
        verification_token = hashlib.sha256(
            (request_record['id'] + str(datetime.now())).encode()
        ).hexdigest()[:32]

        verification = {
            'request_id': request_record['id'],
            'method': 'email_verification',
            'token': verification_token,
            'email': email,
            'expires_at': datetime.now() + timedelta(hours=24),
            'verification_link': f"https://compliance.example.com/verify/{verification_token}"
        }

        self.db.store_verification(verification)

        # Send verification email
        self._send_verification_email(email, verification['verification_link'])

        return verification

    def verify_request(self, verification_token):
        """Verify data subject identity via token."""
        verification = self.db.get_verification_by_token(verification_token)

        if not verification:
            return {'status': 'invalid_token'}

        if datetime.now() > verification['expires_at']:
            return {'status': 'token_expired'}

        # Update request status
        request = self.db.get_dsr_request(verification['request_id'])
        request['verification_status'] = 'verified'
        request['verified_at'] = datetime.now()

        self.db.update_dsr_request(request)

        # Mark verification as used
        self.db.mark_verification_used(verification_token)

        return {
            'status': 'verified',
            'request_id': verification['request_id'],
            'next_step': 'processing'
        }
```

### 2. Access Request Processing

```python
class AccessRequestProcessor:
    """
    Handle right to access requests and generate data exports.
    """

    def __init__(self, database, storage_service, encryption_service):
        self.db = database
        self.storage = storage_service
        self.encryption = encryption_service

    def process_access_request(self, request_id):
        """
        Process access request and prepare data export.
        """
        request = self.db.get_dsr_request(request_id)
        data_subject_id = self._identify_data_subject(request)

        # Retrieve all personal data
        all_data = self._retrieve_all_data(data_subject_id)

        # Organize by category
        organized_data = self._organize_by_category(all_data)

        # Generate export
        export = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'created_at': datetime.now(),
            'data_subject_id': data_subject_id,
            'data_categories': list(organized_data.keys()),
            'total_records': sum(len(v) for v in organized_data.values()),
            'contents': organized_data
        }

        # Create secure export file
        export_file = self._create_secure_export(export)

        # Generate secure download link
        download_link = self._generate_secure_link(export_file)

        # Store export record
        self.db.store_access_export(export)

        # Update request status
        request['status'] = 'export_ready'
        request['export_id'] = export['id']
        request['download_expires_at'] = datetime.now() + timedelta(days=7)
        self.db.update_dsr_request(request)

        return {
            'status': 'export_ready',
            'download_link': download_link,
            'expires_at': request['download_expires_at'].isoformat(),
            'data_categories': export['data_categories'],
            'record_count': export['total_records']
        }

    def _retrieve_all_data(self, data_subject_id):
        """Retrieve all personal data for subject from all systems."""
        data = {}

        # Main database
        data['user_profile'] = self.db.get_user_profile(data_subject_id)
        data['contact_information'] = self.db.get_contact_data(data_subject_id)
        data['transaction_history'] = self.db.get_transaction_data(data_subject_id)
        data['activity_logs'] = self.db.get_activity_logs(data_subject_id)
        data['preferences'] = self.db.get_user_preferences(data_subject_id)

        # Communication history
        data['emails'] = self.db.get_email_communications(data_subject_id)
        data['messages'] = self.db.get_messages(data_subject_id)

        # Third-party data
        data['third_party_processing'] = self.db.get_third_party_data(data_subject_id)

        # Marketing data
        data['marketing_preferences'] = self.db.get_marketing_data(data_subject_id)

        return data

    def _organize_by_category(self, data):
        """Organize data by category for clarity."""
        categories = {
            'Personal Identifiers': data.get('user_profile', {}),
            'Contact Information': data.get('contact_information', {}),
            'Transaction History': data.get('transaction_history', []),
            'Activity and Usage': data.get('activity_logs', []),
            'Preferences and Settings': data.get('preferences', {}),
            'Communications': {
                'emails': data.get('emails', []),
                'messages': data.get('messages', [])
            },
            'Third-Party Data': data.get('third_party_processing', []),
            'Marketing': data.get('marketing_preferences', {})
        }

        return {k: v for k, v in categories.items() if v}

    def _create_secure_export(self, export):
        """Create encrypted export file."""
        # Convert to JSON
        import json
        export_json = json.dumps(export['contents'], default=str, indent=2)

        # Encrypt
        encrypted_content = self.encryption.encrypt(export_json)

        # Store securely
        file_path = self.storage.save_secure(
            encrypted_content,
            f"dsr_export_{export['id']}.enc"
        )

        return file_path

    def _generate_secure_link(self, file_path, expires_in_days=7):
        """Generate secure temporary download link."""
        return self.storage.generate_temporary_download_link(
            file_path,
            expires_in_days=expires_in_days
        )
```

### 3. Deletion Request Processing

```python
class DeletionRequestProcessor:
    """
    Handle right to erasure (deletion) requests.
    """

    def __init__(self, database, retention_manager):
        self.db = database
        self.retention_manager = retention_manager

    def process_deletion_request(self, request_id):
        """
        Process deletion request with retention checking.
        """
        request = self.db.get_dsr_request(request_id)
        data_subject_id = self._identify_data_subject(request)

        # Check retention justifications
        retention_check = self.retention_manager.check_retention_justifications(
            data_subject_id
        )

        if retention_check['must_retain']:
            # Return conflict for manual review
            request['status'] = 'pending_manual_review'
            request['retention_conflicts'] = retention_check['conflicts']
            self.db.update_dsr_request(request)

            return {
                'status': 'pending_review',
                'reason': 'Data must be retained for legal reasons',
                'conflicts': retention_check['conflicts']
            }

        # Proceed with deletion
        deletion_job = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'data_subject_id': data_subject_id,
            'started_at': datetime.now(),
            'status': 'in_progress',
            'deletion_systems': {}
        }

        # Delete from all systems
        systems = [
            'primary_database',
            'backup_storage',
            'cache',
            'analytics_platform',
            'cdn',
            'email_archive',
            'logging_system'
        ]

        for system in systems:
            try:
                result = self._delete_from_system(system, data_subject_id)
                deletion_job['deletion_systems'][system] = {
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'records_deleted': result.get('count', 0)
                }
            except Exception as e:
                deletion_job['deletion_systems'][system] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

        deletion_job['completed_at'] = datetime.now()
        deletion_job['status'] = 'completed'

        # Store deletion record
        self.db.store_deletion_job(deletion_job)

        # Update request
        request['status'] = 'completed'
        request['completion_timestamp'] = datetime.now()
        self.db.update_dsr_request(request)

        return {
            'status': 'completed',
            'deletion_job_id': deletion_job['id'],
            'systems_processed': len(systems),
            'completion_timestamp': deletion_job['completed_at'].isoformat()
        }

    def _delete_from_system(self, system, data_subject_id):
        """Delete from specific system."""
        if system == 'primary_database':
            return self.db.delete_user_records(data_subject_id)
        elif system == 'backup_storage':
            return self._delete_from_backups(data_subject_id)
        elif system == 'cache':
            return self._delete_from_cache(data_subject_id)
        elif system == 'analytics_platform':
            return self._delete_from_analytics(data_subject_id)
        # ... other systems

        return {'count': 0}

    def _delete_from_backups(self, data_subject_id):
        """Remove from backup systems."""
        # Mark for deletion in next backup cycle
        self.db.mark_for_backup_deletion(data_subject_id)
        return {'count': self.db.count_backup_records(data_subject_id)}
```

### 4. Rectification Request Processing

```python
class RectificationRequestProcessor:
    """
    Handle right to rectification (correction) requests.
    """

    def __init__(self, database):
        self.db = database

    def process_rectification_request(self, request_id):
        """
        Process request to correct inaccurate data.
        """
        request = self.db.get_dsr_request(request_id)
        data_subject_id = self._identify_data_subject(request)
        corrections = request['request_details'].get('corrections', {})

        update_log = {
            'request_id': request_id,
            'data_subject_id': data_subject_id,
            'started_at': datetime.now(),
            'corrections': {}
        }

        for field, new_value in corrections.items():
            # Verify correction is legitimate
            verification = self._verify_correction(
                data_subject_id, field, new_value
            )

            if not verification['valid']:
                update_log['corrections'][field] = {
                    'status': 'pending_verification',
                    'reason': verification['reason']
                }
                continue

            # Get original value for audit trail
            original_value = self.db.get_field_value(data_subject_id, field)

            # Update in all relevant systems
            update_result = self._update_field_everywhere(
                data_subject_id, field, original_value, new_value
            )

            update_log['corrections'][field] = {
                'status': 'updated',
                'original_value': original_value,
                'new_value': new_value,
                'timestamp': datetime.now().isoformat(),
                'systems_updated': update_result['systems']
            }

        # Store update log
        self.db.store_rectification_log(update_log)

        # Update request status
        request['status'] = 'completed'
        request['completion_timestamp'] = datetime.now()
        self.db.update_dsr_request(request)

        return {
            'status': 'completed',
            'corrections_applied': len([
                c for c in update_log['corrections'].values()
                if c['status'] == 'updated'
            ]),
            'pending_verification': len([
                c for c in update_log['corrections'].values()
                if c['status'] == 'pending_verification'
            ])
        }

    def _verify_correction(self, data_subject_id, field, new_value):
        """Verify correction is legitimate."""
        # Prevent modification of audit fields
        protected_fields = ['created_at', 'user_id', 'account_id']
        if field in protected_fields:
            return {
                'valid': False,
                'reason': f'Field {field} cannot be modified'
            }

        # Validate field type matches
        expected_type = self.db.get_field_type(field)
        if not self._validate_type(new_value, expected_type):
            return {
                'valid': False,
                'reason': f'Invalid type for {field}'
            }

        return {'valid': True}

    def _update_field_everywhere(self, data_subject_id, field, old_value, new_value):
        """Update field in all systems containing it."""
        systems_updated = []

        # Primary database
        self.db.update_field(data_subject_id, field, new_value)
        systems_updated.append('primary_database')

        # Cache invalidation
        self._invalidate_cache(data_subject_id, field)
        systems_updated.append('cache')

        # Search indexes if applicable
        if self._is_indexed_field(field):
            self._update_search_index(data_subject_id, field, new_value)
            systems_updated.append('search_index')

        return {'systems': systems_updated}
```

## Request Processing Workflows

### Access Request Workflow

```
1. Request Received
   ↓
2. Format Validation
   ↓
3. Identity Verification (Email/SMS token)
   ↓
4. Retrieve All Personal Data
   - Primary database
   - Archives
   - Third-party systems
   - Backups
   ↓
5. Organize by Category
   ↓
6. Encrypt and Secure
   ↓
7. Generate Secure Download Link
   ↓
8. Notify Data Subject
   ↓
9. Track Download
   ↓
10. Delete Export (after 7 days)
```

### Deletion Request Workflow

```
1. Request Received
   ↓
2. Identity Verification
   ↓
3. Check Retention Justifications
   ├─ If conflicts exist → Manual review
   └─ If none → Proceed
   ↓
4. Delete from All Systems
   - Primary storage
   - Backups
   - Cache
   - Analytics
   - Third-party systems
   ↓
5. Log All Deletions
   ↓
6. Verification of Deletion
   ↓
7. Notify Data Subject
```

## Verification and Authentication

### Multi-Factor Verification

```python
class MultiFactorVerification:
    """
    Implement multi-factor verification for data subject identity.
    """

    def __init__(self, email_service, sms_service):
        self.email = email_service
        self.sms = sms_service

    def initiate_verification(self, data_subject_identifier, verification_methods):
        """
        Initiate multi-factor verification process.
        """
        verification_session = {
            'id': str(uuid.uuid4()),
            'identifier': data_subject_identifier,
            'methods': [],
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=24),
            'verification_status': 'in_progress'
        }

        for method in verification_methods:
            if method == 'email':
                token = self._generate_token()
                self.email.send_verification(data_subject_identifier, token)
                verification_session['methods'].append({
                    'type': 'email',
                    'status': 'sent'
                })

            elif method == 'sms':
                token = self._generate_otp()
                self.sms.send_verification(data_subject_identifier, token)
                verification_session['methods'].append({
                    'type': 'sms',
                    'status': 'sent'
                })

        return verification_session

    def verify_code(self, session_id, method_type, code):
        """Verify code from specific method."""
        session = self._get_verification_session(session_id)

        # Verify code
        if self._validate_code(method_type, code):
            method = next(
                (m for m in session['methods'] if m['type'] == method_type),
                None
            )
            if method:
                method['status'] = 'verified'

        # Check if all required methods verified
        if self._all_methods_verified(session):
            session['verification_status'] = 'complete'

        return {
            'status': session['verification_status'],
            'verified_methods': [m['type'] for m in session['methods'] if m['status'] == 'verified']
        }
```

## Audit Trails and Evidence

### Complete Audit Logging

```python
class DSRAuditTrail:
    """
    Maintain comprehensive audit trails for all DSR activities.
    """

    def __init__(self, database):
        self.db = database

    def log_event(self, request_id, event_type, details, actor=None):
        """
        Log DSR activity event.
        """
        audit_entry = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'event_type': event_type,
            'timestamp': datetime.now(),
            'details': details,
            'actor': actor or 'system',
            'ip_address': self._get_request_ip(),
            'user_agent': self._get_user_agent()
        }

        self.db.store_audit_entry(audit_entry)

        return audit_entry

    def get_audit_trail(self, request_id):
        """Retrieve complete audit trail for request."""
        entries = self.db.get_audit_entries(request_id)

        return {
            'request_id': request_id,
            'total_events': len(entries),
            'events': sorted(entries, key=lambda x: x['timestamp']),
            'generated_at': datetime.now().isoformat()
        }
```

## Deadline Management

### Deadline Tracking and Alerts

```python
class DeadlineManager:
    """
    Manage DSR response deadlines and generate alerts.
    """

    def __init__(self, database, notification_service):
        self.db = database
        self.notify = notification_service

    def check_approaching_deadlines(self):
        """Check for requests approaching deadline."""
        pending_requests = self.db.get_pending_dsr_requests()
        alerts = []

        for request in pending_requests:
            days_remaining = (request['deadline'] - datetime.now()).days

            if days_remaining == 7:
                alerts.append({
                    'request_id': request['id'],
                    'severity': 'medium',
                    'message': f'Request {request['id']} due in 7 days'
                })
            elif days_remaining == 1:
                alerts.append({
                    'request_id': request['id'],
                    'severity': 'high',
                    'message': f'Request {request['id']} due tomorrow'
                })
            elif days_remaining < 0:
                alerts.append({
                    'request_id': request['id'],
                    'severity': 'critical',
                    'message': f'Request {request['id']} OVERDUE'
                })

            for alert in alerts:
                self.notify.send_alert(alert)

        return alerts
```

## Conclusion

Automated data subject rights systems ensure:

- Timely, consistent fulfillment of requests
- Proper identity verification
- Comprehensive audit documentation
- Deadline compliance
- Demonstrable adherence to GDPR requirements

Regular monitoring and testing of these systems maintains compliance and builds data subject trust.
