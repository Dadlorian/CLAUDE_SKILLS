# Execution Algorithms Reference

## Algorithm Categories

### Cost-Based Algorithms
Focus on minimizing total execution cost including market impact.

### Time-Based Algorithms
Execute on predefined schedules regardless of market conditions.

### Volume-Based Algorithms
Adjust pace based on observed market volume.

### Adaptive Algorithms
Dynamically adjust based on market conditions and remaining order size.

## Standard Algorithms

### TWAP (Time-Weighted Average Price)

**Definition**: Execute orders in equal quantities over equal time periods.

**Formula**:
```
Slice Size = Total Qty / Number of Time Periods
Execute same quantity at each period
```

**Characteristics**
- Predictable execution schedule
- Simple to implement
- Ignores market volume
- Good for stable markets

**Pseudocode**:
```
total_qty = 100000
periods = 60  // 1 hour in minutes

slice_qty = total_qty / periods  // 1667 per minute

for minute in 0..59:
    execute_order(slice_qty)
    wait(60 seconds)
```

**Advantages**
- Simple, transparent
- No market dependency
- Predictable schedule
- Easy to explain

**Disadvantages**
- Executes during low volume
- Executes during volatility spikes
- Executes regardless of spread
- Higher market impact risk

### VWAP (Volume-Weighted Average Price)

**Definition**: Execute to match historical or predicted volume distribution.

**Formula**:
```
Target Execution Time = Order Arrival Time + Execution Window
Forecast volume for each period
Execute as % of forecasted volume
```

**Characteristics**
- Matches market participation
- Reduces market impact
- Requires volume forecasting
- More sophisticated than TWAP

**Pseudocode**:
```
total_qty = 100000
forecasted_volume = {h1: 500K, h2: 600K, h3: 400K}  // 1.5M total
execution_window = 3 hours

for hour in 1..3:
    hour_pct = forecasted_volume[hour] / 1500000
    target_qty = total_qty * hour_pct
    execute_during_hour(target_qty)
```

**VWAP Calculation**:
```
VWAP = SUM(Price * Volume) / SUM(Volume)

VWAP at hour close:
= Σ(price_i * volume_i) / Σ(volume_i)
```

**Advantages**
- Aligns with market volume
- Lower market impact
- Better benchmark than TWAP
- Volume responsive

**Disadvantages**
- Requires volume forecasting
- Assumption risk
- May miss liquid periods
- Execution during dry spells

### POIV (Percentage of Volume)

**Definition**: Execute as fixed percentage of real-time market volume.

**Formula**:
```
Target Qty = Real-Time Volume * Target Percentage
Continuously adjust execution pace
```

**Characteristics**
- Reactive to market volume
- Targets participation level
- Real-time adaptation
- Risk of incomplete execution

**Pseudocode**:
```
total_qty = 100000
target_pct = 0.10  // Execute 10% of market volume

remaining_qty = total_qty
while remaining_qty > 0:
    market_volume_now = get_market_volume_1min()
    target_qty = market_volume_now * target_pct
    execute_order(target_qty)
    remaining_qty -= target_qty
    wait(60 seconds)
```

**Advantages**
- Real-time market responsive
- Reduces market visibility
- Lower market impact
- Adaptive execution

**Disadvantages**
- Execution completion uncertain
- May execute over long time
- Volume forecasting still needed
- Cannot guarantee full execution

### Implementation Shortfall (IS)

**Definition**: Dynamic algorithm balancing completion urgency vs market impact.

**Formula**:
```
Cost = Market Impact Cost + Timing Cost
Market Impact ≈ α * (Qty / Market Vol)^β
Timing Cost ≈ Risk * Volatility * Remaining Time
```

**Characteristics**
- Balances speed vs cost
- Most sophisticated
- Requires optimization
- Market condition dependent

**Pseudocode**:
```
def optimal_execution(remaining_qty, time_left, volatility):
    best_cost = infinity
    best_qty = 0

    for qty_to_execute in range(0, remaining_qty):
        market_impact = estimate_market_impact(qty_to_execute)
        timing_risk = estimate_timing_risk(remaining_qty - qty_to_execute,
                                            time_left - 1, volatility)
        total_cost = market_impact + timing_risk

        if total_cost < best_cost:
            best_cost = total_cost
            best_qty = qty_to_execute

    return best_qty
```

**Advantages**
- Optimal execution cost
- Market-aware
- Time-aware
- Adapts to conditions

**Disadvantages**
- Complex implementation
- Requires good models
- Computationally intensive
- Hard to explain to users

## Advanced Algorithms

### Participation Rate Algorithm
```
Execution Rate = Market Rate * Participation %
Execute as % of observed market flow
Adapts to real-time volume
```

### Price-Based Algorithms
```
Buy more when price lower
Buy less when price higher
Trend-aware execution
```

### Volatility-Adjusted Algorithms
```
High volatility: Spread execution over longer time
Low volatility: Accelerate execution
Sigma-normalized metrics
```

### Dark Pool Algorithms
```
Attempt dark pool first
Fallback to lit venues
Minimize market impact
Cost-focused
```

## Algorithm Selection Criteria

### Factors to Consider

| Factor | TWAP | VWAP | POIV | IS |
|--------|------|------|------|-----|
| **Simplicity** | High | High | Medium | Low |
| **Market Impact** | High | Medium | Low | Low |
| **Completion Certainty** | High | High | Medium | High |
| **Speed** | Fixed | Flexible | Flexible | Optimal |
| **Volatility Sensitive** | No | No | No | Yes |

### Selection Logic
```
if order_urgent and small_size:
    use TWAP  // Fast execution needed

elif large_order and stable_market:
    use VWAP  // Minimize impact

elif need_low_visibility:
    use POIV  // Real-time adaptation

elif optimize_cost:
    use IS    // Sophisticated optimization
```

## Parameter Tuning

### Execution Window Selection
- **Short window** (minutes): Fast completion, high impact
- **Medium window** (hours): Balanced approach
- **Long window** (days): Minimize impact, high timing risk

### Percentage Parameters
- **TWAP periods**: More periods = lower impact
- **VWAP forecast accuracy**: Better forecast = better results
- **POIV target %**: Lower % = lower visibility

### Risk Parameters
- **Market impact factor (α)**: Calibrate to historical data
- **Elasticity (β)**: Typically 0.3-0.6
- **Risk aversion**: Higher = slower execution

## Performance Measurement

### Execution Quality Metrics

**VWAP Slippage**:
```
Slippage = (Execution_Price - VWAP) * Quantity
Lower is better (closer to zero)
```

**TWAP Slippage**:
```
Slippage = (Execution_Price - TWAP) * Quantity
Alternative benchmark
```

**Implementation Shortfall**:
```
IS = (Arrival_Price - Execution_Price) * Quantity
Measures vs arrival price
```

### Attribution Analysis
```
Total Cost = Market Impact + Timing Cost + Missed Opportunity

Market Impact: Due to aggressive execution
Timing Cost: Due to market moves while executing
Missed Opportunity: Unable to complete order
```

## Best Practices

1. **Right Algorithm for the Job**: Match algorithm to order characteristics
2. **Parameter Calibration**: Use recent market data for tuning
3. **Performance Tracking**: Monitor slippage and metrics
4. **Graceful Degradation**: Fallback algorithms if primary fails
5. **Monitoring and Alerts**: Real-time execution tracking
6. **Post-Trade Analysis**: Learn from every execution
