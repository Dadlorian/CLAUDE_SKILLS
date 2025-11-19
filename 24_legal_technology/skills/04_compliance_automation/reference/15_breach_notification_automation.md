# Breach Notification Automation Reference

## Automated Data Breach Detection, Assessment, and Notification

### Overview

Data breach notification laws require organizations to notify affected individuals, regulators, and sometimes the media when personal information is compromised. Breach notification automation helps organizations detect potential breaches, assess the risk, determine notification obligations, execute notifications within required timeframes, and maintain compliance documentation.

### Regulatory Framework

#### GDPR Breach Notification (Articles 33-34)

**Notification to Supervisory Authority (Article 33):**
- **Deadline:** Within 72 hours of becoming aware
- **Trigger:** Breach likely to result in risk to rights and freedoms
- **Required Information:**
  - Nature of breach
  - Categories and approximate number of data subjects affected
  - Categories and approximate number of personal data records
  - DPO contact information
  - Likely consequences of breach
  - Measures taken or proposed to address breach and mitigate effects
- **Phased Notification:** If all information not available, can provide in phases
- **Documentation:** Must document all breaches (even if not reported)

**Notification to Data Subjects (Article 34):**
- **Deadline:** Without undue delay
- **Trigger:** Breach likely to result in high risk to rights and freedoms
- **Method:** Clear and plain language, direct communication
- **Required Information:**
  - Nature of breach
  - DPO contact information
  - Likely consequences
  - Measures taken or proposed
  - Recommendations for individuals (e.g., reset password, monitor credit)
- **Exceptions (no notification required):**
  - Appropriate technical and organizational measures applied (e.g., encryption)
  - Subsequent measures ensure high risk no longer likely
  - Disproportionate effort (public communication instead)

#### CCPA/CPRA Breach Notification

**California Civil Code § 1798.82:**
- **Trigger:** Unauthorized acquisition of personal information that compromises security, confidentiality, or integrity
- **Deadline:** Without unreasonable delay
- **Recipients:**
  - Affected California residents
  - California Attorney General (if 500+ California residents affected)
- **Method:** Written notice, electronic notice (if previously agreed), or substitute notice
- **Content:**
  - Contact information for company
  - Types of information compromised
  - Date or estimated date of breach
  - Toll-free numbers and addresses for credit reporting agencies (if SSN or driver's license compromised)

**No Private Right of Action (unless failure to maintain reasonable security)**

#### HIPAA Breach Notification Rule (45 CFR 164.400-414)

**Notification to Individuals:**
- **Trigger:** Unauthorized acquisition, access, use, or disclosure of PHI that compromises security or privacy
- **Deadline:** Without unreasonable delay, no later than 60 days after discovery
- **Method:** First-class mail or email (if individual agreed)
- **Substitute Notice:** If contact information insufficient

**Notification to Media:**
- **Trigger:** Breach affecting 500+ residents of state or jurisdiction
- **Deadline:** Without unreasonable delay, no later than 60 days after discovery
- **Method:** Notice to prominent media outlets serving the area

**Notification to HHS:**
- **Breaches of 500+ individuals:** Contemporaneous with individual notice (within 60 days)
- **Breaches of <500 individuals:** Annual log submitted within 60 days of end of calendar year

**Business Associate Notification:**
- BA must notify covered entity without unreasonable delay, no later than 60 days after discovery

**Breach Risk Assessment Required:**
- Not all impermissible uses/disclosures are breaches
- Must conduct risk assessment considering:
  - Nature and extent of PHI
  - Unauthorized person who accessed PHI
  - Whether PHI actually acquired or viewed
  - Extent to which risk mitigated

#### State Breach Notification Laws

**All 50 U.S. States, D.C., and Territories have breach notification laws**
- Varying definitions of personal information
- Different triggers and thresholds
- Different deadlines (most "without unreasonable delay")
- Different notification requirements
- Some require notification to Attorney General or consumer protection agency

**Notable State Laws:**
- **New York SHIELD Act:** Expanded definition of PI, reasonable security requirements
- **Massachusetts 201 CMR 17:** Comprehensive security regulation with breach notification
- **Colorado, Connecticut, Virginia:** Comprehensive privacy laws with breach notification

#### Other Jurisdictions

**Canada - PIPEDA:**
- Notify Privacy Commissioner and individuals if breach creates real risk of significant harm
- As soon as feasible
- Maintain record of all breaches

**Australia - Privacy Act:**
- Notify Office of the Australian Information Commissioner (OAIC) and individuals
- If eligible data breach (likely to result in serious harm)
- As soon as practicable

**UK - UK GDPR:**
- Similar to EU GDPR (72-hour notification to ICO)

### Breach Lifecycle and Automation

#### 1. Breach Detection

**Security Monitoring and Alerts:**
- SIEM (Security Information and Event Management) alerts
- Intrusion detection/prevention systems (IDS/IPS)
- Data loss prevention (DLP) alerts
- Endpoint detection and response (EDR)
- Cloud access security broker (CASB) alerts
- Anomalous data access or download alerts
- Failed access attempts and suspicious activity

**Automated Incident Detection:**
- Unusual data access patterns (machine learning)
- Large data exports or transfers
- Access to sensitive data by unauthorized users
- Ransomware or malware detection
- Unauthorized system changes
- Dark web monitoring for leaked credentials

**Manual Reporting:**
- Employee incident reporting
- Customer complaints
- Third-party notifications
- External security researchers
- Media reports

**Automated Triage:**
- Classify incidents by severity
- Identify if personal data involved
- Route to appropriate response team
- Escalate high-severity incidents

#### 2. Incident Response and Investigation

**Automated Workflow:**
- Incident ticket creation
- Assignment to response team
- Task checklists and playbooks
- Status tracking and updates
- Communication and collaboration

**Investigation Activities:**
- Scope of breach (what data, how many individuals)
- How breach occurred (root cause)
- When breach occurred and when discovered
- Who may have accessed data
- What data was involved (PII, PHI, financial data, etc.)
- Evidence collection and forensics

**Data Inventory Integration:**
- Identify affected data from data catalog
- Determine data classification and sensitivity
- Identify data owners and stewards
- Assess regulatory implications

**Affected Individual Identification:**
- Query systems to identify affected individuals
- Extract contact information (email, address)
- Categorize by jurisdiction (state, country)
- Deduplicate and validate contact data

#### 3. Breach Risk Assessment

**Automated Risk Scoring:**
- Type and sensitivity of data compromised (SSN, health data, financial, etc.)
- Number of individuals affected
- Likelihood of misuse
- Extent of unauthorized access
- Mitigating factors (encryption, remediation)
- Regulatory impact assessment

**HIPAA-Specific Risk Assessment:**
- Four-factor test:
  - Nature and extent of PHI
  - Unauthorized person who accessed PHI
  - Whether PHI actually acquired or viewed
  - Extent to which risk mitigated
- Document assessment and determination

**GDPR Risk Assessment:**
- Risk to rights and freedoms of individuals
- High risk determination for data subject notification
- Impact on individuals (identity theft, financial loss, discrimination, etc.)
- Likelihood and severity

**Notification Determination:**
- Regulatory obligations by jurisdiction
- Thresholds and triggers
- Deadlines and timelines
- Notification recipients (individuals, regulators, media)

#### 4. Notification Preparation

**Automated Notification Templates:**
- Jurisdiction-specific templates (GDPR, CCPA, state laws)
- Regulation-compliant content
- Customizable for breach specifics
- Multi-language support

**Content Generation:**
- Populate templates with breach details
- Nature of breach
- Data categories compromised
- Approximate numbers
- Date of breach
- Recommended actions for individuals
- Contact information for inquiries
- DPO or privacy officer information

**Approval Workflow:**
- Legal review
- Privacy officer approval
- Executive approval (for significant breaches)
- Public relations review
- Documentation of approvals

**Translation:**
- Automated translation for multi-jurisdiction breaches
- Legal review of translations
- Culturally appropriate content

#### 5. Notification Delivery

**Individual Notifications:**

**Email Notifications:**
- Bulk email distribution
- Personalized content (name, specific data compromised)
- Tracking (sent, delivered, opened)
- Bounced email handling
- GDPR-compliant email service provider

**Postal Mail:**
- Integration with mail service providers
- Address validation and formatting
- Certified or registered mail (for sensitive breaches)
- Batch processing and mailing
- Return mail handling

**Substitute Notice (if contact information insufficient):**
- Email notice (if insufficient mail addresses)
- Posting on website
- Media notice
- Notification via major media outlets

**Multi-Channel Notification:**
- Combination of email, mail, phone, SMS
- Portal for individuals to check if affected
- Call center for inquiries

**Regulatory Notifications:**

**GDPR - Supervisory Authority:**
- Electronic submission via authority portal
- Automated form population
- Attachment of required documentation
- Confirmation of receipt
- Track 72-hour deadline

**HIPAA - HHS Breach Portal:**
- Electronic submission to HHS Breach Notification Portal
- Automated data entry
- Immediate submission for 500+ breaches
- Annual submission for <500 breaches

**State Attorneys General:**
- Email or portal submission
- State-specific formats and requirements
- Multi-state breach coordination

**Media Notifications (HIPAA):**
- Press release distribution
- Media outlet identification
- Timing coordination with individual notification

#### 6. Documentation and Reporting

**Breach Log/Register:**
- Comprehensive record of all breaches (even if not reported)
- Breach details, assessment, notifications, remediation
- Audit trail of all activities
- Timestamp and user tracking

**Compliance Documentation:**
- Risk assessment documentation
- Notification decision rationale
- Copies of all notifications sent
- Proof of delivery
- Regulatory submissions and confirmations
- Timeline of events
- Lessons learned and corrective actions

**Reporting and Dashboards:**
- Breach metrics (count, severity, types)
- Notification status (sent, pending, completed)
- Deadline tracking (approaching, met, missed)
- Regulatory submission status
- Executive summary reports
- Board reporting

#### 7. Post-Breach Activities

**Remediation Tracking:**
- Root cause remediation
- Security enhancements
- Process improvements
- Vendor remediation (if third-party breach)
- Validation of remediation effectiveness

**Ongoing Monitoring:**
- Monitor for additional incidents related to breach
- Dark web monitoring for compromised data
- Credit monitoring for affected individuals (if offered)
- Increased security monitoring

**Lessons Learned:**
- Post-incident review
- Identify gaps in detection, response, notification
- Update incident response plans
- Training and awareness

### Breach Notification Automation Platforms

**OneTrust Incident and Breach Response:**
- Automated breach workflow
- Risk assessment tools
- Multi-jurisdiction notification management
- Template library
- Regulatory submission automation
- Breach register and documentation

**TrustArc Incident Response:**
- Incident intake and triage
- Assessment and notification determination
- Template-based notifications
- Multi-channel delivery
- Compliance tracking

**LogicManager Incident Management:**
- Incident reporting and tracking
- Automated workflows
- Risk assessment
- Notification management
- Documentation and audit trail

**ServiceNow Security Incident Response:**
- Integrated incident and breach management
- ITSM and GRC integration
- Workflow automation
- Communication and collaboration
- Reporting and analytics

**Resolver Incident Management:**
- Incident tracking and investigation
- Breach assessment
- Notification workflows
- Compliance reporting

**IBM Resilient (QRadar SOAR):**
- Security orchestration and automated response
- Playbook-driven incident response
- Integration with security tools
- Case management

### Automation Technologies

**Workflow Automation:**
- Incident response playbooks
- Task automation and assignment
- Approval routing
- Deadline management
- Escalation rules

**Communication Automation:**
- Email distribution platforms (SendGrid, Mailgun, etc.)
- SMS providers (Twilio)
- Postal mail services
- Multi-channel notification orchestration

**Data Discovery and Identification:**
- Integration with data catalog
- Personal data identification
- Affected individual queries
- Contact information extraction

**Document Automation:**
- Template-based notification generation
- Mail merge for personalization
- PDF generation
- Multi-language support

**Integration:**
- SIEM and security tools
- Identity and access management (IAM)
- Data loss prevention (DLP)
- GRC platforms
- Communication platforms (email, SMS, postal)
- Regulatory portals and submission systems

### Best Practices

**1. Preparation:**
- Develop incident response and breach notification plan
- Define roles and responsibilities
- Establish communication protocols
- Create notification templates
- Conduct tabletop exercises

**2. Rapid Detection:**
- Implement robust security monitoring
- Automated alerting for potential breaches
- Clear incident reporting procedures
- Integration with security tools

**3. Accurate Assessment:**
- Thorough investigation to determine scope
- Documented risk assessment
- Legal and privacy officer involvement
- Consider all applicable regulations

**4. Timely Notification:**
- Track deadlines (72 hours for GDPR, 60 days for HIPAA)
- Automated deadline calculations
- Proactive reminders and escalation
- Pre-approved templates for speed

**5. Comprehensive Documentation:**
- Document all breaches (even if no notification required)
- Maintain audit trail of assessment and decisions
- Retain copies of notifications and confirmations
- Evidence for regulatory examinations

**6. Coordination:**
- Legal, privacy, security, IT, PR, customer service coordination
- Clear communication channels
- Unified response
- Executive briefings

**7. Continuous Improvement:**
- Post-breach reviews and lessons learned
- Update plans and procedures
- Security enhancements
- Training and awareness

### Key Metrics

**Detection and Response:**
- Time to detect breach
- Time from detection to containment
- Time from detection to notification decision
- Incident response plan activation time

**Notification Timeliness:**
- Percentage of notifications meeting deadlines
- Average time to notify individuals
- Average time to notify regulators
- Late notification rate

**Notification Coverage:**
- Percentage of affected individuals notified
- Bounced/failed notification rate
- Response rate from individuals
- Inquiry volume and handling

**Compliance:**
- Breaches requiring notification vs. total incidents
- Regulatory findings related to breach notification
- Fines or penalties
- Audit trail completeness

---

*Reference for breach notification automation and incident response in compliance programs*
