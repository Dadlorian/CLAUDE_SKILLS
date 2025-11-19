# Security Implementation Guide

## Security Layers

### Layer 1: Network Security
```
Internet
  ↓
Firewall (only 443, 80)
  ↓
Load Balancer (HTTPS only)
  ↓
BI Platform (DMZ or private network)
  ↓
Database (separate network segment)
```

### Layer 2: Authentication
- SSO (SAML 2.0) - Required
- MFA - Highly recommended
- Certificate-based - For APIs
- Regular password policy - Backup only

### Layer 3: Authorization
- Role-Based Access Control (RBAC)
- Row-Level Security (RLS)
- Column-Level Security
- Object permissions

### Layer 4: Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.2+)
- Data masking
- Audit logging

## Implementation Checklist

### Pre-Deployment
- [ ] Security requirements documented
- [ ] Data classification completed
- [ ] Access control model defined
- [ ] Encryption enabled
- [ ] SSO configured
- [ ] MFA enabled
- [ ] Audit logging configured

### RLS Implementation

**Tableau**:
```tableau
// User filter (calculated field)
[Region] = USERNAME()

// Or data source filter
User Allowed Regions =
CONTAINS([Allowed Regions], [Region])
```

**Power BI**:
```dax
// In security role
[Region] = USERNAME()

// Or lookup table
VAR UserEmail = USERPRINCIPALNAME()
VAR AllowedRegions =
    FILTER(
        UserMapping,
        UserMapping[Email] = UserEmail
    )
RETURN
    [Region] IN AllowedRegions
```

**Looker**:
```lookml
explore: orders {
  access_filter: {
    field: region
    user_attribute: allowed_regions
  }
}
```

### Post-Deployment
- [ ] Penetration testing completed
- [ ] Security review passed
- [ ] Audit logs monitored
- [ ] Access reviews scheduled
- [ ] Incident response plan ready

## Monitoring

### Key Security Metrics
- Failed login attempts
- Unauthorized access attempts
- Data exports
- Permission changes
- Anomalous usage patterns

### Alerting Rules
```
Alert if:
- 5+ failed logins in 10 minutes
- Access from new location
- Data export > 10,000 rows
- Permission changes after hours
- Unusual query patterns
```

## Compliance

### GDPR
- [ ] Data inventory completed
- [ ] Privacy policy updated
- [ ] Consent management
- [ ] Right to access implemented
- [ ] Right to erasure implemented
- [ ] Data breach procedures

### HIPAA
- [ ] BAA signed with vendors
- [ ] Audit logging enabled
- [ ] Encryption at rest/transit
- [ ] Access controls configured
- [ ] Training completed
- [ ] Incident response plan

### SOC 2
- [ ] Access reviews quarterly
- [ ] Change management process
- [ ] Audit logs retained 1+ year
- [ ] Security testing annual
- [ ] Vendor assessments

## Resources
- NIST Framework: https://www.nist.gov/cyberframework
- OWASP: https://owasp.org/
- Security Best Practices: Platform-specific docs
