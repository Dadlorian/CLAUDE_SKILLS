# PACS Architecture Reference

## Overview
Picture Archiving and Communication System (PACS) is a medical imaging technology for storing, retrieving, managing, distributing, and presenting medical images. A PACS eliminates the need to manually file, retrieve, and transport film jackets.

## Core Components

### 1. Image Acquisition
**Sources:**
- CT scanners
- MRI systems
- X-ray machines
- Ultrasound systems
- PET/SPECT cameras
- CR/DR systems
- Mammography units

**Protocols:**
- DICOM Store (C-STORE)
- DICOMweb STOW-RS
- Direct file system import

**Workflow:**
```
Modality → Worklist Query → Acquire Images → Store to PACS
```

### 2. Archive (Storage)

#### Short-Term Storage (Cache)
- **Purpose**: Rapid access to recent studies
- **Technology**: SSD, NVMe, high-speed SAN
- **Capacity**: 30-90 days of data
- **Performance**: < 1 second retrieval time
- **Access Pattern**: Frequent reads

#### Long-Term Archive
- **Purpose**: Permanent retention
- **Technology**: HDD RAID, object storage, tape
- **Capacity**: Petabyte scale
- **Retention**: 5-10 years (or permanent)
- **Cost**: Optimized for $/TB

#### Storage Tiers
```
Tier 1: Hot Cache (SSD) - Last 30 days
Tier 2: Warm Storage (Fast HDD) - 31-365 days
Tier 3: Cold Archive (Slow HDD/Object) - 1-7 years
Tier 4: Frozen Archive (Tape/Glacier) - > 7 years
```

#### Data Migration
- **Automatic**: Rules-based migration between tiers
- **Prefetching**: Restore from cold storage to cache on access
- **Lifecycle**: Automated based on study date, access patterns
- **Verification**: Checksums ensure data integrity

### 3. Database

#### Schema Design
```sql
-- Patient Table
CREATE TABLE patients (
    patient_id VARCHAR(64) PRIMARY KEY,
    patient_name VARCHAR(256),
    birth_date DATE,
    sex CHAR(1),
    -- Additional demographics
);

-- Study Table
CREATE TABLE studies (
    study_instance_uid VARCHAR(64) PRIMARY KEY,
    patient_id VARCHAR(64) REFERENCES patients,
    study_date DATE,
    study_time TIME,
    accession_number VARCHAR(16),
    study_description VARCHAR(64),
    modalities_in_study VARCHAR(256),
    number_of_series INT,
    number_of_instances INT,
    -- Additional metadata
    INDEX idx_patient (patient_id),
    INDEX idx_study_date (study_date),
    INDEX idx_accession (accession_number)
);

-- Series Table
CREATE TABLE series (
    series_instance_uid VARCHAR(64) PRIMARY KEY,
    study_instance_uid VARCHAR(64) REFERENCES studies,
    series_number INT,
    modality VARCHAR(16),
    series_description VARCHAR(64),
    number_of_instances INT,
    -- Additional metadata
    INDEX idx_study (study_instance_uid)
);

-- Instance Table
CREATE TABLE instances (
    sop_instance_uid VARCHAR(64) PRIMARY KEY,
    series_instance_uid VARCHAR(64) REFERENCES series,
    instance_number INT,
    sop_class_uid VARCHAR(64),
    transfer_syntax_uid VARCHAR(64),
    file_path VARCHAR(512),
    file_size BIGINT,
    -- Additional metadata
    INDEX idx_series (series_instance_uid)
);
```

#### Indexing Strategy
- **Patient Queries**: patient_id, patient_name (with text search)
- **Study Queries**: study_date, accession_number, study_description
- **Series Queries**: modality, body_part
- **Full-Text Search**: For descriptions and patient names
- **Composite Indexes**: (patient_id, study_date) for common queries

#### Database Technologies
- **PostgreSQL**: Rich indexing, JSON support, open source
- **MySQL/MariaDB**: Wide adoption, good performance
- **MongoDB**: NoSQL, flexible schema for varying DICOM tags
- **Oracle**: Enterprise features, high performance
- **SQL Server**: Windows integration, good tooling

### 4. DICOM Server (Query/Retrieve)

#### C-FIND Implementation
```
Query Flow:
1. Receive C-FIND request with search criteria
2. Parse query level (PATIENT/STUDY/SERIES/IMAGE)
3. Extract query keys and matching rules
4. Execute database query
5. For each match:
   - Send C-FIND-RSP with status PENDING
   - Include requested return keys
6. Send final C-FIND-RSP with status SUCCESS
```

**Query Optimization:**
- Limit results (e.g., max 1000 matches)
- Paginate large result sets
- Cache common queries
- Database query optimization

#### C-MOVE Implementation
```
Retrieve Flow:
1. Receive C-MOVE request with UIDs
2. Query database for instance locations
3. Establish C-STORE association to destination AE
4. For each instance:
   - Read from storage
   - Send C-STORE to destination
   - Track sub-operation status
5. Send C-MOVE-RSP with completion status
```

**Performance Considerations:**
- Parallel transfers (multiple associations)
- Compression on-the-fly
- Prefetch from cold storage
- Transfer priority queuing

#### C-STORE Implementation
```
Storage Flow:
1. Receive C-STORE request
2. Validate DICOM file
3. Extract metadata
4. Check for duplicates (SOP Instance UID)
5. Store file to filesystem/object storage
6. Insert/update database records
7. Trigger post-processing (AI, routing, etc.)
8. Send C-STORE-RSP with success
```

**Validation:**
- DICOM format compliance
- SOP Class support
- Transfer syntax support
- Mandatory tag presence
- UID uniqueness

### 5. Workflow Manager

#### Functions
- **Auto-routing**: Distribute studies based on rules
- **Prefetching**: Load related priors automatically
- **Notifications**: Alert radiologists of new studies
- **Prioritization**: STAT exams to front of queue
- **Load Balancing**: Distribute workload across radiologists

#### Routing Rules
```
IF modality = "CT" AND body_part CONTAINS "chest" THEN
    route to "Chest CT Worklist"

IF priority = "STAT" THEN
    route to "Emergency Worklist"
    send_notification to "OnCall Radiologist"

IF study_description CONTAINS "stroke protocol" THEN
    route to "Neuro STAT Worklist"
    trigger AI stroke detection
```

#### Prefetching Logic
```
On study open:
1. Query for prior studies (same patient, same modality, last 2 years)
2. Prioritize most recent 3 priors
3. Retrieve to cache if not already present
4. Load in background while radiologist reviews current study
```

### 6. Diagnostic Workstation

#### Requirements
- **High-Resolution Displays**: 3MP-5MP medical-grade monitors
- **Fast Retrieval**: < 5 seconds to first image
- **Viewport Management**: Multi-study, multi-series layout
- **Image Manipulation**: Window/level, zoom, pan, rotate
- **Measurements**: Length, area, angle, Hounsfield units
- **Advanced Visualization**: MPR, MIP, 3D rendering
- **Reporting Integration**: Embedded or linked report creation
- **PACS Integration**: DICOM query/retrieve, DICOMweb

#### Rendering Pipeline
```
1. Retrieve DICOM instance
2. Decompress if needed (JPEG, JPEG 2000, etc.)
3. Extract pixel data
4. Apply modality LUT (rescale slope/intercept)
5. Apply VOI LUT (window/level)
6. Apply presentation LUT (gamma, invert)
7. Render to display
```

#### Caching Strategy
- **Instance Cache**: Recent images in memory
- **Thumbnail Cache**: Low-res previews
- **Rendered Image Cache**: Pre-rendered viewports
- **Prefetch**: Next/previous series

### 7. Web Viewer

#### Architecture
- **Backend**: DICOMweb server (WADO-RS, QIDO-RS)
- **Frontend**: JavaScript viewer (cornerstone.js, OHIF)
- **Rendering**: WebGL for 3D, Canvas for 2D
- **Streaming**: Progressive JPEG, frame-by-frame loading
- **Zero-Footprint**: No client installation

#### Performance Optimization
- **Compression**: JPEG, JPEG 2000 for transmission
- **Progressive Loading**: Show low-res then high-res
- **Frame Streaming**: Load frames as needed
- **Service Workers**: Offline caching
- **CDN**: Distribute static assets geographically

### 8. Integration Layer

#### HL7 Integration
- **ADT Messages**: Patient demographics updates (A01, A08, A40)
- **Order Messages**: Exam orders from RIS (ORM)
- **Result Messages**: Reports to EMR (ORU)
- **Interface Engine**: Mirth Connect, Rhapsody, Cloverleaf

#### FHIR Integration
- **ImagingStudy Resource**: Links to DICOM studies
- **DiagnosticReport**: Radiology reports
- **Patient/Encounter**: Demographics and context
- **RESTful API**: Modern integration approach

#### API Layer
- **RESTful API**: For custom integrations
- **Authentication**: OAuth 2.0, JWT
- **Rate Limiting**: Prevent abuse
- **Documentation**: OpenAPI/Swagger

## Architecture Patterns

### Centralized PACS
```
All Modalities → Single PACS Archive → All Workstations
```
**Pros**: Simple, centralized management, lower cost
**Cons**: Single point of failure, scalability limits

### Distributed PACS
```
Site 1 PACS ←→ Site 2 PACS ←→ Site 3 PACS
                    ↓
              Central VNA
```
**Pros**: Site autonomy, geographic distribution, resilience
**Cons**: Complex, synchronization challenges, higher cost

### Cloud PACS
```
Modalities → VPN → Cloud PACS (AWS/Azure/GCP)
                        ↓
                  Web Viewers
```
**Pros**: Scalability, disaster recovery, remote access
**Cons**: Upload bandwidth, latency, data sovereignty

### Hybrid PACS
```
On-Prem PACS (Hot Cache) ↔ Cloud Archive (Cold Storage)
```
**Pros**: Performance + scalability, cost optimization
**Cons**: Complexity, two systems to manage

## Scalability Strategies

### Horizontal Scaling
- **Multiple DICOM Servers**: Load balance across instances
- **Database Replication**: Read replicas for queries
- **Distributed Storage**: Object storage (S3, Ceph)
- **Microservices**: Independent scaling of components

### Vertical Scaling
- **Faster CPUs**: For image processing
- **More RAM**: For caching
- **Faster Storage**: SSDs, NVMe
- **Limits**: Hardware maximum, diminishing returns

### Performance Optimization
- **Caching**: Redis for metadata, local SSD for images
- **Compression**: Reduce storage and network bandwidth
- **Concurrent Processing**: Multi-threading, async I/O
- **Query Optimization**: Database indexes, query tuning
- **Connection Pooling**: Reuse database/DICOM connections

## Redundancy and High Availability

### Database HA
- **Primary-Secondary Replication**: Failover in minutes
- **Active-Active Clustering**: No downtime
- **Backup Strategy**: Daily full, hourly incremental
- **Point-in-Time Recovery**: Restore to any moment

### Storage Redundancy
- **RAID**: RAID 6 or RAID 10 for local storage
- **Replication**: Multi-site, async replication
- **Erasure Coding**: For object storage (n+k)
- **Backup**: Separate backup system, offsite copies

### Network Redundancy
- **Dual NICs**: Bonded network interfaces
- **Multiple Paths**: Diverse network routes
- **Load Balancers**: HA pair, health checks
- **Geographic Distribution**: Multi-region deployment

### Disaster Recovery
- **RTO (Recovery Time Objective)**: < 4 hours
- **RPO (Recovery Point Objective)**: < 1 hour
- **DR Site**: Geographically separated
- **DR Testing**: Quarterly failover drills
- **Backup Verification**: Regular restore tests

## Security Architecture

### Network Security
- **VLAN Segmentation**: Isolate PACS network
- **Firewall Rules**: Allow only necessary ports
- **VPN**: For remote access
- **IDS/IPS**: Intrusion detection/prevention

### Application Security
- **Authentication**: LDAP/AD integration, MFA
- **Authorization**: Role-based access control (RBAC)
- **Audit Logging**: All access tracked
- **Encryption**: TLS for DICOM, HTTPS for web

### Data Security
- **Encryption at Rest**: Full disk encryption, database encryption
- **Encryption in Transit**: TLS 1.2+, DICOM TLS
- **De-identification**: Remove PHI for research
- **Access Control**: Principle of least privilege

### Compliance
- **HIPAA**: Security and privacy rules
- **GDPR**: For European patients
- **HITECH**: Breach notification
- **SOC 2**: For cloud PACS vendors

## Monitoring and Alerting

### Metrics to Monitor
- **System Health**: CPU, memory, disk, network
- **PACS Performance**: Query time, retrieval time, storage time
- **Storage Capacity**: Used space, growth rate, time to full
- **Database Performance**: Query time, connection pool, replication lag
- **Network**: Bandwidth utilization, packet loss, latency
- **Availability**: Uptime, response time

### Alerting Thresholds
- **Critical**: Disk > 90% full, service down, replication lag > 1 hour
- **Warning**: Disk > 80% full, high CPU, slow queries
- **Informational**: Storage migration complete, backup successful

### Tools
- **System Monitoring**: Prometheus, Grafana, Nagios, Zabbix
- **Log Aggregation**: ELK stack, Splunk
- **APM**: New Relic, DataDog
- **Uptime Monitoring**: Pingdom, UptimeRobot

## Capacity Planning

### Storage Growth Calculation
```
Average Study Size: 500 MB (varies by modality)
Studies per Day: 100
Annual Growth: 100 studies/day × 365 days × 500 MB = 18.25 TB/year
5-Year Requirement: 18.25 TB × 5 × 1.2 (buffer) = 109.5 TB raw
With RAID 6 overhead (1.33x): 145.6 TB
```

### Compute Requirements
- **DICOM Server**: 1 concurrent store per 100 studies/day
- **Query/Retrieve**: Size for peak concurrent users
- **Database**: Scale for metadata size and query load
- **Network**: 1 Gbps per 50 concurrent users (viewing)

### Scaling Triggers
- **Storage**: Add capacity when 70% full
- **CPU**: Add instances when sustained > 70%
- **Memory**: Increase when swap usage detected
- **Network**: Upgrade when sustained > 60% utilization

## PACS Vendors

### Enterprise PACS
- **GE Centricity PACS**: Large healthcare systems
- **Philips IntelliSpace PACS**: Integrated with Philips modalities
- **Sectra PACS**: Orthopedic and mammography focus
- **Carestream Vue PACS**: Multi-site deployments
- **Fujifilm Synapse PACS**: Strong visualization

### Cloud PACS
- **Ambra Health**: Cloud-native, SaaS
- **Intelerad**: Cloud and on-prem options
- **RamSoft PowerServer**: Cloud PACS/RIS
- **Enlitic**: AI-integrated cloud PACS
- **Nuance PowerShare**: Cloud image exchange

### Open Source PACS
- **Orthanc**: Lightweight, REST API, plugins
- **dcm4chee**: Full-featured, Java-based
- **Horos**: macOS DICOM viewer and mini-PACS
- **OHIF Viewer**: Web-based viewer platform

## Integration Standards

### IHE Profiles
- **Scheduled Workflow (SWF)**: Modality worklist and MPPS
- **Patient Information Reconciliation (PIR)**: Patient ID reconciliation
- **Reporting Workflow (RWF)**: Report creation and distribution
- **Post-Processing Workflow (PWF)**: 3D and advanced processing

### Worklist Management
- **DICOM MWL (C-FIND)**: Query for scheduled exams
- **FHIR ImagingStudy**: Link orders to studies
- **HL7 ORM**: Order messages from RIS

### Image Sharing
- **XDS-I**: Cross-enterprise sharing
- **WADO**: Web access to images
- **Email**: Encrypted image transmission
- **Patient Portals**: Patient access to own images

## Best Practices

### Implementation
1. **Requirements Gathering**: Understand workflows thoroughly
2. **Vendor Selection**: Evaluate on workflow fit, not features
3. **Pilot Testing**: Test with real users before rollout
4. **Data Migration**: Plan for existing study migration
5. **Training**: Comprehensive user training
6. **Go-Live Support**: 24/7 support during initial weeks

### Operations
1. **Regular Backups**: Automated, verified backups
2. **Performance Monitoring**: Continuous monitoring
3. **Capacity Planning**: Plan 2 years ahead
4. **Security Patches**: Timely updates
5. **Disaster Recovery Testing**: Quarterly drills
6. **User Feedback**: Regular surveys and improvement

### Optimization
1. **Storage Tiering**: Automate based on access patterns
2. **Compression**: Use lossy compression where appropriate
3. **Prefetching**: Predictive loading of priors
4. **Query Optimization**: Index tuning, query caching
5. **Network Optimization**: QoS, dedicated bandwidth
6. **Workflow Streamlining**: Eliminate manual steps

## Future Trends

- **AI Integration**: Built-in AI analysis
- **Cloud Migration**: Hybrid and full cloud deployments
- **VNA Adoption**: Vendor-neutral long-term archives
- **Advanced Visualization**: Real-time 3D, VR/AR
- **Patient Access**: Direct patient viewing portals
- **Blockchain**: Immutable audit trails
- **Edge Computing**: Processing at acquisition point
