"""
Fraud Alerts - Generate and manage fraud alerts
"""

from datetime import datetime
from typing import Dict, List
import uuid


class AlertGenerator:
    """Generate fraud alerts"""

    @staticmethod
    def create_alert(transaction: Dict, fraud_score: float) -> Dict:
        """Create fraud alert"""
        return {
            'alert_id': str(uuid.uuid4()),
            'transaction_id': transaction['id'],
            'fraud_score': fraud_score,
            'priority': AlertGenerator._calculate_priority(fraud_score),
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }

    @staticmethod
    def _calculate_priority(fraud_score: float) -> int:
        """Calculate alert priority (1=highest, 5=lowest)"""
        if fraud_score > 0.8:
            return 1
        elif fraud_score > 0.7:
            return 2
        elif fraud_score > 0.6:
            return 3
        else:
            return 4


class AlertQueue:
    """Manage fraud alert queue"""

    def __init__(self, storage):
        self.storage = storage
        self.queue_name = 'fraud_alerts'

    def add_alert(self, alert: Dict):
        """Add alert to queue"""
        self.storage.zadd(
            self.queue_name,
            {str(alert['alert_id']): -alert['priority']}  # Negative for reverse sort
        )

    def get_pending_alerts(self, limit: int = 10) -> List[Dict]:
        """Get pending alerts"""
        alert_ids = self.storage.zrange(self.queue_name, 0, limit - 1)
        return [self.storage.get(f'alert:{aid}') for aid in alert_ids]

    def mark_alert_processed(self, alert_id: str):
        """Mark alert as processed"""
        self.storage.zrem(self.queue_name, str(alert_id))
