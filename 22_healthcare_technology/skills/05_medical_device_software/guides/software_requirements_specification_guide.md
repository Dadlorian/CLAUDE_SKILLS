# Software Requirements Specification Guide

## Purpose of SRS

The Software Requirements Specification (SRS) is the foundation of compliant software development. It:
- Defines what the software must do
- Forms basis for design
- Provides test basis
- Enables traceability
- Supports regulatory submissions

## SRS Structure

### Template

```markdown
# Software Requirements Specification

## 1. Introduction

### 1.1 Purpose
This document specifies software requirements for [Device Name] version [X.X].

### 1.2 Scope
This SRS covers software components: [list components]

### 1.3 Intended Use
[Intended use statement from system requirements]

### 1.4 Software Safety Classification
Safety Class: [A/B/C per IEC 62304]
Justification: [Reference to hazard analysis]

## 2. References
- System Requirements Specification: SyRS-001 v2.0
- Risk Management File: RMF-001
- IEC 62304:2006+A1:2015
- [Other applicable standards]

## 3. Definitions and Abbreviations
| Term | Definition |
|------|------------|
| SOUP | Software of Unknown Provenance |
| PHI  | Protected Health Information |

## 4. Functional Requirements

### 4.1 User Management
SRS-001: System shall support multiple user accounts
  Priority: High
  Trace to: SyRS-015
  Verification: TC-001, TC-002

SRS-002: System shall require authentication before access
  Priority: Critical
  Trace to: SyRS-016, RISK-003
  Verification: TC-003

### 4.2 [Feature Category]
[Requirements...]

## 5. Performance Requirements

SRS-100: System shall complete dose calculation within 100ms
  Priority: High
  Trace to: SyRS-042
  Verification: TC-050

SRS-101: System shall support up to 50 concurrent users
  Priority: Medium
  Trace to: SyRS-043
  Verification: TC-051

## 6. Interface Requirements

### 6.1 User Interface
SRS-200: System shall provide touchscreen interface
  Priority: High
  Trace to: SyRS-060
  Verification: TC-100

### 6.2 Hardware Interfaces
SRS-210: System shall communicate with pump motor via SPI
  Priority: Critical
  Trace to: SyRS-065
  Verification: TC-110

### 6.3 Software Interfaces
SRS-220: System shall interface with hospital EMR via HL7
  Priority: High
  Trace to: SyRS-070
  Verification: TC-120

### 6.4 Network Interfaces
SRS-230: System shall support Ethernet and Wi-Fi connectivity
  Priority: Medium
  Trace to: SyRS-075
  Verification: TC-130

## 7. Data Requirements

SRS-300: System shall store patient data in encrypted database
  Priority: Critical
  Trace to: SyRS-080, RISK-010
  Verification: TC-150

SRS-301: System shall maintain audit log of all user actions
  Priority: Critical
  Trace to: SyRS-081, RISK-011
  Verification: TC-151

## 8. Security Requirements

SRS-400: System shall implement role-based access control
  Priority: Critical
  Trace to: SyRS-090, RISK-015
  Verification: TC-200

SRS-401: System shall encrypt data at rest using AES-256
  Priority: Critical
  Trace to: SyRS-091, RISK-016
  Verification: TC-201

SRS-402: System shall encrypt network traffic using TLS 1.3
  Priority: Critical
  Trace to: SyRS-092, RISK-017
  Verification: TC-202

## 9. Safety Requirements

SRS-500: System shall limit maximum bolus dose to 25 units
  Priority: Critical
  Trace to: SyRS-100, RISK-020
  Verification: TC-250

SRS-501: System shall alarm if occlusion detected
  Priority: Critical
  Trace to: SyRS-101, RISK-021
  Verification: TC-251

## 10. Usability Requirements

SRS-600: System shall complete patient selection in ≤3 clicks
  Priority: Medium
  Trace to: SyRS-110
  Verification: TC-300, Usability-Test-01

SRS-601: System shall provide visual and auditory alarm feedback
  Priority: High
  Trace to: SyRS-111
  Verification: TC-301

## 11. Regulatory Requirements

SRS-700: System shall comply with 21 CFR Part 11 for electronic records
  Priority: Critical
  Trace to: REG-001
  Verification: Design Review, TC-400

SRS-701: System shall comply with HIPAA for PHI protection
  Priority: Critical
  Trace to: REG-002
  Verification: Design Review, TC-401

## 12. Environmental Requirements

SRS-800: System shall operate in temperature range 10-40°C
  Priority: High
  Trace to: SyRS-120
  Verification: TC-500

## 13. Requirements Traceability
[See Traceability Matrix RTM-001]

## 14. Assumptions and Dependencies

### Assumptions
- Users will be trained healthcare professionals
- Device will be used in controlled clinical environment

### Dependencies
- SOUP: FreeRTOS v10.5
- SOUP: OpenSSL v3.0.1
- Hardware: ARM Cortex-M7 processor

## Appendix A: Requirement Attributes

Each requirement includes:
- **ID**: Unique identifier (SRS-XXX)
- **Description**: Clear statement of requirement
- **Priority**: Critical, High, Medium, Low
- **Trace to**: Source requirements (system, user needs, risks)
- **Verification**: How will be verified (test cases)
```

## Writing Good Requirements

### SMART Criteria

Requirements should be:
- **Specific**: Clearly defined, no ambiguity
- **Measurable**: Can be tested/verified
- **Achievable**: Technically feasible
- **Relevant**: Necessary for device function
- **Testable**: Can verify compliance

### Good vs. Bad Requirements

**Bad:**
```
SRS-001: System shall be user-friendly
(Not measurable, subjective)

SRS-002: System shall be fast
(Not specific, what is "fast"?)

SRS-003: System shall work correctly
(Not testable, vague)
```

**Good:**
```
SRS-001: System shall complete user login within 2 seconds
(Specific, measurable, testable)

SRS-002: System shall display error message within 500ms of invalid input
(Specific, measurable, testable)

SRS-003: System shall calculate insulin dose with ±5% accuracy
(Specific, measurable, testable with defined tolerance)
```

### Requirement Types

**Functional:**
"The system shall [action] when [condition]"
- SRS-010: System shall calculate bolus dose when user enters carb intake

**Performance:**
"The system shall [action] within [time/throughput]"
- SRS-020: System shall process 100 transactions per second

**Interface:**
"The system shall [communicate/interact] with [entity] using [protocol/method]"
- SRS-030: System shall communicate with EMR using HL7 v2.5

**Safety:**
"The system shall [safety action] to prevent/mitigate [hazard]"
- SRS-040: System shall limit dose to prevent overdose

## Requirements Review

### Review Checklist

For each requirement:
- [ ] Uniquely identified
- [ ] Clear and unambiguous
- [ ] Testable
- [ ] Necessary (not gold-plating)
- [ ] Achievable
- [ ] Traced to source (user need, system req, risk)
- [ ] Trace to verification method defined
- [ ] Priority assigned
- [ ] No conflicts with other requirements

For overall SRS:
- [ ] All system requirements addressed
- [ ] All risk controls included
- [ ] All regulatory requirements included
- [ ] Complete (nothing missing)
- [ ] Consistent (no contradictions)
- [ ] Reviewed and approved

### Review Meeting

**Participants:**
- Software developers
- Systems engineers
- Risk management lead
- Quality assurance
- Clinical/domain experts
- Regulatory affairs

**Agenda:**
1. Review each requirement
2. Identify issues, ambiguities, gaps
3. Verify traceability
4. Verify testability
5. Document action items
6. Obtain approvals

## Traceability

### Forward Traceability

```
User Need UN-005: Device must deliver accurate insulin
    ↓
System Requirement SyRS-020: Deliver insulin ±5% accuracy
    ↓
Software Requirement SRS-042: Calculate dose with ±5% accuracy
    ↓
Design Module: DoseCalculator.calculateBolus()
    ↓
Test Cases: TC-100, TC-101, TC-102
```

### Backward Traceability

```
Test Case TC-100: Verify dose calculation accuracy
    ↓
Software Requirement SRS-042: Calculate dose with ±5% accuracy
    ↓
System Requirement SyRS-020: Deliver insulin ±5% accuracy
    ↓
User Need UN-005: Device must deliver accurate insulin
```

### Risk Control Traceability

```
Hazard H-010: Overdose due to calculation error
    ↓
Risk Control RC-010: Software dose limits
    ↓
Software Requirement SRS-500: Limit bolus to 25 units
    ↓
Design: DoseCalculator.MAX_BOLUS_LIMIT = 25
    ↓
Test Case TC-250: Verify limit enforced
    ↓
Test Result: PASS
```

## Change Management

### Handling Requirement Changes

**Change Request:**
1. Submit change request (CR-XXX)
2. Impact analysis:
   - Affected design elements
   - Affected tests
   - Risk analysis updates
   - Regulatory impact
3. Approval
4. Update SRS (new version)
5. Update design
6. Update tests
7. Re-verify
8. Update traceability

**Version Control:**
- SRS versioned (e.g., v1.0, v1.1, v2.0)
- Change history documented
- Previous versions archived
- All versions traceable to designs and tests

## Tools

### Requirements Management Tools

**Recommended:**
- Jama Connect
- IBM DOORS
- Helix RM
- Polarion Requirements

**Features Needed:**
- Unique requirement IDs
- Traceability linking
- Change tracking
- Review workflows
- Reports (traceability matrix)
- Integration with test tools

### Traceability Matrix Export

```csv
Req ID,Requirement,Source,Design,Test Case,Status
SRS-001,User authentication,SyRS-015,Auth.login(),TC-001,Verified
SRS-002,Password complexity,RISK-003,Auth.validatePwd(),TC-002,Verified
```

## FDA Submission

### SRS in 510(k)

Include:
- Complete SRS
- Traceability to system requirements
- Traceability to risk controls
- Traceability to test cases (summary)

**Level of detail by Level of Concern:**
- **Major**: Detailed SRS, all requirements, complete traceability
- **Moderate**: Detailed SRS, complete requirements
- **Minor**: High-level SRS, major requirements

### Common FDA Questions

1. "How do you ensure all requirements are tested?"
   - Provide traceability matrix showing req → tests

2. "How are risk controls incorporated?"
   - Show requirements derived from risk analysis

3. "How do you handle requirement changes?"
   - Describe change control process, show change log

---

**Key Takeaway**: SRS is foundation of compliant development. Requirements must be clear, testable, complete, and traceable. Link to user needs, system requirements, risk controls, design, and tests. Maintain rigorously throughout lifecycle.
