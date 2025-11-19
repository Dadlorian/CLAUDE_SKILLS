# Clinical Rules Engine Reference

## Overview
Clinical rules engines execute medical logic to provide decision support, automate clinical workflows, and ensure evidence-based care delivery.

## Rules Engine Architectures

### Forward Chaining (Data-Driven)
- Start with known facts (patient data)
- Apply rules to infer new facts
- Continue until no more rules fire
- **Use Case**: Alerts, screening, preventive care

### Backward Chaining (Goal-Driven)
- Start with hypothesis/goal
- Work backward to find supporting facts
- **Use Case**: Diagnosis support, therapy selection

### Hybrid Systems
- Combine forward and backward chaining
- Event-driven + query-based

## Popular Rules Engines

### Drools (JBoss Rules)
**Language**: Java
**Strengths**:
- Mature, production-proven
- Rete algorithm optimization
- Complex event processing
- Decision tables

**Rule Format**:
```drools
rule "High Glucose Alert"
when
    $patient: Patient()
    $glucose: Observation(
        code.coding contains "2345-7",  // LOINC for glucose
        valueQuantity.value > 300,
        subject == $patient.id
    )
then
    ClinicalAlert alert = new ClinicalAlert();
    alert.setSeverity("critical");
    alert.setMessage("Critical hyperglycemia: " + $glucose.getValue() + " mg/dL");
    alert.setRecommendation("Check for DKA. Consider insulin protocol.");
    insert(alert);
end
```

### JBPM (Business Process Management)
**Strengths**:
- Workflow orchestration
- Human task management
- Process versioning
- BPMN 2.0 compliant

**Use Cases**:
- Clinical pathways
- Care coordination workflows
- Multi-step protocols

### Arden Syntax
**Specialization**: Medical logic modules (MLMs)
**Strengths**:
- Healthcare-specific
- ASTM/HL7 standard
- Knowledge sharing

**MLM Structure**:
```arden
maintenance:
    title: Potassium Alert;;
    mlmname: hyperkalemia_alert;;
    arden: version 2.10;;
    version: 1.0;;
    institution: Example Health System;;
    author: Clinical Informatics Team;;
    date: 2023-11-19;;
    validation: testing;;

library:
    purpose: Alert on critical hyperkalemia;;
    explanation: Generates critical alert when K+ > 6.0;;

knowledge:
    type: data-driven;;
    priority: 99;;

data:
    potassium := read last {serum potassium from laboratory};
    potassium_time := time of potassium;

evoke:
    potassium_time;

logic:
    if potassium > 6.0 mmol/L then
        conclude true;
    else
        conclude false;
    endif;

action:
    write "CRITICAL: Potassium " || potassium || " mmol/L";
    write "Repeat K+, check EKG, consider calcium gluconate";
    write "Restrict dietary K+, consider kayexalate/insulin-glucose";
end:
```

### OpenCDS
**Technology**: Java, Drools, HL7 vMR (Virtual Medical Record)
**Strengths**:
- Open source
- Standards-based
- CDS Hooks support
- Knowledge artifact sharing

### CQL (Clinical Quality Language)
**Specification**: HL7 standard
**Strengths**:
- Human-readable
- FHIR-native
- Quality measures
- Decision support

**Example**:
```cql
library DiabetesManagement version '1.0'

using FHIR version '4.0.1'

context Patient

define "Has Diabetes":
  exists([Condition: "Diabetes Mellitus"] C
    where C.clinicalStatus ~ "active")

define "Most Recent HbA1c":
  Last([Observation: "HbA1c"] O
    where O.status = 'final'
    sort by effective.value desc)

define "A1c Uncontrolled":
  "Has Diabetes"
    and "Most Recent HbA1c".value > 9.0 '%'

define "Needs Intensification":
  "A1c Uncontrolled"
    and not exists([MedicationRequest: "Insulin"])
```

## Rule Components

### Condition (When/If)
Define triggering criteria:
- Patient demographics (age, sex, pregnancy)
- Diagnoses (ICD-10, SNOMED)
- Medications (RxNorm, drug classes)
- Lab results (LOINC, values, trends)
- Vital signs (ranges, trends)
- Procedures (CPT, SNOMED)
- Time/temporal logic
- Allergies
- Risk factors

### Action (Then)
Define CDS intervention:
- Generate alert/notification
- Display information
- Suggest order
- Create task/reminder
- Trigger workflow
- Send message
- Update documentation
- Log event

### Metadata
- Rule ID and version
- Author and institution
- Evidence/citations
- Approval status
- Effective dates
- Target population
- Specialty/setting

## Common Rule Patterns

### Screening Rules
```pseudocode
IF patient.age >= 50
   AND patient.sex = "female"
   AND NOT exists(Procedure: "Mammogram" in last 2 years)
THEN
   Recommendation: "Mammogram screening due"
   Category: "Preventive Care"
```

### Medication Safety Rules
```pseudocode
IF medication.class = "ACE Inhibitor"
   AND patient.hasCondition("Pregnancy")
THEN
   Alert: "CONTRAINDICATED: ACE inhibitor in pregnancy"
   Severity: "critical"
   Action: "Discontinue immediately, consider alternative"
```

### Lab Monitoring Rules
```pseudocode
IF patient.takingMedication("Warfarin")
   AND NOT exists(Lab: "INR" in last 4 weeks)
THEN
   Recommendation: "INR due for warfarin monitoring"
   Suggested_Order: INR
```

### Duplicate Order Prevention
```pseudocode
IF new_order.type = "Imaging/Chest X-Ray"
   AND exists(Order: "Chest X-Ray" in last 24 hours)
THEN
   Alert: "Duplicate chest x-ray ordered within 24 hours"
   Severity: "warning"
   Options: ["Continue anyway", "Cancel new order"]
```

## Temporal Logic

### Point-in-Time
```pseudocode
glucose > 300 mg/dL
```

### Duration
```pseudocode
creatinine > 1.5 mg/dL for 48 hours
```

### Trend Analysis
```pseudocode
creatinine increased by > 0.3 mg/dL in 48 hours
```

### Sequence
```pseudocode
antibiotic started BEFORE culture obtained
```

### Periodic Events
```pseudocode
NOT (HbA1c checked every 3 months)
```

## Knowledge Representation

### Decision Tables
|Age|Gender|Smoking|10-yr ASCVD Risk|LDL|Statin Recommendation|
|---|------|-------|----------------|---|---------------------|
|40-75|Any|Yes|>=7.5%|70-189|High-intensity|
|40-75|Any|No|>=7.5%|70-189|Moderate-to-high|
|40-75|Any|Any|5-7.4%|70-189|Moderate|
|40-75|Any|Any|<5%|70-189|Discuss risk|

### Decision Trees
```
Chest Pain
├─ STEMI ECG changes?
│  ├─ Yes → Activate STEMI pathway
│  └─ No → Check troponin
│     ├─ Elevated → NSTEMI pathway
│     └─ Normal → Continue observation
```

### Scoring Systems
```pseudocode
CHADS2-VASc Score:
  CHF: 1 point
  Hypertension: 1 point
  Age >= 75: 2 points
  Diabetes: 1 point
  Stroke/TIA history: 2 points
  Vascular disease: 1 point
  Age 65-74: 1 point
  Sex (female): 1 point

Score >= 2: Anticoagulation recommended
```

## Rule Prioritization

### Severity-Based
1. Critical safety (hard stop)
2. Important safety (interruptive)
3. Best practice (passive)
4. Informational

### Time-Based
1. Time-critical (sepsis, STEMI)
2. Same-day actions
3. Within-encounter actions
4. Longitudinal care

### Specificity-Based
More specific rules override general rules

## Performance Optimization

### Indexing
- Index patient data by common access patterns
- Cache frequently accessed reference data
- Pre-compute derived values

### Rule Compilation
- Compile rules to efficient bytecode
- Optimize rule ordering
- Eliminate redundant conditions

### Incremental Processing
- Process only changed data
- Event-driven firing
- Selective rule execution

### Caching
- Cache patient facts
- Cache intermediate results
- Cache reference data (drug databases)

## Testing Strategies

### Unit Testing
Test individual rules with specific scenarios:
```yaml
test_case: "Potassium Alert - Critical High"
given:
  patient:
    id: "PT123"
    age: 65
  lab_result:
    test: "Potassium"
    value: 6.5
    unit: "mmol/L"
expect:
  alert_fired: true
  severity: "critical"
  message_contains: "CRITICAL: Potassium"
```

### Integration Testing
Test rule interactions:
- Multiple rules firing simultaneously
- Rule conflicts
- Override behavior

### Regression Testing
Prevent rule changes from breaking existing behavior

### Clinical Validation
Real-world patient data testing with clinician review

## Governance

### Rule Lifecycle
1. **Proposal**: Clinical need identified
2. **Development**: Rule authored
3. **Review**: Clinical committee approval
4. **Testing**: Validation with test data
5. **Deployment**: Production release
6. **Monitoring**: Performance tracking
7. **Optimization**: Threshold refinement
8. **Retirement**: Sunset obsolete rules

### Change Control
- Version control (Git)
- Change approval workflow
- Testing requirements
- Deployment process
- Rollback procedures

### Documentation
- Clinical rationale
- Evidence citations
- Test cases
- Known limitations
- Approval records

## Common Pitfalls

### Alert Fatigue
- Too many low-value alerts
- Insufficient specificity
- Poor timing

### Performance Issues
- Complex rules not optimized
- Insufficient caching
- Blocking clinical workflow

### Clinical Inaccuracy
- Outdated clinical logic
- Edge cases not handled
- Insufficient testing

### Maintenance Burden
- Rules not modular
- Hard-coded values
- Poor documentation

## Best Practices

1. **Start Simple**: Begin with high-value, simple rules
2. **Evidence-Based**: Ground in clinical guidelines
3. **Measure Impact**: Track outcomes and overrides
4. **Iterate**: Refine based on real-world use
5. **Modular Design**: Reusable rule components
6. **Version Control**: Track all changes
7. **Clinical Involvement**: Physician-led development
8. **User Testing**: Validate with end users
9. **Performance**: < 3 second response time
10. **Fail Gracefully**: Never block clinical care

## Resources
- Drools Documentation: https://drools.org
- OpenCDS: https://opencds.org
- HL7 CQL: https://cql.hl7.org
- Arden Syntax: ASTM E2210
