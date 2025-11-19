# Software Safety Classification Reference

## Overview

Software safety classification determines the rigor of software development, documentation, and testing required for medical device software. This reference covers classification under IEC 62304, FDA guidance, and EU MDR.

## IEC 62304 Software Safety Classes

### Class A: No Injury or Damage to Health Possible

**Definition:**
Software item whose failure or malfunction cannot result in:
- Injury to patient, operator, or others
- Damage to health of patient, operator, or others

**Characteristics:**
- Minimal patient safety impact
- Typically administrative or non-critical functions
- No direct involvement in diagnosis or treatment

**Examples:**
- Administrative login to device (not controlling device function)
- Non-safety-related data logging
- Cosmetic user interface elements
- Informational displays without clinical significance
- Device usage statistics collection

**Development Requirements:**
- Basic software development plan
- High-level requirements documentation
- Minimal verification and validation
- Basic configuration management
- No specific unit testing requirements
- No specific code coverage requirements

**Documentation Level:**
- Minimal but traceable
- Focus on change control

### Class B: Non-Serious Injury Possible

**Definition:**
Software item whose failure or malfunction can result in:
- Non-serious injury to patient, operator, or others
- Non-serious damage to health

**Characteristics:**
- Moderate patient safety impact
- Could affect diagnosis or treatment but limited consequences
- Errors would likely be detected and corrected

**Examples:**
- Diagnostic imaging display software (viewing only)
- Patient data entry and display
- Non-critical physiological monitoring
- Laboratory information display
- PACS viewing workstations
- Non-invasive patient monitoring alarms
- Device calibration software with verification
- Trending displays for non-critical parameters

**Development Requirements:**
- Detailed software development plan with standards
- Complete software requirements specification
- Software architecture design required
- Detailed design required
- Unit testing OR code review required
- Integration testing required
- System testing against all requirements
- Configuration management
- Problem resolution process
- Verification of architecture and design

**Documentation Level:**
- Comprehensive documentation required
- Traceability matrices required
- Design review records

### Class C: Death or Serious Injury Possible

**Definition:**
Software item whose failure or malfunction can result in:
- Death of patient, operator, or others
- Serious injury to patient, operator, or others
- Serious damage to health

**Characteristics:**
- High patient safety impact
- Direct control of critical functions
- Errors could be undetected or uncorrectable
- Failure leads to severe consequences

**Examples:**
- Insulin pump dosing algorithms
- Ventilator control software
- Radiation therapy treatment planning and delivery
- Surgical robot control software
- Implantable cardioverter defibrillator software
- Anesthesia delivery systems
- Hemodialysis machine control
- Critical care patient monitors with automated intervention
- Blood glucose control algorithms
- Medication dosing calculators
- Closed-loop physiologic control systems

**Development Requirements:**
- Comprehensive software development plan with rigorous standards (e.g., MISRA C)
- Detailed software requirements specification with safety requirements
- Software architecture design with safety analysis
- Detailed design specification required
- Unit testing with code coverage required:
  - 100% statement coverage OR
  - 100% branch coverage
  - May require MC/DC for critical functions
- Comprehensive code review
- Integration testing with comprehensive test cases
- System testing against all requirements
- Rigorous configuration management
- Formal problem resolution process
- Architecture and detailed design verification
- Static analysis tools
- Dynamic analysis
- Security testing

**Documentation Level:**
- Extensive documentation required
- Complete traceability matrices
- Detailed design review records
- Test coverage analysis reports
- Code review records
- Static analysis reports

## Classification Process

### Step 1: Identify Software Items

Break software into functional items/components:
- Individual modules
- Libraries
- SOUP components
- Algorithms
- User interface components

### Step 2: Conduct Hazard Analysis

For each software item, identify:
- Potential failure modes
- Effects of failures
- Contribution to hazardous situations
- Severity of potential harm

### Step 3: Determine Worst-Case Class

**Classification Rule:**
"The software item shall be assigned the highest software safety class of the software items it contains."

**Example:**
If system contains:
- Class A logging function
- Class B display function
- Class C control algorithm

**Entire system is Class C** (can partition if items are segregated)

### Step 4: Document Classification

**Required Documentation:**
- Hazard analysis results
- Severity assessment for each failure mode
- Classification justification for each software item
- System-level classification
- Rationale for classification decisions

### Step 5: Review and Approve

- Independent review of classification
- Risk management team approval
- Quality assurance sign-off

## FDA Level of Concern

### Major Level of Concern

**Definition:**
Failure or latent flaw could directly result in death or serious injury to:
- Patient
- Operator
- Others

**Examples:**
- Blood bank software controlling donor compatibility
- Infusion pump drug libraries
- Radiation therapy planning systems
- Physiologic closed-loop controllers
- Surgical navigation systems

**Documentation Requirements:**
- Extensive (see FDA guidance reference)
- Most rigorous testing and validation
- Comprehensive traceability

### Moderate Level of Concern

**Definition:**
Failure or latent flaw could directly result in minor injury to:
- Patient
- Operator
- Others

**Examples:**
- PACS workstations
- Digital imaging and display
- Patient monitors (non-critical)
- Laboratory analyzers
- Dental imaging software

**Documentation Requirements:**
- Moderate documentation
- System-level testing
- Traceability matrix

### Minor Level of Concern

**Definition:**
Failure or latent flaw is unlikely to result in injury to:
- Patient
- Operator
- Others

**Examples:**
- Clinical communication tools
- Administrative hospital systems
- Appointment scheduling
- Billing systems interfacing with medical devices

**Documentation Requirements:**
- Basic documentation
- High-level requirements
- Validation testing

## EU MDR Software Classification

### Rule 11: Software as Medical Device

**Class IIa:**
Software intended to provide information for decisions with diagnosis/treatment purposes

**Class IIb:**
Software intended to monitor physiological processes

**Class III:**
Software intended to control physiological processes or diagnosis/monitoring of vital signs where nature of variations could lead to immediate danger

**Exceptions:**
Software for general purposes (not medical device)
Software for lifestyle and wellbeing (not medical device)

## Hybrid Classifications

### System with Mixed Classes

**Segregation Strategy:**
If software items can be properly segregated:
- Develop each according to its class
- Document segregation mechanisms
- Verify segregation effectiveness

**Example:**
Ventilator software:
- Class C: Breath control algorithm
- Class B: Display and trending
- Class A: Usage statistics

**Segregation Requirements:**
- Independent modules
- Well-defined interfaces
- No Class C functionality dependent on Class A/B
- Failure of lower class doesn't affect higher class

## Classification Decision Factors

### Severity Assessment Factors

1. **Direct vs. Indirect Impact**
   - Direct: Software controls therapy
   - Indirect: Software informs decision

2. **Detectability**
   - Easily detected errors = lower class
   - Latent or undetectable = higher class

3. **Reversibility**
   - Easily reversed = lower class
   - Irreversible harm = higher class

4. **Dependency**
   - Alternative methods available = lower class
   - Sole source of information = higher class

5. **Time Criticality**
   - Delayed detection acceptable = lower class
   - Immediate detection required = higher class

### Common Classification Scenarios

**Scenario 1: Diagnostic Software**
- Class B if provides information for healthcare professional review
- Class C if used for immediate treatment decisions in critical situations

**Scenario 2: Monitoring Software**
- Class B if monitors non-critical parameters with HCP oversight
- Class C if monitors critical parameters with automated actions

**Scenario 3: Calculation Software**
- Class B if calculations are manually verified
- Class C if calculations directly control therapy

**Scenario 4: Data Display**
- Class A if purely informational, no clinical use
- Class B if used for clinical assessment
- Class C if used for immediate critical decisions

## Special Considerations

### SOUP (Software of Unknown Provenance) Classification

SOUP inherits classification of system where it's used:
- If used in Class C system, SOUP managed as Class C
- Requires thorough evaluation regardless of vendor's classification

### Artificial Intelligence/Machine Learning

**Classification Factors:**
- Autonomy of decision-making
- Clinical significance of output
- Transparency and explainability
- Ability for healthcare professional override

**Tendency:** Often Class B or C due to:
- Complexity
- Potential for unexpected behavior
- Difficulty in validation

### Mobile Medical Apps

Follow same classification rules:
- Accessory to Class III device = often Class III
- Standalone diagnostic tool = typically Class II (IIa/IIb)
- Informational = may be Class I or not a device

### Software Updates

**Major Updates:**
- Reconsider classification
- New features may change class
- Enhanced risk may require reclassification

**Minor Updates:**
- Maintain existing classification
- Document impact analysis
- Verify classification still appropriate

## Classification Documentation Template

```markdown
# Software Safety Classification

## Device Information
- Device Name:
- Software Version:
- Classification Date:

## Hazard Analysis Summary
[Link to detailed hazard analysis]

## Software Item Classifications

| Software Item | Failure Modes | Potential Harm | Severity | Class | Rationale |
|---------------|---------------|----------------|----------|-------|-----------|
| Control Module | Logic error | Patient death | Critical | C | Direct therapy control |
| Display Module | Incorrect data | Delayed treatment | Serious | B | Informs decisions |
| Logging Module | Lost data | No patient impact | None | A | Administrative only |

## System Classification
**Overall Classification:** Class C

**Justification:**
System classified as Class C based on Control Module. Although system contains Class A and B items, the presence of Class C item requires highest classification unless items are properly segregated.

## Segregation Analysis
[If applicable, describe segregation mechanisms]

## Approval
- Risk Management Lead:
- Software Development Lead:
- Quality Assurance:
- Date:
```

## Common Classification Errors

1. **Under-Classification**
   - Not considering all failure modes
   - Assuming errors will be caught
   - Not considering worst-case scenarios

2. **Over-Classification**
   - Not considering mitigating controls
   - Classifying based on general device class
   - Not considering detectability

3. **Inconsistent Classification**
   - Different items with similar risk classified differently
   - Classification changes without justification

4. **Inadequate Documentation**
   - Classification stated without rationale
   - Hazard analysis incomplete
   - Traceability to risk analysis missing

## Best Practices

1. **Start Conservative:** When uncertain, classify higher
2. **Document Rationale:** Clear justification for all decisions
3. **Independent Review:** Have classification reviewed by risk management
4. **Consider All Modes:** Include user errors, environmental factors, timing
5. **Update Regularly:** Revisit classification with each major change
6. **Link to Risk Analysis:** Classification should follow from ISO 14971 risk analysis
7. **Regulatory Alignment:** Consider both IEC 62304 and jurisdiction-specific requirements
8. **Team Involvement:** Include clinical, regulatory, quality in classification
9. **Trace to Requirements:** Classification influences requirements and testing
10. **Maintain Records:** Keep classification decision history

## Regulatory Expectations

### FDA
- Expect Level of Concern determination in 510(k)
- Must justify classification with hazard analysis
- Higher concern = more rigorous documentation

### EU Notified Bodies
- Software classification per Rule 11
- Must align with IEC 62304 class
- Clinical evaluation depth depends on classification

### Other Jurisdictions
- Health Canada: Similar to FDA
- PMDA (Japan): Adopts IEC 62304
- TGA (Australia): Risk-based approach

---

**Key Takeaway**: Proper software safety classification is the foundation of compliant development. Under-classification leads to inadequate controls; over-classification wastes resources. Base classification on rigorous hazard analysis and document thoroughly.
