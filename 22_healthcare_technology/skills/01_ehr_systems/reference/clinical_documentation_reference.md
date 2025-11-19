# Clinical Documentation Reference

## Overview

Clinical documentation is the cornerstone of patient care, capturing clinical findings, assessments, plans, and outcomes. This reference covers documentation types, structures, templates, and best practices for EHR systems.

## Note Types and Categories

### Progress Notes
Daily documentation of patient status during hospitalization or follow-up visits.

**Structure**:
```
Subjective (S):
├── Patient's chief complaint
├── Patient's description of symptoms
├── Review of systems (pertinent)
└── Patient-reported changes since last visit

Objective (O):
├── Vital signs
├── Physical examination findings
├── Laboratory results
├── Imaging results
└── Other objective data

Assessment (A):
├── Current diagnoses
├── Status of each problem
├── Interpretation of findings
└── Clinical judgment

Plan (P):
├── Diagnostic plan
├── Therapeutic plan
├── Patient education
├── Follow-up plans
└── Disposition
```

**Example Progress Note**:
```
Date: 11/19/2023 10:30 AM
Service: Internal Medicine
Attending: Dr. John Smith

SUBJECTIVE:
68 year-old male with community-acquired pneumonia, hospital day #2.
Patient reports feeling better today. Fever improved, less cough.
Denies shortness of breath at rest. Tolerating PO intake.

OBJECTIVE:
Vitals: T 99.1°F, HR 82, BP 128/76, RR 16, SpO2 96% on room air
General: Alert, oriented x3, in no acute distress
HEENT: Mucous membranes moist
Lungs: Decreased breath sounds right base, occasional crackles
Heart: RRR, no murmurs
Abdomen: Soft, non-tender
Extremities: No edema

Labs (today):
WBC 10.2 (down from 14.5 on admit)
Cr 0.9 (baseline)

ASSESSMENT:
1. Community-acquired pneumonia - improving
2. Type 2 diabetes - controlled
3. Hypertension - controlled

PLAN:
1. Pneumonia: Continue ceftriaxone + azithromycin, day 3 of 7
   Monitor clinical response
   CXR today to assess resolution
2. DM: Continue home metformin, monitor BG
3. HTN: Continue home lisinopril
4. Disposition: Likely discharge tomorrow if continued improvement

Discussed with patient. All questions answered.

[Electronic Signature]
Dr. John Smith, MD
Attending Physician
Internal Medicine
```

### History and Physical (H&P)
Comprehensive initial evaluation document.

**Required Components**:
```
1. Chief Complaint (CC)
   └── Brief statement of reason for visit

2. History of Present Illness (HPI)
   ├── Onset
   ├── Location
   ├── Duration
   ├── Character
   ├── Aggravating factors
   ├── Relieving factors
   ├── Timing
   └── Severity (OLDCARTS)

3. Past Medical History (PMH)
   ├── Chronic medical conditions
   ├── Prior hospitalizations
   ├── Prior surgeries
   └── Major illnesses

4. Medications
   ├── Current medications (name, dose, frequency)
   ├── Over-the-counter medications
   ├── Herbal supplements
   └── Medication allergies

5. Allergies
   ├── Drug allergies
   ├── Reactions experienced
   └── Food/environmental allergies

6. Family History (FH)
   ├── First-degree relatives
   ├── Hereditary conditions
   └── Genetic disorders

7. Social History (SH)
   ├── Tobacco use
   ├── Alcohol use
   ├── Illicit drug use
   ├── Occupation
   ├── Living situation
   └── Sexual history (if pertinent)

8. Review of Systems (ROS)
   ├── Constitutional
   ├── HEENT
   ├── Cardiovascular
   ├── Respiratory
   ├── Gastrointestinal
   ├── Genitourinary
   ├── Musculoskeletal
   ├── Skin
   ├── Neurological
   ├── Psychiatric
   ├── Endocrine
   ├── Hematologic/Lymphatic
   └── Allergic/Immunologic

9. Physical Examination
   ├── Vital signs
   ├── General appearance
   ├── HEENT
   ├── Neck
   ├── Cardiovascular
   ├── Respiratory
   ├── Abdomen
   ├── Genitourinary (if indicated)
   ├── Rectal (if indicated)
   ├── Musculoskeletal
   ├── Neurological
   ├── Skin
   └── Psychiatric

10. Assessment and Plan
    ├── Problem list
    ├── Differential diagnosis
    ├── Diagnostic studies ordered
    ├── Treatment plan
    └── Patient education
```

### Discharge Summary
Comprehensive summary at end of hospitalization.

**Required Elements**:
```
1. Patient Demographics
   └── Name, MRN, DOB, Admission/Discharge dates

2. Admission Diagnosis
   └── Reason for hospitalization

3. Discharge Diagnosis
   ├── Principal diagnosis
   └── Secondary diagnoses

4. Hospital Course
   ├── Major events during hospitalization
   ├── Procedures performed
   ├── Consultants involved
   ├── Complications
   └── Response to treatment

5. Discharge Medications
   ├── Complete medication list
   ├── New medications highlighted
   ├── Discontinued medications noted
   └── Medication reconciliation

6. Discharge Condition
   └── Patient's status at discharge

7. Discharge Disposition
   ├── Home
   ├── Skilled nursing facility
   ├── Rehabilitation facility
   └── Other

8. Discharge Instructions
   ├── Activity restrictions
   ├── Dietary restrictions
   ├── Wound care
   ├── Equipment needs
   └── Warning signs to watch for

9. Follow-up Plans
   ├── Follow-up appointments
   ├── Pending laboratory studies
   ├── Pending test results
   └── Specialist referrals

10. Prognosis
    └── Expected outcome
```

### Operative Note
Documentation of surgical procedures.

**Required Components**:
```
1. Preoperative Diagnosis
2. Postoperative Diagnosis
3. Procedure(s) Performed
4. Surgeon(s)
5. Assistant(s)
6. Anesthesia Type
7. Anesthesiologist
8. Findings
9. Indications for Procedure
10. Description of Procedure (detailed narrative)
11. Estimated Blood Loss (EBL)
12. Specimens Removed
13. Drains/Tubes Placed
14. Complications
15. Patient Condition
16. Disposition (to PACU, ICU, floor)
```

### Consultation Note
Documentation by consulting specialist.

**Structure**:
```
1. Reason for Consultation
   └── Specific question to be answered

2. Consultant's HPI
   └── Relevant history from consultant's perspective

3. Pertinent PMH/PSH/Meds/Allergies

4. Focused Review of Systems

5. Focused Physical Examination
   └── Pertinent to consultation question

6. Review of Records
   ├── Labs reviewed
   ├── Imaging reviewed
   └── Prior notes reviewed

7. Consultant's Assessment
   └── Specialist's interpretation

8. Recommendations
   ├── Diagnostic recommendations
   ├── Treatment recommendations
   └── Follow-up recommendations

9. Signature and credentials
```

### Procedure Note
Documentation of bedside or minor procedures.

**Required Elements**:
```
1. Indication for Procedure
2. Consent
   └── Informed consent obtained, risks/benefits discussed
3. Time-Out Performed
   └── Patient identity, procedure, site verified
4. Patient Preparation
   ├── Positioning
   └── Sterile technique
5. Anesthesia/Sedation
6. Procedure Description
   ├── Technique used
   ├── Equipment used
   └── Step-by-step description
7. Findings
8. Specimens Obtained
9. Complications
10. Estimated Blood Loss
11. Patient Tolerance
12. Post-Procedure Plan
```

## Documentation Templates

### Structured Data Elements

**Vital Signs Template**:
```json
{
  "templateName": "Vital Signs",
  "templateType": "flowsheet",
  "dataElements": [
    {
      "elementName": "Temperature",
      "dataType": "numeric",
      "units": ["F", "C"],
      "normalRange": {"min": 97.0, "max": 99.0},
      "criticalLow": 95.0,
      "criticalHigh": 104.0,
      "required": true
    },
    {
      "elementName": "Heart Rate",
      "dataType": "numeric",
      "units": ["bpm"],
      "normalRange": {"min": 60, "max": 100},
      "criticalLow": 40,
      "criticalHigh": 140,
      "required": true
    },
    {
      "elementName": "Blood Pressure Systolic",
      "dataType": "numeric",
      "units": ["mmHg"],
      "normalRange": {"min": 90, "max": 120},
      "criticalLow": 70,
      "criticalHigh": 180,
      "required": true
    },
    {
      "elementName": "Blood Pressure Diastolic",
      "dataType": "numeric",
      "units": ["mmHg"],
      "normalRange": {"min": 60, "max": 80},
      "criticalLow": 40,
      "criticalHigh": 110,
      "required": true
    },
    {
      "elementName": "Respiratory Rate",
      "dataType": "numeric",
      "units": ["breaths/min"],
      "normalRange": {"min": 12, "max": 20},
      "criticalLow": 8,
      "criticalHigh": 30,
      "required": true
    },
    {
      "elementName": "Oxygen Saturation",
      "dataType": "numeric",
      "units": ["%"],
      "normalRange": {"min": 95, "max": 100},
      "criticalLow": 88,
      "required": true
    },
    {
      "elementName": "Pain Score",
      "dataType": "numeric",
      "scale": "0-10",
      "required": false
    }
  ]
}
```

### Smart Phrases/Text Macros

Common shortcuts for efficient documentation:

```
.normal-pe (Normal Physical Exam):
───────────────────────────────────
GENERAL: Alert, oriented x3, NAD
HEENT: NCAT, PERRLA, EOMI, MMM, oropharynx clear
NECK: Supple, no LAD, no JVD
CARDIOVASCULAR: RRR, normal S1/S2, no m/r/g
RESPIRATORY: CTAB, no w/r/r
ABDOMEN: Soft, NT/ND, +BS, no HSM
EXTREMITIES: No c/c/e, pulses 2+ throughout
NEUROLOGICAL: CN II-XII intact, strength 5/5 all extremities, sensation intact
SKIN: Warm, dry, no rashes

.ros-negative (Negative Review of Systems):
───────────────────────────────────
10-point ROS reviewed and negative except as documented in HPI.
Denies fever, chills, night sweats, unintentional weight loss/gain.
Denies chest pain, palpitations, dyspnea, orthopnea, PND, edema.
Denies cough, hemoptysis, wheezing.
Denies nausea, vomiting, diarrhea, constipation, abdominal pain, melena, hematochezia.
Denies dysuria, hematuria, frequency, urgency.
Denies weakness, numbness, tingling, dizziness, headache, vision changes.

.informed-consent (Informed Consent Statement):
───────────────────────────────────
Informed consent obtained after discussion with patient (and/or family)
regarding indication, risks, benefits, and alternatives to the proposed
procedure. Patient/family had opportunity to ask questions. All questions
answered. Patient/family verbalizes understanding and agrees to proceed.
```

### Problem-Oriented Templates

**Diabetes Follow-Up Template**:
```
DIABETES MELLITUS TYPE 2 - FOLLOW-UP

GLYCEMIC CONTROL:
□ Last A1C: _____ (date: _____)
□ Home glucose monitoring:
  Fasting: _____ mg/dL
  Pre-meal: _____ mg/dL
  Bedtime: _____ mg/dL
□ Hypoglycemic episodes: Yes / No
  If yes, frequency: _____

MEDICATIONS:
Current regimen:
□ Metformin: _____ mg _____
□ Glipizide: _____ mg _____
□ Insulin: _____ units _____
□ Medication adherence: Good / Fair / Poor

COMPLICATIONS SCREENING:
□ Last eye exam: _____ (Retinopathy: Y/N)
□ Last foot exam: Today
  Monofilament: Normal / Abnormal
  Pulses: Present / Diminished
  Ulcers: Yes / No
□ Microalbuminuria screening: _____ (date: _____)
□ Lipid panel: _____ (date: _____)

ASSESSMENT:
Type 2 diabetes, [controlled/uncontrolled]
Current A1C: _____ (goal: <7%)

PLAN:
□ Continue current medications
□ Adjust medications: _____
□ Order A1C (if >3 months since last)
□ Order microalbuminuria screening (if >1 year)
□ Referral to ophthalmology (if >1 year)
□ Referral to podiatry (if foot abnormalities)
□ Diabetes education referral
□ Nutrition referral
□ Follow-up: 3 months / 6 months / other: _____
```

## Documentation Standards

### E/M (Evaluation and Management) Documentation

**Key Components**:
1. **History** (Problem Focused, Expanded, Detailed, Comprehensive)
2. **Examination** (Problem Focused, Expanded, Detailed, Comprehensive)
3. **Medical Decision Making** (Straightforward, Low, Moderate, High)

**2021 E/M Guidelines** (Time-Based or MDM-Based):

```
Office/Outpatient Visit Levels (99202-99215):

99211: Minimal (may not require physician)
99212: Straightforward MDM or 10-19 minutes
99213: Low complexity MDM or 20-29 minutes
99214: Moderate complexity MDM or 30-39 minutes
99215: High complexity MDM or 40-54 minutes

Medical Decision Making (MDM) Components:
1. Number and complexity of problems addressed
2. Amount and/or complexity of data reviewed/analyzed
3. Risk of complications, morbidity, mortality
```

### SOAP Note Format

```
S (Subjective):
├── Chief complaint
├── HPI elements
│   ├── Location
│   ├── Quality
│   ├── Severity
│   ├── Duration
│   ├── Timing
│   ├── Context
│   ├── Modifying factors
│   └── Associated signs/symptoms
└── Pertinent ROS

O (Objective):
├── Vital signs
├── Physical examination
├── Laboratory data
├── Imaging results
└── Other objective findings

A (Assessment):
├── Problem list
├── Differential diagnoses
└── Clinical impression

P (Plan):
├── Diagnostics ordered
├── Treatments prescribed
├── Referrals made
├── Patient education provided
└── Follow-up arranged
```

## Clinical Documentation Improvement (CDI)

### Query Process

**Indications for CDI Query**:
```
1. Clinical indicators without corresponding diagnosis
   Example: Troponin 2.5, no myocardial infarction documented

2. Conflicting documentation
   Example: "CHF exacerbation" vs "volume overload"

3. Incomplete documentation
   Example: "Pneumonia" without organism or type

4. Unspecified diagnoses
   Example: "Heart failure" without systolic/diastolic/combined

5. Missing severity/stage
   Example: "CKD" without stage
```

**Query Format**:
```
CLINICAL DOCUMENTATION QUERY

Patient: John Doe, MRN: 123456
Date of Service: 11/19/2023
Provider: Dr. Smith

Clinical Indicators:
• Creatinine 3.2 mg/dL (baseline 1.0)
• BUN 65 mg/dL
• Urinalysis: protein 3+
• Patient on dialysis during admission

Documentation Review:
Progress notes document "renal failure" without further specification

Query:
Based on the clinical indicators above, please clarify the most accurate
diagnosis:

□ Acute kidney injury (AKI)
□ Chronic kidney disease (CKD), Stage ___
□ Acute on chronic kidney disease
□ End-stage renal disease (ESRD)
□ Other: ___________
□ Clinically undetermined

If CKD is selected, please document stage (1-5).

This is not a leading query. Please document based on your clinical judgment.

Response: _____________________
Signature: _____________________ Date: _______
```

### Specificity Requirements

**ICD-10-CM Specificity Examples**:
```
Unspecified → Specified

Heart failure → Systolic heart failure, acute
Diabetes → Type 2 diabetes with diabetic nephropathy
Pneumonia → Community-acquired pneumonia due to Streptococcus pneumoniae
CKD → CKD, stage 3b (eGFR 30-44)
Stroke → Cerebral infarction due to thrombosis of left middle cerebral artery
```

## Documentation Quality Metrics

### Key Quality Indicators

```
1. Completeness
   ├── All required elements present
   ├── Adequate detail provided
   └── Supporting documentation attached

2. Accuracy
   ├── Correct clinical information
   ├── Accurate problem list
   └── Medication reconciliation current

3. Timeliness
   ├── H&P within 24 hours of admission
   ├── Progress notes daily
   ├── Discharge summary within 30 days
   └── Operative note immediately post-op

4. Legibility
   ├── Clear, professional language
   ├── Appropriate medical terminology
   └── Minimal use of abbreviations

5. Authentication
   ├── Electronic signature present
   ├── Credentials displayed
   ├── Date/time stamp
   └── Amendment process followed

6. Compliance
   ├── Regulatory requirements met
   ├── Billing documentation adequate
   └── Legal standards satisfied
```

### Prohibited Abbreviations

The Joint Commission "Do Not Use" List:
```
❌ U or u → Write "unit"
❌ IU → Write "international unit"
❌ Q.D., QD, q.d., qd → Write "daily"
❌ Q.O.D., QOD, q.o.d., qod → Write "every other day"
❌ Trailing zero (1.0 mg) → Write "1 mg"
❌ Lack of leading zero (.5 mg) → Write "0.5 mg"
❌ MS, MSO4, MgSO4 → Write "morphine sulfate" or "magnesium sulfate"
```

## Copy-Forward and Auto-Population Risks

### Safe Copy-Forward Practices

```
Acceptable to Copy-Forward:
✓ Past medical history
✓ Past surgical history
✓ Family history
✓ Social history (if unchanged)
✓ Medication list (with verification)
✓ Allergy list (with verification)

Requires Update Each Time:
✗ Chief complaint
✗ History of present illness
✗ Review of systems
✗ Physical examination
✗ Assessment
✗ Plan
✗ Vital signs
✗ Laboratory values
```

### Documentation Best Practices

```
1. Date and time stamp all entries
2. Use "Amended" or "Addendum" for corrections
3. Never delete or alter original documentation
4. Include your rationale for clinical decisions
5. Document patient education and understanding
6. Document informed consent discussions
7. Document clinical reasoning for test ordering
8. Document why orders were not followed
9. Avoid disparaging comments about other providers
10. Use objective language, not judgmental
```

## Voice Recognition and AI-Assisted Documentation

### Speech-to-Text Integration

**Workflow**:
```
1. Provider speaks narrative
   ↓
2. Speech recognition engine transcribes
   ↓
3. Real-time display of text
   ↓
4. Provider reviews and edits
   ↓
5. Structured data extraction (optional)
   ↓
6. Sign and submit
```

**Accuracy Optimization**:
- Train voice profile
- Use consistent vocabulary
- Speak clearly and at moderate pace
- Use punctuation commands ("period", "comma", "new paragraph")
- Review and edit before signing

### AI-Assisted Documentation

**Ambient Clinical Intelligence**:
```
Patient-Provider Conversation
         ↓
   AI Listening Service
         ↓
   Automatic Transcription
         ↓
   Note Generation (Draft)
         ↓
   Provider Review & Edit
         ↓
   Final Signed Note
```

**AI-Generated Content Should Include**:
- Disclosure that AI was used
- Provider verification and editing
- Final provider accountability

## Regulatory Requirements

### Medicare Documentation Requirements
- Medical necessity documented
- Frequency and duration of treatment
- Progress toward goals
- Response to treatment
- Barriers to treatment

### Meaningful Use/Promoting Interoperability
- Use of certified EHR technology
- CPOE for medications
- E-prescribing
- Summary of care record exchange
- Patient electronic access to health information
- Clinical decision support
- Immunization registry reporting
- Syndromic surveillance reporting

### HIPAA Documentation Requirements
- Minimum necessary standard
- De-identify when appropriate
- Secure messaging for PHI
- Audit trails maintained
- Access controls enforced

## References

- **AMA E/M Documentation**: https://www.ama-assn.org/
- **CMS Documentation Guidelines**: https://www.cms.gov/
- **Joint Commission Standards**: https://www.jointcommission.org/
- **AHIMA Best Practices**: https://ahima.org/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
