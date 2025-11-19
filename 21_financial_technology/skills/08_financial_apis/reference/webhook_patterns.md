# Webhook Patterns for Financial APIs

## Webhook Overview

Webhooks are HTTP callbacks that enable real-time notifications when events occur in financial systems.

## Webhook Use Cases

### Payment Events
- Payment initiated
- Payment approved
- Payment processed
- Payment failed/rejected
- Payment reversed/refunded

### Account Events
- Balance changed
- New transaction posted
- Account status changed
- Account limits reached
- Account locked/disabled

### Consent Events
- Consent created
- Consent approved
- Consent revoked
- Consent expired

## Webhook Event Structure

### Standard Event Format
```json
{
  "id": "evt_123456789",
  "timestamp": "2024-11-19T10:30:00Z",
  "type": "payment.completed",
  "source": "payment_api",
  "version": "1.0",
  "data": {
    "paymentId": "pay-123",
    "amount": "100.00",
    "currency": "EUR",
    "status": "COMPLETED",
    "creditorName": "John Doe",
    "executionDate": "2024-11-19"
  },
  "retryCount": 0,
  "deliveryAttempts": 1
}
```

### Event Types
```
payment.*
  - payment.initiated
  - payment.pending
  - payment.authorized
  - payment.completed
  - payment.failed
  - payment.cancelled
  - payment.reversed

account.*
  - account.balance_changed
  - account.transaction_posted
  - account.transaction_pending
  - account.status_changed
  - account.locked

consent.*
  - consent.created
  - consent.approved
  - consent.revoked
  - consent.expired
```

## Webhook Registration

### Registering Webhook Endpoint
```python
class WebhookManager:
    def register_webhook(self, event_types, callback_url):
        """
        Register webhook for specific events
        """
        webhook_data = {
            "callbackUrl": callback_url,
            "events": event_types,
            "description": "Financial API Webhook",
            "authentication": {
                "type": "OAUTH2",
                "clientId": self.client_id
            }
        }

        response = requests.post(
            f"{self.api_url}/webhooks",
            json=webhook_data,
            headers={"Authorization": f"Bearer {self.token}"},
            cert=("client-cert.pem", "client-key.pem")
        )

        return response.json()

    def list_webhooks(self):
        """
        List registered webhooks
        """
        response = requests.get(
            f"{self.api_url}/webhooks",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        return response.json()["webhooks"]

    def delete_webhook(self, webhook_id):
        """
        Unregister webhook
        """
        response = requests.delete(
            f"{self.api_url}/webhooks/{webhook_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        return response.status_code == 204
```

## Webhook Delivery

### HTTP Delivery Pattern
```
POST /webhooks/payment HTTP/1.1
Host: app.example.com
Content-Type: application/json
X-Webhook-ID: evt_123456789
X-Webhook-Timestamp: 2024-11-19T10:30:00Z
X-Webhook-Signature: sha256=abcdef123456...
Content-Length: 512

{
  "id": "evt_123456789",
  "type": "payment.completed",
  "data": {...}
}
```

### Webhook Signature Verification
```python
import hmac
import hashlib
import json

class WebhookValidator:
    def __init__(self, webhook_secret):
        self.webhook_secret = webhook_secret

    def verify_signature(self, request_body, signature_header):
        """
        Verify webhook signature
        """
        # Calculate expected signature
        computed_signature = hmac.new(
            self.webhook_secret.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()

        expected_header = f"sha256={computed_signature}"

        # Compare using constant-time comparison
        return hmac.compare_digest(signature_header, expected_header)

    def verify_webhook_request(self, request_body, headers):
        """
        Full webhook verification
        """
        # Check timestamp (prevent replay attacks)
        timestamp = headers.get("X-Webhook-Timestamp")
        if not self.is_timestamp_recent(timestamp):
            raise ValueError("Webhook timestamp too old")

        # Check signature
        signature = headers.get("X-Webhook-Signature")
        if not self.verify_signature(request_body, signature):
            raise ValueError("Invalid webhook signature")

        return True

    def is_timestamp_recent(self, timestamp_str, max_age_seconds=300):
        """
        Prevent replay attacks by checking timestamp
        """
        from datetime import datetime, timedelta

        webhook_time = datetime.fromisoformat(timestamp_str)
        now = datetime.utcnow()

        age = (now - webhook_time).total_seconds()
        return age < max_age_seconds
```

## Webhook Handler

### Flask Webhook Handler
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

class WebhookHandler:
    def __init__(self, validator):
        self.validator = validator

    @app.route('/webhooks/payment', methods=['POST'])
    def handle_payment_webhook(self):
        """
        Handle payment event webhook
        """
        try:
            # Verify webhook authenticity
            body = request.get_data(as_text=True)
            self.validator.verify_webhook_request(body, request.headers)

            # Parse event
            event = request.json

            # Process event
            event_type = event.get("type")

            if event_type == "payment.completed":
                self.handle_payment_completed(event)
            elif event_type == "payment.failed":
                self.handle_payment_failed(event)
            elif event_type == "payment.reversed":
                self.handle_payment_reversed(event)

            # Return success (acknowledge receipt)
            return jsonify({"status": "received"}), 200

        except ValueError as e:
            # Signature/timestamp verification failed
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            # Processing error
            return jsonify({"error": str(e)}), 500

    def handle_payment_completed(self, event):
        """
        Process completed payment
        """
        payment_data = event.get("data", {})
        payment_id = payment_data.get("paymentId")

        # Update database
        db.payments.update_one(
            {"paymentId": payment_id},
            {
                "$set": {
                    "status": "COMPLETED",
                    "completedAt": datetime.utcnow()
                }
            }
        )

        # Send notification to user
        self.notify_user(payment_id, "Payment completed")

    def handle_payment_failed(self, event):
        """
        Process failed payment
        """
        payment_data = event.get("data", {})
        payment_id = payment_data.get("paymentId")
        error_reason = payment_data.get("errorCode")

        # Update database
        db.payments.update_one(
            {"paymentId": payment_id},
            {
                "$set": {
                    "status": "FAILED",
                    "failureReason": error_reason
                }
            }
        )

        # Notify user and attempt retry if applicable
        self.handle_payment_failure(payment_id, error_reason)
```

## Retry and Delivery Guarantees

### Exponential Backoff
```python
class WebhookRetry:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    def deliver_webhook_with_retries(self, webhook_url, event_data):
        """
        Deliver webhook with exponential backoff
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    webhook_url,
                    json=event_data,
                    timeout=10,
                    headers={
                        "X-Webhook-Attempt": str(attempt + 1),
                        "X-Webhook-Max-Attempts": str(self.max_retries)
                    }
                )

                # Success on 2xx
                if 200 <= response.status_code < 300:
                    return True

                # Permanent failure on 4xx (except 408, 429)
                if 400 <= response.status_code < 500:
                    if response.status_code not in [408, 429]:
                        raise WebhookException(
                            f"Permanent failure: {response.status_code}"
                        )

                # Temporary failure, retry
                raise WebhookException(
                    f"Temporary failure: {response.status_code}"
                )

            except (requests.Timeout, requests.ConnectionError) as e:
                # Network error, retry
                pass
            except WebhookException as e:
                # Check if permanent failure
                if "Permanent" in str(e):
                    raise

            # Calculate backoff
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                wait_time = min(wait_time, 300)  # Max 5 minutes
                time.sleep(wait_time)

        raise WebhookException("Max retries exceeded")
```

## Idempotency and Deduplication

### Idempotent Processing
```python
class IdempotentWebhookHandler:
    def __init__(self, db):
        self.db = db

    def process_webhook_idempotent(self, event):
        """
        Process webhook in idempotent manner
        """
        event_id = event.get("id")

        # Check if already processed
        processed = self.db.webhook_events.find_one(
            {"eventId": event_id}
        )

        if processed:
            # Already processed, return cached result
            return processed.get("result")

        # Process event
        try:
            result = self.process_event(event)

            # Store processing record
            self.db.webhook_events.insert_one({
                "eventId": event_id,
                "type": event.get("type"),
                "processedAt": datetime.utcnow(),
                "result": result,
                "status": "success"
            })

            return result

        except Exception as e:
            # Store failure record
            self.db.webhook_events.insert_one({
                "eventId": event_id,
                "type": event.get("type"),
                "processedAt": datetime.utcnow(),
                "error": str(e),
                "status": "failed"
            })

            raise

    def process_event(self, event):
        """
        Actual event processing logic
        """
        # Implementation-specific logic
        pass
```

## Webhook Monitoring

### Event Delivery Tracking
```python
class WebhookMonitoring:
    def track_delivery(self, webhook_id, event_id, status, latency_ms):
        """
        Track webhook delivery metrics
        """
        self.db.webhook_deliveries.insert_one({
            "webhookId": webhook_id,
            "eventId": event_id,
            "status": status,  # success, failed, timeout
            "latency": latency_ms,
            "timestamp": datetime.utcnow()
        })

    def get_webhook_health(self, webhook_id, hours=24):
        """
        Get webhook delivery health
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        deliveries = list(self.db.webhook_deliveries.find({
            "webhookId": webhook_id,
            "timestamp": {"$gte": cutoff_time}
        }))

        total = len(deliveries)
        successful = sum(1 for d in deliveries if d["status"] == "success")
        average_latency = (
            sum(d["latency"] for d in deliveries) / total if total > 0 else 0
        )

        return {
            "webhookId": webhook_id,
            "totalEvents": total,
            "successfulDeliveries": successful,
            "successRate": (successful / total * 100) if total > 0 else 0,
            "averageLatency": average_latency,
            "healthStatus": "healthy" if successful / total > 0.95 else "degraded"
        }
```

## Webhook Testing

### Webhook Test Simulation
```python
def test_webhook_handler():
    """
    Test webhook handling
    """
    validator = WebhookValidator("test-secret")
    handler = WebhookHandler(validator)

    # Create test event
    test_event = {
        "id": "evt_test_123",
        "type": "payment.completed",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "paymentId": "pay-test-123",
            "amount": "100.00",
            "currency": "EUR"
        }
    }

    # Create signature
    event_json = json.dumps(test_event)
    signature = "sha256=" + hmac.new(
        "test-secret".encode(),
        event_json.encode(),
        hashlib.sha256
    ).hexdigest()

    # Simulate request
    from werkzeug.test import EnvironBuilder
    from werkzeug.wrappers import Request

    builder = EnvironBuilder(
        method='POST',
        data=event_json,
        headers={
            'X-Webhook-Signature': signature,
            'X-Webhook-Timestamp': datetime.utcnow().isoformat(),
            'Content-Type': 'application/json'
        }
    )

    env = builder.get_environ()
    request = Request(env)

    # Test handler
    response = handler.handle_payment_webhook()
    assert response.status_code == 200
```

## References

- Webhook Best Practices: https://www.svix.com/guides/webhooks/
- Event-Driven Architecture: https://martinfowler.com/articles/201701-event-driven.html
- Idempotency: https://developer.stripe.com/docs/idempotency
