"""Policy document generation"""
from typing import Dict
from datetime import datetime

class PolicyDocumentGenerator:
    def generate_declarations(self, policy: Dict) -> Dict:
        """Generate declarations page"""
        return {
            "document_type": "declarations",
            "policy_id": policy.get('id'),
            "effective_date": policy.get('effective_date'),
            "premium": policy.get('premium'),
            "coverages": policy.get('coverages'),
            "generated_date": datetime.now().isoformat()
        }
    
    def generate_policy(self, policy: Dict) -> Dict:
        """Generate full policy document"""
        return {
            "document_type": "policy",
            "policy_id": policy.get('id'),
            "insuring_agreement": "Standard coverage",
            "exclusions": "See declarations page",
            "conditions": "Customer obligations",
            "generated_date": datetime.now().isoformat()
        }
