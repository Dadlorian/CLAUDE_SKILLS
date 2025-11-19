"""
Banking API Example Implementation

Complete implementation of core banking API endpoints
"""

from flask import Flask, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import jwt
import json
from typing import Dict, List, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


# ============== Authentication ==============

def require_oauth(required_scopes):
    """OAuth decorator to protect endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Unauthorized'}), 401

            try:
                token = auth_header.split(' ')[1]
                decoded = jwt.decode(
                    token,
                    app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )

                # Check scopes
                user_scopes = decoded.get('scope', '').split()
                if not all(scope in user_scopes for scope in required_scopes):
                    return jsonify({'error': 'Insufficient scope'}), 403

                g.user = decoded
                g.token = token

            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ============== Data Models ==============

class Account:
    """Account data model"""
    def __init__(self, account_id, iban, currency, name, balance=0.0):
        self.id = account_id
        self.iban = iban
        self.currency = currency
        self.name = name
        self.balance = balance
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'resourceId': self.id,
            'iban': self.iban,
            'currency': self.currency,
            'name': self.name,
            'status': 'ENABLED'
        }


class Transaction:
    """Transaction data model"""
    def __init__(self, txn_id, account_id, amount, currency, creditor,
                 description, txn_date=None):
        self.id = txn_id
        self.account_id = account_id
        self.amount = amount
        self.currency = currency
        self.creditor = creditor
        self.description = description
        self.date = txn_date or datetime.utcnow()

    def to_dict(self):
        return {
            'transactionId': self.id,
            'bookingDate': self.date.isoformat(),
            'valueDate': self.date.isoformat(),
            'amount': self.amount,
            'currency': self.currency,
            'creditorName': self.creditor,
            'purpose': self.description,
            'status': 'BOOKED'
        }


# ============== In-Memory Storage (use DB in production) ==============

accounts_db = {}
transactions_db = {}
users_db = {
    'user-123': {
        'id': 'user-123',
        'username': 'john.doe',
        'accounts': ['acc-001', 'acc-002']
    }
}


# ============== Account Endpoints ==============

@app.route('/api/v1/accounts', methods=['GET'])
@require_oauth(['accounts:read'])
def list_accounts():
    """GET /accounts - List all user accounts"""
    user_id = g.user['sub']

    # Retrieve user's accounts
    user = users_db.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    accounts = [
        accounts_db[acc_id].to_dict()
        for acc_id in user['accounts']
        if acc_id in accounts_db
    ]

    return jsonify({'accounts': accounts}), 200


@app.route('/api/v1/accounts/<account_id>', methods=['GET'])
@require_oauth(['accounts:read'])
def get_account(account_id):
    """GET /accounts/{id} - Get specific account"""
    user_id = g.user['sub']

    user = users_db.get(user_id)
    if not user or account_id not in user['accounts']:
        return jsonify({'error': 'Account not found'}), 404

    account = accounts_db.get(account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    return jsonify({'account': account.to_dict()}), 200


@app.route('/api/v1/accounts/<account_id>/balances', methods=['GET'])
@require_oauth(['accounts:read', 'balances:read'])
def get_balance(account_id):
    """GET /accounts/{id}/balances - Get account balance"""
    user_id = g.user['sub']

    user = users_db.get(user_id)
    if not user or account_id not in user['accounts']:
        return jsonify({'error': 'Account not found'}), 404

    account = accounts_db.get(account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    balances = [
        {
            'balanceType': 'INTERIM_BOOKED',
            'balanceAmount': {
                'amount': str(account.balance),
                'currency': account.currency
            },
            'referenceDate': datetime.utcnow().isoformat()
        }
    ]

    return jsonify({'balances': balances}), 200


# ============== Transaction Endpoints ==============

@app.route('/api/v1/accounts/<account_id>/transactions', methods=['GET'])
@require_oauth(['accounts:read', 'transactions:read'])
def get_transactions(account_id):
    """GET /accounts/{id}/transactions - Get transactions"""
    user_id = g.user['sub']

    user = users_db.get(user_id)
    if not user or account_id not in user['accounts']:
        return jsonify({'error': 'Account not found'}), 404

    # Get transactions for account
    account_txns = [
        txn.to_dict()
        for txn in transactions_db.values()
        if txn.account_id == account_id
    ]

    return jsonify({
        'booked': account_txns,
        'pending': []
    }), 200


@app.route('/api/v1/accounts/<account_id>/transactions/<transaction_id>',
           methods=['GET'])
@require_oauth(['transactions:read'])
def get_transaction(account_id, transaction_id):
    """GET /accounts/{id}/transactions/{txn_id} - Get specific transaction"""
    user_id = g.user['sub']

    user = users_db.get(user_id)
    if not user or account_id not in user['accounts']:
        return jsonify({'error': 'Account not found'}), 404

    txn = transactions_db.get(transaction_id)
    if not txn or txn.account_id != account_id:
        return jsonify({'error': 'Transaction not found'}), 404

    return jsonify({'transactionDetails': txn.to_dict()}), 200


# ============== Payment Endpoints ==============

@app.route('/api/v1/payments', methods=['POST'])
@require_oauth(['payments:write'])
def create_payment():
    """POST /payments - Initiate payment"""
    user_id = g.user['sub']
    payment_data = request.json

    # Validate payment data
    required_fields = [
        'instructedAmount', 'debtorAccount', 'creditorAccount'
    ]

    for field in required_fields:
        if field not in payment_data:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': f'Missing required field: {field}'
            }), 400

    # Check debtor account access
    debtor_iban = payment_data['debtorAccount'].get('iban')
    user = users_db.get(user_id)

    debtor_account = next(
        (accounts_db[acc_id] for acc_id in user.get('accounts', [])
         if accounts_db.get(acc_id, Account(None, None, None, None)).iban == debtor_iban),
        None
    )

    if not debtor_account:
        return jsonify({'error': 'FORBIDDEN'}), 403

    # Check balance
    amount = float(payment_data['instructedAmount']['amount'])
    if debtor_account.balance < amount:
        return jsonify({'error': 'INSUFFICIENT_FUNDS'}), 402

    # Create payment record
    payment_id = f'pay-{len([p for p in transactions_db.keys() if p.startswith("pay-")])}'

    payment = {
        'paymentId': payment_id,
        'transactionStatus': 'RCVD',
        'amount': amount,
        'currency': payment_data['instructedAmount']['currency'],
        'createdAt': datetime.utcnow().isoformat(),
        'links': {
            'self': {'href': f'/api/v1/payments/{payment_id}'},
            'status': {'href': f'/api/v1/payments/{payment_id}/status'}
        }
    }

    # Store payment
    transactions_db[payment_id] = payment

    return jsonify(payment), 201


@app.route('/api/v1/payments/<payment_id>/status', methods=['GET'])
@require_oauth(['payments:read'])
def get_payment_status(payment_id):
    """GET /payments/{id}/status - Get payment status"""
    payment = transactions_db.get(payment_id)

    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    return jsonify({
        'paymentId': payment_id,
        'transactionStatus': payment.get('transactionStatus', 'COMC')
    }), 200


# ============== Health Check ==============

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============== Error Handlers ==============

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized'}), 401


@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden'}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ============== Sample Data ==============

def initialize_sample_data():
    """Initialize with sample data for testing"""
    # Create sample accounts
    accounts_db['acc-001'] = Account(
        'acc-001',
        'DE89370400440532013000',
        'EUR',
        'Salary Account',
        5000.00
    )

    accounts_db['acc-002'] = Account(
        'acc-002',
        'DE75512108001234567890',
        'EUR',
        'Savings Account',
        10000.00
    )

    # Create sample transactions
    transactions_db['txn-001'] = Transaction(
        'txn-001',
        'acc-001',
        -50.00,
        'EUR',
        'Cafe Espresso',
        'Coffee'
    )


if __name__ == '__main__':
    initialize_sample_data()
    app.run(
        ssl_context=('cert.pem', 'key.pem'),
        host='0.0.0.0',
        port=5000,
        debug=False
    )
