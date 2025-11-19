#!/usr/bin/env python3
"""
GDPR Consent Validator
Validates consent records and ensures compliance with GDPR requirements
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ConsentValidator:
    """Validates consent records for GDPR compliance"""

    def __init__(self):
        self.required_fields = {
            'consent_id',
            'user_id',
            'consent_type',
            'granted',
            'timestamp',
            'ip_address',
            'user_agent',
            'consent_version'
        }
        self.max_consent_duration = timedelta(days=730)  # 24 months

    def validate_consent_record(self, record: Dict) -> Dict[str, any]:
        """
        Validate a consent record for GDPR compliance

        Args:
            record: Consent record dictionary

        Returns:
            Validation result with status and findings
        """
        issues = []

        # Check required fields
        missing_fields = self.required_fields - set(record.keys())
        if missing_fields:
            issues.append(f"Missing required fields: {missing_fields}")

        # Validate timestamp
        try:
            timestamp = datetime.fromisoformat(record.get('timestamp', ''))
            if timestamp > datetime.now():
                issues.append("Timestamp is in the future")
        except ValueError:
            issues.append("Invalid timestamp format (requires ISO 8601)")

        # Validate consent type
        valid_types = ['marketing_email', 'analytics', 'profiling', 'cookies', 'third_party_sharing']
        if record.get('consent_type') not in valid_types:
            issues.append(f"Invalid consent type. Must be one of: {valid_types}")

        # Check for explicit consent
        if record.get('granted') is not True:
            issues.append("Consent must be explicitly granted (true)")

        # Validate consent duration
        if 'consent_duration' in record:
            try:
                duration_days = int(record['consent_duration'])
                if duration_days > 730:
                    issues.append("Consent duration exceeds 24 months (730 days)")
            except ValueError:
                issues.append("Invalid consent duration format")

        # Check for valid proof elements
        if 'verification_code' not in record:
            issues.append("Missing verification code for proof of consent")

        # Check IP address is hashed (GDPR pseudonymization)
        if record.get('ip_address') and not self._is_hashed(record['ip_address']):
            issues.append("IP address should be hashed for privacy")

        # Check user_id is hashed
        if record.get('user_id') and not self._is_hashed(record['user_id']):
            issues.append("User ID should be hashed for privacy")

        return {
            'valid': len(issues) == 0,
            'consent_id': record.get('consent_id'),
            'issues': issues,
            'severity': 'critical' if any('required' in i.lower() or 'explicit' in i.lower() for i in issues) else 'warning',
            'validated_at': datetime.now().isoformat()
        }

    def check_consent_expiration(self, consent_record: Dict) -> Dict[str, any]:
        """Check if consent has expired"""
        timestamp = datetime.fromisoformat(consent_record['timestamp'])
        duration_days = consent_record.get('consent_duration', 730)
        expiration_date = timestamp + timedelta(days=duration_days)

        days_remaining = (expiration_date - datetime.now()).days
        requires_renewal = days_remaining <= 30

        return {
            'consent_id': consent_record.get('consent_id'),
            'granted_date': timestamp.date().isoformat(),
            'expiration_date': expiration_date.date().isoformat(),
            'days_remaining': days_remaining,
            'expired': days_remaining < 0,
            'requires_renewal': requires_renewal,
            'renewal_due_date': (expiration_date - timedelta(days=30)).date().isoformat() if requires_renewal else None
        }

    def validate_consent_batch(self, records: List[Dict]) -> Dict[str, any]:
        """Validate a batch of consent records"""
        results = {
            'total_records': len(records),
            'valid_records': 0,
            'invalid_records': 0,
            'issues_found': [],
            'records_requiring_renewal': 0,
            'validation_summary': []
        }

        for record in records:
            validation = self.validate_consent_record(record)
            expiration_check = self.check_consent_expiration(record)

            if validation['valid']:
                results['valid_records'] += 1
            else:
                results['invalid_records'] += 1
                results['issues_found'].extend(validation['issues'])

            if expiration_check['requires_renewal']:
                results['records_requiring_renewal'] += 1

            results['validation_summary'].append({
                'consent_id': record.get('consent_id'),
                'valid': validation['valid'],
                'requires_renewal': expiration_check['requires_renewal'],
                'issues': validation['issues']
            })

        return results

    @staticmethod
    def _is_hashed(value: str) -> bool:
        """Check if value appears to be hashed (SHA256 = 64 hex chars)"""
        return len(value) == 64 and all(c in '0123456789abcdef' for c in value.lower())

    def generate_consent_verification_code(self, consent_id: str, user_id: str) -> str:
        """Generate a verification code for proof of consent"""
        combined = f"{consent_id}:{user_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


def main():
    validator = ConsentValidator()

    # Example consent records
    test_records = [
        {
            'consent_id': 'cons_001',
            'user_id': hashlib.sha256('user123'.encode()).hexdigest(),
            'consent_type': 'marketing_email',
            'granted': True,
            'timestamp': datetime.now().isoformat(),
            'ip_address': hashlib.sha256('192.168.1.1'.encode()).hexdigest(),
            'user_agent': 'Mozilla/5.0...',
            'consent_version': '2.1',
            'consent_duration': 365,
            'verification_code': 'abc123xyz789'
        }
    ]

    # Validate batch
    results = validator.validate_consent_batch(test_records)
    print(json.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    main()
