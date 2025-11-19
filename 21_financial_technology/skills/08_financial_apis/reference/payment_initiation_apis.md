# Payment Initiation APIs

## Payment Types

### Domestic Transfers
**SEPA Credit Transfer (SCT)**:
- Used within SEPA zone (EU + others)
- Typically settle in 1-2 days
- Fixed amount transfers
- IBAN-based

**Instant Credit Transfer (SCT Inst)**:
- Real-time settlement (within seconds)
- 24/7 operation
- EU regulation requires support
- Same format as SCT

**Domestic Wire (Local)**:
- Country-specific formats
- Bank routing numbers
- Variable settlement time

### International Transfers
**SWIFT Payments**:
- Cross-border transfers
- Variable cost and speed
- Days to settle
- Complex intermediary bank routing

**International ACH**:
- Batch processing
- Several days settlement
- Lower cost
- Availability varies by country

### Recurring Payments
**Standing Orders**:
- Regular payments at fixed intervals
- Defined start/end dates
- Fixed or variable amounts
- Commonly used for subscriptions

**Direct Debits**:
- Creditor initiates collection
- Requires customer authorization
- Used for utilities, subscriptions
- Reversible within timeframe

## Payment Initiation Flow

### Standard Payment Flow
```
1. Client creates payment request
   ├─ Payment details (amount, account)
   ├─ Creditor info (name, IBAN)
   └─ Reference info (invoice #, memo)

2. Server validates payment
   ├─ Amount validation
   ├─ Account verification
   ├─ Fraud checks
   └─ Balance verification

3. Server initiates at bank
   ├─ PSD2 consent check
   └─ Return payment ID

4. Client polls or receives webhook
   └─ Tracks payment status

5. Payment settles
   └─ Funds transferred
```

## Payment Initiation Request

### Create Payment Request
```json
POST /payments/sepa-credit-transfers
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "instructedAmount": {
    "amount": "100.00",
    "currency": "EUR"
  },
  "debtorAccount": {
    "iban": "DE89370400440532013000"
  },
  "creditorName": "John Doe",
  "creditorAccount": {
    "iban": "IT60X0542811101000000123456"
  },
  "remittanceInformationUnstructured": "Invoice 123456",
  "remittanceInformationStructured": {
    "reference": "INV-123456",
    "referenceType": "ISSR"
  },
  "requestedExecutionDate": "2024-11-20",
  "requestedExecutionTime": "2024-11-20T15:00:00Z",
  "recipientPriority": "HIGH"
}
```

### Payment Response
```json
{
  "transactionStatus": "RCVD",
  "paymentId": "pay-123456",
  "paymentStatusUrl": "/payments/pay-123456/status",
  "scaStatus": "STARTED",
  "scaRedirect": {
    "href": "https://bank.example.com/authorize?id=pay-123456"
  },
  "chosenScaMethod": "EMAIL",
  "challengeData": "OTP-data-if-applicable",
  "psuMessage": "Payment ready for authorization",
  "links": {
    "self": { "href": "/payments/pay-123456" },
    "status": { "href": "/payments/pay-123456/status" },
    "scaRedirect": { "href": "https://bank.example.com/auth" },
    "updatePsuIdentification": { "href": "/payments/pay-123456/authorisations/123" }
  }
}
```

## Payment Status Tracking

### Transaction Status Values
```
RCVD        - Received and validated
PDNG        - Pending (awaiting SCA)
ACSP        - AcceptedAsScheduledPayment
ACCC        - AcceptedCreditInitiation
ACPT        - Accepted (approved by bank)
RJCT        - Rejected
CANC        - Cancelled
ACWC        - AcceptedWithChange
PRAD        - Pending Reachable Account
PART        - Partially Accepted
FASL        - Failed Submission
CDCL        - CustomDebugEventLog
COMC        - Completed
```

### Status Polling
```python
class PaymentTracker:
    def get_payment_status(self, payment_id):
        """
        Get current payment status
        """
        response = requests.get(
            f"https://api.bank.com/payments/{payment_id}/status",
            headers={"Authorization": f"Bearer {self.token}"},
            verify="ca-cert.pem",
            cert=("client-cert.pem", "client-key.pem")
        )

        data = response.json()

        return {
            "payment_id": payment_id,
            "status": data["transactionStatus"],
            "status_detail": data.get("statusDetail"),
            "funds_available": self.check_funds(payment_id),
            "timestamp": datetime.utcnow()
        }

    def track_payment_with_polling(self, payment_id, max_attempts=120):
        """
        Poll status until payment completes or fails
        """
        for attempt in range(max_attempts):
            status_info = self.get_payment_status(payment_id)

            if status_info["status"] in ["COMC", "RJCT", "CANC"]:
                return status_info

            if attempt < max_attempts - 1:
                # Wait before next poll (exponential backoff)
                wait_time = min(2 ** (attempt // 10), 60)
                time.sleep(wait_time)

        raise TimeoutError(f"Payment {payment_id} status check timeout")
```

## Payment Confirmation and Cancellation

### Confirm Scheduled Payment
```
POST /payments/{paymentId}/confirmation-of-funds
Content-Type: application/json

{
  "instructedAmount": {
    "amount": "100.00",
    "currency": "EUR"
  }
}

Response:
{
  "fundsAvailable": true,
  "confirmationId": "conf-123",
  "timestamp": "2024-11-19T10:30:00Z"
}
```

### Cancel Payment
```python
def cancel_payment(payment_id):
    """
    Cancel pending payment
    """
    response = requests.delete(
        f"https://api.bank.com/payments/{payment_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "reason": "USER_REQUEST",
            "reasonCode": "CUST"
        }
    )

    if response.status_code == 200:
        return {
            "paymentId": payment_id,
            "status": "CANC",
            "cancelledAt": datetime.utcnow()
        }
    else:
        raise Exception(f"Cancellation failed: {response.text}")
```

## Advanced Payment Features

### Batch Payments
```json
POST /payments/batch
Content-Type: application/json

{
  "batchId": "batch-123",
  "debtorAccount": {
    "iban": "DE89370400440532013000"
  },
  "payments": [
    {
      "instructedAmount": { "amount": "100.00", "currency": "EUR" },
      "creditorName": "John",
      "creditorAccount": { "iban": "IT60X0542811101000000123456" }
    },
    {
      "instructedAmount": { "amount": "200.00", "currency": "EUR" },
      "creditorName": "Jane",
      "creditorAccount": { "iban": "ES9121000418450200051332" }
    }
  ]
}
```

### Scheduled Payments
```json
POST /payments/sepa-credit-transfers
Content-Type: application/json

{
  "instructedAmount": { "amount": "100.00", "currency": "EUR" },
  "debtorAccount": { "iban": "DE89370400440532013000" },
  "creditorName": "Utility Company",
  "creditorAccount": { "iban": "IT60X0542811101000000123456" },
  "requestedExecutionDate": "2024-12-20",
  "frequency": "MONTHLY",
  "startDate": "2024-11-20",
  "endDate": "2025-12-31"
}
```

### Conditional Payments
```python
class ConditionalPaymentProcessor:
    def process_with_conditions(self, payment_data, conditions):
        """
        Process payment only if conditions are met
        """
        # Check conditions
        if not self.check_all_conditions(conditions):
            raise ValueError("Payment conditions not met")

        # Process payment
        return self.initiate_payment(payment_data)

    def check_all_conditions(self, conditions):
        """
        Verify all payment conditions
        """
        checks = {
            "balance": lambda c: self.check_balance(c),
            "rate": lambda c: self.check_exchange_rate(c),
            "time": lambda c: self.check_time_window(c),
            "price": lambda c: self.check_price_limit(c)
        }

        for condition_type, condition_value in conditions.items():
            if condition_type in checks:
                if not checks[condition_type](condition_value):
                    return False

        return True
```

## Error Handling for Payments

### Common Payment Errors

| Error Code | HTTP | Meaning | Recovery |
|-----------|------|---------|----------|
| INSUFFICIENT_FUNDS | 402 | Balance too low | Add funds or reduce amount |
| INVALID_CREDITOR | 400 | Wrong account info | Verify IBAN/BIC |
| SCA_FAILED | 403 | Authentication failed | Retry authorization |
| RATE_LIMIT | 429 | Too many requests | Wait and retry |
| BANK_ERROR | 500 | Bank system error | Retry after delay |
| ACCOUNT_BLOCKED | 403 | Account restricted | Contact bank |
| DUPLICATE_PAYMENT | 409 | Duplicate detected | Use different request ID |

### Error Response Example
```json
{
  "timestamp": "2024-11-19T10:30:00Z",
  "status": 402,
  "error": "INSUFFICIENT_FUNDS",
  "message": "Account has insufficient funds for this payment",
  "details": {
    "availableBalance": 50.00,
    "requestedAmount": 100.00,
    "shortfall": 50.00
  },
  "requestId": "req-123456"
}
```

## Payment Security Best Practices

### Idempotency
```python
def initiate_payment_safely(payment_data):
    """
    Ensure payment is never duplicated
    """
    # Generate unique idempotency key
    idempotency_key = hashlib.sha256(
        json.dumps(payment_data, sort_keys=True).encode()
    ).hexdigest()

    response = requests.post(
        "https://api.bank.com/payments",
        json=payment_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Idempotency-Key": idempotency_key,
            "X-Request-ID": str(uuid.uuid4())
        }
    )

    return response.json()
```

### Request Signing
```python
def sign_payment_request(payment_data, private_key):
    """
    Sign payment request for authenticity
    """
    import jwt

    payload = {
        "payment": payment_data,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }

    signature = jwt.encode(
        payload,
        private_key,
        algorithm="RS256"
    )

    return {
        "payment": payment_data,
        "signature": signature
    }
```

### Rate Limiting
```python
class PaymentRateLimiter:
    def __init__(self, max_per_day=100):
        self.max_per_day = max_per_day
        self.payments_today = {}

    def check_rate_limit(self, user_id):
        """
        Check if user has exceeded daily limit
        """
        today = datetime.now().date()
        key = f"{user_id}:{today}"

        count = self.payments_today.get(key, 0)

        if count >= self.max_per_day:
            raise RateLimitException(
                f"Daily payment limit ({self.max_per_day}) exceeded"
            )

        self.payments_today[key] = count + 1
        return True
```

## Testing Payment APIs

### Test Scenarios

1. **Happy Path**: Valid payment succeeds
2. **Insufficient Funds**: Decline on low balance
3. **Invalid Creditor**: Error on wrong IBAN
4. **Duplicate**: Duplicate payment detection
5. **SCA Required**: User must authorize
6. **Rate Limit**: 429 when limit exceeded
7. **Bank Downtime**: 503 error handling
8. **Timeout**: Longer than expected delays

### Mock Testing
```python
import unittest
from unittest.mock import Mock, patch

class TestPaymentAPI(unittest.TestCase):
    def test_payment_success(self):
        """Test successful payment"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "transactionStatus": "RCVD",
                "paymentId": "pay-123"
            }

            result = self.payment_api.create_payment({
                "amount": "100.00",
                "creditorIban": "IT60X0542811101000000123456"
            })

            self.assertEqual(result["paymentId"], "pay-123")

    def test_insufficient_funds(self):
        """Test payment decline"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 402
            mock_post.return_value.json.return_value = {
                "error": "INSUFFICIENT_FUNDS"
            }

            with self.assertRaises(InsufficientFundsError):
                self.payment_api.create_payment({
                    "amount": "1000000.00"
                })
```

## References

- PSD2 Payment Initiation: https://www.eba.europa.eu/
- SEPA Standards: https://www.iso20022.org/
- Payment Status Codes: ISO 20022
