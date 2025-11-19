#!/usr/bin/env python3
"""Version Tracking for Generated Documents"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

class DocumentVersionTracker:
    def __init__(self, db_file='document_versions.json'):
        self.db_file = db_file
        self.versions = self.load_db()

    def load_db(self):
        if Path(self.db_file).exists():
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}

    def save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.versions, f, indent=2)

    def calculate_hash(self, file_path):
        """Calculate file hash for change detection"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_version(self, file_path, template_id, user_id, input_data):
        """Register a new document version"""
        file_hash = self.calculate_hash(file_path)

        version_info = {
            'file_path': str(file_path),
            'template_id': template_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'file_hash': file_hash,
            'input_hash': hashlib.sha256(
                json.dumps(input_data, sort_keys=True).encode()
            ).hexdigest()
        }

        # Generate version ID
        version_id = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.versions[version_id] = version_info
        self.save_db()

        print(f'Registered version: {version_id}')
        return version_id

    def get_version_history(self, template_id):
        """Get all versions of a template"""
        return {
            vid: info for vid, info in self.versions.items()
            if info['template_id'] == template_id
        }

    def compare_versions(self, version_id1, version_id2):
        """Compare two versions"""
        v1 = self.versions.get(version_id1)
        v2 = self.versions.get(version_id2)

        if not v1 or not v2:
            return None

        return {
            'same_template': v1['template_id'] == v2['template_id'],
            'same_file': v1['file_hash'] == v2['file_hash'],
            'same_input': v1['input_hash'] == v2['input_hash'],
            'time_diff': (
                datetime.fromisoformat(v2['timestamp']) -
                datetime.fromisoformat(v1['timestamp'])
            ).total_seconds()
        }

if __name__ == '__main__':
    tracker = DocumentVersionTracker()

    # Example usage
    tracker.register_version(
        file_path='agreement.pdf',
        template_id='stock_purchase_agreement',
        user_id='user123',
        input_data={'buyer': 'Acme', 'price': 5000000}
    )

    history = tracker.get_version_history('stock_purchase_agreement')
    print(f"Found {len(history)} versions")
