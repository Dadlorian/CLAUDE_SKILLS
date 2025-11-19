# Risk Management Checks Guide

## Pre-Trade Risk Validation

### Order Entry Checks

```java
public class PreTradeRiskValidator {
    private RiskLimitRepository limits;
    private PositionTracker positions;

    public RiskValidationResult validateOrder(Order order) {
        List<ValidationError> errors = new ArrayList<>();

        // 1. Price reasonableness
        if (!isPriceReasonable(order)) {
            errors.add(new ValidationError("PRICE_UNREASONABLE",
                "Price outside 5% of last trade"));
        }

        // 2. Quantity check
        if (!isQuantityReasonable(order)) {
            errors.add(new ValidationError("QUANTITY_UNREASONABLE",
                "Quantity > 100K shares"));
        }

        // 3. Position limit
        Position currentPos = positions.getPosition(order.getAccount(),
            order.getSecurity());
        Position newPos = currentPos.add(order.getQuantity(),
            order.getPrice());

        if (newPos.getQuantity() > limits.getPositionLimit(
                order.getSecurity())) {
            errors.add(new ValidationError("POSITION_LIMIT",
                "Position limit exceeded"));
        }

        // 4. Notional limit
        double notional = order.getQuantity() * order.getPrice();
        if (notional > limits.getNotionalLimit(order.getAccount())) {
            errors.add(new ValidationError("NOTIONAL_LIMIT",
                "Daily notional limit exceeded"));
        }

        // 5. Greeks limits (for options)
        if (order.getSecurity().isOption()) {
            double deltaImpact = calculateDeltaImpact(order);
            if (deltaImpact > limits.getDeltaLimit()) {
                errors.add(new ValidationError("DELTA_LIMIT",
                    "Delta limit exceeded"));
            }
        }

        // 6. Duplicate detection
        if (isDuplicateOrder(order)) {
            errors.add(new ValidationError("DUPLICATE_ORDER",
                "Duplicate order detected"));
        }

        return new RiskValidationResult(errors.isEmpty(), errors);
    }

    private boolean isPriceReasonable(Order order) {
        double lastTrade = marketData.getLastTrade(order.getSecurity());
        double tolerance = lastTrade * 0.05;  // 5%
        return Math.abs(order.getPrice() - lastTrade) < tolerance;
    }

    private boolean isQuantityReasonable(Order order) {
        return order.getQuantity() > 0 &&
               order.getQuantity() <= 1000000;
    }
}
```

## Position Limit Enforcement

```java
public class PositionLimitChecker {
    public static final Map<String, Long> POSITION_LIMITS = Map.ofEntries(
        entry("AAPL", 50000L),
        entry("MSFT", 30000L),
        entry("TSLA", 10000L),
        entry("*", 100000L)  // Default limit
    );

    public boolean checkPositionLimit(String account, String symbol,
                                       long newQuantity) {
        Position position = getPosition(account, symbol);
        long newTotal = position.getQuantity() + newQuantity;

        long limit = POSITION_LIMITS.getOrDefault(symbol,
            POSITION_LIMITS.get("*"));

        if (Math.abs(newTotal) > limit) {
            LOG.warn("Position limit exceeded for " + symbol +
                ": " + newTotal + " > " + limit);
            return false;
        }
        return true;
    }
}
```

## Notional Limits

```java
public class NotionalLimitChecker {
    private static final double DAILY_NOTIONAL_LIMIT = 100_000_000;  // $100M
    private AtomicDouble notionalToday = new AtomicDouble(0);

    public boolean checkNotionalLimit(Order order) {
        double orderNotional = order.getQuantity() * order.getPrice();
        double newTotal = notionalToday.get() + orderNotional;

        if (newTotal > DAILY_NOTIONAL_LIMIT) {
            LOG.warn("Daily notional limit exceeded: " +
                newTotal + " > " + DAILY_NOTIONAL_LIMIT);
            return false;
        }

        notionalToday.set(newTotal);
        return true;
    }

    public void resetDaily() {
        notionalToday.set(0);  // Reset at market open
    }
}
```

## Market Impact Estimation

```cpp
class MarketImpactEstimator {
    // Historical calibration
    static const double ALPHA = 0.15;  // Market impact coefficient
    static const double BETA = 0.5;     // Elasticity

    double estimate_impact(int quantity, int market_depth,
                           double volatility) {
        // Market impact ≈ α * (qty / depth)^β * √volatility
        double ratio = (double)quantity / market_depth;
        double impact = ALPHA * pow(ratio, BETA) * sqrt(volatility);
        return impact;  // In basis points
    }
};
```

## Pre-Trade vs Post-Trade

```
PRE-TRADE CHECKS (Before order sent to exchange):
✓ Price reasonableness (±5% of last)
✓ Quantity limits (>0, <1M)
✓ Position limits
✓ Notional limits
✓ Account status
✓ Instrument restrictions
✓ Duplicate detection

POST-TRADE CHECKS (After execution):
✓ Trade reconciliation
✓ Mark-to-market P&L
✓ Settlement validity
✓ Counterparty credit
✓ Position tracking
✓ Regulatory reporting
```

## Production Deployment

- [ ] All validation checks enabled
- [ ] Limits configured per account/symbol
- [ ] Real-time monitoring of limit utilization
- [ ] Alerting on limit breaches
- [ ] Circuit breaker mechanisms tested
- [ ] Manual override procedures documented
- [ ] Audit trail of all validations
