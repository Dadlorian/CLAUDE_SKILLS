# Trading Venues Reference

## Venue Types

### National Securities Exchanges (Lit Venues)

**NYSE (New York Stock Exchange)**
- **Status**: Primary exchange for large-cap US equities
- **Hours**: 9:30 AM - 4:00 PM ET
- **Open Auctions**: 9:30 AM (opening), 4:00 PM (closing)
- **Technology**: NYSE Euronext systems
- **Feed**: OpenBook (Level 2), New York Stock Exchange Feed
- **Fees**: ~$0.001/share (typical maker-taker)
- **Market Share**: ~20% of US equity volume

**NASDAQ**
- **Status**: Tech-heavy exchange (AAPL, MSFT, GOOGL)
- **Hours**: 9:30 AM - 4:00 PM ET
- **Pre-Market**: 4:00 AM - 9:30 AM ET
- **After-Hours**: 4:00 PM - 8:00 PM ET
- **Feed**: ITCH (binary protocol), OUCH (orders)
- **Fees**: Variable, typical $0.001-0.003/share
- **Market Share**: ~15% of US equity volume

**BATS/CBOE**
- **Status**: Largest electronic exchange by volume
- **Hours**: 4:00 AM - 8:00 PM ET
- **Fee Structure**: Highly competitive
- **Feed**: Proprietary protocols
- **Market Share**: ~20% of US equity volume

**Other Exchanges**:
- NYSE Arca
- NYSE MKT (formerly AMEX)
- NASDAQ OMX
- NASDAQ PSX

### Alternative Trading Systems (ATS)

**BATS BZX/BYX**
- Electronic communication networks
- Similar to exchanges but lighter regulation
- Significant volume in equities and options
- Aggressive fee structure

**Nasdaq OMX PSX**
- Post-execution communications facility
- Lower volume but specialized

**Citadel/Citadel Derivatives**
- Broker-dealer systems
- Internal order matching
- Not available to retail

### Dark Pools

**Barclays LX+**
- Structured dark pool
- Institutional flow
- Execution quality focus
- Higher fees but significant volume

**Goldman Sachs Sigma X**
- Large dark pool
- Significant market share in equities
- Algorithmic execution

**Citadel**
- Pure dark pool operator
- Market-making strategies
- Not for retail

**ITG/Posit**
- Institutional trading
- Anonymous execution

## Venue Characteristics

| Aspect | Lit Exchange | ATS | Dark Pool |
|--------|--------------|-----|-----------|
| **Pre-Trade Transparency** | Full | Full | None |
| **Post-Trade Reporting** | Yes | Yes | Yes |
| **Liquidity** | High | Medium | Variable |
| **Spread** | Tight | Medium | Often mid-point |
| **Market Impact** | High | Medium | Low |
| **Regulatory** | SEC Regulation SHO | ATS Reg | 605 Rule |

## Global Venues

### European Exchanges

**London Stock Exchange (LSE)**
- Largest European exchange
- Trading hours: 8:00 AM - 4:30 PM GMT
- Primary market for UK equities
- Secondary market for international stocks

**Euronext**
- Multiple European exchanges
- Amsterdam, Brussels, Dublin, Lisbon, Paris
- Trading hours: 9:00 AM - 5:30 PM CET
- Most liquid European market

**Deutsche Börse**
- German exchange (Xetra)
- Trading hours: 8:00 AM - 8:00 PM CET
- DAX index primary market

### Asian Exchanges

**Tokyo Stock Exchange**
- Morning session: 9:00 AM - 11:00 AM JST
- Afternoon session: 12:30 PM - 3:00 PM JST
- Japan's largest exchange
- Nikkei index primary market

**Hong Kong Stock Exchange**
- Trading hours: 9:30 AM - 4:00 PM HKT
- Secondary session: 4:00 PM - 5:00 PM HKT
- Asia-Pacific hub for international trading

**Shanghai Stock Exchange**
- Morning session: 9:30 AM - 11:30 AM CST
- Afternoon session: 1:00 PM - 3:00 PM CST
- China's primary exchange

## Access Methods

### Direct Market Access (DMA)
- Direct venue connection
- Firm's credentials
- Lower latency
- Higher costs

### Broker-Assisted
- Through broker's systems
- Broker credit required
- Higher latency
- Lower costs

### Algorithm Selection
- Broker selects venue
- Algorithm-driven routing
- Execution quality focus
- Cost optimization

## Connectivity Standards

### FIX Protocol
- Industry standard
- Order entry and execution reports
- FIX 4.2, 4.4, 5.0
- Typical latency: 1-10ms

### ITCH (Binary)
- NASDAQ proprietary
- Market data feed
- High-speed format
- <100µs latency possible

### Direct Feeds
- Exchange-specific
- Custom binary protocols
- Lowest latency
- Highest complexity

### Co-location
- Physical proximity to exchange
- Reduced network latency
- Significant cost ($5K-20K/month)
- <1ms total latency possible

## Fee Structures

### Typical Maker-Taker Model

```
Maker Rebate:   +$0.001/share
Taker Fee:      -$0.003/share
Example:
  Sell 1000 @ $100 (maker):  $1.00 rebate
  Buy 1000 @ $100 (taker):   -$3.00 fee
```

### Volume-Based Tiers

```
Volume Tier    Maker Rebate    Taker Fee
<100K          $0.0008         -$0.003
100K-500K      $0.0009         -$0.0025
500K+          $0.0010         -$0.002
1M+ (VIP)      $0.0011         -$0.0015
```

### Hidden Liquidity Fees

```
Iceberg/Post-Only:  Additional fee
Post-to Midpoint:   Potential rebate
Adding Liquidity:   Maker side benefits
```

## Venue Selection Logic

### Factors to Consider

```python
def select_venue(security, side, size):
    venues = get_available_venues(security)

    best_score = -infinity
    best_venue = None

    for venue in venues:
        # Score = spread quality - fees - market impact

        spread = get_spread(venue, security)
        fee = get_applicable_fee(venue, side, size)
        depth = get_available_depth(venue, security, size)

        market_impact = estimate_market_impact(
            venue, security, side, size, depth
        )

        score = -(spread + fee + market_impact)

        if score > best_score:
            best_score = score
            best_venue = venue

    return best_venue
```

### Real-Time Venue Monitoring

```
Track for each venue:
- Best bid/ask
- Available depth
- Execution quality
- Latency
- Fee costs
- Downtime/issues

Route orders to:
1. Best execution venue
2. Backup if primary unavailable
3. Diversify for large orders
```

## Regulatory Framework

### SEC Regulation SHO
- Borrow requirement for short sales
- Locate requirement
- Applicable at all venues
- Enforcement by FINRA

### MiFID II (Europe)
- All venues must comply
- Best execution obligation
- Execution quality reporting
- Transparent fee structures

### Best Execution
- Obligation to route to best venue
- Documentation required
- Regular assessment needed
- Auditable venue selection

## Contingency Planning

### Venue Outage Handling

```
If primary venue unavailable:
1. Switch to secondary venue
2. Adjust price expectations
3. Notify traders
4. Document reason for switch
5. Review execution quality
```

### Circuit Breakers
- NYSE: 7%, 13%, 20% index declines
- NASDAQ: Similar percentages
- Automatic trading halts
- Market-wide automatic pause

## Best Practices

1. **Diversify Venues**: Don't rely on single venue
2. **Monitor Execution Quality**: Track slippage by venue
3. **Optimize Routing**: Use SOR algorithms
4. **Fee Optimization**: Understand fee structures
5. **Contingency Plans**: Have backup venues ready
6. **Regulatory Compliance**: Follow best execution rules
