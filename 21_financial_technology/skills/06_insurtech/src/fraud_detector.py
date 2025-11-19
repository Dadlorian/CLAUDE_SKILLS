"""Fraud detection algorithms"""
from typing import Dict

class FraudDetector:
    def calculate_fraud_score(self, claim: Dict) -> int:
        """Calculate fraud risk score (0-100)"""
        score = 0
        
        # High claim amount soon after policy
        if claim.get('days_since_policy', 365) < 30:
            score += 20
        
        # Multiple claims
        if claim.get('prior_claims', 0) > 3:
            score += 20
        
        # Missing documentation
        if len(claim.get('documents', [])) < 2:
            score += 15
        
        # Unusual loss type
        if claim.get('loss_type') in ['arson', 'staged_accident']:
            score += 30
        
        # High claim amount
        if claim.get('amount', 0) > 20000:
            score += 10
        
        return min(score, 100)
    
    def detect_fraud(self, claim: Dict) -> Dict:
        """Detect if claim is likely fraudulent"""
        score = self.calculate_fraud_score(claim)
        
        return {
            "claim_id": claim.get('id'),
            "fraud_score": score,
            "risk_level": "high" if score >= 70 else "medium" if score >= 40 else "low",
            "flagged": score >= 60
        }

if __name__ == "__main__":
    detector = FraudDetector()
    claim = {'id': 'CLM123', 'days_since_policy': 10, 'amount': 25000}
    result = detector.detect_fraud(claim)
    print(f"Fraud Detection: {result}")
