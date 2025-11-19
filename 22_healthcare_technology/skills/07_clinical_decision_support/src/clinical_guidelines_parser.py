"""Clinical Guidelines Parser
Parses and executes clinical guidelines expressed in structured format
"""
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum

class GuidelineStrength(Enum):
    STRONG = "1"
    WEAK = "2"

class EvidenceQuality(Enum):
    HIGH = "A"
    MODERATE = "B"
    LOW = "C"
    VERY_LOW = "D"

@dataclass
class Guideline:
    id: str
    title: str
    condition: Callable[[Any], bool]
    recommendation: str
    strength: GuidelineStrength
    quality: EvidenceQuality
    source: str
    year: int

class GuidelineEngine:
    def __init__(self):
        self.guidelines: List[Guideline] = []
        self._load_guidelines()
    
    def _load_guidelines(self):
        # ACC/AHA Statin Guidelines
        self.guidelines.append(Guideline(
            id="statin_clinical_ascvd",
            title="Statin for Clinical ASCVD",
            condition=lambda p: p.get('clinical_ascvd', False) and p.get('age', 0) < 75,
            recommendation="High-intensity statin (atorvastatin 40-80mg or rosuvastatin 20-40mg)",
            strength=GuidelineStrength.STRONG,
            quality=EvidenceQuality.HIGH,
            source="ACC/AHA Cholesterol Guidelines",
            year=2018
        ))
        
        # Hypertension Guidelines
        self.guidelines.append(Guideline(
            id="hypertension_stage1",
            title="Hypertension Stage 1 Treatment",
            condition=lambda p: 130 <= p.get('sbp', 0) < 140 and p.get('ascvd_risk_10yr', 0) >= 0.10,
            recommendation="Initiate antihypertensive medication + lifestyle modifications",
            strength=GuidelineStrength.STRONG,
            quality=EvidenceQuality.HIGH,
            source="ACC/AHA Hypertension Guidelines",
            year=2017
        ))
        
        # Diabetes Screening
        self.guidelines.append(Guideline(
            id="diabetes_screening_age",
            title="Diabetes Screening for Adults ≥35",
            condition=lambda p: p.get('age', 0) >= 35 and not p.get('has_diabetes', False),
            recommendation="Screen for diabetes with FPG, A1C, or 75g OGTT",
            strength=GuidelineStrength.WEAK,
            quality=EvidenceQuality.MODERATE,
            source="ADA Standards of Care",
            year=2023
        ))
    
    def evaluate_patient(self, patient: Dict) -> List[Dict]:
        """Evaluate patient against all guidelines"""
        applicable_guidelines = []
        
        for guideline in self.guidelines:
            try:
                if guideline.condition(patient):
                    applicable_guidelines.append({
                        'id': guideline.id,
                        'title': guideline.title,
                        'recommendation': guideline.recommendation,
                        'grade': f"{guideline.strength.value}{guideline.quality.value}",
                        'source': f"{guideline.source} ({guideline.year})"
                    })
            except Exception as e:
                print(f"Error evaluating guideline {guideline.id}: {e}")
        
        return applicable_guidelines

# Example usage
if __name__ == "__main__":
    engine = GuidelineEngine()
    
    patient = {
        'age': 65,
        'clinical_ascvd': True,
        'sbp': 135,
        'ascvd_risk_10yr': 0.15,
        'has_diabetes': False
    }
    
    recommendations = engine.evaluate_patient(patient)
    
    for rec in recommendations:
        print(f"\n{rec['title']} (Grade {rec['grade']})")
        print(f"  {rec['recommendation']}")
        print(f"  Source: {rec['source']}")
