# Consent Management Automation Guide

## Executive Summary

This guide covers automated systems for collecting, managing, and revoking consent in compliance with GDPR, CCPA, and other privacy regulations. It addresses consent collection mechanisms, audit trails, revocation workflows, and proof of consent documentation.

## Table of Contents

1. [Introduction](#introduction)
2. [Consent Requirements](#consent-requirements)
3. [Consent Collection Architecture](#consent-collection-architecture)
4. [Consent Types and Categories](#consent-types-and-categories)
5. [Implementation Code](#implementation-code)
6. [Consent Withdrawal and Revocation](#consent-withdrawal-and-revocation)
7. [Proof of Consent](#proof-of-consent)
8. [Monitoring and Compliance](#monitoring-and-compliance)

## Introduction

Valid consent under GDPR requires:

- **Freely given**: No coercion or pressure
- **Specific**: Clear what is being consented to
- **Informed**: Understanding consequences
- **Unambiguous**: Clear affirmative action
- **Granular**: Separate consent for each purpose

Automated consent management ensures:

- Compliance with strict consent requirements
- Comprehensive audit trails
- Revocation tracking
- Proof of valid consent

## Consent Requirements

### GDPR Consent Rules

1. **Pre-checked boxes are invalid** - Must be explicit opt-in
2. **Consent conditions must be separated** - Each purpose needs separate consent
3. **Consent must be freely given** - No bundling with service terms
4. **Easy revocation** - As easy to withdraw as to give
5. **Withdrawal effective immediately** - Processing must stop
6. **Documented** - Keep proof of consent and when given
7. **Specific** - Cannot be generic or vague

### Valid vs. Invalid Consent Examples

**Invalid:**
- Pre-checked boxes
- Silence or inactivity
- Mandatory for service (unless necessary)
- Vague descriptions
- Processing without requesting

**Valid:**
- Explicit opt-in button
- Specific explanation of purposes
- Easy withdrawal option
- Clear privacy policy
- Separate consents per purpose

## Consent Collection Architecture

### 1. Consent Collection Interface

```python
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
from typing import Dict, List, Optional

class ConsentCategory(Enum):
    """Standard consent categories."""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PROFILING = "profiling"
    THIRD_PARTY_SHARING = "third_party_sharing"
    PREFERENCE_DATA = "preference_data"
    ESSENTIAL = "essential"
    PERSONALIZATION = "personalization"

class ConsentCollector:
    """
    Automated consent collection with GDPR compliance.
    """

    def __init__(self, database, notification_service):
        self.db = database
        self.notify = notification_service
        self.valid_categories = [c.value for c in ConsentCategory]

    def initiate_consent_request(self, data_subject_id, consent_categories, context):
        """
        Initiate consent collection request.
        
        Args:
            data_subject_id: Unique identifier for data subject
            consent_categories: List of categories requiring consent
            context: Request context (channel, purpose, etc.)
        """
        # Validate categories
        for category in consent_categories:
            if category not in self.valid_categories:
                raise ValueError(f"Invalid consent category: {category}")

        # Create consent request
        consent_request = {
            'id': str(uuid.uuid4()),
            'data_subject_id': data_subject_id,
            'consent_categories': consent_categories,
            'request_details': self._prepare_request_details(consent_categories),
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=90),
            'status': 'pending',
            'channel': context.get('channel', 'web'),
            'ip_address': context.get('ip_address'),
            'user_agent': context.get('user_agent'),
            'request_url': context.get('request_url')
        }

        # Store request
        self.db.store_consent_request(consent_request)

        # Send consent request
        self._send_consent_interface(data_subject_id, consent_request, context)

        return {
            'request_id': consent_request['id'],
            'status': 'sent',
            'expiry': consent_request['expires_at'].isoformat()
        }

    def _prepare_request_details(self, consent_categories):
        """Prepare detailed descriptions for each consent type."""
        descriptions = {
            ConsentCategory.MARKETING.value: {
                'title': 'Marketing Communications',
                'description': 'We would like to send you emails and notifications about products, services, and offers.',
                'examples': ['Product recommendations', 'Promotional offers', 'Newsletter']
            },
            ConsentCategory.ANALYTICS.value: {
                'title': 'Analytics and Performance',
                'description': 'We use analytics to understand how you use our services and improve our offerings.',
                'examples': ['Page views', 'Feature usage', 'Performance metrics']
            },
            ConsentCategory.PROFILING.value: {
                'title': 'Profile Building',
                'description': 'We build profiles of your interests and preferences for personalized experiences.',
                'examples': ['Interest categories', 'Preference tracking', 'Behavior analysis']
            },
            ConsentCategory.THIRD_PARTY_SHARING.value: {
                'title': 'Third-Party Data Sharing',
                'description': 'We may share your data with carefully selected partners.',
                'examples': ['Marketing partners', 'Analytics providers', 'Payment processors']
            },
            ConsentCategory.PREFERENCE_DATA.value: {
                'title': 'Preference Data Collection',
                'description': 'We track your preferences to provide better service.',
                'examples': ['Language preferences', 'Communication frequency', 'Content preferences']
            },
            ConsentCategory.PERSONALIZATION.value: {
                'title': 'Personalized Experience',
                'description': 'We personalize content and recommendations based on your behavior.',
                'examples': ['Recommended content', 'Personalized searches', 'Custom dashboards']
            }
        }

        return {
            cat: descriptions.get(cat, {})
            for cat in [ConsentCategory.ESSENTIAL.value] + [
                c for c in self.valid_categories if c != ConsentCategory.ESSENTIAL.value
            ]
        }

    def _send_consent_interface(self, data_subject_id, consent_request, context):
        """Send consent collection interface."""
        channel = context.get('channel', 'web')

        if channel == 'web':
            # Generate consent modal/banner
            consent_url = self._generate_consent_url(consent_request['id'])
            # Could embed in web interface or send link

        elif channel == 'email':
            # Send via email
            self.notify.send_consent_email(
                to_email=context.get('email'),
                consent_request=consent_request
            )

        elif channel == 'sms':
            # Send via SMS
            self.notify.send_consent_sms(
                phone_number=context.get('phone'),
                consent_request=consent_request
            )

    def _generate_consent_url(self, request_id):
        """Generate URL for consent interface."""
        return f"https://compliance.example.com/consent/{request_id}"
```

### 2. Consent Recording System

```python
class ConsentRecorder:
    """
    Record and validate explicit consent with comprehensive audit trail.
    """

    def __init__(self, database, audit_logger):
        self.db = database
        self.audit = audit_logger

    def record_consent(self, request_id, consent_responses):
        """
        Record explicit consent from data subject.
        
        Args:
            request_id: ID of consent request
            consent_responses: Dict mapping categories to True/False
        """
        # Retrieve original request
        consent_request = self.db.get_consent_request(request_id)

        if not consent_request:
            raise ValueError(f"Request not found: {request_id}")

        if consent_request['status'] != 'pending':
            raise ValueError(f"Request already processed: {request_id}")

        # Validate responses match requested categories
        for category in consent_request['consent_categories']:
            if category not in consent_responses:
                raise ValueError(f"Missing response for category: {category}")

        # Record timestamp and context
        consent_record = {
            'id': str(uuid.uuid4()),
            'request_id': request_id,
            'data_subject_id': consent_request['data_subject_id'],
            'recorded_at': datetime.now(),
            'consent_details': {}
        }

        # Process each consent response
        for category, given in consent_responses.items():
            consent_entry = {
                'category': category,
                'given': given,
                'timestamp': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
                'version': '1.0'
            }

            # Store individual consent
            self.db.store_individual_consent(
                consent_request['data_subject_id'],
                category,
                given,
                consent_entry
            )

            consent_record['consent_details'][category] = consent_entry

        # Update request status
        consent_request['status'] = 'recorded'
        consent_request['recorded_at'] = datetime.now()
        self.db.update_consent_request(consent_request)

        # Log consent recording
        self.audit.log_event(
            subject_id=consent_request['data_subject_id'],
            event_type='consent_recorded',
            details=consent_record
        )

        return consent_record

    def validate_consent(self, data_subject_id, category):
        """
        Check if valid consent exists for specific category.
        """
        consent = self.db.get_consent(data_subject_id, category)

        if not consent:
            return {
                'valid': False,
                'reason': 'No consent on file'
            }

        if not consent['given']:
            return {
                'valid': False,
                'reason': 'Consent explicitly withheld'
            }

        if datetime.fromisoformat(consent['expires_at']) < datetime.now():
            return {
                'valid': False,
                'reason': 'Consent expired'
            }

        # Check for revocations
        revocations = self.db.get_revocations(data_subject_id, category)
        if revocations and revocations[-1]['timestamp'] > consent['recorded_at']:
            return {
                'valid': False,
                'reason': 'Consent revoked'
            }

        return {
            'valid': True,
            'recorded_at': consent['recorded_at'],
            'expires_at': consent['expires_at']
        }
```

## Consent Types and Categories

### Essential vs. Discretionary Consent

```python
class ConsentTypeClassifier:
    """
    Classify consents as essential or discretionary.
    """

    ESSENTIAL_CATEGORIES = [
        ConsentCategory.ESSENTIAL.value
    ]

    DISCRETIONARY_CATEGORIES = [
        ConsentCategory.MARKETING.value,
        ConsentCategory.ANALYTICS.value,
        ConsentCategory.PROFILING.value,
        ConsentCategory.THIRD_PARTY_SHARING.value,
        ConsentCategory.PREFERENCE_DATA.value,
        ConsentCategory.PERSONALIZATION.value
    ]

    def classify_category(self, category):
        """Classify consent category."""
        if category in self.ESSENTIAL_CATEGORIES:
            return 'essential'
        elif category in self.DISCRETIONARY_CATEGORIES:
            return 'discretionary'
        else:
            return 'unknown'

    def require_all_discretionary(self):
        """
        Determine if all discretionary consents must be obtained.
        False = bundling not allowed, each can be separate
        """
        return False  # GDPR requires granular consent
```

## Implementation Code

### 3. Cookie Consent Management

```python
class CookieConsentManager:
    """
    Manage cookie consent for web properties.
    """

    def __init__(self, database):
        self.db = database
        self.cookie_categories = {
            'functional': {
                'description': 'Essential for site functionality',
                'requires_consent': False
            },
            'analytical': {
                'description': 'Help us understand site usage',
                'requires_consent': True
            },
            'marketing': {
                'description': 'Used for marketing purposes',
                'requires_consent': True
            },
            'preference': {
                'description': 'Remember user preferences',
                'requires_consent': True
            }
        }

    def set_cookie(self, user_id, cookie_name, cookie_category, value):
        """
        Set cookie only if consent exists.
        """
        if cookie_category == 'functional':
            # Always allowed
            return self._store_cookie(user_id, cookie_name, value)

        # Check consent
        consent = self.db.get_consent(user_id, cookie_category)
        if not consent or not consent.get('given'):
            # Do not set cookie
            self._log_cookie_rejection(user_id, cookie_name, cookie_category)
            return False

        return self._store_cookie(user_id, cookie_name, value)

    def _store_cookie(self, user_id, cookie_name, value):
        """Store cookie value."""
        cookie_record = {
            'user_id': user_id,
            'name': cookie_name,
            'value': value,
            'created_at': datetime.now(),
            'last_updated': datetime.now()
        }
        self.db.store_cookie(cookie_record)
        return True

    def get_cookie(self, user_id, cookie_name):
        """Retrieve cookie if consent valid."""
        cookie = self.db.get_cookie(user_id, cookie_name)

        if not cookie:
            return None

        # Verify consent still valid
        category = self._get_cookie_category(cookie_name)
        if category != 'functional':
            consent = self.db.get_consent(user_id, category)
            if not consent or not consent.get('given'):
                return None

        return cookie['value']
```

## Consent Withdrawal and Revocation

### 4. Revocation System

```python
class ConsentRevocationEngine:
    """
    Handle consent withdrawal and revocation.
    """

    def __init__(self, database, notification_service, audit_logger):
        self.db = database
        self.notify = notification_service
        self.audit = audit_logger

    def revoke_consent(self, data_subject_id, categories, reason=None):
        """
        Process consent revocation.
        Revocation is effective immediately.
        """
        revocation_record = {
            'id': str(uuid.uuid4()),
            'data_subject_id': data_subject_id,
            'categories': categories,
            'revoked_at': datetime.now(),
            'reason': reason,
            'effective_immediately': True
        }

        # Store revocation
        self.db.store_revocation(revocation_record)

        # Stop processing for each category
        for category in categories:
            self._stop_processing(data_subject_id, category)

            # Log revocation
            self.audit.log_event(
                subject_id=data_subject_id,
                event_type='consent_revoked',
                details={
                    'category': category,
                    'revocation_id': revocation_record['id']
                }
            )

        # Notify data subject
        self.notify.send_revocation_confirmation(
            data_subject_id,
            categories,
            revocation_record
        )

        return revocation_record

    def _stop_processing(self, data_subject_id, category):
        """Halt processing based on revoked consent."""
        # Identify active processing activities using this consent
        activities = self.db.get_processing_by_consent(data_subject_id, category)

        for activity in activities:
            # Stop activity
            activity['status'] = 'stopped_revoked_consent'
            activity['stopped_at'] = datetime.now()
            self.db.update_activity(activity)

            # Log cessation
            self._log_processing_stop(activity['id'], data_subject_id)

    def revoke_all_consent(self, data_subject_id):
        """
        Revoke all discretionary consent at once.
        """
        discretionary_categories = [
            ConsentCategory.MARKETING.value,
            ConsentCategory.ANALYTICS.value,
            ConsentCategory.PROFILING.value,
            ConsentCategory.THIRD_PARTY_SHARING.value,
            ConsentCategory.PREFERENCE_DATA.value,
            ConsentCategory.PERSONALIZATION.value
        ]

        return self.revoke_consent(
            data_subject_id,
            discretionary_categories,
            reason='bulk_revocation'
        )

    def easy_unsubscribe(self, email_address):
        """
        Provide single-click unsubscribe functionality.
        """
        data_subject = self.db.get_subject_by_email(email_address)

        if data_subject:
            # Revoke marketing consent
            self.revoke_consent(
                data_subject['id'],
                [ConsentCategory.MARKETING.value],
                reason='email_unsubscribe'
            )

        return True
```

## Proof of Consent

### 5. Consent Verification and Proof

```python
class ConsentProofGenerator:
    """
    Generate proof of valid consent for regulatory inspection.
    """

    def __init__(self, database):
        self.db = database

    def generate_consent_proof(self, data_subject_id, category):
        """
        Generate proof that valid consent exists.
        """
        consent = self.db.get_consent(data_subject_id, category)

        if not consent or not consent.get('given'):
            return {
                'valid_consent': False,
                'reason': 'No valid consent on file'
            }

        proof = {
            'data_subject_id': data_subject_id,
            'category': category,
            'valid': True,
            'consent_date': consent['recorded_at'].isoformat(),
            'consent_id': consent['id'],
            'evidence': {
                'ip_address': consent.get('ip_address'),
                'user_agent': consent.get('user_agent'),
                'timestamp': consent['recorded_at'].isoformat(),
                'channel': consent.get('channel'),
                'explicit_affirmation': 'checked_checkbox' if consent.get('method') == 'checkbox' else 'clicked_button'
            },
            'revocations': self._get_revocation_history(data_subject_id, category),
            'current_status': 'active'
        }

        return proof

    def generate_audit_report(self, from_date, to_date):
        """
        Generate consent audit report for regulatory submission.
        """
        consent_records = self.db.get_consents_in_period(from_date, to_date)

        report = {
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': from_date.isoformat(),
                'end': to_date.isoformat()
            },
            'summary': {
                'total_consents': len(consent_records),
                'by_category': self._count_by_category(consent_records),
                'consent_rate': self._calculate_consent_rate(consent_records),
                'revocation_rate': self._calculate_revocation_rate(consent_records)
            },
            'detailed_records': consent_records
        }

        return report

    def _get_revocation_history(self, data_subject_id, category):
        """Get revocation history for category."""
        revocations = self.db.get_revocations(data_subject_id, category)

        return [
            {
                'revoked_at': rev['revoked_at'].isoformat(),
                'reason': rev.get('reason')
            }
            for rev in revocations
        ]
```

## Monitoring and Compliance

### 6. Consent Compliance Monitor

```python
class ConsentComplianceMonitor:
    """
    Monitor consent compliance and flag issues.
    """

    def __init__(self, database, alert_service):
        self.db = database
        self.alerts = alert_service

    def continuous_compliance_check(self):
        """
        Run continuous compliance monitoring.
        """
        checks = [
            self.check_required_consents(),
            self.check_valid_consents(),
            self.check_revocation_implementation(),
            self.check_consent_renewal()
        ]

        for check in checks:
            if check['issues']:
                self.alerts.send_alert(check)

    def check_required_consents(self):
        """
        Verify consent exists for all processing activities.
        """
        processing_activities = self.db.get_all_processing_activities()
        issues = []

        for activity in processing_activities:
            if activity['requires_consent']:
                # Check if any subjects have valid consent
                subjects = activity.get('affected_subjects', [])
                for subject in subjects:
                    if not self._has_valid_consent(subject, activity['category']):
                        issues.append({
                            'type': 'missing_consent',
                            'subject_id': subject,
                            'category': activity['category'],
                            'activity': activity['id']
                        })

        return {
            'check': 'required_consents',
            'issues': issues
        }

    def check_valid_consents(self):
        """Check for expired or revoked consents still in use."""
        consents = self.db.get_all_consents()
        issues = []

        for consent in consents:
            if consent['status'] == 'active':
                # Check expiration
                if datetime.fromisoformat(consent['expires_at']) < datetime.now():
                    issues.append({
                        'type': 'expired_consent',
                        'consent_id': consent['id'],
                        'expired_at': consent['expires_at']
                    })

                # Check revocations
                revocations = self.db.get_revocations(
                    consent['data_subject_id'],
                    consent['category']
                )
                if revocations and revocations[-1]['timestamp'] > consent['recorded_at']:
                    issues.append({
                        'type': 'revoked_consent_in_use',
                        'consent_id': consent['id'],
                        'revoked_at': revocations[-1]['timestamp']
                    })

        return {
            'check': 'valid_consents',
            'issues': issues
        }

    def check_revocation_implementation(self):
        """Verify revocations are being honored."""
        revocations = self.db.get_recent_revocations(days=30)
        issues = []

        for revocation in revocations:
            # Check processing has stopped
            active_activities = self.db.get_active_processing(
                revocation['data_subject_id'],
                revocation['category']
            )

            if active_activities:
                issues.append({
                    'type': 'revocation_not_honored',
                    'revocation_id': revocation['id'],
                    'still_processing': active_activities
                })

        return {
            'check': 'revocation_implementation',
            'issues': issues
        }

    def _has_valid_consent(self, subject_id, category):
        """Check if subject has valid, non-revoked consent."""
        consent = self.db.get_consent(subject_id, category)

        if not consent or not consent.get('given'):
            return False

        # Check not expired
        if datetime.fromisoformat(consent['expires_at']) < datetime.now():
            return False

        # Check not revoked
        revocations = self.db.get_revocations(subject_id, category)
        if revocations and revocations[-1]['timestamp'] > consent['recorded_at']:
            return False

        return True
```

## Conclusion

Automated consent management enables:

- Compliant consent collection
- Easy revocation and withdrawal
- Comprehensive audit trails
- Proof of valid consent
- Continuous compliance monitoring

Properly implemented, it builds trust with data subjects while ensuring regulatory compliance.
