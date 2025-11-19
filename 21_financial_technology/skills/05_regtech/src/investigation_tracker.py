"""Investigation Case Tracking System"""
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class InvestigationCase:
    case_id: str
    alert_id: str
    status: str
    start_time: str
    last_updated: str
    notes: List[str]

class InvestigationTracker:
    """Track investigation cases"""
    
    def __init__(self):
        self.investigations = {}
    
    def start_investigation(self, alert_id: str) -> InvestigationCase:
        """Start investigation"""
        case_id = f"CASE-{alert_id}"
        case = InvestigationCase(
            case_id=case_id,
            alert_id=alert_id,
            status='IN_PROGRESS',
            start_time=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat(),
            notes=[]
        )
        self.investigations[case_id] = case
        return case
    
    def add_note(self, case_id: str, note: str):
        """Add investigation note"""
        if case_id in self.investigations:
            self.investigations[case_id].notes.append(note)
            self.investigations[case_id].last_updated = datetime.utcnow().isoformat()
    
    def close_investigation(self, case_id: str, disposition: str) -> dict:
        """Close investigation"""
        if case_id in self.investigations:
            case = self.investigations[case_id]
            case.status = 'CLOSED'
            return {'case_id': case_id, 'disposition': disposition, 'status': case.status}
        return None
