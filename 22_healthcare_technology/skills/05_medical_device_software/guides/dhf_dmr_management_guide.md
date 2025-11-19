# DHF/DMR Management Guide

## Design History File (DHF) Overview

The DHF contains complete design history of the medical device. It demonstrates that design controls were followed and the device was designed correctly.

## DHF Structure and Organization

### Recommended Folder Structure

```
DHF_DeviceName_v1.0/
├── 00_Index/
│   ├── DHF_Index.xlsx
│   └── Document_Cross_Reference.pdf
├── 01_Planning/
│   ├── Design_Plan.pdf
│   ├── Project_Schedule.pdf
│   └── Resource_Plan.pdf
├── 02_Design_Input/
│   ├── User_Needs.pdf
│   ├── System_Requirements_Specification.pdf
│   ├── Software_Requirements_Specification.pdf
│   ├── Requirements_Traceability_Matrix.xlsx
│   └── Input_Review_Records/
├── 03_Design_Output/
│   ├── System_Architecture.pdf
│   ├── Software_Architecture.pdf
│   ├── Detailed_Design_Specification.pdf
│   ├── Source_Code/ (reference to version control)
│   ├── Schematics/ (if hardware)
│   └── Output_Review_Records/
├── 04_Design_Reviews/
│   ├── Requirements_Review_Minutes.pdf
│   ├── Architecture_Review_Minutes.pdf
│   ├── Detailed_Design_Review_Minutes.pdf
│   ├── Critical_Design_Review_Minutes.pdf
│   └── Final_Design_Review_Minutes.pdf
├── 05_Verification/
│   ├── Verification_Plan.pdf
│   ├── Test_Protocols/
│   ├── Test_Results/
│   ├── Traceability_Matrix.xlsx
│   ├── Code_Review_Records/
│   ├── Static_Analysis_Reports/
│   └── Verification_Report.pdf
├── 06_Validation/
│   ├── Validation_Plan.pdf
│   ├── IQ_Protocol_and_Results.pdf
│   ├── OQ_Protocol_and_Results.pdf
│   ├── PQ_Protocol_and_Results.pdf
│   ├── Clinical_Study_Protocol.pdf (if applicable)
│   ├── Clinical_Study_Report.pdf (if applicable)
│   └── Validation_Report.pdf
├── 07_Risk_Management/
│   ├── Risk_Management_Plan.pdf
│   ├── Hazard_Analysis.xlsx
│   ├── Risk_Assessment.xlsx
│   ├── Risk_Control_Measures.pdf
│   ├── Risk_Control_Verification.pdf
│   ├── Residual_Risk_Evaluation.pdf
│   └── Risk_Management_Report.pdf
├── 08_Design_Transfer/
│   ├── Design_Transfer_Plan.pdf
│   ├── DMR/ (Device Master Record - see below)
│   ├── Production_Readiness_Review.pdf
│   └── Transfer_Verification_Report.pdf
├── 09_Design_Changes/
│   ├── Change_Control_Procedure.pdf
│   ├── Change_Requests/
│   │   ├── DCR-001_Description.pdf
│   │   ├── DCR-002_Description.pdf
│   └── Change_Summary_Log.xlsx
└── 10_Supporting_Documentation/
    ├── Standards_Applied.pdf
    ├── Supplier_Documentation/
    ├── SOUP_Evaluations/
    ├── Usability_Engineering_File/
    └── Biocompatibility/ (if applicable)
```

### DHF Index Template

**DHF_Index.xlsx:**
| Doc ID | Document Title | Version | Date | Location | Reviewer | Approver |
|--------|----------------|---------|------|----------|----------|----------|
| DHF-01-001 | Design and Development Plan | 2.0 | 2024-01-15 | 01_Planning/ | J.Smith | M.Jones |
| DHF-02-001 | Software Requirements Spec | 3.1 | 2024-03-20 | 02_Design_Input/ | A.Brown | M.Jones |

## Device Master Record (DMR) Overview

The DMR defines how to manufacture/build the device. It's the production specification.

### DMR Structure

```
DMR_DeviceName_v1.0/
├── 01_Device_Specifications/
│   ├── Device_Specification.pdf
│   ├── Software_Requirements_Specification.pdf
│   ├── Bill_of_Materials.xlsx
│   └── SOUP_List.xlsx
├── 02_Production_Procedures/
│   ├── Software_Build_Procedure.pdf
│   ├── Software_Installation_Procedure.pdf
│   ├── Hardware_Assembly_Procedure.pdf (if applicable)
│   ├── Calibration_Procedure.pdf
│   └── Configuration_Procedure.pdf
├── 03_Quality_Procedures/
│   ├── In_Process_Inspection_Procedure.pdf
│   ├── Final_Inspection_Procedure.pdf
│   ├── Software_Acceptance_Testing_Procedure.pdf
│   └── Acceptance_Criteria.pdf
├── 04_Packaging_and_Labeling/
│   ├── Packaging_Specification.pdf
│   ├── Label_Artwork.pdf
│   ├── Instructions_for_Use.pdf
│   └── Quick_Start_Guide.pdf
└── 05_Installation_and_Servicing/
    ├── Installation_Procedure.pdf
    ├── Service_Manual.pdf
    └── Troubleshooting_Guide.pdf
```

### Software Build Procedure Example

```markdown
# Software Build Procedure - SBP-001

## Purpose
Define procedure for building production software release

## Scope
Applies to all production software releases

## Build Environment

### Hardware
- CPU: Intel Core i7 or equivalent
- RAM: 16 GB minimum
- Disk: 500 GB SSD

### Software
- Operating System: Ubuntu 20.04 LTS
- Compiler: GCC ARM 10.3.1
- Build System: CMake 3.20.0
- Version Control: Git 2.30.0

## Procedure

### 1. Prepare Build Environment
1.1. Install Ubuntu 20.04 LTS
1.2. Install build tools: `sudo apt install build-essential cmake git`
1.3. Install ARM compiler: `sudo apt install gcc-arm-none-eabi`
1.4. Verify versions match specifications

### 2. Obtain Source Code
2.1. Clone repository: `git clone https://github.com/company/device-sw.git`
2.2. Checkout release tag: `git checkout v1.0.0`
2.3. Verify tag signature: `git tag -v v1.0.0`
2.4. Record commit hash in build record

### 3. Configure Build
3.1. Create build directory: `mkdir build && cd build`
3.2. Run CMake: `cmake -DCMAKE_BUILD_TYPE=Release ..`
3.3. Verify configuration output

### 4. Compile Software
4.1. Build: `make -j8`
4.2. Verify no errors
4.3. Verify no warnings

### 5. Run Automated Tests
5.1. Execute unit tests: `make test`
5.2. Verify all tests pass
5.3. Execute static analysis: `make static-analysis`
5.4. Verify no critical/high issues

### 6. Generate Release Artifacts
6.1. Create firmware binary: `make firmware`
6.2. Calculate checksum: `sha256sum firmware.bin`
6.3. Record checksum: firmware.bin.sha256

### 7. Sign Firmware
7.1. Sign with private key: `./sign_firmware.sh firmware.bin`
7.2. Verify signature: `./verify_signature.sh firmware.bin.sig`

### 8. Archive Build
8.1. Create archive: `./create_archive.sh v1.0.0`
8.2. Archive includes:
   - firmware.bin
   - firmware.bin.sha256
   - firmware.bin.sig
   - build_log.txt
   - test_results.txt
8.3. Store in: `/releases/v1.0.0/`

### 9. Document Build
9.1. Complete Build Record Form BRF-001
9.2. Include:
   - Software version
   - Build date/time
   - Builder name
   - Git commit hash
   - Build environment versions
   - Test results
   - Checksums
9.3. Sign and date build record
9.4. Archive with release

## Acceptance Criteria
- [ ] All unit tests pass
- [ ] Static analysis shows no critical issues
- [ ] Checksum matches expected value
- [ ] Signature verification successful
- [ ] Build record complete and signed

## References
- Software Requirements Specification: SRS-001
- Software Design Specification: SDS-001
- Quality System Procedure: QSP-010
```

## DHF/DMR Management Best Practices

### Version Control

**Document Version Scheme:**
```
Major.Minor format (e.g., 2.1)
- Major: Significant changes requiring review
- Minor: Editorial or minor corrections

Each version includes:
- Version number
- Date
- Author
- Change description
- Reviewer
- Approver
```

**Document Header Template:**
```
Title: [Document Name]
Document Number: [DHF-XX-XXX]
Version: [X.X]
Date: [DD-MMM-YYYY]
Author: [Name]
Reviewer: [Name]
Approver: [Name]

Revision History:
| Version | Date | Author | Changes | Approver |
|---------|------|--------|---------|----------|
| 1.0 | 01-JAN-2024 | J.Smith | Initial release | M.Jones |
| 1.1 | 15-FEB-2024 | J.Smith | Added section 3.2 | M.Jones |
```

### Cross-Referencing

**Maintain Traceability:**
```markdown
# Software Requirements Specification

## Requirement SRS-042
Software shall limit maximum bolus dose to 25 units

Trace from: UN-015 (User Need)
Trace from: RISK-007 (Risk Control)
Trace to: Design-3.2.1 (Architecture)
Trace to: TC-123, TC-124 (Test Cases)

References:
- DHF-02-001: System Requirements v2.0
- DHF-07-002: Risk Assessment v1.3
- DHF-05-015: Test Protocol v1.0
```

### Approval Process

**Multi-Level Approval:**
```
1. Author: Creates/modifies document
2. Peer Review: Technical review by peer
3. Quality Review: QA reviews for compliance
4. Approver: Authorized person approves

Each approval includes:
- Name
- Title
- Signature (or electronic signature)
- Date
```

### Electronic DHF

**Using Electronic Systems:**
- Document management system (e.g., MasterControl, Greenlight Guru)
- Version control for all documents
- Electronic signatures (21 CFR Part 11 compliant)
- Audit trails
- Access controls
- Backup procedures

**21 CFR Part 11 Compliance:**
- System validation
- Audit trails (who, what, when)
- User access controls
- Electronic signature manifestations
- Document retention

### Maintaining DHF

**Throughout Development:**
- Add documents as created
- Don't wait until end of project
- Review DHF completeness at design reviews
- Update index regularly

**Before Release:**
- Complete DHF audit
- Verify all required documents present
- Verify all documents approved
- Verify traceability complete
- Create DHF archive for release

**After Release:**
- Maintain DHF for device lifetime + regulatory retention period
- Update DHF for design changes
- Keep DHF readily retrievable for FDA inspections

## DMR Creation and Maintenance

### Creating DMR from DHF

**Process:**
1. Extract production-relevant documents from DHF
2. Create manufacturing/build procedures
3. Define acceptance criteria
4. Document labeling specifications
5. Review and approve DMR
6. Baseline DMR for production

### DMR Change Control

**All DMR changes require:**
- Change request and approval
- Impact analysis
- Verification of change
- DMR version update
- Training on changes
- First article inspection after change

### DMR and DHR Relationship

**Device History Record (DHR):**
- Created for each manufactured unit/batch
- References DMR
- Documents that DMR was followed
- Includes:
  - Build record
  - Test results
  - Serial number
  - Acceptance signature

## FDA Inspection Readiness

### Common FDA Requests

**DHF Inspection:**
- "Show me the DHF for this device"
- "Walk me through design controls"
- "Show me requirements traceability"
- "Show me risk management documentation"
- "Show me design change controls"

**Be Prepared to Show:**
- Complete, organized DHF
- Traceability matrices
- Design review records
- Verification/validation results
- Change control records
- Management approvals

### Inspection Tips

1. **Know Your DHF:** Understand organization and contents
2. **Have Index Ready:** Quick access to any document
3. **Show Traceability:** Demonstrate requirements to tests
4. **Explain Process:** Describe how design controls followed
5. **Show Approvals:** All documents properly approved
6. **Demonstrate Change Control:** Show how changes managed

---

**Key Takeaway**: DHF demonstrates design done right; DMR defines how to build it right. Complete, organized, traceable documentation is essential. Maintain contemporaneously, not retrospectively. Electronic systems recommended but must be 21 CFR Part 11 compliant. Regular audits ensure readiness for FDA inspection.
