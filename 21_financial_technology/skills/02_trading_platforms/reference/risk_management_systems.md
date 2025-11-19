# Risk Management Systems Reference

## Risk Management Layers

### Pre-Trade Risk
Checks performed BEFORE order enters system.
- Prevents invalid orders
- Enforces limits
- Reduces rejected orders

### Order Entry Risk
Checks during order submission.
- Position limits
- Notional limits
- Account restrictions
- Duplicate detection

### Post-Trade Risk
Checks after order execution.
- Settlement risk
- Counterparty risk
- Mark-to-market P&L
- Exposure monitoring

## Core Risk Types

### Market Risk

**Definition**: Risk of loss due to price changes.

**Components**:
- **Delta Risk**: Exposure to price changes (Δ = ∂P/∂S)
- **Gamma Risk**: Convexity of delta (Γ = ∂²P/∂S²)
- **Vega Risk**: Volatility exposure (ν = ∂P/∂σ)
- **Rho Risk**: Interest rate exposure (ρ = ∂P/∂r)
- **Theta Risk**: Time decay (Θ = ∂P/∂t)

**Measurement**:
```
Position Delta = SUM(quantity_i * delta_i)
Portfolio Delta = SUM(Position Delta)
```

### Credit Risk

**Definition**: Risk of counterparty default.

**Types**:
- **Counterparty Risk**: Broker/Exchange default
- **Settlement Risk**: Default on delivery/payment
- **Pre-settlement Risk**: Replacement cost of unsettled trades

**Monitoring**:
```
Exposure = SUM(|Mark-to-Market Value|) for counterparty
Credit Limit = Maximum allowable exposure
Utilization = Exposure / Credit Limit
Alert if Utilization > Threshold (e.g., 80%)
```

### Liquidity Risk

**Definition**: Risk of inability to exit position.

**Measures**:
- **Bid-Ask Spread**: Wider spread = harder to exit
- **Volume**: Lower volume = harder to find buyers
- **Market Impact**: Cost to exit all at once
- **Time to Exit**: Duration to unwind position

### Operational Risk

**Definition**: Risk from system failures, errors, fraud.

**Components**:
- **System Risk**: Software/hardware failures
- **Human Error**: Manual mistakes
- **Fraud Risk**: Unauthorized trading
- **Process Risk**: Broken procedures

### Regulatory Risk

**Definition**: Risk of regulatory violation.

**Components**:
- **Best Execution**: Must trade at best prices
- **Trade Reporting**: Mandatory reporting requirements
- **Position Limits**: Regulatory position caps
- **Market Conduct**: Prohibition on manipulation

## Risk Limits

### Position Limits

**Single Stock Limit**:
```
Max Quantity = Risk Limit / Stock Price
Example: $5M limit, AAPL @ $150
Max Qty = 5M / 150 = 33,333 shares
```

**Sector Limit**:
```
Max Exposure = Risk Limit / Sector Price Index
Example: Technology sector $10M limit
Monitor total tech exposure
```

**Portfolio Limit**:
```
Max Total Exposure = Risk Limit
SUM(|Position Value|) <= Risk Limit
Monitor across all positions
```

### Notional Limits

**Definition**: Limits on total value traded.

```
Daily Notional Limit = $100M
Orders Today So Far = $45M
Remaining Capacity = $55M
```

### Greeks Limits

**Delta Limit**:
```
Max Delta = 1000 (example)
Portfolio Delta = SUM(delta_i * qty_i)
Alert if Portfolio Delta > Limit
```

**Gamma Limit**:
```
Max Gamma = 100
High gamma = convexity risk
Limit to avoid P&L explosions
```

**Vega Limit**:
```
Max Vega = 500
Monitor volatility exposure
Especially for options
```

### PnL Limits

**Daily PnL Stop Loss**:
```
Max Daily Loss = $500K
If Daily PnL < -$500K, stop trading
Circuit breaker mechanism
```

**Intraday Maximum Drawdown**:
```
Max Intraday Drawdown = $250K
Monitor high-water mark
Proportional circuit breaker
```

## Risk Calculation Methods

### Value at Risk (VaR)

**Definition**: Maximum loss at confidence level over time period.

**Formula**:
```
VaR_95% = Portfolio_Value * z_score * volatility
```

**Example**:
```
Portfolio: $10M
Daily Volatility: 2%
Z-score (95% confidence): 1.645
VaR = 10M * 1.645 * 0.02 = $328.9K

95% confidence: Daily loss won't exceed $328.9K
```

### Expected Shortfall (CVaR)

**Definition**: Average loss when VaR is exceeded.

**Calculation**:
```
ES = Average of losses worse than VaR
More conservative than VaR
Better tail risk measure
```

### Stress Testing

**Approach**:
```
Apply historical/hypothetical scenarios
Example: 2008 Financial Crisis moves
Measure P&L impact
Identify vulnerable positions
```

### Scenario Analysis

**Market Stress Scenarios**:
- Volatility spike (vol +100%)
- Correlation breakdown (normally uncorrelated assets move together)
- Liquidity crisis (spreads widen)
- Interest rate shock (+/-2%)

## Pre-Trade Risk Checks

### Order Validation

```python
def validate_order(order):
    # Checks before sending to exchange

    # 1. Price reasonableness
    if not is_price_reasonable(order.price, order.security):
        reject("Price unreasonable")

    # 2. Quantity reasonability
    if not is_quantity_reasonable(order.qty, order.security):
        reject("Quantity unreasonable")

    # 3. Position limit check
    new_position = current_position + order.qty
    if abs(new_position) > position_limit:
        reject("Position limit exceeded")

    # 4. Notional limit check
    notional = order.qty * order.price
    if notional > notional_limit:
        reject("Notional limit exceeded")

    # 5. Duplicate check
    if recent_order_exists(order):
        reject("Duplicate order")

    # 6. Account active
    if not is_account_active(order.account):
        reject("Account inactive")

    # 7. Greeks limits
    if estimate_delta_impact(order) > delta_limit:
        reject("Delta limit exceeded")

    return True  # Order valid
```

### Margin Requirements

**Initial Margin**:
```
Required Margin = Position Value * Margin Ratio
Example: 100 shares @ $100 with 20% margin
Required = $10,000 * 0.20 = $2,000
```

**Maintenance Margin**:
```
Typically 50-75% of initial margin
Account marked to market daily
Forced liquidation if breached
```

## Post-Trade Monitoring

### Trade Reconstruction

```python
def validate_settlement(trade):
    # Ensure trade details correct

    assert trade.qty > 0
    assert trade.price > 0
    assert trade.settlement_date >= today
    assert trade.counterparty_verified()
    assert trade.sec_id_valid()

    return True
```

### P&L Monitoring

```python
def calculate_pnl(position):
    # P&L = (Current Price - Entry Price) * Quantity

    market_price = get_current_price(position.security)
    entry_price = position.avg_entry_price
    qty = position.quantity

    unrealized_pnl = (market_price - entry_price) * qty
    realized_pnl = position.realized_pnl

    return {
        'unrealized': unrealized_pnl,
        'realized': realized_pnl,
        'total': unrealized_pnl + realized_pnl
    }
```

### Counterparty Monitoring

```python
def monitor_counterparty(counterparty):
    exposure = SUM(mtm_value for all trades)
    utilization = exposure / credit_limit

    if utilization > 0.8:
        alert("High counterparty utilization")

    if exposure > credit_limit:
        block_new_trades(counterparty)
```

## Risk Reporting

### Daily Reports
- Gross/net exposure
- Greeks summary
- VaR estimates
- Limit utilization
- Counterparty exposure

### Real-Time Monitoring
- Current position Greeks
- P&L tracking
- Limit breach alerts
- Trade exceptions

### End-of-Day
- Complete position reconciliation
- Mark-to-market P&L
- Risk metric snapshots
- Regulatory reporting

## Best Practices

1. **Defense in Depth**: Multiple layers of checks
2. **Real-Time Monitoring**: Continuous risk tracking
3. **Escalation**: Clear alert and escalation procedures
4. **Testing**: Regular stress test execution
5. **Auditability**: Complete audit trail of all checks
6. **Transparency**: Clear reporting to management
7. **Automation**: Reduce manual risk assessment
