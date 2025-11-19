# Meaningful Use and ONC Certification Reference

## Overview

This reference covers the ONC (Office of the National Coordinator for Health Information Technology) certification criteria for EHR systems, including Meaningful Use, MIPS, Promoting Interoperability, and 21st Century Cures Act requirements.

## Evolution of EHR Certification Requirements

### Timeline
```
2009 - HITECH Act passed
2011 - Meaningful Use Stage 1
2014 - Meaningful Use Stage 2
2015 - Meaningful Use Stage 3 / MIPS begins
2018 - Promoting Interoperability (replaces Meaningful Use)
2020 - 21st Century Cures Act Information Blocking Rule
2022 - TEFCA (Trusted Exchange Framework)
```

## Meaningful Use Stages

### Stage 1 (2011-2012)
**Focus**: Data capture and sharing

**Core Objectives**:
1. Use CPOE for medication orders
2. Implement drug-drug, drug-allergy interaction checks
3. Maintain up-to-date problem list
4. Generate and transmit e-prescriptions
5. Maintain active medication list
6. Maintain active medication allergy list
7. Record demographics
8. Record vital signs
9. Record smoking status
10. Implement clinical decision support
11. Report clinical quality measures
12. Provide patients with electronic copy of health information
13. Provide clinical summaries for office visits
14. Exchange key clinical information electronically
15. Protect electronic health information

### Stage 2 (2014-2016)
**Focus**: Advance clinical processes

**Enhanced Requirements**:
- Increased CPOE threshold (60% of orders)
- More robust HIE (Health Information Exchange)
- Patient engagement (secure messaging, view/download/transmit)
- Expanded CDS rules
- Syndromic surveillance reporting
- Electronic lab reporting
- Patient-specific education resources

### Stage 3 (2017-2018)
**Focus**: Improved outcomes

**Key Requirements**:
- Coordinated care through patient engagement
- Health information exchange to improve patient safety
- Improved population and public health
- Clinical decision support for high-priority conditions
- e-prescribing for controlled substances

## ONC 2015 Edition Certification Criteria

### Clinical Functionality

#### 170.315(a)(1) - Computerized Provider Order Entry (CPOE)
```
Requirements:
├── Medications
│   ├── Enable user to electronically record orders
│   ├── Display drug-drug interaction checks
│   ├── Display drug-allergy interaction checks
│   └── Display drug formulary status
├── Laboratory
│   ├── Record lab orders electronically
│   └── Support standard LOINC codes
└── Diagnostic Imaging
    ├── Record imaging orders electronically
    └── Support standard CPT codes

Measurement:
• More than 60% of medication orders via CPOE
• More than 60% of lab orders via CPOE
• More than 60% of imaging orders via CPOE
```

#### 170.315(a)(2) - Drug-Drug, Drug-Allergy Interaction Checks
```
Requirements:
├── Drug-Drug Interactions
│   ├── Access drug-drug interaction database
│   ├── Display severity levels
│   ├── Enable provider to take action
│   └── Adjustable sensitivity levels
└── Drug-Allergy Interactions
    ├── Check against active allergy list
    ├── Include inactive ingredients
    ├── Display severity levels
    └── Require documented override

Data Sources:
• First DataBank
• Wolters Kluwer (Medi-Span)
• Gold Standard Drug Database
• Other ONC-approved sources
```

#### 170.315(a)(4) - Demographics
```
Required Fields:
├── Preferred language
├── Sex (at birth)
├── Gender identity
├── Sexual orientation
├── Race (minimum 5 categories per OMB)
├── Ethnicity (Hispanic/Latino or not)
├── Date of birth
└── Date and preliminary cause of death

Privacy Considerations:
• Allow patient to decline to specify
• Protect sensitive demographic data
• Enable data segmentation for privacy
```

#### 170.315(a)(5) - Problems
```
Requirements:
├── Record, change, access problem list
├── Associate problems with encounters
├── Code with SNOMED CT
├── Display problem status (active, resolved, etc.)
└── Support problem onset dates

Problem List Must Include:
• Current and active diagnoses
• Historical diagnoses (resolved)
• ICD-10-CM code mapping
• SNOMED CT as primary coding system
```

#### 170.315(a)(6) - Medications
```
Requirements:
├── Record and access medication list
├── Code with RxNorm
├── Include medication status
├── Support start/end dates
├── Link to prescribing provider
└── Include route, frequency, dose

Medication List Requirements:
• All current medications
• Prescription medications
• Over-the-counter medications
• Samples provided
• Herbal/supplemental products
```

#### 170.315(a)(7) - Medication Allergy List
```
Requirements:
├── Record, change, access allergy list
├── Code with RxNorm or SNOMED CT
├── Record reaction type
├── Record severity
├── Support "No Known Allergies"
└── Support "No Allergy List Available"

Required Reaction Tracking:
• Type of reaction (rash, anaphylaxis, etc.)
• Severity (mild, moderate, severe)
• Onset date
• Status (active, inactive, resolved)
```

#### 170.315(a)(9) - Clinical Decision Support (CDS)
```
Requirements:
├── Evidence-based CDS rules
├── CDS rule implementation
│   ├── At point of care
│   ├── Relevant to workflow
│   └── Based on patient-specific data
├── CDS intervention types
│   ├── Alerts
│   ├── Reminders
│   ├── Clinical guidelines
│   └── Order sets/pathways
├── CDS configuration
│   ├── Enable/disable rules
│   ├── Modify parameters
│   └── Track interventions
└── CDS analytics
    ├── Track trigger events
    ├── Track provider responses
    └── Measure impact

Required CDS Types:
• Drug-drug interactions (5+ severity levels)
• Drug-allergy checks
• Preventive care reminders
• Chronic disease management
• Appropriate use criteria
```

#### 170.315(a)(14) - Implantable Device List
```
Requirements:
├── Record UDI (Unique Device Identifier)
├── Associate with patient
├── Parse UDI into components
│   ├── Device Identifier (DI)
│   └── Production Identifier (PI)
└── Query FDA Global UDI Database

UDI Components:
• Device name
• Model number
• Serial number
• Lot number
• Expiration date
• Manufacturing date
```

### Care Coordination

#### 170.315(b)(1) - Transitions of Care
```
Requirements:
├── Create C-CDA (Consolidated CDA)
│   ├── C-CDA version 2.1 or later
│   ├── Include required sections
│   └── Validate against schema
├── Send via multiple methods
│   ├── Direct messaging (encrypted email)
│   ├── Applicability statement
│   └── Other HIE methods
├── Receive and incorporate
│   ├── Import C-CDA documents
│   ├── Reconcile medications
│   ├── Reconcile allergies
│   └── Reconcile problems
└── Track receipt and review

C-CDA Required Sections:
• Patient demographics
• Problem list
• Medication list
• Medication allergy list
• Immunizations
• Laboratory test results
• Vital signs
• Care plan (if applicable)
• Procedures
• Social history (smoking status)
• Care team members
```

#### 170.315(b)(2) - Clinical Information Reconciliation
```
Requirements:
├── Medication reconciliation
│   ├── Display incoming med list
│   ├── Display current med list
│   ├── Enable side-by-side comparison
│   ├── Accept, modify, or reject each medication
│   └── Document reconciliation completion
├── Allergy reconciliation
│   └── Same process as medications
└── Problem list reconciliation
    └── Same process as medications

Reconciliation Workflow:
1. Receive external summary
2. Display current patient list
3. Display incoming list
4. Enable line-by-line comparison
5. Provider selects action for each item
6. Update patient record
7. Document who/when reconciled
```

#### 170.315(b)(3) - Electronic Prescribing (eRx)
```
Requirements:
├── Create prescription electronically
├── Transmit via NCPDP SCRIPT
├── Include RxNorm codes
├── Receive formulary/benefits
├── Receive medication history
├── Receive fill status notifications
└── Support controlled substances (EPCS)

NCPDP SCRIPT Messages:
• NewRx - New prescription
• RxChangeRequest - Change request from pharmacy
• RxChangeResponse - Provider response
• CancelRx - Cancel prescription
• RxFill - Fill notification
• RxHistoryRequest/Response - Medication history
```

#### 170.315(b)(6) - Data Portability
```
Requirements:
├── Export entire EHR
├── Include all patient data
├── Machine-readable format
├── Include demographic data
├── Include clinical data
├── Include document references
└── Timely export (no delays)

Export Format Options:
• C-CDA documents
• FHIR resources
• Delimited text files (CSV)
• Transition records
```

### Patient Engagement

#### 170.315(e)(1) - View, Download, Transmit (VDT)
```
Requirements:
├── Patient access within 24 hours
├── View online
├── Download in human-readable format
├── Download in computable format
├── Transmit to third party
├── Activity log (audit trail)
└── Must include:
    ├── Lab results
    ├── Problem list
    ├── Medication list
    ├── Medication allergies
    ├── Procedures
    ├── Immunizations
    ├── Care team members
    ├── Vital signs
    ├── Smoking status
    ├── Clinical notes
    └── Care plan

Measurement:
• >5% of patients view, download, or transmit
• Tracked via patient portal analytics
```

#### 170.315(e)(3) - Patient Health Information Capture
```
Requirements:
├── Patient-entered data
│   ├── Through portal or app
│   ├── Incorporated into EHR
│   └── Visible to providers
└── Supported data types:
    ├── Health concerns
    ├── Goals
    ├── Preferences
    └── Self-measured vitals
```

### Health Information Exchange

#### 170.315(g)(10) - Standardized API for Patient Access
```
Requirements:
├── FHIR R4 API
├── OAuth 2.0 authentication
├── SMART on FHIR support
├── Single patient API
├── Include USCDI data classes
├── No special effort required
├── Documentation publicly available
└── Support bulk data export

USCDI Version 1 Data Classes:
• Patient Demographics
• Vital Signs
• Laboratory Results
• Medications
• Medication Allergies
• Immunizations
• Procedures
• Conditions/Problems
• Clinical Notes
• Provenance
• Assessment and Plan of Treatment
• Goals
• Health Concerns
```

## 21st Century Cures Act

### Information Blocking Rule (April 2021)

**Prohibited Practices**:
```
1. Practices likely to interfere with access, exchange, or use of EHI
2. Without reasonable justification
3. If actor knows or should know that practice is likely to interfere

Actors Covered:
├── Health IT developers
├── HIEs
├── HINs (Health Information Networks)
└── Healthcare providers (as of October 2022)
```

**Exceptions to Information Blocking**:
1. **Preventing Harm**: Patient safety concerns
2. **Privacy**: Protect privacy as required by law
3. **Security**: Protect against security risks
4. **Infeasibility**: Technically infeasible
5. **Health IT Performance**: Maintain/improve performance
6. **Content and Manner**: Reasonable content/manner restrictions
7. **Fees**: Reasonable, cost-based fees
8. **Licensing**: Reasonable licensing of intellectual property

### Patient Access to EHI

**Requirements**:
```
Patients must have access to:
├── All Electronic Health Information (EHI)
├── Without delay
├── Without special effort
├── At no or minimal cost
├── In computable format
└── Via API (FHIR R4)

Timeline:
• Immediately upon request (or ASAP)
• No fees except:
  - Labor for creating response
  - Copying (digital or paper)
  - Postage
```

### API Requirements

**FHIR API Mandatory Features**:
```
1. FHIR Release 4.0.1 (R4)
2. SMART App Launch Framework
3. OAuth 2.0 for authorization
4. OpenID Connect for authentication
5. US Core Implementation Guide
6. Bulk Data Access (FHIR Bulk Data Export)
7. Published, complete, accurate documentation
8. No additional authentication requirements
```

## MIPS (Merit-Based Incentive Payment System)

### Performance Categories

**1. Quality (45% of score)**:
```
Requirements:
├── Report on 6 quality measures
├── At least 1 outcome measure (if available)
├── Data completeness threshold: 70%
└── Baseline/benchmark comparison

Submission Methods:
• EHR direct submission
• Registry submission
• QCDR (Qualified Clinical Data Registry)
• Claims-based
```

**2. Promoting Interoperability (25% of score)**:
```
Required Measures:
├── e-Prescribing
│   └── >25% of prescriptions via CPOE
├── Health Information Exchange
│   ├── Support Electronic Referral Loops
│   ├── Provide Patient Access (>50%)
│   └── Query of PDMP (Prescription Drug Monitoring)
├── Provider to Patient Exchange
│   └── >25% of patients access health information
└── Public Health and Clinical Data Exchange
    ├── Immunization Registry Reporting
    └── Electronic Case Reporting

Exclusions:
• Hospital-based providers
• Providers in first year of practice
• Significant hardship
```

**3. Improvement Activities (15% of score)**:
```
Requirements:
├── Perform and attest to improvement activities
├── High-weighted activity = 20 points
├── Medium-weighted activity = 10 points
└── Required: 40 points

Example Activities:
• Use of QCDR for feedback
• Participation in APM
• Medication reconciliation
• Care coordination workflows
• Telemedicine utilization
• Patient safety initiatives
```

**4. Cost (15% of score)**:
```
Automatically calculated by CMS:
├── Total per capita costs
├── Medicare spending per beneficiary
└── Episode-based measures

No provider submission required
```

## Testing and Certification

### ONC-ACB (Authorized Certification Body)

**Certification Process**:
```
1. Pre-certification planning
   ├── Gap analysis
   ├── Feature development
   └── Testing preparation

2. Functional testing
   ├── Test each certified criterion
   ├── Document test results
   └── Remediate failures

3. Interface testing
   ├── C-CDA validation
   ├── FHIR API testing
   ├── Direct messaging
   └── Structured data capture

4. Security testing
   ├── Encryption
   ├── Authentication
   ├── Access controls
   └── Audit logging

5. Usability testing
   ├── Safety-enhanced design
   ├── User-centered design
   └── End-user feedback

6. Certification issuance
   └── CHPL (Certified Health IT Product List) listing
```

### Real World Testing

**Annual Requirements (since 2022)**:
```
Health IT developers must:
├── Create real world testing plan
│   ├── Criteria tested
│   ├── Testing methods
│   ├── Expected outcomes
│   └── Timeline
├── Submit plan to ONC-ACB
├── Conduct testing in production
├── Document results
└── Submit results annually

Testing Focus:
• Interoperability
• Standards conformance
• API performance
• User workflows
• Clinical accuracy
```

## Compliance Monitoring

### CMS Audits

**Audit Process**:
```
1. Selection notification
2. Document submission (30 days)
3. Review and analysis
4. Preliminary findings
5. Response period
6. Final determination
7. Payment adjustment (if applicable)
```

**Commonly Audited Areas**:
- CPOE usage rates
- e-Prescribing rates
- HIE participation
- Patient portal access rates
- Clinical quality measure accuracy
- Security risk analysis documentation

### Penalties for Non-Compliance

**MIPS Penalties**:
```
Performance Threshold: 75 points (2023)
├── Below threshold: Negative payment adjustment (up to -9%)
├── At threshold: Neutral (0% adjustment)
└── Above threshold: Positive payment adjustment (up to +9%)

Exceptional Performance: Additional bonus for top performers
```

**Information Blocking Penalties**:
```
Health IT Developers:
├── CMPs (Civil Monetary Penalties) up to $1 million per violation
├── Removal from ONC certification program
└── Disincentives under other programs

Healthcare Providers:
├── CMPs
├── Referral to CMS for disincentive or exclusion
└── Referral to appropriate agency for investigation
```

## Best Practices for Compliance

### 1. Maintain Documentation
```
Essential Documents:
├── Security risk analysis (annual)
├── HIPAA policies and procedures
├── Staff training records
├── Audit logs
├── System configuration documentation
├── Vendor contracts and BAAs
└── Incident response plans
```

### 2. Continuous Testing
```
Regular Testing Schedule:
├── Weekly: Interface monitoring
├── Monthly: Report validation
├── Quarterly: Security assessments
├── Annually: Full compliance review
└── Ad-hoc: New feature validation
```

### 3. User Training
```
Training Topics:
├── CPOE usage
├── CDS alert response
├── e-Prescribing
├── Clinical documentation
├── Medication reconciliation
├── Patient portal promotion
└── Privacy and security
```

### 4. Performance Monitoring
```
Dashboard Metrics:
├── CPOE percentage
├── e-Prescribing rate
├── Patient portal enrollment
├── Patient portal usage
├── HIE send/receive volumes
├── CDS alert override rates
└── Clinical quality measure performance
```

## References

- **ONC Certification Program**: https://www.healthit.gov/topic/certification-ehrs
- **CMS MIPS**: https://qpp.cms.gov/
- **21st Century Cures Act**: https://www.healthit.gov/curesrule/
- **CHPL (Certified Health IT Product List)**: https://chpl.healthit.gov/
- **TEFCA**: https://www.healthit.gov/topic/interoperability/policy/trusted-exchange-framework-and-common-agreement-tefca

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
