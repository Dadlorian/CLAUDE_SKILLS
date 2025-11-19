// Pre-trade risk validation system
import java.util.concurrent.atomic.*;
import java.util.*;

public class RiskChecker {
    private static final int POSITION_LIMIT = 50000;
    private static final double NOTIONAL_LIMIT = 100_000_000;

    private final Map<String, AtomicInteger> positions;
    private final AtomicReference<Double> dailyNotional;

    public RiskChecker() {
        this.positions = new ConcurrentHashMap<>();
        this.dailyNotional = new AtomicReference<>(0.0);
    }

    public RiskValidationResult validateOrder(Order order) {
        List<String> errors = new ArrayList<>();

        // 1. Price check
        if (!isPriceReasonable(order)) {
            errors.add("PRICE_UNREASONABLE");
        }

        // 2. Position limit check
        int currentPosition = positions.getOrDefault(order.getSecurity(),
                                                    new AtomicInteger(0)).get();
        int newPosition = currentPosition + order.getQuantity();

        if (Math.abs(newPosition) > POSITION_LIMIT) {
            errors.add("POSITION_LIMIT_EXCEEDED");
        }

        // 3. Notional limit check
        double orderNotional = order.getQuantity() * order.getPrice();
        double newNotional = dailyNotional.get() + orderNotional;

        if (newNotional > NOTIONAL_LIMIT) {
            errors.add("NOTIONAL_LIMIT_EXCEEDED");
        }

        // 4. Account status
        if (!isAccountActive(order.getAccount())) {
            errors.add("ACCOUNT_INACTIVE");
        }

        if (errors.isEmpty()) {
            // Update position and notional
            positions.computeIfAbsent(order.getSecurity(),
                k -> new AtomicInteger(0)).addAndGet(order.getQuantity());
            dailyNotional.set(newNotional);
            return new RiskValidationResult(true, new ArrayList<>());
        }

        return new RiskValidationResult(false, errors);
    }

    private boolean isPriceReasonable(Order order) {
        // Would check against last trade price ±5%
        return order.getPrice() > 0.01 && order.getPrice() < 10000;
    }

    private boolean isAccountActive(String account) {
        // Would check account status
        return true;
    }

    static class RiskValidationResult {
        final boolean valid;
        final List<String> errors;

        RiskValidationResult(boolean valid, List<String> errors) {
            this.valid = valid;
            this.errors = errors;
        }
    }

    static class Order {
        private final String security;
        private final String account;
        private final int quantity;
        private final double price;

        public Order(String security, String account,
                    int quantity, double price) {
            this.security = security;
            this.account = account;
            this.quantity = quantity;
            this.price = price;
        }

        public String getSecurity() { return security; }
        public String getAccount() { return account; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }
    }
}
