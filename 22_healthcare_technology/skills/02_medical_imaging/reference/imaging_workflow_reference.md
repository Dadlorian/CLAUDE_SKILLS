# Medical Imaging Workflow Reference

## Complete Imaging Workflow

### End-to-End Process
```
1. Order Creation (RIS/EMR)
2. Scheduling (Appointment)
3. Patient Registration
4. Pre-Exam Preparation
5. Exam Performance (Modality)
6. Image QA and Sending
7. Image Archiving (PACS)
8. Worklist Assignment
9. Image Interpretation
10. Report Creation and Approval
11. Report Distribution
12. Clinical Action
13. Follow-up and Billing
```

## Pre-Examination Workflow

### Order Entry

**RIS Order Creation:**
```
Physician Decision → EMR Order Entry → RIS
```

**Required Information:**
- **Patient Demographics**: Name, DOB, MRN, gender
- **Clinical Indication**: Reason for exam
- **Procedure**: CPT code, description
- **Priority**: STAT, urgent, routine
- **Ordering Physician**: Referring/requesting physician
- **Insurance**: Authorization, pre-cert

**HL7 ORM Message (Order):**
```
MSH|^~\&|EMR|HOSPITAL|RIS|HOSPITAL|20240315143000||ORM^O01|12345|P|2.5
PID|1||123456^^^HOSPITAL^MRN||DOE^JOHN^A||19800515|M|||123 MAIN ST^^CITY^ST^12345
PV1|1|O|RAD||||^SMITH^JANE^^^DR|||||||||||
ORC|NW|A2024031500123|||||||20240315143000
OBR|1|A2024031500123||71020^CHEST XRAY 2 VIEWS|||20240315143000
```

### Scheduling

**Appointment Booking:**
- **Check Availability**: Modality schedule
- **Time Estimation**: Based on procedure
- **Patient Preparation**: Fasting, contrast, medications
- **Resource Allocation**: Room, equipment, staff

**Scheduling Considerations:**
- **Modality**: CT, MRI, X-ray availability
- **Technologist**: Specialized skills (cardiac MRI, peds)
- **Contrast**: IV access, renal function check
- **Urgency**: STAT overrides routine schedule
- **Patient Needs**: Wheelchair access, sedation

**Confirmation:**
- Automated reminders (phone, SMS, email)
- Prep instructions sent
- Insurance verification

### Patient Registration

**Check-In:**
- Verify demographics
- Update insurance
- Obtain consent
- Screen for contraindications

**Safety Screening:**
- **MRI**: Implants, pacemakers, pregnancy
- **Contrast**: Allergies, renal function (GFR)
- **Radiation**: Pregnancy status
- **Claustrophobia**: Sedation needs

**Consent:**
- Procedure risks/benefits
- Contrast administration
- Radiation exposure
- Documentation (signature, witness)

## Examination Workflow

### Modality Worklist (MWL)

**DICOM Worklist Query (C-FIND):**
```
Modality → RIS: Query for today's schedule
RIS → Modality: Return worklist items
```

**Worklist Entry Contains:**
- Patient demographics
- Accession number
- Procedure description
- Scheduled date/time
- Requesting physician

**Benefits:**
- **Reduces Errors**: No manual entry of patient data
- **Consistency**: Same data in modality and RIS
- **Efficiency**: Pre-populated fields
- **Billing**: Accurate procedure capture

### Image Acquisition

**Technologist Workflow:**
```
1. Select patient from worklist
2. Position patient
3. Scout/localizer scan
4. Select protocol
5. Acquire images
6. Review for quality
7. Additional acquisitions if needed
8. Complete exam
```

**Protocol Selection:**
- **Anatomic Region**: Chest, abdomen, brain, etc.
- **Clinical Indication**: Trauma, cancer, infection
- **Patient Factors**: Weight, age, contrast
- **Modality-Specific**: kVp, mAs, sequences, contrast timing

**Quality Control:**
- **Image Quality**: Resolution, artifacts, contrast
- **Patient Coverage**: Entire region of interest
- **Technical Factors**: Proper exposure, no motion
- **Repeat Criteria**: When to re-scan

### Modality Performed Procedure Step (MPPS)

**Purpose:** Notify RIS/PACS that exam is in progress or completed

**MPPS Workflow:**
```
1. Exam Starts → N-CREATE (IN PROGRESS)
   - Procedure step status
   - Scheduled procedure
   - Patient information

2. Exam Ends → N-SET (COMPLETED)
   - Final status
   - Performed procedure
   - Images created (series UIDs)
   - Exposure dose (if applicable)
```

**Benefits:**
- **Real-time Status**: RIS knows exam state
- **Billing Trigger**: Automate charge posting
- **Workflow Tracking**: Monitor exam progress
- **Data Integrity**: Link images to orders

### Image Transmission

**DICOM Store (C-STORE):**
```
Modality → PACS: Send images
PACS: Validate, store, respond
```

**Transmission Modes:**
- **Automatic**: Send immediately after acquisition
- **Manual**: Technologist triggers send
- **Batch**: Send at end of day (rare)

**Error Handling:**
- **Retry**: Automatic retry on network error
- **Queue**: Store locally if PACS unavailable
- **Alert**: Notify IT if persistent failure

## Post-Acquisition Workflow

### PACS Processing

**Image Receipt:**
```
1. Receive C-STORE request
2. Validate DICOM compliance
3. Extract metadata
4. Check for duplicates (SOP Instance UID)
5. Store to filesystem/object storage
6. Update database (patient, study, series, instance)
7. Generate thumbnails
8. Apply routing rules
9. Send C-STORE response (success/failure)
```

**Auto-Routing:**
```
IF priority = "STAT" THEN
  - Route to "Emergency Worklist"
  - Send notification to on-call radiologist

IF study_description CONTAINS "stroke protocol" THEN
  - Route to "Neuro STAT"
  - Trigger AI stroke analysis
  - Prefetch prior brain studies

IF modality = "MR" AND body_part = "CARDIAC" THEN
  - Route to "Cardiac Subspecialist"
```

### Prefetching

**Intelligent Prior Retrieval:**
```
On Study Arrival:
1. Query for prior studies (same patient, relevant modality)
2. Prioritize:
   - Most recent first
   - Same body part
   - Last 2 years
3. Retrieve to cache (C-MOVE from archive)
4. Preload thumbnails
5. Ready when radiologist opens study
```

**Benefits:**
- **Time Savings**: No wait for priors
- **Complete Comparison**: All relevant history available
- **Better Diagnosis**: Longitudinal assessment

### Worklist Management

**Worklist Population:**
- New studies auto-populate worklist
- Sorted by priority, then arrival time
- Filtering by modality, body part, reading radiologist

**Assignment Strategies:**

**Manual:**
- Radiologist selects from global worklist
- Flexible but can lead to cherry-picking

**Auto-Assignment:**
- Round-robin distribution
- Load balancing by radiologist availability
- Subspecialty routing

**Hybrid:**
- STAT auto-assigned immediately
- Routine available for selection
- Escalation if study waits too long

**Worklist States:**
- **Unassigned**: Available for assignment
- **Assigned**: Allocated to radiologist
- **In Progress**: Radiologist viewing
- **Dictated**: Report in progress
- **Preliminary**: Wet read complete
- **Final**: Signed report

## Interpretation Workflow

### Image Review

**Hanging Protocols:**
```
Chest CT Protocol:
- Viewport 1: Axial lung window (current)
- Viewport 2: Axial mediastinum window (current)
- Viewport 3: Coronal lung window (current)
- Viewport 4: Prior study (if available)
```

**Customization:**
- By modality and body part
- By indication (trauma vs. cancer)
- Personal preference
- One-click layout application

### Comparison Studies

**Workflow:**
- Automatic retrieval of most relevant priors
- Side-by-side display
- Synchronized scrolling and window/level
- Linking of same anatomy
- Change detection (growth, resolution)

**Key Images:**
- Radiologist marks important findings
- Quick navigation to critical slices
- Shared with referring physicians

### Measurements and Annotations

**Tools:**
- **Length**: Tumor size, nodule diameter
- **Area**: ROI for density measurement
- **Volume**: 3D lesion volume
- **Angle**: Scoliosis, joint angles
- **Hounsfield Units**: CT density
- **Annotations**: Arrows, text, circles

**Structured Reporting:**
- Template-driven reporting
- Discrete data elements
- Standardized terminology (RadLex)
- Auto-populated from measurements
- Exportable as DICOM SR

## Reporting Workflow

### Report Creation

**Dictation:**
```
1. Radiologist dictates via microphone or foot pedal
2. Speech recognition converts to text (real-time)
3. Radiologist reviews and edits
4. Insert macros/templates as needed
5. Save preliminary report
```

**Templates/Macros:**
- Normal exam templates
- Common findings libraries
- Comparison statements
- Recommendation phrases

**Speech Recognition:**
- **Real-time**: Dragon Medical, M*Modal
- **Accuracy**: 95-98% with training
- **Training**: Voice profile for accuracy
- **Editing**: Inline corrections

### Critical Findings Communication

**Critical Results:**
- Pneumothorax
- Pulmonary embolism
- Aortic dissection/aneurysm
- Acute stroke
- Bowel perforation
- Intracranial hemorrhage

**Communication Workflow:**
```
1. Radiologist identifies critical finding
2. Document in report: "Critical finding discussed with..."
3. Attempt direct phone call to ordering physician
4. If unavailable:
   - Call answering service/on-call
   - Document time and person notified
   - Escalate per hospital policy
5. Document all communication attempts
6. Flag report as "Critical"
7. Alert in EMR
```

**Documentation:**
- Date and time of communication
- Person notified (name, role)
- Content of communication
- Response/action taken

### Report Approval

**Workflow:**
```
Preliminary Report (Wet Read) → Attending Review → Final Report
```

**Addendum:**
- Corrections or additional information
- Clearly marked as "ADDENDUM"
- Original report preserved
- Reason for addendum documented

**Report States:**
- **Draft**: In progress, not visible to clinicians
- **Preliminary**: Available for clinical action, pending attending review
- **Final**: Signed, official report
- **Amended**: Addendum added

### Report Distribution

**HL7 ORU Message (Result):**
```
MSH|^~\&|RIS|HOSPITAL|EMR|HOSPITAL|20240315160000||ORU^R01|67890|P|2.5
PID|1||123456^^^HOSPITAL^MRN||DOE^JOHN^A||19800515|M
OBR|1|A2024031500123||71020^CHEST XRAY 2 VIEWS|||20240315143000|||||||^SMITH^JANE^^^DR
OBX|1|TX|IMPRESSION||No acute cardiopulmonary abnormality.
```

**Distribution Channels:**
- **EMR**: HL7 ORU message, FHIR DiagnosticReport
- **RIS**: Direct database update
- **Fax**: For external providers (legacy)
- **Secure Email**: Encrypted, HIPAA-compliant
- **Patient Portal**: Patient access to reports

**Notifications:**
- **Ordering Physician**: Report availability alert
- **Patient**: Portal notification (non-critical findings)
- **Care Team**: EMR inbox message

## Post-Interpretation Workflow

### Clinical Action

**Referring Physician:**
- Reviews report in EMR
- Correlates with clinical presentation
- Determines next steps (treatment, follow-up, additional imaging)

**Multidisciplinary Conference:**
- Tumor boards
- Radiology-pathology correlation
- Treatment planning
- Radiologist presents imaging

### Follow-Up Recommendations

**Tracking:**
- **Incidental Findings**: Lung nodules, adrenal masses
- **Follow-Up Interval**: 3 months, 6 months, 1 year
- **Reminder System**: Automated alerts in EMR
- **Compliance Monitoring**: Track adherence

**Example Recommendation:**
```
"3mm lung nodule, right upper lobe. Recommend follow-up CT chest in 6-12 months per Fleischner guidelines."
```

### Billing and Coding

**CPT Codes:**
- Procedure codes for imaging services
- Professional component (interpretation)
- Technical component (equipment, staff)

**Charge Posting:**
```
MPPS Completed → RIS → HL7 DFT Message → Billing System
```

**Components:**
- **Professional Fee**: Radiologist interpretation
- **Technical Fee**: Facility, equipment, technologist
- **Contrast**: Separately billable
- **Modifiers**: Bilateral, multiple procedures

### Quality Assurance

**Peer Review:**
- Random sampling (5-10% of studies)
- Targeted review (discrepancies, complaints)
- RADPEER scoring
- Feedback to radiologists

**Discrepancy Analysis:**
- Compare to final pathology/surgery
- Compare wet reads to final reports
- Identify systematic issues
- Educational opportunities

**Performance Metrics:**
- **Turnaround Time**: Order to final report
- **Report Quality**: Completeness, clarity
- **Critical Findings**: Communication compliance
- **Patient Satisfaction**: Survey scores

## Workflow Optimization

### Lean Principles

**Identify Waste:**
- Waiting time for images to load
- Searching for priors
- Manual data entry
- Redundant steps

**Value Stream Mapping:**
- Document current workflow
- Identify value-added vs. non-value-added steps
- Eliminate or reduce waste
- Measure improvement

### Automation

**Automated Processes:**
- Auto-routing based on rules
- Prefetching of priors
- Speech recognition
- Structured reporting templates
- Critical findings alerts
- Billing charge posting

**AI Augmentation:**
- Triage (prioritize critical cases)
- CAD (detect nodules, PE, fractures)
- Quantification (volumes, measurements)
- Protocol selection
- Quality control

### Metrics and KPIs

**Volume Metrics:**
- Studies per day/month
- By modality, body part
- Growth trends

**Efficiency Metrics:**
- **TAT (Turnaround Time)**: Order to final report
  - STAT: < 1 hour
  - Urgent: < 4 hours
  - Routine: < 24 hours
- **Report Time**: Study complete to report final
- **Radiologist Productivity**: Studies per hour

**Quality Metrics:**
- **Discrepancy Rate**: Peer review findings
- **Critical Findings Communication**: 100% compliance
- **Addendum Rate**: < 3%
- **Patient Satisfaction**: Survey scores

**Financial Metrics:**
- Revenue per exam
- Cost per exam
- RVU (Relative Value Units) per radiologist
- Charge capture rate (should be ~100%)

## Specialized Workflows

### Emergency/STAT Imaging

**Fast-Track Workflow:**
```
1. STAT order flagged in RIS
2. Immediate scheduling (bump routine)
3. Technologist alerted
4. Exam performed immediately
5. Images priority transmitted to PACS
6. Auto-routed to "STAT Worklist"
7. Radiologist immediately notified
8. Prelim read within 30 minutes
9. Critical findings communication
10. Final report within 1 hour
```

### Interventional Radiology

**Pre-Procedure:**
- Review prior imaging
- Consent
- Pre-procedure labs (coags, platelets)
- NPO status

**Intra-Procedure:**
- Real-time fluoroscopy
- Cone-beam CT
- Immediate image review
- Documentation of findings

**Post-Procedure:**
- Immediate follow-up imaging
- Recovery monitoring
- Discharge instructions
- Biopsy to pathology

### Mobile/Portable Imaging

**Workflow:**
```
1. Order for bedside imaging (ICU, ER)
2. Portable unit dispatched
3. Technologist goes to patient
4. Acquire images on portable detector
5. Transmit wirelessly or dock to workstation
6. Images sent to PACS
7. Interpreted in normal workflow
```

**Challenges:**
- Image quality (portable vs. fixed equipment)
- Infection control
- Patient positioning
- Wireless reliability

### Teleradiology

**Workflow:**
```
1. Study completed at originating site
2. Auto-forwarded to teleradiology PACS
3. Notification sent to remote radiologist
4. Remote interpretation
5. Report sent back to originating RIS
6. Critical findings communicated directly
```

## Workflow Technology Stack

### RIS (Radiology Information System)
- Order management
- Scheduling
- Reporting
- Billing

### PACS (Picture Archiving and Communication System)
- Image storage
- Query/Retrieve
- Viewing
- Distribution

### EMR/EHR (Electronic Medical Record)
- Orders
- Results viewing
- Clinical documentation
- Patient portal

### Workflow Orchestration
- IHE profiles (SWF, PIR, PWF, RWF)
- HL7 messaging
- DICOM services
- Rules engine

### Analytics
- Business intelligence
- Performance dashboards
- Quality metrics
- Predictive analytics

## Future Workflow Innovations

### AI-Driven Workflow
- Intelligent triage (priority based on AI findings)
- Automated measurements and quantification
- Predictive protocols (optimal scan parameters)
- Auto-generated preliminary reports

### Patient-Centric Workflow
- Self-scheduling via patient portal
- Real-time status updates (exam progress)
- Direct report access with explanations
- Interactive 3D images for patients

### Voice-Activated Workflow
- "Alexa, open next chest CT"
- "Apply lung window"
- "Show prior study"
- Hands-free navigation

### Cloud-Native Workflow
- Zero-footprint viewers (work anywhere)
- Global worklists (distributed reading)
- Real-time collaboration
- Seamless teleradiology

### Blockchain for Imaging
- Immutable audit trail
- Patient consent tracking
- Image provenance
- Cross-enterprise sharing without central authority

## Best Practices

### Workflow Design
1. **Involve End Users**: Radiologists, technologists, referring physicians
2. **Map Current State**: Understand before changing
3. **Identify Pain Points**: Focus on biggest issues
4. **Prioritize**: High-impact, feasible improvements first
5. **Pilot Test**: Small-scale before enterprise rollout
6. **Measure**: KPIs before and after
7. **Iterate**: Continuous improvement

### Change Management
1. **Communication**: Explain why change is happening
2. **Training**: Comprehensive, role-specific
3. **Support**: Super-users, helpdesk, on-site during go-live
4. **Feedback**: Listen and adjust
5. **Celebrate Wins**: Recognize improvements

### Continuous Improvement
1. **Regular Metrics Review**: Monthly dashboard review
2. **User Feedback**: Surveys, focus groups
3. **Benchmarking**: Compare to industry standards
4. **Technology Updates**: Stay current with new features
5. **Process Refinement**: Adjust workflows as needs change

## Resources

- **SIIM Workflow Resources**: Society for Imaging Informatics
- **ACR Imaging 3.0**: Value-based imaging initiative
- **IHE Radiology Profiles**: Standard workflows
- **Lean Healthcare**: Process improvement methods
- **HIMSS Imaging**: Healthcare IT for imaging
