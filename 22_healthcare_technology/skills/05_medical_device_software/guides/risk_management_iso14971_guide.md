# Risk Management ISO 14971 Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing ISO 14971 risk management for medical device software.

## Phase 1: Risk Management Planning

### Step 1: Create Risk Management Plan

**Template:**
```markdown
# Risk Management Plan

## Scope
- Device: [Name and description]
- Software Component: [If applicable]
- Lifecycle Phases: Design, Production, Post-Production

## Organization and Responsibilities
- Risk Management Lead: [Name]
- Team Members: [Names and roles]
- Competence Requirements: [Skills needed]

## Risk Acceptability Criteria
[Include risk matrix - see below]

## Risk Management Activities
- Risk Analysis: Throughout design
- Risk Evaluation: After each design phase
- Risk Control: Integrated into requirements
- Residual Risk Evaluation: Before release
- Post-Production: Continuous monitoring

## Review Process
- Reviews conducted at: [Milestones]
- Participants: [Roles]

## Verification Activities
- Risk control verification through testing

## Documentation
- Risk Management File location
- Update procedures
```

### Step 2: Define Risk Acceptability Matrix

**Example Matrix:**
```
Severity/Probability | Frequent | Probable | Occasional | Remote | Improbable
---------------------|----------|----------|------------|--------|------------
Catastrophic (Death) |    UR    |    UR    |     UR     |   UR   |     AR
Serious Injury       |    UR    |    UR    |     AR     |   AR   |     AL
Moderate Injury      |    UR    |    AR    |     AR     |   AL   |     AL
Negligible          |    AR    |    AR    |     AL     |   AL   |     AL

UR = Unacceptable (must reduce)
AR = ALARP required (reduce if practicable)
AL = Acceptable (broadly acceptable)
```

## Phase 2: Risk Analysis

### Step 1: Define Intended Use

**Document:**
- Intended medical indication
- Patient population (age, health status, conditions)
- Body part/tissues applied to
- User profile (doctors, nurses, technicians, patients)
- Use environment (hospital, clinic, home)
- Operating principles
- Lifetime of device

### Step 2: Identify Reasonably Foreseeable Misuse

**Consider:**
- User errors (wrong dose entered, wrong patient)
- Inadequate training
- Use beyond specified lifetime
- Use in wrong environment
- Off-label use
- Incorrect assembly/connection

### Step 3: Identify Hazards

**Use Systematic Methods:**

**Brainstorming:**
- Multidisciplinary team
- No idea dismissed initially
- Document all suggestions

**Preliminary Hazard Analysis (PHA):**
- High-level early analysis
- Guides detailed analysis

**FMEA (Failure Mode and Effects Analysis):**

**FMEA Process:**
```
1. List device functions
2. For each function:
   a. Identify failure modes
   b. Analyze effects
   c. Identify causes
   d. Assign Severity
   e. Assign Occurrence probability
   f. Identify current controls
   g. Assign Detection probability
   h. Calculate RPN = S × O × D
   i. Prioritize high RPNs
```

**FMEA Template:**
| Function | Failure Mode | Effects | Severity | Causes | Occurrence | Controls | Detection | RPN | Actions |
|----------|--------------|---------|----------|--------|------------|----------|-----------|-----|---------|
| Calculate dose | Incorrect calculation | Wrong dose delivered | 10 | Algorithm error | 3 | Code review, testing | 2 | 60 | Enhanced testing |

**Software-Specific Hazards:**
- Logic errors in algorithms
- Data corruption
- Interface errors
- Timing/synchronization issues
- User interface confusion
- Cybersecurity vulnerabilities
- SOUP component failures
- Memory leaks/overflow
- Race conditions

### Step 4: Estimate Risk

**For Each Hazardous Situation:**

**Severity Assessment:**
```
10 = Catastrophic (death)
8-9 = Serious (permanent injury)
5-7 = Moderate (temporary injury)
1-4 = Negligible (inconvenience)
```

**Probability Estimation:**

**Data Sources:**
- Literature
- Field data from similar devices
- Clinical studies
- Expert judgment
- Usability testing
- Laboratory testing

**Probability Levels:**
```
Frequent:     > 1 in 1,000      (>10^-3)
Probable:     1 in 1,000 to 10,000 (10^-3 to 10^-4)
Occasional:   1 in 10,000 to 100,000 (10^-4 to 10^-5)
Remote:       1 in 100,000 to 1M (10^-5 to 10^-6)
Improbable:   < 1 in 1,000,000  (<10^-6)
```

**Calculate Risk = Severity × Probability**

### Step 5: Document Risk Analysis

**Risk Register Template:**
| Hazard ID | Hazard | Hazardous Situation | Consequence | Severity | Probability | Risk Level | Acceptability |
|-----------|--------|---------------------|-------------|----------|-------------|------------|---------------|
| H-001 | Algorithm error | Wrong dose calculated | Patient overdose | 10 | 3 | 30 | UR |
| H-002 | Display error | Wrong data shown | Delayed treatment | 5 | 2 | 10 | AR |

## Phase 3: Risk Evaluation

### Step 1: Evaluate Each Risk

**Compare against acceptability criteria:**
- If AL (Acceptable): Document, no action required
- If AR (ALARP): Implement controls if practicable
- If UR (Unacceptable): Must implement controls

### Step 2: Document Evaluation

**For Each Risk:**
- Risk level
- Acceptability determination
- Rationale
- Actions required

## Phase 4: Risk Control

### Step 1: Select Risk Control Measures

**Hierarchy (in order of preference):**

**1. Inherent Safety by Design**
- Eliminate hazard completely
- Examples:
  - Use safer algorithm
  - Limit dose range
  - Add redundancy

**2. Protective Measures**
- Add safety features
- Examples:
  - Dose limit checks
  - Alarms and warnings
  - Automatic shutoffs
  - Interlocks
  - Confirmation dialogs

**3. Information for Safety**
- Warnings and instructions
- Examples:
  - User manual warnings
  - On-screen warnings
  - Training requirements
  - Contraindications

**Use Multiple Measures:**
- Often need combination
- Document why higher-level controls not feasible

### Step 2: Analyze Risk Controls for New Risks

**For Each Control:**
- Does it introduce new hazards?
- Does it affect other risks?
- Example: Confirmation dialog reduces wrong selection but adds workflow delay

**If New Risks:**
- Add to risk analysis
- Evaluate new risks
- Control if needed

### Step 3: Document Risk Controls

**Risk Control Table:**
| Hazard ID | Original Risk | Risk Control | Type | New Risk | Residual Risk | Residual Acceptability |
|-----------|---------------|--------------|------|----------|---------------|------------------------|
| H-001 | 30 (UR) | Dose range limits | Design | None | 6 (AL) | Acceptable |
| H-001 | 30 (UR) | Dose confirmation | Protective | Delay (minor) | 6 (AL) | Acceptable |
| H-001 | 30 (UR) | Warnings in manual | Information | None | 6 (AL) | Acceptable |

### Step 4: Implement Risk Controls

**In Software Requirements:**
- Each risk control becomes requirement
- Example: "Software shall limit dose to 100 units maximum" (from H-001 control)
- Trace hazard → control → requirement

**In Design:**
- Implement controls in architecture and code
- Document design decisions
- Review implementation

### Step 5: Verify Risk Control Implementation

**Verification Methods:**
- Testing
- Analysis
- Review
- Inspection

**Traceability:**
```
Hazard H-001 → Control: Dose limit
             → Requirement SRS-042: Max dose 100 units
             → Code: DoseController.setMaxDose(100)
             → Test TC-123: Verify dose limit enforced
             → Result: PASS
```

**Document:**
- Verification method
- Results
- Evidence
- Approval

## Phase 5: Residual Risk Evaluation

### Step 1: Evaluate Each Residual Risk

**After controls applied:**
- Re-assess severity and probability
- Calculate residual risk
- Compare to acceptability criteria

**Acceptable if:**
- Residual risk meets acceptability criteria OR
- Benefits outweigh residual risks OR
- Residual risks are ALARP (as low as reasonably practicable)

### Step 2: Overall Residual Risk Evaluation

**Consider:**
- All residual risks together
- Cumulative effect
- Risk-benefit balance
- Comparison to similar devices
- State of the art

**Document Decision:**
- Overall residual risk acceptable
- Justification
- Benefits analysis
- Approval

## Phase 6: Risk Management Review

### Conduct Review Before Release

**Review Team:**
- Risk management lead
- Development team
- Quality assurance
- Regulatory affairs
- Management

**Review Questions:**
- Was risk management plan followed?
- Are all identified hazards addressed?
- Are all risk controls verified?
- Is overall residual risk acceptable?
- Are production/post-production information collection methods in place?

**Document:**
- Review date
- Participants
- Findings
- Approval decision

## Phase 7: Production and Post-Production Information

### Step 1: Establish Information Collection

**Sources:**
- Complaint data
- Medical device reports
- Field corrective actions
- Returned products
- Literature and publications
- Similar device information

**Procedures:**
- Who collects information
- How often reviewed
- Criteria for action

### Step 2: Review Information

**Frequency:**
- Scheduled (quarterly, annually)
- Triggered by events

**Evaluate:**
- New hazards identified?
- Estimated risks still valid?
- Risk acceptability still valid?
- New information affecting overall risk?

### Step 3: Take Action if Needed

**If Issues Found:**
- Update risk analysis
- Implement new risk controls
- Issue field corrective action
- Notify regulators
- Notify users
- Update risk management file

## Risk Management File Contents

**Required Documents:**
1. Risk Management Plan
2. Hazard Identification Records
3. Risk Analysis (risk register)
4. Risk Evaluation Records
5. Risk Control Implementation Records
6. Risk Control Verification Records
7. Residual Risk Evaluation
8. Overall Risk Acceptability
9. Risk Management Review Records
10. Production/Post-Production Information Reviews

**Organization:**
- Chronological or by phase
- Cross-referenced
- Version controlled
- Part of Design History File

## Software-Specific Guidance

### Software Hazard Analysis (IEC 62304 Section 7)

**Integrated with ISO 14971:**
- Software hazards feed into overall risk analysis
- Software requirements include risk controls
- Software testing verifies risk controls

**Software Hazard Identification:**
- Specification errors
- Design flaws
- Coding errors
- Timing issues
- Data errors
- User interface issues
- Integration issues
- SOUP failures

### SOUP Risk Management

**For Each SOUP Item:**
- Identify known anomalies
- Assess safety impact
- Determine acceptability
- Monitor for updates
- Plan for obsolescence

## Templates and Checklists

### Hazard Identification Checklist
- [ ] Energy hazards considered
- [ ] Biological/chemical hazards considered
- [ ] Mechanical hazards considered
- [ ] Thermal hazards considered
- [ ] Software hazards considered
- [ ] Cybersecurity hazards considered
- [ ] Use errors considered
- [ ] Reasonably foreseeable misuse considered

### Risk Control Checklist
- [ ] Inherent safety explored
- [ ] Protective measures implemented
- [ ] Information for safety provided
- [ ] Multiple controls used for high risks
- [ ] New risks from controls analyzed
- [ ] All controls traced to requirements
- [ ] All controls verified

### Release Review Checklist
- [ ] Risk management plan followed
- [ ] All hazards identified and analyzed
- [ ] All risks evaluated
- [ ] All unacceptable risks controlled
- [ ] Residual risks acceptable
- [ ] Overall risk acceptable
- [ ] Benefits outweigh risks
- [ ] Post-market plan established

## Common Mistakes

**1. Risk Management as One-Time Activity**
- Solution: Continuous throughout lifecycle

**2. Unrealistic Probability Estimates**
- Solution: Use data when available, document assumptions

**3. Relying Only on Information for Safety**
- Solution: Design out hazards first, then add protective measures

**4. Not Considering Use Errors**
- Solution: Conduct usability testing, include human factors analysis

**5. Poor Documentation**
- Solution: Use templates, document rationale

**6. Not Updating for Changes**
- Solution: Risk analysis update mandatory for all changes

**7. No Post-Market Review**
- Solution: Schedule regular reviews, triggered reviews for events

---

**Key Takeaway**: ISO 14971 risk management is continuous, systematic, and documentation-intensive. Start early, involve multidisciplinary team, use structured methods, prefer design controls over warnings, verify everything, and update continuously with post-market data.
