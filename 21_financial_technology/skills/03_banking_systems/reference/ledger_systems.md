# Ledger Systems in Banking

## Ledger Fundamentals

### What is a Ledger?
A ledger is a permanent record of all financial transactions organized by account. It forms the foundation of financial record-keeping and is essential for:
- **Accounting**: Recording financial transactions
- **Reporting**: Generating financial statements
- **Compliance**: Maintaining regulatory audit trails
- **Reconciliation**: Matching transactions to external sources
- **Analysis**: Understanding financial performance

### Types of Ledgers

#### General Ledger (GL)
- **Purpose**: Master record of all financial transactions
- **Structure**: Organized by account (assets, liabilities, equity, income, expenses)
- **Scope**: Company-wide financial summary
- **Users**: Accounting department, management, regulators
- **Example Accounts**:
  ```
  1000 - Cash and Cash Equivalents
  1100 - Customer Deposit Accounts
  2000 - Liabilities
  2100 - Customer Deposits Payable
  3000 - Equity
  3100 - Share Capital
  ```

#### Sub-Ledgers
- **Customer Ledgers**: Individual customer account balances
- **Product Ledgers**: By product type (savings, checking, loans)
- **Cost Center Ledgers**: By business unit or cost center
- **Currency Ledgers**: Separate ledgers per currency
- **Branch Ledgers**: By physical location

### Ledger Entry Components
```
Account Number:     1100 (Customer Checking Account)
Customer ID:        CUST-12345
Transaction Date:   2025-11-19
Transaction Type:   Deposit
Debit Amount:       $1,000.00
Credit Amount:      $0.00
Balance Before:     $5,000.00
Balance After:      $6,000.00
Description:        Cash deposit via teller
Reference:          DEP-2025-11-19-001
```

## Double-Entry Accounting Ledger

### Core Principle
Every transaction has two entries:
- One account is **debited** (increased)
- One account is **credited** (decreased)
- Total debits always equal total credits

### Debits and Credits

#### For Assets (Increase with Debits)
```
Debit   = Increase
Credit  = Decrease

Example: Cash account
Debit:   +$100 (more cash)
Credit:  -$50  (less cash)
```

#### For Liabilities (Increase with Credits)
```
Debit   = Decrease
Credit  = Increase

Example: Customer Deposit Payable
Credit:  +$100 (more owed to customer)
Debit:   -$50  (less owed to customer)
```

#### For Equity (Increase with Credits)
```
Debit   = Decrease
Credit  = Increase

Example: Retained Earnings
Credit:  +$50,000 (profit added)
Debit:   -$5,000  (loss deducted)
```

### Trial Balance
A listing of all GL accounts with their balances to verify:
- All debits = all credits
- No accounts are missing
- No transcription errors

```
General Ledger Trial Balance
as of November 19, 2025

Account                          Debit        Credit
Cash and Cash Equiv.          $10,000,000
Customer Deposits                          $50,000,000
Loans to Customers             $40,000,000
Liabilities                                 $8,000,000
Equity                                      $2,000,000
Income Account                              $100,000
Expense Account                 $1,000,000

Total                          $51,000,000  $51,000,000  ✓ Balanced
```

## Customer Ledger System

### Customer Account Ledger
A detailed transaction history for each customer account

```
Customer ID: CUST-00123
Account: Checking Account 4567
Date        Description      Debit    Credit   Balance
2025-11-01  Opening Balance                    $1,000.00
2025-11-02  Deposit                $500.00    $1,500.00
2025-11-03  Withdrawal      $200.00           $1,300.00
2025-11-04  Direct Debit    $150.00           $1,150.00
2025-11-05  Interest Credit           $2.50   $1,152.50
2025-11-06  Fee Charge      $10.00            $1,142.50
```

### Account Hierarchy in Ledger

```
Bank
├── Retail Banking
│   ├── Savings Accounts
│   │   ├── Customer 001 Account
│   │   ├── Customer 002 Account
│   │   └── ...
│   └── Checking Accounts
│       ├── Customer 003 Account
│       └── ...
└── Corporate Banking
    ├── Business Account
    └── ...
```

### Account Status Tracking
```
Account Ledger Entry with Status:
Account Number:    4567
Status:            Active
Balance:           $1,500.00
Available Balance: $1,450.00
Holds:             $50.00 (pending check)
Last Activity:     2025-11-20 14:30:00 UTC
```

## Multi-Currency Ledger System

### Currency Management
```
Customer Account in Multiple Currencies:

USD Account
├── Debit: $1,000
└── Balance: $5,000

EUR Account
├── Debit: €800
└── Balance: €3,000

GBP Account
├── Debit: £600
└── Balance: £1,500
```

### Currency Conversion Entries
```
Transaction: Convert $1,000 USD to EUR at rate 1.10

Debit:   EUR Account (Asset)          €910.00
Credit:  USD Account (Asset)         ($1,000.00)
Debit:   FX Loss/Gain Account          $90.00 cost
```

### Consolidated Currency View
```
Account Balance Report - Customer 001

USD Balance:                          $10,000.00
EUR Balance: €5,000 @ 1.10 = $5,500.00
GBP Balance: £3,000 @ 1.27 = $3,810.00

Total in USD:                        $19,310.00
```

## Transaction Ledger

### Transaction Record
```
Transaction ID:      TRX-2025-11-20-00001
Account Number:      4567
Transaction Type:    Transfer
Amount:              $500.00
Currency:            USD
From Account:        4567 (Checking)
To Account:          4568 (Savings)
Status:              Posted
Timestamp:           2025-11-20 10:30:00.123 UTC
Processing Date:     2025-11-20
Settlement Date:     2025-11-20
Reference:           "Transfer to savings"
Ledger Entry:
  Debit:  Savings Account (4568)     $500.00
  Credit: Checking Account (4567)    $500.00
```

## Reconciliation Ledger

### Daily Reconciliation
```
Beginning Balance (GL):            $1,000,000.00
+ Deposits Posted:                 +$500,000.00
- Withdrawals Posted:              -$300,000.00
- Checks Cleared:                  -$100,000.00
+ Interest Earned:                 +$2,000.00
- Fees and Charges:                -$5,000.00

Ending Balance (GL):               $1,097,000.00

External Bank Statement:           $1,097,000.00

Difference:                        $0.00 ✓ Reconciled
```

### Exception Handling
```
Outstanding Items:
- Check #1234 (pending)          -$150.00
- Deposit in transit (pending)   +$200.00
- Bank fee not yet posted        -$25.00

Adjusted Bank Balance:           $1,097,025.00
GL Balance:                      $1,097,000.00
Difference to Investigate:       $25.00
```

## Account Classification Ledger

### Chart of Accounts Structure
```
Assets (1000-1999)
├── 1000-1099: Cash and Equivalents
├── 1100-1199: Customer Accounts
├── 1200-1299: Loans Receivable
└── 1300-1399: Investments

Liabilities (2000-2999)
├── 2000-2099: Customer Deposits
├── 2100-2199: Borrowings
└── 2200-2299: Other Liabilities

Equity (3000-3999)
├── 3000-3099: Share Capital
└── 3100-3199: Retained Earnings

Income (4000-4999)
├── 4000-4099: Interest Income
├── 4100-4199: Fee Income
└── 4200-4299: Other Income

Expenses (5000-5999)
├── 5000-5099: Interest Expense
├── 5100-5199: Operating Expenses
└── 5200-5299: Loan Loss Provisions
```

## Batch Ledger Processing

### End-of-Day Batch Process
```
1. Transaction Capture
   └─ Collect all transactions from day

2. Validation and Authorization
   └─ Verify all transactions are valid

3. Ledger Posting
   ├─ Post transactions to GL
   ├─ Post transactions to customer ledgers
   └─ Post transactions to sub-ledgers

4. Balance Calculation
   ├─ Calculate account balances
   ├─ Calculate available balances
   └─ Calculate multi-currency balances

5. Interest Calculation
   ├─ Calculate daily interest accruals
   └─ Post to ledger

6. Fee Charging
   ├─ Identify fee-triggering events
   ├─ Calculate fees
   └─ Post to ledger

7. Reconciliation
   ├─ Reconcile GL to subledgers
   ├─ Identify exceptions
   └─ Create exception reports

8. Reporting
   ├─ Generate ledger reports
   ├─ Generate customer statements
   └─ Generate regulatory reports
```

## Ledger Queries and Reporting

### Common Ledger Queries

#### Account Balance Query
```sql
SELECT
  account_number,
  customer_name,
  SUM(CASE WHEN entry_type = 'DEBIT' THEN amount ELSE 0 END) -
  SUM(CASE WHEN entry_type = 'CREDIT' THEN amount ELSE 0 END) as balance
FROM ledger_entries
WHERE account_id = 4567
  AND transaction_date <= CURRENT_DATE
GROUP BY account_number, customer_name
```

#### Daily Transaction Report
```sql
SELECT
  transaction_id,
  account_number,
  transaction_type,
  amount,
  transaction_date,
  status
FROM ledger_entries
WHERE transaction_date = CURRENT_DATE
ORDER BY transaction_id
```

#### Ledger Balance Report
```sql
SELECT
  gl_account,
  account_description,
  SUM(debit_amount) as total_debits,
  SUM(credit_amount) as total_credits,
  SUM(debit_amount) - SUM(credit_amount) as balance
FROM general_ledger
WHERE posting_date <= CURRENT_DATE
GROUP BY gl_account, account_description
ORDER BY gl_account
```

## Ledger Controls and Auditing

### Ledger Controls
1. **Authorization Controls**: Only authorized users can post entries
2. **Batch Balancing**: All batches must balance before posting
3. **Segregation of Duties**: Entry, authorization, and reconciliation separated
4. **Approval Workflows**: Higher amounts require additional approvals
5. **System Controls**: Invalid entries rejected automatically

### Audit Trail
```
Entry ID: LE-0001234
GL Account: 1100 - Checking Accounts
Amount: $1,000.00
Direction: Debit
Entered By: teller_001 (2025-11-20 10:30:00 UTC)
Approved By: supervisor_002 (2025-11-20 10:32:00 UTC)
Posted By: batch_processor (2025-11-20 23:45:00 UTC)
Modified By: None
Audit Status: Verified
```

### Compliance Considerations
- **Immutable Records**: Posted entries cannot be altered
- **Correction Process**: Errors corrected via reversal + correction entry
- **Retention**: Records retained per regulatory requirements (7-10 years)
- **Access Logging**: All access to ledger logged and audited
- **Regulatory Submissions**: Ledger reports support regulatory filings

## Modern Ledger Technologies

### Cloud-Based Ledger Systems
- Real-time posting and balance updates
- Multi-tenant support for efficiency
- Automatic reconciliation
- Real-time reporting and analytics
- Disaster recovery and business continuity

### Blockchain Ledger Systems
- Distributed ledger technology (DLT)
- Immutable transaction records
- Smart contract-based automation
- Real-time settlement
- Transparency and auditability

### Real-Time Ledger Systems
- Immediate transaction posting
- Live balance updates
- Instant reconciliation
- Real-time regulatory reporting
- No batch processing delays

## Conclusion
Ledger systems are the backbone of banking operations, maintaining accurate financial records and enabling compliance, reporting, and operational management. Modern banking systems use sophisticated ledger technologies to ensure accuracy, security, and regulatory compliance.
