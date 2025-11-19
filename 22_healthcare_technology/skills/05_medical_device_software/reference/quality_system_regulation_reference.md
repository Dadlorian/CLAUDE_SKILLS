# Quality System Regulation (21 CFR Part 820) Reference

## Overview

The Quality System Regulation (QSR), codified in 21 CFR Part 820, establishes quality system requirements for medical device manufacturers. This reference focuses on software-specific QSR compliance.

## Quality System Structure

```
Management Responsibility (820.20)
         ↓
Design Controls (820.30)
         ↓
Document Controls (820.40)
         ↓
Purchasing Controls (820.50)
         ↓
Production & Process Controls (820.70-820.75)
         ↓
Acceptance Activities (820.80-820.86)
         ↓
Nonconforming Product (820.90)
         ↓
Corrective/Preventive Action (820.100)
         ↓
Records (820.180-820.198)
         ↓
Servicing (820.200)
```

## Management Responsibility (§820.20)

### Management with Executive Responsibility

**Requirements:**
- Establish quality policy
- Establish quality objectives
- Provide adequate resources
- Ensure quality system effectiveness
- Conduct management reviews

**Software Implications:**
- Executive commitment to software quality
- Resources for software development per IEC 62304
- Investment in tools and training

### Quality Policy

**Must include:**
- Commitment to meet regulatory requirements
- Commitment to maintain quality system
- Organizational structure
- Authority and responsibility

### Management Representative

**Responsibilities:**
- Ensure quality system requirements established
- Report on quality system performance
- Ensure awareness of regulatory requirements

### Management Review

**Requirements:**
- Review quality system at defined intervals
- Document reviews
- Review data on:
  - Quality system effectiveness
  - Audit results
  - Complaint data
  - CAPA effectiveness

**Software-Specific Reviews:**
- Software development process effectiveness
- Software defect trends
- Validation results
- Post-market surveillance data

## Design Controls (§820.30)

(Covered in detail in design_controls_reference.md)

**Key Software Requirements:**
- Software Development Plan
- Software Requirements Specification
- Architecture and Design documentation
- Verification and Validation
- Traceability
- Design History File (DHF)
- Device Master Record (DMR)
- Design changes controlled

## Document Controls (§820.40)

### Document Approval and Distribution

**Requirements (§820.40(a)):**
- Documents reviewed and approved
- Master list or equivalent
- Document changes reviewed and approved
- Obsolete documents removed from use
- Records of obsolete documents retained

**Software Documents to Control:**
- Software Development Plan
- Requirements specifications
- Design documents
- Test plans and protocols
- Validation protocols
- SOPs for software development
- Configuration management procedures
- Build and release procedures

### Document Change Control

**Requirements (§820.40(b)):**
- Changes reviewed and approved
- Approval by individual(s) who approved original
- Change history maintained

**Software Change Documentation:**
- Version control records
- Change request forms
- Impact analysis
- Verification/validation of changes
- Updated documentation

**Version Control:**
- All documents versioned
- Version numbering scheme
- Change history log
- Traceability to software versions

## Purchasing Controls (§820.50)

### Evaluation of Suppliers

**Requirements (§820.50(a)):**
- Establish procedures for evaluating suppliers
- Evaluate based on ability to meet requirements
- Define type and extent of control
- Maintain records

**Software SOUP Suppliers:**
- Evaluate SOUP vendors
- Assess quality and support
- Monitor for updates and vulnerabilities
- Maintain approved supplier list

### Purchasing Data

**Requirements (§820.50(b)):**
- Purchase orders clear and accurate
- Include:
  - Device/component specifications
  - Quality requirements
  - Acceptance criteria

**SOUP Purchasing:**
- Specific version numbers
- License requirements
- Support agreements
- Source code escrow (if critical)
- Security update commitments

## Production and Process Controls (§820.70-§820.75)

### General Production Controls (§820.70)

**Requirements:**
- Develop, conduct, control, monitor production processes
- Ensure specified requirements met
- Validated processes

**Software "Production":**
- Software build process
- Compilation procedures
- Configuration management
- Release procedures
- Installation procedures

**Build Process Controls:**
- Documented build procedures
- Automated build scripts (validated)
- Build environment specification
- Compiler versions documented
- Build verification (checksums)
- Reproducible builds

### Inspection, Measuring, and Test Equipment (§820.72)

**Requirements:**
- Calibration procedures
- Calibration schedules
- Calibration standards traceable
- Records maintained

**Software Tools:**
- Development tools (compilers, IDEs)
- Testing tools (unit test frameworks)
- Static analysis tools
- Configuration management tools
- Automated test tools

**Tool Qualification:**
Per IEC 62304 Annex C, tools that automate verification must be qualified:
- Tool validation evidence
- Tool version control
- Tool configuration documentation
- Regular tool assessment

### Process Validation (§820.75)

**Requirements:**
- Validate processes that cannot be fully verified
- Establish process parameters
- Initial validation
- Periodic revalidation
- Validation documentation

**Software Process Validation:**
- Software development process
- Software validation (IQ/OQ/PQ)
- Automated testing processes
- Build and release processes
- Installation processes

**Software Validation Documentation:**
- Validation plan
- Validation protocols
- Validation results
- Validation report
- Approval signatures

**Revalidation Triggers:**
- Process changes
- Software changes
- Tool changes
- Environmental changes
- Process performance issues

## Acceptance Activities (§820.80-§820.86)

### Receiving Acceptance (§820.80)

**Requirements:**
- Procedures for receiving inspections
- Verify purchased product meets requirements

**SOUP Receipt:**
- Verify correct version
- Verify integrity (checksums)
- Scan for malware
- Verify license
- Document receipt inspection

### In-Process Acceptance (§820.86)

**Requirements:**
- Identify inspection and test status
- Ensure only tested/released product distributed

**Software Development:**
- Code review status
- Unit test status
- Integration test status
- Static analysis results
- Configuration management status

**Status Indicators:**
- Work in progress
- Under review
- Verified
- Validated
- Released

## Nonconforming Product (§820.90)

### Control of Nonconforming Product

**Requirements:**
- Identify and control nonconforming product
- Review and disposition
- Investigate and document
- Rework procedures

**Software Nonconformities:**
- Software defects/bugs
- Failed tests
- Design flaws
- Requirements deviations

**Disposition Options:**
1. **Rework**: Fix and retest
2. **Use As-Is**: Accept with justification
3. **Reject**: Do not release
4. **Conditional Release**: Use with restrictions

**Bug Severity Classification:**
- **Critical**: Patient safety impact, no workaround
- **Major**: Significant impact, workaround exists
- **Minor**: Cosmetic or minor usability issue

### Nonconformity Review and Disposition

**Documentation:**
- Description of nonconformity
- Investigation results
- Root cause analysis
- Disposition decision
- Verification of disposition
- Approval signatures

## Corrective and Preventive Action (§820.100)

### Corrective Action

**Requirements (§820.100(a)):**
- Establish procedures for CAPA
- Analyze processes, operations, complaints, etc.
- Investigate causes of nonconformities
- Identify action needed
- Verify/validate CAPA
- Ensure information disseminated
- Document activities

**Software CAPA Sources:**
- Software defects
- Failed tests
- User complaints
- Audit findings
- Adverse events
- Post-market data

**CAPA Process:**
1. **Identify Problem**
   - Problem description
   - Impact assessment
   - Data collection

2. **Investigate**
   - Root cause analysis (5 Whys, Fishbone)
   - Identify contributing factors
   - Assess extent of problem

3. **Plan Action**
   - Define corrective action
   - Define preventive action
   - Assign responsibility
   - Set timeline

4. **Implement**
   - Execute actions
   - Document implementation
   - Update procedures/training

5. **Verify Effectiveness**
   - Verify action implemented
   - Validate effectiveness
   - Monitor for recurrence

6. **Document and Close**
   - Complete documentation
   - Management review
   - Close CAPA

### Preventive Action

**Requirements (§820.100(b)):**
- Identify sources of potential nonconformities
- Identify action needed
- Verify/validate preventive action
- Ensure information disseminated

**Software Preventive Actions:**
- Trend analysis of defects
- Code quality metrics
- Complexity analysis
- Static analysis findings
- Security vulnerability scans
- Process improvements

## Traceability (§820.65)

**Requirements:**
- For devices with traceability requirements
- Ability to trace distribution
- Document device history

**Software Traceability:**
- Version control records
- Build records
- Release records
- Distribution records
- Installation records
- Configuration tracking

**Traceability Documentation:**
- Device History Record (DHR) for each release
- Software version in each device
- Build date and builder
- Test results for release
- Installation locations

## Statistical Techniques (§820.250)

**Requirements:**
- Establish procedures for statistical techniques
- Use when needed to validate processes
- Use for data analysis

**Software Applications:**
- Code quality metrics (complexity, coverage)
- Defect density analysis
- Test effectiveness metrics
- Process capability analysis
- Reliability prediction
- Failure rate analysis

**Common Metrics:**
- Defects per 1000 lines of code
- Test coverage percentage
- Defect discovery rate
- Defect removal efficiency
- Mean time between failures
- Requirements volatility

## Records (§820.180-§820.198)

### General Requirements (§820.180)

**Requirements:**
- Establish procedures for records
- Records legible, complete, accurate
- Retained for device lifetime + defined period
- Readily accessible
- Stored in safe environment
- Protect from damage/deterioration

**Software Records:**
- Electronic records permitted (21 CFR Part 11)
- Backups required
- Access controls
- Audit trails
- Migration plan for obsolete media

### Device Master Record (§820.181)

**Requirements:**
- Specifications for finished device
- Production process specifications
- Quality assurance procedures
- Packaging and labeling specifications
- Installation, servicing procedures

**Software DMR:**
- Software Requirements Specification
- Software architecture
- Build procedures
- Release procedures
- Installation procedures
- Configuration specifications
- Version identification

### Device History Record (§820.184)

**Requirements:**
- For each batch/lot or device
- Demonstrate manufacturing complied with DMR
- Quantity manufactured
- Quantity released
- Acceptance records
- Unique identification

**Software DHR:**
- Build log for each release
- Version number
- Build date and environment
- Test results summary
- Release approval
- Distribution records

### Quality System Records (§820.186)

**Requirements:**
- Management reviews
- Corrective/preventive actions
- Internal audits
- Training records
- Complaint files

### Design History File (§820.184)

**Requirements:**
- Contains or references design history
- Allows verification device designed per approved design plan

(See design_controls_reference.md for details)

## Software-Specific QSR Considerations

### Configuration Management

**Critical for Software:**
- Version control all artifacts
- Baseline management
- Change control
- Build management
- Release management

**Configuration Items:**
- Source code
- Requirements documents
- Design documents
- Test documents
- Build scripts
- Tools and compilers

### Automated Processes

**Validation Required:**
- Automated build processes
- Automated testing
- Automated deployment
- Code generation tools
- Test data generation

**Validation Evidence:**
- Tool qualification
- Process validation
- Periodic verification
- Change control for automation

### Electronic Records (21 CFR Part 11)

**Requirements:**
- Validation of systems
- Audit trails
- System access controls
- Authority checks
- Device checks
- Education and training

**Software Development:**
- Requirements management tools
- Test management systems
- Issue tracking systems
- Document management systems
- Configuration management tools

## Internal Audits (§820.22)

**Requirements:**
- Procedures for quality audits
- Conducted per defined schedule
- Results documented
- Follow-up actions

**Software Audit Topics:**
- Design control implementation
- IEC 62304 compliance
- Configuration management
- SOUP management
- Cybersecurity practices
- Validation completeness
- Change control effectiveness
- CAPA for software defects

**Audit Frequency:**
- At least annually
- More frequent for critical processes
- After significant changes
- Based on risk

## FDA Inspections

### FDA Inspection Process

**When:**
- Prior to 510(k) clearance (sometimes)
- Prior to PMA approval (usually)
- Routine inspections (biennial goal)
- For-cause inspections (complaints, recalls)
- Pre-approval inspections

**Focus Areas for Software:**
- Design controls
- Software validation
- SOUP management
- Change control
- Cybersecurity
- Traceability
- DHF completeness

### Inspection Preparation

**Be Ready to Show:**
- Quality Manual
- SOPs (design, validation, change control)
- Design History Files
- Validation records
- Configuration management records
- Audit records
- CAPA records
- Training records

**Software Documentation:**
- Requirements traceability
- Design documents
- Verification/validation results
- SOUP evaluations
- Risk management files
- Change control records

### Common 483 Observations

**Software-Related Findings:**
1. Inadequate design controls
2. Incomplete validation
3. Poor change control
4. Inadequate SOUP management
5. Missing traceability
6. Incomplete DHF
7. Inadequate cybersecurity
8. Poor configuration management

## Best Practices

1. **Integrate IEC 62304**: Use as framework for software QSR compliance
2. **Document Everything**: "If not documented, didn't happen"
3. **Automate with Validation**: Automate processes but validate automation
4. **Version Control Everything**: All artifacts under configuration management
5. **Maintain Complete DHF**: Don't leave gaps to fill at inspection
6. **Regular Internal Audits**: Find issues before FDA does
7. **Effective CAPA**: Investigate root causes, verify effectiveness
8. **Training**: Ensure staff understands requirements
9. **Tool Qualification**: Qualify automated verification tools
10. **Continuous Improvement**: Use metrics to improve processes

## QSR and IEC 62304 Mapping

```
QSR                          IEC 62304
---                          ---------
820.30 Design Controls   →   Section 5 (Development Process)
820.70 Production        →   Section 5.8 (Release)
820.75 Validation        →   Section 5.7 (System Testing)
820.100 CAPA            →   Section 6 (Maintenance)
820.40 Document Control  →   Section 8 (Configuration Mgmt)
820.90 Nonconforming    →   Section 9 (Problem Resolution)
820.30(j) DHF           →   Lifecycle documentation
```

**Using IEC 62304:**
- Satisfies QSR software requirements
- Recognized by FDA
- Provides detailed procedures
- International harmonization

---

**Key Takeaway**: QSR establishes quality system requirements for medical device software. Integration with IEC 62304 provides comprehensive framework. Complete documentation, validated processes, effective change control, and robust CAPA are essential. Regular internal audits prepare for FDA inspections.
