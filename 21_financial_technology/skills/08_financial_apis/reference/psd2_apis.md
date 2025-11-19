# PSD2 API Implementation Guide

## PSD2 Overview

The Revised Payment Services Directive 2 is an EU regulation requiring banks to provide APIs for account information and payment initiation.

## PSD2 Roles

### Account Servicing Payment Service Providers (ASPSPs)
**Role**: Banks, credit institutions, e-money institutions
**Obligations**:
- Provide account information via APIs
- Allow payment initiation
- Implement Strong Customer Authentication
- Secure communication channels
- Fair and non-discriminatory access
- Operate 24/7 (with exemptions)

### Third-Party Providers (TPPs)
**Types**:
- **Account Information Providers (AIPs)** - Read account data
- **Payment Initiation Providers (PIPs)** - Initiate payments
- **Payment Service Providers (PSPs)** - Payments only

**Requirements**:
- Registration with relevant authority
- eIDAS qualified certificate
- QWAC (Qualified Website Authentication Certificate)
- QSEAL (Qualified Seal Certificate)
- Secure communication
- Proper consent mechanisms

## Strong Customer Authentication (SCA)

### SCA Definition
Two-factor authentication using independent factors:
- Possession factor (phone, token)
- Knowledge factor (password, PIN)
- Biometric factor (fingerprint, face)

### SCA Flow

```
┌──────────────┐
│  Customer    │
└──────┬───────┘
       │ Initiates Payment/Access
       │
       ▼
┌──────────────────────┐
│ TPP Application      │
│ (Cannot hold factors) │
└──────┬───────────────┘
       │ Redirects to Bank
       │
       ▼
┌────────────────────────────────┐
│ Bank Authentication Page       │
│ 1. Username/Password (Factor 1)│
│ 2. OTP/Biometric (Factor 2)    │
└──────┬──────────────────────────┘
       │ Factors validated
       │
       ▼
┌────────────────────────────────┐
│ Bank Consent Screen            │
│ Show what's being accessed      │
│ Customer approves/denies        │
└──────┬──────────────────────────┘
       │ Redirect to TPP
       │
       ▼
┌──────────────────────┐
│ TPP Receives         │
│ Authorization Code   │
└──────────────────────┘
```

### SCA Exemptions

**Low-Value Transactions**:
- Individual payments up to €30
- Cumulative limit: €100 or 5 transactions

**Trusted Beneficiaries**:
- Pre-approved recipients
- Require initial SCA to add beneficiary

**Corporate Payments**:
- Business-to-business transfers
- Threshold exemptions apply

**Risk-Based Exemptions**:
- Dynamic scoring systems
- ASPSPs assess transaction risk
- TPPs must respect ASPSP exemption decisions

## API Endpoints Structure

### Common Base Paths
```
https://api.bank.com/v1/
https://api.bank.com/v1.3/
https://api.bank.com/xs2a/v1/
```

### Consent Management

**Create Consent**:
```
POST /consents
Content-Type: application/json

{
  "access": {
    "accounts": ["/accounts/ACCOUNT_ID"],
    "balances": ["/accounts/ACCOUNT_ID/balances"],
    "transactions": ["/accounts/ACCOUNT_ID/transactions"]
  },
  "recurringIndicator": false,
  "validUntil": "2025-12-31",
  "frequencyPerDay": 4
}

Response:
201 Created
{
  "consentId": "3c61e45f-bbf3-40df-9b8a-64c1b0beadac",
  "consentStatus": "RECEIVED",
  "links": {
    "scaRedirect": "https://bank.com/authorize?consent=3c61e45f..."
  }
}
```

**Get Consent Status**:
```
GET /consents/{consentId}

Response:
200 OK
{
  "consentId": "3c61e45f...",
  "consentStatus": "VALID",
  "frequencyPerDay": 4,
  "lastActionDate": "2024-11-19",
  "validUntil": "2025-12-31"
}
```

### Account Information

**List Accounts**:
```
GET /accounts
X-Access-Token: eyJ...

Response:
200 OK
{
  "accounts": [
    {
      "resourceId": "acc-1",
      "iban": "DE89370400440532013000",
      "bban": "370400440532013000",
      "currency": "EUR",
      "name": "Salary Account",
      "type": "CACC",
      "status": "ENABLED",
      "usage": "PRIV"
    }
  ]
}
```

**Get Account Details**:
```
GET /accounts/{account-id}

Response:
200 OK
{
  "account": {
    "resourceId": "acc-1",
    "iban": "DE89370400440532013000",
    "currency": "EUR",
    "name": "Main Checking",
    "accountType": "CACC",
    "status": "ENABLED"
  }
}
```

**Get Balances**:
```
GET /accounts/{account-id}/balances

Response:
200 OK
{
  "balances": [
    {
      "balanceType": "INTERIM_BOOKED",
      "balanceAmount": {
        "amount": "1234.56",
        "currency": "EUR"
      },
      "referenceDate": "2024-11-19"
    },
    {
      "balanceType": "PENDING",
      "balanceAmount": {
        "amount": "500.00",
        "currency": "EUR"
      }
    }
  ]
}
```

**Get Transactions**:
```
GET /accounts/{account-id}/transactions?dateFrom=2024-01-01&dateTo=2024-11-19

Response:
200 OK
{
  "booked": [
    {
      "transactionId": "txn-123",
      "bookingDate": "2024-11-19",
      "valueDate": "2024-11-19",
      "amount": {
        "amount": "-50.00",
        "currency": "EUR"
      },
      "purpose": "Coffee",
      "creditorName": "Cafe Espresso",
      "creditorAccount": {
        "iban": "DE75512108001234567890"
      }
    }
  ],
  "pending": []
}
```

### Payment Initiation

**Initiate Payment**:
```
POST /payments/sepa-credit-transfers
Content-Type: application/json

{
  "instructedAmount": {
    "amount": "100.00",
    "currency": "EUR"
  },
  "debtorAccount": {
    "iban": "DE89370400440532013000"
  },
  "creditorName": "Recipient Name",
  "creditorAccount": {
    "iban": "IT60X0542811101000000123456"
  },
  "remittanceInformationUnstructured": "Invoice 12345",
  "requestedExecutionDate": "2024-11-20"
}

Response:
201 Created
{
  "transactionStatus": "RCVD",
  "paymentId": "pay-456",
  "links": {
    "scaRedirect": "https://bank.com/authorize?payment=pay-456"
  }
}
```

**Get Payment Status**:
```
GET /payments/sepa-credit-transfers/{payment-id}/status

Response:
200 OK
{
  "transactionStatus": "ACSP",
  "paymentId": "pay-456",
  "links": {}
}
```

## Security Implementation

### QWAC Certificate
- Issued by qualified trust service provider
- Identifies the TPP organization
- Validity: 1-3 years
- Must be renewed before expiration

### QSEAL Certificate
- Used for signing requests and responses
- Proves authenticity and integrity
- Applied to sensitive operations
- Must be cryptographically sound

### TLS Requirements
- TLS 1.2 minimum (1.3 preferred)
- Mutual TLS (mTLS) with certificate
- Certificate pinning recommended
- Strong cipher suites only

### Request Signing (Berlin Group)
```
Signature: keyId="SN=3c61e45f",
          algorithm="rsa-sha256",
          headers="(request-target) x-request-id content-type",
          signature="..."
```

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| UNAUTHORIZED | 401 | Authentication failed |
| FORBIDDEN | 403 | Consent not valid |
| NOT_FOUND | 404 | Resource not found |
| INVALID_REQUEST | 400 | Bad request format |
| TOO_MANY_REQUESTS | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Bank error |
| SERVICE_UNAVAILABLE | 503 | Maintenance window |
| CONSENT_INVALID | 403 | Consent expired/revoked |
| SCA_INVALID | 403 | SCA step failed |

## Implementation Checklist

### Pre-Launch
- [ ] Register with NCAs
- [ ] Obtain eIDAS certificates (QWAC, QSEAL)
- [ ] Implement OAuth 2.0 with PKCE
- [ ] Build consent management UI
- [ ] Implement SCA handling
- [ ] Set up secure redirects
- [ ] Test mTLS setup

### API Implementation
- [ ] Accounts endpoints
- [ ] Balances endpoint
- [ ] Transactions endpoint
- [ ] Payments endpoint
- [ ] Payment status
- [ ] Consent management
- [ ] Error handling

### Security
- [ ] Certificate validation
- [ ] Request signature verification
- [ ] Rate limiting
- [ ] Input validation
- [ ] Secure logging
- [ ] Penetration testing
- [ ] Security audit

### Testing
- [ ] Sandbox API testing
- [ ] Full SCA flows
- [ ] Error scenarios
- [ ] Concurrent requests
- [ ] Token expiration
- [ ] Rate limiting
- [ ] Performance testing

## References

- Official PSD2 RTS: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018R0389
- EBA Guidelines: https://www.eba.europa.eu/regulation-and-policy/payment-services-directive-2
- ASPSP API Implementations vary by bank
