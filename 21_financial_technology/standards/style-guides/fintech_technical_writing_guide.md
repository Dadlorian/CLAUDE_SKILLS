# Fintech Technical Writing Guide

**Version:** 1.0
**Last Updated:** 2025-11-19
**Authority:** SEC EDGAR, FCA, FFIEC, Google Developer Style Guide, NIST Special Publications

---

## Table of Contents

1. [Introduction](#introduction)
2. [Financial Terminology and Precision](#financial-terminology-and-precision)
3. [Regulatory Language and Compliance](#regulatory-language-and-compliance)
4. [Audience-Specific Writing](#audience-specific-writing)
5. [Security and Privacy Documentation](#security-and-privacy-documentation)
6. [Financial Accuracy and Precision](#financial-accuracy-and-precision)
7. [Audit Trail Documentation](#audit-trail-documentation)
8. [Anti-Patterns](#anti-patterns)
9. [References](#references)

---

## Introduction

### Purpose

This guide establishes writing standards for fintech documentation to ensure:
- **Regulatory compliance** with SEC, FCA, FINRA, and other financial regulators
- **Financial accuracy** with zero tolerance for rounding errors or ambiguity
- **Legal defensibility** in audit and litigation scenarios
- **Cross-stakeholder clarity** for technical and non-technical audiences

### Scope

Applies to all written materials including:
- API documentation
- System design documents
- Compliance reports
- User agreements and disclosures
- Internal runbooks
- Incident reports
- Audit documentation

---

## Financial Terminology and Precision

### Core Principles

1. **Use industry-standard terminology** from ISO 20022, FIX Protocol, and regulatory bodies
2. **Define ambiguous terms** on first use, even if seemingly obvious
3. **Maintain consistency** across all documentation
4. **Avoid colloquialisms** that may not translate across jurisdictions

### Standard Financial Terms

#### Payment Operations

**CORRECT:**
```
Authorization: A hold placed on funds to verify availability before capture.
Capture: The process of moving authorized funds from the cardholder to the merchant.
Settlement: The final transfer of funds between acquiring and issuing banks.
Refund: A reversal of a captured payment, returning funds to the cardholder.
Void: Cancellation of an authorization before capture occurs.
Chargeback: A forced payment reversal initiated by the cardholder's issuing bank.
```

**INCORRECT:**
```
Charging a card (ambiguous - auth or capture?)
Taking payment (lacks precision)
Money transfer (too generic)
Canceling a charge (void vs. refund?)
```

#### Trading and Investment

**CORRECT:**
```
Order: An instruction to buy or sell a security.
Execution: The completion of an order at a specific price.
Fill: The quantity of an order that has been executed.
Settlement Date: T+2 for equities, T+1 for government securities (specify jurisdiction).
Position: The net quantity of a security held in an account.
Mark-to-Market: Valuation of positions using current market prices.
```

**INCORRECT:**
```
Trade (ambiguous - order, execution, or settlement?)
Buy/sell (without specifying order type, time-in-force, etc.)
Portfolio value (without specifying valuation methodology)
```

#### Account Management

**CORRECT:**
```
Account: A custodial arrangement identified by a unique account number.
Sub-account: A logical division within an account for organizational purposes.
Ledger Balance: The account balance including pending transactions.
Available Balance: Funds available for immediate withdrawal or trading.
Held Funds: Amounts reserved for pending operations (specify reason).
```

**INCORRECT:**
```
Wallet (unless specifically referring to digital wallets)
Balance (without specifying ledger vs. available)
Locked money (use "held funds" with reason)
```

### Precision Requirements

#### Amounts and Quantities

**CORRECT:**
```
The transaction amount is USD 1,234.56 (two decimal places for currency).
The position size is 100.5 shares (fractional shares require explicit notation).
The interest rate is 3.25% APR (specify annual percentage rate vs. APY).
The fee is 0.5% of transaction value, minimum USD 1.00.
```

**INCORRECT:**
```
Amount: $1,234.56 (currency symbol ambiguous - USD, CAD, AUD?)
Approximately $1,235 (never approximate in financial contexts)
3.25% interest (ambiguous - APR, APY, monthly?)
Small fee applies (quantify all fees)
```

#### Time and Dates

**CORRECT:**
```
Settlement occurs on 2025-11-21T15:00:00Z (ISO 8601 with timezone).
Trades execute between 09:30:00-16:00:00 EST (specify timezone).
The cutoff time is 14:00:00 UTC for same-day processing.
Record retention: 7 years from transaction date (specify regulation).
```

**INCORRECT:**
```
Tomorrow (relative dates prohibited in formal documentation)
End of day (ambiguous without timezone)
9:30 AM (missing timezone)
During business hours (define explicitly)
```

### Currency Representation

**CORRECT:**
```
USD 1,000.00 (ISO 4217 code before amount)
EUR 500,00 (European decimal separator when appropriate)
GBP 1,000.00 (always specify currency explicitly)
Multi-currency: {USD: 1000.00, EUR: 850.00, GBP: 750.00}
```

**INCORRECT:**
```
$1,000 (ambiguous currency)
1000 USD (code should precede amount in formal docs)
$1,000.00 USD (redundant)
One thousand dollars (use numerals for amounts)
```

---

## Regulatory Language and Compliance

### SEC and EDGAR Requirements

#### Plain English Principles (SEC Release No. 33-7497)

**CORRECT:**
```
You may lose money by investing in this fund.
The fund invests primarily in U.S. Treasury securities.
Past performance does not guarantee future results.
```

**INCORRECT:**
```
Investment involves risk of capital loss.
The fund's investment objective seeks to maximize returns through...
Historical returns should not be construed as indicative of...
```

#### Risk Disclosure

**CORRECT:**
```
RISK DISCLOSURE

Cryptocurrency trading carries significant risks:

1. Market Risk: Digital asset prices are highly volatile. You may lose
   your entire investment.

2. Custody Risk: If you lose your private keys, your assets cannot be
   recovered.

3. Regulatory Risk: Cryptocurrency regulations vary by jurisdiction and
   may change without notice.

4. Technology Risk: Blockchain networks may experience congestion, forks,
   or security vulnerabilities.

Before trading, ensure you understand these risks and can afford potential losses.
```

**INCORRECT:**
```
Warning: Crypto is risky!
You might lose money if the market goes down.
Please trade carefully.
```

### FCA Documentation Standards

#### Fair and Clear Communications

**CORRECT:**
```
Annual Fee: GBP 120.00 (GBP 10.00 per month)
Interest Rate: 19.9% APR variable (representative example)
Late Payment Fee: GBP 12.00 per occurrence

The interest rate may increase if you miss payments.
```

**INCORRECT:**
```
Low annual fee
Competitive interest rates
Standard fees apply
```

### FINRA and MSRB Requirements

#### Recordkeeping Language

**CORRECT:**
```
This communication is subject to FINRA Rule 2210 and will be retained
for three years from the date of last publication, the first two years
in an easily accessible location.

Principal Approval: John Smith, Series 24, 2025-11-19
```

**INCORRECT:**
```
Filed for compliance
Approved by management
```

### PCI DSS Compliance Language

**CORRECT:**
```
CARDHOLDER DATA ENVIRONMENT (CDE)

The CDE includes all systems that store, process, or transmit cardholder
data (CHD) or sensitive authentication data (SAD).

Cardholder Data:
- Primary Account Number (PAN)
- Cardholder Name
- Expiration Date
- Service Code

Sensitive Authentication Data (NEVER store post-authorization):
- Full magnetic stripe data
- CAV2/CVC2/CVV2/CID
- PINs/PIN blocks

Retention Policy: PAN may be stored only when required for business
purposes, encrypted using AES-256, with key management per PCI DSS
Requirement 3.5.
```

**INCORRECT:**
```
Credit card information must be protected.
Don't store CVV codes.
Encrypt sensitive data.
```

---

## Audience-Specific Writing

### Writing for Regulators

#### Characteristics
- Formal tone
- Complete regulatory citations
- Comprehensive documentation of controls
- Emphasis on compliance and risk management

**EXAMPLE: SOC 2 Type II Report Excerpt**

```
CONTROL ACTIVITY: Access Control (CC6.1)

Control Description:
Prior to granting system access, the identity of new users is verified
through government-issued identification and employment verification.
Access rights are assigned based on the principle of least privilege,
mapped to job function requirements documented in the Access Control
Matrix (ACM-2024-001).

Control Frequency: Continuous (authentication), Daily (access reviews)

Evidence:
- Access Control Matrix: ACM-2024-001
- Identity Verification Procedures: IVP-2024-003
- Access Review Logs: Q3-2024-ACCESS-REVIEW

Testing Performed:
Examined a sample of 25 user provisioning events from Q3 2024 to verify:
1. Identity verification completed before access grant (25/25 compliant)
2. Access rights match job function in ACM (25/25 compliant)
3. Manager approval documented (25/25 compliant)

Test Results: No exceptions noted.
```

### Writing for Auditors

#### Characteristics
- Audit trail completeness
- Version control and change tracking
- Evidence references
- Control effectiveness demonstrations

**EXAMPLE: Change Management Documentation**

```
CHANGE REQUEST: CR-2024-1156

Title: Update Payment Authorization Timeout from 60s to 30s

Business Justification:
Reduce authorization hold time to comply with updated PCI DSS v4.0
guidance on minimizing exposure window for sensitive authentication data.

Risk Assessment:
- Impact: Medium (affects authorization flow)
- Probability: Low (well-tested change)
- Mitigation: Canary deployment with automated rollback

Approval Chain:
1. Engineering Lead: Sarah Chen (2024-10-15, 14:23:00 UTC)
2. Security Officer: Michael Rodriguez (2024-10-15, 15:45:00 UTC)
3. Change Advisory Board: Approved (2024-10-18, 16:00:00 UTC)

Testing Evidence:
- Unit Tests: test_suite_v1.2.3 (100% pass)
- Integration Tests: int_test_v2.4.1 (100% pass)
- Load Tests: 10,000 TPS sustained, no degradation
- Security Tests: SAST scan clean, DAST scan clean

Deployment:
- Canary: 2024-10-20, 02:00:00 UTC (5% traffic, 4 hours)
- Production: 2024-10-20, 08:00:00 UTC (100% traffic)

Post-Deployment Validation:
- Authorization success rate: 99.94% (baseline: 99.92%)
- Average latency: 125ms (baseline: 180ms)
- Error rate: 0.06% (baseline: 0.08%)

Result: Successful, no rollback required.
```

### Writing for Users

#### Characteristics
- Plain language
- User benefit focus
- Clear action steps
- Proactive risk communication

**EXAMPLE: User-Facing Security Notification**

```
IMPORTANT: Enable Two-Factor Authentication

What's Changing:
Starting December 1, 2025, you'll need to use two-factor authentication
(2FA) to access your account. This adds an extra layer of security to
protect your money.

Why This Matters:
2FA makes it much harder for unauthorized people to access your account,
even if they know your password.

What You Need to Do:
1. Open your account settings by November 30, 2025
2. Click "Security" → "Two-Factor Authentication"
3. Choose your preferred method:
   - Text message (SMS) to your phone
   - Authenticator app (recommended for better security)
4. Follow the setup instructions

Need Help?
- Video tutorial: [link]
- Step-by-step guide: [link]
- Contact support: 1-800-555-0100 (24/7)

What Happens If You Don't Set It Up:
After November 30, you won't be able to log in until you enable 2FA.

Questions?
Visit our Security FAQ: [link]
```

**INCORRECT VERSION:**
```
We're implementing MFA per our security roadmap.
Please configure 2FA in your account settings.
For assistance, contact support.
```

### Writing for Developers

#### Characteristics
- Technical precision
- Code examples
- Edge case documentation
- Error handling guidance

**EXAMPLE: API Documentation**

```
POST /api/v2/payments/authorize

Description:
Authorizes a payment method for a specified amount. The authorization
places a hold on funds but does not transfer them. Authorizations expire
after 7 days if not captured.

Authentication:
Bearer token (OAuth 2.0) with scope: payments:write

Request Body:

{
  "amount": "1234.56",           // Required. String to preserve precision.
                                  // Max: 999999.99. Min: 0.01.
  "currency": "USD",              // Required. ISO 4217 currency code.
  "payment_method_id": "pm_...", // Required. Previously tokenized payment method.
  "idempotency_key": "...",       // Required. Client-generated UUID to prevent
                                  // duplicate authorizations.
  "metadata": {                   // Optional. Key-value pairs, max 50 entries.
    "order_id": "ord_12345",
    "customer_id": "cus_67890"
  }
}

Response (Success - 201 Created):

{
  "id": "auth_1a2b3c4d5e6f",
  "object": "authorization",
  "status": "authorized",
  "amount": "1234.56",
  "currency": "USD",
  "payment_method_id": "pm_...",
  "created_at": "2025-11-19T10:30:00Z",
  "expires_at": "2025-11-26T10:30:00Z",
  "metadata": { ... }
}

Error Responses:

400 Bad Request - Invalid request format
{
  "error": {
    "code": "invalid_request",
    "message": "Amount must be a string representing a decimal number",
    "param": "amount",
    "type": "invalid_request_error"
  }
}

402 Payment Required - Insufficient funds
{
  "error": {
    "code": "insufficient_funds",
    "message": "The payment method has insufficient funds",
    "type": "card_error",
    "decline_code": "insufficient_funds"
  }
}

429 Too Many Requests - Rate limit exceeded
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests. Retry after 60 seconds.",
    "retry_after": 60,
    "type": "rate_limit_error"
  }
}

Idempotency:
Requests with the same idempotency_key within 24 hours return the original
authorization without creating a duplicate. After 24 hours, the key expires
and a new authorization may be created.

Best Practices:
1. Always use string type for amounts to prevent floating-point precision loss
2. Store the authorization ID for later capture operations
3. Handle expired authorizations gracefully (they cannot be captured)
4. Implement exponential backoff for rate limit errors
5. Never log full payment method details (PCI DSS compliance)

Rate Limits:
- 100 requests per minute per API key
- 1,000 requests per hour per API key

Code Example (Node.js):

const response = await fetch('https://api.example.com/v2/payments/authorize', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
    'Idempotency-Key': uuidv4()
  },
  body: JSON.stringify({
    amount: '1234.56',  // String, not number!
    currency: 'USD',
    payment_method_id: paymentMethodId
  })
});

if (response.status === 201) {
  const auth = await response.json();
  console.log('Authorization successful:', auth.id);
} else if (response.status === 402) {
  const error = await response.json();
  console.error('Payment failed:', error.error.message);
  // Show user-friendly error message
} else {
  // Handle other errors
}
```

---

## Security and Privacy Documentation

### Threat Model Documentation

**CORRECT:**

```
THREAT MODEL: Customer Payment Data Exfiltration

Asset: Customer payment credentials (PAN, expiration date)
Value: High (PCI DSS Level 1, regulatory penalties, customer trust)

Threat Actors:
1. External attackers (motivation: financial gain)
2. Malicious insiders (motivation: financial gain, espionage)
3. Compromised third-party vendors

Attack Vectors:
1. SQL injection in payment processing endpoints
2. Unauthorized database access via compromised credentials
3. Memory dump from application servers
4. Man-in-the-middle attacks during transmission
5. Physical access to backup media

Existing Controls:
1. Parameterized queries (prevents SQL injection)
2. Database access restricted to service accounts, MFA for human access
3. PAN encryption at rest using AES-256-GCM
4. TLS 1.3 for all data in transit
5. Encrypted backups stored in geographically separate facility

Residual Risks:
1. Zero-day vulnerabilities in web framework (Likelihood: Low, Impact: High)
2. Social engineering to obtain credentials (Likelihood: Medium, Impact: High)

Mitigation Roadmap:
1. Q4 2024: Implement tokenization to eliminate PAN storage
2. Q1 2025: Deploy runtime application self-protection (RASP)
3. Q2 2025: Security awareness training for all staff

Owner: Chief Information Security Officer
Review Frequency: Quarterly
Last Reviewed: 2024-11-01
```

### Incident Response Documentation

**CORRECT:**

```
SECURITY INCIDENT REPORT: INC-2024-0847

Classification: Severity 2 (High)
Type: Unauthorized Access Attempt
Status: Resolved

Timeline (All times UTC):

2024-11-18 22:14:00 - Detection
Intrusion detection system (IDS) flagged 1,247 failed login attempts
from IP 198.51.100.42 targeting admin accounts.

2024-11-18 22:15:00 - Initial Response
Security Operations Center (SOC) analyst confirmed brute force attack
pattern. Initiated IR-PROCEDURE-003 (Brute Force Response).

2024-11-18 22:16:00 - Containment
1. Blocked source IP at firewall (automated)
2. Temporarily disabled targeted admin accounts
3. Notified on-call security engineer

2024-11-18 22:30:00 - Investigation
1. Verified no successful authentications from source IP
2. Confirmed MFA prevented any potential breaches
3. Identified 3 targeted accounts: admin_ops, admin_finance, admin_support
4. No evidence of credential compromise

2024-11-18 22:45:00 - Communication
1. Notified affected account owners
2. Briefed VP Engineering and CISO
3. Determined no customer impact, no notification required per
   data breach policy DBP-2024-001

2024-11-18 23:00:00 - Recovery
1. Reset passwords for targeted accounts (out of abundance of caution)
2. Re-enabled accounts with forced MFA re-enrollment
3. Added source IP to permanent blocklist

2024-11-19 02:00:00 - Post-Incident Review
Root Cause: Publicly available admin account usernames combined with
automated credential stuffing attack.

Actions Taken:
1. Implemented rate limiting: 5 failed attempts = 15-minute lockout
2. Removed admin account username patterns from public documentation
3. Scheduled penetration test focusing on authentication (Q1 2025)

Lessons Learned:
1. MFA successfully prevented unauthorized access (control effective)
2. Detection and response time acceptable (16 minutes to containment)
3. Admin username obfuscation needed improvement

Regulatory Reporting:
No reporting required under current regulations (no data breach occurred).

Evidence Preserved:
- IDS logs: /security/incidents/2024/INC-2024-0847/ids_logs.json
- Firewall logs: /security/incidents/2024/INC-2024-0847/firewall_logs.json
- Account activity: /security/incidents/2024/INC-2024-0847/account_activity.json

Report Prepared By: Alice Johnson, Senior Security Analyst
Reviewed By: Robert Chen, CISO
Date: 2024-11-19
```

### Privacy Documentation (GDPR/CCPA)

**CORRECT:**

```
DATA PROCESSING RECORD

Processing Activity: Customer Transaction Monitoring for Fraud Detection

Legal Basis (GDPR Article 6):
Legitimate interest (fraud prevention, financial crime detection)

Data Controller: FinTech Corp, Inc.
Data Protection Officer: privacy@fintechcorp.com

Personal Data Processed:
- Customer name, address, email, phone number
- Transaction history (amount, merchant, timestamp, location)
- Device fingerprints (IP address, browser signature)
- Behavioral patterns (transaction velocity, amount patterns)

Data Subjects: All customers conducting transactions

Purpose:
Real-time fraud detection and prevention to protect customer accounts
and comply with anti-money laundering (AML) regulations.

Recipients:
- Internal: Fraud operations team (10 staff members)
- External: Fraud detection vendor (Acme Fraud Solutions, DPA signed)
- Regulatory: Disclosed to FinCEN upon SAR filing

Retention Period:
7 years from transaction date (per FINRA Rule 4511)

International Transfers:
None. All processing occurs within EU data centers.

Data Subject Rights:
Right to access: Yes
Right to rectification: Yes (accuracy critical for service)
Right to erasure: Limited (regulatory retention requirements supersede)
Right to restriction: Limited (fraud prevention is legitimate interest)
Right to data portability: Yes
Right to object: Limited (necessary for service provision)

Security Measures:
- Encryption at rest: AES-256
- Encryption in transit: TLS 1.3
- Access controls: Role-based, MFA required
- Audit logging: All access logged, 90-day review
- Data minimization: Only necessary fields collected

Legitimate Interest Assessment:
Necessity: Fraud detection essential to protect customers and comply with AML
Balancing: Customer privacy vs. protection from financial crime
Conclusion: Processing justified given high risk of financial fraud and
regulatory obligations. Minimization and security measures reduce privacy impact.

Review Date: 2025-05-19 (semi-annual)
Last Updated: 2024-11-19
```

---

## Financial Accuracy and Precision

### Decimal Handling

**CRITICAL RULE: Never use floating-point types for financial calculations.**

**CORRECT (Code Example):**

```javascript
// Use decimal libraries for financial calculations
const Decimal = require('decimal.js');

// Configure for financial precision
Decimal.set({
  precision: 20,          // Sufficient for financial calculations
  rounding: Decimal.ROUND_HALF_EVEN  // Banker's rounding
});

function calculateInterest(principal, annualRate, days) {
  const p = new Decimal(principal);
  const r = new Decimal(annualRate).dividedBy(100).dividedBy(365);
  const d = new Decimal(days);

  // Interest = Principal × Rate × Days
  const interest = p.times(r).times(d);

  // Round to 2 decimal places for currency
  return interest.toDecimalPlaces(2, Decimal.ROUND_HALF_EVEN).toString();
}

// Example usage
const result = calculateInterest('10000.00', '5.25', 30);
console.log(result);  // "43.15" (exact, no floating-point errors)
```

**INCORRECT:**

```javascript
// NEVER DO THIS
function calculateInterest(principal, annualRate, days) {
  const interest = (principal * (annualRate / 100) * days) / 365;
  return interest.toFixed(2);  // Floating-point errors, incorrect rounding
}

const result = calculateInterest(10000.00, 5.25, 30);
// May produce 43.14999999999 or similar floating-point error
```

### Currency Rounding

**CORRECT:**

```
Rounding Method: Banker's Rounding (Round Half to Even)

Example:
2.125 → 2.12 (rounds to nearest even)
2.135 → 2.14 (rounds to nearest even)
2.145 → 2.14 (rounds to nearest even)
2.155 → 2.16 (rounds to nearest even)

Rationale: Eliminates systematic bias in rounding errors.

Documentation:
All financial calculations use banker's rounding per IEEE 754-2008
specification. This method reduces cumulative rounding bias in
large-scale calculations compared to traditional "round half up" methods.

Implementation: Decimal.js with ROUND_HALF_EVEN mode
```

### Transaction Reconciliation

**CORRECT:**

```
RECONCILIATION PROCEDURE: Daily Payment Settlement

Objective:
Verify that all payment transactions in the ledger match corresponding
bank settlement transactions within a tolerance of USD 0.00.

Process:
1. Extract ledger transactions for T-1 (previous business day)
2. Extract bank settlement report for T-1
3. Match transactions by unique identifier (payment_id)
4. Compare amounts to 2 decimal places
5. Investigate any discrepancies immediately

Tolerance: USD 0.00 (zero tolerance for financial discrepancies)

Expected Match Rate: 100%

Discrepancy Handling:
- Discrepancies > USD 0.00: Immediate investigation, incident report
- Root cause analysis required within 24 hours
- Remediation documented in RECON-ERROR-LOG

Audit Trail:
All reconciliation runs logged with timestamp, match rate, and discrepancies.
Logs retained for 7 years per regulatory requirements.

Responsible: Finance Operations Team
Frequency: Daily (automated at 06:00:00 UTC)
Escalation: Any discrepancy escalated to CFO within 2 hours
```

### Multi-Currency Handling

**CORRECT:**

```
MULTI-CURRENCY TRANSACTION PROCESSING

Storage:
- All amounts stored in their original currency with 2 decimal places
- Exchange rates stored with 6 decimal places (sufficient for FX precision)
- Never store "converted" amounts; calculate at read time

Exchange Rate Source:
Primary: ECB Reference Rates (European Central Bank)
Fallback: Federal Reserve H.10 Rates
Update Frequency: Daily at 16:00 CET

Example Transaction Record:

{
  "transaction_id": "txn_abc123",
  "amount": "1000.00",
  "currency": "EUR",
  "timestamp": "2025-11-19T14:30:00Z",
  "exchange_rate_snapshot": {
    "EUR_USD": "1.085432",
    "rate_timestamp": "2025-11-19T16:00:00Z",
    "source": "ECB"
  }
}

Display to User:
EUR 1,000.00 (approximately USD 1,085.43 at rate 1.0854)

Note: "Approximately" required when displaying conversions to emphasize
that rates fluctuate. Never show converted amounts without qualification.

Regulatory Compliance:
FX rates and sources documented per FINRA Rule 5320 (best execution).
```

---

## Audit Trail Documentation

### Transaction Logging

**CORRECT:**

```json
{
  "event_id": "evt_1a2b3c4d5e6f7g8h",
  "event_type": "payment.authorized",
  "timestamp": "2025-11-19T14:30:45.123Z",
  "actor": {
    "type": "user",
    "user_id": "usr_12345",
    "session_id": "ses_abcdef",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0..."
  },
  "resource": {
    "type": "payment_authorization",
    "id": "auth_xyz789",
    "account_id": "acc_54321"
  },
  "action": {
    "description": "Payment authorization created",
    "result": "success",
    "amount": "1234.56",
    "currency": "USD",
    "payment_method_id": "pm_token123"
  },
  "system_context": {
    "api_version": "v2",
    "service": "payment-gateway",
    "instance_id": "i-0a1b2c3d4e5f",
    "request_id": "req_unique_id_123",
    "trace_id": "trace_distributed_456"
  },
  "compliance": {
    "pci_dss_scope": true,
    "data_classification": "confidential",
    "retention_years": 7,
    "regulatory_basis": "FINRA_4511"
  }
}
```

**Key Requirements:**
1. **Immutable**: Logs never modified, only appended
2. **Complete**: All CRUD operations logged with before/after state
3. **Tamper-evident**: Cryptographic hashing or append-only storage
4. **Timestamped**: ISO 8601 format with timezone (UTC preferred)
5. **Attributable**: Every action tied to authenticated actor

### Change Audit Documentation

**CORRECT:**

```
CONFIGURATION CHANGE LOG: CHG-2024-1203

Change Type: Production configuration update
System: Payment processing service
Component: Authorization timeout threshold

Previous Value:
authorization_timeout_seconds: 60

New Value:
authorization_timeout_seconds: 30

Change Reason:
Reduce exposure window for sensitive authentication data per PCI DSS v4.0
requirement 3.4.1 guidance.

Risk Assessment:
Impact: Medium (affects all payment authorizations)
Likelihood of issues: Low (well-tested in staging)
Rollback plan: Immediate revert via feature flag, no deployment required

Approval:
Requested by: Engineering Team (2024-11-15)
Approved by:
- Engineering Manager: Sarah Chen (2024-11-15T10:30:00Z)
- Security Officer: Mike Rodriguez (2024-11-15T14:20:00Z)
- Change Advisory Board: Approved (2024-11-18T16:00:00Z)

Testing:
- Staging validation: 2024-11-16 (100,000 test transactions, 0 failures)
- Load test: 10,000 TPS sustained, no degradation
- Security scan: No vulnerabilities introduced

Deployment:
- Date/Time: 2024-11-19T02:00:00Z
- Method: Feature flag gradual rollout
- Canary: 5% traffic for 4 hours
- Full rollout: 100% at 2024-11-19T06:00:00Z

Monitoring:
- Authorization success rate (baseline: 99.92%)
- P50/P95/P99 latency (baseline: 180ms/250ms/400ms)
- Error rate by type

Post-Deployment Results:
- Authorization success rate: 99.94% (+0.02%)
- P50 latency: 125ms (-55ms improvement)
- No rollback required

Audit Trail:
Change ticket: JIRA-1203
Code review: PR-4567 (approved by 2 senior engineers)
Deployment log: /var/log/deployments/2024-11-19-payment-gateway.log

Compliance Documentation:
SOC 2 change management evidence: CM-2024-Q4-1203
PCI DSS change control: PCI-CHG-2024-1203

Documented by: Alice Johnson, DevOps Engineer
Reviewed by: Robert Thompson, Principal Engineer
Date: 2024-11-19
```

### Access Audit Trail

**CORRECT:**

```
ACCESS REVIEW REPORT: Q4-2024-PRODUCTION-ACCESS

Review Period: 2024-10-01 to 2024-12-31
Review Date: 2024-11-15
Reviewer: Sarah Chen, Security Manager
Reviewer Manager Approval: Michael Rodriguez, CISO (2024-11-16)

Scope:
All user accounts with access to production payment processing systems.

Methodology:
1. Extract current access list from identity provider (Okta)
2. Compare access rights against Access Control Matrix (ACM-2024-Q4)
3. Verify job function alignment with HR system
4. Validate business need with managers
5. Check for policy violations (terminated users, excessive privileges)

Findings:

Total Accounts Reviewed: 156
Compliant: 152 (97.4%)
Exceptions: 4 (2.6%)

Exception Details:

1. User: john.smith@example.com
   Issue: Retained payment:write scope after role change to Marketing
   Action: Access revoked 2024-11-15T10:30:00Z
   Ticket: SEC-2024-1789

2. User: alice.johnson@example.com
   Issue: Duplicate account (alice.j@example.com also active)
   Action: Secondary account disabled 2024-11-15T11:00:00Z
   Ticket: SEC-2024-1790

3. User: contractor_bob@vendor.com
   Issue: Contract ended 2024-10-31, access not revoked
   Action: Access revoked immediately, escalated to HR
   Ticket: SEC-2024-1791 (Critical)

4. User: admin_ops@example.com
   Issue: Shared account (policy violation)
   Action: Account disabled, individual accounts created for 3 ops staff
   Ticket: SEC-2024-1792

Risk Assessment:
Exception #3 represents a compliance violation (access not revoked within
24 hours of termination per SOC 2 control CC6.1). Remediated immediately
with no evidence of unauthorized activity during the 15-day period.

Corrective Actions:
1. Enhanced offboarding automation to revoke access immediately upon
   HR system status change (Implemented 2024-11-16)
2. Daily automated check for access/employment mismatches (Q1 2025)
3. Additional training for IT ops on contractor offboarding (Q4 2024)

Next Review: Q1-2025 (scheduled for 2025-02-15)

Evidence:
- Access export: /audits/2024-Q4/access-export-2024-11-15.csv
- ACM reference: /policies/access-control-matrix-2024-Q4.xlsx
- Remediation tickets: SEC-2024-1789 through SEC-2024-1792

Compliance Mapping:
- SOC 2 Type II: CC6.1, CC6.2, CC6.3
- PCI DSS: Requirement 7, 8
- GDPR: Article 32 (security of processing)

Report Status: Final
Distribution: CISO, VP Engineering, Audit Committee
```

---

## Anti-Patterns

### Anti-Pattern 1: Ambiguous Financial Terms

**INCORRECT:**
```
The transaction was processed successfully.
```

**Problems:**
- "Processed" is ambiguous (authorized? captured? settled?)
- No timestamp
- No amount or currency
- No transaction identifier

**CORRECT:**
```
Payment authorization auth_abc123 succeeded at 2025-11-19T14:30:45Z
for USD 1,234.56 using payment method pm_xyz789. Funds are held but
not yet captured. Authorization expires at 2025-11-26T14:30:45Z.
```

### Anti-Pattern 2: Floating-Point for Money

**INCORRECT:**
```python
def calculate_fee(amount):
    return amount * 0.029 + 0.30  # Float arithmetic
```

**Problems:**
- Floating-point precision errors
- Incorrect rounding
- Regulatory compliance risk

**CORRECT:**
```python
from decimal import Decimal, ROUND_HALF_EVEN

def calculate_fee(amount):
    """
    Calculate processing fee: 2.9% + $0.30
    Uses decimal arithmetic for financial precision.
    """
    amt = Decimal(str(amount))
    rate = Decimal('0.029')
    fixed = Decimal('0.30')

    fee = (amt * rate + fixed).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_EVEN
    )

    return str(fee)  # Return as string to preserve precision
```

### Anti-Pattern 3: Vague Error Messages

**INCORRECT:**
```
Error: Payment failed
```

**Problems:**
- No actionable information
- No error code for support
- No guidance for user

**CORRECT:**
```
{
  "error": {
    "code": "card_declined",
    "message": "Your card was declined. Please try a different payment method or contact your bank.",
    "type": "card_error",
    "decline_code": "insufficient_funds",
    "support_reference": "ERR-2024-11-19-ABC123",
    "documentation_url": "https://docs.example.com/errors/card_declined"
  }
}

User-facing message:
"Your card was declined due to insufficient funds. Please try another
payment method or contact your bank at 1-800-555-0100."
```

### Anti-Pattern 4: Missing Regulatory Citations

**INCORRECT:**
```
We retain transaction data for 7 years.
```

**Problems:**
- No regulatory justification
- No specification of what data
- No retention policy reference

**CORRECT:**
```
Transaction Data Retention

Retention Period: 7 years from transaction date

Regulatory Basis:
- FINRA Rule 4511 (customer account records)
- SEC Rule 17a-4 (broker-dealer recordkeeping)
- 26 CFR 1.6001-1 (tax records)

Data Covered:
- Transaction confirmations and statements
- Account opening documents
- Customer communications related to transactions
- Order tickets and execution records

Storage:
- Years 1-2: Online, immediately accessible
- Years 3-7: Archival storage, retrievable within 24 hours

Policy Reference: RET-POL-2024-001
Last Reviewed: 2024-01-15
Next Review: 2025-01-15
```

### Anti-Pattern 5: Incomplete Audit Trails

**INCORRECT:**
```json
{
  "user": "alice",
  "action": "transfer",
  "amount": 1000
}
```

**Problems:**
- Missing timestamp
- Missing destination
- Missing currency
- No session or IP tracking
- Insufficient for forensics

**CORRECT:**
```json
{
  "event_id": "evt_1a2b3c4d",
  "event_type": "account.transfer.executed",
  "timestamp": "2025-11-19T14:30:45.123Z",
  "actor": {
    "user_id": "usr_alice_12345",
    "session_id": "ses_xyz789",
    "ip_address": "203.0.113.42",
    "authentication_method": "mfa_totp"
  },
  "source_account": {
    "account_id": "acc_source_123",
    "account_type": "checking",
    "balance_before": "5000.00",
    "balance_after": "4000.00",
    "currency": "USD"
  },
  "destination_account": {
    "account_id": "acc_dest_456",
    "account_type": "savings",
    "balance_before": "2000.00",
    "balance_after": "3000.00",
    "currency": "USD"
  },
  "transfer": {
    "amount": "1000.00",
    "currency": "USD",
    "transfer_id": "xfer_abc123",
    "type": "internal",
    "status": "completed"
  },
  "compliance": {
    "aml_check": "passed",
    "sanctions_check": "passed",
    "velocity_check": "passed"
  },
  "system_context": {
    "api_version": "v2",
    "request_id": "req_unique_789"
  }
}
```

### Anti-Pattern 6: Security Through Obscurity

**INCORRECT:**
```
Our encryption is military-grade and unbreakable.
```

**Problems:**
- Marketing language, not technical specification
- No algorithm specified
- False claim ("unbreakable")
- Violates Kerckhoffs's principle

**CORRECT:**
```
Data Encryption Specifications

Encryption at Rest:
- Algorithm: AES-256-GCM (Advanced Encryption Standard, 256-bit key,
  Galois/Counter Mode)
- Key Management: AWS KMS with automatic key rotation every 90 days
- Standard: NIST FIPS 197, NIST SP 800-38D

Encryption in Transit:
- Protocol: TLS 1.3 (RFC 8446)
- Cipher Suites:
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
- Certificate: RSA 2048-bit minimum, SHA-256 signature
- Perfect Forward Secrecy: Enabled via ECDHE key exchange

Compliance:
- PCI DSS Requirement 3.4 (cardholder data encryption)
- SOC 2 CC6.7 (encryption of sensitive data)
- NIST SP 800-52 Rev. 2 (TLS guidelines)

Key Storage:
Encryption keys are never stored alongside encrypted data. Keys are
managed in hardware security modules (HSMs) certified to FIPS 140-2 Level 3.

Audit: Cryptographic implementation reviewed annually by independent
security firm. Last review: 2024-09-15 (no findings).
```

---

## References

### Regulatory Standards

1. **SEC (U.S. Securities and Exchange Commission)**
   - SEC Release No. 33-7497 (Plain English)
   - SEC Rule 17a-4 (Electronic recordkeeping)
   - SEC EDGAR Filer Manual

2. **FCA (Financial Conduct Authority - UK)**
   - FCA Handbook (COBS, PRIN, SYSC)
   - FCA Guidelines on clear, fair, and not misleading communications

3. **FINRA (Financial Industry Regulatory Authority)**
   - Rule 2210 (Communications with the public)
   - Rule 4511 (General recordkeeping requirements)

4. **FFIEC (Federal Financial Institutions Examination Council)**
   - IT Examination Handbook
   - Business Continuity Planning Booklet

5. **PCI DSS (Payment Card Industry Data Security Standard)**
   - PCI DSS v4.0 Requirements and Testing Procedures
   - PA-DSS (Payment Application Data Security Standard)

### Technical Standards

1. **ISO 20022**
   - Financial services messaging standard
   - Universal Financial Industry message scheme

2. **FIX Protocol**
   - Financial Information eXchange protocol
   - Trading communications standard

3. **NIST (National Institute of Standards and Technology)**
   - NIST SP 800-53 (Security and privacy controls)
   - NIST SP 800-63B (Digital identity guidelines)
   - NIST Cybersecurity Framework

4. **IETF (Internet Engineering Task Force)**
   - RFC 8446 (TLS 1.3)
   - RFC 7519 (JSON Web Token)

### Industry Style Guides

1. **Google Developer Documentation Style Guide**
   - Technical writing best practices
   - API documentation standards

2. **Microsoft Writing Style Guide**
   - Clear, concise technical communication

3. **Stripe API Documentation**
   - Industry-leading fintech API documentation
   - Error handling and code examples

4. **Plaid API Documentation**
   - Financial services API best practices

### Compliance Frameworks

1. **SOC 2 Type II**
   - Trust Services Criteria (AICPA)

2. **ISO/IEC 27001**
   - Information security management

3. **GDPR (General Data Protection Regulation)**
   - EU data protection regulation

4. **CCPA (California Consumer Privacy Act)**
   - California data privacy law

---

**Document Control**

- **Owner:** Chief Technology Officer
- **Approver:** Chief Compliance Officer
- **Review Frequency:** Quarterly
- **Next Review:** 2025-02-19
- **Version History:**
  - 1.0 (2025-11-19): Initial release

**Questions or Suggestions?**
Contact: technical-writing-standards@example.com
