# Payment API Integration Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication Mechanisms](#authentication-mechanisms)
3. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
4. [Idempotency and Retry Logic](#idempotency-and-retry-logic)
5. [Error Handling](#error-handling)
6. [Webhook Patterns](#webhook-patterns)
7. [Stripe API Examples](#stripe-api-examples)
8. [Security Best Practices](#security-best-practices)
9. [Compliance Requirements](#compliance-requirements)

---

## Introduction

Payment API integration is critical for modern financial applications. This guide covers industry standards and best practices for integrating payment processors like Stripe, with emphasis on security, reliability, and compliance.

Payment APIs handle sensitive financial data and must adhere to PCI-DSS, GDPR, and other regulatory frameworks.

---

## Authentication Mechanisms

### 1. API Key Authentication

API keys are the primary authentication method for most payment APIs.

#### API Key Structure and Management

API Keys have three components:
- **Public Key**: Used in client-side operations (safe to expose)
- **Secret Key**: Used in server-side operations (must be kept confidential)
- **Restricted Key**: Limited permission keys for specific operations

#### Implementation Pattern

```javascript
// Node.js - Stripe Example
const stripe = require('stripe')('sk_live_your_secret_key', {
  apiVersion: '2024-04-10',
  httpClient: stripe.createFetchHttpClient(),
  timeout: 30000,
  maxNetworkRetries: 3
});

// Headers Configuration
const headers = {
  'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}`,
  'Content-Type': 'application/json',
  'Idempotency-Key': generateUUID(),
  'User-Agent': 'MyPaymentApp/1.0'
};
```

#### Key Rotation Strategy

```yaml
Key Rotation Policy:
  Frequency: Quarterly (or upon compromise)
  Process:
    1. Generate new API key in dashboard
    2. Update in secure vault/secrets manager
    3. Deploy to all services
    4. Monitor for failures (1-2 week window)
    5. Rotate again if issues occur
    6. Revoke old key after confirmation

  Emergency Rotation:
    - Immediate key rotation upon suspected compromise
    - Audit logs for unauthorized access
    - Notify affected customers
    - Regenerate session tokens
```

#### Key Storage Best Practices

```python
# GOOD: Using environment variables with secrets manager
import os
from aws_secretsmanager import SecretsManager

secrets_client = SecretsManager()
secret = secrets_client.get_secret_value(
    SecretId='payment-api-keys'
)
api_key = secret['SecretString']['stripe_secret_key']

# GOOD: Using hashicorp vault
import hvac

client = hvac.Client(url='https://vault.company.com', 
                     token=os.environ['VAULT_TOKEN'])
secret = client.secrets.kv.v2.read_secret_version(
    path='payment/stripe'
)
api_key = secret['data']['data']['secret_key']

# BAD: Hardcoding keys
api_key = 'sk_live_1234567890'  # NEVER DO THIS

# BAD: Storing in git
git add api_keys.json  # NEVER COMMIT KEYS
```

### 2. OAuth 2.0 Authentication

OAuth 2.0 is used for delegated access and third-party integrations.

#### OAuth 2.0 Flow Implementation

The Authorization Code Flow is most commonly used for payment account connections:

1. **User initiates connection** to Stripe Account
2. **Redirect to authorization endpoint** with client_id, state, and redirect_uri
3. **User approves** the connection on Stripe
4. **Redirect back** with authorization code
5. **Exchange code** for access token using client_secret
6. **Store tokens** securely and use for API calls

#### OAuth Implementation Example

```python
import hashlib
import secrets
import requests
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

STRIPE_CLIENT_ID = os.environ['STRIPE_CLIENT_ID']
STRIPE_CLIENT_SECRET = os.environ['STRIPE_CLIENT_SECRET']
REDIRECT_URI = 'https://yourapp.com/oauth/callback'

@app.route('/connect-stripe')
def connect_stripe():
    """Initiate OAuth flow"""
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    auth_url = (
        f'https://connect.stripe.com/oauth/authorize'
        f'?client_id={STRIPE_CLIENT_ID}'
        f'&state={state}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope=read_write'
    )
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')

    # Validate state parameter (CSRF protection)
    if state != session.get('oauth_state'):
        return {'error': 'Invalid state parameter'}, 400

    # Exchange code for access token
    try:
        response = requests.post(
            'https://connect.stripe.com/oauth/token',
            data={
                'client_id': STRIPE_CLIENT_ID,
                'client_secret': STRIPE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            },
            timeout=10
        )
        response.raise_for_status()
        token_data = response.json()

        # Store securely
        store_oauth_token(
            user_id=get_current_user_id(),
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            stripe_account_id=token_data['stripe_user_id'],
            scope=token_data['scope']
        )

        return redirect('/dashboard?success=true')
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500
```

### 3. Mutual TLS (mTLS) Authentication

mTLS provides bidirectional certificate-based authentication for enhanced security.

```python
import requests

# mTLS Configuration
mTLS_config = {
    'cert': ('/path/to/client-cert.pem', '/path/to/client-key.pem'),
    'verify': '/path/to/ca-bundle.pem'
}

# API call with mTLS
session = requests.Session()
session.cert = mTLS_config['cert']
session.verify = mTLS_config['verify']

response = session.post(
    'https://secure-api.stripe.com/v1/charges',
    json={
        'amount': 2000,
        'currency': 'usd',
        'source': 'tok_visa'
    },
    timeout=30
)
```

#### Certificate Management

```yaml
Certificate Lifecycle:
  Generation:
    - Create CSR with payment provider
    - Get signed certificate from their CA
    - Store securely in secrets manager

  Rotation:
    - Generate new certificate 30 days before expiry
    - Deploy to all instances
    - Keep old certificate active for 7-14 days overlap
    - Monitor both certs in use
    - Retire old certificate after successful transition

  Storage:
    - Never commit to version control
    - Store in AWS SecretsManager/HashiCorp Vault
    - Use separate certs per environment
    - Encrypt at rest and in transit

  Monitoring:
    - Alert 30 days before expiry
    - Track certificate usage per application
    - Audit certificate operations
```

---

## Rate Limiting and Throttling

### 1. Understanding Rate Limits

Payment APIs implement strict rate limits to prevent abuse and ensure fair resource allocation.

#### Stripe Rate Limits

```
Default Rate Limits (per API key):
├── Requests: 100 per second per account
├── Burst: 2000 requests in quick succession
├── Special Handling:
│   ├── Listings: 200 per second
│   ├── Search: 10 per second
│   └── File uploads: 1 per second
└── Reset: Automatic after limit window expires
```

#### Rate Limit Headers

```
Response Headers:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1234567890

Example Success Response:
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1234567890
Content-Type: application/json

{
  "object": "charge",
  "id": "ch_1234567890",
  "amount": 2000
}

Rate Limit Exceeded Response:
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 60
Content-Type: application/json

{
  "error": {
    "type": "rate_limit_error",
    "message": "Too many requests",
    "param": null
  }
}
```

### 2. Client-Side Rate Limiting Implementation

```python
import time
from threading import Lock

class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: Number of tokens per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = Lock()

    def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, returns wait time in seconds
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0
            else:
                wait_time = (tokens - self.tokens) / self.rate
                return wait_time

# Usage
limiter = TokenBucketRateLimiter(rate=100, capacity=100)

def make_api_call(data):
    wait_time = limiter.acquire(1)
    if wait_time > 0:
        time.sleep(wait_time)
    return stripe.Charge.create(**data)
```

### 3. Adaptive Throttling Strategy

```python
import logging
from datetime import datetime

class AdaptiveThrottler:
    """Adapts request rate based on API response"""

    def __init__(self, initial_rate: float = 50):
        self.current_rate = initial_rate
        self.min_rate = 10
        self.max_rate = 100
        self.adjustment_factor = 0.95  # Reduce on errors
        self.recovery_factor = 1.02    # Increase on success
        self.error_count = 0
        self.success_count = 0
        self.logger = logging.getLogger(__name__)

    def record_success(self):
        """Record successful request"""
        self.success_count += 1
        if self.success_count >= 10:  # Adjust after 10 successes
            self.current_rate = min(
                self.max_rate,
                self.current_rate * self.recovery_factor
            )
            self.success_count = 0
            self.logger.info(f"Rate increased to {self.current_rate:.1f} req/s")

    def record_error(self, status_code: int = None):
        """Record failed request"""
        self.error_count += 1

        # Aggressive backoff on rate limits
        if status_code == 429:
            self.current_rate = max(
                self.min_rate,
                self.current_rate * self.adjustment_factor
            )
            self.logger.warning(f"Rate reduced to {self.current_rate:.1f} req/s")

        if self.error_count >= 3:
            self.current_rate = self.min_rate
            self.error_count = 0
            self.logger.error("Rate limit reached, reset to minimum")

    def get_delay(self) -> float:
        """Get delay before next request in seconds"""
        return 1.0 / self.current_rate

# Usage
throttler = AdaptiveThrottler()

for transaction in transactions:
    try:
        result = stripe.Charge.create(**transaction)
        throttler.record_success()
    except stripe.error.RateLimitError:
        throttler.record_error(429)
        time.sleep(throttler.get_delay())
```

---

## Idempotency and Retry Logic

### 1. Idempotency Keys

Idempotency ensures that duplicate requests produce the same result without side effects.

```
Idempotency Header Usage:

Request 1:
POST /v1/charges HTTP/1.1
Idempotency-Key: unique-transaction-id-123
Content-Type: application/json

{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa"
}

Response:
HTTP/1.1 200 OK
{
  "id": "ch_1234567890",
  "amount": 2000,
  "status": "succeeded"
}

Request 2 (duplicate):
POST /v1/charges HTTP/1.1
Idempotency-Key: unique-transaction-id-123
Content-Type: application/json

{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa"
}

Response (cached):
HTTP/1.1 200 OK
{
  "id": "ch_1234567890",  // Same charge ID
  "amount": 2000,
  "status": "succeeded"
}
```

### 2. Idempotency Key Generation

```python
import uuid
import hashlib
import json
from datetime import datetime

class IdempotencyKeyGenerator:
    """Generates consistent idempotency keys"""

    @staticmethod
    def generate_uuid_key() -> str:
        """Simple UUID-based key"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_hash_key(
        user_id: str,
        transaction_type: str,
        amount: float,
        timestamp: datetime = None
    ) -> str:
        """Deterministic key based on transaction details"""
        if timestamp is None:
            timestamp = datetime.utcnow().date()

        key_data = f"{user_id}:{transaction_type}:{amount}:{timestamp}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    @staticmethod
    def generate_compound_key(data: dict) -> str:
        """Generate key from transaction data"""
        # Use stable fields
        key_fields = {
            'user_id': data.get('user_id'),
            'amount': data.get('amount'),
            'currency': data.get('currency'),
            'customer_id': data.get('customer_id')
        }

        json_str = json.dumps(key_fields, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

# Usage
generator = IdempotencyKeyGenerator()

# For charge creation
charge_key = generator.generate_hash_key(
    user_id='user_123',
    transaction_type='charge',
    amount=2000.00
)

response = stripe.Charge.create(
    amount=2000,
    currency='usd',
    source='tok_visa',
    idempotency_key=charge_key
)
```

### 3. Retry Logic with Exponential Backoff

```python
import random
import logging
import time
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for automatic retry with exponential backoff"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = logging.getLogger(func.__module__)
            attempt = 0
            delay = initial_delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    attempt += 1

                    # Determine if error is retryable
                    if not is_retryable_error(e):
                        raise

                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retries exceeded for {func.__name__}: {str(e)}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        max_delay,
                        initial_delay * (exponential_base ** (attempt - 1))
                    )

                    # Add jitter
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"Attempt {attempt} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    time.sleep(delay)

            return None
        return wrapper
    return decorator

def is_retryable_error(error: Exception) -> bool:
    """Determine if error should trigger retry"""
    import stripe

    # Network errors
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    # Rate limit errors
    if isinstance(error, stripe.error.RateLimitError):
        return True

    # Server errors
    if isinstance(error, stripe.error.APIError):
        return error.http_status >= 500

    return False
```

---

## Error Handling

### 1. Error Classification

```
Payment API Error Hierarchy:

Error Categories:
├── Client Errors (4xx)
│   ├── 400 Bad Request: Invalid parameters
│   ├── 401 Unauthorized: Authentication failure
│   ├── 402 Request Failed: Payment processing failed
│   ├── 403 Forbidden: Insufficient permissions
│   ├── 404 Not Found: Resource doesn't exist
│   └── 429 Too Many Requests: Rate limit exceeded
│
├── Server Errors (5xx)
│   ├── 500 Internal Server Error
│   ├── 502 Bad Gateway: Temporary connectivity issue
│   ├── 503 Service Unavailable: Maintenance or overload
│   └── 504 Gateway Timeout: Request timeout
│
└── Business Logic Errors
    ├── Card Declined
    ├── Insufficient Funds
    ├── Fraudulent Activity Detected
    └── Compliance Check Failed
```

### 2. Error Response Structure

```python
# Stripe Error Response Example
{
  "error": {
    "charge": "ch_1234567890",
    "code": "card_declined",
    "decline_code": "generic_decline",
    "doc_url": "https://stripe.com/docs/error-codes/card-declined",
    "message": "Your card was declined",
    "param": null,
    "payment_intent": "pi_1234567890",
    "payment_method": "card_1234567890",
    "type": "card_error"
  }
}

# Custom Error Handling
class PaymentAPIError(Exception):
    def __init__(self, code: str, message: str, status: int, raw_error: dict = None):
        self.code = code
        self.message = message
        self.status = status
        self.raw_error = raw_error or {}

    def is_retryable(self) -> bool:
        return self.status >= 500 or self.code == 'rate_limit_error'

    def is_customer_error(self) -> bool:
        return 400 <= self.status < 500 and self.code != 'rate_limit_error'

    def __str__(self):
        return f"[{self.code}] {self.message} (HTTP {self.status})"
```

### 3. Comprehensive Error Handler

```python
import stripe
import logging
from enum import Enum

class ErrorSeverity(Enum):
    RETRY = "retry"
    ABORT = "abort"
    NOTIFY = "notify"
    ESCALATE = "escalate"

class PaymentErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def handle(self, error: Exception, context: dict = None) -> ErrorSeverity:
        """Handle payment API errors with appropriate action"""
        context = context or {}

        if isinstance(error, stripe.error.CardError):
            return self._handle_card_error(error, context)
        elif isinstance(error, stripe.error.RateLimitError):
            return self._handle_rate_limit(error, context)
        elif isinstance(error, stripe.error.AuthenticationError):
            return self._handle_auth_error(error, context)
        elif isinstance(error, stripe.error.APIConnectionError):
            return self._handle_connection_error(error, context)
        elif isinstance(error, stripe.error.InvalidRequestError):
            return self._handle_invalid_request(error, context)
        elif isinstance(error, stripe.error.APIError):
            return self._handle_api_error(error, context)
        else:
            return self._handle_unknown_error(error, context)

    def _handle_card_error(self, error: stripe.error.CardError, context: dict):
        """Handle card-specific errors"""
        decline_code = error.decline_code

        self.logger.warning(
            f"Card declined: {decline_code}",
            extra={'error': error.user_message}
        )

        if decline_code == 'fraudulent':
            self._escalate_fraud_alert(context)
            return ErrorSeverity.ESCALATE
        elif decline_code in ['expired_card', 'lost_card', 'stolen_card']:
            return ErrorSeverity.NOTIFY
        else:
            return ErrorSeverity.ABORT

    def _handle_rate_limit(self, error: stripe.error.RateLimitError, context: dict):
        """Handle rate limit errors"""
        self.logger.warning(f"Rate limit exceeded: {error.message}")
        return ErrorSeverity.RETRY

    def _handle_auth_error(self, error: stripe.error.AuthenticationError, context: dict):
        """Handle authentication errors"""
        self.logger.error(f"Authentication failed: {error.message}")
        self._invalidate_credentials()
        return ErrorSeverity.ESCALATE

    def _handle_connection_error(self, error: stripe.error.APIConnectionError, context: dict):
        """Handle connection errors"""
        self.logger.warning(f"Connection error: {error.message}")
        return ErrorSeverity.RETRY

    def _handle_invalid_request(self, error: stripe.error.InvalidRequestError, context: dict):
        """Handle invalid request errors"""
        self.logger.error(f"Invalid request: {error.message}")
        return ErrorSeverity.ABORT

    def _handle_api_error(self, error: stripe.error.APIError, context: dict):
        """Handle general API errors"""
        self.logger.error(f"API error: {error.message}")
        if error.http_status >= 500:
            return ErrorSeverity.RETRY
        return ErrorSeverity.ABORT

    def _handle_unknown_error(self, error: Exception, context: dict):
        """Handle unexpected errors"""
        self.logger.exception("Unexpected error in payment processing")
        return ErrorSeverity.ESCALATE

    def _escalate_fraud_alert(self, context: dict):
        """Escalate fraud detection"""
        pass

    def _invalidate_credentials(self):
        """Invalidate cached credentials"""
        pass
```

---

## Webhook Patterns

### 1. Webhook Event Structure

Stripe sends webhook events as HTTP POST requests with the following structure:

```json
{
  "id": "evt_1234567890",
  "object": "event",
  "api_version": "2024-04-10",
  "created": 1234567890,
  "data": {
    "object": {
      "id": "ch_1234567890",
      "object": "charge",
      "amount": 2000,
      "status": "succeeded"
    },
    "previous_attributes": {
      "status": "processing"
    }
  },
  "livemode": true,
  "pending_webhooks": 1,
  "request": {
    "id": "req_1234567890",
    "idempotency_key": "key_1234567890"
  },
  "type": "charge.succeeded"
}
```

### 2. Webhook Signature Verification

```python
import hmac
import hashlib
import time
from typing import Tuple

class WebhookVerifier:
    """Verify webhook authenticity using Stripe's signing mechanism"""

    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret.encode()

    def verify_signature(
        self,
        body: str,
        signature_header: str,
        tolerance_seconds: int = 300
    ) -> bool:
        """
        Verify webhook signature

        Args:
            body: Raw request body (as string)
            signature_header: Stripe-Signature header value
            tolerance_seconds: Max age of webhook

        Returns:
            True if signature is valid
        """
        timestamp, v1_hash = self._parse_signature_header(signature_header)

        # Verify timestamp (prevent replay attacks)
        if not self._verify_timestamp(timestamp, tolerance_seconds):
            raise ValueError("Webhook timestamp outside tolerance window")

        # Compute expected signature
        signed_content = f"{timestamp}.{body}"
        expected_hash = hmac.new(
            self.webhook_secret,
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(v1_hash, expected_hash)

    def _parse_signature_header(self, header: str) -> Tuple[int, str]:
        """Parse Stripe-Signature header"""
        timestamp = None
        v1_hash = None

        for part in header.split(','):
            key, value = part.split('=', 1)
            if key == 't':
                timestamp = int(value)
            elif key == 'v1':
                v1_hash = value

        if timestamp is None or v1_hash is None:
            raise ValueError("Invalid signature header format")

        return timestamp, v1_hash

    def _verify_timestamp(self, timestamp: int, tolerance: int) -> bool:
        """Verify webhook timestamp is recent"""
        current_time = int(time.time())
        return abs(current_time - timestamp) <= tolerance
```

### 3. Flask Webhook Handler

```python
from flask import request, jsonify

webhook_verifier = WebhookVerifier(os.environ['STRIPE_WEBHOOK_SECRET'])

@app.route('/webhooks/stripe', methods=['POST'])
def handle_stripe_webhook():
    """Handle Stripe webhook"""
    signature = request.headers.get('Stripe-Signature')

    try:
        if not webhook_verifier.verify_signature(
            request.get_data(as_text=True),
            signature
        ):
            return {'error': 'Invalid signature'}, 401
    except ValueError as e:
        return {'error': str(e)}, 401

    event = request.json

    # Route to appropriate handler
    handlers = {
        'charge.succeeded': handle_charge_succeeded,
        'charge.failed': handle_charge_failed,
        'charge.refunded': handle_charge_refunded,
        'payment_intent.succeeded': handle_payment_succeeded,
    }

    handler = handlers.get(event['type'])
    if handler:
        try:
            handler(event['data']['object'])
            return {'status': 'ok'}, 200
        except Exception as e:
            logger.exception(f"Webhook handler failed: {e}")
            return {'error': 'Processing failed'}, 500
    else:
        # Acknowledge unknown events
        return {'status': 'ok'}, 200
```

---

## Stripe API Examples

### Complete Payment Flow

```python
import stripe
import os
import logging

logger = logging.getLogger(__name__)

class StripePaymentProcessor:
    """Complete Stripe payment processing workflow"""

    def __init__(self):
        stripe.api_key = os.environ['STRIPE_SECRET_KEY']

    def create_payment_intent(self, amount: int, currency: str, customer_id: str = None):
        """Create payment intent for Stripe Payment Element"""
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            payment_method_types=['card'],
        )

        logger.info(f"Created payment intent {intent.id} for ${amount/100:.2f}")
        return intent

    def confirm_payment_intent(self, intent_id: str, payment_method_id: str = None):
        """Confirm payment intent"""
        intent = stripe.PaymentIntent.confirm(
            intent_id,
            payment_method=payment_method_id
        )

        logger.info(f"Confirmed payment intent {intent_id}, status: {intent.status}")
        return intent

    def refund_charge(self, charge_id: str, amount: int = None, reason: str = None):
        """Refund charge (full or partial)"""
        refund_params = {'charge': charge_id}

        if amount is not None:
            refund_params['amount'] = amount

        if reason:
            refund_params['reason'] = reason

        refund = stripe.Refund.create(**refund_params)

        logger.info(f"Refunded charge {charge_id}, refund: {refund.id}")
        return refund

    def create_subscription(self, customer_id: str, price_id: str):
        """Create recurring subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete'
        )

        logger.info(f"Created subscription {subscription.id}")
        return subscription

    def list_charges(self, customer_id: str = None, limit: int = 10):
        """List charges for customer"""
        kwargs = {'limit': limit}
        if customer_id:
            kwargs['customer'] = customer_id

        return stripe.Charge.list(**kwargs)

    def retrieve_customer(self, customer_id: str):
        """Retrieve customer details"""
        return stripe.Customer.retrieve(customer_id)

    def update_customer(self, customer_id: str, **kwargs):
        """Update customer information"""
        return stripe.Customer.modify(customer_id, **kwargs)

    def create_customer(self, email: str, name: str = None, **kwargs):
        """Create customer record"""
        params = {'email': email}
        if name:
            params['name'] = name
        params.update(kwargs)

        return stripe.Customer.create(**params)
```

---

## Security Best Practices

### 1. PCI-DSS Compliance

```yaml
PCI-DSS Essential Controls:

  Level 1 (Never Store):
    - CVV/Security codes
    - PIN numbers
    - Full magnetic stripe data

  Level 2 (Tokenize):
    - Full PAN (Primary Account Number)
    - Expiration dates
    - Cardholder name

  Implementation:
    - Use Stripe.js for client-side tokenization
    - Never transmit card data to your servers
    - Use HTTPS exclusively (TLS 1.2+)
    - Never hardcode sensitive credentials
    - Use environment variables or secrets manager
```

### 2. Secure Client Implementation

```html
<!-- Using Stripe.js for secure tokenization -->
<script src="https://js.stripe.com/v3/"></script>
<div id="card-element"></div>

<script>
  const stripe = Stripe('pk_live_your_public_key');
  const elements = stripe.elements();
  const cardElement = elements.create('card');
  cardElement.mount('#card-element');

  document.getElementById('payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const { paymentMethod, error } = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
      billing_details: {
        name: document.getElementById('cardholder-name').value
      }
    });

    if (error) {
      document.getElementById('error').textContent = error.message;
    } else {
      // Send payment method ID to server (never raw card data)
      const response = await fetch('/create-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentMethodId: paymentMethod.id })
      });
    }
  });
</script>
```

---

## Compliance Requirements

### 1. PCI-DSS Compliance Matrix

```
Requirement 1: Firewall Configuration
  ✓ Implement strict firewall rules
  ✓ Restrict payment data flow
  ✓ Block unnecessary ports

Requirement 3: Protect Cardholder Data
  ✓ Restrict access to payment data
  ✓ Encrypt data in transit (TLS 1.2+)
  ✓ Encrypt data at rest
  ✓ Implement strong cryptography

Requirement 4: Maintain Vulnerability Program
  ✓ Security scan quarterly
  ✓ Penetration testing annually
  ✓ Address vulnerabilities

Requirement 7: Limit Access by Need-to-Know
  ✓ Restrict access to payment data
  ✓ Implement role-based access control
  ✓ Audit access regularly

Requirement 8: Identify and Authenticate Access
  ✓ Assign unique IDs
  ✓ Require strong passwords
  ✓ Implement MFA
  ✓ Restrict remote access

Requirement 10: Track and Monitor Access
  ✓ Maintain audit trails
  ✓ Monitor system activity
  ✓ Retain logs for at least 1 year
  ✓ Alert on suspicious activity
```

### 2. GDPR Compliance for Payment Data

```python
from datetime import datetime

class GDPRPaymentCompliance:
    """GDPR compliance implementation"""

    def get_user_payment_data(self, user_id: str) -> dict:
        """Implement right to access"""
        payments = self.db.query(
            "SELECT * FROM payments WHERE user_id = %s",
            (user_id,)
        )
        return {
            'payments': payments,
            'export_date': datetime.utcnow().isoformat(),
            'format': 'JSON'
        }

    def delete_user_payment_data(self, user_id: str):
        """Implement right to be forgotten"""
        self.db.execute("""
            UPDATE payments
            SET
                user_id = NULL,
                email = 'deleted@example.com',
                name = 'Deleted User'
            WHERE user_id = %s
        """, (user_id,))

        # Delete from Stripe
        try:
            stripe.Customer.delete(user_id)
        except:
            pass

        # Log deletion
        self.compliance_log.info(
            f"Payment data deleted for user {user_id}",
            event_type='right_to_be_forgotten'
        )

    def log_data_processing(self, user_id: str, purpose: str, data_types: list):
        """Log all data processing activities for audit"""
        self.db.insert('payment_processing_log', {
            'user_id': user_id,
            'purpose': purpose,
            'data_types': ','.join(data_types),
            'processing_date': datetime.utcnow(),
            'retention_period': '90 days'
        })
```

This comprehensive guide provides production-ready patterns and examples for payment API integration with focus on security, reliability, and compliance.
