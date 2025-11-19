# HIPAA Breach Notification Rule Reference

## Overview

The HIPAA Breach Notification Rule (45 CFR §§164.400-414) requires covered entities and business associates to provide notification following a breach of unsecured protected health information (PHI).

## Effective Date

September 23, 2009 (modified by Omnibus Rule effective March 26, 2013)

## Key Definitions

### Breach (§164.402)

**Definition:** Acquisition, access, use, or disclosure of PHI in a manner not permitted under the Privacy Rule that compromises the security or privacy of PHI.

**Exclusions (Not a Breach):**

1. **Unintentional Acquisition, Access, or Use**
   - By workforce member or person acting under authority
   - Acting in good faith
   - Within scope of authority
   - Does not result in further impermissible use or disclosure

   **Example:** Nurse accidentally accesses wrong patient's record, realizes immediately, closes record, does not share information

2. **Inadvertent Disclosure**
   - From authorized person to another authorized person
   - At same covered entity or business associate or organized healthcare arrangement
   - Information is not further used or disclosed impermissibly

   **Example:** Doctor discusses patient with wrong nurse, both authorized to access PHI at same facility, nurse does not further disclose

3. **Recipient Cannot Reasonably Retain Information**
   - Good faith belief that unauthorized person would not reasonably have been able to retain information

   **Example:** Faxed to wrong number, recipient confirms they did not read it, deleted/destroyed it

### Unsecured PHI (§164.402)

**Definition:** PHI not rendered unusable, unreadable, or indecipherable to unauthorized persons through:

1. **Encryption** (using NIST-specified algorithm)
   - Data at rest: AES 128-bit or higher
   - Data in transit: TLS 1.2 or higher

2. **Destruction**
   - Paper: shredding, burning, pulverizing
   - Electronic media: clearing, purging, or destroying per NIST SP 800-88
   - Hardware: degaussing, disintegration, pulverization

**Key Point:** If PHI was encrypted or properly destroyed, breach notification rules do NOT apply.

### Breach Discovery Date (§164.402)

**First day on which breach is known or should have been known:**
- When any workforce member (other than wrongdoer) becomes aware
- When covered entity/BA should have known through reasonable diligence
- Whichever is earlier

**Not Discovery:** When only the individual(s) who impermissibly used/disclosed knew

## Risk Assessment (§164.402)

### Purpose
Determine if breach notification is required based on probability that PHI has been compromised.

### Presumption
**Impermissible use/disclosure is presumed to be a breach unless covered entity or business associate demonstrates low probability of compromise.**

**Burden of Proof:** On covered entity/business associate to prove NOT a breach.

### Four-Factor Risk Assessment

Must consider AT LEAST the following factors:

#### 1. Nature and Extent of PHI Involved

**Consider:**
- Types of identifiers involved (names, SSNs, addresses, etc.)
- Sensitivity of information (diagnosis, treatment, financial data)
- Likelihood information could identify individual
- Amount of information involved

**Higher Risk Indicators:**
- Full names with SSN, financial account numbers
- Highly sensitive conditions (HIV, mental health, substance abuse)
- Complete medical records
- Large number of data elements

**Lower Risk Indicators:**
- Limited data elements
- Non-sensitive information
- De-identified or partially redacted data

#### 2. Unauthorized Person Who Used PHI or to Whom Disclosure Was Made

**Consider:**
- Relationship to covered entity
- Level of sophistication
- Obligations to protect information
- Intent or reason for unauthorized access

**Higher Risk Indicators:**
- Unknown third party
- Competitor
- Media organization
- Identity thief
- Person with malicious intent

**Lower Risk Indicators:**
- Another covered entity or BA with confidentiality obligations
- Person who inadvertently received information
- Person with professional duty to protect privacy
- Employee of covered entity/BA (depending on circumstances)

#### 3. Whether PHI Was Actually Acquired or Viewed

**Consider:**
- Evidence of actual viewing or acquisition
- Technical logs showing access
- Opportunity to view/acquire
- Forensic evidence

**Higher Risk Indicators:**
- Confirmed viewing/acquisition
- PHI downloaded, printed, or copied
- Extended access time
- Multiple access attempts

**Lower Risk Indicators:**
- No evidence of viewing (e.g., unopened email)
- Technical barriers prevented viewing
- Brief, accidental exposure
- Recipient confirms non-viewing and destruction

#### 4. Extent to Which Risk Has Been Mitigated

**Consider:**
- Actions taken to reduce risk
- Effectiveness of mitigation
- Timeliness of response
- Obtained assurances from recipient

**Risk Mitigation Examples:**
- Retrieved/destroyed information
- Obtained signed confidentiality agreement
- Recipient confirmed destruction and non-viewing
- Technical safeguards prevented access to PHI within larger dataset
- Implemented additional security measures

**Documentation Required:**
- What mitigation steps taken
- When taken
- Evidence of effectiveness
- Assurances obtained

### Risk Assessment Documentation

**Must Document:**
- All four factors considered
- Analysis of each factor
- Conclusion (breach or not)
- Date of assessment
- Person(s) who conducted assessment
- Rationale for conclusion

**Retention:** Minimum 6 years

## Notification Requirements

### Covered Entity Responsibilities

#### 1. Individual Notification (§164.404)

**Timing:**
- Without unreasonable delay
- No later than 60 days from discovery of breach

**Method - First Priority:**
- Written notice by first-class mail to:
  - Individual at last known address
  - Next of kin or personal representative if individual deceased

**Method - Alternative (if insufficient or out-of-date contact information):**
- **Fewer than 10 individuals:** Alternative written notice, telephone, or other means
- **10 or more individuals:**
  - Conspicuous posting on homepage of website for 90 days, OR
  - Notice in major print or broadcast media where individuals likely reside

**Content - Must Include:**

1. **Brief Description of Breach**
   - What happened
   - Date of breach (or estimated date)
   - Date of discovery

2. **Types of Unsecured PHI Involved**
   - Medical information
   - Financial information
   - Demographic information
   - Specific identifiers (SSN, etc.)

3. **Steps Individuals Should Take**
   - Protect against potential harm
   - Monitor accounts
   - Credit monitoring if appropriate
   - Fraud alerts

4. **Brief Description of Entity's Response**
   - Investigation conducted
   - Mitigation efforts
   - Protection against further breaches

5. **Contact Procedures**
   - Designated person/office
   - Toll-free phone number
   - Email address
   - Website
   - Postal address

**Format Requirements:**
- Written in plain language
- Clear and concise
- Not overly legalistic
- Understandable to average reader

**Substitute Notice (when contact information insufficient):**
- Attempt alternative contact methods
- If 10+ individuals: post on website for 90 days or media notice
- If fewer than 10: phone or alternative written notice

#### 2. Media Notification (§164.406)

**Requirement:**
- Breaches affecting 500+ residents of a state or jurisdiction
- Prominent media outlets serving the state/jurisdiction

**Timing:**
- Without unreasonable delay
- No later than 60 days from discovery

**Method:**
- Press release to prominent media outlets
- May supplement with other media

**Content:**
- Same information required for individual notification

#### 3. HHS Secretary Notification (§164.408)

**For Breaches Affecting 500+ Individuals:**
- Contemporaneous with individual notification
- Within 60 days of discovery
- Submit via HHS website breach portal
- Posted on HHS "Wall of Shame" website

**For Breaches Affecting Fewer Than 500 Individuals:**
- Maintain internal log of breaches
- Submit annually to HHS
- By no later than 60 days after end of calendar year
- Via HHS website

**Information to Provide:**
- Name of covered entity
- Breach description
- Number of individuals affected
- Date of breach
- Date of discovery
- Types of PHI involved
- Brief summary

### Business Associate Responsibilities (§164.410)

**Discovery of Breach:**
- Notify covered entity without unreasonable delay
- No later than 60 days from discovery

**Information to Provide:**
- Identification of each individual whose PHI has been breached
- Any other available information required for covered entity to notify individuals
- Information on four-factor risk assessment if BA conducted

**Covered Entity Obligations:**
- Covered entity remains responsible for individual notification
- BA notification to CE does not satisfy individual notification requirement
- CE must still send notifications within 60 days of CE's discovery

## Breach Documentation Requirements (§164.414)

### Breach Log

**Required Elements:**
1. Date of breach
2. Brief description of breach
3. Number of individuals affected (or reasonable estimate)
4. Date breach discovered
5. Date individuals notified (or if not yet notified, anticipated date)
6. Date HHS Secretary notified (or anticipated date)
7. Brief description of risk assessment and conclusion

**Retention:**
- Minimum 6 years from date of creation or last effective date

**Purpose:**
- Track all breaches (regardless of notification requirement)
- Annual reporting to HHS for sub-500 breaches
- Demonstrate compliance
- Identify patterns or systemic issues

## Law Enforcement Delay (§164.412)

**Permitted Delay:**
Covered entity may delay notification if law enforcement official states that notification would:
- Impede criminal investigation
- Cause damage to national security

**Requirements:**
- Written statement from law enforcement
- Specifying time delay needed
- Resume notification after specified time or when law enforcement advises

**Does NOT eliminate notification requirement, only delays it**

## State Law Preemption

### General Rule
HIPAA does not preempt more stringent state breach notification laws.

### Common State Variations
- Shorter notification timeframes
- Different thresholds (e.g., any unauthorized access)
- Additional notification recipients (state attorney general)
- Specific content requirements
- Credit monitoring requirements

### Compliance Strategy
- Identify applicable state laws
- Comply with most stringent requirements
- Document compliance with all applicable laws

## Penalties for Non-Compliance

### Civil Penalties
Same penalty structure as other HIPAA violations:
- Tier 1: $100-$50,000 per violation (unknowing)
- Tier 2: $1,000-$50,000 per violation (reasonable cause)
- Tier 3: $10,000-$50,000 per violation (willful neglect, corrected)
- Tier 4: $50,000-$1,876,814 per violation (willful neglect, not corrected)

### Criminal Penalties
If applicable:
- Tier 1: Up to $50,000 and 1 year
- Tier 2: Up to $100,000 and 5 years
- Tier 3: Up to $250,000 and 10 years

### State Penalties
May include separate penalties under state breach notification laws.

## Common Breach Scenarios

### 1. Lost/Stolen Unencrypted Devices
**Scenario:** Laptop, smartphone, or USB drive with unencrypted PHI lost or stolen

**Analysis:**
- Unsecured PHI: YES (not encrypted)
- Breach presumption: YES
- Notification likely required unless can prove low probability of compromise

### 2. Unauthorized Employee Access
**Scenario:** Employee accesses patient records without job-related reason (e.g., celebrity, neighbor, family member)

**Analysis:**
- Impermissible access: YES
- Need risk assessment
- If malicious intent: likely breach
- If inadvertent and limited: may not be breach

### 3. Misdirected Email/Fax
**Scenario:** PHI sent to wrong recipient

**Analysis:**
- Consider recipient (another CE/BA vs. unknown party)
- Whether actually viewed
- Whether retrieved/destroyed
- Recipient's obligations and assurances
- May or may not be breach depending on factors

### 4. Hacking/Cyber Attack
**Scenario:** Unauthorized external access to system containing PHI

**Analysis:**
- Unsecured PHI: depends on encryption
- Need forensic investigation
- Determine what was accessed/exfiltrated
- Typically requires notification

### 5. Improper Disposal
**Scenario:** PHI discarded without proper destruction (e.g., records in dumpster, unwiped hard drive sold)

**Analysis:**
- Unsecured PHI: YES (not properly destroyed)
- Breach presumption: YES
- Notification likely required

### 6. Insider Theft
**Scenario:** Employee steals PHI for personal gain

**Analysis:**
- Impermissible use: YES
- Breach presumption: YES
- Notification required
- Criminal investigation likely

## Best Practices

### Prevention
1. Encrypt all PHI (renders breach notification rule inapplicable)
2. Implement strong access controls
3. Train workforce on proper PHI handling
4. Monitor for unauthorized access
5. Use secure communication methods
6. Implement proper disposal procedures
7. Conduct regular security risk assessments
8. Maintain business associate agreements
9. Implement data loss prevention (DLP) tools
10. Use mobile device management (MDM) for mobile devices

### Preparation
1. Develop breach response plan
2. Establish breach response team
3. Create notification templates
4. Identify media outlets for each jurisdiction
5. Train staff on breach reporting
6. Establish relationship with forensic specialists
7. Review cyber insurance coverage
8. Prepare FAQ documents for individuals
9. Establish crisis communication plan

### Response
1. Contain breach immediately
2. Preserve evidence
3. Assemble breach response team
4. Conduct thorough investigation
5. Perform four-factor risk assessment
6. Document all steps
7. Notify appropriate parties within timeframes
8. Provide assistance to affected individuals
9. Conduct post-incident review
10. Implement corrective actions

### Documentation
1. Maintain detailed breach log
2. Document risk assessments
3. Keep copies of all notifications
4. Track notification delivery
5. Document mitigation efforts
6. Retain for minimum 6 years
7. Make available for OCR review

## Regulatory Citations

- 45 CFR §164.400 - Applicability
- 45 CFR §164.402 - Definitions
- 45 CFR §164.404 - Notification to individuals
- 45 CFR §164.406 - Notification to the media
- 45 CFR §164.408 - Notification to the Secretary
- 45 CFR §164.410 - Notification by a business associate
- 45 CFR §164.412 - Law enforcement delay
- 45 CFR §164.414 - Administrative requirements and burden of proof

## Additional Resources

- HHS Breach Notification Rule guidance
- HHS Breach Portal ("Wall of Shame"): https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf
- Sample notification letters and templates
- State breach notification law compilation
- Risk assessment worksheets
