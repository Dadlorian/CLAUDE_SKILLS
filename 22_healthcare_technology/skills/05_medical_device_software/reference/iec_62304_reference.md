# IEC 62304 Medical Device Software Lifecycle Reference

## Overview

IEC 62304:2006+AMD1:2015 "Medical device software – Software life cycle processes" is the international standard for medical device software development lifecycle processes.

## Scope

Applies to:
- Software that is part of a medical device
- Software that is itself a medical device (Software as a Medical Device - SaMD)
- Software used in production or quality system of medical devices

Does NOT apply to:
- Software used only during development
- Software used for patient record systems unless it affects medical device data

## Software Safety Classification

### Class A: No Injury or Damage to Health
- Software failure cannot result in harm
- Minimal documentation and testing requirements
- Example: Administrative functions of a device

### Class B: Non-Serious Injury Possible
- Software failure could result in non-serious injury
- Moderate documentation and testing requirements
- Example: Diagnostic imaging viewing software without treatment decision support

### Class C: Death or Serious Injury Possible
- Software failure could result in death or serious injury
- Most rigorous documentation and testing requirements
- Example: Insulin pump control software, ventilator software

**Classification Rule**: Assign the highest class that applies to ANY software item

## Software Development Process (Section 5)

### 5.1 Software Development Planning
**Requirements:**
- Software Development Plan documenting:
  - Deliverables of development activities
  - Tasks and activities to be performed
  - Responsibility assignment
  - Development standards, methods, tools, and languages
  - Software configuration management activities
  - Software problem resolution process
  - Verification activities
  - Risk management activities
  - Documentation and record keeping

**Class-Specific Requirements:**
- Class A: Basic plan
- Class B: More detailed plan with standards
- Class C: Comprehensive plan with detailed procedures and standards (e.g., MISRA C)

### 5.2 Software Requirements Analysis
**Requirements:**
- Document software requirements including:
  - Functional and capability requirements
  - Software system inputs and outputs
  - Interfaces between software items and other systems
  - Software-driven alarms, warnings, and operator messages
  - Security requirements including data integrity and confidentiality
  - Usability engineering requirements
  - Data definition and database requirements
  - Installation and acceptance requirements
  - Requirements related to methods of operation and maintenance
  - User maintenance requirements
  - Regulatory requirements
  - Risk control measures from risk management process

**Activities:**
- Define and document software requirements
- Derive software requirements from system requirements
- Re-evaluate medical device risk analysis
- Establish bidirectional traceability
- Verify software requirements

**Class-Specific Requirements:**
- All Classes: Complete requirements documentation
- Class C: Enhanced review and verification rigor

### 5.3 Software Architectural Design
**Requirements:**
- Transform software requirements into architecture showing:
  - Software items (components/modules)
  - External software interfaces
  - Internal software interfaces between items
  - Software items that are SOUP (Software of Unknown Provenance)

**Activities:**
- Develop architecture
- Specify functional and performance requirements for SOUP
- Identify segregation necessary for risk control
- Verify software architecture

**Class-Specific Requirements:**
- Class B, C: Must verify architecture
- Class C: Enhanced verification including traceability to requirements

### 5.4 Software Detailed Design
**Requirements:**
- Refine architecture into software units that can be coded and tested
- Document:
  - Interfaces between software units and external components
  - Detailed design of each software unit

**Activities:**
- Develop detailed design
- Verify detailed design

**Class-Specific Requirements:**
- Class A: Not required
- Class B: Required
- Class C: Required with comprehensive verification

### 5.5 Software Unit Implementation and Verification
**Requirements:**
- Implement each software unit
- Establish coding standards (e.g., MISRA C for Class C)
- Verify each software unit

**Verification Methods:**
- Testing
- Code review
- Static analysis

**Class-Specific Requirements:**
- Class A: No specific verification required
- Class B: Unit testing or code review
- Class C: 100% statement coverage OR 100% branch coverage, extensive code review

### 5.6 Software Integration and Integration Testing
**Requirements:**
- Integrate software units and SOUP items
- Test integrated software items
- Verify integration

**Test Coverage:**
- Class A: Not specified
- Class B: Test all software items
- Class C: Test all software items with comprehensive test cases

### 5.7 Software System Testing
**Requirements:**
- Test complete software system
- Use software requirements as test basis
- Include regression testing
- Document test plans, procedures, and results

**Test Coverage:**
- All Classes: Test all software requirements
- Class C: Enhanced rigor and documentation

### 5.8 Software Release
**Requirements:**
- Archive software and documentation
- Ensure configuration items include all items necessary to reproduce release
- Document known residual anomalies
- Evaluate residual anomalies for acceptability

## Software Maintenance Process (Section 6)

### 6.1 Establish Maintenance Plan
- Procedures for receiving and evaluating feedback
- Criteria for qualifying problems as defects
- Use of problem resolution process

### 6.2 Problem and Modification Analysis
**Requirements:**
- Document and verify changes
- Analyze impact on safety and existing risk analysis
- Communicate to users and regulators as appropriate

**Change Categories:**
- Problem reports from users/field
- Enhancement requests
- Changes to address newly identified hazards
- Regulatory requirement changes

### 6.3 Modification Implementation
**Requirements:**
- Use development process for modifications
- Perform regression analysis and testing
- Update system and software documentation

## Software Risk Management (Section 7)

### 7.1 Analysis of Software Contributing to Hazardous Situations
**Requirements:**
- Identify software items that could contribute to hazardous situations
- Identify potential causes (sequence of events, software defects, hardware failures, user errors)
- Evaluate published SOUP anomaly lists
- Document in risk management file

### 7.2 Risk Control Measures
**Requirements:**
- Define risk control measures in software requirements
- Verify implementation of risk control measures
- Document in risk management file

### 7.3 Verification of Risk Control Measures
- Verify risk control measure implementation
- Trace to software testing
- Document verification results

### 7.4 Risk Management of Software Changes
- Analyze changes for:
  - Introduction of new hazards
  - Impact on existing hazards
  - Changes to risk control measures
- Update risk management file

## Software Configuration Management (Section 8)

### 8.1 Configuration Management Planning
**Requirements:**
- Configuration management plan including:
  - Configuration items to be controlled
  - Configuration management activities and tasks
  - Responsibility for activities
  - When configuration management activities are performed
  - Software configuration management tools

### 8.2 Configuration Identification
**Requirements:**
- Identify configuration items:
  - SOUP
  - Documentation (specifications, manuals, test records)
  - Software system and software items
  - Configuration management records

- Unique identification scheme for:
  - All releases
  - All software items
  - All documentation versions

### 8.3 Change Control
**Requirements:**
- Change request approval before implementation
- Track change requests and their status
- Evaluate changes for impact on safety and existing software items

**Class-Specific Requirements:**
- All Classes: Formal change control required

## Software Problem Resolution (Section 9)

### 9.1 Problem Resolution Process
**Requirements:**
- Prepare problem reports documenting:
  - Problem description
  - Scope and criticality
- Investigate and document:
  - Cause investigation
  - Impact evaluation
  - Actions to resolve
  - Action implementation and verification

### 9.2 Problem Analysis
- Identify affected versions
- Analyze relevance to safety
- Consider need for adverse event reporting
- Document actions taken

### 9.3 Implementation of Problem Solutions
- Use change control process
- Verify solution effectiveness
- Test for regression
- Provide feedback to reporters

### 9.4 Trend Analysis
- Collect and analyze problem reports
- Identify recurring problems
- Evaluate for safety implications
- Take corrective action

## SOUP (Software of Unknown Provenance) Management

### Definition
Software item that is already developed and generally available, for which adequate records of development processes are not available.

### Examples
- Commercial off-the-shelf (COTS) software
- Open-source software
- Freeware
- Operating systems
- Libraries and frameworks
- Third-party components

### Requirements for SOUP (Annex B)

#### SOUP Identification
- Name
- Manufacturer/supplier
- Version
- Configuration items

#### Functional and Performance Requirements
- Specify what SOUP must do
- Define operating environment
- Define hardware requirements

#### SOUP Hazards
- List of known anomalies
- Evaluation of published anomaly lists
- Assessment of anomalies for safety impact

#### Verification of SOUP
- Testing against functional requirements
- Anomaly evaluation
- Documentation of SOUP verification

#### SOUP Obsolescence Monitoring
- Monitor for updates and patches
- Evaluate security vulnerabilities
- Plan for SOUP replacement if discontinued

## Documentation Requirements Summary

### Software Development Plan
- Development standards and methods
- Software configuration management
- Problem resolution processes

### Software Requirements Specification (SRS)
- All software requirements
- Traceability to system requirements and risk controls

### Software Architecture Document
- High-level design
- Software items and interfaces
- SOUP identification

### Software Detailed Design (Class B, C)
- Software unit design
- Interfaces

### Verification and Validation Plans and Reports
- Test plans
- Test procedures
- Test results
- Traceability matrices

### Risk Management File
- Hazard analysis
- Risk assessments
- Risk control measures
- Verification of controls

### Configuration Management Records
- Version identification
- Change history
- Release records

### Problem Reports and Analysis
- Problem documentation
- Investigation records
- Trend analysis

## Traceability Requirements

### Required Traceability Links

**Forward Traceability:**
- System Requirements → Software Requirements
- Software Requirements → Architecture
- Architecture → Detailed Design (Class B, C)
- Software Requirements → Tests
- Risk Controls → Software Requirements → Tests

**Backward Traceability:**
- Tests → Software Requirements
- Software Requirements → System Requirements
- Software Requirements → Risk Controls

### Traceability Matrix Format
```
| Req ID | Requirement | Design Item | Test Case | Status | Risk Control |
|--------|-------------|-------------|-----------|--------|--------------|
```

## Verification Methods by Class

### Class A
- Minimal verification required
- No unit testing requirement
- Basic integration testing

### Class B
- Unit verification (testing OR code review)
- Integration testing of all items
- System testing against requirements
- Architecture verification

### Class C
- Unit testing with code coverage:
  - 100% statement coverage OR
  - 100% branch coverage
- Comprehensive code review
- Integration testing of all items with comprehensive test cases
- System testing against all requirements
- Architecture and detailed design verification
- Static analysis
- Potential MC/DC (Modified Condition/Decision Coverage) for critical modules

## Integration with Other Standards

### ISO 14971 (Risk Management)
- Section 7 aligns with ISO 14971
- Software hazard analysis required
- Risk control measures integrated into requirements
- Risk management file maintained throughout lifecycle

### ISO 13485 (Quality Management)
- IEC 62304 satisfies software development requirements
- Design controls align with ISO 13485
- Documentation supports quality system

### IEC 62366 (Usability Engineering)
- Usability requirements integrated into software requirements
- User interface verification and validation
- Use error mitigation

### FDA 21 CFR Part 820 (QSR)
- Software development aligns with design controls
- Verification and validation requirements
- Change control and configuration management

## Common Compliance Gaps

1. **Inadequate Software Classification Justification**
   - Solution: Document clear rationale with hazard analysis

2. **Missing Traceability**
   - Solution: Implement traceability matrix from start

3. **Insufficient SOUP Management**
   - Solution: Full SOUP documentation with anomaly lists

4. **Incomplete Risk Management Integration**
   - Solution: Link all hazards to software requirements and tests

5. **Inadequate Change Control**
   - Solution: Formal change control process for all modifications

6. **Missing Code Coverage for Class C**
   - Solution: Automated coverage tools and documented analysis

7. **Insufficient Documentation**
   - Solution: Templates and document review processes

## Best Practices

1. **Start with Classification**: Properly classify software safety class early
2. **Use Templates**: Standardize documentation with templates
3. **Automate Traceability**: Use requirements management tools
4. **Integrate Risk Management**: Make it continuous, not one-time
5. **Code Coverage from Start**: Build testing infrastructure early
6. **Tool Qualification**: Qualify automated tools per Annex C if they automate verification
7. **Version Everything**: Strict version control on all artifacts
8. **Regular Reviews**: Conduct design reviews at each phase
9. **Gap Analysis**: Periodically assess compliance against standard
10. **Training**: Ensure all team members understand IEC 62304

## Revision History

- **IEC 62304:2006**: Original standard
- **IEC 62304:2006/AMD1:2015**: Amendment 1
  - Added requirements for software in medical device cybersecurity
  - Enhanced SOUP requirements
  - Clarified documentation requirements

## Related Standards and Guidance

- **IEC 62304-1:2006**: Compliance standard
- **IEC TR 80002-1:2009**: Guidance on application of IEC 62304
- **IEC TR 80002-3**: Guidance on application of ISO 14971 to software
- **FDA Guidance on Software Validation**: Complementary to IEC 62304
- **AAMI TIR45**: Guidance on IEC 62304 software development
- **MDCG 2019-11**: EU guidance on software qualification and classification

---

**Key Takeaway**: IEC 62304 is the foundation for compliant medical device software development. Full compliance requires rigorous documentation, comprehensive testing proportional to safety class, and integration with risk management processes.
