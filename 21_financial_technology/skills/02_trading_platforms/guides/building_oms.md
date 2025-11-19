# Building an Order Management System (OMS) Guide

## System Architecture Overview

A production OMS must support:
- Order creation, modification, cancellation
- Multi-venue order routing
- Real-time position tracking
- Risk limit enforcement
- Complete audit trail
- Sub-millisecond response times

## Step 1: Define Order State Machine

```java
public enum OrderStatus {
    NEW,
    ACCEPTED,
    PARTIALLY_FILLED,
    FILLED,
    PENDING_AMENDMENT,
    AMENDED,
    PENDING_CANCEL,
    CANCELED,
    REJECTED,
    EXPIRED,
    SUSPENDED
}

public class OrderStateMachine {
    private OrderStatus currentStatus;
    private final AtomicReference<OrderStatus> statusRef =
        new AtomicReference<>(OrderStatus.NEW);

    public boolean transition(OrderStatus targetStatus) {
        // Validate transition
        if (!isValidTransition(currentStatus, targetStatus)) {
            return false;
        }

        // Atomic state change
        boolean success = statusRef.compareAndSet(currentStatus, targetStatus);
        if (success) {
            auditLog.record("Order status change: " +
                currentStatus + " -> " + targetStatus);
        }
        return success;
    }

    private boolean isValidTransition(OrderStatus from, OrderStatus to) {
        // State machine rules
        Map<OrderStatus, Set<OrderStatus>> validTransitions =
            Map.ofEntries(
                entry(NEW, Set.of(ACCEPTED, REJECTED)),
                entry(ACCEPTED, Set.of(PARTIALLY_FILLED, FILLED, CANCELED, REJECTED)),
                entry(PARTIALLY_FILLED, Set.of(FILLED, CANCELED, PENDING_AMENDMENT)),
                entry(PENDING_AMENDMENT, Set.of(AMENDED, CANCELED)),
                entry(AMENDED, Set.of(PARTIALLY_FILLED, FILLED, CANCELED))
            );

        return validTransitions
            .getOrDefault(from, Set.of())
            .contains(to);
    }
}
```

## Step 2: Implement Order Entry Module

```java
@Service
public class OrderEntryService {
    private final OrderValidationService validationService;
    private final RiskManagementService riskService;
    private final OrderBookRepository orderBook;
    private final FIXSessionManager fixManager;

    public OrderResponse submitOrder(OrderRequest request) {
        // 1. Validate order
        ValidationResult validation = validationService.validate(request);
        if (!validation.isValid()) {
            return OrderResponse.rejected(validation.getReasonCode());
        }

        // 2. Check risk limits
        RiskCheckResult riskCheck = riskService.checkPreTradeRisk(request);
        if (!riskCheck.isApproved()) {
            return OrderResponse.rejected("RISK_LIMIT_EXCEEDED");
        }

        // 3. Create order object
        Order order = new Order.Builder()
            .orderId(generateOrderId())
            .account(request.getAccount())
            .security(request.getSecurity())
            .side(request.getSide())
            .quantity(request.getQuantity())
            .orderType(request.getOrderType())
            .limitPrice(request.getLimitPrice())
            .timeInForce(request.getTimeInForce())
            .timestamp(System.nanoTime())
            .build();

        // 4. Store order
        orderBook.save(order);

        // 5. Route to venue
        VenueRoutingDecision routing =
            selectBestVenue(order);
        FIXSession session = fixManager.getSession(routing.getVenue());

        try {
            // 6. Send to exchange
            ExchangeOrderId exchangeId = session.sendNewOrder(order);
            order.setExchangeOrderId(exchangeId);
            order.setStatus(OrderStatus.NEW);

            return OrderResponse.accepted(order.getOrderId(), exchangeId);

        } catch (Exception e) {
            orderBook.updateStatus(order.getOrderId(), OrderStatus.REJECTED);
            return OrderResponse.rejected("EXCHANGE_REJECTION");
        }
    }

    private VenueRoutingDecision selectBestVenue(Order order) {
        // Smart routing logic
        List<Venue> eligibleVenues =
            venueSelector.getEligibleVenues(order.getSecurity());

        return eligibleVenues.stream()
            .map(venue -> new VenueScore(
                venue,
                calculateSpread(venue),
                estimateMarketImpact(venue, order.getQuantity()),
                getLatency(venue)
            ))
            .min(Comparator.comparingDouble(VenueScore::getTotalCost))
            .map(VenueScore::getVenue)
            .map(v -> new VenueRoutingDecision(v))
            .orElse(new VenueRoutingDecision(defaultVenue));
    }
}
```

## Step 3: Implement Amendment Handling

```java
public class OrderAmendmentService {
    private final OrderBookRepository orderBook;
    private final FIXSessionManager fixManager;

    public AmendmentResponse amendOrder(OrderAmendmentRequest request) {
        Order order = orderBook.findById(request.getOrderId());
        if (order == null) {
            return AmendmentResponse.rejected("ORDER_NOT_FOUND");
        }

        // Validate amendment is possible
        if (!canAmend(order)) {
            return AmendmentResponse.rejected(
                "CANNOT_AMEND_ORDER_IN_STATUS: " + order.getStatus());
        }

        // Apply amendment
        Order amendedOrder = order.toBuilder()
            .quantity(request.getNewQuantity() != null ?
                request.getNewQuantity() : order.getQuantity())
            .limitPrice(request.getNewPrice() != null ?
                request.getNewPrice() : order.getLimitPrice())
            .build();

        // Send to exchange
        FIXSession session = fixManager.getSession(order.getVenue());
        try {
            session.sendOrderCancelReplaceRequest(order, amendedOrder);
            orderBook.updateOrder(amendedOrder);
            return AmendmentResponse.accepted(amendedOrder);
        } catch (Exception e) {
            return AmendmentResponse.rejected("EXCHANGE_REJECTION");
        }
    }

    private boolean canAmend(Order order) {
        return Set.of(
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIALLY_FILLED
        ).contains(order.getStatus());
    }
}
```

## Step 4: Implement Execution Report Processing

```java
@Component
public class ExecutionReportProcessor {
    private final OrderBookRepository orderBook;
    private final TradeRecordingService tradeRecorder;
    private final PositionTracker positionTracker;
    private final EventPublisher eventPublisher;

    @FIXMessageHandler(MsgType = "8")  // Execution Report
    public void processExecutionReport(ExecutionReport report) {
        Order order = orderBook.findByExchangeId(report.getOrderId());
        if (order == null) {
            logWarning("Execution report for unknown order: " +
                report.getOrderId());
            return;
        }

        // Update order status
        switch (report.getOrderStatus()) {
            case PARTIALLY_FILLED:
                updatePartialFill(order, report);
                break;

            case FILLED:
                updateFullFill(order, report);
                break;

            case REJECTED:
                updateRejection(order, report);
                break;

            case CANCELED:
                updateCancellation(order, report);
                break;
        }

        // Emit events for downstream processing
        eventPublisher.publishOrderStatusChanged(
            new OrderStatusChangeEvent(order.getOrderId(),
                order.getStatus(), report.getTimestamp())
        );
    }

    private void updatePartialFill(Order order, ExecutionReport report) {
        // Record trade
        Trade trade = new Trade.Builder()
            .orderId(order.getOrderId())
            .quantity(report.getLastQuantity())
            .executionPrice(report.getLastExecutionPrice())
            .executionTime(report.getTransactionTime())
            .build();

        tradeRecorder.recordTrade(trade);

        // Update order
        order.addFill(trade);
        order.setStatus(OrderStatus.PARTIALLY_FILLED);
        orderBook.updateOrder(order);

        // Update position
        positionTracker.updatePosition(
            order.getAccount(),
            order.getSecurity(),
            order.getSide(),
            report.getLastQuantity(),
            report.getLastExecutionPrice()
        );
    }

    private void updateFullFill(Order order, ExecutionReport report) {
        updatePartialFill(order, report);
        order.setStatus(OrderStatus.FILLED);
        orderBook.updateOrder(order);
    }
}
```

## Step 5: Implement Audit Trail

```java
@Component
public class AuditTrailService {
    private final AuditLogRepository auditLog;

    public void logOrderCreation(Order order) {
        logEvent("ORDER_CREATED", order.getOrderId(),
            "Order created: " + order.toString(),
            order.getTimestamp());
    }

    public void logOrderModification(Order before, Order after) {
        logEvent("ORDER_MODIFIED", after.getOrderId(),
            "Price changed from " + before.getLimitPrice() +
            " to " + after.getLimitPrice(),
            System.nanoTime());
    }

    public void logOrderCancellation(Order order, String reason) {
        logEvent("ORDER_CANCELED", order.getOrderId(),
            "Reason: " + reason,
            System.nanoTime());
    }

    public void logExecution(Order order, Trade trade) {
        logEvent("TRADE_EXECUTED", order.getOrderId(),
            "Executed " + trade.getQuantity() + " @ " +
            trade.getExecutionPrice(),
            trade.getExecutionTime());
    }

    private void logEvent(String eventType, String orderId,
                          String description, long timestamp) {
        AuditEntry entry = new AuditEntry.Builder()
            .eventType(eventType)
            .orderId(orderId)
            .description(description)
            .timestamp(timestamp)
            .userId(getCurrentUser())
            .ipAddress(getCurrentIpAddress())
            .sessionId(getCurrentSession())
            .build();

        auditLog.save(entry);
    }
}
```

## Step 6: Performance Optimization

### Key Considerations
1. **Latency**: <500µs from order entry to exchange send
2. **Throughput**: 50K+ orders/second
3. **Memory**: Efficient storage for millions of orders
4. **Lock-Free**: Use concurrent data structures

### Implementation Tips

```java
// Use lock-free data structures
ConcurrentHashMap<Long, Order> orders = new ConcurrentHashMap<>();

// Pre-allocate object pools
ObjectPool<Order> orderPool = new ObjectPool<>(10000);

// Use atomic operations
AtomicLong nextOrderId = new AtomicLong(0);

// Avoid allocations in hot path
// Reuse StringBuilder for string operations
StringBuilder sb = new StringBuilder();

// Use timestamps efficiently
long nanoTime = System.nanoTime();

// Batch writes to disk
BatchingAuditLog auditLog = new BatchingAuditLog(10000);
```

## Step 7: Testing & Validation

```java
@Test
public void testOrderLifecycle() {
    // Create order
    OrderRequest request = new OrderRequest(
        "AAPL", Side.BUY, 1000, 150.50, OrderType.LIMIT);
    OrderResponse response = service.submitOrder(request);

    assertNotNull(response.getOrderId());
    assertEquals(OrderStatus.NEW, response.getStatus());

    // Amendment
    AmendmentRequest amendment = new AmendmentRequest(
        response.getOrderId(), 1500, 150.25);
    AmendmentResponse amendResult = service.amend(amendment);

    assertTrue(amendResult.isSuccess());

    // Verify state
    Order order = orderBook.findById(response.getOrderId());
    assertEquals(1500, order.getQuantity());
    assertEquals(150.25, order.getLimitPrice());
}

@Test
public void testConcurrentOrderSubmission() {
    ExecutorService executor = Executors.newFixedThreadPool(100);

    for (int i = 0; i < 10000; i++) {
        executor.submit(() -> {
            OrderRequest request = generateRandomOrder();
            service.submitOrder(request);
        });
    }

    executor.awaitTermination(10, TimeUnit.SECONDS);

    // Verify all orders processed
    assertEquals(10000, orderBook.count());
}
```

## Production Deployment Checklist

- [ ] Load test with expected peak volume
- [ ] Latency measurement and monitoring in place
- [ ] Redundant FIX session connectivity
- [ ] Order reconciliation with exchange
- [ ] Comprehensive audit trail
- [ ] Real-time monitoring and alerting
- [ ] Disaster recovery procedures
- [ ] Regulatory compliance verified
- [ ] Compliance systems integration
- [ ] 24/7 operations support

## Key Metrics to Monitor

1. **Order Latency**: P50, P95, P99 from entry to exchange
2. **Throughput**: Orders per second, peak capacity
3. **Rejection Rate**: % orders rejected by risk/validation
4. **Fill Rate**: % orders successfully filled
5. **Amendment Rate**: % orders amended
6. **System Availability**: Uptime percentage
