# Cloud Security Documentation Standards

## Overview

This guide establishes standards for security documentation in cloud environments, including threat models, security reviews, and compliance documentation. Based on NIST Cybersecurity Framework, CIS Controls, OWASP standards, AWS Security Best Practices, Microsoft Security Development Lifecycle (SDL), and Google's BeyondCorp security model.

## Table of Contents

1. [Security Documentation Principles](#security-documentation-principles)
2. [Threat Modeling](#threat-modeling)
3. [Security Review Process](#security-review-process)
4. [Security Architecture Documentation](#security-architecture-documentation)
5. [Compliance Documentation](#compliance-documentation)
6. [Incident Response Documentation](#incident-response-documentation)
7. [Security Metrics and Reporting](#security-metrics-and-reporting)
8. [Tools and Automation](#tools-and-automation)
9. [Anti-Patterns](#anti-patterns)
10. [References](#references)

## Security Documentation Principles

### Core Tenets

1. **Defense in Depth**: Document security controls at all layers
2. **Least Privilege**: Document access controls and justifications
3. **Zero Trust**: Assume breach, verify explicitly
4. **Auditability**: All security decisions must be traceable
5. **Continuous Validation**: Security documentation is living, not static
6. **Compliance by Design**: Embed regulatory requirements from start
7. **Privacy by Default**: Data protection and privacy considerations
8. **Security as Code**: Codify security controls and policies

### Documentation Hierarchy

```
/docs/security/
├── threat-models/
│   ├── application-threats.md
│   ├── infrastructure-threats.md
│   └── data-flow-diagrams/
├── security-reviews/
│   ├── 2024-q1-webapp-review.md
│   ├── 2024-q2-api-review.md
│   └── templates/
├── architecture/
│   ├── network-security.md
│   ├── identity-access-mgmt.md
│   ├── data-protection.md
│   └── diagrams/
├── compliance/
│   ├── pci-dss/
│   ├── hipaa/
│   ├── soc2/
│   └── gdpr/
├── policies/
│   ├── acceptable-use.md
│   ├── data-classification.md
│   └── incident-response.md
├── runbooks/
│   ├── security-incident-response.md
│   ├── breach-notification.md
│   └── disaster-recovery.md
└── audits/
    ├── vulnerability-scans/
    ├── penetration-tests/
    └── compliance-audits/
```

## Threat Modeling

### STRIDE Threat Model Template

STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) - Microsoft's threat modeling framework.

```markdown
# Threat Model: {Application/System Name}

**Document Version**: 1.2
**Last Updated**: 2024-03-15
**Owner**: security-team@company.com
**Reviewers**: architecture-team, platform-team
**Status**: Approved

## 1. System Overview

### 1.1 Business Context
Brief description of the application's business purpose, users, and criticality.

**Criticality**: High | Medium | Low
**Data Classification**: Public | Internal | Confidential | Restricted
**Compliance Requirements**: PCI-DSS, HIPAA, SOC2, GDPR

### 1.2 System Description
High-level architecture and key components.

### 1.3 Scope
What is in scope for this threat model and what is explicitly out of scope.

**In Scope**:
- Web application frontend
- API backend services
- Database layer
- Authentication/authorization
- Data storage and transmission

**Out of Scope**:
- Third-party SaaS integrations (covered in separate model)
- Client devices

## 2. Architecture Diagrams

### 2.1 Data Flow Diagram (DFD)

```
[User] --HTTPS--> [CloudFront CDN] --HTTPS--> [ALB] --HTTPS--> [API Gateway]
                                                                      |
                                                                      v
[API Gateway] --mTLS--> [ECS Services] --VPC--> [RDS PostgreSQL]
                              |                        |
                              v                        v
                       [ElastiCache]            [S3 Encrypted]
```

### 2.2 Trust Boundaries

1. **Internet to CDN**: Public internet users
2. **CDN to ALB**: AWS CloudFront to Application Load Balancer
3. **ALB to API Gateway**: Load balancer to API layer
4. **API Gateway to Services**: API to microservices
5. **Services to Data**: Application to data stores

## 3. Assets

### 3.1 Data Assets

| Asset | Classification | Location | Encryption | Backup |
|-------|----------------|----------|------------|--------|
| User PII | Restricted | RDS | AES-256 at rest, TLS 1.3 in transit | Daily |
| Payment Data | Restricted | Stripe (external) | N/A - no storage | N/A |
| Session Tokens | Confidential | ElastiCache | TLS in transit | No |
| Application Logs | Internal | S3 | SSE-S3 | 90-day retention |
| Access Logs | Internal | CloudWatch | Encrypted | 1-year retention |

### 3.2 System Assets

| Asset | Type | Criticality | Dependencies |
|-------|------|-------------|--------------|
| API Services | ECS Fargate | High | RDS, ElastiCache |
| Database | RDS PostgreSQL | Critical | Multi-AZ enabled |
| Cache | ElastiCache Redis | Medium | None |
| CDN | CloudFront | High | S3 origin |

## 4. Threat Identification (STRIDE Analysis)

### 4.1 Spoofing Identity

#### Threat S1: User Authentication Bypass
**Description**: Attacker attempts to bypass authentication mechanisms
**Attack Vector**:
- Credential stuffing
- Session hijacking
- Token forgery

**Existing Controls**:
- JWT with RS256 signing
- MFA enforcement for privileged users
- Rate limiting on authentication endpoints
- Session timeout (30 minutes idle, 8 hours absolute)

**Risk Rating**: Medium (Likelihood: Low, Impact: High)
**Mitigation Status**: ✅ Mitigated
**Additional Controls**: None required

#### Threat S2: Service-to-Service Authentication Spoofing
**Description**: Attacker impersonates internal service
**Attack Vector**:
- Stolen service credentials
- Network position exploitation

**Existing Controls**:
- mTLS for all service-to-service communication
- AWS IAM roles with least privilege
- VPC isolation and security groups
- Certificate rotation every 90 days

**Risk Rating**: Low (Likelihood: Low, Impact: High)
**Mitigation Status**: ✅ Mitigated
**Additional Controls**: Implement service mesh (Istio) for enhanced observability

### 4.2 Tampering

#### Threat T1: Data Tampering in Transit
**Description**: Attacker modifies data during transmission
**Attack Vector**:
- Man-in-the-middle attack
- TLS downgrade

**Existing Controls**:
- TLS 1.3 enforced for all external communications
- TLS 1.2+ for internal communications
- HSTS headers with max-age=31536000
- Certificate pinning for mobile apps

**Risk Rating**: Low (Likelihood: Very Low, Impact: High)
**Mitigation Status**: ✅ Mitigated

#### Threat T2: Database Tampering
**Description**: Unauthorized modification of database records
**Attack Vector**:
- SQL injection
- Compromised application credentials
- Insider threat

**Existing Controls**:
- Parameterized queries (no string concatenation)
- ORM with input sanitization
- Database audit logging enabled
- Principle of least privilege (app has no DROP/ALTER permissions)
- Multi-factor authentication for DBA access

**Risk Rating**: Low (Likelihood: Low, Impact: Critical)
**Mitigation Status**: ✅ Mitigated
**Additional Controls**: Implement database activity monitoring (DAM)

### 4.3 Repudiation

#### Threat R1: User Action Repudiation
**Description**: User denies performing an action
**Attack Vector**: Lack of audit trail

**Existing Controls**:
- Comprehensive audit logging (user ID, timestamp, action, IP)
- CloudWatch Logs with 1-year retention
- Immutable logs (append-only)
- Log integrity verification

**Risk Rating**: Low (Likelihood: Low, Impact: Medium)
**Mitigation Status**: ✅ Mitigated

### 4.4 Information Disclosure

#### Threat I1: Sensitive Data Exposure in Logs
**Description**: PII or credentials leaked in application logs
**Attack Vector**:
- Excessive logging
- Log aggregation compromise

**Existing Controls**:
- Log scrubbing (removes credit cards, SSNs, passwords)
- Encrypted CloudWatch Logs (KMS)
- IAM policies restricting log access
- Regular log review for sensitive data

**Risk Rating**: Medium (Likelihood: Medium, Impact: High)
**Mitigation Status**: ⚠️ Partially Mitigated
**Additional Controls**:
- Implement automated PII detection in logs
- Enable AWS Macie for S3 log buckets

#### Threat I2: Database Backup Exposure
**Description**: Unencrypted or improperly secured database backups
**Attack Vector**:
- S3 bucket misconfiguration
- Stolen AWS credentials

**Existing Controls**:
- Encrypted backups (KMS with CMK)
- S3 bucket policies (no public access)
- S3 Block Public Access enabled
- AWS Config rules for compliance
- Backup access limited to specific IAM roles

**Risk Rating**: Low (Likelihood: Low, Impact: Critical)
**Mitigation Status**: ✅ Mitigated

### 4.5 Denial of Service

#### Threat D1: Application-Layer DDoS
**Description**: Application overwhelmed by malicious requests
**Attack Vector**:
- HTTP flood
- Slowloris attack
- API abuse

**Existing Controls**:
- AWS Shield Standard
- CloudFront with rate limiting
- WAF rules (request rate, geo-blocking)
- Auto-scaling (up to 100 instances)
- Circuit breakers in application code

**Risk Rating**: Medium (Likelihood: Medium, Impact: Medium)
**Mitigation Status**: ✅ Mitigated
**Additional Controls**: Consider AWS Shield Advanced for critical workloads

#### Threat D2: Database Connection Exhaustion
**Description**: Database overwhelmed by connection requests
**Attack Vector**:
- Connection pool exhaustion
- Recursive queries

**Existing Controls**:
- Connection pooling (max 100 connections per service)
- Database connection limits enforced
- Query timeout (30 seconds)
- Read replicas for read-heavy operations

**Risk Rating**: Low (Likelihood: Low, Impact: High)
**Mitigation Status**: ✅ Mitigated

### 4.6 Elevation of Privilege

#### Threat E1: Container Escape
**Description**: Attacker escapes container to host
**Attack Vector**:
- Kernel vulnerability
- Misconfigured container runtime

**Existing Controls**:
- AWS Fargate (managed, isolated compute)
- Non-root container users
- Read-only root filesystem
- Minimal base images (distroless)
- Regular vulnerability scanning (Trivy, ECR scanning)

**Risk Rating**: Low (Likelihood: Very Low, Impact: Critical)
**Mitigation Status**: ✅ Mitigated

#### Threat E2: IAM Privilege Escalation
**Description**: Attacker gains higher AWS privileges
**Attack Vector**:
- Misconfigured IAM policies
- Over-permissive roles

**Existing Controls**:
- Least privilege IAM policies
- IAM Access Analyzer
- Service Control Policies (SCPs)
- Regular IAM policy audits
- No wildcard (*) permissions in production

**Risk Rating**: Low (Likelihood: Low, Impact: Critical)
**Mitigation Status**: ✅ Mitigated

## 5. Risk Summary

| Threat ID | Category | Risk Level | Status | Owner |
|-----------|----------|------------|--------|-------|
| S1 | Spoofing | Medium | Mitigated | Security Team |
| S2 | Spoofing | Low | Mitigated | Security Team |
| T1 | Tampering | Low | Mitigated | Platform Team |
| T2 | Tampering | Low | Mitigated | Platform Team |
| R1 | Repudiation | Low | Mitigated | Platform Team |
| I1 | Information Disclosure | Medium | Partial | Security Team |
| I2 | Information Disclosure | Low | Mitigated | Security Team |
| D1 | Denial of Service | Medium | Mitigated | Platform Team |
| D2 | Denial of Service | Low | Mitigated | Platform Team |
| E1 | Elevation of Privilege | Low | Mitigated | Platform Team |
| E2 | Elevation of Privilege | Low | Mitigated | Security Team |

## 6. Recommendations

### High Priority
1. Implement automated PII detection in logs (I1)
2. Enable AWS Macie for sensitive data discovery (I1)

### Medium Priority
3. Implement service mesh for enhanced observability (S2)
4. Implement database activity monitoring (T2)

### Low Priority
5. Evaluate AWS Shield Advanced for production (D1)
6. Quarterly threat model review and update

## 7. Review History

| Version | Date | Reviewer | Changes |
|---------|------|----------|---------|
| 1.0 | 2024-01-15 | Security Team | Initial threat model |
| 1.1 | 2024-02-20 | Architecture Team | Added service mesh recommendation |
| 1.2 | 2024-03-15 | Security Team | Updated risk ratings, added Macie |

## 8. References

- STRIDE Methodology: https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- AWS Security Best Practices: https://aws.amazon.com/architecture/security-identity-compliance/
```

### PASTA Threat Model Template

PASTA (Process for Attack Simulation and Threat Analysis) - risk-centric methodology.

```markdown
# PASTA Threat Model: {System Name}

## Stage 1: Define Business Objectives

**Business Impact Analysis**:
- Revenue impact if compromised: $500K/day
- Regulatory fines risk: GDPR up to 4% annual revenue
- Reputation damage: High

**Security Objectives**:
- Protect customer PII
- Ensure payment data security (PCI-DSS Level 1)
- Maintain 99.99% availability
- Prevent unauthorized access

## Stage 2: Define Technical Scope

**Architecture Components**:
- Frontend: React SPA hosted on CloudFront
- Backend: Node.js microservices on ECS
- Database: PostgreSQL RDS Multi-AZ
- Authentication: Auth0
- Payment: Stripe integration

## Stage 3: Application Decomposition

**Entry Points**:
1. HTTPS endpoints (API)
2. WebSocket connections (real-time features)
3. Admin console
4. Background job processors

**Trust Levels**:
- Anonymous users (Internet)
- Authenticated users
- Premium users
- Administrators
- Service accounts

## Stage 4: Threat Analysis

**Attack Trees**:
```
Goal: Access Customer PII
├─ Exploit Application Vulnerability
│  ├─ SQL Injection
│  ├─ SSRF
│  └─ Deserialization Attack
├─ Compromise Credentials
│  ├─ Phishing
│  ├─ Credential Stuffing
│  └─ Brute Force
└─ Infrastructure Exploit
   ├─ Container Escape
   ├─ Cloud Misconfiguration
   └─ Supply Chain Attack
```

## Stage 5: Vulnerability & Weakness Analysis

**CVE Analysis**:
- All dependencies scanned (Snyk, npm audit)
- Critical CVEs: 0
- High CVEs: 2 (accepted risk with compensating controls)

**CWE Mapping**:
- CWE-79: XSS - Mitigated with CSP and output encoding
- CWE-89: SQL Injection - Mitigated with parameterized queries
- CWE-200: Information Exposure - Log scrubbing implemented

## Stage 6: Attack Modeling

**Attack Scenarios**:

Scenario 1: Credential Stuffing Attack
- Attacker: External threat actor
- Method: Automated credential testing
- Target: User login endpoint
- Impact: Account takeover
- Likelihood: High
- Mitigation: Rate limiting, CAPTCHA, breach detection

## Stage 7: Risk & Impact Analysis

**Risk Matrix**:

| Threat | Likelihood | Impact | Risk Score | Priority |
|--------|------------|--------|------------|----------|
| SQL Injection | Low | Critical | Medium | P1 |
| DDoS | Medium | High | High | P1 |
| XSS | Low | Medium | Low | P2 |
| Insider Threat | Low | Critical | Medium | P1 |
```

## Security Review Process

### Security Review Checklist Template

```markdown
# Security Review: {Project/Feature Name}

**Date**: 2024-03-15
**Reviewer**: security-team@company.com
**Project Owner**: platform-team@company.com
**Type**: Design Review | Pre-Production | Post-Incident

## 1. Project Overview

**Description**: Brief description of the feature/change
**Business Justification**: Why this change is needed
**Timeline**: Development complete: 2024-03-30, Production: 2024-04-15

## 2. Security Questionnaire

### 2.1 Data Handling

- [ ] Does this handle sensitive data? **Yes** ☑ / No ☐
- [ ] Data classification: Public / Internal / **Confidential** / Restricted
- [ ] PII included? **Yes** ☑ (Email, Name) / No ☐
- [ ] Payment data? Yes ☐ / **No** ☑
- [ ] Data retention period: **90 days**
- [ ] Data deletion process: **Automated soft delete**

### 2.2 Authentication & Authorization

- [ ] Authentication required? **Yes** ☑ / No ☐
- [ ] Authentication method: **OAuth 2.0 / JWT**
- [ ] MFA supported? **Yes** ☑ / No ☐
- [ ] Authorization model: **RBAC** ☑ / ABAC ☐ / Other ☐
- [ ] Least privilege enforced? **Yes** ☑ / No ☐

### 2.3 Network Security

- [ ] Public internet exposure? **Yes** ☑ / No ☐
- [ ] TLS/HTTPS enforced? **Yes** ☑ / No ☐
- [ ] TLS version: **1.3** (minimum 1.2)
- [ ] VPC peering required? Yes ☐ / **No** ☑
- [ ] Security groups reviewed? **Yes** ☑ / No ☐

### 2.4 Cryptography

- [ ] Encryption at rest? **Yes** ☑ / No ☐
- [ ] Encryption method: **AES-256** (KMS)
- [ ] Encryption in transit? **Yes** ☑ / No ☐
- [ ] Key management: AWS KMS / Azure Key Vault / **GCP KMS** / Other
- [ ] Key rotation enabled? **Yes** ☑ (90 days) / No ☐

### 2.5 Input Validation

- [ ] User input sanitized? **Yes** ☑ / No ☐
- [ ] SQL injection protection? **Yes** ☑ (Parameterized queries) / No ☐
- [ ] XSS protection? **Yes** ☑ (CSP, output encoding) / No ☐
- [ ] CSRF protection? **Yes** ☑ (CSRF tokens) / No ☐
- [ ] File upload validation? **Yes** ☑ / No ☐ / N/A ☐

### 2.6 Logging & Monitoring

- [ ] Security events logged? **Yes** ☑ / No ☐
- [ ] Log retention: **1 year**
- [ ] Sensitive data in logs? Yes ☐ / **No** ☑ (scrubbed)
- [ ] Alerting configured? **Yes** ☑ / No ☐
- [ ] SIEM integration? **Yes** ☑ (Splunk) / No ☐

### 2.7 Compliance

- [ ] Compliance requirements: **PCI-DSS** ☑ / HIPAA ☐ / SOC2 ☑ / GDPR ☑
- [ ] Privacy impact assessment: **Completed** ☑ / Not Required ☐
- [ ] Data Processing Agreement: **Signed** ☑ / N/A ☐

### 2.8 Third-Party Dependencies

- [ ] New third-party services? **Yes** ☑ / No ☐
- [ ] Vendor security review: **Completed** ☑ / In Progress ☐
- [ ] Data sharing agreement: **Signed** ☑ / N/A ☐
- [ ] Dependency scanning: **Enabled** ☑ (Snyk)

### 2.9 Infrastructure Security

- [ ] Infrastructure as Code? **Yes** ☑ (Terraform) / No ☐
- [ ] IaC security scanning? **Yes** ☑ (Checkov, tfsec) / No ☐
- [ ] Least privilege IAM? **Yes** ☑ / No ☐
- [ ] Secrets management: **AWS Secrets Manager** ☑ / HashiCorp Vault ☐

### 2.10 Testing

- [ ] Security testing performed? **Yes** ☑ / No ☐
- [ ] SAST (Static Analysis)? **Yes** ☑ (SonarQube) / No ☐
- [ ] DAST (Dynamic Analysis)? **Yes** ☑ (OWASP ZAP) / No ☐
- [ ] Penetration testing? **Scheduled** (Q2 2024) / No ☐
- [ ] Vulnerability scanning? **Yes** ☑ (Weekly) / No ☐

## 3. Identified Issues

| Issue ID | Severity | Description | Remediation | Owner | Due Date |
|----------|----------|-------------|-------------|-------|----------|
| SEC-001 | High | API lacks rate limiting | Implement rate limiting (100 req/min) | Platform Team | 2024-03-25 |
| SEC-002 | Medium | Verbose error messages | Sanitize error responses | Dev Team | 2024-03-30 |
| SEC-003 | Low | Missing security headers | Add CSP, HSTS headers | Platform Team | 2024-03-20 |

## 4. Recommendations

### Must Fix (Blocking)
1. SEC-001: Implement rate limiting before production

### Should Fix (Non-Blocking)
2. SEC-002: Sanitize error messages
3. SEC-003: Add security headers

### Nice to Have
4. Consider implementing API versioning for future compatibility

## 5. Approval

**Security Team Approval**: ☑ Approved with conditions / ☐ Rejected
**Conditions**: SEC-001 must be resolved before production deployment

**Approver**: John Doe, Senior Security Engineer
**Date**: 2024-03-15
**Next Review**: 2024-09-15 (6 months)
```

## Security Architecture Documentation

### Network Security Architecture

```markdown
# Network Security Architecture: {Environment}

## Network Topology

### VPC Architecture (AWS Example)

**VPC**: `10.0.0.0/16` (acme-webapp-prod-vpc)

**Subnets**:

| Type | CIDR | AZ | Purpose | Internet Access |
|------|------|-----|---------|-----------------|
| Public | 10.0.1.0/24 | us-east-1a | Load Balancers | Direct (IGW) |
| Public | 10.0.2.0/24 | us-east-1b | Load Balancers | Direct (IGW) |
| Private-App | 10.0.11.0/24 | us-east-1a | Application Servers | via NAT Gateway |
| Private-App | 10.0.12.0/24 | us-east-1b | Application Servers | via NAT Gateway |
| Private-Data | 10.0.21.0/24 | us-east-1a | Databases | No internet |
| Private-Data | 10.0.22.0/24 | us-east-1b | Databases | No internet |

### Security Groups

**ALB Security Group** (`acme-webapp-prod-alb-sg`):
- Inbound: 443 from 0.0.0.0/0 (HTTPS)
- Inbound: 80 from 0.0.0.0/0 (HTTP redirect)
- Outbound: All to Application Security Group

**Application Security Group** (`acme-webapp-prod-app-sg`):
- Inbound: 8080 from ALB Security Group
- Outbound: 5432 to Database Security Group
- Outbound: 6379 to Cache Security Group
- Outbound: 443 to 0.0.0.0/0 (External APIs)

**Database Security Group** (`acme-webapp-prod-db-sg`):
- Inbound: 5432 from Application Security Group
- Outbound: None

### Network ACLs

**Public Subnet NACL**:
- Allow inbound: 80, 443, ephemeral ports (1024-65535)
- Allow outbound: All
- Deny all other inbound

**Private-Data Subnet NACL**:
- Allow inbound: 5432, 6379 from VPC CIDR
- Allow outbound: To VPC CIDR only
- Deny all internet traffic

### Transit and Peering

**VPC Peering**:
- acme-webapp-prod-vpc <--> acme-shared-services-vpc (monitoring, logging)

**Transit Gateway**: None (future consideration for hub-spoke model)

### DDoS Protection

- **AWS Shield Standard**: Enabled (automatic)
- **AWS WAF**: Enabled with managed rules
  - Core rule set
  - SQL injection protection
  - XSS protection
  - Rate-based rules (2000 req/5min per IP)
  - Geo-blocking (block countries: XX, YY)

### DNS Security

- **Route 53**: DNSSEC signing enabled
- **DNS Firewall**: Enabled to block malicious domains

## Diagram

```
Internet
   |
   v
[CloudFront CDN] -- WAF
   |
   v
[Application Load Balancer] -- Public Subnets (10.0.1.0/24, 10.0.2.0/24)
   |
   v
[ECS Fargate Tasks] -- Private-App Subnets (10.0.11.0/24, 10.0.12.0/24)
   |
   +---> [RDS PostgreSQL] -- Private-Data Subnets (10.0.21.0/24, 10.0.22.0/24)
   +---> [ElastiCache Redis] -- Private-Data Subnets
   |
[NAT Gateway] <-- Outbound internet access
   |
   v
Internet Gateway
```
```

### Identity and Access Management

```markdown
# Identity and Access Management: {Organization}

## Authentication

### User Authentication
- **Primary**: Okta SSO (SAML 2.0)
- **MFA**: Required for all users (Okta Verify, hardware tokens)
- **Password Policy**:
  - Minimum 14 characters
  - Complexity: uppercase, lowercase, number, special character
  - Rotation: 90 days
  - History: Last 12 passwords
  - Lockout: 5 failed attempts, 30-minute lockout

### Service Authentication
- **AWS**: IAM roles with STS AssumeRole
- **Inter-service**: mTLS with certificate rotation every 90 days
- **API Keys**: Rotated every 90 days, stored in AWS Secrets Manager

## Authorization

### Role-Based Access Control (RBAC)

**Roles**:

| Role | Permissions | AWS IAM Groups |
|------|-------------|----------------|
| Developer | Read-only prod, full dev/staging | dev-read-prod, dev-full-dev |
| SRE | Full access except IAM/billing | sre-ops |
| Security | Full access including IAM | security-admins |
| Data Analyst | Read-only data warehouse | data-analysts |

**Example IAM Policy** (Least Privilege):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    },
    {
      "Effect": "Deny",
      "Action": [
        "iam:*",
        "organizations:*",
        "account:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Privileged Access Management

- **Break-glass accounts**: Stored in sealed envelope, audited quarterly
- **Temporary elevated access**: Approved via ServiceNow ticket, time-limited (4 hours)
- **Audit logging**: All privileged actions logged to immutable S3 bucket

## Access Reviews

- **Quarterly**: All IAM roles and permissions
- **Annual**: All user accounts
- **Automated**: IAM Access Analyzer findings reviewed weekly
```

## Compliance Documentation

### SOC 2 Type II Documentation Template

```markdown
# SOC 2 Control Documentation: {Control ID}

**Control ID**: CC6.1
**Control Category**: Logical and Physical Access Controls
**Control Owner**: Security Team
**Last Review**: 2024-03-15

## Control Objective
The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives.

## Control Description
Multi-factor authentication (MFA) is required for all user access to production AWS accounts and systems containing sensitive data.

## Control Activities

### 1. MFA Enforcement
- AWS IAM policies enforce MFA for all production account access
- Conditional Access policies in Okta require MFA
- Service accounts use certificate-based authentication (not password)

### 2. MFA Methods
- Approved methods: Okta Verify (push), hardware tokens (YubiKey), SMS (backup only)
- Unapproved: Email-based MFA, voice calls

### 3. Monitoring and Enforcement
- AWS Config rule checks for MFA enforcement
- Daily report of users without MFA
- Access revoked after 7 days if MFA not configured

## Evidence of Operating Effectiveness

| Evidence Type | Frequency | Location |
|---------------|-----------|----------|
| AWS Config compliance report | Daily | S3: compliance-reports/aws-config/ |
| MFA enrollment report | Weekly | S3: compliance-reports/mfa-enrollment/ |
| Access review log | Quarterly | ServiceNow |
| IAM policy review | Quarterly | Git: infrastructure/iam-policies/ |

## Sample Evidence

**AWS Config Rule**: `mfa-enabled-for-iam-console-access`
- Status: Compliant
- Evaluated Resources: 147/147 compliant
- Last Evaluation: 2024-03-15 08:00:00 UTC

## Testing Procedures (for Auditors)

1. Obtain list of all production IAM users
2. Verify MFA device registered for each user
3. Attempt to access production resources without MFA (should be denied)
4. Review AWS CloudTrail logs for MFA-authenticated sessions

## Deviations and Exceptions

None

## Control Change History

| Date | Change | Approver |
|------|--------|----------|
| 2024-01-01 | Initial implementation | CISO |
| 2024-02-15 | Added hardware token support | Security Team Lead |
```

### GDPR Compliance Documentation

```markdown
# GDPR Compliance: Data Processing Activities

## Record of Processing Activities (Article 30)

### Processing Activity 1: Customer Account Management

**Data Controller**: Acme Corporation
**DPO Contact**: dpo@acme.com

**Purpose**: Manage customer accounts and provide e-commerce services

**Legal Basis**: Contract (Article 6(1)(b))

**Data Subjects**:
- Customers (EU residents)
- Prospective customers

**Categories of Personal Data**:
- Identification data: Name, email, user ID
- Contact data: Address, phone number
- Transaction data: Order history, payment method (tokenized)
- Technical data: IP address, device ID, cookies

**Recipients**:
- Internal: Customer support, billing, fraud prevention teams
- External: Stripe (payment processing), SendGrid (email), AWS (hosting)

**Data Transfers**:
- **To Third Countries**: United States (AWS us-east-1)
- **Safeguards**: Standard Contractual Clauses (SCCs), AWS Data Processing Addendum

**Retention Period**:
- Active customers: Duration of relationship
- Inactive customers: 3 years from last activity, then anonymized
- Deletion: Automated soft delete, hard delete after 90 days

**Security Measures**:
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Access controls (RBAC, MFA)
- Regular security audits
- Pseudonymization where possible

## Data Subject Rights Implementation

| Right | Implementation | Response Time SLA |
|-------|----------------|-------------------|
| Right to Access (Art. 15) | Self-service portal + manual request | 30 days |
| Right to Rectification (Art. 16) | Self-service profile edit | Immediate |
| Right to Erasure (Art. 17) | Automated deletion workflow | 30 days |
| Right to Portability (Art. 20) | JSON export via portal | 30 days |
| Right to Object (Art. 21) | Marketing opt-out, processing objection | 7 days |

## Data Protection Impact Assessment (DPIA)

**Trigger**: Processing involving systematic monitoring or large-scale special category data

**Last DPIA**: 2024-01-15 (AI-based fraud detection system)
**Outcome**: Approved with additional safeguards
**Safeguards Implemented**:
- Enhanced anonymization
- Human review of automated decisions
- Explainability documentation
```

## Incident Response Documentation

### Security Incident Report Template

```markdown
# Security Incident Report: {Incident ID}

**Incident ID**: SEC-2024-003
**Severity**: Critical | **High** | Medium | Low
**Status**: Detected | **Contained** | Eradicated | Recovered | Closed
**Reported**: 2024-03-15 14:30 UTC
**Detected**: 2024-03-15 14:25 UTC
**Contained**: 2024-03-15 15:00 UTC
**Resolved**: 2024-03-15 18:00 UTC

## Incident Summary

Brief description of the security incident.

**Type**: Unauthorized Access | Data Breach | **DDoS Attack** | Malware | Other

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:25 | CloudWatch alarm: High request rate detected |
| 14:30 | On-call engineer investigates, confirms DDoS |
| 14:35 | Incident response team assembled |
| 14:40 | AWS Shield Advanced engaged |
| 14:45 | WAF rules updated to block attack pattern |
| 15:00 | Attack traffic mitigated, service restored |
| 15:30 | Root cause analysis initiated |
| 18:00 | Additional WAF rules deployed |

## Impact Assessment

**Affected Systems**:
- Public API (api.acme.com)
- Web application (www.acme.com)

**Data Affected**: None (no data breach)

**Users Affected**: ~5,000 users experienced intermittent timeouts

**Downtime**: 15 minutes partial outage, 20 minutes degraded performance

**Financial Impact**: Estimated $10,000 in lost revenue

**Compliance Impact**: None (no breach notification required)

## Root Cause

DDoS attack originating from botnet with ~50,000 IPs. Attack targeted API endpoint with computationally expensive queries. Rate limiting was insufficient for distributed attack.

## Containment Actions

1. Activated AWS Shield Advanced
2. Updated WAF rules to block attack signatures
3. Enabled stricter rate limiting (10 req/sec per IP)
4. Geo-blocked non-customer countries

## Eradication

1. Analyzed attack patterns
2. Created permanent WAF rule set
3. Enhanced monitoring for similar patterns

## Recovery

1. Verified all systems operational
2. Checked for data integrity
3. Confirmed no unauthorized access
4. Monitored for 24 hours post-incident

## Lessons Learned

**What Went Well**:
- Quick detection (5 minutes)
- Effective team coordination
- AWS Shield Advanced mitigated attack effectively

**What Could Be Improved**:
- Pre-emptive rate limiting was too permissive
- Geo-blocking should have been configured earlier
- Alert fatigue delayed initial response by 5 minutes

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Update rate limiting rules | Platform Team | 2024-03-20 | ✅ Completed |
| Configure geo-blocking by default | Security Team | 2024-03-25 | ✅ Completed |
| Review and tune CloudWatch alarms | SRE Team | 2024-03-30 | 🔄 In Progress |
| DDoS response runbook update | Security Team | 2024-04-05 | 📝 Planned |
| Conduct tabletop exercise | Security Team | 2024-04-15 | 📝 Planned |

## Notifications

- **Executive**: CISO notified at 14:35
- **Legal**: Notified at 15:00 (no breach, FYI only)
- **Customers**: Status page updated at 14:40, all-clear at 15:30
- **Regulators**: Not required (no data breach)

## Report Prepared By

**Author**: Jane Doe, Security Engineer
**Reviewed**: John Smith, CISO
**Date**: 2024-03-16
```

## Security Metrics and Reporting

### Security Dashboard Metrics

```markdown
# Security Metrics Dashboard: Monthly Report

**Reporting Period**: March 2024
**Prepared By**: Security Team
**Distribution**: Executive Team, Board of Directors

## Executive Summary

- **Overall Security Posture**: Green ✅
- **Critical Vulnerabilities**: 0
- **Security Incidents**: 2 (1 High, 1 Low)
- **Compliance Status**: 100% compliant

## Key Metrics

### Vulnerability Management

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| Mean Time to Patch (Critical) | <24h | 18h | ✅ ↓ |
| Mean Time to Patch (High) | <7d | 5d | ✅ ↓ |
| Critical Vulnerabilities Open | 0 | 0 | ✅ → |
| High Vulnerabilities Open | <5 | 3 | ✅ ↓ |
| Vulnerability Scan Coverage | 100% | 100% | ✅ → |

### Incident Response

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| Mean Time to Detect (MTTD) | <30min | 5min | ✅ ↓ |
| Mean Time to Respond (MTTR) | <1h | 35min | ✅ ↓ |
| Mean Time to Recover | <4h | 3.5h | ✅ ↓ |
| Security Incidents (Total) | - | 2 | ⚠️ ↑ |
| Security Incidents (Critical) | 0 | 0 | ✅ → |

### Access Management

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| MFA Adoption | 100% | 100% | ✅ → |
| Inactive Accounts | 0 | 0 | ✅ → |
| Privileged Accounts | <20 | 15 | ✅ ↓ |
| Overdue Access Reviews | 0 | 0 | ✅ → |

### Compliance

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| SOC 2 Controls Compliant | 100% | 100% | ✅ → |
| PCI-DSS Compliance | Pass | Pass | ✅ → |
| GDPR Data Subject Requests | <30d | 12d avg | ✅ ↓ |
| Policy Acknowledgment | 100% | 98% | ⚠️ ↓ |

### Security Awareness

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| Phishing Simulation Click Rate | <5% | 3% | ✅ ↓ |
| Security Training Completion | 100% | 100% | ✅ → |
| Reported Suspicious Emails | - | 47 | ✅ ↑ |

## Incidents This Month

1. **SEC-2024-003** (High): DDoS attack - Mitigated in 35 minutes
2. **SEC-2024-004** (Low): Misconfigured S3 bucket - No data exposure

## Top Risks

1. Third-party vendor security posture (Medium)
2. Shadow IT adoption (Low)
3. Ransomware threat landscape (Medium)

## Planned Initiatives (Next Month)

1. Deploy AWS GuardDuty for threat detection
2. Implement security awareness gamification
3. Conduct third-party vendor security assessments
```

## Tools and Automation

### Security Tools Stack

| Category | Tools | Purpose |
|----------|-------|---------|
| **SAST** | SonarQube, Semgrep | Static code analysis |
| **DAST** | OWASP ZAP, Burp Suite | Dynamic application testing |
| **SCA** | Snyk, Dependabot | Dependency scanning |
| **IaC Security** | Checkov, tfsec, Trivy | Infrastructure as Code scanning |
| **CSPM** | Prisma Cloud, AWS Security Hub | Cloud security posture |
| **Container Security** | Trivy, Anchore | Container image scanning |
| **SIEM** | Splunk, AWS Security Lake | Security information and event management |
| **Threat Intelligence** | CrowdStrike, Recorded Future | Threat feeds |
| **Secrets Management** | AWS Secrets Manager, HashiCorp Vault | Secrets storage |
| **Policy as Code** | OPA, Sentinel | Policy enforcement |

### Automated Security Checks (CI/CD)

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1

      - name: Snyk dependency scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: OWASP ZAP API scan
        uses: zaproxy/action-api-scan@v0.1.0
        with:
          target: 'https://api-staging.example.com'
```

## Anti-Patterns

### Don't: Store Security Documentation in Inaccessible Locations

```
❌ Security docs in email attachments
❌ Threat models in individual laptops
❌ Compliance evidence in shared drives without version control

✅ Security docs in Git repository
✅ Access controlled, versioned, searchable
✅ Integrated with CI/CD for validation
```

### Don't: Create Point-in-Time Security Reviews

```
❌ Annual security assessment, never updated
❌ Threat model created and forgotten

✅ Continuous security validation
✅ Threat model updated with each major change
✅ Quarterly security reviews
```

### Don't: Document Security Through Obscurity

```
❌ "Security is handled somewhere"
❌ Undocumented compensating controls

✅ Clear, comprehensive security documentation
✅ Transparency in security architecture
✅ Defense in depth with documented layers
```

## References

### Frameworks and Standards

- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **CIS Controls**: https://www.cisecurity.org/controls
- **ISO 27001**: https://www.iso.org/isoiec-27001-information-security.html
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **OWASP ASVS**: https://owasp.org/www-project-application-security-verification-standard/
- **STRIDE**: https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **PASTA**: https://versprite.com/tag/pasta-threat-modeling/
- **ATT&CK Framework**: https://attack.mitre.org/

### Compliance

- **PCI-DSS**: https://www.pcisecuritystandards.org/
- **HIPAA**: https://www.hhs.gov/hipaa/
- **GDPR**: https://gdpr.eu/
- **SOC 2**: https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html
- **FedRAMP**: https://www.fedramp.gov/

### Cloud Security

- **AWS Security Best Practices**: https://aws.amazon.com/architecture/security-identity-compliance/
- **Azure Security Documentation**: https://docs.microsoft.com/azure/security/
- **GCP Security Best Practices**: https://cloud.google.com/security/best-practices
- **Cloud Security Alliance (CSA)**: https://cloudsecurityalliance.org/
- **CIS AWS Foundations Benchmark**: https://www.cisecurity.org/benchmark/amazon_web_services

### Tools

- **OWASP ZAP**: https://www.zaproxy.org/
- **Trivy**: https://aquasecurity.github.io/trivy/
- **Checkov**: https://www.checkov.io/
- **Snyk**: https://snyk.io/
- **SonarQube**: https://www.sonarqube.org/
- **Microsoft Threat Modeling Tool**: https://aka.ms/threatmodelingtool

### Books

- "Threat Modeling: Designing for Security" - Adam Shostack
- "Security Engineering" - Ross Anderson
- "The Web Application Hacker's Handbook" - Dafydd Stuttard, Marcus Pinto
- "Cloud Security and Privacy" - Tim Mather, Subra Kumaraswamy, Shahed Latif
