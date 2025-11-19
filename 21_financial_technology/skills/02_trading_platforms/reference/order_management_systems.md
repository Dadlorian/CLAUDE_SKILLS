# Order Management Systems (OMS) Reference

## Architecture Overview
An Order Management System is the central component managing the entire order lifecycle from creation through execution and settlement.

## Order Lifecycle States

```
New → Accepted → Partially Filled → Filled
         ↓
      Rejected/Canceled
         ↓
      Expired
```

### State Transition Rules
- **New to Accepted**: Validation completed, sent to venue
- **Accepted to Pending Replace**: Amendment pending confirmation
- **Partially Filled to Filled**: Remaining quantity filled
- **Any state to Canceled**: User cancellation or risk breach
- **Any state to Rejected**: Venue rejection or validation failure

## Core Components

### Order Entry Module
- User order creation and validation
- Order type selection (market, limit, iceberg, pegged)
- Time-in-force options (day, GTC, IOC, FOK)
- Position tracking and limit checks

### Routing Engine
- Venue selection logic
- Order splitting for large orders
- Execution strategy selection
- FIX session routing

### State Management
- Order state machine implementation
- Atomic state transitions
- Event-driven updates
- Audit trail maintenance

### Amendment Handling
- Order modification requests
- Quantity changes
- Price changes for limit orders
- Complete replacement logic

### Reconciliation
- Trade confirmation matching
- Execution report processing
- Fill reconciliation
- Discrepancy handling

## Order Attributes

### Mandatory
- OrderID (unique identifier)
- Security identifier (ticker, ISIN, CUSIP)
- Side (buy/sell)
- Quantity (shares/contracts)
- Order type (market/limit)
- Account identifier

### Optional
- Limit price (for limit orders)
- Time-in-force
- Iceberg quantity
- Pegged offset
- Display quantity
- Expire time
- Min quantity

## Performance Characteristics

### Latency Targets
- Order entry to OMS acceptance: <100µs
- OMS to FIX send: <500µs
- Execution report reception to UI: <1ms
- Amendment request to venue: <500µs

### Throughput Targets
- Order entry rate: 50K orders/second
- Execution report processing: 100K reports/second
- Amendment rate: 10K amendments/second

### Storage Requirements
- 1 million active orders: ~500MB (with full history)
- 1 year of order history: ~100GB (compressed)

## Data Structures

### Order Book Entry
```
struct Order {
    uint64_t order_id;
    uint32_t security_id;
    uint64_t timestamp_ns;
    uint32_t account_id;
    Side side;
    OrderType type;
    uint32_t quantity;
    uint32_t filled_quantity;
    double limit_price;
    TimeInForce tif;
    OrderStatus status;
    vector<Fill> fills;
    uint64_t seq_number;
};
```

## Best Practices

1. **Idempotent Operations**: Handle duplicate messages gracefully
2. **Atomic Transitions**: Use atomic operations for state changes
3. **Audit Trail**: Log every state transition with full context
4. **Error Handling**: Clear rejection reasons for end users
5. **Monitoring**: Real-time OMS health metrics and alerts

## Integration Points
- **EMS**: Provides execution algorithms and multi-leg orders
- **RMS**: Validates against position and exposure limits
- **Settlement**: Generates settlement instructions
- **Post-Trade Analytics**: Provides execution data for analysis
- **Compliance**: Feeds market surveillance systems

## Regulatory Considerations
- **Trade Reporting**: All trades must be reported within timeframe
- **Order Audit Trail**: Complete order lifecycle history required
- **Best Execution**: OMS must support best execution determination
- **MiFID II**: Algorithm selection disclosure, slippage reporting
