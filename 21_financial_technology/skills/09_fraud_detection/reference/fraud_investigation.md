# Fraud Investigation Reference

## Overview
Fraud investigation is the systematic examination of suspected fraudulent cases to confirm fraud, identify perpetrators, recover losses, and improve detection.

## Investigation Workflow

### Case Lifecycle
```
1. Alert Generation
   - Rules triggered or model flagged transaction
   - Alert routed to investigation queue

2. Case Assignment
   - Analyst reviews alert
   - Assigned to investigator
   - Priority level set

3. Initial Assessment
   - Quick review of red flags
   - Obvious fraud: Fast-track block
   - Unclear: Deep investigation

4. Evidence Gathering
   - Transaction details review
   - Customer communication check
   - Supporting documentation
   - Network/device analysis

5. Hypothesis Formation
   - What fraud type is this?
   - Who is the perpetrator?
   - What is the scope?
   - What is the evidence?

6. Decision & Action
   - Confirm fraud: Block, report, recover
   - Not fraud: Whitelist, prevent false declines
   - Uncertain: Manual hold, customer contact

7. Closure & Learning
   - Document findings
   - Update systems
   - Train models
   - Feed back to prevention
```

## Investigation Techniques

### Transaction Analysis

**Timeline Reconstruction**
```
Purpose: Understand full scope of fraudulent activity

Method:
1. Pull all transactions for account
2. Sort chronologically
3. Identify patterns
4. Determine fraud timeline
5. Group by fraud pattern

Example:
Day 1: Small test transactions ($10, $25)
Day 2-3: Multiple transactions increasing
Day 4: Large transaction blocked
Day 5: Account locked by customer

Pattern: Escalating fraud, detected on Day 4
```

**Amount Analysis**
```
Purpose: Identify unusual transaction amounts

Method:
1. Calculate baseline (mean, std dev)
2. Compare current to baseline
3. Identify spike transactions
4. Check merchant category

Example:
Baseline: $50 average (±$30)
Flagged transaction: $2,500
Deviation: 60 std devs above mean
Fraud risk: CRITICAL
```

**Merchant Analysis**
```
Purpose: Identify suspicious merchant patterns

Method:
1. List merchants from account
2. Categorize by risk level
3. Check merchant reputation
4. Identify high-risk concentrations

Example:
Legitimate merchants: Groceries, Gas, Utilities
Fraudulent merchants: Money transfer, Crypto, Gift cards
Pattern: Clear shift to high-risk merchants = FRAUD
```

### Device & Network Investigation

**Device Tracking**
```
Purpose: Identify device involvement in fraud

Method:
1. Extract device fingerprints
2. Historical device analysis
3. Track linked accounts
4. Assess device reputation

Evidence:
- Device first seen: 1 hour ago (NEW)
- Device used by: 50 accounts (SUSPICIOUS)
- Device fraud history: 3 confirmed fraud cases
- Device chargeback rate: 15% (HIGH)

Conclusion: Device is fraud ring hub
```

**Network Analysis**
```
Purpose: Identify fraud ring involvement

Method:
1. Pull customer network (devices, cards, addresses)
2. Cross-reference with known fraudsters
3. Assess network clustering
4. Identify ring members

Evidence:
- Customer A linked to Device X
- Device X also linked to Customers B, C, D (all flagged)
- All enrolled within 2 hours
- All transactions to same address

Conclusion: Fraud ring with 4+ members
```

**Geographic Analysis**
```
Purpose: Identify impossible or suspicious geography

Method:
1. Map transaction locations
2. Calculate distances
3. Check time between transactions
4. Assess plausibility

Example:
Transaction 1: New York, 2:00 PM
Transaction 2: Los Angeles, 2:30 PM
Distance: 2,500 miles
Time: 30 minutes
Travel speed needed: 5,000 mph (IMPOSSIBLE)

Conclusion: Geographic fraud confirmed
```

### Customer Communication Investigation

**Email Analysis**
```
Purpose: Understand customer communication

Analysis:
1. Email account creation date
2. Email domain (.com vs spoofed)
3. Previous use pattern
4. Communication tone
5. Language patterns

Evidence:
- Email: banking.secure123@gmail.com (spoofed)
- Created 1 hour ago
- Never used before
- Misspelled company name
- Poor English grammar

Conclusion: Suspicious email, likely fraudster
```

**Phone Number Verification**
```
Purpose: Verify phone authenticity

Method:
1. Check phone number format
2. Verify area code legitimacy
3. Cross-reference with customer
4. Check linked accounts

Evidence:
- Phone: +1 234 567 8901
- Area code: Valid
- Linked to 50 accounts
- Multiple chargebacks
- VoIP service (common fraud)

Conclusion: Phone is fraud tool
```

**Customer Contact**
```
Purpose: Verify transaction legitimacy

Method:
1. Use known contact info
2. Ask about specific transaction
3. Listen for knowledge/reaction
4. Verify recent activity

Evidence:
- Customer: "I don't know this transaction"
- Amount: $2,500 (large for them)
- Merchant: Crypto (not typical)
- Timing: 3 AM (unusual)

Conclusion: Transaction is unauthorized
```

## Evidence Documentation

### Case Evidence Checklist
```
Transaction Evidence:
[ ] Transaction ID and timestamp
[ ] Amount and currency
[ ] Merchant information
[ ] Authorization method (AVS, CVV, 3DS)
[ ] Customer location at time

Device Evidence:
[ ] Device fingerprint
[ ] Device type and OS
[ ] Device age (first seen date)
[ ] Device fraud history
[ ] Linked accounts via device

Network Evidence:
[ ] Shared cards/devices
[ ] Shared addresses
[ ] Shared contact information
[ ] Graph of relationships
[ ] Known fraudster connections

Behavioral Evidence:
[ ] Deviation from baseline
[ ] Velocity patterns
[ ] Time-of-day pattern
[ ] Typing/navigation patterns
[ ] Account changes

Documentation Evidence:
[ ] Customer communication
[ ] Support tickets
[ ] Refund requests
[ ] Chargeback filings
[ ] Complaint records
```

### Evidence Grading
```
Conclusive (A):
- Multiple strong evidence types
- Clear fraud indicators
- Consistent pattern
- High confidence decision

Strong (B):
- Several strong evidence items
- Few contradictions
- High likelihood fraud
- Some ambiguity

Moderate (C):
- Mix of strong and weak evidence
- Some contradictions
- Medium likelihood
- Significant ambiguity

Weak (D):
- Limited evidence
- Many contradictions
- Low likelihood
- High ambiguity

Inconclusive (E):
- Insufficient evidence
- Cannot make determination
- Requires more investigation
```

## Investigation Decision Framework

### Decision Matrix
```
Evidence Grade vs. Transaction Amount:

           < $100    $100-$1K   $1K-$10K   > $10K
Grade A    BLOCK     BLOCK      BLOCK      BLOCK
Grade B    ALLOW*    BLOCK      BLOCK      BLOCK
Grade C    ALLOW*    ALLOW*     BLOCK      BLOCK
Grade D    ALLOW     ALLOW      ALLOW*     BLOCK
Grade E    ALLOW     ALLOW      ALLOW      ALLOW*

*ALLOW = Monitor closely for future patterns
*BLOCK = Automatic prevention on future
```

### Actions by Determination

**Confirmed Fraud**
```
Immediate Actions:
1. Block transaction
2. Lock account
3. Notify customer
4. Retrieve evidence
5. File fraud report

Follow-up Actions:
1. Prevent similar patterns
2. Check linked accounts
3. Investigate fraud ring
4. Coordinate with payment processor
5. Update prevention rules

Recovery Actions:
1. Attempt chargeback recovery
2. Law enforcement reporting
3. Asset recovery (if possible)
4. Customer reimbursement
```

**Likely Fraud**
```
Immediate Actions:
1. Block transaction
2. Request verification
3. Add to watchlist
4. Monitor account closely

Investigation Actions:
1. Gather more evidence
2. Customer contact
3. Device tracking
4. Network analysis

Decision:
1. Escalate to confirmed if more evidence
2. Escalate if pattern emerges
3. Whitelist if proven legitimate
```

**Uncertain**
```
Immediate Actions:
1. Manual review hold
2. Require verification
3. Monitor activity

Investigation Actions:
1. Customer contact
2. Request documentation
3. Behavioral analysis
4. Wait for pattern confirmation

Decision:
1. Escalate if evidence grows
2. Allow if legitimate verified
3. Continue monitoring if unclear
```

**Not Fraud**
```
Immediate Actions:
1. Allow transaction
2. Add to whitelist (optional)
3. Reduce scrutiny

Follow-up Actions:
1. Apologize if falsely flagged
2. Improve prevention rules
3. Prevent future false positives
4. Analyze why false flag occurred
```

## Investigation Quality & Performance

### Investigator Metrics
```
Productivity:
- Cases per day: 8-12
- Case resolution time: 2-4 hours
- Cases pending > 24 hours: < 5%

Accuracy:
- False positive rate: < 5%
- False negative rate: < 2%
- Unconfirmed rate: < 10%

Quality:
- Chargeback recovery rate: > 50%
- Customer satisfaction: > 80%
- Appeal rate: < 5%
```

### Supervision & QA
```
Sampling:
- 10% of cases reviewed weekly
- All high-dollar cases reviewed
- All complex cases reviewed
- All appeals reviewed

Areas Reviewed:
- Evidence sufficiency
- Decision logic
- Documentation quality
- Timeliness
- Process compliance

Feedback:
- Weekly coaching
- Monthly training
- Performance improvement plans
- Incentives for excellence
```

## Investigation Tools & Systems

### Case Management Platform
```
Features:
- Centralized case database
- Assignment workflows
- Evidence attachment
- Decision documentation
- Collaboration tools
- Audit trails
```

### Investigation Tools
```
Data Analysis:
- Transaction query tool
- Customer relationship viewer
- Device network visualizer
- Temporal analysis tools

Communication:
- Customer contact tools
- Bulk messaging
- Survey systems
- Callback scheduling

Documentation:
- Case note templates
- Evidence checklist
- Decision templates
- Report generation
```

## Investigations by Fraud Type

### Account Takeover Investigation
```
Key Questions:
1. When did unauthorized access start?
2. How did attacker gain access?
3. What accounts/cards accessed?
4. What transactions made?
5. Is account still compromised?
6. What data accessed?

Evidence Needed:
- Login location changes
- Device fingerprint changes
- Password change records
- IP address history
- Failed login attempts
- Affected transactions
- Credential compromise evidence

Actions:
- Force password reset
- Revoke active sessions
- Lock suspicious devices
- Check for data breach
- Contact customer
- Monitor for re-compromise
```

### Card Fraud Investigation
```
Key Questions:
1. How was card number obtained?
2. Where is original card?
3. What transactions were made?
4. How many merchants compromised?
5. Are other cardholders affected?
6. Is card still active?

Evidence Needed:
- Transaction history
- Merchant analysis
- Amount patterns
- Geographic analysis
- Device information
- Authorization data
- Shipping addresses

Actions:
- Card replacement authorization
- Merchant investigation
- Dispute chargebacks
- Alert other customers if breach
- Coordinate with card issuer
- Update fraud detection
```

### Friendly Fraud Investigation
```
Key Questions:
1. Did customer truly not receive item?
2. Is customer lying about non-receipt?
3. Is this pattern of abuse?
4. What evidence exists?

Evidence Needed:
- Delivery confirmation
- Customer communication
- Account history
- Refund history
- Return history
- Repeat complaint pattern

Actions:
- Provide delivery proof for chargeback
- Customer communication
- Document pattern
- Prevent future transactions
- Offer resolution
- Report repeat offender
```

## Investigation Best Practices

1. **Thorough Documentation**
   - Record all findings
   - Document evidence
   - Explain reasoning
   - Maintain audit trail

2. **Objective Analysis**
   - Avoid assumptions
   - Follow evidence
   - Consider alternatives
   - Challenge conclusions

3. **Time Management**
   - Prioritize high-value cases
   - Work efficiently
   - Escalate when appropriate
   - Don't over-investigate

4. **Customer Respect**
   - Professional communication
   - Assume innocence initially
   - Provide explanations
   - Resolve quickly

5. **Continuous Learning**
   - Study fraud patterns
   - Learn from feedback
   - Improve investigative skills
   - Share knowledge

6. **Compliance**
   - Follow procedures
   - Meet regulatory requirements
   - Maintain confidentiality
   - Document appropriately

7. **Collaboration**
   - Work with prevention team
   - Share findings
   - Coordinate on networks
   - Improve systems together
