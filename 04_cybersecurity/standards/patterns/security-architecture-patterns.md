# Security Architecture Patterns

> Proven security design patterns from industry leaders, based on Google BeyondCorp, AWS Well-Architected, Microsoft Zero Trust, and NIST frameworks.

---

## 1. Zero Trust Architecture

### Pattern Overview
**Never trust, always verify** - Eliminate implicit trust, verify every access request

### Reference Implementation
Based on Google BeyondCorp and NIST SP 800-207

```
┌─────────────────────────────────────────────────────────────┐
│                     Zero Trust Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────┐      ┌──────────────────┐      ┌────────────┐  │
│  │ User/  │─────▶│  Policy Engine   │─────▶│ Resources  │  │
│  │ Device │      │                  │      │            │  │
│  └────────┘      │ - Identity       │      │ - Apps     │  │
│                  │ - Device Health  │      │ - Data     │  │
│                  │ - Context        │      │ - APIs     │  │
│                  │ - Risk Score     │      └────────────┘  │
│                  └──────────────────┘                       │
│                          │                                  │
│                  ┌──────────────────┐                       │
│                  │ Policy Decision  │                       │
│                  │ Point (PDP)      │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Policy Engine**: Evaluate access requests
2. **Policy Administrator**: Execute policy decisions
3. **Policy Enforcement Point**: Enable/deny access
4. **Identity Provider**: Authenticate users and devices
5. **Device Trust**: Verify device health and compliance
6. **Continuous Monitoring**: Real-time security posture assessment

### Implementation

```python
# Zero Trust policy evaluation
from enum import Enum
from dataclasses import dataclass
from typing import List

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AccessRequest:
    user_id: str
    device_id: str
    resource: str
    action: str
    ip_address: str
    timestamp: datetime

@dataclass
class TrustScore:
    user_trust: int  # 0-100
    device_trust: int  # 0-100
    context_trust: int  # 0-100
    overall: int  # Calculated

class ZeroTrustPolicyEngine:
    def evaluate_access(self, request: AccessRequest) -> bool:
        """Evaluate access request using Zero Trust principles"""

        # 1. Verify identity (MFA required)
        identity_verified = self.verify_identity(request.user_id)
        if not identity_verified:
            self.log_security_event("identity_verification_failed", request)
            return False

        # 2. Verify device health
        device_health = self.check_device_health(request.device_id)
        if not device_health.compliant:
            self.log_security_event("device_not_compliant", request)
            return False

        # 3. Calculate trust score
        trust_score = self.calculate_trust_score(request)
        if trust_score.overall < 70:  # Threshold
            self.log_security_event("low_trust_score", request)
            return False

        # 4. Evaluate contextual factors
        risk_level = self.assess_risk(request, trust_score)
        if risk_level >= RiskLevel.HIGH:
            # Require step-up authentication
            return self.require_step_up_auth(request)

        # 5. Check resource-specific policies
        authorized = self.check_authorization(
            request.user_id,
            request.resource,
            request.action
        )

        # 6. Log decision
        self.log_access_decision(request, authorized, trust_score, risk_level)

        return authorized

    def calculate_trust_score(self, request: AccessRequest) -> TrustScore:
        """Calculate comprehensive trust score"""
        user_trust = self.get_user_trust_score(request.user_id)
        device_trust = self.get_device_trust_score(request.device_id)
        context_trust = self.get_context_trust_score(request)

        overall = (user_trust * 0.4 + device_trust * 0.3 + context_trust * 0.3)

        return TrustScore(
            user_trust=user_trust,
            device_trust=device_trust,
            context_trust=context_trust,
            overall=int(overall)
        )

    def assess_risk(self, request: AccessRequest, trust: TrustScore) -> RiskLevel:
        """Assess risk level based on multiple factors"""
        risk_factors = []

        # Check for anomalies
        if self.is_unusual_location(request.user_id, request.ip_address):
            risk_factors.append("unusual_location")

        if self.is_unusual_time(request.user_id, request.timestamp):
            risk_factors.append("unusual_time")

        if self.is_sensitive_resource(request.resource):
            risk_factors.append("sensitive_resource")

        # Calculate risk level
        if len(risk_factors) >= 3 or trust.overall < 50:
            return RiskLevel.CRITICAL
        elif len(risk_factors) >= 2 or trust.overall < 70:
            return RiskLevel.HIGH
        elif len(risk_factors) >= 1 or trust.overall < 85:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
```

### When to Use
- Enterprise environments with diverse users and devices
- High-security requirements (financial, healthcare, government)
- Remote workforce with BYOD policies
- Cloud-first or hybrid cloud architectures

---

## 2. Defense in Depth

### Pattern Overview
Multiple layers of security controls to protect assets

```
┌─────────────────────────────────────────────────────────┐
│                    Defense in Depth                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 7: Data                                           │
│  └─ Encryption, DLP, Classification                      │
│                                                          │
│  Layer 6: Application                                    │
│  └─ WAF, Input Validation, Secure Coding                 │
│                                                          │
│  Layer 5: Host                                           │
│  └─ EDR, Antivirus, Host Firewall, Patching             │
│                                                          │
│  Layer 4: Network                                        │
│  └─ Segmentation, Firewall, IDS/IPS                      │
│                                                          │
│  Layer 3: Perimeter                                      │
│  └─ Firewall, VPN, DDoS Protection                       │
│                                                          │
│  Layer 2: Physical                                       │
│  └─ Access Control, Cameras, Guards                      │
│                                                          │
│  Layer 1: Policy & Procedures                            │
│  └─ Security Policies, Training, Incident Response       │
└─────────────────────────────────────────────────────────┘
```

### Implementation Example

```javascript
// Defense in Depth for web application
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const mongoSanitize = require('express-mongo-sanitize');
const xss = require('xss-clean');

const app = express();

// Layer 1: Security Headers
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", "'unsafe-inline'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
}));

// Layer 2: Rate Limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: 'Too many requests'
});
app.use('/api/', limiter);

// Layer 3: Input Sanitization
app.use(express.json({ limit: '10kb' }));
app.use(mongoSanitize());  // Prevent NoSQL injection
app.use(xss());  // Prevent XSS

// Layer 4: Authentication
const authenticateToken = require('./middleware/auth');
app.use('/api/protected', authenticateToken);

// Layer 5: Authorization
const checkPermissions = require('./middleware/permissions');
app.use('/api/admin', checkPermissions(['admin']));

// Layer 6: Input Validation
const { body, validationResult } = require('express-validator');

app.post('/api/users',
    // Validate inputs
    body('email').isEmail().normalizeEmail(),
    body('name').trim().isLength({ min: 1, max: 100 }),
    body('age').optional().isInt({ min: 18, max: 120 }),

    (req, res) => {
        // Check validation results
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        // Process request
        createUser(req.body);
        res.status(201).json({ success: true });
    }
);

// Layer 7: Error Handling (no information leakage)
app.use((err, req, res, next) => {
    // Log full error
    logger.error('Application error', { error: err, stack: err.stack });

    // Send generic error to client
    res.status(500).json({
        error: 'Internal server error',
        message: 'An unexpected error occurred'
    });
});
```

---

## 3. Least Privilege Access

### Pattern Overview
Grant minimum permissions necessary to perform a function

### Implementation: AWS IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadSpecificBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-data",
        "arn:aws:s3:::my-app-data/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:ExistingObjectTag/Environment": "production"
        },
        "IpAddress": {
          "aws:SourceIp": "10.0.0.0/16"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-app-data/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### Database-Level Least Privilege

```sql
-- Create role with minimal permissions
CREATE ROLE app_readonly;

-- Grant only SELECT on specific tables
GRANT SELECT ON users TO app_readonly;
GRANT SELECT ON orders TO app_readonly;
GRANT SELECT ON products TO app_readonly;

-- Deny access to sensitive columns
REVOKE SELECT (password_hash, ssn, credit_card) ON users FROM app_readonly;

-- Create application user with role
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT app_readonly TO app_user;

-- For write operations, separate user
CREATE ROLE app_readwrite;
GRANT SELECT, INSERT, UPDATE ON orders TO app_readwrite;
GRANT SELECT, UPDATE ON inventory TO app_readwrite;
-- Note: No DELETE permission granted
```

---

## 4. Secrets Management

### Pattern Overview
Centralized, encrypted storage and rotation of secrets

```
┌────────────────────────────────────────────────────┐
│              Secrets Management Flow                │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐         ┌─────────────────┐         │
│  │   App    │────────▶│  Vault/KMS      │         │
│  │          │  Request│  - Encrypted    │         │
│  │          │◀────────│  - Audit Log    │         │
│  └──────────┘  Secret │  - Auto-rotate  │         │
│                       └─────────────────┘         │
│                                                     │
│  Never in:                                          │
│  ✗ Code repositories                                │
│  ✗ Environment variables (container orchestration) │
│  ✗ Configuration files                              │
│  ✗ Build artifacts                                  │
└────────────────────────────────────────────────────┘
```

### Implementation: HashiCorp Vault

```python
import hvac
from functools import lru_cache

class SecretsManager:
    def __init__(self, vault_url, role_id, secret_id):
        self.client = hvac.Client(url=vault_url)

        # Authenticate using AppRole
        self.client.auth.approle.login(
            role_id=role_id,
            secret_id=secret_id
        )

    @lru_cache(maxsize=100)
    def get_secret(self, path: str, key: str) -> str:
        """Get secret from Vault with caching"""
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path
            )
            return secret['data']['data'][key]
        except Exception as e:
            logger.error(f"Failed to retrieve secret: {e}")
            raise

    def get_database_credentials(self, db_name: str) -> dict:
        """Get dynamic database credentials"""
        # Vault generates temporary credentials
        creds = self.client.secrets.database.generate_credentials(
            name=db_name
        )

        return {
            'username': creds['data']['username'],
            'password': creds['data']['password'],
            'ttl': creds['lease_duration']
        }

    def rotate_secret(self, path: str, new_value: dict):
        """Rotate a secret"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=new_value
        )

# Usage
secrets = SecretsManager(
    vault_url='https://vault.example.com',
    role_id=os.getenv('VAULT_ROLE_ID'),
    secret_id=os.getenv('VAULT_SECRET_ID')
)

# Get API key
api_key = secrets.get_secret('app/prod', 'api_key')

# Get dynamic DB credentials (auto-rotated)
db_creds = secrets.get_database_credentials('postgres-prod')
```

### AWS Secrets Manager

```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'us-east-1' });

async function getSecret(secretName) {
    try {
        const data = await secretsManager.getSecretValue({
            SecretId: secretName
        }).promise();

        if ('SecretString' in data) {
            return JSON.parse(data.SecretString);
        } else {
            // Binary secret
            return Buffer.from(data.SecretBinary, 'base64');
        }
    } catch (error) {
        console.error('Error retrieving secret:', error);
        throw error;
    }
}

// Usage
const dbCredentials = await getSecret('prod/database/credentials');
const client = new PostgresClient({
    host: dbCredentials.host,
    user: dbCredentials.username,
    password: dbCredentials.password
});
```

---

## 5. Security Monitoring & Observability

### Pattern Overview
Comprehensive security event logging, monitoring, and alerting

```python
# Structured security logging
import structlog
from datetime import datetime
from typing import Dict, Any

logger = structlog.get_logger()

class SecurityEventLogger:
    @staticmethod
    def log_authentication(
        event_type: str,
        user_id: str,
        success: bool,
        metadata: Dict[str, Any]
    ):
        """Log authentication events"""
        logger.info(
            "authentication_event",
            event_type=event_type,
            user_id=user_id,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            ip_address=metadata.get('ip_address'),
            user_agent=metadata.get('user_agent'),
            mfa_used=metadata.get('mfa_used', False)
        )

        # Alert on suspicious patterns
        if not success:
            failed_attempts = get_failed_login_count(user_id, window_minutes=10)
            if failed_attempts >= 5:
                SecurityEventLogger.alert_brute_force(user_id, metadata)

    @staticmethod
    def log_authorization(
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        reason: str = None
    ):
        """Log authorization decisions"""
        logger.info(
            "authorization_event",
            user_id=user_id,
            resource=resource,
            action=action,
            granted=granted,
            reason=reason,
            timestamp=datetime.utcnow().isoformat()
        )

        # Alert on repeated authorization failures
        if not granted:
            SecurityEventLogger.check_suspicious_access(user_id, resource)

    @staticmethod
    def log_data_access(
        user_id: str,
        data_type: str,
        action: str,
        count: int
    ):
        """Log sensitive data access"""
        logger.info(
            "data_access_event",
            user_id=user_id,
            data_type=data_type,
            action=action,
            count=count,
            timestamp=datetime.utcnow().isoformat()
        )

        # Alert on bulk data access
        if count > 1000:
            SecurityEventLogger.alert_bulk_data_access(user_id, data_type, count)

    @staticmethod
    def alert_brute_force(user_id: str, metadata: Dict[str, Any]):
        """Alert on brute force attempts"""
        send_security_alert(
            severity='HIGH',
            title='Potential Brute Force Attack',
            description=f'Multiple failed login attempts for user {user_id}',
            metadata=metadata,
            recommended_action='Review logs, consider account lockout'
        )
```

---

## 6. API Gateway Security Pattern

### Pattern Overview
Centralized API security enforcement

```
┌──────────────────────────────────────────────────┐
│              API Gateway Pattern                  │
├──────────────────────────────────────────────────┤
│                                                   │
│  Client ──▶ API Gateway ──▶ Backend Services     │
│             │                                     │
│             ├─ Authentication                     │
│             ├─ Rate Limiting                      │
│             ├─ Input Validation                   │
│             ├─ Request/Response Transform         │
│             ├─ Monitoring & Logging               │
│             └─ TLS Termination                    │
└──────────────────────────────────────────────────┘
```

### Kong API Gateway Configuration

```yaml
# Kong API Gateway security configuration
services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - name: user-route
        paths:
          - /api/users
    plugins:
      # Rate limiting
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
          policy: local

      # Authentication
      - name: jwt
        config:
          key_claim_name: kid
          secret_is_base64: false
          claims_to_verify:
            - exp
            - nbf

      # IP restriction
      - name: ip-restriction
        config:
          whitelist:
            - 10.0.0.0/8
            - 172.16.0.0/12

      # Request validation
      - name: request-validator
        config:
          body_schema: |
            {
              "type": "object",
              "required": ["email", "name"],
              "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string", "minLength": 1}
              }
            }

      # Response transformation (remove sensitive fields)
      - name: response-transformer
        config:
          remove:
            json:
              - password_hash
              - ssn
              - internal_id
```

---

## Pattern Selection Guide

| Pattern | Use Case | Complexity | Security Level |
|---------|----------|------------|----------------|
| Zero Trust | Enterprise, remote workforce | High | Highest |
| Defense in Depth | All applications | Medium | High |
| Least Privilege | All systems | Low | High |
| Secrets Management | All applications with secrets | Medium | Critical |
| Security Monitoring | All production systems | Medium | Essential |
| API Gateway | Microservices, API-heavy apps | Medium | High |

---

## References

- **Google BeyondCorp**: Zero Trust implementation
- **NIST SP 800-207**: Zero Trust Architecture
- **AWS Well-Architected**: Security Pillar
- **Microsoft Zero Trust**: Implementation guidance
- **OWASP**: Application Security Patterns

---

**Version**: 1.0
**Last Updated**: 2025-11-19
