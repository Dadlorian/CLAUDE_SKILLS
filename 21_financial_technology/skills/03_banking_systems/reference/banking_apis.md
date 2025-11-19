# Banking APIs and Integration Architecture

## Banking API Overview

### What are Banking APIs?
Banking APIs are programmatic interfaces that expose banking functions to external applications:
- **Data Access**: Account information, transaction history, balances
- **Payments**: Initiate transactions, check status, receive confirmations
- **Account Management**: Open accounts, manage products, update information
- **Integration**: Connect to third-party services, data aggregators, fintechs

### API Types
```
RESTful APIs:
├── HTTP-based
├── Stateless
├── Resource-oriented
├── Standard HTTP methods (GET, POST, PUT, DELETE)
├── JSON payloads
├── URL structure represents resources
└── Most common in banking

SOAP APIs:
├── XML-based
├── Complex structure
├── Legacy banking systems
├── Strong typing
├── Verbose but explicit
└── Declining but still used

GraphQL APIs:
├── Query language for APIs
├── Client specifies exact data needed
├── Flexible schema
├── Reduces over-fetching
├── Growing adoption
└── More complex to implement

Webhook APIs:
├── Event-driven
├── Bank initiates communication
├── Real-time notifications
├── Status updates
├── Asynchronous
└── Requires customer endpoint
```

## Core Banking APIs

### Account Information APIs

#### List Accounts
```
Endpoint: GET /accounts

Request:
├── Authentication: OAuth 2.0 token
├── Optional filters:
│   ├── Account type
│   ├── Status
│   ├── Product
│   └── Currency

Response:
{
  "accounts": [
    {
      "accountId": "acc-001",
      "accountType": "CHECKING",
      "name": "Primary Checking",
      "currency": "USD",
      "status": "ACTIVE",
      "balance": 5000.00,
      "iban": "DE94500105000000012345",
      "bic": "SOGEDEFF",
      "productName": "Premium Checking"
    },
    {
      "accountId": "acc-002",
      "accountType": "SAVINGS",
      "name": "Emergency Fund",
      "currency": "USD",
      "status": "ACTIVE",
      "balance": 10000.00,
      "iban": "DE94500105000000012346",
      "bic": "SOGEDEFF",
      "productName": "High Yield Savings"
    }
  ]
}

Error Responses:
├── 401 Unauthorized (invalid token)
├── 403 Forbidden (no permission)
├── 429 Too Many Requests (rate limited)
└── 500 Internal Server Error
```

#### Get Account Details
```
Endpoint: GET /accounts/{accountId}

Parameters:
├── accountId: Unique account identifier

Response:
{
  "accountId": "acc-001",
  "accountType": "CHECKING",
  "name": "Primary Checking",
  "currency": "USD",
  "status": "ACTIVE",
  "balance": 5000.00,
  "availableBalance": 4950.00,
  "holds": 50.00,
  "accountNumber": "****9876",
  "routingNumber": "111000025",
  "iban": "DE94500105000000012345",
  "bic": "SOGEDEFF",
  "productName": "Premium Checking",
  "accountHolder": "John Doe",
  "accountOpenDate": "2020-01-15",
  "lastUpdated": "2025-11-20T10:30:00Z",
  "interestRate": 0.05,
  "monthlyFee": 0.00,
  "features": ["online_banking", "mobile_app", "checkbook", "debit_card"]
}
```

#### Get Balances
```
Endpoint: GET /accounts/{accountId}/balances

Response:
{
  "accountId": "acc-001",
  "balances": [
    {
      "currency": "USD",
      "currentBalance": 5000.00,
      "availableBalance": 4950.00,
      "pendingBalance": 50.00,
      "balanceAsOf": "2025-11-20T10:30:00Z",
      "holds": [
        {
          "amount": 25.00,
          "description": "Check #1234",
          "date": "2025-11-19"
        },
        {
          "amount": 25.00,
          "description": "Debit Card Hold",
          "date": "2025-11-20"
        }
      ]
    }
  ]
}
```

#### Get Transaction History
```
Endpoint: GET /accounts/{accountId}/transactions

Query Parameters:
├── from: Start date (YYYY-MM-DD)
├── to: End date (YYYY-MM-DD)
├── limit: Maximum results (default: 100)
├── offset: Pagination offset
├── sort: Field to sort by
└── category: Optional category filter

Response:
{
  "accountId": "acc-001",
  "transactions": [
    {
      "transactionId": "txn-12345",
      "date": "2025-11-20",
      "amount": -150.00,
      "currency": "USD",
      "description": "STARBUCKS #1234 NEW YORK NY",
      "merchant": "Starbucks",
      "merchantCategory": "5814",
      "category": "DINING",
      "type": "DEBIT",
      "balance": 4850.00,
      "status": "POSTED",
      "receiptId": null,
      "reference": "POS-20251120-001"
    },
    {
      "transactionId": "txn-12346",
      "date": "2025-11-19",
      "amount": 2500.00,
      "currency": "USD",
      "description": "EMPLOYER PAYROLL",
      "merchant": "Acme Corp",
      "category": "INCOME",
      "type": "CREDIT",
      "balance": 5000.00,
      "status": "POSTED",
      "reference": "PAYROLL-20251119-001"
    }
  ],
  "pagination": {
    "total": 250,
    "count": 2,
    "limit": 100,
    "offset": 0
  }
}
```

### Payment APIs

#### Initiate Payment
```
Endpoint: POST /payments

Request:
{
  "paymentId": "pay-12345",
  "debitAccount": "acc-001",
  "creditAccount": "acc-002",
  "amount": 500.00,
  "currency": "USD",
  "description": "Transfer to savings",
  "date": "2025-11-20",
  "type": "TRANSFER",
  "executionType": "IMMEDIATE"
}

Response:
{
  "paymentId": "pay-12345",
  "status": "PENDING",
  "amount": 500.00,
  "currency": "USD",
  "createdDate": "2025-11-20T10:30:00Z",
  "expectedDate": "2025-11-20T10:31:00Z",
  "chargeDate": "2025-11-20T10:31:00Z"
}

Error Responses:
├── 400 Bad Request (invalid parameters)
├── 422 Unprocessable Entity (business rule violation)
└── 500 Internal Server Error
```

#### Get Payment Status
```
Endpoint: GET /payments/{paymentId}

Response:
{
  "paymentId": "pay-12345",
  "status": "SETTLED",
  "amount": 500.00,
  "currency": "USD",
  "debitAccount": "acc-001",
  "creditAccount": "acc-002",
  "createdDate": "2025-11-20T10:30:00Z",
  "expectedDate": "2025-11-20T10:31:00Z",
  "settlementDate": "2025-11-20T10:31:00Z",
  "statusHistory": [
    {
      "status": "PENDING",
      "timestamp": "2025-11-20T10:30:00Z"
    },
    {
      "status": "POSTED",
      "timestamp": "2025-11-20T10:30:30Z"
    },
    {
      "status": "SETTLED",
      "timestamp": "2025-11-20T10:31:00Z"
    }
  ]
}
```

## RESTful API Design Best Practices

### Resource Naming
```
Good Resource Names:
├── /accounts - Collection of accounts
├── /accounts/{accountId} - Specific account
├── /accounts/{accountId}/transactions - Account transactions
├── /accounts/{accountId}/statements - Account statements
├── /payments - Payment resources
└── /payments/{paymentId} - Specific payment

Avoid:
├── /getAccounts (use GET instead)
├── /account (singular for collection)
├── /acc-info (unclear)
└── /accounts/12345 (use path parameter instead)
```

### HTTP Methods
```
GET:
├── Retrieve resource
├── Read-only
├── Idempotent
├── Cacheable
└── No body needed

POST:
├── Create new resource
├── May not be idempotent
├── Request body required
├── Response includes created resource
└── Returns 201 Created

PUT:
├── Update entire resource
├── Idempotent
├── Request body required
├── Returns updated resource
└── Returns 200 OK

PATCH:
├── Partial update
├── May not be idempotent
├── Smaller request body
├── Returns updated resource
└── Returns 200 OK

DELETE:
├── Remove resource
├── Idempotent
├── No request body
├── Returns 204 No Content
└── May return deleted object
```

### API Versioning
```
Strategies:

URL Path:
├── /v1/accounts
├── /v2/accounts
└── Clear, explicit, trackable

URL Parameter:
├── /accounts?version=2
├── Less common, harder to route
└── Can be confusing

Header-Based:
├── API-Version: 2
├── Transparent to users
├── Good for internal APIs
└── Less visible in logs

Accept Header:
├── Accept: application/vnd.bank+json;version=2
├── RESTful approach
├── Complex to implement
└── Not widely used in banking

Migration Path:
├── Support multiple versions during transition
├── Timeline for deprecation
├── Clear deprecation notices
├── Documentation for changes
└── Developer migration guides
```

## API Security

### Authentication

#### OAuth 2.0 with PKCE
```
Flow:
1. Client generates code_challenge
2. Redirect to authorization endpoint
3. User authenticates
4. User approves scope
5. Authorization code returned
6. Client exchanges code + code_verifier for token
7. Access token issued
8. Token used for API requests

Token Structure (JWT):
{
  "alg": "RS256",
  "typ": "JWT"
}
{
  "iss": "https://auth.bank.com",
  "sub": "user-12345",
  "aud": "banking-api",
  "exp": 1234567890,
  "iat": 1234567200,
  "scope": "accounts transactions payments",
  "permissions": ["read:accounts", "read:transactions"],
  "bnf": ["cust-001"]
}
```

#### Mutual TLS (MTLS)
```
Requirements:
├── Client certificate
├── Client private key
├── Server certificate
├── Certificate validation

Implementation:
├── API gateway validates client cert
├── Certificate pinning recommended
├── Certificate rotation procedures
├── Revocation checking
└── Strong ciphers only
```

### Rate Limiting
```
Strategy:
├── Per API key: 1,000 requests/hour
├── Per IP: 10,000 requests/hour
├── Burst limit: 100 requests/minute
└── Quota by request type

Headers Returned:
├── X-RateLimit-Limit: 1000
├── X-RateLimit-Remaining: 850
├── X-RateLimit-Reset: 1637356800
└── Retry-After: 60 (if rate limited)

Response Codes:
├── 200: Success
├── 429: Too Many Requests (rate limited)
└── Retry-After header included
```

### Input Validation
```
Validation Rules:
├── Whitelist allowed characters
├── Validate data types
├── Check value ranges
├── Validate date formats
├── Validate currency codes
├── Validate account numbers
└── Check account ownership

Error Responses:
{
  "errors": [
    {
      "error_code": "INVALID_AMOUNT",
      "error_message": "Amount must be positive",
      "field": "amount",
      "value": "-500"
    }
  ]
}
```

## Error Handling

### Standard HTTP Status Codes
```
2xx Success:
├── 200 OK - Request succeeded
├── 201 Created - Resource created
├── 204 No Content - Deletion successful
└── 206 Partial Content - Partial data returned

4xx Client Error:
├── 400 Bad Request - Invalid parameters
├── 401 Unauthorized - Authentication failed
├── 403 Forbidden - No permission
├── 404 Not Found - Resource not found
├── 422 Unprocessable Entity - Business rule violation
└── 429 Too Many Requests - Rate limited

5xx Server Error:
├── 500 Internal Server Error - Server error
├── 503 Service Unavailable - Temporarily down
└── 504 Gateway Timeout - Request timeout
```

### Error Response Format
```json
{
  "errors": [
    {
      "error_code": "INSUFFICIENT_FUNDS",
      "error_message": "Insufficient funds in account",
      "details": "Available balance: $450.00, requested: $500.00",
      "field": null,
      "timestamp": "2025-11-20T10:30:00Z"
    }
  ],
  "request_id": "req-12345"
}
```

## API Documentation

### OpenAPI (Swagger)
```
Specification:
├── YAML or JSON format
├── Machine and human readable
├── Auto-generate documentation
├── Support for code generation
├── Standard in industry

Example:
openapi: 3.0.0
info:
  title: Banking API
  version: 1.0.0
paths:
  /accounts:
    get:
      summary: List accounts
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AccountsList'
```

### Developer Portal
```
Essential Components:
├── API documentation (auto-generated from OpenAPI)
├── Code examples (multiple languages)
├── SDKs (Java, Python, JavaScript, etc.)
├── Sandbox environment
├── Test data and scenarios
├── API keys management
├── Usage analytics
├── Rate limit tracking
├── Blog and tutorials
├── Support and contact
└── API changelog
```

## Integration Patterns

### Real-Time Integration
```
Synchronous:
├── Client makes request
├── Waits for response
├── Receives data immediately
├── Simple to implement
├── Low latency

Use Cases:
├── Account balance lookup
├── Payment initiation
├── Account details retrieval
└── Real-time authorization
```

### Asynchronous Integration
```
Webhook-Based:
├── API notifies client of events
├── Client provides callback URL
├── Bank calls webhook with updates
├── Client acknowledges receipt
├── Event-driven architecture

Use Cases:
├── Payment status updates
├── Transaction notifications
├── Statement generation notifications
└── Account closure notifications

Webhook Implementation:
{
  "event": "payment.settled",
  "timestamp": "2025-11-20T10:31:00Z",
  "data": {
    "paymentId": "pay-12345",
    "status": "SETTLED",
    "amount": 500.00,
    "currency": "USD"
  }
}
```

## API Testing

### Test Scenarios
```
Functional Testing:
├── Happy path (valid inputs)
├── Boundary conditions
├── Error conditions
├── Edge cases
├── Data validation
└── Field validation

Performance Testing:
├── Latency (P50, P95, P99)
├── Throughput (requests per second)
├── Load testing
├── Stress testing
├── Sustained load
└── Spike testing

Security Testing:
├── Authentication bypass
├── Authorization checks
├── Input validation
├── Injection attacks
├── Rate limiting
└── Token expiration
```

### Sandbox Environment
```
Characteristics:
├── Production-like environment
├── Test data (no real funds)
├── Full API functionality
├── No actual transactions
├── Quick response times
├── Reset capability
└── Monitoring tools

Test Data:
├── Test accounts
├── Test transactions
├── Test payments
├── Various scenarios
└── Error conditions
```

## Conclusion
Banking APIs are critical infrastructure enabling modern fintech, open banking, and digital banking. Secure, well-designed APIs following REST principles and industry standards are essential for successful integration ecosystems and customer experiences. Proper authentication, rate limiting, error handling, and documentation ensure secure and reliable integrations.
