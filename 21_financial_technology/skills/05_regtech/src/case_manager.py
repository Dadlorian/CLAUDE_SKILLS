"""Case Management System"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class CaseStatus(Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    SAR_FILED = "SAR_FILED"
    CLOSED = "CLOSED"

@dataclass
class ComplianceCase:
    case_id: str
    alert_id: str
    status: CaseStatus
    priority: str
    created_date: datetime
    sla_deadline: datetime
    assigned_to: str
    investigation_notes: list

class CaseManager:
    def __init__(self):
        self.cases = {}

    def create_case(self, alert_id: str, priority: str) -> ComplianceCase:
        """Create compliance investigation case"""
        case_id = f"CASE-{alert_id}"
        sla_days = 1 if priority == 'HIGH' else 3
        case = ComplianceCase(
            case_id=case_id,
            alert_id=alert_id,
            status=CaseStatus.NEW,
            priority=priority,
            created_date=datetime.utcnow(),
            sla_deadline=datetime.utcnow() + timedelta(days=sla_days),
            assigned_to="UNASSIGNED",
            investigation_notes=[]
        )
        self.cases[case_id] = case
        return case

    def add_investigation_note(self, case_id: str, note: str):
        """Add investigation finding"""
        if case_id in self.cases:
            self.cases[case_id].investigation_notes.append({
                'timestamp': datetime.utcnow().isoformat(),
                'note': note
            })

    def close_case(self, case_id: str, disposition: str):
        """Close case"""
        if case_id in self.cases:
            case = self.cases[case_id]
            case.status = CaseStatus.SAR_FILED if disposition == 'SAR' else CaseStatus.CLOSED
            return True
        return False

if __name__ == "__main__":
    manager = CaseManager()
    case = manager.create_case("ALT-001", "HIGH")
    print(f"Case Created: {case.case_id}, SLA: {case.sla_deadline}")
