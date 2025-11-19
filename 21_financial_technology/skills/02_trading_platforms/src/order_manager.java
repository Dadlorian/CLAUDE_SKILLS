// Thread-safe order management system
import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.*;

public class OrderManager {
    private final ConcurrentHashMap<Long, Order> orders;
    private final AtomicLong nextOrderId;
    private final BlockingQueue<OrderEvent> eventQueue;

    public OrderManager() {
        this.orders = new ConcurrentHashMap<>();
        this.nextOrderId = new AtomicLong(1);
        this.eventQueue = new LinkedBlockingQueue<>(1000000);
    }

    public long submitOrder(OrderRequest request) {
        long orderId = nextOrderId.incrementAndGet();

        Order order = new Order.Builder()
            .orderId(orderId)
            .security(request.getSecurity())
            .side(request.getSide())
            .quantity(request.getQuantity())
            .price(request.getPrice())
            .timestamp(System.nanoTime())
            .status(OrderStatus.NEW)
            .build();

        orders.put(orderId, order);
        publishEvent(new OrderEvent(OrderEventType.CREATED, order));

        return orderId;
    }

    public void updateOrderStatus(long orderId, OrderStatus newStatus) {
        Order order = orders.get(orderId);
        if (order != null) {
            Order updated = order.toBuilder().status(newStatus).build();
            orders.put(orderId, updated);
            publishEvent(new OrderEvent(OrderEventType.STATUS_CHANGED, updated));
        }
    }

    public void recordExecution(long orderId, Execution execution) {
        Order order = orders.get(orderId);
        if (order != null) {
            Order updated = order.addExecution(execution);
            orders.put(orderId, updated);
            publishEvent(new OrderEvent(OrderEventType.EXECUTED, updated));
        }
    }

    private void publishEvent(OrderEvent event) {
        try {
            eventQueue.put(event);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public Order getOrder(long orderId) {
        return orders.get(orderId);
    }

    public int getTotalOrders() {
        return orders.size();
    }

    enum OrderStatus { NEW, ACCEPTED, PARTIALLY_FILLED, FILLED, REJECTED, CANCELED }
    enum OrderEventType { CREATED, STATUS_CHANGED, EXECUTED }

    static class Order {
        final long orderId;
        final String security;
        final String side;
        final int quantity;
        final double price;
        final long timestamp;
        final OrderStatus status;
        final List<Execution> executions;

        public Order(long orderId, String security, String side,
                    int quantity, double price, long timestamp,
                    OrderStatus status, List<Execution> executions) {
            this.orderId = orderId;
            this.security = security;
            this.side = side;
            this.quantity = quantity;
            this.price = price;
            this.timestamp = timestamp;
            this.status = status;
            this.executions = executions;
        }

        static class Builder {
            private long orderId;
            private String security;
            private String side;
            private int quantity;
            private double price;
            private long timestamp;
            private OrderStatus status = OrderStatus.NEW;

            public Builder orderId(long id) { this.orderId = id; return this; }
            public Builder security(String s) { this.security = s; return this; }
            public Builder side(String s) { this.side = s; return this; }
            public Builder quantity(int q) { this.quantity = q; return this; }
            public Builder price(double p) { this.price = p; return this; }
            public Builder timestamp(long t) { this.timestamp = t; return this; }
            public Builder status(OrderStatus s) { this.status = s; return this; }

            public Order build() {
                return new Order(orderId, security, side, quantity, price,
                               timestamp, status, new ArrayList<>());
            }
        }

        public Builder toBuilder() {
            return new Builder()
                .orderId(orderId)
                .security(security)
                .side(side)
                .quantity(quantity)
                .price(price)
                .timestamp(timestamp)
                .status(status);
        }

        public Order addExecution(Execution exec) {
            List<Execution> newExecs = new ArrayList<>(executions);
            newExecs.add(exec);
            return new Order(orderId, security, side, quantity, price,
                           timestamp, status, newExecs);
        }
    }

    static class Execution {
        final int quantity;
        final double price;
        final long timestamp;

        public Execution(int quantity, double price, long timestamp) {
            this.quantity = quantity;
            this.price = price;
            this.timestamp = timestamp;
        }
    }

    static class OrderEvent {
        final OrderEventType type;
        final Order order;

        public OrderEvent(OrderEventType type, Order order) {
            this.type = type;
            this.order = order;
        }
    }
}
