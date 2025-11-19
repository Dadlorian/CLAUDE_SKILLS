"""
Fraud Dashboard - Dashboard metrics and reporting
"""

from typing import Dict
from collections import defaultdict
from datetime import datetime, timedelta


class FraudDashboard:
    """Fraud metrics dashboard"""

    def __init__(self, storage):
        self.storage = storage

    def get_daily_metrics(self) -> Dict:
        """Get daily fraud metrics"""
        today = datetime.now().date()

        metrics = self.storage.get(f'daily_metrics:{today}')

        return metrics or {
            'date': today.isoformat(),
            'transactions': 0,
            'fraud_detected': 0,
            'fraud_rate': 0.0
        }

    def update_metrics(self, is_fraud: bool):
        """Update dashboard metrics"""
        today = datetime.now().date()
        key = f'daily_metrics:{today}'

        metrics = self.storage.get(key) or {
            'date': today.isoformat(),
            'transactions': 0,
            'fraud_detected': 0
        }

        metrics['transactions'] += 1

        if is_fraud:
            metrics['fraud_detected'] += 1

        metrics['fraud_rate'] = metrics['fraud_detected'] / max(metrics['transactions'], 1)

        self.storage.set(key, metrics)

    def get_weekly_summary(self) -> Dict:
        """Get weekly summary"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        total_transactions = 0
        total_fraud = 0

        for i in range(7):
            date = week_start + timedelta(days=i)
            metrics = self.storage.get(f'daily_metrics:{date}')

            if metrics:
                total_transactions += metrics['transactions']
                total_fraud += metrics['fraud_detected']

        return {
            'week_start': week_start.isoformat(),
            'total_transactions': total_transactions,
            'total_fraud': total_fraud,
            'fraud_rate': total_fraud / max(total_transactions, 1)
        }
