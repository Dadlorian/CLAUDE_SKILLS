# E-Discovery Data Processing Standards and Best Practices

## Overview

Data processing is the transformation of raw collected data into reviewable, searchable documents with extracted metadata and text. Processing is a critical phase in the EDRM lifecycle that directly impacts review efficiency, costs, and defensibility. Understanding processing standards, methodologies, and best practices ensures quality results and cost-effective e-discovery.

## Processing Objectives

### Primary Goals

1. **Make Data Review-Ready**
   - Extract and normalize text
   - Parse and organize metadata
   - Create searchable database
   - Enable analytics and searching

2. **Reduce Data Volume**
   - De-duplicate exact copies
   - Identify near-duplicates
   - Thread emails
   - Filter system and junk files

3. **Preserve Integrity**
   - Maintain chain of custody
   - Calculate hash values
   - Preserve metadata
   - Document processing steps

4. **Prepare for Production**
   - Create production-ready formats
   - Generate load files
   - Enable Bates numbering
   - Support redaction workflows

## Standard Processing Steps

### Step 1: Ingestion

**Purpose**: Import collected data into processing system

**Activities**:
- Upload forensic images, PSTs, loose files
- Validate data integrity (hash verification)
- Inventory data sources
- Create processing jobs

**Validation**:
- Hash verification (MD5, SHA-256)
- File count verification
- Size validation
- Error logging

**Best Practices**:
- Verify chain of custody
- Document data sources
- Validate before processing
- Organize by custodian or source

### Step 2: Inventory and Indexing

**Purpose**: Catalog all files and create searchable index

**Activities**:
- Enumerate all files
- Create database records
- Build search indexes
- Generate inventory reports

**Metadata Captured**:
- File names and paths
- File sizes and dates
- File types and extensions
- Custodian and source
- Folder hierarchy

**Output**:
- File inventory report
- Processing statistics
- Volume estimates
- Data source breakdown

### Step 3: De-NIST and System File Removal

**Purpose**: Remove known system files and irrelevant data

**NIST (National Software Reference Library)**:
- Library of known system file hashes
- Windows, Mac, Linux system files
- Application installation files
- Standard fonts and libraries

**De-NISTing Process**:
- Calculate file hashes (MD5, SHA-1)
- Compare against NIST database
- Flag or exclude matching files
- Document exclusions

**Additional Filtering**:
- System folders (Windows, Program Files)
- Temp files and cache
- Operating system files
- Software installation files
- Fonts and system libraries

**Caution**:
- Don't exclude without defensible basis
- Document exclusion criteria
- Consider case-specific needs
- May need to preserve for forensic analysis

**Typical Reduction**: 10-30% volume reduction

### Step 4: Expansion and Extraction

**Purpose**: Expand compressed files and containers

**Archive Expansion**:
- ZIP, RAR, 7Z, TAR, GZ
- Embedded archives (nested ZIPs)
- Email containers (PST, OST, NSF, MBOX)
- Recursive expansion (archives within archives)

**Container Processing**:
- PST/OST files (Outlook)
- NSF files (Lotus Notes)
- MBOX files (Thunderbird, Gmail export)
- DBX files (Outlook Express)

**Embedded Object Extraction**:
- OLE objects in Office documents
- Email attachments
- Embedded images
- Linked files

**Best Practices**:
- Set recursion depth limit (prevent infinite loops)
- Handle password-protected files separately
- Document expansion methodology
- Preserve parent-child relationships

### Step 5: Text Extraction

**Purpose**: Extract searchable text from native files

**Text Extraction Methods**:

**Native Text Extraction**:
- Read text directly from files (Office, PDF, TXT)
- Fastest and most accurate
- Preserves formatting information
- Supports 1000+ file types

**OCR (Optical Character Recognition)**:
- Convert images to searchable text
- Scanned documents, PDFs
- Embedded images
- Screenshots and photos

**OCR Settings**:
- **Language**: English, multi-language, or specific
- **Quality**: Standard (faster) vs. High (more accurate)
- **Preprocessing**: Deskew, despeckle, denoise
- **Output**: Searchable text layer or separate text file

**Text Extraction Quality**:
- **Good Sources**: Native Office files, text PDFs, HTML
- **Moderate Sources**: Scanned PDFs, clear images
- **Poor Sources**: Handwritten documents, low-quality scans, complex layouts

**Best Practices**:
- Use native extraction when possible
- Apply OCR to images and scanned documents
- Configure appropriate OCR language
- Balance quality vs. speed
- Spot-check OCR accuracy
- Document extraction methodology

### Step 6: Metadata Extraction

**Purpose**: Parse and normalize metadata from files

**System Metadata**:
- File names, paths, sizes
- Created, modified, accessed dates
- File system attributes
- Hash values (MD5, SHA-256)

**Application Metadata**:
- Office documents: Author, title, subject, company, modified by
- PDF: Producer, creator, keywords
- Images: EXIF data (camera, GPS, timestamps)
- Audio/Video: Codec, duration, resolution

**Email Metadata**:
- Headers: From, To, CC, BCC, Subject
- Dates: Sent, received
- Message-ID, In-Reply-To, References
- Routing information (SMTP headers)
- Importance and flags
- Attachment names and counts

**Metadata Normalization**:
- Standardize date formats (ISO 8601 or MM/DD/YYYY)
- Normalize character encoding (UTF-8)
- Parse email addresses (display name vs. address)
- Standardize field names
- Handle missing or corrupt metadata

**Best Practices**:
- Extract all available metadata
- Document metadata schema
- Validate metadata accuracy
- Preserve original metadata
- Handle timezone conversions consistently

### Step 7: File Type Identification

**Purpose**: Accurately identify file types

**Methods**:

**Extension-Based** (Unreliable):
- Based on file extension (.docx, .pdf)
- Can be incorrect or misleading
- Easily spoofed

**Signature-Based** (Reliable):
- Analyze file header (magic numbers)
- Identify true file type regardless of extension
- Detect renamed or misidentified files

**Content-Based**:
- Analyze file structure and content
- Identify embedded formats
- Detect format variations

**Tools**:
- libmagic (file command on Unix/Linux)
- TrID (file identifier)
- DROID (Digital Record Object Identification)
- Processing platform built-in identification

**Mismatch Handling**:
- Flag extension/signature mismatches
- Document discrepancies
- Re-classify based on true type
- Investigate deliberate misidentification

### Step 8: De-duplication

**Purpose**: Identify and eliminate duplicate documents

**Exact Duplicate Detection**:
- Hash-based (MD5, SHA-1, SHA-256)
- Binary comparison
- 100% accuracy

**Strategies**:
- **Global De-duplication**: Across all custodians
- **Custodial De-duplication**: Within each custodian
- **Hybrid**: Global for most, custodial for key players

**Near-Duplicate Detection**:
- Shingling algorithms
- Similarity scoring (80-95% threshold)
- Group related documents

**Email Threading**:
- Group related emails into conversations
- Identify inclusive emails
- Reduce review volume by 50-80%

**Best Practices**:
- Document de-duplication methodology
- Preserve duplicate metadata
- Make duplicates accessible if needed
- Validate duplicate groups

**Typical Reduction**: 30-50% overall volume reduction

### Step 9: Exception Handling

**Purpose**: Manage files that cannot be processed normally

**Common Exceptions**:
- **Encrypted Files**: Password-protected or encrypted
- **Corrupted Files**: Damaged or incomplete files
- **Unsupported Formats**: Rare or proprietary formats
- **Large Files**: Exceed processing limits
- **Empty Files**: Zero-byte files
- **Virus-Infected Files**: Malware or infected

**Exception Handling Workflow**:
1. Identify exception type
2. Attempt recovery or alternative processing
3. Document exception and reason
4. Escalate to collection team if needed
5. Generate exception report

**Password-Protected Files**:
- Maintain list of common passwords
- Contact custodians for passwords
- Use password cracking tools (with authorization)
- Document inaccessible files
- Consider specialized forensic tools

**Corrupted Files**:
- Attempt recovery with specialized tools
- Extract partial data if possible
- Document corruption
- Preserve original for potential manual review

**Best Practices**:
- Comprehensive exception logging
- Review exception reports regularly
- Escalate high-priority exceptions
- Document all exception handling steps
- Preserve exceptions for potential later processing

### Step 10: Quality Control

**Purpose**: Validate processing accuracy and completeness

**QC Checks**:

**Data Integrity**:
- Hash verification before/after processing
- File count reconciliation
- Size validation
- Custody verification

**Processing Quality**:
- Random sample review
- Text extraction spot-checks
- Metadata accuracy validation
- OCR quality assessment
- De-duplication verification

**Metadata Validation**:
- Field population rates
- Date format consistency
- Email parsing accuracy
- Attachment relationships

**Search Functionality**:
- Test searches on known documents
- Verify full-text indexing
- Check special character handling
- Validate search index completeness

**Exception Review**:
- Review all exception reports
- Assess exception rates (should be <5%)
- Escalate concerning exceptions
- Validate exception categorization

**Best Practices**:
- QC at least 1-2% of processed documents
- Document QC procedures
- Re-process if quality issues found
- Validate before loading to review platform

### Step 11: Export and Load File Generation

**Purpose**: Prepare data for review platform or production

**Export Formats**:
- Native files
- Images (TIFF, PDF)
- Extracted text
- Metadata (DAT, CSV, XML)
- Load files (OPT, XML)

**Load File Generation**:
- Concordance DAT format
- Opticon OPT format
- EDRM XML format
- Custom delimited formats

**Organization**:
- Logical folder structure
- Relative file paths
- Consistent naming conventions
- Volume management

**Validation**:
- Load file syntax validation
- File path verification
- Import test in target platform
- Document count reconciliation

## Processing Platforms and Tools

### Enterprise Processing Platforms

**Nuix**:
- Industry-leading processing
- 1000+ supported file types
- Advanced analytics
- International language support
- Scripting capabilities

**Relativity Processing (Invariant)**:
- Integrated with Relativity review
- Automatic processing workflows
- Exception handling
- Processing profiles

**OpenText (EnCase, Axcelerate)**:
- Forensic-grade processing
- Legal and investigation focus
- Cloud and on-premises options

**Exterro**:
- End-to-end platform
- Processing and review
- Legal hold integration

### Specialized Tools

**OCR**:
- ABBYY FineReader
- Adobe Acrobat OCR
- Tesseract (open-source)
- Google Cloud Vision
- Amazon Textract

**File Identification**:
- libmagic / file command
- TrID
- DROID
- Siegfried

**Hash Calculation**:
- md5sum, sha256sum
- HashCalc
- QuickHash
- Platform built-in tools

## Processing Performance Metrics

### Speed Metrics

**Processing Throughput**:
- GB per hour
- Documents per hour
- Typical: 50-500 GB/hour (depending on complexity)

**Factors Affecting Speed**:
- File types (native text faster than OCR)
- Hardware (CPU, RAM, SSD vs. HDD)
- De-duplication settings
- OCR quality settings
- Network speed (for remote processing)

### Quality Metrics

**Exception Rate**:
- Goal: <5% exceptions
- Higher rates indicate data quality issues or processing problems

**Text Extraction Rate**:
- Percentage of documents with extracted text
- Goal: >95% for native files
- Goal: 85-95% for OCR (depending on source quality)

**De-duplication Rate**:
- Percentage of documents identified as duplicates
- Typical: 30-50% for email-heavy collections
- Lower for unique document collections

### Cost Metrics

**Processing Cost**:
- Typical: $0.01-$0.05 per page or $50-$150 per GB
- Varies by vendor, volume, complexity

**Cost Factors**:
- Data volume
- File complexity
- OCR requirements
- De-duplication and analytics
- Turnaround time requirements

## Best Practices Summary

### Planning

1. **Assess Data Early**: Understand volumes, types, complexity
2. **Define Requirements**: Specify processing needs (OCR, analytics, de-duplication)
3. **Select Platform**: Choose appropriate processing tool
4. **Configure Settings**: Set up processing profiles and parameters
5. **Test First**: Process sample before full run

### Execution

1. **Validate Inputs**: Verify data integrity before processing
2. **Monitor Progress**: Track processing jobs and exceptions
3. **Handle Exceptions**: Address exceptions promptly
4. **Document Process**: Record all processing decisions and settings
5. **Quality Control**: Validate processing results

### Efficiency

1. **Cull Early**: Apply date, custodian, type filters before processing
2. **De-NIST**: Remove known system files
3. **Deduplicate**: Global de-duplication for maximum reduction
4. **Thread Emails**: Reduce email review volume significantly
5. **Optimize Settings**: Balance quality and speed appropriately

### Defensibility

1. **Document Everything**: Processing methodology, settings, decisions
2. **Preserve Originals**: Maintain original collected data
3. **Track Changes**: Log all processing steps and transformations
4. **Validate Quality**: QC processes and results
5. **Audit Trail**: Comprehensive logging of all processing activities

## Common Processing Challenges

### Challenge: Large Data Volumes

**Solutions**:
- Distributed processing across multiple nodes
- Incremental processing in batches
- Early aggressive culling
- Cloud processing with auto-scaling
- Overnight/weekend processing for large jobs

### Challenge: Complex File Types

**Solutions**:
- Specialized processing tools (CAD, GIS, databases)
- Manual extraction for critical complex files
- Consult with format experts
- Document limitations and approach
- Consider producing in native format

### Challenge: International Characters

**Solutions**:
- Use Unicode (UTF-8) encoding
- Configure proper language settings
- Test with sample international documents
- Verify search functionality for non-English text
- Use processing platform with strong international support (Nuix)

### Challenge: Encrypted/Password-Protected Files

**Solutions**:
- Coordinate with custodians for passwords
- Maintain list of common organizational passwords
- Use password recovery tools (with authorization)
- Document inaccessible files
- Report to requesting party if production required

### Challenge: Poor OCR Quality

**Solutions**:
- Increase OCR quality settings
- Preprocess images (deskew, denoise, enhance)
- Use advanced OCR engines (ABBYY)
- Manual transcription for critical documents
- Document OCR limitations

## Documentation Requirements

### Processing Report Should Include:

1. **Data Sources**
   - Custodians and data sources processed
   - Original data volumes
   - Collection dates and methods

2. **Processing Methodology**
   - Tools and platforms used
   - Processing settings and profiles
   - De-duplication approach
   - OCR settings and languages
   - Exception handling procedures

3. **Results and Statistics**
   - Total documents processed
   - Data reduction (de-NIST, deduplication)
   - Exception counts and types
   - Text extraction rates
   - Final document count for review

4. **Quality Control**
   - QC procedures performed
   - Sample sizes and results
   - Issues identified and resolved
   - Validation of search functionality

5. **Exceptions**
   - Exception reports
   - Types and counts
   - Resolution steps taken
   - Unresolved exceptions

6. **Deliverables**
   - Export formats and contents
   - Load file formats
   - Folder structure
   - File counts and hash values

## Compliance and Standards

### Industry Standards

**EDRM Guidelines**:
- Processing stage best practices
- Defensible processing workflows
- Documentation requirements

**Sedona Conference**:
- Reasonable processing standards
- Cooperation on processing approaches
- Proportionality in processing decisions

**ISO Standards**:
- ISO 27037: Digital evidence collection
- ISO 16175: Records management
- ISO 15489: Information and documentation

### Legal Compliance

**Defensibility Requirements**:
- Use industry-standard tools
- Document methodology thoroughly
- Preserve data integrity
- Validate processing quality
- Maintain audit trails

**Rule 26(f) Considerations**:
- Discuss processing approach with opposing counsel
- Agree on de-duplication methodology
- Clarify text extraction and OCR approach
- Define exception handling

## Resources

### Training and Certification

- ACEDS Processing courses
- Platform-specific training (Nuix, Relativity)
- Digital forensics certifications
- E-discovery processing workshops

### Tools and Software

- Nuix Workstation and Engine
- Relativity Processing
- OpenText Axcelerate
- Everlaw processing
- Open-source tools (Tesseract, libmagic)

### Further Reading

- EDRM processing guidelines
- Sedona Conference best practices
- Vendor white papers
- Technical blogs and forums

## Conclusion

Effective data processing is foundational to successful e-discovery. Proper processing reduces data volumes, ensures searchability, preserves integrity, and prepares data for efficient review. Understanding processing standards, employing best practices, and maintaining rigorous quality control and documentation ensures defensible, cost-effective e-discovery workflows.
