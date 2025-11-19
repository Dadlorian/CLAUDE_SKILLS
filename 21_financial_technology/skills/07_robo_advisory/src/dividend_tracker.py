"""Dividend Tracker - Tracks dividend income and reinvestment"""
from typing import List, Dict


class DividendTracker:
    """Tracks dividend income and reinvestment"""

    def __init__(self):
        self.dividends = []

    def record_dividend(self, symbol: str, amount: float, date: str) -> Dict:
        """Record dividend payment"""
        dividend = {
            'symbol': symbol,
            'amount': amount,
            'date': date,
            'reinvested': False
        }
        self.dividends.append(dividend)
        return dividend

    def reinvest_dividend(self, symbol: str, amount: float,
                         reinvestment_price: float) -> Dict:
        """Record dividend reinvestment"""
        shares = amount / reinvestment_price
        return {
            'symbol': symbol,
            'dividend_amount': amount,
            'shares_purchased': shares,
            'cost_basis': amount
        }

    def get_dividend_income(self, period: str = 'annual') -> float:
        """Get total dividend income"""
        return sum(d['amount'] for d in self.dividends)

    def get_dividend_history(self) -> List[Dict]:
        """Get dividend history"""
        return self.dividends
