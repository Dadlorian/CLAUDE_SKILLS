# Market Making Operations Reference

## Market Making Definition

**Market Making**: Providing liquidity by posting both buy and sell quotes simultaneously, profiting from bid-ask spread.

**Business Model**:
```
Market Maker's Profit/Loss:
= (Ask Price Executed - Bid Price Executed)
- (Holding Costs + Risk Cost + Slippage)
= Spread Captured - Operating Costs
```

## Revenue Sources

### 1. Spread Capture
- **Primary Revenue**: Difference between bid and ask
- **Example**: Buy at $99.95, sell at $100.00 = $0.05/share spread
- **Volume**: Higher volume = higher total spread capture

### 2. Rebates
- **Maker Rebate**: Incentive for providing liquidity
- **Typical**: $0.0005-0.0015 per share
- **Example**: 1M shares × $0.001 = $1,000 rebate

### 3. Statistical Arbitrage
- **Market Impact Strategies**: Profit from temporary dislocations
- **Order Flow Information**: Profit from information edge
- **Inventory Management**: Manage positions for profit

## Risk Management

### Inventory Risk

**Definition**: Risk of loss from price moves while holding inventory.

```python
def inventory_risk(position, volatility_daily, time_in_inventory):
    # Risk = Position Size × Daily Volatility × √Time
    risk = position * volatility_daily * sqrt(time_in_inventory/252)
    return risk

# Example:
position = 1000  # shares
daily_vol = 0.02  # 2% daily
time_days = 1/252  # 1 minute (1/252 of a trading day)
risk = 1000 * 0.02 * sqrt(1/252) = 1000 * 0.02 * 0.063 = $1.26 expected loss
```

### Position Limits

**Maximum Position**:
```
Max Position = Risk Limit / (Daily Volatility × √Time)

Example:
Risk Limit = $1,000
Daily Vol = 2%
Time = 1 minute
Max Pos = $1,000 / (0.02 × 0.063) = 797K shares (at $100/share)
```

### Rebalancing

```python
def rebalancing_logic(position, max_position):
    # When position > limit, reduce
    if abs(position) > max_position:
        side = "BUY" if position < 0 else "SELL"
        qty = abs(position) - max_position * 0.9
        execute_order(side, qty)

    # Rebalance when skewed
    if abs(position) > max_position * 0.7:
        side = "BUY" if position < 0 else "SELL"
        qty = abs(position) * 0.3
        execute_order(side, qty)
```

## Quote Generation

### Dynamic Pricing

```python
def calculate_market_maker_quotes(mid_price, position, inventory_limit):
    # Adjust quotes based on position

    bid_offset = 0.005  # Base half-spread

    # Inventory adjustment
    if position > 0:
        # Long inventory - lower bid to reduce
        bid_offset -= position / inventory_limit * 0.003
        ask_offset = 0.005 + position / inventory_limit * 0.003

    elif position < 0:
        # Short inventory - raise bid to increase
        bid_offset += abs(position) / inventory_limit * 0.003
        ask_offset = 0.005 - abs(position) / inventory_limit * 0.003

    else:
        ask_offset = 0.005

    bid_price = mid_price - bid_offset
    ask_price = mid_price + ask_offset

    return bid_price, ask_price
```

### Volatility Adjustment

```python
def volatility_adjusted_spread(base_spread, current_vol, normal_vol):
    # Widen spread during high volatility
    vol_multiplier = current_vol / normal_vol
    adjusted_spread = base_spread * vol_multiplier
    return adjusted_spread

# Example:
base_spread = 0.01  # 1 cent
current_vol = 0.03  # 3% (increased)
normal_vol = 0.02   # 2% (normal)
adjusted = 0.01 * (0.03 / 0.02) = 0.015  # 1.5 cents (wider)
```

## Market Making Strategies

### Static Quoting

**Simple Spread**:
```
Buy at: Mid - 0.005
Sell at: Mid + 0.005
Fixed spread regardless of conditions
```

**Pros**: Simple, predictable
**Cons**: Ignores market conditions, higher risk

### Dynamic Quoting

**Adaptive Spread**:
```
Spread = Base Spread × f(Volatility, Inventory, Competition)
Real-time adjustment
Responds to conditions
```

**Pros**: More sophisticated, better risk management
**Cons**: Complex, requires good models

### Opportunistic Market Making

**Statistical Arbitrage**:
```
Quote tighter than normal when confident in fill
Quote wider when uncertain
Profit from information advantages
```

### Latency Arbitrage

**Micro-Structure Advantage**:
```
Detect order flow patterns
Execute before latency-disadvantaged traders
Profit from speed advantage
Ultra-low latency critical
```

## Operating Costs

### Explicit Costs

| Cost Item | Typical Charge |
|-----------|----------------|
| Exchange fees | -$0.001/share |
| Co-location | $2,000-10,000/month |
| Network | $1,000-5,000/month |
| Software/Hardware | $100K-1M/year |
| Compliance | $500K-2M/year |
| Personnel | $2M-10M/year |

### Implicit Costs

**Market Impact**:
```
When rebalancing position, incur market impact
Costs depend on size and market depth
Can be significant for large positions
```

**Opportunity Cost**:
```
Capital tied up in inventory
Foregone returns on capital
Typically 2-5% annually
```

## Profitability Analysis

### Break-Even Analysis

```python
def market_maker_profitability(daily_volume, spread_cents,
                               costs_per_share, daily_fees):
    # Revenue from spread
    spread_revenue = daily_volume * (spread_cents / 100)

    # Revenue from rebates
    rebate_revenue = daily_volume * 0.001  # Typical rebate

    # Costs
    exchange_costs = daily_volume * 0.001
    other_costs = daily_fees

    gross_profit = spread_revenue + rebate_revenue
    net_profit = gross_profit - exchange_costs - other_costs

    return {
        'gross_profit': gross_profit,
        'exchange_costs': exchange_costs,
        'net_profit': net_profit,
        'profit_margin': net_profit / gross_profit if gross_profit > 0 else 0
    }

# Example: 100K shares/day, 1.5 cent spread
result = market_maker_profitability(100000, 1.5, 0.001, 5000)
# spread_revenue = 100K * 0.015 = $1,500
# rebate = 100K * 0.001 = $100
# exchange cost = 100K * 0.001 = $100
# net = $1,500 + $100 - $100 - $5,000 = -$3,500 (LOSS)
# Need higher volume or lower costs
```

## Risk Limits for Market Makers

### Position Limits
- **Per Symbol**: $X maximum position
- **Per Sector**: $Y maximum sector exposure
- **Portfolio**: $Z maximum gross/net exposure

### Loss Limits
- **Daily Loss Stop**: Stop trading after $50K loss
- **Weekly Loss Stop**: Stop trading if weekly loss exceeds $200K
- **Monthly Loss Stop**: Regulatory review if monthly loss exceeds $500K

### Concentration Limits
- **Single Stock**: Max 10% of AUM
- **Correlated Stocks**: Max 20% sector exposure
- **Illiquid Stocks**: Limited participation

## Technology Requirements

### Critical Infrastructure

**Ultra-Low Latency**:
- Direct exchange connectivity
- Co-location
- Kernel bypass networking
- Hardware acceleration (FPGA)
- Sub-microsecond clock synchronization

**High Throughput**:
- Ability to process 1M+ quotes/second
- Sub-second order placement
- Real-time position tracking
- Continuous P&L monitoring

**Reliability**:
- 99.99%+ uptime
- Automatic failover
- Order recovery mechanisms
- Disaster recovery

### Hardware Investment
- **Core Server**: $50-200K
- **Co-location Fees**: $5K-50K/month
- **Network**: $10K-100K setup, $5K-20K/month
- **Software**: $100K-1M/year
- **Total**: $500K-5M initial + $1M-5M annual

## Regulatory Considerations

### Market Maker Obligations
- **Continuous Quoting**: Must maintain presence
- **Quote Width**: Quotes must meet requirements
- **Best Bid-Ask**: Must participate in best prices
- **Compliance**: Follow all market conduct rules

### Market Maker Protections
- **Withdrawal**: Can withdraw quotes with notice
- **Emergency**: Can halt quoting in crisis
- **Support**: Receive exchange support and rebates

## Best Practices

1. **Constant Risk Monitoring**: Real-time position and P&L tracking
2. **Inventory Management**: Active rebalancing strategies
3. **Dynamic Pricing**: Adjust quotes for conditions
4. **Cost Optimization**: Minimize exchange/bandwidth costs
5. **Technology Investment**: Low latency is critical
6. **Diversification**: Trade multiple securities/markets
7. **Regulatory Compliance**: Maintain quote obligations
