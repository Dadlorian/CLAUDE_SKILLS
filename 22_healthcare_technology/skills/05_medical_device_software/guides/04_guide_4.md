# Cybersecurity in Medical Device Software Guide

## FDA Cybersecurity Requirements

### Premarket Cybersecurity Submission Content

**Required Documentation**
1. Threat Model (1-2 page executive summary)
2. Security Risk Assessment
3. Security Control Implementation Plan
4. Security Testing Summary
5. SBOM with known vulnerabilities
6. Patch Management Procedures
7. Vulnerability Disclosure Policy

### Postmarket Cybersecurity Plan
- Vulnerability monitoring procedures
- Security update procedures
- Incident response plan
- Customer communication plan

## Implementing Threat Modeling

### STRIDE Methodology
- **Spoofing**: Attacker impersonates legitimate user
- **Tampering**: Unauthorized modification of data
- **Repudiation**: Denying actions were performed
- **Information Disclosure**: Unauthorized data access
- **Denial of Service**: Making system unavailable
- **Elevation of Privilege**: Gaining higher permissions

### Risk Assessment
- Likelihood: How probable is successful attack?
- Impact: What damage if attack succeeds?
- Risk Score = Likelihood × Impact

### Control Selection
- Authentication: Verify user identity
- Encryption: Protect data in transit and at rest
- Access Control: Limit user permissions
- Input Validation: Prevent injection attacks
- Logging: Audit trail of system activities

## Secure Coding Practices

### Critical Areas
- Input validation: All user input checked
- Buffer overflow prevention: Bounds checking
- SQL injection prevention: Parameterized queries
- Cross-site scripting (XSS) prevention: HTML encoding
- Hardcoded secrets: No passwords in code

### Code Review Checklist
- All inputs validated?
- No hardcoded credentials?
- Proper error handling?
- Encryption used correctly?
- Audit logging in place?
- Third-party dependencies secure?

## Vulnerability Management

### Identification
- Static code analysis tools
- Dynamic testing and fuzzing
- Penetration testing
- Dependency scanning

### Assessment and Remediation
- CVSS scoring (severity 0-10)
- Critical vulnerabilities: Fix within 30 days
- High: Fix within 60 days
- Medium: Fix within 90 days
- Low: Fix in next release

### Tracking and Closure
- Central vulnerability database
- Status tracking
- Verification that fix works
- Documentation

## Success Criteria

- [ ] Threat model complete
- [ ] Security controls implemented
- [ ] Vulnerability assessment completed
- [ ] SBOM generated and accurate
- [ ] Security testing results documented
- [ ] Patch procedures defined
- [ ] Team trained in secure coding

## Regulatory Alignment

### FDA Guidance
- 2018 Cybersecurity Guidance
- Premarket and postmarket requirements
- Risk-based approach

### International Standards
- IEC 62271 (Medical device cybersecurity)
- NIST Cybersecurity Framework
- OWASP Top 10
