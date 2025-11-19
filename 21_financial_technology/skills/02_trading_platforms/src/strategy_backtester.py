"""Strategy backtesting framework"""
import numpy as np
from collections import deque
from dataclasses import dataclass

@dataclass
class Trade:
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: int

class StrategyBacktester:
    def __init__(self, initial_capital=1_000_000):
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_pnl = []

    def run(self, ticks):
        """Run strategy on historical tick data"""
        for tick in ticks:
            signal = self.generate_signal(tick)
            if signal:
                self.execute_trade(signal)

    def generate_signal(self, tick):
        """Generate trading signal based on technical analysis"""
        if not hasattr(self, 'price_history'):
            self.price_history = deque(maxlen=20)

        self.price_history.append(tick['price'])

        if len(self.price_history) < 20:
            return None

        # Simple momentum strategy
        prices = list(self.price_history)
        momentum = (prices[-1] - prices[0]) / prices[0]

        if momentum > 0.02:  # >2% momentum
            return {
                'symbol': tick['symbol'],
                'side': 'BUY',
                'quantity': 100,
                'price': tick['price']
            }
        elif momentum < -0.02:  # <-2% momentum
            return {
                'symbol': tick['symbol'],
                'side': 'SELL',
                'quantity': 100,
                'price': tick['price']
            }

        return None

    def execute_trade(self, signal):
        """Execute trade and track position"""
        symbol = signal['symbol']
        quantity = signal['quantity']
        price = signal['price']

        if symbol not in self.positions:
            self.positions[symbol] = {'quantity': 0, 'avg_price': 0}

        pos = self.positions[symbol]
        old_cost = pos['quantity'] * pos['avg_price']
        new_cost = quantity * price

        if signal['side'] == 'BUY':
            pos['quantity'] += quantity
            pos['avg_price'] = (old_cost + new_cost) / pos['quantity']
        else:
            # Close position
            if pos['quantity'] > 0:
                realized_pnl = (price - pos['avg_price']) * quantity
                self.capital += realized_pnl
                pos['quantity'] -= quantity

        trade = Trade(symbol, signal['side'], quantity, price, 0)
        self.trades.append(trade)

    def get_metrics(self):
        """Calculate performance metrics"""
        trades = np.array([t.price for t in self.trades])
        returns = np.diff(trades) / trades[:-1]

        total_return = (self.capital - 1_000_000) / 1_000_000
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        max_dd = np.min(np.cumprod(1 + returns))

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'num_trades': len(self.trades)
        }

if __name__ == "__main__":
    # Example usage
    tester = StrategyBacktester()

    # Simulate ticks
    ticks = [
        {'symbol': 'AAPL', 'price': 150.0},
        {'symbol': 'AAPL', 'price': 150.5},
        {'symbol': 'AAPL', 'price': 151.0},
        # ... more ticks
    ]

    tester.run(ticks)
    print(tester.get_metrics())
