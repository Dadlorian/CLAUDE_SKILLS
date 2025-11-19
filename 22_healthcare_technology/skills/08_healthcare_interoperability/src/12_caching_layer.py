#!/usr/bin/env python3
"""Caching Layer - Redis-based caching for healthcare data"""

import json
from typing import Any, Optional
from datetime import timedelta

class CacheLayer:
    """Healthcare data caching"""

    def __init__(self, redis_client):
        self.cache = redis_client
        self.ttl = {
            'patient': 300,
            'observation': 600,
            'terminology': 86400
        }

    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        data = self.cache.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in cache"""
        self.cache.setex(
            key,
            ttl or self.ttl.get('default', 3600),
            json.dumps(value)
        )

    def invalidate(self, key: str):
        """Invalidate cache entry"""
        self.cache.delete(key)

    def get_patient(self, patient_id: str):
        """Get patient from cache"""
        return self.get(f"patient:{patient_id}")

    def set_patient(self, patient_id: str, patient: dict):
        """Cache patient"""
        self.set(f"patient:{patient_id}", patient, self.ttl['patient'])
