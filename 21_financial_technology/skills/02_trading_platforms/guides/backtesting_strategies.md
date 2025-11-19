# Backtesting Strategies Guide

## Backtesting Framework Architecture

```python
class BacktestEngine:
    def __init__(self, strategy, tick_data, start_date, end_date):
        self.strategy = strategy
        self.tick_data = tick_data
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio = Portfolio()
        self.results = BacktestResults()

    def run(self):
        current_date = self.start_date

        while current_date <= self.end_date:
            # Get daily tick data
            daily_ticks = self.tick_data.get_day(current_date)

            # Replay ticks
            for tick in daily_ticks:
                # Update market data
                self.portfolio.update_prices(tick)

                # Get strategy signal
                signal = self.strategy.calculate_signal(
                    self.portfolio,
                    tick
                )

                # Execute if signal
                if signal.should_trade:
                    order = Order(
                        symbol=signal.symbol,
                        side=signal.side,
                        qty=signal.quantity,
                        price=tick.price
                    )
                    self.portfolio.execute_order(order)

            # Daily accounting
            self.portfolio.mark_to_market(daily_ticks[-1].price)
            self.results.record_day(
                current_date,
                self.portfolio.get_daily_pnl(),
                self.portfolio.get_position()
            )

            current_date += timedelta(days=1)

        return self.results
```

## Sample Strategy Implementation

```python
class MomentumStrategy:
    def __init__(self, lookback_period=20, threshold=0.02):
        self.lookback_period = lookback_period
        self.threshold = threshold
        self.price_history = deque(maxlen=lookback_period)

    def calculate_signal(self, portfolio, tick):
        # Record price
        self.price_history.append(tick.price)

        if len(self.price_history) < self.lookback_period:
            return Signal(should_trade=False)

        # Calculate momentum
        prices = list(self.price_history)
        momentum = (prices[-1] - prices[0]) / prices[0]

        # Generate signal
        if momentum > self.threshold:
            # Buy signal
            return Signal(
                should_trade=True,
                symbol=tick.symbol,
                side=BUY,
                quantity=100
            )
        elif momentum < -self.threshold:
            # Sell signal
            return Signal(
                should_trade=True,
                symbol=tick.symbol,
                side=SELL,
                quantity=100
            )

        return Signal(should_trade=False)
```

## Performance Analysis

```python
class BacktestResults:
    def __init__(self):
        self.daily_returns = []
        self.daily_pnl = []
        self.positions = []
        self.trades = []

    def calculate_metrics(self):
        returns = np.array(self.daily_returns)
        pnl = np.array(self.daily_pnl)

        # Sharpe Ratio
        excess_return = np.mean(returns) - 0.02 / 252  # 2% risk-free rate
        daily_volatility = np.std(returns)
        sharpe = excess_return / daily_volatility * np.sqrt(252)

        # Maximum Drawdown
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)

        # Total Return
        total_return = np.prod(1 + returns) - 1

        # Win Rate
        winning_trades = sum(1 for p in pnl if p > 0)
        win_rate = winning_trades / len(pnl) if pnl else 0

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_daily_return': np.mean(returns),
            'daily_volatility': daily_volatility
        }

    def plot_results(self):
        import matplotlib.pyplot as plt

        cumulative_returns = np.cumprod(1 + np.array(self.daily_returns))

        plt.figure(figsize=(12, 6))
        plt.plot(cumulative_returns)
        plt.title('Cumulative Returns')
        plt.xlabel('Days')
        plt.ylabel('Cumulative Return')
        plt.grid(True)
        plt.show()
```

## Walk-Forward Analysis

```python
def walk_forward_analysis(strategy, tick_data, window_size=252,
                          step_size=63):
    """
    Walk-forward testing: optimize on in-sample, test on out-of-sample
    """
    results = []
    dates = sorted(tick_data.get_dates())

    for i in range(0, len(dates) - window_size, step_size):
        # In-sample period (optimization)
        insample_start = dates[i]
        insample_end = dates[i + window_size - step_size]

        # Out-of-sample period (testing)
        outsample_start = dates[i + window_size - step_size]
        outsample_end = dates[i + window_size]

        # Optimize parameters on in-sample
        optimized_params = optimize_strategy(
            strategy,
            tick_data,
            insample_start,
            insample_end
        )

        # Test on out-of-sample
        strategy.set_parameters(optimized_params)
        oos_results = backtest(
            strategy,
            tick_data,
            outsample_start,
            outsample_end
        )

        results.append(oos_results)

    # Aggregate results
    return aggregate_walk_forward_results(results)
```

## Monte Carlo Simulation

```python
def monte_carlo_analysis(returns, num_simulations=10000):
    """
    Simulate trading performance with random returns
    """
    simulations = []

    for _ in range(num_simulations):
        # Resample returns with replacement
        resampled = np.random.choice(returns, size=len(returns), replace=True)
        cumulative = np.cumprod(1 + resampled)
        simulations.append(cumulative)

    simulations = np.array(simulations)

    # Percentile analysis
    percentiles = {
        'p5': np.percentile(simulations, 5, axis=0),
        'p25': np.percentile(simulations, 25, axis=0),
        'p50': np.percentile(simulations, 50, axis=0),
        'p75': np.percentile(simulations, 75, axis=0),
        'p95': np.percentile(simulations, 95, axis=0),
    }

    return {
        'simulations': simulations,
        'percentiles': percentiles,
        'worst_case': np.min(simulations[-1, :]),
        'best_case': np.max(simulations[-1, :])
    }
```

## Slippage Modeling

```python
class SlippageModel:
    def __init__(self, slippage_bps=1):
        self.slippage_bps = slippage_bps

    def apply_slippage(self, execution_price, side):
        """Apply slippage to simulated execution"""
        slippage = execution_price * (self.slippage_bps / 10000)

        if side == BUY:
            return execution_price + slippage
        else:
            return execution_price - slippage

    def apply_market_impact(self, execution_price, qty, market_depth):
        """Apply market impact based on order size"""
        impact_bps = 0.1 * (qty / market_depth)  # Calibrated formula
        impact = execution_price * (impact_bps / 10000)
        return impact
```

## Robustness Testing

```python
def robustness_test(strategy, tick_data, num_randomizations=100):
    """Test strategy robustness by randomizing parameters"""
    results = []

    for _ in range(num_randomizations):
        # Randomize parameters
        params = strategy.randomize_parameters()
        strategy.set_parameters(params)

        # Run backtest
        result = backtest(strategy, tick_data)
        results.append(result)

    # Analyze distribution
    returns = [r.total_return for r in results]
    sharpes = [r.sharpe_ratio for r in results]

    return {
        'mean_return': np.mean(returns),
        'std_return': np.std(returns),
        'mean_sharpe': np.mean(sharpes),
        'std_sharpe': np.std(sharpes),
        'min_sharpe': np.min(sharpes),
        'max_sharpe': np.max(sharpes)
    }
```

## Common Backtesting Pitfalls

### 1. Lookahead Bias
```python
# BAD: Using future data in signal calculation
def bad_signal(tick, all_future_ticks):
    future_high = max(t.price for t in all_future_ticks)  # WRONG!
    return future_high > threshold

# GOOD: Only use past data
def good_signal(tick, historical_prices):
    past_returns = calculate_returns(historical_prices)
    momentum = past_returns[-1]
    return momentum > threshold
```

### 2. Survivorship Bias
```python
# BAD: Only backtest stocks that still exist
# This excludes bankruptcies and delistings
stocks = get_all_stocks_from_yahoo()  # Only living companies

# GOOD: Include delisted and bankrupt companies
stocks = get_all_historical_stocks()  # Including delisted
```

### 3. Overfitting
```python
# BAD: Optimize too many parameters
params = optimize(strategy, data, num_params=50)

# GOOD: Limit parameters and use out-of-sample testing
params = optimize(strategy, data, num_params=3)
oos_results = test(strategy, data_oos)  # Validate on new data
```

## Production Deployment Checklist

- [ ] Historical tick data verified for accuracy
- [ ] Slippage model calibrated to actual execution
- [ ] Walk-forward analysis shows robust out-of-sample performance
- [ ] Monte Carlo analysis shows acceptable drawdown
- [ ] Parameter sensitivity tested
- [ ] Transaction costs included in simulation
- [ ] Survivorship bias addressed
- [ ] Lookahead bias eliminated
- [ ] Live trading in sandbox with real latency
