# Open Banking APIs

## Overview

Open Banking refers to APIs that allow third-party developers to build applications and services around financial institutions. This enables secure access to customer financial data and payments.

## Architecture Model

```
┌─────────────────────────────────────────────────┐
│            Open Banking Ecosystem                │
├─────────────────────────────────────────────────┤
│                                                   │
│  ASPSPs (Banks)                                 │
│  ├─ Account Information Services (AIS)         │
│  ├─ Payment Initiation Services (PIS)          │
│  └─ Confirmation of Funds (CoF)                │
│                                                   │
│  TPPs (Third-Party Providers)                  │
│  ├─ Account Information Providers (AIPs)       │
│  ├─ Payment Initiation Providers (PIPs)        │
│  └─ Aggregators & Advisors                     │
│                                                   │
│  End Users (Customers)                          │
│  ├─ Grant consent for data access              │
│  ├─ Authorize payments                          │
│  └─ Revoke permissions                          │
│                                                   │
└─────────────────────────────────────────────────┘
```

## Key API Types

### 1. Account Information Services (AIS)
**Purpose**: Read-only access to account and transaction data

**Data Access**:
- Account lists and details (IBAN, account type)
- Balances (current, pending, booked)
- Transactions (6-90 months historical)
- Beneficiaries
- Standing orders

**Authentication Flow**:
```
1. User selects bank and approves access
2. Redirect to bank for authentication + SCA
3. User grants consent for specific data
4. TPP receives access token
5. TPP retrieves data via API
```

**Endpoints**:
```
GET /accounts
GET /accounts/{account-id}
GET /accounts/{account-id}/balances
GET /accounts/{account-id}/transactions
GET /accounts/{account-id}/transactions/{transaction-id}
```

### 2. Payment Initiation Services (PIS)
**Purpose**: Initiate payments on behalf of users

**Capabilities**:
- Single payments
- Periodic payments
- Standing orders
- Payment schedule management
- Payment status inquiry

**Payment Types**:
- Domestic transfers
- International transfers (SEPA, SWIFT)
- Immediate payments
- Bulk payments

**Endpoints**:
```
POST /payments
GET /payments/{payment-id}
GET /payments/{payment-id}/status
POST /payments/{payment-id}/cancellation
```

### 3. Confirmation of Funds (CoF)
**Purpose**: Verify if sufficient funds are available

**Use Cases**:
- Pre-authorization checks
- Online payment validation
- Risk assessment

**Endpoints**:
```
POST /confirmation-of-funds
GET /confirmation-of-funds/{request-id}
```

## Open Banking Standards

### Standard Banking API (GB)
**Country**: United Kingdom
**Organization**: Open Banking Working Group

**Features**:
- Read/Write API
- Payment initiation
- Account information
- Transaction history
- Scheduled payments

### Berlin Group NextGenPSD2
**Country**: Germany (adopted across EU)
**Version**: 1.3.x (latest)

**Features**:
- PSD2-compliant endpoints
- RESTful design
- JSON request/response
- Detailed error codes
- Consent per resource type

**API Structure**:
```
/v1/consent/accounts - Create AIS consent
/v1/consents/{consentId} - Get consent status
/v1/accounts - List accounts
/v1/accounts/{accountId}/balances - Get balance
/v1/accounts/{accountId}/transactions - Get transactions
/v1/payments - Initiate payment
/v1/payments/{paymentId}/status - Get status
```

### Open Banking Brasil
**Country**: Brazil
**Version**: Evolving

**Features**:
- Account information
- Payment initiation
- Credit operations
- Insurance data
- Investment data

## Consent Management

### Consent Types

**AIS Consent**:
```json
{
  "access": {
    "accounts": ["account-1", "account-2"],
    "balances": ["balance-1", "balance-2"],
    "transactions": ["transaction-1", "transaction-2"]
  },
  "validUntil": "2025-12-31T23:59:59Z",
  "frequencyPerDay": 4,
  "recurringIndicator": true
}
```

**PIS Consent**:
```json
{
  "instructedAmount": {
    "currency": "EUR",
    "amount": "1000.00"
  },
  "debtorAccount": {
    "iban": "DE89370400440532013000"
  },
  "creditorAccount": {
    "iban": "IT60X0542811101000000123456"
  },
  "remittanceInformationUnstructured": "Payment for invoice 12345",
  "paymentType": "SEPA_CREDIT_TRANSFER"
}
```

### Consent Lifecycle

```
Created
   ↓
Awaiting User Action
   ↓ (User authorizes)
Active/Valid
   ├─ (Usage within limits)
   ├─ (Frequency exceeded)
   │  ↓
   │  Exceeded
   ├─ (Time expired)
   │  ↓
   │  Expired
   ├─ (User revokes)
   │  ↓
   │  Revoked
   │
Terminated
```

## Data Aggregation Patterns

### Real-time Aggregation
```
Client Request
   ↓
Aggregation API
   ├─ Query Bank A (async)
   ├─ Query Bank B (async)
   ├─ Query Bank C (async)
   ↓ (Collect responses)
Normalize & Cache
   ↓
Return Aggregated View
```

### Incremental Aggregation
- Fetch new transactions since last sync
- Cache older data locally
- Update on user request
- Webhook-based notifications

### Event-Driven Updates
- Bank sends webhook for new transactions
- Aggregator processes and caches
- Pushes update to client
- Maintains eventual consistency

## Error Handling

### Common Errors

```
401 Unauthorized - Invalid or expired token
403 Forbidden - Insufficient consent
404 Not Found - Resource doesn't exist
429 Too Many Requests - Rate limit exceeded
400 Bad Request - Invalid parameters
500 Server Error - Bank internal error
503 Service Unavailable - Bank maintenance
```

### Error Response Format
```json
{
  "errors": [
    {
      "status": 400,
      "code": "INVALID_REQUEST",
      "title": "Invalid Request",
      "detail": "Missing required parameter: amount"
    }
  ]
}
```

## Security Considerations

### Data Protection
- TLS 1.2+ for all communications
- Token-based access (OAuth 2.0)
- Mutual TLS for critical operations
- Data encryption at rest

### Rate Limiting
- Per API per user/app
- Typically 1 request/second
- Quota management
- Fair usage policies

### Fraud Prevention
- Transaction amount limits
- Destination country restrictions
- Device fingerprinting
- Behavioral analysis

## Implementation Checklist

- [ ] Register as TPP with relevant authorities
- [ ] Obtain certificates (eIDAS for EU)
- [ ] Implement OAuth 2.0 with FAPI profile
- [ ] Design consent UI following guidelines
- [ ] Implement webhook handlers
- [ ] Set up error handling and retry logic
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Test with sandbox environments
- [ ] Security penetration testing
- [ ] Get API certification from banks
- [ ] Set up monitoring and alerting

## API Discovery

### How to Find Available APIs

**Europe (PSD2)**:
- ASPSP Register (maintained by NCAs)
- Financial Conduct Authority (FCA) Register
- European Banking Authority (EBA)

**UK**:
- Open Banking Directory
- Plaid/Tink for aggregated access

**US**:
- Plaid
- Finicity
- Yodlee

**Brazil**:
- Open Banking Brasil directory

**Asia-Pacific**:
- Regional regulatory bodies
- Local aggregator services

## References

- PSD2 Technical Specifications: https://www.eba.europa.eu/
- Berlin Group: https://www.berlin-group.org/
- Open Banking Standards: https://www.openbanking.org.uk/
- OAuth 2.0 FAPI: https://openid.net/fapi/
