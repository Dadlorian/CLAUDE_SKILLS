# Healthcare UI/UX Guidelines

## Executive Summary

This document establishes comprehensive UI/UX standards for healthcare technology applications, ensuring compliance with accessibility regulations, clinical workflow optimization, and patient safety principles.

---

## 1. Section 508 Accessibility Compliance

### 1.1 Web Content Accessibility Guidelines (WCAG) 2.1

**Standard**: WCAG 2.1 Level AA compliance (minimum)

#### Color Contrast Requirements
- **Normal text**: 4.5:1 contrast ratio minimum
- **Large text (18pt+)**: 3:1 contrast ratio minimum
- **UI components**: 3:1 contrast ratio for visual elements
- **Forbidden**: Color alone as information carrier; use patterns, icons, text labels

#### Text and Font Standards
```
Font Size:     Minimum 12pt for body, 14pt for clinical data displays
Line Height:   1.5 minimum for readability
Font Family:   Sans-serif preferred (Arial, Helvetica, Verdana)
Letter Spacing: 0.12em minimum for accessibility
```

#### Navigation and Keyboard Access
- **Keyboard Navigation**: All functions accessible via keyboard
- **Tab Order**: Logical, predictable tab sequence matching visual order
- **Focus Indicators**: Visible focus indicator (min 2px outline) for all interactive elements
- **Skip Links**: Implementation for jumping past repetitive content
- **Bypass Blocks**: Mechanism to bypass header/navigation blocks

### 1.2 ARIA Implementation

#### Semantic Markup
```html
<!-- Use semantic HTML first -->
<button>Add Patient</button>
<nav aria-label="Main navigation">...</nav>
<main role="main">...</main>

<!-- ARIA for complex widgets -->
<div role="tablist" aria-label="Patient Records">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Lab Results
  </button>
</div>
```

#### Critical ARIA Attributes
- `aria-label`: For icon buttons (e.g., alerts, settings)
- `aria-describedby`: Complex form fields, warnings
- `aria-live="polite"`: Status updates (non-critical)
- `aria-live="assertive"`: Critical alerts (lab value abnormalities)
- `aria-disabled`: State of disabled medical equipment selectors
- `aria-expanded`: Collapsible clinical sections

### 1.3 Form Accessibility in Clinical Contexts

```html
<!-- Proper form structure -->
<fieldset>
  <legend>Patient Demographics</legend>
  <label for="mrn">
    Medical Record Number (MRN):
    <span aria-label="required">*</span>
  </label>
  <input
    id="mrn"
    type="text"
    aria-required="true"
    aria-describedby="mrn-hint"
  />
  <span id="mrn-hint">Format: 000-000-000</span>
</fieldset>
```

#### Error Handling
- Real-time validation with clear error messages
- Error associations with form fields via `aria-describedby`
- Suggest corrections (e.g., "ICD-10 code invalid, did you mean C34.90?")
- Recovery instructions visible before submission

---

## 2. Clinical Workflow Optimization

### 2.1 Cognitive Load Reduction

#### Information Hierarchy
**Priority Levels:**
1. **Critical**: Lab alerts, patient warnings, medication contraindications
2. **High**: Active diagnoses, current medications, recent changes
3. **Medium**: Historical data, trends, previous encounters
4. **Low**: Archive, historical notes, non-current data

#### Visual Prioritization
```
Critical:  Red (#E63946), 24pt bold, top of screen
High:      Orange (#F77F00), 18pt bold
Medium:    Blue (#457B9D), 14pt regular
Low:       Gray (#6C757D), 12pt regular
```

### 2.2 Task-Centered Design

#### Workflow Mapping
- **Analyze**: Clinician tasks (admission, diagnosis, ordering)
- **Prototype**: Task-specific interfaces (e.g., med order screens)
- **Test**: With actual clinicians (minimum 5 per workflow)
- **Iterate**: Based on error rates and time-to-task metrics

#### Key Metrics
- **Task Completion Time**: Baseline + 10% acceptable
- **Error Rate**: <2% for critical tasks
- **Cognitive Load**: NASA-TLX score <50
- **Satisfaction**: SUS score >70

### 2.3 Clinical Data Display Standards

#### EHR Chart Review Interface
```
┌─────────────────────────────────────────────┐
│ [Patient Name] MRN: [###] | Age: 67 | DOB   │
├─────────────────────────────────────────────┤
│ ALERTS: 3 New Lab Alerts | Drug Interaction │
├─────────────────────────────────────────────┤
│ ACTIVE PROBLEMS     | MEDICATIONS           │
│ • Diabetes Type 2   | • Metformin 500mg BID │
│ • Hypertension      | • Lisinopril 10mg QD  │
│ • COPD              | • Albuterol PRN       │
└─────────────────────────────────────────────┘
```

#### Data Display Principles
- **Scannability**: Monospace fonts for numerical data
- **Grouping**: Related data within visual containers
- **Trends**: Sparklines for vital signs, lab values
- **Timestamps**: All clinical data with date/time stamps
- **Source**: Data origin clearly identified (EHR, device, patient-reported)

### 2.4 Medication Ordering Interface

**Required Elements:**
- Patient allergy display (prominent, color-coded)
- Drug interaction checking (real-time, traffic light system)
- Dosage calculation aids (weight-based, renal function)
- Route/frequency standardization (dropdown, not free text)
- Confirmation screen (2-step verification)

---

## 3. Visual Design Standards

### 3.1 Color Palette for Healthcare

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| Critical/Alert | Red | #E63946 | Lab abnormalities, contraindications |
| Warning | Orange | #F77F00 | Pending actions, review needed |
| Success | Green | #2A9D8F | Confirmation, completed actions |
| Neutral/Info | Blue | #457B9D | General information, context |
| Disabled | Gray | #6C757D | Inactive options, read-only fields |
| Background | White | #FFFFFF | Primary background |
| Secondary BG | Light Gray | #F1F3F5 | Secondary panels, zebra striping |

### 3.2 Icons and Symbols

**Standards Compliance:**
- **Consistency**: Use same icon set (Material Design Healthcare recommended)
- **Redundancy**: Icons + text labels always
- **Size**: Minimum 24x24px for touchscreens
- **Color**: Follow color palette; ensure color-blind safe
- **Testing**: Validate with 100+ clinical staff members

---

## 4. Mobile and Tablet Optimization

### 4.1 Responsive Design Breakpoints

```css
/* Small phones (portrait) */
@media (max-width: 480px) {
  .clinical-data { font-size: 14px; }
  button { padding: 12px; } /* 48px touch target */
}

/* Tablets (portrait/landscape) */
@media (481px to 1024px) {
  .clinical-data { font-size: 16px; }
  button { padding: 10px 16px; }
}

/* Desktop */
@media (min-width: 1025px) {
  .clinical-data { font-size: 14px; }
  button { padding: 8px 12px; }
}
```

### 4.2 Touch Target Standards
- **Minimum size**: 48x48px (for clinical settings)
- **Spacing**: Minimum 8px between touch targets
- **Avoid**: Swipe gestures in critical workflows (unreliable)
- **Confirm**: Long-press for destructive actions (e.g., discharging patient)

---

## 5. Performance and Loading Standards

### 5.1 Clinical Response Time Requirements

| Action | Target Time | Failure Impact |
|--------|-------------|-----------------|
| EHR data load | <2 seconds | Clinician interruption |
| Lab value update | <500ms | Potential missed alert |
| Patient search | <1 second | Workflow delay |
| Medication lookup | <200ms | Ordering delay |
| Alert notification | <100ms | Safety risk |

### 5.2 Progressive Enhancement
- **Core content**: Load immediately (HTML)
- **Clinical data**: Load with enhanced styling (CSS)
- **Interactivity**: Load with JavaScript enhancements
- **Offline support**: Cache critical medication/allergy data

---

## 6. Language and Terminology

### 6.1 Clinical vs. Patient-Facing Language

**EHR Interface (Clinician-Facing):**
```
"Acute myocardial infarction (AMI) STEMI"
"LVEDP 35 mmHg"
"Administer heparin 80 U/kg IV bolus"
```

**Patient Portal (Patient-Facing):**
```
"Heart attack (type where arteries are blocked)"
"Heart function measurement"
"Blood thinner injection in vein"
```

### 6.2 Abbreviation Standards
- Expand abbreviations on first use: "Coronary Artery Disease (CAD)"
- Use standard medical abbreviations only (per JCAHO list)
- Avoid brand names (use generic names: acetaminophen, not Tylenol)
- Spell out units: "mg" is acceptable; "milligrams" in patient materials

---

## 7. Testing and Validation

### 7.1 Accessibility Testing Protocol

**Automated Testing:**
- axe DevTools, Lighthouse, WAVE
- Coverage: ≥80% of page elements
- Frequency: Continuous integration

**Manual Testing:**
- NVDA (Windows), JAWS (Windows), VoiceOver (Mac/iOS)
- Keyboard-only navigation
- Speech-to-text dictation

**User Testing:**
- Minimum 5 users per accessibility category
- Tasks: Admit patient, review labs, order medication
- Metrics: Success rate, time-on-task, SUS score

### 7.2 Clinical Workflow Testing

**Observation Studies:**
- 20+ clinical staff (nurses, physicians, pharmacists)
- Real patient data (de-identified)
- Minimum 4-hour sessions per clinician
- Error tracking and critical incident reporting

**Usability Metrics:**
```
- Task Success Rate: >95%
- Time-on-Task: Within 20% of baseline
- Error Rate: <2% for critical tasks
- Satisfaction (SUS): >75
```

---

## 8. Documentation Requirements

### 8.1 Design Documentation

**Required Components:**
- Design rationale for clinical workflows
- Accessibility compliance statements (Section 508 checklist)
- User research findings (with participant demographics)
- Workflow diagrams (task flows)
- Responsive design breakpoint documentation
- Color contrast verification results

### 8.2 Change Management
- Version control for design updates
- Notification system for clinical staff updates
- Rollback plan for failed deployments
- A/B testing framework for workflow changes

---

## 9. Compliance Checklist

- [ ] WCAG 2.1 Level AA compliance verified
- [ ] Keyboard navigation tested
- [ ] Screen reader tested (NVDA, JAWS)
- [ ] Color contrast verified (4.5:1 normal, 3:1 large)
- [ ] Mobile responsiveness tested (480px, 768px, 1024px+)
- [ ] Touch targets ≥48x48px
- [ ] Clinical workflow testing completed
- [ ] Performance targets met (<2s page load)
- [ ] Error handling tested
- [ ] Accessibility audit completed
- [ ] Clinical staff sign-off obtained

---

## 10. References and Standards

### Regulatory Standards
- Section 508 of the Rehabilitation Act (2001)
- Web Content Accessibility Guidelines (WCAG) 2.1
- 21 CFR Part 11 (FDA Electronic Records)
- IEC 62304 (Medical Device Software Lifecycle)

### Clinical Standards
- JCAHO Standards (medication ordering, patient safety)
- HL7 FHIR standards
- DICOM standards (medical imaging)

### Industry Resources
- AAMI (Association for Advancement of Medical Instrumentation)
- usability.gov (HHS Usability Research)
- Cleveland Clinic Experience: "Every Patient Tells a Story"

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Compliance Level**: FDA 21 CFR Part 11, Section 508 Accessible
