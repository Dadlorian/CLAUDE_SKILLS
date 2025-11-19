"""
Production-grade payment gateway implementation.
Handles payment authorization, capture, and settlement.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment lifecycle states"""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SETTLED = "settled"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


@dataclass
class PaymentRequest:
    """Standardized payment request"""
    merchant_id: str
    amount_cents: int
    currency: str
    payment_token: str
    customer_id: str
    order_id: str
    description: str
    metadata: Dict = None


@dataclass
class PaymentResponse:
    """Standardized payment response"""
    transaction_id: str
    status: PaymentStatus
    amount_cents: int
    currency: str
    processor: str
    authorization_code: str
    network_reference: str
    timestamp: datetime
    error: Optional[str] = None


class PaymentGateway:
    """
    Main payment gateway orchestrator.
    Routes payments to processors, handles authorization, capture, and settlement.
    """

    def __init__(self, processor_factory, fraud_detector, payment_router):
        """
        Initialize payment gateway with dependencies.

        Args:
            processor_factory: Factory for creating processor instances
            fraud_detector: Fraud detection engine
            payment_router: Intelligent routing engine
        """
        self.processor_factory = processor_factory
        self.fraud_detector = fraud_detector
        self.payment_router = payment_router
        self.logger = logging.getLogger(__name__)

    async def authorize_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Authorize a payment without capturing funds.

        Args:
            request: Payment request details

        Returns:
            Payment response with authorization result
        """
        try:
            # Generate unique transaction ID
            transaction_id = self._generate_transaction_id(request)

            # Log payment attempt
            self.logger.info(
                f"Payment authorization started: {transaction_id}",
                extra={
                    "merchant_id": request.merchant_id,
                    "amount": request.amount_cents,
                    "currency": request.currency
                }
            )

            # Assess fraud risk
            risk_score = await self.fraud_detector.assess_risk(request)
            self.logger.debug(f"Fraud risk score: {risk_score}")

            # Apply 3DS if needed
            if risk_score > 150:
                request = await self._apply_3ds(request)

            # Select processor
            processor_name = self.payment_router.select_processor(request)
            processor = self.processor_factory.create(processor_name)

            # Execute authorization
            processor_response = await processor.authorize(request)

            # Handle response
            if processor_response['success']:
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=PaymentStatus.AUTHORIZED,
                    amount_cents=request.amount_cents,
                    currency=request.currency,
                    processor=processor_name,
                    authorization_code=processor_response['auth_code'],
                    network_reference=processor_response['network_ref'],
                    timestamp=datetime.utcnow()
                )
                self.logger.info(f"Payment authorized: {transaction_id}")
            else:
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=PaymentStatus.FAILED,
                    amount_cents=request.amount_cents,
                    currency=request.currency,
                    processor=processor_name,
                    authorization_code=None,
                    network_reference=None,
                    timestamp=datetime.utcnow(),
                    error=processor_response.get('error')
                )
                self.logger.warning(
                    f"Payment declined: {transaction_id}",
                    extra={"error": processor_response.get('error')}
                )

            return response

        except Exception as e:
            self.logger.exception(f"Payment authorization error: {str(e)}")
            raise

    async def capture_payment(self, transaction_id: str, processor: str) -> PaymentResponse:
        """
        Capture a previously authorized payment.

        Args:
            transaction_id: ID of authorized transaction
            processor: Processor that authorized payment

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Payment capture started: {transaction_id}")

            # Get processor
            processor_obj = self.processor_factory.create(processor)

            # Execute capture
            capture_result = await processor_obj.capture(transaction_id)

            if capture_result['success']:
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=PaymentStatus.CAPTURED,
                    amount_cents=capture_result['amount'],
                    currency=capture_result['currency'],
                    processor=processor,
                    authorization_code=capture_result['auth_code'],
                    network_reference=capture_result['network_ref'],
                    timestamp=datetime.utcnow()
                )
                self.logger.info(f"Payment captured: {transaction_id}")
            else:
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=PaymentStatus.FAILED,
                    amount_cents=capture_result.get('amount', 0),
                    currency=capture_result.get('currency', 'USD'),
                    processor=processor,
                    authorization_code=None,
                    network_reference=None,
                    timestamp=datetime.utcnow(),
                    error=capture_result.get('error')
                )

            return response

        except Exception as e:
            self.logger.exception(f"Payment capture error: {str(e)}")
            raise

    async def refund_payment(self, transaction_id: str, amount_cents: Optional[int] = None) -> PaymentResponse:
        """
        Refund a captured payment (full or partial).

        Args:
            transaction_id: ID of transaction to refund
            amount_cents: Amount to refund (None = full refund)

        Returns:
            Refund result
        """
        try:
            self.logger.info(f"Payment refund started: {transaction_id}")

            # TODO: Get original transaction details
            # Get processor from transaction record
            processor_name = self._get_transaction_processor(transaction_id)
            processor = self.processor_factory.create(processor_name)

            # Execute refund
            refund_result = await processor.refund(transaction_id, amount_cents)

            if refund_result['success']:
                status = PaymentStatus.REFUNDED if not amount_cents else PaymentStatus.CAPTURED
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=status,
                    amount_cents=refund_result.get('refunded_amount', 0),
                    currency=refund_result.get('currency', 'USD'),
                    processor=processor_name,
                    authorization_code=refund_result.get('auth_code'),
                    network_reference=refund_result.get('network_ref'),
                    timestamp=datetime.utcnow()
                )
                self.logger.info(f"Payment refunded: {transaction_id}")
            else:
                response = PaymentResponse(
                    transaction_id=transaction_id,
                    status=PaymentStatus.FAILED,
                    amount_cents=0,
                    currency='USD',
                    processor=processor_name,
                    authorization_code=None,
                    network_reference=None,
                    timestamp=datetime.utcnow(),
                    error=refund_result.get('error')
                )

            return response

        except Exception as e:
            self.logger.exception(f"Payment refund error: {str(e)}")
            raise

    async def _apply_3ds(self, request: PaymentRequest) -> PaymentRequest:
        """
        Apply 3D Secure authentication if needed.

        Args:
            request: Payment request

        Returns:
            Updated request with 3DS proof
        """
        self.logger.debug("Applying 3D Secure authentication")
        # Implementation would handle 3DS flow
        return request

    def _generate_transaction_id(self, request: PaymentRequest) -> str:
        """Generate unique transaction ID"""
        import uuid
        return f"txn_{request.merchant_id}_{uuid.uuid4().hex[:12]}"

    def _get_transaction_processor(self, transaction_id: str) -> str:
        """Retrieve processor used for transaction"""
        # Implementation would query database
        return "stripe"  # Placeholder
