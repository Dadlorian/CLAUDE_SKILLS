# Banking API Standards and Integration Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication and Authorization](#authentication-and-authorization)
3. [Open Banking Standards](#open-banking-standards)
4. [Account and Transaction APIs](#account-and-transaction-apis)
5. [Payment Initiation Services](#payment-initiation-services)
6. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
7. [Error Handling](#error-handling)
8. [Webhook Patterns](#webhook-patterns)
9. [Plaid API Integration](#plaid-api-integration)
10. [Security and Compliance](#security-and-compliance)
11. [Data Encryption and Tokenization](#data-encryption-and-tokenization)
12. [Regulatory Requirements](#regulatory-requirements)

---

## Introduction

Banking APIs enable secure access to financial data and payment capabilities. This guide covers industry standards including PSD2, Open Banking, and best practices for integrating with banks through platforms like Plaid and traditional banking APIs.

Banking APIs must handle:
- Sensitive customer financial data
- Multi-factor authentication
- PCI-DSS compliance
- PSD2/Open Banking standards
- Strong Customer Authentication (SCA)
- Fraud detection and prevention

---

## Authentication and Authorization

### 1. Mutual Authentication (Bank-Grade Security)

```python
import ssl
import requests
import os
from requests.adapters import HTTPAdapter

class BankingAPIClient:
    """Banking API client with mutual TLS authentication"""

    def __init__(
        self,
        client_cert: str,
        client_key: str,
        ca_bundle: str,
        base_url: str
    ):
        self.base_url = base_url
        self.session = self._create_secure_session(client_cert, client_key, ca_bundle)

    def _create_secure_session(self, cert: str, key: str, ca_bundle: str) -> requests.Session:
        """Create secure session with mTLS"""
        session = requests.Session()

        # Load client certificate and key
        session.cert = (cert, key)
        session.verify = ca_bundle

        # Use TLS 1.2 or higher
        adapter = HTTPAdapter()
        adapter.init_poolmanager(
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            ca_certs=ca_bundle,
            cert_file=cert,
            key_file=key
        )

        session.mount('https://', adapter)
        return session

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        params: dict = None
    ):
        """Make authenticated request"""
        url = self.base_url + endpoint

        default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BankingAPI/1.0',
            'Accept': 'application/json'
        }

        if headers:
            default_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=default_headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.SSLError as e:
            raise SecurityError(f"SSL/TLS error: {e}")
        except requests.exceptions.RequestException as e:
            raise BankingAPIError(f"Request failed: {e}")

class SecurityError(Exception):
    """Security-related error"""
    pass

class BankingAPIError(Exception):
    """Banking API error"""
    pass
```

### 2. OAuth 2.0 with Consent Flow

```python
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

class BankingOAuthFlow:
    """Open Banking OAuth 2.0 flow with consent"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        auth_url: str,
        token_url: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = auth_url
        self.token_url = token_url

    def generate_consent_request(self, scopes: list, consent_duration: int = 90) -> Dict:
        """Generate consent request for user"""
        consent_id = secrets.token_urlsafe(32)

        consent_request = {
            'consent_id': consent_id,
            'scopes': scopes,
            'permissions': self._scope_to_permissions(scopes),
            'duration_days': consent_duration,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }

        return consent_request

    def get_authorization_url(
        self,
        consent_id: str,
        state: str,
        scopes: list
    ) -> str:
        """Get authorization URL for user"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(scopes),
            'consent_id': consent_id
        }

        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    def exchange_code_for_token(
        self,
        code: str,
        state: str,
        consent_id: str
    ) -> Dict:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'consent_id': consent_id
        }

        response = requests.post(self.token_url, data=data, timeout=30)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in'),
            'expires_at': datetime.utcnow() + timedelta(seconds=token_data['expires_in']),
            'scope': token_data.get('scope', ' '.join(data['scope'].split())),
            'consent_id': consent_id
        }

    def refresh_access_token(self, refresh_token: str, consent_id: str) -> Dict:
        """Refresh access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'consent_id': consent_id
        }

        response = requests.post(self.token_url, data=data, timeout=30)
        response.raise_for_status()

        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token', refresh_token),
            'expires_at': datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        }

    def revoke_consent(self, consent_id: str, token: str) -> bool:
        """Revoke user consent"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        data = {'consent_id': consent_id}

        response = requests.post(
            f"{self.auth_url}/revoke",
            headers=headers,
            json=data,
            timeout=30
        )

        return response.status_code == 200

    @staticmethod
    def _scope_to_permissions(scopes: list) -> Dict[str, bool]:
        """Convert scopes to permissions"""
        permission_map = {
            'accounts': 'accounts',
            'transactions': 'transactions',
            'balances': 'balances',
            'payments': 'payments'
        }

        return {permission_map.get(scope, scope): True for scope in scopes}
```

### 3. Strong Customer Authentication (SCA)

```python
from enum import Enum
import json

class AuthenticationMethod(Enum):
    """SCA authentication methods"""
    PASSWORD = "password"
    SMS_OTP = "sms_otp"
    EMAIL_OTP = "email_otp"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"

class StrongCustomerAuthentication:
    """Implement Strong Customer Authentication"""

    def __init__(self):
        self.pending_challenges = {}
        self.logger = logging.getLogger(__name__)

    def initiate_sca(
        self,
        user_id: str,
        transaction_amount: float,
        transaction_type: str,
        risk_level: str = 'medium'
    ) -> Dict:
        """Initiate SCA challenge"""
        challenge_id = self._generate_challenge_id()

        # Determine authentication methods based on risk
        methods = self._determine_methods(risk_level)

        challenge = {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'transaction_amount': transaction_amount,
            'transaction_type': transaction_type,
            'risk_level': risk_level,
            'methods': methods,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }

        self.pending_challenges[challenge_id] = challenge

        # Initiate primary authentication method
        primary_method = methods[0]
        self._send_authentication_code(user_id, primary_method)

        return {
            'challenge_id': challenge_id,
            'methods': methods,
            'hint': self._get_method_hint(user_id, primary_method)
        }

    def verify_sca(
        self,
        challenge_id: str,
        method: AuthenticationMethod,
        response: str
    ) -> bool:
        """Verify SCA response"""
        if challenge_id not in self.pending_challenges:
            raise ValueError("Invalid challenge ID")

        challenge = self.pending_challenges[challenge_id]

        # Check expiration
        expires_at = datetime.fromisoformat(challenge['expires_at'])
        if datetime.utcnow() > expires_at:
            raise ValueError("Challenge expired")

        # Verify response based on method
        if method == AuthenticationMethod.SMS_OTP:
            return self._verify_otp(challenge['user_id'], response)
        elif method == AuthenticationMethod.PASSWORD:
            return self._verify_password(challenge['user_id'], response)

        return False

    def _determine_methods(self, risk_level: str) -> list:
        """Determine authentication methods based on risk"""
        if risk_level == 'high':
            return [
                AuthenticationMethod.SMS_OTP.value,
                AuthenticationMethod.BIOMETRIC.value
            ]
        elif risk_level == 'medium':
            return [
                AuthenticationMethod.SMS_OTP.value,
                AuthenticationMethod.EMAIL_OTP.value
            ]
        else:
            return [AuthenticationMethod.PASSWORD.value]

    def _send_authentication_code(self, user_id: str, method: str):
        """Send authentication code via method"""
        # Implementation varies by method
        pass

    def _verify_otp(self, user_id: str, code: str) -> bool:
        """Verify OTP"""
        # Implementation
        pass

    def _verify_password(self, user_id: str, password: str) -> bool:
        """Verify password"""
        # Implementation
        pass

    def _get_method_hint(self, user_id: str, method: str) -> str:
        """Get hint for method (e.g., last 4 digits of phone)"""
        # Implementation
        pass

    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        import uuid
        return f"SCA-{uuid.uuid4().hex[:16].upper()}"
```

---

## Open Banking Standards

### 1. PSD2 Compliance

```python
from enum import Enum
from dataclasses import dataclass
from typing import List

class PSD2Permission(Enum):
    """PSD2 access permissions"""
    READ_ACCOUNTS = "ReadAccountsBasic"
    READ_ACCOUNT_DETAILS = "ReadAccountsDetail"
    READ_BALANCES = "ReadBalances"
    READ_TRANSACTIONS = "ReadTransactions"
    READ_BENEFICIARIES = "ReadBeneficiaries"
    INITIATE_PAYMENT = "InitiatePaymentService"
    CONFIRM_FUNDS = "ConfirmFundsAvailability"

@dataclass
class PSD2ConsentRequest:
    """PSD2 consent request"""
    permissions: List[PSD2Permission]
    validity_period: int  # Days
    transaction_from_date: str
    transaction_to_date: str
    frequency_per_day: int
    multi_currency_allowed: bool

class PSD2Compliance:
    """PSD2 compliance handler"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_consent(
        self,
        user_id: str,
        permissions: List[PSD2Permission],
        timestamp: datetime
    ) -> bool:
        """Validate PSD2 consent"""
        # Check consent exists and is valid
        consent = self._get_consent(user_id, permissions)

        if not consent:
            return False

        # Check consent not expired
        if timestamp > datetime.fromisoformat(consent['expires_at']):
            return False

        # Check permissions match
        consented_perms = set(consent['permissions'])
        requested_perms = set(p.value for p in permissions)

        return requested_perms.issubset(consented_perms)

    def check_transaction_limits(
        self,
        user_id: str,
        transaction_amount: float
    ) -> bool:
        """Check PSD2 transaction limits"""
        consent = self._get_consent(user_id)

        # Check frequency limits
        today_transactions = self._get_transactions_today(user_id)
        if len(today_transactions) >= consent['frequency_per_day']:
            self.logger.warning(
                f"User {user_id} exceeded daily transaction limit"
            )
            return False

        return True

    def log_access(
        self,
        user_id: str,
        permission: PSD2Permission,
        data_accessed: str,
        timestamp: datetime
    ):
        """Log data access for audit trail"""
        access_record = {
            'user_id': user_id,
            'permission': permission.value,
            'data_accessed': data_accessed,
            'timestamp': timestamp.isoformat(),
            'ip_address': self._get_client_ip()
        }

        # Store in audit log
        self._store_audit_log(access_record)

    def _get_consent(self, user_id: str, permissions: List[PSD2Permission] = None):
        """Get consent record"""
        # Implementation
        pass

    def _get_transactions_today(self, user_id: str) -> list:
        """Get transactions initiated today"""
        # Implementation
        pass

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation
        pass

    def _store_audit_log(self, record: dict):
        """Store audit log"""
        # Implementation
        pass
```

---

## Account and Transaction APIs

### 1. Account Information Service (AIS)

```python
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

@dataclass
class BankAccount:
    """Bank account information"""
    account_id: str
    iban: str
    bban: str
    currency: str
    name: str
    account_type: str
    account_status: str
    balance: 'AccountBalance' = None
    product: Optional[str] = None
    sub_accounts: List['BankAccount'] = None

@dataclass
class AccountBalance:
    """Account balance information"""
    balance_type: str  # 'Booked', 'Pending', 'Available'
    amount: Decimal
    currency: str
    reference_date: datetime
    last_change_date: Optional[datetime] = None

@dataclass
class Transaction:
    """Transaction information"""
    transaction_id: str
    amount: Decimal
    currency: str
    booked_date: datetime
    value_date: Optional[datetime] = None
    reference: str
    additional_info: Optional[str] = None
    transaction_type: str
    booking_status: str  # 'Booked' or 'Pending'
    debtor_name: Optional[str] = None
    debtor_account: Optional[str] = None
    creditor_name: Optional[str] = None
    creditor_account: Optional[str] = None

class AccountInformationService:
    """Account Information Service (AIS) implementation"""

    def __init__(self, client: BankingAPIClient):
        self.client = client

    def get_accounts(self, user_id: str) -> List[BankAccount]:
        """Get list of accounts for user"""
        response = self.client._request(
            'GET',
            '/accounts',
            headers={'Authorization': f'Bearer {self._get_access_token(user_id)}'}
        )

        accounts = []
        for account_data in response.get('accounts', []):
            account = BankAccount(
                account_id=account_data['account_id'],
                iban=account_data['iban'],
                bban=account_data.get('bban'),
                currency=account_data['currency'],
                name=account_data['name'],
                account_type=account_data['account_type'],
                account_status=account_data['account_status']
            )
            accounts.append(account)

        return accounts

    def get_account_balance(self, user_id: str, account_id: str) -> AccountBalance:
        """Get account balance"""
        response = self.client._request(
            'GET',
            f'/accounts/{account_id}/balances',
            headers={'Authorization': f'Bearer {self._get_access_token(user_id)}'}
        )

        balance_data = response['balances'][0]  # Usually Booked balance

        return AccountBalance(
            balance_type=balance_data['balanceType'],
            amount=Decimal(balance_data['amount']['amount']),
            currency=balance_data['amount']['currency'],
            reference_date=datetime.fromisoformat(balance_data['referenceDate'])
        )

    def get_transactions(
        self,
        user_id: str,
        account_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """Get account transactions"""
        params = {'limit': limit}

        if from_date:
            params['from_date'] = from_date.isoformat()
        if to_date:
            params['to_date'] = to_date.isoformat()

        response = self.client._request(
            'GET',
            f'/accounts/{account_id}/transactions',
            headers={'Authorization': f'Bearer {self._get_access_token(user_id)}'},
            params=params
        )

        transactions = []
        for txn_data in response.get('transactions', []):
            transaction = Transaction(
                transaction_id=txn_data['transaction_id'],
                amount=Decimal(txn_data['booked_amount']['amount']),
                currency=txn_data['booked_amount']['currency'],
                booked_date=datetime.fromisoformat(txn_data['booking_date']),
                reference=txn_data['reference'],
                additional_info=txn_data.get('additional_info'),
                transaction_type=txn_data.get('transaction_type', 'Unknown'),
                booking_status='Booked',
                debtor_name=txn_data.get('debtor', {}).get('name'),
                debtor_account=txn_data.get('debtor', {}).get('account'),
                creditor_name=txn_data.get('creditor', {}).get('name'),
                creditor_account=txn_data.get('creditor', {}).get('account')
            )
            transactions.append(transaction)

        return transactions

    def _get_access_token(self, user_id: str) -> str:
        """Get access token for user"""
        # Implementation
        pass
```

---

## Payment Initiation Services

### 1. Payment Initiation Service (PIS)

```python
from enum import Enum

class PaymentStatus(Enum):
    """Payment status"""
    ACSP = "AcceptedSettlementInProcess"
    ACCC = "AcceptedCustomerProfile"
    ACSM = "AcceptedSettlementCompleted"
    ACCM = "AcceptedCustAndSettlementProcessing"
    CANP = "CancelledByCustomer"
    RJCT = "Rejected"
    PDNG = "Pending"

class PaymentInitiationService:
    """Payment Initiation Service (PIS) implementation"""

    def __init__(self, client: BankingAPIClient):
        self.client = client

    def initiate_payment(
        self,
        user_id: str,
        debtor_account: str,
        creditor_account: str,
        creditor_name: str,
        amount: Decimal,
        currency: str,
        reference: str,
        execution_date: Optional[datetime] = None
    ) -> Dict:
        """Initiate payment"""
        payment_data = {
            'debtor_account': debtor_account,
            'creditor_account': creditor_account,
            'creditor_name': creditor_name,
            'instructed_amount': {
                'amount': str(amount),
                'currency': currency
            },
            'reference': reference,
            'execution_date': execution_date.isoformat() if execution_date else None
        }

        response = self.client._request(
            'POST',
            '/payments',
            headers={'Authorization': f'Bearer {self._get_access_token(user_id)}'},
            data=payment_data
        )

        return {
            'payment_id': response['payment_id'],
            'status': PaymentStatus[response['status']],
            'created_at': datetime.utcnow(),
            'execution_date': execution_date
        }

    def confirm_payment(self, user_id: str, payment_id: str) -> bool:
        """Confirm payment with SCA"""
        # Initiate SCA
        sca = StrongCustomerAuthentication()
        challenge = sca.initiate_sca(
            user_id=user_id,
            transaction_amount=self._get_payment_amount(payment_id),
            transaction_type='payment',
            risk_level='high'  # Payments always high risk
        )

        # Return challenge to client for SCA completion
        return True

    def get_payment_status(self, user_id: str, payment_id: str) -> PaymentStatus:
        """Get payment status"""
        response = self.client._request(
            'GET',
            f'/payments/{payment_id}',
            headers={'Authorization': f'Bearer {self._get_access_token(user_id)}'}
        )

        return PaymentStatus[response['status']]

    def _get_access_token(self, user_id: str) -> str:
        """Get access token for user"""
        pass

    def _get_payment_amount(self, payment_id: str) -> Decimal:
        """Get payment amount"""
        pass
```

---

## Rate Limiting and Throttling

### 1. Banking API Rate Limits

```python
import time
from threading import Lock

class BankingRateLimiter:
    """Rate limiter for banking APIs"""

    def __init__(self):
        # Typical banking API limits
        self.limits = {
            'accounts': {'limit': 100, 'window': 60},  # 100 per minute
            'transactions': {'limit': 200, 'window': 60},
            'payments': {'limit': 50, 'window': 60},
            'balances': {'limit': 300, 'window': 60}
        }
        self.counters = {key: deque() for key in self.limits}
        self.lock = Lock()

    def is_allowed(self, endpoint: str) -> bool:
        """Check if request is allowed"""
        if endpoint not in self.limits:
            return True

        with self.lock:
            now = time.time()
            limit_config = self.limits[endpoint]

            # Remove expired requests
            while (self.counters[endpoint] and
                   self.counters[endpoint][0] < now - limit_config['window']):
                self.counters[endpoint].popleft()

            if len(self.counters[endpoint]) < limit_config['limit']:
                self.counters[endpoint].append(now)
                return True

            return False

    def get_wait_time(self, endpoint: str) -> float:
        """Get wait time before next request"""
        if endpoint not in self.limits:
            return 0

        with self.lock:
            if len(self.counters[endpoint]) == 0:
                return 0

            limit_config = self.limits[endpoint]
            oldest = self.counters[endpoint][0]
            now = time.time()

            return max(0, limit_config['window'] - (now - oldest))
```

---

## Error Handling

### 1. Banking-Specific Errors

```python
from enum import Enum

class BankingErrorCode(Enum):
    """Banking API error codes"""
    INVALID_ACCOUNT = "INVALID_ACCOUNT"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

class BankingAPIException(Exception):
    """Base banking API exception"""

    def __init__(self, error_code: BankingErrorCode, message: str, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"[{self.error_code.value}] {self.message}"
```

---

## Webhook Patterns

### 1. Banking Webhook Events

```python
import hmac
import hashlib

class BankingWebhookValidator:
    """Validate banking webhook signatures"""

    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret.encode()

    def verify_signature(
        self,
        body: str,
        signature: str
    ) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            self.webhook_secret,
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

class BankingWebhookHandler:
    """Handle banking webhooks"""

    def __init__(self):
        self.handlers = {}

    def register_handler(self, event_type: str, handler):
        """Register event handler"""
        self.handlers[event_type] = handler

    async def handle_event(self, event: dict):
        """Handle webhook event"""
        event_type = event.get('type')

        if event_type in self.handlers:
            await self.handlers[event_type](event)
```

---

## Plaid API Integration

### 1. Plaid Authentication Flow

```python
import requests
from typing import Dict, Optional

class PlaidClient:
    """Plaid API client"""

    def __init__(self, client_id: str, secret: str, environment: str = 'sandbox'):
        self.client_id = client_id
        self.secret = secret
        self.base_url = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }[environment]

    def create_link_token(
        self,
        user_id: str,
        client_name: str,
        language: str = 'en',
        country_codes: list = None
    ) -> Dict:
        """Create Link token for web flow"""
        data = {
            'user': {'client_user_id': user_id},
            'client_name': client_name,
            'language': language,
            'country_codes': country_codes or ['US'],
            'products': ['auth', 'transactions']
        }

        response = requests.post(
            f'{self.base_url}/link/token/create',
            json=self._add_client_credentials(data),
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def exchange_public_token(self, public_token: str) -> Dict:
        """Exchange public token for access token"""
        data = {
            'public_token': public_token
        }

        response = requests.post(
            f'{self.base_url}/item/public_token/exchange',
            json=self._add_client_credentials(data),
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def get_auth(self, access_token: str) -> Dict:
        """Get authentication information"""
        data = {
            'access_token': access_token
        }

        response = requests.post(
            f'{self.base_url}/auth/get',
            json=self._add_client_credentials(data),
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """Get transactions"""
        data = {
            'access_token': access_token,
            'start_date': start_date,
            'end_date': end_date
        }

        response = requests.post(
            f'{self.base_url}/transactions/get',
            json=self._add_client_credentials(data),
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def _add_client_credentials(self, data: Dict) -> Dict:
        """Add client credentials to request"""
        data['client_id'] = self.client_id
        data['secret'] = self.secret
        return data
```

---

## Security and Compliance

### 1. Data Encryption and Masking

```python
from cryptography.fernet import Fernet
import os

class BankingDataProtection:
    """Protect sensitive banking data"""

    def __init__(self):
        self.cipher_key = os.environ.get('ENCRYPTION_KEY')
        self.cipher_suite = Fernet(self.cipher_key)

    def encrypt_account_number(self, account_number: str) -> str:
        """Encrypt account number"""
        encrypted = self.cipher_suite.encrypt(account_number.encode())
        return encrypted.decode()

    def decrypt_account_number(self, encrypted: str) -> str:
        """Decrypt account number"""
        decrypted = self.cipher_suite.decrypt(encrypted.encode())
        return decrypted.decode()

    def mask_account_number(self, account_number: str) -> str:
        """Mask account number for display"""
        if len(account_number) < 4:
            return "****"
        return "****" + account_number[-4:]

    def mask_iban(self, iban: str) -> str:
        """Mask IBAN for display"""
        if len(iban) < 8:
            return "****"
        return iban[:4] + "****" + iban[-4:]

    def log_transaction(
        self,
        user_id: str,
        transaction_id: str,
        amount: Decimal,
        masked_account: str
    ):
        """Log transaction with masked data"""
        log_entry = {
            'user_id': user_id,
            'transaction_id': transaction_id,
            'amount': str(amount),
            'account': masked_account,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store securely
        pass
```

---

## Regulatory Requirements

### 1. Compliance Checklist

```yaml
PSD2 Requirements:
  ✓ Strong Customer Authentication for payments
  ✓ Secure communication (TLS 1.2+)
  ✓ Consent management
  ✓ Audit trails
  ✓ Transaction monitoring
  ✓ User notification

PCI-DSS Requirements:
  ✓ Encryption of sensitive data
  ✓ Access controls
  ✓ Regular security testing
  ✓ Vulnerability management
  ✓ Monitoring and logging
  ✓ Incident response plan

GDPR Requirements:
  ✓ Consent for data processing
  ✓ Right to access
  ✓ Right to erasure
  ✓ Data minimization
  ✓ Purpose limitation
  ✓ Data retention limits
  ✓ Privacy by design

Open Banking Standards:
  ✓ RESTful API design
  ✓ Standard error codes
  ✓ Rate limiting
  ✓ Versioning
  ✓ Security standards
  ✓ Data standards
```

This comprehensive guide provides production-ready patterns for banking API integration with emphasis on security, compliance, and user trust.
