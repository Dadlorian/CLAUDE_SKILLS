"""Idempotency support for payment operations"""
import hashlib
import logging
from datetime import datetime, timedelta

class IdempotencyManager:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.ttl_hours = 24

    async def execute_idempotent(self, idempotency_key, operation, *args, **kwargs):
        """Execute operation with idempotency"""
        # Check cache
        existing = await self._get_cached(idempotency_key)
        if existing:
            self.logger.info(f"Returning cached result for {idempotency_key}")
            return existing['result']

        try:
            # Execute operation
            result = await operation(*args, **kwargs)

            # Cache result
            await self._cache_result(idempotency_key, result)

            return result
        except Exception as e:
            self.logger.error(f"Idempotent operation failed: {e}")
            raise

    async def _get_cached(self, key):
        cached = await self.db.get(f"idempotent:{key}")
        if cached:
            if (datetime.utcnow() - cached['created_at']).total_seconds() < self.ttl_hours * 3600:
                return cached
        return None

    async def _cache_result(self, key, result):
        await self.db.set(f"idempotent:{key}", {
            'result': result,
            'created_at': datetime.utcnow()
        }, ex=self.ttl_hours*3600)
