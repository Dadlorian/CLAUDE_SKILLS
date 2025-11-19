# Trading Analytics and Reporting Guide

## P&L Analysis

```python
class PnLAnalytics:
    def calculate_daily_pnl(self, date):
        """Calculate daily profit and loss"""

        positions = self.get_positions_at_date(date)
        pnl = {'realized': 0, 'unrealized': 0, 'total': 0}

        for position in positions:
            # Realized P&L from closed trades
            realized_trades = self.get_closed_trades(position.security, date)
            for trade in realized_trades:
                pnl['realized'] += (trade.exit_price - trade.entry_price) * \
                                  trade.quantity

            # Unrealized P&L from open positions
            current_price = self.get_market_price(position.security, date)
            entry_price = position.avg_entry_price
            pnl['unrealized'] += (current_price - entry_price) * \
                                position.quantity

        pnl['total'] = pnl['realized'] + pnl['unrealized']
        return pnl

    def attribution_analysis(self, portfolio, date):
        """Break down returns by source"""

        return {
            'market_exposure_contribution': self.calc_market_exposure(portfolio),
            'selection_contribution': self.calc_stock_selection(portfolio),
            'sector_contribution': self.calc_sector_performance(portfolio),
            'fx_contribution': self.calc_fx_impact(portfolio),
            'total_return': portfolio.daily_return
        }
```

## Risk Metrics

```python
def calculate_risk_metrics(returns):
    """Calculate VaR, Sharpe, max drawdown"""
    
    # Value at Risk (95% confidence)
    var_95 = np.percentile(returns, 5)

    # Sharpe Ratio
    excess_return = np.mean(returns) - 0.02/252
    sharpe = excess_return / np.std(returns) * np.sqrt(252)

    # Maximum Drawdown
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    max_dd = np.min(cumulative / running_max - 1)

    return {
        'var_95': var_95,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd
    }
```
