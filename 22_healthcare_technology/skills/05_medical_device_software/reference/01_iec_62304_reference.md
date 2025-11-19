# IEC 62304 Medical Device Software Lifecycle Reference

## Standard Overview

IEC 62304 specifies the software lifecycle model for medical device software. It's the primary international standard for medical device software development and is required or referenced in most regulatory submissions.

## Software Safety Classification

### Class A
- **Definition**: Software cannot cause injury or damage to health
- **Characteristics**: No direct patient data processing, informational only
- **Validation Level**: Minimal, basic requirements apply
- **Documentation**: Basic software requirements and architecture

### Class B
- **Definition**: Software function failure could cause non-serious injury
- **Characteristics**: Some patient monitoring or therapeutic support
- **Validation Level**: Moderate level of rigor required
- **Documentation**: Complete SRS, SDS, comprehensive testing
- **Example**: Reminder systems, basic dose calculations

### Class C
- **Definition**: Software function failure could cause death or serious injury
- **Characteristics**: Critical life support, drug delivery, diagnosis
- **Validation Level**: Highest level of rigor and documentation
- **Documentation**: All artifacts, extensive V&V, traceability matrices
- **Example**: Ventilator control software, imaging analysis for surgical planning

## Software Development Lifecycle

### Phase 1: Software Development Planning
- Define development strategy and approach
- Specify tools, standards, and procedures
- Plan configuration management
- Identify safety requirements
- Document development team roles
- Establish risk management plan

### Phase 2: Software Requirements Analysis
- Develop Software Requirements Specification (SRS)
- Define functional and non-functional requirements
- Ensure traceability from system requirements
- Include safety and performance requirements
- Define acceptance criteria
- Review and approve requirements

### Phase 3: Software Architectural Design
- Create Software Design Specification (SDS)
- Define system architecture
- Specify module interfaces
- Describe data flows
- Identify reusable and third-party components
- Perform architecture verification

### Phase 4: Software Unit Implementation
- Implement design in source code
- Follow coding standards
- Document implementation decisions
- Maintain version control
- Conduct unit testing and peer review
- Maintain traceability to design

### Phase 5: Software Unit Verification
- Execute unit tests against SDS
- Achieve required code coverage metrics
- Verify error handling
- Document all test results
- Maintain test-to-code traceability

### Phase 6: Software Integration
- Integrate units according to architectural design
- Verify module interactions
- Test interfaces
- Perform integration testing
- Maintain integration test documentation

### Phase 7: Software System Testing
- Verify complete system meets SRS
- Perform functional testing
- Execute performance testing
- Conduct stress and load testing
- Test edge cases and error conditions
- Document comprehensive test results

### Phase 8: Software Release and Maintenance
- Finalize software for release
- Complete configuration management
- Document software version
- Establish post-release monitoring
- Plan for software updates
- Manage version control and release procedures

## Documentation Requirements

### Software Development Plan
- Development strategy (lifecycle model)
- Safety classification and rationale
- Team roles and responsibilities
- Development tools and standards
- Risk management plan
- Configuration management plan
- Traceability strategy

### Software Requirements Specification
- Functional requirements (what system does)
- Non-functional requirements (performance, reliability)
- Safety requirements
- Regulatory requirements
- Labeling and user interface requirements
- Environment and interface specifications
- Acceptance criteria for each requirement

### Software Design Specification
- System architecture
- Detailed module specifications
- Data structures and algorithms
- Database schema (if applicable)
- Security specifications
- Performance specifications
- Module interaction and interface specifications

### Design History File
- Compilation of all design documents
- Requirements traceability matrix
- Design decisions and rationale
- Design verification reports
- Design review records
- All supporting documentation

### Verification Plan and Report
- Test strategy and approach
- Test case specifications
- Expected results and acceptance criteria
- Test execution report
- Test coverage metrics
- Traceability from tests to requirements

### Validation Plan and Report
- User and clinical validation strategy
- Acceptance testing approach
- Clinical evaluation plan (if applicable)
- Installation and operation testing
- Real-world usage validation
- Validation report with results

## Traceability Concepts

### Forward Traceability
System Requirements → SRS → SDS → Code → Unit Tests → Integration Tests → System Tests

### Backward Traceability
Code → SDS → SRS → System Requirements

### Complete Traceability Matrix
Every requirement must be:
1. Linked to parent requirement (if any)
2. Implemented in design
3. Implemented in code
4. Verified by tests
5. Documented with rationale

## Risk-Based Testing Approach

### Class A Software
- Basic functional testing
- Minimal boundary testing
- Documentation review

### Class B Software
- Comprehensive functional testing
- Boundary value analysis
- Decision table testing
- State transition testing
- Error guessing

### Class C Software
- All Class B testing plus:
- Path coverage (>90%)
- Formal verification of critical paths
- Adversarial testing
- Stress and load testing
- Long-duration stability testing

## Version Control and Configuration Management

### Version Identification
- Major.Minor.Patch format (e.g., 2.3.1)
- Version for all artifacts
- Release dates and contents
- Known issues and limitations
- Justification for version changes

### Change Management
- Change request process
- Change review and approval
- Impact analysis
- Verification of changes
- Traceability of changes
- Release notes

### Configuration Item Control
- All artifacts in version control
- Unique identification
- Clear ownership and responsibility
- Release procedures
- Archive and retention

## Common IEC 62304 Mistakes

1. **Incomplete Requirements**: Missing safety, regulatory, or non-functional requirements
2. **Weak Traceability**: Requirements not clearly linked through design and tests
3. **Insufficient Testing**: Test coverage too low for safety classification
4. **Missing Rationale**: Design decisions not documented with justification
5. **Poor Version Control**: Software versions not clearly identified
6. **Incomplete DHF**: Design History File missing required artifacts
7. **Test Procedures**: Tests not detailed enough to be reproducible
8. **Risk Management**: Hazard analysis not linked to software requirements
9. **Third-Party Code**: External libraries not adequately assessed
10. **Legacy Code**: Old code not brought into compliance with standards

## Adapting IEC 62304 for Agile Development

### Compatibility Approach
1. **Phase Gates**: Use sprints/iterations to deliver complete phases
2. **Incremental Documentation**: Update artifacts each iteration
3. **Test-Driven Development**: Tests drive requirement clarity
4. **Continuous Traceability**: Maintain traceability matrix throughout development
5. **Risk-Based Planning**: Prioritize high-risk features first
6. **Automated Testing**: Regression testing as development progresses
7. **Definition of Done**: Include all requirements for that feature
8. **Release Planning**: Determine which iterations constitute releasable increment
9. **Retrospectives**: Continuous process improvement
10. **Regulatory Alignment**: Keep documentation current for submission readiness

## Real-World Example: Glucose Monitoring SaMD

### Classification
- Software processes patient blood glucose readings
- Calculates insulin dosing recommendations
- Could cause serious injury if calculation is wrong
- **Verdict**: Class C software

### Key Requirements
- Accurate glucose reading processing
- Validated algorithm for dosing recommendations
- Audit trail of all recommendations
- User interface with safety interlocks
- Network security for data transmission

### Testing Strategy
- Unit tests for algorithm validation
- Integration tests for data flow
- System tests for user scenarios
- Performance tests for response time
- Stress tests for concurrent users
- Clinical validation with patient data

### Documentation
- SDS specifying algorithm with mathematical basis
- Complete V&V plan covering all scenarios
- Traceability showing algorithm is tested
- Risk management showing hazards are addressed
- Cybersecurity assessment for data transmission
