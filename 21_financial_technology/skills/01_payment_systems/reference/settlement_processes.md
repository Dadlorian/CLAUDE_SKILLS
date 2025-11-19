# Settlement Processes Reference

## Overview

Settlement is the final step in payment processing where funds are transferred from the card issuer's bank to the acquiring bank and ultimately to the merchant. It involves complex orchestration across multiple financial institutions and involves clearing houses, correspondent banks, and payment networks.

## Settlement Timeline and Process

### Standard Settlement Flow (T+1 to T+3)

```
Transaction Day (T+0):
------
9:00 AM: Customer makes purchase
9:15 AM: Transaction authorized
9:30 AM: Cardholder receives goods/services
9:45 AM: Transaction captured (ready for settlement)

T+0 Evening:
6:00 PM: Merchant submits transactions to processor
6:30 PM: Processor batches transactions
7:00 PM: Batch sent to clearing house

Clearing House Processing (Overnight):
11:00 PM: Clearing house receives batch
11:30 PM: Transaction sorting by network/bank
12:00 AM: Debit/credit matching
12:30 AM: Reconciliation
1:00 AM: Settlement instructions prepared

T+1 Day (Settlement Day):
9:30 AM: Network initiates settlement
- Card network (Visa/Mastercard) calculates amounts
- Debit amounts from issuing banks
- Credit amounts to acquiring banks
- Settlement through Federal Reserve (Fedwire) or TCH

10:00 AM: Acquiring bank receives settlement
- Funds credited to merchant's account at acquiring bank
- Merchant does NOT yet have access (reserve held)

11:00 AM: Acquiring bank posts to merchant account
- Merchant can access funds (usually)
- Statement shows deposit
- Fees deducted

T+2 Day:
Morning: Funds typically available to merchant
- Some acquirers: T+1 (next business day)
- Most: T+2 (2 business days)
- Some: T+3 or longer

Complete Timeline Example:
Monday 2:00 PM: Customer purchases
Tuesday 9:30 AM: Settlement at network
Tuesday 11:00 AM: Acquiring bank receives
Tuesday 2:00 PM: Merchant receives (if next-day settlement)
OR Wednesday/Thursday: Merchant receives (standard)

Typical: $100,000 in transactions
Monday: $100,000 in sales
Wednesday: $98,000 in account (minus $2,000 in fees)
Thursday: Access to funds
```

### Accelerated Settlement

```
Same-Day Settlement:
- Available for select merchants
- Higher fees: +0.25-0.50% per transaction
- Requires early cutoff: 2:00 PM EST
- Available from select processors
- Cost: $25-100 per settlement

Next-Day Settlement:
- Standard for mid-tier merchants
- Most merchants default
- 1 business day from settlement
- No additional fees (usually)

Standard Settlement (T+2):
- Available for all merchants
- Lower fees/requirements
- 2 business days
- Default for new merchants
- Standard pricing

Reserve Holds:
- Percentage of transactions held (1-10%)
- Rolling reserve: Released monthly
- Fixed reserve: Amount held indefinitely
- Protects against chargebacks
- Example: 5% rolling reserve on $100k
  - Wednesday: $5,000 held
  - Thursday: Previous day's $5,000 released
  - Friday: New day's $5,000 held
  - Typically 30-day rolling cycle
```

## Payment Network Clearing and Settlement

### Visa Settlement Process

```
1. Authorization Phase (Same-day)
- Transaction authorized
- Visa network approves
- Issuing bank confirms funds

2. Clearing Phase (Within 24 hours)
- Merchant submits transaction to processor
- Processor batches transactions
- Cleared by Visa network
- Transactions sorted by issuer/acquirer

3. Settlement Phase (T+1 to T+3)
- Visa initiates settlement
- Calculates net amounts
- Debit amounts from issuing banks
- Credit amounts to acquiring banks
- Settlement through Fedwire

Clearing Process:
Merchant (100 Visa transactions)
    |
Processor batches
    |
Visa Clearing
    |
Sorts by: Issuer + Acquirer combination
    |
Net settlement calculation
    |
Example:
- Card A issued by Chase, acquired by Stripe
- 20 transactions, total: $5,000
- Merchant: 20, Issuer: 1
- Settlement: Stripe's account gets $5,000 credit from Chase

4. Funding (T+1 to T+3)
- Acquiring bank credits merchant account
- Or: Processor credits merchant
- Fees deducted
- Statement generated
```

### Mastercard Settlement Process

```
Similar to Visa with variations:

1. Authorization
- Mastercard network
- Faster than Visa historically (improving)

2. Clearing
- Mastercard scheme rules
- Batch creation
- Network routing

3. Settlement
- Mastercard initiates
- Slightly longer timeline (T+2 typical vs. T+1 for Visa)
- Correspondent banking for international
- SWIFT for cross-border

4. Funding
- Acquiring bank credits merchant
- Timeline: T+2 to T+4 (standard)
- T+1 available (premium)
```

### American Express Settlement

```
Different Model (3-party):
- Amex is both issuer and acquirer
- Direct relationship with cardholders
- Direct relationship with merchants
- Simpler settlement (no intermediaries)

Settlement Timeline:
1. Same-day: Transaction authorized
2. Batch: Amex batches transactions
3. Settlement: Next day or T+2
4. Funding: Amex debits merchant account directly
5. Cardholder charged by Amex

Advantages:
- Faster settlement (often next-day)
- Direct communication
- Higher discount rates (charge)
- Better data access

Disadvantages:
- Higher fees (2.5-4% vs. 1.5-2.5% for others)
- Limited acquirer options (direct only)
- Merchant account limited to Amex
```

## Correspondent Banking and International Settlement

### Correspondent Bank Chain

```
Flow:
Merchant's Bank (USA)
    |
Correspondent Bank (USA)
    |
Intermediate Bank (if needed)
    |
Receiving Bank (Foreign Country)
    |
Customer's Account

Example: US to Germany:
1. US Merchant Bank: JPMorgan Chase
2. US Correspondent: Citibank (has relationship in Germany)
3. German Bank: Deutsche Bank
4. Final: Customer's Bank in Germany

Each bank charges:
- JPMorgan: $30 (originating bank)
- Citibank: $15 (correspondent)
- Deutsche Bank: $10 (receiving bank)
- Total: $55 + exchange rate markup (2%)

Timeline:
- US: 1 day processing
- Correspondent: 1 day processing
- Receiving bank: 1 day posting
- Total: 2-3 business days (typical)
- Can extend to 4-5 days with multiple intermediaries

Correspondent Account:
- Banks maintain accounts with each other
- Pre-positioned funds
- Nostro account (our account at their bank)
- Vostro account (their account at our bank)
- Allows fast settlement
```

### Real-Time Settlement (for Real-Time Payments)

```
FedNow and RTP:
- Real-time gross settlement (RTGS)
- No intermediary clearing
- Direct bank-to-bank
- Settlement: Within seconds

FedNow:
- Federal Reserve operates
- 24/7 availability
- Real-time delivery
- Irrevocable settlement

Process:
1. Sender initiates RTP message
2. RTP network routes to receiver's bank
3. Receiver's bank credits account
4. Immediate confirmation
5. Funds available instantly

Timeline:
- Total: < 10 seconds
- Confirmation: Simultaneous
- Availability: Immediate
- No reserve holds typically

Cost:
- Usually free or very low ($0-2)
- Network-based (not processor)
- Growing adoption
```

## Funds Flow and Cash Position Management

### Working Capital Optimization

```
Traditional Model:
Day 1: Customer pays merchant (Stripe account)
  - Stripe holds funds
  - Reserves for fraud/chargebacks
  - Acquiring bank holds reserve

Day 2: Settlement (T+1)
  - Funds move from Visa/Mastercard
  - Acquiring bank credits Stripe
  - Stripe deducts fees

Day 3: Merchant receives (T+2 or T+3)
  - Stripe credits merchant
  - Merchant has access
  - 2-3 day float

Working Capital Impact:
$100,000 daily volume
- 2-day float: $200,000 in-flight
- At 2% cost of capital: $4,000/month cost
- Annual impact: $48,000

Optimization Strategies:
1. Next-Day Settlement
   - Reduce float by 1 day
   - Cost: Usually $0 (no additional fee)
   - Savings: $2,000/month

2. Pay with Deposits
   - Use credit from processor
   - Advance settlements
   - Cost: 0.5-1% fee
   - Can worth it for cash-hungry businesses

3. Factoring Services
   - 3rd party buys future settlements
   - Immediate funding
   - Cost: 2-5% of settlement
   - Good for growth/expansion
```

### Reserve Management

```
Why Reserves Exist:
- Chargeback protection
- Fraud protection
- Operational risk mitigation
- Regulatory requirement

Types of Reserves:

Rolling Reserve:
- Percentage of transactions (3-10%)
- Held for rolling period (typically 30 days)
- Example:
  - Day 1: Process $100,000, hold $10,000 (10% reserve)
  - Day 2: Release previous day's hold ($10,000), hold new day
  - Rolling: Always have 10% outstanding
  - Released: Monthly as cycle completes

Fixed Reserve:
- Flat amount held indefinitely
- Percentage of monthly volume
- Example: $25,000 fixed + 5% rolling
- Collateral for processor
- Reduces processor risk
- Released only with notice

Reserve Release:
- After holding period (30, 60, 90 days)
- Subject to no chargebacks/fraud
- Conditions in agreement
- Can be extended if issues detected

Example Calculation:
Monthly Volume: $500,000

Option A: 5% Rolling Reserve
- Amount held: $25,000 (5% of $500k)
- Duration: 30 days rolling
- Working capital impact: $25,000 (constant)
- Month 1: Hold days 1-30
- Month 2: Hold days 31-60 (release days 1-30)
- Effective: $25,000 out for 30 days, then cycles

Option B: 3% Rolling + $50,000 Fixed
- Amount held: $15,000 rolling + $50,000 fixed
- Duration: 30 days rolling, indefinite fixed
- Working capital impact: $65,000
- Fixed never released
- Rolling released monthly

Preference:
- Avoid fixed reserves if possible
- Negotiate lower rolling percentages
- Higher-risk merchants: Higher reserves
- Long-term: Build trust, reduce reserves
```

## Settlement Exceptions and Issues

### Reconciliation Issues

```
Issue 1: Settlement Amount Mismatch
Submitted: $10,000 (100 transactions)
Settled: $9,950 (98 transactions)
Missing: $200 (2 transactions)

Causes:
- Transactions declined by network
- Duplicate detection (merged)
- Customer return/refund processed
- Processor error

Resolution:
- Review decline report
- Identify specific transactions
- Confirm with customer if refund
- Follow up with processor if error
- Update GL records

Issue 2: Late Settlement
Expected: T+1 (Tuesday)
Actual: T+3 (Thursday)
Delay: 2 days

Causes:
- Network processing delays
- Clearing house backlog
- Holiday impact
- Fraud holds
- High-risk merchant

Resolution:
- Check processor statement
- Contact acquiring bank
- Verify no fraud holds
- Review merchant account status
- Escalate if excessive delays

Issue 3: Partial Settlement Hold
Submitted: $10,000
Settled: $10,000
Held: $2,000 (20%)

Cause:
- Reserve hold (normal)
- Fraud indicator triggered
- Chargeback alert
- Risk management decision

Resolution:
- Review hold reason
- If fraud: Provide evidence
- If chargeback: Defend transaction
- Follow reserve release policy
- Escalate if unreasonable
```

### Chargeback Impact on Settlement

```
Settlement with Chargebacks:

Timeline:
T+0: Transaction authorized and captured
T+1: Settled (funds transferred)
T+30-120: Chargeback filed
T+120-180: Chargeback adjudicated

Financial Impact:
Transaction settlement:
  Dr. Bank Account    $100
    Cr. Merchant Payable  $100

Chargeback (within 120 days):
  Dr. Chargeback Liability $100
    Cr. Bank Account       $100
  (Debit from merchant account)

Effective flow:
- Merchant gets funds
- If no chargeback: Keeps funds
- If chargeback: Funds reversed
- Plus chargeback fee ($25-100)

Risk Management:
- Chargebacks unpredictable
- Can occur weeks/months later
- Must account in financial planning
- Reserve system protects processor
- Merchant absorbs ultimate loss
```

## Settlement Finality and Irrevocability

### When Settlement is Final

```
Card Transactions:
- Network settlement is final (T+1 or T+2)
- Once settled at network level, irreversible
- Chargeback possible but different process
- Returns only through refund (new transaction)
- No reversal by processor

Bank Transfers:
- ACH: Settlement T+1, final at network
- Wire: Real-time settlement, immediate final
- SWIFT: T+1-3, final at receiving bank

Key Point:
- Finality at network level
- Not reversible by processor
- Merchant refunds via manual reversal
- Chargebacks are disputes, not reversals

Irreversibility Protections:
- Merchant can't change mind
- Processor can't claw back funds
- Provides certainty
- Risk-based decision-making
```

### Regulatory Requirements

```
Payment Card Industry (PCI):
- Settlement finality required
- No secondary settlement reversals
- Audit trail of all settlements

ACH:
- Returns window: 5 business days
- Chargebacks: 120 days
- NACHA rules on settlement

Wire Transfers:
- Irrevocable once sent (in most cases)
- No reversal mechanism
- Legal requirement

International:
- SWIFT settlement finality
- Regulations vary by country
- T/C2 (trade confirmation + settlement)

Compliance Documentation:
- Settlement procedures documented
- Approval required
- Audit trail maintained
- Regulatory review annually
```

## Future of Settlement

### Instant Settlement

```
Emerging Capabilities:
- Real-time payment networks (FedNow, RTP, SEPA Instant)
- Blockchain/DLT-based settlement
- Central bank digital currencies (CBDCs)

FedNow Impact:
- Settlement in seconds, not days
- Eliminates working capital float
- Reduces fraud risk window
- Real-time liquidity

CBDC Settlement:
- Central bank digital money
- Programmable payments
- Conditional settlement
- Cross-border settlement (multi-CBDC)

Timeline:
- Current: 1-3 days
- 2024-2026: Some real-time options
- 2026-2030: Majority real-time
- 2030+: Fully real-time globally

Impact on Business:
- No working capital float
- Improved cash flow
- Reduced fraud exposure
- Simpler reconciliation
- Lower cost of capital
```

### Blockchain Settlement

```
Distributed Ledger Technology (DLT):
- Settlement on blockchain
- Real-time, 24/7
- Immutable record
- Smart contracts for conditions

Examples:
- Ripple: XRP Ledger for settlement
- Hyperledger: Enterprise blockchain
- Ethereum: DeFi settlements
- Central Bank networks: Multi-CBDC

Advantages:
- Speed (seconds)
- Certainty (immutable)
- Transparency (all participants see)
- Lower cost (fewer intermediaries)
- 24/7 operation

Challenges:
- Adoption (not all banks ready)
- Regulation (unclear in many jurisdictions)
- Technical standards (still developing)
- Cybersecurity (new attack vectors)

Transition:
- Parallel systems initially
- Traditional + blockchain
- Gradual migration
- Likely 5-10 year transition

Cost Impact:
- Today: $25-100 per settlement
- DLT: $0.01-1.00 per settlement
- Annual savings: Significant (billions globally)
```
