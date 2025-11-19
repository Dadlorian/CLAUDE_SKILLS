# Requirements Traceability Matrix Reference

## Traceability Concept

### Definition
A systematic mapping between software requirements, design, code, and tests ensuring:
- Every requirement is implemented
- Every implementation is tested
- Every test traces back to requirement
- No orphaned code or tests

### Traceability Direction
- **Forward**: Requirement → Design → Code → Test
- **Backward**: Test → Code → Design → Requirement

### Why Traceability Matters
1. **Completeness**: No forgotten requirements
2. **Verification**: Every requirement verified
3. **Impact Analysis**: Understand change effects
4. **Gap Identification**: Find missing or extra implementations
5. **Regulatory Compliance**: FDA expects comprehensive traceability
6. **Maintenance**: Understand code purpose and connections

## Building the Traceability Matrix

### Step 1: Requirements Analysis
1. List all requirements from SRS
2. Assign unique requirement ID
3. Categorize by type (functional, non-functional, safety)
4. Define acceptance criteria
5. Example: REQ-GLUCOSE-001: "System shall accept blood glucose readings between 0-600 mg/dL"

### Step 2: Design Mapping
1. For each requirement, identify design elements
2. Design may implement single or multiple requirements
3. Design may require additional components not in requirements
4. Create cross-reference
5. Example: REQ-GLUCOSE-001 → DESIGN-INPUT-VALIDATION-001

### Step 3: Code Implementation
1. For each design element, identify code modules/functions
2. Map code to design elements
3. May have multiple code functions per design element
4. Create code-to-design mapping
5. Example: DESIGN-INPUT-VALIDATION-001 → glucose_validate() function

### Step 4: Test Case Mapping
1. For each requirement, create test case(s)
2. Test case verifies requirement
3. Test case should map to specific acceptance criteria
4. Create requirement-to-test mapping
5. Example: REQ-GLUCOSE-001 → TEST-GLUCOSE-001, TEST-GLUCOSE-002

### Step 5: Test Execution
1. Execute each test case
2. Record pass/fail
3. If fail, identify issue
4. Link back to code/design/requirement

## Traceability Matrix Format

### Spreadsheet Format
```
Req ID | Requirement | Design | Code Module | Test Case | Test Result | Comments
REQ-001 | Accept 0-600 | DESIGN-VAL-001 | glucose_validate() | TC-001 | PASS | Boundary testing
REQ-002 | Display value | DESIGN-UI-001 | display_glucose() | TC-002 | PASS | Usability tested
REQ-003 | Alert if high | DESIGN-ALERT-001 | check_high() | TC-003 | PASS | Risk control verified
```

### Database Format
- Requirements database (e.g., JAMA, Integrity)
- Links between artifacts
- Query and reporting capabilities
- Version control and audit trail

## Types of Traceability

### Vertical Traceability (Down)
System Requirements → Software Requirements → Design → Implementation → Test
- Ensures requirement is fully implemented and tested
- Identifies gaps in implementation or testing

### Horizontal Traceability (Across)
- Multiple requirements → Single implementation
- Single requirement → Multiple test cases
- Identifies reuse and commonality

### Backwards Traceability
Test → Code → Design → Requirement
- Ensures every test and code serves purpose
- Identifies orphaned code or tests

## Traceability for Different Artifact Types

### Safety Requirements
- **Requirements**: Safety requirements with pass/fail criteria
- **Design**: Design controls/features addressing hazard
- **Code**: Implementation of safety feature
- **Test**: Verification that safety control works
- **Special**: Linked to risk management (hazard)

### Performance Requirements
- **Requirements**: Performance specification (speed, accuracy)
- **Design**: Architecture supporting performance
- **Code**: Optimized implementation
- **Test**: Performance test verifying specification met
- **Special**: Performance test results documented

### User Interface Requirements
- **Requirements**: UI behavior and design
- **Design**: UI mockups, wireframes, specifications
- **Code**: UI implementation code
- **Test**: Usability testing, functional testing
- **Special**: User feedback integration

### Non-Functional Requirements
- **Requirements**: Reliability, scalability, maintainability
- **Design**: Architecture for non-functional requirements
- **Code**: Code quality, design patterns
- **Test**: Load testing, stress testing, reliability testing
- **Special**: Metrics and monitoring

## Traceability Tools

### Spreadsheet-Based
- **Pros**: Simple, flexible, requires no special tools
- **Cons**: Manual, error-prone, difficult for large projects
- **Tools**: Excel, Google Sheets

### Dedicated Requirements Management Tools
- **Tools**: JAMA Software, PTC Integrity, IBM DOORS, Atlassian Confluence
- **Pros**: Automated links, version control, reporting
- **Cons**: Expensive, learning curve
- **Features**: Baseline management, change impact analysis, audit trail

### Application Lifecycle Management (ALM)
- **Tools**: Azure DevOps, Jira, GitLab
- **Pros**: Integrated with development process
- **Cons**: May require customization
- **Features**: Requirements, design, code, tests integrated

### Integration with Version Control
- **Requirements**: In version control (documents or tools)
- **Code**: In version control (naturally)
- **Tests**: In version control (test code)
- **Traceability**: Links tracked in requirements tool

## Maintaining Traceability

### During Development
1. **Requirements Phase**: Create and baseline requirements
2. **Design Phase**: Map design to requirements
3. **Code Phase**: Map code to design
4. **Test Phase**: Map tests to requirements
5. **Execution Phase**: Update test results

### During Changes
1. **Change Identified**: New requirement or modification
2. **Impact Analysis**: What is affected?
   - Other requirements?
   - Design elements?
   - Code modules?
   - Test cases?
3. **Update Design**: Modify design as needed
4. **Update Code**: Implement change
5. **Update Tests**: Add or modify tests
6. **Update Traceability**: Link all changes

### Before Release
1. **Completeness Check**: All requirements traced
2. **Coverage Check**: All requirements have tests
3. **Test Results**: All tests passed
4. **Baseline**: Finalize traceability for release
5. **Archive**: Store in Design History File

## Common Traceability Gaps

### Requirement with No Design
- **Symptom**: Requirement doesn't appear in design
- **Cause**: Oversight, incomplete design
- **Fix**: Add design element or remove requirement
- **Impact**: Requirement not properly planned

### Design with No Requirement
- **Symptom**: Design element not tied to requirement
- **Cause**: Over-engineering, feature creep
- **Fix**: Justify if needed, remove if not
- **Impact**: Scope creep, unnecessary complexity

### Code with No Design
- **Symptom**: Code exists but not in design
- **Cause**: Shortcuts, emergency fixes
- **Fix**: Document in design or remove
- **Impact**: Maintenance and understanding difficult

### Test with No Requirement
- **Symptom**: Test doesn't verify requirement
- **Cause**: Extra testing, defensive programming
- **Fix**: Document purpose or consolidate
- **Impact**: Unnecessary testing effort

### Requirement with No Test
- **Symptom**: Requirement not tested
- **Cause**: Oversight, test coverage gaps
- **Fix**: Create test case(s)
- **Impact**: Requirement verification incomplete

## Traceability Metrics

### Coverage Percentage
- Requirements with tests: X% of total requirements
- Target: 100% for safety-critical software
- Acceptable: >95% for most devices
- Lower risk might allow lower percentage

### Test Coverage (Code)
- Percentage of code lines executed by tests
- Branch coverage more rigorous than statement coverage
- Target for Class C: >95%
- Target for Class B: >80%
- Target for Class A: >60%

### Traceability Completeness
- Forward traceability: % of requirements → design → code → test
- Backward traceability: % of code → design → requirement
- Goal: 100% for both directions

## Regulatory Expectations

### FDA Requirements
- Complete traceability matrix submitted with 510(k)
- All requirements traced to tests
- Test results document that requirements met
- Risk management hazards linked to controls
- Controls linked to design and tests

### Inspection Focus
- Is traceability matrix complete?
- Are all requirements traced?
- Do tests verify requirements?
- Are test results documented?
- Any gaps or unexplained elements?

### Documentation
- Maintain traceability matrix throughout development
- Include in Design History File
- Update with each change
- Sign and approve before release

## Best Practices

1. **Start Early**: Create traceability from first requirements
2. **Automate**: Use tool support for large projects
3. **Regular Review**: Review traceability monthly
4. **Change Management**: Update traceability for every change
5. **Clear IDs**: Use consistent, meaningful identifiers
6. **Document Rationale**: Explain non-obvious links
7. **Baseline**: Freeze traceability for releases
8. **Archive**: Keep historical traceability for each version
9. **Training**: Ensure team understands traceability importance
10. **Tools**: Use version control and tracking tools

## Traceability Example: Glucose Monitoring SaMD

```
Req ID | Requirement | Design Element | Code | Test | Result
------|-----------|-----------|-----------|---------|----------
REQ-001 | Accept readings 0-600 | INPUT-VAL | glucose_validate() | TC-001 | PASS
REQ-002 | Display reading | DISPLAY-UI | show_glucose() | TC-002 | PASS
REQ-003 | Alert if >200 | HIGH-ALERT | alert_high() | TC-003, TC-004 | PASS
REQ-004 | Secure data | SECURITY | encrypt_data() | TC-005 | PASS
REQ-005 | <2sec response | PERF | optimized_algorithm | TC-006 | PASS
```

Each test case includes:
- Test steps
- Expected result
- Actual result
- Links to requirement and code
- Verification that requirement met
