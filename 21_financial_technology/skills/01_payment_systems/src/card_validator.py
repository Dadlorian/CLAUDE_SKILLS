"""Payment card validation"""
import logging
import re

class CardValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_card(self, card_data):
        """Validate card data"""
        errors = []
        
        # Number validation (Luhn)
        if not self._validate_luhn(card_data['number']):
            errors.append('Invalid card number')
        
        # Expiry validation
        if not self._validate_expiry(card_data['exp_month'], card_data['exp_year']):
            errors.append('Card expired')
        
        # CVV validation
        if not self._validate_cvv(card_data.get('cvv', '')):
            errors.append('Invalid CVV')
        
        return {'valid': len(errors) == 0, 'errors': errors}

    def _validate_luhn(self, number):
        """Luhn algorithm validation"""
        digits = [int(d) for d in number if d.isdigit()]
        checksum = sum(digits[-1::-2]) + sum(sum(divmod(d*2, 10)) for d in digits[-2::-2])
        return checksum % 10 == 0

    def _validate_expiry(self, month, year):
        """Validate expiry date"""
        from datetime import datetime
        now = datetime.utcnow()
        
        try:
            exp_date = datetime(int(year), int(month), 1)
            return exp_date > now
        except ValueError:
            return False

    def _validate_cvv(self, cvv):
        """Validate CVV format"""
        return bool(re.match(r'^\d{3,4}$', str(cvv)))

    def detect_card_brand(self, number):
        """Detect card brand from number"""
        if number.startswith('4'):
            return 'visa'
        elif number.startswith('5'):
            return 'mastercard'
        elif number.startswith('3'):
            return 'amex'
        else:
            return 'unknown'
