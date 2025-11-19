# IAM Standards and Compliance Reference

## Industry Standards

### NIST SP 800-63: Digital Identity Guidelines

**Authentication Assurance Levels (AAL)**

| Level | Description | Requirements |
|-------|-------------|--------------|
| AAL1 | Single-factor authentication | Password or memorized secret |
| AAL2 | Multi-factor authentication | Two different factors (possession + knowledge) |
| AAL3 | Multi-factor cryptographic authentication | Hardware-based cryptographic authenticator |

**Federation Assurance Levels (FAL)**

| Level | Description | Requirements |
|-------|-------------|--------------|
| FAL1 | Basic federation | Bearer assertion, HTTPS required |
| FAL2 | Authenticated federation | Signed assertion, authenticated RP |
| FAL3 | Cryptographically verified | Encrypted assertion, key confirmation |

### OAuth 2.0 Best Current Practice (RFC 8252)

**Security Recommendations:**

1. **Authorization Code Flow**
   - Always use PKCE (Proof Key for Code Exchange)
   - Never use implicit grant flow
   - Implement state parameter for CSRF protection

2. **Token Handling**
   - Use short-lived access tokens (1 hour max)
   - Implement refresh token rotation
   - Store tokens securely (never in localStorage)

3. **Client Security**
   - Validate redirect URIs
   - Use client authentication for confidential clients
   - Implement token binding where supported

**Code Example:**

```python
# OAuth 2.0 with PKCE implementation
import hashlib
import base64
from secrets import token_urlsafe

class OAuth2PKCEClient:
    def __init__(self, client_id: str, authorization_endpoint: str, token_endpoint: str):
        self.client_id = client_id
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.code_verifier = None
        self.code_challenge = None

    def generate_pkce_pair(self) -> tuple:
        """Generate PKCE code verifier and challenge"""
        # Generate code verifier (43-128 characters)
        self.code_verifier = token_urlsafe(64)

        # Generate code challenge using S256 method
        challenge_bytes = hashlib.sha256(self.code_verifier.encode()).digest()
        self.code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip('=')

        return self.code_verifier, self.code_challenge

    def get_authorization_url(self, redirect_uri: str, scope: str, state: str) -> str:
        """Build authorization URL with PKCE"""
        if not self.code_challenge:
            self.generate_pkce_pair()

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256'
        }

        from urllib.parse import urlencode
        return f"{self.authorization_endpoint}?{urlencode(params)}"

    def exchange_code(self, authorization_code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for tokens using PKCE"""
        import requests

        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'code_verifier': self.code_verifier
        }

        response = requests.post(self.token_endpoint, data=token_data)
        return response.json()
```

### OpenID Connect Core 1.0

**ID Token Validation Requirements:**

```python
# OpenID Connect ID token validation
import jwt
import requests
from datetime import datetime, timedelta

class OIDCTokenValidator:
    def __init__(self, issuer: str, client_id: str, jwks_uri: str):
        self.issuer = issuer
        self.client_id = client_id
        self.jwks_uri = jwks_uri
        self.jwks_cache = None
        self.jwks_cache_time = None

    def validate_id_token(self, id_token: str) -> dict:
        """Validate OpenID Connect ID token"""
        # Decode header to get key ID
        header = jwt.get_unverified_header(id_token)
        kid = header.get('kid')

        if not kid:
            raise ValueError("Token missing key ID (kid)")

        # Get public key from JWKS
        public_key = self._get_public_key(kid)

        # Verify and decode token
        try:
            claims = jwt.decode(
                id_token,
                public_key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=self.issuer,
                options={
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True
                }
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidAudienceError:
            raise ValueError("Invalid audience")
        except jwt.InvalidIssuerError:
            raise ValueError("Invalid issuer")

        # Additional validations
        self._validate_nonce(claims)
        self._validate_auth_time(claims)

        return claims

    def _get_public_key(self, kid: str):
        """Retrieve public key from JWKS endpoint"""
        # Cache JWKS for 1 hour
        if self.jwks_cache and self.jwks_cache_time:
            if datetime.now() - self.jwks_cache_time < timedelta(hours=1):
                return self._find_key_in_jwks(kid, self.jwks_cache)

        # Fetch fresh JWKS
        response = requests.get(self.jwks_uri)
        self.jwks_cache = response.json()
        self.jwks_cache_time = datetime.now()

        return self._find_key_in_jwks(kid, self.jwks_cache)

    def _find_key_in_jwks(self, kid: str, jwks: dict):
        """Find specific key in JWKS"""
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                from jwt.algorithms import RSAAlgorithm
                return RSAAlgorithm.from_jwk(key)

        raise ValueError(f"Key {kid} not found in JWKS")

    def _validate_nonce(self, claims: dict):
        """Validate nonce if present"""
        # Nonce validation should be implemented based on stored nonce
        pass

    def _validate_auth_time(self, claims: dict):
        """Validate authentication time"""
        auth_time = claims.get('auth_time')
        if auth_time:
            # Check if authentication is recent enough
            current_time = datetime.now().timestamp()
            if current_time - auth_time > 3600:  # 1 hour
                raise ValueError("Authentication too old")
```

## Compliance Frameworks

### SOC 2 Type II - Access Control Requirements

**Trust Service Criteria:**

1. **CC6.1:** Logical and physical access controls
   - Implement MFA for all users
   - Regular access reviews (quarterly minimum)
   - Segregation of duties

2. **CC6.2:** New users, modifications, and terminations
   - Automated provisioning/deprovisioning
   - Manager approval for access requests
   - Immediate revocation upon termination

3. **CC6.3:** Privileged access
   - Just-in-time privileged access
   - Comprehensive audit logging
   - Quarterly privileged access reviews

**Implementation Checklist:**

```yaml
soc2_iam_controls:
  access_provisioning:
    - automated_user_provisioning
    - manager_approval_workflow
    - role_based_access_assignment
    - new_hire_onboarding_automation

  access_deprovisioning:
    - automated_termination_workflow
    - immediate_access_revocation
    - exit_interview_verification
    - periodic_dormant_account_cleanup

  access_reviews:
    - quarterly_access_certification
    - privileged_access_monthly_review
    - automated_review_reminders
    - remediation_tracking

  authentication:
    - mfa_enforcement
    - password_complexity_requirements
    - password_rotation_policy
    - failed_login_monitoring

  monitoring_logging:
    - authentication_event_logging
    - privileged_action_logging
    - access_anomaly_detection
    - log_retention_1_year
```

### GDPR - Identity and Access Requirements

**Article 32: Security of Processing**

Requirements:
- Pseudonymization and encryption of personal data
- Ability to ensure confidentiality, integrity, availability
- Regular testing and evaluation of security measures

**Implementation:**

```python
# GDPR-compliant user data access control
class GDPRAccessControl:
    def __init__(self):
        self.data_categories = {
            'personal': ['name', 'email', 'phone'],
            'sensitive': ['health', 'biometric', 'genetic'],
            'financial': ['credit_card', 'bank_account']
        }
        self.processing_purposes = {}
        self.consent_records = {}

    def check_access_permission(
        self,
        user_id: str,
        data_subject_id: str,
        data_field: str,
        purpose: str
    ) -> bool:
        """Verify if access is allowed under GDPR"""

        # Check if user has role-based permission
        if not self._has_role_permission(user_id, data_field):
            self._log_access_denial(user_id, data_subject_id, data_field, 'no_role_permission')
            return False

        # Check if purpose is legitimate
        if not self._is_legitimate_purpose(purpose):
            self._log_access_denial(user_id, data_subject_id, data_field, 'invalid_purpose')
            return False

        # Check consent for sensitive data
        if self._is_sensitive_data(data_field):
            if not self._has_consent(data_subject_id, purpose):
                self._log_access_denial(user_id, data_subject_id, data_field, 'no_consent')
                return False

        # Log access for audit trail
        self._log_access(user_id, data_subject_id, data_field, purpose)

        return True

    def process_right_to_erasure(self, data_subject_id: str) -> dict:
        """Handle GDPR Right to be Forgotten request"""
        # Identify all data for subject
        data_locations = self._identify_data_locations(data_subject_id)

        # Determine what can be deleted
        erasable_data = []
        retention_required = []

        for location in data_locations:
            if self._has_legal_retention_requirement(location):
                retention_required.append(location)
            else:
                erasable_data.append(location)

        # Execute erasure
        for location in erasable_data:
            self._erase_data(location, data_subject_id)

        return {
            'request_id': self._generate_request_id(),
            'data_subject_id': data_subject_id,
            'erased_locations': erasable_data,
            'retained_locations': retention_required,
            'retention_reasons': self._get_retention_reasons(retention_required)
        }

    def _has_role_permission(self, user_id: str, data_field: str) -> bool:
        """Check role-based permissions"""
        # Implementation would check against IAM system
        return True

    def _is_legitimate_purpose(self, purpose: str) -> bool:
        """Verify purpose is documented and legitimate"""
        valid_purposes = ['contract_fulfillment', 'legal_obligation', 'legitimate_interest']
        return purpose in valid_purposes

    def _is_sensitive_data(self, data_field: str) -> bool:
        """Check if data field is sensitive under GDPR"""
        return data_field in self.data_categories.get('sensitive', [])

    def _has_consent(self, data_subject_id: str, purpose: str) -> bool:
        """Check if valid consent exists"""
        consent = self.consent_records.get(data_subject_id, {})
        return consent.get(purpose, {}).get('granted', False)

    def _log_access(self, user_id: str, data_subject_id: str, data_field: str, purpose: str):
        """Log data access for audit"""
        pass

    def _log_access_denial(self, user_id: str, data_subject_id: str, data_field: str, reason: str):
        """Log access denial"""
        pass
```

### HIPAA - Access Control Requirements

**§ 164.312(a)(1) - Access Control**

Technical safeguards:
- Unique user identification
- Emergency access procedures
- Automatic logoff
- Encryption and decryption

**Implementation:**

```python
# HIPAA-compliant access control
class HIPAAAccessControl:
    def __init__(self):
        self.role_permissions = self._initialize_roles()
        self.emergency_access_log = []

    def _initialize_roles(self) -> dict:
        """Define role-based access for healthcare data"""
        return {
            'physician': ['read_phi', 'write_phi', 'prescribe'],
            'nurse': ['read_phi', 'write_notes'],
            'admin': ['read_demographics'],
            'billing': ['read_demographics', 'read_insurance'],
            'emergency_responder': ['emergency_read_phi']
        }

    def authorize_phi_access(
        self,
        user_id: str,
        patient_id: str,
        access_type: str,
        emergency: bool = False
    ) -> dict:
        """Authorize access to Protected Health Information (PHI)"""

        # Emergency access bypass with enhanced logging
        if emergency:
            return self._grant_emergency_access(user_id, patient_id, access_type)

        # Check if user has treating relationship
        if not self._has_treating_relationship(user_id, patient_id):
            self._log_unauthorized_access_attempt(user_id, patient_id)
            return {'authorized': False, 'reason': 'no_treating_relationship'}

        # Check role-based permissions
        user_role = self._get_user_role(user_id)
        required_permission = f"{access_type}_phi"

        if required_permission not in self.role_permissions.get(user_role, []):
            return {'authorized': False, 'reason': 'insufficient_permissions'}

        # Check minimum necessary rule
        if not self._meets_minimum_necessary(user_role, access_type):
            return {'authorized': False, 'reason': 'exceeds_minimum_necessary'}

        # Log access
        self._log_phi_access(user_id, patient_id, access_type)

        return {'authorized': True, 'session_timeout': 900}  # 15 minutes

    def _grant_emergency_access(self, user_id: str, patient_id: str, access_type: str) -> dict:
        """Grant emergency access with enhanced audit trail"""
        access_record = {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'patient_id': patient_id,
            'access_type': access_type,
            'emergency': True,
            'requires_justification': True
        }

        self.emergency_access_log.append(access_record)

        # Alert privacy officer
        self._alert_privacy_officer(access_record)

        return {
            'authorized': True,
            'emergency_access': True,
            'justification_required': True,
            'session_timeout': 300  # 5 minutes for emergency
        }

    def _has_treating_relationship(self, user_id: str, patient_id: str) -> bool:
        """Verify active treating relationship"""
        # Would check against patient care team assignments
        return True

    def _meets_minimum_necessary(self, role: str, access_type: str) -> bool:
        """Verify access meets minimum necessary standard"""
        # Implement minimum necessary rule
        return True

    def _log_phi_access(self, user_id: str, patient_id: str, access_type: str):
        """Log PHI access for audit trail"""
        pass

    def _alert_privacy_officer(self, access_record: dict):
        """Alert privacy officer of emergency access"""
        pass
```

## Password Policy Standards

### NIST SP 800-63B Password Guidelines

**Modern Password Requirements:**

```python
# NIST-compliant password policy
class NISTPasswordPolicy:
    def __init__(self):
        self.min_length = 8
        self.max_length = 64
        self.blocked_passwords = self._load_common_passwords()

    def validate_password(self, password: str, user_context: dict = None) -> dict:
        """Validate password against NIST guidelines"""
        errors = []

        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")

        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")

        # Check against common passwords
        if password.lower() in self.blocked_passwords:
            errors.append("Password is too common")

        # Check against user context (username, email, etc.)
        if user_context:
            if password.lower() in user_context.get('username', '').lower():
                errors.append("Password cannot contain username")

        # Check for sequential or repeated characters
        if self._has_sequential_chars(password) or self._has_repeated_chars(password):
            errors.append("Password has sequential or repeated characters")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_strength(password)
        }

    def _load_common_passwords(self) -> set:
        """Load common password list"""
        # Would load from file (e.g., SecLists/Common-Credentials)
        return {'password', '123456', 'qwerty', 'letmein', 'admin'}

    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters (abc, 123)"""
        for i in range(len(password) - 2):
            if ord(password[i+1]) == ord(password[i]) + 1 and \
               ord(password[i+2]) == ord(password[i]) + 2:
                return True
        return False

    def _has_repeated_chars(self, password: str) -> bool:
        """Check for repeated characters (aaa, 111)"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False

    def _calculate_strength(self, password: str) -> int:
        """Calculate password strength (0-100)"""
        import math

        # Entropy-based calculation
        charset_size = 0
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(not c.isalnum() for c in password):
            charset_size += 32

        entropy = len(password) * math.log2(charset_size) if charset_size > 0 else 0

        # Normalize to 0-100 scale
        return min(100, int(entropy / 0.8))
```

## Session Management Standards

### OWASP Session Management Cheat Sheet

**Secure Session Implementation:**

```python
# Secure session management
import secrets
import hashlib
from datetime import datetime, timedelta

class SecureSessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(minutes=30)
        self.absolute_timeout = timedelta(hours=8)

    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create secure session"""
        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)

        # Hash session ID for storage
        session_hash = hashlib.sha256(session_id.encode()).hexdigest()

        session_data = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'mfa_verified': False
        }

        self.sessions[session_hash] = session_data

        return session_id

    def validate_session(self, session_id: str, ip_address: str, user_agent: str) -> dict:
        """Validate session and check for anomalies"""
        session_hash = hashlib.sha256(session_id.encode()).hexdigest()

        if session_hash not in self.sessions:
            return {'valid': False, 'reason': 'session_not_found'}

        session = self.sessions[session_hash]

        # Check session timeout
        if datetime.now() - session['last_activity'] > self.session_timeout:
            del self.sessions[session_hash]
            return {'valid': False, 'reason': 'session_timeout'}

        # Check absolute timeout
        if datetime.now() - session['created_at'] > self.absolute_timeout:
            del self.sessions[session_hash]
            return {'valid': False, 'reason': 'absolute_timeout'}

        # Check for session hijacking indicators
        if ip_address != session['ip_address']:
            # Log potential session hijacking
            self._log_security_event('ip_change', session, ip_address)
            return {'valid': False, 'reason': 'ip_mismatch', 'require_reauth': True}

        if user_agent != session['user_agent']:
            self._log_security_event('user_agent_change', session, user_agent)
            return {'valid': False, 'reason': 'user_agent_mismatch', 'require_reauth': True}

        # Update last activity
        session['last_activity'] = datetime.now()

        return {
            'valid': True,
            'user_id': session['user_id'],
            'time_remaining': self.session_timeout - (datetime.now() - session['last_activity'])
        }

    def _log_security_event(self, event_type: str, session: dict, new_value: str):
        """Log security events"""
        pass
```

## References

- NIST SP 800-63-3: Digital Identity Guidelines
- OAuth 2.0 Security Best Current Practice (RFC 8252)
- OpenID Connect Core 1.0
- OWASP Authentication Cheat Sheet
- CIS Controls v8: Identity and Access Management
- ISO/IEC 27001:2013 - Access Control (A.9)

---

**Last Updated:** 2025-01-19
**Version:** 1.0
