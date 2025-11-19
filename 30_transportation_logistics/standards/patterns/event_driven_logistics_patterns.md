# Event-Driven Architecture Patterns for Logistics

## Overview

Event-driven architecture (EDA) is essential for modern logistics systems that require real-time responsiveness, scalability, and system decoupling. This document catalogs proven patterns used by industry leaders like Amazon, Uber, DoorDash, and enterprise logistics platforms.

## Core Concepts

### Event vs. Message vs. Command

| Type | Purpose | Example | Characteristics |
|------|---------|---------|-----------------|
| **Event** | Fact that occurred | `OrderDelivered` | Past tense, immutable, broadcasts to multiple consumers |
| **Command** | Request to do something | `OptimizeRoute` | Imperative, single consumer, can fail |
| **Message** | Generic communication | N/A | Catch-all term |

**Best Practice**: Use events for state changes, commands for actions.

---

## Pattern 1: Event Sourcing for Shipment Tracking

### Problem
Shipments go through many status changes. Need complete audit trail and ability to reconstruct state.

### Solution
Store all state changes as immutable events in an event store.

**Event Stream**:
```
ShipmentCreated → ShipmentTendered → PickupScheduled →
PickedUp → InTransit → OutForDelivery → Delivered
```

**Implementation** (Python with PostgreSQL):
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List
import json

@dataclass
class Event:
    aggregate_id: str      # Shipment ID
    event_type: str
    payload: dict
    version: int
    timestamp: datetime

class EventStore:
    def append(self, event: Event):
        """Append event to immutable log."""
        with db.transaction():
            # Optimistic concurrency control
            current_version = self.get_version(event.aggregate_id)
            if event.version != current_version + 1:
                raise ConcurrencyError("Version mismatch")

            db.execute("""
                INSERT INTO events (aggregate_id, event_type, payload, version, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, event.aggregate_id, event.event_type, json.dumps(event.payload),
                 event.version, event.timestamp)

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for a shipment."""
        return db.query("""
            SELECT * FROM events
            WHERE aggregate_id = ?
            ORDER BY version ASC
        """, aggregate_id)

class Shipment:
    def __init__(self, shipment_id: str):
        self.id = shipment_id
        self.status = None
        self.version = 0
        self.milestones = []

    def apply_event(self, event: Event):
        """Rebuild state from events (event sourcing)."""
        if event.event_type == "ShipmentCreated":
            self.status = "created"
            self.order_id = event.payload['order_id']
        elif event.event_type == "ShipmentTendered":
            self.status = "tendered"
            self.carrier = event.payload['carrier']
        elif event.event_type == "PickedUp":
            self.status = "in_transit"
            self.milestones.append({
                'type': 'pickup',
                'timestamp': event.timestamp,
                'location': event.payload['location']
            })
        elif event.event_type == "Delivered":
            self.status = "delivered"
            self.delivered_at = event.timestamp

        self.version = event.version

    @classmethod
    def from_events(cls, events: List[Event]):
        """Reconstruct shipment from event stream."""
        shipment = cls(events[0].aggregate_id)
        for event in events:
            shipment.apply_event(event)
        return shipment
```

**Benefits**:
- Complete audit trail (compliance requirement)
- Time travel: Reconstruct state at any point
- Event replay for debugging and testing
- Multiple read models (CQRS)

**Used By**: Amazon (order history), Uber (trip replay), FedEx (tracking events)

---

## Pattern 2: CQRS (Command Query Responsibility Segregation)

### Problem
Read and write workloads have different requirements. Reads (tracking queries) are 10-100x more frequent than writes (status updates).

### Solution
Separate read and write models, optimized independently.

**Architecture**:
```
                          ┌──────────────────┐
   Commands               │  Command Handler │
   (Create Order)  ──────>│   (Write Model)  │
                          └─────────┬────────┘
                                    │
                          ┌─────────▼────────┐
                          │   Event Store    │
                          │     (Source)     │
                          └─────────┬────────┘
                                    │
                                    │ Events Published
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
      ┌─────────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
      │  Projection 1    │ │  Projection 2  │ │  Projection 3  │
      │ (Tracking View)  │ │ (Analytics)    │ │  (Search View) │
      │   (PostgreSQL)   │ │  (BigQuery)    │ │(Elasticsearch) │
      └──────────────────┘ └────────────────┘ └────────────────┘
                │                   │                   │
         Queries (Track shipment, Get analytics, Search)
```

**Implementation**:
```python
# Write Model (Command Side)
class CreateShipmentCommand:
    def __init__(self, order_id: str, carrier: str, destination: Address):
        self.order_id = order_id
        self.carrier = carrier
        self.destination = destination

class ShipmentCommandHandler:
    def handle(self, command: CreateShipmentCommand):
        # Business logic and validation
        if not self.is_valid_address(command.destination):
            raise ValidationError("Invalid destination")

        # Create event
        event = Event(
            aggregate_id=generate_id(),
            event_type="ShipmentCreated",
            payload={
                'order_id': command.order_id,
                'carrier': command.carrier,
                'destination': command.destination.to_dict()
            },
            version=1,
            timestamp=datetime.utcnow()
        )

        # Store event
        event_store.append(event)

        # Publish to event bus
        event_bus.publish(event)

# Read Model (Query Side) - Tracking View
class TrackingProjection:
    def handle_shipment_created(self, event: Event):
        db.execute("""
            INSERT INTO shipments_tracking_view (id, order_id, status, carrier)
            VALUES (?, ?, ?, ?)
        """, event.aggregate_id, event.payload['order_id'], 'created', event.payload['carrier'])

    def handle_shipment_in_transit(self, event: Event):
        db.execute("""
            UPDATE shipments_tracking_view
            SET status = 'in_transit',
                current_location = ST_MakePoint(?, ?),
                estimated_delivery = ?
            WHERE id = ?
        """, event.payload['lat'], event.payload['lon'],
             event.payload['eta'], event.aggregate_id)

# Query Service (Read Side)
class TrackingQueryService:
    def get_shipment_status(self, shipment_id: str):
        """Fast read from optimized view."""
        return db.query_one("""
            SELECT id, status, current_location, estimated_delivery
            FROM shipments_tracking_view
            WHERE id = ?
        """, shipment_id)
```

**Benefits**:
- Read optimization: Denormalized views, specialized databases
- Write optimization: Event sourcing, async processing
- Scalability: Scale reads and writes independently
- Multiple representations: Same data, different views (tracking, analytics, search)

**Used By**: LinkedIn, Netflix, Amazon (different views for customers, sellers, operations)

---

## Pattern 3: Saga Pattern for Distributed Transactions

### Problem
Order fulfillment spans multiple services (inventory, shipment, payment, notification). Need transactional guarantees without distributed transactions (2PC).

### Solution
Coordinate long-running transactions using compensating actions.

**Order Fulfillment Saga**:
```
1. Reserve Inventory → [Success] → 2. Create Shipment
                     → [Failure] → Cancel Order

2. Create Shipment → [Success] → 3. Charge Payment
                   → [Failure] → Release Inventory, Cancel Order

3. Charge Payment → [Success] → 4. Send Confirmation
                  → [Failure] → Cancel Shipment, Release Inventory, Refund

4. Send Confirmation → Order Complete
```

**Implementation** (Orchestration Pattern):
```python
from enum import Enum
from typing import Callable, Dict

class SagaStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"

class SagaStep:
    def __init__(self, action: Callable, compensation: Callable):
        self.action = action
        self.compensation = compensation

class OrderFulfillmentSaga:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = SagaStatus.PENDING
        self.completed_steps = []

        # Define saga steps
        self.steps = [
            SagaStep(
                action=self.reserve_inventory,
                compensation=self.release_inventory
            ),
            SagaStep(
                action=self.create_shipment,
                compensation=self.cancel_shipment
            ),
            SagaStep(
                action=self.charge_payment,
                compensation=self.refund_payment
            ),
            SagaStep(
                action=self.send_confirmation,
                compensation=lambda: None  # No compensation needed
            )
        ]

    async def execute(self):
        """Execute saga steps sequentially."""
        try:
            for step in self.steps:
                # Execute step
                result = await step.action()
                self.completed_steps.append(step)

                # Persist state (for crash recovery)
                await self.save_state()

            self.status = SagaStatus.COMPLETED
            return {"status": "success", "order_id": self.order_id}

        except Exception as e:
            # Compensate in reverse order
            await self.compensate()
            raise

    async def compensate(self):
        """Execute compensating transactions."""
        self.status = SagaStatus.COMPENSATING

        for step in reversed(self.completed_steps):
            try:
                await step.compensation()
            except Exception as e:
                # Log but continue compensating
                logger.error(f"Compensation failed: {e}")

        self.status = SagaStatus.FAILED

    async def reserve_inventory(self):
        response = await inventory_service.reserve(
            order_id=self.order_id,
            items=self.order.items
        )
        if not response.success:
            raise InventoryError("Insufficient inventory")
        return response

    async def release_inventory(self):
        await inventory_service.release(self.order_id)

    async def create_shipment(self):
        response = await shipment_service.create(
            order_id=self.order_id,
            destination=self.order.delivery_address
        )
        self.shipment_id = response.shipment_id
        return response

    async def cancel_shipment(self):
        await shipment_service.cancel(self.shipment_id)

    async def charge_payment(self):
        response = await payment_service.charge(
            order_id=self.order_id,
            amount=self.order.total
        )
        self.payment_id = response.payment_id
        return response

    async def refund_payment(self):
        await payment_service.refund(self.payment_id)

    async def send_confirmation(self):
        await notification_service.send_email(
            to=self.order.customer_email,
            template="order_confirmed",
            data={'order_id': self.order_id, 'shipment_id': self.shipment_id}
        )
```

**Alternative: Choreography Pattern**:
```
Events orchestrate the flow (no central coordinator)

OrderCreated Event
   ↓
Inventory Service: Reserves inventory → InventoryReserved Event
   ↓
Shipment Service: Creates shipment → ShipmentCreated Event
   ↓
Payment Service: Charges payment → PaymentCharged Event
   ↓
Notification Service: Sends confirmation

If PaymentFailed Event:
   → Shipment Service: Cancels shipment → ShipmentCancelled Event
   → Inventory Service: Releases inventory
```

**Benefits**:
- No distributed transactions (2PC)
- Resilience: Continue even if services fail temporarily
- Auditability: Full history of saga execution

**Used By**: Uber (trip booking), Amazon (order fulfillment), Airbnb (booking flow)

---

## Pattern 4: Outbox Pattern for Reliable Event Publishing

### Problem
Need to update database AND publish event atomically. If DB update succeeds but event publish fails, system is inconsistent.

### Solution
Write event to "outbox" table in same transaction, then publish asynchronously.

**Implementation**:
```python
# Step 1: Write to DB + Outbox in single transaction
def create_shipment(order_id: str, carrier: str):
    with db.transaction():
        # 1. Update domain table
        shipment_id = db.execute("""
            INSERT INTO shipments (order_id, carrier, status)
            VALUES (?, ?, ?)
            RETURNING id
        """, order_id, carrier, 'created')

        # 2. Write to outbox (same transaction)
        db.execute("""
            INSERT INTO outbox_events (aggregate_id, event_type, payload, created_at)
            VALUES (?, ?, ?, ?)
        """, shipment_id, 'ShipmentCreated',
             json.dumps({'order_id': order_id, 'carrier': carrier}),
             datetime.utcnow())

    # Transaction committed - both writes guaranteed

# Step 2: Outbox Publisher (separate process)
class OutboxPublisher:
    def run(self):
        while True:
            # Poll outbox for unpublished events
            events = db.query("""
                SELECT * FROM outbox_events
                WHERE published_at IS NULL
                ORDER BY created_at ASC
                LIMIT 100
            """)

            for event in events:
                try:
                    # Publish to event bus
                    kafka_producer.send(
                        topic='shipment-events',
                        value=event.payload,
                        key=event.aggregate_id
                    )

                    # Mark as published
                    db.execute("""
                        UPDATE outbox_events
                        SET published_at = ?
                        WHERE id = ?
                    """, datetime.utcnow(), event.id)

                except Exception as e:
                    logger.error(f"Failed to publish event {event.id}: {e}")
                    # Retry on next iteration

            time.sleep(1)  # Poll every second
```

**Benefits**:
- Guaranteed event publishing (at-least-once delivery)
- No distributed transactions
- Simple to implement

**Drawback**: Slight delay in event publishing (eventual consistency)

**Used By**: DoorDash, Uber, most microservices platforms

---

## Pattern 5: Event Carried State Transfer

### Problem
Subscribers need context about an event, but fetching from API adds latency and coupling.

### Solution
Include relevant state in event payload.

**Before (Anti-Pattern)**:
```json
{
  "event_type": "ShipmentStatusChanged",
  "shipment_id": "SHP-12345",
  "new_status": "delivered"
}
```
*Subscriber must call API to get shipment details*

**After (Event Carried State Transfer)**:
```json
{
  "event_type": "ShipmentStatusChanged",
  "shipment_id": "SHP-12345",
  "new_status": "delivered",
  "shipment": {
    "tracking_number": "1Z999AA1234567890",
    "order_id": "ORD-5678",
    "customer": {
      "id": "CUST-9012",
      "email": "customer@example.com",
      "phone": "+1-555-0100"
    },
    "delivery_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102"
    },
    "delivered_at": "2025-01-15T14:30:00Z",
    "proof_of_delivery": {
      "signature_url": "https://...",
      "photo_url": "https://..."
    }
  },
  "previous_status": "out_for_delivery"
}
```

**Benefits**:
- Subscribers are autonomous (no API calls needed)
- Reduced latency
- System continues even if shipment service is down

**Tradeoff**: Larger event payloads, potential data duplication

**Used By**: Netflix, Amazon, Shopify

---

## Pattern 6: Change Data Capture (CDC)

### Problem
Need to publish events for every database change, but don't want to modify application code.

### Solution
Listen to database transaction log (WAL in Postgres, binlog in MySQL) and publish events automatically.

**Architecture**:
```
PostgreSQL Write → WAL (Write-Ahead Log)
                        ↓
                   Debezium (CDC)
                        ↓
                   Kafka Topics
                        ↓
              Consumers (Projections, Services)
```

**Implementation with Debezium**:
```json
{
  "name": "shipments-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "secret",
    "database.dbname": "logistics",
    "database.server.name": "logistics-db",
    "table.include.list": "public.shipments,public.routes,public.vehicles",
    "plugin.name": "pgoutput"
  }
}
```

**Event Output**:
```json
{
  "before": null,
  "after": {
    "id": "SHP-12345",
    "order_id": "ORD-5678",
    "status": "created",
    "carrier": "FEDEX",
    "created_at": 1642258200000
  },
  "source": {
    "version": "1.8.0",
    "connector": "postgresql",
    "name": "logistics-db",
    "ts_ms": 1642258201000,
    "db": "logistics",
    "schema": "public",
    "table": "shipments"
  },
  "op": "c",  // c=create, u=update, d=delete
  "ts_ms": 1642258201234
}
```

**Benefits**:
- Zero application code changes
- Guaranteed capture of all changes
- Supports legacy systems

**Challenges**:
- Events are low-level (DB changes, not business events)
- Need transformation to domain events

**Used By**: LinkedIn (data pipelines), Uber (replication), Netflix (caching)

---

## Best Practices

### 1. Event Naming Convention
- Use past tense: `OrderCreated`, `ShipmentDelivered` (not `CreateOrder`, `DeliverShipment`)
- Be specific: `InventoryReserved` vs. generic `InventoryUpdated`
- Namespace by domain: `logistics.shipment.created`

### 2. Event Versioning
```python
class EventV1:
    version = 1
    event_type = "ShipmentCreated"
    # fields...

class EventV2:
    version = 2
    event_type = "ShipmentCreated"
    # new fields added, old fields kept for compatibility

# Event upcasting (convert old events to new format)
def upcast_event(event: dict) -> dict:
    if event['version'] == 1:
        # Add default values for new fields
        event['carrier_service_type'] = 'GROUND'
        event['version'] = 2
    return event
```

### 3. Idempotent Event Handling
```python
def handle_order_delivered(event: Event):
    # Check if already processed (idempotency)
    if event_store.is_processed(event.id):
        logger.info(f"Event {event.id} already processed, skipping")
        return

    # Process event
    update_order_status(event.order_id, 'delivered')
    send_delivery_confirmation(event.order_id)

    # Mark as processed
    event_store.mark_processed(event.id)
```

### 4. Event Retention
- **Hot events** (last 7 days): Keep in Kafka for replays
- **Warm events** (8-90 days): Archive to S3/blob storage
- **Cold events** (90+ days): Compress and archive, delete from Kafka

## References

- **Martin Fowler**: Event Sourcing, CQRS patterns
- **Uber Engineering Blog**: Saga pattern at scale
- **Amazon Builder's Library**: Event-driven architectures
- **Confluent**: Event streaming patterns with Kafka
- **Microsoft Azure**: Cloud Design Patterns for distributed systems

---

**Version**: 1.0
**Last Updated**: 2025-01-19
