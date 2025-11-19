# Design Controls Reference (21 CFR 820.30)

## Overview

Design Controls are the regulatory requirements under 21 CFR Part 820.30 that ensure medical devices are designed according to sound engineering practices and approved procedures. This reference covers design control principles, processes, and documentation requirements.

## Legal Basis

**21 CFR Part 820.30** - Design Controls
- Mandatory for Class II and Class III devices
- Class I devices exempt unless specifically required
- Applies to device modifications that could affect safety/effectiveness

## Design Control Elements

### §820.30(b) Design and Development Planning

**Requirements:**
Each manufacturer shall establish and maintain plans describing or referencing design and development activities and defining responsibility for implementation.

**Required Elements:**
1. **Design Phases**
   - Concept development
   - Requirements definition
   - Architectural design
   - Detailed design
   - Implementation
   - Integration
   - System testing
   - Design transfer
   - Production

2. **Activity Descriptions**
   - Tasks to be performed in each phase
   - Deliverables from each phase
   - Success criteria
   - Resources required

3. **Responsibility Assignment**
   - Who performs each activity
   - Who reviews each deliverable
   - Who approves phase transitions
   - Clear organizational structure

4. **Interfaces**
   - Design team interfaces
   - Cross-functional coordination
   - External interfaces (suppliers, consultants)

**Software-Specific Elements:**
- Software development methodology (Waterfall, V-Model, Agile)
- Coding standards (MISRA C, CERT C)
- Development tools and environment
- Version control procedures
- Configuration management approach

**Documentation:**
- Design and Development Plan (DDP) or Software Development Plan (SDP)
- Updates as design evolves
- Review and approval records

### §820.30(c) Design Input

**Requirements:**
Each manufacturer shall establish and maintain procedures to ensure design input requirements relating to a device are appropriate and address the intended use of the device.

**Design Input Sources:**
1. **Intended Use and Indications**
   - Target patient population
   - Clinical indications
   - Contraindications
   - Use environment

2. **User Needs**
   - Clinical workflows
   - User experience requirements
   - Training needs
   - Usability requirements

3. **Functional Requirements**
   - What the device must do
   - Performance specifications
   - Accuracy requirements
   - Operational modes

4. **Regulatory Requirements**
   - Applicable standards (IEC 62304, ISO 14971)
   - Essential performance requirements
   - Specific regulatory guidance
   - Jurisdictional requirements

5. **Risk Control Requirements**
   - Requirements derived from risk analysis
   - Safety requirements
   - Security requirements
   - Reliability requirements

6. **Interface Requirements**
   - User interfaces
   - Hardware interfaces
   - Software interfaces
   - Network/communication interfaces

**Characteristics of Good Design Inputs:**
- **Specific**: Clearly defined, not ambiguous
- **Measurable**: Testable and verifiable
- **Achievable**: Technically feasible
- **Unambiguous**: Single interpretation
- **Traceable**: Uniquely identified
- **Complete**: All requirements captured
- **Consistent**: No conflicting requirements

**Documentation:**
- User Requirements Specification (URS)
- System Requirements Specification (SyRS)
- Software Requirements Specification (SRS)
- Risk analysis outputs
- Input review and approval records

### §820.30(d) Design Output

**Requirements:**
Each manufacturer shall establish and maintain procedures for defining and documenting design output in terms that allow an adequate evaluation of conformance to design input requirements.

**Design Output Elements:**

1. **Specifications**
   - Software architecture specification
   - Detailed design specifications
   - Interface control documents
   - Database schema
   - Algorithm descriptions

2. **Code and Executables**
   - Source code
   - Compiled/executable software
   - Build scripts
   - Configuration files

3. **Documentation**
   - Technical documentation
   - User manuals
   - Installation guides
   - Service manuals
   - Training materials

4. **Acceptance Criteria**
   - Pass/fail criteria for testing
   - Performance benchmarks
   - Quality metrics

**Design Output Requirements:**
- **Meet Design Input**: All inputs addressed
- **Essential for Production**: Specifications adequate for manufacturing/building
- **Essential for Procurement**: Component specifications clear
- **Essential for Safety**: Risk controls implemented
- **Device Master Record (DMR)**: Production specifications documented

**Software Design Outputs:**
- Software Architecture Document
- Detailed Design Document
- Source code (with comments)
- Build procedures
- Installation procedures
- User interface specifications
- Database design
- API specifications

**Documentation:**
- Design specifications (architecture, detailed)
- Source code repository
- Build and release procedures
- Output review and approval records

### §820.30(e) Design Review

**Requirements:**
Each manufacturer shall establish and maintain procedures to ensure design reviews are conducted at appropriate intervals throughout development.

**Design Review Objectives:**
1. Evaluate design progress
2. Identify design deficiencies
3. Ensure design inputs translated to outputs
4. Assess compliance with requirements
5. Identify risks and issues

**Design Review Timing:**
- End of each design phase
- Major milestones
- Critical decision points
- Before phase transitions
- Before design transfer

**Review Participants:**
- **Representatives of Design Functions**: Software, hardware, systems engineers
- **Independent Reviewer(s)**: Not directly involved in design stage being reviewed
- **Subject Matter Experts**: Clinical, regulatory, quality, risk management
- **Management**: For approval decisions

**Review Topics:**
- Requirements completeness and correctness
- Design adequacy and feasibility
- Risk analysis updates
- Verification planning
- Issues and anomalies
- Regulatory compliance
- Standards compliance

**Software Review Focus:**
- Software architecture review
- Code reviews
- Security architecture review
- Interface design review
- Database design review
- Algorithm validation

**Documentation:**
- Design review meeting minutes
- Attendance records
- Findings and action items
- Action item closure records
- Approval signatures

### §820.30(f) Design Verification

**Requirements:**
Each manufacturer shall establish and maintain procedures for verifying the device design. Design verification shall confirm that the design output meets the design input requirements.

**Definition:**
"Did we build the product right?"

**Verification Methods:**

1. **Testing**
   - Unit testing
   - Integration testing
   - System testing
   - Performance testing
   - Stress testing
   - Regression testing

2. **Analysis**
   - Mathematical modeling
   - Simulation
   - Calculations
   - Static code analysis

3. **Inspection/Review**
   - Code review
   - Design walkthrough
   - Document review
   - Traceability analysis

4. **Demonstration**
   - Proof of concept
   - Prototype testing

**Software Verification Activities:**
- Unit testing with code coverage
- Integration testing
- System testing
- Static analysis (linting, security scans)
- Dynamic analysis
- Requirements traceability verification
- Interface testing
- Performance/load testing

**Acceptance Criteria:**
- Clearly defined for each test
- Pass/fail criteria
- Measurement tolerances
- Expected results documented

**Documentation:**
- Verification plan
- Test protocols
- Test procedures
- Test results
- Traceability matrix (requirements to tests)
- Verification report
- Approval records

### §820.30(g) Design Validation

**Requirements:**
Each manufacturer shall establish and maintain procedures for validating the device design. Design validation shall ensure devices conform to defined user needs and intended uses.

**Definition:**
"Did we build the right product?"

**Validation Requirements:**
- Performed on initial production units, lots, or batches (or equivalents)
- Performed under actual or simulated use conditions
- Include software validation
- Include user needs validation

**Validation Activities:**

1. **Clinical Validation**
   - Clinical trials
   - Clinical evaluation
   - User acceptance testing in clinical setting

2. **Usability Validation**
   - Simulated use testing
   - Human factors validation
   - Actual use in representative environment

3. **Performance Validation**
   - Essential performance verification
   - Clinical performance validation
   - Real-world performance testing

4. **Software Validation**
   - Installation Qualification (IQ)
   - Operational Qualification (OQ)
   - Performance Qualification (PQ)

**Software Validation Focus:**
- End-to-end workflows
- User scenarios
- Clinical use cases
- Installation in target environment
- Performance under realistic conditions
- User interface validation
- Integration with existing systems

**Validation vs. Verification:**
```
Verification          Validation
-----------          ----------
Requirements → Code  User Needs → Product
"Built right"        "Right product"
Developer testing    User testing
Lab conditions       Real/simulated use
```

**Documentation:**
- Validation plan
- Validation protocols
- Clinical evaluation plan (if applicable)
- Test results
- User feedback
- Validation report
- Approval records

### §820.30(h) Design Transfer

**Requirements:**
Each manufacturer shall establish and maintain procedures to ensure device design is correctly translated into production specifications.

**Design Transfer Activities:**

1. **Production Specification**
   - Manufacturing procedures
   - Software build procedures
   - Quality control procedures
   - Inspection/test procedures

2. **Production Readiness**
   - Production equipment validated
   - Staff trained
   - Suppliers qualified
   - Build environment established

3. **Initial Production Verification**
   - First articles inspected
   - Initial production run
   - Verification of DMR adequacy

**Software Design Transfer:**
- Build and compilation procedures
- Software installation procedures
- Configuration management procedures
- Release procedures
- Deployment procedures
- Version control procedures
- Archive procedures

**Device Master Record (DMR) Creation:**
Complete set of documents defining:
- Device specifications
- Production process specifications
- Quality assurance procedures
- Packaging and labeling specifications
- Installation and servicing procedures

**Documentation:**
- Design transfer plan
- Production procedures
- Device Master Record (DMR)
- Training records
- Initial production verification results
- Transfer approval records

### §820.30(i) Design Changes

**Requirements:**
Each manufacturer shall establish and maintain procedures for the identification, documentation, validation or where appropriate verification, review, and approval of design changes before their implementation.

**Change Control Process:**

1. **Change Request**
   - Problem or opportunity identified
   - Change proposed
   - Justification documented

2. **Change Evaluation**
   - Impact analysis (safety, effectiveness, regulatory)
   - Risk assessment
   - Verification/validation needs determined
   - Resources estimated

3. **Change Approval**
   - Review by appropriate personnel
   - Management approval
   - Regulatory assessment

4. **Change Implementation**
   - Design modifications made
   - Verification/validation performed
   - Documentation updated

5. **Change Effectiveness**
   - Verification of change effectiveness
   - Monitoring for unintended effects

**Impact Analysis Considerations:**
- Safety and effectiveness
- Existing risk analysis
- User interface changes
- Interoperability
- Regulatory requirements
- Validation impact
- Field units (retrofit needs)

**Validation/Verification Requirements:**
- Major changes: Full validation
- Minor changes: Regression testing
- Documentation changes: Review and approval

**Software Change Control:**
- Version control
- Configuration management
- Regression testing
- Traceability update
- Documentation updates (SRS, design docs, test docs)

**Documentation:**
- Change request form
- Impact analysis
- Risk assessment update
- Verification/validation results
- Approval records
- Updated documentation
- Change history log

## Design History File (DHF)

### Definition
Complete compilation of records containing design history of finished device.

### Required Contents

**Per 21 CFR 820.30(j):**
Each manufacturer shall establish and maintain a DHF for each type of device.

**DHF Contents:**

1. **Design Planning**
   - Design and development plan
   - Resource allocation
   - Schedules

2. **Design Inputs**
   - User requirements
   - System requirements
   - Software requirements
   - Regulatory requirements

3. **Design Outputs**
   - Specifications (architecture, detailed design)
   - Source code
   - User documentation
   - Technical documentation

4. **Design Reviews**
   - Review minutes
   - Action items
   - Decisions made

5. **Verification Records**
   - Test plans and protocols
   - Test results
   - Traceability matrices
   - Analysis reports

6. **Validation Records**
   - Validation plans and protocols
   - Clinical evaluation
   - Usability testing
   - Validation reports

7. **Design Transfer**
   - Production specifications
   - Build procedures
   - DMR

8. **Design Changes**
   - Change requests
   - Impact analyses
   - Verification/validation of changes
   - Approvals

9. **Risk Management**
   - Risk management plan
   - Risk analysis
   - Risk evaluation
   - Risk control measures
   - Risk management review

**DHF Organization:**
- Logically organized
- Easy to retrieve
- Cross-referenced
- Version controlled
- Access controlled

### DHF vs. DMR vs. DHR

**Design History File (DHF):**
- How device was designed
- Development records
- One per device type
- Living document during development

**Device Master Record (DMR):**
- How to make the device
- Production specifications
- One per device type
- Controlled document

**Device History Record (DHR):**
- History of specific device units
- Production records
- One per device serial number/lot
- Traceability record

## Software-Specific Design Control Considerations

### IEC 62304 Integration

Design controls align with IEC 62304:

```
Design Control          IEC 62304
--------------          ---------
Planning                5.1 Development Planning
Input                   5.2 Requirements Analysis
Output                  5.3-5.6 Design, Implementation
Verification            5.5-5.7 Unit, Integration, System Testing
Validation              5.8 + User Validation
Transfer                Release Process
Changes                 6. Maintenance Process
```

### Software Requirements Specification (SRS)

**Contents:**
- Functional requirements
- Performance requirements
- Interface requirements (user, hardware, software)
- Safety requirements
- Security requirements
- Data requirements
- Environmental requirements
- Regulatory requirements

**Characteristics:**
- Uniquely identified (e.g., SRS-001)
- Verifiable (testable)
- Unambiguous
- Complete
- Consistent
- Traceable to user needs
- Traceable to design elements
- Traceable to tests

### Traceability

**Required Traceability:**
```
User Needs
    ↓
System Requirements
    ↓
Software Requirements (SRS)
    ↓
Design (Architecture, Detailed)
    ↓
Code Implementation
    ↓
Tests
```

**Traceability Matrix:**
Bidirectional links between:
- User needs ↔ Requirements
- Requirements ↔ Design
- Requirements ↔ Tests
- Risks ↔ Requirements ↔ Tests
- Requirements ↔ Code (for critical functions)

### Code as Design Output

**Considerations:**
- Source code is design output
- Must be reviewed and approved
- Version control mandatory
- Configuration management critical
- Build procedures documented
- Reproducible builds required

## Common Design Control Deficiencies

### FDA 483 Observations

1. **Inadequate Design Plans**
   - Missing or incomplete design plans
   - Plans not followed
   - Responsibilities unclear

2. **Incomplete Design Inputs**
   - Requirements vague or untestable
   - Missing regulatory requirements
   - Risk controls not incorporated

3. **Design Input/Output Mismatch**
   - Outputs don't address all inputs
   - Traceability gaps

4. **Missing or Inadequate Reviews**
   - Reviews not conducted
   - Wrong participants
   - Issues not addressed

5. **Insufficient Verification**
   - Testing incomplete
   - Pass/fail criteria unclear
   - Traceability missing

6. **Inadequate Validation**
   - Not performed under actual use conditions
   - User needs not validated
   - Insufficient clinical validation

7. **Poor Change Control**
   - Changes not evaluated
   - Impact analysis missing
   - Regression testing inadequate

8. **Incomplete DHF**
   - Missing key documents
   - Documents not approved
   - Traceability gaps

## Best Practices

1. **Start with End in Mind**: Define validation early
2. **Use Templates**: Standardize documentation
3. **Automate Traceability**: Use tools to maintain links
4. **Review Early and Often**: Don't wait for formal reviews
5. **Independent Review**: Include people not involved in design
6. **Complete Before Moving On**: Don't leave gaps to fill later
7. **Version Everything**: All documents version controlled
8. **Change Control Everything**: No informal changes
9. **Think Risk**: Integrate risk management throughout
10. **Document Rationale**: Explain decisions, not just results

## Design Control Process Flow

```
User Needs Assessment
         ↓
    Design Input ← Risk Analysis
         ↓
  Design Planning
         ↓
    Design Output
         ↓
   Design Review → Issues/Actions
         ↓
Design Verification → Pass/Fail
         ↓
Design Validation → Pass/Fail
         ↓
   Design Transfer → DMR
         ↓
    Production
         ↓
Post-Market Surveillance → Design Changes (if needed)
```

---

**Key Takeaway**: Design controls ensure systematic, documented development. For software, integration with IEC 62304 provides comprehensive framework. Complete DHF with rigorous traceability is essential for regulatory compliance and quality.
