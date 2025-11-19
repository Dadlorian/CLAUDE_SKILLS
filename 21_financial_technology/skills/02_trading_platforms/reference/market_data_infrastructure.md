# Market Data Infrastructure Reference

## Overview
Market data infrastructure is the backbone of trading systems, providing real-time information about prices, volumes, and trading activity across financial markets.

## Data Types

### Level 1 (Top of Book)
- **Best Bid**: Highest price buyers willing to pay
- **Best Ask**: Lowest price sellers willing to accept
- **Bid Volume**: Quantity available at best bid
- **Ask Volume**: Quantity available at best ask
- **Last Trade**: Most recent transaction price and volume

### Level 2 (Book Depth)
- **Order Book**: Multiple price levels (typically 10-20 levels)
- **Each level**: Price, bid volume, ask volume
- **Timestamp**: Nanosecond precision update timing
- **Sequence number**: For ordering updates

### Level 3 (Full Book)
- **All open orders** at all price levels
- **Order ID mapping** for tracking order changes
- **Trading participant information**
- **VWAP-relevant data** for weighted calculations

### Trade Data
- **Trade price and volume**
- **Trade timestamp** (reported and system)
- **Trading participant** identification
- **Aggressor side** (buyer/seller initiated)
- **Trade conditions** (opening, closing, etc.)

## Data Feed Protocols

### Direct Exchange Feeds
- **NASDAQ ITCH**: NASDAQ's proprietary binary protocol
- **NYSE OpenBook**: NYSE depth-of-book feed
- **CME MDP**: CME's Market Data Platform
- **EUREX Xetra**: European exchange data

### Market Data Protocols
- **MOLD**: Reliable UDP multicast protocol with replay
- **OUCH**: NASDAQ order entry protocol
- **QuickFIX**: Industry-standard protocol for FIX messages
- **Custom binary**: Exchange-specific high-speed formats

## Data Quality Considerations

### Completeness
- No missing messages or gaps
- Snapshot reconstruction capability
- Incremental update sequences

### Accuracy
- Correct timestamps with nanosecond precision
- Accurate prices and volumes
- Proper sequence numbering

### Timeliness
- <1ms latency from exchange to trading system
- Consistent update intervals
- Heartbeat detection for feed loss

### Consistency
- Consistent across multiple feeds
- Proper normalization handling
- Symbol mapping accuracy

## Multi-Feed Aggregation

### Challenges
- Different protocols and formats
- Asynchronous arrivals
- Different timestamp conventions
- Duplicate message handling

### Solution Approaches

**Normalization**
- Convert all feeds to common format
- Timestamp synchronization
- Symbol mapping
- Adjustment handling

**Aggregation**
- Combine bids/asks from multiple sources
- Calculate synthetic spreads
- Best execution monitoring
- Fragmented order detection

**Priority Handling**
- Feed preference rules
- Fallback mechanisms
- Stale data detection
- Conflict resolution

## Snapshot and Incremental Updates

### Snapshot Format
- Complete order book state
- All price levels
- Cumulative volumes
- Reference timestamp

### Incremental Updates
- Changes since last snapshot
- New orders, cancellations, executions
- Efficient bandwidth usage
- Requires snapshot for reconstruction

### Reconstruction Logic
```
snapshot = GetSnapshot()
for update in IncrementalUpdates:
    if update.type == ADD:
        snapshot.AddLevel(update)
    elif update.type == REMOVE:
        snapshot.RemoveLevel(update)
    elif update.type == MODIFY:
        snapshot.UpdateLevel(update)
```

## Performance Requirements

### Latency
- Feed reception: <100µs
- Processing and normalization: <200µs
- Order book update: <100µs
- Total end-to-end: <500µs

### Throughput
- 1000+ symbols
- 100K+ updates/second per symbol
- 1M+ total updates/second
- 200+ concurrent feeds

### Storage
- Real-time book: 1GB for 500 symbols
- Tick database: 1TB/day for comprehensive data
- Snapshot storage: 100MB every minute

## Data Architecture

### Ingestion Pipeline
```
Exchange Feed → NIC → Kernel Bypass →
Processing → Normalization → Aggregation →
Order Book Update → Consumer Distribution
```

### Hardware Acceleration
- **FPGA**: Direct packet parsing
- **NIC offloads**: RSS, GRO, TSO
- **Bypass kernels**: DPDK, Snabb
- **GPU**: VWAP calculations

## Best Practices

1. **Timestamp Everything**: Use nanosecond timestamps consistently
2. **Verify Integrity**: Detect and handle gaps in sequences
3. **Buffer Management**: Avoid memory allocations in hot paths
4. **Lock-Free Design**: Use concurrent data structures
5. **Graceful Degradation**: Handle feed outages
6. **Testing**: Replay feeds for backtesting

## Regulatory Aspects
- **Best Execution**: Monitor best prices across venues
- **Trade Reporting**: Capture all required trade details
- **Market Surveillance**: Detect suspicious trading patterns
- **Audit Trail**: Maintain complete timestamp audit trail
