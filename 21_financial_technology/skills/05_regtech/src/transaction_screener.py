"""Transaction Screening Module"""
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TransactionAlert:
    transaction_id: str
    alert_reason: str
    severity: str

class TransactionScreener:
    def screen_transaction(self, txn: dict) -> TransactionAlert:
        """Screen transaction against rules"""
        alert_reason = []
        if txn['amount'] > 100000:
            alert_reason.append("Large amount")
        if txn.get('country') in ['IR', 'NK', 'SY']:
            alert_reason.append("High-risk country")
        
        severity = 'HIGH' if len(alert_reason) >= 2 else 'MEDIUM' if alert_reason else 'LOW'
        
        return TransactionAlert(
            transaction_id=txn['id'],
            alert_reason=' | '.join(alert_reason) if alert_reason else 'PASSED',
            severity=severity
        )

if __name__ == "__main__":
    screener = TransactionScreener()
    txn = {'id': 'TXN-001', 'amount': 500000, 'country': 'IR'}
    alert = screener.screen_transaction(txn)
    print(f"Alert: {alert.alert_reason}, Severity: {alert.severity}")
