"""
Drug Allergy Cross-Reactivity Checker
Checks for drug allergies and cross-reactivity patterns
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ReactionType(Enum):
    IGE_MEDIATED = "IGE"  # Anaphylaxis, urticaria
    NON_IGE = "NON_IGE"   # Rash, GI upset
    UNKNOWN = "UNKNOWN"

class Severity(Enum):
    SEVERE = "SEVERE"      # Anaphylaxis, SJS/TEN
    MODERATE = "MODERATE"  # Angioedema, severe rash
    MILD = "MILD"          # Rash, GI upset

@dataclass
class Allergy:
    drug_rxcui: str
    drug_name: str
    reaction: str
    reaction_type: ReactionType
    severity: Severity
    onset_date: datetime
    verified: bool = False

@dataclass
class CrossReactivity:
    allergen_class: str
    medication_class: str
    risk_percentage: float
    description: str
    recommendation: str

class AllergyChecker:
    def __init__(self):
        self.cross_reactivity_rules = self._load_cross_reactivity_rules()
    
    def _load_cross_reactivity_rules(self) -> Dict[str, List[CrossReactivity]]:
        """Load cross-reactivity database"""
        return {
            'penicillin': [
                CrossReactivity(
                    allergen_class='penicillin',
                    medication_class='cephalosporin',
                    risk_percentage=2.0,
                    description='1-2% cross-reactivity based on side chain similarity',
                    recommendation='Use with caution if history of mild rash. Avoid if anaphylaxis.'
                ),
                CrossReactivity(
                    allergen_class='penicillin',
                    medication_class='carbapenem',
                    risk_percentage=1.0,
                    description='~1% cross-reactivity, generally safe',
                    recommendation='Safe to use if no history of anaphylaxis'
                ),
                CrossReactivity(
                    allergen_class='penicillin',
                    medication_class='aztreonam',
                    risk_percentage=0.1,
                    description='No significant cross-reactivity',
                    recommendation='Safe to use'
                )
            ],
            'sulfa_antibiotic': [
                CrossReactivity(
                    allergen_class='sulfa_antibiotic',
                    medication_class='sulfa_nonantibiotic',
                    risk_percentage=0.0,
                    description='Different chemical structures, no cross-reactivity',
                    recommendation='Safe to use sulfonamide diuretics, sulfonylureas'
                )
            ]
        }
    
    def check_allergy(
        self,
        patient_allergies: List[Allergy],
        medication_rxcui: str,
        medication_name: str
    ) -> Optional[Dict]:
        """Check if medication conflicts with patient allergies"""
        
        for allergy in patient_allergies:
            # Exact match
            if allergy.drug_rxcui == medication_rxcui:
                return {
                    'match_type': 'EXACT',
                    'severity': 'CRITICAL',
                    'action': 'BLOCK' if allergy.severity == Severity.SEVERE else 'WARN',
                    'allergy': allergy,
                    'message': f"Patient allergic to {allergy.drug_name}",
                    'reaction': allergy.reaction,
                    'date': allergy.onset_date.strftime('%Y-%m-%d')
                }
            
            # Check cross-reactivity
            cross_react = self._check_cross_reactivity(allergy, medication_rxcui)
            if cross_react:
                return {
                    'match_type': 'CROSS_REACTIVITY',
                    'severity': 'WARNING',
                    'action': 'WARN',
                    'allergy': allergy,
                    'cross_reactivity': cross_react,
                    'message': f"Possible cross-reactivity with {allergy.drug_name}",
                    'risk': cross_react.risk_percentage
                }
        
        return None
    
    def _check_cross_reactivity(
        self,
        allergy: Allergy,
        medication_rxcui: str
    ) -> Optional[CrossReactivity]:
        """Check for cross-reactivity patterns"""
        
        allergen_class = self._get_drug_class(allergy.drug_rxcui)
        medication_class = self._get_drug_class(medication_rxcui)
        
        if allergen_class in self.cross_reactivity_rules:
            for rule in self.cross_reactivity_rules[allergen_class]:
                if rule.medication_class == medication_class:
                    # Only alert if risk > 1%
                    if rule.risk_percentage > 1.0:
                        return rule
        
        return None
    
    def _get_drug_class(self, rxcui: str) -> str:
        """Map RxCUI to drug class (simplified)"""
        class_mapping = {
            '7984': 'penicillin',
            '1596450': 'cephalosporin',
            '23796': 'carbapenem'
        }
        return class_mapping.get(rxcui, 'unknown')


# Example usage
if __name__ == "__main__":
    checker = AllergyChecker()
    
    patient_allergies = [
        Allergy(
            drug_rxcui='7984',
            drug_name='Penicillin',
            reaction='Anaphylaxis',
            reaction_type=ReactionType.IGE_MEDIATED,
            severity=Severity.SEVERE,
            onset_date=datetime(2019, 5, 15),
            verified=True
        )
    ]
    
    # Check cephalosporin (cross-reactivity)
    result = checker.check_allergy(patient_allergies, '1596450', 'Ceftriaxone')
    
    if result:
        print(f"\nAllergy Alert: {result['message']}")
        print(f"Severity: {result['severity']}")
        print(f"Action: {result['action']}")
        if 'cross_reactivity' in result:
            cr = result['cross_reactivity']
            print(f"Cross-reactivity risk: {cr.risk_percentage}%")
            print(f"Recommendation: {cr.recommendation}")
