# Data Collection Best Practices Guide

## Overview

Data collection is a critical phase in e-discovery that sets the foundation for all downstream activities. Proper collection ensures data integrity, preserves metadata, maintains chain of custody, and withstands legal scrutiny. This guide provides comprehensive best practices for collecting ESI in various scenarios.

## Collection Planning

### Pre-Collection Assessment

**Data Source Inventory**:
- Email systems (Exchange, Gmail, Office 365, Lotus Notes)
- File shares and personal drives
- Cloud storage (OneDrive, Dropbox, Box, SharePoint)
- Mobile devices (smartphones, tablets)
- Collaboration tools (Slack, Teams, Zoom)
- Databases and business applications
- Social media and web-based accounts
- Backup tapes and archives

**Custodian Identification**:
- Key decision-makers
- Subject matter experts
- Direct participants in events
- Support staff with relevant knowledge
- IT personnel for system data

**Volume Estimation**:
```
Custodian         Email (GB)    Files (GB)    Total (GB)
--------------------------------------------------------
CEO               50            20            70
CFO               40            15            55
Project Manager   30            100           130
Engineer 1        25            80            105
Engineer 2        25            75            100
--------------------------------------------------------
Total                                         460 GB
```

### Collection Methodology Selection

**Decision Matrix**:

| Scenario | Method | Pros | Cons |
|----------|--------|------|------|
| Suspected spoliation | Forensic imaging | Highest defensibility, deleted file recovery | Expensive, slow, disruptive |
| Standard litigation | Logical collection | Cost-effective, fast, good metadata | Less forensic detail |
| Remote workers | Remote collection tools | No travel, non-disruptive | Requires network access |
| Simple matters | Self-collection | Lowest cost, fastest | Lower defensibility, user error risk |

## Forensic Collection

### When to Use Forensic Collection

**Appropriate Scenarios**:
- Suspected data destruction or spoliation
- Criminal matters or serious misconduct
- Need for deleted file recovery
- System-level analysis required
- Opposing party demands forensic collection
- Court order specifies forensic methods

**Forensic Imaging Process**:

1. **Preparation**:
   - Legal authorization (consent or court order)
   - Coordinate with custodian and IT
   - Prepare forensic workstation
   - Gather write-blocking hardware
   - Plan logistics and timing

2. **Imaging**:
   - Write-blocker to prevent alterations
   - Bit-by-bit copy of entire drive
   - Create forensic image (E01, DD, L01, AFF format)
   - Calculate hash values (MD5, SHA-256)
   - Document imaging process

3. **Verification**:
   - Verify hash values match
   - Spot-check random files
   - Ensure image is accessible
   - Document completion

4. **Chain of Custody**:
   - Sign custody forms
   - Document who handled device
   - Record all transfers
   - Secure storage

**Forensic Image Formats**:

**E01 (EnCase)**:
- Industry standard
- Compression and error detection
- Metadata and case information embedded
- Widely supported

**DD (Raw Image)**:
- Simple bit-for-bit copy
- No compression
- Large file sizes
- Universal compatibility

**L01 (Logical Evidence File)**:
- Logical copy with forensic features
- Smaller than physical images
- Faster processing

### Forensic Collection Tools

**Commercial Tools**:
- EnCase Forensic Imager
- FTK Imager (Free)
- X-Ways Forensics
- Cellebrite (for mobile devices)

**Open Source**:
- dd (Linux/Mac)
- dc3dd (enhanced dd)
- Guymager (Linux GUI)

## Logical Collection

### Email Collection

**Exchange Server**:

**Methods**:
- PowerShell Export (New-MailboxExportRequest)
- Third-party tools (Quest, Proofpoint)
- Office 365 eDiscovery export
- Direct PST export from Outlook

**Best Practices**:
- Collect in native PST/MSG format when possible
- Preserve all metadata (headers, timestamps, recipients)
- Include sent items and deleted items folders
- Document folder structure
- Calculate hash values for each PST

**Example PowerShell Export**:
```powershell
New-MailboxExportRequest -Mailbox john.smith@company.com `
  -FilePath \\server\share\smith_export.pst `
  -ContentFilter {(Received -ge '01/01/2020') -and (Received -le '12/31/2023')}
```

**Gmail/Google Workspace**:

**Methods**:
- Google Vault export
- Google Takeout
- Third-party collection tools (Onna, Zapproved)
- API-based collection

**Considerations**:
- MBOX format typical
- May require conversion to PST
- Labels vs. folders differ from traditional email
- Threaded conversations need special handling

**Office 365**:

**Methods**:
- Security & Compliance Center eDiscovery
- PowerShell ContentSearch and export
- Third-party tools

**Example Content Search**:
```powershell
New-ComplianceSearch -Name "Smith Collection" `
  -ExchangeLocation john.smith@company.com `
  -ContentMatchQuery "(date>=2020-01-01) AND (date<=2023-12-31)"

Start-ComplianceSearch -Identity "Smith Collection"
New-ComplianceSearchAction -SearchName "Smith Collection" -Export
```

### File Share Collection

**Approaches**:

**Direct Copy**:
```bash
robocopy "\\fileserver\users\jsmith" "E:\Collections\Smith" /E /COPYALL /R:3 /W:5
```
- Preserves timestamps and permissions
- Fast for local collections
- Maintains folder structure

**Forensic Tools**:
- FTK Imager for logical acquisition
- EnCase for selective collection
- X-Ways for file system collection

**Cloud Storage**:
- Platform-specific APIs
- Download via sync clients (preserves some metadata)
- Third-party collection tools (Onna, CloudNine)

**Metadata Preservation**:
- Capture created, modified, accessed dates
- File path and location
- File size and hash
- Permissions and ownership
- Version history (if available)

### Mobile Device Collection

**iOS Devices**:

**Tools**:
- Cellebrite UFED
- Oxygen Forensics
- Magnet AXIOM
- iTunes backup extraction

**Methods**:
- Physical extraction (requires jailbreak, rarely used)
- Logical extraction (via backup)
- File system extraction
- Cloud extraction (iCloud)

**Challenges**:
- Encryption
- App sandboxing
- Frequent OS updates
- Two-factor authentication

**Android Devices**:

**Tools**:
- Cellebrite
- Oxygen Forensics
- ADB (Android Debug Bridge)

**Methods**:
- Physical extraction
- Logical extraction
- File system extraction
- App-specific extraction

**Considerations**:
- Device must be unlocked
- Developer mode may be required
- Manufacturer-specific challenges
- Varied Android versions

**Best Practices**:
- Put device in airplane mode immediately
- Document device state
- Photograph lock screen and home screen
- Use certified forensic tools
- Preserve original device as evidence

### Cloud and SaaS Collection

**Collaboration Platforms**:

**Slack**:
- Export via Slack Admin (Enterprise Grid only)
- eDiscovery API for legal hold and export
- Third-party tools (Hanzo, Zapproved)
- Preserves threads, reactions, files

**Microsoft Teams**:
- Security & Compliance Center
- Same methods as Office 365
- Includes chat, channel messages, files

**Zoom**:
- Admin portal for recordings and transcripts
- API for meeting metadata
- No native participant chat export (need third-party)

**Cloud Storage** (Dropbox, Box, Google Drive):
- Admin console exports
- API-based collection
- Third-party collection tools
- Preserve file versions, sharing metadata

## Remote Collection

### Remote Collection Tools

**Commercial Solutions**:
- Exterro Remote Collection
- Zapproved Remote Collect
- Nuix Collect
- Relativity Collect

**Process**:
1. Deploy collection agent to custodian's computer
2. Agent inventories data sources
3. Custodian or IT approves collection scope
4. Agent collects data in background
5. Data encrypted and transferred to collection server
6. Generate collection reports and chain of custody

**Advantages**:
- No travel required
- Less disruptive to custodian
- Can schedule during off-hours
- Built-in encryption and security
- Automated documentation

**Challenges**:
- Requires network connectivity
- May need IT assistance for installation
- Bandwidth limitations
- Firewall and security restrictions

### Self-Collection

**When Appropriate**:
- Low-stakes matters
- Trusted custodians
- Cost constraints
- Small data volumes

**Self-Collection Instructions Template**:
```
SELF-COLLECTION INSTRUCTIONS

Matter: Acme Corp. v. Widget Inc.
Custodian: John Smith
Date Range: January 1, 2020 - December 31, 2023

WHAT TO COLLECT:
1. Email from your company email account (john.smith@acme.com)
2. Files from your computer Documents folder
3. Files from shared network drives related to Widget project

HOW TO COLLECT:

EMAIL:
1. Open Outlook
2. Select File > Open & Export > Import/Export
3. Choose "Export to a file" > "Outlook Data File (.pst)"
4. Select your email account
5. Include subfolders
6. Save file as: Smith_Email_[DATE].pst to provided USB drive

FILES:
1. Locate Documents folder (C:\Users\jsmith\Documents)
2. Copy entire Documents folder to USB drive
3. Locate Widget project files on network (\\fileserver\Projects\Widget)
4. Copy Widget folder to USB drive

IMPORTANT:
- Do NOT delete any emails or files
- Do NOT modify any files
- Include DELETED ITEMS folder
- Contact [E-Discovery Coordinator] with questions
- Return USB drive by [DATE]

Custodian Certification:
I certify that I have collected the requested materials according to these
instructions and have not deleted, altered, or withheld any responsive materials.

_______________________________  __________
Custodian Signature              Date
```

**Quality Control for Self-Collection**:
- Clear, simple instructions
- IT support available for questions
- Verification of collection completeness
- Hash calculations
- Spot-check for common errors

## Collection Challenges and Solutions

### Challenge: Encrypted Files/Devices

**Solutions**:
- Obtain passwords from custodians
- Coordinate with IT for system passwords
- Use password recovery tools (with authorization)
- Document inability to access if passwords unavailable
- Notify requesting party

### Challenge: Large Data Volumes

**Solutions**:
- Targeted collection (date ranges, file types, keywords)
- Incremental collection over time
- High-speed network transfer
- Ship hard drives if network insufficient
- Cloud-based collection platforms

### Challenge: Legacy Systems

**Solutions**:
- Identify system requirements and dependencies
- Virtual machine to run legacy applications
- Engage former employees or vendors for access
- Export to standard formats if possible
- Screen capture or manual documentation if extraction impossible

### Challenge: Custodian Left Company

**Solutions**:
- IT-based collection from deactivated accounts
- Backup tape restoration if data purged
- Forward to personal email (if consent and appropriate)
- Collect from device if still available
- Document gaps in collection

### Challenge: Data in Foreign Jurisdictions

**Solutions**:
- Assess data privacy laws (GDPR, local laws)
- Data transfer agreements
- Local counsel consultation
- In-country processing if required
- Document legal restrictions

## Collection Documentation

### Collection Report Template

```
COLLECTION REPORT

Matter: Acme Corp. v. Widget Inc.
Collection Date: [Date]
Custodian: John Smith
Collected By: [Technician Name]

DATA SOURCES COLLECTED:
1. Email: john.smith@acme.com
   - Server: exchange.acme.com
   - Date Range: 01/01/2020 - 12/31/2023
   - Collection Method: PowerShell Export
   - File: Smith_Email.pst (45.3 GB)
   - MD5 Hash: 5d41402abc4b2a76b9719d911017c592

2. Desktop Files: C:\Users\jsmith\
   - Collection Method: FTK Imager Logical Copy
   - File: Smith_Desktop.zip (12.7 GB)
   - SHA-256 Hash: [hash value]

3. Network Shares: \\fileserver\Projects\Widget
   - Collection Method: Robocopy
   - File: Smith_Network.zip (8.2 GB)
   - MD5 Hash: [hash value]

COLLECTION SUMMARY:
Total Data Collected: 66.2 GB
Files Collected: ~125,000
Collection Duration: 4 hours
Exceptions: None

COLLECTION NOTES:
- Custodian cooperative and present during collection
- No encrypted or password-protected files encountered
- Deleted items folder included in email export
- Network share collection limited to Widget project folder per scope

CERTIFICATIONS:
Collected using forensically sound methods
Write-blocking used where appropriate
Hash values calculated and verified
Chain of custody maintained

_______________________________  __________
Technician Signature             Date

_______________________________  __________
Custodian Acknowledgment         Date
```

### Chain of Custody Form

```
CHAIN OF CUSTODY

Matter: Acme Corp. v. Widget Inc.
Evidence ID: ACME-SMITH-001
Description: Email and files for John Smith

INITIAL COLLECTION:
Collected From: John Smith
Collection Date: [Date]
Collected By: [Technician]
Method: Remote collection tool
Location: Acme Corp HQ, Conference Room B

TRANSFERS:
1. From: [Technician] To: [E-Discovery Coordinator] Date: [Date] Reason: Transfer to processing
   Signature: ________________

2. From: [E-Discovery Coordinator] To: [Vendor] Date: [Date] Reason: Processing and hosting
   Signature: ________________

STORAGE LOCATIONS:
- Original: Secure server at Acme Corp (\\evidence-server\litigation\)
- Copy: Processing vendor encrypted storage
- Backup: Encrypted external drive in evidence locker

DISPOSITION:
Data will be retained until matter resolution + 7 years per retention policy
```

## Best Practices Summary

**Planning**:
1. Identify all relevant data sources
2. Choose appropriate collection method
3. Obtain necessary access and permissions
4. Schedule collections to minimize disruption
5. Prepare collection tools and media

**Execution**:
1. Use certified forensic tools when appropriate
2. Preserve metadata and file attributes
3. Calculate hash values for integrity
4. Document collection process thoroughly
5. Maintain strict chain of custody

**Verification**:
1. Verify hash values
2. Spot-check collected data
3. Ensure completeness
4. Validate metadata preservation
5. Document exceptions

**Documentation**:
1. Collection reports for each custodian
2. Chain of custody forms
3. Technical specifications (tools, settings)
4. Exception reports
5. Custodian certifications

**Security**:
1. Encrypt data in transit and at rest
2. Secure physical media
3. Limit access to collected data
4. Track all data movements
5. Proper disposal when authorized

## Conclusion

Proper data collection is foundational to defensible e-discovery. By following these best practices, using appropriate tools and methodologies, and maintaining rigorous documentation, organizations can ensure collected ESI withstands scrutiny and provides a solid foundation for downstream processing, review, and production.
