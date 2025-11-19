"""Machine learning-based fraud scoring"""
import logging
import numpy as np
from datetime import datetime, timedelta

class FraudScorer:
    def __init__(self, ml_model, velocity_engine):
        self.model = ml_model
        self.velocity = velocity_engine
        self.logger = logging.getLogger(__name__)

    async def assess_risk(self, transaction):
        """Calculate fraud risk score (0-300)"""
        features = await self._extract_features(transaction)
        score = self.model.predict(features)[0]
        
        # Add velocity checks
        velocity_score = await self.velocity.calculate_risk(transaction)
        score += velocity_score

        return min(score, 300)

    async def _extract_features(self, transaction):
        """Extract ML features"""
        features = np.array([
            transaction['amount_cents'] / 100,
            self._encode_card_brand(transaction.get('card_brand')),
            self._encode_country(transaction.get('country')),
            self._is_new_customer(transaction),
            await self._device_risk_score(transaction),
        ])
        return features

    def _encode_card_brand(self, brand):
        brands = {'visa': 1, 'mastercard': 2, 'amex': 3}
        return brands.get(brand, 0)

    def _encode_country(self, country):
        high_risk = {'NG', 'RU', 'IR', 'KP', 'SY'}
        return 1 if country in high_risk else 0

    def _is_new_customer(self, transaction):
        return 1 if not transaction.get('customer_id') else 0

    async def _device_risk_score(self, transaction):
        device = transaction.get('device', {})
        score = 0
        if device.get('is_vpn'):
            score += 0.3
        if device.get('is_proxy'):
            score += 0.4
        return min(score, 1.0)
