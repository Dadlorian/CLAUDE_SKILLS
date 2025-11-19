"""Stripe payment processor client"""
import stripe
import logging

class StripeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        stripe.api_key = api_key
        self.logger = logging.getLogger(__name__)

    async def authorize(self, request):
        try:
            charge = stripe.Charge.create(
                amount=request.amount_cents,
                currency=request.currency.lower(),
                source=request.payment_token,
                capture=False,
                description=request.description,
                metadata=request.metadata or {}
            )
            return {
                'success': True,
                'auth_code': charge.id,
                'network_ref': charge.balance_transaction
            }
        except stripe.error.CardError as e:
            return {'success': False, 'error': str(e)}

    async def capture(self, transaction_id):
        try:
            charge = stripe.Charge.retrieve(transaction_id)
            charge.capture()
            return {'success': True, 'auth_code': charge.id, 'network_ref': charge.balance_transaction}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def refund(self, transaction_id, amount=None):
        try:
            refund = stripe.Refund.create(charge=transaction_id, amount=amount)
            return {
                'success': True,
                'refunded_amount': refund.amount,
                'auth_code': refund.id,
                'network_ref': refund.balance_transaction
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
