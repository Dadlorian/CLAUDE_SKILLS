"""Token bucket rate limiting"""
import asyncio
from datetime import datetime
import logging

class RateLimiter:
    def __init__(self, requests_per_second=100, burst_size=None):
        self.rate = requests_per_second
        self.burst_size = burst_size or requests_per_second
        self.tokens = self.burst_size
        self.last_refill = datetime.utcnow()
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def acquire(self):
        """Acquire token or wait"""
        async with self.lock:
            await self._refill()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            # Wait for token
            wait_time = 1.0 / self.rate
            self.logger.debug(f"Rate limited, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
            self.tokens -= 1

    async def _refill(self):
        now = datetime.utcnow()
        elapsed = (now - self.last_refill).total_seconds()
        refill = elapsed * self.rate
        self.tokens = min(self.burst_size, self.tokens + refill)
        self.last_refill = now
