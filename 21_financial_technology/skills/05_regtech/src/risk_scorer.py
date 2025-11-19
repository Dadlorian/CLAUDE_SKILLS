"""Risk Scoring Engine"""
import json
from dataclasses import dataclass
from typing import Dict

@dataclass
class RiskScore:
    customer_id: str
    overall_score: float
    category: str
    components: Dict

class RiskScorer:
    def calculate_risk_score(self, customer: Dict) -> RiskScore:
        """Calculate comprehensive risk score"""
        scores = {}
        scores['customer_type'] = 20 if customer['type'] == 'business' else 15
        scores['geographic'] = {'US': 20, 'CN': 60, 'IR': 90}.get(customer['country'], 40)
        scores['industry'] = {'finance': 25, 'trading': 60, 'tech': 15}.get(customer['industry'], 35)
        scores['transaction'] = 30 if customer.get('high_value_txns') else 15
        scores['behavioral'] = 25 if customer.get('unusual_activity') else 10

        weights = {'customer_type': 0.25, 'geographic': 0.35, 'industry': 0.15, 'transaction': 0.15, 'behavioral': 0.10}
        overall = sum(scores[k] * weights[k] for k in scores)

        category = 'HIGH' if overall > 65 else 'MEDIUM' if overall > 40 else 'LOW'

        return RiskScore(
            customer_id=customer['id'],
            overall_score=overall,
            category=category,
            components=scores
        )

if __name__ == "__main__":
    scorer = RiskScorer()
    customer = {'id': 'CUST-001', 'type': 'business', 'country': 'CN', 'industry': 'trading', 'high_value_txns': True}
    result = scorer.calculate_risk_score(customer)
    print(f"Risk Score: {result.overall_score:.1f}, Category: {result.category}")
