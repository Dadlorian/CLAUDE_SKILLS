"""Alert Generation and Prioritization System"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class AlertStatus(Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"

@dataclass
class ComplianceAlert:
    alert_id: str
    rule_id: str
    severity: int
    transaction_id: str
    customer_id: str
    status: AlertStatus
    created_timestamp: str

class AlertGenerator:
    """Generate and prioritize compliance alerts"""
    
    def generate_alert(self, rule_match: dict, severity: int) -> ComplianceAlert:
        """Generate alert from rule match"""
        return ComplianceAlert(
            alert_id=f"ALT-{rule_match.get('txn_id', 'UNKNOWN')}",
            rule_id=rule_match.get('rule_id'),
            severity=severity,
            transaction_id=rule_match.get('txn_id'),
            customer_id=rule_match.get('customer_id'),
            status=AlertStatus.OPEN,
            created_timestamp=datetime.utcnow().isoformat()
        )
    
    def prioritize_alerts(self, alerts: list) -> list:
        """Sort alerts by priority"""
        return sorted(alerts, key=lambda a: a.severity, reverse=True)
    
    def assign_alert(self, alert: ComplianceAlert, assignee: str) -> dict:
        """Assign alert to analyst"""
        alert.status = AlertStatus.ASSIGNED
        return {'alert_id': alert.alert_id, 'assigned_to': assignee, 'status': alert.status.value}
