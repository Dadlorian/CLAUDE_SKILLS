# Cybersecurity - Elite Professional Security Skills

> Comprehensive cybersecurity expertise covering application security, network security, cloud security, compliance, and security operations based on industry-leading practices from FAANG, financial institutions, and security-first organizations.

---

## 🎯 Overview

This domain provides **production-grade cybersecurity knowledge** across 10 specialized areas, reflecting practices from:
- **Google**: BeyondCorp Zero Trust, infrastructure security
- **Netflix**: Full Cycle Developers security model, chaos engineering for security
- **Stripe**: Payment security, PCI DSS compliance
- **AWS/Microsoft/Google Cloud**: Cloud security best practices
- **NIST, OWASP, SANS, MITRE**: Security frameworks and methodologies
- **Top security organizations**: CrowdStrike, Palo Alto Networks, Cloudflare

### What This Domain Covers

#### Core Security Disciplines
1. **Application Security (AppSec)** - Secure coding, SAST/DAST, dependency management
2. **Network Security** - Zero Trust, firewalls, IDS/IPS, network monitoring
3. **Cloud Security** - Multi-cloud security, CSPM, container security
4. **Identity & Access Management** - MFA, SSO, privileged access, Zero Trust
5. **Threat Intelligence** - Threat hunting, MITRE ATT&CK, IOC management

#### Operational Security
6. **Incident Response** - Detection, containment, forensics, recovery
7. **Security Architecture** - Defense in depth, secure design, reference architectures
8. **Compliance & Governance** - SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR
9. **Penetration Testing** - Ethical hacking, red team operations, vulnerability assessment
10. **Security Operations (SecOps)** - SIEM, SOAR, EDR, 24/7 monitoring

---

## 🏗️ Domain Architecture

### Standards & Patterns
```
04_cybersecurity/
├── standards/
│   ├── style-guides/           # Security documentation, secure coding standards
│   ├── api-guides/             # API security, authentication patterns
│   ├── legacy-integration/     # Secure migration, backward compatibility
│   ├── evidence/               # Security research, benchmarks, CVEs
│   └── patterns/               # Security design patterns, reference architectures
└── skills/
    ├── 01_application_security/
    ├── 02_network_security/
    ├── 03_cloud_security/
    ├── 04_identity_access_management/
    ├── 05_threat_intelligence/
    ├── 06_incident_response/
    ├── 07_security_architecture/
    ├── 08_compliance_governance/
    ├── 09_penetration_testing/
    └── 10_security_operations/
```

### Each Subskill Contains
- **skill.md**: Domain expert prompt with security best practices
- **reference/**: Quick security checklists, tool guides, framework summaries
- **guides/**: Step-by-step security implementation guides
- **src/**: Production-ready secure code examples, security tooling

---

## 🔒 Security Principles

All content follows **industry-standard security principles**:

### CIA Triad
- **Confidentiality**: Protect sensitive data from unauthorized access
- **Integrity**: Prevent unauthorized modification of data
- **Availability**: Ensure systems remain accessible to authorized users

### Defense in Depth
- **Multiple layers** of security controls
- **Fail-secure** defaults - systems fail to secure state
- **Least privilege** - minimal access necessary
- **Complete mediation** - every access verified
- **Separation of duties** - no single point of compromise

### Secure by Design
- **Security early** in development lifecycle
- **Threat modeling** before implementation
- **Secure defaults** - security opt-out, not opt-in
- **Attack surface reduction** - minimize exposure
- **Zero Trust** - never trust, always verify

---

## 📚 10 Cybersecurity Subskills

### 1. Application Security (AppSec)

**Focus**: Securing applications throughout the software development lifecycle

**Key Topics**:
- OWASP Top 10 vulnerability mitigation
- Secure SDLC integration (DevSecOps)
- Static Analysis (SAST): SonarQube, Semgrep, CodeQL
- Dynamic Analysis (DAST): OWASP ZAP, Burp Suite
- Software Composition Analysis (SCA): Snyk, Dependabot
- API security: OAuth 2.0, JWT, rate limiting
- Container security: Docker scanning, Kubernetes security
- Security testing automation in CI/CD

**Reference Practices**:
- Google's Security Development Lifecycle
- Microsoft SDL (Security Development Lifecycle)
- OWASP SAMM (Software Assurance Maturity Model)
- NIST SP 800-218 Secure Software Development Framework

**Tools**: Snyk, Checkmarx, Veracode, SonarQube, OWASP ZAP, Burp Suite Professional

---

### 2. Network Security

**Focus**: Protecting network infrastructure and communications

**Key Topics**:
- Zero Trust Network Access (ZTNA)
- Next-generation firewalls (NGFW)
- Intrusion Detection/Prevention (IDS/IPS): Snort, Suricata
- Network segmentation and micro-segmentation
- VPN technologies: IPSec, WireGuard, OpenVPN
- TLS/SSL best practices and certificate management
- DDoS protection and mitigation
- Network monitoring: Zeek, Wireshark, tcpdump
- DNS security: DNSSEC, DNS filtering

**Reference Practices**:
- NIST Zero Trust Architecture (SP 800-207)
- Palo Alto Networks security best practices
- Cisco Secure Network Architecture
- Cloudflare DDoS protection patterns

**Tools**: Palo Alto NGFW, Cisco Firepower, Suricata, Zeek, Wireshark, pfSense

---

### 3. Cloud Security

**Focus**: Securing cloud infrastructure and workloads across AWS, Azure, GCP

**Key Topics**:
- Cloud Security Posture Management (CSPM)
- Cloud Workload Protection Platforms (CWPP)
- AWS security: IAM, GuardDuty, Security Hub, CloudTrail
- Azure security: Azure AD, Defender, Sentinel
- GCP security: Cloud Armor, Security Command Center
- Kubernetes security: RBAC, pod security, network policies
- Serverless security: Lambda/Functions security
- Container security: Image scanning, runtime protection
- Cloud-native security tools: Falco, Aqua, Prisma Cloud

**Reference Practices**:
- AWS Well-Architected Framework (Security Pillar)
- Azure Security Benchmark
- GCP Security Best Practices
- CIS Benchmarks for cloud platforms

**Tools**: AWS GuardDuty, Azure Defender, GCP Security Command Center, Prisma Cloud, Aqua Security

---

### 4. Identity & Access Management (IAM)

**Focus**: Managing authentication, authorization, and access control

**Key Topics**:
- Multi-factor authentication (MFA): TOTP, FIDO2, WebAuthn
- Single Sign-On (SSO): SAML 2.0, OAuth 2.0, OIDC
- Privileged Access Management (PAM)
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Just-In-Time (JIT) access
- Identity providers: Okta, Auth0, Azure AD, AWS Cognito
- Zero Trust identity architecture
- Directory services security: Active Directory, LDAP

**Reference Practices**:
- NIST Digital Identity Guidelines (SP 800-63)
- Google BeyondCorp Zero Trust model
- Microsoft Zero Trust framework
- OAuth 2.0 Security Best Current Practice

**Tools**: Okta, Auth0, Azure AD, CyberArk, Duo Security, YubiKey

---

### 5. Threat Intelligence & Hunting

**Focus**: Proactive threat detection and intelligence-driven defense

**Key Topics**:
- Threat Intelligence Platforms (TIP): MISP, ThreatConnect
- MITRE ATT&CK framework mapping
- Indicators of Compromise (IOCs): collection and sharing
- Threat modeling: STRIDE, PASTA, attack trees
- Threat hunting methodologies
- Threat feed integration and enrichment
- Adversary emulation and red teaming
- Behavioral analytics and anomaly detection
- STIX/TAXII threat intelligence sharing

**Reference Practices**:
- MITRE ATT&CK Navigator usage
- Lockheed Martin Cyber Kill Chain
- Diamond Model of Intrusion Analysis
- SANS Threat Hunting methodology

**Tools**: MISP, ThreatConnect, Anomali, MITRE ATT&CK Navigator, Yara, Sigma

---

### 6. Incident Response & Forensics

**Focus**: Detecting, responding to, and investigating security incidents

**Key Topics**:
- Incident response frameworks: NIST 800-61, SANS
- Incident detection and triage
- Containment strategies: network isolation, system quarantine
- Eradication and recovery procedures
- Digital forensics: disk, memory, network analysis
- Evidence collection and chain of custody
- Incident response playbooks
- Post-incident review and lessons learned
- Forensic tools: Volatility, Autopsy, Sleuth Kit

**Reference Practices**:
- NIST SP 800-61 Computer Security Incident Handling Guide
- SANS Incident Handler's Handbook
- Google IR best practices
- AWS Security Incident Response Guide

**Tools**: TheHive, Cortex, Volatility, Autopsy, Wireshark, ELK Stack, Velociraptor

---

### 7. Security Architecture

**Focus**: Designing secure systems and infrastructure

**Key Topics**:
- Defense in depth architecture
- Security reference architectures
- Threat modeling: STRIDE, PASTA, attack surface analysis
- Network segmentation: DMZ, VLANs, micro-segmentation
- Data classification and protection
- Encryption architecture: PKI, KMS, HSM
- Security services: WAF, API gateway, secrets management
- Secure design patterns and anti-patterns
- Security architecture review processes

**Reference Practices**:
- NIST Cybersecurity Framework architecture
- AWS/Azure/GCP reference architectures
- SABSA (Sherwood Applied Business Security Architecture)
- TOGAF Security Architecture

**Tools**: Threat modeling tools (Microsoft Threat Modeling Tool, OWASP Threat Dragon), draw.io, Lucidchart

---

### 8. Compliance & Governance

**Focus**: Meeting regulatory requirements and security governance

**Key Topics**:
- SOC 2 Type II compliance and audits
- ISO/IEC 27001:2022 certification
- PCI DSS 4.0 compliance for payment systems
- HIPAA compliance for healthcare data
- GDPR and CCPA privacy compliance
- Risk management: assessment, treatment, monitoring
- Security policy development and enforcement
- GRC (Governance, Risk, Compliance) tools
- Continuous compliance monitoring
- Audit preparation and evidence collection

**Reference Practices**:
- NIST Risk Management Framework (SP 800-37)
- ISO 27001/27002 controls
- CIS Controls v8
- SOC 2 Trust Service Criteria

**Tools**: Vanta, Drata, OneTrust, ServiceNow GRC, Archer, AuditBoard

---

### 9. Penetration Testing

**Focus**: Ethical hacking and security testing

**Key Topics**:
- Penetration testing methodologies: PTES, OSSTMM
- Reconnaissance and OSINT: Google dorking, Shodan, Recon-ng
- Vulnerability scanning: Nessus, OpenVAS, Qualys
- Exploitation: Metasploit, custom exploits, exploit development
- Post-exploitation: privilege escalation, lateral movement
- Web application testing: Burp Suite, OWASP ZAP
- Network penetration testing
- Wireless penetration testing: WiFi, Bluetooth
- Social engineering and phishing
- Red team operations

**Reference Practices**:
- OWASP Web Security Testing Guide
- PTES (Penetration Testing Execution Standard)
- NIST SP 800-115 Technical Guide to Information Security Testing
- MITRE ATT&CK for red teams

**Tools**: Kali Linux, Metasploit, Burp Suite Pro, Cobalt Strike, BloodHound, Nmap, Wireshark

---

### 10. Security Operations (SecOps)

**Focus**: 24/7 security monitoring, detection, and response

**Key Topics**:
- Security Information and Event Management (SIEM): Splunk, ELK
- Security Orchestration, Automation, and Response (SOAR)
- Endpoint Detection and Response (EDR): CrowdStrike, Carbon Black
- Extended Detection and Response (XDR)
- Vulnerability management lifecycle
- Security monitoring and alerting
- Log aggregation and correlation
- Threat detection engineering
- Security metrics and KPIs
- Runbook and playbook development

**Reference Practices**:
- NIST SP 800-92 Guide to Computer Security Log Management
- SANS SOC best practices
- Google SRE security operations
- Microsoft Security Operations Center guidance

**Tools**: Splunk, ELK Stack, Microsoft Sentinel, CrowdStrike Falcon, Palo Alto Cortex XDR, TheHive

---

## 🛠️ Core Security Tools & Technologies

### Security Testing
- **SAST**: SonarQube, Checkmarx, Semgrep, CodeQL
- **DAST**: OWASP ZAP, Burp Suite, Acunetix
- **SCA**: Snyk, Dependabot, WhiteSource, Black Duck
- **Fuzzing**: AFL, LibFuzzer, Peach Fuzzer

### Network Security
- **Firewalls**: Palo Alto NGFW, Cisco Firepower, pfSense
- **IDS/IPS**: Snort, Suricata, Zeek
- **Network Monitoring**: Wireshark, tcpdump, ntopng
- **VPN**: OpenVPN, WireGuard, IPSec

### Cloud Security
- **CSPM**: Prisma Cloud, Dome9, CloudGuard
- **CWPP**: Aqua Security, Sysdig, Twistlock
- **Cloud-Native**: Falco, OPA, Kyverno

### Identity & Access
- **Identity Providers**: Okta, Auth0, Azure AD, Keycloak
- **PAM**: CyberArk, BeyondTrust, Delinea
- **MFA**: Duo, YubiKey, Google Authenticator

### SecOps
- **SIEM**: Splunk, ELK, IBM QRadar, Microsoft Sentinel
- **SOAR**: Splunk Phantom, Palo Alto Cortex XSOAR
- **EDR**: CrowdStrike, SentinelOne, Carbon Black
- **Threat Intel**: MISP, ThreatConnect, Anomali

### Penetration Testing
- **Frameworks**: Metasploit, Cobalt Strike, Empire
- **Web Testing**: Burp Suite, OWASP ZAP, SQLmap
- **Scanners**: Nmap, Nessus, OpenVAS, Qualys
- **Exploit Dev**: Ghidra, IDA Pro, x64dbg

---

## 📖 Learning Path

### Beginner → Intermediate (3-6 months)
1. **Foundations**: CIA triad, security principles, basic cryptography
2. **Application Security**: OWASP Top 10, secure coding basics
3. **Network Basics**: TCP/IP, firewalls, VPNs
4. **Tools**: Wireshark, Nmap, Burp Suite basics
5. **Compliance**: Introduction to SOC 2, ISO 27001

### Intermediate → Advanced (6-12 months)
1. **Cloud Security**: AWS/Azure/GCP security services
2. **Threat Hunting**: MITRE ATT&CK, threat intelligence
3. **Incident Response**: IR playbooks, forensics basics
4. **Advanced AppSec**: SAST/DAST/SCA integration
5. **Penetration Testing**: PTES methodology, ethical hacking

### Advanced → Expert (12+ months)
1. **Security Architecture**: Design secure systems end-to-end
2. **Red Team Operations**: Advanced adversary simulation
3. **Security Engineering**: Build security tools and automation
4. **Zero Trust**: Implement enterprise Zero Trust architecture
5. **Compliance Leadership**: Multi-framework compliance programs

---

## 🎓 Certifications & Standards

### Industry Certifications
- **CISSP**: Certified Information Systems Security Professional
- **OSCP**: Offensive Security Certified Professional
- **CISM**: Certified Information Security Manager
- **CEH**: Certified Ethical Hacker
- **GIAC**: Various SANS certifications (GPEN, GCIH, GCIA)
- **Cloud Security**: AWS Security Specialty, Azure Security Engineer, GCP Security

### Compliance Standards
- **ISO 27001**: Information security management
- **SOC 2**: Trust service principles
- **PCI DSS**: Payment card security
- **NIST CSF**: Cybersecurity framework
- **CIS Controls**: Critical security controls

---

## 🚀 Quick Start

### 1. Choose Your Focus Area
```bash
# Explore subskills
cd 04_cybersecurity/skills/

# Application security
cd 01_application_security/

# Cloud security
cd 03_cloud_security/

# Incident response
cd 06_incident_response/
```

### 2. Review Standards
```bash
# Security patterns
cat ../standards/patterns/security-design-patterns.md

# API security guidelines
cat ../standards/api-guides/api-security-best-practices.md
```

### 3. Use Reference Materials
Each subskill contains:
- **reference/**: Quick lookups, checklists, tool commands
- **guides/**: Step-by-step implementation guides
- **src/**: Production-ready security code examples

---

## 💡 Use Cases

### For Developers
- Integrate security into CI/CD pipelines
- Fix OWASP Top 10 vulnerabilities
- Implement secure authentication and authorization
- Secure APIs and microservices
- Container and Kubernetes security

### For Security Engineers
- Design Zero Trust architectures
- Implement SIEM and security monitoring
- Conduct penetration testing and red team exercises
- Build incident response playbooks
- Automate security operations

### For Compliance Teams
- Achieve SOC 2, ISO 27001, PCI DSS certification
- Implement continuous compliance monitoring
- Develop security policies and procedures
- Prepare for security audits
- Manage risk and governance programs

### For Security Leaders
- Build security programs from scratch
- Mature existing security capabilities
- Demonstrate security ROI to executives
- Align security with business objectives
- Build security culture and awareness

---

## 🔗 External Resources

### Security Organizations
- **OWASP**: Open Web Application Security Project
- **SANS**: Security training and research
- **NIST**: National Institute of Standards and Technology
- **MITRE**: ATT&CK framework and security research
- **CIS**: Center for Internet Security

### Vulnerability Databases
- **CVE**: Common Vulnerabilities and Exposures
- **NVD**: National Vulnerability Database
- **CWE**: Common Weakness Enumeration
- **CVSS**: Common Vulnerability Scoring System

### Security Blogs & Research
- Krebs on Security
- Schneier on Security
- Troy Hunt's blog
- Google Project Zero
- Microsoft Security Response Center
- SANS Internet Storm Center

---

## ⚠️ Security Notice

This domain contains security testing tools and techniques for **authorized, ethical use only**:

✅ **Authorized Use**:
- Penetration testing with written authorization
- Security research in controlled environments
- Defending your own systems and applications
- Educational purposes in labs/CTFs
- Security tool development for defensive purposes

❌ **Unauthorized Use**:
- Attacking systems without permission
- Unauthorized access or data exfiltration
- Malware development for malicious purposes
- Sharing exploits for illegal activities

**Always**:
- Get written authorization before testing
- Follow responsible disclosure practices
- Respect privacy and legal boundaries
- Use security knowledge for defense

---

## 📊 Success Metrics

A mature security program demonstrates:

### Technical Metrics
- **Mean Time to Detect (MTTD)**: < 1 hour for critical incidents
- **Mean Time to Respond (MTTR)**: < 4 hours for critical incidents
- **Vulnerability Remediation**: Critical vulns fixed within 7 days
- **Security Test Coverage**: > 80% of applications
- **Patch Compliance**: > 95% systems patched within SLA

### Business Metrics
- **Zero data breaches** due to preventable vulnerabilities
- **Compliance**: 100% compliance with applicable regulations
- **Security Awareness**: > 90% phishing test pass rate
- **Incident Impact**: Reduced average incident cost
- **Security ROI**: Demonstrable risk reduction

---

## 🤝 Contributing

This cybersecurity domain follows industry best practices. To contribute:

1. **Reference tier-1 sources**: NIST, OWASP, SANS, vendor docs
2. **Include evidence**: CVEs, research papers, real-world examples
3. **Test thoroughly**: All code examples must be secure and tested
4. **Follow standards**: Use domain style guides and conventions
5. **Stay current**: Update with latest threats and mitigations

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintainer**: Elite Cybersecurity Skills Repository
**Compliance**: Aligned with NIST CSF, OWASP, CIS Controls v8

---

*This domain represents industry-leading security practices. Security is a journey, not a destination - stay vigilant, stay current, stay secure.*
