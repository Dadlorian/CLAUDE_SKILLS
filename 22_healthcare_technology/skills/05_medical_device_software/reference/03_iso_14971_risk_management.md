# ISO 14971 Risk Management Reference

## Standard Overview

ISO 14971 establishes the lifecycle approach to managing risk in medical devices. Risk management includes identification of hazards, estimation of risk, risk control, and evaluation of residual risk.

## Risk Terminology

### Hazard
- Potential source of harm
- Physical characteristic or property that can cause harm
- Example: Software calculates incorrect dose → hazard

### Hazardous Situation
- Circumstance in which exposure to hazard can occur
- Example: User receives incorrect dose because of software calculation

### Harm
- Injury or adverse health effect
- Can be physical, psychological, or social
- Example: Overdose leading to organ damage

### Risk
- Combination of probability and severity of harm
- Risk = Probability × Severity
- Example: Incorrect dose 1% of time with 20% chance of serious harm

### Risk Control
- Measures taken to reduce risk to acceptable level
- Can be design changes, protective equipment, training
- Example: Algorithm validation, user verification of dose

## Risk Management Process

### 1. Risk Analysis

#### Hazard Identification
- Brainstorm possible hazards
- Use historical data from similar devices
- Consider user errors and environmental factors
- Think about software-specific hazards
- Document each hazard clearly

#### Hazardous Situation Definition
- Specify circumstances where hazard occurs
- Who is affected (patient, user, bystander)
- What operating conditions exist
- When in device lifecycle does it occur
- Example: "Patient receives overdose when user doesn't verify calculated dose"

#### Harm Assessment
- Describe potential harm in detail
- Severity: Death, serious injury, minor injury, negligible
- Number of people potentially affected
- Duration and reversibility of harm
- Example: "Overdose causes cardiac arrhythmia (serious injury)"

#### Probability Estimation
- How likely is hazardous situation?
- How likely does hazardous situation cause harm?
- Consider: Frequency of use, likelihood of failure, detectability
- Classes: Frequent, Probable, Occasional, Remote, Extremely Remote
- Document sources for estimates

#### Initial Risk Evaluation
- Risk = Severity × Probability matrix
- Severity: Critical (D), Major (C), Moderate (B), Minor (A)
- Probability: Frequent (5), Probable (4), Occasional (3), Remote (2), Extremely Remote (1)
- Calculate risk score (1-25)

### 2. Risk Evaluation

#### Acceptable Risk Determination
- Define what risks are acceptable
- Governance: Executive leadership approval
- Consider: Benefit vs. risk, patient population, alternatives
- Establish decision criteria
- Document rationale

#### High-Risk Hazards
- Risk > 15 (typical threshold): Unacceptable without controls
- Risk 9-15: Likely needs controls
- Risk < 9: May be acceptable as-is
- Executive review for any high-risk hazards

### 3. Risk Control

#### Control Option Selection
- Design changes (eliminate hazard)
- Protective measures (reduce impact)
- Information (labels, training, warnings)
- Combination approaches

#### Control Design
- Specify what control does
- How it reduces risk
- Who implements it
- Requirements for implementation
- Example: "Software validates dose calculation; if >10% above normal, displays warning for user confirmation"

#### Control Verification
- Plan test to verify control works
- Who will do testing
- Acceptance criteria
- Document results

#### Residual Risk Evaluation
- Risk after control is implemented
- Verify risk reduced to acceptable level
- Example: "With user confirmation requirement, probability drops from 1% to 0.1%, making risk acceptable"

#### Risk-Benefit Analysis
- Are benefits of device greater than residual risks?
- What is patient benefit?
- What are alternatives?
- Is overall benefit acceptable?

### 4. Risk Management Report

- List all identified hazards
- Risk analysis for each hazard
- Risk evaluation rationale
- Risk controls implemented
- Verification of controls
- Residual risk assessment
- Post-market surveillance plan
- Management sign-off

## Software-Specific Hazards

### Data Integrity
- **Hazard**: Corrupted patient data
- **Source**: Memory errors, transmission failures
- **Control**: Checksums, parity checking, redundant storage

### Algorithm Errors
- **Hazard**: Incorrect calculation
- **Source**: Design flaw, rounding error, boundary condition
- **Control**: Algorithm validation, extensive testing

### User Interface
- **Hazard**: User selects wrong option
- **Source**: Confusing interface design
- **Control**: Clear labeling, confirmation dialogs, training

### Network Security
- **Hazard**: Unauthorized data access
- **Source**: Weak authentication, unencrypted transmission
- **Control**: Strong cryptography, access controls

### Software Updates
- **Hazard**: Update causes system failure
- **Source**: Inadequate testing, incompatibility
- **Control**: Staged rollout, rollback capability

### Third-Party Components
- **Hazard**: Vulnerability in library code
- **Source**: Unpatched dependencies
- **Control**: Dependency scanning, patch management

## Risk Management Documentation

### Hazard Analysis Table
| ID | Hazard | Hazardous Situation | Harm | Probability | Severity | Risk | Control | Residual Risk |
|----|--------|-------------------|------|-------------|----------|------|---------|---------------|
| H001 | Dose calculation error | User doesn't verify result | Overdose | Occasional (3) | Critical (D) | 15 | Algorithm validation | Rare (1) |

### Traceability Matrix
- Each hazard traced to:
  - Software requirement addressing hazard
  - Design element implementing requirement
  - Test verifying control effectiveness
  - Verification report with results

### Change Management Integration
- Risk assessment for each design change
- Verification that change doesn't introduce new hazards
- Assessment that change doesn't increase residual risk
- Post-change testing and documentation

## Risk-Based Test Planning

### High-Risk Areas (Risk > 15)
- Extensive testing required
- Multiple test approaches
- Stress testing, edge cases
- Real-world scenario testing
- Independent verification
- Example coverage: >95%

### Medium-Risk Areas (Risk 9-15)
- Comprehensive testing
- Multiple approaches
- Standard test cases
- Edge case coverage
- Example coverage: >80%

### Low-Risk Areas (Risk < 9)
- Focused testing
- Critical path coverage
- Example coverage: >50%
- May defer testing for non-critical paths

## Post-Market Risk Management

### Complaint Analysis
- Collect user complaints
- Classify by hazard involved
- Trend analysis: increasing frequency?
- Root cause analysis
- Determine if control is effective

### Control Effectiveness Monitoring
- Are controls working as designed?
- Evidence: complaint trends, usage patterns, field data
- If ineffective: design remediation
- Medical Device Report (MDR) if serious event

### New Hazard Identification
- Monitor for previously unknown hazards
- External safety alerts
- Competitive device issues
- Emerging technologies affecting risk

## Common Risk Management Mistakes

1. **Incomplete Hazard List**: Missing software-specific hazards
2. **Unrealistic Probability**: Underestimating how often hazards occur
3. **Weak Risk Controls**: Controls that don't actually reduce risk
4. **No Verification**: Controls implemented but not tested
5. **Weak Traceability**: Hazards not linked to requirements/tests
6. **Document Isolation**: Risk report not integrated with design/test docs
7. **User Error Ignored**: Assumption users won't make mistakes
8. **No Post-Market**: Risk management stops at approval
9. **Design Creep**: Risk analysis not updated with design changes
10. **Regulatory Justification**: Risk decisions made without clinical context

## Risk-Benefit Analysis Framework

### Patient Harm if Untreated
- Current disease progression
- Mortality and morbidity
- Quality of life impact

### Device Benefits
- Therapeutic benefit
- Diagnostic accuracy
- Life improvement

### Device Residual Risks
- Adverse events
- Inconvenience
- Cost

### Overall Assessment
- Benefit > Risk? Yes/No
- Executive decision documented
- Rationale clear and defensible

## Example: Infusion Pump Risk Analysis

### Hazard: Incorrect Flow Rate
- **Source**: Software calculation error or user input error
- **Harm**: Overdose or underdose → tissue damage, death
- **Probability**: Occasional (1 in 1000 uses)
- **Severity**: Critical (could be fatal)
- **Risk**: HIGH (15 points)

### Controls
1. **Algorithm validation**: Comprehensive testing of calculation
2. **User confirmation**: Display calculated rate for verification
3. **Limits checking**: Software prevents rates >150% of prescribed
4. **Redundancy**: Independent calculation with comparison

### Residual Risk Assessment
- With all controls: Risk drops to ACCEPTABLE (2 points)
- Probability reduced to remote (0.1 in 1000)
- Severity unchanged (critical if occurs)
- Controls verified by testing

### Verification
- Unit tests of algorithm
- Integration tests of calculation pipeline
- System tests with user scenarios
- 100 hours of stress testing
- All documented in V&V report
