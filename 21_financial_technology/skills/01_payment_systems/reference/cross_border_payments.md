# Cross-Border Payments Reference

## Overview

Cross-border payments involve transferring funds across international boundaries with different currencies, regulatory regimes, and banking systems. They represent ~$130 trillion annually and are critical for global commerce.

## International Payment Methods

### SWIFT (Society for Worldwide Interbank Financial Telecommunication)

```
Network:
- 11,000+ institutions in 200+ countries
- Messaging backbone for international payments
- Established 1973, proven reliability

Message Format:
- Standardized SWIFT messaging
- MT103 for customer transfers
- MT202 for bank-to-bank

Processing:
- Overnight batch processing (typically)
- 1-3 business days
- Correspondent banking model

Cost:
- Bank fees: $15-50 outgoing
- Correspondent fees: $10-30
- Receiving bank fees: $10-25
- Total: $35-105 per wire
- Effective cost: 0.5-2% of transfer

Exchange Rate:
- Banks add 2-5% markup
- Only banks can see true rate
- No transparency
```

### Correspondent Banking

```
Definition:
- Bank A (sender's bank) doesn't have direct relationship with Bank C (receiver's bank)
- Bank A uses Bank B (correspondent) to route transaction
- Bank B has relationship with Bank C

Flow:
Customer Bank A -> Bank A's Account at Bank B -> Bank B -> Bank C -> Receiver

Advantages:
- Enables global reach
- Leverages established relationships
- Familiar process

Disadvantages:
- Multiple intermediaries
- Higher costs
- Longer processing time
- Less transparency
- Potential delays and errors

Example:
US Customer with Chase wants to send to India recipient with HDFC
Chase (no direct HDFC relationship)
  -> Citibank (correspondent bank in India)
  -> HDFC Bank

Fees:
- Chase: $30
- Citibank (correspondent): $15
- HDFC: $10
- Receiver gets 85-90% of original amount
```

### Real-Time Gross Settlement (RTGS) Systems

```
Characteristics:
- Immediate settlement (real-time)
- High-value transactions
- Final and irrevocable
- 24/7 availability (some systems)

Systems by Country:

USA - FedWire:
- Federal Reserve
- Settlement: Real-time
- Availability: 9 AM - 4:30 PM EST (weekdays)
- Cost: $15-30

USA - RTP (The Clearing House):
- Same-day and real-time
- 24/7 availability (new)
- Maximum: $1 million per transaction
- Growing adoption

Eurozone - TARGET2:
- ECB (European Central Bank)
- Real-time settlement
- 24/7 availability
- All SEPA countries

UK - CHAPS:
- Bank of England
- Real-time settlement
- High-value transactions
- 24/7 availability
- Maximum: Unlimited

Japan - BOJ-NET:
- Bank of Japan
- Real-time settlement
- 8:30 AM - 3:30 PM JST
- High-value transactions

Singapore - RTGS:
- Monetary Authority of Singapore
- Real-time settlement
- 24/7 availability
- Regional hub for Southeast Asia

Hong Kong - RTGS:
- Hong Kong Monetary Authority
- Real-time settlement
- 24/7 availability
- Regional hub for Asia
```

### SEPA (Single Euro Payments Area)

```
Coverage:
- EU + EEA countries
- Switzerland, UK (post-Brexit)
- ~30 countries

Transaction Types:

SEPA Credit Transfer:
- Domestic and intra-SEPA
- 1 business day settlement
- Low cost
- Used for business payments, payroll

SEPA Direct Debit:
- Recurring payments
- Bill payments
- 1 business day settlement
- Requires mandate

SEPA Instant Credit Transfer:
- Real-time settlement (10 seconds or less)
- Available 24/7/365
- Max €100,000
- Premium fees (1-3% typical)
- Growing adoption

Cost:
- Credit transfer: €0.50-5.00
- Direct debit: €0.01-1.00
- Instant transfer: €0.50-2.00 premium

Standards:
- ISO 20022 standard
- XML format
- Highly standardized
- Simple structure
```

### ACH International (IAT)

```
Definition:
- ACH for cross-border payments
- Used for Canada, Mexico, other partners
- More complex than domestic ACH
- 3-5 business day processing

Characteristics:
- Limited country coverage
- Higher fees than domestic ACH
- More detailed information required
- Different rule set

Supported Corridors:
- USA <-> Canada
- USA <-> Mexico
- Limited other countries

Cost:
- Typically $5-15 per transaction
- Some banks bundle with ACH

Requirements:
- Extensive beneficiary information
- Originating company details
- More detailed record format
- AML/KYC validation

Uses:
- Payroll to Canadian/Mexican employees
- Vendor payments to North America
- Government benefits

Not suitable for:
- Most international payments
- Long settlement times
- Limited corridors
```

## Exchange Rates and Currency Conversion

### Mid-Market Rate

```
Definition:
- True interbank exchange rate
- No markup
- Real market rate
- Used for reference only

Example:
EUR/USD: 1.10000 (true mid-market rate)

Factors Affecting Mid-Market:
- Supply and demand
- Central bank actions
- Economic data
- Geopolitical events
- Time of day (London center hours highest volume)
```

### Bank Markup

```
Typical Markup:
- Traditional banks: 2-4%
- Online transfer services: 1-2%
- Cryptocurrency exchanges: 0.5-1.5%
- Specialist providers: 0.5-1%

Example:
True Rate (Mid-Market): EUR/USD = 1.10000
Bank's Offered Rate: EUR/USD = 1.08500

For €10,000 transfer:
Expected (at mid-market): $11,000.00
Bank provides: $10,850.00
Hidden markup: $150.00 (1.4% margin)

Annual Impact:
- If 100 transfers/year at €10,000 each
- Markup cost: €15,000 annually
- Could be $15,000-30,000 depending on currency pair
```

### Forward Contracts and Rate Locks

```
Forward Contract:
- Lock exchange rate for future transfer
- Protection against currency fluctuation
- Cost: Typically $100-500 or percentage-based
- Commitment: Must execute at locked rate

Example:
Date: January 15, 2024
Want to pay: €50,000 in 30 days (by February 15)
Current spot rate: EUR/USD = 1.10000
Forward rate offered: EUR/USD = 1.09000

Option A (Don't lock):
If rate stays 1.10: Pay $55,000 (good)
If rate goes to 1.11: Pay $55,500 (worse, but get market benefit)
If rate drops to 1.08: Pay $54,000 (good, but locked would be better)

Option B (Lock at 1.09):
Guaranteed cost: $54,500
If rate rises to 1.11: You're protected (would have paid $55,500)
If rate drops to 1.08: You're locked in (would have saved $1,000)

Use Forward When:
- High certainty of amount and timing
- Need budget certainty
- Currency expected to strengthen

Don't Use When:
- Payment timing uncertain
- Amount may change
- Currency expected to weaken
```

## Regulatory and Compliance

### FATCA (Foreign Account Tax Compliance Act)

```
US Requirement:
- US citizens disclose foreign accounts
- Financial institutions report US account holders
- Global financial institutions affected
- IGA (Intergovernmental Agreement) framework

Requirements:
- KYC on foreign account holders
- W-9 or W-8BEN tax form
- Annual reporting to IRS
- Account screening and monitoring

Financial Institution Requirements:
- Identify US persons
- Report to US authorities
- Annual FATCA reporting
- Compliance documentation

Impact on Transfers:
- US persons' transfers flagged
- Additional documentation needed
- Slower processing
- Potential withholding (30% for non-compliance)
```

### CRS (Common Reporting Standard)

```
Global Standard:
- Similar to FATCA but global
- 100+ countries participating
- Automatic exchange of financial information
- Tax transparency initiative

Requirements:
- Identify tax residency
- Report accounts to relevant countries
- Annual reporting
- Due diligence procedures

Implementation:
- Financial institutions report to local tax authority
- Local authority exchanges with other countries
- Based on tax residency, not citizenship
- Account value thresholds apply

Impact on Cross-Border:
- More complex KYC requirements
- Documentation of tax residency
- Potential holds on transfers
- Reporting delays
```

### Sanctions Screening (OFAC)

```
Office of Foreign Assets Control (OFAC):
- US Treasury department
- Maintains sanctions lists
- Blocks transactions to/from sanctioned entities
- Penalties: $100,000-20 million

Lists:
- SDN (Specially Designated Nationals)
- HMO (Hierarchy of Persons)
- Sectoral Sanctions Identifications (SSI)
- Non-SDN Foreign Sanctions Evaders

Required Screening:
- All parties (payer, payee, intermediaries)
- Payment instructions
- Beneficial owners
- Real-time before transaction

Technology:
- AML/KYC software (Sanctions screening)
- False positive management
- Regular list updates
- Documentation of screening

Example:
Payment from US Bank to Russian Bank
- Check sender against SDN list
- Check receiver against SDN list
- Check beneficiary against SDN list
- If any match: Block transaction, file OFAC report
- If no match: Proceed with caution on other Russian transactions
```

### Wire Fraud Prevention

```
Regulatory Requirements:

Originator Information:
- Name of payer
- Account number
- Address
- Identification details

Beneficiary Information:
- Full name (first and last)
- Account number
- Bank identifier code (SWIFT BIC)
- Address
- Country

Intermediaries:
- All correspondent banks identified
- Routing information
- Account at correspondent

Standard:
- ISO 20022 implementation
- Structured Data Field (SDF) requirements
- Complete chain of information

Compliance:
- Verify information accuracy
- Screen against sanctions lists
- Document due diligence
- Keep records 7+ years
- Report suspicious activity
```

## Emerging Payment Systems

### Ripple (XRP Ledger)

```
Technology:
- Blockchain-based cross-border payments
- Settlement in seconds
- Real-time transactions
- Uses XRP cryptocurrency or IOU tokens

Partnerships:
- 200+ financial institutions
- Banks testing RippleNet
- Growing adoption in Asia/Europe

Use Cases:
- Real-time international payments
- Remittances
- Bank-to-bank transfers
- Settlement of trade finance

Advantages:
- Fast settlement (3-5 seconds)
- Lower cost than SWIFT
- Transparency
- Final settlement

Disadvantages:
- Cryptocurrency volatility
- Regulatory uncertainty
- Limited merchant adoption
- Dependence on network liquidity

Cost:
- Network fees: $0.00001 per transaction
- Minimal compared to SWIFT
```

### CBDCs (Central Bank Digital Currencies)

```
Definition:
- Digital version of fiat currency
- Issued by central banks
- Blockchain or distributed ledger based
- Programmable money

Potential Impact:
- Direct central bank to citizen transfers
- Eliminate intermediaries
- Faster settlement (real-time)
- Lower costs

Countries/Projects:
- China: Digital Yuan (pilot)
- EU: Digital Euro (development)
- Sweden: e-Krona (pilot)
- Canada: Project Jasper (exploration)
- Singapore: Project Ubin (exploration)

Timeline:
- Retail CBDCs: 2025-2030 estimated
- Wholesale CBDCs: Earlier (2024-2026)
- Full implementation: 2030+

Cross-Border Use:
- Direct currency transfer
- No intermediaries needed
- Real-time settlement
- Programmable conditions
```

### Stablecoins

```
Definition:
- Cryptocurrency pegged to stable asset
- Usually fiat currency or commodity
- Minimal volatility
- Increasingly used for payments

Types:

Fiat-Backed (most popular):
- USDC (Circle, Coinbase)
- USDT (Tether)
- BUSD (Binance)
- Pegged 1:1 to USD

Commodity-Backed:
- PAX Gold (PAXG)
- DXN (Digital Currency Group)
- Pegged to physical commodity

Algorithmic:
- DAI (MakerDAO)
- Algorithmic stabilization
- Less popular, more complex

Cross-Border Use:
- Fast settlement (blockchain)
- Low cost (no intermediaries)
- 24/7 availability
- Global access
- Programmable payments

Advantages:
- Speed (minutes vs. days)
- Cost (minimal vs. $35-100)
- Transparency
- No banking hours limitations

Disadvantages:
- Regulatory uncertainty
- Volatility risk (small)
- Adoption limitations
- Custody concerns
- AML/KYC challenges
```

## Cost Comparison

### Traditional Wire vs. Modern Alternatives

```
Scenario: US $10,000 to Germany

Traditional Wire (SWIFT):
- Originating bank fee: $30
- Correspondent bank (if needed): $15
- Receiving bank fee: $10
- Total fees: $55
- Exchange rate markup: 2% on $10,000 = $200
- Total cost: $255 (2.55%)
- Time: 1-3 business days
- Effective annual cost: $13,260 for weekly transfer

Online Transfer Service:
- Platform fee: $10
- Exchange rate markup: 0.5% on $10,000 = $50
- Total cost: $60 (0.60%)
- Time: 1-2 business days
- Effective annual cost: $3,120 for weekly transfer

Stablecoin (Blockchain):
- Network fee: $2
- Conversion fee: 0.1%
- Total cost: $12 (0.12%)
- Time: 5-30 minutes
- Effective annual cost: $624 for weekly transfer

Annual Savings:
- Wire vs. Online: $10,140
- Wire vs. Stablecoin: $12,636
- Online vs. Stablecoin: $2,496
```

### Use Case Selection

```
Small Remittances ($50-500):
- Online transfer service (better for small)
- Stablecoin if both parties have crypto
- NOT traditional wire (excessive fees)

Regular Business Payments ($1,000-50,000):
- Online transfer services
- Bank transfers if bulk volume
- Stablecoin if counterparty accepts

Large Transactions ($50,000+):
- Bank wire (volume discounts apply)
- Stablecoin with custody
- Trade finance alternatives (LC, collection)

Urgent Payments:
- Stablecoin (fastest)
- Correspondent banking (if available)
- Real-time systems (RTP, SEPA Instant)

Recurring/Bulk Payments:
- ACH International (North America)
- SEPA (Europe)
- Online bulk transfer services
```

## Implementation Considerations

### Compliance Checklist

```
Before Sending:
- [ ] Verify beneficiary information (name, account, bank)
- [ ] Screen against sanctions lists (OFAC, EU, UN)
- [ ] Verify beneficial ownership
- [ ] Document purpose of payment
- [ ] Obtain tax forms (W-9, W-8BEN, etc.)
- [ ] Confirm currency and exchange rate
- [ ] Identify all intermediary institutions
- [ ] Retain compliance documentation

During Transfer:
- [ ] Monitor transaction progress
- [ ] Verify receipt confirmation
- [ ] Document final settlement
- [ ] Record all fees and charges
- [ ] Update accounting records

After Transfer:
- [ ] Reconcile with beneficiary
- [ ] Investigate delays if any
- [ ] Document final proof of funds
- [ ] Retain records for 7+ years
- [ ] Monitor for fraud indicators
```

### Currency Risk Management

```
Strategy 1: Hedge with Forwards
- Lock exchange rate
- Eliminates currency risk
- Cost: Percentage of amount
- Best for: Certain future payments

Strategy 2: Natural Hedging
- Match revenues and payments in same currency
- Buy in same currency you sell
- Cost: Opportunity cost
- Best for: Ongoing business

Strategy 3: Money Market Hedge
- Borrow in foreign currency
- Convert at spot rate
- Lend proceeds
- Cost: Interest differential
- Best for: One-time large payment

Strategy 4: Accept Currency Risk
- Don't hedge
- Gamble on favorable moves
- Cost: Potential losses
- Best for: Small amounts, short periods

Strategy 5: Partial Hedge
- Hedge percentage of exposure
- Balance risk/cost
- Cost: Partial hedge costs
- Best for: Large ongoing transactions
```
