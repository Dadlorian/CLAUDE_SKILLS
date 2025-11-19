# Webhook Documentation Standards

## Overview

Webhooks allow your API to notify external systems when events occur. This guide establishes standards for documenting webhooks clearly.

---

## Core Components

### 1. Webhook Overview

```markdown
# Webhooks

Webhooks allow you to receive real-time notifications when events occur in your account.

## How webhooks work

1. Configure a webhook endpoint URL in your dashboard
2. When an event occurs (e.g., payment succeeded), we send an HTTP POST to your URL
3. Your server responds with 200 OK to acknowledge receipt
4. If your server doesn't respond, we retry with exponential backoff

## Use cases

- Send confirmation emails when payments succeed
- Update inventory when orders are placed
- Trigger workflows when users sign up
```

### 2. Event Catalog

```markdown
## Available events

| Event | Description | Typical use case |
|-------|-------------|------------------|
| `payment.succeeded` | Payment completed successfully | Send receipt |
| `payment.failed` | Payment failed | Notify customer |
| `user.created` | New user account created | Send welcome email |
| `subscription.canceled` | Subscription canceled | Update access |
```

### 3. Payload Structure

```markdown
## Event payload

All webhook payloads follow this structure:

```json
{
  "id": "evt_1234567890",
  "type": "payment.succeeded",
  "created_at": "2025-11-19T10:30:00Z",
  "data": {
    // Event-specific data
  }
}
```

### Example: payment.succeeded

```json
{
  "id": "evt_abc123",
  "type": "payment.succeeded",
  "created_at": "2025-11-19T10:30:00Z",
  "data": {
    "id": "pmt_123",
    "amount": 1000,
    "currency": "usd",
    "status": "succeeded"
  }
}
```
```

### 4. Security

```markdown
## Verify webhook signatures

Every webhook includes a signature in the `X-Webhook-Signature` header.

### Verification steps

1. Extract the signature from the header
2. Compute HMAC SHA-256 of the raw payload using your webhook secret
3. Compare computed signature with received signature

### Example (Node.js)

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const computed = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(computed)
  );
}
```
```

### 5. Error Handling

```markdown
## Retry policy

If your endpoint doesn't respond with 200 OK:
- Retry 1: after 5 seconds
- Retry 2: after 1 minute
- Retry 3: after 5 minutes
- Retry 4: after 30 minutes
- Retry 5: after 1 hour

After 5 failed attempts, the webhook is marked as failed.

## Best practices

- Respond quickly (< 3 seconds)
- Process webhooks asynchronously
- Return 200 OK before processing
- Use idempotency to handle duplicates
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Based on**: Stripe, GitHub, Twilio webhook patterns
