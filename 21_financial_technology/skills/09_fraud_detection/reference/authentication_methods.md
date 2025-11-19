# Authentication Methods Reference

## Overview
Authentication methods verify user identity and prevent unauthorized access. Integral to fraud prevention and account takeover mitigation.

## Single-Factor Authentication (SFA)

### Password-Based
- **Advantages**: Simple, universal
- **Disadvantages**: Weak security, password reuse, phishing vulnerability
- **Best for**: Initial login, low-risk scenarios

### Security Questions
- **Setup**: User selects and answers 3-5 questions
- **Advantages**: Account recovery, no external dependency
- **Disadvantages**: Answers guessable, security through obscurity
- **Best for**: Account recovery, secondary factor

## Two-Factor Authentication (2FA)

### SMS-Based (OTP)
```
1. User enters password
2. System sends 6-digit code via SMS
3. User enters code within 10 minutes
4. Authentication succeeds if correct
```

**Advantages**
- Universal phone access
- No app installation required
- Simple for users

**Disadvantages**
- SIM swap attacks
- Interception possible
- Delivery delays
- Low security rating by NIST

### Time-Based OTP (TOTP)
```
1. User installs authenticator app (Google Authenticator, Authy)
2. App generates 6-digit code changing every 30 seconds
3. User enters code during login
4. Server verifies TOTP match
```

**Advantages**
- Higher security than SMS
- Works offline
- No delivery delay
- NIST approved

**Disadvantages**
- Requires app installation
- Device loss = access loss
- User friction

### Email-Based OTP
```
1. User enters password
2. System sends 6-digit code via email
3. User clicks link or enters code
4. Authentication succeeds
```

**Advantages**
- Universal email access
- Easy for users
- No SMS dependency

**Disadvantages**
- Email compromise = account access
- Slower delivery
- Lower security than TOTP

### Hardware Keys (U2F/FIDO2)
```
1. User inserts security key (YubiKey, Google Titan)
2. User touches key to confirm
3. Key generates cryptographic proof
4. Server verifies signature
```

**Advantages**
- Highest security
- Phishing resistant
- NIST preferred
- No compromise if device lost

**Disadvantages**
- Cost ($40-80 per user)
- Physical device required
- User adoption challenges
- Backup key management

## Multi-Factor Authentication (MFA)

### Combination Strategies

#### Password + TOTP
- High security
- User-manageable
- Balance of security & usability

#### Password + SMS
- Medium security
- Universal access
- Vulnerable to SIM swap

#### Password + Email + TOTP
- Very high security
- Multiple verification paths
- More user friction

#### Password + Hardware Key
- Maximum security
- NIST preferred
- Higher cost

## Adaptive Authentication

### Risk-Based Challenge

```
Score < 0.3: No additional authentication
  Trust user immediately

Score 0.3-0.6: Optional 2FA
  "For security, please verify with 2FA"

Score 0.6-0.8: Required verification
  Force user through authentication

Score 0.8+: Block + verification call
  Contact user through known channel
```

### Contextual Challenge

```
If access from known device: No challenge
If access from new device: Optional 2FA
If access from new location: Required 2FA
If impossible travel: Block + call
```

### Behavioral-Triggered Challenge

```
If typing speed << baseline: Challenge
If unusual time of access: Challenge
If unusual location: Challenge
If multiple failed attempts: Block
```

## Authentication Flow Architecture

### Standard Flow
```
1. User enters username/password
2. Credentials validated against hash
3. 2FA challenge generated (if required)
4. User submits 2FA response
5. Response validated
6. Session created with authentication token
7. Subsequent requests use token (no re-authentication)
```

### Passwordless Flow
```
1. User enters email
2. Verification link sent via email
3. User clicks link (valid for 15 min)
4. Session created without password
5. Optional: Additional verification required
```

### Biometric Flow
```
1. User taps biometric (fingerprint/face)
2. Device validates against enrolled biometric
3. Device generates cryptographic assertion
4. Server verifies signature
5. Session created
```

## Bypass & Recovery

### Backup Codes
```
During 2FA setup:
- Generate 8-10 backup codes
- User stores securely
- Each code = one-time use
- Used if primary method unavailable

Advantages:
- Account recovery without support
- No device dependency

Disadvantages:
- Users lose codes
- Single use only
- Code reuse attacks
```

### Recovery Questions
```
Setup:
- User answers 3-5 security questions
- Answers stored encrypted
- Used for account recovery

Activation:
- User forgotten password/access
- Answers 2+ recovery questions
- Can reset password or verify identity
```

### Support Recovery
```
User contacts support team:
- Identity verification (DOB, card last 4)
- Support specialist verifies identity
- Resets 2FA or unlocks account
- Requires time and support cost

Security Tradeoff:
- Reduces security vs. customer friction
- Audit trail of recoveries
```

## Session Management

### Token-Based Sessions
```
Authentication -> JWT/OAuth Token Generated ->
Token stored client-side (browser/app) ->
Token sent with each request ->
Server validates token signature ->
Token expires after TTL (15-60 min) ->
Refresh token generates new token
```

### Session Cookies
```
Authentication -> Server creates session ->
Session ID stored in secure cookie ->
Cookie sent with each request (auto) ->
Server validates session active ->
Session expires after TTL ->
User re-authenticates
```

### Token Expiration
```
Short-lived tokens: 15-60 minutes
- Higher security
- More user interruption
- More backend verification

Long-lived tokens: 24 hours
- Better user experience
- Higher risk if compromised
- Less verification overhead
```

## Device Trust & Whitelisting

### Device Registration
```
User approves device during login:
1. User completes authentication
2. "Remember this device?" prompt
3. Device fingerprint captured
4. Device added to whitelist
5. Future authentication from device skipped
```

### Device Verification
```
Known device: Skip 2FA
Unknown device: Require 2FA
Suspicious device: Additional verification

Device considered "known" if:
- Device fingerprint matches saved
- Device hasn't changed
- User confirmed device previously
```

### Device Revocation
```
User removes device from trusted list:
- Via account settings
- Automatic after 90 days
- After password change
- After suspicious activity
```

## Multi-Channel Authentication

### Push Notifications
```
1. User initiates login
2. Push notification sent to registered device
3. User approves/denies on device
4. Server validates approval
5. Login succeeds

Security: Requires physical device access
User Experience: Very high
Phishing Risk: Low (malicious login alerts user)
```

### Voice Calls
```
1. User enters username
2. System calls phone number
3. User speaks PIN or presses keypad
4. System validates response
5. User authenticates

Security: Phone number verification
User Experience: Good
Best for: Users without app/SMS issues
```

### QR Code Scanning
```
1. Login form displays QR code
2. User scans with authenticated device
3. Secure channel established
4. User confirms login
5. Login succeeds

Security: Device confirmation required
User Experience: Good
Setup: Requires scanning capability
```

## Authentication Standards

### NIST SP 800-63B (Digital Identity Guidelines)
```
Authentication Strengths:
- Something You Know (password, PIN)
- Something You Are (biometric)
- Something You Have (device, key)

Recommended:
- Multi-factor for sensitive operations
- Hardware keys preferred
- Avoid SMS when possible
```

### OAuth 2.0 / OpenID Connect
```
Delegated authentication:
- Third-party authentication providers
- Google, Facebook, Apple login
- User consent flow
- No password shared with service
```

### FIDO2 / WebAuthn
```
Standard for passwordless authentication:
- Cryptographic key pairs (public/private)
- Server stores public key
- User proves private key possession
- Phishing resistant
```

## Phishing Prevention

### Email-Based Phishing
```
User receives fake login email:
- Links to malicious site
- User enters credentials
- Attacker gains access

Prevention:
- Security email filtering
- User training
- Link verification
- DMARC/SPF/DKIM
```

### Credential Phishing Prevention
- **Hardware keys**: Cryptographic verification prevents phishing
- **TOTP**: Time-based codes can't be forwarded
- **SMS**: Less secure than above
- **Email**: Vulnerable to compromised email

### Phishing Indicators
```
Check headers: From, Reply-To, SPF
Inspect links: Hover to see actual URL
Look for: Urgency, threats, unusual requests
Request verification: Contact company directly
```

## Fraud Ring & Shared Accounts

### Detection Patterns
```
Same account accessed from:
- Multiple devices
- Multiple locations
- Multiple IP addresses
- At same time (impossible)

Actions:
- Force re-authentication
- Review activity
- Contact user
- Lock account if suspicious
```

### Prevention
```
1. Device whitelisting (known devices only)
2. Velocity checks (limits on access frequency)
3. Behavioral analysis (unusual access patterns)
4. IP reputation checks
5. Geographic impossibility detection
```

## Authentication Metrics

### Success Metrics
- Authentication success rate
- Authentication latency
- 2FA adoption rate
- Backup code usage rate

### Security Metrics
- Failed authentication attempts
- Phishing success rate
- Account takeovers detected
- Credential compromise incidents

### User Experience Metrics
- Step-up authentication friction
- Support requests related to auth
- Authentication abandonment rate
