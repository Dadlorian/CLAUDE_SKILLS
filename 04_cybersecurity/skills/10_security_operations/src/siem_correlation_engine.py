"""
SIEM Correlation Engine
Security event correlation and analysis for Security Operations Center (SOC)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class EventSeverity(Enum):
    """Security event severity"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class SecurityEvent:
    """Security event log"""
    event_id: str
    timestamp: datetime
    source_ip: str
    dest_ip: str
    event_type: str
    severity: EventSeverity
    user: Optional[str]
    description: str
    raw_log: str


@dataclass
class Alert:
    """Security alert from correlation"""
    alert_id: str
    title: str
    severity: EventSeverity
    triggered_at: datetime
    related_events: List[str]
    description: str
    recommendation: str


class SIEMCorrelationEngine:
    """
    SIEM Correlation Engine

    Features:
    - Event collection and normalization
    - Correlation rules
    - Anomaly detection
    - Alert generation
    - Threat hunting queries
    """

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.alerts: List[Alert] = []
        self.correlation_rules = self._load_correlation_rules()

    def _load_correlation_rules(self) -> Dict:
        """Load correlation rules"""
        return {
            'brute_force': {
                'description': 'Multiple failed login attempts',
                'threshold': 5,
                'timewindow_minutes': 5,
                'event_type': 'failed_login'
            },
            'lateral_movement': {
                'description': 'Unusual account accessing multiple systems',
                'threshold': 10,
                'timewindow_minutes': 30,
                'event_type': 'account_logon'
            },
            'data_exfiltration': {
                'description': 'Large data transfer to external IP',
                'threshold': 1000000000,  # 1GB
                'timewindow_minutes': 60,
                'event_type': 'data_transfer'
            },
            'privilege_escalation': {
                'description': 'Privilege elevation attempt',
                'threshold': 3,
                'timewindow_minutes': 10,
                'event_type': 'privilege_change'
            }
        }

    def ingest_event(self, event: SecurityEvent):
        """Ingest security event"""
        self.events.append(event)

        # Run correlation rules
        self._check_correlation_rules(event)

    def _check_correlation_rules(self, new_event: SecurityEvent):
        """Check if event triggers any correlation rules"""

        # Brute force detection
        if new_event.event_type == 'failed_login':
            self._detect_brute_force(new_event)

        # Lateral movement detection
        if new_event.event_type == 'account_logon':
            self._detect_lateral_movement(new_event)

        # Privilege escalation detection
        if new_event.event_type == 'privilege_change':
            self._detect_privilege_escalation(new_event)

    def _detect_brute_force(self, event: SecurityEvent):
        """Detect brute force attacks"""
        rule = self.correlation_rules['brute_force']
        timewindow = timedelta(minutes=rule['timewindow_minutes'])
        cutoff_time = event.timestamp - timewindow

        # Count failed logins from same source IP
        failed_attempts = [
            e for e in self.events
            if e.event_type == 'failed_login'
            and e.source_ip == event.source_ip
            and e.timestamp >= cutoff_time
        ]

        if len(failed_attempts) >= rule['threshold']:
            self._create_alert(
                title="Brute Force Attack Detected",
                severity=EventSeverity.HIGH,
                related_events=[e.event_id for e in failed_attempts],
                description=f"Detected {len(failed_attempts)} failed login attempts from {event.source_ip}",
                recommendation="Block source IP, investigate compromised accounts"
            )

    def _detect_lateral_movement(self, event: SecurityEvent):
        """Detect lateral movement"""
        if not event.user:
            return

        rule = self.correlation_rules['lateral_movement']
        timewindow = timedelta(minutes=rule['timewindow_minutes'])
        cutoff_time = event.timestamp - timewindow

        # Count unique systems accessed by user
        user_logins = [
            e for e in self.events
            if e.event_type == 'account_logon'
            and e.user == event.user
            and e.timestamp >= cutoff_time
        ]

        unique_systems = set(e.dest_ip for e in user_logins)

        if len(unique_systems) >= rule['threshold']:
            self._create_alert(
                title="Possible Lateral Movement",
                severity=EventSeverity.CRITICAL,
                related_events=[e.event_id for e in user_logins],
                description=f"User {event.user} accessed {len(unique_systems)} systems in {rule['timewindow_minutes']} minutes",
                recommendation="Investigate user account, check for compromise"
            )

    def _detect_privilege_escalation(self, event: SecurityEvent):
        """Detect privilege escalation attempts"""
        rule = self.correlation_rules['privilege_escalation']
        timewindow = timedelta(minutes=rule['timewindow_minutes'])
        cutoff_time = event.timestamp - timewindow

        # Count privilege elevation attempts
        priv_events = [
            e for e in self.events
            if e.event_type == 'privilege_change'
            and e.user == event.user
            and e.timestamp >= cutoff_time
        ]

        if len(priv_events) >= rule['threshold']:
            self._create_alert(
                title="Privilege Escalation Detected",
                severity=EventSeverity.CRITICAL,
                related_events=[e.event_id for e in priv_events],
                description=f"Multiple privilege escalation attempts by {event.user}",
                recommendation="Lock account, investigate for compromise"
            )

    def _create_alert(
        self,
        title: str,
        severity: EventSeverity,
        related_events: List[str],
        description: str,
        recommendation: str
    ):
        """Create security alert"""
        alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        alert = Alert(
            alert_id=alert_id,
            title=title,
            severity=severity,
            triggered_at=datetime.now(),
            related_events=related_events,
            description=description,
            recommendation=recommendation
        )

        self.alerts.append(alert)
        print(f"[ALERT] {title} - Severity: {severity.name}")

    def search_events(
        self,
        event_type: Optional[str] = None,
        source_ip: Optional[str] = None,
        user: Optional[str] = None,
        timewindow_hours: int = 24
    ) -> List[SecurityEvent]:
        """Search events with filters"""
        cutoff_time = datetime.now() - timedelta(hours=timewindow_hours)

        results = [
            e for e in self.events
            if e.timestamp >= cutoff_time
        ]

        if event_type:
            results = [e for e in results if e.event_type == event_type]

        if source_ip:
            results = [e for e in results if e.source_ip == source_ip]

        if user:
            results = [e for e in results if e.user == user]

        return results

    def generate_soc_dashboard(self) -> Dict:
        """Generate SOC dashboard metrics"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        events_24h = [e for e in self.events if e.timestamp >= last_24h]
        alerts_24h = [a for a in self.alerts if a.triggered_at >= last_24h]

        event_types = {}
        for event in events_24h:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

        severity_counts = {s.name: 0 for s in EventSeverity}
        for alert in alerts_24h:
            severity_counts[alert.severity.name] += 1

        return {
            'dashboard_time': now.isoformat(),
            'events_last_24h': len(events_24h),
            'alerts_last_24h': len(alerts_24h),
            'event_types': event_types,
            'alert_severity_distribution': severity_counts,
            'critical_alerts': [
                {
                    'alert_id': a.alert_id,
                    'title': a.title,
                    'triggered_at': a.triggered_at.isoformat()
                }
                for a in alerts_24h
                if a.severity == EventSeverity.CRITICAL
            ]
        }


if __name__ == "__main__":
    siem = SIEMCorrelationEngine()

    # Simulate failed login attempts (brute force)
    for i in range(6):
        event = SecurityEvent(
            event_id=f"EVT-{i:04d}",
            timestamp=datetime.now(),
            source_ip="192.0.2.100",
            dest_ip="10.0.0.5",
            event_type="failed_login",
            severity=EventSeverity.MEDIUM,
            user="admin",
            description=f"Failed login attempt {i+1}",
            raw_log=f"Failed login for user admin from 192.0.2.100"
        )
        siem.ingest_event(event)

    # Generate dashboard
    dashboard = siem.generate_soc_dashboard()
    print(f"\nSOC Dashboard:")
    print(f"Events (24h): {dashboard['events_last_24h']}")
    print(f"Alerts (24h): {dashboard['alerts_last_24h']}")
    print(f"Critical alerts: {len(dashboard['critical_alerts'])}")
