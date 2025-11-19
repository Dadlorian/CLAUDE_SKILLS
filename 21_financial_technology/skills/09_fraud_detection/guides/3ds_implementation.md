# 3D Secure Implementation Guide

## Integration Overview

### 3DS Flow Architecture
```
Merchant System
    ↓
Payment Gateway (initiates 3DS check)
    ↓
Directory Server (routes to right ACS)
    ↓
Card Issuer ACS (performs authentication)
    ↓
Response back to Merchant
    ↓
Transaction Processing
```

## Client-Side Implementation

### JavaScript Integration
```html
<!-- 3D Secure 2.0 Implementation -->
<form id="payment-form">
  <input type="hidden" id="card-token" />
  <input type="hidden" id="device-channel" />

  <button type="submit">Complete Payment</button>
</form>

<script>
// Initialize 3DS
const threeds2 = new ThreeDS2({
  merchantId: 'your_merchant_id',
  messageVersion: '2.2.0',
  serverTransactionId: transactionId
});

// Collect device data
const deviceData = {
  browserUserAgent: navigator.userAgent,
  browserAcceptHeader: 'text/html',
  browserJavaEnabled: navigator.javaEnabled(),
  browserLanguage: navigator.language,
  browserColorDepth: window.screen.colorDepth,
  browserScreenHeight: window.screen.height,
  browserScreenWidth: window.screen.width,
  browserTimeZoneOffset: new Date().getTimezoneOffset(),
  ipAddress: getClientIP()
};

// Handle authentication
document.getElementById('payment-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  // Initiate 3DS
  const authResult = await threeds2.authenticate({
    amount: document.getElementById('amount').value,
    currency: 'USD',
    cardToken: document.getElementById('card-token').value,
    deviceData: deviceData
  });

  if (authResult.challengeRequired) {
    // Show challenge to user
    showAuthenticationChallenge(authResult);
  } else {
    // Frictionless - proceed
    submitTransaction(authResult.cavv);
  }
});

function showAuthenticationChallenge(authResult) {
  // Display challenge to user based on method
  if (authResult.method === 'biometric') {
    // Prompt for biometric
    promptBiometric();
  } else if (authResult.method === 'otp') {
    // Show OTP entry
    showOTPEntry();
  } else {
    // Show password entry
    showPasswordEntry();
  }
}
</script>
```

## Server-Side Implementation

### Payment Gateway Integration
```python
from threeds import ThreeDSProcessor

class ThreeDSHandler:
    def __init__(self, gateway_credentials):
        self.processor = ThreeDSProcessor(gateway_credentials)

    def initiate_3ds_authentication(self, transaction):
        """Initiate 3DS authentication"""
        auth_request = {
            'amount': transaction['amount'],
            'currency': transaction['currency'],
            'cardToken': transaction['card_token'],
            'merchantReference': transaction['order_id'],

            # Device data from client
            'deviceData': transaction['device_data'],

            # 3DS specific
            'threeDSMethodCompletionIndicator': 'Y',  # Method performed
            'threeDSRequestorAuthenticationIndicator': '01',  # Payment transaction
            'threeDSRequestorChallengeIndicator': '02',  # No preference

            # Customer/Order Info
            'billAddressMatch': 'Y' if (
                transaction['billing_address'] ==
                transaction['shipping_address']
            ) else 'N',

            'accountType': '01',  # Personal
            'accountChangeIndicator': self._get_account_change(transaction),
            'accountPwdChangeIndicator': self._get_password_change(
                transaction
            ),

            # Transaction Info
            'purchaseType': '01',  # Goods/Services
            'shippingIndicator': self._get_shipping_indicator(transaction),
            'deliveryTimeFrame': '01'  # Electronic delivery
        }

        # Send to processor
        response = self.processor.authenticate(auth_request)

        return self._process_response(response)

    def process_authentication_response(self, auth_response):
        """Process ACS response"""
        # Extract authentication result
        authentication_status = auth_response.get('transStatus')

        result = {
            'authenticated': authentication_status == 'Y',
            'cavv': auth_response.get('cavv'),
            'eci': auth_response.get('eCI'),
            'transaction_id': auth_response.get('transactionId'),
            'status': authentication_status
        }

        # Status interpretation
        if authentication_status == 'Y':
            result['message'] = 'Successfully authenticated'
            result['liability_shift'] = True
        elif authentication_status == 'N':
            result['message'] = 'Authentication failed'
            result['liability_shift'] = False
        elif authentication_status == 'U':
            result['message'] = 'Authentication unavailable'
            result['liability_shift'] = False
        elif authentication_status == 'A':
            result['message'] = 'Authentication attempted'
            result['liability_shift'] = True  # Partial shift

        return result

    def _process_response(self, response):
        """Process ACS response"""
        if response['challengeRequired']:
            return {
                'status': 'challenge_required',
                'challenge_url': response['challenge_url'],
                'challenge_token': response['challenge_token'],
                'method': response['authenticationMethod']
            }
        else:
            return {
                'status': 'frictionless',
                'cavv': response['cavv'],
                'eci': response['eCI'],
                'authentication_status': response['transStatus']
            }

    def _get_account_change(self, transaction):
        """Determine account change indicator"""
        customer = self.get_customer(transaction['customer_id'])
        days_since_change = (
            datetime.now() - customer['last_account_change']
        ).days

        if days_since_change < 30:
            return '02'  # Changed during this transaction
        elif days_since_change < 60:
            return '03'  # Changed in last 30-60 days
        else:
            return '01'  # Not changed
```

## Risk-Based Authentication Configuration

### Frictionless vs Challenge Rules
```python
class RiskBasedAuthenticationEngine:
    def should_challenge_user(self, transaction, risk_score):
        """Determine if user authentication challenge needed"""
        # Low risk - frictionless (no challenge)
        if risk_score < 0.2:
            return False, 'low_risk_frictionless'

        # Medium risk - optional challenge
        if risk_score < 0.5:
            return False, 'medium_risk_no_challenge'

        # Medium-high risk - challenge recommended
        if risk_score < 0.7:
            return True, 'challenge_recommended'

        # High risk - challenge required
        return True, 'high_risk_challenge_required'

    def configure_challenge_parameters(self, transaction, risk_factors):
        """Configure authentication challenge parameters"""
        config = {
            'challengeWindowSize': '05',  # 100% of device
            'challengeIndicator': '04',   # Challenge requested
            'threeDSRequestorChallengeIndicator': '04'
        }

        # Adjust challenge difficulty based on risk
        if risk_factors.get('high_velocity'):
            config['authenticationMethod'] = 'otp'  # OTP for velocity
        elif risk_factors.get('new_device'):
            config['authenticationMethod'] = 'biometric'  # Biometric for new device
        elif risk_factors.get('large_amount'):
            config['authenticationMethod'] = 'password'  # Password for large amounts

        return config
```

## Exemption Handling

### Low-Value Exemption
```python
def apply_low_value_exemption(transaction):
    """Check if transaction qualifies for low-value exemption"""
    # Soft limit: €30
    if transaction['amount'] < 30:
        return {
            'exemption_type': 'low_value',
            'skip_3ds': True,
            'require_fraud_check': False
        }

    # Hard limit: Some networks require 3DS above threshold
    if transaction['amount'] > 250:
        return {
            'exemption_type': 'none',
            'skip_3ds': False,
            'require_fraud_check': True
        }

    return {
        'exemption_type': 'none',
        'skip_3ds': False,
        'require_fraud_check': True
    }
```

### Trusted Merchant Exemption
```python
def apply_trusted_merchant_exemption(merchant_id, transaction):
    """Check if merchant qualifies for exemption"""
    merchant = get_merchant(merchant_id)

    # Criteria
    is_trusted = (
        merchant.get('chargeback_rate', 1.0) < 0.01 and  # < 1% chargebacks
        merchant.get('fraud_rate', 1.0) < 0.005 and  # < 0.5% fraud
        merchant.get('track_record_months', 0) > 12  # > 12 months
    )

    if is_trusted:
        return {
            'exemption_type': 'trusted_merchant',
            'skip_3ds': True,
            'reason': 'Merchant has excellent track record'
        }

    return {
        'exemption_type': 'none',
        'skip_3ds': False
    }
```

## Monitoring 3DS Performance

### Key Metrics
```python
class ThreeDSMonitoring:
    def get_3ds_metrics(self, period_days=30):
        """Get 3DS performance metrics"""
        start_date = datetime.now() - timedelta(days=period_days)

        transactions = self.db.get_transactions(since=start_date)
        threeds_transactions = [
            t for t in transactions if t.get('threeds_version')
        ]

        # Calculate metrics
        metrics = {
            'total_3ds_transactions': len(threeds_transactions),
            'frictionless_rate': self._calculate_frictionless_rate(
                threeds_transactions
            ),
            'challenge_rate': self._calculate_challenge_rate(
                threeds_transactions
            ),
            'decline_rate': self._calculate_decline_rate(
                threeds_transactions
            ),

            # Authentication methods
            'authentication_methods': self._analyze_auth_methods(
                threeds_transactions
            ),

            # Performance impact
            'conversion_impact': self._analyze_conversion_impact(
                threeds_transactions
            ),

            # Chargeback impact
            'chargeback_reduction': self._calculate_chargeback_reduction(
                threeds_transactions
            )
        }

        return metrics

    def _calculate_frictionless_rate(self, transactions):
        """% of transactions processed without challenge"""
        frictionless = sum(
            1 for t in transactions
            if t.get('threeds_result') == 'frictionless'
        )

        return frictionless / len(transactions) if transactions else 0

    def _calculate_challenge_rate(self, transactions):
        """% of transactions requiring challenge"""
        challenged = sum(
            1 for t in transactions
            if t.get('threeds_result') == 'challenged'
        )

        return challenged / len(transactions) if transactions else 0

    def _analyze_auth_methods(self, transactions):
        """Analyze authentication methods used"""
        methods = defaultdict(int)

        for t in transactions:
            method = t.get('threeds_auth_method')
            if method:
                methods[method] += 1

        return dict(methods)

    def _analyze_conversion_impact(self, transactions):
        """Measure impact on conversion rates"""
        conversion_by_method = {}

        for method in ['frictionless', 'challenged', 'declined']:
            method_txns = [
                t for t in transactions
                if t.get('threeds_result') == method
            ]

            if method_txns:
                completed = sum(
                    1 for t in method_txns
                    if t['status'] == 'completed'
                )

                conversion = completed / len(method_txns)
                conversion_by_method[method] = conversion

        return conversion_by_method

    def _calculate_chargeback_reduction(self, transactions):
        """Measure chargeback reduction from 3DS"""
        # Chargebacks on 3DS transactions
        threeds_chargebacks = sum(
            1 for t in transactions
            if t.get('chargeback') == True
        )

        # Chargebacks without 3DS (estimated based on historical)
        without_threeds_chargebacks = (
            len(transactions) * 0.005  # Estimated 0.5% without 3DS
        )

        # Reduction percentage
        reduction = (
            (without_threeds_chargebacks - threeds_chargebacks) /
            without_threeds_chargebacks * 100
        )

        return {
            'actual_chargebacks': threeds_chargebacks,
            'estimated_without_3ds': without_threeds_chargebacks,
            'reduction_percentage': reduction
        }
```

## Troubleshooting Common Issues

### Challenge Abandonment
```python
def analyze_challenge_abandonment(period_days=30):
    """Analyze why users abandon authentication"""
    start_date = datetime.now() - timedelta(days=period_days)

    challenged_txns = get_challenged_transactions(since=start_date)

    completed = sum(1 for t in challenged_txns if t['status'] == 'completed')
    abandoned = len(challenged_txns) - completed

    reasons = {
        'timeout': sum(1 for t in challenged_txns if t.get('timeout')),
        'user_cancel': sum(1 for t in challenged_txns if t.get('user_cancelled')),
        'technical_error': sum(1 for t in challenged_txns if t.get('error')),
        'unknown': abandoned - sum([...])  # Other reasons
    }

    return {
        'total_challenged': len(challenged_txns),
        'completed': completed,
        'abandoned': abandoned,
        'abandonment_rate': abandoned / len(challenged_txns),
        'abandon_reasons': reasons
    }
```

## Best Practices

1. **Frictionless First**: Minimize challenges for low-risk
2. **Fast Fallback**: Quick response if ACS unavailable
3. **Device Data**: Collect comprehensive device info
4. **Monitoring**: Track frictionless rate and conversions
5. **Testing**: Thoroughly test with test cards
6. **Compliance**: Follow network compliance rules
7. **Performance**: Minimize 3DS latency
8. **Recovery**: Have fallback for failed authentications
