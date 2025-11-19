# HIPAA Audit Logging Requirements Reference

## Regulatory Basis

### Security Rule Audit Controls (§164.312(b))

**Requirement:** Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use electronic protected health information (ePHI).

**Standard Type:** Required Implementation Specification

**Scope:** All information systems containing or using ePHI

## Core Audit Logging Requirements

### What Must Be Logged

#### 1. User Access Events

**Login/Logout:**
- User ID
- Date and time of login
- Date and time of logout
- Workstation/device identifier
- IP address
- Login method (local, remote, VPN)
- Success or failure
- Failed login attempts
- Account lockouts

**Example Log Entry:**
```
2024-01-15 08:23:45 | USER_LOGIN | SUCCESS | user.jsmith | workstation-42 | 192.168.1.100 | LOCAL
2024-01-15 08:24:12 | USER_LOGIN | FAILED | user.jdoe | workstation-13 | 10.0.1.50 | INVALID_PASSWORD
```

#### 2. PHI Access Events

**View/Read:**
- User ID
- Date and time
- Patient identifier (MRN, name, DOB)
- Type of information accessed (demographics, clinical notes, lab results, imaging, etc.)
- Specific record/document accessed
- Access method (application, report, query)
- Duration of access
- Workstation/device

**Create/Modify:**
- User ID
- Date and time
- Patient identifier
- Type of information created/modified
- Specific field(s) changed
- Old value (where feasible)
- New value
- Reason for change (if captured)

**Delete:**
- User ID
- Date and time
- Patient identifier
- Type of information deleted
- Reason for deletion
- Soft delete vs. hard delete

**Print:**
- User ID
- Date and time
- Patient identifier
- Documents/reports printed
- Printer used
- Number of copies

**Export/Download:**
- User ID
- Date and time
- Patient identifier(s)
- Data exported
- Export format
- Destination
- Number of records

**Example Log Entry:**
```
2024-01-15 08:25:33 | PHI_VIEW | user.jsmith | MRN:123456 | Patient:Doe,John | Record:LabResults | Test:CBC | workstation-42
2024-01-15 08:27:15 | PHI_MODIFY | user.jsmith | MRN:123456 | Field:Diagnosis | Old:NULL | New:Type2Diabetes | Reason:DiagnosisUpdate
```

#### 3. Administrative Actions

**Permission Changes:**
- Administrator ID
- Date and time
- User affected
- Permission/role added or removed
- Previous permissions
- New permissions
- Reason for change

**User Account Management:**
- Administrator ID
- Date and time
- Action (create, modify, disable, delete)
- User affected
- Changes made

**System Configuration Changes:**
- Administrator ID
- Date and time
- System/application affected
- Configuration parameter changed
- Old value
- New value
- Reason for change

**Security Settings:**
- Administrator ID
- Date and time
- Security control modified
- Previous setting
- New setting
- Justification

**Example Log Entry:**
```
2024-01-15 09:15:22 | PERMISSION_CHANGE | admin.kbrown | TargetUser:user.jsmith | Action:ADD_ROLE | Role:RadiologyAccess | Reason:TicketREQ-12345
```

#### 4. Security Events

**Access Violations:**
- User ID
- Date and time
- Attempted action
- Resource accessed
- Reason for denial (insufficient permissions, invalid credentials)

**Suspicious Activity:**
- User ID
- Date and time
- Activity description
- Risk level
- Automated response taken

**Malware Detection:**
- Date and time
- Affected system/user
- Malware type
- Source
- Action taken

**Intrusion Attempts:**
- Date and time
- Source IP
- Target system
- Attack type
- Response/mitigation

**Example Log Entry:**
```
2024-01-15 10:42:18 | ACCESS_VIOLATION | user.mjones | Action:VIEW_PHI | MRN:987654 | Reason:INSUFFICIENT_PERMISSIONS | RiskLevel:MEDIUM
```

#### 5. Emergency Access

**Break-Glass Account Usage:**
- User ID (emergency account used)
- Actual user identity (if captured)
- Date and time
- Duration of elevated access
- Reason for emergency access
- PHI accessed during emergency
- Approval/justification

**Example Log Entry:**
```
2024-01-15 11:30:05 | EMERGENCY_ACCESS | EmergencyAccount:breakglass-01 | ActualUser:dr.alee | Reason:PatientCrisis | MRN:456789 | Approver:supervisor.tmiller
```

#### 6. Data Transmission

**ePHI Sent:**
- User ID
- Date and time
- Patient identifier(s)
- Recipient
- Transmission method (email, fax, HL7, API)
- Encryption status
- Number of records

**ePHI Received:**
- Date and time
- Sender
- Patient identifier(s)
- Transmission method
- Encryption status
- Processing status

**Example Log Entry:**
```
2024-01-15 12:15:33 | PHI_TRANSMISSION | user.rnurse | MRN:123456 | Recipient:specialist@otherhospital.org | Method:SecureEmail | Encrypted:YES | Records:1
```

#### 7. System Events

**Backup Operations:**
- Date and time
- Backup type (full, incremental, differential)
- Systems/databases backed up
- Backup location
- Success/failure
- Verification status

**Restore Operations:**
- Date and time
- Administrator ID
- Data restored
- Source backup
- Destination
- Reason for restore

**Database Access:**
- User ID (database account)
- Date and time
- Database accessed
- Query executed (if feasible)
- Records affected
- Direct database access (outside application)

**Application Errors:**
- Date and time
- User ID (if applicable)
- Error type
- Error message
- Stack trace
- Affected functionality

**Example Log Entry:**
```
2024-01-15 02:00:00 | BACKUP_COMPLETE | Type:FULL | Database:EHR_PROD | Destination:OFFSITE_STORAGE | Status:SUCCESS | Size:2.3TB | Encrypted:YES
```

### What Should Be Logged (Best Practice)

Additional items beyond minimum requirements:

1. **Search/Query Activities**
   - Search parameters
   - Results returned
   - Time spent reviewing results

2. **Report Generation**
   - Report type
   - Parameters/filters
   - Number of patients included
   - Distribution

3. **Medication Orders**
   - Prescriber
   - Patient
   - Medication
   - Dosage
   - Changes to orders

4. **Clinical Decision Support Alerts**
   - Alert type
   - User response (accepted, overridden)
   - Override reason

5. **Interface/Integration Activity**
   - System-to-system data exchange
   - API calls
   - Data synchronization

## Audit Log Content Requirements

### Minimum Data Elements

Each audit log entry must include:

1. **Who:** User ID, entity, process
2. **What:** Action performed, data accessed/modified
3. **When:** Date and timestamp (with timezone)
4. **Where:** Workstation, IP address, location
5. **Why:** Reason/justification (where applicable)
6. **Result:** Success or failure

### Timestamp Requirements

**Precision:**
- Minimum: Date and time to the second
- Recommended: Millisecond precision
- Include timezone or use UTC

**Synchronization:**
- All systems synchronized to authoritative time source
- NTP (Network Time Protocol) recommended
- Regular time sync verification

**Format:**
- Consistent format across systems
- ISO 8601 recommended: YYYY-MM-DD HH:MM:SS
- Example: 2024-01-15 14:23:45.123 UTC

### Patient Identifier Requirements

**Must Include:**
- Medical Record Number (MRN) - primary identifier
- Patient name (where feasible and doesn't create excessive log size)
- Date of birth (where context requires disambiguation)

**Privacy Consideration:**
- Balance logging detail with log security
- Encrypt logs containing PHI
- Control access to audit logs

## Audit Log Security

### Protection Requirements

#### 1. Integrity (§164.312(c)(1))

**Tamper-Resistance:**
- Write-once, read-many (WORM) storage
- Digital signatures
- Cryptographic hashing
- Blockchain/distributed ledger (emerging)
- Immutable log storage

**Change Detection:**
- Hash verification
- Log file integrity monitoring
- Alert on tampering attempts

**Example Implementation:**
```
Each log entry cryptographically hashed
Hash of current entry includes hash of previous entry (chain)
Any modification breaks chain and triggers alert
```

#### 2. Confidentiality

**Encryption:**
- Encrypt logs containing PHI
- At rest: AES-256 minimum
- In transit: TLS 1.2+ when transmitting logs

**Access Control:**
- Strict role-based access to audit logs
- Separate from general system access
- Audit log access itself must be logged
- Minimum necessary principle

**Segregation of Duties:**
- System administrators should not have unmonitored access to audit logs
- Audit log review by security/compliance personnel
- Prevent log tampering by subjects of audits

#### 3. Availability

**Retention:**
- Minimum: 6 years (HIPAA requirement)
- State laws may require longer
- Consider litigation hold requirements

**Backup:**
- Regular backup of audit logs
- Off-site storage
- Separate from system backups
- Test restoration

**Storage Capacity:**
- Plan for log growth
- Automated archival to long-term storage
- Compression where appropriate (maintaining integrity)

## Audit Log Review Requirements

### Information System Activity Review (§164.308(a)(1)(ii)(D))

**Requirement:** Implement procedures to regularly review records of information system activity such as audit logs, access reports, and security incident tracking reports.

### Review Frequency

**Recommended Schedule:**

**Real-Time/Continuous:**
- Automated alerting for suspicious activity
- High-risk events (mass PHI downloads, unauthorized access attempts)
- Security incidents

**Daily:**
- Failed login attempts
- Emergency access use
- Administrative actions
- Security alerts

**Weekly:**
- User access patterns
- Permission changes
- Unusual activity trends

**Monthly:**
- Comprehensive access review
- User activity reports
- System configuration changes

**Quarterly:**
- In-depth audit log analysis
- Trend analysis
- Compliance verification
- Sample random record access

**Annually:**
- Complete audit log review
- Compliance assessment
- Policy and procedure update

### What to Look For

#### Red Flags/Suspicious Activity

1. **Inappropriate Access:**
   - Employee accessing own/family member records
   - VIP/celebrity patient record access
   - Neighbor/friend record access
   - Excessive record access unrelated to job duties
   - Access outside normal work hours/patterns

2. **Excessive Access:**
   - Unusually high volume of record access
   - Accessing large numbers of patients
   - Bulk data downloads
   - Sequential MRN access patterns

3. **Failed Access Attempts:**
   - Multiple failed login attempts
   - Attempts to access unauthorized records
   - Privilege escalation attempts
   - Repeated permission denied events

4. **Unusual Patterns:**
   - Access from unusual locations/IP addresses
   - Access at unusual times
   - Geographic impossibilities (access from multiple locations simultaneously)
   - Dormant account suddenly active

5. **Administrative Concerns:**
   - Unauthorized permission changes
   - Disabled security controls
   - Deleted or modified audit logs (attempted)
   - Emergency access without justification

### Review Documentation

**Must Document:**
- Date of review
- Reviewer identity
- Time period reviewed
- Systems/logs reviewed
- Findings
- Issues identified
- Follow-up actions
- Resolution

**Documentation Retention:** Minimum 6 years

### Automated Review Tools

**Recommended Capabilities:**

1. **SIEM (Security Information and Event Management)**
   - Centralized log aggregation
   - Real-time analysis
   - Automated alerting
   - Correlation across systems
   - Dashboards and reporting

2. **User Behavior Analytics (UBA)**
   - Baseline normal behavior
   - Detect anomalies
   - Risk scoring
   - Machine learning

3. **Automated Reporting**
   - Scheduled reports
   - Exception reports
   - Trend analysis
   - Compliance reports

4. **Alert Management**
   - Real-time alerting
   - Alert prioritization
   - Escalation workflows
   - Integration with incident response

## Common Audit Logging Mistakes

### 1. Insufficient Logging
- Not logging all ePHI access
- Missing critical events (deletes, exports)
- No logging of administrative actions
- Application-level access not logged

### 2. Excessive Logging
- Logging too much (performance impact)
- Redundant log entries
- Logging non-relevant events
- Unable to find important events in noise

### 3. Poor Log Security
- Logs not encrypted
- Inadequate access controls
- No integrity protection
- Logs accessible to wrong personnel

### 4. No Review Process
- Logs collected but never reviewed
- No automated alerting
- No investigation of suspicious activity
- No documentation of reviews

### 5. Inadequate Retention
- Logs deleted too soon
- No archival process
- Insufficient storage capacity
- Lost logs due to system failures

### 6. Incomplete Logs
- Missing required data elements
- No timestamps
- No patient identifiers
- No user identification

### 7. Inconsistent Logging
- Different log formats across systems
- Unsynchronized clocks
- Gaps in logging
- Inconsistent data elements

## Technical Implementation

### Log Storage Options

#### 1. Database Storage
**Pros:**
- Structured data
- Easy querying
- Good for analysis
- Relationship with operational data

**Cons:**
- Performance impact on production database
- Scalability challenges
- May require separate database

#### 2. File-Based Logs
**Pros:**
- Simple implementation
- Low overhead
- Standard tools available
- Easy to archive

**Cons:**
- Difficult to query
- Manual analysis challenging
- No structure enforcement
- Scaling issues

#### 3. Centralized Log Management
**Pros:**
- Aggregate from multiple systems
- Advanced analysis capabilities
- Long-term retention
- Security and compliance features

**Cons:**
- Additional infrastructure
- Cost
- Complexity
- Integration requirements

**Popular Solutions:**
- Splunk
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Graylog
- AWS CloudWatch Logs
- Azure Monitor Logs

### Log Format Standards

**Common Formats:**

1. **Syslog (RFC 5424)**
   - Standard protocol
   - Widely supported
   - Structured data

2. **JSON**
   - Structured
   - Human-readable
   - Easily parsed
   - Flexible schema

3. **CEF (Common Event Format)**
   - Security-focused
   - Standardized fields
   - SIEM integration

4. **Custom Format**
   - Application-specific
   - Optimized for use case
   - May require custom parsing

**Example JSON Log Entry:**
```json
{
  "timestamp": "2024-01-15T14:23:45.123Z",
  "event_type": "PHI_ACCESS",
  "user_id": "jsmith",
  "user_role": "Nurse",
  "action": "VIEW",
  "patient_mrn": "123456",
  "patient_name": "Doe, John",
  "record_type": "LabResults",
  "workstation": "workstation-42",
  "ip_address": "192.168.1.100",
  "session_id": "abc123def456",
  "result": "SUCCESS",
  "application": "EHR"
}
```

## Audit Logs for Specific Systems

### Electronic Health Records (EHR)
- All PHI access
- Clinical documentation
- Order entry and modifications
- Medication administration
- Clinical decision support interactions

### Laboratory Information Systems (LIS)
- Test orders
- Result entry and verification
- Result viewing
- Report generation
- Interface transactions

### Picture Archiving and Communication Systems (PACS)
- Image viewing
- Image uploads
- Study modifications
- Worklist access
- CD burning/export

### Billing Systems
- Claim creation/modification
- Payment posting
- Account access
- Report generation
- Insurance verification

### Patient Portals
- Patient login/logout
- Record viewing
- Message sending
- Appointment scheduling
- Document downloads

## Compliance Verification

### OCR Audit Protocol

OCR audits typically review:
1. Audit control implementation
2. Types of events logged
3. Log retention practices
4. Log review procedures
5. Documentation of reviews
6. Response to identified issues
7. Log security measures

### Self-Assessment Questions

- [ ] Are audit controls enabled on all systems containing ePHI?
- [ ] Are all required events being logged?
- [ ] Do logs contain all necessary data elements?
- [ ] Are logs protected from tampering?
- [ ] Are logs encrypted where they contain PHI?
- [ ] Is access to logs properly restricted?
- [ ] Are logs retained for at least 6 years?
- [ ] Are logs regularly reviewed?
- [ ] Is log review documented?
- [ ] Are issues identified in logs investigated?
- [ ] Is suspicious activity escalated appropriately?
- [ ] Are clocks synchronized across systems?
- [ ] Are logs backed up?
- [ ] Can historical logs be retrieved and reviewed?

## Best Practices

1. **Enable Comprehensive Logging**
   - Log all ePHI access and modifications
   - Include administrative actions
   - Capture security events
   - Don't rely solely on application logs

2. **Centralize Log Management**
   - Aggregate logs from all systems
   - Use SIEM or log management platform
   - Enable correlation and analysis
   - Simplify review process

3. **Implement Automated Monitoring**
   - Real-time alerting for high-risk events
   - Automated anomaly detection
   - Scheduled report generation
   - Reduce manual review burden

4. **Protect Log Integrity**
   - Use tamper-resistant storage
   - Implement strong access controls
   - Encrypt logs containing PHI
   - Regular integrity verification

5. **Regular Review and Analysis**
   - Establish review schedule
   - Document all reviews
   - Investigate anomalies
   - Track and resolve issues

6. **Retention and Archival**
   - Retain for minimum 6 years
   - Automated archival process
   - Verify archived logs readable
   - Plan for storage growth

7. **Integration with Incident Response**
   - Logs inform incident detection
   - Forensic analysis capabilities
   - Evidence preservation
   - Timeline reconstruction

8. **Training and Awareness**
   - Train staff that access is logged
   - Explain log review process
   - Communicate consequences
   - Deterrent effect of logging

## Regulatory Citations

- 45 CFR §164.312(b) - Audit controls
- 45 CFR §164.308(a)(1)(ii)(D) - Information system activity review
- 45 CFR §164.312(c)(1) - Integrity controls
- 45 CFR §164.316(b)(2)(i) - Time limit (6 year retention)

## Additional Resources

- NIST SP 800-92 - Guide to Computer Security Log Management
- NIST SP 800-53 - Security and Privacy Controls (AU family)
- HHS Audit Protocol
- CMS Security Risk Assessment Tool
