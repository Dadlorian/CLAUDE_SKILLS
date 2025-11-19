"""
Transaction Monitor - Real-time transaction monitoring
"""

from datetime import datetime
from typing import Dict, Callable


class TransactionMonitor:
    """Monitor transactions in real-time"""

    def __init__(self, fraud_scorer: Callable, alert_handler: Callable):
        self.fraud_scorer = fraud_scorer
        self.alert_handler = alert_handler
        self.transaction_count = 0
        self.fraud_detected = 0

    def process_transaction(self, transaction: Dict) -> Dict:
        """Process single transaction"""
        self.transaction_count += 1

        # Score transaction
        result = self.fraud_scorer(transaction)

        # Generate alert if needed
        if result['action'] != 'allow':
            self.fraud_detected += 1
            self.alert_handler(result)

        return result

    def get_metrics(self) -> Dict:
        """Get monitoring metrics"""
        return {
            'total_transactions': self.transaction_count,
            'fraud_detected': self.fraud_detected,
            'fraud_rate': self.fraud_detected / max(self.transaction_count, 1)
        }
