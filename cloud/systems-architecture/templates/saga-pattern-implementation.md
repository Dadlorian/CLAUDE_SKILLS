# Saga Pattern Implementation Guide: [Saga Name]

**Business Process**: [Name of the business process this saga orchestrates]
**Date**: YYYY-MM-DD
**Author**: [Name]
**Status**: [Design | Implementation | Production]
**Saga Type**: [Choreography | Orchestration]

---

## Business Overview

### Purpose
[Describe the business process this saga implements in 2-3 sentences]

### Example Scenario
[Concrete example of the business process]
```
Example: E-commerce Order Saga
User places an order → Process payment → Reserve inventory → Create shipment
If any step fails, compensate previous steps (refund payment, release inventory)
```

### Success Criteria
What constitutes successful completion:
- [ ] [Criterion 1: e.g., Order confirmed and customer notified]
- [ ] [Criterion 2: e.g., Payment captured]
- [ ] [Criterion 3: e.g., Inventory reserved]
- [ ] [Criterion 4: e.g., Shipment created]

### Failure Scenarios
What can go wrong and how we handle it:
1. **[Failure 1]**: [e.g., Payment declined] → Compensation: [Cancel order]
2. **[Failure 2]**: [e.g., Out of stock] → Compensation: [Refund payment, cancel order]
3. **[Failure 3]**: [e.g., Shipping unavailable] → Compensation: [Release inventory, refund payment, cancel order]

---

## Saga Pattern Selection

### Choreography vs. Orchestration

**Selected Pattern**: [Choreography | Orchestration]

#### If Choreography

**Why Chosen**:
- ✅ [Reason 1: e.g., Loose coupling between services]
- ✅ [Reason 2: e.g., Services are autonomous]
- ✅ [Reason 3: e.g., Simple workflow with few steps]

**Trade-offs Accepted**:
- ❌ [Trade-off 1: e.g., Harder to trace complete saga flow]
- ❌ [Trade-off 2: e.g., Potential cyclic dependencies]
- ❌ [Trade-off 3: e.g., Distributed business logic]

#### If Orchestration

**Why Chosen**:
- ✅ [Reason 1: e.g., Complex workflow with many steps]
- ✅ [Reason 2: e.g., Need centralized visibility]
- ✅ [Reason 3: e.g., Multiple conditional branches]

**Trade-offs Accepted**:
- ❌ [Trade-off 1: e.g., Central orchestrator is potential bottleneck]
- ❌ [Trade-off 2: e.g., Services are less autonomous]
- ❌ [Trade-off 3: e.g., Orchestrator contains business logic]

---

## Choreography-Based Saga Design

[Use this section if you selected Choreography pattern]

### Participating Services

| Service | Role | Commands Handled | Events Published |
|---------|------|------------------|------------------|
| [Service1] | [Role] | [Command1, Command2] | [Event1, Event2] |
| [Service2] | [Role] | [Command1] | [Event1, Event2] |
| [Service3] | [Role] | [Command1] | [Event1, Event2] |

---

### Event Flow Diagram

```
[Service1]: Receives initial trigger
     |
     | Publishes: Event1 (e.g., OrderPlaced)
     |
     v
[Service2]: Listens for Event1
     |
     | Executes: [Action, e.g., ProcessPayment]
     | Publishes: Event2 (e.g., PaymentProcessed) OR Event2-Failed
     |
     v
[Service3]: Listens for Event2
     |
     | Executes: [Action, e.g., ReserveInventory]
     | Publishes: Event3 (e.g., InventoryReserved) OR Event3-Failed
     |
     v
[Service4]: Listens for Event3
     |
     | Executes: [Action, e.g., CreateShipment]
     | Publishes: Event4 (e.g., ShipmentCreated)
```

---

### Happy Path Event Chain

**Step 1**: [Service1] - [Action]
```
Event Published:
{
  "eventType": "[EventName1]",
  "aggregateId": "[id]",
  "payload": {
    "[field]": "[value]"
  }
}
Topic: [topic-name]
```

**Step 2**: [Service2] - [Action]
```
Triggered By: [EventName1]

Logic:
  1. [Step 1]
  2. [Step 2]
  3. If successful → Publish [EventName2]
     If failure → Publish [EventName2-Failed]

Event Published:
{
  "eventType": "[EventName2]",
  "aggregateId": "[id]",
  "payload": {
    "[field]": "[value]"
  }
}
Topic: [topic-name]
```

**Step 3**: [Service3] - [Action]
```
Triggered By: [EventName2]

[Continue pattern for each step...]
```

---

### Compensation Flow

**Trigger**: [What triggers compensation, e.g., InventoryReservationFailed event]

**Compensation Chain**:
```
[Service3] publishes: InventoryReservationFailed
     |
     v
[Service2] listens for InventoryReservationFailed
     |
     | Executes: RefundPayment
     | Publishes: PaymentRefunded
     |
     v
[Service1] listens for PaymentRefunded
     |
     | Executes: CancelOrder
     | Publishes: OrderCancelled
```

**Compensation Events**:

| Original Event | Compensation Event | Service | Compensation Action |
|----------------|-------------------|---------|---------------------|
| [Event1] | [CompensationEvent1] | [Service] | [Action to undo] |
| [Event2] | [CompensationEvent2] | [Service] | [Action to undo] |
| [Event3] | [CompensationEvent3] | [Service] | [Action to undo] |

---

### Implementation Example (Choreography)

#### Service 1: Order Service

**Event Publisher**:
```java
@Service
public class OrderService {
  @Autowired
  private OrderRepository orderRepository;

  @Autowired
  private EventPublisher eventPublisher;

  @Transactional
  public Order placeOrder(PlaceOrderCommand command) {
    // Create order
    Order order = Order.create(
      command.customerId(),
      command.items()
    );

    // Save to database
    orderRepository.save(order);

    // Publish event
    OrderPlacedEvent event = new OrderPlacedEvent(
      order.id(),
      order.customerId(),
      order.totalAmount()
    );

    eventPublisher.publish("order-events", event);

    return order;
  }
}
```

**Event Consumer (for compensation)**:
```java
@Service
public class OrderEventConsumer {
  @Autowired
  private OrderRepository orderRepository;

  @KafkaListener(topics = "payment-events")
  public void handlePaymentFailed(PaymentFailedEvent event) {
    Order order = orderRepository.findById(event.orderId());

    // Compensate: Cancel order
    order.cancel("Payment failed");

    orderRepository.save(order);

    // Publish compensation event
    eventPublisher.publish("order-events", new OrderCancelledEvent(order.id()));
  }
}
```

---

#### Service 2: Payment Service

**Event Consumer + Publisher**:
```java
@Service
public class PaymentEventConsumer {
  @Autowired
  private PaymentService paymentService;

  @Autowired
  private EventPublisher eventPublisher;

  @KafkaListener(topics = "order-events")
  @Transactional
  public void handleOrderPlaced(OrderPlacedEvent event) {
    try {
      // Process payment
      Payment payment = paymentService.processPayment(
        event.orderId(),
        event.customerId(),
        event.totalAmount()
      );

      // Publish success event
      eventPublisher.publish("payment-events", new PaymentProcessedEvent(
        payment.id(),
        event.orderId(),
        payment.amount()
      ));

    } catch (PaymentException e) {
      // Publish failure event (triggers compensation)
      eventPublisher.publish("payment-events", new PaymentFailedEvent(
        event.orderId(),
        e.getReason()
      ));
    }
  }

  @KafkaListener(topics = "inventory-events")
  @Transactional
  public void handleInventoryReservationFailed(InventoryReservationFailedEvent event) {
    // Compensate: Refund payment
    Payment payment = paymentService.findByOrderId(event.orderId());
    paymentService.refund(payment.id());

    eventPublisher.publish("payment-events", new PaymentRefundedEvent(
      payment.id(),
      event.orderId()
    ));
  }
}
```

---

## Orchestration-Based Saga Design

[Use this section if you selected Orchestration pattern]

### Orchestrator Service

**Service Name**: [e.g., OrderSagaOrchestrator]
**Technology**: [e.g., AWS Step Functions | Temporal | Camunda | Custom]
**Location**: [Repository, module]

---

### State Machine Definition

**States**:
1. **[StateName1]**: [Description, e.g., ProcessPayment]
2. **[StateName2]**: [Description, e.g., ReserveInventory]
3. **[StateName3]**: [Description, e.g., CreateShipment]
4. **[CompensationState1]**: [Description, e.g., RefundPayment]
5. **[CompensationState2]**: [Description, e.g., ReleaseInventory]

**Transitions**:
```
Start
  |
  v
ProcessPayment
  |--Success--> ReserveInventory
  |--Failure--> End (Failed)

ReserveInventory
  |--Success--> CreateShipment
  |--Failure--> RefundPayment --> End (Compensated)

CreateShipment
  |--Success--> End (Completed)
  |--Failure--> ReleaseInventory --> RefundPayment --> End (Compensated)
```

---

### State Definitions

#### State: ProcessPayment

**Type**: Task
**Service Called**: PaymentService
**Operation**: POST /api/v1/payments

**Input**:
```json
{
  "orderId": "{{orderId}}",
  "customerId": "{{customerId}}",
  "amount": "{{totalAmount}}"
}
```

**Success Output**:
```json
{
  "paymentId": "uuid",
  "status": "PROCESSED"
}
```

**Failure Handling**:
- Retry: 3 attempts with exponential backoff
- On final failure: Transition to End (Failed)

**Timeout**: 30 seconds

---

#### State: ReserveInventory

**Type**: Task
**Service Called**: InventoryService
**Operation**: POST /api/v1/inventory/reservations

**Input**:
```json
{
  "orderId": "{{orderId}}",
  "items": "{{orderItems}}"
}
```

**Success Output**:
```json
{
  "reservationId": "uuid",
  "status": "RESERVED"
}
```

**Failure Handling**:
- No retry (inventory is or isn't available)
- On failure: Transition to RefundPayment (compensation)

**Timeout**: 10 seconds

---

#### State: CreateShipment

**Type**: Task
**Service Called**: ShippingService
**Operation**: POST /api/v1/shipments

**Input**:
```json
{
  "orderId": "{{orderId}}",
  "reservationId": "{{reservationId}}",
  "address": "{{shippingAddress}}"
}
```

**Success Output**:
```json
{
  "shipmentId": "uuid",
  "status": "CREATED"
}
```

**Failure Handling**:
- Retry: 2 attempts
- On final failure: Transition to ReleaseInventory (compensation)

**Timeout**: 15 seconds

---

#### Compensation State: RefundPayment

**Type**: Compensation Task
**Service Called**: PaymentService
**Operation**: POST /api/v1/payments/{{paymentId}}/refund

**Input**:
```json
{
  "paymentId": "{{paymentId}}",
  "reason": "Saga compensation"
}
```

**Success Output**:
```json
{
  "refundId": "uuid",
  "status": "REFUNDED"
}
```

**Failure Handling**:
- Retry: 5 attempts with exponential backoff
- Alert on-call if compensation fails (manual intervention needed)

---

#### Compensation State: ReleaseInventory

**Type**: Compensation Task
**Service Called**: InventoryService
**Operation**: DELETE /api/v1/inventory/reservations/{{reservationId}}

**Input**:
```json
{
  "reservationId": "{{reservationId}}"
}
```

**Success Output**:
```json
{
  "status": "RELEASED"
}
```

**Failure Handling**:
- Retry: 5 attempts
- Alert if fails (manual cleanup may be needed)

---

### Implementation Example (Orchestration)

#### AWS Step Functions State Machine

```json
{
  "Comment": "Order Saga Orchestration",
  "StartAt": "ProcessPayment",
  "States": {
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:ProcessPayment",
      "TimeoutSeconds": 30,
      "Retry": [
        {
          "ErrorEquals": ["TransientError"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "ResultPath": "$.error",
          "Next": "SagaFailed"
        }
      ],
      "ResultPath": "$.paymentResult",
      "Next": "ReserveInventory"
    },

    "ReserveInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:ReserveInventory",
      "TimeoutSeconds": 10,
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "ResultPath": "$.error",
          "Next": "RefundPayment"
        }
      ],
      "ResultPath": "$.inventoryResult",
      "Next": "CreateShipment"
    },

    "CreateShipment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:CreateShipment",
      "TimeoutSeconds": 15,
      "Retry": [
        {
          "ErrorEquals": ["TransientError"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "ResultPath": "$.error",
          "Next": "ReleaseInventory"
        }
      ],
      "ResultPath": "$.shipmentResult",
      "Next": "SagaCompleted"
    },

    "ReleaseInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:ReleaseInventory",
      "TimeoutSeconds": 10,
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 5,
          "BackoffRate": 2.0
        }
      ],
      "ResultPath": "$.compensationResult",
      "Next": "RefundPayment"
    },

    "RefundPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456:function:RefundPayment",
      "TimeoutSeconds": 30,
      "Retry": [
        {
          "ErrorEquals": ["States.ALL"],
          "IntervalSeconds": 2,
          "MaxAttempts": 5,
          "BackoffRate": 2.0
        }
      ],
      "ResultPath": "$.compensationResult",
      "Next": "SagaCompensated"
    },

    "SagaCompleted": {
      "Type": "Succeed"
    },

    "SagaCompensated": {
      "Type": "Fail",
      "Error": "SagaCompensated",
      "Cause": "Saga was compensated due to failure"
    },

    "SagaFailed": {
      "Type": "Fail",
      "Error": "SagaFailed",
      "Cause": "Saga failed and compensation not possible"
    }
  }
}
```

---

#### Temporal Workflow (Alternative)

```java
@WorkflowInterface
public interface OrderSagaWorkflow {
  @WorkflowMethod
  OrderResult processOrder(OrderRequest request);
}

@WorkflowImpl(workflowType = "OrderSaga")
public class OrderSagaWorkflowImpl implements OrderSagaWorkflow {

  private final ActivityStub activities = Workflow.newActivityStub(
    OrderSagaActivities.class,
    ActivityOptions.newBuilder()
      .setStartToCloseTimeout(Duration.ofSeconds(30))
      .build()
  );

  @Override
  public OrderResult processOrder(OrderRequest request) {
    Saga saga = new Saga(new Saga.Options.Builder().build());

    try {
      // Step 1: Process Payment
      PaymentResult payment = activities.processPayment(
        request.orderId(),
        request.customerId(),
        request.amount()
      );
      saga.addCompensation(() -> activities.refundPayment(payment.paymentId()));

      // Step 2: Reserve Inventory
      InventoryResult inventory = activities.reserveInventory(
        request.orderId(),
        request.items()
      );
      saga.addCompensation(() -> activities.releaseInventory(inventory.reservationId()));

      // Step 3: Create Shipment
      ShipmentResult shipment = activities.createShipment(
        request.orderId(),
        inventory.reservationId(),
        request.shippingAddress()
      );

      return OrderResult.success(request.orderId(), shipment.shipmentId());

    } catch (Exception e) {
      // Compensate all previous steps
      saga.compensate();
      return OrderResult.failed(request.orderId(), e.getMessage());
    }
  }
}

@ActivityInterface
public interface OrderSagaActivities {
  PaymentResult processPayment(String orderId, String customerId, Money amount);
  void refundPayment(String paymentId);

  InventoryResult reserveInventory(String orderId, List<OrderItem> items);
  void releaseInventory(String reservationId);

  ShipmentResult createShipment(String orderId, String reservationId, Address address);
}
```

---

## Data Consistency & Idempotency

### Idempotency Keys

**Why Needed**: Prevent duplicate processing if message delivered multiple times

**Implementation**:
```java
@Service
public class PaymentService {
  @Autowired
  private ProcessedMessagesRepository processedMessages;

  @Transactional
  public PaymentResult processPayment(String idempotencyKey, PaymentRequest request) {
    // Check if already processed
    if (processedMessages.exists(idempotencyKey)) {
      return processedMessages.getResult(idempotencyKey);
    }

    // Process payment
    PaymentResult result = doProcessPayment(request);

    // Store idempotency key + result
    processedMessages.save(idempotencyKey, result);

    return result;
  }
}
```

**Idempotency Key Strategy**:
- Use: Event ID or deterministic key (e.g., SHA256 of event payload)
- Store: In database with TTL (e.g., 7 days)
- Clean up: Async job to remove old keys

---

### Eventual Consistency Handling

**Read-Your-Writes Consistency**:
```java
// Problem: User places order, immediately views order status
// Solution: Return order status from command response, not query

@PostMapping("/orders")
public OrderResponse placeOrder(@RequestBody PlaceOrderRequest request) {
  Order order = orderService.placeOrder(request);

  // Return full order state immediately (not eventual)
  return OrderResponse.fromOrder(order);
}
```

**Stale Read Protection**:
- Version numbers on aggregates
- Optimistic locking
- Return "last known state" timestamps

---

### Saga State Persistence

**Orchestration**: State machine state persisted automatically
- AWS Step Functions: Managed by AWS
- Temporal: Durable event sourcing
- Custom: Store in database

**Choreography**: Each service stores its own state
```sql
CREATE TABLE saga_participants (
  id UUID PRIMARY KEY,
  saga_id UUID NOT NULL,
  service_name VARCHAR(50),
  step_name VARCHAR(50),
  status VARCHAR(20), -- PENDING, COMPLETED, COMPENSATED, FAILED
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  compensation_data JSONB
);

CREATE INDEX idx_saga_id ON saga_participants(saga_id);
```

---

## Observability & Monitoring

### Distributed Tracing

**Trace Context Propagation**:
```java
// Include in all events and commands
{
  "eventId": "uuid",
  "eventType": "OrderPlaced",
  "payload": { ... },
  "metadata": {
    "traceId": "abc123",      // Saga trace ID
    "parentSpanId": "def456",  // Parent span
    "spanId": "ghi789"         // This event's span
  }
}
```

**Tools**: Jaeger, Zipkin, AWS X-Ray

---

### Saga Metrics

**Key Metrics**:
```
saga_total{saga_name, status}                  # Counter
saga_duration_seconds{saga_name, status}       # Histogram
saga_step_duration_seconds{saga_name, step}    # Histogram
saga_compensation_total{saga_name, reason}     # Counter
```

**Dashboards**:
- Saga success rate over time
- P95/P99 saga duration
- Compensation rate by reason
- Step-level latency breakdown

---

### Logging

**Required Log Events**:
```
INFO: Saga started (saga_id, saga_type, input)
INFO: Step started (saga_id, step_name)
INFO: Step completed (saga_id, step_name, duration)
WARN: Step failed, compensating (saga_id, step_name, error)
INFO: Compensation completed (saga_id, step_name)
ERROR: Compensation failed (saga_id, step_name, error)
INFO: Saga completed (saga_id, status, duration)
```

**Example**:
```json
{
  "timestamp": "2025-11-19T10:30:00Z",
  "level": "INFO",
  "message": "Saga step completed",
  "saga_id": "saga-123",
  "saga_type": "OrderSaga",
  "step_name": "ProcessPayment",
  "duration_ms": 245,
  "status": "SUCCESS"
}
```

---

### Alerts

**Critical Alerts**:
- Compensation failure rate > 5%
- Saga timeout rate > 1%
- Step X failure rate > 10%

**Warning Alerts**:
- Saga P95 latency > [threshold]
- Compensation rate > 20%

---

## Testing Strategy

### Unit Tests
Test each saga step in isolation with mocks

```java
@Test
public void shouldProcessPaymentSuccessfully() {
  // Arrange
  PaymentRequest request = new PaymentRequest(orderId, amount);
  when(paymentGateway.charge(any())).thenReturn(new PaymentResult("pay-123"));

  // Act
  PaymentResult result = paymentService.processPayment(request);

  // Assert
  assertThat(result.status()).isEqualTo(PaymentStatus.PROCESSED);
  verify(paymentRepository).save(any(Payment.class));
}
```

---

### Integration Tests
Test saga flow end-to-end with test doubles

```java
@SpringBootTest
@Testcontainers
public class OrderSagaIntegrationTest {
  @Container
  static KafkaContainer kafka = new KafkaContainer();

  @Test
  public void shouldCompleteOrderSagaSuccessfully() {
    // Arrange
    PlaceOrderCommand command = new PlaceOrderCommand(...);

    // Act
    orderService.placeOrder(command);

    // Assert: Wait for saga completion
    await().atMost(10, SECONDS).until(() ->
      orderRepository.findById(orderId).get().status() == OrderStatus.CONFIRMED
    );

    assertThat(paymentRepository.findByOrderId(orderId)).isPresent();
    assertThat(inventoryRepository.findReservation(orderId)).isPresent();
  }

  @Test
  public void shouldCompensateWhenInventoryUnavailable() {
    // Arrange: Set up inventory to be out of stock
    inventoryService.setAvailable(productId, false);

    // Act
    orderService.placeOrder(command);

    // Assert: Payment should be refunded, order cancelled
    await().atMost(10, SECONDS).until(() ->
      orderRepository.findById(orderId).get().status() == OrderStatus.CANCELLED
    );

    Payment payment = paymentRepository.findByOrderId(orderId).get();
    assertThat(payment.status()).isEqualTo(PaymentStatus.REFUNDED);
  }
}
```

---

### Chaos Testing
Inject failures to validate compensation

**Test Scenarios**:
1. Kill service mid-transaction → Saga should retry or compensate
2. Introduce network latency → Saga should timeout and compensate
3. Database unavailable → Saga should fail gracefully
4. Message broker down → Saga should retry with exponential backoff

---

## Rollout Plan

### Phase 1: Design & Build (Week 1-2)
- [ ] Design saga state machine
- [ ] Implement orchestrator or event handlers
- [ ] Write unit tests
- [ ] Document ADR

### Phase 2: Integration Testing (Week 3)
- [ ] Set up test environment
- [ ] Integration tests (happy path + compensation)
- [ ] Chaos tests

### Phase 3: Staging Deployment (Week 4)
- [ ] Deploy to staging
- [ ] Manual testing
- [ ] Performance testing (load test with 2x expected traffic)
- [ ] Observability validation (dashboards, alerts)

### Phase 4: Production Rollout (Week 5)
- [ ] Dark launch (process events, don't commit)
- [ ] Canary: 5% traffic for 24 hours
- [ ] Expand: 25% → 50% → 100% (daily increments)
- [ ] Monitor compensation rate

### Phase 5: Optimization (Week 6+)
- [ ] Tune timeouts based on observed latencies
- [ ] Optimize database queries
- [ ] Reduce saga duration (target: [X]ms P95)

---

## Operational Runbook

### Stuck Saga
**Symptoms**: Saga not progressing, stuck in PENDING state

**Diagnosis**:
1. Check saga state (AWS Step Functions console or database)
2. Check last completed step
3. Review logs for errors

**Resolution**:
- If retryable error: Trigger retry
- If stuck waiting for event: Manually publish event or compensate
- If corrupted state: Manual intervention (compensate and notify customer)

---

### High Compensation Rate
**Symptoms**: > 20% of sagas are compensating

**Diagnosis**:
1. Check which step is failing most
2. Review error logs for that service
3. Check service health and dependencies

**Resolution**:
- If service issue: Fix underlying service
- If data issue: Validate input data quality
- If capacity issue: Scale up service

---

### Compensation Failure
**Symptoms**: Alert "Compensation failed for saga-123"

**Diagnosis**:
1. Check compensation logs
2. Identify which compensation step failed
3. Determine if retryable or manual intervention needed

**Resolution**:
- If retryable: Trigger manual retry
- If not retryable: Manual compensation required
  - Create support ticket
  - Manually refund customer
  - Update saga state to COMPENSATED_MANUALLY

---

## References

- **Architecture Decision Record**: [Link to ADR]
- **Service Specifications**: [Links to participating services]
- **Event Schemas**: [Link to schema registry]
- **Observability Dashboard**: [Link to Grafana/Datadog]
- **On-Call Runbook**: [Link to full runbook]

---

## Change History

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial saga design | [Name] |
| YYYY-MM-DD | Added timeout tuning after prod analysis | [Name] |

---

**Last Updated**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD
