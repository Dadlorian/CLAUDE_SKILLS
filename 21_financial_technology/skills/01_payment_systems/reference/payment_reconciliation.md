# Payment Reconciliation Reference

## Overview

Payment reconciliation is the process of verifying that all transactions submitted for processing have been properly settled, matched against bank statements, and accounted for in financial records. Critical for accurate financial reporting and fraud detection.

## Reconciliation Process

### Daily Reconciliation

```
Timeline:
- T+0 (Transaction Day)
  Morning: Monitor submissions (real-time)
  Evening: End-of-day settlement preparation

- T+1 (Settlement Day)
  Morning: Bank posts settlement
  Afternoon: Download statement
  Evening: Reconcile against submissions

Three-Way Reconciliation:
1. Submitted Batch vs. Processor Records
   - Count matching
   - Amount matching
   - Entry matching

2. Processor Records vs. Bank Statement
   - Settlement amount matching
   - Fees verification
   - Chargebacks/returns verification

3. Bank Statement vs. General Ledger
   - Amount posted to bank account
   - All fees accounted
   - Timing of posting

Process Steps:
1. Extract submitted batch file
   - Total count of transactions
   - Total amount of transactions
   - Hash of account numbers
   - List of special transactions

2. Get processor settlement report
   - Transactions settled
   - Returns/chargebacks
   - Fees deducted
   - Net settlement amount
   - Settlement date

3. Download bank statement
   - Deposit amount
   - Deposit date
   - Any holds/reversals
   - All fees

4. Reconcile
   - Submitted count = Processor settled count + returns
   - Submitted amount = Processor settled amount + return amounts
   - Processor net = Bank deposit
   - All fees match

5. Investigate discrepancies
   - Missing transactions
   - Extra transactions
   - Timing differences
   - Amount mismatches
   - Fee variances

6. Document reconciliation
   - Sign-off by responsible person
   - Note any exceptions
   - Record resolution of discrepancies
   - File for audit
```

### Weekly Reconciliation

```
Goal: Consolidate daily reconciliations
Find cumulative issues
Resolve outstanding items

Process:
1. Consolidate daily reports
   - 5-7 daily statements
   - Total submitted
   - Total settled
   - Total returned/declined

2. Identify exceptions
   - Transactions not yet settled (delay)
   - Pending returns/chargebacks
   - Fees not yet applied
   - Reversals outstanding

3. Investigate exceptions
   - Follow up on delayed settlements
   - Confirm return processing
   - Verify chargeback notifications
   - Validate fee calculations

4. Resolve issues
   - Contact processor for delays
   - Process refunds for returns
   - Prepare chargeback defense
   - Dispute incorrect fees

5. Report to management
   - Weekly reconciliation summary
   - Exceptions summary
   - Actions taken
   - Outstanding items
```

### Monthly Reconciliation

```
Goal: Account-level reconciliation
Link payments to GL accounts
Support financial reporting

Process:
1. Sum all transactions
   - Total volume
   - Total value
   - By payment method
   - By merchant
   - By processor

2. Account for settlements
   - Deposits received
   - Timing of deposits
   - By bank account
   - By processor

3. Account for reversals
   - Returns/refunds
   - Chargebacks
   - Adjustments
   - Network corrections

4. Book to general ledger
   - Account: Merchant deposit (asset)
   - Account: Payment processing fees (expense)
   - Account: Chargebacks/returns (expense/revenue)
   - Account: Interchange (if tracked separately)

5. Reconcile to trial balance
   - Bank account in GL matches bank statement
   - All transactions accounted
   - All fees recorded
   - All returns/chargebacks recorded

Example GL Entries:
// Daily deposit received
Dr. Bank Account         $9,750.00
  Cr. Merchant Payables           $9,750.00
  (From payment processor)

// Fees deducted
Dr. Payment Processing Fees $250.00
  Cr. Merchant Payables            $250.00

// Return processed (debit from account)
Dr. Merchant Payables    $100.00
  Cr. Bank Account                 $100.00
  (Customer refund)

// Chargeback processed
Dr. Chargeback Loss      $150.00
  Cr. Bank Account                 $150.00
  (Cardholder dispute)
```

## Reconciliation Issues and Resolutions

### Common Discrepancies

```
1. Timing Differences
Issue:
- Batch submitted on Day 1
- Settlements on Day 2 (T+1)
- Some transactions settle Day 3 (T+2)
- Creates apparent mismatch

Resolution:
- Track settlement timeline per processor
- Expect T+1 to T+3 range
- Monitor for delayed settlements
- Investigate anything > T+3

2. Missing Transactions
Issue:
- Submitted 100 transactions
- Processor settled 98 transactions
- 2 transactions missing

Root Causes:
- Transaction declined by network
- Duplicate detected and merged
- File transmission error
- Customer dispute (refund issued immediately)

Resolution:
- Check processor decline report
- Verify duplicate transactions
- Identify declined transactions
- Refund customer if needed
- Update records

3. Extra Transactions
Issue:
- Processor settled more than submitted
- Reversals being resubmitted
- Returns being re-processed

Root Causes:
- Return reversal (return was wrong)
- Chargeback reversal (merchant won dispute)
- Correction transaction (fix amount)
- Deferred transaction (delayed from previous batch)

Resolution:
- Identify extra transactions
- Determine reason
- Book to appropriate account
- Document exception

4. Amount Mismatches
Issue:
- Submitted $10,000
- Processor settled $9,950
- $50 difference

Root Causes:
- Fees deducted ($25-50 typical)
- Chargebacks/returns processed ($50-200)
- Correction adjustments
- Network fees

Resolution:
- Verify fees breakdown
- Confirm charge backs
- Account for adjustments
- Investigate if unreasonable

5. Fee Discrepancies
Issue:
- Expected fees: $200 (2%)
- Actual fees: $225
- Difference: $25

Root Causes:
- Volume discount calculation
- Premium cards (higher interchange)
- Network assessment changes
- Processor fee changes

Resolution:
- Compare to processor rate card
- Verify volume discounts applied
- Confirm card mix (visa/mc/amex)
- Dispute if calculation error
- Update expected fees for future

6. Chargeback Timing
Issue:
- Chargeback filed 90 days after transaction
- Unexpected in reconciliation
- Creates adjustment

Resolution:
- Monitor chargeback alerts separately
- Track chargebacks as separate GL account
- Reserve for expected chargebacks
- Provision in bad debt account

Example:
// Chargeback in month 3 for transaction from month 1
Dr. Chargeback Loss       $100.00
Dr. Bad Debt Reserve      $100.00  // (reverse old provision)
  Cr. Bank Account                 $100.00
  Cr. Bad Debt Reserve             $100.00

7. Return/Refund Processing
Issue:
- Customer requests refund
- Refund issued immediately to customer
- Debit from merchant account
- Creates negative in reconciliation if not tracked

Resolution:
- Issue credit memo for refund
- Track refunds separately
- Deduct from revenue or offset against payments
- Update GL with refund entry
```

## Reconciliation Automation

### Automated Matching

```
Technology:
- Reconciliation software (BlackLine, Anaplan)
- Custom scripts (Python, Java)
- APIs for data extraction
- Machine learning for intelligent matching

Automated Process:
1. Extract data automatically
   - Fetch submitted batch from system
   - Download processor settlement report via API
   - Pull bank statement (OFX/MT940 format)

2. Parse and normalize data
   - Standardize date formats
   - Normalize currency values
   - Map transaction types
   - Clean transaction descriptions

3. Match transactions
   - Exact match: Amount + Reference + Date
   - Fuzzy match: Amount +/- tolerance
   - ML matching for complex scenarios
   - Flag unmatched items for review

4. Generate exceptions report
   - List unmatched transactions
   - Categorize by type (timing, missing, etc.)
   - Flag high-value discrepancies
   - Prioritize by age and amount

5. Escalate exceptions
   - Auto-resolve known patterns
   - Flag for manual review
   - Send alert notifications
   - Track resolution

Example (Python):
```python
import pandas as pd
from datetime import datetime, timedelta

class PaymentReconciliation:
    def __init__(self):
        self.tolerance = 0.01  # 1 cent tolerance

    def load_data(self):
        """Load submitted, processor, and bank data"""
        self.submitted = pd.read_csv('submitted_batch.csv')
        self.processor = pd.read_csv('processor_settlement.csv')
        self.bank = pd.read_csv('bank_statement.csv')

    def normalize_data(self):
        """Normalize data for matching"""
        # Convert dates to datetime
        for df in [self.submitted, self.processor, self.bank]:
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = df['amount'].astype(float)
            df['reference'] = df['reference'].str.upper().str.strip()

    def match_transactions(self):
        """Match transactions across data sources"""
        matches = []
        unmatched = []

        for idx, submitted_txn in self.submitted.iterrows():
            # Try exact match
            matched = self.processor[
                (self.processor['reference'] == submitted_txn['reference']) &
                (abs(self.processor['amount'] - submitted_txn['amount']) < self.tolerance) &
                ((self.processor['date'] - submitted_txn['date']).dt.days <= 3)
            ]

            if len(matched) > 0:
                matches.append({
                    'reference': submitted_txn['reference'],
                    'amount': submitted_txn['amount'],
                    'status': 'MATCHED'
                })
            else:
                unmatched.append({
                    'reference': submitted_txn['reference'],
                    'amount': submitted_txn['amount'],
                    'status': 'UNMATCHED',
                    'reason': 'Not found in processor settlement'
                })

        return matches, unmatched

    def reconcile_bank(self):
        """Reconcile processor settlement to bank statement"""
        processor_total = self.processor['amount'].sum()
        bank_deposits = self.bank[self.bank['type'] == 'DEPOSIT']['amount'].sum()

        if abs(processor_total - bank_deposits) < self.tolerance:
            return {'status': 'RECONCILED', 'difference': 0}
        else:
            return {
                'status': 'VARIANCE',
                'difference': processor_total - bank_deposits,
                'message': 'Investigation required'
            }

    def generate_report(self):
        """Generate reconciliation report"""
        matches, unmatched = self.match_transactions()
        bank_recon = self.reconcile_bank()

        report = {
            'date': datetime.now(),
            'submitted_count': len(self.submitted),
            'matched_count': len(matches),
            'unmatched_count': len(unmatched),
            'match_rate': len(matches) / len(self.submitted),
            'bank_reconciliation': bank_recon,
            'unmatched_transactions': unmatched,
            'status': 'PASS' if bank_recon['status'] == 'RECONCILED' and len(unmatched) == 0 else 'FAIL'
        }

        return report

# Usage
reconciliation = PaymentReconciliation()
reconciliation.load_data()
reconciliation.normalize_data()
report = reconciliation.generate_report()
print(f"Reconciliation Status: {report['status']}")
print(f"Match Rate: {report['match_rate']:.2%}")
print(f"Unmatched: {report['unmatched_count']}")
```

## Exception Investigation

### Investigation Workflow

```
Exception Received
   |
   v
Categorize Exception
   |
   +-- Timing Issue (expected in 1-2 days)
   |   -> Monitor for resolution
   |
   +-- Missing Transaction
   |   -> Check processor decline report
   |
   +-- Extra Transaction
   |   -> Verify reason code
   |
   +-- Amount Discrepancy
   |   -> Review fees/adjustments
   |
   +-- Fee Variance
   |   -> Compare to rate card
   |
   v
Investigate Root Cause
   |
   v
Determine Resolution
   |
   +-- Reversal needed? -> Process reversal
   |
   +-- Adjustment needed? -> Book adjustment
   |
   +-- Processor error? -> Dispute and escalate
   |
   +-- Customer action needed? -> Contact customer
   |
   v
Document Resolution
   |
   v
Book to GL
   |
   v
Monitor for similar issues
```

## Financial Reporting

### Reserve and Provisions

```
Chargeback Reserve:
- Estimate expected chargebacks (0.05-0.5% of volume)
- Set aside reserve monthly
- Use reserve to cover actual chargebacks
- Adjust reserve quarterly

Example:
Monthly volume: $100,000
Expected chargeback rate: 0.1%
Expected chargebacks: $100
Monthly reserve: $100

GL Entry:
Dr. Chargeback Expense   $100
  Cr. Chargeback Reserve      $100

When chargeback occurs:
Dr. Chargeback Reserve   $50
  Cr. Bank Account            $50

Bad Debt Provision:
- For recurring billing customers
- Estimate uncollectible amounts
- Set aside provision
- Adjust based on actual collections

Example:
Total recurring billing: $50,000/month
Uncollectible rate: 2%
Bad debt provision: $1,000

GL Entry:
Dr. Bad Debt Expense     $1,000
  Cr. Bad Debt Allowance      $1,000

Reporting:
- Present net (receivables minus allowance)
- Disclose reserve and allowance policies
- Show write-offs vs. provisions
```

## Reconciliation Audit

### Internal Controls

```
Key Controls:
1. Segregation of Duties
   - Processor not same as approver
   - Bank statement reviewed by different person
   - GL posted by finance (not operations)

2. Reconciliation Sign-Off
   - Daily reconciliation signed by manager
   - Weekly summary signed by supervisor
   - Monthly GL reconciliation signed by controller

3. Exception Investigation
   - All exceptions investigated
   - Investigation documented
   - Resolution approved
   - Follow-up for patterns

4. Audit Trail
   - All changes logged
   - Timing and user recorded
   - Justification documented
   - Retained for audit

5. Periodic Review
   - Quarterly internal audit
   - Reconciliation process review
   - Compliance assessment
   - Control testing
```

### External Audit

```
Auditor Focus:
- Completeness of transactions
- Accuracy of amounts
- Timeliness of settlement
- Proper GL accounting
- Internal control effectiveness

Testing Procedures:
- Reperform reconciliations
- Test sample of transactions
- Verify settlement amounts
- Confirm bank statement
- Test internal controls
- Assess fraud risk

Common Audit Issues:
- Untimely reconciliations
- Unresolved discrepancies
- Lack of documentation
- Weak controls
- Incorrect GL postings

Remediation:
- Implement automation
- Strengthen controls
- Improve documentation
- Train staff
- Regular supervisor review
```
