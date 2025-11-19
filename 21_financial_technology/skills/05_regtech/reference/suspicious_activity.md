# Suspicious Activity Indicators and Detection

## Money Laundering Typologies

### Placement Schemes

```
STRUCTURING (Smurfing)
Description: Breaking down large illicit proceeds into smaller transactions
Indicators:
├── Multiple transactions just below $10,000
├── Same customer, multiple days/accounts
├── Different locations/branches
├── Different payment methods
├── Round amounts ($5,000, $4,000, $3,000)
├── Rapid deposits followed by withdrawals
├── Multiple customers depositing to same beneficiary
├── Different persons depositing on behalf of one customer
└── Unusual combinations of customers/deposit amounts

Red Flags:
├── "Smurfs" known to authorities
├── Repeated patterns over time
├── Inconsistent with customer profile
├── Customer defensive about deposits
└── Deposits followed by immediate transfers

Detection Approach:
├── Aggregate daily transactions by customer
├── Identify patterns just below threshold
├── Cross-reference smurfs
├── Look for shared beneficiaries
├── Monitor cumulative behavior
└── Alert on pattern frequency

Example:
├── Customer deposits $9,500 on Monday
├── $8,500 on Tuesday
├── $7,000 on Wednesday
├── $6,800 on Thursday
├── Total: $31,800 in 4 days
├── Customer never deposits > $5,000 normally
├── Triggers structuring alert
└── Higher alert score
```

### Trade-Based Money Laundering (TBML)

```
DEFINITION: Using international trade to hide illicit proceeds

METHODS:
1. Over-Invoicing
   ├── Import inflated prices for goods
   ├── Smuggling exporter receives overpayment
   ├── Pays "true" value, keeps difference
   └── Hides proceeds as legitimate payment

2. Under-Invoicing
   ├── Export at artificially low price
   ├── Buyer receives goods discounted
   ├── Seller hides proceeds in buyer's invoice
   └── True cost paid separately, laundered

3. Over-Shipment
   ├── Ship more goods than invoiced
   ├── Buyer pays for invoiced amount only
   ├── Seller receives payment for excess elsewhere
   └── Creates discrepancy in records

4. Round-Tripping
   ├── Goods exported, returned, re-exported
   ├── Value increases with each transaction
   ├── Creates appearance of legitimate business
   ├── Final value much higher than initial

Red Flags:
├── Import/export price discrepancies
├── Goods routed through multiple countries
├── Goods value inconsistent with market
├── Frequent round-trip transactions
├── Unusual commodity selections
├── Payments to/from high-risk jurisdictions
├── Invoice/shipment mismatches
├── Discrepancies in bill of lading
└── Complex intermediaries in supply chain

Detection:
├── Compare prices to market benchmarks
├── Verify shipment documentation
├── Track commodity values over time
├── Identify circular flows
├── Monitor unusual trade patterns
└── Cross-reference with customs data
```

### Cash-Intensive Business AML

```
BUSINESS TYPES:
├── Casinos and gambling establishments
├── Money services/MSBs
├── Restaurants and bars
├── Retail and shops
├── Hotels and hospitality
├── Transportation (taxis, ride-sharing)
├── Entertainment venues
├── Real estate (cash sales)
└── Personal services

CONCERNS:
├── Legitimacy of cash deposits
├── Difficulty distinguishing illicit/licit funds
├── Tax evasion indicators
├── Size and frequency unusual
├── Patterns inconsistent with business
├── Rapid movement of funds
├── No supporting documentation
└── Beneficial owner unclear

Suspicious Patterns:
├── Cash deposits > expected business level
├── Deposits inconsistent with operating hours
├── Round amounts inconsistent with actual sales
├── Sudden increase in deposits
├── Large cash deposits followed by quick withdrawal
├── Structured deposits to avoid reporting
├── Deposits in different branches/banks
├── Customer documentation lacking
└── No supporting invoices/receipts

Example:
├── Small restaurant $30K-50K monthly revenue
├── Deposits suddenly jump to $500K/month
├── No corresponding increase in staff/supplies
├── Deposits in round numbers ($100K exactly)
├── Quick transfers out of account
├── No supporting invoices
└── Owner evasive about business growth
```

### Layering Schemes

```
COMPLEX TRANSACTION CHAINS:

Wire Transfer Layering
├── Customer receives large wire
├── Immediately splits into multiple wires
├── Multiple intermediary jurisdictions
├── Final recipient remote from original
├── Difficult to trace beneficial owner
└── Documentation weak/missing

Red Flags:
├── Multiple wires to same beneficiary country
├── Wires routed through multiple banks
├── Correspondent banking chains
├── Beneficiary frequently changes
├── Wires split into odd amounts
├── Wires between unrelated parties
├── Haste in transaction execution
└── Nervousness about transaction

Shell Company Usage
├── Creation of legal entities
├── Minimal legitimate business
├── Asset ownership transfer
├── Quick dissolution/creation
├── Opaque beneficial ownership
├── Jurisdiction selection (secrecy)
└── Frequent ownership changes

Detection Approach:
├── Trace fund flows
├── Identify ultimate beneficiary
├── Assess business rationale
├── Document fund sources
├── Monitor for patterns
├── Compare to customer profile
└── Escalate inconsistencies

```

### Integration Schemes

```
RETURN TO LEGITIMATE ECONOMY:

Real Estate Purchase
├── Large cash purchase
├── Entity ownership structure
├── Quick sale at profit
├── Mortgage obtained (loan layering)
├── Refinance multiple times
└── Eventual sale at market value

Red Flags:
├── All-cash purchase
├── Purchase price significantly below market
├── Quick resale at higher price
├── Unusual payment methods
├── Non-local buyer
├── Complex entity ownership
├── Weak documentation
├── Financing inconsistent with value
└── Beneficial owner absent from transaction

Business Investment
├── Investment in legitimate business
├── Increased revenue (from laundered funds)
├── Investor takes profits
├── Funds appear legitimate
└── Integration complete

Red Flags:
├── Investment inconsistent with buyer profile
├── Overpayment for business
├── Quick capital injection
├── Investor uninvolved in operations
├── Revenue increase unexplained
├── Profits extracted quickly
├── Beneficial owner structures
└── Business previously unprofitable

Asset Purchase
├── High-value items purchased
├── Jewels, art, antiques
├── Resold in legitimate market
├── Proceeds appear clean
└── Origin of funds obscured

Red Flags:
├── All-cash art/jewelry purchases
├── No collection history
├── Expert appraisal inconsistencies
├── Quick resale at profit
├── Lack of ownership documentation
├── Complex transaction structure
└── Buyer profile inconsistent
```

## Terrorist Financing Indicators

### Legitimate Activity with Suspicious Elements

```
CHARACTERISTICS OF POTENTIAL TF:

1. Unusual Transaction Patterns
   ├── Small, inconspicuous amounts
   ├── Frequent transfers
   ├── Round amounts ($5,000 increments)
   ├── No clear business purpose
   ├── Inconsistent with customer profile
   ├── Rapid movement of funds
   ├── Multiple account involvement
   └── Geographic spread

2. Beneficiary Concerns
   ├── Beneficiary in conflict zone
   ├── Beneficiary identity unclear
   ├── Beneficiary frequently changes
   ├── Multiple unrelated beneficiaries
   ├── Islamic religious organizations
   ├── Charitable organizations to high-risk regions
   ├── NGOs in terrorism-associated areas
   └── Individuals with terrorist associations

3. Communication and Documentation
   ├── Vague remittance descriptions
   ├── Coded language in communications
   ├── Minimal supporting documentation
   ├── Discrepancies in documentation
   ├── Reference to "family" but no relation
   ├── References to "support" (undefined)
   ├── Avoidance of regulatory questions
   └── Use of personal friends as intermediaries

4. Source of Funds
   ├── Unclear employment
   ├── Legitimate employment insufficient for amounts
   ├── Recent employment change
   ├── Previous AML violations
   ├── Criminal history
   ├── Government sanctions
   ├── Previous terrorist associations
   └── Refugee/asylum seeker (higher risk)

5. Geographic Indicators
   ├── Origination from high-risk jurisdiction
   ├── Destination to conflict zone
   ├── Multiple country transfers
   ├── Transit through opaque jurisdictions
   ├── Beneficiary in designated TF jurisdiction
   ├── Customer travel to known TF regions
   └── Historical terrorist activity in region
```

### NGO and Charity Concerns

```
HIGHER-RISK NGO CHARACTERISTICS:

Structure:
├── Informal organization
├── Minimal financial controls
├── Unclear beneficial ownership
├── Rapid organizational changes
├── Minimal legitimate activity
└── Recent incorporation

Financial Indicators:
├── Large fund movements
├── Frequent international transfers
├── Transfers to high-risk jurisdictions
├── Significant cash handling
├── Unexplained fund accumulation
├── Funds held rather than disbursed
├── Minimal record keeping
└── Donations exceeding operational costs

Operational Concerns:
├── Limited humanitarian activity
├── Beneficiaries undefined
├── Lack of evidence of actual assistance
├── No verifiable field presence
├── Minimal staff/organization
├── Connections to terrorist groups
├── Fundraising emphasis
└── Opaque money flows

Detection Approach:
├── Assess legitimate activity level
├── Track fund disbursements
├── Verify beneficiary assistance
├── Monitor geographic focus
├── Cross-reference with sanctions lists
├── Assess connections to designated entities
├── Document organizational structure
└── Annual review and reassessment
```

## Fraud and Embezzlement Indicators

### Internal Fraud Red Flags

```
EMPLOYEE EMBEZZLEMENT:

Early Indicators:
├── Override of normal controls
├── Transactions outside normal procedures
├── Transactions during off-hours
├── Use of temporary accounts
├── Adjustments to customer accounts
├── Creation of duplicate/false accounts
├── Voiding of legitimate transactions
├── Circumventing supervisory review
└── Refusal to take vacation

Financial Indicators:
├── Account balances increasing unexplainably
├── Transactions with unusual amounts
├── Round-dollar amounts
├── Transfers to personal accounts
├── Payee frequently changes
├── Transactions to new payees
├── Transactions inconsistent with business
├── Discrepancies in reconciliation
└── Missing documentation

Behavioral Indicators:
├── Unwillingness to delegate
├── Defensive about transactions
├── Resistance to audits
├── Frequent account access (off-hours)
├── Multiple login attempts
├── Access to accounts outside responsibility
└── Resistance to job rotation

Detection Methods:
├── Exception reports (override patterns)
├── Segregation of duties enforcement
├── Transaction monitoring
├── Account reconciliation procedures
├── Audit and examination procedures
├── Whistleblower program
├── Surprise audits
└── System access logging
```

### Check Fraud

```
COMMON CHECK FRAUD SCHEMES:

Forged Checks:
├── Stolen check stock
├── Fabricated account number/routing
├── Counterfeited checks
├── Altered check amounts
├── Unauthorized signatory
└── Fictitious accounts

Red Flags:
├── Check amount inconsistent with account
├── Check payee unusual
├── Check sequence gaps
├── Volume unusual for customer
├── Customer reports lost checks
├── Check stock discrepancy
├── Multiple checks same payee
├── Signature inconsistencies
├── Routing number incorrect
├── Check material quality poor
└── Recipient unknown to customer

Detection Controls:
├── Check verification system
├── Signature verification
├── Routing number validation
├── Account history analysis
├── Volume monitoring
├── Payee analysis
├── Positive pay systems
└── Stop payment processing
```

## Sanctions Evasion Indicators

```
ATTEMPTED SANCTIONS EVASION:

Deceptive Practices:
├── Misrepresenting beneficial owner
├── False beneficiary identification
├── Using nominee/intermediary
├── Misrepresenting transaction purpose
├── Altering/forging documentation
├── Creating false corporate structure
├── Layering through multiple entities
├── Circumventing screening
└── Using opaque jurisdictions

Detection Indicators:
├── Match to sanctions list (exact/fuzzy)
├── Name variation matching
├── DOB/ID matching to designate
├── Entity ownership to designated party
├── Transaction pattern evasion
├── Unusual intermediaries
├── False documentation
├── Claimed exemption without basis
├── Rapid account closure after transaction
├── Customer resistance to verification
└── Beneficial owner refusal to identify

Documentation Analysis:
├── Document authenticity verification
├── Signature analysis
├── Paper/ink/printing verification
├── Seal and notarization review
├── Cross-reference with authorities
├── Beneficial owner chain tracing
└── Corporate structure analysis

Action:
├── Transaction blocking (if appropriate)
├── Account review and potential closure
├── Enhanced monitoring
├── SAR filing
├── Reporting to appropriate authority
├── Documentation retention
└── Senior management notification
```

## High-Risk Jurisdiction Indicators

```
INCREASED AML RISK FROM JURISDICTION:

Characteristics:
├── Weak AML/CFT regime
├── Non-Cooperative Countries (NCCTs) designation
├── FATF Gray List jurisdiction
├── High corruption index
├── Political instability
├── Civil war/conflict
├── Terrorist activity
├── Drug trafficking hub
├── Money laundering prevalence
├── Sanctions-related jurisdiction
├── OFAC-embargoed country
├── Weak financial regulation
├── Limited transparency
├── Beneficial ownership secrecy
└── Weak customer identification

Enhanced Due Diligence Trigger:
├── Customer located in high-risk jurisdiction
├── Beneficial owner in high-risk jurisdiction
├── Transaction destination is high-risk
├── Transaction source is high-risk
├── Customer claims to reside elsewhere
├── Multiple country involvement
├── Complex beneficial ownership
├── Correspondent banking involved
└── Origin of funds unclear

Assessment Actions:
├── Understand business rationale
├── Source of funds verification
├── Enhanced beneficial owner verification
├── Senior management approval
├── Enhanced ongoing monitoring
├── Frequent review and reassessment
├── Consideration of relationship decline
└── Potential SAR filing
```

## Best Practices for Indicator Assessment

1. **Holistic Review** - Consider all factors together, not individual indicators
2. **Customer Profile Baseline** - Understand normal patterns before assessing anomalies
3. **Documentation** - Document reasoning for alert generation and disposition
4. **False Positive Management** - Context matters; reduce alert fatigue
5. **Escalation Procedures** - Clear path to senior review and SAR filing
6. **Continuous Learning** - Update typologies as new schemes emerge
7. **Regulatory Guidance** - Follow FinCEN and international guidance
8. **Testing and Monitoring** - Validate rules quarterly
9. **Feedback Loop** - Use SAR outcomes to refine indicators
10. **Red Flag Awareness** - Ensure staff trained on current indicators
