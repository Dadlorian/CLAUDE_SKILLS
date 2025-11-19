"""
Production-Ready Webhook Handler
Implements signature verification, retry logic, and event processing

Module: webhook_handler
Requires: flask, pydantic, requests, cryptography
"""

import hashlib
import hmac
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional, Any
from queue import Queue
import threading

from flask import Flask, request, jsonify
from pydantic import BaseModel, Field, validator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """Supported webhook event types"""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    ORDER_PLACED = "order.placed"
    ORDER_SHIPPED = "order.shipped"


class WebhookPayload(BaseModel):
    """Webhook payload schema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WebhookEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    version: str = "1.0"

    @validator('data')
    def validate_data_not_empty(cls, v):
        """Ensure data payload is not empty"""
        if not v:
            raise ValueError("Webhook data cannot be empty")
        return v

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'version': self.version
        }


class SignatureVerifier:
    """
    Verifies webhook signatures using HMAC-SHA256
    Supports multiple signature algorithms
    """

    SUPPORTED_ALGORITHMS = ['sha256', 'sha512']

    def __init__(self, secret: str, algorithm: str = 'sha256'):
        """
        Initialize signature verifier

        Args:
            secret: Webhook secret key
            algorithm: Hashing algorithm to use

        Raises:
            ValueError: If algorithm is not supported
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        self.secret = secret.encode() if isinstance(secret, str) else secret
        self.algorithm = algorithm

    def compute_signature(self, payload: str) -> str:
        """
        Compute HMAC signature for payload

        Args:
            payload: Raw request body or JSON string

        Returns:
            Computed signature (hex format)
        """
        payload_bytes = payload.encode() if isinstance(payload, str) else payload

        if self.algorithm == 'sha256':
            hash_func = hashlib.sha256
        else:
            hash_func = hashlib.sha512

        return hmac.new(
            self.secret,
            payload_bytes,
            hash_func
        ).hexdigest()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature

        Args:
            payload: Raw request body
            signature: Signature from header

        Returns:
            True if signature is valid, False otherwise
        """
        computed = self.compute_signature(payload)
        return hmac.compare_digest(computed, signature)

    def get_header_name(self) -> str:
        """Get expected header name for signature"""
        return f"X-Webhook-Signature-{self.algorithm.upper()}"


class WebhookRetryPolicy:
    """
    Retry policy for failed webhook deliveries
    Implements exponential backoff
    """

    def __init__(
        self,
        max_retries: int = 5,
        initial_delay: int = 60,
        backoff_factor: float = 2.0,
        max_delay: int = 3600
    ):
        """
        Initialize retry policy

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for exponential backoff
            max_delay: Maximum delay between retries in seconds
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

    def get_retry_delay(self, attempt: int) -> int:
        """
        Calculate delay for retry attempt

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = min(
            self.initial_delay * (self.backoff_factor ** attempt),
            self.max_delay
        )
        return int(delay)

    def should_retry(self, attempt: int, status_code: int) -> bool:
        """
        Determine if request should be retried

        Args:
            attempt: Current attempt number
            status_code: HTTP status code from delivery attempt

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        # Retry on 5xx errors or timeout (429)
        return status_code >= 500 or status_code == 429


@dataclass
class WebhookEvent:
    """Internal webhook event representation"""
    id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    delivery_attempts: int = 0
    last_delivery_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None


class WebhookEventQueue:
    """
    Thread-safe queue for webhook events
    Handles event ordering and delivery scheduling
    """

    def __init__(self, max_queue_size: int = 10000):
        """Initialize event queue"""
        self.queue: Queue = Queue(maxsize=max_queue_size)
        self.lock = threading.Lock()

    def enqueue(self, event: WebhookEvent) -> bool:
        """
        Add event to queue

        Args:
            event: Webhook event to queue

        Returns:
            True if successful, False if queue is full
        """
        try:
            self.queue.put_nowait(event)
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue event: {e}")
            return False

    def dequeue(self, timeout: Optional[int] = None) -> Optional[WebhookEvent]:
        """
        Remove event from queue

        Args:
            timeout: Max seconds to wait for event

        Returns:
            Next webhook event or None if queue empty
        """
        try:
            return self.queue.get(timeout=timeout)
        except Exception:
            return None

    def size(self) -> int:
        """Get queue size"""
        return self.queue.qsize()


class WebhookEventHandler(ABC):
    """Abstract base class for webhook event handlers"""

    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can process event type"""
        pass

    @abstractmethod
    async def handle(self, event: WebhookEvent) -> bool:
        """
        Process webhook event

        Args:
            event: Event to handle

        Returns:
            True if successful, False otherwise
        """
        pass


class WebhookProcessor:
    """
    Main webhook processor
    Handles verification, queueing, and delivery
    """

    def __init__(
        self,
        secret: str,
        retry_policy: Optional[WebhookRetryPolicy] = None
    ):
        """
        Initialize webhook processor

        Args:
            secret: Webhook secret for signature verification
            retry_policy: Retry policy for failed deliveries
        """
        self.verifier = SignatureVerifier(secret)
        self.retry_policy = retry_policy or WebhookRetryPolicy()
        self.event_queue = WebhookEventQueue()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.processed_ids: set = set()
        self.lock = threading.Lock()

    def register_handler(
        self,
        event_type: str,
        handler: Callable[[WebhookEvent], bool]
    ) -> None:
        """
        Register event handler

        Args:
            event_type: Type of events to handle
            handler: Callable to process event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type}")

    def verify_request(
        self,
        body: bytes,
        signature_header: Optional[str] = None,
        timestamp_header: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Verify webhook request authenticity

        Args:
            body: Raw request body
            signature_header: Signature from header
            timestamp_header: Timestamp from header

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not signature_header:
            return False, "Missing signature header"

        # Verify timestamp (prevent replay attacks)
        if timestamp_header:
            try:
                timestamp = int(timestamp_header)
                current_time = int(time.time())

                if abs(current_time - timestamp) > 300:  # 5 minute window
                    return False, "Timestamp outside acceptable window"
            except ValueError:
                return False, "Invalid timestamp format"

        # Verify signature
        payload = body.decode() if isinstance(body, bytes) else body

        if not self.verifier.verify_signature(payload, signature_header):
            return False, "Invalid signature"

        return True, None

    def process_payload(self, payload: Dict[str, Any]) -> tuple[bool, str]:
        """
        Process webhook payload

        Args:
            payload: Webhook payload

        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate payload schema
            webhook_payload = WebhookPayload(**payload)

            # Check for duplicate (idempotency)
            with self.lock:
                if webhook_payload.id in self.processed_ids:
                    return True, "Event already processed (idempotent)"

                self.processed_ids.add(webhook_payload.id)

            # Create event
            event = WebhookEvent(
                id=webhook_payload.id,
                event_type=webhook_payload.event_type.value,
                payload=webhook_payload.data,
                timestamp=webhook_payload.timestamp
            )

            # Queue event
            if not self.event_queue.enqueue(event):
                logger.error("Failed to queue event - queue full")
                return False, "Server busy"

            # Process event handlers
            handlers = self.event_handlers.get(webhook_payload.event_type.value, [])

            for handler in handlers:
                try:
                    success = handler(event)
                    if success:
                        logger.info(f"Event {event.id} processed by {handler.__name__}")
                    else:
                        logger.warning(f"Handler {handler.__name__} failed for event {event.id}")
                except Exception as e:
                    logger.error(f"Error in handler {handler.__name__}: {e}")

            return True, "Event received and queued for processing"

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return False, str(e)

    def get_delivery_status(self) -> Dict[str, Any]:
        """Get current delivery queue status"""
        return {
            'queue_size': self.event_queue.size(),
            'processed_events': len(self.processed_ids),
            'registered_handlers': len(self.event_handlers),
            'timestamp': datetime.utcnow().isoformat()
        }


def create_webhook_blueprint(processor: WebhookProcessor) -> any:
    """
    Create Flask blueprint for webhook handling

    Args:
        processor: WebhookProcessor instance

    Returns:
        Flask blueprint
    """
    from flask import Blueprint

    webhook_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

    @webhook_bp.post('/events')
    def handle_webhook():
        """Handle incoming webhook"""
        try:
            # Extract headers
            signature = request.headers.get('X-Webhook-Signature-Sha256')
            timestamp = request.headers.get('X-Webhook-Timestamp')

            # Get raw body
            body = request.get_data()

            # Verify request
            is_valid, error = processor.verify_request(body, signature, timestamp)

            if not is_valid:
                logger.warning(f"Invalid webhook: {error}")
                return jsonify({'error': error}), 401

            # Parse payload
            payload = json.loads(body)

            # Process event
            success, message = processor.process_payload(payload)

            if success:
                return jsonify({
                    'status': 'received',
                    'message': message,
                    'event_id': payload.get('id')
                }), 202

            return jsonify({'error': message}), 400

        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON'}), 400
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @webhook_bp.get('/status')
    def webhook_status():
        """Get webhook processing status"""
        return jsonify(processor.get_delivery_status()), 200

    return webhook_bp


# Example event handlers
def handle_user_created(event: WebhookEvent) -> bool:
    """Example: Handle user.created event"""
    try:
        user_id = event.payload.get('user_id')
        logger.info(f"Processing user creation: {user_id}")
        # Add your business logic here
        return True
    except Exception as e:
        logger.error(f"Error handling user creation: {e}")
        return False


def handle_payment_completed(event: WebhookEvent) -> bool:
    """Example: Handle payment.completed event"""
    try:
        payment_id = event.payload.get('payment_id')
        amount = event.payload.get('amount')
        logger.info(f"Processing payment completion: {payment_id} (${amount})")
        # Add your business logic here
        return True
    except Exception as e:
        logger.error(f"Error handling payment: {e}")
        return False


if __name__ == '__main__':
    # Example usage
    app = Flask(__name__)

    # Initialize processor
    processor = WebhookProcessor(
        secret='your-webhook-secret-key',
        retry_policy=WebhookRetryPolicy(
            max_retries=5,
            initial_delay=60,
            backoff_factor=2.0
        )
    )

    # Register handlers
    processor.register_handler(
        WebhookEventType.USER_CREATED.value,
        handle_user_created
    )
    processor.register_handler(
        WebhookEventType.PAYMENT_COMPLETED.value,
        handle_payment_completed
    )

    # Register blueprint
    app.register_blueprint(create_webhook_blueprint(processor))

    app.run(host='0.0.0.0', port=5000, debug=False)
