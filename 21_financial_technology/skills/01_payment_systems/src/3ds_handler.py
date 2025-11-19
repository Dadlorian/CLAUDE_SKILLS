"""3D Secure authentication handler"""
import logging
import asyncio

class ThreeDSecureHandler:
    def __init__(self, processor_api, auth_service):
        self.processor = processor_api
        self.auth = auth_service
        self.logger = logging.getLogger(__name__)

    async def should_require_3ds(self, transaction, risk_score):
        """Determine if 3DS is needed"""
        if risk_score > 250:
            return True
        if transaction['amount'] > 500:
            return True
        if not transaction.get('customer_id'):
            return True
        if transaction['country'] in ['GB', 'DE', 'FR']:  # EU SCA
            return True
        return False

    async def initiate_3ds(self, transaction):
        """Initiate 3DS authentication"""
        self.logger.info(f"Initiating 3DS for {transaction['id']}")
        
        auth_request = {
            'amount': transaction['amount'],
            'currency': transaction['currency'],
            'card_token': transaction['payment_token']
        }
        
        result = await self.processor.initiate_3ds(auth_request)
        return result

    async def complete_3ds(self, transaction_id, auth_code):
        """Complete 3DS challenge"""
        self.logger.info(f"Completing 3DS for {transaction_id}")
        
        result = await self.processor.complete_3ds(transaction_id, auth_code)
        
        if result['success']:
            return {
                'eci': result['eci'],
                'cavv': result['cavv'],
                'authenticated': True
            }
        else:
            return {'authenticated': False}
