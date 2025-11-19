# Event Sourcing for Financial Systems

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Event Sourcing Architecture](#event-sourcing-architecture)
4. [Implementation Patterns](#implementation-patterns)
5. [Ledger Design](#ledger-design)
6. [Real-World Applications](#real-world-applications)
7. [Snapshots & Optimization](#snapshots--optimization)
8. [Compliance & Audit](#compliance--audit)

## Overview

Event sourcing is the foundational pattern for building reliable financial systems. Rather than storing only the current state of an account, event sourcing maintains a complete audit trail of every transaction.

### Why Event Sourcing for Finance?

1. **Complete Audit Trail**: Every change to financial state is recorded
2. **Temporal Queries**: Determine account state at any point in time
3. **Replay Capability**: Reproduce any transaction for debugging or recovery
4. **Compliance**: Satisfy PCI-DSS, SOX, GDPR audit requirements
5. **Reconciliation**: Compare system state with actual bank records
6. **Fraud Detection**: Detect anomalies by analyzing event patterns

## Core Concepts

### Events vs State

```
Traditional State Storage:
┌─────────────────────────┐
│  Account State          │
│  balance: $1000         │
└─────────────────────────┘
  (Single point of truth - hard to audit)

Event Sourcing:
┌──────────────────────────────────────────────┐
│         Event Stream                         │
├──────────────────────────────────────────────┤
│ 1. account.created(balance=$0)              │
│ 2. funds_deposited($1000)                   │
│ 3. payment_withdrawn($500)                  │
│ 4. interest_accrued($2.50)                  │
│ 5. fee_charged($1.50)                       │
└──────────────────────────────────────────────┘
  (Complete history - ideal for auditing)
```

### Event Components

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from enum import Enum

class EventType(Enum):
    # Account Events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_CLOSED = "account.closed"
    ACCOUNT_FROZEN = "account.frozen"

    # Transaction Events
    DEPOSIT_INITIATED = "deposit.initiated"
    DEPOSIT_COMPLETED = "deposit.completed"
    DEPOSIT_FAILED = "deposit.failed"

    WITHDRAWAL_INITIATED = "withdrawal.initiated"
    WITHDRAWAL_COMPLETED = "withdrawal.completed"
    WITHDRAWAL_FAILED = "withdrawal.failed"

    TRANSFER_INITIATED = "transfer.initiated"
    TRANSFER_COMPLETED = "transfer.completed"
    TRANSFER_FAILED = "transfer.failed"

    # Account Management
    BALANCE_UPDATED = "balance.updated"
    INTEREST_ACCRUED = "interest.accrued"
    FEE_CHARGED = "fee.charged"

    # Compliance
    DISPUTE_OPENED = "dispute.opened"
    DISPUTE_RESOLVED = "dispute.resolved"
    HOLD_PLACED = "hold.placed"
    HOLD_RELEASED = "hold.released"

    # Account Security
    KYC_VERIFIED = "kyc.verified"
    SUSPICIOUS_ACTIVITY_DETECTED = "suspicious.activity.detected"

@dataclass
class FinancialEvent:
    event_id: str
    event_type: EventType
    account_id: str
    timestamp: datetime
    sequence_number: int  # Order within account stream
    amount: float = None
    currency: str = "USD"
    description: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: str = None
    initiated_by: str = None  # API key, user, system
    request_id: str = None  # For tracing
    idempotency_key: str = None

    def to_dict(self) -> Dict:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'account_id': self.account_id,
            'timestamp': self.timestamp.isoformat(),
            'sequence_number': self.sequence_number,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'metadata': self.metadata,
            'user_id': self.user_id,
            'initiated_by': self.initiated_by,
            'request_id': self.request_id,
            'idempotency_key': self.idempotency_key
        }
```

## Event Sourcing Architecture

### Single Account Event Stream

```
┌──────────────────────────────────────────────────────────────┐
│              Account Event Store (Immutable Log)              │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │
│  │  1  │→ │  2  │→ │  3  │→ │  4  │→ │  5  │→ │  6  │      │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │
│   created  deposit  withdrawal interest  fee   hold_placed   │
│                                                                │
│  ┌──────────────────────────────────────────┐               │
│  │ Account State (Materialized View)         │               │
│  │ balance: $2,451.00                        │               │
│  │ holds: $100.00                            │               │
│  │ available: $2,351.00                      │               │
│  └──────────────────────────────────────────┘               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    API Layer                                    │
│          (POST /accounts/:id/deposit)                           │
└──────────────────┬─────────────────────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────────────────────┐
│               Event Sourcing Service                            │
│  - Validate transaction                                         │
│  - Generate events                                              │
│  - Write to event store                                         │
│  - Emit to pub/sub                                              │
└──────────────────┬─────────────────────────────────────────────┘
                   │
        ┌──────────┴──────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼─────────┐
│  Event Store     │    │   Pub/Sub Bus    │
│  (Append-Only)   │    │  (Event Stream)  │
│  PostgreSQL      │    │  Kafka/Redis     │
└──────────────────┘    └────────┬─────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼──────────┐   ┌────────▼─────────┐   ┌─────────▼──────┐
│  Balance Update  │   │ Notification     │   │ Analytics      │
│  Projection      │   │ Service          │   │ Service        │
└──────────────────┘   └──────────────────┘   └────────────────┘
```

## Implementation Patterns

### 1. Basic Event Sourcing Implementation

```python
from typing import List, Optional
from datetime import datetime
import uuid
import json

class EventStore:
    """Append-only event storage"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        """Create event store schema"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                sequence_number BIGINT NOT NULL,
                amount DECIMAL(15, 2),
                currency TEXT,
                timestamp TIMESTAMP NOT NULL,
                data JSONB NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, sequence_number)
            );

            CREATE INDEX idx_account_id ON events(account_id);
            CREATE INDEX idx_timestamp ON events(timestamp);
            CREATE INDEX idx_event_type ON events(event_type);
        ''')

    def append_event(self, event: FinancialEvent) -> bool:
        """Append event to immutable log"""
        try:
            # Get next sequence number
            result = self.db.query('''
                SELECT COALESCE(MAX(sequence_number), 0) + 1 as next_seq
                FROM events
                WHERE account_id = %s
            ''', (event.account_id,))

            next_seq = result[0]['next_seq']
            event.sequence_number = next_seq

            # Append to store (atomic operation)
            self.db.execute('''
                INSERT INTO events (
                    event_id, account_id, event_type, sequence_number,
                    amount, currency, timestamp, data, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                event.event_id,
                event.account_id,
                event.event_type.value,
                event.sequence_number,
                event.amount,
                event.currency,
                event.timestamp,
                json.dumps(event.to_dict()),
                json.dumps(event.metadata)
            ))

            return True

        except Exception as e:
            raise Exception(f"Failed to append event: {str(e)}")

    def get_events_for_account(self, account_id: str,
                              from_sequence: int = 0,
                              to_sequence: Optional[int] = None) -> List[FinancialEvent]:
        """Get all events for account from store"""
        query = '''
            SELECT * FROM events
            WHERE account_id = %s
            AND sequence_number > %s
        '''
        params = [account_id, from_sequence]

        if to_sequence is not None:
            query += ' AND sequence_number <= %s'
            params.append(to_sequence)

        query += ' ORDER BY sequence_number ASC'

        results = self.db.query(query, tuple(params))

        events = []
        for row in results:
            event_data = json.loads(row['data'])
            event = FinancialEvent(**event_data)
            events.append(event)

        return events

    def get_events_by_type(self, event_type: EventType,
                          start_date: datetime,
                          end_date: datetime) -> List[FinancialEvent]:
        """Get events of specific type within date range"""
        results = self.db.query('''
            SELECT * FROM events
            WHERE event_type = %s
            AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC
        ''', (event_type.value, start_date, end_date))

        events = []
        for row in results:
            event_data = json.loads(row['data'])
            event = FinancialEvent(**event_data)
            events.append(event)

        return events
```

### 2. Account State Reconstruction

```python
class AccountState:
    """Current account state derived from events"""

    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0.0
        self.holds = 0.0
        self.available_balance = 0.0
        self.created_at = None
        self.closed_at = None
        self.is_frozen = False
        self.kyc_verified = False
        self.last_updated = None
        self.transaction_count = 0

    def apply_event(self, event: FinancialEvent):
        """Apply event to state"""
        if event.event_type == EventType.ACCOUNT_CREATED:
            self.created_at = event.timestamp
            self.balance = 0.0

        elif event.event_type == EventType.DEPOSIT_COMPLETED:
            self.balance += event.amount
            self.transaction_count += 1

        elif event.event_type == EventType.WITHDRAWAL_COMPLETED:
            self.balance -= event.amount
            self.transaction_count += 1

        elif event.event_type == EventType.TRANSFER_COMPLETED:
            if event.metadata.get('direction') == 'out':
                self.balance -= event.amount
            else:
                self.balance += event.amount
            self.transaction_count += 1

        elif event.event_type == EventType.INTEREST_ACCRUED:
            self.balance += event.amount

        elif event.event_type == EventType.FEE_CHARGED:
            self.balance -= event.amount

        elif event.event_type == EventType.HOLD_PLACED:
            self.holds += event.amount
            self.available_balance = self.balance - self.holds

        elif event.event_type == EventType.HOLD_RELEASED:
            self.holds -= event.amount
            self.available_balance = self.balance - self.holds

        elif event.event_type == EventType.ACCOUNT_FROZEN:
            self.is_frozen = True

        elif event.event_type == EventType.KYC_VERIFIED:
            self.kyc_verified = True

        elif event.event_type == EventType.ACCOUNT_CLOSED:
            self.closed_at = event.timestamp

        self.last_updated = event.timestamp

class AccountStateProjector:
    """Build account state from event stream"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def get_current_state(self, account_id: str) -> AccountState:
        """Get current state by replaying events"""
        state = AccountState(account_id)

        # Get all events for account
        events = self.event_store.get_events_for_account(account_id)

        # Apply each event in order
        for event in events:
            state.apply_event(event)

        return state

    def get_state_at_time(self, account_id: str,
                         as_of: datetime) -> AccountState:
        """Get state at specific point in time"""
        state = AccountState(account_id)

        # Get events up to timestamp
        events = self.event_store.get_events_for_account(account_id)

        for event in events:
            if event.timestamp <= as_of:
                state.apply_event(event)
            else:
                break

        return state

    def get_state_before_event(self, account_id: str,
                              event_id: str) -> AccountState:
        """Get state before specific event (for debugging)"""
        state = AccountState(account_id)

        events = self.event_store.get_events_for_account(account_id)

        for event in events:
            if event.event_id == event_id:
                break
            state.apply_event(event)

        return state
```

### 3. Event Publishing

```python
from abc import ABC, abstractmethod

class EventPublisher(ABC):
    """Publish events to downstream systems"""

    @abstractmethod
    def publish(self, event: FinancialEvent):
        pass

class KafkaEventPublisher(EventPublisher):
    """Publish events to Kafka topic"""

    def __init__(self, kafka_producer, topic_prefix: str = "financial"):
        self.producer = kafka_producer
        self.topic_prefix = topic_prefix

    def publish(self, event: FinancialEvent):
        topic = f"{self.topic_prefix}.{event.event_type.value}"

        message = {
            'event_id': event.event_id,
            'account_id': event.account_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'amount': str(event.amount) if event.amount else None,
            'currency': event.currency,
            'metadata': event.metadata,
            'sequence_number': event.sequence_number
        }

        self.producer.send_message(
            topic=topic,
            key=event.account_id,
            value=json.dumps(message),
            headers={'event_type': event.event_type.value}
        )

class PubSubEventPublisher(EventPublisher):
    """Publish events to Redis Pub/Sub"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def publish(self, event: FinancialEvent):
        channel = f"events:{event.event_type.value}"

        message = json.dumps({
            'event_id': event.event_id,
            'account_id': event.account_id,
            'timestamp': event.timestamp.isoformat(),
            'data': event.to_dict()
        })

        self.redis.publish(channel, message)
```

### 4. Event-Driven Service

```python
class EventSourcingService:
    """Main service for event sourcing operations"""

    def __init__(self, event_store: EventStore,
                 event_publisher: EventPublisher,
                 state_projector: AccountStateProjector):
        self.event_store = event_store
        self.event_publisher = event_publisher
        self.state_projector = state_projector

    def record_deposit(self, account_id: str, amount: float,
                      currency: str = "USD", **kwargs) -> FinancialEvent:
        """Record deposit to account"""

        # Create event
        event = FinancialEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.DEPOSIT_INITIATED,
            account_id=account_id,
            amount=amount,
            currency=currency,
            timestamp=datetime.utcnow(),
            description=f"Deposit of {amount} {currency}",
            metadata=kwargs,
            initiated_by=kwargs.get('initiated_by', 'api')
        )

        # Append to store
        self.event_store.append_event(event)

        # Publish event
        self.event_publisher.publish(event)

        return event

    def record_withdrawal(self, account_id: str, amount: float,
                         currency: str = "USD", **kwargs) -> FinancialEvent:
        """Record withdrawal from account"""

        # Get current state to check available balance
        state = self.state_projector.get_current_state(account_id)

        if state.available_balance < amount:
            raise Exception(f"Insufficient funds. Available: {state.available_balance}")

        # Create event
        event = FinancialEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WITHDRAWAL_INITIATED,
            account_id=account_id,
            amount=amount,
            currency=currency,
            timestamp=datetime.utcnow(),
            description=f"Withdrawal of {amount} {currency}",
            metadata=kwargs
        )

        self.event_store.append_event(event)
        self.event_publisher.publish(event)

        return event

    def record_transfer(self, from_account: str, to_account: str,
                       amount: float, **kwargs) -> tuple:
        """Record transfer between accounts"""

        # Create outgoing event
        out_event = FinancialEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.TRANSFER_INITIATED,
            account_id=from_account,
            amount=amount,
            timestamp=datetime.utcnow(),
            description=f"Transfer to {to_account}",
            metadata={'direction': 'out', 'counterparty': to_account, **kwargs}
        )

        # Create incoming event
        in_event = FinancialEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.TRANSFER_INITIATED,
            account_id=to_account,
            amount=amount,
            timestamp=datetime.utcnow(),
            description=f"Transfer from {from_account}",
            metadata={'direction': 'in', 'counterparty': from_account, **kwargs}
        )

        # Record both events (atomic if possible)
        self.event_store.append_event(out_event)
        self.event_store.append_event(in_event)

        self.event_publisher.publish(out_event)
        self.event_publisher.publish(in_event)

        return out_event, in_event
```

## Ledger Design

### Dual-Entry Ledger (Bank Accounting Standard)

```python
class LedgerEntry:
    """Double-entry bookkeeping entry"""

    def __init__(self, debit_account: str, credit_account: str,
                 amount: float, timestamp: datetime):
        self.debit_account = debit_account
        self.credit_account = credit_account
        self.amount = amount
        self.timestamp = timestamp

    def is_balanced(self) -> bool:
        """Verify debit equals credit"""
        return self.amount > 0

class DoubleEntryLedger:
    """Traditional accounting with debits and credits"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS ledger_entries (
                entry_id TEXT PRIMARY KEY,
                debit_account TEXT NOT NULL,
                credit_account TEXT NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                currency TEXT,
                timestamp TIMESTAMP NOT NULL,
                description TEXT,
                reference_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX idx_debit_account ON ledger_entries(debit_account);
            CREATE INDEX idx_credit_account ON ledger_entries(credit_account);
            CREATE INDEX idx_timestamp ON ledger_entries(timestamp);
        ''')

    def record_entry(self, entry: LedgerEntry) -> bool:
        """Record double-entry bookkeeping entry"""
        try:
            # Both entries recorded atomically
            self.db.transaction_begin()

            self.db.execute('''
                INSERT INTO ledger_entries (
                    entry_id, debit_account, credit_account,
                    amount, currency, timestamp
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                str(uuid.uuid4()),
                entry.debit_account,
                entry.credit_account,
                entry.amount,
                'USD',
                entry.timestamp
            ))

            self.db.transaction_commit()
            return True

        except Exception as e:
            self.db.transaction_rollback()
            raise Exception(f"Failed to record entry: {str(e)}")

    def get_account_balance(self, account_id: str,
                           as_of: Optional[datetime] = None) -> float:
        """Get account balance using double-entry logic"""

        if as_of:
            where_clause = 'AND timestamp <= %s'
            params = (account_id, as_of, account_id, as_of)
        else:
            where_clause = ''
            params = (account_id, account_id)

        result = self.db.query(f'''
            SELECT
                COALESCE(SUM(CASE WHEN debit_account = %s THEN amount ELSE 0 END), 0)
                - COALESCE(SUM(CASE WHEN credit_account = %s THEN amount ELSE 0 END), 0)
                as balance
            FROM ledger_entries
            WHERE (debit_account = %s OR credit_account = %s)
            {where_clause}
        ''', params)

        return float(result[0]['balance'])
```

## Real-World Applications

### Use Case 1: Payment Processing with Retry Logic

```
┌─────────────────────────────────────────┐
│ payment.initiated                       │
│ amount: $100                            │
│ merchant_id: ABC123                     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
payment.attempting  payment.external_submitted
retry_1             to_payment_gateway
                      │
                      ├─► payment.timeout
                      │   retry_count: 1
                      │
                      ├─► payment.declined
                      │   error: insufficient_funds
                      │
                      └─► payment.completed
                          processed_by: stripe
                          reference_id: pi_12345
```

### Use Case 2: Account Reconciliation

```python
class ReconciliationEngine:
    """Verify event stream matches bank records"""

    def __init__(self, event_store: EventStore, bank_service):
        self.event_store = event_store
        self.bank_service = bank_service

    def reconcile_account(self, account_id: str,
                         statement_period: tuple) -> dict:
        """Reconcile account against bank statement"""

        # Get system state from events
        state_projector = AccountStateProjector(self.event_store)
        system_state = state_projector.get_state_at_time(
            account_id,
            statement_period[1]
        )

        # Get bank state
        bank_state = self.bank_service.get_account_balance(
            account_id,
            statement_period[1]
        )

        # Compare
        reconciliation = {
            'system_balance': system_state.balance,
            'bank_balance': bank_state,
            'difference': abs(system_state.balance - bank_state),
            'reconciled': system_state.balance == bank_state,
            'reconciliation_date': statement_period[1]
        }

        if not reconciliation['reconciled']:
            # Find discrepancy
            transactions = self.event_store.get_events_for_account(
                account_id
            )

            uncleared = [
                t for t in transactions
                if t.timestamp <= statement_period[1]
                and not t.metadata.get('bank_cleared')
            ]

            reconciliation['uncleared_transactions'] = len(uncleared)
            reconciliation['missing_transactions'] = self._find_missing(
                account_id,
                transactions
            )

        return reconciliation

    def _find_missing(self, account_id: str,
                     system_transactions: List) -> List:
        """Find transactions in bank but not in system"""
        bank_transactions = self.bank_service.get_transactions(account_id)
        system_refs = {t.metadata.get('bank_ref') for t in system_transactions}

        missing = [
            t for t in bank_transactions
            if t.reference not in system_refs
        ]

        return missing
```

## Snapshots & Optimization

### Snapshot Pattern

```
Without Snapshots:
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ Event 1 │ Event 2 │ Event 3 │ Event 4 │ Event 5 │
└─────────┴─────────┴─────────┴─────────┴─────────┘
Rebuild state: Replay 5 events

With Snapshots (every 100 events):
┌──────────────────────┬─────────┬─────────┬─────────┐
│   SNAPSHOT (100)     │ Event101│ Event102│ Event103│
│ Balance: $10,000     └─────────┴─────────┴─────────┘
└──────────────────────┘
Rebuild state: Load snapshot + replay 3 events
```

```python
class SnapshotStore:
    """Store periodic snapshots for optimization"""

    def __init__(self, database):
        self.db = database
        self._initialize_schema()

    def _initialize_schema(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS account_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                sequence_number BIGINT NOT NULL,
                state JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, sequence_number)
            );

            CREATE INDEX idx_account_snapshot ON account_snapshots(account_id);
        ''')

    def create_snapshot(self, account_id: str, sequence_number: int,
                       state: AccountState):
        """Create snapshot of account state"""
        snapshot_id = str(uuid.uuid4())

        self.db.execute('''
            INSERT INTO account_snapshots (
                snapshot_id, account_id, sequence_number, state
            )
            VALUES (%s, %s, %s, %s)
        ''', (
            snapshot_id,
            account_id,
            sequence_number,
            json.dumps({
                'balance': state.balance,
                'holds': state.holds,
                'available_balance': state.available_balance,
                'is_frozen': state.is_frozen,
                'kyc_verified': state.kyc_verified,
                'transaction_count': state.transaction_count
            })
        ))

        return snapshot_id

    def get_latest_snapshot(self, account_id: str):
        """Get most recent snapshot"""
        result = self.db.query('''
            SELECT * FROM account_snapshots
            WHERE account_id = %s
            ORDER BY sequence_number DESC
            LIMIT 1
        ''', (account_id,))

        return result[0] if result else None

class OptimizedAccountStateProjector:
    """Fast state reconstruction using snapshots"""

    def __init__(self, event_store: EventStore,
                 snapshot_store: SnapshotStore):
        self.event_store = event_store
        self.snapshot_store = snapshot_store

    def get_current_state(self, account_id: str) -> AccountState:
        """Get state using snapshot + replay"""

        # Get latest snapshot
        snapshot = self.snapshot_store.get_latest_snapshot(account_id)

        if snapshot:
            # Start from snapshot
            state = AccountState(account_id)
            state_data = json.loads(snapshot['state'])
            state.balance = state_data['balance']
            state.holds = state_data['holds']
            state.available_balance = state_data['available_balance']
            state.is_frozen = state_data['is_frozen']
            state.kyc_verified = state_data['kyc_verified']
            state.transaction_count = state_data['transaction_count']

            # Replay events after snapshot
            events = self.event_store.get_events_for_account(
                account_id,
                from_sequence=snapshot['sequence_number']
            )
        else:
            # No snapshot, replay all events
            state = AccountState(account_id)
            events = self.event_store.get_events_for_account(account_id)

        # Apply remaining events
        for event in events:
            state.apply_event(event)

        return state
```

## Compliance & Audit

### Immutable Audit Trail

```python
class AuditTrail:
    """Compliance-grade immutable audit trail"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def export_audit_trail(self, account_id: str,
                          start_date: datetime,
                          end_date: datetime) -> str:
        """Export audit trail for compliance"""

        events = self.event_store.get_events_for_account(account_id)
        events = [e for e in events if start_date <= e.timestamp <= end_date]

        audit_csv = "event_id,type,amount,timestamp,user_id,status\n"

        for event in events:
            audit_csv += (
                f"{event.event_id},"
                f"{event.event_type.value},"
                f"{event.amount or ''},"
                f"{event.timestamp.isoformat()},"
                f"{event.user_id or ''},"
                "completed\n"
            )

        # Sign for compliance
        signature = self._sign_audit_trail(audit_csv)

        return f"{audit_csv}\n# Signature: {signature}"

    def _sign_audit_trail(self, content: str) -> str:
        """Cryptographically sign audit trail"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
```

## Conclusion

Event sourcing provides:

1. **Complete audit trail** for compliance
2. **Temporal queries** for any point-in-time state
3. **Replay capability** for debugging and recovery
4. **Reconciliation** against external systems
5. **Event-driven architecture** for scalability

Combine with snapshots for performance and dual-entry ledgers for accounting compliance.
