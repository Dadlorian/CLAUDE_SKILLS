"""Event Validation for Streaming Pipeline"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class EventValidator:
    def __init__(self):
        self.required_fields = ['event_id', 'user_id', 'timestamp', 'event_type']
        self.valid_event_types = {'page_view', 'click', 'purchase', 'signup'}
    
    def validate(self, event: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate event and return (is_valid, errors)"""
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate event_id format (UUID)
        if not re.match(r'^[a-f0-9-]{36}$', event['event_id']):
            errors.append("Invalid event_id format")
        
        # Validate user_id
        if not isinstance(event['user_id'], int) or event['user_id'] <= 0:
            errors.append("Invalid user_id")
        
        # Validate timestamp
        try:
            timestamp = event['timestamp']
            if isinstance(timestamp, str):
                datetime.fromisoformat(timestamp)
            elif not isinstance(timestamp, (int, float)):
                errors.append("Invalid timestamp type")
        except ValueError:
            errors.append("Invalid timestamp format")
        
        # Validate event_type
        if event['event_type'] not in self.valid_event_types:
            errors.append(f"Invalid event_type: {event['event_type']}")
        
        # Validate revenue if present
        if 'revenue' in event and event['revenue'] is not None:
            if not isinstance(event['revenue'], (int, float)) or event['revenue'] < 0:
                errors.append("Invalid revenue value")
        
        return len(errors) == 0, errors

# Example usage
if __name__ == "__main__":
    validator = EventValidator()
    
    valid_event = {
        'event_id': '550e8400-e29b-41d4-a716-446655440000',
        'user_id': 12345,
        'timestamp': '2025-01-15T10:30:00Z',
        'event_type': 'purchase',
        'revenue': 99.99
    }
    
    is_valid, errors = validator.validate(valid_event)
    print(f"Valid: {is_valid}, Errors: {errors}")
