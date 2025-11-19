from flask import Flask, request, jsonify
from functools import wraps
import jwt

app = Flask(__name__)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return {'error': 'Unauthorized'}, 401
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            request.user_id = payload['sub']
        except:
            return {'error': 'Invalid token'}, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/accounts', methods=['GET'])
@require_auth
def list_accounts():
    return {'accounts': []}, 200

@app.route('/accounts/<account_id>', methods=['GET'])
@require_auth
def get_account(account_id):
    return {'accountId': account_id}, 200

@app.route('/payments', methods=['POST'])
@require_auth
def initiate_payment():
    data = request.json
    return {'paymentId': 'pay-001', 'status': 'PENDING'}, 201
