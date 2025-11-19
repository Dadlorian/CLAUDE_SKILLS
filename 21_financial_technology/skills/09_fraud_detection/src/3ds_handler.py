"""
3D Secure Handler - Handle 3DS authentication
"""

from typing import Dict, Tuple


class ThreeDSHandler:
    """Handle 3D Secure authentication"""

    def __init__(self, gateway):
        self.gateway = gateway

    def initiate_3ds(self, transaction: Dict) -> Dict:
        """Initiate 3DS authentication"""
        auth_request = {
            'amount': transaction['amount'],
            'cardToken': transaction['card_token'],
            'merchantReference': transaction['order_id']
        }

        response = self.gateway.authenticate_3ds(auth_request)

        if response.get('challengeRequired'):
            return {
                'status': 'challenge_required',
                'challenge_url': response['challenge_url']
            }
        else:
            return {
                'status': 'frictionless',
                'authentication': response['transStatus'],
                'cavv': response.get('cavv')
            }

    def process_authentication_response(self, response: Dict) -> Dict:
        """Process 3DS authentication result"""
        status = response.get('transStatus')

        return {
            'authenticated': status == 'Y',
            'liability_shift': status in ['Y', 'A'],
            'status': status
        }
