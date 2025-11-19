# Protected Health Information (PHI) Definition Reference

## Legal Definition

**Protected Health Information (PHI)** is individually identifiable health information that is transmitted or maintained in any form or medium (electronic, paper, or oral) by a covered entity or business associate.

**Regulatory Citation:** 45 CFR §160.103

## Components of PHI

For information to be considered PHI, it must meet ALL of the following criteria:

### 1. Individually Identifiable

Information that:
- Identifies the individual, OR
- Could reasonably be used to identify the individual

### 2. Health Information

Information that relates to:
- **Past, present, or future physical or mental health or condition** of an individual
- **Provision of healthcare** to an individual
- **Past, present, or future payment** for the provision of healthcare to an individual

### 3. Created or Received By

- Healthcare provider
- Health plan
- Healthcare clearinghouse
- Business associate
- Employer (in certain contexts)

### 4. Medium

Transmitted or maintained in ANY form:
- Electronic (ePHI)
- Paper
- Oral

## 18 HIPAA Identifiers

PHI includes health information with ANY of these identifiers:

### Direct Identifiers

1. **Names**
   - Full name
   - Last name and initial(s)
   - Maiden name
   - Alias

2. **Geographic Subdivisions Smaller Than State**
   - Street address (including P.O. Box)
   - City
   - County
   - Precinct
   - ZIP code (except first 3 digits if geographic unit contains >20,000 people)
   - ZIP+4
   - Geographic coordinates
   - Other geographic codes

3. **Dates Directly Related to Individual**
   - Date of birth
   - Admission date
   - Discharge date
   - Date of death
   - Service dates
   - All ages over 89 (aggregate as 90+)
   - Dates of procedures
   - **Exception:** Year alone is permitted

4. **Telephone Numbers**
   - Home phone
   - Cell phone
   - Work phone
   - Fax numbers associated with individual

5. **Fax Numbers**
   - Any fax number associated with individual

6. **Email Addresses**
   - Personal email
   - Work email
   - Any email that identifies individual

7. **Social Security Numbers**
   - Full SSN
   - Partial SSN
   - Last 4 digits (when combined with other identifiers)

8. **Medical Record Numbers**
   - Hospital medical record number
   - Clinic patient ID
   - Health system identifier

9. **Health Plan Beneficiary Numbers**
   - Insurance member ID
   - Policy number
   - Subscriber number
   - Medicare/Medicaid ID

10. **Account Numbers**
    - Patient account number
    - Billing account number
    - Financial account number

11. **Certificate/License Numbers**
    - Driver's license number
    - Professional license
    - Birth certificate number
    - Death certificate number

12. **Vehicle Identifiers and Serial Numbers**
    - License plate number
    - VIN (Vehicle Identification Number)
    - Registration number

13. **Device Identifiers and Serial Numbers**
    - Pacemaker serial number
    - Prosthetic device serial number
    - Implanted device identifier
    - Medical equipment serial numbers

14. **Web URLs**
    - Personal website URLs
    - Social media profile URLs
    - Any URL identifying individual

15. **IP Addresses**
    - IPv4 addresses
    - IPv6 addresses
    - Static or dynamic IPs when identifiable

16. **Biometric Identifiers**
    - Fingerprints
    - Voiceprints
    - Retinal/iris scans
    - Facial recognition data
    - DNA
    - Dental records pattern
    - Any unique physical characteristic

17. **Full-Face Photographs**
    - Photos showing full face
    - Comparable images
    - Distinguishing features
    - Tattoos if identifiable

18. **Any Other Unique Identifying Number, Characteristic, or Code**
    - Unique employee number
    - Unique study/research number (if linkable to individual)
    - Badge number
    - Any other unique identifier

**Note:** Generic codes (e.g., CPT codes, ICD-10 codes) are not identifiers unless they uniquely identify an individual.

## What is NOT PHI

### 1. De-Identified Health Information

Information where all 18 identifiers have been removed AND:
- No actual knowledge that remaining information could identify individual
- No reasonable basis to believe information could identify individual

**Two Methods:**
- **Safe Harbor Method:** Remove all 18 identifiers
- **Expert Determination Method:** Statistical/scientific analysis by qualified expert

### 2. Employment Records

Health information in employment records held by covered entity in its role as employer.

**Examples:**
- Workers' compensation records held by employer
- Employee health records in HR files
- FMLA medical certification (held by employer)

**Note:** Same records held by healthcare provider treating employee ARE PHI.

### 3. Education Records Under FERPA

Health information covered by Family Educational Rights and Privacy Act (FERPA).

**Examples:**
- Student health records at K-12 schools
- College student health records at student health centers covered by FERPA
- School immunization records

**Exception:** If healthcare provider is not part of school or university, records are PHI.

### 4. De-Identified Data Sets

Health information stripped of identifiers for research, public health, or other purposes.

**Requirements:**
- All 18 identifiers removed
- No code or key that can re-identify
- Documented de-identification process

### 5. Limited Data Set

Partially de-identified information with Data Use Agreement.

**May Retain:**
- City, state, ZIP code
- Dates (including date of birth)
- Ages (including >89)

**Must Remove:**
- Names
- Street addresses (except city/state/ZIP)
- Telephone/fax numbers
- Email addresses
- SSNs
- Medical record numbers
- Account numbers
- Certificate/license numbers
- Vehicle/device identifiers
- URLs
- IP addresses
- Biometric identifiers
- Photos

**Required:** Data Use Agreement specifying permitted uses, prohibiting re-identification, and requiring safeguards.

## ePHI vs. PHI

### ePHI (Electronic PHI)

PHI that is:
- Transmitted electronically
- Maintained in electronic media
- Subject to HIPAA Security Rule

**Examples:**
- Electronic health records (EHRs)
- Electronic lab results
- Digital imaging (X-rays, MRIs in PACS)
- Emails containing PHI
- Databases with patient information
- PHI on smartphones/tablets
- Scanned documents
- Text messages with PHI
- Faxes transmitted electronically
- Video/audio recordings

**Security Rule Applies:** Administrative, physical, and technical safeguards required.

### Paper PHI

PHI in physical form:
- Medical charts
- Prescription pads
- Printed lab results
- Paper consent forms
- Appointment books/schedules
- Insurance claim forms
- Billing statements

**Privacy Rule Applies:** Physical safeguards, minimum necessary, proper disposal.

### Oral PHI

PHI communicated verbally:
- Doctor-patient conversations
- Phone discussions about patient care
- Conversations at nurses' stations
- Hallway conversations
- Messages left on voicemail

**Privacy Rule Applies:** Reasonable safeguards to limit incidental disclosures.

## Common PHI Identification Scenarios

### Healthcare Context

**Clearly PHI:**
- Patient medical record: Name + diagnosis
- Lab result: Patient name + test results
- Prescription: Patient name + medication
- Appointment schedule: Patient name + date/time
- Billing statement: Patient name + services + charges
- Insurance claim: Patient ID + diagnosis + procedures

**May Be PHI (Context Dependent):**
- Patient name alone (if in healthcare context, typically PHI)
- Appointment list without names (if includes identifiable info)
- Facility visitor log (if indicates healthcare relationship)

**Not PHI:**
- Aggregate statistics without identifiers
- De-identified research data
- Clinical practice guidelines
- General health information (not linked to individual)

### Research Context

**PHI:**
- Study data with names/MRNs
- Coded data with key linking to individuals
- Research database with any 18 identifiers

**Limited Data Set:**
- Research data with dates and ZIP codes
- Requires Data Use Agreement
- More identifiers than fully de-identified

**De-Identified:**
- No 18 identifiers
- No re-identification possible
- May be used without authorization

### Business Associate Context

**PHI Held by BA:**
- Medical billing records
- Claims processing data
- IT audit logs showing PHI access
- Cloud storage of patient records
- Shredding company receipts listing patient names

**Transformation:**
When BA removes identifiers for analytics, becomes de-identified (not PHI).

## Special Categories of PHI

### Psychotherapy Notes

**Definition:** Notes by mental health professional documenting/analyzing counseling session.

**Characteristics:**
- Kept separate from medical record
- Only for provider's use
- Not shared with other providers

**Special Protection:**
- Require separate authorization (even from general medical records authorization)
- Not required to be disclosed to patient
- Not subject to accounting of disclosures

**Not Psychotherapy Notes:**
- Medication prescription and monitoring
- Counseling session start/stop times
- Modalities and frequencies of treatment
- Results of clinical tests
- Summary of diagnosis, functional status, treatment plan, symptoms, prognosis
- These are regular PHI

### Substance Abuse Treatment Records (42 CFR Part 2)

**More Restrictive Than HIPAA:**
- Specific federal regulations for substance abuse treatment
- Stricter consent requirements
- Limited disclosure permissions
- Cannot generally disclose even for TPO without consent

**Applicability:**
- Federally assisted substance abuse programs
- Includes methadone clinics, alcohol treatment centers

**Key Difference:**
- HIPAA allows TPO disclosures without authorization
- Part 2 generally requires patient consent

### HIV/AIDS Information

**State Laws:**
- Many states have specific HIV/AIDS confidentiality laws
- Often more restrictive than HIPAA
- May require specific authorization
- May restrict who can access

**HIPAA:**
- HIV status is PHI
- Same protections as other PHI
- State laws may be more stringent

### Genetic Information

**Genetic Information Nondiscrimination Act (GINA):**
- Prohibits health insurers from using genetic information for underwriting
- Prohibits employment discrimination based on genetic information

**HIPAA Genetic Information:**
- Genetic information is health information
- Treated as PHI
- Health plans cannot use for underwriting purposes

### Mental Health Information

**State Laws:**
- Many states have enhanced protections for mental health records
- May require specific authorization for disclosure
- May limit access by certain parties

**HIPAA:**
- Mental health information is PHI
- Same general protections
- Psychotherapy notes have additional protection
- State laws may require additional safeguards

## Determining PHI Status - Decision Tree

**Question 1:** Is it health information?
- Does it relate to individual's health condition, healthcare provision, or healthcare payment?
- **If NO:** Not PHI
- **If YES:** Continue

**Question 2:** Does it identify an individual or could it be used to identify?
- Does it contain any of 18 identifiers?
- Could reasonable person use it to identify individual?
- **If NO:** Not PHI (likely de-identified)
- **If YES:** Continue

**Question 3:** Is it created/received by covered entity or business associate?
- Healthcare provider, health plan, clearinghouse, or their BA?
- **If NO:** Not subject to HIPAA (may be subject to other laws)
- **If YES:** Continue

**Question 4:** Is it excluded?
- Employment record?
- Education record under FERPA?
- Other exclusion?
- **If YES:** Not HIPAA PHI
- **If NO:** It is PHI

**Question 5:** What form?
- Electronic? → ePHI (Security Rule applies)
- Paper? → PHI (Privacy Rule applies)
- Oral? → PHI (Privacy Rule applies)

## Practical PHI Examples

### Clearly PHI
1. Electronic medical record with patient name and diagnosis
2. Lab test result with patient MRN and values
3. Prescription with patient name and medication
4. X-ray with patient name
5. Patient bill with name and charges
6. Appointment schedule with patient names
7. Insurance claim with member ID and services
8. Phone message about patient's test results
9. Email discussing patient's treatment
10. Patient sign-in sheet at clinic

### Borderline/Context Dependent
1. First name only in healthcare setting (likely PHI with context)
2. De-identified research data (not PHI if properly de-identified)
3. Aggregate statistics (not PHI)
4. Appointment reminder without PHI (depends on message content)
5. Facility directory listing (PHI, but permitted use)

### Not PHI
1. Medical journal article (no specific patient identification)
2. Clinical practice guideline
3. De-identified health statistics
4. Employee's workers' comp claim held by employer
5. Student health record under FERPA

## Best Practices for PHI Identification

1. **Train Workforce**
   - Regular training on PHI identification
   - Examples specific to organization
   - Role-specific training

2. **Label PHI**
   - Mark documents containing PHI
   - Identify systems containing ePHI
   - Clear labeling for proper handling

3. **Inventory PHI**
   - Catalog all PHI locations
   - Document data flows
   - Identify all 18 identifiers in use

4. **Minimize PHI**
   - Collect only necessary identifiers
   - De-identify when possible
   - Use limited data sets for research

5. **Assess New Systems**
   - Determine if new system will contain PHI
   - Apply appropriate safeguards
   - Update inventory

6. **Question Borderline Cases**
   - When unsure, treat as PHI
   - Consult privacy official
   - Document decision

7. **Consider State Laws**
   - Review state-specific requirements
   - Apply most stringent standard
   - Stay current with changes

## Regulatory Citations

- 45 CFR §160.103 - Definitions
- 45 CFR §164.501 - Definitions (Privacy Rule)
- 45 CFR §164.514 - De-identification standards
- 45 CFR §164.514(e) - Limited data set

## Additional Resources

- HHS guidance on de-identification
- Safe Harbor method checklist
- Limited data set template agreements
- PHI identification training materials
