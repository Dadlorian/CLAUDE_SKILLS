# Lending Systems in Banking

## Lending Overview

### Types of Lending
```
Retail Lending:
├── Personal Loans
├── Auto Loans
├── Mortgages
├── Credit Cards
├── Student Loans
└── Home Equity Lines of Credit

Commercial Lending:
├── Small Business Loans
├── Commercial Real Estate Loans
├── Equipment Financing
├── Line of Credit
├── Term Loans
└── Asset-Based Lending

Corporate Lending:
├── Large Corporate Loans
├── Syndicated Loans
├── Bridge Financing
├── Acquisition Financing
├── Project Financing
└── Structured Finance
```

## Loan Origination System (LOS)

### LOS Components

#### Application Management
```
Features:
├── Application intake (online, branch, phone)
├── Document collection and storage
├── Data validation and completeness checking
├── Application status tracking
├── Communication with borrower
└── Application assignment to processors
```

#### Workflow Management
```
Workflow Steps:
├── Application Submission
├── Initial Review & Completeness
├── Underwriting Assessment
├── Appraisal/Valuation (if secured)
├── Credit Decision
├── Documentation Preparation
├── Funding Authorization
├── Loan Disbursement
├── Post-Closing Follow-up
└── Delivery to Servicing
```

#### Document Management
```
Documents Tracked:
├── Application forms
├── Financial statements
├── Pay stubs and employment verification
├── Tax returns
├── Bank statements
├── Credit reports
├── Appraisals
├── Insurance documents
├── Title documents
├── Disclosure forms
└── Signed agreements
```

### Underwriting Process

#### Underwriting Steps
```
1. Application Review
   ├── Completeness check
   ├── Information validation
   └── Initial eligibility screening

2. Credit Analysis
   ├── Credit score review
   ├── Payment history analysis
   ├── Debt-to-income calculation
   ├── Existing liabilities review
   └── Credit bureau inquiries

3. Income Verification
   ├── W-2 employment verification
   ├── Self-employment income analysis
   ├── Income stability assessment
   ├── Income adequacy for debt service
   └── Rental property income verification

4. Asset Evaluation
   ├── Liquid asset verification
   ├── Investment portfolio review
   ├── Real estate appraisal (if secured)
   ├── Equipment valuation (if applicable)
   └── Net worth calculation

5. Risk Assessment
   ├── Loan-to-value (LTV) ratio
   ├── Debt-to-income (DTI) ratio
   ├── Credit quality score
   ├── Collateral quality
   └── Overall risk rating

6. Compliance Review
   ├── Fair lending compliance
   ├── KYC/AML requirements
   ├── Sanctions screening
   ├── Regulatory requirements
   └── Policy compliance

7. Decision & Approval
   ├── Approval with conditions
   ├── Conditional approval
   ├── Denial with explanation
   └── Appeal process availability
```

## Credit Products

### Personal Loans
```
Characteristics:
├── Amount: $1,000 - $100,000
├── Term: 12-84 months
├── Interest Rate: Secured: 4-8%, Unsecured: 6-15%+
├── Collateral: Unsecured or secured (car, home equity)
├── Purpose: Debt consolidation, home improvement, medical
├── Credit Score Required: 620+
└── Typically: Fixed monthly payments

Underwriting Factors:
├── Credit score (most important)
├── Income and employment stability
├── Debt-to-income ratio
├── Payment history
├── Down payment/collateral
└── Loan purpose
```

### Auto Loans
```
Characteristics:
├── Amount: $5,000 - $150,000
├── Term: 24-84 months (typically 60)
├── Interest Rate: 4-15% depending on credit
├── Collateral: Vehicle financed (first lien)
├── LTV: 80-125% typical (including GAP insurance)
├── Insurance Required: Comprehensive and collision
└── Mileage Limits: Often included in terms

Underwriting:
├── Vehicle value and condition
├── Borrower income and history
├── Down payment amount
├── Vehicle loan-to-value ratio
├── Trade-in valuation (if applicable)
└── Insurance requirements
```

### Mortgages
```
Characteristics:
├── Amount: $50,000 - $5,000,000+
├── Term: 15-30 years
├── Interest Rate: 3-8% depending on credit/market
├── Collateral: Real property (first mortgage lien)
├── LTV: 80% conventional (20% down), can go lower
├── Insurance: Property, title, PMI if <20% down
└── Government Programs: FHA (3.5% down), VA, USDA

Underwriting Requirements:
├── Property appraisal (third-party)
├── Title search and insurance
├── 2-year employment history
├── 2 months bank statements
├── 2 years tax returns
├── Debt-to-income ratio (<43% typical)
├── Minimum credit score (620+)
├── Title insurance policy
└── Survey (depending on property)

Loan Types:
├── Fixed-Rate: Constant rate and payment
├── Adjustable-Rate (ARM): Rate changes after period
├── Hybrid: Fixed for period, then adjustable
├── Interest-Only: Pay interest for period
└── Amortizing: Principal + interest payments
```

### Credit Cards
```
Characteristics:
├── Credit Limit: $500 - $100,000+
├── Interest Rate (APR): 8% - 30%+
├── Grace Period: 21-25 days typical
├── Fees: Annual fee, late fees, foreign transaction
├── Rewards: Cash back, points, travel benefits
└── Unsecured: No collateral required

Credit Card Issuance:
├── Instant decisions on many applications
├── Real-time credit bureau inquiry
├── Automated decision engines
├── Instant approval or denial
├── Credit limit determination
└── Immediate card activation

Cardholder Protections:
├── Fair billing practices (30-day dispute window)
├── Lost/stolen card protection (max $50)
├── Purchase protection
├── Chargeback rights
└── Privacy protections
```

### Home Equity Lines of Credit (HELOC)
```
Characteristics:
├── Amount: Up to 80-90% of home equity
├── Interest Rate: Variable, tied to prime rate
├── Collateral: Second mortgage on home
├── Term: 10-year draw, 20-year repay
├── Flexible Access: Borrow/repay/reborrow
├── No Fixed Payment: Minimum required during draw

Mechanics:
├── Establish credit line on home equity
├── Receive debit card for access
├── Borrow as needed (up to limit)
├── Interest-only payments during draw period
├── Balloon payment at end (or refinance)
└── Rate adjusts with prime rate
```

## Loan Servicing

### Loan Account Management
```
Activities:
├── Payment Processing
│   ├── Receive and post payments
│   ├── Apply to principal and interest
│   ├── Late fee assessment
│   ├── Payment allocation
│   └── Automated payment setup
│
├── Escrow Management
│   ├── Collect taxes and insurance
│   ├── Pay property taxes (on mortgages)
│   ├── Pay insurance premiums
│   ├── Annual escrow reconciliation
│   └── Adjust monthly escrow amounts
│
├── Statement Generation
│   ├── Monthly statements
│   ├── Payoff quotes
│   ├── Annual interest statements (1098)
│   └── Loan document requests
│
├── Customer Service
│   ├── Payment status inquiries
│   ├── Payoff amount calculations
│   ├── Loan modification requests
│   ├── Dispute resolution
│   └── Document requests
│
└── Regulatory Compliance
    ├── Truth in Lending disclosures
    ├── Fair Debt Collection Practices
    ├── Consumer protection regulations
    └── Complaint handling
```

### Delinquency Management
```
Delinquency Stages:

30 Days Past Due:
├── Late notice sent
├── Late fees assessed
├── Credit bureau reporting begins
├── Contact to resolve
└── Opportunity to bring current

60 Days Past Due:
├── Final notice sent
├── Further late fees assessed
├── Increased contact/collection efforts
├── Payment plan options presented
└── Foreclosure process may begin

90+ Days Past Due:
├── Charge-off consideration
├── Lawsuit consideration
├── Collection referral
├── Foreclosure proceedings
└── Loss recognition

Collection Actions:
├── Phone calls and letters
├── Payment plans/forbearance
├── Loan modifications
├── Refinancing
├── Workout agreements
├── Garnishment (legal process)
└── Foreclosure/repossession
```

### Loan Modifications
```
Modification Types:

Rate Modification:
├── Lower interest rate
├── Fixed instead of variable
├── Extend term to lower payment
└── Combine above options

Term Modification:
├── Extend amortization period
├── Result: Lower monthly payment
├── Longer overall repayment
└── More total interest paid

Principal Modification:
├── Reduce principal amount owed
├── Forgive portion of debt
├── Reduce by difference in home value (underwater loans)
└── Result: Deeper affordability improvement
```

## Risk Management in Lending

### Credit Risk
```
Components:
├── Probability of Default (PD)
│   ├── Likelihood borrower won't pay
│   ├── Based on credit score, history
│   ├── Macro-economic factors
│   └── Industry/employment factors
│
├── Loss Given Default (LGD)
│   ├── Amount lost if default occurs
│   ├── Less recovery from collateral
│   ├── Less recovery from guarantor
│   └── Percentage of loan amount
│
└── Exposure at Default (EAD)
    ├── Amount outstanding at default
    ├── Principal + interest accrued
    ├── For lines of credit: Amount drawn
    └── For undrawn facilities: 0% typically
```

### Collateral Management
```
Collateral Types:
├── Real Estate
│   ├── Primary residence (mortgage)
│   ├── Investment property
│   ├── Land
│   └── Commercial property
│
├── Personal Property
│   ├── Vehicles (auto loans)
│   ├── Equipment
│   ├── Inventory
│   └── Accounts receivable
│
├── Securities
│   ├── Stock (margin loans)
│   ├── Bonds
│   ├── Mutual funds
│   └── Investment accounts
│
└── Cash
    ├── Certificates of deposit (CD-secured loans)
    ├── Savings account pledged
    └── Money market account pledged
```

### Loan Loss Reserve
```
Calculation:
Reserve = Loan Balance × Probability of Default × Loss Given Default

Factors:
├── Credit quality ratings
├── Historical default rates
├── Economic conditions
├── Unemployment rates
├── Real estate market conditions
├── Loan characteristics (age, type)
├── Geographic concentration
└── Industry concentration

Accounting Treatment (GAAP):
├── Expected Credit Loss (ECL) model
├── Lifetime losses for certain loans
├── 12-month losses for others
├── Includes macroeconomic factors
└── Adjusts as conditions change
```

## Loan Origination Technology

### Key Technologies
```
Digital Application:
├── Online application portal
├── Mobile application
├── Instant pre-qualification
├── Document upload capability
├── Real-time decision notification
└── Digital signing

Automated Underwriting:
├── Rules-based decision engines
├── Credit bureau integration
├── Automatic income verification
├── Automated collateral valuation
├── Fraud detection scoring
└── Decisioning algorithms

Document Processing:
├── Optical character recognition (OCR)
├── Document classification
├── Automated data extraction
├── Document verification
└── Audit trail maintenance

Loan Origination Systems:
├── Ellie Mae (Encompass)
├── Black Knight (LoanDepot)
├── Fiserv
├── Mortgage Cadence
└── Custom systems
```

## Compliance in Lending

### Fair Lending
```
Prohibited Bases:
├── Race or color
├── Religion
├── National origin
├── Sex
├── Marital status
├── Age
├── Disability
└── Public assistance receipt

Compliance Measures:
├── Fair lending policies
├── Staff training
├── Disparate impact testing
├── Data monitoring
├── Regular audits
├── Applicant flow statistics
└── File reviews
```

### Truth in Lending (TILA)
```
Disclosures Required:
├── Finance charge (dollars and APR)
├── Payment schedule
├── Late payment penalties
├── Prepayment penalties
├── Total of payments
├── Payment terms
├── Right to rescind (for home equity lines)
└── Timing: 3 business days before closing

Loan Estimate (for mortgages):
├── Loan amount
├── Interest rate
├── Monthly payment
├── Estimated taxes and insurance
├── Estimated closing costs
└── Provided within 3 days of application

Closing Disclosure (for mortgages):
├── Final loan terms
├── Final closing costs
├── Final payment amounts
├── Provided 3 business days before closing
└── Must match Loan Estimate closely
```

## Conclusion
Modern lending systems combine sophisticated credit analysis, digital application platforms, and comprehensive servicing operations. Banks must balance loan growth with sound credit risk management, maintain regulatory compliance, and provide excellent customer service throughout the loan lifecycle.
