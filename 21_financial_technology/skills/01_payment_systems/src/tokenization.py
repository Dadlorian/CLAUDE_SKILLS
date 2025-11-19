"""Payment card tokenization"""
import logging
from cryptography.fernet import Fernet

class TokenizationEngine:
    def __init__(self, processor_api):
        self.processor = processor_api
        self.logger = logging.getLogger(__name__)

    async def tokenize_card(self, card_data):
        """Securely tokenize card data"""
        try:
            # Validate card
            if not self._validate_card(card_data):
                return {'error': 'Invalid card format'}

            # Send to processor for tokenization
            result = await self.processor.create_token(card_data)
            return {
                'token': result['token'],
                'last_four': card_data['number'][-4:],
                'brand': self._detect_brand(card_data['number'])
            }
        except Exception as e:
            self.logger.error(f"Tokenization failed: {e}")
            return {'error': 'Tokenization failed'}

    def _validate_card(self, card_data):
        # Luhn check
        number = card_data['number'].replace(' ', '')
        digits = [int(d) for d in number]
        checksum = sum(digits[-1::-2]) + sum(sum(divmod(d*2, 10)) for d in digits[-2::-2])
        return checksum % 10 == 0

    def _detect_brand(self, card_number):
        if card_number.startswith('4'):
            return 'visa'
        elif card_number.startswith('5'):
            return 'mastercard'
        elif card_number.startswith('3'):
            return 'amex'
        else:
            return 'other'
