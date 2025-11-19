"""Audit Trail and Logging System"""
from datetime import datetime
from typing import List, Dict

class AuditLogger:
    """Comprehensive audit logging"""
    
    def __init__(self):
        self.logs = []
    
    def log_event(self, event_type: str, user_id: str, action: str, resource_id: str, details: Dict = None) -> dict:
        """Log event to audit trail"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'resource_id': resource_id,
            'details': details or {}
        }
        self.logs.append(log_entry)
        return log_entry
    
    def get_audit_trail(self, resource_id: str) -> List[dict]:
        """Retrieve audit trail for resource"""
        return [log for log in self.logs if log['resource_id'] == resource_id]
    
    def get_user_activity(self, user_id: str) -> List[dict]:
        """Get user activity history"""
        return [log for log in self.logs if log['user_id'] == user_id]
