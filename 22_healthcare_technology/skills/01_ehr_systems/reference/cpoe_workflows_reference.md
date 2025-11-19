# CPOE (Computerized Provider Order Entry) Workflows Reference

## Overview

Computerized Provider Order Entry (CPOE) is a critical EHR system component that allows healthcare providers to electronically enter medical orders (medications, labs, imaging, procedures). This reference covers CPOE workflow patterns, clinical decision support integration, and safety considerations.

## Core CPOE Workflow

### Standard Order Entry Flow

```
1. Patient Selection
   ├── Search for patient
   ├── Verify correct patient (2+ identifiers)
   └── Access patient chart

2. Order Context Establishment
   ├── Select encounter/visit
   ├── Verify patient location
   └── Confirm ordering provider

3. Order Search/Selection
   ├── Search order catalog
   │   ├── By name/mnemonic
   │   ├── By category (lab, medication, imaging)
   │   └── Recent/favorite orders
   ├── Order set selection (optional)
   └── Individual order selection

4. Order Configuration
   ├── Basic order details
   ├── Clinical parameters (dose, route, frequency)
   ├── Special instructions
   └── Order reason/indication

5. Clinical Decision Support (CDS) Checks
   ├── Drug-drug interactions
   ├── Drug-allergy interactions
   ├── Duplicate therapy
   ├── Dose range checking
   ├── Renal/hepatic dosing
   ├── Age-appropriate dosing
   └── Formulary/cost checks

6. Provider Response to Alerts
   ├── Accept recommendation
   ├── Override with reason
   ├── Modify order
   └── Cancel order

7. Order Review and Confirmation
   ├── Review all order details
   ├── Add order comments
   └── Confirm patient identity

8. Order Signing/Submission
   ├── Electronic signature
   ├── Co-signature requirement check
   ├── Order transmission
   └── Acknowledgment confirmation

9. Post-Submission Workflow
   ├── Order routing to fulfillment
   ├── Pharmacy/lab/radiology notification
   ├── MAR (Medication Administration Record) update
   └── Documentation in chart
```

## Medication Ordering Workflow

### Detailed Medication CPOE Flow

#### Phase 1: Medication Selection
```javascript
// Workflow states
const MedicationOrderStates = {
    SEARCHING: 'searching',
    SELECTED: 'selected',
    CONFIGURING: 'configuring',
    CDS_CHECKING: 'cds_checking',
    REVIEWING: 'reviewing',
    SIGNED: 'signed',
    TRANSMITTED: 'transmitted'
};

// Medication search methods
const searchMethods = {
    QUICK_PICK: 'Recent/favorite medications',
    TEXT_SEARCH: 'Free text search by name',
    CATEGORY_BROWSE: 'Browse by drug class',
    ORDER_SET: 'Pre-built order sets',
    PROBLEM_BASED: 'Medication based on diagnosis'
};
```

#### Phase 2: Dosing Configuration
```
Required Fields:
├── Medication Name (generic/brand)
├── Dose
│   ├── Dose quantity (e.g., 500)
│   ├── Dose units (mg, g, mL, etc.)
│   └── Dose form (tablet, capsule, injection)
├── Route
│   ├── PO (by mouth)
│   ├── IV (intravenous)
│   ├── IM (intramuscular)
│   ├── SC (subcutaneous)
│   └── Other routes
├── Frequency
│   ├── Standard frequencies (BID, TID, QID)
│   ├── Time-based (Q4H, Q6H, Q12H)
│   ├── PRN (as needed)
│   └── Custom schedules
├── Duration
│   ├── Number of days/weeks
│   ├── Until discontinued
│   └── Until specific date
└── Priority
    ├── Routine
    ├── Urgent
    └── STAT

Optional Fields:
├── PRN reason (if PRN medication)
├── Administration instructions
├── Do not substitute
├── Pharmacy routing
├── Start date/time
└── Clinical indication
```

#### Phase 3: Clinical Decision Support Checks

**Drug-Drug Interaction Check**
```
Interaction Severity Levels:
├── Critical/Contraindicated
│   └── Action: Hard stop or require override
├── Severe
│   └── Action: Interruptive alert
├── Moderate
│   └── Action: Non-interruptive notification
└── Minor
    └── Action: Passive display or log only

Alert Format:
┌─────────────────────────────────────────┐
│ ⚠️  SEVERE DRUG INTERACTION              │
├─────────────────────────────────────────┤
│ Warfarin + Aspirin                      │
│                                         │
│ Risk: Increased bleeding risk           │
│ Recommendation: Monitor INR closely     │
│                                         │
│ Evidence: Clinical studies, Level A     │
│ Reference: [Link to guideline]         │
├─────────────────────────────────────────┤
│ [Accept]  [Modify Order]  [Override]   │
└─────────────────────────────────────────┘
```

**Drug-Allergy Interaction Check**
```
Allergy Severity Levels:
├── Severe (Anaphylaxis)
│   └── Hard stop - order cannot proceed
├── Moderate (Severe rash, respiratory symptoms)
│   └── Require documented override
└── Mild (Minor rash, GI upset)
    └── Warning with accept/override

Cross-Reactivity Checking:
├── Same drug exact match
├── Drug class match (e.g., all penicillins)
└── Chemical structure similarity
```

**Duplicate Therapy Check**
```
Duplicate Types:
├── Same medication (exact duplicate)
├── Same therapeutic class (e.g., two statins)
├── Same ingredient (different formulations)
└── Overlapping ingredients (combination products)

Alert Example:
┌─────────────────────────────────────────┐
│ ℹ️  DUPLICATE THERAPY ALERT              │
├─────────────────────────────────────────┤
│ New Order: Lisinopril 10mg daily       │
│ Existing: Enalapril 5mg daily          │
│                                         │
│ Both are ACE Inhibitors                │
│ Recommendation: Discontinue one         │
├─────────────────────────────────────────┤
│ [Discontinue Existing]  [Continue Both]│
└─────────────────────────────────────────┘
```

**Dose Range Checking**
```
Checks Performed:
├── Maximum single dose
├── Maximum daily dose
├── Age-appropriate dosing
│   ├── Pediatric dosing (mg/kg)
│   ├── Geriatric dose adjustment
│   └── Neonatal dosing
├── Weight-based dosing verification
├── Renal function adjustment
│   ├── Calculate CrCl (Cockcroft-Gault)
│   ├── Check against renal dosing table
│   └── Recommend dose adjustment
└── Hepatic function adjustment
    ├── Check liver function tests
    └── Recommend dose adjustment

Calculation Example:
Patient Weight: 70 kg
Ordered: Vancomycin 2000mg IV Q12H
Maximum: 15-20 mg/kg/dose
Calculated Max: 70kg × 20mg/kg = 1400mg

Alert: Dose exceeds maximum (2000mg > 1400mg)
```

#### Phase 4: E-Prescribing Workflow (Outpatient)

```
E-Prescription Flow:
├── 1. Order entry and configuration
├── 2. CDS checks completion
├── 3. Pharmacy selection
│   ├── Patient's preferred pharmacy
│   ├── Mail-order pharmacy
│   └── New pharmacy search
├── 4. Prescription transmission
│   ├── Generate NCPDP SCRIPT message
│   ├── Encrypt transmission
│   └── Send via Surescripts network
├── 5. Pharmacy acknowledgment
│   ├── Received and processing
│   ├── Clarification needed
│   └── Unable to fill
├── 6. Fill notification
│   └── Prescription filled and ready
└── 7. Refill management
    ├── Pharmacy refill request
    ├── Provider approval/denial
    └── New prescription if needed
```

## Laboratory Order Workflow

### Lab Order Entry Flow

```
1. Lab Test Selection
   ├── Single test order
   ├── Lab panel/profile
   │   ├── Basic Metabolic Panel (BMP)
   │   ├── Comprehensive Metabolic Panel (CMP)
   │   ├── Complete Blood Count (CBC)
   │   └── Lipid Panel
   └── Custom test combination

2. Order Configuration
   ├── Collection date/time
   │   ├── STAT (immediate)
   │   ├── ASAP
   │   ├── Routine
   │   └── Timed collection
   ├── Specimen type
   │   ├── Blood (serum, plasma, whole blood)
   │   ├── Urine
   │   ├── CSF
   │   └── Other body fluids
   ├── Collection priority
   └── Clinical indication (AOE - Ask at Order Entry)

3. Ask at Order Entry (AOE) Questions
   ├── Fasting status
   ├── Last dose of medication
   ├── Menstrual period (for certain tests)
   ├── Time of last meal
   └── Test-specific questions

4. Clinical Decision Support
   ├── Duplicate test check
   │   └── Same test within timeframe
   ├── Test appropriateness
   │   └── Based on diagnosis/indication
   ├── Preferred test recommendations
   │   └── More specific or cost-effective
   └── Required confirmatory tests

5. Specimen Labeling
   ├── Generate barcode labels
   ├── Print labels
   └── Label verification at collection

6. Order Routing
   ├── Lab department routing
   ├── Send-out lab routing
   └── Reference lab routing
```

### Lab Order Decision Support Example

```
Duplicate Test Check:
┌─────────────────────────────────────────┐
│ ℹ️  RECENT LAB RESULT AVAILABLE          │
├─────────────────────────────────────────┤
│ Test: Comprehensive Metabolic Panel    │
│ Last Result: 2 days ago (11/17/2023)   │
│                                         │
│ Results:                                │
│ • Glucose: 95 mg/dL (Normal)           │
│ • Creatinine: 0.9 mg/dL (Normal)       │
│ • All values within normal limits      │
│                                         │
│ Recommendation: Review existing results │
│ before ordering duplicate test          │
├─────────────────────────────────────────┤
│ [View Results]  [Cancel Order]  [Order │
│                             Anyway]     │
└─────────────────────────────────────────┘
```

## Imaging/Radiology Order Workflow

### Radiology Order Entry Flow

```
1. Imaging Study Selection
   ├── Plain film (X-ray)
   ├── CT (Computed Tomography)
   ├── MRI (Magnetic Resonance Imaging)
   ├── Ultrasound
   ├── Nuclear medicine
   └── Fluoroscopy

2. Order Specification
   ├── Body part/region
   ├── Laterality (left, right, bilateral)
   ├── With/without contrast
   ├── Number of views (for X-ray)
   └── Study-specific protocols

3. Clinical Information
   ├── Clinical indication (required)
   ├── Relevant history
   ├── Prior imaging
   └── Pregnancy status (if applicable)

4. Contrast Decision Support
   ├── Contrast allergy check
   ├── Renal function check (for IV contrast)
   │   ├── eGFR calculation
   │   └── Creatinine level check
   ├── Metformin use check
   └── Contrast premedication orders

5. Radiation Dose Awareness
   ├── Cumulative radiation exposure display
   ├── Alternative imaging suggestions
   │   └── MRI instead of CT (if appropriate)
   └── Lowest dose protocol selection

6. Appropriateness Criteria Integration
   ├── ACR Appropriateness Criteria
   ├── Recommended vs. not recommended
   └── Alternative imaging suggestions

7. Scheduling
   ├── Priority (STAT, urgent, routine)
   ├── Portable vs. department
   ├── Scheduling coordination
   └── Patient preparation instructions
```

### Imaging Appropriateness Example

```
ACR Appropriateness Criteria Check:
┌─────────────────────────────────────────┐
│ 📋 IMAGING APPROPRIATENESS               │
├─────────────────────────────────────────┤
│ Order: CT Abdomen/Pelvis with contrast  │
│ Indication: Abdominal pain, acute       │
│                                         │
│ ACR Rating: Usually Appropriate (7/9)   │
│                                         │
│ Alternative Options:                    │
│ • Ultrasound (Usually Appropriate)      │
│   - No radiation exposure               │
│   - Lower cost                          │
│                                         │
│ • MRI Abdomen/Pelvis                    │
│   (May Be Appropriate)                  │
│                                         │
│ Clinical Note: Consider ultrasound for  │
│ initial evaluation in young patients    │
├─────────────────────────────────────────┤
│ [Proceed with CT]  [Change to US]      │
└─────────────────────────────────────────┘
```

## Order Sets and Protocols

### Order Set Structure

```
Order Set Components:
├── Metadata
│   ├── Order set name
│   ├── Description
│   ├── Target condition/procedure
│   ├── Specialty/service line
│   └── Version and effective date
├── Order Groups
│   ├── Medications
│   │   ├── Required medications
│   │   └── Optional/PRN medications
│   ├── Laboratory tests
│   │   ├── Baseline labs
│   │   └── Monitoring labs
│   ├── Imaging studies
│   ├── Procedures
│   ├── Nursing orders
│   │   ├── Vital signs frequency
│   │   ├── I&O monitoring
│   │   └── Activity level
│   ├── Diet orders
│   ├── Consults
│   └── Patient education
└── Decision Logic
    ├── Conditional orders (if/then)
    ├── Mutually exclusive choices
    ├── Parameter-based customization
    └── Weight/age-based calculations
```

### Order Set Example: Community-Acquired Pneumonia

```json
{
  "orderSetName": "Community-Acquired Pneumonia - Adult",
  "version": "2.1",
  "effectiveDate": "2023-11-01",
  "specialty": "Internal Medicine",
  "orderGroups": [
    {
      "groupName": "Admission Orders",
      "orders": [
        {
          "type": "nursing",
          "orderText": "Vital signs every 4 hours",
          "required": true
        },
        {
          "type": "nursing",
          "orderText": "Oxygen saturation monitoring continuous",
          "required": true
        },
        {
          "type": "nursing",
          "orderText": "Notify MD if: Temp > 38.5°C, RR > 24, SpO2 < 90%",
          "required": true
        }
      ]
    },
    {
      "groupName": "Diagnostic Tests",
      "orders": [
        {
          "type": "lab",
          "orderText": "Complete Blood Count with Differential",
          "required": true,
          "priority": "STAT"
        },
        {
          "type": "lab",
          "orderText": "Comprehensive Metabolic Panel",
          "required": true,
          "priority": "STAT"
        },
        {
          "type": "lab",
          "orderText": "Blood Cultures x2 (before antibiotics)",
          "required": true,
          "priority": "STAT"
        },
        {
          "type": "lab",
          "orderText": "Sputum Culture and Gram Stain",
          "required": false
        },
        {
          "type": "imaging",
          "orderText": "Chest X-ray PA and Lateral",
          "required": true,
          "priority": "STAT"
        }
      ]
    },
    {
      "groupName": "Antibiotic Therapy",
      "selectionType": "choose_one",
      "orders": [
        {
          "type": "medication",
          "orderText": "Ceftriaxone 1g IV daily + Azithromycin 500mg IV daily",
          "required": false,
          "indication": "Preferred for hospitalized patients"
        },
        {
          "type": "medication",
          "orderText": "Levofloxacin 750mg IV daily",
          "required": false,
          "indication": "Alternative, respiratory fluoroquinolone"
        },
        {
          "type": "medication",
          "orderText": "Ampicillin-Sulbactam 3g IV Q6H + Azithromycin 500mg IV daily",
          "required": false,
          "indication": "Beta-lactam allergy alternative"
        }
      ]
    },
    {
      "groupName": "Supportive Care",
      "orders": [
        {
          "type": "medication",
          "orderText": "Acetaminophen 650mg PO Q6H PRN fever or pain",
          "required": false
        },
        {
          "type": "respiratory",
          "orderText": "Oxygen therapy to maintain SpO2 > 92%",
          "required": true
        },
        {
          "type": "diet",
          "orderText": "Regular diet as tolerated",
          "required": true
        },
        {
          "type": "nursing",
          "orderText": "Encourage oral hydration",
          "required": true
        }
      ]
    }
  ]
}
```

## Clinical Decision Support Integration

### CDS Hooks Standard Integration

```javascript
// CDS Hooks specification for CPOE
const cdsHooksConfiguration = {
    // Hook triggered during medication ordering
    "medication-prescribe": {
        prefetch: {
            patient: "Patient/{{context.patientId}}",
            medications: "MedicationRequest?patient={{context.patientId}}&status=active",
            allergies: "AllergyIntolerance?patient={{context.patientId}}&clinical-status=active",
            conditions: "Condition?patient={{context.patientId}}&clinical-status=active"
        },
        context: {
            patientId: "string",
            encounterId: "string",
            medications: "array", // Draft medication orders
            userId: "string"
        }
    },

    // Hook triggered during order signing
    "order-sign": {
        prefetch: {
            patient: "Patient/{{context.patientId}}",
            orders: "ServiceRequest?patient={{context.patientId}}&status=draft"
        },
        context: {
            patientId: "string",
            encounterId: "string",
            draftOrders: "array",
            userId: "string"
        }
    }
};

// CDS Service Response Format
const cdsServiceResponse = {
    cards: [
        {
            summary: "Drug-Drug Interaction: Warfarin + Aspirin",
            indicator: "warning", // info, warning, critical
            source: {
                label: "Clinical Decision Support Service",
                url: "https://cds.example.com"
            },
            detail: "Concurrent use of warfarin and aspirin increases bleeding risk. Monitor INR closely and watch for signs of bleeding.",
            suggestions: [
                {
                    label: "Reduce aspirin dose to 81mg daily",
                    actions: [
                        {
                            type: "update",
                            resource: {
                                // Modified medication order
                            }
                        }
                    ]
                },
                {
                    label: "Discontinue aspirin",
                    actions: [
                        {
                            type: "delete",
                            resourceId: "MedicationRequest/aspirin-123"
                        }
                    ]
                }
            ],
            links: [
                {
                    label: "View Guideline",
                    url: "https://guidelines.example.com/warfarin-aspirin",
                    type: "absolute"
                }
            ]
        }
    ]
};
```

### Five Rights of Medication Administration

CPOE systems must support verification of:

```
1. Right Patient
   ├── Two patient identifiers
   ├── Photo verification
   └── Barcode scanning

2. Right Medication
   ├── Medication name verification
   ├── Barcode scanning
   └── NDC matching

3. Right Dose
   ├── Dose calculation verification
   ├── Dose range checking
   └── Weight-based calculation

4. Right Route
   ├── Route appropriateness
   ├── Route availability
   └── Special route considerations

5. Right Time
   ├── Scheduled time
   ├── Time windows
   └── Timing with meals/other meds
```

## Error Prevention Strategies

### Tall Man Lettering
Display look-alike/sound-alike medications with emphasized differences:

```
hydrALAZINE vs. hydrOXYzine
ceFAZolin vs. cefTRIAXone
vinBLAStine vs. vinCRIStine
DOPamine vs. DOBUTamine
```

### Trailing Zero Elimination
```
❌ Incorrect: 1.0 mg (could be misread as 10 mg)
✅ Correct: 1 mg

❌ Incorrect: .5 mg (decimal point could be missed)
✅ Correct: 0.5 mg
```

### High-Alert Medication Safeguards
```
High-Alert Medications:
├── Insulin
│   ├── Require dose verification
│   └── Display in units only (not mL)
├── Anticoagulants (Warfarin, Heparin)
│   ├── Require indication
│   └── Display lab values (INR, PTT)
├── Opioids
│   ├── Dose limit alerts
│   └── Concurrent CNS depressant warnings
├── Chemotherapy
│   ├── Two-provider verification
│   ├── BSA calculation display
│   └── Protocol conformance check
└── Neuromuscular Blockers
    ├── Hard stop alerts
    └── Require ICU/OR location
```

## Order Modification and Discontinuation

### Order Modification Workflow
```
1. Identify order to modify
   └── Search active orders list

2. Determine modification type
   ├── Dose change
   ├── Frequency change
   ├── Route change
   └── Duration change

3. System options
   ├── Modify existing order (with audit trail)
   └── Discontinue and replace (preferred)

4. Re-run CDS checks
   └── Same checks as new order

5. Document reason for change
   └── Required for audit

6. Sign modified order
   └── Electronic signature
```

### Order Discontinuation Workflow
```
1. Select order to discontinue
   └── From active orders list

2. Document discontinuation reason
   ├── Completed therapy
   ├── Adverse reaction
   ├── Medication ineffective
   ├── Duplicate therapy
   ├── Patient request
   └── Other (require text)

3. Confirm discontinuation
   └── Prevent accidental discontinuation

4. Sign discontinuation
   └── Electronic signature

5. Notification routing
   ├── Pharmacy notification
   ├── Nursing notification
   └── MAR update
```

## Best Practices

### 1. Usability
- Minimize clicks required for common orders
- Provide quick access to recent/favorite orders
- Implement intelligent search with autocomplete
- Display relevant patient context (allergies, active meds)

### 2. Safety
- Never allow CDS hard stops to be globally disabled
- Require override reasons with free-text documentation
- Implement time-delayed override for critical alerts
- Track and report override patterns

### 3. Alert Fatigue Mitigation
- Use tiered alert severity (info, warning, critical)
- Make non-critical alerts non-interruptive
- Regularly review and tune alert thresholds
- Suppress redundant alerts

### 4. Performance
- Prefetch patient data before order entry
- Asynchronous CDS checks where appropriate
- Cache order catalog data
- Optimize search indexing

### 5. Documentation
- Auto-populate order indications when possible
- Link orders to diagnoses
- Capture clinical context
- Maintain complete audit trail

## References

- **CPOE Best Practices**: Joint Commission
- **CDS Hooks**: https://cds-hooks.org/
- **SMART on FHIR**: https://smarthealthit.org/
- **Leapfrog CPOE Evaluation Tool**: https://www.leapfroggroup.org/
- **ACR Appropriateness Criteria**: https://www.acr.org/Clinical-Resources/ACR-Appropriateness-Criteria

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
