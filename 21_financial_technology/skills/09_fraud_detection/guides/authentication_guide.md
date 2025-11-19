# Authentication Guide

## Multi-Factor Authentication Strategy

### Tiered Authentication Based on Risk
```
Risk Score < 0.3:
  - Password only
  - Fast transaction
  - No additional friction

Risk Score 0.3-0.6:
  - Optional 2FA
  - Recommend but not required
  - Remind user of security

Risk Score 0.6-0.8:
  - Required 2FA
  - Must complete authentication
  - Multiple methods available

Risk Score > 0.8:
  - Strong 2FA (hardware key preferred)
  - Additional verification
  - Human review
  - Possible blocking
```

## Implementation Strategy

### Risk-Based 2FA Trigger
```python
class AdaptiveAuthentication:
    def determine_auth_requirement(self, transaction, fraud_score):
        """Determine authentication requirement"""
        auth_requirement = {
            'required': False,
            'method': None,
            'strength': 'none'
        }

        # Determine based on fraud score
        if fraud_score > 0.6:
            auth_requirement['required'] = True

            if fraud_score > 0.8:
                # Strong authentication for high risk
                auth_requirement['method'] = 'hardware_key_or_biometric'
                auth_requirement['strength'] = 'strong'
            else:
                # Standard 2FA for medium-high risk
                auth_requirement['method'] = 'totp_or_sms'
                auth_requirement['strength'] = 'medium'

        elif fraud_score > 0.3:
            # Optional 2FA for medium risk
            auth_requirement['optional'] = True
            auth_requirement['recommended'] = True

        return auth_requirement

    def present_authentication_challenge(self, transaction, requirement):
        """Present authentication to user"""
        if not requirement['required']:
            return self.offer_optional_2fa(transaction)

        # Determine method
        if requirement['method'] == 'hardware_key_or_biometric':
            return self.request_hardware_key_or_biometric(transaction)
        elif requirement['method'] == 'totp_or_sms':
            return self.request_totp_or_sms(transaction)

    def request_totp_or_sms(self, transaction):
        """Request TOTP or SMS OTP"""
        customer = self.get_customer(transaction['customer_id'])

        # Preferred method
        if customer.get('preferred_2fa') == 'totp':
            return self.send_totp_request(transaction)
        elif customer.get('preferred_2fa') == 'sms':
            return self.send_sms_otp(transaction)
        else:
            # Default to SMS
            return self.send_sms_otp(transaction)

    def send_sms_otp(self, transaction):
        """Send one-time password via SMS"""
        customer = self.get_customer(transaction['customer_id'])
        phone = customer['verified_phone']

        # Generate OTP
        otp = self.generate_otp()

        # Store temporarily
        self.cache.setex(
            f'otp:{transaction["id"]}',
            300,  # 5 minute expiration
            otp
        )

        # Send SMS
        send_sms(phone, f'Your verification code: {otp}')

        return {
            'status': 'otp_sent',
            'method': 'sms',
            'expires_in': 300
        }

    def verify_otp(self, transaction_id, otp_code):
        """Verify OTP entered by user"""
        stored_otp = self.cache.get(f'otp:{transaction_id}')

        if not stored_otp:
            return {
                'valid': False,
                'message': 'OTP expired or not found'
            }

        if stored_otp != otp_code:
            return {
                'valid': False,
                'message': 'Invalid OTP code'
            }

        # OTP valid - clear it
        self.cache.delete(f'otp:{transaction_id}')

        return {
            'valid': True,
            'message': 'OTP verified successfully'
        }
```

### Biometric Authentication
```python
class BiometricAuthentication:
    def register_biometric(self, customer_id, biometric_data):
        """Register biometric for customer"""
        # Enroll biometric
        enrollment = self.enroll_biometric(
            biometric_data['type'],  # fingerprint, face, iris
            biometric_data['data']
        )

        # Store template (not raw data)
        self.db.store_biometric_template(
            customer_id=customer_id,
            template=enrollment['template'],
            template_version=enrollment['version'],
            biometric_type=biometric_data['type']
        )

        return {'status': 'registered'}

    def authenticate_biometric(self, customer_id, biometric_sample):
        """Authenticate using biometric"""
        # Retrieve stored template
        template = self.db.get_biometric_template(customer_id)

        if not template:
            return {'authenticated': False, 'reason': 'No biometric enrolled'}

        # Compare sample to template
        match_score = self.compare_biometric(
            template['template'],
            biometric_sample
        )

        # Typically 99%+ match threshold
        authenticated = match_score > 0.99

        return {
            'authenticated': authenticated,
            'match_score': match_score,
            'confidence': 'high' if match_score > 0.995 else 'medium'
        }
```

## Password Management

### Secure Password Practices
```python
class PasswordManager:
    def set_password(self, customer_id, password):
        """Set customer password securely"""
        # Validate strength
        if not self.is_password_strong(password):
            return {
                'valid': False,
                'message': 'Password too weak. Require: 12+ chars, uppercase, number, special char'
            }

        # Hash password
        password_hash = self.hash_password(password)

        # Store hash (never store plaintext)
        self.db.set_password_hash(customer_id, password_hash)

        return {'valid': True, 'message': 'Password set successfully'}

    def is_password_strong(self, password):
        """Validate password strength"""
        checks = {
            'length': len(password) >= 12,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'digit': any(c.isdigit() for c in password),
            'special': any(c in '!@#$%^&*' for c in password)
        }

        # Require at least 4 of 5
        return sum(checks.values()) >= 4

    def hash_password(self, password):
        """Hash password using bcrypt"""
        import bcrypt

        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed.decode('utf-8')

    def verify_password(self, customer_id, password):
        """Verify password against hash"""
        import bcrypt

        hash_value = self.db.get_password_hash(customer_id)

        if not hash_value:
            return False

        return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))
```

## Session Management

### Secure Session Handling
```python
class SessionManager:
    def create_session(self, customer_id, auth_level):
        """Create authenticated session"""
        session_id = self.generate_session_id()

        session_data = {
            'customer_id': customer_id,
            'auth_level': auth_level,  # 'password', '2fa', 'biometric'
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }

        # Store in secure session store
        self.session_store.set(
            f'session:{session_id}',
            session_data,
            ex=3600  # 1 hour expiration
        )

        return {
            'session_id': session_id,
            'expires_in': 3600
        }

    def validate_session(self, session_id):
        """Validate active session"""
        session_data = self.session_store.get(f'session:{session_id}')

        if not session_data:
            return {'valid': False, 'reason': 'Session not found or expired'}

        # Check IP consistency (basic anti-session-hijacking)
        if session_data['ip_address'] != request.remote_addr:
            return {
                'valid': False,
                'reason': 'IP address mismatch'
            }

        # Update last activity
        session_data['last_activity'] = datetime.now()
        self.session_store.set(
            f'session:{session_id}',
            session_data,
            ex=3600
        )

        return {'valid': True, 'auth_level': session_data['auth_level']}

    def destroy_session(self, session_id):
        """Destroy session on logout"""
        self.session_store.delete(f'session:{session_id}')

        return {'status': 'logged_out'}
```

## Account Recovery

### Secure Recovery Process
```python
class AccountRecovery:
    def initiate_password_reset(self, email):
        """Initiate password reset"""
        # Find customer by email
        customer = self.db.get_customer_by_email(email)

        if not customer:
            # Don't reveal if email exists (security best practice)
            return {
                'status': 'pending',
                'message': 'If email is registered, reset link will be sent'
            }

        # Generate reset token
        reset_token = self.generate_secure_token(32)

        # Store with expiration
        self.cache.setex(
            f'password_reset:{reset_token}',
            3600,  # 1 hour expiration
            customer['id']
        )

        # Send email with reset link
        send_password_reset_email(email, reset_token)

        return {
            'status': 'sent',
            'message': 'Password reset email sent'
        }

    def reset_password_with_token(self, reset_token, new_password):
        """Reset password using token"""
        customer_id = self.cache.get(f'password_reset:{reset_token}')

        if not customer_id:
            return {
                'status': 'invalid',
                'message': 'Reset token invalid or expired'
            }

        # Validate new password
        if not self.is_password_strong(new_password):
            return {
                'status': 'weak',
                'message': 'Password too weak'
            }

        # Update password
        password_hash = self.hash_password(new_password)
        self.db.set_password_hash(customer_id, password_hash)

        # Clear token
        self.cache.delete(f'password_reset:{reset_token}')

        # Force logout all sessions
        self.clear_all_sessions(customer_id)

        return {
            'status': 'success',
            'message': 'Password reset successfully'
        }
```

## Best Practices

1. **Defense in Depth**: Multiple authentication methods
2. **Risk-Based**: Adjust authentication based on risk
3. **No Passwords Stored**: Always hash passwords
4. **Session Security**: Secure session management
5. **Recovery Flows**: Secure account recovery
6. **Monitoring**: Detect authentication anomalies
7. **User Education**: Help users protect accounts
8. **Regular Updates**: Keep authentication methods current
