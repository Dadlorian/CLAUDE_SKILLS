# Cloud Security Overview Reference

## Introduction

Cloud security encompasses the technologies, policies, controls, and practices designed to protect cloud-based systems, data, and infrastructure. This reference provides a comprehensive overview of cloud security principles, the shared responsibility model, and key security domains.

## Shared Responsibility Model

### Cloud Provider Responsibilities (Security OF the Cloud)
- **Physical Security**: Data centers, hardware, physical access controls
- **Infrastructure Security**: Hypervisor, network infrastructure, storage infrastructure
- **Service Availability**: SLA commitments, redundancy, disaster recovery
- **Compliance Certifications**: SOC 2, ISO 27001, PCI DSS, FedRAMP, regional certifications
- **Platform Security**: Base security controls, patching, platform-level protections

### Customer Responsibilities (Security IN the Cloud)
- **Data Security**: Encryption, classification, DLP, backup
- **Identity & Access Management**: User authentication, authorization, federation
- **Application Security**: Secure coding, vulnerability management, security testing
- **Operating System**: Patching, hardening, configuration management
- **Network Security**: Security groups, firewalls, network segmentation
- **Compliance**: Meeting regulatory requirements, audit evidence, policy enforcement

### Shared Responsibilities (Varies by Service Model)
- **IaaS**: Customer responsible for OS and above
- **PaaS**: Customer responsible for applications and data
- **SaaS**: Customer responsible for data and user access

## Core Security Domains

### 1. Identity & Access Management (IAM)
**Purpose**: Control who can access what resources and under what conditions

**Key Components**:
- Authentication (who you are): MFA, SSO, federation
- Authorization (what you can do): RBAC, ABAC, policies
- Auditing (what you did): Access logs, activity monitoring

**Best Practices**:
- Implement least privilege access
- Use temporary credentials when possible
- Enable MFA for all users, especially privileged accounts
- Regular access reviews and permission audits
- Centralized identity management

### 2. Data Protection
**Purpose**: Ensure confidentiality, integrity, and availability of data

**Key Components**:
- Encryption at rest: Block storage, object storage, databases
- Encryption in transit: TLS/SSL, VPNs, private links
- Key management: KMS, HSM, key rotation, lifecycle
- Secrets management: Credentials, API keys, certificates
- Data classification: Sensitivity levels, handling requirements

**Best Practices**:
- Encrypt all sensitive data at rest and in transit
- Use cloud-native key management services
- Implement automated key rotation
- Never hardcode secrets in code or configuration
- Classify data and apply appropriate controls

### 3. Network Security
**Purpose**: Protect network traffic and prevent unauthorized access

**Key Components**:
- Network segmentation: VPCs, subnets, VNets
- Traffic filtering: Security groups, NACLs, NSGs, firewalls
- DDoS protection: Rate limiting, distributed defense
- Web application firewall (WAF): OWASP Top 10 protection
- Private connectivity: PrivateLink, Private Endpoints

**Best Practices**:
- Default deny, explicitly allow necessary traffic
- Implement defense-in-depth with multiple layers
- Use private subnets for sensitive resources
- Enable VPC Flow Logs for visibility
- Implement micro-segmentation for critical workloads

### 4. Application Security
**Purpose**: Secure applications throughout the development lifecycle

**Key Components**:
- Secure SDLC: Security requirements, threat modeling
- Security testing: SAST, DAST, SCA, penetration testing
- Container security: Image scanning, runtime protection
- API security: Authentication, authorization, rate limiting
- Supply chain security: Dependency scanning, SBOM

**Best Practices**:
- Shift security left in the development process
- Implement security gates in CI/CD pipelines
- Regular vulnerability scanning and patching
- Input validation and output encoding
- Security training for developers

### 5. Compliance & Governance
**Purpose**: Meet regulatory requirements and maintain security standards

**Key Components**:
- Compliance frameworks: SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR
- Security standards: CIS Benchmarks, NIST, OWASP
- Policy as code: Automated policy enforcement
- Audit logging: Comprehensive, immutable logs
- Security assessments: Vulnerability assessments, penetration testing

**Best Practices**:
- Understand applicable compliance requirements
- Implement security baselines (CIS Benchmarks)
- Enable comprehensive audit logging
- Regular compliance validation and audits
- Document security controls and procedures

### 6. Threat Detection & Response
**Purpose**: Detect, investigate, and respond to security threats

**Key Components**:
- Threat detection: GuardDuty, Sentinel, Security Command Center
- SIEM: Centralized security event management
- Anomaly detection: ML-based behavioral analysis
- Incident response: Playbooks, runbooks, automation
- Forensics: Evidence collection, analysis, preservation

**Best Practices**:
- Centralize security logs and events
- Implement automated threat detection
- Define incident response procedures
- Regular tabletop exercises and drills
- Measure MTTD (Mean Time to Detect) and MTTR (Mean Time to Respond)

## Security Architecture Principles

### Defense-in-Depth
Implement multiple layers of security controls across different levels:
- **Edge Layer**: WAF, DDoS protection, CDN security
- **Network Layer**: Firewalls, security groups, network segmentation
- **Compute Layer**: OS hardening, runtime protection, antimalware
- **Application Layer**: Input validation, authentication, authorization
- **Data Layer**: Encryption, access controls, data loss prevention

### Zero Trust Architecture
Never trust, always verify:
- **Verify Explicitly**: Always authenticate and authorize
- **Least Privilege Access**: Just-in-time, just-enough access
- **Assume Breach**: Minimize blast radius, segment access

### Security by Design
Build security into systems from the ground up:
- Threat modeling during design phase
- Security requirements as first-class requirements
- Secure defaults and configurations
- Fail securely (deny by default)
- Regular security reviews and updates

### Principle of Least Privilege
Grant minimum necessary permissions:
- Role-based access control with minimal roles
- Time-bound access (temporary elevation)
- Regular permission audits and reviews
- Separate duties and responsibilities
- Avoid overly permissive wildcard permissions

## Cloud Security Frameworks

### NIST Cybersecurity Framework
Five core functions:
1. **Identify**: Asset management, risk assessment, governance
2. **Protect**: Access control, data security, protective technology
3. **Detect**: Anomalies, continuous monitoring, detection processes
4. **Respond**: Response planning, communications, analysis, mitigation
5. **Recover**: Recovery planning, improvements, communications

### CIS Controls v8
20 critical security controls organized into:
- **Basic**: Foundational security hygiene
- **Foundational**: Building comprehensive security
- **Organizational**: Organization-wide security practices

### OWASP Cloud-Native Application Security Top 10
1. Insecure cloud, container, or orchestration configuration
2. Injection flaws (application layer, cloud events, cloud services)
3. Improper authentication & authorization
4. CI/CD pipeline & software supply chain flaws
5. Insecure secrets storage
6. Over-permissive or insecure network policies
7. Using components with known vulnerabilities
8. Improper assets management
9. Inadequate compute resource quota limits
10. Ineffective logging & monitoring (e.g., runtime activity)

## Security Best Practices by Cloud Provider

### AWS Security Best Practices
- Enable AWS Organizations and Service Control Policies (SCPs)
- Use AWS IAM Identity Center (formerly SSO) for human access
- Enable MFA for root account and protect root credentials
- Use IAM roles for EC2 instances and Lambda functions
- Enable CloudTrail in all regions and protect logs
- Use AWS Config for configuration management
- Enable GuardDuty for threat detection
- Implement S3 bucket encryption and block public access
- Use VPC endpoints for AWS service access
- Enable VPC Flow Logs for network visibility

### Azure Security Best Practices
- Use Azure AD (Entra ID) for identity management
- Implement Conditional Access policies
- Enable Azure AD Privileged Identity Management (PIM)
- Use Managed Identities for Azure resources
- Enable Azure Activity Logs and Azure Monitor
- Use Azure Policy for governance and compliance
- Enable Microsoft Defender for Cloud (formerly Security Center)
- Implement network security groups (NSGs) and Azure Firewall
- Use Private Endpoints for Azure services
- Enable Azure Key Vault for secrets management

### GCP Security Best Practices
- Use Google Cloud Identity for user management
- Implement Organization Policies for governance
- Enable VPC Service Controls for data exfiltration protection
- Use Workload Identity for GKE pods
- Enable Cloud Audit Logs in all projects
- Use Security Command Center for security posture
- Implement VPC firewall rules with priority-based ordering
- Use Private Google Access for API access from VMs
- Enable Cloud Key Management Service (Cloud KMS)
- Implement Binary Authorization for container deployment

## Security Metrics and KPIs

### Key Security Metrics
- **Mean Time to Detect (MTTD)**: Average time to detect security incidents
- **Mean Time to Respond (MTTR)**: Average time to respond and remediate
- **Vulnerability Density**: Number of vulnerabilities per asset
- **Patch Compliance**: Percentage of systems with current patches
- **Security Finding Remediation Time**: Time to fix security findings
- **Failed Login Attempts**: Indicator of potential attacks
- **Privilege Escalation Events**: Unauthorized elevation attempts
- **Data Exfiltration Attempts**: Unusual data transfer patterns

### Compliance Metrics
- Compliance score (percentage of controls met)
- Audit findings and remediation status
- Policy violations and exceptions
- Security training completion rates
- Access review completion rates

## Common Cloud Security Risks

### Top Cloud Security Threats (CSA)
1. **Data Breaches**: Unauthorized access to sensitive data
2. **Misconfiguration and Inadequate Change Control**: Improperly configured cloud resources
3. **Lack of Cloud Security Architecture and Strategy**: No comprehensive security approach
4. **Insufficient Identity, Credential, Access, and Key Management**: Weak IAM practices
5. **Account Hijacking**: Compromised user credentials
6. **Insider Threat**: Malicious or negligent insiders
7. **Insecure Interfaces and APIs**: Vulnerable cloud service interfaces
8. **Weak Control Plane**: Inadequate management of cloud resources
9. **Metastructure and Applistructure Failures**: Infrastructure and application layer issues
10. **Limited Cloud Usage Visibility**: Lack of visibility into cloud consumption

### Common Misconfigurations
- Publicly accessible storage buckets (S3, Blob Storage, Cloud Storage)
- Overly permissive security groups (0.0.0.0/0 access)
- Disabled logging and monitoring
- Unencrypted data at rest
- Missing MFA on privileged accounts
- Unused or orphaned resources
- Excessive IAM permissions
- Exposed secrets in code or configuration
- Unpatched vulnerabilities
- Disabled security features

## Security Tools and Services

### Cloud-Native Security Services
**AWS**:
- AWS IAM, AWS Organizations, IAM Identity Center
- AWS KMS, AWS Secrets Manager
- AWS Security Hub, AWS GuardDuty, AWS Inspector
- AWS WAF, AWS Shield, AWS Network Firewall
- AWS CloudTrail, AWS Config, Amazon Detective

**Azure**:
- Azure AD (Entra ID), Azure AD PIM
- Azure Key Vault
- Microsoft Defender for Cloud, Azure Sentinel
- Azure WAF, Azure DDoS Protection, Azure Firewall
- Azure Monitor, Azure Activity Logs, Azure Policy

**GCP**:
- Google Cloud IAM, Cloud Identity
- Cloud KMS, Secret Manager
- Security Command Center, Chronicle
- Cloud Armor, Cloud IDS
- Cloud Audit Logs, Cloud Logging, Cloud Monitoring

### Third-Party Security Tools
- **CSPM**: Prisma Cloud, Wiz, Orca Security, Lacework
- **CWPP**: Aqua Security, Sysdig, Palo Alto Prisma Cloud
- **SIEM/SOAR**: Splunk, Sumo Logic, Datadog Security
- **Secrets Management**: HashiCorp Vault, CyberArk
- **Container Security**: Snyk, Aqua, Twistlock
- **Policy as Code**: Open Policy Agent, HashiCorp Sentinel

## Resources and References

### Official Documentation
- AWS Security Best Practices: https://aws.amazon.com/security/best-practices/
- Azure Security Documentation: https://docs.microsoft.com/azure/security/
- GCP Security Best Practices: https://cloud.google.com/security/best-practices

### Security Frameworks
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks/
- OWASP Cloud-Native Application Security: https://owasp.org/www-project-cloud-native-application-security-top-10/

### Industry Resources
- Cloud Security Alliance (CSA): https://cloudsecurityalliance.org/
- SANS Cloud Security: https://www.sans.org/cloud-security/
- MITRE ATT&CK Cloud Matrix: https://attack.mitre.org/matrices/enterprise/cloud/

### Compliance Resources
- SOC 2: https://www.aicpa.org/soc4so
- ISO 27001: https://www.iso.org/isoiec-27001-information-security.html
- PCI DSS: https://www.pcisecuritystandards.org/
- HIPAA: https://www.hhs.gov/hipaa/
- GDPR: https://gdpr.eu/
