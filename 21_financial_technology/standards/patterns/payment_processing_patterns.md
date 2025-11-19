# Payment Processing Patterns

## Table of Contents
1. [Overview](#overview)
2. [Core Patterns](#core-patterns)
3. [Stripe Implementation](#stripe-implementation)
4. [Square Implementation](#square-implementation)
5. [Bank-Grade Implementation](#bank-grade-implementation)
6. [Error Handling](#error-handling)
7. [Real-World Use Cases](#real-world-use-cases)
8. [Performance Considerations](#performance-considerations)

## Overview

Payment processing is one of the most critical components of any fintech system. The patterns described here are designed to handle the complexity of processing payments reliably, securely, and at scale. These patterns are used by companies like Stripe, Square, and major financial institutions.

### Why Payment Patterns Matter

Payment systems require:
- **Reliability**: Every transaction must be processed correctly
- **Idempotency**: Duplicate requests should not create duplicate charges
- **Reconciliation**: All transactions must be auditable and reconcilable
- **Compliance**: PCI-DSS, GDPR, and local regulations must be satisfied
- **Performance**: Payment processing must complete in milliseconds

## Core Patterns

### 1. Three-Tier Payment Processing Pattern

This pattern separates payment processing into three distinct phases:

```
┌─────────────────────────────────────────────────────────┐
│                    Payment Request                       │
│              Validation Phase (Tier 1)                   │
├─────────────────────────────────────────────────────────┤
│  - Check customer KYC status                             │
│  - Validate card/account details                         │
│  - Check velocity limits                                 │
│  - Verify 3D Secure/MFA if required                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   Payment Execution                      │
│              Processing Phase (Tier 2)                   │
├─────────────────────────────────────────────────────────┤
│  - Create auth hold on card/account                      │
│  - Record transaction in ledger                          │
│  - Initiate settlement with payment processor             │
│  - Generate idempotency token                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                  Payment Confirmation                    │
│             Reconciliation Phase (Tier 3)                │
├─────────────────────────────────────────────────────────┤
│  - Capture auth (or void if failed)                      │
│  - Update ledger with final status                       │
│  - Send notification to customer/merchant                │
│  - Log for audit trail                                   │
└─────────────────────────────────────────────────────────┘
```

#### Code Example: Three-Tier Pattern

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal
import uuid
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

@dataclass
class PaymentRequest:
    amount: Decimal
    currency: str
    customer_id: str
    payment_method_id: str
    merchant_id: str
    metadata: dict = None
    idempotency_key: str = None

    def __post_init__(self):
        if not self.idempotency_key:
            self.idempotency_key = str(uuid.uuid4())

@dataclass
class PaymentResult:
    transaction_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    timestamp: datetime
    processor_reference: Optional[str] = None
    error_message: Optional[str] = None

class PaymentProcessor:
    def __init__(self, payment_service, ledger_service, processor_gateway):
        self.payment_service = payment_service
        self.ledger_service = ledger_service
        self.processor_gateway = processor_gateway
        self.idempotency_cache = {}

    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """Process payment through three-tier pattern"""

        # Tier 1: Validation
        validation_result = self._validate_payment(request)
        if not validation_result['valid']:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=validation_result['error']
            )

        # Check idempotency cache
        cached_result = self.idempotency_cache.get(request.idempotency_key)
        if cached_result:
            return cached_result

        # Tier 2: Processing
        try:
            auth_result = self._authorize_payment(request)
            if not auth_result['success']:
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.FAILED,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    processor_reference=auth_result.get('processor_ref'),
                    error_message=auth_result.get('error')
                )

            # Record in ledger
            self.ledger_service.create_entry(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.AUTHORIZED,
                amount=request.amount,
                customer_id=request.customer_id,
                merchant_id=request.merchant_id,
                processor_reference=auth_result['processor_ref']
            )

            # Tier 3: Confirmation
            capture_result = self._capture_payment(
                auth_result['processor_ref'],
                request.amount,
                request.currency
            )

            if capture_result['success']:
                status = PaymentStatus.CAPTURED
                error_msg = None
            else:
                # Void auth if capture fails
                self._void_authorization(auth_result['processor_ref'])
                status = PaymentStatus.FAILED
                error_msg = capture_result.get('error')

            result = PaymentResult(
                transaction_id=request.idempotency_key,
                status=status,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                processor_reference=auth_result['processor_ref'],
                error_message=error_msg
            )

            # Update ledger
            self.ledger_service.update_entry(
                transaction_id=request.idempotency_key,
                status=status
            )

            # Cache result for idempotency
            self.idempotency_cache[request.idempotency_key] = result

            return result

        except Exception as e:
            self.payment_service.log_error(
                transaction_id=request.idempotency_key,
                error=str(e)
            )
            raise

    def _validate_payment(self, request: PaymentRequest) -> dict:
        """Tier 1: Validate payment request"""
        # Check customer KYC status
        customer = self.payment_service.get_customer(request.customer_id)
        if not customer.kyc_verified:
            return {'valid': False, 'error': 'Customer KYC not verified'}

        # Validate payment method
        payment_method = self.payment_service.get_payment_method(
            request.payment_method_id,
            request.customer_id
        )
        if not payment_method.is_valid:
            return {'valid': False, 'error': 'Payment method invalid or expired'}

        # Check amount limits
        if request.amount < Decimal('0.01') or request.amount > Decimal('1000000'):
            return {'valid': False, 'error': 'Amount outside allowed limits'}

        # Check velocity limits
        recent_transactions = self.payment_service.get_recent_transactions(
            request.customer_id,
            hours=24
        )
        daily_total = sum(t.amount for t in recent_transactions)
        if daily_total + request.amount > Decimal('10000'):
            return {'valid': False, 'error': 'Daily limit exceeded'}

        return {'valid': True}

    def _authorize_payment(self, request: PaymentRequest) -> dict:
        """Tier 2: Authorize payment with processor"""
        try:
            auth_response = self.processor_gateway.authorize(
                amount=request.amount,
                currency=request.currency,
                payment_method_id=request.payment_method_id,
                customer_id=request.customer_id,
                metadata=request.metadata or {}
            )

            if auth_response.success:
                return {
                    'success': True,
                    'processor_ref': auth_response.authorization_id
                }
            else:
                return {
                    'success': False,
                    'error': auth_response.error_message,
                    'processor_ref': auth_response.authorization_id
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Authorization failed: {str(e)}'
            }

    def _capture_payment(self, auth_id: str, amount: Decimal, currency: str) -> dict:
        """Tier 3: Capture authorized payment"""
        try:
            capture_response = self.processor_gateway.capture(
                authorization_id=auth_id,
                amount=amount,
                currency=currency
            )

            if capture_response.success:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': capture_response.error_message
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Capture failed: {str(e)}'
            }

    def _void_authorization(self, auth_id: str) -> bool:
        """Void authorization if capture fails"""
        try:
            return self.processor_gateway.void(authorization_id=auth_id)
        except Exception as e:
            # Log error but don't fail - may need manual intervention
            self.payment_service.log_error(
                authorization_id=auth_id,
                error=f'Void failed: {str(e)}'
            )
            return False
```

### 2. Asynchronous Payment Processing Pattern

For high-volume systems, asynchronous processing is essential:

```
┌──────────────────────────────────────────────────────────┐
│           Payment Request (Synchronous)                  │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────┐
│   1. Validate & Queue Payment (Returns 202 Accepted)     │
│      - Create transaction record (PENDING)               │
│      - Generate idempotency token                        │
│      - Push to payment queue                             │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────┐
│   2. Async Worker Processes Payment                      │
│      - Acquire lock (prevent duplicates)                 │
│      - Execute three-tier pattern                        │
│      - Update transaction status                         │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────┐
│   3. Webhooks & Event Notifications                      │
│      - Send payment.completed event                      │
│      - Notify merchant/customer                          │
│      - Trigger downstream processes                      │
└──────────────────────────────────────────────────────────┘
```

```python
import asyncio
import json
from typing import Dict, Callable
from datetime import datetime
import logging

class AsyncPaymentQueue:
    def __init__(self, queue_service, lock_service, payment_processor):
        self.queue_service = queue_service
        self.lock_service = lock_service
        self.payment_processor = payment_processor
        self.webhook_handlers = {}
        self.logger = logging.getLogger(__name__)

    def submit_payment(self, request: PaymentRequest) -> str:
        """Submit payment for async processing"""
        # Create transaction record
        transaction = {
            'id': request.idempotency_key,
            'status': 'PENDING',
            'request': request.__dict__,
            'created_at': datetime.utcnow().isoformat(),
            'retry_count': 0,
            'max_retries': 3
        }

        # Store transaction
        self.queue_service.store_transaction(transaction)

        # Queue for processing
        self.queue_service.enqueue_payment(
            transaction_id=request.idempotency_key,
            priority='normal' if request.amount < 1000 else 'high'
        )

        return request.idempotency_key

    async def process_payment_queue(self):
        """Worker: Process payments from queue"""
        while True:
            try:
                # Get next payment to process
                payment_job = self.queue_service.dequeue_payment(timeout=30)
                if not payment_job:
                    await asyncio.sleep(1)
                    continue

                transaction_id = payment_job['transaction_id']

                # Attempt distributed lock
                acquired = self.lock_service.acquire_lock(
                    f"payment:{transaction_id}",
                    ttl=30
                )

                if not acquired:
                    # Re-queue if can't acquire lock
                    self.queue_service.enqueue_payment(
                        transaction_id=transaction_id,
                        priority='normal'
                    )
                    continue

                try:
                    await self._process_single_payment(transaction_id)
                finally:
                    self.lock_service.release_lock(f"payment:{transaction_id}")

            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)

    async def _process_single_payment(self, transaction_id: str):
        """Process a single payment with retries"""
        transaction = self.queue_service.get_transaction(transaction_id)

        # Reconstruct request
        request_dict = transaction['request']
        request = PaymentRequest(**request_dict)

        try:
            # Execute payment
            result = self.payment_processor.process_payment(request)

            # Update transaction
            self.queue_service.update_transaction(
                transaction_id=transaction_id,
                status=result.status.value,
                result=result.__dict__
            )

            # Emit events
            await self._emit_payment_event(
                event_type='payment.completed',
                transaction_id=transaction_id,
                result=result
            )

        except Exception as e:
            transaction['retry_count'] += 1

            if transaction['retry_count'] < transaction['max_retries']:
                # Re-queue for retry with exponential backoff
                delay = 2 ** transaction['retry_count']
                self.queue_service.enqueue_payment(
                    transaction_id=transaction_id,
                    priority='normal',
                    delay=delay
                )
                self.queue_service.update_transaction(
                    transaction_id=transaction_id,
                    status='RETRYING'
                )
            else:
                # Mark as failed after max retries
                self.queue_service.update_transaction(
                    transaction_id=transaction_id,
                    status='FAILED',
                    error=str(e)
                )

                await self._emit_payment_event(
                    event_type='payment.failed',
                    transaction_id=transaction_id,
                    error=str(e)
                )

    async def _emit_payment_event(self, event_type: str, **kwargs):
        """Emit payment event to webhook handlers"""
        handlers = self.webhook_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_type=event_type, **kwargs)
            except Exception as e:
                self.logger.error(f"Webhook handler error: {e}")

    def register_webhook(self, event_type: str, handler: Callable):
        """Register webhook handler for event"""
        if event_type not in self.webhook_handlers:
            self.webhook_handlers[event_type] = []
        self.webhook_handlers[event_type].append(handler)
```

## Stripe Implementation

Stripe's payment processing follows a specific pattern optimized for reliability:

```python
import stripe
from typing import Dict

class StripePaymentProcessor:
    def __init__(self, api_key: str, webhook_secret: str):
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret

    def process_with_stripe(self, request: PaymentRequest) -> PaymentResult:
        """Process payment using Stripe's API"""
        try:
            # Create payment intent (Stripe's atomic transaction unit)
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                customer=request.customer_id,
                payment_method=request.payment_method_id,
                confirm=True,  # Immediately confirm
                metadata={
                    'merchant_id': request.merchant_id,
                    'idempotency_key': request.idempotency_key,
                    **(request.metadata or {})
                }
            )

            if intent.status == 'succeeded':
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.CAPTURED,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    processor_reference=intent.id
                )
            elif intent.status == 'requires_action':
                # Handle 3D Secure or other authentication
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.PENDING,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    processor_reference=intent.id,
                    error_message='3D Secure authentication required'
                )
            else:
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.FAILED,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    processor_reference=intent.id,
                    error_message=f'Payment intent status: {intent.status}'
                )

        except stripe.error.CardError as e:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=f'Card declined: {e.user_message}'
            )

        except stripe.error.RateLimitError:
            raise Exception('Stripe API rate limit exceeded')

        except stripe.error.AuthenticationError:
            raise Exception('Stripe API authentication failed')

        except stripe.error.APIConnectionError as e:
            raise Exception(f'Stripe API connection error: {str(e)}')

    def handle_stripe_webhook(self, payload: bytes, signature: str) -> Dict:
        """Handle webhook from Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
        except ValueError:
            return {'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            return {'error': 'Invalid signature'}

        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            self._handle_payment_succeeded(intent)
        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            self._handle_payment_failed(intent)
        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            self._handle_refund(charge)

        return {'success': True}

    def _handle_payment_succeeded(self, intent: Dict):
        """Update system when Stripe payment succeeds"""
        metadata = intent.get('metadata', {})
        # Update your ledger with Stripe's confirmation
        print(f"Payment {intent['id']} succeeded")

    def _handle_payment_failed(self, intent: Dict):
        """Update system when Stripe payment fails"""
        metadata = intent.get('metadata', {})
        # Update ledger with failure
        print(f"Payment {intent['id']} failed: {intent.get('last_payment_error')}")

    def _handle_refund(self, charge: Dict):
        """Handle refund from Stripe"""
        print(f"Charge {charge['id']} refunded")
```

## Square Implementation

Square's approach focuses on location-based transactions:

```python
from squareup.client import Client
from squareup.api.payments_api import PaymentsApi

class SquarePaymentProcessor:
    def __init__(self, access_token: str, environment: str = 'production'):
        self.client = Client(
            access_token=access_token,
            environment=environment
        )
        self.payments_api = self.client.payments

    def process_with_square(self, request: PaymentRequest,
                          location_id: str) -> PaymentResult:
        """Process payment using Square's API"""
        try:
            # Create payment
            payment_body = {
                'source_id': request.payment_method_id,
                'idempotency_key': request.idempotency_key,
                'amount_money': {
                    'amount': int(request.amount * 100),
                    'currency': request.currency
                },
                'location_id': location_id,
                'customer_id': request.customer_id,
                'note': f'Payment for merchant {request.merchant_id}'
            }

            result = self.payments_api.create_payment(payment_body)

            if result.is_success():
                payment = result.result
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.CAPTURED,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    processor_reference=payment['payment']['id']
                )
            elif result.is_client_error():
                return PaymentResult(
                    transaction_id=request.idempotency_key,
                    status=PaymentStatus.FAILED,
                    amount=request.amount,
                    currency=request.currency,
                    timestamp=datetime.utcnow(),
                    error_message=str(result.errors)
                )

        except Exception as e:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=f'Square API error: {str(e)}'
            )

    def refund_payment(self, payment_id: str, amount: Decimal) -> bool:
        """Refund a payment"""
        refund_body = {
            'payment_id': payment_id,
            'amount_money': {
                'amount': int(amount * 100),
                'currency': 'USD'
            },
            'reason': 'Merchant refund request'
        }

        result = self.payments_api.refund_payment(refund_body)
        return result.is_success()
```

## Bank-Grade Implementation

Banks use different patterns due to regulatory requirements:

```python
from enum import Enum
from typing import List
import hashlib
import hmac

class BankPaymentStatus(Enum):
    SUBMITTED = "submitted"
    CLEARED = "cleared"
    SETTLEMENT_IN_PROGRESS = "settlement_in_progress"
    SETTLED = "settled"
    REJECTED = "rejected"

class BankPaymentProcessor:
    def __init__(self, bank_gateway, settlement_service, compliance_service):
        self.bank_gateway = bank_gateway
        self.settlement_service = settlement_service
        self.compliance_service = compliance_service

    def process_bank_transfer(self, request: PaymentRequest) -> PaymentResult:
        """Process bank transfer with compliance checks"""

        # Enhanced compliance checks for bank transfers
        compliance_check = self.compliance_service.run_full_check(
            customer_id=request.customer_id,
            amount=request.amount,
            destination_account=request.payment_method_id
        )

        if not compliance_check['approved']:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=compliance_check['reason']
            )

        # Submit to bank
        bank_response = self.bank_gateway.submit_transfer(
            amount=request.amount,
            currency=request.currency,
            from_account=request.customer_id,
            to_account=request.payment_method_id,
            reference=request.idempotency_key,
            priority='normal'  # 'normal' for same-day, 'urgent' for immediate
        )

        if bank_response.success:
            # Schedule settlement (usually T+1 or T+2)
            self.settlement_service.schedule_settlement(
                payment_id=request.idempotency_key,
                bank_reference=bank_response.reference_number,
                scheduled_date=self._calculate_settlement_date(),
                amount=request.amount
            )

            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.AUTHORIZED,  # Banks use authorization for transfers
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                processor_reference=bank_response.reference_number
            )
        else:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=bank_response.error_message
            )

    def _calculate_settlement_date(self) -> datetime:
        """Calculate T+2 settlement date (skip weekends and holidays)"""
        from datetime import timedelta
        settlement_date = datetime.utcnow() + timedelta(days=2)

        # Skip weekends
        while settlement_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            settlement_date += timedelta(days=1)

        # Check against bank holidays
        if self.settlement_service.is_bank_holiday(settlement_date):
            settlement_date += timedelta(days=1)

        return settlement_date
```

## Error Handling

Proper error handling is critical in payment systems:

```python
class PaymentErrorHandler:
    """Comprehensive error handling for payment systems"""

    RETRYABLE_ERRORS = {
        'network_timeout',
        'temporary_outage',
        'rate_limit',
        'service_unavailable'
    }

    PERMANENT_ERRORS = {
        'invalid_payment_method',
        'card_declined',
        'account_closed',
        'invalid_amount',
        'duplicate_transaction',
        'fraud_detected'
    }

    def classify_error(self, error: Exception) -> tuple:
        """Classify error and return (is_retryable, error_code, message)"""

        if isinstance(error, stripe.error.CardError):
            return (False, 'card_declined', error.user_message)

        elif isinstance(error, stripe.error.RateLimitError):
            return (True, 'rate_limit', 'API rate limit exceeded')

        elif isinstance(error, stripe.error.APIConnectionError):
            return (True, 'network_timeout', 'Network connection failed')

        elif isinstance(error, TimeoutError):
            return (True, 'timeout', 'Request timeout')

        elif isinstance(error, ValueError):
            return (False, 'invalid_input', str(error))

        else:
            # Unknown error - treat as potentially retryable
            return (True, 'unknown_error', str(error))

    def handle_payment_error(self, error: Exception, request: PaymentRequest,
                           retry_count: int = 0, max_retries: int = 3) -> PaymentResult:
        """Handle payment error with intelligent retry logic"""

        is_retryable, error_code, message = self.classify_error(error)

        if is_retryable and retry_count < max_retries:
            # Calculate exponential backoff
            delay = 2 ** retry_count + random.uniform(0, 1)

            return {
                'should_retry': True,
                'delay': delay,
                'retry_count': retry_count + 1,
                'error_code': error_code
            }
        else:
            return PaymentResult(
                transaction_id=request.idempotency_key,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.utcnow(),
                error_message=message
            )
```

## Real-World Use Cases

### Use Case 1: E-commerce Checkout

**Scenario**: Online retailer processing payment at checkout

```
Customer submits order →
Validation (address, card) →
Authorize payment →
Create order record →
Capture payment →
Send confirmation email →
Inventory management →
Shipping notification
```

**Pattern**: Three-tier synchronous pattern with immediate feedback

### Use Case 2: Marketplace (Stripe Connect)

**Scenario**: Platform connects sellers and buyers (Uber, Airbnb)

```
Customer pays platform →
Funds held temporarily →
Service completed/delivery →
Platform takes commission →
Seller receives payment →
Negative balance handling for refunds
```

**Pattern**: Two-sided payment pattern with split settlement

### Use Case 3: Subscription Billing (Stripe Billing)

**Scenario**: Monthly/annual recurring charges

```
Customer subscribes →
Create subscription record →
Schedule recurring charge →
Attempt charge on due date →
Handle failures/retries →
Send renewal notice →
Update payment method if declined
```

**Pattern**: Scheduled async processing with retry logic

### Use Case 4: Bank-to-Bank Transfer (ACH)

**Scenario**: Moving funds between financial institutions

```
Customer initiates transfer →
Compliance checks →
Create ACH record →
Submit to ACH network →
Wait for bank confirmation (1-2 days) →
Settlement →
Dispute handling (up to 60 days)
```

**Pattern**: Bank-grade with compliance and settlement tracking

## Performance Considerations

### Throughput Requirements

```
Small Merchant: 100-1,000 transactions/day
  → Synchronous processing acceptable
  → Database per merchant optional
  → Simple queue sufficient

Growing Business: 10,000-100,000 transactions/day
  → Async processing required
  → Dedicated ledger database
  → Redis for caching and locks

Enterprise: 1M+ transactions/day
  → Distributed async system
  → Multiple payment processor connections
  → Sharded databases
  → Real-time analytics
```

### Latency Optimization

```python
class PaymentLatencyOptimizer:
    """Optimize payment processing latency"""

    def __init__(self, cache_service, processor_pool):
        self.cache_service = cache_service
        self.processor_pool = processor_pool

    def fast_payment_validation(self, request: PaymentRequest) -> bool:
        """Quick validation using cache"""
        # Cache customer KYC status
        kyc_status = self.cache_service.get(f"kyc:{request.customer_id}")
        if not kyc_status:
            return False

        # Cache velocity checks
        daily_total = self.cache_service.increment(
            f"daily_total:{request.customer_id}",
            request.amount
        )
        if daily_total > 10000:
            return False

        return True

    def parallel_processing(self, requests: List[PaymentRequest]):
        """Process multiple payments in parallel"""
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(
                self.processor_pool.process_payment,
                requests
            ))
        return results
```

## Conclusion

Payment processing patterns are fundamental to fintech systems. The patterns described above provide:

1. **Three-tier pattern** for fundamental processing reliability
2. **Async pattern** for high-volume systems
3. **Stripe/Square implementations** for commercial providers
4. **Bank-grade pattern** for financial institutions
5. **Error handling** for production robustness

Choose patterns based on your throughput, latency, and compliance requirements.
