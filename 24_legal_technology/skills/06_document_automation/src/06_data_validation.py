#!/usr/bin/env python3
"""Data Validation for Document Automation"""

import re
from datetime import datetime
from typing import Dict, List

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))

class DocumentDataValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        cleaned = re.sub(r'[^\d]', '', phone)
        return len(cleaned) == 10

    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return bool(re.match(pattern, ssn))

    @staticmethod
    def validate_purchase_agreement(data: Dict) -> List[str]:
        errors = []

        # Required fields
        required_fields = ['buyer_name', 'seller_name', 'purchase_price', 'effective_date']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field missing: {field}")

        # Type validation
        if 'purchase_price' in data:
            try:
                price = float(data['purchase_price'])
                if price <= 0:
                    errors.append("Purchase price must be positive")
            except (ValueError, TypeError):
                errors.append("Purchase price must be a number")

        # Date validation
        if 'effective_date' in data:
            try:
                date = datetime.strptime(data['effective_date'], '%Y-%m-%d')
            except ValueError:
                errors.append("Effective date must be in YYYY-MM-DD format")

        # Business rules
        if data.get('shareholders'):
            total_pct = sum(s.get('percentage', 0) for s in data['shareholders'])
            if abs(total_pct - 100) > 0.01:
                errors.append(f"Shareholder percentages must total 100%, currently {total_pct}%")

        # Conditional validation
        if data.get('include_earnout'):
            if not data.get('earnout_amount') or data.get('earnout_amount') <= 0:
                errors.append("Earnout amount required when earnout is included")

        return errors

if __name__ == '__main__':
    # Test validation
    test_data = {
        'buyer_name': 'Acme Corp',
        'seller_name': 'Smith Industries',
        'purchase_price': 5000000,
        'effective_date': '2025-11-19',
        'shareholders': [
            {'name': 'John', 'percentage': 60},
            {'name': 'Jane', 'percentage': 40}
        ],
        'include_earnout': True,
        'earnout_amount': 1000000
    }

    errors = DocumentDataValidator.validate_purchase_agreement(test_data)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Validation passed!")
