# 3D Secure (3DS) Reference

## Overview

3D Secure is an authentication protocol that adds an extra layer of security to online credit and debit card transactions. It authenticates the cardholder at the issuing bank before the transaction is authorized at the network level.

**Current Version**: 3D Secure 2.0/2.2 (released 2016, updated 2021)
**Adoption**: ~80% of online merchants in developed countries
**Standards**: Managed by EMVCo (Visa, Mastercard, Amex, JCB, Discover)

## 3DS 1.0 (Legacy)

### Authentication Flow

```
1. Customer enters card information
2. Merchant detects 3DS-capable card
3. Merchant redirects to Access Control Server (ACS)
4. ACS displays password/challenge screen
5. Customer enters password
6. ACS validates password
7. ACS returns authentication result
8. Merchant receives authentication code
9. Merchant processes transaction with code
10. Authorization happens at network with proof of authentication

Characteristics:
- Static password authentication
- Customer friction (required to enter password)
- High confirmation requirement
- Scope Ambiguity (does not authenticate entire transaction)
- Legacy systems still supporting it
```

### Problems with 3DS 1.0

```
1. User Experience
   - Required password entry (friction)
   - Out-of-band authentication
   - Clunky modal experience
   - Drop-off rates: 20-40%

2. Security Limitations
   - Static passwords (easily guessed)
   - No device fingerprinting
   - No behavioral analysis
   - Limited data for fraud assessment

3. Mobile Issues
   - Redirect caused app drop-off
   - Not optimized for mobile
   - Poor UX on small screens
   - App switching friction

4. Liability Shift
   - Conditional liability shift
   - Only if authentication successful
   - Merchant still liable for some cases
```

## 3D Secure 2.0/2.2

### Modern Authentication

```
Risk-Based Authentication (RBA):
- Not all transactions require active authentication
- Low-risk transactions: Silent pass (no challenge)
- Medium-risk: Passive authentication (behavioral)
- High-risk: Active authentication (OTP, biometric)

Device Recognition:
- Device fingerprinting
- Behavioral analysis
- Location verification
- Velocity checks

Multi-Factor Authentication:
- Something you know: Password/PIN
- Something you have: Phone/Email
- Something you are: Biometric
- Combination of factors for high-risk
```

### 3DS 2.0 Data Elements

```
Device Information:
- Device ID
- Device fingerprint
- User agent
- IP address
- Device channel (app vs. browser)
- Screen resolution
- Timezone
- Browser language

Transaction Information:
- Amount
- Currency
- Timestamp
- Merchant category code
- Transaction ID
- Card data
- Delivery address
- Billing address

Customer Information:
- Account ID
- Account age
- Previous transactions
- Fraud history
- Payment method history
- Device history
- Location history

Shipping Information:
- Shipping address
- Shipping method
- Delivery time
- Type of goods
```

### Authentication Methods

```
Silent Authentication (No Customer Action):
- Device fingerprinting
- Behavioral analysis
- Transaction history
- Network intelligence
- Result: Automatic approval

OTP (One-Time Password):
- SMS to registered phone
- Email with code
- Authenticator app
- Push notification
- Customer must enter code
- One-time use only
- Typical window: 5-10 minutes

Biometric:
- Fingerprint recognition
- Face recognition
- Device-native biometric
- Fast and secure
- Growing availability

Decoupled Authentication:
- Authentication at bank (separate app/channel)
- Customer approves in their banking app
- More secure than OTP
- Better UX than modal
- Real-time decision
```

### Authentication Flow (3DS 2.0)

```
Step 1: Card Details Collection
- Customer enters card information
- Merchant collects device information
- Merchant fingerprints device

Step 2: Merchant Server to Payment Processor
POST /3ds/authentication
{
  "card_number": "4111111111111111",
  "expiry": "12/25",
  "amount": 100.00,
  "currency": "USD",
  "merchant_reference": "ORDER_12345",
  "device_channel": "browser",
  "device_fingerprint": {
    "browser_accept_header": "text/html,application/xhtml+xml,...",
    "browser_ip": "192.168.1.1",
    "browser_java_enabled": false,
    "browser_javascript_enabled": true,
    "browser_language": "en-US",
    "browser_color_depth": "24",
    "browser_screen_height": "1080",
    "browser_screen_width": "1920",
    "browser_tz": "-300",
    "browser_user_agent": "Mozilla/5.0..."
  }
}

Step 3: Payment Processor to ACS (Access Control Server)
- Processor sends authentication request to card network
- Card network routes to ACS (issuer's authentication server)
- ACS evaluates risk

Step 4: Risk Assessment at ACS
- Evaluate device fingerprint
- Check fraud patterns
- Analyze transaction
- Determine authentication level needed

Step 5a: Silent Authentication (Low Risk)
Response:
{
  "authentication_result": {
    "eci": "05",  // eCommerce Indicator (authenticated)
    "cavv": "jHn/VwAUAAFFCIGQQnsgEsAMSV4=",
    "threeds_server_trans_id": "edef48dae20e",
    "decision": "frictionless",
    "authentication_value": "eYpodHRwOi8vZXhhbXBsZS5jb20/"
  }
}
Result: Immediate approval, customer unaware

Step 5b: Challenge (High Risk)
Response:
{
  "authentication_result": {
    "threeds_server_trans_id": "edef48dae20e",
    "acsChallengeMandated": true,
    "acsURL": "https://acs.issuer.com/challenge",
    "decisison": "challenge",
    "challengeWindowSize": "04"  // 390x400 pixels
  }
}
Result: Customer directed to ACS challenge
- ACS displays OTP, biometric, or other challenge
- Customer completes authentication
- ACS sends result back to merchant

Step 6: Transaction Authorization
- Merchant uses 3DS result to authorize
- Network receives ECI (authentication proof)
- Authorization proceeds with liability shift

Step 7: Transaction Settlement
- Transaction settles normally
- Liability shift applied
- Chargeback protection in place
```

### Challenge Types

```
Out of Band (OOB):
- OTP via SMS
- OTP via Email
- Push notification approval
- Phone call verification

SMS OTP:
1. ACS initiates OTP generation
2. ACS sends SMS to cardholder
3. Cardholder receives code
4. Cardholder enters code at ACS
5. ACS validates code
6. ACS returns success to processor
7. Transaction authorized

Biometric:
1. ACS requests device biometric
2. Device prompts user (fingerprint/face)
3. Device captures biometric
4. Device validates locally
5. Device returns result to ACS
6. ACS validates
7. Transaction authorized

HTML Form:
1. ACS returns challenge form
2. Customer fills form (security questions)
3. ACS validates answers
4. ACS returns success
5. Transaction authorized
```

## Implementation

### Server-Side Implementation (Python)

```python
import requests
import json
from datetime import datetime
import uuid

class ThreeDSecureProcessor:
    def __init__(self, api_key, merchant_id):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.base_url = 'https://api.processor.com/3ds'

    def initiate_authentication(self, payment_data, device_info):
        """Initiate 3DS authentication"""

        # Create authentication request
        auth_request = {
            'threeDSRequestorID': self.merchant_id,
            'threeDSRequestorName': 'Example Merchant',
            'threeDSRequestorURL': 'https://example.com',
            'messageVersion': '2.2.0',
            'messageType': 'AReq',
            'deviceRenderingOptions': {
                'sdkInterface': 'both',  # or 'html', 'native'
                'sdkUiType': ['native', 'html']
            },
            'threeDSCompInd': 'Y',  # 3DS requestor completion indicator
            'acctType': '01',  # Personal account
            'acctInfo': {
                'chAccAgeInd': '01',  # Age of account (< 30 days)
                'acctCreate': datetime.now().isoformat(),
                'acctChange': datetime.now().isoformat(),
                'acctPwdChange': datetime.now().isoformat(),
                'acctNbPurchases24': 1,
                'acctOrderCount30Day': 1,
                'acctUnAuthAccess': 'N'
            },
            'browser': {
                'browserAcceptHeader': device_info['accept_header'],
                'browserIpAddress': device_info['ip_address'],
                'browserJavaEnabled': device_info['java_enabled'],
                'browserJavascriptEnabled': device_info['javascript_enabled'],
                'browserLanguage': device_info['language'],
                'browserColorDepth': device_info['color_depth'],
                'browserScreenHeight': device_info['screen_height'],
                'browserScreenWidth': device_info['screen_width'],
                'browserTimeZone': device_info['timezone'],
                'browserUserAgent': device_info['user_agent']
            },
            'purchase': {
                'purchAmount': str(int(payment_data['amount'] * 100)),
                'purchCurrency': '840',  # USD
                'purchExponent': '2',
                'purchDate': datetime.now().isoformat(),
                'transType': '01',  # Goods/services purchase
                'transChannel': '01',  # E-commerce
                'reOrdInd': 'N'  # Not a recurring transaction
            },
            'card': {
                'cardNumber': payment_data['card_number'],
                'cardExpiryDate': payment_data['expiry'],
                'cardSecurityCode': payment_data['cvv']
            },
            'billAddr': {
                'addrLine1': payment_data['billing_address'],
                'city': payment_data['billing_city'],
                'postCode': payment_data['billing_zip'],
                'country': '840'  # USA
            },
            'shipAddr': {
                'addrLine1': payment_data['shipping_address'],
                'city': payment_data['shipping_city'],
                'postCode': payment_data['shipping_zip'],
                'country': '840'  # USA
            },
            'shipAddressUsageInd': '01',  # Same as billing
            'shipNameIndicator': 'Y',
            'homePhone': {
                'cc': '1',
                'subscriber': payment_data.get('phone', '')
            },
            'mobilePhone': {
                'cc': '1',
                'subscriber': payment_data.get('mobile', '')
            },
            'email': payment_data.get('email', ''),
            'notificationURL': 'https://example.com/3ds-notification',
            'deviceChannel': 'browser',  # or 'app'
            'sdkAppID': ''  # For app-based
        }

        # Send to 3DS Server
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                f'{self.base_url}/authenticate',
                json=auth_request,
                headers=headers,
                timeout=10
            )

            result = response.json()

            # Check if challenge required
            if result.get('challengeIndicator') == 'Y':
                # Challenge required
                return {
                    'status': 'challenge_required',
                    'acs_url': result['acsURL'],
                    'challenge_window_size': result.get('challengeWindowSize', '04'),
                    'three_ds_server_trans_id': result['threeDSServerTransID'],
                    'aacs_trans_id': result.get('acsTransID')
                }
            else:
                # Frictionless flow (silent authentication)
                return {
                    'status': 'authenticated',
                    'eci': result.get('eci', '05'),
                    'cavv': result.get('cavv', ''),
                    'three_ds_server_trans_id': result['threeDSServerTransID'],
                    'authentication_value': result.get('authenticationValue', '')
                }

        except requests.exceptions.RequestException as e:
            # 3DS server unavailable, fail open or proceed without 3DS
            return {
                'status': 'error',
                'error': str(e),
                'proceed_without_3ds': True  # Consider fallback
            }

    def process_challenge_result(self, challenge_result):
        """Process result from ACS challenge"""

        # Validate signature
        signature_valid = self.validate_acs_signature(challenge_result)

        if not signature_valid:
            return {
                'status': 'invalid_signature',
                'authenticated': False
            }

        # Extract authentication data
        return {
            'status': 'authenticated',
            'eci': challenge_result.get('eci', '05'),
            'cavv': challenge_result.get('cavv', ''),
            'authentication_value': challenge_result.get('authenticationValue'),
            'three_ds_server_trans_id': challenge_result.get('threeDSServerTransID')
        }

    def validate_acs_signature(self, data):
        """Validate ACS signature for security"""
        # Implementation would use public key from network
        # Verify signature on challenge result
        return True  # Simplified

    def authorize_with_3ds(self, payment_data, authentication_result):
        """Authorize transaction with 3DS proof"""

        auth_request = {
            'amount': payment_data['amount'],
            'currency': payment_data['currency'],
            'card_token': payment_data['card_token'],
            'eci': authentication_result['eci'],  # Proof of authentication
            'cavv': authentication_result['cavv'],  # Cryptographic proof
            'threeds_version': '2.2.0',
            'merchant_reference': payment_data['reference']
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'{self.base_url}/authorize',
            json=auth_request,
            headers=headers
        )

        result = response.json()

        return {
            'authorized': result['status'] == 'approved',
            'transaction_id': result.get('transaction_id'),
            'authorization_code': result.get('auth_code'),
            'liability_shift': True,  # 3DS provides liability shift
            'eci': authentication_result['eci']
        }
```

### Client-Side Implementation (JavaScript)

```javascript
class ThreeDSecureClient {
  constructor(apiKey, merchantId) {
    this.apiKey = apiKey;
    this.merchantId = merchantId;
  }

  // Collect device information
  getDeviceInfo() {
    return {
      accept_header: navigator.language,
      ip_address: '0.0.0.0',  // Would be set by server
      java_enabled: navigator.javaEnabled(),
      javascript_enabled: true,
      language: navigator.language,
      color_depth: window.screen.colorDepth,
      screen_height: window.screen.height,
      screen_width: window.screen.width,
      timezone: new Date().getTimezoneOffset(),
      user_agent: navigator.userAgent,
      fingerprint: this.generateFingerprint()
    };
  }

  // Generate device fingerprint
  generateFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const text = 'Browser Fingerprint';

    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText(text, 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText(text, 4, 17);

    return canvas.toDataURL();
  }

  // Initiate 3DS authentication
  async authenticate(paymentData) {
    const deviceInfo = this.getDeviceInfo();

    // Call server endpoint
    const response = await fetch('/3ds/authenticate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_data: paymentData,
        device_info: deviceInfo
      })
    });

    const result = await response.json();

    if (result.status === 'challenge_required') {
      // Redirect to ACS or show iframe
      return this.handleChallenge(result);
    } else if (result.status === 'authenticated') {
      // Frictionless, proceed with authorization
      return this.authorizeTransaction(paymentData, result);
    } else {
      return this.handleError(result);
    }
  }

  // Handle ACS challenge
  async handleChallenge(challengeData) {
    // Create form and submit to ACS
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = challengeData.acs_url;
    form.style.display = 'none';

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'creq';
    input.value = challengeData.creq;

    form.appendChild(input);
    document.body.appendChild(form);

    // Optional: Show in iframe for better UX
    // const iframe = document.createElement('iframe');
    // iframe.src = challengeData.acs_url;
    // document.body.appendChild(iframe);

    form.submit();
  }

  // Authorize after authentication
  async authorizeTransaction(paymentData, authResult) {
    const response = await fetch('/payments/authorize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_data: paymentData,
        authentication: authResult
      })
    });

    return await response.json();
  }
}

// Usage
document.getElementById('pay-button').addEventListener('click', async () => {
  const client = new ThreeDSecureClient('API_KEY', 'MERCHANT_ID');

  const paymentData = {
    card_number: document.getElementById('card-number').value,
    expiry: document.getElementById('card-expiry').value,
    cvv: document.getElementById('card-cvv').value,
    amount: 100.00,
    currency: 'USD'
  };

  const result = await client.authenticate(paymentData);
  console.log('Payment result:', result);
});
```

## Liability Shift

### Chargeback Protection

```
Without 3DS:
- Liability: Merchant liable for fraud
- Chargeback code: 10.1 (Unauthorized use)
- Merchant absorbs loss: 100%

With 3DS (Successful Authentication):
- Liability: Card issuer liable
- Liability Shift: Merchant protected
- Merchant absorbs loss: 0% (typically)

With 3DS (Failed Authentication):
- Liability: Shared or merchant liable (varies)
- Challenge submitted but failed
- Reduced liability vs. no 3DS
- Chargeback code: Different (reduced liability)

Network Rules:
- Visa: Liability shift with valid ECI
- Mastercard: Liability shift with valid CAVV
- Amex: Similar liability protection
- Discover: Similar protection
```

## 3DS Adoption and Best Practices

### When to Require 3DS

```
Low Risk (No 3DS):
- Returning customer
- Low transaction amount (< $100)
- Repeat transactions
- Established payment method
- Same device/location

Medium Risk (Optional 3DS):
- New customer
- Moderate amount ($100-500)
- Different location
- Different device
- Payment method changing

High Risk (Require 3DS):
- High amount (> $500)
- High-risk category (electronics, gift cards)
- Multiple declines
- Multiple cards used
- Geographic mismatch
- VPN/Proxy detected
- Suspicious patterns

Regulatory Requirements:
- EU/UK: SCA (Strong Customer Auth) for most payments
- PCI-DSS: 3DS recommended for e-commerce
- Some regions: 3DS mandatory for certain amounts
```

### Optimization Strategies

```
Balance Security and Conversion:
- Use risk assessment to reduce friction
- Apply 3DS selectively
- Monitor false decline rates
- Optimize challenge types

Example Strategy:
1. Frictionless first (80% of transactions)
2. OTP challenge for medium risk
3. Biometric for high-value transactions
4. Fallback to old password for unsupported methods

Monitoring:
- Track 3DS decline rates
- Monitor conversion impact
- Measure liability shift benefit
- Balance cost vs. chargeback reduction
```

## 3DS 2.0 Ecosystem

### Network Support

```
Visa Secure:
- Visa's 3DS 2.0 implementation
- VTS (Visa Token Service) integration
- Global reach
- ECI values: 05, 06, 07

Mastercard Identity Check:
- Mastercard's 3DS 2.0
- MDES integration
- Device fingerprinting
- ECI values similar structure

American Express ID Check:
- Amex's 3DS variant
- Limited 3DS 2.0 implementation
- Direct issuer relationships
- Lower ECI standardization

Discover Secure:
- Discover's 3DS implementation
- Full 3DS 2.0 support
- Growing merchant adoption
```
