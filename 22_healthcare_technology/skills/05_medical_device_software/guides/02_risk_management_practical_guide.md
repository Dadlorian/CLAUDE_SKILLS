# Risk Management (ISO 14971) Practical Guide

## Getting Started with ISO 14971

### Before Starting Risk Analysis
1. **Understand Scope**: What is the device? Intended use?
2. **Identify Stakeholders**: Who should be involved in risk analysis?
3. **Gather Information**: Historical data, similar devices, standards
4. **Define Acceptable Risk**: What risk level is acceptable?
5. **Establish Process**: Who will do analysis? When? How?

## Step-by-Step Risk Analysis

### Step 1: Hazard Identification

**Brainstorming Approach**
- Team meeting with diverse expertise (engineer, clinician, QA, user)
- List all potential hazards
- Use FMEA (Failure Modes and Effects Analysis) framework
- Consider software-specific hazards
- No filters yet (capture everything)

**Hazard Categories to Consider**
- **Data Integrity**: Wrong readings, corrupted data
- **Algorithm Errors**: Calculation mistakes, rounding errors
- **User Interface**: Confusing displays, wrong interpretation
- **System Failures**: Crashes, timeouts, memory errors
- **Cybersecurity**: Unauthorized access, data breaches
- **Integration**: Interface failures with other systems
- **Environment**: Temperature, humidity, electromagnetic interference
- **Misuse**: User errors, incorrect usage

**Documentation Example**
```
HAZARD: Glucose reading displays as zero
SOURCE: Software rounding error in certain glucose ranges
SEVERITY: Critical (patient might give incorrect dose)
PROBABILITY: Occasional (happens 1% of readings)
```

### Step 2: Hazardous Situation Definition

**For Each Hazard, Define**
- Who is exposed? (patient, user, caregiver)
- When does it occur? (during use, setup, maintenance)
- How is patient harmed? (step-by-step pathway)
- What conditions enable it? (specific glucose ranges, user actions)

**Example**
```
HAZARD: Glucose reading displays as zero
HAZARDOUS SITUATION: Patient receives reading of 0 mg/dL when actual >200
HARM PATHWAY: 
1. Reading displays incorrectly
2. User sees zero and doesn't give insulin
3. Patient's blood sugar remains high
4. Extended hyperglycemia causes complications
```

### Step 3: Probability and Severity Assessment

**Probability Scale**
- **Frequent (5)**: Occurs regularly, multiple times per year
- **Probable (4)**: Occurs occasionally, few times per year
- **Occasional (3)**: Might occur, rare occurrences
- **Remote (2)**: Unlikely to occur
- **Extremely Remote (1)**: Very unlikely, once per many years

**Severity Scale (Impact if Harm Occurs)**
- **Critical (D)**: Death or permanent serious injury
- **Major (C)**: Serious injury or illness
- **Moderate (B)**: Temporary injury or illness
- **Minor (A)**: Minimal injury, treatable

**Risk Matrix**
```
         Frequent(5) Probable(4) Occasional(3) Remote(2) Extremely Remote(1)
Critical(D)   25        20           15          10              5
Major(C)      20        16           12           8              4
Moderate(B)   15        12            9           6              3
Minor(A)      10         8            6           4              2
```

**Assessment for Our Example**
- Probability: Occasional (3) - happens in ~1% of readings
- Severity: Critical (D) - could cause patient harm
- Risk Score: 15 (HIGH RISK - needs control)

### Step 4: Risk Control Selection

**Control Strategies (In Order of Preference)**
1. **Eliminate**: Remove the hazard entirely
2. **Design Change**: Redesign to minimize hazard
3. **Protective Feature**: Add safety feature
4. **Warning/Training**: Alert user to hazard

**For Our Example - Possible Controls**
```
Control 1: Algorithm improvement
- Use higher precision floating point calculations
- More robust rounding algorithm
- Reduces probability: Occasional(3) → Remote(2)
- Residual Risk: 10 (still needs more controls)

Control 2: Display validation
- Check for unreasonable values (zero when not expected)
- Display warning if value seems wrong
- Ask user to confirm
- Reduces probability further: Remote(2) → Extremely Remote(1)
- Residual Risk: 5 (ACCEPTABLE)

Control 3: User training
- Train user to verify readings seem reasonable
- Verify multiple readings if suspicious
- Reduces impact of error if not caught otherwise
```

**Selected Controls**
- Primary: Improved algorithm + validation
- Secondary: User confirmation requirement
- Tertiary: Training in device manual

### Step 5: Verification of Controls

**For Each Control, Define Test**

**Control: Improved Algorithm**
```
Test Procedure:
1. Calculate glucose for all readings 0-600
2. Compare with reference values
3. Verify no calculation errors
4. Verify no rounding errors at boundaries
5. Test edge cases: 0, 100, 200, 300, 500, 600

Acceptance Criteria:
- All calculations within ±5 mg/dL of reference
- No zero values when input > 0
- 100% accuracy required

Result: PASS
Evidence: Test report MDS-TEST-001-v1.0
```

**Control: Display Validation**
```
Test Procedure:
1. Test with valid readings (should display normally)
2. Test with zero when actual value > 0 (should show warning)
3. Test with extreme values (>600, should show warning)
4. Test user confirmation requirement

Acceptance Criteria:
- Warning displays for unreasonable values
- User must confirm before proceeding
- Confirmed values logged

Result: PASS
Evidence: Test report MDS-TEST-002-v1.0
```

### Step 6: Residual Risk Assessment

**After Controls Implemented**

**Recalculate Risk**
```
Original Risk:
- Probability: Occasional (3)
- Severity: Critical (D)
- Risk Score: 15

After Control 1 (Algorithm):
- Probability: Remote (2)
- Severity: Critical (D)
- Risk Score: 10

After Control 2 (Validation):
- Probability: Extremely Remote (1)
- Severity: Critical (D)
- Risk Score: 5

Is Residual Risk Acceptable?
- Risk Score 5 is LOW RISK
- Executive decision: YES, acceptable
- Risk-benefit analysis: Device benefit > residual risk
```

### Step 7: Documentation and Sign-Off

**Risk Management Report Should Include**
- Hazard identification (all hazards listed)
- Risk analysis (probability, severity, score)
- Risk control strategies
- Verification of controls (test results)
- Residual risk assessment
- Risk-benefit analysis
- Management approval

**Sign-Off**
- Engineering manager: _________________ Date: _______
- Quality assurance: _________________ Date: _______
- Clinical/regulatory: _________________ Date: _______
- Executive: _________________ Date: _______

## Integration with Other Activities

### Link to Design Controls
```
HAZARD → RISK CONTROL → DESIGN REQUIREMENT → DESIGN ELEMENT → TEST
```

**Example**
```
H1: Incorrect dose calculation
↓
RC1: Validate algorithm
↓
REQ-001: Calculate dose accurately
↓
DESIGN: Algorithm with validation
↓
TEST: Boundary value testing for all dose ranges
```

### Link to Traceability Matrix
- Hazard → Risk Control
- Risk Control → Design Requirement
- Design Requirement → Design Element
- Design Element → Code
- Code → Test

## Post-Market Risk Management

### Monitoring Controls Effectiveness
- Collect complaints related to each hazard
- Trend analysis: Is control still effective?
- Compare expected vs. actual complaint rates
- Document monitoring results

### New Hazard Discovery
- Monitor for previously unknown hazards
- Regulatory alerts, competitive devices
- Safety literature
- If new hazard found: Update risk analysis
- Implement new controls if needed
- Report to FDA if serious

### Design Changes and Risk
- Every design change needs risk assessment
- Could new change introduce new hazards?
- Does change affect any existing controls?
- Update risk management documentation

## Common Mistakes in Risk Analysis

1. **Incomplete Hazard List**: Missing software-specific hazards
2. **Unrealistic Probability**: Underestimating likelihood
3. **Weak Controls**: Controls that don't actually reduce risk
4. **No Verification**: Controls implemented but not tested
5. **Inadequate Documentation**: Risk analysis not clearly recorded
6. **No Post-Market Review**: Risk management stops at approval
7. **Controls Too Expensive**: Impractical to implement
8. **No Executive Ownership**: Management doesn't understand risks
9. **Inconsistent Risk Scoring**: Subjective and not standardized
10. **Poor Traceability**: Risk not linked to design and testing

## Tips for Successful Risk Management

1. **Diverse Team**: Include engineers, clinicians, users
2. **Historical Data**: Learn from similar devices
3. **Conservative Estimates**: Overestimate probability initially
4. **Multiple Controls**: Don't rely on single control
5. **Document Everything**: Detailed notes of discussions
6. **Regular Review**: Risk analysis not one-time activity
7. **Executive Engagement**: Clear ownership and approval
8. **Regulatory Alignment**: Know FDA expectations
9. **Clinical Perspective**: Understand real-world usage
10. **Continuous Improvement**: Learn from complaints

## Pre-Submission Checklist

- [ ] Hazard identification complete
- [ ] All hazards assessed for probability and severity
- [ ] Risk scoring performed
- [ ] Controls designed and selected
- [ ] Controls verified by testing
- [ ] Residual risk acceptable
- [ ] Risk management report complete
- [ ] Management sign-off obtained
- [ ] Linked to design and testing
- [ ] Traceability matrix includes risk links
