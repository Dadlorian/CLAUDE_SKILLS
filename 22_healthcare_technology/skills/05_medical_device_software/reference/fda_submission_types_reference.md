# FDA Submission Types Reference

## Overview

This reference covers the different types of FDA submissions for medical devices, focusing on premarket pathways and when each applies.

## Submission Pathways Overview

```
Device Risk Classification
        ↓
┌───────┴───────┐
│               │
Class I      Class II        Class III
   ↓            ↓               ↓
Exempt     510(k) or        PMA or
           De Novo         De Novo
```

## Device Classification

### Class I (Low Risk)
**Examples:**
- Elastic bandages
- Manual surgical instruments
- Most software for administrative purposes

**Premarket Requirements:**
- Most are exempt from premarket notification
- General controls only
- Some require 510(k)

### Class II (Moderate Risk)
**Examples:**
- Powered wheelchairs
- Infusion pumps
- Most diagnostic software
- Patient monitors

**Premarket Requirements:**
- Usually 510(k) clearance
- General and special controls
- De Novo if novel

### Class III (High Risk)
**Examples:**
- Heart valves
- Implantable pacemakers
- Life-sustaining ventilators
- Some AI diagnostic systems

**Premarket Requirements:**
- PMA approval (most)
- General and special controls
- Clinical data usually required
- De Novo if low-to-moderate risk novel device

## 510(k) Premarket Notification

### Purpose
Demonstrate that device is substantially equivalent to a legally marketed predicate device.

### Types of 510(k)

#### Traditional 510(k)
**Most common pathway**
- Comparison to predicate device
- Demonstrate substantial equivalence
- May require performance testing

**Timeline:** 90 days FDA review goal

#### Special 510(k) - Device Modification
**For changes to manufacturer's own device**
- Design controls used
- Change does not affect intended use
- Change does not affect fundamental scientific technology

**Timeline:** 30 days FDA review goal

**Benefits:**
- Faster review
- Less documentation
- Abbreviated review process

#### Abbreviated 510(k)
**Uses guidance documents or consensus standards**
- Declare conformance to special controls
- Use recognized standards
- Reduce testing burden

**Timeline:** 90 days FDA review goal

### Substantial Equivalence

**Definition:**
Device has same intended use and same technological characteristics, OR same intended use, different technological characteristics, but does not raise new questions of safety/effectiveness.

**Comparison Criteria:**
1. **Intended Use**: Same clinical purpose
2. **Technological Characteristics**:
   - Materials
   - Design
   - Energy source
   - Operating principles
   - Software algorithms

**Not Substantially Equivalent (NSE):**
- Different intended use
- Same intended use but raises new safety/effectiveness questions
- Results in De Novo or PMA pathway

### 510(k) Content

**Administrative Information:**
- Applicant information
- Device identification
- Predicate device identification
- Classification

**Device Description:**
- Detailed description
- Intended use statement
- Indications for use
- Operating principles
- Hardware/software specifications

**Substantial Equivalence Discussion:**
- Comparison to predicate
- Similarities and differences
- Why differences don't raise new questions

**Performance Data:**
- Bench testing
- Software validation
- Biocompatibility (if applicable)
- Electrical safety
- Electromagnetic compatibility
- Clinical data (if needed)

**Software Documentation** (per FDA Software Guidance):
- Level of Concern
- Software Description
- Device Hazard Analysis
- Software Requirements Specification
- Design Documentation
- Verification and Validation
- Traceability
- Revision History
- Unresolved Anomalies
- Cybersecurity

**Labeling:**
- Draft labels
- Instructions for use
- Warnings and precautions

### 510(k) Review Process

**Submission:**
- Electronic submission via eSTAR
- Application complete check (15 days)

**Interactive Review:**
- FDA questions (additional information requests)
- Manufacturer responses
- May have multiple rounds

**Decision:**
- **Substantially Equivalent (SE)**: Cleared for marketing
- **Not Substantially Equivalent (NSE)**: Cannot market via 510(k)
- **Additional Information Needed**: Respond to questions

**Timeline:**
- Goal: 90 days (Traditional, Abbreviated)
- Goal: 30 days (Special)
- Clock stops during manufacturer response

## De Novo Classification

### Purpose
New classification pathway for novel low-to-moderate risk devices with no predicate.

### When to Use

**Eligible if:**
- Device is novel (no predicate)
- Device is low-to-moderate risk
- General and special controls provide reasonable assurance of safety/effectiveness

**Examples:**
- Novel diagnostic algorithms
- New types of wearable monitors
- Novel software as medical device (SaMD)

### De Novo Process

**Two Pathways:**

1. **Direct De Novo**
   - Submit without 510(k)
   - Most efficient if clearly no predicate

2. **Post-NSE De Novo**
   - After 510(k) NSE decision
   - Within 30 days of NSE

**Submission Content:**
- Similar to 510(k) but no predicate comparison
- Describe device
- Risk analysis
- Proposed special controls
- Performance data
- Clinical data (if needed)
- Benefit-risk analysis

**FDA Review:**
- Goal: 150 days
- May request additional information
- Interactive review process

**Outcomes:**
- **Granted**: Device classified as Class I or II, special controls established
- **Denied**: Device stays Class III, requires PMA
- **Withdrawn**: Manufacturer withdraws request

**Benefits:**
- Once granted, becomes predicate for future 510(k)s
- Class I or II device (lower regulatory burden than PMA)
- Device can be marketed

### Special Controls

**Purpose:**
Provide reasonable assurance of safety and effectiveness for Class II.

**Examples:**
- Performance standards
- Labeling requirements
- Patient registries
- Post-market surveillance
- Specific testing requirements

**Established Through:**
- De Novo classification
- Regulation/guidance

## PMA (Premarket Approval)

### Purpose
Most stringent regulatory pathway; demonstrates reasonable assurance of safety and effectiveness for Class III devices.

### When Required
- Class III devices
- Life-sustaining or life-supporting
- Implantable
- Substantial importance in preventing health impairment
- Presents potential unreasonable risk

**Examples:**
- Implantable cardioverter defibrillators
- Heart valves
- Breast implants
- Deep brain stimulators

### PMA Content

**Administrative:**
- Applicant information
- Table of contents
- Summary

**Device Description:**
- Comprehensive description
- Operating principles
- Materials
- Software (detailed documentation)

**Manufacturing:**
- Manufacturing processes
- Facilities
- Quality system

**Nonclinical Studies:**
- Bench testing
- Animal studies
- Biocompatibility
- Software verification/validation
- Electrical safety
- Sterilization validation

**Clinical Studies:**
- Study protocols
- Clinical data
- Statistical analysis
- Safety and effectiveness results
- Risk-benefit analysis

**Labeling:**
- Proposed labeling
- Instructions for use
- Training materials

### PMA Review Process

**Filing Review (45 days):**
- Administrative completeness
- Scientific completeness
- Acceptance decision

**Substantive Review (180 days from filing):**
- Scientific review
- Advisory panel (may be required)
- Additional information requests
- Facility inspections

**Advisory Panel:**
- Public meeting
- Expert recommendations
- FDA considers but not bound

**Decision:**
- **Approved**: May be marketed
- **Approvable**: Approve with conditions
- **Not Approvable**: Safety/effectiveness not demonstrated
- **Withdrawn**: Manufacturer withdraws

**Post-Approval:**
- Conditions of approval
- Post-approval studies (often required)
- Annual reports
- PMA supplements for changes

### PMA Supplements

**180-Day Supplement:**
- Significant changes
- Manufacturing changes
- New indications
- Design changes affecting safety/effectiveness

**Special PMA Supplement:**
- Design changes per design controls
- Does not affect safety/effectiveness
- 30-day review goal

**30-Day Notice:**
- Minor changes
- Labeling changes
- Manufacturing process changes (minor)

**Annual Report:**
- Summary of changes
- No pre-approval needed

## HDE (Humanitarian Device Exemption)

### Purpose
Pathway for devices for rare diseases/conditions (<8,000 patients/year in U.S.).

### Requirements
- Humanitarian Use Device (HUD) designation
- Demonstrate probable benefit (not effectiveness)
- No comparable alternative
- IRB approval required for each use
- Annual distribution number (ANN) limit: 8,000 units

### Similar to PMA but:
- Lower evidence threshold
- Probable benefit vs. effectiveness
- Sales restrictions
- IRB oversight

## Breakthrough Devices Program

### Purpose
Expedited pathway for devices that provide more effective treatment or diagnosis of life-threatening or irreversibly debilitating diseases.

### Eligibility
- More effective treatment/diagnosis
- For life-threatening/debilitating diseases
- Breakthrough technology OR no approved alternatives

### Benefits
- Priority review
- Interactive communication with FDA
- Senior management involvement
- Increased data development guidance

### Process
1. Request designation
2. FDA evaluates in 60 days
3. If granted, work with FDA on efficient development
4. Still requires 510(k), De Novo, or PMA

## Q-Submission (Pre-Submission)

### Purpose
Obtain FDA feedback before formal submission.

### Types

**Pre-Submission (Pre-Sub):**
- Discuss regulatory pathway
- Testing protocols
- Clinical trial design
- Software documentation

**Written Feedback Only:**
- Submit questions
- FDA provides written response

**Meeting Requested:**
- Submit questions + meeting request
- FDA teleconference or in-person meeting
- Written feedback + discussion

### Benefits
- Reduce uncertainty
- Align on testing approach
- Clarify regulatory pathway
- Avoid submission deficiencies

### Timeline
- Submit at least 2-3 months before intended submission
- FDA response in 75-90 days

## Software-Specific Pathways

### Software as a Medical Device (SaMD)

**Classification depends on:**
1. **Significance to healthcare decision**
   - Treat/Diagnose
   - Drive clinical management
   - Inform clinical management

2. **Healthcare situation**
   - Critical
   - Serious
   - Non-serious

**Resulting Classification:**
- Category I-II: Usually Class I or II (510(k) or De Novo)
- Category III-IV: Usually Class II or III (510(k), De Novo, or PMA)

### Clinical Decision Support (CDS) Exclusion

**Per 21st Century Cures Act, CDS not regulated if:**
- Not for acquiring/analyzing images or signals
- Provides recommendations
- Enables independent review of basis
- Includes limitations and warnings
- Not for serious/life-threatening conditions driving management

**If CDS meets exclusion:**
- Not a medical device
- No FDA submission required

### Mobile Medical Apps

**Enforcement approach depends on:**
- Intended use
- Risk level
- Functionality

**Higher Risk (Regulated):**
- Transforms mobile platform into medical device
- Accessory to regulated device
- Displays/analyzes medical device data

**Lower Risk (Not Enforced):**
- General wellness
- Patient education
- EHR access
- Simple tools for HCPs

## Submission Preparation Timeline

### Typical Timelines

**510(k) Preparation:**
- 6-12 months (depending on complexity)
- Testing: 3-6 months
- Documentation: 2-4 months
- FDA review: 3-6 months
- **Total: 9-18 months**

**De Novo Preparation:**
- 9-18 months
- Testing: 4-8 months
- Documentation: 3-6 months
- FDA review: 6-12 months
- **Total: 12-24 months**

**PMA Preparation:**
- 2-5 years
- Clinical trials: 1-3 years
- Testing: 6-12 months
- Documentation: 6-12 months
- FDA review: 12-24 months
- **Total: 3-7 years**

## Common Submission Deficiencies

### 510(k) Deficiencies

1. **Inadequate Predicate Comparison**
   - Predicate not appropriate
   - Differences not addressed
   - New questions not acknowledged

2. **Insufficient Performance Data**
   - Testing incomplete
   - Standards not followed
   - Acceptance criteria unclear

3. **Incomplete Software Documentation**
   - Level of Concern not justified
   - V&V inadequate
   - Cybersecurity gaps

4. **Labeling Issues**
   - Indications too broad
   - Warnings inadequate
   - Instructions unclear

### PMA Deficiencies

1. **Inadequate Clinical Data**
   - Sample size too small
   - Study design flaws
   - Endpoints not met

2. **Manufacturing Concerns**
   - Process not validated
   - Quality system gaps
   - Sterilization inadequate

3. **Risk-Benefit Not Demonstrated**
   - Safety concerns unresolved
   - Effectiveness not shown
   - Benefits don't outweigh risks

## Submission Tips

### General Tips

1. **Pre-Submission Meeting**
   - Discuss approach with FDA
   - Align on testing
   - Clarify documentation needs

2. **Use Recognized Standards**
   - IEC 62304 for software
   - ISO 14971 for risk management
   - Electrical safety standards
   - EMC standards

3. **Complete Submission**
   - Address all requirements
   - Don't leave gaps
   - Thorough documentation

4. **Clear Writing**
   - Organized structure
   - Executive summaries
   - Logical flow
   - Tables and figures

5. **Anticipate Questions**
   - Address potential concerns
   - Provide rationale
   - Reference data

### Software-Specific Tips

1. **Level of Concern**
   - Thorough hazard analysis
   - Clear justification
   - Link to patient safety

2. **Traceability**
   - Complete matrices
   - Requirements to tests
   - Risks to controls to tests

3. **Cybersecurity**
   - Threat model
   - SBOM
   - Security testing
   - Update mechanism

4. **Verification and Validation**
   - Test all requirements
   - Realistic conditions
   - Clear pass/fail criteria
   - Documented results

5. **SOUP Management**
   - List all components
   - Known anomalies
   - Validation testing
   - Version control

## Post-Market Requirements

**All Pathways Require:**
- Medical Device Reporting (MDR)
- Corrections and Removals reporting
- Quality System Regulation compliance
- Registration and Listing
- Labeling requirements

**Additional for PMA:**
- Annual reports
- Post-approval studies (often)
- PMA supplements for changes

---

**Key Takeaway**: Choose the appropriate regulatory pathway based on device risk and novelty. 510(k) for substantial equivalence, De Novo for novel low-to-moderate risk, PMA for high-risk devices. Software documentation is critical for all pathways. Pre-submission consultation strongly recommended.
