"""Compliance Rules Engine for Transaction Evaluation"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class RuleType(Enum):
    AMOUNT = "AMOUNT"
    GEOGRAPHIC = "GEOGRAPHIC"
    VELOCITY = "VELOCITY"
    BEHAVIORAL = "BEHAVIORAL"
    SANCTIONS = "SANCTIONS"

@dataclass
class ComplianceRule:
    rule_id: str
    rule_type: RuleType
    description: str
    condition: str
    severity: int  # 1-10

class ComplianceRulesEngine:
    """Rules-based compliance evaluation"""

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> List[ComplianceRule]:
        """Initialize compliance rules"""
        return [
            ComplianceRule(
                rule_id="MON-001",
                rule_type=RuleType.AMOUNT,
                description="Large transaction threshold",
                condition="amount > 100000",
                severity=7
            ),
            ComplianceRule(
                rule_id="MON-002",
                rule_type=RuleType.GEOGRAPHIC,
                description="High-risk country transfer",
                condition="country IN (IR, NK, SY, CU)",
                severity=9
            ),
            ComplianceRule(
                rule_id="MON-003",
                rule_type=RuleType.VELOCITY,
                description="Unusual transaction velocity",
                condition="frequency > baseline * 10",
                severity=6
            ),
            ComplianceRule(
                rule_id="MON-004",
                rule_type=RuleType.BEHAVIORAL,
                description="Transaction inconsistent with profile",
                condition="deviation > 5 standard deviations",
                severity=5
            )
        ]

    def evaluate_rules(self, transaction: Dict) -> List[Dict]:
        """Evaluate all rules against transaction"""
        triggered_rules = []

        # Rule MON-001: Large amount
        if transaction.get('amount', 0) > 100000:
            triggered_rules.append({
                'rule_id': 'MON-001',
                'rule': 'Large transaction',
                'severity': 7,
                'triggered': True,
                'details': f"Amount ${transaction['amount']} exceeds threshold"
            })

        # Rule MON-002: High-risk country
        high_risk_countries = ['IR', 'NK', 'SY', 'CU']
        if transaction.get('beneficiary_country') in high_risk_countries:
            triggered_rules.append({
                'rule_id': 'MON-002',
                'rule': 'High-risk country',
                'severity': 9,
                'triggered': True,
                'details': f"Destination country {transaction['beneficiary_country']} on high-risk list"
            })

        # Rule MON-003: Velocity anomaly
        if transaction.get('frequency_deviation', 0) > 5:
            triggered_rules.append({
                'rule_id': 'MON-003',
                'rule': 'Unusual velocity',
                'severity': 6,
                'triggered': True,
                'details': f"Transaction frequency {transaction['frequency_deviation']}x baseline"
            })

        # Rule MON-004: Profile deviation
        if transaction.get('profile_deviation', 0) > 5:
            triggered_rules.append({
                'rule_id': 'MON-004',
                'rule': 'Behavior mismatch',
                'severity': 5,
                'triggered': True,
                'details': "Transaction inconsistent with customer profile"
            })

        return triggered_rules

    def get_overall_severity(self, triggered_rules: List[Dict]) -> int:
        """Calculate overall alert severity"""
        if not triggered_rules:
            return 0
        return max(rule['severity'] for rule in triggered_rules)

    def list_rules(self) -> List[Dict]:
        """Get all available rules"""
        return [
            {
                'rule_id': rule.rule_id,
                'description': rule.description,
                'type': rule.rule_type.value,
                'severity': rule.severity
            }
            for rule in self.rules
        ]

# Example usage
if __name__ == "__main__":
    engine = ComplianceRulesEngine()

    transaction = {
        'amount': 500000,
        'beneficiary_country': 'IR',
        'frequency_deviation': 8,
        'profile_deviation': 2
    }

    triggered = engine.evaluate_rules(transaction)
    print(f"Triggered Rules: {len(triggered)}")
    for rule in triggered:
        print(f"  - {rule['rule']}: {rule['details']}")

    severity = engine.get_overall_severity(triggered)
    print(f"Overall Severity: {severity}/10")
