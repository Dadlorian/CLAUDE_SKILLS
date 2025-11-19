# E-Discovery Metadata Fields Reference

## Overview

Metadata is "data about data" - information describing the characteristics, context, and properties of electronic documents. In e-discovery, metadata is critical for understanding document authenticity, chronology, relationships, and relevance. Proper extraction, preservation, and production of metadata is essential for defensible e-discovery.

## Types of Metadata

### 1. System Metadata

**Definition**: Metadata created and maintained by computer systems and operating systems.

**Key Fields**:
- **File Name**: Original name of the file
- **File Extension**: File type indicator (.docx, .pdf, .msg)
- **File Path**: Location in file system
- **File Size**: Size in bytes/KB/MB
- **Created Date**: When file was created
- **Modified Date**: When file was last changed
- **Accessed Date**: When file was last opened (unreliable)
- **MD5 Hash**: File fingerprint for de-duplication
- **SHA-256 Hash**: More secure file fingerprint

**Sources**:
- Operating system file tables
- File system metadata
- Directory structures

**Considerations**:
- Can change when file is copied or moved
- Timestamps may reflect copies, not originals
- File system differences (NTFS, FAT32, HFS+, ext4)

### 2. Application Metadata

**Definition**: Metadata embedded in documents by applications (Microsoft Word, Excel, Adobe PDF).

**Key Fields**:
- **Author**: Document creator
- **Title**: Document title
- **Subject**: Document subject/description
- **Keywords/Tags**: Searchable tags
- **Comments**: Document comments
- **Created Date**: When document was created
- **Modified Date**: Last modification date
- **Last Modified By**: User who last modified
- **Revision Number**: Version number
- **Company**: Organization name
- **Manager**: Manager name
- **Template**: Template used
- **Total Edit Time**: Time spent editing
- **Page Count**: Number of pages
- **Word Count**: Number of words
- **Hidden Text**: Track changes, comments, hidden content

**Sources**:
- Document properties (Office, PDF)
- Embedded within file structure
- Application-specific fields

**Extraction Tools**:
- Native application APIs
- Metadata extraction libraries
- Processing tools (Nuix, Relativity)

### 3. Email Metadata

**Definition**: Metadata specific to email messages and communication.

**Key Fields**:

**Header Information**:
- **From**: Sender email address
- **To**: Primary recipient(s)
- **CC**: Carbon copy recipient(s)
- **BCC**: Blind carbon copy recipient(s)
- **Subject**: Email subject line
- **Date Sent**: When email was sent
- **Date Received**: When email was received
- **Message ID**: Unique message identifier
- **Conversation ID**: Thread identifier
- **Importance**: Priority flag (High, Normal, Low)

**Routing Information**:
- **SMTP Headers**: Email routing path
- **Received Headers**: Servers that handled email
- **Return-Path**: Bounce address
- **Reply-To**: Reply address (if different from sender)

**Attachment Information**:
- **Attachment Names**: Names of attached files
- **Attachment Count**: Number of attachments
- **Attachment Sizes**: Size of each attachment
- **Attachment Types**: File types attached

**Conversation Metadata**:
- **Thread ID**: Email conversation identifier
- **In-Reply-To**: Message this is replying to
- **References**: Chain of related messages

**Sources**:
- Email headers (SMTP)
- Email client metadata (Outlook, Gmail)
- Exchange server information

### 4. Embedded Metadata (Hidden Data)

**Definition**: Metadata not immediately visible to users but embedded in documents.

**Types**:
- **Track Changes**: Editing history in Word documents
- **Comments**: Reviewer comments and annotations
- **Hidden Text**: Hidden paragraphs or sections
- **Revision History**: Prior versions within document
- **Notes**: Speaker notes in PowerPoint
- **Form Field Data**: Hidden form responses
- **Custom XML**: Embedded XML data
- **Macros**: Embedded VBA or scripts
- **External Links**: Links to other documents
- **Deleted Cells**: Deleted but recoverable Excel cells

**Risks**:
- May contain privileged or confidential information
- Can reveal attorney work product
- May contradict document content
- Can reveal drafting process and authors

**Extraction Methods**:
- Specialized tools (Metadata Assistant)
- Processing software
- Manual inspection
- Scripting (Python, PowerShell)

**Scrubbing Considerations**:
- Remove before production if sensitive
- Document scrubbing methodology
- Validate complete removal
- Consider privilege implications

## Common Metadata Field Catalog

### Document Control Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| DOCID | Unique document identifier | ACME00001 |
| BEGDOC | Beginning Bates number | ACME00001 |
| ENDDOC | Ending Bates number (ranges) | ACME00005 |
| BEGATTACH | Parent document for attachments | ACME00001 |
| ENDATTACH | Ending parent document | ACME00001 |
| PAGECOUNT | Number of pages | 5 |
| DOCDATE | Document date (calculated) | 01/15/2024 |
| VOLUME | Production volume | VOL001 |

### File System Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| FILENAME | Original file name | Meeting_Notes.docx |
| FILEEXT | File extension | .docx |
| FILEPATH | Original file path | C:\Users\JSmith\Documents\ |
| FILESIZE | File size in bytes | 45678 |
| MD5HASH | MD5 checksum | 5d41402abc4b2a76b9719d911017c592 |
| SHA256HASH | SHA-256 checksum | [64-character hex string] |
| CUSTODIAN | Data custodian | Smith, John |
| DATASOURCE | Source of data | John_Smith_Desktop |
| COLLECTIONDATE | When collected | 01/10/2024 |

### Document Property Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| AUTHOR | Document author | John Smith |
| TITLE | Document title | Q4 Financial Analysis |
| SUBJECT | Document subject | Budget Review |
| COMPANY | Company name | Acme Corporation |
| DATECREATED | Creation date | 01/15/2024 10:30 AM |
| DATEMODIFIED | Last modified date | 01/16/2024 2:45 PM |
| LASTMODIFIEDBY | Last user to modify | Jane Doe |
| KEYWORDS | Document keywords | budget, finance, Q4 |
| COMMENTS | Document comments | For executive review |
| MANAGER | Manager name | Robert Johnson |
| CATEGORY | Document category | Financial |
| DOCTYPE | Document type | Microsoft Word |

### Email-Specific Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| FROM | Email sender | john.smith@acme.com |
| TO | Primary recipients | jane.doe@acme.com; bob.jones@acme.com |
| CC | Carbon copy recipients | legal@acme.com |
| BCC | Blind carbon copy | compliance@acme.com |
| SUBJECT | Email subject | RE: Budget Meeting |
| DATESENT | Date/time sent | 01/15/2024 3:45 PM |
| DATERECEIVED | Date/time received | 01/15/2024 3:46 PM |
| MESSAGEID | Unique message ID | <abc123@mail.acme.com> |
| IMPORTANCE | Priority flag | High |
| THREADID | Conversation thread ID | THREAD_12345 |
| HASATTACH | Has attachments flag | Yes |
| ATTACHCOUNT | Number of attachments | 3 |
| ATTACHNAMES | Attachment file names | report.pdf; data.xlsx; chart.png |

### Processing Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| DUPLICATE | Duplicate status | Duplicate |
| DUPLICATEOF | Original document ID | ACME00001 |
| NEARDUPLICATEOF | Near-duplicate parent | ACME00125 |
| SIMILARITY | Similarity percentage | 95% |
| EMAILTHREAD | Email thread ID | THREAD_001 |
| INCLUSIVE | Inclusive email flag | Yes |
| HASREDACTION | Contains redactions | Yes |
| EXTRACTED_TEXT | Extracted text content | [Full text] |
| OCR_TEXT | OCR text | [OCR text] |
| LANGUAGEDETECTED | Detected language | English |

### Review and Coding Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| RESPONSIVE | Responsiveness coding | Responsive |
| PRIVILEGED | Privilege coding | Attorney-Client Privilege |
| CONFIDENTIAL | Confidentiality designation | Highly Confidential |
| ISSUES | Relevant issues | Contract Dispute; Damages |
| PRODUCTIONSTATUS | Production status | Produced |
| PRODUCTIONTO | Produced to party | Plaintiff |
| PRODUCTIONDATE | Production date | 02/01/2024 |
| REVIEWER | Reviewer name | Smith, John |
| REVIEWDATE | Date reviewed | 01/20/2024 |
| NOTES | Reviewer notes | Key document for damages |

### Production Fields

| Field Name | Description | Example |
|------------|-------------|---------|
| PRODUCTIONBEGDOC | Production Bates start | ACME_PROD_00001 |
| PRODUCTIONENDDOC | Production Bates end | ACME_PROD_00005 |
| PRODUCTIONVOLUME | Production volume ID | PROD_VOL_001 |
| NATIVEPATH | Path to native file | \NATIVES\ACME_PROD_00001.msg |
| TEXTPATH | Path to text file | \TEXT\ACME_PROD_00001.txt |
| IMAGEPATH | Path to images | \IMAGES\ACME_PROD_00001.tif |
| REDACTED | Redacted version flag | Yes |

## Metadata Preservation Best Practices

### 1. Forensic Collection

**Preserve Original Metadata**:
- Use forensically sound collection tools
- Capture full file system metadata
- Preserve MAC times (Modified, Accessed, Created)
- Document collection methodology
- Maintain chain of custody

**Tools**:
- EnCase
- FTK Imager
- Forensic Toolkit
- X-Ways Forensics
- Nuix Collect

### 2. Processing

**Extract All Relevant Metadata**:
- Configure processors to capture all fields
- Extract embedded metadata
- Normalize metadata formats
- Handle special characters properly
- Document extraction process

**Validation**:
- Spot-check metadata accuracy
- Verify date formats
- Confirm author/custodian mapping
- Test with sample documents

### 3. Production

**Determine Metadata to Produce**:
- Negotiate with opposing counsel
- Standard fields vs. extended metadata
- Embedded metadata handling (strip or include)
- Privacy considerations (scrub PII if needed)
- Document agreements

**Common Production Metadata Sets**:

**Basic Set**:
- Document ID (Bates number)
- File name
- File type
- Date created
- Date modified
- Custodian

**Standard Set** (adds):
- Author
- Subject/Title
- Email fields (from, to, cc, date sent)
- Attachment information
- File path
- File size

**Extended Set** (adds):
- MD5/SHA hash
- Last modified by
- Company
- All email headers
- Revision number
- Comments
- Keywords

**Confidential Set** (removes):
- File paths (reveal internal structure)
- Custodian names (privacy)
- Internal metadata fields
- Embedded/hidden metadata

### 4. Metadata Scrubbing

**When to Scrub**:
- Privileged information in metadata
- Work product in track changes
- Attorney comments
- Confidential internal information
- Privacy-protected data (GDPR, CCPA)

**Scrubbing Methods**:
- Convert to PDF (loses most metadata)
- Use metadata removal tools
- Manual inspection and removal
- Automated scrubbing scripts

**Documentation**:
- Document scrubbing methodology
- Identify fields removed
- Validate complete removal
- Inform receiving party if metadata removed

## Metadata Quality Control

### Validation Checklist

- [ ] All promised metadata fields present
- [ ] Date formats consistent
- [ ] No missing values in critical fields
- [ ] File paths accurate and accessible
- [ ] Hash values calculated correctly
- [ ] Email headers properly parsed
- [ ] Attachment relationships correct
- [ ] Duplicate identification accurate
- [ ] Special characters handled properly
- [ ] Metadata matches source documents

### Common Metadata Issues

**Issue**: Incorrect or missing dates

**Solutions**:
- Verify source document dates
- Check timezone handling
- Confirm date format (MM/DD/YYYY vs DD/MM/YYYY)
- Use created date if modified date unreliable

**Issue**: Special characters display incorrectly

**Solutions**:
- Use UTF-8 encoding
- Escape special characters in load files
- Test with international characters
- Validate in target system

**Issue**: Email recipients incomplete

**Solutions**:
- Parse full email headers
- Include BCC if available
- Expand distribution lists
- Verify against source email

**Issue**: Attachment relationships broken

**Solutions**:
- Verify parent-child relationships
- Check attachment count accuracy
- Ensure attachment names preserved
- Test reconstruction in review platform

## Metadata in Legal Context

### Spoliation Risks

**Metadata Alteration**:
- Copying files changes some metadata
- Printing to PDF loses metadata
- Email forwarding changes metadata
- Collection methods affect preservation

**Defensibility**:
- Use forensically sound methods
- Document all processing steps
- Preserve original files
- Validate metadata accuracy

### Privilege Considerations

**Privileged Metadata**:
- Attorney names in author fields
- Law firm names in company fields
- Privileged content in comments
- Work product in revision history

**Protection**:
- Review metadata for privilege
- Redact or remove privileged metadata
- Include in privilege log if withheld
- Claw-back if inadvertently produced

### Authentication

**Metadata as Evidence**:
- Proves document creation date
- Establishes authorship
- Shows document history
- Demonstrates tampering (or lack thereof)

**Challenges to Metadata**:
- Metadata can be altered
- Must establish authenticity
- Chain of custody important
- Expert testimony may be needed

## Platform-Specific Metadata Handling

### Relativity

- 500+ standard metadata fields
- Custom field creation
- Metadata mapping during import
- Field types (text, date, number, yes/no, choice)
- Automatic metadata extraction

### Nuix

- Extracts 500+ metadata types
- Custom metadata profiles
- Scripting for custom extraction
- Metadata normalization
- Export with metadata

### Everlaw

- Automatic metadata extraction
- Custom metadata fields
- Flexible field mapping
- Cloud-native metadata handling

## Resources

### Standards

- EDRM Metadata Specifications
- ISO 16175 (Information and documentation)
- Sedona Conference guidelines

### Tools

- Metadata extraction: ExifTool, MediaInfo
- Metadata scrubbing: Metadata Assistant, Adobe PDF tools
- Analysis: Python libraries (PyPDF2, python-docx, email)

### Training

- ACEDS metadata courses
- Platform-specific training (Relativity, Nuix)
- Forensic metadata analysis

## Conclusion

Metadata is a critical component of e-discovery, providing context, authenticity, and relationships for electronic documents. Proper extraction, preservation, validation, and production of metadata ensures defensible and effective e-discovery processes. Understanding metadata types, sources, and handling best practices is essential for e-discovery professionals.
