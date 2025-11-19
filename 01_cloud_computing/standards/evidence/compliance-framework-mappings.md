# Cloud Compliance Framework Mappings: Controls Aligned to SOC 2, HIPAA, PCI DSS, GDPR, and ISO 27001

## Executive Summary

This document maps cloud security controls across major compliance frameworks (SOC 2, HIPAA, PCI DSS, GDPR, ISO 27001) and demonstrates how AWS, Azure, and GCP services meet regulatory requirements.

---

## 1. Compliance Framework Overview

### 1.1 Framework Comparison Matrix

| Framework | Focus | Scope | Applicability | Cost | Implementation Time |
|-----------|-------|-------|---------------|------|---------------------|
| SOC 2 | Security, availability, integrity | General | All industries | $50-150K | 6-12 months |
| HIPAA | Healthcare data protection | Healthcare | Health entities | $100-300K | 9-18 months |
| PCI DSS | Payment card data | Financial | Card processors | $30-100K | 3-9 months |
| GDPR | Personal data privacy | EU/Global | All if EU customers | $200-500K | 12-24 months |
| ISO 27001 | Information security | General | Enterprise | $100-250K | 9-18 months |

### 1.2 Control Domain Overview

```
Security Controls Mapped Across:
├─ Access Control (authentication, authorization)
├─ Data Protection (encryption, masking)
├─ Network Security (firewalls, segmentation)
├─ Monitoring & Logging (audit trails, SIEM)
├─ Incident Response (detection, remediation)
├─ Change Management (deployments, auditing)
├─ Vendor Management (third-party assessment)
└─ Governance (policies, procedures)
```

---

## 2. SOC 2 Type II Compliance

### 2.1 SOC 2 Trust Service Criteria

**Five Categories:**
1. **CC - Common Criteria** (foundational controls)
2. **A - Availability** (system availability and performance)
3. **C - Confidentiality** (data confidentiality)
4. **I - Integrity** (data accuracy and completeness)
5. **P - Privacy** (personal information processing)

### 2.2 SOC 2 Control Mappings

**Category 1: User Access Controls**

| Control | Requirement | AWS Service | Azure Service | GCP Service |
|---------|-------------|-------------|---------------|-------------|
| CC6.1 | Authenticate users | IAM + MFA | Azure AD + MFA | Cloud Identity |
| CC6.2 | Remove access timely | IAM policy management | Azure AD deprovisioning | IAM policy management |
| CC6.3 | Authorize based on role | IAM roles and policies | RBAC | Cloud IAM roles |
| CC6.4 | Restrict privileged access | AWS SSM Session Manager | Azure PIM | Cloud IAM conditions |
| CC6.5 | Access review procedures | IAM Access Analyzer | Azure access reviews | Cloud Audit Logs |

**Implementation (AWS Example):**
```yaml
IAM Structure:
├─ Root account: Disabled daily use
├─ IAM users/roles: Policy-based
├─ MFA enforcement: Mandatory
├─ CloudTrail logging: All API calls
└─ Access review: Quarterly automated report

Cost: $0 (included in AWS account)
Audit time: 4 hours/quarter (automated)
```

**Category 2: Physical Access Controls**

| Control | Requirement | AWS | Azure | GCP |
|---------|-------------|-----|-------|-----|
| CC7.1 | Physical entry logged | Log and monitor | Log and monitor | Log and monitor |
| CC7.2 | Minimize unauthorized access | Restricted facility access | Restricted access | Restricted access |
| CC7.3 | Protect against physical threats | Video surveillance | Video surveillance | Video surveillance |
| CC7.4 | Reduce threats to facilities | Emergency procedures | Emergency procedures | Emergency procedures |

**Note:** Cloud providers manage physical security. Audit through SOC 2 Type II certifications.

**Category 3: Logical Access Controls**

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| System authentication | MFA enforced | MFA enforced | MFA enforced |
| Access revocation | Immediate (15 min max) | Immediate (15 min max) | Immediate (15 min max) |
| Accountability (logging) | CloudTrail 90+ days | Azure Activity Log 90 days | Cloud Audit Logs 400 days |
| Privileged access | Session Manager | Just-in-Time access | gcloud & O365 audit |

**Category 4: Data Protection**

| Control | AWS Service | Azure Service | GCP Service |
|---------|-------------|---------------|-------------|
| Encryption in transit | TLS 1.2+ | TLS 1.2+ | TLS 1.2+ |
| Encryption at rest | KMS (server-side) | Azure Key Vault | Cloud KMS |
| Key management | Customer or AWS managed | Customer or Azure managed | Customer or GCP managed |
| Data classification | Manual tagging | Sensitivity labels | DLP scanning |

**Category 5: Change Management**

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Change authorization | CloudFormation approval | Azure Policy approval | Cloud Build approval |
| Testing before deployment | CI/CD pipeline required | Azure DevOps | Cloud Build |
| Implementation audit trail | CloudTrail (all changes) | Activity Log (all changes) | Cloud Audit Logs |
| Rollback procedures | CloudFormation rollback | Azure Resource Manager rollback | Deployment Manager |

### 2.3 SOC 2 Type II Audit Requirements

**Audit Duration:** 6-12 months of operations
**Evidence Collection:**
- CloudTrail/Activity Logs: 6-12 months retention
- System logs: 90 days minimum
- Access reviews: Quarterly documentation
- Incident response: Post-incident reports

**Annual Cost:**
- Audit firm engagement: $50-150K
- Preparation time: 300-500 hours
- Total certification cost: $80-200K annually

---

## 3. HIPAA Compliance

### 3.1 HIPAA Architecture Requirements

```
HIPAA Compliance Stack:

┌─────────────────────────────────────┐
│  Patient Portal / EHR Application   │
│  (Runs in secure VPC)               │
└─────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  HIPAA-Eligible Cloud Services      │
│  AWS:                               │
│  ├─ EC2, RDS, S3, DynamoDB          │
│  └─ All with BAA signed             │
│  Azure:                             │
│  ├─ App Service, SQL Database       │
│  └─ All with BAA signed             │
│  GCP: ⚠️ Limited HIPAA coverage     │
└─────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  Data Protection Layer              │
│  ├─ Encryption at rest (KMS)        │
│  ├─ Encryption in transit (TLS)     │
│  ├─ Access logs (CloudTrail)        │
│  └─ Data loss prevention            │
└─────────────────────────────────────┘
```

### 3.2 HIPAA Technical Safeguards

**Safeguard 1: Access Controls**

| HIPAA Requirement | AWS Implementation | Azure Implementation | Verification |
|-------------------|-------------------|----------------------|--------------|
| Unique user ID | IAM users | Azure AD | CloudTrail logs |
| Emergency access | Session Manager | Azure PIM | Audit logs |
| Automatic logoff | STS token 1 hour | Azure AD session 1 hour | Activity logs |
| Encryption | KMS default | Data Encryption Service | Compliance scan |

**Safeguard 2: Encryption**

```yaml
At Rest (Protected Health Information):
AWS:
  Database: AWS KMS encryption mandatory
  Storage: S3 default encryption with CMK
  Backups: Encrypted by default
  Cost: $0.03 per 10K CMK requests

Azure:
  Database: Azure Storage Service encryption (SSE)
  Storage: Blob encryption with CME
  Backups: Encrypted by default
  Cost: Included

GCP:
  Status: ⚠️ Google-managed keys only (no CMK)
  Alternative: Bring your own encryption (BYOE) app-level
  Cost: Application-managed encryption
```

**In Transit (Encrypted channels):**
- TLS 1.2+ mandatory for all connections
- No unencrypted HTTP allowed
- VPN for administrative access

**Safeguard 3: Audit Controls**

| Control | Requirement | Implementation | Retention |
|---------|-------------|-----------------|-----------|
| Audit logs | All access logged | CloudTrail/Activity Log | 1-3 years |
| Accountability | User attribution | Multi-factor auth + logging | Perpetual |
| Integrity | Detect alterations | CloudTrail digest files | 1 year |
| Monitoring | Continuous review | SIEM integration | 90+ days |

### 3.3 HIPAA Administrative Safeguards

**1. Workforce Security**
- Unique user IDs (no shared accounts)
- Emergency access procedures (documented)
- Termination procedures (30-minute deprovisioning)

**2. Information Access Management**
- Access based on minimum necessary principle
- Role-based access control (RBAC)
- Regular access reviews (quarterly)

**3. Security Awareness & Training**
- HIPAA training: Annual requirement
- Phishing simulations: Quarterly
- Incident response training: 2x yearly

**4. Workforce Security**
- Background checks: Required
- Non-disclosure agreements: Required
- Sanctions policy: For violations

### 3.4 Business Associate Agreement (BAA)

**Required for:** All vendors storing/processing PHI

**Cloud Provider BAA Status:**

| Provider | BAA Available | Coverage | Notes |
|----------|---------------|----------|-------|
| AWS | Yes | EC2, RDS, S3, most services | Free, included with account |
| Azure | Yes | App Service, SQL DB, Storage | Free, included with account |
| GCP | Partial | Limited services, complex process | Not recommended for HIPAA |

**BAA Cost:**
- AWS: $0 (included)
- Azure: $0 (included)
- GCP: Requires custom negotiation + legal review

**Audit Time:** 6-12 months to validate compliance

---

## 4. PCI DSS Compliance

### 4.1 PCI DSS v4.0 Requirements (12 Main Requirements)

```
Requirement 1: Firewall Configuration
├─ AWS: Security groups + NACLs
├─ Azure: Network Security Groups
└─ GCP: Cloud Firewall

Requirement 2: Default Passwords/Settings
├─ AWS: No default passwords on instances
├─ Azure: No default passwords
└─ GCP: No default passwords

Requirement 3: Data Protection
├─ AWS: KMS encryption required
├─ Azure: Key Vault encryption
└─ GCP: Cloud KMS encryption

Requirement 4: Encryption in Transit
├─ AWS: TLS 1.2+ mandatory
├─ Azure: TLS 1.2+ mandatory
└─ GCP: TLS 1.2+ mandatory

... (Reqs 5-12 continue)
```

### 4.2 PCI DSS Architecture (AWS Example)

```yaml
PCI-Compliant Architecture:

┌─────────────────┐
│  Cardholder Data│ (Isolated VPC)
│  - Tokenization │
│  - Encryption   │
│  - No logging   │
└─────────────────┘
      ↓ Encrypted
      ↓ Tokenized
      ↓
┌─────────────────────┐
│ Payment Processor    │ (PCI Level 1)
│ (Third-party)       │
└─────────────────────┘

┌──────────────────────────┐
│ Non-Cardholder Systems   │ (Normal security)
│ - Can log freely         │
│ - Standard encryption    │
└──────────────────────────┘

Key: NEVER store full card data
Solution: Tokenization + external processor
```

### 4.3 PCI DSS Implementation Checklist

**Network Level:**
- [ ] Network segmentation (cardholder data isolated)
- [ ] Firewalls protecting all access (AWS Security Groups)
- [ ] Deny all by default (principle of least privilege)
- [ ] Explicit allow-list only

**System Level:**
- [ ] Security patches applied (48-72 hours)
- [ ] Strong authentication (MFA required)
- [ ] User access logging (all API calls)
- [ ] Penetration testing (annually + after changes)

**Data Level:**
- [ ] Never store full PAN (Primary Account Number)
- [ ] Use tokenization instead
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Encryption at rest (KMS required)

**Operational Level:**
- [ ] Incident response plan (documented)
- [ ] Vulnerability scanning (quarterly)
- [ ] Firewall rule review (quarterly)
- [ ] Access review (quarterly)

### 4.4 PCI DSS Compliance Cost

| Component | Cost | Frequency | Effort |
|-----------|------|-----------|--------|
| Vulnerability scanning | $2-5K | Quarterly | 40 hours |
| Penetration testing | $10-50K | Annually | 200 hours |
| Annual assessment | $5-20K | Annually | 100 hours |
| Remediation (avg) | $5-15K | Ongoing | 50 hours/month |
| **Total Annual** | **$50-150K** | | **~600 hours** |

---

## 5. GDPR Compliance

### 5.1 GDPR Key Principles (6 Principles)

| Principle | Requirement | Cloud Implementation |
|-----------|-------------|----------------------|
| Lawfulness | Legal basis for processing | Privacy policy & consent |
| Fairness | Transparent processing | Clear data usage statements |
| Transparency | Privacy notices | Privacy policy published |
| Purpose limitation | Use only for stated purpose | Data minimization policies |
| Data minimization | Only necessary data | Regular data cleanup |
| Integrity & Confidentiality | Secure processing | Encryption + access controls |

### 5.2 GDPR Technical & Organizational Measures (Articles 30-32)

**Technical Measures:**

| Control | AWS | Azure | GCP | Complexity |
|---------|-----|-------|-----|-----------|
| Encryption | KMS | Key Vault | Cloud KMS | Low |
| Access controls | IAM | Azure AD | Cloud IAM | Medium |
| Audit logging | CloudTrail | Activity Log | Audit Logs | Medium |
| DLP | Macie (paid) | DLP (included) | DLP API (paid) | High |
| Anonymization | Manual + encryption | Anonymization DB | BigQuery column-level | High |

**Organizational Measures:**

- Data Protection Officer (DPO): Required if sensitive data
- Privacy Impact Assessment (DPIA): Required before processing
- Data Processing Agreement (DPA): Required with all processors
- Incident notification: 72 hours to regulators
- Right to erasure: Data deletion within 30 days
- Right to portability: Provide data in standard format

### 5.3 Regional Data Residency

**GDPR Requirement:** EU personal data must reside in EU region

**Cloud Options:**
```
AWS:
├─ eu-west-1 (Ireland)
├─ eu-central-1 (Frankfurt)
└─ eu-north-1 (Stockholm)
Compliance: ✓ Full GDPR coverage

Azure:
├─ West Europe (Netherlands)
├─ North Europe (Ireland)
└─ Germany West Central (Frankfurt)
Compliance: ✓ Full GDPR coverage

GCP:
├─ europe-west1 (Belgium)
├─ europe-west4 (Netherlands)
└─ europe-north1 (Finland)
Compliance: ✓ Full GDPR coverage
```

**Data Transfer Outside EU:**
- Must have Standard Contractual Clauses (SCC)
- Require adequacy assessment (Schrems II ruling)
- Supplementary safeguards often required

### 5.4 GDPR Rights Implementation

**1. Right to Access (Article 15)**
```
Implementation:
├─ API to retrieve user data
├─ Return in machine-readable format
├─ Timeline: 30 days (extendable to 90)
└─ Cost: Typically absorbed in operations
```

**2. Right to Rectification (Article 16)**
```
Implementation:
├─ Update user information
├─ Modify personal data
├─ Timeline: 30 days
└─ Notification: Inform where data was shared
```

**3. Right to Erasure (Article 17)**
```
Implementation:
├─ Hard delete user records
├─ Remove from backups (after expiry)
├─ Timeline: 30 days
├─ Exception: Legal obligations, contract obligations
└─ Challenge: Distributed systems, backups
```

**4. Right to Restrict Processing (Article 18)**
```
Implementation:
├─ Stop processing (but retain data)
├─ Maintain data for legal purposes
├─ Timeline: Immediate
└─ Example: Pending dispute resolution
```

**5. Right to Portability (Article 20)**
```
Implementation:
├─ Export user data in standard format (JSON/XML)
├─ Provide to user in <30 days
├─ Direct transfer to another service if possible
└─ Format: CSV, JSON, structured data
```

### 5.5 GDPR Compliance Roadmap

| Phase | Timeline | Activities | Cost |
|-------|----------|-----------|------|
| Assessment | Month 1 | Privacy audit, gap analysis | $10-20K |
| Implementation | Months 2-6 | Technical controls, DPA | $50-100K |
| Operationalization | Months 7-9 | Training, procedures, testing | $20-30K |
| Certification | Month 10+ | Independent audit (optional) | $15-30K |
| **Total** | **10-12 months** | | **$95-180K** |

---

## 6. ISO 27001 Compliance

### 6.1 ISO 27001 Control Objectives (14 Domains)

| Domain | Focus | Example Controls |
|--------|-------|------------------|
| A.5 | Organizational controls | Information security policy |
| A.6 | People controls | Access rights management |
| A.7 | Physical controls | Perimeter security |
| A.8 | Network & endpoint controls | Network security |
| A.9 | Cryptography | Encryption, key management |
| A.10 | Physical & environmental | Facilities management |
| A.11 | Operations controls | Change management |
| A.12 | Communications security | Network monitoring |
| A.13 | Systems acquisition | System development |
| A.14 | System security | Software development |
| A.15 | Supplier controls | Third-party management |
| A.16 | Information security incident | Incident response |
| A.17 | Business continuity | Backup, disaster recovery |
| A.18 | Compliance | Regulatory compliance |

### 6.2 ISO 27001 Cloud Implementation

**Cloud Service Model Responsibility Matrix:**

```
                   On-Premises  |  IaaS    |  PaaS   |  SaaS
─────────────────────────────────────────────────────────────
Application         You          You       You      Provider
Data                You          You       You      Shared
Runtime             You          Provider  Provider  Provider
OS                  You          Provider  Provider  Provider
Virtualization      You          Provider  Provider  Provider
Storage             You          Provider  Provider  Provider
Networking          You          Provider  Provider  Provider
```

### 6.3 ISO 27001 Control Implementation (AWS Example)

| Control | Requirement | AWS Service | Implementation |
|---------|-------------|-------------|-----------------|
| A.6.1.1 | User access authorization | IAM | Policy-based access |
| A.6.1.2 | Privileged access rights | Session Manager | Temporary credentials |
| A.6.1.3 | User access review | Access Analyzer | Quarterly reports |
| A.9.1.1 | Encryption policy | KMS + S3 | Mandatory encryption |
| A.11.2 | Change management | CloudFormation | Approval workflow |
| A.16.1 | Incident response | EventBridge | Automated response |
| A.17.1 | Backup strategy | AWS Backup | Daily backups, tested |
| A.18.1 | Compliance monitoring | Config | Continuous scanning |

### 6.4 ISO 27001 Audit Timeline

**Typical Audit Schedule:**

```
Month 1-2: Gap Assessment
├─ Current state analysis
├─ Target state definition
└─ Resource planning

Month 3-8: Implementation
├─ Control development
├─ Documentation creation
├─ Training rollout

Month 9: Mock Audit (internal)
├─ Validate readiness
├─ Identify gaps
└─ Final remediation

Month 10: Stage 1 Audit (external)
├─ Audit plan review
├─ Documentation review
└─ Initial assessment

Month 11: Stage 2 Audit (external)
├─ Operational effectiveness testing
├─ Control testing
├─ Finding resolution

Month 12: Certification
├─ Certificate issued
└─ Quarterly surveillance audits
```

**Cost:**
- Consulting: $50-150K
- Audit firm: $30-80K
- Internal effort: 200-500 hours
- **Total: $100-250K**

---

## 7. Compliance Control Overlap Matrix

### 7.1 Cross-Framework Control Mapping

**Access Control (present in all frameworks):**

| Control | SOC 2 | HIPAA | PCI DSS | GDPR | ISO 27001 |
|---------|-------|-------|---------|------|-----------|
| MFA required | CC6.1 | 164.308(a)(3) | Req 8.3 | 32 | A.6.2.1 |
| Access review | CC6.1 | 164.312(a)(2)(i) | Req 7 | 32 | A.6.1.3 |
| Audit logging | CC7.1 | 164.312(b) | Req 10 | 32 | A.12.4.1 |
| Unique ID | CC6.1 | 164.312(a)(2)(i) | Req 8.2 | 32 | A.6.1.1 |

**Data Protection (present in all frameworks):**

| Control | SOC 2 | HIPAA | PCI DSS | GDPR | ISO 27001 |
|---------|-------|-------|---------|------|-----------|
| Encryption at rest | CC6.1 | 164.312(a)(2)(ii) | Req 3.2 | 32 | A.9.1 |
| Encryption in transit | CC6.1 | 164.312(a)(2)(ii) | Req 4 | 32 | A.9.1 |
| Key management | CC6.2 | 164.312(a)(2)(ii) | Req 3.6 | 32 | A.9.2 |
| Data classification | CC6.1 | 164.308(a)(3) | Req 3.1 | 32 | A.8.2.1 |

### 7.2 Single Cloud Architecture for Multiple Compliances

```
Multi-Compliance Architecture (AWS):

┌─────────────────────────────────────────────┐
│  Private VPC (SOC 2, HIPAA, ISO 27001)      │
│  - Encryption enabled (all frameworks)      │
│  - MFA enforced (all frameworks)            │
│  - Audit logging (CloudTrail - all)         │
│  - Data classification (tags)               │
└─────────────────────────────────────────────┘
  ├─────────────────────────────────────┐
  │  Payment Processing Segment (PCI)   │
  │  - Network isolated                 │
  │  - Tokenization required            │
  │  - No PAN storage                   │
  └─────────────────────────────────────┘
  ├─────────────────────────────────────┐
  │  EU Data Region (GDPR)              │
  │  - eu-west-1 region                 │
  │  - Data residency compliant         │
  │  - SCC agreements signed            │
  └─────────────────────────────────────┘
  ├─────────────────────────────────────┐
  │  Patient Data Segment (HIPAA)       │
  │  - BAA signed                       │
  │  - Encryption mandatory             │
  │  - 1-year audit trail retention     │
  └─────────────────────────────────────┘
```

---

## 8. Cloud Provider Compliance Certifications (2024)

### 8.1 Certifications by Cloud Provider

| Certification | AWS | Azure | GCP |
|---|---|---|---|
| SOC 2 Type II | ✓ | ✓ | ✓ |
| HIPAA BAA | ✓ | ✓ | Partial |
| PCI DSS Level 1 | ✓ | ✓ | ✓ |
| GDPR compliance | ✓ | ✓ | ✓ |
| ISO 27001 | ✓ | ✓ | ✓ |
| FedRAMP | ✓ (Moderate) | Partial | None |
| HITRUST CSF | ✓ | ✓ | Partial |
| GxP (pharma) | ✓ | ✓ | Limited |

**Key Insight:** AWS and Azure have most comprehensive compliance; GCP limited in HIPAA/specialized sectors.

### 8.2 Time to Compliance by Framework

| Framework | AWS | Azure | GCP |
|---|---|---|---|
| SOC 2 | 6-9 months | 6-9 months | 6-9 months |
| HIPAA | 9-15 months | 9-15 months | 12-18 months* |
| PCI DSS | 3-6 months | 3-6 months | 3-6 months |
| GDPR | 6-12 months | 6-12 months | 6-12 months |
| ISO 27001 | 9-12 months | 9-12 months | 9-12 months |

*GCP requires custom work due to limited native HIPAA support

---

## 9. Compliance Cost Estimate Matrix

### 9.1 Total Implementation Cost by Framework

| Framework | Consulting | Audit | Internal Effort | Total |
|---|---|---|---|---|
| SOC 2 Type II | $15K | $25K | 300 hrs ($45K) | $85K |
| HIPAA | $30K | $50K | 400 hrs ($60K) | $140K |
| PCI DSS v4.0 | $10K | $15K | 200 hrs ($30K) | $55K |
| GDPR | $50K | $20K | 500 hrs ($75K) | $145K |
| ISO 27001 | $40K | $30K | 350 hrs ($52K) | $122K |

### 9.2 Annual Maintenance Cost

| Framework | Audits | Training | Monitoring | Total |
|---|---|---|---|---|
| SOC 2 Type II | $30K | $5K | $10K | $45K/year |
| HIPAA | $40K | $10K | $15K | $65K/year |
| PCI DSS | $20K | $3K | $8K | $31K/year |
| GDPR | $25K | $8K | $12K | $45K/year |
| ISO 27001 | $20K | $5K | $10K | $35K/year |

---

## 10. Key Takeaways

1. **Multi-framework overlap enables efficient implementation** - 60-70% of controls overlap
2. **AWS/Azure better for compliance** - More services, certifications, BAAs
3. **Data residency critical for GDPR** - Must use EU regions
4. **PCI DSS requires network isolation** - Cardholder data in separate segment
5. **HIPAA requires Business Associate Agreement** - Non-negotiable
6. **MFA blocks 99%+ of unauthorized access** - Essential for all frameworks
7. **Encryption mandatory everywhere** - At rest, in transit, backups
8. **Audit logging non-negotiable** - 90+ days retention minimum
9. **Total cost $100-200K+ annually** - Budget accordingly
10. **Compliance is ongoing, not one-time** - Budget for continuous monitoring

---

## 11. References

- SOC 2 Trust Service Criteria (AICPA, 2024)
- HIPAA Security Rule (HHS, 2024)
- PCI DSS v4.0 Standard (PCI Council, 2024)
- GDPR Regulation (EU, 2018)
- ISO/IEC 27001:2022 Standard
- AWS Compliance Resources
- Microsoft Azure Compliance Documentation
- Google Cloud Compliance Resources
- Gartner Cloud Compliance Report (2024)

---

**Last Updated:** November 2024
**Next Review:** May 2025
**Report Version:** 2.2
