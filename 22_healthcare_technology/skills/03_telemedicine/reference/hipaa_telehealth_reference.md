# HIPAA Telehealth Reference

## Overview
Comprehensive guide to HIPAA compliance requirements specific to telehealth delivery, including Privacy Rule, Security Rule, Breach Notification, and enforcement considerations.

---

## HIPAA Basics for Telehealth

### What is HIPAA?

**Health Insurance Portability and Accountability Act (1996)**:
- Federal law protecting health information privacy and security
- Applies to covered entities and business associates
- Civil and criminal penalties for violations

**Three Main Rules**:
1. **Privacy Rule**: How PHI can be used and disclosed
2. **Security Rule**: How ePHI must be protected
3. **Breach Notification Rule**: Procedures when PHI is compromised

---

### Covered Entities

**Who Must Comply**:
- Healthcare providers who transmit health information electronically
- Health plans (insurers)
- Healthcare clearinghouses

**Telehealth Applicability**:
- Healthcare providers offering telehealth services are covered entities
- Must comply with HIPAA regardless of delivery modality (in-person or telehealth)

---

### Business Associates

**Definition**: Third parties that handle PHI on behalf of covered entities

**Telehealth Business Associates**:
- Video platform vendors (Zoom, Doxy.me, Twilio, etc.)
- Cloud hosting providers (AWS, Azure, GCP)
- EHR vendors
- RPM device platform vendors
- Medical transcription services
- IT support providers with PHI access
- Data analytics vendors

**Business Associate Agreement (BAA) Requirements**:
- Must be in writing before PHI is shared
- Specifies permitted uses of PHI
- Requires appropriate safeguards
- Breach reporting obligations
- Return or destruction of PHI at termination
- Allows covered entity to audit compliance

---

## Privacy Rule for Telehealth

### Permitted Uses and Disclosures

**Treatment, Payment, Healthcare Operations (TPO)**:
- Telehealth visits are treatment
- Can use and disclose PHI for TPO without patient authorization
- Minimum necessary standard applies (use only what's needed)

**Examples in Telehealth**:
- Sharing patient information between providers during telehealth consult
- Transmitting prescription to pharmacy after video visit
- Billing insurance for telehealth services
- Quality improvement analysis of telehealth outcomes

---

### Patient Rights

**Right to Access**:
- Patients can access their telehealth visit records
- Must provide within 30 days of request
- Can provide electronically if patient requests

**Right to Amend**:
- Patients can request amendments to telehealth records
- Provider can deny if record is accurate and complete

**Right to Accounting of Disclosures**:
- Patients can request list of certain disclosures
- TPO disclosures generally excluded

**Right to Confidential Communications**:
- Patients can request alternative contact methods
- Example: Don't leave voicemails about telehealth appointments

**Right to Restrict Disclosures**:
- Patients can request restrictions (provider can deny)
- Exception: Must honor if patient paid out-of-pocket and doesn't want health plan to know

**Right to Notice of Privacy Practices**:
- Must provide NPP at first telehealth visit
- Can provide electronically
- Must acknowledge receipt

---

### Minimum Necessary Standard

**Principle**: Use, disclose, and request only the minimum PHI necessary

**Telehealth Examples**:
- Scheduling staff don't need full medical history
- Billing staff need only information relevant to claim
- IT support should have minimum access to PHI

**Exceptions**:
- Disclosures to patient
- Disclosures for treatment (providers can share all necessary information)
- Disclosures required by law

---

### Consent and Authorization

**Consent for Treatment**:
- Not required by HIPAA (may be required by state law)
- Best practice: Obtain telehealth-specific consent

**HIPAA Authorization**:
- Required for uses/disclosures beyond TPO
- Marketing, research, sale of PHI
- Must be in writing with specific elements
- Patient can revoke

**Special Protections**:
- **Psychotherapy Notes**: Require separate authorization
- **Substance Abuse (42 CFR Part 2)**: Stricter consent requirements
- **HIV/AIDS Information**: State-specific consent laws may apply

---

## Security Rule for Telehealth

### Administrative Safeguards

**Security Management Process**:
1. **Risk Analysis**: Identify threats to ePHI in telehealth platform
2. **Risk Management**: Implement security measures
3. **Sanction Policy**: Discipline for security violations
4. **Information System Activity Review**: Monitor audit logs

**Workforce Security**:
- Authorize only necessary personnel to access telehealth platform
- Clearance procedures for staff
- Termination procedures (access revocation)

**Information Access Management**:
- Role-based access control
- Providers: Full clinical access
- Staff: Limited to scheduling/administrative functions
- IT: Technical access, minimal PHI viewing

**Security Awareness Training**:
- Initial training for all telehealth users
- Annual refresher training
- Phishing awareness
- Password management
- Device security

**Incident Response**:
- Procedures for detecting and responding to security incidents
- Breach reporting and mitigation

**Contingency Planning**:
- Data backup procedures
- Disaster recovery plan
- Emergency mode operations (backup communication if platform fails)

**Business Associate Management**:
- Obtain BAAs from all vendors
- Review vendor security practices
- Monitor vendor compliance

---

### Physical Safeguards

**Facility Access Controls**:
- Physical access to servers/data centers (cloud provider responsibility if using cloud)
- Visitor logs and badges

**Workstation Use and Security**:
- Providers should use telehealth in private settings
- Screen privacy filters if in semi-public areas
- Lock computers when unattended
- No telehealth from public computers

**Device and Media Controls**:
- Encryption of devices (laptops, tablets, phones)
- Secure disposal of devices
- Media sanitization before reuse or disposal

**Telehealth-Specific Considerations**:
- **Provider Location**: Ensure privacy during video visits (private room, no unauthorized viewers)
- **Patient Location**: Educate patients on privacy (private space, no others present unless consented)
- **Public WiFi**: Discourage use of public WiFi for telehealth (providers and patients)

---

### Technical Safeguards

**Access Control**:
- **Unique User Identification**: Each user has unique login
- **Emergency Access Procedure**: Break-glass access for emergencies
- **Automatic Logoff**: Session timeouts after inactivity
- **Encryption**: Encryption of ePHI where appropriate (highly recommended for telehealth)

**Audit Controls**:
- Log all access to PHI
- Record user logins, patient record access, video session participants
- Regular audit log review (weekly or monthly)

**Integrity Controls**:
- Ensure ePHI is not improperly altered or destroyed
- Checksums, hashes for data integrity
- Version control for medical records

**Person/Entity Authentication**:
- Verify identity of users accessing ePHI
- Multi-factor authentication strongly recommended
- Password complexity requirements

**Transmission Security**:
- **Encryption**: Encrypt ePHI in transit
  - TLS 1.2 or 1.3 for data transmission
  - DTLS-SRTP for video/audio streams
- **Integrity Controls**: Ensure data not altered during transmission

---

### Encryption Requirements

**Is Encryption Required?**:
- HIPAA Security Rule does not mandate encryption
- Encryption is "addressable" (must implement or document why not)
- **However**: Encryption is considered industry standard for telehealth
- Breach Notification Rule: Encrypted data has safe harbor (breach may not need to be reported)

**Best Practice**: Always encrypt ePHI both in transit and at rest

**Telehealth Encryption**:
- Video/audio streams: DTLS-SRTP (WebRTC standard)
- Data transmission (APIs, web): TLS 1.2+
- Data at rest (databases): AES-256
- Recordings: Encrypted storage

---

## Breach Notification Rule

### What is a Breach?

**Definition**: Unauthorized acquisition, access, use, or disclosure of PHI that compromises security or privacy

**Exceptions** (Not Breaches):
1. **Unintentional Access**: Staff member unintentionally accesses PHI in good faith within scope of authority (and doesn't further use/disclose)
2. **Inadvertent Disclosure**: Between authorized persons at same organization (and info not further used/disclosed)
3. **Unable to Retain**: Recipient unable to retain PHI (e.g., sent to wrong email but recipient didn't open and deleted)

**Low Probability of Compromise**:
- Risk assessment showing low probability PHI was compromised
- Factors: Nature of PHI, unauthorized person, whether PHI acquired/viewed, extent of mitigation
- **Encrypted Data Safe Harbor**: Breach of encrypted PHI (with proper key management) is not a breach

---

### Breach Examples in Telehealth

**Breaches**:
- Hacker gains access to patient video recordings
- Unencrypted laptop with patient data stolen
- Unauthorized person joins telehealth visit
- Patient data emailed to wrong recipient who opens it
- Vendor suffers data breach exposing patient PHI
- Lost unencrypted mobile device with patient information

**Not Breaches** (with proper risk assessment):
- Encrypted device lost (encryption key not compromised)
- Wrong patient invited to telehealth visit but immediately corrected before they joined
- Staff member accidentally views wrong patient chart, realizes immediately, doesn't use info

---

### Breach Notification Requirements

**Timeline**:
- **Discovery**: Breach discovered when known to any employee/agent
- **60 Days**: Must notify affected individuals within 60 days of discovery

**Individual Notification**:
- **Method**: Written notice by first-class mail (or email if patient agreed)
- **Content**:
  - Brief description of breach
  - Date of breach and date discovered
  - Types of PHI involved
  - Steps individuals should take
  - What organization is doing to investigate and mitigate
  - Contact information

**HHS Notification**:
- **>500 Individuals**: Notify HHS Office for Civil Rights within 60 days, media notification
- **<500 Individuals**: Annual notification to HHS (within 60 days of year-end)

**Business Associate Notification**:
- Business associate must notify covered entity within 60 days of discovering breach

**Media Notification** (if >500 individuals in same state/jurisdiction):
- Notify prominent media outlets
- Same 60-day timeline

---

### Breach Response Plan

**Immediate Actions** (within hours):
1. Contain the breach (isolate affected systems)
2. Preserve evidence
3. Notify security/privacy officer and management
4. Begin investigation

**Investigation** (within days):
1. Determine scope: What PHI? How many patients?
2. Identify cause: How did breach occur?
3. Assess harm: What is risk to patients?
4. Document everything

**Mitigation** (within days-weeks):
1. Remediate vulnerability
2. Implement safeguards to prevent recurrence
3. Notify affected parties (if required)
4. Offer credit monitoring/identity protection if appropriate

**Follow-Up** (ongoing):
1. Monitor for further unauthorized access
2. Update policies and procedures
3. Retrain workforce
4. Report to HHS/media if required
5. Cooperate with OCR investigation if initiated

---

## COVID-19 Telehealth Flexibilities

### OCR Temporary Enforcement Discretion

**Public Health Emergency (PHE) Policy**:
- **Period**: March 2020 - May 2023 (PHE ended May 11, 2023)
- **Policy**: OCR would not impose penalties for HIPAA violations related to good faith provision of telehealth
- **Allowed**: Use of non-HIPAA-compliant platforms (FaceTime, Skype, Zoom free, etc.)
- **Not Allowed**: Public-facing platforms (Facebook Live, TikTok, etc.)

**Post-PHE Status**:
- Enforcement discretion ended May 12, 2023
- Must now use HIPAA-compliant platforms with BAAs
- Some flexibilities made permanent (e.g., remote prescribing in certain cases)

---

### Current Requirements (Post-PHE)

**Video Platforms**:
- Must obtain BAA from vendor
- Must use HIPAA-compliant configurations
- Encryption required

**Acceptable Platforms** (with BAA):
- Zoom for Healthcare
- Doxy.me (all tiers)
- Microsoft Teams for Healthcare
- Twilio Video
- Amazon Chime SDK
- VSee
- Any platform willing to sign BAA and provide adequate safeguards

**Not Acceptable** (without BAA):
- Zoom free/personal accounts
- Skype
- FaceTime (Apple does not sign BAAs)
- Google Meet free
- WhatsApp video

---

## State Laws and Telehealth

### Stricter State Laws Apply

**HIPAA is Minimum Standard**:
- States can have stricter privacy laws
- Must comply with both HIPAA and state laws
- If conflict, comply with stricter requirement

**Examples of Stricter State Laws**:
- **California CMIA**: Stricter than HIPAA in some areas
- **Texas HIB**: Additional consent requirements
- **Massachusetts**: Stricter data breach notification timelines

**Special Categories of Information**:
- **Mental Health**: Many states have additional protections
- **HIV/AIDS**: State-specific confidentiality laws
- **Genetic Information**: Additional protections in some states
- **Substance Abuse**: 42 CFR Part 2 (federal), stricter than HIPAA

---

### 42 CFR Part 2 (Substance Abuse Treatment)

**Applicability**: Programs that specialize in substance abuse treatment

**Stricter Requirements**:
- Patient consent required for most disclosures (even for TPO)
- Consent must be in writing with specific elements
- Prohibition on re-disclosure
- Applies to telehealth for substance abuse treatment

**Telehealth Considerations**:
- Obtain Part 2 consent before telehealth visit
- Ensure video platform BAA includes Part 2 compliance
- Train staff on Part 2 requirements
- Separate Part 2 records from general medical records

---

## Enforcement and Penalties

### OCR Enforcement

**Office for Civil Rights (OCR)**:
- HHS agency enforcing HIPAA
- Investigates complaints and breaches
- Conducts compliance audits
- Imposes penalties

**Investigation Process**:
1. Complaint filed or breach reported
2. OCR reviews and determines if jurisdiction
3. Investigation (document requests, interviews)
4. Determination: Violation or no violation
5. If violation: Corrective action plan or penalties

---

### Penalties

**Civil Penalties** (per violation):
- **Tier 1**: Did not know (and could not have known): $100-$50,000
- **Tier 2**: Reasonable cause: $1,000-$50,000
- **Tier 3**: Willful neglect (corrected): $10,000-$50,000
- **Tier 4**: Willful neglect (not corrected): $50,000

**Annual Maximums**: Up to $1.5 million per violation type per year

**Criminal Penalties** (for knowing violations):
- **Tier 1**: Knowingly obtain/disclose PHI: Up to $50,000 fine, 1 year in prison
- **Tier 2**: Offense under false pretenses: Up to $100,000 fine, 5 years in prison
- **Tier 3**: Intent to sell/transfer/use for commercial advantage, harm, or malice: Up to $250,000 fine, 10 years in prison

---

### Notable Telehealth Enforcement Actions

**Examples**:
- **Zoom (2021)**: $85 million FTC settlement (not HIPAA-specific, but privacy violations)
- Various small providers fined for using non-compliant platforms
- Vendors fined for inadequate safeguards

**Lessons**:
- Use only HIPAA-compliant platforms with BAAs
- Implement proper safeguards (encryption, access controls, etc.)
- Train workforce on HIPAA requirements
- Have incident response plan
- Document compliance efforts

---

## HIPAA Compliance Checklist for Telehealth

### Before Launch

**Privacy**:
- [ ] Notice of Privacy Practices updated to include telehealth
- [ ] Telehealth consent form created
- [ ] Patient rights procedures established
- [ ] Minimum necessary policies applied to telehealth workflows

**Security**:
- [ ] Risk analysis completed for telehealth platform
- [ ] Risk management plan implemented
- [ ] Access controls configured (RBAC, MFA)
- [ ] Encryption enabled (in transit and at rest)
- [ ] Audit logging enabled
- [ ] Workforce security policies updated
- [ ] Incident response plan includes telehealth scenarios
- [ ] Data backup and disaster recovery tested

**Business Associates**:
- [ ] BAA signed with video platform vendor
- [ ] BAA signed with cloud hosting provider
- [ ] BAA signed with EHR vendor (if applicable)
- [ ] BAA signed with any other vendors handling PHI
- [ ] Vendor security assessments reviewed

**Training**:
- [ ] All workforce trained on HIPAA basics
- [ ] Telehealth-specific training completed
- [ ] Training documented

---

### Ongoing Compliance

**Monthly**:
- [ ] Review audit logs for anomalies
- [ ] Review access permissions (add/remove users as needed)
- [ ] Check for security patches/updates
- [ ] Review any security incidents

**Quarterly**:
- [ ] Conduct internal compliance audit
- [ ] Review and update risk analysis
- [ ] Test incident response plan
- [ ] Review BAAs and vendor compliance

**Annually**:
- [ ] Comprehensive risk analysis update
- [ ] Workforce HIPAA training refresher
- [ ] Policies and procedures review/update
- [ ] Vendor security assessment review
- [ ] Breach notification procedures review

---

## Best Practices

### For Providers

**Before Telehealth Visit**:
- Use HIPAA-compliant platform only
- Conduct visit in private setting
- Ensure computer screen not visible to others
- Lock office door or use "in session" indicator
- Use headphones for audio privacy

**During Visit**:
- Verify patient identity
- Confirm patient is in private location
- No recording without consent
- No screen sharing of other patients' information

**After Visit**:
- Log out of platform
- Lock computer
- Document visit promptly
- Secure any notes or printouts

---

### For Organizations

**Technology**:
- Choose HIPAA-compliant platforms with strong security
- Obtain BAAs from all vendors
- Implement encryption everywhere
- Use multi-factor authentication
- Regular security assessments

**Policies**:
- Clear telehealth HIPAA policies
- Acceptable use policies for providers
- Patient education on privacy practices
- Incident response procedures

**Training**:
- Initial and annual HIPAA training
- Telehealth-specific scenarios
- Incident reporting procedures
- Test exercises (simulated breaches)

**Monitoring**:
- Regular audit log review
- User access reviews
- Compliance audits
- Patient complaints monitoring

---

## Resources

### Official Guidance
- **HHS OCR**: Official HIPAA guidance and FAQs
- **OCR Telehealth Guidance**: Specific guidance on telehealth and HIPAA
- **HIPAA Privacy, Security, and Breach Notification Rules**: Full regulatory text

### Industry Resources
- **ATA Practice Guidelines**: Telehealth privacy and security
- **NIST Cybersecurity Framework**: Risk-based security approach
- **HITRUST CSF**: Healthcare security framework

### Training Resources
- **HHS Office for Civil Rights**: Free HIPAA training modules
- **AHIMA**: Health information management training
- **Telehealth certification programs**: Specialized telehealth training

---

*Last Updated: 2025*
*Version: 1.0*
