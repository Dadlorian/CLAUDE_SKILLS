# OWASP Web Application Testing Checklist

## Information Gathering
- [ ] Manually explore application
- [ ] Spider/crawl application
- [ ] Identify entry points
- [ ] Map application architecture
- [ ] Identify frameworks and technologies
- [ ] Review robots.txt and sitemap.xml

## Configuration Management
- [ ] Test HTTP methods
- [ ] Test HTTP Strict Transport Security
- [ ] Test for subdomain takeover
- [ ] Test cloud storage
- [ ] Review CSP headers

## Authentication Testing
- [ ] Test for default credentials
- [ ] Test for weak password policy
- [ ] Test for brute force protection
- [ ] Test for authentication bypass
- [ ] Test for account enumeration
- [ ] Test for session fixation
- [ ] Test for logout functionality

## Session Management
- [ ] Test session token strength
- [ ] Test for session fixation
- [ ] Test for session timeout
- [ ] Test for CSRF protection
- [ ] Test cookie attributes (Secure, HttpOnly, SameSite)

## Authorization Testing
- [ ] Test path traversal
- [ ] Test for privilege escalation
- [ ] Test for insecure direct object references (IDOR)
- [ ] Test for missing authorization

## Input Validation
- [ ] Test for SQL injection
- [ ] Test for NoSQL injection
- [ ] Test for XSS (reflected, stored, DOM)
- [ ] Test for XXE
- [ ] Test for SSRF
- [ ] Test for command injection
- [ ] Test for LDAP injection
- [ ] Test for template injection

## Business Logic Testing
- [ ] Test business process flows
- [ ] Test for race conditions
- [ ] Test for logic flaws
- [ ] Test transaction limits

## Cryptography
- [ ] Test for weak SSL/TLS configuration
- [ ] Test for sensitive data in transit
- [ ] Test for weak encryption
- [ ] Test for padding oracle

## Error Handling
- [ ] Test for information disclosure in errors
- [ ] Test for stack traces
- [ ] Test error handling consistency

## API Testing
- [ ] Test API authentication
- [ ] Test API authorization
- [ ] Test rate limiting
- [ ] Test input validation
- [ ] Test API versioning

---

**Reference:** OWASP Testing Guide v4.2
**Last Updated:** 2025-01-19
