"""Real-time position tracking system"""
from collections import defaultdict
from typing import Dict, List, Tuple

class PositionTracker:
    def __init__(self):
        self.positions: Dict[str, 'Position'] = {}
        self.trade_history: List['Trade'] = []

    def on_execution(self, trade: 'Trade'):
        """Process executed trade and update positions"""
        symbol = trade.symbol
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)

        pos = self.positions[symbol]

        # Update position with trade
        old_cost = pos.quantity * pos.avg_price
        new_cost = trade.quantity * trade.price
        new_qty = pos.quantity + (trade.quantity if trade.side == 'BUY'
                                 else -trade.quantity)

        if new_qty != 0:
            pos.avg_price = (old_cost + new_cost) / new_qty
        else:
            pos.avg_price = 0

        pos.quantity = new_qty
        pos.last_trade_price = trade.price

        self.trade_history.append(trade)

    def get_position(self, symbol: str) -> 'Position':
        """Get current position for symbol"""
        return self.positions.get(symbol)

    def get_all_positions(self) -> Dict[str, 'Position']:
        """Get all open positions"""
        return {s: p for s, p in self.positions.items() if p.quantity != 0}

    def get_gross_exposure(self) -> float:
        """Calculate total absolute exposure"""
        return sum(abs(p.quantity) for p in self.positions.values())

    def get_net_exposure(self) -> float:
        """Calculate net exposure (long - short)"""
        return sum(p.quantity for p in self.positions.values())

    def rebalance_to_targets(self, target_weights: Dict[str, float],
                            total_capital: float) -> List['Order']:
        """Generate rebalancing orders to target weights"""
        orders = []

        for symbol, target_weight in target_weights.items():
            target_value = total_capital * target_weight
            current_pos = self.positions.get(symbol)
            current_value = current_pos.quantity * current_pos.last_trade_price \
                           if current_pos else 0

            qty_diff = (target_value - current_value) / (current_pos.last_trade_price
                                                        if current_pos else 1)

            if abs(qty_diff) > 100:  # Minimum trade size
                orders.append({
                    'symbol': symbol,
                    'side': 'BUY' if qty_diff > 0 else 'SELL',
                    'quantity': int(abs(qty_diff))
                })

        return orders

class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.avg_price = 0.0
        self.last_trade_price = 0.0

class Trade:
    def __init__(self, symbol: str, side: str, quantity: int, price: float):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price

if __name__ == "__main__":
    tracker = PositionTracker()

    # Simulate trades
    trades = [
        Trade('AAPL', 'BUY', 100, 150.00),
        Trade('MSFT', 'BUY', 50, 300.00),
        Trade('AAPL', 'BUY', 50, 151.00),
    ]

    for trade in trades:
        tracker.on_execution(trade)

    print("Positions:", tracker.get_all_positions())
    print("Gross exposure:", tracker.get_gross_exposure())
    print("Net exposure:", tracker.get_net_exposure())
