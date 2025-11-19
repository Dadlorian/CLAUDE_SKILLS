"""Drug-Disease Contraindication Checker"""
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Contraindication:
    drug_class: str
    condition: str
    severity: str  # ABSOLUTE, RELATIVE
    rationale: str
    alternatives: List[str]

class ContraindicationChecker:
    def __init__(self):
        self.contraindications = self._load_contraindications()
    
    def _load_contraindications(self) -> List[Contraindication]:
        return [
            Contraindication(
                drug_class='NSAID',
                condition='CKD_STAGE_4_5',
                severity='ABSOLUTE',
                rationale='Risk of acute kidney injury and progression of CKD',
                alternatives=['Acetaminophen', 'Opioids for severe pain']
            ),
            Contraindication(
                drug_class='NSAID',
                condition='ACTIVE_GI_BLEED',
                severity='ABSOLUTE',
                rationale='Increased bleeding risk',
                alternatives=['Acetaminophen']
            ),
            Contraindication(
                drug_class='BETA_BLOCKER',
                condition='ASTHMA_SEVERE',
                severity='RELATIVE',
                rationale='Risk of bronchospasm',
                alternatives=['Calcium channel blockers', 'Cardioselective beta-blockers with caution']
            ),
            Contraindication(
                drug_class='ACE_INHIBITOR',
                condition='PREGNANCY',
                severity='ABSOLUTE',
                rationale='Teratogenic - causes renal dysplasia, oligohydramnios',
                alternatives=['Labetalol', 'Nifedipine', 'Methyldopa']
            )
        ]
    
    def check(self, drug_class: str, patient_conditions: List[str]) -> List[Dict]:
        """Check for drug-disease contraindications"""
        warnings = []
        
        for contraindication in self.contraindications:
            if contraindication.drug_class == drug_class:
                if contraindication.condition in patient_conditions:
                    warnings.append({
                        'severity': contraindication.severity,
                        'condition': contraindication.condition,
                        'rationale': contraindication.rationale,
                        'alternatives': contraindication.alternatives,
                        'action': 'BLOCK' if contraindication.severity == 'ABSOLUTE' else 'WARN'
                    })
        
        return warnings
