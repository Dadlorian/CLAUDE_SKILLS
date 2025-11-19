# Chargebacks Reference

## Overview
Chargebacks are customer disputes of credit card transactions. Merchants can lose transaction value plus fees. Prevention and management critical to fraud strategy.

## Chargeback Process

### Chargeback Timeline
```
Day 0: Transaction occurs
  ↓
Days 0-75: Cardholder notices issue
Day 75: Chargeback filing window closes
  (varies by card network: 120 days for Discover, 540 days for disputed access)
  ↓
Day 1 (after filing): Merchant notified of chargeback
  ↓
Days 1-10: Merchant investigates and submits response
  ↓
Days 10-30: Card network/issuer evaluates evidence
  ↓
Days 30-90: Dispute resolved (chargeback upheld or reversed)
```

### Financial Impact
```
Transaction Amount: $100
Chargeback Fee: $15-$100 (varies by network)
Processing Cost: Additional labor costs

Total Loss: $115-$200
Plus: Potential account suspension if rate too high
```

## Chargeback Reason Codes

### Card-Not-Present (CNP) Fraud
```
Mastercard 4855: Goods/Services Not Provided
  - Merchant never fulfilled order
  - Item never received
  - Service not rendered

Visa 30: Unauthorized Transaction
  - Cardholder claims they didn't authorize
  - Stolen card or account takeover
  - Third-party use without permission

Discover 4750: Goods/Services Not Provided
```

### Authorization-Related
```
Visa 12: No Card Member Authorization
  - No proper authorization obtained
  - Cardholder never approved

Mastercard 4863: Cardholder Does Not Recognize
  - Transaction not authorized by cardholder
  - Account compromise claim

Amex 162: Fraudulent Transaction - Card Present
  - Physical card was present
  - Card presented fraudulently
```

### Processing Errors
```
Visa 22: Incorrect Transaction Amount
  - Charged more than authorized
  - Pricing error

Mastercard 4834: Point of Interaction Error
  - Transaction processing error
  - Merchant system malfunction

Discover 4768: Multiple Transactions
  - Same transaction charged multiple times
  - Duplicate billing
```

### Return & Merchandise
```
Visa 7030: Invoice Number Not Matching
  - Item description doesn't match

Mastercard 4855: Goods/Services Not Provided
  - Item not received despite claim

Discover 4755: Goods/Services Not Provided
```

### Friendly Fraud Variants
```
"Item Not Received" (Most common)
- Customer received item but claims otherwise
- Merchant has delivery proof but insufficient

"Item Not As Described"
- Item received but doesn't match listing
- Subjective dispute (condition, color, etc.)

"Unauthorized Use"
- Cardholder claims they didn't authorize
- Legitimate purchase but disputing anyway

"Return Not Received"
- Customer claims returned item
- Merchant doesn't have proof of receipt
```

## Chargeback Prevention Strategies

### Transaction-Level Prevention
```
Clear Descriptors:
  - Merchant name/descriptor clear
  - Transaction amount correctly stated
  - Business description clear

Authorization:
  - Obtain explicit authorization
  - 3D Secure when possible
  - Save authorization proof

Communication:
  - Send confirmation email
  - Clear order description
  - Prominent return policy
  - Easy contact information
```

### Fraud Detection Integration
```
Block potentially fraudulent transactions:
  - High fraud risk scores
  - Impossible geography
  - Velocity concerns
  - New account abuse

Result:
  - Reduce fraud chargebacks
  - Lower chargeback rate
  - Protect merchant reputation
```

### Customer Verification
```
Identity verification:
  - Verify delivery address
  - Match billing/shipping
  - AVS (Address Verification System) checks
  - CVV verification

Device verification:
  - Device fingerprinting
  - Known device checking
  - Behavioral consistency

Result:
  - Reduce friendly fraud
  - Increase legitimate merchant protection
```

### Documentation
```
Keep records for 18+ months:
  - Transaction details
  - Authorization proof (AVS, CVV, 3DS)
  - Shipping/delivery proof
  - Communication with customer
  - Any disputes or refunds

For disputes:
  - Provide complete documentation
  - Delivery confirmation with signature
  - Photos of items
  - Return tracking information
  - Customer communication records
```

## Chargeback Representment

### Defense Strategy
```
Step 1: Receive chargeback notification
  - Note deadline (usually 7-10 days)
  - Assign investigation resources

Step 2: Investigate thoroughly
  - Pull transaction records
  - Gather all supporting evidence
  - Review customer communication
  - Check for refunds issued

Step 3: Prepare compelling response
  - Clear merchant descriptor
  - Strong proof of delivery
  - Authorization evidence
  - Customer communication
  - Policy compliance evidence

Step 4: Submit representment
  - Before deadline
  - Complete package
  - Professional presentation
  - Follow card network format
```

### Evidence Types

**Delivery Proof**
- Signed delivery confirmation
- GPS tracking data
- Photo of delivery
- Customer signature

**Authorization Proof**
- 3DS authentication records
- AVS match confirmation
- CVV match confirmation
- Cardholder sign-off email

**Communication Records**
- Order confirmation email
- Customer service interactions
- Tracking information sent
- Return policy acknowledgment

**Transaction Details**
- Clear merchant descriptor
- Item description matching listing
- Price matching authorization
- Timestamp consistency

### Representment Success Rates
```
Strong evidence (delivery + authorization): 80-90% success
Moderate evidence (one of above): 50-70% success
Weak evidence (minimal documentation): 10-30% success
No evidence: 0% success
```

## Chargeback Monitoring & Metrics

### Key Metrics
```
Chargeback Rate = Chargebacks / Total Transactions

Target rates:
- <0.5%: Excellent
- 0.5-1%: Acceptable
- 1-2%: Concerning
- >2%: Critical, risk of account termination

Card networks enforce limits:
- Visa: >1.5% = monitoring
- Mastercard: >1.0% = increased fees
- Amex: >0.6% = risk mitigation program
```

### Chargeback Breakdown Analysis
```
By Reason Code:
  - % unauthorized
  - % friendly fraud
  - % processing errors
  - % other

By Merchant Category:
  - Digital vs physical goods
  - High-risk vs low-risk
  - Recurring vs one-time

By Customer Segment:
  - New vs established
  - Geographic region
  - Customer lifetime value
```

### Trend Analysis
```
Daily/Weekly/Monthly trends:
  - Rising chargeback rate = alert
  - Seasonal patterns = baseline adjustment
  - Product changes correlation
  - Marketing campaign impact
```

## Chargeback Prevention Programs

### Visa Chargeback Monitoring Program
```
Thresholds:
- >1.5% monthly chargeback ratio
- >100 chargebacks/month

Consequences:
- Increased fees
- Enhanced monitoring
- Required remediation plan
- Possible account restriction

Prevention:
- Reduce to <1.0% within 30-60 days
- Implement prevention measures
- Regular reporting to Visa
```

### Mastercard Chargeback Monitoring Program
```
Thresholds:
- >1.0% monthly chargeback ratio
- >75 chargebacks/month

Consequences:
- Monthly fees
- Compliance monitoring
- Required action plan

Prevention:
- Reduce to <0.5% to exit program
- Regular performance review
```

### Amex Chargeback/Fraud Monitoring Program
```
Very strict standards:
- >0.6% ratio triggers program
- Amex can terminate accounts

Prevention:
- Implement strong fraud controls
- 3DS for all eligible transactions
- Excellent customer service
- Quick refund processing
```

## Friendly Fraud Prevention

### Detection Patterns
```
High risk indicators:
- Item not received claims with delivery proof
- Multiple chargebacks from same customer
- Chargebacks after delivery confirmation
- Claims inconsistent with transaction details
- Pattern of refund then chargeback
```

### Prevention Tactics
```
Product-Level:
- Digital goods: instant delivery proof
- Physical goods: signature required
- Downloadable: usage tracking
- Services: completion evidence

Customer-Level:
- New customer increased scrutiny
- Repeat offenders tracking
- Velocity checks
- Purchase pattern anomalies

Communication-Level:
- Clear return policies
- Easy refund/return process
- Proactive customer communication
- Response to customer concerns
```

### Case Management
```
Friendly fraud suspected:
1. Check customer history
2. Review all communications
3. Assess evidence strength
4. Prepare detailed response
5. Submit strongest case
6. Track case outcome
7. Build pattern knowledge
```

## Chargeback Integration with Fraud System

### Post-Transaction Learning
```
Chargeback received ->
Analyze transaction details ->
Update fraud model ->
Identify pattern ->
Adjust risk scoring ->
Prevent similar transactions

Example:
- Chargeback for "item not received"
- Transaction: high velocity + new customer
- Adjustment: increase weight of velocity for new customers
```

### Refund Strategy
```
Pre-emptive refund:
- Detect likely dispute
- Offer refund immediately
- Customer satisfaction maintained
- Avoid chargeback fees

Result:
- Reduce chargeback rate
- Improve customer satisfaction
- Lower total cost of dispute

Cost comparison:
- Refund: $100 (product cost)
- Chargeback: $100-$200 (product + fees)
```

## Chargeback Reporting

### Internal Reporting
```
Daily:
- Chargeback count
- Total amount
- Reason codes

Weekly:
- Trend analysis
- Prevention effectiveness
- Representment outcomes

Monthly:
- Comprehensive analysis
- Prevention program status
- Network compliance
- Remediation actions
```

### Network Reporting
```
Required for monitoring programs:
- Monthly chargeback statistics
- Reason code breakdown
- Remediation efforts
- Performance metrics
- Compliance certification
```

## Best Practices

1. **Prevention First**: Fraud prevention reduces chargebacks
2. **Documentation**: Keep complete records for 18+ months
3. **Communication**: Clear merchant info and policies
4. **Proactive**: Use delivery confirmation and signature
5. **Response**: Submit compelling representments
6. **Monitoring**: Track rates and trends closely
7. **Compliance**: Stay below network thresholds
8. **Feedback Loop**: Learn from chargebacks to improve
