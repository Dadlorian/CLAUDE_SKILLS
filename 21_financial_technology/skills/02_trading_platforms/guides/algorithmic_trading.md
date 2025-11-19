# Algorithmic Trading Implementation Guide

## Architecture Framework

```python
class AlgoExecutionEngine:
    def __init__(self, parent_order, algorithm_type):
        self.parent_order = parent_order
        self.algorithm = self._select_algorithm(algorithm_type)
        self.remaining_qty = parent_order.quantity
        self.execution_start = time.time()
        self.child_orders = []

    def _select_algorithm(self, algo_type):
        if algo_type == "TWAP":
            return TWAPAlgorithm(self.parent_order)
        elif algo_type == "VWAP":
            return VWAPAlgorithm(self.parent_order)
        elif algo_type == "POIV":
            return POIVAlgorithm(self.parent_order)
        elif algo_type == "IS":
            return ImplementationShortfallAlgorithm(self.parent_order)

    def execute(self):
        while self.remaining_qty > 0:
            # Get next execution slice
            qty_to_execute = self.algorithm.get_next_slice(
                self.remaining_qty,
                market_data.get_current_state()
            )

            if qty_to_execute == 0:
                time.sleep(0.001)  # Brief pause
                continue

            # Create and submit child order
            child_order = Order(
                security=self.parent_order.security,
                side=self.parent_order.side,
                quantity=qty_to_execute,
                order_type=self.algorithm.get_order_type(),
                price=self.algorithm.get_limit_price()
            )

            oms.submit_order(child_order)
            self.child_orders.append(child_order)
            self.remaining_qty -= qty_to_execute

            # Monitor fills
            filled = self._wait_for_fills(timeout=1.0)
            if filled > 0:
                self.remaining_qty -= filled
```

## TWAP Implementation

```python
class TWAPAlgorithm:
    def __init__(self, parent_order):
        self.parent_order = parent_order
        self.execution_window = parent_order.execution_window  # seconds
        self.slice_size = parent_order.quantity / (self.execution_window)
        self.slices_executed = 0

    def get_next_slice(self, remaining_qty, market_data):
        elapsed = time.time() - self.execution_start
        time_remaining = max(0, self.execution_window - elapsed)

        if time_remaining == 0:
            # Final slice
            return remaining_qty

        # Execute uniform quantity
        return min(int(self.slice_size), remaining_qty)

    def get_order_type(self):
        return "LIMIT"

    def get_limit_price(self):
        # Peg to midpoint + offset
        mid = market_data.get_midpoint()
        offset = 0.01 if self.parent_order.side == BUY else -0.01
        return mid + offset
```

## VWAP Implementation

```python
class VWAPAlgorithm:
    def __init__(self, parent_order):
        self.parent_order = parent_order
        self.volume_forecast = self._build_volume_forecast()
        self.total_forecast_volume = sum(self.volume_forecast)
        self.qty_executed = 0

    def _build_volume_forecast(self):
        # Historical volume pattern
        # Typically: higher at open/close, lower midday
        return [
            0.05,  # 9:30-10:00
            0.08,  # 10:00-11:00
            0.04,  # 11:00-12:00
            0.03,  # 12:00-13:00
            0.06,  # 13:00-14:00
            0.10,  # 14:00-15:00
            0.12,  # 15:00-16:00 (closing period)
        ]

    def get_next_slice(self, remaining_qty, market_data):
        current_hour = self._get_current_hour()

        # Forecast percentage of day's volume in current hour
        hour_vol_pct = self.volume_forecast[current_hour]
        target_qty = int(self.parent_order.quantity * hour_vol_pct)

        # Adjust for actual observed volume
        actual_market_vol = market_data.get_1hour_volume()
        forecast_market_vol = market_data.get_1hour_forecast()
        if forecast_market_vol > 0:
            adjustment = actual_market_vol / forecast_market_vol
            target_qty = int(target_qty * adjustment)

        qty_to_execute = min(
            target_qty - self.qty_executed,
            remaining_qty
        )

        self.qty_executed += qty_to_execute
        return qty_to_execute
```

## POIV (Percentage of Volume)

```python
class POIVAlgorithm:
    def __init__(self, parent_order, target_participation_rate=0.10):
        self.parent_order = parent_order
        self.target_pct = target_participation_rate
        self.check_interval = 60  # seconds

    def get_next_slice(self, remaining_qty, market_data):
        # Get recent 1-minute volume
        one_min_volume = market_data.get_1min_volume()

        # Target is participation_rate % of volume
        target_qty = int(one_min_volume * self.target_pct)

        # Execute up to target, but not more than remaining
        qty_to_execute = min(target_qty, remaining_qty)

        return qty_to_execute
```

## Implementation Shortfall Algorithm

```python
class ImplementationShortfallAlgorithm:
    def __init__(self, parent_order):
        self.parent_order = parent_order
        self.market_impact_alpha = 0.2  # Calibrated from historical
        self.market_impact_beta = 0.5   # elasticity
        self.risk_aversion = 1.0

    def get_next_slice(self, remaining_qty, market_data):
        # Cost = Market Impact + Timing Risk
        # Optimize execution pace

        time_left_hours = self._hours_remaining()
        volatility = market_data.get_volatility()

        best_cost = float('inf')
        best_qty = 0

        # Try different execution quantities
        for test_qty in range(100, remaining_qty + 1, max(1, remaining_qty // 100)):
            # Market impact cost
            market_impact = self._estimate_market_impact(
                test_qty, market_data.get_market_depth()
            )

            # Timing risk cost
            timing_risk = self._estimate_timing_risk(
                remaining_qty - test_qty,
                time_left_hours,
                volatility
            )

            total_cost = market_impact + self.risk_aversion * timing_risk

            if total_cost < best_cost:
                best_cost = total_cost
                best_qty = test_qty

        return best_qty

    def _estimate_market_impact(self, qty, market_depth):
        # Market impact ≈ α * (qty / market_depth)^β
        ratio = qty / max(1, market_depth)
        impact = self.market_impact_alpha * (ratio ** self.market_impact_beta)
        return impact

    def _estimate_timing_risk(self, remaining_qty, hours_left, volatility):
        # Timing risk = qty * volatility * sqrt(hours)
        import math
        risk = remaining_qty * volatility * math.sqrt(hours_left)
        return risk
```

## Execution Monitoring

```python
class ExecutionMonitor:
    def __init__(self, parent_order):
        self.parent_order = parent_order
        self.entry_price = market_data.get_midpoint()
        self.execution_prices = []
        self.execution_quantities = []

    def on_execution(self, fill):
        self.execution_prices.append(fill.price)
        self.execution_quantities.append(fill.quantity)

    def get_execution_quality(self):
        # VWAP Slippage
        total_qty = sum(self.execution_quantities)
        if total_qty == 0:
            return 0

        vwap = sum(p * q for p, q in zip(
            self.execution_prices,
            self.execution_quantities
        )) / total_qty

        vwap_slippage = (vwap - self.entry_price) * total_qty

        # TWAP Slippage
        avg_price = vwap  # Equal to vwap in this context
        current_price = market_data.get_midpoint()
        implementation_shortfall = (current_price - avg_price) * total_qty

        return {
            'vwap': vwap,
            'vwap_slippage': vwap_slippage,
            'implementation_shortfall': implementation_shortfall,
            'avg_execution_price': avg_price
        }

    def report_metrics(self):
        quality = self.get_execution_quality()
        print(f"VWAP Slippage: ${quality['vwap_slippage']:.2f}")
        print(f"Impl Shortfall: ${quality['implementation_shortfall']:.2f}")
        print(f"Avg Price: ${quality['avg_execution_price']:.4f}")
```

## Production Deployment

```python
# Example usage
if __name__ == "__main__":
    # Create parent order
    parent = Order(
        security="AAPL",
        side=BUY,
        quantity=100000,
        algorithm="VWAP",
        execution_window=3600  # 1 hour
    )

    # Create execution engine
    engine = AlgoExecutionEngine(parent, "VWAP")

    # Monitor execution
    monitor = ExecutionMonitor(parent)

    # Start execution
    engine.execute()

    # Report results
    monitor.report_metrics()
```

## Best Practices

1. **Algorithm Selection**: Match algorithm to order size and market conditions
2. **Parameter Tuning**: Calibrate impact coefficients to recent market data
3. **Real-Time Adaptation**: Adjust parameters as market conditions change
4. **Performance Tracking**: Monitor execution quality vs benchmarks
5. **Fail-Safe**: Have fallback algorithms and manual intervention capability
6. **Testing**: Extensive backtesting before production deployment
7. **Risk Management**: Enforce position and P&L limits during execution

## Key Metrics

| Metric | Target | Monitoring |
|--------|--------|-----------|
| **VWAP Slippage** | <2 bps | Every execution |
| **Completion Rate** | >99% | Daily |
| **Execution Time** | <1 hour | Per order |
| **Market Impact** | <5 bps | Post-execution analysis |
