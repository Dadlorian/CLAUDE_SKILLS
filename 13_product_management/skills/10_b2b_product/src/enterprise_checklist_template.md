# Enterprise Readiness Checklist Template

## For: [Customer Name]
**Date**: [Date]
**ACV**: $[Amount]
**Deal Stage**: [Stage]
**Implementation Timeline**: [Dates]

---

## Executive Summary

**Readiness Assessment**: [ ] Ready for Implementation / [ ] Conditional / [ ] Not Ready

**Key Concerns**:
1. [Concern 1]
2. [Concern 2]
3. [Concern 3]

**Mitigation Strategy**:
[Brief description of how concerns will be addressed]

---

## Authentication & Authorization

### SSO (Single Sign-On)
- [ ] SAML 2.0 support confirmed
- [ ] Test with customer's IdP ([IdP name])
- [ ] Troubleshoot any SAML configuration issues
- [ ] Create SAML configuration guide for customer IT
- [ ] Test IdP-initiated and SP-initiated flows

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Multi-Factor Authentication (MFA)
- [ ] Confirm MFA requirements (TOTP, WebAuthn, SMS, etc.)
- [ ] Enable required MFA options
- [ ] Configure MFA enforcement policies at org level
- [ ] Test MFA flow
- [ ] Create MFA setup guide for users

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Role-Based Access Control (RBAC)
- [ ] Define required roles ([list roles])
- [ ] Map roles to customer organizational structure
- [ ] Create custom roles if needed
- [ ] Test permission enforcement across all features
- [ ] Document role permissions matrix
- [ ] Train admins on role management

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Directory Integration
- [ ] Map customer's directory service (Active Directory, Okta, etc.)
- [ ] Set up user provisioning/deprovisioning
- [ ] Test SCIM 2.0 integration if applicable
- [ ] Configure org-level sync
- [ ] Test user lifecycle (create, update, deactivate, delete)

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Security & Compliance

### Data Encryption
- [ ] Confirm encryption requirements (in-transit, at-rest, both)
- [ ] Verify TLS 1.2+ for all connections
- [ ] Confirm data-at-rest encryption status
- [ ] Discuss encryption key management approach
- [ ] Document encryption standards in writing

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Data Isolation
- [ ] Confirm data isolation requirements
- [ ] Verify multi-tenancy with complete data segregation
- [ ] Test data isolation with sample queries
- [ ] Confirm backup data is also isolated
- [ ] Document data isolation architecture

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Audit Logging
- [ ] Confirm audit logging requirements and retention (minimum: [days])
- [ ] Verify audit logs capture required details (user, action, timestamp, IP)
- [ ] Test audit log export functionality
- [ ] Provide audit log access configuration
- [ ] Create audit log search/filter guide for admins
- [ ] Set up real-time audit log streaming if required

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Compliance Certifications
- [ ] [ ] SOC 2 Type II report (provide under NDA)
- [ ] [ ] GDPR Data Processing Agreement (DPA) signed
- [ ] [ ] HIPAA BAA signed (if applicable)
- [ ] [ ] FedRAMP authorized (if applicable)
- [ ] [ ] [Industry-specific certification]

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Security Assessment
- [ ] Confirm if customer wants security assessment/audit
- [ ] Schedule third-party security audit (if requested)
- [ ] Prepare for and remediate findings
- [ ] Provide security assessment report

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Scalability & Performance

### Capacity Requirements
- [ ] Confirm expected concurrent user count: ___
- [ ] Confirm expected data volume: ___
- [ ] Load test with customer's expected volume
- [ ] Confirm system performance meets requirements
- [ ] Document performance expectations

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Infrastructure Requirements
- [ ] Confirm deployment option (cloud only / on-premise / hybrid)
- [ ] Confirm geographic/region requirements: ___
- [ ] Configure infrastructure for customer's geography
- [ ] Confirm auto-scaling is enabled
- [ ] Test infrastructure scalability

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Reliability & Uptime

### SLA Requirements
- [ ] Agree on SLA percentage: [ ] 99.9% [ ] 99.99% [ ] Other: ___
- [ ] Define downtime exclusions (planned maintenance, customer issues, etc.)
- [ ] Define service credits for SLA breaches
- [ ] Document SLA in contract
- [ ] Share status page with customer

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Disaster Recovery & Backup
- [ ] Confirm backup requirements
- [ ] Confirm backup frequency: ___
- [ ] Confirm recovery time objective (RTO): ___
- [ ] Confirm recovery point objective (RPO): ___
- [ ] Test backup and restore procedures
- [ ] Provide disaster recovery documentation

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Maintenance & Updates
- [ ] Define planned maintenance windows with customer
- [ ] Confirm zero-downtime deployment capability
- [ ] Document change management and communication procedures
- [ ] Establish notification process for planned updates

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Integrations & APIs

### API Access
- [ ] Confirm if customer needs API access
- [ ] If yes, confirm required API endpoints
- [ ] Provide API documentation
- [ ] Create API key(s) for customer
- [ ] Set rate limits appropriate for customer size
- [ ] Test API access with customer

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Integrations
- [ ] Identify required integrations: ___
- [ ] Confirm integration status (native / requires setup / not available)
- [ ] For each required integration:
  - [ ] Test integration in production environment
  - [ ] Document configuration steps
  - [ ] Provide troubleshooting guide
  - [ ] Test data sync

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Data Migration
- [ ] Confirm data migration requirements
- [ ] Map legacy system data to new system
- [ ] Develop data migration plan
- [ ] Test data migration with sample data
- [ ] Run full data migration
- [ ] Validate data accuracy post-migration
- [ ] Create rollback plan if needed

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Customization & Configuration

### Custom Fields and Workflows
- [ ] Identify required custom fields: ___
- [ ] Configure custom fields in system
- [ ] Identify required custom workflows: ___
- [ ] Build/configure custom workflows
- [ ] Test custom configurations
- [ ] Document custom configurations for admins

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Professional Services (if needed)
- [ ] Identify custom development needs: ___
- [ ] Scope custom development effort
- [ ] Develop custom features
- [ ] Test custom features
- [ ] Document custom features

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Training & Documentation

### Administrator Training
- [ ] Identify administrator(s): ___
- [ ] Schedule admin training sessions: [dates]
- [ ] Cover topics: SSO, RBAC, user management, audit logs, backups, troubleshooting
- [ ] Provide admin guide (written documentation)
- [ ] Establish post-training support channel

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### End-User Training
- [ ] Identify end-user groups: ___
- [ ] Schedule training by role: [dates]
- [ ] Create role-specific training materials
- [ ] Conduct training sessions
- [ ] Provide user guides by role
- [ ] Set up help/support resources for users

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Documentation
- [ ] Administrator guide: ___
- [ ] User guides by role: ___
- [ ] API documentation: ___
- [ ] Configuration guide: ___
- [ ] Troubleshooting guide: ___
- [ ] All documentation shared with customer: [ ] Yes [ ] No

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Go-Live Planning

### Pre-Go-Live Checklist
- [ ] All technical setup complete
- [ ] Data migration complete and validated
- [ ] Integrations tested
- [ ] Users trained
- [ ] Support team ready
- [ ] Rollback plan documented
- [ ] Communication plan in place

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Go-Live Support
- [ ] Dedicated support team assigned for go-live
- [ ] Support hours: ___
- [ ] Escalation contacts: ___
- [ ] Issue tracking and resolution process defined
- [ ] Post-go-live check-ins scheduled: ___

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Post-Go-Live Assessments
- [ ] 30-day post-go-live review scheduled: [date]
- [ ] 60-day post-go-live review scheduled: [date]
- [ ] 90-day post-go-live review scheduled: [date]
- [ ] Success metrics defined: ___
- [ ] Expansion opportunities identified

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Support & Success Planning

### Dedicated Support
- [ ] Account manager assigned: [Name]
- [ ] Support contact information provided to customer
- [ ] Support SLA defined:
  - Critical issues: [hours] response time
  - High issues: [hours] response time
  - Medium issues: [hours] response time
  - Low issues: [hours] response time

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Success Metrics
- [ ] Success metrics defined with customer: ___
- [ ] Baseline metrics established
- [ ] Tracking mechanism set up
- [ ] 30-60-90 day milestone plan created
- [ ] Expansion opportunities identified

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

### Customer Success Program
- [ ] Monthly business reviews scheduled: [frequency]
- [ ] Quarterly business reviews scheduled: [frequency]
- [ ] Executive check-in scheduled: [frequency]
- [ ] Customer success plan created
- [ ] Health metrics dashboard shared

**Status**: [ ] Not started [ ] In Progress [ ] Complete
**Owner**: [Name]
**Timeline**: [Dates]
**Notes**: [Any issues or considerations]

---

## Implementation Timeline

```
Week 1: [Phase 1 activities]
- [ ] Activity 1
- [ ] Activity 2
- [ ] Activity 3

Week 2: [Phase 2 activities]
- [ ] Activity 1
- [ ] Activity 2
- [ ] Activity 3

Week 3: [Phase 3 activities]
- [ ] Activity 1
- [ ] Activity 2
- [ ] Activity 3

Week 4: [Phase 4 activities]
- [ ] Activity 1
- [ ] Activity 2
- [ ] Activity 3

Go-Live Date: [Date]
```

---

## Open Issues & Blockers

| Issue | Owner | Target Resolution | Status |
|-------|-------|-------------------|--------|
| [Issue 1] | [Owner] | [Date] | [ ] Open [ ] In Progress [ ] Resolved |
| [Issue 2] | [Owner] | [Date] | [ ] Open [ ] In Progress [ ] Resolved |
| [Issue 3] | [Owner] | [Date] | [ ] Open [ ] In Progress [ ] Resolved |

---

## Stakeholder Sign-Off

**Product Readiness**:
- Product Manager: _______________ Date: ___
- Engineering Lead: _______________ Date: ___

**Customer Readiness**:
- Customer Executive Sponsor: _______________ Date: ___
- Customer Technical Lead: _______________ Date: ___
- Customer IT/Security Lead: _______________ Date: ___

**Implementation Readiness**:
- Implementation Manager: _______________ Date: ___
- Professional Services Lead: _______________ Date: ___

---

## Notes

[Space for additional notes, concerns, or follow-ups]
