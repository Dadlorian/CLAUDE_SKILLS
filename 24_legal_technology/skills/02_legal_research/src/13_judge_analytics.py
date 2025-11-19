"""
Judge Analytics
Analytics on judicial behavior, decision patterns, and tendencies
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JudgeProfile:
    """Profile of a judge"""
    name: str
    court: str
    jurisdiction: str
    total_cases: int
    reversal_rate: float
    affirmance_rate: float
    remand_rate: float
    avg_opinion_length: int
    specialization: str


@dataclass
class DecisionPattern:
    """Pattern in judicial decisions"""
    judge_name: str
    issue_area: str
    plaintiff_win_rate: float
    defendant_win_rate: float
    settlement_rate: float


class JudgeAnalytics:
    """
    Analytics engine for judicial data
    """

    def __init__(self):
        """Initialize judge analytics"""
        self.judge_database = {}
        self.case_database = []

    def load_judge_data(self, judge_name: str, judge_profile: Dict) -> JudgeProfile:
        """
        Load judge profile data

        Args:
            judge_name: Name of judge
            judge_profile: Dictionary with judge data

        Returns:
            JudgeProfile object
        """
        profile = JudgeProfile(
            name=judge_name,
            court=judge_profile.get("court", "Unknown"),
            jurisdiction=judge_profile.get("jurisdiction", "Unknown"),
            total_cases=judge_profile.get("total_cases", 0),
            reversal_rate=judge_profile.get("reversal_rate", 0.0),
            affirmance_rate=judge_profile.get("affirmance_rate", 0.0),
            remand_rate=judge_profile.get("remand_rate", 0.0),
            avg_opinion_length=judge_profile.get("avg_opinion_length", 0),
            specialization=judge_profile.get("specialization", "General")
        )

        self.judge_database[judge_name] = profile
        logger.info(f"Loaded profile for Judge {judge_name}")
        return profile

    def add_case_outcome(self, judge_name: str, case_data: Dict):
        """
        Add case outcome data

        Args:
            judge_name: Judge name
            case_data: Dictionary with case information
        """
        case_data["judge"] = judge_name
        self.case_database.append(case_data)

    def get_decision_patterns(self, judge_name: str, issue_area: str = None) -> List[DecisionPattern]:
        """
        Get decision patterns for a judge

        Args:
            judge_name: Judge name
            issue_area: Specific issue area (optional)

        Returns:
            List of decision patterns
        """
        patterns = []

        # Filter cases by judge
        judge_cases = [c for c in self.case_database if c.get("judge") == judge_name]

        if not judge_cases:
            return patterns

        # Group by issue area
        issue_areas = {}
        for case in judge_cases:
            area = case.get("issue_area", "General")
            if issue_area and area != issue_area:
                continue

            if area not in issue_areas:
                issue_areas[area] = []
            issue_areas[area].append(case)

        # Calculate patterns
        for area, cases in issue_areas.items():
            plaintiff_wins = sum(1 for c in cases if c.get("outcome") == "plaintiff_win")
            defendant_wins = sum(1 for c in cases if c.get("outcome") == "defendant_win")
            settlements = sum(1 for c in cases if c.get("outcome") == "settlement")

            total = len(cases)
            if total > 0:
                pattern = DecisionPattern(
                    judge_name=judge_name,
                    issue_area=area,
                    plaintiff_win_rate=plaintiff_wins / total,
                    defendant_win_rate=defendant_wins / total,
                    settlement_rate=settlements / total
                )
                patterns.append(pattern)

        return patterns

    def compare_judges(self, judge1: str, judge2: str) -> Dict:
        """
        Compare two judges

        Args:
            judge1: First judge name
            judge2: Second judge name

        Returns:
            Comparison dictionary
        """
        profile1 = self.judge_database.get(judge1)
        profile2 = self.judge_database.get(judge2)

        if not profile1 or not profile2:
            logger.warning("One or both judges not found")
            return {}

        return {
            "judge1": judge1,
            "judge2": judge2,
            "reversal_rate_diff": abs(profile1.reversal_rate - profile2.reversal_rate),
            "affirmance_rate_diff": abs(profile1.affirmance_rate - profile2.affirmance_rate),
            "avg_opinion_length_diff": abs(profile1.avg_opinion_length - profile2.avg_opinion_length),
            "judge1_profile": {
                "reversal_rate": profile1.reversal_rate,
                "affirmance_rate": profile1.affirmance_rate,
                "specialization": profile1.specialization
            },
            "judge2_profile": {
                "reversal_rate": profile2.reversal_rate,
                "affirmance_rate": profile2.affirmance_rate,
                "specialization": profile2.specialization
            }
        }

    def predict_outcome(self, judge_name: str, case_type: str) -> Dict:
        """
        Predict likely outcome based on judge patterns

        Args:
            judge_name: Judge name
            case_type: Type of case

        Returns:
            Prediction with confidence
        """
        patterns = self.get_decision_patterns(judge_name, case_type)

        if not patterns:
            return {"prediction": "insufficient_data", "confidence": 0.0}

        # Use most specific pattern
        pattern = patterns[0]

        # Determine likely outcome
        if pattern.plaintiff_win_rate > 0.6:
            prediction = "plaintiff_likely_to_win"
            confidence = pattern.plaintiff_win_rate
        elif pattern.defendant_win_rate > 0.6:
            prediction = "defendant_likely_to_win"
            confidence = pattern.defendant_win_rate
        else:
            prediction = "balanced_outcome"
            confidence = 0.5

        return {
            "judge": judge_name,
            "case_type": case_type,
            "prediction": prediction,
            "confidence": confidence,
            "plaintiff_win_rate": pattern.plaintiff_win_rate,
            "defendant_win_rate": pattern.defendant_win_rate
        }

    def get_court_trends(self, court_name: str) -> Dict:
        """
        Get trends for specific court

        Args:
            court_name: Court name

        Returns:
            Dictionary with court trends
        """
        court_judges = [j for j in self.judge_database.values() if j.court == court_name]

        if not court_judges:
            return {"court": court_name, "data": "no_judges_found"}

        avg_reversal_rate = sum(j.reversal_rate for j in court_judges) / len(court_judges)
        avg_affirmance_rate = sum(j.affirmance_rate for j in court_judges) / len(court_judges)

        return {
            "court": court_name,
            "total_judges": len(court_judges),
            "avg_reversal_rate": avg_reversal_rate,
            "avg_affirmance_rate": avg_affirmance_rate,
            "judges": [j.name for j in court_judges]
        }

    def get_bias_analysis(self, judge_name: str) -> Dict:
        """
        Analyze potential bias in judge decisions

        Args:
            judge_name: Judge name

        Returns:
            Bias analysis dictionary
        """
        patterns = self.get_decision_patterns(judge_name)

        if not patterns:
            return {"judge": judge_name, "analysis": "insufficient_data"}

        plaintiff_avg = sum(p.plaintiff_win_rate for p in patterns) / len(patterns)
        defendant_avg = sum(p.defendant_win_rate for p in patterns) / len(patterns)

        # Simple bias detection
        bias = "neutral"
        if plaintiff_avg > 0.65:
            bias = "pro_plaintiff"
        elif defendant_avg > 0.65:
            bias = "pro_defendant"

        return {
            "judge": judge_name,
            "bias_assessment": bias,
            "plaintiff_win_rate_avg": plaintiff_avg,
            "defendant_win_rate_avg": defendant_avg,
            "sample_size": len(patterns)
        }


# Usage example
if __name__ == "__main__":
    analytics = JudgeAnalytics()

    # Load judge data
    analytics.load_judge_data("Judge Smith", {
        "court": "9th Circuit",
        "jurisdiction": "Federal",
        "total_cases": 500,
        "reversal_rate": 0.25,
        "affirmance_rate": 0.70,
        "remand_rate": 0.05,
        "avg_opinion_length": 2000,
        "specialization": "Employment Law"
    })

    # Add case outcomes
    analytics.add_case_outcome("Judge Smith", {
        "issue_area": "employment",
        "outcome": "plaintiff_win",
        "case_name": "Example v. Corp"
    })

    # Get predictions
    prediction = analytics.predict_outcome("Judge Smith", "employment")
    print(f"Outcome Prediction: {prediction}")
