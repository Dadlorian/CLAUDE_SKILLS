# Clinical Workflow Patterns

**Version**: 2.0.0
**Last Updated**: 2025-11-19
**Status**: Production Ready
**Standards Compliance**: FHIR R4, HL7 v2.5.1, HIPAA, Clinical Best Practices

---

## Executive Summary

This guide documents common clinical workflow patterns, integration points, and design best practices for healthcare systems. It provides reusable templates and architectural patterns for implementing typical clinical processes.

---

## 1. Patient Registration & Admission Workflow

### 1.1 Inpatient Admission Flow

**Standard Admission Process:**

```
┌─────────────────────────────────────────────────────────┐
│ Patient Arrives at ED/Admits Through Scheduling         │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────v──────────────────┐
      │ Check-In: Create/Locate Patient │
      │ - Patient matching (MRN search)  │
      │ - Duplicate detection            │
      │ - Verify demographics            │
      └──────────────┬──────────────────┘
                     │
      ┌──────────────v────────────────────┐
      │ Verify Insurance & Eligibility     │
      │ - Check active coverage            │
      │ - Verify pre-authorization         │
      │ - Obtain authorization if needed   │
      └──────────────┬────────────────────┘
                     │
      ┌──────────────v────────────────────┐
      │ Clinical Intake Assessment        │
      │ - Chief complaint                  │
      │ - Vital signs                      │
      │ - Allergies & reactions            │
      │ - Current medications              │
      │ - Active conditions                │
      │ - Social history                   │
      └──────────────┬────────────────────┘
                     │
      ┌──────────────v──────────────────┐
      │ Create Encounter Record          │
      │ - Assign location/bed             │
      │ - Set attending physician         │
      │ - Select admission type           │
      │ - Determine expected LOS          │
      └──────────────┬──────────────────┘
                     │
      ┌──────────────v──────────────────┐
      │ Send ADT^A01 Message             │
      │ (to other systems: pharmacy,     │
      │  lab, billing, etc.)             │
      └──────────────┬──────────────────┘
                     │
      ┌──────────────v──────────────────┐
      │ Patient Admitted to Ward         │
      │ - Room assignment complete       │
      │ - Orders processing begins       │
      └─────────────────────────────────┘
```

**Data Requirements at Admission:**

```
REQUIRED (Before Encounter Created):
  Patient:
    ✓ Legal name (surname, given, middle)
    ✓ Date of birth
    ✓ Gender/Sex at birth
    ✓ Contact phone number
    ✓ Address (if available)

  Encounter:
    ✓ Admission date/time
    ✓ Admission type (IP, OP, ED)
    ✓ Responsible facility
    ✓ Attending physician
    ✓ Admission source

  Insurance:
    ✓ Primary payer
    ✓ Policy number
    ✓ Group number
    ✓ Relationship to subscriber

CLINICAL (First 24 hours):
  ✓ Chief complaint
  ✓ Current medications (reconciliation)
  ✓ Allergies & reactions
  ✓ Active problems/diagnoses
  ✓ Reason for admission
  ✓ Preliminary diagnoses
  ✓ Vital signs (baseline)
  ✓ Physical exam (summary)

ADMINISTRATIVE (Within 48 hours):
  ✓ Advanced directives
  ✓ Emergency contact
  ✓ Preferred language
  ✓ Discharge planning considerations
  ✓ Case management needs
```

### 1.2 Outpatient Visit Registration

**Outpatient Workflow:**

```
Weeks Before Visit:
  └─ Appointment scheduled
     └─ Pre-visit questionnaire (online)
     └─ Insurance verification
     └─ Lab test orders (if needed)

Day of Visit:
  ├─ Check-in (kiosk or staff)
  │  └─ Verify demographics
  │  └─ Check insurance
  │  └─ Confirm medications
  │  └─ Update allergies
  │
  ├─ Waiting area (waiting time tracking)
  │  └─ Patient paging/notification
  │
  ├─ Rooming
  │  └─ Vital signs captured
  │  └─ Triage assessment
  │  └─ Medication reconciliation
  │
  ├─ Provider visit
  │  └─ History & exam
  │  └─ Assessments/diagnoses
  │  └─ Orders (meds, labs, imaging, etc.)
  │  └─ Patient education
  │
  ├─ Checkout
  │  └─ Copay collection
  │  └─ Discharge instructions
  │  └─ Schedule follow-up
  │  └─ Provide visit summary
  │
  └─ Post-Visit
     └─ Send after-visit summary to patient
     └─ Lab results notification
     └─ Prescription fulfillment
     └─ Telehealth follow-up (if needed)
```

---

## 2. Order Entry & Fulfillment Workflow

### 2.1 Medication Order Workflow

**Order Lifecycle:**

```
┌─ Physician Orders Medication ─────────────────┐
│                                               │
│  Required Elements:                           │
│  ✓ Patient (with allergies)                   │
│  ✓ Drug (RxNorm code)                         │
│  ✓ Dose (value + unit)                        │
│  ✓ Route (validated: PO, IV, IM, etc.)        │
│  ✓ Frequency (q6h, q12h, BID, etc.)           │
│  ✓ Indication (why prescribed)                │
│  ✓ Duration (start + stop date/condition)     │
│                                               │
└──────────────────┬──────────────────────────┘
                   │
     ┌─────────────v────────────────┐
     │ CDS Checking                  │
     │ ✓ Drug-drug interactions      │
     │ ✓ Allergy check               │
     │ ✓ Dose validation (renal)     │
     │ ✓ Duplicate therapy           │
     │ ✓ Therapeutic substitutes     │
     │ ✓ Preferred drug (formulary)  │
     └─────────────┬────────────────┘
                   │
        ┌──────────v───────────────┐
        │ Pharmacy Review           │
        │ (within 1 hour)           │
        │ ✓ Verify order            │
        │ ✓ Check interactions      │
        │ ✓ Compound if needed      │
        │ ✓ Verify availability     │
        └──────────┬────────────────┘
                   │
        ┌──────────v──────────────┐
        │ Dispense & Label        │
        │ (bar-code verified)      │
        │ ✓ Correct drug           │
        │ ✓ Correct dose/qty       │
        │ ✓ Correct patient        │
        │ ✓ Expiration date        │
        │ ✓ Storage instructions   │
        └──────────┬──────────────┘
                   │
        ┌──────────v──────────────┐
        │ Nurse Verification       │
        │ (at bedside - 5 rights)  │
        │ ✓ Right patient          │
        │ ✓ Right drug             │
        │ ✓ Right dose             │
        │ ✓ Right route            │
        │ ✓ Right time             │
        └──────────┬──────────────┘
                   │
        ┌──────────v─────────────┐
        │ Administration          │
        │ ✓ Give medication       │
        │ ✓ Document in MAR       │
        │ ✓ Monitor response      │
        │ ✓ Document any adverse  │
        └────────────────────────┘
```

**Medication Data Requirements:**

```
Minimum Required Fields (Order Entry):
  1. Patient identifier (MRN)
  2. Drug code (RxNorm)
  3. Dose (value + unit)
  4. Route
  5. Frequency
  6. Start date
  7. Stop date or PRN with frequency limit
  8. Indication/reason
  9. Special instructions
  10. Ordering provider

Recommended Fields:
  • Therapeutic duplication checking
  • Allergic reaction severity
  • Drug formulation (tablet, liquid, etc.)
  • Refill information (for outpatient)
  • Substitution preferences
  • Prior authorization status
```

### 2.2 Laboratory Order Workflow

**Lab Order Lifecycle:**

```
Order Entry:
  └─ Physician orders lab test
     └─ Select from order set or search
     └─ Verify patient fasting requirement
     └─ Verify specimen collection method
     └─ Verify critical result thresholds

Order Transmission:
  └─ Send order to lab via HL7 (ORM message)
  └─ Lab system receives order
  └─ Order queued for specimen collection

Specimen Collection:
  └─ Phlebotomy collects specimen
  └─ Label specimen (patient ID, time)
  └─ Bar-code label scanned
  └─ Specimen logged into lab system
  └─ Specimen placed in transport

Testing:
  └─ Specimen received in lab
  └─ Specimen verification (bar-code)
  └─ Test performed per protocol
  └─ Quality control checks pass
  └─ Results reviewed by tech
  └─ Results authorized by pathologist

Result Reporting:
  └─ Results entered in system
  └─ Critical results called to unit
  └─ Results sent via HL7 (ORU message)
  └─ Results appear in EHR
  └─ Notification sent to provider
  └─ Patient notification (if appropriate)

Follow-up:
  └─ Provider reviews result
  └─ Orders placed based on result (reflex testing)
  └─ Patient counseled if abnormal
  └─ Documented in clinical note
```

**Lab Data Quality Rules:**

```
Validation Rules:
  ✓ Specimen type matches test requirements
  ✓ Collection time within required window
  ✓ Patient identifier correct (no duplicates)
  ✓ Specimen ID tracked through testing
  ✓ Reference range appropriate for patient age/sex
  ✓ Unusual results reviewed by pathologist
  ✓ Critical values called to nursing
  ✓ Results documented within 24 hours
```

---

## 3. Medication Reconciliation Workflow

### 3.1 Standard Reconciliation Process

**Reconciliation at Key Transitions:**

```
Admission Reconciliation:
  Timeline: Within 24 hours of admission
  Goal: Identify all medications patient takes at home

  Steps:
    1. Interview patient/family about home medications
    2. Obtain medication list from:
       - Outpatient physician
       - Pharmacy records
       - Previous hospital discharge summaries
       - Patient's pill bottles (if available)
    3. Document each medication:
       - Name, dose, route, frequency
       - Last dose taken before admission
       - Why taking (indication)
       - Any recent changes
    4. Reconcile with current orders
       - Continue what appropriate
       - Discontinue/hold what contraindicated
       - Add needed medications
       - Document rationale for changes
    5. Verify with pharmacist
    6. Communicate changes to patient/family

Transfer Reconciliation:
  Timeline: Within 1 hour of transfer to new unit
  Goal: Ensure medication orders appropriate for new setting

  Steps:
    1. Verify all current orders for new unit
    2. Check for duplicate therapy
    3. Verify dose/frequency appropriate for new setting
    4. Add unit-specific PRN orders
    5. Communicate to nursing staff

Discharge Reconciliation:
  Timeline: Before discharge (24 hours prior if possible)
  Goal: Provide patient with accurate discharge medication list

  Steps:
    1. Compare discharge meds to admission list
    2. Note medications:
       - Continued
       - Discontinued
       - Changed (dose/frequency)
       - New (started during stay)
    3. Explain changes to patient
    4. Provide written list with instructions
    5. Send list to outpatient pharmacy
    6. Send list to primary care physician
```

### 3.2 Medication Reconciliation Technology

**Recommended Implementation:**

```
System Features:
  ✓ Automated medication list import (from pharmacy)
  ✓ Patient interview questionnaire (electronic)
  ✓ Allergy/interaction checking
  ✓ Therapeutic substitution suggestions
  ✓ Duplicate therapy detection
  ✓ Workflow routing (pharmacist review)
  ✓ Audit trail (all changes documented)
  ✓ Patient handout generation

Data Elements to Capture:
  • Drug name (generic preferred)
  • Dose (value + unit)
  • Route (PO, IV, topical, etc.)
  • Frequency
  • Indication
  • Allergies/reactions
  • Over-the-counter (OTC) medications
  • Supplements/herbal
  • Adherence status
  • Recent changes

Quality Metrics:
  • Reconciliation completion: >95% within 24h
  • Medication list accuracy: >98%
  • Discrepancy identification: >90%
  • Provider acceptance of recommendations: >85%
```

---

## 4. Clinical Documentation Patterns

### 4.1 Progress Note Structure

**Standard SOAP Format (Recommended):**

```
SOAP NOTE TEMPLATE

S - SUBJECTIVE (What patient reports)
  Chief Complaint:
    [1-2 sentence, in patient's words]

  History of Present Illness:
    Timeline, symptoms, severity, relieving factors, etc.

  Review of Systems:
    Pertinent positive/negative findings

  Past Medical History:
    Relevant chronic conditions

  Medications:
    Current medications (reconciled)

  Allergies:
    [Document severity level]

  Social History:
    Tobacco, alcohol, drugs; occupation; living situation

O - OBJECTIVE (What clinician observes/tests)
  Vital Signs:
    BP, HR, RR, Temp, O2 sat

  Physical Exam:
    Organized by system

  Labs/Imaging:
    Relevant test results

  Other Findings:
    Weight, mental status, etc.

A - ASSESSMENT (Diagnoses & clinical impression)
  Problem List:
    1. [Diagnosis with ICD-10 code]
    2. [Diagnosis with ICD-10 code]
    3. [Diagnosis with ICD-10 code]

  Clinical Impression:
    Brief summary of current status

  Differential Diagnosis:
    If appropriate for presentation

P - PLAN (Treatment plan going forward)
  For each diagnosis:
    Diagnostic Tests:
      [Orders with rationale]

    Medications:
      [New/changed meds with dose, route, frequency]

    Procedures:
      [Any procedures planned]

    Patient Education:
      [Topics discussed]

    Follow-up:
      [Timeline and method]

    Referrals:
      [Specialists, if needed]
```

**Structured Data Requirements:**

```
Mandatory Discrete Elements:
  • Assessment (diagnoses with codes)
  • Vital signs (structured fields)
  • Medications (structured orders)
  • Allergies (coded reactions)
  • Plan/Orders (discrete, not free text)

Optional Narrative:
  • HPI detail (clinical reasoning)
  • Physical exam findings (detail as needed)
  • Assessment rationale
  • Patient education discussion

Quality Rules:
  ✓ Allergy severity documented
  ✓ All orders have duration/indication
  ✓ Reconciliation documented
  ✓ Critical findings flagged
  ✓ Follow-up timeframe specified
```

---

## 5. Discharge Planning Workflow

### 5.1 Discharge Process

**Multi-Disciplinary Discharge Planning:**

```
Day of Admission:
  └─ Identify discharge planning needs
     └─ Anticipated length of stay
     └─ Functional status at discharge
     └─ Equipment/supplies needed
     └─ Skilled nursing facility vs. home

Throughout Stay:
  ├─ Interdisciplinary rounds
  │  └─ Update discharge plan
  │  └─ Adjust timeline as needed
  │
  └─ Patient/Family Education
     └─ Disease process
     └─ Medication management
     └─ Activity restrictions
     └─ Warning signs

24-48 Hours Before Discharge:
  ├─ Finalize discharge medications
  │  └─ Reconcile with admission list
  │  └─ Verify patient understanding
  │
  ├─ Arrange equipment/supplies
  │  └─ Oxygen, wound care, mobility aids
  │  └─ Verify insurance coverage
  │
  ├─ Arrange follow-up
  │  └─ Schedule appointments (PCP, specialist)
  │  └─ Send appointment letters to patient
  │
  └─ Arrange transportation/placement
     └─ Skilled nursing facility (if needed)
     └─ Home health services
     └─ Durable medical equipment

At Discharge:
  ├─ Provide discharge packet
  │  ├─ Hospital visit summary
  │  ├─ Medications list (current)
  │  ├─ Activity restrictions
  │  ├─ Diet recommendations
  │  ├─ Wound care instructions
  │  ├─ Medication instruction sheets
  │  ├─ Follow-up appointment letters
  │  └─ When to seek help/emergency contact
  │
  ├─ Clinical handoff
  │  ├─ Explain diagnosis & treatment
  │  ├─ Answer questions
  │  └─ Assess understanding (teach-back method)
  │
  ├─ Transmit records
  │  ├─ Send discharge summary to PCP (within 24h)
  │  ├─ Send medication list to pharmacy
  │  ├─ Order home health referral (if needed)
  │  └─ Send records to receiving facility (if SNF/rehab)
  │
  └─ System tasks
     ├─ Create discharge orders
     ├─ Send ADT^A03 (discharge) message
     ├─ Finalize billing
     └─ Queue chart for coding/abstraction

Post-Discharge:
  ├─ Follow-up call (24-48 hours)
  │  └─ Assess recovery
  │  └─ Answer questions
  │  └─ Reinforce medications
  │
  └─ Document in chart
     └─ Discharge summary
     └─ Final diagnosis codes
     └─ Procedures performed
```

**Discharge Summary Data Requirements:**

```
Essential Elements:
  • Hospital course summary (2-3 paragraphs)
  • Reason for admission
  • Hospital course details
  • Significant findings
  • Procedures/interventions performed
  • Disposition (home, SNF, etc.)
  • Follow-up plan

Diagnoses & Procedures:
  • Principal diagnosis (ICD-10)
  • Secondary diagnoses (ICD-10)
  • Principal procedure (ICD-10-PCS)
  • Secondary procedures (ICD-10-PCS)

Medications:
  • Current medications (with changes noted)
  • Discontinued medications
  • New medications started
  • Drug allergies/reactions

Activity & Diet:
  • Activity level
  • Weight-bearing status
  • Dietary restrictions
  • Wound care instructions

Follow-up:
  • PCP appointment scheduled (when)
  • Specialist appointments (when)
  • Lab/imaging follow-up
  • Home health services (if applicable)
  • Rehabilitation (if applicable)

Provider:
  • Attending physician
  • Discharge summary signer
  • Instructions read and understood by: [patient/caregiver]
```

---

## 6. Quality Measurement & Safety Patterns

### 6.1 Quality Indicator Tracking

**Common Clinical Quality Measures:**

```
Patient Safety Indicators:
  • Catheter-associated UTI rate (CAUTI)
    Target: < 1 per 1000 catheter days

  • Central line-associated bloodstream infection (CLABSI)
    Target: < 1 per 1000 line days

  • Hospital-acquired pneumonia (HAP)
    Target: < 5 per 1000 ventilator days

  • Medication error rate
    Target: < 0.1 errors per 1000 doses

  • Patient falls with injury
    Target: < 2 per 1000 patient days

Clinical Quality Indicators:
  • Aspirin use in MI patients
    Target: > 95%

  • Beta-blocker use post-MI
    Target: > 95%

  • Pneumococcal vaccination rate (65+)
    Target: > 90%

  • Influenza vaccination rate
    Target: > 95%

  • Sepsis bundle compliance
    Target: > 95%

Efficiency Indicators:
  • Average length of stay
  • Emergency department wait time (median)
  • OR turnover time
  • Radiology turnaround time
  • Lab result turnaround time

Patient Satisfaction:
  • HCAHPS scores (satisfaction survey)
  • Patient would recommend hospital: > 85%
  • Physician communication: > 80%
  • Staff responsiveness: > 75%
```

### 6.2 Safety Event Reporting & Learning

**Event Reporting Workflow:**

```
Event Occurs (No/Minor Harm):
  │
  └─ Staff member reports via secure system
     └─ Incident type selected
     └─ Narrative description
     └─ Location/date/time
     └─ People involved
     └─ Severity level
     └─ Contributing factors
     └─ Immediate actions taken

Manager Review:
  │
  ├─ Acknowledges report
  ├─ Initiates immediate corrective actions if needed
  ├─ Notifies relevant departments
  └─ Routes to quality department

Quality Department Analysis:
  │
  ├─ Trend analysis
  │  └─ Similar events in past 12 months?
  │
  ├─ Root cause analysis (RCA)
  │  └─ Why did this happen?
  │  └─ What contributed?
  │  └─ System vs. human factor?
  │
  ├─ Severity assessment
  │  └─ Potential for patient harm?
  │  └─ Regulatory reporting required?
  │
  └─ Action planning
     └─ Corrective actions identified
     └─ Responsibility assigned
     └─ Timeline set
     └─ Success metrics defined

Implementation & Monitoring:
  │
  ├─ Corrective actions implemented
  ├─ Staff training (if needed)
  ├─ Process changes monitored
  ├─ Effectiveness measured
  └─ Close-out when successful

Culture & Learning:
  │
  └─ Share lessons learned
     └─ Safety huddles
     └─ Educational sessions
     └─ Policy updates
     └─ Prevent similar events
```

---

## 7. Handoff & Care Transitions

### 7.1 Sign-Out Protocol (IPASS mnemonic)

**Effective Handoff Communication:**

```
I - Illness Severity
    "This is a stable/unstable patient..."
    Provides context for urgency

P - Patient Summary
    "Mr. Smith is a 72-year-old with pneumonia
     post-operative from hip fracture repair..."
    1-2 sentence overview

A - Assessment & Recommendation
    "I believe he has hospital-acquired pneumonia.
     I recommend broad-spectrum antibiotics pending
     cultures and CXR."
    Clinical impression & plan

S - Situation Awareness & Contingency
    "He's on supplemental oxygen. If he desaturates
     below 88%, notify me for possible ICU transfer.
     His daughter is at bedside and anxious about
     outcomes."
    Current status & what-if scenarios

S - Synthesis by Receiver
    "Let me confirm: You think he has HAP, you want
     me to start vanc/pip-tazo, monitor sat closely,
     and escalate if it drops below 88%?"
    Receiver confirms understanding
```

### 7.2 Structured Handoff Data

**Information to Communicate:**

```
Essential Clinical Information:
  • Patient name & ID
  • Admitting diagnosis
  • Active problems/diagnoses
  • Current medications (relevant to transfer)
  • Allergies/reactions
  • Precautions (infection control, fall risk)
  • Current IV/device status
  • Recent abnormal results
  • Pending test results

Situation & Contingency:
  • Current clinical status (stable/unstable)
  • Expected trajectory
  • Monitoring requirements
  • When to contact on-call provider
  • Anticipated issues

Administrative:
  • Insurance status
  • Discharge planning needs
  • Family contact/communication preferences
  • Legal issues (guardianship, etc.)

Documentation:
  • Handoff documented in system
  • Chart reviewed by receiver
  • Questions answered before handoff ends
  • Contact information for questions
```

---

## Appendix: Workflow Optimization Tips

**Best Practices for Workflow Design:**

```
1. Eliminate Non-Value Steps
   ✓ Question every step
   ✓ Remove redundancy
   ✓ Simplify complexity
   ✓ Measure before/after

2. Parallel Processing
   ✓ Start tests while awaiting others
   ✓ Patient education while waiting
   ✓ Insurance verification before arrival

3. Standardization
   ✓ Reduce variation
   ✓ Use templates
   ✓ Order sets for common presentations
   ✓ Protocols for routine processes

4. Automation
   ✓ Automate data capture (vital signs)
   ✓ Automate notifications (critical results)
   ✓ Automate routine communications
   ✓ Exception management (alert on outliers)

5. Team Training
   ✓ Clear role definitions
   ✓ Cross-training for flexibility
   ✓ Regular drills/simulations
   ✓ Continuous improvement feedback

6. Technology Support
   ✓ Match EHR to workflow (not vice versa)
   ✓ Minimize clicks/steps
   ✓ Mobile access when needed
   ✓ Real-time information display

7. Measurement & Feedback
   ✓ Track cycle time
   ✓ Monitor quality metrics
   ✓ Gather clinician feedback
   ✓ Adjust based on data
```

---

**Contact**: Clinical Workflow Design & Process Improvement
**Last Reviewed**: 2025-11-19
**Next Review**: 2026-05-19
