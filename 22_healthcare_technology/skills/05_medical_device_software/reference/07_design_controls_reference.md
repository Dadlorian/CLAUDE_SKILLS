# Design Controls (21 CFR 820.30) Reference

## Design Control Overview

### Regulatory Requirement
- **21 CFR 820.30**: Design controls are required for Class III and Class II devices
- **Objective**: Ensure device design meets user needs and intended use
- **Key Concept**: Document design decisions and verify they meet requirements

### Design Control Phases
1. Design Planning
2. Input (Requirements)
3. Output (Design Specification)
4. Review
5. Verification
6. Validation
7. Transfer
8. Changes

## Design Planning (Phase 1)

### Design and Development Plan Contents
- **Product Overview**: What is device? What does it do?
- **Intended Use**: How will it be used? By whom? For what condition?
- **Risk Classification**: Class I, II, or III?
- **Design Team**: Who is involved? Roles and responsibilities?
- **Design Process**: Phases, gates, reviews
- **Design Controls Strategy**: How will each control be addressed?
- **Standards and Regulations**: What standards apply?
- **Tools and Methods**: CAD, simulation, analysis tools
- **V&V Strategy**: High-level testing approach
- **Configuration Management**: How will design artifacts be tracked?

### Risk Assessment in Design Planning
- Preliminary hazard analysis
- Patient population and use environment
- Foreseeable misuse
- Design solutions to address risks
- Risk management integration

## Design Input (Phase 2)

### Input Requirements
- **User Needs**: What does intended user need?
- **Intended Use**: Specific clinical application
- **Patient Population**: Age, gender, health status
- **Use Environment**: Hospital, home, clinic
- **User Expertise**: Specialist vs. general user

### Design Input Documentation
- Requirements specification document
- Source of each requirement (user, standard, regulation)
- Traceability tracking
- Approval by stakeholders
- Baseline for design output

### Input Verification
- **Completeness**: All user needs captured
- **Clarity**: Requirements unambiguous
- **Consistency**: No conflicting requirements
- **Feasibility**: Requirements achievable
- **Testability**: Requirements can be verified

## Design Output (Phase 3)

### Design Output Contents
- **Design Specifications**: How will requirements be met?
- **System Architecture**: High-level design
- **Hardware Specifications**: If applicable
- **Software Specifications**: Code structure, algorithms
- **User Interface Design**: Screens, controls, workflows
- **Safety Features**: How are risks controlled?
- **Performance Specifications**: Speed, accuracy, reliability
- **Labeling and Manuals**: Instructions for use

### Design Output Documentation
- Design History File (DHF)
- Detailed technical specifications
- Drawings and schematics
- Software architecture and code
- Detailed test plans
- Risk management analysis

### Output Verification
- **Traceability**: Each input requirement addressed in output
- **Completeness**: All requirements covered
- **Correctness**: Design correctly implements requirements
- **Feasibility**: Design is buildable and testable
- **Safety**: Risk controls incorporated

## Design Review (Phase 4)

### Design Review Objectives
- **Evaluation**: Is design adequate for intended use?
- **Risk Assessment**: Does design adequately control risks?
- **Completeness**: Are all requirements addressed?
- **Feasibility**: Can it be built and tested as designed?
- **Standards Compliance**: Does it meet applicable standards?

### Design Review Team
- Design engineers
- Quality assurance
- Regulatory/compliance
- Manufacturing (if applicable)
- Clinical/user expertise
- Management

### Design Review Outputs
- **Design Review Report**: Findings and recommendations
- **Issues Log**: Design problems identified
- **Closure Plan**: How issues will be resolved
- **Approval**: Design review sign-off
- **Version Control**: Design baseline for next phase

### Design Review Timing
- After each major design phase
- Before releasing design to next phase
- When major changes are made
- Typically: Planning review, input review, output review, verification review

## Design Verification (Phase 5)

### Verification Definition
- Confirming design output fulfills design input
- Question: Does the design meet the requirements?
- Testing against specification

### Verification Activities
- **Design Review**: Peer review of design
- **Design Analysis**: Mathematical, simulation, FMEA analysis
- **Testing**: Functional and performance testing
- **Inspection**: Visual inspection and measurement
- **Demonstration**: Proof of concept

### Verification Plan
- What design aspects will be verified?
- How will each be verified? (analysis, test, demonstration)
- What are acceptance criteria?
- Who will perform verification?
- Timeline for completion

### Verification Report
- For each design input requirement:
  - How was it verified?
  - What was the result?
  - Pass or fail?
  - Evidence of verification
- Summary of all verifications
- Any waivers or deviations
- Approval and sign-off

## Design Validation (Phase 6)

### Validation Definition
- Confirming device meets user needs and intended use
- Question: Does the design solve the intended problem?
- Testing with actual or representative users

### Validation Activities
- **User Testing**: Real users perform real tasks
- **Clinical Trials**: If applicable, patient testing
- **Field Studies**: Real-world usage
- **Usability Studies**: Can users operate safely?
- **Risk Analysis**: Are all hazards adequately controlled?

### Validation Plan
- How will we confirm device meets user needs?
- What user scenarios will be tested?
- What is the intended user population?
- How many users/patients?
- What metrics indicate successful validation?
- Acceptance criteria

### Validation Report
- Description of validation activities performed
- User population tested
- Test results and findings
- Clinical data (if applicable)
- Issues identified and resolution
- Conclusion: Device meets intended use
- Approval and sign-off

## Design Transfer (Phase 7)

### Definition
- Moving design from development to production
- Ensuring production process can reliably manufacture design

### Transfer Activities
- **Process Feasibility**: Can manufacturing process handle design?
- **Process Validation**: Does manufacturing process work reliably?
- **Controls**: Are process controls adequate?
- **Documentation**: Complete process documentation
- **Training**: Manufacturing staff trained

### Transfer Verification
- First production units tested
- Process outputs consistent with design
- Quality metrics established
- Process improvements incorporated

## Design Changes (Phase 8)

### Change Management Process
1. **Change Identification**: What is changing?
2. **Impact Analysis**: What is affected by change?
3. **Design Review**: Is change acceptable?
4. **Verification**: Does changed design still meet requirements?
5. **Risk Assessment**: Does change introduce new risks?
6. **Approval**: Authorized personnel approval
7. **Documentation**: Record of change and rationale
8. **Implementation**: Change made to design and documentation

### Change Documentation
- Change request or engineering change order (ECO)
- Technical description of change
- Reason for change (bug fix, improvement, new requirement)
- Risk assessment
- Verification results
- Impact on users (any new risks for existing users?)
- Approval signatures and date

### Design Change Triggers
- Bug fixes
- Performance improvements
- Regulatory changes
- Manufacturing issues
- Customer feedback
- Safety improvements
- Cost reductions

## Design History File (DHF)

### DHF Definition
- Compilation of complete design documentation
- Evidence of design control compliance
- Product-specific regulatory submission package

### DHF Contents
1. **Design Plan**: Design and development plan
2. **Input Documentation**: User needs, requirements specification
3. **Output Documentation**: Design specifications, architecture, detailed design
4. **Review Records**: Design review meeting minutes, reports
5. **Verification Records**: Test procedures, results, traceability
6. **Validation Records**: User testing, clinical data
7. **Risk Management**: Hazard analysis, risk controls
8. **Change Records**: Design changes and justification
9. **Traceability Matrix**: Requirements to design to verification
10. **Design Transfer**: Manufacturing process documentation

### DHF Organization
- Logical structure and clear labeling
- Cross-references between sections
- Complete and self-contained
- Ready for regulatory submission
- Indexed for easy navigation

## Common Design Control Deficiencies

1. **Inadequate Input Requirements**: User needs not clearly defined
2. **No Traceability**: Requirements not linked to design and verification
3. **Incomplete Output**: Design specification missing critical aspects
4. **Weak Design Review**: Review not rigorous or properly documented
5. **Insufficient Verification**: Testing inadequate or not comprehensive
6. **No User Validation**: Didn't test with actual users
7. **Poor Documentation**: Design rationale not explained
8. **Inadequate Risk Control**: Hazards identified but not addressed in design
9. **Change Control Issues**: Design changes not properly controlled
10. **Missing DHF**: Design documentation not compiled

## Design Control for Software

### Software-Specific Considerations
- **Requirements Specification**: Clear, traceable software requirements
- **Design Specification**: Architecture, algorithms, data structures
- **Verification**: Code review, unit testing, integration testing
- **Validation**: System testing, usability testing, clinical validation
- **Change Management**: Version control, regression testing

### Software Design Documentation
- Software architecture diagram
- Module specifications
- Data structure definitions
- Algorithm specifications (mathematical basis)
- Interface specifications
- Error handling specifications
- Performance specifications

### Software Verification
- Code review checklist
- Unit test results with coverage metrics
- Integration test results
- System test results
- Risk-based testing evidence
- Traceability matrix

## FDA Inspection Focus Areas

### Common Design Control 483 Observations
1. Design input not complete or documented
2. Design output incomplete
3. Design review not adequately performed
4. Verification insufficient
5. User validation missing
6. Risk management not linked to design
7. Change control not followed
8. Design history file incomplete
9. Software V&V inadequate
10. Traceability matrix missing

### Preparing for Inspection
- DHF organized and indexed
- All design documents present
- Reviews documented and signed
- Test results clear and conclusive
- Traceability complete
- Risk management integrated
- Changes properly controlled
- Design team available for questions
