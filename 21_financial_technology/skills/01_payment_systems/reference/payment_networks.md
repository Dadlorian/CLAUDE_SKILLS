# Payment Networks Reference

## Overview

Payment networks are the infrastructure that connect merchants, acquiring banks, issuing banks, and consumers. They set standards, manage clearing and settlement, and provide the backbone for payment processing globally.

## Major Card Networks

### Visa
**Market Share**: ~54% of global transaction volume
**Characteristics**:
- Operates as a four-party model: Visa, Acquiring Bank, Issuing Bank, Cardholder
- Visa Direct for B2B, P2P, and merchant payouts
- Visa DPM (Deferred Payment Model) for installments
- Real-time processing with Visa Real-Time Transaction Manager

**Key Products**:
```
- Visa Classic/Gold/Platinum (consumer cards)
- Visa Infinite (premium)
- Visa Electron (debit)
- Visa Prepaid programs
- Visa Paywave (contactless)
```

**Settlement Timeline**: T+1 (next business day), with real-time capabilities

### Mastercard
**Market Share**: ~24% of global transaction volume
**Characteristics**:
- Similar four-party model to Visa
- Mastercard Send for payouts and P2P
- Click to Pay for digital payments
- Mastercard Track for fraud intelligence

**Key Products**:
```
- Standard Mastercard
- Mastercard World/Titanium (premium)
- Maestro (debit and prepaid)
- Mastercard Digital Enablement Service
```

**Settlement Timeline**: T+1 to T+2

### American Express
**Market Share**: ~6% of global transaction volume
**Characteristics**:
- Operates as a three-party model (Amex, Merchant, Cardholder)
- Higher approval rates due to direct cardholder relationships
- Premium audience positioning
- Stronger data on spending patterns

**Key Products**:
```
- Personal Cards (Green, Gold, Platinum, Centurion)
- Business Cards
- Corporate Cards
- Amex EveryDay
```

**Settlement Timeline**: T+1 to T+3
**Interchange**: Typically 2-3% higher than Visa/Mastercard

### Discover
**Market Share**: ~1% globally, ~7% in North America
**Characteristics**:
- Also operates as a three-party model
- Strong in USA and Japan
- Popular for cash back rewards
- Lower fraud rates

**Key Products**:
```
- Discover It (consumer)
- Discover Business
- Discover Student
```

**Settlement Timeline**: T+1

## Network Standards

### ISO 8583 Standard
International standard for financial transaction messaging

```
Message Structure:
- Message Type Indicator (MTI): 4 digits (e.g., 0100 = request, 0110 = response)
- Bitmap: Indicates which fields are present
- Data Elements: Field value and length

Example: 0100 (authorization request)
```

### ISO 20022 Standard
Modern XML-based standard for financial messaging
- Replacing ISO 8583 for cross-border payments
- Used in real-time payment networks
- More comprehensive than ISO 8583

## ACH (Automated Clearing House)
**USA Electronic Funds Transfer System**
```
Type: Debit/Credit transfers
Processing: 1-2 business days
Volume: ~15 billion transactions annually
Operators: Federal Reserve and Nacha (The EFT Association)
Limits: Typically $25,000-$100,000 per transaction
```

**ACH Transactions**:
- Direct Deposit (payroll)
- Bill Payment
- P2P Transfer
- Government Benefits

## Wire Transfers

### Domestic Wires (USA - Federal Reserve)
```
Cost: $15-30 per wire
Speed: Same-day delivery (before cutoff)
Limits: No maximum
Irrevocable: Yes (difficult to reverse)
Used for: Large payments, business transactions
```

### International Wires (SWIFT)
```
Standards: SWIFT (Society for Worldwide Interbank Financial Telecommunication)
Network: 11,000+ financial institutions
Message Format: SWIFT MT103 for international payments
Speed: 1-3 business days (typically)
Cost: $15-50 per wire + intermediary bank fees
Exchange Rate: Variable, banks add 2-5% markup
```

## Real-Time Payment Networks

### FedNow (USA - Federal Reserve)
```
Launch: 2023
Processing: Sub-second settlement
Available: 24/7/365
Limits: Up to $500,000
Use Cases: Urgent payments, B2B, P2P
```

### RTP (Real-Time Payments - USA)
```
Operator: The Clearing House
Processing: Real-time (seconds)
Availability: 24/7
Limits: Up to $1 million per transaction
Status: 700+ financial institutions (growing)
```

### SEPA Instant Credit Transfer (Europe)
```
Coverage: All SEPA countries
Processing: 10 seconds or less
Available: 24/7/365
Limits: Up to €100,000
Standard: ISO 20022
```

### India Real Time Gross Settlement
```
System: RTGS (Real Time Gross Settlement)
Processing: 1 minute to 30 minutes
Availability: 9 AM - 4:30 PM (weekdays)
Operator: Reserve Bank of India
Limits: Minimum ₹2 lakhs
```

## Interchange Fees

### Visa & Mastercard Interchange
**Factors Affecting Rates**:
- Transaction type (e-commerce vs. in-store)
- Card type (debit, credit, premium)
- Industry/Merchant category code
- Transaction size
- Cardholder and issuer country

**Typical Rates**:
```
E-commerce Credit Card: 1.5% - 2.5%
E-commerce Debit Card: 0.5% - 1.0%
In-store Credit Card: 2.0% - 3.0%
In-store Debit Card: 0.5% - 1.5%
```

### Amex Interchange
- Typically 2.5% - 3.5% for consumer cards
- Higher for premium cards (up to 4%)
- No separate interchange; included in discount rate

## Network Regulations

### PCI-DSS (Payment Card Industry Data Security Standard)
- Applies to all merchants handling card data
- 12 requirements covering security, compliance, monitoring
- Annual audit required for high-volume merchants
- Certification levels based on transaction volume

### Network Specific Requirements
```
Visa:
- Token adoption for e-commerce
- Chip liability shift
- Fall-through authentication
- Network monitoring for fraud

Mastercard:
- Site Data Protection Program
- Network Security Program
- Detailed Transaction Monitoring

Amex:
- Merchant Code validation
- Account Data Security Program
```

## Network APIs

### Visa Developer Platform
```
Available APIs:
- Payment Gateway APIs
- Debit/Credit Transaction APIs
- Merchant Inquiry APIs
- Tokenization API
- Direct API for balance transfers

Rate Limits: 10,000 requests/minute
Documentation: https://developer.visa.com
```

### Mastercard Developer Zone
```
Available APIs:
- Mastercard Gateway API
- Fraud Scoring
- Marketplace API
- Card Configuration API

Rate Limits: Varies by API
Documentation: https://developer.mastercard.com
```

### American Express
```
Limited Public APIs
Focus: Direct partnerships
Available:
- Amex Connect API (for partners)
- Data & Insights APIs

Requires: Direct relationship with Amex
```

## Network Fraud Controls

### Visa Fraud Tools
```
Visa Advanced Authorization (VAA)
- Real-time fraud scoring
- Dynamic interaction to cardholder
- Increased approval rates

Visa Secure (3D Secure)
- Enhanced authentication
- Low friction flow
- Liability shift capability
```

### Mastercard Fraud Tools
```
Mastercard Identity Check (3D Secure)
- Biometric authentication
- Device fingerprinting
- Risk-based authentication

Mastercard Advisors
- Real-time fraud scoring
- Recommendation engine
```

## Settlement and Clearing

### Clearing Process
```
1. Transaction Authorization (real-time)
2. Clearing (batch, typically daily)
3. Funding (acquiring bank sends funds)
4. Settlement (issuing bank deducts from cardholder)

Timeline: T+1 to T+2 for most transactions
```

### Net Settlement
```
Day 1: Acquire transactions
Day 2: Network clears transactions
       Interchange calculations
       Fees deducted
       Net amount calculated
Day 3: Funds transferred to merchant acquiring bank
       Acquiring bank transfers funds to merchant (T+1 to T+3)
```

## Emerging Networks

### Buy Now, Pay Later (BNPL)
```
Players: Affirm, Klarna, Afterpay, Sezzle
Model: Consumer credit lines
Processing: Multiple installments
Merchant Fees: 2-10% (higher than cards)
```

### Digital Wallets
```
Apple Pay, Google Pay, Samsung Pay
Process:
1. Cardholder adds card to digital wallet
2. Card data tokenized
3. Transaction uses tokenized value
4. Routing goes through original network (Visa, MC, Amex)
```

### Cryptocurrency Networks
```
Bitcoin, Ethereum, Stablecoins
Settlement: On-chain (10 minutes - hours)
Volatility: High (requires hedging)
Regulation: Evolving globally
Use Cases: International settlements, cross-border B2B
```

## Key Metrics

### Network Performance
- **Authorization Rate**: % of transactions approved by network
- **Decline Rate**: % of transactions declined
- **Fraud Rate**: % of fraudulent transactions
- **Chargeback Rate**: % of transactions disputed
- **Settlement Time**: Average time from authorization to funds received

### Typical Benchmarks
```
Authorization Success Rate: 95-98%
Fraud Rate (overall): 0.05-0.15%
Chargeback Rate: 0.05-0.5% (industry dependent)
Settlement Time: 1-3 business days
```
