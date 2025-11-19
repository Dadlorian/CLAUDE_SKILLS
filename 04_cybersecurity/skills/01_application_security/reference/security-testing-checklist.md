# Security Testing Checklist

## Pre-Development

- [ ] Threat model completed
- [ ] Security requirements defined
- [ ] Secure design patterns identified
- [ ] Data classification performed
- [ ] Privacy impact assessment completed

## During Development

### Code Review
- [ ] Manual security code review completed
- [ ] SAST tools integrated in IDE
- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] All outputs encoded
- [ ] Parameterized queries used
- [ ] Secure cryptography implemented
- [ ] Error handling doesn't leak information
- [ ] Security logging implemented

### Dependency Management
- [ ] SCA scan passing (no critical/high vulns)
- [ ] All dependencies from trusted sources
- [ ] Dependency versions pinned
- [ ] License compliance verified
- [ ] Automated dependency updates configured

## Pre-Commit

- [ ] SAST scan passing
- [ ] Secret scanning passing
- [ ] Code linting passing
- [ ] Unit tests include security test cases
- [ ] Git hooks configured

## CI/CD Pipeline

- [ ] SAST scan in pipeline
- [ ] SCA scan in pipeline
- [ ] Secret scanning in pipeline
- [ ] Container scanning (if applicable)
- [ ] IaC scanning (if applicable)
- [ ] Quality gates enforced
- [ ] Failed builds on security issues

## Pre-Deployment

### DAST Testing
- [ ] OWASP ZAP scan completed
- [ ] Burp Suite scan completed
- [ ] All critical/high findings resolved
- [ ] Medium findings reviewed and documented

### Manual Testing
- [ ] OWASP Top 10 testing completed
- [ ] API security testing completed
- [ ] Authentication testing completed
- [ ] Authorization testing completed
- [ ] Session management testing completed
- [ ] Input validation testing completed
- [ ] Business logic testing completed

### Infrastructure
- [ ] Security headers configured
- [ ] TLS/SSL properly configured
- [ ] Firewall rules reviewed
- [ ] Network segmentation implemented
- [ ] Secrets management configured
- [ ] Logging and monitoring configured
- [ ] Backup and recovery tested

## Post-Deployment

- [ ] Penetration testing completed
- [ ] Security monitoring active
- [ ] Incident response plan updated
- [ ] Security documentation updated
- [ ] Vulnerability disclosure process active
- [ ] Regular security scanning scheduled

## OWASP Top 10 Specific Tests

### A01: Broken Access Control
- [ ] Vertical privilege escalation tested
- [ ] Horizontal privilege escalation tested
- [ ] IDOR vulnerabilities tested
- [ ] Direct URL access tested
- [ ] API authorization tested

### A02: Cryptographic Failures
- [ ] TLS 1.2+ enforced
- [ ] Strong cipher suites configured
- [ ] Sensitive data encrypted at rest
- [ ] Secure key management verified
- [ ] Certificate validation tested

### A03: Injection
- [ ] SQL injection tested
- [ ] NoSQL injection tested
- [ ] Command injection tested
- [ ] LDAP injection tested
- [ ] XSS tested (reflected, stored, DOM)

### A04: Insecure Design
- [ ] Threat model reviewed
- [ ] Security controls appropriate for threat level
- [ ] Rate limiting implemented
- [ ] Anti-automation controls tested

### A05: Security Misconfiguration
- [ ] Default credentials removed
- [ ] Unnecessary features disabled
- [ ] Security headers configured
- [ ] Error messages don't leak info
- [ ] Admin interfaces secured

### A06: Vulnerable Components
- [ ] All dependencies scanned
- [ ] No known vulnerable versions
- [ ] Update process documented
- [ ] EOL software identified

### A07: Authentication Failures
- [ ] Weak password policy tested
- [ ] Account enumeration tested
- [ ] Brute force protection tested
- [ ] Session fixation tested
- [ ] Credential stuffing protection tested
- [ ] MFA bypass attempts tested

### A08: Software Integrity Failures
- [ ] Code signing verified
- [ ] SRI for CDN resources
- [ ] CI/CD pipeline secured
- [ ] Artifact integrity verified

### A09: Logging Failures
- [ ] Security events logged
- [ ] Logs protected from tampering
- [ ] Sensitive data not logged
- [ ] Alerting configured
- [ ] Log retention policy implemented

### A10: SSRF
- [ ] URL validation tested
- [ ] Internal network access blocked
- [ ] Cloud metadata access blocked
- [ ] Redirect validation tested

## Compliance Specific

### PCI DSS
- [ ] Requirement 6.2: Security patches
- [ ] Requirement 6.3: Secure SDLC
- [ ] Requirement 6.4: Code reviews
- [ ] Requirement 6.5: OWASP Top 10
- [ ] Requirement 11.3: Penetration testing

### HIPAA
- [ ] Access controls tested
- [ ] Audit logging verified
- [ ] Encryption validated
- [ ] Data integrity controls tested

### GDPR
- [ ] Data protection by design
- [ ] Right to access implemented
- [ ] Right to erasure implemented
- [ ] Data portability tested
- [ ] Consent management tested

---

**Severity Levels**:
- **Critical**: Immediate fix required, blocks deployment
- **High**: Fix within 7 days
- **Medium**: Fix within 30 days
- **Low**: Fix in next release
- **Info**: Document and track
