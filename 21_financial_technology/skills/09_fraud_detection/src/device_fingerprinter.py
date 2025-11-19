"""
Device Fingerprinter - Create and track device identities
"""

import hashlib
from typing import Dict


class DeviceFingerprinter:
    """Generate device fingerprints"""

    @staticmethod
    def create_fingerprint(device_data: Dict) -> str:
        """Create device fingerprint"""
        # Combine key attributes
        components = [
            str(device_data.get('user_agent', '')),
            str(device_data.get('screen_width', '')),
            str(device_data.get('screen_height', '')),
            str(device_data.get('timezone', '')),
            str(device_data.get('language', ''))
        ]

        fingerprint_str = '|'.join(components)

        # Hash fingerprint
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    @staticmethod
    def extract_device_characteristics(raw_data: Dict) -> Dict:
        """Extract key device characteristics"""
        return {
            'device_type': raw_data.get('device_type', 'unknown'),
            'os': raw_data.get('os', 'unknown'),
            'browser': raw_data.get('browser', 'unknown'),
            'screen_width': raw_data.get('screen_width', 0),
            'screen_height': raw_data.get('screen_height', 0),
            'timezone': raw_data.get('timezone', 'UTC'),
            'language': raw_data.get('language', 'en')
        }
