# Payment Routing Reference

## Overview

Payment routing is the intelligent selection and delivery of payment transactions through optimal pathways to maximize success rates, minimize costs, and ensure reliable processing. Critical infrastructure for modern payment systems.

## Routing Principles

### Core Routing Objectives

```
1. Success Rate Optimization (Primary)
   - Maximize approval % for transactions
   - Reduce decline rate
   - Improve customer experience
   - Minimize failed transaction retries

2. Cost Minimization
   - Lowest cost processor for transaction type
   - Optimal interchange category selection
   - Avoid unnecessary premium fees
   - Volume discount optimization

3. Risk Management
   - Fraud detection and prevention
   - Chargeback minimization
   - Compliance with regulations
   - Secure transaction handling

4. Speed Optimization
   - Minimize latency
   - Improve customer experience
   - Real-time processing where possible
   - Fallback speed optimization

Balance Trade-offs:
- Low-cost might mean lower success rate
- Highest success rate might be highest cost
- Find optimal trade-off for business
- Different strategies by segment
```

### Routing Rules Engine

```
Rule Hierarchy:
1. Merchant-Specific Rules (Highest Priority)
   - Override all other rules
   - Exclusions and preferences
   - Contract-specific requirements
   - Example: "Always use Stripe for this merchant"

2. Customer Segment Rules
   - By customer tier (VIP, premium, standard)
   - By customer geography
   - By customer history
   - Example: "VIPs get fastest processor"

3. Transaction-Specific Rules
   - By amount range
   - By payment method (card type)
   - By transaction type (3DS, recurring)
   - Example: "Debit transactions to Stripe"

4. Network/Scheme Rules
   - By card brand (Visa, MC, Amex)
   - By issuer country
   - By transaction geography
   - Example: "Amex transactions to Braintree"

5. Default Rules (Lowest Priority)
   - Fallback for unmatched transactions
   - Standard processor and settings

Example Rule Set:
```
IF merchant_id = "GOLD_CLIENT"
  THEN use_processor = "stripe" OR "adyen"  // Preferred
  ELSE continue_to_next_rule

IF customer_lifetime_value > $100,000
  AND transaction_amount > $1,000
  THEN use_processor = "adyen"  // Better for high-value
  ELSE continue_to_next_rule

IF card_brand = "amex"
  THEN use_processor = "braintree"  // Amex specialist
  ELSE continue_to_next_rule

IF card_brand = "visa" AND country = "US"
  THEN use_processor = "stripe"  // Visa strength
  ELSE continue_to_next_rule

IF transaction_amount < $100 AND card_brand = "debit"
  THEN use_processor = "square"  // Debit strength
  ELSE continue_to_next_rule

DEFAULT use_processor = "stripe"  // Default fallback
```

## Routing Strategies

### Geographic Routing

```
Local Processor Advantage:
- Processor with local presence better approval rates
- Local customer understanding
- Regional compliance expertise
- Network relationships in region

Example Strategy:

US Transactions:
- Stripe (strong in US)
- Square (US-based)
- Success rate: 96-97%

EU Transactions:
- Adyen (EU-based)
- Strong SCA/3DS capabilities
- PSD2 expertise
- Success rate: 94-95%

Asia Transactions:
- Adyen (global coverage)
- Local partners
- Regional payment methods
- Success rate: 90-92%

Implementation:
```
function selectProcessorByRegion(country, cardBrand) {
  const regionProcessors = {
    'US': ['stripe', 'square', 'paypal'],
    'CA': ['stripe', 'square', 'paysafe'],
    'EU': ['adyen', 'stripe', 'worldpay'],
    'ASIA': ['adyen', 'stripe', 'global_payment'],
    'AU': ['stripe', 'adyen', 'square']
  };

  const processors = regionProcessors[country];

  // Filter by card brand strength
  if (cardBrand === 'amex') {
    return processors.filter(p => p !== 'square')[0];  // Square weak on Amex
  }

  return processors[0];  // Return first (best) option
}
```
```

### Payment Method Routing

```
Card Type Specialization:

Debit Cards:
- Square: Excellent (US debit strength)
- Stripe: Good
- Success rate: 97-98%

Credit Cards:
- Stripe: Excellent
- Adyen: Excellent
- PayPal: Good
- Success rate: 95-96%

American Express:
- Braintree: Excellent (Amex owned)
- PayPal: Excellent
- Stripe: Good
- Success rate: 92-94%

Digital Wallets (Apple Pay, Google Pay):
- Stripe: Excellent
- Square: Excellent
- PayPal: Good
- Success rate: 97-99% (wallet already authorized)

Bank Transfers/ACH:
- Adyen: Good
- Stripe: Good
- Dedicated ACH processor: Best
- Success rate: 98-99%

Routing Implementation:
```
SELECT processor
FROM processor_capabilities
WHERE card_type = :card_type
  AND region = :region
  AND processor_success_rate > 95%
ORDER BY avg_cost ASC
LIMIT 1;
```
```

## Smart Routing Algorithms

### Weighted Scoring

```
Multiple Factor Scoring:

Factors and Weights:
- Success Rate: 40% weight
- Processing Cost: 30% weight
- Transaction Speed: 20% weight
- Fraud Rate: 10% weight

Calculation:
score = (success_rate * 0.4) +
        (cost_score * 0.3) +
        (speed_score * 0.2) +
        (fraud_score * 0.1)

Example Calculation:
Processor A:
- Success rate: 96% (score: 96 * 0.4 = 38.4)
- Cost: $0.30 per transaction (normalized score: 90 * 0.3 = 27.0)
- Speed: 245ms (normalized score: 85 * 0.2 = 17.0)
- Fraud rate: 0.08% (normalized score: 92 * 0.1 = 9.2)
- Total Score: 91.6

Processor B:
- Success rate: 94% (score: 94 * 0.4 = 37.6)
- Cost: $0.25 per transaction (normalized score: 95 * 0.3 = 28.5)
- Speed: 180ms (normalized score: 98 * 0.2 = 19.6)
- Fraud rate: 0.05% (normalized score: 98 * 0.1 = 9.8)
- Total Score: 95.5

Winner: Processor B (faster, cheaper, lower fraud)

Implementation (Python):
def calculate_processor_score(processor_metrics):
    weights = {
        'success_rate': 0.4,
        'cost': 0.3,
        'speed': 0.2,
        'fraud_rate': 0.1
    }

    # Normalize scores to 0-100
    success_score = processor_metrics['success_rate'] * 100
    cost_score = (100 - (processor_metrics['cost_per_txn'] * 100))
    speed_score = max(0, 100 - (processor_metrics['avg_latency_ms'] / 10))
    fraud_score = max(0, 100 - (processor_metrics['fraud_rate'] * 1000))

    total_score = (
        success_score * weights['success_rate'] +
        cost_score * weights['cost'] +
        speed_score * weights['speed'] +
        fraud_score * weights['fraud_rate']
    )

    return total_score
```

### Machine Learning Routing

```
Model-Based Selection:

Input Features:
- Card type and brand
- Transaction amount
- Merchant category
- Customer history
- Device characteristics
- Geographic information
- Time of day
- Transaction velocity
- Customer risk score

Target: Processor selection that maximizes success rate

Training Data:
- 1 year of historical transactions
- 100,000+ transactions
- Success/failure outcome
- Processor used

Model Types:
- Classification (select best processor)
- Probability (predict success per processor)
- Multi-armed bandit (explore vs. exploit)

Example (Python with scikit-learn):
```
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class ProcessorSelectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.processor_mapping = {
            0: 'stripe',
            1: 'adyen',
            2: 'square',
            3: 'braintree',
            4: 'paypal'
        }

    def train(self, X_historical, y_successful_processor):
        """
        X_historical: Features from past transactions
        y_successful_processor: Which processor resulted in approval
        """
        self.model.fit(X_historical, y_successful_processor)
        joblib.dump(self.model, 'processor_model.pkl')

    def predict_best_processor(self, transaction_features):
        """
        Predict the best processor for new transaction
        """
        features = np.array([transaction_features])
        prediction = self.model.predict(features)[0]
        confidence = self.model.predict_proba(features)[0].max()

        processor = self.processor_mapping[prediction]

        return {
            'processor': processor,
            'confidence': confidence,
            'prediction_index': prediction
        }

    def predict_all_probabilities(self, transaction_features):
        """
        Get success probability for all processors
        """
        features = np.array([transaction_features])
        probabilities = self.model.predict_proba(features)[0]

        results = {}
        for idx, processor in self.processor_mapping.items():
            results[processor] = probabilities[idx]

        return sorted(results.items(), key=lambda x: x[1], reverse=True)

# Usage
model = ProcessorSelectionModel()

# Training (done offline)
# model.train(X_historical_data, y_successful_processors)

# Inference (real-time)
transaction_features = [
    amount,
    card_brand_encoded,
    merchant_category_encoded,
    customer_risk_score,
    device_risk_score,
    latitude,
    longitude,
    hour_of_day,
    day_of_week,
    transaction_velocity
]

best_processor = model.predict_best_processor(transaction_features)
print(f"Recommended: {best_processor['processor']} "
      f"({best_processor['confidence']:.2%} confidence)")

# Alternative: See all options
all_options = model.predict_all_probabilities(transaction_features)
for processor, prob in all_options:
    print(f"{processor}: {prob:.2%}")
```
```

### Dynamic A/B Testing

```
Online Learning Approach:

Setup:
- Test new processor or strategy
- Route percentage of traffic to test
- Measure success rate
- Compare to control (existing processor)
- Gradually increase winner

Example:
Day 1-3: Test new processor with 5% of traffic
- Stripe (control): 96% success (95% of traffic)
- Adyen (test): 94% success (5% of traffic)
- Result: Keep control

Day 4-6: Test different processor with 5%
- Stripe (control): 96% success (95%)
- Square (test): 97% success (5%)
- Result: Square winning! Increase to 10%

Day 7-14: Continue testing
- Stripe (control): 96% success (90%)
- Square (test): 97% success (10%)
- Confidence threshold reached: Switch to 50/50

Day 15-30: Confidence testing
- Stripe: 96% success (50%)
- Square: 97% success (50%)
- Result: Switch to Square as primary, Stripe as secondary

Impact:
- 1% success improvement
- Process: Safe gradual rollout
- Risk: Minimal downside
- Benefit: Data-driven optimization

Implementation:
```
def route_with_ab_test(transaction):
    control_processor = 'stripe'
    test_processor = 'square'
    test_percentage = 0.05  # 5% to test

    if random.random() < test_percentage:
        # Route to test processor
        return test_processor
    else:
        # Route to control
        return control_processor

# After collecting data:
def evaluate_test_performance():
    control_success = db.query('''
        SELECT COUNT(CASE WHEN status='SUCCESS')
        FROM transactions
        WHERE processor='stripe'
    ''')

    test_success = db.query('''
        SELECT COUNT(CASE WHEN status='SUCCESS')
        FROM transactions
        WHERE processor='square'
    ''')

    control_rate = control_success / total_control
    test_rate = test_success / total_test

    # Statistical significance test
    from scipy.stats import chi2_contingency
    contingency = [[control_success, control_failed],
                   [test_success, test_failed]]

    chi2, p_value, dof, expected = chi2_contingency(contingency)

    if p_value < 0.05 and test_rate > control_rate:
        return 'SWITCH_TO_TEST'
    else:
        return 'KEEP_CONTROL'
```
```

## Processor Failover

### Primary-Secondary Routing

```
Configuration:
Primary Processor: Stripe
Secondary Processor: Adyen (if Stripe fails)
Tertiary Processor: Square (if both fail)

Failover Triggers:
- Processor returns error (5xx, timeout)
- Response time exceeds threshold
- Success rate drops below threshold
- Network connectivity issues

Automatic Failover:
```
def route_with_fallback(transaction, processors_priority):
    for processor in processors_priority:
        try:
            result = charge_with_processor(processor, transaction)

            if result['success']:
                return {
                    'processor': processor,
                    'result': result
                }

            # Check if error is retryable
            if result.get('retryable'):
                continue
            else:
                # Hard decline, don't fallback
                return {
                    'processor': processor,
                    'result': result
                }

        except TimeoutError:
            # Timeout, try next processor
            logger.warning(f'{processor} timed out')
            continue

        except ProcessorUnavailable:
            # Processor down, try next
            logger.warning(f'{processor} unavailable')
            continue

    # All processors failed
    return {
        'success': False,
        'error': 'All processors unavailable'
    }

# Usage
processors = ['stripe', 'adyen', 'square']
result = route_with_fallback(transaction_data, processors)
```

Manual Failover:
- Monitoring alerts on processor health
- Admin notified of failures
- Manual route adjustment possible
- Grace period: 5-15 minutes before switching
```

### Health Checks and Monitoring

```
Health Check Interval:
- Every 60 seconds for active processors
- Every 5 minutes for backup processors
- More frequent during peak hours

Health Checks Include:
- Connectivity test (ping)
- Test transaction (low amount)
- Response time measurement
- Error rate measurement
- Current rate retrievals

Metrics Tracked:
- Availability %
- Response time (p50, p95, p99)
- Error rate %
- Success rate %
- Last health check time

Alerting:
- Availability < 95%: Warning
- Availability < 90%: Critical
- Response time > 2s: Warning
- Success rate < 90%: Warning

Dashboard:
```
Processor Status Dashboard:
┌─────────────────────────────────────┐
│ Processor │ Status │ Availability │ │
├─────────────────────────────────────┤
│ Stripe    │ ✓ LIVE │ 99.8%       │ │
│ Adyen     │ ✓ LIVE │ 99.5%       │ │
│ Square    │ ⚠ SLOW │ 99.2%       │ │
│ Braintree │ ✗ DOWN │ 0%          │ │
└─────────────────────────────────────┘

Last Updated: 2024-01-15 10:30:45
Success Rates (24h):
  Stripe: 96.2%
  Adyen: 94.8%
  Square: 93.5%
  Braintree: [OFFLINE]
```
```

## Cost-Based Routing

### Interchange Optimization

```
Card Categorization:

Qualified (0.05% + $0.21):
- Signature debit
- Pin debit
- Target: Stripe, Square for debit strength

Mid-Qualified (1.51% + $0.95):
- Standard cards
- Most credit cards
- Visa/Mastercard standard

Non-Qualified (2.51% + $0.95):
- Corporate cards
- Rewards cards
- International transactions

Routing by Category:
```
if (card_type == 'debit' && transaction_type == 'pinless_debit'):
  processor = 'square'  // Best interchange rates
elif (card_brand == 'amex'):
  processor = 'braintree'  // Amex strength
elif (amount > $5000):
  processor = 'adyen'  // Better for high-value
else:
  processor = 'stripe'  // Default
```

Cost Tracking:
- Publish daily processor cost comparison
- Optimize routing weekly based on costs
- Negotiate volume discounts with processors
- Pass savings back to merchants
```

### Dynamic Pricing

```
Incentive-Based Routing:
- Offer better pricing to merchants who use best processors
- Create incentives for cost-optimized routing
- Margin improvement through routing

Example:
Standard pricing: 2.9% + $0.30

Optimized routing:
- If routed to Stripe for visa: 2.79% (10bps discount)
- If routed to Square for debit: 2.69% (20bps discount)
- If routed to Adyen for international: 2.89% (10bps discount)

Merchant sees:
- Better rates for optimized routing
- Automatic savings
- Transparent pricing
- Incentive to use our platform for better rates
```
