"""
HIPAA Breach Detection and Monitoring System
Real-time detection of potential security incidents and breaches
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict

class BreachDetectionMonitor:
    def __init__(self, alert_threshold_config=None):
        self.alert_threshold = alert_threshold_config or {
            'failed_logins': 5,
            'timeframe_minutes': 10,
            'mass_download_threshold': 50,
            'unusual_hours_start': 22,  # 10 PM
            'unusual_hours_end': 6,  # 6 AM
        }
        self.user_activity = defaultdict(list)
        self.alerts = []

    def analyze_login_attempts(self, user_id, timestamp, success):
        """Detect brute force attacks"""
        recent_attempts = [a for a in self.user_activity[user_id]
                          if timestamp - a['timestamp'] < timedelta(minutes=self.alert_threshold['timeframe_minutes'])]

        failed_attempts = [a for a in recent_attempts if not a['success']]

        if len(failed_attempts) >= self.alert_threshold['failed_logins']:
            self.create_alert(
                'POTENTIAL_BRUTE_FORCE',
                f'User {user_id} has {len(failed_attempts)} failed login attempts',
                'HIGH',
                {'user_id': user_id, 'attempts': len(failed_attempts)}
            )

    def detect_mass_access(self, user_id, records_accessed, timeframe_minutes=15):
        """Detect mass PHI downloads"""
        if records_accessed > self.alert_threshold['mass_download_threshold']:
            self.create_alert(
                'MASS_PHI_ACCESS',
                f'User {user_id} accessed {records_accessed} records in {timeframe_minutes} minutes',
                'CRITICAL',
                {'user_id': user_id, 'records': records_accessed}
            )

    def check_unusual_access_time(self, timestamp):
        """Flag access outside normal business hours"""
        hour = timestamp.hour
        return hour >= self.alert_threshold['unusual_hours_start'] or hour < self.alert_threshold['unusual_hours_end']

    def create_alert(self, alert_type, message, severity, metadata):
        """Create security alert for investigation"""
        alert = {
            'alert_id': f'ALERT-{datetime.now().timestamp()}',
            'type': alert_type,
            'message': message,
            'severity': severity,
            'metadata': metadata,
            'timestamp': datetime.now(),
            'status': 'OPEN'
        }
        self.alerts.append(alert)
        logging.warning(f'SECURITY ALERT [{severity}]: {message}')
        return alert

if __name__ == "__main__":
    monitor = BreachDetectionMonitor()
    # Example usage
    monitor.analyze_login_attempts('user123', datetime.now(), False)
