# Credit Scoring and Risk Assessment

## Credit Scoring Overview

### What is a Credit Score?
A credit score is a numerical rating (typically 300-850) that summarizes creditworthiness based on:
- **Payment history** (35%)
- **Amounts owed** (30%)
- **Length of credit history** (15%)
- **Credit mix** (10%)
- **New credit** (10%)

### Purpose of Credit Scores
```
Credit Scoring Used For:
├── Lending Decisions
│   ├── Loan approval/denial
│   ├── Credit limit determination
│   └── Interest rate pricing
│
├── Risk Assessment
│   ├── Default probability estimation
│   ├── Portfolio risk monitoring
│   └── Concentration risk analysis
│
├── Collections
│   ├── Delinquency prediction
│   ├── Loss severity estimation
│   └── Collections strategy prioritization
│
└── Marketing
    ├── Customer targeting
    ├── Pre-approved offers
    └── Solicitation strategies
```

## FICO Score Model

### Score Components

#### 1. Payment History (35%)
```
Factors:
├── On-time payments (most important)
├── Payment recency (recent payments more important)
├── Delinquency frequency (30, 60, 90+ days late)
├── Charge-offs and collections
├── Bankruptcies and judgments
├── Frequency of late payments
├── Severity of delinquency
└── Time since delinquency

Impact:
├── Single late payment: -50-100 points
├── Charge-off: -100-150 points
├── Collection: -100-150 points
├── Bankruptcy: -130-200 points
└── Recent payment restores score faster
```

#### 2. Amounts Owed (30%)
```
Factors:
├── Credit utilization ratio (amount used / credit limit)
├── Balances on different account types
├── Amount of installment loans remaining
├── Proportion of credit lines with balances
├── Recent debt inquiries
└── Total amount owed across all accounts

Impact:
├── High utilization (>70%): Reduces score
├── Low utilization (<30%): Improves score
├── Zero balances: May slightly lower score
├── Recent balance increases: Reduces score
└── Strategic paydown: Improves score

Example:
├── Credit limit: $10,000
├── Balance: $3,000
├── Utilization: 30% ✓ Good
├── Balance: $8,000
├── Utilization: 80% ✗ Bad (may reduce score by 50+ points)
```

#### 3. Length of Credit History (15%)
```
Factors:
├── Age of oldest account
├── Age of newest account
├── Average age of all accounts
├── Time since accounts became active
├── Time since last account activity

Impact:
├── Older accounts: Positive
├── Longer history: Positive
├── New accounts: Slightly negative
├── Opening many accounts quickly: Negative
└── Closing old accounts: Can hurt score
```

#### 4. Credit Mix (10%)
```
Account Types:
├── Revolving Credit
│   ├── Credit cards
│   ├── Home equity lines of credit
│   ├── Flexible access to credit
│   └── Balance can change
│
├── Installment Loans
│   ├── Auto loans
│   ├── Personal loans
│   ├── Fixed payments
│   └── Fixed term
│
└── Other Accounts
    ├── Mortgage accounts
    ├── Finance company loans
    └── Student loans

Impact:
├── Mix of account types: Positive
├── Only credit cards: May lower score
├── Only installment loans: May lower score
├── Healthy mix: Improves score
└── Actively managing different types: Positive
```

#### 5. New Credit (10%)
```
Factors:
├── Number of recent inquiries (hard pulls)
├── Number of new accounts opened
├── Time since new accounts opened
├── Recent rate shopping (multiple inquiries in short time)
└── Inquiries that remain on report

Impact:
├── Hard inquiry: -5-10 points
├── New account: -10-45 points (temporary)
├── Multiple inquiries in 45 days: Counted as one (for rate shopping)
├── Score recovery: Improves over 3-6 months
└── Multiple inquiries in short time: Significant negative impact
```

## Alternative Credit Scoring Models

### VantageScore
```
Characteristics:
├── Alternative to FICO
├── Created by Equifax, Experian, TransUnion
├── Scores: 300-850 (like FICO)
├── Weight factors differently than FICO
├── More predictive of credit risk (in some studies)

Factor Weights:
├── Payment history: 40% (higher than FICO)
├── Age and type of credit: 21%
├── Percent of credit used: 20%
├── Total balances: 11%
├── Recent credit behavior: 8%

Advantages:
├── Uses alternative data (rent, utilities, phone)
├── Thinner file friendlier
├── Faster score updates
└── More transparent weighting

Disadvantages:
├── Less widely used than FICO
├── Different scoring methodology
├── Conversion table needed to compare
└── Not used by many traditional lenders
```

### Medical/Alternative Scores
```
Thin File Scoring:
├── Used for customers with limited credit history
├── Incorporates non-traditional data:
│   ├── Rent payment history
│   ├── Utility bill payments
│   ├── Phone/mobile payments
│   ├── Insurance payment history
│   └── Employment history
│
├── Lenders:
│   ├── Online lenders
│   ├── Credit unions
│   ├── Community banks
│   └── Non-prime lenders
│
└── Challenges:
    ├── Data accuracy issues
    ├── Privacy concerns
    ├── Regulatory scrutiny
    └── Model stability
```

### Proprietary Scoring Models
```
Bank-Specific Models:
├── Based on bank's own historical data
├── Incorporates:
│   ├── Historical default rates
│   ├── Bank's own customer behavior
│   ├── Internal data and patterns
│   └── Bank-specific risk factors
│
├── Advantages:
│   ├── More relevant to bank's portfolio
│   ├── Can be more predictive
│   ├── Account for bank-specific factors
│   └── Competitive advantage
│
└── Disadvantages:
    ├── Expensive to develop and maintain
    ├── Requires significant historical data
    ├── Model risk and validation challenges
    └── Regulatory examination
```

## Credit Bureau Data

### The Three Major Credit Bureaus
```
Equifax, Experian, TransUnion:
├── Collect credit information
├── Maintain consumer credit files
├── Calculate credit scores
├── Provide reports to creditors
├── Provide reports to consumers (once/year free)
└── Respond to disputes

Information Collected:
├── Credit accounts (open and closed)
├── Payment history
├── Inquiries
├── Public records (bankruptcies, liens)
├── Collections accounts
├── Tax liens
└── Judgments
```

### Credit Report Structure
```
Consumer Credit Report Contents:

1. Personal Information
   ├── Name and aliases
   ├── Address (current and previous)
   ├── Phone number
   ├── Social Security Number
   ├── Employment history
   ├── Date of birth
   └── Citizenship

2. Trade Lines (Account Information)
   ├── Creditor name
   ├── Account number
   ├── Account type (credit card, auto loan, mortgage)
   ├── Account status (open, closed, paid off)
   ├── Credit limit / loan amount
   ├── Current balance
   ├── Monthly payment
   ├── Payment history (last 24-84 months)
   ├── Date opened
   ├── Date of last activity
   └── Days past due (if delinquent)

3. Inquiries
   ├── Hard inquiries (for credit application)
   ├── Date of inquiry
   ├── Creditor requesting
   ├── Soft inquiries (for marketing, account review)
   └── Remain for 2 years

4. Public Records
   ├── Bankruptcies (7-10 years)
   ├── Liens and judgments (7 years)
   ├── Tax liens (10 years)
   ├── Collections accounts (7 years)
   └── Court records

5. Collections Information
   ├── Collection agency name
   ├── Original creditor
   ├── Amount owed
   ├── Date of charge-off/collection
   └── Collection status
```

## Scoring Models and Algorithms

### Logistic Regression Models
```
Simple Model:
├── Probability of default = 1 / (1 + e^-X)
├── Where X = intercept + (weights × variables)
├── Produces probability between 0 and 1
├── Interpretable coefficients
└── Widely used in banking

Advantages:
├── Simple and interpretable
├── Fast to compute
├── Regulatory acceptance
├── Stable and robust
└── Well-understood by risk officers

Disadvantages:
├── Limited to linear relationships
├── Doesn't capture interactions well
├── Requires variable transformation
└── May not be optimally predictive
```

### Machine Learning Models
```
Decision Trees:
├── Recursive partitioning of data
├── Creates if-then rules
├── Interpretable decision paths
├── Handles non-linear relationships
└── Can overfit without pruning

Random Forests:
├── Multiple decision trees
├── Averages predictions
├── Handles non-linearity
├── More predictive than single trees
├── Less interpretable

Gradient Boosting:
├── Sequential tree building
├── Each tree corrects previous errors
├── Very predictive
├── Requires careful tuning
└── Black box nature raises concerns

Neural Networks:
├── Multiple layers of neurons
├── Very flexible
├── Can learn complex patterns
├── Regulatory concerns (explainability)
└── Risk of overfitting
```

### Model Governance
```
Requirements:
├── Model documentation
├── Variable justification
├── Model development data
├── Validation methodology
├── Performance metrics
├── Monitoring frequency
├── Retraining schedule
├── Challenger models
├── Backtesting results
├── Bias and discrimination testing
├── Model risks and limitations
└── Escalation procedures
```

## Scoring for Lending Decisions

### Risk-Based Pricing
```
Concept:
├── Loan price (interest rate) based on risk
├── Higher risk → Higher interest rate
├── Lower risk → Lower interest rate
└── Expected profit = (Interest Rate - Cost of Funds) × Loan Amount

Pricing Tiers:
├── Tier 1 (Score 760+): 4.5% APR, $0 fees
├── Tier 2 (Score 700-759): 6.0% APR, $100 fee
├── Tier 3 (Score 650-699): 8.5% APR, $250 fee
├── Tier 4 (Score 600-649): 11.0% APR, $500 fee
└── Below 600: Decline or specialty product
```

### Credit Limit Determination
```
Formula:
Credit Limit = Min(Approved Amount, Collateral Value, Bank Policy Limit)

Factors:
├── Credit score (strong predictor)
├── Income and debt-to-income ratio
├── Payment history
├── Length of credit history
├── Existing credit with bank
├── Request amount
├── Collateral value (if secured)
├── Bank risk appetite
└── Market conditions

Examples:
├── Score 750+, Income $100k: Up to $25,000
├── Score 700, Income $100k: Up to $15,000
├── Score 650, Income $100k: Up to $8,000
└── Score 600, Income $100k: Up to $3,000
```

## Compliance and Fair Lending

### Adverse Action Notices
```
Required When:
├── Loan application denied
├── Credit limit reduced
├── Interest rate increased above disclosed
├── Unfavorable terms offered compared to approved applicants

Notice Must Include:
├── Statement of adverse action taken
├── Name of credit bureau providing report
├── Right to free credit report
├── Right to dispute accuracy of report
├── Explanation of score used (if credit scoring used)
├── Key factors in decision (top 4 factors)
└── Instructions for disputing
```

### Discriminatory Scoring Issues
```
Concerns:
├── Score may proxy for protected characteristics
├── Disparate impact on protected groups
├── Model development data bias
├── Missing data bias
├── Variable selection bias
└── Threshold setting bias

Testing Requirements:
├── Disparate impact analysis
├── Adverse effect testing
├── Sensitivity analysis
├── Model explainability
├── Regular monitoring and revalidation
└── Bias mitigation strategies
```

### Model Validation
```
Ongoing Requirements:
├── Annual validation
├── Backtesting (actual vs predicted defaults)
├── Benchmark comparisons
├── Stability testing
├── Segment performance
├── Population shift monitoring
├── Variable performance
├── Discrimination testing
├── Documentation review
└── Challenge by risk management
```

## Credit Scoring Best Practices

### Score Monitoring
```
Portfolio Management:
├── Track average score over time
├── Monitor score distribution
├── Identify trends
├── Compare to benchmarks
├── Score migration analysis
└── Early warning indicators
```

### Score Improvement
```
Customer Education:
├── Payment history importance
├── Credit utilization advice
├── Age of credit recommendations
├── Dispute resolution process
├── Score monitoring tools
├── Financial literacy programs
└── Relationship building
```

## Conclusion
Credit scoring is central to modern lending, enabling fair, consistent risk assessment across millions of consumers. Both FICO and alternative models use predictive analytics to estimate default probability, which drives lending decisions, pricing, and risk management. Proper governance and fair lending compliance are essential to ensure scores are accurate, fair, and legally defensible.
