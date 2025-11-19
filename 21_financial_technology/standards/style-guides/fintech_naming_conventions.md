# FinTech Naming Conventions Style Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-19
**Scope:** Variable, Function, API, Database, and System Naming
**Industry Alignment:** Stripe, Square, PayPal, Bloomberg standards

---

## Table of Contents

1. [Introduction](#introduction)
2. [General Naming Principles](#general-naming-principles)
3. [Financial Entity Naming](#financial-entity-naming)
4. [Payment-Specific Naming](#payment-specific-naming)
5. [Trading System Naming](#trading-system-naming)
6. [Database Naming](#database-naming)
7. [API Endpoint Naming](#api-endpoint-naming)
8. [Event Naming](#event-naming)
9. [ISO 20022 Compliance](#iso-20022-compliance)
10. [Anti-Patterns](#anti-patterns)
11. [References](#references)

---

## Introduction

### Purpose

Consistent naming conventions ensure:
- **Regulatory compliance** with industry standards (ISO 20022, FIX Protocol)
- **Clarity** in financial operations and audit trails
- **Interoperability** with banking and payment systems
- **Maintainability** of financial software systems

### Scope

Applies to:
- Database schemas and tables
- API endpoints and parameters
- Code variables and functions
- Event names and message types
- Configuration files
- Log entries

### Guiding Principles

1. **Clarity over brevity**: `authorization_amount` beats `auth_amt`
2. **Consistency**: Use the same term everywhere (don't mix `user` and `customer`)
3. **Industry alignment**: Follow ISO 20022, FIX, and major fintech APIs
4. **Audit-friendly**: Names should be self-documenting for compliance reviews

---

## General Naming Principles

### Case Conventions

**snake_case**: Databases, events, configuration files
```
customer_account
payment_authorization
transaction_timestamp
```

**camelCase**: JSON API request/response fields (JavaScript/TypeScript compatibility)
```json
{
  "customerId": "cus_123",
  "transactionAmount": "1000.00",
  "createdAt": "2025-11-19T10:00:00Z"
}
```

**PascalCase**: Class names, type definitions, GraphQL types
```typescript
class PaymentAuthorization {}
interface TransactionRecord {}
type AccountBalance = {...}
```

**kebab-case**: URLs, file names, resource identifiers
```
/api/v2/payment-methods
/api/v2/account-statements
transaction-processor.service.ts
```

### Abbreviation Policy

**AVOID abbreviations unless industry-standard:**

**ACCEPTABLE:**
```
id (identifier - universal)
api (application programming interface)
url (uniform resource locator)
pan (primary account number - PCI DSS term)
aml (anti-money laundering - regulatory term)
kyc (know your customer - regulatory term)
ach (automated clearing house - payment network)
eft (electronic funds transfer)
fx (foreign exchange)
p2p (peer-to-peer)
```

**AVOID:**
```
amt → amount
acct → account
txn → transaction (use "transaction" or "tx" if following blockchain conventions)
auth → authorization
cust → customer
pymnt → payment
```

### Prefix and Suffix Standards

**Entity Identifiers (following Stripe pattern):**
```
cus_     customer
acc_     account
pm_      payment method
auth_    authorization
cap_     capture
ref_     refund
xfer_    transfer
ord_     order
exec_    execution
pos_     position
stmt_    statement
```

**Temporal Suffixes:**
```
_at      timestamp (created_at, updated_at, executed_at)
_date    date only (settlement_date, trade_date)
_time    time only (cutoff_time)
_period  time range (billing_period, holding_period)
```

**Status Suffixes:**
```
_status  current state (payment_status, order_status)
_state   state machine state (authorization_state)
_result  outcome (verification_result, reconciliation_result)
```

---

## Financial Entity Naming

### Account Entities

**Account Types:**
```
checking_account
savings_account
investment_account
credit_card_account
loan_account
merchant_account
escrow_account
custody_account
```

**Account Attributes:**
```
account_id (primary identifier)
account_number (external account number, PII)
account_type (checking, savings, etc.)
account_status (active, suspended, closed)
account_balance (current balance)
available_balance (balance minus holds)
ledger_balance (balance including pending)
currency_code (ISO 4217: USD, EUR, GBP)
opened_at (account creation timestamp)
closed_at (account closure timestamp, if applicable)
```

**Example Schema:**
```sql
CREATE TABLE accounts (
  account_id UUID PRIMARY KEY,
  customer_id UUID NOT NULL REFERENCES customers(customer_id),
  account_number VARCHAR(20) NOT NULL UNIQUE,
  account_type VARCHAR(50) NOT NULL,
  account_status VARCHAR(20) NOT NULL DEFAULT 'active',
  currency_code CHAR(3) NOT NULL,
  ledger_balance DECIMAL(19, 4) NOT NULL DEFAULT 0,
  available_balance DECIMAL(19, 4) NOT NULL DEFAULT 0,
  opened_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  closed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Transaction Entities

**Transaction Types (aligned with ISO 20022):**
```
payment_transaction
transfer_transaction
deposit_transaction
withdrawal_transaction
fee_transaction
interest_transaction
dividend_transaction
adjustment_transaction
reversal_transaction
```

**Transaction Attributes:**
```
transaction_id (primary identifier)
transaction_type (payment, transfer, etc.)
transaction_status (pending, completed, failed, reversed)
transaction_timestamp (ISO 8601 with timezone)
amount (transaction amount, always positive)
currency_code (ISO 4217)
direction (debit, credit)
source_account_id
destination_account_id
description (human-readable description)
reference_number (external reference)
```

**Example:**
```sql
CREATE TABLE transactions (
  transaction_id UUID PRIMARY KEY,
  transaction_type VARCHAR(50) NOT NULL,
  transaction_status VARCHAR(20) NOT NULL,
  transaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  amount DECIMAL(19, 4) NOT NULL CHECK (amount > 0),
  currency_code CHAR(3) NOT NULL,
  direction VARCHAR(10) NOT NULL CHECK (direction IN ('debit', 'credit')),
  source_account_id UUID REFERENCES accounts(account_id),
  destination_account_id UUID REFERENCES accounts(account_id),
  description TEXT,
  reference_number VARCHAR(100),
  idempotency_key UUID UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Customer Entities

**Customer Types:**
```
individual_customer (retail customer)
business_customer (commercial entity)
institutional_customer (bank, fund, etc.)
```

**Customer Attributes:**
```
customer_id (primary identifier)
customer_type (individual, business, institutional)
customer_status (active, suspended, closed)
kyc_status (not_started, pending, verified, failed)
kyc_verified_at
risk_rating (low, medium, high)
onboarded_at
```

**Example:**
```sql
CREATE TABLE customers (
  customer_id UUID PRIMARY KEY,
  customer_type VARCHAR(20) NOT NULL,
  customer_status VARCHAR(20) NOT NULL DEFAULT 'active',
  kyc_status VARCHAR(20) NOT NULL DEFAULT 'not_started',
  kyc_verified_at TIMESTAMP WITH TIME ZONE,
  risk_rating VARCHAR(10) NOT NULL DEFAULT 'medium',
  onboarded_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## Payment-Specific Naming

### Payment Lifecycle Stages (Stripe-aligned)

**Authorization:**
```
payment_authorization
authorization_id (auth_xyz123)
authorization_amount
authorization_currency
authorization_status (authorized, expired, voided)
authorized_at
expires_at
```

**Capture:**
```
payment_capture
capture_id (cap_xyz123)
capture_amount (can be less than authorization for partial capture)
capture_currency
capture_status (succeeded, pending, failed)
captured_at
settlement_expected_at
```

**Refund:**
```
payment_refund
refund_id (ref_xyz123)
refund_amount
refund_currency
refund_reason (requested_by_customer, duplicate, fraudulent)
refund_status (pending, succeeded, failed)
refunded_at
```

**Settlement:**
```
payment_settlement
settlement_id
settlement_amount
settlement_currency
settlement_status (pending, completed, failed)
settlement_date (typically T+2 for cards)
settled_at
```

### Payment Methods (Plaid/Stripe pattern)

**Payment Method Types:**
```
card_payment_method
bank_account_payment_method
digital_wallet_payment_method (apple_pay, google_pay)
ach_payment_method
wire_payment_method
cryptocurrency_payment_method
```

**Payment Method Attributes:**
```
payment_method_id (pm_xyz123)
payment_method_type (card, bank_account, etc.)
payment_method_status (active, inactive, expired)
is_default (boolean)
verification_status (unverified, pending, verified)
verified_at
created_at
expires_at (for cards)
```

**Card-Specific (PCI DSS compliant naming):**
```
card_id
card_brand (visa, mastercard, amex, discover)
card_last4 (last 4 digits only - NEVER store full PAN)
card_exp_month
card_exp_year
card_fingerprint (hash for duplicate detection)
card_funding (credit, debit, prepaid, unknown)
cardholder_name
```

**Bank Account-Specific (ACH/EFT):**
```
bank_account_id
bank_name
routing_number (US: ABA routing number)
account_number_last4 (NEVER store full account number)
account_type (checking, savings)
account_holder_name
```

### Payment Flow Example

```typescript
// Authorization request
POST /api/v2/payment-authorizations
{
  "amount": "1000.00",
  "currency": "USD",
  "paymentMethodId": "pm_card_123",
  "description": "Order #12345",
  "idempotencyKey": "unique-key-123"
}

// Authorization response
{
  "authorizationId": "auth_abc123",
  "status": "authorized",
  "amount": "1000.00",
  "currency": "USD",
  "paymentMethodId": "pm_card_123",
  "authorizedAt": "2025-11-19T10:00:00Z",
  "expiresAt": "2025-11-26T10:00:00Z"
}

// Capture request
POST /api/v2/payment-captures
{
  "authorizationId": "auth_abc123",
  "amount": "1000.00",  // Can be less for partial capture
  "idempotencyKey": "unique-key-456"
}

// Capture response
{
  "captureId": "cap_def456",
  "authorizationId": "auth_abc123",
  "status": "succeeded",
  "amount": "1000.00",
  "currency": "USD",
  "capturedAt": "2025-11-19T12:00:00Z",
  "settlementExpectedAt": "2025-11-21T10:00:00Z"
}
```

---

## Trading System Naming

### Order Entities (FIX Protocol aligned)

**Order Types:**
```
market_order (immediate execution at current market price)
limit_order (execution at specified price or better)
stop_order (becomes market order when stop price reached)
stop_limit_order (becomes limit order when stop price reached)
```

**Order Attributes:**
```
order_id (ord_xyz123)
client_order_id (client-assigned identifier)
order_type (market, limit, stop, stop_limit)
order_status (new, partially_filled, filled, cancelled, rejected, expired)
side (buy, sell)
symbol (stock symbol, e.g., AAPL)
quantity (number of shares/units)
filled_quantity (number executed so far)
remaining_quantity (quantity - filled_quantity)
limit_price (for limit orders)
stop_price (for stop orders)
time_in_force (day, gtc, ioc, fok)
placed_at
expires_at
```

**FIX Protocol Field Mapping:**
```
ClOrdID → client_order_id
OrderID → order_id
OrdType → order_type (1=Market, 2=Limit, 3=Stop, 4=Stop Limit)
Side → side (1=Buy, 2=Sell)
Symbol → symbol
OrderQty → quantity
Price → limit_price
StopPx → stop_price
TimeInForce → time_in_force (0=Day, 1=GTC, 3=IOC, 4=FOK)
OrdStatus → order_status
```

### Execution Entities

**Execution Attributes:**
```
execution_id (exec_xyz123)
order_id (reference to order)
execution_type (trade, cancelled, replaced, rejected)
execution_status (new, partial_fill, fill)
executed_quantity
executed_price
execution_timestamp
liquidity_indicator (added, removed)
venue (exchange where executed: NYSE, NASDAQ, etc.)
```

**Fill Tracking:**
```
fill_id
execution_id
fill_quantity
fill_price
fill_timestamp
commission_amount
commission_currency
```

### Position Entities

**Position Tracking:**
```
position_id
account_id
symbol
quantity (positive for long, negative for short)
average_cost_basis
market_value
unrealized_pnl (profit and loss)
realized_pnl
position_opened_at
position_updated_at
```

**Example:**
```sql
CREATE TABLE positions (
  position_id UUID PRIMARY KEY,
  account_id UUID NOT NULL REFERENCES accounts(account_id),
  symbol VARCHAR(10) NOT NULL,
  quantity DECIMAL(19, 8) NOT NULL,  -- Can be fractional, negative for shorts
  average_cost_basis DECIMAL(19, 4),
  market_value DECIMAL(19, 4),
  unrealized_pnl DECIMAL(19, 4),
  realized_pnl DECIMAL(19, 4),
  position_opened_at TIMESTAMP WITH TIME ZONE NOT NULL,
  position_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE(account_id, symbol)
);
```

---

## Database Naming

### Table Naming

**Plural nouns for tables:**
```sql
customers
accounts
transactions
payment_authorizations
payment_captures
orders
executions
positions
```

**Join tables (alphabetical order):**
```sql
account_payment_methods (not payment_method_accounts)
customer_addresses
order_executions
```

**Temporal tables (audit/history):**
```sql
customers_history
accounts_audit
transactions_archive
```

### Column Naming

**Primary Keys:**
```sql
{table_name_singular}_id
customer_id
account_id
transaction_id
```

**Foreign Keys:**
```sql
{referenced_table_singular}_id
customer_id (FK to customers.customer_id)
source_account_id (FK to accounts.account_id)
destination_account_id (FK to accounts.account_id)
```

**Booleans (prefix with is_, has_, can_):**
```sql
is_active
is_verified
is_default
has_mfa_enabled
can_trade_options
```

**Timestamps:**
```sql
created_at (record creation time)
updated_at (last modification time)
deleted_at (soft delete timestamp)
verified_at (verification completion time)
executed_at (execution timestamp)
settled_at (settlement timestamp)
```

**Monetary Amounts:**
```sql
-- Always pair amount with currency
amount DECIMAL(19, 4)
currency_code CHAR(3)

-- Specific amounts
authorization_amount
capture_amount
refund_amount
transaction_amount
```

### Index Naming

**Pattern:** `idx_{table}_{columns}[_{unique}]`

```sql
CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_timestamp ON transactions(transaction_timestamp);
CREATE UNIQUE INDEX idx_transactions_idempotency_key ON transactions(idempotency_key);
CREATE INDEX idx_orders_symbol_status ON orders(symbol, order_status);
```

### Constraint Naming

**Pattern:** `{type}_{table}_{columns}`

```sql
-- Primary key
ALTER TABLE customers ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);

-- Foreign key
ALTER TABLE accounts ADD CONSTRAINT fk_accounts_customer_id
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- Unique
ALTER TABLE customers ADD CONSTRAINT uq_customers_email UNIQUE (email);

-- Check
ALTER TABLE transactions ADD CONSTRAINT chk_transactions_amount_positive
  CHECK (amount > 0);
```

---

## API Endpoint Naming

### RESTful Endpoint Structure

**Pattern:** `/api/{version}/{resource-plural}[/{id}][/{sub-resource-plural}]`

**Core Resources:**
```
GET    /api/v2/customers
POST   /api/v2/customers
GET    /api/v2/customers/{customer_id}
PATCH  /api/v2/customers/{customer_id}
DELETE /api/v2/customers/{customer_id}

GET    /api/v2/accounts
POST   /api/v2/accounts
GET    /api/v2/accounts/{account_id}
GET    /api/v2/accounts/{account_id}/transactions
GET    /api/v2/accounts/{account_id}/statements
```

**Payment Operations:**
```
POST   /api/v2/payment-authorizations
GET    /api/v2/payment-authorizations/{authorization_id}
POST   /api/v2/payment-authorizations/{authorization_id}/capture
POST   /api/v2/payment-authorizations/{authorization_id}/void

POST   /api/v2/payment-captures
GET    /api/v2/payment-captures/{capture_id}

POST   /api/v2/refunds
GET    /api/v2/refunds/{refund_id}

GET    /api/v2/payment-methods
POST   /api/v2/payment-methods
GET    /api/v2/payment-methods/{payment_method_id}
DELETE /api/v2/payment-methods/{payment_method_id}
```

**Trading Operations:**
```
POST   /api/v2/orders
GET    /api/v2/orders
GET    /api/v2/orders/{order_id}
DELETE /api/v2/orders/{order_id}  (cancel order)
PATCH  /api/v2/orders/{order_id}  (modify order)

GET    /api/v2/orders/{order_id}/executions
GET    /api/v2/executions
GET    /api/v2/executions/{execution_id}

GET    /api/v2/positions
GET    /api/v2/positions/{position_id}
```

**Account Operations:**
```
POST   /api/v2/transfers
GET    /api/v2/transfers/{transfer_id}

POST   /api/v2/deposits
GET    /api/v2/deposits/{deposit_id}

POST   /api/v2/withdrawals
GET    /api/v2/withdrawals/{withdrawal_id}
```

### Query Parameters

**Use snake_case for query parameters:**
```
GET /api/v2/transactions?account_id=acc_123&start_date=2025-01-01&end_date=2025-12-31
GET /api/v2/orders?symbol=AAPL&order_status=filled&limit=100&offset=0
GET /api/v2/customers?kyc_status=verified&created_after=2025-01-01T00:00:00Z
```

**Pagination:**
```
limit (number of results per page)
offset (number of results to skip)
page (page number, if using page-based pagination)
cursor (for cursor-based pagination)
```

**Filtering:**
```
{field}_eq (equals)
{field}_gt (greater than)
{field}_gte (greater than or equal)
{field}_lt (less than)
{field}_lte (less than or equal)
{field}_in (in list)

Example:
/api/v2/transactions?amount_gte=1000&amount_lte=5000&status_in=completed,pending
```

---

## Event Naming

### Event Naming Pattern

**Pattern:** `{domain}.{entity}.{action}`

**Payment Events:**
```
payment.authorization.created
payment.authorization.expired
payment.authorization.voided
payment.capture.succeeded
payment.capture.failed
payment.refund.created
payment.refund.succeeded
payment.refund.failed
payment.settlement.pending
payment.settlement.completed
```

**Account Events:**
```
account.created
account.updated
account.suspended
account.closed
account.balance.updated
account.balance.insufficient
```

**Customer Events:**
```
customer.created
customer.updated
customer.kyc.started
customer.kyc.completed
customer.kyc.failed
customer.risk_rating.changed
```

**Order Events:**
```
order.created
order.updated
order.partially_filled
order.filled
order.cancelled
order.rejected
order.expired
```

**Transfer Events:**
```
transfer.created
transfer.pending
transfer.completed
transfer.failed
transfer.reversed
```

### Event Payload Structure

```json
{
  "eventId": "evt_1a2b3c4d5e6f",
  "eventType": "payment.capture.succeeded",
  "eventTimestamp": "2025-11-19T14:30:45.123Z",
  "apiVersion": "v2",
  "data": {
    "object": {
      "id": "cap_xyz123",
      "object": "capture",
      "authorizationId": "auth_abc123",
      "amount": "1000.00",
      "currency": "USD",
      "status": "succeeded",
      "capturedAt": "2025-11-19T14:30:45Z",
      "settlementExpectedAt": "2025-11-21T10:00:00Z"
    },
    "previousAttributes": {
      "status": "pending"
    }
  },
  "metadata": {
    "accountId": "acc_123",
    "customerId": "cus_456",
    "orderId": "ord_789"
  }
}
```

---

## ISO 20022 Compliance

### Message Naming (ISO 20022 Standard)

**Payment Initiation:**
```
pain.001 (CustomerCreditTransferInitiation)
pain.002 (CustomerPaymentStatusReport)
pain.008 (CustomerDirectDebitInitiation)
```

**Account Management:**
```
acmt.001 (AccountOpeningInstruction)
acmt.002 (AccountDetailsConfirmation)
acmt.003 (AccountModificationInstruction)
```

**Cash Management:**
```
camt.053 (BankToCustomerStatement)
camt.054 (BankToCustomerDebitCreditNotification)
camt.060 (AccountReportingRequest)
```

### ISO 20022 Element Mapping

**When implementing ISO 20022 compliance, map internal names to standard elements:**

```typescript
// Internal representation
interface Transfer {
  transferId: string;
  amount: string;
  currency: string;
  debtorAccountId: string;
  creditorAccountId: string;
  remittanceInfo: string;
}

// ISO 20022 pain.001 mapping
function toISO20022Pain001(transfer: Transfer) {
  return {
    CstmrCdtTrfInitn: {  // CustomerCreditTransferInitiation
      GrpHdr: {  // GroupHeader
        MsgId: transfer.transferId,
        CreDtTm: new Date().toISOString()
      },
      PmtInf: {  // PaymentInformation
        PmtInfId: transfer.transferId,
        PmtMtd: 'TRF',  // Transfer
        ReqdExctnDt: new Date().toISOString(),
        Dbtr: {  // Debtor
          Id: transfer.debtorAccountId
        },
        CdtTrfTxInf: {  // CreditTransferTransactionInformation
          Amt: {  // Amount
            InstdAmt: {
              value: transfer.amount,
              Ccy: transfer.currency
            }
          },
          Cdtr: {  // Creditor
            Id: transfer.creditorAccountId
          },
          RmtInf: {  // RemittanceInformation
            Ustrd: transfer.remittanceInfo
          }
        }
      }
    }
  };
}
```

---

## Anti-Patterns

### Anti-Pattern 1: Inconsistent Terminology

**INCORRECT:**
```sql
CREATE TABLE users (user_id UUID PRIMARY KEY, ...);
CREATE TABLE customer_accounts (customer_id UUID, ...);
CREATE TABLE client_profiles (client_id UUID, ...);
```

**Problem:** Three different terms (user, customer, client) for the same concept.

**CORRECT:**
```sql
CREATE TABLE customers (customer_id UUID PRIMARY KEY, ...);
CREATE TABLE customer_accounts (customer_id UUID REFERENCES customers, ...);
CREATE TABLE customer_profiles (customer_id UUID REFERENCES customers, ...);
```

### Anti-Pattern 2: Ambiguous Payment States

**INCORRECT:**
```
payment_processed (does this mean authorized? captured? settled?)
payment_completed (same issue)
payment_done
```

**CORRECT:**
```
payment_authorization_status: authorized | expired | voided
payment_capture_status: succeeded | pending | failed
payment_settlement_status: pending | completed | failed
```

### Anti-Pattern 3: Abbreviated Chaos

**INCORRECT:**
```
txn_amt
cust_acct_bal
pmt_mthd_id
auth_ts
```

**CORRECT:**
```
transaction_amount
customer_account_balance
payment_method_id
authorized_at
```

### Anti-Pattern 4: Inconsistent ID Prefixes

**INCORRECT:**
```
customer123
acc_456
pm-789
authorization_abc
```

**CORRECT:**
```
cus_123
acc_456
pm_789
auth_abc
```

### Anti-Pattern 5: Mixing Singular and Plural

**INCORRECT:**
```sql
CREATE TABLE customer (...);  -- Singular
CREATE TABLE transactions (...);  -- Plural
CREATE TABLE payment_method (...);  -- Singular
```

**CORRECT:**
```sql
CREATE TABLE customers (...);
CREATE TABLE transactions (...);
CREATE TABLE payment_methods (...);
```

### Anti-Pattern 6: Generic Event Names

**INCORRECT:**
```
payment_updated (what specifically changed?)
account_changed
order_modified
```

**CORRECT:**
```
payment.capture.succeeded
payment.refund.created
account.status.changed
account.balance.updated
order.partially_filled
order.cancelled
```

### Anti-Pattern 7: Non-Standard Currency Handling

**INCORRECT:**
```sql
amount_usd DECIMAL(10, 2)
amount_eur DECIMAL(10, 2)
amount_gbp DECIMAL(10, 2)
```

**CORRECT:**
```sql
amount DECIMAL(19, 4)
currency_code CHAR(3)  -- ISO 4217
```

### Anti-Pattern 8: Ambiguous Time References

**INCORRECT:**
```
time (what time? creation? update?)
date (date of what?)
timestamp (timestamp of what?)
```

**CORRECT:**
```
created_at
updated_at
authorized_at
captured_at
settled_at
expires_at
```

---

## References

### Industry Standards

1. **ISO 20022**
   - Universal Financial Industry message scheme
   - https://www.iso20022.org/

2. **FIX Protocol**
   - Financial Information eXchange Protocol
   - https://www.fixtrading.org/

3. **ISO 4217**
   - Currency codes
   - https://www.iso.org/iso-4217-currency-codes.html

4. **PCI DSS**
   - Payment Card Industry Data Security Standard
   - https://www.pcisecuritystandards.org/

### Major Fintech API References

1. **Stripe API**
   - Industry-leading payment API naming conventions
   - https://stripe.com/docs/api

2. **Plaid API**
   - Banking and financial data API standards
   - https://plaid.com/docs/api/

3. **Square Developer Docs**
   - Payment and commerce API patterns
   - https://developer.squareup.com/

4. **PayPal Developer Docs**
   - Payment integration standards
   - https://developer.paypal.com/

5. **Adyen API**
   - Global payment platform conventions
   - https://docs.adyen.com/

### Database Standards

1. **PostgreSQL Naming Conventions**
   - https://www.postgresql.org/docs/current/sql-syntax.html

2. **SQL Style Guide (Simon Holywell)**
   - https://www.sqlstyle.guide/

### REST API Standards

1. **Google API Design Guide**
   - https://cloud.google.com/apis/design

2. **Microsoft REST API Guidelines**
   - https://github.com/microsoft/api-guidelines

3. **Zalando RESTful API Guidelines**
   - https://opensource.zalando.com/restful-api-guidelines/

---

**Document Control**

- **Owner:** Chief Technology Officer
- **Approver:** Head of Engineering
- **Review Frequency:** Quarterly
- **Next Review:** 2025-02-19
- **Version History:**
  - 1.0 (2025-11-19): Initial release

**Questions or Suggestions?**
Contact: engineering-standards@example.com
