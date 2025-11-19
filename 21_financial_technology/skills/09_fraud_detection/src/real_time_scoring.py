"""
Real-Time Scoring - Fast transaction scoring
"""

import time
from typing import Dict
import logging


class RealTimeScorer:
    """Real-time transaction scoring"""

    def __init__(self, components: Dict):
        self.components = components
        self.latency_threshold = 100  # ms

    def score_transaction(self, transaction: Dict) -> Dict:
        """Score transaction with latency tracking"""
        start_time = time.time()

        # Extract features
        features = self._extract_features(transaction)

        # Score with each component
        scores = {}
        for component_name, component in self.components.items():
            scores[component_name] = component.score(features)

        # Combine scores
        final_score = self._combine_scores(scores)

        latency_ms = (time.time() - start_time) * 1000

        # Log if slow
        if latency_ms > self.latency_threshold:
            logging.warning(f"Slow scoring: {latency_ms:.0f}ms")

        return {
            'transaction_id': transaction['id'],
            'fraud_score': final_score,
            'latency_ms': latency_ms
        }

    def _extract_features(self, transaction: Dict) -> Dict:
        """Extract features quickly"""
        return {
            'amount': transaction.get('amount', 0),
            'customer_id': transaction.get('customer_id'),
            'merchant': transaction.get('merchant')
        }

    def _combine_scores(self, scores: Dict) -> float:
        """Combine component scores"""
        weights = {
            'ml_model': 0.4,
            'rules': 0.3,
            'behavioral': 0.2,
            'device': 0.1
        }

        combined = sum(
            scores.get(name, 0) * weight
            for name, weight in weights.items()
        )

        return min(combined, 1.0)
