# 3D Secure Reference

## Overview
3D Secure (3DS) adds an additional authentication layer to card transactions. Customer authenticates with card issuer, reducing fraud and liability for merchants.

## 3D Secure Versions

### 3D Secure 1.0 (Legacy)

**Flow**
```
1. Cardholder initiates transaction
2. Merchant redirects to card issuer
3. Cardholder enters password (Verified by Visa) or passcode (MasterCard SecureCode)
4. Issuer validates authentication
5. Authentication result returned to merchant
6. Transaction processed with authentication liability shift
```

**Disadvantages**
- High cardholder friction (redirects)
- Poor mobile experience
- High abandonment rates (20-30%)
- Visible security issues

### 3D Secure 2.0 / 3D Secure 2.1

**Improvements**
- Risk-based authentication (not all transactions require password)
- Native mobile app support (no redirects)
- Better user experience
- Additional data elements sent to issuers
- Biometric authentication support

**Flow - Frictionless**
```
1. Cardholder initiates transaction
2. Additional data sent to issuer (device, behavioral, location)
3. Issuer assessment of fraud risk
4. Low-risk transactions: Auto-approved (no password)
5. High-risk transactions: Additional authentication required
```

**Flow - Challenge**
```
1. Issuer determines authentication needed
2. Customer presented with authentication challenge
3. Options: Password, OTP, biometric
4. Cardholder authenticates
5. Result returned to merchant
```

## 3D Secure Message Flow

### Classic 3DS 1.0
```
Cardholder Browser <-> Merchant <-> Payment Gateway <-> Card Issuer
                                                          (ACS - Access Control Server)
```

### 3D Secure 2.0 Three-Domain Model
```
Domain 1: Merchant/Acquirer
  - Collects transaction data
  - Sends authentication request

Domain 2: Issuer/ACS
  - Assesses fraud risk
  - Performs authentication
  - Returns result

Domain 3: Interoperability
  - Directory Server
  - Routes messages between domains
  - Manages protocol versions
```

## Data Elements Sent to Issuer (3DS 2.0)

### Transaction Data
- Transaction amount
- Currency
- Merchant name and category
- Transaction date/time
- Order description
- Shipping address
- Billing address

### Cardholder Data
- Email address
- Phone number
- Device ID
- IP address
- Purchase history
- Account age
- Account activity

### Device Data
- Device fingerprint
- Browser type and version
- Device type (mobile, desktop)
- Operating system
- Timezone
- Language
- User-Agent

### Behavioral Data
- Authentication history
- Shipping address change
- Account modification history
- First transaction on device
- Velocity (transactions in time period)

## Risk Assessment in 3DS 2.0

### Issuer Risk Evaluation
```
Low Risk (Score 0-20):
- Known cardholder
- Known device
- Normal transaction amount
- Normal merchant
- Normal time of day

Medium Risk (Score 20-60):
- New device
- Unusual amount
- Unusual merchant
- Geographic anomaly
- Unusual time

High Risk (Score 60-100):
- Potentially fraudulent
- Multiple risk factors
- Impossible geography
- Velocity spike
- Behavioral anomaly
```

### Decision Logic
```
Score 0-30: Approve without authentication
Score 30-70: Request authentication
Score 70-100: Decline or strong authentication
```

## Authentication Methods in 3DS

### Password/Passcode
- Cardholder enters stored password
- Simple but low security
- User friction

### One-Time Password (OTP)
- SMS or email OTP
- Moderate security
- Delivery delays possible

### Biometric
- Fingerprint or facial recognition
- High security
- Native mobile support
- High user acceptance

### Multi-Factor
- Combination of methods
- Highest security
- More user friction

## Exemptions & Out-of-Scope Transactions

### 3DS Not Required
```
Low-value transactions:
- Transactions < €30 (soft limit)
- Multiple exemptions available

Recurring transactions:
- Subscription renewals
- Installment payments
- Can store authentication once

Whitelisted merchants:
- Trusted merchant exemption
- Cardholder has approved
- Reduced authentication

Cardholder-initiated transactions:
- Low fraud risk
- May skip authentication
```

### Risk-Based Exemption
```
Exemption available if:
- Transaction risk score < threshold
- Merchant track record good
- Cardholder previously approved
- Satisfies regulatory requirements
```

## Liability Shift

### With 3DS Authentication
```
Scenario: Cardholder disputes transaction as unauthorized

Result:
- Cardholder authenticated with issuer
- Issuer liable for fraud (not merchant)
- Merchant protected from chargeback
- Authentication proof on record
```

### Without 3DS
```
Scenario: Cardholder disputes transaction as unauthorized

Result:
- No strong authentication performed
- Merchant liable for chargeback
- Acquirer/Processor may hold merchant liable
- Increased chargeback costs
```

### Partial Liability
```
3DS Attempted but Failed:
- Cardholder couldn't complete
- Transaction processed without auth
- Liability shift may not apply
- Depends on decline/bypass rules
```

## Integration Architecture

### Merchant Server Integration
```
1. Merchant collects transaction data
2. Calls Payment Gateway API with 3DS parameters
3. Gateway validates 3DS eligibility
4. Initiates 3DS authentication
5. Returns authentication status
6. Merchant receives cavv (authentication verification value)
7. Transaction processed with cavv
```

### Client-Side Integration
```
1. Payment form collects card data
2. Client sends card to tokenization endpoint
3. Three-domain-model invoked
4. Challenge presented if needed (mobile SDK)
5. Authentication result returned
6. Token used for transaction
```

### Network API Integration
```
1. Merchant connected to Visa/Mastercard network
2. Direct integration with ACS (issuer)
3. Real-time authentication
4. Instant result to merchant
5. No redirect needed
```

## 3DS Response Codes

### Authentication Status
```
Y (Yes): Authenticated
  - Password verified
  - Liability shift applies
  - Merchant protected

N (No): Not Authenticated
  - Failed authentication
  - Liability shift doesn't apply
  - Merchant may decline

U (Unavailable): Authentication Unavailable
  - ACS unavailable
  - Issuer doesn't participate
  - Merchant decision on proceed

A (Attempt): Authentication Attempted
  - ACS tried but inconclusive
  - Some liability shift may apply
```

### Cavv (Cryptogram Authentication Verification Value)
```
High-value token representing:
- Authentication was performed
- Issuer verified cardholder
- Cannot be forged or replayed

Sent with transaction to processor
Stored for chargeback protection
```

## 3DS Optimization

### Frictionless Percentage
```
Goal: Maximize frictionless transactions
Target: 70-85% frictionless for low-risk merchants
Low frictionless: May indicate over-conservative
High frictionless: May indicate under-secure
```

### Challenge Optimization
```
Ask when necessary:
- High fraud risk
- Regulatory requirement
- High-value transactions

Avoid unnecessary challenge:
- Increasing abandonment
- Reducing conversion
- Frustrating customers
```

### Device Detection
```
Mobile transactions:
- Prefer biometric authentication
- Native app integration
- Minimize friction

Desktop transactions:
- Password or OTP
- Slower networks acceptable
```

## Fraud Prevention with 3DS

### Prevented Fraud Types
- Card-not-present fraud (identity theft)
- Stolen card usage
- Account takeover with card data
- First-time fraudster testing

### Not Prevented
- Friendly fraud (cardholder disputes legitimate transaction)
- Merchant fraud (merchant-customer collusion)
- Merchant system compromise
- Issuer-side fraud

## Regulatory & Compliance

### PCI DSS (Payment Card Industry Data Security Standard)
- 3DS reduces scope of compliance
- Reduces card data handling requirements
- Encryption of authentication data

### Strong Customer Authentication (SCA) - Europe
```
PSD2 Regulatory Requirement:
- Strong authentication for online card payments
- 3DS 2.0 satisfies SCA requirement
- Exemptions: Low-value, recurring, low-risk
- Enforcement: January 2021
```

### Regional Variations
```
Europe (PSD2): 3DS mandatory (with exemptions)
US: 3DS recommended, not mandated
Asia: Varies by country
Latin America: Growing mandate
```

## 3DS Metrics

### Transaction Metrics
- Total transactions evaluated for 3DS
- Frictionless rate
- Challenge rate
- Decline rate

### Performance Metrics
- Authentication success rate
- Abandonment rate (cardholder drops out)
- Conversion rate
- Average time to authenticate

### Fraud Metrics
- Fraud rate in 3DS transactions
- Chargeback rate
- Liability shift achieved
- Fraud prevented

### User Experience Metrics
- Customer satisfaction
- Support inquiries about 3DS
- Device type breakdown
- Authentication method preference
