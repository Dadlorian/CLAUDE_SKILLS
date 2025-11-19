# IHE Radiology Profiles Reference

## IHE Overview

### What is IHE?
**Integrating the Healthcare Enterprise (IHE)** is an initiative by healthcare professionals and industry to improve how computer systems in healthcare share information. IHE promotes coordinated use of established standards like DICOM and HL7.

### IHE Process
1. **Profiles**: Define specific use cases and how to use standards
2. **Actors**: Systems or components with specific roles
3. **Transactions**: Interactions between actors
4. **Integration Statements**: Vendor claims of profile support
5. **Connectathons**: Testing events to validate implementations

### IHE Domains
- **Radiology**: Medical imaging workflows
- **Cardiology**: Cardiac imaging and reports
- **Laboratory**: Lab results
- **IT Infrastructure**: Cross-enterprise sharing
- **Patient Care Coordination**: Care delivery workflows

## Core Radiology Profiles

### Scheduled Workflow (SWF)

**Purpose**: Coordinate imaging workflow from order to results

**Actors:**
- **Order Placer**: RIS/EMR creating orders
- **Order Filler**: RIS managing worklists
- **Acquisition Modality**: Imaging device
- **Image Manager/Archive**: PACS
- **Image Display**: Diagnostic workstation
- **Print Server**: Film printer (optional)

**Workflow:**
```
1. Order Placer → Order Filler: Order entry (HL7 ORM)
2. Acquisition Modality → Order Filler: Worklist query (DICOM MWL C-FIND)
3. Acquisition Modality: Perform exam
4. Acquisition Modality → Order Filler: MPPS N-CREATE/N-SET (in progress, completed)
5. Acquisition Modality → Image Manager: Store images (DICOM C-STORE)
6. Image Display → Image Manager: Query/Retrieve images (C-FIND/C-MOVE)
7. Image Display: Interpret and report
```

**Key Transactions:**
- **RAD-2**: Imaging Order Distribution (HL7 ORM)
- **RAD-4**: Procedure Scheduled (HL7 ORU)
- **RAD-5**: Worklist Query (DICOM MWL)
- **RAD-6**: MPPS Create
- **RAD-7**: MPPS Set
- **RAD-8**: Image Store (DICOM C-STORE)

**Benefits:**
- Reduced data entry errors
- Patient safety (right patient, right procedure)
- Automated workflow tracking
- Billing triggers from MPPS

### Patient Information Reconciliation (PIR)

**Purpose**: Reconcile patient demographic information across systems

**Actors:**
- **Order Placer**: Source of patient info
- **Image Manager/Archive**: PACS with patient records
- **Evidence Creator**: Modality creating evidence

**Scenarios:**
1. **Unscheduled Workflow**: Patient arrives without order
2. **Patient Merge**: Duplicate patient IDs merged
3. **Patient Update**: Demographics changed

**Key Transactions:**
- **RAD-12**: Patient Update (HL7 ADT A08)
- **RAD-13**: Patient Merge (HL7 ADT A40)

**Benefits:**
- Maintains data integrity across systems
- Handles emergency/unscheduled exams
- Corrects patient ID errors

### Post-Processing Workflow (PWF)

**Purpose**: Manage workflow for post-processing (3D, advanced visualization)

**Actors:**
- **Image Manager/Archive**: PACS
- **Evidence Creator**: Post-processing workstation
- **Report Manager**: RIS managing reports

**Workflow:**
```
1. Radiologist selects study for post-processing
2. Image Manager → Evidence Creator: Request post-processing
3. Evidence Creator: Performs analysis (3D, MPR, etc.)
4. Evidence Creator → Image Manager: Store results (DICOM SR, SC, 3D)
5. Report Manager: Access results for reporting
```

**DICOM Objects:**
- **Grayscale Softcopy Presentation State**: Annotations, measurements
- **Key Object Selection**: Important images/findings
- **Structured Report**: Measurements, CAD results
- **Secondary Capture**: Screen saves

**Benefits:**
- Standardized post-processing workflow
- Results stored with study
- Available to all authorized users

### Reporting Workflow (RWF)

**Purpose**: Distribute radiology reports

**Actors:**
- **Image Display/Report Creator**: Workstation with reporting
- **Report Manager**: RIS managing reports
- **Report Repository**: Storage for reports
- **Report Reader**: Referring physician system

**Workflow:**
```
1. Report Creator: Dictate/transcribe report
2. Report Creator → Report Manager: Submit for approval
3. Radiologist: Approve report
4. Report Manager → Report Repository: Store final report
5. Report Manager → Referring Physician: Deliver report (HL7 ORU)
```

**Report Formats:**
- **HL7 ORU**: Text report in HL7 message
- **DICOM SR**: Structured report with measurements
- **PDF**: Encapsulated PDF in DICOM
- **CDA**: Clinical Document Architecture XML

**Benefits:**
- Timely report delivery
- Structured reporting support
- Consistent workflow

### Charge Posting (CHG)

**Purpose**: Automate billing/charging based on performed procedures

**Actors:**
- **Order Filler**: RIS tracking procedures
- **Charge Processor**: Billing system

**Workflow:**
```
1. Procedure completed (via MPPS)
2. Order Filler → Charge Processor: Charge posting (HL7 DFT)
```

**Benefits:**
- Automated billing
- Reduced lost charges
- Immediate posting

### Import Reconciliation Workflow (IRWF)

**Purpose**: Handle imported images from outside facilities

**Actors:**
- **Image Manager/Archive**: PACS
- **Evidence Creator**: Import workstation
- **Order Filler**: RIS with orders

**Scenarios:**
1. Patient brings CD from outside
2. Images received via network
3. Scanned film images

**Workflow:**
```
1. Import images to temporary storage
2. Reconcile patient demographics
3. Link to existing or create new study
4. Store reconciled images to PACS
```

**Benefits:**
- Standardized import process
- Patient safety (correct patient match)
- Integration with existing studies

## IT Infrastructure Profiles

### Cross-Enterprise Document Sharing - Imaging (XDS-I)

**Purpose**: Share medical images across different healthcare enterprises

**Architecture:**
- **Document Registry**: Metadata repository
- **Document Repository**: Image storage
- **Image Source**: PACS publishing images
- **Image Consumer**: External facility accessing images
- **Patient Identity Source**: Master patient index

**Workflow:**
```
1. Image Source → Document Repository: Provide & Register (images + metadata)
2. Document Repository → Document Registry: Register metadata
3. Image Consumer → Document Registry: Query for studies
4. Image Consumer → Document Repository: Retrieve images
```

**Standards:**
- **Registry Stored Query**: ITI-18 (HL7 V3, SOAP)
- **Retrieve Document Set**: ITI-43 (HTTP)
- **Provide & Register**: ITI-41 (MTOM/XOP)

**Benefits:**
- Regional health information exchange
- Reduced duplicate exams
- Improved care coordination
- Patient access to images

### Patient Identifier Cross-Referencing (PIX)

**Purpose**: Correlate patient identifiers across different systems

**Actors:**
- **Patient Identity Source**: RIS, PACS with local IDs
- **Patient Identifier Cross-reference Manager**: Master Patient Index (MPI)
- **Patient Identifier Cross-reference Consumer**: System needing ID correlation

**Transactions:**
- **ITI-8**: Patient Identity Feed (HL7 ADT A01, A04, A08, A40)
- **ITI-9**: PIX Query (HL7 QBP^Q23)
- **ITI-10**: PIX Update Notification (HL7 ADT A31, A40)

**Use Case:**
```
Patient has ID "12345" in RIS, "ABC789" in PACS
PIX Manager maintains: 12345 (RIS) ↔ ABC789 (PACS)
Query with "12345" returns "ABC789" for PACS access
```

**Benefits:**
- Links records across systems
- Enables cross-enterprise sharing
- Handles merges and updates

### Patient Demographics Query (PDQ)

**Purpose**: Query patient demographic information

**Actors:**
- **Patient Demographics Supplier**: Master patient index
- **Patient Demographics Consumer**: System needing patient info

**Transaction:**
- **ITI-21**: Patient Demographics Query (HL7 QBP^Q22)
- **ITI-22**: Patient Demographics and Visit Query

**Query Parameters:**
- Patient Name (fuzzy matching supported)
- Patient ID
- Date of Birth
- Sex
- Address

**Benefits:**
- Accurate patient selection
- Demographic verification
- Duplicate detection

### Audit Trail and Node Authentication (ATNA)

**Purpose**: Security framework for healthcare systems

**Actors:**
- **Secure Node**: Any system handling PHI
- **Secure Application**: Applications on secure nodes
- **Audit Record Repository**: Centralized audit log
- **Time Server**: NTP time source

**Requirements:**
- **Node Authentication**: TLS with certificates
- **Audit Logging**: RFC 3881 format, syslog transmission
- **Time Synchronization**: NTP for consistent timestamps

**Audited Events:**
- User authentication
- Patient record access
- Data export/import
- Configuration changes
- Security events

**Benefits:**
- HIPAA compliance
- Security incident detection
- Accountability

### Consistent Time (CT)

**Purpose**: Synchronize time across all systems

**Actor:**
- **Time Client**: All systems
- **Time Server**: NTP server

**Transaction:**
- **ITI-1**: Maintain Time (NTP protocol)

**Requirements:**
- Accuracy: ±1 second
- Synchronization interval: ≤ 4 hours

**Benefits:**
- Accurate event sequencing
- Reliable audit trails
- Workflow coordination

## Advanced Radiology Profiles

### Invoke Image Display (IID)

**Purpose**: Launch external viewer from EMR/RIS

**Actors:**
- **Image Display Invoker**: EMR/RIS
- **Image Display**: DICOM viewer

**Launch Methods:**
- **HTTP**: URL with parameters (studyUID, patientID)
- **HL7**: Message with launch instructions
- **Context Sharing**: CCOW, FHIRcast

**Example URL:**
```
http://viewer.hospital.org/launch?
  studyUID=1.2.840.113619.2.1.1.1&
  patientID=12345&
  accession=A20240315001
```

**Benefits:**
- Single-click image access from EMR
- Context synchronization
- Improved workflow efficiency

### Portable Data for Imaging (PDI)

**Purpose**: Create patient imaging summary on portable media (CD/DVD)

**Actors:**
- **Portable Media Creator**: Export workstation
- **Portable Media Importer**: Import workstation

**Media Contents:**
- **DICOMDIR**: Index file for images
- **Images**: DICOM files in standard hierarchy
- **Viewer**: Auto-run viewer application (optional)
- **README**: Patient instructions

**Directory Structure:**
```
/DICOM/
  DICOMDIR
  PATIENT1/
    STUDY1/
      SERIES1/
        IMAGE001.dcm
        IMAGE002.dcm
      SERIES2/
        IMAGE001.dcm
/VIEWER/
  viewer.exe
autorun.inf
README.txt
```

**Benefits:**
- Patient data portability
- Outside consultation
- Emergency access
- Backup

### Teaching File and Clinical Trial Export (TCE)

**Purpose**: De-identify images for teaching or research

**Actors:**
- **Teaching File/Clinical Trial System**: Repository
- **Teaching File/Clinical Trial Creator**: Export workstation

**De-identification:**
- **Basic Profile**: Remove/blank standard PHI tags
- **Retain Safe Private**: Keep safe private tags (UID mapping)
- **Retain UIDs**: Maintain relationships (clinical trials)
- **Retain Device Identity**: Keep equipment info
- **Retain Patient Characteristics**: Age, sex (research)

**Audit:**
- Log all exports
- Track de-identified studies
- Reversible de-identification (research)

**Benefits:**
- HIPAA-compliant teaching files
- Clinical trial data sharing
- Research collaboration

### Radiation Exposure Monitoring (REM)

**Purpose**: Track and monitor patient radiation exposure

**Actors:**
- **Dose Information Reporter**: Modality reporting dose
- **Dose Information Consumer**: Dose tracking system
- **Dose Registry**: Centralized dose repository

**DICOM Objects:**
- **Radiation Dose SR**: Structured dose report
- **CT Dose Check**: Alerts for high dose
- **X-Ray Dose SR**: Fluoroscopy dose

**Tracked Metrics:**
- **CT**: CTDIvol, DLP
- **Fluoroscopy**: Air Kerma, DAP
- **Radiography**: Entrance dose
- **Nuclear Medicine**: Radiopharmaceutical dose

**Workflow:**
```
1. Modality performs exam
2. Modality → Dose Registry: Store dose SR
3. Dose Registry: Track cumulative dose
4. Alert if thresholds exceeded
```

**Benefits:**
- Patient safety
- Dose optimization
- Regulatory compliance
- Quality improvement

### AI Results (AIR)

**Purpose**: Integrate AI results into radiology workflow

**Actors:**
- **AI Workflow Manager**: Orchestrates AI processing
- **AI Service**: AI algorithm provider
- **Evidence Creator**: Creates result documents

**Workflow:**
```
1. New study arrives
2. AI Workflow Manager → AI Service: Send images
3. AI Service: Perform inference
4. AI Service → Evidence Creator: Return results
5. Evidence Creator: Create DICOM SR/SC
6. Store results with study
```

**Result Formats:**
- **DICOM SR**: Structured findings
- **DICOM SC**: Annotated images
- **DICOM SEG**: Segmentation objects
- **Presentation State**: Overlays

**Benefits:**
- Standardized AI integration
- Worklist prioritization
- Quality assurance
- Clinical validation

## IHE Implementation

### Integration Statement
Documents what IHE profiles and actors a product supports:

```
Product: MyPACS v5.0
Vendor: Medical Imaging Inc.

Supported IHE Profiles:
- Scheduled Workflow (SWF)
  - Image Manager/Archive (ACTOR)
  - Image Display (ACTOR)
- XDS-I
  - Imaging Document Source (ACTOR)
- ATNA
  - Secure Node (ACTOR)

Standards:
- DICOM 2023e
- HL7 v2.5
```

### Connectathon Testing
Annual testing events where vendors validate interoperability:
- Test with multiple vendors
- Verify transactions
- Document results
- Publish outcomes

### Conformance
- **Profile Conformance**: Implement all required transactions
- **Option Support**: Document optional features
- **Standards Versions**: Specify DICOM/HL7 versions
- **Constraints**: Any limitations or extensions

## IHE Profile Selection Guide

### Small Imaging Center
**Essential:**
- Scheduled Workflow (SWF)
- Patient Information Reconciliation (PIR)

**Optional:**
- Portable Data for Imaging (PDI) - for CD burning
- Reporting Workflow (RWF) - if complex reporting

### Hospital Enterprise PACS
**Essential:**
- Scheduled Workflow (SWF)
- Patient Information Reconciliation (PIR)
- Post-Processing Workflow (PWF)
- Reporting Workflow (RWF)
- ATNA (security)
- Consistent Time (CT)

**Recommended:**
- Charge Posting (CHG)
- Import Reconciliation Workflow (IRWF)
- Radiation Exposure Monitoring (REM)

### Regional Health Information Exchange
**Essential:**
- XDS-I
- PIX
- PDQ
- ATNA

**Optional:**
- Cross-Community Access (XCA) - for nationwide exchange

### Research Institution
**Essential:**
- Scheduled Workflow (SWF)
- Teaching File and Clinical Trial Export (TCE)
- ATNA

**Recommended:**
- AI Results (AIR) - for research applications

## Benefits of IHE Profiles

### For Healthcare Providers
- **Reduced integration costs**: Pre-defined standards
- **Faster deployment**: Proven implementations
- **Vendor independence**: Multi-vendor interoperability
- **Best practices**: Industry-validated workflows

### For Vendors
- **Clear requirements**: Defined use cases
- **Market differentiation**: Certified compliance
- **Reduced development**: Reuse specifications
- **Interoperability**: Tested with other vendors

### For Patients
- **Better care**: Coordinated information
- **Safety**: Reduced errors
- **Access**: Images available where needed
- **Privacy**: Security frameworks

## Resources

- **IHE Radiology Technical Framework**: Complete specifications
- **IHE Profiles at a Glance**: Quick reference
- **Connectathon Results**: Vendor testing outcomes
- **IHE Wiki**: Implementation guidance
- **Webinars**: Educational resources
