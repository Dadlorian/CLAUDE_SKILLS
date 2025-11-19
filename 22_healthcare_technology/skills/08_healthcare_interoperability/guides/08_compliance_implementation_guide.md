# Compliance Implementation Guide

## Step 1: HIPAA Compliance Checklist

### Technical Safeguards

#### Access Control
```python
class HIPAAAccessControl:
    def __init__(self, db):
        self.db = db

    def check_access(self, user_id, resource_id, action):
        """Implement minimum necessary principle"""
        # Get user role
        user = self.db.get_user(user_id)

        # Check permissions
        if not self.has_permission(user['role'], resource_id, action):
            raise PermissionError(f"User {user_id} cannot {action} resource {resource_id}")

        # Log access
        self.log_access_event(user_id, resource_id, action)

        return True

    def has_permission(self, role, resource_id, action):
        """Check if role has permission"""
        permissions = {
            'clinician': ['read', 'write'],
            'admin': ['read', 'write', 'delete'],
            'patient': ['read']
        }

        return action in permissions.get(role, [])

    def log_access_event(self, user_id, resource_id, action):
        """Log for audit trail"""
        event = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'resource_id': resource_id,
            'action': action,
            'ip_address': self.get_client_ip(),
            'success': True
        }

        self.db.log_audit_event(event)

    def get_client_ip(self):
        """Get client IP address"""
        # Implementation depends on framework
        pass
```

#### Authentication
```python
import hashlib
import secrets

class HIPAAAuthentication:
    def __init__(self, db):
        self.db = db
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes

    def authenticate_user(self, username, password):
        """Authenticate with password"""
        user = self.db.get_user_by_username(username)

        if not user:
            raise ValueError("Invalid credentials")

        # Check lockout
        if self.is_locked(username):
            raise ValueError("Account locked")

        # Verify password
        if not self.verify_password(password, user['password_hash']):
            self.log_failed_attempt(username)
            raise ValueError("Invalid credentials")

        # Clear failed attempts
        self.db.clear_failed_attempts(username)

        return user

    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"

    def verify_password(self, password, hash_value):
        """Verify password against hash"""
        try:
            salt, hash_hex = hash_value.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except:
            return False

    def is_locked(self, username):
        """Check if account is locked"""
        failed_attempts = self.db.get_failed_attempts(username)
        if failed_attempts >= self.max_attempts:
            lockout_time = self.db.get_lockout_time(username)
            if datetime.utcnow() < lockout_time:
                return True
        return False

    def log_failed_attempt(self, username):
        """Log failed login attempt"""
        self.db.increment_failed_attempts(username)

        failed_count = self.db.get_failed_attempts(username)
        if failed_count >= self.max_attempts:
            lockout_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
            self.db.set_lockout(username, lockout_until)
            self.send_alert(f"Account {username} locked due to multiple failed attempts")
```

#### Encryption
```python
from cryptography.fernet import Fernet
import ssl

class HIPAAEncryption:
    def __init__(self):
        self.cipher_suite = Fernet(self.get_key())

    def encrypt_data(self, plaintext):
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(plaintext.encode())

    def decrypt_data(self, ciphertext):
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(ciphertext).decode()

    def get_key(self):
        """Get encryption key from secure storage"""
        # Should be stored in key management service (KMS)
        # Not in code
        pass

    def setup_tls_context(self):
        """Configure TLS 1.2+ context"""
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        # Use strong cipher suites
        context.set_ciphers(':'.join([
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-ECDSA-AES128-GCM-SHA256'
        ]))

        return context

    def encrypt_at_rest(self, data, db_column):
        """Encrypt data before storage"""
        encrypted = self.encrypt_data(data)
        return encrypted

    def decrypt_from_storage(self, encrypted_data):
        """Decrypt data from database"""
        return self.decrypt_data(encrypted_data)
```

## Step 2: Audit Logging

### Comprehensive Audit Trail
```python
from datetime import datetime

class AuditLog:
    def __init__(self, db):
        self.db = db

    def log_event(self, event_type, details):
        """Log audit event"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': details.get('user_id'),
            'resource_type': details.get('resource_type'),
            'resource_id': details.get('resource_id'),
            'action': details.get('action'),
            'ip_address': details.get('ip_address'),
            'outcome': details.get('outcome'),  # success/failure
            'details': details.get('details')
        }

        # Store in tamper-proof log
        self.db.insert_audit_log(audit_entry)

    def log_access(self, user_id, resource_id, action, success):
        """Log resource access"""
        self.log_event('RESOURCE_ACCESS', {
            'user_id': user_id,
            'resource_id': resource_id,
            'action': action,
            'outcome': 'success' if success else 'failure'
        })

    def log_data_modification(self, user_id, resource_id, before, after):
        """Log data changes"""
        self.log_event('DATA_MODIFICATION', {
            'user_id': user_id,
            'resource_id': resource_id,
            'action': 'update',
            'details': {
                'before': before,
                'after': after
            }
        })

    def log_security_event(self, event_type, details):
        """Log security events"""
        self.log_event('SECURITY_EVENT', {
            'event_type': event_type,
            'details': details
        })

    def get_audit_history(self, resource_id, days=90):
        """Retrieve audit history"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query_audit_logs({
            'resource_id': resource_id,
            'timestamp': {'$gte': cutoff_date}
        })

    def archive_logs(self):
        """Archive old audit logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        old_logs = self.db.query_audit_logs({'timestamp': {'$lt': cutoff_date}})

        # Archive (encrypt and store)
        for log in old_logs:
            self.archive_to_secure_storage(log)

        # Delete from active logs
        self.db.delete_audit_logs({'timestamp': {'$lt': cutoff_date}})
```

## Step 3: Breach Notification

### Breach Response Plan
```python
class BreachResponseManager:
    def __init__(self, db, email_service):
        self.db = db
        self.email = email_service
        self.breach_log = []

    def detect_breach(self, breach_details):
        """Detect and respond to breach"""
        # Validate breach
        is_breach = self.assess_breach(breach_details)

        if is_breach:
            self.handle_breach(breach_details)

    def assess_breach(self, details):
        """Determine if breach occurred"""
        # Check if PHI was compromised
        if details.get('data_type') in ['PHI', 'patient_record', 'payment_info']:
            # Check if unauthorized access
            if details.get('unauthorized_access'):
                return True

        return False

    def handle_breach(self, details):
        """Execute breach response plan"""
        # 1. Contain and stop further access
        self.contain_breach(details)

        # 2. Assess scope of breach
        scope = self.assess_scope(details)

        # 3. Determine who was affected
        affected_individuals = self.identify_affected(scope)

        # 4. Notify affected individuals (60 days)
        self.notify_individuals(affected_individuals, scope)

        # 5. Notify media (if >500 individuals)
        if len(affected_individuals) >= 500:
            self.notify_media()

        # 6. Notify HHS
        self.notify_hhs(affected_individuals, scope)

        # 7. Document and retain records
        self.document_breach(details, scope, affected_individuals)

    def contain_breach(self, details):
        """Stop further unauthorized access"""
        affected_system = details['system']
        self.disable_affected_accounts(affected_system)
        self.reset_affected_credentials(affected_system)
        self.patch_vulnerability(affected_system)

    def assess_scope(self, details):
        """Determine extent of breach"""
        return {
            'date_discovered': datetime.utcnow(),
            'date_of_breach': details.get('breach_date'),
            'systems_affected': details.get('systems'),
            'data_types_exposed': details.get('data_types'),
            'individuals_affected': self.count_affected_individuals(details)
        }

    def identify_affected(self, scope):
        """Find affected individuals"""
        affected = []
        for system in scope['systems_affected']:
            records = self.db.get_exposed_records(system, scope['data_types_exposed'])
            affected.extend([r['individual_id'] for r in records])

        return list(set(affected))

    def notify_individuals(self, individuals, scope):
        """Send notifications to affected individuals"""
        for individual_id in individuals:
            contact = self.db.get_contact_info(individual_id)

            notification = {
                'type': 'breach_notification',
                'date': scope['date_of_breach'],
                'description': 'Your health information may have been accessed',
                'steps_taken': 'We have taken steps to secure your information',
                'contact': 'Call 1-800-XXX-XXXX for more information'
            }

            # Send via multiple channels
            self.email.send(contact['email'], notification)
            self.sms.send(contact['phone'], notification)
            self.mail.send(contact['address'], notification)

    def notify_hhs(self, individuals, scope):
        """Notify US Department of Health and Human Services"""
        # Format according to HHS requirements
        notification = {
            'entity_name': 'Healthcare System Name',
            'date_breach_discovered': scope['date_discovered'].isoformat(),
            'date_of_breach': scope['date_of_breach'].isoformat(),
            'number_individuals': len(individuals),
            'description': 'Unauthorized access to EHR system',
            'actions_taken': 'System secured, individuals notified'
        }

        # Submit to HHS portal
        self.submit_to_hhs(notification)

    def document_breach(self, details, scope, affected):
        """Document for compliance records"""
        record = {
            'timestamp': datetime.utcnow(),
            'details': details,
            'scope': scope,
            'individuals_affected': len(affected),
            'notification_status': 'completed',
            'remediation_steps': self.get_remediation_steps()
        }

        self.db.store_breach_record(record)
```

## Step 4: Security Risk Assessment

```python
class SecurityRiskAssessment:
    def perform_assessment(self):
        """Conduct HIPAA security risk assessment"""
        assessment = {
            'date': datetime.utcnow(),
            'findings': []
        }

        # Access controls
        assessment['findings'].extend(self.assess_access_controls())

        # Audit logging
        assessment['findings'].extend(self.assess_audit_logging())

        # Encryption
        assessment['findings'].extend(self.assess_encryption())

        # Workforce security
        assessment['findings'].extend(self.assess_workforce_security())

        # Incident procedures
        assessment['findings'].extend(self.assess_incident_procedures())

        return assessment

    def assess_access_controls(self):
        """Evaluate access control mechanisms"""
        findings = []

        # Check password policies
        if not self.check_password_policy():
            findings.append({
                'severity': 'high',
                'finding': 'Weak password policy',
                'recommendation': 'Implement strong password requirements'
            })

        # Check MFA
        if not self.check_mfa_enabled():
            findings.append({
                'severity': 'critical',
                'finding': 'Multi-factor authentication not enabled',
                'recommendation': 'Enable MFA for all administrative accounts'
            })

        return findings

    def assess_audit_logging(self):
        """Evaluate audit logging"""
        findings = []

        if not self.check_audit_logging_enabled():
            findings.append({
                'severity': 'critical',
                'finding': 'Audit logging disabled',
                'recommendation': 'Enable and configure audit logging'
            })

        if not self.check_log_retention():
            findings.append({
                'severity': 'high',
                'finding': 'Logs not retained for 6+ years',
                'recommendation': 'Implement log archival and retention'
            })

        return findings
```

## Step 5: Compliance Documentation

### Document Template
```markdown
# HIPAA Compliance Plan

## Administrative Safeguards
- [ ] Access management
- [ ] Security awareness and training
- [ ] Security incident procedures
- [ ] Contingency planning

## Physical Safeguards
- [ ] Facility access controls
- [ ] Workstation use policies
- [ ] Workstation security
- [ ] Device and media controls

## Technical Safeguards
- [ ] Access controls
- [ ] Audit controls
- [ ] Integrity controls
- [ ] Transmission security

## Evidence
- Security policies and procedures
- Training records
- Risk assessments
- Audit logs
- Incident documentation
```

## Next Steps

1. Conduct security risk assessment
2. Implement access controls
3. Enable audit logging
4. Configure encryption
5. Develop breach response plan
6. Train workforce
7. Document compliance efforts
