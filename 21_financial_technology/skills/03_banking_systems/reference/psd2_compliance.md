# PSD2 Compliance and Implementation

## PSD2 Overview

### What is PSD2?
Payment Services Directive 2 (PSD2) is EU regulation that:
- Opens banking APIs for regulated third parties
- Requires Strong Customer Authentication (SCA)
- Mandates transparent payment information
- Enables open banking and fintech innovation
- Protects consumer payment rights

### Key Effective Dates
- **May 2018**: Initial directive implementation
- **September 14, 2019**: Authentication requirements enforced
- **2025+**: Ongoing compliance requirements

### Regulatory Scope
- **Geography**: EU/EEA countries
- **Institutions**: Banks, payment institutions, e-money institutions
- **Services**: Payment accounts, accounts for investment services
- **Exemptions**: Limited (business accounts, certain payment types)

## PSD2 Requirements

### 1. Account Information Services (AIS)

#### Requirements for Banks
```
Banks Must Provide:
├── Dedicated high-availability API
├── Free API access to competitors
├── Real-time (or near real-time) data access
├── Secure authentication
├── Data in structured, standard format
└── Service Level Agreement (SLA)

Data to Provide:
├── Account Identification
├── Account Type
├── Account Holder Name
├── Account Status
├── Balance Information (current & available)
├── Transaction History (at least 90 days)
├── Contact Information
└── Rates and Fees
```

#### Requirements for Third Parties
```
Third Parties (AISPs) Must:
├── Register with financial authorities
├── Implement security measures
├── Obtain customer explicit consent
├── Limit data access to authorized scope
├── Delete data on consent revocation
├── Implement safeguards for customer data
└── Have cyber insurance
```

### 2. Payment Initiation Services (PIS)

#### Requirements for Banks
```
Banks Must Enable:
├── Payment initiation API
├── Validation of payment details
├── Confirmation of funds service (CoFS)
├── Payment status checking
├── Support for single and batch payments
├── Full SEPA payment types
└── Reasonable fees for services

Payment Types:
├── Domestic Credit Transfers
├── SEPA Credit Transfer (SCT)
├── Cross-border payments
└── Immediate Payment Services
```

#### Requirements for Third Parties
```
Third Parties (PISPs) Must:
├── Register with financial authorities
├── Be professionally organized
├── Implement proper security
├── Obtain explicit customer authorization
├── Offer refund mechanism
├── Provide confirmation of payment details
└── Maintain transaction logs
```

### 3. Strong Customer Authentication (SCA)

#### SCA Requirements
```
Definition:
Strong authentication using at least two independent factors

Factor Types:
├── Knowledge: Something you know (password, PIN)
├── Possession: Something you have (phone, card)
└── Inherence: Something you are (biometric: fingerprint, face)

Requirements:
├── Applied to remote customer-initiated transactions
├── Applied to card-not-present transactions
├── Applied to money transfer initiation
└── Applied to payment consent
```

#### Exemptions
```
Transactions Exempt from SCA:
├── Low-value transactions (<€30) - with cumulative limits
├── Whitelisted payees
├── Recurring payments from same account to same payee
├── Transactions from customer's own accounts
├── Business-to-business payments
├── Electronic transactions with specific merchant categories
└── Merchant-initiated transactions (with setup)

Cumulative Exemptions:
├── Max 5 consecutive low-value transactions
├── Cannot exceed €100 cumulative value
├── Reset when threshold exceeded
└── Requires SCA for next transaction
```

#### SCA Implementation

##### Authentication Methods
```
Standard Methods:
├── SMS OTP (One-Time Password)
├── Mobile app push notification
├── Banking app authentication
├── Hardware security token
├── Biometric authentication

Recommended Approach:
├── Two-factor authentication (2FA)
├── One factor from bank (e.g., app)
├── One factor from customer (e.g., biometric)
```

##### Secure Redirect Flow
```
Flow:
1. Customer initiates payment at third-party site
2. Third-party redirects to bank
3. Customer authenticates with bank (SCA)
4. Bank shows payment details
5. Customer confirms payment
6. Bank redirects back to third-party with result
7. Third-party confirms to customer
```

##### Decoupled Authentication
```
Flow:
1. Payment initiated at merchant/PISP
2. Customer receives authentication request on separate device/app
3. Customer approves on separate device
4. Authorization communicated back to bank
5. Payment proceeds

Use Case:
├── QR code at POS scanned by customer phone
├── Authentication happens on phone
├── Payment confirmed at register
```

## Technical Implementation

### API Endpoints Required

```
Account Information Service (AIS) Endpoints:
GET    /accounts
       - List accounts (with customer consent)

GET    /accounts/{accountId}
       - Get account details

GET    /accounts/{accountId}/balances
       - Get current and available balance

GET    /accounts/{accountId}/transactions
       - Get transaction history (paginated)

Payment Initiation Service (PIS) Endpoints:
POST   /payments
       - Initiate single payment

POST   /payments/bulk
       - Initiate bulk payments

GET    /payments/{paymentId}
       - Get payment status

POST   /payments/{paymentId}/authorisation
       - Complete SCA authorization

GET    /confirmation-of-funds
       - Check if funds available

Consent Service Endpoints:
POST   /consents
       - Create new consent

GET    /consents/{consentId}
       - Get consent details

DELETE /consents/{consentId}
       - Revoke consent
```

### Security Requirements

#### Transport Security
```
TLS Requirements:
├── TLS 1.2 minimum (TLS 1.3 preferred)
├── Certificate validation
├── No fallback to weaker protocols
├── Perfect forward secrecy (PFS)
├── Certificate pinning recommended
└── HSTS header required
```

#### Authentication
```
Methods:
├── OAuth 2.0 with PKCE
├── Mutual TLS (MTLS)
├── Combination approaches
└── OpenID Connect for identity
```

#### Data Protection
```
Measures:
├── Encryption in transit (TLS)
├── Encryption at rest (sensitive data)
├── Data masking (PAN, card numbers)
├── Key management with HSM
├── Secure deletion on revocation
└── Regular security audits
```

### Consent Management

#### Consent Request Format
```
{
  "consent": {
    "consentId": "consent-001",
    "consentStatus": "valid",
    "access": {
      "accounts": [
        {
          "iban": "DE94500105000000012345",
          "currency": "EUR"
        }
      ],
      "allPsd2": "allAccounts",
      "availableAccounts": "allAccounts",
      "availableAccountsWithBalance": "allAccounts"
    },
    "recurringIndicator": true,
    "validUntil": "2026-11-19",
    "frequencyPerDay": 4,
    "lastActionDate": "2025-11-19",
    "consentTppInformation": {
      "name": "Example Fintech Ltd",
      "notificationUrl": "https://fintech.example/notification"
    }
  }
}
```

#### Consent Status Lifecycle
```
PENDING
    ├─ Created, awaiting customer authorization
    ↓
VALID
    ├─ Customer authorized
    ├─ AISP/PISP can use consent
    └─ Valid until expiry date
    ↓
EXPIRED
    ├─ Consent validity period ended
    └─ No access possible

OR

REVOKED
    ├─ Customer revoked consent
    └─ No further access

OR

PARTIALLY_AUTHORISED
    ├─ Customer partially authorized
    └─ Limited scope available

OR

REJECTED
    ├─ Customer denied authorization
    └─ AISP/PISP cannot access
```

## Compliance Testing

### Testing Checklist

```
Functional Testing:
├── [ ] AIS endpoints return correct data
├── [ ] PIS endpoints process payments correctly
├── [ ] SCA required for applicable transactions
├── [ ] Exemptions applied correctly
├── [ ] Consent creation and validation
├── [ ] Consent revocation works
├── [ ] Transaction filtering by consent scope
└── [ ] Proper error handling and messages

Security Testing:
├── [ ] TLS 1.2+ enforced
├── [ ] MTLS working correctly
├── [ ] OAuth 2.0 PKCE implemented
├── [ ] Token validation on each request
├── [ ] Scope validation enforced
├── [ ] Rate limiting prevents abuse
├── [ ] Request signing verified (if applicable)
└── [ ] No sensitive data in logs

Performance Testing:
├── [ ] API response time <1 second
├── [ ] Concurrent request handling
├── [ ] Load testing to capacity
├── [ ] SLA compliance (>99.5% uptime)
└── [ ] Database query optimization

Compliance Testing:
├── [ ] PSD2 data format compliance
├── [ ] Error codes standard
├── [ ] Consent logging complete
├── [ ] Audit trail maintained
├── [ ] GDPR data handling
└── [ ] Security standards met (FAPI, etc.)
```

## Common Implementation Challenges

### Challenge 1: Legacy System Integration
```
Problem:
├── Legacy core banking systems
├── No API interfaces
├── Complex data structures
└── Integration complexity

Solutions:
├── API wrapper/adapter layer
├── Data transformation logic
├── Intermediate database (API database)
├── Gradual migration approach
└── Third-party integration platforms
```

### Challenge 2: SCA Complexity
```
Problem:
├── Multiple authentication methods
├── Device management complexity
├── Fallback strategies
├── User confusion

Solutions:
├── Standardized UX flows
├── Clear user guidance
├── Fallback authentication options
├── User education programs
└── Helpdesk support
```

### Challenge 3: High API Availability
```
Problem:
├── 24/7 availability requirement
├── No maintenance windows
├── Performance degradation during peak
└── Regulatory penalties for downtime

Solutions:
├── Redundant infrastructure
├── Load balancing and clustering
├── Auto-scaling capabilities
├── Blue-green deployments
├── Disaster recovery planning
└── Monitoring and alerting
```

## Enforcement and Penalties

### Regulatory Oversight
```
Authorities:
├── National payment authority (each country)
├── Central banks
├── Financial regulators
└── Supervisory authorities

Inspection Frequency:
├── High-risk institutions: Annual
├── Medium-risk: Every 2-3 years
├── Low-risk: Every 4-5 years
```

### Penalty Scale
```
Penalties:
├── Non-compliance (initial): Warning
├── Continuing non-compliance: Administrative fine
├── Major violations: Up to €500,000
├── Serious breaches: Up to €1,000,000
├── Suspension of service rights
└── License revocation (extreme cases)
```

## PSD2 Transition and Future

### Current Status
- PSD2 fully implemented across EU/EEA
- Majority of banks providing API access
- Thousands of fintech companies using APIs
- Regular compliance monitoring

### PSD3 (Proposed)
- Extended access rights for payment data
- Support for additional service types
- Enhanced security measures
- Expanded consumer protections
- Proposed implementation 2027+

## Conclusion
PSD2 compliance is mandatory for all payment service providers and account servicing banks in EU/EEA. Implementation requires secure APIs, strong customer authentication, and proper consent management. While challenging, PSD2 has successfully enabled open banking innovation while protecting consumers through regulatory oversight and security requirements.
