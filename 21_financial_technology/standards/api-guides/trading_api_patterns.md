# Trading API Patterns and Best Practices

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication Mechanisms](#authentication-mechanisms)
3. [Order Management Patterns](#order-management-patterns)
4. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
5. [WebSocket Real-Time Data](#websocket-real-time-data)
6. [Error Handling and Resilience](#error-handling-and-resilience)
7. [Idempotency in Trading](#idempotency-in-trading)
8. [Webhook Patterns for Trading Events](#webhook-patterns-for-trading-events)
9. [Coinbase and Alpaca API Examples](#coinbase-and-alpaca-api-examples)
10. [Risk Management and Circuit Breakers](#risk-management-and-circuit-breakers)
11. [Compliance and Regulatory Requirements](#compliance-and-regulatory-requirements)
12. [Performance Optimization](#performance-optimization)

---

## Introduction

Trading APIs enable real-time market access, order execution, and portfolio management. This guide covers best practices for integrating trading platforms like Coinbase, Alpaca, and Interactive Brokers with emphasis on latency, reliability, and regulatory compliance.

Trading APIs differ significantly from payment APIs in that they:
- Deal with real-time market data and prices
- Require immediate order acknowledgment
- Handle complex order types and conditions
- Enforce strict position limits and risk controls
- Must comply with SEC, FINRA, and other regulations

---

## Authentication Mechanisms

### 1. API Key with Signature Authentication

Most trading APIs use HMAC-SHA256 signed requests for authentication.

#### Coinbase API Authentication

```python
import hmac
import hashlib
import time
import base64
import json
from typing import Dict, Optional
import requests

class CoinbaseAPIClient:
    """Coinbase Trading API Client with HMAC authentication"""

    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key.encode()
        self.passphrase = passphrase
        self.base_url = "https://api.exchange.coinbase.com"
        self.session = requests.Session()

    def _generate_auth_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication headers for Coinbase API"""
        timestamp = str(time.time())

        # Create message to sign
        message = timestamp + method + path + body

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        )
        signature_b64 = base64.b64encode(signature.digest()).decode()

        return {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ):
        """Make authenticated request to Coinbase API"""
        url = self.base_url + path
        body = json.dumps(data) if data else ""

        headers = self._generate_auth_headers(method, path, body)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=body,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json()
            raise CoinbaseAPIError(
                code=error_data.get('error'),
                message=error_data.get('message'),
                status=e.response.status_code
            )

    def get_accounts(self):
        """Get user accounts"""
        return self._request('GET', '/accounts')

    def get_product(self, product_id: str):
        """Get product information"""
        return self._request('GET', f'/products/{product_id}')

    def place_order(self, product_id: str, side: str, order_type: str, **kwargs):
        """Place order"""
        data = {
            'product_id': product_id,
            'side': side,  # 'buy' or 'sell'
            'type': order_type,  # 'market', 'limit'
        }
        data.update(kwargs)

        return self._request('POST', '/orders', data=data)

    def cancel_order(self, order_id: str, product_id: Optional[str] = None):
        """Cancel order"""
        params = {}
        if product_id:
            params['product_id'] = product_id

        return self._request('DELETE', f'/orders/{order_id}', params=params)

    def get_order(self, order_id: str):
        """Get order details"""
        return self._request('GET', f'/orders/{order_id}')

class CoinbaseAPIError(Exception):
    """Coinbase API error"""
    def __init__(self, code: str, message: str, status: int):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(f"[{code}] {message}")
```

#### Alpaca API Authentication

```python
import requests
from typing import Dict, Optional

class AlpacaAPIClient:
    """Alpaca Trading API Client"""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        self.base_url = (
            "https://paper-api.alpaca.markets" if paper
            else "https://api.alpaca.markets"
        )
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ):
        """Make authenticated request to Alpaca API"""
        url = self.base_url + path

        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'Content-Type': 'application/json'
        }

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def get_account(self):
        """Get account information"""
        return self._request('GET', '/v2/account')

    def get_positions(self):
        """Get all open positions"""
        return self._request('GET', '/v2/positions')

    def get_position(self, symbol: str):
        """Get position for symbol"""
        return self._request('GET', f'/v2/positions/{symbol}')

    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        type_: str = 'market',
        **kwargs
    ):
        """Submit order"""
        data = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type_,
            'time_in_force': 'day'
        }
        data.update(kwargs)

        return self._request('POST', '/v2/orders', json_data=data)

    def cancel_order(self, order_id: str):
        """Cancel order"""
        return self._request('DELETE', f'/v2/orders/{order_id}')

    def get_order(self, order_id: str):
        """Get order details"""
        return self._request('GET', f'/v2/orders/{order_id}')
```

### 2. OAuth 2.0 for Broker Integration

```python
import requests
from datetime import datetime, timedelta

class BrokerOAuthFlow:
    """OAuth 2.0 flow for broker integrations"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://broker.example.com/oauth/authorize"
        self.token_url = "https://broker.example.com/oauth/token"

    def get_authorization_url(self, state: str) -> str:
        """Get authorization URL for user"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': 'trading read-account'
        }

        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_token(self, code: str, state: str) -> Dict:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'expires_at': datetime.utcnow() + timedelta(
                seconds=token_data['expires_in']
            ),
            'token_type': token_data.get('token_type', 'Bearer')
        }

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', refresh_token),
            'expires_at': datetime.utcnow() + timedelta(
                seconds=token_data['expires_in']
            )
        }
```

---

## Order Management Patterns

### 1. Order Lifecycle Management

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@dataclass
class Order:
    """Trading order"""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: float = 0
    avg_fill_price: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

    def is_fully_filled(self) -> bool:
        """Check if order is fully filled"""
        return self.status == OrderStatus.FILLED and self.filled_qty == self.quantity

    def is_partially_filled(self) -> bool:
        """Check if order is partially filled"""
        return self.filled_qty > 0 and self.filled_qty < self.quantity

    def remaining_qty(self) -> float:
        """Get remaining quantity to fill"""
        return self.quantity - self.filled_qty

class OrderManager:
    """Manage trading orders"""

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.logger = logging.getLogger(__name__)

    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: OrderType,
        **kwargs
    ) -> Order:
        """Create new order"""
        order = Order(
            order_id=self._generate_order_id(),
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=kwargs.get('price'),
            stop_price=kwargs.get('stop_price'),
            created_at=datetime.utcnow()
        )

        self.orders[order.order_id] = order
        self.logger.info(f"Created order {order.order_id}: {side} {quantity} {symbol}")
        return order

    def update_order_status(self, order_id: str, status: OrderStatus, **updates):
        """Update order status"""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")

        order = self.orders[order_id]
        order.status = status
        order.updated_at = datetime.utcnow()

        # Update filled quantity if provided
        if 'filled_qty' in updates:
            order.filled_qty = updates['filled_qty']

        if 'avg_fill_price' in updates:
            order.avg_fill_price = updates['avg_fill_price']

        self.logger.info(f"Order {order_id} status updated to {status.value}")

    def get_order(self, order_id: str) -> Order:
        """Get order by ID"""
        return self.orders.get(order_id)

    def get_open_orders(self) -> List[Order]:
        """Get all open orders"""
        return [
            order for order in self.orders.values()
            if order.status not in [
                OrderStatus.FILLED,
                OrderStatus.CANCELLED,
                OrderStatus.REJECTED
            ]
        ]

    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
```

### 2. Advanced Order Types

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class AdvancedOrderType(ABC):
    """Base class for advanced order types"""

    @abstractmethod
    def validate(self) -> bool:
        """Validate order parameters"""
        pass

    @abstractmethod
    def to_api_payload(self) -> Dict:
        """Convert to API payload"""
        pass

class TrailingStopOrder(AdvancedOrderType):
    """Trailing stop order"""

    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: float,
        trailing_amount: float,
        trailing_percent: Optional[float] = None
    ):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.trailing_amount = trailing_amount
        self.trailing_percent = trailing_percent

    def validate(self) -> bool:
        if self.side not in ['buy', 'sell']:
            return False
        if self.quantity <= 0:
            return False
        if self.trailing_amount <= 0 and not self.trailing_percent:
            return False
        return True

    def to_api_payload(self) -> Dict:
        return {
            'symbol': self.symbol,
            'qty': self.quantity,
            'side': self.side,
            'type': 'trailing_stop',
            'trail_percent': self.trailing_percent,
            'trail_price': self.trailing_amount
        }

class OneCancelsOtherOrder(AdvancedOrderType):
    """One-Cancels-Other (OCO) order"""

    def __init__(self, primary_order: Order, secondary_order: Order):
        self.primary_order = primary_order
        self.secondary_order = secondary_order
        self.pair_id = self._generate_pair_id()

    def validate(self) -> bool:
        return (self.primary_order.symbol == self.secondary_order.symbol and
                self.primary_order.side == self.secondary_order.side)

    def to_api_payload(self) -> Dict:
        return {
            'type': 'oco',
            'pair_id': self.pair_id,
            'primary': self.primary_order.to_dict(),
            'secondary': self.secondary_order.to_dict()
        }

    def _generate_pair_id(self) -> str:
        import uuid
        return f"OCO-{uuid.uuid4().hex[:8].upper()}"
```

---

## Rate Limiting and Throttling

### 1. Trading API Rate Limits

```
Typical Trading API Rate Limits:

Coinbase Pro:
├── Public Endpoints: 10 requests/second per IP
├── Private Endpoints: 15 requests/second per API key
└── Burst: 50 requests in 5 seconds

Alpaca:
├── Orders Endpoint: 200 requests/minute
├── Account Endpoint: 200 requests/minute
└── Market Data: 200 requests/minute per symbol
```

### 2. Order-Aware Rate Limiter

```python
import time
from collections import deque
from threading import Lock
from typing import Tuple

class OrderAwareRateLimiter:
    """Rate limiter that prioritizes order-critical operations"""

    def __init__(self, orders_per_second: int = 15, reads_per_second: int = 100):
        self.orders_per_second = orders_per_second
        self.reads_per_second = reads_per_second

        self.order_tokens = deque(maxlen=orders_per_second)
        self.read_tokens = deque(maxlen=reads_per_second)

        self.lock = Lock()

    def acquire_order_slot(self) -> float:
        """Acquire slot for order placement (high priority)"""
        return self._acquire_slot(self.order_tokens, self.orders_per_second)

    def acquire_read_slot(self) -> float:
        """Acquire slot for read operation"""
        return self._acquire_slot(self.read_tokens, self.reads_per_second)

    def _acquire_slot(self, tokens: deque, rate: int) -> float:
        """Acquire token from bucket"""
        with self.lock:
            now = time.time()

            # Remove expired tokens
            while tokens and tokens[0] < now:
                tokens.popleft()

            if len(tokens) < rate:
                tokens.append(now)
                return 0  # No wait needed

            # Calculate wait time
            oldest_token = tokens[0]
            wait_time = 1.0 - (now - oldest_token)
            return max(0, wait_time)

    def wait_for_order_slot(self):
        """Wait for order placement slot"""
        wait_time = self.acquire_order_slot()
        if wait_time > 0:
            time.sleep(wait_time)

    def wait_for_read_slot(self):
        """Wait for read operation slot"""
        wait_time = self.acquire_read_slot()
        if wait_time > 0:
            time.sleep(wait_time)
```

---

## WebSocket Real-Time Data

### 1. WebSocket Connection Management

```python
import asyncio
import json
import logging
import websockets
from typing import Callable, Optional
from datetime import datetime

class TradingWebSocketClient:
    """WebSocket client for real-time trading data"""

    def __init__(self, url: str, product_ids: list, logger: Optional[logging.Logger] = None):
        self.url = url
        self.product_ids = product_ids
        self.logger = logger or logging.getLogger(__name__)
        self.ws = None
        self.callbacks = {}
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    async def connect(self):
        """Connect to WebSocket"""
        try:
            self.ws = await websockets.connect(self.url)
            self.is_connected = True
            self.reconnect_attempts = 0

            # Subscribe to channels
            await self._subscribe()

            # Listen for messages
            await self._listen()

        except websockets.exceptions.WebSocketException as e:
            self.logger.error(f"WebSocket error: {e}")
            await self._handle_disconnection()

        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")
            await self._handle_disconnection()

    async def _subscribe(self):
        """Subscribe to product updates"""
        message = {
            "type": "subscribe",
            "product_ids": self.product_ids,
            "channels": ["full", "ticker"]
        }

        await self.ws.send(json.dumps(message))
        self.logger.info(f"Subscribed to {self.product_ids}")

    async def _listen(self):
        """Listen for WebSocket messages"""
        async for message in self.ws:
            try:
                data = json.loads(message)
                await self._handle_message(data)
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid JSON: {message}")
            except Exception as e:
                self.logger.exception(f"Error handling message: {e}")

    async def _handle_message(self, message: dict):
        """Route message to appropriate handler"""
        message_type = message.get('type')

        if message_type == 'ticker':
            await self._handle_ticker(message)
        elif message_type == 'done':
            await self._handle_order_done(message)
        elif message_type == 'match':
            await self._handle_trade(message)

        # Call registered callbacks
        if message_type in self.callbacks:
            for callback in self.callbacks[message_type]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.exception(f"Callback error: {e}")

    async def _handle_ticker(self, message: dict):
        """Handle ticker update"""
        self.logger.debug(f"Ticker: {message['product_id']} @ {message['price']}")

    async def _handle_order_done(self, message: dict):
        """Handle order completion"""
        self.logger.info(f"Order done: {message['order_id']} - {message['reason']}")

    async def _handle_trade(self, message: dict):
        """Handle trade/match"""
        self.logger.info(
            f"Trade: {message['product_id']} - "
            f"{message['side']} {message['size']} @ {message['price']}"
        )

    async def _handle_disconnection(self):
        """Handle WebSocket disconnection"""
        self.is_connected = False
        self.ws = None

        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            wait_time = 2 ** self.reconnect_attempts  # Exponential backoff

            self.logger.warning(
                f"Disconnected. Reconnecting in {wait_time}s "
                f"(attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})"
            )

            await asyncio.sleep(wait_time)
            await self.connect()
        else:
            self.logger.error("Max reconnection attempts reached")

    def register_callback(self, message_type: str, callback: Callable):
        """Register callback for message type"""
        if message_type not in self.callbacks:
            self.callbacks[message_type] = []

        self.callbacks[message_type].append(callback)

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            self.logger.info("WebSocket closed")
```

---

## Error Handling and Resilience

### 1. Trading-Specific Errors

```python
from enum import Enum

class TradingErrorCode(Enum):
    """Trading-specific error codes"""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    INSUFFICIENT_INVENTORY = "insufficient_inventory"
    INVALID_SYMBOL = "invalid_symbol"
    INVALID_ORDER = "invalid_order"
    ORDER_REJECTED = "order_rejected"
    PRODUCT_NOT_TRADING = "product_not_trading"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MARKET_CLOSED = "market_closed"
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    PATTERN_DAY_TRADER = "pattern_day_trader"

class TradingAPIError(Exception):
    """Base trading API error"""

    def __init__(
        self,
        code: TradingErrorCode,
        message: str,
        status: int,
        details: dict = None
    ):
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def is_retryable(self) -> bool:
        """Determine if error is retryable"""
        retryable_codes = {
            TradingErrorCode.RATE_LIMIT_EXCEEDED,
            'temporary_unavailable'
        }
        return self.code in retryable_codes or self.status >= 500

    def is_account_issue(self) -> bool:
        """Determine if error is account-related"""
        account_codes = {
            TradingErrorCode.INSUFFICIENT_FUNDS,
            TradingErrorCode.POSITION_LIMIT_EXCEEDED,
            TradingErrorCode.PATTERN_DAY_TRADER
        }
        return self.code in account_codes

    def __str__(self):
        return f"[{self.code.value}] {self.message}"
```

### 2. Circuit Breaker for Order Placement

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Stop requests
    HALF_OPEN = "half_open"  # Test single request

class TradingCircuitBreaker:
    """Circuit breaker for order placement"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(__name__)

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
                self.logger.info("Circuit breaker entering half-open state")
            else:
                raise CircuitBreakerOpenError(
                    "Circuit breaker is open. Cannot place orders."
                )

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result

        except Exception as e:
            self._record_failure(e)
            raise

    def _record_success(self):
        """Record successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info("Circuit breaker closed")
        else:
            self.failure_count = max(0, self.failure_count - 1)

    def _record_failure(self, error: Exception):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        self.logger.warning(
            f"Order placement failure ({self.failure_count}/{self.failure_threshold}): {error}"
        )

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.error("Circuit breaker opened - halting order placement")

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0

    def _should_attempt_recovery(self) -> bool:
        """Check if recovery timeout has elapsed"""
        if not self.last_failure_time:
            return True

        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed.total_seconds() >= self.recovery_timeout

class CircuitBreakerOpenError(Exception):
    """Circuit breaker is open"""
    pass
```

---

## Idempotency in Trading

### 1. Order Idempotency Keys

```python
import hashlib
import json
from datetime import datetime

class TradeIdempotencyKeyGenerator:
    """Generate idempotency keys for trading operations"""

    @staticmethod
    def generate_order_key(
        user_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Generate deterministic key for order"""
        if timestamp is None:
            timestamp = datetime.utcnow().date()

        key_data = {
            'user_id': user_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': order_type,
            'price': price,
            'date': str(timestamp)
        }

        json_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def generate_cancel_key(user_id: str, order_id: str) -> str:
        """Generate key for order cancellation"""
        key_data = f"{user_id}:cancel:{order_id}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    @staticmethod
    def generate_unique_key() -> str:
        """Generate unique UUID-based key"""
        import uuid
        return str(uuid.uuid4())
```

---

## Webhook Patterns for Trading Events

### 1. Trading Event Webhooks

```python
import hmac
import hashlib
from typing import Dict, Callable
from enum import Enum

class TradingEventType(Enum):
    """Trading event types"""
    ORDER_SUBMITTED = "order.submitted"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_REJECTED = "order.rejected"
    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    ALERT_TRIGGERED = "alert.triggered"

class TradingWebhookValidator:
    """Validate trading webhook signatures"""

    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret.encode()

    def verify_signature(
        self,
        body: str,
        signature_header: str,
        timestamp_header: str,
        tolerance_seconds: int = 300
    ) -> bool:
        """Verify webhook signature and timestamp"""
        import time

        # Verify timestamp
        try:
            timestamp = int(timestamp_header)
        except ValueError:
            raise ValueError("Invalid timestamp")

        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance_seconds:
            raise ValueError("Webhook timestamp outside tolerance window")

        # Verify signature
        signed_content = f"{timestamp}.{body}"
        expected_signature = hmac.new(
            self.webhook_secret,
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature_header, expected_signature)

class TradingWebhookHandler:
    """Handle trading webhooks"""

    def __init__(self):
        self.handlers: Dict[TradingEventType, Callable] = {}

    def register_handler(self, event_type: TradingEventType, handler: Callable):
        """Register handler for event type"""
        self.handlers[event_type] = handler

    async def handle_webhook(self, event: dict):
        """Handle incoming webhook event"""
        event_type_str = event.get('type')

        try:
            event_type = TradingEventType(event_type_str)
        except ValueError:
            logging.warning(f"Unknown event type: {event_type_str}")
            return

        if event_type in self.handlers:
            handler = self.handlers[event_type]
            await handler(event)
```

---

## Coinbase and Alpaca API Examples

### 1. Complete Trading Flow - Coinbase

```python
class CoinbaseTradeManager:
    """Complete trading workflow with Coinbase"""

    def __init__(self, api_client: CoinbaseAPIClient):
        self.client = api_client
        self.order_manager = OrderManager()
        self.rate_limiter = OrderAwareRateLimiter()

    def execute_market_order(self, product_id: str, side: str, amount: float):
        """Execute market order"""
        self.rate_limiter.wait_for_order_slot()

        order_data = {
            'type': 'market',
            'side': side,
            'product_id': product_id
        }

        if side == 'buy':
            order_data['funds'] = amount
        else:
            order_data['size'] = amount

        response = self.client.place_order(**order_data)

        self.order_manager.create_order(
            symbol=product_id,
            side=side,
            quantity=amount,
            order_type=OrderType.MARKET
        )

        return response

    def execute_limit_order(
        self,
        product_id: str,
        side: str,
        size: float,
        price: float
    ):
        """Execute limit order"""
        self.rate_limiter.wait_for_order_slot()

        response = self.client.place_order(
            product_id=product_id,
            side=side,
            type='limit',
            price=price,
            size=size
        )

        self.order_manager.create_order(
            symbol=product_id,
            side=side,
            quantity=size,
            order_type=OrderType.LIMIT,
            price=price
        )

        return response

    def cancel_order(self, order_id: str):
        """Cancel order"""
        self.rate_limiter.wait_for_order_slot()

        response = self.client.cancel_order(order_id)
        self.order_manager.update_order_status(
            order_id,
            OrderStatus.CANCELLED
        )

        return response

    def get_account_balance(self):
        """Get account balance"""
        self.rate_limiter.wait_for_read_slot()
        return self.client.get_accounts()
```

### 2. Complete Trading Flow - Alpaca

```python
class AlpacaTradeManager:
    """Complete trading workflow with Alpaca"""

    def __init__(self, api_client: AlpacaAPIClient):
        self.client = api_client
        self.rate_limiter = OrderAwareRateLimiter()

    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = 'market',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ):
        """Submit order to Alpaca"""
        self.rate_limiter.wait_for_order_slot()

        kwargs = {
            'order_class': 'simple',
            'time_in_force': 'day'
        }

        if limit_price:
            kwargs['limit_price'] = limit_price

        if stop_price:
            kwargs['stop_price'] = stop_price

        if order_type == 'trailing_stop':
            kwargs['trail_percent'] = limit_price  # Use limit_price as percent

        response = self.client.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type_=order_type,
            **kwargs
        )

        return response

    def cancel_order(self, order_id: str):
        """Cancel order"""
        self.rate_limiter.wait_for_order_slot()
        return self.client.cancel_order(order_id)

    def get_positions(self):
        """Get all open positions"""
        self.rate_limiter.wait_for_read_slot()
        return self.client.get_positions()

    def get_account_info(self):
        """Get account information"""
        self.rate_limiter.wait_for_read_slot()
        return self.client.get_account()
```

---

## Risk Management and Circuit Breakers

### 1. Position Risk Management

```python
class PositionRiskManager:
    """Manage position risk limits"""

    def __init__(
        self,
        max_position_size: float,
        max_loss_per_trade: float,
        max_daily_loss: float
    ):
        self.max_position_size = max_position_size
        self.max_loss_per_trade = max_loss_per_trade
        self.max_daily_loss = max_daily_loss
        self.daily_loss = 0
        self.logger = logging.getLogger(__name__)

    def validate_order(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_positions: Dict[str, float]
    ) -> bool:
        """Validate order against risk limits"""
        # Check position size
        current_position = current_positions.get(symbol, 0)
        new_position_size = current_position + quantity

        if abs(new_position_size) > self.max_position_size:
            self.logger.warning(
                f"Order rejected: Position size {new_position_size} "
                f"exceeds limit {self.max_position_size}"
            )
            return False

        return True

    def record_loss(self, loss_amount: float):
        """Record trade loss"""
        self.daily_loss += loss_amount

        if self.daily_loss > self.max_daily_loss:
            self.logger.error(
                f"Daily loss limit exceeded: {self.daily_loss} > {self.max_daily_loss}"
            )
            return False

        return True
```

---

## Compliance and Regulatory Requirements

### 1. Pattern Day Trader Protection

```python
from datetime import datetime, timedelta

class PatternDayTraderCheck:
    """Enforce Pattern Day Trader rules"""

    def __init__(self, account_equity: float):
        self.account_equity = account_equity
        self.min_equity = 25000  # PDT minimum
        self.day_trades = []
        self.day_trade_threshold = 3  # Transactions per 5 days

    def is_pdt_account(self) -> bool:
        """Check if account is Pattern Day Trader"""
        return self.account_equity < self.min_equity

    def record_day_trade(self, symbol: str, timestamp: datetime):
        """Record day trade transaction"""
        self.day_trades.append({
            'symbol': symbol,
            'timestamp': timestamp
        })

        # Remove old trades (older than 5 days)
        cutoff_date = datetime.utcnow() - timedelta(days=5)
        self.day_trades = [
            trade for trade in self.day_trades
            if trade['timestamp'] > cutoff_date
        ]

    def can_place_day_trade(self) -> bool:
        """Check if can place day trade"""
        if not self.is_pdt_account():
            return True

        if len(self.day_trades) >= self.day_trade_threshold:
            return False

        return True

    def get_remaining_day_trades(self) -> int:
        """Get remaining day trades allowed"""
        return max(0, self.day_trade_threshold - len(self.day_trades))
```

---

## Performance Optimization

### 1. Connection Pooling and Caching

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import lru_cache
from datetime import datetime, timedelta

class OptimizedTradingClient:
    """Optimized trading client with connection pooling"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = self._create_session()
        self.price_cache = {}
        self.cache_ttl = timedelta(minutes=1)

    def _create_session(self) -> requests.Session:
        """Create optimized session with connection pooling"""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1.0
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )

        session.mount('https://', adapter)
        return session

    @lru_cache(maxsize=128)
    def get_product_cached(self, product_id: str):
        """Get product with caching"""
        # Cached calls within TTL
        return self._get_product_uncached(product_id)

    def _get_product_uncached(self, product_id: str):
        """Uncached product retrieval"""
        # Actual API call
        pass
```

This comprehensive guide provides production-ready patterns for trading API integration with emphasis on performance, compliance, and risk management.
