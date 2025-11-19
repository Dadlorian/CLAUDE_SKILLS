# Tick Data Processing Reference

## Tick Data Definition

**Tick**: Single market event (trade, quote, order book change)

**Tick Data**: Sequence of all market events with nanosecond timestamps

**Characteristics**:
- High volume (1M+ ticks/second possible)
- Time-ordered sequence
- Complete market history
- Real-time and historical

## Data Types in Tick Stream

### Level 1 Ticks
- **Quote ticks**: Best bid/ask changes
- **Trade ticks**: Completed transactions
- **Volume ticks**: Volume-at-level changes

### Level 2 Ticks
- **Order book changes**: Any level update
- **Depth changes**: Multiple levels simultaneously
- **Imbalance ticks**: Bid-ask imbalance updates

### Level 3 Ticks
- **Order events**: New, cancel, modify, fill
- **Order ID mapping**: Track individual orders
- **Participant identification**: Who placed order

## Tick Processing Pipeline

```
Raw Packets (NIC)
    ↓
Packet Parsing
    ↓
Message Extraction
    ↓
Format Conversion (normalize)
    ↓
Timestamp Adjustment (latency compensation)
    ↓
Order Book Update
    ↓
Analytics (VWAP, volume, etc.)
    ↓
Storage/Distribution
```

## Performance Characteristics

### Volume Rates
- **Slow markets**: 1K ticks/second
- **Normal markets**: 100K ticks/second
- **Active markets**: 1M+ ticks/second
- **Peak events**: 10M ticks/second possible

### Latency Requirements

**Real-Time Processing**:
- Message arrival to processing: <100µs
- Processing to update: <500µs
- Update to consumer distribution: <1ms
- Total end-to-end: <2ms

### Storage Requirements

**Size Estimation**:
```
Per tick: ~50 bytes (price, volume, timestamp, etc.)
Per second (500K ticks): 25MB
Per hour: 90GB
Per day (6 hours trading): 540GB
Per year: 135TB

Compressed: ~20% of original
With archiving: 30TB/year
```

## Tick Data Formats

### Standard Binary Format
```
struct TickData {
    uint64_t timestamp_ns;      // Nanosecond timestamp
    uint32_t security_id;        // Security identifier
    uint8_t tick_type;           // 0=quote, 1=trade, etc.
    uint16_t sequence;           // Sequence number
    int32_t bid_price;           // Bid × 10000 (fixed decimal)
    int32_t ask_price;           // Ask × 10000
    uint32_t bid_volume;         // Shares at bid
    uint32_t ask_volume;         // Shares at ask
    uint32_t trade_price;        // Trade price (if trade)
    uint32_t trade_volume;       // Trade quantity
    uint8_t flags;               // Trade conditions, etc.
};  // 40 bytes per tick
```

### Compressed Format

**Delta Encoding**:
```
Store deltas from previous tick instead of absolute values
timestamp_delta = current_ts - previous_ts (small number)
price_delta = current_price - previous_price (often 0 or ±1)
Reduces average tick to 8-15 bytes
```

**Run-Length Encoding**:
```
If bid/ask unchanged for 100 ticks, store count
Instead of 100 identical ticks, store: count=100, unchanged
Useful for stable markets
```

## Processing Considerations

### Timestamp Synchronization

**Clock Sync Issues**:
```
Multiple feeds may have slightly different clocks
Need to synchronize to single timeline
```

**Solution Approaches**:
```
1. Use exchange-provided timestamps (preferred)
2. Adjust local timestamps based on offset detection
3. PTP (Precision Time Protocol) for hardware sync
4. NTP for less critical sync
```

### Gap Handling

**Network Losses**:
```
May lose packets in UDP transmission
Detect using sequence numbers
Request retransmit or fill from snapshot
```

**Code**:
```cpp
uint16_t last_sequence = 0;

void process_tick(const TickData& tick) {
    if (tick.sequence != last_sequence + 1) {
        uint16_t gap = tick.sequence - last_sequence - 1;
        LOG_WARNING("Gap detected: " << gap << " ticks");
        request_retransmit(last_sequence + 1, tick.sequence - 1);
    }
    last_sequence = tick.sequence;

    process_tick_data(tick);
}
```

### Duplicate Detection

**Idempotent Processing**:
```
If duplicate tick received (from retransmit), don't reprocess
Track processed sequence numbers
Detect and skip duplicates
```

## Order Book Reconstruction

### From Tick Stream

```python
class OrderBook:
    def __init__(self):
        self.bids = SortedDict()  # price -> volume
        self.asks = SortedDict()
        self.timestamp = None

    def apply_tick(self, tick):
        self.timestamp = tick.timestamp

        if tick.type == QUOTE:
            # Update best bid/ask
            self.bids[tick.bid_price] = tick.bid_volume
            self.asks[tick.ask_price] = tick.ask_volume

        elif tick.type == TRADE:
            # Match against book
            self.apply_trade(tick)

        elif tick.type == ORDER:
            # Update order count at level
            self.process_order(tick)

    def get_depth(self, levels=10):
        """Return top N levels"""
        return {
            'bids': list(self.bids.items())[-levels:],
            'asks': list(self.asks.items())[:levels]
        }

    def get_spread(self):
        """Calculate current spread"""
        best_bid = self.bids.peekitem()[0]
        best_ask = self.asks.peekitem(0)[0]
        return best_ask - best_bid
```

## Real-Time Analytics from Ticks

### VWAP Calculation

```python
def calculate_vwap(ticks, window_seconds=3600):
    """Calculate VWAP from tick stream"""
    sum_pq = 0  # sum of price × quantity
    sum_q = 0   # sum of quantity

    cutoff_time = ticks[-1].timestamp - window_seconds * 1e9

    for tick in ticks:
        if tick.timestamp >= cutoff_time and tick.type == TRADE:
            sum_pq += tick.price * tick.quantity
            sum_q += tick.quantity

    vwap = sum_pq / sum_q if sum_q > 0 else 0
    return vwap
```

### Volume Analysis

```python
def volume_analysis(ticks, window_seconds=60):
    """Analyze volume in time window"""
    total_volume = 0
    buy_volume = 0
    sell_volume = 0

    cutoff_time = ticks[-1].timestamp - window_seconds * 1e9

    for tick in ticks:
        if tick.timestamp >= cutoff_time and tick.type == TRADE:
            total_volume += tick.quantity
            if tick.side == BUY:
                buy_volume += tick.quantity
            else:
                sell_volume += tick.quantity

    return {
        'total': total_volume,
        'buy': buy_volume,
        'sell': sell_volume,
        'buy_pct': buy_volume / total_volume if total_volume > 0 else 0
    }
```

### Microstructure Metrics

```python
def calculate_microstructure(ticks):
    """Calculate order book microstructure metrics"""

    # Effective spread
    last_trade = [t for t in ticks if t.type == TRADE][-1]
    midpoint = (last_quote.bid + last_quote.ask) / 2
    effective_spread = 2 * abs(last_trade.price - midpoint)

    # Roll measure (bid-ask bounce)
    prices = [t.price for t in ticks if t.type == TRADE]
    roll = 0
    for i in range(1, len(prices)):
        roll += prices[i] * prices[i-1]  # Approximation

    return {
        'effective_spread': effective_spread,
        'spread_ratio': effective_spread / midpoint,
        'roll': roll / len(prices),
        'volatility': np.std([t.price for t in ticks if t.type == TRADE])
    }
```

## Storage & Retrieval

### High-Speed Tick Database

**Requirements**:
- Ingest 1M+ ticks/second
- Query historical data efficiently
- Compress to reasonable size
- Real-time and batch access

**Solution Approaches**:
1. **In-Memory DB**: InfluxDB, Cassandra for recent data
2. **Time-Series DB**: Specialized for time-ordered data
3. **Columnar DB**: Parquet files for historical archives
4. **Hybrid**: Hot data in memory, cold in archive

## Backtesting with Tick Data

### Replay System

```python
class TickReplayEngine:
    def __init__(self, start_time, end_time):
        self.ticks = load_tick_data(start_time, end_time)
        self.current_idx = 0
        self.order_book = OrderBook()

    def step(self):
        """Process one tick at a time"""
        if self.current_idx >= len(self.ticks):
            return False

        tick = self.ticks[self.current_idx]
        self.order_book.apply_tick(tick)
        self.current_idx += 1

        # Notify listeners
        for listener in self.listeners:
            listener.on_tick(tick, self.order_book)

        return True

    def run(self):
        """Run replay to completion"""
        while self.step():
            pass
```

## Best Practices

1. **Maintain Sequence Integrity**: Track gaps, handle retransmits
2. **Timestamp Consistency**: Synchronize all clocks
3. **Efficient Storage**: Use compression effectively
4. **Fast Retrieval**: Index by timestamp and security
5. **Duplicate Handling**: Idempotent processing
6. **Error Recovery**: Graceful handling of data loss
