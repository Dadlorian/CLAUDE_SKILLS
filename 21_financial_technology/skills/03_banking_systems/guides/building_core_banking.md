# Building Core Banking Systems

## Overview
This guide covers architecture, design patterns, and implementation considerations for building modern core banking systems that support retail, commercial, and corporate banking operations.

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────┐
│           Customer Channels                          │
│  (Web, Mobile, Branch, ATM, Call Center)            │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           API Gateway & Auth                         │
│  (OAuth 2.0, Rate Limiting, Validation)            │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│           Core Banking Services (Microservices)                  │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│ Account      │ Transaction  │ Ledger       │ Payment          │
│ Management   │ Processing   │ Engine       │ Processing       │
├──────────────┼──────────────┼──────────────┼──────────────────┤
│ Lending      │ Deposit      │ Interest     │ Fee              │
│ Services     │ Products     │ Calculation  │ Management       │
└──────────────┴──────────────┴──────────────┴──────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│    Data Layer (PostgreSQL, TimescaleDB)             │
│  - Core accounts, transactions, ledgers             │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Integration Layer                          │
│  (Payment Networks, Clearing, Settlement)           │
└─────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Account Management Service
```
Responsibilities:
├── Customer account creation
├── Account hierarchy management
├── Account status management
├── Product assignment
├── Account closure
├── Access control
└── Interest rate management

API Endpoints:
├── POST /accounts (create)
├── GET /accounts/{id} (retrieve)
├── PUT /accounts/{id} (update)
├── DELETE /accounts/{id} (close)
└── PATCH /accounts/{id}/status (status change)
```

#### 2. Ledger Engine
```
Responsibilities:
├── Double-entry accounting
├── Journal entry creation
├── Balance calculation
├── GL account management
├── Sub-ledger management
├── Multi-currency support
└── Reconciliation

Features:
├── Immutable transaction logs
├── Real-time balance updates
├── Atomic multi-account updates
├── Period-based accounting
└── Audit trail
```

#### 3. Transaction Processing
```
Responsibilities:
├── Transaction validation
├── Authorization
├── Processing
├── Posting to ledger
├── Settlement
├── Error handling
└── Reversal/correction

States:
├── INITIATED → PENDING → POSTED → SETTLED
└── FAILED/REVERSED (terminal states)
```

#### 4. Payment Engine
```
Responsibilities:
├── Payment initiation
├── Payment channel routing
├── Fraud detection
├── Rate limiting
├── Idempotency handling
├── Payment reconciliation
└── Settlement

Channels:
├── ACH (batch)
├── Wire (real-time)
├── SEPA (EU)
├── Card networks
├── In-bank transfers
└── International (SWIFT)
```

## Technology Stack

### Backend
```
Language: Python or Java
├── Python: FastAPI, async, rapid development
└── Java: Spring Boot, enterprise, scalability

Database:
├── PostgreSQL: Transactional data, ACID
├── TimescaleDB: Time-series data
├── Redis: Caching, session management
└── Elasticsearch: Search and analytics

Message Queue:
├── Kafka: Event streaming, high-volume
├── RabbitMQ: Reliable messaging
└── AWS SQS: Managed queueing

API Gateway:
├── Kong: Full-featured, open-source
├── AWS API Gateway: Managed service
└── Custom: Using Spring Cloud Gateway
```

### Infrastructure
```
Containerization:
├── Docker: Application containers
├── Kubernetes: Orchestration

Cloud:
├── AWS: EC2, RDS, S3, Lambda
├── Azure: App Service, SQL Database
└── GCP: Compute Engine, Cloud SQL

CI/CD:
├── Jenkins: On-premise automation
├── GitHub Actions: Cloud-native
└── GitLab CI: Integrated
```

## Data Design

### Account Schema
```sql
CREATE TABLE accounts (
    account_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- CHECKING, SAVINGS, etc
    account_number VARCHAR(20) UNIQUE,
    account_name VARCHAR(255),
    status VARCHAR(20) NOT NULL, -- ACTIVE, SUSPENDED, CLOSED
    current_balance DECIMAL(19,2),
    available_balance DECIMAL(19,2),
    currency_code VARCHAR(3),
    product_id UUID,
    opened_date TIMESTAMP,
    closed_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_account_number (account_number),
    INDEX idx_status (status)
);
```

### Ledger Schema
```sql
CREATE TABLE ledger_entries (
    entry_id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    gl_account_id UUID NOT NULL,
    transaction_id UUID,
    entry_date DATE,
    posting_date TIMESTAMP,
    debit_amount DECIMAL(19,2),
    credit_amount DECIMAL(19,2),
    description VARCHAR(255),
    posted_by VARCHAR(100),
    approved_by VARCHAR(100),
    status VARCHAR(20), -- POSTED, REVERSED, etc
    created_at TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_gl_account_id (gl_account_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_entry_date (entry_date)
);
```

## Implementation Patterns

### Double-Entry Accounting Pattern
```python
class LedgerEntry:
    def __init__(self, account_id, gl_account, debit, credit):
        self.account_id = account_id
        self.gl_account = gl_account
        self.debit = debit
        self.credit = credit

    @property
    def is_balanced(self):
        return self.debit == self.credit

    def post(self, description):
        # Insert both debit and credit entries
        # Ensure atomicity
        # Update balances
        pass

# Example: Customer deposit
deposit_entry = LedgerEntry(
    account_id="acc-001",
    gl_account="1000", # Cash
    debit=Decimal("1000.00"),
    credit=Decimal("0.00")
)

liability_entry = LedgerEntry(
    account_id="acc-001",
    gl_account="2100", # Customer deposits
    debit=Decimal("0.00"),
    credit=Decimal("1000.00")
)
```

### Transaction State Machine Pattern
```python
from enum import Enum
from datetime import datetime

class TransactionState(Enum):
    INITIATED = 1
    PENDING = 2
    POSTED = 3
    SETTLED = 4
    FAILED = 5
    REVERSED = 6

class Transaction:
    def __init__(self, transaction_id, amount, from_account, to_account):
        self.transaction_id = transaction_id
        self.amount = amount
        self.from_account = from_account
        self.to_account = to_account
        self.state = TransactionState.INITIATED
        self.created_at = datetime.now()

    def validate(self):
        # Check balance, limits, compliance
        # Return True/False
        pass

    def authorize(self):
        if self.validate():
            self.state = TransactionState.PENDING
            return True
        self.state = TransactionState.FAILED
        return False

    def post(self):
        if self.state != TransactionState.PENDING:
            raise InvalidTransactionStateError()
        # Create ledger entries
        self.state = TransactionState.POSTED

    def settle(self):
        if self.state != TransactionState.POSTED:
            raise InvalidTransactionStateError()
        # Settle with external parties
        self.state = TransactionState.SETTLED
```

### Idempotent Payment Pattern
```python
class PaymentIdempotency:
    @staticmethod
    def create_or_get(idempotency_key, payment_fn):
        """
        Ensure payment is processed exactly once
        """
        existing = db.query(IdempotencyRecord).filter_by(
            key=idempotency_key
        ).first()

        if existing:
            # Return previous result
            return existing.result

        # Process payment
        result = payment_fn()

        # Store idempotency record
        record = IdempotencyRecord(
            key=idempotency_key,
            result=result,
            created_at=datetime.now()
        )
        db.add(record)
        db.commit()

        return result

# Usage:
result = PaymentIdempotency.create_or_get(
    idempotency_key="pay-unique-key-001",
    payment_fn=lambda: initiate_payment(account, amount)
)
```

## Key Considerations

### Performance
```
Optimization Strategies:
├── Real-time balance calculation
│   ├── Maintain running balance
│   ├── Update on each transaction
│   └── Index for quick access
│
├── Caching
│   ├── Cache account details (Redis)
│   ├── Cache GL account structure
│   ├── Cache interest rates
│   └── 5-minute cache with TTL
│
├── Query Optimization
│   ├── Composite indexes on common queries
│   ├── Partitioning ledger by date
│   ├── Materialized views for reports
│   └── Batch processing for low-priority tasks
│
└── Concurrency
    ├── Optimistic locking for account updates
    ├── Pessimistic locking for critical sections
    ├── Queue for high-volume transactions
    └── Rate limiting at API gateway
```

### Reliability
```
High Availability:
├── Multi-region replication
├── Automatic failover
├── Load balancing
├── Circuit breakers
└── Graceful degradation

Data Integrity:
├── ACID transactions
├── Referential integrity constraints
├── Periodic reconciliation
├── Audit trails
└── Backup and recovery procedures
```

### Compliance
```
Regulatory Requirements:
├── Immutable audit logs
├── Transaction tracking
├── KYC/AML integration
├── PSD2 compliance
├── GDPR data handling
├── Data retention policies
└── Regulatory reporting
```

## Best Practices

### Code Quality
```
Standards:
├── >85% test coverage
├── Unit tests for business logic
├── Integration tests for components
├── End-to-end tests for flows
├── Load testing under expected volumes
├── Security scanning
└── Code reviews before merge
```

### Deployment
```
Strategy:
├── Blue-green deployments
├── Canary releases (1% → 10% → 100%)
├── Instant rollback capability
├── Zero-downtime migrations
├── Data migration procedures
└── Regular disaster recovery testing
```

### Monitoring
```
Key Metrics:
├── Transaction volume and success rate
├── API response times (P50, P95, P99)
├── System availability/uptime
├── Error rates by type
├── Database query performance
├── Memory and CPU utilization
└── Number of active users
```

## Conclusion
Building core banking systems requires careful attention to architecture, data design, transaction handling, and regulatory compliance. Modern approaches using microservices, APIs, and cloud infrastructure can provide scalability and flexibility while maintaining the reliability and security essential for banking.
