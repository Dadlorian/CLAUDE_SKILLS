# Blockchain API Integration Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication Mechanisms](#authentication-mechanisms)
3. [Blockchain Node Communication](#blockchain-node-communication)
4. [Transaction Management](#transaction-management)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Webhook Patterns for Blockchain Events](#webhook-patterns-for-blockchain-events)
8. [Coinbase Custody and Trading APIs](#coinbase-custody-and-trading-apis)
9. [Web3.py and Ethereum Integration](#web3py-and-ethereum-integration)
10. [Security Best Practices](#security-best-practices)
11. [Compliance and Regulatory](#compliance-and-regulatory)
12. [Performance Optimization](#performance-optimization)

---

## Introduction

Blockchain API integration enables interaction with distributed ledgers and cryptocurrency networks. This guide covers standards for integrating with blockchain nodes, exchanges, and custody providers with emphasis on security, reliability, and compliance.

Key considerations for blockchain APIs:
- Immutable transaction records
- Decentralized consensus mechanisms
- High-precision numerical handling
- Gas fees and network costs
- Key management and custody
- Regulatory compliance (FinCEN, OFAC)

---

## Authentication Mechanisms

### 1. API Key Authentication for Blockchain Services

```python
import hmac
import hashlib
import time
import requests
from typing import Dict, Optional

class BlockchainAPIClient:
    """Blockchain API client with HMAC authentication"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_passphrase: Optional[str] = None,
        base_url: str = "https://api.coinbase.com"
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.base_url = base_url
        self.session = requests.Session()

    def _generate_auth_headers(
        self,
        method: str,
        path: str,
        body: str = ""
    ) -> Dict[str, str]:
        """Generate authentication headers"""
        timestamp = str(time.time())

        # Create message to sign
        message = timestamp + method + path + body

        # Create HMAC signature
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        )
        signature_b64 = signature.digest()

        import base64
        signature_encoded = base64.b64encode(signature_b64).decode()

        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature_encoded,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

        if self.api_passphrase:
            headers['CB-ACCESS-PASSPHRASE'] = self.api_passphrase

        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ):
        """Make authenticated request"""
        import json

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

        except requests.exceptions.RequestException as e:
            raise BlockchainAPIError(f"Request failed: {e}")

    def get_account(self, account_id: str) -> Dict:
        """Get account details"""
        return self._request('GET', f'/accounts/{account_id}')

    def get_address(self, account_id: str) -> Dict:
        """Get deposit address for account"""
        return self._request('GET', f'/accounts/{account_id}/addresses')

    def send_money(
        self,
        account_id: str,
        to_address: str,
        amount: str,
        currency: str
    ) -> Dict:
        """Send cryptocurrency"""
        data = {
            'type': 'send',
            'to': to_address,
            'amount': amount,
            'currency': currency
        }

        return self._request(
            'POST',
            f'/accounts/{account_id}/transactions',
            data=data
        )

class BlockchainAPIError(Exception):
    """Blockchain API error"""
    pass
```

### 2. Web3 Provider Authentication

```python
from web3 import Web3
from eth_account import Account
import os

class Web3BlockchainClient:
    """Web3 client for Ethereum and compatible chains"""

    def __init__(
        self,
        rpc_url: str,
        private_key: Optional[str] = None,
        contract_addresses: Optional[Dict[str, str]] = None
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {rpc_url}")

        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = None

        self.contract_addresses = contract_addresses or {}

    def get_balance(self, address: str) -> Dict:
        """Get account balance"""
        if not Web3.is_address(address):
            raise ValueError(f"Invalid address: {address}")

        address = Web3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address)

        return {
            'address': address,
            'balance_wei': balance_wei,
            'balance_eth': self.w3.from_wei(balance_wei, 'ether'),
            'balance_gwei': self.w3.from_wei(balance_wei, 'gwei')
        }

    def get_nonce(self, address: str) -> int:
        """Get account nonce for transaction ordering"""
        if not Web3.is_address(address):
            raise ValueError(f"Invalid address: {address}")

        address = Web3.to_checksum_address(address)
        return self.w3.eth.get_transaction_count(address)

    def get_gas_price(self) -> Dict:
        """Get current gas price"""
        gas_price_wei = self.w3.eth.gas_price

        return {
            'gas_price_wei': gas_price_wei,
            'gas_price_gwei': self.w3.from_wei(gas_price_wei, 'gwei'),
            'gas_price_eth': self.w3.from_wei(gas_price_wei, 'ether')
        }

    def estimate_gas(
        self,
        from_address: str,
        to_address: str,
        value: int = 0,
        data: str = None
    ) -> int:
        """Estimate gas required for transaction"""
        tx_params = {
            'from': Web3.to_checksum_address(from_address),
            'to': Web3.to_checksum_address(to_address),
            'value': value
        }

        if data:
            tx_params['data'] = data

        return self.w3.eth.estimate_gas(tx_params)

    def send_transaction(
        self,
        to_address: str,
        amount_eth: float,
        gas_price_gwei: Optional[float] = None
    ) -> str:
        """Send transaction"""
        if not self.account:
            raise ValueError("Private key required for transaction signing")

        to_address = Web3.to_checksum_address(to_address)
        amount_wei = self.w3.to_wei(amount_eth, 'ether')

        # Get current nonce
        nonce = self.get_nonce(self.account.address)

        # Get gas price
        if gas_price_gwei is None:
            gas_price_wei = self.w3.eth.gas_price
        else:
            gas_price_wei = self.w3.to_wei(gas_price_gwei, 'gwei')

        # Estimate gas
        gas_limit = self.estimate_gas(
            self.account.address,
            to_address,
            amount_wei
        )

        # Build transaction
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': gas_limit,
            'gasPrice': gas_price_wei,
            'chainId': self.w3.eth.chain_id
        }

        # Sign transaction
        signed_tx = self.account.sign_transaction(tx)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()
```

---

## Blockchain Node Communication

### 1. Blockchain RPC Calls

```python
from typing import List, Union
from decimal import Decimal

class BlockchainRPC:
    """Blockchain RPC interface"""

    def __init__(self, w3: Web3):
        self.w3 = w3

    def get_block(self, block_identifier: Union[int, str]) -> Dict:
        """Get block information"""
        block = self.w3.eth.get_block(block_identifier)

        return {
            'number': block['number'],
            'hash': block['hash'].hex(),
            'parent_hash': block['parentHash'].hex(),
            'timestamp': block['timestamp'],
            'miner': block['miner'],
            'difficulty': block['difficulty'],
            'gas_limit': block['gasLimit'],
            'gas_used': block['gasUsed'],
            'transaction_count': len(block['transactions'])
        }

    def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction details"""
        tx = self.w3.eth.get_transaction(tx_hash)

        return {
            'hash': tx['hash'].hex(),
            'from': tx['from'],
            'to': tx['to'],
            'value_eth': self.w3.from_wei(tx['value'], 'ether'),
            'gas': tx['gas'],
            'gas_price_gwei': self.w3.from_wei(tx['gasPrice'], 'gwei'),
            'nonce': tx['nonce'],
            'block_number': tx['blockNumber'],
            'status': 'pending' if tx['blockNumber'] is None else 'confirmed'
        }

    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt"""
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)

        return {
            'transaction_hash': receipt['transactionHash'].hex(),
            'block_number': receipt['blockNumber'],
            'block_hash': receipt['blockHash'].hex(),
            'gas_used': receipt['gasUsed'],
            'cumulative_gas_used': receipt['cumulativeGasUsed'],
            'status': 'success' if receipt['status'] == 1 else 'failed',
            'logs': len(receipt['logs'])
        }

    def get_balance_at_block(
        self,
        address: str,
        block_identifier: Union[int, str] = 'latest'
    ) -> Decimal:
        """Get balance at specific block"""
        address = Web3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address, block_identifier)
        return Decimal(self.w3.from_wei(balance_wei, 'ether'))
```

---

## Transaction Management

### 1. Transaction Lifecycle and Tracking

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class TransactionStatus(Enum):
    """Blockchain transaction status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FINALIZED = "finalized"
    FAILED = "failed"
    REPLACED = "replaced"

@dataclass
class BlockchainTransaction:
    """Blockchain transaction"""
    tx_hash: str
    from_address: str
    to_address: str
    value_eth: Decimal
    gas_price_gwei: Decimal
    gas_limit: int
    nonce: int
    status: TransactionStatus
    block_number: int = None
    block_hash: str = None
    gas_used: int = None
    confirmation_count: int = 0
    created_at: datetime = None

class TransactionManager:
    """Manage blockchain transactions"""

    def __init__(self, w3_client: Web3BlockchainClient):
        self.client = w3_client
        self.transactions = {}
        self.confirmations_required = 12  # ~3 minutes on Ethereum

    def track_transaction(self, tx_hash: str) -> BlockchainTransaction:
        """Start tracking transaction"""
        tx = BlockchainTransaction(
            tx_hash=tx_hash,
            from_address=None,
            to_address=None,
            value_eth=Decimal(0),
            gas_price_gwei=Decimal(0),
            gas_limit=0,
            nonce=0,
            status=TransactionStatus.PENDING,
            created_at=datetime.utcnow()
        )

        self.transactions[tx_hash] = tx
        return tx

    def update_transaction_status(self, tx_hash: str) -> BlockchainTransaction:
        """Update transaction status from blockchain"""
        if tx_hash not in self.transactions:
            raise ValueError(f"Transaction {tx_hash} not tracked")

        try:
            receipt = self.client.w3.eth.get_transaction_receipt(tx_hash)

            if receipt:
                current_block = self.client.w3.eth.block_number
                confirmation_count = current_block - receipt['blockNumber']

                tx = self.transactions[tx_hash]
                tx.block_number = receipt['blockNumber']
                tx.block_hash = receipt['blockHash'].hex()
                tx.gas_used = receipt['gasUsed']
                tx.confirmation_count = confirmation_count

                if receipt['status'] == 1:
                    if confirmation_count >= self.confirmations_required:
                        tx.status = TransactionStatus.FINALIZED
                    else:
                        tx.status = TransactionStatus.CONFIRMED
                else:
                    tx.status = TransactionStatus.FAILED

                return tx
            else:
                # Still pending
                self.transactions[tx_hash].status = TransactionStatus.PENDING
                return self.transactions[tx_hash]

        except Exception as e:
            raise BlockchainAPIError(f"Failed to update transaction: {e}")

    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """Get current transaction status"""
        tx = self.update_transaction_status(tx_hash)
        return tx.status

    def wait_for_confirmation(
        self,
        tx_hash: str,
        max_wait_blocks: int = 100,
        timeout_seconds: int = 600
    ) -> BlockchainTransaction:
        """Wait for transaction confirmation"""
        import time

        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout_seconds:
                raise TimeoutError(f"Transaction confirmation timeout: {tx_hash}")

            tx = self.update_transaction_status(tx_hash)

            if tx.status == TransactionStatus.FINALIZED:
                return tx

            if tx.status == TransactionStatus.FAILED:
                raise BlockchainAPIError(f"Transaction failed: {tx_hash}")

            time.sleep(5)  # Poll every 5 seconds
```

---

## Error Handling

### 1. Blockchain-Specific Errors

```python
from enum import Enum

class BlockchainErrorCode(Enum):
    """Blockchain-specific error codes"""
    INVALID_ADDRESS = "invalid_address"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    INVALID_TRANSACTION = "invalid_transaction"
    TRANSACTION_FAILED = "transaction_failed"
    GAS_ESTIMATION_FAILED = "gas_estimation_failed"
    NONCE_TOO_LOW = "nonce_too_low"
    TX_POOL_FULL = "tx_pool_full"
    REPLACEMENT_UNDERPRICED = "replacement_underpriced"
    NETWORK_ERROR = "network_error"
    NODE_UNAVAILABLE = "node_unavailable"

class BlockchainException(Exception):
    """Base blockchain exception"""

    def __init__(self, error_code: BlockchainErrorCode, message: str, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}

    def is_retryable(self) -> bool:
        """Determine if error is retryable"""
        retryable = {
            BlockchainErrorCode.NETWORK_ERROR,
            BlockchainErrorCode.NODE_UNAVAILABLE,
            BlockchainErrorCode.TX_POOL_FULL
        }
        return self.error_code in retryable

    def __str__(self):
        return f"[{self.error_code.value}] {self.message}"

class BlockchainErrorHandler:
    """Handle blockchain errors"""

    @staticmethod
    def handle_eth_error(error: Exception) -> BlockchainException:
        """Convert Web3 errors to BlockchainException"""
        error_msg = str(error).lower()

        if 'invalid address' in error_msg:
            return BlockchainException(
                BlockchainErrorCode.INVALID_ADDRESS,
                "Invalid Ethereum address format"
            )
        elif 'insufficient balance' in error_msg:
            return BlockchainException(
                BlockchainErrorCode.INSUFFICIENT_BALANCE,
                "Account has insufficient balance"
            )
        elif 'nonce' in error_msg and 'too low' in error_msg:
            return BlockchainException(
                BlockchainErrorCode.NONCE_TOO_LOW,
                "Transaction nonce is too low"
            )
        elif 'replacement transaction underpriced' in error_msg:
            return BlockchainException(
                BlockchainErrorCode.REPLACEMENT_UNDERPRICED,
                "Replacement transaction gas price too low"
            )
        elif 'connection' in error_msg or 'timeout' in error_msg:
            return BlockchainException(
                BlockchainErrorCode.NETWORK_ERROR,
                "Network connection error"
            )
        else:
            return BlockchainException(
                BlockchainErrorCode.INVALID_TRANSACTION,
                str(error)
            )
```

---

## Rate Limiting

### 1. Blockchain API Rate Limiting

```python
import time
from collections import deque
from threading import Lock

class BlockchainRateLimiter:
    """Rate limiter for blockchain APIs"""

    def __init__(self):
        # Typical Infura/Alchemy limits
        self.call_limits = {
            'standard': {'calls': 500, 'period': 1},  # 500 calls/sec
            'archive': {'calls': 100, 'period': 1},   # 100 calls/sec archive
            'trace': {'calls': 50, 'period': 1}       # 50 calls/sec trace
        }

        self.token_buckets = {
            key: deque() for key in self.call_limits
        }

        self.lock = Lock()

    def is_allowed(self, method_type: str = 'standard') -> bool:
        """Check if request is allowed"""
        if method_type not in self.call_limits:
            return True

        with self.lock:
            now = time.time()
            limit_config = self.call_limits[method_type]

            # Remove expired tokens
            while (self.token_buckets[method_type] and
                   self.token_buckets[method_type][0] < now - limit_config['period']):
                self.token_buckets[method_type].popleft()

            if len(self.token_buckets[method_type]) < limit_config['calls']:
                self.token_buckets[method_type].append(now)
                return True

            return False

    def acquire(self, method_type: str = 'standard') -> float:
        """Acquire request slot, returns wait time"""
        if not self.is_allowed(method_type):
            with self.lock:
                oldest = self.token_buckets[method_type][0]
                now = time.time()
                period = self.call_limits[method_type]['period']
                return period - (now - oldest)

        return 0
```

---

## Webhook Patterns for Blockchain Events

### 1. Blockchain Event Monitoring

```python
from typing import Callable, Dict, List

class BlockchainEventListener:
    """Listen for blockchain events"""

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.filters = {}

    def register_event_handler(
        self,
        event_name: str,
        handler: Callable
    ):
        """Register handler for event"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

        self.event_handlers[event_name].append(handler)

    def listen_for_block(self):
        """Listen for new blocks"""
        def block_callback(block_hash):
            block = self.w3.eth.get_block(block_hash)

            for handler in self.event_handlers.get('block', []):
                try:
                    handler({
                        'block_number': block['number'],
                        'block_hash': block_hash.hex(),
                        'timestamp': block['timestamp'],
                        'transactions': len(block['transactions'])
                    })
                except Exception as e:
                    print(f"Error in block handler: {e}")

        self.filters['block'] = self.w3.eth.filter('latest')
        self.filters['block'].watch(block_callback)

    def listen_for_logs(
        self,
        contract_address: str,
        event_signature: str
    ):
        """Listen for contract events"""
        event_filter = self.w3.eth.filter({
            'address': contract_address,
            'topics': [self.w3.keccak(text=event_signature)]
        })

        def log_callback(log):
            for handler in self.event_handlers.get('log', []):
                try:
                    handler({
                        'address': log['address'],
                        'topics': [topic.hex() for topic in log['topics']],
                        'data': log['data'],
                        'block_number': log['blockNumber']
                    })
                except Exception as e:
                    print(f"Error in log handler: {e}")

        event_filter.watch(log_callback)
        self.filters['logs'] = event_filter
```

---

## Coinbase Custody and Trading APIs

### 1. Coinbase Commerce Integration

```python
import hmac
import hashlib
import json
import requests

class CoinbaseCommerceClient:
    """Coinbase Commerce API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.commerce.coinbase.com"

    def create_charge(
        self,
        amount: str,
        currency: str,
        description: str,
        metadata: dict = None
    ) -> Dict:
        """Create charge for payment"""
        data = {
            'name': description,
            'description': description,
            'pricing_type': 'fixed_price',
            'local_price': {
                'amount': amount,
                'currency': currency
            }
        }

        if metadata:
            data['metadata'] = metadata

        headers = {
            'X-CC-Api-Key': self.api_key,
            'X-CC-Version': '2018-03-22',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'{self.base_url}/charges',
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def get_charge(self, charge_id: str) -> Dict:
        """Get charge details"""
        headers = {
            'X-CC-Api-Key': self.api_key,
            'X-CC-Version': '2018-03-22'
        }

        response = requests.get(
            f'{self.base_url}/charges/{charge_id}',
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def verify_webhook(self, body: str, signature: str) -> bool:
        """Verify webhook signature"""
        expected_sig = hmac.new(
            self.api_key.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_sig)
```

---

## Web3.py and Ethereum Integration

### 1. Smart Contract Interaction

```python
from web3 import Web3
from web3.contract import Contract

class SmartContractInteraction:
    """Interact with smart contracts"""

    def __init__(self, w3: Web3, contract_address: str, contract_abi: list):
        self.w3 = w3
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = w3.eth.contract(
            address=self.contract_address,
            abi=contract_abi
        )

    def call_function(self, function_name: str, *args) -> any:
        """Call contract function (read-only)"""
        function = getattr(self.contract.functions, function_name)
        return function(*args).call()

    def execute_function(
        self,
        from_account,
        function_name: str,
        *args,
        gas_price_gwei: float = None,
        gas_limit: int = None
    ) -> str:
        """Execute contract function (state-changing)"""
        function = getattr(self.contract.functions, function_name)

        nonce = self.w3.eth.get_transaction_count(from_account.address)

        if gas_price_gwei is None:
            gas_price = self.w3.eth.gas_price
        else:
            gas_price = self.w3.to_wei(gas_price_gwei, 'gwei')

        if gas_limit is None:
            gas_limit = function(*args).estimate_gas({'from': from_account.address})

        tx = function(*args).build_transaction({
            'from': from_account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = from_account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    def get_event_logs(
        self,
        event_name: str,
        from_block: int = 0,
        to_block: str = 'latest'
    ) -> List[Dict]:
        """Get contract event logs"""
        event = getattr(self.contract.events, event_name)
        logs = event.get_logs(
            from_block=from_block,
            to_block=to_block
        )

        return [dict(log) for log in logs]
```

---

## Security Best Practices

### 1. Private Key Management

```python
from eth_account import Account
import os
from cryptography.fernet import Fernet

class SecureKeyManager:
    """Manage private keys securely"""

    def __init__(self):
        self.encryption_key = os.environ.get('KEY_ENCRYPTION_KEY')
        self.cipher_suite = Fernet(self.encryption_key.encode() if self.encryption_key else None)

    def create_account(self) -> Dict:
        """Create new account"""
        account = Account.create()

        return {
            'address': account.address,
            'private_key': account.key.hex()
        }

    def encrypt_private_key(self, private_key: str) -> str:
        """Encrypt private key"""
        if not self.cipher_suite:
            raise ValueError("Encryption key not configured")

        encrypted = self.cipher_suite.encrypt(private_key.encode())
        return encrypted.decode()

    def decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt private key"""
        if not self.cipher_suite:
            raise ValueError("Encryption key not configured")

        decrypted = self.cipher_suite.decrypt(encrypted_key.encode())
        return decrypted.decode()

    def load_account_from_encrypted_key(self, encrypted_key: str) -> Account:
        """Load account from encrypted key"""
        private_key = self.decrypt_private_key(encrypted_key)
        return Account.from_key(private_key)

    def store_key_in_vault(self, private_key: str, key_name: str):
        """Store key in secure vault (AWS SecretsManager, HashiCorp Vault, etc.)"""
        # Implementation depends on vault provider
        pass
```

---

## Compliance and Regulatory

### 1. OFAC and Sanctions Screening

```python
import requests
from typing import Tuple

class ComplianceScreening:
    """Screen addresses for compliance"""

    def __init__(self):
        self.ofac_api_url = "https://api.compliance.example.com/ofac"

    def screen_address(self, address: str) -> Tuple[bool, str]:
        """Screen address against OFAC list"""
        try:
            response = requests.get(
                f"{self.ofac_api_url}/screen",
                params={'address': address},
                timeout=10
            )

            result = response.json()

            if result.get('match'):
                return False, f"Address matches OFAC list: {result.get('reason')}"

            return True, "Address passed screening"

        except Exception as e:
            # Fail safe - reject on error
            return False, f"Screening service error: {e}"

    def screen_transaction(
        self,
        from_address: str,
        to_address: str,
        amount_eth: float
    ) -> Tuple[bool, str]:
        """Screen transaction for compliance"""
        # Check both addresses
        from_ok, from_msg = self.screen_address(from_address)
        if not from_ok:
            return False, f"Sender: {from_msg}"

        to_ok, to_msg = self.screen_address(to_address)
        if not to_ok:
            return False, f"Recipient: {to_msg}"

        return True, "Transaction approved"
```

---

## Performance Optimization

### 1. Connection Pooling and Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class OptimizedBlockchainClient:
    """Optimized blockchain client with caching"""

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.cache_ttl = timedelta(seconds=30)
        self.last_cache_clear = datetime.utcnow()

    @lru_cache(maxsize=1024)
    def get_balance_cached(self, address: str, block: str = 'latest') -> Decimal:
        """Get balance with caching"""
        from decimal import Decimal
        address = Web3.to_checksum_address(address)
        balance_wei = self.w3.eth.get_balance(address, block)
        return Decimal(self.w3.from_wei(balance_wei, 'ether'))

    def clear_cache_if_needed(self):
        """Clear cache if TTL expired"""
        elapsed = datetime.utcnow() - self.last_cache_clear

        if elapsed > self.cache_ttl:
            self.get_balance_cached.cache_clear()
            self.last_cache_clear = datetime.utcnow()

    def batch_get_balances(self, addresses: list) -> Dict[str, Decimal]:
        """Get balances for multiple addresses"""
        self.clear_cache_if_needed()

        return {
            addr: self.get_balance_cached(addr)
            for addr in addresses
        }
```

This comprehensive guide provides production-ready patterns for blockchain API integration with emphasis on security, compliance, and performance.
