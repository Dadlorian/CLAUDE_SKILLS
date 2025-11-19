# FinTech Technical Writing Style Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-19
**Scope:** Financial Technology Documentation Standards
**Compliance:** SOC 2 Type II, GDPR, PCI DSS 4.0

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Writing Principles](#core-writing-principles)
3. [Audience Segmentation](#audience-segmentation)
4. [Tone and Voice](#tone-and-voice)
5. [Financial Services Language Standards](#financial-services-language-standards)
6. [Regulatory and Compliance Writing](#regulatory-and-compliance-writing)
7. [Security and Risk Communication](#security-and-risk-communication)
8. [API Documentation Standards](#api-documentation-standards)
9. [Error Messages and User Communication](#error-messages-and-user-communication)
10. [Examples and Case Studies](#examples-and-case-studies)
11. [Accessibility and Localization](#accessibility-and-localization)
12. [Review and Approval Workflows](#review-and-approval-workflows)

---

## Executive Summary

This style guide establishes the authoritative standards for all technical writing in the FinTech ecosystem. It aligns with practices established by industry leaders including Stripe, Square, Bloomberg, and PayPal, while incorporating regulatory requirements from financial services authorities globally.

**Key Principles:**
- Precision over brevity (accuracy is non-negotiable)
- Clarity for diverse technical audiences
- Regulatory compliance by default
- Security-first communication
- Accessibility as a requirement, not an afterthought

---

## Core Writing Principles

### 1. Accuracy and Precision

In financial technology, accuracy is a legal and operational requirement, not merely a quality attribute.

**Requirements:**
- Every numerical value must be verified against source systems
- Financial terminology must match legal definitions in applicable jurisdictions
- Technical accuracy takes precedence over brevity
- All monetary amounts must include currency designation
- Decimal precision must match system capabilities

**Example (Correct):**
```
The platform processes transactions with a decimal precision of 8 places
for cryptocurrency values and 2 places for fiat currencies. For example,
Bitcoin transactions are recorded as 0.00000001 BTC (1 Satoshi), while
USD transactions are recorded as $0.01 (1 cent).
```

**Example (Incorrect):**
```
Transactions can be processed with high precision. For example, Bitcoin
values are very precise and USD amounts are precise too.
```

### 2. Clarity and Accessibility

Documentation must serve users across technical skill levels while maintaining precision.

**Multi-Level Documentation Structure:**

**Level 1 - Conceptual:** High-level business context
**Level 2 - Procedural:** Step-by-step implementation
**Level 3 - Reference:** Complete technical specifications
**Level 4 - Troubleshooting:** Problem resolution

### 3. Compliance-First Approach

Every document must address regulatory requirements implicitly or explicitly.

**Regulatory Frameworks to Consider:**
- **Data Protection:** GDPR, CCPA, data residency requirements
- **Financial Regulation:** SOX, Dodd-Frank, MiFID II
- **AML/KYC:** FinCEN regulations, enhanced due diligence
- **Payment Services:** PCI DSS, payment processor regulations
- **Accessibility:** WCAG 2.1 Level AA compliance

### 4. Active Voice with Attribution

Use active voice to clearly identify responsible parties in financial contexts.

**Example (Correct):**
```
The compliance team reviews all transactions flagged by the fraud detection
system. Each review must be completed within 24 hours and documented with
the reviewer's reasoning.
```

**Example (Problematic):**
```
Transactions flagged by the fraud detection system must be reviewed within
24 hours. (Unclear who reviews or documents)
```

### 5. Precision in Definitions

Financial terms often have legal definitions that differ from common usage.

**Pattern:**

```markdown
**[Term]:** [Simple definition]. In the context of [regulatory framework],
[Term] is defined as [precise legal definition] per [regulation reference].

**Example:** [Real fintech implementation example]

**Common Misunderstanding:** [Address likely confusion points]
```

**Example:**

```markdown
**Transaction Settlement:** The point at which funds transfer between
accounts becomes final and irrevocable. In ACH transfers (per NACHA rules),
settlement occurs when the Federal Reserve acknowledges the transfer. For
card transactions (per ISO 8583), settlement typically occurs 1-3 business
days after authorization, depending on the acquirer's processing cycle.

**Example:** A customer authorizes a $500 debit card purchase at 2:00 PM
on Monday. The authorization is approved immediately, but settlement might
not occur until Wednesday morning, during the acquirer's daily batch
processing.

**Common Misunderstanding:** Many users assume authorization = settlement.
This confusion can cause issues when customers see "pending" transactions
that appear multiple times (authorization holds).
```

---

## Audience Segmentation

### Primary Audiences

**1. Developers/Engineers**
- Assume CS degree or equivalent knowledge
- Provide complete technical specifications
- Include code examples in primary implementation languages
- Reference architecture and design patterns
- Detail error codes and troubleshooting

**Document Structure:**
- API reference format
- Code examples with context
- Architecture diagrams
- Performance implications
- Security considerations

**2. Financial Operations Teams**
- Assume finance/accounting background, not necessarily technical
- Focus on business processes and regulatory implications
- Use accounting and finance terminology correctly
- Include audit trails and compliance implications
- Explain financial impact and risk exposure

**Document Structure:**
- Business process flows
- Regulatory context
- Risk assessment
- Reconciliation procedures
- Compliance checklist

**3. Product and Business Stakeholders**
- Assume business/MBA background
- Focus on capabilities and limitations
- Include market context and competitive positioning
- Highlight regulatory or business constraints
- Address user experience implications

**Document Structure:**
- Capability overview
- Business case and ROI
- Market context
- User scenarios
- Limitation and constraints

**4. Security and Compliance Officers**
- Assume security/legal background
- Focus on risk, controls, and audit trails
- Include threat modeling and mitigation strategies
- Reference regulatory requirements explicitly
- Detail data handling and encryption

**Document Structure:**
- Risk assessment
- Control documentation
- Threat model
- Compliance mapping
- Incident response procedures

---

## Tone and Voice

### Core Voice Attributes

**Professional but Accessible:** Stripe's technical documentation achieves this by using conversational language while maintaining absolute precision.

**Confidence Without Arrogance:** Bloomberg's documentation conveys expertise and reliability without condescension.

**Transparency About Limitations:** Square explicitly documents limitations, edge cases, and known issues, building trust.

### Example: Professional Technical Voice

```markdown
GOOD (Professional, clear, transparent):
"The Webhook Signature Verification endpoint uses HMAC-SHA256 signing,
which prevents man-in-the-middle attacks. However, webhook verification
requires you to securely store your webhook signing key. If your key is
compromised, immediately regenerate it in the Dashboard (this will
invalidate all previous signatures within one minute). We recommend
rotating keys quarterly as a security best practice."

BAD (Too casual):
"We use really good encryption for webhooks lol. Just keep your secret
safe or bad things could happen."

BAD (Condescending):
"Obviously, you should understand that HMAC-SHA256 is an industry-standard
cryptographic function (defined in RFC 2104) that produces a
cryptographically secure message authentication code..."
```

### Tone Adjustment by Context

**Informational/Reference:** Neutral, objective, precise
```
The platform supports 150+ currencies, with exchange rates updated every
60 seconds using real-time market feeds.
```

**Warning/Risk:** Direct, clear, action-oriented
```
Never commit API keys to version control. If a key is exposed, regenerate
it immediately. Exposed keys can be used to drain customer funds.
```

**Congratulatory/Successful Outcomes:** Positive, encouraging
```
You've successfully configured webhook signature verification. Your
application is now protected against unauthorized webhook requests.
```

---

## Financial Services Language Standards

### 1. Currency and Amount Formatting

**Standards:**
- Always include currency code: `USD`, `EUR`, `GBP`, not `$`, `€`, `£`
- For international documentation: `USD $100.00` or `100.00 USD`
- Decimal places must match the currency: `USD 0.01` minimum, but `JPY 1` (no decimals)
- Never use `K` or `M` abbreviations in financial contexts
- Avoid word representations: use `$100` not `one hundred dollars`

**Correct Examples:**
- USD 10,000.50 (for international contexts)
- $10,000.50 (for US-centric contexts)
- 10000.50 USD (API response format)
- EUR 1,234.56 (European context)
- GBP 999.99 (British context)

### 2. Transaction and Settlement Language

**Precise Definitions:**

- **Authorization:** The bank confirms the customer has sufficient funds or credit
- **Capture:** The transaction moves to settlement queue (typically occurs immediately after authorization)
- **Settlement:** Funds actually transfer between accounts (1-3 business days typical)
- **Posting:** The transaction appears on the customer's statement
- **Reconciliation:** Matching settled transactions with expected values

**Correct Usage:**
```markdown
1. Customer swipes card (authorization request)
2. Processor approves authorization (customer sees "pending")
3. Merchant initiates capture (usually automatic)
4. ACH clearing house processes batch settlement (typically next business day)
5. Customer's bank posts transaction (1-2 business days after settlement)
6. Accounting team reconciles against settlement report

Total time from authorization to posted: 2-4 business days typical
```

### 3. Regulatory Terminology

**AML/KYC Terms:**
- **Know Your Customer (KYC):** Identity verification process
- **Customer Due Diligence (CDD):** Standard customer information verification
- **Enhanced Due Diligence (EDD):** Deeper investigation for high-risk customers
- **Beneficial Owner:** Natural person who ultimately owns/controls an entity
- **Politically Exposed Person (PEP):** High-risk individual with political connections

**Compliance Terms:**
- **Regulatory Compliance:** Meeting legal requirements (not mere best practices)
- **Audit Trail:** Immutable record of who did what, when, with system verification
- **Attestation:** Formal confirmation (stronger than "review")
- **Certification:** Third-party verification of compliance
- **Remediation:** Steps taken to fix compliance violations

### 4. Risk and Security Language

**Security Contexts:**

```markdown
ENCRYPTION SPECIFICATION (Correct):
"Data is encrypted using AES-256-GCM in transit (TLS 1.3) and at rest
(AWS KMS-managed keys with automatic rotation). Encryption keys are
generated using OS-level cryptographic random sources with minimum
256-bit entropy."

SECURITY CLAIMS (Correct):
"The webhook signature verification uses HMAC-SHA256 (FIPS 140-2 compliant
implementation) to prevent tampering. In security audits, this approach
achieved zero findings."

SECURITY CLAIMS (Incorrect):
"Our security is military-grade" or "unhackable" - avoid absolute claims
```

### 5. Compliance-Specific Language

**For Documentation Subject to Regulatory Review:**

```markdown
**Control Name:** [System Name] - [Control Objective]

**Control Type:** Preventive | Detective | Corrective

**Regulatory Requirement:** [Reference - e.g., "PCI DSS 3.4.1"]

**Description:** [What the control does in objective terms]

**Frequency:** [When verified - Daily | Weekly | Monthly | Quarterly | Annually]

**Evidence:** [What audit trail demonstrates compliance]

**Owner:** [Responsible party with escalation path]

**Last Verified:** [Date and verification method]
```

### 6. Cryptocurrency and Digital Asset Language

```markdown
**Bitcoin:** A decentralized digital currency that operates on a
proof-of-work consensus mechanism. When integrating Bitcoin payments,
note that transaction finality requires ~6 block confirmations (~60
minutes average).

**Stablecoin:** A cryptocurrency designed to maintain stable value relative
to another asset (e.g., USDC pegged to USD). Regulatory treatment varies
by jurisdiction but increasingly subjects stablecoin issuers to money
transmitter requirements.

**Smart Contract:** Executable code on a blockchain that automatically
enforces contract terms. Consider audit requirements before integrating;
many jurisdictions require smart contract code audits for financial products.

**Gas Fees:** The cost to execute transactions on proof-of-stake blockchains
(Ethereum, etc.). Document gas fee variability and user impact in your
documentation.
```

---

## Regulatory and Compliance Writing

### 1. Compliance-Ready Documentation Template

```markdown
# [System/Feature Name] - Compliance Documentation

## Executive Summary
[1-2 paragraph business description]

## Regulatory Scope
**Applicable Regulations:**
- [Regulation 1] - [why applicable] - [jurisdiction]
- [Regulation 2] - [why applicable] - [jurisdiction]

## Functional Requirements
[What the system does in business terms]

## Technical Controls
**Data Processing:**
- [What data is collected]
- [Where it's stored]
- [How long it's retained]
- [Who can access it]

**Security Controls:**
- [Encryption standards]
- [Access control mechanisms]
- [Audit logging approach]
- [Incident response procedures]

## Compliance Evidence
- [System logs with timestamps]
- [Access control matrix]
- [Encryption key rotation logs]
- [Audit trail examples]

## Testing and Validation
**Test Case 1:** [Describe specific compliance test]
**Result:** [Demonstrate compliance]

**Test Case 2:** [Additional scenario]
**Result:** [Demonstrate compliance]

## Approval and Sign-off
[Who verified compliance and when]
```

### 2. Risk and Compliance Statement Examples

**For Data Security:**
```markdown
This system processes customer PII (personally identifiable information)
including name, email, phone, and financial account information.
Processing is limited to [specific business purpose]. Data is encrypted
with AES-256-GCM in transit and at rest. Access is restricted to
[specific roles] and logged in [audit system]. Retention follows [policy],
with secure deletion after [timeframe] per [regulation].
```

**For AML/KYC Compliance:**
```markdown
This feature supports AML/KYC compliance for [jurisdiction] requirements.
The system automatically flags transactions exceeding [threshold] for
review. Customers triggering KYC requirements must complete identity
verification via [method] within [timeframe]. Failed verification results
in account restrictions per [regulation].
```

**For Regulatory Reporting:**
```markdown
This system generates regulatory reports for [agency] per [regulation].
Reports are generated automatically on [schedule], with manual override
capability for [reason]. Report accuracy is verified through [process].
Failed reports trigger [notification procedure].
```

---

## Security and Risk Communication

### 1. Vulnerability Disclosure Language

**When Documenting Known Issues:**

```markdown
**Known Limitation - Transaction Rate Limits**

During high-volume periods (typically Friday 4-5 PM ET), the transaction
processing queue may have latency exceeding our standard SLA. This is a
capacity limitation, not a security vulnerability. We are implementing
[mitigation strategy] scheduled for [date].

**Workaround:** Batch off-peak transactions when possible. Implement
exponential backoff retry logic with jitter (retry after 2s, 4s, 8s, etc.).

**Status:** [In Progress | Planned | Investigating]
**Target Resolution:** [Date]
```

**When Documenting Security Best Practices:**

```markdown
**Security Consideration - API Key Rotation**

API keys are subject to compromise through multiple attack vectors
(accidental exposure, insider threat, supply chain attack). While no
rotation period eliminates compromise risk entirely, we recommend:

- **Quarterly rotation** for production keys
- **Annual rotation minimum** for non-production keys
- **Immediate rotation** upon any suspected compromise
- **Automated rotation** via dashboard (recommended)

**Implementation:** Existing requests using a rotated key will fail with
HTTP 401 immediately after rotation.
```

### 2. Handling Sensitive Examples

**Never Use Real Data:**
```markdown
INCORRECT (Real data):
"Use API key sk_live_XXXXXXXXXXXXXXXXXXXX for testing..."

CORRECT (Masked format):
"Use API key sk_live_** (visible in Dashboard under Settings > API Keys)"

CORRECT (Clearly labeled test data):
"For testing in sandbox, use test API key sk_test_**REDACTED**.
This key will only interact with test resources."
```

### 3. Breach and Incident Communication

**For Documentation About Incident Response:**

```markdown
## Incident Response Procedures

**Detection:** [System that detects the issue]
**Immediate Actions (0-30 minutes):**
1. [Containment step]
2. [Notification step]
3. [Evidence preservation step]

**Investigation (30 minutes - 24 hours):**
1. [Analysis step]
2. [Scope determination]
3. [Root cause identification]

**Communication Timeline:**
- Within 1 hour: Internal team notification
- Within 4 hours: Customer notification (if data exposure)
- Within 72 hours: Regulatory notification (if required)
- Within 5 business days: Written incident report

**Recovery:** [Steps to remediation]

**Post-Incident:** [Process improvements and root cause fixes]
```

---

## API Documentation Standards

### 1. Endpoint Documentation Template

```markdown
## [HTTP Method] [Endpoint Path]

**Availability:** [Sandbox | Production | Both]
**Rate Limit:** [Requests per window]
**Authentication:** [Type - e.g., "API Key in header"]
**Webhook:** [If applicable - webhook event name]

### Description
[Business purpose in 2-3 sentences]

### Request

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {api_key}
Idempotency-Key: {uuid}  # Prevent duplicate processing
```

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `account_id` | UUID | Unique account identifier |

**Query Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `limit` | integer | No | Records per page (1-100, default 20) |
| `created_after` | ISO 8601 | No | Filter to transactions after date |

**Request Body:**
```json
{
  "amount_usd": 10000.50,
  "currency": "USD",
  "customer_id": "cust_abc123",
  "idempotency_key": "uuid-unique-per-request"
}
```

**Validation Rules:**
- `amount_usd`: Must be > 0, max 2 decimal places
- `currency`: Must be valid ISO 4217 code
- `customer_id`: Must exist in system
- `idempotency_key`: If duplicate key sent within 24 hours, return cached response

### Response

**Success Response (200):**
```json
{
  "transaction_id": "txn_abc123xyz",
  "status": "captured",
  "amount_usd": 10000.50,
  "created_at": "2025-11-19T14:30:00Z",
  "settled_at": "2025-11-21T09:15:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "invalid_amount",
  "code": "INVALID_REQUEST",
  "message": "Amount must have maximum 2 decimal places",
  "field": "amount_usd"
}
```

### Error Codes

| Code | HTTP | Meaning | Mitigation |
| --- | --- | --- | --- |
| `invalid_amount` | 400 | Amount format invalid | Validate decimals |
| `insufficient_funds` | 402 | Account lacks funds | Retry after deposit |
| `rate_limited` | 429 | Exceeded rate limit | Implement exponential backoff |
| `server_error` | 500 | Temporary server issue | Retry with idempotency key |

### Webhook Event

```
event_type: "transaction.settled"
payload: {...response body above...}
signature: "sha256=..." # HMAC-SHA256 of payload
```

### Examples

**Python:**
```python
import requests

response = requests.post(
    'https://api.example.com/v1/transactions',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Idempotency-Key': str(uuid.uuid4())
    },
    json={
        'amount_usd': 10000.50,
        'currency': 'USD',
        'customer_id': 'cust_abc123'
    }
)

if response.status_code == 200:
    transaction = response.json()
    print(f"Transaction {transaction['transaction_id']} captured")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**cURL:**
```bash
curl -X POST https://api.example.com/v1/transactions \
  -H "Authorization: Bearer sk_live_**" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "amount_usd": 10000.50,
    "currency": "USD",
    "customer_id": "cust_abc123"
  }'
```
```

### 2. Webhook Documentation Template

```markdown
## Webhook Events

**Signature Verification:** All webhooks include `X-Signature` header
(HMAC-SHA256 of request body with your signing secret)

### Event: transaction.created

**When Triggered:** Immediately when transaction request is received
**Retry Logic:** [How many retries, what triggers manual retry]
**Guaranteed Delivery:** No (webhook may be lost; use polling as backup)

**Payload:**
```json
{
  "event_id": "evt_abc123",
  "event_type": "transaction.created",
  "created_at": "2025-11-19T14:30:00Z",
  "data": {
    "transaction_id": "txn_abc123",
    "status": "authorized",
    "amount_usd": 100.00
  }
}
```

**Signature Verification Example (Python):**
```python
import hmac
import hashlib

signature = request.headers.get('X-Signature')
body = request.body  # Raw bytes

expected_signature = hmac.new(
    webhook_secret.encode(),
    body,
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(signature, expected_signature):
    raise ValueError("Invalid webhook signature")
```
```

---

## Error Messages and User Communication

### 1. Error Message Design Principles

**Principle 1: Be Specific**
```
WRONG: "Invalid request"
RIGHT: "Amount must be between USD 0.01 and USD 999,999.99"
```

**Principle 2: Explain Why**
```
WRONG: "Authentication failed"
RIGHT: "Authentication failed: API key has insufficient permissions for this operation. Grant the 'transactions:write' scope in your dashboard."
```

**Principle 3: Provide Recovery Path**
```
WRONG: "Rate limited"
RIGHT: "Rate limited (10 requests per minute). Wait 45 seconds before retrying, or upgrade to Pro plan for 100 requests/minute."
```

### 2. Error Message Template

```
[Error Code]: [Clear Problem Statement]
Reason: [Why this happened]
Impact: [What fails because of this]
Solution: [Specific steps to fix]
Prevention: [How to avoid next time]
```

**Example:**
```
invalid_card_number: The card number you provided is not valid
Reason: The card number failed the Luhn check (invalid checksum)
Impact: Payment cannot be processed
Solution: Verify card number and try again. Use test card 4242424242424242 for testing
Prevention: Validate card format in UI before submission (format: NNNN-NNNN-NNNN-NNNN)
```

### 3. Regulatory-Sensitive Error Messages

**DO:**
- Provide enough information for the user to fix the issue
- Explain financial or compliance implications if relevant
- Suggest legitimate workarounds

**DON'T:**
- Expose internal systems or technology details
- Reveal security mechanisms (e.g., "firewall blocked request")
- Create opportunities for social engineering

**Example - AML/KYC Rejection:**
```
kyc_verification_failed: Identity verification could not be completed

Your identity verification was unsuccessful. This may occur due to:
- Document quality issues (blurry, cropped, or expired)
- Name mismatch between document and application
- Unavailable verification service in your country

Next Steps:
1. Verify your legal name matches your documents exactly
2. Provide higher-quality document images
3. Wait 24 hours (previous attempts are cached)
4. Contact support@example.com if issues persist

Note: After 3 failed attempts, additional KYC attempts require manual review.
```

---

## Examples and Case Studies

### Example 1: Payment Processing Documentation

**GOOD EXAMPLE - Complete, Compliance-Aware:**

```markdown
## Payment Processing Flow

### Step 1: Authorization Request (0-100ms)
Customer initiates payment. System sends authorization request to card network
(Visa/Mastercard) via processor. This is the point where fraud detection occurs.
Authorization does NOT move funds.

**Example Request:**
```json
{
  "type": "authorization",
  "amount_usd": 45.99,
  "currency": "USD",
  "card_token": "tok_visa",
  "merchant_id": "merchant_abc123"
}
```

**Expected Response:**
```json
{
  "authorization_id": "auth_abc123",
  "status": "approved",
  "risk_score": 12  // 0-100, higher = riskier
}
```

### Step 2: Capture (0-24 hours)
Once you confirm the customer received goods/services, you initiate capture.
This is when funds actually move. Captures can fail even if authorization
succeeded (e.g., if card was canceled in the 2 hours between authorization
and capture).

**Timing:** Most platforms auto-capture within 24 hours, but manual capture
is allowed within 30 days.

### Step 3: Settlement (1-3 business days)
The processor aggregates captures into batches and settles with banks via ACH.
This is when funds actually appear in your account. Settlement typically
occurs at a fixed time each business day (e.g., 2:00 AM ET).

**Reconciliation:** Match settlement report against your captures:
- Count: Number of transactions must match
- Amount: Total captured must match settled (within tolerance)
- Timeline: Investigate delays > 1 business day

### Failure Scenarios

**Scenario 1: Authorization Approved, Capture Fails**
Reason: Card canceled after authorization
Customer Impact: Customer isn't charged (good), may not notice attempt
Your Action: Contact customer, reprocess payment, or update billing info

**Scenario 2: Authorization Declined, Customer Retries**
Reason: Insufficient funds, fraud block, etc.
Customer Impact: Payment fails but customer may retry
Your Action: Don't auto-retry without customer confirmation (can trigger fraud)

**Scenario 3: Settlement Delay**
Reason: Holiday, processor backlog, bank delay
Your Action: Normal behavior; don't escalate immediately. Check settlement report
at 3 AM ET day after capture. Wait until EOD day 3 before escalating.
```

### Example 2: Regulatory Compliance Feature

```markdown
## Transaction Monitoring for AML Compliance

### Purpose
Federal AML regulations require financial institutions to monitor customer
transactions for suspicious patterns. This system automatically flags
transactions for review based on behavior patterns and thresholds.

### Regulatory Basis
- **31 CFR Part 1010:** AML compliance requirements (all financial institutions)
- **31 CFR 1020.320:** Bank Secrecy Act (applies to payment processors)
- **Customer Due Diligence Rule:** Know your customer requirements

### System Behavior

**Automatic Flags (Trigger Review):**
- Single transaction > USD 10,000 (Currency Transaction Report threshold)
- 5+ transactions > USD 2,000 in 24 hours (structuring pattern)
- Transaction to high-risk country (Treasury OFAC list)
- Customer matches PEP database

**Review Process:**
1. Compliance team receives alert within 15 minutes of transaction
2. Team reviews transaction context and customer history
3. Within 24 hours: Approve (allow), Escalate (report to FinCEN), or Block
4. Approved: Transaction processes normally
5. Escalated: Suspicious Activity Report (SAR) filed with FinCEN within 30 days
6. Blocked: Customer notified, transaction reversed, account may be restricted

**Documentation:**
All reviews are logged with reviewer ID, decision, reasoning. This audit
trail is preserved for 5 years per 31 CFR 1010.410.

### Customer Communication

If customer's transaction is blocked, they see:
"Your transaction was temporarily blocked for security review. Our team will
contact you within 24 hours. If you have questions, call [number]."

We do NOT tell them "flagged for AML" as this may affect their financial
relationships elsewhere.
```

---

## Accessibility and Localization

### 1. Writing for Accessibility

**Standards:** WCAG 2.1 Level AA

**Principles:**

- **Clear Language:** Use plain English, short sentences, define jargon
- **Logical Structure:** Use proper heading hierarchy (H1 > H2 > H3)
- **High Contrast:** Don't rely on color alone to convey meaning
- **Descriptive Links:** "Learn more about API keys" not "click here"
- **Alt Text for Images:** "Payment flow diagram showing three stages: auth → capture → settlement"

**Example - Accessibility-First:**

```markdown
# Transaction Status

Users can check transaction status in two ways:

## Method 1: Dashboard (Recommended)
1. Log in to your dashboard
2. Select "Transactions" from the left menu
3. Find your transaction in the list (sorted by date, newest first)
4. Status shows as "Authorized" (pending), "Captured" (processing), or "Settled" (complete)

## Method 2: API

Use the [transaction status API endpoint](./api-reference#get-transaction-status)
with your transaction ID.

### Understanding Transaction Status

- **Authorized** (blue dot): Payment approved, funds reserved for 7 days
- **Captured** (yellow dot): We received your shipment confirmation, processing funds
- **Settled** (green dot): Funds are in your account (no further action needed)

Note: On mobile, use the status filter at the top of the transactions list
for easier navigation.
```

### 2. Multi-Language Considerations

**For Financial Products:**
- Never use machine translation for regulatory content
- Have native speakers review all regulatory text
- Currency amounts must be correct for each locale (e.g., EUR 1,234.56 vs EUR 1.234,56)
- Dates must follow local standards (MM/DD/YYYY vs DD/MM/YYYY)
- Tax/regulatory content may differ significantly by jurisdiction

**Example - Locale-Aware Documentation:**

```markdown
## Supported Currencies and Regions

### United States
- Currency: USD
- Decimal Separator: . (period)
- Thousands Separator: , (comma)
- Example: USD 1,234.56
- Regulatory: All transactions subject to [US regulations]

### European Union (SEPA)
- Currency: EUR
- Decimal Separator: , (comma)
- Thousands Separator: . (period)
- Example: EUR 1.234,56
- Regulatory: All transactions subject to [EU regulations]

### India
- Currency: INR
- Decimal Separator: . (period)
- Grouping: Lakhs system (12,34,567)
- Example: INR 12,34,567.89
- Regulatory: All transactions subject to [Indian regulations]
```

---

## Review and Approval Workflows

### 1. Documentation Review Checklist

**Technical Review (by Engineering Lead):**
- [ ] Technical accuracy verified
- [ ] Code examples tested
- [ ] API specifications match implementation
- [ ] Error codes documented
- [ ] Performance implications noted

**Compliance Review (by Compliance Officer):**
- [ ] Regulatory requirements addressed
- [ ] No commitments made that violate policy
- [ ] Security implications documented
- [ ] Data handling described accurately
- [ ] Audit trail requirements clear

**Product Review (by Product Manager):**
- [ ] Feature description matches roadmap
- [ ] Limitations clearly stated
- [ ] Competitive positioning appropriate
- [ ] Use cases realistic

**Security Review (by Security Officer):**
- [ ] No security mechanisms disclosed
- [ ] Examples don't expose keys/secrets
- [ ] Encryption standards documented
- [ ] Threat model appropriate

### 2. Version Control and Approval

```markdown
# Documentation Title

**Version:** 2.1.0
**Status:** Approved for Production
**Last Reviewed:** 2025-11-19

## Approval Chain

| Role | Name | Approval Date | Notes |
| --- | --- | --- | --- |
| Technical Lead | [Name] | 2025-11-18 | Verified code examples |
| Compliance | [Name] | 2025-11-19 | No regulatory concerns |
| Security | [Name] | 2025-11-18 | Approved threat model |
| Product | [Name] | 2025-11-19 | Ready for launch |

## Version History

**v2.1.0** (2025-11-19) - Added GDPR compliance section
**v2.0.0** (2025-11-01) - Complete rewrite for API v2
**v1.5.0** (2025-09-15) - Added webhook examples

## Change Log

### Changed
- Updated encryption standard from AES-256-CBC to AES-256-GCM
- Added examples for EU GDPR compliance
- Clarified settlement timeline (was 2-4 days, now 1-3 days for most processors)

### Added
- Webhook signature verification section
- AML/KYC compliance requirements
- Regional compliance variations

### Deprecated
- API v1 endpoints (sunset date: 2026-01-01)
```

---

## Summary

This technical writing guide establishes the standards for all FinTech documentation. Key principles are:

1. **Accuracy is non-negotiable** - Precision over brevity
2. **Compliance-first** - Address regulatory requirements explicitly
3. **Audience-aware** - Document for developers, ops, compliance, and stakeholders
4. **Security-conscious** - Never expose keys, be transparent about risk
5. **Accessible** - Clear language, proper formatting, high contrast
6. **Well-reviewed** - Technical, compliance, security, and product approval required

Following this guide ensures documentation that serves users effectively, protects the organization legally, and maintains the security and compliance standards required in financial services.
