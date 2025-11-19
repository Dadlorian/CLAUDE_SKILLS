"""
Fraud Scorer - Combines multiple fraud detection methods into unified score
"""

import numpy as np
from typing import Dict, List, Tuple


class FraudScorer:
    """Main fraud scoring engine"""

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize scorer with component weights"""
        self.weights = weights or {
            'ml_model': 0.35,
            'rules_engine': 0.25,
            'behavioral': 0.20,
            'device': 0.15,
            'network': 0.05
        }

        # Validate weights sum to 1.0
        assert abs(sum(self.weights.values()) - 1.0) < 0.01

    def score_transaction(self, transaction: Dict,
                         components: Dict[str, float]) -> Dict:
        """Score transaction using multiple components"""

        # Validate component scores
        for component_name, weight in self.weights.items():
            if component_name not in components:
                raise ValueError(f"Missing component: {component_name}")

        # Calculate weighted score
        fraud_score = sum(
            components[component_name] * weight
            for component_name, weight in self.weights.items()
        )

        # Normalize to 0-1
        fraud_score = min(max(fraud_score, 0.0), 1.0)

        # Determine action
        action = self._determine_action(fraud_score)

        return {
            'transaction_id': transaction.get('id'),
            'fraud_score': fraud_score,
            'action': action,
            'component_scores': components,
            'weights': self.weights,
            'timestamp': transaction.get('timestamp')
        }

    def _determine_action(self, fraud_score: float) -> str:
        """Determine action based on fraud score"""
        if fraud_score < 0.3:
            return 'allow'
        elif fraud_score < 0.5:
            return 'monitor'
        elif fraud_score < 0.7:
            return 'challenge'
        else:
            return 'block'

    def explain_score(self, components: Dict[str, float]) -> Dict:
        """Explain which components contributed most to fraud score"""
        contributions = {}

        for component_name, score in components.items():
            weight = self.weights.get(component_name, 0)
            contribution = score * weight

            contributions[component_name] = {
                'score': score,
                'weight': weight,
                'contribution': contribution
            }

        # Sort by contribution
        sorted_contrib = sorted(
            contributions.items(),
            key=lambda x: x[1]['contribution'],
            reverse=True
        )

        return {
            'contributions': dict(sorted_contrib),
            'top_factors': [name for name, _ in sorted_contrib[:3]]
        }


class ComponentScorer:
    """Base class for individual scoring components"""

    def score(self, features: Dict) -> float:
        """Score features, returning 0-1 fraud probability"""
        raise NotImplementedError


class MLModelScorer(ComponentScorer):
    """ML model-based fraud scoring"""

    def __init__(self, model):
        self.model = model

    def score(self, features: Dict) -> float:
        """Score using ML model"""
        # Extract feature array
        feature_array = np.array([[features.get(f, 0) for f in self.feature_names]])

        # Get probability
        probability = self.model.predict_proba(feature_array)[0][1]

        return probability


class RulesEngineScorer(ComponentScorer):
    """Rules-based fraud scoring"""

    def __init__(self, rules_engine):
        self.rules_engine = rules_engine

    def score(self, features: Dict) -> float:
        """Score using rules engine"""
        result = self.rules_engine.evaluate_transaction(features)

        return result.get('score', 0.0)


class BehavioralScorer(ComponentScorer):
    """Behavioral anomaly scoring"""

    def __init__(self, behavioral_analyzer):
        self.analyzer = behavioral_analyzer

    def score(self, features: Dict) -> float:
        """Score behavioral anomalies"""
        customer_id = features.get('customer_id')

        if not customer_id:
            return 0.5  # Unknown

        result = self.analyzer.score_customer_behavior(
            customer_id,
            features
        )

        return result.get('anomaly_score', 0.0)


if __name__ == '__main__':
    # Example usage
    scorer = FraudScorer()

    # Example component scores
    components = {
        'ml_model': 0.65,
        'rules_engine': 0.45,
        'behavioral': 0.55,
        'device': 0.70,
        'network': 0.30
    }

    transaction = {
        'id': 'txn_12345',
        'customer_id': 'cust_789',
        'amount': 2500
    }

    result = scorer.score_transaction(transaction, components)
    print(f"Fraud Score: {result['fraud_score']:.2%}")
    print(f"Action: {result['action']}")
    print(f"Components: {result['component_scores']}")

    # Explain the score
    explanation = scorer.explain_score(components)
    print(f"\nTop Factors: {explanation['top_factors']}")
