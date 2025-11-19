# Open Banking Integration Guide

## Integration Workflow

```
Your App
  │
  ├─→ 1. Redirect to Bank
  │     (OAuth authorization)
  │
  ├─→ 2. User Authenticates
  │     (Bank's login page)
  │
  ├─→ 3. Grant Consent
  │     (Data access approval)
  │
  ├─→ 4. Receive Auth Code
  │     (From bank redirect)
  │
  ├─→ 5. Exchange for Token
  │     (Backend call)
  │
  ├─→ 6. Access Bank API
  │     (Accounts, transactions)
  │
  └─→ 7. Display Data
        (In your app)
```

## Step 1: Register with Bank

### Registration Process
1. Create developer account on bank's portal
2. Register your application
3. Provide callback URLs
4. Receive client_id and client_secret
5. Download certificates if required (PSD2/FAPI)

### Required Information
```
Application Name: MyFinanceApp
Website: https://myapp.example.com
Callback URL: https://myapp.example.com/callback
Support Email: support@myapp.example.com
Logo: (200x200 PNG)
```

## Step 2: Implement OAuth Flow

```python
from flask import Flask, request, redirect, session
import requests
import secrets

app = Flask(__name__)

class BankOAuthIntegration:
    def __init__(self, bank_name, client_id, client_secret):
        self.bank_name = bank_name
        self.client_id = client_id
        self.client_secret = client_secret

        # Bank-specific endpoints
        self.banks = {
            'bbva': {
                'auth_url': 'https://api.bbva.com/oauth/authorize',
                'token_url': 'https://api.bbva.com/oauth/token',
                'api_url': 'https://api.bbva.com/v1'
            },
            'santander': {
                'auth_url': 'https://auth.api.santander.com/oauth/authorize',
                'token_url': 'https://auth.api.santander.com/oauth/token',
                'api_url': 'https://api.santander.com/v1'
            },
            'bnp': {
                'auth_url': 'https://api.bnpparibas.com/authorize',
                'token_url': 'https://api.bnpparibas.com/token',
                'api_url': 'https://api.bnpparibas.com/v1'
            }
        }

    def get_authorization_url(self, scope, state=None):
        """Generate authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)

        bank_config = self.banks[self.bank_name]

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': 'https://myapp.example.com/callback',
            'state': state
        }

        return f"{bank_config['auth_url']}?{urlencode(params)}", state

    def exchange_code(self, code):
        """Exchange authorization code for token"""
        bank_config = self.banks[self.bank_name]

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'https://myapp.example.com/callback'
        }

        response = requests.post(
            bank_config['token_url'],
            data=data,
            verify='ca-cert.pem'
        )

        return response.json()

@app.route('/login/<bank_name>')
def login(bank_name):
    """Initiate login with bank"""
    oauth = BankOAuthIntegration(
        bank_name,
        app.config[f'{bank_name.upper()}_CLIENT_ID'],
        app.config[f'{bank_name.upper()}_CLIENT_SECRET']
    )

    auth_url, state = oauth.get_authorization_url(
        scope='accounts:read transactions:read'
    )

    session['oauth_state'] = state
    session['bank_name'] = bank_name

    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')

    # Verify state
    if state != session.get('oauth_state'):
        return 'Invalid state parameter', 400

    bank_name = session.get('bank_name')

    oauth = BankOAuthIntegration(
        bank_name,
        app.config[f'{bank_name.upper()}_CLIENT_ID'],
        app.config[f'{bank_name.upper()}_CLIENT_SECRET']
    )

    token_response = oauth.exchange_code(code)

    # Store token (securely!)
    session['access_token'] = token_response['access_token']
    session['refresh_token'] = token_response['refresh_token']

    return redirect('/dashboard')
```

## Step 3: Access Account Information

```python
class BankAPIClient:
    def __init__(self, bank_name, access_token):
        self.bank_name = bank_name
        self.access_token = access_token

        self.banks = {
            'bbva': {
                'api_url': 'https://api.bbva.com/v1'
            },
            'santander': {
                'api_url': 'https://api.santander.com/v1'
            },
            'bnp': {
                'api_url': 'https://api.bnpparibas.com/v1'
            }
        }

    def get_accounts(self):
        """Fetch user accounts"""
        bank_config = self.banks[self.bank_name]

        response = requests.get(
            f"{bank_config['api_url']}/accounts",
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            },
            verify='ca-cert.pem'
        )

        if response.status_code == 200:
            return response.json()['accounts']
        else:
            raise Exception(f"Error: {response.status_code}")

    def get_account_balance(self, account_id):
        """Get account balance"""
        bank_config = self.banks[self.bank_name]

        response = requests.get(
            f"{bank_config['api_url']}/accounts/{account_id}/balances",
            headers={'Authorization': f'Bearer {self.access_token}'},
            verify='ca-cert.pem'
        )

        if response.status_code == 200:
            balances = response.json()['balances']
            # Find booked balance
            for balance in balances:
                if balance['balanceType'] == 'INTERIM_BOOKED':
                    return balance['balanceAmount']
        else:
            raise Exception(f"Error: {response.status_code}")

    def get_transactions(self, account_id, start_date, end_date):
        """Fetch transactions"""
        bank_config = self.banks[self.bank_name]

        params = {
            'dateFrom': start_date.isoformat(),
            'dateTo': end_date.isoformat()
        }

        response = requests.get(
            f"{bank_config['api_url']}/accounts/{account_id}/transactions",
            headers={'Authorization': f'Bearer {self.access_token}'},
            params=params,
            verify='ca-cert.pem'
        )

        if response.status_code == 200:
            return response.json().get('booked', [])
        else:
            raise Exception(f"Error: {response.status_code}")

@app.route('/dashboard')
def dashboard():
    """Display aggregated data"""
    access_token = session.get('access_token')
    bank_name = session.get('bank_name')

    client = BankAPIClient(bank_name, access_token)

    try:
        accounts = client.get_accounts()
        balances = {
            acc['id']: client.get_account_balance(acc['id'])
            for acc in accounts
        }

        return render_template('dashboard.html', accounts=accounts, balances=balances)
    except Exception as e:
        return f"Error: {e}", 500
```

## Step 4: Handle Consent

### Consent Management
```python
class ConsentManager:
    def create_consent(self, bank_name, user_id, scopes):
        """Create consent record"""
        consent = {
            'id': str(uuid.uuid4()),
            'bank': bank_name,
            'user_id': user_id,
            'scopes': scopes,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=90),
            'status': 'ACTIVE'
        }

        # Store in database
        db.consents.insert_one(consent)

        return consent['id']

    def revoke_consent(self, consent_id):
        """Revoke consent"""
        db.consents.update_one(
            {'id': consent_id},
            {'$set': {'status': 'REVOKED'}}
        )

    def is_consent_valid(self, consent_id):
        """Check if consent is still valid"""
        consent = db.consents.find_one({'id': consent_id})

        if not consent:
            return False

        if consent['status'] != 'ACTIVE':
            return False

        if consent['expires_at'] < datetime.utcnow():
            return False

        return True

@app.route('/consent/revoke/<consent_id>', methods=['POST'])
def revoke_consent(consent_id):
    """Allow user to revoke consent"""
    consent_manager = ConsentManager()
    consent_manager.revoke_consent(consent_id)

    return {'status': 'revoked'}, 200
```

## Step 5: Multi-Bank Aggregation

```python
class MultiBANKAggregator:
    def __init__(self):
        self.banks = ['bbva', 'santander', 'bnp']

    def get_all_accounts(self, user_id):
        """Get accounts from all connected banks"""
        all_accounts = {}

        for bank_name in self.banks:
            token = self.get_user_token_for_bank(user_id, bank_name)

            if not token:
                all_accounts[bank_name] = {'status': 'not_connected'}
                continue

            try:
                client = BankAPIClient(bank_name, token)
                accounts = client.get_accounts()

                all_accounts[bank_name] = {
                    'status': 'connected',
                    'accounts': accounts
                }
            except Exception as e:
                all_accounts[bank_name] = {
                    'status': 'error',
                    'error': str(e)
                }

        return all_accounts

    def get_total_balance(self, user_id, currency='EUR'):
        """Calculate total balance across all banks"""
        all_accounts = self.get_all_accounts(user_id)
        total_balance = 0.0

        for bank_name, bank_data in all_accounts.items():
            if bank_data['status'] != 'connected':
                continue

            token = self.get_user_token_for_bank(user_id, bank_name)
            client = BankAPIClient(bank_name, token)

            for account in bank_data['accounts']:
                balance_info = client.get_account_balance(account['id'])

                # Convert to target currency if needed
                amount = float(balance_info['amount'])

                if balance_info['currency'] != currency:
                    amount = self.convert_currency(
                        amount,
                        balance_info['currency'],
                        currency
                    )

                total_balance += amount

        return total_balance
```

## Step 6: Error Handling

```python
class BankAPIException(Exception):
    """Base exception for bank API errors"""
    pass

class AuthenticationError(BankAPIException):
    """Authentication failed"""
    pass

class InsufficientScopeError(BankAPIException):
    """User hasn't granted required scopes"""
    pass

class RateLimitError(BankAPIException):
    """Rate limit exceeded"""
    pass

def handle_bank_api_error(response):
    """Handle different error responses"""
    if response.status_code == 401:
        raise AuthenticationError("Token expired or invalid")

    if response.status_code == 403:
        raise InsufficientScopeError("Insufficient permissions")

    if response.status_code == 429:
        raise RateLimitError("Rate limit exceeded")

    if response.status_code >= 500:
        raise BankAPIException(f"Bank API error: {response.status_code}")

    raise BankAPIException(f"Error: {response.status_code}")
```

## Step 7: Testing Integration

```python
import responses

@responses.activate
def test_oauth_flow():
    """Test OAuth flow"""

    # Mock authorization endpoint
    responses.add(
        responses.POST,
        'https://api.bbva.com/oauth/token',
        json={
            'access_token': 'test-access-token',
            'refresh_token': 'test-refresh-token',
            'token_type': 'Bearer'
        },
        status=200
    )

    # Mock accounts endpoint
    responses.add(
        responses.GET,
        'https://api.bbva.com/v1/accounts',
        json={
            'accounts': [
                {
                    'id': 'acc-1',
                    'iban': 'ES9121000418450200051332',
                    'currency': 'EUR'
                }
            ]
        },
        status=200
    )

    # Test OAuth exchange
    oauth = BankOAuthIntegration('bbva', 'test-id', 'test-secret')
    tokens = oauth.exchange_code('test-code')

    assert tokens['access_token'] == 'test-access-token'

    # Test API access
    client = BankAPIClient('bbva', tokens['access_token'])
    accounts = client.get_accounts()

    assert len(accounts) == 1
    assert accounts[0]['id'] == 'acc-1'
```

## Troubleshooting

### Common Issues

1. **Invalid redirect_uri**: Ensure exact match with registered
2. **Token expired**: Implement refresh token logic
3. **Rate limited**: Add exponential backoff
4. **Insufficient scopes**: Ask user to re-authenticate
5. **mTLS certificate errors**: Ensure certificates are valid

## Next Steps

1. Test with sandbox environment
2. Get API certification from banks
3. Handle data normalization
4. Implement caching strategy
5. Set up monitoring and alerting
6. Deploy to production

## References

- Bank API Documentation: Check specific bank's developer portal
- OAuth 2.0: https://tools.ietf.org/html/rfc6749
- PSD2: https://www.eba.europa.eu/
