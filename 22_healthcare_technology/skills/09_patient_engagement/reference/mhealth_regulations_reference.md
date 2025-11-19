# Mobile Health (mHealth) Regulations Reference

## FDA Regulatory Framework

### FDA Software Classification

**Non-Regulated Software:**
- Wellness applications (track general health metrics without diagnosis)
- Educational applications (health information delivery only)
- Administrative apps (scheduling, messaging without clinical data analysis)
- Accessories to non-medical devices

**Regulated as Medical Device (SaMD):**
If the app:
- Diagnoses, treats, mitigates, cures, or prevents disease
- Affects body structure or function
- Drives a medical device
- Is intended to diagnose, treat, or monitor

### FDA Guidance on Clinical Decision Support (CDS)

**Non-FDA Regulated CDS:**
- Provides information to support clinical decision
- Practitioner retains control
- Practitioner not required to follow recommendations
- Accurate information presented without bias
- Clearly labeled as CDS
- No device/drug claims

**Regulated CDS:**
- Controls clinical process or outcome
- Automatic override not available
- Intended to provide diagnosis/treatment determination
- Replaces practitioner judgment

### Regulatory Pathways for mHealth

#### 1. Exemption from Device Regulations
**Requirements:**
- Software is not intended to diagnose/treat/mitigate/cure disease
- Not intended to affect body structure/function
- Is educational or wellness in nature
- Clearly labeled as such

**Documentation Needed:**
- Intended use statement
- Comparison with similar unregulated products
- Labeling and marketing materials

#### 2. Class II Device - Premarket Notification (510(k))
**Process:**
- Identify predicate device with substantially equivalent function
- Prepare 510(k) submission
- FDA reviews (typically 30-90 days)
- Receive clearance to market

**Common Predicate Devices:**
- Remote patient monitoring apps
- Mobile weight management apps
- Fitness apps with health tracking

**Submission Includes:**
- Device description and intended use
- Substantial equivalence statement
- Comparison table with predicate
- Software documentation
- Test and validation data
- User manual and labeling

#### 3. Class III Device - Premarket Approval (PMA)
**Process:**
- Submit comprehensive PMA application
- FDA reviews for safety and effectiveness (150-180 days)
- Pre-market approval required before marketing

**Typically Required For:**
- Diagnostic applications with high-risk claims
- Treatment planning applications
- Intensive health monitoring
- Implantable device control

**PMA Submission Includes:**
- Extensive clinical data
- Manufacturing information
- Adverse event history
- Environmental assessment
- Risk analysis

### Digital Health Software Pre-Certification Program

**Purpose:** Risk-based oversight for software manufacturers

**Tier 1 - Lower Risk:**
- Wellness apps
- General health information
- Non-critical monitoring

**Tier 2 - Moderate Risk:**
- Chronic disease management
- Diagnostic support tools
- Patient education with clinical data

**Tier 3 - Higher Risk:**
- Critical clinical decisions
- Real-time monitoring of high-risk conditions
- Treatment planning

**Benefits of Pre-Cert:**
- Streamlined FDA review
- Reduced submission requirements
- Real-world performance monitoring
- Post-market authority

## Regulatory Requirements by Use Case

### Remote Patient Monitoring (RPM)

**FDA Requirements:**
- Clear intended use statement
- Connectivity and data transmission security
- User interface for clinical interpretation
- Clinical validation data
- Labeling and user instructions

**Regulatory Category:**
- Typically Class II
- FDA guidance K161100 applicability checklist
- 510(k) submission usually required

**Compliance Elements:**
```
Security
├─ Data encryption (TLS 1.2+ in transit, AES-256 at rest)
├─ Authentication (user ID, password, MFA)
├─ Authorization (role-based access control)
├─ Audit logging (all data access logged)
└─ Business continuity (backup and recovery)

Data Quality
├─ Data validation (range checks, reasonableness)
├─ Signal integrity (device calibration verification)
├─ Data transmission verification
├─ Error handling and notification
└─ Fallback procedures

User Interface
├─ Clear status indicators
├─ Alert thresholds and notifications
├─ Clinical interpretation support
├─ Trend visualization
└─ Data export capability
```

### Medication Management Apps

**FDA Guidance:** FDA-approved medication reminder and management apps

**Regulatory Requirements if Regulated:**
- Medication database accuracy
- Interaction checking capability
- Alerts for contraindications
- Pharmacy integration security
- Patient identification verification

**Compliance Checklist:**
- Clinical validation of drug databases
- Verification of interaction checking algorithms
- Security penetration testing
- User interface usability testing
- Accessibility compliance (WCAG)
- Documentation of data sources

### Symptom Checking and Triage Apps

**FDA Position:** Often regulated if providing diagnoses

**To Remain Non-Regulated:**
- Provide information only, not diagnosis
- Direct users to seek professional care
- Do not claim to diagnose conditions
- Do not provide treatment recommendations
- Educational material only

**If Regulated as Device:**
- Intended use statement defining scope
- Validation against standard triage protocols
- Clinical evidence supporting recommendations
- Labeling with appropriate disclaimers
- User training requirements

## Privacy and Data Protection Regulations

### HIPAA (Health Insurance Portability and Accountability Act)

**HIPAA Applicability:**
- Covered entities: Healthcare providers, health plans, clearinghouses
- Business associates: Third-party vendors processing PHI
- **Note:** Not all apps are HIPAA-covered if users are patients

**HIPAA Requirements If Applicable:**
- **Privacy Rule:** Patient access to PHI, authorization, minimum necessary
- **Security Rule:** Administrative, physical, technical safeguards
- **Breach Notification:** 60-day notification if breach occurs
- **Business Associate Agreement (BAA):** Required for third parties

### COPPA (Children's Online Privacy Protection Act)

**Applies if:**
- App users include children under 13
- App collects, uses, or discloses personal information from children
- App targets children

**Requirements:**
- Verifiable parental consent before collecting child data
- Clear privacy policy explaining data collection
- Parental access to child's information
- Ability to delete child's information
- No conditioning app access on data collection

### GDPR (General Data Protection Regulation)

**Applies if:**
- App users include EU residents
- App collects EU personal data
- Organization subject to GDPR

**Key Requirements:**
- Legal basis for data processing
- Explicit consent for data collection
- Data minimization principles
- Right to access, correction, deletion
- Data breach notification (72 hours)
- Data protection impact assessments
- Privacy by design

### State Privacy Laws

**California Consumer Privacy Act (CCPA/CPRA):**
- Consumer right to know data collected
- Right to delete collected data
- Right to opt-out of data sales
- Right to non-discrimination

**Virginia Consumer Data Protection Act (VCDPA):**
- Consumer right to access/delete/correct data
- Right to opt-out of targeted advertising
- Applies to for-profit entities processing Virginia residents' data

**Health Breach Notification Laws:**
- Most states require notification within 30-60 days
- Notification to individuals and media (if >500 affected)
- Reasonable security standards required

## Accessibility and Usability Standards

### FDA Guidance on Usability

**Usability Engineering Process:**
1. Define intended user and use environment
2. Identify use-related hazards and risks
3. Perform formative usability testing
4. Design appropriate controls/mitigations
5. Conduct summative usability validation

**Required Testing with Users:**
- Minimum 15 users per target user group
- Representative tasks from actual use
- Document failures and near-misses
- Severity assessment of issues found
- Mitigation strategies for critical issues

### WCAG 2.1 AA Accessibility Standards

**Perceivable:**
- Alternative text for images
- Captions and transcripts for multimedia
- Adaptable content structure
- Distinguishable foreground/background

**Operable:**
- Keyboard accessible (no mouse required)
- Sufficient time for all interactions
- No seizure-inducing flashing
- Navigable interface

**Understandable:**
- Readable text (font size, contrast, line spacing)
- Predictable interface behavior
- Input assistance (error prevention, correction)
- Plain language support

**Robust:**
- Valid HTML markup
- Proper heading structure
- Form labels and validation
- Screen reader compatibility

## Cybersecurity Requirements

### FDA Premarket Cybersecurity Guidance

**Required Documentation:**
```
Software Architecture
├─ System block diagrams
├─ Data flow diagrams
├─ Software component descriptions
└─ External interfaces and integrations

Threat Analysis
├─ Identified threats and vulnerabilities
├─ Attack vectors and exploit scenarios
├─ Severity and likelihood assessment
└─ Impact analysis

Mitigations and Controls
├─ Design controls for identified threats
├─ Implementation details of controls
├─ Testing and validation of controls
├─ Residual risk assessment

Update Management
├─ Software update architecture
├─ Update authentication and integrity
├─ Rollback capabilities
├─ User notification process
```

### NIST Cybersecurity Framework

**Core Functions for mHealth:**

1. **Identify**
   - Asset inventory and valuation
   - Threat and vulnerability assessment
   - Risk prioritization

2. **Protect**
   - Access control implementation
   - Data security and encryption
   - Training and awareness

3. **Detect**
   - Continuous monitoring
   - Anomaly detection
   - Intrusion detection systems

4. **Respond**
   - Incident response plan
   - Threat containment
   - Investigation procedures

5. **Recover**
   - Backup and disaster recovery
   - Restoration procedures
   - Post-incident review

### OWASP Top 10 Mobile Risks

```
1. Improper Platform Usage
2. Insecure Data Storage
3. Insecure Communication
4. Insecure Authentication
5. Insufficient Cryptography
6. Insecure Authorization
7. Client Code Quality
8. Code Tampering
9. Reverse Engineering
10. Extraneous Functionality
```

## International Regulatory Considerations

### CE Mark (Europe)
- Medical Device Directive/Regulation (MDR)
- Requirements similar to FDA
- Notified Body assessment required
- Class II and III require review

### Health Canada Medical Device License
- Similar to FDA 510(k) for most devices
- Licensing application and review
- Post-market surveillance requirements

### TGA (Australia)
- Therapeutic Goods Administration oversight
- Classification as medical device required
- Pre-market approval or notification

### PMDA (Japan)
- Pharmaceuticals and Medical Devices Agency
- Approval pathway required for regulated devices
- Clinical data may be required

## Documentation and Compliance

### Required Documentation for FDA Submission

**Device Master Record (DMR):**
- Device design specifications
- Manufacturing procedures
- Quality system documentation
- Labeling and instructions

**Software Documentation:**
- Software requirements specification (SRS)
- Software design specification (SDS)
- Software verification and validation (V&V)
- Risk management documentation
- Change control and traceability matrix

**Clinical and Non-clinical Testing:**
- Biocompatibility assessment (if applicable)
- Software testing (unit, integration, system)
- Usability testing with representative users
- Performance testing and validation
- Cybersecurity testing

### Labeling and Instructions for Use (IFU)

**Must Include:**
- Clear intended use statement
- User qualifications and training requirements
- Indications and contraindications
- Warnings and precautions
- Instructions for proper use
- Troubleshooting guidance
- Customer support contact information

## Post-Market Compliance

### Adverse Event Reporting

**FDA Medical Device Reporting (MDR):**
- Report serious injuries or deaths within 30 days
- Report malfunctions within 30 days
- Annual summary reports
- Maintain complaint logs
- Investigation of user issues

### Post-Market Surveillance

**Requirements:**
- Monitor app performance in real-world use
- Collect and analyze adverse events
- User feedback and issue tracking
- Performance against claimed specifications
- Regular security assessments
- Compliance monitoring

### Software Updates and Patches

**FDA Expectations:**
- Documented update procedures
- Change management process
- Testing before release
- User notification and consent
- Rollback capability
- Version tracking and traceability

## Compliance Program Development

### Risk-Based Approach

**Low-Risk Apps:**
- Basic compliance documentation
- Privacy policy and terms of service
- Standard security controls
- User testing for usability

**Medium-Risk Apps:**
- Clinical validation data
- More rigorous security testing
- Formative usability testing
- Post-market surveillance plan

**High-Risk Apps:**
- Comprehensive FDA submission
- Clinical evidence from studies
- Full usability validation
- Comprehensive post-market monitoring
- Regular safety audits

### Documentation Timeline

```
Pre-Development:
└─ Regulatory classification analysis

Development:
├─ Design documentation
├─ Risk management planning
└─ Security architecture

Pre-Launch:
├─ Testing and validation
├─ FDA submission (if required)
└─ Labeling and instructions

Post-Launch:
├─ Adverse event monitoring
├─ Performance surveillance
└─ Update management
```
