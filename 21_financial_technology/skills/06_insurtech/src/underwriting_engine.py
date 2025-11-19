"""Underwriting automation engine with rules and scoring"""
from typing import Dict

class UnderwritingEngine:
    def __init__(self):
        self.rules = {}
    
    def calculate_score(self, applicant_data: Dict) -> int:
        """Calculate underwriting risk score"""
        score = 0
        
        # Age factor
        age = applicant_data.get('age', 0)
        if age < 25:
            score += 30
        elif age > 65:
            score += 15
        
        # Claims history
        claims = applicant_data.get('claims_count', 0)
        score += min(claims * 20, 50)
        
        # Good record discount
        if applicant_data.get('clean_record'):
            score = max(0, score - 20)
        
        return min(score, 100)
    
    def make_decision(self, applicant_data: Dict) -> Dict:
        """Make underwriting decision"""
        score = self.calculate_score(applicant_data)
        
        if score <= 30:
            decision = "approve"
            rate_adjustment = 0.9
        elif score <= 60:
            decision = "approve"
            rate_adjustment = 1.0
        elif score <= 80:
            decision = "approve_with_conditions"
            rate_adjustment = 1.2
        else:
            decision = "decline"
            rate_adjustment = 1.0
        
        return {
            "decision": decision,
            "score": score,
            "rate_adjustment": rate_adjustment
        }

if __name__ == "__main__":
    engine = UnderwritingEngine()
    result = engine.make_decision({'age': 35, 'claims_count': 1, 'clean_record': True})
    print(f"Decision: {result}")
