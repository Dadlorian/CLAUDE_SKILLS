# Incident Severity Levels Reference

## Overview

Incident severity classification is critical for appropriate resource allocation, escalation, and response coordination. This reference defines standard severity levels based on Google SRE and PagerDuty best practices.

## Severity Level Definitions

### SEV-1: Critical Impact

**Definition:** Complete service outage or severe degradation affecting all or most users with significant business impact.

**Characteristics:**
- Core functionality is completely unavailable
- Data loss or corruption is occurring
- Security breach or active attack in progress
- Revenue-generating systems are down
- Regulatory/compliance violations in progress
- Customer-facing systems completely unavailable

**Response Requirements:**
- **Response Time:** Immediate (< 5 minutes)
- **Resolution Time Target:** 1-4 hours
- **Escalation:** Automatic executive notification
- **Staffing:** All hands on deck approach
- **Communication:** Hourly updates minimum to stakeholders
- **Post-Mortem:** Required within 48 hours

**Example Scenarios:**
- E-commerce checkout completely down during peak hours
- Database cluster failure causing total service unavailability
- Active data breach with customer data exposure
- Payment processing system completely offline
- Authentication system preventing all user access

**Response Team:**
- Incident Commander (IC)
- Communications Lead
- Multiple Technical Leads
- Executive Sponsor
- Dedicated Scribe
- Customer Support liaison

---

### SEV-2: Major Impact

**Definition:** Significant functionality impaired or degraded, affecting many users with measurable business impact.

**Characteristics:**
- Major features unavailable or severely degraded
- Significant user experience degradation
- Performance degradation affecting substantial user base
- Workaround available but difficult or time-consuming
- Revenue impact is measurable but not catastrophic
- Subset of critical functionality unavailable

**Response Requirements:**
- **Response Time:** < 15 minutes
- **Resolution Time Target:** 4-12 hours
- **Escalation:** Senior engineering and management notified
- **Staffing:** Dedicated team assigned
- **Communication:** Updates every 2-4 hours
- **Post-Mortem:** Required within 1 week

**Example Scenarios:**
- Search functionality down on e-commerce platform
- 30% performance degradation across service
- Single region outage in multi-region deployment
- Secondary authentication method failing (primary still works)
- API rate limiting affecting major customers
- Mobile app login issues (web still functional)

**Response Team:**
- Incident Commander
- Communications Lead
- Technical Lead(s)
- Scribe
- Relevant product/engineering managers

---

### SEV-3: Minor Impact

**Definition:** Limited functionality impairment affecting some users with minimal business impact.

**Characteristics:**
- Non-critical features unavailable or degraded
- Small percentage of users affected
- Easy workaround available
- Performance issues with limited scope
- Cosmetic or minor UX issues in production
- Internal tools or systems affected

**Response Requirements:**
- **Response Time:** < 1 hour during business hours
- **Resolution Time Target:** 24-48 hours
- **Escalation:** Team lead notification
- **Staffing:** Regular on-call rotation
- **Communication:** Daily updates during business hours
- **Post-Mortem:** Optional, team discretion

**Example Scenarios:**
- Minor UI rendering issues on specific browsers
- Batch job delays not affecting real-time operations
- Non-critical API endpoints returning errors
- Metrics dashboard display issues
- Email notification delays
- Minor feature flag configuration issues

**Response Team:**
- On-call engineer (may serve as IC)
- Technical SME if needed
- Team lead awareness

---

### SEV-4: Minimal Impact

**Definition:** Minimal functionality affected or cosmetic issues with negligible business impact.

**Characteristics:**
- Cosmetic issues only
- Very limited user impact
- Feature requests misclassified as incidents
- Documentation or help text errors
- Development/staging environment issues
- Future potential problems identified

**Response Requirements:**
- **Response Time:** Next business day
- **Resolution Time Target:** As scheduled/prioritized
- **Escalation:** None required
- **Staffing:** Normal work queue
- **Communication:** Standard ticket updates
- **Post-Mortem:** Not required

**Example Scenarios:**
- Typos in user interface text
- Broken links in documentation
- Color inconsistencies in UI
- Internal development tool minor bugs
- Analytics tracking gaps for internal metrics
- Staging environment configuration drift

**Response Team:**
- Assigned engineer from normal queue
- No formal incident response required

---

## Severity Assessment Guidelines

### Decision Framework

When assessing incident severity, consider these factors in order:

1. **User Impact**
   - How many users are affected? (percentage)
   - Which user segments are affected? (all, enterprise, free tier)
   - What is the impact severity per user? (complete loss, degraded, minor)

2. **Business Impact**
   - Is revenue directly affected?
   - Are SLA/SLO commitments violated?
   - Is brand reputation at risk?
   - Are there regulatory/compliance implications?

3. **Scope and Duration**
   - What percentage of the service is affected?
   - How long has the issue persisted?
   - Is it escalating or stable?

4. **Workarounds**
   - Are workarounds available?
   - How difficult are they to implement?
   - What percentage of users can use workarounds?

### Severity Escalation

**When to Escalate Severity:**
- Issue persists beyond expected resolution time
- Scope of impact expands
- New critical symptoms discovered
- User/customer escalations increase
- Additional systems failing

**When to De-escalate Severity:**
- Workaround successfully deployed to majority of users
- Root cause identified and mitigation in progress
- Impact scope significantly reduced
- Service restoration in progress with clear timeline

### Special Considerations

**Security Incidents:**
- Active attacks or breaches: Always SEV-1
- Vulnerability discovered but not exploited: SEV-2 or SEV-3
- Potential future risk: SEV-4

**Data Incidents:**
- Active data loss/corruption: SEV-1
- Historical data inconsistency discovered: SEV-2 or SEV-3
- Backup/DR system issues: SEV-2 minimum

**Multi-Region/Service:**
- Total outage: SEV-1
- Single region in multi-region: SEV-2
- Graceful degradation working as designed: May not be incident

---

## Severity Level Comparison Matrix

| Factor | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|--------|-------|-------|-------|-------|
| **User Impact** | All/Most users | Many users | Some users | Few/No users |
| **Functionality** | Core down | Major degraded | Minor degraded | Cosmetic |
| **Business Impact** | Critical | Significant | Minimal | Negligible |
| **Response Time** | < 5 min | < 15 min | < 1 hour | Next day |
| **Resolution Target** | 1-4 hours | 4-12 hours | 24-48 hours | Backlog |
| **Post-Mortem** | Required (48h) | Required (1wk) | Optional | No |
| **Executive Notification** | Immediate | Within 1 hour | As needed | No |
| **Customer Communication** | Hourly | Every 2-4h | Daily | Standard |

---

## Using Severity Levels Effectively

### Best Practices

1. **Start High, Adjust Down**: If uncertain, start with higher severity and downgrade as you learn more

2. **Document the Decision**: Always note why a severity level was chosen in incident timeline

3. **Don't Hesitate to Escalate**: Better to over-respond initially than under-respond

4. **Review Severity Definitions Regularly**: Update based on organizational learning and business changes

5. **Train on Edge Cases**: Ensure team alignment through scenario training

### Common Pitfalls to Avoid

- **Alert Fatigue**: Don't classify too many incidents as SEV-1/SEV-2
- **Severity Inflation**: Maintain discipline in classification
- **Politics Over Impact**: Base severity on actual impact, not who is affected
- **Fixed Mindset**: Be willing to adjust severity as situation evolves
- **Ignoring Trends**: Multiple SEV-3s might indicate a SEV-2 systemic issue

---

## Organizational Customization

This framework should be adapted to your organization's needs. Consider:

- **Industry Requirements**: Financial services may require stricter definitions
- **Company Size**: Startups might combine SEV-3/SEV-4
- **Service Maturity**: More mature services might have more granular levels
- **SLA Commitments**: Align severity with contractual obligations
- **Regulatory Environment**: Compliance requirements may dictate classification

---

## References

- Google SRE Book - "Managing Incidents"
- PagerDuty Incident Response Documentation
- Atlassian Incident Management Handbook
- ITIL Incident Management Framework

**Last Updated:** November 2025
**Review Frequency:** Quarterly
