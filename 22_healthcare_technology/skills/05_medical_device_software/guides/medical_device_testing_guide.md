# Medical Device Testing Guide

## Test Strategy Overview

Medical device software testing must be:
- **Comprehensive**: All requirements tested
- **Risk-Based**: More testing for high-risk areas
- **Documented**: All tests and results recorded
- **Traceable**: Tests linked to requirements
- **Repeatable**: Same results if repeated

## Test Levels

### 1. Unit Testing

**Purpose**: Verify individual software units work correctly

**Scope**:
- Individual functions/methods
- Individual modules
- Isolated components

**When**: During implementation

**Class-Specific Requirements**:
- **Class A**: Optional
- **Class B**: Required (testing OR code review)
- **Class C**: Required with code coverage

**Code Coverage (Class C)**:
- 100% statement coverage OR
- 100% branch coverage
- May require MC/DC for critical algorithms

**Example Test:**
```python
# Unit test for dose calculation
def test_calculate_bolus_normal():
    """Test normal bolus calculation"""
    profile = PatientProfile(carb_ratio=10, correction_factor=50, target_bg=100)
    
    # Test case: 50g carbs, BG=150
    result = calculate_bolus(carbs=50, blood_glucose=150, profile=profile)
    
    # Expected: 50/10 + (150-100)/50 = 5 + 1 = 6 units
    assert result == 6.0, f"Expected 6.0, got {result}"

def test_calculate_bolus_max_limit():
    """Test that dose is limited to maximum"""
    profile = PatientProfile(carb_ratio=1, correction_factor=1, target_bg=100)
    
    # Extreme inputs that would exceed limit
    result = calculate_bolus(carbs=1000, blood_glucose=1000, profile=profile)
    
    # Should be limited to max (e.g., 25 units)
    assert result <= 25.0, f"Dose exceeded maximum: {result}"

def test_calculate_bolus_negative():
    """Test that negative dose becomes zero"""
    profile = PatientProfile(carb_ratio=10, correction_factor=50, target_bg=200)
    
    # Low BG, no carbs -> negative correction
    result = calculate_bolus(carbs=0, blood_glucose=50, profile=profile)
    
    # Should be zero, not negative
    assert result == 0.0, f"Expected 0.0, got {result}"
```

**Code Coverage Measurement:**
```bash
# Python example with coverage.py
pytest --cov=src tests/
coverage report
coverage html  # Generate HTML report

# C++ example with gcov
g++ -fprofile-arcs -ftest-coverage source.cpp -o test
./test
gcov source.cpp
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory out
```

### 2. Integration Testing

**Purpose**: Verify software units work together correctly

**Scope**:
- Interfaces between units
- Data flow between components
- Integration with SOUP
- Integration with hardware

**When**: After unit testing, during integration phase

**Test Approach**:
```markdown
# Integration Test Plan

## Integration Sequence
1. DoseCalculator + DataValidator
2. UserInterface + DoseCalculator
3. AlarmManager + DoseCalculator
4. All components + DatabaseManager
5. Complete system

## Test Cases

IT-001: Dose calculation to motor control
- Input dose via UI
- Verify DoseCalculator receives correct input
- Verify MotorControl receives correct command

IT-002: Alarm generation and display
- Simulate alarm condition
- Verify AlarmManager generates alarm
- Verify UserInterface displays alarm

IT-003: Data persistence
- Enter patient data
- Verify DatabaseManager stores data
- Retrieve data
- Verify data integrity
```

**Interface Testing Example:**
```python
def test_dose_calculator_to_motor_integration():
    """Test integration between dose calculator and motor controller"""
    
    # Create integrated components
    calc = DoseCalculator()
    motor = MotorController()
    
    # Connect calculator to motor
    calc.set_output_handler(motor.set_dose_command)
    
    # Calculate dose
    calc.calculate_bolus(carbs=30, blood_glucose=120, profile=test_profile)
    
    # Verify motor received correct command
    assert motor.get_last_command() == DoseCommand(units=3.5, rate=2.0)
    
    # Verify motor acknowledged
    assert motor.get_status() == MotorStatus.READY
```

### 3. System Testing

**Purpose**: Verify complete system meets software requirements

**Scope**:
- All software requirements
- End-to-end functionality
- System-level performance
- Error handling

**When**: After integration, before validation

**Coverage**: Test every software requirement

**Test Case Template:**
```markdown
Test Case ID: TC-042
Requirement: SRS-042 - System shall limit bolus to 25 units
Test Objective: Verify maximum bolus limit enforced

Preconditions:
- System powered on
- User logged in
- Patient profile loaded

Test Steps:
1. Navigate to bolus entry screen
2. Enter carbs: 500g
3. Enter blood glucose: 400 mg/dL  
4. Press Calculate
5. Verify calculated dose
6. Press Deliver

Expected Results:
- Step 5: Calculated dose shall be 25 units (at limit)
- Step 5: Warning displayed: "Dose at maximum limit"
- Step 6: Confirmation required
- Delivery: Exactly 25 units delivered

Pass/Fail Criteria:
- Dose must not exceed 25 units
- Warning must be displayed
- Confirmation must be required

Test Data:
- Patient profile: Carb ratio=1, Correction factor=1
- Extreme inputs to exceed limit

Actual Results: [Filled during execution]
Pass/Fail: [Checked during execution]
Tester: [Name, Date, Signature]
```

**Regression Testing:**
```markdown
# Regression Test Suite

Executed: After every software change

Scope: Critical/high-priority test cases

Automated: Where feasible

Frequency:
- Every build (automated smoke tests)
- Every release candidate (full regression)

Test Cases:
- All critical functionality (safety)
- All defect re-test cases
- Integration points
- Performance benchmarks
```

### 4. System Integration Testing

**Purpose**: Verify software integrated with complete device

**Scope**:
- Software + Hardware integration
- Complete device functionality
- Environmental conditions
- Real-world scenarios

**Example Tests:**
```markdown
SIT-001: Complete treatment delivery
- Power on device
- Authenticate user
- Load patient profile
- Enter treatment parameters
- Initiate delivery
- Verify actual insulin delivery (measure output)
- Verify data logged correctly

SIT-002: Alarm functionality
- Simulate occlusion (block tubing)
- Verify pressure sensor detects occlusion
- Verify software processes sensor data
- Verify alarm generated
- Verify alarm displayed
- Verify delivery stopped
- Verify alarm logged
```

### 5. Performance Testing

**Purpose**: Verify performance requirements met

**Test Types:**

**Response Time:**
```python
def test_dose_calculation_performance():
    """Verify dose calculation completes within 100ms"""
    import time
    
    start = time.time()
    result = calculate_bolus(carbs=50, blood_glucose=150, profile=test_profile)
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    assert elapsed < 100, f"Calculation took {elapsed}ms, exceeds 100ms requirement"
```

**Load Testing:**
```python
def test_concurrent_users():
    """Verify system handles 50 concurrent users"""
    import concurrent.futures
    
    def simulate_user():
        # Simulate user operations
        login()
        access_patient_data()
        enter_treatment()
        logout()
    
    # Simulate 50 concurrent users
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(simulate_user) for _ in range(50)]
        results = [f.result() for f in futures]
    
    # Verify all succeeded
    assert all(results), "Some users failed under concurrent load"
```

**Stress Testing:**
```markdown
ST-001: Extended operation test
- Run device continuously for 7 days
- Monitor for:
  - Memory leaks
  - Performance degradation
  - Resource exhaustion
  - Unexpected restarts
- Acceptance: No failures, stable performance
```

### 6. Security Testing

**Purpose**: Verify security requirements and identify vulnerabilities

**Test Types:**

**Authentication Testing:**
```markdown
SEC-T-001: Password complexity
- Attempt password: "12345" → Rejected
- Attempt password: "abcdefgh" → Rejected (no numbers)
- Attempt password: "Abcd1234" → Accepted

SEC-T-002: Account lockout
- Enter wrong password 5 times
- Verify account locked
- Verify unlock requires admin

SEC-T-003: Session timeout
- Login
- Wait 15 minutes inactive
- Attempt action
- Verify session expired, re-authentication required
```

**Penetration Testing:**
```markdown
# Penetration Test Scope

Network Security:
- Port scanning
- Protocol fuzzing
- Man-in-the-middle attempts
- Network injection

Application Security:
- Authentication bypass attempts
- Authorization bypass attempts
- Input injection (if applicable)
- Buffer overflow attempts

Physical Security:
- USB port access attempts
- Debug port access attempts
- Physical tampering detection
```

**Vulnerability Scanning:**
```bash
# Automated vulnerability scanning
nmap -sV -sC device_ip_address
nikto -h http://device_ip_address
owasp-zap --scan http://device_ip_address

# Static analysis security
flawfinder src/
bandit -r src/
```

### 7. Usability Testing

**Purpose**: Verify software is usable by intended users

**Test Scenarios:**
```markdown
# Usability Test Protocol

Participants: 10 registered nurses (intended users)

Tasks:
1. Set up new patient
   - Time to complete
   - Errors made
   - Success rate

2. Program basal insulin
   - Time to complete
   - Errors made
   - Success rate

3. Deliver bolus dose
   - Time to complete
   - Errors made  
   - Success rate

4. Respond to alarm
   - Time to recognize alarm
   - Correct response rate

Measurements:
- Task completion time
- Task success rate
- Error rate
- User satisfaction (survey)

Acceptance Criteria:
- ≥90% task completion rate
- ≥80% user satisfaction
- No critical use errors
```

### 8. Compatibility Testing

**Purpose**: Verify software works in all intended environments

**Test Matrix:**
```markdown
# Compatibility Test Matrix

Operating Systems:
- [ ] Windows 10
- [ ] Windows 11
- [ ] macOS 12
- [ ] macOS 13

Browsers (if web-based):
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

Hardware Configurations:
- [ ] Minimum spec
- [ ] Recommended spec
- [ ] High-end spec

Network Conditions:
- [ ] Ethernet
- [ ] Wi-Fi
- [ ] Cellular (if applicable)
- [ ] Low bandwidth
- [ ] High latency
```

## Test Documentation

### Test Plan

**Template:**
```markdown
# Test Plan - TP-001

## 1. Introduction
### 1.1 Scope
[What is being tested]

### 1.2 Objectives
[Goals of testing]

## 2. Test Items
- Software version: v1.0.0
- Hardware version: Rev B
- Configuration: Standard

## 3. Features to Test
- User authentication
- Dose calculation
- Alarm management
- Data logging

## 4. Features NOT to Test
- [Out of scope items]

## 5. Test Approach
### 5.1 Unit Testing
- Method: Automated using pytest
- Coverage goal: 100% branch coverage
- Tools: pytest, coverage.py

### 5.2 System Testing
- Method: Manual execution of test cases
- Coverage: 100% of requirements
- Tools: Test management system

## 6. Pass/Fail Criteria
- All critical test cases pass
- ≥95% non-critical test cases pass
- No unresolved critical defects

## 7. Test Environment
- Hardware: [Specifications]
- Operating system: [Version]
- Tools: [List]

## 8. Schedule
- Unit testing: Weeks 20-24
- Integration: Weeks 25-28
- System testing: Weeks 29-34

## 9. Responsibilities
- Test Lead: J. Smith
- Testers: A. Brown, C. Davis

## 10. Risks and Mitigation
[Testing risks and how to handle]
```

### Test Report

**Template:**
```markdown
# Test Report - TR-001

## Executive Summary
[Overview of testing and results]

## Test Summary
| Test Level | Planned | Executed | Passed | Failed | Pass Rate |
|------------|---------|----------|--------|--------|-----------|
| Unit       | 500     | 500      | 500    | 0      | 100%      |
| Integration| 150     | 150      | 148    | 2      | 99%       |
| System     | 200     | 200      | 197    | 3      | 99%       |
| Total      | 850     | 850      | 845    | 5      | 99%       |

## Defects Summary
| Severity | Open | Resolved | Total |
|----------|------|----------|-------|
| Critical | 0    | 2        | 2     |
| High     | 1    | 2        | 3     |
| Medium   | 2    | 8        | 10    |
| Low      | 5    | 20       | 25    |

## Requirements Coverage
- Requirements tested: 200/200 (100%)
- Requirements passed: 197/200 (98.5%)
- Requirements failed: 3/200 (1.5%)

## Open Issues
[List critical/high priority open defects]

## Conclusion
Testing demonstrates software meets requirements with identified exceptions. All critical defects resolved. Recommend proceed to validation.

## Approvals
[Signatures]
```

## Traceability

### Requirements to Tests

```
SRS-042: Limit bolus to 25 units
    ↓
Test Cases:
- TC-042-01: Verify limit with normal inputs
- TC-042-02: Verify limit with extreme inputs
- TC-042-03: Verify warning displayed
- TC-042-04: Verify confirmation required
```

### Traceability Matrix

| Requirement ID | Requirement | Test Cases | Status |
|----------------|-------------|------------|--------|
| SRS-001 | User authentication | TC-001, TC-002, TC-003 | PASS |
| SRS-042 | Dose limit | TC-042-01, TC-042-02, TC-042-03, TC-042-04 | PASS |

## Defect Management

### Defect Report Template

```markdown
Defect ID: DEF-123
Severity: High
Priority: P1
Status: Open

Title: Dose calculation incorrect for negative correction

Description:
When blood glucose is below target, correction dose calculation returns negative value instead of zero.

Steps to Reproduce:
1. Set patient profile: target BG = 120
2. Enter blood glucose: 80
3. Enter carbs: 0
4. Calculate bolus
5. Observe negative dose

Expected: Dose = 0
Actual: Dose = -0.8

Impact: Could result in no insulin delivery when needed

Found in: System testing
Test Case: TC-098
Software Version: v1.0.0-RC1
Found by: A. Brown
Date: 2024-06-15

Assigned to: J. Smith
Target Resolution: 2024-06-20
```

### Severity Levels

```
Critical: Patient safety impact, no workaround
High: Significant impact, workaround exists  
Medium: Moderate impact
Low: Minor issue, cosmetic
```

---

**Key Takeaway**: Medical device software testing must be comprehensive, risk-based, documented, and traceable. All requirements must be tested. Class C software requires extensive unit testing with code coverage. Regression testing essential. Document all tests and results. Trace requirements to tests.
