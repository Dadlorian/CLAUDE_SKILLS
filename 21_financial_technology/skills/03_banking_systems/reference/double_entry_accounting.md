# Double-Entry Accounting in Banking

## Fundamental Principles

### The Accounting Equation
```
ASSETS = LIABILITIES + EQUITY

Where:
- Assets: Resources owned by the bank
- Liabilities: Obligations of the bank
- Equity: Owner's interest in assets after liabilities paid
```

### The Double-Entry Rule
Every transaction must be recorded in at least two accounts, maintaining balance:
- **Debit** one account (increase or decrease depending on account type)
- **Credit** another account (opposite effect)
- **Total Debits = Total Credits** always

## Account Types and Debit/Credit Rules

### Assets (Accounts: 1000-1999)
```
Increase   → Debit
Decrease   → Credit
Normal Balance: Debit
```

**Examples:**
- Cash account (debit increases cash)
- Loans to customers (debit increases loans)
- Investment securities (debit increases securities)
- Equipment and fixed assets (debit increases fixed assets)

### Liabilities (Accounts: 2000-2999)
```
Increase   → Credit
Decrease   → Debit
Normal Balance: Credit
```

**Examples:**
- Customer deposits (credit increases deposits owed)
- Borrowings from other banks (credit increases borrowing)
- Bonds issued (credit increases bonds payable)
- Accounts payable (credit increases payables)

### Equity (Accounts: 3000-3999)
```
Increase   → Credit
Decrease   → Debit
Normal Balance: Credit
```

**Examples:**
- Share capital (credit increases share capital)
- Retained earnings (credit increases earnings)
- Common stock (credit increases stock)
- Reserves (credit increases reserves)

### Income (Accounts: 4000-4999)
```
Increase   → Credit
Decrease   → Debit
Normal Balance: Credit
```

**Examples:**
- Interest income (credit increases income)
- Fee income (credit increases income)
- Investment gains (credit increases gains)
- Service charges (credit increases income)

### Expenses (Accounts: 5000-5999)
```
Increase   → Debit
Decrease   → Credit
Normal Balance: Debit
```

**Examples:**
- Interest expense (debit increases expense)
- Salaries and wages (debit increases expense)
- Loan loss provisions (debit increases expense)
- Operational expenses (debit increases expense)

## Common Banking Transactions

### Transaction 1: Customer Deposits Cash
**Scenario:** Customer deposits $1,000 in cash into checking account

```
Journal Entry:
Debit:   Cash (1000)                          $1,000
  Credit:   Customer Checking Deposit (2100)          $1,000
```

**Explanation:**
- Bank's asset (cash) increases → Debit
- Bank's liability (amount owed to customer) increases → Credit

### Transaction 2: Customer Withdraws Cash
**Scenario:** Customer withdraws $500 from checking account

```
Journal Entry:
Debit:   Customer Checking Deposit (2100)     $500
  Credit:   Cash (1000)                              $500
```

**Explanation:**
- Bank's liability decreases (less owed to customer) → Debit
- Bank's asset decreases (less cash) → Credit

### Transaction 3: Interest Accrual
**Scenario:** Interest accrued on savings account: $50

```
Journal Entry:
Debit:   Interest Accrued (1100)              $50
  Credit:   Interest Income (4000)                   $50
```

**Explanation:**
- Bank's asset increases (interest to be received) → Debit
- Bank's income increases → Credit

### Transaction 4: Interest Credited to Account
**Scenario:** Interest of $50 credited to savings account

```
Journal Entry:
Debit:   Interest Expense (5000)              $50
  Credit:   Customer Savings Deposit (2100)         $50
```

**Explanation:**
- Bank's expense increases (cost to pay interest) → Debit
- Bank's liability increases (more owed to customer) → Credit

### Transaction 5: Fee Charging
**Scenario:** Monthly maintenance fee of $10 charged to account

```
Journal Entry:
Debit:   Fee Income (4100)                    $10
  Credit:   Customer Checking Deposit (2100)        $10
```

**Explanation:**
- Bank's income increases (fee earned) → Credit (income credit)
  Wait, this should be: Income increases with credit
  Actually: Fee income is credit side
  Customer liability decreases with debit

**Corrected Entry:**
```
Debit:   Customer Checking Deposit (2100)    $10
  Credit:   Fee Income (4100)                        $10
```

**Explanation:**
- Bank's liability decreases (less owed to customer) → Debit
- Bank's income increases → Credit

### Transaction 6: Loan Origination
**Scenario:** Bank originates a $100,000 loan to customer

```
Journal Entry:
Debit:   Loans to Customers (1200)            $100,000
  Credit:   Customer Demand Deposit (2100)          $100,000
```

**Explanation:**
- Bank's asset increases (loan given) → Debit
- Bank's liability increases (customer has access to funds) → Credit

### Transaction 7: Loan Payment
**Scenario:** Customer pays $5,000 toward loan (principal + interest)
- Principal: $4,000
- Interest: $1,000

```
Journal Entry:
Debit:   Cash (1000)                         $5,000
  Credit:   Loans to Customers (1200)               $4,000
  Credit:   Interest Income (4000)                  $1,000
```

**Explanation:**
- Bank's asset increases (cash received) → Debit
- Bank's asset decreases (loan balance reduced) → Credit
- Bank's income increases (interest earned) → Credit

### Transaction 8: Loan Loss Provision
**Scenario:** Set aside $10,000 provision for potential loan losses

```
Journal Entry:
Debit:   Loan Loss Expense (5000)             $10,000
  Credit:   Allowance for Loan Losses (1200)        $10,000
```

**Explanation:**
- Bank's expense increases (provision for losses) → Debit
- Bank's contra-asset increases (reduces net loans) → Credit

### Transaction 9: Bank Borrowing
**Scenario:** Bank borrows $1,000,000 from another bank

```
Journal Entry:
Debit:   Cash (1000)                         $1,000,000
  Credit:   Borrowings from Banks (2100)            $1,000,000
```

**Explanation:**
- Bank's asset increases (cash received) → Debit
- Bank's liability increases (amount owed) → Credit

### Transaction 10: Dividend Payment
**Scenario:** Bank pays $50,000 dividend to shareholders

```
Journal Entry:
Debit:   Retained Earnings (3100)             $50,000
  Credit:   Cash (1000)                              $50,000
```

**Explanation:**
- Bank's equity decreases (distribution to owners) → Debit
- Bank's asset decreases (cash paid out) → Credit

## Trial Balance

### Purpose
- Verify all debits equal all credits
- Ensure no accounts are missing
- Check for transcription errors
- Serve as basis for financial statements

### Example Trial Balance

```
Banking Institution
Trial Balance
As of November 30, 2025

Account                                    Debit          Credit
1000 - Cash and Cash Equivalents        $50,000,000
1100 - Customer Deposit Accounts                         $40,000,000
1200 - Loans to Customers               $60,000,000
1300 - Investment Securities             $20,000,000
2000 - Borrowings from Banks                             $30,000,000
2100 - Customer Deposits Payable                        $100,000,000
3000 - Share Capital                                      $5,000,000
3100 - Retained Earnings                                 $10,000,000
4000 - Interest Income                                    $5,000,000
4100 - Fee Income                                         $1,000,000
5000 - Interest Expense                  $3,000,000
5100 - Salaries and Wages                $2,000,000
5200 - Loan Loss Provision               $1,000,000
                                        ___________      ___________
Total                                  $196,000,000    $196,000,000
                                       ===========      ===========
```

Note: Trial balance balances (both sides equal)

## Journal Entry Recording

### Journal Entry Format
```
Date: November 30, 2025
Entry #: JE-2025-11-30-001

Description: Customer deposit and cash vault entry
Debit: Cash (Account 1000)                    $5,000
  Credit: Customer Checking (Account 2100)            $5,000

Recorded by: teller_001
Approved by: supervisor_002
Posted by: batch_processor
Timestamp: 2025-11-30 23:45:00 UTC
Status: Posted
Audit Code: DEPO-001
```

## Double-Entry Accounting Controls

### Self-Checking Nature
The double-entry system has built-in error detection:
- If debits ≠ credits, an error exists
- Forces careful attention to account classification
- Prevents one-sided recording errors
- Reveals posting mistakes automatically

### Segregation of Duties
Different people handle:
1. **Original Entry**: Teller or clerk records transaction
2. **Authorization**: Supervisor approves entry
3. **Posting**: System posts to ledger
4. **Reconciliation**: Different person reconciles

### Audit Trail
Every entry includes:
- Transaction date
- Entry date
- Who entered it
- Who approved it
- When posted
- Any modifications or reversals

## Error Correction Under Double-Entry System

### Method 1: Reversal and Re-entry
**If error discovered same day:**
```
Original (Incorrect) Entry:
Debit: Cash (1000)                $1,000
  Credit: Customer Checking (2100)       $1,000
(Wrong customer, should be $500)

Reversal Entry:
Debit: Customer Checking (2100)    $1,000
  Credit: Cash (1000)                    $1,000

Correct Entry:
Debit: Cash (1000)                  $500
  Credit: Customer Checking (2100)       $500
(Correct customer and amount)
```

### Method 2: Correcting Entry
**If error discovered after posting:**
```
Original (Incorrect) Entry:
Debit: Customer A Checking         $1,000
  Credit: Cash (1000)                    $1,000

Correcting Entry (to correct customer):
Debit: Customer B Checking          $1,000
  Credit: Customer A Checking             $1,000
(Transfers funds from A to B)
```

## Advanced Double-Entry Concepts

### Offsetting Entries
```
Purchase of securities for $100,000:
Debit: Investment Securities (1300)      $100,000
  Credit: Cash (1000)                            $100,000

Sale of securities for $110,000:
Debit: Cash (1000)                       $110,000
  Credit: Investment Securities (1300)          $100,000
  Credit: Investment Gain (4100)                 $10,000
```

### Multi-Currency Entries
```
Convert $100,000 USD to EUR at rate 1.10:
Debit: EUR Account (1100)                €90,909
  Credit: USD Account (1100)                    $100,000

Record FX loss:
Debit: FX Loss (5000)                     $9,091
  Credit: FX Gain/Loss Adjustment (5000)        $9,091
```

### Consolidated Entries
```
End-of-month interest accrual for all customers:
Debit: Interest Accrued (1100)       $50,000
  Credit: Interest Income (4000)               $50,000
```

## Benefits of Double-Entry Accounting

1. **Accuracy**: Built-in error detection
2. **Completeness**: Forces recording of all aspects
3. **Clarity**: Shows both sides of transaction
4. **Control**: Enables segregation of duties
5. **Analysis**: Provides detailed financial information
6. **Audit Trail**: Complete transaction history
7. **Compliance**: Regulatory requirement
8. **Financial Statements**: Enables profit/loss calculation

## Conclusion
Double-entry accounting is fundamental to banking systems. It ensures accuracy, maintains control, and provides the foundation for financial reporting and regulatory compliance. Every transaction must be recorded with equal debits and credits, maintaining the accounting equation: Assets = Liabilities + Equity.
