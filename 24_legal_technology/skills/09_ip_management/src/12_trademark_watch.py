"""
Trademark Monitoring System Example
Monitors trademark applications and registrations for competitors
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TrademarkRecord:
    """Trademark application/registration data"""
    trademark_id: str
    mark_text: str
    serial_number: str
    filing_date: datetime
    registration_date: Optional[datetime]
    status: str
    owner: str
    classes: List[int]
    goods_services: List[str]
    jurisdiction: str
    similarity_score: Optional[float] = None


@dataclass
class MonitoringAlert:
    """Alert for trademark monitoring"""
    alert_id: str
    severity: AlertSeverity
    trademark_id: str
    reason: str
    detected_date: datetime
    related_trademark: Optional[str] = None
    action_required: str = ""
    priority: int = 0


class TrademarkMonitoringSystem:
    """Monitor and analyze trademark filings"""

    def __init__(self, watch_terms: List[str]):
        self.watch_terms = watch_terms
        self.trademarks: List[TrademarkRecord] = []
        self.alerts: List[MonitoringAlert] = []
        self.alert_counter = 0

    def add_trademark(self, trademark: TrademarkRecord):
        """Add trademark to monitoring system"""
        self.trademarks.append(trademark)

    def monitor_new_filings(self, new_marks: List[TrademarkRecord]) -> List[MonitoringAlert]:
        """
        Monitor for new trademark filings matching watch terms

        Args:
            new_marks: List of newly filed trademarks

        Returns:
            List of alerts for matching trademarks
        """
        new_alerts = []

        for mark in new_marks:
            mark_lower = mark.mark_text.lower()

            for watch_term in self.watch_terms:
                watch_lower = watch_term.lower()

                # Check for exact match
                if watch_lower in mark_lower or mark_lower in watch_lower:
                    alert = MonitoringAlert(
                        alert_id=f"ALERT_{self.alert_counter}",
                        severity=AlertSeverity.CRITICAL if watch_lower == mark_lower else AlertSeverity.HIGH,
                        trademark_id=mark.trademark_id,
                        reason=f"Potential brand conflict with '{watch_term}'",
                        detected_date=datetime.now(),
                        action_required="Review for opposition",
                        priority=1 if watch_lower == mark_lower else 2
                    )
                    self.alert_counter += 1
                    new_alerts.append(alert)
                    self.alerts.append(alert)

        return new_alerts

    def analyze_class_conflicts(self) -> Dict:
        """
        Analyze potential conflicts based on trademark classes

        Returns:
            Dictionary with class-based conflict analysis
        """
        class_distribution = defaultdict(list)
        conflicts = defaultdict(list)

        for trademark in self.trademarks:
            for cls in trademark.classes:
                class_distribution[cls].append(trademark)

        # Find potential conflicts (same class, similar marks)
        for cls, marks in class_distribution.items():
            if len(marks) > 1:
                for i, mark1 in enumerate(marks):
                    for mark2 in marks[i+1:]:
                        similarity = self._calculate_similarity(
                            mark1.mark_text,
                            mark2.mark_text
                        )
                        if similarity > 0.7:
                            conflicts[cls].append({
                                'mark1': mark1.mark_text,
                                'mark2': mark2.mark_text,
                                'owner1': mark1.owner,
                                'owner2': mark2.owner,
                                'similarity': similarity
                            })

        return {
            'total_classes_monitored': len(class_distribution),
            'potential_conflicts': dict(conflicts),
            'conflict_count': sum(len(v) for v in conflicts.values())
        }

    def track_prosecution_timeline(self) -> Dict:
        """
        Track prosecution timeline for monitored trademarks

        Returns:
            Dictionary with prosecution metrics
        """
        prosecution_data = {
            'pending': [],
            'registered': [],
            'abandoned': [],
            'avg_prosecution_time': 0
        }

        prosecution_times = []

        for trademark in self.trademarks:
            if trademark.status.lower() == 'registered' and trademark.registration_date:
                time_to_register = (trademark.registration_date - trademark.filing_date).days
                prosecution_times.append(time_to_register)
                prosecution_data['registered'].append({
                    'mark': trademark.mark_text,
                    'owner': trademark.owner,
                    'prosecution_days': time_to_register
                })
            elif trademark.status.lower() == 'pending':
                days_pending = (datetime.now() - trademark.filing_date).days
                prosecution_data['pending'].append({
                    'mark': trademark.mark_text,
                    'owner': trademark.owner,
                    'days_pending': days_pending
                })

        if prosecution_times:
            prosecution_data['avg_prosecution_time'] = sum(prosecution_times) / len(prosecution_times)

        return prosecution_data

    def identify_renewal_deadlines(self, months_ahead: int = 12) -> List[Dict]:
        """
        Identify trademark renewal deadlines

        Args:
            months_ahead: Number of months to look ahead

        Returns:
            List of renewal reminders
        """
        renewal_reminders = []
        cutoff_date = datetime.now() + timedelta(days=months_ahead * 30)

        for trademark in self.trademarks:
            if trademark.registration_date:
                # Typical renewal is at 10 years
                renewal_date = trademark.registration_date + timedelta(days=365*10)

                if datetime.now() < renewal_date < cutoff_date:
                    days_until_renewal = (renewal_date - datetime.now()).days
                    renewal_reminders.append({
                        'mark': trademark.mark_text,
                        'owner': trademark.owner,
                        'renewal_date': renewal_date.isoformat(),
                        'days_remaining': days_until_renewal,
                        'urgency': 'critical' if days_until_renewal < 90 else 'high' if days_until_renewal < 180 else 'normal'
                    })

        return sorted(renewal_reminders, key=lambda x: x['days_remaining'])

    def generate_monitoring_report(self) -> Dict:
        """
        Generate comprehensive monitoring report

        Returns:
            Complete monitoring analysis
        """
        return {
            'watch_terms': self.watch_terms,
            'total_marks_monitored': len(self.trademarks),
            'total_alerts': len(self.alerts),
            'critical_alerts': sum(1 for a in self.alerts if a.severity == AlertSeverity.CRITICAL),
            'high_alerts': sum(1 for a in self.alerts if a.severity == AlertSeverity.HIGH),
            'class_analysis': self.analyze_class_conflicts(),
            'prosecution_timeline': self.track_prosecution_timeline(),
            'renewal_deadlines': self.identify_renewal_deadlines(),
            'report_date': datetime.now().isoformat()
        }

    @staticmethod
    def _calculate_similarity(mark1: str, mark2: str) -> float:
        """Calculate similarity between two marks (0-1)"""
        m1_lower = mark1.lower()
        m2_lower = mark2.lower()

        if m1_lower == m2_lower:
            return 1.0

        # Simple Levenshtein-like approach
        matches = sum(1 for i, c in enumerate(m1_lower) if i < len(m2_lower) and c == m2_lower[i])
        max_len = max(len(m1_lower), len(m2_lower))

        return matches / max_len if max_len > 0 else 0


# Example usage
if __name__ == "__main__":
    monitor = TrademarkMonitoringSystem(
        watch_terms=['TechVision', 'DataFlow', 'CloudSync']
    )

    # Add sample trademarks
    for i in range(10):
        tm = TrademarkRecord(
            trademark_id=f"TM{1000000 + i}",
            mark_text=f"Brand{i}",
            serial_number=f"SN{90000000 + i}",
            filing_date=datetime.now() - timedelta(days=i*30),
            registration_date=datetime.now() - timedelta(days=i*30) if i < 5 else None,
            status="registered" if i < 5 else "pending",
            owner=f"Company {i % 3}",
            classes=[25 + (i % 10), 42],
            goods_services=["Software", "IT Services"],
            jurisdiction="US"
        )
        monitor.add_trademark(tm)

    report = monitor.generate_monitoring_report()
    print("Trademark Monitoring Report")
    print(f"Marks Monitored: {report['total_marks_monitored']}")
    print(f"Total Alerts: {report['total_alerts']}")
    print(f"Class Conflicts: {report['class_analysis']['conflict_count']}")
    print(f"Renewal Reminders: {len(report['renewal_deadlines'])}")
