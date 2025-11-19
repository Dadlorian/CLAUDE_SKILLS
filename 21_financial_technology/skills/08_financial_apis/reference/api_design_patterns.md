# API Design Patterns for Financial Systems

## RESTful Design Principles

### Resource-Oriented Design
Financial APIs should model real-world concepts as resources:

```
/accounts              - Collection of accounts
/accounts/{id}         - Specific account
/accounts/{id}/balances - Account's balances
/accounts/{id}/transactions - Account's transactions
/payments              - Payment collection
/payments/{id}         - Specific payment
/consents              - Consent collection
/consents/{id}         - Specific consent
```

### HTTP Methods

| Method | Idempotent | Purpose |
|--------|-----------|---------|
| GET | Yes | Retrieve resource |
| POST | No | Create resource |
| PUT | Yes | Replace resource |
| PATCH | No | Partial update |
| DELETE | Yes | Remove resource |

**Example**:
```
GET /accounts - List accounts
POST /payments - Create payment
GET /payments/{id} - Get payment details
GET /payments/{id}/status - Get payment status
PATCH /consents/{id} - Update consent
DELETE /consents/{id} - Revoke consent
```

## Request/Response Patterns

### Request Format
```json
POST /payments
Content-Type: application/json

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
  "remittanceInformationUnstructured": "Invoice #123"
}
```

### Response Format

**Successful Response**:
```json
{
  "transactionStatus": "RCVD",
  "paymentId": "pay-123-456",
  "createdAt": "2024-11-19T10:30:00Z",
  "links": {
    "self": {
      "href": "https://api.example.com/payments/pay-123-456"
    },
    "status": {
      "href": "https://api.example.com/payments/pay-123-456/status"
    }
  }
}
```

**Error Response**:
```json
{
  "timestamp": "2024-11-19T10:30:00Z",
  "status": 400,
  "error": "INVALID_REQUEST",
  "message": "Creditor account IBAN is required",
  "path": "/payments",
  "requestId": "req-12345"
}
```

## Pagination for Large Results

### Offset-Based Pagination
```
GET /accounts/123/transactions?limit=50&offset=100

Response:
{
  "data": [...],
  "pagination": {
    "total": 5000,
    "limit": 50,
    "offset": 100,
    "hasMore": true
  },
  "links": {
    "first": "...",
    "prev": "...",
    "next": "...",
    "last": "..."
  }
}
```

### Cursor-Based Pagination (Preferred)
```
GET /accounts/123/transactions?limit=50&cursor=abc123def456

Response:
{
  "data": [...],
  "pagination": {
    "limit": 50,
    "hasMore": true,
    "nextCursor": "xyz789uvw012"
  },
  "links": {
    "next": "...",
    "self": "..."
  }
}
```

## API Filtering

### Query Parameters
```
GET /transactions?dateFrom=2024-01-01&dateTo=2024-11-19
GET /transactions?minAmount=100&maxAmount=1000
GET /transactions?status=completed&type=transfer
GET /transactions?accountId=acc-123&creditorName=John
```

### Filter Operators
```
GET /transactions?amount[gte]=100&amount[lte]=1000
GET /transactions?date[gte]=2024-01-01
GET /transactions?type[in]=transfer,payment
```

## Relationship Handling

### Embedded Relations
```json
{
  "id": "acc-123",
  "iban": "DE89...",
  "owner": {
    "id": "user-456",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "latestTransactions": [
    {
      "id": "txn-789",
      "amount": "100.00",
      "date": "2024-11-19"
    }
  ]
}
```

### Links to Relations
```json
{
  "id": "acc-123",
  "iban": "DE89...",
  "links": {
    "owner": {
      "href": "/users/user-456"
    },
    "transactions": {
      "href": "/accounts/acc-123/transactions"
    },
    "balances": {
      "href": "/accounts/acc-123/balances"
    }
  }
}
```

### HATEOAS (Hypermedia As The Engine Of Application State)
```json
{
  "id": "pay-123",
  "status": "PENDING_APPROVAL",
  "amount": "100.00",
  "links": {
    "self": {
      "href": "/payments/pay-123",
      "method": "GET"
    },
    "approve": {
      "href": "/payments/pay-123/approve",
      "method": "POST"
    },
    "cancel": {
      "href": "/payments/pay-123/cancel",
      "method": "POST"
    },
    "status": {
      "href": "/payments/pay-123/status",
      "method": "GET"
    }
  }
}
```

## API Versioning

### Version in URL Path (Simplest)
```
https://api.example.com/v1/accounts
https://api.example.com/v2/accounts
https://api.example.com/v1.3/accounts
```

**Pros**: Clear, easy to route
**Cons**: Different URLs for same resource

### Version in Header
```
GET /accounts
Accept-Version: 1.3
```

**Pros**: Single URL, clean
**Cons**: Less visible in documentation

### Version in Accept Header (Content Negotiation)
```
GET /accounts
Accept: application/vnd.myapi.v1+json
```

**Pros**: RESTful approach
**Cons**: More complex

### Semantic Versioning
```
v1.2.3
├─ 1 = Major version (breaking changes)
├─ 2 = Minor version (new features)
└─ 3 = Patch version (bug fixes)
```

## Bulk Operations

### Batch Create
```json
POST /transactions/batch
Content-Type: application/json

{
  "transactions": [
    { "amount": "100", "creditor": "John" },
    { "amount": "200", "creditor": "Jane" }
  ]
}

Response:
{
  "results": [
    { "id": "txn-1", "status": "PENDING" },
    { "id": "txn-2", "status": "PENDING" }
  ]
}
```

### Batch Status Check
```
POST /payments/batch-status
Content-Type: application/json

{
  "paymentIds": ["pay-1", "pay-2", "pay-3"]
}

Response:
{
  "results": [
    { "id": "pay-1", "status": "COMPLETED" },
    { "id": "pay-2", "status": "PENDING" },
    { "id": "pay-3", "status": "FAILED" }
  ]
}
```

## Asynchronous Operations

### Long-Running Operations

```python
# Initiate long operation
POST /account-reconciliation
Content-Type: application/json

{
  "accountId": "acc-123",
  "dateRange": "2024-01-01 to 2024-11-19"
}

Response (202 Accepted):
{
  "operationId": "op-789",
  "status": "PROCESSING",
  "statusUrl": "/operations/op-789/status"
}

# Poll for status
GET /operations/op-789/status

Response:
{
  "operationId": "op-789",
  "status": "COMPLETED",
  "progress": 100,
  "result": { "reconciliationData": {...} },
  "resultUrl": "/operations/op-789/result"
}
```

## State Machines for Complex Operations

### Payment State Diagram
```
INITIATED
  ↓ (Validation OK)
RECEIVED
  ├─ (SCA Required)
  │  ↓
  │  SCA_APPROVED
  │  ↓
  ├─ (Scheduled for future)
  │  ↓
  │  SCHEDULED
  │  ↓
  ├─ (Processing)
  │  ↓
  │  ACCEPTED
  │  ↓
  ├─ (At destination)
  │  ↓
  │  COMPLETED
  │
  ├─ (Rejected)
  │  ↓
  │  REJECTED
  │
  └─ (Cancelled)
     ↓
     CANCELLED

Terminal States: COMPLETED, REJECTED, CANCELLED
```

### Consent State Diagram
```
CREATED
  ↓ (User action pending)
AWAITING_USER_ACTION
  ├─ (User authorizes)
  │  ↓
  │  VALID
  │  ├─ (Limit exceeded)
  │  │  ↓
  │  │  EXCEEDED
  │  ├─ (Expired)
  │  │  ↓
  │  │  EXPIRED
  │  ├─ (User revokes)
  │  │  ↓
  │  │  REVOKED
  │
  └─ (User denies)
     ↓
     REJECTED
```

## Error Code Categorization

### By Severity
```
2xx - Success
3xx - Redirect
4xx - Client error (user/app error)
5xx - Server error (bank/server error)
```

### Specific Financial Errors
```
400 - Invalid request
401 - Unauthorized (authentication failed)
403 - Forbidden (consent/authorization failed)
404 - Resource not found
409 - Conflict (e.g., duplicate transaction ID)
422 - Unprocessable (business logic violation)
429 - Rate limit exceeded
500 - Internal server error
503 - Service unavailable
```

## Caching Strategies

### Cache Control Headers
```
GET /accounts/123

Response Headers:
Cache-Control: max-age=300, private
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 19 Nov 2024 10:00:00 GMT

Subsequent Request:
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

Response:
304 Not Modified (cached data still valid)
```

### Cache Invalidation
```
- Transactions: No caching (always fresh)
- Balances: Cache 1 minute
- Account details: Cache 1 hour
- Exchange rates: Cache 15 minutes
```

## Rate Limiting Response

```
Response Headers:
X-RateLimit-Limit: 1000 (requests per hour)
X-RateLimit-Remaining: 234 (requests left)
X-RateLimit-Reset: 1605897600 (Unix timestamp)

When limit exceeded (429):
Retry-After: 3600 (seconds until reset)
```

## Request ID Tracking

```
Request:
POST /payments
X-Request-ID: req-12345-abcde

Response:
HTTP/1.1 201 Created
X-Request-ID: req-12345-abcde
X-Correlation-ID: corr-99999-zyxwv

(This allows tracking through all systems)
```

## API Documentation

### OpenAPI Specification Example

```yaml
openapi: 3.0.0
info:
  title: Financial API
  version: 1.3.0

paths:
  /accounts:
    get:
      summary: List accounts
      operationId: listAccounts
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
          default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AccountList'
        '401':
          description: Unauthorized

components:
  schemas:
    Account:
      type: object
      properties:
        id:
          type: string
        iban:
          type: string
        currency:
          type: string
```

## References

- REST API Design Best Practices: https://restfulapi.net/
- OpenAPI Specification: https://swagger.io/specification/
- HTTP Status Codes: https://httpwg.org/specs/rfc7231.html#status.codes
