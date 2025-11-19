"""Entity Resolution and Deduplication"""
import hashlib
from typing import Dict, List

class EntityResolver:
    """Entity resolution and customer deduplication"""
    
    def resolve_entity(self, name: str, dob: str, country: str) -> dict:
        """Resolve customer identity"""
        entity_hash = hashlib.sha256(f"{name}{dob}{country}".encode()).hexdigest()[:8]
        return {
            'entity_id': f'ENT-{entity_hash}',
            'name': name,
            'dob': dob,
            'country': country,
            'confidence': 0.95
        }
    
    def find_duplicates(self, customers: List[Dict]) -> List[List[str]]:
        """Find potential duplicate customers"""
        entity_map = {}
        duplicates = []
        
        for customer in customers:
            entity_id = self.resolve_entity(customer['name'], customer['dob'], customer['country'])['entity_id']
            if entity_id in entity_map:
                if not any(customer['id'] in group for group in duplicates):
                    duplicates.append([entity_map[entity_id], customer['id']])
            else:
                entity_map[entity_id] = customer['id']
        
        return duplicates
