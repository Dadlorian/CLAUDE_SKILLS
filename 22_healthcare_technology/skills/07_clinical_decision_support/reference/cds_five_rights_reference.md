# CDS Five Rights Reference

## Overview
The "Five Rights" of Clinical Decision Support is a framework developed by Jerome Osheroff, MD and colleagues to ensure that CDS interventions are effective, appropriate, and well-received by clinicians.

## The Five Rights

### 1. Right Information

**Definition**: Providing evidence-based, actionable clinical knowledge

**Key Principles**:
- **Evidence-Based**: Grounded in clinical guidelines and research
- **Specific**: Tailored to the clinical situation
- **Actionable**: Clear recommendations, not just information
- **Concise**: Brief and to the point
- **Current**: Up-to-date with latest evidence

**Examples**:

**Poor**: "Aspirin may be beneficial"
**Good**: "Start aspirin 81mg daily for secondary prevention post-MI"

**Poor**: "Consider checking renal function"
**Good**: "GFR 35 - reduce metformin dose to 500mg daily or discontinue"

**Poor**: "Drug interaction possible"
**Good**: "Major interaction: Warfarin + aspirin increases bleeding risk 2-3x. Consider gastroprotection with PPI or switch to apixaban."

**Implementation**:
```javascript
function rightInformation(alert) {
  return {
    // Evidence-based clinical fact
    finding: "INR 4.5 (therapeutic range 2-3)",

    // Clinical significance
    significance: "Elevated INR increases bleeding risk",

    // Specific recommendation
    recommendation: "Hold warfarin tonight. Recheck INR tomorrow. Restart at lower dose when INR < 3.5",

    // Evidence citation
    evidence: {
      guideline: "ACC/AHA Anticoagulation Guidelines 2023",
      grade: "1A"
    }
  };
}
```

### 2. Right Person

**Definition**: Delivering CDS to the individual who can act on it

**Key Principles**:
- **Role-Appropriate**: Send to person who can take action
- **Responsibility-Aligned**: Match to clinical responsibility
- **Avoid Alert Spam**: Don't notify irrelevant parties
- **Escalation Path**: Clear escalation if primary person unavailable

**Role-Based Routing**:
```javascript
const alertRouting = {
  "critical-lab": {
    primary: "ordering-provider",
    secondary: "nurse",
    escalation: "attending-physician"
  },

  "drug-interaction": {
    primary: "prescribing-provider",
    secondary: "pharmacist",
    backup: "covering-provider"
  },

  "sepsis-alert": {
    primary: "bedside-nurse",
    secondary: "resident",
    critical: "rapid-response-team"
  },

  "fall-risk": {
    primary: "nurse",
    secondary: "care-coordinator"
  }
};

function routeAlert(alert, patient) {
  const routing = alertRouting[alert.type];
  const primary = findProvider(patient, routing.primary);

  if (primary.available) {
    send(alert, primary);
  } else {
    send(alert, findProvider(patient, routing.secondary));
    notify(routing.escalation, "Alert routed to backup");
  }
}
```

**Examples**:

| Alert Type | Wrong Person | Right Person |
|------------|--------------|--------------|
| Critical K+ 6.5 | Medical student | Resident or attending |
| Renal dose adjustment | Nurse | Prescribing physician or pharmacist |
| Fall risk high | Physician | Nurse or care coordinator |
| Missing mammogram | Hospitalist | Primary care physician |
| Drug-drug interaction | Attending (for resident order) | Ordering resident |

### 3. Right Format

**Definition**: Presenting CDS in a format that fits the clinical workflow

**Key Principles**:
- **Minimal Clicks**: Reduce cognitive load
- **Scannable**: Quick visual processing
- **Contextual**: Embedded in workflow
- **Visual Hierarchy**: Most important info prominent
- **Mobile-Friendly**: Works on all devices

**Format Types**:

#### Interruptive Alerts (Hard Stops)
**When**: Critical safety issues only
**Format**: Modal dialog requiring acknowledgment

```
┌─────────────────────────────────────────┐
│  ⚠️  CRITICAL DRUG ALLERGY              │
├─────────────────────────────────────────┤
│  Patient allergic to PENICILLIN         │
│  Reaction: Anaphylaxis (2019)           │
│                                         │
│  Ordered: Amoxicillin 500mg             │
│                                         │
│  ❌ CANCEL ORDER                        │
│  ⚠️  OVERRIDE (requires reason)         │
└─────────────────────────────────────────┘
```

#### Non-Interruptive Alerts (Soft Stops)
**When**: Important but not critical
**Format**: Notification banner, sidebar

```
┌─────────────────────────────────────────┐
│ ⚠️ Moderate Drug Interaction             │
│ Lisinopril + Spironolactone             │
│ → Hyperkalemia risk                     │
│ Recommendation: Monitor K+ weekly x 4   │
│ [Dismiss] [More Info] [Accept Rec]      │
└─────────────────────────────────────────┘
```

#### Passive CDS
**When**: Background information, order sets
**Format**: Infobuttons, order set templates, calculators

```
┌──────────────────────────────┐
│  Ordering: Heparin Infusion  │
├──────────────────────────────┤
│  Weight-Based Protocol:      │
│  □ 80 units/kg bolus         │
│  □ 18 units/kg/hr infusion   │
│                              │
│  ℹ️ Weight: 75 kg            │
│  → 6,000 unit bolus          │
│  → 1,350 units/hr            │
│                              │
│  [Apply Protocol]            │
└──────────────────────────────┘
```

#### Dashboard/Summary
**When**: Overview of patient status, care gaps
**Format**: Visual dashboard

```
┌─────────────────────────────────────┐
│  Care Gaps for John Smith           │
├─────────────────────────────────────┤
│  ⚠️  A1c > 9% - Due for check       │
│  ⚠️  LDL 145 - Not on statin        │
│  ✓  Flu shot - Up to date           │
│  ⚠️  Colonoscopy - Overdue (age 52) │
│  ⚠️  Foot exam - Due (diabetic)     │
└─────────────────────────────────────┘
```

#### Smart Order Sets
**When**: Common clinical scenarios
**Format**: Pre-built order bundles

```javascript
const STEMIOrderSet = {
  name: "STEMI Bundle",
  autoPopulate: true,
  orders: [
    {
      type: "medication",
      drug: "Aspirin 324mg",
      route: "PO",
      frequency: "STAT",
      checked: true
    },
    {
      type: "medication",
      drug: "Ticagrelor 180mg",
      route: "PO",
      frequency: "STAT",
      checked: true
    },
    {
      type: "lab",
      test: "Troponin",
      checked: true
    },
    {
      type: "consult",
      service: "Cardiology",
      urgency: "STAT",
      checked: true
    },
    {
      type: "notification",
      team: "Cath Lab",
      message: "STEMI activation",
      checked: true
    }
  ]
};
```

### 4. Right Channel

**Definition**: Delivering CDS through the appropriate medium

**Key Principles**:
- **Workflow-Integrated**: Within EHR where clinicians work
- **Severity-Matched**: Channel matches urgency
- **Multi-Modal**: Use multiple channels for critical items
- **Persistent vs Transient**: Match to clinical need

**Channel Options**:

#### EHR Alert
**When**: During order entry, chart review
**Pros**: In workflow, contextual
**Cons**: Can be ignored if alert fatigue

#### SMS/Paging
**When**: Critical results, time-sensitive
**Pros**: Immediate notification
**Cons**: Out of context, interruption

```javascript
if (lab.name === "Potassium" && lab.value > 6.0) {
  // Multi-channel for critical
  sendEHRAlert(orderingProvider);
  sendPage(orderingProvider, "CRITICAL K+ 6.5 for " + patient.name);
  sendSMS(primaryNurse, "Critical K+ - check patient");
}
```

#### Email
**When**: Non-urgent, care gap reports
**Pros**: Non-interruptive, detailed
**Cons**: May not be timely

#### Dashboard/Worklist
**When**: Routine monitoring, care gaps
**Pros**: Organized, prioritized
**Cons**: Requires active checking

#### Automated Voice Call
**When**: Critical results outside EHR
**Pros**: Reaches clinician anywhere
**Cons**: Interruptive

**Channel Selection Matrix**:

| Urgency | In EHR | Outside EHR |
|---------|--------|-------------|
| **Critical (immediate)** | Modal alert | Page + EHR alert |
| **Important (same day)** | Banner alert | SMS + EHR alert |
| **Routine (this week)** | Dashboard | Email |
| **Informational** | Infobutton | None |

### 5. Right Time

**Definition**: Providing CDS at the moment it's most relevant and actionable

**Key Principles**:
- **Just-In-Time**: When decision is being made
- **Anticipatory**: Before errors occur
- **Not Too Early**: Wait for enough context
- **Not Too Late**: Before action is final

**Timing Examples**:

#### Medication Ordering Workflow
```
Selection → Dosing → Routing → Frequency → Sign
    ↓         ↓        ↓          ↓         ↓
  Allergy  Renal    Admin    Duplicate   Final
  Check    Adjust   Check    Check      Review

Too Early: Allergy check before drug selected
Right Time: Allergy check when drug selected
Too Late: Allergy check after order signed
```

#### Implementation
```javascript
const CDSHooks = {
  // TOO EARLY - not yet enough context
  "patient-view": {
    when: "Opening patient chart",
    cds: ["general-alerts", "care-gaps"],
    avoid: ["specific-order-guidance"]  // Don't know what ordering yet
  },

  // RIGHT TIME - specific medication selected
  "medication-prescribe": {
    when: "Prescribing medication",
    cds: [
      "drug-allergy-check",
      "drug-drug-interaction",
      "renal-dosing",
      "duplicate-therapy",
      "pregnancy-warning"
    ]
  },

  // STILL RIGHT TIME - before finalizing
  "order-sign": {
    when: "Signing/finalizing orders",
    cds: [
      "final-safety-check",
      "required-labs",
      "monitoring-plan"
    ]
  },

  // TOO LATE - order already sent
  "order-complete": {
    when: "After order sent to pharmacy",
    cds: [],  // Avoid alerts here - too late to prevent
    alternative: "Call pharmacy to modify"
  }
};
```

#### Temporal Patterns

**Event-Driven (Real-Time)**:
```javascript
// Fire immediately when condition detected
onLabResult(result => {
  if (result.isCritical()) {
    alertProvider.immediately();
  }
});
```

**Batch Processing (Scheduled)**:
```javascript
// Run overnight for non-urgent items
scheduleDailyAt("06:00", () => {
  patients.forEach(patient => {
    const careGaps = identifyCareGaps(patient);
    addToDashboard(careGaps);
  });
});
```

**Predictive (Anticipatory)**:
```javascript
// Alert before problem occurs
if (patient.onWarfarin && !hasScheduledINR(nextWeek)) {
  remind("INR due next week - schedule now");
}
```

**Contextual Timing**:
```javascript
function shouldFireAlert(alert, context) {
  // Don't alert during code blue
  if (context.emergencyInProgress) return false;

  // Don't alert at 3 AM for non-critical
  if (context.hour >= 22 || context.hour <= 6) {
    return alert.severity === "CRITICAL";
  }

  // Don't interrupt during procedures
  if (context.providerInProcedure) {
    return alert.severity === "CRITICAL";
  }

  return true;
}
```

## Applying the Five Rights

### Checklist for CDS Design

- [ ] **Right Information**: Is the recommendation evidence-based, specific, and actionable?
- [ ] **Right Person**: Is it going to someone who can act on it?
- [ ] **Right Format**: Is it scannable, minimal-click, and workflow-appropriate?
- [ ] **Right Channel**: Is it delivered through the best medium for urgency?
- [ ] **Right Time**: Is it firing at the optimal decision point?

### Example: Well-Designed CDS

**Scenario**: Renal dosing adjustment for antibiotic

✓ **Right Information**:
- "GFR 35 mL/min - reduce ceftriaxone to 1g daily (usual dose 2g)"
- Evidence: FDA dosing guidelines, pharmacy database

✓ **Right Person**:
- Prescribing physician (can modify order)
- CC pharmacist (for complex cases)

✓ **Right Format**:
- Non-interruptive banner during order entry
- One-click "Apply Recommendation" button
- Link to dosing calculator

✓ **Right Channel**:
- EHR alert at point of order
- Not page or email (not critical, in workflow)

✓ **Right Time**:
- During medication ordering (can adjust before signing)
- Not after order sent to pharmacy

### Example: Poorly-Designed CDS

**Scenario**: Same renal dosing issue

✗ **Wrong Information**:
- "Patient has renal insufficiency" (not actionable)

✗ **Wrong Person**:
- Alert sent to nurse (cannot modify physician order)

✗ **Wrong Format**:
- Hard stop modal requiring override (not critical)
- Long explanatory text requiring scrolling

✗ **Wrong Channel**:
- Email sent next day (too late)

✗ **Wrong Time**:
- Alert fires when opening chart (before drug selected)

## Measuring Adherence to Five Rights

### Metrics

**Right Information**:
- Override rate with reason "Not applicable"
- User feedback on relevance

**Right Person**:
- % alerts sent to someone who cannot act
- Time from alert to action

**Right Format**:
- Clicks required to act
- Mobile usability scores
- Time to comprehend alert

**Right Channel**:
- % alerts seen and acknowledged
- Delay from alert to action

**Right Time**:
- % alerts firing before relevant workflow step
- % alerts during appropriate hours
- Temporal distance from decision point

## Best Practices Summary

1. **Start with Clinical Need**: Design CDS to solve real problems
2. **Involve Clinicians**: Co-design with end users
3. **Apply Five Rights**: Use as design checklist
4. **Measure & Iterate**: Track metrics and refine
5. **Respect Workflow**: Integrate, don't interrupt
6. **Minimize Burden**: Reduce alert fatigue
7. **Support Decision**: Augment, don't replace judgment
8. **Document Rationale**: Track why CDS designed this way

## Resources
- Osheroff JA, et al. "Improving Outcomes with Clinical Decision Support: An Implementer's Guide" (HIMSS, 2012)
- Campbell EM, et al. "Types of unintended consequences related to computerized provider order entry" (JAMIA, 2006)
- Wright A, et al. "Best practices in clinical decision support: the case of preventive care reminders" (Applied Clinical Informatics, 2010)
