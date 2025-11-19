# Device Intelligence Guide

## Device Fingerprinting Implementation

### JavaScript Fingerprinting
```javascript
// Comprehensive device fingerprinting
class DeviceFingerprinter {
  constructor() {
    this.fingerprint = this.generateFingerprint();
  }

  generateFingerprint() {
    const fp = {
      // Browser
      userAgent: navigator.userAgent,
      language: navigator.language,
      languages: navigator.languages,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      timeOffset: new Date().getTimezoneOffset(),

      // Screen
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      screenDepth: window.screen.colorDepth,
      screenPixelDepth: window.screen.pixelDepth,
      screenOrientation: window.screen.orientation?.type,

      // Device
      deviceMemory: navigator.deviceMemory,
      hardwareConcurrency: navigator.hardwareConcurrency,
      maxTouchPoints: navigator.maxTouchPoints,

      // Canvas (GPU Fingerprinting)
      canvasFingerprint: this.getCanvasFingerprint(),

      // WebGL
      webglFingerprint: this.getWebGLFingerprint(),

      // Fonts
      installedFonts: this.detectFonts(),

      // Plugins
      plugins: this.getPluginList(),

      // Storage
      localStorage: this.testStorage('localStorage'),
      sessionStorage: this.testStorage('sessionStorage'),
      indexedDB: this.testIndexedDB(),

      // Battery
      batteryLevel: this.getBatteryLevel(),

      // Network
      connectionType: navigator.connection?.effectiveType,
      downlink: navigator.connection?.downlink,
      rtt: navigator.connection?.rtt
    };

    return this.hashFingerprint(fp);
  }

  getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px "Arial"';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Browser Fingerprint', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Browser Fingerprint', 4, 17);

    return canvas.toDataURL();
  }

  getWebGLFingerprint() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl');
    if (!gl) return 'unknown';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

    return `${vendor}|${renderer}`;
  }

  detectFonts() {
    const baseFonts = ['monospace', 'sans-serif', 'serif'];
    const testFonts = [
      'Arial', 'Verdana', 'Times New Roman',
      'Courier New', 'Georgia', 'Palatino'
    ];

    const detected = [];
    for (const font of testFonts) {
      if (this.isFontInstalled(font, baseFonts)) {
        detected.push(font);
      }
    }
    return detected;
  }

  isFontInstalled(fontName, baseFonts) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const text = 'mmmmmmmmmmlli';
    const textSize = '72px';

    // Get baseline width
    ctx.font = `${textSize} ${baseFonts[0]}`;
    const baselineWidth = ctx.measureText(text).width;

    // Test font
    ctx.font = `${textSize} ${fontName}, ${baseFonts[0]}`;
    const testWidth = ctx.measureText(text).width;

    return baselineWidth !== testWidth;
  }

  getPluginList() {
    const plugins = [];
    for (let i = 0; i < navigator.plugins.length; i++) {
      plugins.push({
        name: navigator.plugins[i].name,
        version: navigator.plugins[i].version,
        description: navigator.plugins[i].description
      });
    }
    return plugins;
  }

  testStorage(type) {
    try {
      const storage = window[type];
      storage.setItem('test', 'test');
      storage.removeItem('test');
      return true;
    } catch (e) {
      return false;
    }
  }

  testIndexedDB() {
    try {
      return !!indexedDB;
    } catch (e) {
      return false;
    }
  }

  getBatteryLevel() {
    if (navigator.getBattery) {
      return navigator.getBattery().then(battery => battery.level);
    }
    return null;
  }

  hashFingerprint(fp) {
    // Hash the entire fingerprint object
    const str = JSON.stringify(fp);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16);
  }
}

// Usage
const fingerprinter = new DeviceFingerprinter();
console.log('Device Fingerprint:', fingerprinter.fingerprint);
```

## Server-Side Device Identification

### TLS Fingerprinting
```python
import hashlib
from collections import defaultdict

class TLSFingerprinter:
    """
    Analyze TLS handshake characteristics
    """

    def extract_tls_signature(self, request_headers):
        """Extract device signature from TLS details"""
        signature = {
            'tls_version': self._get_tls_version(request_headers),
            'cipher_suites': self._get_cipher_suites(request_headers),
            'elliptic_curves': self._get_elliptic_curves(request_headers),
            'signature_algorithms': self._get_signature_algorithms(
                request_headers
            ),
            'extensions': self._get_extensions(request_headers),
            'certificate_chain': self._get_certificate_chain(
                request_headers
            )
        }

        return self._hash_signature(signature)

    def _get_tls_version(self, headers):
        return headers.get('SSL-Version', 'unknown')

    def _get_cipher_suites(self, headers):
        # Extract from SSL_CIPHER and similar headers
        ciphers = headers.get('SSL-Cipher', '').split(',')
        return ciphers

    def _get_elliptic_curves(self, headers):
        return headers.get('X-TLS-Curves', '').split(',')

    def _get_signature_algorithms(self, headers):
        return headers.get('X-Signature-Algs', '').split(',')

    def _get_extensions(self, headers):
        return {
            'server_name': 'server_name_indication' in str(headers),
            'supported_groups': 'supported_groups' in str(headers),
            'ec_point_formats': 'ec_point_formats' in str(headers),
            'application_layer_protocol': (
                'application_layer_protocol_negotiation' in str(headers)
            )
        }

    def _get_certificate_chain(self, headers):
        # Extract certificate details
        return {
            'issuer': headers.get('SSL-Issuer', ''),
            'subject': headers.get('SSL-Subject', ''),
            'version': headers.get('SSL-Cert-Version', '')
        }

    def _hash_signature(self, signature):
        sig_str = json.dumps(signature, sort_keys=True)
        return hashlib.md5(sig_str.encode()).hexdigest()
```

## Device Risk Scoring

### Device Reputation Calculation
```python
class DeviceRiskCalculator:
    def __init__(self, device_db):
        self.device_db = device_db

    def calculate_device_risk(self, device_id):
        """Calculate risk score for device"""
        device_info = self.device_db.get_device_info(device_id)

        if not device_info:
            # New device
            return {
                'score': 0.5,
                'reason': 'Unknown device',
                'age_days': 0,
                'confidence': 0.5
            }

        risk_components = {}

        # Device age
        risk_components['age'] = self._score_device_age(
            device_info['first_seen']
        )

        # Device fraud history
        risk_components['fraud_history'] = self._score_fraud_history(
            device_id
        )

        # Device velocity
        risk_components['velocity'] = self._score_device_velocity(
            device_id
        )

        # Device sharing
        risk_components['sharing'] = self._score_device_sharing(
            device_id
        )

        # Combine scores
        final_score = np.average(
            list(risk_components.values()),
            weights=[0.2, 0.3, 0.3, 0.2]
        )

        return {
            'score': final_score,
            'components': risk_components,
            'age_days': (datetime.now() - device_info['first_seen']).days,
            'confidence': 0.8 if device_info['transactions'] > 10 else 0.5
        }

    def _score_device_age(self, first_seen):
        """Score device based on age"""
        days_old = (datetime.now() - first_seen).days

        if days_old < 1:
            return 0.9  # New device, high risk
        elif days_old < 7:
            return 0.6
        elif days_old < 30:
            return 0.3
        else:
            return 0.1  # Old device, low risk

    def _score_fraud_history(self, device_id):
        """Score based on confirmed fraud cases"""
        fraud_cases = self.device_db.get_fraud_cases(device_id)

        if not fraud_cases:
            return 0.0

        fraud_rate = len(fraud_cases) / self.device_db.get_transaction_count(
            device_id
        )

        # Scale fraud rate to 0-1
        return min(fraud_rate * 10, 1.0)

    def _score_device_velocity(self, device_id):
        """Score based on transaction velocity"""
        transactions_24h = self.device_db.get_transactions_24h(device_id)
        average_daily = self.device_db.get_average_daily_transactions(
            device_id
        )

        if average_daily == 0:
            return 0.5  # Unknown

        spike_ratio = transactions_24h / (average_daily + 1)

        if spike_ratio > 5:
            return 0.8  # High velocity
        elif spike_ratio > 2:
            return 0.5
        else:
            return 0.1  # Normal

    def _score_device_sharing(self, device_id):
        """Score based on number of accounts using device"""
        account_count = self.device_db.get_account_count(device_id)

        if account_count == 1:
            return 0.0  # Single account (normal)
        elif account_count == 2:
            return 0.3  # Two accounts (possibly family)
        elif account_count <= 5:
            return 0.6  # Multiple accounts
        else:
            return 0.9  # Many accounts (suspicious)
```

## Device Whitelisting & Trust

### Device Approval Workflow
```python
class DeviceTrustManager:
    def __init__(self, trust_db):
        self.trust_db = trust_db

    def is_device_trusted(self, customer_id, device_id):
        """Check if device is in customer's trusted list"""
        trusted_devices = self.trust_db.get_trusted_devices(customer_id)
        return device_id in trusted_devices

    def request_device_trust(self, customer_id, device_id):
        """Request customer to approve device"""
        # Send verification email/SMS
        verification_code = generate_verification_code()

        self.trust_db.store_pending_verification(
            customer_id=customer_id,
            device_id=device_id,
            code=verification_code,
            expires_at=datetime.now() + timedelta(hours=24)
        )

        # Send code to customer's verified email
        send_verification_email(customer_id, verification_code)

        return {'status': 'verification_sent'}

    def approve_device(self, customer_id, device_id, code):
        """Approve and whitelist device"""
        # Verify code
        pending = self.trust_db.get_pending_verification(
            customer_id, device_id, code
        )

        if not pending or pending['expires_at'] < datetime.now():
            return {'status': 'invalid_or_expired'}

        # Add to trusted list
        self.trust_db.add_trusted_device(
            customer_id=customer_id,
            device_id=device_id,
            approved_at=datetime.now()
        )

        # Remove pending verification
        self.trust_db.delete_pending_verification(
            customer_id, device_id
        )

        return {'status': 'device_trusted'}

    def revoke_device_trust(self, customer_id, device_id):
        """Remove device from trusted list"""
        self.trust_db.remove_trusted_device(customer_id, device_id)

        # Force re-authentication on next access
        return {'status': 'device_revoked'}
```

## Device Matching & Analysis

### Historical Device Analysis
```python
class DeviceAnalyzer:
    def get_device_history(self, customer_id):
        """Get all devices used by customer"""
        devices = self.device_db.get_customer_devices(customer_id)

        return {
            'primary_device': self._get_primary_device(devices),
            'secondary_devices': self._get_secondary_devices(devices),
            'abandoned_devices': self._get_abandoned_devices(devices),
            'suspicious_devices': self._get_suspicious_devices(devices)
        }

    def detect_device_anomalies(self, customer_id, current_device_id):
        """Detect device-related anomalies"""
        customer_devices = self.device_db.get_customer_devices(customer_id)
        current_device = self.device_db.get_device(current_device_id)

        anomalies = []

        # New device usage
        if current_device_id not in [d['id'] for d in customer_devices]:
            anomalies.append({
                'type': 'new_device',
                'severity': 'medium',
                'message': 'New device detected'
            })

        # Device not used in long time
        if current_device['last_used'] and (
            datetime.now() - current_device['last_used']
        ).days > 90:
            anomalies.append({
                'type': 'dormant_device',
                'severity': 'low',
                'message': 'Device not used in 90+ days'
            })

        # High fraud device
        if self._score_fraud_history(current_device_id) > 0.7:
            anomalies.append({
                'type': 'high_risk_device',
                'severity': 'high',
                'message': 'Device has fraud history'
            })

        return anomalies
```

## Implementation Best Practices

1. **Client-Server Consistency**
   - Client-side fingerprint
   - Server-side verification
   - Cross-check results

2. **Privacy Respect**
   - Transparent about tracking
   - User consent
   - Data minimization
   - Secure storage

3. **Adaptive Thresholds**
   - New devices: Higher scrutiny
   - Trusted devices: Lower scrutiny
   - Balance security/usability

4. **Feedback Loop**
   - Update device reputation
   - Incorporate investigation findings
   - Continuous learning

5. **Fallback Handling**
   - Device identification fails
   - Use other signals
   - Require verification

6. **Monitoring**
   - Device fingerprint changes
   - Unusual device activity
   - Device sharing patterns
