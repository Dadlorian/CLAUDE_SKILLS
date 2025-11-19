"""Watchlist and Blacklist Management"""
from datetime import datetime
from typing import Dict

class WatchlistManager:
    """Manage customer watchlists and blacklists"""
    
    def __init__(self):
        self.watchlist = {}
        self.blacklist = set()
    
    def add_to_watchlist(self, customer_id: str, reason: str) -> dict:
        """Add to monitoring watchlist"""
        self.watchlist[customer_id] = {
            'reason': reason,
            'date_added': datetime.utcnow().isoformat(),
            'status': 'ACTIVE'
        }
        return self.watchlist[customer_id]
    
    def add_to_blacklist(self, customer_id: str) -> dict:
        """Add to blacklist (block account)"""
        self.blacklist.add(customer_id)
        return {'customer_id': customer_id, 'status': 'BLACKLISTED'}
    
    def is_blacklisted(self, customer_id: str) -> bool:
        """Check if customer is blacklisted"""
        return customer_id in self.blacklist
    
    def is_on_watchlist(self, customer_id: str) -> bool:
        """Check if customer is on watchlist"""
        return customer_id in self.watchlist
    
    def remove_from_watchlist(self, customer_id: str):
        """Remove from watchlist"""
        if customer_id in self.watchlist:
            del self.watchlist[customer_id]
