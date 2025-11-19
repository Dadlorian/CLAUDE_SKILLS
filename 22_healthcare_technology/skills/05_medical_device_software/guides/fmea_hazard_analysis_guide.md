# FMEA and Hazard Analysis Guide

## Overview

Failure Mode and Effects Analysis (FMEA) is systematic method for identifying potential failures and their effects. Essential for ISO 14971 risk management and IEC 62304 software hazard analysis.

## FMEA Types

### Design FMEA (dFMEA)
- Focus: Design deficiencies
- When: During design phase
- Purpose: Identify design-related failures

### Process FMEA (pFMEA)
- Focus: Manufacturing/process failures
- When: During production planning
- Purpose: Identify process-related failures

### Software FMEA
- Focus: Software failures
- When: Throughout software development
- Purpose: Identify software hazards

## FMEA Process

### Step 1: Assemble Team

**Team Members:**
- Design engineers
- Software developers
- Systems engineers
- Clinical/domain experts
- Risk management lead
- Quality assurance

**Team facilitator** guides process

### Step 2: Define Scope

**Define:**
- Device or system being analyzed
- Boundaries of analysis
- Level of detail (system, subsystem, component)
- Lifecycle phase (use, maintenance, disposal)

### Step 3: Identify Functions

**List all functions device performs:**
```markdown
# Device Functions

1. Measure blood glucose
2. Calculate insulin dose
3. Deliver insulin
4. Display data to user
5. Store treatment history
6. Communicate with EMR
7. Alarm on fault conditions
8. Provide user authentication
```

### Step 4: Identify Failure Modes

**For each function, ask: "How could this fail?"**

**Example - Function: Calculate insulin dose**

Failure Modes:
- Calculation incorrect (too high)
- Calculation incorrect (too low)
- Calculation not completed
- Calculation delayed
- Wrong patient data used
- Calculation based on corrupted data

### Step 5: Identify Effects

**For each failure mode: "What happens if this failure occurs?"**

**Example - Failure Mode: Calculation incorrect (too high)**

Effects:
- Excessive insulin delivered
- Patient hypoglycemia
- Patient unconsciousness
- Brain damage
- Death

**Note immediate effect AND ultimate effect**

### Step 6: Assign Severity

**Severity Rating (1-10):**
```
10 = Hazardous (death)
9 = Serious (permanent severe injury)
8 = Very high (serious injury)
7 = High (serious injury, reversible)
6 = Moderate (moderate injury requiring medical intervention)
5 = Low (moderate injury, temporary)
4 = Very low (minor injury requiring medical intervention)
3 = Minor (minor injury, no medical intervention)
2 = Very minor (inconvenience)
1 = None (no effect)
```

**Example:**
- Excessive insulin → Death → **Severity = 10**

### Step 7: Identify Causes

**For each failure mode: "What could cause this?"**

**Example - Failure Mode: Calculation incorrect (too high)**

Causes:
- Algorithm logic error
- Arithmetic overflow
- Wrong formula used
- Input data error
- Timing error in calculation
- Memory corruption

### Step 8: Assign Occurrence

**Occurrence Rating (1-10):**
```
10 = Very high (≥1 in 2)
9 = Very high (1 in 3)
8 = High (1 in 8)
7 = High (1 in 20)
6 = Moderate (1 in 80)
5 = Moderate (1 in 400)
4 = Low (1 in 2,000)
3 = Low (1 in 15,000)
2 = Remote (1 in 150,000)
1 = Nearly impossible (≤1 in 1,500,000)
```

**Base on:**
- Historical data
- Industry data
- Expert judgment
- Testing results

**Example:**
- Algorithm logic error after extensive testing → **Occurrence = 3**

### Step 9: Identify Current Controls

**What prevents or detects this failure?**

Prevention Controls:
- Code review
- Unit testing
- Integration testing
- Static analysis
- Algorithm validation

Detection Controls:
- Dose limit checks
- Range checking
- Self-test
- Alarms

### Step 10: Assign Detection

**Detection Rating (1-10):**
```
10 = Absolute uncertainty (no detection)
9 = Very remote (very remote chance)
8 = Remote (remote chance)
7 = Very low (very low chance)
6 = Low (low chance)
5 = Moderate (moderate chance)
4 = Moderately high (moderately high chance)
3 = High (high chance)
2 = Very high (very high chance)
1 = Almost certain (controls almost certain to detect)
```

**Example:**
- Dose limit check will detect excessive dose → **Detection = 2**

### Step 11: Calculate RPN

**RPN (Risk Priority Number) = Severity × Occurrence × Detection**

**Example:**
```
Severity: 10
Occurrence: 3
Detection: 2
RPN = 10 × 3 × 2 = 60
```

### Step 12: Prioritize and Take Action

**Prioritization:**
- High RPN (>100): Immediate action
- Medium RPN (50-100): Action required
- Low RPN (<50): Monitor

**For high-priority items:**
1. Identify risk reduction actions
2. Assign responsibility
3. Set target completion date
4. Implement actions
5. Re-evaluate RPN

## FMEA Table Template

| Function | Failure Mode | Effects | Sev | Causes | Occ | Current Controls | Det | RPN | Actions | Resp | Date | New RPN |
|----------|--------------|---------|-----|--------|-----|-----------------|-----|-----|---------|------|------|---------|
| Calculate dose | Calculation too high | Patient death | 10 | Algorithm error | 3 | Code review, testing, dose limits | 2 | 60 | Add redundant calculation check | J.Smith | Q2 | 20 |

## Software FMEA Specifics

### Software-Specific Failure Modes

**Logic Errors:**
- Incorrect algorithm
- Wrong formula
- Logic flaw
- Edge case not handled

**Data Errors:**
- Data corruption
- Wrong data used
- Data overflow/underflow
- Type mismatch

**Timing Errors:**
- Deadlock
- Race condition
- Timeout
- Synchronization error

**Interface Errors:**
- Wrong interface called
- Parameters incorrect
- Return value ignored
- Protocol violation

**Resource Errors:**
- Memory leak
- Buffer overflow
- Stack overflow
- Resource exhaustion

**Integration Errors:**
- Component mismatch
- Version incompatibility
- Configuration error

### Software-Specific Causes

- Specification error
- Design flaw
- Coding error
- Compiler bug
- SOUP anomaly
- Configuration error
- User input error
- Environmental condition

### Software-Specific Controls

**Prevention:**
- Requirements review
- Design review
- Code review
- Pair programming
- Static analysis
- Adherence to coding standards

**Detection:**
- Unit testing
- Integration testing
- System testing
- Boundary testing
- Fault injection
- Assertions
- Exception handling
- Watchdog timers

## Integration with ISO 14971

### FMEA Supports Risk Analysis

**FMEA provides:**
1. Hazard identification
2. Failure mode analysis
3. Severity assessment
4. Cause identification

**Use FMEA to populate Risk Register:**

```
Hazard: H-010 - Insulin overdose
Hazardous Situation: Excessive insulin delivered
Harm: Death from hypoglycemia
Severity: 10 (Catastrophic)
Probability: Based on FMEA occurrence
Risk: Severity × Probability
```

### Risk Controls from FMEA

**FMEA actions become risk controls:**

FMEA Action: Add redundant dose calculation
    ↓
Risk Control: RC-010 - Independent dose verification
    ↓
Software Requirement: SRS-150 - Verify dose with secondary algorithm
    ↓
Design Implementation
    ↓
Verification: TC-200 - Test independent verification

## Preliminary Hazard Analysis (PHA)

### Early Lifecycle Analysis

**PHA conducted before detailed FMEA:**
- Conceptual/early design phase
- High-level hazard identification
- Guides detailed analysis

### PHA Template

| Hazard | Hazardous Situation | Potential Causes | Effects | Initial Risk | Mitigation |
|--------|-------------------|------------------|---------|-------------|-----------|
| Software error | Wrong treatment delivered | Algorithm flaw | Patient harm | High | Extensive V&V, dose limits |

### PHA vs. FMEA

**PHA:**
- Early, high-level
- Qualitative
- Identifies major hazards

**FMEA:**
- Detailed, comprehensive
- Quantitative (RPN)
- Systematic analysis of all failure modes

## FMEA Documentation

### FMEA Report Structure

```markdown
# FMEA Report

## 1. Introduction
- Device description
- FMEA scope
- Team members
- Date conducted

## 2. FMEA Methodology
- FMEA type (Design/Process/Software)
- Severity/Occurrence/Detection scales
- RPN calculation

## 3. FMEA Results
[FMEA table]

## 4. High-Priority Issues
Summary of RPN > 100

## 5. Action Plan
| Action | Responsibility | Target Date | Status |
|--------|---------------|------------|--------|

## 6. Risk Reduction Results
[Show before/after RPN]

## 7. Conclusions

## 8. Approvals
```

### Maintaining FMEA

**Update FMEA when:**
- Design changes
- New failure modes identified
- Field data reveals issues
- Risk controls implemented
- Post-market surveillance finds problems

**Version Control:**
- FMEA versioned like other documents
- Change history maintained
- Previous versions archived

## FMEA Tools

### Software Tools

**Specialized:**
- ReliaSoft XFMEA
- IHS FMEA
- Sphera FMEA

**General:**
- Excel/Google Sheets (adequate for small projects)
- Requirements management tools (Jama, DOORS)

### Automation

**Can automate:**
- RPN calculation
- Prioritization/sorting
- Reports
- Tracking action items

## Best Practices

1. **Cross-Functional Team**: Include diverse expertise
2. **Facilitate Well**: Use experienced facilitator
3. **Be Systematic**: Cover all functions, all failure modes
4. **Be Realistic**: Use data when available
5. **Document Assumptions**: Record basis for ratings
6. **Focus on High RPN**: Prioritize risk reduction
7. **Re-Evaluate**: Assess RPN after risk controls
8. **Integrate with Risk Management**: Feed ISO 14971 process
9. **Keep Updated**: Living document throughout lifecycle
10. **Learn from Field**: Update with post-market data

## Common Mistakes

1. **Superficial Analysis**: Not thorough enough
2. **Wrong Team**: Missing key expertise
3. **No Action**: FMEA done but no follow-up
4. **Arbitrary Ratings**: No data or rationale
5. **One-Time Activity**: Not updated with changes
6. **Not Integrated**: Separate from risk management

---

**Key Takeaway**: FMEA is systematic method for hazard identification and risk assessment. Integrate with ISO 14971 risk management. Focus on high RPN items. Maintain throughout lifecycle. Use cross-functional team. Document thoroughly.
