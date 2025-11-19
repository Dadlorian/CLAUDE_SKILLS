"""Webhook handler for payment processor notifications"""
import hmac
import hashlib
import logging
import json
from datetime import datetime

class WebhookHandler:
    def __init__(self, webhook_secrets, db):
        self.webhook_secrets = webhook_secrets
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def handle_webhook(self, body, headers, processor):
        """Process incoming webhook"""
        # Verify signature
        if not self._verify_signature(body, headers, processor):
            self.logger.warning(f"Invalid webhook signature from {processor}")
            return False

        # Parse payload
        payload = json.loads(body)

        # Process by event type
        event_type = payload.get('type')
        
        if event_type == 'payment.authorized':
            await self._handle_authorization(payload)
        elif event_type == 'payment.captured':
            await self._handle_capture(payload)
        elif event_type == 'payment.failed':
            await self._handle_failure(payload)
        elif event_type == 'chargeback.initiated':
            await self._handle_chargeback(payload)

        return True

    def _verify_signature(self, body, headers, processor):
        """Verify webhook signature"""
        signature = headers.get('X-Signature', '')
        secret = self.webhook_secrets.get(processor)
        
        expected = hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)

    async def _handle_authorization(self, payload):
        self.logger.info(f"Handling authorization: {payload['transaction_id']}")

    async def _handle_capture(self, payload):
        self.logger.info(f"Handling capture: {payload['transaction_id']}")

    async def _handle_failure(self, payload):
        self.logger.warning(f"Payment failed: {payload['transaction_id']}")

    async def _handle_chargeback(self, payload):
        self.logger.critical(f"Chargeback: {payload['transaction_id']}")
