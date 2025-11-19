"""
Case Outcome Predictor
Predicts case outcomes based on historical data and ML
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Prediction result"""
    case_id: str
    plaintiff_win_probability: float
    defendant_win_probability: float
    settlement_probability: float
    confidence: float
    key_factors: List[Tuple[str, float]]


class CaseOutcomePredictor:
    """
    Predicts case outcomes
    """

    def __init__(self):
        """Initialize predictor"""
        self.historical_cases = []
        self.feature_importance = {}

    def add_historical_case(self, case_data: Dict):
        """
        Add historical case for training

        Args:
            case_data: Case data dictionary
        """
        self.historical_cases.append(case_data)

    def predict_outcome(self, case_data: Dict) -> PredictionResult:
        """
        Predict case outcome

        Args:
            case_data: Case details

        Returns:
            Prediction result
        """
        # Extract features
        features = self._extract_features(case_data)

        # Calculate probabilities
        plaintiff_prob = self._calculate_plaintiff_win_probability(features)
        defendant_prob = 1.0 - plaintiff_prob
        settlement_prob = self._estimate_settlement_probability(features)

        # Normalize probabilities
        total = plaintiff_prob + defendant_prob + settlement_prob
        plaintiff_prob /= total
        defendant_prob /= total
        settlement_prob /= total

        # Identify key factors
        key_factors = self._identify_key_factors(features)

        # Calculate confidence
        confidence = max(plaintiff_prob, defendant_prob, settlement_prob)

        result = PredictionResult(
            case_id=case_data.get("id", "unknown"),
            plaintiff_win_probability=plaintiff_prob,
            defendant_win_probability=defendant_prob,
            settlement_probability=settlement_prob,
            confidence=confidence,
            key_factors=key_factors
        )

        logger.info(f"Predicted outcome for case {result.case_id}: "
                   f"Plaintiff {plaintiff_prob:.1%}, Defendant {defendant_prob:.1%}")

        return result

    @staticmethod
    def _extract_features(case_data: Dict) -> Dict[str, float]:
        """Extract features from case data"""
        return {
            "plaintiff_funding": case_data.get("plaintiff_funding", 0) / 1000000,
            "defendant_funding": case_data.get("defendant_funding", 0) / 1000000,
            "judge_plaintiff_bias": case_data.get("judge_plaintiff_win_rate", 0.5),
            "precedent_strength": case_data.get("precedent_strength", 0.5),
            "evidence_quality": case_data.get("evidence_quality", 0.5),
            "damages_amount": min(case_data.get("damages_claimed", 0) / 1000000, 10),
        }

    @staticmethod
    def _calculate_plaintiff_win_probability(features: Dict[str, float]) -> float:
        """Calculate plaintiff win probability"""
        # Simple weighted formula
        prob = 0.5

        # Funding advantage
        funding_ratio = features.get("plaintiff_funding", 0) / (
            features.get("defendant_funding", 0) + features.get("plaintiff_funding", 1)
        )
        prob += (funding_ratio - 0.5) * 0.2

        # Judge bias
        judge_bias = features.get("judge_plaintiff_bias", 0.5)
        prob += (judge_bias - 0.5) * 0.3

        # Precedent
        precedent = features.get("precedent_strength", 0.5)
        prob += (precedent - 0.5) * 0.25

        # Evidence
        evidence = features.get("evidence_quality", 0.5)
        prob += (evidence - 0.5) * 0.25

        # Clamp probability
        return max(0.1, min(0.9, prob))

    @staticmethod
    def _estimate_settlement_probability(features: Dict[str, float]) -> float:
        """Estimate settlement probability"""
        # Cases with close probabilities more likely to settle
        prob = max(0.2, 1.0 - abs(features.get("plaintiff_funding", 0) - features.get("defendant_funding", 0)))
        return prob * 0.3

    @staticmethod
    def _identify_key_factors(features: Dict[str, float]) -> List[Tuple[str, float]]:
        """Identify key decision factors"""
        factor_weights = [
            ("Judge Bias", features.get("judge_plaintiff_bias", 0.5)),
            ("Precedent Strength", features.get("precedent_strength", 0.5)),
            ("Evidence Quality", features.get("evidence_quality", 0.5)),
            ("Funding Advantage", features.get("plaintiff_funding", 0) - features.get("defendant_funding", 0)),
        ]

        # Sort by importance
        return sorted(factor_weights, key=lambda x: abs(x[1] - 0.5), reverse=True)

    def get_similar_cases(self, case_data: Dict, top_k: int = 5) -> List[Dict]:
        """
        Find similar historical cases

        Args:
            case_data: Case details
            top_k: Number of similar cases to return

        Returns:
            List of similar cases
        """
        if not self.historical_cases:
            return []

        # Calculate similarity
        similarities = []
        case_features = self._extract_features(case_data)

        for hist_case in self.historical_cases:
            hist_features = self._extract_features(hist_case)
            similarity = self._calculate_similarity(case_features, hist_features)
            similarities.append((hist_case, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return [case for case, _ in similarities[:top_k]]

    @staticmethod
    def _calculate_similarity(features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two feature sets"""
        # Euclidean distance
        distance = 0.0
        for key in features1:
            if key in features2:
                distance += (features1[key] - features2[key]) ** 2

        similarity = 1.0 / (1.0 + distance ** 0.5)
        return similarity


# Usage example
if __name__ == "__main__":
    predictor = CaseOutcomePredictor()

    # Add historical cases
    predictor.add_historical_case({
        "id": "historical_001",
        "plaintiff_funding": 500000,
        "defendant_funding": 1000000,
        "judge_plaintiff_win_rate": 0.55,
        "precedent_strength": 0.7,
        "evidence_quality": 0.8,
        "damages_claimed": 2000000,
        "outcome": "plaintiff_win"
    })

    # Predict outcome
    prediction = predictor.predict_outcome({
        "id": "case_001",
        "plaintiff_funding": 600000,
        "defendant_funding": 900000,
        "judge_plaintiff_win_rate": 0.60,
        "precedent_strength": 0.75,
        "evidence_quality": 0.85,
        "damages_claimed": 2500000
    })

    print(f"Prediction: Plaintiff {prediction.plaintiff_win_probability:.1%}, "
          f"Defendant {prediction.defendant_win_probability:.1%}")
