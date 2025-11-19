"""
Velocity Checker - Monitor transaction frequency and amounts
"""

import redis
from typing import Dict, Tuple


class VelocityChecker:
    """Check transaction velocity"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def check_velocity(self, customer_id: str, amount: float) -> Tuple[bool, str]:
        """Check if transaction exceeds velocity limits"""
        # Check hourly count
        hourly_count = self._increment_hourly_count(customer_id)
        if hourly_count > 20:
            return False, 'hourly_count_exceeded'

        # Check daily amount
        daily_amount = self._add_daily_amount(customer_id, amount)
        if daily_amount > 10000:
            return False, 'daily_amount_exceeded'

        return True, 'ok'

    def _increment_hourly_count(self, customer_id: str) -> int:
        """Get hourly transaction count"""
        key = f'velocity_hourly:{customer_id}'
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)
        return count

    def _add_daily_amount(self, customer_id: str, amount: float) -> float:
        """Get daily transaction amount"""
        key = f'velocity_daily:{customer_id}'
        total = float(self.redis.get(key) or 0)
        new_total = total + amount
        self.redis.set(key, new_total)
        self.redis.expire(key, 86400)
        return new_total
