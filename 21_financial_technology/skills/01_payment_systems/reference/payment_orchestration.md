# Payment Orchestration Reference

## Overview

Payment orchestration is the intelligent routing and management of payment transactions across multiple processors, payment methods, and gateways to optimize for success rate, cost, fraud prevention, and customer experience.

## Orchestration Architecture

### Core Components

```
Payment Request
        |
        v
   Orchestrator (Decision Engine)
        |
        +-- Routing Rules
        |   - Customer segment
        |   - Payment method
        |   - Amount
        |   - Geographic location
        |   - Risk profile
        |
        +-- Processor Selection
        |   - Visa processor A
        |   - Visa processor B
        |   - Mastercard processor
        |   - Alternative methods
        |
        +-- Fallback Logic
        |   - Primary fails -> Secondary
        |   - Different processor
        |   - Different payment method
        |
        +-- Risk Assessment
        |   - Fraud detection
        |   - 3D Secure decision
        |   - Additional authentication
        |
        v
    Processor 1       Processor 2       Processor 3
        |                 |                 |
        +---- Execute Transaction ----+
                         |
                         v
                  Network Processing
                  (Visa, Mastercard, etc.)
                         |
                         v
                  Authorization Response
                         |
                         v
               Reconciliation & Settlement
```

## Routing Strategies

### Rule-Based Routing

```
Simple Rule Example:
if amount > $1,000 and country == 'US':
    processor = 'processor_a'  // Lower fees for high value
elif payment_method == 'visa' and country == 'EU':
    processor = 'processor_b'  // EU optimized
elif card_brand == 'amex':
    processor = 'processor_c'  // Amex specialist
else:
    processor = 'processor_a'  // Default

Complex Rule Example:
rule_engine = {
    'visa_us': {
        'processor': 'stripe',
        'conditions': {
            'card_brand': 'visa',
            'country': 'US',
            'amount_min': 0,
            'amount_max': None
        },
        'priority': 1,
        'success_threshold': 0.95
    },
    'visa_eu': {
        'processor': 'adyen',
        'conditions': {
            'card_brand': 'visa',
            'country': ['GB', 'DE', 'FR', 'ES', 'IT'],
            'amount_min': 0,
            'amount_max': None
        },
        'priority': 2,
        'success_threshold': 0.92
    },
    'amex_high_value': {
        'processor': 'paypalbraintree',
        'conditions': {
            'card_brand': 'amex',
            'amount_min': 1000,
            'amount_max': None
        },
        'priority': 1,
        'success_threshold': 0.98
    },
    'default': {
        'processor': 'stripe',
        'priority': 99,
        'success_threshold': 0.85
    }
}
```

### Optimization-Based Routing

```
Multi-Objective Optimization:

Objectives:
1. Success Rate (maximize approval %)
2. Cost (minimize fees and interchange)
3. Time (minimize latency/TTL)
4. Risk (minimize fraud exposure)

Example Algorithm:
class PaymentOrchestrator:
    def calculate_route_score(self, processor, payment):
        # Weight factors (configurable)
        success_weight = 0.40
        cost_weight = 0.30
        speed_weight = 0.20
        fraud_weight = 0.10

        # Get processor metrics
        success_rate = processor.recent_success_rate()
        cost = processor.calculate_fees(payment)
        latency = processor.average_latency()
        fraud_rate = processor.fraud_rate()

        # Normalize to 0-1 scale
        success_score = success_rate / 100.0
        cost_score = 1.0 - (cost / max_cost)
        speed_score = 1.0 - (latency / max_latency)
        fraud_score = 1.0 - (fraud_rate / max_fraud_rate)

        # Calculate weighted score
        total_score = (
            success_score * success_weight +
            cost_score * cost_weight +
            speed_score * speed_weight +
            fraud_score * fraud_weight
        )

        return total_score

    def select_processor(self, processors, payment):
        # Calculate score for each processor
        scores = [
            (self.calculate_route_score(p, payment), p)
            for p in processors
        ]

        # Sort by score (highest first)
        scores.sort(reverse=True, key=lambda x: x[0])

        # Return highest scoring processor
        return scores[0][1]
```

### Machine Learning-Based Routing

```
ML Routing Model:

Training Data:
- Historical transactions
- Success/failure outcome
- Processor performance
- Customer characteristics
- Payment details
- Time and geography

Features:
- Card brand and type
- Issuing country
- Merchant category
- Transaction amount
- Time of transaction
- Customer history
- Device characteristics
- IP geolocation
- Velocity metrics

Model:
- Gradient boosting (XGBoost)
- Neural network
- Ensemble methods
- Real-time inference

Output:
- Probability of success for each processor
- Select processor with highest success probability

Example (Python):
import xgboost as xgb
import numpy as np

class MLRoutingEngine:
    def __init__(self, model_path):
        self.model = xgb.Booster(model_file=model_path)
        self.processors = ['stripe', 'adyen', 'square', 'paypalbraintree']

    def select_processor(self, payment_data):
        features = self._prepare_features(payment_data)

        # Get success probabilities for each processor
        scores = {}
        for processor in self.processors:
            feature_set = np.append(features, self._encode_processor(processor))
            prob = self.model.predict([feature_set])[0]
            scores[processor] = prob

        # Select processor with highest success probability
        best_processor = max(scores, key=scores.get)
        confidence = scores[best_processor]

        return {
            'processor': best_processor,
            'confidence': confidence,
            'all_scores': scores
        }

    def _prepare_features(self, payment_data):
        return np.array([
            payment_data['amount'],
            payment_data['card_type_encoded'],
            payment_data['issuer_country_encoded'],
            payment_data['merchant_category_encoded'],
            payment_data['hour_of_day'],
            payment_data['day_of_week'],
            payment_data['customer_history_score'],
            payment_data['velocity_score'],
            payment_data['device_risk_score'],
            # ... more features
        ])

    def _encode_processor(self, processor_name):
        encoding = {
            'stripe': [1, 0, 0, 0],
            'adyen': [0, 1, 0, 0],
            'square': [0, 0, 1, 0],
            'paypalbraintree': [0, 0, 0, 1]
        }
        return encoding[processor_name]
```

## Multi-Processor Setup

### Processor Integration

```
Primary Flow:
1. Request routing to selected processor
2. Processor authorizes transaction
3. Transaction recorded in ledger
4. Confirmation sent to caller
5. Settlement handled by processor

Processor Selection:
- Stripe: High-volume merchants, global
- Adyen: International, multi-currency
- PayPal/Braintree: Integration ecosystem
- Square: SMB, integrated POS
- Worldpay: Enterprise, regional expertise

API Integration:
// Stripe API Example
const stripe = require('stripe')(STRIPE_API_KEY);

async function chargeViaStripe(paymentData) {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(paymentData.amount * 100),  // cents
      currency: paymentData.currency,
      payment_method: paymentData.payment_method_id,
      confirm: true,
      description: paymentData.description,
      metadata: {
        order_id: paymentData.order_id,
        customer_id: paymentData.customer_id
      }
    });

    return {
      success: paymentIntent.status === 'succeeded',
      transaction_id: paymentIntent.id,
      status: paymentIntent.status,
      amount: paymentIntent.amount / 100
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      code: error.code
    };
  }
}

// Adyen API Example
const { Client, Config, CheckoutAPI } = require('@adyen/api-library');

async function chargeViaAdyen(paymentData) {
  const config = new Config();
  config.apiKey = ADYEN_API_KEY;
  const client = new Client({ config });
  const checkout = new CheckoutAPI(client);

  const paymentRequest = {
    amount: { value: paymentData.amount * 100, currency: paymentData.currency },
    reference: paymentData.reference,
    paymentMethod: paymentData.payment_method,
    returnUrl: 'https://example.com/result',
    metadata: {
      order_id: paymentData.order_id
    }
  };

  const response = await checkout.payments(paymentRequest);

  return {
    success: response.resultCode === 'Authorised',
    transaction_id: response.pspReference,
    status: response.resultCode,
    amount: paymentData.amount
  };
}
```

## Fallback and Retry Logic

### Fallback Chains

```
Fallback Strategy Example:
1. Primary: Stripe (Visa, highest success rate)
2. Secondary: Adyen (Visa backup processor)
3. Tertiary: PayPal/Braintree (different network)
4. Quaternary: Manual review (high-risk accept)

Triggering Fallback:
- Primary fails/times out
- Decline reason is retryable
- Decline reason triggers specific fallback

Decline Codes Triggering Fallback:
- Processor unavailable (5xx)
- Timeout (retry different processor)
- Temporary decline (soft decline)
- Rate limit exceeded
- Authentication required (try 3DS)

DO NOT Fallback:
- Insufficient funds (R01)
- Account closed (R02)
- Card expired
- Cardholder requested stop (hard decline)

Example Implementation (Python):
class FallbackOrchestrator:
    def __init__(self):
        self.fallback_chains = {
            'visa': ['stripe', 'adyen', 'square', 'braintree'],
            'mastercard': ['adyen', 'stripe', 'square', 'braintree'],
            'amex': ['braintree', 'paypal', 'stripe'],
            'discover': ['stripe', 'adyen', 'square']
        }

        self.retriable_codes = {
            'decline_codes.processor_unavailable',
            'decline_codes.processing_error',
            'decline_codes.timeout',
            'decline_codes.try_again',
            'decline_codes.authentication_required'
        }

    def should_fallback(self, decline_reason):
        return decline_reason in self.retriable_codes

    def process_with_fallback(self, payment_data, card_brand):
        processors = self.fallback_chains.get(card_brand, ['stripe', 'adyen'])

        for processor in processors:
            try:
                result = self.charge_with_processor(processor, payment_data)

                if result['success']:
                    return {
                        'success': True,
                        'processor': processor,
                        'transaction_id': result['transaction_id'],
                        'attempt': processors.index(processor) + 1
                    }

                # Check if we should try next processor
                if not self.should_fallback(result.get('decline_reason')):
                    # Hard decline, don't retry
                    return result

            except Exception as e:
                # Processor error, try next
                logger.warning(f'{processor} failed: {str(e)}')
                continue

        # All processors exhausted
        return {
            'success': False,
            'error': 'All processors declined',
            'attempts': len(processors)
        }

    def charge_with_processor(self, processor, payment_data):
        if processor == 'stripe':
            return charge_via_stripe(payment_data)
        elif processor == 'adyen':
            return charge_via_adyen(payment_data)
        # ... other processors
```

## Risk-Based Routing

### Fraud Risk Assessment

```
Risk Score Calculation:
- Customer history (0-100 points)
- Device risk (0-50 points)
- Geographic risk (0-50 points)
- Transaction patterns (0-50 points)
- Network risk (0-50 points)

Total Risk Score: 0-300 (higher = more risk)

Risk Tiers:
- 0-50: Low risk (approve without 3DS)
- 51-150: Medium risk (optional 3DS)
- 151-250: High risk (require 3DS)
- 251+: Very High risk (require additional auth or decline)

Risk-Based Processing:
if risk_score < 50:
    # Low risk
    execute_transaction()
elif risk_score < 150:
    # Medium risk
    offer_3ds_if_high_value()
elif risk_score < 250:
    # High risk
    require_3ds()
    require_cvc_retry()
else:
    # Very high risk
    hold_for_manual_review()
    send_verification_email()
    decline_and_suggest_retry()
```

### 3D Secure Decision

```
3D Secure Routing Strategy:

When to Trigger 3DS:
- Risk score > 150
- Amount > $500
- New card (first transaction)
- Unusual location
- Suspicious patterns
- Regulatory requirement (SCA in EU)

3DS Flow:
1. Check if card supports 3DS
2. Send 3DS authentication request
3. Customer completes authentication
4. Receive 3DS result
5. Attempt transaction with 3DS liability shift

Example (Python):
class ThreeDSOrchestrator:
    def should_require_3ds(self, payment, risk_score):
        # Always 3DS for high risk
        if risk_score > 250:
            return True

        # 3DS for large amounts
        if payment['amount'] > 500:
            return True

        # 3DS for new customers
        if payment['is_first_transaction']:
            return True

        # 3DS for specific regions (SCA - Strong Customer Auth)
        if payment['country'] in self.sca_required_countries:
            return True

        # Optional 3DS for medium risk
        if risk_score > 150 and payment['amount'] > 100:
            return True

        return False

    def process_with_3ds(self, payment_data):
        # Check 3DS availability
        if not self.supports_3ds(payment_data['card_brand']):
            return self.process_without_3ds(payment_data)

        # Initiate 3DS
        three_ds_response = self.initiate_3ds(payment_data)

        if three_ds_response['requires_action']:
            return {
                'requires_3ds': True,
                'redirect_url': three_ds_response['acs_url'],
                'challenge_id': three_ds_response['challenge_id']
            }

        # Process with 3DS result
        transaction = self.charge_with_3ds_data(
            payment_data,
            three_ds_response['eci'],
            three_ds_response['cavv']
        )

        return transaction
```

## Processor Performance Monitoring

### Metrics Tracking

```
Key Metrics Per Processor:

1. Success Rate (Authorization)
   - % of transactions approved
   - Target: 95%+
   - Tracks processor quality

2. Response Time (TTL)
   - Average time to response
   - Target: <500ms
   - Impacts customer experience

3. Cost (Interchange + Fees)
   - Average cost per transaction
   - Target: Minimize
   - Impacts margins

4. Fraud Rate
   - % transactions that become fraud
   - Target: <0.1%
   - Impacts risk

5. Decline Rate by Code
   - Insufficient funds
   - Card expired
   - Rate limit hit
   - Authentication required

Monitoring Dashboard:
{
  'processor': 'stripe',
  'period': '2024-01-15',
  'transactions': {
    'total': 10000,
    'successful': 9750,
    'declined': 250,
    'errors': 0
  },
  'success_rate': 0.975,
  'response_time_ms': 245,
  'fraud_rate': 0.00095,
  'decline_reasons': {
    'insufficient_funds': 100,
    'card_expired': 50,
    'rate_limit': 25,
    'authentication_required': 75
  },
  'cost': {
    'interchange': 2450.00,
    'assessment_fees': 350.00,
    'processing_fees': 175.00,
    'total': 2975.00,
    'cost_per_transaction': 0.2975
  },
  'trend': 'up'  // improving
}
```

### Processor Health Checks

```
Automated Monitoring:

Periodic Health Check:
- Test transaction to each processor (low amount)
- Verify connection and response
- Monitor response time
- Check for degradation

Alert Conditions:
- Success rate drop below 90%
- Response time > 2 seconds
- Processor returns 5xx errors
- Rate limiting triggered
- Network connectivity issues

Example Health Check (Python):
class ProcessorHealthMonitor:
    def health_check(self, processor):
        test_payment = {
            'amount': 1.00,  # Low amount
            'currency': 'USD',
            'card_token': 'tok_test',
            'merchant_id': 'health_check'
        }

        start_time = time.time()

        try:
            result = self.charge_with_processor(processor, test_payment)
            elapsed = time.time() - start_time

            return {
                'processor': processor,
                'status': 'healthy' if result['success'] else 'degraded',
                'response_time_ms': elapsed * 1000,
                'is_available': True,
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'processor': processor,
                'status': 'unhealthy',
                'error': str(e),
                'is_available': False,
                'timestamp': datetime.now()
            }

    def monitor_all_processors(self, processors):
        health_status = {}
        for processor in processors:
            health_status[processor] = self.health_check(processor)

        # Alert if any processor unhealthy
        for processor, status in health_status.items():
            if status['status'] != 'healthy':
                self.send_alert(f'{processor} is {status["status"]}')

        return health_status
```

## Dynamic Routing Adjustment

### Learning from Outcomes

```
Real-Time Adjustment:

Transaction Outcome Feedback:
1. Transaction attempted
2. Result captured (approved/declined)
3. Actual fraud indicator tracked
4. Processor performance updated
5. Routing weights adjusted

Example:
- Processor A: 96% success, cost $0.30, fraud 0.1%
- Processor B: 92% success, cost $0.25, fraud 0.08%

Initial weight: A = 0.6, B = 0.4
After 1000 transactions:
- A: 960 successes, $300 cost
- B: 920 successes, $250 cost

Adjusted weight: A = 0.55, B = 0.45  (B improving)

If B continues strong, weight becomes: A = 0.5, B = 0.5
Eventually: A = 0.4, B = 0.6 if B maintains advantage
```

### Processor Hot-Swapping

```
Scenario: Processor Degradation
1. Monitor detects success rate drop
2. Automatic weight reduction
3. Route traffic to other processors
4. User not impacted
5. No manual intervention needed

Example:
- Stripe suddenly has 80% success (normal 96%)
- System detects issue
- Stripe weight reduced from 60% to 20%
- Traffic automatically routes to Adyen/Square
- User experience unchanged
- Stripe still gets 20% (for diversity)
- Once recovered, weight increases again
```

## Cost Optimization

### Interchange Routing

```
Optimize Based on Interchange Categories:

Visa Qualified (0.05% + $0.21):
- Signature debit card
- PIN debit card
- Route to Stripe/Square (best for debit)

Visa Mid-Qualified (1.51% + $0.95):
- Standard credit card transactions
- Route based on processor strength

Visa Non-Qualified (2.51% + $0.95):
- Corporate cards
- Rewards cards
- International
- Route to processor with best acceptance

Optimization Algorithm:
for each processor:
    expected_cost = (
        interchange_rate * amount +
        processor_fee +
        other_fees
    ) * (1 - success_rate)  // Factor in failures

select processor with lowest expected cost
```

### Volume Discounts

```
Negotiate Based on Volume:

Tier Structure:
- < $100k/month: Standard rates
- $100k-$500k/month: 10-15% discount
- $500k-$1m/month: 15-25% discount
- > $1m/month: 25-40% discount

Processor Diversification:
- Split volume across processors
- Maintain competition
- Prevent processor lock-in
- Improve negotiating power

Example:
Monthly Volume: $1.5m
- Stripe: 40% ($600k) -> 2.15% rate
- Adyen: 35% ($525k) -> 2.10% rate
- Square: 25% ($375k) -> 2.25% rate

vs.

100% to one processor:
- Single processor at 2.35% rate

Diversified saves: ~0.10% = $1,500/month
Annual savings: $18,000
```
