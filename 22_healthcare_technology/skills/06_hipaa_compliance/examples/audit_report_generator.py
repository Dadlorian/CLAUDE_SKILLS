"""
Automated HIPAA Audit Report Generator
Generates compliance reports from audit logs
"""
from datetime import datetime, timedelta
from collections import defaultdict

class AuditReportGenerator:
    def __init__(self, audit_log_service):
        self.audit_log_service = audit_log_service

    def generate_monthly_report(self, year, month):
        """Generate monthly audit compliance report"""
        logs = self.audit_log_service.get_logs_for_month(year, month)

        report = {
            'period': f'{year}-{month:02d}',
            'total_accesses': len(logs),
            'unique_users': len(set(log['user_id'] for log in logs)),
            'phi_access_by_type': defaultdict(int),
            'access_by_role': defaultdict(int),
            'failed_access_attempts': 0,
            'emergency_access_count': 0,
            'unusual_access_patterns': [],
            'top_accessed_patients': defaultdict(int)
        }

        for log in logs:
            report['access_by_role'][log.get('user_role', 'UNKNOWN')] += 1

            if log['result'] == 'FAILURE':
                report['failed_access_attempts'] += 1

            if log.get('emergency_access'):
                report['emergency_access_count'] += 1

            if log.get('patient_id'):
                report['top_accessed_patients'][log['patient_id']] += 1

        # Top 10 most accessed patients
        report['top_accessed_patients'] = dict(sorted(
            report['top_accessed_patients'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

        return report

    def generate_user_access_report(self, user_id, start_date, end_date):
        """Generate individual user access report"""
        logs = self.audit_log_service.get_user_logs(user_id, start_date, end_date)

        return {
            'user_id': user_id,
            'period': f'{start_date} to {end_date}',
            'total_accesses': len(logs),
            'patients_accessed': len(set(log.get('patient_id') for log in logs if log.get('patient_id'))),
            'access_by_action': defaultdict(int, {log['action']: logs.count(log) for log in logs}),
            'failed_attempts': len([log for log in logs if log['result'] == 'FAILURE']),
            'access_timeline': logs
        }

    def identify_anomalies(self, logs):
        """Identify unusual access patterns"""
        anomalies = []

        # Check for access outside business hours
        for log in logs:
            hour = datetime.fromisoformat(log['timestamp']).hour
            if hour < 6 or hour > 22:
                anomalies.append({
                    'type': 'UNUSUAL_HOURS',
                    'log': log
                })

        # Check for mass access
        user_access_counts = defaultdict(int)
        for log in logs:
            user_access_counts[log['user_id']] += 1

        for user_id, count in user_access_counts.items():
            if count > 100:  # Threshold
                anomalies.append({
                    'type': 'MASS_ACCESS',
                    'user_id': user_id,
                    'count': count
                })

        return anomalies
