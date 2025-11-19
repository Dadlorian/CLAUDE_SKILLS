# Automated Rebalancing Guide

## Rebalancing Automation Framework

Automated rebalancing is a core feature of robo-advisors, systematically maintaining target allocations while minimizing costs and taxes.

## Automated Rebalancing Triggers

### 1. Calendar-Based Rebalancing

**Implementation**:
```python
def calendar_rebalancing(portfolio, frequency='quarterly'):
    """
    Rebalance at fixed time intervals
    frequency: 'monthly', 'quarterly', 'semi-annual', 'annual'
    """
    if should_rebalance_today(frequency):
        target_allocations = portfolio.get_target_allocations()
        trades = calculate_trades(portfolio, target_allocations)
        execute_trades(trades)
        log_rebalancing_event(portfolio, trades)
```

**Frequency Options**:
- **Monthly**: More active, higher costs (not recommended)
- **Quarterly**: Balanced approach (most common)
- **Semi-Annual**: Less trading, moderate cost
- **Annual**: Minimal intervention (lowest cost)

**Typical Schedule**:
```
Q1 Rebalancing: January 15
Q2 Rebalancing: April 15
Q3 Rebalancing: July 15
Q4 Rebalancing: October 15
```

### 2. Threshold-Based Rebalancing

**Implementation**:
```python
def threshold_rebalancing(portfolio, threshold=0.05):
    """
    Rebalance when any position drifts beyond threshold
    threshold: Maximum acceptable drift (0.05 = 5%)
    """
    current_weights = portfolio.get_current_weights()
    target_weights = portfolio.get_target_weights()
    drift = abs(current_weights - target_weights)

    if max(drift) > threshold:
        trades = calculate_minimum_trades(portfolio, target_weights)
        execute_trades(trades)
        log_rebalancing_event(portfolio, trades)
```

**Threshold Selection**:
```
Conservative Portfolios: 3-5% threshold
Moderate Portfolios: 5-10% threshold
Aggressive Portfolios: 10-15% threshold
```

**Example**:
```
Target Allocation: 60% stocks, 40% bonds
Threshold: 5%
Trigger Bands: 55%-65% stocks, 35%-45% bonds

If allocation drifts to 66% stocks, 34% bonds:
- Stock drift: 6% > 5% threshold
- Rebalance to 60/40
```

### 3. Threshold-Corridor Rebalancing

**Implementation**:
```python
def corridor_rebalancing(portfolio, lower=0.05, upper=0.10):
    """
    Asymmetric bands - rebalance when crossing boundaries
    Only rebalance when weight crosses lower or upper bound
    """
    current_weights = portfolio.get_current_weights()
    target_weights = portfolio.get_target_weights()

    for i, (current, target) in enumerate(zip(current_weights, target_weights)):
        if current < target - lower:
            # Below lower corridor - rebalance back to target
            trades = calculate_trades_for_position(portfolio, i, target)
        elif current > target + upper:
            # Above upper corridor - rebalance back to target
            trades = calculate_trades_for_position(portfolio, i, target)

        if trades:
            execute_trades(trades)
```

**Corridor Examples**:
```
Conservative: 3% lower, 5% upper
Moderate: 5% lower, 10% upper
Aggressive: 7% lower, 15% upper
```

## Trade Calculation and Optimization

### 1. Minimum Variance Trade Sequence

**Objective**: Achieve target allocation with minimum number of trades

**Algorithm**:
```python
def calculate_optimal_trades(current_weights, target_weights):
    """
    Find minimal trade set achieving target allocation
    """
    drift = target_weights - current_weights

    # Identify buy and sell positions
    sell_positions = [i for i, d in enumerate(drift) if d < 0]
    buy_positions = [i for i, d in enumerate(drift) if d > 0]

    trades = []

    # Match sells to buys (minimizing trades)
    for sell_idx in sell_positions:
        sell_amount = abs(drift[sell_idx])

        for buy_idx in buy_positions:
            if drift[buy_idx] > 0:
                transfer_amount = min(sell_amount, drift[buy_idx])
                trades.append({
                    'from': sell_idx,
                    'to': buy_idx,
                    'amount': transfer_amount
                })
                drift[buy_idx] -= transfer_amount
                sell_amount -= transfer_amount

    return trades
```

### 2. Tax-Aware Trade Optimization

**Tax-Loss Harvesting Integration**:
```python
def tax_aware_trades(portfolio, target_weights, tax_rate=0.20):
    """
    Optimize trades for both drift correction and tax efficiency
    """
    base_trades = calculate_optimal_trades(
        portfolio.current_weights,
        target_weights
    )

    # Identify harvestable losses
    harvestable = identify_harvestable_positions(portfolio, tax_rate)

    # Modify trades to harvest losses when possible
    optimized_trades = []
    for trade in base_trades:
        if trade['from'] in harvestable:
            # Sell at loss (harvest tax benefit)
            optimized_trades.append({
                'sell': trade['from'],
                'buy_replacement': find_replacement_security(trade['from']),
                'amount': trade['amount']
            })
        else:
            optimized_trades.append(trade)

    return optimized_trades
```

### 3. Cost Minimization

**Factors**:
- Bid-ask spreads (trading costs)
- Commission fees (if applicable)
- Market impact (large trades)
- Transaction timing

**Algorithm**:
```python
def minimize_trading_costs(trades, market_conditions):
    """
    Optimize execution for lowest trading costs
    """
    # Batch trades by asset class
    batched_trades = group_by_asset_class(trades)

    # Execute most liquid first
    sorted_trades = sort_by_liquidity(batched_trades)

    # Time execution for optimal spreads
    execution_times = optimize_execution_timing(sorted_trades)

    return {
        'trades': sorted_trades,
        'execution_times': execution_times,
        'estimated_cost': calculate_total_cost(sorted_trades)
    }
```

## Rebalancing Execution

### 1. Order Generation

**Order Types**:
- **Market Orders**: Immediate execution, known price
- **Limit Orders**: Specific price, may not execute
- **Algorithmic Orders**: Smart execution algorithms
- **Batch Orders**: Multiple securities in single submission

**Example Order Generation**:
```python
def generate_rebalancing_orders(trades, order_type='market'):
    """
    Convert drift-correction trades into executable orders
    """
    orders = []

    for trade in trades:
        if trade['type'] == 'sell':
            orders.append({
                'security': trade['security'],
                'quantity': calculate_shares(trade['amount']),
                'side': 'SELL',
                'order_type': order_type,
                'time_in_force': 'GTC'  # Good till cancelled
            })
        elif trade['type'] == 'buy':
            orders.append({
                'security': trade['security'],
                'amount_usd': trade['amount'],
                'side': 'BUY',
                'order_type': order_type,
                'time_in_force': 'GTC'
            })

    return orders
```

### 2. Settlement and Confirmation

**Post-Trade Process**:
```
1. Order Submission (T)
2. Custodian Execution (T same day)
3. Trade Confirmation (T same day)
4. Settlement (T+1 for stocks, T+2 for bonds)
5. Rebalancing Completion (When all settled)
6. Compliance Logging
```

**Settlement Handling**:
```python
def monitor_settlement(order_id):
    """
    Track settlement progress and handle exceptions
    """
    while True:
        status = custodian_api.get_order_status(order_id)

        if status == 'EXECUTED':
            track_settlement()
        elif status == 'PARTIALLY_FILLED':
            # Handle partial fills
            remaining = status.remaining_quantity
            retry_order = create_order(remaining, 'REMAINING')
        elif status == 'FAILED':
            # Handle failed orders
            send_alert('Order Failed')
            log_exception(order_id)
        elif status == 'SETTLED':
            # Complete
            update_portfolio_positions()
            break
```

## Rebalancing Reporting and Compliance

### 1. Rebalancing Reports

**Required Information**:
```
Rebalancing Report Format:

Date: July 15, 2024
Account: User-123456
Previous Allocation (by %, $):
- VOO: 45%, $45,000
- VEA: 20%, $20,000
- BND: 30%, $30,000
- VNQ: 5%, $5,000

Target Allocation (by %, $):
- VOO: 45%, $45,000
- VEA: 20%, $20,000
- BND: 33%, $33,000
- VNQ: 2%, $2,000

Trades Executed:
- Sell VNQ: 1,234 shares @ $15.23 = $3,000
- Buy BND: 25 shares @ $80.15 = $3,000

Tax Impact:
- Realized Gains: $0
- Realized Losses: $150 (tax benefit: $37.50)
- Wash-Sale Violations: None

Post-Rebalancing Allocation:
- VOO: 45%, $45,000
- VEA: 20%, $20,000
- BND: 33%, $33,000
- VNQ: 2%, $2,000
```

### 2. Compliance Tracking

**Documentation Requirements**:
```python
def log_rebalancing_event(portfolio, trades, results):
    """
    Document rebalancing for regulatory compliance
    """
    compliance_record = {
        'date': datetime.now(),
        'account_id': portfolio.account_id,
        'triggered_by': 'SCHEDULED' or 'THRESHOLD',
        'drift_metrics': portfolio.calculate_drift(),
        'trades': trades,
        'execution_results': results,
        'tax_impact': calculate_tax_impact(trades),
        'communications': [
            'client_notification_sent',
            'trade_confirmation_received',
            'settlement_confirmed'
        ],
        'approvals': [
            'compliance_check_passed',
            'suitability_maintained'
        ]
    }

    # Store in compliance system
    store_compliance_record(compliance_record)

    # Generate audit trail
    generate_audit_trail(compliance_record)
```

## Advanced Rebalancing Features

### 1. Opportunistic Rebalancing

**Combining with Other Actions**:
```python
def opportunistic_rebalancing(portfolio, new_funds=None, withdrawal=None):
    """
    Use deposits/withdrawals for rebalancing
    """
    if new_funds:
        # Allocate new funds to underweight positions
        allocations = allocate_to_underweight(
            portfolio,
            new_funds,
            portfolio.target_weights
        )
        return allocations

    elif withdrawal:
        # Withdraw from overweight positions
        positions_to_liquidate = identify_overweight(
            portfolio,
            portfolio.target_weights
        )
        return liquidate_positions(positions_to_liquidate, withdrawal)
```

### 2. Dividend Reinvestment Rebalancing

**Algorithm**:
```python
def reinvest_dividends_with_rebalancing(portfolio, dividends):
    """
    Use dividend income to achieve rebalancing
    """
    # Identify underweight positions
    underweight_positions = [
        (i, target - current)
        for i, (current, target) in enumerate(
            zip(portfolio.current_weights, portfolio.target_weights)
        )
        if target > current
    ]

    # Allocate dividends to underweight positions
    remaining_dividends = dividends
    allocations = []

    for position, underweight_amount in underweight_positions:
        allocation = min(remaining_dividends, underweight_amount)
        allocations.append((position, allocation))
        remaining_dividends -= allocation

    # Reinvest in market order
    for position, amount in allocations:
        execute_buy_order(position, amount)
```

### 3. Smart Batching

**Grouping Strategies**:
```python
def smart_batch_rebalancing(accounts, batch_size=100):
    """
    Group accounts for batch rebalancing to reduce costs
    """
    # Batch similar-sized accounts together
    batches = []
    for i in range(0, len(accounts), batch_size):
        batch = accounts[i:i+batch_size]

        # Aggregate buy/sell orders
        aggregated_orders = aggregate_orders(batch)

        # Negotiate better rates for bulk orders
        execute_batch_trades(aggregated_orders)

        batches.append(batch)

    return batches
```

## Rebalancing Performance Monitoring

### 1. Cost Analysis

**Metrics**:
```
1. Total Trading Costs
   - Bid-ask spreads: Total spread × amount
   - Commissions: If applicable
   - Market impact: Estimated from execution prices

2. Rebalancing Frequency
   - Number of rebalancing events per period
   - Average cost per rebalancing

3. Drift Management
   - Average drift before rebalancing
   - Drift reduction from rebalancing
```

### 2. Tax Impact Measurement

**Tracking**:
```
1. Realized Gains/Losses
   - Short-term capital gains
   - Long-term capital gains
   - Harvested losses

2. Tax Efficiency Ratio
   - Tax drag / Total return
   - Lower ratio = more tax-efficient
   - Target: <0.5% annual tax drag

3. After-Tax Performance
   - Returns after all taxes
   - Comparison to pre-tax performance
```

## Best Practices

1. **Frequency Selection**: Match to account size and volatility
2. **Threshold Calibration**: Avoid excessive trading and drift
3. **Tax Awareness**: Integrate tax-loss harvesting
4. **Cost Control**: Monitor trading costs and spreads
5. **Automation**: Systematic, emotion-free execution
6. **Documentation**: Complete compliance records
7. **Communication**: Client notification of rebalancing
8. **Monitoring**: Track effectiveness and adjust
9. **Testing**: Backtest algorithms before implementation
10. **Flexibility**: Adapt to changing conditions

## Rebalancing Algorithm Pseudocode

```python
class RebalancingEngine:
    def __init__(self, rebalancing_config):
        self.config = rebalancing_config
        self.last_rebalance = None

    def check_and_rebalance(self, portfolio):
        """Main rebalancing decision logic"""
        if self.should_rebalance(portfolio):
            trades = self.calculate_trades(portfolio)

            if trades:
                self.execute_trades(trades)
                self.log_rebalancing(portfolio, trades)
                self.notify_client(portfolio, trades)

    def should_rebalance(self, portfolio):
        """Determine if rebalancing is needed"""
        if self.config['method'] == 'CALENDAR':
            return self.is_scheduled_rebalance()
        elif self.config['method'] == 'THRESHOLD':
            return self.exceeds_threshold(portfolio)
        elif self.config['method'] == 'HYBRID':
            return (self.is_scheduled_rebalance() or
                    self.exceeds_threshold(portfolio))

    def calculate_trades(self, portfolio):
        """Generate optimal trades"""
        target_weights = portfolio.target_weights
        current_weights = portfolio.current_weights

        # Use tax-aware optimization
        trades = self.tax_aware_optimization(
            current_weights,
            target_weights
        )

        # Minimize costs
        optimized_trades = self.cost_minimize(trades)

        return optimized_trades

    def execute_trades(self, trades):
        """Execute trades with proper error handling"""
        execution_results = []

        for trade in trades:
            try:
                result = self.custodian.execute_order(trade)
                execution_results.append(result)
            except Exception as e:
                self.log_error(trade, e)
                self.send_alert(f"Trade execution error: {e}")

        return execution_results

# Usage
engine = RebalancingEngine({
    'method': 'THRESHOLD',
    'threshold': 0.05,
    'tax_aware': True,
    'cost_optimization': True
})

engine.check_and_rebalance(portfolio)
```

## Conclusion

Automated rebalancing is essential for robo-advisors, maintaining target allocations while minimizing costs and taxes through systematic, algorithm-driven processes. Proper implementation requires balancing frequency, costs, taxes, and operational complexity.
