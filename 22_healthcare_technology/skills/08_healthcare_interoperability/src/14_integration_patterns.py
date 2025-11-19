#!/usr/bin/env python3
"""Integration Patterns - Common healthcare integration patterns"""

from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)

class RequestResponsePattern:
    """Synchronous request-response pattern"""
    def __init__(self, handler: Callable):
        self.handler = handler

    def process(self, request: Dict) -> Dict:
        """Process synchronously"""
        return self.handler(request)

class EventDrivenPattern:
    """Asynchronous event-driven pattern"""
    def __init__(self):
        self.subscribers = {}

    def publish(self, event_type: str, event_data: Dict):
        """Publish event"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event_data)

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

class TransformationPattern:
    """Data transformation pattern"""
    def __init__(self, transformers: List[Callable]):
        self.transformers = transformers

    def transform(self, data: Dict) -> Dict:
        """Apply transformations"""
        result = data
        for transformer in self.transformers:
            result = transformer(result)
        return result
