# Implementing Secure Authentication - Step-by-Step Guide

> Complete guide to implementing production-grade authentication following OWASP ASVS and NIST Digital Identity Guidelines.

---

## Overview

This guide covers implementing secure authentication with:
- Password-based authentication with bcrypt
- Multi-factor authentication (MFA)
- Session management
- Account security (lockout, password reset)
- JWT tokens for APIs

---

## Step 1: Password Storage

### Never Store Plaintext Passwords

```python
# ❌ NEVER DO THIS
user.password = password  # Plaintext storage!

# ❌ NEVER DO THIS
user.password = hashlib.md5(password.encode()).hexdigest()  # MD5 is broken!

# ❌ NEVER DO THIS
user.password = hashlib.sha256(password.encode()).hexdigest()  # No salt, too fast!
```

### Use bcrypt (or Argon2, scrypt)

```python
import bcrypt
from typing import Optional

class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with salt"""
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)  # Cost factor: 12
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False

# Usage
password_hash = PasswordService.hash_password("user_password")
is_valid = PasswordService.verify_password("user_password", password_hash)
```

---

## Step 2: Password Policy

```python
import re
from dataclasses import dataclass

@dataclass
class PasswordRequirements:
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    max_length: int = 128

class PasswordValidator:
    def __init__(self, requirements: PasswordRequirements = None):
        self.requirements = requirements or PasswordRequirements()

    def validate(self, password: str) -> tuple[bool, list[str]]:
        """Validate password against requirements"""
        errors = []

        # Length check
        if len(password) < self.requirements.min_length:
            errors.append(f"Password must be at least {self.requirements.min_length} characters")

        if len(password) > self.requirements.max_length:
            errors.append(f"Password must not exceed {self.requirements.max_length} characters")

        # Complexity checks
        if self.requirements.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if self.requirements.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if self.requirements.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        if self.requirements.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Check against common passwords
        if self.is_common_password(password):
            errors.append("Password is too common - please choose a stronger password")

        return (len(errors) == 0, errors)

    def is_common_password(self, password: str) -> bool:
        """Check against list of common passwords"""
        # Load from common passwords list (e.g., rockyou.txt top 10000)
        common_passwords = self.load_common_passwords()
        return password.lower() in common_passwords

# Usage
validator = PasswordValidator()
is_valid, errors = validator.validate("Test123!")
if not is_valid:
    print("Password validation failed:", errors)
```

---

## Step 3: Multi-Factor Authentication (MFA)

### Time-Based One-Time Password (TOTP)

```python
import pyotp
import qrcode
from io import BytesIO

class TOTPService:
    @staticmethod
    def generate_secret() -> str:
        """Generate new TOTP secret for user"""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(secret: str, user_email: str, issuer: str = "MyApp") -> str:
        """Generate provisioning URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )

    @staticmethod
    def generate_qr_code(provisioning_uri: str) -> bytes:
        """Generate QR code image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        # Allow for time drift (±1 window = ±30 seconds)
        return totp.verify(token, valid_window=1)

# Usage - MFA Setup
def setup_mfa(user):
    # Generate secret
    secret = TOTPService.generate_secret()

    # Store secret (encrypted) in database
    user.mfa_secret = encrypt(secret)
    user.mfa_enabled = True
    db.session.commit()

    # Generate QR code for user to scan
    uri = TOTPService.get_provisioning_uri(secret, user.email)
    qr_code = TOTPService.generate_qr_code(uri)

    return qr_code

# Usage - MFA Verification
def verify_mfa(user, token):
    if not user.mfa_enabled:
        return True  # MFA not enabled

    secret = decrypt(user.mfa_secret)
    return TOTPService.verify_token(secret, token)
```

---

## Step 4: Session Management

```python
from datetime import datetime, timedelta
import secrets
import redis

class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_timeout = timedelta(hours=8)
        self.absolute_timeout = timedelta(days=7)

    def create_session(self, user_id: str, user_agent: str, ip_address: str) -> str:
        """Create new session"""
        # Generate cryptographically secure session token
        session_token = secrets.token_urlsafe(32)

        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'user_agent': user_agent,
            'ip_address': ip_address
        }

        # Store in Redis with expiration
        self.redis.setex(
            f"session:{session_token}",
            self.session_timeout,
            json.dumps(session_data)
        )

        return session_token

    def validate_session(
        self,
        session_token: str,
        user_agent: str,
        ip_address: str
    ) -> Optional[dict]:
        """Validate session and return user data"""
        session_key = f"session:{session_token}"
        session_data = self.redis.get(session_key)

        if not session_data:
            return None

        session = json.loads(session_data)

        # Check absolute timeout
        created_at = datetime.fromisoformat(session['created_at'])
        if datetime.utcnow() - created_at > self.absolute_timeout:
            self.destroy_session(session_token)
            return None

        # Session fixation protection: verify user agent and IP
        if session['user_agent'] != user_agent:
            logger.warning(f"Session hijacking attempt: user_agent mismatch")
            self.destroy_session(session_token)
            return None

        # Optional: Strict IP binding (may cause issues with mobile users)
        # if session['ip_address'] != ip_address:
        #     self.destroy_session(session_token)
        #     return None

        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        self.redis.setex(
            session_key,
            self.session_timeout,
            json.dumps(session)
        )

        return session

    def destroy_session(self, session_token: str):
        """Destroy session"""
        self.redis.delete(f"session:{session_token}")

    def destroy_all_user_sessions(self, user_id: str):
        """Destroy all sessions for user (e.g., after password change)"""
        # Scan for all sessions
        for key in self.redis.scan_iter(match="session:*"):
            session_data = self.redis.get(key)
            if session_data:
                session = json.loads(session_data)
                if session.get('user_id') == user_id:
                    self.redis.delete(key)
```

---

## Step 5: Account Security Features

### Account Lockout (Prevent Brute Force)

```python
class AccountSecurity:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=30)

    def record_failed_login(self, username: str, ip_address: str):
        """Record failed login attempt"""
        key = f"failed_login:{username}"

        # Increment counter
        attempts = self.redis.incr(key)

        # Set expiration on first attempt
        if attempts == 1:
            self.redis.expire(key, self.lockout_duration)

        # Lock account if max attempts exceeded
        if attempts >= self.max_attempts:
            self.lock_account(username)
            logger.warning(
                f"Account locked due to failed login attempts",
                extra={'username': username, 'ip': ip_address}
            )

        return attempts

    def is_account_locked(self, username: str) -> bool:
        """Check if account is locked"""
        return self.redis.exists(f"account_locked:{username}")

    def lock_account(self, username: str):
        """Lock account"""
        self.redis.setex(
            f"account_locked:{username}",
            self.lockout_duration,
            "locked"
        )

    def unlock_account(self, username: str):
        """Unlock account (manual override)"""
        self.redis.delete(f"account_locked:{username}")
        self.redis.delete(f"failed_login:{username}")

    def clear_failed_attempts(self, username: str):
        """Clear failed attempts after successful login"""
        self.redis.delete(f"failed_login:{username}")
```

### Secure Password Reset

```python
class PasswordResetService:
    def __init__(self, redis_client, email_service):
        self.redis = redis_client
        self.email_service = email_service
        self.token_expiration = timedelta(hours=1)

    def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        user = User.query.filter_by(email=email).first()

        # Always return success to prevent user enumeration
        if not user:
            logger.info(f"Password reset requested for non-existent email: {email}")
            return True

        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)

        # Store token
        self.redis.setex(
            f"password_reset:{reset_token}",
            self.token_expiration,
            user.id
        )

        # Send reset email
        reset_link = f"https://example.com/reset-password?token={reset_token}"
        self.email_service.send_password_reset(user.email, reset_link)

        # Log for security monitoring
        logger.info(f"Password reset requested for user: {user.id}")

        return True

    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password using token"""
        # Validate token
        user_id = self.redis.get(f"password_reset:{reset_token}")

        if not user_id:
            logger.warning("Invalid or expired password reset token")
            return False

        user = User.query.get(user_id)
        if not user:
            return False

        # Validate new password
        validator = PasswordValidator()
        is_valid, errors = validator.validate(new_password)

        if not is_valid:
            raise ValueError("Password does not meet requirements")

        # Update password
        user.password_hash = PasswordService.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()

        # Invalidate all existing sessions
        session_manager.destroy_all_user_sessions(user.id)

        # Delete reset token
        self.redis.delete(f"password_reset:{reset_token}")

        db.session.commit()

        # Log password change
        logger.info(f"Password reset completed for user: {user.id}")

        return True
```

---

## Step 6: Putting It All Together

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()

    # Validate password
    validator = PasswordValidator()
    is_valid, errors = validator.validate(data['password'])

    if not is_valid:
        return jsonify({'error': 'Invalid password', 'details': errors}), 400

    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Create user
    user = User(
        email=data['email'],
        password_hash=PasswordService.hash_password(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login with MFA"""
    data = request.get_json()

    # Check account lockout
    if account_security.is_account_locked(data['email']):
        return jsonify({'error': 'Account locked due to too many failed attempts'}), 429

    # Find user
    user = User.query.filter_by(email=data['email']).first()

    if not user or not PasswordService.verify_password(data['password'], user.password_hash):
        # Record failed attempt
        account_security.record_failed_login(data['email'], request.remote_addr)
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify MFA if enabled
    if user.mfa_enabled:
        if not data.get('mfa_token'):
            return jsonify({'error': 'MFA token required', 'mfa_required': True}), 401

        if not verify_mfa(user, data['mfa_token']):
            account_security.record_failed_login(data['email'], request.remote_addr)
            return jsonify({'error': 'Invalid MFA token'}), 401

    # Clear failed attempts
    account_security.clear_failed_attempts(data['email'])

    # Create session
    session_token = session_manager.create_session(
        user.id,
        request.user_agent.string,
        request.remote_addr
    )

    # Log successful login
    logger.info(f"Successful login: user={user.id}, ip={request.remote_addr}")

    return jsonify({
        'session_token': session_token,
        'user': {
            'id': user.id,
            'email': user.email
        }
    }), 200
```

---

## Security Checklist

Authentication Implementation:
- [ ] Passwords hashed with bcrypt (cost factor ≥12)
- [ ] Strong password policy enforced (12+ chars, complexity)
- [ ] Account lockout after 5 failed attempts
- [ ] MFA available (TOTP or FIDO2)
- [ ] Secure session management (httpOnly, secure, SameSite cookies)
- [ ] Session timeout (8 hours idle, 7 days absolute)
- [ ] Session binding (user agent validation)
- [ ] Password reset with secure tokens (1 hour expiration)
- [ ] All sessions invalidated after password change
- [ ] Rate limiting on authentication endpoints
- [ ] Comprehensive security logging
- [ ] No user enumeration (same error messages)
- [ ] HTTPS only (TLS 1.2+)

---

## References

- OWASP Authentication Cheat Sheet
- NIST SP 800-63B: Digital Identity Guidelines
- OWASP ASVS v4.0: Authentication Requirements
