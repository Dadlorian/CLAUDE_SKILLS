"""Policy renewal management"""
from datetime import datetime, timedelta
from typing import Dict, List

class RenewalManager:
    def get_policies_due_renewal(self, policies: List[Dict], days_ahead: int = 60) -> List[Dict]:
        """Get policies due for renewal"""
        due = []
        today = datetime.now()
        
        for policy in policies:
            expiration = datetime.fromisoformat(policy.get('expiration_date', ''))
            days_until_expiration = (expiration - today).days
            
            if 0 <= days_until_expiration <= days_ahead:
                due.append(policy)
        
        return due
    
    def create_renewal_notice(self, policy: Dict) -> Dict:
        """Create renewal notice"""
        return {
            "policy_id": policy.get('id'),
            "notice_type": "renewal",
            "current_premium": policy.get('premium'),
            "renewal_premium": round(policy.get('premium') * 1.03, 2),
            "renewal_date": policy.get('expiration_date'),
            "notice_sent": datetime.now().isoformat()
        }
