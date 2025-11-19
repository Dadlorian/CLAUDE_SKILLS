# Documenting Webhooks - Complete Strategy Guide

## Overview

This comprehensive guide walks you through documenting webhooks effectively, covering webhook design, implementation documentation, testing strategies, and security considerations.

**Time**: 45-60 minutes
**Level**: Advanced
**Prerequisites**: Understanding of REST APIs, webhooks, OpenAPI specifications

---

## What Are Webhooks?

Webhooks are user-defined HTTP callbacks triggered by specific events in your system. Unlike polling, webhooks push data to clients when events occur.

**Common webhook use cases**:
- Payment confirmations
- Order status updates
- User registrations
- File uploads
- Real-time notifications
- Integration triggers

---

## Step 1: Design Your Webhook Strategy

Before documenting, establish your webhook architecture.

### Define Webhook Events

Create a taxonomy of events:

```yaml
Event Types:
  Account:
    - account.created
    - account.updated
    - account.deleted
    - account.verified

  Payments:
    - payment.initiated
    - payment.processing
    - payment.completed
    - payment.failed
    - payment.refunded

  Subscriptions:
    - subscription.created
    - subscription.renewed
    - subscription.canceled
    - subscription.paused

  Orders:
    - order.placed
    - order.shipped
    - order.delivered
    - order.returned
```

### Webhook Event Structure

Define a consistent payload structure:

```json
{
  "id": "evt_1234567890",
  "type": "payment.completed",
  "created_at": "2025-11-19T10:30:00Z",
  "api_version": "2025-11-01",
  "request_id": "req_abc123def456",
  "data": {
    "object": "payment",
    "id": "pmt_1234567890",
    "amount": 1000,
    "currency": "usd",
    "status": "succeeded",
    "created_at": "2025-11-19T10:29:45Z"
  }
}
```

---

## Step 2: Create Webhook OpenAPI Schema

Add webhook definitions to your OpenAPI specification:

```yaml
webhooks:
  paymentCompleted:
    post:
      summary: Payment Completed
      description: |
        Triggered when a payment is successfully processed.

        **Retry Policy**: We retry failed deliveries with exponential backoff:
        - Initial attempt: immediate
        - Retry 1: 5 seconds
        - Retry 2: 30 seconds
        - Retry 3: 2 minutes
        - Retry 4: 5 minutes

      operationId: webhookPaymentCompleted
      tags:
        - Payment Webhooks

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - id
                - type
                - created_at
                - data
              properties:
                id:
                  type: string
                  description: Unique webhook event ID
                  example: evt_1234567890

                type:
                  type: string
                  description: Event type
                  enum:
                    - payment.completed
                    - payment.failed
                    - payment.refunded
                  example: payment.completed

                created_at:
                  type: string
                  format: date-time
                  description: ISO 8601 timestamp
                  example: "2025-11-19T10:30:00Z"

                api_version:
                  type: string
                  description: API version when event was created
                  example: "2025-11-01"

                request_id:
                  type: string
                  description: Original request ID that triggered event
                  example: req_abc123def456

                data:
                  type: object
                  description: Event-specific data
                  properties:
                    object:
                      type: string
                      example: payment

                    id:
                      type: string
                      example: pmt_1234567890

                    amount:
                      type: integer
                      example: 1000

                    currency:
                      type: string
                      example: usd

                    status:
                      type: string
                      example: succeeded

                    created_at:
                      type: string
                      format: date-time
                      example: "2025-11-19T10:29:45Z"

      responses:
        '200':
          description: Webhook processed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: true

        '400':
          description: Invalid webhook payload

        '401':
          description: Invalid signature

  paymentFailed:
    post:
      summary: Payment Failed
      description: |
        Triggered when a payment fails due to insufficient funds,
        invalid card, or other reasons.

      operationId: webhookPaymentFailed
      tags:
        - Payment Webhooks

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: string
                  example: evt_0987654321

                type:
                  type: string
                  enum: [payment.failed]
                  example: payment.failed

                created_at:
                  type: string
                  format: date-time
                  example: "2025-11-19T10:32:00Z"

                data:
                  type: object
                  properties:
                    object:
                      type: string
                      example: payment

                    id:
                      type: string
                      example: pmt_9876543210

                    error:
                      type: object
                      properties:
                        code:
                          type: string
                          example: card_declined

                        message:
                          type: string
                          example: Your card was declined

      responses:
        '200':
          description: Webhook processed successfully
```

---

## Step 3: Document Webhook Registration

Explain how developers register webhooks:

```markdown
## Registering Webhooks

### Via Dashboard

1. Log in to your dashboard
2. Navigate to **Settings** → **Webhooks**
3. Click **Add Webhook**
4. Enter your endpoint URL: `https://yourapp.com/webhooks/payments`
5. Select events to subscribe to
6. Enable/disable webhook as needed

### Via API

Register a webhook programmatically:

**Endpoint**: `POST /webhooks`

**Request**:
```json
{
  "url": "https://yourapp.com/webhooks/payments",
  "events": [
    "payment.completed",
    "payment.failed"
  ],
  "active": true,
  "description": "Production webhook for payment notifications"
}
```

**Response** (201 Created):
```json
{
  "id": "wh_1234567890",
  "url": "https://yourapp.com/webhooks/payments",
  "events": [
    "payment.completed",
    "payment.failed"
  ],
  "active": true,
  "signing_secret": "whsec_abc123def456",
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z"
}
```

**Important**: Store the `signing_secret` securely. You'll need it to verify webhooks.

### Updating a Webhook

**Endpoint**: `PATCH /webhooks/{id}`

```json
{
  "url": "https://newapp.com/webhooks/payments",
  "events": ["payment.completed", "payment.failed", "payment.refunded"],
  "active": true
}
```

### Listing Webhooks

**Endpoint**: `GET /webhooks`

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/webhooks
```

**Response**:
```json
{
  "object": "list",
  "data": [
    {
      "id": "wh_1234567890",
      "url": "https://yourapp.com/webhooks/payments",
      "events": ["payment.completed", "payment.failed"],
      "active": true,
      "created_at": "2025-11-19T10:30:00Z"
    }
  ],
  "has_more": false
}
```

### Deleting a Webhook

**Endpoint**: `DELETE /webhooks/{id}`

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/webhooks/wh_1234567890
```
```

---

## Step 4: Document Webhook Signature Verification

This is critical for security:

```markdown
## Verifying Webhook Signatures

All webhook requests are signed with HMAC-SHA256. Verify the signature to ensure the request came from us.

### Signature Headers

Each webhook request includes:

```
X-Webhook-ID: evt_1234567890
X-Signature-Timestamp: 1700408400
X-Signature-Hash: sha256=abcdef123456...
```

### Verification Process

**Python Example**:
```python
import hmac
import hashlib
import json
import time
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_your_secret_key"

@app.route('/webhooks/payments', methods=['POST'])
def webhook_handler():
    # Get headers
    signature_header = request.headers.get('X-Signature-Hash')
    timestamp_header = request.headers.get('X-Signature-Timestamp')

    # Prevent replay attacks - check timestamp is recent (within 5 minutes)
    current_time = int(time.time())
    if abs(current_time - int(timestamp_header)) > 300:
        return {'error': 'Request too old'}, 401

    # Get raw request body
    raw_body = request.get_data(as_text=True)

    # Recreate signature
    signed_content = f"{timestamp_header}.{raw_body}"
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_content.encode(),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures
    if not hmac.compare_digest(signature_header, expected_signature):
        return {'error': 'Invalid signature'}, 401

    # Process webhook
    webhook_data = json.loads(raw_body)
    handle_webhook(webhook_data)

    return {'success': True}, 200

def handle_webhook(data):
    event_type = data.get('type')

    if event_type == 'payment.completed':
        # Handle payment completed
        payment_id = data['data']['id']
        print(f"Payment {payment_id} completed")

    elif event_type == 'payment.failed':
        # Handle payment failed
        payment_id = data['data']['id']
        error = data['data'].get('error')
        print(f"Payment {payment_id} failed: {error}")
```

**Node.js Example**:
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
const WEBHOOK_SECRET = 'whsec_your_secret_key';

// Use raw body for signature verification
app.post('/webhooks/payments', express.raw({type: 'application/json'}), (req, res) => {
  const signatureHeader = req.headers['x-signature-hash'];
  const timestampHeader = req.headers['x-signature-timestamp'];

  // Verify timestamp (within 5 minutes)
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - parseInt(timestampHeader)) > 300) {
    return res.status(401).json({error: 'Request too old'});
  }

  // Recreate signature
  const signedContent = `${timestampHeader}.${req.body}`;
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(signedContent)
    .digest('hex');

  // Compare signatures
  if (!crypto.timingSafeEqual(signatureHeader, expectedSignature)) {
    return res.status(401).json({error: 'Invalid signature'});
  }

  // Process webhook
  const webhookData = JSON.parse(req.body);
  handleWebhook(webhookData);

  res.json({success: true});
});

function handleWebhook(data) {
  switch(data.type) {
    case 'payment.completed':
      console.log(`Payment ${data.data.id} completed`);
      break;
    case 'payment.failed':
      console.log(`Payment ${data.data.id} failed: ${data.data.error.message}`);
      break;
  }
}
```

**Go Example**:
```go
package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"time"
)

const WEBHOOK_SECRET = "whsec_your_secret_key"

type WebhookPayload struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	CreatedAt time.Time `json:"created_at"`
	Data      map[string]interface{} `json:"data"`
}

func verifyWebhook(w http.ResponseWriter, r *http.Request) {
	signatureHeader := r.Header.Get("X-Signature-Hash")
	timestampHeader := r.Header.Get("X-Signature-Timestamp")

	// Verify timestamp
	timestamp, _ := strconv.ParseInt(timestampHeader, 10, 64)
	currentTime := time.Now().Unix()
	if currentTime - timestamp > 300 {
		http.Error(w, "Request too old", http.StatusUnauthorized)
		return
	}

	// Read body
	body, _ := io.ReadAll(r.Body)

	// Recreate signature
	signedContent := fmt.Sprintf("%s.%s", timestampHeader, string(body))
	expectedSignature := "sha256=" + hex.EncodeToString(
		hmac.New(sha256.New, []byte(WEBHOOK_SECRET)).Sum([]byte(signedContent)),
	)

	// Compare
	if !hmac.Equal([]byte(signatureHeader), []byte(expectedSignature)) {
		http.Error(w, "Invalid signature", http.StatusUnauthorized)
		return
	}

	// Process
	var payload WebhookPayload
	json.Unmarshal(body, &payload)
	handleWebhook(payload)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]bool{"success": true})
}

func handleWebhook(payload WebhookPayload) {
	switch payload.Type {
	case "payment.completed":
		fmt.Printf("Payment %s completed\n", payload.Data["id"])
	case "payment.failed":
		fmt.Printf("Payment %s failed\n", payload.Data["id"])
	}
}

func main() {
	http.HandleFunc("/webhooks/payments", verifyWebhook)
	log.Fatal(http.ListenAndServe(":8080", nil))
}
```
```

---

## Step 5: Document Webhook Testing

Provide testing strategies:

```markdown
## Testing Webhooks

### Local Testing with Ngrok

Expose your local server to the internet for testing:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8080

# Forwarding:
# http://localhost:8080 -> https://abc123.ngrok.io
```

Register webhook with ngrok URL:
```bash
curl -X POST https://api.example.com/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abc123.ngrok.io/webhooks/payments",
    "events": ["payment.completed", "payment.failed"]
  }'
```

### Testing with Webhook.cool

Use a temporary webhook endpoint for testing:

1. Go to https://webhook.cool
2. Click **Create New Webhook**
3. Copy the unique URL
4. Register it with your API
5. Trigger test events
6. View requests in the dashboard

### Manual Testing

Simulate webhook payloads:

```bash
# Send test webhook
curl -X POST http://localhost:8080/webhooks/payments \
  -H "Content-Type: application/json" \
  -H "X-Webhook-ID: evt_test_123" \
  -H "X-Signature-Timestamp: $(date +%s)" \
  -H "X-Signature-Hash: sha256=test_signature" \
  -d '{
    "id": "evt_test_123",
    "type": "payment.completed",
    "created_at": "2025-11-19T10:30:00Z",
    "data": {
      "id": "pmt_test_123",
      "amount": 1000,
      "currency": "usd",
      "status": "succeeded"
    }
  }'
```

### Webhook Logs

Document where developers can view webhook delivery logs:

**Dashboard Path**: Settings → Webhooks → Click webhook → View Logs

**Log Information**:
- Request timestamp
- Webhook ID (evt_xxx)
- Event type
- HTTP status code
- Response body
- Retry attempts
- Error details (if failed)

### Debugging Failed Deliveries

Common issues and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Endpoint doesn't exist | Verify webhook URL is correct and accessible |
| 500 Internal Server | Server error | Check your logs, fix the bug, we'll retry |
| Connection Timeout | Endpoint unreachable | Check firewall, ensure server is running |
| Invalid Signature | Signature mismatch | Verify you're using correct secret, check timestamp |
| SSL Certificate Error | HTTPS certificate invalid | Update your certificate or use valid domain |
```

---

## Step 6: Document Retry Logic

```markdown
## Webhook Retry Policy

When your endpoint returns a non-2xx status code, we automatically retry with exponential backoff:

### Retry Schedule

| Attempt | Delay | Total Time |
|---------|-------|-----------|
| Initial | Immediate | 0 seconds |
| Retry 1 | 5 seconds | 5 seconds |
| Retry 2 | 30 seconds | 35 seconds |
| Retry 3 | 2 minutes | 2m 35s |
| Retry 4 | 5 minutes | 7m 35s |
| Retry 5 | 30 minutes | 37m 35s |
| Retry 6 | 2 hours | 2h 37m 35s |
| Retry 7 | 5 hours | 7h 37m 35s |

After 7 failed retries, the webhook is marked as failed.

### Best Practices for Handling Retries

```python
import json
import logging
from flask import Flask, request

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Track processed webhook IDs to prevent duplicates
processed_webhooks = set()

@app.route('/webhooks/payments', methods=['POST'])
def webhook_handler():
    webhook_data = request.json
    webhook_id = webhook_data.get('id')

    # Idempotency: prevent processing duplicate deliveries
    if webhook_id in processed_webhooks:
        logger.info(f"Webhook {webhook_id} already processed, returning 200")
        return {'success': True}, 200

    try:
        # Process webhook
        handle_webhook(webhook_data)

        # Mark as processed
        processed_webhooks.add(webhook_id)

        logger.info(f"Webhook {webhook_id} processed successfully")
        return {'success': True}, 200

    except Exception as e:
        logger.error(f"Error processing webhook {webhook_id}: {str(e)}")
        # Return 5xx to trigger retry
        return {'error': 'Processing failed'}, 500
```

**Important**: Always be idempotent - webhooks may be delivered multiple times.
```

---

## Step 7: Document Webhook Best Practices

```markdown
## Webhook Best Practices

### 1. Always Verify Signatures

Never skip signature verification, even in development:
```python
# GOOD: Always verify
if not verify_signature(request):
    return 401

# BAD: Skipping verification
handle_webhook(request.json)
```

### 2. Respond Quickly

Return 200 OK immediately, process asynchronously:

```python
from celery import shared_task

@app.route('/webhooks/payments', methods=['POST'])
def webhook_handler():
    # Verify and queue processing immediately
    if not verify_signature(request):
        return 401

    # Queue for async processing
    process_webhook_async.delay(request.json)

    # Return immediately
    return {'success': True}, 200

@shared_task
def process_webhook_async(webhook_data):
    # Heavy processing happens here
    handle_webhook_logic(webhook_data)
```

### 3. Be Idempotent

Handle duplicate deliveries gracefully:
```python
def handle_webhook(data):
    webhook_id = data['id']

    # Check if already processed
    if Webhook.objects.filter(external_id=webhook_id).exists():
        return  # Already processed, do nothing

    # Process new webhook
    Webhook.objects.create(
        external_id=webhook_id,
        event_type=data['type'],
        payload=data
    )
```

### 4. Use Timeouts

Prevent hanging connections:
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_request_with_timeout():
    session = requests.Session()

    # 5 second timeout, retry up to 3 times
    session.mount('https://', HTTPAdapter(
        max_retries=Retry(total=3, backoff_factor=0.5)
    ))

    response = session.get('https://example.com', timeout=5)
    return response
```

### 5. Log Everything

Maintain detailed logs for debugging:
```python
import logging

logger = logging.getLogger(__name__)

def handle_webhook(data):
    logger.info(f"Received webhook: {data['id']} ({data['type']})")

    try:
        # Process
        logger.debug(f"Processing data: {data['data']}")
        result = process(data)
        logger.info(f"Successfully processed webhook: {data['id']}")
    except Exception as e:
        logger.error(f"Failed to process webhook {data['id']}: {str(e)}", exc_info=True)
        raise
```

### 6. Validate Before Processing

Verify data integrity:
```python
def validate_webhook(data):
    required_fields = ['id', 'type', 'created_at', 'data']

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data['data'], dict):
        raise ValueError("data must be an object")

    return True
```

### 7. Use Webhook Secrets

Never hardcode secrets:
```python
# BAD
WEBHOOK_SECRET = "whsec_abc123"  # Hardcoded!

# GOOD
import os
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
```

### 8. Monitor Webhook Health

Track delivery success rates:
```python
def get_webhook_health():
    total_deliveries = Webhook.objects.count()
    successful = Webhook.objects.filter(status='delivered').count()

    if total_deliveries == 0:
        return {'health': 'unknown'}

    success_rate = (successful / total_deliveries) * 100

    return {
        'total_deliveries': total_deliveries,
        'successful': successful,
        'failed': total_deliveries - successful,
        'success_rate': f"{success_rate:.2f}%"
    }
```
```

---

## Step 8: Create Webhook Event Reference

Document each event type:

```markdown
## Event Reference

### payment.completed

Triggered when a payment is successfully processed.

**Event ID Pattern**: `evt_*`

**Data Object** (Payment):
- `id` (string): Payment ID
- `amount` (integer): Amount in cents
- `currency` (string): ISO currency code
- `status` (string): "succeeded"
- `created_at` (string): ISO 8601 timestamp

**Example**:
```json
{
  "id": "evt_abc123",
  "type": "payment.completed",
  "created_at": "2025-11-19T10:30:00Z",
  "data": {
    "id": "pmt_xyz789",
    "amount": 2999,
    "currency": "usd",
    "status": "succeeded",
    "created_at": "2025-11-19T10:29:45Z"
  }
}
```

**Handling Tips**:
- Update order status to "paid"
- Send receipt email
- Trigger fulfillment process
- Update accounting records

---

### payment.failed

Triggered when a payment is declined or fails.

**Data Object** (Payment with Error):
- `id` (string): Payment ID
- `status` (string): "failed"
- `error` (object):
  - `code` (string): Error code
  - `message` (string): Human-readable error

**Error Codes**:
- `card_declined`: Card was declined
- `insufficient_funds`: Account has insufficient funds
- `lost_card`: Card reported lost
- `expired_card`: Card has expired
- `processing_error`: Internal processing error

**Example**:
```json
{
  "id": "evt_def456",
  "type": "payment.failed",
  "created_at": "2025-11-19T10:32:00Z",
  "data": {
    "id": "pmt_abc123",
    "amount": 1999,
    "currency": "usd",
    "status": "failed",
    "error": {
      "code": "card_declined",
      "message": "Your card was declined by the bank"
    },
    "created_at": "2025-11-19T10:31:45Z"
  }
}
```

**Handling Tips**:
- Notify user of failed payment
- Show error message with recovery steps
- Offer alternative payment methods
- Don't retry automatically (we do that)

---

### subscription.renewed

Triggered when a subscription automatically renews.

**Data Object** (Subscription):
- `id` (string): Subscription ID
- `status` (string): "active"
- `current_period_start` (string): ISO 8601 timestamp
- `current_period_end` (string): ISO 8601 timestamp

**Example**:
```json
{
  "id": "evt_ghi789",
  "type": "subscription.renewed",
  "created_at": "2025-11-19T10:35:00Z",
  "data": {
    "id": "sub_renewal123",
    "status": "active",
    "current_period_start": "2025-11-19T10:35:00Z",
    "current_period_end": "2025-12-19T10:35:00Z"
  }
}
```
```

---

## Step 9: Security Considerations

```markdown
## Webhook Security

### TLS/SSL Requirements

- All webhooks must use HTTPS
- Valid certificate required
- TLS 1.2 or higher

### Replay Attack Prevention

- Check `X-Signature-Timestamp` header
- Reject requests older than 5 minutes
- Verify signature with timestamp

```python
import time

def verify_timestamp(timestamp_header):
    timestamp = int(timestamp_header)
    current_time = int(time.time())

    if abs(current_time - timestamp) > 300:  # 5 minutes
        raise ValueError("Request too old")
```

### Rate Limiting

- Webhooks don't count against API rate limits
- No more than 100 concurrent delivery attempts
- Implement timeouts on your endpoint

### Data Validation

- Always validate incoming data
- Don't assume field types
- Handle missing fields gracefully

### Secret Management

- Store signing secret securely (use environment variables)
- Rotate secrets periodically
- Never commit secrets to version control

### Monitoring

- Track webhook delivery failures
- Alert on high failure rates (>5%)
- Monitor endpoint response times
- Log all webhook events for debugging
```

---

## Step 10: Common Webhook Patterns

```markdown
## Common Webhook Implementation Patterns

### Pattern 1: Event Store (Event Sourcing)

Store all events for replay:

```python
class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

@app.route('/webhooks/payments', methods=['POST'])
def webhook_handler():
    data = request.json

    # Store event
    event = WebhookEvent.objects.create(
        event_id=data['id'],
        event_type=data['type'],
        payload=data
    )

    # Process
    process_webhook(data)
    event.processed = True
    event.save()

    return {'success': True}, 200
```

### Pattern 2: Dead Letter Queue

Handle failed webhooks separately:

```python
from celery import shared_task

@shared_task
def process_webhook_async(webhook_data):
    try:
        handle_webhook_logic(webhook_data)
    except Exception as e:
        # Send to dead letter queue
        dead_letter_queue.put({
            'webhook_id': webhook_data['id'],
            'error': str(e),
            'timestamp': time.time()
        })
```

### Pattern 3: Webhook Routing

Route to different handlers by event type:

```python
WEBHOOK_HANDLERS = {
    'payment.completed': handle_payment_completed,
    'payment.failed': handle_payment_failed,
    'subscription.renewed': handle_subscription_renewed,
}

def route_webhook(data):
    handler = WEBHOOK_HANDLERS.get(data['type'])
    if handler:
        handler(data)
    else:
        logger.warning(f"No handler for webhook type: {data['type']}")
```

### Pattern 4: Webhook Middleware

Create reusable middleware:

```python
from functools import wraps

def webhook_handler(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Verify signature
        if not verify_signature(request):
            return 401

        # Verify timestamp
        if not verify_timestamp(request):
            return 401

        # Validate data
        try:
            validate_webhook(request.json)
        except ValueError as e:
            return 400

        # Call handler
        return func(request, *args, **kwargs)

    return wrapper

@app.route('/webhooks/payments', methods=['POST'])
@webhook_handler
def webhook_payments():
    process_webhook(request.json)
    return 200
```
```

---

## Webhook Documentation Checklist

- [ ] Define all webhook event types
- [ ] Document event payload schemas
- [ ] Explain signature verification process
- [ ] Provide code examples for verification
- [ ] Document registration/management endpoints
- [ ] Explain retry policy and schedule
- [ ] Provide testing strategies
- [ ] Document idempotency requirements
- [ ] Include security best practices
- [ ] Create event reference guide
- [ ] Show timeout/timeout handling
- [ ] Document error codes and meanings
- [ ] Provide debugging guides
- [ ] Show webhook logs/monitoring
- [ ] Include complete working examples
- [ ] Document retry and backoff strategies

---

## Troubleshooting Webhooks

### "Signature verification failed"

**Causes**:
- Using wrong secret key
- Request body was modified
- Timestamp validation failing

**Solutions**:
```python
# Debug: Print what we're signing
signed_content = f"{timestamp}.{raw_body}"
print(f"Signed content: {signed_content}")
print(f"Expected hash: {expected_hash}")
print(f"Actual hash: {actual_hash}")
```

### "Webhooks not being delivered"

**Check**:
1. Is webhook registered? (`GET /webhooks`)
2. Is it active? (`active: true`)
3. Is endpoint accessible? (test with curl)
4. Check webhook logs for error details
5. Verify firewall isn't blocking requests

### "High failure rates"

**Monitor**:
- Response times (should be <5 seconds)
- Error rates (should be <1%)
- Retry exhaustion (logs when we give up)

**Actions**:
- Scale your endpoint
- Optimize request handling
- Implement caching
- Check for downstream service issues

---

## Next Steps

- [API Contract Testing](./api-testing-documentation.md)
- [Generating SDKs](./creating-sdk-documentation.md)
- [OpenAPI Specifications](./creating-openapi-spec.md)

---

**Complete Examples**: See webhook implementation examples in `src/webhook-examples/` directory.
