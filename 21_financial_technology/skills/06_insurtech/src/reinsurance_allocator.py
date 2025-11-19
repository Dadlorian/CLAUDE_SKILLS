"""Reinsurance allocation and management"""
from typing import Dict

class ReinsuranceAllocator:
    def allocate_to_reinsurance(self, policy: Dict) -> Dict:
        """Allocate premium to reinsurance"""
        premium = policy.get('premium', 0)
        coverage_type = policy.get('product', 'auto')
        
        allocations = {'auto': 0.30, 'home': 0.25, 'health': 0.20}
        ceded_percentage = allocations.get(coverage_type, 0.25)
        
        return {
            "policy_id": policy.get('id'),
            "gross_premium": premium,
            "ceded_percentage": ceded_percentage,
            "ceded_premium": round(premium * ceded_percentage, 2),
            "net_premium": round(premium * (1 - ceded_percentage), 2)
        }
