# Software Validation Protocols Reference

## Overview

Software validation provides objective evidence that software specifications conform to user needs and intended uses. This reference covers IQ/OQ/PQ protocols, test design, execution, and documentation for medical device software.

## Validation Fundamentals

### Definition (FDA)
"Confirmation by examination and provision of objective evidence that software specifications conform to user needs and intended uses, and that the particular requirements implemented through software can be consistently fulfilled."

### Key Principles

1. **Software validation is a part of design validation**
2. **Software validation is risk-based**
3. **"If it's not documented, it didn't happen"**
4. **Validation must be performed on final released version**
5. **Validation requires actual or simulated use conditions**
6. **Validation must include user needs, not just requirements**

### Validation vs. Verification

**Verification**: "Did we build the product right?"
- Requirements → Code
- Developer testing
- Unit, integration, system tests

**Validation**: "Did we build the right product?"
- User Needs → Product
- User testing
- IQ/OQ/PQ, clinical validation

## IQ/OQ/PQ Framework

### Installation Qualification (IQ)

**Definition:**
Documented verification that all key aspects of software installation adhere to appropriate codes and approved design intentions and that manufacturer's recommendations are suitably considered.

**Purpose:**
- Verify software installed correctly
- Confirm installation environment meets requirements
- Document installation configuration

**IQ Activities:**

1. **Environment Verification**
   - Operating system version
   - Hardware specifications (CPU, RAM, disk space)
   - Database version and configuration
   - Network configuration
   - Security settings

2. **Software Installation**
   - Installation procedure followed
   - All components installed
   - File integrity verified (checksums)
   - License activation
   - Version verification

3. **Configuration**
   - System settings configured per specifications
   - User accounts created
   - Permissions assigned
   - Network connections established
   - Database initialized

4. **Documentation**
   - Installation logs
   - Configuration files
   - Network diagrams
   - User account list

**IQ Test Cases Example:**
```
IQ-001: Verify operating system version
IQ-002: Verify hardware meets minimum requirements
IQ-003: Verify software version installed
IQ-004: Verify all software components present
IQ-005: Verify file integrity (MD5/SHA checksums)
IQ-006: Verify database created and accessible
IQ-007: Verify network connectivity
IQ-008: Verify security certificates installed
IQ-009: Verify backup procedures configured
IQ-010: Verify system logs configured
```

### Operational Qualification (OQ)

**Definition:**
Documented verification that the system operates according to the operational specification in the selected environment.

**Purpose:**
- Verify all software functions work correctly
- Confirm software meets functional requirements
- Test normal operating conditions

**OQ Activities:**

1. **Functional Testing**
   - Test each software requirement
   - Verify inputs/outputs
   - Test calculations and algorithms
   - Test user interfaces
   - Test reports and displays

2. **Interface Testing**
   - Hardware interfaces
   - Software interfaces
   - Network interfaces
   - Database interfaces
   - User interface

3. **Security Testing**
   - User authentication
   - Access controls
   - Audit trails
   - Data encryption
   - Session management

4. **Error Handling**
   - Invalid inputs
   - Boundary conditions
   - Exception handling
   - Error messages
   - Recovery procedures

**OQ Test Cases Example:**
```
OQ-001: Verify user login/logout functionality
OQ-002: Verify patient data entry and validation
OQ-003: Verify calculation algorithm accuracy
OQ-004: Verify report generation
OQ-005: Verify data export functionality
OQ-006: Verify alarm functionality
OQ-007: Verify access controls (user roles)
OQ-008: Verify audit trail captures user actions
OQ-009: Verify data backup and restore
OQ-010: Verify system response to network failure
```

### Performance Qualification (PQ)

**Definition:**
Documented verification that the system performs according to defined acceptance criteria under normal operating conditions and worst-case scenarios, demonstrating fitness for intended use.

**Purpose:**
- Verify software meets user needs
- Validate clinical/operational performance
- Test under realistic conditions
- Demonstrate fitness for intended use

**PQ Activities:**

1. **Clinical Workflows**
   - End-to-end clinical scenarios
   - Typical patient cases
   - Complex/edge cases
   - Multi-user scenarios

2. **Performance Testing**
   - Response time under load
   - Concurrent users
   - Large datasets
   - Peak usage periods

3. **Usability Validation**
   - User acceptance testing
   - Task completion
   - Error rates
   - User satisfaction

4. **Reliability Testing**
   - Extended operation
   - Stress testing
   - Failure recovery
   - Data integrity over time

**PQ Test Cases Example:**
```
PQ-001: Complete patient admission workflow
PQ-002: Process 100 patient records
PQ-003: Generate monthly reports with actual data
PQ-004: Simulate 50 concurrent users
PQ-005: Verify system uptime over 7-day period
PQ-006: Validate clinical decision support accuracy
PQ-007: User acceptance by clinical staff
PQ-008: Verify data integrity after backup/restore
PQ-009: Simulate system failure and recovery
PQ-010: Validate integration with hospital systems
```

## Validation Protocol Structure

### Protocol Header

```
Title: [Validation Protocol for Device/Software Name]
Protocol Number: [VP-XXXX-YY]
Version: [X.X]
Date: [DD-MMM-YYYY]
Device/Software: [Name and Version]
Prepared By: [Name, Title, Date, Signature]
Reviewed By: [Name, Title, Date, Signature]
Approved By: [Name, Title, Date, Signature]
```

### 1. Introduction

**Contents:**
- Purpose of validation
- Scope of validation
- Device/software description
- Intended use
- Regulatory context

### 2. Validation Team

**Roles and Responsibilities:**
- Validation Lead
- Test Engineers
- Clinical/Domain Experts
- Quality Assurance
- Regulatory Affairs
- IT/System Administrators

### 3. Test Environment

**Description:**
- Hardware specifications
- Operating system
- Database system
- Network configuration
- Security environment
- Test data sources

### 4. Acceptance Criteria

**Define:**
- Success criteria for protocol
- Pass/fail criteria for individual tests
- Measurement tolerances
- Data acceptance limits
- Conditions for protocol completion

**Example:**
```
Overall Acceptance:
- 100% of critical test cases pass
- ≥95% of non-critical test cases pass
- All deviations investigated and resolved
- No unresolved critical defects
```

### 5. Test Cases

**For Each Test Case:**

```
Test Case ID: [TC-XXX]
Test Type: [IQ/OQ/PQ]
Requirement Traceability: [REQ-XXX]
Risk Traceability: [RISK-XXX]
Test Objective: [What is being tested]

Prerequisites:
- [Conditions that must be met]

Test Steps:
1. [Action to perform]
2. [Action to perform]
...

Expected Results:
- [What should happen]

Actual Results:
- [Filled during execution]

Pass/Fail: [Checked during execution]

Tester: [Name, Date, Signature]

Deviations/Comments:
- [Any issues or notes]
```

### 6. Test Data

**Description:**
- Source of test data
- Data sanitization procedures
- Synthetic vs. actual data
- Data privacy compliance

### 7. Deviation Handling

**Procedure:**
- How deviations documented
- Investigation process
- Resolution requirements
- Re-test requirements

### 8. Test Execution

**Records:**
- Execution schedule
- Test environment state
- Software version tested
- Tester assignments

### 9. Traceability Matrix

**Link:**
- User Needs → Requirements → Test Cases
- Risks → Controls → Test Cases

### 10. Appendices

**Include:**
- Test data samples
- Screenshots
- Output samples
- Configuration files

## Test Case Design

### Test Coverage

**Requirements Coverage:**
- Every software requirement has ≥1 test case
- Critical requirements have multiple test cases
- Traceability matrix documents coverage

**Risk Coverage:**
- Every identified risk has verification test
- Risk controls verified through testing
- High-risk areas have enhanced testing

**Code Coverage (for Verification):**
- Class C: 100% statement or branch coverage
- Class B: Unit testing or code review
- Class A: No specific requirement

### Test Types

**1. Functional Testing**
- Normal operations
- All features/functions
- Input/output validation
- Calculations and algorithms

**2. Boundary Testing**
- Minimum values
- Maximum values
- Out-of-range values
- Null/empty inputs

**3. Negative Testing**
- Invalid inputs
- Error conditions
- Exception handling
- Recovery from errors

**4. Interface Testing**
- User interface elements
- Hardware interfaces
- Software interfaces
- API testing

**5. Security Testing**
- Authentication
- Authorization
- Data protection
- Audit trails

**6. Performance Testing**
- Response times
- Throughput
- Concurrent users
- Resource utilization

**7. Usability Testing**
- Task completion
- Error rates
- User satisfaction
- Learning curve

**8. Regression Testing**
- Verify bug fixes
- Verify no new issues
- Test after changes
- Automated where possible

### Test Data Strategy

**Sources:**
1. **Synthetic Data**: Created for testing
2. **Anonymized Data**: Real data de-identified
3. **Simulated Data**: Generated to mimic real patterns
4. **Edge Cases**: Unusual but valid scenarios

**Characteristics:**
- Representative of actual use
- Covers range of possibilities
- Includes edge cases
- Privacy-compliant
- Documented provenance

## Validation Execution

### Pre-Execution Activities

1. **Protocol Approval**
   - All signatures obtained
   - Protocol finalized (no changes during execution)

2. **Environment Preparation**
   - Test system configured
   - Software installed per IQ
   - Test data loaded
   - Tools prepared

3. **Team Training**
   - Testers trained on protocol
   - Roles and responsibilities understood
   - Deviation procedures reviewed

### During Execution

**Test Execution Rules:**
1. Follow protocol exactly (no deviations from procedure)
2. Document all results contemporaneously
3. Do not leave blank spaces
4. Cross out errors with single line, initial and date
5. No white-out or erasure
6. Record unexpected observations
7. Escalate failures immediately

**Documentation:**
- Complete all fields
- Record actual results
- Mark pass/fail
- Sign and date
- Attach supporting evidence (screenshots, logs)

### Deviation Management

**When Test Fails or Deviates:**

1. **Document**
   - Describe what happened
   - Note expected vs. actual
   - Record evidence

2. **Investigate**
   - Determine root cause
   - Classify severity
   - Assess impact

3. **Resolve**
   - Fix if software defect
   - Clarify if requirement misunderstanding
   - Modify if protocol error (with approval)

4. **Re-Test**
   - Execute test again after fix
   - Verify resolution
   - Document re-test results

**Deviation Severity:**
- **Critical**: Affects patient safety or device effectiveness
- **Major**: Significant impact on functionality
- **Minor**: Cosmetic or minor issues

### Post-Execution Activities

1. **Data Review**
   - Verify all tests executed
   - Check all data complete
   - Review pass/fail results

2. **Deviation Review**
   - All deviations resolved
   - Re-tests completed
   - Impact assessed

3. **Traceability Check**
   - All requirements tested
   - All risks addressed
   - No gaps in coverage

## Validation Report

### Report Structure

**1. Executive Summary**
- Validation objective
- Overall results
- Conclusion (pass/fail)

**2. Introduction**
- Device/software description
- Validation scope
- Regulatory basis

**3. Validation Approach**
- Methodology
- Test environment
- Validation team

**4. Test Results Summary**

```
Test Category    Total    Passed    Failed    Pass Rate
-------------    -----    ------    ------    ---------
IQ                 10       10         0        100%
OQ                 50       49         1         98%
PQ                 20       20         0        100%
-------------    -----    ------    ------    ---------
Total              80       79         1         99%
```

**5. Deviations and Resolutions**

```
Deviation ID    Severity    Description    Resolution    Status
------------    --------    -----------    ----------    ------
DEV-001         Minor       Typo in UI     Corrected     Closed
```

**6. Traceability Analysis**
- Requirements coverage
- Risk coverage
- Gaps (if any)

**7. Conclusion**
- Acceptance criteria met (yes/no)
- Software validated (yes/no)
- Readiness for release (yes/no)
- Limitations or caveats

**8. Approval Signatures**
- Validation Lead
- Quality Assurance
- Regulatory Affairs
- Management

**9. Appendices**
- Completed test protocols
- Deviation reports
- Traceability matrix
- Supporting evidence

## Revalidation

### Triggers for Revalidation

1. **Software Changes**
   - New features added
   - Existing features modified
   - Bug fixes affecting functionality

2. **Environmental Changes**
   - Operating system upgrade
   - Database version change
   - Hardware platform change

3. **Regulatory Changes**
   - New regulatory requirements
   - Standard updates
   - Guideline changes

4. **Post-Market Issues**
   - Complaints indicating validation gap
   - Adverse events
   - Field failures

### Revalidation Approach

**Full Revalidation:**
- Major software changes
- Complete IQ/OQ/PQ
- New validation report

**Partial Revalidation:**
- Minor software changes
- Regression testing
- Impacted areas only
- Validation supplement

**Change Assessment:**
- Evaluate impact of change
- Determine revalidation extent
- Document rationale
- Obtain approval

## Special Validation Considerations

### Retrospective Validation
- For legacy software already in use
- Document existing evidence
- Perform gap analysis
- Execute tests for gaps
- More challenging but sometimes necessary

### Concurrent Validation
- Validation during production
- For custom/configured systems
- First installations serve as validation
- Higher risk, requires extensive monitoring

### Prospective Validation
- Standard approach
- Validation before release
- Preferred method

### Continuous Software Validation
- For Agile/DevOps environments
- Automated testing
- Continuous integration/deployment
- Risk-based regression suites
- Emerging regulatory acceptance

## Automated Testing in Validation

### Benefits
- Repeatable
- Faster execution
- Regression testing enabler
- Consistent results

### Challenges
- Tool qualification required
- Script validation needed
- Maintenance overhead
- Not suitable for all tests (e.g., usability)

### Tool Qualification
Per IEC 62304 Annex C:
- If tool automates verification, must be qualified
- Validation of tool itself
- Documentation of tool version
- Change control for tools

## Best Practices

1. **Start Early**: Plan validation during design
2. **Risk-Based**: Focus on high-risk areas
3. **Traceability**: Maintain bidirectional traceability
4. **Independence**: Separate validation from development
5. **Realistic Conditions**: Test in actual use environment
6. **Complete Documentation**: Document everything contemporaneously
7. **User Involvement**: Include end users in PQ
8. **Automate Wisely**: Automate regression, keep exploratory manual
9. **Version Control**: Lock protocol versions before execution
10. **Learn and Improve**: Analyze failures to improve process

## Common Validation Deficiencies

1. **Inadequate Test Coverage**
   - Not all requirements tested
   - Edge cases missed
   - Risk controls not verified

2. **Poor Documentation**
   - Incomplete test results
   - Missing signatures/dates
   - Deviations not documented

3. **Validation on Wrong Version**
   - Not final released version
   - Validation doesn't match production

4. **Unrealistic Test Conditions**
   - Lab environment, not clinical
   - Synthetic data not representative

5. **Inadequate Revalidation**
   - Changes not revalidated
   - Impact not assessed

6. **Traceability Gaps**
   - Requirements without tests
   - Risks without verification

---

**Key Takeaway**: Software validation proves that software meets user needs under actual use conditions. IQ/OQ/PQ framework provides systematic approach. Complete, contemporaneous documentation is essential. Validation is not one-time—changes require revalidation.
