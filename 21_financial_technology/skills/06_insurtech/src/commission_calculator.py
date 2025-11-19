"""Commission calculation for agents/brokers"""
from typing import Dict

class CommissionCalculator:
    def calculate_commission(self, policy: Dict) -> Dict:
        """Calculate commission on premium"""
        premium = policy.get('premium', 0)
        product = policy.get('product', 'auto')
        
        rates = {'auto': 0.12, 'home': 0.15, 'health': 0.08}
        rate = rates.get(product, 0.10)
        
        commission = premium * rate
        
        return {
            "policy_id": policy.get('id'),
            "premium": premium,
            "commission_rate": rate,
            "commission_amount": round(commission, 2)
        }
