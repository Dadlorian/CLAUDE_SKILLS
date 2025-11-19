# Building a Payment Gateway Guide

## Architecture Overview

A payment gateway is a software service that enables merchants to accept electronic payments. It serves as the bridge between the merchant's website/app and payment processors, acquiring banks, and payment networks.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│ Merchant Website / Mobile App                           │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────v───────────────────────────┐
│ Payment Gateway (Your Service)                           │
│ ├─ Payment Form / UI                                     │
│ ├─ PCI Tokenization Engine                              │
│ ├─ Request Router & Orchestration                       │
│ ├─ Risk & Fraud Assessment                              │
│ └─ State Management & Persistence                       │
└─────────────────────────────┬───────────────────────────┘
        │           │              │
        v           v              v
    ┌─────┐   ┌──────┐   ┌──────────┐
    │Stripe│  │Adyen │  │PayPal    │
    └─────┘   └──────┘   └──────────┘
        │           │              │
        └───────────┬──────────────┘
                    v
        ┌──────────────────────┐
        │ Payment Networks     │
        │ (Visa, MC, Amex)     │
        └──────────────────────┘
```

### 1. Tokenization Layer

**Purpose**: Collect card data securely without merchant storing PAN

```python
# Tokenization endpoint (Python/Flask example)
@app.route('/tokenize', methods=['POST'])
def tokenize_card():
    """
    Securely tokenize card data without storing PAN
    """
    try:
        card_data = {
            'number': request.json['cardNumber'],
            'exp_month': request.json['expiryMonth'],
            'exp_year': request.json['expiryYear'],
            'cvc': request.json['cvv']
        }

        # Validate card format
        if not validate_card_number(card_data['number']):
            return jsonify({'error': 'Invalid card number'}), 400

        # Call payment processor's tokenization endpoint
        processor_response = requests.post(
            'https://api.processor.com/tokens',
            json=card_data,
            headers={'Authorization': f'Bearer {PROCESSOR_API_KEY}'}
        )

        token_data = processor_response.json()

        return jsonify({
            'token': token_data['token'],
            'last_four': card_data['number'][-4:],
            'brand': detect_card_brand(card_data['number']),
            'expiry': f"{card_data['exp_month']}/{card_data['exp_year']}"
        })

    except Exception as e:
        logger.error(f'Tokenization failed: {str(e)}')
        return jsonify({'error': 'Tokenization failed'}), 500
```

### 2. Request Router & Orchestration

**Purpose**: Route transactions to optimal processor

```python
class PaymentRouter:
    def __init__(self):
        self.processors = {
            'stripe': StripeProcessor(),
            'adyen': AdyenProcessor(),
            'square': SquareProcessor()
        }

    def route_payment(self, payment_data):
        """
        Intelligently route payment to best processor
        """
        # Apply routing rules
        processor_name = self.select_processor(payment_data)
        processor = self.processors[processor_name]

        # Execute payment
        result = processor.authorize(payment_data)

        # Fallback if needed
        if not result['success'] and self.should_fallback(result):
            fallback_name = self.get_fallback_processor(processor_name)
            processor = self.processors[fallback_name]
            result = processor.authorize(payment_data)

        # Record transaction
        self.record_transaction(payment_data, result)

        return result

    def select_processor(self, payment_data):
        """Select best processor for transaction"""
        card_brand = payment_data['card_brand']
        amount = payment_data['amount']
        country = payment_data['country']

        if card_brand == 'amex':
            return 'square'  # Best Amex processor
        elif amount > 1000 and country == 'US':
            return 'stripe'  # Stripe best for high-value US
        elif country in ['DE', 'FR', 'GB']:
            return 'adyen'  # Adyen best for EU
        else:
            return 'stripe'  # Default

    def should_fallback(self, result):
        """Determine if transaction should fallback"""
        retryable_codes = [
            'decline_codes.processor_unavailable',
            'decline_codes.timeout',
            'decline_codes.try_again'
        ]
        return result.get('code') in retryable_codes
```

### 3. Risk & Fraud Assessment

**Purpose**: Evaluate transaction risk and determine authentication requirements

```python
class FraudDetector:
    def assess_transaction_risk(self, transaction):
        """
        Calculate fraud risk score (0-300)
        """
        score = 0

        # Customer risk (0-100)
        if not transaction['customer_id']:
            score += 50  # New customer
        else:
            customer_history = self.get_customer_history(transaction['customer_id'])
            if customer_history['chargebacks'] > 0.02:
                score += 40  # High chargeback history
            elif customer_history['transaction_count'] > 10:
                score += 0   # Trusted customer
            else:
                score += 20  # New customer

        # Device risk (0-100)
        device = transaction['device']
        if device['is_vpn']:
            score += 30
        if device['is_proxy']:
            score += 40
        if device['is_new_to_customer']:
            score += 25

        # Geographic risk (0-100)
        if transaction['country'] in HIGH_RISK_COUNTRIES:
            score += 40
        if transaction['billing_country'] != transaction['shipping_country']:
            score += 20

        # Velocity risk (0-50)
        velocity = self.calculate_velocity(transaction['customer_id'])
        if velocity['transactions_last_hour'] > 5:
            score += 30
        if velocity['transactions_last_day'] > 20:
            score += 20

        return score

    def get_authentication_requirement(self, risk_score):
        """Determine if 3DS is required based on risk"""
        if risk_score > 250:
            return 'REQUIRED'  # Force 3DS authentication
        elif risk_score > 150:
            return 'RECOMMENDED'  # Offer 3DS
        else:
            return 'OPTIONAL'  # User choice
```

### 4. State Management & Persistence

**Purpose**: Track payment state through lifecycle

```python
class PaymentStateMachine:
    """
    Payment states: PENDING -> AUTHORIZED -> CAPTURED -> SETTLED
    """

    def create_payment(self, payment_data):
        """Create new payment record"""
        payment = {
            'id': generate_idempotency_id(),
            'created_at': datetime.now(),
            'status': 'PENDING',
            'merchant_id': payment_data['merchant_id'],
            'amount': payment_data['amount'],
            'currency': payment_data['currency'],
            'metadata': payment_data.get('metadata', {})
        }

        # Store in database
        db.payments.insert_one(payment)
        return payment

    def authorize_payment(self, payment_id, auth_result):
        """Move to AUTHORIZED state"""
        db.payments.update_one(
            {'id': payment_id},
            {
                '$set': {
                    'status': 'AUTHORIZED',
                    'authorization_code': auth_result['auth_code'],
                    'processor': auth_result['processor'],
                    'network_reference': auth_result['network_ref'],
                    'authorized_at': datetime.now()
                }
            }
        )

    def capture_payment(self, payment_id):
        """Move to CAPTURED state (ready for settlement)"""
        payment = db.payments.find_one({'id': payment_id})

        if payment['status'] != 'AUTHORIZED':
            raise PaymentException('Payment not authorized')

        processor = self.get_processor(payment['processor'])
        capture_result = processor.capture(payment)

        db.payments.update_one(
            {'id': payment_id},
            {
                '$set': {
                    'status': 'CAPTURED',
                    'captured_at': datetime.now()
                }
            }
        )

        return capture_result

    def get_payment_status(self, payment_id):
        """Get current payment status"""
        return db.payments.find_one({'id': payment_id})
```

## Implementation Best Practices

### 1. Idempotency

```python
def process_payment(idempotency_key, payment_data):
    """
    Ensure payment can be safely retried
    """
    # Check if already processed
    existing = db.payments.find_one({'idempotency_key': idempotency_key})
    if existing:
        return existing  # Return same result

    # Process payment
    try:
        result = execute_authorization(payment_data)

        # Store with idempotency key
        payment = {
            'idempotency_key': idempotency_key,
            'result': result,
            'created_at': datetime.now()
        }
        db.payments.insert_one(payment)

        return result

    except Exception as e:
        logger.error(f'Payment failed: {str(e)}')
        raise
```

### 2. Circuit Breaker

```python
class CircuitBreaker:
    """
    Prevent cascading failures when processor is down
    """

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.is_open():
            raise ProcessorUnavailable('Circuit breaker open')

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def is_open(self):
        if self.failure_count >= self.failure_threshold:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed < self.timeout:
                return True
            else:
                self.failure_count = 0  # Reset
        return False

    def on_success(self):
        self.failure_count = 0

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
```

### 3. Webhook Handling

```python
@app.route('/webhooks/payment', methods=['POST'])
def handle_webhook():
    """
    Receive payment status updates from processor
    """
    payload = request.get_json()

    # Verify signature
    if not verify_webhook_signature(payload, request.headers):
        return jsonify({'error': 'Invalid signature'}), 401

    # Process by type
    event_type = payload['type']

    if event_type == 'payment.authorized':
        handle_authorization(payload)
    elif event_type == 'payment.captured':
        handle_capture(payload)
    elif event_type == 'payment.failed':
        handle_failure(payload)
    elif event_type == 'chargeback.initiated':
        handle_chargeback(payload)

    return jsonify({'status': 'received'}), 200

def verify_webhook_signature(payload, headers):
    """Verify processor signature"""
    signature = headers.get('X-Signature')
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)
```

## Key Metrics

```
Payment Gateway Health:
- Success Rate: % of transactions approved (target: 95%+)
- Response Time: Average authorization time (target: <500ms)
- Availability: % of time system operational (target: 99.9%)
- Fraud Rate: % fraudulent transactions (target: <0.1%)
- Chargeback Rate: % disputed transactions (target: <0.5%)
- PCI Compliance: % of requirements met (target: 100%)

Monitoring:
- Real-time alerts for errors
- Daily success rate tracking
- Weekly processor comparison
- Monthly fraud analysis
- Quarterly compliance audit
```
