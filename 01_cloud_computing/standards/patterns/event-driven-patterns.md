# Event-Driven Architecture Patterns

## Overview

Event-driven architecture (EDA) patterns enable loosely coupled, scalable systems where components communicate through events. This guide covers essential patterns for building responsive, real-time, and resilient event-driven systems.

## Table of Contents

1. [Event Sourcing Pattern](#event-sourcing-pattern)
2. [CQRS with Event Sourcing](#cqrs-with-event-sourcing)
3. [Event Notification Pattern](#event-notification-pattern)
4. [Event-Carried State Transfer](#event-carried-state-transfer)
5. [Event Streaming Pattern](#event-streaming-pattern)
6. [Event Collaboration Pattern](#event-collaboration-pattern)
7. [Event Store Pattern](#event-store-pattern)

## Event-Driven Architecture Fundamentals

```
┌──────────────────────────────────────────┐
│      Event-Driven Core Concepts          │
├──────────────────────────────────────────┤
│                                          │
│  Event: Immutable fact that happened    │
│  Event Producer: Publishes events       │
│  Event Consumer: Subscribes to events   │
│  Event Broker: Routes events             │
│  Event Store: Persists events            │
│  Event Handler: Processes events         │
│                                          │
└──────────────────────────────────────────┘
```

---

## 1. Event Sourcing Pattern

### Description

Store all changes to application state as a sequence of events, rather than storing just current state. The current state is derived by replaying events.

### When to Use

- Need complete audit trail
- Temporal queries (state at any point in time)
- Complex business domains
- Event replay capabilities needed
- Debugging and troubleshooting requirements
- Compliance and regulatory requirements

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│           Event Sourcing Architecture            │
└──────────────────────────────────────────────────┘

   Command              Event Store           Read Model
     │                 (Source of Truth)     (Projection)
     │                      │                      │
     ▼                      │                      │
┌─────────┐                │                      │
│Command  │   Event        │                      │
│Handler  ├───────────────►│                      │
└─────────┘                │                      │
                           │                      │
                      ┌────▼────┐                 │
                      │ Events  │                 │
                      │┌───────┐│                 │
                      ││Event 1││                 │
                      │├───────┤│                 │
                      ││Event 2││   Replay        │
                      │├───────┤│   ──────────────►
                      ││Event 3││                 │
                      │├───────┤│                 │
                      ││Event 4││                 │
                      │└───────┘│                 │
                      └─────────┘            ┌────▼────┐
                           │                 │Current  │
                           │                 │State    │
                           │                 │View     │
                           │                 └─────────┘
                           │
                      Aggregate Root
                      (Reconstructed State)
```

### Implementation Example

```python
# event_sourcing.py
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import json

# Events
@dataclass
class Event:
    """Base event class"""
    event_id: str
    aggregate_id: str
    event_type: str
    timestamp: datetime
    version: int
    data: Dict[str, Any]

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'aggregate_id': self.aggregate_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'data': self.data
        }

# Domain Events for Bank Account
@dataclass
class AccountOpenedEvent:
    account_id: str
    owner_name: str
    initial_balance: float
    timestamp: datetime = None

@dataclass
class MoneyDepositedEvent:
    account_id: str
    amount: float
    timestamp: datetime = None

@dataclass
class MoneyWithdrawnEvent:
    account_id: str
    amount: float
    timestamp: datetime = None

@dataclass
class AccountClosedEvent:
    account_id: str
    final_balance: float
    timestamp: datetime = None

# Aggregate Root
class BankAccount:
    """Aggregate root that applies events"""

    def __init__(self, account_id: str):
        self.account_id = account_id
        self.owner_name = None
        self.balance = 0.0
        self.is_closed = False
        self.version = 0
        self._uncommitted_events: List[Event] = []

    def open_account(self, owner_name: str, initial_balance: float):
        """Open new account - generates event"""
        if self.owner_name:
            raise ValueError("Account already opened")

        event = AccountOpenedEvent(
            account_id=self.account_id,
            owner_name=owner_name,
            initial_balance=initial_balance,
            timestamp=datetime.now()
        )

        self._apply_event(event)
        self._uncommitted_events.append(event)

    def deposit(self, amount: float):
        """Deposit money - generates event"""
        if self.is_closed:
            raise ValueError("Cannot deposit to closed account")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        event = MoneyDepositedEvent(
            account_id=self.account_id,
            amount=amount,
            timestamp=datetime.now()
        )

        self._apply_event(event)
        self._uncommitted_events.append(event)

    def withdraw(self, amount: float):
        """Withdraw money - generates event"""
        if self.is_closed:
            raise ValueError("Cannot withdraw from closed account")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")

        event = MoneyWithdrawnEvent(
            account_id=self.account_id,
            amount=amount,
            timestamp=datetime.now()
        )

        self._apply_event(event)
        self._uncommitted_events.append(event)

    def close_account(self):
        """Close account - generates event"""
        if self.is_closed:
            raise ValueError("Account already closed")

        event = AccountClosedEvent(
            account_id=self.account_id,
            final_balance=self.balance,
            timestamp=datetime.now()
        )

        self._apply_event(event)
        self._uncommitted_events.append(event)

    def _apply_event(self, event):
        """Apply event to update internal state"""
        if isinstance(event, AccountOpenedEvent):
            self.owner_name = event.owner_name
            self.balance = event.initial_balance

        elif isinstance(event, MoneyDepositedEvent):
            self.balance += event.amount

        elif isinstance(event, MoneyWithdrawnEvent):
            self.balance -= event.amount

        elif isinstance(event, AccountClosedEvent):
            self.is_closed = True

        self.version += 1

    def get_uncommitted_events(self) -> List:
        """Get events that need to be saved"""
        return self._uncommitted_events

    def mark_events_as_committed(self):
        """Clear uncommitted events after saving"""
        self._uncommitted_events = []

    @classmethod
    def from_events(cls, events: List) -> 'BankAccount':
        """Reconstruct aggregate from events (replay)"""
        if not events:
            raise ValueError("No events to replay")

        first_event = events[0]
        account = cls(first_event.account_id)

        for event in events:
            account._apply_event(event)

        return account


# Event Store
class EventStore:
    """Simple in-memory event store"""

    def __init__(self):
        self.events: Dict[str, List[Event]] = {}

    def save_events(self, aggregate_id: str, events: List,
                   expected_version: int = None):
        """Save events for an aggregate"""

        if aggregate_id not in self.events:
            self.events[aggregate_id] = []

        current_version = len(self.events[aggregate_id])

        # Optimistic concurrency check
        if expected_version is not None and current_version != expected_version:
            raise ValueError(
                f"Concurrency conflict: expected version {expected_version}, "
                f"got {current_version}"
            )

        # Convert domain events to Event objects
        for idx, domain_event in enumerate(events):
            event = Event(
                event_id=str(uuid.uuid4()),
                aggregate_id=aggregate_id,
                event_type=type(domain_event).__name__,
                timestamp=domain_event.timestamp or datetime.now(),
                version=current_version + idx + 1,
                data=domain_event.__dict__
            )
            self.events[aggregate_id].append(event)

        print(f"Saved {len(events)} events for aggregate {aggregate_id}")

    def get_events(self, aggregate_id: str) -> List:
        """Get all events for an aggregate"""
        events = self.events.get(aggregate_id, [])
        return [self._to_domain_event(e) for e in events]

    def get_events_since(self, aggregate_id: str, version: int) -> List:
        """Get events since a specific version"""
        all_events = self.events.get(aggregate_id, [])
        filtered = [e for e in all_events if e.version > version]
        return [self._to_domain_event(e) for e in filtered]

    def _to_domain_event(self, event: Event):
        """Convert Event to domain event"""
        event_classes = {
            'AccountOpenedEvent': AccountOpenedEvent,
            'MoneyDepositedEvent': MoneyDepositedEvent,
            'MoneyWithdrawnEvent': MoneyWithdrawnEvent,
            'AccountClosedEvent': AccountClosedEvent
        }

        event_class = event_classes.get(event.event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event.event_type}")

        return event_class(**event.data)


# Repository
class BankAccountRepository:
    """Repository for bank accounts using event sourcing"""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def save(self, account: BankAccount):
        """Save aggregate by storing its events"""
        uncommitted = account.get_uncommitted_events()

        if uncommitted:
            expected_version = account.version - len(uncommitted)
            self.event_store.save_events(
                account.account_id,
                uncommitted,
                expected_version
            )
            account.mark_events_as_committed()

    def get(self, account_id: str) -> BankAccount:
        """Load aggregate by replaying events"""
        events = self.event_store.get_events(account_id)

        if not events:
            raise ValueError(f"Account {account_id} not found")

        return BankAccount.from_events(events)


# Usage Example
def main():
    # Setup
    event_store = EventStore()
    repository = BankAccountRepository(event_store)

    # Create and save account
    account_id = str(uuid.uuid4())
    account = BankAccount(account_id)
    account.open_account("John Doe", 1000.0)
    account.deposit(500.0)
    account.withdraw(200.0)

    repository.save(account)
    print(f"Account balance: ${account.balance}")

    # Load account from events (replay)
    loaded_account = repository.get(account_id)
    print(f"Loaded account balance: ${loaded_account.balance}")

    # Make more changes
    loaded_account.deposit(100.0)
    loaded_account.close_account()
    repository.save(loaded_account)

    # Verify final state
    final_account = repository.get(account_id)
    print(f"Final balance: ${final_account.balance}, Closed: {final_account.is_closed}")

    # Show all events
    all_events = event_store.get_events(account_id)
    print(f"\nTotal events: {len(all_events)}")
    for event in all_events:
        print(f"  - {type(event).__name__}")


if __name__ == "__main__":
    main()
```

### Event Store with PostgreSQL

```python
# postgresql_event_store.py
import psycopg2
import json
from datetime import datetime

class PostgreSQLEventStore:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self._create_tables()

    def _create_tables(self):
        """Create event store tables"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id UUID PRIMARY KEY,
                    aggregate_id UUID NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    version INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    data JSONB NOT NULL,
                    metadata JSONB,
                    UNIQUE (aggregate_id, version)
                );

                CREATE INDEX IF NOT EXISTS idx_events_aggregate
                ON events(aggregate_id, version);

                CREATE INDEX IF NOT EXISTS idx_events_type
                ON events(event_type);

                CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON events(timestamp);
            """)
            self.conn.commit()

    def save_events(self, aggregate_id: str, events: List[Event],
                   expected_version: int = None):
        """Save events with optimistic concurrency"""
        with self.conn.cursor() as cursor:
            # Check current version
            cursor.execute(
                "SELECT COALESCE(MAX(version), 0) FROM events WHERE aggregate_id = %s",
                (aggregate_id,)
            )
            current_version = cursor.fetchone()[0]

            if expected_version is not None and current_version != expected_version:
                raise ValueError("Concurrency conflict")

            # Insert events
            for event in events:
                cursor.execute("""
                    INSERT INTO events
                    (event_id, aggregate_id, event_type, version, timestamp, data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    event.event_id,
                    event.aggregate_id,
                    event.event_type,
                    event.version,
                    event.timestamp,
                    json.dumps(event.data)
                ))

            self.conn.commit()

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for aggregate"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT event_id, aggregate_id, event_type, version, timestamp, data
                FROM events
                WHERE aggregate_id = %s
                ORDER BY version ASC
            """, (aggregate_id,))

            events = []
            for row in cursor.fetchall():
                events.append(Event(
                    event_id=row[0],
                    aggregate_id=row[1],
                    event_type=row[2],
                    version=row[3],
                    timestamp=row[4],
                    data=row[5]
                ))

            return events
```

### Trade-offs

**Pros:**
- Complete audit trail
- Temporal queries
- Event replay for debugging
- Natural fit for event-driven architecture
- Can recreate state at any point

**Cons:**
- Storage overhead (all events stored)
- Complexity in querying current state
- Event schema evolution challenges
- Performance considerations for large event streams
- Learning curve

### Anti-patterns

- **Mutable Events**: Events should be immutable
- **Large Events**: Events too big, should contain only necessary data
- **No Versioning**: Not versioning events leads to evolution issues
- **Synchronous Projections**: Blocking on read model updates

### Real-world Examples

**Microsoft**: Azure Event Hubs with Event Sourcing for cloud services.

**Amazon**: Event sourcing in AWS for services like DynamoDB Streams.

**Eventbrite**: Uses event sourcing for ticketing and event management.

---

## 2. CQRS with Event Sourcing

### Description

Combine Command Query Responsibility Segregation (CQRS) with Event Sourcing for optimal read/write separation using events as source of truth.

### Architecture Diagram

```
┌────────────────────────────────────────────────────┐
│       CQRS + Event Sourcing Architecture           │
└────────────────────────────────────────────────────┘

    Command              Event Store           Projections
      │                     │                      │
┌─────▼──────┐             │                      │
│  Command   │   Events    │                      │
│  Handler   ├────────────►│                      │
└────────────┘             │                      │
                      ┌────▼─────┐                │
                      │  Events  │                │
                      │  Stream  │                │
                      └────┬─────┘                │
                           │                      │
                           │  Event Bus           │
                           │                      │
              ┌────────────┼────────────┐         │
              │            │            │         │
         ┌────▼────┐  ┌───▼────┐  ┌───▼────┐    │
         │Project. │  │Project.│  │Project.│    │
         │Handler  │  │Handler │  │Handler │    │
         │   #1    │  │  #2    │  │  #3    │    │
         └────┬────┘  └───┬────┘  └───┬────┘    │
              │           │           │          │
         ┌────▼────┐ ┌───▼────┐ ┌───▼──────┐   │
         │ Redis   │ │Elastic │ │Postgres  │   │
         │ (Cache) │ │(Search)│ │(Reports) │   │
         └─────────┘ └────────┘ └──────────┘   │
              │           │           │          │
              └───────────┴───────────┘          │
                          │                      │
                     ┌────▼─────┐                │
                     │  Query   │                │
                     │ Handlers │                │
                     └──────────┘                │
```

### Real-world Examples

**Greg Young**: EventStore DB - purpose-built database for event sourcing.

**Axon Framework**: Java framework for CQRS and Event Sourcing.

---

## 3. Event Notification Pattern

### Description

Services publish lightweight event notifications when state changes. Consumers can query for more details if needed.

### When to Use

- Loose coupling between services
- Notifying interested parties of changes
- Triggering workflows
- Audit trails
- Real-time updates

### Implementation Example

```python
# event_notification.py
import boto3
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EventNotification:
    """Lightweight event notification"""
    event_type: str
    aggregate_id: str
    timestamp: datetime
    metadata: dict = None

    def to_message(self) -> dict:
        return {
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }


class EventPublisher:
    """Publish event notifications via SNS"""

    def __init__(self, topic_arn: str):
        self.sns = boto3.client('sns')
        self.topic_arn = topic_arn

    def publish(self, event: EventNotification):
        """Publish event notification"""
        message = event.to_message()

        self.sns.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(message),
            MessageAttributes={
                'event_type': {
                    'DataType': 'String',
                    'StringValue': event.event_type
                }
            }
        )

        print(f"Published event: {event.event_type} for {event.aggregate_id}")


# Example: Order Service publishes notifications
class OrderService:
    def __init__(self, event_publisher: EventPublisher):
        self.publisher = event_publisher

    def create_order(self, order_data: dict) -> str:
        """Create order and publish notification"""
        order_id = self._save_order(order_data)

        # Publish notification
        notification = EventNotification(
            event_type='OrderCreated',
            aggregate_id=order_id,
            timestamp=datetime.now(),
            metadata={
                'customer_id': order_data['customer_id'],
                'total_amount': order_data['total']
            }
        )

        self.publisher.publish(notification)

        return order_id

    def _save_order(self, order_data: dict) -> str:
        # Database save logic
        return "order-123"


# Consumers query for details when notified
class InventoryService:
    """Subscribes to OrderCreated events"""

    def handle_order_created(self, notification: EventNotification):
        """Handle order created notification"""
        order_id = notification.aggregate_id

        # Query order service for full details
        order_details = self._fetch_order_details(order_id)

        # Reserve inventory
        self._reserve_inventory(order_details)

    def _fetch_order_details(self, order_id: str) -> dict:
        # HTTP call to order service
        pass

    def _reserve_inventory(self, order_details: dict):
        # Reserve inventory logic
        pass
```

### Real-world Examples

**GitHub**: Webhooks for repository events (push, pull request, etc.).

**Stripe**: Webhook events for payment processing.

**Slack**: Event subscriptions for workspace activities.

---

## 4. Event-Carried State Transfer

### Description

Events contain full state data, so consumers don't need to query the source. Enables autonomous services with local caches.

### When to Use

- Reduce inter-service coupling
- Improve read performance
- Handle high query loads
- Network partitions possible
- Eventually consistent data acceptable

### Implementation Example

```python
# event_carried_state.py
@dataclass
class UserProfileUpdatedEvent:
    """Event carries complete user profile"""
    user_id: str
    email: str
    full_name: str
    preferences: dict
    timestamp: datetime

class UserService:
    """Publishes events with full state"""

    def update_profile(self, user_id: str, updates: dict):
        # Update database
        user = self._update_user(user_id, updates)

        # Publish event with full state
        event = UserProfileUpdatedEvent(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            preferences=user.preferences,
            timestamp=datetime.now()
        )

        self._publish_event(event)


class OrderService:
    """Maintains local cache from events"""

    def __init__(self):
        self.user_cache = {}

    def handle_user_profile_updated(self, event: UserProfileUpdatedEvent):
        """Update local cache with user data"""
        self.user_cache[event.user_id] = {
            'email': event.email,
            'full_name': event.full_name,
            'preferences': event.preferences
        }

    def create_order(self, user_id: str, items: list):
        """Use cached user data - no remote call needed"""
        user_data = self.user_cache.get(user_id)

        if not user_data:
            # Fallback to query if not in cache
            user_data = self._query_user_service(user_id)

        # Create order with user data
        order = self._create_order(user_id, items, user_data)
        return order
```

### Trade-offs

**Pros:**
- No runtime coupling
- Better availability
- Lower latency
- Reduced load on source service

**Cons:**
- Larger events
- Storage overhead
- Eventual consistency
- Data duplication

---

## 5. Event Streaming Pattern

### Description

Continuous streams of events processed in real-time using stream processing frameworks.

### When to Use

- Real-time analytics
- Complex event processing
- Stream transformations
- Continuous queries
- IoT data processing

### Architecture with Kafka

```python
# kafka_event_streaming.py
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json

class EventStream:
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    def create_topic(self, topic_name: str, partitions: int = 3,
                    replication_factor: int = 3):
        """Create Kafka topic"""
        topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replication_factor
        )

        self.admin.create_topics([topic])

    def publish_event(self, topic: str, event: dict, key: str = None):
        """Publish event to stream"""
        self.producer.send(
            topic,
            key=key.encode('utf-8') if key else None,
            value=event
        )
        self.producer.flush()


# Stream processor
class OrderEventProcessor:
    """Process order event stream"""

    def __init__(self, bootstrap_servers: list):
        self.consumer = KafkaConsumer(
            'orders',
            bootstrap_servers=bootstrap_servers,
            group_id='order-processor',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def process_stream(self):
        """Process events from stream"""
        for message in self.consumer:
            event = message.value

            if event['event_type'] == 'OrderCreated':
                self._handle_order_created(event)
            elif event['event_type'] == 'OrderCancelled':
                self._handle_order_cancelled(event)

    def _handle_order_created(self, event: dict):
        # Processing logic
        pass
```

### Real-world Examples

**LinkedIn**: Apache Kafka for event streaming at massive scale.

**Netflix**: Kafka for real-time stream processing and analytics.

**Uber**: Real-time event streaming for trip processing and analytics.

---

## Tool Recommendations

### Event Brokers

**Apache Kafka**
- High-throughput streaming
- Event log persistence
- Stream processing (Kafka Streams)

**AWS Services**
- Amazon Kinesis (streaming)
- Amazon SNS (pub/sub)
- Amazon SQS (queuing)
- EventBridge (event bus)

**Azure Services**
- Azure Event Hubs
- Azure Service Bus
- Azure Event Grid

**GCP Services**
- Cloud Pub/Sub
- Dataflow (stream processing)

### Event Stores

- EventStore DB
- Apache Kafka (can be used as event store)
- AWS DynamoDB Streams
- PostgreSQL (custom implementation)

### Stream Processing

- Apache Kafka Streams
- Apache Flink
- Apache Spark Streaming
- AWS Kinesis Data Analytics

---

## Summary

Event-driven patterns enable:
- **Loose Coupling**: Services communicate through events
- **Scalability**: Asynchronous processing
- **Resilience**: Temporal decoupling
- **Auditability**: Complete event history

### Pattern Selection

| Requirement | Pattern |
|-------------|---------|
| Audit trail | Event Sourcing |
| Read/write optimization | CQRS + Event Sourcing |
| Simple notifications | Event Notification |
| Autonomous services | Event-Carried State |
| Real-time processing | Event Streaming |

### FAANG Examples

- **Amazon**: Event-driven architecture throughout AWS
- **Netflix**: Reactive microservices with events
- **Facebook**: Real-time event processing for news feed
- **Uber**: Event-driven trip processing and tracking
- **LinkedIn**: Kafka-based event streaming infrastructure
