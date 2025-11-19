# Teleradiology Reference

## Overview

**Teleradiology** is the transmission of radiological patient images from one location to another for interpretation and consultation. It enables remote reporting, subspecialty expertise access, and 24/7 coverage.

### Key Benefits
- **Access to Expertise**: Rural hospitals access subspecialists
- **24/7 Coverage**: Nighthawk services for after-hours
- **Workload Distribution**: Balance across facilities
- **Disaster Recovery**: Backup when on-site reading unavailable
- **Efficiency**: Reduced turnaround time (TAT)

### Types of Teleradiology

**Nighthawk Services:**
- **Coverage**: Overnight and weekend preliminary readings
- **Geography**: Often leverages time zones (US to Australia)
- **Turnaround**: STAT <30 min, routine <12 hours
- **Quality**: Board-certified radiologists

**Subspecialty Reading:**
- **Neuroradiology**: Complex brain/spine cases
- **Pediatric**: Children's imaging
- **Musculoskeletal**: Orthopedic cases
- **Cardiac**: Cardiac CT/MRI
- **Purpose**: Access expertise not available locally

**Overflow/Peak Coverage:**
- **Temporary**: Handle backlogs
- **Seasonal**: Flu season, etc.
- **Staff Shortage**: Vacations, conferences

**Final Reads:**
- **Primary Service**: All interpretations remote
- **Full-time**: Replace on-site radiologists
- **Cost Savings**: Lower overhead than local staff

## Technical Architecture

### Image Transmission

**DICOM Transmission:**
```
Originating PACS → DICOM Router → Teleradiology PACS → Remote Workstation
```

**Push Model:**
- Automatic forwarding based on rules
- Studies sent immediately after acquisition
- No query needed at remote site

**Pull Model:**
- Remote radiologist queries local PACS
- On-demand retrieval
- VPN or secure connection required

**DICOMweb:**
```
Local PACS → DICOMweb Server → HTTPS/TLS → Web Viewer
```
- Modern, RESTful approach
- Better firewall traversal
- WADO-RS for retrieval, QIDO-RS for query

### Network Requirements

**Bandwidth:**
- **Minimum**: 10 Mbps for single radiologist
- **Recommended**: 50-100 Mbps for practice group
- **High Volume**: 1 Gbps for large enterprise
- **Calculation**: Average study 50-500 MB, 5-10 studies/hour

**Latency:**
- **Target**: < 100 ms round-trip
- **Acceptable**: < 200 ms
- **Impact**: Affects responsiveness, scrolling

**Reliability:**
- **Uptime**: 99.9% (8.76 hours downtime/year)
- **Redundancy**: Backup connection (4G/5G failover)
- **QoS**: Prioritize medical imaging traffic

### Compression

**Transmission Compression:**
- **Lossy JPEG 2000**: 10:1 to 20:1 for speed
- **Lossless**: For final interpretation
- **Progressive**: Load low-res first, refine

**Example:**
```
Original: 500 MB CT study
Compressed (15:1): 33 MB
Transfer time (50 Mbps): ~5 seconds
```

**Regulatory Considerations:**
- **ACR Standard**: Lossy acceptable for initial triage if lossless available
- **State Laws**: Some require lossless for final interpretation
- **Documentation**: Must document if lossy used

### Security

**Encryption:**
- **DICOM TLS**: Encrypted DICOM transmission
- **VPN**: IPsec or SSL VPN tunnel
- **DICOMweb HTTPS**: TLS 1.2 or higher
- **End-to-End**: Encrypt entire pathway

**Authentication:**
- **Multi-Factor**: Password + token/biometric
- **LDAP/AD**: Centralized user management
- **SAML/OAuth**: Single sign-on
- **Role-Based Access**: Limit access to authorized users

**Audit Logging:**
- **Access Logs**: Who viewed which studies
- **Transmission Logs**: What was sent where
- **ATNA Compliance**: IHE Audit Trail profile
- **Retention**: 6+ years typical

**HIPAA Compliance:**
- **Business Associate Agreement (BAA)**: Required with vendor
- **Encryption**: At rest and in transit
- **Access Control**: Minimum necessary
- **Breach Notification**: 60-day requirement

## Workflow Management

### Study Routing

**Rule-Based Routing:**
```
IF modality = "CT" AND body_part = "HEAD" AND priority = "STAT"
  THEN route to "Neuro STAT Worklist" at Remote Site A

IF time > 22:00 OR time < 08:00
  THEN route to "Nighthawk Service"

IF modality = "MRI" AND body_part = "CARDIAC"
  THEN route to "Cardiac Subspecialist"
```

**Dynamic Load Balancing:**
- Distribute studies based on radiologist availability
- Monitor worklist depth
- Adjust routing in real-time
- Prevent overload

### Worklist Management

**Prioritization:**
1. **STAT/Emergency**: < 30 minutes
2. **Urgent**: < 2 hours
3. **Routine**: < 24 hours
4. **Comparison/Prior**: As needed

**Tracking:**
- **Study Arrival Time**: When transmitted
- **Assignment Time**: When radiologist starts
- **Completion Time**: When report finalized
- **TAT Metrics**: Monitor performance

### Critical Findings Notification

**Workflow:**
```
1. Radiologist identifies critical finding
2. Attempt phone contact with ordering physician
3. If unsuccessful, escalate per hospital protocol
4. Document all communication attempts
5. Final report flagged as critical
```

**Examples of Critical Findings:**
- Pneumothorax
- Pulmonary embolism
- Aortic dissection/aneurysm
- Intracranial hemorrhage
- Bowel perforation

**Notification Methods:**
- **Phone Call**: Primary method
- **Secure Text**: SMS to physician
- **EMR Alert**: Popup in EMR
- **Email**: Secure email with encryption

## Viewer Requirements

### Diagnostic Workstation (On-Site Equivalent)

**Display:**
- **Resolution**: 3-5 megapixel medical-grade monitors
- **Calibration**: DICOM GSDF (Grayscale Standard Display Function)
- **Dual Monitors**: Minimum for efficient workflow
- **Luminance**: 350-500 cd/m² (calibrated)

**Performance:**
- **Load Time**: < 5 seconds to first image
- **Scrolling**: Smooth 60 fps
- **Multi-Study**: Open 5+ studies simultaneously
- **Hanging Protocols**: Customizable layouts

**Tools:**
- **Window/Level**: Presets + manual adjustment
- **MPR/MIP**: Multi-planar reformation
- **Measurements**: Length, area, angle, HU
- **Annotations**: Draw, text, arrows
- **PACS Integration**: Query, retrieve, store

### Web-Based Viewers (Zero-Footprint)

**Technology:**
- **HTML5/JavaScript**: cornerstone.js, OHIF Viewer
- **WebGL**: Hardware-accelerated rendering
- **WebAssembly**: Near-native performance
- **DICOMweb**: Modern image access

**Advantages:**
- **No Installation**: Browser-based
- **Cross-Platform**: Windows, Mac, Linux, mobile
- **Auto-Update**: Always latest version
- **Lower IT Burden**: Centralized management

**Limitations:**
- **Performance**: Slightly slower than native
- **Display Calibration**: Harder to enforce
- **Advanced Tools**: May be limited vs. desktop
- **Offline**: Requires internet connection

**Regulatory:**
- **FDA Clearance**: Some web viewers have 510(k)
- **Intended Use**: Primary vs. review only
- **Validation**: Performance equivalence to workstation

### Mobile Viewers

**Use Cases:**
- **Consultation**: Quick review for guidance
- **Triage**: Identify urgent cases
- **Critical Findings**: Review images during notification
- **NOT for Primary Diagnosis**: Screen size/quality insufficient

**Features:**
- **Touch Gestures**: Pinch-zoom, swipe
- **Offline Mode**: Download studies for review
- **Push Notifications**: New study alerts
- **Secure**: Encrypted storage, MDM support

**Examples:**
- **ResolutionMD**: FDA-cleared mobile viewer
- **Visage Ease**: Mobile app for Visage PACS
- **OHIF Mobile**: Open-source mobile viewer

## Regulatory and Legal

### State Licensing

**Requirement:**
- Radiologist must be licensed in state where patient is located
- **Example**: Patient in California, radiologist in Nevada needs CA license

**Exceptions:**
- **Emergency**: Some states allow emergency reads
- **Consultation**: Non-binding consultation may not require license

**Interstate Compacts:**
- **Efforts**: Streamline multi-state licensing
- **Status**: Limited adoption in radiology

### Standard of Care

**ACR–AAPM–SIIM Practice Parameter:**
- **Communication**: Direct with ordering physician
- **Documentation**: Record date, time, radiologist
- **Credentialing**: Equivalent to on-site radiologists
- **QA**: Regular peer review

**Turnaround Times:**
- **STAT**: 20-30 minutes
- **Urgent**: 2 hours
- **Routine**: 12-24 hours
- **Must be defined** and monitored

### Malpractice Insurance

**Coverage:**
- **Tail Coverage**: Covers claims after employment ends
- **Geographic Scope**: Must cover all states where licensed
- **Teleradiology-Specific**: Some insurers offer specialized policies

### Credentialing

**Hospital Privileges:**
- Teleradiologists need privileges at interpreting site
- Peer review by on-site radiologists
- Equivalent to local staff requirements

**Verification:**
- Board certification
- State licenses (all relevant states)
- CME credits
- Malpractice claims history

## Business Models

### Service Pricing

**Per-Study:**
- **Range**: $15-$50 per study (varies by modality)
- **Modality Weighting**: CT/MRI higher than X-ray
- **Body Part**: Neuro/cardiac higher complexity

**Full-Time Equivalent (FTE):**
- **Range**: $200K-$400K per FTE annually
- **Includes**: Benefits, vacation coverage
- **Risk Sharing**: Predictable cost

**Hourly:**
- **Range**: $150-$300 per hour
- **Use Case**: Overflow, part-time coverage
- **Variability**: Costs fluctuate with volume

**Hybrid:**
- Base retainer + per-study over threshold
- Balances predictability and flexibility

### Service Level Agreements (SLA)

**Turnaround Time:**
- STAT: 95% within 30 minutes
- Urgent: 95% within 2 hours
- Routine: 95% within 12 hours
- Penalties for non-compliance

**Availability:**
- **Uptime**: 99.5% or higher
- **Backup Coverage**: Radiologist replacement within 30 minutes
- **Holidays**: Covered without surcharge

**Quality Metrics:**
- **Discrepancy Rate**: < 5% on peer review
- **Critical Miss**: Zero tolerance
- **Report Quality**: Standardized templates

## Quality Assurance

### Peer Review

**Process:**
- **Random Sampling**: 5% of studies
- **Targeted Review**: Discrepancies, complaints
- **Scoring**: RADPEER or equivalent
- **Feedback**: Quarterly to radiologists

**RADPEER Scoring:**
- **1**: No discrepancy
- **2**: Minor discrepancy, no patient management impact
- **3**: Likely management impact, not urgent
- **4**: Major discrepancy, patient management significantly affected

### Performance Metrics

**Productivity:**
- **Studies/Hour**: 8-12 typical (varies by modality)
- **Downtime**: < 10% unproductive time
- **Report Length**: Adequate detail vs. efficiency

**Accuracy:**
- **Concordance**: Agreement with follow-up
- **Addendum Rate**: < 3%
- **Critical Miss**: Track near-zero

**Communication:**
- **Critical Findings**: 100% documented notification
- **Response Time**: Answer queries within 2 hours

### Monitor Calibration

**DICOM GSDF:**
- **Standard**: Grayscale Standard Display Function
- **Calibration**: Monthly or when drift detected
- **Tools**: Photometer, calibration software
- **Documentation**: Log calibration dates and results

**Ambient Lighting:**
- **Recommended**: < 20 lux
- **Dark Room**: Preferred for diagnostic reading
- **Glare**: Minimize reflections

## Technology Trends

### AI Integration

**Triage:**
- AI flags critical findings (PE, pneumothorax)
- Studies moved to top of worklist
- Radiologist notified immediately

**Automation:**
- **Measurements**: Automated RECIST, CAC scoring
- **Hanging Protocols**: AI-suggested layouts
- **Speech Recognition**: Automated transcription

### Cloud-Based Teleradiology

**Architecture:**
```
Hospital PACS → Cloud Gateway → Cloud PACS → Cloud Workstation
```

**Benefits:**
- **Scalability**: Handle volume spikes
- **Disaster Recovery**: Built-in redundancy
- **Cost**: Pay-as-you-go vs. infrastructure investment
- **Access**: Work from anywhere

**Concerns:**
- **Latency**: Internet dependency
- **Data Sovereignty**: Where data stored
- **Compliance**: HIPAA, GDPR

### 5G Networks

**Capabilities:**
- **Bandwidth**: Multi-Gbps speeds
- **Latency**: < 10 ms
- **Reliability**: 99.999% availability

**Use Cases:**
- **Mobile Teleradiology**: Ambulance to hospital
- **Remote Areas**: Broadband alternative
- **Disaster Response**: Rapid deployment

### Virtual Reality (VR)

**3D Visualization:**
- VR headset for immersive 3D rendering
- Surgical planning
- Complex anatomy understanding

**Current Status:**
- **Experimental**: Not yet diagnostic standard
- **Education**: Training tool
- **Future**: Potential for diagnostic use

## Case Studies

### Rural Hospital Implementation

**Scenario:**
- 25-bed rural hospital
- No on-site radiologist
- 50 studies/day (X-ray, CT, some MRI)

**Solution:**
- Teleradiology contract for 24/7 coverage
- DICOM router auto-forwards studies
- Web-based viewer for ER physicians (preliminary)
- STAT TAT: 30 minutes, routine: 8 hours

**Outcome:**
- Maintained ER accreditation
- Cost: $120K/year vs. $400K+ for on-site radiologist
- Patient satisfaction: Faster results

### Academic Medical Center Nighthawk

**Scenario:**
- Large academic hospital
- Residents on-call overnight
- 100-150 studies per night
- Faculty review in morning (delays care)

**Solution:**
- Nighthawk teleradiology (10 PM - 8 AM)
- Board-certified radiologists provide final reads
- Critical findings notification protocol
- Residents still read for training (wet reads)

**Outcome:**
- Improved patient care (final reads overnight)
- Reduced resident burnout
- Faculty review only discrepancies (10% of volume)

### Subspecialty Network

**Scenario:**
- Regional health system (5 hospitals)
- Limited subspecialty expertise
- Need neuro, cardiac, MSK subspecialists

**Solution:**
- Hybrid teleradiology model
- On-site generalists for most studies
- Route complex cases to remote subspecialists
- Web conferencing for consultations

**Outcome:**
- Improved diagnostic accuracy
- Retained patient volume (no external referrals)
- Radiologist satisfaction (complex cases get expert input)

## Challenges and Solutions

### Challenge: Time Zone Differences
**Solution:** Leverage global workforce (nighthawk to Australia/India), clearly document radiologist location

### Challenge: Image Quality Variability
**Solution:** Standardize protocols, QA at sending site, reject poor-quality studies before transmission

### Challenge: Radiologist Isolation
**Solution:** Regular video conferences, peer learning, on-site visits, team communication tools

### Challenge: Critical Findings Communication
**Solution:** Automated notification systems, backup contacts, documented workflows, audit logs

### Challenge: Network Downtime
**Solution:** Redundant connections, local cache, mobile hotspot backup, downtime protocols

### Challenge: Inconsistent Reporting
**Solution:** Standardized templates, macros, style guides, peer review feedback

## Best Practices

### Implementation
1. **Pilot Phase**: Start small, validate workflow
2. **Training**: Educate clinical staff on teleradiology process
3. **SLA Definition**: Clear expectations and metrics
4. **Backup Plan**: Local radiologist on-call for system failures
5. **Regular Review**: Monthly QA meetings with vendor

### Operations
1. **Monitor TAT**: Track and address delays
2. **Critical Findings Protocol**: Test quarterly
3. **Network Monitoring**: 24/7 with alerts
4. **Peer Review**: Consistent feedback loop
5. **Radiologist Satisfaction**: Prevent burnout, maintain quality

### Security
1. **Encryption**: All transmission paths
2. **VPN**: Secure connections for remote radiologists
3. **MFA**: Multi-factor authentication
4. **Audit**: Regular security assessments
5. **Incident Response**: Plan for breaches

## Future of Teleradiology

### Trends
- **AI-Augmented Reading**: Real-time AI assistance
- **Decentralized Model**: Radiologists work from home
- **Global Talent Pool**: Access best radiologists worldwide
- **Patient Engagement**: Direct patient communication
- **Integrated Diagnostics**: Combine imaging with genomics, pathology

### Challenges Ahead
- **Regulatory Harmonization**: Simplify multi-state licensing
- **Standardization**: Common platforms and interfaces
- **Workforce Shortage**: Growing demand, limited radiologists
- **Quality Maintenance**: Ensure consistency across providers

## Resources

- **ACR Teleradiology Practice Parameter**: Guidelines
- **SIIM**: Society for Imaging Informatics in Medicine
- **State Medical Boards**: Licensing requirements
- **Teleradiology Vendors**: Nighthawk Radiology, Virtual Radiologic, etc.
- **Legal Resources**: Healthcare law firms specializing in teleradiology
