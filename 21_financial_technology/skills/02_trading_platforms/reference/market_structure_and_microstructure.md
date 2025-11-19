# Market Structure and Microstructure Reference

## Market Architecture

### Market Types

**Auction Market**
- Single price clearing
- Order accumulation at opening/closing
- Price discovery through matching
- Example: Opening/closing auctions

**Continuous Market**
- Orders match immediately
- Price discovery continuous
- Liquidity available at discrete levels
- Example: Intraday trading

**Hybrid Market**
- Continuous with auction phases
- Intraday + opening/closing auctions
- Most modern equity markets

### Venue Types

**Exchange (Lit Venues)**
- Centralized order book
- Pre-trade transparency (Level 2/3)
- Post-trade transparency (trades public)
- Regulatory oversight
- Examples: NYSE, NASDAQ, LSE

**Alternative Trading Systems (ATS)**
- Electronic communication networks
- Often dark (pre-trade dark)
- Similar regulation to exchanges
- Examples: BATS, Direct Edge

**Dark Pools**
- No pre-trade transparency
- Post-trade public reporting
- Lower transaction costs
- Execution quality concerns
- Examples: Citadel, Barclays LX+

**Broker Crossing Networks**
- Broker proprietary systems
- Internal order matching
- External reporting required

## Order Book Structure

### Standard Order Book

```
Level   Bid Qty    Bid Price    Ask Price   Ask Qty
  1       500        $99.95       $100.00      400
  2      1000        $99.90       $100.05      800
  3      1500        $99.85       $100.10     1200
  4      2000        $99.80       $100.15     1500
  5      2500        $99.75       $100.20     2000
```

### Book Dynamics
- **Spread**: Difference between best bid and ask ($0.05)
- **Depth**: Total quantity at each level
- **Imbalance**: Bid quantity vs ask quantity
- **Resilience**: How quickly depleted levels replenish

### Market Depth

**Thin Markets**
- Few orders at best levels
- Wide spreads
- High execution risk
- Prices move on small orders

**Deep Markets**
- Many orders across levels
- Tight spreads
- Stable prices
- Liquidity available

## Microstructure Concepts

### Bid-Ask Spread

**Determinants**
- **Inventory**: Inventory costs to market maker
- **Information**: Information risk to counterparty
- **Competition**: Number of competitors
- **Volatility**: Price uncertainty
- **Order Flow**: Trading activity level

**Components**
- **Effective Spread**: (Trade price - midpoint) × 2
- **Realized Spread**: (Midpoint at later time - trade price) × 2
- **Quote Spread**: Published bid-ask spread

### Price Behavior

**Tick Size**
- **Definition**: Minimum price increment
- **Large tick**: $0.01 (traditional equities)
- **Small tick**: $0.001 (pilot program)
- **Effects**: Spread changes, liquidity changes

**Mid-Quote**
- **Calculation**: (Best Bid + Best Ask) / 2
- **Reference**: Midpoint of spread
- **Movement**: Indicates price direction

**Returns**
- **Log Returns**: ln(P_t / P_{t-1})
- **Volatility**: Standard deviation of returns
- **Autocorrelation**: Dependency on previous returns

### Market Maker Mechanics

**Inventory Management**
- Position accumulation avoidance
- Rebalancing frequency
- Hedging strategies
- Risk limits

**Liquidity Provision**
- Quote placement
- Order size decisions
- Risk-return tradeoff
- Profit optimization

**Information Asymmetry**
- Adverse selection
- Order flow information
- Inventory information
- Price discovery role

## Order Flow and Liquidity

### Liquidity Tiers

**Maker Liquidity**
- Passive limit orders
- Sitting on order book
- Add to liquidity
- Lower fees (rebate)

**Taker Liquidity**
- Aggressive market orders
- Remove from order book
- Take existing liquidity
- Higher fees (cost)

### Liquidity Quality

**Availability**
- Quantity at spread
- Depth across price levels
- Time to full satisfaction

**Temporality**
- Duration available
- Recovery after depletion
- Consistency over time

**Resilience**
- Recovery speed
- How fast spread tightens
- Order flow impact

### Information Asymmetry

**Adverse Selection**
- Market maker loses on informed trades
- Uninformed trades increase maker profit
- Spread wider when informed likely

**Inventory Risk**
- Accumulation of position
- Rebalancing costs
- Unwanted exposure management

## Execution Concepts

### Market Impact

**Temporary Impact**
- Bid-ask spread costs
- Immediate price concession
- Recovers quickly
- Liquidity provision costs

**Permanent Impact**
- Price movement from order flow
- Information revelation
- Persists after execution
- Market learns from trade

**Total Impact**
- Sum of temporary and permanent
- Depends on order size
- Depends on market depth
- Non-linear with size

### Execution Shortfall Components

```
Total Shortfall = Timing Cost + Liquidity Cost + Opportunity Cost

Timing Cost: Market move during execution
Liquidity Cost: Execution at worse prices than midpoint
Opportunity Cost: Unable to complete order
```

## Statistical Properties

### Return Distribution
- **Leptokurtosis**: Fat tails (more extreme moves)
- **Skewness**: Asymmetric distribution
- **Clustering**: Volatility persistence
- **Jump Risk**: Discontinuous price changes

### Volume Patterns
- **U-Shape**: High at open/close, low midday
- **Intraday Seasonality**: Time-of-day patterns
- **Monthly Effects**: Month-end rebalancing
- **Day-of-Week**: Different day patterns

### Volatility Regimes
- **Low Vol**: Stable prices, tight spreads
- **High Vol**: Wide spreads, big moves
- **Regime Switching**: Rapid changes
- **Correlation**: Vol increases with volume

## Fragmentation Effects

### Market Fragmentation
- **Lit Venues**: ~60% equity trading
- **Dark Pools**: ~20% equity trading
- **Broker Crossing**: ~10% equity trading
- **Off-Venue**: Small percent

### Execution Quality Impact
- **Best Price**: Must check all venues
- **Order Routing**: Complex SOR needed
- **Latency**: Speed to all venues critical
- **Regulatory**: RegSHO compliance required

## Behavioral Microstructure

### Order Clustering
- Orders arrive in bursts
- Self-exciting point process
- Predictable phases
- Execution scheduling

### Price Momentum
- Short-term reversals
- Medium-term continuations
- Long-term reversals
- Trading implications

### Herding Behavior
- Correlated order flow
- Information cascades
- Feedback effects
- Market stress indicators

## Regulatory Structure
- **Pre-Trade Transparency**: Quote disclosure (lit venues)
- **Post-Trade Transparency**: Trade reporting
- **Best Execution**: Obligation to seek best terms
- **Order Protection**: Limit order protection rules
