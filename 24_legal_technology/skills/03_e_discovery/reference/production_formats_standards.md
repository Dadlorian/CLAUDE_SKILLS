# E-Discovery Production Formats and Standards

## Overview

Production format determines how electronically stored information (ESI) is delivered from one party to another in litigation. The choice of production format affects cost, usability, metadata preservation, and review efficiency. Understanding production formats and negotiating appropriate specifications is critical for effective e-discovery.

## Production Format Categories

### 1. Native Format Production

**Definition**: Documents produced in their original application format

**File Types**:
- Microsoft Word (.docx, .doc)
- Microsoft Excel (.xlsx, .xls)
- Microsoft PowerPoint (.pptx, .ppt)
- PDF (.pdf)
- Email (.msg, .eml, .pst)
- Images (.jpg, .png, .tiff)
- Video (.mp4, .avi, .mov)
- Audio (.mp3, .wav)
- Databases (.mdb, .accdb, SQL exports)

**Advantages**:
- Full functionality preserved (formulas, hyperlinks, macros)
- All metadata retained
- Searchable text included
- Smaller file sizes
- Lower production costs
- Best for complex documents (databases, spreadsheets)

**Disadvantages**:
- Can contain embedded/hidden metadata
- Harder to apply redactions
- File compatibility issues
- Requires appropriate software to view
- May contain active content (macros, scripts)
- More difficult to Bates number

**When to Request Native**:
- Spreadsheets with formulas or complex calculations
- Databases
- Documents with embedded objects
- PowerPoint with animations or embedded media
- Email with attachments (PST/MSG format)
- Documents where metadata is critical

**When to Produce Native**:
- Requested by opposing counsel
- Document complexity requires it
- Reduces production cost significantly
- Agreement on handling embedded metadata

**Native Production Best Practices**:
- Organize in logical folder structure
- Provide metadata in load file
- Include extracted text files
- Document any redactions separately
- Scan for viruses before delivery
- Hash files for integrity verification

---

### 2. TIFF Image Production

**Definition**: Documents converted to multi-page Tagged Image File Format (TIFF) with accompanying load files

**Characteristics**:
- Industry standard for many years
- Static images of documents
- Separate metadata load file (DAT)
- Image cross-reference file (OPT)
- Extracted text files

**Advantages**:
- Standardized format
- Redactions can be "burned in" (permanent)
- Bates numbering applied to images
- No executable content (safe)
- Platform-independent
- Well-supported by review platforms
- Preserves visual appearance

**Disadvantages**:
- Large file sizes
- Some metadata lost in conversion
- Not searchable without OCR/text extraction
- Conversion costs
- Loss of native functionality
- Color information may be lost (if black & white)

**Technical Specifications**:

**Standard TIFF Settings**:
- **Format**: Group 4 compression
- **Resolution**: 300 DPI (minimum, 400-600 DPI for small text)
- **Color**: Black & white (1-bit) or grayscale (8-bit) or color (24-bit)
- **Size**: 8.5" x 11" or original page size
- **Orientation**: Portrait or auto-rotate to match original

**File Organization**:
```
PRODUCTION_001/
├── IMAGES/
│   ├── 0001/
│   │   ├── ACME00001.tif
│   │   ├── ACME00002.tif
│   │   └── ...
│   ├── 0002/
│   │   └── ...
├── TEXT/
│   ├── ACME00001.txt
│   ├── ACME00002.txt
│   └── ...
├── LOADFILES/
│   ├── METADATA.dat
│   ├── IMAGES.opt
│   └── VOLUME_INFO.xml
```

**Load Files**:
- **DAT file**: Metadata (Concordance format)
- **OPT file**: Image cross-reference (Opticon format)
- **Text files**: Extracted searchable text

**When to Use TIFF**:
- Traditional litigation with established workflows
- When redactions are necessary
- Confidentiality designations needed
- Bates numbering required
- Opposing counsel requests TIFF
- Standard format agreed upon

---

### 3. PDF Production

**Definition**: Documents converted to Portable Document Format (Adobe PDF)

**Types**:

**Native PDF**:
- Already in PDF format
- Retain as-is or convert to PDF/A

**Converted PDF**:
- Convert from other formats (Word, Excel, etc.) to PDF

**Image PDF**:
- Scanned documents as PDF
- Requires OCR for searchability

**Searchable PDF**:
- Native or converted with embedded searchable text
- Or image PDF with OCR layer

**Advantages**:
- Widely compatible (Adobe Reader free)
- Smaller than TIFF
- Searchable text embedded
- Can include hyperlinks and bookmarks
- Redactions can be applied
- Bates numbering possible
- Color preservation

**Disadvantages**:
- Some metadata lost in conversion
- Native functionality lost (Excel formulas)
- Redaction tools vary in quality
- PDF/A conversion may be required
- Can contain embedded files or scripts

**PDF Standards**:

**PDF/A (Archive)**:
- ISO standard for archival
- Self-contained (all fonts embedded)
- No external dependencies
- No encryption, scripts, or external content
- Preferred for long-term preservation

**PDF Specifications**:
- **Version**: PDF 1.4+ or PDF/A-1b
- **Text**: Searchable text embedded
- **Fonts**: Embedded (not referenced)
- **Compression**: Appropriate for images
- **Color**: Preserve original or convert to grayscale
- **Security**: No password protection or DRM

**When to Use PDF**:
- Default production format for many matters
- Balance of size and usability
- Searchable text important
- Color preservation needed
- Hyperlinks should be preserved
- Widely accessible format desired

---

### 4. Hybrid Production

**Definition**: Combination of native files and images based on document type

**Typical Approach**:
- **Native**: Spreadsheets, databases, certain complex documents
- **PDF/TIFF**: Standard documents (Word, email, presentations)

**Example Hybrid Spec**:
- Excel files: Native (.xlsx) with metadata
- Databases: Native export with schema documentation
- Word documents: PDF with searchable text
- Email: PDF with metadata and native attachments
- PowerPoint: PDF with speaker notes extracted

**Advantages**:
- Optimizes format for document type
- Preserves functionality where needed
- Manageable file sizes
- Balances cost and usability

**Disadvantages**:
- More complex production process
- Requires clear specification
- More QC needed
- Potential confusion on format

**When to Use Hybrid**:
- Complex document mix
- Cost optimization important
- Sophisticated parties/counsel
- Clear specifications agreed upon

---

### 5. Paper Production

**Definition**: Hard copy documents delivered on paper

**When Required**:
- Court order specifies paper
- Original signatures needed
- Certain government agencies
- Legacy matters or preferences

**Considerations**:
- Most expensive format
- Difficult to search
- Requires scanning for review
- Not common in modern e-discovery
- Typically only for specific documents

---

## Production Components

### Metadata Load File

**Purpose**: Deliver document metadata in structured format

**Common Formats**:
- Concordance DAT (most common)
- CSV (simple metadata)
- EDRM XML (structured, comprehensive)

**Essential Fields**:
- Document ID / Bates number
- File name and path
- File type and size
- Dates (created, modified, sent/received)
- Author, custodian
- Email fields (from, to, cc, subject)
- Hash values (MD5, SHA-256)

**Example DAT Structure**:
```
DOCID¶CUSTODIAN¶AUTHOR¶DATECREATED¶SUBJECT¶FILEPATH
ACME00001¶Smith, John¶John Smith¶01/15/2024¶Budget Meeting¶\NATIVES\ACME00001.docx
ACME00002¶Doe, Jane¶Jane Doe¶01/16/2024¶RE: Budget Meeting¶\NATIVES\ACME00002.msg
```

### Image Cross-Reference File (OPT)

**Purpose**: Link Bates numbers to image files and define page breaks

**Format**: Comma-delimited text (Opticon format)

**Structure**:
```
[Bates Number],[Volume],[Image Path],[Doc Break],[Folder Break],[Box Break]
```

**Example**:
```
ACME00001,VOL001,IMAGES\0001\ACME00001.tif,Y,,
ACME00002,VOL001,IMAGES\0001\ACME00002.tif,,,
ACME00003,VOL001,IMAGES\0001\ACME00003.tif,Y,,
```

### Extracted Text Files

**Purpose**: Provide searchable text separate from images

**Format**: Plain text (.txt) files

**Naming**: Match document ID (ACME00001.txt)

**Content**:
- Extracted text from native files
- OCR text from images
- Email headers and body
- Metadata as text

**Encoding**: UTF-8 for international characters

### Native Files (if included)

**Organization**:
- Folder structure by range or custodian
- Original or renamed to Bates number
- Preserve folder relationships if relevant

**Path References**:
- Relative paths in load file
- Accessible from production root

---

## Production Specifications

### Key Specifications to Define

1. **Format**
   - Native, TIFF, PDF, or hybrid
   - Specific file types for native (if hybrid)

2. **Metadata**
   - Fields to include
   - Load file format (DAT, CSV, XML)
   - Delimiter characters

3. **Images** (if applicable)
   - Resolution (DPI)
   - Color or black & white
   - TIFF or PDF
   - Compression settings

4. **Text**
   - Extracted text files included?
   - OCR for images?
   - Text file format and encoding

5. **Numbering**
   - Bates number prefix
   - Number of digits
   - Page-level or document-level
   - Attachment numbering convention

6. **Redactions**
   - Redacted vs. withheld
   - Placeholder pages for withheld documents
   - Redaction log format

7. **Organization**
   - Folder structure
   - Volume size (documents per volume)
   - File naming conventions

8. **Delivery**
   - Media (hard drive, FTP, cloud link)
   - Encryption requirements
   - Hash file for verification
   - Production cover letter

### Sample Production Specification

**Case**: *Acme Corp. v. Widget Inc.*
**Production**: Defendant's First Production

**Format**: Hybrid
- Native: Excel, Access databases, CAD files
- PDF: All other documents (searchable, PDF/A-1b)

**Metadata**: Concordance DAT format
- Delimiter: ASCII 20 (¶)
- Quote: ASCII 254 (þ)
- Newline: ASCII 174 («)
- Fields: DOCID, BEGATTACH, CUSTODIAN, AUTHOR, DATECREATED, SUBJECT, FILENAME, FILEPATH, MD5HASH, DOCTYPE, PAGECOUNT, NATIVEPATH, TEXTPATH

**Images**: N/A (PDF production)

**Text**: Extracted text in separate .txt files
- UTF-8 encoding
- One file per document

**Numbering**: WIDGET_PROD_0000001
- Seven-digit Bates numbers
- Page-level numbering
- Attachments numbered sequentially

**Redactions**: Burned-in redactions in PDF
- Redaction log in Excel format
- Privilege placeholders for withheld documents

**Confidentiality**: Designations applied per protective order
- "CONFIDENTIAL" stamp on designated documents

**Organization**:
- Folder: NATIVES (native files)
- Folder: TEXT (extracted text)
- Folder: LOADFILES (DAT, production log)

**Delivery**: Encrypted external hard drive
- MD5 hash file included
- Production cover letter

**Schedule**: Rolling production, 5,000 documents per week

---

## Bates Numbering Standards

### Bates Number Components

**Prefix**: Case or party identifier (ACME, WIDGET, PROD)
**Number**: Sequential digits (0001, 00001, 000001)
**Suffix**: Optional (page, volume, version)

**Examples**:
- ACME00001
- WIDGET_PROD_0000001
- DEF-001-00001 (Defendant 001, document 00001)

### Numbering Approaches

**Document-Level Numbering**:
- One number per document (multi-page docs have one number)
- Easier to reference
- Less granular

**Page-Level Numbering**:
- Sequential number on every page
- More granular referencing
- Standard for image productions
- Easier to cite specific pages

**Attachment Numbering**:
- **Sequential**: Attachments numbered after parent
  - Parent: ACME00001-ACME00005
  - Attachment: ACME00006-ACME00010
- **Nested**: Attachments use parent number with suffix
  - Parent: ACME00001
  - Attachment: ACME00001-A, ACME00001-B

### Bates Stamping

**Placement**:
- Typically bottom right or top right corner
- Consistent placement across production
- Should not obscure important content

**Format**:
- Clear, readable font
- Sufficient size (10-12pt typical)
- Contrasting color (if color production)

**Endorsements** (Additional Information):
- Confidentiality designation
- Production date
- Case number or name
- Party producing

---

## Confidentiality Designations

### Protective Order Compliance

**Standard Designations**:
- "CONFIDENTIAL"
- "HIGHLY CONFIDENTIAL - ATTORNEYS' EYES ONLY"
- "CONFIDENTIAL - SOURCE CODE"

**Application**:
- Apply per protective order requirements
- Consistent placement (header or footer)
- Clear and legible
- Burned into images or applied to PDF

**Tracking**:
- Metadata field for designation
- Designation log if required
- Process for challenging designations

---

## Quality Control for Productions

### Pre-Production QC

**Validation Checklist**:
- [ ] Document count matches expected
- [ ] Redactions applied correctly and completely
- [ ] Bates numbers sequential with no gaps
- [ ] Load file syntax valid
- [ ] File paths correct and files accessible
- [ ] Metadata complete and accurate
- [ ] Text files present and readable
- [ ] Confidentiality designations applied
- [ ] Sample import test successful

**Load File Testing**:
- Parse load file for errors
- Verify field count consistent
- Check for special characters
- Validate date formats
- Confirm file paths resolve

**Image/PDF Testing**:
- Spot-check random samples
- Verify Bates numbering
- Check redaction quality
- Confirm endorsements legible
- Validate page breaks (OPT file)

**Import Testing**:
- Test import into review platform (Relativity, Concordance)
- Verify document count
- Check metadata population
- Validate parent-child relationships
- Confirm text searchability

### Post-Production Tracking

**Production Log**:
- Production number and date
- Document range (ACME00001-ACME05000)
- Number of documents and pages
- Format (native, TIFF, PDF)
- Delivery method
- Recipient confirmation

**Version Control**:
- Track production versions
- Document any corrections or supplements
- Maintain all production iterations

---

## Common Production Issues

### Issue: Load File Errors

**Symptoms**: Import failures, field count mismatches, special character errors

**Solutions**:
- Validate load file syntax before delivery
- Test import in target platform
- Use standard delimiters (ASCII 20)
- Escape special characters properly
- Provide sample for testing

### Issue: Missing Files

**Symptoms**: File paths don't resolve, missing natives or text files

**Solutions**:
- Use relative paths (not absolute)
- Verify all referenced files exist
- Test from production root directory
- Include all folders in delivery
- Provide file listing for verification

### Issue: Redaction Failures

**Symptoms**: Incomplete redactions, text visible, metadata not removed

**Solutions**:
- Use proper redaction tools
- Burn redactions into images/PDFs
- Remove embedded metadata if redacted
- QC every redacted document
- Use placeholder pages for withheld docs

### Issue: Image Quality

**Symptoms**: Unreadable text, poor resolution, incorrect orientation

**Solutions**:
- Use sufficient DPI (300-600)
- Preserve color if important
- Auto-rotate to correct orientation
- Spot-check quality before production
- Reprocess problem documents

---

## Negotiating Production Format

### Rule 26(f) Conference Discussion

**Topics**:
1. Preferred format (native, TIFF, PDF, hybrid)
2. Metadata fields to include
3. Redaction approach
4. Bates numbering convention
5. Load file format
6. De-duplication methodology
7. Delivery method and encryption
8. Production schedule

**Considerations**:
- **Requesting Party**: Usability and searchability
- **Producing Party**: Cost and burden
- **Both**: Platform compatibility

### Agreement Documentation

**ESI Protocol Should Include**:
- Specific production format by document type
- Metadata field definitions
- Load file format and delimiters
- Image specifications (if applicable)
- Numbering convention
- Delivery method
- Timeline for productions
- Process for addressing errors

---

## Platform Compatibility

### Relativity

**Accepts**:
- Concordance DAT and OPT
- EDRM XML
- Native files with metadata
- TIFF and PDF images
- Custom delimited formats (configurable)

**Import Process**:
- Create import profile
- Map fields
- Upload files
- Process and validate

### Concordance

**Native Format**:
- DAT files (Concordance format)
- CPL image database
- DII import

### Everlaw, Logikcull, Disco

**Accepts**:
- Native files
- PDF and TIFF with load files
- DAT and OPT formats
- EDRM XML
- Cloud-based upload

---

## Best Practices Summary

1. **Negotiate Early**: Agree on format during Rule 26(f) conference
2. **Document Specifications**: Written agreement on all details
3. **Test Before Production**: Sample import to validate
4. **Quality Control**: Rigorous QC before delivery
5. **Provide Documentation**: Cover letter, production log, hash file
6. **Maintain Copies**: Retain production copies indefinitely
7. **Track Productions**: Detailed logs of all productions
8. **Clear Communication**: Notify of any issues or limitations
9. **Secure Delivery**: Encrypt productions, secure transfer
10. **Responsive to Issues**: Quickly address and correct errors

---

## Resources

### Standards Organizations

- EDRM (Electronic Discovery Reference Model)
- Sedona Conference
- ISO standards for document formats

### Technical Specifications

- TIFF specification (ISO 12639)
- PDF/A standard (ISO 19005)
- Concordance file formats
- EDRM XML schema

### Platform Documentation

- Relativity import guides
- Platform-specific production guides
- Vendor best practices

---

## Conclusion

Production format selection significantly impacts e-discovery cost, efficiency, and usability. Understanding format options, technical specifications, and quality control procedures ensures successful productions that meet legal requirements, platform compatibility, and party needs. Clear communication and agreement on production specifications during Rule 26(f) conferences prevents disputes and ensures smooth discovery processes.
