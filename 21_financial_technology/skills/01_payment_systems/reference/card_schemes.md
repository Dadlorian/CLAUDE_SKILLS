# Card Schemes Reference

## Overview

Card schemes are the rules, standards, and requirements that govern how payment cards operate within a network. Major schemes include Visa, Mastercard, American Express, Discover, and emerging schemes like JCB, UnionPay, and Mir.

## Visa Card Schemes

### Visa Product Lines

```
Consumer Cards:
- Visa Classic: Standard card, wide acceptance
- Visa Gold: Premium features, higher rewards
- Visa Platinum: High-end, concierge services
- Visa Infinite: Ultra-premium, exclusive benefits
- Visa Signature: Mid-tier benefits
- Visa Electron: Debit-only, limited credit
- Visa Propel: Business cards

Business Cards:
- Visa Commercial: Corporate cards for expenses
- Visa Government: Government employee cards
- Visa Large Ticket: High-limit cards for large purchases

Prepaid Cards:
- Visa Prepaid: Load with funds, use like debit
- Visa Healthcare: FSA/HSA eligible
- Visa Gift: Pre-loaded gift cards
- Visa B2B: Virtual cards for business payments

Regional Variants:
- Visa Electron: Debit in Europe/Asia
- Visa Plus: ATM network
- Visa Interlink: Debit cards
```

### Visa Technical Requirements

```
Chip Specification (EMV):
- Contact-based smartchip
- 8 contacts on card
- Cryptographic authentication
- Application Dedicated File (ADF)
- Data Authentication Code (DAC)

Contactless (NFC):
- Radio frequency (13.56 MHz)
- Near Field Communication
- CVC-less transaction below limits
- Transaction limit: $25-100 (varies by issuer)

Magnetic Stripe (Legacy):
- Track 1: Full card data including name
- Track 2: Card number, expiry, service code
- Still required for backwards compatibility

Security:
- Visa Dynamic Passcode (VDP)
- Real-time tokenization
- Network Tokenization with VTS
- 3D Secure authentication
- Chip liability shift (2015+)
```

### Visa Interchange Categories

```
Qualified Transaction (Lower Rate):
- Signature debit card transaction
- PIN transaction below interchange caps
- Typical rate: 0.05% + $0.21

Mid-Qualified (Medium Rate):
- Non-qualified categories
- Card not present transactions
- Business cards
- Typical rate: 1.51% + $0.95

Non-Qualified (Higher Rate):
- Rewards cards
- Premium/Infinite cards
- International transactions
- Corporate cards
- Typical rate: 2.51% + $0.95

Transaction-Type Specific:
- E-commerce: 1.51%-2.51%
- Card-not-present: 1.81%-2.51%
- In-store (chip): 0.05%-1.51%
- In-store (mag stripe): 0.30%-2.51%
- International: 2.00%-2.51%
```

## Mastercard Card Schemes

### Mastercard Product Lines

```
Consumer Debit:
- Mastercard Debit: Standard debit card
- Mastercard Prepaid: Prepaid and stored value
- Mastercard Healthcare: HSA/FSA cards

Consumer Credit:
- Mastercard Standard: Entry-level credit
- Mastercard World: Mid-tier benefits
- Mastercard World Signia: Premium

Consumer Business:
- Mastercard World Business
- Mastercard Corporate
- Mastercard Government

Youth/Student Programs:
- Mastercard Student: For college students
- Youth Cards: Banking for minors

Specialty Programs:
- Mastercard Rewards: Rewards optimization
- Mastercard Assist: Underbanked populations
- Mastercard Healthcare: Medical cards
```

### Mastercard Technical Standards

```
Chip Specifications (EMV):
- Contact-based smartchip
- 8-contact interface
- EMV transaction processing
- Application Cryptogram Generation (ACG)

Contactless Technology:
- Radio frequency interface
- Mastercard Pay Pass
- Quick transaction processing
- CVC-less for small amounts

Security Features:
- Mastercard Advisors (ML-based fraud)
- Mastercard Identity Check (3D Secure)
- Mastercard Digital Enablement Service (MDES)
- Device-based security
- Biometric authentication support

Magnetic Stripe (Legacy):
- Track 1 and Track 2 data
- Full PAN and expiry encoded
- Service code for transaction type
```

### Mastercard Interchange Categories

```
Interchange Rates by Card Type:

Debit Cards:
- PIN debit: 0.05% + $0.21 (same as Visa)
- Signature debit: 0.05% + $0.21

Credit Cards:
- Qualified: 1.51% + $0.95
- Mid-qualified: 1.66% + $0.95
- Non-qualified: 1.88% + $0.95

Regional Variations:
- US Domestic: Standard rates above
- US-to-International: 1.80%-2.20% + $0.95
- International-to-US: 2.00%-2.50% + $0.95

Special Categories:
- Corporate cards: 2.20%-2.70%
- Purchasing cards: 2.00%-2.50%
- Rewards cards: 1.80%-2.50%
```

## American Express

### American Express Product Lines

```
Consumer Cards:
- Green Card: Entry-level, no foreign transaction fee
- Gold Card: Premium benefits, dining rewards
- Platinum Card: Ultra-premium, concierge services
- Centurion Card (Black Card): Exclusive, invitation-only
- EveryDay: No annual fee, everyday rewards

Business Cards:
- Business Green, Gold, Platinum
- Corporate Cards: Multi-user accounts
- Business Centurion: Premium business

Specialty Products:
- Gift Cards
- Prepaid Cards (limited market)
- Corporate Travel Cards
```

### American Express Three-Party Model

```
Unique Structure:
- Amex (Merchant acquirer and card issuer)
- Cardholder
- Merchant

NOT a typical four-party model like Visa/Mastercard

Implications:
- Amex knows cardholder directly
- Better data on spending patterns
- Can set own interchange rates
- Higher rates than Visa/Mastercard
- Higher approval rates (known customer)
- Different settlement processes

Amex Discount Rate (MDR):
- Premium cards: 3.0%-4.0%
- Standard cards: 2.5%-3.5%
- No separate interchange/assessment
- All-in rate to merchant
```

### American Express Security

```
Chip Implementation:
- EMV chip for in-store
- EMV for mag stripe fallback
- Contact-based authentication

Contactless:
- Limited in US (growing)
- Chip-preferred for security

3D Secure (Amex Identity Check):
- Account verification
- OTP or passive authentication
- Liability shift with 3DS

Tokenization:
- Amex Token Service
- Network-level tokenization
- Limited to Amex ecosystem
- Automatic updates with card changes
```

### American Express Interchange (No Separate Assessment)

```
All-In Discount Rate (Merchant Pays):

Premium Cards (Gold, Platinum):
- Card Present: 3.5%-4.0%
- Card Not Present: 3.8%-4.2%
- International: 4.0%-4.5%

Standard Cards (Green, EveryDay):
- Card Present: 2.5%-3.0%
- Card Not Present: 2.8%-3.2%
- International: 3.0%-3.5%

Differences from Visa/Mastercard:
- 1-1.5% higher than Visa for same card tier
- No separate interchange + assessment fees
- Minimum monthly fees typical
- Volume discounts available
- No transaction minimums usually

Notable Differences:
- Premium positions (concierge, travel)
- Affluent cardholder base
- Higher average transaction value
- Lower fraud rates
- Longer settlement periods (2-3 days)
```

## Discover Card Scheme

### Discover Products

```
Consumer Cards:
- Discover It: Cash back rewards
- Discover It Student: College student card
- Discover It Business: Small business card
- Discover Secured: For credit building

Specialty:
- Discover Home Loans: Mortgage products
- Discover Personal Loans: Installment loans
- Discover Money Market: Banking products
```

### Discover Technical Details

```
Three-Party Model (like Amex):
- Discover (Issuer and acquirer)
- Cardholder
- Merchant

Network:
- GlobalNet network
- Interoperability with Mastercard (2009 agreement)
- Growing acceptance globally

Chip and Contactless:
- EMV chip support
- Contactless (NFC) support
- 3D Secure authentication

Competitive Advantages:
- No foreign transaction fees
- Strong cash back rewards
- Lower fraud rates
- Excellent customer service
- Accepted globally via Mastercard network
```

### Discover Pricing

```
Discount Rates:
- Similar to Amex (3-party model)
- Typically 1.5%-2.5% (lower than Amex)
- Card Present: 1.5%-1.8%
- Card Not Present: 1.7%-2.0%
- International: 1.8%-2.0% (competitive advantage)

Market Share:
- ~1% globally
- ~7% in North America (US/Canada)
- Growing in US market
- Popular for cash back seekers
```

## JCB (Japan Credit Bureau)

### JCB Overview

```
Origin: Japan
Coverage: 130+ countries
Card Holders: ~50 million
Transaction Volume: ~1 billion transactions/month
Focus: Asian market, particularly Japan

Markets:
- Japan: Dominant (most Japanese cards are JCB)
- Asia-Pacific: Growing adoption
- Global: Limited vs. Visa/Mastercard
- USA: Specialty acceptance
```

### JCB Products

```
Consumer Cards:
- JCB Standard
- JCB Gold
- JCB Platinum
- JCB PREMIUM

Business Cards:
- JCB Corporate
- JCB Gold Business
- JCB Platinum Business
```

### JCB Technical Standards

```
Chip Support: Full EMV compliance
Contactless: Yes, standard adoption
3D Secure: JCB SecureCode
Tokenization: JCB Token Service

Interchange:
- Japan Domestic: ~1.5%
- International: ~2.5%
- Premium cards: +0.5-1%
```

## UnionPay (China)

### UnionPay Overview

```
Origin: China
Coverage: 180+ countries
Card Holders: ~9 billion cards issued
Focus: Chinese market and expansion

Characteristics:
- State-owned (majority by PBOC)
- Mandatory for Chinese card issuance
- Rapid international expansion
- Strong in Asia-Pacific
- Growing in Europe and Americas
```

### UnionPay Products

```
Consumer Cards:
- UnionPay Standard
- UnionPay Gold
- UnionPay Platinum
- UnionPay Elite

Debit and Prepaid:
- UnionPay Debit
- UnionPay Prepaid
- Digital wallets (ApplePay, GooglePay, etc.)
```

### UnionPay Technical Standards

```
Chip Support: Full EMV compliance
Contactless: Extensive mobile support
Mobile Wallets: Primary in China
Interchange:
- China Domestic: ~0.6-0.8%
- International: ~2.0-2.5%
- Premium cards: +0.5%
```

## Mir (Russia)

### Mir Card System

```
Origin: Russia
Focus: Domestic Russian market
Launch: 2014
Background: Response to SWIFT sanctions

Characteristics:
- Russian government backed
- Mandatory for Russian citizen cards (2021+)
- Limited international acceptance
- Processing in Russia
- Russian data residency
```

### Mir Card Features

```
Products:
- Mir Classic
- Mir Gold
- Mir Platinum
- Mir Ultimate (premium)

Technical:
- EMV chip support
- Contactless/NFC
- 3D Secure
- Tokenization

Acceptance:
- ~95% in Russia
- Growing in Belarus, Kazakhstan
- Limited global acceptance
- ~200 million cards in circulation
```

## Emerging Card Schemes

### RuPay (India)

```
Operator: National Payments Corporation of India (NPCI)
Domestic Focus: India
Cards Issued: ~300 million
Features:
- EMV chip and PIN
- Domestic processing
- Lower interchange rates than Visa/Mastercard
- Growing international acceptance

Interchange:
- Debit: 0.40%-0.60%
- Credit: 0.75%-1.00%
- Strategic: Push domestic payments
```

### EFTPOS (Australia/NZ)

```
Operator: EFTPOS networks (multiple operators)
Focus: Australia and New Zealand
Usage: Primarily debit card processing
Features:
- PIN-based transactions
- High volume, low value
- Local processing
- Competition from Visa/Mastercard

Market:
- Declining as Visa/Mastercard expand
- Still significant in NZ
- Regulatory pressure for interoperability
```

## Scheme Comparison

### Market Dominance

```
Global Transaction Volume Distribution:
- Visa: 54%
- Mastercard: 24%
- Amex: 6%
- UnionPay: 8%
- Others (JCB, RuPay, Discover, Mir): 8%

Geographic Variations:

USA:
- Visa: 50%
- Mastercard: 25%
- Amex: 20%
- Discover: 5%

Europe:
- Visa: 45%
- Mastercard: 42%
- Amex: 5%
- Local schemes: 8%

Asia-Pacific:
- Visa: 25%
- Mastercard: 20%
- UnionPay: 30%
- JCB: 5%
- Local schemes: 20%
```

### Interchange Rate Comparison

```
Entry-Level Card (same tier):
- Visa: 1.51% + $0.95
- Mastercard: 1.51% + $0.95
- Amex: 2.75%-3.25%
- Discover: 1.55% + $0.95
- JCB: ~2.0% (varies)
- UnionPay: 2.0% (international)

Premium Card (same tier):
- Visa: 2.51% + $0.95
- Mastercard: 2.50% + $0.95
- Amex: 3.5%-4.0%
- Discover: 2.0% + $0.95
- JCB: ~2.5%
- UnionPay: 2.5%+

Visa/Mastercard: Highly competitive, similar rates
Amex: Premium (1-1.5% higher), all-in rate
Discover: Competitive, trying to gain share
Others: Regional variations, growing but limited
```

### Fraud and Security Comparison

```
Fraud Rate (approximate):
- Amex: 0.02% (lowest - known customers)
- Discover: 0.03%
- Visa: 0.05%
- Mastercard: 0.06%
- UnionPay: 0.08%
- JCB: 0.06%
- Mir: 0.10% (less mature)

Security Features Available:
- Amex: Strong (direct customer knowledge)
- Visa: Good (VTS tokenization, real-time tools)
- Mastercard: Good (MDES, ML-based)
- Discover: Good (similar to Amex)
- JCB: Good (Token Service, SecureCode)
- UnionPay: Good (improving infrastructure)
- Mir: Developing (newer system)

3D Secure Adoption:
- Visa Secure: ~90% coverage
- Mastercard Identity Check: ~88%
- Amex: ~85% (Amex Identity Check)
- Others: 60-80% (regional variation)
```

### Settlement and Timeline

```
Visa/Mastercard:
- T+1 to T+2 typical
- Settlement to merchant: T+1 to T+3 via acquiring bank
- Consistent across regions

Amex/Discover:
- T+1 to T+2 typical
- Often same next day via direct relationship

JCB:
- Japan: T+0 to T+1 (next business day)
- International: T+2 to T+3

UnionPay:
- China: T+0 to T+1
- International: T+1 to T+2

Mir:
- Russia: T+0 to T+1
- International: T+1 to T+2 (limited)
```

## Scheme Rules and Restrictions

### Visa Rules

```
Acceptance:
- No discrimination (must accept all Visa products)
- No surcharge allowed in most countries
- No minimum transaction (in most countries)

Tokenization:
- Visa Token Service (VTS) mandated for e-commerce
- Fallback to card number if token unavailable
- Automatic reissuance on card changes

Transaction Types:
- Authorization via Visa network required
- Clearing and settlement rules defined
- Return/reversal procedures specified

Chargebacks:
- 120-day window (varies by code)
- Chargeback reason codes defined
- Arbitration process for disputes
- Fees for merchants: $15-100 per chargeback
```

### Mastercard Rules

```
Acceptance:
- Zero surcharge rule (enforced)
- No discrimination between Mastercard products
- No minimum transaction amounts

Tokenization:
- MDES (Digital Enablement Service)
- Network token adoption encouraged
- Cryptogram validation for security

Transaction Processing:
- Network rules for authorization
- Clearing rules and timelines
- Settlement procedures defined

Chargeback Management:
- 120-day window from transaction
- Specific reason codes
- Merchant liability model
- Chargeback fees: $15-100+
```

### Amex Rules

```
Acceptance:
- Higher merchant discount rate
- Separate agreements per merchant
- Potential surcharge allowance (varies by country)

Settlement:
- Direct to Amex (not via acquiring bank)
- T+1 or T+2 typical
- Less intermediaries involved

Chargeback:
- Claims ratio important metric
- High ratio triggers fees and restrictions
- Target: <0.5% claims
- Fee: Significant (up to 1% of volume)

Controls:
- Amex monitors merchants closely
- Suspension possible for high fraud/chargebacks
- Stronger risk management than Visa/MC
```

## Scheme Selection

### Factors for Merchants

```
1. Customer Base
   - Visa/Mastercard: Global acceptance needed
   - Amex: Premium customers
   - UnionPay: Chinese/Asian customers
   - Discover: US market

2. Volume and Value
   - High volume: Visa/Mastercard (better rates)
   - Premium/High value: Amex (better security)
   - Mixed: Multiple schemes

3. International
   - Global: Visa/Mastercard mandatory
   - Specific regions: Local schemes
   - Multiple: Accept all major schemes

4. Cost Optimization
   - Routing to lowest-cost scheme
   - Dual-messaging capabilities
   - Scheme selection logic in gateway

5. Compliance
   - PCI-DSS: All schemes require it
   - Regional: Some schemes mandate local processing
   - Data residency: Mir requires Russian processing
```
