# ACH (Automated Clearing House) Processing Reference

## Overview

ACH is the primary electronic funds transfer system in the United States, enabling direct transfers between bank accounts. It processes over 15 billion transactions annually with a total value exceeding $60 trillion.

**Operators**: Federal Reserve and The Clearing House (TCH)
**Regulation**: Nacha (The EFT Association) sets rules and standards
**Settlement**: T+1 to T+2 business days typical

## Transaction Types

### ACH Credit (Push)
**Direction**: Originator's bank -> Receiver's bank
**Timing**: Money pushed to receiver's account

**Use Cases**:
- Payroll direct deposit
- Vendor payments
- Government benefits distribution
- Business-to-business payments
- Expense reimbursements

**Example Flow**:
```
1. Employer submits payroll file to bank (Friday)
2. Bank processes and batches transactions
3. ACH clearing house processes overnight (Friday night)
4. Funds available in employee accounts (Monday or Tuesday)
5. Bank debits employer's account (after settlement)
```

### ACH Debit (Pull)
**Direction**: Receiver's bank -> Originator's bank
**Timing**: Money pulled from originator's account

**Use Cases**:
- Automatic bill payments
- Insurance premium collection
- Gym membership fees
- Subscription billing
- Loan payments

**Risk**: Requires Authorised User Agreement (for consumer debits)

**Example Flow**:
```
1. Consumer authorizes monthly gym payment
2. Gym submits debit request to their bank
3. Originating Depository Financial Institution (ODFI) receives request
4. ACH clearing house processes overnight
5. Funds pulled from consumer's account (Receiving Depository Financial Institution - RDFI)
6. Funds appear in gym's account (T+1)
```

## ACH Network Architecture

### Three-Party Model

```
ODFI (Originating DFI):
- Merchant's or payer's bank
- Submits ACH file to clearing house
- Responsible for accuracy
- Liable for fraudulent entries
- Validates account numbers and rules

ACH Clearing House:
- Federal Reserve Banks (East, Central, West)
- The Clearing House (TCH)
- Processes files overnight
- Matches debit/credit entries
- Calculates settlement amounts

RDFI (Receiving DFI):
- Receiver's bank
- Posts transactions to accounts
- Processes returns/corrections
- Handles chargebacks
- Returns invalid entries
```

### Processing Timeline

```
11:00 AM EST (Original Deadline):
- File submission cutoff (Standard Entry Class)
- Allows next-day settlement (if using 1-day timeline)

2:00 PM EST (Secondary Deadline):
- Extended deadline
- Allows next-day settlement
- Higher fees typically apply

Overnight Processing (6 PM - 8 AM):
- Sorting and batching
- Debit/credit matching
- Settlement calculations
- Fraud checks

Settlement (9:30 AM EST):
- Funds transferred between banks
- Accounts updated
- Credit entries posted same day (usually)
- Debit entries posted within 1-2 days
```

## ACH File Format

### NACHA File Structure

```
ASCII-formatted file with fixed-length records

File Header Record (1 record):
- Record Type Code: 1
- Priority Code: 00 (routine)
- Immediate Destination: Receiving bank routing number
- Immediate Origin: Originating bank routing number
- File Creation Date: YYMMDD
- File Creation Time: HHMM (24-hour format)
- File ID Modifier: A (or unique identifier)
- Record Size: 094 (always)
- Blocking Factor: 10 (always)
- Format Code: 1 (ASCII)

Batch Header Record (1 per batch):
- Record Type Code: 5
- Service Class Code:
  - 200 = Credits only
  - 220 = Debits only
  - 200 = Both debits and credits
- Company Name: Originating entity name
- Company Discretionary Data: Optional
- Company Identification: FEIN or DUN number
- Standard Entry Class Code:
  - PPD = Payroll (Prearranged Payment and Deposit)
  - CCD = Corporate Credit or Debit
  - IAT = International
  - WEB = Internet-initiated
  - TEL = Telephone-initiated
- Company Entry Description: Transaction description
- Company Descriptive Date: YYMMDD
- Effective Entry Date: YYMMDD
- Settlement Date: JJJ (Julian date, 0-999)
- Originating DFI Identification: Bank routing number

Entry Detail Records (multiple):
- Record Type Code: 6
- Transaction Code:
  - 22 = Debit checking account
  - 23 = Debit savings account
  - 24 = Debit general ledger account
  - 27 = Debit loan account
  - 32 = Credit checking account
  - 33 = Credit savings account
  - etc.
- Receiving DFI Identification: Bank routing number (first 8 digits)
- Check Digit: Routing number check digit
- Account Number: Receiver's account number (up to 17 chars)
- Amount: Transaction amount in cents (no decimal point)
- Individual Identification Number: Reference number
- Individual Name: Account holder name (up to 22 chars)
- Discretionary Data: Optional bank-specific data
- Addenda Record Indicator: Y if addenda present
- Trace Number: Unique transaction identifier

Addenda Records (optional):
- Record Type Code: 7
- Addenda Type Code: 05 for PPD, 10 for WEB, etc.
- Payment-Related Information: Additional details

Batch Control Record (1 per batch):
- Record Type Code: 8
- Service Class Code: (must match batch header)
- Entry/Addenda Count: Total entries + addenda
- Entry Hash: Sum of receiving bank routing numbers
- Total Debits: Sum of all debit amounts
- Total Credits: Sum of all credit amounts
- Company Identification: (must match header)
- Message Authentication Code: Optional security code
- Reserved: Reserved field
- Originating DFI Identification: (must match header)
- Batch Number: Sequential number

File Control Record (1 record):
- Record Type Code: 9
- Batch Count: Number of batches
- Block Count: Number of 940-byte records
- Entry/Addenda Count: Total entries across all batches
- Entry Hash: Sum of all routing numbers (mod 10)
- Total Debits: Sum of all debits
- Total Credits: Sum of all credits
- Reserved: Reserved field
```

### Example NACHA File

```
101 031000053 0000000001 240115 1015 A094101The Bank      Origin Bank Inc    240115
5200Company Name         1234567890PPDPAYROLL   240115 240115   1031000050000001
622012345678901234567      00000500000Individual Name       000000000000001003100001
622012345678901234567      00000750000Another Person       000000000000001003100002
82000002000000000200061728850000075000000005000000000000 Company Name               000001
9000001000001000004000061728850000075000000005000000000000000000000000000000000000000000
```

## ACH Processing Implementation

### Entry Class Codes

```
PPD (Payroll Prearranged Payment and Deposit):
- Most common for payroll
- Requires preauthorization
- 5 business day advance notice required
- Can be stopped by employer

CCD (Corporate Credit or Debit):
- Business-to-business transfers
- 2 business day advance notice
- More flexible than PPD
- Can include addenda records

WEB (Web-Initiated Entry):
- Internet-initiated by consumer
- Authorized via website
- 10-day documentation retention
- Used for bill payments, loan payments

TEL (Telephone-Initiated Entry):
- Consumer authorization via phone
- 10-day documentation retention
- Less common than WEB

IAT (International ACH Transaction):
- Cross-border payments
- More complex formatting
- Longer processing
- Higher fees

ARC (Accounts Receivable Check Conversion):
- Conversion of check to ACH
- Requires original check
- Single debit only
- Common for utility/mortgage payments

POP (Point of Purchase):
- Consumer authorization at checkout
- Debit only
- Single transaction
- Document retention required
```

## ACH Returns and Corrections

### Return Codes

**Valid Reasons for Returns**:

```
R01: Insufficient Funds
- Receiver's account has insufficient balance
- Transaction reverted to originator
- Originator can resubmit
- Can be rejected by RDFI

R02: Account Closed
- Receiving account has been closed
- Entry cannot be deposited
- RDFI returns immediately
- Originator must request new account information

R03: Routing Number Check Digit Error
- Invalid routing number
- RDFI cannot identify destination bank
- Entry returned immediately

R04: Reserved (Not Currently Used)

R05: Improper Debit Entry
- ACH debit submitted to account that only receives credits
- Or other improper entry class code
- Returned by RDFI

R06: Returned per ODFIs Request
- ODFI requested return
- Common for testing, duplicate entries
- OR merchant requested reversal

R07: Authorization Revoked by Customer
- Consumer canceled recurring transaction
- Or cardholder revoked authorization
- RDFI returns entry

R08: Payment Stopped
- Originator requested stop
- (Similar to stop payment on check)
- RDFI honors request and returns

R09: Uncollected Funds (Reclamation)
- Item returned or left uncollected
- RDFI placing hold on funds
- Complex settlement scenario

R10: Customer Advises Not Authorized
- Consumer disputes authorization
- RDFI investigates
- May require documentation
- Can result in charge-back
```

### Return Processing

```
Standard Return Timeline:
1. Transaction is submitted (Day 0)
2. ACH processes overnight (Day 0->1)
3. Funds are posted (Day 1)
4. If returned, return initiated (Days 2-5)
5. Return processes overnight (Day 5->6)
6. Originator receives return notification (Day 6)
7. Originator reconciles (Days 6-7)

Return Details Sent Back:
- Original entry detail (from 94-byte record)
- Return reason code
- Trace number (matches original)
- Receiving bank information
- Timestamp

Originator Responsibilities:
- Monitor returns daily
- Investigate root cause
- Correct account information if needed
- Contact consumer if needed
- Determine resubmission strategy
- Update records
```

### Exceptions and Corrections

```
Notification of Change (NOC):
- RDFI notifies ODFI of changes
- New account number if account moved
- Name change, address change
- Not a return, but informational
- Originator should update records

Reclaim/Reclamation Entries:
- Entry returned for lack of funds
- Reclaim entry may be submitted
- One reclaim allowed per return
- Same amount, same account
```

## ACH Security

### File Encryption

```
In Transit:
- SFTP (SSH File Transfer Protocol)
- HTTPS for web portals
- TLS 1.2 minimum

At Rest:
- AES-256 encryption
- Secure key management
- File delete after processing

Example (Python):
from paramiko import SSHClient, AutoAddPolicy
import pysftp

# SFTP upload with encryption
cnopts = pysftp.CnOpts()
cnopts.hostkeys.load('known_hosts')

with pysftp.Connection('sftp.bank.com',
                      username='company_id',
                      private_key='ach_key.pem',
                      cnopts=cnopts) as sftp:
    sftp.put('payroll_ach.txt', '/incoming/payroll_ach.txt')
```

### Authentication and Authorization

```
Originating Company Requirements:
- Valid FEIN (Federal Employer ID Number)
- or D-U-N-S number
- Company name on file
- Authorized signing officer
- ACH agreement with bank

Transaction Authorization:
- API key or OAuth token (for API submissions)
- Database authentication (for batch uploads)
- Role-based access control
- Audit logging of all submissions

Example Authorization:
// API request with authentication
POST /ach/submit HTTP/1.1
Host: api.bank.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
X-Request-Id: req_123456789

{
  "company_id": "COMP_ABC123",
  "batch_id": "batch_001",
  "entry_class_code": "PPD",
  "effective_date": "2024-01-22",
  "entries": [...]
}
```

### Fraud Prevention

```
Monitoring Controls:
- Volume anomalies (unusual spikes)
- Frequency anomalies (too many small transactions)
- Dollar amount anomalies (unusually large)
- Timing anomalies (unusual submission times)
- Routing number anomalies (new destinations)

Example Detection Rules:
1. Alert if daily volume > 10% above 30-day average
2. Alert if single entry > $100,000 (configurable)
3. Block entries to new routing numbers (pending review)
4. Require approval for PPD entries with no prior history
5. Flag non-standard entry class codes for verification
6. Monitor for duplicate entries (same amount, account, date)
```

## ACH Reconciliation

### Daily Reconciliation Process

```
1. Submission Reconciliation
   - Confirm all submitted entries
   - Verify entry counts and amounts
   - Check for duplicates

2. Settlement Reconciliation
   - Verify settlement amount matches submissions
   - Account for returns and corrections
   - Reconcile bank statement

3. Posting Reconciliation
   - Confirm funds posted to accounts
   - Verify no posting errors
   - Match to customer records

Example (Python):
def reconcile_ach_file(submitted_file, bank_statement):
    submitted = parse_ach_file(submitted_file)
    statement = parse_bank_statement(bank_statement)

    # Verify entry counts
    submitted_count = len(submitted['entries'])
    statement_count = statement['ach_transaction_count']

    if submitted_count != statement_count:
        raise ReconciliationError(
            f'Count mismatch: submitted {submitted_count}, '
            f'statement {statement_count}'
        )

    # Verify amounts
    submitted_total = sum(e['amount'] for e in submitted['entries'])
    statement_total = statement['ach_total']

    if submitted_total != statement_total:
        raise ReconciliationError(
            f'Amount mismatch: submitted ${submitted_total}, '
            f'statement ${statement_total}'
        )

    # Verify net amount
    expected_net = submitted_total - statement['returns_total']
    actual_net = statement['net_ach_amount']

    return {
        'status': 'OK' if expected_net == actual_net else 'FAILED',
        'submitted_entries': submitted_count,
        'statement_entries': statement_count,
        'submitted_amount': submitted_total,
        'returns': statement['returns_total'],
        'expected_net': expected_net,
        'actual_net': actual_net
    }
```

## ACH Limits and Rules

### Transaction Limits

```
Standard Limits:
- Individual transaction: No maximum
- Daily batch: No maximum
- Monthly total: No maximum
- Multiple originating companies: Allowed

ACH Debit Limitations:
- Consumer debits: Require pre-authorization
- Corporate debits: More flexible
- WEB entries: 10-day authorization retention
- PPD entries: 5-day advance notice
```

### Processing Rules

```
Nacha Rules Summary:
- Record size: 94 bytes (fixed)
- File padding: Filled with spaces to 940-byte blocks
- Batch count: Up to 9,999 batches per file
- Entry count: Up to 9,999 entries per batch
- Settlement timeline: 1-2 business days typical
- Correction window: 90 days (varies)

Receiver Account Validations:
- Routing number format and check digit validation
- Account number range validation (up to 17 characters)
- Legal entity vs. personal account considerations
```

## ACH Pricing

### Typical Fees

```
Per Entry:
- Standard ACH: $0.25-1.00
- Same-day ACH: $0.50-2.00
- International ACH (IAT): $5.00-15.00

Volume-Based Pricing:
- 1-100 entries/month: $1.00 per entry
- 101-1,000 entries/month: $0.50 per entry
- 1,001+ entries/month: $0.25 per entry

Monthly Minimums:
- Often $25-50 minimum fee
- Waived for high-volume filers

Return Fees:
- Per return: $1.00-3.00
- Encourages clean data
- Investigated and analyzed
```

## ACH Integration

### API Integration

```
Modern ACH Submission:
// Create payroll batch via API
POST /v1/ach/batches
{
  "entry_class_code": "PPD",
  "effective_date": "2024-01-26",
  "entries": [
    {
      "transaction_code": 32,  // Credit checking account
      "routing_number": "021000021",
      "account_number": "987654321",
      "amount": 5000.00,
      "individual_name": "John Doe",
      "individual_id": "EMP_001"
    },
    {
      "transaction_code": 32,
      "routing_number": "044000037",
      "account_number": "123456789",
      "amount": 7500.00,
      "individual_name": "Jane Smith",
      "individual_id": "EMP_002"
    }
  ]
}

Response:
{
  "batch_id": "batch_20240126_001",
  "status": "SUBMITTED",
  "entry_count": 2,
  "total_amount": 12500.00,
  "effective_date": "2024-01-26",
  "submission_date": "2024-01-23",
  "estimated_settlement": "2024-01-26"
}
```

### Return Processing API

```
// Retrieve returns for batch
GET /v1/ach/batches/batch_20240126_001/returns

Response:
{
  "batch_id": "batch_20240126_001",
  "returns": [
    {
      "trace_number": "021000021000001",
      "return_code": "R02",
      "return_reason": "Account Closed",
      "original_amount": 5000.00,
      "returned_at": "2024-01-25T10:30:00Z",
      "original_entry": {
        "routing_number": "021000021",
        "account_number": "987654321",
        "individual_name": "John Doe"
      }
    }
  ],
  "return_count": 1,
  "total_returned_amount": 5000.00
}
```

## Common ACH Implementation Mistakes

### 1. Incorrect Formatting
```
WRONG:
- Using spaces instead of fixed-length fields
- Incorrect record type codes
- Missing required fields

RIGHT:
- Follow NACHA standard exactly
- Use fixed-length 94-byte records
- Validate against NACHA rules
- Test with ACH validator before submission
```

### 2. Missing Authorization
```
WRONG:
- Submitting WEB entries without 10-day retention
- Submitting PPD without advance notice
- Consumer debits without preauthorization

RIGHT:
- Document all authorizations
- Maintain for required retention period
- Provide proper advance notice
- Keep signed forms or digital proof
```

### 3. Poor Reconciliation
```
WRONG:
- Not reconciling daily
- Not investigating returns
- Resubmitting invalid entries repeatedly

RIGHT:
- Daily reconciliation process
- Root cause analysis for returns
- Correction of account information
- Proper resubmission with corrected data
```

### 4. Inadequate Returns Management
```
WRONG:
- Ignoring returns
- Resubmitting without correction
- Not contacting customer

RIGHT:
- Process returns promptly
- Correct account information
- Contact customer for resolution
- Update records for next submission
```
