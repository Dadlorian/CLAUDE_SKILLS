# Clinical Pathways Reference

## Overview
Clinical pathways (also called critical pathways, care pathways, or clinical protocols) are structured multidisciplinary care plans that detail essential steps in the care of patients with specific clinical conditions.

## Core Components

### Pathway Elements
1. **Inclusion Criteria**: Which patients enter the pathway
2. **Exclusion Criteria**: Which patients are excluded
3. **Time Phases**: Pathway stages (ED, Floor, ICU, Discharge)
4. **Interventions**: Ordered actions at each phase
5. **Decision Points**: Branch logic based on patient response
6. **Outcomes**: Expected goals and metrics
7. **Variance Tracking**: Deviations from standard pathway

## Common Clinical Pathways

### Sepsis Pathway

#### Screening Criteria (qSOFA)
- Respiratory rate ≥ 22/min
- Altered mental status (GCS < 15)
- Systolic BP ≤ 100 mmHg

**2+ criteria → Sepsis suspected**

#### SIRS Criteria (Alternative)
- Temperature > 38°C or < 36°C
- Heart rate > 90 bpm
- Respiratory rate > 20/min or PaCO2 < 32 mmHg
- WBC > 12,000 or < 4,000 or > 10% bands

**2+ criteria + infection → Sepsis**

#### Sepsis Bundle (1-hour)
```
Hour 0 (Recognition):
├─ Obtain blood cultures
├─ Measure lactate
├─ Administer broad-spectrum antibiotics
├─ Begin crystalloid 30 mL/kg for hypotension or lactate ≥ 4
└─ Apply vasopressors if hypotensive during/after fluid resuscitation

Hour 3:
├─ Remeasure lactate if initial > 2
└─ Continue fluid resuscitation if needed

Hour 6:
├─ Target MAP ≥ 65 mmHg
├─ Target CVP 8-12 mmHg
└─ Target ScvO2 ≥ 70%
```

#### Automation Points
- Auto-fire sepsis alert on qSOFA ≥ 2
- Page critical care team
- Activate sepsis order set
- Start lactate timer
- Track bundle completion metrics

### STEMI Pathway

#### Activation Criteria
- ECG with ST elevation:
  - ≥ 1mm in two contiguous limb leads, OR
  - ≥ 2mm in two contiguous precordial leads
- OR new LBBB with clinical suspicion

#### Time Targets
```
Door → ECG: < 10 minutes
Door → Cath Lab: < 90 minutes
First Medical Contact → Device: < 90 minutes
```

#### Pathway Steps
```
0-10 min (ED Arrival):
├─ 12-lead ECG
├─ IV access
├─ Aspirin 324mg PO
├─ Oxygen if SpO2 < 90%
└─ STEMI identified → Activate

10-20 min (Activation):
├─ Page cardiology fellow
├─ Activate cath lab team
├─ Load P2Y12 inhibitor (ticagrelor 180mg or prasugrel 60mg)
├─ Anticoagulation (heparin or bivalirudin)
├─ Beta-blocker if no contraindications
└─ Nitroglycerin for chest pain

20-90 min (Cath Lab):
├─ Transfer to cath lab
├─ Coronary angiography
├─ PCI of culprit lesion
└─ TIMI flow restoration

Post-PCI:
├─ CCU admission
├─ High-intensity statin
├─ ACE inhibitor
├─ Cardiac rehab referral
└─ Smoking cessation
```

### Stroke Pathway

#### Rapid Triage
```
Last Known Well < 4.5 hours → tPA candidate
Last Known Well < 24 hours → Thrombectomy candidate
```

#### NIHSS (Stroke Severity)
- 0: No stroke symptoms
- 1-4: Minor stroke
- 5-15: Moderate stroke
- 16-20: Moderate-severe stroke
- 21-42: Severe stroke

#### Acute Stroke Protocol
```
0-10 min:
├─ Fingerstick glucose
├─ Vital signs
├─ NIHSS assessment
├─ Last known well time
└─ Stroke alert activated

10-25 min:
├─ Non-contrast head CT
├─ Blood work (CBC, BMP, PT/INR, troponin)
├─ ECG
└─ Neurology consult

25-60 min:
├─ tPA decision if < 4.5 hours
│  ├─ Inclusion criteria met?
│  ├─ Exclusion criteria absent?
│  └─ Patient/family consent
├─ CTA head/neck if thrombectomy candidate
└─ Admit to stroke unit or ICU

tPA Administration:
├─ 0.9 mg/kg (max 90mg)
├─ 10% bolus over 1 minute
├─ 90% infusion over 60 minutes
├─ No antiplatelet/anticoagulants for 24 hours
└─ Neuro checks q15min during, q30min after
```

### Community-Acquired Pneumonia (CAP) Pathway

#### Severity Assessment (CURB-65)
- **C**onfusion
- **U**rea > 20 mg/dL (BUN > 7 mmol/L)
- **R**espiratory rate ≥ 30/min
- **B**lood pressure: SBP < 90 or DBP ≤ 60
- Age ≥ **65**

**Score**:
- 0-1: Outpatient treatment
- 2: Consider hospitalization
- 3-5: Hospitalize, consider ICU

#### Treatment Pathway
```
Outpatient (CURB-65 0-1):
├─ Previously healthy + no antibiotics in 3 months:
│  └─ Amoxicillin 1g TID or Doxycycline 100mg BID
└─ Comorbidities or recent antibiotics:
   └─ Augmentin + azithromycin OR respiratory fluoroquinolone

Inpatient (CURB-65 2):
├─ Beta-lactam (ceftriaxone, ampicillin-sulbactam)
└─ + Macrolide (azithromycin) or doxycycline

ICU (CURB-65 3-5 or septic):
├─ Beta-lactam (ceftriaxone, cefotaxime)
└─ + Azithromycin or respiratory fluoroquinolone
└─ Add vancomycin or linezolid if MRSA risk
```

### Hip Fracture Pathway

#### Time Targets
- Surgery within 48 hours of admission
- Pain assessment every 4 hours
- VTE prophylaxis within 24 hours

#### Pathway Steps
```
ED (0-6 hours):
├─ X-ray hip/pelvis
├─ Pain management (nerve block preferred over opioids)
├─ Orthopedic consult
├─ Admit to orthopedic service
└─ NPO for surgery

Floor (6-48 hours):
├─ Pre-op medical clearance
├─ ECG, CBC, BMP
├─ Hold anticoagulants
├─ VTE prophylaxis (LMWH or fondaparinux)
├─ Continue pain management
└─ Delirium screening (CAM)

OR (< 48 hours):
├─ Surgical fixation or arthroplasty
├─ Anesthesia optimization (regional > general)
└─ Antibiotic prophylaxis

Post-Op:
├─ Early mobilization (POD 1)
├─ Physical therapy BID
├─ Pain management
├─ VTE prophylaxis
├─ Osteoporosis treatment
├─ Fall risk assessment
└─ Discharge planning
```

### Heart Failure Exacerbation Pathway

#### Admission Criteria
- Dyspnea at rest
- Volume overload (edema, pulmonary congestion)
- BNP > 500 or NT-proBNP > 1000

#### Treatment Protocol
```
Initial Management:
├─ IV diuresis (furosemide, typically 2x home dose)
├─ Daily weights
├─ Strict I/O monitoring
├─ Low-sodium diet (< 2g/day)
├─ Fluid restriction (< 2L/day)
└─ Continue GDMT (ACE-I, beta-blocker, MRA)

Monitoring:
├─ Daily weights (target -1 to -2 kg/day)
├─ BMP daily (watch K, Cr)
├─ Clinical assessment (JVP, edema, lung sounds)
└─ Consider RHC if refractory

Diuretic Resistance:
├─ Increase dose
├─ Switch to continuous infusion
├─ Add metolazone or thiazide
└─ Consider ultrafiltration

Discharge Criteria:
├─ Euvolemic or improved
├─ Stable renal function
├─ Converted to oral diuretics
├─ Patient education completed
└─ Follow-up scheduled within 7 days
```

## Pathway Automation

### EHR Integration Points

#### Pathway Activation
```javascript
// Trigger pathway when criteria met
if (patient.hasCondition('STEMI') || ECG.showsSTElevation()) {
  activatePathway('STEMI_PATHWAY');
  pageTeam('CARDIOLOGY');
  fireOrderSet('STEMI_BUNDLE');
  startTimer('DOOR_TO_BALLOON');
}
```

#### Task Automation
```javascript
const pathway = {
  name: "Sepsis",
  phases: [
    {
      name: "Hour 0",
      tasks: [
        { action: "order", type: "lab", code: "Blood Culture x2" },
        { action: "order", type: "lab", code: "Lactate" },
        { action: "order", type: "med", code: "Ceftriaxone 2g IV" },
        { action: "order", type: "fluid", code: "NS 30mL/kg bolus" },
        { action: "notify", team: "ICU", message: "Sepsis alert" }
      ],
      timeLimit: 60  // minutes
    }
  ]
};
```

#### Variance Tracking
```javascript
function trackVariance(pathway, patient) {
  const variances = [];

  // Check if tasks completed on time
  for (const task of pathway.tasks) {
    if (!task.completed) {
      variances.push({
        type: "OMISSION",
        task: task.name,
        reason: task.varianceReason || "Unknown"
      });
    } else if (task.completedTime > task.deadline) {
      variances.push({
        type: "DELAY",
        task: task.name,
        delayMinutes: task.completedTime - task.deadline
      });
    }
  }

  return variances;
}
```

## Pathway Representation (FHIR)

### PlanDefinition Resource
```json
{
  "resourceType": "PlanDefinition",
  "id": "sepsis-pathway",
  "title": "Sepsis Management Pathway",
  "status": "active",
  "type": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type",
      "code": "clinical-protocol"
    }]
  },
  "action": [
    {
      "title": "Obtain blood cultures",
      "timingDuration": {
        "value": 60,
        "unit": "minutes"
      },
      "definitionCanonical": "ActivityDefinition/blood-culture-order"
    },
    {
      "title": "Administer antibiotics",
      "timingDuration": {
        "value": 60,
        "unit": "minutes"
      },
      "definitionCanonical": "ActivityDefinition/broad-spectrum-antibiotics"
    }
  ]
}
```

## Quality Metrics

### Pathway Compliance
- **Activation Rate**: % eligible patients enrolled
- **Completion Rate**: % patients completing pathway
- **Time Metrics**: Door-to-needle, door-to-balloon, etc.
- **Variance Rate**: % patients with deviations

### Clinical Outcomes
- Mortality reduction
- Length of stay
- Complication rates
- Readmission rates
- Cost savings

## Best Practices

1. **Evidence-Based**: Ground in clinical guidelines
2. **Multidisciplinary**: Involve all care team members
3. **Flexible**: Allow for clinical judgment
4. **Measurable**: Define clear metrics
5. **Integrated**: Build into EHR workflow
6. **Monitored**: Track compliance and outcomes
7. **Updated**: Revise based on new evidence
8. **Trained**: Educate staff on pathway use
9. **Patient-Centered**: Consider patient preferences
10. **Iterative**: Continuously improve

## Resources
- Institute for Healthcare Improvement (IHI)
- Society of Hospital Medicine (Care Pathways)
- American College of Cardiology (STEMI guidelines)
- Surviving Sepsis Campaign
- American Stroke Association (Stroke guidelines)
