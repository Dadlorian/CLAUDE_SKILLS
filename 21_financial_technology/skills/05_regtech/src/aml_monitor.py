"""
AML Monitor - Transaction Monitoring and Alert Generation
Real-time suspicious activity detection
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class AlertSeverity(Enum):
    LOW = 1
    MEDIUM = 3
    HIGH = 7
    CRITICAL = 10

class AlertType(Enum):
    LARGE_AMOUNT = "LARGE_AMOUNT"
    STRUCTURING = "STRUCTURING"
    GEOGRAPHIC_RISK = "GEOGRAPHIC_RISK"
    VELOCITY = "VELOCITY"
    UNUSUAL_PATTERN = "UNUSUAL_PATTERN"
    HIGH_RISK_BENEFICIARY = "HIGH_RISK_BENEFICIARY"

@dataclass
class Transaction:
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    transaction_type: str
    beneficiary_country: str
    timestamp: str
    is_cash: bool = False

@dataclass
class CustomerBaseline:
    customer_id: str
    avg_transaction_amount: float
    avg_monthly_volume: int
    typical_countries: List[str]
    typical_transaction_types: List[str]

@dataclass
class Alert:
    alert_id: str
    transaction_id: str
    customer_id: str
    alert_type: AlertType
    severity: AlertSeverity
    score: float
    description: str
    requires_investigation: bool
    created_timestamp: str

class AMLMonitor:
    """Transaction monitoring system"""

    def __init__(self):
        self.high_risk_countries = ['IR', 'NK', 'SY', 'CU']
        self.alerts = []

    def monitor_transaction(self, transaction: Transaction, baseline: CustomerBaseline) -> Optional[Alert]:
        """
        Monitor single transaction for suspicious activity
        Returns alert if suspicious
        """
        score = 0
        alert_reason = []

        # Check 1: Large amount detection
        if transaction.amount > baseline.avg_transaction_amount * 5:
            score += 3
            alert_reason.append(f"Amount {transaction.amount} is 5x baseline")

        # Check 2: Structuring detection (multiple transactions just under threshold)
        # This would check aggregated daily transactions in real implementation
        if transaction.amount > 9000 and transaction.amount < 10000:
            score += 2
            alert_reason.append("Transaction just below $10K threshold")

        # Check 3: Geographic risk
        if transaction.beneficiary_country in self.high_risk_countries:
            score += 4
            alert_reason.append(f"High-risk country: {transaction.beneficiary_country}")
        elif transaction.beneficiary_country not in baseline.typical_countries:
            score += 2
            alert_reason.append(f"Unusual country: {transaction.beneficiary_country}")

        # Check 4: Transaction type unusual
        if transaction.transaction_type not in baseline.typical_transaction_types:
            score += 1
            alert_reason.append(f"Unusual transaction type: {transaction.transaction_type}")

        # Check 5: Cash transaction
        if transaction.is_cash:
            score += 2
            alert_reason.append("Cash transaction")

        # Determine if alert needed
        if score >= 5:
            severity = self._score_to_severity(score)
            alert = Alert(
                alert_id=f"ALT-{transaction.transaction_id}",
                transaction_id=transaction.transaction_id,
                customer_id=transaction.customer_id,
                alert_type=self._determine_alert_type(alert_reason),
                severity=severity,
                score=score,
                description=" | ".join(alert_reason),
                requires_investigation=(severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]),
                created_timestamp=datetime.utcnow().isoformat()
            )
            self.alerts.append(alert)
            return alert

        return None

    def detect_structuring_pattern(self, transactions: List[Transaction]) -> Optional[Dict]:
        """
        Detect structuring pattern (multiple transactions below reporting threshold)
        """
        total_amount = sum(t.amount for t in transactions)
        transaction_count = len(transactions)

        # Check for structuring indicators
        small_transactions = [t for t in transactions if t.amount < 5000]
        if (len(small_transactions) >= 3 and
            total_amount > 10000 and
            all(t.is_cash for t in small_transactions)):

            return {
                'pattern': 'STRUCTURING_DETECTED',
                'transaction_count': transaction_count,
                'total_amount': total_amount,
                'small_transaction_count': len(small_transactions),
                'severity': AlertSeverity.HIGH.name,
                'recommendation': 'FILE_SAR'
            }

        return None

    def analyze_customer_behavior(self, customer_id: str, transactions: List[Transaction]) -> Dict:
        """
        Analyze customer transaction behavior and identify anomalies
        """
        if not transactions:
            return {}

        amounts = [t.amount for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        max_amount = max(amounts)
        min_amount = min(amounts)

        # Calculate standard deviation (simplified)
        variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5

        # Identify outliers (> 2 standard deviations)
        outliers = [t for t in transactions if abs(t.amount - avg_amount) > 2 * std_dev]

        return {
            'customer_id': customer_id,
            'transaction_count': len(transactions),
            'average_amount': avg_amount,
            'max_amount': max_amount,
            'min_amount': min_amount,
            'std_deviation': std_dev,
            'outlier_count': len(outliers),
            'outlier_percentage': (len(outliers) / len(transactions) * 100) if transactions else 0,
            'behavior_score': len(outliers) / max(len(transactions), 1) * 100
        }

    def calculate_transaction_risk_score(self, transaction: Transaction) -> float:
        """
        Calculate comprehensive risk score for transaction
        Scale: 0-100
        """
        risk_score = 0

        # Amount risk (0-30 points)
        if transaction.amount > 100000:
            risk_score += 30
        elif transaction.amount > 50000:
            risk_score += 20
        elif transaction.amount > 10000:
            risk_score += 10

        # Geographic risk (0-30 points)
        if transaction.beneficiary_country in self.high_risk_countries:
            risk_score += 30
        elif transaction.beneficiary_country in ['CN', 'RU', 'TR']:
            risk_score += 15
        else:
            risk_score += 5

        # Transaction type risk (0-20 points)
        if transaction.transaction_type == 'wire_transfer':
            risk_score += 15
        elif transaction.transaction_type == 'cash':
            risk_score += 20

        # Velocity risk (0-20 points)
        # Would require additional context in real implementation
        risk_score += 5

        return min(risk_score, 100)

    def _score_to_severity(self, score: float) -> AlertSeverity:
        """Convert numeric score to severity level"""
        if score >= 8:
            return AlertSeverity.CRITICAL
        elif score >= 6:
            return AlertSeverity.HIGH
        elif score >= 4:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

    def _determine_alert_type(self, reasons: List[str]) -> AlertType:
        """Determine alert type from reasons"""
        if any('threshold' in r for r in reasons):
            return AlertType.STRUCTURING
        elif any('country' in r for r in reasons):
            return AlertType.GEOGRAPHIC_RISK
        elif any('Amount' in r for r in reasons):
            return AlertType.LARGE_AMOUNT
        else:
            return AlertType.UNUSUAL_PATTERN

# Example usage
if __name__ == "__main__":
    monitor = AMLMonitor()

    # Customer baseline
    baseline = CustomerBaseline(
        customer_id="CUST-001",
        avg_transaction_amount=5000,
        avg_monthly_volume=10,
        typical_countries=['US', 'CA', 'UK'],
        typical_transaction_types=['wire_transfer', 'ach']
    )

    # Sample transactions
    transactions = [
        Transaction(
            transaction_id="TXN-001",
            customer_id="CUST-001",
            amount=500000,
            currency="USD",
            transaction_type="wire_transfer",
            beneficiary_country="IR",
            timestamp=datetime.utcnow().isoformat()
        ),
        Transaction(
            transaction_id="TXN-002",
            customer_id="CUST-001",
            amount=25000,
            currency="USD",
            transaction_type="wire_transfer",
            beneficiary_country="SY",
            timestamp=datetime.utcnow().isoformat()
        )
    ]

    # Monitor transactions
    for txn in transactions:
        alert = monitor.monitor_transaction(txn, baseline)
        if alert:
            print("ALERT GENERATED:", json.dumps(asdict(alert), indent=2))

    # Analyze behavior
    behavior = monitor.analyze_customer_behavior("CUST-001", transactions)
    print("\nBehavior Analysis:", json.dumps(behavior, indent=2))

    # Calculate risk scores
    for txn in transactions:
        risk_score = monitor.calculate_transaction_risk_score(txn)
        print(f"\nTransaction {txn.transaction_id} Risk Score: {risk_score:.1f}")
