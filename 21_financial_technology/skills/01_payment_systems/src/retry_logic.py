"""Exponential backoff retry logic for payment operations"""
import asyncio
import logging
from typing import Callable, Any

class RetryPolicy:
    def __init__(self, max_retries=3, initial_delay=1, max_delay=32):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry"""
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    self.logger.error(f"Max retries reached: {e}")
                    raise
                
                delay = min(self.initial_delay * (2 ** attempt), self.max_delay)
                jitter = delay * 0.1
                self.logger.warning(f"Retry {attempt + 1} in {delay}s: {e}")
                await asyncio.sleep(delay)
