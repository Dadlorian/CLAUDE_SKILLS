# API Testing for Financial Systems

## Testing Pyramid

```
         Manual/
        Exploratory
         (10-15%)
            △
           / \
          /   \
         /  E2E \
        /  Tests \
       / (20-30%) \
      /____________\
          / \
         /   \
        / API \  Integration
       / Tests \   Tests
      /  (40%) \ (20%)
     /____________\
          / \
         /   \
        /Unit \
       /Tests \
      / (40%) \
     /____________\

Financial APIs need extra emphasis on:
- Security testing
- Integration testing (3rd party APIs)
- Compliance testing
- Performance/load testing
```

## Unit Testing

### Testing API Handlers
```python
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestPaymentAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.client = app.test_client()
        self.test_user = {
            "id": "user-123",
            "scope": "payments:write"
        }

    def test_create_payment_success(self):
        """Test successful payment creation"""
        payment_data = {
            "amount": "100.00",
            "currency": "EUR",
            "creditorIban": "IT60X0542811101000000123456",
            "reference": "Invoice 123"
        }

        response = self.client.post(
            '/payments',
            json=payment_data,
            headers={
                'Authorization': 'Bearer test-token',
                'Content-Type': 'application/json'
            }
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertIn('paymentId', data)
        self.assertEqual(data['status'], 'RCVD')

    def test_create_payment_insufficient_balance(self):
        """Test payment with insufficient funds"""
        payment_data = {
            "amount": "1000000.00",
            "currency": "EUR",
            "creditorIban": "IT60X0542811101000000123456"
        }

        with patch('payment_service.check_balance') as mock_balance:
            mock_balance.return_value = False

            response = self.client.post(
                '/payments',
                json=payment_data,
                headers={'Authorization': 'Bearer test-token'}
            )

            self.assertEqual(response.status_code, 402)

    def test_invalid_iban_format(self):
        """Test validation of IBAN"""
        payment_data = {
            "amount": "100.00",
            "currency": "EUR",
            "creditorIban": "INVALID"  # Not valid IBAN
        }

        response = self.client.post(
            '/payments',
            json=payment_data,
            headers={'Authorization': 'Bearer test-token'}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
```

## Integration Testing

### Testing API with Mocked Backend
```python
import responses
import requests

class TestBankIntegration(unittest.TestCase):
    @responses.activate
    def test_account_aggregation(self):
        """Test aggregating accounts from multiple banks"""

        # Mock Bank A API
        responses.add(
            responses.GET,
            'https://bank-a.com/api/accounts',
            json={
                "accounts": [
                    {"id": "acc-1", "iban": "DE89...", "balance": 1000}
                ]
            },
            status=200
        )

        # Mock Bank B API
        responses.add(
            responses.GET,
            'https://bank-b.com/api/accounts',
            json={
                "accounts": [
                    {"id": "acc-2", "iban": "IT60...", "balance": 500}
                ]
            },
            status=200
        )

        # Test aggregation
        aggregator = AccountAggregator()
        result = aggregator.get_all_accounts("user-123")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "acc-1")
        self.assertEqual(result[1]["id"], "acc-2")
```

## Contract Testing

### API Contract Tests
```python
from pact import Consumer, Provider

consumer = Consumer("FinanceApp")
provider = Provider("BankingAPI")

def test_get_accounts_contract():
    """Test API contract for accounts endpoint"""

    (consumer
     .given('accounts exist')
     .upon_receiving('a request for accounts')
     .with_request('get', '/accounts')
     .will_respond_with(200, body={
         "accounts": [
             {
                 "id": "acc-1",
                 "iban": "DE89...",
                 "currency": "EUR",
                 "balance": 1000.00
             }
         ]
     }))

    # Test with provider
    with consumer.pact_with(provider):
        # Make request
        response = requests.get("http://localhost:8000/accounts")

        # Verify response
        assert response.status_code == 200
        assert "accounts" in response.json()
```

## Security Testing

### OAuth Flow Testing
```python
class TestOAuthFlow(unittest.TestCase):
    def test_valid_authorization_code_flow(self):
        """Test complete OAuth authorization flow"""

        # 1. Get authorization URL
        auth_url = oauth_client.get_authorization_url(
            scope="accounts:read payments:write"
        )

        # 2. Simulate user authorization (in real browser)
        auth_code = self.simulate_user_authorization(auth_url)

        # 3. Exchange code for token
        token_response = oauth_client.exchange_code(auth_code)

        self.assertIn('access_token', token_response)
        self.assertIn('refresh_token', token_response)
        self.assertEqual(token_response['token_type'], 'Bearer')

    def test_invalid_client_credentials(self):
        """Test rejection of invalid client"""

        oauth_client_bad = OAuthClient(
            client_id="invalid-id",
            client_secret="invalid-secret"
        )

        with self.assertRaises(AuthenticationError):
            oauth_client_bad.exchange_code("valid-code")

    def test_expired_authorization_code(self):
        """Test that expired codes are rejected"""

        # Code expired after 10 minutes
        expired_code = "expired-code-from-10-minutes-ago"

        with self.assertRaises(InvalidGrantError):
            oauth_client.exchange_code(expired_code)

    def test_csrf_protection(self):
        """Test CSRF state parameter validation"""

        # Get auth URL with state
        auth_url = oauth_client.get_authorization_url()
        state = extract_state_from_url(auth_url)

        # Simulate callback with wrong state
        callback_url = f"https://app.example.com/callback?code=xyz&state=wrong-state"

        with self.assertRaises(CSRFValidationError):
            oauth_client.handle_callback(callback_url)
```

### TLS/Certificate Testing
```python
import ssl
import socket

class TestTLS(unittest.TestCase):
    def test_tls_1_2_minimum(self):
        """Verify TLS 1.2 is minimum"""

        context = ssl.create_default_context()

        # Try to use TLS 1.1 (should fail)
        context.minimum_version = ssl.TLSVersion.TLSv1_1

        with self.assertRaises(ssl.SSLError):
            socket.create_connection(
                ('api.example.com', 443),
                _create_socket_from_context=context
            )

    def test_certificate_validation(self):
        """Test certificate chain validation"""

        try:
            response = requests.get(
                'https://api.example.com/accounts',
                verify=True  # Enable certificate verification
            )
            # Should succeed with valid cert
            self.assertEqual(response.status_code, 200)
        except ssl.SSLError:
            self.fail("Valid certificate rejected")

    def test_self_signed_certificate_rejected(self):
        """Ensure self-signed certs are rejected"""

        with self.assertRaises(ssl.SSLError):
            requests.get(
                'https://self-signed.example.com',
                verify=True
            )
```

## Load Testing

### Performance Testing
```python
from locust import HttpUser, task, between

class APILoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(10)
    def get_accounts(self):
        """Load test account retrieval"""
        self.client.get(
            "/accounts",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(3)
    def create_payment(self):
        """Load test payment creation"""
        self.client.post(
            "/payments",
            json={
                "amount": "100.00",
                "currency": "EUR",
                "creditorIban": "IT60X0542811101000000123456"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(5)
    def get_transactions(self):
        """Load test transaction retrieval"""
        self.client.get(
            "/accounts/acc-123/transactions",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    def on_start(self):
        """Get auth token at start"""
        self.token = self.get_test_token()

    def get_test_token(self):
        """Obtain test token"""
        response = self.client.post(
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": "test-client",
                "client_secret": "test-secret"
            }
        )
        return response.json()["access_token"]
```

## Compliance Testing

### PSD2 Compliance Testing
```python
class TestPSD2Compliance(unittest.TestCase):
    def test_sca_required_for_payments(self):
        """Test Strong Customer Authentication is enforced"""

        # Payment without SCA should be rejected
        payment_data = {
            "amount": "100.00",
            "creditorIban": "IT60X0542811101000000123456"
        }

        response = self.client.post(
            '/payments',
            json=payment_data,
            headers={'Authorization': 'Bearer user-token-without-sca'}
        )

        # Should require SCA
        self.assertEqual(response.status_code, 403)
        self.assertIn('SCA', response.json['error'])

    def test_consent_validity(self):
        """Test that only valid consents are accepted"""

        # Use expired consent
        response = self.client.get(
            '/accounts',
            headers={
                'Authorization': 'Bearer user-token',
                'Consent-ID': 'expired-consent-123'
            }
        )

        self.assertEqual(response.status_code, 403)

    def test_rate_limiting_psd2(self):
        """Test PSD2 rate limit: 1 req/sec per account"""

        account_id = 'acc-123'

        # First request should succeed
        response1 = self.client.get(
            f'/accounts/{account_id}',
            headers={'Authorization': 'Bearer token'}
        )
        self.assertEqual(response1.status_code, 200)

        # Second request immediately after should be rate limited
        response2 = self.client.get(
            f'/accounts/{account_id}',
            headers={'Authorization': 'Bearer token'}
        )
        self.assertEqual(response2.status_code, 429)
```

## Webhook Testing

### Webhook Delivery Testing
```python
import json
import hmac
import hashlib
from flask import Flask

class TestWebhooks(unittest.TestCase):
    def test_webhook_delivery(self):
        """Test webhook is delivered correctly"""

        webhook_secret = "test-secret"

        # Create test event
        event = {
            "id": "evt_test_123",
            "type": "payment.completed",
            "data": {"paymentId": "pay-123"}
        }

        event_json = json.dumps(event)

        # Create signature
        signature = hmac.new(
            webhook_secret.encode(),
            event_json.encode(),
            hashlib.sha256
        ).hexdigest()

        # Send webhook
        response = requests.post(
            'https://app.example.com/webhooks',
            json=event,
            headers={
                'X-Webhook-Signature': f'sha256={signature}',
                'X-Webhook-Timestamp': datetime.utcnow().isoformat()
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_webhook_signature_validation(self):
        """Test invalid signatures are rejected"""

        event = {"id": "evt_123", "type": "payment.completed"}
        event_json = json.dumps(event)

        # Wrong signature
        response = requests.post(
            'https://app.example.com/webhooks',
            json=event,
            headers={
                'X-Webhook-Signature': 'sha256=wrongsignature',
                'X-Webhook-Timestamp': datetime.utcnow().isoformat()
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_webhook_retry_logic(self):
        """Test webhook retry on failure"""

        # Simulate endpoint that fails first time, succeeds second
        attempt_count = [0]

        def webhook_handler():
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                return 500  # Fail
            return 200  # Success

        # Send webhook with retry enabled
        result = send_webhook_with_retry(
            url='https://app.example.com/webhooks',
            event={},
            max_retries=3
        )

        self.assertTrue(result['delivered'])
        self.assertEqual(attempt_count[0], 2)
```

## Testing Checklist

- [ ] Unit tests for all functions
- [ ] Integration tests with mocked 3rd party APIs
- [ ] OAuth flow testing (authorization code, refresh, invalid tokens)
- [ ] TLS/certificate validation
- [ ] CSRF protection
- [ ] Rate limiting enforcement
- [ ] PSD2 compliance checks
- [ ] Webhook delivery and retry
- [ ] Error handling and edge cases
- [ ] Load testing (performance)
- [ ] Security testing (injection, XSS, etc.)
- [ ] Contract testing with bank APIs
- [ ] Compliance testing (GDPR, data retention)
- [ ] Pen testing and security audit
- [ ] End-to-end user flows

## References

- Testing Pyramid: https://martinfowler.com/articles/practical-test-pyramind.html
- API Testing Best Practices: https://swagger.io/tools/swagger-inspector/
- Security Testing: https://owasp.org/www-project-api-security/
- Load Testing: https://locust.io/
