# Breach Notification Automation Guide

## Executive Summary

This comprehensive guide covers automated systems for detecting, assessing, classifying, and reporting data breaches under GDPR, state privacy laws, and industry regulations. It provides frameworks for incident response automation, notification workflows, and regulatory reporting.

## Table of Contents

1. [Introduction](#introduction)
2. [Breach Definition and Requirements](#breach-definition-and-requirements)
3. [Detection and Classification](#detection-and-classification)
4. [Risk Assessment Framework](#risk-assessment-framework)
5. [Notification Workflows](#notification-workflows)
6. [Code Implementation](#code-implementation)
7. [Regulatory Reporting](#regulatory-reporting)
8. [Post-Incident Management](#post-incident-management)

## Introduction

GDPR requires breach notification to:
- Supervisory authority (within 72 hours)
- Affected data subjects (without undue delay)
- Media (if high risk)

Automation enables:
- Rapid breach detection and classification
- Timely assessment of risk
- Automated notification generation
- Regulatory reporting
- Incident documentation

## Breach Definition and Requirements

### What Constitutes a Breach

Under GDPR Article 33, a breach is:

> "a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to personal data transmitted, stored or otherwise processed"

### Notification Trigger

Breaches must be reported if there is risk to rights and freedoms of data subjects. Factors include:

- **Nature and scope** of breach
- **Likelihood and severity** of risk
- **Type of data** (sensitive vs. general)
- **Number of subjects** affected
- **Consequences** (identity theft, fraud, etc.)

### Timeline Requirements

- **72 hours**: Notify authority (from becoming aware)
- **Without undue delay**: Notify data subjects
- **ASAP**: Internal notification
- **Immediate**: Incident response activation

## Detection and Classification

### 1. Automated Breach Detection

```python
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid
from typing import Dict, List, Optional

class BreachSeverity(Enum):
    """Breach severity classification."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class BreachType(Enum):
    """Types of security breaches."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    MISCONFIGURATION = "misconfiguration"
    ENCRYPTION_FAILURE = "encryption_failure"
    DELETION = "deletion"
    ALTERATION = "alteration"
    LOSS = "loss"

class BreachDetectionEngine:
    """
    Automated breach detection from multiple sources.
    """

    def __init__(self, database, security_tools, notification_service):
        self.db = database
        self.security = security_tools
        self.notify = notification_service

    def detect_and_report_breach(self, breach_evidence: Dict):
        """
        Detect breach and initiate response.
        
        Args:
            breach_evidence: Evidence of breach (from security tools, user reports, etc.)
        """
        # Create incident record
        incident = {
            'id': str(uuid.uuid4()),
            'reported_at': datetime.now(),
            'source': breach_evidence.get('source'),
            'type': breach_evidence.get('type'),
            'description': breach_evidence.get('description'),
            'status': 'detected',
            'severity': None,
            'affected_data': None,
            'assessment': None
        }

        # Store incident
        self.db.store_incident(incident)

        # Trigger investigation
        self._initiate_investigation(incident, breach_evidence)

        return incident

    def _initiate_investigation(self, incident, evidence):
        """
        Initiate breach investigation and assessment.
        """
        investigation = {
            'id': str(uuid.uuid4()),
            'incident_id': incident['id'],
            'started_at': datetime.now(),
            'status': 'in_progress',
            'findings': []
        }

        # Collect evidence
        evidence_files = self._collect_evidence(incident, evidence)
        investigation['evidence_files'] = evidence_files

        # Assess scope
        scope_assessment = self._assess_scope(incident)
        investigation['scope'] = scope_assessment

        # Identify affected data
        affected_data = self._identify_affected_data(
            incident,
            scope_assessment
        )
        investigation['affected_data'] = affected_data

        # Store investigation
        self.db.store_investigation(investigation)

        # Alert incident response team
        self.notify.alert_incident_response_team(incident, investigation)

        return investigation

    def _assess_scope(self, incident):
        """
        Assess scope of breach.
        """
        scope = {
            'assessment_date': datetime.now().isoformat(),
            'breach_type': incident.get('type'),
            'entry_point': self._identify_entry_point(incident),
            'lateral_movement': self._assess_lateral_movement(incident),
            'systems_affected': self._identify_affected_systems(incident),
            'data_accessed': self._identify_accessed_data(incident),
            'scope_severity': self._calculate_scope_severity(incident)
        }

        return scope

    def _identify_affected_data(self, incident, scope):
        """
        Identify what personal data was involved.
        """
        affected_data = {
            'data_categories': [],
            'subject_count': 0,
            'sensitive_indicators': []
        }

        # Query affected systems
        systems = scope.get('systems_affected', [])
        for system in systems:
            system_data = self.db.get_data_in_system(system)
            
            for item in system_data:
                if self._is_accessible_by_breach(item, incident):
                    # Identify data categories
                    categories = self._categorize_data(item)
                    affected_data['data_categories'].extend(categories)

                    # Track affected subjects
                    if 'subject_id' in item:
                        affected_data['subject_count'] += 1

                    # Flag sensitive data
                    if self._is_sensitive(item):
                        affected_data['sensitive_indicators'].append(
                            f"Sensitive data: {categories}"
                        )

        # Deduplicate
        affected_data['data_categories'] = list(set(affected_data['data_categories']))

        return affected_data

    def _identify_entry_point(self, incident):
        """Identify how breach occurred."""
        breach_type = incident.get('type')

        entry_points = {
            BreachType.UNAUTHORIZED_ACCESS.value: 'Unauthorized system access',
            BreachType.MALWARE.value: 'Malware infection',
            BreachType.RANSOMWARE.value: 'Ransomware deployment',
            BreachType.DATA_EXFILTRATION.value: 'Data exfiltration',
            BreachType.INSIDER_THREAT.value: 'Insider threat',
            BreachType.MISCONFIGURATION.value: 'Configuration error',
            BreachType.ENCRYPTION_FAILURE.value: 'Encryption failure'
        }

        return entry_points.get(breach_type, 'Unknown')

    def _identify_affected_systems(self, incident):
        """Identify systems involved in breach."""
        # Analyze logs, system checks, security alerts
        affected = []

        # Check database access logs
        db_incidents = self.security.check_database_access_logs(
            incident['reported_at'] - timedelta(hours=24),
            incident['reported_at']
        )
        if db_incidents:
            affected.append('database')

        # Check file access
        file_incidents = self.security.check_file_access_logs(
            incident['reported_at'] - timedelta(hours=24),
            incident['reported_at']
        )
        if file_incidents:
            affected.append('file_storage')

        # Check network activity
        network_incidents = self.security.check_network_logs(
            incident['reported_at'] - timedelta(hours=24),
            incident['reported_at']
        )
        if network_incidents:
            affected.append('network')

        return affected

    def _identify_accessed_data(self, incident):
        """Identify what data was actually accessed."""
        breach_type = incident.get('type')

        if breach_type == BreachType.DATA_EXFILTRATION.value:
            # Data was copied/stolen
            exfiltration_logs = self.security.get_exfiltration_logs(
                incident['reported_at'] - timedelta(hours=48),
                incident['reported_at']
            )
            return {
                'method': 'exfiltration',
                'data_size': sum(log['size'] for log in exfiltration_logs),
                'records_count': len(exfiltration_logs)
            }

        elif breach_type == BreachType.UNAUTHORIZED_ACCESS.value:
            # Someone accessed data
            access_logs = self.security.get_unauthorized_access_logs(
                incident['reported_at'] - timedelta(hours=48),
                incident['reported_at']
            )
            return {
                'method': 'unauthorized_access',
                'access_count': len(access_logs),
                'data_accessed': list(set(
                    log['data_type'] for log in access_logs
                ))
            }

        return {'method': 'unknown'}

    def _is_sensitive(self, data_item):
        """Check if data is sensitive."""
        sensitive_types = [
            'health',
            'genetic',
            'biometric',
            'criminal',
            'financial',
            'ssn',
            'passport'
        ]

        data_type = data_item.get('type', '').lower()
        return any(sensitive in data_type for sensitive in sensitive_types)

    def _calculate_scope_severity(self, incident):
        """Calculate severity based on scope."""
        factors = {
            'breach_type_severity': self._get_breach_type_severity(incident.get('type')),
            'affected_system_count': len(self._identify_affected_systems(incident)),
            'data_sensitivity': self._assess_data_sensitivity(incident)
        }

        # Weighted calculation
        severity_score = (
            factors['breach_type_severity'] * 0.4 +
            min(factors['affected_system_count'] / 5, 1.0) * 0.3 +
            factors['data_sensitivity'] * 0.3
        )

        if severity_score > 0.75:
            return BreachSeverity.CRITICAL
        elif severity_score > 0.5:
            return BreachSeverity.HIGH
        elif severity_score > 0.25:
            return BreachSeverity.MEDIUM
        else:
            return BreachSeverity.LOW
```

## Risk Assessment Framework

### 2. Risk Assessment System

```python
class BreachRiskAssessment:
    """
    Assess risk to data subjects from breach.
    Required to determine notification necessity.
    """

    def __init__(self, database):
        self.db = database

    def assess_risk(self, incident_id, investigation):
        """
        Comprehensive risk assessment per GDPR Article 34.
        
        Returns:
            high_risk (bool): Whether notification to subjects required
        """
        incident = self.db.get_incident(incident_id)
        
        risk_factors = {
            'data_sensitivity': self._assess_data_sensitivity(investigation),
            'subject_count': self._assess_subject_count(investigation),
            'likelihood_of_misuse': self._assess_misuse_likelihood(incident, investigation),
            'identity_theft_risk': self._assess_identity_theft_risk(investigation),
            'financial_impact': self._assess_financial_impact(investigation),
            'discrimination_risk': self._assess_discrimination_risk(investigation)
        }

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(risk_factors)

        assessment = {
            'incident_id': incident_id,
            'assessment_date': datetime.now().isoformat(),
            'risk_factors': risk_factors,
            'overall_risk_score': overall_risk['score'],
            'risk_level': overall_risk['level'],
            'notification_required': overall_risk['level'] in ['HIGH', 'CRITICAL'],
            'reasoning': overall_risk['reasoning']
        }

        return assessment

    def _assess_data_sensitivity(self, investigation):
        """
        Assess sensitivity of data involved.
        Scale: 0 (not sensitive) to 1 (highly sensitive)
        """
        data_categories = investigation.get('affected_data', {}).get('data_categories', [])
        
        sensitive_weights = {
            'health': 1.0,
            'genetic': 1.0,
            'biometric': 0.9,
            'criminal': 0.9,
            'financial': 0.8,
            'identification': 0.7,
            'contact': 0.3,
            'general': 0.1
        }

        if not data_categories:
            return 0.5  # Unknown = medium sensitivity

        sensitivities = [
            sensitive_weights.get(cat.lower(), 0.5)
            for cat in data_categories
        ]

        return max(sensitivities) if sensitivities else 0.5

    def _assess_subject_count(self, investigation):
        """
        Assess number of affected subjects.
        More subjects = higher risk notification needed.
        """
        subject_count = investigation.get('affected_data', {}).get('subject_count', 0)

        if subject_count == 0:
            return 0.1
        elif subject_count < 100:
            return 0.3
        elif subject_count < 1000:
            return 0.6
        else:
            return 1.0

    def _assess_misuse_likelihood(self, incident, investigation):
        """
        Assess likelihood data will be misused.
        """
        breach_type = incident.get('type')
        
        # Exfiltration = high misuse risk
        if breach_type == BreachType.DATA_EXFILTRATION.value:
            return 0.9

        # Unauthorized access = medium risk
        elif breach_type == BreachType.UNAUTHORIZED_ACCESS.value:
            return 0.6

        # Loss/deletion = low misuse risk (identity theft risk instead)
        elif breach_type in [BreachType.LOSS.value, BreachType.DELETION.value]:
            return 0.2

        return 0.5

    def _assess_identity_theft_risk(self, investigation):
        """
        Assess risk of identity theft.
        """
        data_categories = investigation.get('affected_data', {}).get('data_categories', [])
        
        identity_data = [
            'identification',
            'ssn',
            'passport',
            'financial',
            'contact'
        ]

        has_identity_data = any(
            cat.lower() in identity_data
            for cat in data_categories
        )

        return 0.8 if has_identity_data else 0.2

    def _calculate_overall_risk(self, risk_factors):
        """
        Calculate overall risk using weighted factors.
        """
        weights = {
            'data_sensitivity': 0.25,
            'subject_count': 0.20,
            'likelihood_of_misuse': 0.25,
            'identity_theft_risk': 0.15,
            'financial_impact': 0.10,
            'discrimination_risk': 0.05
        }

        risk_score = sum(
            risk_factors.get(factor, 0) * weight
            for factor, weight in weights.items()
        )

        # Normalize to 0-1
        risk_score = min(risk_score, 1.0)

        # Determine risk level
        if risk_score > 0.75:
            risk_level = 'CRITICAL'
        elif risk_score > 0.5:
            risk_level = 'HIGH'
        elif risk_score > 0.25:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'score': risk_score,
            'level': risk_level,
            'reasoning': self._generate_risk_reasoning(risk_factors, risk_score)
        }

    def _generate_risk_reasoning(self, factors, score):
        """Generate human-readable risk reasoning."""
        reasons = []

        if factors['data_sensitivity'] > 0.7:
            reasons.append('Sensitive personal data involved')

        if factors['subject_count'] > 0.7:
            reasons.append('Large number of subjects affected')

        if factors['likelihood_of_misuse'] > 0.7:
            reasons.append('High likelihood of misuse')

        if factors['identity_theft_risk'] > 0.7:
            reasons.append('Identity theft risk present')

        return ' | '.join(reasons) if reasons else 'Standard data breach'
```

## Notification Workflows

### 3. Authority Notification System

```python
class AuthorityNotificationEngine:
    """
    Handle notification to supervisory authority.
    Required within 72 hours of becoming aware.
    """

    def __init__(self, database, notification_service):
        self.db = database
        self.notify = notification_service

    def prepare_authority_notification(self, incident_id, assessment):
        """
        Prepare notification for supervisory authority (DPA).
        """
        incident = self.db.get_incident(incident_id)
        investigation = self.db.get_investigation(incident_id)

        notification = {
            'id': str(uuid.uuid4()),
            'incident_id': incident_id,
            'authority_notification_id': str(uuid.uuid4()),
            'prepared_at': datetime.now(),
            'deadline': datetime.now() + timedelta(hours=72),
            'content': {
                'nature_of_breach': self._describe_breach(incident, investigation),
                'data_categories': investigation.get('affected_data', {}).get('data_categories', []),
                'approximate_number_of_subjects': investigation.get('affected_data', {}).get('subject_count', 0),
                'likely_consequences': self._describe_consequences(assessment),
                'measures_taken': self._describe_measures_taken(incident),
                'contact_point': self._get_contact_point()
            }
        }

        return notification

    def _describe_breach(self, incident, investigation):
        """Describe breach facts."""
        return f"""
Breach Type: {incident.get('type')}
Breach Date: {incident.get('reported_at', datetime.now()).isoformat()}
Discovery Date: {investigation.get('started_at').isoformat()}
Description: {incident.get('description')}
Entry Point: {investigation.get('scope', {}).get('entry_point')}
Systems Affected: {', '.join(investigation.get('scope', {}).get('systems_affected', []))}
        """

    def _describe_consequences(self, assessment):
        """Describe likely consequences for data subjects."""
        return f"""
Risk Level: {assessment['risk_level']}
Risk Score: {assessment['overall_risk_score']:.2%}
Identity Theft Risk: High likelihood of identity theft and financial loss
Discrimination Risk: Possible discrimination based on accessed data
Privacy Impact: Unauthorized access to personal information
        """

    def _describe_measures_taken(self, incident):
        """Describe remediation measures."""
        measures = {
            'incident_confirmation': 'Breach confirmed and logged',
            'containment': 'Affected systems isolated and secured',
            'investigation': 'Forensic investigation initiated',
            'notification': 'Affected subjects will be notified',
            'prevention': 'Security improvements planned and implemented'
        }

        return '\n'.join(f"- {v}" for v in measures.values())

    def submit_notification(self, notification, authority_email):
        """
        Submit notification to supervisory authority.
        """
        # Create formal notification document
        notification_document = self._create_notification_document(notification)

        # Send to authority
        submission = self.notify.send_to_authority(
            recipient_email=authority_email,
            subject=f"Data Breach Notification - {notification['incident_id']}",
            content=notification_document,
            attachments=self._prepare_attachments(notification)
        )

        # Log submission
        notification['submitted_at'] = datetime.now()
        notification['submission_id'] = submission['id']
        self.db.store_notification(notification)

        return submission
```

### 4. Data Subject Notification

```python
class DataSubjectNotificationEngine:
    """
    Handle notification to affected data subjects.
    """

    def __init__(self, database, email_service, sms_service):
        self.db = database
        self.email = email_service
        self.sms = sms_service

    def prepare_subject_notifications(self, incident_id, assessment):
        """
        Prepare notifications for affected data subjects.
        """
        incident = self.db.get_incident(incident_id)
        investigation = self.db.get_investigation(incident_id)
        affected_subjects = self._get_affected_subjects(investigation)

        notifications = []

        for subject in affected_subjects:
            notification = {
                'id': str(uuid.uuid4()),
                'incident_id': incident_id,
                'subject_id': subject['id'],
                'prepared_at': datetime.now(),
                'status': 'prepared',
                'content': self._create_subject_notification_content(
                    incident,
                    investigation,
                    assessment,
                    subject
                )
            }

            notifications.append(notification)

        return notifications

    def _create_subject_notification_content(self, incident, investigation, assessment, subject):
        """
        Create personalized notification content for subject.
        """
        content = {
            'subject_heading': 'Data Breach Notification',
            'body': self._generate_breach_notification_text(
                incident, investigation, assessment
            ),
            'what_happened': self._describe_what_happened(incident, investigation),
            'what_information_was_involved': self._describe_affected_data(investigation, subject),
            'what_we_are_doing': self._describe_remediation(incident),
            'what_you_can_do': self._provide_subject_guidance(assessment),
            'contact_information': self._get_contact_info()
        }

        return content

    def _generate_breach_notification_text(self, incident, investigation, assessment):
        """Generate main notification text."""
        return f"""
We are writing to inform you of a security incident affecting our systems that may have involved your personal information.

On {incident.get('reported_at').strftime('%B %d, %Y')}, we discovered a data security incident.
Following investigation, we have determined that your personal information may have been affected.

Risk Assessment: {assessment['risk_level']}

This letter provides you with information about the incident and steps we are taking to protect your privacy.
        """

    def _describe_what_happened(self, incident, investigation):
        """Explain what happened in plain language."""
        return f"""
What Happened:
Our investigation found that {incident.get('description').lower()}.
The breach was discovered on {incident.get('reported_at').strftime('%B %d, %Y')}.
We have initiated a comprehensive investigation and taken immediate steps to secure our systems.
        """

    def _describe_affected_data(self, investigation, subject):
        """List what personal data was involved."""
        affected_data = investigation.get('affected_data', {})
        data_categories = affected_data.get('data_categories', [])

        return f"""
The following types of your personal information may have been affected:
{chr(10).join(f"- {cat.title()}" for cat in data_categories)}
        """

    def _describe_remediation(self, incident):
        """Explain remediation steps."""
        return """
What We're Doing:
- We have isolated affected systems and prevented unauthorized access
- We have engaged third-party security experts to investigate
- We are implementing additional security measures
- We are enhancing our security monitoring and controls
        """

    def _provide_subject_guidance(self, assessment):
        """Provide guidance for affected subjects."""
        guidance = """
What You Can Do:
- Monitor your accounts for suspicious activity
- Consider freezing credit if concerned about identity theft
- Change passwords for accounts that use your email
- Enable two-factor authentication where available
- Review credit reports for unauthorized activity
- Contact us if you notice suspicious activity
        """

        if assessment['risk_level'] in ['HIGH', 'CRITICAL']:
            guidance += """

Given the sensitivity of the data involved, we recommend:
- Consider identity theft protection services
- Monitor financial accounts closely
- Be alert to phishing and social engineering attempts
            """

        return guidance

    def send_notifications(self, notifications):
        """
        Send notifications to affected data subjects.
        """
        results = {
            'sent': 0,
            'failed': 0,
            'pending': 0,
            'details': []
        }

        for notification in notifications:
            subject = self.db.get_subject(notification['subject_id'])
            
            try:
                # Send via email
                email_result = self.email.send(
                    to_email=subject.get('email'),
                    subject='Important Security Notification',
                    content=notification['content']
                )

                # Send via SMS if number available
                if subject.get('phone'):
                    self.sms.send(
                        to_phone=subject['phone'],
                        content=self._create_sms_notification(notification['content'])
                    )

                notification['status'] = 'sent'
                notification['sent_at'] = datetime.now()
                results['sent'] += 1

            except Exception as e:
                notification['status'] = 'failed'
                notification['error'] = str(e)
                results['failed'] += 1

            self.db.store_notification(notification)
            results['details'].append(notification)

        return results
```

## Code Implementation

### 5. Incident Response Orchestration

```python
class IncidentResponseOrchestrator:
    """
    Orchestrate complete incident response workflow.
    """

    def __init__(self, database, services):
        self.db = database
        self.services = services

    def execute_incident_response(self, incident_id):
        """
        Execute complete incident response process.
        """
        incident = self.db.get_incident(incident_id)
        
        # Timeline tracking
        response_timeline = {
            'incident_id': incident_id,
            'start_time': datetime.now(),
            'milestones': []
        }

        # 1. Activate incident response (immediate)
        response_timeline['milestones'].append({
            'step': 'incident_activation',
            'time': datetime.now(),
            'status': 'completed'
        })

        # 2. Investigation (ongoing)
        investigation = self.services['detection'].initiate_investigation(
            incident,
            self.db.get_incident_evidence(incident_id)
        )

        response_timeline['milestones'].append({
            'step': 'investigation_started',
            'time': datetime.now(),
            'investigation_id': investigation['id']
        })

        # 3. Assessment (within 24 hours)
        assessment = self.services['risk'].assess_risk(
            incident_id,
            investigation
        )

        response_timeline['milestones'].append({
            'step': 'risk_assessment_completed',
            'time': datetime.now(),
            'risk_level': assessment['risk_level']
        })

        # 4. Authority notification (within 72 hours)
        if assessment['notification_required']:
            authority_notification = self.services['authority'].prepare_authority_notification(
                incident_id,
                assessment
            )

            authority_deadline = datetime.now() + timedelta(hours=72)
            self.services['authority'].submit_notification(
                authority_notification,
                authority_email=self._get_dpa_email()
            )

            response_timeline['milestones'].append({
                'step': 'authority_notified',
                'time': datetime.now(),
                'deadline': authority_deadline
            })

        # 5. Subject notifications (without undue delay)
        subject_notifications = self.services['subject'].prepare_subject_notifications(
            incident_id,
            assessment
        )

        self.services['subject'].send_notifications(subject_notifications)

        response_timeline['milestones'].append({
            'step': 'subjects_notified',
            'time': datetime.now(),
            'count': len(subject_notifications)
        })

        # 6. Documentation and closure
        response_timeline['end_time'] = datetime.now()
        response_timeline['duration_hours'] = (
            (response_timeline['end_time'] - response_timeline['start_time']).total_seconds() / 3600
        )

        self.db.store_response_timeline(response_timeline)

        return {
            'status': 'incident_response_completed',
            'incident_id': incident_id,
            'timeline': response_timeline
        }

    def _get_dpa_email(self):
        """Get relevant Data Protection Authority email."""
        # Return based on organization jurisdiction
        dpa_emails = {
            'EU': 'breach-notification@dpa.eu',
            'US': 'breach@attorney.general.gov',
            'UK': 'breach@ico.org.uk'
        }
        return dpa_emails.get('EU')  # Default to EU
```

## Regulatory Reporting

### 6. Compliance Reporting

```python
class BreachComplianceReporter:
    """
    Generate compliance reports for regulatory inspection.
    """

    def __init__(self, database):
        self.db = database

    def generate_breach_report(self, incident_id):
        """
        Generate comprehensive breach report for regulators.
        """
        incident = self.db.get_incident(incident_id)
        investigation = self.db.get_investigation(incident_id)
        assessment = self.db.get_risk_assessment(incident_id)
        response_timeline = self.db.get_response_timeline(incident_id)

        report = {
            'report_id': str(uuid.uuid4()),
            'generated_at': datetime.now().isoformat(),
            'incident_id': incident_id,
            'executive_summary': self._executive_summary(incident, assessment),
            'incident_details': incident,
            'investigation_findings': investigation,
            'risk_assessment': assessment,
            'response_timeline': response_timeline,
            'actions_taken': self._list_actions(incident),
            'preventive_measures': self._list_preventive_measures(incident)
        }

        return report

    def generate_annual_breach_report(self, year):
        """
        Generate annual breach report covering all incidents.
        """
        incidents = self.db.get_incidents_by_year(year)

        report = {
            'year': year,
            'generated_at': datetime.now().isoformat(),
            'total_incidents': len(incidents),
            'by_severity': self._group_by_severity(incidents),
            'by_type': self._group_by_type(incidents),
            'subjects_affected': self._total_subjects_affected(incidents),
            'notification_timelines': self._analyze_notification_timelines(incidents),
            'trend_analysis': self._analyze_trends(incidents)
        }

        return report
```

## Post-Incident Management

### 7. Remediation and Prevention

```python
class RemediationManager:
    """
    Manage post-incident remediation and prevention.
    """

    def __init__(self, database):
        self.db = database

    def create_remediation_plan(self, incident_id):
        """
        Create remediation and prevention plan.
        """
        incident = self.db.get_incident(incident_id)
        
        plan = {
            'id': str(uuid.uuid4()),
            'incident_id': incident_id,
            'created_at': datetime.now(),
            'immediate_actions': self._immediate_actions(incident),
            'short_term_remediation': self._short_term_remediation(incident),
            'long_term_prevention': self._long_term_prevention(incident),
            'monitoring_plan': self._create_monitoring_plan(incident)
        }

        return plan

    def _immediate_actions(self, incident):
        """Define immediate response actions."""
        return [
            'Isolate affected systems',
            'Disable compromised credentials',
            'Engage forensic team',
            'Activate incident response team',
            'Document all findings'
        ]

    def _short_term_remediation(self, incident):
        """Define short-term fixes (30 days)."""
        return [
            'Patch vulnerabilities',
            'Implement network segmentation',
            'Enhance monitoring',
            'Update security policies',
            'Conduct security awareness training'
        ]

    def _long_term_prevention(self, incident):
        """Define long-term improvements."""
        return [
            'Implement data classification system',
            'Deploy advanced threat detection',
            'Establish zero-trust architecture',
            'Regular security assessments',
            'Continuous vulnerability management'
        ]

    def _create_monitoring_plan(self, incident):
        """Create post-incident monitoring strategy."""
        return {
            'duration_months': 12,
            'monitoring_activities': [
                'Weekly security logs review',
                'Monthly vulnerability scans',
                'Quarterly penetration testing',
                'Real-time threat detection',
                'Data access auditing'
            ],
            'success_criteria': [
                'No recurrence of similar breach',
                'Improved incident response time',
                'Enhanced data protection controls'
            ]
        }
```

## Conclusion

Automated breach notification systems enable organizations to:

- Detect breaches rapidly
- Assess risk accurately
- Notify authorities and subjects timely
- Maintain comprehensive documentation
- Demonstrate regulatory compliance
- Implement preventive measures

Proper automation reduces response time from days to hours, minimizing harm to data subjects and regulatory penalties.
