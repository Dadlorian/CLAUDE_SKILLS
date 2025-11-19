# Design Controls Implementation Guide

## Overview
Design controls (21 CFR 820.30) ensure devices are designed using systematic, documented processes. This guide provides step-by-step implementation for software.

## Design Planning

### Create Design and Development Plan

**Template:**
```markdown
# Design and Development Plan

## Project Information
- Device: [Name]
- Regulatory Classification: Class II
- Target Markets: USA (FDA), EU (MDR)

## Design Phases
1. Requirements (Weeks 1-4)
2. Architecture Design (Weeks 5-8)
3. Detailed Design (Weeks 9-12)
4. Implementation (Weeks 13-24)
5. Integration (Weeks 25-28)
6. System Testing (Weeks 29-34)
7. Validation (Weeks 35-40)
8. Design Transfer (Weeks 41-42)

## Team Structure
- Project Lead: [Name]
- Software Lead: [Name]  
- Systems Engineer: [Name]
- Risk Management: [Name]
- Quality Assurance: [Name]
- Regulatory Affairs: [Name]

## Standards to Follow
- IEC 62304 for software lifecycle
- ISO 14971 for risk management
- IEC 62366 for usability
- Coding: MISRA C
- Testing: IEEE 829

## Design Reviews
- Requirements Review (Week 4)
- Architecture Review (Week 8)
- Detailed Design Review (Week 12)
- Integration Review (Week 28)
- Pre-Validation Review (Week 34)
- Final Design Review (Week 40)

## Verification Methods
- Code review (100% of code)
- Unit testing (100% branch coverage for Class C)
- Integration testing
- System testing (all requirements)
- Static analysis

## Documentation Deliverables
- Requirements Specification
- Design Specification
- Test Plans and Results
- Risk Management File
- Traceability Matrices
- Design History File
```

## Design Input

### Requirements Development Process

**Step 1: Gather User Needs**
- Interview users (clinicians, patients, technicians)
- Observe workflows
- Review similar devices
- Analyze complaints from existing devices

**Step 2: Define Intended Use**
```markdown
# Intended Use Statement

Device: InsulinPumpPro
Intended Use: Continuous subcutaneous insulin infusion for treatment of diabetes mellitus in persons requiring insulin.

Patient Population: Adults and pediatric patients (age 7+) with diabetes mellitus

User: Patient (self-administration) or caregiver

Environment: Home, clinic, hospital

Duration of Use: Continuous (device lifetime 4 years)
```

**Step 3: Create User Requirements**
| ID | User Need | Priority | Source |
|----|-----------|----------|--------|
| UN-001 | Deliver accurate insulin dose | Critical | Clinical requirement |
| UN-002 | Alert user to occlusion | Critical | Safety requirement |
| UN-003 | Easy to program | High | User interviews |

**Step 4: Derive System Requirements**
| ID | System Requirement | Trace to User Need | Verification Method |
|----|-------------------|-------------------|---------------------|
| SYS-001 | System shall deliver insulin ±5% accuracy | UN-001 | Testing |
| SYS-002 | System shall detect occlusions within 30 seconds | UN-002 | Testing |

**Step 5: Derive Software Requirements**
```markdown
# Software Requirements Specification

## Functional Requirements
SRS-001: Software shall calculate basal insulin dose per user profile
  Trace: SYS-001
  Verification: TC-001, TC-002

SRS-002: Software shall calculate bolus dose based on carb ratio and correction factor
  Trace: SYS-001  
  Verification: TC-003, TC-004, TC-005

## Performance Requirements  
SRS-010: Software shall complete dose calculation within 100ms
  Trace: SYS-003
  Verification: TC-020

## Safety Requirements
SRS-020: Software shall limit single bolus to 25 units
  Trace: RISK-005 control
  Verification: TC-040

## Interface Requirements
SRS-030: Software shall communicate with pump motor via SPI interface
  Trace: SYS-010
  Verification: TC-050
```

**Step 6: Requirements Review**
- Verify all user needs addressed
- Verify requirements are clear, testable, complete
- Verify risk controls incorporated
- Obtain approvals

## Design Output

### Architecture Development

**Create Architecture Document:**
```markdown
# Software Architecture

## System Context
[Diagram showing software in device context]

## Software Components
- DoseCalculation: Calculates insulin doses
- UserInterface: Touchscreen interaction
- MotorControl: Commands pump motor
- AlarmManager: Processes and displays alarms
- DataLogger: Records events and data
- Communication: Network interface

## Component Diagram
[Show components and interfaces]

## Data Flow
[Show how data flows through system]

## SOUP Components
- FreeRTOS v10.5: Real-time operating system
- Mbedtls v3.1: Cryptographic library

## Safety Architecture
- DoseCalculation runs in protected memory
- Watchdog monitors dose calculation
- Independent dose limit checker
```

**Detailed Design (Class C):**
```markdown
# Detailed Design: DoseCalculation Module

## Purpose
Calculate basal and bolus insulin doses

## Interfaces
Input: UserProfile, BloodGlucose, CarbIntake
Output: DoseCommand

## Algorithm
```
function CalculateBolus(carbGrams, bloodGlucose, profile):
  carbDose = carbGrams / profile.carbRatio
  correctionDose = (bloodGlucose - profile.targetBG) / profile.correctionFactor
  totalDose = carbDose + correctionDose
  totalDose = min(totalDose, MAX_BOLUS_LIMIT)
  return totalDose
```

## Error Handling
- If bloodGlucose < 20 or > 600: Error, do not dose
- If carbGrams < 0: Error
- If totalDose < 0: Set to 0
```

## Design Verification

### Design Review
**Participants:**
- Software developers
- Systems engineer
- Risk management
- Quality assurance
- Independent reviewer (not involved in design)

**Review Checklist:**
- [ ] All requirements addressed in design
- [ ] Design is implementable
- [ ] Interfaces clearly defined
- [ ] SOUP properly specified
- [ ] Risk controls implemented
- [ ] Design supports testability
- [ ] No conflicts or ambiguities

### Traceability Verification
Verify bidirectional traceability:
- Requirements → Design elements
- Design elements → Requirements

## Design Validation

### Plan Validation Early
During requirements phase, define:
- How will we validate this meets user needs?
- What clinical/user testing needed?
- What are acceptance criteria?

### Validation Protocol
```markdown
# Design Validation Protocol

## Objective
Demonstrate device meets user needs and intended use

## Validation Activities

### IQ - Installation Qualification
- Verify software installation in pump
- Verify configuration
- Verify security

### OQ - Operational Qualification  
- Test all software functions
- Verify performance
- Verify interfaces

### PQ - Performance Qualification
- End-to-end clinical scenarios
- User acceptance by clinicians/patients
- Real-world environment
- Extended duration testing

### Clinical Validation
- Clinical study per protocol
- Demonstrate safety and effectiveness
- User satisfaction assessment
```

## Design Transfer

### Create Device Master Record

**DMR Contents:**
- Software Requirements Specification
- Software Design Specification  
- Build Procedures
- Installation Procedures
- Acceptance Test Procedures
- Labeling Specifications

**Build Procedures:**
```markdown
# Software Build Procedure

## Build Environment
- OS: Ubuntu 20.04 LTS
- Compiler: arm-gcc 10.3
- Build Tool: CMake 3.20

## Build Steps
1. Clone repository: git clone [URL]
2. Checkout release tag: git checkout v1.0.0
3. Run build: ./build.sh release
4. Verify checksums: sha256sum build/firmware.bin
5. Expected: [hash value]
6. Sign firmware: ./sign.sh firmware.bin
7. Archive: Store in release/ directory

## Build Verification
- All tests pass
- No compiler warnings
- Static analysis clean
- Code coverage ≥95%
```

### Design Transfer Verification
- Verify DMR complete and approved
- Verify first production units meet DMR
- Verify manufacturing can follow DMR
- Verify test procedures adequate

## Design Changes

### Change Control Process

**Change Request Form:**
```markdown
# Design Change Request DCR-###

## Requested Change
[Description of what needs to change]

## Justification  
[Why change is needed]

## Impact Analysis

### Safety Impact
[Effect on patient safety, risk analysis]

### Performance Impact
[Effect on device performance]

### Regulatory Impact
[510(k) supplement required? PMA supplement?]

### Affected Documents
- [ ] Requirements
- [ ] Design
- [ ] Test Procedures
- [ ] User Manual
- [ ] Risk Analysis

### Verification/Validation Needed
- [ ] Unit tests
- [ ] Integration tests
- [ ] System tests  
- [ ] Regression tests
- [ ] Validation (IQ/OQ/PQ)

## Approval
- Requestor: [Name, Date]
- Engineering: [Name, Date]
- Quality: [Name, Date]
- Regulatory: [Name, Date]
- Management: [Name, Date]
```

**Implementation:**
1. Implement change per development process
2. Update all affected documentation
3. Execute verification/validation
4. Update DHF
5. Update DMR if production affected

## Design History File

### DHF Organization

**Folder Structure:**
```
DHF/
├── 01_Planning/
│   ├── Design_Plan.pdf
│   └── Project_Schedule.pdf
├── 02_Requirements/
│   ├── User_Needs.pdf
│   ├── System_Requirements.pdf
│   ├── Software_Requirements.pdf
│   └── Requirements_Review.pdf
├── 03_Design/
│   ├── Architecture.pdf
│   ├── Detailed_Design.pdf
│   └── Design_Reviews/
├── 04_Verification/
│   ├── Test_Plans.pdf
│   ├── Test_Results/
│   └── Traceability_Matrix.pdf
├── 05_Validation/
│   ├── Validation_Protocol.pdf
│   ├── Validation_Report.pdf
│   └── Clinical_Study_Report.pdf
├── 06_Risk_Management/
│   └── Risk_Management_File/
├── 07_Design_Transfer/
│   ├── DMR/
│   └── Transfer_Verification.pdf
└── 08_Design_Changes/
    └── Change_Records/
```

### DHF Maintenance
- Add documents as created
- Version control all documents
- Cross-reference related documents
- Maintain index/table of contents
- Regular completeness audits

---

**Key Takeaway**: Design controls provide systematic framework ensuring devices are designed right. Key elements: clear requirements, documented design, thorough verification and validation, complete DHF, rigorous change control. Software aligns well with IEC 62304.
