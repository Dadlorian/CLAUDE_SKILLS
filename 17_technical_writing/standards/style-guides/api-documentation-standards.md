# API Documentation Standards

## Executive Summary

This document establishes standards for world-class API documentation based on industry leaders (Stripe, Twilio, Plaid) and research-backed best practices.

**Goal**: Enable developers to make their first successful API call in under 15 minutes.

---

## API Documentation Hierarchy

Every API should have these documentation layers:

### 1. **Quickstart** (Priority 1 - Must Have)
**Purpose**: First successful API call in 5-10 minutes
**Audience**: New developers, evaluation stage
**Content**:
- Single, most common use case
- Complete, copy-paste code
- Expected output
- Next steps

**Example Structure**:
```markdown
# Quickstart: Send your first message

Get up and running in 5 minutes.

## 1. Get your API key

1. Sign up at [https://example.com/signup](https://example.com/signup)
2. Navigate to API Keys in your dashboard
3. Click "Create API Key"
4. Copy your key (it starts with `sk_live_`)

## 2. Install the SDK

```bash
npm install @example/sdk
```

## 3. Send a message

```javascript
const { ExampleClient } = require('@example/sdk');

const client = new ExampleClient('YOUR_API_KEY');

async function sendMessage() {
  const message = await client.messages.create({
    to: '+15555551234',
    from: '+15555555678',
    body: 'Hello from Example API!'
  });

  console.log(`Message sent! ID: ${message.id}`);
}

sendMessage();
```

## 4. Run the code

```bash
node send-message.js
```

**Expected output**:
```
Message sent! ID: msg_1234567890
```

## What's next?

- [Receive messages](./receive-messages.md)
- [Handle delivery status](./delivery-status.md)
- [API Reference](./api-reference.md)
```

---

### 2. **API Reference** (Priority 1 - Must Have)

**Purpose**: Complete technical specification of all endpoints
**Audience**: Developers implementing specific features
**Content**:
- All endpoints, parameters, responses
- Authentication details
- Error codes
- Rate limits

**Structure per Endpoint**:

```markdown
## Create a payment

Creates a payment intent for collecting payment.

```http
POST /v1/payments
```

### Authentication

Requires API key in `Authorization` header:
```
Authorization: Bearer sk_live_your_api_key
```

### Request body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | integer | Yes | Amount in smallest currency unit (e.g., cents). Minimum: 50. |
| `currency` | string | Yes | Three-letter ISO currency code (e.g., `usd`, `eur`). |
| `description` | string | No | Payment description. Maximum 500 characters. |
| `metadata` | object | No | Key-value pairs for storing additional information. Maximum 50 keys. |

### Example request

```bash
curl https://api.example.com/v1/payments \
  -u sk_live_your_api_key: \
  -d amount=1000 \
  -d currency=usd \
  -d description="Order #12345"
```

```javascript
const payment = await stripe.payments.create({
  amount: 1000,
  currency: 'usd',
  description: 'Order #12345'
});
```

```python
payment = stripe.Payment.create(
    amount=1000,
    currency='usd',
    description='Order #12345'
)
```

### Response

Returns a `Payment` object.

```json
{
  "id": "pmt_1234567890",
  "object": "payment",
  "amount": 1000,
  "currency": "usd",
  "status": "pending",
  "description": "Order #12345",
  "created_at": "2025-11-19T10:30:00Z",
  "metadata": {}
}
```

### Status values

| Status | Description |
|--------|-------------|
| `pending` | Payment created, awaiting confirmation |
| `processing` | Payment is being processed |
| `succeeded` | Payment completed successfully |
| `failed` | Payment failed |
| `canceled` | Payment was canceled |

### Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `amount_too_small` | Amount below minimum (50) | Increase amount to at least 50 |
| `invalid_currency` | Currency not supported | Use supported currency (see [currencies](./currencies.md)) |
| `rate_limit_exceeded` | Too many requests | Retry after 60 seconds |

### Rate limits

- **Rate limit**: 100 requests per second
- **Burst limit**: 1000 requests per minute
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Idempotency

This endpoint supports idempotency using the `Idempotency-Key` header:

```bash
curl https://api.example.com/v1/payments \
  -u sk_live_your_api_key: \
  -H "Idempotency-Key: unique_key_12345" \
  -d amount=1000 \
  -d currency=usd
```

Requests with the same key return the same response for 24 hours.
```

---

### 3. **Authentication Guide** (Priority 1 - Must Have)

Every API needs clear authentication documentation.

**Required Content**:
- How to obtain credentials
- Where to store credentials (environment variables, secrets managers)
- How to authenticate requests
- Token lifecycle (expiration, refresh)
- Security best practices

**Example**:

```markdown
# Authentication

The Example API uses API keys for authentication. Include your API key in the `Authorization` header:

```bash
curl https://api.example.com/v1/resource \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Get your API key

1. Sign in to your [dashboard](https://example.com/dashboard)
2. Navigate to **Settings → API Keys**
3. Click **Create API Key**
4. Copy the key immediately (it won't be shown again)

## API key types

| Type | Prefix | Use case |
|------|--------|----------|
| Live | `sk_live_` | Production environments |
| Test | `sk_test_` | Development and testing |

**Important**: Never use live keys in test mode or vice versa.

## Secure your API key

❌ **Never**:
- Commit API keys to version control
- Share API keys in support tickets
- Use production keys in development
- Embed keys in client-side code

✅ **Always**:
- Store keys in environment variables
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys every 90 days
- Delete unused keys

### Environment variables

```bash
# .env
EXAMPLE_API_KEY=sk_live_your_api_key_here
```

```javascript
// Load from environment
require('dotenv').config();
const apiKey = process.env.EXAMPLE_API_KEY;
```

## Rotate API keys

1. Create a new API key
2. Update your application to use the new key
3. Deploy the changes
4. Verify the new key works
5. Delete the old key

**Recommended rotation schedule**: Every 90 days

## Rate limiting

All requests count toward your rate limit:
- **Standard**: 100 requests/second
- **Premium**: 1000 requests/second

When rate limited, retry after the time specified in the `Retry-After` header.

```javascript
if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  await sleep(retryAfter * 1000);
  // Retry request
}
```
```

---

### 4. **Error Reference** (Priority 2 - Should Have)

**Purpose**: Comprehensive error catalog with solutions
**Audience**: Developers debugging issues

**Structure**:

```markdown
# Error Reference

All API errors follow this format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "not-an-email"
    },
    "request_id": "req_1234567890"
  }
}
```

## Error response fields

| Field | Type | Description |
|-------|------|-------------|
| `error.code` | string | Machine-readable error code |
| `error.message` | string | Human-readable description |
| `error.details` | object | Additional context (optional) |
| `error.request_id` | string | Request ID for support |

## HTTP status codes

| Status | Meaning | When it occurs |
|--------|---------|----------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Valid API key but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (contact support) |
| 503 | Service Unavailable | Temporary outage |

## Common errors

### `invalid_api_key`

**HTTP Status**: 401
**Cause**: API key is malformed, expired, or doesn't exist
**Solution**:
1. Verify you copied the complete API key
2. Check for extra spaces or characters
3. Generate a new API key if needed
4. Ensure you're using the correct key type (test vs. live)

### `rate_limit_exceeded`

**HTTP Status**: 429
**Cause**: Too many requests in short time
**Solution**:
1. Implement exponential backoff
2. Use the `Retry-After` header
3. Batch requests when possible
4. Upgrade plan for higher limits

**Example retry logic**:
```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
}
```

### `validation_error`

**HTTP Status**: 422
**Cause**: Request data failed validation
**Solution**: Check `error.details` for specific field errors

**Example**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "email": ["Email format is invalid"],
      "amount": ["Amount must be at least 50"]
    }
  }
}
```

## Handling errors

### JavaScript/TypeScript

```javascript
try {
  const response = await fetch('https://api.example.com/v1/resource', {
    headers: { 'Authorization': `Bearer ${apiKey}` }
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(`Error: ${error.error.code} - ${error.error.message}`);

    // Handle specific errors
    switch (error.error.code) {
      case 'rate_limit_exceeded':
        // Implement retry logic
        break;
      case 'validation_error':
        // Show field-specific errors
        break;
      default:
        // Generic error handling
    }

    throw new Error(error.error.message);
  }

  const data = await response.json();
  return data;
} catch (error) {
  console.error('Request failed:', error);
  throw error;
}
```

### Python

```python
import requests

try:
    response = requests.post(
        'https://api.example.com/v1/resource',
        headers={'Authorization': f'Bearer {api_key}'},
        json={'data': 'value'}
    )
    response.raise_for_status()
    return response.json()

except requests.exceptions.HTTPError as e:
    error = e.response.json()['error']

    if error['code'] == 'rate_limit_exceeded':
        # Implement retry with backoff
        time.sleep(60)
    elif error['code'] == 'validation_error':
        # Handle validation errors
        print(f"Validation errors: {error['details']}")
    else:
        print(f"API error: {error['message']}")

    raise

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    raise
```

## Getting help

If you encounter an error not listed here:
1. Check the [status page](https://status.example.com)
2. Search the [community forum](https://community.example.com)
3. Contact support with your `request_id`
```

---

## Code Sample Standards

### Multi-Language Support

Provide code samples in **minimum 5 languages**:

**Priority 1** (Must have):
- JavaScript/TypeScript (Node.js)
- Python
- curl (bash)

**Priority 2** (Should have):
- Ruby
- PHP
- Go
- Java
- C# (.NET)

### Code Sample Quality

Every code sample must:

✅ **Be complete and self-contained**
```javascript
// ✅ GOOD - Includes imports and error handling
const fetch = require('node-fetch');

async function getUser(userId) {
  try {
    const response = await fetch(`https://api.example.com/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${process.env.API_KEY}` }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw error;
  }
}

// ❌ BAD - Incomplete, no error handling
const response = fetch(url);
const data = response.json();
```

✅ **Use realistic values**
```python
# ✅ GOOD - Realistic example
payment = stripe.Payment.create(
    amount=1999,  # $19.99
    currency='usd',
    customer='cus_1234567890',
    description='Premium subscription - Monthly'
)

# ❌ BAD - Nonsensical example
payment = stripe.Payment.create(
    amount=123,
    currency='foo',
    customer='xxx'
)
```

✅ **Include security best practices**
```javascript
// ✅ GOOD - Uses environment variables
const apiKey = process.env.EXAMPLE_API_KEY;

// ❌ BAD - Hardcoded credentials
const apiKey = 'sk_live_abc123';  // NEVER DO THIS
```

✅ **Be tested and working**
- All code samples must execute successfully
- Automate testing in CI/CD
- Version-specific examples (Node 18+, Python 3.9+)

### Code Comments

```javascript
// ✅ GOOD - Explains WHY, not WHAT
// Retry with exponential backoff for transient errors
const maxRetries = 3;
for (let i = 0; i < maxRetries; i++) {
  try {
    return await makeRequest();
  } catch (error) {
    if (i === maxRetries - 1) throw error;
    await sleep(Math.pow(2, i) * 1000);
  }
}

// ❌ BAD - States the obvious
// Loop 3 times
for (let i = 0; i < 3; i++) {
  // Try to make request
  try {
    // Return the result
    return await makeRequest();
  } catch (error) {
    // If last retry, throw error
    if (i === 2) throw error;
    // Wait before retry
    await sleep(Math.pow(2, i) * 1000);
  }
}
```

---

## OpenAPI/Swagger Standards

Use **OpenAPI 3.1** for machine-readable API specifications.

**Benefits**:
- Generate interactive documentation (Swagger UI, Redoc)
- Generate SDKs in multiple languages
- Enable API mocking and testing
- Validate API requests/responses

**Example OpenAPI Spec**:

```yaml
openapi: 3.1.0
info:
  title: Example API
  version: 1.0.0
  description: |
    The Example API allows you to manage users, payments, and more.

    ## Authentication
    Use Bearer token authentication:
    ```
    Authorization: Bearer YOUR_API_KEY
    ```
  contact:
    name: API Support
    email: support@example.com
    url: https://example.com/support
  license:
    name: MIT
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://sandbox-api.example.com/v1
    description: Sandbox

paths:
  /users:
    post:
      summary: Create a user
      description: Creates a new user account
      operationId: createUser
      tags:
        - Users
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  format: email
                  description: User's email address
                  example: alice@example.com
                name:
                  type: string
                  description: User's full name
                  minLength: 1
                  maxLength: 100
                  example: Alice Johnson
                role:
                  type: string
                  enum: [admin, member, guest]
                  default: member
                  description: User's role
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Email already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          description: Unique user identifier
          example: usr_1234567890
        email:
          type: string
          format: email
          example: alice@example.com
        name:
          type: string
          example: Alice Johnson
        role:
          type: string
          enum: [admin, member, guest]
        created_at:
          type: string
          format: date-time
          example: 2025-11-19T10:30:00Z

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: validation_error
            message:
              type: string
              example: Invalid email format
            details:
              type: object
              additionalProperties: true
```

---

## Versioning Documentation

### API Versioning

Document version changes clearly:

```markdown
# API Versions

## v2 (Current)

**Base URL**: `https://api.example.com/v2`
**Status**: ✅ Active
**Support until**: December 2026

### Changes from v1
- **Breaking**: `user.username` renamed to `user.email`
- **Added**: Pagination for all list endpoints
- **Changed**: Rate limit increased to 1000 req/min

### Migration guide
See [Migrating from v1 to v2](./migration-v1-to-v2.md)

## v1 (Deprecated)

**Base URL**: `https://api.example.com/v1`
**Status**: ⚠️ Deprecated (use v2)
**Sunset date**: January 1, 2026

### Deprecation timeline
- **2025-06-01**: v2 released, v1 marked deprecated
- **2025-09-01**: v1 feature freeze (no new features)
- **2026-01-01**: v1 sunset (will return 410 Gone)
```

---

## Implementation Checklist

### For New API Documentation

- [ ] Quickstart (< 10 minutes to first API call)
- [ ] Complete API reference (all endpoints documented)
- [ ] Authentication guide
- [ ] Error reference (all error codes with solutions)
- [ ] Rate limiting documentation
- [ ] Code samples in 5+ languages
- [ ] OpenAPI 3.1 specification
- [ ] Interactive API explorer (Swagger UI/Redoc)
- [ ] Postman/Insomnia collection
- [ ] Webhook documentation (if applicable)
- [ ] Versioning and changelog
- [ ] Migration guides for breaking changes
- [ ] SDK documentation (if applicable)

### Quality Gates

All API documentation must pass:

- [ ] **Accuracy**: Technical reviewby API engineers
- [ ] **Completeness**: All endpoints documented
- [ ] **Code samples**: Tested and working
- [ ] **Links**: No broken links
- [ ] **Search**: All major terms findable
- [ ] **Mobile**: Responsive on mobile devices
- [ ] **Accessibility**: WCAG 2.2 AA compliant

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Based on**: Stripe, Twilio, Plaid API documentation analysis
**Review cycle**: Quarterly
