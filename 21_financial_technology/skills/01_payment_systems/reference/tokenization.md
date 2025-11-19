# Tokenization Reference

## Overview

Tokenization is the process of replacing sensitive payment card data (PAN, expiry, CVV) with a non-sensitive token that can be used to represent the same card in transactions. This is a critical security control for PCI-DSS compliance and data protection.

## Token Types

### Network Tokens
**Issued by**: Card networks (Visa, Mastercard, Amex)
**Characteristics**:
- Replace the original card number
- Valid across multiple merchants
- Issued by the card network
- More fraud-resistant than merchant tokens

**Benefits**:
- Network decides when token expires
- Automatic replacement when card is reissued
- Lower fraud rates
- Better for recurring billing

**Implementation**:
```
1. Cardholder saves card with payment processor
2. Processor registers with card network (Network Tokenization Service)
3. Card network generates network token (looks like card number)
4. Processor returns token to customer's wallet
5. Subsequent transactions use network token

Token Format Example:
Original: 4111-1111-1111-1111
Token: 4532-0123-4567-8910 (different number, routes to original issuer)
```

### Merchant Tokens
**Issued by**: Merchant/Payment processor
**Characteristics**:
- Only valid with the issuing merchant/processor
- Cannot be used elsewhere
- Merchant is responsible for token security
- Non-standardized formats

**Benefits**:
- Quick implementation
- Full control over token lifecycle
- Can include metadata
- Flexible expiry policies

**Limitations**:
- Higher fraud rates
- Cannot be shared across processors
- Merchant must update on card changes
- Requires PCI-DSS compliance

### Hosted Tokens
**Issued by**: Payment service provider
**Characteristics**:
- Token stored with PSP (Stripe, PayPal, etc.)
- Payment processor handles token security
- Merchant stores payment processor customer ID
- Abstraction from actual card data

**Best For**:
- Merchants wanting to avoid PCI scope
- Multi-transaction scenarios
- Subscription billing
- Marketplace payments

## Tokenization Standards

### PCI-DSS Requirements
```
Standard Requirement 3.2:
"Do not store sensitive authentication data after authorization"

Sensitive Data includes:
- CVC/CVV codes (full magnetic stripe read data)
- Chip unique data
- PIN blocks
- PINs
- PIN blocks
- Full card number (even if encrypted)
- CVC/CVV
- Expiry date (if full card number stored)
```

### EMV Token Requestor ID (TRID)
```
Requirement: Every tokenization service provider must have a unique TRID
Format: 40-bit number issued by card network
Identifies: Which service provider created the token
Used for: Routing and reconciliation
```

## Tokenization Process

### Step-by-Step Implementation

#### 1. Card Data Collection
```
Option A: Direct Card Entry
- Customer enters card details in payment form
- Form uses HTTPS (TLS 1.2 minimum)
- Data sent directly to tokenization service
- Merchant never sees full PAN

Option B: Hosted Payment Page
- Merchant redirects to payment provider's page
- Customer enters card details
- Payment provider collects and tokenizes
- Merchant receives token via callback

Option C: Mobile Wallet
- Customer uses Apple Pay, Google Pay
- Device creates encrypted wrapper
- Token included in encrypted payload
- Merchant processes token
```

#### 2. Tokenization Service Processing
```
1. Receive card data over secure channel
2. Validate card format (Luhn check, length, BIN)
3. Check for fraud/suspicious activity
4. Retrieve card metadata from network
5. Generate unique token
6. Store mapping: Token -> PAN (encrypted)
7. Return token to requestor
8. Delete raw card data from memory
```

#### 3. Token Vaulting
```
Secure Token Storage
- Encrypted database
- Key management service (AWS KMS, Azure Key Vault)
- Role-based access control
- Audit logging of all access
- Tokenization service manages lifecycle
- Automatic re-tokenization on card reissue

Storage Structure:
{
  "token_id": "tok_1A2B3C4D5E6F",
  "encrypted_pan": "...",
  "card_brand": "visa",
  "last_four": "4242",
  "expiry_month": 12,
  "expiry_year": 2025,
  "fingerprint": "fp_...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

#### 4. Transaction Processing with Tokens
```
Original Card Transaction:
Merchant -> Payment Processor -> Acquiring Bank -> Card Network
            (Has card number)

Token-Based Transaction:
Merchant -> Payment Processor -> Acquiring Bank -> Card Network
            (Has token only)                      (Token mapped to original)

Network validates token against original issuer
Original issuer approves/declines
Response goes back through chain
```

## Network Tokenization Implementations

### Visa Token Service (VTS)
```
How it Works:
1. Cardholder stores card in digital wallet or with merchant
2. Payment processor sends card data to Visa
3. Visa generates network token
4. Token looks like a real card number
5. Routes to original card through Visa network
6. Automatically updates when card changes

Benefits:
- Fraud monitoring by Visa
- Automatic token updates
- Accepted at all Visa merchants
- Liability protection

Implementation:
POST /tokenization/v1/vts/
{
  "cardNumber": "4111111111111111",
  "expiryMonth": 12,
  "expiryYear": 2025,
  "cvv": "123"
}

Response:
{
  "networkToken": "4532012345678910",
  "expiryMonth": 12,
  "expiryYear": 2025,
  "iin": "453201",
  "last4": "8910"
}
```

### Mastercard Digital Enablement Service (MDES)
```
How it Works:
1. Card stored with payment service provider
2. Provider sends card to Mastercard
3. Mastercard generates network token and cryptogram
4. Token used for transactions
5. Cryptogram validates token authenticity

Benefits:
- Cryptographic validation prevents token fraud
- Device fingerprinting support
- Biometric authentication integration
- Automatic token management

Token Structure:
{
  "digitizedToken": "5425123456789010",
  "cryptogram": "AgAAA0ABC...",
  "tokenExpiry": "2025-12"
}
```

### American Express Token Service
```
How it Works:
1. Card registered with Amex-enabled service
2. Service provisioned by Amex
3. Token generated by Amex
4. Token has same format as Amex card

Characteristics:
- Limited network (only Amex-enabled merchants)
- Strong fraud controls
- Premium cardholder protection
```

## Tokenization Security

### Key Management

```
Requirements (PCI-DSS 3.6):
- Encryption keys must be rotated regularly (annually minimum)
- Keys must be stored in secure hardware security module (HSM)
- Key generation must be cryptographically secure
- Keys must not be stored in plaintext
- Access to keys must be logged

Implementation Example:
AWS KMS Integration:
1. Master key stored in HSM
2. Application never accesses master key
3. KMS encrypts/decrypts on behalf of application
4. All key operations logged to CloudTrail
5. Keys automatically rotated annually
```

### Encryption Standards

```
Symmetric Encryption (for storage):
- AES-256 with GCM mode
- IV (Initialization Vector) unique per record
- Format: IV || Ciphertext || Authentication Tag

Asymmetric Encryption (for transmission):
- RSA-2048 minimum
- TLS 1.2+ for all network communication
- Certificate pinning recommended

Example:
Encrypted Token = {
  "iv": "random_16_bytes",
  "ciphertext": "aes_encrypted_data",
  "tag": "authentication_tag",
  "algorithm": "AES-256-GCM"
}
```

### Access Control

```
Role-Based Access:
- Development team: Read tokenized data, test environment
- Payment processor: Decrypt tokens for authorization
- Compliance team: Audit logs of all access
- Merchants: Only access own tokens

Implementation:
- Database-level encryption
- API authentication (mutual TLS)
- API key rotation (90 days)
- Audit logging for all token access
```

## Token Lifecycle Management

### Token Expiration

```
Triggers for Token Expiration:
1. Physical card expiration
   - Network notifies when card issued expires
   - Token automatically expires

2. Card replacement
   - New card issued
   - Old token invalidated
   - New token issued

3. Cardholder request
   - Revoke token immediately
   - Block future transactions

4. Merchant request
   - Remove stored token
   - Prevent unauthorized reuse

Typical Lifespans:
- Network tokens: Until card expires or account closed
- Merchant tokens: Merchant-defined (1-3 years typical)
- One-time tokens: Single transaction only
```

### Token Reissue Flow

```
When Card Network Updates:
1. Card network detects change (new expiry, fraud, etc.)
2. Network sends notification to tokenization service
3. Service generates new token
4. Service maps old token -> new token
5. Merchants should transition to new token
6. Old token deprecated (30-90 day grace period)

Implementation:
POST /tokens/{old_token_id}/reissue
{
  "reason": "card_expiration"
}

Response:
{
  "old_token": "tok_1A2B3C4D5E6F",
  "new_token": "tok_2X3Y4Z5W6V7U",
  "transition_deadline": "2025-03-15T00:00:00Z"
}
```

## Token Format Standards

### Vault Format
```
Non-PCI-compliant token (random string):
tok_1A2B3C4D5E6F7G8H9I0J

Network Token Format (looks like card):
4532012345678910 (54 = Mastercard BIN)

One-Time Token Format:
ott_abc123def456ghi789jkl

Fingerprint (consistent identifier):
fp_53c64aadb32f56daf2a5be8ec64c7e15
```

## Common Tokenization Mistakes

### 1. Storing Full Card Numbers
```
WRONG:
payment_method = {
  "card_number": "4111111111111111",
  "expiry": "12/25",
  "cvv": "123"
}

RIGHT:
payment_method = {
  "token": "tok_1A2B3C4D5E6F",
  "last_four": "1111",
  "expiry": "12/25"
}
```

### 2. Storing CVV
```
PCI-DSS explicitly forbids storing CVV after authorization
NEVER store: "cvv": "123"
Always request fresh CVV for important operations
```

### 3. Inconsistent Token Handling
```
WRONG:
- Different expiration policies
- Unencrypted token storage
- No audit logging

RIGHT:
- Centralized token management
- Encrypted vault with audit logs
- Clear lifecycle policies
- Regular key rotation
```

### 4. Not Using Network Tokens
```
WRONG:
- Only using merchant tokens
- Higher fraud rates
- Customer can't move between merchants

RIGHT:
- Prefer network tokens where available
- Fall back to merchant tokens
- Regular network token re-registration
```

## Token Migration Strategies

### Greenfield Implementation
```
1. Implement tokenization from day one
2. All new payment methods stored as tokens
3. No card data ever stored in merchant systems
4. Simplifies PCI scope
```

### Legacy System Migration
```
Phase 1 (Months 1-2):
- Implement tokenization for new customers
- Don't tokenize existing stored cards yet
- Begin vaulting new tokens

Phase 2 (Months 3-6):
- Batch re-tokenize existing stored cards
- Update payment database with tokens
- Maintain migration ledger

Phase 3 (Months 6-12):
- Monitor for any re-tokenization failures
- Decommission old card storage
- Complete audit trail cleanup

Testing:
- Batch tokenization on test data first
- Validate token format
- Test all transaction types with tokens
- Confirm audit logs
```

## Token Fraud Prevention

### Token-Specific Controls

```
1. Token Binding
   - Bind token to specific merchant
   - Token only works with issuing merchant
   - Prevents token reuse across merchants

2. Geographic Binding
   - Restrict token use to specific regions
   - Detect unusual locations
   - Flag international use of domestic tokens

3. Device Binding
   - Bind token to specific device
   - Token includes device fingerprint
   - Changing device requires re-auth

4. Amount Thresholds
   - Set velocity limits on token transactions
   - Alert on unusually large transactions
   - Automatic fraud review triggers
```

## Tokenization Compliance

### PCI-DSS Scope Reduction

```
With Tokenization:
- Merchant not in PCI scope for tokenized cards
- Payment processor in scope
- Merchant only handles tokens
- Significant compliance burden reduction

Without Tokenization:
- Merchant in PCI scope level 1-2
- Annual audits required
- Significant compliance costs
- Higher breach liability
```

### Regulatory Alignment

```
GDPR (Europe):
- Token counts as pseudonymized data
- Reduces personal data handling
- Still requires privacy controls
- Data subject rights still apply

CCPA (California):
- Token can facilitate data deletion
- Maintain token-to-PAN mapping for deletion
- Consider tokenization for compliance

PCI-DSS:
- Tokenization recommended (Req 3.2.1)
- Network tokens reduce fraud
- Proper key management essential
```
