#!/usr/bin/env python3
"""
Breach Detection Engine
Automated detection and classification of data breaches
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class BreachSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DataSensitivity(Enum):
    HIGHLY_SENSITIVE = 5  # Health, biometric, financial
    SENSITIVE = 4        # Identity, location
    MODERATE = 3         # Contact information
    LOW_SENSITIVITY = 2  # Behavioral data
    PUBLIC = 1          # Public information

class BreachDetectionEngine:
    """Detects and assesses data breaches"""

    def __init__(self):
        self.breach_registry = []
        self.breach_alerts = []
        self.investigation_queue = []

    def detect_unusual_access_pattern(self, access_logs: List[Dict]) -> List[Dict]:
        """Detect unusual access patterns that might indicate breach"""
        alerts = []

        # Group by user
        user_activities = {}
        for log in access_logs:
            user = log.get('user_id')
            if user not in user_activities:
                user_activities[user] = []
            user_activities[user].append(log)

        # Analyze each user's activity
        for user, activities in user_activities.items():
            # Check for abnormal volume
            if len(activities) > 100 and self._is_unusual_volume(activities):
                alerts.append({
                    'alert_type': 'unusual_access_volume',
                    'severity': 'high',
                    'user_id': user,
                    'access_count': len(activities),
                    'time_period': '1_hour',
                    'recommendation': 'Investigate immediately'
                })

            # Check for access outside business hours
            after_hours = [a for a in activities if self._is_after_hours(a.get('timestamp'))]
            if len(after_hours) > len(activities) * 0.5:
                alerts.append({
                    'alert_type': 'after_hours_access',
                    'severity': 'medium',
                    'user_id': user,
                    'after_hours_access_count': len(after_hours),
                    'recommendation': 'Verify user authorization'
                })

            # Check for access to sensitive data by non-authorized user
            for activity in activities:
                if activity.get('data_sensitivity') == 'highly_sensitive':
                    if not self._is_authorized_for_data(user, activity.get('data_category')):
                        alerts.append({
                            'alert_type': 'unauthorized_sensitive_access',
                            'severity': 'critical',
                            'user_id': user,
                            'data_accessed': activity.get('data_category'),
                            'timestamp': activity.get('timestamp'),
                            'action': 'IMMEDIATE_INVESTIGATION_REQUIRED'
                        })

        return alerts

    def analyze_data_exfiltration_indicators(self, network_logs: List[Dict]) -> Dict:
        """Analyze network logs for data exfiltration indicators"""
        indicators = {
            'large_data_transfers': [],
            'unusual_destinations': [],
            'encryption_circumvention': [],
            'risk_score': 0
        }

        for log in network_logs:
            # Check for large data transfers
            if log.get('bytes_transferred', 0) > 1_000_000_000:  # 1GB+
                indicators['large_data_transfers'].append({
                    'source': log.get('source'),
                    'destination': log.get('destination'),
                    'bytes': log.get('bytes_transferred'),
                    'timestamp': log.get('timestamp'),
                    'risk_level': 'high'
                })
                indicators['risk_score'] += 3

            # Check for unusual destinations
            if not self._is_trusted_destination(log.get('destination')):
                indicators['unusual_destinations'].append({
                    'destination': log.get('destination'),
                    'source': log.get('source'),
                    'bytes': log.get('bytes_transferred'),
                    'risk_level': 'medium'
                })
                indicators['risk_score'] += 2

            # Check for unencrypted data transfer
            if not log.get('encrypted', False) and log.get('data_type') == 'sensitive':
                indicators['encryption_circumvention'].append({
                    'source': log.get('source'),
                    'destination': log.get('destination'),
                    'data_type': log.get('data_type'),
                    'timestamp': log.get('timestamp'),
                    'risk_level': 'critical'
                })
                indicators['risk_score'] += 5

        return indicators

    def classify_breach_severity(self, breach_data: Dict) -> Dict:
        """Classify breach severity using risk scoring"""
        risk_score = 0

        # Data sensitivity (0-25 points)
        data_sensitivity = breach_data.get('data_sensitivity', DataSensitivity.PUBLIC.value)
        affected_individuals = breach_data.get('affected_individuals', 0)

        if data_sensitivity >= 5:  # Highly sensitive
            risk_score += 25
        elif data_sensitivity >= 4:
            risk_score += 20
        elif data_sensitivity >= 3:
            risk_score += 15
        else:
            risk_score += 5

        # Number of affected individuals (0-25 points)
        if affected_individuals > 100_000:
            risk_score += 25
        elif affected_individuals > 10_000:
            risk_score += 20
        elif affected_individuals > 1_000:
            risk_score += 15
        elif affected_individuals > 100:
            risk_score += 10
        else:
            risk_score += 5

        # Breach scope (0-20 points)
        if breach_data.get('data_accessible_to_unauthorized', False):
            risk_score += 20
        elif breach_data.get('data_encrypted', False):
            risk_score -= 5  # Reduce score if encrypted

        # Time to detection (0-15 points)
        detection_time = breach_data.get('time_to_detection_hours', 24)
        if detection_time <= 1:
            risk_score += 10
        elif detection_time <= 24:
            risk_score += 15
        else:
            risk_score += 5

        # Likelihood of harm (0-15 points)
        if breach_data.get('data_available_on_dark_web', False):
            risk_score += 15
        elif breach_data.get('threat_actor_identified', False):
            risk_score += 12
        else:
            risk_score += 5

        # Determine severity
        if risk_score >= 80:
            severity = BreachSeverity.CRITICAL.value
        elif risk_score >= 60:
            severity = BreachSeverity.HIGH.value
        elif risk_score >= 40:
            severity = BreachSeverity.MEDIUM.value
        else:
            severity = BreachSeverity.LOW.value

        return {
            'risk_score': risk_score,
            'severity': severity,
            'requires_regulatory_notification': severity in ['critical', 'high'],
            'notification_timeline_hours': 72 if severity == BreachSeverity.CRITICAL.value else 360,
            'recommended_actions': self._get_recommended_actions(severity)
        }

    def generate_breach_notification_package(self, breach_id: str, breach_data: Dict) -> Dict:
        """Generate breach notification package for regulators and individuals"""
        severity_assessment = self.classify_breach_severity(breach_data)

        package = {
            'breach_id': breach_id,
            'detection_date': breach_data.get('detection_date'),
            'notification_date': datetime.now().isoformat(),
            'affected_individuals': breach_data.get('affected_individuals'),
            'data_categories_affected': breach_data.get('data_categories'),
            'breach_description': breach_data.get('description'),
            'severity': severity_assessment['severity'],
            'risk_score': severity_assessment['risk_score'],
            'regulatory_authority_notification': {
                'required': severity_assessment['requires_regulatory_notification'],
                'deadline': (datetime.now() + timedelta(hours=severity_assessment['notification_timeline_hours'])).isoformat(),
                'authority': 'ICO',
                'form': 'GDPR_Article_33_Notification'
            },
            'individual_notification': {
                'required': severity_assessment['requires_regulatory_notification'],
                'method': ['email', 'postal_mail'],
                'content_template': 'breach_notification_letter',
                'timeline_days': 30
            },
            'evidence_preservation': [
                'System logs and audit trails',
                'Network traffic captures',
                'Forensic disk images',
                'Database snapshots',
                'Incident timeline'
            ],
            'investigation_status': 'IN_PROGRESS'
        }

        return package

    def generate_breach_register_entry(self, breach_id: str, breach_data: Dict) -> Dict:
        """Generate entry for breach register (Article 33 compliance)"""
        severity = self.classify_breach_severity(breach_data)

        return {
            'breach_id': breach_id,
            'date_of_breach': breach_data.get('breach_date'),
            'date_discovered': breach_data.get('detection_date'),
            'date_reported_to_authority': breach_data.get('authority_notification_date'),
            'data_categories': breach_data.get('data_categories'),
            'approximate_number_affected': breach_data.get('affected_individuals'),
            'severity_level': severity['severity'],
            'likely_consequences': breach_data.get('likely_consequences'),
            'measures_taken': breach_data.get('mitigation_measures', []),
            'resolution_status': 'PENDING'
        }

    def assess_notification_requirement(self, breach_data: Dict) -> Dict:
        """Assess if regulatory notification is required"""
        risk_assessment = self.classify_breach_severity(breach_data)

        requires_notification = risk_assessment['requires_regulatory_notification']

        exceptions = []
        # GDPR exceptions: unlikely to result in high risk to rights and freedoms
        if not breach_data.get('data_accessible_to_unauthorized', False):
            exceptions.append("Data likely not accessible to unauthorized parties")
        if breach_data.get('data_encrypted', False):
            exceptions.append("Data was encrypted")

        notification_exempt = requires_notification and len(exceptions) >= 1

        return {
            'notification_required': requires_notification and not notification_exempt,
            'severity': risk_assessment['severity'],
            'exemption_applicable': notification_exempt,
            'exemption_reasons': exceptions,
            'regulatory_authority': 'ICO' if not notification_exempt else None,
            'notification_deadline': (datetime.now() + timedelta(hours=72)).isoformat() if requires_notification else None
        }

    # Helper methods
    @staticmethod
    def _is_unusual_volume(activities: List[Dict]) -> bool:
        """Check if access volume is unusual"""
        timestamps = [a.get('timestamp') for a in activities]
        # Simple check: more than 50 accesses per minute is unusual
        return len(activities) > 50

    @staticmethod
    def _is_after_hours(timestamp: str) -> bool:
        """Check if access is after business hours"""
        dt = datetime.fromisoformat(timestamp)
        return dt.hour < 6 or dt.hour > 18 or dt.weekday() > 4

    @staticmethod
    def _is_authorized_for_data(user_id: str, data_category: str) -> bool:
        """Check if user is authorized to access data category"""
        # Placeholder - would integrate with actual authorization system
        return True

    @staticmethod
    def _is_trusted_destination(destination: str) -> bool:
        """Check if destination is trusted"""
        trusted_ips = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
        # Simplified check
        return destination.startswith(('10.', '172.', '192.'))

    @staticmethod
    def _get_recommended_actions(severity: str) -> List[str]:
        """Get recommended actions based on severity"""
        actions = {
            'critical': [
                'Initiate incident response plan immediately',
                'Isolate affected systems',
                'Preserve all evidence',
                'Notify legal and executive leadership',
                'Prepare regulatory notification',
                'Begin affected party notification',
                'Engage forensics team'
            ],
            'high': [
                'Activate incident response team',
                'Assess scope and impact',
                'Prepare regulatory notification',
                'Plan notification to affected parties',
                'Implement containment measures'
            ],
            'medium': [
                'Conduct impact assessment',
                'Implement remediation measures',
                'Document investigation',
                'Review controls'
            ],
            'low': [
                'Monitor situation',
                'Document incident',
                'Review affected data'
            ]
        }
        return actions.get(severity, [])


def main():
    engine = BreachDetectionEngine()

    # Example breach data
    breach_example = {
        'breach_date': '2024-01-10',
        'detection_date': '2024-01-12',
        'affected_individuals': 5000,
        'data_categories': ['name', 'email', 'phone_number'],
        'data_sensitivity': 3,
        'data_encrypted': False,
        'data_accessible_to_unauthorized': True,
        'time_to_detection_hours': 48,
        'description': 'Unauthorized access to customer database',
        'likely_consequences': 'Risk of identity theft'
    }

    # Classify breach
    severity = engine.classify_breach_severity(breach_example)
    notification_req = engine.assess_notification_requirement(breach_example)
    notification_pkg = engine.generate_breach_notification_package('BREACH_2024_001', breach_example)

    print(json.dumps({
        'severity_assessment': severity,
        'notification_requirement': notification_req,
        'notification_package': notification_pkg
    }, indent=2, default=str))


if __name__ == '__main__':
    main()
