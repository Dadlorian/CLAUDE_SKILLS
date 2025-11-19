# IEC 62304 Implementation Guide

## Step-by-Step Implementation

### Phase 1: Planning and Preparation (Weeks 1-2)

#### Step 1.1: Software Safety Classification
**Actions:**
1. Conduct hazard analysis per ISO 14971
2. For each potential failure mode, assess:
   - Could it result in death or serious injury? → Class C
   - Could it result in non-serious injury? → Class B
   - No injury possible? → Class A
3. Assign highest applicable class to software system
4. Document classification rationale

**Deliverable:** Software Safety Classification Document

#### Step 1.2: Create Software Development Plan
**Template Contents:**
```markdown
# Software Development Plan

## 1. Project Overview
- Device name and description
- Software safety class
- Regulatory target (FDA, EU MDR, etc.)

## 2. Development Organization
- Team structure
- Roles and responsibilities
- Required competencies

## 3. Development Lifecycle Model
- Methodology (V-Model, Agile, hybrid)
- Phase descriptions
- Phase transition criteria

## 4. Deliverables
- Requirements documents
- Design documents
- Test documents
- Risk management outputs

## 5. Standards and Tools
- Coding standards (MISRA C, CERT C++)
- Development environment
- Configuration management tools
- Testing tools

## 6. Activities
- Requirements analysis
- Design
- Implementation
- Integration
- Testing
- Risk management activities

## 7. Verification Methods
- Unit testing approach
- Integration testing
- System testing
- Code coverage goals (Class C: 100% statement/branch)

## 8. Configuration Management
- Version control procedures
- Baseline management
- Change control process

## 9. Problem Resolution
- Problem reporting
- Investigation process
- Resolution procedures

## 10. Risk Management
- Integration with ISO 14971 process
- Hazard analysis updates
- Risk control verification
```

**Deliverable:** Approved Software Development Plan

#### Step 1.3: Establish Configuration Management
**Actions:**
1. Set up version control system (Git, SVN)
2. Define branching strategy
3. Establish naming conventions
4. Configure automated builds
5. Set up issue tracking system

**Configuration Items:**
- Source code
- Requirements documents
- Design documents
- Test documents
- Build scripts
- SOUP components

**Deliverable:** Configuration Management Plan

#### Step 1.4: Establish Problem Resolution Process
**Actions:**
1. Set up bug tracking system
2. Define severity levels:
   - Critical: Patient safety impact
   - Major: Significant functional impact
   - Minor: Cosmetic/usability
3. Define investigation procedures
4. Define resolution workflow

**Deliverable:** Problem Resolution Procedure

### Phase 2: Requirements Analysis (Weeks 3-6)

#### Step 2.1: Define System Requirements
**Actions:**
1. Gather user needs
2. Define intended use
3. Define system requirements
4. Review with stakeholders

**Deliverable:** System Requirements Specification

#### Step 2.2: Derive Software Requirements
**For Each System Requirement:**
1. Derive software requirement(s)
2. Assign unique identifier (SRS-001, SRS-002...)
3. Write requirement clearly and testably
4. Link to system requirement (traceability)

**Software Requirement Categories:**
- Functional requirements
- Performance requirements
- Interface requirements
- Data requirements
- Security requirements
- Usability requirements
- Regulatory requirements
- Risk control requirements (from ISO 14971)

**Requirement Quality Checklist:**
- [ ] Uniquely identified
- [ ] Clear and unambiguous
- [ ] Testable/verifiable
- [ ] Complete
- [ ] Consistent with other requirements
- [ ] Traceable to system requirement
- [ ] Linked to risk controls (if applicable)

**Deliverable:** Software Requirements Specification (SRS)

#### Step 2.3: Conduct Requirements Review
**Review Team:**
- Software developers
- Systems engineers
- Risk management lead
- Quality assurance
- Clinical/domain experts

**Review Checklist:**
- All system requirements addressed
- Requirements clear and testable
- No contradictions
- All risk controls included
- Traceability complete

**Deliverable:** Requirements Review Record

### Phase 3: Software Architecture Design (Weeks 7-10)

#### Step 3.1: Develop Software Architecture
**Actions:**
1. Identify major software components
2. Define component interfaces
3. Identify SOUP items
4. Document segregation (if mixed safety classes)
5. Create architecture diagrams

**Architecture Documentation:**
```markdown
# Software Architecture

## System Overview
[High-level description, block diagram]

## Software Items
| Item | Description | Responsibility | Safety Class |
|------|-------------|----------------|--------------|
| ControlModule | Therapy control | Dosing algorithm | C |
| DisplayModule | User interface | Display data | B |
| LoggingModule | Event logging | Record events | A |

## Interfaces
### External Interfaces
- Hardware: Pump motor, sensors
- Network: Hospital EMR system
- User: Touchscreen interface

### Internal Interfaces
[Component interaction diagrams]

## SOUP Items
| Name | Version | Supplier | Purpose | Functional Requirements |
|------|---------|----------|---------|------------------------|
| OpenSSL | 3.0.1 | OpenSSL Foundation | Encryption | AES-256, TLS 1.3 |
| SQLite | 3.40.0 | SQLite Consortium | Database | Store patient data |

## Segregation Strategy (if applicable)
[How safety-critical components are isolated from non-critical]
```

**Deliverable:** Software Architecture Document

#### Step 3.2: Verify Software Architecture
**Verification Activities:**
- Architecture review meeting
- Traceability verification (requirements → architecture)
- Coverage analysis (all requirements addressed)
- SOUP evaluation

**Deliverable:** Architecture Verification Record

### Phase 4: Detailed Design (Weeks 11-14) [Class B/C Only]

#### Step 4.1: Create Detailed Design
**For Each Software Unit:**
- Unit name and purpose
- Inputs and outputs
- Processing logic
- Error handling
- Data structures
- Algorithms (pseudocode or flowcharts)

**Deliverable:** Detailed Design Document

#### Step 4.2: Verify Detailed Design
**Verification:**
- Design review
- Traceability to architecture
- Completeness check

**Deliverable:** Design Verification Record

### Phase 5: Implementation (Weeks 15-24)

#### Step 5.1: Establish Coding Standards
**Select Standards:**
- Class C: MISRA C or CERT C (mandatory)
- Class B: Coding style guide (recommended)
- Class A: Basic style guide

**Configure Tools:**
- Static analysis tools
- Code formatters
- Linters

**Deliverable:** Coding Standards Document

#### Step 5.2: Implement Software Units
**Development Process:**
1. Implement unit per detailed design
2. Follow coding standards
3. Include inline comments
4. Handle errors appropriately
5. Commit to version control with meaningful messages

**Code Quality Practices:**
- Defensive programming
- Input validation
- Error logging
- Clear variable naming
- Modular design

#### Step 5.3: Unit Verification

**Class A:** No specific requirement (optional testing)

**Class B:** Choose one:
- Unit testing, OR
- Code review

**Class C:** All required:
- Unit testing with 100% statement coverage OR 100% branch coverage
- Code review
- Static analysis

**Unit Test Process:**
1. Write test cases for unit
2. Execute tests
3. Measure code coverage
4. Document results
5. Fix failures and re-test

**Code Review Process:**
1. Create review checklist
2. Peer review code
3. Document findings
4. Address issues
5. Re-review

**Deliverable:** Unit Verification Records, Coverage Reports

### Phase 6: Integration (Weeks 25-28)

#### Step 6.1: Integration Planning
**Define:**
- Integration sequence
- Integration tests for each step
- Test environment

#### Step 6.2: Integrate Software Items
**Incremental Integration:**
1. Integrate two units
2. Test integration
3. Add next unit
4. Test integration
5. Repeat until complete

**Integration Test Coverage:**
- Class A: Not specified
- Class B: Test all software items
- Class C: Test all software items with comprehensive tests

**Deliverable:** Integration Test Report

### Phase 7: System Testing (Weeks 29-34)

#### Step 7.1: Develop System Test Plan
**Contents:**
- Test objectives
- Test environment
- Test data
- Test cases (one per software requirement minimum)
- Acceptance criteria
- Regression test strategy

**Deliverable:** System Test Plan

#### Step 7.2: Execute System Tests
**Process:**
1. Set up test environment
2. Execute tests per plan
3. Document results (pass/fail)
4. Investigate failures
5. Fix defects
6. Re-test
7. Perform regression testing

**Test Coverage:**
- All software requirements tested
- Traceability matrix updated
- Edge cases included
- Error handling verified

**Deliverable:** System Test Report, Traceability Matrix

### Phase 8: Risk Management Integration (Ongoing)

#### Step 8.1: Software Hazard Analysis
**For Each Hazard:**
1. Identify software contribution to hazard
2. Identify potential causes (defects, timing, user error)
3. Document in risk management file
4. Derive risk control requirements

**Deliverable:** Software Hazard Analysis

#### Step 8.2: Implement Risk Controls
**Actions:**
1. Incorporate risk control requirements into SRS
2. Implement controls in design/code
3. Verify controls in testing
4. Trace hazards → controls → tests

**Deliverable:** Risk Control Traceability

#### Step 8.3: Verify Risk Controls
**Verification:**
- Each risk control has test case(s)
- Tests demonstrate effectiveness
- Results documented in risk management file

**Deliverable:** Risk Control Verification Report

### Phase 9: Release (Week 35)

#### Step 9.1: Prepare Release Package
**Release Contents:**
- Executable software (with version identifier)
- User documentation
- Installation instructions
- Known residual anomalies
- Release notes

#### Step 9.2: Evaluate Residual Anomalies
**For Each Known Bug:**
- Describe anomaly
- Assess patient safety impact
- Determine acceptability
- Document rationale if accepted
- Plan resolution if not acceptable

**Deliverable:** Known Anomalies List

#### Step 9.3: Archive Software Configuration
**Archive:**
- Source code (specific version/tag)
- Executable
- All documentation
- Build environment specification
- All verification/validation records

**Deliverable:** Release Archive, Software Configuration Index

#### Step 9.4: Release Approval
**Final Review:**
- All requirements verified
- All tests passed (or anomalies evaluated)
- Risk management complete
- Documentation complete
- Design History File complete

**Deliverable:** Software Release Record

### Phase 10: Maintenance (Post-Release)

#### Step 10.1: Establish Maintenance Plan
**Plan Contents:**
- Feedback collection procedures
- Problem evaluation criteria
- Modification process
- Communication procedures

**Deliverable:** Maintenance Plan

#### Step 10.2: Problem and Modification Analysis
**For Each Problem Report:**
1. Document problem
2. Verify and reproduce
3. Analyze impact on safety and risk analysis
4. Determine if modification needed
5. Communicate to users/regulators if needed

#### Step 10.3: Implement Modifications
**Process:**
1. Use development process for changes (requirements → design → implementation → testing)
2. Perform regression analysis
3. Update documentation
4. Update risk analysis
5. Verify modification
6. Release per release process

**Deliverable:** Modification Records

## Checklists and Templates

### Project Kickoff Checklist
- [ ] Software safety class determined
- [ ] Development team identified
- [ ] Development plan created and approved
- [ ] Configuration management established
- [ ] Problem resolution process established
- [ ] Development tools selected and configured
- [ ] Coding standards selected

### Requirements Phase Checklist
- [ ] User needs documented
- [ ] System requirements defined
- [ ] Software requirements derived
- [ ] All requirements uniquely identified
- [ ] All requirements testable
- [ ] Risk controls incorporated
- [ ] Traceability established
- [ ] Requirements reviewed and approved

### Design Phase Checklist
- [ ] Software architecture created
- [ ] Software items identified
- [ ] Interfaces defined
- [ ] SOUP items identified and specified
- [ ] Architecture verified
- [ ] Detailed design created (Class B/C)
- [ ] Detailed design verified (Class B/C)

### Implementation Phase Checklist
- [ ] Coding standards established
- [ ] Static analysis configured
- [ ] Code implemented per design
- [ ] Unit tests created and executed (Class B/C)
- [ ] Code coverage achieved (Class C: 100% statement or branch)
- [ ] Code reviews conducted
- [ ] Unit verification documented

### Testing Phase Checklist
- [ ] Integration test plan created
- [ ] Integration testing completed
- [ ] System test plan created
- [ ] All requirements have test cases
- [ ] System tests executed
- [ ] All tests passed or anomalies evaluated
- [ ] Regression testing completed
- [ ] Traceability matrix complete

### Release Checklist
- [ ] All verification activities complete
- [ ] All validation activities complete
- [ ] Risk management activities complete
- [ ] Known anomalies evaluated
- [ ] Software configuration archived
- [ ] Design History File complete
- [ ] Release approved

## Tools and Automation

### Recommended Tools

**Requirements Management:**
- Jama Connect
- IBM DOORS
- Helix RM
- Polarion

**Version Control:**
- Git
- Subversion
- Perforce

**Issue Tracking:**
- Jira
- Bugzilla
- Azure DevOps

**Static Analysis:**
- Coverity
- Klocwork
- SonarQube
- PC-lint

**Testing:**
- Google Test (C++)
- JUnit (Java)
- pytest (Python)
- NUnit (.NET)

**Code Coverage:**
- gcov/lcov
- Bullseye Coverage
- Squish Coco

**Build Automation:**
- Jenkins
- GitLab CI/CD
- Azure Pipelines

## Common Pitfalls and Solutions

**Pitfall 1: Classification Too Late**
- Solution: Classify software before planning

**Pitfall 2: Inadequate Traceability**
- Solution: Use requirements management tool from start

**Pitfall 3: Testing as Afterthought**
- Solution: Plan testing during requirements phase

**Pitfall 4: Ignoring SOUP**
- Solution: Identify and document SOUP early, monitor continuously

**Pitfall 5: Weak Requirements**
- Solution: Use clear templates, rigorous reviews

**Pitfall 6: Insufficient Code Coverage**
- Solution: Automated coverage measurement, enforce thresholds

**Pitfall 7: Poor Change Control**
- Solution: Formal change process, impact analysis mandatory

**Pitfall 8: Documentation Gaps**
- Solution: Document contemporaneously, use templates

## Success Metrics

- Requirements traceability: 100%
- Test coverage: 100% of requirements
- Code coverage (Class C): ≥100% statement or branch
- Design review participation: All required roles
- Code review: 100% of code
- Anomaly closure: All critical/major before release

## Timeline Summary

**Small Project (Class A/B):** 6-9 months
**Medium Project (Class B/C):** 9-15 months
**Large Project (Class C with novelty):** 15-24 months

Add validation and regulatory submission time on top.

---

**Key Takeaway**: IEC 62304 implementation is systematic and documentation-intensive. Start with proper classification, maintain rigorous traceability, scale rigor to safety class, integrate risk management throughout, and document everything contemporaneously.
