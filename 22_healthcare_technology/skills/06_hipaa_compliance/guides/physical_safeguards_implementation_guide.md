# Physical Safeguards Implementation Guide

## Overview

Physical safeguards are physical measures, policies, and procedures to protect electronic information systems, related buildings, and equipment from natural and environmental hazards and unauthorized intrusion.

**Regulatory Basis:** 45 CFR §164.310

## Implementation Components

### 1. Facility Access Controls (§164.310(a)(1)) - REQUIRED

#### 1.1 Contingency Operations (Addressable)

**Emergency Access Procedures:**

```
EMERGENCY FACILITY ACCESS PROCEDURE

Emergency Scenarios:
- Fire/evacuation
- Natural disaster
- Power outage
- After-hours patient emergency
- System failure requiring immediate access

Emergency Access Methods:
1. Break-glass key box (monitored location)
2. Emergency contact list (security, facilities)
3. Backup access codes
4. Facility manager on-call
5. Law enforcement escort (if needed)

Procedures:
1. Identify emergency requiring facility access
2. Contact security or facilities manager
3. Obtain emergency access authorization
4. Document access:
   - Date and time
   - Person accessing
   - Reason for emergency access
   - Authorization granted by
5. Restore normal access procedures
6. Review emergency access logs monthly

Emergency Contact List:
- Facilities Manager: [Name] [Phone]
- Security Director: [Name] [Phone]
- IT Director: [Name] [Phone]
- On-call Administrator: [Name] [Phone]
```

#### 1.2 Facility Security Plan (Addressable)

**Comprehensive Facility Security:**

**Perimeter Security:**
- Fencing around property (where applicable)
- Controlled entry points
- Security lighting (parking lots, entrances)
- Landscaping that doesn't provide hiding spots
- Surveillance cameras at all entrances

**Entry Point Controls:**
- Main entrance staffed during business hours
- After-hours access via badge/key only
- Visitor buzzer/intercom systems
- Mantrap/vestibule for high-security areas
- Server room separate from general access

**Access Control Systems:**
```
ACCESS CONTROL IMPLEMENTATION

Badge Access System:
- Proximity card readers
- Unique cards per individual
- Access levels programmed per area:
  * Public areas (reception, waiting room)
  * Clinical areas (exam rooms, nursing stations)
  * Restricted areas (server room, medical records)
  * High-security areas (pharmacy, executive offices)

Access Schedules:
- Staff: Access during work hours ±1 hour
- Cleaning crew: After-hours only, escorted
- Maintenance: Scheduled access, logged
- Executives: 24/7 access
- IT: 24/7 access to server room

Badge Management:
- Issued on hire date
- Returned on termination (immediately)
- Lost badge reported immediately
- Replacement badge process
- Temporary badges for visitors/vendors
- Badge expiration (annually renewed)
```

**Visitor Management:**
```
VISITOR MANAGEMENT PROCEDURE

Visitor Definition:
- Patients (scheduled appointments)
- Patient families/visitors
- Vendors
- Contractors
- Delivery personnel
- Auditors/regulators
- Job applicants

Visitor Process:
1. Check in at reception desk
2. Provide photo ID (for non-patients)
3. Complete visitor log:
   - Name
   - Company (if applicable)
   - Person visiting
   - Purpose of visit
   - Time in
   - Time out
4. Issue visitor badge (clearly marked)
5. Escort requirements:
   - Vendors in clinical areas: REQUIRED
   - Contractors: REQUIRED
   - Patient visitors in waiting areas: NOT REQUIRED
   - Patient visitors to patient rooms: NOT REQUIRED (unless behavioral health)
6. Return badge upon departure
7. Sign out in log

Vendor Access to Systems:
- Business Associate Agreement required
- Advance approval by IT and Security Official
- Escorted at all times
- Access logged in vendor access log
- System changes documented
```

**Surveillance Systems:**
- Cameras at all exterior doors
- Cameras in parking areas
- Cameras covering hallways to restricted areas
- Server room camera (24/7 recording)
- Retention: 90 days minimum
- Reviewed after incidents
- Controlled access to video footage

**Security Personnel:**
- Security guard at main entrance (larger facilities)
- After-hours security rounds
- Alarm monitoring
- Incident response

**Environmental Controls:**
- Fire suppression systems
- Temperature/humidity monitoring (server room)
- Water detection systems
- Smoke detectors
- Emergency power/UPS systems

**Deliverable:** Facility Security Plan document

#### 1.3 Access Control and Validation (Addressable)

**Access Validation Procedures:**

```
ACCESS VALIDATION PROCEDURE

New Access Requests:
1. Manager submits Facility Access Request Form
2. Specify areas needed and justification
3. Security Official approves
4. Facilities programs badge
5. Access tested and verified
6. Documentation retained

Quarterly Access Reviews:
1. Generate access report by individual
2. Managers review team access
3. Verify continued need
4. Request removal of unnecessary access
5. Document recertification
6. Make approved changes
7. Retain documentation

Access Testing:
- Badge readers tested monthly
- Failed reader repaired within 24 hours
- Backup access procedures if reader fails

Access Logs:
- Electronic logs from badge system
- Review monthly for anomalies
- Investigate after-hours access
- Document reviews
```

**Deliverable:** Access validation procedures

#### 1.4 Maintenance Records (Addressable)

**Maintenance Documentation:**

```
MAINTENANCE LOG

For All Physical Security Components:
- Access control systems
- Surveillance cameras
- Locks and keys
- Alarm systems
- Environmental controls
- Fire suppression

Log Entry Requirements:
- Date of maintenance
- Type of maintenance (repair, upgrade, testing)
- Component serviced
- Vendor/person performing work
- Work performed
- Parts replaced
- Vendor access to systems (Yes/No)
- Supervised by (staff member name)
- Next maintenance due date

Hardware Disposal Records:
- Asset tag number
- Type of device
- Contained ePHI (Yes/No)
- Disposal method:
  * Hard drive destruction (certificate required)
  * Degaussing
  * Shredding
  * Incineration
- Date of disposal
- Disposal vendor
- Certificate of destruction retained

Key/Badge Management:
- Key/badge issuance log
- Key/badge return log
- Lost key/badge reports
- Lock rekeying log
```

**Deliverable:** Maintenance record system

### 2. Workstation Use (§164.310(b)) - REQUIRED

**Workstation Use Policy:**

```
WORKSTATION USE POLICY

Scope: All workstations accessing ePHI

Proper Workstation Functions:
- Clinical documentation
- Patient scheduling
- Billing and claims
- Email communications (work-related)
- Practice management tasks
- Approved web-based applications

Prohibited Uses:
- Personal email (non-work)
- Social media (unless job-related)
- Online shopping
- Gaming or entertainment
- Downloading unauthorized software
- Accessing inappropriate content
- Storing personal files
- Using for non-work purposes

Physical Environment:

Workstation Positioning:
- Face workstation away from public view
- Position to prevent screen viewing by unauthorized persons
- Not visible from windows
- Not accessible to patients/visitors

Privacy Screens:
- Required for workstations in public areas
- Required for laptops in public spaces
- Limits viewing angle

Clear Screen/Clear Desk:
- Lock workstation when leaving (Windows+L)
- Never leave workstation unlocked and unattended
- Remove/file documents with PHI when not in use
- No sticky notes with passwords
- Secure PHI documents at end of day

Auto-Lock Settings:
- Screen saver with password: 5 minutes of inactivity
- Automatic logoff: 15 minutes of inactivity
- Cannot be disabled by users

Mobile Workstations (Carts, Laptops):
- Cable lock when in patient rooms
- Stored in secure area when not in use
- Never left in vehicles
- Full disk encryption required

Personal Devices:
- Not permitted to access ePHI unless:
  * Approved BYOD program
  * Mobile Device Management (MDM) enrolled
  * Full device encryption
  * Remote wipe capability
  * User agreement signed

Monitoring:
- Managers conduct workstation audits monthly
- Check for policy compliance
- Observe workstation positioning
- Verify automatic logoff functioning
- Document audits

Violations:
- Sanction policy applies
- Coaching for first minor violation
- Progressive discipline for repeated violations
```

**Deliverable:** Workstation Use Policy and audit checklist

### 3. Workstation Security (§164.310(c)) - REQUIRED

**Physical Workstation Safeguards:**

```
WORKSTATION SECURITY STANDARDS

Desktop Computers:
- Located in secure areas (not accessible to public)
- Cable locks for equipment in semi-public areas
- Locked offices or locked cabinets (after hours)
- Power cables secured to prevent accidental disconnect
- No food or drinks near computers

Laptops:
- Cable lock when in use in public areas
- Stored in locked drawer/cabinet when not in use
- Never left in vehicles
- Asset tag and inventory tracking
- Full disk encryption (required)

Mobile Devices (Tablets, Smartphones):
- Personal PIN/password required
- Auto-lock after 2 minutes
- Full device encryption
- Remote wipe capability enabled
- Mobile Device Management (MDM) enrolled
- Never left unattended

Workstation on Wheels (WOWs):
- Cable lock when in patient rooms
- Parked in locked storage area overnight
- Battery checked daily
- Asset tracking
- Quarterly inventory verification

Physical Security Measures:

Facility-Level:
- Alarm system armed after hours
- Security cameras in hallways
- Badge access to clinical areas
- Visitor escort requirements

Office-Level:
- Lockable doors for offices with workstations
- Lock offices when unoccupied
- Window coverings for ground-floor offices
- Secure storage for portable devices

Workstation-Level:
- Cable locks for laptops and monitors
- Locked cabinets for portable devices
- Privacy screens in public areas
- USB port locks (if required by policy)

Theft Prevention:
- Asset tags on all equipment
- Serial number inventory
- Video surveillance in equipment areas
- Theft reporting procedures
- Law enforcement notification

Theft Response Procedure:
1. Report theft immediately to security/management
2. Notify law enforcement
3. Notify Security Official
4. Remote wipe device if capable
5. Disable all accounts/access
6. Change any shared passwords
7. Conduct breach risk assessment
8. Document incident
9. Notification if required
```

**Deliverable:** Workstation Security Policy and procedures

### 4. Device and Media Controls (§164.310(d))

#### 4.1 Disposal (Required)

**ePHI Disposal Procedures:**

```
SECURE DISPOSAL POLICY

Paper Records with PHI:

Shredding Requirements:
- Cross-cut shredder (minimum)
- Micro-cut for highly sensitive (recommended)
- Shred bins in secure areas
- Locked shred bins
- Shredding vendor with BAA
- Certificate of destruction for large volumes

Shredding Process:
1. Identify documents containing PHI for disposal
2. Remove staples/binder clips (if required by shredder)
3. Place in designated locked shred bin
4. Regular shredding schedule (at least weekly)
5. Supervise vendor shredding (or use locked console)
6. Obtain certificate of destruction
7. Retain certificate for 6 years

Electronic Media:

Hard Drives/SSDs:
- Remove from computers being disposed
- Degauss magnetic drives (HDDs)
- Physical destruction:
  * Drill through platters (minimum 3 holes)
  * Shred/disintegrate
  * Incinerate
- SSDs require physical destruction or crypto-erase
- Use NIST SP 800-88 compliant methods
- Obtain certificate of destruction
- Document disposal in asset management system

USB Drives/Removable Media:
- Physical destruction (shred, incinerate)
- Never donate or sell
- Track all removable media
- Disposal log maintained

CDs/DVDs:
- Shred using media shredder
- If no shredder: break/destroy beyond recovery
- Never throw away intact

Smartphones/Tablets:
- Factory reset (insufficient alone)
- Remove SIM card and destroy
- Physical destruction if contained ePHI
- Or certified data wiping service

Printers/Copiers:
- Remove and destroy hard drives
- Use vendor service with BAA
- Certificate of hard drive destruction

Backup Tapes:
- Degauss or physically destroy
- Cannot be reused after ePHI stored
- Disposal log

Fax Machines:
- Remove and destroy memory chips
- Physical destruction

Disposal Vendor Requirements:
- Business Associate Agreement required
- Bonded and insured
- NAID AAA Certification (preferred)
- On-site destruction available (for high-security)
- Certificates of destruction provided
- Periodic vendor audits
```

**Deliverable:** Disposal Policy and certificate tracking

#### 4.2 Media Re-use (Required)

**Media Sanitization for Re-use:**

```
MEDIA RE-USE POLICY

Before Re-using Media That Contained ePHI:

Hard Drives (HDD):
- Overwrite entire drive (minimum 3 passes)
- Use DoD 5220.22-M standard or equivalent
- Verify successful wipe
- Document sanitization

Solid State Drives (SSD):
- Crypto-erase (if hardware supports)
- Secure erase command
- Or physical destruction (cannot reliably overwrite)

USB Drives:
- Format and overwrite
- Or dedicated use (never leave facility)

Optical Media (CD/DVD):
- Cannot be reliably sanitized
- Must be destroyed if contained ePHI
- Use write-once media for backups

Computers/Laptops:
- Wipe hard drive before re-assignment
- Re-image operating system
- Verify ePHI removed
- Document sanitization in asset log

Smartphones/Tablets:
- Factory reset with encryption
- Verify device encrypted before reset
- Re-enrollment in MDM
- Test to ensure ePHI inaccessible

Encryption-Based Sanitization:
- If device/media was encrypted
- Destroy encryption keys
- Data becomes unrecoverable
- Fastest method for large volumes
- Document key destruction

Tools:
- DBAN (Darik's Boot and Nuke) - free
- Blancco - commercial
- Manufacturer secure erase utilities
- Document tool used and results

Documentation:
- Asset tag
- Date sanitized
- Method used
- Person performing
- Verification completed
- Re-assignment details
```

**Deliverable:** Media re-use procedures

#### 4.3 Accountability (Addressable)

**Hardware and Media Tracking:**

```
ACCOUNTABILITY SYSTEM

Asset Inventory:
- All hardware receiving asset tags upon receipt
- Asset management database
- Annual physical inventory verification

Inventory Data Elements:
- Asset tag number
- Serial number
- Type of device
- Make and model
- Location (building, room)
- Assigned to (user or department)
- Contains/accesses ePHI (Yes/No)
- Encryption status
- Purchase date
- Warranty expiration
- Disposal/retirement date

Check-Out/Check-In System:

For Portable Devices:
- Laptop/tablet checkout log
- Removable media checkout log
- Temporary device loans documented
- Expected return date
- Actual return date
- Condition upon return

Chain of Custody:

For Media Leaving Facility:
- Backup tapes to off-site storage
- Devices for repair
- Media for destruction
- Documentation includes:
  * Date/time removed
  * Person taking custody
  * Destination
  * Transport method
  * Return date (if applicable)
  * Disposal confirmation (if applicable)

Movement Tracking:
- Asset transfers between locations
- Asset re-assignments
- Update inventory in real-time
- Manager approval for transfers

Reconciliation:
- Quarterly physical inventory spot checks
- Annual comprehensive inventory
- Investigate discrepancies
- Report missing assets
- Update disposal records
```

**Deliverable:** Asset management system and procedures

#### 4.4 Data Backup and Storage (Addressable)

**Backup Procedures Before Equipment Movement:**

```
BACKUP BEFORE MOVEMENT POLICY

Scenarios Requiring Backup:

Equipment Relocation:
- Moving to new facility
- Office reconfigurations
- Temporary relocations

Equipment Maintenance:
- Sending for repair
- Warranty service
- Upgrade installations

Equipment Disposal:
- Retirement of systems
- Hardware refresh projects
- End of useful life

Procedures:

1. Before Movement:
- Perform full backup of device
- Verify backup successful
- Test restore (sample files)
- Document backup date and method
- Encrypt backup media
- Securely store backup

2. During Movement:
- Use secure transport
- Maintain chain of custody
- Escort if containing ePHI
- Insurance for valuable equipment

3. After Movement:
- Verify equipment operational
- Test ePHI accessibility
- Document successful movement
- Retain backup for 30 days minimum

Backup Storage:
- Encrypted backups required
- Secure storage location
- Off-site for critical systems
- Access controls on backup media
- Backup retention per policy
```

**Deliverable:** Equipment movement procedures

## Physical Security Assessment Checklist

### Facility Access
- [ ] Controlled entry points
- [ ] Badge access system functional
- [ ] Visitor management process
- [ ] Security cameras operational
- [ ] After-hours access restricted
- [ ] Server room separately secured
- [ ] Environmental controls functioning
- [ ] Emergency access procedures documented

### Workstations
- [ ] Positioned away from public view
- [ ] Privacy screens where needed
- [ ] Auto-lock configured (≤15 min)
- [ ] Cable locks on laptops
- [ ] Clear desk policy enforced
- [ ] Personal device policy compliant

### Devices
- [ ] Asset inventory current
- [ ] Mobile devices encrypted
- [ ] Remote wipe enabled
- [ ] Device checkout log maintained
- [ ] Disposal procedures followed
- [ ] Certificates of destruction retained

### Physical Security
- [ ] Doors locked after hours
- [ ] Alarm system functional
- [ ] Keys/badges tracked
- [ ] Shred bins available and locked
- [ ] Equipment storage secured
- [ ] Backup media secured off-site

## Common Physical Security Mistakes

1. **Workstations visible to public**
   - Fix: Reposition or add privacy screens

2. **No automatic screen lock**
   - Fix: Configure via Group Policy

3. **Improper disposal of PHI**
   - Fix: Implement shredding program with BAA

4. **Lost/stolen devices not encrypted**
   - Fix: Full disk encryption on all mobile devices

5. **No visitor management**
   - Fix: Implement sign-in log and escort procedures

6. **Unrestricted facility access**
   - Fix: Badge access system with access levels

7. **No asset tracking**
   - Fix: Asset tagging and inventory system

8. **Workstations left unlocked**
   - Fix: Training and automatic logoff

## Implementation Timeline

**Month 1:**
- Assess current physical security
- Identify gaps
- Develop implementation plan

**Month 2-3:**
- Implement facility access controls
- Deploy badge system (if needed)
- Establish visitor management

**Month 4-5:**
- Deploy workstation security measures
- Implement disposal procedures
- Create asset management system

**Month 6:**
- Train workforce
- Conduct physical security audit
- Document all procedures

## Documentation Requirements

- [ ] Facility Security Plan
- [ ] Visitor logs
- [ ] Access logs
- [ ] Workstation Use Policy
- [ ] Disposal Policy
- [ ] Certificates of destruction
- [ ] Media re-use logs
- [ ] Asset inventory
- [ ] Maintenance logs
- [ ] Physical security assessment reports

## Regulatory Citations

45 CFR §164.310 - Physical Safeguards

## Conclusion

Physical safeguards are essential to protect ePHI from unauthorized physical access, theft, and environmental hazards. Regular assessments and workforce training ensure ongoing compliance.
