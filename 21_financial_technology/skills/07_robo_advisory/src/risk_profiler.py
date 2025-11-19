"""
Risk Profiler - Assesses investor risk tolerance and capacity
"""
from typing import Dict


class RiskProfiler:
    """Evaluates investor risk profile"""

    CAPACITY_QUESTIONS = [
        "Years to retirement?",
        "Annual income stability?",
        "Liquidity needs (% annual)?",
        "Debt level?",
        "Emergency fund months?"
    ]

    TOLERANCE_QUESTIONS = [
        "Comfort with 30% portfolio decline?",
        "Investment experience?",
        "Return vs safety priority?"
    ]

    def __init__(self):
        self.capacity_score = 0
        self.tolerance_score = 0
        self.overall_score = 0

    def assess_capacity(self, responses: Dict) -> float:
        """Calculate financial risk capacity"""
        score = 0
        
        # Time horizon (0-10 points)
        years = responses.get('years_to_goal', 0)
        score += min(10, years / 2)
        
        # Income stability (0-10 points)
        stability = responses.get('income_stability', 5)
        score += stability
        
        # Liquidity needs (0-10 points)
        needs = responses.get('liquidity_percent', 2)
        score += max(0, 10 - (needs * 2))

        self.capacity_score = score / 3
        return self.capacity_score

    def assess_tolerance(self, responses: Dict) -> float:
        """Calculate psychological risk tolerance"""
        score = 0

        # Loss aversion
        loss_comfort = responses.get('loss_comfort', 5)
        score += loss_comfort

        # Experience
        experience = responses.get('investment_experience', 5)
        score += experience

        # Return preference
        return_priority = responses.get('return_priority', 5)
        score += return_priority

        self.tolerance_score = score / 3
        return self.tolerance_score

    def calculate_overall_score(self) -> float:
        """Combine capacity and tolerance"""
        self.overall_score = (self.capacity_score * 0.6 + 
                             self.tolerance_score * 0.4)
        return self.overall_score

    def get_risk_profile(self) -> str:
        """Map score to risk profile"""
        score = self.overall_score
        if score < 3:
            return "Conservative"
        elif score < 5:
            return "Moderate-Conservative"
        elif score < 7:
            return "Moderate"
        elif score < 9:
            return "Moderate-Aggressive"
        else:
            return "Aggressive"
