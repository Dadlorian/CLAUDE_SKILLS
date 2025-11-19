"""Profit and Loss calculation engine"""
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class Position:
    symbol: str
    quantity: int
    avg_entry_price: float
    current_price: float

class PnLCalculator:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = []

    def update_position(self, symbol, quantity, price):
        """Record position update"""
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol, quantity, price, price)
        else:
            pos = self.positions[symbol]
            # Calculate new average entry price
            old_cost = pos.quantity * pos.avg_entry_price
            new_cost = quantity * price
            new_qty = pos.quantity + quantity

            if new_qty != 0:
                pos.avg_entry_price = (old_cost + new_cost) / new_qty
            pos.quantity = new_qty
            pos.current_price = price

    def mark_to_market(self, prices: Dict[str, float]):
        """Update all positions to current market prices"""
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.current_price = prices[symbol]

    def get_unrealized_pnl(self, symbol) -> float:
        """Calculate unrealized P&L for a position"""
        if symbol not in self.positions:
            return 0.0

        pos = self.positions[symbol]
        unrealized = (pos.current_price - pos.avg_entry_price) * pos.quantity
        return unrealized

    def get_total_pnl(self) -> float:
        """Calculate total portfolio P&L"""
        total = sum(self.get_unrealized_pnl(s)
                   for s in self.positions.keys())
        return total

    def get_pnl_by_symbol(self) -> Dict[str, float]:
        """Get P&L breakdown by symbol"""
        return {symbol: self.get_unrealized_pnl(symbol)
                for symbol in self.positions.keys()}

    def calculate_daily_attribution(self, daily_returns: Dict[str, float]
                                   ) -> Dict[str, float]:
        """Attribution analysis of daily P&L"""
        attribution = {}

        for symbol, pos in self.positions.items():
            if symbol in daily_returns:
                contribution = pos.quantity * pos.current_price * \
                              daily_returns[symbol]
                attribution[symbol] = contribution

        return attribution

if __name__ == "__main__":
    calc = PnLCalculator()

    # Add positions
    calc.update_position('AAPL', 1000, 150.00)
    calc.update_position('MSFT', 500, 300.00)

    # Update prices
    calc.mark_to_market({
        'AAPL': 151.00,
        'MSFT': 301.50
    })

    # Calculate
    print("Total P&L:", calc.get_total_pnl())
    print("By symbol:", calc.get_pnl_by_symbol())
