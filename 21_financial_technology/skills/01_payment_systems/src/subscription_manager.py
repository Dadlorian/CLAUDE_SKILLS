"""Manage recurring subscriptions"""
import logging
from datetime import datetime, timedelta

class SubscriptionManager:
    def __init__(self, db, payment_gateway):
        self.db = db
        self.payment_gateway = payment_gateway
        self.logger = logging.getLogger(__name__)

    async def create_subscription(self, customer_id, plan_id, payment_token):
        """Create recurring subscription"""
        subscription = {
            'customer_id': customer_id,
            'plan_id': plan_id,
            'payment_token': payment_token,
            'status': 'ACTIVE',
            'created_at': datetime.utcnow(),
            'next_billing': datetime.utcnow() + timedelta(days=1)
        }
        
        await self.db.save_subscription(subscription)
        return subscription

    async def process_recurring_charge(self):
        """Process due subscriptions"""
        due = await self.db.get_due_subscriptions()
        
        for sub in due:
            try:
                result = await self.payment_gateway.authorize_payment({
                    'customer_id': sub['customer_id'],
                    'amount': sub['plan']['amount'],
                    'token': sub['payment_token']
                })
                
                if result['success']:
                    await self._extend_subscription(sub)
                else:
                    await self._handle_failed_charge(sub)
            except Exception as e:
                self.logger.error(f"Subscription charge failed: {e}")

    async def cancel_subscription(self, subscription_id):
        """Cancel subscription"""
        await self.db.update_subscription(
            subscription_id,
            {'status': 'CANCELLED', 'cancelled_at': datetime.utcnow()}
        )

    async def _extend_subscription(self, subscription):
        plan = await self.db.get_plan(subscription['plan_id'])
        next_billing = subscription['next_billing'] + timedelta(days=plan['interval_days'])
        
        await self.db.update_subscription(
            subscription['id'],
            {'next_billing': next_billing}
        )

    async def _handle_failed_charge(self, subscription):
        self.logger.warning(f"Failed charge for subscription {subscription['id']}")
        # Trigger dunning process
