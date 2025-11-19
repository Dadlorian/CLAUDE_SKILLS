# Building a Banking API from Scratch

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│            Banking API Server                    │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────────────────────────────┐  │
│  │        API Gateway Layer                  │  │
│  │  - TLS/mTLS                              │  │
│  │  - Rate Limiting                         │  │
│  │  - Request Validation                    │  │
│  └──────────────────────────────────────────┘  │
│                    ▲                             │
│                    │                             │
│  ┌─────────────────┴──────────────────────────┐ │
│  │      Authentication Layer                  │ │
│  │  - OAuth 2.0 Server                       │ │
│  │  - Token Validation                       │ │
│  │  - Consent Management                     │ │
│  └──────────────────────────────────────────┘  │
│                    ▲                             │
│                    │                             │
│  ┌─────────────────┴──────────────────────────┐ │
│  │      Business Logic Layer                  │ │
│  │  - Account Service                        │ │
│  │  - Transaction Service                    │ │
│  │  - Payment Service                        │ │
│  │  - Balance Service                        │ │
│  └──────────────────────────────────────────┘  │
│                    ▲                             │
│                    │                             │
│  ┌─────────────────┴──────────────────────────┐ │
│  │      Data Access Layer                     │ │
│  │  - Account Repository                     │ │
│  │  - Transaction Repository                 │ │
│  │  - Cache Layer (Redis)                    │ │
│  │  - Database (PostgreSQL)                  │ │
│  └──────────────────────────────────────────┘  │
│                                                   │
└─────────────────────────────────────────────────┘
```

## Step 1: Set Up Project Structure

```bash
banking-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth2.py
│   │   └── consent.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── payments.py
│   │   └── balances.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   └── payment_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   └── payment.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations.py
│   └── security/
│       ├── __init__.py
│       ├── tls.py
│       └── validation.py
├── tests/
│   ├── test_accounts.py
│   ├── test_payments.py
│   └── test_security.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Step 2: Set Up Flask Application

```python
# app/main.py
from flask import Flask
from flask_cors import CORS
import logging

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])

    # Set up CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['ALLOWED_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Set up logging
    setup_logging(app)

    # Register blueprints
    from app.api import accounts_bp, transactions_bp, payments_bp
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(payments_bp)

    # Error handlers
    register_error_handlers(app)

    return app

def setup_logging(app):
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f'Server error: {error}')
        return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app = create_app('development')
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5000)
```

## Step 3: Set Up Authentication

```python
# app/auth/oauth2.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import uuid

oauth2_bp = Blueprint('auth', __name__, url_prefix='/auth')

class OAuthServer:
    def __init__(self, app):
        self.app = app
        self.tokens = {}  # In production, use database

    def create_authorization_code(self, client_id, user_id, scopes):
        """Generate authorization code"""
        code = str(uuid.uuid4())
        self.tokens[code] = {
            'client_id': client_id,
            'user_id': user_id,
            'scopes': scopes,
            'created_at': datetime.utcnow(),
            'expires_in': 600  # 10 minutes
        }
        return code

    def exchange_code_for_token(self, code, client_id, client_secret):
        """Exchange authorization code for access token"""
        if code not in self.tokens:
            raise ValueError('Invalid authorization code')

        token_data = self.tokens.pop(code)

        if token_data['client_id'] != client_id:
            raise ValueError('Client ID mismatch')

        # Generate access token (JWT)
        access_token = jwt.encode({
            'sub': token_data['user_id'],
            'client_id': client_id,
            'scopes': token_data['scopes'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, self.app.config['SECRET_KEY'], algorithm='HS256')

        # Generate refresh token
        refresh_token = str(uuid.uuid4())

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }

@oauth2_bp.route('/authorize', methods=['GET'])
def authorize():
    """OAuth authorization endpoint"""
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')

    # Validate client_id and redirect_uri
    # Redirect to login form (in real app)
    # User authenticates and grants consent
    # Generate authorization code

    auth_code = oauth_server.create_authorization_code(
        client_id, 'user-123', scope.split()
    )

    return {'code': auth_code, 'state': state}

@oauth2_bp.route('/token', methods=['POST'])
def token():
    """OAuth token endpoint"""
    grant_type = request.json.get('grant_type')

    if grant_type == 'authorization_code':
        code = request.json.get('code')
        client_id = request.json.get('client_id')
        client_secret = request.json.get('client_secret')

        try:
            tokens = oauth_server.exchange_code_for_token(
                code, client_id, client_secret
            )
            return jsonify(tokens), 200
        except ValueError as e:
            return {'error': str(e)}, 400

    return {'error': 'Unsupported grant type'}, 400
```

## Step 4: Set Up Database Models

```python
# app/models/account.py
from sqlalchemy import Column, String, Float, DateTime, Enum
from app.database import Base
from datetime import datetime
import enum

class AccountType(enum.Enum):
    CACC = "CACC"  # Current Account
    SVGS = "SVGS"  # Savings Account
    TRAD = "TRAD"  # Trading Account

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    iban = Column(String, unique=True, nullable=False)
    bban = Column(String, nullable=False)
    currency = Column(String, default='EUR')
    name = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.CACC)
    status = Column(String, default='ENABLED')
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'resourceId': self.id,
            'iban': self.iban,
            'bban': self.bban,
            'currency': self.currency,
            'name': self.name,
            'accountType': self.account_type.value,
            'status': self.status
        }
```

## Step 5: Set Up API Endpoints

```python
# app/api/accounts.py
from flask import Blueprint, request, jsonify, g
from app.auth.oauth2 import require_oauth
from app.services.account_service import AccountService

accounts_bp = Blueprint('accounts', __name__, url_prefix='/api/v1/accounts')
account_service = AccountService()

@accounts_bp.route('', methods=['GET'])
@require_oauth(['accounts:read'])
def list_accounts():
    """List user accounts"""
    user_id = g.user['sub']

    try:
        accounts = account_service.get_user_accounts(user_id)
        return jsonify({
            'accounts': [acc.to_dict() for acc in accounts]
        }), 200
    except Exception as e:
        return {'error': str(e)}, 500

@accounts_bp.route('/<account_id>', methods=['GET'])
@require_oauth(['accounts:read'])
def get_account(account_id):
    """Get specific account"""
    user_id = g.user['sub']

    try:
        account = account_service.get_account(user_id, account_id)
        if not account:
            return {'error': 'Account not found'}, 404

        return jsonify(account.to_dict()), 200
    except Exception as e:
        return {'error': str(e)}, 500

@accounts_bp.route('/<account_id>/balances', methods=['GET'])
@require_oauth(['accounts:read', 'balances:read'])
def get_balance(account_id):
    """Get account balance"""
    user_id = g.user['sub']

    try:
        balance = account_service.get_balance(user_id, account_id)
        return jsonify({
            'balances': [
                {
                    'balanceType': 'INTERIM_BOOKED',
                    'balanceAmount': {
                        'amount': str(balance),
                        'currency': 'EUR'
                    }
                }
            ]
        }), 200
    except Exception as e:
        return {'error': str(e)}, 500
```

## Step 6: Implement Business Logic

```python
# app/services/account_service.py
from app.models.account import Account
from app.database import db
import logging

logger = logging.getLogger(__name__)

class AccountService:
    def get_user_accounts(self, user_id):
        """Get all accounts for user"""
        try:
            accounts = db.session.query(Account).filter(
                Account.user_id == user_id,
                Account.status == 'ENABLED'
            ).all()

            logger.info(f'Retrieved {len(accounts)} accounts for user {user_id}')
            return accounts

        except Exception as e:
            logger.error(f'Error retrieving accounts: {e}')
            raise

    def get_account(self, user_id, account_id):
        """Get specific account"""
        try:
            account = db.session.query(Account).filter(
                Account.id == account_id,
                Account.user_id == user_id
            ).first()

            return account

        except Exception as e:
            logger.error(f'Error retrieving account: {e}')
            raise

    def get_balance(self, user_id, account_id):
        """Get account balance"""
        account = self.get_account(user_id, account_id)

        if not account:
            raise ValueError('Account not found')

        return account.balance

    def transfer_funds(self, from_account_id, to_account_id, amount):
        """Transfer funds between accounts"""
        try:
            from_account = db.session.query(Account).filter(
                Account.id == from_account_id
            ).first()

            to_account = db.session.query(Account).filter(
                Account.id == to_account_id
            ).first()

            if not from_account or not to_account:
                raise ValueError('Account not found')

            if from_account.balance < amount:
                raise ValueError('Insufficient funds')

            from_account.balance -= amount
            to_account.balance += amount

            db.session.commit()

            logger.info(f'Transferred {amount} from {from_account_id} to {to_account_id}')
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f'Transfer error: {e}')
            raise
```

## Step 7: Testing

```python
# tests/test_accounts.py
import unittest
from app.main import create_app
from app.database import db

class TestAccountsAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_list_accounts(self):
        """Test listing accounts"""
        response = self.client.get(
            '/api/v1/accounts',
            headers={'Authorization': 'Bearer test-token'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('accounts', response.json)

    def test_unauthorized_access(self):
        """Test that unauthorized access is rejected"""
        response = self.client.get('/api/v1/accounts')

        self.assertEqual(response.status_code, 401)
```

## Deployment Checklist

- [ ] Database set up and migrated
- [ ] Redis configured for caching
- [ ] TLS certificates generated
- [ ] OAuth clients registered
- [ ] Environment variables configured
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] Monitoring set up
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Tests passing
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] API documentation generated
- [ ] Runbooks created

## References

- Flask Documentation: https://flask.palletsprojects.com/
- OAuth 2.0: https://tools.ietf.org/html/rfc6749
- SQLAlchemy: https://www.sqlalchemy.org/
