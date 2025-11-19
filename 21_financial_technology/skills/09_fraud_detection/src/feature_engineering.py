"""
Feature Engineering - Extract features from raw transaction data
"""

from typing import Dict
import math


class FeatureEngineer:
    """Extract features from transactions"""

    @staticmethod
    def extract_features(transaction: Dict, customer_profile: Dict = None) -> Dict:
        """Extract features for fraud detection"""
        features = {}

        # Transaction features
        features['amount'] = transaction.get('amount', 0)
        features['amount_log'] = math.log1p(transaction.get('amount', 0))

        # Temporal features
        hour = transaction.get('hour', 12)
        features['is_night'] = 1 if hour < 6 or hour > 22 else 0
        features['is_weekend'] = 1 if transaction.get('day_of_week', 3) > 5 else 0

        # Customer baseline features
        if customer_profile:
            baseline_amount = customer_profile.get('avg_amount', transaction.get('amount', 0))
            features['amount_deviation'] = abs(transaction.get('amount', 0) - baseline_amount)

        # Device features
        features['device_age_days'] = transaction.get('device_age_days', 30)
        features['is_new_device'] = 1 if transaction.get('device_age_days', 30) < 1 else 0

        # Merchant features
        features['high_risk_merchant'] = 1 if transaction.get('merchant_category') in [
            'cryptocurrency', 'money_transfer', 'gambling'
        ] else 0

        return features
