# Security Architecture Patterns

## Overview

Security architecture patterns provide proven approaches to protecting cloud applications, data, and infrastructure from threats. This guide covers essential security patterns implementing defense-in-depth, zero trust, and principle of least privilege.

## Table of Contents

1. [Zero Trust Pattern](#zero-trust-pattern)
2. [Defense in Depth Pattern](#defense-in-depth-pattern)
3. [Secrets Management Pattern](#secrets-management-pattern)
4. [Least Privilege Pattern](#least-privilege-pattern)
5. [Encryption Patterns](#encryption-patterns)
6. [Identity and Access Management](#identity-and-access-management)
7. [Security Monitoring Pattern](#security-monitoring-pattern)
8. [Network Segmentation Pattern](#network-segmentation-pattern)

## Security Principles

```
┌──────────────────────────────────────────┐
│      Core Security Principles            │
├──────────────────────────────────────────┤
│                                          │
│  1. Defense in Depth                    │
│     Multiple layers of security         │
│                                          │
│  2. Least Privilege                     │
│     Minimum necessary permissions       │
│                                          │
│  3. Zero Trust                          │
│     Never trust, always verify          │
│                                          │
│  4. Security by Design                  │
│     Built-in, not bolted-on             │
│                                          │
│  5. Fail Securely                       │
│     Secure defaults, fail closed        │
│                                          │
│  6. Separation of Duties                │
│     Prevent single point of compromise  │
│                                          │
│  7. Complete Mediation                  │
│     Check every access                  │
│                                          │
└──────────────────────────────────────────┘
```

---

## 1. Zero Trust Pattern

### Description

"Never trust, always verify" - assumes breach and verifies every request regardless of source. No implicit trust based on network location.

### When to Use

- Modern cloud-native applications
- Remote workforce
- Multi-cloud environments
- Microservices architecture
- High security requirements
- Compliance requirements (PCI-DSS, HIPAA)

### Zero Trust Principles

```
┌──────────────────────────────────────────┐
│        Zero Trust Architecture           │
├──────────────────────────────────────────┤
│                                          │
│  1. Verify Explicitly                   │
│     - Always authenticate & authorize   │
│     - Use all data points               │
│                                          │
│  2. Least Privilege Access              │
│     - Just-in-time access               │
│     - Just-enough access                │
│                                          │
│  3. Assume Breach                       │
│     - Segment access                    │
│     - Verify end-to-end encryption      │
│     - Monitor and log everything        │
│                                          │
└──────────────────────────────────────────┘
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│          Zero Trust Architecture                 │
└──────────────────────────────────────────────────┘

         User/Device
              │
              │ 1. Authentication
              ▼
      ┌──────────────┐
      │  Identity    │
      │  Provider    │◄──── MFA Required
      │  (Okta/Auth0)│
      └──────┬───────┘
             │ 2. Token
             │
             ▼
      ┌──────────────┐
      │   Policy     │
      │   Engine     │◄──── Context: Device, Location,
      │   (OPA)      │      Time, Risk Score
      └──────┬───────┘
             │ 3. Authorization Decision
             │
             ▼
      ┌──────────────┐
      │   Gateway    │
      │   (Envoy)    │
      └──────┬───────┘
             │ 4. Encrypted Connection (mTLS)
             │
      ┌──────▼───────┬──────────┬──────────┐
      │              │          │          │
  ┌───▼───┐    ┌────▼────┐┌───▼────┐┌───▼────┐
  │Service│    │Service  ││Service ││Service │
  │  A    │    │   B     ││   C    ││   D    │
  └───────┘    └─────────┘└────────┘└────────┘
      │              │          │          │
      └──────────────┴──────────┴──────────┘
                     │
              ┌──────▼───────┐
              │ Continuous   │
              │ Monitoring   │
              │ & Analytics  │
              └──────────────┘
```

### Implementation Example

```python
# zero_trust_gateway.py
from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests

@dataclass
class AuthContext:
    """Authentication context for zero trust"""
    user_id: str
    device_id: str
    ip_address: str
    location: str
    timestamp: datetime
    risk_score: float
    mfa_verified: bool

class ZeroTrustGateway:
    def __init__(self, policy_engine_url: str, secret_key: str):
        self.policy_engine_url = policy_engine_url
        self.secret_key = secret_key

    def authenticate(self, username: str, password: str,
                    mfa_token: str, context: Dict) -> Optional[str]:
        """
        Authenticate user with MFA and context

        Returns JWT token if successful
        """
        # 1. Verify credentials
        if not self._verify_credentials(username, password):
            return None

        # 2. Verify MFA
        if not self._verify_mfa(username, mfa_token):
            return None

        # 3. Assess risk
        auth_context = AuthContext(
            user_id=username,
            device_id=context.get('device_id'),
            ip_address=context.get('ip_address'),
            location=context.get('location'),
            timestamp=datetime.now(),
            risk_score=self._calculate_risk_score(context),
            mfa_verified=True
        )

        # 4. Check against policy
        if not self._check_policy(auth_context):
            return None

        # 5. Generate token
        token = self._generate_token(auth_context)

        return token

    def authorize(self, token: str, resource: str, action: str) -> bool:
        """
        Authorize access to resource
        Zero trust: verify every request
        """
        # 1. Verify token
        try:
            claims = jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return False

        # 2. Check token expiration (short-lived tokens)
        if datetime.fromtimestamp(claims['exp']) < datetime.now():
            return False

        # 3. Verify against policy engine
        policy_decision = self._query_policy_engine(
            user_id=claims['user_id'],
            resource=resource,
            action=action,
            context=claims['context']
        )

        # 4. Log access attempt
        self._log_access(claims['user_id'], resource, action, policy_decision)

        return policy_decision

    def _verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password"""
        # Implementation would check against identity provider
        return True

    def _verify_mfa(self, username: str, mfa_token: str) -> bool:
        """Verify MFA token"""
        # Implementation would verify TOTP/SMS code
        return True

    def _calculate_risk_score(self, context: Dict) -> float:
        """
        Calculate risk score based on context
        - New device: +30
        - Unusual location: +25
        - Unusual time: +15
        - Failed attempts: +20
        - VPN/Proxy: +10
        """
        risk_score = 0.0

        # Check device
        if not self._is_known_device(context.get('device_id')):
            risk_score += 30

        # Check location
        if not self._is_usual_location(context.get('location')):
            risk_score += 25

        # Check time
        if not self._is_business_hours():
            risk_score += 15

        # Check IP reputation
        if self._is_suspicious_ip(context.get('ip_address')):
            risk_score += 20

        return risk_score

    def _check_policy(self, context: AuthContext) -> bool:
        """Check if authentication meets policy requirements"""

        # High risk requires additional verification
        if context.risk_score > 50:
            # Would trigger additional verification
            return False

        return True

    def _generate_token(self, context: AuthContext) -> str:
        """Generate short-lived JWT token"""
        expiration = datetime.now() + timedelta(minutes=15)  # Short-lived

        claims = {
            'user_id': context.user_id,
            'exp': expiration.timestamp(),
            'context': {
                'device_id': context.device_id,
                'ip_address': context.ip_address,
                'location': context.location,
                'risk_score': context.risk_score
            }
        }

        token = jwt.encode(claims, self.secret_key, algorithm='HS256')
        return token

    def _query_policy_engine(self, user_id: str, resource: str,
                            action: str, context: Dict) -> bool:
        """Query Open Policy Agent for authorization decision"""
        response = requests.post(
            f"{self.policy_engine_url}/v1/data/authz/allow",
            json={
                'input': {
                    'user': user_id,
                    'resource': resource,
                    'action': action,
                    'context': context
                }
            }
        )

        return response.json().get('result', False)

    def _log_access(self, user_id: str, resource: str,
                   action: str, allowed: bool):
        """Log all access attempts for audit"""
        # Implementation would send to SIEM/logging system
        pass

    def _is_known_device(self, device_id: str) -> bool:
        # Check device registry
        return True

    def _is_usual_location(self, location: str) -> bool:
        # Check against user's typical locations
        return True

    def _is_business_hours(self) -> bool:
        # Check if current time is business hours
        return True

    def _is_suspicious_ip(self, ip: str) -> bool:
        # Check IP reputation
        return False
```

### Open Policy Agent (OPA) Policy

```rego
# authz.rego - Zero Trust Authorization Policy
package authz

import future.keywords.if

# Default deny
default allow = false

# Allow if all conditions met
allow if {
    # User authenticated with MFA
    input.context.mfa_verified == true

    # Risk score acceptable
    input.context.risk_score < 50

    # User has permission
    has_permission

    # Device is compliant
    device_compliant

    # Request from allowed location
    location_allowed
}

# Check user permissions
has_permission if {
    # Get user roles
    user_roles := data.roles[input.user]

    # Check if any role grants permission
    some role in user_roles
    data.permissions[role][input.resource][input.action]
}

# Check device compliance
device_compliant if {
    device := data.devices[input.context.device_id]
    device.compliant == true
    device.last_scan_days < 7
}

# Check location
location_allowed if {
    # Allow from corporate network
    input.context.ip_address in data.corporate_networks
}

location_allowed if {
    # Allow from approved countries
    input.context.location in data.approved_countries
}
```

### Terraform - Zero Trust Infrastructure

```hcl
# zero_trust_infrastructure.tf

# Service Mesh for mTLS
resource "aws_appmesh_mesh" "zero_trust" {
  name = "zero-trust-mesh"

  spec {
    egress_filter {
      type = "DROP_ALL"  # Deny by default
    }
  }
}

# Virtual Gateway with TLS
resource "aws_appmesh_virtual_gateway" "gateway" {
  name      = "zero-trust-gateway"
  mesh_name = aws_appmesh_mesh.zero_trust.id

  spec {
    listener {
      port_mapping {
        port     = 443
        protocol = "http"
      }

      tls {
        mode = "STRICT"

        certificate {
          acm {
            certificate_arn = aws_acm_certificate.gateway.arn
          }
        }

        validation {
          trust {
            file {
              certificate_chain = "/etc/ssl/certs/ca-bundle.crt"
            }
          }
        }
      }
    }
  }
}

# Network segmentation
resource "aws_security_group" "zero_trust" {
  name        = "zero-trust-sg"
  description = "Zero trust security group - deny by default"
  vpc_id      = var.vpc_id

  # No default ingress - explicit allow required
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Zero Trust Security Group"
  }
}

# Explicit allow rules (least privilege)
resource "aws_security_group_rule" "allow_https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = var.allowed_cidrs
  security_group_id = aws_security_group.zero_trust.id
}

# WAF for application layer protection
resource "aws_wafv2_web_acl" "zero_trust" {
  name  = "zero-trust-waf"
  scope = "REGIONAL"

  default_action {
    block {}  # Default deny
  }

  # Rate limiting
  rule {
    name     = "rate-limit"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Geo blocking
  rule {
    name     = "geo-block"
    priority = 2

    action {
      block {}
    }

    statement {
      geo_match_statement {
        country_codes = var.blocked_countries
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "geo-block"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "zero-trust-waf"
    sampled_requests_enabled   = true
  }
}
```

### Trade-offs

**Pros:**
- Maximum security posture
- Granular access control
- Reduces attack surface
- Supports remote workforce
- Compliance friendly

**Cons:**
- Implementation complexity
- Performance overhead
- User friction (more auth steps)
- Operational overhead
- Legacy system challenges

### Anti-patterns

- **Implicit Trust**: Trusting based on network location
- **Weak MFA**: SMS-based MFA (vulnerable to SIM swapping)
- **Long-Lived Tokens**: Tokens that don't expire
- **Missing Monitoring**: Not logging all access attempts

### Real-world Examples

**Google**: BeyondCorp - pioneered zero trust approach.

**Microsoft**: Azure AD Conditional Access for zero trust.

**Okta**: Zero Trust Platform for identity-based security.

---

## 2. Defense in Depth Pattern

### Description

Multiple layers of security controls throughout the system, so if one layer fails, others provide protection.

### Security Layers

```
┌──────────────────────────────────────────┐
│      Defense in Depth Layers             │
├──────────────────────────────────────────┤
│                                          │
│  Layer 7: Data                          │
│  - Encryption at rest                   │
│  - Data classification                  │
│  - DLP (Data Loss Prevention)           │
│                                          │
│  Layer 6: Application                   │
│  - Input validation                     │
│  - OWASP Top 10 protection              │
│  - WAF (Web Application Firewall)       │
│                                          │
│  Layer 5: Endpoint                      │
│  - EDR (Endpoint Detection)             │
│  - Antivirus                            │
│  - Patch management                     │
│                                          │
│  Layer 4: Network                       │
│  - Network segmentation                 │
│  - Firewalls                            │
│  - IDS/IPS                              │
│                                          │
│  Layer 3: Perimeter                     │
│  - DDoS protection                      │
│  - VPN                                  │
│  - SIEM                                 │
│                                          │
│  Layer 2: Identity                      │
│  - MFA                                  │
│  - SSO                                  │
│  - IAM                                  │
│                                          │
│  Layer 1: Physical                      │
│  - Datacenter security                  │
│  - Access controls                      │
│                                          │
└──────────────────────────────────────────┘
```

### Real-world Examples

**AWS**: Multiple security layers (IAM, Security Groups, NACLs, WAF, GuardDuty).

**Microsoft**: Defense in depth across Azure security stack.

---

## 3. Secrets Management Pattern

### Description

Centralized, secure storage and access control for sensitive information (passwords, API keys, certificates).

### When to Use

- Storing credentials
- API keys and tokens
- Database passwords
- TLS certificates
- Encryption keys
- Any sensitive configuration

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│        Secrets Management Architecture           │
└──────────────────────────────────────────────────┘

   Application
        │
        │ 1. Request secret (with auth)
        ▼
  ┌──────────────┐
  │   Secrets    │
  │   Manager    │◄──── Encryption at rest
  │(Vault/KMS)   │◄──── Audit logging
  └──────┬───────┘◄──── Access policies
         │
         │ 2. Return secret
         │ (encrypted in transit)
         │
         ▼
   Application
   (Secret in memory only,
    never written to disk)
```

### Implementation Example

```python
# secrets_manager.py
import boto3
import json
from typing import Dict, Any
import hvac  # HashiCorp Vault client
from dataclasses import dataclass
from abc import ABC, abstractmethod

class SecretsProvider(ABC):
    """Abstract secrets provider"""

    @abstractmethod
    def get_secret(self, name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_secret(self, name: str, value: Dict[str, Any]):
        pass

    @abstractmethod
    def delete_secret(self, name: str):
        pass

class AWSSecretsManager(SecretsProvider):
    """AWS Secrets Manager implementation"""

    def __init__(self, region: str = 'us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region)

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Get secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=name)
            return json.loads(response['SecretString'])
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            raise

    def set_secret(self, name: str, value: Dict[str, Any]):
        """Store secret in AWS Secrets Manager"""
        try:
            self.client.create_secret(
                Name=name,
                SecretString=json.dumps(value),
                KmsKeyId='alias/aws/secretsmanager'  # Use KMS for encryption
            )
        except self.client.exceptions.ResourceExistsException:
            # Update if exists
            self.client.update_secret(
                SecretId=name,
                SecretString=json.dumps(value)
            )

    def delete_secret(self, name: str):
        """Delete secret"""
        self.client.delete_secret(
            SecretId=name,
            ForceDeleteWithoutRecovery=False,
            RecoveryWindowInDays=30  # Allow recovery
        )

    def rotate_secret(self, name: str):
        """Trigger secret rotation"""
        self.client.rotate_secret(
            SecretId=name,
            RotationLambdaARN='arn:aws:lambda:...'
        )


class HashiCorpVault(SecretsProvider):
    """HashiCorp Vault implementation"""

    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Get secret from Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(path=name)
        return secret['data']['data']

    def set_secret(self, name: str, value: Dict[str, Any]):
        """Store secret in Vault"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=name,
            secret=value
        )

    def delete_secret(self, name: str):
        """Delete secret"""
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=name)

    def create_dynamic_secret(self, database_name: str, role: str) -> Dict:
        """Create dynamic database credentials"""
        creds = self.client.secrets.database.generate_credentials(
            name=role,
            mount_point='database'
        )
        return creds['data']


class SecretsCache:
    """Cache secrets in memory with TTL"""

    def __init__(self, provider: SecretsProvider, ttl: int = 300):
        self.provider = provider
        self.ttl = ttl
        self.cache = {}

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Get secret with caching"""
        from datetime import datetime, timedelta

        # Check cache
        if name in self.cache:
            cached_secret, cached_time = self.cache[name]
            if datetime.now() < cached_time + timedelta(seconds=self.ttl):
                return cached_secret

        # Fetch from provider
        secret = self.provider.get_secret(name)

        # Cache it
        self.cache[name] = (secret, datetime.now())

        return secret


# Usage example
class DatabaseConnection:
    """Database connection using secrets manager"""

    def __init__(self, secrets_manager: SecretsProvider):
        self.secrets_manager = secrets_manager

    def connect(self, db_name: str):
        """Connect using credentials from secrets manager"""
        # Get credentials
        secret = self.secrets_manager.get_secret(f'database/{db_name}')

        # Create connection (credentials never in code or environment)
        import psycopg2
        conn = psycopg2.connect(
            host=secret['host'],
            database=secret['database'],
            user=secret['username'],
            password=secret['password'],
            port=secret.get('port', 5432)
        )

        return conn


# Automatic secret rotation
class SecretRotator:
    """Automatic secret rotation"""

    def __init__(self, secrets_manager: SecretsProvider):
        self.secrets_manager = secrets_manager

    def rotate_database_password(self, secret_name: str):
        """Rotate database password"""
        import secrets
        import string

        # Generate new password
        alphabet = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        # Get current secret
        current_secret = self.secrets_manager.get_secret(secret_name)

        # Update database
        self._update_database_password(
            current_secret['host'],
            current_secret['username'],
            current_secret['password'],
            new_password
        )

        # Update secret
        current_secret['password'] = new_password
        self.secrets_manager.set_secret(secret_name, current_secret)

    def _update_database_password(self, host: str, username: str,
                                  old_password: str, new_password: str):
        """Update password in database"""
        # Implementation depends on database type
        pass
```

### Terraform - AWS Secrets Manager

```hcl
# secrets_manager.tf

# Database credentials secret
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "production/database/credentials"
  description             = "Production database credentials"
  recovery_window_in_days = 30

  tags = {
    Environment = "production"
    Managed     = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id

  secret_string = jsonencode({
    username = "dbadmin"
    password = random_password.db_password.result
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    database = "production"
  })
}

# Generate secure password
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Rotation Lambda
resource "aws_lambda_function" "secret_rotation" {
  filename      = "rotation_function.zip"
  function_name = "secret-rotation"
  role          = aws_iam_role.rotation_lambda.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  environment {
    variables = {
      SECRETS_MANAGER_ENDPOINT = "https://secretsmanager.${var.region}.amazonaws.com"
    }
  }
}

# Rotation schedule
resource "aws_secretsmanager_secret_rotation" "db_rotation" {
  secret_id           = aws_secretsmanager_secret.db_credentials.id
  rotation_lambda_arn = aws_lambda_function.secret_rotation.arn

  rotation_rules {
    automatically_after_days = 30
  }
}

# IAM policy for application to read secret
resource "aws_iam_policy" "read_db_secret" {
  name        = "read-db-secret"
  description = "Allow reading database secret"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = aws_kms_key.secrets.arn
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${var.region}.amazonaws.com"
          }
        }
      }
    ]
  })
}

# KMS key for secret encryption
resource "aws_kms_key" "secrets" {
  description             = "KMS key for secrets encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "Secrets Encryption Key"
  }
}
```

### Best Practices

```
┌──────────────────────────────────────────┐
│    Secrets Management Best Practices     │
├──────────────────────────────────────────┤
│                                          │
│  ✓ Never commit secrets to code         │
│  ✓ Use secrets manager, not env vars    │
│  ✓ Rotate secrets regularly (30-90 days)│
│  ✓ Use short-lived credentials          │
│  ✓ Encrypt at rest with KMS             │
│  ✓ Encrypt in transit with TLS          │
│  ✓ Audit all secret access              │
│  ✓ Principle of least privilege         │
│  ✓ Use dynamic secrets when possible    │
│  ✓ Implement emergency rotation         │
│                                          │
└──────────────────────────────────────────┘
```

### Real-world Examples

**HashiCorp**: Vault for secrets management at scale.

**AWS**: Secrets Manager with automatic rotation.

**1Password**: Secrets Automation for development teams.

---

## 4. Least Privilege Pattern

### Description

Grant only the minimum permissions necessary to perform required tasks. Reduce blast radius of compromised credentials.

### Implementation with IAM

```hcl
# least_privilege_iam.tf

# Application role with minimal permissions
resource "aws_iam_role" "app_role" {
  name = "app-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Specific permission for S3 bucket (not all buckets)
resource "aws_iam_policy" "app_s3_access" {
  name = "app-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.app_data.arn}/user-uploads/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.app_data.arn
        Condition = {
          StringLike = {
            "s3:prefix" = "user-uploads/*"
          }
        }
      }
    ]
  })
}

# Time-based permissions
resource "aws_iam_policy" "business_hours_only" {
  name = "business-hours-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ec2:*"]
        Resource = "*"
        Condition = {
          DateGreaterThan = {
            "aws:CurrentTime" = "2024-01-01T09:00:00Z"
          }
          DateLessThan = {
            "aws:CurrentTime" = "2024-01-01T17:00:00Z"
          }
        }
      }
    ]
  })
}
```

### Real-world Examples

**AWS**: IAM with fine-grained permissions.

**Google**: Cloud IAM with predefined and custom roles.

---

## 5. Encryption Patterns

### Description

Protect data confidentiality through encryption at rest and in transit.

### Encryption Strategy

```
┌──────────────────────────────────────────┐
│       Encryption Best Practices          │
├──────────────────────────────────────────┤
│                                          │
│  At Rest:                               │
│  - Database encryption                  │
│  - Disk encryption                      │
│  - S3 encryption (SSE-KMS)             │
│  - Backup encryption                    │
│                                          │
│  In Transit:                            │
│  - TLS 1.2+ only                       │
│  - Strong cipher suites                 │
│  - Certificate pinning                  │
│  - mTLS for service-to-service         │
│                                          │
│  Key Management:                        │
│  - Use KMS/HSM                         │
│  - Rotate keys regularly                │
│  - Separate keys by environment         │
│  - Envelope encryption                  │
│                                          │
└──────────────────────────────────────────┘
```

### Implementation Example

```python
# encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import boto3
import base64

class EncryptionService:
    """Application-level encryption service"""

    def __init__(self, kms_key_id: str):
        self.kms = boto3.client('kms')
        self.kms_key_id = kms_key_id

    def encrypt_data(self, plaintext: bytes) -> dict:
        """Envelope encryption using KMS"""

        # Generate data key
        response = self.kms.generate_data_key(
            KeyId=self.kms_key_id,
            KeySpec='AES_256'
        )

        data_key = response['Plaintext']
        encrypted_data_key = response['CiphertextBlob']

        # Encrypt data with data key
        f = Fernet(base64.urlsafe_b64encode(data_key))
        ciphertext = f.encrypt(plaintext)

        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'encrypted_key': base64.b64encode(encrypted_data_key).decode()
        }

    def decrypt_data(self, encrypted_data: dict) -> bytes:
        """Decrypt data using KMS"""

        # Decrypt data key
        encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
        response = self.kms.decrypt(CiphertextBlob=encrypted_key)
        data_key = response['Plaintext']

        # Decrypt data
        f = Fernet(base64.urlsafe_b64encode(data_key))
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        plaintext = f.decrypt(ciphertext)

        return plaintext
```

---

## Summary

Security patterns provide defense against:
- **Unauthorized Access**: Zero Trust, Least Privilege
- **Data Breaches**: Encryption, Secrets Management
- **Attack Vectors**: Defense in Depth, Network Segmentation
- **Compliance**: Audit logging, Access controls

### Security Implementation Checklist

```
☐ Implement Zero Trust architecture
☐ Enable MFA for all users
☐ Use secrets manager (no hardcoded credentials)
☐ Encrypt data at rest and in transit
☐ Implement least privilege IAM
☐ Enable comprehensive logging
☐ Set up security monitoring (SIEM)
☐ Regular security assessments
☐ Incident response plan
☐ Disaster recovery plan
```

### FAANG Security Practices

- **Amazon**: AWS security services (GuardDuty, Security Hub, Macie)
- **Facebook**: Zero Trust with BeyondCorp-like approach
- **Apple**: Strong encryption and privacy by design
- **Netflix**: Comprehensive security automation
- **Google**: BeyondCorp zero trust model

**Remember**: Security is not a product, it's a process. Continuous improvement and adaptation are essential.
