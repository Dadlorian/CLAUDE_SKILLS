# Dark Pools and Alternative Venues Reference

## Dark Pool Definition

**Dark Pool**: Electronic trading venue with no pre-trade transparency of orders or prices.

**Key Characteristics**:
- No level 1 or level 2 quotes published
- No real-time price discovery
- Post-trade transparency (trades reported after execution)
- Lower market impact for large orders
- Institutional focus

## Dark Pool Types

### Operator-Owned Dark Pools

**Citadel**
- Pure dark pool operator
- Largest US dark pool
- ~4-5% market share
- Sophisticated order routing

**Barclays LX+**
- Investment bank dark pool
- Structured dark pool
- Quality order flow focus
- ~2-3% market share

**Goldman Sachs Sigma X**
- GS institutional client orders
- Integrated with GS algorithms
- High execution quality
- ~2-3% market share

**JP Morgan eSpeed**
- JPM client orders
- Institutional focus
- Execution quality
- ~1-2% market share

### Broker-Dealer Crossing Networks

**Existing for decades**
- E*TRADE, Schwab internalized flow
- Fidelity Crossing Network
- Charles Schwab Client-to-Client

**Characteristics**:
- Broker-specific client flow
- Limited to broker clients
- No external market access
- Cost reduction focus

## Dark Pool Mechanics

### Order Types

**Pegged Orders**:
- Price pegged to lit market
- Example: 0.5 cents inside national best bid/offer
- Execution at peg level if liquidity available

**Block Orders**:
- Large institutional orders
- Negotiated outside dark pool system
- Reported as block trades

**Iceberg Orders**:
- Visible portion displayed
- Hidden reserve replenishes
- Minimize market impact

### Pricing Methods

**Mid-Point Execution**:
- Execute at midpoint of NBBO
- No information leakage
- Appealing to both sides
- Most common dark pool execution

**VWAP-Based**:
- Execute at VWAP from previous session
- Reference-based pricing
- Fair to both sides
- Less common now

**Percentage of Volume**:
- Execute as % of prior period volume
- Time-weighted execution
- Reduces execution signal

## Execution Quality Comparison

### Lit Venue Execution

```
Venue: NYSE
Order: Buy 10,000 AAPL
Entry Price: $150.00
Execution: 0.05 at $150.00, 0.95 at $150.01
Final Cost: $150.0095/share
Total Cost: 10,000 × $150.0095 = $1,500,095
vs VWAP of $150.00: $95 slippage
```

### Dark Pool Execution

```
Venue: Citadel Dark Pool
Order: Buy 10,000 AAPL
Entry Price: $150.00 (NBBO: 149.99 bid / 150.00 ask)
Execution: 10,000 at midpoint $149.995
Total Cost: 10,000 × $149.995 = $1,499,950
vs VWAP of $150.00: -$50 savings
Market Impact: None (no price discovery)
```

## Dark Pool Challenges

### Information Risk

**Information Leakage**:
- Traders may assume large dark orders present
- Patterns may reveal intent
- Front-running risk (even with anonymity)

### Execution Risk

**Incomplete Fill**:
- May not find matching liquidity
- Fallback to lit venues required
- Execution timing affects quality

**Legging Risk**:
- Multi-leg orders may not complete
- Execution of partial orders
- Residual position management

### Regulatory Scrutiny

**SEC Concerns**:
- Impact on price discovery
- Market fragmentation effects
- Investor protection issues

**Recent Regulations**:
- Venue Identification Code (VIC) requirements
- Order-to-execution tracking
- Surveillance obligations
- Compliance costs increasing

## Market Regulation of Dark Pools

### Rule 10b-5 (SEC)
- Prohibition on market manipulation
- Applies to dark pools
- Spoofing, layering, marking the close

### Rule 605/606 (SEC)
- Execution quality reporting
- Routing practices disclosure
- Applicable to ATSs and venues
- Annual reporting requirement

### Rule 1000 (SEC)
- ATS Registration requirements
- Governance rules
- Audit trail requirements
- SHO compliance

### Examples of Dark Pool Fines

```
Barclays LX+: $70M (2015)
- Failure to isolate certain orders
- Improper system access
- Misleading marketing

Citadel Securities: $700K (2016)
- Disruptive trading violations
- Rapid order entry/cancellation

JP Morgan eSpeed: $50M (2020)
- Disclosure failures
- Market manipulation concerns
```

## Alternative Trading Systems (ATS)

### ATS Definition

**Alternative Trading System**: Electronic communication network not registered as national securities exchange.

**Registration**: SEC Form ATS-N filing
**Requirements**: Similar to exchanges but lighter touch
**Regulation**: SEC oversight

### Major ATSs

**BATS BZX**
- Originally "Better Alternative Trading System"
- Now CBOE subsidiary
- ~10% US equity volume
- Aggressive pricing

**Nasdaq OMX PSX**
- Post-execution communications facility
- Smaller ATS
- Specialized focus
- ~1% volume

**Liquidnet**
- Institutional trading platform
- Block trading focus
- 70K+ institutional clients
- Dark pool characteristics

## Hybrid Models

### Lit + Dark Combination

**CBOE Strategy**:
- BZX (lit exchange) for transparency
- BYX (dark pool) for anonymity
- Integrated routing
- Best of both approaches

**Venue Benefits**:
- Lit venues get price discovery
- Dark pools get low-impact execution
- Traders access both

## Execution Routing Logic

### Smart Order Router Decision

```python
def route_order(order):
    """Determine optimal execution venue"""

    if order.size > 100000:
        # Large orders benefit from dark pool
        if try_dark_pool(order):
            return "DARK_POOL"

    # Check best lit venue price
    best_lit = find_best_lit_venue(order)

    # Estimate dark pool price (mid-point)
    dark_price = estimate_dark_pool_price(order)

    # Compare net cost
    if dark_price_better(best_lit, dark_price, order.size):
        # Try dark pool first
        if try_dark_pool(order):
            return "DARK_POOL"
        # Fallback to lit if no fill
        return best_lit

    return best_lit
```

## Market Impact of Dark Pools

### Positive Effects
- Reduced execution costs for large orders
- Lower market impact
- Institutional clients benefit
- Volatility reduction during execution

### Negative Effects
- Price discovery reduced
- Tick size changes (post-regulation)
- Information asymmetry
- Reduced transparency

### Empirical Evidence
```
Studies show:
- Dark pool use reduces execution cost 5-15 bps for large orders
- Overall market quality largely unaffected
- Spreads have tightened significantly post-Reg SHO
- Total market volume increasing with dark pools
```

## Compliance Requirements for Dark Pool Operators

### SEC Filings
- **Form ATS-N**: Initial registration
- **Annual updates**: Changes to operations
- **Audit reports**: Third-party compliance audits
- **Reporting**: Monthly volume, weekly trades

### Operational Requirements
- **Surveillance**: Market manipulation detection
- **Order Audit Trail**: Complete tracking
- **System Testing**: Capacity, resilience
- **Business Continuity**: Disaster recovery

### Best Execution
- **Routing**: To best execution venues
- **Pricing**: Fair to both sides
- **Conflict of Interest**: Disclosures

## Future of Dark Pools

### Trends

**Increasing Regulation**:
- SEC tightening requirements
- Transparency requirements increasing
- Surveillance expectations higher
- Compliance costs rising

**Technology Change**:
- Blockchain-based systems emerging
- Smart contract execution
- New market structure possibilities

**Market Evolution**:
- Crypto dark pools emerging
- International dark pools expanding
- Consolidation of small dark pools
- Winners/losers emerging

## Best Practices for Users

1. **Appropriate Order Types**: Use when order size significant
2. **Execution Quality Monitoring**: Track dark pool results
3. **Fallback Strategy**: Have lit venue fallback
4. **Disclosure**: Communicate dark pool usage
5. **Testing**: Backtest dark pool assumptions
6. **Regulation**: Stay current with requirements
