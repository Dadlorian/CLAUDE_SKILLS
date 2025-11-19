# FIX Protocol Implementation Guide

## Session Setup

### Client-Side Initialization

```java
public class FIXClientInitializer {
    public static void main(String[] args) throws Exception {
        // Create session settings
        SessionSettings settings = new SessionSettings("fix_client.cfg");

        // Config file content:
        // [DEFAULT]
        // BeginString=FIX.4.4
        // SenderCompID=CLIENT1
        // TargetCompID=EXCH1
        // HeartBtInt=30
        // ResetOnLogout=Y

        Application application = new TradingApplication();
        MessageStoreFactory storeFactory = new FileStoreFactory(settings);
        LogFactory logFactory = new FileLogFactory(settings);

        Acceptor acceptor = new SocketInitiator(
            application, storeFactory, settings, logFactory);

        acceptor.start();
        System.out.println("FIX Client started");
    }
}
```

### Message Building

```java
public class OrderSubmissionService {
    private Session session;

    public void sendNewOrder(String symbol, Side side, int qty, double price) {
        NewOrderSingle order = new NewOrderSingle();

        // Header fields
        order.set(new BeginString("FIX.4.4"));
        order.set(new BodyLength(150));  // Will be calculated
        order.set(new MsgType(MsgType.NEW_ORDER_SINGLE));

        // Standard fields
        order.set(new ClOrdID("ORD" + System.currentTimeMillis()));
        order.set(new Symbol(symbol));
        order.set(new Side(side == Side.BUY ? Side.BUY : Side.SELL));
        order.set(new OrderQty(qty));
        order.set(new OrdType(OrdType.LIMIT));
        order.set(new Price(price));
        order.set(new TimeInForce(TimeInForce.DAY));

        try {
            Session.sendToTarget(order, session);
        } catch (SessionNotFound e) {
            LOG.error("Session not found", e);
        }
    }
}
```

### Execution Report Handling

```java
public class TradingApplication implements Application {
    @Override
    public void fromApp(Message message, SessionID sessionID)
            throws FieldNotFound, IncorrectDataFormat, IncorrectTagValue,
            UnsupportedMessageType {

        if (MsgType.EXECUTION_REPORT.equals(
                message.getHeader().getString(MsgType.FIELD))) {
            handleExecutionReport(message);
        }
    }

    private void handleExecutionReport(Message message)
            throws FieldNotFound {
        String orderId = message.getString(ClOrdID.FIELD);
        char orderStatus = message.getChar(OrdStatus.FIELD);
        int filledQty = message.getInt(CumQty.FIELD);
        double execPrice = message.getDouble(AvgPx.FIELD);

        switch (orderStatus) {
            case OrdStatus.NEW:
                processNewOrder(orderId);
                break;
            case OrdStatus.PARTIALLY_FILLED:
                processPartialFill(orderId, filledQty, execPrice);
                break;
            case OrdStatus.FILLED:
                processFullFill(orderId, filledQty, execPrice);
                break;
            case OrdStatus.REJECTED:
                processRejection(orderId, message.getString(Text.FIELD));
                break;
        }
    }
}
```

## Order Modification

```java
public void amendOrder(String originalOrderId, int newQty, double newPrice) {
    OrderCancelReplaceRequest replace = new OrderCancelReplaceRequest();

    replace.set(new ClOrdID("AMEND" + System.currentTimeMillis()));
    replace.set(new OrigClOrdID(originalOrderId));
    replace.set(new OrderQty(newQty));
    replace.set(new Price(newPrice));

    try {
        Session.sendToTarget(replace, session);
    } catch (SessionNotFound e) {
        LOG.error("Session not found", e);
    }
}
```

## Advanced Topics

### Resynchronization

```java
public class ResyncHandler {
    public void handleSequenceGap(int expectedSeq, int receivedSeq) {
        // Request missing messages
        ResendRequest resendRequest = new ResendRequest();
        resendRequest.set(new BeginSeqNo(expectedSeq));
        resendRequest.set(new EndSeqNo(receivedSeq - 1));

        try {
            Session.sendToTarget(resendRequest, session);
        } catch (SessionNotFound e) {
            LOG.error("Cannot resend", e);
        }
    }
}
```

### Test Request/Heartbeat

```java
public class HeartbeatManager {
    private final ScheduledExecutorService scheduler =
        Executors.newScheduledThreadPool(1);

    public void startHeartbeat(int intervalSeconds) {
        scheduler.scheduleAtFixedRate(
            this::sendHeartbeat,
            intervalSeconds,
            intervalSeconds,
            TimeUnit.SECONDS
        );
    }

    private void sendHeartbeat() {
        Heartbeat hb = new Heartbeat();
        try {
            Session.sendToTarget(hb, session);
        } catch (SessionNotFound e) {
            LOG.error("Cannot send heartbeat", e);
        }
    }
}
```

## Performance Optimization

- Use binary FIX for latency-critical paths
- Pre-compile message templates
- Use object pooling to avoid allocations
- Batch message sending when possible
- Monitor message queue depths

## Production Deployment Checklist

- [ ] Session configuration tested
- [ ] Message encoding/decoding validated
- [ ] Error handling comprehensive
- [ ] Reconnection logic implemented
- [ ] Monitoring and alerting in place
- [ ] Load testing completed
- [ ] Failover procedures tested
