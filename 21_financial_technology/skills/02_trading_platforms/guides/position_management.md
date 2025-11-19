# Position Management Guide

## Position Tracking

```python
class PositionTracker:
    def __init__(self):
        self.positions = {}  # symbol -> Position

    def on_execution(self, trade):
        """Update position after trade execution"""

        symbol = trade.symbol
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)

        pos = self.positions[symbol]

        # Calculate new average entry price
        old_cost = pos.quantity * pos.avg_entry_price
        new_cost = trade.quantity * trade.price
        total_cost = old_cost + new_cost
        new_quantity = pos.quantity + trade.quantity

        if new_quantity != 0:
            pos.avg_entry_price = total_cost / new_quantity

        pos.quantity = new_quantity
        pos.last_trade_price = trade.price
        pos.last_update_time = trade.timestamp

        return pos

    def get_position_pnl(self, symbol, current_price):
        """Calculate unrealized P&L for position"""

        if symbol not in self.positions:
            return 0

        pos = self.positions[symbol]
        unrealized_pnl = (current_price - pos.avg_entry_price) * pos.quantity

        return unrealized_pnl

    def rebalance_positions(self, target_weights):
        """Rebalance portfolio to target weights"""

        trades_needed = []

        for symbol, target_weight in target_weights.items():
            current_value = self.positions[symbol].quantity * \
                          self.market_data.get_price(symbol)

            target_value = self.portfolio_value * target_weight

            qty_diff = (target_value - current_value) / \
                      self.market_data.get_price(symbol)

            if abs(qty_diff) > 100:  # Minimum trade size
                trades_needed.append({
                    'symbol': symbol,
                    'quantity': int(qty_diff)
                })

        return trades_needed
```
