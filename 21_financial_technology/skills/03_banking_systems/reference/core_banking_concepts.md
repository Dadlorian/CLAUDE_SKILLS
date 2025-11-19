# Core Banking Concepts

## Overview
Core banking refers to the essential business activities and systems that banks use to conduct their primary operations. A core banking system is the backbone technology that supports account management, payments, lending, and other fundamental banking services.

## Banking Services Model

### Retail Banking
- **Personal Banking**: Individual customer accounts and services
- **Credit Products**: Consumer loans, mortgages, credit cards
- **Deposit Products**: Savings accounts, current accounts, CDs
- **Payments**: Transfers, bill payments, ATM withdrawals
- **Wealth Management**: Basic investment products, insurance

### Corporate Banking
- **Cash Management**: Liquidity management, treasury services
- **Trade Finance**: Letters of credit, import/export financing
- **Lending**: Corporate loans, revolving credit facilities
- **Payments**: Wholesale payments, international transfers
- **Advisory**: Financial advisory, M&A support

### Investment Banking
- **Securities**: IPOs, equity offerings, debt issuance
- **Mergers & Acquisitions**: Transaction advisory, valuation
- **Trading**: Equities, bonds, commodities trading
- **Underwriting**: Securities underwriting, guarantee services
- **Capital Markets**: Market making, trading infrastructure

## Account Management

### Account Types
```
Current Account (Checking)
├── Primary account for frequent transactions
├── No interest earned
├── Unlimited deposits/withdrawals
└── Check book and debit card provided

Savings Account
├── For long-term savings
├── Earns interest on balance
├── Limited monthly withdrawals (may apply)
└── Subject to minimum balance requirements

Fixed Deposit Account
├── Fixed-term investment product
├── Fixed interest rate
├── Predetermined maturity date
└── Penalty for early withdrawal

Recurring Deposit Account
├── Regular deposit schedule
├── Fixed installments
├── Maturity at specified term
└── Interest compounding
```

### Account Lifecycle

```
Account Opening
    ↓
KYC Verification
    ↓
Account Activation
    ↓
Active Use
    ├─ Deposits
    ├─ Withdrawals
    ├─ Transfers
    └─ Interest Accrual
    ↓
Account Maintenance
    ├─ Fee Charging
    ├─ Interest Crediting
    └─ Reconciliation
    ↓
Account Closure/Dormancy
    └─ Final Reconciliation
```

### Account Hierarchy
- **Customer**: Entity owning one or more accounts
- **Account**: Customer's financial container
- **Sub-Accounts**: Internal accounting sub-divisions
- **GL Accounts**: General ledger accounts for accounting
- **Cost Centers**: For internal profitability tracking

## Double-Entry Accounting

### Fundamental Principle
Every financial transaction affects two accounts:
- **Debit**: Decrease in liabilities, increase in assets
- **Credit**: Increase in liabilities, decrease in assets
- **Always Balanced**: Total Debits = Total Credits

### Accounting Equation
```
Assets = Liabilities + Equity
```

### Transaction Examples

#### Customer Deposit
```
Debit: Cash/Vault (Asset)         +$1,000
Credit: Customer Account (Liability) +$1,000
        (Bank owes customer this amount)
```

#### Customer Withdrawal
```
Debit: Customer Account (Liability)   -$500
Credit: Cash/Vault (Asset)            -$500
```

#### Interest Earned
```
Debit: Accrued Interest Receivable    +$50
Credit: Interest Income Account       +$50
```

#### Fee Charging
```
Debit: Fee Income                     +$10
Credit: Customer Account (Liability)  -$10
        (Reduction of bank's liability)
```

### Account Classifications

#### Assets (Increase with Debit)
- Cash and cash equivalents
- Loans to customers
- Investment securities
- Fixed assets
- Other assets

#### Liabilities (Increase with Credit)
- Customer deposits
- Borrowings from other banks
- Bonds issued
- Accounts payable
- Other liabilities

#### Equity (Increase with Credit)
- Share capital
- Retained earnings
- Reserves
- Profit/loss

## Transaction Processing

### Transaction States
```
INITIATED
    │ Validation
    ↓
PENDING
    │ Processing
    ↓
POSTED (Successful) or FAILED (Unsuccessful)
    │
    ├─→ POSTED
    │       │ Settlement
    │       ↓
    │   SETTLED
    │
    └─→ FAILED
            │ Reversal/Correction
            ↓
        REVERSED or CORRECTED
```

### Transaction Flow
1. **Initiation**: Customer initiates transaction (online, ATM, branch)
2. **Validation**: Check account status, sufficient balance, limits
3. **Authorization**: Approve transaction based on rules and fraud checks
4. **Processing**: Create ledger entries, update balances
5. **Settlement**: Complete payment to receiving bank/account
6. **Confirmation**: Notify customer of transaction status

### Transaction Components
- **Amount**: Transaction value
- **Currency**: Transaction currency
- **Account**: Source and destination accounts
- **Reference**: Unique transaction identifier
- **Timestamp**: Exact transaction time
- **Status**: Current transaction state
- **Metadata**: Additional context and tracking

## Balance Management

### Balance Types

#### Ledger Balance (Book Balance)
- Balance after all posted transactions
- Updated after each transaction
- Used for transaction processing
- May include pending items

#### Available Balance
- Amount available for withdrawal/transfer
- Excludes holds and pending items
- Updated in real-time
- Affects transaction approval

#### Current Balance
- Current point-in-time balance
- Includes all transactions up to now
- Used for statement reporting
- May differ from available balance

### Multi-Currency Balances
```
Balances in different currencies:
- USD Balance: $10,000
- EUR Balance: €5,000
- GBP Balance: £3,000

All converted to reporting currency:
- Reporting Currency: USD
- USD: $10,000
- EUR converted: €5,000 × 1.10 = $5,500
- GBP converted: £3,000 × 1.27 = $3,810
- Total: $19,310
```

## Interest Management

### Interest Calculation

#### Simple Interest
```
Interest = Principal × Rate × Time
Interest = $10,000 × 5% × 1 year = $500
```

#### Compound Interest
```
Amount = Principal × (1 + Rate)^Time
Amount = $10,000 × (1.05)^1 = $10,500
Interest = $500
```

### Interest Accrual Process
1. **Daily Accrual**: Calculate daily interest on balance
2. **Accrual Entry**: Create accrual journal entries
3. **Monthly Crediting**: Credit interest to customer account
4. **Adjustments**: Handle balance changes and corrections
5. **Tax Reporting**: Track for 1099 reporting

### Interest Scenarios

#### Savings Account Interest
```
Opening Balance: $10,000
Rate: 0.5% annual, compounded daily
Days in period: 30

Daily Interest = $10,000 × 0.5% ÷ 365 = $0.137
Monthly Accrued = $0.137 × 30 = $4.11
New Balance = $10,004.11
```

#### Loan Interest
```
Loan Amount: $100,000
Rate: 5% annual
Term: 5 years (60 months)

Monthly Payment = $100,000 × [0.05/12 × (1 + 0.05/12)^60] / [(1 + 0.05/12)^60 - 1]
Monthly Payment ≈ $1,887.12

Total Interest Paid ≈ $13,227.20
```

## Fees and Charges

### Fee Types

#### Account Fees
- Monthly maintenance fee: $10-15
- Minimum balance fee: If balance < $X
- Inactivity fee: For dormant accounts

#### Transaction Fees
- Wire transfer fee: $15-30
- ACH fee: $1-5
- Check printing fee: $10-20
- Card replacement fee: $5-10

#### Overdraft Fees
- Insufficient fund fee: $30-35
- Overdraft interest: Higher rate than loan rate
- Overdraft limit: Up to $X

### Fee Calculation and Charging
```
Fee Application Rules:
1. Fee is initiated when condition met
2. Fee amount calculated based on rule
3. Debit entry to Fee Income account
4. Credit entry to Customer Liability account
5. Customer balance reduced immediately
6. Fee reversal if customer requests
```

## Regulatory Compliance Foundations

### KYC (Know Your Customer)
- Customer identification verification
- Address verification
- Source of funds verification
- Beneficial ownership identification
- Risk assessment and categorization

### AML (Anti-Money Laundering)
- Transaction monitoring
- Suspicious activity detection
- Sanctions screening
- Suspicious activity reporting (SAR)
- Currency transaction reporting (CTR)

### Data Protection
- Customer information security
- Access controls and logging
- Encryption and data masking
- Retention policies and disposal
- Privacy rights and requests

### Regulatory Reporting
- Daily regulatory reports
- Monthly compliance reviews
- Annual compliance certifications
- Regulatory audits and examinations
- Exception handling and escalation

## Banking Ratios and Metrics

### Capital Ratios (Basel III)
```
Tier 1 Ratio = Tier 1 Capital / Risk-Weighted Assets ≥ 8.5%
Total Ratio = (Tier 1 + Tier 2 Capital) / Risk-Weighted Assets ≥ 10.5%
```

### Liquidity Ratios
```
Liquidity Coverage Ratio (LCR) = High-Quality Assets / Expected Outflows ≥ 100%
Net Stable Funding Ratio (NSFR) = Available Stable Funding / Required Stable Funding ≥ 100%
```

### Asset Quality Ratios
```
Non-Performing Loan Ratio = NPLs / Total Loans
Loan Loss Reserve Ratio = Loan Loss Reserves / NPLs
```

### Profitability Ratios
```
Return on Assets (ROA) = Net Income / Total Assets
Return on Equity (ROE) = Net Income / Equity
Net Interest Margin (NIM) = (Interest Income - Interest Expense) / Average Assets
```

## Core Banking System Functions

### Primary Functions
1. **Account Management**: Create, maintain, close customer accounts
2. **Ledger Management**: Maintain GL and customer ledgers
3. **Transaction Processing**: Initiate, process, settle transactions
4. **Payment Processing**: Handle various payment channels
5. **Interest Management**: Calculate and credit interest
6. **Fee Management**: Calculate and charge fees
7. **Reconciliation**: Automated and manual reconciliation
8. **Reporting**: Generate statements and regulatory reports
9. **Security**: Authentication, authorization, audit logging
10. **Compliance**: KYC, AML, regulatory compliance

### Supporting Functions
- Customer information management (CIF)
- Product management and pricing
- Limits and controls management
- Risk management and fraud detection
- Data management and archival
- Integration with payment networks
- Mobile and online banking
- Call center and branch integration

## Modern Banking Innovations

### Digital Banking
- Online banking platforms
- Mobile banking applications
- API-based banking services
- Automated account opening (eOA)
- Video KYC

### Neobanking
- Cloud-native architectures
- API-first design
- Instant account opening
- Streamlined user experience
- Low-cost operations

### Open Banking
- API standardization (PSD2, FAPI)
- Third-party integrations
- Account aggregation
- Payment initiation services
- Data sharing platforms

### Real-Time Payments
- Instant fund transfers
- 24/7 operation
- Real-time balance updates
- Reduced settlement risk
- Lower costs

## Conclusion
Core banking concepts form the foundation of all banking operations. Understanding account management, double-entry accounting, transaction processing, and regulatory requirements is essential for building modern banking systems.
