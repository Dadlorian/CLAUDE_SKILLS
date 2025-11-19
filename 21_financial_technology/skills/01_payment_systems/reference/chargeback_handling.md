# Chargeback Handling Reference

## Overview

A chargeback is a reversal of a transaction initiated by the cardholder's bank (issuer) when the cardholder disputes the transaction. Chargebacks protect consumers but create liability for merchants and acquiring banks.

**Annual chargebacks**: ~600 million globally
**Typical merchant chargeback rate**: 0.05-0.5% of transactions
**Chargeback cost to merchant**: Transaction amount + $15-100 fee + potential account closure

## Chargeback Timeline

### Standard Process

```
Day 0: Transaction Occurs
- Customer makes purchase
- Transaction authorized and settled
- Funds available to merchant

Days 1-180: Chargeback Initiation Window
- Customer calls issuer to dispute
- Issuer initiates chargeback investigation
- Most chargebacks filed within 60-120 days

Typical Timeline (USA):
- Day 0: Transaction date
- Days 1-60: Customer dispute period (varies by reason code)
- Day 45-60: Issuer files chargeback claim
- Day 60-75: Acquiring bank notifies merchant
- Day 75-105: Merchant provides evidence
- Day 105-120: Issuer reviews evidence
- Day 120-180: Arbitration or resolution

Visa/Mastercard Timelines:
- Initial response: 7-10 days for merchant
- Issuer review: 30-45 days
- Total: 60-90 days typical
- Can extend to 540 days (extreme cases)
```

### Notification to Merchant

```
Chargeback Notification:
- Acquiring bank notifies merchant (usually via dashboard)
- Includes:
  - Chargeback date
  - Transaction reference
  - Chargeback amount
  - Reason code
  - Customer dispute description
  - Evidence deadline
  - Instructions for response

Response Deadline:
- Visa: 7-10 days (varies by code)
- Mastercard: 7-10 days (varies by code)
- Amex: 20 days typical
- Miss deadline: Automatic loss

Evidence Requirements:
- Signed sales receipt or electronic equivalent
- Proof of delivery
- Proof of authorization
- Customer communication
- Shipping records
- Email evidence
- Proof of service delivery (for digital goods)
```

## Chargeback Reason Codes

### Visa Reason Codes

**Category 1: Authorization-Related** (10.1-10.9)
```
10.1: Unauthorized Transaction
- Cardholder claims they didn't authorize
- Most common reason code
- ~35% of all chargebacks
- Merchant defense: Signed receipt, 3DS proof

10.3: No Authorization
- Similar to 10.1
- No CID match claimed
- Merchant defense: CID match proof

10.4: Transaction Not Permitted
- Card used without authorization
- Lost/stolen card claim
- Merchant defense: Shipping proof

10.5: Product Not as Described (Goods)
- Goods delivered but not as advertised
- Quality issues
- Wrong item
- Merchant defense: Signed receipt, proof of delivery

10.6: Transaction not Recognized
- Unrecognized recurring transaction
- Customer claim: cancelled subscription
- Merchant defense: Cancellation confirmation
```

**Category 2: Processing Error** (12.1-12.9)
```
12.1: Late Presentment
- Transaction presented after authorization valid period
- Rare with modern processing
- Merchant defense: Timely presentment proof

12.2: Incorrect Transaction Amount
- Merchant charged wrong amount
- Customer charged twice
- Merchant defense: Correct amount proof

12.3: Incorrect Currency
- Wrong currency applied
- Merchant defense: Correct currency proof

12.4: Non-Matching Account Number
- Account number doesn't match card
- System error
- Merchant defense: Technical error proof

12.5: Duplicate Processing
- Same transaction charged multiple times
- System error
- Merchant defense: Duplicate check
```

**Category 3: Fraud** (13.1-13.9)
```
13.1: Counterfeit Transaction
- Forged card or data
- Card skimming
- Merchant defense: Device receipt
- Chip vs. swipe analysis
- Declining rate: Low (merchant usually wins)

13.2: Card Not Present Fraud
- CNP fraud
- Card data stolen and used online
- Merchant defense: 3DS, address match, CVV match
- Declining rate: High (merchant usually loses)

13.3: Not In-Person
- Card wasn't physically present
- Merchant defense: Shipping proof
- Address verification
- 3D Secure

13.4: Insufficient Identification
- Cardholder couldn't be identified
- Rare in card-present
- Merchant defense: ID verification

13.5: Card Not Valid or Expired
- Merchant accepted expired card
- Merchant defense: Swipe proof (should decline)

13.6: Recurring Transaction Not Cancelled
- Subscription not cancelled
- Cardholder claims cancellation
- Merchant defense: Cancellation proof
- Clear terms and conditions

13.7: Partial Cancellation Reversal
- Some transaction cancelled
- Merchant didn't process refund
- Merchant defense: Refund proof
```

**Category 4: Consumer Disputes** (20.1, 20.3-20.8)
```
20.1: Merchant Return Disputes
- Customer returned item
- Merchant didn't refund
- Winning rate: ~5% (merchant usually loses)
- Merchant defense: Cancellation policy

20.3: Service Not Rendered
- Service promised but not delivered
- Merchant defense: Proof of service
- Completion documentation

20.4: Goods Damaged on Delivery
- Physical damage to goods
- Merchant defense: Insurance claim
- Shipping proof

20.5: Goods Not Received
- Delivery claim vs. merchant claim
- Merchant defense: Tracking proof
- Signature confirmation
- Geolocation data

20.6: Goods Not As Described
- Items don't match description
- Quality issues
- Merchant defense: Product description
- Communication with customer

20.7: Cancel Recurring Transaction
- Customer authorized but wants to cancel
- Merchant defense: Cancellation confirmation
- Clear billing/cancellation process

20.8: Timely Notification
- Merchant didn't give proper notice
- For recurring billings
- Merchant defense: Terms and communication
```

**Category 5: Account Management** (30.x-30.9)
```
30.1: Dollar Amount Coding Error
- Merchant coded wrong amount
- Rare with modern systems
- Merchant defense: Correct coding

30.2: Transaction Submitted in Error
- Merchant accidentally submitted
- Duplicate processing
- Merchant defense: Delete and resubmit

30.3: Not as Submitted
- Transaction data was altered
- Merchant defense: Original submission
```

### Mastercard Reason Codes

Similar structure to Visa with variations:
```
4101: Cardholder-Initiated Retrieval Request
- Basic unauthorized claim
- Similar to Visa 10.1
- Merchant win rate: ~35%

4302: Merchant Error
- Merchant made mistake
- Processing error
- Merchant win rate: ~10%

4321: Invalid Card Number
- Account number doesn't match
- System error
- Merchant win rate: ~20%

4325: Chargeback Rights Not Recognized
- Cardholder claims no authorization
- Merchant win rate: ~40%

4554: Goods/Services Not Received or Only Partially Received
- Delivery dispute
- Merchant win rate: ~50% (with tracking)

4855: Goods/Services Not as Described or Defective
- Quality/mismatch dispute
- Merchant win rate: ~20%

4863: Cardholder Does Not Recognize - Possible Fraud
- Claimed CNP fraud
- Merchant win rate: ~25%

4871: Chip Liability Shift
- Merchant didn't use chip
- Merchant win rate: ~5%
```

## Chargeback Defense Strategy

### Evidence Collection

```
Critical Evidence:
1. Authorization Proof
   - Signed receipt (physical)
   - Electronic authorization
   - 3D Secure proof (ECI + CAVV)
   - API response showing approval
   - Timestamp of authorization

2. Address Verification
   - AVS (Address Verification Service) match
   - Billing address match
   - Shipping address match
   - Document showing addresses

3. Card Verification
   - CVV match proof
   - Card present indicator
   - Chip/PIN transaction (if available)
   - Signature match (for card-present)

4. Delivery Proof
   - Tracking number
   - Shipping carrier proof
   - Signature confirmation
   - Geolocation data
   - Delivery photo
   - UPS/FedEx delivery confirmation

5. Service Delivery Proof
   - Service completion documentation
   - Customer communication
   - Usage logs (for digital goods)
   - Download confirmations
   - Email confirmation

6. Customer Communication
   - Email correspondence
   - Chat logs
   - Support tickets
   - Return/refund requests
   - Order confirmation sent to customer

7. Business Records
   - Invoice
   - Order confirmation
   - Terms and conditions
   - Privacy policy
   - Refund policy
   - Cancellation documentation
```

### Defense Evidence Package

```
Organization:
1. Cover letter with key facts
2. Numbered evidence list
3. Organized exhibits

Example Package:

---COVER LETTER---
Date: January 15, 2024
To: Merchant Services Department

Re: Chargeback Dispute - Transaction XXX

On December 15, 2023, our merchant processed a transaction
for $99.99 by cardholder John Doe, Card ending in 4242.

We provide comprehensive evidence of authorization and
delivery as outlined below:

Key Facts:
- Transaction was properly authorized
- Customer information was verified
- Goods were shipped and signed for
- Customer communication confirms receipt

We respectfully request reversal of this chargeback.

---EXHIBITS---

Exhibit 1: Transaction Authorization
- Payment processor confirmation
- Timestamp: 2023-12-15 14:30:45 UTC
- Amount: $99.99
- AVS: Match
- CVV: Match
- 3DS Result: Authenticated (ECI 05)

Exhibit 2: Order Confirmation
- Order number: ORD-2023-12345
- Customer email: john.doe@example.com
- Date: 2023-12-15
- Amount: $99.99

Exhibit 3: Shipping Proof
- Tracking number: 1Z999AA1012345678
- Carrier: UPS
- Ship date: 2023-12-16
- Delivery date: 2023-12-19
- Signature: J. Doe
- Photo confirmation: [image]

Exhibit 4: Customer Communication
- Order confirmation email
- Delivery notification email
- Customer received and signed
- No complaints or issues raised

---END EXHIBITS---
```

## Prevention Strategies

### 3D Secure Implementation

```
Reduces Chargebacks:
- 3DS authentication provides proof
- Liability shift to issuer
- Fraud chargebacks much harder
- Implementation: See 3D Secure reference

Impact:
- Chargebacks from fraud: 80% reduction
- Unauthorized transaction claims: 70% reduction
- Overall chargeback rate: 40-50% reduction
```

### AVS and CVV Matching

```
Address Verification System (AVS):
- Match billing address on file
- Reduce fraud
- Score impact: Improves decision

CVV Verification:
- Verify 3-digit code
- Proves card in hand
- Score impact: Improves decision

Implement:
- Always request AVS/CVV
- Verify match
- Decline on mismatch (or review)
- Document in authorization response

Impact:
- Fraud reduction: 20-30%
- False positives: 5-10% decline rate increase
```

### Delivery Tracking and Signature

```
Signature Confirmation:
- Require signature on delivery
- Proof of delivery
- Legal documentation
- Protects against "not received" claims

Tracking Requirement:
- Always use trackable shipping
- Not USPS First Class (poor tracking)
- Use UPS, FedEx, DHL
- Signature confirmation adds $1-5 per package

Cost-Benefit:
- Signature fee: $2-5 per order
- Chargeback loss: $99-300+ (transaction + fees)
- ROI: Positive if chargeback rate > 2%
- Recommended: For orders > $50

Implementation:
- Automatic for high-risk orders
- Optional for customers ($2-5 fee)
- Tracking provided to customer
- Delivery photo evidence captured
```

### Clear Policies and Communication

```
Key Policies:
1. Terms and Conditions
   - Clearly state what customer gets
   - Return/refund policy
   - Cancellation policy
   - Shipping policy
   - Digital goods policy

2. Refund Policy
   - Clear refund process
   - Timeline for refunds
   - Conditions for refunds
   - Exceptions documented

3. Cancellation Policy
   - How to cancel subscription
   - Cancellation window
   - No questions asked policy
   - Easy cancellation process

4. Digital Goods
   - No refunds for digital goods
   - Delivery methods
   - Instant delivery documentation
   - Usage rights

Communication:
- Send order confirmation immediately
- Include tracking information
- Proactive delivery notification
- Post-delivery follow-up
- Customer service accessibility
```

### Recurring Transaction Management

```
Best Practices:
1. Clear Billing Description
   - Merchant descriptor must be clear
   - Include company name and service
   - Not cryptic or confusing

2. Preauthorization
   - Get customer agreement in writing
   - Store agreement/authorization
   - Clearly state: amount, frequency, term

3. Notification Before Billing
   - Send reminder before billing date
   - Especially for variable amounts
   - Allow easy modification

4. Cancellation Process
   - Easy one-click cancellation
   - No friction
   - Confirmation email
   - Refund issued if needed

5. Unusual Charges
   - Flag unusually large charges
   - Verify with customer first
   - Allow customer to approve

Example Recurring Notification:
---
Subject: Your [Service Name] Subscription Renews Tomorrow

Hi [Customer Name],

Your [Service Name] subscription renews tomorrow.

Billing Amount: $9.99
Billing Date: January 20, 2024
Billing Frequency: Monthly

To manage your subscription:
- Change plan: [link]
- Update payment method: [link]
- Cancel subscription: [link]

Questions? Contact us at support@example.com

---
```

## Chargeback Response Process

### Decision Tree

```
Chargeback Received
   |
   v
Read Reason Code and Details
   |
   v
Determine Liability
   |
   +-- Legitimate Chargeback?
   |   (No evidence or clearly wrong)
   |   |-> ACCEPT and REFUND (not all)
   |
   +-- Clear Evidence Available?
   |   (Strong case to win)
   |   |-> GATHER EVIDENCE
   |
   +-- Weak Evidence?
   |   (Risky case)
   |   |-> GATHER BEST EVIDENCE
   |       AND DECIDE
   |
   v
Gather Evidence
   |
   +-- Authorization Proof
   +-- Address Verification
   +-- Delivery Proof (if applicable)
   +-- Customer Communication
   +-- Merchant Records
   |
   v
Assess Evidence Quality
   |
   v
Win Rate Prediction
   |
   +-- High Win Rate (>80%)
   |   |-> FIGHT (invest time/cost)
   |
   +-- Medium Win Rate (40-80%)
   |   |-> FIGHT (if merchant is high value)
   |
   +-- Low Win Rate (<40%)
   |   |-> ACCEPT (write off loss)
   |
   v
Submit Response
   |
   v
Monitor for Appeal
   |
   v
Resolution
```

### Winning Strategies by Reason Code

```
10.1: Unauthorized Transaction
- Win Rate: 35-45% (difficult)
- Key Evidence:
  - 3D Secure proof (most important)
  - AVS/CVV match
  - Shipping proof
  - Customer communication
- Strategy: Focus on 3DS if available
- If no 3DS: Accept loss unless exceptional evidence

4554: Goods Not Received
- Win Rate: 60-75% (with tracking)
- Key Evidence:
  - Tracking number with signature
  - Delivery photo
  - Geolocation data
- Strategy: Require signature confirmation
- Without signature: Win rate drops to 20%

4855: Goods Not as Described
- Win Rate: 20-30% (very difficult)
- Key Evidence:
  - Product description from listing
  - Customer communication
  - Return request documentation
  - Customer refusal to cooperate
- Strategy: Offer refund/replacement
- Win rate improves with clear documentation
- Preventive: Detailed descriptions, photos

4863: Card Not Present Fraud
- Win Rate: 20-35% (difficult)
- Key Evidence:
  - 3D Secure proof (critical)
  - AVS/CVV match
  - IP geolocation match
  - Customer account history
- Strategy: 3DS mandatory for e-commerce
- Without 3DS: Likely loss

4871: Chip Liability Shift
- Win Rate: 5-10% (almost always lose)
- Reason: Card present transaction liability shifted to merchant
- Strategy: Use chip/EMV reader for card-present
- Acceptance: Not fighting pays off (cost savings)

6.1: Recurring Transaction Not Cancelled
- Win Rate: 40-60% (moderate)
- Key Evidence:
  - Cancellation confirmation
  - Terms showing how to cancel
  - Email confirming cancellation
  - Billing terms
- Strategy: Document easy cancellation process
- Evidence: Cancellation email sent before chargeback claim
```

## Chargeback Prevention Tools

### Fraud Detection

```
Real-Time Fraud Scoring:
- Machine learning models
- Velocity checks
- Device fingerprinting
- Behavioral analysis
- Decline high-fraud transactions pre-authorization

Example Rules:
- Multiple cards from same customer (30 days)
- Multiple transactions from different cards (30 minutes)
- Shipping address ≠ billing address
- New customer + high amount
- IP doesn't match geolocation
- Device never seen before
- VPN/Proxy detected
```

### Risk Scoring

```
Risk Score Components:
- Customer history (40%)
- Transaction amount (20%)
- Merchant category (20%)
- Device risk (10%)
- Geographic risk (10%)

Low Risk: < 30 (approve, no 3DS needed)
Medium Risk: 30-70 (approve with 3DS optional)
High Risk: 70-100 (require 3DS, review)
Very High: > 100 (decline or escalate)
```

### Chargeback Dispute Rate Monitoring

```
Metrics:
- Monthly chargeback rate (%)
- Chargeback rate by reason code
- Win/loss rate by reason
- Cost of chargebacks vs. revenue
- Trend analysis (increasing/decreasing)

Thresholds:
- Visa/Mastercard limits by region
- Typically: 0.5% chargeback rate
- Exceed limits: Penalties, fees, suspension risk

Responses:
- < 0.3%: Excellent
- 0.3-0.5%: Good
- 0.5-1.0%: At Risk
- > 1.0%: High Risk (remediation required)

Remediation:
- Implement 3D Secure
- Improve fulfillment
- Better customer service
- Enhanced verification
- Loss mitigation
```

## Chargeback Costs

### Visible Costs

```
Per Chargeback:
- Transaction amount: $0-500+ (varies)
- Chargeback fee: $15-100 (typically $25-50)
- Wire transfer fee: $0-30
- Representment fee (if fight): $10-100
- Arbitration fee: $500-2,500 (if escalated)
- Legal fees: $500-5,000+ (if litigated)

Total Cost Per Chargeback:
- Simple case: $50-100
- Fought case: $100-300
- Escalated/arbitration: $500-2,500+
- Litigation: $5,000+

Annual Impact (1,000 chargebacks):
- Average cost: $100 per chargeback
- Total: $100,000 annually
- Plus: Time investment by staff
- Plus: Loss of customer lifetime value
```

### Hidden Costs

```
Opportunity Costs:
- Staff time investigating: 30 min - 2 hours per chargeback
- Annual cost for 1,000 chargebacks: $50,000-100,000

Reputational Costs:
- Customer churn (lost future sales)
- Negative reviews
- Payment processor restrictions
- Risk of account closure

Financial Costs:
- Card processor fee increases (higher rates)
- Reserve requirements (10-20% of monthly volume)
- Potential account termination
- Having to find new processor (difficult)

Example:
1% chargeback rate with $100,000 monthly volume:
- 1,000 transactions, 10 chargebacks
- Direct cost: $1,000-3,000
- Staff time: $1,500-2,500
- Customer lifetime value lost: $5,000+
- Total monthly impact: $7,500-10,500
- Annual impact: $90,000-126,000
- Plus: Risk of processor penalties
```
