# Financial API Standards

## Overview

Financial APIs are governed by a set of internationally recognized standards designed to ensure security, interoperability, and compliance.

## Key Standards

### 1. PSD2 (Revised Payment Services Directive 2)
**Scope**: EU regulation for electronic payments
**Key Components**:
- Strong Customer Authentication (SCA)
- Secure Communication
- Access Regulation
- Liability rules
- Exemptions for low-risk transactions

**Technical Requirements**:
- 90 character PIN minimum
- Certificate-based identification
- Rate limiting: 1 request per second per account
- 24-hour operation requirement
- Real-time transaction status

### 2. FAPI (Financial-grade API)
**Organization**: OpenID Foundation
**Versions**: 1.0-Final, 2.0-Draft

**Components**:
- **OAuth 2.0 Baseline** - Security profiles for authentication
- **FAPI 1 Level 1** - Standard security for open banking
- **FAPI 1 Level 2** - Enhanced security with mTLS
- **FAPI 2** - Modern security practices

**Security Features**:
- Signed request objects (JARM)
- mTLS with certificate pinning
- Mutual TLS for all connections
- Token binding
- Request/response signatures

### 3. OAuth 2.0
**Standard**: RFC 6749, RFC 6750, RFC 6819

**Financial-Grade Profiles**:
- Bearer Token Usage (RFC 6750)
- Proof Key for Public Clients (PKCE)
- Token Introspection (RFC 7662)
- Token Revocation (RFC 7009)
- Refresh Token Rotation

**Grant Types**:
```
Authorization Code Grant - Web apps
Refresh Token Grant - Token renewal
Client Credentials Grant - Backend services
```

### 4. OpenID Connect
**Standard**: OpenID Connect Core 1.0

**Features**:
- Identity verification
- User information endpoints
- ID token vs access token
- Claim normalization
- Hybrid flows

### 5. ISO 20022
**Standard**: International standard for financial messaging

**Components**:
- XML schema definition
- Data dictionary
- Business process modeling
- IBAN/BIC standards

**Examples**:
- `pain.001.003.02` - Credit Transfer Initiation
- `pain.008.003.02` - Direct Debit Initiation
- `camt.053.002.02` - Account Statement
- `camt.054.002.01` - Debit/Credit Notification

### 6. eIDAS (Electronic IDentification and Authentication)
**Scope**: EU regulation for digital signatures and authentication

**Key Points**:
- Qualified Electronic Certificates (QEC)
- Advanced Electronic Signatures
- Qualified Timestamps
- Recognized across EU

## Compliance Matrix

| Standard | Scope | Applies To | Key Requirements |
|----------|-------|-----------|------------------|
| PSD2 | EU | PSP, TPPs | SCA, Secure Comms, AIS/PIS |
| FAPI | Global | Banks, Fintechs | OAuth 2.0, mTLS, Signing |
| OAuth 2.0 | Global | All APIs | Authorization, Tokens |
| OIDC | Global | Identity | User Info, ID Tokens |
| ISO 20022 | Global | Messaging | Data Format, IBAN/BIC |
| eIDAS | EU | Digital Auth | Signatures, Certificates |

## Rate Limiting Standards

### PSD2 Requirements
- Maximum 1 request per second per dedicated account
- Exemptions for low-value transactions
- Different limits for AIS vs PIS
- Fair access requirements

### Industry Best Practices
- Distributed rate limiting across regions
- Time-window based quotas
- Priority for critical operations
- Clear error responses

## Strong Customer Authentication (SCA)

### Two-Factor Authentication
```
Factor 1: Something you know (password, PIN)
Factor 2: Something you have (phone, token) OR
         Something you are (biometric)
```

### SCA Exemptions
- Low-value transactions (€30 or less)
- Trusted beneficiaries
- Corporate payments above threshold
- Risk-based exemptions

### Secure Redirect
1. Customer initiates payment/access
2. Redirected to bank for SCA
3. Bank redirects back with authorization
4. No credentials shared with merchant

## Data Security Standards

### Encryption Requirements
- TLS 1.2 or higher for all communications
- AES-256 for data at rest
- Perfect forward secrecy recommended
- Certificate pinning for sensitive endpoints

### Authentication Methods
- Mutual TLS (mTLS) with certificates
- OAuth 2.0 with bearer tokens
- Signature-based authentication
- Challenge-response protocols

## API Documentation Standards

### Required Elements
- API versioning scheme
- Rate limit specifications
- Error code definitions
- Security requirements
- Sample requests/responses
- Webhook specifications

### Format
- OpenAPI/Swagger for REST APIs
- JSON Schema for data validation
- Examples in multiple languages

## Audit and Monitoring

### Required Logging
- All authentication attempts
- All data access requests
- All transaction initiations
- Failed requests with reasons
- Timestamp (UTC minimum)

### Retention Requirements
- Typically 5-7 years for financial transactions
- 6 months minimum for logs
- GDPR compliance for personal data

## Backward Compatibility

### API Evolution
- Maintain existing endpoints for 2+ versions
- Deprecation notice period (6-12 months)
- Clear migration path
- Automated update notifications

### Version Numbering
- Semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes = major version
- New features = minor version
- Bug fixes = patch version

## Testing Standards

### Security Testing
- Penetration testing
- OAuth flow validation
- mTLS certificate validation
- Token expiration handling
- Rate limit enforcement

### Functional Testing
- API contract testing
- Data validation
- Error handling
- Webhook delivery
- Retry logic

## Regulatory Compliance

### GDPR Compliance
- Explicit consent for data access
- Right to data portability
- Data deletion upon request
- Breach notification requirements

### AML/KYC
- Know Your Customer verification
- Anti-Money Laundering checks
- Transaction monitoring
- Suspicious activity reporting

## References

- PSD2 Directive: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366
- FAPI Specifications: https://openid.net/fapi/
- OAuth 2.0: https://tools.ietf.org/html/rfc6749
- OpenID Connect: https://openid.net/connect/
- ISO 20022: https://www.iso20022.org/
