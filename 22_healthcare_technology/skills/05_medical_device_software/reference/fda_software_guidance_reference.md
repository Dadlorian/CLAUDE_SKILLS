# FDA Software Guidance Reference

## Overview

This reference consolidates FDA's key guidance documents for medical device software, Software as a Medical Device (SaMD), and related regulatory requirements.

## General Principles of Software Validation (2002)

### Scope
Final Guidance issued January 2002 establishing FDA's expectations for software validation.

### Key Principles

1. **Software Engineering Practices**
   - Requirements specification
   - Design specifications
   - Code implementation
   - Testing and validation
   - Maintenance procedures

2. **Risk-Based Approach**
   - Level of concern determines validation depth
   - Higher risk = more rigorous validation

3. **Validation Throughout Lifecycle**
   - Not just testing at the end
   - Continuous verification and validation

4. **Documentation Requirements**
   - Software Development Plan
   - Requirements specifications
   - Design specifications
   - Traceability analysis
   - Test plans and results

### Level of Concern

**Major Level of Concern:**
- Software functions presenting potential for SERIOUS INJURY or DEATH
- Examples: Infusion pumps, radiation therapy, surgical robots

**Moderate Level of Concern:**
- Software functions presenting potential for MINOR INJURY
- Examples: Diagnostic imaging, patient monitors

**Minor Level of Concern:**
- Software functions unlikely to result in injury
- Examples: Administrative hospital information systems

### Documentation by Level of Concern

**Major:**
- Software Requirements Specification (detailed)
- Software Design Specification (detailed)
- Traceability Analysis (comprehensive)
- Software Development Life Cycle Plan
- Verification and Validation Plan (extensive)
- Unit/Integration/System Test Plans and Results
- Regression Test Plan and Results
- Revision Level History

**Moderate:**
- Software Requirements Specification
- Software Design Specification
- Traceability Analysis
- Configuration Management Plan
- Verification and Validation Plan
- System Test Plan and Results
- Revision Level History

**Minor:**
- Software Requirements Specification (high-level)
- Hazard Analysis
- Validation Testing Plan and Results
- Revision Level History

### Off-the-Shelf (OTS) Software

**Concerns:**
- Unknown development process
- Limited access to source code
- Reliance on vendor
- Version changes

**Requirements:**
- Hazard analysis
- Intended use documentation
- Validation testing appropriate to level of concern
- Version control
- Configuration management

## Content of Premarket Submissions for Software (2005)

### Software Documentation in 510(k)

**Required Documentation:**

1. **Level of Concern**
   - Justification for level assignment
   - Risk analysis supporting determination

2. **Software Description**
   - Device name and intended use
   - Software model and release version
   - Configuration including hardware/software environment
   - Software development methodology
   - Development tools and compilers

3. **Device Hazard Analysis**
   - Software requirements related to safety
   - Hazard analysis methodology
   - Hazardous situations identified
   - Risk control measures

4. **Software Requirements Specification (SRS)**
   - Functional requirements
   - Performance requirements
   - Interface requirements
   - User requirements
   - Data definitions
   - Security requirements

5. **Software Design Documentation**
   - Architecture (high-level design)
   - Detailed design (for Major concern)
   - Interfaces (internal and external)

6. **Traceability Analysis**
   - Requirements to tests
   - Requirements to design (for Major concern)
   - Hazards to requirements to tests

7. **Software Development and Maintenance Plan**
   - Development methodology
   - Configuration management
   - Problem resolution
   - Maintenance procedures

8. **Verification and Validation Documentation**
   - V&V plan
   - Test protocols
   - Test results (summary)
   - Pass/fail criteria
   - Traceability

9. **Revision Level History**
   - Version number
   - Date released
   - Changes made
   - Problems resolved

10. **Unresolved Anomalies**
    - Description of known bugs
    - Assessment of impact
    - Plan for resolution

### Software Documentation in PMA

Similar to 510(k) but more extensive:
- Complete test results (not just summary)
- More detailed design documentation
- Clinical data integration
- Complete risk management file
- Software maintenance procedures

## Software as a Medical Device (SaMD) Guidance (2017)

### Definition
Software intended for medical purposes that operates on general-purpose computing platforms without being part of a hardware medical device.

### International Medical Device Regulators Forum (IMDRF) Framework

**SaMD Categories Based on:**
1. **Significance of information to healthcare decision**
   - Treat or diagnose
   - Drive clinical management
   - Inform clinical management

2. **Healthcare situation or condition**
   - Critical
   - Serious
   - Non-serious

### SaMD Risk Categorization

```
                    Critical    Serious    Non-Serious
Treat/Diagnose      IV          III        II
Drive Management    III         II         I
Inform Management   II          I          I

I = Lowest risk
IV = Highest risk
```

### Clinical Evaluation

**Risk-based approach to clinical evidence:**

**Category I (Lowest Risk):**
- Valid clinical association established
- Analytical/clinical validation

**Category II-III:**
- Valid clinical association
- Analytical validation
- Clinical validation

**Category IV (Highest Risk):**
- Valid clinical association
- Analytical validation
- Clinical validation
- Evidence from clinical investigation

### Quality Management System

**SaMD Specific Considerations:**
- Agile/iterative development accommodation
- Risk management throughout product lifecycle
- Software maintenance and updates
- Change management
- Post-market surveillance specific to software

## Cybersecurity Guidance

### Premarket Cybersecurity (2014, updated 2018)

**Required in Submissions:**

1. **Cybersecurity Risk Assessment**
   - Threat model
   - Asset identification
   - Attack surface analysis
   - Impact analysis
   - Vulnerability assessment

2. **Cybersecurity Architecture**
   - Security features and functions
   - Secure boot
   - Authentication and authorization
   - Encryption (in transit and at rest)
   - Audit logging
   - Secure interfaces

3. **Security Testing**
   - Vulnerability testing
   - Penetration testing
   - Fuzz testing
   - Static and dynamic code analysis

4. **Software Bill of Materials (SBOM)**
   - Commercial, open-source, and off-the-shelf software components
   - Version information
   - Known vulnerabilities

5. **Secure Update Mechanism**
   - Authenticated updates
   - Rollback capability
   - Integrity verification
   - User notification

### Postmarket Cybersecurity (2016)

**Routine Updates and Patches:**
- Proactive vulnerability assessment
- Coordinated disclosure
- Timely patching
- Communication to users

**Cybersecurity Incident Response:**
- Detection and monitoring
- Analysis and investigation
- Containment and remediation
- Communication to FDA and customers

**Vulnerability Monitoring:**
- NIST National Vulnerability Database
- ICS-CERT advisories
- Vendor security bulletins
- Component tracking

## Design Control Guidance (1997)

### Software-Specific Design Control Considerations

**Design and Development Planning:**
- Software development methodology
- Standards to be followed (e.g., IEC 62304)
- Development tools
- Testing strategies

**Design Input:**
- Functional requirements
- Performance requirements
- Safety requirements
- Regulatory requirements
- Usability requirements

**Design Output:**
- Source code
- Executable code
- User documentation
- Technical documentation

**Design Review:**
- Requirements review
- Architecture review
- Code review
- Test review

**Design Verification:**
- Unit testing
- Integration testing
- System testing
- Traceability verification

**Design Validation:**
- User acceptance testing
- Clinical validation (if applicable)
- Simulated use testing
- Field testing

**Design Transfer:**
- Build procedures
- Installation procedures
- Configuration management
- Release procedures

**Design Changes:**
- Impact analysis
- Regression testing
- Version control
- Change approval

## Artificial Intelligence/Machine Learning (AI/ML) Guidance

### AI/ML-Based SaMD Action Plan (2021)

**Key Concepts:**

1. **Good Machine Learning Practice (GMLP)**
   - Clinical study participants and data sets representative
   - Training data collected using good software engineering practices
   - Reference datasets independent and representative
   - Selected reference datasets robust and relevant
   - Model design appropriate for intended use
   - Focus on human factors and usability
   - Deployed models monitored for performance
   - Deployed models updated when necessary
   - Risk management for algorithmic bias

2. **Predetermined Change Control Plans**
   - Pre-specified acceptable modifications (SaMD Pre-Specifications)
   - Algorithm Change Protocol (ACP)
   - Documentation of performance boundaries

3. **Real-World Performance Monitoring**
   - Performance metrics
   - Data monitoring
   - User feedback
   - Post-market surveillance

**Total Product Lifecycle (TPLC) Regulatory Approach:**
- Initial premarket review
- Modifications through predetermined change control
- Real-world performance monitoring

## Mobile Medical Applications Guidance (2015)

### Mobile Medical App Definition
Software application that runs on mobile platform (smartphone, tablet) and:
- Meets definition of medical device AND
- Intended use is for medical purposes

### FDA Enforcement Discretion

**Not Enforce (low risk):**
- Apps that help patients self-manage without providing specific treatment suggestions
- General wellness apps
- Electronic health record access
- Apps that automate simple tasks for healthcare providers

**Enforce (higher risk):**
- Apps that transform mobile platform into regulated medical device
- Apps that become accessories to regulated medical device
- Apps that display/analyze medical device data

### Regulatory Requirements
When enforcement applies, same requirements as other medical devices:
- Quality System Regulation (21 CFR 820)
- Premarket review (510(k), De Novo, or PMA)
- Medical Device Reporting (21 CFR 803)
- Corrections and Removals (21 CFR 806)

## 21 CFR Part 11 - Electronic Records and Signatures

### Applicability to Medical Device Software

**Requirements for:**
- Electronic records used in regulatory submissions
- Electronic signatures on quality system documents
- Audit trails for electronic records
- Electronic records that replace paper records

### Controls for Closed Systems

1. **Validation**
   - Accuracy, reliability, consistent intended performance
   - Ability to discern invalid/altered records

2. **Audit Trail**
   - Secure, computer-generated, time-stamped audit trail
   - Record operator actions
   - Independent review of audit trail

3. **System Access**
   - Authority checks
   - Device checks
   - Operational system checks

4. **Education and Training**
   - Training on Part 11 requirements
   - Documentation of training

5. **Documentation Controls**
   - Procedures to control documentation
   - Revisions maintained
   - Distribution controls

6. **Data Integrity**
   - Electronic signature manifestations
   - Handwritten signature executed to electronic signature
   - Signature/record linkage

### Electronic Signatures

**Requirements:**
- Unique to one individual
- Not reusable by others
- Under sole control of individual
- Linked to record so cannot be removed/transferred
- First-time use requires identity verification
- Signed electronic records must include:
  - Name
  - Date and time
  - Meaning of signature

## Clinical Decision Support (CDS) Software (2022)

### CDS Functions NOT Medical Devices

Under 21st Century Cures Act, certain CDS excluded from medical device definition:

**Criteria for Exclusion:**
1. Not for acquiring, processing, or analyzing medical image or signal
2. Displays/analyzes/prints medical information about a patient
3. Supports or provides recommendations about prevention, diagnosis, or treatment
4. Meets ALL of these:
   - Not intended for purpose of identifying serious/life-threatening conditions
   - Not intended to drive clinical management of those conditions
   - Enables HCP to independently review basis for recommendations
   - Includes descriptions of limitations, warnings, or other appropriate info

**Still Regulated:**
- CDS for acquisition/analysis of images or signals
- CDS for serious/critical situations
- CDS that doesn't allow independent review
- CDS lacking transparency about limitations

## Quality System Regulation (21 CFR Part 820)

### Software-Specific Requirements

**§820.30 Design Controls:**
- Software development planning
- Design input requirements
- Design output specifications
- Design review at appropriate stages
- Design verification (testing)
- Design validation (user validation)
- Design transfer to production
- Design change control

**§820.70 Production and Process Controls:**
- Software build procedures
- Software installation procedures
- Automated processes validated

**§820.75 Process Validation:**
- Software validation per intended use
- Validation before release
- Revalidation for changes

## Summary of Key Requirements

### For All Medical Device Software:
1. Follow software lifecycle standard (IEC 62304 recognized)
2. Risk-based approach to development rigor
3. Comprehensive documentation
4. Verification and validation
5. Configuration management
6. Change control

### For Premarket Submissions:
1. Level of Concern documentation
2. Software Requirements Specification
3. Hazard analysis
4. Traceability analysis
5. V&V documentation
6. Unresolved anomalies

### For Cybersecurity:
1. Threat modeling
2. Security architecture
3. SBOM
4. Security testing
5. Update mechanism
6. Vulnerability monitoring

### For Post-Market:
1. Complaint handling
2. Medical Device Reporting
3. Corrections and Removals
4. Continuous monitoring
5. Periodic updates
6. Patch management

## Common FDA 510(k) Deficiencies

1. **Insufficient Level of Concern Justification**
   - Provide detailed hazard analysis
   - Link software failures to patient harms

2. **Incomplete Software Requirements**
   - Missing safety requirements
   - Vague, untestable requirements
   - Insufficient interface specifications

3. **Inadequate Traceability**
   - Gaps in requirements-to-tests mapping
   - Missing hazard-to-control-to-test links

4. **Insufficient Testing Documentation**
   - Missing test protocols
   - Incomplete test results
   - Unclear pass/fail criteria

5. **Unresolved Anomalies Not Addressed**
   - Impact not assessed
   - No resolution plan

6. **Cybersecurity Gaps**
   - Incomplete threat model
   - Missing SBOM
   - Inadequate security testing

7. **OTS/SOUP Not Managed**
   - No validation testing
   - Version not controlled
   - Anomalies not evaluated

## Useful References

- **FDA Guidance Repository**: https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/guidance-documents-medical-devices-and-radiation-emitting-products
- **FDA Software Digital Health**: https://www.fda.gov/medical-devices/digital-health-center-excellence
- **FDA Cybersecurity**: https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity
- **Recognized Standards**: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfstandards/search.cfm

---

**Key Takeaway**: FDA expects rigorous software development processes proportional to risk. Compliance requires comprehensive documentation, thorough testing, cybersecurity controls, and post-market surveillance. IEC 62304 and ISO 14971 provide frameworks that satisfy FDA expectations.
