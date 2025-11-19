# Event-Driven Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Event Architecture Patterns](#event-architecture-patterns)
3. [Message Queue Documentation](#message-queue-documentation)
4. [Event Schema Management](#event-schema-management)
5. [Event Sourcing](#event-sourcing)
6. [Choreography vs. Orchestration](#choreography-vs-orchestration)
7. [Monitoring Event Flows](#monitoring-event-flows)
8. [Error Handling and Dead Letter Queues](#error-handling-and-dead-letter-queues)
9. [Consumer Documentation](#consumer-documentation)
10. [Best Practices](#best-practices)

## Overview

Event-driven architecture enables systems to react to changes in near-real-time through asynchronous message passing. This approach decouples services, enables scalability, and provides an audit trail of all system changes through events.

This guide provides comprehensive patterns for documenting event-driven systems, ensuring all stakeholders understand event flows, consumer contracts, and operational characteristics.

## Event Architecture Patterns

### Pattern 1: Event Publisher Documentation

```markdown
## Order Service - Event Publisher

### Published Events

#### OrderCreated
**Domain**: Order Management
**Trigger**: New order submitted by customer
**Frequency**: ~500/min during peak hours
**Latency**: 100-500ms from order submission
**Retention**: 30 days

**Schema Version**: 2
**Compatibility**: Backward compatible from v1.x

**Event Payload**:
```json
{
  "event_type": "OrderCreated",
  "event_id": "evt-20251119-xyz789",
  "event_timestamp": "2025-11-19T14:32:15.123Z",
  "event_version": "2.1",

  "order_id": "ORD-20251119-001",
  "customer_id": "CUST-54321",
  "order_timestamp": "2025-11-19T14:32:00Z",

  "items": [
    {
      "sku": "PROD-12345",
      "product_name": "Wireless Headphones",
      "quantity": 1,
      "unit_price_cents": 9999,
      "subtotal_cents": 9999,
      "tax_cents": 800
    }
  ],

  "order_total_cents": 10799,
  "currency": "USD",
  "tax_total_cents": 800,

  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94103",
    "country": "US"
  },

  "shipping_method": "STANDARD",
  "estimated_delivery_days": 5,

  "metadata": {
    "source": "web",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "203.0.113.45",
    "session_id": "sess-abc123",
    "request_id": "req-20251119-xyz789"
  }
}
```

**Subscribers**: Inventory Service, Payment Service, Notification Service, Analytics Service

**Publishing Mechanism**:
- **Broker**: RabbitMQ (production), In-memory (test)
- **Topic**: `order.events` (fanout exchange)
- **Format**: JSON
- **Guarantee**: At-least-once delivery
- **Partition Key**: `order_id` (for ordering guarantees)

#### OrderConfirmed
**Schema Version**: 1
**Subscribers**: Inventory Service, Notification Service

**Event Payload**:
```json
{
  "event_type": "OrderConfirmed",
  "event_id": "evt-20251119-abc123",
  "event_timestamp": "2025-11-19T14:33:45.456Z",

  "order_id": "ORD-20251119-001",
  "customer_id": "CUST-54321",
  "confirmation_timestamp": "2025-11-19T14:33:30Z",

  "payment_reference": "pay-xyz789",
  "amount_cents": 10799,
  "currency": "USD",

  "shipping_details": {
    "carrier": "FedEx",
    "estimated_pickup": "2025-11-20T00:00:00Z",
    "tracking_enabled": true
  }
}
```

### Pattern 2: Event Consumer Documentation

```markdown
## Inventory Service - Event Consumer

### Subscriptions

#### Consuming OrderCreated Events
**Topic**: `order.events`
**Event Type**: OrderCreated
**Processing Mode**: Stream (process immediately)
**Parallelism**: 10 concurrent consumers
**Max Processing Time**: 30 seconds per event

**Event Handler Logic**:
1. Validate order items exist in inventory database
2. Check stock availability (reserved_count + received_count - allocated_count)
3. If insufficient stock:
   - Publish `InventoryReservationFailed` event
   - Trigger backorder process
4. If sufficient stock:
   - Create inventory reservation record
   - Publish `InventoryReserved` event
   - Notify warehouse management system

**Implementation**:
```go
func handleOrderCreatedEvent(ctx context.Context, event OrderCreatedEvent) error {
    // Validate event structure
    if err := event.Validate(); err != nil {
        return fmt.Errorf("invalid event: %w", err)
    }

    // Begin transaction
    tx := db.BeginTx(ctx, nil)
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
            panic(r)
        }
    }()

    // Process each order item
    for _, item := range event.Items {
        stock, err := getStockWithLock(tx, item.SKU)
        if err != nil {
            tx.Rollback()
            return err
        }

        availableStock := stock.ReceivedCount - stock.AllocatedCount
        if availableStock < item.Quantity {
            // Publish failure event
            publishEvent(ctx, inventoryReservationFailedEvent(event.OrderID, item.SKU))
            tx.Rollback()
            return nil
        }

        // Create reservation
        reservation := &Reservation{
            OrderID: event.OrderID,
            SKU: item.SKU,
            Quantity: item.Quantity,
            CreatedAt: time.Now(),
        }
        if err := tx.Create(reservation).Error; err != nil {
            tx.Rollback()
            return err
        }

        // Update allocated count
        if err := tx.Model(&stock).Update("allocated_count",
            gorm.Expr("allocated_count + ?", item.Quantity)).Error; err != nil {
            tx.Rollback()
            return err
        }
    }

    // Commit transaction
    if err := tx.Commit().Error; err != nil {
        return err
    }

    // Publish success event
    publishEvent(ctx, inventoryReservedEvent(event.OrderID))
    return nil
}
```

**Error Handling**:
- Network errors: Retry up to 5 times with exponential backoff (max 30s)
- Validation errors: Send to dead-letter queue
- Database errors: Retry transaction
- Timeout: Return error and let message broker retry from queue

**Metrics**:
```
inventory_order_events_received_total: Counter
inventory_event_processing_duration_seconds: Histogram
inventory_reservation_success_total: Counter
inventory_reservation_failed_total: Counter
```

### Pattern 3: Event Flow Diagrams

```
    User Places Order
            │
            ▼
    ┌───────────────────┐
    │  Order Service    │
    │ Creates Order     │
    │ (Aggregate Root)  │
    └────────┬──────────┘
             │
             │ Publishes OrderCreated
             ▼
    ┌──────────────────────────────────────────┐
    │         RabbitMQ / Kafka Topic           │
    │         order.events (fanout)            │
    └──┬─────────────┬──────────────┬─────────┘
       │             │              │
       │             │              │
       ▼             ▼              ▼
  ┌─────────┐  ┌────────────┐  ┌───────────┐
  │Inventory│  │  Payment   │  │Notification│
  │ Service │  │  Service   │  │  Service  │
  │Consumes │  │  Consumes  │  │  Consumes │
  │ Event   │  │   Event    │  │   Event   │
  └────┬────┘  └─────┬──────┘  └─────┬─────┘
       │              │               │
       │ Processes    │ Processes     │ Sends
       │ Stock        │ Payment       │ Email
       │              │               │
       ▼              ▼               ▼
  Publishes      Publishes        Task Complete
  Inventory      Payment
  Event          Event
       │              │
       └──────┬───────┘
              │
              ▼
       ┌─────────────────┐
       │ Analytics Svc   │
       │ Aggregates all  │
       │ events for      │
       │ reporting       │
       └─────────────────┘
```

## Message Queue Documentation

### RabbitMQ Configuration

```markdown
## RabbitMQ Setup and Topology

### Exchange Configuration

```yaml
exchanges:
  - name: order.events
    type: topic
    durable: true
    auto_delete: false
    internal: false
    arguments:
      x-message-ttl: 2592000000  # 30 days in milliseconds
      x-max-length: 10000000     # 10M messages max

  - name: order.events.dlx
    type: topic
    durable: true
    auto_delete: false
    internal: false
    arguments:
      x-message-ttl: 604800000   # 7 days for dead letters
```

### Queue Configuration

```yaml
queues:
  - name: inventory.order.events
    durable: true
    exclusive: false
    auto_delete: false
    arguments:
      x-dead-letter-exchange: order.events.dlx
      x-dead-letter-routing-key: inventory.order.events.dlx
      x-max-length: 100000
      x-message-ttl: 3600000  # 1 hour expiry

  - name: payment.order.events
    durable: true
    exclusive: false
    auto_delete: false
    arguments:
      x-dead-letter-exchange: order.events.dlx
      x-dead-letter-routing-key: payment.order.events.dlx
      x-max-length: 100000

  - name: notification.order.events
    durable: true
    exclusive: false
    auto_delete: false
    arguments:
      x-dead-letter-exchange: order.events.dlx
      x-dead-letter-routing-key: notification.order.events.dlx
      x-max-length: 50000

  - name: inventory.order.events.dlx
    durable: true
    exclusive: false
    auto_delete: false
    arguments:
      x-message-ttl: 604800000  # 7 days retention

bindings:
  - queue: inventory.order.events
    exchange: order.events
    routing_key: "order.#"

  - queue: payment.order.events
    exchange: order.events
    routing_key: "order.created"

  - queue: notification.order.events
    exchange: order.events
    routing_key: "order.*"
```

### Consumer Configuration

```yaml
consumer_settings:
  prefetch_count: 10  # Process up to 10 messages concurrently
  auto_ack: false     # Require explicit acknowledgment
  exclusive: false    # Allow multiple consumers
  no_wait: false

  timeout:
    receive: 30s      # Max time to process one message
    shutdown: 10s     # Max time for graceful shutdown
    reconnect: 5s     # Backoff before reconnect attempt
```

### Monitoring Metrics

```
rabbitmq_queue_messages_total: Messages currently in queue
rabbitmq_queue_messages_acked: Messages acknowledged by consumers
rabbitmq_queue_messages_nacked: Messages negatively acknowledged
rabbitmq_queue_messages_redelivered: Messages redelivered after nack
rabbitmq_consumer_count: Active consumers per queue
rabbitmq_queue_memory_bytes: Memory used by queue
```

## Event Schema Management

### Schema Registry Pattern

```markdown
## Event Schema Registry

All events must be registered in the schema registry before publishing.

### Schema Definition

```json
{
  "namespace": "com.example.order",
  "name": "OrderCreated",
  "type": "record",
  "version": 2,
  "doc": "Published when a customer creates a new order",

  "compatibility_level": "BACKWARD",
  "timestamp": "2025-11-19T00:00:00Z",

  "fields": [
    {
      "name": "event_type",
      "type": "string",
      "doc": "Event type identifier"
    },
    {
      "name": "event_id",
      "type": "string",
      "doc": "Unique event identifier (UUID v4)"
    },
    {
      "name": "event_timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "When event occurred"
    },
    {
      "name": "order_id",
      "type": "string",
      "doc": "Order identifier (UUID v4)"
    },
    {
      "name": "customer_id",
      "type": "string",
      "doc": "Customer identifier (UUID v4)"
    },
    {
      "name": "items",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            { "name": "sku", "type": "string" },
            { "name": "quantity", "type": "int" },
            { "name": "unit_price_cents", "type": "long" },
            { "name": "tax_cents", "type": "long" }
          ]
        }
      }
    },
    {
      "name": "order_total_cents",
      "type": "long",
      "doc": "Total order amount in cents"
    },
    {
      "name": "currency",
      "type": "string",
      "doc": "ISO 4217 currency code",
      "default": "USD"
    },
    {
      "name": "metadata",
      "type": {
        "type": "map",
        "values": "string"
      },
      "doc": "Additional metadata",
      "default": {}
    }
  ]
}
```

### Schema Evolution

```markdown
## Managing Schema Changes

### Adding Optional Fields
- Version: 2.0 → 2.1
- Backward compatible: YES
- Forward compatible: NO
- Example: Adding optional `promotion_code` field
```json
{
  "name": "promotion_code",
  "type": ["null", "string"],
  "default": null,
  "doc": "Applied promotion code if any"
}
```

### Removing Fields
- Version: 2.1 → 3.0
- Backward compatible: NO (breaking change)
- Action: Requires migration period
- Steps:
  1. Release v2.2 that stops publishing the field
  2. Wait 30 days for all consumers to update
  3. Release v3.0 removing field from schema
  4. Retire schema v2.x after 90 days

### Renaming Fields
- Version: 2.1 → 2.2
- Process:
  1. Add new field with new name
  2. Copy data from old field to new field
  3. Deprecate old field (document removal date)
  4. Wait 6 months for consumer migration
  5. Remove old field in major version bump

### Default Values
- Always provide sensible defaults for new fields
- Use null for optional fields without defaults
- Communicate defaults in migration guide
```

## Event Sourcing

### Event Store Documentation

```markdown
## Event Store Implementation

### Append-Only Log Pattern

```
Timeline ────────────────────────────────────────→

Event 1: OrderCreated (T=0s)
├─ order_id: ORD-001
├─ customer_id: CUST-123
└─ total: $99.99

Event 2: PaymentAuthorized (T=2s)
├─ order_id: ORD-001
├─ payment_id: PAY-456
└─ amount: $99.99

Event 3: OrderConfirmed (T=5s)
├─ order_id: ORD-001
└─ confirmation_time: T=5s

Event 4: OrderShipped (T=2d)
├─ order_id: ORD-001
├─ tracking_number: TRK-789
└─ carrier: FedEx
```

### Snapshots

For performance, create snapshots of aggregate state:

```json
{
  "snapshot_version": 1,
  "aggregate_id": "ORD-001",
  "aggregate_type": "Order",
  "snapshot_timestamp": "2025-11-19T14:35:00Z",

  "state": {
    "order_id": "ORD-001",
    "customer_id": "CUST-123",
    "status": "SHIPPED",
    "items": [...],
    "total_cents": 9999,
    "created_at": "2025-11-19T14:32:00Z",
    "confirmed_at": "2025-11-19T14:33:30Z",
    "shipped_at": "2025-11-21T08:00:00Z",
    "tracking_number": "TRK-789"
  },

  "event_count_since_snapshot": 15,
  "last_applied_event_id": "evt-20251119-xyz789"
}
```

### Projections

```markdown
## Materialized Views from Event Stream

### Order Status Projection

Purpose: Provide fast read model for order status queries

Source events:
- OrderCreated
- OrderConfirmed
- OrderShipped
- OrderDelivered
- OrderCancelled

Projection table:
```sql
CREATE TABLE order_status_projection (
  order_id UUID PRIMARY KEY,
  customer_id UUID NOT NULL,
  current_status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  confirmed_at TIMESTAMP,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  last_event_id UUID NOT NULL,
  last_updated TIMESTAMP NOT NULL
);

CREATE INDEX idx_customer_orders ON order_status_projection(customer_id);
CREATE INDEX idx_status ON order_status_projection(current_status);
```

Query example:
```sql
-- Get all pending orders for customer
SELECT order_id, created_at, current_status
FROM order_status_projection
WHERE customer_id = $1 AND current_status IN ('CONFIRMED', 'SHIPPED');
```

### Customer Analytics Projection

Purpose: Track customer spending patterns and behavior

Source events:
- OrderCreated
- OrderConfirmed
- OrderCancelled
- PaymentAuthorized

Materialized view:
```sql
CREATE TABLE customer_analytics_projection (
  customer_id UUID PRIMARY KEY,
  total_orders INT NOT NULL DEFAULT 0,
  total_spent_cents BIGINT NOT NULL DEFAULT 0,
  average_order_value_cents INT,
  last_order_date TIMESTAMP,
  customer_tier VARCHAR(20),
  last_event_id UUID NOT NULL,
  last_updated TIMESTAMP NOT NULL
);

CREATE INDEX idx_tier ON customer_analytics_projection(customer_tier);
```
```

## Choreography vs. Orchestration

### Choreography Pattern

```markdown
## Event-Driven Choreography

Decentralized workflow where each service listens to events and reacts independently.

### Order Fulfillment Choreography

```
Order Service:
  1. Receive CreateOrder command
  2. Create Order aggregate
  3. Publish OrderCreated event
  4. Return to client (async fulfillment continues)

Inventory Service (listening to OrderCreated):
  1. Receive OrderCreated event
  2. Check stock availability
  3. If available: publish InventoryReserved event
  4. If unavailable: publish InventoryFailed event

Payment Service (listening to InventoryReserved):
  1. Receive InventoryReserved event
  2. Authorize payment
  3. Publish PaymentAuthorized event

Fulfillment Service (listening to PaymentAuthorized):
  1. Receive PaymentAuthorized event
  2. Create warehouse pick list
  3. Publish OrderReadyForShipment event

Notification Service (listening to all events):
  1. Listen to OrderCreated → send confirmation email
  2. Listen to PaymentAuthorized → send receipt
  3. Listen to OrderReadyForShipment → send notification
```

### Advantages
- Loosely coupled services
- Easy to add new subscribers
- Services can operate independently
- Natural event-driven model

### Disadvantages
- Complex to understand overall flow
- Difficult debugging across multiple services
- Eventual consistency challenges
- If one service fails, compensation is complex
```

### Orchestration Pattern

```markdown
## Orchestrator-Based Workflow

Centralized conductor service manages the workflow and coordinates other services.

### Order Fulfillment Orchestration

```
┌────────────────────────────────────────┐
│   Order Fulfillment Orchestrator       │
│                                        │
│  1. Wait for CreateOrder command       │
│  2. Send ReserveStock to Inventory     │
│  3. Wait for StockReserved response    │
│  4. Send AuthorizePayment to Payment   │
│  5. Wait for PaymentAuthorized         │
│  6. Send CreatePickList to Fulfillment │
│  7. Wait for PickListCreated           │
│  8. Publish OrderConfirmed event       │
│  9. Handle failures with compensation  │
│                                        │
└────────────────────────────────────────┘
         ↓        ↓         ↓        ↓
    Inventory  Payment  Fulfillment Notification
```

### Saga Pattern (Distributed Transactions)

```json
{
  "saga_id": "saga-20251119-001",
  "saga_type": "OrderFulfillmentSaga",
  "saga_version": 1,

  "steps": [
    {
      "step_id": 1,
      "step_name": "ReserveInventory",
      "service": "inventory-service",
      "status": "COMPLETED",
      "result": {
        "reserved_quantity": 1,
        "reservation_id": "res-123"
      },
      "compensation": {
        "service": "inventory-service",
        "action": "ReleaseReservation",
        "params": {
          "reservation_id": "res-123"
        }
      }
    },
    {
      "step_id": 2,
      "step_name": "AuthorizePayment",
      "service": "payment-service",
      "status": "COMPLETED",
      "result": {
        "authorization_id": "auth-456",
        "amount_cents": 9999
      },
      "compensation": {
        "service": "payment-service",
        "action": "ReverseAuthorization",
        "params": {
          "authorization_id": "auth-456"
        }
      }
    },
    {
      "step_id": 3,
      "step_name": "CreateShipment",
      "service": "fulfillment-service",
      "status": "FAILED",
      "error": "Warehouse unavailable",
      "result": null,
      "compensation": {
        "applied": true,
        "applied_at": "2025-11-19T14:34:00Z"
      }
    }
  ],

  "saga_status": "COMPENSATING",
  "initiated_at": "2025-11-19T14:32:00Z",
  "completed_at": null
}
```

### Advantages
- Clear overall workflow
- Easier to understand and debug
- Good for complex business processes
- Centralized error handling

### Disadvantages
- Orchestrator becomes single point of failure
- Orchestrator service complexity grows
- Tight coupling to orchestrator
- Orchestrator must coordinate all services
```

## Monitoring Event Flows

### Event Flow Tracing

```markdown
## Distributed Tracing for Events

Every event should carry tracing context:

```json
{
  "event_type": "OrderCreated",
  "event_id": "evt-20251119-xyz789",

  "trace_context": {
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "parent_span_id": "00f067aa0ba902b7",
    "span_id": "05e3ac9a45ff6289",
    "trace_flags": "01"
  },

  "... rest of event"
}
```

This enables tracking the complete flow:
- User initiates order (HTTP request)
- Order Service creates order (span 1)
- Order Service publishes event (span 2)
- Inventory Service consumes event (span 3, parent=span 2)
- Inventory Service publishes event (span 4)
- Payment Service consumes event (span 5, parent=span 4)

### Event Flow Dashboard Metrics

```
Event Latency (milliseconds):
- OrderCreated published to first consumption: 50-200ms
- OrderCreated to InventoryReserved: 200-800ms
- OrderCreated to PaymentAuthorized: 800-2000ms
- OrderCreated to OrderConfirmed: 2000-5000ms

Event Throughput:
- OrderCreated: 500 events/min (peak)
- InventoryReserved: 450 events/min (95% success rate)
- PaymentAuthorized: 430 events/min (95.5% of reserved inventory)

Queue Depths:
- order.events: 5,000-10,000 messages (normal)
- inventory.order.events: 100-500 messages
- payment.order.events: 50-200 messages
- notification.order.events: 1,000-3,000 messages

Consumer Lag:
- Inventory consumer: 0-5 second lag
- Payment consumer: 0-10 second lag
- Notification consumer: 0-30 second lag
```

## Error Handling and Dead Letter Queues

### Dead Letter Queue Pattern

```markdown
## Handling Failed Events

When event processing fails:

```
order.events (main queue)
    │
    ├─ Event processing succeeds → ACK
    │
    └─ Event processing fails → NACK
         │
         └─ Redelivery attempt 1 (after 100ms)
              ├─ Success → ACK
              └─ Fail → NACK
                   │
                   └─ Redelivery attempt 2 (after 500ms)
                        ├─ Success → ACK
                        └─ Fail → NACK
                             │
                             └─ Redelivery attempt 3 (after 2000ms)
                                  ├─ Success → ACK
                                  └─ Fail → Send to DLQ
                                       │
                                       └─ inventory.order.events.dlx
                                            (manual review required)
```

### DLQ Configuration

```yaml
dead_letter_queue:
  name: inventory.order.events.dlx
  durable: true
  retention_days: 7

  metadata_tracking:
    original_queue: inventory.order.events
    original_routing_key: order.created
    first_failed_at: timestamp
    failure_reason: "Maximum retries exceeded"
    failure_count: 3
    last_attempted_at: timestamp
    error_message: "Database connection failed"
    error_stacktrace: "..."

  manual_intervention:
    requires_review: true
    review_deadline: 24_hours
    escalation_service: platform-on-call

  reprocessing:
    enabled: true
    reprocess_after_hours: 24
    max_reprocess_attempts: 2
```

### DLQ Monitoring Alert

```
Alert: DLQ Backlog Threshold Exceeded
Condition: Messages in DLQ > 100 for > 5 minutes
Severity: High
Action: Notify service owner and DLQ team
Details:
  - Current DLQ depth: 250 messages
  - Time since first message: 2 hours
  - Failure rate: 15% of all events
  - Common error: "Inventory database unavailable"
Runbook: https://wiki.example.com/dlq-processing
```

## Consumer Documentation

### Consumer Template

```markdown
## Notification Service - Event Consumer

### Service Details
- **Owner**: Notifications Team
- **On-Call**: @notifications-oncall
- **Runbook**: [Notification Service Runbook](./runbooks/notification-service.md)

### Subscriptions

#### OrderCreated Event
- **Exchange**: order.events
- **Routing Key**: order.created
- **Processing**: Send confirmation email
- **Failure Handling**: Retry up to 3 times, then send to DLQ

#### OrderConfirmed Event
- **Exchange**: order.events
- **Routing Key**: order.confirmed
- **Processing**: Send order receipt
- **Failure Handling**: Critical failure (page on-call)

#### OrderShipped Event
- **Exchange**: order.events
- **Routing Key**: order.shipped
- **Processing**: Send shipping notification
- **Failure Handling**: Retry with longer backoff

### Processing SLA
- **Target latency**: < 500ms from event publish to email sent
- **Availability**: 99.9% (1 hour downtime per month acceptable)
- **Max processing time**: 30 seconds per event
- **Parallel consumers**: 5 (configurable)

### Dependency Services
- **SendGrid API**: Email delivery provider
  - Timeout: 5 seconds
  - Rate limit: 10,000 emails/min
  - Retry: 3 attempts with exponential backoff

- **Customer Service**: Retrieve email template preferences
  - Timeout: 2 seconds
  - Circuit breaker: 50% error threshold
  - Fallback: Use default template

### Error Handling
1. **Email validation fails**: Log and skip (non-critical)
2. **SendGrid API unavailable**: Retry with backoff, eventually DLQ
3. **Customer service timeout**: Use default template, send email
4. **Database error**: Transaction rollback, event NACK for redelivery

### Metrics
```
notifications_events_received_total{event_type="OrderCreated"}
notifications_emails_sent_total{event_type="OrderCreated"}
notifications_email_failures_total{error_type="validation_error"}
notifications_event_processing_duration_seconds{quantile="p95"}
notifications_consumer_lag_seconds{queue="notification.order.events"}
```

### Monitoring
- Alert if email send success rate < 99%
- Alert if consumer lag > 60 seconds
- Alert if event processing time > 5 seconds (P99)
```

## Best Practices

### Event Design Checklist

```markdown
## Guidelines for Publishing Events

- [ ] Event has unique event_id (UUID v4)
- [ ] Event has event_timestamp in ISO 8601 UTC format
- [ ] Event has event_type clearly identifying the event
- [ ] Event schema is registered and versioned
- [ ] All required fields have meaningful data
- [ ] Sensitive data is redacted or encrypted
- [ ] Event is idempotent (safe to replay)
- [ ] Event contains trace/correlation IDs
- [ ] Event documentation includes:
    - Trigger conditions
    - Published by which service
    - Consumed by which services
    - Expected frequency and latency
    - Retention policy

### Consumer Guidelines

- [ ] Consumer is idempotent (can handle duplicate events)
- [ ] Consumer has explicit error handling
- [ ] Consumer implements circuit breaker pattern
- [ ] Consumer has timeout for processing
- [ ] Consumer logs event_id for debugging
- [ ] Consumer publishes metrics on events received/processed
- [ ] Consumer has documentation on what triggers it
- [ ] Consumer graceful shutdown implemented
- [ ] Consumer tested with network failures
- [ ] Consumer tested with slow/failed dependencies
```

### Documentation Artifacts

```markdown
## Event Catalog

Maintain a living document of all events in the system:

| Event Name | Publisher | Consumers | Frequency | Retention | Schema Version |
|---|---|---|---|---|---|
| OrderCreated | order-service | inventory, payment, notification | 500/min | 30 days | 2.1 |
| OrderConfirmed | order-service | inventory, notification | 450/min | 30 days | 1.0 |
| InventoryReserved | inventory-service | order, fulfillment | 400/min | 30 days | 1.2 |
| PaymentAuthorized | payment-service | order, fulfillment | 430/min | 30 days | 1.0 |
| OrderShipped | fulfillment-service | notification, analytics | 400/min | 90 days | 1.1 |

## Consumer Implementation Matrix

Shows which services are consuming which events:

```
         │ Order│Inventory│Payment│Fulfillment│Notification│Analytics
         │      │         │       │           │            │
OrderCreated │ X  │    X    │   X   │      -    │      X     │    X
OrderConfirmed│X  │    X    │   -   │      -    │      X     │    X
InventoryReserved│-│   -    │   X   │      X    │      -     │    X
PaymentAuthorized│X│   -    │   -   │      X    │      X     │    X
OrderShipped │ -  │    -    │   -   │      -    │      X     │    X
```
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Author**: Platform Architecture Team
**Review Frequency**: Quarterly
