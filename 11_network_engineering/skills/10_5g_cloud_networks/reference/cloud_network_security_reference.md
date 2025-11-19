# Cloud Network Security Reference

## Cloud Network Security Foundations

Cloud network security protects data in transit, controls access, prevents unauthorized connections, and ensures compliance with regulatory requirements.

## Defense in Depth Architecture

### Layered Security Model

**Layer 1: Perimeter**
- DDoS protection
- WAF (Web Application Firewall)
- Cloud DNS filtering
- Ingress filtering

**Layer 2: Network**
- Network ACLs
- Security Groups
- Network policies
- VPN encryption

**Layer 3: Transport**
- mTLS between services
- TLS 1.3 for HTTPS
- IPSec for tunnels
- DTLS for UDP

**Layer 4: Application**
- Authentication & authorization
- API gateways
- Rate limiting
- Input validation

**Layer 5: Data**
- Encryption at rest
- Encryption in transit
- Field-level encryption
- Tokenization

## Zero-Trust Architecture

### Zero-Trust Principles

1. **Never Trust, Always Verify**
   - Every access request authenticated
   - Every connection authorized
   - Continuous verification

2. **Least Privilege Access**
   - Minimal required permissions
   - Time-limited access
   - Revokable credentials

3. **Assume Breach**
   - Lateral movement prevention
   - Immediate incident response
   - Continuous monitoring

### Implementation Components

**Identity & Access Management**
```
User/Device --> MFA --> Identity Provider --> Policy Engine
                          |                       |
                     Device Posture ---------->Policy Decision
```

**Network Segmentation**
- Micro-segmentation by:
  - User identity
  - Device type
  - Application
  - Sensitivity level

**Continuous Monitoring**
- Real-time threat detection
- Behavioral analytics
- Anomaly detection
- Audit logging

## Network Segmentation

### Logical Segmentation

**VPC/VNet Boundaries**
- Separate VPCs for different environments
- Dev/Staging/Production isolation
- Customer tenant isolation
- Compliance boundary enforcement

**Subnet-Level Segmentation**
```
VPC: 10.0.0.0/16
├── Public Subnet: 10.0.1.0/24 (DMZ)
├── App Subnet: 10.0.2.0/24 (Private)
├── Database Subnet: 10.0.3.0/24 (Private)
└── Management Subnet: 10.0.4.0/24 (Private)
```

### Micro-Segmentation

**Container-Level Segmentation**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-isolation
spec:
  podSelector:
    matchLabels:
      app: payment
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: api
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## DDoS Protection

### Attack Vectors
- **Volumetric** - Bandwidth saturation (UDP floods, DNS amplification)
- **Protocol** - Protocol exploitation (SYN floods, Ping of Death)
- **Application** - Layer 7 attacks (HTTP floods, Slowloris)

### Cloud DDoS Solutions

**AWS Shield**
- Standard: Always-on, free
- Advanced: $3,000/month
- WAF integration
- Real-time protection

**Azure DDoS Protection**
- Standard: Free, basic protection
- Premium: $2,944/month
- Advanced analytics
- Custom policies

**GCP Cloud Armor**
- Pay-per-request model
- Layer 7 filtering
- Custom rules
- Preconfigured rules

### DDoS Mitigation Strategies

1. **Rate Limiting**
   - Requests per IP
   - Connection limits
   - Bandwidth throttling

2. **Geographic Blocking**
   - Country-level blocking
   - Regional distribution
   - GeoIP filtering

3. **Behavioral Analysis**
   - Traffic pattern detection
   - Anomaly alerts
   - Bot detection

## Web Application Firewall (WAF)

### WAF Rules

**SQL Injection Protection**
```
Pattern: (UNION|SELECT|INSERT|DELETE|DROP)
Action: Block
```

**Cross-Site Scripting (XSS) Protection**
```
Pattern: <script|onclick|onerror
Action: Block
```

**Path Traversal Protection**
```
Pattern: \.\.\/|\.\.\\
Action: Block
```

### Cloud WAF Implementations

**AWS WAF**
- Web ACLs
- Rules and rule groups
- Managed rule groups
- Custom rate-based rules

**Azure WAF**
- Application Gateway integration
- Front Door integration
- Managed rulesets
- Custom rules

**GCP Cloud Armor**
- Security policies
- Adaptive protection
- Custom rules
- Rules preview

## Encryption & Cryptography

### Encryption in Transit

**TLS/SSL Configuration**
```
Minimum: TLS 1.2
Recommended: TLS 1.3
Ciphers: AEAD suites (AES-GCM, ChaCha20-Poly1305)
Key Exchange: ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)
```

**mTLS Implementation**
```
Client Certificate Auth
↓
Server validates client cert
↓
Server Certificate Auth
↓
Client validates server cert
↓
Encrypted channel established
```

### Encryption at Rest

**Key Management**
```
Application
    ↓ (plaintext)
Encryption Service
    ↓ (request KMS key)
KMS Service
    ↓ (returns key)
Encryption Service
    ↓ (encrypt data)
Storage
```

**Key Rotation**
- Automatic rotation: Every 90 days
- Manual rotation on demand
- Old keys retained for decryption
- Secure key disposal

## Access Control

### Identity and Access Management (IAM)

**AWS IAM Policies**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:DescribeInstances",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "10.0.0.0/8"
        }
      }
    }
  ]
}
```

**Azure RBAC**
- Role definitions
- Scope: Subscription/RG/Resource
- Built-in and custom roles
- Conditional access

**GCP IAM**
- Roles: Basic, Predefined, Custom
- Service accounts
- Workload identity
- Conditions

### API Gateway Security

**Authentication Methods**
- API keys
- OAuth 2.0
- JWT tokens
- mTLS certificates

**Rate Limiting**
```
Per-user rate limits
Per-API rate limits
Burst allowance
Tiered throttling
```

## Compliance & Auditing

### Compliance Frameworks

**PCI DSS**
- Network segmentation
- Encryption of sensitive data
- Access controls
- Audit logging

**HIPAA**
- Data encryption
- Access controls
- Audit trails
- Business associate agreements

**GDPR**
- Data residency
- Data deletion
- Consent management
- Breach notification

### Audit Logging

**Log Collection**
```
Application Logs
    ↓
Log Aggregation Service
    ↓
Centralized Storage (S3/Blob/GCS)
    ↓
Long-term Retention & Analysis
```

**Log Content**
- Source and destination IPs
- Port numbers
- Protocol
- Action (allow/deny)
- Timestamp
- User identity

**AWS CloudTrail Example**
```json
{
  "eventVersion": "1.05",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAI23HXD2O5Y2EXAMPLE"
  },
  "eventTime": "2023-11-19T12:34:56Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "CreateSecurityGroup",
  "requestParameters": {
    "groupName": "web-sg"
  },
  "responseElements": {
    "groupId": "sg-0123456789abcdef"
  }
}
```

## Threat Detection

### Anomaly Detection

**Traffic Pattern Analysis**
- Baseline establishment
- Deviation detection
- Alert generation
- Automated response

**Behavioral Analytics**
- User behavior profiling
- Connection pattern analysis
- Data access monitoring
- Privilege escalation detection

### Intrusion Detection/Prevention (IDS/IPS)

**Network-Based IDS/IPS**
- Packet inspection
- Signature matching
- Anomaly detection
- Automated blocking

**Host-Based IDS/IPS**
- System call monitoring
- File integrity checking
- Process monitoring
- Log analysis

## Secrets Management

### Secret Storage

**Cloud KMS Solutions**
- AWS Secrets Manager
- Azure Key Vault
- GCP Secret Manager
- HashiCorp Vault

**Secrets in Applications**
```
Application Request
    ↓
Authenticate to Secrets Service
    ↓
Retrieve Secret (cached/TTL)
    ↓
Use Secret in-memory
    ↓
Automatic Rotation
```

### Secret Rotation

**Automated Rotation**
```
Generate new secret
    ↓
Update in KMS
    ↓
Notify applications
    ↓
Wait for grace period
    ↓
Disable old secret
    ↓
Audit log
```

## Cloud Network Security Best Practices

### Design Principles
1. **Defense in Depth** - Multiple security layers
2. **Least Privilege** - Minimal permissions
3. **Secure by Default** - Explicit allows
4. **Compliance First** - Regulatory alignment
5. **Monitoring Focus** - Comprehensive logging

### Implementation Checklist
- [ ] VPC/VNet isolation per environment
- [ ] All traffic encrypted in transit
- [ ] Network ACLs and Security Groups configured
- [ ] DDoS protection enabled
- [ ] WAF rules deployed
- [ ] Secrets management implemented
- [ ] Audit logging enabled
- [ ] Security group reviews scheduled
- [ ] Incident response plan documented
- [ ] Regular security assessments

### Monitoring & Response

**Key Metrics**
- Failed authentication attempts
- Policy violations
- Unusual traffic patterns
- Port scan attempts
- Data exfiltration indicators

**Incident Response**
1. Detection and alerting
2. Investigation and containment
3. Remediation
4. Recovery
5. Post-incident review

---

**Reference:** AWS Security, Azure Security, GCP Security Documentation
**Last Updated:** 2025-11-19
