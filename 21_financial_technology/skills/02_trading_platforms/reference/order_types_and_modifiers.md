# Order Types and Modifiers Reference

## Basic Order Types

### Market Order
- **Definition**: Execute immediately at best available price
- **Guarantee**: Execution (subject to liquidity)
- **Uncertainty**: Final price unknown
- **Use Case**: Urgent execution needed
- **Market Impact**: High (aggressive)
- **Slippage Risk**: High

```
Market Order Execution:
- Matched against best ask (buy) or best bid (sell)
- If quantity exceeds level, walk down book
- Continues until filled or no liquidity
```

### Limit Order
- **Definition**: Execute at specified price or better
- **Guarantee**: None (may not fill)
- **Certainty**: Known maximum price
- **Use Case**: Opportunistic execution
- **Market Impact**: Low (passive)
- **Slippage Risk**: Order may not fill

```
Buy Limit Order: Execute at limit price or lower
Sell Limit Order: Execute at limit price or higher
```

### Stop Order (Stop-Loss)
- **Definition**: Market order triggered at stop price
- **Trigger**: When market price hits stop level
- **Execution**: Converts to market order
- **Use Case**: Risk management, loss limitation
- **Caution**: Execution price unpredictable at trigger

```
Buy Stop: Triggered when price rises above stop
Sell Stop: Triggered when price falls below stop
```

### Stop-Limit Order
- **Definition**: Stop order that becomes limit order
- **Trigger**: Stop price
- **Execution**: Limit order at specified price
- **Advantage**: Price protection with trigger
- **Risk**: May not fill after trigger

```
Example: Stock at $100
Sell Stop-Limit: Stop at $95, Limit at $94
- Triggered when price hits $95
- Sells at $94 or better (or doesn't fill)
```

## Time-in-Force Modifiers

### Day (DAY)
- **Duration**: Market hours only
- **Expiration**: End of trading session
- **Most common**: For liquid markets
- **Default**: In most systems

### Good-Till-Canceled (GTC)
- **Duration**: Until manually canceled
- **Risk**: Forgotten orders
- **Liquidity**: Can execute days/weeks later
- **Regulatory**: Some restrictions apply
- **Best Practice**: Set expiration reminder

### Immediate-or-Cancel (IOC)
- **Execution**: All-or-nothing (not required)
- **Cancellation**: Unfilled portion immediately canceled
- **Use Case**: Quick exit strategies
- **Market Impact**: Moderate

### Fill-or-Kill (FOK)
- **Execution**: All-or-nothing (required)
- **Rejection**: If not fully fillable
- **Use Case**: Block trades, bulk operations
- **Market Impact**: Low (doesn't split orders)

### At-the-Opening (OPG)
- **Execution**: At opening price
- **Timing**: Pre-market or opening auction
- **Use Case**: Opening participation
- **Risk**: May not match if opening unusual

### At-the-Close (CLO)
- **Execution**: At closing price/auction
- **Timing**: End of session
- **Use Case**: Portfolio rebalancing
- **Risk**: Closing auction participation requirements

## Advanced Order Types

### Pegged Orders
- **Behavior**: Price automatically adjusts
- **Peg Type**:
  - Primary peg: Best bid/ask
  - Midpoint peg: Mid of spread
  - Market peg: Best bid/ask that improves

```
Example: Apple at $150-$150.10
Pegged order with +$0.05 offset = $150.05 (bid) to $150.15 (ask)
```

### Iceberg Orders
- **Display**: Only portion visible to market
- **Reserve**: Remaining quantity hidden
- **Replenishment**: New quantity shows as old fills
- **Use Case**: Minimize market impact
- **Strategy**: Hide large order intent

```
Example: Buy 100K shares of XYZ
Display 5K at a time
Market sees 5K bids repeatedly
Actually executing 100K total
```

### Bracket Orders
- **Structure**: Primary order + profit target + stop loss
- **Execution**: When primary fills, both contingent orders active
- **Protection**: Automatic risk management
- **Cancellation**: One fill cancels others

```
Buy 100 @ $100
  ├─ Sell 100 @ $110 (profit target)
  └─ Sell 100 @ $95 (stop loss)
```

### Trailing Stop Orders
- **Mechanism**: Stop price follows market
- **Adjustment**: Moves up by trailing amount
- **Reset**: Never moves back down
- **Use Case**: Momentum capture with protection

```
Stock rises from $100 to $125
Trailing stop of $5 starts at $95
Follows to $120 as price goes to $125
Triggered if price drops $5 from highest
```

### One-Cancels-Other (OCO)
- **Structure**: Two orders linked
- **Trigger**: Fill one, automatically cancels other
- **Use Case**: Alternative execution paths
- **Example**: Buy at limit OR buy on breakout

### One-Triggers-Other (OTO)
- **Structure**: Primary order triggers contingent order
- **Execution**: First order must fill to activate second
- **Use Case**: Conditional execution
- **Example**: Sell triggers buy at lower price

## Order Modifiers

### Quantity Modifiers

**Minimum Quantity**
- **Requirement**: Must fill at least minimum
- **Rejection**: If minimum not available
- **Use Case**: Transaction cost thresholds

**Display Quantity (Iceberg)**
- **Visible Amount**: Smaller than total
- **Hidden Amount**: Reserve quantity
- **Refinement**: Minimum increment

### Price Modifiers

**Price Offset**
- **Basis**: Pegged to reference price
- **Offset Amount**: Fixed or percentage
- **Adjustment**: Real-time as reference moves

**Post-Only Flag**
- **Behavior**: Add to book, never execute against
- **Guarantee**: Maker fee (not taker)
- **Rejection**: If would execute immediately

### Execution Modifiers

**All-or-Nothing (AON)**
- **Requirement**: Entire quantity at once
- **Rejection**: Partial fills not acceptable
- **Liquidity**: May not fill in fragmented market

**Match Immediately (MIO)**
- **Requirement**: Satisfy immediately or cancel
- **Similar to**: IOC but slightly different

### Participant Type Modifiers

**Retail Order Flow**
- **Flag**: Indicates retail participant
- **Venue**: Retail order handling rules
- **Pricing**: Potential midpoint orders

**Qualified Investor**
- **Restriction**: Options/derivative trading
- **Account Type**: Accredited or qualified only

## Order Quality Indicators

### Aggressive vs Passive
- **Aggressive**: Market/marketable limit orders
- **Passive**: Non-marketable limit orders
- **Impact**: On execution quality metrics

### Liquidity Assessment
- **Depth Available**: Quantity at each level
- **Spread Width**: Bid-ask spread size
- **Resilience**: How quickly book rebounds

## Regulatory Considerations

### Order Protection Rule (SEC)
- Limit orders must execute at best price or better
- Bid/ask setting rules
- Trade through protection

### Short Sale Rule (RegSHO)
- Threshold: Shares short not locatable
- Locate Requirement: Broker must find shares
- Borrow Requirement: Shares must be borrowed

### Pattern Day Trader Rule
- Definition: 4+ day trades in 5 trading days
- Requirement: $25K minimum equity
- Buying Power: 4x maintenance excess

## Best Practices

1. **Default to Simple**: Use market/limit unless special need
2. **Day Orders**: Most common, reset daily
3. **Risk Limits**: Combine with bracket orders
4. **Monitoring**: Check GTC orders regularly
5. **Documentation**: Log all order modifiers for audit
