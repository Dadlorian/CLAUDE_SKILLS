// Enterprise order validation system
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class EnterpriseOrderValidator {
    private static final int MIN_PRICE = 1;
    private static final int MAX_PRICE = 1000000;
    private static final int MIN_SIZE = 1;
    private static final int MAX_SIZE = 10000000;

    private final ConcurrentHashMap<String, Integer> positions;
    private final ConcurrentHashMap<String, Integer> notional;
    private final RiskLimits riskLimits;

    public EnterpriseOrderValidator(RiskLimits limits) {
        this.riskLimits = limits;
        this.positions = new ConcurrentHashMap<>();
        this.notional = new ConcurrentHashMap<>();
    }

    public ValidationResult validate(Order order) {
        ValidationResult result = new ValidationResult();

        // Price validation
        if (order.getPrice() < MIN_PRICE || order.getPrice() > MAX_PRICE) {
            result.addError("INVALID_PRICE");
        }

        // Size validation
        if (order.getQuantity() < MIN_SIZE || 
            order.getQuantity() > MAX_SIZE) {
            result.addError("INVALID_SIZE");
        }

        // Position limit check
        String symbol = order.getSymbol();
        int currentPos = positions.getOrDefault(symbol, 0);
        int newPos = currentPos + (order.getSide() == Side.BUY ?
                                   order.getQuantity() :
                                   -order.getQuantity());

        int posLimit = riskLimits.getPositionLimit(symbol);
        if (Math.abs(newPos) > posLimit) {
            result.addError("POSITION_LIMIT");
        }

        // Notional check
        double orderNotional = (double)order.getQuantity() * order.getPrice();
        String account = order.getAccount();
        double currentNotional = notional.getOrDefault(account, 0);
        double newNotional = currentNotional + orderNotional;

        double notionalLimit = riskLimits.getNotionalLimit(account);
        if (newNotional > notionalLimit) {
            result.addError("NOTIONAL_LIMIT");
        }

        // Account status
        if (!riskLimits.isAccountActive(account)) {
            result.addError("ACCOUNT_INACTIVE");
        }

        return result;
    }

    public void updatePosition(Order order) {
        String symbol = order.getSymbol();
        int qty = order.getSide() == Side.BUY ?
                  order.getQuantity() :
                  -order.getQuantity();

        positions.compute(symbol,
            (k, v) -> (v == null ? 0 : v) + qty);
    }

    static class ValidationResult {
        private java.util.List<String> errors = new java.util.ArrayList<>();

        public void addError(String error) {
            errors.add(error);
        }

        public boolean isValid() {
            return errors.isEmpty();
        }

        public java.util.List<String> getErrors() {
            return errors;
        }
    }

    static class RiskLimits {
        public int getPositionLimit(String symbol) { return 50000; }
        public double getNotionalLimit(String account) { return 100_000_000; }
        public boolean isAccountActive(String account) { return true; }
    }

    enum Side { BUY, SELL }

    interface Order {
        String getSymbol();
        String getAccount();
        int getQuantity();
        double getPrice();
        Side getSide();
    }
}
