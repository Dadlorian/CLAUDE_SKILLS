"""Risk Management Analysis - ISO 14971 Implementation"""
from dataclasses import dataclass
from enum import Enum
from typing import List

class Severity(Enum):
    CRITICAL = 5  # Death or permanent injury
    MAJOR = 4     # Serious injury
    MODERATE = 3  # Temporary injury
    MINOR = 2     # Minor issue
    NEGLIGIBLE = 1

class Probability(Enum):
    FREQUENT = 5      # Regular occurrence
    PROBABLE = 4      # Occasional
    OCCASIONAL = 3    # Rare
    REMOTE = 2        # Very rare
    EXTREMELY_REMOTE = 1

@dataclass
class Hazard:
    """Hazard identification per ISO 14971"""
    id: str
    name: str
    source: str
    harm: str
    severity: Severity
    probability: Probability
    
    @property
    def risk_score(self) -> int:
        """Risk = Severity × Probability"""
        return self.severity.value * self.probability.value
    
    def is_acceptable(self, threshold: int = 9) -> bool:
        """Risk acceptable if score below threshold"""
        return self.risk_score < threshold

@dataclass
class RiskControl:
    """Risk control measure"""
    id: str
    hazard_id: str
    description: str
    reduces_probability: bool
    new_probability: Probability
    verification_method: str
    
    def effectiveness(self, original_hazard: Hazard) -> float:
        """Calculate control effectiveness percentage"""
        original = original_hazard.probability.value
        remaining = self.new_probability.value
        return ((original - remaining) / original) * 100

class RiskAnalysis:
    """Perform ISO 14971 risk analysis"""
    
    def __init__(self):
        self.hazards: List[Hazard] = []
        self.controls: List[RiskControl] = []
    
    def add_hazard(self, hazard: Hazard):
        """Document hazard"""
        self.hazards.append(hazard)
    
    def add_control(self, control: RiskControl):
        """Document risk control"""
        self.controls.append(control)
    
    def residual_risk_assessment(self):
        """Evaluate residual risk after controls"""
        results = {}
        for hazard in self.hazards:
            hazard_controls = [c for c in self.controls if c.hazard_id == hazard.id]
            residual_prob = hazard.probability
            
            for control in hazard_controls:
                if control.reduces_probability:
                    residual_prob = control.new_probability
            
            residual_risk = hazard.severity.value * residual_prob.value
            results[hazard.id] = {
                'original_risk': hazard.risk_score,
                'residual_risk': residual_risk,
                'acceptable': residual_risk < 9
            }
        return results

# Example: Glucose Device Risk Analysis
def example_risk_analysis():
    analysis = RiskAnalysis()
    
    # Hazard 1: Incorrect dose calculation
    hazard1 = Hazard(
        id='H001',
        name='Incorrect glucose reading',
        source='Software rounding error',
        harm='Patient receives wrong insulin dose',
        severity=Severity.CRITICAL,
        probability=Probability.OCCASIONAL
    )
    analysis.add_hazard(hazard1)
    
    # Risk Control 1: Algorithm validation
    control1 = RiskControl(
        id='RC001',
        hazard_id='H001',
        description='Comprehensive algorithm testing',
        reduces_probability=True,
        new_probability=Probability.REMOTE,
        verification_method='100+ test cases, boundary testing'
    )
    analysis.add_control(control1)
    
    # Risk Control 2: User confirmation
    control2 = RiskControl(
        id='RC002',
        hazard_id='H001',
        description='User must confirm reading before dose',
        reduces_probability=True,
        new_probability=Probability.EXTREMELY_REMOTE,
        verification_method='Usability testing with representative users'
    )
    analysis.add_control(control2)
    
    return analysis
