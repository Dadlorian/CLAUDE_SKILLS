"""Policy search and lookup"""
from typing import Dict, List

class PolicySearch:
    def __init__(self):
        self.policies = {}
    
    def search_by_number(self, policy_number: str) -> Dict:
        """Search by policy number"""
        return self.policies.get(policy_number, {"found": False})
    
    def search_by_customer(self, email: str) -> List[Dict]:
        """Search by customer email"""
        return [p for p in self.policies.values() if p.get('email') == email]
    
    def search_by_product(self, product: str) -> List[Dict]:
        """Search by product type"""
        return [p for p in self.policies.values() if p.get('product') == product]
    
    def search_by_status(self, status: str) -> List[Dict]:
        """Search by policy status"""
        return [p for p in self.policies.values() if p.get('status') == status]
