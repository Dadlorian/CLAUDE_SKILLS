# HIPAA Breach Response Guide

## Immediate Response (Day 0)

### 1. Contain the Incident
- Isolate affected systems
- Disable compromised accounts
- Preserve evidence
- Stop ongoing unauthorized access

### 2. Assemble Breach Response Team
- Security Official (lead)
- Privacy Official
- IT Director
- Legal Counsel
- Compliance Officer
- Communications/PR (if needed)

### 3. Initial Documentation
```
BREACH INCIDENT REPORT

Incident ID: BR-2024-001
Discovery Date: [Date discovered]
Discovery Method: [How discovered]
Reported By: [Name]
Initial Assessment: [Brief description]
Systems Affected: [List]
Estimated Individuals: [Number or TBD]
```

## Investigation Phase (Days 1-7)

### 4-Factor Risk Assessment

**Factor 1: Nature and Extent of PHI**
- What identifiers were involved?
- How many data elements?
- Sensitivity level (HIV, mental health, substance abuse)?
- Number of individuals affected?

**Factor 2: Unauthorized Person**
- Who accessed/received the PHI?
- Internal vs. external?
- Malicious intent or accidental?
- Confidentiality obligations?

**Factor 3: Was PHI Actually Acquired/Viewed?**
- Evidence of actual viewing?
- Technical logs showing access?
- Recipient confirmation?
- Encrypted and key not compromised?

**Factor 4: Risk Mitigation**
- What was done to mitigate?
- Information retrieved/destroyed?
- Assurances obtained?
- Additional safeguards implemented?

### Breach Determination

**Breach:** Low probability of compromise NOT demonstrated
**Not a Breach:** Low probability of compromise demonstrated

**Documentation Required:**
- 4-factor assessment
- Analysis of each factor
- Conclusion and rationale
- Date of assessment
- Assessor names

## Notification Phase (Days 8-60)

### If Breach Confirmed:

**Individual Notification** (Within 60 days of discovery)

Required Content:
1. Brief description of what happened
2. Date of breach (or estimate)
3. Date discovered
4. Types of PHI involved
5. Steps individuals should take
6. What entity is doing
7. Contact information

Delivery Method:
- Written notice (first-class mail)
- Substitute notice if contact info insufficient

**Media Notification** (If 500+ individuals in state/jurisdiction)
- Press release to prominent media outlets
- Within 60 days
- Same content as individual notice

**HHS Secretary Notification**
- 500+ individuals: Immediately via breach portal
- Fewer than 500: Annually (by March 1 of following year)
- Posted on HHS "Wall of Shame" (if 500+)

### Sample Individual Notification Letter
```
[Date]

Dear [Patient Name]:

We are writing to inform you of an incident that may have involved some of your
protected health information.

WHAT HAPPENED:
On [date], we discovered that [description of breach event].

WHAT INFORMATION WAS INVOLVED:
The information involved may have included [list types: name, date of birth,
medical record number, diagnosis, treatment information, etc.].

WHAT WE ARE DOING:
We have [description of response and mitigation]. We are also [additional
safeguards being implemented].

WHAT YOU CAN DO:
We recommend that you [specific actions: monitor EOBs, credit reports, etc.].

MORE INFORMATION:
For more information or questions, please contact our Privacy Officer at
[phone] or [email].

We sincerely apologize for this incident and any inconvenience it may cause.

Sincerely,
[Name, Title]
```

## Post-Breach Activities

### Root Cause Analysis
- Why did breach occur?
- What controls failed?
- What could have prevented it?

### Corrective Actions
- Implement fixes for identified vulnerabilities
- Update policies and procedures
- Enhance training
- Improve monitoring
- Document all changes

### Lessons Learned
- Conduct post-incident review
- Document findings
- Share learnings (anonymized)
- Update incident response plan

## Breach Response Checklist

**Immediate (Day 0):**
- [ ] Contain incident
- [ ] Preserve evidence
- [ ] Assemble response team
- [ ] Document discovery

**Investigation (Days 1-7):**
- [ ] Conduct 4-factor risk assessment
- [ ] Determine if breach
- [ ] Identify all affected individuals
- [ ] Document assessment

**Notification (Days 8-60):**
- [ ] Notify individuals (if breach)
- [ ] Notify media (if 500+)
- [ ] Notify HHS Secretary
- [ ] Notify business associate or covered entity
- [ ] Document all notifications

**Post-Breach:**
- [ ] Root cause analysis
- [ ] Implement corrective actions
- [ ] Update policies
- [ ] Additional training
- [ ] Lessons learned documentation

## Common Breach Scenarios

### Lost/Stolen Unencrypted Device
- **Assessment:** Likely breach (unsecured PHI)
- **Notification:** Required
- **Prevention:** Full disk encryption

### Unauthorized Employee Access
- **Assessment:** Risk assessment required
- **Notification:** Depends on factors
- **Prevention:** Access controls, audit logging

### Misdirected Fax/Email
- **Assessment:** Depends on recipient
- **Notification:** May be avoided if retrieved
- **Prevention:** Verification procedures

### Hacking/Ransomware
- **Assessment:** Forensic investigation needed
- **Notification:** Likely required
- **Prevention:** Security controls, backups

### Improper Disposal
- **Assessment:** Likely breach
- **Notification:** Required
- **Prevention:** Shredding, data wiping

## Documentation Retention

All breach documentation retained for 6 years minimum:
- Incident reports
- Investigation notes
- Risk assessments
- Notification letters
- Delivery confirmations
- HHS submission confirmations
- Corrective action plans
- Lessons learned reports

## Regulatory Citations
- 45 CFR §164.400-414 - Breach Notification Rule
- 45 CFR §164.402 - Definitions (breach, unsecured PHI)
- 45 CFR §164.404 - Notification to individuals
- 45 CFR §164.406 - Notification to media
- 45 CFR §164.408 - Notification to Secretary

## Resources
- HHS Breach Notification Guidance
- HHS Breach Portal
- Sample notification templates
- Risk assessment tool
