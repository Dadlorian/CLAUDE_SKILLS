# Fraud Prevention Guide

Practical fraud detection and prevention strategies using ML, velocity checks, device fingerprinting, and risk scoring.

## Overview

Payment fraud costs businesses billions annually. Effective fraud prevention requires a multi-layered approach combining machine learning, rule-based systems, device intelligence, and behavioral analytics while minimizing false positives that hurt legitimate customers.

## Core Prevention Layers

### 1. Device Fingerprinting

```python
import hashlib
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeviceFingerprint:
    fingerprint_id: str
    ip_address: str
    user_agent: str
    screen_resolution: str
    timezone: str
    language: str
    plugins: list
    canvas_hash: str
    webgl_hash: str
    risk_score: float
    first_seen: datetime
    last_seen: datetime

class DeviceFingerprintCollector:
    """Collect and analyze device fingerprints"""

    def generate_fingerprint(self, device_data: Dict) -> str:
        """Generate unique device fingerprint"""
        components = [
            device_data.get('user_agent', ''),
            device_data.get('screen_resolution', ''),
            device_data.get('timezone', ''),
            device_data.get('language', ''),
            device_data.get('canvas_hash', ''),
            device_data.get('webgl_hash', ''),
            ','.join(sorted(device_data.get('plugins', [])))
        ]

        fingerprint_string = '|'.join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    async def analyze_device(self, fingerprint: DeviceFingerprint) -> Dict:
        """Analyze device for fraud indicators"""
        risk_signals = []
        risk_score = 0.0

        # Check if device seen before
        device_history = await self._get_device_history(fingerprint.fingerprint_id)

        if not device_history:
            risk_signals.append('first_time_device')
            risk_score += 0.2

        # Check for suspicious patterns
        if await self._is_vpn_or_proxy(fingerprint.ip_address):
            risk_signals.append('vpn_or_proxy')
            risk_score += 0.3

        if self._has_suspicious_user_agent(fingerprint.user_agent):
            risk_signals.append('suspicious_user_agent')
            risk_score += 0.15

        # Check device velocity
        recent_transactions = await self._get_recent_transactions(
            fingerprint.fingerprint_id,
            hours=24
        )
        if len(recent_transactions) > 10:
            risk_signals.append('high_device_velocity')
            risk_score += 0.25

        # Check for device manipulation
        if self._detect_fingerprint_manipulation(device_data):
            risk_signals.append('fingerprint_manipulation')
            risk_score += 0.4

        return {
            'fingerprint_id': fingerprint.fingerprint_id,
            'risk_score': min(risk_score, 1.0),
            'risk_signals': risk_signals,
            'device_history': device_history
        }

    def _detect_fingerprint_manipulation(self, device_data: Dict) -> bool:
        """Detect if device fingerprint is being spoofed"""
        # Check for common manipulation patterns
        if device_data.get('plugins') == []:
            return True  # Suspiciously empty plugins

        if 'HeadlessChrome' in device_data.get('user_agent', ''):
            return True  # Automated browser

        return False
```

### 2. Velocity Checks

```python
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Tuple

class VelocityChecker:
    """Monitor transaction velocity to detect suspicious patterns"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.thresholds = {
            'card_attempts_per_hour': 3,
            'card_attempts_per_day': 10,
            'transactions_per_ip_hour': 5,
            'unique_cards_per_device_day': 3,
            'high_value_per_day': 5000,
            'failed_attempts_per_hour': 3
        }

    async def check_velocity(self, transaction_data: Dict) -> Tuple[bool, List[str]]:
        """Check if transaction exceeds velocity thresholds"""
        violations = []

        # Check card velocity
        card_key = f"velocity:card:{transaction_data['card_fingerprint']}"
        card_count = await self.redis.incr(card_key)
        await self.redis.expire(card_key, 3600)  # 1 hour

        if card_count > self.thresholds['card_attempts_per_hour']:
            violations.append('card_velocity_exceeded')

        # Check IP velocity
        ip_key = f"velocity:ip:{transaction_data['ip_address']}:hour"
        ip_count = await self.redis.incr(ip_key)
        await self.redis.expire(ip_key, 3600)

        if ip_count > self.thresholds['transactions_per_ip_hour']:
            violations.append('ip_velocity_exceeded')

        # Check device velocity (unique cards)
        device_key = f"velocity:device:{transaction_data['device_fingerprint']}:cards"
        await self.redis.sadd(device_key, transaction_data['card_fingerprint'])
        await self.redis.expire(device_key, 86400)  # 24 hours

        unique_cards = await self.redis.scard(device_key)
        if unique_cards > self.thresholds['unique_cards_per_device_day']:
            violations.append('multiple_cards_same_device')

        # Check failed attempt velocity
        if not transaction_data.get('successful'):
            failed_key = f"velocity:failed:{transaction_data['card_fingerprint']}"
            failed_count = await self.redis.incr(failed_key)
            await self.redis.expire(failed_key, 3600)

            if failed_count > self.thresholds['failed_attempts_per_hour']:
                violations.append('excessive_failed_attempts')

        # Check high-value transaction velocity
        if transaction_data['amount'] > 500:
            high_value_key = f"velocity:highvalue:{transaction_data['customer_id']}:day"
            high_value_sum = await self.redis.incrby(
                high_value_key,
                int(transaction_data['amount'] * 100)
            )
            await self.redis.expire(high_value_key, 86400)

            if high_value_sum / 100 > self.thresholds['high_value_per_day']:
                violations.append('high_value_velocity_exceeded')

        is_suspicious = len(violations) > 0
        return is_suspicious, violations
```

### 3. Risk Scoring Engine

```python
from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class RiskScoringEngine:
    """ML-based risk scoring for transactions"""

    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)
        self.feature_names = [
            'amount', 'hour_of_day', 'day_of_week',
            'device_risk_score', 'ip_risk_score',
            'card_age_days', 'customer_age_days',
            'previous_transactions_count', 'previous_chargebacks',
            'distance_from_shipping', 'cvv_provided',
            'shipping_matches_billing', 'email_domain_age',
            'phone_verified', 'transaction_velocity'
        ]

    def calculate_risk_score(self, transaction: Dict,
                            customer: Dict,
                            device: Dict) -> Dict:
        """Calculate comprehensive risk score"""

        # Extract features
        features = self._extract_features(transaction, customer, device)

        # Get ML model prediction
        ml_score = self.model.predict_proba([features])[0][1]

        # Calculate rule-based score
        rule_score = self._calculate_rule_based_score(transaction, customer, device)

        # Combine scores (weighted average)
        combined_score = (ml_score * 0.7) + (rule_score * 0.3)

        # Determine risk level
        risk_level = self._determine_risk_level(combined_score)

        # Get contributing factors
        risk_factors = self._identify_risk_factors(transaction, customer, device)

        return {
            'risk_score': round(combined_score, 3),
            'risk_level': risk_level,
            'ml_score': round(ml_score, 3),
            'rule_score': round(rule_score, 3),
            'risk_factors': risk_factors,
            'recommendation': self._get_recommendation(risk_level)
        }

    def _extract_features(self, transaction: Dict,
                         customer: Dict, device: Dict) -> List[float]:
        """Extract features for ML model"""
        return [
            float(transaction['amount']),
            float(transaction['timestamp'].hour),
            float(transaction['timestamp'].weekday()),
            float(device.get('risk_score', 0)),
            float(transaction.get('ip_risk_score', 0)),
            float((datetime.utcnow() - customer['card_added_at']).days),
            float((datetime.utcnow() - customer['created_at']).days),
            float(customer.get('transaction_count', 0)),
            float(customer.get('chargeback_count', 0)),
            float(transaction.get('shipping_distance_km', 0)),
            float(1 if transaction.get('cvv_provided') else 0),
            float(1 if transaction.get('addresses_match') else 0),
            float(customer.get('email_domain_age_days', 0)),
            float(1 if customer.get('phone_verified') else 0),
            float(transaction.get('velocity_score', 0))
        ]

    def _calculate_rule_based_score(self, transaction: Dict,
                                    customer: Dict, device: Dict) -> float:
        """Calculate score based on business rules"""
        score = 0.0

        # High-risk countries
        if transaction['country'] in ['NG', 'GH', 'VN']:
            score += 0.3

        # First transaction
        if customer.get('transaction_count', 0) == 0:
            score += 0.2

        # High amount for new customer
        if transaction['amount'] > 1000 and customer.get('transaction_count', 0) < 5:
            score += 0.25

        # Shipping to different country than billing
        if transaction['shipping_country'] != transaction['billing_country']:
            score += 0.15

        # Email from temporary provider
        if customer['email'].endswith(('@tempmail.com', '@guerrillamail.com')):
            score += 0.3

        # No CVV provided
        if not transaction.get('cvv_provided'):
            score += 0.15

        # VPN/Proxy usage
        if transaction.get('is_vpn'):
            score += 0.2

        return min(score, 1.0)

    def _determine_risk_level(self, score: float) -> str:
        """Map risk score to risk level"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        elif score >= 0.2:
            return 'low'
        else:
            return 'minimal'

    def _identify_risk_factors(self, transaction: Dict,
                               customer: Dict, device: Dict) -> List[str]:
        """Identify specific risk factors"""
        factors = []

        if customer.get('transaction_count', 0) == 0:
            factors.append('first_transaction')

        if transaction['amount'] > 500:
            factors.append('high_value_transaction')

        if device.get('risk_score', 0) > 0.6:
            factors.append('suspicious_device')

        if transaction.get('is_vpn'):
            factors.append('vpn_detected')

        if not transaction.get('cvv_provided'):
            factors.append('no_cvv')

        if transaction['shipping_country'] != transaction['billing_country']:
            factors.append('cross_border_shipping')

        return factors

    def _get_recommendation(self, risk_level: str) -> str:
        """Get action recommendation based on risk level"""
        recommendations = {
            'minimal': 'approve',
            'low': 'approve',
            'medium': 'require_3ds',
            'high': 'manual_review',
            'critical': 'decline'
        }
        return recommendations.get(risk_level, 'manual_review')
```

### 4. 3D Secure Challenge

```python
class ThreeDSecureManager:
    """Manage 3D Secure authentication challenges"""

    def __init__(self, payment_processor):
        self.processor = payment_processor

    async def should_challenge(self, risk_score: float,
                              transaction: Dict) -> bool:
        """Determine if 3DS challenge is needed"""

        # Always challenge high-risk transactions
        if risk_score >= 0.6:
            return True

        # Challenge based on amount
        if transaction['amount'] > 1000:
            return True

        # Challenge for certain countries (PSD2)
        if transaction['country'] in ['GB', 'FR', 'DE', 'IT', 'ES']:
            # SCA required for most transactions in EU
            if transaction['amount'] > 30:
                return True

        # Challenge first-time customers for amounts > $100
        if transaction.get('customer_transaction_count', 0) == 0:
            if transaction['amount'] > 100:
                return True

        return False

    async def initiate_3ds_challenge(self, transaction_id: str,
                                     payment_method: Dict) -> Dict:
        """Initiate 3DS authentication"""

        challenge = await self.processor.create_3ds_challenge(
            transaction_id=transaction_id,
            card_number=payment_method['card_number'],
            amount=transaction['amount'],
            currency=transaction['currency'],
            return_url=f"https://api.example.com/3ds/callback/{transaction_id}"
        )

        return {
            'challenge_required': True,
            'challenge_url': challenge['url'],
            'challenge_token': challenge['token']
        }
```

### 5. Fraud Rules Engine

```python
from dataclasses import dataclass
from typing import Callable, List

@dataclass
class FraudRule:
    name: str
    condition: Callable
    action: str  # 'block', 'review', 'challenge'
    risk_weight: float

class FraudRulesEngine:
    """Configurable rules-based fraud detection"""

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> List[FraudRule]:
        """Define fraud detection rules"""
        return [
            FraudRule(
                name='email_domain_mismatch',
                condition=lambda t, c: (
                    t['email'].split('@')[1] != c['original_email'].split('@')[1]
                ),
                action='review',
                risk_weight=0.3
            ),
            FraudRule(
                name='excessive_failed_attempts',
                condition=lambda t, c: c.get('failed_attempts_24h', 0) > 3,
                action='block',
                risk_weight=0.5
            ),
            FraudRule(
                name='high_value_new_customer',
                condition=lambda t, c: (
                    t['amount'] > 1000 and c.get('transaction_count', 0) == 0
                ),
                action='review',
                risk_weight=0.4
            ),
            FraudRule(
                name='shipping_to_freight_forwarder',
                condition=lambda t, c: self._is_freight_forwarder(t['shipping_address']),
                action='review',
                risk_weight=0.35
            ),
            FraudRule(
                name='impossible_geography',
                condition=lambda t, c: self._check_impossible_travel(t, c),
                action='block',
                risk_weight=0.6
            )
        ]

    async def evaluate_rules(self, transaction: Dict, customer: Dict) -> Dict:
        """Evaluate all fraud rules"""
        triggered_rules = []
        total_risk = 0.0
        recommended_action = 'approve'

        for rule in self.rules:
            try:
                if rule.condition(transaction, customer):
                    triggered_rules.append({
                        'name': rule.name,
                        'action': rule.action,
                        'weight': rule.risk_weight
                    })
                    total_risk += rule.risk_weight

                    # Update recommended action
                    if rule.action == 'block':
                        recommended_action = 'block'
                    elif rule.action == 'review' and recommended_action != 'block':
                        recommended_action = 'review'
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")

        return {
            'triggered_rules': triggered_rules,
            'total_risk': min(total_risk, 1.0),
            'recommended_action': recommended_action
        }

    def _is_freight_forwarder(self, address: Dict) -> bool:
        """Check if shipping address is a known freight forwarder"""
        freight_forwarders = [
            'package forwarder', 'mail forwarding', 'parcel forwarding'
        ]
        address_text = f"{address.get('company', '')} {address.get('address1', '')}"
        return any(ff in address_text.lower() for ff in freight_forwarders)

    def _check_impossible_travel(self, transaction: Dict, customer: Dict) -> bool:
        """Check if transaction location is impossible given recent activity"""
        last_location = customer.get('last_transaction_location')
        last_time = customer.get('last_transaction_time')

        if not last_location or not last_time:
            return False

        # Calculate distance and time difference
        distance_km = self._calculate_distance(
            last_location,
            transaction['location']
        )
        time_diff_hours = (transaction['timestamp'] - last_time).total_seconds() / 3600

        # Check if travel speed is impossible (e.g., > 900 km/h)
        max_speed_kmh = 900
        required_speed = distance_km / time_diff_hours if time_diff_hours > 0 else float('inf')

        return required_speed > max_speed_kmh
```

## Best Practices

### 1. Layered Defense
- Combine multiple detection methods
- Use ML for pattern recognition
- Apply rules for known fraud vectors
- Leverage device intelligence
- Monitor behavioral signals

### 2. False Positive Management
```python
class FalsePositiveOptimizer:
    """Reduce false positives while maintaining fraud detection"""

    async def adjust_thresholds(self, historical_data: List[Dict]):
        """Optimize thresholds based on historical performance"""
        # Analyze false positive rate
        fp_rate = self._calculate_fp_rate(historical_data)

        if fp_rate > 0.05:  # More than 5% false positives
            # Increase threshold slightly
            self.risk_threshold += 0.05
            logger.info(f"Increased risk threshold to {self.risk_threshold}")

    def _calculate_fp_rate(self, data: List[Dict]) -> float:
        """Calculate false positive rate"""
        declined = [t for t in data if t['action'] == 'declined']
        false_positives = [t for t in declined if not t['was_fraud']]
        return len(false_positives) / len(declined) if declined else 0
```

### 3. Real-time Monitoring
- Track fraud rates by country, product, amount
- Monitor model performance drift
- Alert on unusual patterns
- Track false positive rates

### 4. Continuous Learning
- Retrain ML models monthly
- Update rules based on new fraud patterns
- Analyze missed fraud cases
- A/B test new detection methods

## Production Considerations

### Performance
- Cache risk scores (1-minute TTL)
- Use Redis for velocity checks
- Async processing for non-blocking
- Batch device fingerprint lookups

### Compliance
- PSD2 Strong Customer Authentication
- GDPR data retention limits
- PCI DSS for card data handling
- Fair Credit Reporting Act (US)

### Testing
```python
# Test fraud detection with synthetic data
test_cases = [
    {
        'name': 'normal_transaction',
        'expected_risk': 'low',
        'amount': 50,
        'is_vpn': False,
        'customer_age_days': 365
    },
    {
        'name': 'high_risk_transaction',
        'expected_risk': 'high',
        'amount': 2000,
        'is_vpn': True,
        'customer_age_days': 0
    }
]
```

## References

- [Stripe Radar Documentation](https://stripe.com/docs/radar)
- [Device Fingerprinting Guide](../reference/tokenization.md)
- [3D Secure Implementation](../reference/3d_secure.md)
