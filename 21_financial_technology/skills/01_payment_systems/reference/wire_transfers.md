# Wire Transfers Reference

## Overview

Wire transfers are real-time or near-real-time high-value transfer mechanisms enabling immediate movement of funds between financial institutions. Unlike ACH, wires are irrevocable and cannot be stopped once sent.

**Types**:
- Domestic Wires (Fed Wire in USA)
- International Wires (SWIFT)
- Same-day Wires
- Expedited Wires

## Domestic Wire Transfers (USA)

### Federal Reserve Wire Network (Fedwire)

**Operator**: Federal Reserve System (12 regional banks)
**Coverage**: All US financial institutions
**Processing**: Real-time, 24/7/365
**Settlement**: Immediate and final

**Characteristics**:
```
Real-Time Gross Settlement (RTGS):
- Settlement happens immediately
- No batching or delayed settlement
- Irrevocable once sent
- Guaranteed delivery

Use Cases:
- Large business transactions
- Real estate closings
- Stock/bond settlements
- Urgent fund transfers
- Correspondent bank settlements
```

### The Clearing House (TCH) Wire Network

**Operator**: The Clearing House
**Coverage**: Participating banks
**Processing**: Real-time
**Settlement**: Immediate

**Characteristics**:
```
Alternative to Fedwire:
- Similar capabilities
- Growing adoption
- Used by major banks
- Same settlement finality
```

### Wire Transfer Process

```
Step-by-Step Flow:

1. Initiation (Sender's Bank)
   - Customer provides wire details
   - Bank creates wire instructions
   - Authentication/authorization required
   - Wire details enter system

2. Validation (Sender's Bank)
   - Routing number verification
   - Account number validation
   - Amount validation
   - AML/KYC screening
   - Fraud checks

3. Transmission
   - Bank-to-bank secure transmission
   - FedWire network routing
   - Encrypted message format
   - Routing to receiver's bank

4. Receipt (Receiver's Bank)
   - Bank receives wire instructions
   - Verifies account exists
   - Posts amount to account
   - Account updated real-time

5. Confirmation
   - Receiver's bank confirms receipt
   - Sender receives confirmation number
   - Both parties receive details
   - Funds immediately available (usually)

Timeline:
- Submission to settlement: seconds to minutes
- Confirmation to recipient: typically same day
- Funds available: immediately (usually)
```

### Wire Transfer Message Format

**ISO 8583 and FedWire Specifications**:

```
FedWire Message Structure:

Header:
- Start of Message (SOM)
- Message Type (MT101 domestic, MT202 international)
- Sender's Routing Number
- Receiver's Routing Number
- Timestamp

Body:
- Originator's Bank (Sending Bank)
- Originating Customer ID
- Originating Account Number
- Amount (in cents, no decimal)
- Receiver's Bank (Receiving Bank)
- Receiving Customer ID
- Receiving Account Number
- Remittance Information (purpose/reference)
- Charges Code (who pays fees: OUR, BEN, SHA)

Security:
- Message Authentication Code (MAC)
- Digital Signature
- Encryption

Trailer:
- Checksum
- End of Message (EOM)
```

### Wire Transfer Details

**Information Required**:

```
For Domestic Wire:
1. Sender Information
   - Account holder name
   - Account number
   - Bank routing number
   - Bank name and address

2. Recipient Information
   - Full legal name
   - Account number
   - Bank routing number
   - Bank name and address
   - Recipient country

3. Transfer Details
   - Amount (in USD)
   - Purpose/reference
   - Delivery date (immediate or future)
   - Wire type (standard, expedited)

4. Special Instructions
   - Charges (OUR/BEN/SHA)
   - Intermediary bank (if needed)
   - Correspondent bank details
   - Reference codes (invoice, PO, etc.)
```

## International Wire Transfers (SWIFT)

### SWIFT Network

**Organization**: Society for Worldwide Interbank Financial Telecommunication
**Members**: 11,000+ financial institutions in 200+ countries
**Message Format**: SWIFT standardized (MT103, MT202, etc.)
**Processing**: Overnight batching (typically)

**Characteristics**:
```
Global Financial Standard:
- Universal adoption for international transfers
- Highly standardized messaging
- Strong security
- Regulatory compliance built-in

Processing Timeline:
- 1-3 business days typical
- Same-day SWIFT available (higher cost)
- Overnight settlement in many corridors
```

### SWIFT Message Types

```
MT101: General Financial Institution Transfer
- Used for most business-to-business transfers
- Carries full payment instructions
- Includes remittance details

MT102: Multiple Customer Credit Transfer
- Batch payments from bank to multiple recipients
- Used by corporate cash management
- More efficient for volume

MT202: General Financial Institution Transfer (Correspondent)
- Bank-to-bank transfers
- Intermediary bank details
- Settlement instructions

MT103: Single Customer Credit Transfer
- Consumer to consumer transfers
- Most common SWIFT message
- Includes beneficiary details

MT900: Confirmation of Debit
- Confirms fund debit from account
- Sender receives confirmation

MT910: Confirmation of Credit
- Confirms fund credit to account
- Receiver gets confirmation

MT940: Statement/Advice Message
- Bank statement reporting
- Transaction details
- Account reconciliation
```

### SWIFT Transfer Process

```
International Wire Transfer Timeline:

Day 1 (Submission):
8:00 AM - Customer submits wire request to bank
9:00 AM - Bank validates and screens for AML/KYC
10:00 AM - Bank generates SWIFT MT103 message
11:00 AM - Bank submits to SWIFT network

Day 1 (Overnight SWIFT Processing):
5:00 PM - SWIFT routing to correspondent/receiver bank
6:00 PM - Receiver bank AML/KYC screening
7:00 PM - Settlement at clearing house (CHIPS, EURO1, etc.)

Day 2 (Settlement):
8:00 AM - Funds settled in receiver's account currency
9:00 AM - Receiver bank confirms to end beneficiary

Day 2 (Confirmation):
10:00 AM - Receiver notified
Funds available for use

Total Time: 24-48 hours typical
```

### SWIFT Message Example

```
:20:TRANSREF
:23B:CRED
:32A:240115USD12500,00
:50K:/SNDRACCT123456
SENDER CORPORATION
123 MAIN ST
NEW YORK NY 10001 USA
:52A:DEUTDEDBX
:53B:/CORRESPONDENT
BANK OF AMERICA
NEW YORK
:54A:RBOCINBBXXX
:56A:/INTMDIARY
DEUTSCHE BANK
FRANKFURT
:57A:CHASUS33XXX
:59:/RCPTACCT789012
RECIPIENT COMPANY INC
456 MARKET ST
SAN FRANCISCO CA 94102 USA
:70:Invoice 2024-001 Payment
:71A:OUR
:72:/2/CDET//ABC123

Meaning:
:20: Transaction reference
:23B: Transaction type (Credit)
:32A: Date, currency, amount
:50K: Sender account and name
:52A: Sender's bank
:53B: Correspondent bank
:54A: Intermediary bank
:56A: Another intermediary
:57A: Receiver's bank
:59: Receiver account and name
:70: Remittance information
:71A: Charges (OUR = Sender pays)
:72: Beneficiary to bank information
```

## Wire Transfer Costs

### Domestic Wire Fees

```
Standard Domestic Wire:
- Sending fee: $15-30
- Receiving fee: $0-15 (some banks charge)
- Total: $15-45 per wire

Expedited/Same-Day Wire:
- Sending fee: $25-50
- Receiving fee: $0-20
- Total: $25-70 per wire

High-Volume Discounts:
- 100+ wires/month: $10-20 per wire
- 1,000+ wires/month: $5-10 per wire
```

### International Wire Fees

```
Outgoing International Wire:
- SWIFT fee: $15-50
- Correspondent bank fee: $10-30
- Intermediary bank fees: $10-30 (if used)
- Total: $35-110 per wire

Incoming International Wire:
- SWIFT fee: $0 (usually)
- Receiving bank fee: $10-25
- Intermediary bank fees: $10-25 (if used)
- Total: $10-50 per wire

Same-Day International Wire:
- 50-100% premium over standard
- Typically $50-200 total fees
```

## Wire Transfer Exchange Rates

### Currency Conversion

```
Hidden Costs in International Transfers:

Mid-Market Rate Example:
EUR/USD = 1.10000 (true market rate)

Bank's Offered Rate:
EUR/USD = 1.08500 (bank's rate)

Cost on €10,000 transfer:
Mid-Market: $11,000
Bank Rate: $10,850
Hidden Markup: $150 (1.4% margin)

Comparison (Typical):
- Traditional banks: 2-4% markup
- Online transfer services: 1-2% markup
- Specialist providers: 0.5-1% markup
```

### Rate Protection

```
Forward Contracts:
- Lock in exchange rate for future transfer
- Protection against currency fluctuation
- Advance planning required
- Cost: Typically $100-500

Limit Orders:
- Execute when rate hits target
- Can wait days/weeks for rate
- No guarantee of execution
- Common for hedging

Example:
Forward Contract Setup:
- Want to pay €50,000 in 30 days
- Current rate: EUR/USD = 1.10
- Lock in rate: EUR/USD = 1.09
- Guaranteed cost: USD $54,500
- If market rate drops to 1.08, you're protected
- If market rate rises to 1.11, you saved money
```

## Wire Transfer Security

### Authentication

```
Multi-Factor Authentication (MFA):
- Something you know (password)
- Something you have (security token, phone)
- Something you are (biometric)

Implementation:
1. Username/password login
2. SMS or push notification approval
3. Hardware token confirmation
4. Biometric verification for large wires

Authorization Controls:
- Dual approval for wires > $50,000
- IP address whitelisting
- Device registration
- Velocity checks (limits per day/week)
```

### Fraud Prevention

```
Red Flags and Monitoring:

Unusual Activity:
- Wire to new beneficiary (not in history)
- Wire outside normal business pattern
- Round-dollar amount (unusual precision)
- Wire to high-risk country
- Change in wire frequency or size
- Urgent request (time pressure)
- Multiple wires in short period

Protection Measures:
- Beneficiary registry (pre-approved recipients)
- Amount limits by beneficiary
- Confirmation call to wire initiator
- Email confirmation before execution
- Delay before execution (cooling-off period)
- Transaction signing/approval workflow

Example Fraud Detection Rules:
1. Wire > $100,000 requires dual approval
2. New beneficiary requires confirmation
3. Wires to certain countries require review
4. Velocity: Max 5 wires/day, 20 wires/month
5. Amount: Max $500,000 per wire
```

### Irrevocability and Recovery

```
Once Sent = Permanent:
- Wire is irrevocable once sent
- Cannot be stopped (cannot issue stop payment like check)
- No consumer protection like credit cards
- Funds immediately leave sender's account

Recovery Process (if mistake):
1. Contact sending bank immediately
2. Contact receiving bank
3. Provide full wire details
4. Request beneficiary to return funds
5. Negotiate with receiving bank (rare)
6. Law enforcement involvement
7. Civil suit (last resort)

Success Rate: Very low (5-10% for fraud recovery)
Time to Recovery: Months to years
Cost to Pursue: Tens of thousands

Prevention is Critical:
- Triple-check beneficiary information
- Use confirmation call process
- Implement cooling-off period
- Train staff on fraud
```

## Wire Transfer APIs and Integration

### Wire Submission API

```
Example (Node.js with Payment Processor):

const axios = require('axios');

async function submitDomesticWire(wireDetails) {
  const payload = {
    transaction_type: 'DOMESTIC_WIRE',
    amount_cents: wireDetails.amount * 100,
    currency: 'USD',
    sender: {
      account_number: wireDetails.sender_account,
      routing_number: '021000021'  // Example: Chase NYC
    },
    receiver: {
      account_number: wireDetails.receiver_account,
      routing_number: wireDetails.receiver_routing,
      bank_name: wireDetails.receiver_bank_name,
      account_holder_name: wireDetails.receiver_name
    },
    reference: wireDetails.reference_code,
    delivery_type: 'IMMEDIATE'  // IMMEDIATE or SCHEDULED
  };

  try {
    const response = await axios.post(
      'https://api.bankingservice.com/v1/wires',
      payload,
      {
        headers: {
          'Authorization': `Bearer ${process.env.API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return {
      success: true,
      wire_id: response.data.transaction_id,
      confirmation_number: response.data.confirmation_number,
      status: response.data.status,  // SUBMITTED, PROCESSING, COMPLETED
      estimated_delivery: response.data.estimated_delivery
    };
  } catch (error) {
    return {
      success: false,
      error: error.response.data.error_code,
      message: error.response.data.message
    };
  }
}
```

### Wire Status Tracking

```
POST /v1/wires/{wire_id}/status

Response:
{
  "wire_id": "wire_20240115_001",
  "status": "COMPLETED",
  "amount": 12500.00,
  "currency": "USD",
  "sender_account": "123456789",
  "receiver_account": "987654321",
  "receiver_bank_routing": "044000037",
  "reference": "Invoice-2024-001",
  "submitted_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:35:00Z",
  "completed_at": "2024-01-15T10:45:00Z",
  "confirmation_number": "FW123456789",
  "total_fees": 25.00,
  "final_amount": 12475.00
}
```

## Wire Transfer Compliance

### Regulatory Requirements

```
AML/KYC Screening:
- OFAC lists (Office of Foreign Assets Control)
- Sanctions screening
- PEP (Politically Exposed Persons) checks
- Transaction monitoring
- Beneficial ownership information

Documentation:
- Wire instruction retention (7 years)
- Customer identification documents
- Beneficial ownership documentation
- Transaction records
- Beneficiary verification

Reporting Obligations:
- Large transactions (>$10,000 CTR - Currency Transaction Report)
- Suspicious transactions (SAR - Suspicious Activity Report)
- International transfers (SWIFT message retention)
- Record keeping and reporting to FinCEN
```

### Cross-Border Rules

```
Common Reporting Standard (CRS):
- Information exchange between countries
- Tax reporting for non-residents
- Account holder identification

Structured Data Field (SDF) Requirements:
- Structured remittance information
- Beneficiary information
- Originator information
- ISO 20022 standard

Example SDF:
/BENEFICIARY/John Smith/123 Main St/San Francisco/USA
/ORDERINGCUSTOMER/Acme Corp/456 Oak Ave/New York/USA
/INVOICENUMBER/2024-001
/ORDERNUMBER/PO-12345
```

## Common Wire Transfer Issues

### 1. Incorrect Routing Number
```
WRONG:
- Using consumer checking routing number
- Using SWIFT BIC incorrectly
- Transposing routing digits

RIGHT:
- Verify routing number from bank
- Use ABA routing number for domestic
- Use SWIFT BIC code for international
- Cross-reference multiple sources
```

### 2. Incorrect Account Number
```
WRONG:
- Using account nickname instead of full number
- Wrong account type (savings vs. checking)
- Account number with letters or special chars

RIGHT:
- Verify full account number
- Confirm account type matches wire type
- 17-character maximum (usually)
- Numeric characters only
```

### 3. Missing Beneficiary Information
```
WRONG:
- Wire without full beneficiary name
- Missing or incomplete address
- No reference/invoice information

RIGHT:
- Full legal name (first and last)
- Complete address with country
- Invoice/order reference for reconciliation
- Specific payment purpose
```

### 4. Fraud and Impersonation
```
WRONG:
- Trusting wire request without verification
- Sending wire based on email
- Not confirming verbal instruction

RIGHT:
- Call sender back to verify wire request
- Use established procedures
- Document authorization
- Confirm unusual requests separately
- Use confirmation numbers
```

## Wire Transfer Compliance Mistakes

### 1. Inadequate Due Diligence
```
WRONG:
- Wire without AML/KYC screening
- Sending to sanctioned entities
- Skipping beneficial ownership checks

RIGHT:
- Screen all parties against OFAC/PEP lists
- Document due diligence
- Monitor ongoing compliance
- Flag and report suspicious activity
```

### 2. Poor Documentation
```
WRONG:
- No record of wire authorization
- Missing beneficiary documentation
- No audit trail

RIGHT:
- Document all wires (7+ year retention)
- Keep authorization records
- Maintain audit trail
- Electronic signature where required
```

### 3. Inadequate Fraud Controls
```
WRONG:
- No verification of beneficiary
- No dual approval for large wires
- No velocity limits

RIGHT:
- Beneficiary registry and pre-approval
- Multi-person authorization for $50k+
- Daily/monthly wire limits
- Unusual activity alerts
```
