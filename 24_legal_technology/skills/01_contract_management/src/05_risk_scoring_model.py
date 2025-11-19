"""
Risk Scoring Model - Score contracts based on multiple risk factors
Uses gradient boosting for risk assessment
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import json

class RiskScoringModel:
    """Score contracts based on risk factors"""
    
    RISK_FACTORS = {
        'unlimited_liability': {'weight': 0.25, 'max_risk': 5},
        'unilateral_termination': {'weight': 0.20, 'max_risk': 5},
        'payment_terms_risk': {'weight': 0.15, 'max_risk': 4},
        'price_escalation': {'weight': 0.12, 'max_risk': 4},
        'insurance_gaps': {'weight': 0.10, 'max_risk': 4},
        'compliance_issues': {'weight': 0.10, 'max_risk': 5},
        'ip_risk': {'weight': 0.08, 'max_risk': 4},
    }
    
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def assess_unlimited_liability(self, text: str) -> float:
        """Check for unlimited liability clauses"""
        risk_keywords = [
            'unlimited liability',
            'indemnify',
            'hold harmless',
            'consequential damages'
        ]
        
        found_count = sum(1 for kw in risk_keywords if kw.lower() in text.lower())
        return min(found_count / 2, 1.0) * 5  # Scale to 0-5
    
    def assess_termination_rights(self, text: str) -> float:
        """Check for unilateral termination rights"""
        unilateral_patterns = [
            'may terminate without cause',
            'either party may terminate',
            'termination at will'
        ]
        
        found_count = sum(1 for p in unilateral_patterns if p.lower() in text.lower())
        return min(found_count / 1.5, 1.0) * 5
    
    def assess_payment_risk(self, days_net: int = 30) -> float:
        """Assess payment terms risk"""
        if days_net <= 15:
            return 5
        elif days_net <= 30:
            return 3
        elif days_net <= 60:
            return 2
        else:
            return 1
    
    def assess_price_escalation(self, escalation_rate: float = 0) -> float:
        """Assess price escalation risk"""
        if escalation_rate > 0.05:  # >5% annual
            return 4
        elif escalation_rate > 0.03:
            return 3
        elif escalation_rate > 0.01:
            return 2
        else:
            return 1
    
    def assess_insurance_gaps(self, required_coverage: dict) -> float:
        """Check for adequate insurance requirements"""
        required_types = ['general_liability', 'professional_liability', 'cyber_liability']
        covered_types = sum(1 for t in required_types if required_coverage.get(t, False))
        
        coverage_percentage = covered_types / len(required_types)
        return (1 - coverage_percentage) * 4
    
    def calculate_overall_risk(self, contract_data: dict) -> dict:
        """Calculate overall risk score"""
        risk_scores = {
            'unlimited_liability': self.assess_unlimited_liability(contract_data.get('text', '')),
            'unilateral_termination': self.assess_termination_rights(contract_data.get('text', '')),
            'payment_terms_risk': self.assess_payment_risk(contract_data.get('payment_days', 30)),
            'price_escalation': self.assess_price_escalation(contract_data.get('escalation_rate', 0)),
            'insurance_gaps': self.assess_insurance_gaps(contract_data.get('insurance', {})),
            'compliance_issues': contract_data.get('compliance_risk', 1) * 5,
            'ip_risk': contract_data.get('ip_risk', 1) * 4,
        }
        
        # Calculate weighted overall score
        weighted_sum = sum(
            risk_scores[factor] * self.RISK_FACTORS[factor]['weight']
            for factor in self.RISK_FACTORS
        )
        
        overall_score = weighted_sum / sum(
            self.RISK_FACTORS[f]['weight'] for f in self.RISK_FACTORS
        )
        
        # Determine risk level
        if overall_score < 2:
            risk_level = 'LOW'
            color = 'GREEN'
        elif overall_score < 3:
            risk_level = 'MODERATE'
            color = 'YELLOW'
        elif overall_score < 4:
            risk_level = 'HIGH'
            color = 'ORANGE'
        else:
            risk_level = 'CRITICAL'
            color = 'RED'
        
        return {
            'overall_score': round(overall_score, 2),
            'risk_level': risk_level,
            'color': color,
            'risk_factors': risk_scores,
            'top_risks': sorted(
                risk_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }


# Example usage
if __name__ == "__main__":
    scorer = RiskScoringModel()
    
    contract_data = {
        'text': 'This contract includes unlimited liability and indemnification clauses...',
        'payment_days': 45,
        'escalation_rate': 0.03,
        'insurance': {'general_liability': True, 'professional_liability': False},
        'compliance_risk': 0.2,
        'ip_risk': 0.3
    }
    
    risk_assessment = scorer.calculate_overall_risk(contract_data)
    print(json.dumps(risk_assessment, indent=2))
